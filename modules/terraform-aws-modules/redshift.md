# Terraform AWS Redshift Module

## Module Information

- **Module Name**: `redshift`
- **Module ID**: `terraform-aws-modules/redshift/aws`
- **Source**: `terraform-aws-modules/redshift/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-redshift
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/redshift/aws/latest
- **Latest Version**: 7.1.0
- **Purpose**: Creates and manages a single AWS Redshift data warehouse cluster together with its parameter group, subnet group, optional security group, and supporting automation (scheduled actions, usage limits, managed VPC endpoints, snapshots, logging)
- **Service**: AWS Redshift (Managed Data Warehouse Service)
- **Category**: Analytics, Database, Data Warehousing
- **Keywords**: redshift, data-warehouse, analytics, mpp, columnar-storage, olap, business-intelligence, kms-encryption, secrets-manager, cluster, vpc-security-group, ra3, scheduled-actions, snapshot, spectrum
- **Use For**: Enterprise data warehousing, business intelligence reporting, OLAP workloads, data lake integration via Spectrum, ETL pipeline destinations, historical data analysis, ad-hoc SQL queries at scale, cost-optimized on/off analytics clusters

## Description

This Terraform module provisions a complete AWS Redshift data warehouse cluster, including the cluster resource itself plus optional parameter group, subnet group, and security group (all can be created by the module or supplied externally via `create_*` toggles). It supports single-node development clusters and multi-node production clusters across the RA3, DC2, and DS2 node families, and can restore a cluster directly from an existing snapshot (`snapshot_identifier`/`snapshot_arn`) instead of creating an empty database.

AWS Redshift is a fully managed, petabyte-scale data warehouse service that delivers fast query performance on large datasets using columnar storage and massively parallel processing (MPP). It is SQL-compatible and integrates with BI tools, data visualization platforms, ETL pipelines, and (via Redshift Spectrum) data lakes in S3.

The module defaults to security best practices: AWS Secrets Manager manages the admin credentials out of the box (`manage_master_password = true`), a dedicated security group is created for the cluster when a `vpc_id` is supplied, and KMS encryption, enhanced VPC routing, automatic password rotation, and Multi-AZ (RA3) are all available as opt-in flags. It also exposes advanced operational features: scheduled actions for automatic pause/resume/resize, usage limits for concurrency scaling and Spectrum spend, managed VPC endpoints (RA3 only), authentication profiles for federated/IdP login, CloudWatch or S3 audit logging, and cross-region snapshot copying. Version 7.0 introduced a breaking change set (Terraform >= 1.11, AWS provider >= 6.27) that replaced module-generated random passwords with a write-only `master_password_wo`/`master_password_wo_version` pair and restructured several nested-object variables — see the Compatibility notes before generating code against this module.

## Key Features

- **Managed Master Password by Default**: AWS Secrets Manager owns the admin credentials out of the box (`manage_master_password = true`); no plaintext password in state
- **Write-Only Password Support**: Optional `master_password_wo` / `master_password_wo_version` write-only attributes (Terraform >= 1.11) let you supply your own password without ever persisting it in state
- **Automatic Secret Rotation**: Built-in Secrets Manager rotation via `manage_master_password_rotation`, scheduled by day-interval or by cron/rate expression
- **Module-Managed Security Group**: Creates and manages its own security group (`create_security_group`, default `true`) with rules expressed as `security_group_ingress_rules` / `security_group_egress_rules` maps of `aws_vpc_security_group_ingress_rule` / `egress_rule` resources (not inline SG rules)
- **Flexible Cluster Topology**: Single-node and multi-node clusters across RA3, DC2, and DS2 node types
- **Restore From Snapshot**: Provision a cluster directly from an existing snapshot via `snapshot_identifier` or `snapshot_arn`
- **Encryption at Rest**: KMS-based encryption for cluster data and the Secrets Manager secret, using customer-managed keys
- **Enhanced VPC Routing**: Forces COPY/UNLOAD traffic through the VPC for network-level control
- **Multi-AZ & AZ Relocation**: High-availability options available on RA3 clusters
- **Parameter Group & Subnet Group Management**: Creates or reuses parameter/subnet groups via `create_parameter_group` / `create_subnet_group` toggles
- **Snapshot Automation**: Automated and manual snapshot retention, scheduled snapshots, and cross-region snapshot copy
- **Scheduled Actions**: Pause, resume, and resize the cluster on a cron/rate schedule for cost control
- **Usage Limits**: Guardrails on concurrency scaling and Redshift Spectrum spend, with configurable breach actions
- **Managed VPC Endpoints**: Private cross-VPC access to RA3 clusters
- **Authentication Profiles**: JDBC/ODBC driver authentication profiles for federated/IdP login
- **Flexible Logging**: Connection, user, and user-activity logs to S3 or CloudWatch with configurable retention
- **IAM Role Association**: Attach up to 10 IAM roles for S3/Glue/Spectrum access
- **Per-Resource Region Override**: `region` variable targets a different AWS region than the provider default without a provider alias
- **Comprehensive Tagging**: Tagging support for every resource the module creates, including generated sub-resources

## Main Use Cases

1. **Enterprise Data Warehousing**: Centralize and analyze large volumes of structured data from multiple business systems
2. **Business Intelligence Reporting**: Power BI dashboards and analytical reports with fast query performance
3. **OLAP Workloads**: Execute complex analytical and multidimensional queries
4. **Data Lake Integration**: Query data in S3 using Redshift Spectrum alongside warehouse data
5. **ETL Pipeline Destinations**: Serve as the target for data transformation and loading workflows
6. **Historical Data Analysis**: Store and analyze years of transactional and operational data
7. **Cost-Optimized Analytics**: Use scheduled pause/resume/resize to cut costs for non-24/7 workloads
8. **Secure Analytics Platform**: Encrypted, VPC-isolated data warehouse with audit logging and rotated credentials

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| **Cluster Core** | | | |
| `create` | `bool` | `true` | Determines whether the cluster and all associated resources are created |
| `region` | `string` | `null` | AWS region for created resources if different from the provider region |
| `cluster_identifier` | `string` | `""` (required) | Unique identifier for the cluster (must be lowercase) |
| `node_type` | `string` | `""` (required) | Node type, e.g. `ra3.xlplus`, `dc2.large`, `ds2.xlarge` |
| `number_of_nodes` | `number` | `1` | Number of compute nodes; values > 1 switch `cluster_type` to multi-node |
| `cluster_version` | `string` | `null` | Redshift engine version to deploy on the cluster |
| `database_name` | `string` | `null` | Initial database name (defaults to `dev` if omitted) |
| `allow_version_upgrade` | `bool` | `null` (AWS default `true`) | Allow major engine version upgrades during the maintenance window |
| **Credentials & Rotation** | | | |
| `master_username` | `string` | `"awsuser"` | Master DB user account name |
| `manage_master_password` | `bool` | `true` | Use AWS Secrets Manager to manage admin credentials; conflicts with `master_password_wo` |
| `master_password_wo` | `string` | `null` | Write-only master password; only applied when `manage_master_password = false` and no `snapshot_identifier` |
| `master_password_wo_version` | `string` | `null` | Bump this value to trigger a `master_password_wo` update |
| `master_password_secret_kms_key_id` | `string` | `null` | KMS key used to encrypt the Secrets Manager credentials secret |
| `manage_master_password_rotation` | `bool` | `false` | Enable automatic Secrets Manager rotation of the admin credentials |
| `master_password_rotation_automatically_after_days` | `number` | `null` | Rotation interval in days (alternative to a schedule expression) |
| `master_password_rotation_schedule_expression` | `string` | `null` | `cron()`/`rate()` rotation schedule (alternative to days) |
| **Encryption & Availability** | | | |
| `encrypted` | `bool` | `null` | Enable encryption at rest |
| `kms_key_arn` | `string` | `null` | Customer-managed KMS key ARN for cluster encryption (requires `encrypted = true`) |
| `enhanced_vpc_routing` | `bool` | `null` | Force all COPY/UNLOAD traffic through the VPC |
| `multi_az` | `bool` | `null` | Enable Multi-AZ cluster configuration |
| `availability_zone_relocation_enabled` | `bool` | `null` | Allow automatic AZ relocation (RA3 only) |
| `publicly_accessible` | `bool` | `null` | Allow public network access |
| `port` | `number` | `5439` | Cluster connection port (also the default for security group rule ports) |
| **Security Group** (new in v7.0) | | | |
| `create_security_group` | `bool` | `true` | Create a dedicated security group for the cluster |
| `vpc_id` | `string` | `""` | VPC ID for the created security group; required when `create_security_group = true` |
| `security_group_name` | `string` | `""` | Name (or name prefix) for the created security group |
| `security_group_ingress_rules` | `map(object)` | `{}` | Ingress rules (`cidr_ipv4`, `ip_protocol`, `from_port`/`to_port` default to `port`) |
| `security_group_egress_rules` | `map(object)` | `{}` | Egress rules for the created security group, same shape as ingress |
| `vpc_security_group_ids` | `list(string)` | `[]` | Additional existing security group IDs to attach alongside the module-created one |
| **Subnet & Parameter Groups** | | | |
| `create_subnet_group` | `bool` | `true` | Create a Redshift subnet group |
| `subnet_ids` | `list(string)` | `[]` | VPC subnet IDs for the subnet group; required when `create_subnet_group = true` |
| `create_parameter_group` | `bool` | `true` | Create a Redshift parameter group |
| `parameter_group_family` | `string` | `"redshift-2.0"` | Parameter group family version |
| `parameter_group_parameters` | `list(object({name,value}))` | `null` | List of `{ name, value }` parameter group settings (list, not a map) |
| **Backup & Restore** | | | |
| `automated_snapshot_retention_period` | `number` | `null` | Days to retain automated snapshots (`0` disables them) |
| `preferred_maintenance_window` | `string` | `"sat:10:00-sat:10:30"` | Weekly maintenance window (UTC) |
| `skip_final_snapshot` | `bool` | `true` | Skip the final snapshot on cluster deletion |
| `final_snapshot_identifier` | `string` | `null` | Final snapshot identifier (requires `skip_final_snapshot = false`) |
| `snapshot_identifier` | `string` | `null` | Restore the cluster from an existing snapshot; conflicts with `snapshot_arn` |
| `snapshot_arn` | `string` | `null` | Restore from a snapshot ARN (cross-account/region); conflicts with `snapshot_identifier` |
| `snapshot_copy` | `object` | `null` | Cross-region automatic snapshot copy config (`destination_region`, `grant_name`, ...) |
| **IAM** | | | |
| `iam_role_arns` | `list(string)` | `[]` | IAM role ARNs to associate with the cluster (max 10) |
| `default_iam_role_arn` | `string` | `null` | Default IAM role ARN used for COPY/UNLOAD/Spectrum when none is specified |
| **Automation & Limits** | | | |
| `snapshot_schedule` | `object` | `null` | Snapshot schedule definition to create and associate with the cluster |
| `scheduled_actions` | `map(object)` | `{}` | Pause/resume/resize automation; target actions nest under `target_action` |
| `create_scheduled_action_iam_role` | `bool` | `false` | Auto-create the IAM role used by scheduled actions |
| `endpoint_access` | `map(object)` | `{}` | Managed VPC endpoint definitions (RA3 only) |
| `usage_limits` | `map(object)` | `{}` | Usage limits for concurrency scaling and Spectrum |
| `authentication_profiles` | `map(object)` | `{}` | Federated/IdP authentication profiles (JSON `content`) |
| **Logging** | | | |
| `logging` | `object` | `null` | Audit logging config (`bucket_name`/`log_destination_type`/`log_exports`/`s3_key_prefix`); presence of this object enables logging, there is no separate `enable` flag |
| `create_cloudwatch_log_group` | `bool` | `false` | Create a CloudWatch log group for each `logging.log_exports` entry |
| `cloudwatch_log_group_retention_in_days` | `number` | `0` | CloudWatch log retention in days |
| **Tags** | | | |
| `tags` | `map(string)` | `{}` | Tags applied to all resources created by the module |

## Main Outputs

| Output | Description |
|--------|-------------|
| `cluster_arn` | The Redshift cluster ARN |
| `cluster_id` | The Redshift cluster ID |
| `cluster_identifier` | The Redshift cluster identifier |
| `cluster_endpoint` | The connection endpoint (`hostname:port`) |
| `cluster_hostname` | The hostname of the cluster (endpoint without the port) |
| `cluster_dns_name` | The DNS name of the cluster |
| `cluster_port` | The port the cluster responds on |
| `cluster_database_name` | The name of the default database |
| `cluster_node_type` | The type of nodes in the cluster |
| `cluster_type` | `single-node` or `multi-node` |
| `cluster_version` | The version of the Redshift engine software |
| `cluster_availability_zone` | The availability zone of the cluster |
| `cluster_encrypted` | Whether the data in the cluster is encrypted |
| `cluster_nodes` | The nodes in the cluster (`node_role`, `private_ip_address`, `public_ip_address`) |
| `cluster_master_username` | The master username (sensitive) |
| `cluster_master_password` | The master password, only populated when not Secrets Manager-managed (sensitive) |
| `master_password_secret_arn` | ARN of the managed master password secret |
| `cluster_secretsmanager_secret_rotation_enabled` | Whether automatic secret rotation is enabled |
| `cluster_vpc_security_group_ids` | All VPC security group IDs associated with the cluster, including the module-created one - use this since there is no dedicated `security_group_id`/`security_group_arn` output |
| `parameter_group_arn` / `parameter_group_id` | ARN / name of the parameter group |
| `subnet_group_arn` / `subnet_group_id` | ARN / ID of the subnet group |
| `snapshot_schedule_arn` | ARN of the snapshot schedule |
| `scheduled_actions` | Map of scheduled action details |
| `scheduled_action_iam_role_arn` | Scheduled actions IAM role ARN |
| `endpoint_access` | Map of managed VPC endpoints and their attributes |
| `usage_limits` | Map of usage limits and their attributes |
| `authentication_profiles` | Map of authentication profiles and their attributes |

## Usage Examples

### Example 1: Minimal Development Cluster

```hcl
module "redshift" {
  source  = "terraform-aws-modules/redshift/aws"
  version = "~> 7.1"

  cluster_identifier = "dev-analytics"
  node_type          = "dc2.large"
  number_of_nodes    = 1

  database_name   = "analytics_dev"
  master_username = "admin"

  # Secrets Manager-managed password (default behavior)
  manage_master_password = true

  # Network - the module creates its own security group since vpc_id is set
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  security_group_ingress_rules = {
    vpc_access = {
      cidr_ipv4   = module.vpc.vpc_cidr_block
      description = "Redshift access from within the VPC"
      # from_port/to_port default to var.port (5439) when omitted
    }
  }

  encrypted           = true
  publicly_accessible = false
  skip_final_snapshot = true

  tags = {
    Environment = "development"
    Terraform   = "true"
  }
}
```

### Example 2: Production Multi-Node Cluster with Full Security

```hcl
resource "aws_kms_key" "redshift" {
  description             = "KMS key for Redshift encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

module "redshift_production" {
  source  = "terraform-aws-modules/redshift/aws"
  version = "~> 7.1"

  cluster_identifier = "prod-analytics"
  node_type          = "ra3.xlplus"
  number_of_nodes    = 3

  database_name   = "analytics_prod"
  master_username = "admin"

  # Secrets Manager-managed password with automatic rotation
  manage_master_password                            = true
  manage_master_password_rotation                   = true
  master_password_rotation_automatically_after_days = 90
  master_password_secret_kms_key_id                 = aws_kms_key.redshift.id

  encrypted   = true
  kms_key_arn = aws_kms_key.redshift.arn

  # High availability (RA3 only)
  availability_zone_relocation_enabled = true
  enhanced_vpc_routing                 = true
  publicly_accessible                  = false

  # Network - module-managed security group
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  security_group_ingress_rules = {
    vpc_access = {
      cidr_ipv4   = module.vpc.vpc_cidr_block
      description = "VPC access"
    }
  }

  # IAM roles for S3/Glue access
  iam_role_arns        = [aws_iam_role.redshift_s3.arn]
  default_iam_role_arn = aws_iam_role.redshift_s3.arn

  # Parameter group with security settings (list of objects, not a map)
  parameter_group_parameters = [
    { name = "require_ssl", value = "true" },
    { name = "enable_user_activity_logging", value = "true" },
    { name = "max_concurrency_scaling_clusters", value = "3" },
  ]

  # Backups
  automated_snapshot_retention_period = 7
  skip_final_snapshot                 = false
  final_snapshot_identifier           = "prod-analytics-final"

  # Cross-region snapshot copy - the grant must exist in the destination region
  snapshot_copy = {
    destination_region = "us-west-2"
    grant_name          = aws_redshift_snapshot_copy_grant.us_west_2.snapshot_copy_grant_name
  }

  # CloudWatch audit logging
  logging = {
    log_destination_type = "cloudwatch"
    log_exports           = ["connectionlog", "userlog", "useractivitylog"]
  }
  create_cloudwatch_log_group            = true
  cloudwatch_log_group_retention_in_days = 30
  cloudwatch_log_group_kms_key_id        = aws_kms_key.redshift.id

  tags = {
    Environment = "production"
    CostCenter  = "analytics"
    Backup      = "daily"
  }
}

# Snapshot copy grants must be created with a provider aliased to the destination region
provider "aws" {
  alias  = "us_west_2"
  region = "us-west-2"
}

resource "aws_redshift_snapshot_copy_grant" "us_west_2" {
  provider = aws.us_west_2

  snapshot_copy_grant_name = "prod-analytics-us-west-2"
  kms_key_id                = aws_kms_key.redshift_us_west_2.arn
}
```

### Example 3: Cost-Optimized Cluster with Scheduled Pause/Resume/Resize

```hcl
module "redshift_scheduled" {
  source  = "terraform-aws-modules/redshift/aws"
  version = "~> 7.1"

  cluster_identifier = "scheduled-analytics"
  node_type          = "ra3.xlplus"
  number_of_nodes    = 2

  database_name           = "analytics"
  master_username         = "admin"
  manage_master_password  = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  security_group_ingress_rules = {
    vpc_access = {
      cidr_ipv4 = module.vpc.vpc_cidr_block
    }
  }

  encrypted            = true
  enhanced_vpc_routing = true

  # Scheduled actions for cost optimization - target actions nest under `target_action`
  create_scheduled_action_iam_role = true

  scheduled_actions = {
    pause_nightly = {
      description = "Pause cluster nightly to save cost"
      schedule    = "cron(0 22 * * ? *)"
      target_action = {
        pause_cluster = true
      }
    }
    resume_weekday = {
      description = "Resume cluster on weekday mornings"
      schedule    = "cron(0 6 ? * MON-FRI *)"
      target_action = {
        resume_cluster = true
      }
    }
    scale_up_monday = {
      description = "Scale up for the heavy Monday workload"
      schedule    = "cron(0 8 ? * MON *)"
      target_action = {
        resize_cluster = {
          node_type       = "ra3.xlplus"
          number_of_nodes = 4
        }
      }
    }
    scale_down_friday = {
      description = "Scale back down before the weekend"
      schedule    = "cron(0 18 ? * FRI *)"
      target_action = {
        resize_cluster = {
          node_type       = "ra3.xlplus"
          number_of_nodes = 2
        }
      }
    }
  }

  # Usage limits
  usage_limits = {
    concurrency_scaling = {
      feature_type  = "concurrency-scaling"
      limit_type    = "time"
      amount        = 60 # minutes per day
      breach_action = "log"
    }
    spectrum_daily = {
      feature_type  = "spectrum"
      limit_type    = "data-scanned"
      amount        = 1000 # TB
      period        = "daily"
      breach_action = "emit-metric"
    }
  }

  tags = {
    Environment   = "production"
    CostOptimized = "true"
  }
}
```

### Example 4: Cluster with Managed VPC Endpoint (RA3 Only)

```hcl
module "redshift_endpoint" {
  source  = "terraform-aws-modules/redshift/aws"
  version = "~> 7.1"

  cluster_identifier = "endpoint-analytics"
  node_type          = "ra3.xlplus"
  number_of_nodes    = 2

  database_name           = "analytics"
  master_username         = "admin"
  manage_master_password  = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  security_group_ingress_rules = {
    vpc_access = {
      cidr_ipv4 = module.vpc.vpc_cidr_block
    }
  }

  encrypted            = true
  enhanced_vpc_routing = true
  publicly_accessible  = false

  # Managed VPC endpoint (RA3 only) - typically placed in its own subnet group
  endpoint_access = {
    private_endpoint = {
      subnet_group_name      = aws_redshift_subnet_group.endpoint.id
      vpc_security_group_ids = [aws_security_group.redshift_endpoint.id]
    }
  }

  tags = {
    Environment = "production"
  }
}

resource "aws_redshift_subnet_group" "endpoint" {
  name       = "endpoint-analytics-endpoint"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redshift_endpoint" {
  name_prefix = "redshift-endpoint-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }
}
```

### Example 5: Restore from Snapshot

```hcl
module "redshift_restored" {
  source  = "terraform-aws-modules/redshift/aws"
  version = "~> 7.1"

  cluster_identifier = "restored-analytics"
  node_type          = "ra3.xlplus"

  # Restore from an existing snapshot instead of creating an empty database
  snapshot_identifier = "prod-analytics-2024-01-15"

  # Still safe to request a Secrets Manager-managed password after restore
  manage_master_password = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  security_group_ingress_rules = {
    vpc_access = {
      cidr_ipv4 = module.vpc.vpc_cidr_block
    }
  }

  encrypted = true

  tags = {
    Environment  = "staging"
    RestoredFrom = "prod-snapshot"
  }
}
```

### Example 6: Bring Your Own Security Group and Write-Only Password

```hcl
module "redshift_custom_sg" {
  source  = "terraform-aws-modules/redshift/aws"
  version = "~> 7.1"

  cluster_identifier = "custom-sg-analytics"
  node_type          = "ra3.xlplus"

  database_name   = "analytics"
  master_username = "admin"

  # Bring your own credentials via a write-only attribute (never persisted in state)
  manage_master_password     = false
  master_password_wo         = var.redshift_master_password # declare as `ephemeral = true` in the caller
  master_password_wo_version = 1                             # bump to rotate the password

  # Bring your own security group instead of letting the module create one
  create_security_group  = false
  vpc_security_group_ids = [aws_security_group.redshift.id]
  subnet_ids              = module.vpc.database_subnets

  encrypted = true

  tags = {
    Environment = "production"
  }
}
```

## Best Practices

### Security and Access Control

1. **Keep the Default Managed Password**: Leave `manage_master_password = true` (the default since v7.0) so Secrets Manager owns the admin credentials; only switch to `master_password_wo` if you have an external secrets pipeline
2. **Never Reference the Removed `master_password` Argument**: It was renamed to the write-only `master_password_wo`/`master_password_wo_version` pair in v7.0, and random-password generation support was removed entirely
3. **Enable Password Rotation**: Set `manage_master_password_rotation = true` with `master_password_rotation_automatically_after_days` (e.g. `90`) or a `master_password_rotation_schedule_expression`
4. **Always Encrypt**: Set `encrypted = true` with a customer-managed `kms_key_arn`
5. **Use Enhanced VPC Routing**: Set `enhanced_vpc_routing = true` to route COPY/UNLOAD through the VPC
6. **Disable Public Access**: Set `publicly_accessible = false` for production clusters
7. **Prefer the Module-Managed Security Group**: Leave `create_security_group = true` and pass `vpc_id`; define narrow `security_group_ingress_rules` using `cidr_ipv4`/`ip_protocol` (not the legacy `cidr_blocks`/`protocol` list attributes) instead of wide-open CIDR ranges
8. **Require SSL and Enable Activity Logging**: Set `require_ssl` and `enable_user_activity_logging` via `parameter_group_parameters` for audit trails
9. **Use IAM Roles, Not Static Credentials**: Attach roles via `iam_role_arns`/`default_iam_role_arn` for S3/Glue/Spectrum access (maximum 10 roles per cluster)

### High Availability and Backup

1. **Use Multi-AZ**: Enable `multi_az = true` for production clusters on supported node types
2. **Enable AZ Relocation**: Set `availability_zone_relocation_enabled = true` for RA3 clusters
3. **Configure Snapshot Retention**: Set `automated_snapshot_retention_period` to 7-35 days based on RPO
4. **Enable Final Snapshots**: Set `skip_final_snapshot = false` with `final_snapshot_identifier` for production
5. **Cross-Region Snapshots**: Configure `snapshot_copy`, remembering the destination-region grant must be created separately via a provider alias
6. **Restore, Don't Recreate**: Use `snapshot_identifier`/`snapshot_arn` to stand up a cluster from an existing snapshot rather than manually reloading data

### Performance and Cost Optimization

1. **Choose the Right Node Type**: RA3 for production (independent compute/storage scaling), DC2/DS2 for smaller or dev/test workloads
2. **Use Scheduled Actions**: Configure `scheduled_actions` (nested under `target_action`) for pause/resume/resize during off-hours
3. **Set Usage Limits**: Configure `usage_limits` for concurrency scaling and Spectrum with `breach_action = "emit-metric"` for cost alerts
4. **Enable CloudWatch or S3 Logging**: Configure `logging` with `log_exports` for query and connection visibility

### Compatibility and Upgrades

1. **Match the Version Constraints**: Terraform >= 1.11 and AWS provider >= 6.27 are required for the write-only (`_wo`) attributes this module uses; pin `version = "~> 7.1"` in the module source
2. **Read the Upgrade Guide Before Bumping Major Versions**: `docs/UPGRADE-7.0.md` documents the `master_password` -> `master_password_wo` rename plus the restructuring of `endpoint_access` and `snapshot_schedule` into nested objects when migrating from 6.x

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-redshift
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/redshift/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-redshift/tree/master/examples/complete
- **Upgrade Guide (v6 -> v7)**: https://github.com/terraform-aws-modules/terraform-aws-redshift/blob/master/docs/UPGRADE-7.0.md
- **AWS Redshift Documentation**: https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html
- **Redshift Best Practices**: https://docs.aws.amazon.com/redshift/latest/dg/best-practices.html
- **Redshift Security**: https://docs.aws.amazon.com/redshift/latest/mgmt/security.html
- **Redshift Spectrum**: https://docs.aws.amazon.com/redshift/latest/dg/c-using-spectrum.html
- **Redshift Pricing**: https://aws.amazon.com/redshift/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Trust the Default Password Management**: `manage_master_password` defaults to `true` - do not set `master_password_wo` unless you also explicitly set `manage_master_password = false`, otherwise it is silently ignored
2. **Never Emit the Old `master_password` Argument**: It does not exist in v7.x; use `master_password_wo` + `master_password_wo_version` (write-only, requires Terraform >= 1.11) instead
3. **Version Constraints Are Load-Bearing**: Generate a root `terraform` block requiring `>= 1.11` and an `aws` provider `>= 6.27` alongside `version = "~> 7.1"` for the module, or apply will fail
4. **Let the Module Own the Security Group by Default**: `create_security_group = true` (default) plus `vpc_id` is usually simpler than supplying `vpc_security_group_ids`; ingress/egress rule objects use `cidr_ipv4`/`ip_protocol`, not `cidr_blocks`/`protocol`, and `from_port`/`to_port` default to `port` (5439) when omitted
5. **There Is No Dedicated Security Group Output**: Read the created security group ID from `cluster_vpc_security_group_ids`, not a `security_group_id` output
6. **`scheduled_actions` Nests Under `target_action`**: `pause_cluster`, `resume_cluster`, and `resize_cluster` are keys inside each action's `target_action` object, not top-level keys
7. **`parameter_group_parameters` Is a List, Not a Map**: Use `[{ name = "...", value = "..." }, ...]`
8. **Configure Network Inputs Together**: Provide both `vpc_id` and `subnet_ids` (required respectively when `create_security_group`/`create_subnet_group` default to `true`)
9. **Enable Encryption for Production**: Set `encrypted = true` and provide `kms_key_arn`
10. **Configure Backups**: Set `automated_snapshot_retention_period` (7+ days) and `skip_final_snapshot = false` for production
11. **Tag Resources**: Apply comprehensive tags including Environment, CostCenter, and Application
12. **Use Scheduled Actions and Usage Limits**: Configure pause/resume/resize and Spectrum/concurrency-scaling limits to control cost
13. **RA3-Only Features**: Use `availability_zone_relocation_enabled`, `multi_az`, and `endpoint_access` only with RA3 node types
14. **Snapshot Restores Skip `master_password_wo`**: When `snapshot_identifier` is set, the write-only password path is not applied - only `manage_master_password` takes effect
