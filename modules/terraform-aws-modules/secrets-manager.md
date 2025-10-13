# Terraform AWS Secrets Manager Module

## Module Information

- **Module Name**: `secrets-manager`
- **Source**: `terraform-aws-modules/secrets-manager/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-secrets-manager
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/secrets-manager/aws/latest
- **Latest Version**: 2.0.0
- **Purpose**: Terraform module that creates and manages AWS Secrets Manager secrets for secure storage and rotation of sensitive credentials and configuration data
- **Service**: AWS Secrets Manager
- **Category**: Security, Secrets Management, Credentials Management
- **Keywords**: secrets-manager, aws-secrets-manager, secret-management, password-management, credentials-storage, api-keys, database-credentials, secret-rotation, automatic-rotation, lambda-rotation, kms-encryption, encryption-at-rest, secret-versioning, secret-replication, multi-region, cross-region, resource-policy, iam-policy, secret-recovery, deletion-protection, recovery-window, random-password, password-generation, secret-string, binary-secret, replica-secret, secret-arn, version-staging, rotation-schedule, rotation-lambda, access-control, least-privilege, secrets-retrieval, application-secrets, configuration-secrets, environment-variables
- **Use For**: database password storage, API key management, application credentials, OAuth tokens, encryption keys, certificate storage, multi-region secret replication, automated password rotation, CI/CD secrets management, application configuration storage, third-party service credentials, disaster recovery secret backup

## Description

AWS Secrets Manager is a fully managed service that helps protect access to applications, services, and IT resources without the upfront cost and complexity of managing hardware security modules (HSMs). This Terraform module provides a comprehensive solution for creating, managing, and rotating secrets in AWS with support for encryption, cross-region replication, and fine-grained access control. The module simplifies the process of storing sensitive data like database credentials, API keys, OAuth tokens, and other secrets while maintaining security best practices and compliance requirements.

The module supports multiple secret management scenarios including text-based and binary secrets, automatic random password generation, and Lambda-based rotation for supported database engines and services. It enables configuration of KMS encryption using either AWS-managed keys or customer-managed keys for enhanced security control. The module provides flexible access control through resource policies with support for IAM principals, conditions, and least privilege principles. It also supports secret versioning, allowing applications to retrieve specific versions of secrets and enabling zero-downtime credential updates.

This module is essential for organizations implementing secure credential management practices, particularly those running applications on AWS services like ECS, EKS, Lambda, or EC2. It integrates seamlessly with AWS services and third-party applications that support Secrets Manager, enabling automated credential retrieval without hardcoding sensitive values in application code or configuration files. The module's support for cross-region replication ensures secrets are available for disaster recovery scenarios, while configurable recovery windows protect against accidental deletion. With comprehensive tagging, rotation scheduling, and policy-based access control, this module serves as the foundation for enterprise-grade secret management in AWS.

## Key Features

- **Text and Binary Secret Storage**: Store secrets as text strings (JSON, YAML, plain text) or binary data for flexibility
- **Random Password Generation**: Automatically generate secure random passwords with configurable length and character sets
- **KMS Encryption**: Encrypt secrets at rest using AWS-managed keys or customer-managed KMS keys for enhanced security
- **Secret Rotation**: Enable automatic secret rotation with Lambda functions for databases, services, and custom credentials
- **Rotation Scheduling**: Configure rotation frequency using rate expressions (hours, days) or cron expressions
- **Cross-Region Replication**: Replicate secrets to multiple AWS regions for disaster recovery and global application support
- **Region-Specific KMS Keys**: Use different KMS keys per replica region for compliance and security requirements
- **Resource Policies**: Define fine-grained access control using IAM policy statements with principals and conditions
- **Block Public Access**: Prevent secrets from being publicly accessible through policy misconfiguration
- **Secret Versioning**: Maintain multiple versions of secrets with staging labels for gradual rollout and rollback
- **Configurable Recovery Window**: Set deletion recovery period from 0 to 30 days to protect against accidental deletion
- **Immediate Deletion**: Force immediate secret deletion for testing environments (bypassing recovery window)
- **Name Prefix Support**: Generate unique secret names using prefixes for multi-environment deployments
- **Secret Metadata**: Add descriptions and tags to secrets for organization, documentation, and cost allocation
- **Ignore Changes**: Configure Terraform to ignore external secret value changes for manually managed secrets
- **Multiple Output Formats**: Access secret ARN, ID, name, value, and version information for integration
- **IAM Integration**: Seamless integration with IAM roles and policies for application access
- **Tagging Support**: Comprehensive tagging for resource organization, compliance tracking, and cost management
- **Conditional Creation**: Control secret creation with boolean flags for environment-specific deployments
- **Policy Version Management**: Automatically manage resource policy versions and updates

## Main Use Cases

1. **Database Credential Management**: Store and rotate database passwords for RDS, Aurora, and other database systems
2. **API Key Storage**: Securely store third-party service API keys and tokens for application integrations
3. **Application Configuration**: Store sensitive application configuration data and environment variables
4. **OAuth Token Management**: Manage OAuth tokens, refresh tokens, and authentication credentials
5. **Certificate Storage**: Store SSL/TLS certificates, private keys, and certificate chains
6. **CI/CD Pipeline Secrets**: Provide secrets to CI/CD tools and deployment pipelines without hardcoding
7. **Multi-Region Applications**: Replicate secrets across regions for globally distributed applications
8. **Microservices Credentials**: Manage service-to-service authentication credentials in microservices architectures
9. **Disaster Recovery**: Maintain encrypted backup copies of critical secrets in multiple regions
10. **Compliance and Auditing**: Track secret access and rotation for regulatory compliance (SOC2, HIPAA, PCI-DSS)

## Best Practices

### Secret Creation and Management

1. **Use Descriptive Names**: Name secrets clearly indicating their purpose, environment, and owner (e.g., "prod-rds-admin-password")
2. **Use Name Prefixes**: Leverage name prefixes for consistent naming across environments and avoid collisions
3. **Add Comprehensive Tags**: Tag secrets with owner, environment, application, cost-center, and compliance requirements
4. **Provide Descriptions**: Always include descriptions explaining the secret's purpose and usage
5. **Use JSON for Structured Secrets**: Store multiple related credentials in JSON format for easier management and retrieval
6. **Separate Secrets by Environment**: Maintain separate secrets for dev, staging, and production to prevent cross-environment access
7. **Version Control Configuration**: Store Terraform configurations for secrets (not values) in version control
8. **Document Secret Schemas**: Maintain documentation of JSON structures used in secrets for consistency

### Security and Encryption

1. **Enable KMS Encryption**: Always use KMS encryption; prefer customer-managed keys for sensitive production secrets
2. **Use Separate KMS Keys**: Create dedicated KMS keys for different applications or compliance boundaries
3. **Rotate KMS Keys**: Establish and follow KMS key rotation policies (annual or as required by compliance)
4. **Implement Least Privilege**: Configure resource policies granting minimum necessary access to secrets
5. **Block Public Policies**: Always set `block_public_policy = true` to prevent accidental public exposure
6. **Use IAM Conditions**: Add IAM condition keys (VPC, IP address, MFA) to resource policies for defense in depth
7. **Audit Secret Access**: Enable CloudTrail logging to monitor who accesses secrets and when
8. **Use VPC Endpoints**: Access Secrets Manager through VPC endpoints to keep traffic within AWS network
9. **Encrypt Replica Secrets**: Use region-specific KMS keys for replicated secrets to maintain encryption sovereignty
10. **Review Policies Regularly**: Audit resource policies quarterly to ensure they follow least privilege principles

### Secret Rotation

1. **Enable Rotation for Credentials**: Automatically rotate database passwords, API keys, and service credentials
2. **Use AWS Rotation Templates**: Leverage AWS-provided Lambda rotation functions for supported databases
3. **Test Rotation Logic**: Thoroughly test rotation Lambda functions in non-production environments first
4. **Set Appropriate Rotation Frequency**: Balance security (shorter intervals) with operational impact (longer intervals)
5. **Monitor Rotation Success**: Set up CloudWatch alarms for failed rotation attempts
6. **Implement Gradual Rollout**: Use secret version staging labels to gradually roll out rotated credentials
7. **Handle Rotation Failures**: Implement retry logic and alerting for rotation failures
8. **Rotate Immediately After Creation**: For new secrets, rotate immediately to establish baseline rotation schedule
9. **Document Rotation Process**: Maintain runbooks for manual rotation procedures and troubleshooting
10. **Grant Rotation Permissions**: Ensure Lambda rotation functions have necessary permissions to update target systems

### Replication and High Availability

1. **Replicate Critical Secrets**: Enable cross-region replication for secrets used by mission-critical applications
2. **Match Application Regions**: Replicate secrets to all regions where applications are deployed
3. **Use Region-Specific Endpoints**: Configure applications to retrieve secrets from local region replicas for lower latency
4. **Monitor Replication Lag**: Track replication status and set up alerts for replication failures
5. **Test Failover Scenarios**: Regularly test application failover using replicated secrets in secondary regions
6. **Document Replication Strategy**: Maintain clear documentation of which secrets are replicated and why
7. **Consider Replication Costs**: Balance availability needs with data transfer and storage costs

### Access Control and Integration

1. **Use IAM Roles**: Grant access to secrets via IAM roles for EC2, ECS, Lambda, and other services
2. **Implement Service-Specific Policies**: Create separate resource policies for different applications or services
3. **Use Condition Keys**: Restrict access based on source VPC, IP address, or tags using IAM conditions
4. **Grant Version-Specific Access**: When needed, grant access to specific secret versions rather than current version
5. **Cache Secrets Appropriately**: Implement client-side caching with TTL to reduce API calls and costs
6. **Retrieve Secrets at Runtime**: Fetch secrets during application startup or runtime, never embed in code or containers
7. **Use AWS SDKs**: Leverage AWS SDKs and Secrets Manager caching libraries for efficient secret retrieval
8. **Implement Circuit Breakers**: Handle Secrets Manager API failures gracefully with fallback mechanisms

### Deletion and Recovery

1. **Set Appropriate Recovery Windows**: Use 30-day recovery window for production secrets, shorter for non-production
2. **Never Use Immediate Deletion in Production**: Reserve `recovery_window_in_days = 0` for testing only
3. **Document Deletion Procedures**: Maintain clear procedures and approvals required for secret deletion
4. **Backup Before Deletion**: Export secret values to secure backup before marking for deletion
5. **Monitor Deletion Events**: Set up alerts for secret deletion events for security monitoring
6. **Review Dependents First**: Identify and update all applications using a secret before deletion
7. **Test Recovery Process**: Periodically test secret recovery procedures to ensure they work

### Monitoring and Observability

1. **Enable CloudTrail Logging**: Log all Secrets Manager API calls for security auditing and troubleshooting
2. **Set Up Access Alerts**: Create EventBridge rules to alert on secret access from unexpected sources
3. **Monitor Rotation Status**: Track rotation success/failure rates using CloudWatch metrics
4. **Track Secret Age**: Alert when secrets exceed their intended rotation period
5. **Dashboard Key Metrics**: Create dashboards showing secret access patterns, rotation status, and errors
6. **Log Secret Retrieval**: Log (but don't include values) when applications retrieve secrets for debugging
7. **Audit Secret Inventory**: Regularly review all secrets to identify unused or stale secrets
8. **Compliance Reporting**: Include secret rotation and access reports in compliance documentation

### Cost Optimization

1. **Remove Unused Secrets**: Regularly audit and delete secrets that are no longer needed
2. **Optimize Replication**: Only replicate secrets to regions where they're actually needed
3. **Implement Caching**: Use Secrets Manager caching libraries to reduce API calls (cost per 10,000 calls)
4. **Consolidate Related Secrets**: Store related credentials in single JSON secrets when appropriate
5. **Monitor API Costs**: Track GetSecretValue API calls and optimize retrieval patterns
6. **Use Long Cache TTLs**: Balance security with cost by using longer cache TTLs for less sensitive secrets
7. **Avoid Frequent Rotation**: Set rotation intervals based on actual security needs, not arbitrary short periods

### Development and Deployment

1. **Use Terraform Variables**: Parameterize secret names and configurations for environment flexibility
2. **Implement Ignore Changes**: Use `ignore_changes` for secret values managed outside Terraform
3. **Separate Secret Creation**: Consider creating secrets separately from application deployment
4. **Use Data Sources**: Reference existing secrets using data sources when not managing them directly
5. **Test in Lower Environments**: Validate secret configuration and rotation in dev/staging before production
6. **Automate Secret Creation**: Include secret creation in infrastructure provisioning workflows
7. **Version Pin Module**: Pin module version to prevent unexpected changes during deployments
8. **Document Dependencies**: Clearly document which applications and services depend on each secret

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-secrets-manager
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/secrets-manager/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-secrets-manager/tree/master/examples
- **AWS Secrets Manager Documentation**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- **AWS Secrets Manager API Reference**: https://docs.aws.amazon.com/secretsmanager/latest/apireference/Welcome.html
- **Secret Rotation**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html
- **Rotation Lambda Functions**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/reference_available-rotation-templates.html
- **Best Practices**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html
- **Security**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/security.html
- **Secrets Manager Caching**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets.html
- **Cross-Region Replication**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/create-manage-multi-region-secrets.html
- **Pricing**: https://aws.amazon.com/secrets-manager/pricing/
- **Compliance**: https://aws.amazon.com/compliance/services-in-scope/
- **VPC Endpoints**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/vpc-endpoint-overview.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Security First**: Always use KMS encryption; prefer customer-managed keys for production secrets
2. **Enable Rotation**: Implement automatic rotation for database credentials and long-lived secrets
3. **Use Resource Policies**: Configure least privilege access using resource policy statements
4. **Block Public Access**: Always set block_public_policy to true to prevent public exposure
5. **Replicate Critical Secrets**: Enable cross-region replication for mission-critical application secrets
6. **Set Recovery Windows**: Use 30-day recovery window for production, 7 days for staging, 0 for testing
7. **Tag Comprehensively**: Apply tags for owner, environment, application, compliance, and cost tracking
8. **Monitor Rotation**: Set up CloudWatch alarms for rotation failures and missed rotation schedules
9. **Use Descriptive Names**: Name secrets clearly with environment and purpose (e.g., "prod-rds-admin")
10. **Cache Appropriately**: Implement client-side caching to reduce API calls and costs
11. **Audit Access**: Enable CloudTrail and regularly review secret access patterns
12. **Document Secret Structure**: Maintain clear documentation of JSON schemas used in secrets for consistency
