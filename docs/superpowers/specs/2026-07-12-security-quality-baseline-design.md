# Security & Quality Baseline — Design

**Date:** 2026-07-12
**Status:** Approved (design), pending implementation plan
**Branch:** `feature/security-baseline`

## Goal

Add a proportionate, GitHub-native security & quality layer to `tfmodsearch` — a
public MIT-licensed PyPI package that AI agents install via `uvx` into their own
environments. The supply-chain integrity of the package matters; its runtime
attack surface is small (offline except one module, no secrets/auth/user data).
So: maximize free native controls, minimize ongoing maintenance. No third-party
SAST vendors, no SBOM pipeline, no action SHA-pinning (all deferred).

## Context — current posture (verified 2026-07-12)

Already in place:
- **CI** (`.github/workflows/ci.yml`): `lint` (pre-commit → ruff + ruff-format +
  mypy + hygiene hooks) and `test` (full pytest suite) on every PR and push to
  `master`.
- **Publish** (`.github/workflows/publish.yml`): OIDC Trusted Publishing to PyPI
  + PEP 740 attestations. Already the supply-chain best practice.
- **Secret scanning + push protection: ENABLED** on the repo (`gh api` confirmed).

Gaps this design closes:
- No Dependabot (no `.github/dependabot.yml`; `automated-security-fixes` disabled).
- No CodeQL / SAST over the Python code.
- ruff `S` (flake8-bandit) rules not in `select`.
- No least-privilege `permissions:` on workflows (default `GITHUB_TOKEN` scope).
- No `SECURITY.md` disclosure policy; private vulnerability reporting off.

## Decisions (from brainstorming)

1. **Scope:** proportionate GitHub-native baseline (not minimal, not maximal).
2. **Dependabot:** version-updates for **GitHub Actions only** + repo-level
   **security-updates** for pip deps. No routine pip version bumps.
3. **CodeQL:** **default setup** (GitHub-managed, no in-repo workflow file).

## Components

### A. Files committed to the repo (delivered in the PR)

**A1. `.github/dependabot.yml`** — GitHub Actions version-updates only:

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

No `pip` block by decision — pip security PRs come from the repo-level
`automated-security-fixes` toggle (Section B), which needs no version-update
config to fire.

**A2. `SECURITY.md`** — short disclosure policy:
- Supported versions: `0.9.x` (latest minor).
- Reporting channel: GitHub **Private Vulnerability Reporting** (the "Report a
  vulnerability" button) as primary, maintainer email as fallback.
- Response expectations: acknowledge within a few days; best-effort for a
  volunteer OSS project.
- Scope note: the MCP server; explicitly calls out `tfmod_registry_docs.py` as
  the only module that performs network I/O.

**A3. `pyproject.toml` — enable ruff `S` (flake8-bandit)** in `[tool.ruff.lint]
select`. Existing findings (verified counts) and their handling:

| Rule | Count | Location | Handling |
|---|---|---|---|
| `S101` assert | 341 | `tests/**` | `per-file-ignores` for tests |
| `S603` subprocess-no-shell | 11 | `tests/**` (e2e spawn) | `per-file-ignores` for tests |
| `S607` partial-path process | 5 | `tests/**` (e2e spawn) | `per-file-ignores` for tests |
| `S101` assert | 6 | `src/` | review each: user-facing validation → explicit `raise`; internal invariants → scoped ignore |
| `S301` pickle load | 1 | `tfmod_search_lib.py` (index loader) | targeted `# noqa: S301` + justification comment (index is built locally, trusted) |
| `S310` urlopen | 1 | `tfmod_registry_docs.py` | **add explicit `https://` scheme guard before the request** (real hardening of the one networked path), then `# noqa: S310` |

`per-file-ignores` added under `[tool.ruff.lint.per-file-ignores]`:
```toml
"tests/**" = ["S101", "S603", "S607"]
```

The S310 handling is a genuine security improvement, not a suppression: the
scheme check prevents `file://` / `ftp://` fetches should a registry coordinate
ever influence the URL. This is the "security проверка кода" the user asked about.

**A4. Workflow hardening — top-level least-privilege `permissions:`** on both
workflows:
- `ci.yml`: add `permissions:\n  contents: read` at top level.
- `publish.yml`: add `permissions:\n  contents: read` at top level; keep the
  existing job-level `id-token: write` on the `publish` job (job-level overrides
  top-level, so OIDC still works).

No SHA-pinning of actions (deferred to the "maximal" tier).

### B. Repo settings via `gh api` (executed after approval — NOT in the PR)

Idempotent, run with explicit go-ahead:
- `PUT /repos/SantyagoSeaman/tfmodsearch/vulnerability-alerts` — Dependabot alerts (prereq).
- `PUT /repos/SantyagoSeaman/tfmodsearch/automated-security-fixes` — Dependabot security updates (currently disabled).
- `PATCH /repos/SantyagoSeaman/tfmodsearch/code-scanning/default-setup` with `state=configured`, `query_suite=default` — CodeQL default setup.
- `PUT /repos/SantyagoSeaman/tfmodsearch/private-vulnerability-reporting` — makes the SECURITY.md reporting button functional.
- Secret scanning + push protection — already enabled; no action.

### C. Tests & verification

- ruff `S` passes after ignores → enforced automatically by the existing
  pre-commit + CI `lint` job (no new CI job needed).
- Small contract test (in the style of the repo's manifest/contract tests):
  - `.github/dependabot.yml` parses and includes the `github-actions` ecosystem.
  - `SECURITY.md` exists and mentions a reporting channel.
- Full `pytest` suite + `pre-commit run --all-files` green.

### D. Delivery

- Branch `feature/security-baseline` → PR → green CI → merge.
- **No version bump / PyPI release** — this is infra/hygiene, not a package
  change. Add a `CHANGELOG.md` entry under `[Unreleased]`.

## Explicitly out of scope (YAGNI here)

Action SHA-pinning, `pip-audit`/`gitleaks` CI steps (CodeQL + secret scanning
already cover this ground), SBOM generation, OpenSSF Scorecard badge, branch
protection rules. All parked in the "maximal" tier for a later decision.

## Success criteria

- Dependabot alerts + security-updates active; a weekly Actions version-update
  channel configured.
- CodeQL default setup running on PRs and on schedule.
- ruff `S` enforced in CI with all existing findings triaged (suppressed with
  justification or fixed), and the S310 path hardened with a scheme guard.
- Both workflows run with least-privilege `GITHUB_TOKEN`.
- `SECURITY.md` present and its reporting button live.
- Full suite green; no PyPI release required.
