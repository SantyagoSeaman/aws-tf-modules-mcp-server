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

    def test_prefix_rule_needs_length_four(self):
        # long-token prefix tolerance
        assert _token_matches_parts("authoriz", {"authorizer"}) is True
        # short parts never prefix-match ("db" must not absorb "database")
        assert _token_matches_parts("database", {"db"}) is False

    def test_no_mid_word_substring(self):
        # "ui" inside "guide" must not match
        assert _token_matches_parts("ui", {"guide"}) is False


class TestCapabilityCoverage:
    def test_strong_keyword_coverage_is_full(self):
        doc = make_doc("gateway", ["jwt-authorizer", "http-api"], "body text")
        idx = make_index([doc], {"jwt": 3.0, "authorizer": 3.0})
        assert _capability_coverage("jwt authorizer", idx, 0) == pytest.approx(1.0)

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

    def test_fail_open_on_empty_and_stopword_queries(self):
        doc = make_doc("anything", ["kw"], "body")
        idx = make_index([doc], {})
        assert _capability_coverage("", idx, 0) == pytest.approx(1.0)
        assert _capability_coverage("aws terraform module", idx, 0) == pytest.approx(1.0)

    def test_zero_idf_tokens_are_excluded(self):
        doc = make_doc("mod", ["alpha"], "body")
        idx = make_index([doc], {"alpha": 2.0})  # "novelterm" has no idf entry
        assert _capability_coverage("alpha novelterm", idx, 0) == pytest.approx(1.0)
