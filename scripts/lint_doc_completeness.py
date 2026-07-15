#!/usr/bin/env python3
"""Completeness linter for module docs: flags collapsed/opaque-typed input rows.

Offline modes (`--check`, no flags) operate only on local `.md` files under
`modules/terraform-aws-modules/`. The `--suggest MODULE` mode additionally
fetches the live Terraform Registry type for each flagged variable and prints
the exact top-level field roster to append (or "GENUINE any" when the live
type has no object body). Network access is confined to `--suggest` and is
guarded by an https-scheme check plus a try/except so the offline modes never
import-fail or exit non-zero due to network trouble.

Exports (importable for tests):
- Flag: dataclass (line, variable, type_cell)
- find_opaque_rows(md_text) -> list[Flag]
- top_level_fields(type_str) -> list[str]
- roster(fields, cap=8) -> str
- check_corpus(docs_dir, allowlist) -> list[str]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REGISTRY_API_BASE = "https://registry.terraform.io/v1/modules"

# --- Regexes (verbatim from the design; the corpus baseline is calibrated to
# exactly these) ---------------------------------------------------------
HEADER_RE = re.compile(r"^#{2,3}\s+.*Input", re.IGNORECASE)
OPAQUE_RE = re.compile(
    r"^`(any|object|map\(object\)|list\(object\)|set\(object\)|map\(any\)|object\(\))`$",
    re.IGNORECASE,
)
EXPANDED_RE = re.compile(r"object\(\{", re.IGNORECASE)
HINT_RE = re.compile(
    # `per-\w` is its own alternative: a word boundary cannot follow the hyphen,
    # so `\bper-\b` would never match a phrase like "per-resource".
    r"`[^`]+`|[{}\[\]]|\bper-\w|\b(shape|keys?|fields?|nest\w*|each|see|submodule|example)\b",
    re.IGNORECASE,
)
SEPARATOR_RE = re.compile(r"^:?-+:?$")


@dataclass(frozen=True)
class Flag:
    """One flagged input row: 1-based line number, variable name, raw Type cell."""

    line: int
    variable: str
    type_cell: str


def _split_row(line: str) -> list[str] | None:
    """Split a markdown table row into its cell strings, or None if not a row."""
    raw = line.strip()
    if not raw.startswith("|"):
        return None
    parts = raw.split("|")
    # Drop the leading empty segment before the first pipe, and the trailing
    # empty segment after a final pipe (rows normally end with "|").
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def find_opaque_rows(md_text: str) -> list[Flag]:
    """Flag Main Input Variables table rows with an opaque, unexpanded Type and no
    Description shape signal (see OPAQUE_RE/EXPANDED_RE/HINT_RE above)."""
    lines = md_text.splitlines()
    flags: list[Flag] = []
    i = 0
    n = len(lines)
    while i < n:
        if HEADER_RE.match(lines[i]):
            i += 1
            while i < n and not lines[i].lstrip().startswith("#"):
                cells = _split_row(lines[i])
                if cells is not None and len(cells) >= 4:
                    if not all(SEPARATOR_RE.match(c) for c in cells):
                        variable = cells[0].split("/")[0].strip().strip("` ")
                        type_cell = cells[1]
                        desc = " ".join(cells[3:])
                        if (
                            OPAQUE_RE.search(type_cell)
                            and not EXPANDED_RE.search(type_cell)
                            and not HINT_RE.search(desc)
                        ):
                            flags.append(Flag(line=i + 1, variable=variable, type_cell=type_cell))
                i += 1
        else:
            i += 1
    return flags


def top_level_fields(type_str: str) -> list[str]:
    """Top-level attribute names of the first `object({...})` body in an HCL type
    string. Handles `map(object({...}))`/`list(object({...}))`/`set(object({...}))`
    by locating the first `object({`. Returns [] when there is no object body."""
    match = re.search(r"object\(\{", type_str, re.IGNORECASE)
    if not match:
        return []
    brace_start = match.end() - 1  # index of the body-opening "{"
    depth = 0
    body_start = brace_start + 1
    body_end = len(type_str)
    i = brace_start
    while i < len(type_str):
        char = type_str[i]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                body_end = i
                break
        i += 1
    body = type_str[body_start:body_end]

    fields: list[str] = []
    seen: set[str] = set()
    segment: list[str] = []
    nest_depth = 0

    def flush() -> None:
        text = "".join(segment).strip()
        if not text:
            return
        name_match = re.match(r"^([A-Za-z_]\w*)\s*=", text)
        if name_match:
            name = name_match.group(1)
            if name not in seen:
                seen.add(name)
                fields.append(name)

    for char in body:
        if char in "{([":
            nest_depth += 1
            segment.append(char)
        elif char in "})]":
            nest_depth -= 1
            segment.append(char)
        elif char == "," and nest_depth == 0:
            flush()
            segment = []
        elif char == "\n" and nest_depth == 0:
            flush()
            segment = []
        else:
            segment.append(char)
    flush()
    return fields


def roster(fields: list[str], cap: int = 8) -> str:
    """Render '— fields: `a`, `b`, `c`' (all, when <= cap) or a capped version with
    an explicit '(N shown; see grep_module_docs)' tail."""
    if not fields:
        return ""
    if len(fields) <= cap:
        shown = fields
        tail = ""
    else:
        shown = fields[:cap]
        tail = f", … ({cap} shown; see grep_module_docs)"
    rendered = ", ".join(f"`{f}`" for f in shown)
    return f"— fields: {rendered}{tail}"


def check_corpus(docs_dir: str, allowlist: set[str]) -> list[str]:
    """ "<module.md>::<variable>" for every flagged row across docs_dir not in
    allowlist."""
    out: list[str] = []
    for path in sorted(Path(docs_dir).glob("*.md")):
        text = path.read_text()
        for flag in find_opaque_rows(text):
            key = f"{path.name}::{flag.variable}"
            if key not in allowlist:
                out.append(key)
    return out


def _load_allowlist(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    out: set[str] = set()
    for line in path.read_text().splitlines():
        entry = line.split("#", 1)[0].strip()
        if entry:
            out.add(entry)
    return out


def fetch_module_inputs(module: str, namespace: str = "terraform-aws-modules", provider: str = "aws") -> dict[str, str]:
    """Merged {variable_name: hcl_type_str} from a module's root inputs and every
    submodule's inputs (root wins on name collision). Raises on network/parse
    failure -- callers wrap this in try/except."""
    url = f"{REGISTRY_API_BASE}/{namespace}/{module}/{provider}"
    if not url.startswith("https://"):
        raise ValueError(f"refusing non-https URL: {url}")
    with urllib.request.urlopen(url, timeout=25) as resp:  # noqa: S310 - scheme guarded above
        data: dict[str, Any] = json.load(resp)

    inputs: dict[str, str] = {}
    root = data.get("root") or {}
    for inp in root.get("inputs") or []:
        name = inp.get("name")
        if name:
            inputs[name] = inp.get("type") or ""
    for sub in data.get("submodules") or []:
        for inp in sub.get("inputs") or []:
            name = inp.get("name")
            if name and name not in inputs:
                inputs[name] = inp.get("type") or ""
    return inputs


def _classify_and_print(flag: Flag, inputs: dict[str, str]) -> None:
    type_str = inputs.get(flag.variable, "")
    fields = top_level_fields(type_str) if type_str else []
    if not fields:
        print(f"{flag.variable}: class=1 (any) -> GENUINE any (example-keys or xref or allowlist)")
        return
    cls = 2 if len(type_str) <= 350 else 3
    print(f"{flag.variable}: class={cls} ({len(type_str)} chars) -> {roster(fields)}")


def cmd_suggest(module: str, docs_dir: str) -> None:
    doc_path = Path(docs_dir) / f"{module}.md"
    if not doc_path.is_file():
        print(f"no local doc for module {module!r} at {doc_path}")
        return
    flags = find_opaque_rows(doc_path.read_text())
    if not flags:
        print(f"{module}: no flagged rows")
        return

    try:
        inputs = fetch_module_inputs(module)
    except Exception as exc:  # noqa: BLE001 - degrade to offline-safe report
        print(f"fetch failed: {exc}")
        inputs = {}

    for flag in flags:
        _classify_and_print(flag, inputs)


def cmd_check(docs_dir: str, allowlist_path: Path) -> None:
    allowlist = _load_allowlist(allowlist_path)
    unresolved = check_corpus(docs_dir, allowlist)
    for key in unresolved:
        print(key)
    if unresolved:
        sys.exit(1)


def cmd_report(docs_dir: str) -> None:
    for path in sorted(Path(docs_dir).glob("*.md")):
        for flag in find_opaque_rows(path.read_text()):
            print(f"{path.name}:{flag.line} {flag.variable} {flag.type_cell}")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    default_docs_dir = repo_root / "modules" / "terraform-aws-modules"
    default_allowlist = repo_root / "tests" / "fixtures" / "doc_completeness_allowlist.txt"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="CI guard: exit 1 if any unallowlisted opaque row remains")
    parser.add_argument("--allowlist", default=None, help=f"path to allowlist file (default: {default_allowlist})")
    parser.add_argument(
        "--suggest", metavar="MODULE", default=None, help="fetch registry types and print field rosters for MODULE"
    )
    parser.add_argument("--docs-dir", default=None, help=f"docs directory (default: {default_docs_dir})")
    args = parser.parse_args()

    docs_dir = args.docs_dir or str(default_docs_dir)

    if args.suggest:
        cmd_suggest(args.suggest, docs_dir)
        return

    if args.check:
        allowlist_path = Path(args.allowlist) if args.allowlist else default_allowlist
        cmd_check(docs_dir, allowlist_path)
        return

    cmd_report(docs_dir)


if __name__ == "__main__":
    main()
