"""
Registry client for the Terraform Registry module API: fetch, assemble, and cache
full module documentation for `grep_module_docs`.

Network access for the whole server is confined to this module. All HTTP is done
via `urllib.request` (stdlib only, no new dependencies).

Exports:
- parse_module_id(module_id) -> (namespace, name, provider)
- assemble_document(detail) -> str  (deterministic, `=====`-delimited greppable text)
- get_assembled_docs(module_id, version, *, cache_dir, ttl_hours, refresh, fetch)
    -> (assembled_text, resolved_version, source_url, cache_hit, fetched_at_iso)
"""

import datetime
import json
import os
import threading
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

REGISTRY_API_BASE = "https://registry.terraform.io/v1/modules"
REGISTRY_WEB_BASE = "https://registry.terraform.io/modules"

# In-memory per-process cache: (cache_dir, module_id, version-or-"latest") -> assembled
# tuple. Keying on cache_dir (not just module_id/version) keeps callers that point at
# different cache directories - e.g. isolated tmp_path dirs in tests - from bleeding
# into each other. Mirrors the _MODEL_CACHE pattern in tfmod_search_lib.py. Bypassed by
# refresh=True.
_MEMORY_CACHE: dict[tuple[str, str, str], dict[str, Any]] = {}


def parse_module_id(module_id: str) -> tuple[str, str, str]:
    """
    Split a "namespace/name/provider" module id into its three parts.

    Raises ValueError with a helpful example if `module_id` is not exactly
    3 non-empty, "/"-separated parts.
    """
    parts = module_id.split("/")
    if len(parts) != 3 or not all(parts):
        raise ValueError(
            f"Invalid module_id {module_id!r}: expected exactly "
            '"namespace/name/provider", e.g. "terraform-aws-modules/vpc/aws"'
        )
    namespace, name, provider = parts
    return namespace, name, provider


def _http_fetch(namespace: str, name: str, provider: str, version: str | None) -> dict:
    """Default fetcher: GET the registry module detail endpoint and parse JSON."""
    url = f"{REGISTRY_API_BASE}/{namespace}/{name}/{provider}"
    if version is not None:
        url = f"{url}/{version}"
    if not url.startswith("https://"):
        raise ValueError(f"Refusing to fetch non-https URL: {url!r}")
    with urllib.request.urlopen(url, timeout=25) as resp:  # noqa: S310 - scheme guarded above
        return json.load(resp)


def _format_input_row(item: dict[str, Any]) -> str:
    name = item.get("name", "")
    itype = item.get("type", "")
    description = item.get("description", "")
    if item.get("required"):
        req_or_default = "required"
    else:
        req_or_default = item.get("default", "")
    return f"- {name} | {itype} | {req_or_default} | {description}"


def _format_output_row(item: dict[str, Any]) -> str:
    name = item.get("name", "")
    description = item.get("description", "")
    return f"- {name} | {description}"


def _format_resource_row(item: dict[str, Any]) -> str:
    name = item.get("name", "")
    rtype = item.get("type")
    mode = item.get("mode")
    if rtype:
        if mode:
            return f"- {rtype}.{name} ({mode})"
        return f"- {rtype}.{name}"
    return f"- {name}"


def _render_block(items: list[dict[str, Any]] | None, formatter: Callable[[dict[str, Any]], str]) -> str:
    if not items:
        return ""
    return "\n".join(formatter(item) for item in items)


def assemble_document(detail: dict[str, Any]) -> str:
    """
    Build one deterministic, greppable text from a registry module detail JSON:
    top module header, root readme/inputs/outputs/resources, then each submodule
    and example. Section marker lines (`===== ... =====`) delimit blocks and double
    as the source of `grep_module_docs`'s match `section` labels.

    Missing/empty fields are handled gracefully: root readme/inputs/outputs section
    markers are always emitted (possibly with an empty body); resources/submodules/
    examples sections are skipped entirely when there is nothing to render.
    """
    namespace = detail.get("namespace", "")
    name = detail.get("name", "")
    provider = detail.get("provider", "")
    version = detail.get("version", "")
    root = detail.get("root", {}) or {}

    parts = [f"===== MODULE {namespace}/{name}/{provider} @ {version} ====="]

    parts.append("")
    parts.append("===== ROOT README =====")
    readme = root.get("readme") or ""
    if readme:
        parts.append(readme)

    parts.append("")
    parts.append("===== ROOT INPUTS =====")
    inputs_block = _render_block(root.get("inputs"), _format_input_row)
    if inputs_block:
        parts.append(inputs_block)

    parts.append("")
    parts.append("===== ROOT OUTPUTS =====")
    outputs_block = _render_block(root.get("outputs"), _format_output_row)
    if outputs_block:
        parts.append(outputs_block)

    resources_block = _render_block(root.get("resources"), _format_resource_row)
    if resources_block:
        parts.append("")
        parts.append("===== ROOT RESOURCES =====")
        parts.append(resources_block)

    for submodule in detail.get("submodules") or []:
        sub_name = submodule.get("name", "")
        parts.append("")
        parts.append(f"===== SUBMODULE: {sub_name} =====")

        sub_readme = submodule.get("readme") or ""
        if sub_readme:
            parts.append("--- readme ---")
            parts.append(sub_readme)

        sub_inputs_block = _render_block(submodule.get("inputs"), _format_input_row)
        if sub_inputs_block:
            parts.append("--- inputs ---")
            parts.append(sub_inputs_block)

        sub_outputs_block = _render_block(submodule.get("outputs"), _format_output_row)
        if sub_outputs_block:
            parts.append("--- outputs ---")
            parts.append(sub_outputs_block)

    for example in detail.get("examples") or []:
        example_name = example.get("name", "")
        example_readme = example.get("readme") or ""
        parts.append("")
        parts.append(f"===== EXAMPLE: {example_name} =====")
        if example_readme:
            parts.append(example_readme)

    return "\n".join(parts) + "\n"


def _cache_file(cache_dir: Path, namespace: str, name: str, provider: str, version_key: str) -> Path:
    return cache_dir / f"{namespace}__{name}__{provider}__{version_key}.json"


def _read_cache_entry(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _write_cache_entry(path: Path, entry: dict[str, Any]) -> None:
    """Atomically write a cache entry (temp file + rename).

    Concurrent HTTP tool calls may write the same entry simultaneously;
    os.replace guarantees readers never observe a partially written file.
    Worst case under a race is a duplicate fetch, never corruption.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}-{threading.get_ident()}")
    try:
        tmp.write_text(json.dumps(entry))
        os.replace(tmp, path)
    except OSError:
        tmp.unlink(missing_ok=True)
        raise


def _is_latest_entry_fresh(entry: dict[str, Any], ttl_hours: int) -> bool:
    if ttl_hours <= 0:
        return False
    fetched_at = entry.get("fetched_at")
    if not fetched_at:
        return False
    try:
        fetched_dt = datetime.datetime.fromisoformat(fetched_at)
    except ValueError:
        return False
    age_hours = (datetime.datetime.now(datetime.UTC) - fetched_dt).total_seconds() / 3600
    return age_hours <= ttl_hours


def get_assembled_docs(
    module_id: str,
    version: str | None,
    *,
    cache_dir: Path,
    ttl_hours: int = 24,
    refresh: bool = False,
    fetch: Callable[[str, str, str, str | None], dict] = _http_fetch,
) -> tuple[str, str, str, bool, str]:
    """
    Fetch (or read from cache) the full docs for a registry module, assemble them
    into one greppable text, and return:

        (assembled_text, resolved_version, source_url, cache_hit, fetched_at_iso)

    Cache policy: a pinned `version` is immutable and never refetched once cached.
    `version=None` resolves to "latest" and is refetched once `fetched_at` is older
    than `ttl_hours` (ttl_hours=0 => always stale). Every fetch also writes the
    concrete resolved-version cache entry, so a later pinned request for that same
    version is a hit. `refresh=True` bypasses both the in-memory and on-disk cache
    reads (but still populates them on the resulting fetch).
    """
    namespace, name, provider = parse_module_id(module_id)
    version_key = version if version is not None else "latest"
    cache_dir_key = str(cache_dir)
    memory_key = (cache_dir_key, module_id, version_key)
    is_pinned = version is not None

    def _source_url(resolved_version: str) -> str:
        return f"{REGISTRY_WEB_BASE}/{namespace}/{name}/{provider}/{resolved_version}"

    if not refresh:
        # Memory and disk are checked with the SAME freshness policy (pinned =
        # always fresh, latest = fresh within ttl_hours) so an in-process repeat of
        # a "latest" lookup still refetches once the entry goes stale, exactly like
        # a fresh disk read would.
        entry = _MEMORY_CACHE.get(memory_key) or _read_cache_entry(
            _cache_file(cache_dir, namespace, name, provider, version_key)
        )
        if entry is not None and (is_pinned or _is_latest_entry_fresh(entry, ttl_hours)):
            resolved_version = entry["resolved_version"]
            _MEMORY_CACHE[memory_key] = entry
            return (entry["assembled_text"], resolved_version, _source_url(resolved_version), True, entry["fetched_at"])

    detail = fetch(namespace, name, provider, version)
    resolved_version = detail["version"]
    assembled_text = assemble_document(detail)
    fetched_at = datetime.datetime.now(datetime.UTC).isoformat()

    entry = {
        "module_id": module_id,
        "resolved_version": resolved_version,
        "assembled_text": assembled_text,
        "fetched_at": fetched_at,
    }
    # Write/cache the entry under the requested key (e.g. "latest") ...
    _write_cache_entry(_cache_file(cache_dir, namespace, name, provider, version_key), entry)
    _MEMORY_CACHE[memory_key] = entry
    # ... and always also under the concrete resolved version, so a later pinned
    # request for that version is a cache hit without refetching.
    if version_key != resolved_version:
        _write_cache_entry(_cache_file(cache_dir, namespace, name, provider, resolved_version), entry)
        _MEMORY_CACHE[(cache_dir_key, module_id, resolved_version)] = entry

    return (assembled_text, resolved_version, _source_url(resolved_version), False, fetched_at)
