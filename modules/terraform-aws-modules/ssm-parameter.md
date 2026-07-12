# Terraform AWS SSM Parameter Module

## Module Information

- **Module Name**: `ssm-parameter`
- **Module ID**: `terraform-aws-modules/ssm-parameter/aws`
- **Source**: `terraform-aws-modules/ssm-parameter/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ssm-parameter
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ssm-parameter/aws/latest
- **Latest Version**: 2.1.1
- **Purpose**: Terraform module that creates and manages AWS Systems Manager (SSM) Parameter Store parameters for secure configuration and secrets management
- **Service**: AWS Systems Manager Parameter Store
- **Category**: Configuration Management, Secrets Management, Security
- **Keywords**: ssm, parameter-store, systems-manager, configuration, secrets, secure-string, kms-encryption, credentials, write-only, string, stringlist, securestring, wrapper
- **Use For**: Application configuration management, secrets and credentials storage, environment-specific settings, database connection strings, API keys and tokens, feature flags, microservices configuration, AMI ID parameters

## Description

This Terraform module creates and manages AWS Systems Manager (SSM) Parameter Store parameters for centralized configuration and secrets management. It supports all three parameter types (String, StringList, SecureString) with automatic type detection from the arguments supplied, and native `for_each` support for bulk parameter creation from a single module block.

Key capabilities include KMS encryption for SecureString parameters, parameter tiers (Standard up to 4KB free, Advanced up to 8KB paid, Intelligent-Tiering for automatic optimization), regex validation via `allowed_pattern`, and AWS integration data types (`aws:ec2:image`, `aws:ssm:integration`). As of v2.0, the module requires Terraform >= 1.11 and AWS provider >= 6.28 because SecureString values are written using the provider's write-only argument (`value_wo` / `value_wo_version`) instead of the plain `value` attribute, so secret content is never persisted in Terraform state. The `ignore_value_changes` option lets Terraform manage a parameter's metadata while leaving its value untouched for parameters updated externally (Console, API, other pipelines).

Parameter Store integrates with EC2, ECS, Lambda, CloudFormation, and CodeBuild. Parameters support hierarchical naming with forward slashes (paths must start with `/`). The module also ships a `wrappers` submodule that wraps the root module with an `items`/`defaults` map interface, primarily for Terragrunt users who cannot use native `for_each` on a `terraform { source = ... }` block.

## Key Features

- **Automatic Type Detection**: Infers `String`, `StringList`, or `SecureString` from the arguments supplied (`values` → StringList, `secure_type = true` → SecureString) when `type` is omitted
- **All Three Parameter Types**: String (default), StringList (auto JSON-encoded from a `values` list), SecureString (KMS-encrypted)
- **Write-Only Secret Values**: SecureString values are set via Terraform's write-only `value_wo`/`value_wo_version` arguments (requires Terraform >= 1.11) so secrets are not stored in state
- **KMS Encryption**: SecureString uses the AWS-managed `alias/aws/ssm` key by default; specify `key_id` for a customer-managed key
- **Bulk Creation**: Native `for_each` support for managing many related parameters from one module block
- **Wrapper Submodule**: Bundled `wrappers` submodule for Terragrunt-style multi-instance management via `items`/`defaults` maps
- **Parameter Tiers**: `Standard` (free, 4KB), `Advanced` (paid, 8KB), `Intelligent-Tiering` (automatic)
- **Value Change Ignoring**: `ignore_value_changes = true` for parameters whose value is managed outside Terraform (e.g., feature flags toggled via Console/API)
- **Overwrite Control**: `overwrite` governs whether the module may adopt/overwrite a pre-existing parameter of the same name
- **Regex Validation**: `allowed_pattern` for input format validation
- **AWS-native Data Types**: `aws:ec2:image` (AMI ID validation) and `aws:ssm:integration` (Systems Manager webhook integrations)
- **Multi-Region**: Per-resource `region` argument to target a region other than the provider default
- **Conditional Creation**: `create = false` disables all resources in the module

## Main Use Cases

1. **Application Configuration**: Store settings across dev/staging/production environments
2. **Secrets Storage**: Database passwords, API keys, tokens with SecureString encryption
3. **Feature Flags**: Dynamic application behavior toggles (use `ignore_value_changes` for external management)
4. **Database Connections**: Connection strings, hostnames, ports, credentials
5. **Infrastructure Parameters**: AMI IDs (with `data_type = "aws:ec2:image"`), VPC IDs, resource ARNs
6. **Microservices Config**: Centralized configuration for distributed architectures
7. **Systems Manager Webhooks**: `aws:ssm:integration` parameters for incident/alerting integrations (e.g., Opsgenie)
8. **Terragrunt Fleets**: Managing many similar parameters per environment via the `wrappers` submodule

## Submodules

### 1. wrappers

- **Purpose**: Wraps the root module behind an `items`/`defaults` map interface so multiple parameters can be managed without native Terraform `for_each` on the module source (needed by Terragrunt)
- **Source**: `terraform-aws-modules/ssm-parameter/aws//wrappers`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/ssm-parameter/aws/latest/submodules/wrappers
- **Key Features**: Per-item overrides via `items`, shared defaults via `defaults`, no extra functionality beyond fan-out (`for_each = var.items`)
- **Use Cases**: Terragrunt configurations managing many parameters from one `terragrunt.hcl`, DRY multi-parameter Terraform stacks

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `null` | Name of the parameter. Paths (containing `/`) must start with `/` |
| `value` | `string` | `null` | Single string value for the parameter (write-only internally for `SecureString`) |
| `values` | `list(string)` | `[]` | List of values (auto-jsonencoded, triggers StringList type when `type` is omitted) |
| `type` | `string` | `null` | Parameter type: `String`, `StringList`, or `SecureString` (auto-detected if omitted) |
| `secure_type` | `bool` | `false` | Set to `true` to use SecureString type with KMS encryption |
| `key_id` | `string` | `null` | KMS key ID/ARN for SecureString encryption (uses AWS-managed key if null) |
| `value_wo_version` | `number` | `null` (module defaults to `1` for SecureString) | Must be **incremented** whenever a SecureString `value` changes, or the update will not be applied |
| `tier` | `string` | `null` | `Standard` (free, 4KB), `Advanced` (paid, 8KB), or `Intelligent-Tiering` |
| `allowed_pattern` | `string` | `null` | Regex pattern to validate parameter value |
| `data_type` | `string` | `null` | `text`, `aws:ec2:image`, or `aws:ssm:integration` |
| `description` | `string` | `null` | Description of the parameter |
| `ignore_value_changes` | `bool` | `false` | Ignore value changes for externally managed parameters |
| `overwrite` | `bool` | `null` | Overwrite an existing parameter of the same name; provider defaults to `false` on create, `true` thereafter |
| `region` | `string` | `null` | AWS region for this parameter if different from the provider's configured region |
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
| `raw_value` | Raw value as stored in SSM (before decoding), sensitive |
| `secure_value` | Sensitive parameter value, kept in a separate output from `insecure_value` |
| `insecure_value` | Non-sensitive parameter value (for String/StringList; not applicable to SecureString) |
| `secure_type` | Boolean indicating if parameter is SecureString |

## Usage Examples

### Example 1: Simple String Parameter

```hcl
module "app_environment" {
  source  = "terraform-aws-modules/ssm-parameter/aws"
  version = "~> 2.1"

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
  source  = "terraform-aws-modules/ssm-parameter/aws"
  version = "~> 2.1"

  name        = "/myapp/database/password"
  value       = var.db_password
  secure_type = true
  key_id      = aws_kms_key.ssm.id  # Optional: uses AWS-managed key if omitted

  # Bump this whenever var.db_password rotates - write-only values are
  # never diffed by content, only by this version number.
  value_wo_version = var.db_password_version

  tags = {
    Application = "myapp"
  }
}
```

### Example 3: StringList Parameter

```hcl
# Using values list (recommended - auto-detects StringList type)
module "allowed_ips" {
  source  = "terraform-aws-modules/ssm-parameter/aws"
  version = "~> 2.1"

  name   = "/myapp/allowed-ips"
  values = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

# Alternative: comma-separated string with explicit type
module "allowed_ips_alt" {
  source  = "terraform-aws-modules/ssm-parameter/aws"
  version = "~> 2.1"

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
  version  = "~> 2.1"
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
  source  = "terraform-aws-modules/ssm-parameter/aws"
  version = "~> 2.1"

  name                 = "/myapp/features/new-ui"
  value                = "false"
  ignore_value_changes = true  # Terraform won't revert external value changes

  tags = { Type = "feature-flag" }
}
```

### Example 6: AMI ID with AWS Data Type Validation

```hcl
module "ami_parameter" {
  source  = "terraform-aws-modules/ssm-parameter/aws"
  version = "~> 2.1"

  name      = "/myapp/ami/amazon-linux-2"
  value     = data.aws_ami.amazon_linux_2.id
  data_type = "aws:ec2:image"  # AWS validates this is a valid AMI ID
}
```

### Example 7: Wrapper Submodule for Multiple Parameters (Terragrunt-friendly)

```hcl
module "parameters" {
  source  = "terraform-aws-modules/ssm-parameter/aws//wrappers"
  version = "~> 2.1"

  defaults = {
    create = true
    tags   = { Environment = "dev", ManagedBy = "Terraform" }
  }

  items = {
    db_host = { name = "/myapp/db/host", value = "db.example.com" }
    db_pass = { name = "/myapp/db/password", value = var.db_password, secure_type = true }
  }
}
```

## Best Practices

### Security

1. **Use SecureString for Sensitive Data**: Set `secure_type = true` for passwords, API keys, tokens
2. **Use Custom KMS Keys**: Specify `key_id` for customer-managed key rotation control
3. **Least Privilege IAM**: Grant `GetParameter`/`GetParameters` only for specific paths
4. **Never Hardcode Secrets**: Use Terraform variables or CI/CD secrets management, not literal values in `.tf` files

### Operations (write-only SecureString values)

1. **Bump `value_wo_version` on Every Rotation**: Since `value_wo` is a write-only argument (Terraform >= 1.11), Terraform never compares its content across plans; a changed `value` on a SecureString parameter is silently ignored unless `value_wo_version` is also incremented
2. **Derive the Version Deterministically**: Use a counter variable, a timestamp, or a hash of the secret (e.g., `md5(var.db_password)`) as `value_wo_version` so rotations are automatic and reproducible
3. **Don't Rely on the Default**: The module defaults `value_wo_version` to `1` for SecureString parameters when unset, which is fine for initial creation but must be overridden for any subsequent update

### Organization

1. **Hierarchical Naming**: Use `/app/env/component/param` pattern for IAM path-based access
2. **Use for_each or the wrappers Submodule**: Manage related parameters efficiently with local maps, or use the `wrappers` submodule under Terragrunt
3. **Tag Consistently**: Include `Application`, `Environment`, `ManagedBy` tags
4. **Choose Correct Tier**: `Standard` (free, 4KB) for most; `Advanced` (8KB) only when needed
5. **Set `overwrite` Deliberately**: Set `overwrite = true` only when intentionally adopting/overwriting a parameter created outside Terraform

### Other

1. **`ignore_value_changes`**: Use for parameters managed outside Terraform (feature flags)
2. **Pattern Validation**: Use `allowed_pattern` to validate value formats
3. **Data Types**: Use `aws:ec2:image` for AMI IDs to get AWS validation
4. **Consider Secrets Manager**: For secrets requiring automatic rotation, prefer AWS Secrets Manager over Parameter Store SecureString

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ssm-parameter
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ssm-parameter/aws/latest
- **Wrappers Submodule**: https://registry.terraform.io/modules/terraform-aws-modules/ssm-parameter/aws/latest/submodules/wrappers
- **AWS Parameter Store Documentation**: https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html
- **IAM Policies for Parameter Store**: https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-access.html
- **`aws_ssm_parameter` Resource Reference**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter
- **Terraform Write-Only Arguments**: https://developer.hashicorp.com/terraform/language/resources/ephemeral#write-only-arguments

## Notes for AI Agents

**Key patterns for code generation:**

1. **Version Requirement**: Module v2.x requires Terraform >= 1.11 and AWS provider >= 6.28; pin `version = "~> 2.1"`. If the target environment cannot meet these, pin `version = "~> 1.2"` instead (older API without `value_wo`/`region`/`value_wo_version`)
2. **Type Detection**: Use `values = [...]` for StringList (auto-detects), `secure_type = true` for SecureString
3. **Critical SecureString Gotcha**: For `secure_type = true`, changing `value` alone does NOT update the parameter in AWS — always also change `value_wo_version` (increment, timestamp, or hash of the value) or the rotation will be silently skipped
4. **Paths**: Parameters with `/` must start with `/` (e.g., `/myapp/config`, not `myapp/config`)
5. **Bulk Creation**: Use `for_each` with local maps for multiple related parameters, or the `wrappers` submodule (`source = "...//wrappers"`) for Terragrunt-style `items`/`defaults` maps
6. **Sensitive Data**: Always use `secure_type = true` for passwords, tokens, API keys
7. **External Management**: Use `ignore_value_changes = true` for feature flags managed via Console/API
8. **Custom KMS**: Specify `key_id` only if a customer-managed key is required (AWS-managed key is the default)
9. **AMI Parameters**: Use `data_type = "aws:ec2:image"` for AMI ID validation
10. **Output Selection**: Use the `value` output (auto-decodes JSON) for most cases; use `raw_value`/`secure_value` only when the decoded form is not wanted
