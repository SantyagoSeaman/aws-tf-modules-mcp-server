---
module_name: ssm-parameter
keywords: [ssm, parameter-store, systems-manager, configuration-management, secrets-management, secure-string, kms-encryption, parameters, configuration, secrets, credentials, hierarchical-storage, version-control, change-tracking, tags, compliance, audit, access-control, iam, string, stringlist, securestring, plaintext, encrypted, centralized-config, application-config]
---

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
- **Keywords**: ssm, parameter-store, systems-manager, configuration-management, secrets-management, secure-string, kms-encryption, parameters, configuration, secrets, credentials, hierarchical-storage, version-control, change-tracking, tags, compliance, audit, access-control, iam, string, stringlist, securestring, plaintext, encrypted, centralized-config, application-config
- **Use For**: Application configuration management, secrets and credentials storage, environment-specific settings management, database connection strings storage, API keys and tokens management, feature flags and toggles, centralized configuration for microservices, license key storage, third-party service credentials, infrastructure configuration parameters, AMI ID management, cross-account configuration sharing

## Description

This Terraform module provides streamlined creation and management of AWS Systems Manager (SSM) Parameter Store parameters, enabling centralized storage of configuration data and secrets in a secure, hierarchical structure. The module supports all three parameter types (String, StringList, and SecureString) with automatic type detection, flexible value handling, and options for ignoring value changes when parameters are managed externally. It simplifies the creation of multiple parameters through native Terraform `for_each` support and provides comprehensive outputs for both secure and non-secure parameter values.

AWS Systems Manager Parameter Store is a fully managed, secure, and scalable service for storing configuration data and secrets without the need to manage separate infrastructure. It separates sensitive data from code, provides version tracking for all parameter changes, enables granular access control through IAM policies, and integrates seamlessly with other AWS services like EC2, ECS, Lambda, CloudFormation, and CodeBuild. SecureString parameters leverage AWS KMS for encryption at rest, ensuring sensitive data like passwords, database credentials, and API keys remain protected while maintaining accessibility for authorized applications and users.

The module offers extensive configuration options including parameter tiers (Standard, Advanced, Intelligent-Tiering), KMS encryption keys for SecureString parameters, allowed pattern validation using regular expressions, data type specification for AWS integrations, and comprehensive tagging support. It's designed for use cases ranging from simple string values to complex hierarchical configurations for multi-environment deployments, making it ideal for storing application settings, feature flags, database connection strings, and any configuration data that needs centralized management, versioning, and secure access control.

## Key Features

- **Multiple Parameter Types**: Support for String, StringList, and SecureString parameter types
- **Automatic Type Detection**: Intelligent detection of parameter type based on `secure_type` flag and value format
- **Bulk Parameter Creation**: Native `for_each` support for creating multiple parameters efficiently
- **SecureString Encryption**: KMS encryption for sensitive data with optional custom KMS key specification
- **Parameter Tiers**: Support for Standard, Advanced, and Intelligent-Tiering parameter tiers
- **Value Flexibility**: Accept both single values and lists with automatic JSON encoding for StringList
- **Value Change Ignoring**: Option to ignore value changes for externally managed parameters
- **Pattern Validation**: Regular expression validation for parameter values via `allowed_pattern`
- **Data Type Support**: Specification of data types including text, aws:ssm:integration, and aws:ec2:image
- **Version Tracking**: Automatic versioning of all parameter changes by AWS
- **Comprehensive Outputs**: Separate outputs for secure and non-secure values with sensitivity flags
- **Hierarchical Organization**: Support for hierarchical parameter naming with forward slashes
- **Tagging Support**: Full tagging capabilities for resource organization and cost allocation
- **Conditional Creation**: Control parameter creation with boolean `create` flag
- **Description Support**: Optional parameter descriptions for documentation purposes
- **IAM Integration**: Seamless integration with IAM for granular access control
- **Cross-Service Compatibility**: Works with EC2, ECS, Lambda, CloudFormation, CodeBuild, and other AWS services

## Main Use Cases

1. **Application Configuration Management**: Store and manage application settings across multiple environments
2. **Secrets and Credentials Storage**: Securely store database passwords, API keys, and authentication tokens
3. **Environment-Specific Settings**: Manage different configurations for dev, staging, and production environments
4. **Feature Flags and Toggles**: Centralize feature flag management for dynamic application behavior
5. **Database Connection Strings**: Store and version database connection parameters securely
6. **Third-Party Integration Credentials**: Manage credentials for external service integrations
7. **Infrastructure Configuration**: Store Terraform variables, AMI IDs, and infrastructure parameters
8. **Microservices Configuration**: Centralized configuration management for distributed microservices architectures
9. **Compliance and Auditing**: Track configuration changes with built-in versioning and CloudTrail integration
10. **Cross-Account Configuration Sharing**: Share configuration parameters across AWS accounts securely

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether to create the SSM Parameter |
| `name` | `string` | `null` | Name of the SSM parameter |
| `value` | `string` | `null` | Value of the parameter |
| `values` | `list(string)` | `[]` | List of parameter values (will be JSON encoded for StringList) |
| `type` | `string` | `null` | Parameter type: `String`, `StringList`, or `SecureString` |
| `secure_type` | `bool` | `false` | Determines if the value should be treated as SecureString |
| `key_id` | `string` | `null` | KMS key ID or ARN for encrypting SecureString parameters |
| `description` | `string` | `null` | Description of the parameter |
| `tier` | `string` | `null` | Parameter tier: `Standard`, `Advanced`, or `Intelligent-Tiering` |
| `allowed_pattern` | `string` | `null` | Regular expression for parameter value validation |
| `data_type` | `string` | `null` | Parameter data type: `text`, `aws:ssm:integration`, or `aws:ec2:image` |
| `ignore_value_changes` | `bool` | `false` | Ignore changes in parameter value (useful for externally managed values) |
| `tags` | `map(string)` | `{}` | Tags to assign to the parameter |

## Main Outputs

| Output | Description |
|--------|-------------|
| `ssm_parameter_arn` | ARN of the parameter |
| `ssm_parameter_name` | Name of the parameter |
| `ssm_parameter_type` | Type of the parameter |
| `ssm_parameter_version` | Version of the parameter |
| `ssm_parameter_tags_all` | All tags used for the parameter |
| `raw_value` | Raw parameter value (sensitive) |
| `value` | Decoded parameter value (non-sensitive) |
| `insecure_value` | Insecure parameter value |
| `secure_value` | Secure parameter value (sensitive) |
| `secure_type` | Whether the parameter is a SecureString |

## Usage Examples

### Example 1: Simple String Parameter

```hcl
module "app_environment" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name  = "/myapp/environment"
  value = "production"

  tags = {
    Application = "myapp"
    Environment = "production"
  }
}
```

### Example 2: SecureString Parameter with KMS Encryption

```hcl
# Create KMS key for parameter encryption
resource "aws_kms_key" "parameter_store" {
  description             = "KMS key for SSM Parameter Store encryption"
  deletion_window_in_days = 10

  tags = {
    Name = "parameter-store-key"
  }
}

resource "aws_kms_alias" "parameter_store" {
  name          = "alias/parameter-store"
  target_key_id = aws_kms_key.parameter_store.key_id
}

# Create secure parameter
module "database_password" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name        = "/myapp/database/password"
  value       = "SuperSecretPassword123!"
  description = "Database master password"

  secure_type = true
  key_id      = aws_kms_key.parameter_store.id

  tags = {
    Application = "myapp"
    Type        = "credential"
    Encrypted   = "true"
  }
}
```

### Example 3: StringList Parameter

```hcl
# Using comma-separated string
module "allowed_ips" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name  = "/myapp/security/allowed-ips"
  value = "10.0.1.0/24,10.0.2.0/24,10.0.3.0/24"
  type  = "StringList"

  tags = {
    Application = "myapp"
    Type        = "security"
  }
}

# Using list of values (will be JSON encoded)
module "environment_list" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name   = "/myapp/environments"
  values = ["dev", "staging", "production"]

  tags = {
    Application = "myapp"
  }
}
```

### Example 4: Multiple Parameters with for_each

```hcl
locals {
  application_config = {
    "/myapp/database/host" = {
      value       = "db.example.com"
      description = "Database hostname"
    }
    "/myapp/database/port" = {
      value       = "5432"
      description = "Database port"
    }
    "/myapp/database/name" = {
      value       = "myapp_production"
      description = "Database name"
    }
    "/myapp/database/username" = {
      value       = "dbadmin"
      description = "Database username"
    }
    "/myapp/database/password" = {
      value       = "SecurePassword123!"
      description = "Database password"
      secure_type = true
    }
    "/myapp/api/key" = {
      value       = "api-key-12345"
      description = "Third-party API key"
      secure_type = true
    }
  }
}

module "app_parameters" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  for_each = local.application_config

  name        = each.key
  value       = each.value.value
  description = try(each.value.description, null)
  secure_type = try(each.value.secure_type, false)

  tags = {
    Application = "myapp"
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}
```

### Example 5: Advanced Tier with Pattern Validation

```hcl
module "version_parameter" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name            = "/myapp/version"
  value           = "1.2.3"
  description     = "Application version (semantic versioning)"
  tier            = "Advanced"
  allowed_pattern = "^\\d+\\.\\d+\\.\\d+$"  # Validates semver format

  tags = {
    Application = "myapp"
    Type        = "version"
  }
}

module "email_parameter" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name            = "/myapp/admin/email"
  value           = "admin@example.com"
  description     = "Administrator email address"
  allowed_pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

  tags = {
    Application = "myapp"
    Type        = "contact"
  }
}
```

### Example 6: Hierarchical Configuration for Multiple Environments

```hcl
locals {
  environments = ["dev", "staging", "production"]

  base_config = {
    "database/port"     = "5432"
    "database/max_conn" = "100"
    "api/timeout"       = "30"
    "api/retry_count"   = "3"
  }

  env_specific_config = {
    dev = {
      "database/host" = "dev-db.internal.example.com"
      "api/endpoint"  = "https://api-dev.example.com"
      "log_level"     = "DEBUG"
    }
    staging = {
      "database/host" = "staging-db.internal.example.com"
      "api/endpoint"  = "https://api-staging.example.com"
      "log_level"     = "INFO"
    }
    production = {
      "database/host" = "prod-db.internal.example.com"
      "api/endpoint"  = "https://api.example.com"
      "log_level"     = "WARN"
    }
  }
}

# Create base parameters for all environments
module "base_parameters" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  for_each = merge([
    for env in local.environments : {
      for key, value in local.base_config :
      "/myapp/${env}/${key}" => {
        value       = value
        environment = env
      }
    }
  ]...)

  name  = each.key
  value = each.value.value

  tags = {
    Application = "myapp"
    Environment = each.value.environment
    Type        = "base-config"
    ManagedBy   = "Terraform"
  }
}

# Create environment-specific parameters
module "env_parameters" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  for_each = merge([
    for env in local.environments : {
      for key, value in local.env_specific_config[env] :
      "/myapp/${env}/${key}" => {
        value       = value
        environment = env
      }
    }
  ]...)

  name  = each.key
  value = each.value.value

  tags = {
    Application = "myapp"
    Environment = each.value.environment
    Type        = "env-config"
    ManagedBy   = "Terraform"
  }
}
```

### Example 7: Intelligent-Tiering with External Value Management

```hcl
module "dynamic_feature_flag" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name        = "/myapp/features/new-ui-enabled"
  value       = "false"
  description = "Feature flag for new UI (managed externally)"
  tier        = "Intelligent-Tiering"

  # Ignore value changes since this is toggled via AWS Console or API
  ignore_value_changes = true

  tags = {
    Application = "myapp"
    Type        = "feature-flag"
    Managed     = "external"
  }
}
```

### Example 8: AMI ID Parameter with Data Type

```hcl
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

module "ami_parameter" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  name        = "/myapp/ami/amazon-linux-2"
  value       = data.aws_ami.amazon_linux_2.id
  description = "Latest Amazon Linux 2 AMI ID"
  data_type   = "aws:ec2:image"

  tags = {
    Application = "myapp"
    Type        = "ami"
    OS          = "amazon-linux-2"
  }
}
```

### Example 9: Conditional Parameter Creation

```hcl
variable "create_production_params" {
  description = "Whether to create production parameters"
  type        = bool
  default     = false
}

module "production_config" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  create = var.create_production_params

  name        = "/myapp/production/api-key"
  value       = "prod-api-key-value"
  description = "Production API key"
  secure_type = true

  tags = {
    Application = "myapp"
    Environment = "production"
  }
}
```

### Example 10: Integration with AWS Secrets Manager Alternative

```hcl
# Store non-rotatable secrets in Parameter Store with KMS encryption
module "service_credentials" {
  source = "terraform-aws-modules/ssm-parameter/aws"

  for_each = {
    "/myapp/services/github/token" = {
      value       = var.github_token
      description = "GitHub personal access token"
    }
    "/myapp/services/slack/webhook" = {
      value       = var.slack_webhook_url
      description = "Slack webhook URL for notifications"
    }
    "/myapp/services/datadog/api-key" = {
      value       = var.datadog_api_key
      description = "Datadog API key"
    }
  }

  name        = each.key
  value       = each.value.value
  description = each.value.description
  secure_type = true
  tier        = "Advanced"

  tags = {
    Application = "myapp"
    Type        = "service-credential"
    ManagedBy   = "Terraform"
  }
}
```

## Best Practices

### Security and Access Control

1. **Use SecureString for Sensitive Data**: Always set `secure_type = true` for passwords, API keys, tokens, and any sensitive information to ensure KMS encryption at rest.
2. **Implement Custom KMS Keys**: Use customer-managed KMS keys instead of the default AWS-managed key for better control over encryption and key rotation policies.
3. **Apply Least Privilege IAM Policies**: Grant IAM principals only the minimum required permissions (GetParameter, GetParameters) for specific parameter paths using resource-based conditions.
4. **Enable CloudTrail Logging**: Monitor parameter access and modifications through CloudTrail to maintain audit trails for compliance and security investigations.
5. **Use Parameter Hierarchies**: Organize parameters in hierarchical paths (e.g., `/app/env/component/setting`) to simplify IAM policy management and enable path-based access control.
6. **Rotate Sensitive Values**: Implement regular rotation of SecureString parameters containing credentials, either manually or through automation with Lambda functions.
7. **Avoid Hardcoding Secrets**: Never commit parameter values to version control; use variables, Terraform Cloud/Enterprise variables, or CI/CD secrets management.

### Configuration Management

1. **Establish Naming Conventions**: Use consistent, hierarchical naming patterns like `/application/environment/component/parameter` for easy organization and filtering.
2. **Document with Descriptions**: Always provide meaningful `description` values to help team members understand the parameter's purpose and usage.
3. **Use Pattern Validation**: Leverage `allowed_pattern` to validate parameter values against expected formats (e.g., email addresses, version numbers, IP ranges).
4. **Choose Appropriate Tiers**: Use Standard tier (free, up to 4KB) for most parameters; use Advanced tier (charged, up to 8KB) only when necessary; consider Intelligent-Tiering for automatic optimization.
5. **Tag Comprehensively**: Apply consistent tags including Application, Environment, ManagedBy, CostCenter, and Owner for resource tracking and cost allocation.
6. **Leverage for_each for Bulk Operations**: Use `for_each` with local maps to create and manage multiple related parameters efficiently in a single module call.

### Version Control and Change Management

1. **Enable Version Tracking**: Take advantage of automatic parameter versioning to track changes over time and enable rollback capabilities.
2. **Use ignore_value_changes Judiciously**: Only set `ignore_value_changes = true` for parameters that are intentionally managed outside Terraform (e.g., feature flags toggled via console).
3. **Implement Change Notifications**: Set up CloudWatch Events or EventBridge rules to trigger notifications when parameters are modified.
4. **Test in Lower Environments First**: Always test parameter changes in development and staging environments before applying to production.
5. **Document External Changes**: If parameters are modified outside Terraform, document the changes and reasons to maintain clear operational records.

### Performance and Optimization

1. **Use Intelligent-Tiering**: For parameters with variable access patterns, use Intelligent-Tiering to automatically optimize costs based on usage.
2. **Batch Parameter Retrieval**: In applications, use GetParameters (plural) API to retrieve multiple parameters in a single call instead of individual GetParameter calls.
3. **Implement Caching**: Cache parameter values in applications with appropriate TTL to reduce API calls and improve performance.
4. **Minimize Parameter Size**: Keep parameter values under 4KB when possible to use the free Standard tier and reduce retrieval latency.
5. **Use Parameter Labels**: Create parameter labels (aliases) to reference specific versions for gradual rollouts and canary deployments.

### Operational Excellence

1. **Separate Secrets from Configuration**: Use Parameter Store for configuration and consider AWS Secrets Manager for secrets requiring automatic rotation.
2. **Implement Disaster Recovery**: Export critical parameters to backup storage and document recovery procedures for cross-region disaster scenarios.
3. **Monitor Parameter Costs**: Track Advanced tier parameter usage and cross-region data transfer to manage costs effectively.
4. **Use Data Types for Validation**: Specify `data_type` (e.g., aws:ec2:image) to leverage AWS's built-in validation for specific parameter formats.
5. **Automate Parameter Updates**: Use CI/CD pipelines to update parameters alongside application deployments for consistent configuration management.
6. **Review Unused Parameters**: Regularly audit and delete obsolete parameters to reduce clutter and potential security exposure.

### Compliance and Auditing

1. **Enable Parameter Store Logging**: Ensure CloudTrail is enabled to log all parameter access and modifications for compliance audits.
2. **Implement Change Approval**: Require change approval processes for production parameter modifications through Terraform Cloud/Enterprise or custom workflows.
3. **Use Resource Policies**: For cross-account parameter sharing, implement resource policies with explicit allow/deny rules for fine-grained access control.
4. **Regular Access Reviews**: Periodically review IAM policies granting parameter access to ensure compliance with least privilege principles.
5. **Encrypt All Sensitive Data**: Maintain a policy that all parameters containing PII, credentials, or sensitive business data must use SecureString type.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ssm-parameter
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ssm-parameter/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-ssm-parameter/tree/master/examples
- **AWS Systems Manager Parameter Store Documentation**: https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html
- **Parameter Store Pricing**: https://aws.amazon.com/systems-manager/pricing/
- **AWS Systems Manager User Guide**: https://docs.aws.amazon.com/systems-manager/latest/userguide/
- **IAM Policies for Parameter Store**: https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-access.html
- **Parameter Store Integration Examples**: https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-about-examples.html
- **KMS Encryption for SecureString**: https://docs.aws.amazon.com/kms/latest/developerguide/services-parameter-store.html
- **CloudTrail Logging for Parameter Store**: https://docs.aws.amazon.com/systems-manager/latest/userguide/monitoring-cloudtrail-logs.html
- **Parameter Store CloudWatch Metrics**: https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-throughput.html
- **AWS Secrets Manager vs Parameter Store**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_how-services-use-secrets_PS.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Use SecureString by Default**: For any sensitive data, always set `secure_type = true` to ensure KMS encryption
2. **Leverage for_each**: Create multiple parameters efficiently using `for_each` with local maps or variables
3. **Implement Hierarchical Naming**: Use forward-slash delimited paths (e.g., `/app/env/component/param`) for better organization
4. **Apply Consistent Tags**: Include Application, Environment, ManagedBy, and Owner tags on all parameters
5. **Choose Appropriate Tiers**: Use Standard tier (free, 4KB limit) for most use cases; Advanced tier only when needed
6. **Validate Values**: Use `allowed_pattern` to enforce value formats and prevent configuration errors
7. **Document Parameters**: Always provide meaningful `description` values for team collaboration
8. **Manage Secrets Externally**: Store sensitive values in Terraform Cloud variables or CI/CD secrets, not in code
9. **Use Custom KMS Keys**: Specify `key_id` for SecureString parameters to control encryption keys
10. **Enable CloudTrail**: Ensure CloudTrail logging is enabled for audit and compliance requirements
11. **Implement IAM Least Privilege**: Grant parameter access based on specific path prefixes using IAM conditions
12. **Consider Secrets Manager**: For secrets requiring automatic rotation, use AWS Secrets Manager instead
13. **Cache Parameter Values**: In applications, cache retrieved values to reduce API calls and costs
14. **Version Awareness**: Leverage automatic versioning for rollback capabilities and change tracking
15. **Test Before Production**: Always validate parameter changes in non-production environments first
