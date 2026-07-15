"""Regression guards for the v0.21.0 reproduction pack.

Source: `tfmodsearch-improvements-2.md` "Reproduction pack (v0.21.0)" — five
"the tool ran fine but the result was unsatisfactory" cases extracted from the
condition-A agent transcripts. The report measured them against a stale **0.19.1**
daemon (its numbers are all "byte-identical to v0.19"); re-measured against the
real shipped 0.21.0 (source + PyPI wheel + GHCR image), four of the five are
already fixed and one (Repro 5) is genuinely open.

These tests pin that ground truth so a future edit cannot silently regress the
four fixed behaviors, and mark the open one (xfail) so it flips to a passing
guard the moment the confidence signal lands.

Offline: operates on the curated docs and the local index only (no live server).
Repros 1-4 exercise the exact `get_module` code path (`filter_module_sections` /
`orientation_head`); Repro 5 exercises `search_modules_impl`.
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
    orientation_head,
    search_modules_impl,
)
from tfmod_search_lib import load_index

DOCS = PROJECT_ROOT / "modules" / "terraform-aws-modules"


def _doc(module: str) -> str:
    return (DOCS / f"{module}.md").read_text()


# --------------------------------------------------------------------------- #
# Repro 1 — redshift R8: the leaf bool type must be reachable from `inputs`.
# The failing agents wrote `target_action = { pause_cluster = { ... } }` (an
# object) because sections=['inputs'] never stated pause_cluster is a bare bool.
# --------------------------------------------------------------------------- #
def test_repro1_redshift_inputs_states_leaf_bool_type() -> None:
    payload = filter_module_sections(_doc("redshift"), ["inputs"])
    assert "pause_cluster = true" in payload, (
        "redshift sections=['inputs'] must show the terminal bool shape "
        "(pause_cluster = true), not just the nesting path — else the agent "
        "wraps the bool in an object and terraform apply fails"
    )


# --------------------------------------------------------------------------- #
# Repro 2 — wafv2 R22: `override_action` must be reachable from `inputs`.
# The failing agents wrote `action = "count"` on a managed_rule_group_statement
# because the doc was silent on override_action.
# --------------------------------------------------------------------------- #
def test_repro2_wafv2_inputs_mentions_override_action() -> None:
    payload = filter_module_sections(_doc("wafv2"), ["inputs"])
    assert "override_action" in payload, (
        "wafv2 sections=['inputs'] must name override_action (managed-rule-group / "
        "rule-group-reference statements take it; standalone match statements take "
        "action; mutually exclusive) — else the agent picks the wrong key"
    )


# --------------------------------------------------------------------------- #
# Repro 3 — sections=['inputs'] must be SCOPED, not the whole combined bundle.
# On 0.19.x these were byte-identical to sections=['inputs','examples']; the fix
# (0.20.0 _extract_interface_h3) recurses into the named sub-block.
# --------------------------------------------------------------------------- #
REPRO3_COMBINED_HEADING_MODULES = [
    "s3-bucket",
    "vpc",
    "opensearch",
    "apigateway-v2",
    "elasticache",
]


@pytest.mark.parametrize("module", REPRO3_COMBINED_HEADING_MODULES)
def test_repro3_inputs_is_scoped_not_whole_bundle(module: str) -> None:
    text = _doc(module)
    inputs_only = filter_module_sections(text, ["inputs"])
    inputs_examples = filter_module_sections(text, ["inputs", "examples"])
    assert inputs_only != inputs_examples, (
        f"{module}: sections=['inputs'] is byte-identical to "
        f"sections=['inputs','examples'] — the inputs filter is a no-op "
        f"(the 0.19.x over-fetch bug)"
    )
    assert len(inputs_only) < len(inputs_examples), (
        f"{module}: sections=['inputs'] ({len(inputs_only)} chars) must be smaller "
        f"than sections=['inputs','examples'] ({len(inputs_examples)} chars)"
    )


# --------------------------------------------------------------------------- #
# Repro 4 — the default (bare) head must carry a real compact inputs table, so
# the agent is not forced into an immediate sections=['inputs'] double-fetch.
# --------------------------------------------------------------------------- #
REPRO4_MODULES = [
    "s3-bucket",
    "vpc",
    "acm",
    "kms",
    "batch",
    "step-functions",
    "rds-proxy",
]


@pytest.mark.parametrize("module", REPRO4_MODULES)
def test_repro4_bare_head_carries_inputs_table(module: str) -> None:
    head = orientation_head(_doc(module))
    assert "Main Input Variables" in head, (
        f"{module}: default head must inline the Main Input Variables section "
        f"(kills the bare->sections=['inputs'] double-fetch)"
    )
    assert "| `" in head, (
        f"{module}: default head must contain an actual variable table row "
        f"(name/type/default), not just the heading"
    )


# --------------------------------------------------------------------------- #
# Repro 5 — search_modules gives no "no confident match" signal (OPEN).
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def _repro_state():
    logger = logging.getLogger("test_repro_pack")
    logger.addHandler(logging.NullHandler())
    index_path = PROJECT_ROOT / "model" / "tfmod_e5_small_index.pkl"
    if not index_path.exists():
        pytest.skip(f"Index file not found at {index_path}")
    index = load_index(str(index_path), logger)
    ServerStateManager.reset()
    state = ServerStateManager.initialize(
        index=index,
        weights=SearchWeights(w_kw=2.0, w_exact=3.0, w_bm25=1.0, w_sem=1.0),
        index_path=index_path,
        logger=logger,
    )
    yield state
    ServerStateManager.reset()


def test_repro5_score_band_separates_real_from_absent_capability(_repro_state) -> None:
    """The score evidence the future confidence signal (lever 3) will key on.

    A real capability query sits in the high band; a capability genuinely absent
    from the catalog AND not sharing an exact module-name token sits well below.
    NOTE the deliberate gap this guard documents: "vpc peering ..." is absent yet
    scores in the HIGH band because the query shares the exact-name token "vpc"
    with the real vpc module — so a naive top-score threshold does NOT separate
    it. Any lever-3 confidence design must handle the shared-token near-miss, not
    just the clean cognito case.
    """
    real = search_modules_impl("s3 bucket with encryption", _repro_state, top_k=3)
    absent = search_modules_impl("cognito", _repro_state, top_k=3)
    assert real.results[0].score > 5.5, f"real hit unexpectedly low: {real.results[0].score}"
    assert (
        absent.results[0].score < 5.0
    ), f"absent-capability query 'cognito' unexpectedly high: {absent.results[0].score}"


@pytest.mark.xfail(
    strict=True,
    reason="Repro 5 / lever 3 OPEN: search_modules has no confidence/no-match "
    "signal yet. Remove this marker when the confidence field lands.",
)
def test_repro5_search_exposes_confidence_signal(_repro_state) -> None:
    """Desired API: a low-confidence query surfaces a machine-readable signal so
    the agent need not dump modules_list to prove a capability is absent."""
    result = search_modules_impl("cognito", _repro_state, top_k=3)
    assert hasattr(result, "confidence"), "SearchOutput should carry a confidence signal"
    assert result.confidence in {"low", "none"}
