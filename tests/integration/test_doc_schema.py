"""Schema-integrity guards for the curated module documentation.

These tests are the mechanism that keeps `get_module`'s section machinery working
as the corpus evolves. They fail CI the moment a new or edited doc drifts away
from the heading contract the server relies on:

* every doc carries the universal core headings (no missing, no duplicates), so
  the always-included orientation context is always present;
* every doc exposes its interface via one of the three recognised schemes
  (split / combined `Main Module:`/`Root Module:` / submodule-only), so the
  `inputs`/`outputs`/`examples` logical keys always resolve to a real section
  instead of silently reporting "not found" (the BUG-1 failure mode); and
* the default orientation head stays well-formed and compact.
"""

import re
from pathlib import Path

import pytest

from tfmod_mcp_server import filter_module_sections, orientation_head

DOCS = sorted((Path(__file__).parent.parent.parent / "modules/terraform-aws-modules").glob("*.md"))

# Headings that must appear in every curated doc: the high-signal context the
# orientation head builds from. Includes the two orientation keys the head
# requests (Key Features / Main Use Cases) so a future doc cannot drop one and
# leave get_module emitting a "Requested sections not found" footer.
UNIVERSAL_CORE_HEADINGS = (
    "Description",
    "Module Information",
    "Key Features",
    "Main Use Cases",
    "Best Practices",
    "Additional Resources",
    "Notes for AI Agents",
)

# Logical keys whose resolution the server guarantees for every doc.
INTERFACE_KEYS = ("inputs", "outputs", "examples")

_H2 = re.compile(r"^## (.+)$", re.MULTILINE)


def _headings(text: str) -> list[str]:
    return [m.group(1).strip() for m in _H2.finditer(text)]


def _id(p: Path) -> str:
    return p.name


def test_docs_directory_is_populated():
    assert len(DOCS) >= 50, f"expected the full curated catalog, found {len(DOCS)} docs"


@pytest.mark.parametrize("doc", DOCS, ids=_id)
def test_no_doc_opens_with_yaml_frontmatter(doc):
    """RC4 #4 lint guard: a curated page must NOT open with a YAML front-matter
    block. The parser reads metadata from `## Module Information`, so a leading
    `---`/`module_name:`/`keywords:` fence is redundant and leaks into the
    get_module and search-inline renders as raw YAML (measured on wafv2 over
    four runs). Keep the catalog fence-free at build time."""
    head = doc.read_text().lstrip()
    assert not head.startswith("---"), (
        f"{doc.name}: opens with a YAML front-matter fence; move any metadata into "
        f"`## Module Information` and drop the block (it renders as raw YAML)."
    )


@pytest.mark.parametrize("doc", DOCS, ids=_id)
def test_every_doc_has_universal_core_headings(doc):
    """Missing a core heading would drop always-on context from every response."""
    headings = _headings(doc.read_text())
    missing = [h for h in UNIVERSAL_CORE_HEADINGS if h not in headings]
    assert not missing, f"{doc.name}: missing core heading(s) {missing}"


@pytest.mark.parametrize("doc", DOCS, ids=_id)
def test_no_duplicate_core_headings(doc):
    """A duplicated core heading breaks section splitting and dedup."""
    headings = _headings(doc.read_text())
    dupes = [h for h in UNIVERSAL_CORE_HEADINGS if headings.count(h) > 1]
    assert not dupes, f"{doc.name}: duplicated core heading(s) {dupes}"


@pytest.mark.parametrize("doc", DOCS, ids=_id)
def test_every_doc_uses_a_recognized_interface_scheme(doc):
    """Each doc must expose its interface via one of the three allowed schemes."""
    headings_lower = [h.lower() for h in _headings(doc.read_text())]
    split = any(h == "main input variables" for h in headings_lower)
    combined = any(h.startswith(("main module", "root module")) for h in headings_lower)
    submodule_only = any(h.startswith("submodule") for h in headings_lower)
    assert split or combined or submodule_only, (
        f"{doc.name}: no recognised interface section "
        "(expected 'Main Input Variables', a 'Main Module:'/'Root Module:' section, "
        "or numbered submodule sections)"
    )


@pytest.mark.parametrize("doc", DOCS, ids=_id)
def test_interface_keys_resolve_for_every_doc(doc):
    """inputs/outputs/examples must resolve to a real section on every doc (BUG-1 guard)."""
    text = doc.read_text()
    filtered = filter_module_sections(text, list(INTERFACE_KEYS))
    assert "Requested sections not found" not in filtered, (
        f"{doc.name}: interface keys {INTERFACE_KEYS} did not resolve — "
        "the doc's headings break get_module(sections=...) section filtering"
    )


@pytest.mark.parametrize("doc", DOCS, ids=_id)
def test_orientation_head_is_well_formed(doc):
    """The default orientation head carries core context and stays smaller than the full doc."""
    text = doc.read_text()
    head = orientation_head(text)
    assert "## Module Information" in head, f"{doc.name}: orientation head missing Module Information"
    assert len(head) <= len(text) + 512, f"{doc.name}: orientation head unexpectedly larger than full doc"


@pytest.mark.parametrize("doc", DOCS, ids=_id)
def test_orientation_head_reports_nothing_missing(doc):
    """The default head's own keys (features/use-cases) must resolve on every doc.

    Guards against a doc dropping Key Features or Main Use Cases and get_module
    then emitting a "Requested sections not found" footer on its default response.
    """
    head = orientation_head(doc.read_text())
    assert "Requested sections not found" not in head, (
        f"{doc.name}: orientation head reports missing sections — a heading the "
        "default view requests (Key Features / Main Use Cases) is absent"
    )


@pytest.mark.parametrize("doc", DOCS, ids=_id)
def test_submodule_inventory_surfaced_in_head(doc):
    """A1: a doc's ## Submodules inventory (if present) is inlined in the head.

    Guards the head-assembly contract: when a doc carries the compact submodule
    inventory, the orientation head must surface that exact heading inline (so an
    agent sees which submodule to reach for) without expanding the far larger
    ``## Submodule N:`` deep-dive sections.
    """
    text = doc.read_text()
    if "Submodules" not in _headings(text):
        pytest.skip(f"{doc.name}: no submodule inventory")
    head = orientation_head(text)
    assert "## Submodules" in head, f"{doc.name}: submodule inventory not surfaced in the orientation head"
