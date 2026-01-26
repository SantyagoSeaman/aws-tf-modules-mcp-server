# Terraform AWS SNS Module

## Module Information

- **Module Name**: `sns`
- **Source**: `terraform-aws-modules/sns/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-sns
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/sns/aws/latest
- **Latest Version**: 7.1.0
- **Purpose**: Terraform module to create and manage AWS SNS topics with subscriptions, policies, and encryption
- **Service**: AWS SNS (Simple Notification Service)
- **Category**: Messaging, Notifications, Event-Driven Architecture
- **Keywords**: sns, notifications, pub-sub, messaging, topics, subscriptions, sqs, lambda, fifo, kms-encryption, topic-policy, fan-out, event-driven, dead-letter-queue, message-filtering

## Description

AWS Simple Notification Service (SNS) is a fully managed pub/sub messaging service that enables you to decouple microservices, distributed systems, and serverless applications. This Terraform module provides a comprehensive solution for creating and managing SNS topics with various configurations including standard and FIFO topics, multiple subscription types, encryption, and advanced policy management.

The module supports creating both standard and FIFO (First-In-First-Out) topics, allowing you to choose the appropriate message ordering and delivery guarantees for your use case. It handles the complete lifecycle of SNS topics including subscription management for various protocols (SQS, Lambda, HTTP/HTTPS, email, SMS, and more), topic policies for access control, and encryption using AWS KMS. The module also provides configuration options for message delivery policies, feedback mechanisms, data protection policies, and message filtering.

This module is particularly valuable for building event-driven architectures where multiple subscribers need to receive notifications from a single source. It integrates seamlessly with other AWS services like Lambda, SQS, Kinesis Firehose, and CloudWatch, enabling robust fan-out patterns and asynchronous communication flows.

## Key Features

- **Standard SNS Topics**: Create standard SNS topics for at-least-once message delivery with best-effort ordering
- **FIFO Topics**: Support for FIFO topics with strict message ordering and exactly-once delivery guarantees
- **Content-Based Deduplication**: Automatic deduplication of messages in FIFO topics based on message content
- **Multiple Subscription Protocols**: Support for SQS, Lambda, HTTP/HTTPS, email, SMS, application endpoints, and Kinesis Firehose subscriptions
- **KMS Encryption**: Server-side encryption of messages using AWS KMS customer managed keys or AWS managed keys
- **Topic Access Policies**: Flexible IAM policy configuration with statement builder for topic-level access control
- **Data Protection Policies**: Built-in data protection to detect and deny messages containing sensitive data (non-FIFO topics only)
- **Message Filtering**: Subscription-level message filtering based on message attributes to reduce unnecessary deliveries
- **Delivery Policies**: Customizable retry logic, backoff functions, and throttling controls for HTTP/HTTPS endpoints
- **Delivery Status Logging**: Multi-channel feedback configurations (Application, Firehose, HTTP, Lambda, SQS) for tracking message delivery
- **X-Ray Tracing**: Integration with AWS X-Ray for distributed tracing (PassThrough/Active modes)
- **Archive Policy**: Configure message archiving for FIFO topics with message replay capability
- **Signature Versions**: Configure message signature versions (SHA1 or SHA256) for enhanced security verification
- **Conditional Creation**: Control resource creation via `create` flag for conditional deployments
- **Tagging Support**: Comprehensive tagging capabilities for resource organization and cost allocation

## Main Use Cases

1. **Application Monitoring and Alerts**: Send real-time alerts for application errors, performance issues, and system health events
2. **Event-Driven Workflows**: Coordinate distributed workflows and trigger downstream processes across microservices
3. **Fan-Out Architecture**: Broadcast messages to multiple subscribers simultaneously for parallel processing patterns
4. **Mobile Push Notifications**: Deliver push notifications to iOS, Android, and other mobile platforms via application endpoints
5. **Email and SMS Notifications**: Send transactional emails and SMS messages for user notifications and alerts
6. **Serverless Event Routing**: Route events from various sources to Lambda functions for serverless application architectures
7. **Cross-Service Integration**: Enable asynchronous communication between AWS services like S3, CloudWatch, and EventBridge
8. **Distributed Systems Communication**: Enable reliable message passing between microservices in distributed architectures

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | - | SNS topic name (required) |
| `create` | `bool` | `true` | Controls whether resources are created |
| `fifo_topic` | `bool` | `false` | Creates a FIFO topic for ordered message delivery |
| `content_based_deduplication` | `bool` | `false` | Enables automatic deduplication for FIFO topics |
| `kms_master_key_id` | `string` | `null` | KMS key ID/ARN/alias for server-side encryption |
| `subscriptions` | `map(object)` | `{}` | Map of subscription configurations with protocol, endpoint, filters |
| `topic_policy_statements` | `map(object)` | `null` | Custom IAM policy statements for topic access |
| `data_protection_policy` | `string` | `null` | JSON policy for data protection (non-FIFO only) |
| `delivery_policy` | `string` | `null` | JSON delivery policy for retry behavior |
| `tracing_config` | `string` | `null` | X-Ray tracing mode: "PassThrough" or "Active" |
| `signature_version` | `number` | `null` | Message signature hashing (1=SHA1, 2=SHA256) |
| `display_name` | `string` | `null` | Display name for topic |
| `archive_policy` | `string` | `null` | Archive policy for FIFO message replay |
| `fifo_throughput_scope` | `string` | `null` | FIFO throughput scope: "Topic" or "MessageGroup" |
| `create_topic_policy` | `bool` | `true` | Whether to create topic policy |
| `enable_default_topic_policy` | `bool` | `true` | Whether to enable default topic policy |
| `create_subscription` | `bool` | `true` | Whether to create subscriptions |
| `tags` | `map(string)` | `{}` | Tags to apply to resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `topic_arn` | The ARN of the SNS topic |
| `topic_id` | The ARN of the SNS topic (alias for topic_arn) |
| `topic_name` | The name of the topic |
| `topic_owner` | AWS Account ID of the SNS topic owner |
| `topic_beginning_archive_time` | Oldest timestamp for FIFO replay (FIFO topics only) |
| `subscriptions` | Map of all created subscriptions and their attributes |

## Usage Examples

### Basic SNS Topic

```hcl
module "sns_topic" {
  source  = "terraform-aws-modules/sns/aws"
  version = "~> 7.0"

  name = "my-notification-topic"

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}
```

### SNS Topic with SQS Subscription

```hcl
module "sns_topic" {
  source  = "terraform-aws-modules/sns/aws"
  version = "~> 7.0"

  name              = "orders-notifications"
  kms_master_key_id = module.kms.key_id

  subscriptions = {
    sqs = {
      protocol = "sqs"
      endpoint = aws_sqs_queue.orders.arn
      filter_policy = jsonencode({
        event_type = ["order_placed", "order_shipped"]
      })
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### FIFO Topic with Content Deduplication

```hcl
module "sns_fifo" {
  source  = "terraform-aws-modules/sns/aws"
  version = "~> 7.0"

  name                        = "orders-fifo"
  fifo_topic                  = true
  content_based_deduplication = true
  fifo_throughput_scope       = "MessageGroup"

  subscriptions = {
    sqs_fifo = {
      protocol = "sqs"
      endpoint = aws_sqs_queue.orders_fifo.arn
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Complete Example with Custom Policies

```hcl
module "sns_complete" {
  source  = "terraform-aws-modules/sns/aws"
  version = "~> 7.0"

  name              = "app-notifications"
  display_name      = "Application Notifications"
  kms_master_key_id = module.kms.key_id
  tracing_config    = "Active"
  signature_version = 2

  # Custom delivery policy
  delivery_policy = jsonencode({
    http = {
      defaultHealthyRetryPolicy = {
        minDelayTarget     = 20
        maxDelayTarget     = 20
        numRetries         = 3
        backoffFunction    = "linear"
      }
    }
  })

  # Topic policy statements
  topic_policy_statements = {
    pub = {
      actions = ["sns:Publish"]
      principals = [{
        type        = "AWS"
        identifiers = ["arn:aws:iam::123456789012:role/publisher"]
      }]
    }
    sub = {
      actions = ["sns:Subscribe", "sns:Receive"]
      principals = [{
        type        = "AWS"
        identifiers = ["*"]
      }]
      conditions = [{
        test     = "StringEquals"
        variable = "AWS:SourceOwner"
        values   = ["123456789012"]
      }]
    }
  }

  # Multiple subscriptions
  subscriptions = {
    sqs = {
      protocol = "sqs"
      endpoint = aws_sqs_queue.notifications.arn
    }
    lambda = {
      protocol = "lambda"
      endpoint = aws_lambda_function.processor.arn
    }
  }

  # SQS feedback configuration
  sqs_feedback = {
    failure_role_arn    = aws_iam_role.feedback.arn
    success_role_arn    = aws_iam_role.feedback.arn
    success_sample_rate = 100
  }

  tags = {
    Environment = "production"
    Application = "notifications"
  }
}
```

## Best Practices

### Topic Configuration

1. **Choose Appropriate Topic Type**: Use standard topics for high throughput and best-effort ordering; use FIFO topics when strict ordering and exactly-once delivery are required
2. **Enable Content-Based Deduplication**: For FIFO topics, enable content-based deduplication to automatically prevent duplicate messages
3. **Configure FIFO Throughput Scope**: Set to "MessageGroup" for higher throughput when order is only needed within groups
4. **Use Descriptive Topic Names**: Name topics clearly to indicate their purpose (e.g., "orders-created", "payment-processed")

### Security and Access Control

1. **Enable KMS Encryption**: Always encrypt sensitive message data using customer-managed KMS keys
2. **Implement Least Privilege Policies**: Configure topic policies to grant minimum necessary permissions
3. **Use Condition Keys**: Leverage IAM condition keys in topic policies to restrict access based on source
4. **Enable Data Protection Policies**: Implement data protection policies to automatically detect and block messages containing PII
5. **Use SHA256 Signatures**: Set `signature_version = 2` to use SHA256 instead of SHA1

### Subscription Management

1. **Use Subscription Filters**: Implement message filtering at the subscription level to reduce unnecessary message deliveries
2. **Configure Dead Letter Queues**: Attach DLQs to subscriptions to capture failed message deliveries
3. **Set Appropriate Retry Policies**: Configure delivery retry policies based on subscriber characteristics
4. **Enable Raw Message Delivery**: For SQS and HTTP subscriptions, enable raw message delivery when SNS metadata wrapper is not needed

### Monitoring and Observability

1. **Enable X-Ray Tracing**: Activate message tracing to track message flows through distributed systems
2. **Configure Feedback Logging**: Enable feedback logging for all subscription protocols to track delivery success and failures
3. **Set Up CloudWatch Alarms**: Create alarms for key metrics like NumberOfNotificationsFailed

### Cost Optimization

1. **Use Message Filtering**: Reduce costs by filtering messages at the subscription level
2. **Optimize Message Size**: Keep message payloads small; use S3 references for large data
3. **Right-Size FIFO Usage**: Only use FIFO topics when ordering guarantees are required

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-sns
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/sns/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-sns/tree/master/examples
- **AWS SNS Documentation**: https://docs.aws.amazon.com/sns/latest/dg/welcome.html
- **SNS Message Filtering**: https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering.html
- **SNS FIFO Topics**: https://docs.aws.amazon.com/sns/latest/dg/sns-fifo-topics.html
- **SNS Data Protection**: https://docs.aws.amazon.com/sns/latest/dg/sns-message-data-protection.html
- **SNS Security**: https://docs.aws.amazon.com/sns/latest/dg/sns-security.html
- **SNS Pricing**: https://aws.amazon.com/sns/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Choose Topic Type Carefully**: Evaluate whether standard or FIFO topics are required based on ordering and delivery guarantees
2. **Enable Encryption**: Always use KMS encryption for sensitive data; reference existing KMS keys or create new ones
3. **Configure Topic Policies**: Implement least privilege access policies using `topic_policy_statements`
4. **Set Up Subscriptions Properly**: Configure subscription filters, and retry policies based on subscriber requirements
5. **Use Data Protection**: Enable data protection policies (non-FIFO only) to prevent accidental transmission of sensitive information
6. **Tag Consistently**: Apply comprehensive tags for resource management and cost tracking
7. **Monitor Delivery Status**: Enable feedback logging to track message delivery health
8. **FIFO Constraints**: Remember that FIFO topic names must end with `.fifo`, and SQS subscribers must also be FIFO queues
9. **Data Protection Limitation**: Data protection policies are only supported for non-FIFO topics
10. **Implement Idempotency**: Ensure downstream systems handle duplicate messages gracefully for standard topics
