---
module_name: eventbridge
keywords: [eventbridge, event-bus, event-driven, serverless, event-routing, event-bridge, event-pattern, cloudwatch-events, scheduled-events, cron, rate-expression, event-rule, event-target, event-source, event-archive, event-replay, api-destination, event-pipe, event-connection, lambda-target, sqs-target, sns-target, kinesis-target, step-functions, ecs-task, cloudwatch-logs, event-filtering, event-transformation, cross-account-events, saas-integration, webhooks, event-schema, schema-registry, dead-letter-queue, dlq, retry-policy, input-transformer, event-bus-policy, partner-event-source, custom-event-bus, default-event-bus, event-source-mapping, idempotency, event-deduplication, cloudtrail-events, aws-events, third-party-events, event-driven-architecture, async-communication, decoupling, microservices-events, event-ingestion, event-processing, event-distribution, real-time-events, scheduled-tasks, cron-jobs, event-scheduler]
---

# Terraform AWS EventBridge Module

## Module Information

- **Module Name**: `eventbridge`
- **Source**: `terraform-aws-modules/eventbridge/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-eventbridge
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eventbridge/aws/latest
- **Latest Version**: 4.2.1
- **Purpose**: Terraform module that creates and manages AWS EventBridge resources for building event-driven architectures and serverless applications
- **Service**: AWS EventBridge (Amazon EventBridge)
- **Category**: Integration, Serverless, Event-Driven Architecture
- **Keywords**: eventbridge, event-bus, event-driven, serverless, event-routing, event-pattern, cloudwatch-events, scheduled-events, cron, rate-expression, event-rule, event-target, event-source, event-archive, event-replay, api-destination, event-pipe, event-connection, lambda-target, sqs-target, sns-target, kinesis-target, step-functions, ecs-task, cloudwatch-logs, event-filtering, event-transformation, cross-account-events, saas-integration, webhooks, event-schema, schema-registry, dead-letter-queue, dlq, retry-policy, input-transformer, event-bus-policy, partner-event-source, custom-event-bus, default-event-bus, event-source-mapping, idempotency, event-deduplication, cloudtrail-events, aws-events, third-party-events, event-driven-architecture, async-communication, decoupling, microservices-events, event-ingestion, event-processing, event-distribution, real-time-events, scheduled-tasks, cron-jobs, event-scheduler
- **Use For**: Microservices decoupling and communication, serverless workflow orchestration, scheduled task execution and cron jobs, real-time data processing pipelines, cross-account and cross-region event routing, SaaS application integration via webhooks, AWS service event monitoring and automation, API gateway event processing, third-party service integration, audit trail and compliance event tracking, IoT device event processing, multi-tenant event isolation

## Description

This Terraform module provides a comprehensive solution for creating and managing AWS EventBridge resources, enabling organizations to build scalable event-driven architectures. EventBridge is a serverless event bus service that facilitates application integration by routing events from various sources to target services based on defined rules and patterns. The module abstracts the complexity of configuring event buses, rules, targets, schedules, pipes, connections, and archives, providing a declarative approach to implementing event-driven systems that decouple application components and enable real-time processing.

The module supports the full spectrum of EventBridge capabilities including custom and default event buses for event routing, rules with sophisticated event pattern matching for filtering and routing logic, multiple target types for event delivery (Lambda, SQS, SNS, Kinesis, Step Functions, ECS, CloudWatch Logs, and more), event schedules for time-based triggering using cron or rate expressions, EventBridge Pipes for advanced event streaming and transformation, API destinations for sending events to external HTTP endpoints, and event archives with replay capabilities for disaster recovery and debugging. The module also handles IAM permissions, resource policies for cross-account access, and dead-letter queues for failed event delivery handling.

Built for production use cases, the module implements AWS best practices including conditional resource creation for flexible deployment scenarios, comprehensive IAM policy management for secure event routing, KMS encryption support for sensitive event data, detailed CloudWatch Logs integration for event bus monitoring, and flexible tagging strategies for resource organization. The module's design supports complex architectures including multi-tenant event isolation through custom buses, cross-account event sharing, SaaS partner integrations, and hybrid cloud event routing, making it ideal for modern microservices, serverless applications, and event-driven workflows.

## Key Features

- **Event Bus Management**: Create and manage custom event buses and utilize default event bus for AWS service events
- **Event Rules Configuration**: Define sophisticated event pattern matching rules with JSON-based filtering logic
- **Multiple Target Types**: Route events to Lambda functions, SQS queues, SNS topics, Kinesis streams, Step Functions, ECS tasks, CloudWatch Logs, and more
- **Event Schedules**: Create time-based event triggers using cron expressions or rate expressions for scheduled tasks
- **EventBridge Pipes**: Configure advanced event streaming with filtering, enrichment, and transformation capabilities
- **API Destinations**: Send events to external HTTP endpoints and third-party SaaS applications via webhooks
- **Event Archives**: Create archives for event storage and replay capabilities for disaster recovery and debugging
- **Event Replay**: Replay archived events to recover from failures or reprocess historical data
- **Cross-Account Event Routing**: Configure resource policies for cross-account event sharing and multi-account architectures
- **IAM Role Management**: Automatically create and attach IAM roles with appropriate permissions for event targets
- **Event Transformation**: Transform event data before delivery using input transformers and input paths
- **Dead Letter Queues**: Configure DLQ for failed event deliveries with retry policies and error handling
- **Event Pattern Filtering**: Advanced event filtering using content-based filtering with prefix, suffix, and numeric matching
- **Connection Management**: Manage OAuth and API key-based connections for API destinations securely
- **Schedule Groups**: Organize related schedules into groups for better management and monitoring
- **Flexible Targets**: Support for multiple targets per rule with parallel event delivery
- **Event Bus Logging**: Enable CloudWatch Logs integration for event bus activity monitoring and debugging
- **Resource-Based Policies**: Configure event bus policies for fine-grained access control and cross-account permissions
- **Partner Event Sources**: Integrate with SaaS partner event sources through EventBridge partner ecosystem
- **Event Schema Registry Integration**: Leverage schema discovery and validation for structured event processing
- **Conditional Resource Creation**: Granular control over resource creation with boolean flags for flexible deployments
- **Comprehensive Tagging**: Apply consistent tags to all EventBridge resources for cost allocation and governance
- **KMS Encryption Support**: Encrypt sensitive event data at rest using customer-managed KMS keys
- **Retry Configuration**: Configure retry attempts and exponential backoff for failed event deliveries
- **Input Path Customization**: Extract and map specific event attributes to target inputs using JSON path expressions

## Main Use Cases

1. **Microservices Decoupling**: Implement loosely coupled microservices architectures with asynchronous event-based communication
2. **Serverless Workflow Orchestration**: Coordinate Lambda functions, Step Functions, and other serverless components via events
3. **Scheduled Task Automation**: Execute periodic tasks, batch jobs, and cron jobs using EventBridge Scheduler
4. **Real-Time Data Processing**: Build streaming data pipelines processing events from AWS services, applications, and IoT devices
5. **Cross-Account Integration**: Route events across AWS accounts for centralized monitoring, logging, and processing
6. **SaaS Application Integration**: Connect external SaaS applications via webhooks and API destinations for bi-directional event flow
7. **Infrastructure Automation**: Automate responses to AWS service events (EC2 state changes, CloudTrail API calls, etc.)
8. **Audit and Compliance**: Capture and route compliance-related events to centralized logging and SIEM systems
9. **Multi-Tenant Event Isolation**: Isolate tenant events using custom event buses for SaaS applications
10. **Event Replay and Recovery**: Archive events for disaster recovery, debugging, and historical data reprocessing

## Best Practices

### Event Bus Design and Architecture

1. **Custom Event Buses for Isolation**: Create separate custom event buses for different applications, tenants, or environments to isolate event traffic and simplify access control
2. **Naming Conventions**: Use consistent naming conventions for event buses, rules, and targets (e.g., `{environment}-{application}-{purpose}`) for clarity
3. **Event Bus Per Bounded Context**: Align event buses with domain-driven design bounded contexts in microservices architectures
4. **Default Bus for AWS Services**: Use the default event bus for AWS service events (CloudTrail, EC2, etc.) and custom buses for application events
5. **Cross-Account Event Routing**: Configure resource-based policies on event buses for cross-account event sharing in multi-account architectures
6. **Event Bus Limits**: Monitor event bus quotas (PutEvents rate, rules per bus) and distribute load across multiple buses if needed

### Event Rule Configuration

1. **Specific Event Patterns**: Define precise event patterns with specific matching criteria to reduce unnecessary rule evaluations and target invocations
2. **Content-Based Filtering**: Use advanced filtering with prefix, suffix, numeric, and exists operators to minimize event processing overhead
3. **Rule Naming Strategy**: Use descriptive rule names that clearly indicate the event pattern and target (e.g., `order-created-to-inventory-lambda`)
4. **Avoid Overly Broad Patterns**: Refrain from catch-all patterns that match all events unless required for auditing or monitoring
5. **Rule Priority with Multiple Targets**: When multiple targets exist, design event patterns to avoid unintended multiple invocations
6. **Test Event Patterns**: Use EventBridge event pattern sandbox or test events to validate patterns before production deployment
7. **Version Event Patterns**: Include event schema versions in patterns to handle schema evolution gracefully

### Target Configuration

1. **Dead Letter Queues**: Configure DLQ (SQS) for all targets to capture failed event deliveries for later analysis and reprocessing
2. **Retry Policies**: Set appropriate retry attempts (3-5 retries) and exponential backoff for transient failures
3. **Target IAM Permissions**: Use least privilege IAM roles for EventBridge to invoke targets with only necessary permissions
4. **Input Transformation**: Transform event payloads to match target input requirements using input transformers instead of custom Lambda wrappers
5. **Multiple Targets Strategy**: Use multiple targets per rule judiciously, considering idempotency and consistency requirements
6. **Batch Size Configuration**: For SQS and Kinesis targets, configure appropriate batch sizes to balance throughput and latency
7. **Target-Specific Settings**: Configure target-specific parameters (ECS task count, Step Functions input, etc.) based on workload characteristics
8. **Asynchronous Processing**: Design targets to handle events asynchronously and idempotently to avoid blocking and duplicate processing

### Event Scheduling

1. **Timezone Awareness**: Use explicit timezone settings in cron expressions for schedule rules to avoid daylight saving time issues
2. **Rate vs Cron Expressions**: Use rate expressions for simple periodic tasks and cron for complex schedules requiring specific times
3. **Schedule Groups**: Organize related schedules into schedule groups for unified management and monitoring
4. **Flexible Time Windows**: Configure flexible time windows for schedules that don't require precise execution timing
5. **Schedule Overlap Prevention**: Design scheduled tasks to complete before the next invocation to prevent overlapping executions
6. **Error Handling for Schedules**: Implement error handling and DLQ for scheduled targets to capture failed executions
7. **Schedule Monitoring**: Monitor scheduled event metrics in CloudWatch to detect missed or failed executions

### Security and Compliance

1. **Resource-Based Policies**: Implement restrictive resource-based policies on event buses to control which accounts and services can send events
2. **Encryption at Rest**: Enable KMS encryption for sensitive event data, especially for compliance-regulated workloads
3. **IAM Role Segregation**: Create separate IAM roles for different event rules and targets to follow least privilege principle
4. **Cross-Account Security**: Use IAM conditions in cross-account policies to restrict event sources and validate event origins
5. **Audit Event Bus Activity**: Enable CloudWatch Logs for event bus to audit all events passing through for security monitoring
6. **Sensitive Data Handling**: Avoid including sensitive data in event payloads; use references and retrieve data from secure stores
7. **Connection Secret Management**: Store API keys and OAuth credentials for API destinations in AWS Secrets Manager with rotation
8. **Event Schema Validation**: Use EventBridge Schema Registry to validate event structures and prevent malformed events

### Performance and Optimization

1. **Event Payload Size**: Keep event payloads under 256 KB; use references to S3 or databases for large data payloads
2. **Batch Event Submission**: Use PutEvents API to batch up to 10 events per request to reduce API calls and improve throughput
3. **Rule Evaluation Efficiency**: Design event patterns to fail fast by placing most selective criteria first in pattern matching
4. **Target Throttling**: Implement backpressure and throttling in targets to handle high event volumes without overwhelming downstream services
5. **Archive Storage Optimization**: Configure archive retention periods based on compliance requirements to optimize storage costs
6. **Pipe Filtering**: Use EventBridge Pipes filtering to reduce unnecessary invocations and data transfer costs
7. **Monitoring Performance Metrics**: Track FailedInvocations, ThrottledRules, and DeadLetterInvocations metrics for performance tuning

### Cost Optimization

1. **Event Filtering at Source**: Filter events as early as possible in the event pattern to avoid processing and target invocation costs
2. **Target Cost Awareness**: Consider target invocation costs (Lambda, Step Functions) when designing event-driven workflows
3. **Archive Retention Policies**: Set appropriate archive retention periods; archives are charged per GB-month stored
4. **Cross-Region Considerations**: Minimize cross-region event routing to reduce data transfer costs
5. **Schedule Optimization**: Consolidate multiple scheduled rules into fewer schedules with batched processing when possible
6. **API Destination Caching**: Implement caching strategies for API destinations to reduce outbound HTTP requests
7. **Development Environment Management**: Use conditional creation to disable non-essential event rules in development environments

### Operational Excellence

1. **Event Versioning**: Include schema version fields in events to support backward-compatible schema evolution
2. **Idempotency Keys**: Include unique event IDs or idempotency keys for deduplication in target processing logic
3. **Comprehensive Tagging**: Tag all EventBridge resources with environment, application, cost center, and owner tags for governance
4. **Monitoring and Alerting**: Create CloudWatch alarms for FailedInvocations, ThrottledRules, and DLQ message counts
5. **Event Replay Strategy**: Regularly test event replay procedures to ensure disaster recovery readiness
6. **Documentation**: Document event schemas, patterns, and data flows for team knowledge sharing and onboarding
7. **Change Management**: Version control event patterns and infrastructure code; test changes in non-production environments
8. **Capacity Planning**: Monitor PutEvents API usage and plan for peak loads; request quota increases proactively

### High Availability and Disaster Recovery

1. **Multi-AZ Deployment**: EventBridge is inherently multi-AZ; ensure targets are also multi-AZ for end-to-end availability
2. **Cross-Region Replication**: Implement cross-region event routing for critical workflows requiring regional failover
3. **Event Archiving**: Enable archives for critical event buses to support replay during disaster recovery scenarios
4. **Target Redundancy**: Configure multiple targets in different availability zones or regions for critical events
5. **DLQ Monitoring**: Actively monitor and alert on DLQ messages to detect and recover from systematic failures
6. **Replay Testing**: Periodically test event replay from archives to validate recovery procedures
7. **Health Checks**: Implement health check events to validate end-to-end event delivery paths

### Development and Deployment

1. **Infrastructure as Code**: Manage all EventBridge resources using Terraform with version-controlled configurations
2. **Environment Segregation**: Use separate event buses and rules for development, staging, and production environments
3. **Test Events**: Use EventBridge test event feature to validate rules and targets before production deployment
4. **Gradual Rollout**: Deploy event-driven changes gradually using canary deployments or feature flags
5. **Rollback Procedures**: Maintain previous versions of event rules and patterns for quick rollback during incidents
6. **Local Development**: Use tools like LocalStack or SAM Local for local EventBridge testing and development
7. **CI/CD Integration**: Automate EventBridge resource deployment through CI/CD pipelines with proper validation and testing stages

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-eventbridge
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eventbridge/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-eventbridge/tree/master/examples
- **AWS EventBridge Documentation**: https://docs.aws.amazon.com/eventbridge/latest/userguide/what-is-amazon-eventbridge.html
- **Event Pattern Reference**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html
- **EventBridge Targets**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-targets.html
- **EventBridge Scheduler**: https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html
- **EventBridge Pipes**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes.html
- **API Destinations**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-api-destinations.html
- **Event Archives and Replay**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-archive-event.html
- **Schema Registry**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-schema.html
- **Cross-Account Events**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cross-account.html
- **EventBridge Security**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-security.html
- **EventBridge Best Practices**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-best-practices.html
- **AWS EventBridge Pricing**: https://aws.amazon.com/eventbridge/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Event Bus Strategy**: Determine whether to use default or custom event buses based on event source isolation requirements
2. **Event Pattern Design**: Create specific, well-defined event patterns with appropriate filtering to minimize unnecessary target invocations
3. **Target Selection**: Choose appropriate targets based on processing requirements (synchronous vs asynchronous, stateful vs stateless)
4. **IAM Permissions**: Ensure EventBridge has necessary IAM permissions to invoke targets; the module can create roles automatically
5. **Dead Letter Queues**: Always configure DLQ for production rules to capture and analyze failed event deliveries
6. **Retry Configuration**: Set appropriate retry policies (typically 3-5 retries with exponential backoff) for transient failures
7. **Event Transformation**: Use input transformers to reshape event payloads instead of wrapper Lambda functions for cost efficiency
8. **Scheduling Syntax**: Use correct cron or rate expression syntax; test schedules before production deployment
9. **Cross-Account Setup**: When routing events cross-account, configure both source permissions and target resource policies
10. **Archive Configuration**: Enable archives for critical event buses to support disaster recovery and debugging capabilities
11. **Monitoring**: Create CloudWatch alarms for FailedInvocations, ThrottledRules, and DLQ metrics to detect issues
12. **Tagging**: Apply comprehensive tags to all resources for cost allocation, governance, and resource management
13. **Security**: Use KMS encryption for sensitive event data and implement least privilege IAM policies
14. **API Destinations**: Store connection credentials securely in AWS Secrets Manager with automatic rotation
15. **Testing**: Use EventBridge test events feature to validate event patterns and rules before production deployment
