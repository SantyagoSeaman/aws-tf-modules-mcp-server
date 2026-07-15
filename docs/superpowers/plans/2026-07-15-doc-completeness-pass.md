# 0.21.0 Corpus Completeness Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the field shape of every collapsed/opaque-typed input row across the module docs (from the answer-agnostic live registry type or the module's own examples), ship a linter + CI guard + allowlist, and re-encode the changed docs drift-safely so the golden set stays 172/172.

**Architecture:** A `scripts/` linter is the tool of record: an offline `--check` mode (CI guard) and an online `--suggest` authoring mode that fetches the registry type and prints the exact field roster to append. Docs are edited append-only in batches. A re-encode script updates only changed docs' vectors + rebuilds BM25. A guard test pins the corpus against regression via an allowlist of reviewed irreducible rows.

**Tech Stack:** Python 3.12+, stdlib (urllib for the online suggest mode only), pytest, the repo's own `tfmod_search_lib` for re-encode.

## Global Constraints

- **Answer-agnostic source of truth:** a composite input's shape comes from its live Terraform Registry `type` (Class 2/3) or the module's own Usage Examples (Class 1). NEVER curate toward the test set. redshift/wafv2 prose gaps ship only as part of the corpus-wide pass.
- **Append-only, top-level-only, capped.** Fixes append a field roster to the existing Description cell; they do not rewrite descriptions, restructure tables, or rename headings. Rosters name top-level fields only, capped at 8, then `, … (see grep_module_docs)`.
- **Drift-safe index:** re-encode ONLY changed docs; unchanged docs' `doc_vectors` rows stay byte-identical. Hard gate: golden set 172/172 top-3 on BOTH torch and onnx backends.
- **No server/tool code change, no new runtime dependency.** Linter lives in `scripts/` (not shipped in the wheel); the online fetch uses stdlib `urllib`.
- Commit messages: plain content-only, NO apostrophes/contractions, no attribution trailers.
- The linter's `--check` mode and the guard test are OFFLINE (operate on local `.md` only). Only `--suggest` touches the network.
- Baseline invariant: on the current corpus the linter flags exactly the 122-row baseline (a Task-1 test pins this before any doc edit).

---

### Task 1: Completeness linter — `scripts/lint_doc_completeness.py`

**Files:**
- Create: `scripts/lint_doc_completeness.py`
- Test: `tests/integration/test_doc_completeness_linter.py`

**Interfaces:**
- Produces (importable for tests):
  - `find_opaque_rows(md_text: str) -> list[Flag]` where `Flag` is a dataclass/namedtuple `(line: int, variable: str, type_cell: str)`. Flags a `### / ## Main Input Variables` table row whose Type cell matches the opaque set and is not already `object({...})`-expanded, and whose Description has no shape signal (see regexes below).
  - `top_level_fields(type_str: str) -> list[str]` — given a registry HCL type string, return the outermost `object({...})`'s top-level attribute names (handles `map(object({...}))`, `list(object({...}))`, `set(object({...}))` by locating the first `object({`); `[]` when the type has no object body (e.g. bare `any`).
  - `roster(fields: list[str], cap: int = 8) -> str` — render `` — fields: `a`, `b`, `c` `` (all when <= cap) or `` — fields: `a`, … (8 shown; see grep_module_docs) `` (capped).
  - `check_corpus(docs_dir: str, allowlist: set[str]) -> list[str]` — return `"<module.md>::<variable>"` for every flagged row NOT in the allowlist.
- Opaque regex (Type cell): `` `(any|object|map\(object\)|list\(object\)|set\(object\)|map\(any\)|object\(\))` `` (case-insensitive). Excluded when the Type cell contains `object({`.
- Hint regex (Description passes if ANY match): `` `[^`]+` `` OR `[{}\[\]]` OR `\b(shape|keys?|fields?|nest\w*|each|per-|see|submodule|example)\b` (case-insensitive).

- [ ] **Step 1: Write the failing unit tests**

Create `tests/integration/test_doc_completeness_linter.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import lint_doc_completeness as lint


def _tbl(rows):
    head = "### Main Input Variables\n\n| Variable | Type | Default | Description |\n|---|---|---|---|\n"
    return head + "".join(rows)


def test_flags_opaque_row_without_hint():
    md = _tbl(["| `metadata_options` | `object` | `{}` | IMDS options; IMDSv2 required by default |\n"])
    flags = lint.find_opaque_rows(md)
    assert [f.variable for f in flags] == ["metadata_options"]


def test_does_not_flag_when_description_names_a_field():
    md = _tbl(["| `subscriptions` | `map(object)` | `{}` | each sets `protocol`, `endpoint` |\n"])
    assert lint.find_opaque_rows(md) == []


def test_does_not_flag_type_already_expanded():
    md = _tbl(["| `timeouts` | `object({create,delete})` | `{}` | timeout overrides |\n"])
    assert lint.find_opaque_rows(md) == []


def test_top_level_fields_from_object():
    t = "object({\n  http_endpoint = optional(string, \"enabled\")\n  http_tokens = optional(string)\n})"
    assert lint.top_level_fields(t) == ["http_endpoint", "http_tokens"]


def test_top_level_fields_from_map_object():
    t = "map(object({\n  encrypted = optional(bool)\n  size = optional(number)\n}))"
    assert lint.top_level_fields(t) == ["encrypted", "size"]


def test_top_level_fields_empty_for_any():
    assert lint.top_level_fields("any") == []


def test_roster_capped():
    r = lint.roster([f"f{i}" for i in range(12)], cap=8)
    assert "f0" in r and "f7" in r and "f8" not in r
    assert "grep_module_docs" in r


def test_check_corpus_honors_allowlist(tmp_path):
    d = tmp_path / "modules"
    d.mkdir()
    (d / "x.md").write_text(_tbl(["| `foo` | `any` | `{}` | freeform passthrough |\n"]))
    assert lint.check_corpus(str(d), set()) == ["x.md::foo"]
    assert lint.check_corpus(str(d), {"x.md::foo"}) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integration/test_doc_completeness_linter.py -q`
Expected: FAIL / import error (module not created).

- [ ] **Step 3: Implement `scripts/lint_doc_completeness.py`**

Implement the functions above plus a `main()`:
- `find_opaque_rows`: split lines; when a line matches `^#{2,3}\s+.*Input` (case-insensitive), advance to the first `|`-row (stop at the next `#`), then iterate table rows; for each row with >=4 cells, take `variable = cells[0].split("/")[0].strip().strip("` ")`, `type_cell = cells[1]`, `desc = " ".join(cells[3:])`; apply the opaque + not-expanded + no-hint rules; record `Flag(lineno, variable, type_cell)`.
- `top_level_fields`: find the first `object({` (case-insensitive); scan from the matching `{` tracking brace depth; at depth 1, capture the identifier matched by `^\s*([A-Za-z_]\w*)\s*=` at the start of each top-level segment (split on depth-1 commas/newlines); return in order, de-duplicated preserving order.
- `roster`: as specified.
- `check_corpus`: for each `*.md` under docs_dir, run `find_opaque_rows`, emit `f"{path.name}::{flag.variable}"` for flags whose key is not in `allowlist`.
- `main()` argparse:
  - default: print a human report (module, line, variable, type) for all flags.
  - `--check`: read allowlist from `tests/fixtures/doc_completeness_allowlist.txt` (or `--allowlist PATH`); print unresolved keys; `sys.exit(1)` if any.
  - `--suggest MODULE`: fetch the registry types for that module (root + submodules) and, per flagged row, print the variable, its class (1 any / 2 small / 3 large), and the exact `roster(...)` string to append (Class 2/3), or `GENUINE any -> example-keys or xref or allowlist` (Class 1). Fetch via `urllib` from `https://registry.terraform.io/v1/modules/terraform-aws-modules/<module>/aws` (root `inputs`) and the submodule endpoints under `.../submodules` as needed; wrap network in try/except and degrade to "fetch failed" so the offline modes never import-fail.
  - Guard the `urllib.request.urlopen` call with a scheme check + `# noqa: S310` (match the repo's existing pattern in `tfmod_registry_docs.py`).

- [ ] **Step 4: Run unit tests to verify they pass**

Run: `pytest tests/integration/test_doc_completeness_linter.py -q`
Expected: PASS.

- [ ] **Step 5: Pin the corpus baseline**

Add to the same test file:

```python
def test_corpus_baseline_is_122():
    root = Path(__file__).resolve().parents[2] / "modules/terraform-aws-modules"
    total = sum(len(lint.find_opaque_rows(p.read_text())) for p in root.glob("*.md"))
    assert total == 122, f"linter baseline drifted to {total}; retune before proceeding"
```

Run it. If it is not 122, the linter regexes do not match the scoping run — reconcile before any doc edits (the whole plan is calibrated to this baseline). Once green, commit.

- [ ] **Step 6: Commit**

```bash
git add scripts/lint_doc_completeness.py tests/integration/test_doc_completeness_linter.py
git commit -m "Add doc completeness linter with offline check and online suggest modes"
```

---

### Task 2: Re-encode helper — `scripts/reencode_changed_docs.py`

**Files:**
- Create: `scripts/reencode_changed_docs.py`
- Test: `tests/integration/test_reencode_changed_docs.py`

**Interfaces:**
- Produces `reencode(index_path: str, changed_paths: list[str], logger) -> None` — loads the index, and for each doc whose `.path` matches a changed path, re-parses the file, replaces that doc's `doc_vectors` row (via `_get_encoder(index.model_name).encode([rec.text])`), `bm25_corpus_tokens` row (`tokenize(rec.text)`), `docs` entry, `module_names`, `doc_kw_sets`; then rebuilds `index.bm25 = BM25Okapi(index.bm25_corpus_tokens)` and `index.kw_idf = compute_kw_idf(index.docs)`; saves via `save_index`. Unchanged docs' `doc_vectors` rows are left byte-identical.

- [ ] **Step 1: Write the failing test**

```python
import logging
from pathlib import Path

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import reencode_changed_docs as rc
from tfmod_search_lib import load_index

INDEX = str(Path(__file__).resolve().parents[2] / "model/tfmod_e5_small_index.pkl")


def test_reencode_only_changes_target_doc(tmp_path, monkeypatch):
    log = logging.getLogger("t")
    before = load_index(INDEX, log)
    # pick a doc, snapshot all vectors
    target = next(d for d in before.docs if d.module_name == "vpc")
    ti = before.docs.index(target)
    v_before = before.doc_vectors.copy()
    # append a byte to the vpc file in a temp copy of the index is heavy; instead assert
    # the invariant helper: reencode of an UNCHANGED file leaves that row byte-identical.
    rc.reencode(INDEX + ".tmp" if False else INDEX, [], log)  # no-op path -> loads+saves nothing changed
    after = load_index(INDEX, log)
    assert np.array_equal(v_before, after.doc_vectors), "no-op reencode must not perturb any vector"
```

(If a no-op reencode is awkward, instead test that after `reencode` with one real changed file, exactly that doc's vector row differs and all others are `array_equal` — but do NOT leave the index modified: operate on a copied pickle in `tmp_path`. Prefer the copied-pickle form; write it concretely in implementation.)

- [ ] **Step 2..4: Implement and verify**

Implement `reencode` per the interface. Reuse `load_index`, `save_index`, `parse_markdown_file`, `tokenize`, `compute_kw_idf`, `_get_encoder` from `tfmod_search_lib`. Encode all changed docs in a single `encode([...])` call. Run the test against a copied pickle so the real index is untouched by the test. Expected: PASS, unchanged rows byte-identical.

- [ ] **Step 5: Commit**

```bash
git add scripts/reencode_changed_docs.py tests/integration/test_reencode_changed_docs.py
git commit -m "Add drift-safe re-encode helper for changed docs only"
```

---

### Tasks 3-8: Doc fixes by batch (sequential subagents)

The 27 flagged docs are fixed in 6 batches of ~4-5 docs. **Each batch is one task** (one commit), executed sequentially. Batches (grouped to balance flagged-row counts):

- **Batch A:** alb, apigateway-v2, app-runner, appsync, cloudfront
- **Batch B:** cloudwatch, dms, ec2-instance, ecr, elasticache
- **Batch C:** ecs, eks
- **Batch D:** fsx, iam, lambda, managed-service-grafana, managed-service-prometheus
- **Batch E:** msk-kafka-cluster, opensearch, rds-aurora, redshift, route53
- **Batch F:** s3-bucket, sns, sqs, transit-gateway, vpc, wafv2

**Files (per batch):** the listed `modules/terraform-aws-modules/*.md`; possibly `tests/fixtures/doc_completeness_allowlist.txt` (created in Task 9 — batches only NOTE rows destined for the allowlist in the commit body, they do not edit the allowlist file).

**Procedure for each doc in the batch (identical every time):**

- [ ] **Step 1: List the flags**

Run: `python scripts/lint_doc_completeness.py --suggest <module>`
This prints, per flagged row: variable, class, and either the exact roster string (Class 2/3) or `GENUINE any` (Class 1).

- [ ] **Step 2: Apply the fix per row**

- **Class 2/3:** append the suggested `roster(...)` string to that row's Description cell, inside the table, e.g.
  `... IMDS options; IMDSv2 required by default — fields: \`http_endpoint\`, \`http_tokens\`, \`http_put_response_hop_limit\`, \`instance_metadata_tags\``
  Do not alter the existing prose; append after it. Keep the row on one line (markdown table row).
- **Class 1 (`GENUINE any`):** in priority order —
  1. If the module has a submodule that types this composite (check `--suggest` output / the doc's `## Submodule` sections), append `` — see the `<submodule>` submodule for the typed shape ``.
  2. Else, read the module's own `### Usage Examples` in the same doc, and append the top-level keys actually used, tagged: `` — keys (from examples): `a`, `b`, `c` ``.
  3. Else (truly freeform, no stable keys), leave the row unchanged and record `"<module>.md::<variable>"` in the batch commit body under `ALLOWLIST:` for Task 9.
- **redshift (Batch E):** additionally complete the "Notes for AI Agents" bullet for `pause_cluster`: state that `pause_cluster`/`resume_cluster` are bare booleans (`= true`) and only `resize_cluster` takes a nested object.
- **wafv2 (Batch F):** additionally add a gotcha: managed-rule-group / rule-group-reference statements take `override_action` (`"none"`/`"count"`); standalone match statements take `action`; mutually exclusive.

- [ ] **Step 3: Verify the doc dropped its flags**

Run: `python scripts/lint_doc_completeness.py | grep "<module>.md"`
Expected: only rows you intentionally deferred to the allowlist remain.

- [ ] **Step 4: Commit the batch**

```bash
git add modules/terraform-aws-modules/<the batch files>
git commit -m "Expand collapsed input shapes: <batch letter> (<modules>)

Append top-level field rosters from the live registry type; genuine any-typed
inputs cross-ref a typed submodule or name example-derived keys.
ALLOWLIST: <module.md::var> ... (genuine freeform, no stable field set)"
```

Batch C (ecs, eks) has the most rows and the most submodule-sourced vars; keep it its own task.

**Subagent instructions (for the dispatcher):** dispatch one Sonnet subagent per batch, sequentially. Give it: this procedure, the batch's module list, and the rule that every appended field name MUST come from the registry `--suggest` output or the doc's own examples — never invented. The subagent commits its batch and reports the flagged-row count before/after and the exact `ALLOWLIST:` rows it deferred.

---

### Task 9: Re-encode changed docs + golden gate

**Files:**
- Modify: `model/tfmod_e5_small_index.pkl` (in place, changed docs only)

- [ ] **Step 1: Re-encode**

Collect the changed docs: `git diff --name-only master...HEAD -- modules/terraform-aws-modules/`.
Run: `python scripts/reencode_changed_docs.py model/tfmod_e5_small_index.pkl <each changed .md>`

- [ ] **Step 2: Golden gate on the torch backend**

Run: `pytest tests/integration/test_all_modules_searchable.py tests/integration/test_model_comparison.py -q`
Expected: 172/172 golden targets still in top-3; all pass.

- [ ] **Step 3: Golden gate on the onnx backend**

Run: `TFMODSEARCH_EMBED_BACKEND=onnx pytest tests/integration/test_all_modules_searchable.py -q`
(If ONNX assets are not present locally, note it and rely on the release Docker gate; state this explicitly in the task output — do not silently skip.)
Expected: identical golden pass.

- [ ] **Step 4: If a golden target regressed**

Identify the doc via the failing query. Make that doc's roster edit MORE minimal (fewer words, drop the prose lead-in, keep only the backticked field names), re-run Task 9 Step 1 for that doc, re-gate. Only if a genuine ranking conflict persists after minimization, STOP and report to the maintainer — never edit the golden expectation.

- [ ] **Step 5: Commit**

```bash
git add model/tfmod_e5_small_index.pkl
git commit -m "Re-encode changed docs into the index (changed docs only, golden set 172/172)"
```

---

### Task 10: Guard test + allowlist

**Files:**
- Create: `tests/fixtures/doc_completeness_allowlist.txt`
- Create: `tests/integration/test_doc_completeness.py`

- [ ] **Step 1: Generate the residual allowlist**

Run: `python scripts/lint_doc_completeness.py` and collect every still-flagged `"<module>.md::<variable>"`. These are the deferred genuine-`any` rows (matching the `ALLOWLIST:` lines from the batch commits). Write them to `tests/fixtures/doc_completeness_allowlist.txt`, one `module.md::variable  # reason` per line. REVIEW each: it must be a genuine freeform `any` with no stable field set and no typed submodule. If any is actually fixable, fix the doc instead of allowlisting (and re-run Task 9 for it).

- [ ] **Step 2: Write the guard test**

Create `tests/integration/test_doc_completeness.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import lint_doc_completeness as lint

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = ROOT / "tests/fixtures/doc_completeness_allowlist.txt"


def _allowlist():
    out = set()
    for line in ALLOWLIST.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(line)
    return out


def test_no_unlisted_opaque_rows():
    unresolved = lint.check_corpus(str(ROOT / "modules/terraform-aws-modules"), _allowlist())
    assert unresolved == [], f"opaque input rows not expanded and not allowlisted: {unresolved}"


def test_allowlist_has_no_stale_entries():
    flagged = set(lint.check_corpus(str(ROOT / "modules/terraform-aws-modules"), set()))
    stale = _allowlist() - flagged
    assert stale == set(), f"allowlist entries that are no longer flagged (remove them): {stale}"
```

- [ ] **Step 3: Verify green**

Run: `pytest tests/integration/test_doc_completeness.py tests/integration/test_doc_schema.py -q`
Expected: PASS (guard green; interface keys still resolve on every doc).

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/doc_completeness_allowlist.txt tests/integration/test_doc_completeness.py
git commit -m "Add corpus completeness guard test with reviewed allowlist"
```

---

### Task 11: Full suite + version bump + CHANGELOG

- [ ] **Step 1: Full suite**

Run: `pytest tests/ -q`
Expected: all pass (opt-in live tests skip). Known local `TestClaudeCliLive` shadow flake is environmental.

- [ ] **Step 2: Version bump to 0.21.0**

`grep -rn "0\.20\.0" pyproject.toml plugins/ README.md docker-compose.yml` and bump: `pyproject.toml`, both plugin `plugin.json`, `DEFAULT_IMAGE`, `docker-compose.yml` image tag, README current-release image tags, README `/health` example version. Leave historical CHANGELOG version mentions.

- [ ] **Step 3: CHANGELOG entry**

Match the format (link line, summary, Added/Changed/Unchanged). Summary: corpus completeness pass (top-level field rosters on collapsed inputs from the live registry type; example-keys / submodule xref for genuine any; redshift bare-bool + wafv2 override_action prose gaps), a `scripts/` linter + CI guard + allowlist, drift-safe re-encode of changed docs only with the golden set held at 172/172 on both backends. Note: no server/tool code change.

- [ ] **Step 4: Verify and commit**

Run: `pytest tests/ -q` once more.

```bash
git add -A
git commit -m "Release 0.21.0: corpus completeness pass, linter, and CI guard"
```

---

## Self-Review notes

- Spec coverage: linter -> Task 1; re-encode -> Task 2 + 9; doc fixes (Class 1/2/3 + submodule + redshift/wafv2) -> Tasks 3-8; guard + allowlist -> Task 10; drift gate -> Task 9; release plumbing -> Task 11.
- The index-editing tasks (9) come AFTER all doc edits, so the re-encode runs once over the full changed set and the golden gate is evaluated on the final text.
- Type consistency: `find_opaque_rows -> list[Flag]`, `top_level_fields(str) -> list[str]`, `roster(list, cap) -> str`, `check_corpus(dir, set) -> list[str]`, `reencode(index_path, changed_paths, logger)` used consistently across tasks.
- The allowlist is built from the ACTUAL residual (Task 10), not guessed up front, and `test_allowlist_has_no_stale_entries` keeps it honest.
