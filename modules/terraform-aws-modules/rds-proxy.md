# Terraform AWS RDS Proxy Module

## Module Information

- **Module Name**: `rds-proxy`
- **Module ID**: `terraform-aws-modules/rds-proxy/aws`
- **Source**: `terraform-aws-modules/rds-proxy/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds-proxy
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds-proxy/aws/latest
- **Latest Version**: 4.4.0
- **Purpose**: Terraform module that creates an AWS RDS Proxy and its supporting resources (target group, endpoints, IAM role/policy, CloudWatch log group) for connection pooling in front of RDS instances or Aurora clusters
- **Service**: AWS RDS Proxy (Amazon RDS Proxy)
- **Category**: Database, Connection Management, Scalability
- **Keywords**: rds-proxy, connection-pooling, database-proxy, aurora, mysql, postgresql, secrets-manager, iam-authentication, serverless-database, lambda-rds, tls-encryption, session-pinning, cloudwatch-logs, ipv6, connection-management
- **Use For**: Lambda database connections, serverless application databases, connection pooling for microservices, containerized application databases (ECS/Fargate/Kubernetes), high-traffic database access, unpredictable database workloads, database failover automation, credential rotation without downtime, connection storm prevention, database CPU optimization, IPv6-only VPC deployments

## Description

AWS RDS Proxy is a fully managed database proxy service that sits between applications and relational databases, providing intelligent connection pooling, credential management, and enhanced database resilience. This Terraform module deploys a single `aws_db_proxy` and its supporting resources: a default target group, one or more `aws_db_proxy_endpoint` resources, an IAM role and inline policy scoped to Secrets Manager/KMS access, and an optional CloudWatch log group. It supports both `MYSQL` and `POSTGRESQL` engine families and can target either a standalone RDS instance (`target_db_instance`) or an Aurora cluster (`target_db_cluster`), letting applications share and reuse database connections instead of opening a new connection per request.

The module addresses a common problem in serverless and containerized architectures, where applications (e.g. Lambda functions, ECS tasks) can rapidly open thousands of short-lived database connections, overwhelming the database and degrading performance. By pooling and multiplexing connections, RDS Proxy reduces the CPU/memory overhead of connection establishment, authenticates using credentials stored in AWS Secrets Manager (with optional IAM database authentication), and automatically fails over to standby instances without requiring application changes.

The module's IAM role/policy is scoped to least privilege: it grants `kms:Decrypt` only via the Secrets Manager service principal (restricted to `kms_key_arns` when provided) and `secretsmanager:GetSecretValue`/related actions only for the secret ARNs referenced in `auth`. It exposes fine-grained connection-pool tuning (borrow timeout, idle percentages, session pinning filters, init query), configurable read-write/read-only endpoints, and — as of v4.4.0 — IPv4/IPv6/dual-stack network type controls for both the proxy endpoint and the target connection. The module has no submodules; it is a single, focused resource set.

## Key Features

- **Managed Connection Pooling**: Pools and reuses database connections to reduce CPU/memory overhead on the target database
- **MySQL and PostgreSQL Support**: Full support for both `MYSQL` and `POSTGRESQL` engine families
- **Aurora and RDS Compatibility**: Targets either an Aurora cluster (`target_db_cluster`) or a standalone RDS instance (`target_db_instance`), mutually exclusive
- **Multi-Credential Auth Map**: Configure multiple named authentication entries (`auth`), each with its own Secrets Manager secret, auth scheme, and optional IAM auth setting
- **IAM Database Authentication**: Supports per-auth-entry `iam_auth` plus a proxy-wide `default_auth_scheme` (`NONE`/`IAM_AUTH`) for passwordless client access
- **Read-Write / Read-Only Endpoints**: Create additional named `aws_db_proxy_endpoint` resources (e.g. for distributing read traffic to Aurora replicas) via the `endpoints` map
- **IPv4/IPv6/Dual-Stack Networking** (v4.4.0+): Control proxy endpoint and target connection network types via `endpoint_network_type` and `target_connection_network_type`
- **TLS Enforcement**: `require_tls = true` by default, enforcing encrypted client connections
- **Session Pinning Control**: `session_pinning_filters` lets you exclude specific SQL operation classes from pinning a session to one connection
- **Init Query Support**: Run SQL statements (`init_query`) automatically on every new pooled database connection
- **Connection Pool Tuning**: `max_connections_percent`, `max_idle_connections_percent`, `idle_client_timeout`, `connection_borrow_timeout`
- **Least-Privilege IAM Automation**: Auto-creates an IAM role and inline policy scoped to only the Secrets Manager secrets referenced in `auth` (toggle via `create_iam_role`/`create_iam_policy`, or supply `role_arn`)
- **CloudWatch Logs Integration**: Configurable log group with retention, storage class (`STANDARD`/`INFREQUENT_ACCESS`), and CMK encryption; optional debug/SQL statement logging
- **Region Override**: `region` variable allows per-resource region targeting for multi-region provider setups
- **Conditional Creation**: `create` flag toggles nearly all resources for use in conditional/composed root modules
- **Granular Tagging**: Separate tag maps for the proxy (`proxy_tags`), IAM role (`iam_role_tags`), and log group (`log_group_tags`) in addition to global `tags`
- **No Submodules**: Single-purpose module with a compact, predictable resource graph

## Main Use Cases

1. **Serverless Database Connections**: Optimize database connections for AWS Lambda functions that frequently scale up and down
2. **Containerized Applications**: Manage database connections for ECS, Fargate, and Kubernetes workloads with unpredictable scaling
3. **Microservices Architecture**: Provide efficient connection pooling for many microservices accessing shared databases
4. **Connection Storm Prevention**: Prevent database overload during traffic spikes by pooling and queuing connections
5. **High-Availability Applications**: Automatically redirect connections to standby/replica instances during failover
6. **Credential Rotation**: Rotate database credentials via Secrets Manager without application downtime or reconnection storms
7. **IAM-Authenticated Access**: Enable passwordless database access using proxy-level IAM database authentication
8. **Read Workload Distribution**: Distribute read queries across Aurora read replicas using dedicated read-only endpoints
9. **Database Performance Optimization**: Reduce database CPU/memory overhead caused by frequent connection churn
10. **IPv6-Only Networking**: Deploy proxy endpoints and target connections in IPv6-only or dual-stack VPC subnets

## Submodules

This module has **no submodules**. It is a standalone module that creates all RDS Proxy resources directly (`aws_db_proxy`, `aws_db_proxy_default_target_group`, `aws_db_proxy_target`, `aws_db_proxy_endpoint`, `aws_cloudwatch_log_group`, `aws_iam_role`, `aws_iam_role_policy`).

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Proxy identifier (must begin with a letter, ASCII letters/digits/hyphens only) |
| `engine_family` | `string` | `""` | Database engine type: `"MYSQL"` or `"POSTGRESQL"` (effectively required) |
| `vpc_subnet_ids` | `list(string)` | `[]` | VPC subnet IDs for proxy deployment (2+ AZs recommended) |
| `vpc_security_group_ids` | `list(string)` | `[]` | Security groups for the proxy |
| `auth` | `map(object)` | `{ default = { auth_scheme = "SECRETS" } }` | Named auth entries: `auth_scheme`, `client_password_auth_type`, `description`, `iam_auth`, `secret_arn`, `username` |
| `target_db_cluster` | `bool` | `false` | Set to `true` to target an Aurora cluster (mutually exclusive with `target_db_instance`) |
| `target_db_instance` | `bool` | `false` | Set to `true` to target a standalone RDS instance |
| `db_cluster_identifier` | `string` | `""` | Target Aurora cluster identifier (when `target_db_cluster = true`) |
| `db_instance_identifier` | `string` | `""` | Target RDS instance identifier (when `target_db_instance = true`) |
| `require_tls` | `bool` | `true` | Enforce TLS encryption for client connections to the proxy |
| `default_auth_scheme` | `string` | `null` | Proxy-wide default auth scheme: `"NONE"` or `"IAM_AUTH"` |
| `endpoint_network_type` | `string` | `null` | Proxy endpoint network type: `IPV4`, `IPV6`, or `DUAL` |
| `target_connection_network_type` | `string` | `null` | Network type for proxy-to-database connections: `IPV4` or `IPV6` |
| `endpoints` | `map(object)` | `{}` | Additional named `aws_db_proxy_endpoint` resources (e.g. read-only endpoint) |
| `max_connections_percent` | `number` | `90` | Maximum connection pool size as a percentage of target's max connections |
| `max_idle_connections_percent` | `number` | `50` | Idle connection threshold percentage |
| `idle_client_timeout` | `number` | `1800` | Seconds before idle client connections disconnect |
| `connection_borrow_timeout` | `number` | `null` | Seconds to wait for an available pooled connection |
| `session_pinning_filters` | `list(string)` | `[]` | SQL operation classes excluded from connection pinning |
| `init_query` | `string` | `""` | SQL statement(s) run on every new pooled database connection |
| `debug_logging` | `bool` | `false` | Enable SQL statement logging to CloudWatch (disable in production) |
| `create_iam_role` | `bool` | `true` | Create IAM role for Secrets Manager/KMS access |
| `create_iam_policy` | `bool` | `true` | Create the inline IAM policy attached to the role |
| `role_arn` | `string` | `""` | Existing IAM role ARN to use instead of creating one |
| `kms_key_arns` | `list(string)` | `[]` | KMS key ARNs the IAM policy is scoped to for secret decryption |
| `manage_log_group` | `bool` | `true` | Create the CloudWatch log group (fails if already exists) |
| `log_group_retention_in_days` | `number` | `30` | CloudWatch log retention period |
| `log_group_class` | `string` | `null` | `STANDARD` or `INFREQUENT_ACCESS` (cost optimization) |
| `region` | `string` | `null` | AWS region override for all resources in this module call |
| `create` | `bool` | `true` | Set to `false` to disable creation of nearly all resources |
| `tags` | `map(string)` | `{}` | Tags applied to all resources (merged with per-resource tag maps) |

## Main Outputs

| Output | Description |
|--------|-------------|
| `proxy_id` | The ID of the proxy |
| `proxy_arn` | The ARN of the proxy |
| `proxy_endpoint` | Primary proxy endpoint for database connections |
| `proxy_default_target_group_id` | The ID of the default target group |
| `proxy_default_target_group_arn` | The ARN of the default target group |
| `proxy_default_target_group_name` | The name of the default target group |
| `proxy_target_id` | Identifier combining proxy name, target group, target type, and resource ID |
| `proxy_target_type` | Target type, e.g. `RDS_INSTANCE` or `TRACKED_CLUSTER` |
| `proxy_target_endpoint` | Hostname for the target RDS instance (only for `RDS_INSTANCE` targets) |
| `proxy_target_port` | Port for the target database |
| `proxy_target_rds_resource_id` | Identifier representing the DB instance or DB cluster target |
| `db_proxy_endpoints` | Full resource objects/attributes for all configured DB proxy endpoints |
| `log_group_arn` | CloudWatch log group ARN |
| `log_group_name` | CloudWatch log group name |
| `iam_role_arn` | IAM role ARN used by the proxy |
| `iam_role_name` | IAM role name |
| `iam_role_unique_id` | Stable and unique string identifying the IAM role |

## Usage Examples

### PostgreSQL Aurora Cluster with Read-Write/Read-Only Endpoints

```hcl
module "rds_proxy" {
  source  = "terraform-aws-modules/rds-proxy/aws"
  version = "~> 4.4"

  name                   = "pg-proxy"
  iam_role_name          = "pg-proxy-role"
  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [module.rds_proxy_sg.security_group_id]

  engine_family = "POSTGRESQL"

  # Target Aurora cluster
  target_db_cluster     = true
  db_cluster_identifier = module.rds.cluster_id

  # Authentication via Secrets Manager (Aurora-managed master user secret)
  auth = {
    root = {
      description = "Cluster generated master user password"
      secret_arn  = module.rds.cluster_master_user_secret[0].secret_arn
    }
  }

  # Separate endpoints for write and read traffic
  endpoints = {
    read_write = {
      name                   = "read-write-endpoint"
      vpc_subnet_ids         = module.vpc.private_subnets
      vpc_security_group_ids = [module.rds_proxy_sg.security_group_id]
    }
    read_only = {
      name                   = "read-only-endpoint"
      vpc_subnet_ids         = module.vpc.private_subnets
      vpc_security_group_ids = [module.rds_proxy_sg.security_group_id]
      target_role            = "READ_ONLY"
    }
  }

  kms_key_arns = [module.kms.key_arn]

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

# NOTE: when the underlying database itself uses IAM database authentication,
# it must be disabled at the RDS/Aurora level - RDS Proxy requires
# username/password (Secrets Manager) auth against the target database.
# module "rds" { ... iam_database_authentication_enabled = false ... }
```

### MySQL RDS Instance with Connection Pool Tuning

```hcl
module "rds_proxy" {
  source  = "terraform-aws-modules/rds-proxy/aws"
  version = "~> 4.4"

  name                   = "mysql-proxy"
  iam_role_name          = "mysql-proxy-role"
  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [module.rds_proxy_sg.security_group_id]

  engine_family = "MYSQL"
  debug_logging = true

  # Target standalone RDS instance
  target_db_instance     = true
  db_instance_identifier = module.rds.db_instance_identifier

  auth = {
    app_user = {
      description = "Application user credentials"
      secret_arn  = aws_secretsmanager_secret.db_credentials.arn
    }
  }

  # Connection pool tuning
  max_connections_percent      = 80
  max_idle_connections_percent = 40
  idle_client_timeout          = 3600
  session_pinning_filters      = ["EXCLUDE_VARIABLE_SETS"]

  log_group_retention_in_days = 7
  log_group_class             = "INFREQUENT_ACCESS"

  tags = {
    Environment = "development"
  }
}
```

### Lambda-Optimized IAM-Authenticated Configuration

```hcl
module "rds_proxy" {
  source  = "terraform-aws-modules/rds-proxy/aws"
  version = "~> 4.4"

  name                   = "lambda-db-proxy"
  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [aws_security_group.lambda_rds_proxy.id]

  engine_family = "POSTGRESQL"

  target_db_cluster     = true
  db_cluster_identifier = module.aurora.cluster_id

  # Enforce IAM authentication proxy-wide (passwordless client access)
  default_auth_scheme = "IAM_AUTH"

  auth = {
    lambda = {
      description = "Lambda database credentials"
      secret_arn  = aws_secretsmanager_secret.lambda_db.arn
      iam_auth    = "REQUIRED"
    }
  }

  # Tuned for Lambda burst/connection-storm traffic
  max_connections_percent      = 90
  max_idle_connections_percent = 50
  connection_borrow_timeout    = 30
  idle_client_timeout          = 900

  require_tls   = true
  debug_logging = false

  tags = {
    Application = "serverless-api"
    Environment = "production"
  }
}
```

## Best Practices

### Connection Pool Configuration

1. **Optimize Connection Limits**: Set `max_connections_percent` based on the database instance connection limit (typically 80-90%)
2. **Configure Idle Connections**: Set `max_idle_connections_percent` around 50% to keep warm connections available for bursts
3. **Tune Borrow Timeout**: Use a 30-120 second `connection_borrow_timeout` matched to application timeout requirements
4. **Minimize Session Pinning**: Use `session_pinning_filters` and avoid operations that pin connections (temp tables, prepared statements, session variables)
5. **Use Init Query Sparingly**: `init_query` runs on every new pooled connection, so keep it minimal to avoid added latency
6. **Monitor Connection Usage**: Track `DatabaseConnectionsCurrentlyInUse` to right-size the pool

### Authentication and Security

1. **Use Secrets Manager**: Always store database credentials in AWS Secrets Manager and reference them via `auth[*].secret_arn`
2. **Enable Automatic Rotation**: Configure Secrets Manager rotation for regular credential updates
3. **Require TLS**: Keep the default `require_tls = true` to enforce encrypted client connections
4. **Scope KMS Access**: Pass `kms_key_arns` explicitly rather than relying on the wildcard fallback so the IAM policy stays least-privilege
5. **Security Group Restrictions**: Allow proxy ingress only from application security groups, and proxy-to-database egress only to the database security group
6. **IAM Auth Has Two Levers**: `default_auth_scheme` (proxy-wide `NONE`/`IAM_AUTH`) and per-entry `auth[*].iam_auth` control IAM database authentication independently — verify both when enabling IAM auth
7. **Underlying DB Constraint**: When using RDS Proxy with IAM auth, the target RDS/Aurora resource itself must use username/password authentication (`iam_database_authentication_enabled = false`) — RDS Proxy cannot connect to a target that has native IAM DB auth enabled

### Endpoint and Network Configuration

1. **Separate Read and Write**: Create distinct read-write and read-only entries in `endpoints` for workload isolation
2. **Read-Only for Scaling**: Set `target_role = "READ_ONLY"` on an endpoint to distribute read traffic across Aurora read replicas
3. **DNS Resolution**: Use the proxy endpoint DNS name (not the underlying instance endpoint) in application connection strings for automatic failover
4. **IPv6/Dual-Stack**: If using `endpoint_network_type = "IPV6"`, the associated subnets must be IPv6-only and `target_connection_network_type` must also be `IPV6`

### Logging and Monitoring

1. **Enable CloudWatch Logs**: Keep `manage_log_group = true` for troubleshooting connection issues
2. **Log Retention Strategy**: Set `log_group_retention_in_days` (7-30 days) to balance cost and diagnostic needs; use `log_group_class = "INFREQUENT_ACCESS"` for cost savings on rarely-read logs
3. **Debug Logging**: Enable `debug_logging` during initial rollout only — disable in production since it can log sensitive SQL statement data
4. **Key Metrics**: `DatabaseConnections`, `ClientConnections`, `QueryDatabaseResponseLatency`, `ClientConnectionsSetupFailedBorrowTimeout` (pool exhaustion)

### Operational Patterns

1. **Conditional Deployment**: Use `create = false` to disable the module cleanly in composed root modules (e.g. per-environment toggles)
2. **Multi-Region Providers**: Set `region` when the module is invoked against a non-default provider region/alias
3. **Existing IAM Role**: Set `create_iam_role = false` and supply `role_arn` to reuse a centrally managed role instead of creating one per proxy
4. **Tag Layering**: Use `proxy_tags`, `iam_role_tags`, and `log_group_tags` for resource-specific tags in addition to the shared `tags` map
5. **Test Failover**: Perform periodic failover tests against Aurora clusters to validate application retry/reconnect behavior

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds-proxy
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds-proxy/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-rds-proxy/tree/master/examples
- **AWS RDS Proxy Documentation**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html
- **Managing RDS Proxy**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-managing.html
- **IAM Database Authentication**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.html
- **Connection Pooling (How It Works)**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.howitworks.html
- **RDS Proxy Best Practices**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-best-practices.html
- **Monitoring RDS Proxy**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-monitoring.html
- **RDS Proxy Pricing**: https://aws.amazon.com/rds/proxy/pricing/
- **Lambda with RDS Proxy**: https://aws.amazon.com/blogs/compute/using-amazon-rds-proxy-with-aws-lambda/
- **Troubleshooting**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-troubleshooting.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Requires Terraform >= 1.5.7 and AWS provider >= 6.28**: earlier provider versions lack `endpoint_network_type`/`target_connection_network_type` support
2. **Engine Family Selection**: Set `engine_family` to `"MYSQL"` or `"POSTGRESQL"` matching the target database — it has no functional default despite the empty-string variable default
3. **Target Type Selection**: Set exactly one of `target_db_cluster = true` OR `target_db_instance = true`, never both
4. **Secrets Manager Setup**: Ensure the referenced secret(s) exist in Secrets Manager before creating the proxy; the module's IAM policy is scoped to the exact `secret_arn` values in `auth`
5. **Default Auth Entry**: If `auth` is left at its default (`{ default = { auth_scheme = "SECRETS" } }`), no `secret_arn` is set — always override `auth` with a real secret ARN
6. **VPC Subnet IDs**: Specify at least two subnet IDs in different availability zones
7. **Security Groups**: Restrict proxy ingress to application security groups; restrict proxy-to-database egress to the database security group
8. **Connection Pool Sizing**: Start with `max_connections_percent = 90` and `max_idle_connections_percent = 50`, then tune from CloudWatch metrics
9. **TLS Requirement**: Default `require_tls = true` is secure; only disable if a legacy client cannot support TLS
10. **IAM Role Reuse**: The module auto-creates an IAM role by default; set `create_iam_role = false` and pass `role_arn` to reuse an existing role
11. **KMS Key Access**: Pass `kms_key_arns` explicitly when secrets are encrypted with customer-managed keys, to keep the generated IAM policy least-privilege
12. **Multiple Endpoints**: Add read-only entries to `endpoints` (with `target_role = "READ_ONLY"`) for Aurora clusters with read replicas
13. **IAM DB Auth Prerequisite**: If enabling `default_auth_scheme = "IAM_AUTH"` or `auth[*].iam_auth`, the target RDS/Aurora resource must have `iam_database_authentication_enabled = false` (native IAM DB auth is incompatible with RDS Proxy IAM auth)
14. **IPv6 Consistency**: If setting `endpoint_network_type = "IPV6"`, also set `target_connection_network_type = "IPV6"` and ensure subnets are IPv6-capable
15. **Testing**: Validate connectivity through the proxy endpoint (not the raw DB endpoint) after deployment, before switching application traffic
