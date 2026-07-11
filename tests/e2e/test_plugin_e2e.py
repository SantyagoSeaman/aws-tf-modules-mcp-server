"""
End-to-end tests for the Claude Code / Codex plugin packaging.

Contract tests validate the marketplace and plugin manifests, the MCP server
wiring, and the skills against the layout both ecosystems expect. When the
`claude` CLI is available, the plugin is additionally strict-validated and
live-installed into an isolated CLAUDE_CONFIG_DIR.
"""

import json
import os
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent
PLUGIN_DIR = PROJECT_ROOT / "plugins" / "tfmod-search"
SKILLS_DIR = PLUGIN_DIR / "skills"


def _load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def _project_version() -> str:
    with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


def _parse_frontmatter(skill_md: Path) -> tuple[dict, str]:
    text = skill_md.read_text()
    assert text.startswith("---\n"), f"{skill_md} missing YAML front-matter"
    _, frontmatter, body = text.split("---\n", 2)
    return yaml.safe_load(frontmatter), body


class TestClaudeManifests:
    def test_marketplace_manifest(self):
        mp = _load_json(PROJECT_ROOT / ".claude-plugin" / "marketplace.json")
        assert mp["name"] == "tfmodsearch"
        assert mp["owner"]["name"]
        (entry,) = mp["plugins"]
        assert entry["name"] == "tfmod-search"
        source = PROJECT_ROOT / entry["source"]
        assert source.resolve() == PLUGIN_DIR.resolve()
        assert source.is_dir()

    def test_plugin_manifest(self):
        manifest = _load_json(PLUGIN_DIR / ".claude-plugin" / "plugin.json")
        assert manifest["name"] == "tfmod-search"
        assert manifest["version"] == _project_version()
        server = manifest["mcpServers"]["tfmod-search"]
        assert server["command"] == "uvx"
        assert server["args"] == ["tfmodsearch"]


class TestCodexManifests:
    def test_marketplace_manifest(self):
        mp = _load_json(PROJECT_ROOT / ".agents" / "plugins" / "marketplace.json")
        (entry,) = mp["plugins"]
        assert entry["name"] == "tfmod-search"
        source = PROJECT_ROOT / entry["source"]["path"]
        assert source.resolve() == PLUGIN_DIR.resolve()

    def test_plugin_manifest(self):
        manifest = _load_json(PLUGIN_DIR / ".codex-plugin" / "plugin.json")
        assert manifest["name"] == "tfmod-search"
        assert manifest["version"] == _project_version()
        assert (PLUGIN_DIR / manifest["skills"]).is_dir()
        server = _load_json(PLUGIN_DIR / manifest["mcpServers"])["tfmod-search"]
        assert server["command"] == "uvx"
        assert server["args"] == ["tfmodsearch"]

    def test_no_ambiguous_mcp_json_at_plugin_root(self):
        # Claude and Codex both auto-scan a root `.mcp.json`, with incompatible
        # formats; the plugin must not ship one.
        assert not (PLUGIN_DIR / ".mcp.json").exists()


class TestSkills:
    def test_expected_skills_present(self):
        skills = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
        assert skills == {"aws-terraform-modules", "tf-module"}

    @pytest.mark.parametrize("skill_name", sorted(p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")))
    def test_skill_frontmatter(self, skill_name):
        frontmatter, body = _parse_frontmatter(SKILLS_DIR / skill_name / "SKILL.md")
        assert frontmatter["name"] == skill_name
        assert frontmatter["description"]
        assert len(frontmatter["description"]) <= 1024
        assert body.strip(), "skill body must not be empty"

    def test_flagship_skill_references_all_tools(self):
        _, body = _parse_frontmatter(SKILLS_DIR / "aws-terraform-modules" / "SKILL.md")
        for tool in ("search_modules", "get_module", "modules_list"):
            assert tool in body, f"flagship skill must reference {tool}"

    def test_lookup_skill_is_user_invoked_with_arguments(self):
        frontmatter, body = _parse_frontmatter(SKILLS_DIR / "tf-module" / "SKILL.md")
        assert frontmatter.get("disable-model-invocation") is True
        assert "$ARGUMENTS" in body

    def test_codex_skill_binding_declares_mcp_dependency(self):
        binding = yaml.safe_load((SKILLS_DIR / "aws-terraform-modules" / "agents" / "openai.yaml").read_text())
        assert binding["policy"]["allow_implicit_invocation"] is True
        assert {"type": "mcp", "value": "tfmod-search"} in binding["dependencies"]["tools"]


requires_claude_cli = pytest.mark.skipif(shutil.which("claude") is None, reason="claude CLI not installed")


@requires_claude_cli
class TestClaudeCliLive:
    @pytest.mark.e2e
    @pytest.mark.timeout(120)
    def test_strict_validation(self):
        for target in (".claude-plugin/marketplace.json", "plugins/tfmod-search"):
            proc = subprocess.run(
                ["claude", "plugin", "validate", target, "--strict"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert proc.returncode == 0, f"{target}: {proc.stdout}\n{proc.stderr}"

    @pytest.mark.e2e
    @pytest.mark.timeout(300)
    def test_live_install_into_isolated_config(self, tmp_path):
        """Full install flow against an isolated config: add marketplace from
        the local repo, install the plugin, and verify its component inventory."""
        env = {**os.environ, "CLAUDE_CONFIG_DIR": str(tmp_path / "claude-config")}

        def plugin(*args: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                ["claude", "plugin", *args],
                env=env,
                cwd=tmp_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

        added = plugin("marketplace", "add", str(PROJECT_ROOT))
        assert added.returncode == 0, added.stderr or added.stdout

        installed = plugin("install", "tfmod-search@tfmodsearch")
        assert installed.returncode == 0, installed.stderr or installed.stdout

        listed = plugin("list")
        assert listed.returncode == 0
        assert "tfmod-search" in listed.stdout

        details = plugin("details", "tfmod-search")
        assert details.returncode == 0, details.stderr or details.stdout
        inventory = details.stdout
        assert "aws-terraform-modules" in inventory, "flagship skill missing from inventory"
        assert "tf-module" in inventory, "lookup skill missing from inventory"
