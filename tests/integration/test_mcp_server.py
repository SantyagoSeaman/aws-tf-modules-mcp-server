"""
Integration tests for the MCP server (tfmod_mcp_server.py).

Tests both the search_modules tool and get_module resource.
"""

import logging
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import tfmod_mcp_server
from tests.integration import PROJECT_ROOT
from tfmod_mcp_server import (
    ModulesListOutput,
    SearchWeights,
    ServerState,
    ServerStateManager,
    _extract_interface_h3,
    _parse_submodule_address,
    filter_module_sections,
    get_module_documentation,
    get_module_impl,
    modules_list_impl,
    orientation_head,
    search_modules_impl,
)
from tfmod_search_lib import load_index

ANY_OVERLAY_FIXTURES = PROJECT_ROOT / "tests" / "fixtures" / "any_overlay"


def _input_row_cells(rendered: str, var_name: str) -> list[str]:
    """Locate the Main Input Variables row for `var_name` (a bare, backtick-
    wrapped Variable-column cell, e.g. "lifecycle_rule") and split it into
    cells via the server's own table-row splitter, for precise cell-level
    assertions instead of fragile whole-row substring/comma counting (a
    Description cell can carry its own commas/backticked names that would
    otherwise collide with a Type-cell assertion)."""
    matched = next(row for row in rendered.splitlines() if row.startswith(f"| `{var_name}`"))
    return tfmod_mcp_server._split_table_row(matched)


def _output_row_cells(rendered: str, output_name: str) -> list[str]:
    """Same as `_input_row_cells`, for a Main Outputs table row (the Output
    column, not Variable)."""
    matched = next(row for row in rendered.splitlines() if row.startswith(f"| `{output_name}`"))
    return tfmod_mcp_server._split_table_row(matched)


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
        """Test that search hits surface module_id and latest_version registry coordinates."""
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
        """Default returns a compact orientation head; sections=['all'] returns the full doc."""
        # Default (no sections) → orientation head
        head = get_module_impl("vpc", server_state)
        assert isinstance(head, str), "Should return string"
        assert "vpc" in head.lower(), "Should contain VPC content"
        assert "## Module Information" in head, "Orientation head must carry module info"
        assert "Available sections" in head, "Head lists the full section inventory as a menu"

        # Escape hatch → complete document, larger than the head
        full = get_module_impl("vpc", server_state, sections=["all"])
        assert len(full) > len(head), "Full document should exceed the orientation head"
        assert len(full) > 10000, "Full document should be substantial"

        # Path identifier resolves to an orientation head too
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

    def test_default_returns_orientation_head(self, server_state):
        """Omitting sections returns the compact orientation head, not the full document."""
        head = get_module_impl("security-group", server_state)
        full = get_module_impl("security-group", server_state, sections=["all"])
        assert len(head) < len(full), "Default head should be smaller than the full document"
        assert "## Module Information" in head, "Core context is always present in the head"
        assert "Available sections" in head, "Head lists the full section inventory as a menu"
        # sections=None is the same as omitting the argument
        assert get_module_impl("security-group", server_state, sections=None) == head

    def test_full_escape_hatch_returns_complete_document(self, server_state):
        """sections=['all'] bypasses section filtering/truncation -- the full
        section inventory is always present. Since the 2026-07-21 all-63-
        catalog build every module carries a committed any-overlay (all_
        inputs/all_outputs at minimum), so the complete-interface-table
        supersede and any-overlay appendix transforms still apply here
        exactly as they do for every other view -- there is no longer a
        catalog module for which the raw doc is untouched, so the baseline is
        built through the same transform pipeline get_module_impl uses for
        this branch (mirrors TestCompleteInputTable/TestCompleteOutputTable's
        own full-doc-escape-hatch checks)."""
        for key in ("all", "full", "everything"):
            full = get_module_impl("security-group", server_state, sections=[key])
            raw = get_module_documentation("security-group", server_state)
            expected = tfmod_mcp_server._full_document_view(raw)
            assert (
                full == expected
            ), f"sections=['{key}'] should return the complete document (overlay transforms applied)"

    def test_orientation_head_includes_version_pin_hint(self, server_state):
        """The default head surfaces an actionable exact-version pin (BUG-5)."""
        head = get_module_impl("vpc", server_state)
        assert "Version pin" in head, "Orientation head should surface an exact-pin hint"
        assert 'version = "' in head, "Pin hint should show an exact version pin"

    def test_response_carries_escalation_pointer(self, server_state):
        """Head and filtered responses point to the module source for complete/exact
        data now that grep_module_docs (D7, 2026-07-21) has been removed."""
        for resp in (
            get_module_impl("s3-bucket", server_state),
            get_module_impl("s3-bucket", server_state, sections=["inputs"]),
        ):
            assert "grep_module_docs" not in resp, "Response must not reference the removed grep tool"
            assert "COMPLETE inputs/outputs" in resp, "Response must flag that it is a curated subset"
            assert "module source" in resp, "Response must name source as the creation-condition tier"

    def test_footer_grep_hint_mentions_shapes(self):
        """D7 (2026-07-21): grep_module_docs was removed outright. The footer
        still carries the TYPE/SHAPE phrase for the one case it used to
        reserve for grep (a map(object)/any field's nested sub-shape), but now
        routes it to the module source directly instead of a live-grep tool."""
        doc = (
            "---\nm: x\n---\n\n## Module Information\n\n- **Module ID**: x/y/aws\n\n"
            "## Description\n\nd\n\n## Notes for AI Agents\n\nn\n"
        )
        out = filter_module_sections(doc, [])
        assert "TYPE/SHAPE" in out, "Footer must carry the explicit type/shape verification phrase"

    def test_footer_routes_completeness_and_name_confirmation_to_get_module(self):
        """D1: the footer's COMPLETE/name-confirmation escalation routes to ONE
        offline get_module(sections=["inputs","outputs"]) call, not to
        grep_module_docs -- the old wording invited an unnecessary live
        round-trip for data get_module already serves authoritatively."""
        doc = (
            "---\nm: x\n---\n\n## Module Information\n\n- **Module ID**: x/y/aws\n\n"
            "## Description\n\nd\n\n## Notes for AI Agents\n\nn\n"
        )
        out = filter_module_sections(doc, [])
        assert (
            'sections=["inputs","outputs"]' in out
        ), "Footer must point completeness/name-confirmation at the full interface call"
        assert "confirm a name exists, grep" not in out, "Footer must not route name-confirmation to grep"
        assert (
            "to confirm a name exists, grep the live doc" not in out
        ), "Old name-confirmation-to-grep phrasing must be gone"

    def test_footer_routes_remaining_escalation_cases_to_module_source_not_grep(self):
        """D7 (2026-07-21): grep_module_docs was removed outright. The footer
        still names the three cases it used to reserve for grep -- a module
        outside the catalog, a pinned/older version, or a map(object)/any
        field's nested sub-shape -- but must never name the removed tool."""
        doc = (
            "---\nm: x\n---\n\n## Module Information\n\n- **Module ID**: x/y/aws\n\n"
            "## Description\n\nd\n\n## Notes for AI Agents\n\nn\n"
        )
        out = filter_module_sections(doc, [])
        assert "grep_module_docs" not in out, "Footer must not reference the removed grep tool"
        assert "outside this catalog" in out, "Footer must still reserve an escalation for non-catalog modules"
        assert "pinned" in out.lower(), "Footer must still reserve an escalation for pinned/older versions"
        assert "nested" in out.lower(), "Footer must still reserve an escalation for a nested map(object)/any sub-shape"

    def test_head_cap_pointer_mentions_full_interface(self, server_state):
        """D1: the capped head input-table pointer (fires when a module's root
        input table is wider than the head's bounded sample) now points at
        the full interface (inputs AND outputs), not inputs alone."""
        head = get_module_impl("s3-bucket", server_state)
        assert "more inputs" in head, "s3-bucket has more inputs than the head cap -- pointer must fire"
        assert 'get_module(sections=["inputs","outputs"]) for the full interface' in head

    def test_footer_disclaimer_is_compact(self):
        """RC2 F1: the honest-limits disclaimer is a 1-2 line pointer, not a long
        repeated paragraph -- it is verbatim on every get_module call (measured
        42.8K chars of pure repetition across 56 calls at the old ~764-char size),
        so it must be collapsed while keeping the escalation load-bearing."""
        doc = (
            "---\nm: x\n---\n\n## Module Information\n\n- **Module ID**: x/y/aws\n\n"
            "## Description\n\nd\n\n## Notes for AI Agents\n\nn\n"
        )
        out = filter_module_sections(doc, [])
        disclaimer_line = next(line for line in out.splitlines() if line.startswith("Curated subset."))
        assert len(disclaimer_line) < 400, (
            f"disclaimer line ({len(disclaimer_line)} chars) must be far shorter than the old " f"~764-char paragraph"
        )
        # The now-removed verbose repetition must be gone.
        assert "Do not assert an exact default" not in out
        assert "confirm it in the full doc first" not in out

    # ---- #5 (independent review, 2026-07-21): context-aware footer ----

    def test_footer_served_complete_does_not_invite_a_redundant_recall(self):
        """When the caller has already guaranteed a complete root interface
        (served_complete_root_interface=True), the footer must NOT tell the
        agent to call sections=["inputs","outputs"] to get what it already
        has -- that used to invite a pointless re-call."""
        doc = (
            "---\nm: x\n---\n\n## Module Information\n\n- **Module ID**: x/y/aws\n\n"
            "## Description\n\nd\n\n## Notes for AI Agents\n\nn\n"
        )
        out = filter_module_sections(doc, [], served_complete_root_interface=True)
        assert "or to confirm a name exists, call" not in out, "Must not invite a redundant re-call"
        assert "COMPLETE inputs/outputs" in out, "Footer must still name what it already serves"
        assert "already" in out.lower(), "Footer must state the interface is already complete"
        assert "module source" in out, "Footer must still reserve escalation for what is genuinely missing"

    def test_footer_served_complete_preserves_marker_anchor(self):
        """The appendix-splice anchor (_FILTER_FOOTER_MARKER) must still
        match verbatim on a served_complete_root_interface=True footer, or
        the any-overlay appendix would silently land in the wrong place
        (see _insert_before_footer)."""
        doc = (
            "---\nm: x\n---\n\n## Module Information\n\n- **Module ID**: x/y/aws\n\n"
            "## Description\n\nd\n\n## Notes for AI Agents\n\nn\n"
        )
        out = filter_module_sections(doc, [], served_complete_root_interface=True)
        assert tfmod_mcp_server._FILTER_FOOTER_MARKER in out
        appended = tfmod_mcp_server._insert_before_footer(out, "APPENDIX", is_filtered=True)
        assert appended.index("APPENDIX") < appended.index("Curated subset.")

    def test_footer_not_served_complete_keeps_existing_wording(self):
        """served_complete_root_interface defaults to False -- byte-identical
        to the pre-#5 footer wording for every existing caller that does not
        pass it explicitly (orientation_head, and any non-inputs/outputs
        sections request)."""
        doc = (
            "---\nm: x\n---\n\n## Module Information\n\n- **Module ID**: x/y/aws\n\n"
            "## Description\n\nd\n\n## Notes for AI Agents\n\nn\n"
        )
        default_out = filter_module_sections(doc, [])
        explicit_false_out = filter_module_sections(doc, [], served_complete_root_interface=False)
        assert default_out == explicit_false_out
        assert 'call `get_module` with `sections=["inputs","outputs"]`' in default_out

    def test_orientation_head_lists_available_sections_menu(self, server_state):
        """The head advertises the full section inventory + logical-key legend as a follow-up menu."""
        head = get_module_impl("eks", server_state)
        assert "Available sections" in head, "Head must advertise the section inventory"
        assert "best-practices" in head, "Footer should list the logical keys agents can request"
        # The inventory is complete: it lists headings that are NOT expanded in the head body.
        assert "Submodule 4: karpenter" in head, "Inventory should include omitted headings"
        assert "Not included above" in head, "Head should flag which sections would expand on request"

    def test_orientation_head_surfaces_submodule_inventory_inline(self, server_state):
        """A1: the head inlines the compact ## Submodules inventory (name + source), not deep-dives."""
        head = get_module_impl("iam", server_state)
        assert "## Submodules" in head, "Submodule inventory heading should be inline in the head"
        assert (
            "terraform-aws-modules/iam/aws//modules/iam-role" in head
        ), "Inventory source strings must be inline so the agent can pin a submodule"
        # The full deep-dive submodule sections must NOT be expanded into the head body.
        assert "## Submodule 4: iam-role" not in head, "Deep-dive submodule sections must stay out of the head"
        full = get_module_impl("iam", server_state, sections=["all"])
        assert len(head) < len(full), "Inventory-in-head must still be far smaller than the full doc"

    def test_orientation_head_without_submodules_has_no_inventory(self, server_state):
        """A doc with no ## Submodules section gets no inventory heading in the head body."""
        head = get_module_impl("kms", server_state)
        assert "## Submodules" not in head, "No inventory heading when the doc has none"

    def test_filter_extra_exact_titles_are_exact_only(self):
        """extra_exact_titles includes a title by exact equality, never as a prefix match."""
        text = "# T\n\n## Submodules\ninventory body\n\n" "## Submodule 1: alpha\ndeep dive\n\n## Description\ndesc\n"
        out = filter_module_sections(text, [], extra_exact_titles=("Submodules",))
        assert "## Submodules\ninventory body" in out, "Exact 'Submodules' heading included"
        assert "## Submodule 1: alpha" not in out, "Prefix-similar deep-dive heading excluded"

    def test_sections_reduce_payload(self, server_state):
        """Test that requesting sections returns a smaller document containing them."""
        full = get_module_impl("security-group", server_state, sections=["all"])
        filtered = get_module_impl("security-group", server_state, sections=["inputs"])
        assert len(filtered) < len(full), "Filtered response should be smaller than full document"
        assert "## Main Input Variables" in filtered, "Requested inputs section should be present"

    def test_inputs_key_resolves_on_combined_scheme(self, server_state):
        """inputs resolves on docs bundling the interface into a combined section (BUG-1)."""
        filtered = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert "Requested sections not found" not in filtered, "inputs must resolve, not report missing"
        assert "## Root Module: S3 Bucket" in filtered, "Combined interface section should be pulled"

    def test_inputs_key_resolves_on_submodule_only_doc(self, server_state):
        """inputs resolves on pure submodule-collection docs via submodule fallback (BUG-1)."""
        filtered = get_module_impl("iam", server_state, sections=["inputs"])
        assert "Requested sections not found" not in filtered, "inputs must resolve, not report missing"
        assert "## Submodule 1: iam-account" in filtered, "Submodule sections should be pulled"

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
        assert "Available sections" in filtered, "Footer should advertise the full section inventory"
        assert "Not included above" in filtered, "Footer should flag what was not expanded"
        assert "Best Practices" in filtered, "Every section title should appear in the footer menu"

    def test_freeform_heading_substring_match(self, server_state):
        """Test that free-form entries match H2 headings by substring."""
        filtered = get_module_impl("eks", server_state, sections=["karpenter"])
        assert "## Submodule 4: karpenter" in filtered, "Substring should match the submodule heading"

    def test_submodules_key_resolves_to_compact_inventory_only(self, server_state):
        """L5: the submodules key pulls the compact index, not the numbered deep-dive sections.

        The submodule NAMES/purposes/pinnable sources are already in the compact
        ## Submodules inventory (also inlined in the default head, A1); bundling
        every ## Submodule N: deep-dive alongside it was pure over-fetch. A
        specific submodule is still reachable by name (test_freeform_heading_
        substring_match) or via the //modules/<sub> address (A3).
        """
        filtered = get_module_impl("eks", server_state, sections=["submodules"])
        assert "## Submodules" in filtered, "Submodules index section should be present"
        assert "## Submodule 1:" not in filtered, "Numbered submodule deep-dive sections must not be bundled"

    def test_unmatched_section_reported(self, server_state):
        """Test that unmatched entries are reported with available sections."""
        filtered = get_module_impl("vpc", server_state, sections=["nonexistent-section-xyz"])
        assert "Requested sections not found: nonexistent-section-xyz" in filtered
        assert "Available sections" in filtered, "Footer should list available sections for retry"

    def test_filter_returns_text_without_h2_unchanged(self):
        """Test that documents without H2 sections pass through unfiltered."""
        text = "# Title\n\nJust a paragraph, no sections.\n"
        assert filter_module_sections(text, ["inputs"]) == text

    @pytest.mark.parametrize("mod", ["s3-bucket", "ecr", "lambda"])
    def test_sections_inputs_examples_no_overfetch_real_docs(self, server_state, mod):
        """BUG-1 repros: requesting inputs+examples must not drag in whole combined bundles."""
        out = get_module_impl(mod, server_state, sections=["inputs", "examples"])
        assert "Requested sections not found" not in out
        # not the whole bundle: a root/submodule ### Main Outputs sub-section must not be
        # dragged in alongside the requested inputs/examples H3s
        assert "### Main Outputs" not in out
        full = get_module_impl(mod, server_state, sections=["all"])
        assert len(out) < len(full)

    @pytest.mark.parametrize("mod", ["vpc", "redshift"])
    def test_default_head_has_root_inputs_real_docs(self, server_state, mod):
        """Default orientation head inlines root inputs for both combined (vpc) and
        split-toplevel (redshift) interface schemes."""
        out = get_module_impl(mod, server_state)
        assert "Main Input Variables" in out
        assert "Requested sections not found" not in out

    def test_collection_head_no_inputs_noise_real_doc(self, server_state):
        """iam is a pure submodule-collection doc (no Root/Main Module bundle); the default
        head must not report a spurious 'not found' for the silently-requested inputs key."""
        out = get_module_impl("iam", server_state)
        assert "Requested sections not found" not in out


class TestAnyOverlay:
    """
    Task 3 of the any-shape overlay feature: serve the committed
    model/any_overlay/<id>.json overlay (built by scripts/build_any_overlay.py,
    Tasks 1-2) on the existing get_module serve path, without rewriting the
    render subsystem. Design: evals/specs/2026-07-20-consolidated-interface-
    any-overlay-design.md ("Integration" section).

    Uses a FIXTURE overlay (tests/fixtures/any_overlay/) against the real,
    committed s3-bucket doc -- real model/any_overlay/*.json data is built and
    reviewed in a later step; the real directory stays .gitkeep-only.
    """

    @pytest.fixture
    def any_overlay_dir(self, monkeypatch):
        """Point the server at the fixture overlay directory instead of the
        (currently empty, .gitkeep-only) real model/any_overlay/."""
        monkeypatch.setattr(tfmod_mcp_server, "_ANY_OVERLAY_DIR", ANY_OVERLAY_FIXTURES)
        return ANY_OVERLAY_FIXTURES

    # ---- guard: anti-silent-no-op (the primary Task 3 requirement) ----

    def test_inputs_section_appends_block_for_every_overlay_var(self, server_state, any_overlay_dir):
        """Every var key in the fixture overlay gets an appended block in
        sections=["inputs"] output -- including fixture_no_row_var and
        fixture_honest_any_var, which have NO row at all in s3-bucket's real
        Main Input Variables table (appendix-anchored, not row-anchored)."""
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        for var_name in ("versioning", "lifecycle_rule", "fixture_no_row_var", "fixture_honest_any_var"):
            assert var_name in out, f"overlay var {var_name!r} missing from rendered inputs section"

    def test_honest_any_var_note_rendered(self, server_state, any_overlay_dir):
        """A var with no example and no field names still gets its honest note,
        never a fabricated example."""
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert "test fixture honest-any case" in out

    def test_example_rendered_as_fenced_hcl(self, server_state, any_overlay_dir):
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert "```hcl" in out
        assert "versioning = {" in out
        assert "enabled = true" in out

    def test_field_names_rendered_and_labeled(self, server_state, any_overlay_dir):
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert "made_up_field" in out
        assert "Field names read by the module source" in out
        assert "use them directly" in out

    def test_honesty_labels_present(self, server_state, any_overlay_dir):
        """The mandatory example-provenance labels from the spec are present."""
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert "Apply-verified example" in out
        assert "one accepted form" in out
        assert "grep_module_docs" not in out, "removed grep tool must never be referenced (D7, 2026-07-21)"

    def test_appendix_adds_no_new_h2_heading(self, server_state, any_overlay_dir):
        """The appendix is fenced content spliced into the existing response --
        it must not introduce a new top-level (H2) heading."""
        content = get_module_documentation("s3-bucket", server_state)
        # D7 Change A: s3-bucket has a resolvable root bundle, so get_module_impl
        # scopes the default inputs view to root only -- match that here.
        baseline = filter_module_sections(content, ["inputs"], interface_scope="root")
        overlaid = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert len(overlaid) > len(baseline), "overlay content should have been appended"
        assert re.findall(r"(?m)^## ", overlaid) == re.findall(r"(?m)^## ", baseline)

    def test_appendix_absent_when_inputs_not_requested(self, server_state, any_overlay_dir):
        """A sections request unrelated to inputs must not gain any-overlay content."""
        out = get_module_impl("s3-bucket", server_state, sections=["outputs"])
        assert "fixture_no_row_var" not in out
        assert "any-overlay" not in out

    def test_full_doc_view_also_gets_appendix(self, server_state, any_overlay_dir):
        """sections=["all"] (the full-document escape hatch) also gets the
        appendix -- it is a non-head view exactly like sections=["inputs"]."""
        full = get_module_impl("s3-bucket", server_state, sections=["all"])
        assert "fixture_no_row_var" in full

    # ---- full-doc appendix placement: true end, never a mid-document "---" ----

    def test_full_doc_appendix_lands_after_all_real_content_not_mid_document(self, server_state, any_overlay_dir):
        """cloudwatch.md carries a decorative "---" rule mid-document (before
        "## Submodule 1: log-group", ~16% through the file) that is NOT
        filter_module_sections' own generated footer -- the raw
        sections=["all"] escape hatch returns the document verbatim, so
        rfind-ing a bare "---" used to anchor the appendix there instead of
        at the true end. The appendix must land after the LAST real section
        (the final submodule), not before it."""
        full = get_module_impl("cloudwatch", server_state, sections=["all"])
        marker_idx = full.index("fixture_cloudwatch_marker")
        last_submodule_idx = full.rindex("## Submodule 13: log-anomaly-detector")
        assert marker_idx > last_submodule_idx, "appendix must land after the last submodule section, not mid-document"
        # The decorative "---" is still present, verbatim, well before the appendix.
        decorative_idx = full.index("\n---\n")
        assert decorative_idx < last_submodule_idx < marker_idx

    def test_insert_before_footer_full_doc_always_appends_at_strict_end(self):
        """Unit-level: is_filtered=False (the raw full-document path) must
        never search for a "---" marker at all -- always strict end-append,
        even when the raw text contains a decorative mid-document rule."""
        raw = "# Doc\n\nSome intro.\n\n---\n\n## Section\n\nBody text.\n"
        out = tfmod_mcp_server._insert_before_footer(raw, "APPENDIX", is_filtered=False)
        assert out.index("APPENDIX") > out.rindex("Body text.")

    def test_insert_before_footer_filtered_anchors_on_real_footer_not_bare_dash(self):
        """Unit-level: is_filtered=True must anchor on filter_module_sections'
        own distinctive footer prefix, not a bare "---" -- so a decorative
        rule inside KEPT section body content (a hypothetical future doc
        shape) can never be mistaken for the real footer."""
        rendered = (
            "## Description\n\nSome body text with a decorative rule below.\n\n---\n\nMore body text.\n\n"
            "---\nCurated subset. For the COMPLETE inputs/outputs ...\n"
            "Available sections ...\n"
        )
        out = tfmod_mcp_server._insert_before_footer(rendered, "APPENDIX", is_filtered=True)
        assert out.index("APPENDIX") > out.index("More body text.")
        assert out.index("APPENDIX") < out.index("Curated subset.")

    # ---- --network none / no-fetch ----

    def test_no_network_access_serving_overlay(self, server_state, any_overlay_dir, monkeypatch):
        """Committed overlay = static data -- get_module makes zero network
        calls while serving it. get_module stays 100% network-decoupled; since
        D7 (2026-07-21) this server makes no live Registry reads at all -- the
        tool that used to (grep_module_docs) was removed outright."""

        def _blocked(*_args, **_kwargs):
            raise AssertionError("network access attempted while serving get_module")

        monkeypatch.setattr(socket.socket, "connect", _blocked)
        monkeypatch.setattr(socket, "create_connection", _blocked)
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert "versioning" in out
        assert "lifecycle_rule" in out

    # ---- head view: cell-substitution only, cap contract intact ----

    def test_head_substitutes_any_type_cell_for_overlay_var(self, server_state, any_overlay_dir):
        """`versioning` is within the head's capped sample rows; its `any` Type
        cell is replaced with a sections=["inputs"] pointer."""
        head = get_module_impl("s3-bucket", server_state)
        assert 'sections=["inputs"]' in head

    def test_head_never_inlines_example_or_field_list(self, server_state, any_overlay_dir):
        head = get_module_impl("s3-bucket", server_state)
        assert "```hcl" not in head, "Head must never inline example blocks (token budget)"
        assert "field names observed" not in head.lower(), "Head must not inline the field-name checklist"
        assert "fixture_no_row_var" not in head

    def test_head_has_no_below_wording(self, server_state, any_overlay_dir):
        head = get_module_impl("s3-bucket", server_state)
        assert "below" not in head.lower()

    def test_head_cap_contract_intact_with_overlay(self, server_state, any_overlay_dir):
        """The head's bounded-sample cap (_cap_head_input_table) still fires
        with an overlay present -- the substitution runs before it and does
        not defeat it."""
        head = get_module_impl("s3-bucket", server_state)
        full = get_module_impl("s3-bucket", server_state, sections=["all"])
        assert len(head) < len(full)
        assert "more inputs" in head, "cap pointer line must still be present"

    # ---- Fix 1 (2026-07-21): inline the field-name hint AT the input-table
    # row, not only in the appendix below it -- an A/B eval measured a worker
    # reading the table, seeing bare `any`, and grepping instead of scrolling
    # down to the appendix. ----

    def test_inputs_table_cell_inlines_field_names_for_overlay_var(self, server_state, any_overlay_dir):
        """`lifecycle_rule`'s Type cell in the sections=["inputs"] TABLE gets
        its overlay field names inlined, capped at 6 with a "+N more" tail,
        and a pointer to the example -- the row splits into the same 4
        columns as every other row (pipe-structure intact)."""
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        cells = _input_row_cells(out, "lifecycle_rule")
        assert len(cells) == 4, "row must still split into exactly 4 columns"
        assert cells[1] == (
            "any -- fields: id, enabled, status, expiration, transition, filter, +2 more; example below"
        ), f"unexpected rendered Type cell: {cells[1]!r}"
        # The full field list (including the 7th/8th names dropped from the
        # capped cell) still lives in the appendix, one call away.
        assert "abort_incomplete_multipart_upload_days" in out

    def test_inputs_table_cell_field_names_capped_at_six(self, server_state, any_overlay_dir):
        """Never more than 6 names inlined before the "+N more" tail (token
        budget / one-line-per-row) -- the 7th/8th overlay field names must
        not leak into the Type cell itself, only be folded into the count."""
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        cells = _input_row_cells(out, "lifecycle_rule")
        assert "+2 more" in cells[1]
        assert "tags" not in cells[1], "7th field name must not leak into the capped Type cell"
        assert "abort_incomplete_multipart_upload_days" not in cells[1], "8th field name must not leak either"

    def test_inputs_table_cell_example_only_var_gets_pointer_no_fields(self, server_state, any_overlay_dir):
        """`website` has an overlay example but no field names -- its cell
        points at the example, without a false "fields:" list."""
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        cells = _input_row_cells(out, "website")
        assert cells[1] == "any -- see any-overlay example below"

    def test_inputs_table_cell_fields_only_var_has_no_example_claim(self, server_state, any_overlay_dir):
        """`object_lock_configuration` has overlay field names but NO
        example -- the cell must not claim "example below" when the
        appendix will not actually render one for this var (honesty)."""
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        cells = _input_row_cells(out, "object_lock_configuration")
        assert cells[1] == "any -- fields: mode, days"

    def test_inputs_table_cell_honest_any_row_left_bare(self, server_state, any_overlay_dir):
        """`logging` has an overlay entry with neither example nor field
        names (honest-any) -- its real table row is left exactly as the
        curated doc wrote it."""
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        cells = _input_row_cells(out, "logging")
        assert cells[1] == "`any`"

    def test_inputs_table_cell_no_overlay_var_row_untouched(self, server_state, any_overlay_dir):
        """A row with no overlay entry at all (e.g. a bool/string-typed
        input) is completely unaffected."""
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        cells = _input_row_cells(out, "create_bucket")
        assert cells[1] == "`bool`"

    def test_full_doc_view_also_gets_inlined_cell(self, server_state, any_overlay_dir):
        """The full-document escape hatch (sections=["all"]) gets the same
        inline cell treatment as sections=["inputs"] -- same non-head family."""
        full = get_module_impl("s3-bucket", server_state, sections=["all"])
        cells = _input_row_cells(full, "lifecycle_rule")
        assert cells[1].startswith("any -- fields:")

    def test_head_still_unaffected_by_fix_1(self, server_state, any_overlay_dir):
        """The head keeps pointing to sections=["inputs"] only -- Fix 1 never
        inlines field names into the head's capped table."""
        head = get_module_impl("s3-bucket", server_state)
        assert 'sections=["inputs"]' in head
        assert "fields:" not in head
        assert "example below" not in head

    def test_elasticache_log_delivery_configuration_cell_matches_real_overlay(self, server_state):
        """Same scenario the report is asked to show: elasticache's real
        (committed, not fixture) any-overlay inlines
        `log_delivery_configuration`'s field names AT its real Main Module
        table row -- exercised against the actual model/any_overlay data,
        not the fixture. The real elasticache overlay now also carries
        `all_inputs` (2026-07-21 complete-interface-in-one-call fix), so the
        table row grew from 4 to 5 columns (Variable/Type/Required/Default/
        Description) -- the Type cell (index 1) is unaffected by that
        column-count change."""
        out = get_module_impl("elasticache", server_state, sections=["inputs"])
        cells = _input_row_cells(out, "log_delivery_configuration")
        assert len(cells) == 5, "row must split into exactly 5 columns now that all_inputs supersedes the table"
        assert cells[1].startswith("any -- fields: ")
        assert "example below" in cells[1]

    # ---- Fix 2 (2026-07-21): reworded appendix labels no longer invite a
    # confirmatory grep_module_docs round-trip; D7 (2026-07-21) then removed
    # grep_module_docs outright, so the labels now route to the module
    # source directly instead of a live-grep tool. ----

    def test_appendix_labels_no_longer_say_confirm_shapes_via_grep(self, server_state, any_overlay_dir):
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert "confirm shapes via" not in out
        assert "not a schema" not in out
        assert "grep_module_docs" not in out, "removed grep tool must never be referenced"

    def test_appendix_field_name_label_says_use_them_directly(self, server_state, any_overlay_dir):
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert "Field names read by the module source" in out
        assert "use them directly" in out
        assert "deep nested sub-shape" in out

    def test_appendix_example_label_says_copy_and_adapt(self, server_state, any_overlay_dir):
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert "copy and adapt this" in out
        assert "one accepted form" in out, "one-accepted-form caveat must survive the reword"
        assert "for fields beyond this example, consult the module source directly" in out

    # ---- no regression: a module with no overlay is byte-identical ----

    def test_module_without_overlay_is_byte_identical(self, server_state, any_overlay_dir):
        """vpc has no matching overlay file in the fixture dir -- its rendered
        output (head and sections=["inputs"]) is unaffected."""
        content = get_module_documentation("vpc", server_state)

        head_baseline = orientation_head(content)
        head_with_dir = get_module_impl("vpc", server_state)
        assert head_with_dir == head_baseline

        # D7 Change A: vpc has a resolvable root bundle, so get_module_impl
        # scopes the default inputs view to root only -- match that here.
        inputs_baseline = filter_module_sections(content, ["inputs"], interface_scope="root")
        inputs_with_dir = get_module_impl("vpc", server_state, sections=["inputs"])
        assert inputs_with_dir == inputs_baseline

    def test_no_overlay_directory_present_is_unaffected(self, server_state, monkeypatch, tmp_path):
        """When _ANY_OVERLAY_DIR holds no matching overlay file, every module
        renders unchanged (isolated from the committed model/any_overlay/ data).
        D7 Change A: s3-bucket and vpc both have a resolvable root bundle, so
        their default inputs view is root-scoped; iam has none (a pure
        submodule-collection doc), so its fallback still walks every
        submodule (BUG-1) -- interface_scope must match per module."""
        monkeypatch.setattr(tfmod_mcp_server, "_ANY_OVERLAY_DIR", tmp_path)
        for mod, interface_scope in (("s3-bucket", "root"), ("vpc", "root"), ("iam", "all")):
            content = get_module_documentation(mod, server_state)
            assert get_module_impl(mod, server_state) == orientation_head(content)
            assert get_module_impl(mod, server_state, sections=["inputs"]) == filter_module_sections(
                content, ["inputs"], interface_scope=interface_scope
            )

    # ---- version skew label ----

    def test_version_skew_label_when_built_from_differs_from_doc_pin(self):
        overlay = {
            "built_from_version": "5.10.0",
            "vars": {"root::x": {"examples": ["x = {}"], "field_names": [], "provenance": "example"}},
        }
        rendered = tfmod_mcp_server._render_any_overlay_appendix(overlay, "5.14.1")
        assert "5.10.0" in rendered
        assert "5.14.1" in rendered
        assert "verify" in rendered.lower()

    def test_no_skew_label_when_versions_match(self):
        overlay = {
            "built_from_version": "5.14.1",
            "vars": {"root::x": {"examples": ["x = {}"], "field_names": [], "provenance": "example"}},
        }
        rendered = tfmod_mcp_server._render_any_overlay_appendix(overlay, "5.14.1")
        assert "verify" not in rendered.lower()

    # ---- token bloat: shared honesty labels hoisted once, not per var ----

    def test_shared_example_label_rendered_once_not_per_var(self):
        """The example-provenance honesty sentence must be hoisted to a
        one-time appendix intro, not repeated once per var -- on a module
        with many any-vars (s3-bucket has ~20) the repeated ~230-char
        sentence was the dominant token cost."""
        vars_obj = {
            f"root::v{i}": {"examples": [f"v{i} = {{}}"], "field_names": [], "provenance": "example"} for i in range(5)
        }
        overlay = {"built_from_version": "5.14.1", "vars": vars_obj}
        rendered = tfmod_mcp_server._render_any_overlay_appendix(overlay, "5.14.1")
        assert rendered.count("Apply-verified example from") == 1
        for i in range(5):
            assert f"v{i} = {{}}" in rendered

    def test_shared_field_names_label_rendered_once_not_per_var(self):
        vars_obj = {
            f"root::v{i}": {"examples": [], "field_names": [f"field_{i}"], "provenance": "names-only"} for i in range(5)
        }
        overlay = {"built_from_version": "5.14.1", "vars": vars_obj}
        rendered = tfmod_mcp_server._render_any_overlay_appendix(overlay, "5.14.1")
        assert rendered.count("Field names read by the module source") == 1
        for i in range(5):
            assert f"field_{i}" in rendered

    def test_version_skew_notice_rendered_once_not_per_var(self):
        vars_obj = {
            f"root::v{i}": {"examples": [f"v{i} = {{}}"], "field_names": [], "provenance": "example"} for i in range(5)
        }
        overlay = {"built_from_version": "5.10.0", "vars": vars_obj}
        rendered = tfmod_mcp_server._render_any_overlay_appendix(overlay, "5.14.1")
        assert rendered.count("Version skew") == 1

    def test_per_var_block_has_no_repeated_boilerplate(self):
        """A single var's own rendered block must not carry the shared
        honesty sentences -- those live only in the appendix intro now."""
        entry = {"examples": ["x = 1"], "field_names": ["a", "b"], "provenance": "example+names"}
        block = tfmod_mcp_server._render_any_overlay_var_block("root::x", entry, "5.14.1")
        assert "Apply-verified example from" not in block
        assert "Field names observed in module source" not in block
        assert "a" in block
        assert "b" in block
        assert "example+names" in block  # provenance tag now carried per block

    def test_appendix_overhead_drops_materially_on_heavy_module(self):
        """Re-measurement per the MAJOR 3 fix: on a heavy module
        (s3-bucket-shaped, 19 any-vars each with a real-sized example +
        field-name list), hoisting the shared honesty labels out of the
        per-var loop must cut the total appendix size materially (target:
        roughly halve on the heaviest module). Measured before this fix:
        16041 chars for this exact synthetic shape; after hoisting, 11233
        chars (~30% smaller). The remaining size is real per-var content
        (the example HCL and the field-name list itself, which this fix
        deliberately does not touch -- no honesty loss, and the example cap
        stays in force) rather than repeated boilerplate, so a full halving
        is not achievable without dropping real information; the assertion
        below guards the material reduction actually delivered."""
        example = (
            "lifecycle_rule = [\n"
            "  {\n"
            '    id      = "log"\n'
            "    enabled = true\n\n"
            "    filter = {\n"
            '      prefix = "log/"\n'
            "    }\n\n"
            "    transition = [\n"
            "      {\n"
            "        days          = 30\n"
            '        storage_class = "STANDARD_IA"\n'
            "      }\n"
            "    ]\n\n"
            "    expiration = {\n"
            "      days = 365\n"
            "    }\n"
            "  }\n"
            "]"
        )
        field_names = [
            "id",
            "enabled",
            "status",
            "expiration",
            "transition",
            "storage_class",
            "noncurrent_version_expiration",
            "noncurrent_version_transition",
            "filter",
            "prefix",
            "tags",
            "tag",
            "abort_incomplete_multipart_upload_days",
        ]
        vars_obj = {
            f"root::any_var_{i}": {"examples": [example], "field_names": field_names, "provenance": "example+names"}
            for i in range(19)
        }
        overlay = {"built_from_version": "5.14.1", "vars": vars_obj}
        rendered = tfmod_mcp_server._render_any_overlay_appendix(overlay, "5.14.1")
        assert len(rendered) < 16041 * 0.75

    # ---- _load_any_overlay: fail-safe on anything unexpected ----

    def test_load_any_overlay_missing_file_returns_none(self, any_overlay_dir):
        assert tfmod_mcp_server._load_any_overlay("terraform-aws-modules/does-not-exist/aws") is None

    def test_load_any_overlay_no_module_id_returns_none(self, any_overlay_dir):
        assert tfmod_mcp_server._load_any_overlay("") is None

    def test_load_any_overlay_malformed_json_returns_none(self, tmp_path, monkeypatch):
        (tmp_path / "x__y__aws.json").write_text("{not valid json", encoding="utf-8")
        monkeypatch.setattr(tfmod_mcp_server, "_ANY_OVERLAY_DIR", tmp_path)
        assert tfmod_mcp_server._load_any_overlay("x/y/aws") is None

    def test_load_any_overlay_wrong_shape_returns_none(self, tmp_path, monkeypatch):
        (tmp_path / "x__y__aws.json").write_text('["not", "a", "dict"]', encoding="utf-8")
        monkeypatch.setattr(tfmod_mcp_server, "_ANY_OVERLAY_DIR", tmp_path)
        assert tfmod_mcp_server._load_any_overlay("x/y/aws") is None

    def test_load_any_overlay_missing_vars_key_is_valid(self, tmp_path, monkeypatch):
        """A zero-any catalog module's overlay carries all_inputs/all_outputs
        and NO `vars` key at all (not even an empty one) -- this must load
        successfully, not fail closed."""
        (tmp_path / "x__y__aws.json").write_text(
            '{"module_id": "x/y/aws", "built_from_version": "1.0.0", "all_inputs": {"root": []}}',
            encoding="utf-8",
        )
        monkeypatch.setattr(tfmod_mcp_server, "_ANY_OVERLAY_DIR", tmp_path)
        overlay = tfmod_mcp_server._load_any_overlay("x/y/aws")
        assert overlay is not None
        assert "vars" not in overlay

    def test_load_any_overlay_present_but_wrong_shape_vars_returns_none(self, tmp_path, monkeypatch):
        """A PRESENT `vars` key that is not a dict still fails the whole
        overlay closed -- only a MISSING `vars` key is treated as empty."""
        (tmp_path / "x__y__aws.json").write_text(
            '{"module_id": "x/y/aws", "built_from_version": "1.0.0", "vars": ["not", "a", "dict"]}',
            encoding="utf-8",
        )
        monkeypatch.setattr(tfmod_mcp_server, "_ANY_OVERLAY_DIR", tmp_path)
        assert tfmod_mcp_server._load_any_overlay("x/y/aws") is None


class TestAnyOverlaySubmoduleAddress:
    """MAJOR 1 fix: get_module_impl's submodule-address branch
    (module_identifier like "s3-bucket//modules/notification") used to return
    its scoped body BEFORE the any-overlay wiring, so a submodule with its
    OWN any-vars (e.g. fsx's submodule-scoped vars) never got an appendix at
    all. The fixture overlay carries a notification::-scoped var and an
    object::-scoped var (a DIFFERENT submodule) alongside the existing
    root::-scoped vars, so cross-scope leakage is directly testable.
    """

    @pytest.fixture
    def any_overlay_dir(self, monkeypatch):
        monkeypatch.setattr(tfmod_mcp_server, "_ANY_OVERLAY_DIR", ANY_OVERLAY_FIXTURES)
        return ANY_OVERLAY_FIXTURES

    def test_submodule_inputs_view_gets_scoped_overlay_appendix(self, server_state, any_overlay_dir):
        out = get_module_impl("s3-bucket//modules/notification", server_state, sections=["inputs"])
        assert "fixture_notification_var" in out
        assert "function_arn" in out

    def test_submodule_inputs_view_excludes_other_submodule_vars(self, server_state, any_overlay_dir):
        """A different submodule's (object::) overlay vars must never leak
        into the notification submodule's inputs view."""
        out = get_module_impl("s3-bucket//modules/notification", server_state, sections=["inputs"])
        assert "fixture_object_var" not in out
        assert "fixture_object_only_field" not in out

    def test_submodule_inputs_view_excludes_root_scope_vars(self, server_state, any_overlay_dir):
        """Root-scope overlay vars must never leak into a submodule's own
        scoped inputs view."""
        out = get_module_impl("s3-bucket//modules/notification", server_state, sections=["inputs"])
        assert "fixture_no_row_var" not in out
        assert "fixture_honest_any_var" not in out

    def test_different_submodule_address_gets_its_own_scoped_appendix(self, server_state, any_overlay_dir):
        """The object submodule's own address gets ITS scoped var, and none
        of notification's or root's."""
        out = get_module_impl("s3-bucket//modules/object", server_state, sections=["inputs"])
        assert "fixture_object_var" in out
        assert "fixture_object_only_field" in out
        assert "fixture_notification_var" not in out
        assert "fixture_no_row_var" not in out

    def test_submodule_full_doc_escape_hatch_gets_full_unscoped_appendix(self, server_state, any_overlay_dir):
        """sections=["all"] on a submodule address returns the complete
        PARENT document verbatim -- every scope's overlay vars belong there,
        exactly like the non-submodule full-doc escape hatch."""
        out = get_module_impl("s3-bucket//modules/notification", server_state, sections=["all"])
        assert "fixture_notification_var" in out
        assert "fixture_object_var" in out
        assert "fixture_no_row_var" in out

    def test_submodule_default_head_has_no_appendix(self, server_state, any_overlay_dir):
        """The default scoped submodule head (no explicit sections) does not
        request the inputs view explicitly -- mirrors the top-level default
        orientation head, which never gets the full appendix either."""
        out = get_module_impl("s3-bucket//modules/notification", server_state)
        assert "fixture_notification_var" not in out

    def test_submodule_unrelated_sections_have_no_appendix(self, server_state, any_overlay_dir):
        out = get_module_impl("s3-bucket//modules/notification", server_state, sections=["outputs"])
        assert "fixture_notification_var" not in out

    def test_submodule_without_overlay_match_is_unaffected(self, server_state, any_overlay_dir):
        """iam has no fixture overlay file at all -- its submodule-address
        inputs view is unaffected by this wiring."""
        content = get_module_documentation("iam", server_state)
        # submodule_scope="iam-role" mirrors get_module_impl's own call (#6
        # fix, independent review): the interface-key "inputs" fallback is
        # restricted to iam-role's own bundle only, so it no longer drags
        # every OTHER iam submodule's curated "Main Input Variables" table
        # in alongside it.
        body = filter_module_sections(content, ["iam-role", "inputs"], submodule_scope="iam-role")
        hint = tfmod_mcp_server._version_pin_hint(content)
        baseline = f"{hint}\n\n{body}" if hint else body
        out = get_module_impl("iam//modules/iam-role", server_state, sections=["inputs"])
        assert out == baseline


class TestCompleteInputTable:
    """
    complete-interface-in-one-call (2026-07-21): sections=["inputs"] serves
    the module's COMPLETE input list from the committed overlay's
    `all_inputs`, superseding the curated (possibly PARTIAL) table -- not
    just the any-typed enrichment. Design:
    evals/specs/2026-07-21-complete-interface-one-call-design.md.

    Uses the FIXTURE overlay (tests/fixtures/any_overlay/cloudwatch), whose
    all_inputs["log-group"] mirrors cloudwatch.md's real "Submodule 1:
    log-group" curated table PLUS one field (`fixture_extra_field`) absent
    from that curated table -- the anti-silent-no-op guard for this feature.
    """

    @pytest.fixture
    def any_overlay_dir(self, monkeypatch):
        monkeypatch.setattr(tfmod_mcp_server, "_ANY_OVERLAY_DIR", ANY_OVERLAY_FIXTURES)
        return ANY_OVERLAY_FIXTURES

    def test_complete_table_includes_field_absent_from_curated_doc(self, server_state, any_overlay_dir):
        """The primary anti-silent-no-op guard: a field with NO row at all in
        the curated cloudwatch.md doc now appears, because it is present in
        the overlay's all_inputs."""
        out = get_module_impl("cloudwatch", server_state, sections=["inputs"])
        assert "| `fixture_extra_field` |" in out

    def test_complete_table_still_includes_every_curated_field(self, server_state, any_overlay_dir):
        """Every field the curated table already had is preserved -- the
        supersede is a superset, not a replacement that drops rows."""
        out = get_module_impl("cloudwatch", server_state, sections=["inputs"])
        for name in (
            "create",
            "name",
            "name_prefix",
            "retention_in_days",
            "kms_key_id",
            "log_group_class",
            "skip_destroy",
            "tags",
        ):
            assert f"| `{name}` |" in out, f"{name} missing from the complete table"

    def test_complete_table_has_five_columns(self, server_state, any_overlay_dir):
        out = get_module_impl("cloudwatch", server_state, sections=["inputs"])
        cells = _input_row_cells(out, "fixture_extra_field")
        assert len(cells) == 5, "Variable | Type | Required | Default | Description"
        assert cells[0] == "`fixture_extra_field`"
        assert cells[1] == "`string`"
        assert cells[2] == "No"
        assert cells[3] == "`null`"
        assert cells[4] == "Fixture-only field absent from the curated table, proving supersede completeness"

    def test_complete_table_preserves_curated_description(self, server_state, any_overlay_dir):
        """`kms_key_id`'s row keeps the human-curated description verbatim
        (the overlay fixture's own description text is identical to the
        curated one on purpose, so a passing assertion here really exercises
        the curated-description lookup rather than a coincidence)."""
        out = get_module_impl("cloudwatch", server_state, sections=["inputs"])
        cells = _input_row_cells(out, "kms_key_id")
        assert cells[4] == "ARN of KMS key used to encrypt log data"

    def test_other_submodule_tables_unaffected(self, server_state, any_overlay_dir):
        """log-stream has no all_inputs entry -- its curated table (still 4
        columns) is untouched by the log-group supersede."""
        out = get_module_impl("cloudwatch", server_state, sections=["inputs"])
        start = out.index("## Submodule 2: log-stream")
        end = out.index("## Submodule 3: log-metric-filter")
        block = out[start:end]
        header_line = next(line for line in block.splitlines() if line.startswith("| Variable"))
        assert header_line == "| Variable | Type | Default | Description |"

    def test_any_overlay_appendix_still_present_alongside_complete_table(self, server_state, any_overlay_dir):
        """The pre-existing any-overlay appendix (root::fixture_cloudwatch_marker)
        still renders even though log-group's table structure changed."""
        out = get_module_impl("cloudwatch", server_state, sections=["inputs"])
        assert "fixture_cloudwatch_marker" in out

    def test_head_unchanged_byte_identical(self, server_state, any_overlay_dir):
        """The default orientation head never gets the complete table -- byte
        identical to the pre-feature head."""
        content = get_module_documentation("cloudwatch", server_state)
        baseline = orientation_head(content)
        head = get_module_impl("cloudwatch", server_state)
        assert head == baseline

    def test_full_doc_escape_hatch_also_gets_complete_table(self, server_state, any_overlay_dir):
        full = get_module_impl("cloudwatch", server_state, sections=["all"])
        assert "| `fixture_extra_field` |" in full

    def test_submodule_address_inputs_gets_complete_table(self, server_state, any_overlay_dir):
        """A submodule-address request (e.g. cloudwatch//modules/log-group)
        also gets the complete table for its own scope."""
        out = get_module_impl("cloudwatch//modules/log-group", server_state, sections=["inputs"])
        assert "| `fixture_extra_field` |" in out

    def test_module_with_no_all_inputs_key_is_byte_identical(self, server_state, any_overlay_dir):
        """s3-bucket's FIXTURE overlay has vars but no all_inputs key at all --
        its sections=["inputs"] output is unaffected (graceful fallback), aside
        from D7 Change A's root-only scoping (s3-bucket has a resolvable root
        bundle) -- no submodule-interface menu either, since with no
        all_inputs/all_outputs key there is nothing to advertise."""
        content = get_module_documentation("s3-bucket", server_state)
        baseline = filter_module_sections(content, ["inputs"], interface_scope="root")
        baseline = tfmod_mcp_server._inline_any_overlay_input_cells(baseline, content)
        baseline = tfmod_mcp_server._with_any_overlay_appendix(baseline, content, is_filtered=True)
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert out == baseline

    def test_no_overlay_module_byte_identical(self, server_state, any_overlay_dir):
        """A module with no overlay file at all (vpc, in the fixture dir) is
        completely unaffected, aside from D7 Change A's root-only scoping
        (vpc has a resolvable root bundle)."""
        content = get_module_documentation("vpc", server_state)
        baseline = filter_module_sections(content, ["inputs"], interface_scope="root")
        out = get_module_impl("vpc", server_state, sections=["inputs"])
        assert out == baseline

    def test_no_network_access_with_complete_input_table(self, server_state, any_overlay_dir, monkeypatch):
        """The complete-input-table supersede (all_inputs) is a static file
        read only -- zero network calls, same as the rest of get_module."""

        def _blocked(*_args, **_kwargs):
            raise AssertionError("network access attempted while serving the complete input table")

        monkeypatch.setattr(socket.socket, "connect", _blocked)
        monkeypatch.setattr(socket, "create_connection", _blocked)
        out = get_module_impl("cloudwatch", server_state, sections=["inputs"])
        assert "| `fixture_extra_field` |" in out

    # ---- unit-level: _scope_for_h2_title ----

    def test_scope_for_h2_title_root(self):
        assert tfmod_mcp_server._scope_for_h2_title("Main Module: ElastiCache", frozenset({"root"})) == "root"
        assert tfmod_mcp_server._scope_for_h2_title("Root Module: S3 Bucket", frozenset({"root"})) == "root"

    def test_scope_for_h2_title_root_absent_from_candidates(self):
        assert tfmod_mcp_server._scope_for_h2_title("Main Module: X", frozenset({"user-group"})) is None

    def test_scope_for_h2_title_submodule_exact(self):
        scopes = frozenset({"root", "user-group", "serverless-cache"})
        assert tfmod_mcp_server._scope_for_h2_title("Submodule 2: user-group", scopes) == "user-group"

    def test_scope_for_h2_title_submodule_decorated_heading(self):
        """A heading with trailing decoration (e.g. "(Recommended)") still
        resolves via substring match."""
        scopes = frozenset({"root", "flow-log", "vpc-endpoints"})
        assert tfmod_mcp_server._scope_for_h2_title("Submodule 2: flow-log (Recommended)", scopes) == "flow-log"

    def test_scope_for_h2_title_non_matching_heading(self):
        scopes = frozenset({"root", "user-group"})
        assert tfmod_mcp_server._scope_for_h2_title("Best Practices", scopes) is None
        assert tfmod_mcp_server._scope_for_h2_title("Submodules", scopes) is None


class TestElasticacheRealAllInputs:
    """Real-data check (not fixture): the committed
    model/any_overlay/terraform-aws-modules__elasticache__aws.json now
    carries all_inputs, so sections=["inputs"] must include the fields that
    were measured missing from the curated .md table -- the root-cause
    finding of the complete-interface-in-one-call design (evals/specs/
    2026-07-21-complete-interface-one-call-design.md)."""

    def test_previously_missing_fields_now_present(self, server_state):
        out = get_module_impl("elasticache", server_state, sections=["inputs"])
        for name in (
            "create_subnet_group",
            "create_security_group",
            "subnet_group_name",
            "preferred_cache_cluster_azs",
            "parameter_group_name",
            "port",
        ):
            assert f"| `{name}` |" in out, f"{name} still missing from sections=['inputs']"

    def test_real_zero_any_module_gets_complete_input_table(self, server_state):
        """Full-catalog extension (2026-07-21): rds has zero any-vars, but as
        of the all-63-catalog build it now DOES get a committed overlay --
        carrying all_inputs/all_outputs with no `vars` key. rds.md is also
        split-scheme (no "## Main Module:" bundle, no submodules), so this
        doubles as the real-data end-to-end proof for the
        `_scope_for_h2_title` split-scheme fix. Fields the curated table never
        listed (it documents a curated subset, not the full registry
        interface) must now appear via the complete-table supersede."""
        out = get_module_impl("rds", server_state, sections=["inputs"])
        for name in ("ca_cert_identifier", "auto_minor_version_upgrade", "copy_tags_to_snapshot"):
            assert f"| `{name}` |" in out, f"{name} still missing from sections=['inputs']"

    def test_real_zero_any_module_gets_no_vars_enrichment(self, server_state):
        """rds has no `type = any` inputs at all, so its overlay carries no
        `vars` -- no any-cell hint, no any-overlay appendix, ever."""
        out = get_module_impl("rds", server_state, sections=["inputs"])
        assert "any -- fields:" not in out
        assert "any-typed input overlay" not in out


class TestCompleteOutputTable:
    """
    complete-interface-in-one-call, outputs half: sections=["outputs"] serves
    the module's COMPLETE output list from the committed overlay's
    `all_outputs`, superseding the curated (possibly PARTIAL) table -- the
    same fix TestCompleteInputTable exercises for inputs, mirrored for
    outputs. Design: evals/specs/2026-07-21-complete-interface-one-call-
    design.md.

    Uses the FIXTURE overlay (tests/fixtures/any_overlay/cloudwatch), whose
    all_outputs["log-group"] mirrors cloudwatch.md's real "Submodule 1:
    log-group" curated table PLUS one field (`fixture_extra_output`) absent
    from that curated table -- the anti-silent-no-op guard for this feature.
    """

    @pytest.fixture
    def any_overlay_dir(self, monkeypatch):
        monkeypatch.setattr(tfmod_mcp_server, "_ANY_OVERLAY_DIR", ANY_OVERLAY_FIXTURES)
        return ANY_OVERLAY_FIXTURES

    def test_complete_table_includes_field_absent_from_curated_doc(self, server_state, any_overlay_dir):
        """The primary anti-silent-no-op guard: an output with NO row at all
        in the curated cloudwatch.md doc now appears, because it is present
        in the overlay's all_outputs."""
        out = get_module_impl("cloudwatch", server_state, sections=["outputs"])
        assert "| `fixture_extra_output` |" in out

    def test_complete_table_still_includes_every_curated_field(self, server_state, any_overlay_dir):
        """Every output the curated table already had is preserved -- the
        supersede is a superset, not a replacement that drops rows."""
        out = get_module_impl("cloudwatch", server_state, sections=["outputs"])
        for name in ("cloudwatch_log_group_name", "cloudwatch_log_group_arn"):
            assert f"| `{name}` |" in out, f"{name} missing from the complete table"

    def test_complete_table_has_two_columns(self, server_state, any_overlay_dir):
        out = get_module_impl("cloudwatch", server_state, sections=["outputs"])
        cells = _output_row_cells(out, "fixture_extra_output")
        assert len(cells) == 2, "Output | Description"
        assert cells[0] == "`fixture_extra_output`"
        assert cells[1] == "Fixture-only output absent from the curated table, proving supersede completeness"

    def test_complete_table_preserves_curated_description(self, server_state, any_overlay_dir):
        """`cloudwatch_log_group_arn`'s row keeps the human-curated
        description verbatim (the overlay fixture's own description text is
        identical to the curated one on purpose, so a passing assertion
        here really exercises the curated-description lookup rather than a
        coincidence)."""
        out = get_module_impl("cloudwatch", server_state, sections=["outputs"])
        cells = _output_row_cells(out, "cloudwatch_log_group_arn")
        assert cells[1] == "ARN of the log group"

    def test_other_submodule_tables_unaffected(self, server_state, any_overlay_dir):
        """log-stream has no all_outputs entry -- its curated table is
        untouched by the log-group supersede."""
        out = get_module_impl("cloudwatch", server_state, sections=["outputs"])
        start = out.index("## Submodule 2: log-stream")
        end = out.index("## Submodule 3: log-metric-filter")
        block = out[start:end]
        header_line = next(line for line in block.splitlines() if line.startswith("| Output"))
        assert header_line == "| Output | Description |"

    def test_head_unchanged_byte_identical(self, server_state, any_overlay_dir):
        """The default orientation head never carries outputs at all, let
        alone the complete table -- byte identical to the pre-feature head."""
        content = get_module_documentation("cloudwatch", server_state)
        baseline = orientation_head(content)
        head = get_module_impl("cloudwatch", server_state)
        assert head == baseline

    def test_full_doc_escape_hatch_also_gets_complete_table(self, server_state, any_overlay_dir):
        full = get_module_impl("cloudwatch", server_state, sections=["all"])
        assert "| `fixture_extra_output` |" in full

    def test_submodule_address_outputs_gets_complete_table(self, server_state, any_overlay_dir):
        """A submodule-address request (e.g. cloudwatch//modules/log-group)
        also gets the complete output table for its own scope."""
        out = get_module_impl("cloudwatch//modules/log-group", server_state, sections=["outputs"])
        assert "| `fixture_extra_output` |" in out

    def test_module_with_no_all_outputs_key_is_byte_identical(self, server_state, any_overlay_dir):
        """s3-bucket's FIXTURE overlay has vars but no all_outputs key at
        all -- its sections=["outputs"] output is unaffected (graceful
        fallback), aside from D7 Change A's root-only scoping (s3-bucket has
        a resolvable root bundle)."""
        content = get_module_documentation("s3-bucket", server_state)
        baseline = filter_module_sections(content, ["outputs"], interface_scope="root")
        out = get_module_impl("s3-bucket", server_state, sections=["outputs"])
        assert out == baseline

    def test_no_overlay_module_byte_identical(self, server_state, any_overlay_dir):
        """A module with no overlay file at all (vpc, in the fixture dir) is
        completely unaffected, aside from D7 Change A's root-only scoping
        (vpc has a resolvable root bundle)."""
        content = get_module_documentation("vpc", server_state)
        baseline = filter_module_sections(content, ["outputs"], interface_scope="root")
        out = get_module_impl("vpc", server_state, sections=["outputs"])
        assert out == baseline

    def test_no_network_access_with_complete_output_table(self, server_state, any_overlay_dir, monkeypatch):
        """The complete-output-table supersede (all_outputs) is a static
        file read only -- zero network calls, same as the rest of
        get_module."""

        def _blocked(*_args, **_kwargs):
            raise AssertionError("network access attempted while serving the complete output table")

        monkeypatch.setattr(socket.socket, "connect", _blocked)
        monkeypatch.setattr(socket, "create_connection", _blocked)
        out = get_module_impl("cloudwatch", server_state, sections=["outputs"])
        assert "| `fixture_extra_output` |" in out

    def test_inputs_only_request_unaffected_by_output_fixture(self, server_state, any_overlay_dir):
        """A pure sections=["inputs"] request must not gain any output-table
        content -- the two supersedes are independent."""
        out = get_module_impl("cloudwatch", server_state, sections=["inputs"])
        assert "fixture_extra_output" not in out

    def test_outputs_only_request_unaffected_by_input_fixture(self, server_state, any_overlay_dir):
        """A pure sections=["outputs"] request must not gain any input-table
        content (nor the any-overlay input appendix) -- the two supersedes
        are independent."""
        out = get_module_impl("cloudwatch", server_state, sections=["outputs"])
        assert "fixture_extra_field" not in out
        assert "fixture_cloudwatch_marker" not in out


class TestNoVarsOverlaySplitScheme:
    """
    Full-catalog extension (2026-07-21): every one of the 63 catalog modules
    now gets a committed overlay carrying all_inputs/all_outputs, but only
    modules with at least one `type = any` input also carry a `vars` key. Two
    things must hold for the ~41 zero-any modules:

    1. `_load_any_overlay` must accept an overlay with NO `vars` key at all
       (not just an empty `vars: {}`) -- it used to require `vars` to be a
       present dict, which would silently reject every such overlay.
    2. The complete-table supersede must actually fire for the SPLIT-SCHEME
       corpus (48 of 63 docs, e.g. rds.md) -- a doc with no submodules, whose
       "Main Input Variables"/"Main Outputs" table sits directly under its
       own top-level H2, not wrapped in a "Main Module: X" bundle. Without a
       root-scope match for that bare heading, `_scope_for_h2_title` always
       returned None for these docs and the supersede silently no-opped on
       the majority of the catalog.

    Uses a FIXTURE overlay (tests/fixtures/any_overlay/rds.json) with
    all_inputs/all_outputs at "root" scope and NO "vars" key, against the
    real, committed rds.md doc (confirmed split-scheme: no "## Main Module:"/
    "## Submodules" heading at all).
    """

    @pytest.fixture
    def any_overlay_dir(self, monkeypatch):
        monkeypatch.setattr(tfmod_mcp_server, "_ANY_OVERLAY_DIR", ANY_OVERLAY_FIXTURES)
        return ANY_OVERLAY_FIXTURES

    def test_load_any_overlay_accepts_missing_vars_key(self, any_overlay_dir):
        overlay = tfmod_mcp_server._load_any_overlay("terraform-aws-modules/rds/aws")
        assert overlay is not None
        assert "vars" not in overlay
        assert overlay["all_inputs"]["root"][0]["name"] == "identifier"

    def test_complete_input_table_fires_for_split_scheme_doc(self, server_state, any_overlay_dir):
        """The primary anti-silent-no-op guard for the split-scheme fix: a
        field with no row at all in the curated rds.md doc now appears."""
        out = get_module_impl("rds", server_state, sections=["inputs"])
        assert "| `fixture_extra_field` |" in out

    def test_complete_input_table_preserves_curated_rows_and_description(self, server_state, any_overlay_dir):
        out = get_module_impl("rds", server_state, sections=["inputs"])
        cells = _input_row_cells(out, "identifier")
        assert cells[4] == "Name of the RDS instance"

    def test_complete_output_table_fires_for_split_scheme_doc(self, server_state, any_overlay_dir):
        out = get_module_impl("rds", server_state, sections=["outputs"])
        assert "| `fixture_extra_output` |" in out

    def test_complete_output_table_preserves_curated_description(self, server_state, any_overlay_dir):
        out = get_module_impl("rds", server_state, sections=["outputs"])
        cells = _output_row_cells(out, "db_instance_endpoint")
        assert cells[1] == "Connection endpoint (`hostname:port`)"

    def test_no_any_cell_hint_injected_without_vars(self, server_state, any_overlay_dir):
        """No `vars` key -> no any-typed cell substitution anywhere (there is
        nothing to hint at)."""
        out = get_module_impl("rds", server_state, sections=["inputs"])
        assert "any -- fields:" not in out
        assert "any -- see any-overlay example below" not in out

    def test_no_any_overlay_appendix_injected_without_vars(self, server_state, any_overlay_dir):
        """No `vars` key -> the any-overlay appendix (example HCL / field
        list block) never renders -- `_render_any_overlay_appendix` returns
        "" for an empty vars_obj, so `_insert_before_footer` is a no-op."""
        out = get_module_impl("rds", server_state, sections=["inputs"])
        assert "any-typed input overlay" not in out

    def test_does_not_crash_on_full_doc_escape_hatch(self, server_state, any_overlay_dir):
        out = get_module_impl("rds", server_state, sections=["all"])
        assert "| `fixture_extra_field` |" in out
        assert "| `fixture_extra_output` |" in out

    def test_head_unchanged_byte_identical(self, server_state, any_overlay_dir):
        """The default orientation head never gets the complete table --
        byte-identical to the pre-feature head even with a no-vars overlay
        present."""
        content = get_module_documentation("rds", server_state)
        baseline = orientation_head(content)
        head = get_module_impl("rds", server_state)
        assert head == baseline

    # ---- unit-level: _scope_for_h2_title split-scheme root resolution ----

    def test_scope_for_h2_title_split_scheme_input_heading(self):
        assert tfmod_mcp_server._scope_for_h2_title("Main Input Variables", frozenset({"root"})) == "root"

    def test_scope_for_h2_title_split_scheme_output_headings(self):
        assert tfmod_mcp_server._scope_for_h2_title("Main Outputs", frozenset({"root"})) == "root"
        assert tfmod_mcp_server._scope_for_h2_title("Key Outputs", frozenset({"root"})) == "root"

    def test_scope_for_h2_title_split_scheme_root_absent_from_candidates(self):
        """A doc whose overlay has no "root" scope (e.g. cloudwatch, which
        is submodule-only) must not resolve the bare heading to "root"."""
        assert tfmod_mcp_server._scope_for_h2_title("Main Input Variables", frozenset({"log-group"})) is None


class TestElasticacheRealAllOutputs:
    """Real-data check (not fixture): the committed
    model/any_overlay/terraform-aws-modules__elasticache__aws.json now also
    carries all_outputs, so sections=["outputs"] must include output names
    the curated .md table omits entirely."""

    def test_previously_missing_outputs_now_present(self, server_state):
        out = get_module_impl("elasticache", server_state, sections=["outputs"])
        for name in (
            "cloudwatch_log_group_arn",
            "cloudwatch_log_group_name",
            "global_replication_group_engine_version_actual",
        ):
            assert f"| `{name}` |" in out, f"{name} still missing from sections=['outputs']"

    def test_measured_names_present_as_individual_rows(self, server_state):
        """The exact output names this fix was reported against -- already
        present in the curated doc (some bundled two-per-row via `/`), now
        guaranteed as their OWN row via the complete table, so an exact-name
        grep always finds them."""
        out = get_module_impl("elasticache", server_state, sections=["outputs"])
        for name in (
            "replication_group_primary_endpoint_address",
            "replication_group_id",
            "subnet_group_name",
        ):
            assert f"| `{name}` |" in out, f"{name} missing from sections=['outputs']"

    def test_real_zero_any_module_gets_complete_output_table(self, server_state):
        """Full-catalog extension (2026-07-21): rds has zero any-vars, but as
        of the all-63-catalog build it now DOES get a committed overlay --
        carrying all_inputs/all_outputs with no `vars` key. Output names the
        curated table never listed must now appear via the complete-table
        supersede."""
        out = get_module_impl("rds", server_state, sections=["outputs"])
        for name in ("db_instance_ca_cert_identifier", "db_instance_domain", "db_instance_status"):
            assert f"| `{name}` |" in out, f"{name} still missing from sections=['outputs']"


def test_extract_interface_h3_inputs_only():
    block = (
        "## Root Module: S3 Bucket\n\n"
        "### Description\n\nThe root module.\n\n"
        "### Main Input Variables\n\n| Variable | Type |\n|---|---|\n| `bucket` | `string` |\n\n"
        "### Main Outputs\n\n| Output | Description |\n|---|---|\n| `s3_bucket_id` | id |\n\n"
        "### Usage Examples\n\n#### Example 1\n\n```hcl\nx = 1\n```\n"
    )
    out = _extract_interface_h3(block, {"inputs"})
    assert "## Root Module: S3 Bucket" in out
    assert "### Main Input Variables" in out
    assert "`bucket`" in out
    assert "### Main Outputs" not in out
    assert "### Description" not in out
    assert "### Usage Examples" not in out


def test_extract_interface_h3_examples_matches_singular_and_carries_children():
    block = (
        "## Submodule 1: notification\n\n"
        "### Main Input Variables\n\n| Variable | Type |\n|---|---|\n| `bucket_id` | `string` |\n\n"
        "### Usage Example\n\n#### Example A\n\n```hcl\ny = 2\n```\n"
    )
    out = _extract_interface_h3(block, {"examples"})
    assert "### Usage Example" in out
    assert "#### Example A" in out
    assert "y = 2" in out
    assert "### Main Input Variables" not in out


def test_extract_interface_h3_no_match_returns_empty():
    block = "## Root Module: X\n\n### Description\n\nnothing here.\n"
    assert _extract_interface_h3(block, {"inputs"}) == ""


def test_extract_interface_h3_outputs_matches_key_outputs_variant():
    # ecs and a few others title the outputs H3 "Key Outputs", not "Main Outputs".
    block = (
        "## Root Module (Integrated)\n\n"
        "### Main Input Variables\n\n| V | T |\n|---|---|\n| `cluster_name` | `string` |\n\n"
        "### Key Outputs\n\n| O | D |\n|---|---|\n| `cluster_arn` | arn |\n\n"
    )
    out = _extract_interface_h3(block, {"outputs"})
    assert "### Key Outputs" in out
    assert "`cluster_arn`" in out
    assert "### Main Input Variables" not in out


def test_filter_rejects_unknown_interface_scope():
    import pytest

    with pytest.raises(ValueError, match="interface_scope"):
        filter_module_sections("## Description\n\nd\n", ["inputs"], interface_scope="rot")


def test_interface_key_whole_section_fallback_when_no_h3():
    # network-firewall style: interface lives as H3 entries under "## Submodules"
    # (no "### Main Input Variables" table anywhere) -> the key must still resolve
    # by including the whole matched section, never report "not found".
    doc = (
        "---\nm: nf\n---\n\n## Module Information\n\n- **Module ID**: x/nf/aws\n\n"
        "## Description\n\nd\n\n"
        "## Submodules\n\n### 1. firewall\n\nThe firewall submodule takes `firewall_name`.\n\n"
        "### 2. policy\n\nThe policy submodule.\n\n"
        "## Notes for AI Agents\n\nn\n"
    )
    out = filter_module_sections(doc, ["inputs"])
    assert "Requested sections not found" not in out
    assert "## Submodules" in out
    assert "firewall_name" in out


def _combined_doc():
    return (
        "---\nmodule_name: demo\n---\n\n"
        "## Module Information\n\n- **Module ID**: x/demo/aws\n\n"
        "## Description\n\nDemo.\n\n"
        "## Root Module: Demo\n\n"
        "### Main Input Variables\n\n| V | T |\n|---|---|\n| `root_in` | `string` |\n\n"
        "### Main Outputs\n\n| O | D |\n|---|---|\n| `root_out` | x |\n\n"
        "## Submodule 1: sub\n\n"
        "### Main Input Variables\n\n| V | T |\n|---|---|\n| `sub_in` | `string` |\n\n"
        "### Main Outputs\n\n| O | D |\n|---|---|\n| `sub_out` | y |\n\n"
        "## Notes for AI Agents\n\nNote.\n"
    )


def test_inputs_extracts_h3_not_whole_bundle_all_scope():
    out = filter_module_sections(_combined_doc(), ["inputs"])
    assert "`root_in`" in out and "`sub_in`" in out  # inputs from root AND submodule
    assert "root_out" not in out and "sub_out" not in out  # outputs NOT dragged in
    assert "Requested sections not found" not in out  # matched, not unmatched


def test_inputs_root_scope_excludes_submodule():
    out = filter_module_sections(_combined_doc(), ["inputs"], interface_scope="root")
    assert "`root_in`" in out
    assert "`sub_in`" not in out
    assert "root_out" not in out


def test_silent_keys_suppress_not_found():
    doc = (
        "---\nm: x\n---\n\n## Module Information\n\n- **Module ID**: x/y/aws\n\n"
        "## Description\n\nd\n\n## Submodule 1: only\n\n### Main Input Variables\n\n| V | T |\n|---|---|\n| `a` | `s` |\n\n"
        "## Notes for AI Agents\n\nn\n"
    )
    # 'features' absent here; as a silent key it must not appear in "not found"
    out = filter_module_sections(doc, ["features"], silent_keys=frozenset({"features"}))
    assert "Requested sections not found" not in out
    # without silent_keys, it IS reported
    out2 = filter_module_sections(doc, ["features"])
    assert "Requested sections not found: features" in out2


def test_head_inlines_root_inputs_combined():
    out = orientation_head(_combined_doc())  # helper from Task 2 test
    assert "### Main Input Variables" in out
    assert "`root_in`" in out
    assert "`sub_in`" not in out  # submodule inputs stay out of the head
    assert "Requested sections not found" not in out


def test_head_no_inputs_noise_for_collection_doc():
    # collection doc: only a submodule bundle, no root inputs
    doc = (
        "---\nm: coll\n---\n\n## Module Information\n\n- **Module ID**: x/coll/aws\n\n"
        "## Description\n\nd\n\n## Key Features\n\n- f\n\n## Main Use Cases\n\n- u\n\n"
        "## Submodule 1: only\n\n### Main Input Variables\n\n| V | T |\n|---|---|\n| `a` | `s` |\n\n"
        "## Notes for AI Agents\n\nn\n"
    )
    out = orientation_head(doc)
    assert "Requested sections not found" not in out
    assert "`a`" not in out  # submodule inputs not inlined in a collection head


class TestD7ChangeARootScopeDefault:
    """
    D7 Change A (2026-07-21): scope the complete inputs/outputs interface to
    the module's ROOT overlay scope by default. Root cause: concatenating
    every submodule scope's COMPLETE interface alongside root overflowed the
    MCP tool output cap on wide modules (eks measured 105200 bytes for
    sections=["inputs"], 114272 for ["inputs","outputs"] -- both over any
    sane cap). Submodule scopes stay reachable on demand via the existing
    submodule address. Design: evals/specs/2026-07-21-d7-remove-grep-scope-
    default-design.md (Change A).

    Uses the REAL committed eks overlay (8 scopes: root + 7 submodules).
    """

    def test_default_inputs_view_serves_root_scope_only(self, server_state):
        """sections=["inputs"] on eks includes a known root-only input and
        excludes a known submodule-only one (checked as its OWN table row --
        eks's root inputs pass through per-node-group config objects whose
        Type-cell text can otherwise embed submodule field names) -- the
        default response no longer concatenates every scope."""
        out = get_module_impl("eks", server_state, sections=["inputs"])
        assert "| `name` |" in out, "root-scope input must be present"
        assert (
            "| `launch_template_id` |" not in out
        ), "eks-managed-node-group-only input must not leak into the default view as its own row"
        assert "queue_kms_data_key_reuse_period_seconds" not in out, "karpenter-only input must not leak in either"
        assert "## Submodule 1: eks-managed-node-group" not in out, "submodule bundles must not be concatenated"

    def test_default_inputs_and_outputs_view_serves_root_scope_only(self, server_state):
        """Same guarantee for the combined sections=["inputs","outputs"] call
        -- the pairing that measured 114272 bytes pre-fix."""
        out = get_module_impl("eks", server_state, sections=["inputs", "outputs"])
        assert "| `name` |" in out
        assert "| `launch_template_id` |" not in out
        assert "queue_kms_data_key_reuse_period_seconds" not in out

    def test_default_inputs_view_stays_under_safety_ceiling(self, server_state):
        """The whole point of the fix: eks's default inputs response must fit
        comfortably under the tool output cap, not just be smaller than
        before."""
        out = get_module_impl("eks", server_state, sections=["inputs"])
        assert len(out.encode("utf-8")) < tfmod_mcp_server._COMPLETE_TABLE_BYTE_CAP * 2

    def test_default_inputs_and_outputs_view_stays_under_safety_ceiling(self, server_state):
        out = get_module_impl("eks", server_state, sections=["inputs", "outputs"])
        assert len(out.encode("utf-8")) < tfmod_mcp_server._COMPLETE_TABLE_BYTE_CAP * 3

    def test_submodule_address_serves_that_scope_complete_interface(self, server_state):
        """get_module("eks//modules/karpenter", sections=["inputs"]) serves
        the karpenter scope's own complete interface -- a field the curated
        table never listed at all now appears."""
        out = get_module_impl("eks//modules/karpenter", server_state, sections=["inputs"])
        assert "| `queue_kms_data_key_reuse_period_seconds` |" in out

    def test_submodule_address_does_not_serve_other_submodules_complete_data(self, server_state):
        """A field unique to a DIFFERENT submodule's overlay scope
        (eks-managed-node-group) must not leak into the karpenter address
        response."""
        out = get_module_impl("eks//modules/karpenter", server_state, sections=["inputs"])
        assert "| `launch_template_id` |" not in out

    def test_submodule_address_does_not_drag_sibling_curated_tables(self, server_state):
        """#6 (independent review): get_module("eks//modules/karpenter",
        sections=["inputs"]) used to return ~110 rows -- only ~48 of them
        karpenter's own -- because filter_module_sections' interface-key
        fallback walked EVERY combined bundle (root + every other
        submodule), not just the addressed one. The response must now carry
        only karpenter's own bundle (plus core sections), not the root
        bundle or any sibling submodule bundle."""
        out = get_module_impl("eks//modules/karpenter", server_state, sections=["inputs"])
        headings = re.findall(r"(?m)^## .+$", out)
        assert headings.count("## Submodule 4: karpenter") == 1
        for other in (
            "## Submodule 1: eks-managed-node-group",
            "## Submodule 2: self-managed-node-group",
            "## Submodule 3: fargate-profile",
            "## Submodule 5: hybrid-node-role",
            "## Submodule 6: capability",
            "## Main Module: EKS Cluster",
        ):
            assert other not in headings, f"sibling bundle {other!r} must not leak into a karpenter address response"
        row_count = out.count("\n| `")
        assert row_count < 60, f"response carries {row_count} table rows -- karpenter's overlay has only 48"

    def test_submodule_address_complete_interface_footer_stays_curated_subset(self, server_state):
        """#5 scope check: the submodule-address branch is intentionally left
        out of the served_complete_root_interface wording (it names the ROOT
        scope specifically, which would be wrong for a submodule response) --
        its footer keeps the existing curated-subset wording."""
        out = get_module_impl("eks//modules/karpenter", server_state, sections=["inputs"])
        disclaimer_line = next(line for line in out.splitlines() if line.startswith("Curated subset."))
        assert "already ARE the COMPLETE" not in disclaimer_line

    def test_root_scoped_inputs_footer_states_completeness_when_supersede_fires(self, server_state):
        """#5 (independent review): eks's root inputs supersede inline (its
        table sits directly under "### Main Input Variables"), so the
        default sections=["inputs"] response already carries the COMPLETE
        root interface -- the footer must say so instead of inviting a
        redundant sections=["inputs","outputs"] re-call."""
        out = get_module_impl("eks", server_state, sections=["inputs"])
        disclaimer_line = next(line for line in out.splitlines() if line.startswith("Curated subset."))
        assert "already ARE the COMPLETE" in disclaimer_line
        assert "or to confirm a name exists, call" not in disclaimer_line, "Must not invite a redundant re-call"
        assert '"<name>//modules/<submodule>"' in disclaimer_line

    def test_footer_lists_submodule_scope_names(self, server_state):
        """The default root-scoped response advertises the reachable
        submodule scopes and how to reach them."""
        out = get_module_impl("eks", server_state, sections=["inputs"])
        assert "Submodule interfaces available on demand" in out
        for name in (
            "eks-managed-node-group",
            "self-managed-node-group",
            "fargate-profile",
            "karpenter",
            "hybrid-node-role",
            "capability",
        ):
            assert name in out, f"{name} missing from the submodule-scope menu"
        assert 'get_module("eks//modules/<submodule>"' in out

    def test_footer_absent_for_rootless_doc(self, server_state):
        """A module with no resolvable root bundle (iam) keeps the pre-
        existing all-scope fallback behavior -- no submodule-scope menu is
        appended, since nothing was hidden behind root-scoping."""
        out = get_module_impl("iam", server_state, sections=["inputs"])
        assert "Submodule interfaces available on demand" not in out

    def test_footer_absent_when_inputs_outputs_not_requested(self, server_state):
        """A sections request that never touches inputs/outputs (e.g. a
        heading substring match) gets no submodule-scope menu."""
        out = get_module_impl("eks", server_state, sections=["karpenter"])
        assert "Submodule interfaces available on demand" not in out

    def test_rootless_doc_inputs_view_unaffected(self, server_state):
        """cloudwatch has no resolvable root bundle -- its default
        sections=["inputs"] behavior is unchanged: submodule bundles are
        still walked (the pre-existing BUG-1 fix), not root-scoped away."""
        out = get_module_impl("cloudwatch", server_state, sections=["inputs"])
        assert "Requested sections not found" not in out
        assert "## Submodule 1: log-group" in out

    def test_safety_cap_truncates_instead_of_overflowing(self, server_state, monkeypatch):
        """Synthetic oversized case: with the byte cap lowered far below a
        single real table's size, the complete-table render truncates with
        an explicit pointer rather than emitting the whole (much larger)
        table."""
        monkeypatch.setattr(tfmod_mcp_server, "_COMPLETE_TABLE_BYTE_CAP", 2000)
        out = get_module_impl("eks", server_state, sections=["inputs"])
        assert "more rows omitted" in out
        assert f"{tfmod_mcp_server._COMPLETE_TABLE_BYTE_CAP}-byte safety cap" in out
        # Never trips into emitting the whole 104-row uncapped table.
        assert out.count("| `") < 200

    def test_safety_cap_is_a_noop_when_table_fits(self, server_state):
        """The default (real) cap never fires on the real catalog -- the
        pointer line must be absent when nothing was truncated."""
        out = get_module_impl("eks", server_state, sections=["inputs"])
        assert "more rows omitted" not in out


class TestD7ChangeA2GroupedH3Completeness:
    """
    D7 Change A2 (2026-07-21, release-blocker fix). Root cause: on modules
    whose curated root inputs/outputs are grouped under multiple
    `### <Category>` H3 subsections instead of sitting in one table directly
    under the inputs/outputs H2, the D7 Change A inline complete-table
    supersede could not locate a single replaceable table and silently
    no-opped -- serving the curated (possibly PARTIAL) subset under a
    "COMPLETE inputs/outputs" footer claim. With grep_module_docs removed (D7
    Change B), an agent confirming a variable name on one of these modules
    got a false "does not exist", with no fallback left. The fix appends the
    complete root table (from the same committed overlay, same byte cap)
    whenever the overlay has root data but the inline supersede did not
    actually fire for root -- detected explicitly via
    `_content_with_complete_input_tables_ex`/`_content_with_complete_output_
    tables_ex` reporting which scopes were superseded, not re-derived by
    guessing at heading shape a second time.

    Uses REAL committed docs/overlays (not fixtures) -- these are actual
    catalog gaps, not synthetic ones.
    """

    def test_grouped_h3_module_gains_previously_absent_root_input(self, server_state):
        """eventbridge groups its root inputs under 5 H3 subsections (Core
        Toggles, Bus/Rules/Targets, Scheduler & Pipes, ...);
        `append_rule_postfix` had NO row at all anywhere in the curated doc.
        It must now be present."""
        out = get_module_impl("eventbridge", server_state, sections=["inputs"])
        assert "`append_rule_postfix`" in out

    def test_grouped_h3_module_appends_a_labeled_complete_table(self, server_state):
        """The fallback is clearly labeled as its own section, not silently
        blended into the curated table."""
        out = get_module_impl("eventbridge", server_state, sections=["inputs"])
        assert "## Complete Root Inputs" in out

    def test_grouped_h3_module_output_side_also_completes(self, server_state):
        """datadog-forwarders groups its root outputs under 4 H3
        subsections -- the outputs view gets the mirrored appended-table
        treatment, under its own labeled heading."""
        out = get_module_impl("datadog-forwarders", server_state, sections=["outputs"])
        assert "## Complete Root Outputs" in out

    def test_already_superseded_module_gets_no_duplicate_table(self, server_state):
        """eks supersedes correctly inline (its root table sits directly
        under "### Main Input Variables" inside the "## Main Module: EKS
        Cluster" bundle) -- the fallback must not also append a second,
        duplicate complete table for the same (already-complete) scope."""
        out = get_module_impl("eks", server_state, sections=["inputs"])
        assert "## Complete Root Inputs" not in out

    def test_split_scheme_module_gets_no_duplicate_table(self, server_state):
        """rds (split-scheme doc: a single root table sits directly under
        its own top-level "## Main Input Variables" H2) also supersedes
        inline -- no duplicate appended table either."""
        out = get_module_impl("rds", server_state, sections=["inputs"])
        assert "## Complete Root Inputs" not in out

    def test_sso_empty_root_scope_does_not_crash_or_emit_empty_table(self, server_state):
        """sso's overlay has a "root" key present in both all_inputs and
        all_outputs, but with ZERO entries (every real field belongs to one
        of its two submodules) -- must not crash, and must not claim
        completeness by appending an empty table."""
        out = get_module_impl("sso", server_state, sections=["inputs", "outputs"])
        assert "## Complete Root Inputs" not in out
        assert "## Complete Root Outputs" not in out

    @pytest.mark.parametrize("module_name", ["sso", "cloudwatch", "fsx", "iam"])
    def test_empty_root_scope_footer_never_claims_completeness(self, server_state, module_name):
        """Nit (independent review): an empty-root-scope overlay (sso,
        cloudwatch, fsx, iam -- every real field belongs to a submodule, not
        root) must never emit a false "complete" footer claim alongside the
        BLOCKER 2 fallback that already keeps it from appending an empty
        table. The footer must keep the genuinely-still-a-subset wording and
        must still route the agent to sections=["inputs","outputs"] (a
        harmless no-op re-call, not a false completeness claim) or the
        submodule address / module source."""
        out = get_module_impl(module_name, server_state, sections=["inputs", "outputs"])
        disclaimer_line = next(line for line in out.splitlines() if line.startswith("Curated subset."))
        assert (
            "already ARE the COMPLETE" not in disclaimer_line
        ), f"{module_name}: footer must not claim a complete root interface it never served"
        assert "## Complete Root Inputs" not in out
        assert "## Complete Root Outputs" not in out

    def test_grouped_h3_append_fired_footer_states_completeness(self, server_state):
        """#5 (independent review): eventbridge's root inputs are grouped
        under H3 subsections, so the inline supersede cannot fire and the A2
        append fallback serves the complete table instead -- the footer must
        recognize THAT path too, not only the inline-supersede path."""
        out = get_module_impl("eventbridge", server_state, sections=["inputs"])
        disclaimer_line = next(line for line in out.splitlines() if line.startswith("Curated subset."))
        assert "already ARE the COMPLETE" in disclaimer_line
        assert "or to confirm a name exists, call" not in disclaimer_line, "Must not invite a redundant re-call"

    def test_appended_table_respects_byte_cap(self, server_state, monkeypatch):
        """Synthetic oversized case: with the byte cap lowered far below the
        real table's size, the APPENDED complete table truncates with an
        explicit pointer instead of emitting the whole (much larger) table --
        same guarantee `TestD7ChangeARootScopeDefault` already exercises for
        the inline-superseded case."""
        monkeypatch.setattr(tfmod_mcp_server, "_COMPLETE_TABLE_BYTE_CAP", 2000)
        out = get_module_impl("eventbridge", server_state, sections=["inputs"])
        assert "## Complete Root Inputs" in out
        assert "more rows omitted" in out
        assert f"{tfmod_mcp_server._COMPLETE_TABLE_BYTE_CAP}-byte safety cap" in out

    def test_full_catalog_sweep_root_interface_is_complete(self, server_state):
        """SWEEP VERIFICATION: render sections=["inputs","outputs"] (or
        whichever half applies) for every one of the 63 catalog modules;
        for each whose overlay has a non-empty root-scope input and/or
        output list, every one of those names must appear in the response,
        and the response must stay well clear of the byte cap -- the
        release-blocker regression this fix exists to close, checked across
        the whole catalog rather than the handful of modules measured by
        hand."""
        cap = tfmod_mcp_server._COMPLETE_TABLE_BYTE_CAP
        short: list[tuple[str, list[str]]] = []
        overflow: list[tuple[str, int]] = []
        checked = 0
        for doc in server_state.index.docs:
            content = get_module_documentation(doc.path, server_state)
            overlay = tfmod_mcp_server._load_any_overlay(tfmod_mcp_server._resolve_overlay_module_id(content))
            if not overlay:
                continue
            root_inputs = (overlay.get("all_inputs") or {}).get("root") or []
            root_outputs = (overlay.get("all_outputs") or {}).get("root") or []
            if not root_inputs and not root_outputs:
                continue
            checked += 1
            sections = [key for key, items in (("inputs", root_inputs), ("outputs", root_outputs)) if items]
            out = get_module_impl(doc.path, server_state, sections=sections)
            missing = [i["name"] for i in root_inputs if f"`{i['name']}`" not in out]
            missing += [o["name"] for o in root_outputs if f"`{o['name']}`" not in out]
            if missing:
                short.append((doc.path, missing))
            byte_len = len(out.encode("utf-8"))
            if byte_len > cap * 4:
                overflow.append((doc.path, byte_len))
        assert checked >= 55, "sanity check: the sweep must have actually walked the real catalog"
        assert not short, f"modules still missing root interface rows: {short}"
        assert not overflow, f"modules whose response overflowed a generous byte multiple of the cap: {overflow}"


class TestNEW1ScopeForH2TitleDeterminism:
    """NEW-1 (2026-07-22 pre-release re-review, BLOCKER): unit-level coverage
    for `_scope_for_h2_title`'s substring-match fallback. Root cause: the old
    implementation iterated `candidate_scopes` (a frozenset) in whatever
    order it happened to hash-iterate in -- PYTHONHASHSEED-dependent -- so a
    title containing more than one scope key as a substring resolved
    nondeterministically. The catalog's one real instance: iam.md's
    "## Submodule 8: iam-role-for-service-accounts (IRSA)" contains both
    "iam-role" and "iam-role-for-service-accounts" as substrings.

    Fix: try candidates longest-key-first (ties broken alphabetically), with
    a name-boundary guard (the character right after a match must not
    continue a hyphenated identifier -- reject "-"/alnum, accept
    end-of-string/whitespace/punctuation).

    A real frozenset's iteration order is fixed for one process's lifetime
    (it derives from PYTHONHASHSEED, set once at interpreter start), so the
    only way to exercise more than one order within a single test process is
    to control it explicitly -- these tests pass plain, differently-ordered
    tuples as `candidate_scopes` (the function only ever iterates its input,
    never relies on it being a "real" frozenset), directly simulating what a
    hash-randomized frozenset would produce across different seeded
    processes. `TestNEW1SeedIndependentIamRendering` below additionally
    proves this end-to-end under real different PYTHONHASHSEED values.
    """

    IAM_SCOPES = (
        "iam-account",
        "iam-group",
        "iam-oidc-provider",
        "iam-policy",
        "iam-read-only-policy",
        "iam-role",
        "iam-role-for-service-accounts",
        "iam-user",
        "root",
    )

    IRSA_TITLE = "Submodule 8: iam-role-for-service-accounts (IRSA)"

    @pytest.mark.parametrize(
        "ordering",
        [
            IAM_SCOPES,
            tuple(reversed(IAM_SCOPES)),
            ("iam-role", "iam-role-for-service-accounts", "root", "iam-user", "iam-account"),
            ("root", "iam-role-for-service-accounts", "iam-role"),
            ("iam-role", "root", "iam-role-for-service-accounts"),
        ],
        ids=["forward", "reversed", "iam-role-first", "irsa-before-role", "role-before-irsa"],
    )
    def test_irsa_heading_resolves_correctly_regardless_of_iteration_order(self, ordering):
        assert (
            tfmod_mcp_server._scope_for_h2_title(self.IRSA_TITLE, ordering) == "iam-role-for-service-accounts"
        ), f"ordering {ordering!r} must still resolve to the more specific scope"

    @pytest.mark.parametrize("ordering", [IAM_SCOPES, tuple(reversed(IAM_SCOPES))])
    def test_iam_role_heading_resolves_exactly_regardless_of_order(self, ordering):
        assert tfmod_mcp_server._scope_for_h2_title("Submodule 4: iam-role", ordering) == "iam-role"

    def test_boundary_guard_does_not_break_decorated_heading_with_space_suffix(self):
        """The boundary guard must not regress the pre-existing decorated-
        heading case ("Submodule 2: flow-log (Recommended)") -- its next
        character after the match is a space, not "-"/alnum, so it must
        still match."""
        assert (
            tfmod_mcp_server._scope_for_h2_title(
                "Submodule 2: flow-log (Recommended)", ("flow-log", "flow-log-other", "root")
            )
            == "flow-log"
        )

    def test_restricted_scope_does_not_match_inside_longer_name(self):
        """Simulates the get_module("iam//modules/iam-role", ...) restriction:
        only_scopes narrows candidate_scopes down to {"iam-role"} BEFORE this
        function ever runs. With the boundary guard, "iam-role" must NOT
        match inside "iam-role-for-service-accounts" even though it IS a
        substring -- this is manifestation 2 of NEW-1 (the deterministic
        double-serve)."""
        assert tfmod_mcp_server._scope_for_h2_title(self.IRSA_TITLE, frozenset({"iam-role"})) is None

    def test_unambiguous_title_still_resolves(self):
        """Sanity: an unambiguous submodule title is unaffected by the fix."""
        assert (
            tfmod_mcp_server._scope_for_h2_title("Submodule 1: iam-account", frozenset(self.IAM_SCOPES))
            == "iam-account"
        )


class TestNEW1IamRealCatalogScopeResolution:
    """NEW-1 integration coverage against the real, committed iam overlay and
    doc (not a fixture) -- the exact reproduction the re-review measured."""

    def test_iam_inputs_view_surfaces_irsa_only_fields(self, server_state):
        """Pre-fix, this was nondeterministic: on the bad variant IRSA's real
        inputs (attach_ebs_csi_policy and the other attach_*_policy toggles)
        appeared nowhere in the response. Must now always be present."""
        out = get_module_impl("iam", server_state, sections=["inputs"])
        assert "`attach_ebs_csi_policy`" in out
        assert "`attach_velero_policy`" in out

    def test_iam_all_view_surfaces_irsa_only_fields(self, server_state):
        out = get_module_impl("iam", server_state, sections=["all"])
        assert "`attach_ebs_csi_policy`" in out

    def test_iam_role_only_field_never_appears_under_irsa_heading(self, server_state):
        """iam-role-only fields (never part of IRSA's own interface) must not
        leak under the IRSA heading via a wrong-scope supersede."""
        out = get_module_impl("iam", server_state, sections=["inputs"])
        irsa_start = out.index("## Submodule 8: iam-role-for-service-accounts")
        irsa_block = out[irsa_start:]
        assert "`create_instance_profile`" not in irsa_block
        assert "`enable_saml`" not in irsa_block

    def test_submodule_address_iam_role_table_appears_exactly_once(self, server_state):
        """get_module("iam//modules/iam-role", sections=["inputs"]) used to
        deterministically serve iam-role's complete table TWICE -- once
        correctly under "## Submodule 4: iam-role", once mislabeled under
        "## Submodule 8: iam-role-for-service-accounts (IRSA)". A field
        unique to iam-role's own interface must now appear exactly once."""
        out = get_module_impl("iam//modules/iam-role", server_state, sections=["inputs"])
        assert out.count("`create_instance_profile`") == 1
        assert out.count("`source_trust_policy_documents`") == 1


_IAM_SEED_RENDER_SCRIPT = """
import sys
sys.path.insert(0, "src")
import logging
from pathlib import Path
from tfmod_search_lib import load_index
from tfmod_mcp_server import ServerState, SearchWeights, get_module_impl

logger = logging.getLogger("iam_seed_test")
logger.addHandler(logging.NullHandler())
index_path = Path("model/tfmod_e5_small_index.pkl")
index = load_index(str(index_path), logger)
weights = SearchWeights(w_kw=2.0, w_exact=3.0, w_bm25=1.0, w_sem=1.0)
state = ServerState(index=index, weights=weights, index_path=index_path, logger=logger)
sections = sys.argv[1].split(",")
sys.stdout.write(get_module_impl("iam", state, sections=sections))
"""


class TestNEW1SeedIndependentIamRendering:
    """NEW-1 end-to-end regression (2026-07-22 pre-release re-review,
    BLOCKER): render get_module("iam", sections=[...]) in fresh subprocesses
    under different real PYTHONHASHSEED values and assert byte-identical
    output -- the direct reproduction of the reported nondeterminism
    (measured pre-fix: PYTHONHASHSEED in {0, 1, 42} rendered one variant,
    {2, 3} another). A frozenset's iteration order is fixed for one
    process's lifetime, so this is the only way to genuinely exercise more
    than one order for the real catalog's iam overlay from outside
    `_scope_for_h2_title` itself."""

    def _render_under_seed(self, seed: str, sections: str) -> str:
        env = dict(os.environ, PYTHONHASHSEED=seed)
        result = subprocess.run(
            [sys.executable, "-c", _IAM_SEED_RENDER_SCRIPT, sections],
            cwd=str(PROJECT_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"subprocess failed (seed={seed}): {result.stderr}"
        return result.stdout

    @pytest.mark.parametrize("sections", ["inputs", "all"])
    def test_iam_render_is_byte_identical_across_hash_seeds(self, sections):
        # One seed from each pre-fix "variant group" the re-review measured
        # (0/1/42 vs 2/3), plus a third data point.
        seeds = ["0", "2", "42"]
        rendered = {seed: self._render_under_seed(seed, sections) for seed in seeds}
        baseline_seed = seeds[0]
        baseline = rendered[baseline_seed]
        for seed in seeds[1:]:
            assert rendered[seed] == baseline, (
                f"get_module('iam', sections=['{sections}']) differs between "
                f"PYTHONHASHSEED={baseline_seed} and PYTHONHASHSEED={seed}"
            )
        assert "attach_ebs_csi_policy" in baseline, "IRSA-only input must be present under every hash seed"


class TestNEW2FullDocEscapeHatchGetsA2Completeness:
    """NEW-2 (2026-07-22 pre-release re-review): the D7 Change A2 grouped-H3
    completeness fallback (_append_missing_root_complete_tables) used to run
    only on the sections=["inputs"|"outputs"] path -- the all/full escape
    hatch relied on the inline supersede alone, which no-ops on grouped-H3
    docs (eventbridge groups its root inputs under 5 H3 subsections), so
    get_module("eventbridge", sections=["all"]) lacked append_rule_postfix
    even though the CHANGELOG claimed all/full completeness. The fallback
    now fires on this path too (via the shared `_full_document_view`)."""

    def test_eventbridge_all_gains_previously_missing_root_input(self, server_state):
        out = get_module_impl("eventbridge", server_state, sections=["all"])
        assert "`append_rule_postfix`" in out

    def test_eventbridge_all_appends_labeled_complete_table(self, server_state):
        out = get_module_impl("eventbridge", server_state, sections=["all"])
        assert "## Complete Root Inputs" in out

    def test_already_superseded_module_full_doc_gets_no_duplicate_table(self, server_state):
        """eks supersedes correctly inline on the full-doc view too -- the
        A2 fallback must not append a second, duplicate complete table."""
        out = get_module_impl("eks", server_state, sections=["all"])
        assert "## Complete Root Inputs" not in out

    def test_rootless_module_full_doc_does_not_crash_or_claim_completeness(self, server_state):
        """iam's overlay root scope is empty -- the fallback must be a no-op
        on the full-doc view exactly as it is on the sections view."""
        out = get_module_impl("iam", server_state, sections=["all"])
        assert "## Complete Root Inputs" not in out
        assert "## Complete Root Outputs" not in out


class TestNEW3AppendedTableCarriesAnyHint:
    """NEW-3 (2026-07-22 pre-release re-review, nit): the D7 Change A2
    appended "## Complete Root Inputs" table used to show a bare `any` Type
    cell for any-typed rows (_inline_any_overlay_input_cells runs BEFORE the
    A2 append and is heading-anchored on "### Main Input Variables", so it
    never sees the appended table's own "## Complete Root Inputs" heading)
    even though the same var's overlay entry carries a field-name hint.
    Verified on eventbridge's connections/targets/pipes -- real catalog data."""

    @pytest.mark.parametrize("var_name", ["connections", "targets", "pipes"])
    def test_eventbridge_appended_table_row_shows_field_hint_not_bare_any(self, server_state, var_name):
        out = get_module_impl("eventbridge", server_state, sections=["all"])
        start = out.index("## Complete Root Inputs")
        appended_block = out[start:]
        row = next(line for line in appended_block.splitlines() if line.startswith(f"| `{var_name}`"))
        cells = tfmod_mcp_server._split_table_row(row)
        assert cells[1] != "`any`", f"{var_name}'s appended-table Type cell must not stay bare `any`"
        assert cells[1].startswith("any -- fields:"), f"unexpected appended-table Type cell: {cells[1]!r}"

    def test_eventbridge_sections_inputs_view_also_gets_hinted_appended_table(self, server_state):
        """Same guarantee on the sections=["inputs"] view (not only all/full)."""
        out = get_module_impl("eventbridge", server_state, sections=["inputs"])
        start = out.index("## Complete Root Inputs")
        appended_block = out[start:]
        row = next(line for line in appended_block.splitlines() if line.startswith("| `connections`"))
        cells = tfmod_mcp_server._split_table_row(row)
        assert cells[1].startswith("any -- fields:")


class TestNEW5AppendedTableRendersAboveAppendix:
    """NEW-5 (2026-07-22 pre-release re-review, nit): the D7 Change A2
    appended complete table used to render BELOW the any-overlay appendix
    (insert order was appendix-then-A2) -- the authoritative complete table
    should read above the example/field-name appendix, not after it."""

    def test_eventbridge_complete_table_precedes_any_overlay_appendix(self, server_state):
        out = get_module_impl("eventbridge", server_state, sections=["inputs"])
        table_idx = out.index("## Complete Root Inputs")
        appendix_idx = out.index("any-typed input overlay")
        assert table_idx < appendix_idx, "the complete table must render above the any-overlay appendix"

    def test_eventbridge_full_doc_view_same_ordering(self, server_state):
        out = get_module_impl("eventbridge", server_state, sections=["all"])
        table_idx = out.index("## Complete Root Inputs")
        appendix_idx = out.index("any-typed input overlay")
        assert table_idx < appendix_idx


class TestNEW4CompleteBranchFooterLooseBound:
    """NEW-4 (accepted under clarity-over-bytes, 2026-07-22 pre-release
    re-review): the complete-branch footer disclaimer (545 chars measured)
    is deliberately NOT shrunk -- but it must stay under a much looser sane
    bound so it cannot grow unbounded over time."""

    def test_complete_branch_disclaimer_stays_under_loose_bound(self, server_state):
        out = get_module_impl("eks", server_state, sections=["inputs"])
        disclaimer_line = next(line for line in out.splitlines() if line.startswith("Curated subset."))
        assert "already ARE the COMPLETE" in disclaimer_line, "sanity: must be the complete-branch wording"
        assert (
            len(disclaimer_line) < 700
        ), f"complete-branch disclaimer line ({len(disclaimer_line)} chars) must stay under a loose sane bound"


class TestCapCompleteTableRowsUnit:
    """Unit-level: _cap_complete_table_rows, the shared truncation helper
    behind both _build_all_inputs_table and _build_all_outputs_table."""

    def test_all_rows_kept_when_under_cap(self):
        header = "| A | B |\n|---|---|\n"
        rows = [f"| `v{i}` | x |\n" for i in range(5)]
        out = tfmod_mcp_server._cap_complete_table_rows(header, rows)
        assert out == header + "".join(rows)
        assert "more rows omitted" not in out

    def test_truncates_with_pointer_when_over_cap(self):
        header = "| A | B |\n|---|---|\n"
        rows = [f"| `v{i}` | {'x' * 50} |\n" for i in range(50)]
        out = tfmod_mcp_server._cap_complete_table_rows(header, rows, cap=500)
        assert "more rows omitted" in out
        assert len(out.encode("utf-8")) < 500 + 400  # header/rows within cap + one pointer line
        # Not every row survived.
        assert out.count("| `v") < 50

    def test_pointer_reports_correct_remaining_count(self):
        header = "| A | B |\n|---|---|\n"
        rows = [f"| `v{i}` | {'x' * 20} |\n" for i in range(10)]
        out = tfmod_mcp_server._cap_complete_table_rows(header, rows, cap=100)
        kept = out.count("| `v")
        assert f"+{10 - kept} more rows omitted" in out


class TestSubmoduleAddress:
    """A3: get_module accepts a submodule address and returns a scoped head."""

    @pytest.mark.parametrize(
        ("identifier", "expected"),
        [
            ("iam//modules/iam-role", ("iam", "iam-role")),
            ("terraform-aws-modules/iam/aws//modules/iam-role", ("iam", "iam-role")),
            ("iam//iam-role", ("iam", "iam-role")),
            ("route53//modules/zones", ("route53", "zones")),
            ("iam // modules/iam-role", ("iam", "iam-role")),
            ("vpc", None),
            ("modules/terraform-aws-modules/vpc.md", None),
            ("iam//", None),
            ("//modules/iam-role", None),
            ("iam//modules/", None),
            ("iam//modules", None),
        ],
    )
    def test_parse_submodule_address(self, identifier, expected):
        assert _parse_submodule_address(identifier) == expected

    def test_submodule_address_without_segment_falls_back(self, server_state):
        """'iam//modules/' has no submodule segment → normal resolution, not a bogus scope."""
        # Not a submodule address, so it falls through to normal path/name resolution,
        # which rejects it (no such module/file) instead of scoping to a bogus section.
        with pytest.raises(ValueError):
            get_module_impl("iam//modules/", server_state)

    def test_submodule_address_honors_full_doc_escape_hatch(self, server_state, monkeypatch, tmp_path):
        """A submodule address + sections=['all'] returns the complete parent doc verbatim
        (isolated from committed overlays; the overlay-appendix interaction on the
        submodule-address path is covered by the TestAnyOverlay submodule tests)."""
        monkeypatch.setattr(tfmod_mcp_server, "_ANY_OVERLAY_DIR", tmp_path)
        for key in ("all", "full", "everything"):
            out = get_module_impl("iam//modules/iam-role", server_state, sections=[key])
            assert out == get_module_documentation("iam", server_state), f"['{key}'] should return the full parent doc"
            assert "Requested sections not found" not in out

    def test_submodule_address_returns_scoped_head(self, server_state):
        """get_module('iam//modules/iam-role') scopes to that submodule's section."""
        scoped = get_module_impl("iam//modules/iam-role", server_state)
        assert "## Submodule 4: iam-role" in scoped, "The addressed submodule's section is expanded"
        assert "Version pin" in scoped, "Scoped head keeps the exact-version pin hint"
        assert "## Module Information" in scoped, "Parent core context is retained for orientation"
        # It is scoped, not the whole parent: a different submodule's deep-dive is absent.
        assert "## Submodule 7: iam-oidc-provider" not in scoped, "Other submodules must not be expanded"
        full = get_module_impl("iam", server_state, sections=["all"])
        assert len(scoped) < len(full), "Scoped head is smaller than the full parent doc"

    def test_submodule_full_id_form_matches_short_form(self, server_state):
        """The ns/name/provider//modules/sub form resolves identically to the short form."""
        short = get_module_impl("iam//modules/iam-role", server_state)
        full_id = get_module_impl("terraform-aws-modules/iam/aws//modules/iam-role", server_state)
        assert short == full_id

    def test_unknown_submodule_degrades_gracefully(self, server_state):
        """An unknown submodule returns core context + a menu of the real submodules, not an error."""
        scoped = get_module_impl("iam//modules/does-not-exist", server_state)
        assert "## Module Information" in scoped, "Parent core context still returned"
        assert "Requested sections not found: does-not-exist" in scoped, "Miss is reported"
        assert "Submodule 4: iam-role" in scoped, "Footer lists the real submodule titles for retry"


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
        """Test that each full-detail module item has correct structure."""
        result = modules_list_impl(server_state, detail="full")

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

    def test_modules_list_output_schema_has_no_path_required_union(self):
        """Regression (0.23.1): the modules_list output-item schema must NOT be a
        union and must NOT require `path`.

        A prior heterogeneous ``list[Compact] | list[Full]`` output type produced
        an item schema a strict MCP output-schema validator (the plugin proxy /
        host client) mis-resolved into requiring `path`, so the COMPACT default
        (which has no path) failed over HTTP with "'path' is a required property".
        The single optional-field model must keep `path` optional and carry no
        anyOf for any validator to mis-resolve."""
        schema = ModulesListOutput.model_json_schema()
        modules = schema["properties"]["modules"]
        assert "anyOf" not in modules, "modules field must not be a union (anyOf mis-resolves for strict validators)"
        # resolve the item schema (either inline or via $ref/$defs)
        items = modules["items"]
        if "$ref" in items:
            ref = items["$ref"].split("/")[-1]
            items = schema["$defs"][ref]
        assert "anyOf" not in items, "modules item schema must not be a union"
        required = items.get("required", [])
        assert "path" not in required, f"path must be OPTIONAL on modules items, got required={required}"
        assert set(required) == {"module_name", "module_id", "latest_version"}

    def test_modules_list_compact_is_lean_full_is_complete(self, server_state):
        """The compact default serializes WITHOUT path/description/keywords (byte-lean,
        no null noise); detail=full serializes WITH them. Guards the 0.23.1 unified
        model + drop-none serializer against re-bloating the compact response."""
        compact = modules_list_impl(server_state).model_dump()
        assert compact["modules"], "compact list is empty"
        c0 = compact["modules"][0]
        assert set(c0) == {
            "module_name",
            "purpose",
            "module_id",
            "latest_version",
        }, f"compact item leaked keys: {set(c0)}"
        assert "path" not in c0

        full = modules_list_impl(server_state, detail="full").model_dump()
        f0 = full["modules"][0]
        assert {"module_name", "path", "description", "keywords", "module_id", "latest_version"} <= set(f0)
        assert "purpose" not in f0, "full item should not carry the compact-only purpose key"

    def test_modules_list_contains_expected_modules(self, server_state):
        """Test that modules_list includes known modules."""
        result = modules_list_impl(server_state)

        module_names = [m.module_name for m in result.modules]

        # Check for some known modules (depends on test data)
        expected_modules = ["vpc", "s3-bucket", "eks", "lambda", "iam", "security-group"]
        for expected in expected_modules:
            assert expected in module_names, f"Should include {expected} module"

    def test_modules_list_descriptions_truncated(self, server_state):
        """Test that full-detail descriptions are properly truncated."""
        result = modules_list_impl(server_state, detail="full")

        for module in result.modules:
            # Descriptions should be truncated to ~200 chars
            assert len(module.description) <= 203, f"Description for {module.module_name} should be truncated"

    def test_modules_list_includes_module_id(self, server_state):
        """Test that every catalog entry carries a non-empty module_id registry coordinate."""
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


class TestResponseByteMetering:
    """D2: opt-in per-tool-call response-size logging, gated by
    TFMODSEARCH_LOG_RESPONSE_BYTES. Unset/falsy must be a true no-op
    (byte-identical to pre-D2 behavior); truthy must emit exactly one
    'response_bytes tool=<name> bytes=<N>' INFO line per tool call, with N
    the true UTF-8 byte length of the serialized response. Exercises the
    actual @app.tool-decorated wrapper functions (not the _impl helpers) so
    the hook at each tool's real return point is covered.
    """

    def test_flag_unset_emits_no_response_bytes_lines(self, server_state, caplog, monkeypatch):
        """Default (env var unset) must be a true no-op: no response_bytes
        line from any of the three tools, behavior otherwise unchanged."""
        monkeypatch.delenv("TFMODSEARCH_LOG_RESPONSE_BYTES", raising=False)
        with caplog.at_level(logging.INFO):
            tfmod_mcp_server.modules_list()
            tfmod_mcp_server.search_modules("vpc")
            tfmod_mcp_server.get_module("vpc")
        assert not any(
            "response_bytes" in record.message for record in caplog.records
        ), "No response_bytes line must be logged while the flag is unset"

    def test_flag_falsy_emits_no_response_bytes_lines(self, server_state, caplog, monkeypatch):
        """Explicit falsy values (not just unset) must also disable logging."""
        for falsy in ("0", "false", "False", "no", "off", ""):
            monkeypatch.setenv("TFMODSEARCH_LOG_RESPONSE_BYTES", falsy)
            with caplog.at_level(logging.INFO):
                tfmod_mcp_server.modules_list()
            assert not any(
                "response_bytes" in record.message for record in caplog.records
            ), f"No response_bytes line must be logged for falsy value {falsy!r}"

    def test_modules_list_logs_true_byte_length(self, server_state, caplog, monkeypatch):
        monkeypatch.setenv("TFMODSEARCH_LOG_RESPONSE_BYTES", "1")
        caplog.clear()
        with caplog.at_level(logging.INFO):
            result = tfmod_mcp_server.modules_list()
        lines = [r.message for r in caplog.records if r.message.startswith("response_bytes tool=modules_list")]
        assert len(lines) == 1, "Exactly one response_bytes line must be logged per tool call"
        expected_bytes = len(result.model_dump_json().encode("utf-8"))
        assert lines[0] == f"response_bytes tool=modules_list bytes={expected_bytes}"

    def test_search_modules_logs_true_byte_length(self, server_state, caplog, monkeypatch):
        monkeypatch.setenv("TFMODSEARCH_LOG_RESPONSE_BYTES", "1")
        caplog.clear()
        with caplog.at_level(logging.INFO):
            result = tfmod_mcp_server.search_modules("vpc")
        lines = [r.message for r in caplog.records if r.message.startswith("response_bytes tool=search_modules")]
        assert len(lines) == 1, "Exactly one response_bytes line must be logged per tool call"
        expected_bytes = len(result.model_dump_json().encode("utf-8"))
        assert lines[0] == f"response_bytes tool=search_modules bytes={expected_bytes}"

    def test_get_module_logs_true_byte_length(self, server_state, caplog, monkeypatch):
        monkeypatch.setenv("TFMODSEARCH_LOG_RESPONSE_BYTES", "1")
        caplog.clear()
        with caplog.at_level(logging.INFO):
            result = tfmod_mcp_server.get_module("vpc")
        lines = [r.message for r in caplog.records if r.message.startswith("response_bytes tool=get_module")]
        assert len(lines) == 1, "Exactly one response_bytes line must be logged per tool call"
        assert isinstance(result, str), "get_module returns a plain string -- measured directly, no re-serialization"
        expected_bytes = len(result.encode("utf-8"))
        assert lines[0] == f"response_bytes tool=get_module bytes={expected_bytes}"

    def test_flag_on_does_not_change_response_content(self, server_state, monkeypatch):
        """D2 must never alter what a tool returns -- only whether a log line
        is emitted alongside it."""
        monkeypatch.delenv("TFMODSEARCH_LOG_RESPONSE_BYTES", raising=False)
        off_result = tfmod_mcp_server.get_module("vpc")
        monkeypatch.setenv("TFMODSEARCH_LOG_RESPONSE_BYTES", "1")
        on_result = tfmod_mcp_server.get_module("vpc")
        assert off_result == on_result, "Response content must be identical regardless of the metering flag"
