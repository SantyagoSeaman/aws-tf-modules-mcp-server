"""Exact-name matching is hyphen-boundary aware, not raw substring.

The ranker awards the w_exact component when a module name appears in the
normalized query. A raw substring check fires spuriously when a short
module name occurs inside an unrelated word (the name lands mid-word after
normalization joins the phrase with hyphens). The helper requires the name
to sit on hyphen boundaries.
"""

from tfmod_search_lib import exact_name_match, normalize_modname


class TestExactNameMatch:
    def test_whole_query_is_the_name(self):
        assert exact_name_match("vpc", normalize_modname("vpc")) is True

    def test_name_as_word_inside_phrase(self):
        # "vpc" on hyphen boundaries inside a longer normalized phrase
        assert exact_name_match("vpc", normalize_modname("vpc with private subnets")) is True

    def test_multiword_name_inside_phrase(self):
        assert exact_name_match("s3-bucket", normalize_modname("s3 bucket with kms encryption")) is True

    def test_name_inside_unrelated_word_is_rejected(self):
        # "rds" occurs inside "records"; must NOT match
        assert exact_name_match("rds", normalize_modname("manage dns records zones")) is False

    def test_short_name_inside_word_is_rejected(self):
        # "eks" occurs inside "weeks"; must NOT match
        assert exact_name_match("eks", normalize_modname("deploy this in two weeks")) is False

    def test_name_at_word_start_inside_word_is_rejected(self):
        # "alb" occurs inside "albums"; must NOT match
        assert exact_name_match("alb", normalize_modname("music albums storage")) is False

    def test_hyphenated_name_on_boundary(self):
        assert exact_name_match("memory-db", normalize_modname("memory db cluster setup")) is True

    def test_empty_name_never_matches(self):
        assert exact_name_match("", normalize_modname("anything")) is False

    # -- Punctuation tolerance (B4): non-alphanumeric characters on either
    # side are mapped to hyphen boundaries before the containment check. --

    def test_query_with_trailing_comma_and_more_words_still_matches(self):
        assert exact_name_match("vpc", normalize_modname("vpc, private subnets")) is True

    def test_query_with_trailing_period_matches(self):
        assert exact_name_match("vpc", normalize_modname("vpc.")) is True

    def test_colon_after_module_name_in_query_matches(self):
        # "eks: karpenter autoscaling" -- the colon used to defeat the
        # hyphen-boundary test entirely, hiding the "eks" exact component.
        assert exact_name_match("eks", normalize_modname("eks: karpenter autoscaling")) is True

    def test_punctuated_module_name_side_also_tolerated(self):
        # Both-direction: punctuation normalization applies to module_name too.
        assert exact_name_match("vpc.", normalize_modname("vpc private subnets")) is True

    def test_name_inside_unrelated_word_still_rejected_with_punctuation_present(self):
        # "rds" inside "records" must stay rejected even when the query is
        # littered with punctuation elsewhere.
        assert exact_name_match("rds", normalize_modname("manage, dns records, zones.")) is False
