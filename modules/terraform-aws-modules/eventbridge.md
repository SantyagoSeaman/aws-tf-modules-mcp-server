# Terraform AWS EventBridge Module

## Module Information

- **Module Name**: `eventbridge`
- **Source**: `terraform-aws-modules/eventbridge/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-eventbridge
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eventbridge/aws/latest
- **Latest Version**: 4.3.0 (requires Terraform >= 1.5.7, AWS provider >= 6.28)
- **Purpose**: Terraform module that creates and manages AWS EventBridge resources (buses, rules, targets, scheduler, pipes, archives, connections, API destinations, permissions) for building event-driven architectures
- **Service**: AWS EventBridge (Amazon EventBridge)
- **Category**: Integration, Serverless, Event-Driven Architecture
- **Keywords**: eventbridge, event-bus, event-rule, event-pattern, event-target, eventbridge-scheduler, cron, eventbridge-pipes, api-destination, event-archive, dead-letter-queue, cross-account, step-functions, serverless, event-driven, iam-role
- **Use For**: microservices decoupling and async communication, serverless workflow orchestration, scheduled task execution and cron jobs, real-time streaming pipelines (SQS/DynamoDB Streams/Kinesis to Lambda/SQS/Step Functions), cross-account and cross-region event routing, SaaS/webhook integration via API destinations, AWS service event monitoring and automation, audit trail and event replay via archives, centralized event bus logging to CloudWatch/S3/Firehose

## Description

This Terraform module provisions AWS EventBridge resources end to end, letting teams declare custom or default event buses, rules with event-pattern or schedule matching, and targets (Lambda, SQS, SNS, Kinesis, Kinesis Firehose, Step Functions, ECS, CloudWatch Logs, other event buses, HTTP API destinations) in a single, composable configuration. It has **no submodules** — every capability is toggled through `create_*` boolean flags on one root module, so a single module block can create just a bus, just a rule, or a fully wired bus + rules + targets + scheduler + pipes + IAM roles.

Beyond the classic rule/target model, the module covers the newer EventBridge building blocks: **EventBridge Scheduler** (`schedules`/`schedule_groups`, cron or rate expressions with timezones and flexible time windows), **EventBridge Pipes** (`pipes`, point-to-point integrations with source filtering, enrichment, and target parameter mapping for SQS, DynamoDB Streams, Kinesis, and more), **Archives** with replay support, **Connections/API Destinations** for authenticated outbound HTTP calls, and bus-level **log delivery** to CloudWatch Logs, S3, or Kinesis Firehose. It also manages the supporting IAM: a role for EventBridge (and, optionally, a separate role for Pipes), pre-built policies scoped to each target service, five generic mechanisms to attach custom policies, and cross-account access via `aws_cloudwatch_event_permission` resource policies.

The module is maintained by the `terraform-aws-modules` org (serverless.tf) and is a common building block for event-driven, serverless AWS architectures alongside the `lambda`, `sqs`, `sns`, and `step-functions` sibling modules.

## Key Features

- **No Submodules**: A single root module; every resource family is gated by a `create_*` flag, so unused features (pipes, schedules, archives, connections) cost nothing when disabled
- **Event Bus**: Create a custom bus or attach to an existing/default bus (data source lookup), with optional KMS encryption, partner event source association, and bus-level dead-letter config
- **Event Rules & Targets**: JSON event-pattern or `schedule_expression` rules; each rule fans out to a map of targets (Lambda, SQS, SNS, Kinesis, Kinesis Firehose, Step Functions, ECS, CloudWatch Logs, another event bus, or an API destination) with per-target input transformation and DLQ
- **EventBridge Scheduler**: `schedules` and `schedule_groups` for cron/rate triggers with timezone, start/end dates, flexible time windows, and ECS-parameter support — works against any bus, not just default
- **EventBridge Pipes**: Source → filter/enrich → target pipelines (SQS, DynamoDB Streams, Kinesis, and more) with per-pipe IAM role (or bring-your-own `role_arn`), CloudWatch/S3/Firehose pipe logging
- **API Destinations & Connections**: Authenticated HTTP targets (API key, Basic, OAuth client credentials) with per-destination invocation rate limiting
- **Event Archives & Replay**: Pattern-scoped archives with configurable retention for disaster recovery and historical reprocessing
- **Cross-Account Permissions**: Resource-based policies keyed as `"{principal} {statement_id}"`, with optional AWS Organizations condition
- **Bus-Level Logging**: `log_config` (level/detail) plus `log_delivery` map for CloudWatch Logs, S3, and Firehose destinations — including a pattern for attaching log delivery to an externally managed bus
- **Schemas Discoverer**: Optional automatic EventBridge schema discovery for the bus
- **IAM Role Management**: Auto-creates the EventBridge role (and optionally a dedicated Pipes role) with prebuilt, tightly-scoped policies per target service plus X-Ray tracing policy support
- **Flexible Custom IAM Policies**: Five ways to attach extra policies to the EventBridge role (`policy`, `policies`, `policy_json`, `policy_jsons`, `policy_statements`)
- **Configurable Naming**: Automatic `-rule`/`-target`/`-schedule`/`-pipe`/`-connection`/`-destination`/`-group` name suffixes, individually toggleable via `append_*_postfix`
- **Region Override**: Per-resource `region` argument for multi-region provider configurations
- **Comprehensive Tagging**: Tags on every resource, plus dedicated `role_tags` for IAM roles

## Main Input Variables

### Core Toggles

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Master toggle for all resource creation |
| `bus_name` | `string` | `"default"` | Event bus name; used to look up the default bus when `create_bus = false` |
| `create_bus` | `bool` | `true` | `true` creates a new custom bus named `bus_name`; `false` looks up an existing bus (e.g. AWS's built-in `default` bus) via data source |
| `create_rules` | `bool` | `true` | Create EventBridge rules |
| `create_targets` | `bool` | `true` | Create EventBridge targets |
| `create_permissions` | `bool` | `true` | Create resource-based permissions from the `permissions` map |
| `create_schedules` / `create_schedule_groups` | `bool` | `true` | Create EventBridge Scheduler resources |
| `create_pipes` | `bool` | `true` | Create EventBridge Pipes |
| `create_archives` | `bool` | `false` | Create event archives |
| `create_connections` / `create_api_destinations` | `bool` | `false` | Create API connections / API destinations |
| `create_log_delivery` / `create_log_delivery_source` | `bool` | `true` | Manage CloudWatch/S3/Firehose log delivery for the bus |
| `create_schemas_discoverer` | `bool` | `false` | Create a default schemas discoverer for the bus |
| `region` | `string` | `null` | Region override for all resources in this module call |

### Bus, Rules, Targets

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `bus_description` | `string` | `null` | Description for a custom bus |
| `kms_key_identifier` | `string` | `null` | KMS key ARN/ID/alias for bus encryption |
| `event_source_name` | `string` | `null` | Partner event source to match the new bus with |
| `dead_letter_config` | `any` | `{}` | **Bus-level** DLQ config (`{ arn = <sqs_arn> }`) for undeliverable events; per-target retries use `dead_letter_arn` inside `targets` instead |
| `rules` | `map(any)` | `{}` | Map of rule definitions: `description`, `event_pattern` (use `jsonencode`) or `schedule_expression`, `enabled` |
| `targets` | `any` | `{}` | Map keyed by rule name → list of target objects (`name`, `arn` or `destination`, `input`/`input_path`, `dead_letter_arn`, `input_transformer`, `attach_role_arn`, service-specific `*_target` blocks) |
| `log_config` | `object({include_detail, level})` | `null` | Bus event-log verbosity (`level`: OFF/ERROR/INFO/TRACE) |
| `log_delivery` | `map(object)` | `{}` | Log delivery destinations keyed by `cloudwatch_logs` \| `s3` \| `firehose`, each with `destination_arn` (and `source_name` when attaching to a bus owned by another module call) |

### Scheduler & Pipes

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `schedules` | `map(any)` | `{}` | Schedule definitions: `schedule_expression`, `timezone`, `arn` (target), `input`, `group_name`, `role_arn` (optional — defaults to the module's EventBridge role) |
| `schedule_groups` | `any` | `{}` | Schedule group definitions (`name`/`name_prefix`, `tags`) |
| `schedule_group_timeouts` | `map(string)` | `{}` | Create/delete timeouts for schedule groups |
| `pipes` | `any` | `{}` | Pipe definitions: `source`, `target`, `enrichment`, `source_parameters`, `target_parameters`, `log_configuration`, `role_arn`/`create_role` |
| `create_pipe_role_only` | `bool` | `false` | Create only the shared Pipes IAM role without any pipe resources |

### Archives, Connections, API Destinations, Permissions

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `archives` | `map(any)` | `{}` | Archive definitions: `description`, `event_pattern`, `retention_days`, `kms_key_identifier` |
| `connections` | `any` | `{}` | Connection definitions (`authorization_type`: API_KEY \| BASIC \| OAUTH_CLIENT_CREDENTIALS, `auth_parameters`) |
| `api_destinations` | `map(any)` | `{}` | API destination definitions: `invocation_endpoint`, `http_method`, `invocation_rate_limit_per_second`, `connection_name` |
| `permissions` | `map(any)` | `{}` | Cross-account access; keys formatted as `"{principal} {statement_id}"`, values may set `action`, `event_bus_name`, `condition_org` |

### IAM Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_role` | `bool` | `true` | Create the IAM role used by EventBridge (rules/schedules) |
| `role_name` | `string` | `null` | Custom IAM role name (auto-generated if omitted) |
| `role_permissions_boundary`, `role_path`, `policy_path` | `string` | `null` | IAM hardening options |
| `trusted_entities` | `list(string)` | `[]` | Extra principals allowed to assume the EventBridge role |
| `attach_lambda_policy` / `attach_sqs_policy` / `attach_sns_policy` / `attach_kinesis_policy` / `attach_kinesis_firehose_policy` / `attach_ecs_policy` / `attach_sfn_policy` / `attach_cloudwatch_policy` / `attach_tracing_policy` / `attach_api_destination_policy` | `bool` | `false` | Attach the matching prebuilt, service-scoped policy to the EventBridge role |
| `lambda_target_arns`, `sqs_target_arns`, `sns_target_arns`, `kinesis_target_arns`, `kinesis_firehose_target_arns`, `ecs_target_arns`, `sfn_target_arns`, `cloudwatch_target_arns` | `list(string)` | `[]` | Resource ARNs the matching policy is scoped to — **required** alongside the matching `attach_*_policy` or the policy grants no access |
| `ecs_pass_role_resources` | `list(string)` | `[]` | Roles approved for `iam:PassRole` when targeting ECS (defaults to `["*"]` if unset) |
| `policy`, `policies`, `policy_json`, `policy_jsons`, `policy_statements` (+ matching `attach_*`) | — | — | Five generic ways to attach custom/extra policies to the EventBridge role |

## Main Outputs

| Output | Description |
|--------|-------------|
| `eventbridge_bus_name` / `eventbridge_bus_arn` | Event bus name / ARN |
| `eventbridge_bus` | Full bus resource attributes |
| `eventbridge_rule_ids` / `eventbridge_rule_arns` | Rule IDs / ARNs, keyed by rule map key |
| `eventbridge_rules` / `eventbridge_targets` | Full rule / target resource attribute maps |
| `eventbridge_schedule_ids` / `eventbridge_schedule_arns` | Scheduler schedule IDs / ARNs |
| `eventbridge_schedule_group_ids` / `eventbridge_schedule_group_arns` / `eventbridge_schedule_group_states` | Schedule group IDs / ARNs / states |
| `eventbridge_pipe_ids` / `eventbridge_pipe_arns` | Pipe IDs / ARNs |
| `eventbridge_pipe_role_arns` / `eventbridge_pipe_role_names` | IAM role ARNs/names created for Pipes |
| `eventbridge_archive_arns` | Archive ARNs |
| `eventbridge_connection_ids` / `eventbridge_connection_arns` | Connection IDs / ARNs |
| `eventbridge_api_destination_arns` | API destination ARNs |
| `eventbridge_permission_ids` | Cross-account permission statement IDs |
| `eventbridge_role_arn` / `eventbridge_role_name` | EventBridge IAM role ARN / name |
| `eventbridge_log_delivery_source_arn` / `eventbridge_log_delivery_source_name` | Log delivery source ARN/name — pass into a second module call to attach log delivery to an externally managed bus |

## Usage Examples

### Example 1: Event Rule with Lambda Target

```hcl
module "eventbridge" {
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "~> 4.3"

  bus_name = "orders-event-bus"

  rules = {
    orders = {
      description   = "Capture order events"
      event_pattern = jsonencode({
        source      = ["myapp.orders"]
        detail-type = ["Order Placed"]
      })
    }
  }

  targets = {
    orders = [
      {
        name = "process-order"
        arn  = aws_lambda_function.order_processor.arn
      }
    ]
  }

  attach_lambda_policy = true
  lambda_target_arns   = [aws_lambda_function.order_processor.arn]

  tags = {
    Environment = "production"
    Application = "orders"
  }
}
```

### Example 2: EventBridge Scheduler (Cron Job)

```hcl
module "eventbridge" {
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "~> 4.3"

  bus_name = "scheduler-example" # any bus works; "default" bus also supports schedule_expression on rules

  attach_lambda_policy = true
  lambda_target_arns   = [aws_lambda_function.cleanup.arn, aws_lambda_function.sync.arn]

  schedules = {
    daily_cleanup = {
      description         = "Daily cleanup job at 1 AM"
      schedule_expression = "cron(0 1 * * ? *)"
      timezone            = "Europe/London"
      arn                 = aws_lambda_function.cleanup.arn
      input               = jsonencode({ task = "cleanup" })
    }

    hourly_sync = {
      description         = "Sync data every hour"
      schedule_expression = "rate(1 hour)"
      arn                 = aws_lambda_function.sync.arn
    }
  }

  tags = {
    Environment = "production"
  }
}
```
> `role_arn` on a schedule is optional — if omitted, the module's own EventBridge IAM role (created because `attach_lambda_policy = true`) is used as the invocation role.

### Example 3: EventBridge Pipes (Filtered SQS to Lambda)

```hcl
module "eventbridge_pipes" {
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "~> 4.3"

  create_bus     = false
  create_rules   = false
  create_targets = false

  pipes = {
    sqs_to_lambda = {
      source = aws_sqs_queue.source.arn
      target = aws_lambda_function.processor.arn

      source_parameters = {
        filter_criteria = {
          filter1 = {
            pattern = jsonencode({ body = { eventType = ["order"] } })
          }
        }
        sqs_queue_parameters = {
          batch_size = 10
        }
      }

      target_parameters = {
        lambda_function_parameters = {
          invocation_type = "REQUEST_RESPONSE"
        }
      }

      tags = {
        Pipe = "sqs_to_lambda"
      }
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 4: Multi-Target Rule with Dead Letter Queue

```hcl
module "eventbridge" {
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "~> 4.3"

  bus_name = "application-events"

  rules = {
    user_signup = {
      description   = "User signup events"
      event_pattern = jsonencode({
        source      = ["myapp.users"]
        detail-type = ["User Signed Up"]
      })
    }
  }

  targets = {
    user_signup = [
      {
        name            = "send-welcome-email"
        arn             = aws_lambda_function.welcome_email.arn
        dead_letter_arn = aws_sqs_queue.dlq.arn
      },
      {
        name = "notify-analytics"
        arn  = aws_sqs_queue.analytics.arn
      },
      {
        name            = "start-onboarding"
        arn             = aws_sfn_state_machine.onboarding.arn
        attach_role_arn = true
      }
    ]
  }

  attach_lambda_policy = true
  attach_sqs_policy    = true
  attach_sfn_policy    = true

  lambda_target_arns = [aws_lambda_function.welcome_email.arn]
  sqs_target_arns    = [aws_sqs_queue.analytics.arn, aws_sqs_queue.dlq.arn]
  sfn_target_arns    = [aws_sfn_state_machine.onboarding.arn]

  tags = {
    Environment = "production"
  }
}
```

### Example 5: Event Archive for Replay

```hcl
module "eventbridge" {
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "~> 4.3"

  bus_name        = "critical-events"
  create_archives = true

  archives = {
    all_events = {
      description    = "Archive all events for 30 days"
      retention_days = 30
    }

    order_events = {
      description    = "Archive order events for 90 days"
      retention_days = 90
      event_pattern  = jsonencode({
        source = ["myapp.orders"]
      })
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 6: API Destination (Webhook) + Cross-Account Permission

```hcl
module "eventbridge" {
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "~> 4.3"

  bus_name = "webhook-bus"

  create_connections      = true
  create_api_destinations = true

  connections = {
    slack = {
      authorization_type = "API_KEY"
      auth_parameters = {
        api_key = {
          key   = "Authorization"
          value = "Bearer ${var.slack_token}"
        }
      }
    }
  }

  api_destinations = {
    slack = {
      description                      = "Send events to Slack"
      invocation_endpoint              = "https://hooks.slack.com/services/xxx"
      http_method                      = "POST"
      invocation_rate_limit_per_second = 10
    }
  }

  rules = {
    alerts = {
      description   = "Send alerts to Slack"
      event_pattern = jsonencode({
        source      = ["myapp.alerts"]
        detail-type = ["Alert"]
      })
    }
  }

  targets = {
    alerts = [
      {
        name            = "slack-webhook"
        destination     = "slack"
        attach_role_arn = true
      }
    ]
  }

  attach_api_destination_policy = true

  # Allow another account to PutEvents on this bus
  permissions = {
    "111122223333 PartnerAccess" = {
      action = "events:PutEvents"
    }
  }

  tags = {
    Environment = "production"
  }
}
```

## Main Use Cases

1. **Microservices Decoupling**: Loosely coupled, asynchronous event-based service communication
2. **Serverless Workflow Orchestration**: Coordinate Lambda, Step Functions, and other serverless components
3. **Scheduled Task Automation**: Cron/rate-based jobs via EventBridge Scheduler
4. **Real-Time Streaming Pipelines**: Pipes from SQS/DynamoDB Streams/Kinesis into Lambda, SQS, or Step Functions with inline filtering
5. **Cross-Account Integration**: Route events across AWS accounts via resource-based permissions
6. **SaaS/Webhook Integration**: Connect external services via API destinations and connections
7. **Infrastructure Automation**: React to AWS service events (EC2, CloudTrail, etc.)
8. **Audit and Compliance**: Capture and route compliance events to logging/SIEM systems
9. **Multi-Tenant Event Isolation**: Separate custom buses per tenant/application
10. **Event Replay and Recovery**: Archive events for disaster recovery and reprocessing

## Best Practices

### Event Bus Design
1. **Explicit Default-Bus Targeting**: To attach rules/targets to AWS's built-in `default` bus, set `create_bus = false` (leave `bus_name` as `"default"`); do **not** set `create_bus = true` with `bus_name = "default"` — AWS rejects creating a bus literally named `default`
2. **Custom Buses for Isolation**: Create separate custom buses per application/tenant to scope IAM and event patterns
3. **Naming Conventions**: Use `{environment}-{application}-{purpose}` for custom bus names

### Event Rules and Targets
1. **Specific Event Patterns**: Narrow `source`/`detail-type`/`detail` matchers to cut unnecessary target invocations
2. **DLQ Per Target**: Set `dead_letter_arn` on every production target; the module-level `dead_letter_config` only covers bus-level undeliverable events
3. **Input Transformation**: Prefer `input_transformer`/`input_path` over wrapping every target in a Lambda shim

### IAM and Security
1. **Always Pair Policy Flags with ARN Lists**: `attach_lambda_policy = true` with an empty `lambda_target_arns` produces a policy with no effective access — set the ARN list alongside the flag
2. **Least Privilege**: Use the specific `*_target_arns` lists instead of relying on defaults; `ecs_pass_role_resources` defaults to `["*"]` if left unset — restrict it explicitly
3. **KMS Encryption**: Set `kms_key_identifier` for sensitive event data on custom buses
4. **Cross-Account Policies**: Scope `permissions` entries to the minimum `action` needed and prefer the `condition_org` (AWS Organizations) guard over open principals
5. **Secrets in Connections**: Reference secrets from environment/Secrets Manager rather than hardcoding `auth_parameters` values in code

### Scheduling and Pipes
1. **Timezone Awareness**: Always set `timezone` on schedules that use `cron()` expressions
2. **Scheduler over Legacy Cron Rules**: Prefer `schedules` (EventBridge Scheduler) over `schedule_expression` on rules for new work — it supports timezones, flexible windows, and groups
3. **Group Related Schedules**: Use `schedule_groups` to organize and scope IAM/limits per team or workload
4. **Filter at the Pipe Source**: Use `source_parameters.filter_criteria` in Pipes to avoid invoking targets for irrelevant records

### Naming and Observability
1. **Understand Auto-Suffixing**: By default the module appends `-rule`/`-target's rule name`/`-schedule`/`-pipe`/`-connection`/`-destination`/`-group` to AWS resource names; module outputs stay keyed by your own map key regardless — disable via `append_*_postfix = false` if you need exact names
2. **Enable Bus Logging**: Set `log_config` and `log_delivery` for CloudWatch Logs/S3/Firehose visibility into bus activity, especially for custom buses handling sensitive workloads
3. **External Bus Log Delivery**: To attach logging to a bus owned by a different module call, pass that call's `eventbridge_log_delivery_source_name` output into a second module instance with `create_bus = false` and `create_log_delivery_source = false`

### Cost and Performance
1. **Event Payload Size**: Keep events under 256 KB; use S3 references for larger payloads
2. **Archive Retention**: Set `retention_days` deliberately — archives are billed per GB-month

## Important Gotchas

1. **Default Bus Naming**: `create_bus = true` with `bus_name = "default"` fails — see Best Practices above
2. **ECS Pass Role**: ECS targets require `ecs_pass_role_resources` set to the task role ARNs, or the pass-role policy defaults to `"*"`
3. **DLQ Scope**: `dead_letter_config` (module-level) configures the **bus's** DLQ; per-target retry failures need `dead_letter_arn` inside each `targets`/`schedules`/`pipes` entry
4. **Policy Without ARNs Grants Nothing**: Enabling an `attach_*_policy` flag without the matching `*_target_arns` list produces an empty-resource IAM policy
5. **Provider/Terraform Floor**: v4.x requires Terraform >= 1.5.7 and AWS provider >= 6.28 — pin `version = "~> 4.3"`
6. **No Submodules**: All features are enabled via `create_*` flags on the single root module — there is nothing under a `//modules/` path to reference

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-eventbridge
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eventbridge/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-eventbridge/tree/master/examples
- **AWS EventBridge Documentation**: https://docs.aws.amazon.com/eventbridge/latest/userguide/what-is-amazon-eventbridge.html
- **Event Pattern Reference**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html
- **EventBridge Scheduler**: https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html
- **EventBridge Pipes**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes.html
- **AWS EventBridge Pricing**: https://aws.amazon.com/eventbridge/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **No Submodules**: All features are exposed via `create_*` flags on the root module — never reference a `//modules/...` path
2. **Event Bus Strategy**: `create_bus = false` for AWS's default bus; `create_bus = true` with a real custom `bus_name` for isolation (never `bus_name = "default"` with `create_bus = true`)
3. **Rules ↔ Targets Keys**: `rules` and `targets` are matched by map key (e.g., `rules.orders` pairs with `targets.orders`)
4. **Schedules Are Flat**: `schedules.<key>` fields (`arn`, `input`, `timezone`, `role_arn`) live directly on the schedule object — there is no nested `target` block (unlike some other scheduler examples)
5. **IAM Policy Flags Need ARNs**: Every `attach_*_policy = true` must be paired with its `*_target_arns` list to actually grant access
6. **Dead Letter Queues**: Module-level `dead_letter_config` = bus DLQ; use per-item `dead_letter_arn` for target/schedule/pipe-level retries
7. **Event Patterns**: Always wrap `event_pattern` values with `jsonencode()`
8. **Cron Syntax**: `cron(min hour day month day-of-week year)`, using `?` for the unused day-of-month or day-of-week field; always set `timezone` alongside it
9. **Version Constraint**: Use `version = "~> 4.3"`; requires Terraform >= 1.5.7 and AWS provider >= 6.28
10. **Cross-Account Access**: Set `permissions` (default `create_permissions = true`) with keys formatted `"{account_id_or_*} {statement_id}"`
11. **Encryption**: Set `kms_key_identifier` on the bus for KMS encryption of sensitive event data
12. **Pipes Filtering**: Use `source_parameters.filter_criteria` (a map of `{ pattern = jsonencode(...) }` objects) to filter Pipe source events before they reach the target
