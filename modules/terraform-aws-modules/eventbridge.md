# Terraform AWS EventBridge Module

## Module Information

- **Module Name**: `eventbridge`
- **Source**: `terraform-aws-modules/eventbridge/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-eventbridge
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eventbridge/aws/latest
- **Latest Version**: 4.3.0
- **Purpose**: Terraform module that creates and manages AWS EventBridge resources for building event-driven architectures and serverless applications
- **Service**: AWS EventBridge (Amazon EventBridge)
- **Category**: Integration, Serverless, Event-Driven Architecture
- **Keywords**: eventbridge, event-bus, event-driven, serverless, event-rule, event-target, scheduled-events, cron, event-pipe, api-destination, event-archive, lambda-target, sqs-target, step-functions, cross-account-events, dead-letter-queue
- **Use For**: Microservices decoupling and communication, serverless workflow orchestration, scheduled task execution and cron jobs, real-time data processing pipelines, cross-account and cross-region event routing, SaaS application integration via webhooks, AWS service event monitoring and automation, API gateway event processing, third-party service integration, audit trail and compliance event tracking

## Description

This Terraform module provides a comprehensive solution for creating and managing AWS EventBridge resources, enabling organizations to build scalable event-driven architectures. EventBridge is a serverless event bus service that facilitates application integration by routing events from various sources to target services based on defined rules and patterns. The module abstracts the complexity of configuring event buses, rules, targets, schedules, pipes, connections, and archives, providing a declarative approach to implementing event-driven systems.

The module supports the full spectrum of EventBridge capabilities including custom and default event buses, rules with sophisticated event pattern matching, multiple target types (Lambda, SQS, SNS, Kinesis, Step Functions, ECS, CloudWatch Logs), event schedules using cron or rate expressions, EventBridge Pipes for advanced streaming and transformation, API destinations for HTTP endpoints, and event archives with replay capabilities. The module handles IAM permissions, resource policies for cross-account access, and dead-letter queues for failed delivery handling.

**Note**: This module has NO submodules. All EventBridge capabilities (buses, rules, targets, schedules, pipes, archives, API destinations, connections, permissions) are managed through conditional resource creation flags within the main module.

## Key Features

- **Event Bus Management**: Create custom event buses or use default bus with KMS encryption support
- **Event Rules Configuration**: Define event pattern matching rules with JSON-based filtering logic
- **Multiple Target Types**: Route events to Lambda, SQS, SNS, Kinesis, Step Functions, ECS, CloudWatch Logs, and more
- **EventBridge Scheduler**: Create time-based triggers using cron or rate expressions with timezone support
- **EventBridge Pipes**: Configure event streaming with filtering, enrichment, and transformation
- **API Destinations**: Send events to external HTTP endpoints with OAuth/API key authentication
- **Event Archives**: Store events for replay capabilities and disaster recovery
- **Cross-Account Event Routing**: Configure resource policies for multi-account architectures
- **IAM Role Management**: Automatically create IAM roles with appropriate target permissions
- **Dead Letter Queues**: Configure DLQ for failed deliveries with retry policies
- **Bus-Level Logging**: Enable CloudWatch Logs, S3, or Firehose logging for event bus activity
- **Conditional Resource Creation**: Granular control via boolean flags (`create_*`) for flexible deployments
- **Comprehensive Tagging**: Apply consistent tags to all EventBridge resources

## Main Input Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Master toggle for all resource creation |
| `bus_name` | `string` | `"default"` | Event bus name (use custom name for custom buses) |
| `create_bus` | `bool` | `true` | Create custom EventBridge bus |
| `create_rules` | `bool` | `true` | Create EventBridge rules |
| `create_targets` | `bool` | `true` | Create EventBridge targets |
| `create_schedules` | `bool` | `true` | Create EventBridge schedules |
| `create_pipes` | `bool` | `true` | Create EventBridge pipes |
| `create_archives` | `bool` | `false` | Enable event archiving |
| `create_connections` | `bool` | `false` | Create API connections |
| `create_api_destinations` | `bool` | `false` | Create API destinations |
| `kms_key_identifier` | `string` | `null` | KMS key for bus encryption |

### Rules and Targets

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `rules` | `map(any)` | `{}` | Map of EventBridge rules with event patterns |
| `targets` | `any` | `{}` | Map of targets per rule (Lambda, SQS, etc.) |
| `dead_letter_config` | `any` | `{}` | SQS dead-letter queue configuration |

### Schedules and Pipes

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `schedules` | `any` | `{}` | EventBridge Scheduler definitions |
| `schedule_groups` | `any` | `{}` | Schedule group definitions |
| `pipes` | `any` | `{}` | EventBridge Pipes definitions |

### Archives, Connections, API Destinations

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `archives` | `map(any)` | `{}` | Archive definitions with retention |
| `connections` | `any` | `{}` | API connection definitions (OAuth, API key) |
| `api_destinations` | `map(any)` | `{}` | API destination definitions |

### IAM Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_role` | `bool` | `true` | Create IAM role for EventBridge |
| `role_name` | `string` | `null` | Custom IAM role name |
| `attach_lambda_policy` | `bool` | `false` | Attach Lambda invocation policy |
| `attach_sqs_policy` | `bool` | `false` | Attach SQS send message policy |
| `attach_sns_policy` | `bool` | `false` | Attach SNS publish policy |
| `attach_kinesis_policy` | `bool` | `false` | Attach Kinesis put record policy |
| `attach_ecs_policy` | `bool` | `false` | Attach ECS run task policy |
| `attach_sfn_policy` | `bool` | `false` | Attach Step Functions policy |
| `attach_cloudwatch_policy` | `bool` | `false` | Attach CloudWatch Logs policy |
| `lambda_target_arns` | `list(string)` | `[]` | Lambda ARNs for policy scope |
| `sqs_target_arns` | `list(string)` | `[]` | SQS ARNs for policy scope |
| `ecs_target_arns` | `list(string)` | `[]` | ECS cluster ARNs for policy scope |
| `ecs_pass_role_resources` | `list(string)` | `[]` | Approved roles for ECS tasks |

## Main Outputs

| Output | Description |
|--------|-------------|
| `eventbridge_bus_name` | The EventBridge Bus Name |
| `eventbridge_bus_arn` | The EventBridge Bus ARN |
| `eventbridge_rule_ids` | The EventBridge Rule IDs (map) |
| `eventbridge_rule_arns` | The EventBridge Rule ARNs (map) |
| `eventbridge_schedule_ids` | The EventBridge Schedule IDs |
| `eventbridge_schedule_arns` | The EventBridge Schedule ARNs |
| `eventbridge_pipe_ids` | The EventBridge Pipes IDs |
| `eventbridge_pipe_arns` | The EventBridge Pipes ARNs |
| `eventbridge_archive_arns` | The EventBridge Archive ARNs |
| `eventbridge_connection_ids` | The EventBridge Connection IDs |
| `eventbridge_api_destination_arns` | The EventBridge API Destination ARNs |
| `eventbridge_role_arn` | The ARN of the IAM role created |
| `eventbridge_role_name` | The name of the IAM role created |

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

### Example 2: Scheduled Lambda Execution (Cron Job)

```hcl
module "eventbridge_scheduler" {
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "~> 4.3"

  create_bus = false  # Use default bus

  schedules = {
    daily_cleanup = {
      description         = "Daily cleanup job at 1 AM"
      schedule_expression = "cron(0 1 * * ? *)"
      timezone            = "Europe/London"

      target = {
        arn      = aws_lambda_function.cleanup.arn
        role_arn = aws_iam_role.scheduler_role.arn
        input    = jsonencode({ task = "cleanup" })
      }
    }

    hourly_sync = {
      description         = "Sync data every hour"
      schedule_expression = "rate(1 hour)"

      target = {
        arn      = aws_lambda_function.sync.arn
        role_arn = aws_iam_role.scheduler_role.arn
      }
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 3: EventBridge Pipes (SQS to Lambda)

```hcl
module "eventbridge_pipes" {
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "~> 4.3"

  create_bus = false

  pipes = {
    sqs_to_lambda = {
      source = aws_sqs_queue.source.arn
      target = aws_lambda_function.processor.arn

      source_parameters = {
        filter_criteria = {
          filter = [
            {
              pattern = jsonencode({
                body = { eventType = ["order"] }
              })
            }
          ]
        }
        sqs_queue_parameters = {
          batch_size = 10
        }
      }
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 4: Multi-Target Rule with DLQ

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
        name = "start-onboarding"
        arn  = aws_sfn_state_machine.onboarding.arn
      }
    ]
  }

  attach_lambda_policy = true
  attach_sqs_policy    = true
  attach_sfn_policy    = true

  lambda_target_arns = [aws_lambda_function.welcome_email.arn]
  sqs_target_arns    = [aws_sqs_queue.analytics.arn, aws_sqs_queue.dlq.arn]

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

  # Rules and targets...
  rules   = {}
  targets = {}

  tags = {
    Environment = "production"
  }
}
```

### Example 6: API Destination (Webhook)

```hcl
module "eventbridge" {
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "~> 4.3"

  bus_name                   = "webhook-bus"
  create_connections         = true
  create_api_destinations    = true

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
    slack_webhook = {
      description                      = "Send events to Slack"
      invocation_endpoint              = "https://hooks.slack.com/services/xxx"
      http_method                      = "POST"
      invocation_rate_limit_per_second = 10
      connection_name                  = "slack"
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
        destination     = "slack_webhook"
        attach_role_arn = true
      }
    ]
  }

  attach_api_destination_policy = true

  tags = {
    Environment = "production"
  }
}
```

## Main Use Cases

1. **Microservices Decoupling**: Implement loosely coupled microservices with asynchronous event-based communication
2. **Serverless Workflow Orchestration**: Coordinate Lambda functions, Step Functions, and serverless components
3. **Scheduled Task Automation**: Execute periodic tasks, batch jobs, and cron jobs using EventBridge Scheduler
4. **Real-Time Data Processing**: Build streaming pipelines processing events from AWS services and applications
5. **Cross-Account Integration**: Route events across AWS accounts for centralized monitoring and processing
6. **SaaS Application Integration**: Connect external SaaS applications via webhooks and API destinations
7. **Infrastructure Automation**: Automate responses to AWS service events (EC2, CloudTrail, etc.)
8. **Audit and Compliance**: Capture and route compliance-related events to logging and SIEM systems
9. **Multi-Tenant Event Isolation**: Isolate tenant events using custom event buses for SaaS applications
10. **Event Replay and Recovery**: Archive events for disaster recovery and historical data reprocessing

## Best Practices

### Event Bus Design

1. **Custom Event Buses for Isolation**: Create separate custom event buses for different applications or tenants
2. **Default Bus for AWS Services**: Use default bus for AWS service events, custom buses for application events
3. **Naming Conventions**: Use consistent naming (e.g., `{environment}-{application}-{purpose}`)

### Event Rules and Patterns

1. **Specific Event Patterns**: Define precise patterns to reduce unnecessary rule evaluations
2. **Content-Based Filtering**: Use prefix, suffix, numeric operators to minimize processing
3. **Test Event Patterns**: Validate patterns in EventBridge sandbox before production

### Target Configuration

1. **Dead Letter Queues**: Configure DLQ (SQS) for all production targets
2. **Retry Policies**: Set 3-5 retries with exponential backoff for transient failures
3. **Least Privilege IAM**: Use specific target ARN lists instead of wildcards
4. **Input Transformation**: Use input transformers instead of Lambda wrappers

### Scheduling

1. **Timezone Awareness**: Always set explicit timezone in cron expressions
2. **Scheduler vs Rules**: Prefer EventBridge Scheduler over legacy scheduled rules
3. **Schedule Groups**: Organize related schedules into groups

### Security

1. **KMS Encryption**: Enable for sensitive event data (`kms_key_identifier`)
2. **Resource-Based Policies**: Implement restrictive policies for cross-account access
3. **Connection Secrets**: Store API credentials in AWS Secrets Manager with rotation
4. **Audit Logging**: Enable bus-level logging to CloudWatch for security monitoring

### Performance and Cost

1. **Event Payload Size**: Keep under 256 KB; use S3 references for large data
2. **Filter Early**: Filter events at the pattern level to reduce target invocation costs
3. **Archive Retention**: Set appropriate retention periods (charged per GB-month)

## Important Gotchas

1. **Default Bus Naming**: Setting `bus_name = "default"` with `create_bus = true` creates a custom bus, not AWS default
2. **ECS Pass Role**: When using ECS targets, you MUST provide `ecs_pass_role_resources` with task role ARNs
3. **Policy Order**: Set `attach_*_policy` flags BEFORE module creates the IAM role
4. **DLQ at Target Level**: DLQ configuration is in `targets` map, not module-level
5. **Version 4.0+ Breaking**: Requires Terraform >= 1.5.7 and AWS Provider >= 6.0

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

1. **No Submodules**: This module has no submodules - all features via conditional creation flags
2. **Event Bus Strategy**: Use `create_bus = false` for default bus, `create_bus = true` with custom `bus_name` for isolation
3. **Rules and Targets Maps**: Rules and targets use matching keys (e.g., `rules.orders` → `targets.orders`)
4. **IAM Policy Flags**: Enable only necessary `attach_*_policy` flags and provide specific ARN lists
5. **Dead Letter Queues**: Configure `dead_letter_arn` at target level for production workloads
6. **Scheduling Syntax**: Cron format is `cron(min hour day month day-of-week year)` with `?` for day/day-of-week
7. **Event Patterns**: Use `jsonencode()` for event_pattern values in rules
8. **Version Constraint**: Use `version = "~> 4.3"` for patch-level updates
9. **Cross-Account**: Use `create_permissions = true` with `permissions` map for cross-account access
10. **Encryption**: Set `kms_key_identifier` for KMS encryption of sensitive event data
