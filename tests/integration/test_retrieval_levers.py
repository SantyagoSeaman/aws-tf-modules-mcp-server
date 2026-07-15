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
