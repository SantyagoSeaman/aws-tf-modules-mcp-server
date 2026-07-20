"""
Integration tests for the MCP server (tfmod_mcp_server.py).

Tests both the search_modules tool and get_module resource.
"""

import logging
import re
import socket
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
        """sections=['all'] bypasses filtering and returns the unmodified full document."""
        for key in ("all", "full", "everything"):
            full = get_module_impl("security-group", server_state, sections=[key])
            raw = get_module_documentation("security-group", server_state)
            assert full == raw, f"sections=['{key}'] should return the complete document verbatim"

    def test_orientation_head_includes_version_pin_hint(self, server_state):
        """The default head surfaces an actionable exact-version pin (BUG-5)."""
        head = get_module_impl("vpc", server_state)
        assert "Version pin" in head, "Orientation head should surface an exact-pin hint"
        assert 'version = "' in head, "Pin hint should show an exact version pin"

    def test_response_carries_escalation_pointer(self, server_state):
        """Head and filtered responses point to grep_module_docs for complete/exact data."""
        for resp in (
            get_module_impl("s3-bucket", server_state),
            get_module_impl("s3-bucket", server_state, sections=["inputs"]),
        ):
            assert "grep_module_docs" in resp, "Response must point to the live-registry tier"
            assert "COMPLETE inputs/outputs" in resp, "Response must flag that it is a curated subset"
            assert "module source" in resp, "Response must name source as the creation-condition tier"

    def test_footer_grep_hint_mentions_shapes(self):
        """Footer broadens the grep pointer from names to names AND type/shape verification."""
        doc = (
            "---\nm: x\n---\n\n## Module Information\n\n- **Module ID**: x/y/aws\n\n"
            "## Description\n\nd\n\n## Notes for AI Agents\n\nn\n"
        )
        out = filter_module_sections(doc, [])
        assert "TYPE/SHAPE" in out, "Footer must carry the explicit type/shape verification phrase"

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
        disclaimer_line = next(line for line in out.splitlines() if "grep_module_docs" in line)
        assert len(disclaimer_line) < 400, (
            f"disclaimer line ({len(disclaimer_line)} chars) must be far shorter than the old " f"~764-char paragraph"
        )
        # The now-removed verbose repetition must be gone.
        assert "Do not assert an exact default" not in out
        assert "confirm it in the full doc first" not in out

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
        assert "Field names observed in module source" in out
        assert "not a schema" in out

    def test_honesty_labels_present(self, server_state, any_overlay_dir):
        """The mandatory example-provenance labels from the spec are present."""
        out = get_module_impl("s3-bucket", server_state, sections=["inputs"])
        assert "Apply-verified example" in out
        assert "one accepted form" in out
        assert "grep_module_docs" in out

    def test_appendix_adds_no_new_h2_heading(self, server_state, any_overlay_dir):
        """The appendix is fenced content spliced into the existing response --
        it must not introduce a new top-level (H2) heading."""
        content = get_module_documentation("s3-bucket", server_state)
        baseline = filter_module_sections(content, ["inputs"])
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

    # ---- --network none / no-fetch ----

    def test_no_network_access_serving_overlay(self, server_state, any_overlay_dir, monkeypatch):
        """Committed overlay = static data -- get_module makes zero network
        calls while serving it. get_module stays 100% network-decoupled; live
        Registry access stays confined to grep_module_docs."""

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

    # ---- no regression: a module with no overlay is byte-identical ----

    def test_module_without_overlay_is_byte_identical(self, server_state, any_overlay_dir):
        """vpc has no matching overlay file in the fixture dir -- its rendered
        output (head and sections=["inputs"]) is unaffected."""
        content = get_module_documentation("vpc", server_state)

        head_baseline = orientation_head(content)
        head_with_dir = get_module_impl("vpc", server_state)
        assert head_with_dir == head_baseline

        inputs_baseline = filter_module_sections(content, ["inputs"])
        inputs_with_dir = get_module_impl("vpc", server_state, sections=["inputs"])
        assert inputs_with_dir == inputs_baseline

    def test_no_overlay_directory_present_is_unaffected(self, server_state):
        """Without the fixture monkeypatch, _ANY_OVERLAY_DIR is the real
        (.gitkeep-only) model/any_overlay/ -- every module renders unchanged."""
        for mod in ("s3-bucket", "vpc", "iam"):
            content = get_module_documentation(mod, server_state)
            assert get_module_impl(mod, server_state) == orientation_head(content)
            assert get_module_impl(mod, server_state, sections=["inputs"]) == filter_module_sections(
                content, ["inputs"]
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
        assert rendered.count("Field names observed in module source") == 1
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
        16041 chars for this exact synthetic shape."""
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
        assert len(rendered) < 16041 * 0.6

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

    def test_submodule_address_honors_full_doc_escape_hatch(self, server_state):
        """A submodule address + sections=['all'] returns the complete parent doc verbatim."""
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
