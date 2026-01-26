# Terraform AWS Lambda Module

## Module Information

- **Module Name**: terraform-aws-lambda
- **Source**: `terraform-aws-modules/lambda/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-lambda
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/latest
- **Latest Version**: 8.1.0
- **Purpose**: Terraform module that creates and manages AWS Lambda functions, layers, and aliases with comprehensive support for building, packaging, and deploying serverless applications
- **Service**: AWS Lambda (Serverless Compute)
- **Category**: Compute, Serverless, Application Integration
- **Keywords**: lambda, serverless, faas, lambda-function, lambda-layer, lambda-alias, lambda-edge, container-image, vpc-lambda, event-source-mapping, provisioned-concurrency, function-url, dead-letter-queue, codedeploy, canary-deployment, docker-build
- **Use For**: API backend implementation, event-driven data processing, real-time file processing, scheduled task automation, microservices architecture, stream processing from Kinesis or DynamoDB, IoT data processing, chatbot and voice assistant backends, image and video processing, ETL workflows, serverless web applications, webhook handlers

## Description

This Terraform module provides comprehensive management of AWS Lambda resources including functions, layers, and aliases with advanced capabilities for building, packaging, and deploying serverless applications. The module is part of the serverless.tf framework and handles the complete lifecycle of Lambda deployments from dependency installation to production deployment. It supports multiple deployment strategies including .zip file archives, container images, and Lambda@Edge, with flexible options for storing packages locally or in S3 buckets.

The module addresses common Lambda deployment challenges by automating dependency management for multiple runtimes (Python, Node.js, Java, Go, .NET, Ruby), building deployment packages with customizable build commands, and managing complex infrastructure configurations. It supports both local and Docker-based builds, enabling consistent deployment packages across different development environments. The module integrates seamlessly with AWS services through configurable event source mappings, VPC networking, EFS file system mounts, and comprehensive IAM policy management with six different methods for attaching permissions.

Key architectural capabilities include controlled deployment strategies (rolling updates, canary deployments, rollbacks), version management, provisioned concurrency for consistent performance, function URLs for direct HTTP access, and asynchronous event configurations with dead letter queues. The module handles Lambda@Edge deployments for CloudFront, supports code signing for enhanced security, and provides flexible configuration for environment variables, runtime settings, and resource limits. With support for conditional resource creation and extensive configuration options, this module enables teams to implement sophisticated serverless architectures while maintaining infrastructure as code best practices.

## Key Features

- **Automated Dependency Management**: Build and install dependencies for Python (pip), Node.js (npm), and other runtimes
- **Flexible Package Building**: Create deployment packages from single directories, multiple sources, or custom build commands
- **Docker Build Support**: Use Docker containers for consistent dependency builds across environments
- **S3 Package Storage**: Store deployment packages in S3 buckets for large functions or centralized package management
- **Container Image Deployment**: Deploy Lambda functions using container images from ECR
- **Lambda Layers**: Create and manage Lambda layers for shared code and dependencies
- **Lambda Aliases**: Configure function aliases for blue/green deployments and traffic shifting
- **Lambda@Edge Support**: Deploy Lambda functions at CloudFront edge locations
- **VPC Integration**: Configure Lambda functions to access resources in VPCs with subnet and security group configuration
- **EFS File System Access**: Mount Elastic File System for persistent storage across invocations
- **Event Source Mapping**: Configure event sources from Kinesis, DynamoDB Streams, SQS, and other services
- **Asynchronous Configuration**: Set up async invocation with retry behavior and dead letter queues
- **Function URLs**: Create direct HTTPS endpoints for Lambda functions without API Gateway
- **IAM Policy Management**: Six flexible methods to attach IAM policies (JSON, ARN, statement, assume role, CloudWatch logs, VPC)
- **Provisioned Concurrency**: Pre-initialize execution environments for consistent low-latency performance
- **Reserved Concurrency**: Set maximum concurrent executions to control scaling and costs
- **Code Signing**: Implement code signing for enhanced security and integrity verification
- **CloudWatch Logs Integration**: Automatic log group creation with configurable retention periods
- **X-Ray Tracing**: Enable AWS X-Ray for distributed tracing and performance analysis
- **Environment Variables**: Configure runtime environment variables with optional encryption
- **Multiple Runtimes**: Support for Python, Node.js, Java, Go, .NET, Ruby, and custom runtimes
- **Architecture Support**: Deploy for x86_64 or ARM64 (Graviton2) architectures
- **Version Management**: Automatic function version publishing for rollback and alias management
- **Conditional Creation**: Create or skip Lambda resources based on variables
- **Custom Build Commands**: Execute arbitrary build commands during package creation
- **Source Path Patterns**: Include/exclude files from deployment packages with glob patterns
- **CloudFormation Deployment**: Advanced deployment controls including rolling updates and canary deployments

## Main Use Cases

1. **REST API Backends**: Implement serverless API endpoints with Function URLs or API Gateway integration
2. **Event-Driven Processing**: Process events from S3, DynamoDB, Kinesis, SQS, SNS, or EventBridge
3. **Scheduled Tasks**: Run cron jobs and scheduled automation using EventBridge rules
4. **Real-Time Stream Processing**: Process streaming data from Kinesis or DynamoDB Streams
5. **File Processing**: Automatically process uploaded files from S3 with image resizing, transcoding, or ETL
6. **Microservices Architecture**: Build distributed applications with Lambda as microservice components
7. **Webhook Handlers**: Receive and process webhooks from third-party services
8. **Data Transformation**: Execute ETL jobs and data transformation pipelines
9. **IoT Data Processing**: Process telemetry and sensor data from IoT devices
10. **ChatOps and Automation**: Implement chatbots, Slack bots, and automation workflows

## Main Module: Lambda Function

### Description

The main Lambda module provides complete functionality for creating and managing AWS Lambda functions with comprehensive build, package, and deployment capabilities. This module handles everything from dependency installation to production deployment, supporting multiple package sources (local builds, S3 storage, existing packages, container images) and advanced configurations including VPC networking, async invocation, event source mappings, and IAM policy management.

### Key Features

- Complete Lambda function lifecycle management from build to deployment
- Automated dependency installation and package building
- Support for all AWS Lambda runtimes and architectures
- Flexible IAM policy attachment with multiple methods
- VPC, EFS, and networking configuration
- Event source mapping and trigger management
- Comprehensive monitoring and logging integration

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `function_name` | `string` | `""` | Unique name for Lambda function |
| `handler` | `string` | `""` | Function entry point (e.g., index.handler) |
| `runtime` | `string` | `""` | Lambda runtime (python3.12, nodejs20.x, etc.) |
| `source_path` | `any` | `null` | Path to function source code or build configuration |
| `create_function` | `bool` | `true` | Whether to create Lambda function |
| `timeout` | `number` | `3` | Function timeout in seconds (max 900) |
| `memory_size` | `number` | `128` | Memory allocated to function in MB |
| `environment_variables` | `map(string)` | `{}` | Environment variables for function |
| `layers` | `list(string)` | `null` | List of Lambda layer ARNs |
| `vpc_subnet_ids` | `list(string)` | `null` | VPC subnet IDs for function |
| `vpc_security_group_ids` | `list(string)` | `null` | Security group IDs for function in VPC |
| `attach_policy_json` | `bool` | `false` | Whether to attach IAM policy JSON |
| `policy_json` | `string` | `null` | IAM policy JSON document |
| `attach_cloudwatch_logs_policy` | `bool` | `true` | Whether to attach CloudWatch Logs policy |
| `cloudwatch_logs_retention_in_days` | `number` | `null` | CloudWatch log group retention period |
| `create_package` | `bool` | `true` | Whether to create deployment package |
| `store_on_s3` | `bool` | `false` | Store deployment package on S3 |
| `s3_bucket` | `string` | `null` | S3 bucket for deployment package |
| `publish` | `bool` | `false` | Whether to publish function version |
| `reserved_concurrent_executions` | `number` | `-1` | Reserved concurrent executions (-1 = unreserved) |
| `provisioned_concurrent_executions` | `number` | `-1` | Provisioned concurrent executions |
| `create_function_url` | `bool` | `false` | Whether to create Lambda function URL |
| `tracing_mode` | `string` | `null` | X-Ray tracing mode (Active or PassThrough) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `lambda_function_arn` | ARN of the Lambda function |
| `lambda_function_name` | Name of the Lambda function |
| `lambda_function_invoke_arn` | Invoke ARN of the Lambda function |
| `lambda_function_qualified_arn` | ARN with version or alias |
| `lambda_function_version` | Latest published version |
| `lambda_function_url` | Function URL if created |
| `lambda_function_url_id` | Function URL ID if created |
| `lambda_role_arn` | ARN of IAM role created for Lambda |
| `lambda_role_name` | Name of IAM role created for Lambda |
| `lambda_cloudwatch_log_group_arn` | ARN of CloudWatch log group |
| `local_filename` | Path to local deployment package |
| `s3_object_key` | S3 object key if stored on S3 |

### Usage Examples

#### Example 1: Simple Lambda Function

```hcl
module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

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

#### Example 2: Lambda with Dependencies and Custom Build

```hcl
module "lambda_with_dependencies" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "lambda-with-deps"
  description   = "Lambda function with Python dependencies"
  handler       = "app.handler"
  runtime       = "python3.12"
  timeout       = 30
  memory_size   = 512

  source_path = [
    {
      path = "${path.module}/src"
      pip_requirements = true
      patterns = [
        "!\\.terragrunt-source-version",
        "!.*/.*\\.txt",
      ]
    }
  ]

  environment_variables = {
    LOG_LEVEL = "INFO"
    API_ENDPOINT = "https://api.example.com"
  }

  attach_cloudwatch_logs_policy = true
  cloudwatch_logs_retention_in_days = 7

  tags = {
    Application = "data-processor"
  }
}
```

#### Example 3: Lambda in VPC with Multiple IAM Policies

```hcl
module "lambda_vpc" {
  source = "terraform-aws-modules/lambda/aws"

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
      effect = "Allow"
      actions = ["s3:GetObject"]
      resources = ["${module.s3_bucket.s3_bucket_arn}/*"]
    }
  }

  environment_variables = {
    TABLE_NAME = module.dynamodb_table.dynamodb_table_id
    BUCKET_NAME = module.s3_bucket.s3_bucket_id
  }

  timeout     = 60
  memory_size = 1024

  tags = {
    Environment = "production"
  }
}
```

#### Example 4: Lambda with S3 Package Storage and Layers

```hcl
# Create Lambda layer for dependencies
module "lambda_layer" {
  source = "terraform-aws-modules/lambda/aws"

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
  source = "terraform-aws-modules/lambda/aws"

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

#### Example 5: Lambda with Event Source Mapping

```hcl
module "lambda_stream_processor" {
  source = "terraform-aws-modules/lambda/aws"

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
      event_source_arn  = aws_dynamodb_table.main.stream_arn
      starting_position = "LATEST"
      batch_size        = 100
      maximum_batching_window_in_seconds = 10
    }
  }

  # Dead letter queue for failures
  dead_letter_target_arn = aws_sqs_queue.dlq.arn
  attach_dead_letter_policy = true

  tags = {
    UseCase = "stream-processing"
  }
}
```

#### Example 6: Lambda with Function URL and CORS

```hcl
module "lambda_api" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "api-lambda"
  handler       = "api.handler"
  runtime       = "nodejs20.x"
  timeout       = 10

  source_path = "${path.module}/src/api"

  # Create Function URL
  create_function_url = true

  function_url_config = {
    authorization_type = "NONE"

    cors = {
      allow_origins     = ["https://example.com"]
      allow_methods     = ["GET", "POST"]
      allow_headers     = ["content-type", "x-api-key"]
      expose_headers    = ["x-request-id"]
      max_age          = 3600
    }
  }

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

#### Example 7: Container Image Lambda

```hcl
module "lambda_container" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "container-lambda"
  description   = "Lambda function from container image"

  create_package = false

  image_uri    = "${aws_ecr_repository.lambda.repository_url}:latest"
  package_type = "Image"

  timeout     = 60
  memory_size = 1024

  environment_variables = {
    ENVIRONMENT = "production"
  }

  # IAM policies
  attach_policy_json = true
  policy_json = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:*"]
        Resource = "*"
      }
    ]
  })

  tags = {
    Deployment = "container"
  }
}
```

#### Example 8: Lambda with Provisioned Concurrency and Alias

```hcl
module "lambda_production" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "production-lambda"
  handler       = "index.handler"
  runtime       = "python3.12"

  source_path = "${path.module}/src/production"

  # Publish versions
  publish = true

  # Create alias
  create_lambda_alias = true
  lambda_alias = {
    name = "production"
    description = "Production alias"

    # Provisioned concurrency for consistent performance
    provisioned_concurrent_executions = 5
  }

  # Reserved concurrency to limit scaling
  reserved_concurrent_executions = 100

  memory_size = 2048
  timeout     = 30

  # Enable X-Ray tracing
  tracing_mode = "Active"

  environment_variables = {
    ENV = "production"
    LOG_LEVEL = "INFO"
  }

  tags = {
    Environment = "production"
    CriticalityLevel = "high"
  }
}
```

#### Example 9: Scheduled Lambda (Cron Job)

```hcl
module "lambda_scheduled" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "scheduled-task"
  description   = "Runs daily cleanup tasks"
  handler       = "cleanup.handler"
  runtime       = "python3.12"

  source_path = "${path.module}/src/cleanup"

  timeout     = 900  # 15 minutes
  memory_size = 512

  # EventBridge rule for scheduling
  create_current_version_allowed_triggers = false
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
  schedule_expression = "cron(0 2 * * ? *)"  # 2 AM UTC daily
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.daily_cleanup.name
  target_id = "lambda"
  arn       = module.lambda_scheduled.lambda_function_arn
}
```

## Submodules

### 1. alias

- **Purpose**: Manages Lambda function aliases with weighted traffic routing for blue/green deployments
- **Source**: `terraform-aws-modules/lambda/aws//modules/alias`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/latest/submodules/alias
- **Key Features**: Static and dynamic alias management, weighted traffic shifting, async event configuration, version-specific permissions, auto-refresh for external deployments
- **Use Cases**: Blue/green deployments, canary releases, CodeDeploy integration, version pinning

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | - | Name of the Lambda alias |
| `function_name` | `string` | - | Name of the Lambda function |
| `function_version` | `string` | `""` | Version to point alias to |
| `refresh_alias` | `bool` | `true` | Auto-refresh alias to latest version |

#### Main Outputs

| Output | Description |
|--------|-------------|
| `lambda_alias_arn` | ARN of the Lambda alias |
| `lambda_alias_name` | Name of the Lambda alias |
| `lambda_alias_invoke_arn` | Invoke ARN for API Gateway |

#### Usage Example

```hcl
module "lambda_alias" {
  source = "terraform-aws-modules/lambda/aws//modules/alias"

  name             = "production"
  function_name    = module.lambda_function.lambda_function_name
  function_version = module.lambda_function.lambda_function_version

  # Weighted traffic routing for canary
  routing_additional_version_weights = {
    "2" = 0.1  # 10% to version 2
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

- **Purpose**: AWS CodeDeploy integration for orchestrated Lambda deployments with rollback capabilities
- **Source**: `terraform-aws-modules/lambda/aws//modules/deploy`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/latest/submodules/deploy
- **Key Features**: CodeDeploy application and deployment group creation, canary and rolling deployments, automatic rollback on CloudWatch alarms, lifecycle hook integration
- **Use Cases**: Production deployments requiring gradual rollouts, automated rollback on failures, traffic shifting with monitoring

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `alias_name` | `string` | - | Lambda alias name for deployment |
| `function_name` | `string` | - | Lambda function name |
| `target_version` | `string` | - | Target Lambda version |
| `deployment_config_name` | `string` | `"CodeDeployDefault.LambdaAllAtOnce"` | Deployment configuration |
| `create_app` | `bool` | `true` | Create CodeDeploy application |
| `alarm_names` | `list(string)` | `[]` | CloudWatch alarms for auto-rollback |

#### Main Outputs

| Output | Description |
|--------|-------------|
| `codedeploy_app_name` | CodeDeploy application name |
| `codedeploy_deployment_group_name` | Deployment group name |
| `deploy_script` | Deployment execution script |

#### Usage Example

```hcl
module "lambda_deploy" {
  source = "terraform-aws-modules/lambda/aws//modules/deploy"

  alias_name     = module.lambda_alias.lambda_alias_name
  function_name  = module.lambda_function.lambda_function_name
  target_version = module.lambda_function.lambda_function_version

  # Canary deployment: 10% traffic for 5 minutes
  deployment_config_name = "CodeDeployDefault.LambdaCanary10Percent5Minutes"

  # Auto-rollback on alarm
  alarm_names = [
    aws_cloudwatch_metric_alarm.lambda_errors.alarm_name
  ]

  triggers = {
    redeployment = sha256(jsonencode([
      module.lambda_function.lambda_function_version
    ]))
  }
}
```

## Best Practices

### Function Design and Development

1. **Separate Handler from Business Logic**: Keep the Lambda handler thin and separate business logic for easier testing and reusability.
2. **Initialize Outside Handler**: Initialize SDK clients, database connections, and global variables outside the handler function to reuse them across invocations.
3. **Write Idempotent Code**: Design functions to produce the same result when invoked multiple times with the same input to handle retries safely.
4. **Use Environment Variables**: Configure application settings using environment variables rather than hard-coding values.
5. **Implement Graceful Error Handling**: Catch and handle exceptions appropriately; use structured logging for debugging.
6. **Keep Deployment Packages Small**: Minimize package size by excluding unnecessary files and dependencies to reduce cold start times.
7. **Use Layers for Shared Code**: Extract common dependencies and utilities into Lambda layers to reduce duplication and deployment package size.
8. **Implement Timeout and Retry Logic**: Design functions to handle timeouts gracefully and implement retry logic for external service calls.

### Performance Optimization

1. **Right-Size Memory Configuration**: Test different memory settings; higher memory also provides more CPU, which may reduce execution time and cost.
2. **Enable SnapStart for Java**: Use Lambda SnapStart to reduce cold start latency for Java functions.
3. **Use Provisioned Concurrency**: Configure provisioned concurrency for functions requiring consistent sub-second response times.
4. **Cache Static Assets in /tmp**: Utilize the /tmp directory (up to 10GB with configuration) to cache files across invocations.
5. **Minimize Cold Starts**: Keep packages small, limit the number of layers, and avoid unnecessary initialization code.
6. **Choose Appropriate Architecture**: Consider ARM64 (Graviton2) for better price-performance ratio on supported workloads.
7. **Optimize Dependencies**: Import only required libraries and modules; avoid importing entire SDKs when only specific clients are needed.
8. **Implement Connection Pooling**: Reuse database connections and HTTP clients across invocations to reduce connection overhead.

### Security and Compliance

1. **Apply Least Privilege IAM Policies**: Grant only the minimum permissions required for function execution; avoid wildcards in policies.
2. **Use IAM Roles, Not Access Keys**: Lambda automatically provides temporary credentials through execution roles; never hard-code access keys.
3. **Enable Code Signing**: Implement code signing to ensure only trusted code runs in your Lambda functions.
4. **Encrypt Environment Variables**: Use AWS KMS to encrypt sensitive configuration data in environment variables.
5. **Use VPC with Private Subnets**: Place Lambda functions accessing private resources in VPC private subnets, not public subnets.
6. **Implement Security Scanning**: Use AWS Security Hub and Amazon GuardDuty to monitor Lambda security posture.
7. **Enable X-Ray Tracing**: Use AWS X-Ray for security analysis and performance troubleshooting in production.
8. **Rotate Secrets Regularly**: Use AWS Secrets Manager or Parameter Store for sensitive credentials and implement rotation.
9. **Validate Input Data**: Always validate and sanitize input data to prevent injection attacks and unexpected behavior.
10. **Use Function URLs with Authorization**: When using Function URLs, implement IAM authorization or API Gateway for authentication.

### Deployment and CI/CD

1. **Version Control Everything**: Store all Lambda code, dependencies, and infrastructure configuration in version control.
2. **Use Terraform Workspaces or Environments**: Separate development, staging, and production environments with distinct state files.
3. **Implement Blue/Green Deployments**: Use Lambda aliases and traffic shifting for zero-downtime deployments.
4. **Pin Module Versions**: Use specific module versions in production (e.g., `version = "~> 7.0"`) to prevent unexpected changes.
5. **Test Locally First**: Use tools like AWS SAM CLI or LocalStack to test Lambda functions locally before deployment.
6. **Publish Versions**: Set `publish = true` to create immutable versions for rollback capability.
7. **Use Build Automation**: Automate dependency installation and package building in CI/CD pipelines.
8. **Implement Canary Deployments**: Use weighted alias routing to gradually shift traffic to new versions.
9. **Tag Resources Consistently**: Apply tags for environment, application, cost center, and owner to all Lambda resources.
10. **Store Packages on S3**: Use S3 storage for deployment packages larger than 50MB or for centralized package management.

### Monitoring and Observability

1. **Enable CloudWatch Logs**: Ensure CloudWatch Logs integration is enabled with appropriate retention periods.
2. **Use Structured Logging**: Implement structured logging (JSON format) for easier parsing and analysis in CloudWatch Insights.
3. **Set Up CloudWatch Alarms**: Create alarms for errors, throttles, duration, and concurrent executions.
4. **Monitor Cold Starts**: Track initialization duration to identify performance issues.
5. **Implement Custom Metrics**: Use CloudWatch embedded metric format to publish custom business and performance metrics.
6. **Use AWS X-Ray**: Enable X-Ray tracing to visualize service maps and identify bottlenecks in distributed applications.
7. **Configure Dead Letter Queues**: Set up DLQs to capture failed async invocations for analysis and reprocessing.
8. **Track Cost Metrics**: Use AWS Cost Anomaly Detection and tag-based cost allocation to monitor Lambda spending.
9. **Implement Health Checks**: Create synthetic monitors to continuously test function availability and performance.
10. **Review CloudWatch Insights**: Regularly analyze logs using CloudWatch Insights to identify patterns and issues.

### Cost Optimization

1. **Optimize Memory and Timeout**: Right-size memory allocation and set appropriate timeouts to avoid over-provisioning.
2. **Use ARM64 Architecture**: Switch to ARM64 (Graviton2) for up to 34% better price-performance on compatible workloads.
3. **Minimize Execution Duration**: Optimize code to reduce execution time; Lambda charges per millisecond.
4. **Delete Unused Functions**: Regularly audit and remove unused Lambda functions and versions.
5. **Set Appropriate Log Retention**: Configure CloudWatch log retention to balance observability needs with storage costs.
6. **Use Reserved Concurrency Wisely**: Set reserved concurrency to prevent unexpected scaling and runaway costs.
7. **Batch Process When Possible**: Process multiple records per invocation when using stream processing to reduce invocation count.
8. **Review Provisioned Concurrency**: Only use provisioned concurrency for functions with strict latency requirements; it incurs continuous charges.
9. **Optimize Package Size**: Smaller packages reduce storage costs and improve cold start performance.
10. **Monitor Free Tier Usage**: AWS provides 1M free requests and 400,000 GB-seconds per month; optimize to stay within free tier when possible.

### Operational Excellence

1. **Document Function Purpose**: Maintain clear descriptions for all functions, including purpose, triggers, and dependencies.
2. **Implement Retry Logic**: Configure retry attempts and backoff strategies for async invocations and stream processing.
3. **Use EventBridge for Scheduling**: Prefer EventBridge rules over CloudWatch Events for scheduled Lambda invocations.
4. **Configure Concurrency Limits**: Set reserved concurrency to protect downstream systems from overload.
5. **Test at Scale**: Load test Lambda functions to understand scaling behavior and downstream system limits.
6. **Plan for Quotas**: Be aware of AWS Lambda service quotas (concurrent executions, deployment package size, etc.).
7. **Implement Circuit Breakers**: Add circuit breaker patterns when calling external services to prevent cascading failures.
8. **Use SQS for Buffering**: Place SQS queues between event sources and Lambda for better control over processing rates.
9. **Monitor Upstream Services**: Track event source behavior to anticipate Lambda scaling requirements.
10. **Maintain Runbooks**: Document common operational procedures, troubleshooting steps, and rollback procedures.

### VPC and Networking

1. **Use Hyperplane ENIs**: Modern Lambda VPC integration uses Hyperplane ENIs for fast scaling without ENI limits.
2. **Place in Private Subnets**: Deploy VPC-enabled Lambda functions in private subnets, never public subnets.
3. **Use VPC Endpoints**: Configure VPC endpoints for AWS services (S3, DynamoDB, etc.) to avoid NAT Gateway costs.
4. **Configure NAT Gateway**: Ensure NAT Gateway or NAT Instance is available for Lambda to access internet resources.
5. **Security Group Best Practices**: Use security groups to control outbound access; Lambda doesn't accept inbound connections.
6. **Consider Multi-AZ**: Deploy Lambda with subnets in multiple availability zones for resilience.
7. **Monitor VPC Flow Logs**: Enable VPC Flow Logs to monitor Lambda network traffic patterns.
8. **Plan IP Addresses**: Ensure VPC subnets have sufficient IP addresses for Lambda scaling.

### Event-Driven Architecture

1. **Use Async Invocation for Non-Critical Paths**: Invoke Lambda asynchronously when immediate response isn't required.
2. **Configure DLQs for Reliability**: Always configure dead letter queues for async invocations and stream processing.
3. **Implement Idempotency Tokens**: Use idempotency tokens to prevent duplicate processing of events.
4. **Batch Processing Configuration**: Tune batch size and batching window for optimal throughput in stream processing.
5. **Handle Partial Batch Failures**: Implement proper error handling for partial batch failures in stream processing.
6. **Use EventBridge for Routing**: Leverage EventBridge for complex event routing and filtering logic.
7. **Implement Fan-Out Patterns**: Use SNS topics to fan out events to multiple Lambda functions.
8. **Monitor Event Age**: Track event age to identify processing delays and backlogs.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-lambda
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-lambda/tree/master/examples
- **AWS Lambda Documentation**: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
- **Lambda Best Practices**: https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html
- **Lambda Runtimes**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
- **Lambda Layers**: https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html
- **Lambda Concurrency**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html
- **Lambda Pricing**: https://aws.amazon.com/lambda/pricing/
- **AWS Serverless Application Model (SAM)**: https://docs.aws.amazon.com/serverless-application-model/
- **Lambda Performance Optimization**: https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html#function-code
- **Lambda Security Best Practices**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-security.html
- **Lambda Monitoring**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-monitoring.html
- **Lambda in VPC**: https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html
- **Serverless.tf Framework**: https://serverless.tf/

## Notes for AI Agents

When using this module in automated workflows:

1. **Choose Appropriate Runtime**: Select the most recent runtime version supported by AWS; older runtimes may be deprecated
2. **Build Dependencies Correctly**: Use `pip_requirements = true` for Python or appropriate build configuration for other runtimes
3. **Right-Size Resources**: Start with 512MB memory and adjust based on CloudWatch metrics; higher memory provides more CPU
4. **Use Layers for Large Dependencies**: Extract large dependencies (>10MB) into Lambda layers to reduce deployment package size
5. **Enable CloudWatch Logs**: Always set `attach_cloudwatch_logs_policy = true` and configure appropriate retention periods
6. **Apply Least Privilege IAM**: Use specific IAM policies; avoid `attach_policy = true` with overly permissive policies
7. **Configure VPC Carefully**: Only use VPC when accessing private resources; VPC adds latency to cold starts
8. **Set Appropriate Timeouts**: Configure timeout based on expected execution duration; default 3 seconds is often too short
9. **Use Environment Variables**: Store configuration in environment variables, not hard-coded in function code
10. **Publish Versions**: Set `publish = true` for production functions to enable versioning and rollback capability
11. **Store Large Packages on S3**: Use `store_on_s3 = true` for packages larger than 50MB or for centralized management
12. **Tag Consistently**: Include Environment, Application, Owner, and CostCenter tags on all Lambda resources
13. **Monitor Cold Starts**: Track initialization duration; optimize by reducing package size and dependencies
14. **Implement DLQs**: Configure dead letter queues for async invocations to capture and analyze failures
15. **Test Before Production**: Validate Lambda functions in development/staging environments before production deployment
16. **Use Provisioned Concurrency Sparingly**: Only enable for latency-sensitive functions; it incurs continuous costs
17. **Consider ARM64**: Use ARM64 architecture for better price-performance when runtime and dependencies support it
18. **Implement Proper Error Handling**: Catch exceptions and log errors with context for easier debugging
