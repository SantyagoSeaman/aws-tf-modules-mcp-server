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
- L2/L7/L8: a genuinely-absent capability with no lexical hit -> "low"; a clean
  query -> "high"; a near-tie -> "tie"; hint present for low/tie, absent for
  high. Extends `test_repro_pack.py` (removes the Repro-5 xfail). NOTE: the clean
  "low" example is `sagemaker`, not `cognito` — `cognito` earns a real (if
  incidental) keyword overlap because several unrelated modules list it as a
  related-service keyword, so it classifies as "tie". This is the two-signal
  classifier behaving correctly, not a bug; forcing it to "low" would require
  overfitting the threshold, which the Out-of-scope section forbids.
- L3: expand_top on a confident query populates top_module_doc; off by default;
  never populated when confidence != high.
- L5: sections=["submodules","inputs"] is scoped, not the full bundle;
  regression test on vpc.
- Full suite green; no index rebuild (none of these touch embeddings).

## Out of scope

Lever 9 (shipped). Index/ranker retuning toward any test pair (overfit).
Push / PR / merge / tag / publish (await explicit maintainer approval).

---

# RC2 revision (Run #8 measured, 2026-07-16)

The 0.22.0-rc container was measured (Run #8, 3A+3B Sonnet, same method as run
#7) and came out **worse**: A cost $24.48 -> $26.86 (+9.7%), doc calls 117 -> 143
(+22%), while payload chars fell 4.4%. Source: `tfmodsearch-improvements-2.md`
"Run #8 addendum". This section revises the design; the package version stays
`0.22.0` and the next test image is tagged `0.22.0-rc2`.

## The corrected objective: turns, not bytes

Measured across both runs' transcripts: **one extra tool-call turn costs ~$0.093
blended** ($0.047 early-session -> $0.129 late as context grows ~4x). The entire
payload diet (-51.8K chars) is worth **$0.004-0.09** — under 4% of the turn
delta. **Optimizing bytes-per-call while adding calls is a guaranteed net loss.**

Standing design gate for every future server feature (record in CLAUDE.md):
`value - (extra_turns x ~$0.09 x session_length_factor)`. The byte levers
(L1/L4/L6) stay — they are ~free and do not add turns — but they are worth
pennies; effort goes to turn-count.

## Tier 0 — correctness (independent of the cost model)

**C1. Scoped grep drops the enclosing nested-key name (defect #1).** An input
row is a single f-string `- name | type | default | description`
(`_format_input_row` in `tfmod_registry_docs.py`), but `type`/`description` can
be multi-line, so a `grep_module_docs(scope=["inputs"])` match landing on a
continuation line loses the `- <name>` header — the model back-fills a
plausible-but-wrong container name from the prose (run8: 2/3 A workers emitted
invalid HCL, `default_route_settings` vs real `stage_default_route_settings`).
Fix: `grep_document` (`tfmod_doc_grep.py`) carries the nearest enclosing
list-item. Add `enclosing: str | None` to `DocMatch`: when the matched line does
not itself start with `"- "`, walk backward (non-marker, same section) to the
nearest line starting with `"- "` and record it; render it in
`grep_module_docs_impl` output (e.g. an `under: <row>` breadcrumb) so the
container key is always present. Answer-agnostic; works for inputs/outputs/
resources uniformly.

**C2. Single-snapshot version consistency (defect #2).** `expand_top`'s inlined
`top_module_doc` said global-accelerator `3.0.1` while `results[].latest_version`
in the same payload said `3.0.0`; the wrong pin propagated to a final answer.
Root cause: the head's pin comes from `_version_pin_hint(d.text)` (re-parses the
doc body) while `results[].latest_version` is the separately-stored index
metadata field — a drift-safe metadata patch desyncs them. Fix: thread the
metadata version into the head on the expand_top path. `orientation_head(text,
version_override=None)` and `_version_pin_hint(text, version_override=None)`;
when `version_override` is set it is used verbatim instead of re-parsing.
`search_modules_impl` calls
`orientation_head(d.text, version_override=d.latest_version)` so the head pin and
the result field are the same string by construction. `get_module_impl` keeps the
re-parse (single source, no contradiction possible).

## Tier 1 — the turn levers

**T1. Remove the tie verdict and its imperative.** Measured net-negative: tie
fired on 55% of searches (41/74), the "fetch both" imperative was acted on
**0/41** and delivered **0/41** benefit (31/41 final = top-1 anyway), and it
provoked **+28 search reformulations**. Score-ratio carries no separating signal
(resolved and catalog-gap ties both span 1.0-2.3x). Delete the `"tie"` branch,
`SEARCH_NEAR_TIE_RATIO`, the ratio plumbing in the verdict, and the tie hint.
Verdict domain becomes `{"high", "low"}` only.

**T2. expand_top default-on for high confidence.** The one right-direction lever,
currently strangled (used by 1/6 workers; 16/23 calls suppressed by tie/low).
Counterfactual (fleet-wide expand_top, no tie) collapses ~42 turns ≈ -$3.9-4.2 ->
below the 0.21.0 baseline. Change the default to `expand_top=True`; it inlines
`top_module_doc` only when `confidence == "high"` (so a `low`/catalog-gap verdict
never inlines the wrong doc). The residency cost of the ~1.5K-char head is pennies
against $0.09/turn and the top hit is the final pick 31/41 — the trade is strongly
positive. Callers can still pass `expand_top=False` to suppress (pure-browse
searches). Gated by C2 (single-snapshot) so the inlined head can never contradict
the result row.

## Tier 2 — honest no-match (lands WITH Tier 1, not after)

Removing tie naively sends the 10/41 catalog-gap queries (which earned
*incidental* keyword overlap from unrelated modules listing the term) into
`"high"` -> expand_top would inline the wrong module. So the no-match detector
must get stronger in the same change.

**T3. Semantic-floor no-match.** Expose the absolute semantic signal the scorer
already computes but discards: `cos_raw` (`tfmod_search_lib.py:1142`) is the
per-doc cosine scaled to [0,1] **before** the per-query min-max — it is
comparable across queries, unlike the combined score. Add `sem_sim: float` to
`ScoredHit` (`sem_sim=float(cos_raw[i])`) and populate it in
`compute_scores_detailed`; `compute_scores` wrapper unchanged.

Classifier (`_classify_confidence`), preserving the working "not-lexical -> low"
path and adding the incidental-keyword catch:
```
top1_lexical = top1.exact_hit or top1.kw_overlap
if not top1_lexical:                       -> "low"   # semantic-only ceiling (as before)
elif not top1.exact_hit and top1.sem_sim < SEARCH_SEM_FLOOR:  -> "low"   # incidental-kw catalog gap (NEW)
else:                                      -> "high"
```
`exact_hit` always wins to `"high"` (a name match is decisive). No ratio anywhere.
`SEARCH_SEM_FLOOR` is a module constant, **provisional** and A/B-tuned by the
morning run — set an initial value (start ~0.88 on the [0,1] scale; e5 cosines are
compressed, band is narrow) and `logger.debug` the top-1 `sem_sim` on every search
so the run reveals the real catalog-gap-vs-match distribution. Do NOT tune it
toward any specific test pair.

**T4. Directional (not imperative) no-match hint.** The `low` verdict's
directional hints were followed 3/4; imperatives demanding paid calls get ignored
(and then narrated as done). Keep the `low` hint directional and non-committal:
name the nearest module, suggest `modules_list` to confirm absence or
`grep_module_docs` on that nearest module — no "you must fetch" imperative.

## Tier 3 — free bytes (zero turns; do because free, expect pennies)

**F1. Compress the get_module footer disclaimer.** The 764-char honest-limits
prose block (`footer_lines[1]` in `filter_module_sections`) is verbatim on 56/56
get_module calls (42.8K chars of pure repetition). Collapse to a 1-2 line
actionable pointer that keeps the load-bearing escalation (curated subset -> full
inputs/outputs/exact types + nested shapes via `grep_module_docs <Module ID>`;
resource-creation conditions in module source) and drops the repetition. Keep the
"Available sections" menu line and the omitted/unmatched lines unchanged.

**F2. Search-payload boilerplate.** The addendum notes ~19% of each search payload
duplicates the get_module header; with the tie hint deleted (T1) much of that
recurring text is already gone. Confirm what remains after T1; trim only obvious
verbatim repetition, no behavior change.

## Testing (RC2 deltas)

- C1: a synthetic inputs section with a multi-line `type` — a scoped grep match on
  a continuation line carries the enclosing `- <name>` row; a match on the header
  row itself has `enclosing=None`.
- C2: `search_modules_impl(expand_top=True)` on a high-confidence query — the
  version string in `top_module_doc` equals `results[0].latest_version` (patch the
  fixture doc's metadata field away from its body bullet to prove the override
  wins).
- T1: no verdict ever returns `"tie"`; `SEARCH_NEAR_TIE_RATIO` is gone; the
  near-tie fixture (elasticache/memory-db) now returns `"high"`. Remove/replace the
  tie tests in `test_retrieval_levers.py`.
- T2: default `search_modules_impl(query)` on a high-confidence query populates
  `top_module_doc`; a `low` query does not; `expand_top=False` suppresses it.
- T3: a genuinely-absent capability with only incidental keyword overlap and
  `sem_sim < SEARCH_SEM_FLOOR` -> `"low"`; a real single-keyword match with strong
  `sem_sim` -> `"high"`; an exact-name query -> `"high"` regardless of sem_sim.
- F1: get_module default head no longer contains the long disclaimer paragraph but
  still contains a `grep_module_docs` escalation pointer and the Module ID.
- Full suite green; **no index rebuild** (sem_sim is read from the existing
  embeddings at query time — embeddings untouched).

## Build

Tag the next test image `0.22.0-rc2`, run it on the same daemon port used for RC
testing. Package version stays `0.22.0` (this is still the unreleased 0.22.0
branch); no multi-file version-bump sprawl.

# RC3 revision (Run #9 measured, 2026-07-16)

Run #9 tested RC2 and **the forecast held**: A-fleet $22.72 (−$1.76 below the
0.21.0 baseline), get_module 56 → 3 calls (−94.6%), tie-driven reformulations
41 → 0, first all-perfect A selection, 12/12 honesty. The three headline levers
worked as designed. Model refinement carried forward: the inline *relocates*
get_module's bytes into the search response rather than deleting them, so
$/turn rose +7.6% while turns fell −39%; net still a large win because turns
dominate bytes 19–30×. Updated scoring formula:
`value − (Δturns × ~$0.09 × session_len) − (Δcontext_chars × ~$1.5/M)`.

RC3 is another **measured** candidate (not final): three residual "calibration
hygiene" items from Run #9's defect scan, all worth cents not dollars — fixed
for trust and context hygiene, not cost.

## #1 — decoupled expand_top inline gate (the only item with any cost)

Run #9: confidence banding is non-monotonic in the displayed `score` (probe:
score 3.91 → "high", 5.0 → "low"), and a catalog-gap query whose best
wrong-domain hit lands "high" drags a 13–17K-char irrelevant doc into context
via the inline — the entire +11% payload delta on absence-proof workflows.

The report proposed "make the band a monotonic function of absolute score".
**Rejected**: the displayed `score` is per-query min-max normalized on each
component, so it is NOT cross-query comparable — the no-keyword branch always
yields ~5.0 for its top hit (real match or gap alike), the log-damped keyword
branch scores systematically lower. A floor on absolute score would mislabel
every no-keyword semantic query "high". The "5.0 → low" is the confidence axis
working correctly (no lexical → semantic ceiling → gap); it only looks
incoherent against the non-comparable displayed number.

Instead: keep the two-band verdict unchanged and make the **auto-inline gate
stricter than the verdict** (`_should_inline_top`). Inlining a wrong 13–17K doc
is asymmetric-cost — far more than the one get_module turn it would save on a
real match — so it earns a stricter test: exact-name hit → always inline;
lexical-but-not-exact → inline only when it clears `SEARCH_SEM_FLOOR` AND
dominates rank-2 by `SEARCH_INLINE_SCORE_MARGIN` (within-query score gap;
evaluated only in the keyword branch, where the scale is consistent). Verdict
stays "high" (a real match exists); only the expensive inline is withheld on a
flat field. `SEARCH_INLINE_SCORE_MARGIN = 0.5` is PROVISIONAL — deliberately
small to preserve the measured turn savings; the debug log now emits
`score`/`score_gap`/`inline` per search for A/B refinement.

## #2 — render-time single-snapshot version, applied to ALL mentions

rc2 (C2) synced the pin *banner* with `results[].latest_version`, but the
curated doc *body* still carries its own `**Latest Version**` bullet that can be
stale (3 of 55 modules in Run #9 traffic) and contradict both the banner and the
metadata field in one response. `_reconcile_body_version` rewrites the body
bullet to the threaded snapshot at render time inside `orientation_head` (only
when an override is present; no override → body bullet is the snapshot, no-op).
Drift-safe by construction: emitted text only, embeddings untouched. This is the
only drift-safe fix — editing the .md body would force an index re-encode.

## #3 — word-boundary blurb clip

`_clip_blurb` hard-cut mid-word on the char cap, leaving a dangling partial word
in every non-top-1 result row. Clip on the last space instead
(`rsplit(" ", 1)[0]`), matching `extract_description`.

## Watch item (no server change)

Head-only orientation risk: 1 wrong leaf shape in 69 gradings (a worker
skeletoned a nested input without fetching `inputs`/`examples`). Not acted on;
if it recurs across runs, make the footer's "shapes live in inputs/examples"
pointer more prominent rather than inlining more content.

## Testing (RC3 deltas)

- #1: `_should_inline_top` fixtures — exact → always; lexical+floor+dominant →
  inline; lexical+floor+flat-field → withheld though verdict stays "high";
  lexical below floor → withheld; non-lexical → withheld; single lexical hit →
  inline. Integration: a monkeypatched flat high-confidence field yields
  `confidence == "high"` with `top_module_doc is None`.
- #2: `_reconcile_body_version` rewrites/no-ops correctly; `orientation_head`
  with an override reconciles the body bullet, not just the banner; the inlined
  head's body bullet equals `results[].latest_version`.
- #3: `_clip_blurb` clips on a word boundary (next source char is whitespace);
  the first-sentence branch is unaffected.
- Full suite green; **no index rebuild**.

## Build

Tag the next test image `0.22.0-rc3`, run it on the same daemon port as RC2.
Package version stays `0.22.0`.

# RC4 revision (Run #10 measured, 2026-07-16)

Run #10 tested RC3 and confirmed the hygiene fixes: 0 score/verdict inversions
in 74 pairs, 74/74 version triples consistent (the rc2 desync class is extinct),
no mid-word cuts, and the head-only watch item closed (0 recurrences). RC3 was
the cheapest A-fleet of ten runs ($21.18) with the first all-PASS judged
selection. Two meta-findings reshaped the backlog:

1. **Output consistency is a first-class cost lever.** The headline saving came
   NOT from the payload trim but from consumer thinking tokens: A-side output
   halved (172K -> 86K), carrying -$1.29 of -$1.54; the turns-first formula
   alone predicted the wrong sign. New term: `- Δconsumer_thinking × $15/M`.
   Principle: **every internally inconsistent field is paid for twice -- once in
   bytes, once in the consumer's tokens spent deciding which field to trust.**
   This is why the RC3 version-desync fix mattered far beyond its byte count.

2. **The RC3 inline gate was the right intuition, wrong mechanism.** Run #10
   asked to reverse two RC3 decisions.

## #1 + #2 — capability-aware unified verdict (reverses RC3's decoupling)

Run #10 defect 1: the RC3 gate keyed on the score margin, but the failure mode
is CAPABILITY mismatch. A wide-margin score win still inlined a module whose doc
has zero occurrences of the query's central capability term (a 12K-char doc,
4/6 repro; a near-miss where the correct module sat one rank behind an
adjacent-domain giant). A score-gap gate is structurally blind to this.

Run #10 defect 2: RC3 decided the verdict and the inline with two DIFFERENT
signals -- it suppressed the inline on thin-margin CORRECT top-1s (4 of 7 fleet
get_module calls were this pattern) while wide-margin WRONG top-1s sailed
through, and the docstring still promised "high => doc inlined". A contract the
docstring states and the server breaks is a trust defect.

Rejected the report's literal "monotonic function of absolute score" wording:
the displayed `score` is per-query min-max normalized and NOT cross-query
comparable (already the RC2/RC3 finding), so a floor on it misbehaves. Instead:

- **`_capability_covered(query, index, doc_index)`** (RC4 #1): take the query's
  most salient token (highest BM25 IDF, skipping a small generic-infra
  stopword set) and require it to appear in the top-1 candidate's
  name/keywords/doc text. Absent -> the query is not covered here. Reads only
  query <-> candidate (answer-agnostic, ranker untouched); fails open when there
  is no salience signal so it can only ever DEMOTE a positively-uncovered hit.
- **Unify verdict and inline** (RC4 #2): the classifier now takes the query and
  index, and its lexical-non-exact branch requires capability-overlap (primary)
  AND the RC2 semantic floor (secondary, incidental-keyword guard). Deleted
  `_should_inline_top` and `SEARCH_INLINE_SCORE_MARGIN`; the caller inlines iff
  the verdict is "high", so the docstring contract holds again. A wrong-domain
  top hit is demoted BEFORE it can drag its doc into context, and a thin-margin
  correct hit (capability-covered) inlines as it should.

Live sanity (production weights): real lexical-non-exact matches
(dns/cdn/cache/kubernetes/queue/secrets) stay high+inline; a forced wrong-domain
top-1 (query central term absent from the doc) demotes to low+no-inline. No real
match in the probe set was newly demoted; the pre-existing non-lexical gaps
(load-balancer/container-registry, curated-keyword mismatches) are unchanged.

## #4 — string hygiene

- **Front-matter leak**: `extract_description` skipped the `---` fences as
  horizontal rules but picked up the YAML body lines (`module_name:`,
  `keywords:`) as content -- only `wafv2.md` opens with front-matter, so its
  search-result description leaked raw YAML. `_strip_yaml_frontmatter` drops the
  leading block first. Pure code fix, no index effect.
- **S3 SSE nested shape**: the `server_side_encryption_configuration` input row
  now names the canonical nested keys (`rule` >
  `apply_server_side_encryption_by_default` > { `sse_algorithm`,
  `kms_master_key_id` }, `bucket_key_enabled`), matching the completeness-pass
  style, so a grep of the curated doc finds them. Re-encoded s3-bucket only;
  because the row sits past the e5 ~512-token truncation window, its embedding
  vector is byte-identical -- **zero embedding drift**, golden set held; BM25
  avgdl shifts marginally (5420.09 -> 5420.51) with no top-3 reshuffle.

## Deferred: #3 (band knife-edge)

Max-low 4.01 vs min-high 4.06 -- no inversions, but equivalent phrasings can
straddle the 0.05 gap. Deferred: with the verdict now gated on capability
coverage (a token-presence signal) rather than a score threshold, the score
knife-edge is expected to lose most of its bite; revisit only if Run #11 still
shows phrasing-luck verdicts.

## Testing (RC4 deltas)

- #1: `_capability_covered` fixtures (central term present/absent, match in
  keywords/name, fail-open without salience). Classifier: lexical-non-exact with
  a capability miss -> "low" even with strong sem_sim.
- #2: `top_module_doc` present iff `confidence == "high"` across live queries; a
  forced wrong-domain top-1 -> low + no inline; `expand_top=False` still
  suppresses. `_should_inline_top`/`SEARCH_INLINE_SCORE_MARGIN` gone.
- #4: `extract_description` strips front-matter (wafv2 no longer leaks YAML);
  the s3-bucket SSE row names the canonical child keys; re-encode is
  vector-byte-identical for every doc.

## Build

Tag the next test image `0.22.0-rc4`, run it on the same daemon port as RC3.
Package version stays `0.22.0`.
