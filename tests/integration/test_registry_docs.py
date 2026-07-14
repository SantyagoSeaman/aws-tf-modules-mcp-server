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
