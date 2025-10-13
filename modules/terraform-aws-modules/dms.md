# Terraform AWS DMS Module

## Module Information

- **Module Name**: `dms`
- **Source**: `terraform-aws-modules/dms/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-dms
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/dms/aws/latest
- **Latest Version**: 2.6.0
- **Purpose**: Terraform module to create AWS Database Migration Service (DMS) resources for database migrations and continuous data replication
- **Service**: AWS Database Migration Service (AWS DMS)
- **Category**: Database, Migration, Data Integration
- **Keywords**: aurora, cdc, certificate, change-data-capture, cloudwatch-logs, data-migration, data-replication, database-migration, db2, documentdb, dynamodb, endpoint, etl, event-subscription, full-load, heterogeneous-migration, homogeneous-migration, iam-role, kafka, kinesis, mongodb, msk, multi-az, mysql, neptune, ongoing-replication, opensearch, oracle, postgresql, redshift, replication-instance, replication-task, s3, sap-ase, schema-conversion, serverless, sql-server, subnet-group, target-endpoint, timestream
- **Use For**: database migration to AWS cloud, cross-platform database migrations, continuous data replication for disaster recovery, modernizing legacy databases, real-time data streaming to analytics platforms, consolidating databases from multiple sources, migrating from commercial to open-source databases, hybrid cloud data synchronization, data lake population from operational databases, database version upgrades with minimal downtime, multi-region database replication, heterogeneous database migrations

## Description

The AWS Database Migration Service (DMS) Terraform module provides a comprehensive solution for creating and managing database migration infrastructure on AWS. AWS DMS is a cloud service that enables migration of relational databases, data warehouses, NoSQL databases, and other data stores with minimal downtime. The module simplifies the deployment of replication instances, configuration of source and target endpoints, creation of replication tasks, and management of IAM roles required for DMS operations. It supports both one-time migrations and continuous data replication scenarios, making it suitable for database modernization, disaster recovery, and data integration use cases.

This module handles the complete lifecycle of DMS resources including replication subnet groups for network isolation, replication instances with configurable compute capacity and storage, and endpoint configurations for various database engines and data stores. It supports complex migration scenarios with multiple source and target endpoints, enabling parallel migrations, multi-database consolidations, and heterogeneous database migrations between different database engines. The module provides flexible configuration options for migration types including full load, change data capture (CDC), and full load with CDC for minimal downtime migrations.

The module integrates seamlessly with AWS services by automatically managing required IAM roles and policies for DMS operations, CloudWatch logging, and VPC networking. It supports advanced DMS features including event subscriptions for monitoring migration progress, SSL/TLS certificates for secure connections, serverless replication configurations for automatic scaling, and detailed task settings for performance optimization. With built-in support for S3 endpoints, Kafka streaming, Kinesis data streams, and various AWS database services, this module enables organizations to build comprehensive data migration and replication pipelines using infrastructure-as-code best practices.

## Key Features

- **Replication Instance Management**: Create and configure DMS replication instances with customizable compute classes, storage allocation, and Multi-AZ deployment options
- **Subnet Group Configuration**: Define replication subnet groups for network isolation and multi-AZ high availability
- **Comprehensive Endpoint Support**: Configure source and target endpoints for 15+ database engines and data stores including Oracle, SQL Server, PostgreSQL, MySQL, MongoDB, S3, Kafka, Kinesis, DynamoDB, Redshift, and more
- **S3 Endpoint Integration**: Specialized support for S3 endpoints with configurable data formats (CSV, Parquet, ORC) and compression options
- **Replication Task Management**: Create multiple replication tasks with configurable migration types (full load, CDC, full load with CDC)
- **Serverless Replication Support**: Configure serverless DMS replication with automatic capacity scaling and Multi-AZ deployment
- **IAM Role Automation**: Automatically create and manage required IAM roles including dms-vpc-role, dms-cloudwatch-logs-role, and dms-access-for-endpoint
- **Event Subscriptions**: Configure SNS-based event subscriptions for monitoring replication instance, task, and endpoint events
- **Certificate Management**: Create and manage SSL/TLS certificates for secure database connections
- **CloudWatch Logging Integration**: Enable detailed CloudWatch logs for debugging and monitoring replication tasks
- **Multi-AZ High Availability**: Deploy replication instances across multiple Availability Zones for fault tolerance
- **Change Data Capture (CDC)**: Support for ongoing replication using database transaction logs
- **Task Settings Customization**: Fine-tune task behavior with detailed settings for LOB handling, parallel load, validation, and error handling
- **Table Mapping Rules**: Define selection and transformation rules for filtering and transforming data during migration
- **Permission Boundary Support**: Apply IAM permission boundaries for delegated administration scenarios
- **Redshift Target Permissions**: Optional configuration for granting DMS access to Amazon Redshift targets
- **Comprehensive Tagging**: Apply tags across all resources for cost allocation, governance, and organization
- **Conditional Resource Creation**: Control creation of individual components (instances, endpoints, tasks) with feature flags

## Main Use Cases

1. **Database Migration to AWS**: Migrate on-premises or cloud databases to AWS managed database services with minimal downtime
2. **Heterogeneous Database Migrations**: Migrate between different database engines (e.g., Oracle to PostgreSQL, SQL Server to Aurora)
3. **Continuous Data Replication**: Set up ongoing replication for disaster recovery, read replicas, or multi-region deployments
4. **Database Modernization**: Migrate from commercial databases to open-source alternatives for cost optimization
5. **Data Lake Population**: Continuously stream database changes to S3 data lakes in Parquet or other analytics-friendly formats
6. **Real-Time Analytics**: Replicate data to Kinesis or Kafka for real-time processing and analytics pipelines
7. **Database Consolidation**: Migrate and consolidate multiple databases into a single target database or data warehouse
8. **Development and Testing**: Create near-real-time copies of production databases for development and testing environments
9. **Hybrid Cloud Synchronization**: Maintain synchronized data between on-premises and cloud databases for gradual migration
10. **Zero-Downtime Upgrades**: Perform database version upgrades with minimal application downtime using parallel replication

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `tags` | `map(string)` | `{}` | Map of tags to apply to all resources |
| `create_iam_roles` | `bool` | `true` | Determines whether to create required DMS IAM roles |
| `iam_role_permissions_boundary` | `string` | `null` | ARN of the policy for IAM role permissions boundary |
| `iam_role_tags` | `map(string)` | `{}` | Additional tags for DMS IAM roles |
| `enable_redshift_target_permissions` | `bool` | `false` | Enable permissions for Redshift target endpoint |
| `create_repl_subnet_group` | `bool` | `true` | Determines whether to create replication subnet group |
| `repl_subnet_group_name` | `string` | `null` | Name of the replication subnet group |
| `repl_subnet_group_description` | `string` | `null` | Description for the replication subnet group |
| `repl_subnet_group_subnet_ids` | `list(string)` | `[]` | List of EC2 subnet IDs for the replication subnet group |
| `repl_subnet_group_tags` | `map(string)` | `{}` | Additional tags for replication subnet group |
| `create_repl_instance` | `bool` | `true` | Determines whether to create replication instance |
| `repl_instance_allocated_storage` | `number` | `null` | Amount of storage in GB to be allocated for the replication instance |
| `repl_instance_auto_minor_version_upgrade` | `bool` | `true` | Indicates that minor engine upgrades applied automatically |
| `repl_instance_allow_major_version_upgrade` | `bool` | `true` | Indicates that major version upgrades are allowed |
| `repl_instance_apply_immediately` | `bool` | `null` | Indicates whether changes should be applied immediately |
| `repl_instance_engine_version` | `string` | `null` | Engine version number of the replication instance |
| `repl_instance_multi_az` | `bool` | `null` | Specifies if the replication instance is a Multi-AZ deployment |
| `repl_instance_preferred_maintenance_window` | `string` | `null` | Weekly time range for maintenance |
| `repl_instance_publicly_accessible` | `bool` | `null` | Specifies the accessibility options for the replication instance |
| `repl_instance_class` | `string` | `null` | Compute and memory capacity of the replication instance |
| `repl_instance_id` | `string` | `null` | Replication instance identifier |
| `repl_instance_vpc_security_group_ids` | `list(string)` | `null` | List of VPC security group IDs to be used |
| `repl_instance_tags` | `map(string)` | `{}` | Additional tags for replication instance |
| `endpoints` | `any` | `{}` | Map of endpoint definitions to create |
| `s3_endpoints` | `any` | `{}` | Map of S3 endpoint definitions to create |
| `replication_tasks` | `any` | `{}` | Map of replication task definitions to create |
| `event_subscriptions` | `any` | `{}` | Map of event subscription definitions to create |
| `certificates` | `map(any)` | `{}` | Map of certificates to create |
| `create_access_iam_role` | `bool` | `false` | Determines whether to create access IAM role |
| `access_iam_role_name` | `string` | `null` | Name to use for access IAM role |
| `access_secret_arns` | `list(string)` | `[]` | List of secret ARNs for access IAM role policy |
| `access_source_s3_bucket_arns` | `list(string)` | `[]` | List of source S3 bucket ARNs for access IAM role policy |
| `access_target_s3_bucket_arns` | `list(string)` | `[]` | List of target S3 bucket ARNs for access IAM role policy |
| `access_target_elasticsearch_arns` | `list(string)` | `[]` | List of Elasticsearch ARNs for access IAM role policy |
| `access_target_kinesis_arns` | `list(string)` | `[]` | List of Kinesis ARNs for access IAM role policy |

## Main Outputs

| Output | Description |
|--------|-------------|
| `replication_subnet_group_id` | ID of the replication subnet group |
| `replication_instance_arn` | ARN of the replication instance |
| `replication_instance_private_ips` | List of private IP addresses of the replication instance |
| `replication_instance_public_ips` | List of public IP addresses of the replication instance |
| `replication_instance_tags_all` | Map of tags assigned to the replication instance |
| `endpoints` | Map of endpoint configurations (marked as sensitive) |
| `s3_endpoints` | Map of S3 endpoint configurations (marked as sensitive) |
| `replication_tasks` | Map of replication task details |
| `serverless_replication_tasks` | Map of serverless replication task details |
| `event_subscriptions` | Map of event subscription details |
| `certificates` | Map of certificate details (marked as sensitive) |
| `dms_access_for_endpoint_iam_role_arn` | ARN of the DMS access for endpoint IAM role |
| `dms_access_for_endpoint_iam_role_id` | Name of the DMS access for endpoint IAM role |
| `dms_access_for_endpoint_iam_role_unique_id` | Stable unique ID of the DMS access for endpoint IAM role |
| `dms_cloudwatch_logs_iam_role_arn` | ARN of the DMS CloudWatch Logs IAM role |
| `dms_cloudwatch_logs_iam_role_id` | Name of the DMS CloudWatch Logs IAM role |
| `dms_cloudwatch_logs_iam_role_unique_id` | Stable unique ID of the DMS CloudWatch Logs IAM role |
| `dms_vpc_iam_role_arn` | ARN of the DMS VPC IAM role |
| `dms_vpc_iam_role_id` | Name of the DMS VPC IAM role |
| `dms_vpc_iam_role_unique_id` | Stable unique ID of the DMS VPC IAM role |
| `access_iam_role_name` | Name of the access IAM role |
| `access_iam_role_arn` | ARN of the access IAM role |
| `access_iam_role_unique_id` | Stable unique ID of the access IAM role |

## Usage Examples

### Example 1: Basic Database Migration (PostgreSQL to MySQL)

```hcl
module "database_migration_basic" {
  source = "terraform-aws-modules/dms/aws"

  # Replication subnet group
  repl_subnet_group_name        = "basic-migration"
  repl_subnet_group_description = "DMS replication subnet group"
  repl_subnet_group_subnet_ids  = module.vpc.database_subnets

  # Replication instance
  repl_instance_allocated_storage = 100
  repl_instance_class             = "dms.t3.medium"
  repl_instance_id                = "basic-migration-instance"
  repl_instance_multi_az          = false
  repl_instance_vpc_security_group_ids = [module.security_group.security_group_id]

  # Source endpoint (PostgreSQL)
  endpoints = {
    source_postgres = {
      endpoint_id   = "source-postgres"
      endpoint_type = "source"
      engine_name   = "postgres"
      server_name   = "source-db.example.com"
      port          = 5432
      database_name = "sourcedb"
      username      = "postgres_user"
      password      = "SecurePassword123!"
      ssl_mode      = "require"
    }

    # Target endpoint (MySQL)
    target_mysql = {
      endpoint_id   = "target-mysql"
      endpoint_type = "target"
      engine_name   = "mysql"
      server_name   = module.rds_mysql.db_instance_address
      port          = 3306
      database_name = "targetdb"
      username      = "mysql_user"
      password      = "SecurePassword456!"
    }
  }

  # Replication task
  replication_tasks = {
    postgres_to_mysql = {
      replication_task_id = "postgres-to-mysql-task"
      migration_type      = "full-load"
      source_endpoint_key = "source_postgres"
      target_endpoint_key = "target_mysql"
      table_mappings      = jsonencode({
        rules = [{
          rule-type = "selection"
          rule-id   = "1"
          rule-name = "1"
          object-locator = {
            schema-name = "public"
            table-name  = "%"
          }
          rule-action = "include"
        }]
      })
    }
  }

  tags = {
    Environment = "production"
    Project     = "database-migration"
  }
}
```

### Example 2: Continuous Data Replication with CDC

```hcl
module "database_replication_cdc" {
  source = "terraform-aws-modules/dms/aws"

  # Replication subnet group
  repl_subnet_group_name       = "cdc-replication"
  repl_subnet_group_subnet_ids = module.vpc.database_subnets

  # Replication instance with Multi-AZ
  repl_instance_allocated_storage            = 200
  repl_instance_class                        = "dms.c5.xlarge"
  repl_instance_id                           = "cdc-replication-instance"
  repl_instance_multi_az                     = true
  repl_instance_publicly_accessible          = false
  repl_instance_auto_minor_version_upgrade   = true
  repl_instance_preferred_maintenance_window = "sun:05:00-sun:06:00"

  # Endpoints
  endpoints = {
    source_oracle = {
      endpoint_id   = "source-oracle"
      endpoint_type = "source"
      engine_name   = "oracle"
      server_name   = "oracle-prod.example.com"
      port          = 1521
      database_name = "ORCL"
      username      = "dms_user"
      password      = data.aws_secretsmanager_secret_version.oracle_password.secret_string

      extra_connection_attributes = "useLogminerReader=N;useBfile=Y"
    }

    target_aurora = {
      endpoint_id   = "target-aurora-postgres"
      endpoint_type = "target"
      engine_name   = "aurora-postgresql"
      server_name   = module.aurora_postgresql.cluster_endpoint
      port          = 5432
      database_name = "postgres"
      username      = "postgres"
      password      = data.aws_secretsmanager_secret_version.aurora_password.secret_string
      ssl_mode      = "require"
    }
  }

  # CDC replication task
  replication_tasks = {
    oracle_to_aurora_cdc = {
      replication_task_id       = "oracle-aurora-cdc"
      migration_type            = "full-load-and-cdc"
      source_endpoint_key       = "source_oracle"
      target_endpoint_key       = "target_aurora"
      replication_task_settings = jsonencode({
        Logging = {
          EnableLogging = true
          LogComponents = [{
            Id       = "TRANSFORMATION"
            Severity = "LOGGER_SEVERITY_DEFAULT"
          }, {
            Id       = "SOURCE_CAPTURE"
            Severity = "LOGGER_SEVERITY_INFO"
          }]
        }
        ChangeProcessingDdlHandlingPolicy = {
          HandleSourceTableDropped   = true
          HandleSourceTableTruncated = true
        }
        FullLoadSettings = {
          TargetTablePrepMode = "DROP_AND_CREATE"
        }
      })
      table_mappings = jsonencode({
        rules = [{
          rule-type = "selection"
          rule-id   = "1"
          rule-name = "include-all-tables"
          object-locator = {
            schema-name = "%"
            table-name  = "%"
          }
          rule-action = "include"
        }]
      })
    }
  }

  # Event subscription
  event_subscriptions = {
    replication_task = {
      name                             = "cdc-replication-events"
      enabled                          = true
      sns_topic_arn                    = aws_sns_topic.dms_events.arn
      source_type                      = "replication-task"
      event_categories                 = ["failure", "state change", "configuration change"]
    }
  }

  tags = {
    Environment = "production"
    Use-Case    = "continuous-replication"
  }
}
```

### Example 3: S3 Data Lake Migration

```hcl
module "s3_data_lake_migration" {
  source = "terraform-aws-modules/dms/aws"

  # Replication subnet group
  repl_subnet_group_name       = "s3-datalake"
  repl_subnet_group_subnet_ids = module.vpc.private_subnets

  # Replication instance
  repl_instance_class = "dms.c5.large"
  repl_instance_id    = "s3-datalake-instance"

  # Create access IAM role for S3
  create_access_iam_role       = true
  access_iam_role_name         = "dms-s3-access"
  access_target_s3_bucket_arns = [module.s3_datalake.s3_bucket_arn]

  # Source database endpoint
  endpoints = {
    source_mysql = {
      endpoint_id   = "mysql-source"
      endpoint_type = "source"
      engine_name   = "mysql"
      server_name   = module.rds_mysql.db_instance_address
      port          = 3306
      database_name = "production"
      username      = "dms_user"
      password      = data.aws_secretsmanager_secret_version.mysql_pass.secret_string
    }
  }

  # S3 target endpoint
  s3_endpoints = {
    target_s3_parquet = {
      endpoint_id                 = "s3-parquet-target"
      endpoint_type               = "target"
      bucket_name                 = module.s3_datalake.s3_bucket_id
      bucket_folder               = "mysql-exports"
      compression_type            = "GZIP"
      data_format                 = "parquet"
      date_partition_enabled      = true
      date_partition_delimiter    = "SLASH"
      parquet_timestamp_in_millisecond = true
      parquet_version             = "parquet-2-0"
      service_access_role_arn     = module.database_migration_service.access_iam_role_arn
    }
  }

  # Replication task
  replication_tasks = {
    mysql_to_s3 = {
      replication_task_id = "mysql-to-s3-parquet"
      migration_type      = "full-load-and-cdc"
      source_endpoint_key = "source_mysql"
      target_endpoint_key = "target_s3_parquet"
      table_mappings      = jsonencode({
        rules = [{
          rule-type = "selection"
          rule-id   = "1"
          rule-name = "include-all"
          object-locator = {
            schema-name = "%"
            table-name  = "%"
          }
          rule-action = "include"
        }]
      })
    }
  }

  tags = {
    Purpose = "data-lake-ingestion"
  }
}
```

### Example 4: Real-Time Streaming to Kafka

```hcl
module "kafka_streaming" {
  source = "terraform-aws-modules/dms/aws"

  # Replication instance
  repl_subnet_group_name       = "kafka-streaming"
  repl_subnet_group_subnet_ids = module.vpc.private_subnets
  repl_instance_class          = "dms.c5.2xlarge"
  repl_instance_id             = "kafka-streaming-instance"

  # Source endpoint
  endpoints = {
    source_postgres = {
      endpoint_id   = "postgres-source"
      endpoint_type = "source"
      engine_name   = "postgres"
      server_name   = module.aurora_postgresql.cluster_endpoint
      port          = 5432
      database_name = "app_database"
      username      = "dms_user"
      password      = data.aws_secretsmanager_secret_version.db_pass.secret_string
      ssl_mode      = "require"
    }

    target_kafka = {
      endpoint_id   = "kafka-target"
      endpoint_type = "target"
      engine_name   = "kafka"

      kafka_settings = {
        broker                         = join(",", module.msk_cluster.bootstrap_brokers)
        topic                          = "database-changes"
        message_format                 = "json"
        include_transaction_details    = true
        include_partition_value        = true
        partition_include_schema_table = true
        include_table_alter_operations = true
        include_control_details        = true
        message_max_bytes              = 1048576
      }
    }
  }

  # CDC replication task to Kafka
  replication_tasks = {
    postgres_to_kafka = {
      replication_task_id = "postgres-kafka-cdc"
      migration_type      = "cdc"
      source_endpoint_key = "source_postgres"
      target_endpoint_key = "target_kafka"
      start_replication_task = true
      table_mappings = jsonencode({
        rules = [{
          rule-type = "selection"
          rule-id   = "1"
          rule-name = "include-tables"
          object-locator = {
            schema-name = "public"
            table-name  = "%"
          }
          rule-action = "include"
        }]
      })
    }
  }

  tags = {
    Use-Case = "real-time-streaming"
  }
}
```

### Example 5: Serverless DMS Replication

```hcl
module "serverless_migration" {
  source = "terraform-aws-modules/dms/aws"

  # Replication subnet group
  repl_subnet_group_name       = "serverless-migration"
  repl_subnet_group_subnet_ids = module.vpc.database_subnets

  # Skip replication instance for serverless
  create_repl_instance = false

  # Endpoints
  endpoints = {
    source = {
      endpoint_id   = "serverless-source"
      endpoint_type = "source"
      engine_name   = "postgres"
      server_name   = "source-db.example.com"
      port          = 5432
      database_name = "sourcedb"
      username      = "postgres"
      password      = data.aws_secretsmanager_secret_version.source_pass.secret_string
    }

    target = {
      endpoint_id   = "serverless-target"
      endpoint_type = "target"
      engine_name   = "postgres"
      server_name   = module.aurora_postgresql_serverless.cluster_endpoint
      port          = 5432
      database_name = "targetdb"
      username      = "postgres"
      password      = data.aws_secretsmanager_secret_version.target_pass.secret_string
    }
  }

  # Serverless replication task
  replication_tasks = {
    serverless_task = {
      replication_task_id = "serverless-replication"
      migration_type      = "full-load-and-cdc"
      source_endpoint_key = "source"
      target_endpoint_key = "target"

      # Serverless configuration
      serverless_config = {
        max_capacity_units     = 4
        min_capacity_units     = 1
        multi_az               = true
        vpc_security_group_ids = [module.security_group.security_group_id]
      }

      table_mappings = jsonencode({
        rules = [{
          rule-type = "selection"
          rule-id   = "1"
          rule-name = "all-tables"
          object-locator = {
            schema-name = "%"
            table-name  = "%"
          }
          rule-action = "include"
        }]
      })
    }
  }

  tags = {
    Type = "serverless"
  }
}
```

### Example 6: Multi-Source Database Consolidation

```hcl
module "database_consolidation" {
  source = "terraform-aws-modules/dms/aws"

  # Replication subnet group
  repl_subnet_group_name       = "consolidation"
  repl_subnet_group_subnet_ids = module.vpc.database_subnets

  # High-capacity replication instance
  repl_instance_allocated_storage = 500
  repl_instance_class             = "dms.r5.xlarge"
  repl_instance_id                = "consolidation-instance"
  repl_instance_multi_az          = true

  # Multiple source endpoints
  endpoints = {
    source_mysql_1 = {
      endpoint_id   = "mysql-region-1"
      endpoint_type = "source"
      engine_name   = "mysql"
      server_name   = "mysql-1.example.com"
      port          = 3306
      database_name = "region1_db"
      username      = "dms_user"
      password      = data.aws_secretsmanager_secret_version.mysql1_pass.secret_string
    }

    source_mysql_2 = {
      endpoint_id   = "mysql-region-2"
      endpoint_type = "source"
      engine_name   = "mysql"
      server_name   = "mysql-2.example.com"
      port          = 3306
      database_name = "region2_db"
      username      = "dms_user"
      password      = data.aws_secretsmanager_secret_version.mysql2_pass.secret_string
    }

    source_postgres = {
      endpoint_id   = "postgres-legacy"
      endpoint_type = "source"
      engine_name   = "postgres"
      server_name   = "postgres.example.com"
      port          = 5432
      database_name = "legacy_db"
      username      = "dms_user"
      password      = data.aws_secretsmanager_secret_version.postgres_pass.secret_string
    }

    # Consolidated target
    target_aurora = {
      endpoint_id   = "aurora-consolidated"
      endpoint_type = "target"
      engine_name   = "aurora-postgresql"
      server_name   = module.aurora_postgresql.cluster_endpoint
      port          = 5432
      database_name = "consolidated_db"
      username      = "postgres"
      password      = data.aws_secretsmanager_secret_version.aurora_pass.secret_string
    }
  }

  # Multiple replication tasks
  replication_tasks = {
    mysql1_to_aurora = {
      replication_task_id = "mysql1-consolidation"
      migration_type      = "full-load-and-cdc"
      source_endpoint_key = "source_mysql_1"
      target_endpoint_key = "target_aurora"
      table_mappings      = jsonencode({
        rules = [{
          rule-type = "selection"
          rule-id   = "1"
          rule-name = "region1-tables"
          object-locator = {
            schema-name = "%"
            table-name  = "%"
          }
          rule-action = "include"
        }, {
          rule-type = "transformation"
          rule-id   = "2"
          rule-name = "add-region-prefix"
          rule-target = "table"
          object-locator = {
            schema-name = "%"
            table-name  = "%"
          }
          rule-action = "add-prefix"
          value       = "region1_"
        }]
      })
    }

    mysql2_to_aurora = {
      replication_task_id = "mysql2-consolidation"
      migration_type      = "full-load-and-cdc"
      source_endpoint_key = "source_mysql_2"
      target_endpoint_key = "target_aurora"
      table_mappings      = jsonencode({
        rules = [{
          rule-type = "selection"
          rule-id   = "1"
          rule-name = "region2-tables"
          object-locator = {
            schema-name = "%"
            table-name  = "%"
          }
          rule-action = "include"
        }, {
          rule-type = "transformation"
          rule-id   = "2"
          rule-name = "add-region-prefix"
          rule-target = "table"
          object-locator = {
            schema-name = "%"
            table-name  = "%"
          }
          rule-action = "add-prefix"
          value       = "region2_"
        }]
      })
    }

    postgres_to_aurora = {
      replication_task_id = "postgres-consolidation"
      migration_type      = "full-load-and-cdc"
      source_endpoint_key = "source_postgres"
      target_endpoint_key = "target_aurora"
      table_mappings      = jsonencode({
        rules = [{
          rule-type = "selection"
          rule-id   = "1"
          rule-name = "legacy-tables"
          object-locator = {
            schema-name = "public"
            table-name  = "%"
          }
          rule-action = "include"
        }]
      })
    }
  }

  # Event monitoring
  event_subscriptions = {
    tasks = {
      name              = "consolidation-task-events"
      enabled           = true
      sns_topic_arn     = aws_sns_topic.dms_alerts.arn
      source_type       = "replication-task"
      event_categories  = ["failure", "state change"]
    }
  }

  tags = {
    Purpose = "database-consolidation"
  }
}
```

### Example 7: Secure Migration with SSL Certificates

```hcl
module "secure_migration" {
  source = "terraform-aws-modules/dms/aws"

  # Replication instance
  repl_subnet_group_name       = "secure-migration"
  repl_subnet_group_subnet_ids = module.vpc.private_subnets
  repl_instance_class          = "dms.c5.large"
  repl_instance_id             = "secure-migration-instance"

  # SSL/TLS Certificates
  certificates = {
    source_cert = {
      certificate_id  = "source-db-certificate"
      certificate_pem = file("${path.module}/certs/source-ca.pem")
    }
  }

  # Endpoints with SSL
  endpoints = {
    source_postgres_ssl = {
      endpoint_id         = "postgres-source-ssl"
      endpoint_type       = "source"
      engine_name         = "postgres"
      server_name         = "secure-postgres.example.com"
      port                = 5432
      database_name       = "securedb"
      username            = "dms_user"
      password            = data.aws_secretsmanager_secret_version.db_pass.secret_string
      ssl_mode            = "verify-full"
      certificate_arn     = module.secure_migration.certificates["source_cert"].certificate_arn
    }

    target_aurora_ssl = {
      endpoint_id   = "aurora-target-ssl"
      endpoint_type = "target"
      engine_name   = "aurora-postgresql"
      server_name   = module.aurora_postgresql.cluster_endpoint
      port          = 5432
      database_name = "targetdb"
      username      = "postgres"
      password      = data.aws_secretsmanager_secret_version.aurora_pass.secret_string
      ssl_mode      = "require"
    }
  }

  # Replication task
  replication_tasks = {
    secure_replication = {
      replication_task_id = "secure-postgres-migration"
      migration_type      = "full-load-and-cdc"
      source_endpoint_key = "source_postgres_ssl"
      target_endpoint_key = "target_aurora_ssl"
      table_mappings      = jsonencode({
        rules = [{
          rule-type = "selection"
          rule-id   = "1"
          rule-name = "all-tables"
          object-locator = {
            schema-name = "%"
            table-name  = "%"
          }
          rule-action = "include"
        }]
      })
    }
  }

  tags = {
    Security = "high"
  }
}
```

## Best Practices

### Replication Instance Configuration

1. **Right-Size Instance Class**: Choose appropriate instance classes based on workload; use R5 instances for memory-intensive migrations, C5 for compute-intensive tasks
2. **Enable Multi-AZ for Production**: Always enable Multi-AZ deployment for production replication instances to ensure high availability during failures
3. **Allocate Sufficient Storage**: Provision adequate storage (100GB minimum) for transaction logs and cached changes during CDC replication
4. **Plan Maintenance Windows**: Schedule maintenance windows during low-traffic periods to minimize impact on replication performance
5. **Monitor Instance Metrics**: Track CPU utilization, freeable memory, and swap usage; scale up if CPU consistently exceeds 80% or memory is constrained
6. **Use Private Subnets**: Deploy replication instances in private subnets with NAT gateway for secure outbound connectivity
7. **Configure Security Groups**: Create dedicated security groups allowing inbound access only from DMS endpoints and monitoring tools

### Endpoint Configuration

1. **Use Secrets Manager**: Store database credentials in AWS Secrets Manager instead of hardcoding passwords in Terraform
2. **Verify Network Connectivity**: Test connectivity from VPC to source/target databases before configuring endpoints
3. **Enable SSL/TLS**: Use SSL mode "require" or "verify-full" for all database connections to encrypt data in transit
4. **Configure Extra Connection Attributes**: Tune database-specific settings like parallelLoadThreads, maxFileSize, or readTableSpaceName for optimal performance
5. **Test Endpoints Before Tasks**: Use DMS console "Test Connection" feature to validate endpoint configuration before creating replication tasks
6. **Use Service-Linked Roles**: For RDS and Aurora endpoints, leverage DMS service-linked roles for automatic credential rotation
7. **Document Endpoint Dependencies**: Maintain documentation of endpoint prerequisites including database users, permissions, and network requirements

### Replication Task Optimization

1. **Choose Appropriate Migration Type**: Use "full-load" for one-time migrations, "cdc" for ongoing replication, or "full-load-and-cdc" for minimal downtime migrations
2. **Implement Table Mapping Rules**: Use selection rules to filter unnecessary tables and transformation rules to rename or restructure data during migration
3. **Enable Parallel Load**: Configure parallelLoadThreads setting (up to 32) for large tables to improve full load performance
4. **Optimize LOB Handling**: Use "limited LOB mode" with appropriate LobMaxSize for better performance; avoid "full LOB mode" unless necessary
5. **Configure Target Table Preparation**: Use "DROP_AND_CREATE" for initial loads, "TRUNCATE_BEFORE_LOAD" for refreshes, or "DO_NOTHING" for incremental loads
6. **Break Large Migrations**: Split very large migrations into multiple tasks using table filtering to reduce complexity and improve manageability
7. **Enable Validation**: Turn on data validation for critical migrations to ensure data integrity, but be aware of performance impact
8. **Set Appropriate Task Settings**: Configure FullLoadSettings, ChangeProcessingDdlHandlingPolicy, and ErrorBehavior based on your requirements

### Performance Tuning

1. **Monitor Replication Lag**: Track CDCLatencySource and CDCLatencyTarget metrics; investigate if lag exceeds 60 seconds consistently
2. **Optimize Source Database**: On source databases, ensure proper indexing, disable unnecessary triggers, and allocate sufficient transaction log space
3. **Reduce Target Load**: Temporarily drop indexes and foreign keys on target during full load; recreate after completion
4. **Use Batch Apply**: Enable BatchApplyEnabled setting for targets that support it (like S3, Redshift) for better throughput
5. **Adjust Commit Rate**: Tune CommitRate and CommitTimeout settings to balance between latency and transactional consistency
6. **Monitor Network Bandwidth**: Ensure sufficient network bandwidth between source, DMS instance, and target; use VPC peering or Direct Connect for high-volume migrations
7. **Scale Vertically During Peak**: Temporarily scale up replication instance class during initial full load, then scale down for CDC phase

### Security and Compliance

1. **Apply IAM Permission Boundaries**: Use iam_role_permissions_boundary for delegated administration scenarios to limit privilege escalation
2. **Enable Encryption at Rest**: Configure encryption for replication instance storage using KMS keys for data at rest protection
3. **Use VPC Endpoints**: Leverage VPC endpoints for S3, Secrets Manager, and CloudWatch to keep traffic within AWS network
4. **Implement Least Privilege**: Grant minimum required permissions to DMS IAM roles; avoid using wildcard permissions
5. **Audit with CloudTrail**: Enable CloudTrail logging for all DMS API calls for security auditing and compliance
6. **Secure Endpoint Passwords**: Never store passwords in plaintext; use Secrets Manager with automatic rotation
7. **Restrict Public Access**: Set repl_instance_publicly_accessible to false for production instances; use bastion hosts or VPN for management access

### Monitoring and Alerting

1. **Enable CloudWatch Logging**: Configure detailed CloudWatch logs with appropriate log levels (INFO for production, DEBUG for troubleshooting)
2. **Set Up Event Subscriptions**: Create SNS subscriptions for replication-instance, replication-task, and endpoint events to get real-time alerts
3. **Monitor Key Metrics**: Track FullLoadThroughputRowsSource, FullLoadThroughputRowsTarget, CPUUtilization, and FreeableMemory
4. **Configure CloudWatch Alarms**: Set alarms for unhealthy tasks, high replication lag, instance CPU >80%, and memory <20%
5. **Use DMS Task Logs**: Regularly review task logs for warnings and errors even when tasks appear healthy
6. **Implement Custom Metrics**: Export DMS metrics to external monitoring tools for long-term trend analysis and capacity planning
7. **Test Alerting Channels**: Verify SNS subscriptions and alarm actions work correctly before production cutover

### Cost Optimization

1. **Stop Unused Instances**: Delete or stop replication instances when not actively migrating to avoid ongoing charges
2. **Right-Size for Workload**: Start with smaller instance classes and scale up only when metrics indicate resource constraints
3. **Use Serverless for Variable Workloads**: Consider DMS Serverless for intermittent or unpredictable migration workloads
4. **Optimize Storage Allocation**: Allocate only necessary storage; DMS charges for allocated storage even if unused
5. **Clean Up After Migration**: Delete endpoints, tasks, instances, and subnet groups after successful migration completion
6. **Monitor Data Transfer Costs**: Track inter-AZ and inter-region data transfer charges; keep source and target in same region when possible
7. **Leverage Savings Plans**: For long-running replication instances, consider compute savings plans for cost reduction

### High Availability and Disaster Recovery

1. **Deploy Multi-AZ**: Enable Multi-AZ for automatic failover to standby instance in case of infrastructure failure
2. **Plan for Failover**: Test failover scenarios; understand that failover takes 5-10 minutes and in-flight transactions may be lost
3. **Implement Redundant Tasks**: For critical replications, consider running parallel tasks in different regions
4. **Backup Task Configurations**: Export and version control table mappings and task settings for disaster recovery
5. **Monitor Health Checks**: Set up health checks for replication tasks and implement automated restart procedures
6. **Document Recovery Procedures**: Maintain runbooks for common failure scenarios including instance failures, endpoint connectivity issues, and task errors

### Migration Planning and Execution

1. **Conduct Pre-Migration Assessment**: Use DMS Fleet Advisor or AWS SCT to assess source databases and estimate migration complexity
2. **Test in Non-Production**: Always test migration workflow in dev/staging environment before production cutover
3. **Perform Dry Runs**: Run full-load migrations multiple times to validate table mappings, task settings, and performance
4. **Plan Cutover Windows**: Schedule cutover during maintenance windows with adequate buffer for unexpected issues
5. **Implement Rollback Plan**: Have tested rollback procedures in case migration encounters critical issues
6. **Validate Data Integrity**: Use DMS validation feature or custom scripts to verify row counts and data consistency post-migration
7. **Monitor Post-Migration**: Continue monitoring replication lag and task health for at least 72 hours after cutover

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-dms
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/dms/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-dms/tree/master/examples
- **AWS DMS Documentation**: https://docs.aws.amazon.com/dms/latest/userguide/Welcome.html
- **AWS DMS Best Practices**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_BestPractices.html
- **DMS Source Databases**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.html
- **DMS Target Databases**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.html
- **DMS Task Settings**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TaskSettings.html
- **DMS Table Mapping**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TableMapping.html
- **DMS Monitoring with CloudWatch**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Monitoring.html
- **DMS Serverless**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Serverless.html
- **AWS Schema Conversion Tool**: https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Welcome.html
- **AWS DMS Pricing**: https://aws.amazon.com/dms/pricing/
- **DMS Security**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Security.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Database Compatibility**: Verify source and target database engines are supported by DMS and compatible for the chosen migration type
2. **Network Prerequisites**: Ensure VPC, subnets, security groups, and routing are configured before creating DMS resources
3. **IAM Role Timing**: DMS service-linked roles (dms-vpc-role, dms-cloudwatch-logs-role) must be created before first use in an account; set create_iam_roles = true for first deployment
4. **Secrets Management**: Use data.aws_secretsmanager_secret_version or similar for endpoint passwords; never hardcode credentials
5. **Task Dependencies**: Replication tasks depend on endpoints and replication instance; use implicit dependencies or explicit depends_on
6. **Migration Type Selection**: "full-load" is for one-time, "cdc" requires existing data, "full-load-and-cdc" is for minimal downtime; choose appropriately
7. **Table Mappings JSON**: table_mappings must be valid JSON string; use jsonencode() function for complex mapping rules
8. **Task Settings JSON**: replication_task_settings must be valid JSON; incorrect JSON causes task creation to fail without clear errors
9. **Serverless vs Instance**: Serverless tasks don't require replication instance; set create_repl_instance = false when using serverless_config
10. **S3 Endpoint Considerations**: S3 endpoints require special permissions; use create_access_iam_role = true with access_target_s3_bucket_arns
11. **Multi-AZ Costs**: Multi-AZ doubles instance costs but provides automatic failover; evaluate based on availability requirements
12. **Endpoint Testing**: Always test endpoint connectivity before creating tasks; use DMS console or AWS CLI test-connection command
13. **CDC Prerequisites**: Source databases must have binary logging enabled for CDC; PostgreSQL needs logical replication, MySQL needs binlog_format=ROW
14. **Task State Management**: Use start_replication_task parameter cautiously; tasks may fail to start if endpoints aren't ready
15. **Resource Cleanup**: Always delete tasks before deleting endpoints or instances; dependency order matters for clean destruction
