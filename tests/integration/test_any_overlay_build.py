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
S3_VERSION = "5.14.1"  # fixture pin (tests/fixtures/any_examples/s3_bucket) -- independent of the real catalog doc
S3_CATALOG_VERSION = "5.15.1"  # the real, committed modules/terraform-aws-modules/s3-bucket.md pin
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
    assert catalog_dict.get(S3_ID) == S3_CATALOG_VERSION
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
# all_inputs - complete root+submodule input list from the registry detail
# already fetched (complete-interface-in-one-call design).
# --------------------------------------------------------------------------- #

SAMPLE_DETAIL = {
    "root": {
        "inputs": [
            {
                "name": "create_subnet_group",
                "type": "bool",
                "required": False,
                "default": "true",
                "description": "Determines whether the subnet group will be created",
            },
            {"name": "port", "type": "number", "required": False, "default": "null", "description": "The port number"},
        ],
        "outputs": [
            {"name": "replication_group_id", "description": "Identifier of the replication group"},
            {"name": "port", "description": "The port number"},
        ],
    },
    "submodules": [
        {
            "name": "user-group",
            "inputs": [
                {"name": "users", "type": "list(string)", "required": True, "default": "", "description": "User ARNs"},
            ],
            "outputs": [
                {"name": "group_id", "description": "ID of the user group"},
            ],
        },
        {
            "name": "wrappers",
            "inputs": [
                {"name": "defaults", "type": "any", "required": False, "default": "{}", "description": "ignored"},
            ],
            "outputs": [
                {"name": "defaults", "description": "ignored"},
            ],
        },
    ],
}


def test_extract_all_inputs_covers_root_and_submodules():
    all_inputs = bao._extract_all_inputs(SAMPLE_DETAIL)
    assert {i["name"] for i in all_inputs["root"]} == {"create_subnet_group", "port"}
    assert {i["name"] for i in all_inputs["user-group"]} == {"users"}
    assert "wrappers" not in all_inputs, "wrappers is never a real submodule scope"


def test_extract_all_inputs_item_shape():
    all_inputs = bao._extract_all_inputs(SAMPLE_DETAIL)
    port = next(i for i in all_inputs["root"] if i["name"] == "port")
    assert port == {
        "name": "port",
        "type": "number",
        "required": False,
        "default": "null",
        "description": "The port number",
    }
    users = next(i for i in all_inputs["user-group"] if i["name"] == "users")
    assert users["required"] is True


def test_extract_all_inputs_handles_missing_root_and_submodules():
    assert bao._extract_all_inputs({}) == {"root": []}


# --------------------------------------------------------------------------- #
# all_outputs - complete root+submodule output list from the SAME registry
# detail response all_inputs is extracted from (complete-interface-in-one-call
# design, outputs half). Outputs carry no type/required/default in the
# Registry API - name + description only.
# --------------------------------------------------------------------------- #


def test_extract_all_outputs_covers_root_and_submodules():
    all_outputs = bao._extract_all_outputs(SAMPLE_DETAIL)
    assert {o["name"] for o in all_outputs["root"]} == {"replication_group_id", "port"}
    assert {o["name"] for o in all_outputs["user-group"]} == {"group_id"}
    assert "wrappers" not in all_outputs, "wrappers is never a real submodule scope"


def test_extract_all_outputs_item_shape():
    all_outputs = bao._extract_all_outputs(SAMPLE_DETAIL)
    port = next(o for o in all_outputs["root"] if o["name"] == "port")
    assert port == {"name": "port", "description": "The port number"}
    assert "type" not in port
    assert "required" not in port
    assert "default" not in port


def test_extract_all_outputs_handles_missing_root_and_submodules():
    assert bao._extract_all_outputs({}) == {"root": []}


def test_build_module_overlay_includes_all_inputs_from_detail(tmp_path):
    archive = _tar_gz_of_tf_files(EC_DIR, "terraform-aws-elasticache-1.9.0")
    detail_url = f"https://registry.terraform.io/v1/modules/{EC_ID}/{EC_VERSION}"
    v_tag_url = "https://codeload.github.com/terraform-aws-modules/terraform-aws-elasticache/tar.gz/refs/tags/v1.9.0"
    detail_payload = {
        "source": "https://github.com/terraform-aws-modules/terraform-aws-elasticache",
        "root": {
            "inputs": [
                {
                    "name": "port",
                    "type": "number",
                    "required": False,
                    "default": "null",
                    "description": "The port",
                }
            ],
            "outputs": [
                {"name": "port", "description": "The port"},
            ],
        },
        "submodules": [],
    }
    detail_bytes = json.dumps(detail_payload).encode()

    def fetch(url):
        if url == detail_url:
            return detail_bytes
        if url == v_tag_url:
            return archive
        raise RuntimeError(f"unexpected url in test fetch: {url}")

    overlay = bao.build_module_overlay(EC_ID, EC_VERSION, fetch=fetch, workdir=tmp_path)

    assert overlay is not None
    assert overlay["all_inputs"]["root"] == [
        {"name": "port", "type": "number", "required": False, "default": "null", "description": "The port"}
    ]
    assert overlay["all_outputs"]["root"] == [{"name": "port", "description": "The port"}]
    assert "root::log_delivery_configuration" in overlay["vars"]


def test_build_module_overlay_degrades_gracefully_when_detail_fetch_fails_after_source(tmp_path):
    """A transient failure on the SECOND (all_inputs/all_outputs) detail
    fetch must not fail the whole build -- the overlay still carries its
    vars, just without all_inputs/all_outputs."""
    archive = _tar_gz_of_tf_files(EC_DIR, "terraform-aws-elasticache-1.9.0")
    detail_url = f"https://registry.terraform.io/v1/modules/{EC_ID}/{EC_VERSION}"
    v_tag_url = "https://codeload.github.com/terraform-aws-modules/terraform-aws-elasticache/tar.gz/refs/tags/v1.9.0"
    detail_bytes = json.dumps({"source": "https://github.com/terraform-aws-modules/terraform-aws-elasticache"}).encode()

    calls = {"detail": 0}

    def fetch(url):
        if url == detail_url:
            calls["detail"] += 1
            if calls["detail"] == 1:
                return detail_bytes
            raise RuntimeError("simulated transient failure")
        if url == v_tag_url:
            return archive
        raise RuntimeError(f"unexpected url in test fetch: {url}")

    overlay = bao.build_module_overlay(EC_ID, EC_VERSION, fetch=fetch, workdir=tmp_path)
    assert overlay is not None
    assert "root::log_delivery_configuration" in overlay["vars"]
    assert "all_inputs" not in overlay
    assert "all_outputs" not in overlay


# --------------------------------------------------------------------------- #
# Full-catalog extension (2026-07-21): every one of the 63 catalog modules
# gets an overlay now, not just the ones with `type = any` inputs. The two
# halves (vars via GitHub source, all_inputs/all_outputs via registry detail)
# must fail independently.
# --------------------------------------------------------------------------- #


def test_build_module_overlay_zero_any_vars_still_gets_all_inputs(tmp_path):
    """A module with zero `type = any` variables (the common case, 41 of 63
    catalog modules) must still get all_inputs/all_outputs from the registry
    detail -- with no `vars` key at all."""
    plain_src = tmp_path / "plain_src"
    plain_src.mkdir()
    (plain_src / "variables.tf").write_text('variable "name" {\n  type = string\n}\n')

    module_id = "someorg/plain/aws"
    version = "1.0.0"
    archive = _tar_gz_of_tf_files(plain_src, "terraform-aws-plain-1.0.0")
    detail_url = f"https://registry.terraform.io/v1/modules/{module_id}/{version}"
    v_tag_url = "https://codeload.github.com/someorg/terraform-aws-plain/tar.gz/refs/tags/v1.0.0"
    detail_payload = {
        "source": "https://github.com/someorg/terraform-aws-plain",
        "root": {
            "inputs": [
                {"name": "name", "type": "string", "required": True, "default": "", "description": "Name"},
            ],
            "outputs": [{"name": "name_out", "description": "Name output"}],
        },
        "submodules": [],
    }
    detail_bytes = json.dumps(detail_payload).encode()

    def fetch(url):
        if url == detail_url:
            return detail_bytes
        if url == v_tag_url:
            return archive
        raise RuntimeError(f"unexpected url in test fetch: {url}")

    overlay = bao.build_module_overlay(module_id, version, fetch=fetch, workdir=tmp_path / "work")

    assert overlay is not None
    assert overlay["module_id"] == module_id
    assert overlay["built_from_version"] == version
    assert overlay["all_inputs"]["root"] == [
        {"name": "name", "type": "string", "required": True, "default": "", "description": "Name"}
    ]
    assert overlay["all_outputs"]["root"] == [{"name": "name_out", "description": "Name output"}]
    assert "vars" not in overlay


def test_build_module_overlay_source_fetch_fails_still_gets_all_inputs(tmp_path):
    """The GitHub source cannot be resolved (a non-GitHub `source` field, so
    `fetch_module_source` fails outright) but the registry detail (all_inputs/
    all_outputs) still succeeds -- the module still gets an overlay, just
    without vars. Proves the two halves are decoupled failures."""
    module_id = "someorg/nogithub/aws"
    version = "1.0.0"
    detail_url = f"https://registry.terraform.io/v1/modules/{module_id}/{version}"
    detail_payload = {
        "source": "https://gitlab.com/someorg/terraform-nogithub",
        "root": {
            "inputs": [
                {"name": "x", "type": "string", "required": False, "default": '"y"', "description": "X"},
            ],
            "outputs": [],
        },
        "submodules": [],
    }
    detail_bytes = json.dumps(detail_payload).encode()

    def fetch(url):
        if url == detail_url:
            return detail_bytes
        raise RuntimeError(f"unexpected url in test fetch: {url}")

    overlay = bao.build_module_overlay(module_id, version, fetch=fetch, workdir=tmp_path)

    assert overlay is not None
    assert "vars" not in overlay
    assert overlay["all_inputs"]["root"][0]["name"] == "x"
    assert overlay["all_outputs"] == {"root": []}


def test_build_module_overlay_returns_none_when_both_halves_fail(tmp_path):
    """Total failure (source AND registry detail both unreachable) -> no
    overlay at all, matching the pre-existing fetch-failure contract."""

    def always_raises(url):
        raise RuntimeError("simulated network failure")

    overlay = bao.build_module_overlay("someorg/whatever/aws", "1.0.0", fetch=always_raises, workdir=tmp_path)
    assert overlay is None


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


# --------------------------------------------------------------------------- #
# Full-catalog coverage regression guard (2026-07-21): every one of the 63
# catalog modules must have a committed overlay carrying all_inputs/
# all_outputs, not just the modules with `type = any` inputs. Exercises the
# REAL, committed model/any_overlay/ directory (built via `--all`), so this is
# a durable guard against a future catalog module landing without a
# corresponding overlay regeneration.
# --------------------------------------------------------------------------- #


def test_every_catalog_module_has_committed_overlay_with_complete_interface():
    catalog = dict(bao.discover_catalog_modules(REPO_ROOT / "modules"))
    overlay_dir = REPO_ROOT / "model" / "any_overlay"
    missing = []
    no_all_inputs = []
    no_all_outputs = []
    for module_id in catalog:
        path = overlay_dir / bao._overlay_filename(module_id)
        if not path.is_file():
            missing.append(module_id)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("all_inputs"):
            no_all_inputs.append(module_id)
        if not data.get("all_outputs"):
            no_all_outputs.append(module_id)
    assert not missing, f"catalog modules with no overlay file at all: {sorted(missing)}"
    assert not no_all_inputs, f"overlays missing all_inputs: {sorted(no_all_inputs)}"
    assert not no_all_outputs, f"overlays missing all_outputs: {sorted(no_all_outputs)}"


def test_any_overlay_dir_has_exactly_63_files():
    files = sorted((REPO_ROOT / "model" / "any_overlay").glob("*.json"))
    assert len(files) == 63, f"expected 63 overlay files, found {len(files)}: {[f.name for f in files]}"


def test_22_any_modules_carry_vars_41_do_not():
    """The catalog-wide split matches the design: 22 modules with at least
    one `type = any` input carry `vars`; the remaining 41 (zero any-vars)
    carry only all_inputs/all_outputs."""
    overlay_dir = REPO_ROOT / "model" / "any_overlay"
    with_vars = 0
    without_vars = 0
    for path in overlay_dir.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("vars"):
            with_vars += 1
        else:
            without_vars += 1
    assert with_vars == 22
    assert without_vars == 41
