# Terraform AWS Notify Slack Module

## Module Information

- **Module Name**: `notify-slack`
- **Source**: `terraform-aws-modules/notify-slack/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-notify-slack
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/notify-slack/aws/latest
- **Latest Version**: 7.2.0
- **Purpose**: Creates SNS topic and Lambda function to send AWS notifications to Slack channels via webhooks
- **Service**: AWS SNS (Simple Notification Service), AWS Lambda
- **Category**: Monitoring, Alerting, Integration
- **Keywords**: slack, notifications, sns, lambda, cloudwatch-alarms, alerts, monitoring, guardduty, webhook, chatops, serverless, kms-encryption, event-driven, sns-topic, slack-integration
- **Use For**: CloudWatch alarm notifications, GuardDuty security alerts, operational incident alerts, DevOps event notifications, ChatOps integration, multi-environment alerting, application error notifications

## Description

The Terraform AWS Notify Slack module creates an SNS topic and Lambda function (Python 3.13 runtime) that forwards AWS notifications to Slack channels using incoming webhooks. It supports multiple event sources including CloudWatch Alarms, GuardDuty findings, and generic SNS messages.

The module handles Lambda deployment, IAM role management, CloudWatch log groups, and SNS topic configuration. It supports both creating new SNS topics and integrating with existing ones. Security features include KMS encryption for webhook URLs, SNS topic encryption, and CloudWatch Logs encryption.

Key capabilities include VPC deployment for network isolation, dead letter queue configuration, SNS filter policies for message routing, and delivery status logging for operational monitoring.

## Key Features

- **SNS Topic Management**: Create new or use existing SNS topics for event routing
- **Lambda Function**: Python 3.13 runtime with x86_64 or arm64 architecture support
- **CloudWatch Alarms Integration**: Direct alarm-to-Slack notification pipeline
- **GuardDuty Support**: Forward security findings to Slack channels
- **KMS Encryption**: Encrypt webhook URLs, SNS topics, and CloudWatch logs
- **VPC Deployment**: Deploy Lambda in private subnets for network isolation
- **Dead Letter Queue**: Capture failed invocations for debugging
- **SNS Filter Policies**: Filter messages at subscription level
- **Delivery Status Logging**: Monitor notification delivery with configurable sample rates
- **Custom Lambda Code**: Provide custom notification logic via `lambda_source_path`
- **Comprehensive Tagging**: Tag all created resources consistently

## Main Use Cases

1. **CloudWatch Alarm Notifications**: Real-time alerts when metrics exceed thresholds
2. **Security Alerts**: GuardDuty findings delivered to security team channels
3. **Multi-Environment Alerting**: Separate notification channels for dev/staging/prod
4. **Operational Monitoring**: Centralize infrastructure alerts for DevOps teams
5. **ChatOps Integration**: Route AWS events to team communication channels
6. **Incident Response**: Enable rapid response through real-time Slack notifications

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `sns_topic_name` | `string` | *Required* | SNS topic name to create or reference |
| `slack_webhook_url` | `string` | *Required* | Slack incoming webhook URL |
| `slack_channel` | `string` | *Required* | Target Slack channel name |
| `slack_username` | `string` | *Required* | Display username for Slack messages |
| `create` | `bool` | `true` | Whether to create all resources |
| `create_sns_topic` | `bool` | `true` | Create new SNS topic (false = use existing) |
| `runtime` | `string` | `"python3.13"` | Lambda function runtime version |
| `architectures` | `list(string)` | `null` | Lambda architecture: `["x86_64"]` or `["arm64"]` |
| `slack_emoji` | `string` | `":aws:"` | Custom emoji for Slack message avatar |
| `kms_key_arn` | `string` | `""` | KMS key ARN for webhook URL decryption |
| `sns_topic_kms_key_id` | `string` | `""` | KMS key for SNS topic encryption |
| `cloudwatch_log_group_kms_key_id` | `string` | `null` | KMS key for Lambda log encryption |
| `cloudwatch_log_group_retention_in_days` | `number` | `0` | Log retention (0 = never expire) |
| `log_events` | `bool` | `false` | Log incoming SNS events for debugging |
| `lambda_function_name` | `string` | `"notify_slack"` | Lambda function name |
| `lambda_function_vpc_subnet_ids` | `list(string)` | `null` | VPC subnet IDs for Lambda |
| `lambda_function_vpc_security_group_ids` | `list(string)` | `null` | VPC security group IDs |
| `reserved_concurrent_executions` | `number` | `-1` | Reserved concurrency (-1 = no limit) |
| `enable_sns_topic_delivery_status_logs` | `bool` | `false` | Enable SNS delivery logging |
| `subscription_filter_policy` | `string` | `null` | SNS filter policy JSON |
| `lambda_dead_letter_target_arn` | `string` | `null` | SNS/SQS ARN for failed invocations |
| `tags` | `map(string)` | `{}` | Tags for all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `slack_topic_arn` | SNS topic ARN for sending Slack notifications |
| `notify_slack_lambda_function_arn` | Lambda function ARN |
| `notify_slack_lambda_function_name` | Lambda function name |
| `notify_slack_lambda_function_invoke_arn` | ARN for API Gateway invocation |
| `notify_slack_lambda_function_version` | Latest published Lambda version |
| `lambda_iam_role_arn` | IAM role ARN used by Lambda |
| `lambda_iam_role_name` | IAM role name used by Lambda |
| `lambda_cloudwatch_log_group_arn` | CloudWatch log group ARN |

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

### Example 2: Using Existing SNS Topic

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

### Example 3: KMS Encryption with Multi-Environment

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

### Example 4: GuardDuty Integration

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

resource "aws_sns_topic_policy" "guardduty" {
  arn = module.notify_slack_security.slack_topic_arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action    = "sns:Publish"
      Resource  = module.notify_slack_security.slack_topic_arn
    }]
  })
}
```

### Example 5: VPC-Deployed Lambda

```hcl
module "notify_slack_vpc" {
  source  = "terraform-aws-modules/notify-slack/aws"
  version = "~> 7.0"

  sns_topic_name = "slack-notifications-vpc"

  slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  slack_channel     = "aws-alerts"
  slack_username    = "AWS Reporter"

  lambda_function_vpc_subnet_ids         = ["subnet-xxx", "subnet-yyy"]
  lambda_function_vpc_security_group_ids = ["sg-xxx"]

  tags = {
    Environment = "production"
  }
}
```

## Best Practices

### Security

1. **Encrypt Webhook URLs**: Use KMS encryption via `kms_key_arn` to protect credentials in Terraform state
2. **Encrypt SNS Topics**: Enable server-side encryption with `sns_topic_kms_key_id`
3. **Encrypt CloudWatch Logs**: Use `cloudwatch_log_group_kms_key_id` for compliance
4. **Never Commit Webhooks**: Store webhook URLs in AWS Secrets Manager or SSM Parameter Store
5. **VPC Deployment**: Deploy Lambda in private subnets for sensitive environments
6. **Rotate Webhooks**: Periodically rotate Slack webhook URLs

### Operations

1. **Enable Debug Logging**: Use `log_events = true` during initial setup, disable in production
2. **Set Log Retention**: Configure `cloudwatch_log_group_retention_in_days` (7-30 days typical)
3. **Monitor Delivery**: Enable `enable_sns_topic_delivery_status_logs` for operational visibility
4. **Configure DLQ**: Use `lambda_dead_letter_target_arn` to capture failed notifications
5. **Test Webhooks**: Validate Slack webhook URLs before applying configuration

### Cost Optimization

1. **ARM Architecture**: Use `architectures = ["arm64"]` for ~20% Lambda cost savings
2. **Short Log Retention**: Use 7 days for non-production environments
3. **Reuse SNS Topics**: Consolidate notifications through shared topics where appropriate
4. **Filter Policies**: Use `subscription_filter_policy` to reduce unnecessary Lambda invocations

### Multi-Environment

1. **Separate Channels**: Use different Slack channels per environment
2. **For_each Pattern**: Deploy multiple instances efficiently with for_each
3. **Consistent Tagging**: Apply environment tags for cost tracking
4. **Environment-Specific Logging**: Enable debug logging only in non-production

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-notify-slack
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/notify-slack/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-notify-slack/tree/master/examples
- **AWS SNS Documentation**: https://docs.aws.amazon.com/sns/latest/dg/welcome.html
- **AWS Lambda Documentation**: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
- **Slack Incoming Webhooks**: https://api.slack.com/messaging/webhooks
- **EventBridge Integration**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html

## Notes for AI Agents

1. **Webhook Security**: Always use KMS-encrypted webhook URLs in production
2. **Test Before Deploy**: Validate Slack webhook URLs are active before applying
3. **Environment Isolation**: Deploy separate instances per environment with distinct channels
4. **SNS Topic Strategy**: Decide between new topics (`create_sns_topic = true`) or existing (`create_sns_topic = false`)
5. **EventBridge for GuardDuty**: Use EventBridge rules to route GuardDuty findings to SNS
6. **SNS Topic Policy**: Add SNS topic policy when using EventBridge as event source
7. **Version Constraint**: Use `version = "~> 7.0"` for stability with patch updates
8. **Required Variables**: `sns_topic_name`, `slack_webhook_url`, `slack_channel`, `slack_username` are all required
9. **Output Usage**: Use `slack_topic_arn` output for CloudWatch alarm actions
10. **Cross-Region**: Deploy module in each region requiring monitoring
