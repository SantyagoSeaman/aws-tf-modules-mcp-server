# Terraform AWS Step Functions Module

## Module Information

- **Module Name**: `step-functions`
- **Source**: `terraform-aws-modules/step-functions/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-step-functions
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/step-functions/aws/latest
- **Latest Version**: 5.1.0
- **Purpose**: Creates AWS Step Functions state machines with automatic IAM role and policy management for integrated AWS services
- **Service**: AWS Step Functions (Workflow Orchestration)
- **Category**: Workflow, Serverless, Orchestration
- **Keywords**: step-functions, state-machine, workflow, orchestration, serverless, lambda-integration, dynamodb-integration, sqs-integration, ecs-integration, service-integrations, iam-policies, cloudwatch-logging, kms-encryption
- **Use For**: microservices orchestration, ETL pipelines, order processing, saga pattern, batch job orchestration, ML pipelines, event-driven workflows, distributed transactions

## Description

This Terraform module simplifies the creation and management of AWS Step Functions state machines with automatic IAM role creation and pre-built policies for 20+ AWS service integrations. It handles the complexity of provisioning state machines along with their associated IAM roles, policies, CloudWatch Logs groups, and encryption configuration.

The module supports both Standard workflows (long-running, exactly-once execution) and Express workflows (high-volume, at-least-once execution). It provides five flexible methods to attach custom IAM policies and includes pre-configured service integrations for Lambda, DynamoDB, SQS, SNS, ECS, EKS, Batch, EventBridge, API Gateway, SageMaker, and more.

Part of the serverless.tf framework, this module follows best practices for infrastructure as code and integrates seamlessly with other AWS Terraform modules.

## Key Features

- **Standard and Express Types**: Support for both STANDARD (long-running) and EXPRESS (high-volume) workflow types
- **Automatic IAM Role Management**: Creates IAM roles with least-privilege permissions based on service integrations
- **20+ Service Integrations**: Pre-built policies for Lambda, DynamoDB, ECS, EKS, SQS, SNS, EventBridge, Batch, Glue, SageMaker, Athena, API Gateway, and more
- **5 Policy Attachment Methods**: Single ARN, multiple ARNs, JSON policy, multiple JSON policies, or dynamic policy statements
- **CloudWatch Logs Integration**: Optional log group creation with configurable retention and KMS encryption
- **KMS Encryption Support**: Encryption configuration for state machine data at rest
- **Conditional Resource Creation**: Fine-grained control with `create`, `create_role`, `use_existing_role` flags
- **Version Publishing**: State machine versioning support via `publish` parameter
- **Permissions Boundary Support**: Enforce organizational IAM limits via `role_permissions_boundary`
- **Comprehensive Tagging**: Tags for state machine, IAM role, and CloudWatch log group

## Main Use Cases

1. **Microservices Orchestration**: Coordinate workflows across distributed microservices
2. **ETL Data Pipelines**: Automate extract, transform, load processes with error handling
3. **Order Processing**: Multi-stage order fulfillment with inventory, payment, and shipping
4. **Saga Pattern**: Distributed transactions with compensating actions for failures
5. **Batch Job Orchestration**: Long-running batch processing with dependencies
6. **ML Pipelines**: Data preparation, model training, validation, and deployment
7. **Event-Driven Automation**: Reactive systems with complex business logic
8. **Human-in-the-Loop Workflows**: Approval workflows with wait states and callbacks

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the Step Function |
| `definition` | `string` | `""` | Amazon States Language JSON definition |
| `type` | `string` | `"STANDARD"` | Type: STANDARD or EXPRESS |
| `create` | `bool` | `true` | Whether to create Step Function resource |
| `create_role` | `bool` | `true` | Whether to create IAM role |
| `use_existing_role` | `bool` | `false` | Use an existing IAM role instead |
| `role_arn` | `string` | `""` | ARN of existing IAM role (when use_existing_role = true) |
| `publish` | `bool` | `false` | Create a version when state machine is created |
| `service_integrations` | `any` | `{}` | Map of AWS service integrations with resource ARNs |
| `attach_policies_for_integrations` | `bool` | `true` | Attach service integration policies to IAM role |
| `tags` | `map(string)` | `{}` | Tags for the Step Function |

### IAM Policy Attachment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `attach_policy` | `bool` | `false` | Attach single policy ARN |
| `policy` | `string` | `null` | Single policy ARN to attach |
| `attach_policies` | `bool` | `false` | Attach list of policy ARNs |
| `policies` | `list(string)` | `[]` | List of policy ARNs |
| `number_of_policies` | `number` | `0` | Number of policies to attach |
| `attach_policy_json` | `bool` | `false` | Attach JSON policy document |
| `policy_json` | `string` | `null` | JSON policy document |
| `attach_policy_statements` | `bool` | `false` | Attach dynamic policy statements |
| `policy_statements` | `any` | `{}` | Map of policy statements |

### CloudWatch Logs Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `logging_configuration` | `map(string)` | `{}` | Execution history logging configuration |
| `attach_cloudwatch_logs_policy` | `bool` | `true` | Attach CloudWatch Logs policy |
| `use_existing_cloudwatch_log_group` | `bool` | `false` | Use existing log group |
| `cloudwatch_log_group_name` | `string` | `null` | CloudWatch log group name |
| `cloudwatch_log_group_retention_in_days` | `number` | `null` | Log retention in days |
| `cloudwatch_log_group_kms_key_id` | `string` | `null` | KMS key ARN for log encryption |

### Encryption and IAM Role Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `encryption_configuration` | `any` | `{}` | Encryption config for state machine data |
| `role_name` | `string` | `null` | Custom IAM role name |
| `role_description` | `string` | `null` | IAM role description |
| `role_permissions_boundary` | `string` | `null` | Permissions boundary ARN |
| `trusted_entities` | `list(string)` | `[]` | Additional trusted entities for role |

## Main Outputs

| Output | Description |
|--------|-------------|
| `state_machine_arn` | ARN of the Step Function |
| `state_machine_id` | ID of the Step Function (same as ARN) |
| `state_machine_name` | Name of the Step Function |
| `state_machine_status` | Current status of the Step Function |
| `state_machine_creation_date` | Creation date of the Step Function |
| `state_machine_version_arn` | ARN of state machine version |
| `role_arn` | ARN of the IAM role |
| `role_name` | Name of the IAM role |
| `cloudwatch_log_group_arn` | ARN of the CloudWatch log group |
| `cloudwatch_log_group_name` | Name of the CloudWatch log group |

## Usage Examples

### Basic Step Function

```hcl
module "step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "~> 5.0"

  name = "my-step-function"
  type = "STANDARD"

  definition = <<EOF
{
  "Comment": "A Hello World example",
  "StartAt": "Hello",
  "States": {
    "Hello": {
      "Type": "Pass",
      "Result": "Hello",
      "Next": "World"
    },
    "World": {
      "Type": "Pass",
      "Result": "World",
      "End": true
    }
  }
}
EOF

  tags = {
    Environment = "production"
  }
}
```

### With Lambda and DynamoDB Integration

```hcl
module "step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "~> 5.0"

  name       = "order-processing"
  type       = "STANDARD"
  definition = local.order_workflow_definition

  service_integrations = {
    lambda = {
      lambda = [
        module.validate_order_lambda.lambda_function_arn,
        module.process_payment_lambda.lambda_function_arn,
        module.ship_order_lambda.lambda_function_arn,
      ]
    }

    dynamodb = {
      dynamodb = [aws_dynamodb_table.orders.arn]
    }

    sqs = {
      sqs = [aws_sqs_queue.notifications.arn]
    }
  }

  tags = {
    Application = "order-system"
  }
}
```

### Express Workflow with CloudWatch Logging

```hcl
module "express_step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "~> 5.0"

  name       = "high-volume-processor"
  type       = "EXPRESS"
  definition = local.processor_definition

  logging_configuration = {
    include_execution_data = true
    level                  = "ALL"
  }

  cloudwatch_log_group_retention_in_days = 7

  service_integrations = {
    lambda = {
      lambda = [module.processor_lambda.lambda_function_arn]
    }
    xray = {
      xray = true
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### With Custom IAM Policy Statements

```hcl
module "step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "~> 5.0"

  name       = "data-pipeline"
  definition = local.pipeline_definition

  # Method 5: Dynamic policy statements
  attach_policy_statements = true
  policy_statements = {
    s3_read = {
      effect    = "Allow"
      actions   = ["s3:GetObject", "s3:ListBucket"]
      resources = [
        aws_s3_bucket.data.arn,
        "${aws_s3_bucket.data.arn}/*"
      ]
    }
    secrets_read = {
      effect    = "Allow"
      actions   = ["secretsmanager:GetSecretValue"]
      resources = [aws_secretsmanager_secret.api_key.arn]
    }
  }

  tags = {
    Pipeline = "data-processing"
  }
}
```

### Using Existing IAM Role

```hcl
module "step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "~> 5.0"

  name       = "existing-role-sfn"
  definition = local.definition

  use_existing_role = true
  role_arn          = aws_iam_role.step_functions.arn

  # Don't create a new role
  create_role = false
}
```

## Service Integrations Reference

The `service_integrations` map supports the following AWS services:

| Service | Key | Description |
|---------|-----|-------------|
| Lambda | `lambda` | Invoke Lambda functions |
| DynamoDB | `dynamodb` | Read/write DynamoDB tables |
| SQS | `sqs` | Send messages to SQS queues |
| SNS | `sns` | Publish to SNS topics |
| ECS | `ecs` | Run ECS tasks |
| EKS | `eks` | Run EKS tasks |
| Batch | `batch` | Submit Batch jobs |
| EventBridge | `events` | Put events to EventBridge |
| Step Functions | `stepfunction`, `stepfunction_Sync` | Invoke other state machines |
| API Gateway | `apigateway` | Invoke API Gateway endpoints |
| SageMaker | `sagemaker` | SageMaker operations |
| Glue | `glue` | Glue job operations |
| Athena | `athena` | Athena query execution |
| EMR | `emr` | EMR cluster operations |
| X-Ray | `xray` | Enable X-Ray tracing |

### Service Integration Format

```hcl
service_integrations = {
  # Using specific resource ARNs
  lambda = {
    lambda = ["arn:aws:lambda:region:account:function:name"]
  }

  # Using default resources (for services that support it)
  xray = {
    xray = true
  }

  # Multiple resource types
  dynamodb = {
    dynamodb = ["arn:aws:dynamodb:region:account:table/table-name"]
  }
}
```

## Best Practices

### State Machine Design

1. **Use EXPRESS for High-Volume**: For >4000 executions/second or duration <5 minutes
2. **Implement Idempotency**: Design tasks to safely handle retries
3. **Keep Payloads Small**: Stay under 256KB by using S3 references for large data
4. **Use Parallel States**: Execute independent tasks concurrently

### IAM and Security

1. **Scope Service Integrations**: Specify exact resource ARNs, avoid wildcards
2. **Enable KMS Encryption**: For sensitive data at rest
3. **Use Permissions Boundaries**: Enforce organizational limits
4. **EventBridge Permissions**: Set `events = true` when using `stepfunction_Sync`

### Logging and Monitoring

1. **Enable Logging**: Use `logging_configuration` for execution history
2. **Set Retention**: Configure `cloudwatch_log_group_retention_in_days`
3. **Enable X-Ray**: For distributed tracing with `xray = true`
4. **Monitor Metrics**: Create alarms for ExecutionsFailed, ExecutionsTimedOut

### Operations

1. **Version State Machines**: Use `publish = true` for rollback capability
2. **Validate Definitions**: Test ASL JSON before deployment
3. **Use Terraform Templates**: Parameterize definitions for environments

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-step-functions
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/step-functions/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-step-functions/tree/master/examples
- **AWS Step Functions Documentation**: https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html
- **Amazon States Language Specification**: https://states-language.net/spec.html
- **Step Functions Best Practices**: https://docs.aws.amazon.com/step-functions/latest/dg/best-practices.html
- **Service Integrations Guide**: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-service-integrations.html
- **Standard vs Express Workflows**: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html
- **Step Functions Pricing**: https://aws.amazon.com/step-functions/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Definition Validation**: Validate ASL JSON syntax before applying; use `jsonencode()` for Terraform-generated definitions
2. **Service Integration Patterns**: Use the module's `service_integrations` map for common AWS services rather than custom IAM policies
3. **Type Selection**: Choose EXPRESS for event-driven, high-volume workloads; STANDARD for long-running, auditable processes
4. **Encryption**: Enable KMS encryption for workflows processing sensitive data
5. **Logging**: Balance logging verbosity with cost; avoid logging sensitive data in production
6. **Existing Resources**: Use `use_existing_role = true` with `role_arn` for shared infrastructure patterns
7. **Conditional Creation**: Use `create`, `create_role` flags for flexible resource management
8. **Version Publishing**: Enable `publish = true` for production workflows requiring rollback
9. **EventBridge Integration**: When using `stepfunction_Sync`, include `events = true` to avoid permission errors
10. **No Submodules**: This module has no submodules; all configuration is at the root level
