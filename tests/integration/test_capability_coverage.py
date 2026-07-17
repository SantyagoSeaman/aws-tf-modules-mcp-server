"""Unit tests for the IDF-weighted capability coverage score.

Coverage measures how much of the query's IDF mass the candidate doc
asserts in capability fields. Strong evidence (1.0): module name, keywords,
extracted description. Weak evidence (0.3): body-only mention. The tests
run against synthetic docs and a fake BM25 idf table - no real index, no
embedding model.
"""

from types import SimpleNamespace

import pytest

from tfmod_mcp_server import (
    _COVERAGE_ALPHA,
    _COVERAGE_THETA,
    _capability_coverage,
    _field_parts,
    _token_matches_parts,
)
from tfmod_search_lib import DocRecord, extract_description


def make_index(docs, idf):
    return SimpleNamespace(docs=docs, bm25=SimpleNamespace(idf=idf))


def make_doc(name, keywords, text):
    return DocRecord(path=f"modules/x/{name}.md", module_name=name, keywords=keywords, text=text)


class TestFieldParts:
    def test_hyphenated_keyword_splits_into_parts(self):
        assert {"jwt", "authorizer"} <= _field_parts("jwt-authorizer")

    def test_multiple_fields_merge(self):
        parts = _field_parts("memory-db", "redis", "in-memory")
        assert {"memory", "db", "redis", "in"} <= parts


class TestTokenMatchesParts:
    def test_equality(self):
        assert _token_matches_parts("redis", {"redis"}) is True

    def test_trailing_plural(self):
        assert _token_matches_parts("buckets", {"bucket"}) is True
        assert _token_matches_parts("bucket", {"buckets"}) is True

    def test_short_stopword_like_token_plural_strip_does_not_fire(self):
        # The plural-strip equality only fires when the stripped token has
        # length >= 3, so "as" (stem "a") and "its" (stem "it") can never be
        # conflated with a shorter word via the plural rule.
        assert _token_matches_parts("as", {"a"}) is False
        assert _token_matches_parts("its", {"it"}) is False

    def test_prefix_rule_needs_length_five(self):
        # long-token prefix tolerance (>= 5 chars both sides)
        assert _token_matches_parts("authoriz", {"authorizer"}) is True
        # short parts never prefix-match ("db" must not absorb "database")
        assert _token_matches_parts("database", {"db"}) is False

    def test_prefix_rule_four_char_artifacts_no_longer_match(self):
        # Regression tests: the old 4-char boundary let these unrelated pairs
        # absorb each other; the 5-char boundary kills all of them.
        assert _token_matches_parts("database", {"data"}) is False
        assert _token_matches_parts("base", {"based"}) is False
        assert _token_matches_parts("automatic", {"auto"}) is False
        assert _token_matches_parts("without", {"with"}) is False

    def test_no_mid_word_substring(self):
        # "ui" inside "guide" must not match
        assert _token_matches_parts("ui", {"guide"}) is False

    def test_hyphenated_compound_query_token_matches_when_every_run_matches(self):
        # Symmetry fix: _field_parts already splits FIELD strings into alnum
        # runs; a hyphenated compound written as a single tokenizer TOKEN
        # (tokenize() does not split on hyphens) must get the same treatment
        # on the query side, or it can never strong-match split field parts.
        # Every run must match -- this is what the old, accidental 4-char
        # prefix rule was silently providing for exactly one run at a time.
        assert _token_matches_parts("auto-scaling-group", {"auto", "scaling", "group"}) is True
        assert _token_matches_parts("data-warehouse", {"data", "warehouse"}) is True
        assert _token_matches_parts("web-application-firewall", {"web", "application", "firewall"}) is True

    def test_hyphenated_compound_query_token_partial_match_is_rejected(self):
        # A partial compound match is not evidence of coverage -- ALL runs
        # must match, not a majority.
        assert _token_matches_parts("data-warehouse", {"data", "lake"}) is False

    def test_plain_non_compound_token_unaffected_by_compound_rule(self):
        # A token with no punctuation never enters the compound-decomposition
        # branch at all; unmatched plain tokens behave exactly as before.
        assert _token_matches_parts("bedrock", {"unrelated", "parts", "only"}) is False


class TestCapabilityCoverage:
    def test_strong_keyword_coverage_is_full(self):
        doc = make_doc("gateway", ["webhook-dispatcher", "http-api"], "body text")
        idx = make_index([doc], {"webhook": 3.0, "dispatcher": 3.0})
        assert _capability_coverage("webhook dispatcher", idx, 0) == pytest.approx(1.0)

    def test_body_only_mention_is_weak(self):
        # extract_description (default max_length=200) does not stop at the
        # first paragraph break - it keeps accumulating non-header lines
        # until the running length hits the cap. The lead paragraph here is
        # padded past 200 chars on its own so the description cuts off
        # before the "Integrations" section, keeping "authpool" out of the
        # extracted description and therefore out of strong evidence -
        # otherwise it would count as strong, not a body-only mention.
        lead = (
            "Managed search and indexing engine for large scale full text and "
            "vector search workloads, with configurable replication, automated "
            "backups, and multi region deployment options for production grade "
            "use cases."
        )
        assert len(lead) > 200
        text = f"# Search Service\n\n{lead}\n\n## Integrations\nWorks with authpool for sign in."
        doc = make_doc("searchdb", ["search", "index"], text)
        idx = make_index([doc], {"authpool": 3.0})
        assert "authpool" not in extract_description(doc.text)
        assert _capability_coverage("authpool", idx, 0) == pytest.approx(_COVERAGE_ALPHA)

    def test_absent_term_scores_zero(self):
        doc = make_doc("registry", ["containers"], "container registry body")
        idx = make_index([doc], {"vault": 3.0})
        assert _capability_coverage("vault", idx, 0) == pytest.approx(0.0)

    def test_idf_weighting_dominates(self):
        # rare absent term (idf 4.0) outweighs common matched term (idf 1.0)
        doc = make_doc("db", ["database"], "database body")
        idx = make_index([doc], {"database": 1.0, "sharding": 4.0})
        cov = _capability_coverage("database sharding", idx, 0)
        assert cov == pytest.approx(1.0 * 1.0 / (1.0 + 4.0))
        assert cov < _COVERAGE_THETA

    def test_dense_keyword_mass_survives_one_absent_property_word(self):
        # the false-low class: many strong keyword hits + one absent
        # property adjective must stay above theta
        doc = make_doc("memdb", ["redis", "in-memory", "database", "multi-az"], "body")
        idx = make_index(
            [doc],
            {"redis": 2.5, "memory": 2.0, "database": 1.5, "az": 2.0, "durability": 3.0},
        )
        cov = _capability_coverage("redis memory database az durability", idx, 0)
        assert cov > _COVERAGE_THETA

    def test_description_counts_as_strong(self):
        text = "# Title\n\nCreates managed relational database clusters.\n\n## More\nbody"
        doc = make_doc("engine", ["engine"], text)
        idx = make_index([doc], {"relational": 3.0})
        assert _capability_coverage("relational", idx, 0) == pytest.approx(1.0)

    def test_fail_closed_on_contentless_query(self):
        # Out-of-catalog honesty (F1 fix): an empty query, or a query whose
        # every token is filtered as stopword/catalog-filler, carries no
        # evidence to trust. It must NOT fail open to a blanket "covers
        # everything" verdict -- the old fail-open behavior let a contentless
        # query ("?", "please help", "aws terraform module") reach
        # verdict=high and inline a wrong doc. The corpus idf table here is
        # non-empty so the degraded-index guard (tested separately below)
        # does not mask this path.
        doc = make_doc("anything", ["kw"], "body")
        idx = make_index([doc], {"something": 2.0})
        assert _capability_coverage("", idx, 0) == pytest.approx(0.0)
        assert _capability_coverage("aws terraform module", idx, 0) == pytest.approx(0.0)

    def test_degraded_index_empty_idf_fails_open(self):
        # A genuinely empty/absent corpus idf table means the index itself
        # cannot judge coverage -- this is the one remaining fail-open case,
        # distinct from a contentless query.
        doc = make_doc("anything", ["kw"], "body")
        idx = make_index([doc], {})
        assert _capability_coverage("some real capability terms here", idx, 0) == pytest.approx(1.0)

    def test_zero_idf_token_participates_at_mean_idf_weight_when_matched(self):
        # "novelterm" has no idf entry (out-of-corpus) but IS present in this
        # doc's own keywords -- it must count as strong evidence at the
        # corpus's MEAN idf weight (C1 calibration, 2026-07-17: an unknown
        # word's principled prior is "typical rarity", not "as rare as the
        # single rarest word anywhere in the corpus" -- the prior max-based
        # weight measurably overweighed informal/slang/typo tokens on real
        # queries, e.g. "pls create s3 bucket"), not be silently dropped.
        doc = make_doc("mod", ["alpha", "novelterm"], "body")
        idx = make_index([doc], {"alpha": 2.0, "beta": 6.0})  # mean idf = 4.0 (max would be 6.0)
        cov = _capability_coverage("alpha novelterm", idx, 0)
        assert cov == pytest.approx(1.0)  # both match strong regardless of the exact fallback weight

    def test_out_of_vocab_token_weighted_at_mean_not_max(self):
        # C1: pins the exact fallback weight as mean(idf.values()), not max.
        doc = make_doc("mod", ["alpha"], "body")
        idx = make_index([doc], {"alpha": 1.0, "beta": 2.0, "gamma": 6.0})  # mean = 3.0, max = 6.0
        cov = _capability_coverage("alpha bedrock", idx, 0)  # "bedrock" absent from idf and from the doc
        # alpha (matched, strong) weight=1.0; bedrock (unmatched) weight=mean=3.0 (would be 6.0 under the old max rule)
        assert cov == pytest.approx(1.0 / (1.0 + 3.0))

    def test_out_of_vocab_token_collapses_coverage_below_theta_when_unmatched(self):
        # An out-of-catalog term (e.g. "bedrock", "snowflake") still
        # participates at a real, non-zero fallback weight rather than being
        # dropped -- when it matches nothing, it can still drag coverage
        # below theta even though the query's other term matches in full,
        # just less aggressively than the pre-C1 max-weighted version.
        doc = make_doc("mod", ["alpha"], "body")
        idx = make_index([doc], {"alpha": 1.0, "some-other-high-idf-term": 5.0})
        cov = _capability_coverage("alpha bedrock", idx, 0)  # "bedrock" absent from idf and from the doc
        assert cov < _COVERAGE_THETA

    def test_weak_tier_requires_word_boundary_not_substring(self):
        # "ui" must not earn weak (body-mention) credit from being a
        # substring of "guide" -- the weak-tier match is now a word-boundary
        # regex, not `t in body`.
        doc = make_doc("docsvc", ["docs"], "This is a helpful guide for developers.")
        idx = make_index([doc], {"ui": 3.0})
        assert _capability_coverage("ui", idx, 0) == pytest.approx(0.0)

    def test_connector_words_do_not_change_coverage(self):
        # A synthetic-doc equivalent of the "audit trail and compliance
        # monitoring for cloud resources" class: general English connector
        # words ("and", "for") and catalog filler ("cloud") must not change
        # coverage relative to the connector-free phrasing -- both resolve to
        # the same content-token set now that _ENGLISH_STOPWORDS is filtered
        # alongside _CAPABILITY_STOPWORDS.
        doc = make_doc("logstore", ["monitoring"], "General purpose object storage with lifecycle rules.")
        idx = make_index([doc], {"trail": 3.0, "compliance": 2.5, "audit": 2.0})
        with_connectors = _capability_coverage("audit trail and compliance monitoring for cloud resources", idx, 0)
        without_connectors = _capability_coverage("audit trail compliance monitoring", idx, 0)
        assert with_connectors == pytest.approx(without_connectors)
