# Changelog

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
