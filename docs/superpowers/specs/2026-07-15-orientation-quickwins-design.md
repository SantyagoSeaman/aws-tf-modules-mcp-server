# 0.20.0 — Orientation quick wins (server-only) design

## Context

Post-testing report `tfmodsearch-improvements.md` (v4 Sonnet log analysis, 2026-07-15)
measured how condition-A workers actually used the tools across 6 transcripts. Three
findings are pure server output-shaping wins — no index rebuild, no corpus edit, no
network, no tool-schema change. They ship together as 0.20.0. The larger items from the
same report (no-confident-match signal, one-shot `expand_top`, `.tf` source grep,
background prefetch, the corpus-wide completeness linter) are explicitly out of scope
here; the linter is its own release (0.21.0), the rest need their own specs.

North star (unchanged, from the report): get the model to the right module in the fewest
calls and orient it fast, then get out of the way. All three changes reduce wasted tool
calls / re-billed cache-read chars without the server doing the model's reasoning.

## Scope — three changes

### Change 1 — Fix `sections=['inputs']` over-fetch on combined-heading modules (report addendum item 2)

**Problem.** The BUG-1 fix made an interface key (`inputs`/`outputs`/`examples`/`usage`/
`variables`) that finds no exact H2 heading fall back to the *whole* combined bundle —
every `## Root Module:` / `## Submodule N:` H2 block in full. So asking for *just inputs*
returns the entire root plus all submodules. Measured: s3-bucket 13.5K→30.9K, vpc
11.7K→27.5K, elasticache 12.4K→29.2K, apigateway-v2 9.7K→19.1K, opensearch 14.5K→26.2K
(≈2.3–2.4×, +~165K chars), and it lands on the earliest calls (highest cache-read
multiplier).

**Two doc schemes (verified across all 55 docs).**
- *Combined*: `## Root Module: X` (and `## Submodule N: Y`) H2 blocks, each containing H3
  sub-sections `### Description`, `### Key Features`, `### Main Input Variables`,
  `### Main Outputs`, `### Usage Examples` (submodules use singular `### Usage Example`).
  50/55 docs. The alias `inputs`→`Main Input Variables` has no top-level H2 here, so the
  fallback fires.
- *Split-toplevel*: `## Main Input Variables` / `## Main Outputs` / `## Usage Examples`
  as their own H2s (e.g. autoscaling, redshift). The exact alias already resolves; the
  fallback never fires; no over-fetch. **This scheme is already correct — do not touch.**

**Fix.** In the interface-key fallback, extract only the H3 sub-section(s) whose heading
matches the requested key from inside each combined bundle, instead of adding the whole
bundle. Keep the bundle's `## …` heading line above the extracted H3(s) so the agent
knows which module (root vs submodule N) the inputs belong to. Key→H3-title-prefix
(case-insensitive `startswith`, to absorb singular/plural and "Main …" phrasing):

| interface key            | H3 prefix matched      |
|--------------------------|------------------------|
| `inputs`, `variables`    | `main input variables` |
| `outputs`                | `main output`          |
| `examples`, `usage`      | `usage example`        |

An H3 sub-block runs from its `### ` heading to the next `###`/`##` (so `### Usage
Examples` naturally carries its `#### Example N` children).

**Scope of extraction.** A new keyword-only parameter `interface_scope` on
`filter_module_sections`:
- `"all"` (default, used by `get_module(sections=[…])`) — extract the matching H3(s) from
  **every** combined bundle (root + all submodules). Still far smaller than whole bundles.
- `"root"` (used by the orientation head, Change 2) — extract only from the root/main
  bundle (`## Root Module:` / `## Main Module:`), skipping `## Submodule N:` bundles.

**Matched/unmatched bookkeeping.** An interface key counts as matched if the exact H2
alias hit OR at least one combined bundle (respecting `interface_scope`) yielded an
extraction. Only truly-absent keys go to the "Requested sections not found" footer line
(subject to `silent_keys`, Change 2).

**Regression tests (required, from the report).** `s3-bucket`, `ecr`, `lambda` with
`sections=['inputs','examples']` must return: (a) no "Requested sections not found", and
(b) NOT the full bundle — assert the response excludes a section that lives in a combined
bundle but is not inputs/examples (e.g. the root `### Main Outputs` heading is absent, and
total length is materially below the whole-doc length). Plus a direct unit test on the
combined-bundle extractor.

### Change 2 — Inline compact ROOT inputs into the default orientation head (report addendum item 1)

**Problem.** The default `get_module(mod)` head returns prose only (features, use-cases,
submodules inventory, version pin) — no inputs. Workers see it is thin, then immediately
re-call `get_module(mod, sections=['inputs'])`: measured 12 redundant calls / 123,150
wasted chars, 100% concentrated in the xhigh workers. Folding the root inputs into the
default head removes the second call.

**Fix.** `orientation_head` additionally inlines the ROOT module's input table:
- Combined docs → the root bundle's `### Main Input Variables` H3 only (via
  `interface_scope="root"`, Change 1's mechanism).
- Split-toplevel docs → the single `## Main Input Variables` H2 (exact alias, already
  root-only).
Sizes are compact (root inputs measured 12–39 lines across the heavy modules: vpc 12,
eks 16, elasticache 18, lambda 39); the head stays far under the full-doc size.

**Best-effort — no spurious "not found".** 5/55 docs are pure submodule-collections with
NO root inputs (cloudwatch, ecs, fsx, iam, network-firewall). For these the head must
simply omit inputs — never emit "Requested sections not found: inputs". Realized via a new
keyword-only parameter `silent_keys: frozenset[str]` on `filter_module_sections`: keys in
this set are matched best-effort and, when unmatched, are dropped from the "not found"
footer line entirely. The head passes `silent_keys=frozenset({"features","use-cases",
"inputs"})` (all server-injected keys — they are defaults, not user requests).

The head keeps its current structure and order: version-pin hint, then core sections +
Key Features + Main Use Cases + Submodules inventory + **root inputs** + section-index
footer. Only `get_module` with no `sections` (and the submodule-address orientation head)
changes; explicit `sections=[…]` and `sections=["all"]` are unchanged except via Change 1.

**Tests.** For a combined module (e.g. vpc) and a split-toplevel module (e.g. redshift),
the default head contains the root `Main Input Variables` heading and at least one known
input row, and does NOT contain a submodule's input table. For a collection doc (e.g.
iam), the default head contains neither an inputs block nor a "not found" line.

### Change 3 — Broaden the grep hint from "names" to "names and shapes/types" (report addendum item 11)

**Problem.** The escalation guidance points the model at `grep_module_docs` mainly for
verifying resource/rule *names*. The one worker who repurposed grep for a *shape* question
is what fixed a shape miss. Widen the stated scope so the proven recovery path is used for
type/shape disambiguation too.

**Fix.** Pure wording, no logic. Update, consistently:
- the `filter_module_sections` footer honest-limits sentence (the "grep the live registry
  doc … using the Module ID" line) to name shape/type verification explicitly;
- the `grep_module_docs` tool description;
- the `tf-module` skill's grep-escalation hint if it phrases it as names-only (audit; edit
  only if present).

Assert the new phrasing appears in the footer via an existing get_module test.

## Explicitly out of scope for 0.20.0

- Trim non-top-1 `search_modules` keywords (report item 5a) — deferred: the only clean
  omission needs a wrap-serializer that re-triggers the FastMCP empty-`outputSchema`
  regression (the UpdateNoticeMixin saga); marginal char saving. Revisit when `expand_top`
  reshapes `SearchHit` anyway.
- No-confident-match / `module_exists` signal and `search_modules(expand_top=true)`
  (items 3, 4) — need a score-distribution spike; own spec.
- `.tf` source grep + build-time source bundling (KEEP item 5) — own release/spec.
- Background prefetch on `get_module` (KEEP item 7) — breaks the offline-curated-tools
  invariant; own spec.
- Completeness linter + doc edits (items 6–10) — that is 0.21.0.

## Invariants preserved

- **Index untouched.** No embedding change; golden set unaffected by construction.
- **No corpus edits.** Docs unchanged (0.21.0 does that).
- **No network, no new dependency.** All changes are in `tfmod_mcp_server.py` logic +
  wording + tests.
- **`sections=["all"|"full"|"everything"]`** still returns the complete document verbatim.
- **Core sections** (front-matter, Description, Module Information, Notes for AI Agents,
  Important Gotchas) remain always-included.
- Split-toplevel interface docs are byte-identical for `sections=['inputs']` (fallback
  never fired for them before or after).

## Files touched

- `src/tfmod_mcp_server.py` — `filter_module_sections` (new `interface_scope`,
  `silent_keys` params + H3 sub-section extraction helper), `orientation_head` (inline
  root inputs), footer wording, `grep_module_docs` description wording.
- `tests/integration/test_mcp_server.py` — over-fetch regression, head-inputs, collection
  no-noise, footer wording, split-toplevel unchanged.
- Version bump per the release process (`## Release Process` in CLAUDE.md): pyproject,
  both plugin manifests, `DEFAULT_IMAGE`, docker-compose image tag, README current-release
  image tags, CHANGELOG.
