---
module_name: datadog-forwarders
keywords: [datadog, monitoring, observability, log-forwarding, metrics, traces, lambda, cloudwatch, rds-monitoring, vpc-flow-logs, privatelink, vpc-endpoints, s3-logs, cloudtrail, elb-logs, cloudfront-logs, kinesis, sns, custom-metrics, enhanced-monitoring, log-aggregation, aws-integration, serverless-monitoring, infrastructure-monitoring, application-monitoring, security-monitoring]
---

# Terraform AWS Datadog Forwarders Module

## Module Information

- **Module Name**: `datadog-forwarders`
- **Source**: `terraform-aws-modules/datadog-forwarders/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-datadog-forwarders
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest
- **Latest Version**: 7.0.0
- **Purpose**: Terraform module that creates AWS Lambda functions and VPC endpoints to forward logs, metrics, and traces from AWS services to Datadog for centralized monitoring and observability
- **Service**: AWS Lambda, Datadog Integration
- **Category**: Monitoring, Observability, Logging
- **Keywords**: datadog, monitoring, observability, log-forwarding, metrics, traces, lambda, cloudwatch, rds-monitoring, vpc-flow-logs, privatelink, vpc-endpoints, s3-logs, cloudtrail, elb-logs, cloudfront-logs, kinesis, sns, custom-metrics, enhanced-monitoring, log-aggregation, aws-integration, serverless-monitoring, infrastructure-monitoring, application-monitoring, security-monitoring
- **Use For**: AWS log aggregation to Datadog, CloudWatch logs forwarding, RDS enhanced monitoring integration, VPC flow log analysis, S3 bucket log collection, CloudTrail security monitoring, ELB access log forwarding, Lambda metrics collection, custom metrics shipping, trace data forwarding, Datadog PrivateLink integration, multi-account log centralization

## Description

This Terraform module provides comprehensive deployment and management of Datadog forwarder Lambda functions and associated infrastructure for shipping AWS logs, metrics, and traces to Datadog. The module creates three specialized forwarder functions: a general-purpose log forwarder for CloudWatch logs, S3 events, Kinesis streams, and various AWS service logs; an RDS enhanced monitoring forwarder for database performance metrics; and a VPC flow log forwarder for network traffic analysis. Each forwarder is implemented as a Python-based Lambda function with configurable memory, timeout, and runtime settings.

The module handles the complete infrastructure setup including S3 buckets for Lambda deployment packages, IAM roles and policies with least-privilege access, CloudWatch log groups for function logging, and optional KMS encryption for sensitive data. It supports secure API key management through AWS Secrets Manager, preventing hardcoding of credentials in Terraform configurations. The forwarders automatically subscribe to relevant CloudWatch log groups and process incoming data in real-time, transforming and forwarding it to Datadog's ingestion endpoints.

Additionally, the module provides optional PrivateLink VPC endpoints for secure, private connectivity to Datadog services including metrics, agent, logs, API, processes, and traces endpoints. This enables organizations to send telemetry data to Datadog without traversing the public internet, improving security and reducing data transfer costs. The module is highly configurable with extensive input variables for customizing forwarder behavior, Lambda function settings, networking configuration, and resource tagging, making it suitable for diverse AWS environments from small single-account deployments to complex multi-account enterprise architectures.

## Key Features

- **Three Specialized Forwarders**: Log forwarder, RDS enhanced monitoring forwarder, and VPC flow log forwarder for different data types
- **Comprehensive Log Source Support**: CloudWatch logs, S3 events, Kinesis streams, CloudTrail, VPC flow logs, ELB access logs, and CloudFront logs
- **RDS Enhanced Monitoring**: Dedicated forwarder for RDS database performance metrics and enhanced monitoring data
- **VPC Flow Log Processing**: Specialized forwarder for network traffic analysis and security monitoring
- **PrivateLink VPC Endpoints**: Optional private connectivity for Datadog agent, metrics, logs, API, processes, and traces
- **Secure API Key Management**: Integration with AWS Secrets Manager for storing Datadog API and application keys
- **KMS Encryption Support**: Optional KMS encryption for Lambda environment variables and sensitive data
- **Configurable Lambda Settings**: Customizable memory size, timeout, runtime version, and architecture (x86_64/arm64)
- **Automatic Log Subscription**: Automatic CloudWatch Logs subscription filter creation for log forwarding
- **S3 Bucket Management**: Automated S3 bucket creation for Lambda deployment packages with versioning support
- **IAM Role Automation**: Pre-configured IAM roles and policies with least-privilege access for each forwarder
- **CloudWatch Log Groups**: Dedicated log groups for forwarder function logging and troubleshooting
- **Multiple Datadog Sites**: Support for different Datadog sites (US, EU, Gov, etc.) via configurable endpoint
- **Custom Metrics Support**: Forward custom metrics from Lambda functions and applications
- **Trace Forwarding**: Support for forwarding distributed traces to Datadog APM
- **Enhanced Lambda Metrics**: Generate enhanced metrics for Lambda function performance
- **Conditional Resource Creation**: Individual enable/disable flags for each forwarder type
- **Flexible Tagging**: Comprehensive tagging support for all created resources
- **Version Control**: Pinnable forwarder version for consistent deployments
- **Multi-Architecture Support**: Lambda functions support both x86_64 and ARM64 (Graviton) architectures

## Main Use Cases

1. **Centralized Log Aggregation**: Collect and forward logs from multiple AWS services to Datadog for unified log management
2. **RDS Database Monitoring**: Monitor RDS database performance with enhanced monitoring metrics in Datadog
3. **Network Security Analysis**: Analyze VPC flow logs for security threats and network traffic patterns
4. **CloudTrail Security Monitoring**: Forward CloudTrail audit logs to Datadog for compliance and security analysis
5. **Application Performance Monitoring**: Collect Lambda execution metrics and custom application metrics
6. **S3 Bucket Activity Tracking**: Monitor S3 bucket access and data operations through access logs
7. **Load Balancer Monitoring**: Forward ELB and ALB access logs for request analysis and performance monitoring
8. **Serverless Observability**: Monitor AWS Lambda functions with enhanced metrics and distributed tracing
9. **Multi-Account Log Centralization**: Aggregate logs from multiple AWS accounts into a single Datadog organization
10. **Private Network Integration**: Use PrivateLink endpoints for secure, private data transmission to Datadog

## Submodules

### 1. log_forwarder

- **Purpose**: AWS Lambda function that forwards logs, custom metrics, and traces from CloudWatch, S3, Kinesis, and other AWS services to Datadog
- **Source**: `terraform-aws-modules/datadog-forwarders/aws//modules/log_forwarder`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest/submodules/log_forwarder
- **Key Features**: CloudWatch log forwarding, S3 event processing, Kinesis stream support, custom metrics generation, enhanced Lambda metrics
- **Use Cases**: General log aggregation, CloudTrail monitoring, S3 access log analysis, Lambda metrics collection

### 2. rds_enhanced_monitoring_forwarder

- **Purpose**: AWS Lambda function that processes RDS enhanced monitoring data from CloudWatch logs and forwards to Datadog
- **Source**: `terraform-aws-modules/datadog-forwarders/aws//modules/rds_enhanced_monitoring_forwarder`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest/submodules/rds_enhanced_monitoring_forwarder
- **Key Features**: RDS performance metrics, Enhanced monitoring data processing, Low memory footprint, Automatic CloudWatch subscription
- **Use Cases**: RDS database monitoring, MySQL/PostgreSQL performance tracking, Aurora cluster monitoring, database performance optimization

### 3. vpc_flow_log_forwarder

- **Purpose**: AWS Lambda function that processes VPC flow log data from CloudWatch logs and forwards to Datadog
- **Source**: `terraform-aws-modules/datadog-forwarders/aws//modules/vpc_flow_log_forwarder`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest/submodules/vpc_flow_log_forwarder
- **Key Features**: VPC flow log processing, Network traffic analysis, KMS encryption requirement, CloudWatch log group reading
- **Use Cases**: Network security monitoring, Traffic pattern analysis, Security group validation, Network troubleshooting

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `tags` | `map(string)` | `{}` | Map of tags to add to all resources |
| `dd_api_key` | `string` | `null` | Datadog API key |
| `dd_api_key_secret_arn` | `string` | `null` | ARN of Secrets Manager secret containing Datadog API key |
| `dd_app_key` | `string` | `null` | Datadog application key |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site to send data to |
| `kms_alias` | `string` | `null` | Alias of KMS key for encryption |
| `create_log_forwarder` | `bool` | `true` | Create log forwarder resources |
| `log_forwarder_name` | `string` | `"datadog-log-forwarder"` | Log forwarder Lambda function name |
| `log_forwarder_runtime` | `string` | `"python3.12"` | Log forwarder Lambda runtime |
| `log_forwarder_memory_size` | `number` | `1024` | Log forwarder memory size in MB |
| `log_forwarder_timeout` | `number` | `120` | Log forwarder timeout in seconds |
| `log_forwarder_version` | `string` | `"4.12.0"` | Datadog forwarder version |
| `create_rds_em_forwarder` | `bool` | `true` | Create RDS enhanced monitoring forwarder |
| `rds_em_forwarder_name` | `string` | `"datadog-rds-enhanced-monitoring-forwarder"` | RDS forwarder function name |
| `rds_em_forwarder_runtime` | `string` | `"python3.12"` | RDS forwarder Lambda runtime |
| `rds_em_forwarder_memory_size` | `number` | `256` | RDS forwarder memory size in MB |
| `create_vpc_fl_forwarder` | `bool` | `true` | Create VPC flow log forwarder |
| `vpc_fl_forwarder_name` | `string` | `"datadog-vpc-flow-log-forwarder"` | VPC flow log forwarder function name |
| `vpc_fl_forwarder_runtime` | `string` | `"python3.12"` | VPC flow log forwarder runtime |
| `vpc_fl_forwarder_memory_size` | `number` | `256` | VPC flow log forwarder memory size in MB |
| `vpc_id` | `string` | `null` | VPC ID for VPC endpoints |
| `subnet_ids` | `list(string)` | `[]` | Subnet IDs for VPC endpoints |
| `security_group_ids` | `list(string)` | `[]` | Security group IDs for VPC endpoints |
| `create_metrics_vpce` | `bool` | `false` | Create Datadog metrics VPC endpoint |
| `create_agent_vpce` | `bool` | `false` | Create Datadog agent VPC endpoint |
| `create_log_forwarder_vpce` | `bool` | `false` | Create Datadog log forwarder VPC endpoint |
| `create_api_vpce` | `bool` | `false` | Create Datadog API VPC endpoint |
| `create_processes_vpce` | `bool` | `false` | Create Datadog processes VPC endpoint |
| `create_traces_vpce` | `bool` | `false` | Create Datadog traces VPC endpoint |

## Main Outputs

| Output | Description |
|--------|-------------|
| `log_forwarder_lambda_arn` | Log forwarder Lambda function ARN |
| `log_forwarder_role_arn` | Log forwarder IAM role ARN |
| `log_forwarder_s3_bucket_arn` | S3 bucket ARN for log forwarder deployment package |
| `log_forwarder_cloudwatch_log_group_arn` | CloudWatch log group ARN for log forwarder |
| `rds_em_forwarder_lambda_arn` | RDS enhanced monitoring forwarder Lambda function ARN |
| `rds_em_forwarder_role_arn` | RDS enhanced monitoring forwarder IAM role ARN |
| `rds_em_forwarder_cloudwatch_log_group_arn` | CloudWatch log group ARN for RDS forwarder |
| `vpc_fl_forwarder_lambda_arn` | VPC flow log forwarder Lambda function ARN |
| `vpc_fl_forwarder_role_arn` | VPC flow log forwarder IAM role ARN |
| `vpc_fl_forwarder_cloudwatch_log_group_arn` | CloudWatch log group ARN for VPC flow log forwarder |
| `metrics_vpce_id` | Datadog metrics VPC endpoint ID |
| `agent_vpce_id` | Datadog agent VPC endpoint ID |
| `log_forwarder_vpce_id` | Datadog log forwarder VPC endpoint ID |
| `api_vpce_id` | Datadog API VPC endpoint ID |
| `processes_vpce_id` | Datadog processes VPC endpoint ID |
| `traces_vpce_id` | Datadog traces VPC endpoint ID |

## Submodule 1: log_forwarder

### Description

The log forwarder submodule creates an AWS Lambda function that ships logs, custom metrics, and traces from various AWS services to Datadog. It supports forwarding from CloudWatch Logs, S3 buckets, Kinesis data streams, CloudTrail, VPC flow logs, SNS topics, ELB access logs, and CloudFront logs. The function automatically processes incoming events, transforms them into Datadog-compatible format, and sends them to the configured Datadog site using the provided API key.

### Key Features

- Forward logs from CloudWatch Logs, S3, CloudTrail, VPC, SNS, CloudFront, and ELB
- Process S3 bucket events and Kinesis data stream events
- Generate enhanced Lambda metrics for function performance monitoring
- Support for custom metrics forwarding from applications
- Automatic retry logic for failed submissions
- Configurable Lambda runtime, memory, and timeout settings
- S3 bucket management for deployment package storage

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `dd_api_key` | `string` | `null` | Datadog API key |
| `dd_api_key_secret_arn` | `string` | `null` | ARN of Secrets Manager secret with API key |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site endpoint |
| `forwarder_version` | `string` | `"4.12.0"` | Datadog forwarder version |
| `name` | `string` | `"datadog-log-forwarder"` | Lambda function name |
| `runtime` | `string` | `"python3.12"` | Lambda runtime |
| `memory_size` | `number` | `1024` | Lambda memory size in MB |
| `timeout` | `number` | `120` | Lambda timeout in seconds |
| `architecture` | `string` | `"arm64"` | Lambda architecture (x86_64 or arm64) |
| `reserved_concurrent_executions` | `number` | `100` | Reserved concurrent executions |
| `tags` | `map(string)` | `{}` | Tags for resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `lambda_arn` | ARN of the forwarder Lambda function |
| `lambda_qualified_arn` | Versioned ARN of Lambda function |
| `role_arn` | ARN of Lambda execution role |
| `role_name` | Name of Lambda execution role |
| `s3_bucket_arn` | ARN of S3 bucket for deployment package |
| `s3_bucket_id` | ID of S3 bucket |
| `cloudwatch_log_group_arn` | ARN of CloudWatch log group |
| `lambda_source_code_hash` | Base64-encoded SHA256 hash of deployment package |

### Usage Example

```hcl
# Store Datadog API key in Secrets Manager
resource "aws_secretsmanager_secret" "datadog_api_key" {
  name        = "datadog-api-key"
  description = "Datadog API Key for log forwarding"
}

resource "aws_secretsmanager_secret_version" "datadog_api_key" {
  secret_id     = aws_secretsmanager_secret.datadog_api_key.id
  secret_string = var.datadog_api_key
}

# Create log forwarder
module "datadog_log_forwarder" {
  source = "terraform-aws-modules/datadog-forwarders/aws//modules/log_forwarder"

  dd_api_key_secret_arn = aws_secretsmanager_secret.datadog_api_key.arn
  dd_site               = "datadoghq.com"

  name                           = "production-log-forwarder"
  forwarder_version              = "4.12.0"
  memory_size                    = 2048
  timeout                        = 300
  reserved_concurrent_executions = 200

  tags = {
    Environment = "production"
    Application = "datadog-integration"
    ManagedBy   = "Terraform"
  }
}

# Subscribe CloudWatch log group to forwarder
resource "aws_cloudwatch_log_subscription_filter" "app_logs" {
  name            = "datadog-log-subscription"
  log_group_name  = aws_cloudwatch_log_group.application.name
  filter_pattern  = ""
  destination_arn = module.datadog_log_forwarder.lambda_arn
}

# Grant permission for CloudWatch Logs to invoke Lambda
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.datadog_log_forwarder.lambda_arn
  principal     = "logs.amazonaws.com"
  source_arn    = "${aws_cloudwatch_log_group.application.arn}:*"
}
```

## Submodule 2: rds_enhanced_monitoring_forwarder

### Description

The RDS enhanced monitoring forwarder submodule creates an AWS Lambda function specifically designed to process RDS enhanced monitoring data from CloudWatch Logs and forward it to Datadog. This forwarder is optimized for handling RDS-specific metrics including OS-level metrics, database engine metrics, and instance-level performance data. It requires minimal memory (256 MB) and automatically subscribes to RDS enhanced monitoring log groups.

### Key Features

- Specialized processing for RDS enhanced monitoring DATA_MESSAGE format
- Optimized for low memory usage (256 MB default)
- Automatic CloudWatch Logs subscription for RDS monitoring
- Support for all RDS database engines (MySQL, PostgreSQL, Oracle, SQL Server, MariaDB, Aurora)
- Real-time metric forwarding to Datadog
- Configurable Lambda runtime and execution parameters

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `dd_api_key` | `string` | `null` | Datadog API key |
| `dd_api_key_secret_arn` | `string` | `null` | ARN of Secrets Manager secret with API key |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site endpoint |
| `forwarder_version` | `string` | `"4.12.0"` | Datadog forwarder version |
| `name` | `string` | `"datadog-rds-enhanced-monitoring-forwarder"` | Lambda function name |
| `runtime` | `string` | `"python3.12"` | Lambda runtime |
| `memory_size` | `number` | `256` | Lambda memory size in MB |
| `timeout` | `number` | `10` | Lambda timeout in seconds |
| `architecture` | `string` | `"arm64"` | Lambda architecture |
| `tags` | `map(string)` | `{}` | Tags for resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `lambda_arn` | ARN of the RDS forwarder Lambda function |
| `lambda_qualified_arn` | Versioned ARN of Lambda function |
| `role_arn` | ARN of Lambda execution role |
| `role_name` | Name of Lambda execution role |
| `cloudwatch_log_group_arn` | ARN of CloudWatch log group |
| `lambda_source_code_hash` | Base64-encoded SHA256 hash of deployment package |

### Usage Example

```hcl
# Create RDS enhanced monitoring forwarder
module "datadog_rds_forwarder" {
  source = "terraform-aws-modules/datadog-forwarders/aws//modules/rds_enhanced_monitoring_forwarder"

  dd_api_key_secret_arn = aws_secretsmanager_secret.datadog_api_key.arn
  dd_site               = "datadoghq.com"

  name      = "rds-monitoring-forwarder"
  tags = {
    Environment = "production"
    Purpose     = "rds-monitoring"
  }
}

# Enable RDS enhanced monitoring on database instance
resource "aws_db_instance" "database" {
  identifier = "production-database"
  engine     = "postgres"

  # Enable enhanced monitoring (60 second granularity)
  enabled_cloudwatch_logs_exports = ["postgresql"]
  monitoring_interval             = 60
  monitoring_role_arn             = aws_iam_role.rds_monitoring.arn

  # Other configuration...
}

# Subscribe enhanced monitoring log group to forwarder
resource "aws_cloudwatch_log_subscription_filter" "rds_monitoring" {
  name            = "datadog-rds-monitoring"
  log_group_name  = "RDSOSMetrics"
  filter_pattern  = ""
  destination_arn = module.datadog_rds_forwarder.lambda_arn
}

# Grant permission for CloudWatch Logs
resource "aws_lambda_permission" "allow_rds_monitoring" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.datadog_rds_forwarder.lambda_arn
  principal     = "logs.amazonaws.com"
  source_arn    = "${data.aws_cloudwatch_log_group.rds_os_metrics.arn}:*"
}
```

## Submodule 3: vpc_flow_log_forwarder

### Description

The VPC flow log forwarder submodule creates an AWS Lambda function that processes VPC flow log data from CloudWatch Logs and forwards it to Datadog for network traffic analysis and security monitoring. This forwarder requires KMS encryption for the Datadog API key and supports optional reading of CloudWatch log groups. It's optimized for processing network flow data and converting it into Datadog's network monitoring format.

### Key Features

- Specialized VPC flow log processing and formatting
- KMS encryption requirement for enhanced security
- Optional CloudWatch log group reading capability
- Network traffic pattern analysis
- Support for VPC flow log custom formats
- Low memory footprint (256 MB default)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `kms_alias` | `string` | required | Alias of KMS key for encryption |
| `dd_api_key_secret_arn` | `string` | `null` | ARN of Secrets Manager secret with API key |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site endpoint |
| `forwarder_version` | `string` | `"4.12.0"` | Datadog forwarder version |
| `name` | `string` | `"datadog-vpc-flow-log-forwarder"` | Lambda function name |
| `runtime` | `string` | `"python3.12"` | Lambda runtime |
| `memory_size` | `number` | `256` | Lambda memory size in MB |
| `timeout` | `number` | `120` | Lambda timeout in seconds |
| `read_cloudwatch_logs` | `bool` | `false` | Whether to read CloudWatch log groups |
| `architecture` | `string` | `"arm64"` | Lambda architecture |
| `tags` | `map(string)` | `{}` | Tags for resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `lambda_arn` | ARN of the VPC flow log forwarder Lambda function |
| `lambda_qualified_arn` | Versioned ARN of Lambda function |
| `role_arn` | ARN of Lambda execution role |
| `role_name` | Name of Lambda execution role |
| `cloudwatch_log_group_arn` | ARN of CloudWatch log group |
| `lambda_source_code_hash` | Base64-encoded SHA256 hash of deployment package |

### Usage Example

```hcl
# Create KMS key for encryption
resource "aws_kms_key" "datadog" {
  description             = "KMS key for Datadog API key encryption"
  deletion_window_in_days = 10

  tags = {
    Name = "datadog-encryption-key"
  }
}

resource "aws_kms_alias" "datadog" {
  name          = "alias/datadog"
  target_key_id = aws_kms_key.datadog.key_id
}

# Create VPC flow log forwarder
module "datadog_vpc_fl_forwarder" {
  source = "terraform-aws-modules/datadog-forwarders/aws//modules/vpc_flow_log_forwarder"

  kms_alias             = aws_kms_alias.datadog.name
  dd_api_key_secret_arn = aws_secretsmanager_secret.datadog_api_key.arn
  dd_site               = "datadoghq.com"

  name                 = "vpc-flow-log-forwarder"
  read_cloudwatch_logs = true

  tags = {
    Environment = "production"
    Purpose     = "network-monitoring"
  }
}

# Create VPC flow log
resource "aws_flow_log" "vpc" {
  vpc_id          = aws_vpc.main.id
  traffic_type    = "ALL"
  iam_role_arn    = aws_iam_role.flow_log.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_log.arn
}

# Subscribe flow log group to forwarder
resource "aws_cloudwatch_log_subscription_filter" "vpc_flow_log" {
  name            = "datadog-vpc-flow-log"
  log_group_name  = aws_cloudwatch_log_group.vpc_flow_log.name
  filter_pattern  = ""
  destination_arn = module.datadog_vpc_fl_forwarder.lambda_arn
}

# Grant permission for CloudWatch Logs
resource "aws_lambda_permission" "allow_vpc_flow_log" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.datadog_vpc_fl_forwarder.lambda_arn
  principal     = "logs.amazonaws.com"
  source_arn    = "${aws_cloudwatch_log_group.vpc_flow_log.arn}:*"
}
```

## Usage Examples

### Example 1: All Forwarders with PrivateLink

```hcl
# Create all forwarders with VPC endpoints
module "datadog_forwarders" {
  source = "terraform-aws-modules/datadog-forwarders/aws"

  kms_alias             = "alias/datadog"
  dd_api_key_secret_arn = aws_secretsmanager_secret.datadog_api_key.arn
  dd_site               = "datadoghq.com"

  # Enable all forwarders
  create_log_forwarder    = true
  create_rds_em_forwarder = true
  create_vpc_fl_forwarder = true

  # PrivateLink VPC endpoints
  vpc_id             = aws_vpc.main.id
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.datadog_vpce.id]

  create_metrics_vpce        = true
  create_agent_vpce          = true
  create_log_forwarder_vpce  = true
  create_api_vpce            = true
  create_processes_vpce      = true
  create_traces_vpce         = true

  tags = {
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}
```

### Example 2: Log Forwarder Only

```hcl
module "log_forwarder_only" {
  source = "terraform-aws-modules/datadog-forwarders/aws"

  dd_api_key_secret_arn = aws_secretsmanager_secret.datadog_api_key.arn

  # Only create log forwarder
  create_log_forwarder    = true
  create_rds_em_forwarder = false
  create_vpc_fl_forwarder = false

  # Customize log forwarder
  log_forwarder_name        = "custom-log-forwarder"
  log_forwarder_memory_size = 2048
  log_forwarder_timeout     = 300

  tags = {
    Environment = "development"
  }
}
```

### Example 3: EU Datadog Site

```hcl
module "datadog_forwarders_eu" {
  source = "terraform-aws-modules/datadog-forwarders/aws"

  dd_api_key_secret_arn = aws_secretsmanager_secret.datadog_api_key_eu.arn
  dd_site               = "datadoghq.eu"  # EU site

  kms_alias = "alias/datadog-eu"

  tags = {
    Environment = "production"
    Region      = "eu-west-1"
  }
}
```

## Best Practices

### Security and Access Control

1. **Use Secrets Manager for API Keys**: Always store Datadog API and application keys in AWS Secrets Manager instead of hardcoding them in Terraform configurations.
2. **Enable KMS Encryption**: Use customer-managed KMS keys for encrypting Lambda environment variables containing sensitive data, especially for the VPC flow log forwarder.
3. **Implement Least Privilege IAM**: Review and customize IAM policies to grant only necessary permissions for each forwarder function.
4. **Use PrivateLink Endpoints**: Deploy VPC endpoints for Datadog services to keep telemetry data within AWS network and avoid public internet exposure.
5. **Rotate API Keys Regularly**: Implement a rotation schedule for Datadog API keys and update Secrets Manager secrets accordingly.
6. **Enable CloudTrail Logging**: Monitor forwarder Lambda function invocations and IAM policy changes through CloudTrail.
7. **Restrict S3 Bucket Access**: Apply bucket policies to restrict access to Lambda deployment packages to authorized principals only.

### Configuration and Deployment

1. **Pin Forwarder Versions**: Specify exact `forwarder_version` values to ensure consistent deployments and controlled updates.
2. **Choose Appropriate Site**: Configure `dd_site` correctly based on your Datadog account region (US, EU, Gov, etc.).
3. **Tag Resources Comprehensively**: Apply tags including Environment, Application, Owner, and CostCenter for resource tracking.
4. **Use ARM64 Architecture**: Leverage ARM64 (Graviton) Lambda functions for better price-performance ratio.
5. **Customize Lambda Settings**: Tune memory size and timeout based on your log volume and processing requirements.
6. **Enable Concurrent Execution Limits**: Set `reserved_concurrent_executions` to prevent Lambda throttling during traffic spikes.
7. **Version Control Configurations**: Store all forwarder configurations in version control systems for audit and rollback capabilities.

### Performance and Optimization

1. **Right-Size Lambda Memory**: Monitor Lambda execution metrics and adjust memory allocation; more memory provides more CPU power.
2. **Optimize Log Filtering**: Use CloudWatch Logs subscription filter patterns to forward only necessary logs and reduce Lambda invocations.
3. **Batch CloudWatch Log Subscriptions**: Subscribe multiple log groups to a single forwarder instead of creating individual forwarders.
4. **Monitor Lambda Metrics**: Track Duration, Errors, Throttles, and ConcurrentExecutions to identify performance issues.
5. **Use Latest Python Runtime**: Keep Lambda runtime up to date (Python 3.12) for performance improvements and security patches.
6. **Configure Appropriate Timeouts**: Set realistic timeout values; 120 seconds for log forwarder, 10 seconds for RDS/VPC forwarders.
7. **Implement Dead Letter Queues**: Configure DLQs for failed invocations to ensure no data loss during processing errors.

### Cost Optimization

1. **Consolidate Forwarders**: Use a single log forwarder for multiple log sources instead of creating separate forwarders per source.
2. **Filter Unnecessary Logs**: Apply subscription filter patterns to exclude debug or verbose logs that don't require forwarding.
3. **Use Reserved Capacity**: For predictable workloads, consider reserved capacity for Lambda to reduce costs.
4. **Monitor Data Transfer**: Track data transfer costs especially when not using PrivateLink endpoints.
5. **Optimize Memory Allocation**: Use AWS Lambda Power Tuning to find optimal memory configuration for cost-performance balance.
6. **Disable Unused Forwarders**: Set `create_*_forwarder = false` for forwarder types not needed in your environment.
7. **Review Datadog Ingestion**: Monitor Datadog log and metric ingestion to identify and reduce unnecessary data transmission.

### Monitoring and Observability

1. **Enable CloudWatch Logs for Forwarders**: Keep forwarder function logs enabled for troubleshooting and debugging.
2. **Set Up CloudWatch Alarms**: Create alarms for Lambda errors, throttles, and duration metrics.
3. **Monitor Datadog Integration**: Use Datadog's AWS Integration dashboard to verify forwarder health and data flow.
4. **Track Lambda Costs**: Use AWS Cost Explorer with resource tags to monitor forwarder Lambda costs.
5. **Implement Error Notifications**: Configure SNS topics or EventBridge rules to notify on Lambda function failures.
6. **Review CloudWatch Logs Retention**: Set appropriate retention periods for forwarder logs to balance costs and compliance.

### Operational Excellence

1. **Document API Key Management**: Maintain clear documentation of which Secrets Manager secrets contain which Datadog API keys.
2. **Test in Non-Production**: Deploy and test forwarders in development/staging before production deployment.
3. **Implement Change Management**: Use Terraform workspaces or separate state files for different environments.
4. **Automate Deployment**: Integrate forwarder deployment into CI/CD pipelines for consistent infrastructure provisioning.
5. **Plan for Disaster Recovery**: Document procedures for recreating forwarders and restoring Secrets Manager secrets.
6. **Regular Version Updates**: Stay current with Datadog forwarder releases for bug fixes and new features.
7. **Maintain Runbooks**: Create operational runbooks for common issues like Lambda throttling or API key expiration.

### High Availability

1. **Deploy Across Multiple AZs**: Use subnet IDs from multiple Availability Zones for VPC endpoints.
2. **Configure Lambda Retries**: Leverage Lambda's built-in retry mechanism for asynchronous invocations.
3. **Implement Circuit Breakers**: Monitor error rates and implement automated remediation for persistent failures.
4. **Use Multiple Forwarders**: For critical workloads, consider deploying redundant forwarders in different regions.
5. **Test Failover Scenarios**: Regularly test forwarder behavior during AWS service disruptions.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-datadog-forwarders
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-datadog-forwarders/tree/master/examples
- **Datadog Forwarder Documentation**: https://docs.datadoghq.com/logs/guide/forwarder/
- **Datadog AWS Integration**: https://docs.datadoghq.com/integrations/amazon_web_services/
- **AWS Lambda Best Practices**: https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html
- **Datadog Log Collection**: https://docs.datadoghq.com/logs/log_collection/
- **Datadog PrivateLink**: https://docs.datadoghq.com/agent/guide/private-link/
- **AWS Secrets Manager**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/
- **CloudWatch Logs Subscription Filters**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/SubscriptionFilters.html
- **RDS Enhanced Monitoring**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.html
- **VPC Flow Logs**: https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Store API Keys Securely**: Always use AWS Secrets Manager for Datadog API keys via `dd_api_key_secret_arn`
2. **Enable Required Forwarders**: Set `create_*_forwarder` flags based on actual monitoring needs
3. **Configure Datadog Site**: Specify correct `dd_site` value based on Datadog account region
4. **Use KMS Encryption**: Provide `kms_alias` for VPC flow log forwarder (required)
5. **Tag Resources**: Apply comprehensive tags for cost allocation and resource tracking
6. **Choose Right Architecture**: Use ARM64 for cost savings; x86_64 for compatibility if needed
7. **Set Appropriate Memory**: Log forwarder: 1024-2048 MB; RDS/VPC forwarders: 256 MB
8. **Configure PrivateLink**: Enable VPC endpoints for secure, private data transmission
9. **Monitor Lambda Metrics**: Track errors, throttles, and duration for performance optimization
10. **Implement Log Filtering**: Use CloudWatch subscription filter patterns to reduce costs
11. **Version Control**: Pin `forwarder_version` for consistent deployments
12. **Test Before Production**: Validate forwarder configurations in non-production environments
13. **Document Integration**: Maintain clear documentation of log sources and subscription filters
14. **Plan for Scale**: Set `reserved_concurrent_executions` based on expected log volume
15. **Review IAM Policies**: Customize IAM policies to grant minimum required permissions
