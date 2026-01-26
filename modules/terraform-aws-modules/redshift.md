# Terraform AWS Redshift Module

## Module Information

- **Module Name**: `redshift`
- **Source**: `terraform-aws-modules/redshift/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-redshift
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/redshift/aws/latest
- **Latest Version**: 7.1.0
- **Purpose**: Creates and manages AWS Redshift data warehouse clusters with comprehensive configuration for security, high availability, automated operations, and networking
- **Service**: AWS Redshift (Managed Data Warehouse Service)
- **Category**: Analytics, Database, Data Warehousing
- **Keywords**: redshift, data-warehouse, analytics, mpp, columnar-storage, sql, business-intelligence, kms-encryption, vpc-routing, snapshot, cluster, parameter-group, scheduled-actions, secrets-manager, multi-az
- **Use For**: Enterprise data warehousing, business intelligence reporting, OLAP workloads, data lake integration, ETL pipeline destinations, historical data analysis, ad-hoc SQL queries at scale

## Description

This Terraform module provides complete deployment and management of AWS Redshift data warehouse clusters with extensive configuration capabilities for cluster topology, security, networking, and operational features. The module creates Redshift clusters with configurable node types and cluster sizes, manages associated resources including parameter groups for cluster optimization, subnet groups for VPC placement, and security groups for network access control. It supports both single-node development clusters and multi-node production clusters with automatic distribution of data across nodes for parallel query processing.

AWS Redshift is a fully managed, petabyte-scale data warehouse service designed for fast query performance on large datasets using columnar storage and massively parallel processing (MPP) architecture. The service provides compatibility with standard SQL and integrates seamlessly with business intelligence tools, data visualization platforms, and ETL pipelines.

The module enables production-grade Redshift clusters with security best practices including KMS encryption, AWS Secrets Manager integration for master password management with automatic rotation, enhanced VPC routing, automated snapshot management, and Multi-AZ support for RA3 clusters. It supports advanced features such as scheduled actions for automatic cluster pause/resume/resize, usage limits for concurrency scaling and Spectrum, managed VPC endpoints (RA3 only), CloudWatch logging, and cross-region snapshot copying.

## Key Features

- **Managed Master Password**: AWS Secrets Manager integration with automated password rotation support
- **Multi-AZ Support**: High availability configuration with automatic AZ relocation (RA3 clusters)
- **Flexible Cluster Configuration**: Support for single-node and multi-node topologies with RA3, DC2, DS2 node types
- **Encryption at Rest**: KMS-based encryption for data, logs, and secrets with customer-managed keys
- **Enhanced VPC Routing**: Force all COPY and UNLOAD traffic through VPC for security
- **Security Group Management**: Built-in ingress/egress rule definitions without separate resources
- **Parameter Group Management**: Create and manage cluster parameter groups for performance tuning
- **Subnet Group Configuration**: Define VPC subnet groups for cluster placement
- **Automated Snapshots**: Configurable retention with snapshot schedules and cross-region copying
- **Scheduled Actions**: Automatic cluster pause, resume, and resize operations on schedule
- **Usage Limits**: Set limits on concurrency scaling and Spectrum query usage
- **Managed VPC Endpoints**: Create dedicated VPC endpoints for RA3 cluster access
- **CloudWatch Logging**: Connection logs, user logs, and user activity logs with retention
- **Authentication Profiles**: External identity provider integration support
- **IAM Role Association**: Attach up to 10 IAM roles for S3, Glue, and AWS service access
- **Comprehensive Tagging**: Full tagging support for all created resources

## Main Use Cases

1. **Enterprise Data Warehousing**: Centralize and analyze large volumes of structured data from multiple business systems
2. **Business Intelligence Reporting**: Power BI dashboards and analytical reports with fast query performance
3. **OLAP Workloads**: Execute complex analytical queries for multidimensional data analysis
4. **Data Lake Integration**: Query data in S3 using Redshift Spectrum alongside warehouse data
5. **ETL Pipeline Destinations**: Serve as target for data transformation and loading workflows
6. **Historical Data Analysis**: Store and analyze years of transactional and operational data
7. **Cost-Optimized Analytics**: Use scheduled pause/resume to reduce costs for non-24/7 workloads
8. **Secure Analytics Platform**: Encrypted, VPC-isolated data warehouse with audit logging

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `cluster_identifier` | `string` | required | Unique identifier for the cluster (must be lowercase) |
| `node_type` | `string` | required | Node type (e.g., ra3.xlplus, dc2.large, ra3.4xlarge) |
| `number_of_nodes` | `number` | `1` | Number of compute nodes (>1 triggers multi-node mode) |
| `database_name` | `string` | `null` | Initial database name (defaults to "dev") |
| `master_username` | `string` | `"awsuser"` | Master DB user account name |
| `manage_master_password` | `bool` | `true` | Use AWS Secrets Manager for password management |
| `master_password_wo` | `string` | `null` | Master password (8+ chars with upper, lower, number) |
| `manage_master_password_rotation` | `bool` | `false` | Enable automated master password rotation |
| `master_password_rotation_automatically_after_days` | `number` | `null` | Password rotation interval in days |
| `encrypted` | `bool` | `null` | Enable encryption at rest |
| `kms_key_arn` | `string` | `null` | KMS key ARN for encryption |
| `master_password_secret_kms_key_id` | `string` | `null` | KMS key for Secrets Manager secret |
| `vpc_id` | `string` | `""` | VPC ID for security group placement |
| `subnet_ids` | `list(string)` | `[]` | VPC subnet IDs for subnet group |
| `vpc_security_group_ids` | `list(string)` | `[]` | VPC security group IDs to associate |
| `enhanced_vpc_routing` | `bool` | `null` | Enable enhanced VPC routing |
| `multi_az` | `bool` | `null` | Enable Multi-AZ cluster configuration |
| `availability_zone_relocation_enabled` | `bool` | `null` | Enable automatic AZ relocation (RA3 only) |
| `port` | `number` | `5439` | Cluster connection port |
| `publicly_accessible` | `bool` | `null` | Allow public network access |
| `automated_snapshot_retention_period` | `number` | `null` | Days to retain automated snapshots (0=disabled) |
| `preferred_maintenance_window` | `string` | `"sat:10:00-sat:10:30"` | Weekly maintenance window (UTC) |
| `skip_final_snapshot` | `bool` | `true` | Skip final snapshot on deletion |
| `final_snapshot_identifier` | `string` | `null` | Final snapshot identifier |
| `iam_role_arns` | `list(string)` | `[]` | IAM Role ARNs to associate (max 10) |
| `default_iam_role_arn` | `string` | `null` | Default IAM role ARN |
| `parameter_group_family` | `string` | `"redshift-2.0"` | Parameter group family version |
| `parameter_group_parameters` | `list(object)` | `null` | Parameter group parameters |
| `snapshot_schedule` | `object` | `null` | Snapshot schedule configuration |
| `scheduled_actions` | `map(object)` | `{}` | Scheduled actions (pause/resume/resize) |
| `create_scheduled_action_iam_role` | `bool` | `false` | Create IAM role for scheduled actions |
| `endpoint_access` | `map(object)` | `{}` | Managed VPC endpoints (RA3 only) |
| `usage_limits` | `map(object)` | `{}` | Usage limits (concurrency scaling, Spectrum) |
| `logging` | `object` | `null` | Cluster logging configuration |
| `create_cloudwatch_log_group` | `bool` | `false` | Create CloudWatch log group |
| `cloudwatch_log_group_retention_in_days` | `number` | `null` | CloudWatch log retention days |
| `snapshot_copy` | `object` | `null` | Cross-region snapshot copy settings |
| `security_group_ingress_rules` | `map(object)` | `{}` | Security group ingress rules |
| `security_group_egress_rules` | `map(object)` | `{}` | Security group egress rules |
| `tags` | `map(string)` | `{}` | Tags for all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `cluster_arn` | The Redshift cluster ARN |
| `cluster_id` | The Redshift cluster ID |
| `cluster_identifier` | The Redshift cluster identifier |
| `cluster_endpoint` | The connection endpoint (hostname:port) |
| `cluster_hostname` | The hostname of the cluster |
| `cluster_dns_name` | The DNS name of the cluster |
| `cluster_port` | The port the cluster responds on |
| `cluster_database_name` | The name of the default database |
| `cluster_node_type` | The type of nodes in the cluster |
| `cluster_type` | The Redshift cluster type |
| `cluster_availability_zone` | The availability zone of the cluster |
| `cluster_encrypted` | Whether the data is encrypted |
| `cluster_version` | The version of Redshift engine software |
| `cluster_nodes` | The nodes in the cluster (role, IPs) |
| `cluster_master_username` | The master username (sensitive) |
| `cluster_master_password` | The master password (sensitive) |
| `master_password_secret_arn` | ARN of managed master password secret |
| `cluster_secretsmanager_secret_rotation_enabled` | Whether automatic rotation is enabled |
| `cluster_vpc_security_group_ids` | VPC security group IDs associated |
| `parameter_group_arn` | ARN of the parameter group |
| `parameter_group_id` | ID of the parameter group |
| `subnet_group_arn` | ARN of the subnet group |
| `subnet_group_id` | ID of the subnet group |
| `snapshot_schedule_arn` | ARN of the snapshot schedule |
| `scheduled_actions` | Map of scheduled action details |
| `scheduled_action_iam_role_arn` | Scheduled actions IAM role ARN |
| `endpoint_access` | Map of VPC endpoints and attributes |
| `usage_limits` | Map of usage limits and attributes |

## Usage Examples

### Example 1: Development Cluster with Secrets Manager

```hcl
module "redshift_dev" {
  source  = "terraform-aws-modules/redshift/aws"
  version = "~> 7.1"

  cluster_identifier = "dev-analytics"
  node_type          = "dc2.large"
  number_of_nodes    = 1

  database_name   = "analytics_dev"
  master_username = "admin"

  # Use Secrets Manager for password (recommended)
  manage_master_password = true

  # Network configuration
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  security_group_ingress_rules = {
    vpc_access = {
      from_port   = 5439
      to_port     = 5439
      protocol    = "tcp"
      cidr_blocks = [module.vpc.vpc_cidr_block]
      description = "VPC access"
    }
  }

  # Security
  encrypted           = true
  publicly_accessible = false

  # Dev settings - skip final snapshot
  skip_final_snapshot = true

  tags = {
    Environment = "development"
    Terraform   = "true"
  }
}
```

### Example 2: Production Multi-Node Cluster with Full Security

```hcl
# KMS key for Redshift encryption
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

  # Managed password with rotation
  manage_master_password                           = true
  manage_master_password_rotation                  = true
  master_password_rotation_automatically_after_days = 90
  master_password_secret_kms_key_id                = aws_kms_key.redshift.id

  # Encryption
  encrypted   = true
  kms_key_arn = aws_kms_key.redshift.arn

  # High availability (RA3 only)
  availability_zone_relocation_enabled = true
  enhanced_vpc_routing                 = true

  # Network
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  security_group_ingress_rules = {
    vpc_access = {
      from_port   = 5439
      to_port     = 5439
      protocol    = "tcp"
      cidr_blocks = [module.vpc.vpc_cidr_block]
      description = "VPC access"
    }
  }

  # IAM roles for S3 access
  iam_role_arns     = [aws_iam_role.redshift_s3.arn]
  default_iam_role_arn = aws_iam_role.redshift_s3.arn

  # Parameter group with security settings
  parameter_group_parameters = [
    { name = "require_ssl", value = "true" },
    { name = "enable_user_activity_logging", value = "true" },
    { name = "max_concurrency_scaling_clusters", value = "3" }
  ]

  # Backups
  automated_snapshot_retention_period = 7
  skip_final_snapshot                 = false
  final_snapshot_identifier           = "prod-analytics-final"

  # Cross-region snapshot copy
  snapshot_copy = {
    destination_region = "us-west-2"
    grant_name         = "prod-snapshot-copy-grant"
  }

  # CloudWatch logging
  logging = {
    enable      = true
    log_exports = ["connectionlog", "userlog", "useractivitylog"]
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
```

### Example 3: Cost-Optimized Cluster with Scheduled Pause/Resume

```hcl
module "redshift_scheduled" {
  source  = "terraform-aws-modules/redshift/aws"
  version = "~> 7.1"

  cluster_identifier = "scheduled-analytics"
  node_type          = "ra3.xlplus"
  number_of_nodes    = 2

  database_name              = "analytics"
  master_username            = "admin"
  manage_master_password     = true

  # Network
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  security_group_ingress_rules = {
    vpc_access = {
      from_port   = 5439
      to_port     = 5439
      protocol    = "tcp"
      cidr_blocks = [module.vpc.vpc_cidr_block]
    }
  }

  # Security
  encrypted            = true
  enhanced_vpc_routing = true

  # Scheduled actions for cost optimization
  create_scheduled_action_iam_role = true

  scheduled_actions = {
    # Pause at 10 PM UTC daily
    pause_nightly = {
      schedule      = "cron(0 22 * * ? *)"
      pause_cluster = true
    }
    # Resume at 6 AM UTC on weekdays
    resume_weekday = {
      schedule       = "cron(0 6 ? * MON-FRI *)"
      resume_cluster = true
    }
    # Scale up for heavy workload on Mondays
    scale_up_monday = {
      schedule = "cron(0 8 ? * MON *)"
      resize_cluster = {
        node_type       = "ra3.xlplus"
        number_of_nodes = 4
      }
    }
    # Scale down Friday evening
    scale_down_friday = {
      schedule = "cron(0 18 ? * FRI *)"
      resize_cluster = {
        node_type       = "ra3.xlplus"
        number_of_nodes = 2
      }
    }
  }

  # Usage limits
  usage_limits = {
    concurrency_scaling = {
      feature_type  = "concurrency-scaling"
      limit_type    = "time"
      amount        = 60  # minutes per day
      breach_action = "log"
    }
    spectrum_daily = {
      feature_type  = "spectrum"
      limit_type    = "data-scanned"
      amount        = 1000  # TB
      period        = "daily"
      breach_action = "emit-metric"
    }
  }

  tags = {
    Environment = "production"
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

  database_name          = "analytics"
  master_username        = "admin"
  manage_master_password = true

  # Network
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  security_group_ingress_rules = {
    vpc = {
      from_port   = 5439
      to_port     = 5439
      protocol    = "tcp"
      cidr_blocks = [module.vpc.vpc_cidr_block]
    }
  }

  # Security
  encrypted            = true
  enhanced_vpc_routing = true
  publicly_accessible  = false

  # Managed VPC endpoint (RA3 only)
  endpoint_access = {
    private_endpoint = {
      subnet_ids             = module.vpc.private_subnets
      vpc_security_group_ids = [aws_security_group.redshift_endpoint.id]
    }
  }

  tags = {
    Environment = "production"
  }
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

  # Restore from snapshot
  snapshot_identifier = "prod-analytics-2024-01-15"

  # Override snapshot settings with new password
  manage_master_password = true

  # Network (must match original or be compatible)
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  security_group_ingress_rules = {
    vpc_access = {
      from_port   = 5439
      to_port     = 5439
      protocol    = "tcp"
      cidr_blocks = [module.vpc.vpc_cidr_block]
    }
  }

  # Keep original encryption
  encrypted = true

  tags = {
    Environment = "staging"
    RestoredFrom = "prod-snapshot"
  }
}
```

## Best Practices

### Security and Access Control

1. **Use Managed Passwords**: Set `manage_master_password = true` to use AWS Secrets Manager instead of hardcoding passwords
2. **Enable Password Rotation**: Set `manage_master_password_rotation = true` with appropriate rotation interval for production
3. **Enable Encryption**: Always set `encrypted = true` with customer-managed KMS keys (`kms_key_arn`)
4. **Use Enhanced VPC Routing**: Set `enhanced_vpc_routing = true` to route COPY/UNLOAD through VPC
5. **Disable Public Access**: Set `publicly_accessible = false` for production clusters
6. **Require SSL**: Set `require_ssl = true` in parameter group parameters
7. **Enable Activity Logging**: Set `enable_user_activity_logging = true` in parameter group for audit trails
8. **Use IAM Roles**: Attach IAM roles via `iam_role_arns` instead of using access keys for S3/Glue access
9. **Limit IAM Roles**: Associate only necessary roles (maximum 10 per cluster)

### High Availability and Backup

1. **Use Multi-AZ**: Enable `multi_az = true` for production clusters on supported node types
2. **Enable AZ Relocation**: Set `availability_zone_relocation_enabled = true` for RA3 clusters
3. **Configure Snapshot Retention**: Set `automated_snapshot_retention_period` to 7-35 days based on RPO
4. **Enable Final Snapshots**: Set `skip_final_snapshot = false` for production with `final_snapshot_identifier`
5. **Cross-Region Snapshots**: Configure `snapshot_copy` for disaster recovery in another region
6. **Test Restores**: Regularly test cluster restoration from snapshots

### Performance and Optimization

1. **Choose Appropriate Node Types**: Use RA3 for production (separate compute/storage), DC2 for performance
2. **Size Clusters Appropriately**: Start with 2+ nodes for production workloads
3. **Configure Concurrency Scaling**: Set `max_concurrency_scaling_clusters` parameter for variable loads
4. **Use Usage Limits**: Configure `usage_limits` to manage concurrency scaling and Spectrum costs
5. **Enable CloudWatch Logging**: Configure `logging` with appropriate `log_exports` for monitoring

### Cost Optimization

1. **Use Scheduled Actions**: Configure `scheduled_actions` for pause/resume during off-hours
2. **Implement Resize Schedules**: Use scheduled resize actions for predictable workload patterns
3. **Monitor Usage Limits**: Set `usage_limits` with `breach_action = "emit-metric"` for cost alerts
4. **Use RA3 for Flexibility**: RA3 nodes allow independent compute/storage scaling
5. **Review Reserved Instances**: Evaluate reserved instances for predictable 24/7 workloads

### Operational Excellence

1. **Use Infrastructure as Code**: Manage all resources through Terraform for consistency
2. **Tag Comprehensively**: Apply tags including Environment, CostCenter, Application, Owner
3. **Configure Maintenance Windows**: Set `preferred_maintenance_window` during low-traffic periods
4. **Enable CloudWatch Logging**: Configure log retention with `cloudwatch_log_group_retention_in_days`
5. **Monitor with Alarms**: Set up CloudWatch alarms for CPU, disk space, and connection metrics

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-redshift
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/redshift/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-redshift/tree/master/examples
- **AWS Redshift Documentation**: https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html
- **Redshift Best Practices**: https://docs.aws.amazon.com/redshift/latest/dg/best-practices.html
- **Redshift Security**: https://docs.aws.amazon.com/redshift/latest/mgmt/security.html
- **Redshift Pricing**: https://aws.amazon.com/redshift/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Use Secrets Manager**: Always set `manage_master_password = true` - never hardcode passwords
2. **Choose Right Node Type**: Use `ra3.xlplus` for production (flexible storage), `dc2.large` for dev/test
3. **Enable Encryption**: Set `encrypted = true` and provide `kms_key_arn` for production
4. **Configure Network**: Provide `vpc_id` and `subnet_ids`; use `security_group_ingress_rules` for access control
5. **Set `enhanced_vpc_routing = true`**: Required for security compliance in most organizations
6. **Set `publicly_accessible = false`**: Default for production environments
7. **Configure Backups**: Set `automated_snapshot_retention_period` (7+ days) and `skip_final_snapshot = false` for production
8. **Tag Resources**: Apply comprehensive tags including Environment, CostCenter, Application
9. **Use Scheduled Actions**: Configure pause/resume for non-24/7 workloads to reduce costs
10. **Attach IAM Roles**: Include `iam_role_arns` for S3/Glue access instead of credentials
11. **Enable Logging**: Set `logging` with `log_exports` for audit and compliance
12. **Parameter Group**: Customize `parameter_group_parameters` for SSL, logging, and concurrency settings
13. **RA3 Features**: Use `availability_zone_relocation_enabled` and `endpoint_access` only with RA3 node types
14. **Version Pinning**: Always specify `version = "~> 7.1"` in module source for stability
