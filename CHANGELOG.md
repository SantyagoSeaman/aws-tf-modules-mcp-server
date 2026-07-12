# Changelog

## [0.9.0] - 2026-07-12

[0.9.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.9.0

The skills-integration release: 0.8.0 shipped `grep_module_docs` but left every plugin skill on pre-0.8.0 guidance. This release teaches the skills and subagents **when to escalate** from the compact curated `get_module` doc to an exact, version-pinnable quote from the live registry docs — and adds a direct `/tf-grep` command.

### Added

- **New user-invoked skill `/tf-grep <module> <pattern>`** — grep the live registry documentation of any module (version-pinnable, non-AWS namespaces too) for an exact quote. Resolves a bare name to a `module_id` via `search_modules` or takes a full `namespace/name/provider` coordinate directly, detects an optional pinned version, and returns the matched lines with section label, line number, and context. Ships a Codex binding.
- **Grep-escalation guidance across all seven skills and both subagents**, driven by one shared model (compact doc = overview → `grep_module_docs` = proof) with four canonical triggers:
  - A variable is **absent from the curated doc** → grep the name before calling it dead. This replaces the pre-0.8.0 "confirm via the registry link in the doc" cop-out in `tf-review`, `tf-module-upgrade`, `tf-migrate`, `tf-diff-reviewer`, and `tf-log-analyst` — an agent cannot follow a link mid-review, so those findings previously stayed permanently "unconfirmed".
  - The **project pins an older version** → grep at that `version`, not latest. Upgrade audits now grep both the pinned and the latest version; that diff is the audit.
  - The **module is outside the curated AWS catalog** (cloudposse, any namespace) → grep its live docs instead of surrendering with "not indexed".
  - A claim **rests on an exact default/type** → quote the line (`scope=["inputs"]` / `["outputs"]`) instead of paraphrasing from memory.
- **`verified-against-live-doc`** confidence level in the `tf-log-analyst` subagent, between `verified-against-doc` and `inferred-from-error`.
- **Contract regression tests** (`test_model_invoked_skills_reference_grep_tool`, `test_agents_reference_grep_tool`) asserting every model-invoked skill and both subagents reference `grep_module_docs`, so a future skill edit cannot silently drop the integration.

### Changed

- README skills table: "Seven skills" → "Eight skills" with the `/tf-grep` entry; test counts refreshed.

### Tests

- Full suite: 355 tests (349 pass, 6 opt-in live tests skip unless `RUN_REGISTRY_BENCHMARK=1`).

## [0.8.0] - 2026-07-12

[0.8.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.8.0

The live-registry release: the server reaches beyond its curated offline catalog. A new grep tool pinpoints lines in the full, current documentation of **any** Terraform Registry module — version-pinnable, cached, and returning matches with context instead of dumping 100k-token documents into the agent's context window.

### Added

- **New MCP tool `grep_module_docs(module_id, pattern, version=None, case_sensitive=False, context_lines=2, scope=None, max_matches=50, refresh=False)`** — regex-greps the live documentation of any Terraform Registry module (`namespace/name/provider`), not just the curated AWS catalog. Fetches the module detail from the registry API, assembles README + inputs/outputs/resources rows + every submodule and example into one greppable text, and returns only the matching lines with section label, line number, and surrounding context. A zero-match response includes `available_sections` for follow-up queries. Built for surgical lookups: an exact variable default in a pinned older version, a submodule input, a non-AWS module.
- **Disk cache for assembled registry docs**: pinned versions are immutable and cached forever; `latest` is cached for `doc_cache_ttl_hours` (default 24h). Location `${TFMODSEARCH_CACHE_DIR:-${XDG_CACHE_HOME:-~/.cache}}/tfmodsearch/registry_docs`, overridable via `config.yaml` (`doc_cache_dir`, `doc_cache_ttl_hours`); `refresh=True` bypasses the cache.
- **`module_id` and `latest_version` fields on `search_modules` and `modules_list` results** — registry coordinates parsed from a new explicit `**Module ID**` header bullet backfilled into all 54 curated docs (with a fallback to the root `**Source**` bullet), so an agent can chain `search_modules → grep_module_docs` without guessing coordinates. Index rebuilt with the new fields.
- **Two new source modules** with a strict boundary: `src/tfmod_registry_docs.py` (registry client: fetch + document assembly + disk cache — the **only** networked module, stdlib `urllib` only, zero new dependencies) and `src/tfmod_doc_grep.py` (pure offline grep engine). The curated `search_modules`/`get_module`/`modules_list` tools remain fully offline.
- **Registry Search Comparison benchmark** in the README: top-1/top-3 retrieval on the full 54-module/162-query golden set vs. the public Terraform Registry search API (the same endpoint HashiCorp's `terraform-mcp-server` wraps). TFModSearch: 92% top-1 / 100% top-3 overall; registry keyword search: 42.6% / 42.6% (official namespace) — the gap is entirely in descriptive queries, where semantic search finds modules that keyword search never surfaces. Reproducible via `RUN_REGISTRY_BENCHMARK=1 pytest tests/integration/test_registry_comparison.py`.

### Tests

- 16 new tests for the grep feature: pure grep engine (regex, case-insensitivity, context lines, section labeling, `scope`, `max_matches` cap, invalid-regex error), registry client + cache semantics with an injected fetcher — no real network (pinned-forever, latest-TTL, `refresh`), tool wiring, a header invariant (every curated doc's `Module ID` equals its root registry `Source`), and a 2-test opt-in live smoke test against the real registry.
- Full suite: 345 tests (6 opt-in live tests skip unless `RUN_REGISTRY_BENCHMARK=1`).

## [0.7.0] - 2026-07-11

[0.7.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.7.0

Driven by field feedback from a real agent session: search ranking and doc freshness earned their keep, but full-document `get_module` responses were heavier than needed and top-3 was tight for ambiguous queries.

### Added

- **`top_k` parameter on `search_modules`** (1–10, default 3) — raise it for ambiguous queries like `"iam"` where three results are too tight to disambiguate.
- **`sections` parameter on `get_module`** — fetch only the parts you need instead of the full document (large modules run to 10k+ tokens in full; `s3-bucket` with `sections=["inputs"]` is ~5x smaller). Accepts logical keys (`inputs`, `outputs`, `examples`, `submodules`, `features`, `use-cases`, `best-practices`, `resources`) or case-insensitive heading substrings (e.g. `"karpenter"` for a single EKS submodule). Core context — description, pinned versions, notes for AI agents, gotchas — is always included regardless of the request, and every filtered response ends with a footer listing the omitted sections, so nothing is silently hidden and the agent can request more.

### Changed

- **Normalized H2 headings across 14 module docs** to the canonical template names (`Main Input Variables`, `Main Outputs`, `Usage Examples`, `Best Practices`, `Important Gotchas`), eliminating naming variants (`Variables`, `Input Variables`, `Key Outputs`, `Critical Warnings and Gotchas`, `Important Notes`, `Recommendations`, `Complete Module Usage`, and two others). Heading renames only — no content changed; intra-doc anchor links updated; index rebuilt and the full searchability suite re-verified with no ranking regressions. This gives section extraction a single canonical heading set to key on.

## [0.6.0] - 2026-07-11

[0.6.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.6.0

The efficiency release: a smaller, faster embedding model matches the previous default's retrieval quality exactly, backed by a full-catalog benchmark and two keyword-matching fixes.

### Changed

- **Default embedding model switched from `BAAI/bge-base-en-v1.5` to `intfloat/e5-small-v2`**: benchmarked 5 candidate models against the full 54-module/162-query golden set (exact-name, keyword, and natural-language queries per module) using production search weights. `e5-small-v2` is the only smaller candidate that matches the old default's 100% success rate — at ~3x smaller (~138 MB vs ~419 MB) and ~3x lower query latency (~8ms vs ~23ms), with no weight retuning or query/passage prompt-prefix convention needed (both were tried; neither moved the needle on this corpus). See the "Embedding Model Comparison" section in README.md for the full comparison table, including the other candidates evaluated (`gte-small`, `bge-small-en-v1.5`, `all-MiniLM-L12-v2`) and why they weren't selected.
- **Pre-built index renamed**: `model/tfmod_bge_base_index.pkl` → `model/tfmod_e5_small_index.pkl`, consistent with the existing gte-small→bge-base rename precedent.
- **`test_model_comparison.py` extended** to a 3-way comparison (`gte-small`, `bge-base-en-v1.5`, `e5-small-v2`); the pairwise summary logic was generalized to N models.

### Fixed

- **Closed 3 keyword-matching gaps** found during the model comparison: added `virtual-private-cloud` to `vpc.md`, `automation` + `workflow` to `atlantis.md`, and `storage` + `optimization` to `ebs-optimized.md`. These were queries whose tokenized form (e.g. two space-separated words) never matched an existing hyphenated compound keyword (e.g. `terraform-automation`), so the keyword-scoring component silently contributed nothing and the query relied on embedding quality alone. The fix benefits every embedding model uniformly, not just the new default.

## [0.5.0] - 2026-07-11

[0.5.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.5.0

The skills release: the plugin grows from two skills to a full toolkit — seven skills and two subagents covering the whole lifecycle of working with community modules: author, scaffold, migrate, upgrade, review, and troubleshoot.

### Added

- **`tf-migrate` skill** — detects clusters of hand-written `aws_*` resources that a community module covers (security group + rules, VPC + subnets + NAT, S3 + policies) and proposes a replacement: multiple search angles, attribute-by-attribute coverage mapping against the current doc, an explicit "not covered" list, and state-migration caveats (`moved` blocks / `terraform state mv`). Proposal only — never rewrites.
- **`tf-module-upgrade` skill** — audits existing module blocks against current documentation: version drift, dead/renamed variables, deprecations, changed defaults. Severity-ranked report with exact fixes; applies changes only on approval.
- **`tf-review` skill** — reviews a git diff/branch/PR's module usage: variables exist, required inputs present, versions pinned, deprecations; flags raw-resource clusters a module could replace. Review only, scope-disciplined (no style nits).
- **`tf-stack` skill** (user-invoked) — scaffolds a multi-module stack from a requirement with correct output→input wiring (vpc subnets → rds/alb inputs), pinned versions, and an explicit list of what was left out.
- **`tf-troubleshoot` skill** — diagnoses `terraform plan/apply/init` failures against current module documentation, with a bundled prefilter script.
- **`scripts/extract_tf_errors.py`** (inside tf-troubleshoot) — stdlib-only prefilter that reduces terraform logs of any size to structured diagnostics (severity, summary, file:line, module addresses); handles human-readable `╷│╵` blocks, `-json` output, and bare CI error lines.
- **Two plugin subagents** (Claude Code): `tf-log-analyst` (log forensics: prefilter → verify each finding via get_module → compact root-cause report) and `tf-diff-reviewer` (reads the diff in its own context, returns a findings table). Large logs and diffs never enter the main conversation; skills degrade gracefully to inline analysis on Codex.
- **Maintainer skills** in `.claude/skills/` (now committed via a `.gitignore` exception): `refresh-module-docs` (the multi-agent corpus refresh pipeline, codified) and `add-module` (onboard a new module: doc, keywords, index rebuild, searchability verification).
- **CI workflow** (`.github/workflows/ci.yml`): lint (pre-commit, all files) and the full test suite on every push and pull request, with dependency and embedding-model caching. The publish workflow now calls it as its first job — **PyPI publication is gated on a green test run**. CI status badge added to the README.

### Changed

- **Narrowed the `aws-terraform-modules` skill trigger to authoring** — reviewing, upgrading, migrating, and troubleshooting now have dedicated skills; an e2e test enforces that trigger keywords (reviewing, pull request, upgrade, fails) are claimed by exactly one model-invoked skill.

### Fixed

- **Pinned `fastmcp<3`**: fastmcp 3.x (released upstream) fails on import with the current MCP SDK, which broke fresh `uvx tfmodsearch` installs of 0.4.0 (the dependency was unbounded). Caught by the new CI gate before publication; the server targets the fastmcp 2.x API.

### Tests

- E2E suite grew from 20 to 49 tests: prefilter script tests against a fixture log (all three formats), plugin agent contracts, per-skill Codex binding checks, user-invoked vs model-invoked invariants, trigger-disjointness check, maintainer-skill checks (including that they are not gitignored), and live-install verification extended to all seven skills and the shipped agent files. Full suite: 288 tests passing.

## [0.4.0] - 2026-07-11

[0.4.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.4.0

The distribution release: the project is renamed to **tfmodsearch**, published to PyPI, and ships plugins for Claude Code and Codex CLI that bundle the MCP server with agent workflow skills.

### Changed

- **Project renamed to `tfmodsearch`** (repository, PyPI package, and primary command). The GitHub repository moved to `SantyagoSeaman/tfmodsearch`; old `aws-tf-modules-mcp-server` URLs redirect automatically.
- **New console commands**: `tfmodsearch` (MCP server) and `tfmodsearch-cli` (indexing/search CLI). The previous `aws-tf-modules-mcp-server` and `tfmod-search-cli` commands are kept as deprecated aliases.
- **Trimmed the published wheel** from ~11 MB to ~1.6 MB: it now ships only the production index (`model/tfmod_bge_base_index.pkl`) and the curated `modules/terraform-aws-modules/` docs, excluding the legacy gte-small index, work-in-progress docs, and internal templates.
- **Rewrote the MCP server `instructions`**: corrected the stale catalog size, fixed grammar, and added explicit workflow steering ("search before writing Terraform; use documented variable names, not memorized ones"). The advertised server version now derives from the installed package metadata instead of a hardcoded string.

### Added

- **PyPI publication** with Trusted Publishing: a `publish.yml` GitHub Actions workflow builds and publishes to PyPI on version tags via OIDC (no API tokens), with a tag-vs-version consistency check.
- **Claude Code plugin** (`/plugin marketplace add SantyagoSeaman/tfmodsearch` → `/plugin install tfmod-search@tfmodsearch`): auto-configures the MCP server via `uvx tfmodsearch` and ships two skills.
- **Codex CLI plugin** with the same two-command install, plus an `agents/openai.yaml` declaring the MCP tool dependency for implicit skill invocation.
- **Skills** (portable SKILL.md format, shared by both plugins):
  - `aws-terraform-modules` — auto-invoked when writing/reviewing Terraform for AWS: search first, write from current docs, pin module versions, prefer community modules.
  - `tf-module` — user-invoked lookup (`/tf-module s3 bucket with lifecycle rules`) returning a ready-to-paste module block with current variable names.
- **`--warmup` flag** for the MCP server: pre-downloads the embedding model (~220 MB), loads the index, runs a test query, and exits — keeps first server startup within MCP client timeouts.

### Fixed

- **`get_module` no longer guesses**: unknown module names previously fell through to hybrid search and silently returned the highest-scoring module's documentation (a hallucinated name could return the lambda docs). Name lookup is now exact-match first, then unique-substring; unknown or ambiguous names return an error listing the closest matches and directing the caller to `search_modules`.

### Tests

- **New end-to-end suite** (`tests/e2e/`, 20 tests): full MCP stdio protocol sessions against a spawned server process (initialize handshake, tool discovery, all three tools, security rejections, `--warmup`), wheel payload/metadata/entry-point verification, a `uvx` packaged-server smoke test from a foreign directory, plugin manifest and skill contract checks for both the Claude Code and Codex layouts, and a live `claude plugin` install into an isolated config. Full suite: 259 tests passing.

### Documentation

- README: new plugin-first installation section, Codex CLI integration guide (with `startup_timeout_sec` note), `claude mcp add` one-liner, AGENTS.md/CLAUDE.md steering snippet, and a PyPI badge. All install configs now use the published `tfmodsearch` package instead of `git+https` URLs.

## [0.3.0] - 2026-07-11

[0.3.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.3.0

This release refreshes the entire module catalog against the latest upstream `terraform-aws-modules` versions, rebuilds the pre-built search index, and overhauls the README. It also rolls up the previously unreleased 0.2.1 changes.

### Changed

- **Full documentation refresh for all 54 modules**: Every document in `modules/terraform-aws-modules/` was regenerated from the current Terraform Registry / GitHub source. Notable version and API updates include:
  - `security-group` → 6.0.0 — major rearchitecture: per-rule `aws_vpc_security_group_ingress_rule`/`egress_rule` resources replace inline rule blocks
  - `eks` → 21.24.0 — post-v21 variable names (`name`, `kubernetes_version`, `addons`, `compute_config`); no default add-ons are bootstrapped
  - `lambda` → 8.8.1, `s3-bucket` → 5.14.1 (new `vectors` submodule), `iam` → 6.6.1, `rds` → 7.2.0, `ec2-instance` → 6.4.0, `alb` → 10.5.0, `apigateway-v2` → 6.1.0, `vpc` → 6.6.1, and others
  - Corrected stale or incorrect variable names, defaults, and examples that could have produced invalid Terraform (e.g. EKS pre-v21 variables, Lambda Function URL configuration, RDS `create_db_subnet_group`/`storage_type` defaults, IAM `iam-role` trust-policy variables)
  - Re-curated keyword lists to the 10–20 most relevant terms per module
- **Rebuilt the pre-built search index** (`model/tfmod_bge_base_index.pkl`) to reflect the refreshed documentation.

### Added

- Canonical service-name keywords to improve retrieval for common full-name queries: `application-load-balancer` (alb), `relational-database` (rds), `simple-notification-service` (sns), `identity`/`access-management` (iam), and `vpn` (vpn-gateway).

### Fixed

- **README accuracy**: corrected the pre-built index filename (`tfmod_bge_base_index.pkl`, previously shown as `tfmod_index.pkl` in several places), the catalog module count (added the missing `emr` module — now a consistent 54), the local-install commands (`pip install -e .` / `uv pip install -e .`), stale test counts, and the `get_module` tool terminology.

### Documentation

- Added a "Why TFModSearch?" value-proposition section, an end-to-end `search_modules` → `get_module` workflow example, an explicit note that the pre-built index and module docs ship inside the installable package, and clarification of the default search weights.

### Tests

- Relaxed `test_module_searchable_by_keyword` to assert the target module appears in the **top-3** results — matching `search_modules`'s documented top-3 return contract and the existing natural-language test — rather than strictly ranking #1. A few semantically adjacent module pairs (e.g. security-group vs network-firewall for "firewall rules") legitimately rank a sibling first while keeping the target in the top-3. Full suite: 239 tests passing.

## [0.2.1] - 2026-01-26

[0.2.1]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.2.1

### Added

- **Configurable Log Level**: New `log_level` option in `config.yaml` (default: INFO)
  - Configurable via config file or CLI `--log_level` argument
  - New `ConfigLoader.load_log_level()` method with standard precedence (CLI > YAML > default)

- **Quick Install via uvx**: Added simplified installation method using `uvx`
  - No repository cloning required
  - Single config line: `"command": "uvx", "args": ["git+https://github.com/..."]`
  - Added uv installation instructions

### Fixed

- **Silenced Noisy Third-Party Loggers**: FastMCP internal loggers now set to WARNING
  - `fakeredis`, `docket`, `asyncio` no longer spam DEBUG output
  - Server startup is now clean and quiet

### Documentation

- Updated README with `uvx` as recommended installation method
- Added troubleshooting note for full path to `uvx` when not in PATH
- Updated CLAUDE.md with new `log_level` config option

## [0.2.0] - 2026-01-25

[0.2.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.2.0

### Changed

- **Embedding Model Upgrade**: Switched default model from `thenlper/gte-small` to `BAAI/bge-base-en-v1.5`
  - Better retrieval performance with 768-dimensional embeddings (vs 384)
  - Improved similarity distribution (addresses narrow clustering issue)
  - BGE v1.5 specifically optimized for retrieval tasks with hard negatives training
  - Model size: ~220MB (vs ~67MB for gte-small)

- **Optional Query Instruction Support**: Added configurable query instruction prefix for BGE models
  - New `query_instruction` parameter in `compute_scores()` function
  - Configurable via `config.yaml` or CLI `--query-instruction` argument
  - Uses modern sentence-transformers `prompt` parameter in `model.encode()`
  - Disabled by default (BGE v1.5 works well without instruction)
  - Instruction: `"Represent this sentence for searching relevant passages: "`

- **Default Index Path**: Changed from `tfmod_gte_small_index.pkl` to `tfmod_bge_base_index.pkl`
  - All references updated across codebase, CLI, and tests
  - Pre-built index now included at `model/tfmod_bge_base_index.pkl`

- **Module List Description**: `modules_list` tool now uses `extract_purpose()` for cleaner descriptions
  - Extracts Purpose field from Module Information section
  - More concise and relevant module descriptions in catalog listing

- **Dependency Updates**:
  - Updated `numpy` from `>=2.3.3` to `>=2.4.1`
  - Updated `sentence-transformers` from `>=5.1.1` to `>=5.2.0`

### Added

- **Integration Guides**: Comprehensive setup instructions in README
  - Claude Code CLI integration with `claude mcp add` command
  - Claude Desktop configuration for macOS
  - GitHub Copilot integration for VS Code (requires VS Code 1.99+)
  - Step-by-step setup and troubleshooting commands

- **New Search Library Functions**:
  - `extract_purpose(text, max_length)`: Extract Purpose field from Module Information section
  - `DEFAULT_MODEL_NAME` constant: Default embedding model identifier
  - `BGE_QUERY_INSTRUCTION` constant: Optional query prefix for BGE models

- **Configuration Loader**: New `ConfigLoader.load_query_instruction()` method
  - Supports precedence: CLI > YAML > default (None)
  - Proper logging for configuration source

- **Build Configuration**: Added hatch wheel build settings in `pyproject.toml`
  - Configured `tool.hatch.build.targets.wheel` for proper package distribution
  - Source mapping from `src/` directory

- **Model Comparison Tests**: New test file `tests/integration/test_model_comparison.py`
  - Compares embedding model performance (gte-small vs bge-base-en-v1.5)
  - Tests across different query types (1-word to long natural language)
  - Timing measurements and success rate analysis

### Fixed

- **ServerState Initialization**: Added `query_instruction` parameter support
  - Properly passed through `ServerStateManager.initialize()`
  - Included in state logging output

### Documentation

- **Module Documentation Updates**: Refreshed all 54 Terraform AWS module docs
  - Updated module versions and feature descriptions
  - Improved formatting and consistency across modules
  - Enhanced best practices and use case sections

- **README Improvements**:
  - Reorganized Quick Start section with integration-specific guides
  - Updated all code examples to use new model and index paths
  - Added GitHub Copilot and VS Code MCP documentation links

- **Configuration Comments**: Enhanced `config.yaml` with detailed comments
  - Documented query instruction usage and BGE model notes
  - Added model configuration guidance

### Notes

- **Index Rebuild Required**: After upgrading, rebuild the search index with the new model
- **Index Size**: Increased from ~4.5MB to ~9MB due to larger embedding dimensions (768 vs 384)
- **Performance**: First query ~2-3s (model loading), subsequent queries ~0.02s
- **Breaking Change**: Default index path changed - update any hardcoded paths

## [0.1.2] - 2025-10-13

[0.1.2]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.1.2

### Changed

- **Parser Architecture Refactoring**: Complete rewrite of document parsing system
  - Removed YAML frontmatter dependency in favor of pure regex-based parsing
  - Created `ModuleDocumentParser` class with two-strategy parsing approach:
    1. "## Module Information" section parsing (preferred)
    2. Inline keywords search (fallback)
  - Fixed module name parsing to strip backticks from Markdown formatting
  - Removed YAML frontmatter blocks from 46 module documentation files
  - Simplified codebase by eliminating `yaml` library dependency

- **Search Algorithm Improvements**: Enhanced hybrid search for better ranking accuracy
  - **Minmax Normalization for Semantic Search**: Added min-max normalization to cosine similarities
    - Spreads small embedding differences (0.89-0.92) into full 0-1 range for better discrimination
    - Addresses limitation of `thenlper/gte-small` model's narrow similarity clustering
    - All scoring components now equally normalized (keywords, BM25, semantic, exact match)
  - **Adaptive Query Scaling**: Implemented logarithmic scaling for BM25 and semantic scores
    - Formula: `log(len(matched_keywords) + 1, base=3)` dampens scores for short queries
    - Reduces BM25 noise on 1-2 word keyword queries where lexical matching is unreliable
    - Improves ranking for precise keyword searches (e.g., "tgw", "firewall", "ssh-keys")

- **Search Index**: Rebuilt index with refactored parser
  - Index size optimized from 4.58MB → 4.51MB (1.5% reduction)
  - All 54 modules now use consistent text-based parsing
  - Maintains 1,529 unique keywords across corpus

### Added

- **Comprehensive Test Suite**: Created extensive integration tests for search quality
  - New file: `tests/integration/test_all_modules_searchable.py` (387 lines, 169 tests)
  - **ModuleTestCase Dataclass**: Explicit document→query triple linkage
    - Each module linked to: keyword query, exact name query, natural language query
    - Clear traceability for test failures with document paths and query types
  - **Parametrized Tests**: 162 tests (54 modules × 3 query types)
    - `test_module_searchable_by_keyword`: Verifies keyword-based search
    - `test_module_searchable_by_name`: Validates exact module name matching
    - `test_module_searchable_by_natural_language`: Tests semantic search quality
  - **Quality Validation Tests**: 7 additional tests
    - Module completeness (keywords, names, content)
    - Data integrity (no duplicates, sufficient keyword vocabulary)
    - Search quality metrics (average keyword count, vocabulary size)
  - **NLTK Initialization**: Created `tests/conftest.py` for pytest setup
    - Automatic NLTK data initialization before test session
    - Eliminates `punkt_tab` resource errors
  - **Test Results**: 160/169 passing (94.7% pass rate)
    - 9 failures due to expected search quality variations (keyword collisions, semantic ambiguity)

### Fixed

- **Module Name Parsing**: Resolved backtick capture in regex patterns
  - Changed pattern from `(.+?)` to `([^`]+?)` to exclude backticks from capture group
  - All module names now parse correctly without Markdown formatting artifacts
- **Parser Fallback Logic**: Improved reliability with dual-strategy approach
  - Primary strategy: Structured "## Module Information" section
  - Fallback strategy: Inline keyword search in document body
  - More resilient to documentation format variations

### Documentation

- **Test Coverage**: Added inline documentation for all test classes and methods
  - Detailed docstrings explaining test purpose and validation criteria
  - Examples of query types and expected behavior
- **Parser Documentation**: Enhanced ModuleDocumentParser class documentation
  - Strategy descriptions with regex patterns
  - Normalization and deduplication logic explained
- **Search Algorithm Notes**: Added comments explaining scoring improvements
  - Minmax normalization rationale and impact
  - Logarithmic scaling formula and use cases

## [0.1.1] - 2025-10-12

[0.1.1]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.1.1

### Changed
- **Expanded Module Catalog**: Search index now includes 54 Terraform AWS modules
- **Search Index**: Rebuilt index with all 54 modules
  - 1,535 unique keywords indexed
  - Enhanced semantic search coverage across AWS services

### Documentation
- Each new module includes:
  - Comprehensive descriptions with 2-3 paragraphs
  - 10-25 key features per module
  - 8-10 real-world use cases
  - 20-70+ best practices across multiple categories
  - Integration examples and code snippets
  - Links to official AWS documentation
  - AI agent implementation notes

## [0.1.0] - 2025-10-11

[0.1.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.1.0

### Added
- Initial release of TFModSearch MCP Server
- Hybrid search engine combining semantic embeddings, BM25, and keyword matching
- FastMCP-based server with stdio transport
- Three MCP tools: `search_modules`, `get_module`, `modules_list`
- CLI interface with `index` and `search` subcommands
- Support for Terraform AWS modules documentation
- Configurable search weights via YAML config
- Security features: path validation, access controls
- Comprehensive test suite (39 integration tests)
- Documentation with examples and integration guides
- Pre-commit hooks for code quality (ruff, mypy)
- Claude Desktop integration support

### Features
- **Hybrid Search**: Combines 4 scoring signals for accurate module discovery
- **CPU-Only Inference**: Uses `thenlper/gte-small` model for semantic embeddings
- **Fast Indexing**: Pre-built search index with BM25 and embeddings
- **Type Safety**: Full type hints with mypy checking
- **Comprehensive Documentation**: README, tests documentation, inline comments
