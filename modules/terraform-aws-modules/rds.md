# Terraform AWS RDS Module

## Module Information

- **Module Name**: `rds`
- **Source**: `terraform-aws-modules/rds/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest
- **Latest Version**: 7.1.0
- **Purpose**: Creates and manages AWS RDS database instances with comprehensive configuration for storage, networking, security, monitoring, and high availability
- **Service**: AWS RDS (Amazon Relational Database Service)
- **Category**: Database, Managed Services
- **Keywords**: rds, database, mysql, postgresql, oracle, mssql, mariadb, multi-az, read-replica, backup, encryption, performance-insights, parameter-group, option-group, subnet-group, blue-green-deployment
- **Use For**: Production relational databases, application backends, database migration to cloud, read-heavy workloads with replicas, high-availability database systems, disaster recovery setups, cross-region replication

## Description

This Terraform module provides a comprehensive solution for deploying and managing Amazon RDS database instances. It supports multiple database engines including MySQL, PostgreSQL, MariaDB, Oracle, and Microsoft SQL Server. The module abstracts RDS configuration complexity while providing extensive customization for storage, networking, security, monitoring, and high availability through specialized submodules.

The module supports deployment scenarios from simple single-instance databases to complex multi-AZ configurations with read replicas, cross-region replication, and blue-green deployments. It handles automated backups with configurable retention, point-in-time recovery, encryption at rest using AWS KMS, enhanced monitoring with CloudWatch integration, and Performance Insights for query diagnostics. Storage autoscaling, IAM database authentication, and Secrets Manager integration are also supported.

**Important**: Security groups must be managed separately using the `terraform-aws-security-group` module. The `password` variable is deprecated in v7.0.0+; use `password_wo` and `password_wo_version` instead.

## Key Features

- **Multiple Database Engines**: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server with configurable versions
- **Storage Options**: GP2, GP3, IO1, IO2 with configurable IOPS and storage autoscaling
- **Multi-AZ Deployments**: High availability with automatic failover across availability zones
- **Read Replicas**: Support for read replicas with cross-region replication
- **Blue-Green Deployments**: Zero-downtime updates using AWS blue-green deployment strategy
- **Automated Backups**: Configurable retention (0-35 days) with cross-region replication
- **Storage Encryption**: Encryption at rest using AWS KMS (customer-managed or AWS-managed keys)
- **Enhanced Monitoring**: CloudWatch monitoring at 1-60 second intervals for OS-level metrics
- **Performance Insights**: Advanced database performance monitoring with query-level diagnostics
- **IAM Database Authentication**: Token-based authentication using AWS IAM credentials
- **CloudWatch Log Exports**: Export database logs (error, slow query, general, audit)
- **Conditional Resource Creation**: Flexible flags to enable/disable individual resources

## Main Use Cases

1. **Production Databases**: Highly available, managed relational databases for applications
2. **Database Migration**: Moving on-premises databases to AWS
3. **Read-Heavy Workloads**: Primary database with read replicas to distribute traffic
4. **High-Availability Systems**: Multi-AZ deployments with automatic failover
5. **Disaster Recovery**: Cross-region backups and read replicas for business continuity
6. **Development/Testing**: Isolated database instances for non-production environments
7. **Zero-Downtime Updates**: Blue-green deployments for database upgrades

## Submodules

### 1. db_instance

- **Purpose**: Creates and manages AWS RDS database instances with full lifecycle management
- **Source**: `terraform-aws-modules/rds/aws//modules/db_instance`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_instance
- **Key Features**: Instance lifecycle, storage configuration, encryption, monitoring, backup management
- **Use Cases**: Production databases, application backends, read replicas

### 2. db_subnet_group

- **Purpose**: Creates DB subnet groups defining where RDS instances can be deployed in VPC
- **Source**: `terraform-aws-modules/rds/aws//modules/db_subnet_group`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_subnet_group
- **Key Features**: Subnet group creation, VPC integration, multi-AZ subnet configuration
- **Use Cases**: Network isolation, multi-AZ deployments, VPC database placement

### 3. db_parameter_group

- **Purpose**: Creates RDS parameter groups for database engine parameter customization
- **Source**: `terraform-aws-modules/rds/aws//modules/db_parameter_group`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_parameter_group
- **Key Features**: Engine parameter customization, parameter family support, dynamic modification
- **Use Cases**: Performance tuning, character set configuration, connection limits

### 4. db_option_group

- **Purpose**: Creates RDS option groups for additional database features (Oracle, SQL Server)
- **Source**: `terraform-aws-modules/rds/aws//modules/db_option_group`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_option_group
- **Key Features**: Engine-specific options, version-specific configuration, port configuration
- **Use Cases**: Oracle advanced features, SQL Server audit logs, transparent data encryption

### 5. db_instance_role_association

- **Purpose**: Associates IAM roles with RDS instances for AWS service integration
- **Source**: `terraform-aws-modules/rds/aws//modules/db_instance_role_association`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_instance_role_association
- **Key Features**: IAM role association, S3 integration, Lambda integration
- **Use Cases**: S3 import/export, Lambda function invocation, cross-service integration

### 6. db_instance_automated_backups_replication

- **Purpose**: Replicates automated backups to a different AWS region for disaster recovery
- **Source**: `terraform-aws-modules/rds/aws//modules/db_instance_automated_backups_replication`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_instance_automated_backups_replication
- **Key Features**: Cross-region backup replication, KMS encryption, configurable retention
- **Use Cases**: Disaster recovery, cross-region data protection, compliance requirements

## Usage Examples

### Basic PostgreSQL Instance

```hcl
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 7.0"

  identifier = "my-postgres-db"

  engine               = "postgres"
  engine_version       = "16.4"
  family               = "postgres16"
  major_engine_version = "16"
  instance_class       = "db.t4g.medium"

  allocated_storage     = 20
  max_allocated_storage = 100

  db_name  = "myapp"
  username = "dbadmin"
  port     = 5432

  # Use write-only password (v7.0.0+)
  manage_master_user_password = true

  multi_az               = false
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.security_group.security_group_id]

  maintenance_window      = "Mon:00:00-Mon:03:00"
  backup_window           = "03:00-06:00"
  backup_retention_period = 7

  tags = {
    Environment = "dev"
  }
}
```

### Production Multi-AZ with Monitoring

```hcl
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 7.0"

  identifier = "prod-postgres-db"

  engine               = "postgres"
  engine_version       = "16.4"
  family               = "postgres16"
  major_engine_version = "16"
  instance_class       = "db.r6g.xlarge"

  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  db_name  = "production"
  username = "dbadmin"
  port     = 5432

  manage_master_user_password = true

  # High availability
  multi_az = true

  # Network
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.security_group.security_group_id]
  publicly_accessible    = false

  # Backup
  backup_retention_period = 30
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"
  skip_final_snapshot     = false
  deletion_protection     = true

  # Monitoring
  monitoring_interval                   = 60
  monitoring_role_name                  = "rds-monitoring-role"
  create_monitoring_role                = true
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  enabled_cloudwatch_logs_exports       = ["postgresql", "upgrade"]

  # Parameter group
  parameters = [
    {
      name  = "max_connections"
      value = "200"
    },
    {
      name  = "shared_buffers"
      value = "{DBInstanceClassMemory/4}"
    }
  ]

  tags = {
    Environment = "production"
    Application = "web-app"
  }
}
```

### MySQL with Read Replica

```hcl
# Primary instance
module "master" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 7.0"

  identifier = "mysql-master"

  engine               = "mysql"
  engine_version       = "8.0"
  family               = "mysql8.0"
  major_engine_version = "8.0"
  instance_class       = "db.r6g.large"

  allocated_storage     = 50
  max_allocated_storage = 500
  storage_encrypted     = true

  db_name  = "myapp"
  username = "admin"
  port     = 3306

  manage_master_user_password = true

  multi_az               = true
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.security_group.security_group_id]

  backup_retention_period = 14

  tags = {
    Environment = "production"
  }
}

# Read replica
module "replica" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 7.0"

  identifier = "mysql-replica"

  replicate_source_db = module.master.db_instance_identifier

  engine               = "mysql"
  engine_version       = "8.0"
  family               = "mysql8.0"
  major_engine_version = "8.0"
  instance_class       = "db.r6g.large"

  allocated_storage     = 50
  max_allocated_storage = 500
  storage_encrypted     = true

  multi_az               = false
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.security_group.security_group_id]

  backup_retention_period = 0
  skip_final_snapshot     = true

  tags = {
    Environment = "production"
    Role        = "replica"
  }
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `identifier` | `string` | - | Unique identifier for the RDS instance |
| `engine` | `string` | - | Database engine (mysql, postgres, oracle-ee, sqlserver-ex, etc.) |
| `engine_version` | `string` | - | Database engine version |
| `instance_class` | `string` | - | RDS instance type (db.t3.micro, db.m5.large, etc.) |
| `allocated_storage` | `number` | - | Initial storage allocation in GB |
| `max_allocated_storage` | `number` | `0` | Maximum storage for autoscaling (0 disables) |
| `storage_type` | `string` | `"gp3"` | Storage type (gp2, gp3, io1, io2) |
| `storage_encrypted` | `bool` | `true` | Enable storage encryption |
| `kms_key_id` | `string` | `null` | KMS key ARN for encryption |
| `db_name` | `string` | `null` | Initial database name |
| `username` | `string` | - | Master username |
| `manage_master_user_password` | `bool` | `true` | Use Secrets Manager for password |
| `password_wo` | `string` | `null` | Write-only password (v7.0.0+) |
| `multi_az` | `bool` | `false` | Enable Multi-AZ deployment |
| `db_subnet_group_name` | `string` | `null` | Subnet group name |
| `vpc_security_group_ids` | `list(string)` | `[]` | Security group IDs |
| `publicly_accessible` | `bool` | `false` | Allow public access |
| `backup_retention_period` | `number` | `null` | Backup retention days (0-35) |
| `backup_window` | `string` | `null` | Daily backup window (UTC) |
| `maintenance_window` | `string` | `null` | Weekly maintenance window (UTC) |
| `monitoring_interval` | `number` | `0` | Enhanced monitoring interval (0, 1, 5, 10, 15, 30, 60) |
| `performance_insights_enabled` | `bool` | `false` | Enable Performance Insights |
| `deletion_protection` | `bool` | `false` | Prevent accidental deletion |
| `skip_final_snapshot` | `bool` | `false` | Skip final snapshot on deletion |
| `copy_tags_to_snapshot` | `bool` | `true` | Copy tags to snapshots (default changed in v7.0.0) |
| `create_db_instance` | `bool` | `true` | Create the DB instance |
| `create_db_subnet_group` | `bool` | `true` | Create subnet group |
| `create_db_parameter_group` | `bool` | `true` | Create parameter group |
| `create_db_option_group` | `bool` | `true` | Create option group |

## Main Outputs

| Output | Description |
|--------|-------------|
| `db_instance_endpoint` | Connection endpoint (hostname:port) |
| `db_instance_address` | Hostname of the RDS instance |
| `db_instance_port` | Database port number |
| `db_instance_identifier` | Unique identifier |
| `db_instance_arn` | ARN of the instance |
| `db_instance_username` | Master username |
| `db_instance_master_user_secret_arn` | Secrets Manager secret ARN (when managed) |
| `db_instance_availability_zone` | Availability zone |
| `db_instance_engine` | Database engine |
| `db_instance_engine_version_actual` | Running engine version |
| `db_subnet_group_id` | Subnet group ID |
| `db_parameter_group_id` | Parameter group ID |
| `db_option_group_id` | Option group ID |

## Best Practices

### Security

1. **Enable encryption**: Always set `storage_encrypted = true` with customer-managed KMS keys for production
2. **Network isolation**: Deploy in private subnets, use restrictive security groups
3. **Use IAM authentication**: Enable `iam_database_authentication_enabled` when supported
4. **Managed passwords**: Use `manage_master_user_password = true` for Secrets Manager integration
5. **Disable public access**: Keep `publicly_accessible = false` for production
6. **Enable deletion protection**: Set `deletion_protection = true` for production databases

### High Availability

1. **Enable Multi-AZ**: Set `multi_az = true` for production workloads
2. **Use read replicas**: Distribute read traffic and provide failover options
3. **Cross-region backups**: Use `db_instance_automated_backups_replication` submodule for DR
4. **Configure subnet groups**: Span at least 2 availability zones

### Backup & Recovery

1. **Set retention period**: Use 7-35 days based on RPO requirements
2. **Configure backup windows**: Schedule during low-activity periods
3. **Don't skip final snapshots**: Keep `skip_final_snapshot = false` for production
4. **Test recovery**: Regularly verify backup restoration procedures

### Performance

1. **Enable Performance Insights**: Set `performance_insights_enabled = true`
2. **Configure enhanced monitoring**: Use `monitoring_interval = 60` for production
3. **Tune parameters**: Create custom parameter groups for workload optimization
4. **Enable storage autoscaling**: Set `max_allocated_storage` to prevent out-of-space issues
5. **Use GP3 storage**: Better price/performance than GP2 with independent IOPS configuration

### Cost Optimization

1. **Right-size instances**: Start small and scale based on metrics
2. **Use reserved instances**: For predictable production workloads
3. **Stop dev instances**: Automate stopping non-production databases
4. **Clean up snapshots**: Implement lifecycle policies for manual snapshots

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-rds/tree/master/examples
- **AWS RDS User Guide**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/
- **AWS RDS Best Practices**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html
- **RDS Performance Insights**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.html
- **RDS Pricing**: https://aws.amazon.com/rds/pricing/

## Notes for AI Agents

When using this module:

1. **Version**: Use `version = "~> 7.0"` for latest features
2. **Password handling**: Use `manage_master_user_password = true` instead of plaintext passwords
3. **Security groups**: Create separately using `terraform-aws-security-group` module
4. **GP3 storage**: Note IOPS/throughput minimums depend on allocated storage and engine
5. **Multi-AZ**: Always enable for production workloads
6. **Encryption**: Always enable with KMS for sensitive data
7. **Monitoring**: Enable Performance Insights and enhanced monitoring for production
8. **Backups**: Configure appropriate retention (7+ days for production)
9. **Deletion protection**: Enable for production to prevent accidents
10. **Subnet groups**: Ensure subnets span multiple AZs for high availability
