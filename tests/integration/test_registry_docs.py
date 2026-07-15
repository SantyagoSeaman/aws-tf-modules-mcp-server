import json
from pathlib import Path

import pytest

from tfmod_registry_docs import assemble_document, get_assembled_docs, parse_module_id

FIX = json.loads((Path(__file__).parent.parent / "fixtures/registry_vpc_min.json").read_text())


def test_parse_module_id_ok():
    assert parse_module_id("terraform-aws-modules/vpc/aws") == ("terraform-aws-modules", "vpc", "aws")


def test_parse_module_id_bad():
    with pytest.raises(ValueError):
        parse_module_id("vpc/aws")


def test_assemble_contains_sections_and_inputs():
    text = assemble_document(FIX)
    assert "===== ROOT README =====" in text
    assert "===== ROOT INPUTS =====" in text
    assert "enable_nat_gateway" in text  # rendered input row


def test_pinned_version_not_refetched(tmp_path):
    calls = {"n": 0}

    def fake_fetch(ns, name, prov, ver):
        calls["n"] += 1
        return FIX

    get_assembled_docs("terraform-aws-modules/vpc/aws", "6.6.1", cache_dir=tmp_path, fetch=fake_fetch)
    b = get_assembled_docs("terraform-aws-modules/vpc/aws", "6.6.1", cache_dir=tmp_path, fetch=fake_fetch)
    assert calls["n"] == 1 and b[3] is True  # second is cache hit


def test_refresh_bypasses_cache(tmp_path):
    calls = {"n": 0}

    def fake_fetch(ns, name, prov, ver):
        calls["n"] += 1
        return FIX

    get_assembled_docs("terraform-aws-modules/vpc/aws", "6.6.1", cache_dir=tmp_path, fetch=fake_fetch)
    get_assembled_docs("terraform-aws-modules/vpc/aws", "6.6.1", cache_dir=tmp_path, refresh=True, fetch=fake_fetch)
    assert calls["n"] == 2


def test_latest_ttl_expiry(tmp_path):
    calls = {"n": 0}

    def fake_fetch(ns, name, prov, ver):
        calls["n"] += 1
        return FIX

    get_assembled_docs("terraform-aws-modules/vpc/aws", None, cache_dir=tmp_path, ttl_hours=0, fetch=fake_fetch)
    get_assembled_docs("terraform-aws-modules/vpc/aws", None, cache_dir=tmp_path, ttl_hours=0, fetch=fake_fetch)
    assert calls["n"] == 2  # ttl=0 always stale


def test_http_fetch_rejects_non_https(monkeypatch):
    """The one networked path must refuse any non-https URL before opening it."""
    import tfmod_registry_docs as rd

    monkeypatch.setattr(rd, "REGISTRY_API_BASE", "http://insecure.example/v1/modules")
    with pytest.raises(ValueError, match="non-https"):
        rd._http_fetch("terraform-aws-modules", "vpc", "aws", None)


def test_write_cache_entry_is_atomic_and_leaves_no_tmp(tmp_path):
    from tfmod_registry_docs import _write_cache_entry

    target = tmp_path / "ns--name--prov--1.0.0.json"
    _write_cache_entry(target, {"document": "x", "fetched_at": 0})

    assert target.exists()
    assert json.loads(target.read_text())["document"] == "x"
    leftovers = [p for p in tmp_path.iterdir() if p.name != target.name]
    assert leftovers == [], f"temp files left behind: {leftovers}"


def test_unwritable_cache_dir_degrades_to_uncached_fetch(tmp_path, caplog):
    """A root-owned/read-only cache dir must not fail the tool call (found live:
    a compose named volume mounted over ~/.cache is created root-owned)."""
    import logging
    import stat

    ro_parent = tmp_path / "ro"
    ro_parent.mkdir()
    cache_dir = ro_parent / "registry_docs"
    ro_parent.chmod(stat.S_IRUSR | stat.S_IXUSR)  # read+exec only: mkdir inside fails
    try:
        import tfmod_registry_docs as rd

        calls = []

        def fake_fetch(ns, name, prov, ver):
            calls.append(ver)
            return FIX

        with caplog.at_level(logging.WARNING):
            text, resolved, _url, cache_hit, _ts = get_assembled_docs(
                "terraform-aws-modules/vpc/aws", None, cache_dir=cache_dir, fetch=fake_fetch
            )
        assert calls, "fetch did not happen"
        assert text and resolved
        assert cache_hit is False
        assert any("not writable" in r.message for r in caplog.records)
        # Second call: still works (refetches, since nothing could be cached)
        rd._MEMORY_CACHE.clear()
        text2, *_ = get_assembled_docs("terraform-aws-modules/vpc/aws", None, cache_dir=cache_dir, fetch=fake_fetch)
        assert text2 == text
    finally:
        ro_parent.chmod(stat.S_IRWXU)
