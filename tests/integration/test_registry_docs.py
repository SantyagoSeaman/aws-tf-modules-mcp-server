import io
import json
import tarfile
from pathlib import Path

import pytest

from tfmod_registry_docs import (
    assemble_document,
    fetch_module_detail,
    fetch_module_source,
    get_assembled_docs,
    parse_module_id,
)

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


# --------------------------------------------------------------------------- #
# fetch_module_source - build-time GitHub source fetch for the any-overlay
# example extractor. All tests inject `fetch` so they run fully offline.
# --------------------------------------------------------------------------- #

DETAIL_GITHUB = json.dumps({"source": "https://github.com/terraform-aws-modules/terraform-aws-s3-bucket"}).encode()


def _make_tar_gz(files: dict[str, bytes], top_dir: str = "terraform-aws-s3-bucket-5.14.1") -> bytes:
    """Build an in-memory gzipped tarball wrapping `files` (relative paths ->
    contents) in a single top-level directory, mirroring the layout of a
    real GitHub codeload archive."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for rel_path, content in files.items():
            info = tarfile.TarInfo(name=f"{top_dir}/{rel_path}")
            info.size = len(content)
            tf.addfile(info, io.BytesIO(content))
    return buf.getvalue()


def _fetch_returning(url_to_bytes: dict[str, bytes], raise_for: set[str] = frozenset()):
    def fetch(url):
        if url in raise_for or any(url.startswith(p) for p in raise_for):
            raise RuntimeError(f"simulated 404 for {url}")
        if url not in url_to_bytes:
            raise RuntimeError(f"unexpected URL in test fetch: {url}")
        return url_to_bytes[url]

    return fetch


def test_fetch_module_source_uses_v_prefixed_tag_first(tmp_path):
    archive = _make_tar_gz({"variables.tf": b'variable "x" {}\n', "examples/complete/main.tf": b"module {}\n"})
    detail_url = "https://registry.terraform.io/v1/modules/terraform-aws-modules/s3-bucket/aws/5.14.1"
    v_tag_url = "https://codeload.github.com/terraform-aws-modules/terraform-aws-s3-bucket/tar.gz/refs/tags/v5.14.1"
    fetch = _fetch_returning({detail_url: DETAIL_GITHUB, v_tag_url: archive})

    result = fetch_module_source("terraform-aws-modules/s3-bucket/aws", "5.14.1", tmp_path, fetch=fetch)

    assert result == tmp_path
    assert (tmp_path / "variables.tf").read_text() == 'variable "x" {}\n'
    assert (tmp_path / "examples/complete/main.tf").read_text() == "module {}\n"


def test_fetch_module_source_falls_back_to_bare_version_tag(tmp_path):
    archive = _make_tar_gz({"variables.tf": b'variable "x" {}\n'}, top_dir="terraform-aws-cloudtrail-0.24.0")
    detail_url = "https://registry.terraform.io/v1/modules/cloudposse/cloudtrail/aws/0.24.0"
    v_tag_url = "https://codeload.github.com/cloudposse/terraform-aws-cloudtrail/tar.gz/refs/tags/v0.24.0"
    bare_tag_url = "https://codeload.github.com/cloudposse/terraform-aws-cloudtrail/tar.gz/refs/tags/0.24.0"
    detail = json.dumps({"source": "https://github.com/cloudposse/terraform-aws-cloudtrail"}).encode()
    fetch = _fetch_returning({detail_url: detail, bare_tag_url: archive}, raise_for={v_tag_url})

    result = fetch_module_source("cloudposse/cloudtrail/aws", "0.24.0", tmp_path, fetch=fetch)

    assert result == tmp_path
    assert (tmp_path / "variables.tf").is_file()


def test_fetch_module_source_falls_back_to_tags_api(tmp_path):
    archive = _make_tar_gz({"variables.tf": b'variable "x" {}\n'}, top_dir="weird-repo-rel-9.9.9")
    detail_url = "https://registry.terraform.io/v1/modules/someorg/weird/aws/9.9.9"
    v_tag_url = "https://codeload.github.com/someorg/weird-repo/tar.gz/refs/tags/v9.9.9"
    bare_tag_url = "https://codeload.github.com/someorg/weird-repo/tar.gz/refs/tags/9.9.9"
    tags_api_url = "https://api.github.com/repos/someorg/weird-repo/tags"
    resolved_tag_url = "https://codeload.github.com/someorg/weird-repo/tar.gz/refs/tags/rel-9.9.9"
    detail = json.dumps({"source": "https://github.com/someorg/weird-repo"}).encode()
    tags_json = json.dumps([{"name": "rel-9.9.9"}, {"name": "rel-8.0.0"}]).encode()
    fetch = _fetch_returning(
        {detail_url: detail, tags_api_url: tags_json, resolved_tag_url: archive},
        raise_for={v_tag_url, bare_tag_url},
    )

    result = fetch_module_source("someorg/weird/aws", "9.9.9", tmp_path, fetch=fetch)

    assert result == tmp_path
    assert (tmp_path / "variables.tf").is_file()


def test_fetch_module_source_returns_none_on_non_github_source(tmp_path):
    detail_url = "https://registry.terraform.io/v1/modules/someorg/mod/aws/1.0.0"
    detail = json.dumps({"source": "git::https://example.com/someorg/mod.git"}).encode()
    fetch = _fetch_returning({detail_url: detail})

    assert fetch_module_source("someorg/mod/aws", "1.0.0", tmp_path, fetch=fetch) is None


def test_fetch_module_source_returns_none_when_no_tag_matches(tmp_path):
    detail_url = "https://registry.terraform.io/v1/modules/someorg/mod/aws/1.0.0"
    tags_api_url = "https://api.github.com/repos/someorg/mod/tags"
    detail = json.dumps({"source": "https://github.com/someorg/mod"}).encode()
    fetch = _fetch_returning(
        {detail_url: detail, tags_api_url: b"[]"},
        raise_for={
            "https://codeload.github.com/someorg/mod/tar.gz/refs/tags/v1.0.0",
            "https://codeload.github.com/someorg/mod/tar.gz/refs/tags/1.0.0",
        },
    )

    assert fetch_module_source("someorg/mod/aws", "1.0.0", tmp_path, fetch=fetch) is None


def test_fetch_module_source_never_raises_on_fetch_exception(tmp_path):
    def always_raises(url):
        raise RuntimeError("network is down")

    assert fetch_module_source("terraform-aws-modules/s3-bucket/aws", "5.14.1", tmp_path, fetch=always_raises) is None


def test_fetch_module_source_bad_module_id_returns_none(tmp_path):
    assert fetch_module_source("not-a-valid-id", "1.0.0", tmp_path, fetch=lambda url: b"") is None


def test_fetch_module_source_extracts_only_tf_files_and_skips_others(tmp_path):
    archive = _make_tar_gz(
        {
            "variables.tf": b'variable "x" {}\n',
            "README.md": b"# readme\n",
            "modules/vectors/variables.tf": b'variable "y" {}\n',
            "LICENSE": b"MIT\n",
        }
    )
    detail_url = "https://registry.terraform.io/v1/modules/terraform-aws-modules/s3-bucket/aws/5.14.1"
    v_tag_url = "https://codeload.github.com/terraform-aws-modules/terraform-aws-s3-bucket/tar.gz/refs/tags/v5.14.1"
    fetch = _fetch_returning({detail_url: DETAIL_GITHUB, v_tag_url: archive})

    result = fetch_module_source("terraform-aws-modules/s3-bucket/aws", "5.14.1", tmp_path, fetch=fetch)

    assert result == tmp_path
    assert (tmp_path / "variables.tf").is_file()
    assert (tmp_path / "modules/vectors/variables.tf").is_file()
    assert not (tmp_path / "README.md").exists()
    assert not (tmp_path / "LICENSE").exists()


# --------------------------------------------------------------------------- #
# fetch_module_detail - standalone registry detail GET (the all_inputs source
# for build_any_overlay.py's complete-interface-in-one-call extraction). All
# tests inject `fetch` so they run fully offline.
# --------------------------------------------------------------------------- #


def test_fetch_module_detail_returns_parsed_json():
    detail_url = "https://registry.terraform.io/v1/modules/terraform-aws-modules/vpc/aws/6.6.1"
    fetch = _fetch_returning({detail_url: json.dumps({"version": "6.6.1"}).encode()})
    assert fetch_module_detail("terraform-aws-modules/vpc/aws", "6.6.1", fetch=fetch) == {"version": "6.6.1"}


def test_fetch_module_detail_returns_none_on_bad_module_id():
    assert fetch_module_detail("not-a-valid-id", "1.0.0", fetch=lambda url: b"") is None


def test_fetch_module_detail_returns_none_on_fetch_exception():
    def always_raises(url):
        raise RuntimeError("network is down")

    assert fetch_module_detail("terraform-aws-modules/vpc/aws", "6.6.1", fetch=always_raises) is None


def test_fetch_module_detail_returns_none_on_malformed_json():
    detail_url = "https://registry.terraform.io/v1/modules/terraform-aws-modules/vpc/aws/6.6.1"
    fetch = _fetch_returning({detail_url: b"{not valid json"})
    assert fetch_module_detail("terraform-aws-modules/vpc/aws", "6.6.1", fetch=fetch) is None


def test_fetch_module_source_guards_against_path_traversal(tmp_path):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        evil = b"resource evil {}\n"
        info = tarfile.TarInfo(name="terraform-aws-s3-bucket-5.14.1/../../evil.tf")
        info.size = len(evil)
        tf.addfile(info, io.BytesIO(evil))
        good = b'variable "x" {}\n'
        info2 = tarfile.TarInfo(name="terraform-aws-s3-bucket-5.14.1/variables.tf")
        info2.size = len(good)
        tf.addfile(info2, io.BytesIO(good))
    archive = buf.getvalue()

    detail_url = "https://registry.terraform.io/v1/modules/terraform-aws-modules/s3-bucket/aws/5.14.1"
    v_tag_url = "https://codeload.github.com/terraform-aws-modules/terraform-aws-s3-bucket/tar.gz/refs/tags/v5.14.1"
    fetch = _fetch_returning({detail_url: DETAIL_GITHUB, v_tag_url: archive})

    result = fetch_module_source("terraform-aws-modules/s3-bucket/aws", "5.14.1", tmp_path, fetch=fetch)

    assert result == tmp_path
    assert (tmp_path / "variables.tf").is_file()
    assert not (tmp_path.parent / "evil.tf").exists()
