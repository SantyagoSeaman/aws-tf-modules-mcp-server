# 0.21.0 — Corpus completeness pass + linter design

## Context

The v4 post-testing report's load-bearing item 6: make the doc generator's shape-completeness
uniform across the corpus, so an agent orienting on any module sees the field structure of a
composite input, not just its purpose. Answer-agnostic (validated by the docs that already pass),
not trap-curation.

Scoping measurement (this repo, 2026-07-15): a tuned linter flags **122 collapsed/opaque-typed
`### Main Input Variables` rows across 27 of 55 docs** whose Description names neither the object's
fields nor where its shape lives. Cross-referenced against the live Terraform Registry `type` for
each variable, they split into four treatment classes:

| Class | Count | Registry `type` | Treatment |
|---|---|---|---|
| 1 — genuine `any` | 30 | literally `any` (no shape exists) | name keys from the module's own examples, or cross-ref a typed submodule; else allowlist |
| 2 — small `object({...})` | 35 | real, <=350 chars | append the object's top-level field names to the Description |
| 3 — large `object`/`map(object(...))` | 20 | real, >350 chars | append top-level field names only, capped, + "see full type via grep" |
| submodule var | 37 | in a submodule's inputs, not root | same class logic, sourced from the submodule's registry inputs |

The maintainer chose the **full pass** (expand every flagged row) over a targeted subset,
accepting the higher index-drift risk. This spec makes that pass safe and answer-agnostic.

## North star and non-goals

- **Answer-agnostic.** The source of truth for a shape is the variable's live Terraform Registry
  `type` (Class 2/3) or the module's own Usage Examples (Class 1). Never curate toward the 23-item
  test set. redshift/wafv2 (report items 7/8) are fixed only as part of the corpus-wide pass, not
  as standalone cherry-picks.
- **Compact, not bloated.** Expansions name **top-level fields only** (no deep nesting), capped at
  ~8 with an ellipsis + grep pointer beyond that. The whole point of the collapsed types was to
  keep the curated doc small; the fix adds a one-line field roster, not the full HCL type.
- **Not a rewrite.** Edits **append** a shape roster to the existing Description cell; they do not
  restructure tables, rename headings, or touch any section other than the flagged rows (plus the
  two named prose gaps). Minimizing perturbation is the primary drift mitigation.
- **No new runtime code, no new dependency.** The linter is a `scripts/` dev tool + a CI guard
  test. Server code is untouched. The only shipped change is doc text + the re-encoded index.

## Components

### 1. Linter — `scripts/lint_doc_completeness.py`

Not shipped in the wheel (like `scripts/export_onnx_model.py`). Pure-stdlib, offline (operates on
the local `.md` files; does NOT call the registry — the registry lookups are an authoring aid, see
below, kept out of the guard so CI stays offline).

- Parses every `### Main Input Variables` / `## Main Input Variables` table (root and submodule).
- Flags a row whose Type cell is **opaque** — `any`, `object`, `map(object)`, `list(object)`,
  `set(object)`, `map(any)`, `object()` — AND is not already expanded in the Type cell
  (`object({...})`) AND whose Description contains **no shape signal**: no backticked identifier,
  no `{}`/`[]`, none of the words shape/key(s)/field(s)/nest/each/per-/see/submodule/example.
  (This is the tuned rule already validated against the corpus; it is deliberately lenient — a
  Description that names even one field in backticks passes.)
- `--check` mode: exit non-zero and print each unresolved flag NOT in the allowlist. Used by CI.
- Default mode: human report (doc, line, var, type) for authoring.

Exact opacity/hint regexes are given in the plan; they must reproduce the 122-row baseline on the
current corpus (a plan task asserts this before any edits, so the linter is pinned to known ground
truth).

### 2. Allowlist — `tests/fixtures/doc_completeness_allowlist.txt`

One `module.md::variable_name` per line + a short reason, for rows that are legitimately
irreducible: the source type is genuinely `any` AND the input is free-form pass-through with no
stable field set to name and no typed submodule sibling. Every allowlist entry is a reviewed
decision, not a silence. The guard passes when every flag is either fixed or allowlisted.

### 3. Guard test — `tests/integration/test_doc_completeness.py`

Runs the linter `--check` against the shipped corpus with the allowlist. Fails if any non-allowlisted
opaque row exists. This is the regression protection: a future doc (new module or edit) must either
name its composite inputs' shapes or add an explicit, reasoned allowlist entry. Offline, fast.

### 4. Doc edits (the pass)

For each flagged row, by class:

- **Class 2 (small object).** Append to the Description: `` — fields: `a`, `b`, `c`, … `` using the
  object's top-level attribute names from the registry `type`. Example: ec2-instance
  `metadata_options` (`object({ http_endpoint, http_protocol_ipv6, http_tokens,
  http_put_response_hop_limit, instance_metadata_tags })`).
- **Class 3 (large object).** Same, capped at ~8 top-level fields, then `, … (see full type via
  grep_module_docs)`. Example: cloudfront `default_cache_behavior`.
- **Class 1 (genuine `any`).** No type to expand. In priority order: (a) if a typed submodule
  sibling exists, cross-ref it (report item 10 — e.g. wafv2 root `rules` is `any` but the
  `web-acl-rule` submodule types the statement; render a pointer); (b) else name the common keys
  from the module's own Usage Examples (report item 9 — e.g. s3-bucket `lifecycle_rule` keys `id`,
  `enabled`, `filter`, `expiration`, `transition` as they appear in the examples), tagged as
  example-derived; (c) else allowlist with reason. Never invent a structure the source does not
  have.
- **Submodule vars.** Same class logic, sourced from the submodule's registry inputs.
- **Two named prose gaps (item 6 output, validation):**
  - redshift `pause_cluster`/`resume_cluster` are bare booleans (`= true`); only `resize_cluster`
    takes a nested object — complete the "Notes for AI Agents" bullet that today states only the
    path.
  - wafv2 `override_action` (`"none"`/`"count"`) applies to managed-rule-group / rule-group-
    reference statements; standalone match statements take `action`; mutually exclusive — add the
    gotcha (the word does not currently appear anywhere in the doc).

The registry `type` and the module examples are fetched during authoring via the existing
`tfmod_registry_docs` client / `grep_module_docs`; the fetched values are the answer-agnostic
source. No fetch happens at runtime or in CI.

### 5. Drift-safe index re-encode (highest risk)

Editing Description cells changes embedded text for ~27 docs. Per the drift policy:

- Re-encode **only the changed docs** (encode each edited doc's new text; keep every unchanged
  doc's embedding byte-identical — the v0.14.1 incremental pattern, extended from append to
  in-place update).
- **Golden gate: 172/172 top-3 must still pass** (`tests/integration/test_all_modules_searchable.py`
  + model-comparison golden set) on the re-encoded index, on BOTH backends (torch + onnx) per the
  0.19.0 parity policy.
- If a doc's edit drops a golden query, first make that doc's edit **more minimal** (shorter roster,
  fewer words) and re-encode; only if a genuine ranking conflict remains, escalate to the maintainer
  — do not silently loosen the golden expectation.

This is the release's main risk and its explicit gate. Append-only, top-level-only, capped edits are
chosen specifically to keep the per-doc embedding perturbation small.

## Testing

- `test_doc_completeness.py` — the guard (linter `--check` + allowlist) passes on the final corpus.
- `test_doc_schema.py` — still green (interface keys resolve on every doc; unchanged).
- `test_all_modules_searchable.py` + golden set — **172/172 on both backends** against the
  re-encoded index.
- Full suite green.
- A unit test for the linter itself (opaque detection, hint detection, allowlist honoring) on
  synthetic tables.

## Files touched

- Create: `scripts/lint_doc_completeness.py`, `tests/integration/test_doc_completeness.py`,
  `tests/fixtures/doc_completeness_allowlist.txt`.
- Modify: up to 27 files under `modules/terraform-aws-modules/*.md` (append-only shape rosters +
  the two prose gaps).
- Modify: `model/tfmod_e5_small_index.pkl` (per-doc re-encode of changed docs only).
- Version bump per the release process; CHANGELOG.

## Out of scope

- Any server/tool code change (0.20.0 territory; done).
- Deep/nested type expansion (kept top-level only by design).
- `.tf` source grep and background prefetch (separate specs).
- Non-top-1 metadata trim / `expand_top` / no-confident-match (separate spec; needs a spike).
