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
import io
import json
import logging
import os
import re
import tarfile
import threading
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

REGISTRY_API_BASE = "https://registry.terraform.io/v1/modules"
REGISTRY_WEB_BASE = "https://registry.terraform.io/modules"
GITHUB_ARCHIVE_BASE = "https://codeload.github.com"
GITHUB_API_BASE = "https://api.github.com"

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


PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"


def _pypi_json_fetch(url: str, timeout: int) -> dict:
    if not url.startswith("https://"):
        raise ValueError(f"refusing non-https URL: {url}")
    with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 - scheme guarded above
        return json.loads(resp.read())


def fetch_latest_pypi_version(
    package: str = "tfmodsearch",
    timeout: int = 5,
    fetcher: Callable[[str, int], dict] | None = None,
) -> str | None:
    """Latest released version of *package* on PyPI, or None on any failure.

    Used by the HTTP daemon update check. One anonymous GET to the public
    PyPI JSON API; never raises - the caller treats None as "unknown".
    """
    fetch = fetcher or _pypi_json_fetch
    try:
        payload = fetch(PYPI_JSON_URL.format(package=package), timeout)
        version = payload["info"]["version"]
        return version if isinstance(version, str) and version else None
    except Exception:
        return None


def is_newer_version(latest: str, current: str) -> bool:
    """True when *latest* is strictly newer than *current*.

    Plain X.Y.Z int-tuple comparison; any parse failure returns False
    (fail closed: no update notice on uncertainty). This project publishes
    plain numeric versions, so rc/dev suffixes intentionally do not match.
    """
    try:
        return tuple(map(int, latest.split("."))) > tuple(map(int, current.split(".")))
    except (ValueError, AttributeError):
        return False


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


_UNWRITABLE_CACHE_DIRS_WARNED: set[str] = set()
_UNWRITABLE_WARN_LOCK = threading.Lock()


def _write_cache_entry(path: Path, entry: dict[str, Any]) -> None:
    """Atomically write a cache entry (temp file + rename), best-effort.

    Concurrent HTTP tool calls may write the same entry simultaneously;
    os.replace guarantees readers never observe a partially written file.
    Worst case under a race is a duplicate fetch, never corruption.

    An unwritable cache dir (read-only rootfs, a root-owned named volume
    mounted over ~/.cache) must degrade to uncached fetches with a WARNING,
    never fail the tool call: the cache is an optimization, not a dependency.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}-{threading.get_ident()}")
        try:
            tmp.write_text(json.dumps(entry))
            os.replace(tmp, path)
        except OSError:
            tmp.unlink(missing_ok=True)
            raise
    except OSError as exc:
        key = str(path.parent)
        with _UNWRITABLE_WARN_LOCK:
            already_warned = key in _UNWRITABLE_CACHE_DIRS_WARNED
            _UNWRITABLE_CACHE_DIRS_WARNED.add(key)
        if not already_warned:
            logging.getLogger(__name__).warning(
                f"Registry doc cache dir {key} is not writable ({exc}); "
                "serving fetches uncached. Fix the ownership/permissions of the "
                "cache dir (for the Docker named volume: "
                "docker exec -u root <container> chown app:app /home/app/.cache) "
                "or set TFMODSEARCH_CACHE_DIR to a writable location."
            )


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


# --------------------------------------------------------------------------- #
# fetch_module_source - build-time GitHub source fetch for tfmod_any_examples.
# Downloads a module's .tf files (not its rendered docs) so the pure/offline
# extractor in tfmod_any_examples.py can read variables.tf/main.tf/examples/**.
# Kept in this module to preserve the "all HTTP is confined to
# tfmod_registry_docs.py" invariant.
# --------------------------------------------------------------------------- #

_GITHUB_SOURCE_RE = re.compile(r"^(?:git::)?https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$")


def _url_fetch(url: str, timeout: int = 25) -> bytes:
    """Default fetch(url) -> bytes primitive for fetch_module_source: a plain
    HTTPS GET, stdlib only (mirrors _http_fetch/_pypi_json_fetch's https guard)."""
    if not url.startswith("https://"):
        raise ValueError(f"Refusing to fetch non-https URL: {url!r}")
    with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 - scheme guarded above
        return resp.read()


def _parse_github_source(source: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from a registry module detail's `source` field.

    Returns None for anything that is not a plain GitHub HTTPS URL - the only
    scheme this fetcher supports (the registry API also allows other VCS
    hosts, but the curated + cloudposse catalogs are all GitHub).
    """
    if not source:
        return None
    m = _GITHUB_SOURCE_RE.match(source.strip())
    if not m:
        return None
    return m.group(1), m.group(2)


def _extract_tf_files(archive_bytes: bytes, dest_dir: Path) -> bool:
    """
    Extract every `.tf` file from a gzipped tarball into dest_dir, preserving
    the archive's internal relative paths minus the single top-level
    "<repo>-<ref>/" directory GitHub codeload archives always wrap content in
    (so "examples/complete/main.tf" and "modules/vectors/variables.tf" land at
    dest_dir/examples/complete/main.tf and dest_dir/modules/vectors/variables.tf).

    Guards against path traversal (zip-slip): a member whose resolved path
    would land outside dest_dir is silently skipped. Returns True iff at
    least one `.tf` file was written; never raises (a corrupt/unexpected
    archive returns False so the caller can try the next tag/fallback).
    """
    try:
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as tf:
            members = tf.getmembers()

            root_prefix = None
            for member in members:
                if "/" in member.name:
                    root_prefix = member.name.split("/", 1)[0] + "/"
                    break

            dest_dir = dest_dir.resolve()
            dest_dir.mkdir(parents=True, exist_ok=True)
            extracted_any = False
            for member in members:
                if not member.isfile() or not member.name.endswith(".tf"):
                    continue
                name = member.name
                if root_prefix and name.startswith(root_prefix):
                    name = name[len(root_prefix) :]
                if not name:
                    continue
                target = (dest_dir / name).resolve()
                try:
                    target.relative_to(dest_dir)
                except ValueError:
                    continue  # zip-slip guard: member escapes dest_dir
                target.parent.mkdir(parents=True, exist_ok=True)
                fobj = tf.extractfile(member)
                if fobj is None:
                    continue
                target.write_bytes(fobj.read())
                extracted_any = True
            return extracted_any
    except (tarfile.TarError, OSError, EOFError):
        return False


def fetch_module_source(
    module_id: str,
    version: str,
    dest_dir: Path,
    *,
    fetch: Callable[[str], bytes] | None = None,
) -> Path | None:
    """
    Resolve a registry module's GitHub source and download+extract its `.tf`
    files into dest_dir, for offline shape/example extraction
    (tfmod_any_examples.py). Never raises: any failure (unparseable module_id,
    non-GitHub source, network error, no matching tag, corrupt archive)
    returns None so a caller can fall back to serving honest `any`.

    Tries the GitHub release tag as "v{version}" then bare "{version}"
    (terraform-aws-modules tags "vX.Y.Z"; some vendors - e.g. cloudposse - tag
    bare "X.Y.Z"), then falls back to the GitHub tags API to find a tag whose
    name contains the version string.

    `fetch(url) -> bytes` is the single injectable HTTP primitive - used for
    the registry API detail call and every GitHub archive/tags download - so
    tests can run fully offline.
    """
    fetch = fetch or _url_fetch
    try:
        namespace, name, provider = parse_module_id(module_id)
    except ValueError:
        return None

    try:
        detail_url = f"{REGISTRY_API_BASE}/{namespace}/{name}/{provider}/{version}"
        detail = json.loads(fetch(detail_url))
    except Exception:
        return None

    gh = _parse_github_source(detail.get("source", ""))
    if gh is None:
        return None
    owner, repo = gh

    for tag in (f"v{version}", version):
        archive_url = f"{GITHUB_ARCHIVE_BASE}/{owner}/{repo}/tar.gz/refs/tags/{tag}"
        try:
            data = fetch(archive_url)
        except Exception:  # noqa: S112 - probing candidate tags; a miss is expected, try the next one
            continue
        if data and _extract_tf_files(data, dest_dir):
            return dest_dir

    try:
        tags_json = json.loads(fetch(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/tags"))
    except Exception:
        return None
    for tag_entry in tags_json:
        tag_name = tag_entry.get("name", "")
        if version not in tag_name:
            continue
        archive_url = f"{GITHUB_ARCHIVE_BASE}/{owner}/{repo}/tar.gz/refs/tags/{tag_name}"
        try:
            data = fetch(archive_url)
        except Exception:  # noqa: S112 - probing candidate tags; a miss is expected, try the next one
            continue
        if data and _extract_tf_files(data, dest_dir):
            return dest_dir

    return None
