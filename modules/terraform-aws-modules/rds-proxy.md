# Terraform AWS RDS Proxy Module

## Module Information

- **Module Name**: `rds-proxy`
- **Source**: `terraform-aws-modules/rds-proxy/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds-proxy
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds-proxy/aws/latest
- **Latest Version**: 4.1.0
- **Purpose**: Terraform module that creates and manages AWS RDS Proxy resources for efficient database connection pooling and management
- **Service**: AWS RDS Proxy (Amazon RDS Proxy)
- **Category**: Database, Connection Management, Scalability
- **Keywords**: rds-proxy, aws-rds-proxy, database-proxy, connection-pooling, connection-management, rds, aurora, mysql, postgresql, database-scaling, secrets-manager, iam-authentication, database-authentication, connection-reuse, serverless-database, lambda-rds, database-failover, high-availability, connection-throttling, credential-management, tls-encryption, database-security, connection-limits, session-pinning, read-write-endpoint, read-only-endpoint, proxy-endpoint, cloudwatch-logs, database-monitoring, sql-logging, connection-timeout, idle-connections, max-connections, vpc-security, security-groups, subnet-groups, kms-encryption, iam-role, iam-policy, database-resilience, traffic-management, connection-efficiency, database-performance, cpu-optimization, memory-optimization, application-scaling, microservices-database, container-database, kubernetes-database, ecs-database, fargate-database, connection-overhead, query-performance, database-bottleneck, connection-storm, serverless-aurora, database-credentials, secret-rotation, cross-az, multi-az
- **Use For**: Lambda database connections, serverless application databases, connection pooling for microservices, containerized application databases, high-traffic database access, unpredictable database workloads, database failover automation, credential rotation without downtime, ECS/Fargate database connections, Kubernetes database access, connection storm prevention, database CPU optimization

## Description

AWS RDS Proxy is a fully managed database proxy service that sits between applications and relational databases, providing intelligent connection pooling, credential management, and enhanced database resilience. This Terraform module simplifies the deployment and configuration of RDS Proxy resources, including the proxy itself, authentication configurations, target groups, IAM roles and policies, CloudWatch log groups, and multiple proxy endpoints. The module supports both MySQL and PostgreSQL engine families and works seamlessly with Amazon RDS databases and Aurora clusters, enabling applications to efficiently share and reuse database connections rather than opening new connections for every request.

The module addresses critical challenges in modern application architectures, particularly for serverless and containerized workloads where applications can quickly open thousands of database connections, overwhelming database resources and causing performance degradation. By pooling and reusing connections, RDS Proxy significantly reduces the CPU and memory overhead associated with connection establishment, allowing databases to dedicate more resources to processing queries. The proxy automatically handles authentication using credentials stored in AWS Secrets Manager, supports IAM database authentication for enhanced security, and maintains connections to standby database instances, providing automatic failover capabilities without application code changes.

Built for production environments, the module provides comprehensive configuration options including connection borrow timeouts, maximum and idle connection percentages, session pinning filters for connection-sensitive operations, and TLS encryption enforcement for all connections. It supports multiple proxy endpoints (read-write and read-only) for separating workload types, integrates with CloudWatch for logging and monitoring, and enables fine-grained IAM permissions for proxy management and database access. The module automatically creates necessary IAM roles with appropriate policies for accessing Secrets Manager and KMS, handles VPC subnet and security group configurations, and provides extensive tagging capabilities for resource organization and cost tracking. With support for up to 200 Secrets Manager secrets per proxy and the ability to serve thousands of concurrent application connections, this module is essential for building scalable, resilient, and secure database connectivity layers in AWS.

## Key Features

- **Connection Pooling**: Efficiently pool and reuse database connections to reduce CPU and memory overhead
- **MySQL and PostgreSQL Support**: Full support for both MySQL and PostgreSQL engine families
- **Aurora and RDS Compatibility**: Works with Aurora clusters and standalone RDS instances
- **AWS Secrets Manager Integration**: Automatically retrieves database credentials from Secrets Manager
- **IAM Database Authentication**: Support for IAM-based database authentication for passwordless access
- **Multiple Authentication Methods**: Configure multiple authentication schemes for different database users
- **Read-Write Endpoints**: Create read-write proxy endpoints for write operations and failover scenarios
- **Read-Only Endpoints**: Establish read-only endpoints for distributing read traffic across read replicas
- **Connection Throttling**: Queue or throttle application connections when connection pool is full
- **Automatic Failover**: Seamlessly redirect connections to standby instances during database failures
- **Session Pinning Prevention**: Configure filters to avoid connection pinning that reduces pooling efficiency
- **TLS Encryption Required**: Enforce TLS encryption for all client connections to the proxy
- **Configurable Connection Timeouts**: Set connection borrow timeout to control how long clients wait for connections
- **Connection Limit Controls**: Configure maximum and idle connection percentages for optimal resource utilization
- **CloudWatch Logs Integration**: Send proxy logs to CloudWatch for monitoring and troubleshooting
- **Debug Logging**: Optional SQL statement logging for detailed debugging
- **Log Encryption**: Support for KMS-encrypted CloudWatch log groups
- **IAM Role Automation**: Automatically create and configure IAM roles with appropriate permissions
- **Secrets Manager Policy**: Generate IAM policies for retrieving database credentials from Secrets Manager
- **KMS Decryption Policy**: Create policies for decrypting secrets encrypted with customer-managed KMS keys
- **VPC Subnet Configuration**: Deploy proxy in specific VPC subnets across availability zones
- **Security Group Management**: Configure security groups to control network access to the proxy
- **Multi-AZ Deployment**: Automatically deployed across multiple availability zones for high availability
- **Resource Tagging**: Comprehensive tagging support for all created resources
- **Conditional Creation**: Flexible resource creation flags for modular deployments

## Main Use Cases

1. **Serverless Database Connections**: Optimize database connections for AWS Lambda functions that frequently scale up and down
2. **Containerized Applications**: Manage database connections for ECS, Fargate, and Kubernetes workloads with unpredictable scaling
3. **Microservices Architecture**: Provide efficient connection pooling for dozens of microservices accessing shared databases
4. **Connection Storm Prevention**: Prevent database overload during traffic spikes by throttling and queuing connections
5. **High-Availability Applications**: Automatically handle database failovers without application code changes
6. **Credential Rotation**: Rotate database credentials using Secrets Manager without application downtime
7. **Multi-Tenant Applications**: Share connection pools across tenants while maintaining authentication boundaries
8. **Database Performance Optimization**: Reduce database CPU and memory usage by minimizing connection overhead
9. **IAM-Authenticated Access**: Enable passwordless database access using IAM authentication for enhanced security
10. **Read Workload Distribution**: Distribute read queries across Aurora read replicas using read-only endpoints

## Best Practices

### Connection Pool Configuration

1. **Optimize Connection Limits**: Set `max_connections_percent` based on database instance connection limits (typically 80-90%)
2. **Configure Idle Connections**: Set `max_idle_connections_percent` to 50% to maintain warm connections for bursts
3. **Tune Borrow Timeout**: Use 30-120 second `connection_borrow_timeout` based on application timeout requirements
4. **Minimize Session Pinning**: Avoid operations that pin connections (temp tables, prepared statements, session variables)
5. **Use Appropriate Filters**: Configure `session_pinning_filters` to prevent unnecessary pinning patterns
6. **Monitor Connection Usage**: Track `DatabaseConnectionsCurrentlyInUse` metric to optimize pool sizing
7. **Scale With Traffic**: Adjust connection percentages based on observed application connection patterns

### Authentication and Security

1. **Use Secrets Manager**: Always store database credentials in AWS Secrets Manager for secure credential management
2. **Enable Automatic Rotation**: Configure Secrets Manager secret rotation for regular credential updates
3. **Prefer IAM Authentication**: Use IAM database authentication when possible for passwordless, temporary credentials
4. **Require TLS**: Always set `require_tls = true` to enforce encrypted connections
5. **KMS Encryption**: Use customer-managed KMS keys for encrypting Secrets Manager secrets in compliance scenarios
6. **Least Privilege IAM**: Grant minimum necessary IAM permissions for proxy access and secret retrieval
7. **Unique Secrets per User**: Create separate Secrets Manager secrets for each database user for granular credential management
8. **Security Group Restrictions**: Configure security groups to allow proxy access only from application security groups
9. **VPC Endpoint**: Use VPC endpoints for Secrets Manager to keep secret retrieval traffic within AWS network
10. **Audit Secret Access**: Enable CloudTrail logging for Secrets Manager to audit credential retrieval

### Endpoint Configuration

1. **Separate Read and Write**: Create separate read-write and read-only endpoints for workload isolation
2. **Read-Only for Scaling**: Use read-only endpoints to distribute read traffic across Aurora read replicas
3. **Target Group Association**: Ensure proxy target groups correctly reference Aurora cluster or RDS instance
4. **Endpoint Naming**: Use descriptive endpoint names indicating purpose (e.g., "app-db-write", "app-db-read")
5. **DNS Resolution**: Use proxy endpoint DNS names in application connection strings for automatic failover
6. **Connection String Updates**: Update application connection strings to point to proxy endpoints instead of database endpoints
7. **Test Failover**: Regularly test automatic failover behavior by promoting Aurora read replicas

### Performance and Optimization

1. **Maximize Connection Reuse**: Design applications to close connections quickly to return them to the pool
2. **Avoid Long Transactions**: Keep transactions short to prevent connection holding and improve pool turnover
3. **Monitor Pinning**: Track `ClientConnectionsSetupFailedBorrowTimeout` to identify session pinning issues
4. **Right-Size Pool**: Start with conservative connection limits and increase based on monitoring
5. **Use Connection Multiplexing**: Leverage RDS Proxy's ability to multiplex many application connections to fewer database connections
6. **Reduce Connection Overhead**: Measure database CPU reduction after enabling proxy (typically 20-40% improvement)
7. **Query Performance**: Expect minimal latency overhead from proxy (typically <5ms)
8. **Cold Start Mitigation**: For Lambda, proxy reduces cold start impact by maintaining warm database connections

### Logging and Monitoring

1. **Enable CloudWatch Logs**: Always enable logging for troubleshooting connection issues
2. **Log Retention Strategy**: Set appropriate retention periods (7-30 days typical) to balance cost and troubleshooting needs
3. **Debug Logging Initially**: Enable debug logging during initial deployment to capture SQL statements for troubleshooting
4. **Disable Debug in Production**: Turn off debug logging in production to reduce costs and avoid logging sensitive query data
5. **Key Metrics to Monitor**:
   - `DatabaseConnections`: Total connections proxy maintains to database
   - `ClientConnections`: Number of application connections to proxy
   - `QueryDatabaseResponseLatency`: Database query response time
   - `ClientConnectionsSetupFailedBorrowTimeout`: Failed connection attempts due to pool exhaustion
6. **Set Up Alarms**: Create CloudWatch alarms for connection pool exhaustion and high borrow timeouts
7. **Dashboard Creation**: Build dashboards showing connection pool utilization and performance metrics

### High Availability and Resilience

1. **Multi-AZ Deployment**: RDS Proxy automatically deploys across multiple AZs; ensure database does the same
2. **Aurora for Best HA**: Use Aurora clusters for fastest failover times (typically 30-60 seconds)
3. **Test Failover Regularly**: Perform quarterly failover tests to validate application behavior
4. **Connection Retry Logic**: Implement exponential backoff retry logic in applications for transient errors
5. **Health Checks**: Configure application health checks to detect proxy connectivity issues
6. **Monitor Failover Events**: Track `DatabaseConnectionRequests` metric during failovers to observe connection patterns
7. **Document Recovery Procedures**: Maintain runbooks for RDS Proxy issues and database failover scenarios

### Cost Optimization

1. **Right-Size Connection Pool**: Avoid over-provisioning; monitor actual connection usage before scaling
2. **Evaluate ROI**: RDS Proxy is most cost-effective for applications with >100 concurrent connections
3. **CloudWatch Log Costs**: Set appropriate log retention and disable debug logging to control costs
4. **Proxy vs Database Scaling**: In some cases, scaling database instance may be more cost-effective than proxy
5. **Usage-Based Pricing**: Understand that proxy charges are based on vCPU hours of underlying database
6. **Multi-Tenant Sharing**: Share single proxy across multiple applications to amortize costs
7. **Monitor Unused Proxies**: Regularly audit and remove proxies that are no longer actively used

### Application Integration

1. **Connection String Changes**: Update application database connection strings to use proxy endpoint
2. **Connection Pooling Compatibility**: Disable or minimize application-level connection pooling when using RDS Proxy
3. **Framework Configuration**: Configure ORMs (Hibernate, Entity Framework) to work efficiently with proxy
4. **Lambda Best Practices**: Set appropriate Lambda timeout values accounting for connection borrow timeout
5. **Container Configuration**: Configure container connection limits based on proxy connection pool capacity
6. **Kubernetes Integration**: Use Kubernetes secrets to store proxy connection strings
7. **Health Check Endpoints**: Implement application health checks that validate proxy connectivity

### Deployment and Operations

1. **Infrastructure as Code**: Manage all RDS Proxy resources through Terraform for consistency
2. **Staged Rollouts**: Deploy proxy in non-production environments first to validate configuration
3. **Blue-Green Deployment**: Use separate proxies for blue-green database migrations
4. **Change Management**: Require approval for production proxy configuration changes
5. **Version Control**: Store proxy configurations in Git for change tracking and rollback
6. **Tag Consistently**: Apply tags for environment, application, cost-center, and database-name
7. **Module Version Pinning**: Pin module version in production: `version = "~> 4.1"` for stability
8. **Backup Configuration**: Export and document proxy configurations for disaster recovery
9. **Migration Planning**: Plan careful migration from direct database connections to proxy
10. **Rollback Strategy**: Maintain ability to quickly revert to direct database connections if issues arise

### Secrets Manager Integration

1. **Secret Format**: Use correct JSON format for database credentials in Secrets Manager secrets
2. **Required Fields**: Ensure secrets contain required fields: username, password, engine, host, port, dbname
3. **Secret Naming**: Use consistent naming convention for secrets (e.g., "rds/production/myapp")
4. **IAM Permissions**: Verify proxy IAM role has `secretsmanager:GetSecretValue` permission
5. **KMS Key Access**: If using customer-managed KMS keys, grant proxy IAM role `kms:Decrypt` permission
6. **Secret Rotation**: Test secret rotation with proxy to ensure seamless credential updates
7. **Multiple Secrets**: Use separate secrets for different database users accessing through same proxy
8. **Cross-Account Secrets**: When using cross-account secrets, configure appropriate resource policies

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-rds-proxy
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/rds-proxy/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-rds-proxy/tree/master/examples
- **AWS RDS Proxy Documentation**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html
- **RDS Proxy API Reference**: https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_Operations_RDS_Proxy.html
- **Managing RDS Proxy**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-managing.html
- **Secrets Manager Integration**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-setup.html
- **IAM Database Authentication**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.html
- **Connection Pooling**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.howitworks.html
- **Best Practices**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-best-practices.html
- **Monitoring RDS Proxy**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-monitoring.html
- **RDS Proxy Pricing**: https://aws.amazon.com/rds/proxy/pricing/
- **Lambda with RDS Proxy**: https://aws.amazon.com/blogs/compute/using-amazon-rds-proxy-with-aws-lambda/
- **Troubleshooting**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-troubleshooting.html
- **Session Pinning**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-pinning.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Engine Family Selection**: Set `engine_family` to "MYSQL" or "POSTGRESQL" matching your database engine
2. **Secrets Manager Setup**: Ensure database credentials exist in Secrets Manager before creating proxy
3. **Secret ARN Format**: Provide complete secret ARN in authentication configuration
4. **VPC Subnet IDs**: Specify at least two subnet IDs in different availability zones
5. **Security Groups**: Create security groups allowing proxy access from application security groups
6. **Target RDS/Aurora**: Specify target database cluster or instance identifier in target group configuration
7. **Connection Pool Sizing**: Start with `max_connections_percent = 90` and `max_idle_connections_percent = 50`
8. **TLS Requirement**: Always set `require_tls = true` for production environments
9. **CloudWatch Logging**: Enable logging with appropriate retention for troubleshooting
10. **IAM Role Creation**: Module automatically creates IAM role; provide `role_arn` if using existing role
11. **Multiple Endpoints**: Create read-only endpoints for Aurora clusters with read replicas
12. **Session Pinning**: Configure `session_pinning_filters` to prevent unnecessary connection pinning
13. **Tagging Strategy**: Apply comprehensive tags for environment, application, and database identification
14. **Monitoring Setup**: Create CloudWatch alarms for connection pool exhaustion and high latency
15. **Testing**: Validate connectivity through proxy after deployment before switching application traffic
