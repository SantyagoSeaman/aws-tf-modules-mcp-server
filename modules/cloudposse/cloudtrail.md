# Terraform AWS CloudTrail Module

## Module Information

- **Module Name**: `cloudtrail`
- **Module ID**: `cloudposse/cloudtrail/aws`
- **Source**: `cloudposse/cloudtrail/aws`
- **GitHub Repository**: https://github.com/cloudposse/terraform-aws-cloudtrail
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/cloudtrail/aws/latest
- **Latest Version**: 0.24.0
- **Purpose**: Terraform module that provisions an AWS CloudTrail trail — recording management-event and data-event API activity as a durable event history — and delivers it into an existing, separately provisioned encrypted/versioned S3 bucket, with optional CloudWatch Logs streaming, SNS delivery notifications, and CloudTrail Insights anomaly detection
- **Service**: AWS CloudTrail
- **Category**: Security, Logging, Governance
- **Keywords**: cloudtrail, aws-cloudtrail, api-logging, api-activity, event-history, management-events, data-events, trail, audit-log, s3-log-bucket, kms-encrypted-logs, cloudtrail-insights, organization-trail, multi-region-trail, log-file-validation, cloudwatch-logs, sns-notifications, insight-selector
- **Use For**: recording AWS account API activity as an auditable event history, centralizing management-event and data-event logs into an encrypted S3 bucket, cross-account audit-log delivery to a dedicated Audit/Log-Archive account, AWS-Organizations-wide trail covering every member account, multi-region trail coverage across all AWS regions, log-file integrity validation via signed digests, streaming CloudTrail events to CloudWatch Logs for near-real-time alerting, SNS notifications on log-file delivery, granular data-event logging for S3/Lambda/DynamoDB API calls, CloudTrail Insights anomaly detection on unusual API call volume

## Description

AWS CloudTrail records the history of API calls made against an AWS account or AWS Organization — who called which API, when, from where, and against which resource — and delivers that event history as log files to an S3 bucket. This Terraform module creates a single `aws_cloudtrail` resource and wires up the trail's delivery, encryption, and notification settings; it does **not** create the destination S3 bucket itself. The bucket can live in the same AWS account as the trail or in a completely separate account, which is the common pattern for organizations that isolate their audit/log-archive environment from production, staging, and development accounts: the trail is created in the source account while the bucket — and the bucket policy granting CloudTrail write access — lives in the Audit account.

The module's core levers split cleanly into what gets logged and where it goes. `include_global_service_events` controls whether global-service (e.g. IAM, STS) management events are captured, `is_multi_region_trail` decides whether the trail spans every AWS region or just the region it is applied in, and `is_organization_trail` promotes it to an AWS-Organizations-wide trail that automatically covers every member account. Beyond management events, `event_selector` (classic) and `advanced_event_selector` (the newer, more flexible mechanism) turn on **data-event** logging — object-level S3 access, Lambda invocations, DynamoDB item operations, and similar high-volume, resource-level API calls that management-event logging alone does not capture. `insight_selector` additionally enables CloudTrail Insights, which detects unusual API call volume or error-rate patterns on top of the recorded event history.

For delivery and integrity, `kms_key_arn` encrypts the log objects CloudTrail writes to S3 with a customer-managed KMS key, `enable_log_file_validation` turns on signed digest files so log tampering can be detected after the fact, and `cloud_watch_logs_group_arn`/`cloud_watch_logs_role_arn` optionally stream events to CloudWatch Logs for near-real-time monitoring and alerting alongside the S3 archive. `sns_topic_name` optionally publishes a notification every time a new log file is delivered. Like every Cloud Posse module, resource naming and tagging are driven by the shared `namespace`/`stage`/`name`/`context` label convention (via the `cloudposse/label/null` dependency), not by this module's own logic.

## Key Features

- **Single Trail Resource**: Creates one `aws_cloudtrail` resource capturing account (or organization) API activity as an event history
- **Bring-Your-Own Bucket**: `s3_bucket_name` (required) targets an existing, already-encrypted/versioned S3 bucket — same account or a different one — the module never creates or manages the bucket or its policy
- **Multi-Region Trail**: `is_multi_region_trail` (default `true`) captures events from every AWS region instead of just the region the trail is applied in
- **AWS Organizations Trail**: `is_organization_trail` promotes the trail to an org-wide trail automatically covering every member account (must be applied from the management or a delegated administrator account)
- **Global Service Events**: `include_global_service_events` captures IAM/STS and other global-service management events
- **Data-Event Logging (classic)**: `event_selector` turns on object-level S3, Lambda, and DynamoDB data-event logging with `include_management_events`/`read_write_type`/`data_resource` controls
- **Data-Event Logging (advanced)**: `advanced_event_selector` is the newer, field-based selector mechanism (`field_selector` with `equals`/`not_equals`/`starts_with`/etc.) for the same data-event use case
- **CloudTrail Insights**: `insight_selector` enables anomaly detection on unusual API call volume/error rate
- **Log File Integrity Validation**: `enable_log_file_validation` (default `true`) creates signed digest files proving the delivered logs have not been tampered with
- **KMS Encryption**: `kms_key_arn` encrypts CloudTrail's delivered log objects with a customer-managed KMS key
- **CloudWatch Logs Streaming**: `cloud_watch_logs_group_arn` + `cloud_watch_logs_role_arn` stream trail events to a CloudWatch Logs group for near-real-time monitoring
- **SNS Delivery Notifications**: `sns_topic_name` publishes a notification on every log-file delivery
- **S3 Key Prefix**: `s3_key_prefix` namespaces this trail's objects within a shared destination bucket
- **Cloud Posse Label Convention**: Consistent resource naming/tagging via `namespace`/`stage`/`name`/`context` inputs shared across every Cloud Posse module
- **Conditional Creation**: The `enabled` flag (part of the Cloud Posse `context`) toggles whether the module creates any resources at all

## Main Use Cases

1. **Account-Wide API Activity Logging**: Record every management-event API call made against an AWS account as a durable, queryable event history
2. **AWS Organizations Audit Trail**: Deploy one trail that automatically covers every current and future member account via `is_organization_trail`
3. **Cross-Account Log Isolation**: Run the trail in a workload account while logs land in a dedicated Audit/Log-Archive account's bucket, restricting read access to security teams only
4. **Data-Event Logging for Sensitive Data Stores**: Turn on `event_selector`/`advanced_event_selector` to capture object-level S3 GetObject/PutObject calls or Lambda invocations, not just management events
5. **Tamper-Evident Log Integrity**: Enable `enable_log_file_validation` so any post-delivery modification of a log file is cryptographically detectable
6. **Near-Real-Time Security Monitoring**: Stream events to CloudWatch Logs (`cloud_watch_logs_group_arn`) and drive metric filters/alarms off specific API calls
7. **Anomaly Detection on API Behavior**: Use `insight_selector` (CloudTrail Insights) to surface unusual spikes in API call volume or error rate
8. **Delivery Notifications**: Wire `sns_topic_name` so downstream automation (Lambda, SIEM ingestion) fires the moment a new log file lands
9. **Global Resource Activity Tracking**: Capture IAM and other global-service events once via `include_global_service_events`
10. **Regulatory Audit Evidence**: Retain an immutable, KMS-encrypted event history of account activity for SOC2/PCI/HIPAA-style audit evidence

## Usage Examples

### Example 1: Single-account trail against an existing bucket

```hcl
module "cloudtrail" {
  source  = "cloudposse/cloudtrail/aws"
  version = "0.24.0"

  namespace = "eg"
  stage     = "dev"
  name      = "cluster"

  s3_bucket_name = "my-cloudtrail-logs-bucket"

  enable_log_file_validation    = true
  include_global_service_events = true
  is_multi_region_trail         = false
  enable_logging                = true
}
```

### Example 2: Multi-region organization trail with a companion log bucket, KMS encryption, and CloudWatch Logs streaming

```hcl
module "cloudtrail_s3_bucket" {
  source  = "cloudposse/cloudtrail-s3-bucket/aws"
  version = "0.32.0"

  namespace = "eg"
  stage     = "audit"
  name      = "cloudtrail"

  # Grants the bucket policy CloudTrail itself requires to deliver logs --
  # this module does NOT write that policy, cloudtrail-s3-bucket does.
  force_destroy = false
}

resource "aws_cloudwatch_log_group" "cloudtrail" {
  name              = "/cloudtrail/eg-audit"
  retention_in_days = 365
}

resource "aws_iam_role" "cloudtrail_cloudwatch" {
  name = "eg-audit-cloudtrail-cloudwatch"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "cloudtrail.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

module "cloudtrail" {
  source  = "cloudposse/cloudtrail/aws"
  version = "0.24.0"

  namespace = "eg"
  stage     = "audit"
  name      = "org"

  s3_bucket_name = module.cloudtrail_s3_bucket.bucket_id

  is_organization_trail          = true
  is_multi_region_trail          = true
  include_global_service_events  = true
  enable_log_file_validation     = true

  kms_key_arn                = aws_kms_key.cloudtrail.arn
  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.cloudtrail.arn}:*"
  cloud_watch_logs_role_arn  = aws_iam_role.cloudtrail_cloudwatch.arn

  insight_selector = [
    { insight_type = "ApiCallRateInsight" },
    { insight_type = "ApiErrorRateInsight" },
  ]
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `s3_bucket_name` | `string` | *(required)* | Name of the existing S3 bucket where CloudTrail delivers logs — this module does NOT create the bucket (see `cloudposse/cloudtrail-s3-bucket/aws`) |
| `enable_logging` | `bool` | `true` | Enable logging for the trail |
| `enable_log_file_validation` | `bool` | `true` | Enables signed digest files so delivered log content can be validated for integrity |
| `include_global_service_events` | `bool` | `false` | Publishes events from global services such as IAM to the log files |
| `is_multi_region_trail` | `bool` | `true` | Creates the trail across all regions instead of just the region it is applied in |
| `is_organization_trail` | `bool` | `false` | Makes this an AWS-Organizations-wide trail covering every member account (apply from the management/delegated administrator account) |
| `kms_key_arn` | `string` | `""` | KMS key ARN used to encrypt the logs CloudTrail delivers to S3 |
| `cloud_watch_logs_group_arn` | `string` | `""` | ARN of the CloudWatch Logs log group CloudTrail streams events to |
| `cloud_watch_logs_role_arn` | `string` | `""` | ARN of the IAM role CloudTrail assumes to write to the CloudWatch Logs group |
| `sns_topic_name` | `string` | `null` | Name of an SNS topic that receives a notification for every log-file delivery |
| `s3_key_prefix` | `string` | `null` | Prefix under which this trail's objects are stored in the destination bucket |
| `event_selector` | `list(object)` | `[]` | Classic data-event selector — object fields: `include_management_events`, `read_write_type`, `exclude_management_event_sources`, `data_resource` (list of `{ type, values }`); enables object-level S3/Lambda/DynamoDB data-event logging beyond `include_global_service_events`' management events |
| `advanced_event_selector` | `list(object)` | `[]` | Newer, field-based data-event selector — object fields: `name`, `field_selector` (list of `{ field, equals, not_equals, starts_with, not_starts_with, ends_with, not_ends_with }`); do not set alongside `event_selector` on the same trail |
| `insight_selector` | `list(object)` | `[]` | CloudTrail Insights selector for anomaly detection — object field: `insight_type` (e.g. `ApiCallRateInsight`, `ApiErrorRateInsight`) |
| `enabled` | `bool` | `null` | Set to `false` to prevent the module from creating any resources |
| `namespace` | `string` | `null` | ID element — organization abbreviation, e.g. `eg` or `cp` |
| `stage` | `string` | `null` | ID element — e.g. `prod`, `staging`, `audit` |
| `name` | `string` | `null` | ID element — the component or solution name |
| `environment` | `string` | `null` | ID element — usually a region or role abbreviation |
| `tenant` | `string` | `null` | ID element _(rarely used)_ — a customer identifier for multi-tenant setups |
| `attributes` | `list(string)` | `[]` | ID element — additional attributes appended to `id` |
| `tags` | `map(string)` | `{}` | Additional tags applied to all resources |
| `additional_tag_map` | `map(string)` | `{}` | Additional key-value pairs merged into each map in `tags_as_list_of_maps`; not added to `tags` or `id` |
| `context` | `any` | `{ "enabled": true, ... }` | Cloud Posse context object bundling namespace/stage/name/tags/etc. — see Notes for AI Agents for the full field list |
| `delimiter` | `string` | `null` | Delimiter between ID elements; defaults to `-` |
| `label_key_case` | `string` | `null` | Letter case of generated tag keys: `lower`, `title`, or `upper` |
| `label_value_case` | `string` | `null` | Letter case of ID elements/tag values: `lower`, `title`, `upper`, or `none` |
| `label_order` | `list(string)` | `null` | Order in which ID elements appear in `id` |
| `id_length_limit` | `number` | `null` | Limit `id` to this many characters (`0` = unlimited) |
| `descriptor_formats` | `any` | `{}` | Additional named descriptors for the `descriptors` output — map values shaped `{ format = string, labels = list(string) }` |
| `regex_replace_chars` | `string` | `null` | Regex of characters to strip from ID elements; defaults to stripping everything but hyphens, letters, and digits |
| `labels_as_tags` | `set(string)` | `["default"]` | Set of ID elements to also emit as tags; set to `[]` to suppress all generated tags |

## Main Outputs

| Output | Description |
|--------|-------------|
| `cloudtrail_id` | The ID of the trail (the trail **name** on AWS provider < v5, the trail **ARN** on AWS provider >= v5) |
| `cloudtrail_arn` | The Amazon Resource Name of the trail |
| `cloudtrail_home_region` | The region in which the trail was created |

## Best Practices

### Bucket and Encryption

1. **Provision the Bucket via the Companion Module**: Use `cloudposse/cloudtrail-s3-bucket/aws` (or an equivalent bucket + policy) before this module — `s3_bucket_name` is a required input, not a resource this module creates, and CloudTrail cannot deliver logs without the correct bucket policy attached.
2. **Encrypt Delivered Logs**: Set `kms_key_arn` to a customer-managed key whose key policy already grants the CloudTrail service principal `kms:GenerateDataKey*`/`kms:Decrypt` — the ARN alone does not grant CloudTrail access if the key policy is missing that statement.
3. **Enable Log File Validation**: Leave `enable_log_file_validation = true` (the default) so tampering with delivered log files is cryptographically detectable.

### Trail Scope

1. **Prefer an Organization Trail for New Estates**: Set `is_organization_trail = true` in the management (or a delegated administrator) account so every current and future member account is covered automatically, instead of deploying one trail per account.
2. **Default to Multi-Region**: Leave `is_multi_region_trail = true` unless there is a specific reason to scope the trail to a single region — a single-region trail misses API activity in every other region.
3. **Enable Global Service Events Once**: Turn on `include_global_service_events` in exactly one trail per account/organization scope to avoid recording IAM and other global events redundantly.

### Data Events and Insights

1. **Add Data Events Deliberately**: `event_selector`/`advanced_event_selector` data-event logging (S3 object-level, Lambda, DynamoDB) is high-volume and billed per event — scope it to the specific buckets/functions that need it rather than logging all data events account-wide.
2. **Prefer `advanced_event_selector` for New Trails**: It is the more flexible, field-based mechanism; do not configure both `event_selector` and `advanced_event_selector` on the same trail.
3. **Turn On Insights for Anomaly Detection**: Add `insight_selector` entries (`ApiCallRateInsight`/`ApiErrorRateInsight`) to catch unusual API call volume or error-rate patterns that a fixed rule would miss.

### Monitoring and Notifications

1. **Stream to CloudWatch Logs for Near-Real-Time Alerting**: Set `cloud_watch_logs_group_arn`/`cloud_watch_logs_role_arn` and drive metric filters/alarms off specific API calls (e.g. root login, security group changes) — the S3 archive alone is not near-real-time.
2. **Wire SNS for Delivery Automation**: Set `sns_topic_name` when downstream automation (SIEM ingestion, a Lambda processor) needs to react the moment a new log file lands.
3. **Pin the Module Version**: Use an explicit `version = "0.24.0"` — Cloud Posse's own README usage snippet intentionally omits a version pin, so do not copy it verbatim into production code.

## Additional Resources

- **Module Repository**: https://github.com/cloudposse/terraform-aws-cloudtrail
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/cloudtrail/aws/latest
- **Module Examples**: https://github.com/cloudposse/terraform-aws-cloudtrail/tree/main/examples/complete
- **Companion Bucket Module**: https://registry.terraform.io/modules/cloudposse/cloudtrail-s3-bucket/aws/latest
- **Related — CloudWatch Alarms for CloudTrail**: https://github.com/cloudposse/terraform-aws-cloudtrail-cloudwatch-alarms
- **AWS CloudTrail User Guide**: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html
- **CloudTrail Data Events vs Management Events**: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-management-and-data-events-with-cloudtrail.html
- **CloudTrail Insights**: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-insights.html
- **aws_cloudtrail Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudtrail
- **AWS CloudTrail Pricing**: https://aws.amazon.com/cloudtrail/pricing/

## Important Gotchas

- **The Bucket Is Not Created Here**: `s3_bucket_name` is a required input pointing at an already-existing bucket. CloudTrail additionally needs a specific bucket policy (allowing `s3:GetBucketAcl` and scoped `s3:PutObject` for the `cloudtrail.amazonaws.com` service principal) before it can deliver logs — Cloud Posse ships `cloudposse/cloudtrail-s3-bucket/aws` specifically to create the bucket with that policy already attached; hand-rolling the bucket without the matching policy is a common apply-succeeds-but-no-logs-arrive failure mode.
- **KMS Key Policy Is Separate from `kms_key_arn`**: Setting `kms_key_arn` tells CloudTrail which key to use, but the key's own resource policy must independently grant the CloudTrail service principal `kms:GenerateDataKey*`/`kms:Decrypt` (and `kms:DescribeKey`) — an ARN pointing at a key whose policy does not grant CloudTrail access silently blocks log delivery.
- **`cloudtrail_id` Changes Meaning by AWS Provider Major Version**: The output is the trail's **name** on `hashicorp/aws` provider < v5 and the trail's **ARN** on provider >= v5 — code consuming this output across a provider upgrade needs to account for the format change, not just the value.
- **`event_selector` and `advanced_event_selector` Are Not Meant to Be Combined**: Both configure the same underlying data-event-selector API differently; setting both on one trail produces conflicting/oscillating plan diffs. Pick one — `advanced_event_selector` for new trails.
- **`is_organization_trail` Requires Org-Level Standing**: It must be applied from the AWS Organizations management account or a delegated CloudTrail administrator account, and AWS Organizations trusted access for CloudTrail must already be enabled — applying it from an ordinary member account fails.
- **Data Events Are Priced and Volumed Differently from Management Events**: Turning on `event_selector`/`advanced_event_selector` for, e.g., all S3 objects in an account can produce a very large, continuously billed event volume — scope `data_resource`/`field_selector` to the specific resources that need data-event coverage.
- **This Module Is Not the `config` Module**: It logs *what API calls happened* (the event history) — it does not evaluate resource configuration against compliance rules. For continuous compliance rule evaluation, see the separate `cloudposse/config/aws` module.

## Notes for AI Agents

This module is published by Cloud Posse (namespace `cloudposse`), not the `terraform-aws-modules` org. It uses Cloud Posse's `context`/`label` convention — inputs like `namespace`, `stage`, `name`, `environment`, `tenant`, `attributes`, `tags` and a `context` object drive resource naming/tagging across every Cloud Posse module. Do NOT propagate this convention onto other (differently-styled) modules in the same project; set the label inputs this module needs and leave other vendors' modules alone.

When using this module in automated workflows:

1. **The S3 Bucket Is Not Created Here**: `s3_bucket_name` is a required input — provision the bucket (and its CloudTrail-write bucket policy) separately, ideally with the companion `cloudposse/cloudtrail-s3-bucket/aws` module, before or alongside this module.
2. **Distinguish This Module From `config`**: This module is API-activity/event-history logging (management and data events) into an S3 bucket — it has no compliance-rule-evaluation feature. Resource-configuration compliance rules (AWS Config Managed/Custom Rules, CIS benchmarks) live in the separate `cloudposse/config/aws` module; do not describe this module using "compliance"/"audit-rules" framing that belongs there.
3. **KMS Encryption Needs a Key Policy, Not Just an ARN**: If `kms_key_arn` is set, verify the referenced key's policy grants the CloudTrail service principal the needed `kms:GenerateDataKey*`/`kms:Decrypt`/`kms:DescribeKey` permissions — this module does not manage the KMS key or its policy.
4. **`cloudtrail_id` Is Provider-Version-Dependent**: It resolves to the trail name on `hashicorp/aws` < v5 and to the trail ARN on >= v5; do not assume a fixed format when wiring this output into other resources.
5. **`event_selector` vs `advanced_event_selector`**: Configure at most one of these two data-event mechanisms per trail; prefer `advanced_event_selector` for new configurations and verify the exact field shape via `grep_module_docs` or the registry type before writing entries, since both are nested `list(object({...}))` types easy to get wrong from memory.
6. **`is_organization_trail` Is Account-Scoped**: Only apply it with `true` from the AWS Organizations management account or a delegated CloudTrail administrator account with trusted access already enabled.
7. **Pin the Module Version**: Use an explicit `version = "0.24.0"` constraint for reproducible deployments; Cloud Posse's own usage examples intentionally omit a version pin, which is not a pattern to copy into real infrastructure.
8. **Verify Exact Variable Shapes via `grep_module_docs`**: Cloud Posse modules occasionally rename or add label inputs across minor versions — confirm `event_selector`/`advanced_event_selector`/`insight_selector` object fields against the pinned `0.24.0` docs before relying on memorized shapes.
