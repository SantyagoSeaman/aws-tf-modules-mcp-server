"""
Integration tests for CLI index command.
Tests the full index build pipeline with real module documentation.
"""

import logging
import subprocess
import sys
from pathlib import Path

import pytest

from tests.integration import PROJECT_ROOT
from tfmod_search_lib import compute_scores, load_index


@pytest.fixture
def test_logger():
    """Provide a logger for tests."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
    return logger


@pytest.fixture
def test_index_path(tmp_path):
    """Provide a temporary path for test index file."""
    return str(tmp_path / "test_tfmod_gte_small_index.pkl")


@pytest.fixture
def project_paths():
    """Provide project paths for testing."""
    return {
        "docs_dir": str(PROJECT_ROOT / "modules" / "terraform-aws-modules"),
        "cli_script": str(PROJECT_ROOT / "src" / "tfmod_search_cli.py"),
    }


def test_cli_index_builds_successfully(test_index_path, project_paths):
    """
    Test that the CLI index command builds an index successfully
    with the specified parameters.
    """
    # Verify required directories exist
    assert Path(project_paths["docs_dir"]).exists(), f"Documentation directory not found: {project_paths['docs_dir']}"

    # Build the command
    cmd = [
        sys.executable,
        project_paths["cli_script"],
        "index",
        "--docs_dir",
        project_paths["docs_dir"],
        "--index_path",
        test_index_path,
        "--model",
        "thenlper/gte-small",
    ]

    # Run the index command
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,  # 5 minutes max (first run downloads model)
    )

    # Check command succeeded
    assert result.returncode == 0, f"Index command failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

    # Verify index file was created
    assert Path(test_index_path).exists(), f"Index file was not created at {test_index_path}"

    # Verify output message
    assert "Indexed" in result.stdout, f"Expected 'Indexed' in output, got: {result.stdout}"
    assert "documents" in result.stdout, f"Expected 'documents' in output, got: {result.stdout}"


def test_cli_index_creates_valid_index(test_index_path, project_paths, test_logger):
    """
    Test that the created index can be loaded and contains valid data.
    """
    # First, build the index
    cmd = [
        sys.executable,
        project_paths["cli_script"],
        "index",
        "--docs_dir",
        project_paths["docs_dir"],
        "--index_path",
        test_index_path,
        "--model",
        "thenlper/gte-small",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    assert result.returncode == 0, f"Index build failed: {result.stderr}"

    # Load the index
    index = load_index(test_index_path, test_logger)

    # Verify index structure
    assert index is not None, "Index is None"
    assert index.model_name == "thenlper/gte-small", f"Expected model 'thenlper/gte-small', got '{index.model_name}'"

    # Verify index contains documents
    assert len(index.docs) > 0, "Index contains no documents"

    # Verify all expected components are present
    assert index.bm25 is not None, "BM25 index is missing"
    assert index.doc_vectors is not None, "Document vectors are missing"
    assert len(index.doc_vectors) == len(
        index.docs
    ), f"Vector count mismatch: {len(index.doc_vectors)} vs {len(index.docs)} docs"

    print(f"\n✓ Index loaded successfully with {len(index.docs)} documents")
    print(f"✓ Model: {index.model_name}")


def test_cli_index_search_integration(test_index_path, project_paths, test_logger):
    """
    End-to-end test: Build index, then search it to verify functionality.
    """
    # Build the index
    build_cmd = [
        sys.executable,
        project_paths["cli_script"],
        "index",
        "--docs_dir",
        project_paths["docs_dir"],
        "--index_path",
        test_index_path,
        "--model",
        "thenlper/gte-small",
    ]

    result = subprocess.run(build_cmd, capture_output=True, text=True, timeout=300)
    assert result.returncode == 0, f"Index build failed: {result.stderr}"

    # Load the index
    index = load_index(test_index_path, test_logger)

    # Test a search query
    test_queries = ["vpc networking subnets", "s3 bucket storage", "lambda function serverless"]

    for query in test_queries:
        results = compute_scores(
            index, query, w_kw=2.0, w_exact=3.0, w_bm25=1.0, w_sem=1.0, top_k=5, logger=test_logger
        )

        # Verify we get results
        assert len(results) > 0, f"No results for query: {query}"

        # Verify results structure
        score, doc_idx = results[0]
        assert isinstance(score, float), "Score should be float"
        assert isinstance(doc_idx, int), "Doc index should be int"
        assert 0 <= doc_idx < len(index.docs), "Invalid doc index"

        # Verify top result has positive score
        assert score > 0, f"Top result has non-positive score for query: {query}"

        print(f"\n✓ Query '{query}' returned {len(results)} results")
        print(f"  Top result: {index.docs[doc_idx].module_name} (score: {score:.3f})")


def test_cli_index_with_real_paths(tmp_path, test_logger):
    """
    Test with the actual project paths as specified in the requirement.
    This test uses a temporary path for the index but real project directories.
    """
    test_index = str(tmp_path / "integration_test_index.pkl")

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "src" / "tfmod_search_cli.py"),
        "index",
        "--docs_dir",
        "./modules/terraform-aws-modules",
        "--index_path",
        test_index,
        "--model",
        "thenlper/gte-small",
    ]

    # Run from project root
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=300)

    assert result.returncode == 0, f"Failed with real paths:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

    assert Path(test_index).exists(), "Index file not created"

    # Verify the index
    index = load_index(test_index, test_logger)
    assert len(index.docs) > 0, "No documents indexed"

    print(f"\n✓ Successfully built index with {len(index.docs)} documents using real project paths")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s"])
