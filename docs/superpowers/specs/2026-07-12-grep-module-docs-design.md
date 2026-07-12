# Design: `grep_module_docs` — live registry-docs grep tool

- **Date**: 2026-07-12
- **Status**: Approved (design), pending implementation plan
- **Author**: brainstormed with the maintainer

## 1. Summary & Motivation

TFModSearch today serves a **curated, offline, AWS-only** catalog: `search_modules`
(hybrid semantic search), `get_module` (compact curated doc), `modules_list`
(catalog). Its main weakness is staleness — module APIs change between major
versions, and the shipped docs are a point-in-time snapshot with no version axis.

`grep_module_docs` closes that gap. It fetches the **full, current documentation
for any Terraform Registry module** (optionally pinned to a specific version),
caches it, and runs a **regex grep** over the assembled text, returning only the
matching lines with a few lines of context — the way the internal Grep tool
works. A single registry module's docs are large (the `vpc` root README alone is
~107 KB / ~27k tokens, plus 236 inputs, 119 outputs, submodules and examples), so
dumping the whole document into context is not viable. Grep is the point: pinpoint
retrieval (e.g. "what is the exact name/default of the NAT-gateway variable in
6.6.1?") without flooding the context window.

This is a new, self-contained tool over the **entire registry**, complementary to
the existing AWS-only curated tools.

## 2. Goals / Non-Goals

**Goals**
- Fetch full docs for any registry module by coordinates, optionally version-pinned.
- Assemble everything (readme + inputs/outputs/resources + submodules + examples)
  into one deterministic, greppable text.
- Regex grep with context lines, returning only matches (server-side grep).
- Disk cache: pinned versions cached forever (immutable), `latest` cached with a TTL.
- Make the chain **discoverable**: surface `module_id` (+ `latest_version`) as
  structured fields in `search_modules` / `modules_list` so an agent can go
  `search_modules → grep_module_docs` without guessing coordinates.
- Zero new runtime dependencies; keep the rest of the server offline.

**Non-Goals (YAGNI)**
- Registry **providers** (a different endpoint) — modules only.
- Semantic search over live docs (that stays the curated index's job).
- A separate `fetch`/`grep` tool split (single tool; see §13 for the future option).
- Serving stale cache on network failure (error out with guidance instead).

## 3. Decisions (from brainstorming)

| Aspect | Decision |
|---|---|
| Doc source | Terraform Registry API `/v1/modules/{ns}/{name}/{provider}[/{version}]` |
| Module scope | Any registry module via coordinates `namespace/name/provider` (+ optional version) |
| Greppable doc | Everything assembled into one text (readme + inputs/outputs/resources + submodules + examples) |
| Match model | Single regex `pattern`, case-insensitive by default, symmetric context lines |
| Cache policy | Pinned version = forever (immutable); `latest` = TTL (default 24h) + `refresh` flag |
| Decomposition | One tool `grep_module_docs` (fetch + assemble + cache + grep) |
| `module_id` chaining | Surface `module_id` + `latest_version` in `search_modules` / `modules_list`; store an explicit `Module ID` bullet in each doc header |

## 4. Tool API

```python
grep_module_docs(
    module_id: str,              # "namespace/name/provider", e.g. "terraform-aws-modules/vpc/aws"
    pattern: str,                # regex (Python re)
    version: str | None = None,  # None = latest
    case_sensitive: bool = False,
    context_lines: int = 2,      # lines before AND after each match (0..20), like -C
    scope: list[str] | None = None,  # restrict parts: root, inputs, outputs, resources,
                                     # submodules, examples (default: all)
    max_matches: int = 50,       # cap on returned matches (token budget)
    refresh: bool = False,       # bypass cache and refetch
) -> GrepOutput
```

### Output schema

```python
class GrepMatch(BaseModel):
    section: str        # "root/readme", "root/inputs", "submodule:flow-log/readme",
                        # "example:complete/readme", ...
    line_number: int    # 1-based line within the assembled document
    line: str           # the matching line
    before: list[str]   # up to context_lines preceding lines
    after: list[str]    # up to context_lines following lines

class CacheInfo(BaseModel):
    hit: bool
    fetched_at: str            # ISO-8601 timestamp of the underlying fetch
    policy: str                # "pinned" | "latest-ttl"

class GrepOutput(BaseModel):
    module_id: str
    resolved_version: str      # concrete version actually served (never "latest")
    source_url: str            # registry URL of the resolved module version
    total_matches: int         # matches found before max_matches cap
    returned_matches: int
    truncated: bool            # total_matches > max_matches
    cache: CacheInfo
    matches: list[GrepMatch]
    available_sections: list[str]  # always the full list of section labels in the
                                   # assembled doc, so the agent can refine pattern/scope
                                   # (especially useful when total_matches == 0)
```

## 5. Document Assembly

One HTTP call returns the whole module detail (root + submodules + examples). We
render it into a single deterministic text. Section-boundary markers (`===== … =====`)
double as human structure and as the source of each match's `section` label.

```
===== MODULE terraform-aws-modules/vpc/aws @ 6.6.1 =====

===== ROOT README =====
<root readme markdown, verbatim>

===== ROOT INPUTS =====
- name | type | required|default | description        (one line per input)

===== ROOT OUTPUTS =====
- name | description

===== ROOT RESOURCES =====
- aws_vpc.this (managed)

===== SUBMODULE: flow-log =====
--- readme ---
<submodule readme>
--- inputs ---
- name | type | required|default | description
--- outputs ---
- name | description

===== EXAMPLE: complete =====
<example readme>
```

Rendering `inputs`/`outputs` as one line each is a deliberate feature: grepping a
variable name (`enable_nat_gateway`) returns its row — type, default, description —
not just prose mentions. `scope` restricts which of these blocks are grepped
(default: all).

Assembly is pure and deterministic given the API JSON; it is unit-tested against a
committed fixture.

## 6. Grep Semantics

- Compile `pattern` with Python `re`, adding `re.IGNORECASE` unless `case_sensitive`.
- Walk the assembled text line by line (restricted to `scope` blocks if given).
- For each matching line collect `context_lines` before/after.
- **Overlapping/adjacent matches merge** into one block (ripgrep-style) to avoid
  duplicated context; `total_matches` still counts logical matches.
- Cap returned matches at `max_matches`; set `truncated` accordingly.
- Invalid regex → `re.error` caught, returned as a clear error message.
- Zero matches → empty `matches`, `total_matches == 0`, and `available_sections`
  filled so the agent can adjust `pattern`/`scope`.

The grep engine is a pure function `grep_document(text, pattern, *, case_sensitive,
context_lines, scope, max_matches) -> (matches, total, sections)`, independent of
network and cache, and fully offline-testable.

## 7. Cache Design

- **Location**: `${TFMODSEARCH_CACHE_DIR:-${XDG_CACHE_HOME:-~/.cache}}/tfmodsearch/registry_docs/`,
  overridable via `config.yaml` (`doc_cache_dir`). Stdlib only.
- **Entry format**: one JSON file per entry,
  `{namespace}__{name}__{provider}__{version}.json`, containing
  `{module_id, resolved_version, assembled_text, fetched_at}`.
- **Policy**:
  - Pinned version → immutable → cached forever.
  - `latest` (version omitted) → stored under a `…__latest.json` entry carrying
    `fetched_at`; a hit within `doc_cache_ttl_hours` (default 24) is served from
    cache, otherwise refetched. On every `latest` fetch we ALSO write a pinned
    entry under the concrete `resolved_version`, so a later pinned request for that
    version is a hit.
  - `refresh=True` bypasses the cache and refetches (updating both entries).
- **In-memory layer**: a small per-process LRU over assembled texts avoids
  re-reading/re-assembling from disk within a session (mirrors the existing
  `_MODEL_CACHE` pattern).

## 8. Error Handling

| Condition | Behavior |
|---|---|
| `module_id` not exactly 3 `/`-parts | `ValueError` with a correct example |
| Module not found (HTTP 404) | Clear "module not found" error |
| Version not found | Fetch `/versions`, error listing available versions (mirrors `get_module`'s suggestion pattern) |
| Invalid regex | Catch `re.error`, friendly message |
| Network failure / timeout (25s) | Error explaining the tool needs network; mention `refresh` and that pinned versions are cached |
| No matches | Not an error; empty matches + `available_sections` |

## 9. `module_id` / `latest_version` Integration

**Doc header change.** No doc uses YAML front-matter; all metadata lives in the
`## Module Information` prose section, parsed by regex
(`_parse_module_information_section`). We add an explicit machine-readable bullet
right after `Module Name`:

```
- **Module Name**: `vpc`
- **Module ID**: `terraform-aws-modules/vpc/aws`
- **Source**: `terraform-aws-modules/vpc/aws`   # kept; this is the terraform `source =` value
- ...
- **Latest Version**: 6.6.1                       # already present
```

`Module ID` is preferred over deriving from `Source` because `Source` is
semantically the Terraform `source` argument and carries a `//modules/…` suffix for
submodules; a dedicated field is always the clean root coordinate.

**Parser.** Add a regex for `**Module ID**` (mirroring `**Module Name**`) → new
`DocRecord.module_id`; parse the existing `**Latest Version**` bullet → new
`DocRecord.latest_version`. Fallback: if `Module ID` is absent, derive from the
first root `**Source**` line (strip any `//…`). New `DocRecord` fields default to
`""` so **older pickled indices still load**.

**Models.** Add `module_id: str` and `latest_version: str` to `SearchHit` and
`ModuleListItem`.

**Backfill.** A one-time script inserts the `Module ID` bullet into all 54 docs
(value taken from each doc's root `**Source**`). Update `modules/module_template.md`
and the `add-module` maintainer skill so new docs carry the field going forward.

**Index rebuild.** Rebuild and commit `model/tfmod_e5_small_index.pkl` with the new
fields (the wheel force-includes this file).

**Invariant test.** All 54 docs yield a non-empty `module_id`, equal to their root
`**Source**`.

Note: `latest_version` is a snapshot from the curated docs — a hint, not a
guarantee of the current registry latest. `grep_module_docs(version=None)` always
resolves the true latest at fetch time.

## 10. Code Layout / Files Touched

| File | Change |
|---|---|
| `src/tfmod_registry_docs.py` *(new)* | `fetch_module_detail`, `resolve_version`, `assemble_document`, disk cache read/write + in-memory LRU |
| `src/tfmod_doc_grep.py` *(new)* | pure `grep_document(...)` |
| `src/tfmod_mcp_server.py` | `grep_module_docs` tool + testable `_impl`; add `module_id`/`latest_version` to `SearchHit`/`ModuleListItem`; update server `instructions` (three-tool boundaries) |
| `src/tfmod_search_lib.py` | parse `Module ID`/`Latest Version`; new `DocRecord` fields; config keys `doc_cache_dir`, `doc_cache_ttl_hours` |
| `config.yaml` | `doc_cache_dir` (optional), `doc_cache_ttl_hours: 24` |
| `modules/terraform-aws-modules/*.md` | backfill `Module ID` bullet (×54) |
| `modules/module_template.md`, `add-module` skill | include `Module ID` |
| `model/tfmod_e5_small_index.pkl` | rebuild with new fields |
| `tests/…` | offline unit tests + cache tests + opt-in live test |
| `README.md`, `CLAUDE.md` | tool docs, new fields, tool-boundary guidance |

## 11. Dependencies

Zero new runtime dependencies. Uses stdlib `urllib.request`, `json`, `re`,
`pathlib`, `time`. Network access is confined to `tfmod_registry_docs.py`; the rest
of the server stays offline.

## 12. Testing Plan

- **Offline unit tests** against a committed, trimmed registry-response fixture:
  assembly determinism, section labeling, grep (regex, IGNORECASE, context, match
  merging, `scope`, `max_matches` cap, zero-match `available_sections`, invalid
  regex).
- **Parser tests**: `module_id` / `latest_version` extraction, `Source` fallback,
  the all-54-non-empty invariant.
- **Cache tests** (monkeypatch the fetcher, count calls): pinned never refetches,
  `latest` TTL expiry refetches, `refresh` bypasses, `doc_cache_dir` override,
  concrete-version entry written on `latest` fetch.
- **Model/output tests**: `SearchHit`/`ModuleListItem` carry the new fields;
  `GrepOutput` shape and score/`truncated` correctness.
- **Opt-in live test** (env-gated like `RUN_REGISTRY_BENCHMARK`, marker `benchmark`,
  graceful skip if unreachable): real fetch of `terraform-aws-modules/vpc/aws`, grep
  a known variable, assert a match with context.

## 13. Future Options (out of scope now)

- **Fetch/grep split** (brainstorm approach B): add `fetch_module_docs` returning a
  section table-of-contents for repeated cheap greps. Easy follow-on if usage shows
  multi-grep sessions dominate.
- **Registry providers** grep via the provider docs endpoint.
- **Serve-stale-on-failure** (`allow_stale`) if offline resilience becomes a need.

## 14. Rollout

- Minor feature release (new tool + additive fields; backward compatible).
- Index rebuild required; wheel repackaged (already force-includes the index).
- README "MCP Tools" + CLAUDE.md updated; server `instructions` updated to steer
  agents: `search_modules` (find AWS module) → `get_module` (curated compact,
  offline) vs `grep_module_docs` (any registry module, live, version-pinned,
  pinpoint regex lookups).
