# Terraform AWS KMS Module

## Module Information

- **Module Name**: `kms`
- **Source**: `terraform-aws-modules/kms/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-kms
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/kms/aws/latest
- **Latest Version**: 4.2.0
- **Purpose**: Creates and manages AWS KMS keys (standard, external, and multi-region primary/replica), aliases, grants, and key policies
- **Service**: AWS KMS (Key Management Service)
- **Category**: Security, Encryption
- **Keywords**: kms, encryption, cmk, key-rotation, key-policy, key-statements, multi-region, key-aliases, key-grants, byok, external-key, custom-key-store, cloudhsm, symmetric-encryption, asymmetric-encryption, hmac, dnssec, envelope-encryption
- **Use For**: encrypting S3/EBS/RDS/DynamoDB data at rest, securing Secrets Manager and Parameter Store values, envelope encryption for application data, compliance requirements (HIPAA/PCI-DSS/FedRAMP), cross-region encrypted disaster recovery, digital signing and signature verification, message authentication (HMAC), bring-your-own-key and CloudHSM-backed keys, service-specific encryption (CloudWatch Logs/SNS/SQS/Lambda), Route53 DNSSEC zone signing

## Description

This module provisions AWS KMS customer master keys (CMKs) and their supporting resources — aliases, grants, and key policies — for encrypting data across AWS services. It manages a single flat set of resources with no submodules: one `module` block creates either a standard AWS-managed-material key, an external (BYOK) key, or a multi-region primary/replica of either type, selected via `create_external`, `create_replica`, and `create_replica_external` flags.

AWS KMS uses hardware security modules (HSMs) to protect key material and integrates with most AWS services for server-side encryption. The module builds a least-privilege default key policy from separate principal lists (owners, administrators, users, service users, and per-crypto-operation users), which can be extended with custom `key_statements`, merged with `source_policy_documents`/`override_policy_documents`, or bypassed entirely with a raw `policy` JSON document. It also supports key grants for temporary delegated access, CloudHSM-backed custom key stores, and built-in policy statements for Route53 DNSSEC signing and EC2 AutoScaling encrypted-EBS use cases.

The module targets Terraform >= 1.5.7 and the AWS provider >= 6.28. Since v4.0 it uses the provider's per-resource `region` argument to create multi-region replica keys without requiring a second `provider "aws" { alias = ... }` block.

## Key Features

- **Standard, External & Multi-Region Keys**: create standard AWS-managed-material keys, external (BYOK) keys, and multi-region primary/replica keys (both standard and external) from one module
- **Symmetric, Asymmetric & HMAC Support**: `ENCRYPT_DECRYPT`, `SIGN_VERIFY`, and `GENERATE_VERIFY_MAC` key usages with RSA, ECC, HMAC, and other key specs
- **Automatic Key Rotation**: configurable rotation with a 90-2560 day period (symmetric `ENCRYPT_DECRYPT` keys only)
- **Granular Default Key Policy**: auto-generates a least-privilege policy from separate owner/administrator/user/service-user/crypto-operation principal lists
- **Custom Key Statements**: append arbitrary IAM statements via `key_statements`, or merge/override full policy documents via `source_policy_documents` / `override_policy_documents`
- **Full Policy Override**: supply a raw `policy` JSON document to bypass the module's generated policy entirely
- **Key Aliases**: static aliases plus `computed_aliases` for names derived from other resources, with optional name-prefix mode
- **Key Grants**: temporary, revocable permission delegation with encryption-context constraints
- **Multi-Region Replication**: create a primary key (`multi_region = true`) and replicas in other regions via the `region` argument, no provider aliasing required
- **External Key Material (BYOK)**: import your own 256-bit key material with optional expiration (`valid_to`), including for multi-region replicas
- **CloudHSM Custom Key Store**: back keys with a dedicated CloudHSM cluster via `custom_key_store_id`
- **Route53 DNSSEC Signing**: built-in key policy statements for DNSSEC signing, scoped to specific accounts/hosted zones
- **AutoScaling Service-Linked Role Support**: pre-built policy statements for encrypted EBS volumes launched by AutoScaling
- **Deletion Protection**: configurable 7-30 day deletion waiting period
- **Comprehensive Tagging**: consistent tags applied to keys, aliases, and grants

## Main Use Cases

1. **Data-at-Rest Encryption**: dedicated CMKs for S3, EBS, RDS, DynamoDB
2. **Secrets Management**: encrypt Secrets Manager and SSM Parameter Store values
3. **Envelope Encryption**: manage data encryption keys (DEKs) for application-level encryption
4. **Compliance**: meet HIPAA, PCI-DSS, FedRAMP, GDPR key-management controls
5. **Cross-Region Disaster Recovery**: multi-region primary/replica keys keep ciphertext usable after regional failover
6. **Digital Signatures & Verification**: asymmetric `SIGN_VERIFY` keys for code signing and document signing
7. **Message Authentication**: HMAC keys (`GENERATE_VERIFY_MAC`) for API/message integrity checks
8. **Service-Specific Encryption**: dedicated keys for CloudWatch Logs, SNS, SQS, Lambda environment variables
9. **Bring Your Own Key**: import externally generated key material for key-custody requirements
10. **Route53 DNSSEC**: sign DNS zones with a KMS-backed asymmetric key

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create KMS resources |
| `description` | `string` | `null` | Key description displayed in AWS console |
| `key_usage` | `string` | `null` (`ENCRYPT_DECRYPT`) | `ENCRYPT_DECRYPT`, `SIGN_VERIFY`, or `GENERATE_VERIFY_MAC` |
| `customer_master_key_spec` | `string` | `null` (`SYMMETRIC_DEFAULT`) | Key spec for **standard/replica** keys: `SYMMETRIC_DEFAULT`, `RSA_2048/3072/4096`, `HMAC_256`, `ECC_NIST_P256/384/521`, `ECC_SECG_P256K1` |
| `key_spec` | `string` | `null` (`SYMMETRIC_DEFAULT`) | Key spec used only for **external** keys (`create_external = true`); adds `HMAC_224/384/512`, `ML_DSA_*`, `SM2` |
| `multi_region` | `bool` | `false` | Create a multi-region primary key |
| `enable_key_rotation` | `bool` | `true` | Enable automatic key rotation (symmetric `ENCRYPT_DECRYPT` keys only) |
| `rotation_period_in_days` | `number` | `null` (365) | Custom rotation period, 90-2560 days |
| `deletion_window_in_days` | `number` | `null` (30) | Deletion wait period, 7-30 days |
| `is_enabled` | `bool` | `null` (`true`) | Whether the key is enabled |
| `enable_default_policy` | `bool` | `true` | Whether the module's generated default key policy (from `key_*` variables) is included |
| `key_owners` | `list(string)` | `[]` | IAM ARNs granted full `kms:*` permissions |
| `key_administrators` | `list(string)` | `[]` | IAM ARNs for key management (not cryptographic usage) |
| `key_users` | `list(string)` | `[]` | IAM ARNs for general Encrypt/Decrypt/GenerateDataKey/DescribeKey |
| `key_service_users` | `list(string)` | `[]` | IAM ARNs allowed to create/list/revoke grants for AWS resources |
| `key_service_roles_for_autoscaling` | `list(string)` | `[]` | AutoScaling service-linked roles for encrypted EBS volumes |
| `key_symmetric_encryption_users` / `key_hmac_users` / `key_asymmetric_public_encryption_users` / `key_asymmetric_sign_verify_users` | `list(string)` | `[]` | IAM ARNs scoped to one specific crypto operation type |
| `key_statements` | `list(object)` | `null` | Custom IAM policy statements appended to the generated policy (uses `condition`, singular, since v4.0) |
| `policy` | `string` | `null` | Raw key policy JSON; when set, it **replaces** the generated policy and all `key_*`/`enable_default_policy` inputs are ignored |
| `source_policy_documents` / `override_policy_documents` | `list(string)` | `[]` | Additional `aws_iam_policy_document` JSON merged into (or overriding, by `sid`) the generated policy |
| `bypass_policy_lockout_safety_check` | `bool` | `null` (`false`) | Skips the safety check that prevents the key from becoming unmanageable; leave `false` |
| `aliases` | `list(string)` | `[]` | Alias names (without `alias/` prefix); must be static strings, not computed values |
| `computed_aliases` | `map(object({name=string}))` | `{}` | Aliases whose name can come from a computed/upstream resource attribute |
| `aliases_use_name_prefix` | `bool` | `false` | Treat alias names as name prefixes instead of exact names |
| `grants` | `map(object)` | `null` | Grant definitions: `grantee_principal`, `operations`, `constraints` (list, not map, since v4.0), `retire_on_delete`, `retiring_principal` |
| `create_external` | `bool` | `false` | Create an external key expecting imported key material instead of AWS-generated material |
| `key_material_base64` | `string` | `null` | Base64-encoded 256-bit key material for external/replica-external keys |
| `valid_to` | `string` | `null` | RFC3339 expiration timestamp for imported external key material |
| `create_replica` / `create_replica_external` | `bool` | `false` | Create a multi-region replica of a standard or external key |
| `primary_key_arn` / `primary_external_key_arn` | `string` | `null` | Primary key ARN required when creating a standard/external replica |
| `custom_key_store_id` | `string` | `null` | ID of a KMS custom key store (e.g. CloudHSM) to hold the key instead of KMS |
| `enable_route53_dnssec` | `bool` | `false` | Attach the Route53 DNSSEC signing key policy statements |
| `route53_dnssec_sources` | `list(object({account_ids, hosted_zone_arn}))` | `null` | Accounts/hosted zones allowed to use the key for DNSSEC signing |
| `region` | `string` | `null` | AWS region for the resources, overriding the provider region (requires AWS provider >= 6.0) |
| `tags` | `map(string)` | `{}` | Tags applied to all created resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `key_arn` | The ARN of the key |
| `key_id` | The globally unique key identifier |
| `key_policy` | The IAM resource policy attached to the key |
| `key_region` | The AWS region where the key is managed |
| `aliases` | Map of created aliases and their attributes |
| `grants` | Map of created grants and their attributes (sensitive) |
| `external_key_state` | State of an external CMK (`PendingImport`, `Enabled`, etc.) |
| `external_key_usage` | The cryptographic operations the external CMK supports |
| `external_key_expiration_model` | Whether external key material expires (`KEY_MATERIAL_EXPIRES` / `KEY_MATERIAL_DOES_NOT_EXPIRE`) |

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

### CloudWatch Logs Encryption (Custom Key Statement)

```hcl
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

module "kms_cloudwatch" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  description         = "CloudWatch Logs encryption key"
  enable_key_rotation = true

  key_administrators = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/Admin"]

  # key_statements are appended to the module's generated default policy
  key_statements = [
    {
      sid     = "CloudWatchLogs"
      actions = ["kms:Encrypt*", "kms:Decrypt*", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:Describe*"]
      resources = ["*"]

      principals = [{
        type        = "Service"
        identifiers = ["logs.${data.aws_region.current.name}.amazonaws.com"]
      }]

      condition = [{
        test     = "ArnLike"
        variable = "kms:EncryptionContext:aws:logs:arn"
        values   = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:*"]
      }]
    }
  ]

  aliases = ["cloudwatch-logs/encryption"]
}
```

### Multi-Region Primary + Replica Key

```hcl
# Primary key (created in the default provider region)
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

# Replica key in another region - uses the `region` argument, no provider alias needed
module "kms_replica" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  region = "eu-west-1"

  create_replica  = true
  primary_key_arn = module.kms_primary.key_arn

  key_administrators = ["arn:aws:iam::123456789012:role/GlobalAdmin"]
  key_users          = ["arn:aws:iam::123456789012:role/GlobalApp"]

  aliases = ["global-app/replica-eu"]
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
  valid_to             = "2027-12-31T23:59:59Z"

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

  description               = "Code signing key"
  key_usage                 = "SIGN_VERIFY"
  customer_master_key_spec  = "RSA_4096" # standard key: use customer_master_key_spec, not key_spec
  enable_key_rotation       = false      # rotation is not supported for asymmetric keys

  key_administrators                = ["arn:aws:iam::123456789012:role/SecurityAdmin"]
  key_asymmetric_sign_verify_users  = ["arn:aws:iam::123456789012:role/CIPipeline"]

  aliases = ["code-signing/rsa-4096"]
}
```

### HMAC Key for Message Authentication

```hcl
module "kms_hmac" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  description               = "HMAC key for API request signing"
  key_usage                 = "GENERATE_VERIFY_MAC"
  customer_master_key_spec  = "HMAC_256"
  enable_key_rotation       = false # rotation is not supported for HMAC keys

  key_administrators = ["arn:aws:iam::123456789012:role/SecurityAdmin"]
  key_hmac_users     = ["arn:aws:iam::123456789012:role/ApiGatewayRole"]

  aliases = ["api/hmac-signing"]
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
      # constraints is a LIST of objects since v4.0 (not a bare map)
      constraints = [
        {
          encryption_context_equals = { Department = "Engineering" }
        }
      ]
    }
  }

  aliases = ["app/key-with-grants"]
}
```

### Route53 DNSSEC Signing

```hcl
data "aws_caller_identity" "current" {}

module "kms_dnssec" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 4.0"

  description               = "Route53 DNSSEC signing key"
  key_usage                 = "SIGN_VERIFY"
  customer_master_key_spec  = "ECC_NIST_P256"
  enable_key_rotation       = false

  key_administrators = ["arn:aws:iam::123456789012:role/DNSAdmin"]

  enable_route53_dnssec = true # required for the DNSSEC policy statements to be added
  route53_dnssec_sources = [
    { account_ids = [data.aws_caller_identity.current.account_id] }
  ]

  aliases = ["route53/dnssec"]
}
```

## Best Practices

### Key Design

1. **Separate Keys by Purpose**: create dedicated keys for different services and data classifications instead of one shared key
2. **Use Descriptive Aliases**: format like `alias/env/service/purpose` for easy identification; use `computed_aliases` when the name is only known after apply
3. **Enable Rotation for Symmetric Keys**: enable automatic rotation (90-365 days recommended) for `ENCRYPT_DECRYPT` symmetric keys; leave it `false` for asymmetric and HMAC keys, where AWS does not support it
4. **Plan Multi-Region Upfront**: `multi_region` cannot be changed after key creation; decide at design time and use the `region` argument for replicas rather than provider aliasing

### Security

1. **Least Privilege**: grant minimum required permissions via `key_owners`/`key_administrators`/`key_users` and the operation-specific `key_*_users` lists rather than a broad custom `policy`
2. **Separate Admin/User Roles**: key administrators should not also be listed as key users
3. **Prefer Grants for Temporary Access**: use `grants` over policy changes for short-lived or workload-scoped delegation, and set encryption-context `constraints`
4. **Know When `policy` Overrides Everything**: setting the `policy` variable disables the module's generated policy entirely, including `key_statements` and all `key_*` lists — use `key_statements`/`source_policy_documents` instead when you only need to extend, not replace, the default policy
5. **Keep the Lockout Safety Check On**: leave `bypass_policy_lockout_safety_check = false` (default) to avoid creating an unmanageable key
6. **Use the Right Key-Spec Variable**: `customer_master_key_spec` for standard/replica keys, `key_spec` only for external keys (`create_external = true`) — they are not interchangeable

### Operations

1. **Set a 30-Day Deletion Window**: for production keys, to prevent accidental permanent loss
2. **Monitor with CloudTrail**: all KMS operations are automatically logged
3. **Tag Comprehensively**: include Environment, Owner, and CostCenter tags
4. **Reference by Alias**: use aliases in application configuration so keys can be rotated or replaced without code changes

### Cost Optimization

1. **Consolidate Where Appropriate**: share keys across similar use cases instead of creating one per resource
2. **Delete Unused Keys**: schedule unused keys for deletion after confirming no dependent ciphertext remains
3. **Cache Data Keys**: cache generated data encryption keys in applications to reduce `GenerateDataKey` API calls

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-kms
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/kms/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-kms/tree/master/examples/complete
- **Upgrade Guide (v3 to v4)**: https://github.com/terraform-aws-modules/terraform-aws-kms/blob/master/docs/UPGRADE-4.0.md
- **AWS KMS Documentation**: https://docs.aws.amazon.com/kms/
- **KMS Best Practices**: https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html
- **Key Policy Reference**: https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html
- **Multi-Region Keys**: https://docs.aws.amazon.com/kms/latest/developerguide/multi-region-keys-overview.html
- **Route53 DNSSEC + KMS**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring-dnssec.html

## Notes for AI Agents

When using this module:

1. **Grants `constraints` is a LIST**: since v4.0, `grants.<key>.constraints` must be `[{ encryption_context_equals = {...} }]`, not a bare map — a common source of apply errors when copying older (v3.x) examples
2. **Key-Spec Variable Depends on Key Type**: use `customer_master_key_spec` for standard/replica keys; use `key_spec` only when `create_external = true`
3. **`policy` Fully Replaces the Generated Policy**: don't set both `policy` and `key_owners`/`key_administrators`/`key_statements` expecting them to merge — use `key_statements`, `source_policy_documents`, or `override_policy_documents` to extend the default policy instead
4. **Rotation Is Symmetric-Only**: set `enable_key_rotation = true` only for `ENCRYPT_DECRYPT` symmetric keys; always set it `false` for `SIGN_VERIFY` and `GENERATE_VERIFY_MAC` keys
5. **Aliases Must Be Static**: `aliases` uses `toset()`, so values must be literal strings; use `computed_aliases` for names derived from other resources (e.g. `aws_iam_role.lambda.name`)
6. **Multi-Region Replicas Use `region`, Not Provider Aliases**: pass `region = "<replica-region>"` directly to the module (requires AWS provider >= 6.0) instead of declaring a second aliased provider block
7. **Route53 DNSSEC Needs the Flag**: `route53_dnssec_sources` has no effect unless `enable_route53_dnssec = true` is also set
8. **Tag Consistently**: always add Environment, Owner, and purpose tags
9. **Set Deletion Window**: use `deletion_window_in_days = 30` for production keys
10. **Service Integration**: use `key_service_users` for AWS service principals that need to create grants (e.g. CloudWatch Logs, EC2); use `key_service_roles_for_autoscaling` specifically for the AutoScaling service-linked role
11. **BYOK Compliance**: use `create_external = true` with `key_material_base64` for imported key material; pair with `valid_to` if the material should expire
12. **Cross-Account Access**: add statements via `key_statements` or `source_policy_documents` for cross-account scenarios rather than hand-writing a full custom `policy`
