"""Contract tests for the repo's security & quality configuration files."""

from pathlib import Path

import pytest
import yaml


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_dependabot_config_covers_github_actions():
    cfg_path = _repo_root() / ".github" / "dependabot.yml"
    assert cfg_path.exists(), "missing .github/dependabot.yml"
    cfg = yaml.safe_load(cfg_path.read_text())
    assert cfg["version"] == 2
    ecosystems = {u["package-ecosystem"] for u in cfg["updates"]}
    assert "github-actions" in ecosystems


def test_security_policy_exists_and_describes_reporting():
    sec_path = _repo_root() / "SECURITY.md"
    assert sec_path.exists(), "missing SECURITY.md"
    text = sec_path.read_text().lower()
    assert "report" in text
    assert "vulnerabilit" in text


@pytest.mark.parametrize("workflow", ["ci.yml", "publish.yml"])
def test_workflow_has_least_privilege_permissions(workflow):
    wf_path = _repo_root() / ".github" / "workflows" / workflow
    wf = yaml.safe_load(wf_path.read_text())
    assert wf["permissions"] == {"contents": "read"}, f"{workflow} must declare top-level permissions: contents: read"


def test_publish_job_retains_oidc_permission():
    """Least-privilege hardening must not strip the publish job's OIDC token grant."""
    wf = yaml.safe_load((_repo_root() / ".github" / "workflows" / "publish.yml").read_text())
    assert wf["jobs"]["publish"]["permissions"] == {"id-token": "write"}
