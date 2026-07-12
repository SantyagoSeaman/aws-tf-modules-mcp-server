# Security & Quality Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a proportionate, GitHub-native security & quality layer (Dependabot, CodeQL, ruff security lint, workflow hardening, disclosure policy) to the public `tfmodsearch` PyPI package.

**Architecture:** Four tasks. Tasks 1–3 land committed files on `feature/security-baseline` (ruff `S` + code triage; Dependabot + SECURITY.md; workflow permissions + CHANGELOG). Task 4 flips GitHub repo-settings toggles via `gh api` — executed by the controller **outside** the PR, not committed.

**Tech Stack:** Python 3.13, ruff (flake8-bandit `S` rules), pytest, GitHub Actions, Dependabot, CodeQL, `gh` CLI.

## Global Constraints

- No new runtime dependencies — stdlib only for `src/` (ruff/pytest are already dev deps).
- The server stays offline except `src/tfmod_registry_docs.py` (the only networked module).
- Commit messages: plain, content-only — **no** Co-Authored-By / attribution trailers.
- Push only after explicit user approval; `gh api` settings changes (Task 4) run only with an explicit go-ahead.
- Every text file ends with a trailing newline.
- `CLAUDE.md` is gitignored — never `git add -f` it.
- No version bump / PyPI release — this is infra/hygiene. CHANGELOG entry goes under `[Unreleased]`.
- Repo coordinates: `SantyagoSeaman/tfmodsearch`; default branch `master`.
- Scope guard (YAGNI): no action SHA-pinning, no pip-audit/gitleaks, no SBOM, no Scorecard, no branch-protection.

---

### Task 1: Enable ruff `S` security lint + triage findings + harden the network path

**Files:**
- Modify: `pyproject.toml` (`[tool.ruff.lint] select`, add `[tool.ruff.lint.per-file-ignores]`)
- Modify: `src/tfmod_registry_docs.py:55` (S310 — add https scheme guard + noqa)
- Modify: `src/tfmod_search_lib.py:887` (S301 — noqa), `:768`, `:972` (S101 — noqa)
- Modify: `src/tfmod_mcp_server.py:468,864,927,1006` (S101 — noqa)
- Test: `tests/integration/test_registry_docs.py` (new scheme-guard test)

**Interfaces:**
- Consumes: `_http_fetch(namespace: str, name: str, provider: str, version: str | None) -> dict` and module global `REGISTRY_API_BASE` in `src/tfmod_registry_docs.py`.
- Produces: `_http_fetch` now raises `ValueError` when the assembled URL is not `https://` before any network call.

Verified current `S` findings (whole repo): 8 in `src/` (6× S101, 1× S301, 1× S310), 357 in `tests/` (341× S101, 11× S603, 5× S607). Nothing elsewhere.

- [ ] **Step 1: Write the failing scheme-guard test**

Add to `tests/integration/test_registry_docs.py`:

```python
def test_http_fetch_rejects_non_https(monkeypatch):
    """The one networked path must refuse any non-https URL before opening it."""
    import tfmod_registry_docs as rd

    monkeypatch.setattr(rd, "REGISTRY_API_BASE", "http://insecure.example/v1/modules")
    with pytest.raises(ValueError, match="non-https"):
        rd._http_fetch("terraform-aws-modules", "vpc", "aws", None)
```

Ensure `import pytest` is present at the top of the file (it is — the file already uses pytest).

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/integration/test_registry_docs.py::test_http_fetch_rejects_non_https -v`
Expected: FAIL — no `ValueError` raised (guard not yet added); the monkeypatched `http://` URL would proceed to `urlopen`.

- [ ] **Step 3: Add the https scheme guard in `_http_fetch`**

In `src/tfmod_registry_docs.py`, replace the fetch body (around lines 52–56):

```python
    url = f"{REGISTRY_API_BASE}/{namespace}/{name}/{provider}"
    if version is not None:
        url = f"{url}/{version}"
    if not url.startswith("https://"):
        raise ValueError(f"Refusing to fetch non-https URL: {url!r}")
    with urllib.request.urlopen(url, timeout=25) as resp:  # noqa: S310 - scheme guarded above
        return json.load(resp)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/integration/test_registry_docs.py::test_http_fetch_rejects_non_https -v`
Expected: PASS.

- [ ] **Step 5: Annotate the pickle load (S301)**

In `src/tfmod_search_lib.py` at the `pickle.load` call (line ~887), change:

```python
    with open(path, "rb") as f:
        index = pickle.load(f)  # noqa: S301 - index is our own locally-built, trusted artifact
```

- [ ] **Step 6: Annotate the six internal-invariant asserts (S101)**

These asserts narrow `Optional[Logger]` for mypy and guard programmer error only — they are not security checks. Append `  # noqa: S101` to each:

- `src/tfmod_mcp_server.py:468` → `assert self._logger is not None, "ServerState must have a logger"  # noqa: S101`
- `src/tfmod_mcp_server.py:864` → `assert state.logger is not None, "ServerState must have a logger"  # noqa: S101`
- `src/tfmod_mcp_server.py:927` → `assert state.logger is not None, "ServerState must have a logger"  # noqa: S101`
- `src/tfmod_mcp_server.py:1006` → `assert state.logger is not None, "ServerState must have a logger"  # noqa: S101`
- `src/tfmod_search_lib.py:768` → `assert logger is not None, "Logger must not be None"  # noqa: S101`
- `src/tfmod_search_lib.py:972` → `assert logger is not None, "Logger must not be None"  # noqa: S101`

(Verify each target line still reads `assert ... is not None` before editing — line numbers may shift by ±1 after Step 3/5.)

- [ ] **Step 7: Enable `S` in ruff and ignore it for tests**

In `pyproject.toml`, add `"S"` to `[tool.ruff.lint] select` (after `"UP"`):

```toml
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # Pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
    "S",  # flake8-bandit (security)
]
```

Add a new table (place it right after the `[tool.ruff.lint.isort]` block):

```toml
[tool.ruff.lint.per-file-ignores]
# Tests legitimately use assert (S101) and spawn the packaged server as a
# subprocess in e2e checks (S603/S607).
"tests/**" = ["S101", "S603", "S607"]
```

- [ ] **Step 8: Verify ruff is clean across the whole repo**

Run: `uv run ruff check --select S .`
Expected: `All checks passed!` (the 8 src findings are now noqa'd or guarded; the 357 test findings are per-file-ignored).

Then run the full linter to confirm nothing else broke:
Run: `uv run ruff check .`
Expected: `All checks passed!`

- [ ] **Step 9: Run the registry test module + a broad smoke**

Run: `uv run pytest tests/integration/test_registry_docs.py -v`
Expected: PASS (all, including the new test).

- [ ] **Step 10: Commit**

```bash
git add pyproject.toml src/tfmod_registry_docs.py src/tfmod_search_lib.py src/tfmod_mcp_server.py tests/integration/test_registry_docs.py
git commit -m "Enable ruff S security lint; harden registry fetch to https-only"
```

---

### Task 2: Dependabot config + SECURITY.md + config contract test

**Files:**
- Create: `.github/dependabot.yml`
- Create: `SECURITY.md`
- Create: `tests/integration/test_security_config.py`

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: `tests/integration/test_security_config.py` with helpers `_repo_root()` returning the git repo root `Path`; later extended in Task 3.

- [ ] **Step 1: Write the failing contract test**

Create `tests/integration/test_security_config.py`:

```python
"""Contract tests for the repo's security & quality configuration files."""

from pathlib import Path

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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/integration/test_security_config.py -v`
Expected: FAIL — `.github/dependabot.yml` and `SECURITY.md` do not exist yet.

- [ ] **Step 3: Create `.github/dependabot.yml`**

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"
    commit-message:
      prefix: "ci"
```

- [ ] **Step 4: Create `SECURITY.md`**

```markdown
# Security Policy

## Supported Versions

Only the latest published minor release receives security fixes.

| Version | Supported |
| ------- | --------- |
| 0.9.x   | ✅        |
| < 0.9   | ❌        |

## Reporting a Vulnerability

Please report suspected vulnerabilities privately — do **not** open a public issue.

- **Preferred:** use GitHub's [Private Vulnerability Reporting](https://github.com/SantyagoSeaman/tfmodsearch/security/advisories/new) ("Report a vulnerability" on the repository's Security tab).
- **Fallback:** email makeev.alex@gmail.com.

You can expect an acknowledgement within a few days. This is a volunteer-maintained
open-source project, so fixes are best-effort; we will keep you informed of progress
and coordinate disclosure once a fix is available.

## Scope

`tfmodsearch` runs locally and is offline by design, with one exception:
`src/tfmod_registry_docs.py` makes outbound HTTPS requests to the public
Terraform Registry API (`registry.terraform.io`) for the `grep_module_docs`
tool. Reports concerning that network path, the registry documentation cache,
or the `get_module` path-traversal guards are especially welcome.
```

- [ ] **Step 5: Run the contract test to verify it passes**

Run: `uv run pytest tests/integration/test_security_config.py -v`
Expected: PASS (both tests).

- [ ] **Step 6: Run pre-commit on the new files**

Run: `uv run pre-commit run --files .github/dependabot.yml SECURITY.md tests/integration/test_security_config.py`
Expected: all hooks Pass (check-yaml validates dependabot.yml; end-of-file-fixer confirms trailing newlines).

- [ ] **Step 7: Commit**

```bash
git add .github/dependabot.yml SECURITY.md tests/integration/test_security_config.py
git commit -m "Add Dependabot (github-actions) config, SECURITY.md, and config contract tests"
```

---

### Task 3: Workflow least-privilege permissions + CHANGELOG

**Files:**
- Modify: `.github/workflows/ci.yml` (add top-level `permissions`)
- Modify: `.github/workflows/publish.yml` (add top-level `permissions`, keep job-level `id-token: write`)
- Modify: `tests/integration/test_security_config.py` (extend with workflow-permissions test)
- Modify: `CHANGELOG.md` (add `[Unreleased]` section)

**Interfaces:**
- Consumes: `_repo_root()` from `tests/integration/test_security_config.py` (Task 2).
- Produces: nothing downstream.

- [ ] **Step 1: Write the failing workflow-permissions test**

Append to `tests/integration/test_security_config.py`:

```python
import pytest


@pytest.mark.parametrize("workflow", ["ci.yml", "publish.yml"])
def test_workflow_has_least_privilege_permissions(workflow):
    wf_path = _repo_root() / ".github" / "workflows" / workflow
    wf = yaml.safe_load(wf_path.read_text())
    assert wf["permissions"] == {"contents": "read"}, (
        f"{workflow} must declare top-level permissions: contents: read"
    )
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/integration/test_security_config.py::test_workflow_has_least_privilege_permissions -v`
Expected: FAIL — neither workflow declares top-level `permissions` yet (`KeyError`/assertion).

- [ ] **Step 3: Add `permissions` to `ci.yml`**

In `.github/workflows/ci.yml`, insert after the `on:` block and before `jobs:`:

```yaml
permissions:
  contents: read
```

- [ ] **Step 4: Add `permissions` to `publish.yml`**

In `.github/workflows/publish.yml`, insert after the `on:` block and before `jobs:`:

```yaml
permissions:
  contents: read
```

Leave the existing job-level `permissions: id-token: write` on the `publish` job untouched — job-level permissions override the top-level default, so OIDC Trusted Publishing keeps working.

- [ ] **Step 5: Run the test to verify it passes**

Run: `uv run pytest tests/integration/test_security_config.py -v`
Expected: PASS (all four tests: dependabot, security policy, ci.yml perms, publish.yml perms).

Note on YAML `on:`: PyYAML parses the bare key `on` as the boolean `True`, so in the loaded dict the trigger block is keyed `True`, not `"on"`. The tests here only read `wf["permissions"]`, which is unaffected. Do not add an assertion on `wf["on"]`.

- [ ] **Step 6: Add the `[Unreleased]` CHANGELOG section**

In `CHANGELOG.md`, insert immediately after the `# Changelog` header line and before `## [0.9.0] - 2026-07-12`:

```markdown

## [Unreleased]

### Security

- **Dependabot**: weekly version-updates for GitHub Actions plus repo-level security-updates for Python dependencies (auto-PRs on known vulnerabilities).
- **CodeQL default setup**: GitHub-managed SAST over the Python code on pull requests and a weekly schedule.
- **ruff `S` (flake8-bandit)** security lint enforced in CI; the single networked path (`tfmod_registry_docs.py`) now refuses any non-`https` URL before opening it.
- **Least-privilege `GITHUB_TOKEN`**: both workflows declare top-level `permissions: contents: read` (publish keeps job-scoped `id-token: write` for OIDC).
- **`SECURITY.md`** disclosure policy with GitHub Private Vulnerability Reporting enabled.
```

- [ ] **Step 7: Run pre-commit on the changed files**

Run: `uv run pre-commit run --files .github/workflows/ci.yml .github/workflows/publish.yml CHANGELOG.md tests/integration/test_security_config.py`
Expected: all hooks Pass.

- [ ] **Step 8: Full suite green**

Run: `uv run pytest tests/ -q`
Expected: PASS (existing suite + the new contract tests; 6 opt-in live tests skip).

- [ ] **Step 9: Commit**

```bash
git add .github/workflows/ci.yml .github/workflows/publish.yml CHANGELOG.md tests/integration/test_security_config.py
git commit -m "Harden workflow token permissions; document security baseline in CHANGELOG"
```

---

### Task 4: Enable GitHub repo-settings toggles via `gh api` (controller-only, outside the PR)

**Not a code task and not a commit.** The controller runs these after Tasks 1–3, with the user's explicit go-ahead (they change live repo settings). A subagent must not run these.

**Files:** none.

- [ ] **Step 1: Enable Dependabot alerts (prerequisite)**

Run: `gh api -X PUT repos/SantyagoSeaman/tfmodsearch/vulnerability-alerts`
Expected: HTTP 204 (no output).

- [ ] **Step 2: Enable Dependabot security updates**

Run: `gh api -X PUT repos/SantyagoSeaman/tfmodsearch/automated-security-fixes`
Expected: HTTP 204 (no output).

- [ ] **Step 3: Enable CodeQL default setup**

Run: `gh api -X PATCH repos/SantyagoSeaman/tfmodsearch/code-scanning/default-setup -f state=configured -f query_suite=default`
Expected: JSON acknowledging the run was queued (`"run_id"`/`"run_url"` present).

- [ ] **Step 4: Enable Private Vulnerability Reporting**

Run: `gh api -X PUT repos/SantyagoSeaman/tfmodsearch/private-vulnerability-reporting`
Expected: HTTP 204 (no output).

- [ ] **Step 5: Verify settings**

Run:
```bash
gh api repos/SantyagoSeaman/tfmodsearch --jq '.security_and_analysis'
gh api repos/SantyagoSeaman/tfmodsearch/code-scanning/default-setup --jq '.state'
```
Expected: `dependabot_security_updates.status == "enabled"`; default-setup `state == "configured"`. (Secret scanning + push protection remain `enabled` from before.)

---

## Self-Review

**1. Spec coverage:**
- Dependabot (Actions version-updates) → Task 2; alerts + security-updates → Task 4. ✅
- SECURITY.md + private vuln reporting → Task 2 (file) + Task 4 (toggle). ✅
- ruff `S` + per-file-ignores + S310 guard + S301/S101 noqa → Task 1. ✅
- CodeQL default setup → Task 4. ✅
- Workflow `permissions` hardening → Task 3. ✅
- Contract test → Task 2 (+ extended Task 3). ✅
- CHANGELOG `[Unreleased]` → Task 3. ✅
- Delivery via branch/PR, no release → whole plan; CI green in Task 3 Step 8. ✅

**2. Placeholder scan:** No TBD/TODO; every code step shows exact content. ✅

**3. Type consistency:** `_http_fetch` signature and `REGISTRY_API_BASE` name match the actual source; `_repo_root()` defined in Task 2 and reused in Task 3. ✅
