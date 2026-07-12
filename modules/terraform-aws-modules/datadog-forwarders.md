# Terraform AWS Datadog Forwarders Module

## Module Information

- **Module Name**: `datadog-forwarders`
- **Module ID**: `terraform-aws-modules/datadog-forwarders/aws`
- **Source**: `terraform-aws-modules/datadog-forwarders/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-datadog-forwarders
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest
- **Latest Version**: 7.2.0
- **Compatibility**: Terraform >= 1.5.7, AWS provider >= 6.28 (root module and all three submodules; raised from `>= 1.3`/`>= 5.0` in v6.x by the v7.0.0 breaking change) — pin `~> 7.2` when generating configs.
- **Purpose**: Terraform module that deploys AWS Lambda based Datadog forwarders (log/CloudWatch, RDS enhanced monitoring, VPC flow logs) plus optional PrivateLink VPC endpoints, to ship AWS logs, metrics, and traces to Datadog
- **Service**: AWS Lambda, Amazon CloudWatch, Datadog Integration
- **Category**: Monitoring, Observability, Logging
- **Keywords**: datadog, log-forwarding, lambda, cloudwatch-logs, rds-monitoring, vpc-flow-logs, privatelink, vpc-endpoint, s3-logs, cloudtrail, kms-encryption, secrets-manager, observability, serverless
- **Use For**: centralized AWS log aggregation to Datadog, RDS enhanced monitoring integration, VPC flow log security analysis, CloudTrail/S3/ELB/CloudFront log forwarding, Lambda custom metrics and distributed tracing, PrivateLink-only connectivity to Datadog, multi-account log centralization, EU/Gov Datadog site compliance

## Description

This module deploys up to three purpose-built AWS Lambda "forwarder" functions that ship data to Datadog, plus optional AWS PrivateLink VPC endpoints for private connectivity to Datadog's ingestion services. The **log forwarder** ships CloudWatch Logs, S3 events, CloudTrail, VPC flow logs, ELB/CloudFront access logs, Kinesis stream events, and Lambda custom metrics/traces to Datadog. The **RDS enhanced monitoring forwarder** parses RDS `RDSOSMetrics` `DATA_MESSAGE` payloads and forwards database performance metrics. The **VPC flow log forwarder** processes VPC flow log records for network traffic analysis. All three wrap Datadog's official [`datadog-serverless-functions`](https://github.com/DataDog/datadog-serverless-functions) Lambda code, which is vendored as zip artifacts inside the module (avoiding the need to download/build artifacts during `terraform apply`, including in ephemeral CI/CD runners).

The root module composes three local submodules (`modules/log_forwarder`, `modules/rds_enhanced_monitoring_forwarder`, `modules/vpc_flow_log_forwarder`), each independently toggleable via `create_*_forwarder` flags and independently usable on its own. Every forwarder supports full "bring your own IAM" patterns (`*_role_arn`/`*_policy_arn`, or disable module-managed IAM via `create_*_role`/`create_*_role_policy` and attach a custom policy), arbitrary Lambda environment variables (`*_environment_variables`) for PII redaction/scrubbing rules/PrivateLink endpoint overrides, and optional VPC deployment (`*_subnet_ids`/`*_security_group_ids`). Optional PrivateLink VPC endpoints (metrics, agent, log-intake, API, processes, traces — six total) let all forwarder traffic and Datadog Agent traffic stay off the public internet.

The module itself does **not** create the KMS key or Secrets Manager secret needed to store the Datadog API key — these must be provisioned separately and passed in via `kms_alias` and `dd_api_key_secret_arn`. Note that the module's own semantic version (`7.2.0`) is unrelated to the `log_forwarder_version`/`rds_em_forwarder_version`/`vpc_fl_forwarder_version` input variables, which pin the vendored upstream Datadog forwarder Lambda code version (default `4.12.0`, following Datadog's own release numbering) — do not confuse the two when reading examples or pinning versions.

## Key Features

- **Three Specialized Forwarders**: Log forwarder, RDS enhanced monitoring forwarder, VPC flow log forwarder — each independently enabled via `create_log_forwarder`/`create_rds_em_forwarder`/`create_vpc_fl_forwarder`
- **Comprehensive Log Sources**: CloudWatch Logs, S3 events, CloudTrail, VPC flow logs, ELB/CloudFront access logs, Kinesis data streams, Lambda enhanced metrics
- **Six PrivateLink VPC Endpoints**: metrics, agent, log forwarder (intake), API, processes, and traces endpoints for private connectivity to Datadog — all disabled by default
- **Vendored Lambda Artifacts**: Datadog forwarder zip files packaged within the module; no external downloads during `terraform apply` or CI/CD
- **Full BYO-IAM Support**: Each forwarder can use module-managed IAM (with `use_role_name_prefix`, `role_path`, `permissions_boundary`) or accept externally-managed `role_arn`/`policy_arn`
- **Custom Lambda Environment Variables**: `*_environment_variables` per forwarder for scrubbing rules, PII redaction (`REDACT_IP`, `REDACT_EMAIL`), and PrivateLink `DD_URL` overrides
- **Layered Encryption**: KMS CMK (via `kms_alias`) encrypts the Datadog API key; separate optional `*_kms_key_arn` encrypts Lambda environment variables; separate optional `*_log_kms_key_id` encrypts CloudWatch log groups
- **Secrets Manager Integration**: Recommended secure API key delivery via `dd_api_key_secret_arn` (plaintext `dd_api_key` also supported but discouraged)
- **ARM64 Default Architecture**: Cost-optimized Graviton architecture by default (`x86_64` also supported)
- **Multiple Datadog Sites**: `datadoghq.com` (default), `datadoghq.eu`, and Gov regions via `dd_site`
- **VPC Deployment**: Each forwarder Lambda can run inside a VPC with its own subnets/security groups
- **S3 Artifact Bucket Controls**: Encryption, SSE-C blocking, and deny-insecure-transport policy on the log forwarder's Lambda zip artifact bucket

## Main Use Cases

1. **Centralized Log Aggregation**: Collect and forward logs from multiple AWS services to Datadog for unified log management
2. **RDS Database Monitoring**: Monitor RDS/Aurora database performance with enhanced monitoring metrics in Datadog
3. **Network Security Analysis**: Analyze VPC flow logs in Datadog for threats and traffic patterns
4. **CloudTrail Security Monitoring**: Forward CloudTrail audit logs to Datadog for compliance and security analysis
5. **Serverless Observability**: Collect Lambda enhanced metrics, custom metrics, and distributed traces from CloudWatch logs
6. **S3 Bucket Activity Tracking**: Monitor S3 access/data-event logs shipped to an S3 bucket the forwarder reads from
7. **Load Balancer Monitoring**: Forward ELB/ALB and CloudFront access logs for request analysis
8. **Private Connectivity Compliance**: Use PrivateLink VPC endpoints to keep all Datadog traffic off the public internet
9. **Multi-Account Log Centralization**: Aggregate logs from multiple AWS accounts into a single Datadog organization
10. **EU/Gov Data Residency**: Route data to the `datadoghq.eu` or Gov Datadog site for regional compliance requirements

## Submodules

### 1. log_forwarder
- **Purpose**: AWS Lambda function that forwards logs, custom metrics, and traces from CloudWatch, S3, Kinesis, and other AWS services to Datadog
- **Source**: `terraform-aws-modules/datadog-forwarders/aws//modules/log_forwarder`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest/submodules/log_forwarder
- **Key Features**: CloudWatch/S3/CloudTrail/Kinesis log ingestion, enhanced Lambda metrics generation, its own vendored S3 artifact bucket (via `terraform-aws-modules/s3-bucket/aws`), full BYO-IAM support

### 2. rds_enhanced_monitoring_forwarder
- **Purpose**: AWS Lambda function that processes RDS enhanced monitoring `DATA_MESSAGE` payloads from CloudWatch logs and forwards them to Datadog
- **Source**: `terraform-aws-modules/datadog-forwarders/aws//modules/rds_enhanced_monitoring_forwarder`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest/submodules/rds_enhanced_monitoring_forwarder
- **Key Features**: Low default memory footprint (256 MB), supports all RDS engines (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Aurora), does **not** require `kms_alias`

### 3. vpc_flow_log_forwarder
- **Purpose**: AWS Lambda function that processes VPC flow log `DATA_MESSAGE` payloads from CloudWatch logs (or S3) and forwards them to Datadog
- **Source**: `terraform-aws-modules/datadog-forwarders/aws//modules/vpc_flow_log_forwarder`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest/submodules/vpc_flow_log_forwarder
- **Key Features**: Network traffic analysis, the only submodule that directly requires `kms_alias` (re-encrypts the Datadog API key via `aws_kms_ciphertext` for the vendored Lambda code), low default memory footprint (256 MB)

## Main Input Variables

### Required

| Variable | Type | Description |
|----------|------|-------------|
| `kms_alias` | `string` | Alias of a pre-existing KMS CMK (must start with `alias/`) used to encrypt/decrypt the Datadog API key. Always required at the **root module** level — even if `create_vpc_fl_forwarder = false` — because it has no default. The key/alias itself is **not** created by this module. |

### Datadog Authentication

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `dd_api_key_secret_arn` | `string` | `""` | ARN of a Secrets Manager secret containing the Datadog API key (recommended over `dd_api_key`) |
| `dd_api_key` | `string` | `""` | Plaintext Datadog API key; used only if `dd_api_key_secret_arn` is unset — avoid in production, prefer Secrets Manager |
| `dd_app_key` | `string` | `""` | Datadog application key (consumed by the VPC flow log forwarder) |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site (`datadoghq.com`, `datadoghq.eu`, or Gov endpoints) |

### Feature Toggles

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_log_forwarder` | `bool` | `true` | Create the log forwarder Lambda |
| `create_rds_em_forwarder` | `bool` | `true` | Create the RDS enhanced monitoring forwarder Lambda |
| `create_vpc_fl_forwarder` | `bool` | `true` | Create the VPC flow log forwarder Lambda |
| `create_metrics_vpce` / `create_agent_vpce` / `create_log_forwarder_vpce` / `create_api_vpce` / `create_processes_vpce` / `create_traces_vpce` | `bool` | `false` | Create the corresponding PrivateLink VPC endpoint — all six default to disabled |

### Log Forwarder Lambda Artifact Bucket (root-level, no prefix — used only by the log forwarder)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_bucket` | `bool` | `true` | Create the S3 bucket hosting the log forwarder's Lambda zip artifact |
| `bucket_name` | `string` | `""` | Artifact bucket name (auto-generated when empty) |
| `bucket_attach_deny_insecure_transport_policy` | `bool` | `true` | Deny non-TLS requests to the artifact bucket |
| `bucket_encryption_settings` | `map(string)` | `{sse_algorithm = "AES256"}` | Server-side encryption for the artifact bucket |
| `bucket_blocked_encryption_types` | `list(string)` | `["SSE-C"]` | Encryption types rejected on object upload |

### Log Forwarder Configuration (`log_forwarder_*`)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `log_forwarder_version` | `string` | `"4.12.0"` | Vendored Datadog forwarder Lambda code version (independent of the module's own version) |
| `log_forwarder_name` | `string` | `"datadog-log-forwarder"` | Lambda function name |
| `log_forwarder_memory_size` | `number` | `1024` | Memory in MB |
| `log_forwarder_timeout` | `number` | `120` | Timeout in seconds |
| `log_forwarder_runtime` | `string` | `"python3.12"` | Lambda runtime |
| `log_forwarder_architectures` | `list(string)` | `["arm64"]` | CPU architecture (`["arm64"]` or `["x86_64"]`) |
| `log_forwarder_reserved_concurrent_executions` | `number` | `100` | Reserved concurrency |
| `log_forwarder_s3_log_bucket_arns` | `list(string)` | `[]` | S3 buckets the forwarder is granted read access to |
| `log_forwarder_subnet_ids` / `log_forwarder_security_group_ids` | `list(string)` | `null` | Run the Lambda inside a VPC |
| `log_forwarder_environment_variables` | `map(string)` | `{}` | Extra Lambda env vars (`REDACT_IP`, `REDACT_EMAIL`, `DD_SCRUBBING_RULE`, `DD_URL` for PrivateLink, etc.) |
| `log_forwarder_log_retention_days` | `number` | `7` | CloudWatch log group retention |
| `create_log_forwarder_role` / `create_log_forwarder_role_policy` | `bool` | `true` | Disable to bring your own IAM via `log_forwarder_role_arn`/`log_forwarder_policy_arn` |
| `log_forwarder_role_arn` / `log_forwarder_policy_arn` | `string` | `null` | Externally-managed IAM role/policy ARN (BYO-IAM) |
| `log_forwarder_kms_key_arn` | `string` | `null` | KMS key for encrypting Lambda environment variables (separate from `kms_alias`) |

### RDS Enhanced Monitoring Forwarder Configuration (`rds_em_forwarder_*`)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `rds_em_forwarder_version` | `string` | `"4.12.0"` | Vendored forwarder Lambda code version |
| `rds_em_forwarder_name` | `string` | `"datadog-rds-enhanced-monitoring-forwarder"` | Lambda function name |
| `rds_em_forwarder_memory_size` | `number` | `256` | Memory in MB |
| `rds_em_forwarder_timeout` | `number` | `10` | Timeout in seconds |
| `rds_em_forwarder_reserved_concurrent_executions` | `number` | `10` | Reserved concurrency |
| `rds_em_forwarder_environment_variables` | `map(string)` | `{}` | Extra Lambda env vars |
| `create_rds_em_forwarder_role` / `create_rds_em_forwarder_role_policy` | `bool` | `true` | Disable for BYO-IAM (`rds_em_forwarder_role_arn`/`rds_em_forwarder_policy_arn`) |

### VPC Flow Log Forwarder Configuration (`vpc_fl_forwarder_*`)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_fl_forwarder_version` | `string` | `"4.12.0"` | Vendored forwarder Lambda code version |
| `vpc_fl_forwarder_name` | `string` | `"datadog-vpc-flow-log-forwarder"` | Lambda function name |
| `vpc_fl_forwarder_memory_size` | `number` | `256` | Memory in MB |
| `vpc_fl_forwarder_timeout` | `number` | `10` | Timeout in seconds |
| `vpc_fl_forwarder_s3_log_bucket_arns` | `list(string)` | `[]` | S3 buckets containing VPC flow logs |
| `vpc_fl_forwarder_read_cloudwatch_logs` | `bool` | `false` | Allow reading VPC flow logs from CloudWatch Logs (in addition to/instead of S3) |
| `create_vpc_fl_forwarder_role` / `create_vpc_fl_forwarder_role_policy` | `bool` | `true` | Disable for BYO-IAM (`vpc_fl_forwarder_role_arn`/`vpc_fl_forwarder_policy_arn`) |

### VPC Endpoints

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_id` | `string` | `null` | VPC ID for endpoint creation (required if any `create_*_vpce` is `true`) |
| `*_vpce_subnet_ids` | `list(string)` | `[]` | Subnet IDs for each endpoint type (`metrics`, `agent`, `log_forwarder`, `api`, `processes`, `traces`) |
| `*_vpce_security_group_ids` | `list(string)` | `[]` | Security group IDs for each endpoint |
| `*_vpce_policy` | `any` | `null` | Endpoint policy document (defaults to full access) |

### Common

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

## Main Outputs

### Log Forwarder

| Output | Description |
|--------|-------------|
| `log_forwarder_lambda_arn` / `log_forwarder_lambda_qualified_arn` | Lambda function ARN (qualified when `publish = true`) |
| `log_forwarder_role_arn` / `log_forwarder_role_name` | IAM role ARN/name |
| `log_forwarder_s3_bucket_id` / `log_forwarder_s3_bucket_arn` | S3 artifact bucket name/ARN |
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
| `*_endpoint_id` / `*_endpoint_arn` | VPC endpoint ID/ARN, per endpoint type |
| `*_endpoint_dns_entry` | DNS entries for the endpoint |
| `*_endpoint_network_interface_ids` | ENIs backing the endpoint |

## Submodule 1: log_forwarder

### Description

Standalone log forwarder Lambda that ships logs, custom metrics, and traces from CloudWatch Logs, S3, and other AWS services to Datadog. Use this submodule directly when only the log forwarder is needed, without the RDS or VPC flow log forwarders. It is the only submodule that creates its own S3 bucket (via `terraform-aws-modules/s3-bucket/aws`) for the vendored Lambda zip artifact, and does **not** require `kms_alias`.

### Key Features

- Forward logs from CloudWatch Logs, S3, CloudTrail, SNS, CloudFront, and ELB
- Generate enhanced Lambda metrics (`aws.lambda.enhanced.*`) parsed from the AWS REPORT log line
- ARM64 architecture default for cost optimization
- Full BYO-IAM support and custom Lambda environment variables

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `dd_api_key_secret_arn` | `string` | `""` | ARN of Secrets Manager secret with the API key |
| `dd_api_key` | `string` | `""` | Datadog API key (plaintext alternative) |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site endpoint |
| `forwarder_version` | `string` | `"4.12.0"` | Vendored Datadog forwarder Lambda code version |
| `name` | `string` | `"datadog-log-forwarder"` | Lambda function name |
| `memory_size` | `number` | `1024` | Lambda memory in MB |
| `timeout` | `number` | `120` | Lambda timeout in seconds |
| `architectures` | `list(string)` | `["arm64"]` | Lambda CPU architecture |
| `reserved_concurrent_executions` | `number` | `100` | Reserved concurrent executions |
| `s3_log_bucket_arns` | `list(string)` | `[]` | S3 buckets to read logs from |
| `environment_variables` | `map(string)` | `{}` | Extra Lambda environment variables |
| `create_role` / `create_role_policy` | `bool` | `true` | Disable for BYO-IAM (`role_arn`/`policy_arn`) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `lambda_arn` / `lambda_qualified_arn` | Lambda function ARN (qualified when `publish = true`) |
| `role_arn` | IAM execution role ARN |
| `s3_bucket_id` / `s3_bucket_arn` | S3 bucket for the Lambda zip artifact |
| `cloudwatch_log_group_arn` | CloudWatch log group ARN |

### Usage Example

```hcl
module "datadog_log_forwarder" {
  source  = "terraform-aws-modules/datadog-forwarders/aws//modules/log_forwarder"
  version = "~> 7.2"

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

# Subscribe a CloudWatch log group to the forwarder
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

Standalone Lambda function that processes RDS enhanced monitoring `DATA_MESSAGE` payloads from CloudWatch Logs and forwards them to Datadog. Optimized for low memory usage (256 MB default) and handles OS-level metrics, database engine metrics, and instance-level performance data. Does **not** require `kms_alias` or a KMS-encrypted secret.

### Key Features

- Specialized processing for the RDS enhanced monitoring `DATA_MESSAGE` format
- Low memory footprint (256 MB default)
- Supports all RDS database engines (MySQL, PostgreSQL, Oracle, SQL Server, MariaDB, Aurora)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `dd_api_key_secret_arn` | `string` | `""` | ARN of Secrets Manager secret with the API key |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site endpoint |
| `name` | `string` | `"datadog-rds-enhanced-monitoring-forwarder"` | Lambda function name |
| `memory_size` | `number` | `256` | Lambda memory in MB |
| `timeout` | `number` | `10` | Lambda timeout in seconds |
| `reserved_concurrent_executions` | `number` | `10` | Reserved concurrency |
| `environment_variables` | `map(string)` | `{}` | Extra Lambda environment variables |
| `create_role` / `create_role_policy` | `bool` | `true` | Disable for BYO-IAM (`role_arn`/`policy_arn`) |

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
  version = "~> 7.2"

  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  name = "rds-monitoring-forwarder"

  tags = {
    Environment = "production"
  }
}

# Subscribe the RDS enhanced monitoring log group to the forwarder
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

Standalone Lambda function that processes VPC flow log `DATA_MESSAGE` payloads from CloudWatch Logs (or S3) and forwards them to Datadog for network traffic analysis and security monitoring. This is the **only** submodule that requires `kms_alias` — it re-encrypts the Datadog API key with the referenced KMS CMK via `aws_kms_ciphertext` for consumption by the vendored Lambda code.

### Key Features

- VPC flow log processing and formatting for Datadog
- KMS re-encryption of the Datadog API key (required)
- Supports both CloudWatch Logs and S3 as log sources
- Low memory footprint (256 MB default)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `kms_alias` | `string` | required | Alias (`alias/...`) of the KMS CMK used to re-encrypt the Datadog API key |
| `dd_api_key_secret_arn` | `string` | `""` | ARN of Secrets Manager secret with the API key |
| `dd_app_key` | `string` | `""` | Datadog application key |
| `dd_site` | `string` | `"datadoghq.com"` | Datadog site endpoint |
| `name` | `string` | `"datadog-vpc-flow-log-forwarder"` | Lambda function name |
| `memory_size` | `number` | `256` | Lambda memory in MB |
| `timeout` | `number` | `10` | Lambda timeout in seconds |
| `s3_log_bucket_arns` | `list(string)` | `[]` | S3 buckets containing VPC flow logs |
| `read_cloudwatch_logs` | `bool` | `false` | Allow reading VPC flow logs from CloudWatch Logs |
| `create_role` / `create_role_policy` | `bool` | `true` | Disable for BYO-IAM (`role_arn`/`policy_arn`) |

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
  version = "~> 7.2"

  kms_alias             = "alias/datadog" # KMS key/alias must already exist
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  name                 = "vpc-flow-log-forwarder"
  read_cloudwatch_logs = true

  tags = {
    Environment = "production"
  }
}

# Subscribe the flow log group to the forwarder
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

Prerequisites for all examples: a KMS CMK + alias and a Secrets Manager secret holding the Datadog API key must exist beforehand — this module does not create them.

```hcl
resource "aws_kms_key" "datadog" {
  description         = "Datadog KMS CMK"
  enable_key_rotation = true
}

resource "aws_kms_alias" "datadog" {
  name          = "alias/datadog"
  target_key_id = aws_kms_key.datadog.key_id
}

# Create this secret out-of-band (e.g. via `aws secretsmanager put-secret-value`)
# so the API key is never passed to Terraform in plaintext
data "aws_secretsmanager_secret" "datadog_api_key" {
  name = "datadog/api_key"
}
```

### Example 1: Basic — All Three Forwarders

```hcl
module "datadog_forwarders" {
  source  = "terraform-aws-modules/datadog-forwarders/aws"
  version = "~> 7.2"

  kms_alias             = aws_kms_alias.datadog.name
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  tags = {
    Environment = "production"
  }
}
```

### Example 2: Log Forwarder Only, with S3 Sources

```hcl
module "log_forwarder_only" {
  source  = "terraform-aws-modules/datadog-forwarders/aws"
  version = "~> 7.2"

  kms_alias             = aws_kms_alias.datadog.name
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  # Disable the other two forwarders
  create_rds_em_forwarder = false
  create_vpc_fl_forwarder = false

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
  version = "~> 7.2"

  kms_alias             = aws_kms_alias.datadog.name
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  vpc_id = module.vpc.vpc_id

  create_metrics_vpce             = true
  metrics_vpce_subnet_ids         = module.vpc.private_subnets
  metrics_vpce_security_group_ids = [aws_security_group.datadog.id]

  create_agent_vpce             = true
  agent_vpce_subnet_ids         = module.vpc.private_subnets
  agent_vpce_security_group_ids = [aws_security_group.datadog.id]

  create_log_forwarder_vpce             = true
  log_forwarder_vpce_subnet_ids         = module.vpc.private_subnets
  log_forwarder_vpce_security_group_ids = [aws_security_group.datadog.id]

  # Run the log forwarder Lambda inside the same VPC so it can reach the endpoints
  log_forwarder_subnet_ids         = module.vpc.private_subnets
  log_forwarder_security_group_ids = [aws_security_group.lambda.id]

  # Required to route the forwarder's traffic through the log-intake PrivateLink endpoint
  log_forwarder_environment_variables = {
    DD_USE_PRIVATE_LINK  = true
    DD_FETCH_LAMBDA_TAGS = false # required when using PrivateLink
    DD_URL               = "api-pvtlink.logs.datadoghq.com"
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 4: EU Datadog Site

```hcl
module "datadog_forwarders_eu" {
  source  = "terraform-aws-modules/datadog-forwarders/aws"
  version = "~> 7.2"

  kms_alias             = aws_kms_alias.datadog_eu.name
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key_eu.arn
  dd_site               = "datadoghq.eu"

  tags = {
    Environment = "production"
    Region      = "eu-west-1"
  }
}
```

### Example 5: Custom (BYO) IAM Policy for the Log Forwarder

```hcl
data "aws_iam_policy_document" "custom_log_forwarder" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "tag:GetResources",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "custom_log_forwarder" {
  name   = "custom-datadog-log-forwarder"
  policy = data.aws_iam_policy_document.custom_log_forwarder.json
}

module "datadog_forwarders" {
  source  = "terraform-aws-modules/datadog-forwarders/aws"
  version = "~> 7.2"

  kms_alias             = aws_kms_alias.datadog.name
  dd_api_key_secret_arn = data.aws_secretsmanager_secret.datadog_api_key.arn

  # Skip the module-managed policy and attach a custom one instead
  create_log_forwarder_role_policy = false
  log_forwarder_policy_arn         = aws_iam_policy.custom_log_forwarder.arn

  tags = {
    Environment = "production"
  }
}
```

## Best Practices

### Security

1. **Use Secrets Manager**: Store the Datadog API key in AWS Secrets Manager via `dd_api_key_secret_arn` rather than the plaintext `dd_api_key` variable.
2. **Create a dedicated KMS CMK for Datadog**: The module doesn't create the CMK — provision one with `enable_key_rotation = true` and a tightly scoped key policy, and reference it via `kms_alias`.
3. **Prefer PrivateLink over public endpoints**: Enable the relevant `create_*_vpce` flags and set `DD_USE_PRIVATE_LINK = true` / the matching `DD_URL` in `*_environment_variables` for traffic that must stay off the public internet.
4. **Keep the S3 artifact bucket private and encrypted**: Leave `bucket_attach_deny_insecure_transport_policy = true` (default) and don't widen `bucket_blocked_encryption_types` unless required.
5. **Scope custom IAM narrowly**: When using BYO-IAM (`create_*_role_policy = false` + `*_policy_arn`), grant only `logs:*`, `tag:GetResources`, and the specific S3/Secrets Manager ARNs each forwarder needs — not `*`.

### Configuration

1. **Pin the module version**: Use `version = "~> 7.2"` — the `log_forwarder_version`/`rds_em_forwarder_version`/`vpc_fl_forwarder_version` variables pin the vendored Datadog code separately and do not track the module version.
2. **Set the correct Datadog site**: Configure `dd_site` (`datadoghq.com`, `datadoghq.eu`, Gov) to match the account's Datadog organization region.
3. **Keep ARM64 unless you need x86_64-only layers**: The `["arm64"]` default is cheaper; only switch `*_architectures` to `["x86_64"]` for compatibility reasons.
4. **Set concurrency limits deliberately**: Tune `*_reserved_concurrent_executions` based on expected log volume to avoid throttling other Lambdas in the account.

### Performance

1. **Right-size memory**: Log forwarder 1024–2048 MB for high log volume; RDS/VPC-FL forwarders are fine at the 256 MB default.
2. **Filter before subscribing**: Use `filter_pattern` on `aws_cloudwatch_log_subscription_filter` to avoid forwarding noisy/irrelevant log lines.
3. **Consolidate log sources**: Route multiple CloudWatch log groups to one log forwarder rather than deploying several log forwarders.

### Cost Optimization

1. **Disable unused forwarders**: Set `create_rds_em_forwarder = false` and/or `create_vpc_fl_forwarder = false` when not needed — both default to `true`.
2. **Exclude debug/verbose logs at the subscription filter**, not inside the Lambda, to reduce both Lambda invocations and Datadog ingestion volume.
3. **Enable PrivateLink endpoints only where needed**: Interface VPC endpoints bill per-hour per-AZ — six enabled endpoints in a 3-AZ VPC add up quickly.

### Important Notes / Gotchas

1. **Prerequisites are not created by this module**: The KMS key/alias and the Secrets Manager secret must exist before `terraform apply`.
2. **`kms_alias` is always required at the root level**, even if you set `create_vpc_fl_forwarder = false` — it has no default and Terraform will fail plan/apply without it. It is **not** a valid input for the `log_forwarder` or `rds_enhanced_monitoring_forwarder` submodules when used standalone — don't pass it there.
3. **Two unrelated version numbers**: the module's semantic version (e.g. `7.2.0`, used in `version = "~> 7.2"`) is independent from `log_forwarder_version`/`rds_em_forwarder_version`/`vpc_fl_forwarder_version` (default `"4.12.0"`, Datadog's own forwarder code release).
4. **VPC endpoints default disabled**: All six `create_*_vpce` variables default to `false`.
5. **CloudWatch log retention defaults to 7 days** (`*_log_retention_days`) — raise it for compliance/audit needs.
6. **v7.0.0 was a breaking change**: minimum Terraform bumped to `>= 1.5.7` and AWS provider to `>= 6.0` (currently `>= 6.28`) — upgrading from a 4.x/5.x/6.x pin requires bumping the provider first.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-datadog-forwarders
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/datadog-forwarders/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-datadog-forwarders/tree/master/examples
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-datadog-forwarders/blob/master/CHANGELOG.md
- **Datadog Serverless Functions (upstream Lambda code)**: https://github.com/DataDog/datadog-serverless-functions
- **Datadog Forwarder Documentation**: https://docs.datadoghq.com/serverless/forwarder/
- **Datadog AWS Integration**: https://docs.datadoghq.com/integrations/amazon_web_services/
- **Datadog PrivateLink Guide**: https://docs.datadoghq.com/agent/guide/private-link/

## Notes for AI Agents

When generating Terraform code with this module:

1. **Required prerequisites**: Create a KMS CMK + alias and a Secrets Manager secret holding the Datadog API key *before* calling this module — it does not create either.
2. **Always set `kms_alias`** on the root module call, even when only the log or RDS forwarder is enabled — it's a required root-level input with no default.
3. **Never pass `kms_alias` into the `log_forwarder` or `rds_enhanced_monitoring_forwarder` submodules directly** — it is not a valid input for either; only `vpc_flow_log_forwarder` and the root module accept it.
4. **Prefer `dd_api_key_secret_arn` over `dd_api_key`** for security; the latter puts the key in plaintext state.
5. **Set `dd_site = "datadoghq.eu"`** for EU customers (default is the US site).
6. **Disable unneeded forwarders** with `create_rds_em_forwarder = false` / `create_vpc_fl_forwarder = false` (both default `true`).
7. **VPC endpoints are opt-in**: set the relevant `create_*_vpce = true` plus matching `*_vpce_subnet_ids`/`*_vpce_security_group_ids`, and set `vpc_id`.
8. **Wire log subscriptions manually**: creating a forwarder does not auto-subscribe log groups — add `aws_cloudwatch_log_subscription_filter` and `aws_lambda_permission` resources pointing at the forwarder's `lambda_arn` output for each log group to forward.
9. **Use `version = "~> 7.2"`**, not `"~> 4.12"` (an older major version) — do not confuse the module version with the `*_forwarder_version` variable defaults, which happen to read `"4.12.0"`.
10. **For BYO-IAM**, set `create_*_role_policy = false` (or `create_*_role = false`) and provide `*_policy_arn` (or `*_role_arn`) instead of relying on the module-managed IAM.
11. **For PrivateLink-only traffic**, set the relevant `*_environment_variables` (`DD_USE_PRIVATE_LINK = true`, `DD_FETCH_LAMBDA_TAGS = false`, `DD_URL = "api-pvtlink.logs.datadoghq.com"`) in addition to enabling the VPC endpoints and running the Lambda inside the VPC.
