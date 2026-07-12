# Terraform AWS RDS Aurora Module

## Module Information

- **Module Name**: `rds-aurora`
- **Module ID**: `terraform-aws-modules/rds-aurora/aws`
- **Source**: `terraform-aws-modules/rds-aurora/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds-aurora
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds-aurora/aws/latest
- **Latest Version**: 10.3.0
- **Purpose**: Terraform module for creating and managing AWS RDS Aurora clusters (MySQL, PostgreSQL, Limitless, DSQL), including provisioned/serverless instances, autoscaling, global clusters, and RDS Multi-AZ (non-Aurora) clusters
- **Service**: AWS RDS Aurora (Amazon Relational Database Service - Aurora)
- **Category**: Database, Managed Services, Cloud Infrastructure
- **Keywords**: aurora, rds, database, postgresql, mysql, serverless, serverless-v2, global-cluster, autoscaling, multi-az, read-replica, encryption, high-availability, dsql, limitless, secrets-manager, enhanced-monitoring
- **Use For**: Production relational databases, multi-region database deployments, serverless database workloads, auto-scaling database clusters, high-availability database systems, disaster recovery setups, global database applications, microservices data persistence, read-heavy workloads with replica scaling, cost-optimized serverless databases, horizontally-scalable Limitless workloads, distributed SQL with Aurora DSQL

## Description

This Terraform module provides a comprehensive solution for deploying and managing Amazon Aurora database clusters on AWS, along with RDS Multi-AZ (non-Aurora) clusters. Aurora is a MySQL- and PostgreSQL-compatible relational database built for the cloud, combining enterprise-grade performance with open-source simplicity. The module supports multiple engine types (Aurora MySQL, Aurora PostgreSQL, Aurora Limitless), both provisioned and serverless (v1/v2) deployment modes, and advanced features such as global clusters, read replica autoscaling, custom endpoints, and cluster/instance-level parameter groups.

The module enables flexible cluster architectures, from simple single-region deployments to sophisticated multi-region global databases with automatic failover. It supports Aurora Serverless v1 and v2 for variable workloads, Aurora Limitless (via `cluster_scalability_type = "limitless"` and a `shard_group` configuration) for horizontally scalable databases, and heterogeneous clusters with mixed instance classes and promotion-tier control for failover priority. A separate `dsql` submodule manages AWS Aurora DSQL (Distributed SQL) clusters, including multi-region cluster peering. Integration with AWS Secrets Manager (`manage_master_user_password`) provides automatic master password management without storing credentials in Terraform state; alternatively, write-only password arguments (`master_password_wo`) can be used where a managed secret is not supported (e.g., Limitless, Global Database secondary clusters).

Built with production readiness in mind, the module includes options for security (encryption enabled by default, IAM database authentication, network isolation via auto-created or existing security groups), high availability (Multi-AZ instance placement, automated backups, activity streams), and operational excellence (enhanced/cluster-level monitoring, Performance Insights, Database Insights, CloudWatch log exports, parameter groups). Requires Terraform >= 1.11.1 and AWS Provider >= 6.54.

## Key Features

- **Multiple Database Engines**: Aurora MySQL, Aurora PostgreSQL, Aurora (MySQL-compatible), Aurora Limitless, and Aurora DSQL (via submodule)
- **Deployment Modes**: Provisioned clusters, Serverless v1 (`scaling_configuration`), Serverless v2 (`serverlessv2_scaling_configuration`), and Limitless (`cluster_scalability_type` + `shard_group`)
- **Global Clusters**: Multi-region database clusters with `global_cluster_identifier`, cross-region secondary clusters, and write forwarding
- **Read Replica Autoscaling**: CPU- or connection-based automatic scaling with configurable min/max capacity and cooldowns
- **Heterogeneous Clusters**: Mix different instance classes per entry in `instances`, with `promotion_tier` control for failover priority
- **Secrets Manager Integration**: Automatic master password management (`manage_master_user_password`, enabled by default) with optional rotation; `master_password_wo` write-only password for cases where managed secrets aren't supported
- **Aurora DSQL Support**: Distributed SQL clusters with single- or multi-region peering via the `dsql` submodule
- **Enhanced & Cluster-Level Monitoring**: `cluster_monitoring_interval` plus per-instance `monitoring_interval`, Performance Insights, Database Insights (`database_insights_mode`)
- **Custom Endpoints**: `endpoints` map for fine-grained routing to specific instances or instance groups
- **S3 Import**: Restore databases from a Percona Xtrabackup stored in S3 (MySQL only)
- **RDS Multi-AZ (non-Aurora)**: Supports Multi-AZ DB clusters (not the Aurora engine) via `allocated_storage`, `iops`, `storage_type`
- **Encryption at Rest**: Storage encryption enabled by default (`storage_encrypted = true`) using AWS KMS
- **IAM Database Authentication**: Token-based authentication without storing passwords
- **CloudWatch Logs Export**: Audit, error, general, slowquery, and postgresql log types, optionally into module-managed log groups
- **Security Groups**: Auto-create or use existing security groups, with ingress/egress rule maps
- **Database Activity Streams & Role Associations**: `cluster_activity_stream` and `role_associations` for auditing and cross-service IAM roles
- **Point-in-Time Restore & Cloning**: `restore_to_point_in_time`, `snapshot_identifier`, `replication_source_identifier`
- **Conditional Resource Creation**: `create`, `create_db_subnet_group`, `create_security_group`, `create_monitoring_role`, `create_cloudwatch_log_group` flags

## Main Use Cases

1. **Production Application Databases**: Highly available, scalable relational databases for web and mobile applications
2. **Multi-Region Applications**: Global database clusters with low-latency reads in multiple geographic regions
3. **Serverless Workloads**: Auto-scaling databases for development environments and intermittent workloads
4. **Read-Heavy Applications**: Auto-scaling read replicas for applications with high read-to-write ratios
5. **Enterprise Database Migration**: Moving on-premises MySQL or PostgreSQL databases to managed Aurora
6. **Microservices Architecture**: Individual Aurora clusters for service-specific data isolation
7. **Horizontally Scalable Workloads**: Aurora Limitless shard groups for very large, write-heavy relational workloads
8. **Distributed SQL**: Aurora DSQL clusters (via the `dsql` submodule) for multi-region, active-active SQL databases
9. **Disaster Recovery**: Cross-region replication, global clusters, and automated backup for business continuity
10. **Cost Optimization**: Serverless Aurora for variable workloads to reduce costs during idle periods

## Submodules

### 1. dsql

- **Purpose**: Creates AWS Aurora DSQL (Distributed SQL) clusters with single- or multi-region peering capabilities
- **Source**: `terraform-aws-modules/rds-aurora/aws//modules/dsql`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds-aurora/aws/latest/submodules/dsql
- **Key Features**: Multi-region cluster deployment with witness region, cluster peering configuration, KMS encryption support, deletion protection with `force_destroy` override
- **Use Cases**: Distributed database workloads, multi-region data residency requirements, cross-region database peering, geographically distributed applications

## Submodule 1: dsql

### Description

The `dsql` submodule creates and manages Aurora DSQL (Distributed SQL) clusters, which provide distributed database capabilities within a single region or across multiple AWS regions. It supports cluster peering to connect two or more DSQL clusters for multi-region, active-active workloads, and includes configuration options for encryption, deletion protection, and witness-region configuration.

### Key Features

- Single-region or multi-region DSQL cluster deployment with a configurable witness region
- Cluster peering (`create_cluster_peering` + `clusters`) to connect multiple DSQL clusters
- KMS encryption support with customer-managed key, or `AWS_OWNED_KMS_KEY`
- Deletion protection (`deletion_protection_enabled`) with a `force_destroy` escape hatch for non-production use
- Flexible tagging for resource management and cost allocation
- VPC endpoint service integration for private connectivity
- Conditional resource creation via the `create` flag

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name used across resources created |
| `create` | `bool` | `true` | Whether the DSQL cluster should be created |
| `region` | `string` | `null` | AWS region for this cluster (defaults to the provider's region); set on the secondary cluster in a multi-region pair |
| `witness_region` | `string` | `null` | Witness region for multi-region clusters; setting this makes the cluster multi-region (changing it recreates the cluster) |
| `create_cluster_peering` | `bool` | `false` | Whether to create cluster peering resources |
| `clusters` | `list(string)` | `null` | List of DSQL cluster ARNs to peer with this cluster |
| `kms_encryption_key` | `string` | `null` | ARN of the KMS key for cluster encryption, or `AWS_OWNED_KMS_KEY` |
| `deletion_protection_enabled` | `bool` | `null` | Whether deletion protection is enabled for the cluster |
| `force_destroy` | `bool` | `null` | Destroys the cluster even if `deletion_protection_enabled` is `true` |
| `timeouts` | `object({create})` | `null` | Create timeout configuration for the cluster |
| `tags` | `map(string)` | `{}` | Map of tags to assign to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | The Amazon Resource Name (ARN) of the DSQL cluster |
| `identifier` | The unique identifier of the DSQL cluster |
| `encryption_details` | Details about the encryption configuration of the cluster |
| `multi_region_properties` | Multi-region properties of the DSQL cluster (witness region, peered clusters) |
| `vpc_endpoint_service_name` | The VPC endpoint service name for private connectivity |

### Usage Example

```hcl
# Two DSQL clusters peered across regions (multi-region, active-active)
module "dsql_cluster_1" {
  source = "terraform-aws-modules/rds-aurora/aws//modules/dsql"

  name = "dsql-1"

  witness_region          = "us-west-2"
  create_cluster_peering  = true
  clusters                = [module.dsql_cluster_2.arn]

  deletion_protection_enabled = true

  tags = {
    Environment = "production"
  }
}

module "dsql_cluster_2" {
  source = "terraform-aws-modules/rds-aurora/aws//modules/dsql"

  region = "us-east-2"
  name   = "dsql-2"

  witness_region          = "us-west-2"
  create_cluster_peering  = true
  clusters                = [module.dsql_cluster_1.arn]

  deletion_protection_enabled = true

  tags = {
    Environment = "production"
  }
}

# Single-region DSQL cluster (no peering)
module "dsql_single_region" {
  source = "terraform-aws-modules/rds-aurora/aws//modules/dsql"

  name = "dsql-single"

  tags = {
    Environment = "production"
  }
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name used across resources created (must be set) |
| `engine` | `string` | `null` | Database engine: `aurora`, `aurora-mysql`, `aurora-postgresql` (must be set) |
| `engine_version` | `string` | `null` | Specific engine version (e.g., `17.5` for PostgreSQL, `8.0` for MySQL, `16.9-limitless` for Limitless) |
| `engine_mode` | `string` | `"provisioned"` | Database engine mode: `global`, `multimaster`, `parallelquery`, `provisioned`, `serverless` (v1) |
| `master_username` | `string` | `null` | Master DB username; required unless `snapshot_identifier`, `replication_source_identifier`, or a secondary `global_cluster_identifier` is used |
| `cluster_instance_class` | `string` | `null` | Default compute/memory capacity per instance (e.g., `db.r8g.large`, `db.serverless`) |
| `instances` | `map(object)` | `{}` | Map of cluster instances; each entry can override `instance_class`, `promotion_tier`, `publicly_accessible`, `monitoring_interval`, etc. |
| `vpc_id` | `string` | `""` | VPC ID for security group placement |
| `db_subnet_group_name` | `string` | `""` | Database subnet group (existing, or created when `create_db_subnet_group = true`) |
| `subnets` | `list(string)` | `[]` | List of subnet IDs used by the created database subnet group |
| `create_db_subnet_group` | `bool` | `false` | Whether to create the database subnet group (default is to use an existing one) |
| `storage_encrypted` | `bool` | `true` | Enable encryption at rest |
| `kms_key_id` | `string` | `null` | ARN for KMS encryption key (requires `storage_encrypted = true`) |
| `backup_retention_period` | `number` | `null` | Days to retain automated backups |
| `deletion_protection` | `bool` | `null` | Prevent accidental cluster deletion |
| `skip_final_snapshot` | `bool` | `false` | Skip final snapshot before deletion |
| `manage_master_user_password` | `bool` | `true` | Use RDS-managed Secrets Manager secret for the master password; cannot be combined with `master_password_wo` |
| `master_password_wo` | `string` | `null` | Write-only master password; required unless `manage_master_user_password`, `snapshot_identifier`, `replication_source_identifier`, or secondary global cluster |
| `autoscaling_enabled` | `bool` | `false` | Enable read replica autoscaling |
| `autoscaling_min_capacity` | `number` | `0` | Minimum autoscaled read replicas |
| `autoscaling_max_capacity` | `number` | `2` | Maximum autoscaled read replicas |
| `autoscaling_target_cpu` | `number` | `70` | Target CPU percentage for autoscaling |
| `cluster_scalability_type` | `string` | `null` | Set to `limitless` to enable Aurora Limitless (requires `shard_group`); default is `standard` |
| `shard_group` | `object` | `null` | Aurora Limitless DB shard group configuration (`identifier`, `max_acu`, `min_acu`, `compute_redundancy`) |
| `global_cluster_identifier` | `string` | `null` | ID of an `aws_rds_global_cluster` to attach this cluster to (primary or secondary) |
| `is_primary_cluster` | `bool` | `true` | Set `false` on secondary/replica clusters in a global database |
| `serverlessv2_scaling_configuration` | `object` | `null` | Serverless v2 `min_capacity`/`max_capacity` (ACUs); used with `engine_mode = "provisioned"` and `instance_class = "db.serverless"` |
| `scaling_configuration` | `object` | `null` | Serverless v1 scaling properties; only valid when `engine_mode = "serverless"` |
| `enabled_cloudwatch_logs_exports` | `list(string)` | `[]` | Log types: `audit`, `error`, `general`, `slowquery`, `postgresql` |
| `cluster_monitoring_interval` | `number` | `0` | Enhanced monitoring frequency at the cluster level (0=disabled; 1, 5, 10, 15, 30, 60 seconds) |
| `vpc_security_group_ids` | `list(string)` | `[]` | List of existing VPC security groups to associate, in addition to any created |
| `security_group_ingress_rules` | `map(object)` | `{}` | Map of ingress rules for the auto-created security group |
| `iam_database_authentication_enabled` | `bool` | `null` | Enable IAM database authentication |
| `endpoints` | `map(object)` | `{}` | Additional cluster endpoints (`READER`/`ANY`) with `static_members`/`excluded_members` for workload routing |
| `create` | `bool` | `true` | Whether to create cluster resources at all |
| `create_security_group` | `bool` | `true` | Create security group or use existing (via `vpc_security_group_ids`) |
| `create_monitoring_role` | `bool` | `true` | Create IAM role for enhanced monitoring |
| `apply_immediately` | `bool` | `null` | Apply changes immediately or during the next maintenance window |
| `allow_major_version_upgrade` | `bool` | `false` | Allow major engine version upgrades when changing `engine_version` |
| `auto_minor_version_upgrade` | `bool` | `null` | Apply minor engine upgrades automatically during the maintenance window |
| `s3_import` | `object` | `null` | Restore a MySQL cluster from a Percona Xtrabackup stored in S3 |
| `tags` | `map(string)` | `{}` | Map of tags to assign to all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `cluster_endpoint` | Writer endpoint for the cluster (primary connection) |
| `cluster_reader_endpoint` | Read-only endpoint, load-balanced across replicas |
| `additional_cluster_endpoints` | Map of custom `endpoints` and their attributes |
| `cluster_port` | Database port number |
| `cluster_id` | RDS Cluster Identifier |
| `cluster_arn` | Amazon Resource Name (ARN) of the cluster |
| `cluster_resource_id` | RDS Cluster Resource ID |
| `cluster_members` | List of RDS instance identifiers in the cluster |
| `cluster_instances` | Map of cluster instances with full attributes |
| `cluster_master_username` | Database master username (sensitive) |
| `cluster_master_user_secret` | Generated Secrets Manager secret object (when `manage_master_user_password = true`) |
| `cluster_upgrade_rollout_order` | Order in which cluster members are upgraded (first, second, last) |
| `security_group_id` | Security group ID of the cluster |
| `cluster_engine_version_actual` | Running engine version |
| `cluster_database_name` | Auto-created database name |
| `db_subnet_group_name` | Subnet group identifier |
| `enhanced_monitoring_iam_role_arn` | Enhanced monitoring IAM role ARN |
| `db_cluster_parameter_group_arn` | Cluster parameter group ARN |
| `db_parameter_group_arn` | DB (instance) parameter group ARN |
| `db_shard_group_arn` / `db_shard_group_endpoint` | Aurora Limitless shard group ARN and connection endpoint |
| `db_cluster_activity_stream_kinesis_stream_name` | Kinesis stream used for the database activity stream |
| `cluster_role_associations` | Map of IAM roles associated with the cluster |

## Usage Examples

### Basic PostgreSQL Cluster

```hcl
module "aurora_cluster" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 10.3"

  name           = "my-aurora-postgres"
  engine         = "aurora-postgresql"
  engine_version = "17.5"

  cluster_instance_class = "db.r8g.large"
  instances = {
    one = {}
    two = {
      instance_class = "db.r8g.2xlarge"
    }
  }

  vpc_id               = "vpc-12345678"
  db_subnet_group_name = "db-subnet-group"

  security_group_ingress_rules = {
    vpc_ingress = {
      cidr_ipv4 = "10.20.0.0/20"
    }
  }

  storage_encrypted           = true
  apply_immediately           = true
  cluster_monitoring_interval = 10

  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}
```

### Autoscaled Cluster

```hcl
module "aurora_cluster" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 10.3"

  name           = "my-aurora-autoscaled"
  engine         = "aurora-postgresql"
  engine_version = "17.5"

  cluster_instance_class = "db.r8g.large"
  instances = {
    one = {} # Primary writer instance
  }

  autoscaling_enabled      = true
  autoscaling_min_capacity = 1
  autoscaling_max_capacity = 5
  autoscaling_target_cpu   = 70

  vpc_id               = "vpc-12345678"
  db_subnet_group_name = "db-subnet-group"
  storage_encrypted    = true

  tags = {
    Environment = "production"
  }
}
```

### Heterogeneous Cluster with Mixed Instance Classes

```hcl
module "aurora_cluster" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 10.3"

  name           = "my-aurora-heterogeneous"
  engine         = "aurora-postgresql"
  engine_version = "17.5"

  cluster_instance_class = "db.r8g.large"
  instances = {
    writer = {
      instance_class      = "db.r8g.2xlarge"
      publicly_accessible = false
    }
    reader_analytics = {
      identifier     = "analytics-reader"
      instance_class = "db.r8g.2xlarge"
    }
    reader_reporting = {
      identifier     = "reporting-reader"
      instance_class = "db.r8g.large"
      promotion_tier = 15 # Lower priority for failover
    }
  }

  autoscaling_enabled      = true
  autoscaling_min_capacity = 1
  autoscaling_max_capacity = 5

  vpc_id  = "vpc-12345678"
  subnets = ["subnet-1", "subnet-2", "subnet-3"]

  storage_encrypted   = true
  deletion_protection = true

  tags = {
    Environment = "production"
  }
}
```

### Serverless v2 Cluster

```hcl
module "aurora_serverless" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 10.3"

  name              = "my-aurora-serverless"
  engine            = "aurora-postgresql"
  engine_mode       = "provisioned"
  engine_version    = "17.5"
  storage_encrypted = true
  master_username   = "root"

  vpc_id               = "vpc-12345678"
  db_subnet_group_name = "db-subnet-group"

  security_group_ingress_rules = {
    vpc_ingress = {
      cidr_ipv4 = "10.20.0.0/20"
    }
  }

  serverlessv2_scaling_configuration = {
    min_capacity = 2
    max_capacity = 10
  }

  cluster_instance_class = "db.serverless"
  instances = {
    one = {}
    two = {}
  }

  apply_immediately   = true
  skip_final_snapshot = true

  tags = {
    Environment = "production"
  }
}
```

### Global Database (Multi-Region)

```hcl
resource "aws_rds_global_cluster" "this" {
  global_cluster_identifier = "my-global-db"
  engine                    = "aurora-postgresql"
  engine_version            = "17.5"
  database_name             = "example_db"
  storage_encrypted         = true
}

module "aurora_primary" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 10.3"

  name                      = "my-global-db"
  database_name             = aws_rds_global_cluster.this.database_name
  engine                    = aws_rds_global_cluster.this.engine
  engine_version            = aws_rds_global_cluster.this.engine_version
  global_cluster_identifier = aws_rds_global_cluster.this.id
  cluster_instance_class    = "db.r8g.large"
  instances                 = { for i in range(2) : i => {} }

  vpc_id               = "vpc-12345678"
  db_subnet_group_name = "db-subnet-group-primary"

  # Global clusters do not support the RDS-managed master user password
  master_password_wo         = random_password.master.result
  master_password_wo_version = 1

  skip_final_snapshot = true
  tags                = { Environment = "production" }
}

module "aurora_secondary" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 10.3"

  region              = "us-east-1" # secondary region
  is_primary_cluster  = false

  name                      = "my-global-db"
  engine                    = aws_rds_global_cluster.this.engine
  engine_version            = aws_rds_global_cluster.this.engine_version
  global_cluster_identifier = aws_rds_global_cluster.this.id
  source_region             = "eu-west-1" # primary region
  cluster_instance_class    = "db.r8g.large"
  instances                 = { for i in range(2) : i => {} }

  vpc_id               = "vpc-87654321"
  db_subnet_group_name = "db-subnet-group-secondary"

  master_password_wo         = random_password.master.result
  master_password_wo_version = 1

  skip_final_snapshot = true
  depends_on          = [module.aurora_primary]
  tags                = { Environment = "production" }
}
```

## Best Practices

### Cluster Architecture and Design

1. **Choose the Right Engine Mode**: Use provisioned mode for predictable workloads, Serverless v2 for variable workloads, Limitless (`cluster_scalability_type = "limitless"`) for very large write-heavy workloads, and DSQL for distributed multi-region SQL
2. **Size Instances Appropriately**: Start with smaller instance classes and scale up based on performance metrics rather than over-provisioning
3. **Use Multi-AZ Deployments**: Spread instances across multiple availability zones for production workloads to ensure high availability and automatic failover
4. **Leverage Read Replicas**: Distribute read traffic across read replicas and enable autoscaling to handle variable read workloads
5. **Design for Failure**: Architect applications to handle database failover scenarios with connection retry logic and proper timeouts
6. **Separate Workloads**: Use the `endpoints` map to route different application workloads (analytics, reporting, OLTP) to specific instances
7. **Consider Global Clusters**: For globally distributed applications, use Aurora Global Database (`global_cluster_identifier`, `is_primary_cluster = false` on secondaries) for low-latency reads in multiple regions

### Security and Compliance

1. **Enable Encryption at Rest**: Keep `storage_encrypted = true` (the default) and use customer-managed KMS keys (`kms_key_id`) for sensitive data
2. **Implement Network Isolation**: Deploy clusters in private subnets and use `security_group_ingress_rules`/`vpc_security_group_ids` to restrict access to authorized sources only
3. **Use IAM Database Authentication**: Enable `iam_database_authentication_enabled` for applications that support token-based authentication to avoid storing credentials
4. **Rotate Credentials Regularly**: Prefer `manage_master_user_password = true` (Secrets Manager) and enable `manage_master_user_password_rotation`; use `master_password_wo` only where managed secrets aren't supported (Limitless, global secondaries)
5. **Enable Deletion Protection**: Set `deletion_protection = true` for production clusters to prevent accidental deletion
6. **Audit Database Activity**: Enable `enabled_cloudwatch_logs_exports` and consider `cluster_activity_stream` for security monitoring and compliance
7. **Encrypt Connections**: Configure SSL/TLS (`cluster_ca_cert_identifier`) for all client connections to encrypt data in transit
8. **Apply Least Privilege**: Grant only necessary database permissions to application users and use separate users for different applications
9. **Use Parameter Groups Carefully**: Customize `cluster_parameter_group`/`db_parameter_group` to disable unnecessary features and enforce security settings

### Backup and Disaster Recovery

1. **Configure Appropriate Retention**: Set `backup_retention_period` based on recovery point objectives (RPO), typically 7-35 days for production
2. **Test Recovery Procedures**: Regularly test point-in-time recovery (`restore_to_point_in_time`) and snapshot restoration to verify backup integrity
3. **Enable Automated Backups**: Ensure automated backups are enabled and scheduled during low-activity periods (`preferred_backup_window`)
4. **Use Global Clusters for DR**: Implement Aurora Global Database for cross-region disaster recovery with sub-second replication lag
5. **Set `skip_final_snapshot` Deliberately**: Keep it `false` (default) in production so a final snapshot is taken on destroy; only set `true` for ephemeral/test clusters
6. **Tag Snapshots**: Apply meaningful tags for easier management and lifecycle policies
7. **Document Recovery Procedures**: Maintain runbooks with step-by-step recovery procedures for various failure scenarios
8. **Monitor Backup Status**: Set up CloudWatch alarms to alert on backup failures or missing backups

### Performance Optimization

1. **Enable Performance Insights**: Activate `cluster_performance_insights_enabled` to identify slow queries and performance bottlenecks
2. **Configure Monitoring Intervals**: Set `cluster_monitoring_interval` (and per-instance `monitoring_interval`) to 1-60 seconds based on troubleshooting needs
3. **Optimize Parameter Groups**: Tune `cluster_parameter_group`/`db_parameter_group` parameters based on workload characteristics (OLTP vs. analytics)
4. **Monitor Query Performance**: Export slow query logs to CloudWatch and regularly review slow queries for optimization
5. **Scale Read Workloads**: Use read replicas and the reader endpoint to offload read traffic from the primary instance
6. **Configure Autoscaling**: Set up read replica autoscaling with appropriate CPU/connection thresholds and min/max replica counts
7. **Right-Size Instances**: Monitor CPU, memory, and I/O metrics to ensure instance classes match workload requirements
8. **Use Limitless for Extreme Scale**: For very large, write-heavy relational workloads that outgrow a single-writer cluster, evaluate `cluster_scalability_type = "limitless"` with an appropriately sized `shard_group`

### Cost Optimization

1. **Use Serverless for Variable Workloads**: Choose Aurora Serverless v2 (`serverlessv2_scaling_configuration`) for development, testing, or infrequently accessed databases
2. **Right-Size Clusters**: Regularly review utilization metrics and downsize over-provisioned instances
3. **Optimize Backup Retention**: Balance retention requirements with storage costs; use shorter retention for non-critical environments
4. **Delete Unused Snapshots**: Implement lifecycle policies to delete old manual snapshots that are no longer needed
5. **Use Reserved Instances**: For predictable production workloads, purchase reserved instances for significant cost savings
6. **Leverage Autoscaling**: Configure read replica autoscaling to scale down during low-traffic periods
7. **Evaluate Cross-Region Costs**: Weigh the necessity of global clusters and cross-region replication against data transfer costs
8. **Use Tags for Cost Allocation**: Apply consistent tags via `tags`/`cluster_tags` to track costs by application, environment, or business unit

### Operational Excellence

1. **Enable Auto Minor Version Upgrades**: Allow `auto_minor_version_upgrade` during maintenance windows for security patches
2. **Plan Major Upgrades Carefully**: Set `allow_major_version_upgrade = true` only when intentionally upgrading, and test in non-production first
3. **Configure Maintenance Windows**: Set `preferred_maintenance_window` during low-traffic periods to minimize impact
4. **Implement Comprehensive Tagging**: Use consistent tagging strategies for resource organization, cost tracking, and automation
5. **Monitor Key Metrics**: Set up CloudWatch alarms for CPU, memory, storage, connections, and replication lag
6. **Use CloudWatch Log Exports**: Export database logs (error, slow query, audit) to CloudWatch for centralized logging
7. **Document Cluster Configuration**: Maintain documentation of cluster architecture, networking, and configuration decisions
8. **Implement Change Management**: Use Infrastructure as Code (Terraform) for all database changes with proper code review
9. **Set Up Alerting**: Configure SNS topics and CloudWatch alarms for critical events like failover, high CPU, or storage thresholds
10. **Use DB Activity Streams**: Enable `cluster_activity_stream` for real-time monitoring of database activity for compliance and security

### High Availability and Reliability

1. **Deploy Across Multiple AZs**: Provision at least two instances (or use `availability_zones`) so the cluster spans multiple AZs for fault tolerance
2. **Test Failover Scenarios**: Regularly test failover procedures by manually triggering failovers during maintenance windows
3. **Monitor Replication Lag**: Set up alarms for replica lag to detect replication issues before they impact availability
4. **Use Health Checks**: Implement application-level health checks that verify database connectivity and query execution
5. **Configure Appropriate Timeouts**: Set connection and query timeouts in applications to handle transient failures gracefully
6. **Plan for Capacity**: Monitor growth trends and plan for capacity increases before hitting limits
7. **Implement Circuit Breakers**: Use circuit breaker patterns in applications to prevent cascading failures during database issues

### Development and Deployment

1. **Use Terraform State Management**: Store Terraform state in S3 with state locking for team collaboration
2. **Version Control Configuration**: Keep all Terraform configurations in version control with proper branching strategies
3. **Separate Environments**: Use separate Aurora clusters for development, staging, and production environments
4. **Parameterize Configurations**: Use Terraform variables and separate tfvars files for environment-specific configurations
5. **Apply Changes Incrementally**: Make small, incremental changes and test thoroughly before applying to production
6. **Use Terraform Plan**: Always review `terraform plan` output before applying changes to production clusters
7. **Pin Module Version**: Pin `version = "~> 10.3"` (or tighter) to avoid unintended upgrades, especially across major versions with breaking changes
8. **Automate with CI/CD**: Integrate Terraform deployments into CI/CD pipelines with proper approval gates for production

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds-aurora
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds-aurora/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-rds-aurora/tree/master/examples
- **Changelog**: https://github.com/terraform-aws-modules/terraform-aws-rds-aurora/blob/master/CHANGELOG.md
- **AWS Aurora User Guide**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/
- **AWS Aurora PostgreSQL**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.AuroraPostgreSQL.html
- **AWS Aurora MySQL**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.AuroraMySQL.html
- **Aurora Serverless v2**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html
- **Aurora Limitless Database**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-limitless.html
- **Aurora Global Database**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html
- **Amazon Aurora DSQL**: https://docs.aws.amazon.com/aurora-dsql/latest/userguide/what-is-aurora-dsql.html
- **Performance Insights**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_PerfInsights.html
- **IAM Database Authentication**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.IAMDBAuth.html
- **RDS Aurora Pricing**: https://aws.amazon.com/rds/aurora/pricing/
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

## Notes for AI Agents

When using this module in automated workflows:

1. **Version Requirements**: Requires Terraform >= 1.11.1 and AWS Provider >= 6.54 (as of module v10.3.0)
2. **Secrets Manager by Default**: `manage_master_user_password = true` is the default; credentials are stored in Secrets Manager, not Terraform state. It cannot be combined with `master_password_wo`
3. **Write-Only Password for Special Cases**: Aurora Limitless and Global Database secondary clusters do not support the managed secret — use `master_password_wo` + `master_password_wo_version` instead
4. **Encryption Enabled by Default**: `storage_encrypted = true` is the default; no action needed for basic encryption
5. **`name` and `engine` Must Be Set**: Both default to empty/`null` but are functionally required for cluster creation
6. **Instance Configuration**: Define instances using the `instances` map; at least one instance is typically required for provisioned/Serverless v2 clusters (Limitless uses `shard_group` instead)
7. **Network Configuration**: Either provide an existing `db_subnet_group_name`, or set `create_db_subnet_group = true` together with `subnets` (note: `create_db_subnet_group` defaults to `false`, unlike many other terraform-aws-modules)
8. **Security Groups**: Module creates a security group by default (`create_security_group = true`); use `security_group_ingress_rules`/`security_group_egress_rules` to define access, or supply `vpc_security_group_ids` for existing ones
9. **Autoscaling Setup**: Enable with `autoscaling_enabled = true` and set `autoscaling_min_capacity`, `autoscaling_max_capacity`, `autoscaling_target_cpu` (or `autoscaling_target_connections`)
10. **Heterogeneous Clusters**: Override `instance_class` per instance in the `instances` map; use `promotion_tier` for failover priority
11. **Engine Selection**: Use `aurora-postgresql` for PostgreSQL, `aurora-mysql` for MySQL; always specify `engine_version` explicitly
12. **Monitoring**: Use `cluster_monitoring_interval` (not `monitoring_interval`, which is not a top-level variable — it only exists per-instance inside `instances`); add log types to `enabled_cloudwatch_logs_exports`
13. **Production Settings**: Set `deletion_protection = true`, keep `skip_final_snapshot = false`, and configure an appropriate `backup_retention_period`
14. **Tagging**: Apply consistent tags via `tags` (and `cluster_tags` if tagging only the cluster resource, e.g., for AWS Instance Scheduler)
15. **Global Clusters**: Create an `aws_rds_global_cluster` resource, reference it via `global_cluster_identifier` on the primary, and set `is_primary_cluster = false` plus `source_region` on secondary-region module calls
16. **Limitless Clusters**: Set `cluster_scalability_type = "limitless"` and provide `shard_group { identifier, max_acu, ... }`; not compatible with `manage_master_user_password`
17. **DSQL Clusters**: Use the `dsql` submodule (`//modules/dsql`) for distributed SQL — it is a distinct resource type (`aws_dsql_cluster`), not part of the top-level `aws_rds_cluster` resources
