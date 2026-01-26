# Terraform AWS RDS Proxy Module

## Module Information

- **Module Name**: `rds-proxy`
- **Source**: `terraform-aws-modules/rds-proxy/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds-proxy
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds-proxy/aws/latest
- **Latest Version**: 4.4.0
- **Purpose**: Terraform module that creates and manages AWS RDS Proxy resources for efficient database connection pooling and management
- **Service**: AWS RDS Proxy (Amazon RDS Proxy)
- **Category**: Database, Connection Management, Scalability
- **Keywords**: rds-proxy, connection-pooling, database-proxy, aurora, mysql, postgresql, secrets-manager, iam-authentication, serverless-database, lambda-rds, high-availability, connection-management, database-scaling, tls-encryption, cloudwatch-logs
- **Use For**: Lambda database connections, serverless application databases, connection pooling for microservices, containerized application databases, high-traffic database access, unpredictable database workloads, database failover automation, credential rotation without downtime, ECS/Fargate database connections, Kubernetes database access, connection storm prevention, database CPU optimization

## Description

AWS RDS Proxy is a fully managed database proxy service that sits between applications and relational databases, providing intelligent connection pooling, credential management, and enhanced database resilience. This Terraform module simplifies the deployment and configuration of RDS Proxy resources, including the proxy itself, authentication configurations, target groups, IAM roles and policies, CloudWatch log groups, and multiple proxy endpoints. The module supports both MySQL and PostgreSQL engine families and works seamlessly with Amazon RDS databases and Aurora clusters, enabling applications to efficiently share and reuse database connections rather than opening new connections for every request.

The module addresses critical challenges in modern application architectures, particularly for serverless and containerized workloads where applications can quickly open thousands of database connections, overwhelming database resources and causing performance degradation. By pooling and reusing connections, RDS Proxy significantly reduces the CPU and memory overhead associated with connection establishment, allowing databases to dedicate more resources to processing queries. The proxy automatically handles authentication using credentials stored in AWS Secrets Manager, supports IAM database authentication for enhanced security, and maintains connections to standby database instances, providing automatic failover capabilities without application code changes.

Built for production environments, the module provides comprehensive configuration options including connection borrow timeouts, maximum and idle connection percentages, session pinning filters for connection-sensitive operations, and TLS encryption enforcement for all connections. It supports multiple proxy endpoints (read-write and read-only) for separating workload types, integrates with CloudWatch for logging and monitoring, and enables fine-grained IAM permissions for proxy management and database access.

## Key Features

- **Connection Pooling**: Efficiently pool and reuse database connections to reduce CPU and memory overhead
- **MySQL and PostgreSQL Support**: Full support for both MySQL and PostgreSQL engine families
- **Aurora and RDS Compatibility**: Works with Aurora clusters and standalone RDS instances
- **AWS Secrets Manager Integration**: Automatically retrieves database credentials from Secrets Manager
- **IAM Database Authentication**: Support for IAM-based database authentication for passwordless access
- **Multiple Authentication Methods**: Configure multiple authentication schemes for different database users
- **Read-Write Endpoints**: Create read-write proxy endpoints for write operations and failover scenarios
- **Read-Only Endpoints**: Establish read-only endpoints for distributing read traffic across read replicas
- **Connection Throttling**: Queue or throttle application connections when connection pool is full
- **Automatic Failover**: Seamlessly redirect connections to standby instances during database failures
- **Session Pinning Prevention**: Configure filters to avoid connection pinning that reduces pooling efficiency
- **TLS Encryption Required**: Enforce TLS encryption for all client connections to the proxy (enabled by default)
- **Configurable Connection Timeouts**: Set connection borrow timeout to control how long clients wait for connections
- **Connection Limit Controls**: Configure maximum and idle connection percentages for optimal resource utilization
- **CloudWatch Logs Integration**: Send proxy logs to CloudWatch for monitoring and troubleshooting
- **Debug Logging**: Optional SQL statement logging for detailed debugging
- **IAM Role Automation**: Automatically create and configure IAM roles with appropriate permissions
- **VPC Subnet Configuration**: Deploy proxy in specific VPC subnets across availability zones
- **Security Group Management**: Configure security groups to control network access to the proxy
- **Resource Tagging**: Comprehensive tagging support for all created resources

## Main Use Cases

1. **Serverless Database Connections**: Optimize database connections for AWS Lambda functions that frequently scale up and down
2. **Containerized Applications**: Manage database connections for ECS, Fargate, and Kubernetes workloads with unpredictable scaling
3. **Microservices Architecture**: Provide efficient connection pooling for dozens of microservices accessing shared databases
4. **Connection Storm Prevention**: Prevent database overload during traffic spikes by throttling and queuing connections
5. **High-Availability Applications**: Automatically handle database failovers without application code changes
6. **Credential Rotation**: Rotate database credentials using Secrets Manager without application downtime
7. **Multi-Tenant Applications**: Share connection pools across tenants while maintaining authentication boundaries
8. **Database Performance Optimization**: Reduce database CPU and memory usage by minimizing connection overhead
9. **IAM-Authenticated Access**: Enable passwordless database access using IAM authentication for enhanced security
10. **Read Workload Distribution**: Distribute read queries across Aurora read replicas using read-only endpoints

## Submodules

This module has **no submodules**. It is a standalone module that creates all RDS Proxy resources directly.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | - | Proxy identifier (must begin with letter, alphanumeric/hyphens only) |
| `engine_family` | `string` | - | Database engine type: `"MYSQL"` or `"POSTGRESQL"` |
| `vpc_subnet_ids` | `list(string)` | `[]` | VPC subnet IDs for proxy deployment |
| `vpc_security_group_ids` | `list(string)` | `[]` | Security groups for the proxy |
| `auth` | `map(object)` | `{}` | Authentication config (auth_scheme, iam_auth, secret_arn) |
| `target_db_cluster` | `bool` | `false` | Set to `true` to target Aurora cluster |
| `target_db_instance` | `bool` | `false` | Set to `true` to target RDS instance |
| `db_cluster_identifier` | `string` | `""` | Target Aurora cluster identifier |
| `db_instance_identifier` | `string` | `""` | Target RDS instance identifier |
| `require_tls` | `bool` | `true` | Enforce TLS encryption for proxy connections |
| `max_connections_percent` | `number` | `90` | Maximum connection pool size percentage |
| `max_idle_connections_percent` | `number` | `50` | Idle connection threshold percentage |
| `idle_client_timeout` | `number` | `1800` | Seconds before idle connections disconnect |
| `connection_borrow_timeout` | `number` | `null` | Seconds to wait for available connection |
| `debug_logging` | `bool` | `false` | Enable SQL statement logging to CloudWatch |
| `endpoints` | `map(object)` | `{}` | Additional proxy endpoints configuration |
| `create_iam_role` | `bool` | `true` | Create IAM role for Secrets Manager access |
| `role_arn` | `string` | `""` | External IAM role ARN (if not creating) |
| `kms_key_arns` | `list(string)` | `[]` | KMS key ARNs for secret decryption |
| `manage_log_group` | `bool` | `true` | Create CloudWatch log group |
| `log_group_retention_in_days` | `number` | `30` | CloudWatch log retention period |
| `tags` | `map(string)` | `{}` | Tags for all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `proxy_id` | The ID of the proxy |
| `proxy_arn` | The ARN of the proxy |
| `proxy_endpoint` | Primary proxy endpoint for database connections |
| `proxy_default_target_group_id` | The ID of the default target group |
| `proxy_default_target_group_arn` | The ARN of the default target group |
| `proxy_target_endpoint` | Hostname for target RDS instance |
| `proxy_target_port` | Port for target database |
| `db_proxy_endpoints` | All configured DB proxy endpoints |
| `log_group_arn` | CloudWatch log group ARN |
| `log_group_name` | CloudWatch log group name |
| `iam_role_arn` | IAM role ARN for proxy |
| `iam_role_name` | IAM role name |

## Usage Examples

### MySQL Aurora Cluster with IAM Authentication

```hcl
module "rds_proxy" {
  source  = "terraform-aws-modules/rds-proxy/aws"
  version = "~> 4.4"

  name                   = "mysql-proxy"
  engine_family          = "MYSQL"
  vpc_subnet_ids         = module.vpc.database_subnets
  vpc_security_group_ids = [aws_security_group.rds_proxy.id]

  # Target Aurora cluster
  target_db_cluster     = true
  db_cluster_identifier = module.aurora.cluster_id

  # Authentication via Secrets Manager
  auth = {
    "cluster" = {
      auth_scheme = "SECRETS"
      description = "Cluster master user credentials"
      iam_auth    = "REQUIRED"
      secret_arn  = module.aurora.cluster_master_user_secret[0].secret_arn
    }
  }

  # Multiple endpoints for read/write separation
  endpoints = {
    read_write = {
      name                   = "read-write-endpoint"
      vpc_subnet_ids         = module.vpc.database_subnets
      vpc_security_group_ids = [aws_security_group.rds_proxy.id]
      tags                   = { Name = "rds-proxy-read-write-endpoint" }
    }
    read_only = {
      name                   = "read-only-endpoint"
      vpc_subnet_ids         = module.vpc.database_subnets
      vpc_security_group_ids = [aws_security_group.rds_proxy.id]
      target_role            = "READ_ONLY"
      tags                   = { Name = "rds-proxy-read-only-endpoint" }
    }
  }

  # KMS keys for Secrets Manager decryption
  kms_key_arns = [module.kms.key_arn]

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}
```

### PostgreSQL RDS Instance with Connection Pool Tuning

```hcl
module "rds_proxy" {
  source  = "terraform-aws-modules/rds-proxy/aws"
  version = "~> 4.4"

  name                   = "postgresql-proxy"
  engine_family          = "POSTGRESQL"
  vpc_subnet_ids         = module.vpc.database_subnets
  vpc_security_group_ids = [aws_security_group.rds_proxy.id]

  # Target RDS instance
  target_db_instance     = true
  db_instance_identifier = module.db.db_instance_identifier

  # Authentication via Secrets Manager
  auth = {
    "instance" = {
      auth_scheme = "SECRETS"
      description = "RDS instance credentials"
      iam_auth    = "REQUIRED"
      secret_arn  = aws_secretsmanager_secret.db_credentials.arn
    }
  }

  # Connection pool configuration
  max_connections_percent      = 80
  max_idle_connections_percent = 40
  idle_client_timeout          = 3600

  # CloudWatch logging
  log_group_retention_in_days = 7
  debug_logging               = true

  tags = {
    Environment = "development"
  }
}
```

### Lambda-Optimized Configuration

```hcl
module "rds_proxy" {
  source  = "terraform-aws-modules/rds-proxy/aws"
  version = "~> 4.4"

  name                   = "lambda-db-proxy"
  engine_family          = "POSTGRESQL"
  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [aws_security_group.lambda_rds_proxy.id]

  target_db_cluster     = true
  db_cluster_identifier = module.aurora.cluster_id

  auth = {
    "lambda" = {
      auth_scheme = "SECRETS"
      description = "Lambda database credentials"
      iam_auth    = "REQUIRED"
      secret_arn  = aws_secretsmanager_secret.lambda_db.arn
    }
  }

  # Optimized for Lambda burst traffic
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

1. **Optimize Connection Limits**: Set `max_connections_percent` based on database instance connection limits (typically 80-90%)
2. **Configure Idle Connections**: Set `max_idle_connections_percent` to 50% to maintain warm connections for bursts
3. **Tune Borrow Timeout**: Use 30-120 second `connection_borrow_timeout` based on application timeout requirements
4. **Minimize Session Pinning**: Avoid operations that pin connections (temp tables, prepared statements, session variables)
5. **Monitor Connection Usage**: Track `DatabaseConnectionsCurrentlyInUse` metric to optimize pool sizing

### Authentication and Security

1. **Use Secrets Manager**: Always store database credentials in AWS Secrets Manager for secure credential management
2. **Enable Automatic Rotation**: Configure Secrets Manager secret rotation for regular credential updates
3. **Require TLS**: Always set `require_tls = true` to enforce encrypted connections (default)
4. **KMS Encryption**: Use customer-managed KMS keys for encrypting Secrets Manager secrets
5. **Security Group Restrictions**: Configure security groups to allow proxy access only from application security groups
6. **IAM Authentication Note**: When using RDS Proxy with IAM auth, the underlying database must use username/password authentication - this is an AWS limitation

### Endpoint Configuration

1. **Separate Read and Write**: Create separate read-write and read-only endpoints for workload isolation
2. **Read-Only for Scaling**: Use read-only endpoints to distribute read traffic across Aurora read replicas
3. **Endpoint Naming**: Use descriptive endpoint names indicating purpose (e.g., "app-db-write", "app-db-read")
4. **DNS Resolution**: Use proxy endpoint DNS names in application connection strings for automatic failover

### Performance and Optimization

1. **Maximize Connection Reuse**: Design applications to close connections quickly to return them to the pool
2. **Avoid Long Transactions**: Keep transactions short to prevent connection holding
3. **Monitor Pinning**: Track `ClientConnectionsSetupFailedBorrowTimeout` to identify session pinning issues
4. **Reduce Connection Overhead**: Expect 20-40% database CPU improvement after enabling proxy
5. **Minimal Latency Overhead**: Proxy adds typically <5ms latency

### Logging and Monitoring

1. **Enable CloudWatch Logs**: Always enable logging for troubleshooting connection issues
2. **Log Retention Strategy**: Set appropriate retention periods (7-30 days) to balance cost and needs
3. **Debug Logging**: Enable during initial deployment, disable in production to avoid logging sensitive data
4. **Key Metrics**:
   - `DatabaseConnections`: Total proxy-to-database connections
   - `ClientConnections`: Application connections to proxy
   - `QueryDatabaseResponseLatency`: Query response time
   - `ClientConnectionsSetupFailedBorrowTimeout`: Pool exhaustion failures

### High Availability

1. **Multi-AZ Deployment**: RDS Proxy automatically deploys across multiple AZs
2. **Aurora for Best HA**: Use Aurora clusters for fastest failover times (30-60 seconds)
3. **Test Failover**: Perform quarterly failover tests to validate application behavior
4. **Connection Retry Logic**: Implement exponential backoff retry in applications

### Application Integration

1. **Disable App-Level Pooling**: Minimize application-level connection pooling when using RDS Proxy
2. **Lambda Best Practices**: Set Lambda timeout accounting for connection borrow timeout
3. **Framework Configuration**: Configure ORMs to work efficiently with proxy
4. **Health Check Endpoints**: Implement health checks that validate proxy connectivity

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds-proxy
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds-proxy/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-rds-proxy/tree/master/examples
- **AWS RDS Proxy Documentation**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html
- **Managing RDS Proxy**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-managing.html
- **Secrets Manager Integration**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-setup.html
- **IAM Database Authentication**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.html
- **Connection Pooling**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.howitworks.html
- **Best Practices**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-best-practices.html
- **Monitoring RDS Proxy**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-monitoring.html
- **RDS Proxy Pricing**: https://aws.amazon.com/rds/proxy/pricing/
- **Lambda with RDS Proxy**: https://aws.amazon.com/blogs/compute/using-amazon-rds-proxy-with-aws-lambda/
- **Troubleshooting**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-troubleshooting.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Engine Family Selection**: Set `engine_family` to `"MYSQL"` or `"POSTGRESQL"` matching your database
2. **Target Type Selection**: Set exactly one of `target_db_cluster = true` OR `target_db_instance = true`
3. **Secrets Manager Setup**: Ensure database credentials exist in Secrets Manager before creating proxy
4. **Secret ARN Format**: Provide complete secret ARN in authentication configuration
5. **VPC Subnet IDs**: Specify at least two subnet IDs in different availability zones
6. **Security Groups**: Create security groups allowing proxy access from application security groups
7. **Connection Pool Sizing**: Start with `max_connections_percent = 90` and `max_idle_connections_percent = 50`
8. **TLS Requirement**: Default `require_tls = true` is secure; disable only if necessary
9. **IAM Role Creation**: Module automatically creates IAM role; provide `role_arn` if using existing
10. **KMS Key Access**: If using customer-managed KMS keys, specify in `kms_key_arns`
11. **Multiple Endpoints**: Create read-only endpoints for Aurora clusters with read replicas
12. **Tagging Strategy**: Apply comprehensive tags for environment, application, and database identification
13. **Testing**: Validate connectivity through proxy after deployment before switching application traffic
