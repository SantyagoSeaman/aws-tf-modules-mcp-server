# Terraform AWS Datadog Forwarders Module

## Module Information

- **Module Name**: `datadog-forwarders`
- **Source**: `terraform-aws-modules/datadog-forwarders/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-datadog-forwarders
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest
- **Latest Version**: 4.12.0
- **Purpose**: Creates AWS Lambda functions and VPC endpoints to forward logs, metrics, and traces from AWS services to Datadog
- **Service**: AWS Lambda, Datadog Integration
- **Category**: Monitoring, Observability, Logging
- **Keywords**: datadog, log-forwarding, lambda, cloudwatch-logs, rds-monitoring, vpc-flow-logs, privatelink, s3-logs, cloudtrail, metrics, traces, observability
- **Use For**: AWS log aggregation to Datadog, CloudWatch logs forwarding, RDS enhanced monitoring integration, VPC flow log analysis, S3 bucket log collection, CloudTrail security monitoring, Datadog PrivateLink integration

## Description

This module deploys Datadog forwarder Lambda functions for shipping AWS logs, metrics, and traces to Datadog. It creates three specialized forwarders: a log forwarder for CloudWatch logs, S3 events, and various AWS service logs; an RDS enhanced monitoring forwarder for database performance metrics; and a VPC flow log forwarder for network traffic analysis. Lambda artifacts are vendored within the module, eliminating external downloads during CI/CD.

The module manages complete infrastructure including S3 buckets for Lambda packages, IAM roles with least-privilege access, and CloudWatch log groups. It supports secure API key management through AWS Secrets Manager and KMS encryption for sensitive data. Forwarders use ARM64 architecture by default for cost optimization.

Optional PrivateLink VPC endpoints provide secure, private connectivity to Datadog services (metrics, agent, logs, API, processes, traces) without traversing the public internet. The module supports flexible IAM management - bring your own roles/policies or let the module create them.

## Key Features

- **Three Specialized Forwarders**: Log forwarder, RDS enhanced monitoring forwarder, and VPC flow log forwarder
- **Comprehensive Log Sources**: CloudWatch logs, S3 events, CloudTrail, VPC flow logs, ELB/CloudFront access logs
- **PrivateLink VPC Endpoints**: Six endpoint types (metrics, agent, log forwarder, API, processes, traces)
- **Vendored Lambda Artifacts**: Lambda zip files packaged within module (no external downloads during CI/CD)
- **Secrets Manager Integration**: Secure API key management via `dd_api_key_secret_arn`
- **KMS Encryption**: Required for RDS and VPC flow log forwarders
- **ARM64 Default Architecture**: Cost-optimized Graviton architecture (x86_64 also supported)
- **Flexible IAM Management**: Bring your own roles/policies or let the module create them
- **Multiple Datadog Sites**: Support for US (`datadoghq.com`), EU (`datadoghq.eu`), and Gov regions
- **Conditional Resource Creation**: Individual enable/disable flags for each forwarder and endpoint
- **VPC Deployment**: Forwarders can run inside VPC with security groups and subnets

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

### Required

| Variable | Type | Description |
|----------|------|-------------|
| `kms_alias` | `string` | KMS key alias for encrypting Datadog API key |

**Note**: Either `dd_api_key_secret_arn` (recommended) OR `dd_api_key` must be provided.

### Datadog Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `dd_api_key_secret_arn` | `string` | `""` | ARN of Secrets Manager secret containing Datadog API key |
| `dd_api_key` | `string` | `""` | Datadog API key (alternative to Secrets Manager) |
| `dd_app_key` | `string` | `""` | Datadog application key |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site (`datadoghq.com`, `datadoghq.eu`) |

### Feature Toggles

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_log_forwarder` | `bool` | `true` | Create log forwarder Lambda |
| `create_rds_em_forwarder` | `bool` | `true` | Create RDS enhanced monitoring forwarder |
| `create_vpc_fl_forwarder` | `bool` | `true` | Create VPC flow log forwarder |
| `create_bucket` | `bool` | `true` | Create S3 bucket for Lambda artifacts |
| `create_metrics_vpce` | `bool` | `false` | Create metrics VPC endpoint |
| `create_agent_vpce` | `bool` | `false` | Create agent VPC endpoint |
| `create_log_forwarder_vpce` | `bool` | `false` | Create log forwarder VPC endpoint |
| `create_api_vpce` | `bool` | `false` | Create API VPC endpoint |
| `create_processes_vpce` | `bool` | `false` | Create processes VPC endpoint |
| `create_traces_vpce` | `bool` | `false` | Create traces VPC endpoint |

### Log Forwarder Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `log_forwarder_version` | `string` | `"4.12.0"` | Datadog forwarder version |
| `log_forwarder_name` | `string` | `"datadog-log-forwarder"` | Lambda function name |
| `log_forwarder_memory_size` | `number` | `1024` | Memory in MB |
| `log_forwarder_timeout` | `number` | `120` | Timeout in seconds |
| `log_forwarder_runtime` | `string` | `"python3.12"` | Lambda runtime |
| `log_forwarder_architectures` | `list(string)` | `["arm64"]` | CPU architecture |
| `log_forwarder_reserved_concurrent_executions` | `number` | `100` | Reserved concurrency |
| `log_forwarder_s3_log_bucket_arns` | `list(string)` | `[]` | S3 buckets to read logs from |
| `log_forwarder_subnet_ids` | `list(string)` | `null` | VPC subnet IDs |
| `log_forwarder_security_group_ids` | `list(string)` | `null` | VPC security group IDs |
| `log_forwarder_log_retention_days` | `number` | `7` | CloudWatch log retention |

### RDS Enhanced Monitoring Forwarder

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `rds_em_forwarder_name` | `string` | `"datadog-rds-enhanced-monitoring-forwarder"` | Lambda function name |
| `rds_em_forwarder_memory_size` | `number` | `256` | Memory in MB |
| `rds_em_forwarder_timeout` | `number` | `10` | Timeout in seconds |
| `rds_em_forwarder_reserved_concurrent_executions` | `number` | `10` | Reserved concurrency |

### VPC Flow Log Forwarder

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_fl_forwarder_name` | `string` | `"datadog-vpc-flow-log-forwarder"` | Lambda function name |
| `vpc_fl_forwarder_memory_size` | `number` | `256` | Memory in MB |
| `vpc_fl_forwarder_timeout` | `number` | `10` | Timeout in seconds |
| `vpc_fl_forwarder_s3_log_bucket_arns` | `list(string)` | `[]` | S3 buckets containing VPC flow logs |
| `vpc_fl_forwarder_read_cloudwatch_logs` | `bool` | `false` | Allow reading CloudWatch logs |

### VPC Endpoints

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_id` | `string` | `null` | VPC ID for endpoint creation |
| `*_vpce_subnet_ids` | `list(string)` | `[]` | Subnet IDs for each endpoint type |
| `*_vpce_security_group_ids` | `list(string)` | `[]` | Security group IDs for each endpoint |

### Common

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `tags` | `map(string)` | `{}` | Tags to add to all resources |

## Main Outputs

### Log Forwarder

| Output | Description |
|--------|-------------|
| `log_forwarder_lambda_arn` | Lambda function ARN |
| `log_forwarder_lambda_qualified_arn` | Qualified ARN with version |
| `log_forwarder_role_arn` | IAM role ARN |
| `log_forwarder_s3_bucket_id` | S3 bucket name for artifacts |
| `log_forwarder_cloudwatch_log_group_arn` | CloudWatch log group ARN |

### RDS Enhanced Monitoring Forwarder

| Output | Description |
|--------|-------------|
| `rds_em_forwarder_lambda_arn` | Lambda function ARN |
| `rds_em_forwarder_role_arn` | IAM role ARN |
| `rds_em_forwarder_cloudwatch_log_group_arn` | CloudWatch log group ARN |

### VPC Flow Log Forwarder

| Output | Description |
|--------|-------------|
| `vpc_fl_forwarder_lambda_arn` | Lambda function ARN |
| `vpc_fl_forwarder_role_arn` | IAM role ARN |
| `vpc_fl_forwarder_cloudwatch_log_group_arn` | CloudWatch log group ARN |

### VPC Endpoints

| Output | Description |
|--------|-------------|
| `*_endpoint_id` | VPC endpoint ID |
| `*_endpoint_arn` | VPC endpoint ARN |
| `*_endpoint_dns_entry` | DNS entries for endpoint |

## Submodule 1: log_forwarder

### Description

Standalone log forwarder Lambda function that ships logs, custom metrics, and traces from CloudWatch Logs, S3 buckets, and other AWS services to Datadog. Use this submodule when you only need the log forwarder without RDS or VPC flow log forwarders.

### Key Features

- Forward logs from CloudWatch Logs, S3, CloudTrail, SNS, CloudFront, and ELB
- Generate enhanced Lambda metrics for function performance monitoring
- ARM64 architecture default for cost optimization
- Configurable Lambda runtime, memory, and timeout settings

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `dd_api_key_secret_arn` | `string` | `""` | ARN of Secrets Manager secret with API key |
| `dd_api_key` | `string` | `""` | Datadog API key (alternative) |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site endpoint |
| `forwarder_version` | `string` | `"4.12.0"` | Datadog forwarder version |
| `name` | `string` | `"datadog-log-forwarder"` | Lambda function name |
| `memory_size` | `number` | `1024` | Lambda memory in MB |
| `timeout` | `number` | `120` | Lambda timeout in seconds |
| `architectures` | `list(string)` | `["arm64"]` | Lambda architecture |
| `reserved_concurrent_executions` | `number` | `100` | Reserved concurrent executions |
| `s3_log_bucket_arns` | `list(string)` | `[]` | S3 buckets to read logs from |

### Main Outputs

| Output | Description |
|--------|-------------|
| `lambda_arn` | Lambda function ARN |
| `lambda_qualified_arn` | Versioned ARN |
| `role_arn` | IAM execution role ARN |
| `s3_bucket_id` | S3 bucket ID for artifacts |
| `cloudwatch_log_group_arn` | CloudWatch log group ARN |

### Usage Example

```hcl
module "datadog_log_forwarder" {
  source  = "terraform-aws-modules/datadog-forwarders/aws//modules/log_forwarder"
  version = "~> 4.12"

  kms_alias             = "alias/datadog"
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  name        = "production-log-forwarder"
  memory_size = 2048
  timeout     = 300

  s3_log_bucket_arns = [
    "arn:aws:s3:::my-application-logs",
    "arn:aws:s3:::my-cloudtrail-logs"
  ]

  tags = {
    Environment = "production"
  }
}

# Subscribe CloudWatch log group to forwarder
resource "aws_cloudwatch_log_subscription_filter" "app_logs" {
  name            = "datadog-log-subscription"
  log_group_name  = aws_cloudwatch_log_group.application.name
  filter_pattern  = ""
  destination_arn = module.datadog_log_forwarder.lambda_arn
}

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

Standalone Lambda function that processes RDS enhanced monitoring data from CloudWatch Logs and forwards to Datadog. Optimized for low memory usage (256 MB) and handles OS-level metrics, database engine metrics, and instance-level performance data.

### Key Features

- Specialized processing for RDS enhanced monitoring DATA_MESSAGE format
- Low memory footprint (256 MB default)
- Support for all RDS database engines (MySQL, PostgreSQL, Oracle, SQL Server, MariaDB, Aurora)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `dd_api_key_secret_arn` | `string` | `""` | ARN of Secrets Manager secret with API key |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site endpoint |
| `name` | `string` | `"datadog-rds-enhanced-monitoring-forwarder"` | Lambda function name |
| `memory_size` | `number` | `256` | Lambda memory in MB |
| `timeout` | `number` | `10` | Lambda timeout in seconds |
| `reserved_concurrent_executions` | `number` | `10` | Reserved concurrency |

### Main Outputs

| Output | Description |
|--------|-------------|
| `lambda_arn` | Lambda function ARN |
| `role_arn` | IAM execution role ARN |
| `cloudwatch_log_group_arn` | CloudWatch log group ARN |

### Usage Example

```hcl
module "datadog_rds_forwarder" {
  source  = "terraform-aws-modules/datadog-forwarders/aws//modules/rds_enhanced_monitoring_forwarder"
  version = "~> 4.12"

  kms_alias             = "alias/datadog"
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  name = "rds-monitoring-forwarder"

  tags = {
    Environment = "production"
  }
}

# Subscribe RDS enhanced monitoring log group to forwarder
resource "aws_cloudwatch_log_subscription_filter" "rds_monitoring" {
  name            = "datadog-rds-monitoring"
  log_group_name  = "RDSOSMetrics"
  filter_pattern  = ""
  destination_arn = module.datadog_rds_forwarder.lambda_arn
}

resource "aws_lambda_permission" "allow_rds_monitoring" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.datadog_rds_forwarder.lambda_arn
  principal     = "logs.amazonaws.com"
  source_arn    = "arn:aws:logs:*:*:log-group:RDSOSMetrics:*"
}
```

## Submodule 3: vpc_flow_log_forwarder

### Description

Standalone Lambda function that processes VPC flow log data from CloudWatch Logs or S3 and forwards to Datadog for network traffic analysis and security monitoring. Requires KMS encryption for the Datadog API key.

### Key Features

- VPC flow log processing and formatting for Datadog
- KMS encryption requirement for security
- Support for CloudWatch Logs and S3 sources
- Low memory footprint (256 MB default)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `kms_alias` | `string` | required | KMS key alias for encryption |
| `dd_api_key_secret_arn` | `string` | `""` | ARN of Secrets Manager secret with API key |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site endpoint |
| `name` | `string` | `"datadog-vpc-flow-log-forwarder"` | Lambda function name |
| `memory_size` | `number` | `256` | Lambda memory in MB |
| `timeout` | `number` | `10` | Lambda timeout in seconds |
| `s3_log_bucket_arns` | `list(string)` | `[]` | S3 buckets containing VPC flow logs |
| `read_cloudwatch_logs` | `bool` | `false` | Allow reading CloudWatch logs |

### Main Outputs

| Output | Description |
|--------|-------------|
| `lambda_arn` | Lambda function ARN |
| `role_arn` | IAM execution role ARN |
| `cloudwatch_log_group_arn` | CloudWatch log group ARN |

### Usage Example

```hcl
module "datadog_vpc_fl_forwarder" {
  source  = "terraform-aws-modules/datadog-forwarders/aws//modules/vpc_flow_log_forwarder"
  version = "~> 4.12"

  kms_alias             = "alias/datadog"
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  name                 = "vpc-flow-log-forwarder"
  read_cloudwatch_logs = true

  tags = {
    Environment = "production"
  }
}

# Subscribe flow log group to forwarder
resource "aws_cloudwatch_log_subscription_filter" "vpc_flow_log" {
  name            = "datadog-vpc-flow-log"
  log_group_name  = aws_cloudwatch_log_group.vpc_flow_log.name
  filter_pattern  = ""
  destination_arn = module.datadog_vpc_fl_forwarder.lambda_arn
}

resource "aws_lambda_permission" "allow_vpc_flow_log" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.datadog_vpc_fl_forwarder.lambda_arn
  principal     = "logs.amazonaws.com"
  source_arn    = "${aws_cloudwatch_log_group.vpc_flow_log.arn}:*"
}
```

## Usage Examples

### Example 1: Basic - All Forwarders

```hcl
# Prerequisites: KMS key and Secrets Manager secret must exist
data "aws_secretsmanager_secret" "datadog_api_key" {
  name = "datadog/api_key"
}

module "datadog_forwarders" {
  source  = "terraform-aws-modules/datadog-forwarders/aws"
  version = "~> 4.12"

  kms_alias             = "alias/datadog"
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  tags = {
    Environment = "production"
  }
}
```

### Example 2: Log Forwarder Only with S3 Sources

```hcl
module "log_forwarder_only" {
  source  = "terraform-aws-modules/datadog-forwarders/aws"
  version = "~> 4.12"

  kms_alias             = "alias/datadog"
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  # Disable other forwarders
  create_rds_em_forwarder = false
  create_vpc_fl_forwarder = false

  # Customize log forwarder
  log_forwarder_name        = "custom-log-forwarder"
  log_forwarder_memory_size = 2048
  log_forwarder_timeout     = 300
  log_forwarder_s3_log_bucket_arns = [
    "arn:aws:s3:::my-application-logs",
    "arn:aws:s3:::my-cloudtrail-logs"
  ]

  tags = {
    Environment = "production"
  }
}
```

### Example 3: All Forwarders with PrivateLink VPC Endpoints

```hcl
module "datadog_forwarders" {
  source  = "terraform-aws-modules/datadog-forwarders/aws"
  version = "~> 4.12"

  kms_alias             = "alias/datadog"
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  # VPC configuration
  vpc_id = module.vpc.vpc_id

  # Enable VPC endpoints for private connectivity
  create_metrics_vpce             = true
  metrics_vpce_subnet_ids         = module.vpc.private_subnets
  metrics_vpce_security_group_ids = [aws_security_group.datadog.id]

  create_agent_vpce             = true
  agent_vpce_subnet_ids         = module.vpc.private_subnets
  agent_vpce_security_group_ids = [aws_security_group.datadog.id]

  create_log_forwarder_vpce             = true
  log_forwarder_vpce_subnet_ids         = module.vpc.private_subnets
  log_forwarder_vpce_security_group_ids = [aws_security_group.datadog.id]

  # Lambda VPC configuration
  log_forwarder_subnet_ids         = module.vpc.private_subnets
  log_forwarder_security_group_ids = [aws_security_group.lambda.id]

  tags = {
    Environment = "production"
  }
}
```

### Example 4: EU Datadog Site

```hcl
module "datadog_forwarders_eu" {
  source  = "terraform-aws-modules/datadog-forwarders/aws"
  version = "~> 4.12"

  kms_alias             = "alias/datadog-eu"
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key_eu.arn
  dd_site               = "datadoghq.eu"  # EU site

  tags = {
    Environment = "production"
    Region      = "eu-west-1"
  }
}
```

## Best Practices

### Security

1. **Use Secrets Manager**: Store Datadog API keys in AWS Secrets Manager via `dd_api_key_secret_arn` (recommended over `dd_api_key`)
2. **Enable KMS Encryption**: Create KMS key and provide `kms_alias` (required for VPC flow log forwarder)
3. **Use PrivateLink**: Deploy VPC endpoints for private connectivity to Datadog (no public internet exposure)
4. **Enable S3 Security**: Set `bucket_attach_deny_insecure_transport_policy = true` for Lambda artifact bucket

### Configuration

1. **Pin Forwarder Version**: Specify `log_forwarder_version` for consistent deployments
2. **Set Correct Site**: Configure `dd_site` based on your Datadog region (`datadoghq.com`, `datadoghq.eu`)
3. **Use ARM64**: Keep default `["arm64"]` architecture for cost optimization
4. **Set Concurrency Limits**: Configure `reserved_concurrent_executions` based on expected log volume

### Performance

1. **Right-Size Memory**: Log forwarder: 1024-2048 MB; RDS/VPC forwarders: 256 MB
2. **Filter Logs**: Use CloudWatch subscription filter patterns to forward only necessary logs
3. **Consolidate Forwarders**: Use single log forwarder for multiple log sources
4. **Set Realistic Timeouts**: Log forwarder: 120s; RDS/VPC forwarders: 10s

### Cost Optimization

1. **Disable Unused Forwarders**: Set `create_*_forwarder = false` when not needed
2. **Filter Before Forwarding**: Exclude debug/verbose logs at subscription filter level
3. **Monitor Datadog Ingestion**: Track log/metric volume to optimize data transmission

### Important Notes

1. **Prerequisites**: Module does NOT create Secrets Manager secret or KMS key - you must create them beforehand
2. **VPC Endpoints Default Disabled**: All `create_*_vpce` variables default to `false`
3. **CloudWatch Log Retention**: Default is only 7 days (`log_forwarder_log_retention_days`)
4. **ARM64 Default**: Forwarders use ARM64 architecture by default

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-datadog-forwarders
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-datadog-forwarders/tree/master/examples
- **Datadog Forwarder Documentation**: https://docs.datadoghq.com/logs/guide/forwarder/
- **Datadog AWS Integration**: https://docs.datadoghq.com/integrations/amazon_web_services/
- **Datadog PrivateLink**: https://docs.datadoghq.com/agent/guide/private-link/

## Notes for AI Agents

When generating Terraform code with this module:

1. **Required Prerequisites**: Create KMS key and Secrets Manager secret BEFORE using module
2. **Required Variable**: `kms_alias` is required; either `dd_api_key_secret_arn` or `dd_api_key` must be provided
3. **Use Secrets Manager**: Prefer `dd_api_key_secret_arn` over `dd_api_key` for security
4. **Datadog Site**: Set `dd_site = "datadoghq.eu"` for EU customers (default is US)
5. **Disable Unused**: Set `create_rds_em_forwarder = false` and/or `create_vpc_fl_forwarder = false` if not needed
6. **VPC Endpoints**: All `create_*_vpce` default to `false` - enable only if PrivateLink needed
7. **Log Subscriptions**: Create `aws_cloudwatch_log_subscription_filter` and `aws_lambda_permission` for each log group
8. **Memory Sizing**: Log forwarder default 1024 MB is sufficient; increase for high-volume use cases
9. **Version Pinning**: Use `version = "~> 4.12"` in module source for stability
