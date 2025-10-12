---
module_name: efs
keywords: [efs, elastic-file-system, nfs, network-file-system, shared-storage, file-storage, mount-targets, access-points, posix, file-system-encryption, kms-encryption, at-rest-encryption, in-transit-encryption, performance-mode, general-purpose, max-io, throughput-mode, bursting, elastic, provisioned-throughput, lifecycle-policy, infrequent-access, ia-storage, backup-policy, aws-backup, replication, cross-region, multi-az, availability-zones, security-groups, file-system-policy, iam-policy, nfs-mount, linux, container-storage, ecs, eks, kubernetes, persistent-storage, stateful-applications]
---

# Terraform AWS EFS Module

## Module Information

- **Module Name**: `efs`
- **Source**: `terraform-aws-modules/efs/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-efs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/efs/aws/latest
- **Latest Version**: 1.8.0
- **Purpose**: Terraform module that creates and manages AWS Elastic File System (EFS) resources for scalable, shared file storage across multiple EC2 instances and containers
- **Service**: AWS EFS (Elastic File System)
- **Category**: Storage, File Storage, Network File System
- **Keywords**: efs, elastic-file-system, nfs, network-file-system, shared-storage, file-storage, mount-targets, access-points, posix, file-system-encryption, kms-encryption, at-rest-encryption, in-transit-encryption, performance-mode, general-purpose, max-io, throughput-mode, bursting, elastic, provisioned-throughput, lifecycle-policy, infrequent-access, ia-storage, backup-policy, aws-backup, replication, cross-region, multi-az, availability-zones, security-groups, file-system-policy, iam-policy, nfs-mount, linux, container-storage, ecs, eks, kubernetes, persistent-storage, stateful-applications
- **Use For**: shared application storage, container persistent volumes, content management systems, web server content sharing, development environments, big data analytics, machine learning training data, media processing workflows, home directories, database backups, cross-instance data sharing, Kubernetes persistent storage

## Description

AWS Elastic File System (EFS) is a fully managed, elastic, scalable network file system that provides simple, scalable file storage for use with AWS Cloud services and on-premises resources. This Terraform module provides a comprehensive solution for creating and managing EFS file systems with support for encryption, access points, mount targets, lifecycle policies, and cross-region replication. The module simplifies the process of deploying shared file storage that can be accessed simultaneously by thousands of EC2 instances, ECS containers, Lambda functions, and on-premises servers through AWS Direct Connect or VPN.

The module supports multiple performance and throughput configurations to meet different workload requirements, from general-purpose file sharing to high-throughput big data analytics. It enables fine-grained access control through EFS access points with POSIX user and group settings, allowing multiple applications or teams to share a single file system with isolated views. The module handles mount target creation across multiple availability zones for high availability, configures security groups for NFS traffic, and supports both at-rest encryption using AWS KMS and in-transit encryption using TLS. It also provides lifecycle management policies to automatically transition infrequently accessed files to a cost-optimized Infrequent Access (IA) storage class.

This module is essential for organizations running stateful applications, containerized workloads on ECS or EKS, or any scenario requiring shared file storage across multiple compute resources. It integrates seamlessly with AWS Backup for automated backup management and supports cross-region replication for disaster recovery scenarios. The module's support for access points makes it ideal for multi-tenant applications, where each tenant requires isolated access to specific directories with their own permissions. With comprehensive tagging, monitoring integration, and policy-based access control, this module serves as the foundation for enterprise-grade shared file storage in AWS.

## Key Features

- **Managed Network File System**: Fully managed NFSv4.1 and NFSv4.0 protocol support for Linux-based workloads
- **Encryption at Rest**: Encrypt file system data at rest using AWS-managed or customer-managed KMS keys
- **In-Transit Encryption**: Support for TLS encryption of data in transit between clients and EFS
- **Performance Modes**: Choose between General Purpose (low latency) or Max I/O (high throughput, higher latency) modes
- **Throughput Modes**: Select Bursting (scales with file system size), Elastic (automatic scaling), or Provisioned (fixed throughput) modes
- **Multi-AZ Mount Targets**: Create mount targets in multiple availability zones for high availability and fault tolerance
- **One Zone Storage Class**: Deploy file systems to a single availability zone for cost optimization (up to 47% savings)
- **Access Points**: Define application-specific entry points with POSIX user identity and root directory settings
- **POSIX Permissions**: Enforce POSIX user IDs, group IDs, and file permissions at the access point level
- **Lifecycle Management**: Automatically transition files to Infrequent Access (IA) storage class based on access patterns
- **Infrequent Access Storage**: Cost-optimized storage class for files accessed less frequently (up to 92% cost reduction)
- **Backup Policies**: Enable automatic backups using AWS Backup service with configurable retention policies
- **Cross-Region Replication**: Replicate file systems to other AWS regions for disaster recovery and compliance
- **File System Policies**: Define IAM-based access control policies at the file system level
- **Security Group Integration**: Configure security groups to control NFS traffic to mount targets
- **Elastic Scaling**: Automatically scale storage capacity from gigabytes to petabytes as files are added or removed
- **Concurrent Access**: Support thousands of concurrent connections from EC2, ECS, EKS, Lambda, and on-premises clients
- **Tagging Support**: Comprehensive tagging for resource organization, cost allocation, and compliance tracking
- **CloudWatch Integration**: Native integration with CloudWatch for monitoring file system metrics and performance
- **VPC Integration**: Deploy mount targets within VPCs with subnet-level placement control

## Main Use Cases

1. **Container Persistent Storage**: Provide persistent volumes for ECS and EKS containers requiring shared storage across pods
2. **Content Management Systems**: Store and share web content, media files, and documents across multiple web servers
3. **Development Environments**: Share source code, build artifacts, and development tools across development teams
4. **Big Data Analytics**: Store and process large datasets for Hadoop, Spark, and other analytics frameworks
5. **Machine Learning**: Store training datasets and model artifacts accessible by multiple training instances
6. **Media Processing**: Share video and image files for transcoding, rendering, and processing workflows
7. **Home Directories**: Provide network home directories for users across multiple Linux instances
8. **Application Migration**: Lift-and-shift on-premises applications requiring shared file storage to AWS
9. **Backup and Archive**: Store database backups, log files, and archival data with lifecycle policies
10. **Kubernetes Persistent Volumes**: Serve as ReadWriteMany (RWX) storage class for Kubernetes workloads

## Best Practices

### File System Configuration

1. **Enable Encryption by Default**: Always enable at-rest encryption for production file systems to protect sensitive data
2. **Use Customer-Managed KMS Keys**: For compliance requirements, use customer-managed KMS keys instead of AWS-managed keys
3. **Choose Appropriate Performance Mode**: Use General Purpose for most workloads; reserve Max I/O for massively parallel applications (1000+ instances)
4. **Start with Elastic Throughput**: Use Elastic throughput mode for unpredictable or variable workloads; it automatically scales with demand
5. **Use Provisioned Throughput Sparingly**: Only use Provisioned mode when you need consistent high throughput exceeding bursting limits
6. **Deploy Multi-AZ for Production**: Create mount targets in at least two availability zones for high availability
7. **Consider One Zone for Dev/Test**: Use One Zone storage class for non-production environments to reduce costs
8. **Name File Systems Descriptively**: Use clear naming conventions indicating environment, application, and purpose

### Access Control and Security

1. **Use Access Points**: Create dedicated access points for each application or tenant to enforce consistent POSIX permissions
2. **Enforce Least Privilege**: Configure access point POSIX users with minimum necessary permissions (non-root when possible)
3. **Implement File System Policies**: Use IAM-based file system policies to restrict access to specific AWS principals
4. **Deny Insecure Transport**: Configure file system policies to deny mounting without TLS encryption for sensitive data
5. **Restrict Security Groups**: Limit NFS port (2049) access to only known security groups or IP ranges
6. **Use VPC Endpoints**: Keep traffic within AWS network by accessing EFS through VPC endpoints
7. **Avoid Root Access Points**: Create access points with non-root POSIX users unless root access is specifically required
8. **Implement Defense in Depth**: Combine security groups, file system policies, and access point permissions for layered security
9. **Audit Mount Access**: Enable CloudTrail logging to monitor file system mount and policy changes
10. **Use IAM Roles**: Grant access through IAM roles rather than IAM users for applications and services

### Performance Optimization

1. **Optimize for Throughput**: For large file workloads, use larger I/O sizes (1 MB) to maximize throughput
2. **Parallelize Access**: Distribute file operations across multiple threads or instances to leverage EFS scalability
3. **Monitor Burst Credits**: Track burst credit balance in CloudWatch and switch to Provisioned mode if consistently depleted
4. **Use Regional Storage**: Deploy Standard storage class (multi-AZ) for frequently accessed data requiring high availability
5. **Implement Client-Side Caching**: Use operating system caching and attribute caching to reduce latency
6. **Pre-warm File System**: For predictable workloads, pre-warm the file system by reading data before peak usage
7. **Benchmark Performance**: Test performance with your specific workload patterns before production deployment
8. **Avoid Small File Workloads**: EFS is optimized for larger files; consider alternatives (S3, EBS) for many small files

### Lifecycle and Cost Management

1. **Enable Lifecycle Policies**: Automatically transition infrequently accessed files to IA storage to reduce costs by up to 92%
2. **Choose Appropriate Transition Period**: Start with 30 days for transition to IA; adjust based on access patterns
3. **Monitor Storage Classes**: Track distribution of data across Standard and IA storage classes using CloudWatch
4. **Clean Up Unused Data**: Regularly audit and delete unnecessary files to optimize storage costs
5. **Use One Zone for Dev/Test**: Deploy development and testing file systems in One Zone to save up to 47% on storage costs
6. **Implement Data Retention Policies**: Define and enforce data retention policies to prevent unlimited storage growth
7. **Track Throughput Costs**: Monitor Provisioned throughput usage to ensure you're not over-provisioned
8. **Review Elastic Throughput Charges**: For Elastic mode, review throughput billing to understand actual usage patterns

### Backup and Disaster Recovery

1. **Enable AWS Backup**: Use AWS Backup for automated, centralized backup management across file systems
2. **Configure Backup Schedules**: Implement daily or weekly backup schedules based on RPO requirements
3. **Set Retention Policies**: Define appropriate backup retention periods based on compliance and recovery needs
4. **Enable Cross-Region Replication**: Replicate critical file systems to secondary regions for disaster recovery
5. **Test Recovery Procedures**: Regularly test file system restoration from backups to validate RTO
6. **Monitor Replication Status**: Set up alarms for replication lag or failures
7. **Document Recovery Runbooks**: Maintain clear procedures for restoring file systems in disaster scenarios
8. **Use Multiple Backup Strategies**: Combine AWS Backup with application-level backups for defense in depth

### Mount Configuration

1. **Use EFS Mount Helper**: Utilize the amazon-efs-utils package and EFS mount helper for simplified mounting
2. **Enable Automatic Mounting**: Add EFS mounts to /etc/fstab for automatic mounting on instance startup
3. **Use TLS for In-Transit Encryption**: Mount with TLS option (efs-utils) when security requirements mandate in-transit encryption
4. **Configure Mount Options**: Set appropriate NFS mount options (rsize, wsize, timeo, retrans) for your workload
5. **Implement Health Checks**: Monitor mount availability and implement automatic remounting on failures
6. **Use DNS Names**: Mount using EFS DNS names for automatic failover across availability zones
7. **Test Cross-AZ Failover**: Validate that applications can fail over to mount targets in different AZs

### Monitoring and Observability

1. **Enable CloudWatch Metrics**: Monitor key metrics including ClientConnections, DataReadIOBytes, DataWriteIOBytes, and PercentIOLimit
2. **Set Up Burst Credit Alarms**: Alert when burst credits fall below thresholds to avoid performance degradation
3. **Monitor Throughput Utilization**: Track permitted throughput vs. metered throughput to optimize configuration
4. **Track Storage Size**: Monitor file system size growth to predict costs and capacity planning
5. **Alert on Mount Failures**: Create EventBridge rules to alert on failed mount attempts
6. **Dashboard Key Metrics**: Build CloudWatch dashboards showing performance, storage, and access patterns
7. **Log File System Events**: Enable CloudTrail logging for security auditing and compliance
8. **Monitor Access Point Usage**: Track metrics per access point to identify high-usage applications

### Application Integration

1. **Use Consistent Region**: Ensure file system and accessing resources are in the same AWS region
2. **Implement Retry Logic**: Handle transient NFS errors gracefully with exponential backoff retry logic
3. **Use Kubernetes CSI Driver**: Deploy AWS EFS CSI driver for Kubernetes persistent volume integration
4. **Configure Resource Limits**: Set appropriate storage quotas and limits for each access point or application
5. **Test Concurrent Access**: Validate application behavior with multiple simultaneous connections
6. **Handle File Locking**: Implement proper NFS file locking for applications requiring exclusive access
7. **Optimize for Workload**: Choose between throughput modes based on whether workload is read-heavy, write-heavy, or balanced

### Compliance and Governance

1. **Tag Comprehensively**: Apply tags for owner, environment, compliance scope, data classification, and cost center
2. **Implement Encryption**: Enable encryption for all file systems storing regulated data (PII, PHI, PCI)
3. **Document Data Classification**: Clearly document what types of data are stored on each file system
4. **Enable Audit Logging**: Use CloudTrail and VPC Flow Logs to maintain audit trails for compliance
5. **Implement Lifecycle Policies**: Configure retention policies to meet regulatory requirements
6. **Review Access Regularly**: Audit file system policies and access point configurations quarterly
7. **Maintain Compliance Reports**: Include EFS configuration in SOC2, ISO 27001, and other compliance reports

### Development and Deployment

1. **Use Infrastructure as Code**: Manage all EFS resources through Terraform for consistency and version control
2. **Separate Environments**: Create separate file systems for dev, staging, and production environments
3. **Test Performance First**: Validate performance with representative workloads in staging before production
4. **Document Mount Instructions**: Maintain clear documentation for mounting and accessing file systems
5. **Version Pin Module**: Pin Terraform module version to prevent unexpected changes during deployments
6. **Use Terraform Workspaces**: Leverage workspaces or separate state files for multi-environment deployments
7. **Implement Gradual Rollouts**: Test changes in non-production before applying to production file systems
8. **Automate Provisioning**: Include EFS provisioning in application deployment automation

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-efs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/efs/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-efs/tree/master/examples
- **AWS EFS Documentation**: https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html
- **AWS EFS API Reference**: https://docs.aws.amazon.com/efs/latest/APIReference/Welcome.html
- **EFS Performance**: https://docs.aws.amazon.com/efs/latest/ug/performance.html
- **EFS Storage Classes**: https://docs.aws.amazon.com/efs/latest/ug/storage-classes.html
- **EFS Access Points**: https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html
- **EFS Encryption**: https://docs.aws.amazon.com/efs/latest/ug/encryption.html
- **EFS Replication**: https://docs.aws.amazon.com/efs/latest/ug/efs-replication.html
- **EFS Best Practices**: https://docs.aws.amazon.com/efs/latest/ug/best-practices.html
- **EFS Security**: https://docs.aws.amazon.com/efs/latest/ug/security-considerations.html
- **EFS Pricing**: https://aws.amazon.com/efs/pricing/
- **EFS CSI Driver for Kubernetes**: https://docs.aws.amazon.com/eks/latest/userguide/efs-csi.html
- **EFS Mount Helper**: https://docs.aws.amazon.com/efs/latest/ug/efs-mount-helper.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Enable Encryption**: Always set `encrypted = true` and use customer-managed KMS keys for production
2. **Deploy Multi-AZ**: Configure mount targets in multiple availability zones for high availability
3. **Use Access Points**: Create access points with specific POSIX users rather than relying on root access
4. **Choose Performance Mode**: Use General Purpose for most workloads; Max I/O only for massively parallel applications
5. **Start with Elastic Throughput**: Use Elastic throughput mode unless you have specific provisioned throughput requirements
6. **Enable Lifecycle Policies**: Configure transition to IA storage after 30-90 days to optimize costs
7. **Implement Security Groups**: Restrict NFS port (2049) to only necessary security groups or IP ranges
8. **Enable Backup Policies**: Use AWS Backup for automated backup management
9. **Tag Comprehensively**: Apply tags for owner, environment, application, and cost tracking
10. **Monitor Performance**: Set up CloudWatch alarms for burst credits, throughput, and storage capacity
11. **Use File System Policies**: Implement IAM-based policies to restrict access to authorized principals only
12. **Document Access Patterns**: Maintain clear documentation of which applications use each file system and access point
