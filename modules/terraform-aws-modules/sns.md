# Terraform AWS SNS Module

## Module Information

- **Module Name**: `sns`
- **Module ID**: `terraform-aws-modules/sns/aws`
- **Source**: `terraform-aws-modules/sns/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-sns
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/sns/aws/latest
- **Latest Version**: 7.1.0
- **Minimum Versions**: Terraform >= 1.5.7, AWS Provider >= 6.28
- **Purpose**: Terraform module that creates a single AWS SNS topic with its access policy, subscriptions, and (optionally) a data protection policy
- **Service**: AWS SNS (Simple Notification Service)
- **Category**: Messaging, Event-Driven Architecture
- **Keywords**: sns, simple-notification-service, pub-sub, messaging, topic, subscription, sqs, lambda, fifo, kms-encryption, topic-policy, fan-out, event-driven, message-filtering, data-protection-policy, delivery-status-logging
- **Use For**: application alerting, fan-out to SQS/Lambda, mobile push and SMS/email notifications, serverless event routing, decoupling microservices, cross-account pub/sub, ordered FIFO event streams, CloudWatch alarm actions

## Description

This Terraform module creates and configures a single AWS SNS topic, Amazon's fully managed pub/sub messaging service used to decouple producers from one or more subscribers (SQS, Lambda, HTTP/HTTPS, email, SMS, mobile push application endpoints, and Kinesis Data Firehose). It wraps `aws_sns_topic` together with the associated `aws_sns_topic_policy`, `aws_sns_topic_subscription`, and `aws_sns_topic_data_protection_policy` resources to provide a single, opinionated interface for the most common topic configurations while still exposing full control over access policy, encryption, and delivery behavior through pass-through variables.

The module supports both standard topics (high throughput, best-effort ordering, at-least-once delivery) and FIFO topics (strict ordering, exactly-once delivery, optional content-based deduplication); it automatically appends the required `.fifo` suffix to the topic name when `fifo_topic = true`. It builds the topic's resource-based access policy from a default statement (scoped to the calling account) plus any number of custom `topic_policy_statements`, or accepts a fully externally-authored policy via `topic_policy`/`source_topic_policy_documents`/`override_topic_policy_documents` for merging with other IAM policy documents. Server-side encryption is available via an AWS-managed or customer-managed KMS key, and per-subscription message filtering, redrive policies (DLQs), and raw message delivery are configured through the `subscriptions` map.

Additional capabilities include per-protocol delivery-status feedback logging (application, Firehose, HTTP, Lambda, SQS) with configurable IAM roles and sampling rates, AWS X-Ray tracing, custom delivery/retry policies for HTTP(S) endpoints, message archiving and replay for FIFO topics, and data protection policies that detect and block messages containing sensitive data (non-FIFO topics only). The module has no nested submodules — it manages a single topic and its directly attached resources per module call; provision multiple topics with `for_each` on the module block.

## Key Features

- **Standard and FIFO Topics**: `fifo_topic = true` creates an ordered, exactly-once-delivery topic; the module auto-appends `.fifo` to `name` (or `name_prefix`) so you don't need to add the suffix yourself
- **Content-Based Deduplication & Throughput Scope**: `content_based_deduplication` for automatic FIFO dedup; `fifo_throughput_scope = "MessageGroup"` for higher per-message-group throughput
- **Multi-Protocol Subscriptions**: One `subscriptions` map handles SQS, Lambda, HTTP/HTTPS, email, email-JSON, SMS, application (mobile push), and Firehose endpoints, each with its own filter policy, redrive policy, and delivery options
- **Flexible Access Policy Composition**: Default account-scoped statement (toggle with `enable_default_topic_policy`) plus a structured `topic_policy_statements` map, or fully external policies merged via `source_topic_policy_documents` / `override_topic_policy_documents`, or a raw `topic_policy` JSON document
- **KMS Encryption**: Server-side encryption via `kms_master_key_id` (AWS-managed alias or customer-managed CMK)
- **Data Protection Policy**: `data_protection_policy` detects and denies messages containing sensitive data patterns (PII, etc.) — supported on non-FIFO topics only
- **Message Filtering**: Per-subscription `filter_policy` / `filter_policy_scope` (MessageAttributes or MessageBody) to reduce unnecessary deliveries and downstream cost
- **Delivery Status Logging**: Per-protocol feedback role/sample-rate configuration (`application_feedback`, `firehose_feedback`, `http_feedback`, `lambda_feedback`, `sqs_feedback`) for tracking delivery success/failure
- **X-Ray Tracing & Signature Version**: `tracing_config` (`PassThrough`/`Active`) for distributed tracing; `signature_version` (1=SHA1, 2=SHA256) for message signing — ignored on FIFO topics
- **FIFO Archive & Replay**: `archive_policy` enables message archiving; subscribers can replay archived messages via `replay_policy`
- **Conditional Creation**: `create`, `create_topic_policy`, and `create_subscription` flags independently gate resource creation for composition and testing
- **Region Override**: Per-resource `region` argument to manage a topic in a region different from the default provider region

## Main Use Cases

1. **Application Monitoring and Alerts**: Fan out CloudWatch alarms and application errors to email, Slack integrations, or on-call tooling
2. **Event-Driven Workflows**: Trigger downstream Lambda functions or SQS-backed workers from a single publish event
3. **Fan-Out Architecture**: Broadcast one message to multiple independent subscribers for parallel processing
4. **Mobile Push Notifications**: Deliver push notifications to iOS/Android/other platforms via application endpoints
5. **Email and SMS Notifications**: Send transactional emails and SMS for user-facing alerts
6. **Serverless Event Routing**: Route events to Lambda for serverless architectures without a message broker to manage
7. **Cross-Account Integration**: Grant scoped publish/subscribe access to other AWS accounts via `topic_policy_statements` conditions
8. **Ordered Event Streams**: Use FIFO topics with FIFO SQS subscribers where strict ordering and exactly-once delivery matter (e.g., order processing)
9. **Sensitive-Data Guardrails**: Use `data_protection_policy` to automatically block accidental transmission of PII on standard topics

## Submodules

This module does not define nested/child submodules — it manages a single root-level SNS topic (`aws_sns_topic`) plus its directly attached policy, subscriptions, and data protection policy. To provision multiple topics, use Terraform's native `for_each` on the module call rather than looking for a submodule.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether resources are created |
| `name` | `string` | `null` | Name of the SNS topic (`.fifo` is appended automatically when `fifo_topic = true`) |
| `use_name_prefix` | `bool` | `false` | Use `name` as a prefix (`aws_sns_topic.name_prefix`) instead of an exact name |
| `fifo_topic` | `bool` | `false` | Creates a FIFO topic for ordered, exactly-once message delivery |
| `content_based_deduplication` | `bool` | `false` | Enables automatic content-based deduplication for FIFO topics |
| `fifo_throughput_scope` | `string` | `null` | `"Topic"` or `"MessageGroup"` — higher throughput when ordering only matters within a group |
| `kms_master_key_id` | `string` | `null` | KMS key ID/ARN/alias for server-side encryption |
| `display_name` | `string` | `null` | Display name shown in SMS/email deliveries |
| `signature_version` | `number` | `null` | `1` (SHA1) or `2` (SHA256); ignored when `fifo_topic = true` |
| `tracing_config` | `string` | `null` | X-Ray tracing mode: `"PassThrough"` or `"Active"` |
| `delivery_policy` | `string` | `null` | JSON delivery policy (retry/backoff/throttle) for HTTP(S) endpoints |
| `archive_policy` | `string` | `null` | JSON archive policy for FIFO message replay |
| `data_protection_policy` | `string` | `null` | JSON data protection policy (non-FIFO topics only) |
| `create_topic_policy` | `bool` | `true` | When `true`, manage access via a **standalone `aws_sns_topic_policy`** resource whose document the module **generates** (default statement + `topic_policy_statements` + source/override docs); `topic_policy` is ignored. When `false`, no standalone resource is created and `topic_policy` becomes the topic's **inline** `aws_sns_topic.policy` |
| `enable_default_topic_policy` | `bool` | `true` | Include the module's default account-scoped statement in the generated policy |
| `topic_policy_statements` | `map(object)` | `null` | Custom IAM statements (actions, principals, conditions) merged into the generated policy |
| `topic_policy` | `string` | `null` | Externally authored JSON policy, applied verbatim as the topic's **inline** policy — takes effect **only when `create_topic_policy = false`**; ignored when `create_topic_policy = true` |
| `source_topic_policy_documents` / `override_topic_policy_documents` | `list(string)` | `[]` | Additional `aws_iam_policy_document` JSON strings to source/override into the generated policy |
| `create_subscription` | `bool` | `true` | Whether to create the entries in `subscriptions` |
| `subscriptions` | `map(object)` | `{}` | Subscriptions keyed by name; each sets `protocol`, `endpoint`, and optional `filter_policy`, `filter_policy_scope`, `raw_message_delivery`, `redrive_policy`, `replay_policy`, `delivery_policy` |
| `application_feedback` / `firehose_feedback` / `http_feedback` / `lambda_feedback` / `sqs_feedback` | `object` | `{}` | Per-protocol `{failure_role_arn, success_role_arn, success_sample_rate}` delivery-status logging config |
| `region` | `string` | `null` | Region to manage the topic in (defaults to the provider's region) |
| `tags` | `map(string)` | `{}` | Tags to apply to all created resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `topic_arn` | The ARN of the SNS topic |
| `topic_id` | The ARN of the SNS topic (same value as `topic_arn`, clone of the resource `id`) |
| `topic_name` | The name of the topic |
| `topic_owner` | AWS Account ID of the SNS topic owner |
| `topic_beginning_archive_time` | Oldest timestamp a FIFO subscriber can replay from (FIFO topics only) |
| `subscriptions` | Map of all created `aws_sns_topic_subscription` resources and their attributes |

## Usage Examples

### Example 1: Simple Topic

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

### Example 2: Topic with SQS Subscription and Custom Access Policy

```hcl
module "sns_topic" {
  source  = "terraform-aws-modules/sns/aws"
  version = "~> 7.0"

  name              = "orders-notifications"
  kms_master_key_id = module.kms.key_id

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
      condition = [{
        test     = "StringLike"
        variable = "sns:Endpoint"
        values   = [aws_sqs_queue.orders.arn]
      }]
    }
  }

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

### Example 3: FIFO Topic with FIFO SQS Subscription

```hcl
module "sns_fifo" {
  source  = "terraform-aws-modules/sns/aws"
  version = "~> 7.0"

  # Note: do NOT add ".fifo" yourself — the module appends it automatically
  name                         = "orders"
  fifo_topic                   = true
  content_based_deduplication  = true
  fifo_throughput_scope        = "MessageGroup"

  subscriptions = {
    sqs_fifo = {
      protocol = "sqs"
      # The subscribing SQS queue must also be FIFO
      endpoint = aws_sqs_queue.orders_fifo.arn
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 4: Complete Topic with Feedback Logging, Data Protection, and Multiple Subscriptions

```hcl
module "sns_complete" {
  source  = "terraform-aws-modules/sns/aws"
  version = "~> 7.0"

  name              = "app-notifications"
  display_name      = "Application Notifications"
  kms_master_key_id = module.kms.key_id
  tracing_config    = "Active"
  signature_version = 2

  delivery_policy = jsonencode({
    http = {
      defaultHealthyRetryPolicy = {
        minDelayTarget  = 20
        maxDelayTarget  = 20
        numRetries      = 3
        backoffFunction = "linear"
      }
    }
  })

  data_protection_policy = jsonencode({
    Name        = "DenyInboundEmailAddress"
    Description = "Deny inbound messages containing email addresses"
    Statement = [
      {
        Sid             = "DenyInboundEmailAddress"
        DataDirection   = "Inbound"
        DataIdentifier  = ["arn:aws:dataprotection::aws:data-identifier/EmailAddress"]
        Operation       = { Deny = {} }
        Principal       = ["*"]
      }
    ]
    Version = "2021-06-01"
  })

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

  # Delivery-status logging per protocol
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

## Important Gotchas

1. **FIFO naming is automatic**: When `fifo_topic = true`, the module strips any trailing `.fifo` from `name` and re-appends it — do not manually append `.fifo` to avoid a double suffix; just set the base name.
2. **FIFO subscribers must also be FIFO**: SQS queues subscribed to a FIFO SNS topic must themselves be FIFO queues (`.fifo` name, `fifo_queue = true`).
3. **Data protection policy is non-FIFO only**: `aws_sns_topic_data_protection_policy` is only created when `fifo_topic = false`; setting `data_protection_policy` on a FIFO topic has no effect.
4. **`signature_version` is ignored on FIFO topics**: The module forces `signature_version = null` for the underlying resource whenever `fifo_topic = true`, regardless of what you set.
5. **Two distinct policy mechanisms — `create_topic_policy` selects which one, and `topic_policy` only wins in the `false` branch**: the topic's access policy can live in one of two places, and `create_topic_policy` decides which:
   - **`create_topic_policy = true` (default)** → the module creates a **standalone `aws_sns_topic_policy`** resource whose document it **generates** from `enable_default_topic_policy` + `topic_policy_statements` + `source_topic_policy_documents`/`override_topic_policy_documents`. In this branch `topic_policy` is **ignored** (the topic's own inline `policy` attribute is forced to `null`). So `create_topic_policy = true` + `topic_policy = <json>` **silently drops your JSON** and applies the generated policy — this is the trap.
   - **`create_topic_policy = false`** → no standalone resource is created; `var.topic_policy` is applied **verbatim** as the topic's **inline** `aws_sns_topic.policy`. This is the only branch where `topic_policy` takes effect, but you lose the module's generated statements entirely.
   - **To supply a full, externally-authored policy while keeping the managed resource**, keep `create_topic_policy = true` and pass your document through `source_topic_policy_documents` (and set `enable_default_topic_policy = false` to drop the module's default statement) — do **not** reach for `topic_policy`.
6. **Disabling the default statement can lock you out**: Setting `enable_default_topic_policy = false` without providing equivalent `topic_policy_statements` can leave the topic with an access policy that the topic owner cannot manage — always ensure at least one statement grants the account/role that manages the topic.
7. **`name` has no default but is effectively required**: `name` defaults to `null`; leaving it unset causes the underlying `aws_sns_topic` resource to fail unless `use_name_prefix` generates one from context — always pass `name` explicitly.
8. **Archive/replay require FIFO**: `archive_policy` (topic-level) and `replay_policy` (per-subscription) only apply to FIFO topics; a FIFO topic with an active archive policy cannot be deleted until the archive is deactivated first.
9. **Provider/Terraform floor raised in v7.0.0**: Upgrading from a v6.x pin requires Terraform >= 1.5.7 and AWS provider >= 6.28 — review the module's `CHANGELOG.md` before bumping the version constraint on existing state.

## Best Practices

### Topic Configuration
1. **Choose the Right Topic Type**: Use standard topics for high throughput and best-effort ordering; use FIFO topics only when strict ordering and exactly-once delivery are required, since FIFO caps throughput.
2. **Enable Content-Based Deduplication**: For FIFO topics without a natural per-message dedup ID, enable `content_based_deduplication` to avoid duplicate processing.
3. **Set `fifo_throughput_scope = "MessageGroup"`**: Improves throughput when ordering is only required within a message group, not across the whole topic.
4. **Use Descriptive, Purpose-Based Names**: Name topics after the event they carry (e.g., `orders-created`, `payment-processed`), not the consumer.

### Security and Access Control
1. **Encrypt with a Customer-Managed KMS Key**: Set `kms_master_key_id` for sensitive workloads to get key policy control, rotation, and audit trail via CloudTrail.
2. **Apply Least-Privilege Topic Policies**: Scope `topic_policy_statements` actions/principals/resources to only what publishers and subscribers actually need.
3. **Use Condition Keys to Restrict Subscriptions**: Combine `sns:Endpoint` or `AWS:SourceAccount` conditions in policy statements to prevent arbitrary cross-account subscriptions.
4. **Keep the Default Topic Policy Unless You Have a Replacement**: Don't set `enable_default_topic_policy = false` without also granting equivalent management permissions through `topic_policy_statements`.
5. **Enable Data Protection Policies for PII-Adjacent Topics**: Use `data_protection_policy` on non-FIFO topics to automatically deny messages containing sensitive data patterns.
6. **Prefer SHA256 Signatures**: Set `signature_version = 2` on standard topics for stronger message-signature verification (not applicable to FIFO).

### Subscription Management
1. **Filter at the Subscription, Not the Consumer**: Use `filter_policy`/`filter_policy_scope` so subscribers only receive relevant messages, reducing invocation/processing cost.
2. **Attach Redrive Policies**: Set `redrive_policy` on subscriptions to route delivery failures to a dead-letter SQS queue instead of silently dropping them.
3. **Enable Raw Message Delivery Where Appropriate**: For SQS/HTTP subscriptions that don't need the SNS envelope, set `raw_message_delivery = true` to simplify consumer parsing.
4. **Tune Delivery Retry Policy for HTTP(S) Endpoints**: Configure `delivery_policy` backoff/retry settings to match the reliability of the receiving endpoint.

### Monitoring and Observability
1. **Enable Feedback Logging Per Protocol**: Configure `sqs_feedback`, `lambda_feedback`, `http_feedback`, etc. to capture delivery success/failure in CloudWatch Logs.
2. **Enable X-Ray Tracing for Distributed Debugging**: Set `tracing_config = "Active"` when the topic is part of a traced request path.
3. **Alarm on Delivery Failures**: Create CloudWatch alarms on `NumberOfNotificationsFailed` and `NumberOfNotificationsFilteredOut-InvalidAttributes`.

### Cost Optimization
1. **Filter Early**: Subscription-level filtering avoids paying for downstream compute (Lambda invocations, SQS polls) on messages the consumer would discard anyway.
2. **Keep Payloads Small**: Reference large data in S3 rather than embedding it in the message; SNS has a 256KB message size limit.
3. **Use FIFO Only When Needed**: FIFO topics have lower throughput ceilings than standard topics — don't default to FIFO for workloads that don't require ordering.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-sns
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/sns/aws/latest
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-sns/blob/master/CHANGELOG.md
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-sns/tree/master/examples/complete
- **AWS Provider `aws_sns_topic` Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic
- **AWS SNS Developer Guide**: https://docs.aws.amazon.com/sns/latest/dg/welcome.html
- **SNS Message Filtering**: https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering.html
- **SNS FIFO Topics**: https://docs.aws.amazon.com/sns/latest/dg/sns-fifo-topics.html
- **SNS Message Data Protection**: https://docs.aws.amazon.com/sns/latest/dg/sns-message-data-protection.html
- **SNS Security Best Practices**: https://docs.aws.amazon.com/sns/latest/dg/sns-security.html
- **SNS Pricing**: https://aws.amazon.com/sns/pricing/

## Notes for AI Agents

When generating Terraform code with this module:

1. **Always set `name` explicitly** — it defaults to `null` and the resource creation fails without it (unless relying on `use_name_prefix`).
2. **Never manually append `.fifo`** to `name` when `fifo_topic = true` — the module does this automatically; a manually appended suffix is stripped and re-added, but is still error-prone and unnecessary.
3. **Pick topic type deliberately**: default to standard topics; only set `fifo_topic = true` when the user explicitly needs strict ordering or exactly-once delivery, and remember any SQS subscriber must then also be FIFO.
4. **Default to encrypted topics for anything beyond trivial demos**: set `kms_master_key_id` to a customer-managed key ARN/alias.
5. **Build access policies with `topic_policy_statements`**, not a hand-rolled `topic_policy` JSON string, unless the user needs to merge in externally authored `aws_iam_policy_document` data sources (then use `source_topic_policy_documents`/`override_topic_policy_documents`).
6. **Use `data_protection_policy` only on non-FIFO topics** — it is silently ignored otherwise; don't combine it with `fifo_topic = true`.
7. **Configure `subscriptions` with filters and redrive policies** rather than creating bare subscriptions with no failure handling, when the user's use case implies production traffic.
8. **Tag consistently** (`Environment`, `Application`, `Terraform = "true"`, plus any org-mandated cost/ownership tags).
9. **Pin the module version** (e.g., `version = "~> 7.0"`); note the Terraform >= 1.5.7 / AWS provider >= 6.28 floor introduced in v7.0.0 when upgrading from older pins.
10. **Design consumers for at-least-once delivery** on standard topics — implement idempotent processing downstream, since SNS does not guarantee exactly-once delivery outside of FIFO topics.
