"""Integration tests for the evidence-based verdict rule.

Verdict = high iff (whole-query exact name) OR (coverage >= theta AND
sem >= sem-floor AND score >= score-floor). These tests pin the rule with
real-catalog exemplars chosen per mechanism class (signals recorded in
comments); they are NOT the private regression probe rows.

All measured signals below were captured with the production search weights
(w_kw=1.0, w_exact=3.0, w_bm25=2.0, w_sem=3.0), which is also what the `state`
fixture below configures, so the recorded numbers match what
search_modules_impl actually computes in these tests.
"""

import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.integration import PROJECT_ROOT
from tfmod_mcp_server import SearchWeights, ServerStateManager, search_modules_impl
from tfmod_search_lib import load_index


@pytest.fixture(scope="module")
def state():
    logger = logging.getLogger("test_verdict_rule")
    logger.addHandler(logging.NullHandler())
    index_path = PROJECT_ROOT / "model" / "tfmod_e5_small_index.pkl"
    if not index_path.exists():
        pytest.skip(f"Index file not found at {index_path}")
    index = load_index(str(index_path), logger)
    ServerStateManager.reset()
    st = ServerStateManager.initialize(
        index=index,
        weights=SearchWeights(w_kw=1.0, w_exact=3.0, w_bm25=2.0, w_sem=3.0),
        index_path=index_path,
        logger=logger,
    )
    yield st
    ServerStateManager.reset()


class TestWholeQueryExact:
    def test_bare_module_name_is_high(self, state):
        # "eks" normalizes to the module name itself -> rule step 1 fires
        # regardless of every other signal.
        # Measured: top1=eks score=7.15 exact=True sem=0.9203 cov=1.000.
        out = search_modules_impl("eks", state, top_k=3)
        assert out.results[0].module_name == "eks"
        assert out.confidence == "high"


class TestEvidenceBasedHigh:
    def test_capability_query_without_name_token_is_high(self, state):
        # No "elasticache" token anywhere in the query, so step 1 (whole-query
        # exact name) cannot fire -- the verdict must come purely from
        # coverage + sem + score.
        # Measured: top1=elasticache score=6.65 sem=0.9167 cov=0.898 (all
        # three floors clear: cov 0.898 >= 0.5, sem 0.9167 >= 0.88,
        # score 6.65 >= 4.5).
        out = search_modules_impl("redis cluster with automatic failover", state, top_k=3)
        assert out.results[0].module_name == "elasticache"
        assert out.confidence == "high"
        assert out.top_module_doc is not None


class TestEvidenceBasedLow:
    def test_wrong_domain_body_mention_is_low(self, state):
        # Top-1 is an adjacent-domain module: it asserts "monitoring" (a real
        # keyword) but the query's rarest, defining term "trail" (idf 2.03)
        # only ever appears in the doc body -- never in the module name,
        # keywords, or extracted description -- so it counts at
        # _COVERAGE_ALPHA (0.3), not in full; "audit"/"compliance" are
        # likewise body-only mentions.
        # Measured: top1=cloudwatch score=3.85 sem=0.9260 cov=0.403
        # (< theta 0.5) -> the coverage gate (rule step 2) fires before the
        # sem/score floors are even reached.
        # Discriminating: under the OLD classifier this same query/hit
        # resolved "high" (its single-central-token check only required
        # "trail" to appear ANYWHERE in name/keywords/full text, which it
        # does, in the body) -- a wrong-domain false-high the coverage
        # rewrite fixes.
        out = search_modules_impl("audit trail and compliance monitoring for cloud resources", state, top_k=3)
        assert out.results[0].module_name == "cloudwatch"
        assert out.confidence == "low"
        assert out.hint is not None
        assert out.top_module_doc is None


class TestParaphraseDeterminism:
    def test_intent_pair_shares_verdict(self, state):
        # Two phrasings of one intent (rotating Secrets Manager credentials);
        # both resolve top1=secrets-manager.
        #   "secrets manager for rotating database credentials":
        #     score=9.31 sem=0.9398 cov=0.496
        #   "centralized vault for rotating sensitive application credentials":
        #     score=3.15 sem=0.9152 cov=0.205
        # Both land "low" (coverage below theta on both phrasings) -- the
        # point of this test is NOT that "low" is the ideal verdict here
        # (see the extract_description note below) but that the two
        # phrasings AGREE, unlike the old classifier: phrasing one had
        # exact_hit=True (the ranker boundary-matched the module name
        # inside the longer query) and kw_overlap=False, while phrasing two
        # had both False -- the old "high" came from the exact-hit branch,
        # flipping "high" vs "low" for the identical top-1 module. This
        # rewrite removes that path: a name token inside a longer query no
        # longer short-circuits the verdict.
        #
        # Root-cause note (extract_description landmine, confirmed by
        # measurement): coverage undercounts here because the query's
        # highest-idf token "rotating" (idf 3.59) never matches the doc's
        # own keyword "secret-rotation" (gerund vs noun form is outside the
        # trailing-plural/prefix tolerance in _token_matches_parts) and the
        # real "## Description" prose -- which does contain the word
        # "rotating" verbatim -- is never reached by extract_description
        # (it fills its 200-char budget from the preceding "## Module
        # Information" bullet block on every doc in this catalog, confirmed
        # across all 55 docs). Fixing either gap is out of this task's scope
        # (Task 3 consumes _capability_coverage as shipped by Task 2) but
        # would very likely flip this pair to "high".
        a = search_modules_impl("secrets manager for rotating database credentials", state, top_k=3)
        b = search_modules_impl("centralized vault for rotating sensitive application credentials", state, top_k=3)
        assert a.results[0].module_name == b.results[0].module_name == "secrets-manager"
        assert a.confidence == b.confidence
