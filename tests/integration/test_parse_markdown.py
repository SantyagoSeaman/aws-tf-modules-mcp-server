"""
Integration tests for parse_markdown_file function.
Tests parsing of all Terraform module documentation files.
"""

import logging

import pytest

from tests.integration import PROJECT_ROOT
from tfmod_search_lib import extract_description, parse_markdown_file


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
def terraform_modules_dir():
    """Provide path to terraform-aws-modules documentation directory."""
    return PROJECT_ROOT / "modules" / "terraform-aws-modules"


def test_parse_all_terraform_modules(terraform_modules_dir, test_logger):
    """
    Test that all .md files in terraform-aws-modules directory
    can be parsed and have module_name and keywords.
    """
    # Find all markdown files
    md_files = list(terraform_modules_dir.glob("*.md"))

    # Verify we found some files
    assert len(md_files) > 0, f"No markdown files found in {terraform_modules_dir}"

    print(f"\n\nTesting {len(md_files)} markdown files:")

    parsed_successfully = []
    failed_to_parse = []
    missing_module_name = []
    missing_keywords = []

    for md_file in md_files:
        print(f"\n  Testing: {md_file.name}")

        # Parse the file
        record = parse_markdown_file(md_file, test_logger)

        if record is None:
            failed_to_parse.append(md_file.name)
            print("    ✗ Failed to parse")
            continue

        # Check module_name
        if not record.module_name:
            missing_module_name.append(md_file.name)
            print("    ⚠ Missing module_name")
        else:
            print(f"    ✓ Module Name: {record.module_name}")

        # Check keywords
        if not record.keywords or len(record.keywords) == 0:
            missing_keywords.append(md_file.name)
            print("    ⚠ Missing keywords")
        else:
            print(f"    ✓ Keywords: {len(record.keywords)} found")
            print(f"      First 5: {', '.join(record.keywords[:5])}")

        if record.module_name and record.keywords:
            parsed_successfully.append(md_file.name)

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files: {len(md_files)}")
    print(f"Successfully parsed with module_name and keywords: {len(parsed_successfully)}")
    print(f"Failed to parse: {len(failed_to_parse)}")
    print(f"Missing module_name: {len(missing_module_name)}")
    print(f"Missing keywords: {len(missing_keywords)}")
    print("=" * 80)

    # Report failures
    if failed_to_parse:
        print("\n✗ Files that failed to parse:")
        for f in failed_to_parse:
            print(f"  - {f}")

    if missing_module_name:
        print("\n⚠ Files missing module_name:")
        for f in missing_module_name:
            print(f"  - {f}")

    if missing_keywords:
        print("\n⚠ Files missing keywords:")
        for f in missing_keywords:
            print(f"  - {f}")

    # Assertions
    assert len(failed_to_parse) == 0, f"Failed to parse {len(failed_to_parse)} files: {', '.join(failed_to_parse)}"

    assert (
        len(missing_module_name) == 0
    ), f"{len(missing_module_name)} files missing module_name: {', '.join(missing_module_name)}"

    assert len(missing_keywords) == 0, f"{len(missing_keywords)} files missing keywords: {', '.join(missing_keywords)}"

    # All files should be successfully parsed
    assert len(parsed_successfully) == len(md_files), f"Expected all {len(md_files)} files to be parsed successfully"


def test_parse_specific_module_structure(terraform_modules_dir, test_logger):
    """
    Test parsing of a specific module file to verify structure details.
    """
    s3_file = terraform_modules_dir / "s3-bucket.md"

    # Skip test if file doesn't exist
    if not s3_file.exists():
        pytest.skip(f"Test file {s3_file} not found")

    record = parse_markdown_file(s3_file, test_logger)

    # Verify record was created
    assert record is not None, "Failed to parse s3-bucket.md"

    # Verify module name
    assert record.module_name, "Module name is empty"
    assert "s3" in record.module_name.lower(), f"Expected 's3' in module name, got: {record.module_name}"

    # Verify keywords
    assert record.keywords, "Keywords list is empty"
    assert len(record.keywords) > 0, "No keywords found"

    # Check for expected keywords based on the file content
    keywords_set = set(record.keywords)
    expected_keywords = ["s3", "bucket", "encryption", "kms"]

    found_keywords = [kw for kw in expected_keywords if kw in keywords_set]

    print(f"\n\nModule: {record.module_name}")
    print(f"Total keywords: {len(record.keywords)}")
    print(f"Found expected keywords: {found_keywords}")
    print(f"All keywords: {', '.join(sorted(record.keywords)[:20])}...")

    # At least some expected keywords should be present
    assert len(found_keywords) > 0, f"Expected at least one of {expected_keywords} in keywords"

    # Verify text content exists
    assert record.text, "Document text is empty"
    assert len(record.text) > 100, "Document text is too short"


def test_parse_module_name_normalization(terraform_modules_dir, test_logger):
    """
    Test that module names are properly normalized.
    """
    md_files = list(terraform_modules_dir.glob("*.md"))

    assert len(md_files) > 0, "No markdown files found for testing"

    for md_file in md_files:
        record = parse_markdown_file(md_file, test_logger)

        if record and record.module_name:
            # Module names should be lowercase
            assert record.module_name == record.module_name.lower(), f"Module name not lowercase: {record.module_name}"

            # Module names should not have spaces
            assert " " not in record.module_name, f"Module name contains spaces: {record.module_name}"

            # Module names should use hyphens, not underscores
            # (based on normalize_modname function)
            if "_" in record.module_name:
                print(f"⚠ Warning: Module name contains underscore: {record.module_name}")


def test_parse_keywords_normalization(terraform_modules_dir, test_logger):
    """
    Test that keywords are properly normalized (lowercase, unique, sorted).
    """
    md_files = list(terraform_modules_dir.glob("*.md"))

    assert len(md_files) > 0, "No markdown files found for testing"

    for md_file in md_files:
        record = parse_markdown_file(md_file, test_logger)

        if record and record.keywords:
            # All keywords should be lowercase
            for kw in record.keywords:
                assert kw == kw.lower(), f"Keyword not lowercase in {md_file.name}: {kw}"

            # Keywords should be unique (no duplicates)
            assert len(record.keywords) == len(set(record.keywords)), f"Duplicate keywords found in {md_file.name}"

            # Keywords should be sorted
            assert record.keywords == sorted(record.keywords), f"Keywords not sorted in {md_file.name}"


def test_extract_description_basic():
    """
    Test basic description extraction from simple text.
    """
    # Simple text without markdown
    text = "This is a simple description."
    result = extract_description(text)
    assert result == "This is a simple description."

    # Text with leading/trailing whitespace
    text = "  This is a description with whitespace.  "
    result = extract_description(text)
    assert result == "This is a description with whitespace."


def test_extract_description_with_headers():
    """
    Test that markdown headers are skipped when extracting description.
    """
    text = """# Main Title

## Subtitle

This is the actual description that should be extracted.

## Another Section

More content here."""

    result = extract_description(text, max_length=200)
    assert result == "This is the actual description that should be extracted. More content here."
    assert not result.startswith("#")


def test_extract_description_with_horizontal_rules():
    """
    Test that horizontal rules are skipped.
    """
    text = """# Title

---

This is the description after a horizontal rule.

***

More content after another rule."""

    result = extract_description(text)
    assert "---" not in result
    assert "***" not in result
    assert "This is the description" in result
    assert "More content" in result


def test_extract_description_truncation():
    """
    Test that long descriptions are properly truncated at word boundaries.
    """
    # Create a text longer than default max_length (200)
    text = " ".join(["word"] * 100)  # 100 words = ~400 characters
    result = extract_description(text, max_length=50)

    # Should be truncated
    assert len(result) <= 53  # 50 + "..." = 53
    assert result.endswith("...")
    assert not result.endswith(" ...")  # No trailing space before ellipsis


def test_extract_description_empty_text():
    """
    Test handling of empty or whitespace-only text.
    """
    # Empty string
    assert extract_description("") == ""

    # Only whitespace
    assert extract_description("   \n\n   ") == ""

    # Only headers
    text = "# Title\n## Subtitle\n### Another Header"
    assert extract_description(text) == ""


def test_extract_description_custom_max_length():
    """
    Test that custom max_length parameter works correctly.
    """
    text = "This is a longer description that will be truncated at various lengths."

    # Very short max_length
    result = extract_description(text, max_length=20)
    assert len(result) <= 23  # 20 + "..."
    assert result.endswith("...")

    # Exact length (should not truncate if text is shorter)
    short_text = "Short text"
    result = extract_description(short_text, max_length=100)
    assert result == "Short text"
    assert not result.endswith("...")


def test_extract_description_real_modules(terraform_modules_dir, test_logger):
    """
    Test description extraction from real Terraform module files.
    """
    md_files = list(terraform_modules_dir.glob("*.md"))
    assert len(md_files) > 0, "No markdown files found for testing"

    for md_file in md_files:
        record = parse_markdown_file(md_file, test_logger)

        if record and record.text:
            description = extract_description(record.text)

            # Description should not be empty for valid modules
            assert description, f"Empty description extracted from {md_file.name}"

            # Description should not start with markdown syntax
            assert not description.startswith("#"), f"Description starts with header in {md_file.name}"
            assert not description.startswith("---"), f"Description starts with horizontal rule in {md_file.name}"

            # Description should be within reasonable length
            assert len(description) <= 203, f"Description too long in {md_file.name}: {len(description)} chars"

            print(f"\n{md_file.name}:")
            print(f"  Description: {description[:100]}...")


def test_extract_description_multiline_paragraphs():
    """
    Test extraction of descriptions that span multiple lines/paragraphs.
    """
    text = """# Module Title

First paragraph with some content.
This continues on a second line.

Second paragraph here.

## Section Header

This should also be included."""

    result = extract_description(text, max_length=200)

    # Should join multiple paragraphs
    assert "First paragraph" in result
    assert "Second paragraph" in result

    # Should not include the section header text
    assert "Section Header" not in result


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s"])
