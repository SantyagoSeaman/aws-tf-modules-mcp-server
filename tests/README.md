# Tests

This directory contains tests for the TFModSearch MCP Server.

## Setup

Install test dependencies:

```bash
# Using uv (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run integration tests only
```bash
pytest tests/integration/
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/integration/test_cli_index.py
```

### Run specific test function
```bash
pytest tests/integration/test_cli_index.py::test_cli_index_builds_successfully -v
```

## Test Structure

- `tests/integration/` - Integration tests that test complete workflows
  - `test_cli_index.py` - Tests for CLI index command with real module documentation
  - `test_parse_markdown.py` - Tests for parse_markdown_file function with all module docs

## Integration Test Details

### test_cli_index.py

Comprehensive tests for the index building process:

1. **test_cli_index_builds_successfully** - Verifies the CLI command executes without errors
2. **test_cli_index_creates_valid_index** - Validates the created index structure and content
3. **test_cli_index_search_integration** - End-to-end test that builds index and performs searches
4. **test_cli_index_with_real_paths** - Tests with actual project paths as specified

### test_parse_markdown.py

Tests for the Markdown parser that extracts module information:

1. **test_parse_all_terraform_modules** - Validates all .md files can be parsed with module_name and keywords
2. **test_parse_specific_module_structure** - Verifies parsing of s3-bucket.md structure in detail
3. **test_parse_module_name_normalization** - Ensures module names are lowercase and hyphenated
4. **test_parse_keywords_normalization** - Ensures keywords are lowercase, unique, and sorted

### Notes

- Integration tests may take 2-5 minutes on first run (downloads the `thenlper/gte-small` model)
- Subsequent runs are faster as the model is cached
- Tests use temporary directories for index files (automatic cleanup)
- All tests run from the project root directory
