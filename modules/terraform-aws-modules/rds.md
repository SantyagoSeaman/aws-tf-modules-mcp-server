---
module_name: rds
keywords: [rds, relational-database, database, db-instance, mysql, postgresql, postgres, oracle, mssql, sql-server, mariadb, aurora, db-subnet-group, db-parameter-group, db-option-group, subnet-group, parameter-group, option-group, database-instance, managed-database, cloud-database, db-engine, multi-az, high-availability, backup, snapshot, automated-backup, point-in-time-recovery, storage-encryption, kms, encryption, replica, read-replica, cross-region, replication, blue-green-deployment, enhanced-monitoring, performance-insights, cloudwatch, monitoring, iam-authentication, iam-role, security-group, vpc, storage-autoscaling, storage-type, gp2, gp3, io1, iops, provisioned-iops, maintenance-window, backup-window, s3-import, role-association, automated-backups-replication, deletion-protection, final-snapshot, engine-version, instance-class, allocated-storage, db-name, master-username, master-password, secrets-manager, license-model, character-set, timezone, ca-certificate, ssl, tls]
---

# Terraform AWS RDS Module

## Module Information

- **Module Name**: `rds`
- **Source**: `terraform-aws-modules/rds/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest
- **Latest Version**: 6.13.0
- **Purpose**: Terraform module for creating and managing AWS RDS (Relational Database Service) instances with comprehensive configuration options
- **Service**: AWS RDS (Amazon Relational Database Service)
- **Category**: Database, Managed Services, Cloud Infrastructure
- **Keywords**: rds, relational-database, database, db-instance, mysql, postgresql, postgres, oracle, mssql, sql-server, mariadb, aurora, db-subnet-group, db-parameter-group, db-option-group, subnet-group, parameter-group, option-group, database-instance, managed-database, cloud-database, db-engine, multi-az, high-availability, backup, snapshot, automated-backup, point-in-time-recovery, storage-encryption, kms, encryption, replica, read-replica, cross-region, replication, blue-green-deployment, enhanced-monitoring, performance-insights, cloudwatch, monitoring, iam-authentication, iam-role, security-group, vpc, storage-autoscaling, storage-type, gp2, gp3, io1, iops, provisioned-iops, maintenance-window, backup-window, s3-import, role-association, automated-backups-replication, deletion-protection, final-snapshot, engine-version, instance-class, allocated-storage, db-name, master-username, master-password, secrets-manager, license-model, character-set, timezone, ca-certificate, ssl, tls
- **Use For**: Production relational databases, application backend databases, multi-tier application data layer, microservices data persistence, database migration from on-premises to cloud, read-heavy workloads with read replicas, high-availability database systems, disaster recovery database setups, cross-region database replication, development and testing environments, data warehousing and analytics databases, legacy application database hosting

## Description

This Terraform module provides a comprehensive solution for deploying and managing Amazon RDS database instances on AWS. Amazon RDS is a fully managed relational database service that supports multiple database engines including MySQL, PostgreSQL, MariaDB, Oracle, and Microsoft SQL Server. The module abstracts the complexity of RDS instance configuration while providing extensive customization options for storage, networking, security, monitoring, and high availability. It includes specialized submodules for managing database subnet groups, parameter groups, option groups, and IAM role associations, enabling modular and reusable infrastructure patterns.

The module supports a wide range of deployment scenarios from simple single-instance databases to complex multi-AZ configurations with read replicas, cross-region replication, and blue-green deployments. It handles critical operational concerns including automated backups with configurable retention periods, point-in-time recovery, encryption at rest using AWS KMS, enhanced monitoring with CloudWatch integration, and Performance Insights for query-level diagnostics. The module also supports advanced features like storage autoscaling, IAM database authentication, S3 data import, and integration with AWS Secrets Manager for secure credential management.

Built with production readiness and operational excellence in mind, this module enables teams to deploy enterprise-grade database infrastructure using Infrastructure as Code principles. It provides fine-grained control over database parameters, storage types (standard, GP2, GP3, IO1), instance sizing, maintenance windows, and backup schedules. The module follows Terraform best practices with conditional resource creation, comprehensive outputs for integration with other resources, and clear separation of concerns through its submodule architecture. Whether deploying a simple development database or a complex multi-region production system, this module provides the flexibility and reliability required for modern cloud-native applications.

## Key Features

- **Multiple Database Engines**: Support for MySQL, PostgreSQL, MariaDB, Oracle, and Microsoft SQL Server with configurable versions
- **Database Instance Management**: Complete lifecycle management of RDS instances with customizable configurations
- **Storage Options**: Multiple storage types including GP2, GP3, IO1 with configurable IOPS and storage autoscaling
- **Multi-AZ Deployments**: High availability configuration with automatic failover across availability zones
- **Read Replicas**: Support for read replicas with cross-region replication capabilities
- **Blue-Green Deployments**: Zero-downtime updates using blue-green deployment strategy
- **Automated Backups**: Configurable automated backups with retention periods and backup windows
- **Point-in-Time Recovery**: Restore database to any point within the backup retention period
- **Snapshot Management**: Manual and automated snapshot creation with cross-region copy capabilities
- **Storage Encryption**: Encryption at rest using AWS KMS with customer-managed or AWS-managed keys
- **Enhanced Monitoring**: Detailed CloudWatch monitoring at 1-60 second intervals for OS-level metrics
- **Performance Insights**: Advanced database performance monitoring with query-level diagnostics
- **CloudWatch Log Exports**: Export database logs (error, slow query, general, audit) to CloudWatch
- **IAM Database Authentication**: Token-based authentication using AWS IAM credentials
- **Secrets Manager Integration**: Automatic credential management using AWS Secrets Manager
- **S3 Import**: Direct data import from Amazon S3 during database restoration
- **DB Subnet Groups**: Custom subnet group configuration for VPC networking via dedicated submodule
- **DB Parameter Groups**: Database engine parameter customization via dedicated submodule
- **DB Option Groups**: Additional database feature configuration via dedicated submodule
- **IAM Role Association**: Associate IAM roles with database instances for AWS service integration
- **Deletion Protection**: Prevent accidental deletion of production databases
- **Custom Maintenance Windows**: Configure maintenance and backup windows to minimize impact
- **Security Group Integration**: Network access control using VPC security groups
- **Tagging Support**: Comprehensive resource tagging for cost allocation and resource management
- **Conditional Resource Creation**: Flexible module configuration with create flags for all resources

## Main Use Cases

1. **Production Application Databases**: Highly available, managed relational databases for web and mobile applications
2. **Microservices Data Layer**: Individual RDS instances for service-specific data isolation and management
3. **Database Migration**: Moving on-premises Oracle, SQL Server, MySQL, or PostgreSQL databases to AWS
4. **Read-Heavy Workloads**: Primary database with read replicas to distribute read traffic and improve performance
5. **High-Availability Systems**: Multi-AZ deployments with automatic failover for business-critical applications
6. **Disaster Recovery**: Cross-region read replicas and automated backups for business continuity
7. **Development and Testing**: Isolated database instances for development, staging, and testing environments
8. **Analytics and Reporting**: Dedicated read replicas for analytics queries without impacting production workloads
9. **Legacy Application Hosting**: Managed databases for legacy applications requiring specific engine versions
10. **Zero-Downtime Updates**: Blue-green deployments for database upgrades without application downtime

## Submodules

### 1. db_instance

- **Purpose**: Creates and manages AWS RDS database instances with comprehensive configuration options
- **Source**: `terraform-aws-modules/rds/aws//modules/db_instance`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_instance
- **Key Features**: Full instance lifecycle management, storage configuration, encryption, monitoring, backup management
- **Use Cases**: Production databases, application backends, read replicas, test environments

### 2. db_subnet_group

- **Purpose**: Creates and manages AWS DB subnet groups defining where RDS instances can be deployed
- **Source**: `terraform-aws-modules/rds/aws//modules/db_subnet_group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_subnet_group
- **Key Features**: Subnet group creation, VPC integration, multi-AZ subnet configuration, tagging support
- **Use Cases**: Network isolation, multi-AZ deployments, VPC database placement, subnet organization

### 3. db_parameter_group

- **Purpose**: Creates and manages RDS parameter groups for database engine parameter customization
- **Source**: `terraform-aws-modules/rds/aws//modules/db_parameter_group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_parameter_group
- **Key Features**: Engine parameter customization, parameter family support, parameter modification, tagging
- **Use Cases**: Performance tuning, character set configuration, connection limits, engine-specific settings

### 4. db_option_group

- **Purpose**: Creates and manages RDS option groups for additional database features and configurations
- **Source**: `terraform-aws-modules/rds/aws//modules/db_option_group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_option_group
- **Key Features**: Optional feature enablement, engine-specific options, Oracle and SQL Server features, tagging
- **Use Cases**: Oracle advanced features, SQL Server features, transparent data encryption, auditing

### 5. db_instance_role_association

- **Purpose**: Associates IAM roles with RDS database instances for AWS service integration
- **Source**: `terraform-aws-modules/rds/aws//modules/db_instance_role_association`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_instance_role_association
- **Key Features**: IAM role association, feature-based role mapping, S3 integration support, Lambda integration
- **Use Cases**: S3 import/export, Lambda function invocation, CloudWatch Logs access, cross-service integration

## Submodule 1: db_instance

### Description

The db_instance submodule creates and manages AWS RDS database instances with full lifecycle management capabilities. This submodule provides comprehensive configuration options for all aspects of RDS instances including storage types, engine versions, instance sizing, networking, security, monitoring, and backup configurations. It supports all RDS database engines and includes advanced features like Performance Insights, enhanced monitoring, IAM authentication, and blue-green deployments.

### Key Features

- Support for all RDS database engines (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server)
- Multiple storage types with configurable IOPS and storage autoscaling
- Multi-AZ deployment with automatic failover capabilities
- Comprehensive backup and point-in-time recovery configuration
- Enhanced monitoring and Performance Insights integration
- IAM database authentication and Secrets Manager integration
- Blue-green deployment support for zero-downtime updates

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `identifier` | `string` | - | Unique identifier for the RDS instance |
| `engine` | `string` | - | Database engine type (mysql, postgres, oracle-ee, sqlserver-ex, etc.) |
| `engine_version` | `string` | - | Database engine version to use |
| `instance_class` | `string` | - | RDS instance type (e.g., db.t3.micro, db.m5.large) |
| `allocated_storage` | `number` | - | Initial storage allocation in GB |
| `storage_type` | `string` | `"gp2"` | Storage type (standard, gp2, gp3, io1) |
| `storage_encrypted` | `bool` | `true` | Enable storage encryption at rest |
| `kms_key_id` | `string` | `null` | ARN of KMS key for storage encryption |
| `db_name` | `string` | `null` | Name of the initial database to create |
| `username` | `string` | - | Master username for the database |
| `password` | `string` | - | Master password (sensitive, use Secrets Manager recommended) |
| `vpc_security_group_ids` | `list(string)` | `[]` | List of VPC security group IDs to associate |
| `db_subnet_group_name` | `string` | `null` | Database subnet group name |
| `multi_az` | `bool` | `false` | Enable Multi-AZ deployment for high availability |
| `publicly_accessible` | `bool` | `false` | Allow public access to the instance |
| `backup_retention_period` | `number` | `null` | Number of days to retain automated backups (0-35) |
| `backup_window` | `string` | `null` | Daily time range for automated backups (UTC) |
| `maintenance_window` | `string` | `null` | Weekly time range for system maintenance (UTC) |
| `monitoring_interval` | `number` | `0` | Enhanced monitoring interval in seconds (0, 1, 5, 10, 15, 30, 60) |
| `performance_insights_enabled` | `bool` | `false` | Enable Performance Insights for query analysis |
| `skip_final_snapshot` | `bool` | `false` | Skip final snapshot when deleting instance |
| `deletion_protection` | `bool` | `false` | Protect instance from accidental deletion |

### Main Outputs

| Output | Description |
|--------|-------------|
| `db_instance_endpoint` | Connection endpoint for the database (hostname:port) |
| `db_instance_address` | Hostname of the RDS instance |
| `db_instance_port` | Port number the database listens on |
| `db_instance_identifier` | Unique identifier of the RDS instance |
| `db_instance_arn` | Amazon Resource Name (ARN) of the instance |
| `db_instance_username` | Master username for the database |
| `db_instance_engine` | Database engine type |
| `db_instance_engine_version_actual` | Running database engine version |
| `db_instance_availability_zone` | Availability zone of the instance |
| `enhanced_monitoring_iam_role_arn` | IAM role ARN for enhanced monitoring |

### Usage Example

```hcl
module "production_db" {
  source = "terraform-aws-modules/rds/aws//modules/db_instance"

  identifier = "prod-app-db"
  engine     = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.xlarge"

  # Storage configuration
  allocated_storage     = 100
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id           = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  max_allocated_storage = 1000  # Enable storage autoscaling

  # Database configuration
  db_name  = "production"
  username = "dbadmin"
  password = "ChangeMe123!"  # Use AWS Secrets Manager in production
  port     = 5432

  # Network configuration
  vpc_security_group_ids = ["sg-0123456789abcdef0"]
  db_subnet_group_name   = "prod-db-subnet-group"
  publicly_accessible    = false

  # High availability
  multi_az = true

  # Backup configuration
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"
  skip_final_snapshot    = false
  deletion_protection    = true

  # Monitoring
  monitoring_interval         = 60
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = {
    Environment = "production"
    Application = "web-app"
    ManagedBy   = "terraform"
  }
}
```

## Submodule 2: db_subnet_group

### Description

The db_subnet_group submodule manages AWS DB subnet groups that define the subnets where RDS database instances can be deployed within a VPC. This submodule is essential for network isolation and Multi-AZ deployments, allowing you to specify which subnets across different availability zones are available for database placement. It provides a simple interface for creating and managing subnet groups with optional naming flexibility and comprehensive tagging support.

### Key Features

- Creates DB subnet groups for VPC network isolation
- Supports Multi-AZ subnet configurations across availability zones
- Flexible naming with optional prefix support
- Conditional resource creation with create flag
- Comprehensive tagging for resource organization

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the DB subnet group |
| `name` | `string` | - | Name of the DB subnet group |
| `use_name_prefix` | `bool` | `false` | Use name as prefix for unique naming |
| `description` | `string` | `null` | Description of the subnet group |
| `subnet_ids` | `list(string)` | - | List of VPC subnet IDs for the DB subnet group |
| `tags` | `map(string)` | `{}` | Map of tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `db_subnet_group_id` | The name of the DB subnet group |
| `db_subnet_group_arn` | Amazon Resource Name (ARN) of the DB subnet group |

### Usage Example

```hcl
module "db_subnet_group" {
  source = "terraform-aws-modules/rds/aws//modules/db_subnet_group"

  name        = "production-db-subnet-group"
  description = "Subnet group for production RDS databases"

  # Specify subnets in different availability zones for Multi-AZ
  subnet_ids = [
    "subnet-0123456789abcdef0",  # us-east-1a
    "subnet-0abcdef123456789f",  # us-east-1b
    "subnet-0fedcba987654321f"   # us-east-1c
  ]

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Use the subnet group with an RDS instance
module "database" {
  source = "terraform-aws-modules/rds/aws"

  identifier           = "prod-db"
  db_subnet_group_name = module.db_subnet_group.db_subnet_group_id

  # ... other database configuration
}
```

## Submodule 3: db_parameter_group

### Description

The db_parameter_group submodule creates and manages AWS RDS parameter groups, which allow customization of database engine parameters for performance tuning, character set configuration, connection management, and engine-specific settings. Parameter groups are engine-family specific and provide a way to apply consistent database configurations across multiple instances. This submodule supports dynamic parameter modification and includes validation to ensure parameter compatibility with the specified database family.

### Key Features

- Creates custom parameter groups for any RDS engine family
- Supports multiple parameter configurations with name-value pairs
- Dynamic parameter modification without instance restart (when supported)
- Parameter family validation to ensure compatibility
- Flexible naming with prefix support
- Conditional resource creation

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the DB parameter group |
| `name` | `string` | - | Name of the DB parameter group |
| `use_name_prefix` | `bool` | `false` | Use name as prefix for unique naming |
| `description` | `string` | `null` | Description of the parameter group |
| `family` | `string` | - | Database parameter group family (e.g., postgres15, mysql8.0) |
| `parameters` | `list(object)` | `[]` | List of parameter objects with name, value, and optional apply_method |
| `tags` | `map(string)` | `{}` | Map of tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `db_parameter_group_id` | The identifier of the DB parameter group |
| `db_parameter_group_arn` | Amazon Resource Name (ARN) of the DB parameter group |

### Usage Example

```hcl
module "postgres_parameter_group" {
  source = "terraform-aws-modules/rds/aws//modules/db_parameter_group"

  name        = "prod-postgres-params"
  description = "Custom parameter group for PostgreSQL 15"
  family      = "postgres15"

  parameters = [
    {
      name  = "max_connections"
      value = "200"
    },
    {
      name  = "shared_buffers"
      value = "256MB"
    },
    {
      name  = "effective_cache_size"
      value = "1GB"
    },
    {
      name  = "work_mem"
      value = "16MB"
    },
    {
      name  = "maintenance_work_mem"
      value = "128MB"
    },
    {
      name         = "log_min_duration_statement"
      value        = "1000"  # Log queries taking more than 1 second
      apply_method = "immediate"
    }
  ]

  tags = {
    Environment = "production"
    Engine      = "postgresql"
  }
}

# Use the parameter group with an RDS instance
module "database" {
  source = "terraform-aws-modules/rds/aws"

  identifier         = "prod-db"
  parameter_group_name = module.postgres_parameter_group.db_parameter_group_id

  # ... other database configuration
}
```

## Submodule 4: db_option_group

### Description

The db_option_group submodule creates and manages AWS RDS option groups, which enable additional features and functionality for Oracle and SQL Server database engines. Option groups allow you to configure engine-specific features like Oracle Advanced Security, SQL Server audit logs, transparent data encryption, and other database-specific capabilities that aren't available through parameter groups. This submodule provides flexible configuration of options with version-specific settings and port configurations.

### Key Features

- Creates option groups for Oracle and SQL Server databases
- Supports multiple options with individual settings and configurations
- Version-specific option configuration for major engine versions
- Port configuration for options requiring network access
- Security group association for option-level network access
- Conditional resource creation and flexible naming

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the DB option group |
| `name` | `string` | - | Name of the option group |
| `use_name_prefix` | `bool` | `false` | Use name as prefix for unique naming |
| `option_group_description` | `string` | `null` | Description of the option group |
| `engine_name` | `string` | - | Database engine name (e.g., oracle-ee, sqlserver-se) |
| `major_engine_version` | `string` | - | Major version of the database engine |
| `options` | `list(object)` | `[]` | List of option configurations with settings |
| `tags` | `map(string)` | `{}` | Map of tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `db_option_group_id` | The identifier of the DB option group |
| `db_option_group_arn` | Amazon Resource Name (ARN) of the DB option group |

### Usage Example

```hcl
module "oracle_option_group" {
  source = "terraform-aws-modules/rds/aws//modules/db_option_group"

  name                     = "prod-oracle-options"
  option_group_description = "Option group for Oracle Enterprise Edition"
  engine_name              = "oracle-ee"
  major_engine_version     = "19"

  options = [
    {
      option_name = "STATSPACK"
      option_settings = []
    },
    {
      option_name = "OEM"
      port        = 5500
      option_settings = []
    },
    {
      option_name = "Timezone"
      option_settings = [
        {
          name  = "TIME_ZONE"
          value = "US/Eastern"
        }
      ]
    }
  ]

  tags = {
    Environment = "production"
    Engine      = "oracle-ee"
  }
}

# Example for SQL Server with audit logging
module "sqlserver_option_group" {
  source = "terraform-aws-modules/rds/aws//modules/db_option_group"

  name                     = "prod-sqlserver-options"
  option_group_description = "Option group for SQL Server with auditing"
  engine_name              = "sqlserver-se"
  major_engine_version     = "15.00"

  options = [
    {
      option_name = "SQLSERVER_AUDIT"
      option_settings = [
        {
          name  = "IAM_ROLE_ARN"
          value = "arn:aws:iam::123456789012:role/rds-audit-role"
        },
        {
          name  = "S3_BUCKET_ARN"
          value = "arn:aws:s3:::my-audit-bucket"
        }
      ]
    }
  ]

  tags = {
    Environment = "production"
    Engine      = "sqlserver-se"
  }
}
```

## Submodule 5: db_instance_role_association

### Description

The db_instance_role_association submodule manages the association between an RDS database instance and an IAM role, enabling integration with other AWS services. This is commonly used to grant RDS instances permissions to access S3 buckets for data import/export, invoke Lambda functions, publish logs to CloudWatch, or integrate with other AWS services. The association is feature-specific, meaning different features require different role associations with appropriate IAM policies.

### Key Features

- Associates IAM roles with RDS database instances
- Enables S3 integration for data import and export operations
- Supports Lambda function invocation from database
- Feature-based role mapping for specific integrations
- Conditional resource creation

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the role association |
| `db_instance_identifier` | `string` | - | The DB instance identifier to associate the role with |
| `feature_name` | `string` | - | Name of the feature for the DB instance role association (e.g., S3_INTEGRATION) |
| `role_arn` | `string` | - | Amazon Resource Name (ARN) of the IAM role to associate |

### Main Outputs

| Output | Description |
|--------|-------------|
| `db_instance_role_association_id` | Identifier of the role association (DB Instance Identifier and IAM Role ARN) |

### Usage Example

```hcl
# Create IAM role for S3 integration
resource "aws_iam_role" "rds_s3_integration" {
  name = "rds-s3-integration-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "rds_s3_policy" {
  name = "rds-s3-access"
  role = aws_iam_role.rds_s3_integration.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject"
        ]
        Resource = [
          "arn:aws:s3:::my-data-bucket",
          "arn:aws:s3:::my-data-bucket/*"
        ]
      }
    ]
  })
}

# Associate the role with the RDS instance
module "rds_s3_association" {
  source = "terraform-aws-modules/rds/aws//modules/db_instance_role_association"

  db_instance_identifier = module.database.db_instance_identifier
  feature_name          = "S3_INTEGRATION"
  role_arn              = aws_iam_role.rds_s3_integration.arn
}

# Example for Oracle with S3 import
module "oracle_s3_integration" {
  source = "terraform-aws-modules/rds/aws//modules/db_instance_role_association"

  db_instance_identifier = "prod-oracle-db"
  feature_name          = "S3_INTEGRATION"
  role_arn              = aws_iam_role.rds_s3_integration.arn
}
```

## Best Practices

### Database Architecture and Design

1. **Choose the Right Engine**: Select the database engine based on application requirements, licensing costs, and feature compatibility
2. **Size Instances Appropriately**: Start with smaller instance classes and scale based on actual performance metrics rather than over-provisioning
3. **Design for Scalability**: Use read replicas for read-heavy workloads and separate analytical queries from transactional workloads
4. **Normalize Data Appropriately**: Balance between normalization for data integrity and denormalization for query performance
5. **Plan for Growth**: Monitor storage usage trends and enable storage autoscaling to prevent out-of-space conditions
6. **Use Multi-AZ for Production**: Always enable Multi-AZ deployments for production workloads to ensure high availability
7. **Separate Environments**: Use dedicated RDS instances for development, staging, and production environments

### Storage Configuration

1. **Choose Storage Type Wisely**: Use GP3 for most workloads, GP2 for small databases, and IO1/IO2 for high-performance requirements
2. **Enable Storage Autoscaling**: Configure max_allocated_storage to allow automatic storage growth without downtime
3. **Monitor IOPS Usage**: Track IOPS consumption and upgrade to provisioned IOPS storage if consistently hitting limits
4. **Provision Adequate Storage**: Allocate at least 20% more storage than current needs to accommodate growth and performance
5. **Consider Storage Performance**: Remember that GP2 IOPS scales with storage size (3 IOPS per GB, baseline minimum 100)
6. **Optimize for Workload**: Use provisioned IOPS (IO1/IO2) for latency-sensitive or high-throughput applications
7. **Monitor Storage Metrics**: Set up CloudWatch alarms for storage space, IOPS utilization, and throughput

### Security and Compliance

1. **Enable Encryption at Rest**: Always set storage_encrypted = true and use customer-managed KMS keys for sensitive data
2. **Implement Network Isolation**: Deploy RDS instances in private subnets and use security groups to restrict access
3. **Use IAM Database Authentication**: Enable IAM authentication for applications that support it to avoid storing credentials
4. **Rotate Credentials Regularly**: Implement password rotation policies and use AWS Secrets Manager for credential management
5. **Enable Deletion Protection**: Set deletion_protection = true for production databases to prevent accidental deletion
6. **Encrypt Connections**: Require SSL/TLS for all database connections and use certificate validation
7. **Enable Audit Logging**: Export database audit logs to CloudWatch for security monitoring and compliance
8. **Apply Least Privilege**: Grant only necessary database permissions to application users and use separate credentials per application
9. **Use Security Groups Effectively**: Create specific security groups for database access and avoid using 0.0.0.0/0 rules
10. **Disable Public Access**: Keep publicly_accessible = false for production databases and use VPN or Direct Connect for external access
11. **Enable CloudWatch Log Exports**: Export error logs, slow query logs, and audit logs for security analysis

### Backup and Disaster Recovery

1. **Configure Appropriate Retention**: Set backup_retention_period to at least 7 days for production, 14-35 days for critical systems
2. **Test Recovery Procedures**: Regularly test point-in-time recovery and snapshot restoration to verify backup integrity
3. **Schedule Backup Windows**: Set backup_window during low-activity periods to minimize performance impact
4. **Use Cross-Region Replicas**: For critical workloads, implement read replicas in secondary regions for disaster recovery
5. **Automate Snapshot Management**: Use AWS Backup or Lambda functions to automate snapshot creation and retention policies
6. **Tag Snapshots**: Apply meaningful tags to manual snapshots for lifecycle management and cost tracking
7. **Don't Skip Final Snapshots**: Set skip_final_snapshot = false for production databases to ensure recovery options
8. **Monitor Backup Status**: Create CloudWatch alarms to alert on backup failures or missing backups
9. **Document Recovery Procedures**: Maintain runbooks with RTO/RPO targets and step-by-step recovery procedures
10. **Test Failover**: Regularly test Multi-AZ failover procedures to ensure applications handle failover gracefully

### Performance Optimization

1. **Enable Performance Insights**: Activate performance_insights_enabled for query-level performance diagnostics
2. **Configure Enhanced Monitoring**: Set monitoring_interval to 60 seconds for production databases to track OS-level metrics
3. **Optimize Parameter Groups**: Tune database parameters based on workload characteristics (connection limits, buffer sizes, cache settings)
4. **Use Read Replicas**: Offload read traffic to read replicas to reduce load on the primary instance
5. **Monitor Slow Queries**: Enable slow query logging and regularly review slow queries for optimization opportunities
6. **Optimize Query Performance**: Use database-specific query analysis tools and create appropriate indexes
7. **Configure Connection Pooling**: Implement connection pooling in applications to reduce connection overhead
8. **Size Memory Appropriately**: Choose instance classes with enough memory to fit working set in RAM
9. **Monitor Key Metrics**: Track CPU utilization, freeable memory, read/write IOPS, and database connections
10. **Upgrade Engine Versions**: Regularly upgrade to newer engine versions for performance improvements and bug fixes
11. **Use Appropriate Instance Classes**: Choose instance classes optimized for your workload (memory-optimized for large datasets, burstable for development)

### Cost Optimization

1. **Right-Size Instances**: Regularly review CloudWatch metrics and downsize over-provisioned instances
2. **Use Reserved Instances**: Purchase reserved instances for predictable production workloads for up to 69% savings
3. **Optimize Storage**: Use GP3 instead of GP2 for better price/performance ratio and independently configure IOPS
4. **Stop Dev/Test Instances**: Implement automation to stop development and test databases during non-business hours
5. **Delete Unused Snapshots**: Implement lifecycle policies to delete old manual snapshots that are no longer needed
6. **Optimize Backup Retention**: Balance retention requirements with storage costs; use shorter retention for non-critical databases
7. **Monitor Data Transfer**: Place applications in the same region and availability zone as databases to reduce data transfer costs
8. **Use Read Replicas Strategically**: Only create read replicas when needed for performance or availability, not by default
9. **Leverage Storage Autoscaling**: Configure autoscaling to prevent over-provisioning while ensuring capacity
10. **Use Tags for Cost Allocation**: Apply consistent tags to track costs by application, environment, or business unit
11. **Consider Serverless Options**: For variable workloads, evaluate Aurora Serverless v2 as an alternative

### Monitoring and Observability

1. **Enable Enhanced Monitoring**: Configure 60-second monitoring intervals for production databases
2. **Set Up CloudWatch Alarms**: Create alarms for CPU, memory, storage space, IOPS, connections, and replication lag
3. **Export Logs to CloudWatch**: Enable log exports for error logs, slow query logs, and audit logs
4. **Use Performance Insights**: Enable Performance Insights with at least 7-day retention for query analysis
5. **Monitor Replication Lag**: For read replicas, set up alarms for replica lag exceeding acceptable thresholds
6. **Track Connection Counts**: Monitor database connections and set alarms for approaching max_connections limit
7. **Monitor Storage Growth**: Track storage usage trends to predict when scaling will be needed
8. **Create Dashboards**: Build CloudWatch dashboards for at-a-glance monitoring of database health
9. **Implement Log Analysis**: Use CloudWatch Logs Insights to analyze database logs for errors and performance issues
10. **Monitor Backup Status**: Set up notifications for backup failures or missing automated backups

### High Availability and Reliability

1. **Enable Multi-AZ**: Always use Multi-AZ deployments for production databases to ensure automatic failover
2. **Test Failover Scenarios**: Regularly test failover by rebooting instances with failover option
3. **Use Multiple Availability Zones**: Deploy database subnet groups across at least two availability zones
4. **Implement Application Retry Logic**: Configure applications to retry connections with exponential backoff during failovers
5. **Monitor Failover Events**: Set up CloudWatch Events to track and alert on failover occurrences
6. **Use Read Replicas for DR**: Create cross-region read replicas for disaster recovery scenarios
7. **Configure Appropriate Timeouts**: Set connection and query timeouts in applications to handle transient failures
8. **Document RTO/RPO**: Define and document Recovery Time Objective and Recovery Point Objective for each database
9. **Use Health Checks**: Implement application-level health checks that verify database connectivity
10. **Plan Maintenance Windows**: Schedule maintenance during low-traffic periods and communicate with stakeholders

### Operational Excellence

1. **Use Infrastructure as Code**: Manage all RDS resources using Terraform with version control
2. **Enable Auto Minor Upgrades**: Allow automatic minor version upgrades during maintenance windows for security patches
3. **Plan Major Upgrades**: Test major version upgrades in non-production environments before applying to production
4. **Implement Tagging Strategy**: Use consistent tags for environment, application, owner, and cost center
5. **Configure Maintenance Windows**: Set maintenance_window during periods that minimize business impact
6. **Monitor Engine Versions**: Track engine versions and plan upgrades to avoid end-of-life versions
7. **Use Parameter Store**: Store database configuration values in AWS Systems Manager Parameter Store
8. **Implement Change Management**: Use Terraform plan and approval processes before applying database changes
9. **Document Database Architecture**: Maintain up-to-date documentation of database configurations and dependencies
10. **Create Runbooks**: Document operational procedures for common tasks (failover, scaling, recovery)
11. **Use Terraform State Management**: Store Terraform state in S3 with DynamoDB locking for team collaboration
12. **Review Security Groups**: Regularly audit security group rules and remove unnecessary access

### Development and Deployment

1. **Use Separate Parameter Groups**: Create environment-specific parameter groups for development, staging, and production
2. **Parameterize Configurations**: Use Terraform variables for all environment-specific settings
3. **Test Changes in Non-Production**: Always test parameter changes, engine upgrades, and configuration updates in dev/staging first
4. **Use Blue-Green Deployments**: Leverage blue-green deployment feature for zero-downtime updates
5. **Implement CI/CD Integration**: Integrate Terraform database deployments into CI/CD pipelines with approval gates
6. **Version Control Everything**: Keep all Terraform configurations, parameter group settings, and option groups in version control
7. **Use Terraform Modules**: Leverage the RDS module for consistent configuration across environments
8. **Document Dependencies**: Clearly document database dependencies on other infrastructure components
9. **Plan Database Migrations**: Use tools like Flyway or Liquibase for schema version control and migrations
10. **Avoid Manual Changes**: Never make manual changes through the AWS Console; always use Terraform

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-rds/tree/master/examples
- **AWS RDS User Guide**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/
- **AWS RDS Best Practices**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html
- **RDS MySQL Documentation**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_MySQL.html
- **RDS PostgreSQL Documentation**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html
- **RDS Oracle Documentation**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Oracle.html
- **RDS SQL Server Documentation**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_SQLServer.html
- **RDS Performance Insights**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.html
- **Enhanced Monitoring**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.html
- **IAM Database Authentication**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.html
- **RDS Backup and Restore**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_CommonTasks.BackupRestore.html
- **RDS Blue-Green Deployments**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/blue-green-deployments.html
- **RDS Pricing**: https://aws.amazon.com/rds/pricing/
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

## Notes for AI Agents

When using this module in automated workflows:

1. **Security First**: Always enable encryption at rest and in transit, use KMS customer-managed keys for production
2. **High Availability**: Enable Multi-AZ deployments for production workloads to ensure automatic failover
3. **Network Isolation**: Deploy databases in private subnets with restrictive security group rules
4. **Credential Management**: Use AWS Secrets Manager for master passwords, never hardcode credentials
5. **Backup Strategy**: Configure backup retention periods appropriate for RPO requirements (7-35 days)
6. **Monitoring**: Enable enhanced monitoring and Performance Insights for production databases
7. **Storage Planning**: Enable storage autoscaling to prevent out-of-space conditions
8. **Tagging**: Apply consistent tags for environment, application, owner, and cost center
9. **Parameter Groups**: Create custom parameter groups for production workloads with optimized settings
10. **Deletion Protection**: Enable deletion protection for production databases to prevent accidental deletion
11. **Engine Selection**: Choose database engine based on application compatibility and licensing requirements
12. **Instance Sizing**: Start with appropriate instance classes based on workload analysis, not guesses
13. **Testing**: Always test database configurations, parameter changes, and engine upgrades in non-production first
14. **Documentation**: Document RTO/RPO requirements, backup strategies, and failover procedures
