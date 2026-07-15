# 0.22.0 Retrieval Levers — Design

## Goal

Cut retrieval-side token cost (the ~99% of billed tokens, dominated by cache
re-billing of resident docs) with structural, answer-agnostic changes to the
three curated tools. Source: `tfmodsearch-improvements-2.md` (N=3 run #7 against
the real shipped 0.21.0). Every change helps any user on any module/query; none
tunes toward the 23-requirement test set.

## Guiding finding

~99% of billed tokens are retrieval-side and the real multiplier is re-billing:
a fetched doc is re-read as `cache_read` on every later turn (avg 6-26x, up to
~494x). So every byte removed from a `get_module` / `modules_list` /
`search_modules` payload is multiplied by residency. Payload size is the lever.

Lever 9 (corpus-wide completeness lint) already shipped in 0.20.0
(`scripts/lint_doc_completeness.py` + guard + allowlist) and is out of scope.

## Levers (all in this release)

### Tier 1 — pure size wins (no index change)

**L1. Lean `modules_list`.** 31,516 chars, byte-identical every call. Add
`detail: Literal["compact","full"] = "compact"`. Compact item carries
`module_name`, `module_id`, `latest_version`, and a clipped one-line `purpose`
(<=120 chars) — drops the 12-18-item `keywords` array and the long description
that make up the bulk. `detail="full"` returns the current full item verbatim.
`module_id`/`latest_version` stay in compact (they are the grep-chaining
coordinates). Breaking change to the default shape; documented in CHANGELOG.

**L4. Claw back the default-head input-table regression.** The 0.20.0
double-fetch fix inlined the whole `### Main Input Variables` table into the
default head (+31% mean head growth, +5.5% aggregate chars). Cap the inlined
table to the essential rows — inputs with no default (required) — and append a
one-line pointer `(+N optional inputs -> get_module(sections=["inputs"]))`. Full
table stays behind `sections=["inputs"]`. If a module has no required inputs,
keep the first ~8 rows so the head table is never empty (Repro 4 guard: head
still contains a real `| \`` row). Applied only to the default head, not to
explicit `sections=["inputs"]`.

**L6. Trim non-top-1 metadata in `search_modules`.** Full `keywords` +
description only on `results[0]`; rank>=2 hits get `keywords=[]` and a
description clipped to the first sentence (<=140 chars). Nothing in any
transcript reads a non-top-1 keyword array.

### Tier 2 — search confidence signal (L2 + L7 + L8, one feature)

Raw combined score is not comparable across queries, and a single top1/top2
ratio conflates "absent" with "contested". The robust classifier needs two
signals the scorer currently collapses into one number:

1. top1/top2 score ratio -> confident (big gap) vs ambiguous (small gap);
2. whether top-1 earned a lexical component (exact-name match `w_exact` or any
   keyword overlap) -> a real match exists vs semantic-only ceiling (absent).

Implementation: refactor the scoring core into
`compute_scores_detailed(...) -> list[ScoredHit]` where
`ScoredHit = (score, doc_index, exact_hit: bool, kw_overlap: bool)`.
`compute_scores` becomes a thin wrapper `[(h.score, h.doc_index) for h in ...]`
(backward compatible for CLI and other callers).

`search_modules_impl` classifies:
- `top1_lexical = top1.exact_hit or top1.kw_overlap`
- `ratio = top1.score / top2.score` (inf when no rank-2 or rank-2 score == 0)
- verdict: `not top1_lexical` -> `"low"`; elif `ratio < SEARCH_NEAR_TIE_RATIO`
  -> `"tie"`; else `"high"`.

`SearchOutput` gains `confidence: str` (always present) and `hint: str | None`
(dropped from JSON when None, via the existing None-drop mechanism). For `low`,
hint = "no confident catalog match; confirm with modules_list or try
grep_module_docs on <nearest> for '<term>'" (L8 — nearest = top-1 module). For
`tie`, hint names the contested top-2 (L7).

Threshold `SEARCH_NEAR_TIE_RATIO = 2.5` is a module-level constant — R15
(elasticache 11.32 vs memory-db 4.90 = 2.3x) flags `tie`; clean queries clear
>3x and stay `high`. Thresholds are indicative (N=3) and validated by the
morning A/B run.

### Tier 3 — depends on Tier 2

**L3. `search_modules(expand_top=False)`.** Opt-in. When `True` and
`confidence == "high"`, inline the top-1 orientation head into
`SearchOutput.top_module_doc: str | None` (dropped when None) — one call replaces
the confident search->get_module pair. Default `False` so it never bloats normal
search responses (which would fight the re-bill lever). Docstring tells agents to
pass it when they intend to immediately fetch the top hit.

**L5. Submodule-level `sections` scoping.** `sections=["submodules","inputs"]`
returns full submodule bundles (18,972 chars). (a) Note in the tool description
that submodule names are already in the default head, so an existence check needs
no `sections` call. (b) When a submodule section is requested, return only that
submodule's requested sub-block, not all submodules bundled. Add a regression
test either way.

## Error handling

- `detail` outside {compact,full} -> validation error from the Literal type.
- Empty / single-result search -> `confidence="high"`, `hint=None`, ratio=inf.
- Head input-table cap must be a pure post-process on the assembled head; on any
  parse ambiguity (no recognizable table) it returns the head unchanged.

## Testing

- L1: modules_list compact omits keywords + clips purpose; full restores them;
  count unchanged; module_id/latest_version present in both.
- L4: default head for the 5 regressed modules is smaller than 0.21.0 and still
  carries a real input row + the "+N optional" pointer; sections=["inputs"] full
  table unchanged.
- L6: search rank>=2 hits have empty keywords + clipped description; rank-1 full.
- L2/L7/L8: cognito -> "low"; a clean query -> "high"; a near-tie -> "tie";
  hint present for low/tie, absent for high. Extends `test_repro_pack.py`
  (removes the Repro-5 xfail).
- L3: expand_top on a confident query populates top_module_doc; off by default;
  never populated when confidence != high.
- L5: sections=["submodules","inputs"] is scoped, not the full bundle;
  regression test on vpc.
- Full suite green; no index rebuild (none of these touch embeddings).

## Out of scope

Lever 9 (shipped). Index/ranker retuning toward any test pair (overfit).
Push / PR / merge / tag / publish (await explicit maintainer approval).
