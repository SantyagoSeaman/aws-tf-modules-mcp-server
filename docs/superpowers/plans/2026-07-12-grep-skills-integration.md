# grep_module_docs Skills Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Teach the plugin's skills and subagents when and how to escalate from the compact curated `get_module` doc to an exact, version-pinnable `grep_module_docs` quote, and add a user-invoked `/tf-grep` command for direct quote lookups.

**Architecture:** Docs-and-skills change only — no Python/MCP-server code changes. One new skill directory (`tf-grep`) with a Codex binding, surgical text edits into the existing 7 skills and 2 agents, e2e contract-test updates in `tests/e2e/test_plugin_e2e.py`, and a README skills-table update. Each edit replaces a specific pre-0.8.0 "confirm via the registry link" / "not indexed, say so" clause with concrete grep guidance.

**Tech Stack:** Markdown SKILL.md files with YAML front-matter, `agents/openai.yaml` Codex bindings, pytest e2e contract tests.

## Global Constraints

- Model-invoked skill descriptions must keep trigger keywords disjoint — the keywords `reviewing`, `pull request`, `upgrade`, `fails` may each appear in exactly one model-invoked skill's description (enforced by `test_trigger_descriptions_are_disjoint`). `tf-grep` is **user-invoked**, so it is exempt, but its description must not introduce any of those four keywords.
- `tf-grep` front-matter must set `disable-model-invocation: true` and its body must contain the literal token `$ARGUMENTS` (enforced by `test_user_invoked_skills_take_arguments`).
- `tf-grep` must ship `agents/openai.yaml` with `policy.allow_implicit_invocation: false` and the `{type: mcp, value: tfmod-search}` dependency (enforced by `test_codex_skill_binding_declares_mcp_dependency`).
- Skills are portable across Claude Code and Codex: no Claude-only tool names in shared SKILL.md bodies beyond the MCP tool names themselves (`search_modules`, `get_module`, `modules_list`, `grep_module_docs`).
- Commit messages: plain content-only, no `Co-Authored-By`/attribution trailers.
- `CLAUDE.md` is gitignored — update it locally if desired, but never `git add -f` it.
- Branch `feature/grep-skills-integration` already exists and the spec is already committed on it (`0a5bf49`). Do not create a new branch.
- No version bump and no CHANGELOG entry in this plan — those happen at the separate, explicitly-approved release step.

---

### Task 1: New `/tf-grep` skill + Codex binding + e2e set membership

**Files:**
- Create: `plugins/tfmod-search/skills/tf-grep/SKILL.md`
- Create: `plugins/tfmod-search/skills/tf-grep/agents/openai.yaml`
- Modify: `tests/e2e/test_plugin_e2e.py:85-95` (add `tf-grep` to `EXPECTED_SKILLS` and `USER_INVOKED_SKILLS`)
- Test: `tests/e2e/test_plugin_e2e.py::TestSkills`

**Interfaces:**
- Produces: an eighth skill `tf-grep`, user-invoked, that later tasks and the README reference. No code symbols.

- [ ] **Step 1: Update the e2e skill sets (the failing test)**

In `tests/e2e/test_plugin_e2e.py`, change the two set literals. Replace:

```python
EXPECTED_SKILLS = {
    "aws-terraform-modules",
    "tf-module",
    "tf-migrate",
    "tf-module-upgrade",
    "tf-review",
    "tf-stack",
    "tf-troubleshoot",
}
# user-invoked only; everything else may be model-invoked
USER_INVOKED_SKILLS = {"tf-module", "tf-stack"}
```

with:

```python
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
```

- [ ] **Step 2: Run the skill tests to verify they fail**

Run: `.venv/bin/pytest tests/e2e/test_plugin_e2e.py::TestSkills -q`
Expected: FAIL — `test_expected_skills_present` fails (the `tf-grep` directory does not exist yet), and the parametrized `tf-grep` cases error on the missing `SKILL.md`.

- [ ] **Step 3: Create the `tf-grep` SKILL.md**

Create `plugins/tfmod-search/skills/tf-grep/SKILL.md` with exactly:

````markdown
---
name: tf-grep
description: Grep the full, live documentation of any Terraform Registry module for an exact quote — a variable's real default, a submodule input, an output name — optionally at a pinned version. Invoke with a module and a pattern, e.g. "vpc enable_nat_gateway" or "cloudposse/label/null context".
disable-model-invocation: true
---

# Grep live Terraform module documentation

Pull an exact quote from a module's current registry documentation for:
$ARGUMENTS

`get_module` gives a compact curated overview of the 54 AWS catalog modules;
this skill is for the *exact line* — the real default, the precise type, an
output name, a submodule input — from the **live** registry docs of **any**
module, including non-AWS ones and specific older versions.

## Workflow

1. **Resolve the module to a `module_id`** (`namespace/name/provider`):
   - If an argument already looks like `namespace/name/provider` (two slashes,
     e.g. `cloudposse/label/null`), use it directly.
   - Otherwise treat the first argument as a module name and call
     `search_modules`; take the top hit's `module_id`.
2. **Detect an optional version.** If an argument looks like a semver
   (`6.6.1`, `20.8.4`), pass it as `version`; otherwise omit it and the latest
   is used.
3. **Build the pattern and grep.** The remaining argument(s) are the search
   intent. For a literal variable/output name, use it as-is (escape regex
   metacharacters such as `.` if the name contains them). Call
   `grep_module_docs` with `module_id`, `pattern`, and `version` when given.
   Narrow with `scope="root/inputs"` / `"root/outputs"` when the intent is
   clearly a variable or an output.
4. **Reply with the exact matches** — each with its section label, line number,
   and surrounding context — plus the resolved version and source URL. Do not
   paraphrase; the quote is the deliverable.
5. **Zero matches:** show the `available_sections` the tool returned, broaden
   the pattern once (drop `scope`, loosen the regex) and retry; if it is still
   empty, report that and point at the closest sections to look in.

## Notes

- The pattern is a regex, case-insensitive by default.
- For a module pinned to an older major in a project, pass that version so the
  quote reflects what the code actually targets — the latest docs may have
  moved on.
- `module_id` also appears in every `search_modules` / `modules_list` result
  and in each curated doc's `Module ID` header, so you rarely have to guess it.
- `refresh=true` bypasses the disk cache when you suspect a stale `latest`.
````

- [ ] **Step 4: Create the Codex binding**

Create `plugins/tfmod-search/skills/tf-grep/agents/openai.yaml` with exactly:

```yaml
policy:
  allow_implicit_invocation: false
dependencies:
  tools:
    - type: "mcp"
      value: "tfmod-search"
```

- [ ] **Step 5: Run the skill tests to verify they pass**

Run: `.venv/bin/pytest tests/e2e/test_plugin_e2e.py::TestSkills -q`
Expected: PASS — `test_expected_skills_present` now sees all eight, and the parametrized `tf-grep` cases (`test_skill_frontmatter`, `test_user_invoked_skills_take_arguments`, `test_model_invoked_skills_do_not_disable_invocation` skips it as user-invoked, `test_codex_skill_binding_declares_mcp_dependency`) pass. `test_trigger_descriptions_are_disjoint` still passes (tf-grep is user-invoked, excluded).

- [ ] **Step 6: Commit**

```bash
git add plugins/tfmod-search/skills/tf-grep/ tests/e2e/test_plugin_e2e.py
git commit -m "Add user-invoked /tf-grep skill for exact live-doc quotes"
```

---

### Task 2: Weave grep escalation into the authoring and lookup skills

**Files:**
- Modify: `plugins/tfmod-search/skills/aws-terraform-modules/SKILL.md` (Step 5 "Verify" + the non-catalog Notes bullet)
- Modify: `plugins/tfmod-search/skills/tf-module/SKILL.md` (add a variable-specific step)

**Interfaces:**
- Consumes: the shared mental model from the spec (E1–E4). No code symbols.
- Produces: `grep_module_docs` mentioned in both files (the contract test in Task 6 asserts it for `aws-terraform-modules`; `tf-module` is user-invoked and not asserted, but the mention is intended).

- [ ] **Step 1: Edit `aws-terraform-modules` Step 5 (Verify)**

In `plugins/tfmod-search/skills/aws-terraform-modules/SKILL.md`, replace:

```
5. **Verify.** After writing, cross-check every variable used against the
   documentation. Run `terraform validate` and `terraform fmt` when available.
```

with:

```
5. **Verify.** After writing, cross-check every variable used against the
   documentation. When you are unsure a variable exists, or the project pins an
   older major than the doc describes, confirm it with `grep_module_docs` — an
   exact quote from the live registry docs at that version — instead of
   shipping the uncertainty. Run `terraform validate` and `terraform fmt` when
   available.
```

- [ ] **Step 2: Edit the `aws-terraform-modules` non-catalog Notes bullet**

In the same file, replace:

```
- The corpus covers the terraform-aws-modules organization only. Modules from
  other namespaces (cloudposse, project-specific) are not indexed — say so
  rather than guessing their APIs.
```

with:

```
- The curated corpus covers the terraform-aws-modules organization only, so
  `search_modules`/`get_module` will not find other namespaces (cloudposse,
  project-specific). You are not stuck: `grep_module_docs` greps the live
  registry docs of *any* module — derive its `module_id` from the block's
  `source` and grep the variable you need. Say the module is outside the
  curated catalog, then verify against its live docs rather than guessing.
```

- [ ] **Step 3: Add a variable-specific step to `tf-module`**

In `plugins/tfmod-search/skills/tf-module/SKILL.md`, replace:

```
4. If the query is ambiguous or nothing fits well, do not guess — show the
   top-3 candidates with one-line descriptions and ask which to expand.
```

with:

```
4. If the query is ambiguous or nothing fits well, do not guess — show the
   top-3 candidates with one-line descriptions and ask which to expand.
5. If the request is really about one specific variable, default, or output
   ("what's the default of `X` in vpc?") rather than a whole module, skip the
   full doc and answer with an exact `grep_module_docs` quote — that is what
   the `/tf-grep` command is for, and you can call the same tool here.
```

- [ ] **Step 4: Verify both files now reference the tool**

Run: `grep -l grep_module_docs plugins/tfmod-search/skills/aws-terraform-modules/SKILL.md plugins/tfmod-search/skills/tf-module/SKILL.md`
Expected: both file paths printed.

Run: `.venv/bin/pytest tests/e2e/test_plugin_e2e.py::TestSkills -q`
Expected: PASS (no regressions; `test_flagship_skill_references_all_tools` still passes — the three original tools are untouched).

- [ ] **Step 5: Commit**

```bash
git add plugins/tfmod-search/skills/aws-terraform-modules/SKILL.md plugins/tfmod-search/skills/tf-module/SKILL.md
git commit -m "Weave grep_module_docs escalation into authoring and lookup skills"
```

---

### Task 3: Replace the "registry link" cop-out in the review/upgrade/migrate skills

**Files:**
- Modify: `plugins/tfmod-search/skills/tf-module-upgrade/SKILL.md` (Steps 1, 2, 3)
- Modify: `plugins/tfmod-search/skills/tf-review/SKILL.md` (Step 2)
- Modify: `plugins/tfmod-search/skills/tf-migrate/SKILL.md` (Step 4)

**Interfaces:**
- Produces: `grep_module_docs` mentioned in all three files (Task 6's contract test asserts it for each).

- [ ] **Step 1: Edit `tf-module-upgrade` Step 1 (Inventory)**

In `plugins/tfmod-search/skills/tf-module-upgrade/SKILL.md`, replace:

```
1. **Inventory.** Scan `*.tf` files for `module` blocks whose `source` is
   `terraform-aws-modules/...`. For each block record: file:line, source,
   pinned `version` (or its absence), and every variable set.
```

with:

```
1. **Inventory.** Scan `*.tf` files for `module` blocks whose `source` is
   `terraform-aws-modules/...`. For each block record: file:line, source,
   pinned `version` (or its absence), and every variable set. Blocks from other
   namespaces (cloudposse, project-specific) are not in the curated catalog but
   can still be audited via `grep_module_docs` against their live docs — include
   them, marked as live-doc-verified rather than curated-doc-verified.
```

- [ ] **Step 2: Edit `tf-module-upgrade` Step 2 (Ground truth)**

In the same file, replace:

```
2. **Ground truth.** For each distinct module: `get_module` → current version
   and input schema. One call per module, reused across blocks. Passing
   `sections=["inputs", "outputs"]` keeps responses small — version pins and
   gotchas are always included.
```

with:

```
2. **Ground truth.** For each distinct module: `get_module` → current version
   and input schema. One call per module, reused across blocks. Passing
   `sections=["inputs", "outputs"]` keeps responses small — version pins and
   gotchas are always included. When a block pins an older version than the
   doc, `grep_module_docs` at the pinned `version` shows what the code
   currently relies on and at the latest shows what changed — that diff is the
   audit.
```

- [ ] **Step 3: Edit `tf-module-upgrade` Step 3 (Dead variables)**

In the same file, replace:

```
   - **Dead variables** — variables set that do not appear in the current
     doc. Treat as *suspicious, not proven dead*: the docs are curated
     summaries; confirm via the registry link in the doc before reporting as
     removed, and mark unconfirmed cases as such.
```

with:

```
   - **Dead variables** — variables set that do not appear in the current
     doc. The curated doc is a summary, so absence there is *suspicious, not
     proven*. Confirm with `grep_module_docs`: grep the variable at the latest
     version (a hit ⇒ not dead, just unsummarized) and at the pinned version
     (a hit there but not at latest ⇒ genuinely removed or renamed — report it
     with the quoted line). Mark a finding unconfirmed only if the grep itself
     is inconclusive.
```

- [ ] **Step 4: Edit `tf-review` Step 2 (inline verification)**

In `plugins/tfmod-search/skills/tf-review/SKILL.md`, replace:

```
   inline: read only the `.tf` hunks, then for each touched
   terraform-aws-modules block check against the current doc:
   - every variable set exists in the current inputs (absence in the curated
     doc = *suspicious*, confirm via the doc's registry link before calling
     it dead)
   - required inputs present, `version` pinned and not a major behind
   - deprecated arguments per the doc's notes
```

with:

```
   inline: read only the `.tf` hunks, then for each touched
   terraform-aws-modules block check against the current doc:
   - every variable set exists in the current inputs (absence in the curated
     doc = *suspicious*; confirm with `grep_module_docs` at the version the
     block pins before calling it dead)
   - required inputs present, `version` pinned and not a major behind
   - deprecated arguments per the doc's notes
   Blocks whose `source` is outside the curated catalog are verified the same
   way — grep their live docs — rather than skipped.
```

- [ ] **Step 5: Edit `tf-migrate` Step 4 (Coverage check)**

In `plugins/tfmod-search/skills/tf-migrate/SKILL.md`, replace:

```
   Never claim coverage from memory; only from the retrieved doc. If an
   input's existence is uncertain (docs are curated summaries), say so and
   point to the registry link in the doc.
```

with:

```
   Never claim coverage from memory; only from the retrieved doc. When an
   input's existence is uncertain (the curated doc is a summary), confirm it
   with `grep_module_docs` by name: quote the matched line in the mapping
   table, or move the attribute to "not covered" on a confirmed miss.
```

- [ ] **Step 6: Verify all three files reference the tool and tests pass**

Run: `grep -L grep_module_docs plugins/tfmod-search/skills/tf-module-upgrade/SKILL.md plugins/tfmod-search/skills/tf-review/SKILL.md plugins/tfmod-search/skills/tf-migrate/SKILL.md`
Expected: no output (`-L` prints files *without* a match; none should lack it).

Run: `.venv/bin/pytest tests/e2e/test_plugin_e2e.py -q`
Expected: PASS — in particular `test_trigger_descriptions_are_disjoint` and `test_skills_delegate_to_agents` still pass (descriptions and the `tf-diff-reviewer` reference in tf-review are untouched).

- [ ] **Step 7: Commit**

```bash
git add plugins/tfmod-search/skills/tf-module-upgrade/SKILL.md plugins/tfmod-search/skills/tf-review/SKILL.md plugins/tfmod-search/skills/tf-migrate/SKILL.md
git commit -m "Replace registry-link cop-out with grep_module_docs in review/upgrade/migrate skills"
```

---

### Task 4: Add grep escalation to the troubleshoot and stack skills

**Files:**
- Modify: `plugins/tfmod-search/skills/tf-troubleshoot/SKILL.md` (Step 3)
- Modify: `plugins/tfmod-search/skills/tf-stack/SKILL.md` (Step 2)

**Interfaces:**
- Produces: `grep_module_docs` mentioned in both files (Task 6 asserts it for `tf-troubleshoot`; `tf-stack` is user-invoked, mention intended but not asserted).

- [ ] **Step 1: Edit `tf-troubleshoot` Step 3 (Analyze)**

In `plugins/tfmod-search/skills/tf-troubleshoot/SKILL.md`, replace:

```
3. **Analyze in isolation.** On Claude Code, launch the `tf-log-analyst`
   agent with the log path and the script path — it verifies each finding
   against current docs and returns a compact report; relay it. Where
   subagents are unavailable, analyze the extracted findings inline:
   for every finding naming a terraform-aws-modules module, `get_module`
   and check the failing variable against the documented inputs — renamed,
   removed, type mismatch, missing required, or deprecated.
```

with:

```
3. **Analyze in isolation.** On Claude Code, launch the `tf-log-analyst`
   agent with the log path and the script path — it verifies each finding
   against current docs and returns a compact report; relay it. Where
   subagents are unavailable, analyze the extracted findings inline:
   for every finding naming a terraform-aws-modules module, `get_module`
   and check the failing variable against the documented inputs — renamed,
   removed, type mismatch, missing required, or deprecated. Escalate to
   `grep_module_docs` when the curated doc is not enough: the failing variable
   is absent from it (grep the exact name), the log shows an older pinned
   version (grep at that `version`), or the module is not in the catalog (grep
   its live docs and mark the diagnosis verified instead of inferred).
```

- [ ] **Step 2: Edit `tf-stack` Step 2 (Read before writing)**

In `plugins/tfmod-search/skills/tf-stack/SKILL.md`, replace:

```
2. **Read before writing.** `get_module` for every chosen module — blocks are
   written from the retrieved docs, never from memory. Pin each module's
   `version` to the documented current version.
```

with:

```
2. **Read before writing.** `get_module` for every chosen module — blocks are
   written from the retrieved docs, never from memory. Pin each module's
   `version` to the documented current version. When you are unsure of an exact
   output or input name for the wiring, grep it with `grep_module_docs`
   (`scope="root/outputs"` for outputs) rather than guessing; a component with
   no catalog module (non-AWS, third-party) can still be wired from its live
   docs the same way.
```

- [ ] **Step 3: Verify and run tests**

Run: `grep -L grep_module_docs plugins/tfmod-search/skills/tf-troubleshoot/SKILL.md plugins/tfmod-search/skills/tf-stack/SKILL.md`
Expected: no output.

Run: `.venv/bin/pytest tests/e2e/test_plugin_e2e.py -q`
Expected: PASS — `test_troubleshoot_skill_ships_prefilter_script` still finds `extract_tf_errors.py` in the body (that line is untouched).

- [ ] **Step 4: Commit**

```bash
git add plugins/tfmod-search/skills/tf-troubleshoot/SKILL.md plugins/tfmod-search/skills/tf-stack/SKILL.md
git commit -m "Add grep_module_docs escalation to troubleshoot and stack skills"
```

---

### Task 5: Add grep verification to both subagents

**Files:**
- Modify: `plugins/tfmod-search/agents/tf-diff-reviewer.md` (Step 3)
- Modify: `plugins/tfmod-search/agents/tf-log-analyst.md` (Step 3 + confidence scale)

**Interfaces:**
- Produces: `grep_module_docs` mentioned in both agent files (Task 6's `test_agents_reference_grep_tool` asserts it).

- [ ] **Step 1: Edit `tf-diff-reviewer` Step 3 (Verify against current docs)**

In `plugins/tfmod-search/agents/tf-diff-reviewer.md`, replace:

```
3. **Verify against current docs.** For each distinct terraform-aws-modules
   module: `get_module` (tfmod-search MCP server), then check:
   - every variable used exists in the current inputs (a variable absent from
     the doc is *suspicious*, not proven dead — the doc links to the registry
     for the exhaustive list; mark such findings accordingly)
   - required inputs are present
   - `version` is pinned; flag unpinned or a major behind current
   - deprecated arguments per the doc's notes
```

with:

```
3. **Verify against current docs.** For each distinct terraform-aws-modules
   module: `get_module` (tfmod-search MCP server), then check:
   - every variable used exists in the current inputs (a variable absent from
     the curated doc is *suspicious*, not proven dead — confirm with
     `grep_module_docs` at the version the block pins before reporting it, and
     quote the line)
   - required inputs are present
   - `version` is pinned; flag unpinned or a major behind current
   - deprecated arguments per the doc's notes
   Module blocks whose `source` is outside the curated catalog are verified the
   same way via `grep_module_docs` and marked live-doc-verified, not skipped.
```

- [ ] **Step 2: Edit `tf-log-analyst` Step 3 (Verify against current documentation)**

In `plugins/tfmod-search/agents/tf-log-analyst.md`, replace:

```
3. **Verify against current documentation, not memory.** For every finding
   that names a module from terraform-aws-modules: call `get_module` (the
   tfmod-search MCP server) and check the failing variable against the
   documented inputs. Quote the documented variable name/type you verified.
   If the module is not in the tfmod-search catalog, say so explicitly and
   reason from the error text alone, clearly marked as unverified.
```

with:

```
3. **Verify against current documentation, not memory.** For every finding
   that names a module from terraform-aws-modules: call `get_module` (the
   tfmod-search MCP server) and check the failing variable against the
   documented inputs. Quote the documented variable name/type you verified.
   When the curated doc is not enough — the variable is absent from it, or the
   log pins an older version — escalate to `grep_module_docs` (grep the exact
   name, at the log's version when present) and quote the live line. A module
   outside the catalog is no longer a dead end: grep its live registry docs the
   same way; fall back to reasoning from the error text alone only when even the
   grep is inconclusive, clearly marked as unverified.
```

- [ ] **Step 3: Edit the `tf-log-analyst` confidence scale**

In the same file, replace:

```
- Confidence: verified-against-doc | inferred-from-error
```

with:

```
- Confidence: verified-against-doc | verified-against-live-doc | inferred-from-error
```

- [ ] **Step 4: Verify and run tests**

Run: `grep -L grep_module_docs plugins/tfmod-search/agents/tf-diff-reviewer.md plugins/tfmod-search/agents/tf-log-analyst.md`
Expected: no output.

Run: `.venv/bin/pytest tests/e2e/test_plugin_e2e.py::TestAgents -q`
Expected: PASS — `test_agent_frontmatter`, `test_claude_manifest_registers_agents`, `test_skills_delegate_to_agents` all still pass (front-matter and agent names untouched).

- [ ] **Step 5: Commit**

```bash
git add plugins/tfmod-search/agents/tf-diff-reviewer.md plugins/tfmod-search/agents/tf-log-analyst.md
git commit -m "Add grep_module_docs verification to tf-diff-reviewer and tf-log-analyst agents"
```

---

### Task 6: Contract regression test + README skills table + full-suite verification

**Files:**
- Modify: `tests/e2e/test_plugin_e2e.py` (add `test_model_invoked_skills_reference_grep_tool` to `TestSkills`, `test_agents_reference_grep_tool` to `TestAgents`)
- Modify: `README.md:77-85` (skills table: "Seven" → "Eight", add the `/tf-grep` bullet)

**Interfaces:**
- Consumes: `grep_module_docs` mentions added in Tasks 2–5 (all five model-invoked skills + both agents now contain the token).

- [ ] **Step 1: Add the skill contract test**

In `tests/e2e/test_plugin_e2e.py`, inside `class TestSkills`, after the existing `test_troubleshoot_skill_ships_prefilter_script` method, add:

```python
    @pytest.mark.parametrize("skill_name", sorted(EXPECTED_SKILLS - USER_INVOKED_SKILLS))
    def test_model_invoked_skills_reference_grep_tool(self, skill_name):
        """Every model-invoked skill must teach the compact-doc -> grep
        escalation. Regression guard for the grep_module_docs skills
        integration: future skill edits cannot silently drop the guidance."""
        _, body = _parse_frontmatter(SKILLS_DIR / skill_name / "SKILL.md")
        assert "grep_module_docs" in body, f"{skill_name} must reference grep_module_docs"
```

- [ ] **Step 2: Add the agent contract test**

In the same file, inside `class TestAgents`, after `test_skills_delegate_to_agents`, add:

```python
    @pytest.mark.parametrize("agent_name", sorted(EXPECTED_AGENTS))
    def test_agents_reference_grep_tool(self, agent_name):
        """Both subagents must verify findings against live docs via
        grep_module_docs, not only the curated get_module doc."""
        _, body = _parse_frontmatter(self.AGENTS_DIR / f"{agent_name}.md")
        assert "grep_module_docs" in body, f"{agent_name} must reference grep_module_docs"
```

- [ ] **Step 3: Run the new contract tests to verify they pass**

Run: `.venv/bin/pytest tests/e2e/test_plugin_e2e.py -q -k "reference_grep_tool"`
Expected: PASS — 5 model-invoked skills (`aws-terraform-modules`, `tf-migrate`, `tf-module-upgrade`, `tf-review`, `tf-troubleshoot`) + 2 agents = 7 cases pass. (If any fail, the corresponding Task 2–5 edit is missing — go fix it before proceeding.)

- [ ] **Step 4: Update the README skills table**

In `README.md`, replace:

```
- **Seven skills**:
  - `aws-terraform-modules` — auto-invoked when writing Terraform for AWS: search first, write from current docs, pin versions
  - `/tf-module <query>` — instant module lookup with a ready-to-paste snippet
  - `/tf-stack <requirement>` — scaffold a multi-module stack with correct output→input wiring
```

with:

```
- **Eight skills**:
  - `aws-terraform-modules` — auto-invoked when writing Terraform for AWS: search first, write from current docs, pin versions
  - `/tf-module <query>` — instant module lookup with a ready-to-paste snippet
  - `/tf-grep <module> <pattern>` — grep the live registry docs of any module (version-pinnable, non-AWS too) for an exact quote
  - `/tf-stack <requirement>` — scaffold a multi-module stack with correct output→input wiring
```

- [ ] **Step 5: Sweep for other stale skill counts in the README**

Run: `grep -n -i "seven skill" README.md`
Expected: no output. If any line still says "seven skills", change "seven"/"Seven" to "eight"/"Eight" in that prose line (do not touch `CHANGELOG.md` history entries, which are point-in-time records).

- [ ] **Step 6: Run the full e2e + integration suite**

Run: `.venv/bin/pytest tests/ -q`
Expected: PASS — all previously-passing tests plus the 7 new contract cases and the tf-grep parametrized cases. The 6 opt-in live tests skip (no `RUN_REGISTRY_BENCHMARK=1`).

- [ ] **Step 7: Update the README test-count line to the actual number**

Run: `.venv/bin/pytest tests/ -q --co | tail -1` to see the collected count, and `.venv/bin/pytest tests/e2e -q --co | tail -1` for the e2e count. Update the two count references if they drifted:
- `README.md` "End-to-End (49 tests)" → the new e2e collected count.
- `README.md` "**Total**: 345 tests ..." → the new total collected count.

Only edit the numbers; leave the surrounding wording. (CLAUDE.md carries the same counts but is gitignored — update it locally if you keep it in sync, but it is not committed.)

- [ ] **Step 8: Commit**

```bash
git add tests/e2e/test_plugin_e2e.py README.md
git commit -m "Add grep_module_docs contract tests; document /tf-grep skill"
```

---

## Self-Review

**1. Spec coverage:**
- Spec §1 (shared mental model E1–E4) → woven across Tasks 2–5 (each skill keeps the triggers its workflow hits). ✓
- Spec §2 (new `/tf-grep` skill + Codex binding) → Task 1. ✓
- Spec §3 (surgical edits to 7 skills + 2 agents) → aws-terraform-modules + tf-module (Task 2), tf-module-upgrade + tf-review + tf-migrate (Task 3), tf-troubleshoot + tf-stack (Task 4), tf-diff-reviewer + tf-log-analyst (Task 5). All 9 files covered. ✓
- Spec §4 (tests: EXPECTED_SKILLS/USER_INVOKED_SKILLS += tf-grep; new contract test; trigger-disjointness unaffected) → Task 1 sets, Task 6 contract tests. ✓
- Spec §5 (README skills table; CHANGELOG/version at release time) → README in Task 6; CHANGELOG/version explicitly deferred per Global Constraints. ✓

**2. Placeholder scan:** No "TBD"/"handle edge cases"/"similar to Task N". Every edit shows the literal old→new text and every test step shows the exact command and expected result. ✓

**3. Type/string consistency:** The token asserted by the contract test (`grep_module_docs`) is exactly the token inserted in Tasks 2–5. `EXPECTED_SKILLS - USER_INVOKED_SKILLS` after Task 1 = `{aws-terraform-modules, tf-migrate, tf-module-upgrade, tf-review, tf-troubleshoot}` — precisely the 5 files Task 6 Step 3 expects (tf-grep, tf-module, tf-stack are user-invoked and excluded). The Codex binding matches `tf-stack`'s verbatim, satisfying `test_codex_skill_binding_declares_mcp_dependency` for the `allow_implicit_invocation is False` branch. ✓

**Note on tf-module/tf-stack:** they are edited to mention `grep_module_docs` (Tasks 2, 4) but are user-invoked, so the contract test does not assert them — intentional, matching the spec's scope. Their mentions are a usability nicety, not a guarded contract.
