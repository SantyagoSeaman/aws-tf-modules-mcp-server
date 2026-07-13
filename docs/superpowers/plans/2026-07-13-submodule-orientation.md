# submodule-orientation Implementation Plan

**Goal:** Make submodules reachable without an index rebuild by (A1) surfacing the
`## Submodules` inventory inline in the `get_module` orientation head and (A3)
accepting a submodule address (`iam//modules/iam-role`) that returns a scoped head;
plus a **gated** parent keyword-enrichment that ships only if the index rebuild keeps
the golden set at 100%.

**Architecture:** All A1/A3 logic lives in `src/tfmod_mcp_server.py` — a new
`extra_exact_titles` param on `filter_module_sections`, a `_parse_submodule_address`
helper, and an interception branch in `get_module_impl`. No index change for the core.
Enrichment edits `## Module Information` keyword bullets in ≤17 curated docs and rebuilds
`model/tfmod_e5_small_index.pkl` behind a golden-set gate.

**Tech Stack:** Python 3.13, FastMCP, Pydantic, stdlib `re`, pytest. No new deps.

## Global Constraints

- No new runtime dependencies; server stays offline (A1/A3 are pure text ops).
- A1/A3 must not touch the index or embeddings — they ship unconditionally.
- Enrichment is gated: control rebuild green → enrich → golden set must stay 100%,
  else defer enrichment and ship A1+A3 only (spec §5).
- `//` is the submodule-address sentinel; non-`//` identifiers keep exact today's behaviour.
- A1 surfaces **only** the exact `## Submodules` heading, never `## Submodule N:` deep-dives.
- Version bump touches 3 files + `uv.lock`: `pyproject.toml`,
  `plugins/tfmod-search/.claude-plugin/plugin.json`,
  `plugins/tfmod-search/.codex-plugin/plugin.json`, then `uv lock`.
- Commit messages: plain content-only, no attribution trailers. Push only after approval.
- Trailing newline at EOF on every text file.

---

### Task 1: A1 — `extra_exact_titles` on `filter_module_sections`, inventory in the head

**Files:**
- Modify: `src/tfmod_mcp_server.py` (`filter_module_sections`, `orientation_head`)
- Test: `tests/integration/test_mcp_server.py`

**Interfaces:**
- `filter_module_sections(text, requested, *, extra_exact_titles: tuple[str, ...] = ())`
  — sections whose title equals (case-insensitively) any `extra_exact_titles` entry are
  always included, exactly like `_CORE_SECTIONS`.
- `orientation_head` passes `extra_exact_titles=("Submodules",)`.

- [ ] **Step 1:** Add failing tests: orientation head of `iam` contains
  `terraform-aws-modules/iam/aws//modules/iam-role` (inventory source string) and the
  heading `## Submodules`, but does **not** contain `## Submodule 4: iam-role` (deep-dive);
  a submodule-less doc (e.g. `atlantis`) head is byte-identical to the pre-change output
  except for nothing (no `Submodules` heading present).
- [ ] **Step 2:** Add the keyword-only `extra_exact_titles` param; fold it into the
  `wanted` seed set alongside `_CORE_SECTIONS` (case-insensitive equality). Default `()`
  keeps every existing caller unchanged.
- [ ] **Step 3:** `orientation_head` passes `extra_exact_titles=("Submodules",)`. Verify
  the inventory lands in the body, not the footer's "Not included" list.
- [ ] **Step 4:** `pytest tests/integration/test_mcp_server.py -q`.

### Task 2: A3 — submodule address → scoped head

**Files:**
- Modify: `src/tfmod_mcp_server.py` (`_parse_submodule_address` new, `get_module_impl`)
- Test: `tests/integration/test_mcp_server.py`

**Interfaces:**
- `_parse_submodule_address(identifier) -> tuple[str, str] | None` — `(parent_name, sub)`
  or `None`. `//` absent → `None`. Left side with `/` → treat as `module_id`, take middle
  part as name. Right side → last path component.
- `get_module_impl` intercepts an address before the normal resolver, fetches the parent
  via `get_module_documentation(parent_name)`, returns
  `_version_pin_hint + filter_module_sections(text, [sub] + (sections or []))`.

- [ ] **Step 1:** Unit tests for `_parse_submodule_address`: `"iam//modules/iam-role"` →
  `("iam","iam-role")`; `"terraform-aws-modules/iam/aws//modules/iam-role"` →
  `("iam","iam-role")`; `"iam//iam-role"` → `("iam","iam-role")`; `"vpc"` → `None`;
  `"modules/terraform-aws-modules/vpc.md"` → `None` (path, no `//`).
- [ ] **Step 2:** Tests for `get_module_impl("iam//modules/iam-role")`: contains the
  iam-role section + version-pin hint; does **not** contain `iam-oidc-provider`'s detail;
  full-id form returns the same; `"iam//modules/does-not-exist"` returns core sections and
  a footer that lists real submodule titles (no exception).
- [ ] **Step 3:** Implement `_parse_submodule_address` + the interception branch.
- [ ] **Step 4:** `pytest tests/integration/test_mcp_server.py -q`.

### Task 3: Schema guard + docstrings/descriptions

**Files:**
- Modify: `tests/integration/test_doc_schema.py`
- Modify: `src/tfmod_mcp_server.py` (get_module tool docstring, `sections` Field, server
  `instructions` — mention the submodule-address form + inline inventory)

- [ ] **Step 1:** Add `test_submodule_inventory_surfaced_in_head`: for every doc that has a
  `## Submodules` heading, its `orientation_head` contains that heading.
- [ ] **Step 2:** Update the `get_module` tool description / docstring / `sections` Field and
  the server `instructions` string to document `get_module("<name>//modules/<sub>")` and the
  inline submodule inventory. Keep the 0.13.0 honest-limits footer wording intact.
- [ ] **Step 3:** `pytest tests/integration/test_doc_schema.py tests/integration/test_mcp_server.py -q`.

### Task 4: Enrichment gate — control rebuild

**Files:**
- Temp (not committed): `scratchpad/rebuild_index.sh`

- [ ] **Step 1:** Rebuild the index from unchanged docs to a scratchpad path; run
  `test_all_modules_searchable` against it (169). Record pass/fail. This tests
  reproducibility of the committed `.pkl`.
- [ ] **Step 2:** Decision point:
  - Control **green** → proceed to Task 5.
  - Control **drifts** → **skip Task 5**; note in CHANGELOG that enrichment is deferred;
    ship A1+A3. (Report the drift to the maintainer before finalizing the release.)

### Task 5: Parent keyword-enrichment (only if Task 4 green)

> **Outcome: DEFERRED.** The Task 4 control rebuild (zero doc changes) drifted the e5
> embeddings and dropped one golden-set target (`lambda` by keyword) — the committed
> `.pkl` is not bit-reproducible from current deps. Per the gate, enrichment is deferred
> to a dedicated index migration; A1 + A3 ship in 0.14.0 without any rebuild.

**Files:**
- Modify: `modules/terraform-aws-modules/{iam,cloudwatch,eks,s3-bucket,fsx,ecs,route53}.md`
  (and other `## Submodule N:` docs as warranted) — `**Keywords**` bullet only
- Modify: `model/tfmod_e5_small_index.pkl` (rebuilt, committed)
- Test: `tests/integration/test_all_modules_searchable.py`

- [ ] **Step 1:** Add submodule short-names + salient terms to each parent's `**Keywords**`
  bullet. Heading text and all other content untouched (keeps `test_doc_schema.py` green).
- [ ] **Step 2:** Rebuild + commit the index; `test_all_modules_searchable` must stay 100%.
  Add a targeted test: each enriched parent is still returned top-3 for its own name and now
  for at least one representative submodule-capability query.
- [ ] **Step 3:** If any golden-set target regresses and can't be recovered by keyword
  choice → revert enrichment, ship A1+A3.

### Task 6: Full suite + lint

- [ ] **Step 1:** `uv run pre-commit run --all-files` (ruff/mypy ground truth — trust it over
  local tool versions).
- [ ] **Step 2:** `pytest tests/ -q` in the foreground (background runs get killed in this env).
  All green; opt-in live tests skip.

### Task 7: Version bump + docs + CHANGELOG

**Files:**
- Modify: `pyproject.toml`, `plugins/tfmod-search/.claude-plugin/plugin.json`,
  `plugins/tfmod-search/.codex-plugin/plugin.json` → `0.14.0`; then `uv lock`.
- Modify: `CHANGELOG.md` ([0.14.0] entry).
- Modify: `README.md` (submodule-address form + inline inventory in the `get_module` section;
  test counts).
- Modify: `CLAUDE.md` (local, gitignored — never `git add -f`).

- [ ] **Step 1:** Bump the 3 files, `uv lock`, confirm `uv.lock` shows `0.14.0`.
- [ ] **Step 2:** CHANGELOG + README + CLAUDE.md edits.
- [ ] **Step 3:** Re-run `pytest tests/ -q` (test-count assertions, if any, updated).

### Task 8: PR → green CI → resolve Copilot → merge → release

- [ ] **Step 1:** Commit, push branch, open PR to `master`.
- [ ] **Step 2:** Wait for required checks (lint, test 3.12, test 3.13) green.
- [ ] **Step 3:** Resolve any substantive Copilot review threads
  (`resolveReviewThread` GraphQL); confirm `mergeStateStatus CLEAN`, 0 unresolved.
- [ ] **Step 4:** `gh pr merge --squash --delete-branch`.
- [ ] **Step 5:** `gh release create v0.14.0 --target master --notes-file <scratchpad>` →
  triggers `publish.yml` OIDC PyPI publish. Confirm PyPI `latest: 0.14.0`.
- [ ] **Step 6:** Update memory (`project_get_module_orientation` / a submodule note).
