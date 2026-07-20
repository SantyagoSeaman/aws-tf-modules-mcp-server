import re
from pathlib import Path

from tfmod_any_examples import coverage_report, extract_examples, find_any_vars, observed_field_names

FIXTURES = Path(__file__).parent.parent / "fixtures/any_examples"
S3_DIR = FIXTURES / "s3_bucket"
EC_DIR = FIXTURES / "elasticache"
OS_DIR = FIXTURES / "opensearch"
HELPER_DIR = FIXTURES / "helper_module"
MERGE_DIR = FIXTURES / "merge_synthetic"
FOREACH_DIR = FIXTURES / "merge_synthetic_foreach"


def _looks_balanced(block: str) -> bool:
    return block.count("[") == block.count("]") and block.count("{") == block.count("}")


# --------------------------------------------------------------------------- #
# find_any_vars
# --------------------------------------------------------------------------- #


def test_find_any_vars_root_count_matches_real_module():
    any_vars = find_any_vars(S3_DIR)
    root = [name for scope, name in any_vars if scope == "root"]
    assert len(root) == 13
    assert set(root) == {
        "website",
        "cors_rule",
        "logging",
        "grant",
        "lifecycle_rule",
        "replication_configuration",
        "server_side_encryption_configuration",
        "intelligent_tiering",
        "object_lock_configuration",
        "metric_configuration",
        "inventory_configuration",
        "analytics_configuration",
        "metadata_encryption_configuration",
    }


def test_find_any_vars_is_comment_tolerant():
    # "website" declares `type = any # map(string)` (idiom N14) - must still count.
    any_vars = find_any_vars(S3_DIR)
    assert ("root", "website") in any_vars


def test_find_any_vars_finds_real_submodule():
    any_vars = find_any_vars(S3_DIR)
    sub = {name for scope, name in any_vars if scope == "notification"}
    assert sub == {"lambda_notifications", "sqs_notifications", "sns_notifications"}


def test_find_any_vars_excludes_wrappers():
    any_vars = find_any_vars(S3_DIR)
    scopes = {scope for scope, _ in any_vars}
    names = {name for _, name in any_vars}
    assert "wrappers" not in scopes
    # "defaults"/"items" are wrappers-only any-vars; must never surface.
    assert "defaults" not in names
    assert "items" not in names


def test_find_any_vars_total_count():
    any_vars = find_any_vars(S3_DIR)
    assert len(any_vars) == 16  # 13 root + 3 notification submodule


def test_find_any_vars_opensearch_root():
    any_vars = find_any_vars(OS_DIR)
    root = {name for scope, name in any_vars if scope == "root"}
    assert "cluster_config" in root
    assert len(root) == 17


def test_find_any_vars_elasticache_root():
    any_vars = find_any_vars(EC_DIR)
    root = {name for scope, name in any_vars if scope == "root"}
    # The real elasticache module declares two root any-vars.
    assert root == {"log_delivery_configuration", "security_group_rules"}


# --------------------------------------------------------------------------- #
# extract_examples - s3-bucket lifecycle_rule (flagship: object-vs-scalar bug)
# --------------------------------------------------------------------------- #


def test_s3_lifecycle_rule_example_matches_real_bytes_and_parses():
    examples = extract_examples(S3_DIR, "root", "lifecycle_rule")
    assert examples, "expected at least one non-trivial lifecycle_rule example"

    source_text = (S3_DIR / "examples/complete/main.tf").read_text()
    for block in examples:
        assert block in source_text, "extracted block must be a verbatim substring of the source file"
        assert _looks_balanced(block)

    combined = "\n".join(examples)
    assert combined.startswith("lifecycle_rule = [") or "lifecycle_rule = [" in combined
    assert "abort_incomplete_multipart_upload_days = 7" in combined


def test_s3_lifecycle_rule_field_names_scalar_not_object_form():
    fields = observed_field_names(S3_DIR, "root", "lifecycle_rule")
    assert "abort_incomplete_multipart_upload_days" in fields
    # The curated docs' historical bug: an object-shaped
    # abort_incomplete_multipart_upload is never actually read by the module.
    assert "abort_incomplete_multipart_upload" not in fields


def test_s3_lifecycle_rule_field_names_cover_nested_dynamic_blocks():
    fields = observed_field_names(S3_DIR, "root", "lifecycle_rule")
    for expected in (
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
    ):
        assert expected in fields, f"expected {expected!r} in observed field names"


def test_trivial_cors_rule_assignment_is_skipped():
    assert extract_examples(S3_DIR, "root", "cors_rule") == []


# --------------------------------------------------------------------------- #
# elasticache log_delivery_configuration - the instance-ceiling case: no
# example sets destination/log_type, but the module reads them.
# --------------------------------------------------------------------------- #


def test_elasticache_log_delivery_field_names_include_offexample_fields():
    fields = observed_field_names(EC_DIR, "root", "log_delivery_configuration")
    for expected in (
        "destination",
        "log_type",
        "destination_type",
        "log_format",
        "create_cloudwatch_log_group",
        "cloudwatch_log_group_name",
        "cloudwatch_log_group_retention_in_days",
        "cloudwatch_log_group_kms_key_id",
        "cloudwatch_log_group_skip_destroy",
        "cloudwatch_log_group_class",
        "tags",
    ):
        assert expected in fields, f"expected {expected!r} in observed field names"


def test_elasticache_log_delivery_field_names_exclude_loop_meta_names():
    fields = observed_field_names(EC_DIR, "root", "log_delivery_configuration")
    assert "k" not in fields
    assert "v" not in fields
    assert "each" not in fields
    assert "key" not in fields


def test_elasticache_log_delivery_example_omits_offexample_fields():
    examples = extract_examples(EC_DIR, "root", "log_delivery_configuration")
    assert examples
    combined = "\n".join(examples)
    assert "cloudwatch_log_group_name" in combined
    assert "destination_type" in combined
    # Bare "destination"/"log_type" keys (as opposed to "destination_type")
    # are never assigned in any example - only read in module source.
    assert re.search(r"(?m)^\s*destination\s*=", combined) is None
    assert re.search(r"(?m)^\s*log_type\s*=", combined) is None


def test_elasticache_example_helper_module_not_misattributed():
    examples = extract_examples(EC_DIR, "root", "log_delivery_configuration")
    combined = "\n".join(examples)
    assert "bogus" not in combined


# --------------------------------------------------------------------------- #
# opensearch cluster_config - deep dynamic-block nesting + a real-world
# same-example helper module (module "vpc").
# --------------------------------------------------------------------------- #


def test_opensearch_cluster_config_example_extracted_and_parses():
    examples = extract_examples(OS_DIR, "root", "cluster_config")
    assert examples
    for block in examples:
        assert _looks_balanced(block)
    combined = "\n".join(examples)
    assert "dedicated_master_enabled" in combined
    assert "bogus" not in combined  # module "vpc" helper must not leak in


def test_opensearch_cluster_config_field_names_include_offexample_fields():
    fields = observed_field_names(OS_DIR, "root", "cluster_config")
    for expected in (
        "warm_count",
        "warm_enabled",
        "warm_type",
        "cold_storage_options",
        "multi_az_with_standby_enabled",
        "dedicated_master_enabled",
        "zone_awareness_enabled",
        "node_options",
    ):
        assert expected in fields, f"expected {expected!r} in observed field names"


# --------------------------------------------------------------------------- #
# Dedicated synthetic helper-module fixture - attribution must route by
# `source`, never by argument name.
# --------------------------------------------------------------------------- #


def test_helper_module_argument_not_misattributed():
    examples = extract_examples(HELPER_DIR, "root", "widget_config")
    assert examples
    combined = "\n".join(examples)
    assert "bogus" not in combined
    assert "large" in combined
    assert "blue" in combined


# --------------------------------------------------------------------------- #
# N2 idiom - merge()-injected synthetic keys must be subtracted even though a
# downstream consumer reads them off the aliased local.
# --------------------------------------------------------------------------- #


def test_merge_injected_synthetic_key_subtracted():
    fields = observed_field_names(MERGE_DIR, "root", "targets")
    assert "arn" in fields
    assert "role_arn" in fields
    assert "name" not in fields  # merge(t, {"name" = i}) - synthetic, not user-supplied


# --------------------------------------------------------------------------- #
# for_each-comprehension merge-injection - the real terraform-aws-modules/
# eventbridge `pipes` bug: MERGE_DIR only covers a locals RHS that references
# var_name and NOTHING else; eventbridge's real locals RHS references
# var.pipes AND a second var in the same expression, and the merge-injected
# key is read back via a RESOURCE for_each comprehension chained through that
# locals alias - two gaps neither of which MERGE_DIR exercises.
# --------------------------------------------------------------------------- #


def test_merge_injected_key_subtracted_when_locals_rhs_references_extra_var():
    """Mirrors the real terraform-aws-modules/eventbridge `pipes` idiom: the
    locals RHS that merge()-injects the synthetic "Name" key also references
    a SECOND var (a postfix-toggle flag) in the same expression, and the
    injected key is read back off `each.value` inside a resource whose
    for_each comprehension is chained through that locals alias. A strict
    "RHS references ONLY var_name" check never recognizes the alias, so
    "Name" used to survive subtraction and leak through as a bogus observed
    field name."""
    fields = observed_field_names(FOREACH_DIR, "root", "pipes")
    assert "source" in fields
    assert "target" in fields
    assert "Name" not in fields


def test_merge_injected_key_subtracted_from_direct_for_each_rhs():
    """The merge() call can also live directly in a resource's own for_each
    comprehension RHS (no locals indirection at all): `for_each = { for k, v
    in var.pipes : k => merge(v, {"Direct" = k}) }`. The injected key must be
    subtracted here too."""
    fields = observed_field_names(FOREACH_DIR, "root", "pipes")
    assert "arn" in fields
    assert "Direct" not in fields


# --------------------------------------------------------------------------- #
# coverage_report
# --------------------------------------------------------------------------- #


def test_coverage_report_s3_bucket_classifies_vars():
    report = coverage_report(S3_DIR)
    assert report["vars"]["root::lifecycle_rule"] == "covered"
    assert report["vars"]["root::cors_rule"] == "trivial_only"
    assert report["covered"] >= 1
    assert report["trivial_only"] >= 1
    total = report["covered"] + report["trivial_only"] + report["none"]
    assert total == len(find_any_vars(S3_DIR))


def test_coverage_report_elasticache():
    report = coverage_report(EC_DIR)
    assert report["vars"]["root::log_delivery_configuration"] == "covered"


def test_coverage_report_opensearch():
    report = coverage_report(OS_DIR)
    assert report["vars"]["root::cluster_config"] == "covered"


def test_coverage_report_merge_synthetic():
    report = coverage_report(MERGE_DIR)
    # merge_synthetic has no examples/ dir at all -> the one any-var is "none".
    assert report["vars"]["root::targets"] == "none"
