# 0.22.0 Retrieval Levers Implementation Plan

> **For agentic workers:** TDD per task, commit each. Steps use checkbox syntax.

**Goal:** Ship L1, L4, L6 (Tier 1), L2/L7/L8 (Tier 2), L3, L5 (Tier 3) from the
2026-07-15 spec. No index rebuild — none touch embeddings.

## Global Constraints

- No apostrophes / contractions in commit messages (heredoc breakage).
- No push / PR / merge / tag / publish without explicit maintainer approval.
- Never full-rebuild the index (embedding drift breaks the golden set).
- Full suite green before finishing: `pytest tests/ -q`.

---

### Task 1 (L6): trim non-top-1 metadata in search_modules
- Test: rank>=2 SearchHit has `keywords == []` and `len(description) <= 141`;
  rank-1 keeps full keywords + description.
- Impl: in `search_modules_impl` build loop, gate keywords/description by index.

### Task 2 (L1): lean modules_list with detail param
- Test: `modules_list_impl(state, detail="compact")` items omit keywords, carry
  module_id/latest_version/clipped purpose; `detail="full"` restores keywords;
  count unchanged.
- Impl: `ModuleListItemCompact` model; `detail` param on impl + tool; clip
  purpose to 120 chars.
- Update existing modules_list tests to the new default shape.

### Task 3 (L4): cap default-head input table
- Test: default head for s3-bucket/vpc/elasticache/apigateway-v2/opensearch is
  shorter than the uncapped table and still contains `| \`` and `optional inputs`
  pointer; `sections=["inputs"]` unchanged.
- Impl: `_cap_head_input_table(head)` post-process in `orientation_head`; keep
  no-default rows, else first ~8; append pointer; return unchanged on no table.

### Task 4 (L2/L7/L8): search confidence signal
- Test (extends test_repro_pack): cognito -> "low"; clean query -> "high";
  near-tie -> "tie"; hint present for low/tie, absent for high. Remove Repro-5
  xfail.
- Impl: `ScoredHit` namedtuple + `compute_scores_detailed`; `compute_scores`
  wraps it; `SEARCH_NEAR_TIE_RATIO=2.5`; classify in `search_modules_impl`;
  `SearchOutput.confidence` + `hint`; extend mixin None/empty-drop for hint.

### Task 5 (L3): expand_top
- Test: `search_modules_impl(q, expand_top=True)` on a confident query sets
  `top_module_doc`; default off; never set when confidence != "high".
- Impl: `expand_top` param; inline `orientation_head` of top-1 when high.

### Task 6 (L5): submodule-section scoping
- Test: `get_module_impl('vpc', sections=['submodules','inputs'])` is smaller
  than the full submodule bundle and still names the submodules.
- Impl: scope submodule sub-block extraction in `filter_module_sections`;
  docstring note that submodule names are already in the default head.

### Task 7: version bump + CHANGELOG + docs
- Bump 0.21.0 -> 0.22.0 across pyproject, both plugin.json, launcher
  DEFAULT_IMAGE, docker-compose, README current-release tags; CHANGELOG entry.
- Full suite green.

### Task 8: self-review + local RC image on :8766
- Opus review of full branch diff vs spec.
- Build `ghcr.io/santyagoseaman/tfmodsearch:0.22.0-rc` locally; stand up on 8766
  (leave 0.21.0 on 8765 untouched) for the morning A/B.
