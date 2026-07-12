# Terraform AWS DMS Module

## Module Information

- **Module Name**: `dms`
- **Module ID**: `terraform-aws-modules/dms/aws`
- **Source**: `terraform-aws-modules/dms/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-dms
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/dms/aws/latest
- **Latest Version**: 2.6.1
- **Purpose**: Terraform module to create AWS Database Migration Service (DMS) resources for database migrations and continuous data replication
- **Service**: AWS Database Migration Service (AWS DMS)
- **Category**: Database, Migration, Data Integration
- **Keywords**: dms, database-migration, cdc, change-data-capture, replication-instance, replication-task, serverless-replication, endpoint, s3-endpoint, full-load, multi-az, mysql, postgresql, oracle, sql-server, aurora, kafka, kinesis
- **Use For**: database migration to AWS, cross-platform/heterogeneous database migrations, continuous data replication for disaster recovery, legacy database modernization, real-time streaming to Kafka/Kinesis, data lake population from operational databases (S3), consolidating multiple source databases into one target, minimal-downtime database version upgrades

## Description

The AWS DMS Terraform module creates and manages Database Migration Service resources used to move relational databases, data warehouses, and other data stores into or between AWS with minimal downtime. It provisions the replication subnet group, replication instance (or DMS Serverless replication config), source/target endpoints — including a specialized S3 endpoint resource — replication tasks, event subscriptions, SSL/TLS certificates, and the IAM roles DMS requires to operate (`dms-vpc-role`, `dms-cloudwatch-logs-role`, `dms-access-for-endpoint`), all from a single root module (no submodules).

The module is built around key-based maps rather than fixed arguments: `endpoints`, `s3_endpoints`, `replication_tasks`, `event_subscriptions`, and `certificates` each accept a map of objects, letting a single module call create any combination of resources — from one source/target/task to many endpoints feeding multiple tasks. Endpoints and tasks are cross-referenced by map key (`source_endpoint_key` / `target_endpoint_key` in a task refer to keys in `endpoints`/`s3_endpoints`), and tasks can alternatively reference externally-created endpoints via `source_endpoint_arn` / `target_endpoint_arn`. Migration types (`full-load`, `cdc`, `full-load-and-cdc`) and detailed task settings/table mappings (typically supplied as JSON via `file()` or `jsonencode()`) control how data flows from source to target.

DMS Serverless is supported by adding a `serverless_config` block inside a `replication_tasks` entry instead of provisioning a classic replication instance (set `create_repl_instance = false`); this provisions an `aws_dms_replication_config` resource with automatic capacity scaling, surfaced via the `serverless_replication_tasks` output. The module also optionally creates a dedicated "access" IAM role (`create_access_iam_role`) with a generated policy granting access to Secrets Manager secrets, S3 buckets, KMS keys, Kinesis streams, Elasticsearch/OpenSearch domains, and DynamoDB tables used by endpoints — plus support for fully custom IAM policy statements via `access_iam_statements`.

## Key Features

- **Replication Instance Management**: Create classic DMS replication instances with configurable class, storage, engine version, Multi-AZ, and network type (`IPV4`/`DUAL`)
- **DMS Serverless**: Provision `aws_dms_replication_config` (serverless replication) by attaching `serverless_config` to a replication task and skipping the instance
- **Subnet Group Configuration**: Create a replication subnet group for network isolation, or reuse an existing one via `repl_instance_subnet_group_id`
- **Broad Endpoint Support**: Configure source/target endpoints for 15+ engines (Oracle, SQL Server, PostgreSQL, MySQL, MariaDB, Aurora, Aurora PostgreSQL, MongoDB, Db2, SAP ASE, Redshift, DynamoDB, OpenSearch, Kafka/MSK, Kinesis, Redis) through the generic `endpoints` map
- **Dedicated S3 Endpoint Resource**: Separate `s3_endpoints` map targeting `aws_dms_s3_endpoint`, with data format (CSV/Parquet/ORC), compression, and date-partitioning options
- **Multi-Resource Combinations**: Map-and-key design (`endpoints`, `s3_endpoints`, `replication_tasks`, `event_subscriptions`, `certificates`) lets one module call manage arbitrarily complex topologies (multiple sources, multiple targets, many tasks)
- **IAM Role Automation**: Auto-creates `dms-vpc-role`, `dms-cloudwatch-logs-role`, and `dms-access-for-endpoint` service roles (`create_iam_roles`), plus an optional dedicated "access" IAM role/policy for endpoint access to Secrets Manager, S3, KMS, Kinesis, Elasticsearch, and DynamoDB
- **Event Subscriptions**: SNS-based event subscriptions for replication-instance, replication-task, and replication-config event sources
- **Certificate Management**: Create and manage SSL/TLS certificates (`aws_dms_certificate`) for secure endpoint connections
- **Secrets Manager Integration**: Endpoints support `secrets_manager_arn` for credential retrieval instead of inline `username`/`password`
- **Redshift Target Permissions**: `enable_redshift_target_permissions` lets `redshift.amazonaws.com` assume the access-for-endpoint role
- **Conditional Resource Creation**: Feature flags (`create`, `create_repl_instance`, `create_repl_subnet_group`, `create_iam_roles`, `create_access_iam_role`, `create_access_policy`) control which components get created
- **Configurable Timeouts**: Per-resource timeout blocks for replication instance, replication config (serverless), and event subscription operations
- **Comprehensive Tagging**: Global `tags` plus per-resource-type tag maps (`repl_instance_tags`, `repl_subnet_group_tags`, `iam_role_tags`, `access_iam_role_tags`)

## Main Use Cases

1. **Database Migration to AWS**: Migrate on-premises or cloud databases to AWS managed database services with minimal downtime
2. **Heterogeneous Database Migrations**: Migrate between different database engines (e.g., Oracle to PostgreSQL, SQL Server to Aurora)
3. **Continuous Data Replication**: Set up ongoing CDC replication for disaster recovery, read replicas, or multi-region deployments
4. **Database Modernization**: Migrate from commercial databases to open-source alternatives for cost optimization
5. **Data Lake Population**: Continuously stream database changes into S3 in Parquet or other analytics-friendly formats
6. **Real-Time Streaming**: Replicate data to Kafka (MSK) or Kinesis for real-time processing and analytics pipelines
7. **Database Consolidation**: Migrate and consolidate multiple source databases into a single target database or warehouse
8. **Serverless/Variable Workloads**: Use DMS Serverless for intermittent or unpredictable migration workloads without managing an instance
9. **Hybrid Cloud Synchronization**: Maintain synchronized data between on-premises and cloud databases during gradual migration
10. **Zero-Downtime Upgrades**: Perform database version upgrades using parallel full-load-and-cdc replication

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `tags` | `map(string)` | `{}` | Map of tags to apply to all resources |
| `create_iam_roles` | `bool` | `true` | Determines whether to create required DMS service IAM roles (`dms-vpc-role`, `dms-cloudwatch-logs-role`, `dms-access-for-endpoint`) |
| `iam_role_permissions_boundary` | `string` | `null` | ARN of the policy used as permissions boundary for DMS service IAM roles |
| `iam_role_tags` | `map(string)` | `{}` | Additional tags for DMS service IAM roles |
| `enable_redshift_target_permissions` | `bool` | `false` | Permits `redshift.amazonaws.com` to assume the `dms-access-for-endpoint` role |
| `create_repl_subnet_group` | `bool` | `true` | Determines whether to create the replication subnet group |
| `repl_subnet_group_name` | `string` | `null` | Name of the replication subnet group (stored lowercase) |
| `repl_subnet_group_subnet_ids` | `list(string)` | `[]` | List of EC2 subnet IDs for the replication subnet group |
| `create_repl_instance` | `bool` | `true` | Determines whether to create a replication instance (set `false` when using DMS Serverless) |
| `repl_instance_class` | `string` | `null` | Compute/memory class of the replication instance, e.g. `dms.t3.medium` |
| `repl_instance_id` | `string` | `null` | Replication instance identifier (stored lowercase) |
| `repl_instance_allocated_storage` | `number` | `null` | Storage in GB for the instance (min 5, max 6144, AWS default 50) |
| `repl_instance_multi_az` | `bool` | `null` | Multi-AZ deployment; mutually exclusive with `repl_instance_availability_zone` |
| `repl_instance_publicly_accessible` | `bool` | `null` | Whether the replication instance gets a public IP |
| `repl_instance_vpc_security_group_ids` | `list(string)` | `null` | VPC security group IDs for the replication instance |
| `repl_instance_engine_version` | `string` | `null` | DMS engine version for the replication instance |
| `repl_instance_kms_key_arn` | `string` | `null` | KMS key ARN used to encrypt replication instance storage/connection params |
| `repl_instance_subnet_group_id` | `string` | `null` | Use an existing subnet group instead of creating one |
| `endpoints` | `any` | `{}` | Map of endpoint definitions (`aws_dms_endpoint`) keyed by logical name |
| `s3_endpoints` | `any` | `{}` | Map of S3 endpoint definitions (`aws_dms_s3_endpoint`) keyed by logical name |
| `replication_tasks` | `any` | `{}` | Map of replication task definitions; include `serverless_config` for DMS Serverless |
| `event_subscriptions` | `any` | `{}` | Map of event subscription definitions (`aws_dms_event_subscription`) |
| `certificates` | `map(any)` | `{}` | Map of SSL/TLS certificate definitions (`aws_dms_certificate`) |
| `create_access_iam_role` | `bool` | `true` | Determines whether to create the dedicated "access" IAM role for endpoints |
| `access_iam_role_name` | `string` | `null` | Name (or prefix) for the access IAM role |
| `access_secret_arns` | `list(string)` | `[]` | Secrets Manager secret ARNs the access role may read |
| `access_source_s3_bucket_arns` | `list(string)` | `[]` | Source S3 bucket ARNs the access role may read |
| `access_target_s3_bucket_arns` | `list(string)` | `[]` | Target S3 bucket ARNs the access role may write |
| `access_kms_key_arns` | `list(string)` | `[]` | KMS key ARNs the access role is permitted to decrypt |
| `access_iam_statements` | `any` | `{}` | Additional custom IAM policy statements for the access role |

## Main Outputs

| Output | Description |
|--------|-------------|
| `replication_subnet_group_id` | ID of the replication subnet group |
| `replication_instance_arn` | ARN of the replication instance |
| `replication_instance_private_ips` / `replication_instance_public_ips` | IP addresses of the replication instance |
| `endpoints` | Map of created endpoints and their full attributes (sensitive) |
| `s3_endpoints` | Map of created S3 endpoints and their full attributes (sensitive) |
| `replication_tasks` | Map of created (classic) replication tasks and their attributes |
| `serverless_replication_tasks` | Map of created DMS Serverless replication configs and their attributes |
| `event_subscriptions` | Map of created event subscriptions |
| `certificates` | Map of created certificates (sensitive) |
| `dms_vpc_iam_role_arn` / `dms_cloudwatch_logs_iam_role_arn` / `dms_access_for_endpoint_iam_role_arn` | ARNs of the DMS service IAM roles |
| `access_iam_role_arn` / `access_iam_role_name` | ARN/name of the dedicated endpoint access IAM role |

## Usage Examples

### Example 1: Basic Database Migration (PostgreSQL to MySQL)

```hcl
module "database_migration_basic" {
  source  = "terraform-aws-modules/dms/aws"
  version = "~> 2.0"

  # Replication subnet group
  repl_subnet_group_name        = "basic-migration"
  repl_subnet_group_description = "DMS replication subnet group"
  repl_subnet_group_subnet_ids  = module.vpc.database_subnets

  # Replication instance
  repl_instance_allocated_storage      = 100
  repl_instance_class                  = "dms.t3.medium"
  repl_instance_id                     = "basic-migration-instance"
  repl_instance_multi_az               = false
  repl_instance_vpc_security_group_ids = [module.security_group.security_group_id]

  # Source and target endpoints
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
      table_mappings = jsonencode({
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

### Example 2: Continuous CDC Replication with Secrets Manager and Event Subscriptions

```hcl
module "database_replication_cdc" {
  source  = "terraform-aws-modules/dms/aws"
  version = "~> 2.0"

  repl_subnet_group_name       = "cdc-replication"
  repl_subnet_group_subnet_ids = module.vpc.database_subnets

  # Multi-AZ replication instance
  repl_instance_allocated_storage            = 200
  repl_instance_class                        = "dms.c5.xlarge"
  repl_instance_id                           = "cdc-replication-instance"
  repl_instance_multi_az                     = true
  repl_instance_publicly_accessible          = false
  repl_instance_preferred_maintenance_window = "sun:05:00-sun:06:00"

  # Access role for Secrets Manager
  create_access_iam_role = true
  access_secret_arns = [
    module.secrets_manager_oracle.secret_arn,
    module.secrets_manager_aurora.secret_arn,
  ]

  endpoints = {
    source_oracle = {
      endpoint_id                 = "source-oracle"
      endpoint_type                = "source"
      engine_name                  = "oracle"
      server_name                  = "oracle-prod.example.com"
      port                         = 1521
      database_name                = "ORCL"
      secrets_manager_arn          = module.secrets_manager_oracle.secret_arn
      extra_connection_attributes  = "useLogminerReader=N;useBfile=Y"
    }

    target_aurora = {
      endpoint_id          = "target-aurora-postgres"
      endpoint_type        = "target"
      engine_name          = "aurora-postgresql"
      server_name          = module.aurora_postgresql.cluster_endpoint
      port                 = 5432
      database_name        = "postgres"
      secrets_manager_arn  = module.secrets_manager_aurora.secret_arn
      ssl_mode             = "require"
    }
  }

  replication_tasks = {
    oracle_to_aurora_cdc = {
      replication_task_id  = "oracle-aurora-cdc"
      migration_type       = "full-load-and-cdc"
      source_endpoint_key  = "source_oracle"
      target_endpoint_key  = "target_aurora"
      replication_task_settings = file("${path.module}/configs/task_settings.json")
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

  event_subscriptions = {
    replication_task = {
      name                          = "cdc-replication-events"
      enabled                       = true
      sns_topic_arn                 = aws_sns_topic.dms_events.arn
      source_type                   = "replication-task"
      task_event_subscription_keys  = ["oracle_to_aurora_cdc"]
      event_categories              = ["failure", "state change", "configuration change"]
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
  source  = "terraform-aws-modules/dms/aws"
  version = "~> 2.0"

  repl_subnet_group_name       = "s3-datalake"
  repl_subnet_group_subnet_ids = module.vpc.private_subnets

  repl_instance_class = "dms.c5.large"
  repl_instance_id    = "s3-datalake-instance"

  # Access role for the S3 target
  create_access_iam_role       = true
  access_iam_role_name         = "dms-s3-access"
  access_target_s3_bucket_arns = [module.s3_datalake.s3_bucket_arn]

  endpoints = {
    source_mysql = {
      endpoint_id          = "mysql-source"
      endpoint_type        = "source"
      engine_name          = "mysql"
      server_name          = module.rds_mysql.db_instance_address
      port                 = 3306
      database_name        = "production"
      secrets_manager_arn  = module.secrets_manager_mysql.secret_arn
    }
  }

  s3_endpoints = {
    target_s3_parquet = {
      endpoint_id                      = "s3-parquet-target"
      endpoint_type                    = "target"
      bucket_name                      = module.s3_datalake.s3_bucket_id
      bucket_folder                    = "mysql-exports"
      compression_type                 = "GZIP"
      data_format                      = "parquet"
      date_partition_enabled           = true
      date_partition_delimiter         = "SLASH"
      parquet_timestamp_in_millisecond = true
      parquet_version                  = "parquet-2-0"
      service_access_role_arn          = module.database_migration_service.access_iam_role_arn
    }
  }

  replication_tasks = {
    mysql_to_s3 = {
      replication_task_id  = "mysql-to-s3-parquet"
      migration_type       = "full-load-and-cdc"
      source_endpoint_key  = "source_mysql"
      target_endpoint_key  = "target_s3_parquet"
      table_mappings = jsonencode({
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

### Example 4: Real-Time Streaming to Kafka (MSK)

```hcl
module "kafka_streaming" {
  source  = "terraform-aws-modules/dms/aws"
  version = "~> 2.0"

  repl_subnet_group_name       = "kafka-streaming"
  repl_subnet_group_subnet_ids = module.vpc.private_subnets
  repl_instance_class          = "dms.c5.2xlarge"
  repl_instance_id             = "kafka-streaming-instance"

  endpoints = {
    source_postgres = {
      endpoint_id          = "postgres-source"
      endpoint_type        = "source"
      engine_name          = "postgres"
      server_name          = module.aurora_postgresql.cluster_endpoint
      port                 = 5432
      database_name        = "app_database"
      secrets_manager_arn  = module.secrets_manager_postgres.secret_arn
      ssl_mode             = "require"
    }

    target_kafka = {
      endpoint_id   = "kafka-target"
      endpoint_type = "target"
      engine_name   = "kafka"

      kafka_settings = {
        broker                          = join(",", module.msk_cluster.bootstrap_brokers)
        topic                           = "database-changes"
        message_format                  = "json"
        include_transaction_details     = true
        include_partition_value         = true
        partition_include_schema_table  = true
        include_table_alter_operations  = true
        include_control_details         = true
      }
    }
  }

  replication_tasks = {
    postgres_to_kafka = {
      replication_task_id     = "postgres-kafka-cdc"
      migration_type          = "cdc"
      source_endpoint_key     = "source_postgres"
      target_endpoint_key     = "target_kafka"
      start_replication_task  = true
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

### Example 5: DMS Serverless Replication

```hcl
module "serverless_migration" {
  source  = "terraform-aws-modules/dms/aws"
  version = "~> 2.0"

  repl_subnet_group_name       = "serverless-migration"
  repl_subnet_group_subnet_ids = module.vpc.database_subnets

  # No classic replication instance for serverless
  create_repl_instance = false

  endpoints = {
    source = {
      endpoint_id          = "serverless-source"
      endpoint_type        = "source"
      engine_name          = "postgres"
      server_name          = "source-db.example.com"
      port                 = 5432
      database_name        = "sourcedb"
      secrets_manager_arn  = module.secrets_manager_source.secret_arn
    }

    target = {
      endpoint_id          = "serverless-target"
      endpoint_type        = "target"
      engine_name          = "postgres"
      server_name          = module.aurora_postgresql_serverless.cluster_endpoint
      port                 = 5432
      database_name        = "targetdb"
      secrets_manager_arn  = module.secrets_manager_target.secret_arn
    }
  }

  # Replication task with serverless_config creates aws_dms_replication_config
  replication_tasks = {
    serverless_task = {
      replication_task_id  = "serverless-replication"
      migration_type       = "full-load-and-cdc"
      source_endpoint_key  = "source"
      target_endpoint_key  = "target"

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

## Supported Database Engines

### Source and Target (Bidirectional)
- Aurora MySQL / Aurora PostgreSQL
- MySQL / MariaDB
- PostgreSQL
- Oracle
- SQL Server
- MongoDB
- Amazon S3 (via dedicated `s3_endpoints`)

### Target Only
- Amazon Redshift
- Amazon Kinesis Data Streams
- Amazon DynamoDB
- Amazon OpenSearch (Elasticsearch)
- Apache Kafka (Amazon MSK)
- Redis

## Best Practices

### Replication Instance and Serverless Configuration
1. **Right-Size Instance Class**: Use memory-optimized (R5/R6) classes for large CDC caches, compute-optimized (C5/C6) for high-throughput full loads
2. **Enable Multi-AZ for Production**: Set `repl_instance_multi_az = true` (or `serverless_config.multi_az = true`) for production workloads to ensure automatic failover
3. **Prefer Serverless for Variable Load**: Use DMS Serverless (`create_repl_instance = false` + `serverless_config`) for intermittent or unpredictable migrations to avoid managing/right-sizing an instance
4. **Allocate Sufficient Storage**: Provision enough `repl_instance_allocated_storage` (100GB+ typical) for transaction logs and CDC caches
5. **Restrict Public Access**: Keep `repl_instance_publicly_accessible = false` for production; access via bastion/VPN inside the VPC
6. **Encrypt at Rest**: Set `repl_instance_kms_key_arn` to a customer-managed KMS key instead of relying on the default AWS-managed key

### Endpoint Configuration
1. **Use Secrets Manager**: Prefer `secrets_manager_arn` over inline `username`/`password`; grant access via `access_secret_arns` on the module's access IAM role
2. **Enable SSL/TLS**: Set `ssl_mode` to `require` or `verify-full` for all database connections
3. **Reference by Key**: Use the logical map key (`source_endpoint_key` / `target_endpoint_key`) to link `endpoints`/`s3_endpoints` entries to `replication_tasks`; use `source_endpoint_arn`/`target_endpoint_arn` only for endpoints created outside the module
4. **Tune Connection Attributes**: Use `extra_connection_attributes` for engine-specific tuning (e.g., `parallelLoadThreads`, `heartbeatFrequency`)

### Replication Task Design
1. **Choose the Right Migration Type**: `full-load` for one-time migrations, `cdc` for ongoing replication (source must already have matching data), `full-load-and-cdc` for minimal-downtime cutovers
2. **Externalize Task Settings and Mappings**: Load `replication_task_settings` and `table_mappings` via `file()`/`jsonencode()` rather than inlining large JSON blocks
3. **Filter with Table Mappings**: Use `selection` rules to include only needed schemas/tables and `transformation` rules to rename or restructure data in transit
4. **Split Large Migrations**: Break very large migrations into multiple tasks by table/schema filtering for easier operations and troubleshooting

### Security
1. **Least-Privilege Access Role**: Scope `access_secret_arns`, `access_source_s3_bucket_arns`, `access_target_s3_bucket_arns`, `access_kms_key_arns`, etc. to only the resources each endpoint needs; use `access_iam_statements` for anything not covered by the built-in variables
2. **Apply Permissions Boundaries**: Set `iam_role_permissions_boundary` / `access_iam_role_permissions_boundary` for delegated-administration environments
3. **Never Hardcode Passwords**: Store credentials in Secrets Manager; avoid plaintext `password` values in Terraform state
4. **Audit with CloudTrail**: Enable CloudTrail for all DMS API activity to support security review and compliance

### Monitoring and Operations
1. **Enable Event Subscriptions**: Subscribe to `replication-instance`, `replication-task`, and (for serverless) `replication-config` events via SNS to catch failures and state changes in real time
2. **Enable Detailed Logging**: Turn on `Logging.EnableLogging` in task settings for CloudWatch Logs visibility during troubleshooting
3. **Watch Replication Lag**: Monitor `CDCLatencySource`/`CDCLatencyTarget` CloudWatch metrics; investigate sustained lag
4. **Clean Up After Migration**: Delete tasks before endpoints/instances, and remove one-time migration resources after cutover to avoid ongoing charges

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-dms
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/dms/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-dms/tree/master/examples
- **AWS DMS Documentation**: https://docs.aws.amazon.com/dms/latest/userguide/Welcome.html
- **AWS DMS Best Practices**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_BestPractices.html
- **DMS Task Settings Reference**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TaskSettings.html
- **DMS Table Mapping Reference**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TableMapping.html
- **DMS Serverless**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Serverless.html
- **AWS DMS Pricing**: https://aws.amazon.com/dms/pricing/
- **DMS Security**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Security.html

## Notes for AI Agents

When using this module in automated workflows:

1. **No Submodules**: All functionality (instance, endpoints, tasks, event subscriptions, certificates, IAM roles) lives in the root module — there is nothing under `//modules/*` to reference
2. **IAM Role Timing**: DMS service-linked roles (`dms-vpc-role`, `dms-cloudwatch-logs-role`) are account-wide and only need to be created once; set `create_iam_roles = true` on first deployment, `false` on subsequent module calls in the same account to avoid `EntityAlreadyExists` errors
3. **Secrets Management**: Prefer `secrets_manager_arn` on endpoints over inline `username`/`password`; grant the module's access role read access via `access_secret_arns`
4. **Serverless vs Instance**: DMS Serverless tasks don't need a replication instance — set `create_repl_instance = false` and add `serverless_config` inside the `replication_tasks` entry; the resulting resource is `aws_dms_replication_config`, surfaced via the `serverless_replication_tasks` output (not `replication_tasks`)
5. **Endpoint Cross-Referencing**: Use the map key from `endpoints`/`s3_endpoints` in a task's `source_endpoint_key`/`target_endpoint_key`; use `source_endpoint_arn`/`target_endpoint_arn` only when the endpoint was created outside this module call
6. **Table Mappings and Task Settings are JSON Strings**: `table_mappings` and `replication_task_settings` must be valid JSON (via `jsonencode()` or `file()`); malformed JSON fails task creation with unclear errors
7. **S3 Endpoints Require Their Own Map**: S3 source/target endpoints go in `s3_endpoints`, not `endpoints`; they also need `create_access_iam_role = true` with `access_source_s3_bucket_arns`/`access_target_s3_bucket_arns` set
8. **CDC Prerequisites**: Source databases must support change capture before `cdc`/`full-load-and-cdc` tasks work — PostgreSQL needs logical replication enabled, MySQL needs `binlog_format=ROW`, Oracle needs supplemental logging
9. **Instance/Subnet Group IDs Must Be Lowercase**: `repl_instance_id` and `repl_subnet_group_name` are stored as lowercase strings; uppercase input causes plan/apply diffs or failures
10. **Multi-AZ vs Availability Zone**: `repl_instance_multi_az = true` and `repl_instance_availability_zone` are mutually exclusive — set only one
11. **Storage Bounds**: `repl_instance_allocated_storage` must be between 5 and 6144 GB
12. **Resource Deletion Order**: Delete/replace tasks before endpoints or the replication instance; the module's implicit dependency graph handles this on `apply`, but manual `terraform destroy -target` should follow the same order
13. **Provider Requirements**: Requires Terraform `>= 1.0`, AWS provider `>= 5.96`, and the `time` provider `>= 0.9` (used internally for IAM role propagation delay via `time_sleep`)
