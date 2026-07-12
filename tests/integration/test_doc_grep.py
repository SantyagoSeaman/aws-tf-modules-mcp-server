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
