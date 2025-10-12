---
module_name: kms
keywords: [kms, key-management, encryption, cmk, customer-master-key, key-rotation, key-policy, encryption-at-rest, data-encryption, crypto, cryptographic-keys, aws-kms, symmetric-encryption, asymmetric-encryption, key-aliases, key-grants, multi-region-keys, external-keys, key-material, cloud-security, data-protection, compliance, access-control, iam-policy, key-administrators, key-users, envelope-encryption, encryption-sdk, server-side-encryption, client-side-encryption, key-store, hsm, hardware-security-module, fips, dnssec, signing-keys, ecc, rsa, aes, key-lifecycle, key-deletion, bring-your-own-key, byok, automatic-rotation, manual-rotation, cloudwatch-logs, s3-encryption, ebs-encryption, rds-encryption, secrets-manager, parameter-store]
---

# Terraform AWS KMS Module

## Module Information

- **Module Name**: `kms`
- **Source**: `terraform-aws-modules/kms/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-kms
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/kms/aws/latest
- **Latest Version**: 4.1.0
- **Purpose**: Terraform module that creates and manages AWS KMS (Key Management Service) resources including customer master keys, aliases, grants, and policies
- **Service**: AWS KMS (Key Management Service)
- **Category**: Security, Encryption, Compliance
- **Keywords**: kms, encryption, cmk, key-rotation, key-policy, data-encryption, cryptographic-keys, symmetric-encryption, asymmetric-encryption, key-aliases, multi-region-keys, external-keys, compliance, access-control, iam-policy, envelope-encryption, server-side-encryption, dnssec, signing-keys, automatic-rotation, bring-your-own-key, cloudwatch-logs, s3-encryption, ebs-encryption, rds-encryption
- **Use For**: encrypting data at rest, securing application secrets, protecting database credentials, envelope encryption patterns, compliance requirements (HIPAA/PCI-DSS), server-side encryption for S3/EBS/RDS, signing and verification operations, cross-region data replication with encryption, external key material management, service-specific encryption keys, automated key lifecycle management, secure multi-tenant architectures

## Description

This Terraform module provides comprehensive management of AWS Key Management Service (KMS) resources, enabling organizations to create and manage customer master keys (CMKs) for encrypting data across AWS services and applications. The module supports both symmetric and asymmetric encryption keys, with flexible configuration options for key policies, access controls, rotation schedules, and multi-region deployments. It abstracts the complexity of KMS key management while providing fine-grained control over cryptographic operations and access permissions.

AWS KMS is a managed service that makes it easy to create and control the encryption keys used to encrypt data. The service uses hardware security modules (HSMs) to protect the security of encryption keys and integrates with most AWS services to provide encryption at rest. This module simplifies the creation of KMS keys by providing sensible defaults while allowing customization for specific security requirements, compliance needs, and operational workflows.

The module supports advanced features including external key material (bring-your-own-key), multi-region key replication for global applications, key grants for temporary access delegation, and service-specific policies for seamless integration with CloudWatch Logs, S3, EBS, RDS, and other AWS services. It enables both encryption/decryption operations and digital signing/verification use cases, supporting modern cryptographic standards including AES, RSA, and ECC key specifications.

## Key Features

- **Symmetric and Asymmetric Keys**: Create keys for both encryption/decryption (symmetric) and signing/verification (asymmetric) operations
- **Automatic Key Rotation**: Enable automatic annual rotation of key material while maintaining the same key ID and ARN
- **Key Policy Management**: Configure detailed IAM resource policies controlling key administrators, users, and service permissions
- **Key Aliases**: Create human-readable aliases for keys to simplify key management and application integration
- **Key Grants**: Delegate temporary, granular permissions for cryptographic operations without modifying key policies
- **Multi-Region Keys**: Replicate keys across AWS regions for global applications with consistent encryption
- **External Key Material**: Import and manage your own key material (BYOK - Bring Your Own Key) for compliance requirements
- **Custom Key Store Support**: Integrate with AWS CloudHSM custom key stores for dedicated hardware security modules
- **Key Usage Flexibility**: Configure keys for specific purposes (ENCRYPT_DECRYPT, SIGN_VERIFY, GENERATE_VERIFY_MAC)
- **Service Integration Policies**: Pre-configured policy templates for CloudWatch Logs, S3, EBS, RDS, and other AWS services
- **Key Specifications**: Support for various cryptographic algorithms including AES_256, RSA_2048, RSA_4096, ECC_NIST_P256, ECC_NIST_P384
- **DNSSEC Signing Keys**: Specialized configuration for Route53 DNSSEC with appropriate key specifications
- **Deletion Protection**: Configure deletion window (7-30 days) to prevent accidental key deletion
- **Tag Management**: Comprehensive tagging support for cost allocation, access control, and resource organization
- **Policy Lockout Safety**: Built-in safety checks to prevent locking yourself out of key management
- **Compliance Support**: Features for meeting HIPAA, PCI-DSS, FedRAMP, and other regulatory requirements
- **Cross-Account Access**: Configure key policies for secure cross-account encryption and decryption
- **Conditional Access**: Support for IAM condition keys including MFA requirements and source IP restrictions
- **Key State Management**: Track key states (Enabled, Disabled, PendingDeletion, PendingImport) throughout lifecycle
- **Audit Trail Integration**: Automatic CloudTrail logging of all key usage and management operations

## Main Use Cases

1. **Data-at-Rest Encryption**: Encrypt sensitive data stored in S3, EBS volumes, RDS databases, and other storage services
2. **Secrets Management**: Protect application secrets, API keys, and database credentials in AWS Secrets Manager and Systems Manager Parameter Store
3. **Compliance and Governance**: Meet regulatory requirements for encryption key management (HIPAA, PCI-DSS, GDPR, FedRAMP)
4. **Envelope Encryption**: Implement envelope encryption patterns for large datasets using data encryption keys (DEKs) encrypted by KMS
5. **Cross-Region Replication**: Enable encrypted data replication across AWS regions for disaster recovery and global applications
6. **Service-Specific Encryption**: Create dedicated encryption keys for CloudWatch Logs, SNS topics, SQS queues, and Lambda environment variables
7. **Digital Signatures**: Generate and verify cryptographic signatures for code signing, document signing, and API authentication
8. **Multi-Tenant Security**: Implement cryptographic isolation between tenants in multi-tenant SaaS applications
9. **Bring Your Own Key (BYOK)**: Import external key material to maintain control over encryption keys for compliance
10. **Automated Key Lifecycle**: Implement automated key rotation, expiration, and deletion policies for security best practices

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether KMS resources will be created |
| `description` | `string` | `null` | The description of the key as viewed in AWS console |
| `key_usage` | `string` | `"ENCRYPT_DECRYPT"` | Specifies the intended use of the key (ENCRYPT_DECRYPT, SIGN_VERIFY, GENERATE_VERIFY_MAC) |
| `customer_master_key_spec` | `string` | `null` | Key specification (SYMMETRIC_DEFAULT, RSA_2048, RSA_4096, ECC_NIST_P256, etc.) |
| `enable_key_rotation` | `bool` | `true` | Specifies whether automatic key rotation is enabled (only for symmetric keys) |
| `rotation_period_in_days` | `number` | `null` | Custom rotation period in days (90-2560), defaults to 365 if not specified |
| `multi_region` | `bool` | `false` | Indicates whether the KMS key is a multi-Region key |
| `deletion_window_in_days` | `number` | `null` | The waiting period before key deletion (7-30 days) |
| `bypass_policy_lockout_safety_check` | `bool` | `null` | Flag to bypass the key policy lockout safety check |
| `key_owners` | `list(string)` | `[]` | List of IAM ARNs for key owners (full permissions) |
| `key_administrators` | `list(string)` | `[]` | List of IAM ARNs for key administrators (can manage but not use key) |
| `key_users` | `list(string)` | `[]` | List of IAM ARNs for key users (can use key for crypto operations) |
| `key_service_users` | `list(string)` | `[]` | List of IAM ARNs for service principals that can use the key |
| `key_symmetric_encryption_users` | `list(string)` | `[]` | List of IAM ARNs allowed to perform symmetric encryption/decryption |
| `key_hmac_users` | `list(string)` | `[]` | List of IAM ARNs allowed to perform HMAC operations |
| `key_asymmetric_public_encryption_users` | `list(string)` | `[]` | List of IAM ARNs allowed to use public key for asymmetric encryption |
| `key_asymmetric_sign_verify_users` | `list(string)` | `[]` | List of IAM ARNs allowed to perform sign/verify operations |
| `aliases` | `list(string)` | `[]` | List of alias names for the KMS key (without 'alias/' prefix) |
| `computed_aliases` | `map(any)` | `{}` | Map of computed aliases with additional configuration |
| `grants` | `map(any)` | `{}` | Map of grant configurations for delegated permissions |
| `policy` | `string` | `null` | Custom key policy (JSON). If not provided, policy is generated from key_* variables |
| `enable_default_policy` | `bool` | `true` | Whether to enable the default key policy |
| `source_policy_documents` | `list(string)` | `[]` | List of additional IAM policy documents to merge with default policy |
| `override_policy_documents` | `list(string)` | `[]` | List of IAM policy documents that override the default policy |
| `create_external` | `bool` | `false` | Whether to create an external KMS key (for importing key material) |
| `key_material_base64` | `string` | `null` | Base64 encoded 256-bit symmetric encryption key material for external keys |
| `valid_to` | `string` | `null` | Time at which the imported key material expires (RFC3339 format) |
| `custom_key_store_id` | `string` | `null` | ID of the KMS Custom Key Store for CloudHSM integration |
| `tags` | `map(string)` | `{}` | Map of tags to assign to all KMS resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `key_arn` | The Amazon Resource Name (ARN) of the key |
| `key_id` | The globally unique identifier for the key |
| `key_region` | The AWS region where the key is managed |
| `key_policy` | The IAM resource policy attached to the key |
| `external_key_expiration_model` | Whether the external key material expires (KEY_MATERIAL_EXPIRES or KEY_MATERIAL_DOES_NOT_EXPIRE) |
| `external_key_state` | The state of the external CMK (PendingImport, Enabled, Disabled, etc.) |
| `external_key_usage` | The cryptographic operations for which the external key can be used |
| `aliases` | A map of alias names and their attributes created for the key |
| `grants` | A map of grants created and their attributes (marked as sensitive) |

## Usage Examples

### Example 1: Basic Encryption Key with Auto-Rotation

```hcl
module "kms_basic" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 3.0"

  description             = "KMS key for encrypting application data"
  key_usage               = "ENCRYPT_DECRYPT"
  enable_key_rotation     = true
  rotation_period_in_days = 90
  deletion_window_in_days = 30

  # Define key administrators
  key_administrators = [
    "arn:aws:iam::123456789012:role/KMSAdminRole",
    "arn:aws:iam::123456789012:user/admin"
  ]

  # Define key users
  key_users = [
    "arn:aws:iam::123456789012:role/ApplicationRole",
    "arn:aws:iam::123456789012:role/DataProcessingRole"
  ]

  # Create alias for easy reference
  aliases = ["myapp/encryption-key"]

  tags = {
    Environment = "production"
    Application = "core-app"
    ManagedBy   = "terraform"
  }
}

# Use the key in S3 bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = module.kms_basic.key_arn
    }
  }
}
```

### Example 2: Multi-Region Key for Global Application

```hcl
# Primary key in us-east-1
module "kms_primary" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 3.0"

  description         = "Multi-region KMS key for global application"
  multi_region        = true
  enable_key_rotation = true

  key_administrators = [
    "arn:aws:iam::123456789012:role/GlobalKMSAdmin"
  ]

  key_users = [
    "arn:aws:iam::123456789012:role/GlobalAppRole"
  ]

  aliases = ["global-app/primary"]

  tags = {
    Region      = "primary"
    Application = "global-app"
  }
}

# Replica key in eu-west-1
module "kms_replica" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 3.0"

  providers = {
    aws = aws.eu_west_1
  }

  description                = "Replica of multi-region KMS key"
  create_replica             = true
  primary_key_arn            = module.kms_primary.key_arn
  primary_external_key_arn   = module.kms_primary.external_key_arn

  aliases = ["global-app/replica-eu"]

  tags = {
    Region      = "replica"
    Application = "global-app"
  }
}
```

### Example 3: Service-Specific Key for CloudWatch Logs

```hcl
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

module "kms_cloudwatch" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 3.0"

  description             = "KMS key for CloudWatch Logs encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 7

  key_administrators = [
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/AdminRole"
  ]

  # Grant CloudWatch Logs service permission to use the key
  key_service_users = [
    "logs.${data.aws_region.current.name}.amazonaws.com"
  ]

  # Additional policy for CloudWatch Logs
  source_policy_documents = [
    data.aws_iam_policy_document.cloudwatch_logs.json
  ]

  aliases = ["cloudwatch-logs/encryption"]

  tags = {
    Service = "cloudwatch-logs"
    Purpose = "log-encryption"
  }
}

data "aws_iam_policy_document" "cloudwatch_logs" {
  statement {
    sid    = "Enable CloudWatch Logs Encryption"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["logs.${data.aws_region.current.name}.amazonaws.com"]
    }

    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:CreateGrant",
      "kms:DescribeKey"
    ]

    resources = ["*"]

    condition {
      test     = "ArnLike"
      variable = "kms:EncryptionContext:aws:logs:arn"
      values   = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:*"]
    }
  }
}

# Use with log group
resource "aws_cloudwatch_log_group" "example" {
  name              = "/aws/application/logs"
  kms_key_id        = module.kms_cloudwatch.key_arn
  retention_in_days = 30
}
```

### Example 4: External Key Material (BYOK)

```hcl
# Generate key material externally (example using OpenSSL)
# openssl rand -base64 32

module "kms_external" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 3.0"

  description     = "External KMS key with imported material"
  create_external = true

  # Import your own key material (base64 encoded 256-bit key)
  key_material_base64 = "Wblj06fduthWggmsT0cLVoIMOkeLbc2kVfMud77i/JY="

  # Optional: Set expiration time for key material
  valid_to = "2026-12-31T23:59:59Z"

  key_administrators = [
    "arn:aws:iam::123456789012:role/SecurityTeam"
  ]

  key_users = [
    "arn:aws:iam::123456789012:role/ComplianceApp"
  ]

  aliases = ["compliance/byok-key"]

  tags = {
    KeyType    = "external"
    Compliance = "required"
  }
}
```

### Example 5: Asymmetric Key for Digital Signatures

```hcl
module "kms_signing" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 3.0"

  description               = "Asymmetric KMS key for code signing"
  key_usage                 = "SIGN_VERIFY"
  customer_master_key_spec  = "RSA_4096"

  # Note: Rotation not supported for asymmetric keys
  enable_key_rotation = false

  key_administrators = [
    "arn:aws:iam::123456789012:role/SecurityAdmin"
  ]

  # Users who can sign
  key_asymmetric_sign_verify_users = [
    "arn:aws:iam::123456789012:role/CIPipelineRole",
    "arn:aws:iam::123456789012:role/CodeSigningRole"
  ]

  aliases = ["code-signing/rsa-4096"]

  tags = {
    Purpose = "digital-signatures"
    KeySpec = "RSA_4096"
  }
}

# Example: Use with AWS Signer
resource "aws_signer_signing_profile" "example" {
  platform_id = "AWSLambda-SHA384-ECDSA"
  name        = "lambda_signing_profile"

  signature_validity_period {
    value = 5
    type  = "YEARS"
  }
}
```

### Example 6: DNSSEC Signing Key for Route53

```hcl
module "kms_dnssec" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 3.0"

  description              = "KMS key for Route53 DNSSEC signing"
  key_usage                = "SIGN_VERIFY"
  customer_master_key_spec = "ECC_NIST_P256"
  deletion_window_in_days  = 7

  # DNSSEC keys cannot be rotated
  enable_key_rotation = false

  key_administrators = [
    "arn:aws:iam::123456789012:role/DNSAdmin"
  ]

  # Grant Route53 DNSSEC service permissions
  source_policy_documents = [
    data.aws_iam_policy_document.route53_dnssec.json
  ]

  aliases = ["route53/dnssec-signing"]

  tags = {
    Service = "route53-dnssec"
    KeyType = "ecc-p256"
  }
}

data "aws_iam_policy_document" "route53_dnssec" {
  statement {
    sid    = "Allow Route53 DNSSEC Service"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["dnssec-route53.amazonaws.com"]
    }

    actions = [
      "kms:DescribeKey",
      "kms:GetPublicKey",
      "kms:Sign"
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }

  statement {
    sid    = "Allow Route53 DNSSEC to create grant"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["dnssec-route53.amazonaws.com"]
    }

    actions   = ["kms:CreateGrant"]
    resources = ["*"]

    condition {
      test     = "Bool"
      variable = "kms:GrantIsForAWSResource"
      values   = ["true"]
    }
  }
}
```

### Example 7: Cross-Account Key Access

```hcl
data "aws_caller_identity" "current" {}

module "kms_cross_account" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 3.0"

  description         = "KMS key with cross-account access"
  enable_key_rotation = true

  # Current account administrators
  key_administrators = [
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/KMSAdmin"
  ]

  # Grant access to another AWS account
  source_policy_documents = [
    data.aws_iam_policy_document.cross_account_policy.json
  ]

  aliases = ["shared/cross-account-key"]

  tags = {
    SharedWith = "123456789999"
    Purpose    = "cross-account-encryption"
  }
}

data "aws_iam_policy_document" "cross_account_policy" {
  statement {
    sid    = "Enable Cross Account Access"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::123456789999:root"]
    }

    actions = [
      "kms:Decrypt",
      "kms:DescribeKey"
    ]

    resources = ["*"]

    # Optional: Add conditions for security
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = [
        "s3.us-east-1.amazonaws.com",
        "s3.eu-west-1.amazonaws.com"
      ]
    }
  }
}
```

### Example 8: Key with Grants for Temporary Access

```hcl
module "kms_with_grants" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 3.0"

  description         = "KMS key with grant-based access delegation"
  enable_key_rotation = true

  key_administrators = [
    "arn:aws:iam::123456789012:role/KMSAdmin"
  ]

  key_users = [
    "arn:aws:iam::123456789012:role/BaseAppRole"
  ]

  # Define grants for specific use cases
  grants = {
    lambda_grant = {
      grantee_principal = "arn:aws:iam::123456789012:role/LambdaExecutionRole"
      operations = [
        "Decrypt",
        "DescribeKey"
      ]
      constraints = {
        encryption_context_equals = {
          "Department" = "Engineering"
        }
      }
    }

    service_grant = {
      grantee_principal = "arn:aws:iam::123456789012:role/ServiceRole"
      operations = [
        "Encrypt",
        "Decrypt",
        "GenerateDataKey"
      ]
      retiring_principal = "arn:aws:iam::123456789012:role/ServiceRole"
      grant_creation_tokens = ["service-token-2024"]
    }
  }

  aliases = ["app/key-with-grants"]

  tags = {
    GrantManagement = "enabled"
  }
}
```

## Best Practices

### Key Design and Architecture

1. **Separate Keys by Purpose**: Create separate KMS keys for different services, environments, and data classifications to limit blast radius of compromises
2. **Use Descriptive Aliases**: Assign meaningful aliases to keys (e.g., `alias/prod/rds/customer-db`) for easier identification and management
3. **Plan for Key Hierarchy**: Design logical key organization aligned with your security and compliance requirements
4. **Consider Multi-Region Keys**: Use multi-region keys for globally distributed applications requiring consistent encryption across regions
5. **Implement Key Ownership Model**: Clearly define key owners, administrators, and users with appropriate separation of duties

### Security and Access Control

1. **Enable Key Rotation**: Always enable automatic key rotation for symmetric encryption keys (every 90-365 days)
2. **Apply Least Privilege**: Grant only the minimum required permissions in key policies and IAM policies
3. **Separate Administrative and Usage Permissions**: Key administrators should manage keys but not use them for cryptographic operations
4. **Use Grants for Temporary Access**: Prefer grants over key policy modifications for temporary or programmatic access delegation
5. **Implement Encryption Context**: Use encryption context for additional security and audit capabilities in encrypt/decrypt operations
6. **Require MFA for Sensitive Operations**: Add MFA conditions to key policies for key deletion or policy changes
7. **Restrict Cross-Account Access**: Carefully control and monitor cross-account key access with strict conditions
8. **Validate Policy Changes**: Always review key policy changes to prevent lockout scenarios

### Operational Excellence

1. **Set Appropriate Deletion Windows**: Use 30-day deletion window for production keys to allow recovery from accidental deletion
2. **Monitor Key Usage**: Enable CloudTrail logging and create CloudWatch alarms for unusual key usage patterns
3. **Tag Comprehensively**: Apply consistent tags for cost tracking, compliance, ownership, and lifecycle management
4. **Document Key Purpose**: Use detailed descriptions explaining what each key protects and who owns it
5. **Implement Backup Strategies**: For critical keys, consider replica keys in disaster recovery regions
6. **Test Key Policies**: Validate key policies in development before applying to production
7. **Automate Key Lifecycle**: Use Terraform for consistent, repeatable key provisioning and management
8. **Review Key Inventory Regularly**: Conduct periodic audits of all KMS keys to identify unused or unnecessary keys

### Compliance and Governance

1. **Meet Regulatory Requirements**: Configure keys to satisfy specific compliance standards (HIPAA, PCI-DSS, GDPR, FedRAMP)
2. **Enable Audit Logging**: Ensure all key operations are logged to CloudTrail for compliance and forensics
3. **Implement Data Classification**: Match key security controls to data sensitivity levels
4. **Use Custom Key Stores When Required**: For compliance requiring hardware security module (HSM) control, use AWS CloudHSM custom key stores
5. **Document Compliance Mappings**: Maintain documentation mapping keys to specific compliance requirements
6. **Implement Key Material Expiration**: For external keys, set appropriate expiration dates aligned with security policies

### Cost Optimization

1. **Consolidate Key Usage**: Balance security isolation with cost by sharing keys across similar use cases where appropriate
2. **Delete Unused Keys**: Schedule keys for deletion if no longer needed to avoid ongoing charges
3. **Monitor API Call Costs**: Track KMS API requests as they incur charges; optimize application code to minimize unnecessary calls
4. **Use Key Caching**: Implement data key caching in applications to reduce GenerateDataKey API calls
5. **Consider Regional Pricing**: Be aware that KMS pricing varies by region when deploying multi-region architectures

### Performance and Scalability

1. **Implement Client-Side Caching**: Cache data encryption keys to reduce KMS API calls and improve application performance
2. **Use Envelope Encryption**: For large data encryption, use envelope encryption pattern with local data keys
3. **Plan for API Rate Limits**: Design applications to handle KMS API throttling gracefully with exponential backoff
4. **Monitor Request Metrics**: Track KMS request rates and optimize application patterns if approaching service limits
5. **Use Async Encryption**: For high-throughput scenarios, implement asynchronous encryption patterns

### High Availability and Disaster Recovery

1. **Deploy Multi-Region Keys**: For mission-critical global applications, use multi-region keys for seamless failover
2. **Implement Cross-Region Backups**: Ensure encrypted backups can be decrypted in disaster recovery regions
3. **Test Key Failover**: Regularly test disaster recovery procedures involving KMS keys
4. **Document Key Dependencies**: Maintain inventory of which applications and data depend on each key
5. **Plan for Key Compromise**: Have incident response procedures for key compromise scenarios

### Development Best Practices

1. **Use Terraform Modules**: Leverage this module for consistent, tested key provisioning across environments
2. **Version Control Key Configurations**: Store all KMS configurations in version control with peer review
3. **Test in Non-Production First**: Always test key policy changes in dev/staging before production
4. **Implement CI/CD Validation**: Add automated tests for key policy syntax and permission validation
5. **Use Variables for Account IDs**: Parameterize account IDs and ARNs for multi-account deployments
6. **Handle Key Not Found Errors**: Implement robust error handling for scenarios where keys are deleted or unavailable
7. **Avoid Hardcoding Key IDs**: Use aliases or Terraform outputs to reference keys in application configurations

## Additional Resources

- **AWS KMS Documentation**: https://docs.aws.amazon.com/kms/
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/kms/aws/latest
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-kms
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-kms/tree/master/examples
- **AWS KMS Best Practices**: https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html
- **KMS Pricing**: https://aws.amazon.com/kms/pricing/
- **AWS KMS API Reference**: https://docs.aws.amazon.com/kms/latest/APIReference/
- **Key Policy Reference**: https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html
- **Envelope Encryption**: https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#enveloping
- **AWS Encryption SDK**: https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/
- **CloudTrail with KMS**: https://docs.aws.amazon.com/kms/latest/developerguide/logging-using-cloudtrail.html
- **KMS Quotas**: https://docs.aws.amazon.com/kms/latest/developerguide/limits.html
- **Multi-Region Keys**: https://docs.aws.amazon.com/kms/latest/developerguide/multi-region-keys-overview.html
- **Custom Key Stores**: https://docs.aws.amazon.com/kms/latest/developerguide/custom-key-store-overview.html
- **KMS Grant Concept**: https://docs.aws.amazon.com/kms/latest/developerguide/grants.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Security First**: Always implement least privilege access in key policies; never grant wildcard permissions
2. **Enable Rotation by Default**: Set `enable_key_rotation = true` for all symmetric encryption keys unless there's a specific reason not to
3. **Use Separate Keys**: Create dedicated keys for different services and environments to maintain security boundaries
4. **Implement Proper Tagging**: Apply comprehensive tags including Environment, Owner, CostCenter, and Compliance metadata
5. **Set Deletion Windows**: Always configure appropriate deletion windows (30 days for production) to prevent accidental data loss
6. **Validate Key Policies**: Use `bypass_policy_lockout_safety_check = false` (default) to prevent policy lockouts
7. **Monitor Key Usage**: Integrate with CloudWatch and CloudTrail for comprehensive monitoring and alerting
8. **Handle Asymmetric Keys Correctly**: Remember that asymmetric keys cannot be rotated; plan key lifecycle accordingly
9. **Use Aliases for Flexibility**: Reference keys by aliases in application code to allow key rotation without code changes
10. **Test Cross-Account Access**: Thoroughly test cross-account key access patterns in non-production environments
11. **Implement Encryption Context**: Use encryption context in application code for additional security layer and audit trail
12. **Plan for Compliance**: Configure key policies and features to align with specific compliance requirements (HIPAA, PCI-DSS, etc.)
13. **Consider Multi-Region for HA**: Use multi-region keys for applications requiring high availability across geographic regions
14. **Document Key Purpose**: Always provide descriptive descriptions and tags explaining what data each key protects
15. **Handle External Keys Carefully**: When using external key material, ensure proper key material lifecycle management
16. **Optimize API Calls**: Implement key caching strategies to minimize KMS API calls and associated costs
17. **Implement Error Handling**: Design applications to gracefully handle KMS throttling and temporary unavailability
18. **Regular Audits**: Periodically review key inventory, usage patterns, and access policies for security optimization
