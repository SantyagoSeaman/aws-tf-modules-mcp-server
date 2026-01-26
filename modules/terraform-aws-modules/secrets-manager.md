# Terraform AWS Secrets Manager Module

## Module Information

- **Module Name**: `secrets-manager`
- **Source**: `terraform-aws-modules/secrets-manager/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-secrets-manager
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/secrets-manager/aws/latest
- **Latest Version**: 2.1.0
- **Purpose**: Terraform module for creating and managing AWS Secrets Manager resources with support for rotation, replication, and fine-grained access control policies
- **Service**: AWS Secrets Manager
- **Category**: Security, Secrets Management
- **Keywords**: secrets-manager, secret-rotation, kms-encryption, cross-region-replication, resource-policy, random-password, secret-versioning, database-credentials, api-keys, lambda-rotation
- **Use For**: database password storage, API key management, application credentials, multi-region secret replication, automated password rotation, CI/CD secrets management, cross-account secret sharing

## Description

AWS Secrets Manager is a fully managed service for protecting access to applications, services, and IT resources. This Terraform module provides a comprehensive solution for creating, managing, and rotating secrets with support for encryption, cross-region replication, and fine-grained access control. The module simplifies storing sensitive data like database credentials, API keys, and OAuth tokens while maintaining security best practices.

The module supports multiple secret management scenarios: text-based and binary secrets, automatic random password generation, and Lambda-based rotation for supported database engines. It enables KMS encryption using either AWS-managed or customer-managed keys. Resource policies provide flexible access control with IAM principals and conditions. Cross-region replication ensures secrets availability for disaster recovery scenarios.

## Key Features

- **Secret Storage**: Store secrets as text strings (JSON, plain text) or binary data
- **Random Password Generation**: Auto-generate secure passwords with configurable length (default 32 chars) and character sets
- **KMS Encryption**: Encrypt secrets using AWS-managed or customer-managed KMS keys
- **Secret Rotation**: Enable automatic rotation via Lambda functions for databases and services
- **Cross-Region Replication**: Replicate secrets to multiple regions with per-region KMS keys
- **Resource Policies**: Define fine-grained access control with IAM policy statements
- **Block Public Access**: Prevent secrets from being publicly accessible
- **Recovery Window**: Configurable deletion grace period (0-30 days, default 30)
- **Write-Once Protection**: Protect ephemeral credentials with `secret_string_wo`
- **Lifecycle Management**: Control secret creation with boolean flags

## Main Use Cases

1. **Database Credential Management**: Store and rotate RDS/Aurora passwords with Lambda rotation
2. **API Key Storage**: Securely store third-party API keys with auto-generated passwords
3. **Cross-Account Sharing**: Share secrets across AWS accounts using resource policies
4. **Multi-Region Applications**: Replicate secrets for globally distributed applications
5. **CI/CD Pipeline Secrets**: Provide secrets to deployment pipelines without hardcoding
6. **Disaster Recovery**: Maintain encrypted backup copies in multiple regions

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls creation of all resources |
| `name` | `string` | `null` | Friendly name for the secret |
| `name_prefix` | `string` | `null` | Creates unique name with specified prefix |
| `description` | `string` | `null` | Human-readable secret description |
| `kms_key_id` | `string` | `null` | ARN/ID of custom KMS key |
| `secret_string` | `string` | `null` | Plaintext secret content |
| `secret_binary` | `string` | `null` | Base64-encoded binary secret |
| `secret_string_wo` | `string` | `null` | Write-once protected text (ephemeral) |
| `recovery_window_in_days` | `number` | `null` | Deletion grace period: 0 or 7-30 days |
| `create_random_password` | `bool` | `false` | Auto-generate random password |
| `random_password_length` | `number` | `32` | Length of generated passwords |
| `random_password_override_special` | `string` | `"!@#$%&*()-_=+[]{}<>:?"` | Special chars for passwords |
| `ignore_secret_changes` | `bool` | `false` | Ignore external secret modifications |
| `create_policy` | `bool` | `false` | Enable IAM resource policy creation |
| `policy_statements` | `map(object)` | `null` | Custom IAM policy statements |
| `block_public_policy` | `bool` | `null` | Validate policy prevents public access |
| `enable_rotation` | `bool` | `false` | Activate automated rotation |
| `rotation_lambda_arn` | `string` | `""` | Lambda ARN for rotation logic |
| `rotation_rules` | `object` | `null` | Rotation schedule configuration |
| `replica` | `map(object)` | `null` | Cross-region replication config |
| `tags` | `map(string)` | `{}` | Resource tags |

## Main Outputs

| Output | Description |
|--------|-------------|
| `secret_arn` | The ARN of the created secret |
| `secret_id` | The unique identifier of the secret |
| `secret_name` | The friendly name of the secret |
| `secret_version_id` | Identifier of the current version |
| `secret_string` | Plaintext secret content (sensitive) |
| `secret_binary` | Binary secret content (sensitive) |
| `secret_replica` | Attributes of replicas (regions, ARNs, status) |

## Usage Examples

### Basic Secret with JSON Credentials

```hcl
module "secrets_manager" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name_prefix             = "myapp-db-"
  description             = "Database credentials for MyApp"
  recovery_window_in_days = 30

  secret_string = jsonencode({
    username = "admin"
    password = "changeme"
  })

  tags = {
    Environment = "production"
    Application = "myapp"
  }
}
```

### Auto-Generated Password

```hcl
module "secrets_manager" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name                              = "api-key"
  create_random_password            = true
  random_password_length            = 64
  random_password_override_special  = "!@#$%^&*"

  tags = {
    Team = "platform"
  }
}
```

### Multi-Region Replication

```hcl
module "secrets_manager" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name          = "cross-region-secret"
  secret_string = "sensitive-data"

  replica = {
    us-east-1 = {
      region     = "us-east-1"
      kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/abc123"
    }
    us-west-2 = {
      region = "us-west-2"
    }
  }

  tags = {
    Replicated = "true"
  }
}
```

### With Resource Policy

```hcl
module "secrets_manager" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name                = "shared-secret"
  create_policy       = true
  block_public_policy = true

  policy_statements = {
    read = {
      sid     = "AllowCrossAccountRead"
      actions = [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ]
      effect = "Allow"
      principals = [{
        type        = "AWS"
        identifiers = ["arn:aws:iam::123456789012:root"]
      }]
    }
  }

  secret_string = jsonencode({
    api_key = "secret-value"
  })
}
```

### With Lambda Rotation

```hcl
module "rotated_secret" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name            = "db-credentials"
  description     = "RDS credentials with automatic rotation"
  create_policy   = true
  enable_rotation = true

  rotation_lambda_arn = aws_lambda_function.rotation.arn
  rotation_rules = {
    automatically_after_days = 30
  }

  secret_string = jsonencode({
    engine   = "mysql"
    host     = "db.example.com"
    username = "admin"
    password = "initial-password"
    dbname   = "mydb"
    port     = 3306
  })

  policy_statements = {
    lambda_rotation = {
      sid     = "AllowLambdaRotation"
      actions = [
        "secretsmanager:DescribeSecret",
        "secretsmanager:GetSecretValue",
        "secretsmanager:PutSecretValue",
        "secretsmanager:UpdateSecretVersionStage"
      ]
      effect = "Allow"
      principals = [{
        type        = "AWS"
        identifiers = [aws_lambda_function.rotation.arn]
      }]
    }
  }
}
```

### Custom KMS Encryption

```hcl
module "secrets_manager" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name        = "encrypted-secret"
  kms_key_id  = aws_kms_key.secrets.arn

  secret_string = jsonencode({
    sensitive_data = "encrypted-with-cmk"
  })

  tags = {
    Compliance = "PCI-DSS"
  }
}
```

## Best Practices

### Security

1. **Enable KMS Encryption**: Use customer-managed keys for sensitive production secrets
2. **Block Public Access**: Always set `block_public_policy = true` to prevent exposure
3. **Least Privilege**: Configure resource policies with minimum necessary permissions
4. **Use VPC Endpoints**: Access Secrets Manager through VPC endpoints for private traffic
5. **Audit Access**: Enable CloudTrail to monitor secret access patterns

### Secret Management

1. **Use JSON Format**: Store multiple credentials in JSON for easier management
2. **Descriptive Names**: Use clear naming with environment prefix (e.g., "prod-rds-admin")
3. **Set Recovery Window**: Use 30-day recovery for production, 7 days for staging
4. **Enable Rotation**: Automate credential rotation for database passwords
5. **Tag Consistently**: Apply owner, environment, and compliance tags

### Rotation

1. **Test Rotation First**: Validate Lambda rotation in non-production environments
2. **Monitor Failures**: Set up CloudWatch alarms for rotation failures
3. **Grant Proper Permissions**: Ensure Lambda has `GetSecretValue`, `PutSecretValue`, `UpdateSecretVersionStage`
4. **Use AWS Templates**: Leverage AWS-provided rotation Lambda templates for RDS/Aurora

### Replication

1. **Replicate Critical Secrets**: Enable cross-region for mission-critical applications
2. **Region-Specific KMS**: Use different KMS keys per replica region for compliance
3. **Test Failover**: Regularly test application failover using replicated secrets

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-secrets-manager
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/secrets-manager/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-secrets-manager/tree/master/examples
- **AWS Secrets Manager Documentation**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- **Secret Rotation**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html
- **Rotation Lambda Templates**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/reference_available-rotation-templates.html
- **Best Practices**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html
- **Pricing**: https://aws.amazon.com/secrets-manager/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Use `name_prefix`**: Prefer `name_prefix` over `name` for unique secret names across environments
2. **JSON Secrets**: Store credentials as JSON with `jsonencode()` for structured data
3. **KMS for Production**: Always specify `kms_key_id` for production secrets
4. **Block Public**: Set `block_public_policy = true` in all environments
5. **Recovery Window**: Use `recovery_window_in_days = 30` for production, `0` only for testing
6. **Rotation Setup**: When enabling rotation, both `rotation_lambda_arn` and `rotation_rules` are required
7. **Policy SIDs**: Ensure all policy statement SIDs are unique
8. **Name Conflicts**: Specify either `name` OR `name_prefix`, not both
9. **Secret Content**: One of `secret_string`, `secret_binary`, `secret_string_wo`, or `create_random_password` must be set
10. **Replica Deletion**: Replicas must be deleted before the primary secret
