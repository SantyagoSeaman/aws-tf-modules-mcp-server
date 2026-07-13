# Design: submodule reachability + a sufficient orientation head (A1 + A3 + parent keyword-enrichment)

- **Date**: 2026-07-13
- **Status**: Approved (design), pending implementation
- **Author**: brainstormed with the maintainer
- **Companion**: `orientation-and-submodule-design.md` (experiment writeup, external vault), `doc-escalation-design.md` (depth ladder)

## 1. Summary & Motivation

The v3 A/B experiment showed TFModSearch matches the HashiCorp registry MCP on
module-selection accuracy at ~half the cost — but **submodules are unreachable**.
`search_modules` indexes one `DocRecord` per top-level `.md` file
(`build_index` globs `*.md`; `tfmod_search_lib.py:772-779`), and submodules are
H2 sections *inside* the parent file. So the correct answer to a requirement like
R17 ("an IAM role assumable via GitHub Actions OIDC" → `iam//modules/iam-role`) can
never be a direct hit; the agent must know to open the parent `iam` doc and read
down to the submodule — an extra, fallible hop.

This change closes that hop with the two cheapest, **index-safe** levers from the
experiment writeup, plus one gated enrichment:

- **A1** — surface the `## Submodules` **inventory inline** in the orientation head
  (name + purpose + source string + features), so the moment search lands on the
  parent, the head answers "here are the submodules, pick one, here's the source to
  pin". Pure head-assembly change.
- **A3** — `get_module` accepts a **submodule address** (`iam//modules/iam-role`)
  and returns an orientation head **scoped to that submodule's section**, instead of
  the whole 895-line `iam.md`. Pure resolver change.
- **Parent keyword-enrichment (gated)** — add submodule short-names / capability
  terms to the parent doc's `**Keywords**` bullet so the parent ranks higher on
  submodule-specific, name-absent queries. Requires an index rebuild → **shipped only
  if the golden set stays green** (see §5).

Deliberately **excluded** (per maintainer decision): **A2** (index each submodule as
its own searchable record). It is the only lever that changes the retrieval surface
(54 → ~111 records, ranking redesign, forced rebuild) and its marginal value over
A1+A3 is gated on a v4 measurement that does not exist yet. See §6.

## 2. Goals / Non-Goals

**Goals**
- Make a submodule reachable in **≤ 1 extra `get_module` call** once search lands on
  the parent (A1), and in **1 call** when the agent already knows the address (A3).
- Keep the change **index-safe by default**: A1 and A3 touch only server code and
  ship regardless. No embedding drift risk for the core.
- Give parents a stronger keyword signal for submodule queries **without** blowing up
  the index — behind a golden-set gate.

**Non-Goals (YAGNI)**
- A2 (submodules as index records) — deferred, evidence-gated on v4.
- B1/B2 (key-inputs subset + synthesized `module {}` skeleton in the head) — separate
  follow-up; needs a new inputs-table parser (`ModuleInfo` carries no inputs today).
- Physical file split of multi-submodule docs — rejected (breaks packaging, the
  `test_doc_schema.py` per-file schema, `Module ID` plumbing, and authoring).
- Any change to `grep_module_docs` / the source tier.

## 3. Decisions (from brainstorming)

| Aspect | Decision |
|---|---|
| Split mechanism (if A2 ever) | **Index-time logical split only** — never physical file split |
| A1 scope | Inline **only** the exact `## Submodules` inventory heading — NOT the `## Submodule N:` deep-dives (those would blow up the head) |
| A1 data source | The inventory **already** carries per-submodule Purpose + Source + Features (verified in `iam.md:55`); zero doc edits for A1 |
| A3 address forms | `<name>//modules/<sub>` and full `<ns>/<name>/<provider>//modules/<sub>`; `//` is the sentinel |
| A3 output | version-pin hint + core sections + the matched `## Submodule N: <sub>` section (reuses `filter_module_sections`) |
| A3 miss | Unknown `<sub>` → core sections + footer that lists every real submodule title (graceful, no error dump) |
| Enrichment gate | Rebuild index → full golden set (`test_all_modules_searchable`, 169) must stay 100%; else defer enrichment, ship A1+A3 |
| Version | minor bump 0.13.0 → **0.14.0** |

## 4. Design detail

### A1 — inventory inline in the head
`orientation_head` today assembles `filter_module_sections(text, ["features",
"use-cases"])` + a version-pin hint (`tfmod_mcp_server.py:1042-1056`).
`_ORIENTATION_KEYS = ("features", "use-cases")` (`:774`).

The obvious "add `submodules` to the keys" is **wrong**: the `submodules` alias maps
to canonical `Submodules` and `filter_module_sections` deliberately expands that to
*any* `title.lower().startswith("submodule")` (`:866`) — for iam that drags in all 8
full deep-dive sections (lines 115→832). The head must show **only** the compact
`## Submodules` inventory.

Fix: add an `extra_exact_titles` keyword-only parameter to `filter_module_sections`
that includes sections whose title is an **exact** (case-insensitive equality) match —
the same mechanism as `_CORE_SECTIONS`, but caller-supplied. `orientation_head` passes
`extra_exact_titles=("Submodules",)`. Exact "Submodules" (plural) matches the inventory
and never the "Submodule N: …" deep-dives. Present only when the doc has that heading
(37/54 docs); absent otherwise, no footer noise.

### A3 — `get_module(submodule address)` → scoped head
`_parse_submodule_address(identifier)`:
- Returns `None` if `//` not present (existing behaviour unchanged).
- Splits on `//`; right side → last path component = `<sub>` (`modules/iam-role` →
  `iam-role`); left side → parent locator.
- Normalises the parent to a **module name**: if it contains `/` it's a `module_id`
  (`terraform-aws-modules/iam/aws` → middle part `iam`), else it's already a name.

`get_module_impl` intercepts a submodule address **before** the normal resolver
(which would treat `iam//modules/iam-role` as a file path and fail). It fetches the
parent's full text via `get_module_documentation(parent_name)`, then returns
`_version_pin_hint(text)` + `filter_module_sections(text, [sub] (+ any explicit
sections))`. That yields parent context (Description / Module Information / Notes /
Gotchas) + the one submodule section. Reuses everything; no new assembly path.

### Parent keyword-enrichment (gated)
For the 17 docs that carry `## Submodule N:` sections, add the submodule short-names
and 1–3 salient capability terms to the parent's `**Keywords**` bullet (e.g. `iam`
gains `iam-role, oidc-provider, irsa, service-account, github-actions`). This feeds
the keyword-IDF + exact-keyword signals (`d.keywords`) and, because `d.text` is the
whole file, also nudges the embedding toward submodule queries. Focused on the big
multi-submodule parents where dilution is worst: iam(8), cloudwatch(13), eks(6),
s3-bucket(5), fsx(4), ecs(4), route53(3).

## 5. The index-rebuild gate (the one real risk)

`parse()` sets `body = text` (full file) and `build_index` encodes `[d.text …]`, so
editing any keyword bullet changes an embedding. Memory `project_index_embedding_drift`
records that a full rebuild post-0.11.0 drifted e5 embeddings and broke the golden set
(0.11.1 deliberately patched `latest_version` in place to avoid a rebuild). Therefore:

1. **Control rebuild** — rebuild the index with **no doc changes**; run
   `test_all_modules_searchable` (169) + model comparison. This directly tests whether
   the committed `.pkl` is reproducible from current deps.
2. If control is **green** → apply enrichment, rebuild, re-run the golden set. Keep the
   enriched index **only if it stays 100%**.
3. If control (or the enriched rebuild) **drifts** → the index is not safely
   reproducible in this release. **Ship A1 + A3 alone**; move enrichment to a dedicated,
   carefully-validated index-migration change. A1+A3 need no rebuild and are unaffected.

A1 and A3 are independent of this gate and ship in 0.14.0 unconditionally.

## 6. Why A2 is out of scope (for the record)

- 54 → ~111 records (57 `## Submodule N:` sections, skewed: cloudwatch 13, iam 8,
  eks 6, s3-bucket 5). Doubles the retrieval surface.
- "Weight tuning" is really a ranking **redesign**: bare-name "IAM" must still return
  the parent (`w_exact` protects it), and the parent contains submodule text so parent
  + own-submodule crowd the top-k → needs a dedup rule.
- Forces a rebuild (drift) + a golden-set **expansion** with submodule-target queries.
- Its unique win over A1+A3 — beating semantic dilution in big parents — is exactly
  what a name-absent v4 run would measure. Build A2 only if v4 shows the dilution costs
  selection accuracy. No such data yet.

## 7. Testing strategy

- **A1**: orientation head of a submodule-bearing doc (iam) contains the `## Submodules`
  inventory and its source strings, but **not** the deep-dive `## Submodule N:` bodies;
  a doc without submodules is unchanged.
- **A3**: `get_module_impl("iam//modules/iam-role")` returns a scoped head containing the
  iam-role section + version-pin hint, not the other 7 submodules; the full-id form
  resolves identically; an unknown submodule degrades gracefully.
- **`_parse_submodule_address`**: unit table (name form, id form, `modules/` prefix
  stripping, non-address returns `None`).
- **Schema guard**: extend `test_doc_schema.py` — every doc with a `## Submodules`
  inventory has it surfaced by the orientation head.
- **Enrichment** (only if it ships): `test_all_modules_searchable` stays 100%; the
  enriched parents are still found by their own name.

## 8. Rollout

Minor release 0.14.0. Version bump in `pyproject.toml` + both plugin manifests + `uv.lock`.
CHANGELOG entry. README `get_module` section documents the submodule-address form and the
inline inventory. CLAUDE.md (local, gitignored) updated. If enrichment ships, the committed
index `.pkl` is replaced and the change note flags the rebuild.
