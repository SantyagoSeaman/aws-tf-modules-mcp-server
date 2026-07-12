"""Invariant: every curated module doc carries an explicit **Module ID** header
bullet equal to the root **Source** coordinate (namespace/name/provider)."""

import re
from pathlib import Path

DOCS = sorted((Path(__file__).parent.parent.parent / "modules/terraform-aws-modules").glob("*.md"))


def _module_info(text: str) -> str:
    m = re.search(r"## Module Information\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else ""


def _bullet(section: str, key: str) -> str | None:
    m = re.search(rf"^\s*-\s*\*\*{key}\*\*:\s*`?([^`\n]+?)`?\s*$", section, re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else None


def test_every_doc_has_module_id_equal_to_root_source():
    assert DOCS, "no module docs found"
    for p in DOCS:
        section = _module_info(p.read_text())
        module_id = _bullet(section, "Module ID")
        source = _bullet(section, "Source")
        assert module_id, f"{p.name}: missing **Module ID**"
        assert re.fullmatch(r"[a-z0-9-]+/[a-z0-9-]+/[a-z0-9]+", module_id), f"{p.name}: bad id {module_id!r}"
        assert source and source.split("//")[0] == module_id, f"{p.name}: id {module_id!r} != source {source!r}"
