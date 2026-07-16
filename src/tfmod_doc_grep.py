"""
Pure, offline regex-grep engine over an assembled Terraform Registry module document.

The assembled text (see tfmod_registry_docs.assemble_document) uses "=====" delimited
section-marker lines (e.g. "===== ROOT README =====", "===== SUBMODULE: flow-log ====="
with inner "--- readme ---" / "--- inputs ---" / "--- outputs ---" sub-markers, and
"===== EXAMPLE: <name> =====") to structure the document. This module walks that text,
tracks the current section label, and returns matching lines with surrounding context —
independent of network access or caching, so it is fully offline-testable.

Exports:
- DocMatch: a single matching line plus its section label and context
- grep_document(text, pattern, ...) -> (matches, total_matches, available_sections)
- SECTION_MARK: the "=====" marker string used to delimit sections
"""

import re
from dataclasses import dataclass

SECTION_MARK = "====="

_MAIN_MARKER_RE = re.compile(r"^=====\s+(.*?)\s+=====\s*$")
_SUB_MARKER_RE = re.compile(r"^---\s+(.*?)\s+---\s*$")

_ROOT_LABELS = {
    "ROOT README": "root/readme",
    "ROOT INPUTS": "root/inputs",
    "ROOT OUTPUTS": "root/outputs",
    "ROOT RESOURCES": "root/resources",
}

_SUB_LABEL_SUFFIXES = {
    "readme": "readme",
    "inputs": "inputs",
    "outputs": "outputs",
}


@dataclass
class DocMatch:
    section: str
    line_number: int  # 1-based, within the full assembled text
    line: str
    before: list[str]
    after: list[str]
    enclosing: str | None = None


def _label_lines(lines: list[str]) -> tuple[list[str | None], list[bool]]:
    """
    Scan lines in order, tracking the current section label as section markers are
    encountered. Returns (section label per line, is-marker-line per line). Marker
    lines are labeled with the section they open (or None for the top MODULE line).
    """
    sections: list[str | None] = []
    is_marker: list[bool] = []
    current_section: str | None = None
    current_submodule: str | None = None

    for raw in lines:
        stripped = raw.strip()
        main_m = _MAIN_MARKER_RE.match(stripped)

        if main_m:
            header = main_m.group(1).strip()
            if header.startswith("SUBMODULE:"):
                current_submodule = header.split(":", 1)[1].strip()
                current_section = None  # set by the inner "--- ... ---" marker below
            elif header.startswith("EXAMPLE:"):
                current_submodule = None
                name = header.split(":", 1)[1].strip()
                current_section = f"example:{name}/readme"
            elif header in _ROOT_LABELS:
                current_submodule = None
                current_section = _ROOT_LABELS[header]
            else:
                # Top "MODULE ..." line (or anything unrecognized) opens no section.
                current_submodule = None
                current_section = None
            sections.append(current_section)
            is_marker.append(True)
            continue

        sub_m = _SUB_MARKER_RE.match(stripped)
        if sub_m:
            key = sub_m.group(1).strip().lower()
            if current_submodule is not None and key in _SUB_LABEL_SUFFIXES:
                current_section = f"submodule:{current_submodule}/{_SUB_LABEL_SUFFIXES[key]}"
            sections.append(current_section)
            is_marker.append(True)
            continue

        sections.append(current_section)
        is_marker.append(False)

    return sections, is_marker


def _collect_available_sections(sections: list[str | None]) -> list[str]:
    """Ordered, de-duplicated list of section labels as first encountered."""
    seen: set[str] = set()
    ordered: list[str] = []
    for label in sections:
        if label is not None and label not in seen:
            seen.add(label)
            ordered.append(label)
    return ordered


def _scope_matches(label: str | None, scope: list[str] | None) -> bool:
    if scope is None:
        return True
    if label is None:
        return False
    for key in scope:
        if key == "root" and label.startswith("root/"):
            return True
        if key == "submodules" and label.startswith("submodule:"):
            return True
        if key == "examples" and label.startswith("example:"):
            return True
        if key in ("inputs", "outputs", "resources") and label.endswith(f"/{key}"):
            return True
    return False


def _find_enclosing(lines: list[str], is_marker: list[bool], sections: list[str | None], idx: int) -> str | None:
    """
    Find the nearest enclosing "- <name> | ..." list-item header for a match on
    a continuation line (RC2 C1).

    An input/output/resource row is a single logical entry that can span
    multiple physical lines when a field (e.g. a nested object/map type)
    embeds newlines. Only the row's first physical line starts with "- "; a
    match landing on a later line of that same row would otherwise lose the
    row's name entirely. Walk backward from idx over non-marker lines in the
    SAME section, stopping at the nearest "- "-prefixed line (the header) or
    at the section boundary (marker line or section-label change), whichever
    comes first.

    Returns None when the line at idx itself starts with "- " (it is its own
    header) or when no enclosing header is found within the section.
    """
    if lines[idx].strip().startswith("- "):
        return None

    label = sections[idx]
    j = idx - 1
    while j >= 0:
        if is_marker[j] or sections[j] != label:
            break
        stripped = lines[j].strip()
        if stripped.startswith("- "):
            return stripped
        j -= 1
    return None


def _gather_context(lines: list[str], is_marker: list[bool], start_idx: int, step: int, count: int) -> list[str]:
    """
    Walk from start_idx in direction `step` (-1 for before, +1 for after), skipping
    marker lines, collecting up to `count` non-marker line contents. May cross into
    an adjacent section. Returned in reading order.
    """
    collected: list[str] = []
    idx = start_idx + step
    while 0 <= idx < len(lines) and len(collected) < count:
        if not is_marker[idx]:
            collected.append(lines[idx])
        idx += step
    if step < 0:
        collected.reverse()
    return collected


def grep_document(
    text: str,
    pattern: str,
    *,
    case_sensitive: bool = False,
    context_lines: int = 2,
    scope: list[str] | None = None,
    max_matches: int = 50,
) -> tuple[list[DocMatch], int, list[str]]:
    """
    Grep an assembled module document.

    Returns (matches capped at max_matches, total logical matches before the cap,
    ordered unique list of section labels encountered in the document).

    Raises ValueError if `pattern` is not a valid regex.
    """
    try:
        flags = 0 if case_sensitive else re.IGNORECASE
        compiled = re.compile(pattern, flags)
    except re.error as e:
        raise ValueError(f"Invalid regex: {e}") from e

    lines = text.splitlines()
    sections, is_marker = _label_lines(lines)
    available_sections = _collect_available_sections(sections)

    matches: list[DocMatch] = []
    total = 0
    for idx, line in enumerate(lines):
        if is_marker[idx]:
            continue
        label = sections[idx]
        if not _scope_matches(label, scope):
            continue
        if not compiled.search(line):
            continue

        total += 1
        if len(matches) < max_matches:
            before = _gather_context(lines, is_marker, idx, -1, context_lines)
            after = _gather_context(lines, is_marker, idx, 1, context_lines)
            enclosing = _find_enclosing(lines, is_marker, sections, idx)
            matches.append(
                DocMatch(
                    section=label if label is not None else "",
                    line_number=idx + 1,
                    line=line,
                    before=before,
                    after=after,
                    enclosing=enclosing,
                )
            )

    return matches, total, available_sections
