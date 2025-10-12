---
module_name: notify-slack
keywords: [slack, notifications, sns, lambda, cloudwatch, alerts, monitoring, guardduty, webhook, chatops, incident-response, serverless, python, kms-encryption, event-driven, alarm-notifications, security-alerts, chatbot, messaging, integration, aws-events, slack-integration, sns-topic, lambda-function, encrypted-webhook, cloudwatch-alarms, guardduty-findings, malware-protection, event-notifications, alerting, real-time-notifications, devops, sre, monitoring-integration, slack-webhook, notification-service, alert-routing, event-handler, aws-notifications, slack-channel, automated-alerts, security-monitoring, operational-alerts]
---

# Terraform AWS Notify Slack Module

## Module Information

- **Module Name**: `notify-slack`
- **Source**: `terraform-aws-modules/notify-slack/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-notify-slack
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/notify-slack/aws/latest
- **Latest Version**: 7.1.0
- **Purpose**: Terraform module that creates AWS SNS topic and Lambda function to send notifications from AWS services to Slack channels
- **Service**: AWS SNS (Simple Notification Service), AWS Lambda
- **Category**: Monitoring, Alerting, Integration, Operations
- **Keywords**: slack, notifications, sns, lambda, cloudwatch, alerts, monitoring, guardduty, webhook, chatops, incident-response, serverless, python, kms-encryption, event-driven, alarm-notifications, security-alerts, chatbot, messaging, integration, aws-events, slack-integration, sns-topic, lambda-function, encrypted-webhook, cloudwatch-alarms, guardduty-findings, malware-protection, event-notifications, alerting, real-time-notifications, devops, sre, monitoring-integration, slack-webhook, notification-service, alert-routing, event-handler, aws-notifications, slack-channel, automated-alerts, security-monitoring, operational-alerts
- **Use For**: CloudWatch alarm notifications, GuardDuty security alerts, malware scan notifications, operational incident alerts, automated monitoring notifications, DevOps event notifications, real-time system alerts, ChatOps integration, security event notifications, multi-environment alerting, infrastructure monitoring alerts, application error notifications

## Description

The Terraform AWS Notify Slack module provides a complete solution for routing AWS service notifications to Slack channels using an event-driven serverless architecture. The module creates an SNS topic that receives notifications from various AWS services and a Lambda function (Python 3.13 runtime) that processes these events and forwards them to Slack using incoming webhooks. This integration enables teams to receive real-time alerts and notifications directly in their Slack workspace, facilitating rapid incident response and improved operational visibility.

The module supports multiple AWS event sources including CloudWatch Alarms, GuardDuty findings, and GuardDuty Malware Protection scan results. It provides flexible configuration options for both creating new SNS topics or integrating with existing ones, making it suitable for various architectural patterns. The module handles the complexity of Lambda deployment, IAM role management, CloudWatch log group creation, and SNS topic configuration, providing a production-ready notification pipeline with minimal configuration.

Security features include support for KMS-encrypted Slack webhook URLs, customizable IAM permissions, and CloudWatch Logs integration for audit trails. The module follows AWS best practices for Lambda function deployment, including configurable architectures (x86_64 or ARM), customizable runtime environments, and optional dead-letter queue configuration. It's designed for multi-environment deployments with support for resource tagging and environment-specific configurations.

## Key Features

- **SNS Topic Management**: Create new SNS topics or integrate with existing topics for flexible event routing
- **Lambda Function Automation**: Automatically deploys Python 3.13 Lambda function with all necessary permissions and configurations
- **Multiple Event Sources**: Supports CloudWatch Alarms, GuardDuty findings, and GuardDuty Malware Protection scan results
- **Encrypted Webhook Support**: Optional KMS encryption for Slack webhook URLs to protect sensitive credentials
- **Customizable Slack Messages**: Configure channel names, usernames, and message formatting options
- **IAM Role Management**: Automatically creates and configures IAM roles with least-privilege permissions
- **CloudWatch Logs Integration**: Built-in logging with configurable retention periods for troubleshooting and auditing
- **SNS Delivery Status Logging**: Optional SNS topic delivery status logs for monitoring notification delivery
- **Multi-Architecture Support**: Configurable Lambda architecture for x86_64 or ARM (Graviton2) processors
- **Dead Letter Queue Support**: Optional DLQ configuration for failed Lambda invocations
- **Resource Tagging**: Comprehensive tagging support for all created resources
- **Environment Variables**: Flexible Lambda environment variable configuration for custom behavior
- **Lambda Dependencies**: Uses terraform-aws-lambda module for reliable function deployment
- **Version Management**: Supports Lambda function versioning and aliases
- **CloudWatch Log Group**: Automatic log group creation with configurable retention policies
- **Backward Compatibility**: Maintains backward-compatible outputs for seamless upgrades

## Main Use Cases

1. **CloudWatch Alarm Notifications**: Receive real-time alerts when CloudWatch alarms trigger for metrics thresholds
2. **Security Incident Alerts**: Get immediate Slack notifications for GuardDuty security findings and threats
3. **Malware Scan Notifications**: Monitor and respond to GuardDuty Malware Protection scan results in real-time
4. **Multi-Environment Alerting**: Deploy separate notification channels for development, staging, and production environments
5. **Operational Monitoring**: Centralize infrastructure and application alerts in Slack for DevOps teams
6. **Incident Response Automation**: Enable rapid response to critical events through real-time Slack notifications
7. **ChatOps Integration**: Build ChatOps workflows by routing AWS events to team communication channels
8. **Compliance Monitoring**: Track security and compliance events with archived Slack notifications
9. **Application Error Tracking**: Route application errors and exceptions to development team channels
10. **Cost Optimization Alerts**: Receive notifications when AWS spending exceeds configured budgets

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `slack_webhook_url` | `string` | *Required* | The URL of Slack webhook for sending notifications |
| `slack_channel` | `string` | *Required* | The name of the Slack channel for notifications |
| `slack_username` | `string` | *Required* | The username that will appear on Slack messages |
| `sns_topic_name` | `string` | `""` | Name of SNS topic to create or use |
| `create` | `bool` | `true` | Whether to create all resources |
| `create_sns_topic` | `bool` | `true` | Whether to create new SNS topic |
| `lambda_function_name` | `string` | `"notify_slack"` | The name of the Lambda function to create |
| `runtime` | `string` | `"python3.13"` | Lambda function runtime version |
| `kms_key_arn` | `string` | `""` | ARN of KMS key for encrypting webhook URL |
| `lambda_description` | `string` | `""` | Description of the Lambda function |
| `log_events` | `bool` | `false` | Enable logging of incoming SNS messages |
| `enable_sns_topic_delivery_status_logs` | `bool` | `false` | Enable SNS topic delivery status logging |
| `architectures` | `list(string)` | `null` | Instruction set architecture for Lambda function |
| `cloudwatch_log_group_retention_in_days` | `number` | `0` | CloudWatch log group retention period (0 = never expire) |
| `cloudwatch_log_group_kms_key_id` | `string` | `null` | KMS key ID for encrypting CloudWatch logs |
| `tags` | `map(string)` | `{}` | Tags to apply to all created resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `slack_topic_arn` | ARN of the SNS topic for sending messages to Slack |
| `notify_slack_lambda_function_arn` | ARN of the Lambda function that sends notifications |
| `notify_slack_lambda_function_name` | Name of the Lambda notification function |
| `notify_slack_lambda_function_invoke_arn` | Invoke ARN for triggering Lambda from API Gateway |
| `lambda_iam_role_arn` | ARN of the IAM role used by Lambda function |
| `lambda_iam_role_name` | Name of the IAM role used by Lambda function |
| `lambda_cloudwatch_log_group_arn` | ARN of the CloudWatch log group for Lambda logs |
| `notify_slack_lambda_function_version` | Latest published version of Lambda function |

## Usage Examples

### Example 1: Simple Slack Notification

Basic configuration creating a new SNS topic and Lambda function for Slack notifications.

```hcl
module "notify_slack" {
  source  = "terraform-aws-modules/notify-slack/aws"
  version = "~> 7.1"

  sns_topic_name = "slack-notifications"

  slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  slack_channel     = "aws-alerts"
  slack_username    = "AWS Reporter"

  tags = {
    Environment = "production"
    Team        = "DevOps"
  }
}

# Example CloudWatch alarm that sends to Slack
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

Configuration that integrates with an existing SNS topic instead of creating a new one.

```hcl
resource "aws_sns_topic" "existing" {
  name = "existing-notifications-topic"

  tags = {
    Environment = "production"
  }
}

module "notify_slack" {
  source  = "terraform-aws-modules/notify-slack/aws"
  version = "~> 7.1"

  sns_topic_name   = aws_sns_topic.existing.name
  create_sns_topic = false

  slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  slack_channel     = "operations"
  slack_username    = "AWS Monitor"

  lambda_function_name = "notify-slack-ops"

  tags = {
    Environment = "production"
    Owner       = "ops-team"
  }
}
```

### Example 3: Multi-Environment with KMS Encryption

Advanced configuration using KMS-encrypted webhook URLs and multiple environments.

```hcl
resource "aws_kms_key" "slack_webhook" {
  description             = "KMS key for Slack webhook encryption"
  deletion_window_in_days = 7

  tags = {
    Purpose = "Slack webhook encryption"
  }
}

resource "aws_kms_ciphertext" "slack_url" {
  plaintext = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  key_id    = aws_kms_key.slack_webhook.arn
}

module "notify_slack" {
  source  = "terraform-aws-modules/notify-slack/aws"
  version = "~> 7.1"

  for_each = toset(["dev", "staging", "prod"])

  sns_topic_name                        = "slack-topic-${each.value}"
  enable_sns_topic_delivery_status_logs = true

  lambda_function_name = "notify-slack-${each.value}"
  lambda_description   = "Slack notifications for ${each.value} environment"

  slack_webhook_url = aws_kms_ciphertext.slack_url.ciphertext_blob
  slack_channel     = "aws-${each.value}"
  slack_username    = "AWS ${title(each.value)}"

  kms_key_arn = aws_kms_key.slack_webhook.arn
  log_events  = true

  cloudwatch_log_group_retention_in_days = 7
  cloudwatch_log_group_kms_key_id        = aws_kms_key.slack_webhook.id

  tags = {
    Environment = each.value
    Managed     = "Terraform"
  }
}

# CloudWatch alarm for Lambda duration monitoring
resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "NotifySlackDuration"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Average"
  threshold           = 5000
  alarm_description   = "Slack notification Lambda duration exceeds 5 seconds"

  alarm_actions = [module.notify_slack["prod"].slack_topic_arn]

  dimensions = {
    FunctionName = module.notify_slack["prod"].notify_slack_lambda_function_name
  }
}
```

### Example 4: GuardDuty Integration

Configuration for routing GuardDuty security findings to Slack.

```hcl
module "notify_slack_security" {
  source  = "terraform-aws-modules/notify-slack/aws"
  version = "~> 7.1"

  sns_topic_name = "guardduty-findings"

  slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  slack_channel     = "security-alerts"
  slack_username    = "AWS Security"

  lambda_function_name = "guardduty-to-slack"
  lambda_description   = "Forward GuardDuty findings to Slack"

  log_events = true

  cloudwatch_log_group_retention_in_days = 30

  tags = {
    Purpose     = "Security monitoring"
    Compliance  = "Required"
    Environment = "production"
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

## Best Practices

### Security Configuration

1. **Encrypt Webhook URLs**: Use KMS encryption for Slack webhook URLs to protect credentials from exposure in Terraform state
2. **Least Privilege IAM**: Module automatically creates minimal IAM permissions; avoid granting additional unnecessary permissions
3. **Secure Webhook Storage**: Never commit plaintext webhook URLs to version control; use encrypted values or AWS Secrets Manager
4. **Enable CloudWatch Logs Encryption**: Encrypt CloudWatch log groups with KMS keys for compliance requirements
5. **Regular Webhook Rotation**: Periodically rotate Slack webhook URLs and update KMS-encrypted values
6. **SNS Topic Policies**: Restrict SNS topic access to only authorized AWS services and accounts
7. **VPC Configuration**: For highly sensitive environments, consider deploying Lambda in VPC with private subnets

### Operational Excellence

1. **Enable Logging**: Set `log_events = true` in non-production environments for debugging event payloads
2. **Configure Log Retention**: Set appropriate CloudWatch log retention periods to balance cost and compliance (7-30 days typical)
3. **Monitor Lambda Metrics**: Create CloudWatch alarms for Lambda errors, duration, and throttling
4. **SNS Delivery Logging**: Enable `enable_sns_topic_delivery_status_logs` to track notification delivery failures
5. **Dead Letter Queue**: Configure DLQ for Lambda to capture and analyze failed notification attempts
6. **Environment-Specific Channels**: Use separate Slack channels for different environments (dev, staging, prod)
7. **Descriptive Naming**: Use clear, consistent naming conventions for Lambda functions and SNS topics

### Performance and Reliability

1. **Lambda Architecture**: Consider ARM (Graviton2) architecture for cost savings (set `architectures = ["arm64"]`)
2. **Timeout Configuration**: Adjust Lambda timeout based on Slack API response times (default is usually sufficient)
3. **Reserved Concurrency**: For critical alerts, configure reserved concurrency to ensure Lambda availability
4. **Retry Configuration**: Lambda automatically retries SNS invocations; monitor retry metrics for persistent failures
5. **Webhook Validation**: Test webhook URLs before deployment to avoid notification failures

### Cost Optimization

1. **Log Retention**: Set shorter retention periods (7 days) for non-production environments to reduce CloudWatch costs
2. **SNS Topic Reuse**: Reuse SNS topics across multiple services when appropriate instead of creating multiple topics
3. **ARM Architecture**: Use `architectures = ["arm64"]` for up to 20% cost savings on Lambda execution
4. **Alarm Threshold Tuning**: Optimize CloudWatch alarm thresholds to reduce unnecessary notifications and SNS invocations
5. **Filter Events**: Use SNS filter policies to process only relevant events and reduce Lambda invocations

### Monitoring and Alerting

1. **Lambda Error Alarms**: Monitor Lambda errors and create alerts for notification delivery failures
2. **Duration Monitoring**: Track Lambda duration metrics to identify performance degradation
3. **SNS Metrics**: Monitor SNS NumberOfNotificationsFailed and NumberOfNotificationsDelivered metrics
4. **Slack Delivery Verification**: Periodically verify Slack notifications are being delivered successfully
5. **Log Analysis**: Review CloudWatch logs for failed webhook calls or malformed events

### Multi-Environment Deployment

1. **Environment Tagging**: Use consistent tagging strategy across all environments for cost tracking and organization
2. **Separate Channels**: Use different Slack channels per environment to avoid alert confusion
3. **For_each Pattern**: Use for_each to deploy multiple environment-specific instances efficiently
4. **Terraform Workspaces**: Consider using Terraform workspaces for managing environment-specific configurations
5. **State Isolation**: Use separate Terraform state files for different environments

### Integration Patterns

1. **EventBridge Integration**: Use EventBridge rules to route specific AWS service events to SNS topics
2. **Multiple Event Sources**: Single module instance can handle multiple event sources through one SNS topic
3. **Alarm Consolidation**: Group related CloudWatch alarms to use the same SNS topic for organized notifications
4. **Cross-Region Notifications**: Deploy module in each region requiring monitoring for region-specific events
5. **Service-Specific Topics**: Consider separate SNS topics for different service categories (security, performance, operations)

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-notify-slack
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/notify-slack/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-notify-slack/tree/master/examples
- **AWS SNS Documentation**: https://docs.aws.amazon.com/sns/latest/dg/welcome.html
- **AWS Lambda Documentation**: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
- **Slack Incoming Webhooks**: https://api.slack.com/messaging/webhooks
- **AWS CloudWatch Alarms**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html
- **AWS GuardDuty**: https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html
- **AWS KMS Encryption**: https://docs.aws.amazon.com/kms/latest/developerguide/overview.html
- **EventBridge Integration**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html
- **Lambda Best Practices**: https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html
- **SNS Best Practices**: https://docs.aws.amazon.com/sns/latest/dg/sns-best-practices.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Webhook Security**: Always use KMS-encrypted webhook URLs in production; never expose plaintext webhooks
2. **Test Before Deploy**: Validate Slack webhook URLs are active before applying Terraform configuration
3. **Environment Isolation**: Deploy separate instances per environment with distinct Slack channels
4. **Enable Logging Initially**: Use `log_events = true` during initial setup for debugging, disable in production
5. **Monitor Delivery**: Set up CloudWatch alarms for Lambda errors and SNS delivery failures
6. **Tag Consistently**: Apply comprehensive tags for cost tracking and resource organization
7. **SNS Topic Strategy**: Decide between creating new topics or using existing ones based on event routing needs
8. **Multi-Region Deployment**: Deploy module in each region that generates events requiring Slack notifications
9. **Alarm Threshold Testing**: Test CloudWatch alarm thresholds to ensure appropriate notification frequency
10. **Slack Channel Design**: Plan Slack channel structure (by environment, service, severity) before deployment
11. **KMS Key Management**: Create dedicated KMS keys for webhook encryption with appropriate key policies
12. **Cost Monitoring**: Track Lambda invocations and SNS message costs, especially in high-traffic scenarios
13. **Webhook Rotation**: Implement process for rotating Slack webhooks and updating encrypted values
14. **Event Filtering**: Use SNS filter policies to reduce unnecessary Lambda invocations and costs
15. **Lambda Versioning**: Use Lambda versions and aliases for controlled deployments and rollbacks
