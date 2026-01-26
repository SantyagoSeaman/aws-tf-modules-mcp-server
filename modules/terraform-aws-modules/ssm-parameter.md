# Terraform AWS SSM Parameter Module

## Module Information

- **Module Name**: `ssm-parameter`
- **Source**: `terraform-aws-modules/ssm-parameter/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ssm-parameter
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ssm-parameter/aws/latest
- **Latest Version**: 1.1.2
- **Purpose**: Terraform module that creates and manages AWS Systems Manager (SSM) Parameter Store parameters for secure configuration and secrets management
- **Service**: AWS Systems Manager Parameter Store
- **Category**: Configuration Management, Secrets Management, Security
- **Keywords**: ssm, parameter-store, systems-manager, configuration, secrets, secure-string, kms-encryption, credentials, hierarchical-storage, string, stringlist, securestring
- **Use For**: Application configuration management, secrets and credentials storage, environment-specific settings, database connection strings, API keys and tokens, feature flags, microservices configuration, AMI ID parameters

## Description

This Terraform module creates and manages AWS Systems Manager (SSM) Parameter Store parameters for centralized configuration and secrets management. It supports all three parameter types (String, StringList, SecureString) with automatic type detection and native `for_each` support for bulk parameter creation.

Key capabilities include KMS encryption for SecureString parameters, parameter tiers (Standard up to 4KB free, Advanced up to 8KB paid, Intelligent-Tiering for automatic optimization), regex validation via `allowed_pattern`, and AWS integration data types (`aws:ec2:image`, `aws:ssm:integration`). The `ignore_value_changes` option allows Terraform to manage parameters whose values are updated externally.

Parameter Store integrates with EC2, ECS, Lambda, CloudFormation, and CodeBuild. SecureString parameters use AWS KMS encryption at rest. Parameters support hierarchical naming with forward slashes (paths must start with `/`).

## Key Features

- **Three Parameter Types**: String (default), StringList (auto-detected from `values` list), SecureString (via `secure_type = true`)
- **Automatic Type Detection**: Uses `values` → StringList, `secure_type = true` → SecureString, otherwise String
- **KMS Encryption**: SecureString uses AWS-managed KMS by default; specify `key_id` for customer-managed keys
- **Bulk Creation**: Native `for_each` support for managing multiple parameters efficiently
- **Parameter Tiers**: Standard (free, 4KB), Advanced (paid, 8KB), Intelligent-Tiering (automatic)
- **Value Change Ignoring**: `ignore_value_changes = true` for parameters managed outside Terraform
- **Regex Validation**: `allowed_pattern` for input validation
- **AWS Data Types**: Support for `aws:ec2:image` and `aws:ssm:integration` data types
- **Hierarchical Paths**: Forward-slash naming (paths must start with `/`)

## Main Use Cases

1. **Application Configuration**: Store settings across dev/staging/production environments
2. **Secrets Storage**: Database passwords, API keys, tokens with SecureString encryption
3. **Feature Flags**: Dynamic application behavior toggles (use `ignore_value_changes` for external management)
4. **Database Connections**: Connection strings, hostnames, ports, credentials
5. **Infrastructure Parameters**: AMI IDs (with `data_type = "aws:ec2:image"`), VPC IDs, resource ARNs
6. **Microservices Config**: Centralized configuration for distributed architectures

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `null` | Name of the parameter. Paths (containing `/`) must start with `/` |
| `value` | `string` | `null` | Single string value for the parameter |
| `values` | `list(string)` | `[]` | List of values (auto-jsonencoded, triggers StringList type) |
| `type` | `string` | `null` | Parameter type: `String`, `StringList`, or `SecureString` |
| `secure_type` | `bool` | `false` | Set to `true` to use SecureString type with KMS encryption |
| `key_id` | `string` | `null` | KMS key ID/ARN for SecureString encryption (uses AWS-managed key if null) |
| `tier` | `string` | `null` | `Standard` (free, 4KB), `Advanced` (paid, 8KB), or `Intelligent-Tiering` |
| `allowed_pattern` | `string` | `null` | Regex pattern to validate parameter value |
| `data_type` | `string` | `null` | `text`, `aws:ec2:image`, or `aws:ssm:integration` |
| `description` | `string` | `null` | Description of the parameter |
| `ignore_value_changes` | `bool` | `false` | Ignore value changes for externally managed parameters |
| `create` | `bool` | `true` | Whether to create the SSM parameter |
| `tags` | `map(string)` | `{}` | Tags to assign to the parameter |

## Main Outputs

| Output | Description |
|--------|-------------|
| `ssm_parameter_arn` | ARN of the parameter |
| `ssm_parameter_name` | Name of the parameter |
| `ssm_parameter_type` | Type of the parameter (String/StringList/SecureString) |
| `ssm_parameter_version` | Version number of the parameter |
| `value` | Decoded parameter value (recommended for most use cases) |
| `raw_value` | Raw value as stored in SSM (before decoding) |
| `secure_value` | Secure parameter value (nonsensitive output) |
| `insecure_value` | Insecure parameter value |
| `secure_type` | Boolean indicating if parameter is SecureString |

## Usage Examples

### Example 1: Simple String Parameter

```hcl
module "app_environment" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name  = "/myapp/environment"
  value = "production"

  tags = {
    Application = "myapp"
  }
}
```

### Example 2: SecureString with Custom KMS Key

```hcl
module "database_password" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name        = "/myapp/database/password"
  value       = var.db_password
  secure_type = true
  key_id      = aws_kms_key.ssm.id  # Optional: uses AWS-managed key if omitted

  tags = {
    Application = "myapp"
  }
}
```

### Example 3: StringList Parameter

```hcl
# Using values list (recommended - auto-detects StringList type)
module "allowed_ips" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name   = "/myapp/allowed-ips"
  values = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

# Alternative: comma-separated string with explicit type
module "allowed_ips_alt" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name  = "/myapp/allowed-ips"
  value = "10.0.1.0/24,10.0.2.0/24,10.0.3.0/24"
  type  = "StringList"
}
```

### Example 4: Multiple Parameters with for_each

```hcl
locals {
  parameters = {
    "/myapp/db/host"     = { value = "db.example.com" }
    "/myapp/db/port"     = { value = "5432" }
    "/myapp/db/password" = { value = var.db_password, secure_type = true }
    "/myapp/api/key"     = { value = var.api_key, secure_type = true }
  }
}

module "parameters" {
  source   = "terraform-aws-modules/ssm-parameter/aws"
  for_each = local.parameters

  name        = each.key
  value       = each.value.value
  secure_type = try(each.value.secure_type, false)

  tags = { Application = "myapp", ManagedBy = "Terraform" }
}
```

### Example 5: Feature Flag with External Management

```hcl
# Terraform creates the parameter but value changes are managed via Console/API
module "feature_flag" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name                 = "/myapp/features/new-ui"
  value                = "false"
  ignore_value_changes = true  # Terraform won't revert external value changes

  tags = { Type = "feature-flag" }
}
```

### Example 6: AMI ID with AWS Data Type Validation

```hcl
module "ami_parameter" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name      = "/myapp/ami/amazon-linux-2"
  value     = data.aws_ami.amazon_linux_2.id
  data_type = "aws:ec2:image"  # AWS validates this is a valid AMI ID
}
```

### Example 7: Pattern Validation

```hcl
module "version" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name            = "/myapp/version"
  value           = "1.2.3"
  allowed_pattern = "^\\d+\\.\\d+\\.\\d+$"  # Validates semver format
}
```

## Best Practices

### Security

1. **Use SecureString for Sensitive Data**: Set `secure_type = true` for passwords, API keys, tokens
2. **Use Custom KMS Keys**: Specify `key_id` for customer-managed key rotation control
3. **Least Privilege IAM**: Grant GetParameter/GetParameters only for specific paths
4. **Never Hardcode Secrets**: Use Terraform variables or CI/CD secrets management

### Organization

1. **Hierarchical Naming**: Use `/app/env/component/param` pattern for IAM path-based access
2. **Use for_each**: Manage related parameters efficiently with local maps
3. **Tag Consistently**: Include Application, Environment, ManagedBy tags
4. **Choose Correct Tier**: Standard (free, 4KB) for most; Advanced (8KB) only when needed

### Operations

1. **ignore_value_changes**: Use for parameters managed outside Terraform (feature flags)
2. **Pattern Validation**: Use `allowed_pattern` to validate value formats
3. **Data Types**: Use `aws:ec2:image` for AMI IDs to get AWS validation
4. **Consider Secrets Manager**: For secrets requiring automatic rotation

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ssm-parameter
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ssm-parameter/aws/latest
- **AWS Parameter Store Documentation**: https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html
- **IAM Policies for Parameter Store**: https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-access.html

## Notes for AI Agents

**Key patterns for code generation:**

1. **Type Detection**: Use `values = [...]` for StringList (auto-detects), `secure_type = true` for SecureString
2. **Paths**: Parameters with `/` must start with `/` (e.g., `/myapp/config`, not `myapp/config`)
3. **Bulk Creation**: Use `for_each` with local maps for multiple related parameters
4. **Sensitive Data**: Always use `secure_type = true` for passwords, tokens, API keys
5. **External Management**: Use `ignore_value_changes = true` for feature flags managed via Console/API
6. **Custom KMS**: Specify `key_id` only if customer-managed key is required (AWS-managed key is default)
7. **AMI Parameters**: Use `data_type = "aws:ec2:image"` for AMI ID validation
8. **Output Selection**: Use `value` output (auto-decodes JSON) for most cases
