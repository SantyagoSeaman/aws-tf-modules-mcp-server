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
    filter_module_sections,
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
    index_path = PROJECT_ROOT / "model" / "tfmod_e5_small_index.pkl"
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
    index_path = PROJECT_ROOT / "model" / "tfmod_e5_small_index.pkl"

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

    def test_search_hit_includes_module_id(self, server_state):
        """Test that search hits surface module_id and latest_version for chaining into grep_module_docs."""
        result = search_modules_impl("vpc", server_state)

        top = result.results[0]
        assert top.module_id == "terraform-aws-modules/vpc/aws"
        assert top.latest_version, "latest_version should be non-empty"

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


class TestSearchTopK:
    """Test the top_k parameter of search_modules."""

    def test_default_returns_three(self, server_state):
        """Test that search returns 3 results by default."""
        result = search_modules_impl("aws", server_state)
        assert len(result.results) == 3, "Default should return exactly 3 results"

    def test_custom_top_k(self, server_state):
        """Test that top_k=5 returns 5 results."""
        result = search_modules_impl("aws", server_state, top_k=5)
        assert len(result.results) == 5, "top_k=5 should return exactly 5 results"

    def test_top_k_one(self, server_state):
        """Test that top_k=1 returns only the best match."""
        result = search_modules_impl("vpc", server_state, top_k=1)
        assert len(result.results) == 1, "top_k=1 should return exactly 1 result"
        assert "vpc" in result.results[0].module_name.lower(), "Top result should be VPC module"

    def test_top_k_clamped_to_max(self, server_state):
        """Test that top_k above 10 is clamped to 10."""
        result = search_modules_impl("aws", server_state, top_k=50)
        assert len(result.results) == 10, "top_k=50 should be clamped to 10 results"

    def test_top_k_clamped_to_min(self, server_state):
        """Test that top_k below 1 is clamped to 1."""
        result = search_modules_impl("aws", server_state, top_k=0)
        assert len(result.results) == 1, "top_k=0 should be clamped to 1 result"

    def test_larger_top_k_extends_ranking(self, server_state):
        """Test that a larger top_k keeps the same top results, just adds more."""
        top3 = search_modules_impl("kubernetes cluster", server_state).results
        top5 = search_modules_impl("kubernetes cluster", server_state, top_k=5).results
        assert [r.module_name for r in top5[:3]] == [
            r.module_name for r in top3
        ], "First 3 of top-5 should match top-3 ranking"


class TestGetModuleSections:
    """Test the sections parameter of get_module."""

    def test_no_sections_returns_full_document(self, server_state):
        """Test that omitting sections returns the unmodified full document."""
        full = get_module_impl("security-group", server_state)
        assert get_module_impl("security-group", server_state, sections=None) == full

    def test_sections_reduce_payload(self, server_state):
        """Test that requesting sections returns a smaller document containing them."""
        full = get_module_impl("security-group", server_state)
        filtered = get_module_impl("security-group", server_state, sections=["inputs"])
        assert len(filtered) < len(full), "Filtered response should be smaller than full document"
        assert "## Main Input Variables" in filtered, "Requested inputs section should be present"

    def test_core_sections_always_included(self, server_state):
        """Test that core context is included regardless of the request."""
        filtered = get_module_impl("security-group", server_state, sections=["inputs"])
        assert "## Module Information" in filtered, "Module Information (version pins) must always be included"
        assert "## Description" in filtered, "Description must always be included"
        assert "## Notes for AI Agents" in filtered, "Notes for AI Agents must always be included"

    def test_gotchas_always_included(self, server_state):
        """Test that a doc's Important Gotchas section survives filtering."""
        filtered = get_module_impl("emr", server_state, sections=["outputs"])
        assert "## Important Gotchas" in filtered, "Important Gotchas must always be included"
        assert "## Main Outputs" in filtered, "Requested outputs section should be present"

    def test_omitted_sections_listed_in_footer(self, server_state):
        """Test that the footer lists omitted sections as a table of contents."""
        filtered = get_module_impl("security-group", server_state, sections=["inputs"])
        assert "Sections omitted from this response" in filtered, "Footer should list omitted sections"
        assert "Best Practices" in filtered, "Omitted section titles should appear in the footer"

    def test_freeform_heading_substring_match(self, server_state):
        """Test that free-form entries match H2 headings by substring."""
        filtered = get_module_impl("eks", server_state, sections=["karpenter"])
        assert "## Submodule 4: karpenter" in filtered, "Substring should match the submodule heading"

    def test_submodules_key_matches_numbered_sections(self, server_state):
        """Test that the submodules key pulls the index and all numbered submodule sections."""
        filtered = get_module_impl("eks", server_state, sections=["submodules"])
        assert "## Submodules" in filtered, "Submodules index section should be present"
        assert "## Submodule 1:" in filtered, "Numbered submodule sections should be present"

    def test_unmatched_section_reported(self, server_state):
        """Test that unmatched entries are reported with available sections."""
        filtered = get_module_impl("vpc", server_state, sections=["nonexistent-section-xyz"])
        assert "Requested sections not found: nonexistent-section-xyz" in filtered
        assert "Available sections:" in filtered, "Footer should list available sections for retry"

    def test_filter_returns_text_without_h2_unchanged(self):
        """Test that documents without H2 sections pass through unfiltered."""
        text = "# Title\n\nJust a paragraph, no sections.\n"
        assert filter_module_sections(text, ["inputs"]) == text


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

    def test_modules_list_includes_module_id(self, server_state):
        """Test that every catalog entry carries a non-empty module_id for chaining into grep_module_docs."""
        result = modules_list_impl(server_state)

        assert all(m.module_id for m in result.modules), "Every module should have a non-empty module_id"


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
