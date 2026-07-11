# Terraform AWS Notify Slack Module

## Module Information

- **Module Name**: `notify-slack`
- **Source**: `terraform-aws-modules/notify-slack/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-notify-slack
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/notify-slack/aws/latest
- **Latest Version**: 7.5.1
- **Purpose**: Creates (or reuses) an SNS topic and a Lambda function that forwards AWS event notifications to a Slack channel via incoming webhooks
- **Service**: AWS SNS (Simple Notification Service), AWS Lambda
- **Category**: Monitoring, Alerting, Integration
- **Keywords**: slack, notifications, sns, lambda, cloudwatch-alarms, guardduty, webhook, chatops, kms-encryption, sns-topic, dead-letter-queue, vpc-lambda, aws-backup, serverless, incident-response
- **Use For**: CloudWatch alarm notifications, GuardDuty security/malware alerts, AWS Backup job status alerts, DMS/Glue job notifications, operational incident alerts, DevOps event notifications, ChatOps integration, multi-environment alerting, generic SNS-to-Slack relaying

## Description

The Terraform AWS Notify Slack module provisions an SNS topic (or subscribes to an existing one) and an AWS Lambda function (Python 3.13 runtime, built via the `terraform-aws-modules/lambda/aws` submodule) that relays AWS notifications to a Slack channel through an incoming webhook. It ships with built-in message parsers that recognize and pretty-print several AWS event payload shapes — CloudWatch Alarms, CloudWatch Logs Metric Alarms, GuardDuty Findings, GuardDuty Malware Protection Object Scan Results, AWS Backup job events, DMS notifications, and Glue job notifications — while falling back to a generic text message formatter for anything else. Because the Lambda subscribes to the SNS topic, any AWS service that can publish to SNS (CloudWatch Alarms, EventBridge rules, Backup, DMS, Glue, custom application code, etc.) can drive a Slack notification without further code.

The module manages the SNS topic, topic subscription, Lambda function, its CloudWatch Logs group, and the IAM role/policy needed for execution (including delivery-status feedback roles when SNS delivery logging is enabled). It supports both plaintext and KMS-encrypted webhook URLs, SNS topic server-side encryption, CloudWatch Logs encryption, custom SNS topic policies, and subscription filter policies (by message attributes or message body) to control which messages reach Lambda. For network-isolated environments, the Lambda function can be deployed into private VPC subnets with custom security groups.

Operationally, the module exposes knobs for dead-letter-queue routing of failed invocations, reserved concurrency, ephemeral storage size, x86_64/arm64 architecture selection, custom IAM role paths/boundaries/prefixes, and the ability to swap in fully custom Lambda source code via `lambda_source_path` instead of the bundled notifier. It is maintained by the `terraform-aws-modules` organization and is commonly paired with `terraform-aws-modules/cloudwatch` or native `aws_cloudwatch_metric_alarm` resources to build end-to-end alerting pipelines.

## Key Features

- **SNS Topic Management**: Create a new SNS topic or subscribe the Lambda to an existing one (`create_sns_topic = false`)
- **Multi-Format Event Parsing**: Built-in formatters for CloudWatch Alarms, CloudWatch Logs Metric Alarms, GuardDuty Findings, GuardDuty Malware Protection scan results, AWS Backup, DMS, and Glue notifications, plus a generic text fallback
- **Lambda Function**: Python 3.13 runtime with selectable `x86_64` or `arm64` architecture and configurable ephemeral storage
- **KMS Encryption**: Encrypt the Slack webhook URL, SNS topic (server-side), and CloudWatch Logs independently
- **VPC Deployment**: Run the Lambda in private subnets with custom security groups for network isolation
- **Dead Letter Queue**: Route failed invocations to an SNS topic or SQS queue (requires both `lambda_dead_letter_target_arn` and `lambda_attach_dead_letter_policy = true`)
- **SNS Filter Policies**: Filter which messages reach Lambda using `subscription_filter_policy` and `subscription_filter_policy_scope` (`MessageAttributes` or `MessageBody`)
- **Custom SNS Topic Policy**: Attach a fully custom SNS access policy via `sns_topic_policy`
- **Delivery Status Logging**: Sample and log SNS delivery success/failure via a dedicated IAM feedback role
- **Custom Lambda Code**: Override the bundled notifier entirely via `lambda_source_path`
- **IAM Customization**: Configure role name prefix, path, permissions boundary, or supply an existing role via `lambda_role`
- **Comprehensive Tagging**: Independent tag maps for the Lambda function, IAM role, SNS topic, and CloudWatch log group

## Main Use Cases

1. **CloudWatch Alarm Notifications**: Real-time Slack alerts when metrics cross alarm thresholds
2. **Security Alerts**: GuardDuty findings and malware scan results routed to a security channel
3. **Backup Monitoring**: AWS Backup job success/failure notifications
4. **Data Pipeline Alerts**: DMS replication and Glue job status notifications
5. **Multi-Environment Alerting**: Separate SNS topics/channels per dev/staging/prod environment
6. **Operational Monitoring**: Centralize infrastructure alerts for DevOps teams
7. **ChatOps Integration**: Route arbitrary AWS events (via EventBridge → SNS) to team channels
8. **Incident Response**: Enable rapid response through real-time Slack notifications

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `sns_topic_name` | `string` | *Required* | Name of the SNS topic to create, or the existing topic to subscribe to |
| `slack_webhook_url` | `string` | *Required* | Slack incoming webhook URL (plaintext or KMS ciphertext) |
| `slack_channel` | `string` | *Required* | Target Slack channel name |
| `slack_username` | `string` | *Required* | Display username for Slack messages |
| `create` | `bool` | `true` | Whether to create all resources |
| `create_sns_topic` | `bool` | `true` | Create a new SNS topic (`false` = subscribe to an existing topic) |
| `runtime` | `string` | `"python3.13"` | Lambda function runtime version |
| `architectures` | `list(string)` | `null` | Lambda instruction set: `["x86_64"]` or `["arm64"]` |
| `slack_emoji` | `string` | `":aws:"` | Custom emoji for Slack message avatar |
| `log_level` | `string` | `"INFO"` | Lambda logging level |
| `kms_key_arn` | `string` | `""` | KMS key ARN used to decrypt the Slack webhook URL |
| `sns_topic_kms_key_id` | `string` | `""` | KMS key ARN/ID for SNS topic server-side encryption |
| `cloudwatch_log_group_kms_key_id` | `string` | `null` | KMS key ARN for Lambda CloudWatch Logs encryption |
| `cloudwatch_log_group_retention_in_days` | `number` | `0` | Log retention in days (`0` = never expire) |
| `log_events` | `bool` | `false` | Log incoming SNS events for debugging |
| `lambda_function_name` | `string` | `"notify_slack"` | Lambda function name |
| `lambda_source_path` | `string` | `null` | Path to custom Lambda source, replacing the bundled notifier |
| `lambda_function_vpc_subnet_ids` | `list(string)` | `null` | VPC subnet IDs for Lambda (enables VPC attach) |
| `lambda_function_vpc_security_group_ids` | `list(string)` | `null` | VPC security group IDs for Lambda |
| `reserved_concurrent_executions` | `number` | `-1` | Reserved concurrency (`-1` = unlimited, `0` = disable triggering) |
| `enable_sns_topic_delivery_status_logs` | `bool` | `false` | Enable SNS delivery status logging (creates feedback IAM role) |
| `sns_topic_policy` | `string` | `null` | Custom, fully-formed SNS topic access policy JSON |
| `subscription_filter_policy` | `string` | `null` | SNS subscription filter policy JSON |
| `subscription_filter_policy_scope` | `string` | `null` | Filter scope: `MessageAttributes` or `MessageBody` |
| `lambda_dead_letter_target_arn` | `string` | `null` | SNS/SQS ARN for failed invocations |
| `lambda_attach_dead_letter_policy` | `bool` | `false` | Must be `true` to attach IAM permissions for the DLQ target |
| `iam_role_boundary_policy_arn` | `string` | `null` | Permissions boundary ARN for the Lambda IAM role |
| `putin_khuylo` | `bool` | `true` | Must remain `true` (or resources are silently not created); see Notes for AI Agents |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `slack_topic_arn` | SNS topic ARN to use as a target for alarms/events |
| `notify_slack_lambda_function_arn` | Lambda function ARN |
| `notify_slack_lambda_function_name` | Lambda function name |
| `notify_slack_lambda_function_invoke_arn` | ARN for API Gateway invocation |
| `notify_slack_lambda_function_version` | Latest published Lambda version |
| `notify_slack_lambda_function_last_modified` | Timestamp the Lambda function was last modified |
| `lambda_iam_role_arn` | IAM role ARN used by Lambda |
| `lambda_iam_role_name` | IAM role name used by Lambda |
| `lambda_cloudwatch_log_group_arn` | CloudWatch log group ARN for the Lambda function |
| `sns_topic_feedback_role_arn` | IAM role ARN used for SNS delivery status logging |

## Usage Examples

### Example 1: Basic Slack Notification

```hcl
module "notify_slack" {
  source  = "terraform-aws-modules/notify-slack/aws"
  version = "~> 7.0"

  sns_topic_name = "slack-notifications"

  slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  slack_channel     = "aws-alerts"
  slack_username    = "AWS Reporter"

  tags = {
    Environment = "production"
    Team        = "DevOps"
  }
}

# CloudWatch alarm that sends to Slack
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "high-cpu-usage"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "CPU usage exceeds 80%"

  alarm_actions = [module.notify_slack.slack_topic_arn]
}
```

### Example 2: Using an Existing SNS Topic

```hcl
module "notify_slack" {
  source  = "terraform-aws-modules/notify-slack/aws"
  version = "~> 7.0"

  create_sns_topic = false
  sns_topic_name   = "existing-notifications-topic"

  slack_webhook_url    = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  slack_channel        = "operations"
  slack_username       = "AWS Monitor"
  lambda_function_name = "notify-slack-ops"

  tags = {
    Environment = "production"
  }
}
```

### Example 3: KMS Encryption with Multi-Environment Deployment

```hcl
resource "aws_kms_key" "slack_webhook" {
  description             = "KMS key for Slack webhook encryption"
  deletion_window_in_days = 7
}

resource "aws_kms_ciphertext" "slack_url" {
  plaintext = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  key_id    = aws_kms_key.slack_webhook.arn
}

module "notify_slack" {
  source  = "terraform-aws-modules/notify-slack/aws"
  version = "~> 7.0"

  for_each = toset(["dev", "staging", "prod"])

  sns_topic_name       = "slack-topic-${each.value}"
  lambda_function_name = "notify-slack-${each.value}"
  lambda_description   = "Slack notifications for ${each.value}"

  slack_webhook_url = aws_kms_ciphertext.slack_url.ciphertext_blob
  slack_channel     = "aws-${each.value}"
  slack_username    = "AWS ${title(each.value)}"

  kms_key_arn                            = aws_kms_key.slack_webhook.arn
  sns_topic_kms_key_id                   = aws_kms_key.slack_webhook.id
  cloudwatch_log_group_kms_key_id        = aws_kms_key.slack_webhook.id
  cloudwatch_log_group_retention_in_days = 7

  log_events                            = each.value != "prod"
  enable_sns_topic_delivery_status_logs = true

  tags = {
    Environment = each.value
  }
}
```

### Example 4: GuardDuty Findings via EventBridge

```hcl
module "notify_slack_security" {
  source  = "terraform-aws-modules/notify-slack/aws"
  version = "~> 7.0"

  sns_topic_name       = "guardduty-findings"
  lambda_function_name = "guardduty-to-slack"

  slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  slack_channel     = "security-alerts"
  slack_username    = "AWS Security"

  log_events                             = true
  cloudwatch_log_group_retention_in_days = 30

  # Grant EventBridge permission to publish to the topic
  sns_topic_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action    = "sns:Publish"
      Resource  = "arn:aws:sns:*:*:guardduty-findings"
    }]
  })

  tags = {
    Purpose    = "Security monitoring"
    Compliance = "Required"
  }
}

# EventBridge rule to capture GuardDuty findings
resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  name        = "guardduty-findings-to-slack"
  description = "Capture GuardDuty findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
  })
}

resource "aws_cloudwatch_event_target" "sns" {
  rule      = aws_cloudwatch_event_rule.guardduty_findings.name
  target_id = "SendToSNS"
  arn       = module.notify_slack_security.slack_topic_arn
}
```

### Example 5: VPC-Deployed Lambda with Dead Letter Queue

```hcl
resource "aws_sqs_queue" "notify_slack_dlq" {
  name = "notify-slack-dlq"
}

module "notify_slack_vpc" {
  source  = "terraform-aws-modules/notify-slack/aws"
  version = "~> 7.0"

  sns_topic_name = "slack-notifications-vpc"

  slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  slack_channel     = "aws-alerts"
  slack_username    = "AWS Reporter"

  lambda_function_vpc_subnet_ids         = ["subnet-xxx", "subnet-yyy"]
  lambda_function_vpc_security_group_ids = ["sg-xxx"]

  lambda_dead_letter_target_arn    = aws_sqs_queue.notify_slack_dlq.arn
  lambda_attach_dead_letter_policy = true

  tags = {
    Environment = "production"
  }
}
```

## Best Practices

### Security

1. **Encrypt Webhook URLs**: Use KMS encryption via `kms_key_arn` (with a KMS-encrypted `slack_webhook_url`) to protect credentials in Terraform state
2. **Encrypt SNS Topics**: Enable server-side encryption with `sns_topic_kms_key_id`
3. **Encrypt CloudWatch Logs**: Use `cloudwatch_log_group_kms_key_id` for compliance
4. **Never Commit Webhooks**: Store webhook URLs in AWS Secrets Manager or SSM Parameter Store and pass them in via data sources
5. **VPC Deployment**: Deploy Lambda in private subnets for sensitive environments
6. **Scope SNS Topic Policy**: When using `sns_topic_policy`, restrict `Principal` and `Resource` to the specific publishers (e.g., `events.amazonaws.com`) instead of using wildcards
7. **Rotate Webhooks**: Periodically rotate Slack webhook URLs

### Operations

1. **Enable Debug Logging**: Use `log_events = true` during initial setup, disable in production
2. **Set Log Retention**: Configure `cloudwatch_log_group_retention_in_days` (7-30 days typical)
3. **Monitor Delivery**: Enable `enable_sns_topic_delivery_status_logs` for operational visibility into failed SNS deliveries
4. **Configure DLQ Correctly**: Set both `lambda_dead_letter_target_arn` and `lambda_attach_dead_letter_policy = true` — the ARN alone does not grant IAM permission to publish
5. **Test Webhooks**: Validate Slack webhook URLs before applying configuration

### Cost Optimization

1. **ARM Architecture**: Use `architectures = ["arm64"]` for lower Lambda cost per invocation
2. **Short Log Retention**: Use 7 days for non-production environments
3. **Reuse SNS Topics**: Consolidate notifications through shared topics where appropriate
4. **Filter Policies**: Use `subscription_filter_policy`/`subscription_filter_policy_scope` to avoid unnecessary Lambda invocations

### Multi-Environment

1. **Separate Channels**: Use different Slack channels per environment
2. **for_each Pattern**: Deploy multiple instances efficiently keyed by environment name
3. **Consistent Tagging**: Apply environment tags for cost tracking
4. **Environment-Specific Logging**: Enable debug logging only in non-production

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-notify-slack
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/notify-slack/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-notify-slack/tree/master/examples
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-notify-slack/blob/master/CHANGELOG.md
- **AWS SNS Documentation**: https://docs.aws.amazon.com/sns/latest/dg/welcome.html
- **AWS Lambda Documentation**: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
- **Slack Incoming Webhooks**: https://api.slack.com/messaging/webhooks
- **EventBridge Integration**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html

## Notes for AI Agents

1. **Required Variables**: `sns_topic_name`, `slack_webhook_url`, `slack_channel`, `slack_username` are always required
2. **`putin_khuylo` Gotcha**: This module defines a variable `putin_khuylo` (default `true`) that gates `local.create` (`var.create && var.putin_khuylo`); leave it at the default `true` — setting it `false` silently prevents all resources from being created even if `create = true`
3. **Dead Letter Queue Needs Two Variables**: Set `lambda_dead_letter_target_arn` *and* `lambda_attach_dead_letter_policy = true` together; the ARN alone does not attach the required IAM permission
4. **Version Requirements**: Module requires Terraform >= 1.5.7 and AWS provider >= 6.28; pin with `version = "~> 7.0"` for stability with patch/minor updates
5. **SNS Topic Strategy**: Decide between a new topic (`create_sns_topic = true`, default) or subscribing to an existing one (`create_sns_topic = false`)
6. **EventBridge as Source**: For event sources other than CloudWatch Alarms (e.g., GuardDuty, custom EventBridge rules), create an `aws_cloudwatch_event_rule`/`aws_cloudwatch_event_target` pair targeting `slack_topic_arn`, and grant `events.amazonaws.com` publish permission via `sns_topic_policy`
7. **Built-In Event Parsers**: The bundled Lambda already understands CloudWatch Alarms, CloudWatch Logs Metric Alarms, GuardDuty Findings, GuardDuty Malware Protection results, AWS Backup, DMS, and Glue payloads — no custom code needed for these; use `lambda_source_path` only for genuinely custom formats
8. **Output Usage**: Use the `slack_topic_arn` output as the target for `alarm_actions`, EventBridge targets, or other SNS publishers
9. **Cross-Region**: Deploy one module instance per region requiring monitoring (SNS/Lambda are regional)
10. **Webhook Secret Handling**: Prefer sourcing `slack_webhook_url` from Secrets Manager/SSM or a KMS ciphertext rather than hardcoding it in Terraform files
