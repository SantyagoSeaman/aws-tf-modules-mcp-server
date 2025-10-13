# Terraform AWS RDS Aurora Module

## Module Information

- **Module Name**: `rds-aurora`
- **Source**: `terraform-aws-modules/rds-aurora/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds-aurora
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds-aurora/aws/latest
- **Latest Version**: 9.16.0
- **Purpose**: Terraform module for creating and managing AWS RDS Aurora database clusters with extensive configuration options
- **Service**: AWS RDS Aurora (Amazon Relational Database Service - Aurora)
- **Category**: Database, Managed Services, Cloud Infrastructure
- **Keywords**: aurora, rds, database, postgresql, mysql, serverless, global-cluster, autoscaling, multi-az, limitless, dsql, read-replica, cluster, relational-database, aws-aurora, aurora-postgresql, aurora-mysql, db-cluster, database-cluster, managed-database, cloud-database, aurora-serverless, serverless-v2, enhanced-monitoring, performance-insights, s3-import, backup, encryption, kms, snapshot, failover, high-availability, disaster-recovery, cross-region, replication, endpoint, custom-endpoint, scaling, capacity, monitoring, cloudwatch, iam-authentication, security-group, subnet-group, parameter-group, cluster-parameter-group, db-instance, writer-endpoint, reader-endpoint
- **Use For**: Production relational databases, multi-region database deployments, serverless database workloads, auto-scaling database clusters, high-availability database systems, disaster recovery setups, global database applications, microservices data persistence, application backend databases, read-heavy workloads with replica scaling, cost-optimized serverless databases, enterprise database consolidation

## Description

This Terraform module provides a comprehensive solution for deploying and managing Amazon Aurora database clusters on AWS. Aurora is a MySQL and PostgreSQL-compatible relational database built for the cloud, combining the performance and availability of enterprise databases with the simplicity and cost-effectiveness of open-source databases. The module abstracts the complexity of Aurora cluster configuration, supporting both provisioned and serverless deployment modes, multiple database engines (Aurora PostgreSQL and Aurora MySQL), and advanced features like global clusters, read replica autoscaling, and custom endpoints.

The module enables flexible cluster architectures ranging from simple single-region deployments to sophisticated multi-region global databases with automatic failover capabilities. It supports Aurora Serverless v1 and v2 for variable workloads that require automatic scaling based on demand, as well as Aurora Limitless for horizontally scalable databases. Features like enhanced monitoring, Performance Insights, S3 data import, and integration with AWS services such as CloudWatch, KMS, and IAM provide enterprise-grade database management capabilities. The module also supports Aurora DSQL (Distributed SQL) clusters for distributed database workloads across multiple regions.

Built with production readiness in mind, this module includes comprehensive options for security (encryption at rest and in transit, IAM authentication, network isolation), high availability (Multi-AZ deployments, automated backups, point-in-time recovery), and operational excellence (configurable monitoring intervals, CloudWatch log exports, automated minor version upgrades). The module follows Terraform best practices with clear input variables, comprehensive outputs, and conditional resource creation, making it suitable for both development environments and production-grade database deployments.

## Key Features

- **Multiple Database Engines**: Support for Aurora PostgreSQL and Aurora MySQL with configurable engine versions
- **Deployment Modes**: Provisioned clusters, Serverless v1, Serverless v2, and Aurora Limitless configurations
- **Global Clusters**: Multi-region database clusters with cross-region read replicas and automatic failover
- **Read Replica Autoscaling**: Automatic scaling of read replicas based on CPU utilization or custom metrics
- **Serverless Capabilities**: Aurora Serverless v1 and v2 with automatic capacity scaling for variable workloads
- **Aurora DSQL Support**: Distributed SQL clusters with multi-region capabilities via the dsql submodule
- **Aurora Limitless**: Horizontally scalable databases for massive throughput requirements
- **Enhanced Monitoring**: Integration with CloudWatch for detailed database performance metrics at 1-60 second intervals
- **Performance Insights**: Advanced database performance monitoring and query analysis
- **Custom Endpoints**: Create custom endpoint configurations for load balancing and workload isolation
- **S3 Import**: Direct data import from Amazon S3 buckets during cluster creation
- **Multi-AZ Deployments**: High availability with automatic failover across availability zones
- **Encryption**: Storage encryption using AWS KMS with customer-managed or AWS-managed keys
- **IAM Database Authentication**: Token-based authentication using AWS IAM credentials
- **Backup and Recovery**: Automated backups with configurable retention periods and point-in-time recovery
- **Snapshot Management**: Manual and automated snapshot creation with cross-region copy capabilities
- **CloudWatch Logs**: Export of audit logs, error logs, general logs, and slow query logs to CloudWatch
- **Security Groups**: Configurable security group rules for network access control
- **Subnet Groups**: Custom database subnet group configuration for VPC networking
- **Parameter Groups**: Cluster and instance-level parameter group customization
- **Tagging Support**: Comprehensive resource tagging for cost allocation and resource management
- **Deletion Protection**: Prevent accidental deletion of production database clusters
- **Blue/Green Deployments**: Support for zero-downtime database updates (Aurora PostgreSQL)
- **Conditional Resource Creation**: Flexible module configuration with create flags for all resources

## Main Use Cases

1. **Production Application Databases**: Highly available, scalable relational databases for web and mobile applications
2. **Multi-Region Applications**: Global database clusters with low-latency reads in multiple geographic regions
3. **Serverless Workloads**: Auto-scaling databases for development environments and intermittent workloads
4. **Read-Heavy Applications**: Auto-scaling read replicas for applications with high read-to-write ratios
5. **Enterprise Database Migration**: Moving on-premises MySQL or PostgreSQL databases to managed Aurora
6. **Microservices Architecture**: Individual Aurora clusters for service-specific data isolation
7. **Data Analytics**: Aurora as a source for business intelligence and analytics tools
8. **Disaster Recovery**: Cross-region replication and automated backup for business continuity
9. **Cost Optimization**: Serverless Aurora for variable workloads to reduce costs during idle periods
10. **High-Availability Systems**: Multi-AZ deployments with automatic failover for critical applications

## Submodules

### 1. dsql

- **Purpose**: Creates AWS Aurora DSQL (Distributed SQL) clusters with multi-region peering capabilities
- **Source**: `terraform-aws-modules/rds-aurora/aws//modules/dsql`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/rds-aurora/aws/latest/submodules/dsql
- **Key Features**: Multi-region cluster deployment, cluster peering configuration, KMS encryption support, deletion protection
- **Use Cases**: Distributed database workloads, multi-region data residency requirements, cross-region database peering, geographically distributed applications

## Submodule 1: dsql

### Description

The dsql submodule creates and manages Aurora DSQL (Distributed SQL) clusters, which provide distributed database capabilities across multiple AWS regions. This submodule enables the creation of individual DSQL clusters and supports cluster peering to connect multiple clusters for distributed workloads. It includes comprehensive configuration options for encryption, deletion protection, and witness region configuration for multi-region setups.

### Key Features

- Multi-region DSQL cluster deployment with configurable witness regions
- Cluster peering capabilities to connect multiple DSQL clusters
- KMS encryption support with customer-managed or AWS-managed keys
- Deletion protection to prevent accidental cluster deletion
- Flexible tagging for resource management and cost allocation
- VPC endpoint service integration for private connectivity
- Conditional resource creation with create flags

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether the DSQL cluster should be created |
| `witness_region` | `string` | `null` | AWS region to use as the witness region for the DSQL cluster |
| `create_cluster_peering` | `bool` | `false` | Determines whether to create cluster peering resources |
| `clusters` | `list(string)` | `[]` | List of DSQL cluster ARNs to peer with this cluster |
| `kms_encryption_key` | `string` | `null` | ARN of the KMS key for cluster encryption |
| `deletion_protection_enabled` | `bool` | `true` | Whether deletion protection is enabled for the cluster |
| `tags` | `map(string)` | `{}` | Map of tags to assign to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | The Amazon Resource Name (ARN) of the DSQL cluster |
| `identifier` | The unique identifier of the DSQL cluster |
| `encryption_details` | Details about the encryption configuration of the cluster |
| `vpc_endpoint_service_name` | The VPC endpoint service name for private connectivity |

### Usage Example

```hcl
# Create a primary DSQL cluster in us-east-1
module "dsql_cluster_primary" {
  source = "terraform-aws-modules/rds-aurora/aws//modules/dsql"

  witness_region               = "us-west-2"
  deletion_protection_enabled  = true

  # Optional: Use customer-managed KMS key for encryption
  kms_encryption_key = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"

  tags = {
    Environment = "production"
    Name        = "dsql-primary"
    Region      = "us-east-1"
  }
}

# Create a secondary DSQL cluster and peer it with the primary
module "dsql_cluster_secondary" {
  source = "terraform-aws-modules/rds-aurora/aws//modules/dsql"

  witness_region          = "eu-west-1"
  create_cluster_peering  = true
  clusters                = [module.dsql_cluster_primary.arn]

  deletion_protection_enabled = true

  tags = {
    Environment = "production"
    Name        = "dsql-secondary"
    Region      = "us-west-2"
  }
}
```

## Best Practices

### Cluster Architecture and Design

1. **Choose the Right Engine Mode**: Use provisioned mode for predictable workloads, Serverless v2 for variable workloads, and Serverless v1 for infrequent usage patterns
2. **Size Instances Appropriately**: Start with smaller instance classes and scale up based on performance metrics rather than over-provisioning
3. **Use Multi-AZ Deployments**: Always enable Multi-AZ for production workloads to ensure high availability and automatic failover
4. **Leverage Read Replicas**: Distribute read traffic across read replicas and enable autoscaling to handle variable read workloads
5. **Design for Failure**: Architect applications to handle database failover scenarios with connection retry logic and proper timeouts
6. **Separate Workloads**: Use custom endpoints to route different application workloads (analytics, reporting, OLTP) to specific instances
7. **Consider Global Clusters**: For globally distributed applications, use Aurora Global Database for low-latency reads in multiple regions

### Security and Compliance

1. **Enable Encryption at Rest**: Always set `storage_encrypted = true` and use customer-managed KMS keys for sensitive data
2. **Implement Network Isolation**: Deploy Aurora clusters in private subnets and use security groups to restrict access to authorized sources only
3. **Use IAM Database Authentication**: Enable IAM authentication for applications that support token-based authentication to avoid storing credentials
4. **Rotate Credentials Regularly**: Implement password rotation policies for database users and use AWS Secrets Manager for credential management
5. **Enable Deletion Protection**: Set deletion protection for production clusters to prevent accidental deletion
6. **Audit Database Activity**: Enable audit logging and export logs to CloudWatch for security monitoring and compliance
7. **Encrypt Connections**: Configure SSL/TLS for all client connections to encrypt data in transit
8. **Apply Least Privilege**: Grant only necessary database permissions to application users and use separate users for different applications
9. **Use Parameter Groups Carefully**: Review and customize parameter groups to disable unnecessary features and enforce security settings

### Backup and Disaster Recovery

1. **Configure Appropriate Retention**: Set backup retention periods based on recovery point objectives (RPO), typically 7-35 days for production
2. **Test Recovery Procedures**: Regularly test point-in-time recovery and snapshot restoration to verify backup integrity
3. **Enable Automated Backups**: Ensure automated backups are enabled and schedule them during low-activity periods
4. **Copy Snapshots Cross-Region**: For critical workloads, copy snapshots to a secondary region for disaster recovery
5. **Use Global Clusters for DR**: Implement Aurora Global Database for cross-region disaster recovery with sub-second RPO
6. **Tag Snapshots**: Apply meaningful tags to manual snapshots for easier management and lifecycle policies
7. **Document Recovery Procedures**: Maintain runbooks with step-by-step recovery procedures for various failure scenarios
8. **Monitor Backup Status**: Set up CloudWatch alarms to alert on backup failures or missing backups

### Performance Optimization

1. **Enable Performance Insights**: Activate Performance Insights to identify slow queries and performance bottlenecks
2. **Configure Enhanced Monitoring**: Set monitoring intervals to 1-60 seconds based on your troubleshooting needs
3. **Optimize Parameter Groups**: Tune cluster and instance parameters based on workload characteristics (OLTP vs. analytics)
4. **Use Query Caching**: Enable result caching for frequently executed queries to reduce database load
5. **Implement Connection Pooling**: Use connection pooling in applications to reduce connection overhead and improve scalability
6. **Monitor Query Performance**: Export slow query logs to CloudWatch and regularly review slow queries for optimization
7. **Scale Read Workloads**: Use read replicas and reader endpoints to offload read traffic from the primary instance
8. **Configure Autoscaling**: Set up read replica autoscaling with appropriate CPU thresholds and min/max replica counts
9. **Right-Size Instances**: Monitor CPU, memory, and I/O metrics to ensure instance classes match workload requirements

### Cost Optimization

1. **Use Serverless for Variable Workloads**: Choose Aurora Serverless v2 for development, testing, or infrequently accessed databases
2. **Right-Size Clusters**: Regularly review utilization metrics and downsize over-provisioned instances
3. **Optimize Backup Retention**: Balance retention requirements with storage costs; use shorter retention for non-critical environments
4. **Delete Unused Snapshots**: Implement lifecycle policies to delete old manual snapshots that are no longer needed
5. **Use Reserved Instances**: For predictable production workloads, purchase reserved instances for significant cost savings
6. **Monitor Data Transfer Costs**: Place applications in the same region and availability zone when possible to reduce data transfer costs
7. **Leverage Autoscaling**: Configure read replica autoscaling to scale down during low-traffic periods
8. **Optimize Cross-Region Replication**: Evaluate the necessity of global clusters and cross-region read replicas for cost vs. benefit
9. **Use Tags for Cost Allocation**: Apply consistent tags to track costs by application, environment, or business unit

### Operational Excellence

1. **Enable Auto Minor Version Upgrades**: Allow automatic minor version upgrades during maintenance windows for security patches
2. **Plan Major Upgrades Carefully**: Test major version upgrades in non-production environments before applying to production
3. **Configure Maintenance Windows**: Set maintenance windows during low-traffic periods to minimize impact
4. **Implement Comprehensive Tagging**: Use consistent tagging strategies for resource organization, cost tracking, and automation
5. **Monitor Key Metrics**: Set up CloudWatch alarms for CPU, memory, storage, connections, and replication lag
6. **Use CloudWatch Log Exports**: Export database logs (error, slow query, audit) to CloudWatch for centralized logging
7. **Document Cluster Configuration**: Maintain documentation of cluster architecture, networking, and configuration decisions
8. **Implement Change Management**: Use Infrastructure as Code (Terraform) for all database changes with proper code review
9. **Set Up Alerting**: Configure SNS topics and CloudWatch alarms for critical events like failover, high CPU, or storage thresholds
10. **Use DB Activity Streams**: Enable Database Activity Streams for real-time monitoring of database activity for compliance and security

### High Availability and Reliability

1. **Deploy Across Multiple AZs**: Always deploy Aurora clusters across at least two availability zones for fault tolerance
2. **Test Failover Scenarios**: Regularly test failover procedures by manually triggering failovers during maintenance windows
3. **Monitor Replication Lag**: Set up alarms for replica lag to detect replication issues before they impact availability
4. **Use Health Checks**: Implement application-level health checks that verify database connectivity and query execution
5. **Configure Appropriate Timeouts**: Set connection and query timeouts in applications to handle transient failures gracefully
6. **Plan for Capacity**: Monitor growth trends and plan for capacity increases before hitting limits
7. **Implement Circuit Breakers**: Use circuit breaker patterns in applications to prevent cascading failures during database issues

### Development and Deployment

1. **Use Terraform State Management**: Store Terraform state in S3 with DynamoDB locking for team collaboration
2. **Version Control Configuration**: Keep all Terraform configurations in version control with proper branching strategies
3. **Separate Environments**: Use separate Aurora clusters for development, staging, and production environments
4. **Parameterize Configurations**: Use Terraform variables and separate tfvars files for environment-specific configurations
5. **Apply Changes Incrementally**: Make small, incremental changes and test thoroughly before applying to production
6. **Use Terraform Plan**: Always review terraform plan output before applying changes to production clusters
7. **Implement Pre-Production Testing**: Test all changes in staging environments that mirror production configuration
8. **Automate with CI/CD**: Integrate Terraform deployments into CI/CD pipelines with proper approval gates for production

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds-aurora
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds-aurora/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-rds-aurora/tree/master/examples
- **AWS Aurora User Guide**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/
- **AWS Aurora PostgreSQL**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.AuroraPostgreSQL.html
- **AWS Aurora MySQL**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.AuroraMySQL.html
- **Aurora Serverless v2**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html
- **Aurora Global Database**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html
- **Performance Insights**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_PerfInsights.html
- **Aurora Best Practices**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.BestPractices.html
- **RDS Aurora Pricing**: https://aws.amazon.com/rds/aurora/pricing/
- **Aurora Security**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.html
- **IAM Database Authentication**: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.IAMDBAuth.html
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

## Notes for AI Agents

When using this module in automated workflows:

1. **Security First**: Always enable encryption at rest and in transit, use KMS customer-managed keys for production
2. **High Availability**: Enable Multi-AZ deployments for production workloads
3. **Network Isolation**: Deploy clusters in private subnets with restrictive security groups
4. **Backup Strategy**: Configure appropriate backup retention periods based on RPO requirements
5. **Monitoring**: Enable enhanced monitoring and Performance Insights for production clusters
6. **Credential Management**: Use AWS Secrets Manager for master password storage, never hardcode credentials
7. **Tagging**: Apply consistent tags for cost allocation, environment identification, and resource management
8. **Autoscaling**: Configure read replica autoscaling for variable read workloads
9. **Engine Selection**: Choose Aurora PostgreSQL for advanced features and compliance, Aurora MySQL for MySQL compatibility
10. **Serverless Considerations**: Use Serverless v2 for modern workloads, Serverless v1 for legacy applications
11. **Global Clusters**: For multi-region applications, evaluate Aurora Global Database for low-latency reads
12. **Cost Optimization**: Right-size instances, use autoscaling, and consider reserved instances for production
13. **Testing**: Always test major version upgrades and failover procedures in non-production environments first
14. **Documentation**: Document cluster architecture, networking decisions, and disaster recovery procedures
