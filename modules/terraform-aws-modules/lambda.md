# Terraform AWS Lambda Module

## Module Information

- **Module Name**: `lambda`
- **Source**: `terraform-aws-modules/lambda/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-lambda
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/latest
- **Latest Version**: 8.8.1
- **Purpose**: Terraform module that creates and manages AWS Lambda functions, layers, and aliases, including building and packaging deployment artifacts
- **Service**: AWS Lambda (Serverless Compute)
- **Category**: Compute, Serverless, Application Integration
- **Keywords**: lambda, serverless, faas, lambda-layer, lambda-alias, lambda-edge, container-image, event-source-mapping, provisioned-concurrency, function-url, dead-letter-queue, codedeploy, canary-deployment, docker-build, vpc-lambda
- **Use For**: API backend implementation, event-driven data processing, real-time file processing, scheduled task automation, microservices architecture, stream processing from Kinesis or DynamoDB, IoT data processing, chatbot and voice assistant backends, image and video processing, ETL workflows, serverless web applications, webhook handlers

## Description

This Terraform module provides comprehensive management of AWS Lambda resources — Functions, Layers, and Aliases — and, uniquely among most Lambda modules, also owns the build and packaging pipeline that turns application source code into a deployable artifact. It is part of the serverless.tf framework and handles the full lifecycle from dependency installation (pip/poetry for Python, npm for Node.js, or arbitrary custom build commands), through zip-archive creation with content-based hashing (to avoid unnecessary redeployments), to storing the package locally or in S3 and deploying it. It supports .zip-file deployments, container images from ECR, and Lambda@Edge, and can build dependencies either on the local machine or inside Docker (including private package installs via a forwarded SSH agent).

The module addresses the operational complexity of running Lambda in production: VPC networking (subnets, security groups), EFS mounts, dead-letter queues and asynchronous invocation configuration, event source mappings (SQS, Kinesis, DynamoDB Streams, MSK, Amazon MQ, etc.), Function URLs with CORS, code signing, provisioned/reserved concurrency, X-Ray tracing, structured CloudWatch logging with configurable retention/encryption, and six independent methods of attaching IAM policies to the execution role (inline JSON, JSON list, managed policy ARN, ARN list, generated policy statements, and assume-role trust statements). It also exposes newer AWS Lambda capabilities such as SnapStart, tenant isolation mode, Managed Instances capacity providers, and Durable Functions (execution-state retention/timeout configuration).

Because creating a Lambda Function and a Lambda Layer share almost identical mechanics, the same module root is used for both (toggled via `create_layer`). Controlled, zero-downtime deployment strategies — rolling updates, canary releases, weighted traffic shifting, and automatic rollback — are implemented through two companion submodules (`alias` and `deploy`) that build on top of Lambda aliases and AWS CodeDeploy, while a third submodule (`docker-build`) builds and pushes container images to ECR for container-based Lambda deployments. The module supports conditional resource creation throughout (`create`, `create_function`, `create_layer`, `create_role`, etc.), making it composable for advanced, multi-module serverless architectures.

## Key Features

- **Build & Package Pipeline**: Installs dependencies (pip, poetry, npm) and builds deployment zip-archives with content-based hashing to avoid needless redeploys
- **Docker Builds**: Builds dependencies inside Docker (with optional SSH agent forwarding) for any runtime/architecture, decoupled from the local toolchain
- **Flexible Source Composition**: `source_path` accepts a single directory, a list of directories/files, or per-entry build config (patterns, commands, prefix-in-zip) for complex multi-source packages
- **Multiple Deployment Origins**: Deploy a freshly built package, an existing local zip, a package already in S3, or a container image from ECR
- **S3 or Local Package Storage**: Store built artifacts locally or centrally in S3 (`store_on_s3`)
- **Lambda Layers**: Same module creates Layers (`create_layer = true`) for shared code/dependencies, reusable across functions
- **Lambda@Edge**: First-class support for edge functions deployed to CloudFront (`lambda_at_edge = true`)
- **VPC & EFS Integration**: Attaches Lambda to VPC subnets/security groups and mounts EFS access points for persistent storage
- **Event Source Mapping**: Native configuration of triggers from SQS, Kinesis, DynamoDB Streams, MSK, and Amazon MQ
- **Function URLs**: Direct HTTPS invocation endpoints with IAM or NONE authorization, CORS, and buffered/response-streaming invoke modes
- **Six IAM Policy Attachment Methods**: `policy_json(s)`, `policy`/`policies` (ARNs), `policy_statements`, and `assume_role_policy_statements` for the trust policy
- **Provisioned & Reserved Concurrency**: Pre-warmed execution environments for latency-sensitive workloads and hard caps on concurrent executions
- **Code Signing & Encryption**: Code signing configuration, KMS-encrypted environment variables, and KMS-encrypted CloudWatch Logs/S3 artifacts
- **Newer Lambda Capabilities**: SnapStart, tenant isolation mode, Managed Instances capacity provider, Durable Functions (execution timeout/retention)
- **Controlled Deployments via Submodules**: `alias` submodule for weighted/blue-green routing, `deploy` submodule for AWS CodeDeploy-orchestrated rollouts with auto-rollback
- **Container Image Builds**: `docker-build` submodule builds and pushes images to ECR (including buildx/multi-stage builds) ready for `package_type = "Image"`
- **Conditional Creation**: Every resource group (function, layer, role, package, policies) can be toggled independently for composable architectures

## Main Use Cases

1. **REST API Backends**: Implement serverless API endpoints with Function URLs or API Gateway integration
2. **Event-Driven Processing**: Process events from S3, DynamoDB, Kinesis, SQS, SNS, or EventBridge
3. **Scheduled Tasks**: Run cron jobs and scheduled automation using EventBridge rules
4. **Real-Time Stream Processing**: Process streaming data from Kinesis, DynamoDB Streams, or MSK
5. **File Processing**: Automatically process uploaded files from S3 with image resizing, transcoding, or ETL
6. **Microservices Architecture**: Build distributed applications with Lambda as microservice components
7. **Webhook Handlers**: Receive and process webhooks from third-party services
8. **Container-Based Workloads**: Deploy larger or dependency-heavy functions as container images from ECR
9. **Controlled Production Rollouts**: Canary/blue-green deployments via CodeDeploy with automatic alarm-based rollback
10. **Edge Compute**: Run request/response manipulation logic at CloudFront edge locations with Lambda@Edge

## Main Module: Lambda Function / Layer

### Description

The main module (root of the source) creates and manages an AWS Lambda Function or, when `create_layer = true`, a Lambda Layer, handling everything from source-code build/packaging to deployment. It supports all package sources (local build, existing local zip, existing S3 object, container image) and advanced configuration including VPC networking, EFS, async invocation, event source mappings, Function URLs, and IAM policy management.

### Key Features

- Complete Lambda function/layer lifecycle management from build to deployment
- Automated dependency installation and package building (local or Docker)
- Support for all AWS Lambda runtimes and both x86_64/arm64 architectures
- Flexible IAM policy attachment with six independent methods
- VPC, EFS, and networking configuration
- Event source mapping and trigger (`allowed_triggers`) management
- CloudWatch Logs, X-Ray tracing, and Function URL support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `function_name` | `string` | `""` | Unique name for the Lambda function |
| `handler` | `string` | `""` | Function entry point (e.g., `index.handler`) |
| `runtime` | `string` | `""` | Lambda runtime (e.g., `python3.12`, `nodejs20.x`) |
| `source_path` | `any` | `null` | Path (or list of paths/build configs) to function source code |
| `create` | `bool` | `true` | Master switch for all resources created by the module |
| `create_function` | `bool` | `true` | Whether to create the Lambda Function |
| `create_layer` | `bool` | `false` | Whether to create a Lambda Layer instead of/alongside a function |
| `timeout` | `number` | `3` | Function timeout in seconds (max 900) |
| `memory_size` | `number` | `128` | Memory allocated to the function in MB (128–10,240) |
| `architectures` | `list(string)` | `null` | `["x86_64"]` or `["arm64"]` |
| `environment_variables` | `map(string)` | `{}` | Environment variables for the function |
| `layers` | `list(string)` | `null` | List of Lambda Layer version ARNs (max 5) |
| `vpc_subnet_ids` / `vpc_security_group_ids` | `list(string)` | `null` | VPC placement for the function |
| `attach_policy_json` / `policy_json` | `bool` / `string` | `false` / `null` | Attach an inline IAM policy JSON document |
| `attach_policy_statements` / `policy_statements` | `bool` / `any` | `false` / `{}` | Attach IAM policy generated from statement maps |
| `attach_cloudwatch_logs_policy` | `bool` | `true` | Whether to attach the CloudWatch Logs policy |
| `cloudwatch_logs_retention_in_days` | `number` | `null` | Log group retention period |
| `create_package` | `bool` | `true` | Whether the module should build a deployment package |
| `local_existing_package` | `string` | `null` | Path to an existing zip to deploy (skips build) |
| `store_on_s3` / `s3_bucket` | `bool` / `string` | `false` / `null` | Store the built package in S3 instead of locally |
| `package_type` | `string` | `"Zip"` | `"Zip"` or `"Image"` |
| `image_uri` | `string` | `null` | ECR image URI when `package_type = "Image"` |
| `publish` | `bool` | `false` | Whether to publish a new Lambda version on change |
| `reserved_concurrent_executions` | `number` | `-1` | Reserved concurrency (`-1` = unreserved) |
| `provisioned_concurrent_executions` | `number` | `-1` | Provisioned concurrency (`>=1` enables, `0` disables) |
| `create_lambda_function_url` | `bool` | `false` | Whether to create a Lambda Function URL |
| `authorization_type` / `cors` / `invoke_mode` | `string` / `any` / `string` | `"NONE"` / `{}` / `null` | Function URL auth, CORS, and invoke mode (`BUFFERED`/`RESPONSE_STREAM`) |
| `tracing_mode` | `string` | `null` | X-Ray tracing mode (`Active` or `PassThrough`) |
| `event_source_mapping` | `any` | `{}` | Map of event source mapping configurations (SQS, Kinesis, DynamoDB Streams, etc.) |
| `allowed_triggers` | `map(any)` | `{}` | Map of Lambda permissions for invoking services/principals |
| `dead_letter_target_arn` | `string` | `null` | SNS topic/SQS queue ARN for failed async invocations |
| `snap_start` | `bool` | `false` | Enable SnapStart for supported runtimes |
| `tenant_isolation_mode` | `bool` | `false` | Enable tenant isolation mode |
| `durable_config_execution_timeout` / `durable_config_retention_period` | `number` | `null` | Durable Functions execution timeout and state retention |
| `build_in_docker` | `bool` | `false` | Build dependencies inside a Docker container |

### Main Outputs

| Output | Description |
|--------|-------------|
| `lambda_function_arn` / `lambda_function_arn_static` | ARN of the Lambda function (static form avoids cycles, e.g. with Step Functions) |
| `lambda_function_name` | Name of the Lambda function |
| `lambda_function_invoke_arn` / `lambda_function_qualified_invoke_arn` | Invoke ARN (unqualified/qualified) for API Gateway integration |
| `lambda_function_qualified_arn` | ARN including the published version |
| `lambda_function_version` | Latest published version |
| `lambda_function_url` / `lambda_function_url_id` | Function URL and its generated ID, if created |
| `lambda_role_arn` / `lambda_role_name` | IAM role created for the Lambda execution role |
| `lambda_cloudwatch_log_group_arn` / `lambda_cloudwatch_log_group_name` | CloudWatch log group for the function |
| `lambda_layer_arn` / `lambda_layer_layer_arn` | Layer ARN with/without version qualifier |
| `local_filename` | Path to the local deployment package, if stored locally |
| `s3_object` | Map of S3 object data for the deployment package, if stored on S3 |

### Usage Examples

#### Example 1: Simple Lambda Function

```hcl
module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "simple-lambda"
  description   = "Simple Lambda function example"
  handler       = "index.lambda_handler"
  runtime       = "python3.12"

  source_path = "${path.module}/src/lambda-function"

  tags = {
    Environment = "development"
  }
}
```

#### Example 2: Lambda with Python Dependencies and Custom Patterns

```hcl
module "lambda_with_dependencies" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "lambda-with-deps"
  description   = "Lambda function with Python dependencies"
  handler       = "app.handler"
  runtime       = "python3.12"
  timeout       = 30
  memory_size   = 512

  source_path = [
    {
      path              = "${path.module}/src"
      pip_requirements  = true
      patterns          = [
        "!\\.terragrunt-source-version",
        "!.*/.*\\.txt",
      ]
    }
  ]

  environment_variables = {
    LOG_LEVEL    = "INFO"
    API_ENDPOINT = "https://api.example.com"
  }

  attach_cloudwatch_logs_policy     = true
  cloudwatch_logs_retention_in_days = 7

  tags = {
    Application = "data-processor"
  }
}
```

#### Example 3: Lambda in VPC with Multiple IAM Policies

```hcl
module "lambda_vpc" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "vpc-lambda"
  description   = "Lambda function with VPC access"
  handler       = "index.handler"
  runtime       = "nodejs20.x"

  source_path = "${path.module}/src/vpc-lambda"

  # VPC Configuration
  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [module.security_group.security_group_id]
  attach_network_policy  = true

  # IAM Policies
  attach_policy_json = true
  policy_json = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = module.dynamodb_table.dynamodb_table_arn
      }
    ]
  })

  attach_policy_statements = true
  policy_statements = {
    s3_read = {
      effect    = "Allow"
      actions   = ["s3:GetObject"]
      resources = ["${module.s3_bucket.s3_bucket_arn}/*"]
    }
  }

  environment_variables = {
    TABLE_NAME  = module.dynamodb_table.dynamodb_table_id
    BUCKET_NAME = module.s3_bucket.s3_bucket_id
  }

  timeout     = 60
  memory_size = 1024

  tags = {
    Environment = "production"
  }
}
```

#### Example 4: Lambda Layer plus Function Using It (Stored on S3)

```hcl
# Create Lambda layer for dependencies
module "lambda_layer" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  create_layer = true
  layer_name   = "python-dependencies"
  description  = "Shared Python dependencies"

  compatible_runtimes = ["python3.12"]

  source_path = "${path.module}/layers/python-deps"

  store_on_s3 = true
  s3_bucket   = aws_s3_bucket.lambda_packages.id
}

# Lambda function using the layer
module "lambda_with_layer" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "lambda-with-layer"
  handler       = "app.handler"
  runtime       = "python3.12"

  source_path = "${path.module}/src/app"

  # Use the created layer
  layers = [module.lambda_layer.lambda_layer_arn]

  # Store function package on S3
  store_on_s3 = true
  s3_bucket   = aws_s3_bucket.lambda_packages.id

  environment_variables = {
    ENV = "production"
  }
}
```

#### Example 5: Lambda with DynamoDB Streams Event Source Mapping and DLQ

```hcl
module "lambda_stream_processor" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "stream-processor"
  handler       = "index.handler"
  runtime       = "python3.12"
  timeout       = 300
  memory_size   = 2048

  source_path = "${path.module}/src/stream-processor"

  # IAM policy for DynamoDB Streams
  attach_policy_statements = true
  policy_statements = {
    dynamodb_streams = {
      effect = "Allow"
      actions = [
        "dynamodb:GetRecords",
        "dynamodb:GetShardIterator",
        "dynamodb:DescribeStream",
        "dynamodb:ListStreams"
      ]
      resources = [aws_dynamodb_table.main.stream_arn]
    }
  }

  # Event source mapping
  event_source_mapping = {
    dynamodb = {
      event_source_arn                   = aws_dynamodb_table.main.stream_arn
      starting_position                  = "LATEST"
      batch_size                         = 100
      maximum_batching_window_in_seconds = 10
    }
  }

  # Dead letter queue for failures
  dead_letter_target_arn   = aws_sqs_queue.dlq.arn
  attach_dead_letter_policy = true

  tags = {
    UseCase = "stream-processing"
  }
}
```

#### Example 6: Lambda with Function URL and CORS

```hcl
module "lambda_api" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "api-lambda"
  handler       = "api.handler"
  runtime       = "nodejs20.x"
  timeout       = 10

  source_path = "${path.module}/src/api"

  # Create Function URL
  create_lambda_function_url = true
  authorization_type         = "NONE"

  cors = {
    allow_origins  = ["https://example.com"]
    allow_methods  = ["GET", "POST"]
    allow_headers  = ["content-type", "x-api-key"]
    expose_headers = ["x-request-id"]
    max_age        = 3600
  }

  invoke_mode = "RESPONSE_STREAM"

  environment_variables = {
    API_VERSION = "v1"
  }

  tags = {
    Type = "API"
  }
}

output "lambda_api_url" {
  description = "Function URL for API"
  value       = module.lambda_api.lambda_function_url
}
```

#### Example 7: Container Image Lambda (built via docker-build submodule)

```hcl
data "aws_ecr_authorization_token" "token" {}

provider "docker" {
  registry_auth {
    address  = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com"
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

module "docker_image" {
  source  = "terraform-aws-modules/lambda/aws//modules/docker-build"
  version = "~> 8.0"

  create_ecr_repo = true
  ecr_repo        = "my-lambda-repo"

  use_image_tag = true
  image_tag     = "1.0"

  source_path = "${path.module}/src/container-lambda"
  build_args = {
    FOO = "bar"
  }
}

module "lambda_container" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name  = "container-lambda"
  description    = "Lambda function from container image"
  create_package = false

  image_uri    = module.docker_image.image_uri
  package_type = "Image"

  timeout     = 60
  memory_size = 1024

  environment_variables = {
    ENVIRONMENT = "production"
  }

  tags = {
    Deployment = "container"
  }
}
```

#### Example 8: Lambda with Provisioned Concurrency and Alias

```hcl
module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "production-lambda"
  handler       = "index.handler"
  runtime       = "python3.12"

  source_path = "${path.module}/src/production"

  # Publish an immutable version on every change
  publish = true

  # Reserved concurrency to limit scaling
  reserved_concurrent_executions = 100

  memory_size = 2048
  timeout     = 30

  # Enable X-Ray tracing
  tracing_mode = "Active"

  environment_variables = {
    ENV       = "production"
    LOG_LEVEL = "INFO"
  }

  tags = {
    Environment       = "production"
    CriticalityLevel  = "high"
  }
}

module "lambda_alias" {
  source  = "terraform-aws-modules/lambda/aws//modules/alias"
  version = "~> 8.0"

  name             = "production"
  function_name    = module.lambda_function.lambda_function_name
  function_version = module.lambda_function.lambda_function_version
}

resource "aws_lambda_provisioned_concurrency_config" "production" {
  function_name                     = module.lambda_function.lambda_function_name
  qualifier                         = module.lambda_alias.lambda_alias_name
  provisioned_concurrent_executions = 5
}
```

#### Example 9: Scheduled Lambda (Cron Job)

```hcl
module "lambda_scheduled" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "scheduled-task"
  description   = "Runs daily cleanup tasks"
  handler       = "cleanup.handler"
  runtime       = "python3.12"

  source_path = "${path.module}/src/cleanup"

  timeout     = 900 # 15 minutes
  memory_size = 512

  allowed_triggers = {
    daily_cleanup = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.daily_cleanup.arn
    }
  }

  environment_variables = {
    RETENTION_DAYS = "30"
  }

  tags = {
    Schedule = "daily"
  }
}

resource "aws_cloudwatch_event_rule" "daily_cleanup" {
  name                = "daily-cleanup"
  description         = "Trigger cleanup Lambda daily"
  schedule_expression = "cron(0 2 * * ? *)" # 2 AM UTC daily
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.daily_cleanup.name
  target_id = "lambda"
  arn       = module.lambda_scheduled.lambda_function_arn
}
```

## Submodules

### 1. alias

- **Purpose**: Manages a Lambda function alias with weighted traffic routing, async event configuration, and event source mapping/permissions scoped to the alias
- **Source**: `terraform-aws-modules/lambda/aws//modules/alias`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/latest/submodules/alias
- **Key Features**: Static and auto-refreshing aliases, weighted traffic shifting for canary releases, "use existing alias" mode for external tooling (e.g., CodeDeploy), per-alias async event config and permissions
- **Use Cases**: Blue/green deployments, canary releases, CodeDeploy integration, environment-specific version pinning

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the Lambda alias |
| `function_name` | `string` | `""` | Name of the Lambda function |
| `function_version` | `string` | `""` | Version the alias points to (`$LATEST` or a number) |
| `refresh_alias` | `bool` | `true` | Auto-refresh alias to the latest function version |
| `use_existing_alias` | `bool` | `false` | Manage an existing alias instead of creating one |
| `routing_additional_version_weights` | `map(number)` | `{}` | Weighted traffic split across additional versions |
| `allowed_triggers` | `map(any)` | `{}` | Lambda permissions scoped to this alias |

#### Main Outputs

| Output | Description |
|--------|-------------|
| `lambda_alias_arn` | ARN of the Lambda alias |
| `lambda_alias_name` | Name of the Lambda alias |
| `lambda_alias_invoke_arn` | Invoke ARN for API Gateway integration |
| `lambda_alias_function_version` | Function version the alias currently uses |

#### Usage Example

```hcl
module "lambda_alias" {
  source  = "terraform-aws-modules/lambda/aws//modules/alias"
  version = "~> 8.0"

  name             = "production"
  function_name    = module.lambda_function.lambda_function_name
  function_version = module.lambda_function.lambda_function_version

  # Weighted traffic routing for canary
  routing_additional_version_weights = {
    "2" = 0.1 # 10% to version 2
  }

  allowed_triggers = {
    api_gateway = {
      principal  = "apigateway.amazonaws.com"
      source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*"
    }
  }
}
```

### 2. deploy

- **Purpose**: Creates AWS CodeDeploy application/deployment group resources (or reuses existing ones) and orchestrates a Lambda alias deployment, optionally waiting for completion
- **Source**: `terraform-aws-modules/lambda/aws//modules/deploy`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/latest/submodules/deploy
- **Key Features**: CodeDeploy app/deployment group creation, generates and optionally saves the AppSpec deploy script, runs `aws deploy create-deployment`, automatic rollback on CloudWatch alarms, before/after traffic-shift hook support, SNS deployment-event triggers
- **Use Cases**: Production deployments requiring gradual/canary rollouts, automated rollback on failure, traffic shifting with alarm-based monitoring

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `alias_name` | `string` | `""` | Lambda alias name to deploy through |
| `function_name` | `string` | `""` | Lambda function name |
| `current_version` / `target_version` | `string` | `""` | Current and target Lambda versions (not `$LATEST`) |
| `deployment_config_name` | `string` | `"CodeDeployDefault.LambdaAllAtOnce"` | CodeDeploy deployment configuration (e.g., canary/linear presets) |
| `create_app` / `use_existing_app` | `bool` | `false` / `false` | Create a new or reuse an existing CodeDeploy application |
| `create_deployment_group` / `use_existing_deployment_group` | `bool` | `false` / `false` | Create a new or reuse an existing deployment group |
| `run_deployment` / `wait_deployment_completion` | `bool` | `false` / `false` | Trigger the deployment and optionally block until it completes |
| `alarms` / `alarm_enabled` | `list(string)` / `bool` | `[]` / `false` | CloudWatch alarms for auto-rollback and whether alarm monitoring is active |
| `auto_rollback_events` | `list(string)` | `["DEPLOYMENT_STOP_ON_ALARM"]` | Events that trigger an automatic rollback |
| `before_allow_traffic_hook_arn` / `after_allow_traffic_hook_arn` | `string` | `""` | Lambda hook functions run before/after traffic shift |

#### Main Outputs

| Output | Description |
|--------|-------------|
| `codedeploy_app_name` | CodeDeploy application name |
| `codedeploy_deployment_group_name` / `codedeploy_deployment_group_id` | Deployment group name/ID |
| `deploy_script` | Path to the generated deployment script |
| `appspec_content` | AppSpec document as JSON |

#### Usage Example

```hcl
module "lambda_deploy" {
  source  = "terraform-aws-modules/lambda/aws//modules/deploy"
  version = "~> 8.0"

  alias_name     = module.lambda_alias.lambda_alias_name
  function_name  = module.lambda_function.lambda_function_name
  target_version = module.lambda_function.lambda_function_version

  create_app               = true
  app_name                 = "my-awesome-app"
  create_deployment_group  = true
  deployment_group_name    = "production"

  create_deployment          = true
  run_deployment              = true
  wait_deployment_completion  = true

  # Canary deployment: 10% traffic for 5 minutes
  deployment_config_name = "CodeDeployDefault.LambdaCanary10Percent5Minutes"

  # Auto-rollback on alarm
  alarm_enabled = true
  alarms = [
    aws_cloudwatch_metric_alarm.lambda_errors.alarm_name
  ]
}
```

### 3. docker-build

- **Purpose**: Builds a Docker image from a `Dockerfile`, optionally creates an ECR repository, and pushes the image so it can be referenced by `image_uri` in the main module
- **Source**: `terraform-aws-modules/lambda/aws//modules/docker-build`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/latest/submodules/docker-build
- **Key Features**: Optional ECR repository creation with lifecycle policy, buildx/multi-stage build support, build args and cache-from sources, SAM CLI metadata generation for local testing
- **Use Cases**: Container-image Lambda deployments, CI/CD pipelines that build and publish Lambda container images alongside infrastructure

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `source_path` | `string` | `null` | Path to the folder containing the Dockerfile/build context |
| `docker_file_path` | `string` | `"Dockerfile"` | Path to the Dockerfile within `source_path` |
| `create_ecr_repo` | `bool` | `false` | Whether to create a new ECR repository |
| `ecr_repo` | `string` | `null` | Name of the ECR repository to use or create |
| `ecr_address` | `string` | `null` | Cross-account ECR registry address (requires `create_ecr_repo = false`) |
| `image_tag` | `string` | `null` | Image tag; defaults to a timestamp if unset |
| `use_image_tag` | `bool` | `true` | Use a tag in the image URI vs. resolving to the latest digest |
| `build_args` | `map(string)` | `{}` | Docker build arguments |
| `platform` | `string` | `null` | Target architecture platform for the build |

#### Main Outputs

| Output | Description |
|--------|-------------|
| `image_uri` | ECR image URI to pass to the main module's `image_uri` variable |
| `image_id` | ID of the built Docker image |

#### Usage Example

```hcl
module "docker_image" {
  source  = "terraform-aws-modules/lambda/aws//modules/docker-build"
  version = "~> 8.0"

  create_ecr_repo = true
  ecr_repo        = "my-cool-ecr-repo"

  use_image_tag = true
  image_tag     = "1.0"

  source_path = "context"
  build_args = {
    FOO = "bar"
  }
}

module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name  = "my-lambda1"
  create_package = false

  image_uri    = module.docker_image.image_uri
  package_type = "Image"
}
```

## Best Practices

### Function Design and Development

1. **Separate Handler from Business Logic**: Keep the Lambda handler thin and separate business logic for easier testing and reusability.
2. **Initialize Outside Handler**: Initialize SDK clients, database connections, and global variables outside the handler function to reuse them across invocations.
3. **Write Idempotent Code**: Design functions to produce the same result when invoked multiple times with the same input to handle retries safely.
4. **Use Environment Variables**: Configure application settings using `environment_variables` rather than hard-coding values.
5. **Keep Deployment Packages Small**: Minimize package size by excluding unnecessary files and dependencies (`patterns`) to reduce cold start times.
6. **Use Layers for Shared Code**: Extract common dependencies and utilities into Lambda layers (`create_layer = true`) to reduce duplication and package size.
7. **Set `hash_extra` for Reused Source Paths**: When multiple module calls share the same `source_path`, set distinct `hash_extra` values to avoid corrupted concurrent zip writes.

### Performance Optimization

1. **Right-Size Memory Configuration**: Test different `memory_size` settings; higher memory also provides more CPU, which may reduce execution time and cost.
2. **Enable SnapStart**: Set `snap_start = true` to reduce cold start latency for supported runtimes (e.g., Java).
3. **Use Provisioned Concurrency**: Configure `provisioned_concurrent_executions` (directly, or via the `alias`/`aws_lambda_provisioned_concurrency_config`) for functions requiring consistent sub-second response times.
4. **Minimize Cold Starts**: Keep packages small, limit the number of layers, and avoid unnecessary initialization code.
5. **Choose ARM64 Where Possible**: Set `architectures = ["arm64"]` for better price-performance on supported workloads.
6. **Build in Docker for Native Dependencies**: Use `build_in_docker = true` with a runtime-matched `docker_image` when packages require compiled/native dependencies.

### Security and Compliance

1. **Apply Least Privilege IAM Policies**: Grant only the minimum permissions required for function execution via `policy_statements`; avoid wildcards.
2. **Use IAM Roles, Not Access Keys**: Lambda automatically provides temporary credentials through the execution role; never hard-code access keys.
3. **Enable Code Signing**: Set `code_signing_config_arn` to ensure only trusted code runs in your Lambda functions.
4. **Encrypt Sensitive Data**: Use `kms_key_arn` to encrypt environment variables, and `cloudwatch_logs_kms_key_id`/`s3_kms_key_id` to encrypt logs and stored artifacts.
5. **Use VPC with Private Subnets**: Place Lambda functions accessing private resources in VPC private subnets, not public subnets.
6. **Consider Tenant Isolation Mode**: Enable `tenant_isolation_mode` for workloads processing data from multiple tenants that require stronger execution-environment isolation.
7. **Validate Input Data**: Always validate and sanitize input data to prevent injection attacks and unexpected behavior.
8. **Secure Function URLs**: When using `create_lambda_function_url`, prefer `authorization_type = "AWS_IAM"` over `"NONE"` unless the endpoint is intentionally public.

### Deployment and CI/CD

1. **Pin Module Versions**: Use specific module versions in production (e.g., `version = "~> 8.0"`) to prevent unexpected changes.
2. **Publish Versions**: Set `publish = true` to create immutable versions for rollback capability.
3. **Use the `alias` Submodule for Environments**: Point distinct aliases (e.g., `production`, `staging`) at specific function versions for controlled promotion.
4. **Implement Canary Deployments**: Use the `deploy` submodule with a `CodeDeployDefault.LambdaCanary*`/`LambdaLinear*` config and `alarm_enabled = true` for automated rollback.
5. **Separate Code from Infrastructure When Needed**: Set `ignore_source_code_hash = true` with `create_package = false` when code deployment is managed by a separate CI/CD pipeline (e.g., `aws lambda update-function-code`).
6. **Store Packages on S3**: Use `store_on_s3 = true` for deployment packages larger than 50MB or for centralized package management.
7. **Tag Resources Consistently**: Apply tags for environment, application, cost center, and owner to all Lambda resources.

### Monitoring and Observability

1. **Enable CloudWatch Logs**: Ensure `attach_cloudwatch_logs_policy = true` with an appropriate `cloudwatch_logs_retention_in_days`.
2. **Use Structured Logging**: Set `logging_log_format = "JSON"` for easier parsing and analysis in CloudWatch Logs Insights.
3. **Configure Advanced Log Controls**: Tune `logging_application_log_level` and `logging_system_log_level` independently for verbosity control.
4. **Set Up CloudWatch Alarms**: Create alarms for errors, throttles, duration, and concurrent executions, and wire them into the `deploy` submodule for auto-rollback.
5. **Use AWS X-Ray**: Set `tracing_mode = "Active"` to visualize service maps and identify bottlenecks in distributed applications.
6. **Configure Dead Letter Queues**: Set `dead_letter_target_arn` and `attach_dead_letter_policy = true` to capture failed async invocations for analysis and reprocessing.

### Cost Optimization

1. **Optimize Memory and Timeout**: Right-size `memory_size` and `timeout` to avoid over-provisioning.
2. **Use ARM64 Architecture**: Switch to `arm64` for better price-performance on compatible workloads.
3. **Use Reserved Concurrency Wisely**: Set `reserved_concurrent_executions` to prevent unexpected scaling and runaway costs.
4. **Review Provisioned Concurrency**: Only use provisioned concurrency for functions with strict latency requirements; it incurs continuous charges.
5. **Set Appropriate Log Retention**: Configure `cloudwatch_logs_retention_in_days` to balance observability needs with storage costs.
6. **Consider Managed Instances**: For steady, predictable high-throughput workloads, evaluate `managed_instances_capacity_provider_arn` against standard on-demand Lambda pricing.

### VPC and Networking

1. **Place in Private Subnets**: Deploy VPC-enabled Lambda functions (`vpc_subnet_ids`) in private subnets, never public subnets.
2. **Use VPC Endpoints**: Configure VPC endpoints for AWS services (S3, DynamoDB, etc.) to avoid NAT Gateway costs and reduce latency.
3. **Attach the Network Policy**: Set `attach_network_policy = true` so the execution role can create/manage ENIs.
4. **Plan Security Group Cleanup on Destroy**: Use `replace_security_groups_on_destroy` and `replacement_security_group_ids` to avoid orphaned ENIs when tearing down VPC-attached functions.

### Event-Driven Architecture

1. **Configure DLQs for Reliability**: Always configure dead letter queues for async invocations and stream processing.
2. **Tune Batch Settings**: Set `batch_size` and `maximum_batching_window_in_seconds` in `event_source_mapping` for optimal throughput.
3. **Handle Partial Batch Failures**: Implement proper error handling (`ReportBatchItemFailures`) for partial batch failures in stream/queue processing.
4. **Control Trigger Scope**: Use `create_current_version_allowed_triggers` and `create_unqualified_alias_allowed_triggers` to manage which versions/aliases receive invoke permissions.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-lambda
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-lambda/tree/master/examples
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-lambda/blob/master/CHANGELOG.md
- **AWS Lambda Documentation**: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
- **Lambda Best Practices**: https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html
- **Lambda Runtimes**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
- **Lambda Concurrency**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html
- **Lambda Pricing**: https://aws.amazon.com/lambda/pricing/
- **Lambda Security Best Practices**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-security.html
- **Lambda in VPC**: https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html
- **Serverless.tf Framework**: https://serverless.tf/

## Notes for AI Agents

When using this module in automated workflows:

1. **Choose Appropriate Runtime**: Select the most recent runtime version supported by AWS; older runtimes may be deprecated.
2. **Build Dependencies Correctly**: Use `pip_requirements = true` (or `poetry_install = true`) for Python, `npm_requirements = true` for Node.js, or `commands` for custom builds.
3. **Right-Size Resources**: Start with 512MB memory and adjust based on CloudWatch metrics; higher memory also provides more CPU.
4. **Use Layers for Large Dependencies**: Extract large dependencies (>10MB) into Lambda layers to reduce deployment package size.
5. **Enable CloudWatch Logs**: Always set `attach_cloudwatch_logs_policy = true` and configure appropriate retention (`cloudwatch_logs_retention_in_days`).
6. **Apply Least Privilege IAM**: Use `policy_statements`/`policy_json`; avoid `attach_policy = true` with overly permissive managed policies.
7. **Configure VPC Carefully**: Only use VPC when accessing private resources; VPC adds latency to cold starts unless traffic stays within AWS's Hyperplane ENIs.
8. **Set Appropriate Timeouts**: Configure `timeout` based on expected execution duration; the default of 3 seconds is often too short.
9. **Publish Versions for Production**: Set `publish = true` for production functions to enable versioning, aliasing, and rollback.
10. **Store Large Packages on S3**: Use `store_on_s3 = true` for packages larger than 50MB or for centralized management.
11. **Use the Correct Function URL Variables**: Function URL configuration is top-level (`create_lambda_function_url`, `authorization_type`, `cors`, `invoke_mode`) — there is no `function_url_config` object in current versions.
12. **Use `image_uri` for Container Deployments**: Set `create_package = false` and `package_type = "Image"`; build the image with the `docker-build` submodule if Terraform should own the build.
13. **Tag Consistently**: Include `Environment`, `Application`, `Owner`, and cost-center tags on all Lambda resources via the `tags` variable.
14. **Implement DLQs**: Configure `dead_letter_target_arn` and `attach_dead_letter_policy = true` for async invocations to capture and analyze failures.
15. **Use Provisioned Concurrency Sparingly**: Only enable for latency-sensitive functions; it incurs continuous costs even when idle.
16. **Consider ARM64**: Use `architectures = ["arm64"]` for better price-performance when the runtime and dependencies support it.
17. **Pin the Module Version**: Always set an explicit `version` constraint (e.g., `~> 8.0`) — this module evolves frequently and has had breaking changes across major versions (e.g., v8.0.0 raised minimum provider/Terraform requirements).
