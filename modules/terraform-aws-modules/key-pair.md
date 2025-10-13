# Terraform AWS Key Pair Module

## Module Information

- **Module Name**: `key-pair`
- **Source**: `terraform-aws-modules/key-pair/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-key-pair
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/key-pair/aws/latest
- **Latest Version**: 2.1.0
- **Purpose**: Terraform module that creates and manages AWS EC2 key pairs for SSH access to EC2 instances
- **Service**: AWS EC2 (Elastic Compute Cloud) - Key Pairs
- **Category**: Security, Compute, Access Management
- **Keywords**: key-pair, ec2-key-pair, ssh-key, public-key, private-key, rsa, ed25519, key-generation, tls-private-key, openssh, pem, key-import, key-material, ssh-access, ec2-access, instance-access, ssh-authentication, key-fingerprint, key-management, cryptography, asymmetric-encryption, public-key-cryptography, key-rotation, ssh-login, remote-access, bastion-host, jumpbox, secure-access, 4096-bit, key-algorithm, key-pair-creation
- **Use For**: EC2 SSH access, secure instance login, bastion host authentication, remote server administration, automated deployment access, CI/CD instance access, development environment setup, emergency instance access, key rotation workflows, multi-account key management

## Description

AWS EC2 Key Pairs are cryptographic key pairs used for secure SSH authentication to EC2 instances. This Terraform module provides a flexible and secure way to create and manage EC2 key pairs, supporting multiple key generation and import scenarios. The module can generate private keys automatically using Terraform's TLS provider, import externally created public keys, or work with existing key material, making it adaptable to various security policies and operational workflows.

The module supports both RSA and ED25519 cryptographic algorithms, with configurable key sizes for RSA keys (defaulting to 4096 bits for enhanced security). It can conditionally create key pairs based on environment requirements, generate private keys within Terraform (with appropriate security considerations), or import public keys from external key generation tools. The module outputs key pair metadata including ARNs, fingerprints, and IDs, as well as private and public key material in multiple formats (PEM, OpenSSH) for integration with different systems and tools.

This module is essential for organizations managing EC2 infrastructure, particularly those requiring standardized key management across multiple environments, accounts, or regions. It simplifies key pair creation in infrastructure-as-code workflows, supports key rotation strategies, and integrates seamlessly with bastion hosts, jump boxes, and automated deployment systems. By managing key pairs through Terraform, teams can version control their access configurations, audit key usage, and maintain consistent security practices across their AWS infrastructure.

## Key Features

- **Module-Generated Private Keys**: Automatically generate private keys using Terraform's TLS provider for simplified key creation
- **External Public Key Import**: Import public keys from externally generated key pairs for organizations with existing key management processes
- **RSA Algorithm Support**: Create RSA key pairs with configurable bit sizes (default 4096 bits) for strong encryption
- **ED25519 Algorithm Support**: Generate modern ED25519 keys for enhanced security and performance over traditional RSA
- **Configurable RSA Key Size**: Specify RSA key bit size (2048, 3072, 4096) to balance security and performance requirements
- **Conditional Key Pair Creation**: Control key pair creation with boolean flags for environment-specific deployments
- **Private Key Generation Control**: Optionally generate private keys or use externally managed private keys based on security policies
- **Multiple Output Formats**: Export keys in PEM and OpenSSH formats for compatibility with different tools and systems
- **Key Fingerprint Generation**: Automatic generation of MD5 and SHA256 fingerprints for key verification and auditing
- **Key Pair Metadata**: Output key pair ARN, ID, name, and fingerprint for integration with other AWS resources
- **Tagging Support**: Comprehensive tagging capabilities for resource organization, cost allocation, and compliance tracking
- **Dynamic Naming**: Support for key name prefixes to generate unique key pair names automatically
- **State Management**: Secure storage of private keys in Terraform state (with appropriate backend encryption)
- **Idempotent Operations**: Safe to run multiple times without creating duplicate resources
- **Cross-Region Support**: Create key pairs in any AWS region for multi-region architectures

## Main Use Cases

1. **EC2 Instance SSH Access**: Create key pairs for secure SSH authentication to EC2 instances across environments
2. **Bastion Host Configuration**: Generate dedicated key pairs for bastion hosts and jump boxes in secure network architectures
3. **CI/CD Pipeline Access**: Provision key pairs for automated deployment systems to access EC2 instances
4. **Development Environment Setup**: Standardize key pair creation across development, staging, and production environments
5. **Multi-Account Key Management**: Manage key pairs consistently across multiple AWS accounts in organization structures
6. **Key Rotation Workflows**: Facilitate key rotation by programmatically creating new key pairs and deprecating old ones
7. **Emergency Access Keys**: Create and store emergency access key pairs for disaster recovery scenarios
8. **Automated Instance Provisioning**: Generate key pairs as part of automated infrastructure deployment workflows
9. **Compliance and Auditing**: Track key pair creation and usage through Terraform state and AWS CloudTrail
10. **Cross-Region Deployments**: Create identical key pairs across multiple regions for consistent access patterns

## Best Practices

### Key Generation and Security

1. **Use Strong Key Algorithms**: Prefer ED25519 for new deployments or RSA 4096-bit keys for maximum security
2. **Avoid Storing Private Keys in State**: When possible, generate keys outside Terraform and import only public keys to avoid sensitive data in state files
3. **Encrypt Terraform State**: Always use encrypted state backends (S3 with KMS, Terraform Cloud) when storing private keys in state
4. **Use External Key Generation**: For production environments, generate keys using secure key management tools (AWS KMS, HashiCorp Vault) and import public keys
5. **Enable State File Access Controls**: Restrict access to Terraform state files containing private keys using IAM policies and S3 bucket policies
6. **Rotate Keys Regularly**: Establish a key rotation schedule (e.g., every 90-180 days) and use Terraform to manage the rotation process
7. **Use Different Keys per Environment**: Create separate key pairs for development, staging, and production to limit blast radius of compromised keys
8. **Limit Key Distribution**: Minimize the number of people and systems with access to private keys
9. **Use ED25519 When Possible**: Prefer ED25519 over RSA for better security, smaller key sizes, and faster operations
10. **Validate Key Fingerprints**: Always verify key fingerprints after creation to ensure key integrity

### Access Control and Management

1. **Implement Least Privilege**: Restrict key pair usage to only the instances and users that require access
2. **Use IAM Policies**: Control who can create, import, or delete key pairs using IAM policies
3. **Tag Key Pairs Consistently**: Apply tags indicating owner, environment, purpose, and expiration date for tracking
4. **Document Key Ownership**: Maintain clear documentation of which teams or individuals own which key pairs
5. **Disable Unused Keys**: Remove or disable key pairs that are no longer in use to reduce security risk
6. **Monitor Key Usage**: Use AWS CloudTrail to monitor key pair creation, deletion, and association with instances
7. **Implement Key Approval Process**: Require approval workflows for production key pair creation
8. **Use Unique Keys per Application**: Avoid sharing key pairs across multiple applications or services

### Operational Excellence

1. **Version Control Key Configurations**: Store Terraform configurations for key pairs in version control for audit trails
2. **Use Descriptive Key Names**: Name key pairs clearly indicating their purpose, environment, and owner (e.g., "prod-bastion-ops-team")
3. **Automate Key Rotation**: Create Terraform workflows or modules to automate key rotation and instance updates
4. **Test Key Access**: Validate new key pairs can successfully authenticate to instances before distributing
5. **Backup Private Keys Securely**: Store private key backups in secure key vaults (AWS Secrets Manager, HashiCorp Vault) with encryption
6. **Document Key Locations**: Maintain documentation of where private keys are stored and who has access
7. **Use Key Name Prefixes**: Leverage key name prefixes for auto-generated unique names in multi-environment deployments
8. **Plan for Key Expiration**: Set expiration dates for keys and implement automated alerts before expiration

### Instance and Application Integration

1. **Use Systems Manager**: Consider AWS Systems Manager Session Manager as an alternative to SSH for enhanced security
2. **Configure SSH Properly**: Disable password authentication and root login on instances when using key pairs
3. **Use SSH Certificates**: For advanced use cases, consider SSH certificates with short lifetimes instead of static key pairs
4. **Implement Jump Hosts**: Use dedicated bastion hosts with key pairs rather than distributing keys to all instances
5. **Rotate Keys on Instance Launch**: Include key rotation logic in instance user data or AMI baking processes
6. **Use Instance Profiles**: Combine key pair access with IAM instance profiles for layered security
7. **Limit SSH Access**: Use security groups and NACLs to restrict SSH access to known IP ranges or VPN endpoints

### Monitoring and Compliance

1. **Enable CloudTrail Logging**: Log all key pair API calls for security auditing and compliance
2. **Set Up Key Creation Alerts**: Create CloudWatch alarms or EventBridge rules for new key pair creation events
3. **Audit Key Usage Regularly**: Periodically review which key pairs exist and whether they're still needed
4. **Track Key Age**: Monitor key pair age and alert when keys exceed rotation thresholds
5. **Compliance Reporting**: Include key pair inventory in compliance reports (SOC2, ISO 27001, PCI-DSS)
6. **Scan for Exposed Keys**: Use tools to scan code repositories and logs for accidentally committed private keys
7. **Monitor Failed Authentication**: Track SSH authentication failures in instance logs to detect potential attacks

### Disaster Recovery

1. **Store Keys in Multiple Locations**: Backup private keys in geographically distributed secure locations
2. **Document Recovery Procedures**: Maintain runbooks for key recovery and instance access in disaster scenarios
3. **Test Recovery Processes**: Regularly test ability to access instances using backup keys
4. **Create Emergency Access Keys**: Maintain separate emergency access key pairs stored securely for break-glass scenarios
5. **Cross-Region Key Availability**: Ensure key pairs needed for DR are available in disaster recovery regions

### Cost Optimization

1. **Remove Unused Key Pairs**: Regularly audit and delete unused key pairs to reduce management overhead
2. **Consolidate Where Appropriate**: Use shared key pairs for non-production environments to reduce complexity (with proper access controls)
3. **Automate Key Lifecycle**: Reduce manual effort and errors by fully automating key creation, rotation, and deletion

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-key-pair
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/key-pair/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-key-pair/tree/master/examples
- **AWS Key Pairs Documentation**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html
- **AWS EC2 API Reference**: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_CreateKeyPair.html
- **SSH Key Best Practices**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-best-practices.html
- **ED25519 vs RSA**: https://blog.g3rt.nl/upgrade-your-ssh-keys.html
- **Terraform TLS Provider**: https://registry.terraform.io/providers/hashicorp/tls/latest/docs
- **AWS Systems Manager Session Manager**: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html
- **AWS Secrets Manager**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- **EC2 Instance Connect**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-methods.html
- **SSH Security Hardening**: https://aws.amazon.com/blogs/security/securely-connect-to-linux-instances-running-in-a-private-amazon-vpc/

## Notes for AI Agents

When using this module in automated workflows:

1. **Security First**: Never commit private keys to version control; use secure state backends with encryption
2. **Prefer External Generation**: Generate keys outside Terraform using secure tools and import only public keys for production
3. **Use Strong Algorithms**: Default to ED25519 or RSA 4096-bit keys for maximum security
4. **Encrypt State Backend**: Always use encrypted S3 buckets or Terraform Cloud for state storage when private keys are managed
5. **Tag Consistently**: Apply comprehensive tags including owner, environment, purpose, and creation date
6. **Implement Rotation**: Build key rotation into infrastructure workflows and document rotation schedules
7. **Monitor Creation**: Set up alerts for new key pair creation to detect unauthorized access attempts
8. **Audit Regularly**: Review existing key pairs and remove unused ones to reduce security risk
9. **Document Thoroughly**: Maintain clear documentation of key ownership, purpose, and storage locations
10. **Test Access**: Validate key pairs work correctly before relying on them for production access
11. **Use Conditional Creation**: Leverage the `create` parameter to control key pair creation across environments
12. **Consider Alternatives**: Evaluate AWS Systems Manager Session Manager as a more secure alternative to traditional SSH key pairs
