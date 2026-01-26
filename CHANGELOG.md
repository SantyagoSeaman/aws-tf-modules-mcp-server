# Changelog

## [0.2.0] - 2026-01-25

[0.2.0]: https://github.com/SantyagoSeaman/aws-tf-modules-mcp-server/releases/tag/v0.2.0

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

[0.1.2]: https://github.com/SantyagoSeaman/aws-tf-modules-mcp-server/releases/tag/v0.1.2

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

[0.1.1]: https://github.com/SantyagoSeaman/aws-tf-modules-mcp-server/releases/tag/v0.1.1

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

[0.1.0]: https://github.com/SantyagoSeaman/aws-tf-modules-mcp-server/releases/tag/v0.1.0

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
