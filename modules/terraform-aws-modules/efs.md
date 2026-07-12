# Terraform AWS EFS Module

## Module Information

- **Module Name**: `efs`
- **Module ID**: `terraform-aws-modules/efs/aws`
- **Source**: `terraform-aws-modules/efs/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-efs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/efs/aws/latest
- **Latest Version**: 2.2.0
- **Purpose**: Creates and manages AWS Elastic File System (EFS) resources with encryption, access points, mount targets, lifecycle policies, backup policy, and cross-region replication
- **Service**: AWS EFS (Elastic File System)
- **Category**: Storage, File Storage, Network File System
- **Keywords**: efs, elastic-file-system, nfs, shared-storage, mount-targets, access-points, encryption-at-rest, lifecycle-policy, backup-policy, cross-region-replication, security-groups, container-storage, eks, kubernetes, persistent-volumes
- **Use For**: shared application storage, container persistent volumes, content management systems, web server content sharing, development environments, big data analytics, machine learning training data, media processing workflows, home directories, Kubernetes persistent storage

## Description

AWS Elastic File System (EFS) is a fully managed, elastic, scalable network file system (NFSv4) that provides shared file storage for use with AWS compute services (EC2, ECS, EKS, Lambda) and on-premises resources. This Terraform module provisions a single EFS file system end-to-end with security-first defaults: encryption at rest enabled by default, secure-transport (TLS) enforcement for both the API and mount-target data plane, and automatic AWS Backup policy integration.

The module supports both performance modes (`generalPurpose`, `maxIO`) and all three throughput modes (`bursting`, `elastic`, `provisioned`) to match different workload profiles. It manages mount targets across multiple availability zones — including IPv4, IPv6, and dual-stack addressing — for high-availability access, or a single AZ for cost-optimized "One Zone" storage. Fine-grained access control is provided through EFS access points with POSIX user/group identities and root-directory scoping, letting multiple applications share one file system with isolated views. The module also creates and manages a dedicated security group for NFS (port 2049) traffic, attaches a file system IAM resource policy built from statement objects or externally sourced policy documents, and can configure cross-region (or cross-AZ) replication with overwrite-protection controls for disaster recovery.

This module is the standard building block for stateful, shared-storage workloads in AWS: persistent volumes for ECS/EKS containers, home directories, CMS/media asset storage, and shared datasets for analytics or ML training. Comprehensive tagging, a per-resource `region` override for multi-region module calls, and typed input objects make it straightforward to compose into larger platform modules while keeping a strict, self-documenting variable contract.

## Key Features

- **Encryption by Default**: File systems are encrypted at rest via AWS KMS (`encrypted = true`); supports customer-managed KMS keys via `kms_key_arn`
- **Dual Secure-Transport Enforcement**: Denies non-TLS connections both at the file-system policy level (`deny_nonsecure_transport`) and specifically via mount targets (`deny_nonsecure_transport_via_mount_target`)
- **Performance Modes**: `generalPurpose` (default, low latency) or `maxIO` (higher aggregate throughput) — immutable after creation
- **Throughput Modes**: `bursting` (default, scales with size), `elastic` (automatic scaling), or `provisioned` (fixed MiB/s, billed regardless of usage)
- **Multi-AZ Mount Targets**: Create mount targets across AZs via a simple keyed map; supports IPv4, IPv6, and dual-stack (`ip_address_type`) addressing and per-target security group overrides
- **One Zone Storage**: Deploy to a single AZ (`availability_zone_name`) for lower-cost storage in non-critical environments
- **Access Points**: Application-scoped entry points with POSIX identity (`uid`, `gid`, `secondary_gids`) and `root_directory` path/permissions for multi-tenant isolation on one file system
- **Lifecycle Management**: Automatic transition to Infrequent Access and Archive storage classes, with optional transition back to Standard on access
- **AWS Backup Integration**: Backup policy created and enabled by default (`create_backup_policy` / `enable_backup_policy`)
- **Cross-Region/AZ Replication**: Built-in replica configuration (`create_replication_configuration`) with a `protection` block to control replication-overwrite behavior on the destination
- **Automatic Security Group**: Creates a security group with named ingress/egress rule maps, defaulting to NFS 2049/TCP
- **Flexible IAM Policy**: Build the file-system policy from `policy_statements` (a map of statement objects) and merge in `source_policy_documents` / `override_policy_documents`
- **Per-Resource Region Override**: `region` argument on the module and on individual `mount_targets` entries supports multi-region resource placement from a single provider configuration
- **Comprehensive Tagging**: Tags applied to the file system, mount targets, access points, security group, and replica

## Main Use Cases

1. **Container Persistent Storage**: Provide ReadWriteMany persistent volumes for ECS and EKS workloads
2. **Content Management Systems**: Store and share web content, media files, and documents across multiple web servers
3. **Development Environments**: Share source code, build artifacts, and tooling across development teams
4. **Big Data Analytics**: Store and process large datasets for Hadoop, Spark, and other analytics frameworks
5. **Machine Learning**: Store training datasets and model artifacts accessible by multiple training instances
6. **Media Processing**: Share video and image files for transcoding, rendering, and processing workflows
7. **Home Directories**: Provide network home directories for users across multiple Linux instances
8. **Disaster Recovery**: Replicate file systems cross-region/cross-AZ with overwrite protection for business continuity

## Main Input Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `name` | `string` | `""` | The name of the file system |
| `creation_token` | `string` | `null` | Unique idempotency token (max 64 chars); auto-generated by Terraform if omitted |
| `encrypted` | `bool` | `true` | Enable encryption at rest |
| `kms_key_arn` | `string` | `null` | ARN of KMS key for encryption (requires `encrypted = true`) |
| `performance_mode` | `string` | `null` (`generalPurpose`) | `generalPurpose` or `maxIO` — permanent after creation |
| `throughput_mode` | `string` | `null` (`bursting`) | `bursting`, `elastic`, or `provisioned` |
| `provisioned_throughput_in_mibps` | `number` | `null` | Throughput in MiB/s; only used with `throughput_mode = "provisioned"` |
| `availability_zone_name` | `string` | `null` | AZ for One Zone storage; omit for regional/multi-AZ |
| `region` | `string` | `null` | AWS region for the resources, if different from the provider region |
| `tags` | `map(string)` | `{}` | Tags to apply to all resources |

### Lifecycle Policy

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `lifecycle_policy` | `object` | `{}` | Lifecycle policy configuration object |

Supported keys: `transition_to_ia` (`AFTER_1_DAY` … `AFTER_365_DAYS`), `transition_to_archive` (same value set), `transition_to_primary_storage_class` (`AFTER_1_ACCESS`).

### Mount Targets

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `mount_targets` | `map(object)` | `{}` | Map of mount target definitions, one per AZ/subnet |

```hcl
mount_targets = {
  "az-key" = {
    subnet_id       = "subnet-xxx"  # Required
    ip_address      = null          # Optional: static IPv4 address
    ip_address_type = null          # Optional: IPV4, IPV6, or DUAL_STACK
    ipv6_address    = null          # Optional: static IPv6 address
    security_groups = []            # Optional: override the module-created security group
    region           = null         # Optional: per-target region override
  }
}
```

### Access Points

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `access_points` | `map(object)` | `{}` | Map of access point definitions |

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
| `create_backup_policy` | `bool` | `true` | Create a backup policy resource |
| `enable_backup_policy` | `bool` | `true` | Set the backup policy to `ENABLED` (vs `DISABLED`) |

### Replication & Protection

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_replication_configuration` | `bool` | `false` | Enable cross-region/cross-AZ replication |
| `replication_configuration_destination` | `object` | `null` | Destination configuration for replication |
| `protection` | `object({ replication_overwrite = optional(string) })` | `null` | Set `replication_overwrite = "ENABLED"`/`"DISABLED"` to control overwrite protection |

```hcl
replication_configuration_destination = {
  region                  = "eu-west-2"  # Required if not targeting an existing file_system_id
  availability_zone_name  = null         # Optional: create a One Zone replica
  file_system_id          = null         # Optional: replicate into an existing EFS file system
  kms_key_id              = null         # Optional: KMS key for the destination
}
```

### Security Group Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_security_group` | `bool` | `true` | Create and manage a security group |
| `security_group_name` | `string` | `null` | Name for the security group |
| `security_group_use_name_prefix` | `bool` | `false` | Treat `security_group_name` as a name prefix |
| `security_group_description` | `string` | `null` (`Managed by Terraform`) | Security group description |
| `security_group_vpc_id` | `string` | `null` | VPC ID for the security group |
| `security_group_ingress_rules` | `map(object)` | `{}` | Named ingress rules; `from_port`/`to_port`/`ip_protocol` default to `2049`/`2049`/`tcp` |
| `security_group_egress_rules` | `map(object)` | `{}` | Named egress rules; same NFS defaults as ingress |

### IAM Policy Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `attach_policy` | `bool` | `true` | Attach a file system resource policy |
| `bypass_policy_lockout_safety_check` | `bool` | `null` (`false`) | Bypass the policy lockout safety check |
| `deny_nonsecure_transport` | `bool` | `true` | Require `aws:SecureTransport` for API/data-plane access |
| `deny_nonsecure_transport_via_mount_target` | `bool` | `true` | Require `aws:SecureTransport` specifically for mount-target access |
| `policy_statements` | `map(object)` | `null` | Custom IAM policy statements, keyed by an arbitrary map key (each with `sid`, `actions`, `resources`, `principals`, `conditions`, etc.) |
| `source_policy_documents` | `list(string)` | `[]` | JSON policy documents merged in as the base document (statements must have unique `sid`s) |
| `override_policy_documents` | `list(string)` | `[]` | JSON policy documents merged last; statements with matching `sid`s override earlier ones |

## Main Outputs

| Output | Description |
|--------|-------------|
| `id` | File system ID (e.g., `fs-ccfc0d65`) |
| `arn` | Amazon Resource Name of the file system |
| `dns_name` | DNS name for the file system |
| `size_in_bytes` | Latest known metered size of stored data |
| `access_points` | Map of access points and their attributes |
| `mount_targets` | Map of mount targets and their attributes |
| `security_group_id` | ID of the created security group |
| `security_group_arn` | ARN of the security group |
| `replication_configuration_destination_file_system_id` | File system ID of the replica |

## Usage Examples

### Basic EFS File System

```hcl
module "efs" {
  source  = "terraform-aws-modules/efs/aws"
  version = "~> 2.2"

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
  version = "~> 2.2"

  name        = "my-app-efs"
  encrypted   = true
  kms_key_arn = aws_kms_key.efs.arn

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
      # relies on the default NFS 2049/TCP ingress
      description = "NFS ingress from VPC private subnets"
      cidr_ipv4   = module.vpc.vpc_cidr_block
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
  version = "~> 2.2"

  name      = "replicated-efs"
  encrypted = true

  # Enable replication to another region, protected from destination overwrite
  create_replication_configuration = true
  replication_configuration_destination = {
    region = "us-west-2"
  }
  protection = {
    replication_overwrite = "DISABLED"
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
  version = "~> 2.2"

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
  version = "~> 2.2"

  name = "restricted-efs"

  attach_policy = true
  # NOTE: policy_statements is a map (keyed by an arbitrary name), not a list
  policy_statements = {
    allow_app_role = {
      sid     = "AllowSpecificRole"
      actions = ["elasticfilesystem:ClientMount", "elasticfilesystem:ClientWrite"]
      principals = [
        {
          type        = "AWS"
          identifiers = [aws_iam_role.app.arn]
        }
      ]
    }
  }

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
3. **Keep Secure Transport Enabled**: `deny_nonsecure_transport` and `deny_nonsecure_transport_via_mount_target` both default to `true`; do not disable either
4. **Restrict Security Groups**: Limit NFS port (2049) access to only necessary CIDR blocks or referenced security groups
5. **Use Access Points**: Create dedicated access points with non-root POSIX users for each application instead of mounting the root of the file system

### Performance

1. **Choose Performance Mode Carefully**: `performance_mode` cannot be changed after creation; use `generalPurpose` for most workloads, `maxIO` only for massively parallel applications
2. **Start with Elastic Throughput**: Use `throughput_mode = "elastic"` for unpredictable workloads
3. **Avoid Provisioned Unless Necessary**: Provisioned throughput at 256 MiB/s costs roughly $1,500/month regardless of usage

### High Availability & Disaster Recovery

1. **Deploy Multi-AZ for Production**: Create mount targets in at least two availability zones
2. **Use One Zone for Dev/Test**: Specify `availability_zone_name` for non-production to reduce storage cost
3. **Enable Replication for DR**: Use `create_replication_configuration = true` for critical data, and set `protection.replication_overwrite = "DISABLED"` to prevent accidental replica overwrite
4. **Consider Dual-Stack Mount Targets**: Use `ip_address_type = "DUAL_STACK"` on `mount_targets` entries when clients need IPv6 connectivity

### Cost Optimization

1. **Enable Lifecycle Policies**: Set `transition_to_ia` (and optionally `transition_to_archive`) to move infrequently accessed files to cheaper storage classes
2. **Monitor Storage Classes**: Track distribution across Standard, IA, and Archive tiers
3. **Right-size Throughput**: Prefer elastic throughput over over-provisioned fixed throughput

### Operations

1. **Enable Backups**: Keep the default `enable_backup_policy = true` for automated AWS Backup coverage
2. **Tag Resources**: Apply comprehensive tags for cost allocation and organization
3. **Pin the Module Version**: Use `version = "~> 2.2"`; the module requires Terraform >= 1.5.7 and AWS provider >= 6.28

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-efs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/efs/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-efs/tree/master/examples
- **v1.x to v2.x Upgrade Guide**: https://github.com/terraform-aws-modules/terraform-aws-efs/blob/master/docs/UPGRADE-2.0.md
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
2. **Secure Transport is Enforced Twice**: `deny_nonsecure_transport` (API/policy) and `deny_nonsecure_transport_via_mount_target` (mount-target data plane) both default to `true`
3. **Backup is Enabled by Default**: `enable_backup_policy = true` provides automatic AWS Backup coverage
4. **Performance Mode is Permanent**: Choose `generalPurpose` unless you need `maxIO`; it cannot be changed later
5. **Multi-AZ vs One Zone**: Omit `availability_zone_name` for multi-AZ; specify it for One Zone (cost savings, single-AZ availability)
6. **Mount Targets Need VPC/Subnets**: VPC and subnets must exist before creating mount targets
7. **Security Group Auto-Created**: Set `security_group_vpc_id` to enable automatic security group creation; supply `security_group_ingress_rules`/`security_group_egress_rules` as named maps (defaults already target NFS 2049/TCP)
8. **Access Points for Isolation**: Use access points with non-root POSIX users to isolate application access on a shared file system
9. **Cost Warning**: Provisioned throughput is expensive (~$1,500/month at 256 MiB/s); prefer `elastic` mode unless a fixed floor is required
10. **`policy_statements` is a Map, Not a List (Breaking Change in v2.0)**: Each statement must be keyed, e.g. `policy_statements = { my_stmt = { sid = "...", actions = [...] } }` — passing a list will fail on module versions >= 2.0
11. **`security_group_rules` was Removed in v2.0**: Use the separate `security_group_ingress_rules` and `security_group_egress_rules` maps instead
12. **Version/Provider Floor**: Module versions >= 2.0 require Terraform >= 1.5.7 and AWS provider >= 6.12 (>= 6.28 as of v2.2); pin with `version = "~> 2.2"`
13. **IPv6/Dual-Stack Mount Targets**: Set `ip_address_type = "DUAL_STACK"` (or `"IPV6"`) on a `mount_targets` entry for IPv6 client access
14. **Replica Overwrite Protection**: Use `protection = { replication_overwrite = "DISABLED" }` alongside `create_replication_configuration` to prevent the replica from being overwritten by a future full restore
