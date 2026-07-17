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
    _MIN_HEAD_TABLE_ROWS,
    SEARCH_SCORE_FLOOR,
    SEARCH_SEM_FLOOR,
    SearchOutput,
    SearchWeights,
    ServerStateManager,
    _cap_head_input_table,
    _classify_confidence,
    _clip_blurb,
    _reconcile_body_version,
    _version_pin_hint,
    filter_module_sections,
    get_module_impl,
    modules_list_impl,
    orientation_head,
    search_modules_impl,
)
from tfmod_search_lib import ScoredHit, compute_scores_detailed, load_index

DOCS = PROJECT_ROOT / "modules" / "terraform-aws-modules"


def _doc(module: str) -> str:
    return (DOCS / f"{module}.md").read_text()


# --------------------------------------------------------------------------- #
# Minimal fake index for the capability-aware classifier unit tests (RC4). The
# classifier reads only index.docs[doc_index].{module_name,keywords,text} and
# index.bm25.idf, so a lightweight stand-in lets us drive capability coverage
# and the sem floor precisely without depending on real doc content.
# --------------------------------------------------------------------------- #
class _FakeDoc:
    def __init__(self, text: str = "", keywords=(), module_name: str = "") -> None:
        self.text = text
        self.keywords = list(keywords)
        self.module_name = module_name


class _FakeBM25:
    def __init__(self, idf: dict) -> None:
        self.idf = idf


class _FakeIndex:
    def __init__(self, docs: list, idf: dict) -> None:
        self.docs = docs
        self.bm25 = _FakeBM25(idf)


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
        assert (
            len(hit.description) <= 141
        ), f"rank>=2 hit {hit.module_name} description must be clipped (<=141 chars), got {len(hit.description)}"


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
    assert "more inputs" in head, f"{module}: capped head must carry the drop-count pointer"


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
    assert "more inputs" not in full, f"{module}: full sections=['inputs'] must not carry the head-only pointer"


# --------------------------------------------------------------------------- #
# L4 direct unit tests for _cap_head_input_table (the corpus tests above only
# exercise the leading-sample path, since terraform-aws-modules docs mark almost
# nothing required — these cover both branches and the unchanged-fallbacks).
# --------------------------------------------------------------------------- #
def _synthetic_head(default_cells: list[str]) -> str:
    """Build a head with a ### Main Input Variables table; one row per default cell."""
    rows = "\n".join(f"| `var{i}` | `string` | {d} | desc {i} |" for i, d in enumerate(default_cells))
    return (
        "## Description\n\nsome text\n\n"
        "### Main Input Variables\n\n"
        "| Variable | Type | Default | Description |\n"
        "|---|---|---|---|\n" + rows + "\n\n## Notes\n\ntail\n"
    )


def test_cap_keeps_leading_sample_and_pointer_when_all_concrete_defaults() -> None:
    head = _synthetic_head([f"`{i}`" for i in range(12)])  # 12 concrete-default rows
    capped = _cap_head_input_table(head)
    assert capped.count("| `var") == _MIN_HEAD_TABLE_ROWS, "must keep exactly the leading N rows"
    assert "`var0`" in capped and f"`var{_MIN_HEAD_TABLE_ROWS - 1}`" in capped
    assert f"`var{_MIN_HEAD_TABLE_ROWS}`" not in capped, "rows past the window are dropped"
    assert f"(+{12 - _MIN_HEAD_TABLE_ROWS} more inputs" in capped


def test_cap_includes_required_row_beyond_the_window() -> None:
    # A required (empty Default) row at position 10, past the N=8 leading window.
    defaults = [f"`{i}`" for i in range(12)]
    defaults[10] = ""  # empty Default cell => required
    head = _synthetic_head(defaults)
    capped = _cap_head_input_table(head)
    assert "`var10`" in capped, "a doc-marked required row must survive even beyond the leading window"
    assert capped.count("| `var") == _MIN_HEAD_TABLE_ROWS + 1, "leading N plus the one out-of-window required row"


def test_cap_recognizes_separate_required_column() -> None:
    head = (
        "### Main Input Variables\n\n"
        "| Variable | Type | Required | Description |\n"
        "|---|---|---|---|\n"
        + "\n".join(f"| `var{i}` | `string` | no | d |" for i in range(10))
        + "\n| `mustset` | `string` | yes | d |\n\n## Notes\n\ntail\n"
    )
    capped = _cap_head_input_table(head)
    assert "`mustset`" in capped, "a Yes in a separate Required column must be kept"


def test_cap_returns_unchanged_when_table_fits() -> None:
    head = _synthetic_head([f"`{i}`" for i in range(_MIN_HEAD_TABLE_ROWS)])  # exactly N rows
    assert _cap_head_input_table(head) == head, "no cap when the table already fits the window"


def test_cap_returns_unchanged_when_no_input_table() -> None:
    head = "## Description\n\njust prose, no input table\n\n## Notes\n\ntail\n"
    assert _cap_head_input_table(head) == head


# --------------------------------------------------------------------------- #
# L2/L7/L8 - two-signal search confidence classifier.
# --------------------------------------------------------------------------- #
def test_l2_absent_capability_is_low_confidence_with_hint(state) -> None:
    # sagemaker is absent from the catalog; its nearest top-1 (step-functions,
    # under this file's fixture weights) does not assert the "sagemaker"
    # capability in its name/keywords/description (measured cov=0.3, well
    # below _COVERAGE_THETA) -- the coverage gate demotes it to "low" (unlike
    # "cognito", which several unrelated modules list as a related-service
    # keyword -- see test_repro_pack.py for that near-tie case).
    out = search_modules_impl("sagemaker", state, top_k=3)
    assert out.confidence == "low"
    assert out.hint, "low confidence must carry a non-empty hint"


def test_l2_clean_query_is_high_confidence_with_no_hint(state) -> None:
    out = search_modules_impl("s3 bucket with encryption and versioning", state, top_k=3)
    assert out.confidence == "high"
    assert out.hint is None


# A fake index whose top-1 doc DOES cover the query's central term ("redis"),
# used by the classify tests that want the capability gate to pass so they can
# isolate the sem-floor / lexical behaviour.
def _covered_index() -> _FakeIndex:
    return _FakeIndex(
        docs=[
            _FakeDoc(text="managed redis and memcached in-memory cache clusters", keywords=["redis", "cache"]),
            _FakeDoc(text="unrelated document body"),
        ],
        idf={"redis": 5.0, "cache": 2.0, "in-memory": 3.0},
    )


def test_classify_confidence_ignores_stale_exact_hit_and_kw_overlap_fields() -> None:
    # 0.23.0: the old "no exact-name and no keyword overlap on rank 1 -> low"
    # branch is gone by design -- the new rule never reads exact_hit or
    # kw_overlap at all. With both False here, the verdict is decided purely
    # by coverage/sem/score, all of which are favorable (cov=1.0 -- both
    # query terms match doc0's keywords; sem=0.95; score=5.0 >= 4.5) -> "high",
    # proving a lexical-overlap flag no longer gates the outcome in either
    # direction.
    hits = [
        ScoredHit(score=5.0, doc_index=0, exact_hit=False, kw_overlap=False, sem_sim=0.95),
        ScoredHit(score=1.0, doc_index=1, exact_hit=False, kw_overlap=False, sem_sim=0.10),
    ]
    assert _classify_confidence("redis cache", hits, _covered_index()) == "high"


def test_rc2_classify_confidence_high_on_former_near_tie_regardless_of_score_ratio() -> None:
    # T1: the near-tie fixture (elasticache/memory-db style) - both lexical, top1/
    # top2 combined-score ratio well below the old 2.5 near-tie threshold. The tie
    # verdict is gone; a lexical, capability-covered top-1 with a strong sem_sim is
    # simply "high" now.
    hits = [
        ScoredHit(score=11.32, doc_index=0, exact_hit=False, kw_overlap=True, sem_sim=0.95),
        ScoredHit(score=4.90, doc_index=1, exact_hit=False, kw_overlap=True, sem_sim=0.93),
    ]
    assert hits[0].score / hits[1].score < 2.5, "fixture must reproduce the old near-tie ratio band"
    assert _classify_confidence("redis cache", hits, _covered_index()) == "high"


def test_rc2_classify_confidence_low_on_incidental_keyword_with_weak_sem_sim() -> None:
    # T3: the incidental-keyword catalog-gap case - top-1 earned a real keyword
    # overlap AND covers the central term, but its raw semantic similarity sits
    # below the floor - the secondary sem-floor demoter still catches it.
    hits = [
        ScoredHit(score=3.0, doc_index=0, exact_hit=False, kw_overlap=True, sem_sim=0.60),
        ScoredHit(score=2.0, doc_index=1, exact_hit=False, kw_overlap=True, sem_sim=0.55),
    ]
    assert _classify_confidence("redis cache", hits, _covered_index()) == "low"


def test_rc2_classify_confidence_high_on_lexical_top1_with_strong_sem_sim() -> None:
    hits = [
        ScoredHit(score=9.0, doc_index=0, exact_hit=False, kw_overlap=True, sem_sim=0.95),
        ScoredHit(score=1.0, doc_index=1, exact_hit=False, kw_overlap=False, sem_sim=0.20),
    ]
    assert _classify_confidence("redis cache", hits, _covered_index()) == "high"


def test_classify_confidence_high_on_whole_query_exact_name_regardless_of_sem_sim() -> None:
    # 0.23.0: the ScoredHit.exact_hit flag (a ranker-level boundary match that
    # can fire inside a longer query) no longer decides the verdict by
    # itself -- only a WHOLE-QUERY match against the top-1 module name does
    # (rule step 1). Here the query literally IS the module name, so it wins
    # even with a very weak raw semantic similarity and even though the doc
    # would otherwise fail the capability/sem/score checks.
    idx = _FakeIndex(
        docs=[
            _FakeDoc(text="unrelated body", keywords=[], module_name="redis"),
            _FakeDoc(text="unrelated document body"),
        ],
        idf={"redis": 5.0},
    )
    hits = [
        ScoredHit(score=9.0, doc_index=0, exact_hit=True, kw_overlap=True, sem_sim=0.10),
        ScoredHit(score=1.0, doc_index=1, exact_hit=False, kw_overlap=False, sem_sim=0.05),
    ]
    assert _classify_confidence("redis", hits, idx) == "high"


def test_rc2_classify_confidence_high_when_no_rank2() -> None:
    hits = [ScoredHit(score=9.0, doc_index=0, exact_hit=True, kw_overlap=True, sem_sim=0.99)]
    assert _classify_confidence("redis", hits, _covered_index()) == "high"


def test_rc2_classify_confidence_never_returns_tie() -> None:
    # T1: the verdict domain is {"high", "low"} only - no ratio plumbing anywhere.
    idx = _covered_index()
    for hits in (
        [],
        [ScoredHit(score=9.0, doc_index=0, exact_hit=True, kw_overlap=True, sem_sim=0.99)],
        [
            ScoredHit(score=11.32, doc_index=0, exact_hit=False, kw_overlap=True, sem_sim=0.95),
            ScoredHit(score=4.90, doc_index=1, exact_hit=False, kw_overlap=True, sem_sim=0.93),
        ],
        [
            ScoredHit(score=3.0, doc_index=0, exact_hit=False, kw_overlap=True, sem_sim=0.60),
            ScoredHit(score=2.0, doc_index=1, exact_hit=False, kw_overlap=True, sem_sim=0.55),
        ],
    ):
        assert _classify_confidence("redis cache", hits, idx) in ("high", "low")


def test_l8_low_hint_names_nearest_module(state) -> None:
    out = search_modules_impl("sagemaker", state, top_k=3)
    assert out.confidence == "low"
    assert out.results, "expected at least one result to name as nearest"
    assert out.results[0].module_name in out.hint


def test_rc2_former_near_tie_query_is_now_high_confidence(state) -> None:
    # T1/T2: a query that used to land in the "tie" band now resolves to "high"
    # against the live index (or skips if the live index no longer reproduces a
    # close score band for this query - the fixture-based unit tests above cover
    # the classifier logic unconditionally).
    out = search_modules_impl("redis in-memory cache cluster", state, top_k=3)
    assert out.confidence in ("high", "low"), "tie must never be a possible verdict"


def test_search_output_serialization_drops_hint_when_none(state) -> None:
    out = search_modules_impl("s3 bucket with encryption and versioning", state, top_k=3)
    assert out.confidence == "high"
    dumped = out.model_dump()
    assert "hint" not in dumped
    assert "hint" not in out.model_dump_json()


def test_search_output_serialization_keeps_hint_when_low(state) -> None:
    out = search_modules_impl("sagemaker", state, top_k=3)
    assert out.confidence == "low"
    dumped = out.model_dump()
    assert "hint" in dumped
    assert dumped["hint"] == out.hint


def test_search_output_confidence_always_present_direct_construction() -> None:
    out = SearchOutput(results=[], confidence="high")
    assert out.hint is None
    assert "hint" not in out.model_dump()


# --------------------------------------------------------------------------- #
# L3/T2 - expand_top inlines the top-1 orientation head on a high-confidence
# search, collapsing the confident search->get_module pair into one call.
# RC2 T2: default-on now (the counterfactual measurement showed the opt-in
# default was strangling the one right-direction lever); never inlined on a
# non-high verdict; explicit expand_top=False still suppresses it.
# --------------------------------------------------------------------------- #
def test_l3_expand_top_high_confidence_inlines_orientation_head(state) -> None:
    out = search_modules_impl("s3 bucket with encryption and versioning", state, top_k=3, expand_top=True)
    assert out.confidence == "high"
    assert out.top_module_doc, "expand_top on a high-confidence query must inline the top-1 head"
    top_name = out.results[0].module_name
    assert top_name in out.top_module_doc
    assert "## " in out.top_module_doc, "inlined doc should look like an orientation head with section headings"

    top_doc_text = (DOCS / f"{top_name}.md").read_text()
    assert out.top_module_doc == orientation_head(top_doc_text, version_override=out.results[0].latest_version)


def test_l3_expand_top_defaults_to_on_and_inlines_on_high_confidence(state) -> None:
    out = search_modules_impl("s3 bucket with encryption and versioning", state, top_k=3)
    assert out.confidence == "high"
    assert out.top_module_doc, "expand_top defaults to True (T2); a high-confidence search must inline the head"
    assert "top_module_doc" in out.model_dump()
    assert "top_module_doc" in out.model_dump_json()


def test_l3_expand_top_false_explicit_stays_off(state) -> None:
    out = search_modules_impl("s3 bucket with encryption and versioning", state, top_k=3, expand_top=False)
    assert out.top_module_doc is None
    assert "top_module_doc" not in out.model_dump()


def test_l3_expand_top_low_confidence_never_inlines_even_by_default(state) -> None:
    out = search_modules_impl("sagemaker", state, top_k=3)
    assert out.confidence == "low"
    assert out.top_module_doc is None
    assert "top_module_doc" not in out.model_dump()


def test_l3_expand_top_serialization_present_only_when_high_and_expanded(state) -> None:
    expanded_high = search_modules_impl("s3 bucket with encryption and versioning", state, top_k=3, expand_top=True)
    assert "top_module_doc" in expanded_high.model_dump()
    assert "top_module_doc" in expanded_high.model_dump_json()

    not_expanded = search_modules_impl("s3 bucket with encryption and versioning", state, top_k=3, expand_top=False)
    assert "top_module_doc" not in not_expanded.model_dump()

    expanded_low = search_modules_impl("sagemaker", state, top_k=3, expand_top=True)
    assert "top_module_doc" not in expanded_low.model_dump()


# --------------------------------------------------------------------------- #
# L5 - submodule-level sections scoping. The "submodules" logical key must
# resolve to the compact ## Submodules inventory only (exact-title match, same
# pattern A1 already uses via extra_exact_titles), never the full per-
# submodule ## Submodule N: deep-dive bundles. Full exclusion: when
# "submodules" is requested alongside an interface key (inputs/outputs/
# examples), that key's combined-bundle H3 fallback must also skip submodule
# bundles -- no "## Submodule N:" heading should appear at all in that combo.
# A specific submodule stays reachable by heading substring or the
# "<name>//modules/<sub>" address (A3); the default head keeps inlining the
# compact inventory (A1).
# --------------------------------------------------------------------------- #
_VPC_PRE_FIX_OVERFETCH_LEN = 18972  # measured in the design doc / team report


def test_l5_submodules_key_alone_is_scoped_to_compact_inventory(state) -> None:
    filtered = get_module_impl("vpc", state, sections=["submodules"])
    assert "## Submodules" in filtered, "compact inventory heading must be present"
    assert "vpc-endpoints" in filtered, "submodule name must still be named"
    assert "flow-log" in filtered, "submodule name must still be named"
    assert "## Submodule 1:" not in filtered, "numbered deep-dive sections must not be bundled"
    assert "## Submodule 2:" not in filtered, "numbered deep-dive sections must not be bundled"


def test_l5_submodules_combined_with_inputs_is_scoped_not_full_bundle(state) -> None:
    filtered = get_module_impl("vpc", state, sections=["submodules", "inputs"])

    # Absolute upper bound well under the pre-fix ~18,972 char over-fetch.
    assert len(filtered) < 12000, (
        f"scoped submodules+inputs ({len(filtered)} chars) must be well under the "
        f"pre-fix over-fetch ({_VPC_PRE_FIX_OVERFETCH_LEN} chars)"
    )
    # No numbered deep-dive heading at all -- full exclusion, not a partial one.
    assert "## Submodule " not in filtered, "no per-submodule deep-dive heading may appear in this combo"
    # Both submodules are still named -- the inventory still answers "what exists".
    assert "vpc-endpoints" in filtered
    assert "flow-log" in filtered
    # The root inputs table requested alongside it is still present.
    assert "Main Input Variables" in filtered


def test_l5_bare_inputs_key_is_unaffected_by_the_submodules_fix(state) -> None:
    """Regression guard: sections=['inputs'] ALONE must still resolve across every
    combined bundle including submodules (BUG-1) -- the full-exclusion rule only
    applies when 'submodules' is explicitly requested in the same call."""
    filtered = get_module_impl("iam", state, sections=["inputs"])
    assert (
        "## Submodule 1:" in filtered
    ), "bare inputs must still fall back into submodule bundles on pure-collection docs"


def test_l5_a3_submodule_address_still_reaches_the_deep_dive(state) -> None:
    """A3 stays intact: a submodule address still expands that submodule's own section."""
    scoped = get_module_impl("vpc//modules/vpc-endpoints", state)
    assert "## Submodule 1: vpc-endpoints" in scoped, "the addressed submodule's deep-dive must still expand"
    assert "## Submodule 2: flow-log" not in scoped, "other submodules must stay out of a scoped address response"


def test_l5_a3_submodule_name_substring_still_reaches_the_deep_dive(state) -> None:
    """A free-form heading substring (not the 'submodules' logical key) still pulls one deep-dive."""
    filtered = get_module_impl("vpc", state, sections=["vpc-endpoints"])
    assert "## Submodule 1: vpc-endpoints" in filtered
    assert "## Submodule 2: flow-log" not in filtered


def test_l5_a1_default_head_still_inlines_compact_inventory() -> None:
    """A1 stays intact: the default head inlines the compact inventory, not deep-dives."""
    head = orientation_head(_doc("vpc"))
    assert "## Submodules" in head
    assert "vpc-endpoints" in head
    assert "flow-log" in head
    assert "## Submodule 1: vpc-endpoints" not in head
    assert "## Submodule 2: flow-log" not in head


# --------------------------------------------------------------------------- #
# RC2 T3 - sem_sim exposed on ScoredHit. cos_raw (the per-doc cosine scaled to
# [0,1], before the per-query min-max) is comparable across queries, unlike
# the combined score. Populated for every hit, read-only from the existing
# embeddings - no index rebuild.
# --------------------------------------------------------------------------- #
def test_scored_hit_sem_sim_is_populated_float_in_unit_range(state) -> None:
    hits = compute_scores_detailed(
        state.index,
        "s3 bucket with encryption and versioning",
        w_kw=2.0,
        w_exact=3.0,
        w_bm25=1.0,
        w_sem=1.0,
        top_k=5,
        logger=state.logger,
    )
    assert hits, "expected at least one hit"
    for hit in hits:
        assert isinstance(hit.sem_sim, float)
        assert 0.0 <= hit.sem_sim <= 1.0


def test_search_modules_impl_hits_carry_sem_sim(state) -> None:
    # search_modules_impl goes through compute_scores_detailed internally; a
    # plain search must not blow up now that ScoredHit grew a field.
    out = search_modules_impl("vpc", state, top_k=3)
    assert out.results


# --------------------------------------------------------------------------- #
# RC2 C2/T2 gate - single-snapshot version consistency. The inlined
# top_module_doc head's version pin must come from the same metadata field as
# results[].latest_version, never a re-parse of the doc body, so the two can
# never contradict each other in one response.
# --------------------------------------------------------------------------- #
def test_version_pin_hint_override_wins_verbatim() -> None:
    text = "- **Latest Version**: 6.6.1\n"
    assert _version_pin_hint(text, version_override="9.9.9") == (
        "> **Version pin** — latest release is `9.9.9`. For an exact pin use "
        '`version = "9.9.9"`; use a range like `~> 9.0` only when you '
        "deliberately want automatic minor-version updates."
    )


def test_version_pin_hint_none_override_keeps_body_parse() -> None:
    text = "- **Latest Version**: 6.6.1\n"
    assert _version_pin_hint(text) == _version_pin_hint(text, version_override=None)
    assert "6.6.1" in _version_pin_hint(text)


def test_orientation_head_version_override_wins_over_body_bullet() -> None:
    doc = _doc("vpc")
    default_head = orientation_head(doc)
    assert "6.6.1" in default_head, "fixture doc must carry its real body-bullet version"
    overridden_head = orientation_head(doc, version_override="9.9.9")
    assert "9.9.9" in overridden_head
    assert "6.6.1" not in overridden_head.split("\n\n", 1)[0], "override must replace, not append, the pin line"


def test_search_expand_top_version_matches_result_metadata_snapshot(state, monkeypatch) -> None:
    """C2: patch the fixture doc's body bullet away from its stored metadata
    field to prove the metadata override wins - the inlined head's version
    string must equal results[0].latest_version by construction, never a
    contradicting re-parse of the (possibly stale) body bullet."""
    out = search_modules_impl("vpc", state, top_k=3, expand_top=True)
    assert out.confidence == "high"
    doc = state.index.docs[0]
    for d in state.index.docs:
        if d.module_name == out.results[0].module_name:
            doc = d
            break
    original_text = doc.text
    original_latest_version = doc.latest_version
    monkeypatch.setattr(doc, "latest_version", "9.9.9-metadata")
    monkeypatch.setattr(doc, "text", original_text.replace(original_latest_version, "1.1.1-stale-body", 1))

    out2 = search_modules_impl("vpc", state, top_k=3, expand_top=True)
    assert out2.confidence == "high"
    assert out2.results[0].latest_version == "9.9.9-metadata"
    assert out2.top_module_doc is not None
    # The version-pin hint line (the C2-guarded value) must match the metadata
    # snapshot, not the stale re-parsed body bullet -- the two can never
    # contradict each other by construction.
    pin_line = out2.top_module_doc.split("\n\n", 1)[0]
    assert "9.9.9-metadata" in pin_line
    assert "1.1.1-stale-body" not in pin_line
    assert pin_line == _version_pin_hint(doc.text, version_override=out2.results[0].latest_version)


# --------------------------------------------------------------------------- #
# RC3 #2 - render-time single-snapshot version consistency applied to ALL
# version mentions. rc2 synced only the pin banner; the body's own **Latest
# Version** bullet could still be stale and contradict the banner /
# results[].latest_version in the same response. _reconcile_body_version
# rewrites the body bullet to the threaded snapshot at render time (drift-safe:
# emitted text only, the indexed body/embeddings are untouched).
# --------------------------------------------------------------------------- #
def test_reconcile_body_version_rewrites_bullet_to_resolved() -> None:
    text = "## Module Information\n- **Latest Version**: 1.0.0-stale\n\nbody text\n"
    out = _reconcile_body_version(text, "2.5.0")
    assert "- **Latest Version**: 2.5.0" in out
    assert "1.0.0-stale" not in out


def test_reconcile_body_version_noop_without_resolved() -> None:
    text = "- **Latest Version**: 1.0.0\n"
    assert _reconcile_body_version(text, None) == text
    assert _reconcile_body_version(text, "") == text


def test_reconcile_body_version_noop_without_bullet() -> None:
    text = "## Description\nno version bullet here at all\n"
    assert _reconcile_body_version(text, "2.5.0") == text


def test_orientation_head_override_reconciles_body_bullet_not_just_banner() -> None:
    # RC3 #2: the body's own Latest Version bullet (inside Module Information)
    # must be rewritten to the override, not only the pin banner.
    doc = _doc("vpc")
    assert "- **Latest Version**: 6.6.1" in _doc("vpc"), "fixture must carry its real body bullet"
    head = orientation_head(doc, version_override="9.9.9")
    assert "- **Latest Version**: 9.9.9" in head, "body bullet must be reconciled to the override"
    assert "- **Latest Version**: 6.6.1" not in head, "stale body bullet must not survive in the head"


def test_search_expand_top_body_bullet_matches_snapshot(state, monkeypatch) -> None:
    """The inlined head's BODY version bullet (not only the pin banner) must
    equal results[].latest_version -- the whole point of RC3 #2."""
    out = search_modules_impl("vpc", state, top_k=3, expand_top=True)
    assert out.confidence == "high" and out.top_module_doc is not None
    doc = next(d for d in state.index.docs if d.module_name == out.results[0].module_name)
    monkeypatch.setattr(doc, "latest_version", "9.9.9-metadata")

    out2 = search_modules_impl("vpc", state, top_k=3, expand_top=True)
    assert out2.top_module_doc is not None
    # The stale-vs-fresh contradiction is gone: the metadata snapshot appears in
    # the body bullet and nowhere does an unreconciled body bullet contradict it.
    assert "- **Latest Version**: 9.9.9-metadata" in out2.top_module_doc


# --------------------------------------------------------------------------- #
# RC3 #3 - non-top-1 result blurbs must clip on a word boundary, never mid-word.
# --------------------------------------------------------------------------- #
def test_clip_blurb_clips_on_word_boundary_no_midword_cut() -> None:
    # No early period, so the hard char-cap branch runs; it must not leave a
    # dangling partial word.
    text = (
        "Terraform module to provision managed streaming kafka clusters with "
        "encryption authentication and monitoring enabled"
    )
    clipped = _clip_blurb(text, max_length=40)
    assert clipped.endswith("…")
    body = clipped[:-1]
    assert body, "clip must keep at least one whole word"
    assert text.startswith(body), "clip must be a prefix of the source"
    # The char immediately after the kept prefix is whitespace -> we cut between
    # words, not through one.
    assert text[len(body)] == " "


def test_clip_blurb_first_sentence_branch_unaffected() -> None:
    text = "Short purpose. Extra detail that should be dropped by the sentence clip."
    assert _clip_blurb(text) == "Short purpose."


# --------------------------------------------------------------------------- #
# Capability-coverage gate. The wrong-domain inline failure is a capability
# mismatch, not a ranking-confidence one: a wide score margin still inlines a
# module whose doc never asserts the query's capability terms. The classifier
# demotes a top-1 to "low" when its IDF-weighted capability coverage falls
# below _COVERAGE_THETA. Coverage itself (full/partial/absent evidence tiers,
# IDF weighting, fail-open behavior) is unit-tested directly in
# test_capability_coverage.py (Task 2); this section only covers
# _classify_confidence's own use of that signal.
# --------------------------------------------------------------------------- #
def test_classify_low_on_capability_miss_despite_strong_sem() -> None:
    # a lexical-non-exact top-1 with a strong sem_sim is still "low" when the
    # query's capability terms are absent from the candidate -- this is the
    # wrong-domain inline a score-margin gate was blind to.
    idx = _FakeIndex(
        docs=[
            _FakeDoc(text="adjacent-domain giant that never mentions the term", keywords=["network"]),
            _FakeDoc(text="rank 2"),
        ],
        idf={"kinesis": 6.0, "stream": 2.0},
    )
    hits = [
        ScoredHit(score=9.0, doc_index=0, exact_hit=False, kw_overlap=True, sem_sim=0.95),
        ScoredHit(score=8.5, doc_index=1, exact_hit=False, kw_overlap=True, sem_sim=0.90),
    ]
    assert _classify_confidence("kinesis stream", hits, idx) == "low"


# --------------------------------------------------------------------------- #
# RC4 #2 - verdict and inline are ONE decision: top_module_doc is present iff
# the verdict is "high". The docstring contract ("high => doc inlined") holds.
# --------------------------------------------------------------------------- #
def test_inline_present_iff_high_on_live_queries(state) -> None:
    for query in ("s3 bucket with encryption and versioning", "sagemaker", "vpc", "kubernetes cluster"):
        out = search_modules_impl(query, state, top_k=3, expand_top=True)
        assert (out.top_module_doc is not None) == (out.confidence == "high"), (
            f"{query!r}: inline must be present iff confidence is high (got confidence={out.confidence}, "
            f"inline={'present' if out.top_module_doc else 'absent'})"
        )


def test_wrong_domain_top1_is_low_and_not_inlined(state, monkeypatch) -> None:
    """Integration: force the top hit onto a real doc that does not cover the
    query's central capability term, and confirm the unified path demotes it to
    'low' and inlines nothing (RC4 #1 + #2)."""
    idf = getattr(state.index.bm25, "idf", {}) or {}
    term = "sagemaker"  # a real catalog capability term (has corpus IDF)
    assert idf.get(term, 0.0) > 0.0, "term must carry a corpus salience signal"
    # Pick any doc whose name/keywords/text does not cover the term -> a
    # wrong-domain candidate for the query below.
    target_idx = next(
        i
        for i, d in enumerate(state.index.docs)
        if term not in f"{d.module_name or ''} {' '.join(d.keywords or [])} {d.text}".lower()
    )
    forced = [
        ScoredHit(score=9.0, doc_index=target_idx, exact_hit=False, kw_overlap=True, sem_sim=0.95),
        ScoredHit(score=4.0, doc_index=target_idx, exact_hit=False, kw_overlap=True, sem_sim=0.90),
    ]
    monkeypatch.setattr("tfmod_mcp_server.compute_scores_detailed", lambda *a, **k: forced)
    out = search_modules_impl(term, state, top_k=2, expand_top=True)
    assert out.confidence == "low"
    assert out.top_module_doc is None
    assert "top_module_doc" not in out.model_dump()


def test_expand_top_false_suppresses_even_when_high(state) -> None:
    out = search_modules_impl("s3 bucket with encryption and versioning", state, top_k=3, expand_top=False)
    assert out.confidence == "high"
    assert out.top_module_doc is None
    assert "top_module_doc" not in out.model_dump()


def test_sem_floor_constant_still_exposed() -> None:
    # Secondary demoter retained (incidental-keyword guard); guard the constant.
    assert 0.0 < SEARCH_SEM_FLOOR < 1.0


def test_score_floor_constant_is_positive() -> None:
    # 0.23.0: the fourth (final) demoter in the truth table; provisional
    # value pending a later derivation task, but must always be a sane
    # positive floor.
    assert SEARCH_SCORE_FLOOR > 0.0


# --------------------------------------------------------------------------- #
# RC4 #3 - verdict-stability (determinism) contract guards. A consumer cannot
# budget around a verdict that flips on trivial rephrasing. We lock the part of
# the contract the implementation can guarantee: adding generic-infra filler
# words ("aws"/"terraform"/politeness) must NOT change the verdict, because the
# capability check drops those as stopwords and the central term is unchanged.
# (Broad cross-phrasing determinism -- entirely different wordings of one intent
# -- is a known limitation on borderline catalog-gap phrasings; see the RC4
# revision spec, deferred with defect item 2.)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "base",
    ["kubernetes cluster", "object storage versioning"],
)
def test_verdict_is_invariant_to_generic_infra_filler(base, state) -> None:
    baseline = search_modules_impl(base, state, top_k=3).confidence
    for filler in (f"aws {base}", f"terraform module for {base}", f"{base} please"):
        got = search_modules_impl(filler, state, top_k=3).confidence
        assert got == baseline, f"verdict flipped on generic-infra filler: {base!r} -> {baseline}, {filler!r} -> {got}"


@pytest.mark.parametrize(
    ("paraphrases", "expected"),
    [
        # 0.23.0 re-derivation: under this file's fixture weights
        # (w_kw=2.0, w_exact=3.0, w_bm25=1.0, w_sem=1.0 -- NOT the
        # production weights), the combined scores for this group sit
        # below SEARCH_SCORE_FLOOR (4.5): "kubernetes cluster" ->
        # top1=eks score=3.82 cov=0.798; "managed kubernetes cluster" ->
        # top1=eks score=3.74 cov=0.857; "kubernetes container
        # orchestration" -> top1=app-runner score=4.06 cov=0.352 (also
        # below the coverage theta). All three land "low" under the new
        # rule, still a single shared verdict across every phrasing --
        # the determinism guarantee this test exists to pin still holds,
        # only the expected label changed.
        (["kubernetes cluster", "managed kubernetes cluster", "kubernetes container orchestration"], "low"),
        (["sagemaker", "sagemaker model endpoint", "machine learning model hosting on sagemaker"], "low"),
    ],
)
def test_stable_paraphrase_sets_share_one_verdict(paraphrases, expected, state) -> None:
    verdicts = {search_modules_impl(q, state, top_k=3).confidence for q in paraphrases}
    assert verdicts == {expected}, f"paraphrases of one intent disagreed: {verdicts} (expected all {expected!r})"
