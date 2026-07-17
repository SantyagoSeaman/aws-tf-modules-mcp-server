"""
End-to-end packaging tests: build the wheel, verify its payload and metadata,
and run the packaged entry point via uvx from a foreign working directory.
"""

import shutil
import subprocess
import tomllib
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent


def _project_version() -> str:
    with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


@pytest.fixture(scope="module")
def built_wheel(tmp_path_factory) -> Path:
    if shutil.which("uv") is None:
        pytest.skip("uv is not installed")
    out_dir = tmp_path_factory.mktemp("dist")
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(out_dir)],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )
    wheels = list(out_dir.glob("tfmodsearch-*.whl"))
    assert len(wheels) == 1, f"expected exactly one wheel, got {wheels}"
    return wheels[0]


@pytest.mark.e2e
def test_wheel_payload(built_wheel):
    names = zipfile.ZipFile(built_wheel).namelist()

    assert "model/tfmod_e5_small_index.pkl" in names
    assert "config.yaml" in names
    for module in ("tfmod_mcp_server.py", "tfmod_search_cli.py", "tfmod_search_lib.py"):
        assert module in names

    docs = [n for n in names if n.startswith("modules/terraform-aws-modules/")]
    assert len(docs) == 55
    # Cloud Posse gap-fillers ship from their own vendor subdir (force-included separately).
    cloudposse_docs = [n for n in names if n.startswith("modules/cloudposse/")]
    assert len(cloudposse_docs) == 8, f"cloudposse docs missing from wheel: {cloudposse_docs}"

    strays = [
        n
        for n in names
        if "gte_small" in n or n.startswith("modules/temp/") or "UPDATE_PROMPTS" in n or "module_template" in n
    ]
    assert not strays, f"stray files leaked into the wheel: {strays}"


@pytest.mark.e2e
def test_wheel_metadata_and_entry_points(built_wheel):
    version = _project_version()
    zf = zipfile.ZipFile(built_wheel)
    dist_info = f"tfmodsearch-{version}.dist-info"

    metadata = zf.read(f"{dist_info}/METADATA").decode()
    assert "Name: tfmodsearch" in metadata
    assert f"Version: {version}" in metadata

    entry_points = zf.read(f"{dist_info}/entry_points.txt").decode()
    for script in ("tfmodsearch", "tfmodsearch-cli", "aws-tf-modules-mcp-server", "tfmod-search-cli"):
        assert f"{script} = " in entry_points, f"missing console script: {script}"


@pytest.mark.e2e
@pytest.mark.timeout(600)
def test_uvx_runs_packaged_server_warmup(built_wheel, tmp_path):
    """The wheel must run from any directory: package-relative index/config resolution."""
    if shutil.which("uvx") is None:
        pytest.skip("uvx is not installed")
    proc = subprocess.run(
        ["uvx", "--from", str(built_wheel), "tfmodsearch", "--warmup"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=580,
    )
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert "Warmup complete" in proc.stdout
    assert "63 modules" in proc.stdout
