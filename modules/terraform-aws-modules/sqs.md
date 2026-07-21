# Terraform AWS SQS Module

## Module Information

- **Module Name**: `sqs`
- **Module ID**: `terraform-aws-modules/sqs/aws`
- **Source**: `terraform-aws-modules/sqs/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-sqs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/sqs/aws/latest
- **Latest Version**: 5.2.2
- **Purpose**: Creates and manages Amazon SQS standard and FIFO queues, including an optional companion dead-letter queue, KMS/SSE encryption, and IAM queue policies
- **Service**: AWS SQS (Simple Queue Service)
- **Category**: Messaging, Integration, Application Services
- **Keywords**: sqs, queue, message-queue, fifo-queue, dead-letter-queue, dlq, redrive-policy, kms-encryption, sse, async-processing, event-driven, microservices, serverless, lambda-trigger, queue-policy
- **Use For**: asynchronous microservices communication, decoupling application components, background/batch job processing, event-driven architectures, message buffering and load leveling, order processing with FIFO ordering, serverless (Lambda/SNS/EventBridge) integration, fault-tolerant message handling via DLQ

## Description

The Terraform AWS SQS module creates and configures Amazon Simple Queue Service (SQS) queues, the fully managed message-queuing service used for asynchronous, decoupled communication between distributed application components. A single module call manages one `aws_sqs_queue` (standard or FIFO), and can optionally provision a paired dead-letter queue (DLQ), IAM queue policies for both the primary queue and the DLQ, and redrive/redrive-allow policies — all with sane, production-ready defaults.

Encryption is server-side by default using SQS-owned keys (SSE-SQS), with an easy switch to a customer-managed KMS key (CMK) via `kms_master_key_id`. The module exposes fine-grained control over queue behavior (visibility timeout, message retention, delivery delay, long polling, max message size, FIFO deduplication/throughput scope) and lets every DLQ attribute be overridden independently of the source queue via `dlq_*` variables (falling back to the source queue's value when unset). Queue and DLQ IAM policies are built from a structured `queue_policy_statements` / `dlq_queue_policy_statements` map (compiled with `aws_iam_policy_document`), avoiding hand-written JSON.

The module also emits static ARN outputs (`queue_arn_static`, `dead_letter_queue_arn_static`) computed from account ID/partition/region rather than the resource attribute, specifically to avoid Terraform cycle errors when a queue ARN is referenced by a resource that the queue policy also depends on (e.g., Step Functions state machines). A `wrappers` submodule is included for creating many queues from one `for_each`-style block, primarily for Terragrunt-driven, multi-instance deployments.

## Key Features

- **Standard & FIFO Queues**: `fifo_queue = true` creates a FIFO queue with exactly-once processing and strict ordering; the module auto-appends the `.fifo` suffix to the name
- **Dead Letter Queue (DLQ)**: `create_dlq = true` provisions a matching DLQ and wires up the redrive policy automatically (default `maxReceiveCount = 5` if not overridden)
- **Independent DLQ Tuning**: Any `dlq_*` variable (retention, visibility timeout, KMS key, SSE, FIFO throughput, tags, etc.) overrides the corresponding source-queue setting just for the DLQ
- **Redrive Allow Policy**: `create_dlq_redrive_allow_policy` (default `true`) automatically restricts the DLQ's redrive permission to only the source queue (`redrivePermission = "byQueue"`)
- **SSE / KMS Encryption**: SQS-managed SSE is enabled by default (`sqs_managed_sse_enabled = true`); setting `kms_master_key_id` switches the queue to customer-managed KMS encryption (SSE is automatically disabled when a KMS key is set)
- **Structured IAM Queue Policies**: `queue_policy_statements` / `dlq_queue_policy_statements` build policies via `aws_iam_policy_document` with support for `source_queue_policy_documents` and `override_queue_policy_documents` merging
- **Static ARN Outputs**: `queue_arn_static` / `dead_letter_queue_arn_static` prevent circular dependencies (e.g., Step Functions referencing the queue in both a policy and a state machine definition)
- **Content-Based Deduplication & Scope**: FIFO-specific `content_based_deduplication`, `deduplication_scope`, and `fifo_throughput_limit` for high-throughput FIFO configurations
- **Long Polling**: `receive_wait_time_seconds` (0-20s) reduces empty-response API calls and cost
- **Flexible Naming**: Explicit `name`, or `use_name_prefix = true` to treat `name` as a prefix (note: FIFO queues cannot use a name prefix)
- **Conditional Creation**: `create`, `create_dlq`, `create_queue_policy`, `create_dlq_queue_policy` toggle each resource group independently
- **Multi-Region Provider Support**: `region` variable pins the resources to a specific AWS region independent of the default provider region
- **Comprehensive Tagging**: `tags` applied to the queue; `dlq_tags` merged on top for the DLQ

## Main Use Cases

1. **Asynchronous Microservices Communication**: Decouple services using queues for non-blocking inter-service messaging
2. **Background Job Processing**: Queue long-running tasks for asynchronous processing by workers or Lambda
3. **Load Leveling and Traffic Buffering**: Absorb traffic spikes by buffering requests for controlled downstream processing
4. **Event-Driven Architectures**: Use SQS as the message backbone between producers and consumers
5. **Order Processing Systems**: Use FIFO queues with content-based deduplication to preserve strict ordering
6. **Serverless Application Integration**: Trigger Lambda functions from SQS, or fan out from SNS/EventBridge into SQS
7. **Fault-Tolerant Message Handling**: Route failed/unprocessable messages to a DLQ for analysis and reprocessing
8. **Cross-Account/Service Messaging**: Grant scoped `sqs:SendMessage`/`sqs:ReceiveMessage` access via queue policies (e.g., allowing SNS or another AWS account to publish)

## Submodules

### 1. wrappers

- **Purpose**: Create and manage multiple SQS queue instances from a single module block using the `for_each`-over-map wrapper pattern
- **Source**: `terraform-aws-modules/sqs/aws//wrappers`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/sqs/aws/latest/submodules/wrappers
- **Key Features**: Accepts `defaults` (shared config applied to every item) and `items` (map of per-queue overrides); adds no functionality beyond the root module, purely a `for_each` shim
- **Use Cases**: Terragrunt configurations that cannot use native `for_each`, managing many similarly-configured queues (e.g., one per tenant/environment) from one config block

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the SQS queue (and dependent resources) |
| `name` | `string` | `null` | Queue name; Terraform assigns a random name if omitted |
| `use_name_prefix` | `bool` | `false` | Treat `name` as a prefix instead of an exact name (not usable with FIFO queues) |
| `fifo_queue` | `bool` | `false` | Create a FIFO queue; `.fifo` suffix is added automatically |
| `content_based_deduplication` | `bool` | `null` | Enable content-based deduplication for FIFO queues |
| `deduplication_scope` | `string` | `null` | FIFO dedup scope: `messageGroup` or `queue` |
| `fifo_throughput_limit` | `string` | `null` | FIFO throughput quota scope: `perQueue` or `perMessageGroupId` |
| `visibility_timeout_seconds` | `number` | `null` | Visibility timeout (0-43,200 seconds) |
| `message_retention_seconds` | `number` | `null` | Message retention (60-1,209,600 seconds; AWS default 4 days) |
| `delay_seconds` | `number` | `null` | Message delivery delay (0-900 seconds) |
| `receive_wait_time_seconds` | `number` | `null` | Long-polling wait time (0-20 seconds) |
| `max_message_size` | `number` | `null` | Max message size (1,024-262,144 bytes) |
| `sqs_managed_sse_enabled` | `bool` | `true` | Enable SSE with SQS-owned keys (ignored/overridden if `kms_master_key_id` is set) |
| `kms_master_key_id` | `string` | `null` | KMS key ID/ARN for encryption; setting this disables SSE-SQS |
| `kms_data_key_reuse_period_seconds` | `number` | `null` | KMS data key reuse period (60-86,400 seconds) |
| `create_dlq` | `bool` | `false` | Create a companion dead-letter queue and wire up its redrive policy |
| `redrive_policy` | `any` | `{}` | Redrive policy merged over the auto-generated default (`maxReceiveCount = 5`); `maxReceiveCount` must be an integer |
| `create_dlq_redrive_allow_policy` | `bool` | `true` | Create a redrive-allow policy scoping the DLQ to only accept redrives from this source queue |
| `dlq_name`, `dlq_tags`, `dlq_kms_master_key_id`, `dlq_visibility_timeout_seconds`, `dlq_message_retention_seconds`, etc. | various | `null` | Per-attribute overrides for the DLQ; each falls back to the matching source-queue value (e.g. `visibility_timeout_seconds`) when unset |
| `create_queue_policy` / `create_dlq_queue_policy` | `bool` | `false` | Create an IAM queue policy for the primary queue / DLQ |
| `queue_policy_statements` / `dlq_queue_policy_statements` | `map(object)` | `null` | Structured IAM policy statements (sid, actions, principals, conditions) for the queue / DLQ — fields: `sid`, `actions`, `not_actions`, `effect`, `resources`, `not_resources`, `principals`, `not_principals`, … (8 shown; call get_module with sections=["inputs","outputs"] for the complete list) |
| `region` | `string` | `null` | AWS region for the resources; defaults to the provider's configured region |
| `tags` | `map(string)` | `{}` | Tags applied to the primary queue (and DLQ, merged with `dlq_tags`) |

## Main Outputs

| Output | Description |
|--------|-------------|
| `queue_id` / `queue_url` | The URL of the SQS queue (both are aliases of the same value) |
| `queue_arn` | The ARN of the SQS queue (resource attribute) |
| `queue_arn_static` | Statically computed ARN (account/partition/region + name); use to avoid dependency cycles, e.g. with Step Functions |
| `queue_name` | The name of the SQS queue |
| `dead_letter_queue_id` / `dead_letter_queue_url` | The URL of the DLQ |
| `dead_letter_queue_arn` | The ARN of the DLQ (resource attribute) |
| `dead_letter_queue_arn_static` | Statically computed DLQ ARN; same cycle-avoidance use case |
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

  # Create DLQ with redrive policy (default maxReceiveCount is 5 if omitted)
  create_dlq = true
  redrive_policy = {
    maxReceiveCount = 5  # must be an integer, not a string
  }

  # Configure visibility timeout (~6x expected processing time)
  visibility_timeout_seconds = 300

  tags = {
    Environment = "production"
    QueueType   = "fifo"
  }
}
```

### Example 3: Encrypted Queue with Customer-Managed KMS Key

```hcl
resource "aws_kms_key" "sqs" {
  description             = "KMS key for SQS encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

module "encrypted_queue" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "~> 5.2"

  name = "sensitive-data-queue"

  # Setting kms_master_key_id disables SSE-SQS automatically
  kms_master_key_id                 = aws_kms_key.sqs.key_id
  kms_data_key_reuse_period_seconds = 3600

  message_retention_seconds  = 1209600  # 14 days
  visibility_timeout_seconds = 300
  receive_wait_time_seconds  = 20       # long polling

  # DLQ inherits the same KMS key unless dlq_kms_master_key_id is set
  create_dlq = true
  redrive_policy = {
    maxReceiveCount = 3
  }

  tags = {
    Environment   = "production"
    SecurityLevel = "high"
  }
}
```

### Example 4: Cross-Account / SNS Queue Policy

```hcl
data "aws_caller_identity" "current" {}

module "queue_with_policy" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "~> 5.2"

  name = "cross-account-queue"

  create_queue_policy = true
  queue_policy_statements = {
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

    sns_publish = {
      sid     = "AllowSNSPublish"
      actions = ["sqs:SendMessage"]
      principals = [
        {
          type        = "Service"
          identifiers = ["sns.amazonaws.com"]
        }
      ]
      condition = [
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
  }
}
```

### Example 5: Queue Referenced by Step Functions (Static ARN)

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

# Use queue_arn_static in the IAM policy to avoid a dependency cycle
data "aws_iam_policy_document" "step_function" {
  statement {
    actions   = ["sqs:SendMessage"]
    resources = [module.step_function_queue.queue_arn_static]
  }
}
```

### Example 6: Multiple Queues via the `wrappers` Submodule

```hcl
module "sqs_queues" {
  source  = "terraform-aws-modules/sqs/aws//wrappers"
  version = "~> 5.2"

  defaults = {
    visibility_timeout_seconds = 60
    create_dlq                 = true
    redrive_policy = {
      maxReceiveCount = 5
    }
    tags = {
      Environment = "production"
    }
  }

  items = {
    orders = {
      name = "orders-queue"
    }
    notifications = {
      name                = "notifications-queue"
      fifo_queue          = true
      visibility_timeout_seconds = 120
    }
  }
}
```

## Best Practices

### Queue Design

1. **Choose Queue Type Wisely**: Use standard queues for maximum throughput; use FIFO only when strict ordering and exactly-once processing are required
2. **Always Configure a DLQ**: Set `create_dlq = true` with an explicit `maxReceiveCount` (typically 3-10) so failed messages are captured instead of retried forever or silently dropped
3. **Design for Idempotency**: Standard queues can deliver a message more than once; consumers must handle duplicates safely
4. **Use Separate Queues per Workload**: Create dedicated queues per message type/priority rather than multiplexing unrelated traffic on one queue

### Configuration

1. **Set Visibility Timeout Generously**: Configure it to roughly 6x the expected consumer processing time to avoid duplicate delivery while a message is still being processed
2. **Enable Long Polling**: Set `receive_wait_time_seconds = 20` to cut empty-response API calls and cost
3. **FIFO Naming**: Do not include `.fifo` in `name` — the module appends it automatically; also note FIFO queues cannot use `use_name_prefix`
4. **`maxReceiveCount` Type**: Must be a number in `redrive_policy` (e.g., `5`), not a string (`"5"`)

### Security

1. **Encryption Is On by Default**: SSE-SQS is enabled out of the box; no action is needed for baseline at-rest encryption
2. **Use a Customer-Managed KMS Key for Compliance**: Set `kms_master_key_id` when audit trails, key rotation policies, or cross-account key sharing are required; this automatically disables SSE-SQS
3. **Scope Queue Policies Narrowly**: Only set `create_queue_policy = true` when cross-account or cross-service (SNS/EventBridge) access is genuinely needed, and constrain principals/conditions as tightly as possible
4. **Prefer VPC Endpoints**: Access SQS through an interface VPC endpoint to keep traffic off the public internet

### Performance & Cost

1. **Batch Operations**: Send/receive up to 10 messages per API call to reduce request volume and cost
2. **Tune KMS Reuse Period**: Set `kms_data_key_reuse_period_seconds` in the 300-3600s range to reduce KMS API calls when using CMK encryption
3. **Monitor Queue Depth**: Track `ApproximateNumberOfMessagesVisible` (CloudWatch) to detect consumer bottlenecks or scaling needs

### Integration

1. **Static ARNs for Step Functions**: Use `queue_arn_static` / `dead_letter_queue_arn_static` instead of `queue_arn` when the ARN is needed by a resource (e.g., an IAM policy) that the queue itself also depends on, to avoid a Terraform dependency cycle
2. **Fan-Out with SNS**: Subscribe multiple SQS queues to one SNS topic for fan-out message delivery
3. **Lambda Event Source Mapping**: Pair the queue with a Lambda `aws_lambda_event_source_mapping`, tuning `batch_size` and reserved concurrency to match downstream capacity
4. **Multi-Queue Deployments**: Use the `wrappers` submodule (source `terraform-aws-modules/sqs/aws//wrappers`) when creating many similarly-shaped queues, especially from Terragrunt

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-sqs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/sqs/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-sqs/tree/master/examples/complete
- **Wrappers Submodule**: https://registry.terraform.io/modules/terraform-aws-modules/sqs/aws/latest/submodules/wrappers
- **AWS SQS Documentation**: https://docs.aws.amazon.com/sqs/
- **SQS Developer Guide**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html
- **SQS FIFO Queues**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues.html
- **SQS Dead Letter Queues**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html
- **SQS Best Practices**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-best-practices.html
- **Lambda with SQS**: https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
- **SQS Pricing**: https://aws.amazon.com/sqs/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Version Pin**: Use `version = "~> 5.2"`; v5.0 was a breaking change requiring Terraform >= 1.5.7 and AWS provider >= 6.0
2. **Queue Type**: Set `fifo_queue = true` only when strict ordering/exactly-once semantics are required; standard queues offer higher throughput
3. **FIFO Naming**: Do NOT include `.fifo` in `name` — the module appends it automatically, and FIFO queues cannot combine with `use_name_prefix`
4. **DLQ Setup**: Prefer `create_dlq = true` with `redrive_policy = { maxReceiveCount = 5 }` (integer, not string) for production queues; the module already defaults `maxReceiveCount` to 5 if `redrive_policy` is left empty
5. **Encryption Default**: SSE-SQS is enabled by default; set `kms_master_key_id` only when compliance/audit requirements call for a CMK (this disables SSE-SQS automatically, no need to also set `sqs_managed_sse_enabled = false`)
6. **Long Polling**: Set `receive_wait_time_seconds = 20` by default to reduce API costs, unless near-real-time short polling is explicitly required
7. **Visibility Timeout**: Set to roughly 6x the expected consumer processing time (e.g., 300 for ~50-second processing)
8. **Static ARNs**: Use `queue_arn_static` / `dead_letter_queue_arn_static` instead of `queue_arn` when the ARN feeds into a resource (Step Functions, IAM policy) that would otherwise create a dependency cycle back to the queue
9. **Queue Policy**: Only set `create_queue_policy = true` (or `create_dlq_queue_policy = true`) when cross-account access or service integration (SNS, EventBridge) requires it — don't add it by default
10. **DLQ Overrides**: Use `dlq_*` variables to diverge DLQ settings (retention, KMS key, tags) from the source queue; unset `dlq_*` values fall back to the corresponding source-queue value
11. **Multiple Queues**: For many similarly-configured queues, prefer the `wrappers` submodule (`terraform-aws-modules/sqs/aws//wrappers`) over repeating the root module block
12. **Tags**: Apply consistent tags (`Environment`, `Application`, `Owner`) for cost allocation and governance; use `dlq_tags` to add DLQ-specific tags on top of `tags`
