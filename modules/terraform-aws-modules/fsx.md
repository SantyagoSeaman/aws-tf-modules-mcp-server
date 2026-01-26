# Terraform AWS FSx Module

## Module Information

- **Module Name**: `fsx`
- **Source**: `terraform-aws-modules/fsx/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-fsx
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest
- **Latest Version**: 1.3.1
- **Purpose**: Terraform module to create AWS FSx file systems supporting Lustre, NetApp ONTAP, OpenZFS, and Windows File Server
- **Service**: AWS FSx (Fully Managed File Storage)
- **Category**: Storage, File Systems, High-Performance Computing
- **Keywords**: fsx, lustre, ontap, openzfs, windows-file-server, high-performance-storage, nfs, smb, iscsi, s3-integration, active-directory, multi-az, backup, encryption, hpc, machine-learning, file-share, shared-storage
- **Use For**: High-performance computing clusters, machine learning training workloads, Windows file server migration with Active Directory, NetApp ONTAP workloads in AWS, Linux ZFS file system migration, video rendering and media processing, container persistent storage (EKS/ECS)

## Description

The AWS FSx Terraform module provides a comprehensive infrastructure-as-code solution for deploying and managing multiple types of AWS FSx file systems, each optimized for different workload requirements and protocols. AWS FSx is a suite of fully managed file storage services that eliminates the operational overhead of deploying, managing, and scaling file servers while providing high performance, rich features, and seamless integration with AWS services. The module offers four specialized submodules—Lustre, NetApp ONTAP, OpenZFS, and Windows File Server—each tailored to specific use cases, protocols, and performance characteristics.

FSx for Lustre delivers high-performance parallel file systems designed for compute-intensive workloads requiring sub-millisecond latencies and throughput measured in terabytes per second, with seamless S3 data repository integration for data lakes and analytics. FSx for NetApp ONTAP brings enterprise NetApp storage capabilities to AWS with support for multi-protocol access (NFS, SMB, iSCSI, NVMe), advanced data management features like snapshots and cloning, automatic tiering to reduce costs, and compatibility with existing NetApp tools. FSx for OpenZFS provides a fully managed implementation of the OpenZFS file system optimized for migrating Linux-based workloads, offering up to 2 million IOPS with microsecond latencies, instant snapshots, and thin provisioning. FSx for Windows File Server delivers native Windows file systems with SMB protocol support, Active Directory integration, and features like DFS, quotas, and file-level restore.

The module architecture follows Terraform best practices with separate submodules for each file system type, allowing granular resource management, conditional creation, flexible networking configurations, and comprehensive security settings. Each submodule handles VPC integration, security group management, backup configuration, encryption with KMS, CloudWatch logging, and tagging.

## Key Features

- **4 Specialized Submodules**: Separate modules for Lustre, NetApp ONTAP, OpenZFS, and Windows File Server
- **FSx for Lustre**: High-performance parallel file system for HPC/ML with S3 data repository integration
- **FSx for NetApp ONTAP**: Multi-protocol enterprise storage (NFS, SMB, iSCSI) with ONTAP data management
- **FSx for OpenZFS**: Managed OpenZFS for Linux workloads with up to 2M IOPS and microsecond latencies
- **FSx for Windows File Server**: Native Windows file systems with SMB protocol and Active Directory
- **Multiple Deployment Types**: Scratch, Persistent, Single-AZ, and Multi-AZ deployments
- **Storage Classes**: SSD, HDD, and Intelligent-Tiering options for cost optimization
- **S3 Data Repository**: Automatic data synchronization between FSx Lustre and S3 buckets
- **Multi-Protocol Support**: ONTAP supports NFS, SMB, iSCSI, and NVMe protocols
- **Storage Virtual Machines**: ONTAP SVM support for multi-tenancy and workload isolation
- **Active Directory Integration**: Native AD authentication for Windows and ONTAP SMB
- **High Availability**: Multi-AZ deployment with automatic failover
- **Data Management**: Snapshots, cloning, compression, deduplication, and tiering
- **Security Group Management**: Automated security group creation with custom rules
- **Encryption**: KMS encryption for data at rest and in transit
- **Backup Configuration**: Automated backups with 0-90 day retention
- **CloudWatch Integration**: Logging and monitoring for operational observability

## Main Use Cases

1. **High-Performance Computing**: Parallel file storage for scientific simulations and computational workloads
2. **Machine Learning Training**: Fast data access for training large-scale ML models
3. **Video Rendering and Processing**: Shared storage for media workflows and post-production
4. **Financial Services**: Low-latency storage for trading systems and risk modeling
5. **Genomics and Life Sciences**: High-throughput storage for DNA sequencing and drug discovery
6. **Windows Enterprise Applications**: File shares, home directories, and departmental storage
7. **NetApp Migration**: Lift-and-shift migration of on-premises NetApp ONTAP storage
8. **Linux File Server Migration**: Move ZFS-based Linux file servers to managed AWS infrastructure
9. **Container Storage**: Persistent volumes for Kubernetes (EKS) and Docker (ECS) applications

## Submodules

### 1. lustre

- **Purpose**: Create high-performance FSx for Lustre file systems for compute-intensive workloads with S3 integration
- **Source**: `terraform-aws-modules/fsx/aws//modules/lustre`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/lustre
- **Key Features**: Scratch and persistent deployment types, SSD/HDD/Intelligent-Tiering storage, S3 data repository associations, sub-millisecond latencies
- **Use Cases**: HPC clusters, ML training, video processing, financial simulations, data analytics pipelines

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name for the file system |
| `deployment_type` | `string` | required | SCRATCH_1, SCRATCH_2, PERSISTENT_1, or PERSISTENT_2 |
| `storage_capacity` | `number` | required | Storage capacity in GiB |
| `storage_type` | `string` | `"SSD"` | SSD, HDD (PERSISTENT_1 only), or INTELLIGENT_TIERING |
| `subnet_ids` | `list(string)` | required | Subnet IDs for file system deployment |
| `per_unit_storage_throughput` | `number` | `null` | Throughput per TiB (50, 100, 125, 200, 250, 500, 1000 MB/s) |
| `data_compression_type` | `string` | `"NONE"` | LZ4 or NONE |
| `automatic_backup_retention_days` | `number` | `0` | Backup retention (0-90 days, PERSISTENT only) |
| `data_repository_associations` | `map(object)` | `{}` | S3 data repository configurations |
| `security_group_ingress_rules` | `map(object)` | `{}` | Ingress rules for security group |

#### Main Outputs

| Output | Description |
|--------|-------------|
| `file_system_id` | FSx file system ID |
| `file_system_arn` | File system ARN |
| `file_system_dns_name` | DNS name for mounting |
| `file_system_mount_name` | Lustre mount name |
| `security_group_id` | Security group ID |

#### Usage Example

```hcl
module "fsx_lustre" {
  source  = "terraform-aws-modules/fsx/aws//modules/lustre"
  version = "~> 1.3"

  name             = "ml-training-lustre"
  deployment_type  = "PERSISTENT_1"
  storage_capacity = 1200
  storage_type     = "SSD"
  subnet_ids       = [module.vpc.private_subnets[0]]

  per_unit_storage_throughput = 50
  data_compression_type       = "LZ4"

  # S3 data repository integration
  data_repository_associations = {
    s3_data = {
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
      description = "Allow VPC traffic"
    }
  }

  tags = { Environment = "production" }
}
```

### 2. ontap

- **Purpose**: Create FSx for NetApp ONTAP file systems with multi-protocol support and enterprise data management
- **Source**: `terraform-aws-modules/fsx/aws//modules/ontap`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/ontap
- **Key Features**: Multi-protocol access (NFS/SMB/iSCSI), Storage Virtual Machines (SVMs), snapshots, cloning, compression, deduplication, SnapLock compliance
- **Use Cases**: Enterprise file shares, database storage, VMware Cloud on AWS, multi-tenant storage, NetApp migrations

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name for the file system |
| `deployment_type` | `string` | required | SINGLE_AZ_1 or MULTI_AZ_1 |
| `storage_capacity` | `number` | required | Storage capacity in GiB |
| `throughput_capacity` | `number` | required | Throughput in MBps (128, 256, 512, 1024, 2048, 4096) |
| `subnet_ids` | `list(string)` | required | Subnet IDs for deployment |
| `preferred_subnet_id` | `string` | `null` | Primary subnet for Multi-AZ (required for MULTI_AZ_1) |
| `fsx_admin_password` | `string` | `null` | ONTAP admin password (sensitive) |
| `automatic_backup_retention_days` | `number` | `7` | Backup retention (0-90 days) |
| `route_table_ids` | `list(string)` | `[]` | Route tables for Multi-AZ |
| `storage_virtual_machines` | `map(object)` | `{}` | SVM configurations with volumes |
| `security_group_ingress_rules` | `map(object)` | `{}` | Ingress rules for security group |

#### Main Outputs

| Output | Description |
|--------|-------------|
| `file_system_id` | FSx file system ID |
| `file_system_arn` | File system ARN |
| `file_system_dns_name` | Management DNS endpoint |
| `file_system_endpoints` | ONTAP CLI, REST API, and iSCSI endpoints |
| `storage_virtual_machines` | Map of SVM configurations |
| `volumes` | Map of volume details |
| `security_group_id` | Security group ID |

#### Usage Example

```hcl
module "fsx_ontap" {
  source  = "terraform-aws-modules/fsx/aws//modules/ontap"
  version = "~> 1.3"

  name                = "enterprise-ontap"
  deployment_type     = "MULTI_AZ_1"
  storage_capacity    = 1024
  throughput_capacity = 256
  subnet_ids          = module.vpc.private_subnets
  preferred_subnet_id = module.vpc.private_subnets[0]
  route_table_ids     = module.vpc.private_route_table_ids

  fsx_admin_password = var.ontap_admin_password

  storage_virtual_machines = {
    svm1 = {
      name = "production-svm"
      volumes = {
        data = {
          name                       = "data-vol"
          junction_path              = "/data"
          size_in_bytes              = 107374182400  # 100 GiB
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
    vpc = { cidr_ipv4 = module.vpc.vpc_cidr_block }
  }

  tags = { Environment = "production" }
}
```

### 3. openzfs

- **Purpose**: Create FSx for OpenZFS file systems for Linux-based workloads requiring high IOPS and low latency
- **Source**: `terraform-aws-modules/fsx/aws//modules/openzfs`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/openzfs
- **Key Features**: Up to 2M IOPS, microsecond latencies, instant snapshots, data compression, NFS protocol, thin provisioning, quotas
- **Use Cases**: Linux file server migrations, database storage, container persistent volumes, analytics workloads

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name for the file system |
| `deployment_type` | `string` | required | SINGLE_AZ_1 or MULTI_AZ_1 |
| `storage_capacity` | `number` | required | Storage capacity in GiB |
| `storage_type` | `string` | `"SSD"` | SSD or HDD |
| `throughput_capacity` | `number` | required | Throughput in MBps (128, 256, 512, 1024, 2048) |
| `subnet_ids` | `list(string)` | required | Subnet IDs for deployment |
| `automatic_backup_retention_days` | `number` | `0` | Backup retention (0-90 days) |
| `root_volume_configuration` | `object` | `{}` | Root volume settings (compression, quotas, NFS exports) |
| `volumes` | `map(object)` | `{}` | Child volume configurations |
| `disk_iops_configuration` | `object` | `null` | IOPS mode and value |
| `security_group_ingress_rules` | `map(object)` | `{}` | Ingress rules for security group |

#### Main Outputs

| Output | Description |
|--------|-------------|
| `file_system_id` | FSx file system ID |
| `file_system_arn` | File system ARN |
| `file_system_dns_name` | NFS mount endpoint |
| `file_system_root_volume_id` | Root volume ID |
| `volumes` | Map of child volume attributes |
| `security_group_id` | Security group ID |

#### Usage Example

```hcl
module "fsx_openzfs" {
  source  = "terraform-aws-modules/fsx/aws//modules/openzfs"
  version = "~> 1.3"

  name                = "linux-zfs"
  deployment_type     = "SINGLE_AZ_1"
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
    vpc = { cidr_ipv4 = module.vpc.vpc_cidr_block }
  }

  tags = { Environment = "production" }
}
```

### 4. windows

- **Purpose**: Create FSx for Windows File Server with SMB protocol and Active Directory integration
- **Source**: `terraform-aws-modules/fsx/aws//modules/windows`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/windows
- **Key Features**: Native Windows file system, SMB 2.0-3.1.1 protocol, Active Directory authentication, DFS namespaces, audit logging, shadow copies
- **Use Cases**: Windows applications, home directories, web serving, content management, WorkSpaces storage, SQL Server storage

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name for the file system |
| `storage_capacity` | `number` | required | Storage in GiB (32-65,536; min 2,000 for HDD) |
| `storage_type` | `string` | `"SSD"` | SSD or HDD |
| `throughput_capacity` | `number` | required | MBps (8-2,048 in power-of-2 increments) |
| `deployment_type` | `string` | `"SINGLE_AZ_1"` | SINGLE_AZ_1, SINGLE_AZ_2, or MULTI_AZ_1 |
| `subnet_ids` | `list(string)` | required | Subnet IDs for deployment |
| `preferred_subnet_id` | `string` | `null` | Primary subnet for Multi-AZ |
| `active_directory_id` | `string` | `null` | AWS Managed Microsoft AD directory ID |
| `self_managed_active_directory` | `object` | `null` | On-premises AD configuration |
| `automatic_backup_retention_days` | `number` | `7` | Backup retention (0-90 days) |
| `audit_log_configuration` | `object` | `null` | Audit logging settings |
| `aliases` | `list(string)` | `[]` | DNS aliases for file system access |
| `security_group_ingress_rules` | `map(object)` | `{}` | Ingress rules for security group |

**Note**: Either `active_directory_id` OR `self_managed_active_directory` is required (mutually exclusive).

#### Main Outputs

| Output | Description |
|--------|-------------|
| `file_system_id` | FSx file system ID |
| `file_system_arn` | File system ARN |
| `file_system_dns_name` | Primary DNS endpoint for SMB access |
| `preferred_file_server_ip` | IP of preferred file server |
| `remote_administration_endpoint` | PowerShell remote management endpoint |
| `cloudwatch_log_group_arn` | Audit log group ARN |
| `security_group_id` | Security group ID |

#### Usage Example

```hcl
module "fsx_windows" {
  source  = "terraform-aws-modules/fsx/aws//modules/windows"
  version = "~> 1.3"

  name                = "windows-file-server"
  storage_capacity    = 1024
  storage_type        = "SSD"
  throughput_capacity = 512
  deployment_type     = "MULTI_AZ_1"
  subnet_ids          = module.vpc.private_subnets
  preferred_subnet_id = module.vpc.private_subnets[0]

  # AWS Managed Microsoft AD
  active_directory_id = aws_directory_service_directory.this.id

  # Audit logging
  audit_log_configuration = {
    file_access_audit_log_level       = "SUCCESS_AND_FAILURE"
    file_share_access_audit_log_level = "SUCCESS_AND_FAILURE"
  }

  # Backup configuration
  automatic_backup_retention_days   = 7
  daily_automatic_backup_start_time = "05:00"
  copy_tags_to_backups              = true

  security_group_ingress_rules = {
    vpc = {
      cidr_ipv4   = module.vpc.vpc_cidr_block
      description = "Allow VPC traffic"
    }
  }

  tags = { Environment = "production" }
}
```

## Best Practices

### File System Selection and Design

1. **Choose the Right File System Type**: Use Lustre for HPC/ML, ONTAP for multi-protocol enterprise storage, OpenZFS for Linux migrations, Windows for SMB workloads
2. **Deployment Type Selection**: Use Scratch for temporary/cost-sensitive workloads, Persistent for production data requiring durability
3. **Multi-AZ for Production**: Deploy Multi-AZ file systems for business-critical applications requiring high availability
4. **Storage Class Optimization**: Use SSD for latency-sensitive workloads, HDD for throughput-oriented large datasets, Intelligent-Tiering for cost optimization
5. **Capacity Planning**: Size appropriately—Lustre minimum 1.2 TiB, ONTAP 1 TiB, OpenZFS 64 GiB, Windows 32 GiB

### Performance Optimization

1. **Right-Size Throughput**: Monitor CloudWatch metrics and adjust throughput capacity to match workload patterns
2. **Compression Configuration**: Enable LZ4 compression for ONTAP and OpenZFS to reduce storage costs
3. **EFA for Lustre**: Use Elastic Fabric Adapter for Lustre workloads requiring ultra-low latency networking
4. **Storage Tiering**: Use ONTAP capacity pool tiering to move infrequently accessed data to lower-cost S3 storage
5. **IOPS Provisioning**: For ONTAP and OpenZFS, provision IOPS independently when applications need high random I/O

### Security Best Practices

1. **Encryption at Rest**: Always enable KMS encryption using customer-managed keys for sensitive workloads
2. **Security Group Restrictions**: Configure security groups to allow access only from specific subnets or CIDR ranges
3. **Active Directory Integration**: For Windows and ONTAP SMB, use AWS Managed Microsoft AD for centralized authentication
4. **Network Isolation**: Deploy file systems in private subnets; use VPC endpoints for AWS service integration
5. **Root Squash**: For Lustre, enable root squash to prevent root users on clients from having root access

### Backup and Disaster Recovery

1. **Automated Backups**: Enable automatic daily backups with 7-90 day retention based on RPO requirements
2. **Cross-Region Replication**: For ONTAP, use SnapMirror for cross-region replication
3. **Point-in-Time Recovery**: Leverage ONTAP and OpenZFS snapshot capabilities for granular recovery
4. **S3 Data Repository**: For Lustre, use S3 as durable long-term storage independent of file system lifecycle

### Cost Optimization

1. **Intelligent-Tiering Storage**: Use Intelligent-Tiering for Lustre to optimize costs based on access patterns
2. **Capacity Pool Tiering**: Enable ONTAP capacity pool tiering to move cold data to S3
3. **Scratch for Temporary Workloads**: Use Lustre Scratch deployment for temporary compute jobs
4. **Right-Size Storage**: Monitor utilization and adjust capacity to avoid paying for unused space
5. **HDD for Large Datasets**: Use HDD storage class for throughput-oriented workloads where latency is less critical

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-fsx
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-fsx/tree/master/examples
- **AWS FSx Documentation**: https://docs.aws.amazon.com/fsx/
- **FSx for Lustre Guide**: https://docs.aws.amazon.com/fsx/latest/LustreGuide/what-is.html
- **FSx for NetApp ONTAP Guide**: https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/what-is-fsx-ontap.html
- **FSx for OpenZFS Guide**: https://docs.aws.amazon.com/fsx/latest/OpenZFSGuide/what-is-fsx.html
- **FSx for Windows Guide**: https://docs.aws.amazon.com/fsx/latest/WindowsGuide/what-is.html
- **FSx Pricing**: https://aws.amazon.com/fsx/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Submodule Selection**: Choose based on workload—`lustre` for HPC/ML, `ontap` for multi-protocol enterprise, `openzfs` for Linux, `windows` for SMB
2. **Deployment Type**: Use Scratch for temporary workloads, Persistent for production, Multi-AZ for high availability
3. **Storage Sizing**: Start with minimum capacity—Lustre 1.2 TiB, ONTAP 1 TiB, OpenZFS 64 GiB, Windows 32 GiB
4. **Throughput Configuration**: Match throughput to workload (8-2048 MBps); monitor and adjust based on metrics
5. **Security Groups**: Always configure security groups to restrict access to known client subnets
6. **Encryption**: Enable KMS encryption with customer-managed keys for production workloads
7. **Backup Strategy**: Enable automatic backups with 7-30 day retention for production file systems
8. **Network Configuration**: Deploy in private subnets with appropriate route tables
9. **Active Directory**: For Windows or ONTAP SMB, ensure AD integration is properly configured
10. **Windows Requirement**: Windows File Server always requires Active Directory (AWS Managed or self-managed)
11. **S3 Integration**: For Lustre data repository associations, ensure IAM role has S3 access permissions
12. **Tagging**: Implement comprehensive tagging for cost allocation and resource management
