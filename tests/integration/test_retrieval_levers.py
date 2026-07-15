"""Tests for the 0.22.0 retrieval-levers (spec 2026-07-15).

Offline: curated docs + local index only. Covers L1 (lean modules_list), L4
(default-head input-table cap), L6 (non-top-1 metadata trim), L2/L7/L8 (search
confidence signal), L3 (expand_top), L5 (submodule-section scoping).
"""

import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.integration import PROJECT_ROOT
from tfmod_mcp_server import (
    SearchWeights,
    ServerStateManager,
    filter_module_sections,
    get_module_impl,
    modules_list_impl,
    orientation_head,
    search_modules_impl,
)
from tfmod_search_lib import load_index

DOCS = PROJECT_ROOT / "modules" / "terraform-aws-modules"


def _doc(module: str) -> str:
    return (DOCS / f"{module}.md").read_text()


@pytest.fixture(scope="module")
def state():
    logger = logging.getLogger("test_retrieval_levers")
    logger.addHandler(logging.NullHandler())
    index_path = PROJECT_ROOT / "model" / "tfmod_e5_small_index.pkl"
    if not index_path.exists():
        pytest.skip(f"Index file not found at {index_path}")
    index = load_index(str(index_path), logger)
    ServerStateManager.reset()
    st = ServerStateManager.initialize(
        index=index,
        weights=SearchWeights(w_kw=2.0, w_exact=3.0, w_bm25=1.0, w_sem=1.0),
        index_path=index_path,
        logger=logger,
    )
    yield st
    ServerStateManager.reset()


# --------------------------------------------------------------------------- #
# L6 — non-top-1 metadata trim.
# --------------------------------------------------------------------------- #
def test_l6_rank1_keeps_full_metadata(state) -> None:
    out = search_modules_impl("s3 bucket with encryption", state, top_k=3)
    top = out.results[0]
    assert top.keywords, "rank-1 must keep its full keyword array"


def test_l6_lower_ranks_drop_keywords_and_clip_description(state) -> None:
    out = search_modules_impl("s3 bucket with encryption", state, top_k=3)
    assert len(out.results) >= 2, "need at least 2 results to test the trim"
    for hit in out.results[1:]:
        assert hit.keywords == [], f"rank>=2 hit {hit.module_name} must drop keywords"
        assert len(hit.description) <= 141, (
            f"rank>=2 hit {hit.module_name} description must be clipped (<=141 chars), " f"got {len(hit.description)}"
        )


# --------------------------------------------------------------------------- #
# L1 — lean modules_list (compact default, full behind detail=full).
# --------------------------------------------------------------------------- #
def test_l1_compact_is_default_and_omits_keywords(state) -> None:
    out = modules_list_impl(state)
    assert out.count == len(out.modules) > 0
    for item in out.modules:
        assert not hasattr(item, "keywords"), "compact items must not carry keyword arrays"
        assert item.module_id, f"{item.module_name}: compact must keep module_id (grep coordinate)"
        assert item.latest_version, f"{item.module_name}: compact must keep latest_version"
        assert len(item.purpose) <= 120, f"{item.module_name}: purpose must be clipped (<=120), got {len(item.purpose)}"


def test_l1_full_detail_restores_keywords(state) -> None:
    out = modules_list_impl(state, detail="full")
    assert out.count == len(out.modules) > 0
    assert any(item.keywords for item in out.modules), "detail=full must restore keyword arrays"
    for item in out.modules:
        assert hasattr(item, "keywords")


def test_l1_compact_is_much_smaller_than_full(state) -> None:
    compact = modules_list_impl(state)
    full = modules_list_impl(state, detail="full")
    assert (
        len(compact.model_dump_json()) < len(full.model_dump_json()) * 0.6
    ), "compact modules_list must be well under 60% of the full dump size"


# --------------------------------------------------------------------------- #
# L4 — cap the default-head input table to required rows.
# --------------------------------------------------------------------------- #
L4_MODULES = ["s3-bucket", "vpc", "elasticache", "apigateway-v2", "opensearch"]


def _uncapped_head(doc: str) -> str:
    """Rebuild the pre-L4 head (same section selection as orientation_head, no cap)."""
    return filter_module_sections(
        doc,
        ["features", "use-cases", "inputs"],
        extra_exact_titles=("Submodules",),
        interface_scope="root",
        silent_keys=frozenset({"features", "use-cases", "inputs"}),
    )


@pytest.mark.parametrize("module", L4_MODULES)
def test_l4_capped_head_is_smaller_than_full_inputs(module: str) -> None:
    doc = _doc(module)
    head = orientation_head(doc)
    bypassed = _uncapped_head(doc)
    full_inputs = filter_module_sections(doc, ["inputs"])
    assert len(head) < len(bypassed) or len(head) < len(full_inputs), (
        f"{module}: capped default head ({len(head)} chars) must be smaller than either "
        f"the cap-bypassed head ({len(bypassed)} chars) or the full sections=['inputs'] "
        f"view ({len(full_inputs)} chars)"
    )


@pytest.mark.parametrize("module", L4_MODULES)
def test_l4_capped_head_still_has_a_real_row_and_pointer(module: str) -> None:
    head = orientation_head(_doc(module))
    assert "| `" in head, f"{module}: capped head must still contain a real input row"
    assert "optional inputs" in head, f"{module}: capped head must carry the drop-count pointer"


@pytest.mark.parametrize("module", L4_MODULES)
def test_l4_sections_inputs_still_returns_full_table(module: str, state) -> None:
    doc = _doc(module)
    head = orientation_head(doc)
    full = get_module_impl(module, state, sections=["inputs"])
    head_rows = head.count("| `")
    full_rows = full.count("| `")
    assert full_rows >= head_rows, (
        f"{module}: sections=['inputs'] ({full_rows} rows) must not be smaller than "
        f"the capped default head ({head_rows} rows)"
    )
    assert "optional inputs" not in full, f"{module}: full sections=['inputs'] must not carry the head-only pointer"
