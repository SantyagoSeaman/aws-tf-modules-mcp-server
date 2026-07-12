# Terraform AWS RDS Module

## Module Information

- **Module Name**: `rds`
- **Module ID**: `terraform-aws-modules/rds/aws`
- **Source**: `terraform-aws-modules/rds/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest
- **Latest Version**: 7.2.0
- **Purpose**: Creates and manages a single AWS RDS database instance (MySQL, PostgreSQL, MariaDB, Oracle, or SQL Server) with full control over storage, networking, security, monitoring, and high-availability configuration
- **Service**: AWS RDS (Amazon Relational Database Service)
- **Category**: Database, Managed Services
- **Keywords**: rds, relational-database, database, mysql, postgresql, mariadb, oracle, sqlserver, multi-az, read-replica, backup, encryption, kms, performance-insights, secrets-manager, blue-green-deployment, iam-authentication
- **Use For**: production relational databases, application backends, on-premises database migration, read-heavy workloads with replicas, high-availability database systems, cross-region disaster recovery, near-zero-downtime engine upgrades, dev/test database environments, legacy Oracle/SQL Server modernization

## Description

This Terraform module deploys and manages a single Amazon RDS database instance, supporting MySQL, PostgreSQL, MariaDB, Oracle, and Microsoft SQL Server engines. It is built from six composable submodules — `db_instance`, `db_subnet_group`, `db_parameter_group`, `db_option_group`, `db_instance_role_association`, and `db_instance_automated_backups_replication` — which the root module wires together but which can also be invoked independently to manage resources outside the primary instance lifecycle. (For Aurora clusters, use the separate `terraform-aws-modules/rds-aurora/aws` module instead.)

The module covers deployment patterns ranging from a single dev instance to production-grade Multi-AZ deployments with automatic failover, same-region or cross-region read replicas, and RDS Blue/Green Deployments for low-downtime major-version or parameter upgrades. It supports restoring from a snapshot, point-in-time recovery, and S3-based import of MySQL data (Percona Xtrabackup). Storage can autoscale (`max_allocated_storage`) and use gp2/gp3/io1/io2 volumes, including dedicated log volumes for I/O-intensive workloads.

Security and operability are first-class: storage encryption via AWS KMS is enabled by default, master credentials are managed through Secrets Manager (with optional automatic rotation) rather than stored in plaintext, and IAM database authentication is available for token-based access. Enhanced Monitoring, Performance/Database Insights, and CloudWatch Logs exports provide operational visibility. The module explicitly does **not** create security groups — those must be provisioned separately (e.g. with `terraform-aws-security-group`) and referenced via `vpc_security_group_ids`.

## Key Features

- **Five Database Engines**: MySQL, PostgreSQL, MariaDB, Oracle (SE2/EE), and SQL Server (Express/Web/Standard/Enterprise) with per-engine parameter and option groups
- **Six Composable Submodules**: `db_instance`, `db_subnet_group`, `db_parameter_group`, `db_option_group`, `db_instance_role_association`, `db_instance_automated_backups_replication` — usable together or standalone
- **Multi-AZ High Availability**: Synchronous standby with automatic failover across Availability Zones
- **Read Replicas**: Same-region or cross-region replicas via `replicate_source_db`, including encrypted replicas with a destination KMS key
- **Blue/Green Deployments**: Near-zero-downtime engine and configuration upgrades via `blue_green_update`
- **Automated & Managed Backups**: Configurable retention (0-35 days), custom backup windows, snapshot and point-in-time restore
- **Cross-Region Backup Replication**: `db_instance_automated_backups_replication` submodule replicates automated backups to a DR region
- **Flexible Storage**: gp2, gp3, io1, io2 with Storage Autoscaling (`max_allocated_storage`) and Dedicated Log Volume support
- **Encryption at Rest**: KMS-backed `storage_encrypted` enabled by default, with customer-managed key support
- **Secrets Manager Integration**: `manage_master_user_password` (default) with optional automatic secret rotation schedule
- **Write-Only Password Support**: `password_wo`/`password_wo_version` ephemeral attributes for self-managed passwords without persisting plaintext in state (the legacy `password` variable has been removed)
- **IAM Database Authentication**: Token-based authentication via `iam_database_authentication_enabled`
- **Enhanced Monitoring & Insights**: OS-level metrics (1-60s interval) plus query-level Performance Insights / Database Insights (`standard` or `advanced` mode)
- **CloudWatch Log Exports**: Ship engine logs (error, slow query, audit, general, postgresql, upgrade, etc.) with optional dedicated log groups
- **S3 Import & Point-in-Time Restore**: Restore MySQL from a Percona Xtrabackup dump in S3, or restore any engine from a backup at a point in time
- **Self-Managed Active Directory**: Domain-join support for SQL Server/Oracle authentication
- **Conditional Resource Creation**: `create_db_instance`, `create_db_subnet_group`, `create_db_parameter_group`, `create_db_option_group` flags let each piece be created, reused, or skipped independently

## Main Use Cases

1. **Production Databases**: Highly available, managed relational database backends for applications
2. **Database Migration**: Moving on-premises MySQL/PostgreSQL/Oracle/SQL Server databases to AWS
3. **Read-Heavy Workloads**: Primary instance with read replicas to distribute query traffic
4. **High-Availability Systems**: Multi-AZ deployments with automatic failover
5. **Disaster Recovery**: Cross-region read replicas and automated backup replication for business continuity
6. **Near-Zero-Downtime Upgrades**: Blue/Green Deployments for major engine or parameter changes
7. **Development & Testing**: Isolated, low-cost database instances for non-production environments
8. **Compliance-Driven Workloads**: Encryption at rest, IAM authentication, and audit logging for regulated data
9. **Legacy Modernization**: Oracle/SQL Server option groups (TDE, native audit) and Active Directory authentication

## Submodules

### 1. db_instance

- **Purpose**: Creates and fully manages the `aws_db_instance` resource itself (invoked internally by the root module)
- **Source**: `terraform-aws-modules/rds/aws//modules/db_instance`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_instance
- **Key Features**: Full instance lifecycle, storage/encryption/backup configuration, Enhanced Monitoring & Performance Insights, Secrets Manager password management
- **Use Cases**: Standalone instances, primary databases, read replicas (via `replicate_source_db`), snapshot restores

### 2. db_subnet_group

- **Purpose**: Creates an `aws_db_subnet_group` defining which VPC subnets an instance can be placed in
- **Source**: `terraform-aws-modules/rds/aws//modules/db_subnet_group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_subnet_group
- **Key Features**: Subnet group creation, name-prefix support, multi-AZ subnet placement
- **Use Cases**: Network isolation, spanning subnets across AZs for Multi-AZ/replica placement (root module does **not** create this by default — `create_db_subnet_group` defaults to `false`)

### 3. db_parameter_group

- **Purpose**: Creates an `aws_db_parameter_group` for engine-level parameter tuning
- **Source**: `terraform-aws-modules/rds/aws//modules/db_parameter_group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_parameter_group
- **Key Features**: Engine-family-specific parameters, dynamic/pending-reboot apply methods, `skip_destroy` option
- **Use Cases**: Performance tuning (`shared_buffers`, `max_connections`), enabling logical replication for Blue/Green, character-set configuration

### 4. db_option_group

- **Purpose**: Creates an `aws_db_option_group` for engine features not exposed through parameters (mainly Oracle, SQL Server, MariaDB)
- **Source**: `terraform-aws-modules/rds/aws//modules/db_option_group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_option_group
- **Key Features**: Engine/major-version-scoped options, `option_settings`, `skip_destroy`; automatically ignored for engines without option group support (e.g. PostgreSQL)
- **Use Cases**: Oracle TDE/Statspack, SQL Server native backup/audit, MariaDB audit plugin

### 5. db_instance_role_association

- **Purpose**: Associates an IAM role with a running DB instance for a named feature
- **Source**: `terraform-aws-modules/rds/aws//modules/db_instance_role_association`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_instance_role_association
- **Key Features**: Maps `db_instance_identifier` + `feature_name` to `role_arn`
- **Use Cases**: S3 import/export (Oracle/SQL Server), Lambda invocation from PostgreSQL, other IAM-role-gated engine features

### 6. db_instance_automated_backups_replication

- **Purpose**: Replicates automated backups from a source instance to a different AWS Region for disaster recovery
- **Source**: `terraform-aws-modules/rds/aws//modules/db_instance_automated_backups_replication`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest/submodules/db_instance_automated_backups_replication
- **Key Features**: Cross-region replication via `source_db_instance_arn`, destination `kms_key_arn`, configurable `retention_period`
- **Use Cases**: Cross-region disaster recovery, compliance requiring geographically separated backups

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `identifier` | `string` | n/a (required) | Name of the RDS instance |
| `engine` | `string` | `null` | Database engine (`mysql`, `postgres`, `mariadb`, `oracle-ee`, `sqlserver-ex`, etc.) |
| `engine_version` | `string` | `null` | Database engine version |
| `family` | `string` | `null` | DB parameter group family (e.g. `postgres17`) |
| `major_engine_version` | `string` | `null` | DB option group major version (e.g. `17`) |
| `instance_class` | `string` | `null` | RDS instance type (e.g. `db.t4g.medium`) |
| `allocated_storage` | `number` | `null` | Initial storage allocation in GB |
| `max_allocated_storage` | `number` | `0` | Ceiling for Storage Autoscaling (`0` disables) |
| `storage_type` | `string` | `null` | `standard`, `gp2`, `gp3`, or `io1`/`io2` |
| `iops` | `number` | `null` | Provisioned IOPS (requires `io1`/`io2`/`gp3`); has per-engine minimum `allocated_storage` |
| `storage_encrypted` | `bool` | `true` | Enable storage encryption |
| `kms_key_id` | `string` | `null` | KMS key ARN for encryption (destination key for encrypted replicas) |
| `db_name` | `string` | `null` | Initial database name to create |
| `username` | `string` | `null` | Master username |
| `manage_master_user_password` | `bool` | `true` | Manage master password via Secrets Manager |
| `password_wo` / `password_wo_version` | `string` / `number` | `null` | Write-only password for self-managed credentials (increment version to rotate) |
| `iam_database_authentication_enabled` | `bool` | `false` | Enable IAM database authentication |
| `multi_az` | `bool` | `false` | Enable Multi-AZ deployment |
| `db_subnet_group_name` | `string` | `null` | Name of an existing (or to-be-created) subnet group |
| `create_db_subnet_group` | `bool` | `false` | Whether to create the subnet group (root module default is **off**) |
| `subnet_ids` | `list(string)` | `[]` | Subnet IDs for a newly created subnet group |
| `vpc_security_group_ids` | `list(string)` | `[]` | Security group IDs (create separately, e.g. with `terraform-aws-security-group`) |
| `publicly_accessible` | `bool` | `false` | Allow public access |
| `port` | `string` | `null` | Database port |
| `backup_retention_period` | `number` | `null` | Backup retention in days (0-35) |
| `backup_window` | `string` | `null` | Daily backup window (UTC) |
| `maintenance_window` | `string` | `null` | Weekly maintenance window (UTC) |
| `deletion_protection` | `bool` | `false` | Prevent accidental deletion |
| `skip_final_snapshot` | `bool` | `false` | Skip final snapshot on deletion |
| `replicate_source_db` | `string` | `null` | Identifier (same-region) or ARN (cross-region) of the source instance to replicate |
| `snapshot_identifier` | `string` | `null` | Restore from an existing snapshot |
| `blue_green_update` | `object({ enabled = optional(bool) })` | `null` | Enable RDS Blue/Green Deployments for updates |
| `monitoring_interval` | `number` | `0` | Enhanced Monitoring interval in seconds (`0`, `1`, `5`, `10`, `15`, `30`, `60`) |
| `create_monitoring_role` | `bool` | `false` | Auto-create the Enhanced Monitoring IAM role |
| `performance_insights_enabled` | `bool` | `false` | Enable Performance Insights |
| `database_insights_mode` | `string` | `null` | `standard` or `advanced` Database Insights |
| `enabled_cloudwatch_logs_exports` | `list(string)` | `[]` | Log types to export to CloudWatch |
| `parameters` | `list(object)` | `null` | DB parameters to apply (`name`, `value`, `apply_method`) |
| `options` | `list(object)` | `null` | DB option group entries (`option_name`, `port`, `option_settings`, ...) |
| `engine_lifecycle_support` | `string` | `null` | `open-source-rds-extended-support` or `...-disabled` (MySQL/PostgreSQL only) |
| `create_db_instance` / `create_db_parameter_group` / `create_db_option_group` | `bool` | `true` | Toggles to disable creation of individual sub-resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `db_instance_endpoint` | Connection endpoint (`hostname:port`) |
| `db_instance_address` | Hostname of the RDS instance |
| `db_instance_port` | Database port number |
| `db_instance_identifier` | Instance identifier |
| `db_instance_arn` | ARN of the instance |
| `db_instance_resource_id` | RDS Resource ID (used for IAM auth policies) |
| `db_instance_username` | Master username |
| `db_instance_master_user_secret_arn` | Secrets Manager secret ARN (when `manage_master_user_password = true`) |
| `db_instance_availability_zone` | Availability zone |
| `db_instance_engine` / `db_instance_engine_version_actual` | Engine and actual running version |
| `db_instance_hosted_zone_id` | Canonical hosted zone ID (for a Route 53 alias record) |
| `db_subnet_group_id` / `db_subnet_group_arn` | Subnet group identifier and ARN |
| `db_parameter_group_id` / `db_parameter_group_arn` | Parameter group identifier and ARN |
| `db_option_group_id` / `db_option_group_arn` | Option group identifier and ARN |
| `enhanced_monitoring_iam_role_arn` | ARN of the Enhanced Monitoring IAM role |
| `db_instance_role_associations` | Map of DB instance identifiers to associated IAM role ARNs |

## Usage Examples

### Basic MySQL Instance

```hcl
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 7.0"

  identifier = "demodb"

  engine               = "mysql"
  engine_version       = "8.0.43"
  family               = "mysql8.0"      # DB parameter group
  major_engine_version = "8.0"           # DB option group
  instance_class       = "db.t4g.large"

  allocated_storage     = 20
  max_allocated_storage = 100

  db_name  = "demodb"
  username = "dbadmin"
  port     = 3306

  # Managed master password (Secrets Manager) — default, shown for clarity
  manage_master_user_password = true

  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.security_group.security_group_id]

  maintenance_window = "Mon:00:00-Mon:03:00"
  backup_window       = "03:00-06:00"

  deletion_protection = true

  tags = {
    Owner       = "team-data"
    Environment = "dev"
  }
}
```

### Production Multi-AZ PostgreSQL with Monitoring

```hcl
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 7.0"

  identifier = "prod-postgres-db"

  engine               = "postgres"
  engine_version       = "17.6"
  family               = "postgres17"
  major_engine_version = "17"
  instance_class       = "db.r6g.xlarge"

  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id             = aws_kms_key.rds.arn

  db_name  = "production"
  username = "dbadmin"
  port     = 5432

  manage_master_user_password = true
  master_user_password_rotation_automatically_after_days = 30

  multi_az = true

  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.security_group.security_group_id]
  publicly_accessible    = false

  backup_retention_period = 30
  backup_window            = "03:00-04:00"
  maintenance_window       = "Mon:04:00-Mon:05:00"
  skip_final_snapshot      = false
  deletion_protection      = true

  monitoring_interval                   = 60
  create_monitoring_role                = true
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  enabled_cloudwatch_logs_exports       = ["postgresql", "upgrade"]

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

### MySQL Primary with Read Replica

```hcl
module "primary" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 7.0"

  identifier = "mysql-primary"

  engine               = "mysql"
  engine_version       = "8.0.43"
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

  multi_az                = true
  db_subnet_group_name    = module.vpc.database_subnet_group
  vpc_security_group_ids  = [module.security_group.security_group_id]

  # Backups must be enabled to create a replica
  backup_retention_period = 14

  tags = { Environment = "production" }
}

module "replica" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 7.0"

  identifier = "mysql-replica"

  # Same-region: use the primary's identifier. Cross-region: use its ARN instead.
  replicate_source_db = module.primary.db_instance_identifier

  instance_class = "db.r6g.large"

  # Username/password must not be set on a replica
  manage_master_user_password = false

  vpc_security_group_ids = [module.security_group.security_group_id]

  backup_retention_period = 0
  skip_final_snapshot     = true

  tags = { Environment = "production", Role = "replica" }
}
```

### Blue/Green Deployment for a PostgreSQL Upgrade

```hcl
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 7.0"

  identifier = "postgres-blue-green"

  engine               = "postgres"
  engine_version       = "17.6"
  family               = "postgres17"
  major_engine_version = "17"
  instance_class       = "db.t4g.large"

  allocated_storage     = 20
  max_allocated_storage = 100

  db_name  = "app"
  username = "app_admin"
  port     = 5432

  multi_az                = true
  db_subnet_group_name    = module.vpc.database_subnet_group
  vpc_security_group_ids  = [module.security_group.security_group_id]

  blue_green_update = {
    enabled = true
  }

  # Blue/Green deployments are not compatible with a Secrets-Manager-managed password
  manage_master_user_password = false
  password_wo                 = var.db_password
  password_wo_version         = 1

  # Logical replication must be enabled for Blue/Green to work on PostgreSQL
  parameters = [
    {
      name         = "rds.logical_replication"
      value        = "1"
      apply_method = "pending-reboot"
    }
  ]

  backup_retention_period = 7
  skip_final_snapshot     = false
  deletion_protection     = true

  tags = { Environment = "production" }
}
```

## Best Practices

### Security

1. **Enable encryption**: Keep `storage_encrypted = true` (default) and use customer-managed KMS keys for regulated workloads
2. **Isolate networking**: Deploy in private subnets, keep `publicly_accessible = false`, and restrict `vpc_security_group_ids` to necessary sources
3. **Prefer managed credentials**: Keep `manage_master_user_password = true` and configure `master_user_password_rotation_automatically_after_days` instead of static passwords
4. **Use write-only passwords when self-managing**: If a static password is unavoidable, set `password_wo`/`password_wo_version` — the module no longer accepts a plaintext `password` variable
5. **Enable IAM database authentication** where supported (MySQL, PostgreSQL) for token-based, credential-free access
6. **Enable deletion protection**: Set `deletion_protection = true` and `skip_final_snapshot = false` for production
7. **Security groups are external**: This module does not create security groups — always pair it with `terraform-aws-security-group`

### High Availability & Disaster Recovery

1. **Enable Multi-AZ**: Set `multi_az = true` for production workloads
2. **Use read replicas**: Offload read traffic and provide a promotable standby via `replicate_source_db`
3. **Replicate backups cross-region**: Use the `db_instance_automated_backups_replication` submodule for DR
4. **Span subnet groups across AZs**: Provide at least two AZs' subnets to `db_subnet_group`
5. **Use Blue/Green for risky changes**: Prefer `blue_green_update` over in-place major-version or parameter-group changes to minimize downtime and risk

### Backup & Recovery

1. **Set an adequate retention period**: 7-35 days for production (`backup_retention_period` must be `> 0` to create replicas)
2. **Schedule non-overlapping windows**: `backup_window` and `maintenance_window` should not overlap and should target low-traffic periods
3. **Keep final snapshots**: `skip_final_snapshot = false` for production, with a meaningful `final_snapshot_identifier_prefix`
4. **Test recovery paths**: Regularly verify `snapshot_identifier` and `restore_to_point_in_time` restores

### Performance & Storage

1. **Prefer gp3 with explicit IOPS/throughput**: Better price/performance than gp2, but `iops`/`storage_throughput` have per-engine minimum `allocated_storage` thresholds — check before setting them on small volumes
2. **Enable Storage Autoscaling**: Set `max_allocated_storage` to avoid out-of-space incidents
3. **Enable observability**: Turn on `performance_insights_enabled` and `monitoring_interval` (e.g. `60`) for production
4. **Tune with a dedicated parameter group**: Adjust engine parameters (e.g. `shared_buffers`, `max_connections`) instead of relying on the AWS default group

### Cost Optimization

1. **Right-size instances**: Use CloudWatch/Performance Insights metrics before committing to Reserved Instances
2. **Review extended support**: Set `engine_lifecycle_support = "open-source-rds-extended-support-disabled"` for non-critical MySQL/PostgreSQL workloads to avoid extended-support charges
3. **Trim Performance Insights retention**: Keep the default 7-day `performance_insights_retention_period` unless long-term analysis is required
4. **Prune snapshots and idle instances**: Automate cleanup of manual snapshots and stop non-production instances outside business hours

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-rds/tree/master/examples
- **Blue/Green Deployment Example**: https://github.com/terraform-aws-modules/terraform-aws-rds/tree/master/examples/blue-green-deployment
- **AWS RDS User Guide**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/
- **AWS RDS Best Practices**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html
- **RDS Storage & gp3 IOPS/Throughput Limits**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#gp3-storage
- **RDS Blue/Green Deployments**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/blue-green-deployments.html
- **RDS Performance Insights**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.html
- **terraform-aws-security-group Module**: https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest
- **RDS Pricing**: https://aws.amazon.com/rds/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Version pin**: Use `version = "~> 7.0"`; the module requires Terraform >= 1.11.1 and AWS provider >= 6.28
2. **No plaintext password input**: The legacy `password` variable has been removed — use `manage_master_user_password = true` (default) or `password_wo`/`password_wo_version`
3. **Security groups are external**: Always create them separately (e.g. `terraform-aws-security-group`) and pass IDs via `vpc_security_group_ids`
4. **Subnet group is not created by default**: `create_db_subnet_group` defaults to `false` — either pass an existing `db_subnet_group_name` or set `create_db_subnet_group = true` with `subnet_ids`
5. **`manage_master_user_password` conflicts**: It cannot be used together with `replicate_source_db` (read replicas) or `blue_green_update` — set it to `false` in those configurations
6. **GP3 minimums**: `iops`/`storage_throughput` are rejected below a per-engine `allocated_storage` threshold — omit them for small volumes
7. **`family` vs `major_engine_version`**: `family` drives the parameter group (e.g. `postgres17`), `major_engine_version` drives the option group (e.g. `17`) — keep both consistent with `engine_version`
8. **Option groups auto-skip**: Engines without option group support (e.g. PostgreSQL) ignore `option_group_name`/`options` even if set
9. **Production defaults**: Set `deletion_protection = true` and `skip_final_snapshot = false` for anything production
10. **Monitoring setup**: Enable both `performance_insights_enabled = true` and `monitoring_interval` (1-60); set `create_monitoring_role = true` to auto-create the IAM role
11. **Blue/Green prerequisites**: Requires logical replication enabled beforehand for PostgreSQL (`rds.logical_replication` parameter) and is incompatible with `manage_master_user_password = true`
12. **Cross-region replicas**: Use the source instance's ARN (not identifier) for `replicate_source_db` and set `kms_key_id` to a key in the destination region
13. **Tagging**: Use the shared `tags` variable plus resource-specific overrides (`db_instance_tags`, `db_subnet_group_tags`, `db_parameter_group_tags`, `db_option_group_tags`) where finer control is needed
