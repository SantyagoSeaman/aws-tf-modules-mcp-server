# Changelog

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
