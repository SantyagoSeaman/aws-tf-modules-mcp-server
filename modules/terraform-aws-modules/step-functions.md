# Terraform AWS Step Functions Module

## Module Information

- **Module Name**: `step-functions`
- **Module ID**: `terraform-aws-modules/step-functions/aws`
- **Source**: `terraform-aws-modules/step-functions/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-step-functions
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/step-functions/aws/latest
- **Latest Version**: 5.1.0
- **Purpose**: Creates an AWS Step Functions state machine together with its IAM role and pre-built IAM policies for 35+ AWS service integration patterns
- **Service**: AWS Step Functions (Workflow Orchestration)
- **Category**: Workflow, Serverless, Orchestration
- **Keywords**: step-functions, state-machine, sfn, workflow, orchestration, serverless, asl, states-language, standard-express, service-integrations, lambda, dynamodb, iam-role, cloudwatch-logs, kms-encryption, xray-tracing, saga-pattern
- **Use For**: microservices orchestration, ETL pipelines, order processing, saga pattern / distributed transactions, batch job orchestration, ML training pipelines, event-driven automation, human-in-the-loop approval workflows

## Description

This module provisions a single AWS Step Functions state machine (`aws_sfn_state_machine`) along with the supporting IAM role, IAM policies, and optional CloudWatch Logs log group needed to run it. It is maintained as part of the [serverless.tf framework](https://github.com/antonbabenko/serverless.tf) and is designed to remove the boilerplate of hand-writing IAM policy documents for every AWS service a state machine calls into.

Its defining feature is the `service_integrations` variable: a map of 35+ pre-built IAM policy templates (keyed by service and, for many services, by specific API action / integration pattern such as `.sync` or `.waitForTaskToken`) mirroring AWS's [service integration IAM templates](https://docs.aws.amazon.com/step-functions/latest/dg/service-integration-iam-templates.html). Enabling an integration attaches exactly the permissions that pattern needs, scoped to the resource ARNs supplied, instead of requiring a custom `aws_iam_policy_document`. Beyond built-in integrations, the module offers five additional ways to attach custom IAM policies (single ARN, list of ARNs, JSON document, list of JSON documents, or dynamic policy statements) for anything not covered by the built-in map.

The module also manages CloudWatch Logs execution logging (with configurable retention and optional KMS-encrypted log group), AWS-owned or customer-managed KMS encryption of state machine data at rest, X-Ray tracing (auto-enabled when the `xray` integration is used), state machine versioning via `publish`, and the option to bring your own IAM role instead of creating one. It supports both `STANDARD` (long-running, exactly-once, full execution history) and `EXPRESS` (high-throughput, at-least-once) state machine types. The module has no submodules; everything is configured through root-level input variables.

## Key Features

- **Automatic IAM Role & Policy Management**: Creates a least-privilege IAM role and generates policies from declarative input instead of hand-written policy JSON
- **35+ Pre-Built Service Integrations**: Ready-made policies for Lambda, DynamoDB, SNS, SQS, ECS, EKS, Batch, Glue, SageMaker, Athena, EMR, CodeBuild, API Gateway, EventBridge, nested Step Functions, and X-Ray, including action/pattern-specific variants (e.g. `ecs_Sync`, `batch_WaitForTaskToken`)
- **STANDARD & EXPRESS Types**: `type` accepts either value (case-insensitive; the module normalizes it to uppercase internally)
- **5 Ways to Attach Custom IAM Policies**: single ARN (`policy`), list of ARNs (`policies`), single JSON document (`policy_json`), list of JSON documents (`policy_jsons`), or dynamic policy statements (`policy_statements`)
- **Deny-All Escape Hatch**: `service_integrations.no_tasks.deny_all = true` overrides every other attached policy — useful for a locked-down "no permissions" state machine
- **CloudWatch Logs Integration**: Optional execution-history log group with configurable retention, tags, and KMS encryption; disabled by default unless `logging_configuration.level` is set to something other than `OFF`
- **KMS Encryption at Rest**: `encryption_configuration` supports `AWS_OWNED_KEY` or `CUSTOMER_MANAGED_KMS_KEY` with configurable data-key reuse period
- **X-Ray Tracing**: Automatically enables `tracing_configuration` when `service_integrations.xray.xray = true` is set — no separate flag needed
- **Bring-Your-Own-Role**: `use_existing_role = true` with `role_arn` skips role/policy creation entirely for shared-infrastructure patterns
- **Conditional Resource Creation**: `create` and `create_role` flags allow disabling all or part of the module's resources
- **Version Publishing**: `publish = true` creates a state machine version on each apply (exposed via `state_machine_version_arn`) for rollback support
- **Per-Resource Region Override**: `region` variable allows placing the state machine in a region different from the default provider region (AWS provider v6+ pattern)

## Main Use Cases

1. **Microservices Orchestration**: Coordinate calls across distributed Lambda/ECS/EKS services with built-in retry and error handling
2. **ETL / Data Pipelines**: Chain Glue jobs, Athena queries, and EMR steps with the module's pre-built Glue/Athena/EMR integrations
3. **Order Processing**: Multi-stage fulfillment combining Lambda, DynamoDB, and SQS/SNS notifications
4. **Saga Pattern / Distributed Transactions**: Compensating-action workflows across multiple services
5. **Batch Job Orchestration**: Submit and wait on AWS Batch jobs via the `batch_Sync` / `batch_WaitForTaskToken` integrations
6. **ML Training Pipelines**: Orchestrate SageMaker training and transform jobs via `sagemaker_CreateTrainingJob_Sync` / `sagemaker_CreateTransformJob_Sync`
7. **Event-Driven Automation**: React to EventBridge events and fan out to downstream services
8. **Human-in-the-Loop Workflows**: Approval workflows using wait states and callback (`waitForTaskToken`) patterns
9. **Nested / Cross-Account State Machines**: Invoke other state machines synchronously via `stepfunction_Sync`
10. **CI/CD Orchestration**: Drive CodeBuild builds (`codebuild_StartBuild_Sync`) as part of a larger deployment workflow

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the Step Function |
| `definition` | `string` | `""` | Amazon States Language (ASL) JSON definition |
| `type` | `string` | `"STANDARD"` | `STANDARD` or `EXPRESS` (case-insensitive) |
| `create` | `bool` | `true` | Whether to create the Step Function resource |
| `publish` | `bool` | `false` | Create a state machine version on each apply |
| `service_integrations` | `any` | `{}` | Map of pre-built AWS service integration IAM policies to attach (see reference table below) |
| `attach_policies_for_integrations` | `bool` | `true` | Whether to attach the `service_integrations` policies to the IAM role |
| `encryption_configuration` | `any` | `{}` | KMS encryption config: `{ type, kms_key_id, kms_data_key_reuse_period_seconds }` |
| `logging_configuration` | `map(string)` | `{}` | Execution logging config: `{ level, include_execution_data, log_destination }`; logging is disabled unless `level != "OFF"` |
| `sfn_state_machine_timeouts` | `map(string)` | `{}` | `create`/`update`/`delete` Terraform operation timeouts |
| `region` | `string` | `null` | Region to manage the resource in; defaults to the provider's region |
| `tags` | `map(string)` | `{}` | Tags applied to the Step Function |

### IAM Role Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_role` | `bool` | `true` | Whether to create an IAM role for the Step Function |
| `use_existing_role` | `bool` | `false` | Use an existing IAM role instead of creating one |
| `role_arn` | `string` | `""` | ARN of an existing IAM role (required when `use_existing_role = true`) |
| `role_name` | `string` | `null` | Custom IAM role name (defaults to `var.name`) |
| `role_description` | `string` | `null` | IAM role description |
| `role_path` | `string` | `null` | Path for the IAM role |
| `role_permissions_boundary` | `string` | `null` | Permissions boundary ARN for the IAM role |
| `role_force_detach_policies` | `bool` | `true` | Force-detach policies from the role before destroying it |
| `role_tags` | `map(string)` | `{}` | Tags applied to the IAM role |
| `trusted_entities` | `list(string)` | `[]` | Additional principals allowed to assume the role |
| `aws_region_assume_role` | `string` | `""` | AWS region(s) from which the role can be assumed by Step Functions |
| `policy_path` | `string` | `null` | Path used for the IAM policies the module creates |

### Custom Policy Attachment Variables (5 methods)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `attach_policy` | `bool` | `false` | Attach a single existing policy ARN (`policy`) |
| `policy` | `string` | `null` | Existing policy ARN to attach |
| `attach_policies` | `bool` | `false` | Attach a list of existing policy ARNs (`policies`) |
| `policies` | `list(string)` | `[]` | List of existing policy ARNs |
| `number_of_policies` | `number` | `0` | Count of ARNs in `policies` (required when `attach_policies = true`) |
| `attach_policy_json` | `bool` | `false` | Attach a single inline JSON policy document (`policy_json`) |
| `policy_json` | `string` | `null` | JSON policy document string |
| `attach_policy_jsons` | `bool` | `false` | Attach a list of inline JSON policy documents (`policy_jsons`) |
| `policy_jsons` | `list(string)` | `[]` | List of JSON policy document strings |
| `number_of_policy_jsons` | `number` | `0` | Count of documents in `policy_jsons` (required when `attach_policy_jsons = true`) |
| `attach_policy_statements` | `bool` | `false` | Attach dynamically generated policy statements (`policy_statements`) |
| `policy_statements` | `any` | `{}` | Map of `{ effect, actions, resources, ... }` statements |

### CloudWatch Logs Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `attach_cloudwatch_logs_policy` | `bool` | `true` | Attach the CloudWatch Logs write policy to the IAM role |
| `use_existing_cloudwatch_log_group` | `bool` | `false` | Use an existing log group instead of creating one |
| `cloudwatch_log_group_name` | `string` | `null` | CloudWatch log group name |
| `cloudwatch_log_group_retention_in_days` | `number` | `null` | Log retention in days (e.g. `1, 3, 5, 7, 14, 30, ...`) |
| `cloudwatch_log_group_kms_key_id` | `string` | `null` | KMS key ARN for log group encryption |
| `cloudwatch_log_group_tags` | `map(string)` | `{}` | Tags applied to the CloudWatch log group |

## Main Outputs

| Output | Description |
|--------|-------------|
| `state_machine_arn` | ARN of the Step Function |
| `state_machine_id` | ID of the Step Function (same value as ARN) |
| `state_machine_name` | Name of the Step Function |
| `state_machine_status` | Current status of the Step Function |
| `state_machine_creation_date` | Creation date of the Step Function |
| `state_machine_version_arn` | ARN of the published state machine version (when `publish = true`) |
| `role_arn` | ARN of the IAM role created for the Step Function |
| `role_name` | Name of the IAM role created for the Step Function |
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

### With Lambda, DynamoDB, and SQS Integrations

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

### Express Workflow with Logging, X-Ray, and KMS Encryption

```hcl
module "express_step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "~> 5.0"

  name       = "high-volume-processor"
  type       = "EXPRESS"
  definition = local.processor_definition
  publish    = true

  encryption_configuration = {
    type                              = "CUSTOMER_MANAGED_KMS_KEY"
    kms_key_id                        = aws_kms_key.sfn.arn
    kms_data_key_reuse_period_seconds = 600
  }

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

### .sync Integration Pattern (Batch + EventBridge)

```hcl
module "step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "~> 5.0"

  name       = "batch-job-pipeline"
  definition = local.batch_pipeline_definition

  service_integrations = {
    # `.sync` / `.waitForTaskToken` integrations need `events = true` (or explicit
    # rule ARNs) so Step Functions can create the managed EventBridge rule that
    # tracks job completion. Omitting it raises:
    #   AccessDeniedException: '...' is not authorized to create managed-rule
    batch_Sync = {
      events = true
    }
  }

  tags = {
    Pipeline = "batch-processing"
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

  # Method 5: dynamic policy statements — use for anything not covered
  # by a built-in service_integrations entry
  attach_policy_statements = true
  policy_statements = {
    s3_read = {
      effect  = "Allow"
      actions = ["s3:GetObject", "s3:ListBucket"]
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

### Using an Existing IAM Role

```hcl
module "step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "~> 5.0"

  name       = "existing-role-sfn"
  definition = local.definition

  create_role       = false
  use_existing_role = true
  role_arn          = aws_iam_role.step_functions.arn
}
```

## Service Integrations Reference

`service_integrations` is a map keyed by integration name; each value is itself a map supplying the resource ARNs (or `true` to use the AWS default resource, where supported) required by that integration's built-in policy. Many services expose multiple keys — one per specific API action or execution pattern (`.sync`, `.waitForTaskToken`) — mirroring AWS's [service integration IAM templates](https://docs.aws.amazon.com/step-functions/latest/dg/service-integration-iam-templates.html).

| Service | Available Keys |
|---------|-----------------|
| Lambda | `lambda` |
| DynamoDB | `dynamodb` |
| SNS | `sns` |
| SQS | `sqs` |
| X-Ray | `xray` (also enables `tracing_configuration`) |
| ECS | `ecs_Sync`, `ecs_WaitForTaskToken` |
| EKS | `eks_CreateCluster`, `eks_CreateNodeGroup`, `eks_DeleteCluster`, `eks_DeleteNodegroup` |
| Batch | `batch_Sync`, `batch_WaitForTaskToken` |
| Glue | `glue_Sync`, `glue_WaitForTaskToken` |
| Athena | `athena_StartQueryExecution_Sync`, `athena_StartQueryExecution`, `athena_StopQueryExecution`, `athena_GetQueryExecution`, `athena_GetQueryResults` |
| SageMaker | `sagemaker_CreateTrainingJob_Sync`, `sagemaker_CreateTrainingJob_WaitForTaskToken`, `sagemaker_CreateTransformJob_Sync`, `sagemaker_CreateTransformJob_WaitForTaskToken` |
| EMR | `emr_AddStep`, `emr_CancelStep`, `emr_CreateCluster`, `emr_SetClusterTerminationProtection`, `emr_ModifyInstanceFleetByName`, `emr_ModifyInstanceGroupByName`, `emr_TerminateCluster` |
| CodeBuild | `codebuild_StartBuild_Sync`, `codebuild_StartBuild`, `codebuild_StopBuild`, `codebuild_BatchDeleteBuilds`, `codebuild_BatchGetReports` |
| API Gateway | `apigateway` |
| Step Functions (nested) | `stepfunction`, `stepfunction_Sync` |
| EventBridge | `eventbridge` |
| Deny All | `no_tasks` (`{ deny_all = true }`) — overrides every other attached policy, including logging |

```hcl
service_integrations = {
  # Explicit resource ARNs
  lambda = {
    lambda = ["arn:aws:lambda:region:account:function:name"]
  }

  # `true` uses the service's default/wildcard resource, where supported
  xray = {
    xray = true
  }

  # `.sync` patterns generally need `events = true` for the managed EventBridge rule
  ecs_Sync = {
    ecs           = ["arn:aws:ecs:region:account:task-definition/name"]
    ecs_Wildcard  = ["arn:aws:ecs:region:account:task/*"]
    iam_PassRole  = [aws_iam_role.ecs_task.arn]
    events        = true
  }
}
```

## Best Practices

### State Machine Design

1. **Choose EXPRESS for High-Volume, Short-Lived Workflows**: Use `EXPRESS` when throughput exceeds ~4000 executions/second or executions complete within minutes; use `STANDARD` when you need full execution history, exactly-once semantics, or executions can run up to a year.
2. **Design Idempotent Tasks**: `STANDARD` workflows retry on failure and may invoke a task more than once — tasks must tolerate duplicate execution.
3. **Keep Payloads Under 256 KB**: Pass S3 object references instead of large payloads between states.
4. **Use Parallel/Map States for Independent Work**: Fan out concurrent branches instead of sequential chains where dependencies allow.

### IAM and Security

1. **Prefer `service_integrations` Over Custom Policies**: Use the built-in integration keys for supported services instead of writing custom `policy_statements`; it keeps permissions scoped to the exact API actions the integration pattern needs.
2. **Scope Resource ARNs Precisely**: Pass exact resource ARNs into `service_integrations` rather than `true`/wildcards wherever the integration supports it.
3. **Remember `events = true` for `.sync` / `.waitForTaskToken` Integrations**: ECS, Batch, Glue, SageMaker, EMR, CodeBuild, and `stepfunction_Sync` integrations create a managed EventBridge rule; omitting `events` causes an `AccessDeniedException` at runtime, not at plan time.
4. **Apply a Permissions Boundary in Multi-Tenant Accounts**: Set `role_permissions_boundary` to enforce organizational IAM limits on the generated role.
5. **Encrypt Sensitive State Data**: Set `encryption_configuration.type = "CUSTOMER_MANAGED_KMS_KEY"` for workflows handling sensitive payloads.

### Logging, Tracing, and Operations

1. **Enable Execution Logging Deliberately**: Logging is off by default (`logging_configuration.level` defaults to unset/`OFF`); set `level = "ALL"` or `"ERROR"` and `include_execution_data` carefully — `ALL` with execution data can log sensitive payloads.
2. **Set Log Retention**: Always set `cloudwatch_log_group_retention_in_days` to avoid indefinite (never-expiring) log storage costs.
3. **Enable X-Ray for Distributed Tracing**: Set `service_integrations.xray.xray = true` to trace calls across integrated services.
4. **Version Before Production Rollouts**: Use `publish = true` and consume `state_machine_version_arn` so you can roll back to a prior version.
5. **Validate ASL Before Apply**: Lint/validate the Amazon States Language JSON (e.g. with the [Step Functions VS Code extension](https://docs.aws.amazon.com/step-functions/latest/dg/statemachine-graph-view.html) or `aws stepfunctions validate-state-machine-definition`) before passing it into `definition`.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-step-functions
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/step-functions/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-step-functions/tree/master/examples/complete
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-step-functions/blob/master/CHANGELOG.md
- **AWS Step Functions Documentation**: https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html
- **Amazon States Language Specification**: https://states-language.net/spec.html
- **Service Integration IAM Templates**: https://docs.aws.amazon.com/step-functions/latest/dg/service-integration-iam-templates.html
- **Standard vs Express Workflows**: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html
- **Step Functions Pricing**: https://aws.amazon.com/step-functions/pricing/
- **serverless.tf Framework**: https://github.com/antonbabenko/serverless.tf

## Notes for AI Agents

When using this module in automated workflows:

1. **Definition Validation**: Generate `definition` with `jsonencode()` when building the ASL from Terraform data rather than hand-interpolating heredoc JSON, to avoid syntax errors.
2. **Prefer `service_integrations` Over Custom Policies**: Reach for the pre-built map before `policy_statements`/`policy_json`; it is less error-prone and self-documents which AWS services the state machine calls.
3. **`.sync` / `.waitForTaskToken` Needs `events = true`**: For `ecs_Sync`, `batch_Sync`, `glue_Sync`, `sagemaker_*_Sync`, `emr_*`, `codebuild_*_Sync`, and `stepfunction_Sync`, always include `events = true` (or explicit EventBridge rule ARNs) unless you already know the target rule exists.
4. **Type is Case-Insensitive**: `type = "express"` and `type = "EXPRESS"` both work — the module uppercases it internally — but prefer uppercase for readability/consistency with AWS docs.
5. **Logging is Off by Default**: Set `logging_configuration.level` explicitly (`ALL`, `ERROR`, `FATAL`) if execution history logging is required; no CloudWatch log group is created otherwise.
6. **X-Ray Needs No Separate Flag**: Setting `service_integrations.xray.xray = true` both grants the IAM permission and enables `tracing_configuration` — do not look for a separate `enable_xray` variable.
7. **Existing-Role Pattern**: For shared infrastructure, set `create_role = false`, `use_existing_role = true`, and supply `role_arn`.
8. **Enable `publish = true` for Production**: This exposes `state_machine_version_arn`, needed for safe rollback and for pinning aliases/triggers to a specific version.
9. **No Submodules**: This module has a single root module with no submodules; all configuration happens through the variables above.
10. **Encryption Requires a `type` Key**: `encryption_configuration` is an `any`-typed map but the underlying resource requires `type` to be `"AWS_OWNED_KEY"` or `"CUSTOMER_MANAGED_KMS_KEY"` — an empty map (the default) means encryption configuration is omitted entirely, not disabled-with-defaults.
