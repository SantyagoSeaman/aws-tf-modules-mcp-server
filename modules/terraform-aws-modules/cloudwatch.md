# Terraform AWS CloudWatch Module

## Module Information

- **Module Name**: `cloudwatch`
- **Module ID**: `terraform-aws-modules/cloudwatch/aws`
- **Source**: `terraform-aws-modules/cloudwatch/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-cloudwatch
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest
- **Latest Version**: 5.7.2
- **Purpose**: Collection of Terraform submodules that create and manage AWS CloudWatch resources (log groups, metric filters/alarms, composite alarms, metric streams, log subscription filters, data protection policies, anomaly detectors, CIS security alarms, and query definitions)
- **Service**: AWS CloudWatch (Monitoring, Logs and Observability)
- **Category**: Monitoring, Observability, Logging, Security
- **Keywords**: cloudwatch, monitoring, alarms, metrics, logs, log-group, metric-filter, composite-alarm, cis-benchmark, metric-stream, anomaly-detection, log-subscription-filter, kms-encryption, data-protection-policy
- **Use For**: application performance monitoring, infrastructure health tracking, log aggregation and analysis, security event detection (CIS benchmarks), compliance/PII log redaction, automated incident response via SNS/Lambda, real-time alerting, anomaly detection, hybrid-cloud metric export (Datadog/Splunk/New Relic), standardized Logs Insights queries

## Description

This module has **no resources at its root** — it is a curated collection of 13 independent, single-purpose submodules under `modules/`, each wrapping one CloudWatch resource type. There is nothing to gain from calling `terraform-aws-modules/cloudwatch/aws` directly; every usage must reference a specific submodule via `source = "terraform-aws-modules/cloudwatch/aws//modules/<submodule-name>"`. This design lets you pull in only the pieces you need (e.g. just `log-group`, or `log-group` + `metric-alarm` + `log-metric-filter` together) without unused resource definitions cluttering your state.

The submodules cover the full CloudWatch surface: log group/stream lifecycle management with KMS encryption and retention control, log metric filters that turn log patterns into custom metrics, metric alarms (single and composite) with SNS/Lambda actions, bulk alarm creation across multiple dimensions (e.g. one alarm per Lambda function), CIS AWS Foundations Benchmark security alarms pre-wired to CloudTrail logs, log data protection policies for PII masking/redaction, log subscription filters for streaming logs to Lambda/Kinesis/Firehose, metric streams for near-real-time export to third-party observability platforms, Logs Insights query definitions for reusable troubleshooting queries, account-wide log policies, and ML-based log anomaly detection.

Each submodule also ships a matching module under `wrappers/`, following the standard terraform-aws-modules wrapper pattern, so multiple instances can be created from a single module block using `for_each` over a map of configurations — useful when generating many similar alarms or log groups from a common variables file (e.g. with Terragrunt).

## Key Features

- **13 Independent Submodules**: No shared root resources; use only the submodules you need
- **Log Group Management**: Retention (1 day to indefinite), KMS encryption, STANDARD/INFREQUENT_ACCESS log classes, `skip_destroy` protection
- **Metric Alarms**: Full `aws_cloudwatch_metric_alarm` surface including metric math (`metric_query`), anomaly-detection thresholds, extended (percentile) statistics
- **Bulk Alarms by Dimension**: Generate many alarms (one per dimension-value set) from one config block via `metric-alarms-by-multiple-dimensions`
- **Composite Alarms**: Combine alarm states with AND/OR/NOT alarm-rule expressions plus an `actions_suppressor` to prevent notification storms
- **CIS Foundations Benchmark Alarms**: 15 pre-built CloudTrail-based security controls (unauthorized API calls, root usage, IAM/VPC/security-group changes, etc.), individually disable via `disabled_controls`
- **Log Data Protection Policies**: Auto-generate a masking/audit policy from `data_identifiers`, or supply a raw `policy_document`
- **Log Subscription Filters**: Stream logs in real time to Lambda, Kinesis, or Kinesis Firehose
- **Metric Streams**: Near-real-time export to Kinesis Firehose in `json`, `opentelemetry0.7`, or `opentelemetry1.0` format, with per-namespace include/exclude filters
- **Query Definitions**: Reusable, shareable CloudWatch Logs Insights queries across one or more log groups
- **Log Anomaly Detection**: ML-based baseline learning and anomaly scoring on log groups, no manual thresholds
- **Account Policies**: Apply data-protection or subscription-filter policies account-wide (`log-account-policy`)
- **Wrapper Modules**: Every submodule has a `wrappers/` counterpart for `for_each`-driven multi-instance creation

## Main Use Cases

1. **Application Performance Monitoring**: Track latency, error rates, and throughput via metric alarms and log metric filters
2. **Infrastructure Health Tracking**: Alarm on EC2/RDS/Lambda/ECS metrics with configurable thresholds and evaluation periods
3. **Security Event Detection**: Deploy `cis-alarms` against CloudTrail logs for unauthorized access, IAM/network changes, root usage
4. **Log Aggregation and Analysis**: Centralize logs into retention-managed, optionally KMS-encrypted log groups
5. **PII/Compliance Redaction**: Mask sensitive data in logs with `log-data-protection-policy` (GDPR/PCI-DSS/HIPAA workflows)
6. **Automated Incident Response**: Route ALARM/OK/INSUFFICIENT_DATA state transitions to SNS, PagerDuty, or Lambda for remediation
7. **Fleet-Wide Monitoring**: Create one alarm per resource (Lambda function, ASG instance, etc.) with `metric-alarms-by-multiple-dimensions`
8. **Hybrid Cloud Observability**: Stream CloudWatch metrics to Datadog/Splunk/New Relic via `metric-stream`
9. **Real-Time Log Processing**: Forward filtered logs to Lambda/Kinesis for SIEM ingestion or custom processing
10. **Standardized Troubleshooting**: Share common Logs Insights queries across teams with `query-definition`
11. **Anomaly Detection**: Surface unusual log patterns without manually tuned thresholds via `log-anomaly-detector`

## Submodules

### 1. log-group

- **Purpose**: Creates a CloudWatch log group
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-group
- **Key Features**: KMS encryption, configurable retention, STANDARD/INFREQUENT_ACCESS log class, `skip_destroy`
- **Use Cases**: Application logging, AWS service logs, audit trails

### 2. log-stream

- **Purpose**: Creates a log stream within an existing CloudWatch log group
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-stream`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-stream
- **Key Features**: Simple stream creation, integrates with any existing log group
- **Use Cases**: Segregating logs by instance/container, per-component log streams

### 3. log-metric-filter

- **Purpose**: Extracts a custom CloudWatch metric from log events matching a filter pattern
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-metric-filter`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-metric-filter
- **Key Features**: Pattern-based extraction, custom metric value/unit, default value for non-matches, dimensions
- **Use Cases**: Error-rate tracking, log-derived business metrics, alertable log patterns

### 4. metric-alarm

- **Purpose**: Creates a single CloudWatch metric alarm
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/metric-alarm`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/metric-alarm
- **Key Features**: Comparison operators, metric math (`metric_query`), extended statistics, anomaly-detection bands
- **Use Cases**: CPU/latency/error alarms, threshold-based alerting

### 5. metric-alarms-by-multiple-dimensions

- **Purpose**: Creates one alarm per entry in a map of dimension sets, sharing all other settings
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/metric-alarms-by-multiple-dimensions`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/metric-alarms-by-multiple-dimensions
- **Key Features**: Bulk alarm creation, per-alarm name suffix/delimiter, consistent configuration
- **Use Cases**: Per-Lambda-function alarms, per-instance alarms, fleet monitoring

### 6. cis-alarms

- **Purpose**: Creates CIS AWS Foundations Benchmark log metric filters + alarms against a CloudTrail log group
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/cis-alarms`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/cis-alarms
- **Key Features**: 15 pre-built controls, selectively disable/override controls, random name prefix option
- **Use Cases**: Security compliance monitoring, unauthorized-access/root-usage detection

### 7. log-data-protection-policy

- **Purpose**: Attaches a data protection (PII masking/audit) policy to a log group
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-data-protection-policy`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-data-protection-policy
- **Key Features**: Auto-generated policy from `data_identifiers`, or raw `policy_document`, findings destinations (CW Logs/Firehose/S3)
- **Use Cases**: GDPR/PCI-DSS log redaction, sensitive-data masking

### 8. log-subscription-filter

- **Purpose**: Streams log events matching a filter pattern to another AWS service in real time
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-subscription-filter`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-subscription-filter
- **Key Features**: Lambda/Kinesis/Firehose destinations, filter patterns, distribution mode
- **Use Cases**: Real-time log processing, SIEM/log-forwarding pipelines

### 9. metric-stream

- **Purpose**: Continuously exports CloudWatch metrics to a Kinesis Firehose delivery stream
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/metric-stream`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/metric-stream
- **Key Features**: `json`/`opentelemetry0.7`/`opentelemetry1.0` formats, namespace include/exclude filters, extra statistics
- **Use Cases**: Third-party APM integration (Datadog, Splunk, New Relic), metric data lakes

### 10. query-definition

- **Purpose**: Saves a reusable CloudWatch Logs Insights query
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/query-definition`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/query-definition
- **Key Features**: Multi-log-group queries, shared across the console/team
- **Use Cases**: Standardized troubleshooting queries, common log-analysis patterns

### 11. composite-alarm

- **Purpose**: Combines multiple alarm states into one alarm via a logical `alarm_rule` expression
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/composite-alarm`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/composite-alarm
- **Key Features**: AND/OR/NOT alarm-rule logic, `actions_suppressor` to mute during maintenance
- **Use Cases**: Multi-signal alerting, service health checks, reduced alarm fatigue

### 12. log-account-policy

- **Purpose**: Creates an account-wide CloudWatch Logs policy (data protection or subscription filter)
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-account-policy`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-account-policy
- **Key Features**: `DATA_PROTECTION_POLICY` or `SUBSCRIPTION_FILTER_POLICY` scope `ALL`, same PII-masking options as `log-data-protection-policy`
- **Use Cases**: Organization-wide log compliance, centralized data protection

### 13. log-anomaly-detector

- **Purpose**: Creates a CloudWatch Logs anomaly detector using ML-based pattern baselining
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-anomaly-detector`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-anomaly-detector
- **Key Features**: Automatic baselining, configurable evaluation frequency, optional KMS encryption
- **Use Cases**: Proactive issue detection, unknown-unknowns discovery

---

## Submodule 1: log-group

### Description

Creates a CloudWatch log group. Serves as the target/parent for log streams, metric filters, subscription filters, data protection policies, and anomaly detectors.

### Key Features

- Customizable `name` or `name_prefix`
- Retention from 1 day up to 3653 days, or `0` for never-expire
- Optional KMS encryption via `kms_key_id`
- `STANDARD` or `INFREQUENT_ACCESS` log class for cost optimization
- `skip_destroy` to remove from state without deleting the log group/logs

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the log group |
| `name` | `string` | `null` | Name of the log group |
| `name_prefix` | `string` | `null` | Creates a unique name beginning with this prefix (conflicts with `name`) |
| `retention_in_days` | `number` | `null` | 0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, or 3653 (0 = never expire) |
| `kms_key_id` | `string` | `null` | ARN of KMS key used to encrypt log data |
| `log_group_class` | `string` | `null` | `STANDARD` or `INFREQUENT_ACCESS` |
| `skip_destroy` | `bool` | `null` | If `true`, remove from state instead of deleting on destroy |
| `tags` | `map(string)` | `{}` | Tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_log_group_name` | Name of the log group |
| `cloudwatch_log_group_arn` | ARN of the log group |

### Usage Example

```hcl
module "application_log_group" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-group"
  version = "~> 5.0"

  name              = "/aws/application/my-app"
  retention_in_days = 30
  kms_key_id        = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  log_group_class   = "STANDARD"

  tags = {
    Environment = "production"
    Application = "my-app"
  }
}

# Cost-optimized, protected archive log group
module "archive_log_group" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-group"
  version = "~> 5.0"

  name              = "/aws/archive/historical-logs"
  retention_in_days = 365
  log_group_class   = "INFREQUENT_ACCESS"
  skip_destroy      = true

  tags = {
    Environment = "production"
    Purpose     = "long-term-archive"
  }
}
```

## Submodule 2: log-stream

### Description

Creates an individual log stream within an existing CloudWatch log group, for logical segregation of log events by source (instance, container, invocation).

### Key Features

- Create a stream inside any existing log group
- Minimal configuration surface

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the log stream |
| `name` | `string` | `null` | Name of the log stream |
| `log_group_name` | `string` | `null` | Name of the log group to create the stream in |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_log_stream_name` | Name of the log stream |
| `cloudwatch_log_stream_arn` | ARN of the log stream |

### Usage Example

```hcl
module "application_log_stream" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-stream"
  version = "~> 5.0"

  name           = "app-server-instance-i-1234567890abcdef0"
  log_group_name = module.application_log_group.cloudwatch_log_group_name
}
```

## Submodule 3: log-metric-filter

### Description

Creates a CloudWatch Logs metric filter that scans log events for a pattern and publishes a derived numeric metric, enabling alarms on application-specific events that aren't natively exposed as CloudWatch metrics.

### Key Features

- Pattern-based metric extraction (`pattern`)
- Custom metric name/namespace/value/unit
- Optional per-metric `dimensions` via `metric_transformation_dimensions`
- Default value emission when the pattern does not match

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_cloudwatch_log_metric_filter` | `bool` | `true` | Whether to create the metric filter |
| `name` | `string` | *required* | Name of the metric filter |
| `pattern` | `string` | *required* | CloudWatch Logs filter pattern |
| `log_group_name` | `string` | *required* | Log group to attach the filter to |
| `metric_transformation_name` | `string` | *required* | Destination metric name |
| `metric_transformation_namespace` | `string` | *required* | Destination metric namespace |
| `metric_transformation_value` | `string` | `"1"` | Value published per matching event |
| `metric_transformation_default_value` | `string` | `null` | Value emitted when the pattern does not match |
| `metric_transformation_unit` | `string` | `null` | Metric unit (defaults to `None` if omitted) |
| `metric_transformation_dimensions` | `map(string)` | `{}` | Additional metric dimensions, e.g. `{ name = "$.value" }` |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_log_metric_filter_id` | Name of the metric filter |

### Usage Example

```hcl
module "error_metric_filter" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-metric-filter"
  version = "~> 5.0"

  log_group_name = "/aws/lambda/my-function"
  name           = "error-count"
  pattern        = "[ERROR]"

  metric_transformation_name      = "ErrorCount"
  metric_transformation_namespace = "MyApplication"
  metric_transformation_value     = "1"
  metric_transformation_unit      = "Count"
}
```

## Submodule 4: metric-alarm

### Description

Creates a single CloudWatch metric alarm that monitors a metric (or a metric-math expression) and triggers actions when the value breaches a threshold.

### Key Features

- Standard comparison operators (`GreaterThanThreshold`, `LessThanOrEqualToThreshold`, etc.)
- Metric math via `metric_query` (conflicts with `metric_name`/`namespace`/`period`/`statistic`)
- Extended (percentile) statistics via `extended_statistic`
- Anomaly-detection alarms via `threshold_metric_id`
- Separate action lists per alarm state (`alarm_actions`, `ok_actions`, `insufficient_data_actions`)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_metric_alarm` | `bool` | `true` | Whether to create the alarm |
| `alarm_name` | `string` | *required* | Unique, descriptive alarm name |
| `comparison_operator` | `string` | *required* | `GreaterThanOrEqualToThreshold`, `GreaterThanThreshold`, `LessThanThreshold`, `LessThanOrEqualToThreshold` |
| `evaluation_periods` | `number` | *required* | Number of periods to evaluate |
| `threshold` | `number` | `null` | Value compared against the statistic |
| `metric_name` | `string` | `null` | Metric name (conflicts with `metric_query`) |
| `namespace` | `string` | `null` | Metric namespace |
| `period` | `string` | `null` | Period (seconds) over which the statistic applies |
| `statistic` | `string` | `null` | `SampleCount`, `Average`, `Sum`, `Minimum`, `Maximum` |
| `dimensions` | `any` | `null` | Metric dimensions |
| `alarm_description` | `string` | `null` | Description shown in the console |
| `alarm_actions` | `list(string)` | `null` | ARNs notified on transition to `ALARM` |
| `ok_actions` | `list(string)` | `null` | ARNs notified on transition to `OK` |
| `insufficient_data_actions` | `list(string)` | `null` | ARNs notified on transition to `INSUFFICIENT_DATA` |
| `treat_missing_data` | `string` | `"missing"` | `missing`, `notBreaching`, `breaching`, `ignore` |
| `datapoints_to_alarm` | `number` | `null` | Breaching datapoints required to trigger |
| `metric_query` | `any` | `[]` | List of metric-math expressions (up to 20) |
| `tags` | `map(string)` | `{}` | Tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_metric_alarm_arn` | ARN of the metric alarm |
| `cloudwatch_metric_alarm_id` | ID of the metric alarm |

### Usage Examples

#### Example 1: CPU Utilization Alarm

```hcl
module "cpu_alarm" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/metric-alarm"
  version = "~> 5.0"

  alarm_name          = "high-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 80

  metric_name = "CPUUtilization"
  namespace   = "AWS/EC2"
  period      = 300
  statistic   = "Average"

  dimensions = {
    InstanceId = "i-1234567890abcdef0"
  }

  alarm_description = "This metric monitors EC2 CPU utilization"
  alarm_actions      = [aws_sns_topic.alerts.arn]
  ok_actions         = [aws_sns_topic.alerts.arn]

  tags = {
    Environment = "production"
  }
}
```

#### Example 2: Lambda Error Rate Alarm

```hcl
module "lambda_error_alarm" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/metric-alarm"
  version = "~> 5.0"

  alarm_name          = "lambda-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  threshold           = 5
  datapoints_to_alarm = 1

  metric_name = "Errors"
  namespace   = "AWS/Lambda"
  period      = 60
  statistic   = "Sum"

  dimensions = {
    FunctionName = "my-critical-function"
  }

  alarm_description  = "Alert when the Lambda function has more than 5 errors per minute"
  alarm_actions      = [aws_sns_topic.critical_alerts.arn]
  treat_missing_data = "notBreaching"

  tags = {
    Environment = "production"
    Team        = "backend"
  }
}
```

## Submodule 5: metric-alarms-by-multiple-dimensions

### Description

Creates one `aws_cloudwatch_metric_alarm` per entry of the `dimensions` map, sharing all other alarm settings — ideal for fleets of similar resources (Lambda functions, ASG instances, ECS services) that need identical alarm logic with different dimension values.

### Key Features

- One alarm per key in `dimensions`; alarm name = `alarm_name + alarm_name_delimiter + key`
- Shares comparison operator, threshold, period, statistic across all generated alarms
- Same metric-math (`metric_query`) support as `metric-alarm`

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_metric_alarm` | `bool` | `true` | Whether to create the alarms |
| `alarm_name` | `string` | *required* | Base name; combined with `alarm_name_delimiter` and each dimension-map key |
| `alarm_name_delimiter` | `string` | `""` | Delimiter between `alarm_name` and the dimension-map key |
| `comparison_operator` | `string` | *required* | Comparison operator for all alarms |
| `evaluation_periods` | `number` | *required* | Evaluation periods for all alarms |
| `threshold` | `number` | *required* | Threshold for all alarms |
| `metric_name` | `string` | `null` | Metric name for all alarms |
| `namespace` | `string` | `null` | Namespace for all alarms |
| `period` | `string` | `null` | Period for all alarms |
| `statistic` | `string` | `null` | Statistic for all alarms |
| `dimensions` | `any` | `{}` | Map of `alarm-key => { DimensionName = "value", ... }`, one alarm per key |
| `alarm_actions` | `list(string)` | `null` | Alarm actions shared by all generated alarms |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_metric_alarm_arns` | Map of dimension-key to alarm ARN |
| `cloudwatch_metric_alarm_ids` | Map of dimension-key to alarm ID |

### Usage Example

```hcl
module "lambda_duration_alarms" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/metric-alarms-by-multiple-dimensions"
  version = "~> 5.0"

  alarm_name            = "lambda-duration-"
  alarm_description     = "Lambda duration is too high"
  comparison_operator   = "GreaterThanOrEqualToThreshold"
  evaluation_periods    = 1
  threshold             = 5000
  period                = 60
  statistic             = "Maximum"
  unit                  = "Milliseconds"

  namespace   = "AWS/Lambda"
  metric_name = "Duration"

  # Creates two alarms: "lambda-duration-lambda1" and "lambda-duration-lambda2"
  dimensions = {
    lambda1 = { FunctionName = "index" }
    lambda2 = { FunctionName = "signup" }
  }

  alarm_actions = [aws_sns_topic.lambda_alerts.arn]
}
```

## Submodule 6: cis-alarms

### Description

Creates CloudWatch Logs metric filters + metric alarms for the AWS CIS Foundations Benchmark controls, driven by a CloudTrail log group. Ships 15 pre-built controls; any subset can be disabled or overridden.

### Key Features

- 15 built-in controls (see table below), each a metric filter + alarm pair
- `disabled_controls` to skip specific controls by ID
- `control_overrides` to customize pattern/description per control
- Optional random name-prefix (`use_random_name_prefix`) to avoid collisions across regions/accounts

### Built-in Control IDs

`UnauthorizedAPICalls`, `NoMFAConsoleSignin`, `RootUsage`, `IAMChanges`, `CloudTrailCfgChanges`, `ConsoleSigninFailures`, `DisableOrDeleteCMK`, `S3BucketPolicyChanges`, `AWSConfigChanges`, `SecurityGroupChanges`, `NACLChanges`, `NetworkGWChanges`, `RouteTableChanges`, `VPCChanges`, `AWSOrganizationsChanges`

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the CIS alarms |
| `log_group_name` | `string` | `""` | CloudTrail log group name to monitor |
| `alarm_actions` | `list(string)` | `[]` | ARNs notified when alarms trigger |
| `ok_actions` | `list(string)` | `[]` | ARNs notified on OK transition |
| `insufficient_data_actions` | `list(string)` | `[]` | ARNs notified on INSUFFICIENT_DATA transition |
| `namespace` | `string` | `"CISBenchmark"` | CloudWatch namespace used for the generated metrics |
| `disabled_controls` | `list(string)` | `[]` | Control IDs to skip (see list above) |
| `control_overrides` | `any` | `{}` | Per-control overrides, keyed by control ID |
| `use_random_name_prefix` | `bool` | `false` | Prefix resource names with a random pet name |
| `name_prefix` | `string` | `""` | Static name prefix (ignored if `use_random_name_prefix = true`) |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_metric_alarm_arns` | Map of control ID to alarm ARN |
| `cloudwatch_metric_alarm_ids` | Map of control ID to alarm ID |

### Usage Example

```hcl
resource "aws_sns_topic" "cis_alerts" {
  name = "cis-security-alerts"
}

module "cis_alarms" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/cis-alarms"
  version = "~> 5.0"

  log_group_name = "aws-cloudtrail-logs"
  alarm_actions  = [aws_sns_topic.cis_alerts.arn]

  # Optionally skip controls that don't apply
  disabled_controls = [
    "AWSOrganizationsChanges",
  ]

  tags = {
    Environment = "production"
    Compliance  = "CIS"
  }
}
```

## Submodule 7: log-data-protection-policy

### Description

Attaches an `aws_cloudwatch_log_data_protection_policy` to a log group, either generated from a simple `data_identifiers` list (audit + redact statements) or supplied directly as a JSON `policy_document`.

### Key Features

- `create_log_data_protection_policy = true` auto-builds an audit + de-identify (mask) policy from `data_identifiers`
- Or set `create_log_data_protection_policy = false` (default) and pass a raw `policy_document` JSON string
- Configurable findings destination: CloudWatch Logs, Kinesis Firehose, or S3

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the policy resource |
| `log_group_name` | `string` | `null` | Log group to attach the policy to |
| `create_log_data_protection_policy` | `bool` | `false` | Build the policy document from `data_identifiers` instead of `policy_document` |
| `policy_document` | `string` | `null` | Raw JSON data protection policy (used when `create_log_data_protection_policy = false`) |
| `data_identifiers` | `list(string)` | `null` | Managed data identifier ARNs to mask (e.g. `arn:aws:dataprotection::aws:data-identifier/EmailAddress`) |
| `log_data_protection_policy_name` | `string` | `null` | Name of the generated policy document |
| `findings_destination_cloudwatch_log_group` | `string` | `null` | Log group to receive audit findings |
| `findings_destination_firehose_delivery_stream` | `string` | `null` | Firehose stream to receive audit findings |
| `findings_destination_s3_bucket` | `string` | `null` | S3 bucket to receive audit findings |

### Main Outputs

| Output | Description |
|--------|-------------|
| `log_group_name` | Name of the log group the policy was attached to |

### Usage Example

```hcl
module "log_data_protection" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-data-protection-policy"
  version = "~> 5.0"

  log_group_name = "/aws/application/payment-processor"

  create_log_data_protection_policy = true
  log_data_protection_policy_name   = "RedactPII"

  data_identifiers = [
    "arn:aws:dataprotection::aws:data-identifier/EmailAddress",
    "arn:aws:dataprotection::aws:data-identifier/CreditCardNumber",
  ]

  findings_destination_cloudwatch_log_group = "audit-log-group"
}
```

## Submodule 8: log-subscription-filter

### Description

Creates a CloudWatch Logs subscription filter that streams matching log events in real time to Lambda, Kinesis Data Streams, or Kinesis Data Firehose.

### Key Features

- Lambda, Kinesis, or Firehose destinations via `destination_arn`
- Filter pattern to stream only relevant events (empty pattern streams everything)
- `distribution` (`ByLogStream` or `Random`) for Kinesis/Firehose fan-out

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the subscription filter |
| `name` | `string` | `null` | Name of the subscription filter |
| `log_group_name` | `string` | `null` | Log group to subscribe to |
| `filter_pattern` | `string` | `""` | Filter pattern (empty string matches everything) |
| `destination_arn` | `string` | `null` | ARN of the destination (Lambda/Kinesis/Firehose) |
| `role_arn` | `string` | `null` | IAM role ARN required for Kinesis/Firehose destinations |
| `distribution` | `string` | `null` | `ByLogStream` or `Random` |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_log_subscription_filter_name` | Name of the subscription filter |

### Usage Example

```hcl
module "firehose_log_subscription" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-subscription-filter"
  version = "~> 5.0"

  name            = "all-logs-to-s3"
  log_group_name  = "/aws/application/api"
  filter_pattern  = ""  # empty pattern streams all logs
  destination_arn = aws_kinesis_firehose_delivery_stream.logs.arn
  role_arn        = aws_iam_role.log_subscription_role.arn
}
```

## Submodule 9: metric-stream

### Description

Creates a CloudWatch Metric Stream that continuously exports metrics to a Kinesis Firehose delivery stream for near-real-time delivery to third-party observability platforms.

### Key Features

- Output formats: `json`, `opentelemetry0.7`, `opentelemetry1.0`
- `include_filter` (send only listed namespaces/metrics) or `exclude_filter` (send everything except listed) — mutually exclusive
- `statistics_configuration` to stream additional statistics (e.g. `p99`) for selected metrics

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the metric stream |
| `name` | `string` | `null` | Name of the metric stream (conflicts with `name_prefix`) |
| `name_prefix` | `string` | `null` | Name prefix (conflicts with `name`) |
| `firehose_arn` | `string` | *required* | ARN of the Kinesis Firehose delivery stream |
| `role_arn` | `string` | *required* | IAM role ARN CloudWatch assumes to write to Firehose |
| `output_format` | `string` | *required* | `json`, `opentelemetry0.7`, or `opentelemetry1.0` |
| `include_filter` | `any` | `{}` | Map of `key => { namespace = "...", metric_names = [...] }` to include |
| `exclude_filter` | `any` | `{}` | Same shape as `include_filter`, but for exclusion |
| `statistics_configuration` | `any` | `[]` | List of `{ additional_statistics = [...], include_metric = [...] }` |
| `tags` | `map(string)` | `{}` | Tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_metric_stream` | ARN of the metric stream |
| `cloudwatch_metric_stream_state` | State of the metric stream (`running`/`stopped`) |
| `cloudwatch_metric_stream_creation_date` | Creation timestamp (RFC3339) |
| `cloudwatch_metric_stream_last_update_date` | Last update timestamp (RFC3339) |

### Usage Example

```hcl
module "datadog_metric_stream" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/metric-stream"
  version = "~> 5.0"

  name          = "datadog-metrics"
  firehose_arn  = aws_kinesis_firehose_delivery_stream.datadog.arn
  role_arn      = aws_iam_role.metric_stream.arn
  output_format = "opentelemetry0.7"

  # Include only specific namespaces/metrics to control cost
  include_filter = {
    ec2 = {
      namespace    = "AWS/EC2"
      metric_names = ["CPUUtilization", "NetworkIn"]
    }
    rds = {
      namespace = "AWS/RDS"
    }
  }

  tags = {
    Environment = "production"
    Destination = "datadog"
  }
}
```

## Submodule 10: query-definition

### Description

Creates a reusable CloudWatch Logs Insights query definition, savable and shareable across the console/team.

### Key Features

- Query multiple log groups at once via `log_group_names`
- Standardizes common troubleshooting queries

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the query definition |
| `name` | `string` | *required* | Name of the query |
| `query_string` | `string` | *required* | CloudWatch Logs Insights query string |
| `log_group_names` | `list(string)` | `null` | Log groups to associate the query with |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_query_definition_id` | ID of the query definition |

### Usage Example

```hcl
module "error_query" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/query-definition"
  version = "~> 5.0"

  name            = "Find-Application-Errors"
  log_group_names = ["/aws/application/api", "/aws/application/worker"]

  query_string = <<-EOQ
    fields @timestamp, @message, @logStream
    | filter @message like /ERROR/
    | sort @timestamp desc
    | limit 100
  EOQ
}
```

## Submodule 11: composite-alarm

### Description

Creates a CloudWatch composite alarm that combines the state of multiple existing alarms via an `alarm_rule` expression (`ALARM(...)`, `OK(...)`, `INSUFFICIENT_DATA(...)` combined with `AND`/`OR`/`NOT`).

### Key Features

- Logical combination of alarm states, reducing false positives/alarm fatigue
- `actions_suppressor` to mute notifications while a maintenance/suppressor alarm is active
- Separate action lists per alarm state

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the composite alarm |
| `alarm_name` | `string` | `null` | Name of the composite alarm (must be unique in the region) |
| `alarm_description` | `string` | `null` | Description of the composite alarm |
| `alarm_rule` | `string` | `null` | Expression combining other alarms' states (max 10240 chars) |
| `actions_enabled` | `bool` | `true` | Whether actions execute on state changes |
| `alarm_actions` | `list(string)` | `null` | Actions on transition to ALARM (max 5) |
| `ok_actions` | `list(string)` | `null` | Actions on transition to OK (max 5) |
| `insufficient_data_actions` | `list(string)` | `null` | Actions on transition to INSUFFICIENT_DATA (max 5) |
| `actions_suppressor` | `map(any)` | `{}` | `{ alarm = "...", extension_period = <secs>, wait_period = <secs> }` |
| `tags` | `map(string)` | `{}` | Tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_composite_alarm_arn` | ARN of the composite alarm |
| `cloudwatch_composite_alarm_id` | ID of the composite alarm |

### Usage Example

```hcl
module "composite_alarm" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/composite-alarm"
  version = "~> 5.0"

  alarm_name        = "critical-resource-pressure"
  alarm_description = "Both CPU and memory are critically high"

  alarm_rule = join(" AND ", [
    "ALARM(${module.cpu_alarm.cloudwatch_metric_alarm_id})",
    "ALARM(${module.memory_alarm.cloudwatch_metric_alarm_id})",
  ])

  alarm_actions = [aws_sns_topic.critical_alerts.arn]
  ok_actions    = [aws_sns_topic.critical_alerts.arn]

  # Suppress notifications while a maintenance-window alarm is active
  actions_suppressor = {
    alarm            = module.maintenance_window_alarm.cloudwatch_metric_alarm_id
    extension_period = 20
    wait_period      = 10
  }

  tags = {
    Environment = "production"
    Severity    = "critical"
  }
}
```

## Submodule 12: log-account-policy

### Description

Creates an account-wide CloudWatch Logs policy (`DATA_PROTECTION_POLICY` or `SUBSCRIPTION_FILTER_POLICY`), applying governance rules across log groups without editing each one individually. Shares the same policy-generation options as `log-data-protection-policy`.

### Key Features

- Account-scoped enforcement (`log_account_policy_scope = "ALL"` is currently the only accepted value)
- Auto-generated data protection policy from `data_identifiers`, or a raw `policy_document`
- One account policy per `log_account_policy_type` per account

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the account policy |
| `log_account_policy_name` | `string` | `null` | Name of the account policy |
| `log_account_policy_type` | `string` | `"audit-policy"` | `DATA_PROTECTION_POLICY` or `SUBSCRIPTION_FILTER_POLICY` — set explicitly, the module default is not a valid AWS value |
| `log_account_policy_scope` | `string` | `null` | Only `ALL` is currently accepted |
| `log_account_policy_selection_criteria` | `string` | `null` | Criteria for subscription-filter policies (e.g. `LogGroupName NOT IN [...]`) |
| `create_log_data_protection_policy` | `bool` | `false` | Build the policy document from `data_identifiers` instead of `policy_document` |
| `policy_document` | `string` | `null` | Raw JSON policy (used when `create_log_data_protection_policy = false`) |
| `data_identifiers` | `list(string)` | `null` | Managed data identifier ARNs to mask |
| `findings_destination_cloudwatch_log_group` | `string` | `null` | Log group to receive audit findings |

### Main Outputs

| Output | Description |
|--------|-------------|
| `log_account_policy_name` | Name of the account policy |

### Usage Example

```hcl
module "account_data_protection" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-account-policy"
  version = "~> 5.0"

  log_account_policy_name = "account-wide-pii-protection"
  log_account_policy_type = "DATA_PROTECTION_POLICY"
  log_account_policy_scope = "ALL"

  create_log_data_protection_policy = true
  log_data_protection_policy_name   = "Account-PII-Protection"

  data_identifiers = [
    "arn:aws:dataprotection::aws:data-identifier/EmailAddress",
    "arn:aws:dataprotection::aws:data-identifier/SSN",
  ]

  findings_destination_cloudwatch_log_group = "my-cloudwatch-audit-log-group"
}
```

## Submodule 13: log-anomaly-detector

### Description

Creates a CloudWatch Logs anomaly detector that uses machine learning to baseline normal log behavior and score deviations, without manually defined thresholds.

### Key Features

- Automatic baseline learning and anomaly scoring
- Configurable evaluation frequency and anomaly-visibility window
- Optional `filter_pattern` to scope detection to a subset of log events
- Optional KMS encryption of the detector's model/findings

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the anomaly detector |
| `detector_name` | `string` | `null` | Name of the anomaly detector |
| `log_group_arns` | `list(string)` | `null` | ARNs of log group(s) to watch (currently only one is supported by the API) |
| `evaluation_frequency` | `string` | `null` | `ONE_MIN`, `FIVE_MIN`, `TEN_MIN`, `FIFTEEN_MIN`, `THIRTY_MIN`, `ONE_HOUR` |
| `anomaly_visibility_time` | `number` | `null` | Days an anomaly stays visible before being re-baselined (7–90) |
| `filter_pattern` | `string` | `null` | Restrict detection to log events matching this pattern |
| `kms_key_id` | `string` | `null` | KMS key to encrypt the detector's model and findings |
| `enabled` | `bool` | `null` | Whether the detector is enabled |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | ARN of the anomaly detector |

### Usage Example

```hcl
module "application_anomaly_detector" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-anomaly-detector"
  version = "~> 5.0"

  detector_name        = "app-log-anomaly-detector"
  evaluation_frequency = "FIVE_MIN"

  log_group_arns = [
    aws_cloudwatch_log_group.application.arn,
  ]

  filter_pattern = "[ERROR]"
  enabled        = true
}
```

## Best Practices

### Monitoring and Alerting

1. **Layer Your Monitoring**: Combine metric alarms, log metric filters, and composite alarms so a single failure mode is caught by more than one signal.
2. **Use Composite Alarms for Correlated Conditions**: Reduce false positives by requiring multiple signals (e.g. high CPU AND high memory) before paging someone.
3. **Configure All Three Alarm States**: Wire `ok_actions` and `insufficient_data_actions`, not just `alarm_actions`, to detect monitoring gaps and recoveries.
4. **Tune Evaluation Periods Deliberately**: Balance `evaluation_periods`/`datapoints_to_alarm` against `period` to avoid alerting on transient spikes.
5. **Prefer Metric Math for Derived Metrics**: Use `metric_query` for ratios/percentages rather than post-processing alarm data downstream.

### Log Management

1. **Set Retention by Log Type**: Short retention for debug logs, longer for application/audit logs — `retention_in_days` directly drives storage cost.
2. **Use `INFREQUENT_ACCESS` for Rarely Queried Logs**: Cuts storage cost for logs kept mainly for compliance, not active querying.
3. **Encrypt Sensitive Log Groups**: Set `kms_key_id` on any log group that may contain sensitive data.
4. **Protect Audit Trails from Accidental Deletion**: Use `skip_destroy = true` on log groups backing compliance/forensic requirements.
5. **Mask PII at the Source**: Attach `log-data-protection-policy` to any log group that could receive PII, credit card numbers, or secrets.

### Security and Compliance

1. **Deploy `cis-alarms` on CloudTrail Logs**: Gives baseline detection of unauthorized API calls, root usage, and IAM/network/security-group changes with minimal setup.
2. **Route Security Alarms to Multiple Channels**: Fan out `alarm_actions` to SNS topics feeding email, Slack, and incident-management tooling.
3. **Prefer `data_identifiers` Over Hand-Written Policies**: Managed data identifiers (`log-data-protection-policy`/`log-account-policy`) are less error-prone than a hand-authored `policy_document`.
4. **Centralize with Account Policies**: Use `log-account-policy` when the same data-protection or subscription-filter policy should apply account-wide instead of per log group.

### Cost Optimization

1. **Right-Size Retention**: Periodically re-review `retention_in_days`; it's a leading driver of CloudWatch Logs cost.
2. **Filter Metric Streams Aggressively**: Use `include_filter` (not `exclude_filter`) to send only the namespaces/metrics you actually consume downstream — Firehose ingestion is billed per record.
3. **Extract Once, Reuse Often**: Turn a repeated Logs Insights query pattern into a `log-metric-filter` instead of re-querying with Insights on demand.
4. **Audit Unused Alarms**: Alarms that never fire or reference deleted resources still cost money and add noise — remove them.

### Operational Excellence

1. **Reference Submodules Directly**: Never call the root `terraform-aws-modules/cloudwatch/aws` module — it has no resources; always target `//modules/<name>`.
2. **Pin the Module Version**: Use `version = "~> 5.0"` (or tighter) on every submodule call to avoid unannounced breaking changes.
3. **Chain Log Groups Before Dependents**: Create the `log-group` first, then reference its `cloudwatch_log_group_name`/`arn` output from `log-metric-filter`, `log-subscription-filter`, `log-data-protection-policy`, and `log-anomaly-detector`.
4. **Use `metric-alarms-by-multiple-dimensions` for Fleets**: Avoid `count`/`for_each` boilerplate around the single-alarm submodule when monitoring many similar resources.
5. **Use `wrappers/<submodule>` for Config-Driven Deployments**: When alarms/log groups are generated from a YAML/Terragrunt config map, the wrapper modules provide a ready-made `for_each` interface.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-cloudwatch
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-cloudwatch/tree/master/examples
- **AWS CloudWatch Documentation**: https://docs.aws.amazon.com/cloudwatch/
- **CloudWatch Logs Documentation**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/
- **CloudWatch Logs Insights Query Syntax**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html
- **CloudWatch Metric Streams**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Metric-Streams.html
- **CloudWatch Logs Anomaly Detection**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/LogsAnomalyDetection.html
- **CloudWatch Log Data Protection**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/mask-sensitive-log-data.html
- **CloudWatch Composite Alarms**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Create_Composite_Alarm.html
- **CIS AWS Foundations Benchmark**: https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-cis-controls.html
- **CloudWatch Pricing**: https://aws.amazon.com/cloudwatch/pricing/

## Notes for AI Agents

When generating Terraform for this module:

1. **Always Target a Submodule**: The root module (`terraform-aws-modules/cloudwatch/aws`) creates nothing — every `source` must include `//modules/<submodule-name>`.
2. **Create Log Groups First**: `log-metric-filter`, `log-subscription-filter`, `log-data-protection-policy`, and `log-anomaly-detector` all need an existing log group name/ARN as input.
3. **Watch for Required Fields With No Default**: e.g. `metric-alarm.alarm_name`/`comparison_operator`/`evaluation_periods`, `metric-stream.firehose_arn`/`role_arn`/`output_format`, `query-definition.name`/`query_string`, `log-metric-filter.name`/`pattern`/`log_group_name`/`metric_transformation_name`/`metric_transformation_namespace` — Terraform will fail to plan if these are omitted.
4. **`create*` Flag Naming Is Inconsistent**: Most submodules use `create`, but `log-metric-filter` uses `create_cloudwatch_log_metric_filter` and `metric-alarm`/`metric-alarms-by-multiple-dimensions` use `create_metric_alarm` — copy the exact variable name for the submodule in use.
5. **`log-account-policy.log_account_policy_type` Has No Valid Default**: Its default (`"audit-policy"`) is not an accepted AWS value — always set it explicitly to `DATA_PROTECTION_POLICY` or `SUBSCRIPTION_FILTER_POLICY`.
6. **Use `metric-alarms-by-multiple-dimensions` for Multiple Similar Resources**: Pass a map to `dimensions` instead of looping the single-alarm submodule with `for_each`.
7. **Pick the Right Data-Protection Path**: Set `create_log_data_protection_policy = true` plus `data_identifiers` for the common PII-masking case; only fall back to a raw `policy_document` for custom policy logic.
8. **CIS Control IDs Are CamelCase Strings**: When populating `disabled_controls` in `cis-alarms`, use the exact IDs (e.g. `RootUsage`, `IAMChanges`) — see the built-in control list above.
9. **Pin Module Versions**: Always set `version = "~> 5.0"` (or narrower) on submodule blocks to avoid picking up breaking changes across major versions.
10. **Tag Consistently**: Most submodules expose `tags`; set `Environment`/`Team`/cost-allocation tags uniformly across log groups, alarms, and streams for traceability.
