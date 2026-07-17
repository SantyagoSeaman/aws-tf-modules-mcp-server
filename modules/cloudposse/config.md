# Terraform AWS Config Module

## Module Information

- **Module Name**: `config`
- **Module ID**: `cloudposse/config/aws`
- **Source**: `cloudposse/config/aws`
- **GitHub Repository**: https://github.com/cloudposse/terraform-aws-config
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/config/aws/latest
- **Latest Version**: 2.0.0
- **Purpose**: Terraform module that enables and configures AWS Config — configuration recorder, delivery channel, AWS Managed/custom compliance rules, and multi-account/multi-region aggregation — with an optional SNS topic for compliance findings
- **Service**: AWS Config
- **Category**: Security, Compliance, Governance
- **Keywords**: config, aws-config, config-rules, config-rule, compliance, audit, configuration-recorder, delivery-channel, config-aggregator, conformance-pack, managed-rules, custom-rules, drift-detection, resource-inventory, governance, cis-benchmark, multi-account-aggregation
- **Use For**: enabling AWS Config across an account or an entire AWS Organization, continuous resource configuration recording, compliance auditing against managed and custom rules, CIS AWS Foundations Benchmark checks, multi-account/multi-region configuration aggregation, drift detection triggers, SNS notifications for non-compliant findings, deploying AWS Config Conformance Packs, governance baselines for regulated workloads, security posture reporting

## Description

AWS Config is a fully managed service that continuously records the configuration of AWS resources in an account and evaluates those configurations against a set of rules, producing an auditable, point-in-time and historical compliance record. This Terraform module wires together a complete, working AWS Config deployment: a configuration recorder that snapshots supported resource types (optionally including global resources such as IAM in a single designated region), a delivery channel that streams that history to an existing S3 bucket, and the AWS Config Rules that evaluate compliance — AWS Managed Rules (via `managed_rules`), plus two custom rule types backed by a Lambda function (`custom_lambda_rules`) or an inline CFN Guard/policy document (`custom_policy_rules`).

Beyond a single account, the module also manages AWS Config Aggregators, letting one account collect configuration and compliance data from many accounts and regions into a single view. It supports two aggregation models: a standard account-based aggregator that pulls from an explicit list of `child_resource_collector_accounts`, and an AWS-Organizations-wide aggregator (`is_organization_aggregator`) that automatically includes every account in the organization instead of a maintained list. Cross-account aggregation is wired through `aws_config_aggregate_authorization` resources on the sending side, and the module can optionally provision the IAM roles AWS Config needs — a base delivery/recorder role and, separately, an organization-aggregator role.

Two focused submodules extend the root module: `conformance-pack`, which deploys an AWS Config Conformance Pack (a YAML template bundling managed and custom rules) as a single artifact, and `cis-1-2-rules`, which provisions the specific rule catalog for the CIS AWS Foundations Benchmark v1.2. Like every Cloud Posse module, it builds resource names and tags through the shared `label`/`context` convention, and it can optionally create an SNS topic (via the `sns-topic` module) so compliance findings trigger downstream notifications.

## Key Features

- **Configuration Recorder**: Continuously records configuration snapshots of supported AWS resource types, optionally including global resources (IAM) in one designated collector region
- **Delivery Channel**: Streams the recorded configuration history to an existing S3 bucket (the bucket is NOT created by this module)
- **Recording Mode Control**: `recording_mode` sets CONTINUOUS vs DAILY recording frequency, with per-resource-type overrides via `recording_mode_override`
- **AWS Managed Rules**: Enable any number of AWS Config Managed Rules via the `managed_rules` map, each independently toggled with `enabled`
- **Custom Lambda Rules**: Define custom compliance rules backed by a Lambda function via `custom_lambda_rules`
- **Custom Policy Rules**: Define custom compliance rules backed by an inline CFN Guard/policy document via `custom_policy_rules`
- **Multi-Region Aggregation**: Aggregate configuration/compliance data from multiple regions into one recorder region via `aws_config_configuration_aggregator`
- **Multi-Account Aggregation**: Aggregate data from a fixed list of `child_resource_collector_accounts` into a designated central account
- **AWS Organizations Aggregator**: Set `is_organization_aggregator = true` to automatically aggregate every account in the AWS Organization instead of maintaining an explicit account list
- **Cross-Account Authorization**: Manages `aws_config_aggregate_authorization` resources so child accounts can send data to the central aggregator account
- **Disabled Aggregation Regions**: `disabled_aggregation_regions` (defaults to `["ap-northeast-3"]`) skips aggregator creation in regions with known Config limitations
- **Optional SNS Notifications**: `create_sns_topic` provisions an SNS topic (via the `sns-topic` module) with configurable `subscribers` for compliance findings
- **Existing SNS Topic Support**: `findings_notification_arn` routes findings to an already-existing SNS topic instead of creating a new one
- **Optional IAM Role Creation**: `create_iam_role` provisions the delivery/recorder IAM role with the AWS-managed `AWS_ConfigRole` policy attached
- **Separate Organization-Aggregator IAM Role**: `create_organization_aggregator_iam_role` provisions a distinct role with the `AWSConfigRoleForOrganizations` policy, independent of the base recorder role
- **Conformance Pack Submodule**: Deploy an AWS Config Conformance Pack template (local file or GitHub-hosted, with `parameter_overrides`) as a single unit
- **CIS 1.2 Rule Set Submodule**: Provision the CIS AWS Foundations Benchmark v1.2 rule catalog with `cis-1-2-rules`, including logging-account and global-resource-region toggles
- **Cloud Posse Label Convention**: Consistent resource naming/tagging via `namespace`/`stage`/`name`/`context` inputs shared across every Cloud Posse module
- **KMS Encryption Support**: `s3_kms_key_arn` and `sqs_queue_kms_master_key_id`/`sns_encryption_key_id` encrypt delivered config data and the optional SNS/SQS notification path
- **Conditional Creation**: The `enabled` flag (part of the Cloud Posse `context`) toggles whether the module creates any resources at all

## Main Use Cases

1. **Continuous Compliance Auditing**: Evaluate every resource change against AWS Managed and custom Config Rules
2. **CIS AWS Foundations Benchmark**: Deploy the CIS 1.2 rule catalog via the `cis-1-2-rules` submodule for baseline hardening checks
3. **Multi-Account Governance**: Aggregate configuration and compliance data from every account in an AWS Organization into one security account
4. **Regulatory/Conformance Reporting**: Roll out an AWS Config Conformance Pack for a specific compliance framework in one deployment
5. **Drift Detection**: Detect configuration drift on critical resources (security groups, IAM, S3) via managed/custom rules
6. **Custom Compliance Logic**: Enforce org-specific policies with Lambda-backed or CFN-Guard-backed custom rules
7. **Global Resource Tracking**: Record IAM and other global resources once, in a single designated collector region
8. **Compliance Notifications**: Route non-compliant-resource findings to an SNS topic for Slack/PagerDuty/email alerting
9. **Security Baseline for New Accounts**: Bootstrap AWS Config recording and rules as part of a landing-zone/account-vending pipeline
10. **Audit Evidence Collection**: Retain a durable configuration history in S3 for SOC2/PCI/HIPAA audit evidence

## Usage Examples

### Example 1: Single-account AWS Config with managed rules and SNS notifications

```hcl
module "config_storage" {
  source  = "cloudposse/config-storage/aws"
  version = "1.0.2"

  namespace = "acme"
  stage     = "prod"
  name      = "config"
}

module "config" {
  source  = "cloudposse/config/aws"
  version = "2.0.0"

  namespace = "acme"
  stage     = "prod"
  name      = "config"

  s3_bucket_id  = module.config_storage.bucket_id
  s3_bucket_arn = module.config_storage.bucket_arn

  global_resource_collector_region = "us-east-1"

  create_iam_role  = true
  create_sns_topic = true

  subscribers = {
    email = {
      protocol = "email"
      endpoint = "compliance-alerts@acme.example"
    }
  }

  # NOTE: the object shape below (description/identifier/input_parameters/tags/enabled)
  # is the actual v2.0.0 `managed_rules` type — see "Notes for AI Agents" for a gotcha
  # about a stale example elsewhere in this module's own docs.
  managed_rules = {
    s3-bucket-public-read-prohibited = {
      description       = "Checks that S3 buckets do not allow public read access."
      identifier        = "S3_BUCKET_PUBLIC_READ_PROHIBITED"
      input_parameters  = {}
      tags              = {}
      enabled           = true
    }
    iam-user-mfa-enabled = {
      description       = "Checks whether IAM users have MFA enabled."
      identifier        = "IAM_USER_MFA_ENABLED"
      input_parameters  = {}
      tags              = {}
      enabled           = true
    }
  }
}
```

### Example 2: AWS-Organizations-wide aggregator in the central security account

```hcl
module "config_storage" {
  source  = "cloudposse/config-storage/aws"
  version = "1.0.2"

  namespace = "acme"
  stage     = "security"
  name      = "config"
}

module "config_org_aggregator" {
  source  = "cloudposse/config/aws"
  version = "2.0.0"

  namespace = "acme"
  stage     = "security"
  name      = "config"

  s3_bucket_id  = module.config_storage.bucket_id
  s3_bucket_arn = module.config_storage.bucket_arn

  # Deploy this exact region value identically across every account in the org
  global_resource_collector_region = "us-east-1"

  is_organization_aggregator              = true
  create_organization_aggregator_iam_role = true
  create_iam_role                         = true

  # Osaka is excluded by default; only add regions Config aggregation actually supports
  disabled_aggregation_regions = ["ap-northeast-3"]
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `s3_bucket_id` | `string` | *(required)* | The id (name) of an existing S3 bucket used to store the configuration history — this module does NOT create the bucket (see `cloudposse/config-storage/aws`) |
| `s3_bucket_arn` | `string` | *(required)* | The ARN of the existing S3 bucket used to store the configuration history |
| `global_resource_collector_region` | `string` | *(required)* | The single region that records global resources (e.g. IAM); must be the same value across every account/region deployment |
| `enabled` | `bool` | `null` | Set to false to prevent the module from creating any resources |
| `namespace` | `string` | `null` | ID element — organization abbreviation, e.g. `eg` or `cp` |
| `stage` | `string` | `null` | ID element — e.g. `prod`, `staging`, `security` |
| `name` | `string` | `null` | ID element — the component or solution name |
| `tags` | `map(string)` | `{}` | Additional tags applied to all resources |
| `context` | `any` | `{ "enabled": true, ... }` | Cloud Posse context object bundling namespace/stage/name/tags/etc. — see Notes for AI Agents for the full field list |
| `create_iam_role` | `bool` | `false` | Creates the IAM Role AWS Config uses for the delivery channel/recorder (and SNS publish, if enabled) |
| `create_organization_aggregator_iam_role` | `bool` | `false` | Creates a separate IAM Role for the AWS Organizations aggregator to fetch data from member accounts |
| `iam_role_arn` | `string` | `null` | ARN of an existing IAM Role to use instead of `create_iam_role` |
| `iam_role_organization_aggregator_arn` | `string` | `null` | ARN of an existing IAM Role to use instead of `create_organization_aggregator_iam_role` |
| `is_organization_aggregator` | `bool` | `false` | Makes the aggregator an AWS-Organizations-wide aggregator instead of an explicit account list |
| `central_resource_collector_account` | `string` | `null` | Account ID of the central account that aggregates Config data from other accounts (omit to aggregate only within this account) |
| `child_resource_collector_accounts` | `set(string)` | `null` | Account IDs of other accounts that will send their AWS Config data to this account (non-organization aggregation only) |
| `disabled_aggregation_regions` | `list(string)` | `["ap-northeast-3"]` | Regions where config aggregation is disabled |
| `recording_mode` | `object` | `null` | CONTINUOUS vs DAILY recording frequency, with an optional per-resource-type override — fields: `recording_frequency`, `recording_mode_override` |
| `s3_key_prefix` | `string` | `null` | Prefix for AWS Config objects stored in the S3 bucket |
| `s3_kms_key_arn` | `string` | `null` | ARN of the KMS key used to encrypt objects delivered by AWS Config to the S3 bucket |
| `managed_rules` | `map(object)` | `{}` | AWS Config Managed Rules to enable, keyed by rule name — each entry needs `description`, `identifier`, `input_parameters`, `tags`, `enabled` |
| `custom_lambda_rules` | `map(object)` | `{}` | Custom Config Rules backed by a Lambda function — fields: `description`, `lambda_function_arn`, `input_parameters`, `source_identifier`, `evaluation_mode`, `scope`, `tags`, `enabled` |
| `custom_policy_rules` | `map(object)` | `{}` | Custom Config Rules backed by an inline CFN Guard/policy document — fields: `description`, `policy`, `policy_runtime`, `enable_debug_log_delivery`, `evaluation_mode`, `input_parameters`, `scope`, `tags`, `enabled` |
| `create_sns_topic` | `bool` | `false` | Creates an SNS topic for findings notifications (provide `subscribers` when true) |
| `subscribers` | `map(any)` | `{}` | SNS topic subscriptions for the findings topic — fields: `protocol`, `endpoint`, `endpoint_auto_confirms`, `raw_message_delivery` (see the `sns-topic` module) |
| `findings_notification_arn` | `string` | `null` | ARN of an existing SNS topic to send findings to instead of `create_sns_topic` |
| `sns_encryption_key_id` | `string` | `""` | KMS CMK ID used to encrypt the SNS findings topic |
| `sqs_queue_kms_master_key_id` | `string` | `""` | KMS CMK ID used to encrypt the SNS topic's dead-letter SQS queue |
| `allowed_aws_services_for_sns_published` | `list(string)` | `[]` | AWS services allowed to publish to the SNS findings topic when no external policy is used |
| `allowed_iam_arns_for_sns_publish` | `list(string)` | `[]` | IAM role/user ARNs allowed to publish to the SNS findings topic when no external policy is used |
| `force_destroy` | `bool` | `false` | Allows the delivery-channel-dependent resources to be destroyed even with objects present |

## Main Outputs

| Output | Description |
|--------|-------------|
| `aws_config_configuration_recorder_id` | The ID of the AWS Config Recorder |
| `storage_bucket_id` | Name (ID) of the S3 bucket storing the configuration history (echoes the `s3_bucket_id` input) |
| `storage_bucket_arn` | ARN of the S3 bucket storing the configuration history (echoes the `s3_bucket_arn` input) |
| `sns_topic` | The SNS topic used for findings notifications (set only when `create_sns_topic = true`) |
| `sns_topic_subscriptions` | SNS topic subscriptions created for the findings topic |
| `iam_role` | IAM Role used to make read/write requests to the delivery channel and describe AWS resources |
| `iam_role_organization_aggregator` | IAM Role used by the organization aggregator to fetch AWS Config data from member accounts |
| `custom_lambda_rule_arns` | Map of custom Lambda rule names to their ARNs |
| `custom_policy_rule_arns` | Map of custom policy rule names to their ARNs |

## Submodules

### 1. conformance-pack

- **Purpose**: Creates an `aws_config_conformance_pack` — deploys an AWS Config Conformance Pack template (a YAML bundle of managed/custom rules) as a single unit
- **Source**: `cloudposse/config/aws//modules/conformance-pack`
- **Documentation Link**: https://registry.terraform.io/modules/cloudposse/config/aws/latest/submodules/conformance-pack
- **Key Features**: Local or GitHub-hosted templates, `parameter_overrides` for template parameters, private-repo `access_token` support
- **Use Cases**: Rolling out a compliance framework's rule bundle as one unit, standardized org-wide conformance baselines

### 2. cis-1-2-rules

- **Purpose**: Creates the AWS Config Rules for the CIS AWS Foundations Benchmark v1.2 from a curated set of YAML rule catalogs
- **Source**: `cloudposse/config/aws//modules/cis-1-2-rules`
- **Documentation Link**: https://registry.terraform.io/modules/cloudposse/config/aws/latest/submodules/cis-1-2-rules
- **Key Features**: `config_rules_paths` catalog selection (cloudtrail, cmk, iam, network, vpc rule groups by default), logging-account vs global-resource-region toggles, `cloudtrail_bucket_name`/`support_policy_arn` wiring
- **Use Cases**: CIS Benchmark v1.2 compliance certification, security baseline audits, landing-zone hardening checks

## Best Practices

### Recorder and Delivery Setup

1. **Provision Storage First**: Create the S3 bucket (e.g., via `cloudposse/config-storage/aws`) before this module — `s3_bucket_id`/`s3_bucket_arn` are required inputs, not resources this module creates.
2. **Pick One Global Collector Region**: Set `global_resource_collector_region` to exactly one region per account; only the recorder in that region sets `include_global_resource_types = true`, so IAM and other global resources are not double-recorded.
3. **Prefer CONTINUOUS Recording for Security-Critical Types**: Use `recording_mode.recording_mode_override` to keep high-signal resource types on CONTINUOUS while defaulting the rest to DAILY to control cost.
4. **Encrypt Delivered Data**: Set `s3_kms_key_arn` so AWS Config objects land in S3 encrypted with a customer-managed key.

### Multi-Account and Multi-Region Aggregation

1. **Use the Organization Aggregator for New Estates**: Set `is_organization_aggregator = true` with `create_organization_aggregator_iam_role = true` so every current and future organization account is aggregated automatically, instead of maintaining `child_resource_collector_accounts` by hand.
2. **Deploy the Aggregator Once, in the Central Account**: The `aws_config_configuration_aggregator` resource is only created when the calling account is the `central_resource_collector_account` (or that variable is omitted, meaning "this account") AND the current region equals `global_resource_collector_region` — applying this module identically everywhere will not duplicate the aggregator, but confirm it lands by checking the plan in the intended central account/region.
3. **Authorize Every Child Account**: Each non-central, non-organization account must apply this module with `central_resource_collector_account` set to the security account ID so its `aws_config_aggregate_authorization` grant is created.
4. **Watch the Osaka Exception**: Leave `ap-northeast-3` in `disabled_aggregation_regions` (the default) unless that region is explicitly onboarded to Config aggregation.

### Compliance Rules

1. **Start with AWS Managed Rules**: Cover common controls (public S3 buckets, unencrypted volumes, MFA) via `managed_rules` before writing custom logic.
2. **Reserve Custom Rules for Gaps**: Use `custom_lambda_rules` for logic needing external API calls or complex evaluation, and `custom_policy_rules` (CFN Guard) for declarative, no-Lambda policy checks.
3. **Toggle Rules Explicitly**: Every rule map entry requires `enabled = true`/`false` — a rule left out of the map is simply absent, not "disabled"; keep unused rules in the map with `enabled = false` if a documented-but-off state matters.
4. **Adopt the CIS Submodule for Fast Baselines**: Use `cis-1-2-rules` to stand up the CIS AWS Foundations Benchmark v1.2 rule set instead of hand-authoring the equivalent managed rules.

### Notifications and IAM

1. **Separate the Two IAM Roles**: `create_iam_role` (recorder/delivery/SNS) and `create_organization_aggregator_iam_role` (organization aggregator) are independent — enabling one does not create the other.
2. **Reuse an Existing SNS Topic When Possible**: Set `findings_notification_arn` instead of `create_sns_topic = true` when a shared compliance-notifications topic already exists.
3. **Restrict Through the Bucket, Not the Module**: AWS Config itself has no logging-redaction concept (unlike CloudTrail/WAF) — control exposure through the S3 bucket policy and `s3_kms_key_arn`.
4. **Pin the Module Version**: Use an explicit `version = "2.0.0"` — Cloud Posse's own README usage snippet intentionally omits a version pin, so do not copy it verbatim into production code.

## Additional Resources

- **Module Repository**: https://github.com/cloudposse/terraform-aws-config
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/config/aws/latest
- **Module Examples**: https://github.com/cloudposse/terraform-aws-config/tree/main/examples/complete
- **Companion Storage Module**: https://registry.terraform.io/modules/cloudposse/config-storage/aws/latest
- **AWS Config Developer Guide**: https://docs.aws.amazon.com/config/latest/developerguide/WhatIsConfig.html
- **AWS Config Managed Rules List**: https://docs.aws.amazon.com/config/latest/developerguide/managed-rules-by-aws-config.html
- **Multi-Account Multi-Region Data Aggregation**: https://docs.aws.amazon.com/config/latest/developerguide/aggregate-data.html
- **aws_config_configuration_aggregator Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/config_configuration_aggregator
- **CIS AWS Foundations Benchmark**: https://docs.aws.amazon.com/audit-manager/latest/userguide/CIS-1-2.html
- **AWS Config Pricing**: https://aws.amazon.com/config/pricing/

## Notes for AI Agents

This module is published by Cloud Posse (namespace `cloudposse`), not the `terraform-aws-modules` org. It uses Cloud Posse's `context`/`label` convention — inputs like `namespace`, `stage`, `name`, `environment`, `tenant`, `attributes`, `tags` and a `context` object drive resource naming/tagging across every Cloud Posse module. Do NOT propagate this convention onto other (differently-styled) modules in the same project; set the label inputs this module needs and leave other vendors' modules alone.

When using this module in automated workflows:

1. **The S3 Bucket Is Not Created Here**: `s3_bucket_id` and `s3_bucket_arn` are required inputs — provision the bucket separately (Cloud Posse ships a companion `cloudposse/config-storage/aws` module) before or alongside this module.
2. **Stale README Usage Snippet**: The module's own top-level `README.md` "Usage" example sets a `trigger_type` key inside `managed_rules`, but the actual v2.0.0 variable type is `map(object({ description, identifier, input_parameters, tags, enabled }))` with no `trigger_type` field — verify the exact shape via `grep_module_docs` or the registry type before writing `managed_rules`/`custom_lambda_rules`/`custom_policy_rules` entries, not from that snippet.
3. **Aggregation Is Conditional, Not Universal**: The root `aws_config_configuration_aggregator` resource is only created when the applying account equals `central_resource_collector_account` (or that input is omitted) AND the current region equals `global_resource_collector_region`; applying this module unmodified in a member/child account instead creates an `aws_config_aggregate_authorization` grant, not an aggregator.
4. **Organization vs. Account Aggregation Are Mutually Exclusive Paths**: Setting `is_organization_aggregator = true` switches the aggregator to an AWS-Organizations-wide source and requires an organization-aggregator IAM role (`create_organization_aggregator_iam_role` or `iam_role_organization_aggregator_arn`); leaving it `false` uses the fixed `child_resource_collector_accounts` list instead — do not set both models expecting them to combine.
5. **One Global Collector Region, Repo-Wide**: `global_resource_collector_region` must be the identical value across every account/region that deploys this module — a mismatch causes IAM and other global resources to be recorded zero times or more than once.
6. **Two Independent IAM Roles**: `create_iam_role` provisions the base recorder/delivery (and optional SNS-publish) role; `create_organization_aggregator_iam_role` provisions a separate role solely for the organization aggregator. Enabling one does not create the other.
7. **`ap-northeast-3` Is Excluded by Default**: `disabled_aggregation_regions` defaults to `["ap-northeast-3"]` (Osaka) due to known AWS Config aggregation limitations there — only remove it if that region is explicitly supported in the target organization.
8. **Rules Need `enabled = true` to Exist**: All three rule maps (`managed_rules`, `custom_lambda_rules`, `custom_policy_rules`) are filtered by `enabled` at apply time — an entry with `enabled = false` is a documented no-op, but an entry simply absent from the map is indistinguishable from "never considered."
9. **Pin the Module Version**: Use an explicit `version = "2.0.0"` constraint for reproducible deployments; Cloud Posse's own usage examples intentionally omit a version pin, which is not a pattern to copy into real infrastructure.
10. **Verify Managed Rule Identifiers**: Confirm exact AWS Config Managed Rule `identifier` values via `grep_module_docs` or the AWS documentation before pinning them in `managed_rules` — identifiers are case-sensitive AWS-defined constants (e.g. `S3_BUCKET_PUBLIC_READ_PROHIBITED`).
