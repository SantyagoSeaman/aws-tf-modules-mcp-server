#!/usr/bin/env python3
"""
Build committed any-var overlay JSON files (`model/any_overlay/`) from catalog
module source.

Design: evals/specs/2026-07-20-consolidated-interface-any-overlay-design.md
("examples-primary"), extended by evals/specs/2026-07-21-complete-interface-
one-call-design.md ("complete-interface-in-one-call"). For EVERY catalog
module, fetches the registry detail at the doc's pinned Latest Version
(network confined to tfmod_registry_docs.fetch_module_detail/
fetch_module_source) and writes one deterministic JSON file per module:

    { module_id, built_from_version,
      all_inputs: { "<scope>": [ {name, type, required, default, description} ] },
      all_outputs: { "<scope>": [ {name, description} ] },
      vars: { "<scope>::<var>": { examples, field_names, provenance, note? } } }

`all_inputs`/`all_outputs` (the complete root+submodule input/output lists)
are attached for every module - this is the primary artifact now, giving
`get_module` a complete interface table for all 63 catalog modules, not just
the ones with `type = any` inputs. `vars` (any-typed input examples/observed
field names) is attached ADDITIONALLY, only for modules that have at least
one `type = any` input AND whose GitHub source could be fetched and
extracted; a module with zero any-vars gets no `vars` key at all.

The two halves fail independently: a module whose GitHub source cannot be
resolved (network error, no matching GitHub tag, non-GitHub source, etc.)
still gets an overlay carrying all_inputs/all_outputs, just no `vars`. Only a
module for which NEITHER half could be built (e.g. total network failure, or
an unresolvable module_id) gets no overlay file at all - `get_module` then
keeps serving the honest curated doc exactly as it did before this feature
existed.

This script only orchestrates; it never opens a socket itself - all HTTP goes
through the injectable `fetch` callable threaded down into
tfmod_registry_docs.fetch_module_source, so tests run fully offline.

Exports (importable for tests):
- discover_catalog_modules(modules_dir) -> list[(module_id, latest_version)]
- build_overlay_from_source(module_id, version, source_dir) -> dict | None
- build_module_overlay(module_id, version, *, fetch=None, workdir=None) -> dict | None
- serialize_overlay(overlay) -> str
- write_overlay(overlay, out_dir) -> Path

Usage:
    python scripts/build_any_overlay.py terraform-aws-modules/s3-bucket/aws
    python scripts/build_any_overlay.py --all
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tfmod_any_examples import (  # noqa: E402 -- sys.path must be set up first
    coverage_report,
    extract_examples,
    find_any_vars,
    observed_field_names,
)

from tfmod_registry_docs import fetch_module_detail, fetch_module_source  # noqa: E402 -- sys.path must be set up first

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = REPO_ROOT / "modules"
OVERLAY_DIR = REPO_ROOT / "model" / "any_overlay"

ALLOWED_PROVENANCE = ("example", "example+names", "names-only", "honest-any")

_HONEST_ANY_NOTE = (
    "no example and no observed field names found in the module source; "
    "likely pass-through/context plumbing or a runtime-polymorphic value - "
    "stays honest `any`, see the module source directly for the raw shape"
)

# --------------------------------------------------------------------------- #
# Catalog discovery - the committed docs' own "## Module Information" bullets,
# no network. Deliberately matched at exact bullet indentation/prefix
# ("- **Module ID**: `...`") so module_template.md's numbered-list "2. **Module
# ID**:" placeholder line and UPDATE_PROMPTS.md's prose mentions never match.
# --------------------------------------------------------------------------- #

_MODULE_ID_BULLET_RE = re.compile(r"^- \*\*Module ID\*\*:\s*`([^`]+)`", re.MULTILINE)
_LATEST_VERSION_BULLET_RE = re.compile(r"^- \*\*Latest Version\*\*:\s*(\S+)", re.MULTILINE)


def discover_catalog_modules(modules_dir: str | Path = MODULES_DIR) -> list[tuple[str, str]]:
    """
    Every catalog module's (module_id, latest_version), sorted by module_id.

    Read straight from the committed `.md` docs - no network. `module_template.md`
    and anything under a `temp/` directory are skipped (mirrors build_index's
    corpus scan); a doc missing either bullet is silently excluded too.
    """
    modules_dir = Path(modules_dir)
    found: dict[str, str] = {}
    for md_path in sorted(modules_dir.rglob("*.md")):
        if md_path.name == "module_template.md":
            continue
        if "temp" in md_path.relative_to(modules_dir).parts[:-1]:
            continue
        text = md_path.read_text(encoding="utf-8", errors="replace")
        id_match = _MODULE_ID_BULLET_RE.search(text)
        version_match = _LATEST_VERSION_BULLET_RE.search(text)
        if not id_match or not version_match:
            continue
        found[id_match.group(1).strip()] = version_match.group(1).strip()
    return sorted(found.items())


# --------------------------------------------------------------------------- #
# Provenance classification (spec data model).
# --------------------------------------------------------------------------- #


def _classify_provenance(examples: list[str], field_names: list[str]) -> tuple[str, str | None]:
    """
    (provenance, note) per the overlay's trust order:
    - "example": has a non-trivial example and every observed field name
      already appears in it (no incremental information from the checklist).
    - "example+names": has an example AND the field-name scan surfaces names
      not present in that example (the instance-ceiling case, e.g. elasticache
      `destination`/`log_type`).
    - "names-only": no example, but the field-name scan found something.
    - "honest-any": neither - stays honest `any` with a short note.
    """
    if examples:
        combined = "\n".join(examples)
        extra = [name for name in field_names if not re.search(r"\b" + re.escape(name) + r"\b", combined)]
        return ("example+names" if extra else "example"), None
    if field_names:
        return "names-only", None
    return "honest-any", _HONEST_ANY_NOTE


# --------------------------------------------------------------------------- #
# Overlay construction.
# --------------------------------------------------------------------------- #


def build_overlay_from_source(module_id: str, version: str, source_dir: str | Path) -> dict | None:
    """
    Pure (no network): build the overlay dict for `module_id`@`version` from an
    already-fetched `source_dir`. Returns None when the module has zero
    `type = any` variables - such modules get no overlay file at all.
    """
    source_dir = Path(source_dir)
    any_vars = find_any_vars(source_dir)
    if not any_vars:
        return None

    vars_obj: dict[str, dict] = {}
    for scope, var_name in any_vars:
        examples = extract_examples(source_dir, scope, var_name)
        field_names = observed_field_names(source_dir, scope, var_name)
        provenance, note = _classify_provenance(examples, field_names)
        entry: dict = {
            "examples": examples,
            "field_names": field_names,
            "provenance": provenance,
        }
        if note:
            entry["note"] = note
        vars_obj[f"{scope}::{var_name}"] = entry

    return {
        "module_id": module_id,
        "built_from_version": version,
        "vars": vars_obj,
    }


def _extract_all_inputs(detail: dict) -> dict[str, list[dict]]:
    """
    Complete root+submodule input list from a registry module detail JSON
    (complete-interface-in-one-call design), keyed by the SAME scope
    convention `vars` uses ("root", or a submodule's directory name) -
    EVERY input, not just `type = any` ones, each as
    {name, type, required, default, description}. A "wrappers" submodule is
    skipped (never a real submodule scope - mirrors find_any_vars). Pure,
    offline: `detail` is the JSON dict already fetched, no I/O here.
    """

    def _entry(item: dict) -> dict:
        return {
            "name": item.get("name", ""),
            "type": item.get("type", ""),
            "required": bool(item.get("required", False)),
            "default": item.get("default", "") or "",
            "description": item.get("description", "") or "",
        }

    root_inputs = (detail.get("root") or {}).get("inputs") or []
    all_inputs: dict[str, list[dict]] = {"root": [_entry(item) for item in root_inputs]}
    for submodule in detail.get("submodules") or []:
        name = submodule.get("name")
        if not name or name == "wrappers":
            continue
        all_inputs[name] = [_entry(item) for item in submodule.get("inputs") or []]
    return all_inputs


def _extract_all_outputs(detail: dict) -> dict[str, list[dict]]:
    """
    Complete root+submodule output list from a registry module detail JSON
    (complete-interface-in-one-call design, outputs half), keyed by the SAME
    scope convention `all_inputs` uses ("root", or a submodule's directory
    name) - EVERY output, each as {name, description}. Outputs carry no
    type/required/default in the Registry API, unlike inputs. A "wrappers"
    submodule is skipped (never a real submodule scope - mirrors
    _extract_all_inputs). Pure, offline: `detail` is the JSON dict already
    fetched, no I/O here.
    """

    def _entry(item: dict) -> dict:
        return {
            "name": item.get("name", ""),
            "description": item.get("description", "") or "",
        }

    root_outputs = (detail.get("root") or {}).get("outputs") or []
    all_outputs: dict[str, list[dict]] = {"root": [_entry(item) for item in root_outputs]}
    for submodule in detail.get("submodules") or []:
        name = submodule.get("name")
        if not name or name == "wrappers":
            continue
        all_outputs[name] = [_entry(item) for item in submodule.get("outputs") or []]
    return all_outputs


def _attach_all_interface(overlay: dict, module_id: str, version: str, *, fetch: Callable[[str], bytes] | None) -> None:
    """
    Fetch the registry detail for `module_id`@`version` ONCE and merge its
    complete input AND output lists into `overlay["all_inputs"]`/
    `overlay["all_outputs"]`, in place. Best-effort: a detail-fetch failure
    (transient network error, malformed JSON) leaves `overlay` exactly as
    `build_overlay_from_source` produced it - vars-only, neither key set -
    rather than failing the whole build over a nicety that was already
    reached once (successfully) inside fetch_module_source to resolve the
    GitHub source. Both keys come from the SAME detail response, so this is
    one fetch, not two.
    """
    detail = fetch_module_detail(module_id, version, fetch=fetch)
    if detail is not None:
        overlay["all_inputs"] = _extract_all_inputs(detail)
        overlay["all_outputs"] = _extract_all_outputs(detail)


def build_module_overlay(
    module_id: str,
    version: str,
    *,
    fetch: Callable[[str], bytes] | None = None,
    workdir: str | Path | None = None,
) -> dict | None:
    """
    Build the full committed overlay for `module_id`@`version` (real network
    unless `fetch` is injected). `workdir`, when given, is used as the source
    extraction directory directly (and NOT cleaned up by this function);
    otherwise a temp directory is created and removed automatically.

    Two independent halves, in this order:

    1. `vars` (any-typed input examples/observed field names): fetches the
       module's GitHub source (`fetch_module_source`) and, if that succeeds,
       runs the pure/offline extractors via `build_overlay_from_source`. Set
       only when the source fetch succeeds AND the module has at least one
       `type = any` input.
    2. `all_inputs`/`all_outputs` (every root+submodule input/output, not
       just any-typed ones): a registry detail fetch, always attempted
       regardless of whether step 1 succeeded (see `_attach_all_interface`).

    A failure in either half never fails the other - a module whose GitHub
    source cannot be resolved (network error, non-GitHub source, no matching
    tag) still gets all_inputs/all_outputs with no `vars` key; a transient
    failure on the second (all_inputs/all_outputs) detail fetch leaves `vars`
    intact with neither key set. Returns None only when NEITHER half produced
    anything - nothing at all to write; the caller then keeps serving the
    honest curated doc exactly as before this feature existed.
    """
    overlay = {"module_id": module_id, "built_from_version": version}

    def _attach_vars(source_dir: Path) -> None:
        vars_overlay = build_overlay_from_source(module_id, version, source_dir)
        if vars_overlay is not None:
            overlay["vars"] = vars_overlay["vars"]

    if workdir is not None:
        source_dir = fetch_module_source(module_id, version, Path(workdir), fetch=fetch)
        if source_dir is not None:
            _attach_vars(source_dir)
    else:
        with tempfile.TemporaryDirectory(prefix="tfmod_any_overlay_") as tmp:
            source_dir = fetch_module_source(module_id, version, Path(tmp), fetch=fetch)
            if source_dir is not None:
                _attach_vars(source_dir)

    _attach_all_interface(overlay, module_id, version, fetch=fetch)

    if "vars" not in overlay and "all_inputs" not in overlay:
        return None
    return overlay


# --------------------------------------------------------------------------- #
# Serialization - deterministic (sorted keys, stable list order from the pure
# extractors) so a re-run on unchanged source diffs clean.
# --------------------------------------------------------------------------- #


def serialize_overlay(overlay: dict) -> str:
    return json.dumps(overlay, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _overlay_filename(module_id: str) -> str:
    return module_id.replace("/", "__") + ".json"


def write_overlay(overlay: dict, out_dir: str | Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / _overlay_filename(overlay["module_id"])
    path.write_text(serialize_overlay(overlay), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# Coverage summary - reuses tfmod_any_examples.coverage_report per built
# module so the number is measured on every run, never remembered/hardcoded.
# --------------------------------------------------------------------------- #


def _sum_coverage(reports: list[dict]) -> dict[str, int]:
    totals = {"covered": 0, "trivial_only": 0, "none": 0}
    for report in reports:
        for key in totals:
            totals[key] += report.get(key, 0)
    return totals


def _print_summary(
    written: list[str],
    no_vars: list[str],
    fetch_failed: list[str],
    coverage_totals: dict[str, int],
    out=sys.stdout,
) -> None:
    with_vars = len(written) - len(no_vars)
    print(
        f"any-overlay build: {len(written)} overlay(s) written "
        f"({with_vars} with vars, {len(no_vars)} without vars), "
        f"{len(fetch_failed)} module(s) skipped (both source and registry detail fetch failed)",
        file=out,
    )
    if fetch_failed:
        print("  fetch failed: " + ", ".join(sorted(fetch_failed)), file=out)
    total_vars = sum(coverage_totals.values())
    if total_vars:
        print(
            f"any-var coverage across built modules ({total_vars} vars): "
            f"covered={coverage_totals['covered']} "
            f"trivial_only={coverage_totals['trivial_only']} "
            f"none={coverage_totals['none']}",
            file=out,
        )


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build committed any-var overlay JSON files (model/any_overlay/) from catalog module source."
    )
    parser.add_argument(
        "module_ids",
        nargs="*",
        help='Specific module_id(s) to build, e.g. "terraform-aws-modules/s3-bucket/aws". '
        "Omit and pass --all to build the full catalog instead.",
    )
    parser.add_argument("--all", action="store_true", help="Build overlays for every catalog module.")
    parser.add_argument(
        "--modules-dir", default=str(MODULES_DIR), help="Catalog markdown docs root (default: modules/)."
    )
    parser.add_argument(
        "--out-dir", default=str(OVERLAY_DIR), help="Overlay output directory (default: model/any_overlay/)."
    )
    args = parser.parse_args(argv)

    if not args.all and not args.module_ids:
        parser.error("pass one or more module_ids, or --all")

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("build_any_overlay")

    catalog = dict(discover_catalog_modules(args.modules_dir))
    if args.all:
        targets = sorted(catalog.items())
    else:
        targets = []
        for module_id in args.module_ids:
            if module_id not in catalog:
                logger.warning(
                    f"{module_id}: not found in the catalog (no Module ID/Latest Version bullet pair); skipping"
                )
                continue
            targets.append((module_id, catalog[module_id]))

    written: list[str] = []
    no_vars: list[str] = []
    fetch_failed: list[str] = []
    reports: list[dict] = []

    for module_id, version in targets:
        with tempfile.TemporaryDirectory(prefix="tfmod_any_overlay_") as tmp:
            source_dir = fetch_module_source(module_id, version, Path(tmp))
            overlay = {"module_id": module_id, "built_from_version": version}

            if source_dir is None:
                logger.warning(f"{module_id}@{version}: source fetch failed; vars omitted for this module")
            else:
                reports.append(coverage_report(source_dir))
                vars_overlay = build_overlay_from_source(module_id, version, source_dir)
                if vars_overlay is not None:
                    overlay["vars"] = vars_overlay["vars"]

            _attach_all_interface(overlay, module_id, version, fetch=None)

            if "vars" not in overlay and "all_inputs" not in overlay:
                fetch_failed.append(module_id)
                logger.warning(
                    f"{module_id}@{version}: source and registry detail fetch both failed; "
                    "skipping (no artifact written, served as honest curated doc)"
                )
                continue

            if "vars" not in overlay:
                no_vars.append(module_id)

            path = write_overlay(overlay, args.out_dir)
            written.append(module_id)
            var_count = len(overlay.get("vars", {}))
            logger.info(f"{module_id}@{version}: wrote {path} ({var_count} any-var(s))")

    _print_summary(written, no_vars, fetch_failed, _sum_coverage(reports))
    return 0


if __name__ == "__main__":
    sys.exit(main())
