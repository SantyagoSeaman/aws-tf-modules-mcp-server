"""
Registry client for the Terraform Registry module API.

Two remaining concerns after the 2026-07-21 D7 removal of `grep_module_docs`
(the tool that used to be this module's primary consumer):
- The 0.17.0 PyPI update check (fetch_latest_pypi_version/is_newer_version).
- Build-time GitHub source fetch for the any-overlay example extractor
  (fetch_module_source/fetch_module_detail, used by scripts/build_any_overlay.py).

Network access for the whole server is confined to this module. All HTTP is done
via `urllib.request` (stdlib only, no new dependencies).

Exports:
- parse_module_id(module_id) -> (namespace, name, provider)
- fetch_latest_pypi_version(package, timeout, fetcher) -> str | None
- is_newer_version(latest, current) -> bool
- fetch_module_source(module_id, version, dest_dir, *, fetch) -> Path | None
- fetch_module_detail(module_id, version, *, fetch) -> dict | None
"""

import io
import json
import re
import tarfile
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

REGISTRY_API_BASE = "https://registry.terraform.io/v1/modules"
GITHUB_ARCHIVE_BASE = "https://codeload.github.com"
GITHUB_API_BASE = "https://api.github.com"


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
    HTTPS GET, stdlib only (mirrors _pypi_json_fetch's https guard)."""
    if not url.startswith("https://"):
        raise ValueError(f"Refusing to fetch non-https URL: {url!r}")
    with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 - scheme guarded above
        return resp.read()


def fetch_module_detail(
    module_id: str,
    version: str,
    *,
    fetch: Callable[[str], bytes] | None = None,
) -> dict[str, Any] | None:
    """
    Fetch the raw registry module detail JSON for `module_id`@`version` (root
    and submodule `inputs`/`outputs`/`resources`, etc.) via the same GET
    `fetch_module_source` uses internally to resolve GitHub source -- exposed
    standalone here so a caller (build_any_overlay.py's `all_inputs`
    extraction, the complete-interface-in-one-call feature) can read the
    detail's input metadata directly without also downloading source. Never
    raises: an unparseable module_id, network error, or malformed JSON
    response returns None.
    """
    fetch = fetch or _url_fetch
    try:
        namespace, name, provider = parse_module_id(module_id)
    except ValueError:
        return None
    try:
        detail_url = f"{REGISTRY_API_BASE}/{namespace}/{name}/{provider}/{version}"
        return json.loads(fetch(detail_url))
    except Exception:
        return None


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
