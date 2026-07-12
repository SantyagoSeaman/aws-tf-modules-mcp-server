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


EXPECTED_SKILLS = {
    "aws-terraform-modules",
    "tf-module",
    "tf-migrate",
    "tf-module-upgrade",
    "tf-review",
    "tf-stack",
    "tf-troubleshoot",
    "tf-grep",
}
# user-invoked only; everything else may be model-invoked
USER_INVOKED_SKILLS = {"tf-module", "tf-stack", "tf-grep"}
# skills that declare the MCP dependency for Codex (all but the pure-lookup one)
CODEX_BOUND_SKILLS = EXPECTED_SKILLS - {"tf-module"}
EXPECTED_AGENTS = {"tf-log-analyst", "tf-diff-reviewer"}


class TestSkills:
    def test_expected_skills_present(self):
        skills = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
        assert skills == EXPECTED_SKILLS

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

    @pytest.mark.parametrize("skill_name", sorted(USER_INVOKED_SKILLS))
    def test_user_invoked_skills_take_arguments(self, skill_name):
        frontmatter, body = _parse_frontmatter(SKILLS_DIR / skill_name / "SKILL.md")
        assert frontmatter.get("disable-model-invocation") is True
        assert "$ARGUMENTS" in body

    @pytest.mark.parametrize("skill_name", sorted(EXPECTED_SKILLS - USER_INVOKED_SKILLS))
    def test_model_invoked_skills_do_not_disable_invocation(self, skill_name):
        frontmatter, _ = _parse_frontmatter(SKILLS_DIR / skill_name / "SKILL.md")
        assert frontmatter.get("disable-model-invocation") is not True

    @pytest.mark.parametrize("skill_name", sorted(CODEX_BOUND_SKILLS))
    def test_codex_skill_binding_declares_mcp_dependency(self, skill_name):
        binding = yaml.safe_load((SKILLS_DIR / skill_name / "agents" / "openai.yaml").read_text())
        assert {"type": "mcp", "value": "tfmod-search"} in binding["dependencies"]["tools"]
        # user-invoked skills must not fire implicitly on Codex either
        expected_implicit = skill_name not in USER_INVOKED_SKILLS
        assert binding["policy"]["allow_implicit_invocation"] is expected_implicit

    def test_troubleshoot_skill_ships_prefilter_script(self):
        script = SKILLS_DIR / "tf-troubleshoot" / "scripts" / "extract_tf_errors.py"
        assert script.is_file()
        _, body = _parse_frontmatter(SKILLS_DIR / "tf-troubleshoot" / "SKILL.md")
        assert "extract_tf_errors.py" in body

    def test_trigger_descriptions_are_disjoint(self):
        """Each description must own its trigger vocabulary: the review/upgrade/
        error/scaffold keywords may appear in exactly one model-invoked skill."""
        descriptions = {
            name: _parse_frontmatter(SKILLS_DIR / name / "SKILL.md")[0]["description"].lower()
            for name in EXPECTED_SKILLS - USER_INVOKED_SKILLS
        }
        for keyword, owner in [
            ("reviewing", "tf-review"),
            ("pull request", "tf-review"),
            ("upgrade", "tf-module-upgrade"),
            ("fails", "tf-troubleshoot"),
        ]:
            holders = {name for name, d in descriptions.items() if keyword in d}
            assert holders == {owner}, f"trigger keyword '{keyword}' claimed by {holders}, expected only {owner}"


class TestAgents:
    AGENTS_DIR = PLUGIN_DIR / "agents"

    def test_expected_agents_present(self):
        agents = {p.stem for p in self.AGENTS_DIR.glob("*.md")}
        assert agents == EXPECTED_AGENTS

    @pytest.mark.parametrize("agent_name", sorted(EXPECTED_AGENTS))
    def test_agent_frontmatter(self, agent_name):
        frontmatter, body = _parse_frontmatter(self.AGENTS_DIR / f"{agent_name}.md")
        assert frontmatter["name"] == agent_name
        assert frontmatter["description"]
        assert body.strip(), "agent system prompt must not be empty"

    def test_claude_manifest_registers_agents(self):
        # the plugin.json schema requires individual agent file paths, not a directory
        manifest = _load_json(PLUGIN_DIR / ".claude-plugin" / "plugin.json")
        registered = {Path(p).stem for p in manifest["agents"]}
        assert registered == EXPECTED_AGENTS
        for p in manifest["agents"]:
            assert (PLUGIN_DIR / p).is_file()

    def test_skills_delegate_to_agents(self):
        _, troubleshoot = _parse_frontmatter(SKILLS_DIR / "tf-troubleshoot" / "SKILL.md")
        assert "tf-log-analyst" in troubleshoot
        _, review = _parse_frontmatter(SKILLS_DIR / "tf-review" / "SKILL.md")
        assert "tf-diff-reviewer" in review


class TestMaintainerSkills:
    MAINTAINER_SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"

    def test_present_with_valid_frontmatter(self):
        skills = {p.parent.name for p in self.MAINTAINER_SKILLS_DIR.glob("*/SKILL.md")}
        assert skills >= {"refresh-module-docs", "add-module"}
        for name in skills:
            frontmatter, body = _parse_frontmatter(self.MAINTAINER_SKILLS_DIR / name / "SKILL.md")
            assert frontmatter["name"] == name
            assert frontmatter["description"]
            assert body.strip()

    def test_not_gitignored(self):
        """.claude/ is ignored but .claude/skills/ must be committed for contributors."""
        proc = subprocess.run(
            ["git", "check-ignore", str(self.MAINTAINER_SKILLS_DIR / "add-module" / "SKILL.md")],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 1, "maintainer skills must not be gitignored"


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
        for skill in EXPECTED_SKILLS:
            assert skill in inventory, f"skill {skill} missing from inventory"

        # `plugin details` under-reports components declared via manifest paths
        # (shows "Agents (0)" like it shows "MCP servers (0)" for inline config,
        # which `claude mcp list` proves connected). Assert the real thing:
        # the agent files ship inside the installed plugin cache.
        cache = tmp_path / "claude-config" / "plugins" / "cache"
        installed_agents = {p.stem for p in cache.rglob("agents/*.md")}
        assert EXPECTED_AGENTS <= installed_agents, f"agents missing from install cache: {installed_agents}"
