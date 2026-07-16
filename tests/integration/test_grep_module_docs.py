def test_grep_impl_returns_matches(monkeypatch, tmp_path):
    import json
    from pathlib import Path

    import tfmod_registry_docs as rd

    fix = json.loads((Path(__file__).parent.parent / "fixtures/registry_vpc_min.json").read_text())
    monkeypatch.setattr(rd, "_http_fetch", lambda ns, n, p, v: fix)
    from tfmod_mcp_server import grep_module_docs_impl

    out = grep_module_docs_impl(
        "terraform-aws-modules/vpc/aws",
        "enable_nat_gateway",
        version="6.6.1",
        cache_dir=tmp_path,
    )
    assert out.total_matches >= 1
    assert out.resolved_version == fix["version"]
    assert out.matches[0].section.startswith("root/")


def test_grep_impl_invalid_module_id(tmp_path):
    import pytest

    from tfmod_mcp_server import grep_module_docs_impl

    with pytest.raises(ValueError):
        grep_module_docs_impl("vpc/aws", "x", cache_dir=tmp_path)


def test_grep_impl_match_carries_enclosing_breadcrumb(monkeypatch, tmp_path):
    """RC2 C1 end-to-end: a scoped grep match landing on a continuation line of a
    multi-line input row (nested object type) must carry the enclosing
    "- <name> | ..." header row in the tool response, so the container key is
    always visible even when the match itself is not on the header line."""
    import tfmod_registry_docs as rd

    detail = {
        "namespace": "ns",
        "name": "x",
        "provider": "aws",
        "version": "1.0.0",
        "root": {
            "readme": "some readme",
            "inputs": [
                {
                    "name": "complex_input",
                    "type": "object({\n  a = string\n  b = number\n})",
                    "description": "A complex input",
                    "default": "n/a",
                    "required": False,
                },
            ],
        },
    }
    monkeypatch.setattr(rd, "_http_fetch", lambda ns, n, p, v: detail)
    from tfmod_mcp_server import grep_module_docs_impl

    out = grep_module_docs_impl(
        "ns/x/aws",
        "b = number",
        version="1.0.0",
        scope=["inputs"],
        cache_dir=tmp_path,
    )
    assert out.total_matches == 1
    m = out.matches[0]
    assert m.line.strip() == "b = number"
    assert m.enclosing == "- complex_input | object({"

    # A match on the header row itself carries no enclosing breadcrumb.
    out2 = grep_module_docs_impl(
        "ns/x/aws",
        "complex_input",
        version="1.0.0",
        scope=["inputs"],
        cache_dir=tmp_path,
    )
    assert out2.total_matches == 1
    assert out2.matches[0].enclosing is None


def test_grep_impl_zero_matches_lists_sections(monkeypatch, tmp_path):
    import json
    from pathlib import Path

    import tfmod_registry_docs as rd

    fix = json.loads((Path(__file__).parent.parent / "fixtures/registry_vpc_min.json").read_text())
    monkeypatch.setattr(rd, "_http_fetch", lambda ns, n, p, v: fix)
    from tfmod_mcp_server import grep_module_docs_impl

    out = grep_module_docs_impl(
        "terraform-aws-modules/vpc/aws", "zzz_no_match_zzz", version="6.6.1", cache_dir=tmp_path
    )
    assert out.total_matches == 0 and out.available_sections
