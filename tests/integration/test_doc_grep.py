from tfmod_doc_grep import grep_document

DOC = """===== MODULE ns/x/aws @ 1.0.0 =====

===== ROOT README =====
line about NAT gateway
another line
===== ROOT INPUTS =====
- enable_nat_gateway | bool | false | Enable NAT
- azs | list | [] | Availability zones
"""


def test_finds_line_with_context_and_section():
    matches, total, sections = grep_document(DOC, "enable_nat_gateway", context_lines=1)
    assert total == 1
    m = matches[0]
    assert "enable_nat_gateway" in m.line
    assert m.section == "root/inputs"
    assert any("INPUTS" not in b for b in m.before)  # has a context line
    assert "root/readme" in sections and "root/inputs" in sections


def test_case_insensitive_default():
    matches, total, _ = grep_document(DOC, "nat GATEWAY")
    assert total >= 1


def test_case_sensitive_flag():
    _, total, _ = grep_document(DOC, "NAT GATEWAY", case_sensitive=True)
    assert total == 0


def test_scope_restricts_search():
    _, total, _ = grep_document(DOC, "gateway", scope=["inputs"])
    assert total == 1  # only the inputs row, not the readme prose


def test_max_matches_caps_returned_not_total():
    matches, total, _ = grep_document(DOC, "line", context_lines=0, max_matches=1)
    assert total == 2 and len(matches) == 1


def test_invalid_regex_raises_valueerror():
    import pytest

    with pytest.raises(ValueError):
        grep_document(DOC, "(")


# --------------------------------------------------------------------------- #
# RC2 C1 - scoped grep must carry the enclosing "- <name> | ..." header row
# when a match lands on a continuation line of a multi-line input row (e.g. a
# nested object/map type), so the model never back-fills a plausible-but-wrong
# container name from the surrounding prose.
# --------------------------------------------------------------------------- #
DOC_MULTILINE_INPUT = """===== MODULE ns/x/aws @ 1.0.0 =====

===== ROOT README =====
Some prose line that happens to start with a dash below.
- not a data row, just a readme bullet
===== ROOT INPUTS =====
- simple_input | string | "" | A simple input
- complex_input | object({
  a = string
  b = number
}) | n/a | A complex input
- another_input | bool | false | Another input
"""


def test_enclosing_is_none_when_match_is_on_the_header_row_itself():
    matches, total, _ = grep_document(DOC_MULTILINE_INPUT, "complex_input", scope=["inputs"])
    assert total == 1
    assert matches[0].line.startswith("- complex_input")
    assert matches[0].enclosing is None


def test_enclosing_carries_the_header_row_for_a_continuation_line_match():
    matches, total, _ = grep_document(DOC_MULTILINE_INPUT, "b = number", scope=["inputs"])
    assert total == 1
    m = matches[0]
    assert m.line.strip() == "b = number"
    assert m.enclosing == "- complex_input | object({"


def test_enclosing_walks_back_over_multiple_continuation_lines():
    matches, total, _ = grep_document(DOC_MULTILINE_INPUT, r"\}\) \| n/a", scope=["inputs"])
    assert total == 1
    m = matches[0]
    assert m.enclosing == "- complex_input | object({"


def test_enclosing_is_none_for_a_simple_single_line_row_match():
    matches, total, _ = grep_document(DOC_MULTILINE_INPUT, "simple_input", scope=["inputs"])
    assert total == 1
    assert matches[0].enclosing is None


DOC_ORPHAN_CONTINUATION = """===== MODULE ns/x/aws @ 1.0.0 =====

===== ROOT README =====
- readme bullet, not an input row
prose continuation of readme
===== ROOT INPUTS =====
  orphan continuation line with no preceding dash row in THIS section
- real_input | string | "" | desc
"""


def test_enclosing_does_not_cross_into_a_different_section():
    # "- readme bullet, not an input row" is the nearest "- " line overall, but
    # it lives in a different section (root/readme). Walking back for the
    # orphan continuation line in root/inputs must stop at the section marker
    # rather than leaking a false enclosing row from the previous section.
    matches, total, _ = grep_document(DOC_ORPHAN_CONTINUATION, "orphan continuation", scope=["inputs"])
    assert total == 1
    assert matches[0].enclosing is None
