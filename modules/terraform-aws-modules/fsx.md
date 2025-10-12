---
module_name: fsx
keywords: [fsx, file-system, lustre, ontap, netapp, openzfs, windows-file-server, smb, nfs, iscsi, nvme, storage, high-performance-computing, hpc, machine-learning, ml, scratch, persistent, ssd, hdd, intelligent-tiering, throughput, iops, s3-integration, data-repository, active-directory, multi-az, single-az, backup, snapshot, encryption, kms, compression, deduplication, tiering, cloudwatch, multi-protocol, svm, storage-virtual-machine, volume, subnet, security-group, vpc, efs, efa, elastic-fabric-adapter, zfs, cifs, data-lake, analytics, video-processing, financial-modeling, sagemaker, batch, eks, ecs, containers, file-share, shared-storage]
---

# Terraform AWS FSx Module

## Module Information

- **Module Name**: `fsx`
- **Source**: `terraform-aws-modules/fsx/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-fsx
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest
- **Latest Version**: 1.3.0
- **Purpose**: Terraform module that creates AWS FSx file system resources supporting Lustre, NetApp ONTAP, OpenZFS, and Windows File Server
- **Service**: AWS FSx (Fully Managed File Storage)
- **Category**: Storage, File Systems, High-Performance Computing
- **Keywords**: fsx, file-system, lustre, ontap, netapp, openzfs, windows-file-server, smb, nfs, iscsi, nvme, storage, high-performance-computing, hpc, machine-learning, ml, scratch, persistent, ssd, hdd, intelligent-tiering, throughput, iops, s3-integration, data-repository, active-directory, multi-az, single-az, backup, snapshot, encryption, kms, compression, deduplication, tiering, cloudwatch, multi-protocol, svm, storage-virtual-machine, volume, subnet, security-group, vpc, efs, efa, elastic-fabric-adapter, zfs, cifs, data-lake, analytics, video-processing, financial-modeling, sagemaker, batch, eks, ecs, containers, file-share, shared-storage
- **Use For**: High-performance computing clusters requiring sub-millisecond latency storage, machine learning training workloads with large datasets, migrating Windows file servers to AWS with Active Directory integration, running NetApp ONTAP workloads in the cloud, moving Linux ZFS file systems to AWS, video rendering and media processing workflows, financial modeling and simulations, genomics and life sciences data analysis, electronic design automation (EDA) workloads, shared storage for containerized applications

## Description

The AWS FSx Terraform module provides a comprehensive infrastructure-as-code solution for deploying and managing multiple types of AWS FSx file systems, each optimized for different workload requirements and protocols. AWS FSx is a suite of fully managed file storage services that eliminates the operational overhead of deploying, managing, and scaling file servers while providing high performance, rich features, and seamless integration with AWS services. The module offers four specialized submodules—Lustre, NetApp ONTAP, OpenZFS, and Windows File Server—each tailored to specific use cases, protocols, and performance characteristics, allowing teams to provision enterprise-grade file storage using declarative Terraform configurations.

FSx for Lustre delivers high-performance parallel file systems designed for compute-intensive workloads requiring sub-millisecond latencies and throughput measured in terabytes per second, with seamless S3 data repository integration for data lakes and analytics. FSx for NetApp ONTAP brings enterprise NetApp storage capabilities to AWS with support for multi-protocol access (NFS, SMB, iSCSI, NVMe), advanced data management features like snapshots and cloning, automatic tiering to reduce costs, and compatibility with existing NetApp tools and workflows. FSx for OpenZFS provides a fully managed implementation of the OpenZFS file system optimized for migrating Linux-based workloads, offering up to 2 million IOPS with microsecond latencies, instant snapshots, and thin provisioning. FSx for Windows File Server delivers native Windows file systems with SMB protocol support, Active Directory integration, and features like DFS, quotas, and file-level restore, making it ideal for Windows-based enterprise applications and shared storage scenarios.

The module architecture follows Terraform best practices with separate submodules for each file system type, allowing granular resource management, conditional creation, flexible networking configurations, and comprehensive security settings. Each submodule handles VPC integration, security group management, backup configuration, encryption with KMS, CloudWatch logging, and tagging. The module supports advanced deployment options including Multi-AZ high availability, intelligent tiering storage classes, data compression and deduplication, automated maintenance windows, and integration with AWS services like SageMaker, Batch, EKS, and ECS. This modular design enables teams to standardize FSx deployments across multiple file system types while maintaining consistent security policies, monitoring, and operational workflows.

## Key Features

- **4 Specialized Submodules**: Separate modules for Lustre, NetApp ONTAP, OpenZFS, and Windows File Server with type-specific configurations
- **FSx for Lustre**: High-performance parallel file system for HPC, ML, and analytics with S3 data repository integration
- **FSx for NetApp ONTAP**: Multi-protocol enterprise storage (NFS, SMB, iSCSI, NVMe) with ONTAP data management features
- **FSx for OpenZFS**: Managed OpenZFS implementation for Linux workloads with up to 2M IOPS and microsecond latencies
- **FSx for Windows File Server**: Native Windows file systems with SMB protocol and Active Directory integration
- **Multiple Deployment Types**: Support for Scratch (temporary), Persistent, Single-AZ, and Multi-AZ deployments based on workload needs
- **Storage Classes**: Flexible storage options including SSD, HDD, and Intelligent-Tiering for cost optimization
- **S3 Data Repository**: Automatic data synchronization between FSx Lustre and S3 buckets for data lake workflows
- **Multi-Protocol Support**: ONTAP submodule supports NFS, SMB, iSCSI, and NVMe protocols for heterogeneous environments
- **Storage Virtual Machines**: ONTAP SVM support for multi-tenancy and workload isolation
- **Active Directory Integration**: Native AD authentication for Windows File Server and ONTAP SMB shares
- **High Availability**: Multi-AZ deployment options with automatic failover for business-critical applications
- **Data Management Features**: Snapshots, cloning, compression, deduplication, and tiering capabilities
- **Security Group Management**: Automated security group creation and custom ingress/egress rule configuration
- **Encryption**: KMS encryption for data at rest and in transit with customer-managed or AWS-managed keys
- **Backup Configuration**: Automated backup policies with configurable retention periods and maintenance windows
- **CloudWatch Integration**: Logging and monitoring integration for operational observability
- **Performance Tuning**: Configurable throughput capacity (8-2048 MBps) and IOPS provisioning
- **Elastic Fabric Adapter**: EFA support for Lustre workloads requiring ultra-low latency networking
- **Root Squash Configuration**: Lustre root squash settings for security and access control
- **Volume Management**: Multiple volume support for OpenZFS and ONTAP with independent configurations
- **Tagging Support**: Comprehensive resource tagging for cost allocation and resource management

## Main Use Cases

1. **High-Performance Computing**: Parallel file storage for scientific simulations, weather modeling, and computational fluid dynamics
2. **Machine Learning Training**: Fast data access for training large-scale ML models with TensorFlow, PyTorch, or MXNet
3. **Video Rendering and Processing**: Shared storage for media workflows, transcoding, and post-production pipelines
4. **Financial Services**: Low-latency storage for trading systems, risk modeling, and quantitative analysis
5. **Genomics and Life Sciences**: High-throughput storage for DNA sequencing, protein folding, and drug discovery
6. **Electronic Design Automation**: Shared storage for semiconductor design, verification, and simulation workloads
7. **Windows Enterprise Applications**: File shares for business applications, home directories, and departmental storage
8. **NetApp Migration**: Lift-and-shift migration of on-premises NetApp ONTAP storage to AWS
9. **Linux File Server Migration**: Move ZFS-based Linux file servers to managed AWS infrastructure
10. **Container Storage**: Persistent volumes for Kubernetes (EKS) and Docker (ECS) containerized applications

## Submodules

### 1. lustre

- **Purpose**: Create high-performance FSx for Lustre file systems for compute-intensive workloads with S3 integration
- **Source**: `terraform-aws-modules/fsx/aws//modules/lustre`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/lustre
- **Key Features**: Scratch and persistent deployment types, SSD/HDD/Intelligent-Tiering storage, S3 data repository associations, sub-millisecond latencies
- **Use Cases**: HPC clusters, ML training, video processing, financial simulations, data analytics pipelines

### 2. ontap

- **Purpose**: Create FSx for NetApp ONTAP file systems with multi-protocol support and enterprise data management
- **Source**: `terraform-aws-modules/fsx/aws//modules/ontap`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/ontap
- **Key Features**: Multi-protocol access (NFS/SMB/iSCSI/NVMe), Storage Virtual Machines (SVMs), snapshots, cloning, compression, deduplication
- **Use Cases**: Enterprise file shares, database storage, VMware Cloud on AWS, multi-tenant storage, NetApp migrations

### 3. openzfs

- **Purpose**: Create FSx for OpenZFS file systems for Linux-based workloads requiring high IOPS and low latency
- **Source**: `terraform-aws-modules/fsx/aws//modules/openzfs`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/openzfs
- **Key Features**: Up to 2M IOPS, microsecond latencies, instant snapshots, data compression, NFS protocol, thin provisioning
- **Use Cases**: Linux file server migrations, database storage, container persistent volumes, analytics workloads

### 4. windows

- **Purpose**: Create FSx for Windows File Server with SMB protocol and Active Directory integration
- **Source**: `terraform-aws-modules/fsx/aws//modules/windows`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/fsx/aws/latest/submodules/windows
- **Key Features**: Native Windows file system, SMB 2.0-3.1.1 protocol, Active Directory authentication, DFS namespaces, file-level restore
- **Use Cases**: Windows applications, home directories, web serving, content management, WorkSpaces storage, SQL Server storage

## Best Practices

### File System Selection and Design

1. **Choose the Right File System Type**: Use Lustre for HPC/ML, ONTAP for multi-protocol enterprise storage, OpenZFS for Linux migrations, Windows for SMB workloads
2. **Deployment Type Selection**: Use Scratch for temporary/cost-sensitive workloads, Persistent for production data requiring durability
3. **Multi-AZ for Production**: Deploy Multi-AZ file systems for business-critical applications requiring high availability and automatic failover
4. **Storage Class Optimization**: Use SSD for latency-sensitive workloads, HDD for throughput-oriented large datasets, Intelligent-Tiering for cost optimization
5. **Capacity Planning**: Size storage capacity based on workload requirements; Lustre requires 1.2 TiB minimum, ONTAP 1 TiB, OpenZFS 64 GiB, Windows 32 GiB
6. **Throughput Configuration**: Match throughput capacity (MBps) to application needs; start conservatively and scale up based on metrics
7. **Volume Architecture**: For ONTAP and OpenZFS, use multiple volumes to separate workloads and apply different configurations per volume
8. **Data Repository Strategy**: For Lustre, configure S3 data repository associations for seamless data lake integration and cost-effective long-term storage

### Performance Optimization

1. **Right-Size Throughput**: Monitor CloudWatch metrics and adjust throughput capacity to match workload patterns; avoid over-provisioning
2. **IOPS Provisioning**: For ONTAP, provision IOPS independently from throughput when applications need high random I/O performance
3. **Compression Configuration**: Enable data compression for ONTAP and OpenZFS to reduce storage costs and improve effective throughput
4. **Deduplication**: Enable deduplication on ONTAP volumes with redundant data patterns to optimize storage efficiency
5. **EFA for Lustre**: Use Elastic Fabric Adapter (EFA) networking for Lustre workloads requiring ultra-low latency and high bandwidth
6. **Client Caching**: Configure appropriate client-side caching settings to reduce file system load and improve application responsiveness
7. **Parallel Access**: Design applications to leverage parallel access patterns; Lustre excels at simultaneous access from multiple clients
8. **Stripe Configuration**: For Lustre, configure appropriate stripe count and size based on file sizes and access patterns
9. **Read/Write Patterns**: Optimize for sequential I/O when possible; both Lustre and OpenZFS perform best with large sequential operations
10. **Storage Tiering**: Use ONTAP capacity pool tiering to automatically move infrequently accessed data to lower-cost S3 storage

### Security Best Practices

1. **Encryption at Rest**: Always enable KMS encryption for data at rest using customer-managed keys for sensitive workloads
2. **Encryption in Transit**: All FSx file systems support encryption in transit; ensure clients use encrypted protocols (TLS, Kerberos)
3. **Security Group Restrictions**: Configure security groups to allow access only from specific subnets, security groups, or CIDR ranges
4. **Active Directory Integration**: For Windows and ONTAP SMB, use AWS Managed Microsoft AD or self-managed AD for centralized authentication
5. **IAM Access Control**: Use IAM policies to control who can create, modify, and delete FSx file systems and backups
6. **Network Isolation**: Deploy file systems in private subnets; use VPC endpoints for AWS service integration without internet exposure
7. **Audit Logging**: Enable CloudWatch Logs for Windows File Server audit events and ONTAP file access auditing
8. **Backup Encryption**: Ensure automated backups are encrypted with the same or higher security as the source file system
9. **Root Squash**: For Lustre, enable root squash to prevent root users on clients from having root access to the file system
10. **Antivirus Scanning**: For Windows File Server, integrate with AWS-compatible antivirus solutions for real-time protection

### Backup and Disaster Recovery

1. **Automated Backups**: Enable automatic daily backups with appropriate retention periods (7-90 days based on RPO requirements)
2. **Backup Windows**: Schedule backup windows during low-activity periods to minimize performance impact
3. **Manual Snapshots**: Create manual snapshots before major changes or deployments for instant rollback capability
4. **Cross-Region Replication**: For ONTAP, use SnapMirror for cross-region replication to meet disaster recovery requirements
5. **Retention Policies**: Define backup retention policies based on compliance requirements and recovery point objectives
6. **Backup Testing**: Regularly test backup restoration to validate recovery procedures and meet RTO objectives
7. **Point-in-Time Recovery**: Leverage ONTAP and OpenZFS snapshot capabilities for granular point-in-time recovery
8. **Clone for Testing**: Use ONTAP FlexClone or OpenZFS clones to create instant, space-efficient copies for testing
9. **S3 Data Repository**: For Lustre, use S3 as a data repository for durable, long-term storage independent of file system lifecycle
10. **Multi-AZ Failover Testing**: Periodically test Multi-AZ failover to validate automatic failover and recovery time objectives

### Cost Optimization

1. **Intelligent-Tiering Storage**: Use Intelligent-Tiering storage class for Lustre to automatically optimize costs based on access patterns
2. **Capacity Pool Tiering**: Enable ONTAP capacity pool tiering to move infrequently accessed data to S3 at lower cost
3. **Data Compression**: Enable compression to reduce storage capacity consumption without additional cost
4. **Deduplication**: Use ONTAP deduplication to eliminate redundant data and reduce storage costs
5. **Right-Size Storage**: Monitor storage utilization and adjust capacity to avoid paying for unused space
6. **Scratch for Temporary Workloads**: Use Lustre Scratch deployment type for temporary compute jobs to reduce costs
7. **Backup Retention**: Optimize backup retention periods to balance recovery needs with backup storage costs
8. **Throughput Matching**: Avoid over-provisioning throughput capacity; scale up incrementally based on actual usage
9. **HDD for Large Datasets**: Use HDD storage class for large, throughput-oriented workloads where latency is less critical
10. **Thin Provisioning**: Use OpenZFS thin provisioning to allocate storage on-demand rather than pre-allocating full capacity

### Monitoring and Observability

1. **CloudWatch Metrics**: Monitor key metrics including throughput, IOPS, storage capacity, and network throughput
2. **CloudWatch Alarms**: Create alarms for storage capacity (>80%), throughput saturation, and error rates
3. **Performance Baselines**: Establish performance baselines during normal operation for anomaly detection
4. **Client Metrics**: Monitor client-side metrics to identify application-level performance issues vs file system issues
5. **Audit Logging**: Enable and regularly review Windows File Server audit logs for security and compliance
6. **CloudWatch Logs Integration**: Export FSx logs to CloudWatch Logs for centralized log analysis and long-term retention
7. **Dashboard Creation**: Build CloudWatch dashboards showing file system health, performance, and capacity trends
8. **SNS Notifications**: Configure SNS topics for critical alerts requiring immediate operator attention
9. **Capacity Planning**: Track storage growth rates and project future capacity needs for proactive scaling
10. **Network Monitoring**: Monitor VPC Flow Logs for network traffic patterns and potential connectivity issues

### High Availability and Reliability

1. **Multi-AZ Deployments**: Use Multi-AZ for production workloads requiring 99.9% availability SLA
2. **Subnet Configuration**: For Multi-AZ, specify subnets in different availability zones for automatic failover
3. **Route Table Validation**: Ensure route tables for standby subnets allow proper network connectivity during failover
4. **Client Reconnection**: Design applications to handle brief interruptions during Multi-AZ failover (typically <1 minute)
5. **Health Monitoring**: Monitor file system status and health checks to detect issues before they impact applications
6. **Maintenance Windows**: Schedule maintenance windows during low-activity periods to minimize impact
7. **Update Strategy**: Allow AWS to apply patches automatically during maintenance windows for security and reliability
8. **Connection Limits**: Monitor concurrent connection counts and ensure applications respect file system limits
9. **Retry Logic**: Implement exponential backoff retry logic in applications for transient failures
10. **Dependency Management**: Ensure applications can gracefully handle file system unavailability at startup

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
- **FSx Performance**: https://docs.aws.amazon.com/fsx/latest/LustreGuide/performance.html
- **FSx Security**: https://docs.aws.amazon.com/fsx/latest/LustreGuide/security.html
- **FSx Best Practices**: https://docs.aws.amazon.com/fsx/latest/LustreGuide/best-practices.html
- **NetApp Cloud Volumes**: https://docs.netapp.com/us-en/cloud-manager-fsx-ontap/
- **OpenZFS Documentation**: https://openzfs.org/wiki/Main_Page

## Notes for AI Agents

When using this module in automated workflows:

1. **Submodule Selection**: Choose the appropriate submodule based on workload: `lustre` for HPC/ML, `ontap` for multi-protocol enterprise, `openzfs` for Linux, `windows` for SMB
2. **Deployment Type**: Use Scratch for temporary workloads, Persistent for production, Multi-AZ for high availability requirements
3. **Storage Sizing**: Start with minimum required capacity; Lustre 1.2 TiB, ONTAP 1 TiB, OpenZFS 64 GiB, Windows 32 GiB
4. **Throughput Configuration**: Match throughput to workload (8-2048 MBps); monitor and adjust based on CloudWatch metrics
5. **Security Groups**: Always configure security groups to restrict access to known client subnets or security groups
6. **Encryption**: Enable KMS encryption with customer-managed keys for production and sensitive data workloads
7. **Backup Strategy**: Enable automatic backups with 7-30 day retention for production file systems
8. **Network Configuration**: Deploy in private subnets with appropriate route tables; use VPC endpoints for AWS service access
9. **Active Directory**: For Windows or ONTAP SMB, ensure AD integration is properly configured with valid credentials
10. **Monitoring**: Set up CloudWatch alarms for capacity (>80%), throughput, IOPS, and file system health
11. **S3 Integration**: For Lustre, configure data repository associations to integrate with S3 data lakes
12. **Tagging**: Implement comprehensive tagging for cost allocation, environment identification, and resource management
