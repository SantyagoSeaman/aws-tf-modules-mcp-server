# Design: Integrate grep_module_docs into the plugin skills

**Date:** 2026-07-12
**Status:** Approved
**Prereq:** `grep_module_docs` MCP tool (shipped in 0.8.0, spec: `2026-07-12-grep-module-docs-design.md`)

## Problem

0.8.0 shipped `grep_module_docs` — exact, version-pinnable quotes from the live
Terraform Registry documentation of **any** module — but none of the plugin's
seven skills or two subagents mention it. Agents driven by those skills still
follow pre-0.8.0 guidance, which has three now-obsolete weak spots:

1. **The "registry link" cop-out.** `tf-review`, `tf-module-upgrade`,
   `tf-migrate`, `tf-diff-reviewer`, and `tf-log-analyst` all treat a variable
   absent from the curated doc as "*suspicious, not proven dead* — confirm via
   the registry link in the doc". An agent cannot click a link mid-review; in
   practice findings stay "unconfirmed". `grep_module_docs` confirms or refutes
   in one call, at the exact pinned version.
2. **The non-catalog surrender.** `aws-terraform-modules` instructs: modules
   outside the terraform-aws-modules namespace "are not indexed — say so rather
   than guessing their APIs". The tool greps any registry module's live docs;
   surrendering is no longer necessary.
3. **The version blind spot.** All skills verify against the curated doc, which
   documents the *latest* version at catalog-refresh time. Projects pin older
   majors; upgrade audits and troubleshooting need "what did this variable look
   like at the pinned version" — exactly what `version=` provides.

## Goals

- Every model-invoked skill and both agents teach **when to escalate** from the
  compact curated doc to an exact live quote, with the same mental model.
- A user-invoked `/tf-grep` skill gives users a direct "give me the exact quote"
  command, including for non-AWS modules.
- Contract tests keep the guidance from regressing.

## Non-goals

- No new model-invoked skill (trigger-disjointness risk vs `aws-terraform-modules`;
  the non-catalog scenario is handled inside existing skills).
- No skill restructuring — surgical edits into existing workflow steps only.
- No MCP server / code changes; this is a docs-and-skills release.
- No changes to the curated corpus or index.

## Section 1 — The shared mental model

Each skill embeds (adapted to its workflow, not copy-pasted verbatim) the
three-tier access model:

- **`search_modules` / `modules_list`** — find the module; results carry
  `module_id` (registry coordinate `namespace/name/provider`) and `latest_version`.
- **`get_module`** — the curated compact doc: offline, 54 AWS modules, current
  as of the catalog refresh. This is the **overview** — start here.
- **`grep_module_docs`** — exact quotes from the **live** registry docs of any
  module, optionally version-pinned. This is the **proof** — escalate here.

Canonical escalation triggers (each skill keeps only the ones its workflow hits):

| # | Trigger | Action |
|---|---------|--------|
| E1 | A variable/attribute is absent from the curated doc | Grep its name before claiming it is dead/missing/renamed. Replaces every "confirm via the registry link" step. |
| E2 | The project pins an older version | Grep at **that** version (`version="x.y.z"`), not latest. For upgrades: grep both pinned and latest to diff behavior. |
| E3 | The module is outside the curated catalog (cloudposse, any namespace) | Grep is the only source. Derive `module_id` from the block's `source` argument (strip `//submodule` suffix and any `?ref=`). |
| E4 | A claim rests on an exact default/type/description | Quote the line (`scope=["inputs"]` / `scope=["outputs"]`) instead of paraphrasing from memory. |

Practical notes taught alongside: the pattern is a regex (escape literal dots);
matching is case-insensitive by default; a zero-match response lists
`available_sections` for a retry; `refresh=True` bypasses a suspected-stale
cache; `module_id` comes from search results or the doc's `Module ID` header.

## Section 2 — New skill: `/tf-grep`

**File:** `plugins/tfmod-search/skills/tf-grep/SKILL.md`
**Frontmatter:** `disable-model-invocation: true` (user-invoked, like
`tf-module`/`tf-stack` — exempt from trigger-disjointness).

**Invocation examples:**
- `/tf-grep vpc enable_nat_gateway`
- `/tf-grep eks 20.8.4 bootstrap_self_managed_addons` (pinned version)
- `/tf-grep cloudposse/label/null context` (non-catalog module)

**Workflow the skill teaches:**
1. Resolve the module argument to a `module_id`: if it already looks like
   `namespace/name/provider`, use it directly; otherwise `search_modules` and
   take the top hit's `module_id`.
2. Detect an optional version among the arguments (semver-looking token);
   pass it as `version`.
3. Treat the rest as the search intent; build a regex (variable name as-is;
   escape regex metacharacters in literal lookups); call `grep_module_docs`.
4. Reply with the exact matched lines — section label, line number, context —
   plus resolved version and source URL. Zero matches → show
   `available_sections`, suggest a broader pattern or a different `scope`,
   retry once with an obvious broadening before asking the user.

**Codex binding:** `plugins/tfmod-search/skills/tf-grep/agents/openai.yaml`,
identical to `tf-stack`'s: `policy.allow_implicit_invocation: false` plus the
`tfmod-search` MCP tool dependency (the e2e test asserts exactly this for
user-invoked skills).

## Section 3 — Surgical edits to existing skills and agents

Per file — the step being changed and the change. Exact wording lands in the
implementation plan; the spec fixes intent and placement.

### `aws-terraform-modules/SKILL.md`
- **Step 5 (Verify):** add — when unsure a variable exists (or the project pins
  an older major), confirm with `grep_module_docs` (E1/E2) instead of shipping
  uncertainty.
- **Notes, non-catalog bullet:** replace "say so rather than guessing" with:
  not searchable, but fully greppable — derive `module_id` from the `source`
  and use `grep_module_docs` (E3); state that the compact catalog does not
  cover it, then verify against live docs.

### `tf-module-upgrade/SKILL.md`
- **Step 2 (Ground truth):** add — for blocks pinned to an older version, grep
  the pinned version to establish what the code *currently* relies on, and the
  latest to see what changes (E2).
- **Step 3 (Dead variables):** replace "confirm via the registry link in the
  doc" with `grep_module_docs` confirmation: grep the variable at latest
  (present ⇒ not dead) and at the pinned version (present there but not at
  latest ⇒ removed/renamed — report with the quote) (E1+E2).
- **Step 1 (Inventory) note:** blocks from other namespaces are no longer
  skipped silently — they can be audited via grep (E3), marked as
  "live-doc-verified" rather than "curated-doc-verified".

### `tf-review/SKILL.md`
- **Step 2 (inline path):** replace the "absence in the curated doc =
  suspicious, confirm via the doc's registry link" clause with grep
  verification at the version the diff pins (E1/E2). Non-catalog module blocks
  in the diff: verify via grep instead of skipping (E3).

### `tf-migrate/SKILL.md`
- **Step 4 (Coverage check):** replace "If an input's existence is uncertain
  (docs are curated summaries), say so and point to the registry link" with:
  grep each uncertain input by name; quote the match in the mapping table, or
  move it to "not covered" on a confirmed miss (E1/E4).

### `tf-troubleshoot/SKILL.md`
- **Step 3 (Analyze):** add the escalation ladder — failing variable absent
  from the curated doc → grep it (E1); log shows an older pinned version →
  grep at that version (E2); module not in the catalog → grep its live docs
  and mark the diagnosis verified instead of "reasoning from the error text
  alone" (E3).

### `tf-stack/SKILL.md`
- **Step 3 (wiring):** add — when unsure of an exact output name, grep with
  `scope=["outputs"]` rather than guessing (E4). Components without a
  catalog module (non-AWS or third-party) may still be wired from live docs
  via grep (E3).

### `tf-module/SKILL.md`
- **New step:** when the request targets a specific variable/default rather
  than a whole module ("what's the default of X in vpc?"), answer with a
  `grep_module_docs` quote instead of the full doc (E4); mention `/tf-grep`
  as the direct route.

### `agents/tf-diff-reviewer.md`
- **Step 3 (Verify):** same replacement as tf-review — grep at the pinned
  version instead of "the doc links to the registry for the exhaustive list";
  non-catalog blocks verified via grep, findings marked live-doc-verified.

### `agents/tf-log-analyst.md`
- **Step 3 (Verify):** replace "if the module is not in the tfmod-search
  catalog, say so explicitly and reason from the error text alone" with grep
  verification of the failing variable (any namespace, at the version from the
  log when present). **Confidence scale** gains `verified-against-live-doc`
  between `verified-against-doc` and `inferred-from-error`.

## Section 4 — Tests

In `tests/e2e/test_plugin_e2e.py`:

- `EXPECTED_SKILLS` += `"tf-grep"`; `USER_INVOKED_SKILLS` += `"tf-grep"`.
  `CODEX_BOUND_SKILLS` derives automatically; existing parametrized tests then
  cover tf-grep's frontmatter, `$ARGUMENTS` presence, and Codex binding.
- **New contract test:** every model-invoked skill and both agent files mention
  `grep_module_docs` — pinning the integration this design adds so future skill
  edits cannot silently drop it.
- Trigger-disjointness: unaffected (new skill is user-invoked); the existing
  test still passes unchanged.
- Live-install e2e (`claude plugin` into isolated config) picks up the eighth
  skill via the existing glob-driven assertions where applicable.

## Section 5 — Docs & release

- README: skills table gains `/tf-grep`; the skills section's counts move from
  "seven skills" to "eight skills" everywhere they appear (README, CLAUDE.md —
  local only, plugin descriptions if they state a count).
- CHANGELOG: entry targets **0.9.0** (precedent: 0.5.0 was also a skills-only
  minor — a new skill is new functionality, not a patch). Version bump touches
  all three files (`pyproject.toml` + both plugin manifests) per the 0.8.0
  release gotcha; the bump itself happens at release time, not in this PR.
- Work lands on branch `feature/grep-skills-integration` → PR; release/tag is a
  separate, explicitly-approved step.

## Constraints

- Model-invoked skill descriptions must keep trigger keywords disjoint (e2e-enforced).
- Skills are portable (Claude Code + Codex): no Claude-specific tool names in
  shared SKILL.md bodies beyond the MCP tool names themselves.
- Commit messages: plain content-only, no attribution trailers.
- `CLAUDE.md` is gitignored — update locally, never force-add.
