# Terraform AWS SQS Module

## Module Information

- **Module Name**: `sqs`
- **Source**: `terraform-aws-modules/sqs/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-sqs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/sqs/aws/latest
- **Latest Version**: 5.2.1
- **Purpose**: Creates and manages Amazon SQS queues with support for standard and FIFO queues, dead letter queues, encryption, and IAM policies
- **Service**: AWS SQS (Simple Queue Service)
- **Category**: Messaging, Integration, Application Services
- **Keywords**: sqs, queue, message-queue, fifo-queue, dead-letter-queue, dlq, kms-encryption, async-processing, event-driven, microservices, serverless, lambda-trigger
- **Use For**: Asynchronous microservices communication, decoupling application components, task queue management, batch job processing, event-driven architectures, message buffering, order processing systems, serverless application integration, background job processing

## Description

The Terraform AWS SQS module provides a complete solution for creating and managing Amazon Simple Queue Service (SQS) queues. Amazon SQS is a fully managed message queuing service enabling asynchronous communication between distributed application components with reliable, scalable, and cost-effective message delivery. The module supports both standard queues (maximum throughput, at-least-once delivery) and FIFO queues (exactly-once processing, strict message ordering).

This module simplifies SQS queue management with infrastructure-as-code configuration for queue attributes, encryption settings, access policies, and AWS service integrations. It handles dead letter queue configuration for automatic routing of failed messages to a separate queue for analysis. The module supports multiple encryption options including SQS-managed keys (SSE-SQS, enabled by default) and customer-managed KMS keys for enhanced security and compliance.

The module enables advanced features such as content-based deduplication for FIFO queues, configurable visibility timeouts, message delay capabilities, and long polling. It provides static ARN outputs to prevent circular dependencies with Step Functions and integrates seamlessly with Lambda, SNS, and EventBridge for building resilient distributed systems.

## Key Features

- **Standard Queue Support**: High-throughput queues with at-least-once delivery and best-effort ordering
- **FIFO Queue Support**: Exactly-once processing with strict message ordering (automatically adds `.fifo` suffix)
- **Dead Letter Queue (DLQ)**: Built-in DLQ creation with configurable redrive policies and maxReceiveCount
- **SQS-Managed Encryption**: Server-side encryption enabled by default using AWS-owned keys (free, no management overhead)
- **KMS Encryption**: Optional customer-managed KMS encryption with configurable data key reuse periods (60-86,400 seconds)
- **Content-Based Deduplication**: Automatic FIFO message deduplication based on message content hash
- **Queue Policies**: IAM policy creation for both primary and dead letter queues with fine-grained access control
- **Static ARN Outputs**: Prevents circular dependencies in Step Functions and other services
- **Long Polling Support**: Configurable receive wait times (0-20 seconds) to reduce costs
- **Flexible Naming**: Auto-generated names or custom names with optional prefixes
- **Conditional Creation**: All resources can be conditionally created via `create` flags
- **Visibility Timeout**: Configurable message visibility (0-43,200 seconds / 12 hours max)
- **Message Retention**: Configurable retention period (60 seconds to 14 days, default 4 days)
- **Message Delay**: Delivery delay configuration (0-900 seconds / 15 minutes max)
- **Comprehensive Tagging**: Full tag support for cost allocation and resource organization

## Main Use Cases

1. **Asynchronous Microservices Communication**: Decouple microservices using queues for non-blocking inter-service messaging
2. **Background Job Processing**: Queue long-running tasks for asynchronous processing by workers or Lambda functions
3. **Load Leveling and Traffic Buffering**: Absorb traffic spikes by buffering requests for controlled processing
4. **Event-Driven Architectures**: Build event-driven systems with SQS as the message backbone
5. **Order Processing Systems**: Use FIFO queues to maintain strict ordering for e-commerce transactions
6. **Serverless Application Integration**: Connect Lambda functions with SQS for scalable event processing
7. **Fault-Tolerant Message Handling**: Capture failed messages in DLQ for analysis and reprocessing
8. **System Decoupling**: Isolate application components to prevent cascading failures

## Submodules

### 1. wrappers

- **Purpose**: Manage multiple SQS queue instances using the single module wrapper pattern
- **Source**: `terraform-aws-modules/sqs/aws//modules/wrapper`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/sqs/aws/latest/submodules/wrapper
- **Key Features**: Bulk queue creation with shared defaults, useful for Terragrunt configurations
- **Use Cases**: Multi-environment deployments, managing multiple related queues with consistent settings

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create SQS queue |
| `name` | `string` | `null` | Queue name (auto-generated if omitted) |
| `use_name_prefix` | `bool` | `false` | Use name as prefix for unique naming |
| `fifo_queue` | `bool` | `false` | Create FIFO queue (auto-adds `.fifo` suffix) |
| `content_based_deduplication` | `bool` | `null` | Enable content-based deduplication for FIFO queues |
| `visibility_timeout_seconds` | `number` | `null` | Visibility timeout (0-43,200 seconds) |
| `message_retention_seconds` | `number` | `null` | Message retention (60-1,209,600 seconds, default 4 days) |
| `delay_seconds` | `number` | `null` | Message delivery delay (0-900 seconds) |
| `receive_wait_time_seconds` | `number` | `null` | Long polling wait time (0-20 seconds) |
| `max_message_size` | `number` | `null` | Max message size (1,024-262,144 bytes) |
| `sqs_managed_sse_enabled` | `bool` | `true` | Enable SSE with SQS-owned keys |
| `kms_master_key_id` | `string` | `null` | KMS key ID for encryption (overrides SSE-SQS) |
| `kms_data_key_reuse_period_seconds` | `number` | `null` | KMS key reuse period (60-86,400 seconds) |
| `create_dlq` | `bool` | `false` | Create Dead Letter Queue |
| `redrive_policy` | `any` | `{}` | DLQ redrive policy with `maxReceiveCount` |
| `create_queue_policy` | `bool` | `false` | Create IAM queue policy |
| `queue_policy_statements` | `map(object)` | `null` | Custom IAM policy statements |
| `tags` | `map(string)` | `{}` | Resource tags |

## Main Outputs

| Output | Description |
|--------|-------------|
| `queue_id` | The URL of the SQS queue |
| `queue_url` | The URL of the SQS queue (alias) |
| `queue_arn` | The ARN of the SQS queue |
| `queue_arn_static` | Static ARN (use for Step Functions to avoid cycles) |
| `queue_name` | The name of the SQS queue |
| `dead_letter_queue_id` | The URL of the DLQ |
| `dead_letter_queue_url` | The URL of the DLQ (alias) |
| `dead_letter_queue_arn` | The ARN of the DLQ |
| `dead_letter_queue_arn_static` | Static DLQ ARN (use for Step Functions) |
| `dead_letter_queue_name` | The name of the DLQ |

## Usage Examples

### Example 1: Basic Standard Queue

```hcl
module "sqs" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "~> 5.2"

  name = "my-application-queue"

  tags = {
    Environment = "production"
    Application = "order-service"
  }
}
```

### Example 2: FIFO Queue with Dead Letter Queue

```hcl
module "fifo_queue" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "~> 5.2"

  name       = "orders-processing"  # .fifo suffix added automatically
  fifo_queue = true

  # Enable content-based deduplication
  content_based_deduplication = true

  # Create DLQ with redrive policy
  create_dlq = true
  redrive_policy = {
    maxReceiveCount = 5  # Must be integer, not string
  }

  # Configure visibility timeout (6x expected processing time)
  visibility_timeout_seconds = 300

  tags = {
    Environment = "production"
    QueueType   = "fifo"
  }
}
```

### Example 3: Encrypted Queue with KMS

```hcl
# Create KMS key for SQS encryption
resource "aws_kms_key" "sqs" {
  description             = "KMS key for SQS encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

module "encrypted_queue" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "~> 5.2"

  name = "sensitive-data-queue"

  # Enable KMS encryption (disables SSE-SQS)
  kms_master_key_id                 = aws_kms_key.sqs.id
  kms_data_key_reuse_period_seconds = 3600

  # Queue configuration
  message_retention_seconds  = 1209600  # 14 days
  visibility_timeout_seconds = 300
  receive_wait_time_seconds  = 20  # Enable long polling

  # Create DLQ with same encryption
  create_dlq            = true
  dlq_kms_master_key_id = aws_kms_key.sqs.id
  redrive_policy = {
    maxReceiveCount = 3
  }

  tags = {
    Environment   = "production"
    SecurityLevel = "high"
    Encryption    = "kms-cmk"
  }
}

output "queue_url" {
  value = module.encrypted_queue.queue_url
}

output "queue_arn" {
  value = module.encrypted_queue.queue_arn
}
```

### Example 4: Queue with IAM Policy (Cross-Account/SNS)

```hcl
data "aws_caller_identity" "current" {}

module "queue_with_policy" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "~> 5.2"

  name = "cross-account-queue"

  # Enable queue policy
  create_queue_policy = true
  queue_policy_statements = {
    # Allow cross-account access
    cross_account_send = {
      sid     = "AllowCrossAccountSend"
      actions = ["sqs:SendMessage"]
      principals = [
        {
          type        = "AWS"
          identifiers = ["arn:aws:iam::123456789012:root"]
        }
      ]
    }

    # Allow SNS to publish
    sns_publish = {
      sid     = "AllowSNSPublish"
      actions = ["sqs:SendMessage"]
      principals = [
        {
          type        = "Service"
          identifiers = ["sns.amazonaws.com"]
        }
      ]
      conditions = [
        {
          test     = "ArnEquals"
          variable = "aws:SourceArn"
          values   = ["arn:aws:sns:us-east-1:${data.aws_caller_identity.current.account_id}:my-topic"]
        }
      ]
    }
  }

  tags = {
    Environment = "production"
    Integration = "cross-account"
  }
}
```

### Example 5: High-Throughput Queue with Long Polling

```hcl
module "high_throughput_queue" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "~> 5.2"

  name = "high-volume-events"

  # Optimize for throughput
  visibility_timeout_seconds = 30
  message_retention_seconds  = 345600  # 4 days
  receive_wait_time_seconds  = 20      # Long polling (cost savings)
  delay_seconds              = 0       # No delivery delay
  max_message_size           = 262144  # 256 KB

  # Use SSE-SQS (lower latency than KMS)
  sqs_managed_sse_enabled = true

  # DLQ for failed messages
  create_dlq = true
  redrive_policy = {
    maxReceiveCount = 10
  }

  tags = {
    Environment = "production"
    Throughput  = "high"
  }
}
```

### Example 6: Queue for Step Functions (Static ARN)

```hcl
module "step_function_queue" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "~> 5.2"

  name = "step-function-tasks"

  visibility_timeout_seconds = 600

  create_dlq = true
  redrive_policy = {
    maxReceiveCount = 3
  }

  tags = {
    Environment = "production"
    Integration = "step-functions"
  }
}

# Use static ARN to prevent circular dependency
resource "aws_sfn_state_machine" "example" {
  name     = "example-state-machine"
  role_arn = aws_iam_role.step_function.arn

  definition = jsonencode({
    StartAt = "SendToQueue"
    States = {
      SendToQueue = {
        Type     = "Task"
        Resource = "arn:aws:states:::sqs:sendMessage"
        Parameters = {
          QueueUrl    = module.step_function_queue.queue_url
          MessageBody = "$.input"
        }
        End = true
      }
    }
  })
}

# Use queue_arn_static in IAM policy to avoid cycles
data "aws_iam_policy_document" "step_function" {
  statement {
    actions   = ["sqs:SendMessage"]
    resources = [module.step_function_queue.queue_arn_static]
  }
}
```

## Best Practices

### Queue Design

1. **Choose Queue Type Wisely**: Use standard queues for maximum throughput; use FIFO only when strict ordering and exactly-once processing are required
2. **Always Configure DLQ**: Set `create_dlq = true` with appropriate `maxReceiveCount` (typically 3-10) to capture failed messages
3. **Design for Idempotency**: Standard queues may deliver messages more than once; ensure consumers handle duplicates
4. **Use Separate Queues**: Create dedicated queues for different message types or priorities

### Configuration

1. **Set Visibility Timeout**: Configure to at least 6x expected processing time to prevent duplicate processing
2. **Enable Long Polling**: Set `receive_wait_time_seconds = 20` to reduce empty responses and costs
3. **FIFO Queue Naming**: Do not include `.fifo` suffix in name; module adds it automatically
4. **maxReceiveCount Type**: Must be integer in `redrive_policy`, not string

### Security

1. **Encryption Enabled by Default**: SSE-SQS is enabled by default; no action needed for basic encryption
2. **Use KMS for Compliance**: Switch to KMS encryption when audit trails or key rotation policies are required
3. **Explicit Queue Policies**: Set `create_queue_policy = true` only when cross-account access or specific IAM restrictions needed
4. **Use VPC Endpoints**: Access SQS through VPC endpoints to keep traffic within AWS network

### Performance

1. **Use Batch Operations**: Send/receive up to 10 messages per request to reduce API calls
2. **Configure KMS Reuse**: Set `kms_data_key_reuse_period_seconds = 300-3600` to reduce KMS API calls when using KMS encryption
3. **Monitor Queue Depth**: Track ApproximateNumberOfMessagesVisible to detect processing bottlenecks

### Integration

1. **Static ARNs for Step Functions**: Use `queue_arn_static` and `dead_letter_queue_arn_static` outputs to prevent circular dependencies
2. **Fan-Out with SNS**: Use SNS topics to fan out messages to multiple SQS queues
3. **Lambda Event Source**: Configure Lambda event source mappings with appropriate batch size and concurrency

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-sqs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/sqs/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-sqs/tree/master/examples
- **AWS SQS Documentation**: https://docs.aws.amazon.com/sqs/
- **SQS Developer Guide**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html
- **SQS FIFO Queues**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues.html
- **SQS Dead Letter Queues**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html
- **SQS Best Practices**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-best-practices.html
- **Lambda with SQS**: https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
- **SQS Pricing**: https://aws.amazon.com/sqs/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Version**: Use `version = "~> 5.2"` for latest stable features
2. **Queue Type**: Set `fifo_queue = true` only when strict ordering required; standard queues offer higher throughput
3. **FIFO Naming**: Do NOT include `.fifo` in name variable; module adds suffix automatically
4. **DLQ Setup**: Always set `create_dlq = true` with `redrive_policy = { maxReceiveCount = 5 }` (integer, not string)
5. **Encryption Default**: SSE-SQS is enabled by default; set `kms_master_key_id` only for compliance requirements
6. **Long Polling**: Always set `receive_wait_time_seconds = 20` to reduce costs
7. **Visibility Timeout**: Set to 6x expected processing time (e.g., 300 for 50-second processing)
8. **Static ARN**: Use `queue_arn_static` output when referencing in Step Functions or IAM policies to avoid circular dependencies
9. **Queue Policy**: Only set `create_queue_policy = true` when cross-account access or SNS integration needed
10. **Tags**: Apply consistent tags including `Environment`, `Application`, `Owner` for governance
11. **DLQ Encryption**: DLQ inherits encryption settings; use `dlq_kms_master_key_id` to override
12. **Message Retention**: Default is 4 days; set `message_retention_seconds = 1209600` for 14 days max
