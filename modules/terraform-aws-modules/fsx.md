# Terraform AWS FSx Module

## Module Information

- **Module Name**: `fsx`
- **Source**: `terraform-aws-modules/fsx/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-fsx
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest
- **Latest Version**: 1.3.1
- **Compatibility**: Terraform >= 1.3, AWS provider >= 5.100 (all four submodules)
- **Purpose**: Terraform module that creates AWS FSx file systems — Lustre, NetApp ONTAP, OpenZFS, and Windows File Server — each via its own independent submodule
- **Service**: AWS FSx (Fully Managed File Storage)
- **Category**: Storage, File Systems, High-Performance Computing
- **Keywords**: fsx, lustre, ontap, openzfs, windows-file-server, nfs, smb, iscsi, file-cache, active-directory, multi-az, hpc, s3-data-repository, snaplock, storage-virtual-machine, kms-encryption
- **Use For**: HPC/ML training data storage backed by S3 via Lustre, on-premises HPC cache acceleration with Amazon File Cache, NetApp ONTAP lift-and-shift with SnapMirror/SnapLock compliance retention, Linux NFS file server migration to OpenZFS, Windows SMB file shares with Active Directory, EKS/ECS persistent shared storage, multi-protocol enterprise NAS (NFS/SMB/iSCSI) via ONTAP SVMs, video rendering and genomics pipelines, VMware Cloud on AWS datastores via ONTAP iSCSI

## Description

The AWS FSx Terraform module is a **submodule-only** module — the root module has no resources of its own. It provides four independent, purpose-built submodules (`lustre`, `ontap`, `openzfs`, `windows`) for deploying AWS FSx fully managed file storage, each targeting a different protocol and workload profile. Consumers must always source a specific submodule (e.g. `terraform-aws-modules/fsx/aws//modules/lustre`); there is no top-level `fsx` resource to instantiate.

FSx for Lustre provides a high-performance parallel file system (sub-millisecond latencies, throughput up to terabytes per second) with native S3 data repository association for data-lake and analytics workflows, and can additionally provision Amazon File Cache — a high-speed, Lustre-based cache in front of on-premises NFS or S3 data. FSx for NetApp ONTAP brings enterprise NetApp capabilities to AWS: multi-protocol access (NFS, SMB, iSCSI), Storage Virtual Machines (SVMs) with per-SVM Active Directory joins, scale-out deployments via multiple HA pairs, snapshots, cloning, tiering, and SnapLock WORM compliance volumes. FSx for OpenZFS is a managed OpenZFS implementation for Linux workloads, delivering over 1 million IOPS at sub-millisecond-to-few-hundred-microsecond latencies, with instant cloning/snapshots and hierarchical child volumes. FSx for Windows File Server delivers a native Windows file system over SMB with AWS Managed or self-managed Active Directory integration, DNS aliases, and file/share access audit logging to CloudWatch.

Each submodule independently manages its FSx file system (and related child resources such as ONTAP SVMs/volumes, OpenZFS volumes/snapshots, and Lustre data repository associations/file caches), an optional dedicated security group with custom ingress/egress rules, KMS encryption, automatic backups, and optional CloudWatch logging (Lustre and Windows). All resource creation is conditional via a `create` flag, and every resource accepts a `tags` map for cost allocation and governance.

## Key Features

- **4 Independent Submodules**: `lustre`, `ontap`, `openzfs`, `windows` — no shared root module, no cross-submodule resources
- **FSx for Lustre**: SCRATCH_1/2 and PERSISTENT_1/2 deployment types, S3 data repository associations with auto-import/export policies, Intelligent-Tiering storage (with `data_read_cache_configuration` SSD read cache and `metadata_configuration`), EFA + NVIDIA GPUDirect Storage support (`efa_enabled`, PERSISTENT_2 only), root squash configuration, and optional Amazon File Cache creation (`create_file_cache`)
- **FSx for NetApp ONTAP**: SINGLE_AZ_1/MULTI_AZ_1 deployment, scale-out via `ha_pairs` (1–6) with per-HA-pair throughput, Storage Virtual Machines with independent (self-managed) Active Directory joins, volume tiering policies, and SnapLock (Enterprise/Compliance) WORM retention volumes
- **FSx for OpenZFS**: SINGLE_AZ_1/2 and MULTI_AZ_1 deployment, over 1M IOPS at sub-ms/low-µs latencies, hierarchical root + child volumes with NFS exports, user/group quotas and reservations, data compression, and root/child volume snapshots
- **FSx for Windows File Server**: SMB protocol, AWS Managed Microsoft AD or self-managed AD join (mutually exclusive), DNS aliases, file/file-share access audit logging to CloudWatch, and restore-from-backup (`backup_id`)
- **Storage Classes & Throughput**: SSD/HDD/Intelligent-Tiering storage classes and user-provisioned or fixed throughput/IOPS depending on file system type
- **Automated Security Groups**: Each submodule can create a dedicated security group (`create_security_group`) with fully customizable `security_group_ingress_rules`/`security_group_egress_rules` maps — **ingress is empty by default**, so clients cannot reach the file system until rules are added
- **Encryption at Rest**: KMS encryption on every file system type, using an AWS-managed key unless `kms_key_id` is supplied
- **Automated Backups**: Configurable daily automatic backups (0–90 day retention) plus on-demand backup/restore for Lustre and Windows
- **CloudWatch Integration**: Optional CloudWatch log group creation for Lustre (data repository/file system events) and Windows (audit logs)
- **Conditional Creation**: `create = false` skips all resources in a submodule while keeping the module composable in larger configurations

## Main Use Cases

1. **High-Performance Computing**: Parallel Lustre storage for scientific simulations and computational workloads
2. **Machine Learning Training**: Fast, S3-backed data access for training large-scale ML models
3. **Hybrid HPC Caching**: Accelerate on-premises NFS or S3 data access for burst compute via Amazon File Cache (Lustre submodule)
4. **NetApp Migration**: Lift-and-shift on-premises NetApp ONTAP storage, including SnapMirror replication and SnapLock retention
5. **Regulated Data Retention**: WORM/immutable storage for compliance workloads using ONTAP SnapLock volumes
6. **Linux File Server Migration**: Move ZFS-based Linux file servers to a managed, high-IOPS AWS service
7. **Windows Enterprise File Shares**: Home directories, departmental shares, and SQL Server storage over SMB with AD authentication
8. **Container Persistent Storage**: Shared, POSIX-compliant volumes for Kubernetes (EKS) and Docker (ECS) workloads
9. **Multi-Protocol Enterprise NAS**: Serve NFS, SMB, and iSCSI simultaneously from ONTAP Storage Virtual Machines
10. **Video Rendering and Genomics**: High-throughput shared storage for media post-production and life-sciences pipelines

## Submodules

### 1. lustre

- **Purpose**: Create FSx for Lustre file systems (and optionally Amazon File Cache) for compute-intensive workloads with S3 integration
- **Source**: `terraform-aws-modules/fsx/aws//modules/lustre`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/lustre
- **Key Features**: Scratch/Persistent 1/2 deployment types, SSD/HDD/Intelligent-Tiering storage, S3 data repository associations, EFA/GPUDirect Storage, Amazon File Cache creation
- **Use Cases**: HPC clusters, ML training, video processing, financial simulations, on-premises cache acceleration

### 2. ontap

- **Purpose**: Create FSx for NetApp ONTAP file systems with multi-protocol support and enterprise data management
- **Source**: `terraform-aws-modules/fsx/aws//modules/ontap`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/ontap
- **Key Features**: Multi-protocol access (NFS/SMB/iSCSI), scale-out HA pairs, Storage Virtual Machines, SnapLock compliance, tiering
- **Use Cases**: Enterprise file shares, database storage, VMware Cloud on AWS, multi-tenant storage, NetApp migrations

### 3. openzfs

- **Purpose**: Create FSx for OpenZFS file systems for Linux-based workloads requiring high IOPS and low latency
- **Source**: `terraform-aws-modules/fsx/aws//modules/openzfs`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/openzfs
- **Key Features**: Single/Multi-AZ deployment, over 1M IOPS, instant snapshots, hierarchical volumes, user/group quotas
- **Use Cases**: Linux file server migrations, database storage, container persistent volumes, analytics workloads

### 4. windows

- **Purpose**: Create FSx for Windows File Server file systems with SMB protocol and Active Directory integration
- **Source**: `terraform-aws-modules/fsx/aws//modules/windows`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/windows
- **Key Features**: Native Windows file system, SMB, AWS Managed or self-managed AD, DNS aliases, audit logging, restore from backup
- **Use Cases**: Windows applications, home directories, SQL Server storage, WorkSpaces storage, content management

## Submodule 1: lustre

### Description

Creates an `aws_fsx_lustre_file_system` (and, optionally, an `aws_fsx_file_cache`), along with S3 `aws_fsx_data_repository_association` resources, a dedicated security group, and an optional CloudWatch log group. Designed for parallel, high-throughput, low-latency compute workloads with tight S3 integration.

### Key Features

- Scratch (SCRATCH_1/2, no replication) and Persistent (PERSISTENT_1/2, replicated) deployment types
- SSD, HDD (PERSISTENT_1 only), and Intelligent-Tiering (PERSISTENT_2 only, requires `data_read_cache_configuration` + `metadata_configuration`) storage
- S3 data repository associations with configurable auto-import/auto-export event policies
- EFA + NVIDIA GPUDirect Storage support via `efa_enabled` (PERSISTENT_2 only, immutable at creation)
- Root squash configuration to restrict root-level client access
- Optional Amazon File Cache creation (`create_file_cache`) as a caching layer in front of on-premises NFS or S3

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name for the file system |
| `deployment_type` | `string` | `null` | `SCRATCH_1`, `SCRATCH_2`, `PERSISTENT_1`, or `PERSISTENT_2` |
| `storage_capacity` | `number` | `null` | Storage capacity in GiB |
| `storage_type` | `string` | `null` | `SSD`, `HDD` (PERSISTENT_1 only), or `INTELLIGENT_TIERING` (PERSISTENT_2 only) |
| `subnet_ids` | `list(string)` | `[]` | Subnet IDs for file system deployment |
| `per_unit_storage_throughput` | `number` | `null` | Throughput per TiB for PERSISTENT_1/2 (MB/s/TiB) |
| `data_compression_type` | `string` | `null` | `LZ4` or `NONE` |
| `efa_enabled` | `bool` | `null` | Enable EFA/GPUDirect Storage (PERSISTENT_2 only) |
| `automatic_backup_retention_days` | `number` | `null` | Backup retention 0–90 days (PERSISTENT only) |
| `data_repository_associations` | `any` | `{}` | Map of S3 data repository association configurations |
| `root_squash_configuration` | `any` | `{}` | Root squash settings to restrict client root access |
| `create_file_cache` | `bool` | `false` | Whether to create an Amazon File Cache instead of/alongside a file system |
| `log_configuration` | `map(string)` | `{level = "WARN_ERROR"}` | CloudWatch log level configuration |
| `security_group_ingress_rules` | `any` | `{}` | Ingress rules for the created security group (empty by default — clients cannot connect until set) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `file_system_id` | FSx file system ID |
| `file_system_arn` | File system ARN |
| `file_system_dns_name` | DNS name for mounting, e.g. `fs-12345678.fsx.us-west-2.amazonaws.com` |
| `file_system_mount_name` | Lustre mount name |
| `file_system_network_interface_ids` | ENI IDs the file system is accessible from |
| `data_repository_associations` | Map of created data repository associations and attributes |
| `file_cache_id` / `file_cache_dns_name` | Identifier/DNS name of the Amazon File Cache (if created) |
| `security_group_id` | Security group ID |

### Usage Example

```hcl
module "fsx_lustre" {
  source = "terraform-aws-modules/fsx/aws//modules/lustre"

  name = "ml-training-lustre"

  deployment_type              = "PERSISTENT_2"
  storage_capacity             = 1200
  storage_type                 = "SSD"
  subnet_ids                   = [module.vpc.private_subnets[0]]
  per_unit_storage_throughput  = 125
  data_compression_type        = "LZ4"

  root_squash_configuration = {
    root_squash = "365534:65534"
  }

  log_configuration = {
    level = "ERROR_ONLY"
  }

  # S3 data repository integration
  data_repository_associations = {
    training_data = {
      data_repository_path = "s3://my-ml-datasets/training/"
      file_system_path     = "/data"

      s3 = {
        auto_import_policy = { events = ["NEW", "CHANGED", "DELETED"] }
        auto_export_policy = { events = ["NEW", "CHANGED", "DELETED"] }
      }
    }
  }

  security_group_ingress_rules = {
    vpc = {
      cidr_ipv4   = module.vpc.vpc_cidr_block
      description = "Allow Lustre traffic from the VPC"
      from_port   = 988
      to_port     = 988
      ip_protocol = "tcp"
    }
  }

  tags = { Environment = "production" }
}
```

## Submodule 2: ontap

### Description

Creates an `aws_fsx_ontap_file_system` along with one or more `aws_fsx_ontap_storage_virtual_machine` (SVM) resources and their `aws_fsx_ontap_volume` resources, a dedicated security group, and route table associations for Multi-AZ endpoint routing.

### Key Features

- `SINGLE_AZ_1` and `MULTI_AZ_1` deployment types
- Scale-out via `ha_pairs` (1–6 HA pairs) with `throughput_capacity_per_ha_pair`, or single-pair `throughput_capacity`
- Storage Virtual Machines with optional independent (self-managed) Active Directory joins per SVM
- Volume-level tiering policies (auto-tier cold data to lower-cost capacity pool storage)
- SnapLock (`COMPLIANCE`/`ENTERPRISE`) WORM retention volumes with configurable autocommit/retention periods
- Multi-protocol access: NFS, SMB, iSCSI, and NVMe

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name for the file system |
| `deployment_type` | `string` | `"MULTI_AZ_1"` | `SINGLE_AZ_1` or `MULTI_AZ_1` |
| `storage_capacity` | `number` | `null` | Storage capacity in GiB |
| `throughput_capacity` | `number` | `null` | Throughput in MBps (128/256/512/1024/2048/4096); mutually exclusive with `throughput_capacity_per_ha_pair` |
| `ha_pairs` | `number` | `null` | Number of HA pairs to deploy (1–6, use for scale-out) |
| `subnet_ids` | `list(string)` | `[]` | Subnet IDs for deployment |
| `preferred_subnet_id` | `string` | `""` | Primary subnet (required for `MULTI_AZ_1`) |
| `route_table_ids` | `list(string)` | `[]` | Route tables for Multi-AZ endpoint routing |
| `fsx_admin_password` | `string` | `null` | ONTAP `fsxadmin` password (sensitive) |
| `automatic_backup_retention_days` | `number` | `null` | Backup retention (0–90 days) |
| `storage_virtual_machines` | `any` | `{}` | Map of SVM definitions, each with nested `volumes` |
| `security_group_ingress_rules` | `any` | `{}` | Ingress rules for the created security group (empty by default) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `file_system_id` | FSx file system ID |
| `file_system_arn` | File system ARN |
| `file_system_dns_name` | Management DNS endpoint |
| `file_system_endpoints` | ONTAP CLI, REST API, and iSCSI endpoints |
| `storage_virtual_machines` | Map of created SVMs and their attributes |
| `volumes` | Map of created volumes and their attributes |
| `security_group_id` | Security group ID |

### Usage Example

```hcl
module "fsx_ontap" {
  source = "terraform-aws-modules/fsx/aws//modules/ontap"

  name                = "enterprise-ontap"
  deployment_type     = "MULTI_AZ_1"
  storage_capacity    = 1024
  throughput_capacity = 256
  subnet_ids          = module.vpc.private_subnets
  preferred_subnet_id = module.vpc.private_subnets[0]
  route_table_ids     = module.vpc.private_route_table_ids

  fsx_admin_password                = var.ontap_admin_password
  automatic_backup_retention_days   = 7
  daily_automatic_backup_start_time = "05:00"

  storage_virtual_machines = {
    production = {
      name = "production-svm"

      volumes = {
        data = {
          name                       = "data-vol"
          junction_path              = "/data"
          size_in_megabytes          = 102400
          storage_efficiency_enabled = true

          tiering_policy = {
            name           = "AUTO"
            cooling_period = 31
          }
        }
      }
    }
  }

  security_group_ingress_rules = {
    vpc = {
      cidr_ipv4   = module.vpc.vpc_cidr_block
      description = "Allow NFS/SMB/iSCSI traffic from the VPC"
      from_port   = 0
      to_port     = 0
      ip_protocol = "tcp"
    }
  }

  tags = { Environment = "production" }
}
```

## Submodule 3: openzfs

### Description

Creates an `aws_fsx_openzfs_file_system`, its root volume configuration, optional `aws_fsx_openzfs_volume` child volumes, and optional root/child `aws_fsx_openzfs_snapshot` resources, plus a dedicated security group.

### Key Features

- `SINGLE_AZ_1`, `SINGLE_AZ_2`, and `MULTI_AZ_1` deployment types
- Over 1 million IOPS at sub-millisecond-to-few-hundred-microsecond latencies (user-provisioned IOPS via `disk_iops_configuration`)
- Hierarchical volumes: one root volume plus any number of child `volumes`, each with independent compression, quotas, and NFS exports
- Per-user/per-group storage quotas and capacity reservations
- Root and child volume snapshots (`create_snapshot`) with configurable `delete_volume_options`

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name for the file system |
| `deployment_type` | `string` | `null` | `SINGLE_AZ_1`, `SINGLE_AZ_2`, or `MULTI_AZ_1` |
| `storage_capacity` | `number` | `null` | Storage capacity in GiB |
| `storage_type` | `string` | `null` | `SSD` or `HDD` |
| `throughput_capacity` | `number` | `null` | Throughput in MBps (128/256/512/1024/2048) |
| `subnet_ids` | `list(string)` | `[]` | Subnet IDs for deployment |
| `preferred_subnet_id` | `string` | `null` | Primary subnet (required for `MULTI_AZ_1`) |
| `route_table_ids` | `list(string)` | `[]` | Route tables for Multi-AZ endpoint routing |
| `disk_iops_configuration` | `map(string)` | `{}` | IOPS `mode` (`AUTOMATIC`/`USER_PROVISIONED`) and `iops` value |
| `root_volume_configuration` | `any` | `{}` | Root volume settings: compression, quotas, NFS exports, record size |
| `volumes` | `any` | `{}` | Map of child volume configurations |
| `automatic_backup_retention_days` | `number` | `null` | Backup retention (0–90 days) |
| `security_group_ingress_rules` | `any` | `{}` | Ingress rules for the created security group (empty by default) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `file_system_id` | FSx file system ID |
| `file_system_arn` | File system ARN |
| `file_system_dns_name` | NFS mount endpoint |
| `file_system_root_volume_id` | Root volume ID (`fsvol-...`) |
| `volumes` | Map of created child volumes and attributes |
| `child_volumes_snapshots` | Map of child volume snapshots (if created) |
| `security_group_id` | Security group ID |

### Usage Example

```hcl
module "fsx_openzfs" {
  source = "terraform-aws-modules/fsx/aws//modules/openzfs"

  name                = "linux-zfs"
  deployment_type     = "SINGLE_AZ_2"
  storage_capacity    = 1024
  storage_type        = "SSD"
  throughput_capacity = 160
  subnet_ids          = [module.vpc.private_subnets[0]]

  automatic_backup_retention_days = 7

  disk_iops_configuration = {
    mode = "USER_PROVISIONED"
    iops = 3072
  }

  root_volume_configuration = {
    data_compression_type = "LZ4"
    record_size_kib       = 128

    nfs_exports = {
      client_configurations = [
        {
          clients = "10.0.0.0/16"
          options = ["async", "rw", "no_root_squash"]
        }
      ]
    }
  }

  volumes = {
    data = {
      name = "data"

      user_and_group_quotas = [
        {
          type                       = "USER"
          id                         = 1001
          storage_capacity_quota_gib = 128
        }
      ]
    }
  }

  security_group_ingress_rules = {
    vpc = {
      cidr_ipv4   = module.vpc.vpc_cidr_block
      description = "Allow NFS traffic from the VPC"
      from_port   = 2049
      to_port     = 2049
      ip_protocol = "tcp"
    }
  }

  tags = { Environment = "production" }
}
```

## Submodule 4: windows

### Description

Creates an `aws_fsx_windows_file_system`, a dedicated security group, and an optional CloudWatch log group for file/file-share access audit logging.

### Key Features

- Native Windows file system over SMB (2.0–3.1.1)
- AWS Managed Microsoft AD (`active_directory_id`) or self-managed Active Directory (`self_managed_active_directory`) — mutually exclusive, one is always required
- DNS `aliases` for friendlier file system access names
- File and file-share access audit logging to CloudWatch (`audit_log_configuration`)
- User-provisioned IOPS via `disk_iops_configuration`
- Restore a new file system from an existing backup via `backup_id`

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name for the file system |
| `storage_capacity` | `number` | `null` | Storage in GiB (32–65,536; minimum 2,000 for HDD) |
| `storage_type` | `string` | `null` | `SSD` or `HDD` (`HDD` supported on `SINGLE_AZ_2`/`MULTI_AZ_1` only) |
| `throughput_capacity` | `number` | `null` | MBps (8–2,048, power-of-2 increments) |
| `deployment_type` | `string` | `null` | `SINGLE_AZ_1`, `SINGLE_AZ_2`, or `MULTI_AZ_1` |
| `subnet_ids` | `list(string)` | `[]` | Subnet IDs for deployment |
| `preferred_subnet_id` | `string` | `null` | Primary subnet (required for `MULTI_AZ_1`) |
| `active_directory_id` | `string` | `null` | AWS Managed Microsoft AD directory ID |
| `self_managed_active_directory` | `any` | `{}` | On-premises/self-managed AD join configuration |
| `automatic_backup_retention_days` | `number` | `null` | Backup retention 0–90 days (AWS default 7 if unset) |
| `audit_log_configuration` | `any` | `{file_access_audit_log_level = "FAILURE_ONLY", file_share_access_audit_log_level = "FAILURE_ONLY"}` | Audit logging levels |
| `aliases` | `list(string)` | `[]` | DNS aliases for file system access |
| `security_group_ingress_rules` | `any` | `{}` | Ingress rules for the created security group (empty by default) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `file_system_id` | FSx file system ID |
| `file_system_arn` | File system ARN |
| `file_system_dns_name` | Primary DNS endpoint for SMB access |
| `file_system_preferred_file_server_ip` | IP of the preferred/primary file server |
| `file_system_remote_administration_endpoint` | PowerShell remote administration endpoint |
| `cloudwatch_log_group_arn` | Audit log group ARN (if created) |
| `security_group_id` | Security group ID |

### Usage Example

```hcl
module "fsx_windows" {
  source = "terraform-aws-modules/fsx/aws//modules/windows"

  name                = "windows-file-server"
  storage_capacity    = 1024
  storage_type        = "SSD"
  throughput_capacity = 512
  deployment_type     = "MULTI_AZ_1"
  subnet_ids          = module.vpc.private_subnets
  preferred_subnet_id = module.vpc.private_subnets[0]

  # AWS Managed Microsoft AD
  active_directory_id = aws_directory_service_directory.this.id

  audit_log_configuration = {
    file_access_audit_log_level       = "SUCCESS_AND_FAILURE"
    file_share_access_audit_log_level = "SUCCESS_AND_FAILURE"
  }

  automatic_backup_retention_days   = 7
  daily_automatic_backup_start_time = "05:00"
  copy_tags_to_backups              = true

  security_group_ingress_rules = {
    vpc = {
      cidr_ipv4   = module.vpc.vpc_cidr_block
      description = "Allow SMB traffic from the VPC"
      from_port   = 445
      to_port     = 445
      ip_protocol = "tcp"
    }
  }

  tags = { Environment = "production" }
}
```

## Best Practices

### File System Selection and Design

1. **Choose the right file system type**: Lustre for HPC/ML and S3-integrated analytics, ONTAP for multi-protocol enterprise storage/NetApp migrations, OpenZFS for Linux NFS workloads needing very high IOPS, Windows for SMB/Active Directory workloads.
2. **Deployment type selection**: Use Scratch Lustre for temporary/cost-sensitive compute jobs; use Persistent Lustre, and Multi-AZ for ONTAP/OpenZFS/Windows, for production data requiring durability and automatic failover.
3. **Scale ONTAP with `ha_pairs`, not just throughput**: For sustained high throughput/IOPS beyond a single HA pair, use `ha_pairs` (2–6) with `throughput_capacity_per_ha_pair` instead of maxing out `throughput_capacity` on a single pair.
4. **Size appropriately at creation**: Lustre minimum ~1.2 TiB (PERSISTENT), ONTAP 1,024 GiB, OpenZFS 64 GiB, Windows 32 GiB (2,000 GiB minimum for HDD) — most capacity/throughput fields cannot shrink after creation.

### Performance Optimization

1. **Right-size throughput/IOPS**: Monitor CloudWatch metrics and adjust `throughput_capacity`/`disk_iops_configuration` to match observed workload patterns rather than over-provisioning up front.
2. **Enable compression**: Set `data_compression_type = "LZ4"` for Lustre and OpenZFS to reduce storage consumption and often improve effective throughput.
3. **Use EFA for ultra-low-latency Lustre**: Set `efa_enabled = true` (PERSISTENT_2 only) for GPU/HPC clients needing Elastic Fabric Adapter and GPUDirect Storage.
4. **Use ONTAP tiering for cost/performance balance**: Set a volume `tiering_policy` (`AUTO`/`SNAPSHOT_ONLY`) to move infrequently accessed data to lower-cost capacity pool storage automatically.
5. **Consider Lustre Intelligent-Tiering**: For PERSISTENT_2 workloads with uneven access patterns, use `storage_type = "INTELLIGENT_TIERING"` with `data_read_cache_configuration` to pay for used capacity rather than provisioned SSD.

### Security Best Practices

1. **Always configure ingress rules**: All four submodules create a security group with **no ingress rules by default** — the file system is unreachable from any client until `security_group_ingress_rules` is set to at least allow the required protocol/port from trusted CIDRs.
2. **Encrypt at rest with customer-managed KMS keys**: Set `kms_key_id` for sensitive workloads instead of relying on the AWS-managed default key, especially where key rotation/audit policies are required.
3. **Use Active Directory for authenticated access**: For Windows and ONTAP SMB, prefer AWS Managed Microsoft AD (`active_directory_id`) for centralized authentication over self-managed AD unless there's an existing on-premises AD to integrate with.
4. **Deploy in private subnets**: Never expose FSx file systems in public subnets; restrict `security_group_ingress_rules` CIDRs to VPC/on-premises ranges only.
5. **Use root squash for Lustre**: Configure `root_squash_configuration` to prevent root users on Lustre clients from having root-equivalent access to the file system.
6. **Use SnapLock for regulated/immutable data**: For ONTAP volumes holding compliance data, configure `snaplock_configuration` (`ENTERPRISE` or `COMPLIANCE`) with appropriate `retention_period`/`autocommit_period`.

### Backup and Disaster Recovery

1. **Enable automatic daily backups**: Set `automatic_backup_retention_days` (7–35 days is a common range) based on RPO requirements; `0` disables backups where supported.
2. **Don't skip the final backup in production**: Leave `skip_final_backup = false` (the default) for OpenZFS/Windows production file systems so a backup is captured automatically on deletion.
3. **Use ONTAP SnapMirror for cross-region DR**: Not managed by this module directly, but ONTAP file systems created here support SnapMirror replication configured via the AWS/NetApp CLI or additional `aws_fsx_*` resources.
4. **Treat S3 as durable storage for Lustre**: Use `data_repository_associations` so working-set data on the file system remains recoverable/independent of the file system's own lifecycle.

### Cost Optimization

1. **Use Scratch Lustre for ephemeral jobs**: `SCRATCH_1`/`SCRATCH_2` deployment types cost less and are appropriate for data that is reproducible or backed by S3.
2. **Enable ONTAP capacity pool tiering**: Move cold data out of primary SSD storage automatically via `tiering_policy`.
3. **Right-size storage and throughput**: Monitor utilization via CloudWatch and adjust capacity/throughput rather than over-provisioning "for headroom."
4. **Prefer HDD for large, throughput-oriented, latency-tolerant datasets** where supported (Lustre PERSISTENT_1, OpenZFS, Windows SINGLE_AZ_2/MULTI_AZ_1).

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-fsx
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-fsx/tree/master/examples
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-fsx/blob/master/CHANGELOG.md
- **AWS FSx Documentation**: https://docs.aws.amazon.com/fsx/
- **FSx for Lustre Guide**: https://docs.aws.amazon.com/fsx/latest/LustreGuide/what-is.html
- **FSx for NetApp ONTAP Guide**: https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/what-is-fsx-ontap.html
- **FSx for OpenZFS Guide**: https://docs.aws.amazon.com/fsx/latest/OpenZFSGuide/what-is-fsx.html
- **FSx for Windows Guide**: https://docs.aws.amazon.com/fsx/latest/WindowsGuide/what-is.html
- **Amazon File Cache**: https://docs.aws.amazon.com/fsx/latest/FileCacheGuide/what-is.html
- **FSx Pricing**: https://aws.amazon.com/fsx/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Always target a submodule directly**: There is no root `fsx` module resource — source `//modules/lustre`, `//modules/ontap`, `//modules/openzfs`, or `//modules/windows` explicitly.
2. **Submodule selection**: Choose based on workload — `lustre` for HPC/ML/S3-integrated analytics, `ontap` for multi-protocol enterprise/NetApp migration, `openzfs` for Linux NFS, `windows` for SMB.
3. **Ingress rules are mandatory for connectivity**: `security_group_ingress_rules` defaults to `{}` on every submodule — always populate it (or pass `security_group_ids` to an existing SG) or clients will be unable to reach the file system.
4. **Deployment type drives availability**: Use Multi-AZ (`MULTI_AZ_1`) for ONTAP/OpenZFS/Windows production workloads and PERSISTENT_1/2 for Lustre production workloads; Scratch Lustre and Single-AZ are for non-critical/dev workloads only.
5. **Windows always requires Active Directory**: Set exactly one of `active_directory_id` or `self_managed_active_directory` — omitting both will fail to apply.
6. **ONTAP scale-out uses `ha_pairs`, not multiple file systems**: For throughput/IOPS beyond one HA pair, set `ha_pairs` (2–6) and `throughput_capacity_per_ha_pair` rather than provisioning separate file systems.
7. **Enable KMS encryption with a customer-managed key** (`kms_key_id`) for production workloads instead of relying on the AWS-managed default.
8. **Enable automatic backups** (`automatic_backup_retention_days`, typically 7–30 days) for any production file system.
9. **S3 integration requires IAM permissions**: For Lustre `data_repository_associations`, ensure the FSx service role/account has the necessary S3 bucket permissions (`s3:GetObject`, `s3:PutObject`, `s3:ListBucket`, etc.).
10. **Reference module outputs for composition**: Use `file_system_id`, `file_system_arn`, and `file_system_dns_name` (or `file_system_endpoints` for ONTAP) to wire the file system into mount targets, EKS persistent volumes, or other modules.
11. **Tag consistently**: Populate the `tags` map on every submodule call for cost allocation and resource ownership tracking.
