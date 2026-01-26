# Terraform AWS KMS Module

## Module Information

- **Module Name**: `kms`
- **Source**: `terraform-aws-modules/kms/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-kms
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/kms/aws/latest
- **Latest Version**: 4.2.0
- **Purpose**: Creates and manages AWS KMS keys, aliases, grants, and policies for data encryption
- **Service**: AWS KMS (Key Management Service)
- **Category**: Security, Encryption
- **Keywords**: kms, encryption, cmk, key-rotation, key-policy, symmetric-encryption, asymmetric-encryption, multi-region-keys, key-aliases, key-grants, byok, cloudwatch-logs-encryption, s3-encryption, ebs-encryption
- **Use For**: encrypting data at rest, securing application secrets, envelope encryption, compliance requirements (HIPAA/PCI-DSS), server-side encryption for S3/EBS/RDS, digital signing, cross-region encrypted replication, bring-your-own-key scenarios

## Description

This module provides comprehensive management of AWS KMS resources, enabling creation of customer master keys (CMKs) for encrypting data across AWS services. It supports both symmetric and asymmetric keys with flexible configuration for key policies, rotation schedules, and multi-region deployments.

AWS KMS uses hardware security modules (HSMs) to protect encryption keys and integrates with most AWS services for encryption at rest. The module supports external key material (BYOK), multi-region key replication, key grants for temporary access, and service-specific policies for CloudWatch Logs, S3, EBS, RDS, and other services.

## Key Features

- **Symmetric and Asymmetric Keys**: Supports ENCRYPT_DECRYPT, SIGN_VERIFY, and GENERATE_VERIFY_MAC operations
- **Automatic Key Rotation**: Configurable rotation period (90-2560 days) for symmetric keys
- **Key Policy Management**: IAM-based policies with key owners, administrators, users, and service roles
- **Key Aliases**: Human-readable aliases with optional name prefix support
- **Key Grants**: Temporary, granular permissions delegation with encryption context constraints
- **Multi-Region Keys**: Primary and replica keys across AWS regions
- **External Key Material (BYOK)**: Import custom key material with optional expiration
- **CloudHSM Integration**: Custom key store support for dedicated HSMs
- **Service Integration**: Built-in support for AutoScaling, Route53 DNSSEC, and other AWS services
- **Deletion Protection**: Configurable deletion window (7-30 days)

## Main Use Cases

1. **Data-at-Rest Encryption**: Encrypt S3, EBS, RDS, and other storage services
2. **Secrets Management**: Protect secrets in Secrets Manager and Parameter Store
3. **Compliance**: Meet HIPAA, PCI-DSS, GDPR, FedRAMP encryption requirements
4. **Envelope Encryption**: Encrypt data encryption keys (DEKs) with KMS
5. **Cross-Region Replication**: Encrypted data replication with multi-region keys
6. **Digital Signatures**: Code signing and document verification
7. **Service-Specific Encryption**: Dedicated keys for CloudWatch Logs, SNS, SQS, Lambda
8. **Bring Your Own Key**: Import external key material for compliance

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create KMS resources |
| `description` | `string` | `null` | Key description displayed in AWS console |
| `key_usage` | `string` | `"ENCRYPT_DECRYPT"` | Key usage: ENCRYPT_DECRYPT, SIGN_VERIFY, GENERATE_VERIFY_MAC |
| `customer_master_key_spec` | `string` | `null` | Key spec: SYMMETRIC_DEFAULT, RSA_2048, RSA_4096, ECC_NIST_P256, etc. |
| `enable_key_rotation` | `bool` | `true` | Enable automatic key rotation (symmetric keys only) |
| `rotation_period_in_days` | `number` | `null` | Custom rotation period (90-2560 days), defaults to 365 |
| `multi_region` | `bool` | `false` | Create multi-region key |
| `deletion_window_in_days` | `number` | `null` | Deletion wait period (7-30 days) |
| `key_owners` | `list(string)` | `[]` | IAM ARNs with full key permissions |
| `key_administrators` | `list(string)` | `[]` | IAM ARNs for key management (not usage) |
| `key_users` | `list(string)` | `[]` | IAM ARNs for cryptographic operations |
| `key_service_users` | `list(string)` | `[]` | Service principals that can use the key |
| `key_service_roles_for_autoscaling` | `list(string)` | `[]` | AutoScaling service-linked roles |
| `aliases` | `list(string)` | `[]` | Alias names (without 'alias/' prefix) |
| `grants` | `map(any)` | `{}` | Grant configurations for delegated permissions |
| `policy` | `string` | `null` | Custom key policy JSON (overrides key_* variables) |
| `source_policy_documents` | `list(string)` | `[]` | Additional IAM policy documents to merge |
| `create_external` | `bool` | `false` | Create external key for importing key material |
| `key_material_base64` | `string` | `null` | Base64-encoded 256-bit key material for external keys |
| `valid_to` | `string` | `null` | External key material expiration (RFC3339) |
| `primary_key_arn` | `string` | `null` | Primary key ARN for replica creation |
| `route53_dnssec_sources` | `list(object)` | `[]` | Route53 hosted zones for DNSSEC signing |
| `tags` | `map(string)` | `{}` | Tags for all KMS resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `key_arn` | The ARN of the key |
| `key_id` | The globally unique key identifier |
| `key_policy` | The IAM resource policy attached to the key |
| `key_region` | The AWS region where the key is managed |
| `aliases` | Map of created aliases and their attributes |
| `grants` | Map of created grants and their attributes |
| `external_key_state` | State of external CMK (PendingImport, Enabled, etc.) |
| `external_key_expiration_model` | Whether external key material expires |

## Usage Examples

### Basic Encryption Key with Auto-Rotation

```hcl
module "kms" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  description             = "Application data encryption key"
  enable_key_rotation     = true
  rotation_period_in_days = 90
  deletion_window_in_days = 30

  key_administrators = ["arn:aws:iam::123456789012:role/KMSAdmin"]
  key_users          = ["arn:aws:iam::123456789012:role/AppRole"]

  aliases = ["myapp/encryption"]

  tags = {
    Environment = "production"
    Application = "myapp"
  }
}
```

### Multi-Region Key

```hcl
# Primary key
module "kms_primary" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  description         = "Multi-region key for global app"
  multi_region        = true
  enable_key_rotation = true

  key_administrators = ["arn:aws:iam::123456789012:role/GlobalAdmin"]
  key_users          = ["arn:aws:iam::123456789012:role/GlobalApp"]

  aliases = ["global-app/primary"]
}

# Replica key in another region
module "kms_replica" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  providers = { aws = aws.eu_west_1 }

  create_replica  = true
  primary_key_arn = module.kms_primary.key_arn

  aliases = ["global-app/replica-eu"]
}
```

### CloudWatch Logs Encryption

```hcl
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

module "kms_cloudwatch" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  description         = "CloudWatch Logs encryption key"
  enable_key_rotation = true

  key_administrators = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/Admin"]

  key_service_users = ["logs.${data.aws_region.current.name}.amazonaws.com"]

  source_policy_documents = [data.aws_iam_policy_document.cloudwatch.json]

  aliases = ["cloudwatch-logs/encryption"]
}

data "aws_iam_policy_document" "cloudwatch" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["logs.${data.aws_region.current.name}.amazonaws.com"]
    }
    actions   = ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey*", "kms:DescribeKey"]
    resources = ["*"]
    condition {
      test     = "ArnLike"
      variable = "kms:EncryptionContext:aws:logs:arn"
      values   = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:*"]
    }
  }
}
```

### External Key (BYOK)

```hcl
module "kms_external" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  description     = "External key with imported material"
  create_external = true

  key_material_base64 = var.key_material_base64
  valid_to            = "2027-12-31T23:59:59Z"

  key_administrators = ["arn:aws:iam::123456789012:role/SecurityTeam"]
  key_users          = ["arn:aws:iam::123456789012:role/ComplianceApp"]

  aliases = ["compliance/byok-key"]
}
```

### Asymmetric Signing Key

```hcl
module "kms_signing" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  description              = "Code signing key"
  key_usage                = "SIGN_VERIFY"
  customer_master_key_spec = "RSA_4096"
  enable_key_rotation      = false  # Not supported for asymmetric keys

  key_administrators           = ["arn:aws:iam::123456789012:role/SecurityAdmin"]
  key_asymmetric_sign_verify_users = ["arn:aws:iam::123456789012:role/CIPipeline"]

  aliases = ["code-signing/rsa-4096"]
}
```

### Key with Grants

```hcl
module "kms_with_grants" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  description         = "Key with grant-based access"
  enable_key_rotation = true

  key_administrators = ["arn:aws:iam::123456789012:role/KMSAdmin"]

  grants = {
    lambda = {
      grantee_principal = "arn:aws:iam::123456789012:role/LambdaRole"
      operations        = ["Decrypt", "DescribeKey"]
      constraints = {
        encryption_context_equals = { Department = "Engineering" }
      }
    }
  }

  aliases = ["app/key-with-grants"]
}
```

### Route53 DNSSEC Signing

```hcl
module "kms_dnssec" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  description              = "Route53 DNSSEC signing key"
  key_usage                = "SIGN_VERIFY"
  customer_master_key_spec = "ECC_NIST_P256"
  enable_key_rotation      = false

  key_administrators = ["arn:aws:iam::123456789012:role/DNSAdmin"]

  route53_dnssec_sources = [
    { account_ids = [data.aws_caller_identity.current.account_id] }
  ]

  aliases = ["route53/dnssec"]
}
```

## Best Practices

### Key Design

1. **Separate Keys by Purpose**: Create dedicated keys for different services and data classifications
2. **Use Descriptive Aliases**: Format like `alias/env/service/purpose` for easy identification
3. **Enable Rotation**: Always enable automatic rotation for symmetric keys (90-365 days recommended)
4. **Plan Multi-Region**: Use multi-region keys for global applications requiring consistent encryption

### Security

1. **Least Privilege**: Grant minimum required permissions via key policies
2. **Separate Admin/User Roles**: Key administrators should not use keys for crypto operations
3. **Use Grants for Temporary Access**: Prefer grants over policy changes for short-term delegation
4. **Implement Encryption Context**: Add context for audit trail and access control
5. **Validate Policies**: Keep `bypass_policy_lockout_safety_check = false` (default)

### Operations

1. **Set 30-Day Deletion Window**: For production keys to prevent accidental loss
2. **Monitor with CloudTrail**: All KMS operations are automatically logged
3. **Tag Comprehensively**: Include Environment, Owner, CostCenter tags
4. **Test in Non-Production**: Validate policy changes before production deployment

### Cost Optimization

1. **Consolidate Where Appropriate**: Share keys across similar use cases
2. **Delete Unused Keys**: Schedule unused keys for deletion
3. **Implement Key Caching**: Cache data keys in applications to reduce API calls

## Additional Resources

- **AWS KMS Documentation**: https://docs.aws.amazon.com/kms/
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/kms/aws/latest
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-kms
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-kms/tree/master/examples
- **KMS Best Practices**: https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html
- **Key Policy Reference**: https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html
- **Multi-Region Keys**: https://docs.aws.amazon.com/kms/latest/developerguide/multi-region-keys-overview.html

## Notes for AI Agents

When using this module:

1. **Enable Rotation**: Set `enable_key_rotation = true` for symmetric keys (not supported for asymmetric)
2. **Use Separate Keys**: Create dedicated keys per service/environment for security isolation
3. **Implement Tagging**: Always add Environment, Owner, and purpose tags
4. **Set Deletion Window**: Use `deletion_window_in_days = 30` for production
5. **Reference by Alias**: Use aliases in application configs to allow key rotation without code changes
6. **Handle Asymmetric Keys**: Remember rotation is not supported; plan lifecycle accordingly
7. **Service Integration**: Use `key_service_users` for AWS service principals (CloudWatch, S3, etc.)
8. **Cross-Account Access**: Add policies via `source_policy_documents` for cross-account scenarios
9. **BYOK Compliance**: Use `create_external = true` with `key_material_base64` for imported keys
10. **Multi-Region HA**: Use `multi_region = true` for global applications requiring failover
