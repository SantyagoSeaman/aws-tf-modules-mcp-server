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
