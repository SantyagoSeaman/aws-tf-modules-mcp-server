"""
Integration tests for the MCP server (tfmod_mcp_server.py).

Tests both the search_modules tool and get_module resource.
"""

import logging
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.integration import PROJECT_ROOT
from tfmod_mcp_server import (
    ModulesListOutput,
    SearchWeights,
    ServerState,
    ServerStateManager,
    get_module_documentation,
    get_module_impl,
    modules_list_impl,
    search_modules_impl,
)
from tfmod_search_lib import load_index


@pytest.fixture(scope="module")
def test_logger():
    """Provide a logger for tests."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
    return logger


@pytest.fixture(scope="module")
def mcp_index(test_logger):
    """Load the search index for MCP server tests."""
    index_path = PROJECT_ROOT / "model" / "tfmod_bge_base_index.pkl"
    if not index_path.exists():
        pytest.skip(f"Index file not found at {index_path}")
    return load_index(str(index_path), test_logger)


@pytest.fixture(scope="module")
def search_weights():
    """Default search weights for testing."""
    return SearchWeights(w_kw=2.0, w_exact=3.0, w_bm25=1.0, w_sem=1.0)


@pytest.fixture
def server_state(mcp_index, search_weights, test_logger):
    """Create a ServerState instance for testing."""
    index_path = PROJECT_ROOT / "model" / "tfmod_bge_base_index.pkl"

    # Reset ServerStateManager to allow re-initialization in tests
    ServerStateManager.reset()

    # Initialize the singleton state for tool functions
    state = ServerStateManager.initialize(
        index=mcp_index, weights=search_weights, index_path=index_path, logger=test_logger
    )

    yield state

    # Cleanup: reset after test
    ServerStateManager.reset()


class TestSearchModulesTool:
    """Test the search_modules MCP tool."""

    def test_search_vpc_exact_name(self, server_state):
        """Test searching for VPC module by exact name."""
        # Execute search
        result = search_modules_impl("vpc", server_state)

        # Verify results
        assert len(result.results) <= 3, "Should return at most 3 results"
        assert len(result.results) > 0, "Should return at least 1 result"

        # Top result should be VPC module
        top_result = result.results[0]
        assert "vpc" in top_result.module_name.lower(), "Top result should be VPC module"
        assert top_result.score > 0, "Score should be positive"
        assert len(top_result.keywords) > 0, "Should have keywords"
        assert len(top_result.description) > 0, "Should have description"
        assert len(top_result.path) > 0, "Should have path"

    def test_search_s3_with_functionality(self, server_state):
        """Test searching for S3 module by functionality description."""
        result = search_modules_impl("object storage with encryption", server_state)

        assert len(result.results) > 0, "Should find matching modules"

        # Check that S3 is in top results
        module_names = [r.module_name.lower() for r in result.results]
        assert any("s3" in name or "bucket" in name for name in module_names), "S3/bucket module should be in results"

    def test_search_eks_natural_language(self, server_state):
        """Test searching with natural language query."""
        result = search_modules_impl("kubernetes cluster", server_state)

        assert len(result.results) > 0, "Should find matching modules"

        # EKS should be in results
        module_names = [r.module_name.lower() for r in result.results]
        assert any(
            "eks" in name or "kubernetes" in name for name in module_names
        ), "EKS/kubernetes module should be in results"

    def test_search_returns_max_three_results(self, server_state):
        """Test that search returns maximum 3 results."""
        result = search_modules_impl("aws", server_state)

        assert len(result.results) <= 3, "Should return at most 3 results"

    def test_search_results_structure(self, server_state):
        """Test that search results have correct structure."""
        result = search_modules_impl("vpc", server_state)

        for hit in result.results:
            # Check all required fields are present
            assert isinstance(hit.module_name, str), "module_name should be string"
            assert isinstance(hit.path, str), "path should be string"
            assert isinstance(hit.keywords, list), "keywords should be list"
            assert isinstance(hit.description, str), "description should be string"
            assert isinstance(hit.score, float), "score should be float"

            # Check field contents
            assert len(hit.module_name) > 0, "module_name should not be empty"
            assert len(hit.path) > 0, "path should not be empty"
            assert hit.score >= 0, "score should be non-negative"
            assert len(hit.description) <= 203, "description should be truncated to ~200 chars"

    def test_search_without_index_raises_error(self, search_weights, test_logger):
        """Test that searching without loaded index raises error."""
        # Create a ServerState with None index to trigger error
        bad_state = ServerState(index=None, weights=search_weights, index_path=Path("test.pkl"), logger=test_logger)
        with pytest.raises(RuntimeError, match="Index is not loaded"):
            search_modules_impl("vpc", bad_state)


class TestGetModuleTool:
    """Test the get_module MCP tool."""

    def test_get_module_by_name(self, server_state):
        """Test retrieving module by name."""
        content = get_module_documentation("vpc", server_state)

        assert len(content) > 1000, "Module content should be substantial"
        assert "vpc" in content.lower() or "VPC" in content, "Content should mention VPC"
        assert isinstance(content, str), "Content should be string"

    def test_get_module_by_path(self, server_state):
        """Test retrieving module by file path."""
        content = get_module_documentation("modules/terraform-aws-modules/s3-bucket.md", server_state)

        assert len(content) > 1000, "Module content should be substantial"
        assert "s3" in content.lower() or "bucket" in content.lower(), "Content should mention S3/bucket"

    def test_get_module_all_modules(self, server_state):
        """Test retrieving all indexed modules."""
        # Get all unique module names from index
        module_names = {doc.module_name for doc in server_state.index.docs if doc.module_name}

        for module_name in module_names:
            content = get_module_documentation(module_name, server_state)
            assert len(content) > 0, f"Content for {module_name} should not be empty"
            assert isinstance(content, str), f"Content for {module_name} should be string"

    def test_get_module_security_absolute_path(self, server_state):
        """Test that absolute paths are rejected for security."""
        with pytest.raises(ValueError, match="Absolute paths are not allowed"):
            get_module_documentation("/etc/passwd", server_state)

    def test_get_module_security_path_traversal(self, server_state):
        """Test that path traversal is rejected for security."""
        with pytest.raises(ValueError, match="Access denied"):
            get_module_documentation("modules/../../etc/passwd", server_state)

    def test_get_module_security_outside_modules_dir(self, server_state):
        """Test that paths outside modules/ are rejected."""
        with pytest.raises(ValueError, match="Access denied"):
            get_module_documentation("src/tfmod_mcp_server.py", server_state)

    def test_get_module_nonexistent_file(self, server_state):
        """Test that nonexistent file paths return error."""
        with pytest.raises(ValueError, match="not found"):
            get_module_documentation("modules/nonexistent-file.md", server_state)

    def test_get_module_returns_full_content(self, server_state):
        """Test that get_module returns full content, not truncated."""
        # Get module by name
        content_by_name = get_module_documentation("vpc", server_state)

        # Get same module by path
        vpc_doc = next((doc for doc in server_state.index.docs if doc.module_name == "vpc"), None)
        if vpc_doc:
            content_by_path = get_module_documentation(vpc_doc.path, server_state)

            # Both should return full content
            assert len(content_by_name) > 10000, "Should return full content (not truncated)"
            assert len(content_by_path) > 10000, "Should return full content (not truncated)"

    def test_get_module_tool_implementation(self, server_state):
        """Test calling the get_module tool implementation function."""
        # Test with module name
        content = get_module_impl("vpc", server_state)

        assert isinstance(content, str), "Should return string"
        assert len(content) > 10000, "Should return full content"
        assert "vpc" in content.lower(), "Should contain VPC content"

        # Test with path
        content_path = get_module_impl("modules/terraform-aws-modules/s3-bucket.md", server_state)

        assert len(content_path) > 1000, "Should return substantial content"
        assert "s3" in content_path.lower() or "bucket" in content_path.lower(), "Should contain S3/bucket content"


class TestModulesListTool:
    """Test the modules_list MCP tool."""

    def test_modules_list_returns_all_modules(self, server_state):
        """Test that modules_list returns all indexed modules."""
        result = modules_list_impl(server_state)

        # Verify result structure
        assert isinstance(result, ModulesListOutput), "Should return ModulesListOutput"
        assert hasattr(result, "modules"), "Should have modules field"
        assert hasattr(result, "count"), "Should have count field"

        # Verify count matches modules list
        assert result.count == len(result.modules), "Count should match modules list length"
        assert result.count == len(server_state.index.docs), "Should return all indexed documents"

    def test_modules_list_structure(self, server_state):
        """Test that each module item has correct structure."""
        result = modules_list_impl(server_state)

        for module in result.modules:
            # Check all required fields are present
            assert isinstance(module.module_name, str), "module_name should be string"
            assert isinstance(module.path, str), "path should be string"
            assert isinstance(module.description, str), "description should be string"
            assert isinstance(module.keywords, list), "keywords should be list"

            # Check field contents
            assert len(module.path) > 0, "path should not be empty"
            # module_name can be empty for some docs
            # description is extracted, can be empty if no content
            assert all(isinstance(kw, str) for kw in module.keywords), "all keywords should be strings"

    def test_modules_list_contains_expected_modules(self, server_state):
        """Test that modules_list includes known modules."""
        result = modules_list_impl(server_state)

        module_names = [m.module_name for m in result.modules]

        # Check for some known modules (depends on test data)
        expected_modules = ["vpc", "s3-bucket", "eks", "lambda", "iam", "security-group"]
        for expected in expected_modules:
            assert expected in module_names, f"Should include {expected} module"

    def test_modules_list_descriptions_truncated(self, server_state):
        """Test that descriptions are properly truncated."""
        result = modules_list_impl(server_state)

        for module in result.modules:
            # Descriptions should be truncated to ~200 chars
            assert len(module.description) <= 203, f"Description for {module.module_name} should be truncated"


class TestMCPServerIntegration:
    """Integration tests combining multiple MCP server features."""

    def test_modules_list_then_get_module(self, server_state):
        """Test workflow: list modules, then get one."""
        # Step 1: Get full catalog
        catalog = modules_list_impl(server_state)
        assert len(catalog.modules) > 0, "Should have modules in catalog"

        # Step 2: Pick first module and get its documentation
        first_module = catalog.modules[0]
        doc = get_module_impl(first_module.module_name, server_state)

        # Verify we got documentation
        assert len(doc) > 100, "Should get substantial documentation"
        assert isinstance(doc, str), "Documentation should be string"

    def test_search_then_get_module(self, server_state):
        """Test workflow: search for module, then get full documentation."""
        # Step 1: Search for S3 bucket module
        search_result = search_modules_impl("s3 bucket encryption", server_state)
        assert len(search_result.results) > 0, "Should find S3 module"

        # Step 2: Get full documentation using path from search result
        top_result = search_result.results[0]
        full_content = get_module_documentation(top_result.path, server_state)

        # Verify we got full content
        assert len(full_content) > len(top_result.description), "Full content should be longer than description"
        assert len(full_content) > 1000, "Full content should be substantial"

    def test_search_results_are_ranked(self, server_state):
        """Test that search results are properly ranked by score."""
        result = search_modules_impl("vpc", server_state)

        # Scores should be in descending order
        scores = [hit.score for hit in result.results]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by score (descending)"

        # Top result should have highest score
        if len(scores) > 1:
            assert scores[0] >= scores[-1], "Top result should have highest score"

    def test_module_paths_are_valid(self, server_state):
        """Test that all module paths in search results are valid."""
        result = search_modules_impl("aws", server_state)

        for hit in result.results:
            # Each path should be accessible via get_module
            content = get_module_documentation(hit.path, server_state)
            assert len(content) > 0, f"Path {hit.path} should be accessible"
