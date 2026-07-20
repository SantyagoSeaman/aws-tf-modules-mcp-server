import io
import json
import re
import sys
import tarfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_any_overlay as bao  # noqa: E402 -- sys.path must be set up first
from tfmod_any_examples import find_any_vars  # noqa: E402 -- sys.path must be set up first

FIXTURES = REPO_ROOT / "tests/fixtures/any_examples"
S3_DIR = FIXTURES / "s3_bucket"
EC_DIR = FIXTURES / "elasticache"
OS_DIR = FIXTURES / "opensearch"

S3_ID = "terraform-aws-modules/s3-bucket/aws"
S3_VERSION = "5.14.1"
EC_ID = "terraform-aws-modules/elasticache/aws"
EC_VERSION = "1.9.0"
OS_ID = "terraform-aws-modules/opensearch/aws"
OS_VERSION = "2.11.0"

ALLOWED_PROVENANCE = {"example", "example+names", "names-only", "honest-any"}


def _looks_balanced(block: str) -> bool:
    return block.count("[") == block.count("]") and block.count("{") == block.count("}")


# --------------------------------------------------------------------------- #
# build_overlay_from_source - pure, offline (a)-(e)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("module_id", "version", "source_dir"),
    [
        (S3_ID, S3_VERSION, S3_DIR),
        (EC_ID, EC_VERSION, EC_DIR),
        (OS_ID, OS_VERSION, OS_DIR),
    ],
)
def test_overlay_parses_and_keys_map_to_real_any_vars(module_id, version, source_dir):
    overlay = bao.build_overlay_from_source(module_id, version, source_dir)
    assert overlay is not None

    # (a) round-trips through JSON exactly like the committed file will.
    reparsed = json.loads(bao.serialize_overlay(overlay))
    assert reparsed == overlay

    assert overlay["module_id"] == module_id
    assert overlay["built_from_version"] == version

    # (b) every key maps to a real any-var of that module.
    real_vars = {f"{scope}::{name}" for scope, name in find_any_vars(source_dir)}
    assert set(overlay["vars"]) == real_vars
    assert set(overlay["vars"])  # non-empty for all three fixtures


@pytest.mark.parametrize("source_dir", [S3_DIR, EC_DIR, OS_DIR])
def test_example_strings_are_balanced_hcl(source_dir):
    overlay = bao.build_overlay_from_source("x/y/aws", "0.0.0", source_dir)
    for entry in overlay["vars"].values():
        for block in entry["examples"]:
            assert _looks_balanced(block), f"unbalanced example block: {block!r}"


@pytest.mark.parametrize(
    ("source_dir", "scope", "var_name"),
    [
        (S3_DIR, "root", "lifecycle_rule"),
        (EC_DIR, "root", "log_delivery_configuration"),
        (OS_DIR, "root", "cluster_config"),
    ],
)
def test_field_names_nonempty_for_covered_vars(source_dir, scope, var_name):
    overlay = bao.build_overlay_from_source("x/y/aws", "0.0.0", source_dir)
    entry = overlay["vars"][f"{scope}::{var_name}"]
    assert entry["examples"], "flagship var must have a non-trivial example"
    assert entry["field_names"], "flagship var must have observed field names"
    assert entry["provenance"] in ("example", "example+names")


@pytest.mark.parametrize("source_dir", [S3_DIR, EC_DIR, OS_DIR])
def test_provenance_values_from_allowed_set(source_dir):
    overlay = bao.build_overlay_from_source("x/y/aws", "0.0.0", source_dir)
    for key, entry in overlay["vars"].items():
        assert entry["provenance"] in ALLOWED_PROVENANCE, f"{key}: unexpected provenance {entry['provenance']!r}"
        # `note` is reserved for the honest-any fallback (per spec's honesty labels).
        assert ("note" in entry) == (entry["provenance"] == "honest-any"), key


# --------------------------------------------------------------------------- #
# (f) determinism - two independent builds from the same source serialize
# byte-identical.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("source_dir", [S3_DIR, EC_DIR, OS_DIR])
def test_build_is_deterministic(source_dir):
    first = bao.serialize_overlay(bao.build_overlay_from_source("x/y/aws", "0.0.0", source_dir))
    second = bao.serialize_overlay(bao.build_overlay_from_source("x/y/aws", "0.0.0", source_dir))
    assert first == second


def test_write_overlay_twice_produces_identical_bytes(tmp_path):
    overlay = bao.build_overlay_from_source(EC_ID, EC_VERSION, EC_DIR)
    path1 = bao.write_overlay(overlay, tmp_path / "run1")
    path2 = bao.write_overlay(overlay, tmp_path / "run2")
    assert path1.read_bytes() == path2.read_bytes()


# --------------------------------------------------------------------------- #
# (g) known honest-any vars - un-exampled, no meaningful observed names.
# --------------------------------------------------------------------------- #


def test_s3_metadata_encryption_configuration_is_honest_any_not_example():
    overlay = bao.build_overlay_from_source(S3_ID, S3_VERSION, S3_DIR)
    entry = overlay["vars"]["root::metadata_encryption_configuration"]
    assert entry["provenance"] in ("honest-any", "names-only")
    assert entry["provenance"] != "example"
    assert entry["provenance"] != "example+names"
    if entry["provenance"] == "honest-any":
        assert entry["examples"] == []
        assert "note" in entry and entry["note"]


def test_opensearch_cognito_options_is_honest_any_not_example():
    overlay = bao.build_overlay_from_source(OS_ID, OS_VERSION, OS_DIR)
    entry = overlay["vars"]["root::cognito_options"]
    assert entry["provenance"] in ("honest-any", "names-only")
    assert entry["provenance"] not in ("example", "example+names")


# --------------------------------------------------------------------------- #
# Zero any-vars -> no overlay at all.
# --------------------------------------------------------------------------- #


def test_module_with_zero_any_vars_returns_none(tmp_path):
    (tmp_path / "variables.tf").write_text('variable "plain" {\n  type = string\n}\n')
    assert bao.build_overlay_from_source("someorg/plain/aws", "1.0.0", tmp_path) is None


# --------------------------------------------------------------------------- #
# serialize_overlay / write_overlay - naming + formatting contract.
# --------------------------------------------------------------------------- #


def test_serialize_overlay_sorts_keys_and_ends_with_newline():
    overlay = {"vars": {}, "module_id": "a/b/c", "built_from_version": "1.0.0"}
    text = bao.serialize_overlay(overlay)
    assert text.endswith("\n") and not text.endswith("\n\n")
    keys_in_order = [m.group(1) for m in re.finditer(r'^  "([a-z_]+)":', text, re.MULTILINE)]
    assert keys_in_order == sorted(keys_in_order)


def test_write_overlay_filename_from_module_id(tmp_path):
    overlay = bao.build_overlay_from_source(EC_ID, EC_VERSION, EC_DIR)
    path = bao.write_overlay(overlay, tmp_path)
    assert path.name == "terraform-aws-modules__elasticache__aws.json"
    assert path.parent == tmp_path


# --------------------------------------------------------------------------- #
# discover_catalog_modules - reads the real committed docs, no network.
# --------------------------------------------------------------------------- #


def test_discover_catalog_modules_finds_real_catalog():
    catalog = bao.discover_catalog_modules(REPO_ROOT / "modules")
    catalog_dict = dict(catalog)
    assert catalog_dict.get(S3_ID) == S3_VERSION
    assert len(catalog) == 63  # matches the documented catalog size
    assert catalog == sorted(catalog)  # deterministic ordering


def test_discover_catalog_modules_excludes_template_and_prompts():
    catalog_ids = {mid for mid, _ver in bao.discover_catalog_modules(REPO_ROOT / "modules")}
    assert not any("module_template" in mid for mid in catalog_ids)
    assert "UPDATE_PROMPTS" not in catalog_ids


# --------------------------------------------------------------------------- #
# build_module_overlay - the fetch-then-build path, injected fetch (offline).
# --------------------------------------------------------------------------- #


def _tar_gz_of_tf_files(root: Path, top_dir: str) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for path in sorted(root.rglob("*.tf")):
            rel = path.relative_to(root)
            data = path.read_bytes()
            info = tarfile.TarInfo(name=f"{top_dir}/{rel.as_posix()}")
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_build_module_overlay_end_to_end_with_injected_fetch(tmp_path):
    archive = _tar_gz_of_tf_files(EC_DIR, "terraform-aws-elasticache-1.9.0")
    detail_url = f"https://registry.terraform.io/v1/modules/{EC_ID}/{EC_VERSION}"
    v_tag_url = "https://codeload.github.com/terraform-aws-modules/terraform-aws-elasticache/tar.gz/refs/tags/v1.9.0"
    detail = json.dumps({"source": "https://github.com/terraform-aws-modules/terraform-aws-elasticache"}).encode()

    def fetch(url):
        if url == detail_url:
            return detail
        if url == v_tag_url:
            return archive
        raise RuntimeError(f"unexpected url in test fetch: {url}")

    overlay = bao.build_module_overlay(EC_ID, EC_VERSION, fetch=fetch, workdir=tmp_path)

    assert overlay is not None
    assert overlay["module_id"] == EC_ID
    assert overlay["built_from_version"] == EC_VERSION
    assert "root::log_delivery_configuration" in overlay["vars"]


def test_build_module_overlay_returns_none_when_fetch_fails(tmp_path):
    def always_raises(url):
        raise RuntimeError("simulated network failure")

    assert bao.build_module_overlay(EC_ID, EC_VERSION, fetch=always_raises, workdir=tmp_path) is None


# --------------------------------------------------------------------------- #
# Wheel packaging guard (cheap, offline - the real wheel build is covered by
# tests/e2e/test_package_e2e.py).
# --------------------------------------------------------------------------- #


def test_pyproject_force_includes_any_overlay_dir():
    import tomllib

    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    force_include = data["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"]
    assert force_include.get("model/any_overlay") == "model/any_overlay"


def test_any_overlay_dir_exists_for_wheel_build():
    # hatchling raises FileNotFoundError on a force-include source that does
    # not exist at all; a committed placeholder keeps the wheel buildable
    # before real overlay JSON files land (later, human-reviewed step).
    assert (REPO_ROOT / "model/any_overlay").is_dir()
