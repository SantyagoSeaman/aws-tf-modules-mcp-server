# Terraform AWS SQS Module

## Module Information

- **Module Name**: `sqs`
- **Source**: `terraform-aws-modules/sqs/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-sqs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/sqs/aws/latest
- **Latest Version**: 5.0.0
- **Purpose**: Terraform module that creates and manages Amazon SQS (Simple Queue Service) queues with support for standard and FIFO queues, dead letter queues, and encryption
- **Service**: AWS SQS (Simple Queue Service)
- **Category**: Messaging, Integration, Application Services
- **Keywords**: sqs, simple-queue-service, queue, message-queue, messaging, fifo-queue, standard-queue, dead-letter-queue, dlq, message-broker, async-processing, event-driven, decoupling, microservices, kms-encryption, server-side-encryption, content-based-deduplication, redrive-policy, long-polling, message-ordering, distributed-systems, fault-tolerance
- **Use For**: Asynchronous microservices communication, decoupling application components, task queue management, batch job processing, event-driven architectures, message buffering and throttling, order processing systems, serverless application integration, distributed system coordination, handling traffic spikes, background job processing, reliable message delivery

## Description

The Terraform AWS SQS module provides a complete solution for creating and managing Amazon Simple Queue Service (SQS) queues with comprehensive configuration options. Amazon SQS is a fully managed message queuing service that enables asynchronous communication between distributed application components, providing reliable, scalable, and cost-effective message delivery. The module supports both standard queues (offering maximum throughput and at-least-once delivery) and FIFO queues (providing exactly-once processing and strict message ordering).

This module simplifies SQS queue management by providing an infrastructure-as-code approach to configuring queue attributes, encryption settings, access policies, and integration with other AWS services. It handles the complexity of dead letter queue configuration, enabling automatic handling of message processing failures by routing problematic messages to a separate queue for analysis and reprocessing. The module supports multiple encryption options including AWS-managed keys (SSE-SQS) and customer-managed KMS keys for enhanced security and compliance requirements.

The module enables advanced features such as content-based deduplication for FIFO queues, configurable visibility timeouts to prevent duplicate processing, message delay capabilities for scheduled delivery, and long polling to reduce costs and latency. It integrates seamlessly with other AWS services including Lambda for serverless processing, SNS for fan-out messaging patterns, and EventBridge for event-driven architectures, making it an essential component for building resilient and scalable distributed systems.

## Key Features

- **Standard Queue Support**: Create high-throughput standard queues with at-least-once delivery and best-effort ordering
- **FIFO Queue Support**: Enable FIFO (First-In-First-Out) queues for exactly-once processing and strict message ordering
- **Dead Letter Queue (DLQ)**: Automatically create and configure dead letter queues for handling message processing failures
- **KMS Encryption**: Secure messages at rest using AWS KMS with customer-managed or AWS-managed encryption keys
- **Server-Side Encryption**: Enable SQS-managed server-side encryption (SSE-SQS) for simplified encryption management
- **Content-Based Deduplication**: Automatically deduplicate FIFO queue messages based on message content hash
- **Custom Deduplication Scope**: Configure deduplication at message group or queue level for FIFO queues
- **Visibility Timeout**: Control message visibility duration to prevent duplicate processing during message handling
- **Message Retention**: Configure message retention period from 60 seconds to 14 days
- **Long Polling**: Enable long polling to reduce costs and eliminate empty responses
- **Message Delay**: Set delivery delay for messages from 0 to 15 minutes for scheduled processing
- **Redrive Policy**: Configure automatic message redrive from DLQ back to source queue after troubleshooting
- **Queue Policies**: Create custom IAM resource policies for fine-grained access control
- **Maximum Message Size**: Configure maximum message size up to 256 KB
- **Receive Wait Time**: Set long polling duration for receive message requests
- **KMS Data Key Reuse**: Configure KMS data key reuse period to optimize encryption performance
- **Flexible Tagging**: Comprehensive tag support for cost allocation and resource organization
- **Conditional Resource Creation**: Control queue and DLQ creation with boolean flags for environment-specific deployments
- **Name Prefix Support**: Use name prefixes for dynamic queue naming in multi-environment deployments
- **CloudWatch Integration**: Native integration with CloudWatch for queue metrics and monitoring

## Main Use Cases

1. **Asynchronous Microservices Communication**: Decouple microservices by using queues for non-blocking inter-service communication
2. **Background Job Processing**: Queue long-running tasks for asynchronous processing by worker services or Lambda functions
3. **Load Leveling and Traffic Buffering**: Absorb traffic spikes by buffering requests in queues for controlled processing
4. **Event-Driven Architectures**: Build event-driven systems with SQS as the message backbone for event distribution
5. **Order Processing Systems**: Use FIFO queues to maintain strict ordering for e-commerce transactions and order fulfillment
6. **Batch Job Coordination**: Coordinate distributed batch processing jobs across multiple workers with message queues
7. **Serverless Application Integration**: Integrate Lambda functions with SQS for scalable serverless event processing
8. **Fault-Tolerant Message Handling**: Use dead letter queues to capture and analyze failed messages for improved reliability
9. **Priority Task Management**: Separate high-priority and low-priority tasks using multiple queues with different processing logic
10. **System Decoupling and Resilience**: Isolate application components to prevent cascading failures and improve system resilience

## Best Practices

### Queue Design and Architecture

1. **Choose the Right Queue Type**: Use standard queues for maximum throughput and FIFO queues only when strict ordering and exactly-once processing are required
2. **Implement Dead Letter Queues**: Always configure DLQs to capture failed messages and prevent message loss during processing errors
3. **Set Appropriate maxReceiveCount**: Configure maxReceiveCount between 3-10 based on expected transient failures to balance retry attempts with DLQ routing
4. **Use Separate Queues for Different Workloads**: Create dedicated queues for different message types or priorities rather than mixing them in a single queue
5. **Design for Idempotency**: Ensure message consumers are idempotent since standard queues may deliver messages more than once

### Message Configuration

1. **Optimize Visibility Timeout**: Set visibility timeout to at least 6 times the expected processing time to prevent duplicate processing
2. **Configure Appropriate Message Retention**: Use shorter retention (1-4 days) for time-sensitive data and longer retention (7-14 days) for audit trails
3. **Enable Long Polling**: Set receive_wait_time_seconds to 20 seconds to reduce empty responses and lower costs
4. **Keep Messages Small**: Keep message size under 256 KB; use S3 for larger payloads and include S3 references in SQS messages
5. **Use Message Attributes Wisely**: Leverage message attributes for metadata and filtering rather than parsing message body

### FIFO Queue Configuration

1. **Enable Content-Based Deduplication**: Use content-based deduplication for FIFO queues to automatically prevent duplicate messages
2. **Design Message Group IDs Carefully**: Use granular message group IDs to maximize parallelism while maintaining required ordering
3. **Set Deduplication Scope Appropriately**: Use message group-level deduplication for higher throughput when ordering is only needed within groups
4. **Understand Throughput Limits**: FIFO queues support 300 messages/second (3000 with batching); use standard queues for higher throughput needs
5. **Use .fifo Suffix**: Always append .fifo to FIFO queue names as required by AWS

### Security and Encryption

1. **Enable Encryption at Rest**: Always enable encryption for queues containing sensitive data using KMS or SSE-SQS
2. **Use Customer-Managed KMS Keys**: Use CMKs for sensitive workloads requiring key rotation policies and detailed access logging
3. **Implement Least Privilege Policies**: Create restrictive queue policies that grant minimum necessary permissions to specific principals
4. **Rotate KMS Keys Regularly**: Enable automatic key rotation for customer-managed KMS keys used for SQS encryption
5. **Audit Queue Access**: Enable CloudTrail logging for SQS API calls to monitor queue access and detect unauthorized activity
6. **Secure Queue URLs**: Treat queue URLs as sensitive information; avoid exposing them in logs or client-side code
7. **Use VPC Endpoints**: Access SQS through VPC endpoints to keep traffic within AWS network and avoid internet exposure

### Dead Letter Queue Management

1. **Monitor DLQ Depth**: Set CloudWatch alarms on DLQ message count to alert on processing failures
2. **Set Up DLQ Redrive**: Use redrive policies to automatically move messages back to source queue after fixing issues
3. **Analyze DLQ Messages**: Regularly review DLQ messages to identify and fix recurring processing errors
4. **Configure DLQ Retention**: Set longer retention on DLQs (14 days) to ensure adequate time for troubleshooting
5. **Use Same Encryption for DLQ**: Apply the same encryption settings to DLQs as source queues for consistent security

### Performance Optimization

1. **Use Batch Operations**: Use batch send and receive operations to reduce API calls and improve throughput
2. **Optimize Polling Strategy**: Use long polling to reduce empty responses and lower costs compared to short polling
3. **Configure KMS Data Key Reuse**: Set kms_data_key_reuse_period_seconds to 300-3600 seconds to reduce KMS API calls
4. **Implement Parallel Processing**: Scale message consumers horizontally to process messages in parallel
5. **Monitor Queue Metrics**: Track ApproximateAgeOfOldestMessage and ApproximateNumberOfMessagesVisible to detect processing bottlenecks

### Cost Optimization

1. **Use Long Polling**: Enable long polling to reduce the number of empty ReceiveMessage responses and lower costs
2. **Batch Messages**: Use batch operations to process up to 10 messages per request and reduce API call costs
3. **Set Appropriate Retention**: Use shorter retention periods when possible to reduce storage costs
4. **Choose Standard Over FIFO**: Use standard queues unless strict ordering is required; FIFO queues have different pricing
5. **Monitor Queue Depth**: Set alarms for excessive queue depth indicating underutilized consumers or processing issues

### Operational Excellence

1. **Implement Comprehensive Tagging**: Tag queues with environment, application, cost-center, and owner for organization and cost tracking
2. **Use Infrastructure as Code**: Always manage SQS queues through Terraform for version control and reproducible deployments
3. **Document Queue Purpose**: Use clear naming conventions and tags to document each queue's purpose and message schema
4. **Test DLQ Workflows**: Regularly test dead letter queue handling and redrive processes in non-production environments
5. **Implement Message Tracing**: Use message attributes or correlation IDs to trace messages through distributed systems

### Monitoring and Observability

1. **Set Up CloudWatch Alarms**: Create alarms for queue depth, age of oldest message, and DLQ message count
2. **Monitor Message Processing Time**: Track visibility timeout expirations to identify slow or failing consumers
3. **Enable CloudWatch Metrics**: Monitor SQS metrics including NumberOfMessagesSent, NumberOfMessagesReceived, and ApproximateNumberOfMessagesVisible
4. **Log Processing Failures**: Log detailed error information when messages fail processing to aid in troubleshooting
5. **Implement Health Checks**: Create health check endpoints for queue consumers that verify SQS connectivity and processing capability

### Integration Patterns

1. **Fan-Out with SNS**: Use SNS topics to fan out messages to multiple SQS queues for parallel processing
2. **Lambda Event Source Mapping**: Configure Lambda event source mappings with appropriate batch size and concurrency limits
3. **Implement Circuit Breakers**: Add circuit breaker patterns around SQS consumers to prevent cascade failures
4. **Use SQS as Event Source**: Leverage SQS as a reliable event source for EventBridge, Lambda, and ECS/Fargate applications
5. **Combine with Step Functions**: Use SQS with Step Functions for complex workflow orchestration and error handling

### High Availability and Disaster Recovery

1. **SQS is Multi-AZ by Default**: Understand that SQS queues are automatically replicated across multiple availability zones
2. **Plan for Regional Failures**: For critical workloads, consider cross-region message replication strategies
3. **Backup Queue Configurations**: Store queue configurations in version-controlled Terraform code for rapid recovery
4. **Test Failure Scenarios**: Regularly test queue failover and recovery procedures in non-production environments
5. **Document Recovery Procedures**: Maintain runbooks for queue recovery and DLQ message reprocessing

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-sqs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/sqs/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-sqs/tree/master/examples
- **AWS SQS Documentation**: https://docs.aws.amazon.com/sqs/
- **SQS Developer Guide**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html
- **SQS FIFO Queues**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues.html
- **SQS Dead Letter Queues**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html
- **SQS Encryption**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-server-side-encryption.html
- **SQS Best Practices**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-best-practices.html
- **SQS API Reference**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/Welcome.html
- **SQS Pricing**: https://aws.amazon.com/sqs/pricing/
- **Lambda with SQS**: https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
- **CloudWatch Metrics for SQS**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-monitoring-using-cloudwatch.html
- **SQS Message Attributes**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-message-metadata.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Queue Type Selection**: Choose `fifo_queue = true` only when strict ordering and exactly-once processing are required; standard queues offer higher throughput
2. **DLQ Configuration**: Always set `create_dlq = true` with appropriate `maxReceiveCount` (typically 3-10) to handle message processing failures
3. **Encryption Decision**: Enable encryption by setting `kms_master_key_id` for sensitive data; use `null` (default SSE-SQS) for non-sensitive workloads
4. **Naming Convention**: For FIFO queues, ensure queue name ends with `.fifo` suffix; use descriptive names reflecting message purpose
5. **Visibility Timeout**: Set `visibility_timeout_seconds` to at least 6x expected processing time to prevent duplicate processing
6. **Message Retention**: Configure `message_retention_seconds` based on data sensitivity and compliance requirements (default 345600 = 4 days)
7. **Long Polling**: Always set `receive_wait_time_seconds = 20` to enable long polling and reduce costs
8. **FIFO Deduplication**: For FIFO queues, enable `content_based_deduplication = true` unless using custom deduplication IDs
9. **KMS Performance**: Set `kms_data_key_reuse_period_seconds = 300` to balance security and performance when using KMS encryption
10. **Queue Policy**: Only create queue policies when cross-account access or specific IAM restrictions are needed
11. **Tagging Strategy**: Apply consistent tags including `Environment`, `Application`, `Owner`, and `CostCenter` for governance
12. **Validate Before Apply**: Verify queue configuration in staging before production deployment, especially for FIFO queues

## Usage Examples

### Example 1: Basic Standard Queue

```hcl
module "basic_queue" {
  source = "terraform-aws-modules/sqs/aws"

  name = "basic-standard-queue"

  tags = {
    Environment = "production"
    Application = "order-processing"
  }
}
```

### Example 2: FIFO Queue with Dead Letter Queue

```hcl
module "fifo_queue" {
  source = "terraform-aws-modules/sqs/aws"

  name       = "orders-processing-queue.fifo"
  fifo_queue = true

  # Enable content-based deduplication
  content_based_deduplication = true

  # Create dead letter queue
  create_dlq = true
  redrive_policy = {
    maxReceiveCount = 5
  }

  # Configure visibility timeout for processing
  visibility_timeout_seconds = 300

  tags = {
    Environment = "production"
    Application = "order-processing"
    QueueType   = "fifo"
  }
}
```

### Example 3: Encrypted Queue with Customer-Managed KMS Key

```hcl
# Create KMS key for SQS encryption
resource "aws_kms_key" "sqs" {
  description             = "KMS key for SQS encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_alias" "sqs" {
  name          = "alias/sqs-queue-key"
  target_key_id = aws_kms_key.sqs.key_id
}

module "encrypted_queue" {
  source = "terraform-aws-modules/sqs/aws"

  name = "encrypted-sensitive-queue"

  # Enable KMS encryption
  kms_master_key_id                 = aws_kms_key.sqs.id
  kms_data_key_reuse_period_seconds = 3600

  # Configure queue attributes
  message_retention_seconds = 1209600  # 14 days
  visibility_timeout_seconds = 300

  # Enable long polling
  receive_wait_time_seconds = 20

  # Create DLQ
  create_dlq = true
  redrive_policy = {
    maxReceiveCount = 3
  }

  tags = {
    Environment     = "production"
    Application     = "payment-processing"
    SecurityLevel   = "high"
    Encryption      = "kms-cmk"
  }
}

# Output queue information
output "queue_url" {
  description = "URL of the encrypted SQS queue"
  value       = module.encrypted_queue.queue_url
}

output "queue_arn" {
  description = "ARN of the encrypted SQS queue"
  value       = module.encrypted_queue.queue_arn
}

output "dlq_url" {
  description = "URL of the dead letter queue"
  value       = module.encrypted_queue.dead_letter_queue_url
}
```

### Example 4: Queue with Custom Policy

```hcl
data "aws_caller_identity" "current" {}

module "queue_with_policy" {
  source = "terraform-aws-modules/sqs/aws"

  name = "cross-account-queue"

  # Enable queue policy creation
  create_queue_policy = true
  queue_policy_statements = {
    allow_cross_account = {
      sid     = "AllowCrossAccountSend"
      actions = ["sqs:SendMessage"]

      principals = [
        {
          type        = "AWS"
          identifiers = ["arn:aws:iam::123456789012:root"]
        }
      ]
    }

    allow_sns_publish = {
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
    Application = "cross-account-integration"
  }
}
```

### Example 5: High-Throughput Standard Queue with Optimized Settings

```hcl
module "high_throughput_queue" {
  source = "terraform-aws-modules/sqs/aws"

  name = "high-volume-events-queue"

  # Optimize for high throughput
  visibility_timeout_seconds = 30
  message_retention_seconds  = 345600  # 4 days
  receive_wait_time_seconds  = 20      # Enable long polling
  delay_seconds              = 0        # No delivery delay

  # Maximum message size
  max_message_size = 262144  # 256 KB

  # Create DLQ for failed messages
  create_dlq = true
  redrive_policy = {
    maxReceiveCount = 10
  }

  # Use SSE-SQS for encryption (lower latency than KMS)
  sqs_managed_sse_enabled = true

  tags = {
    Environment = "production"
    Application = "event-processing"
    Throughput  = "high"
  }
}
```

### Example 6: Delayed Message Processing Queue

```hcl
module "delayed_queue" {
  source = "terraform-aws-modules/sqs/aws"

  name = "scheduled-notifications-queue"

  # Set default delay for all messages
  delay_seconds = 900  # 15 minutes delay

  # Configure retention and visibility
  message_retention_seconds  = 604800  # 7 days
  visibility_timeout_seconds = 600

  # Enable long polling
  receive_wait_time_seconds = 20

  tags = {
    Environment = "production"
    Application = "notification-service"
    Purpose     = "delayed-delivery"
  }
}
```
