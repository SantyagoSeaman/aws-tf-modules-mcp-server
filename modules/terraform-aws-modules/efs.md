# Terraform AWS EFS Module

## Module Information

- **Module Name**: `efs`
- **Source**: `terraform-aws-modules/efs/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-efs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/efs/aws/latest
- **Latest Version**: 1.8.0
- **Purpose**: Creates and manages AWS Elastic File System (EFS) resources with encryption, access points, mount targets, lifecycle policies, and cross-region replication
- **Service**: AWS EFS (Elastic File System)
- **Category**: Storage, File Storage, Network File System
- **Keywords**: efs, elastic-file-system, nfs, shared-storage, mount-targets, access-points, file-system-encryption, lifecycle-policy, infrequent-access, backup-policy, replication, multi-az, security-groups, container-storage, eks, kubernetes, persistent-volumes
- **Use For**: shared application storage, container persistent volumes, content management systems, web server content sharing, development environments, big data analytics, machine learning training data, media processing workflows, home directories, Kubernetes persistent storage

## Description

AWS Elastic File System (EFS) is a fully managed, elastic, scalable network file system that provides simple, scalable file storage for use with AWS Cloud services and on-premises resources. This Terraform module provides a comprehensive solution for creating and managing EFS file systems with security-first defaults: encryption enabled by default, secure transport enforcement, and automatic backup policy integration.

The module supports multiple performance modes (generalPurpose, maxIO) and throughput modes (bursting, elastic, provisioned) to meet different workload requirements. It enables fine-grained access control through EFS access points with POSIX user and group settings, allowing multiple applications to share a single file system with isolated views. The module handles mount target creation across multiple availability zones for high availability, automatically creates and manages security groups for NFS traffic, and supports cross-region replication for disaster recovery scenarios.

This module is essential for organizations running stateful applications, containerized workloads on ECS or EKS, or any scenario requiring shared file storage across multiple compute resources. With comprehensive tagging, monitoring integration, and policy-based access control, this module serves as the foundation for enterprise-grade shared file storage in AWS.

## Key Features

- **Encryption by Default**: File systems are encrypted at rest using AWS KMS (configurable with custom KMS keys)
- **Secure Transport Enforcement**: Requires `aws:SecureTransport` for all connections by default
- **Performance Modes**: Choose between General Purpose (low latency) or Max I/O (high throughput) - cannot be changed after creation
- **Throughput Modes**: Select Bursting (scales with size), Elastic (automatic scaling), or Provisioned (fixed throughput)
- **Multi-AZ Mount Targets**: Create mount targets in multiple availability zones via simple map configuration
- **One Zone Storage**: Deploy to single AZ for cost optimization by specifying `availability_zone_name`
- **Access Points**: Define application-specific entry points with POSIX user identity (uid, gid, secondary_gids) and root directory settings
- **Lifecycle Management**: Automatic transition to Infrequent Access (IA) and Archive storage classes
- **AWS Backup Integration**: Backup policy enabled by default with `enable_backup_policy = true`
- **Cross-Region Replication**: Built-in support for disaster recovery via `create_replication_configuration`
- **Automatic Security Group**: Creates and manages security group with NFS port 2049/TCP rules
- **IAM Policy Support**: Flexible policy attachment with statement merging capabilities
- **Comprehensive Tagging**: Apply tags to all resources for organization and cost allocation

## Main Use Cases

1. **Container Persistent Storage**: Provide persistent volumes for ECS and EKS containers requiring shared storage across pods
2. **Content Management Systems**: Store and share web content, media files, and documents across multiple web servers
3. **Development Environments**: Share source code, build artifacts, and development tools across development teams
4. **Big Data Analytics**: Store and process large datasets for Hadoop, Spark, and other analytics frameworks
5. **Machine Learning**: Store training datasets and model artifacts accessible by multiple training instances
6. **Media Processing**: Share video and image files for transcoding, rendering, and processing workflows
7. **Home Directories**: Provide network home directories for users across multiple Linux instances
8. **Kubernetes Persistent Volumes**: Serve as ReadWriteMany (RWX) storage class for Kubernetes workloads

## Input Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `name` | `string` | `""` | The name of the file system |
| `creation_token` | `string` | `null` | Unique identifier for idempotent creation |
| `encrypted` | `bool` | `true` | Enable encryption at rest |
| `kms_key_arn` | `string` | `null` | ARN of KMS key for encryption (requires encrypted=true) |
| `performance_mode` | `string` | `null` | `generalPurpose` or `maxIO` (permanent after creation) |
| `throughput_mode` | `string` | `null` | `bursting`, `elastic`, or `provisioned` |
| `provisioned_throughput_in_mibps` | `number` | `null` | Throughput in MiB/s for provisioned mode |
| `availability_zone_name` | `string` | `null` | AZ for One Zone storage; omit for regional/multi-AZ |
| `tags` | `map(string)` | `{}` | Tags to apply to all resources |

### Lifecycle Policy

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `lifecycle_policy` | `any` | `{}` | Lifecycle policy configuration object |

Lifecycle policy object supports:
- `transition_to_ia`: `AFTER_1_DAY`, `AFTER_7_DAYS`, `AFTER_14_DAYS`, `AFTER_30_DAYS`, `AFTER_60_DAYS`, `AFTER_90_DAYS`, `AFTER_180_DAYS`, `AFTER_270_DAYS`, `AFTER_365_DAYS`
- `transition_to_primary_storage_class`: `AFTER_1_ACCESS`
- `transition_to_archive`: Similar values as `transition_to_ia`

### Mount Targets

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `mount_targets` | `any` | `{}` | Map of mount target definitions |

Mount target object structure:
```hcl
mount_targets = {
  "az-key" = {
    subnet_id = "subnet-xxx"  # Required
  }
}
```

### Access Points

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `access_points` | `any` | `{}` | Map of access point definitions |

Access point object structure:
```hcl
access_points = {
  "app-name" = {
    name = "app-access-point"
    posix_user = {
      gid            = 1001
      uid            = 1001
      secondary_gids = [1002]
    }
    root_directory = {
      path = "/app"
      creation_info = {
        owner_gid   = 1001
        owner_uid   = 1001
        permissions = "755"
      }
    }
    tags = {}
  }
}
```

### Backup Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_backup_policy` | `bool` | `true` | Create backup policy resource |
| `enable_backup_policy` | `bool` | `true` | Enable automatic backups via AWS Backup |

### Replication Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_replication_configuration` | `bool` | `false` | Enable cross-region replication |
| `replication_configuration_destination` | `any` | `null` | Destination configuration for replication |

Replication destination object:
```hcl
replication_configuration_destination = {
  region         = "eu-west-2"           # Required if not specifying file_system_id
  file_system_id = null                  # Optional: replicate to existing EFS
  kms_key_id     = null                  # Optional: KMS key for destination
}
```

### Security Group Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_security_group` | `bool` | `true` | Create and manage security group |
| `security_group_name` | `string` | `null` | Name for the security group |
| `security_group_vpc_id` | `string` | `null` | VPC ID for security group |
| `security_group_ingress_rules` | `any` | `{}` | Ingress rules (defaults to NFS 2049/TCP) |
| `security_group_egress_rules` | `any` | `{}` | Egress rules (defaults to NFS 2049/TCP) |

### IAM Policy Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `attach_policy` | `bool` | `true` | Attach file system policy |
| `bypass_policy_lockout_safety_check` | `bool` | `false` | Bypass policy lockout safety check |
| `deny_nonsecure_transport` | `bool` | `true` | Deny connections without TLS |
| `policy_statements` | `any` | `null` | Custom IAM policy statements |

## Outputs

| Output | Description |
|--------|-------------|
| `id` | File system ID (e.g., fs-ccfc0d65) |
| `arn` | Amazon Resource Name of the file system |
| `dns_name` | DNS name for the file system |
| `size_in_bytes` | Latest known metered size of stored data |
| `access_points` | Map of access points and their attributes |
| `mount_targets` | Map of mount targets and their attributes |
| `security_group_id` | ID of the created security group |
| `security_group_arn` | ARN of the security group |
| `replication_configuration_destination_file_system_id` | Replica file system ID |

## Usage Examples

### Basic EFS File System

```hcl
module "efs" {
  source  = "terraform-aws-modules/efs/aws"
  version = "~> 1.8"

  name = "my-app-efs"

  tags = {
    Environment = "dev"
    Project     = "my-app"
  }
}
```

### EFS with Mount Targets and Access Points

```hcl
module "efs" {
  source  = "terraform-aws-modules/efs/aws"
  version = "~> 1.8"

  name           = "my-app-efs"
  encrypted      = true
  kms_key_arn    = aws_kms_key.efs.arn

  performance_mode = "generalPurpose"
  throughput_mode  = "elastic"

  lifecycle_policy = {
    transition_to_ia = "AFTER_30_DAYS"
  }

  # Mount targets in multiple AZs
  mount_targets = {
    "us-east-1a" = {
      subnet_id = module.vpc.private_subnets[0]
    }
    "us-east-1b" = {
      subnet_id = module.vpc.private_subnets[1]
    }
  }

  # Access point for application
  access_points = {
    app = {
      name = "app-data"
      posix_user = {
        gid = 1001
        uid = 1001
      }
      root_directory = {
        path = "/app"
        creation_info = {
          owner_gid   = 1001
          owner_uid   = 1001
          permissions = "755"
        }
      }
    }
  }

  # Security group configuration
  security_group_vpc_id = module.vpc.vpc_id
  security_group_ingress_rules = {
    vpc = {
      cidr_ipv4 = module.vpc.vpc_cidr_block
    }
  }

  tags = {
    Environment = "production"
    Project     = "my-app"
  }
}
```

### EFS with Cross-Region Replication

```hcl
module "efs" {
  source  = "terraform-aws-modules/efs/aws"
  version = "~> 1.8"

  name      = "replicated-efs"
  encrypted = true

  # Enable replication to another region
  create_replication_configuration = true
  replication_configuration_destination = {
    region = "us-west-2"
  }

  mount_targets = {
    "us-east-1a" = {
      subnet_id = module.vpc.private_subnets[0]
    }
  }

  security_group_vpc_id = module.vpc.vpc_id

  tags = {
    Environment = "production"
    DR          = "enabled"
  }
}
```

### One Zone EFS (Cost Optimized)

```hcl
module "efs" {
  source  = "terraform-aws-modules/efs/aws"
  version = "~> 1.8"

  name                   = "dev-efs"
  availability_zone_name = "us-east-1a"  # Creates One Zone storage class

  lifecycle_policy = {
    transition_to_ia = "AFTER_7_DAYS"
  }

  mount_targets = {
    "us-east-1a" = {
      subnet_id = module.vpc.private_subnets[0]
    }
  }

  security_group_vpc_id = module.vpc.vpc_id

  tags = {
    Environment = "dev"
  }
}
```

### EFS with Custom IAM Policy

```hcl
module "efs" {
  source  = "terraform-aws-modules/efs/aws"
  version = "~> 1.8"

  name = "restricted-efs"

  attach_policy = true
  policy_statements = [
    {
      sid     = "AllowSpecificRole"
      actions = ["elasticfilesystem:ClientMount", "elasticfilesystem:ClientWrite"]
      principals = [
        {
          type        = "AWS"
          identifiers = [aws_iam_role.app.arn]
        }
      ]
    }
  ]

  mount_targets = {
    "us-east-1a" = {
      subnet_id = module.vpc.private_subnets[0]
    }
  }

  security_group_vpc_id = module.vpc.vpc_id
}
```

## Best Practices

### Security

1. **Keep Encryption Enabled**: The module enables encryption by default; do not disable for production workloads
2. **Use Customer-Managed KMS Keys**: For compliance requirements, specify `kms_key_arn` with your own KMS key
3. **Keep Secure Transport Enabled**: The `deny_nonsecure_transport = true` default enforces TLS; do not disable
4. **Restrict Security Groups**: Limit NFS port (2049) access to only necessary CIDR blocks or security groups
5. **Use Access Points**: Create dedicated access points with non-root POSIX users for each application

### Performance

1. **Choose Performance Mode Carefully**: `performance_mode` cannot be changed after creation; use `generalPurpose` for most workloads, `maxIO` only for massively parallel applications
2. **Start with Elastic Throughput**: Use `throughput_mode = "elastic"` for unpredictable workloads
3. **Avoid Provisioned Unless Necessary**: Provisioned throughput at 256 MiB/s costs ~$1,500/month

### High Availability

1. **Deploy Multi-AZ for Production**: Create mount targets in at least two availability zones
2. **Use One Zone for Dev/Test**: Specify `availability_zone_name` for non-production to save up to 47%
3. **Enable Replication for DR**: Use `create_replication_configuration = true` for critical data

### Cost Optimization

1. **Enable Lifecycle Policies**: Set `transition_to_ia` to move infrequently accessed files to cheaper storage
2. **Monitor Storage Classes**: Track distribution across Standard, IA, and Archive tiers
3. **Right-size Throughput**: Review Elastic throughput billing or avoid over-provisioning

### Operations

1. **Enable Backups**: Keep default `enable_backup_policy = true` for automated backups
2. **Tag Resources**: Apply comprehensive tags for cost allocation and organization
3. **Use Infrastructure as Code**: Pin module version (e.g., `version = "~> 1.8"`) to prevent unexpected changes

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-efs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/efs/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-efs/tree/master/examples
- **AWS EFS Documentation**: https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html
- **EFS Performance**: https://docs.aws.amazon.com/efs/latest/ug/performance.html
- **EFS Storage Classes**: https://docs.aws.amazon.com/efs/latest/ug/storage-classes.html
- **EFS Access Points**: https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html
- **EFS Encryption**: https://docs.aws.amazon.com/efs/latest/ug/encryption.html
- **EFS Replication**: https://docs.aws.amazon.com/efs/latest/ug/efs-replication.html
- **EFS Best Practices**: https://docs.aws.amazon.com/efs/latest/ug/best-practices.html
- **EFS Pricing**: https://aws.amazon.com/efs/pricing/
- **EFS CSI Driver for Kubernetes**: https://docs.aws.amazon.com/eks/latest/userguide/efs-csi.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Encryption is On by Default**: No action needed; `encrypted = true` is the default
2. **Secure Transport is Enforced**: `deny_nonsecure_transport = true` is default; TLS required
3. **Backup is Enabled by Default**: `enable_backup_policy = true` provides automatic AWS Backup
4. **Performance Mode is Permanent**: Choose `generalPurpose` unless you need `maxIO`; cannot be changed later
5. **Multi-AZ vs One Zone**: Omit `availability_zone_name` for multi-AZ; specify it for One Zone (cost savings)
6. **Mount Targets Need VPC/Subnets**: VPC and subnets must exist before creating mount targets
7. **Security Group Auto-Created**: Set `security_group_vpc_id` to enable automatic security group creation
8. **Access Points for Isolation**: Use access points with POSIX users to isolate application access
9. **Cost Warning**: Provisioned throughput is expensive (~$1,500/month at 256 MiB/s); prefer elastic mode
10. **Pin Module Version**: Always specify version constraint to avoid breaking changes
