# AWS AppConfig Terraform Module

## Module Information

- **Module Name**: `appconfig`
- **Source**: `terraform-aws-modules/appconfig/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-appconfig
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/appconfig/aws/latest
- **Latest Version**: 2.0.1
- **Terraform**: >= 1.0
- **AWS Provider**: >= 5.0
- **Purpose**: Create and manage AWS AppConfig resources for dynamic application configuration and feature flags
- **Service**: AWS AppConfig (Application Configuration)
- **Category**: Configuration Management, Feature Flags, DevOps
- **Keywords**: appconfig, feature-flags, configuration-management, deployment-strategy, validation, canary-deployment, gradual-rollout, configuration-profile, environment, rollback

## Description

Terraform module that creates and manages AWS AppConfig resources for dynamic application configuration management and feature flag deployment. AWS AppConfig enables organizations to quickly and securely adjust application behavior in production environments without full code deployments, reducing the risk associated with configuration changes through controlled rollouts and automated validation. This module creates AppConfig applications, environments, configuration profiles, deployment strategies, and manages the complete lifecycle of configuration deployments.

The module supports multiple configuration types including feature flags for enabling/disabling application features and freeform configurations for general application settings. It provides comprehensive validation capabilities through JSON Schema validators and Lambda function validators to ensure configuration correctness before deployment. Configuration data can be sourced from hosted AppConfig storage, Amazon S3, AWS Systems Manager Parameter Store, SSM Documents, or AWS Secrets Manager. The module manages deployment strategies with linear or exponential growth patterns, enabling gradual rollouts with configurable deployment durations and bake times for monitoring.

AppConfig integrates with CloudWatch for monitoring and automatic rollback capabilities, IAM for access control, and AWS KMS for encryption. The module simplifies the creation of retrieval roles for accessing configuration data and supports multiple environments (development, staging, production) with separate configuration profiles and deployment strategies. This enables safe testing of configuration changes in non-production environments before deploying to production with controlled, gradual rollouts.

## Key Features

- **Application Management**: Create and manage AppConfig applications as logical containers for environments and configurations
- **Multiple Environments**: Define separate environments (dev, staging, prod) with isolated configuration deployments
- **Configuration Profiles**: Support for feature flags and freeform configuration profiles with flexible naming and descriptions
- **Hosted Configuration Storage**: Built-in hosted configuration store for centralized configuration management
- **External Configuration Sources**: Integration with S3, SSM Parameter Store, SSM Documents, Secrets Manager, and CodePipeline
- **JSON Schema Validation**: Validate configuration data structure and semantics using JSON Schema 4.X specifications
- **Lambda Validation**: Custom validation logic through Lambda functions with 15-second execution time limit
- **Deployment Strategies**: Configurable linear or exponential deployment patterns for gradual rollouts
- **Predefined Strategies**: Access to AWS-managed deployment strategies for common use cases
- **Custom Growth Patterns**: Define custom deployment duration, step percentage, and bake time settings
- **Automatic Rollback**: CloudWatch alarm integration for automatic configuration rollback on detected issues
- **Version Management**: Hosted configuration version tracking with numbered releases
- **IAM Retrieval Roles**: Automated creation of IAM roles for secure configuration data access
- **Multi-Validator Support**: Up to two validators per configuration profile for comprehensive validation
- **Feature Flag Management**: Enable/disable features with basic or multi-variant flag configurations
- **Tag Support**: Comprehensive resource tagging for cost allocation and resource management
- **Environment-Specific Deployments**: Deploy different configurations to different environments independently
- **Bake Time Configuration**: Post-deployment monitoring period before considering rollout complete

## Use Cases

- **Feature Flag Management**: Enable/disable application features dynamically without code deployments for gradual feature rollouts
- **A/B Testing**: Implement multi-variant feature flags for testing different feature implementations with user segments
- **Configuration Tuning**: Adjust application performance parameters, timeouts, and thresholds in production without downtime
- **Canary Deployments**: Roll out configuration changes to small percentages of infrastructure first to validate before wider deployment
- **Emergency Rollback**: Quickly revert configuration changes when issues are detected through CloudWatch alarms
- **Environment Parity**: Maintain consistent configuration management across development, staging, and production environments
- **Access Control Management**: Dynamically update IP whitelists, security policies, and access control lists
- **Third-Party Integration**: Manage API keys, endpoints, and integration settings for external services
- **Operational Dashboards**: Control dashboard visibility, metrics, and operational toggles centrally
- **Compliance Configuration**: Centrally manage compliance-related settings with audit trails and validation

## Submodules

This module does not contain submodules. All AppConfig resources are managed through the main module.

## Variables

### Core Configuration
- `create` (bool): Whether to create AppConfig resources (default: true)
- `tags` (map(string)): Tags to apply to all resources (default: {})
- `name` (string): Name of the AppConfig application (1-64 characters, required)
- `description` (string): Description of the AppConfig application (default: null)

### Environment Configuration
- `environments` (map(any)): Map of environment configurations (default: {})
  - Each environment can specify:
    - `name`: Environment name (required)
    - `description`: Environment description
    - `monitors`: CloudWatch alarm ARNs for monitoring
    - `tags`: Environment-specific tags

### Configuration Source Selection
- `use_hosted_configuration` (bool): Use AppConfig hosted configuration store (default: false)
- `use_s3_configuration` (bool): Use S3 as configuration source (default: false)
- `use_ssm_parameter_configuration` (bool): Use SSM Parameter Store as configuration source (default: false)
- `use_ssm_document_configuration` (bool): Use SSM Document as configuration source (default: false)
- `s3_configuration_bucket_arn` (string): S3 bucket ARN for configuration (default: null)
- `s3_configuration_object_key` (string): S3 object key pattern (default: "*")
- `ssm_parameter_configuration_arn` (string): SSM Parameter ARN (default: null)
- `ssm_document_configuration_arn` (string): SSM Document ARN (default: null)

### Configuration Profile Settings
- `config_profile_name` (string): Name of the configuration profile (default: null)
- `config_profile_description` (string): Description of the configuration profile (default: null)
- `config_profile_type` (string): Configuration type: "AWS.AppConfig.FeatureFlags" or "AWS.Freeform" (default: null)
- `config_profile_location_uri` (string): Configuration location URI (default: "hosted")
- `config_profile_retrieval_role_arn` (string): IAM role ARN for configuration retrieval (default: null)

### Configuration Profile Validators
- `config_profile_validator` (list(any)): List of validators for the configuration profile (default: [])
  - Each validator specifies:
    - `type`: Validator type ("JSON_SCHEMA" or "LAMBDA")
    - `content`: JSON Schema content or Lambda function ARN

### Hosted Configuration Version
- `hosted_config_version_content` (string): Content of the hosted configuration version (default: null)
- `hosted_config_version_content_type` (string): Content type (e.g., "application/json") (default: null)
- `hosted_config_version_description` (string): Description of the configuration version (default: null)

### Deployment Strategy Configuration
- `create_deployment_strategy` (bool): Whether to create a deployment strategy (default: true)
- `deployment_strategy_id` (string): ID of existing deployment strategy (default: null)
- `deployment_strategy_name` (string): Name of the deployment strategy (default: null)
- `deployment_strategy_description` (string): Description of the deployment strategy (default: null)
- `deployment_strategy_deployment_duration_in_minutes` (number): Deployment duration, 0-1440 minutes (default: 0)
- `deployment_strategy_final_bake_time_in_minutes` (number): Bake time after 100% deployment (default: 0)
- `deployment_strategy_growth_factor` (number): Percentage of targets per interval, 1-100 (default: 100)
- `deployment_strategy_growth_type` (string): Growth type ("LINEAR" or "EXPONENTIAL") (default: null)
- `deployment_strategy_replicate_to` (string): Replication target (default: "NONE")

### Deployment Configuration
- `deployments` (any): Map of deployment configurations for environments (default: {})
  - Each deployment specifies:
    - `environment_key`: Key from environments map
    - `deployment_strategy_id`: Strategy to use for deployment
    - `configuration_version`: Version to deploy
    - `description`: Deployment description
    - `kms_key_identifier`: KMS key for encryption
- `deployment_description` (string): Deployment description, max 1024 characters (default: null)
- `deployment_configuration_version` (string): Configuration version to deploy (default: null)

### IAM Retrieval Role
- `create_retrieval_role` (bool): Whether to create IAM retrieval role (default: true)
- `retrieval_role_name` (string): Name of the retrieval role (default: null)
- `retrieval_role_use_name_prefix` (bool): Use name prefix for role (default: true)
- `retrieval_role_path` (string): IAM role path (default: null)
- `retrieval_role_description` (string): Description of the retrieval role (default: null)
- `retrieval_role_permissions_boundary` (string): Permissions boundary ARN (default: null)
- `retrieval_role_tags` (map(string)): Tags for the retrieval role (default: {})

### IAM Retrieval Role Policy
- `create_retrieval_role_policy` (bool): Whether to create retrieval role policy (default: false)
- `retrieval_role_policy_name` (string): Name of the policy (default: null)
- `retrieval_role_policy_use_name_prefix` (bool): Use name prefix for policy (default: false)
- `retrieval_role_policy_path` (string): Policy path (default: null)
- `retrieval_role_policy_description` (string): Policy description (default: null)
- `retrieval_role_policy_statements` (any): IAM policy statements (default: {})

## Outputs

### Application Information
- `application_arn`: ARN of the AppConfig application
- `application_id`: Unique identifier for the AppConfig application

### Environment Information
- `environments`: Map of created AppConfig environments with their details

### Configuration Profile Information
- `configuration_profile_arn`: ARN of the configuration profile
- `configuration_profile_id`: Unique identifier combining application ID and configuration profile ID
- `configuration_profile_configuration_profile_id`: Configuration profile ID alone

### Hosted Configuration Version
- `hosted_configuration_version_arn`: ARN of the hosted configuration version
- `hosted_configuration_version_id`: Unique identifier combining application, profile, and version
- `hosted_configuration_version_version_number`: Version number of the hosted configuration

### Deployment Strategy
- `deployment_strategy_arn`: ARN of the deployment strategy
- `deployment_strategy_id`: Unique identifier for the deployment strategy

### Deployments
- `deployments`: Map of deployment details for each environment

### IAM Retrieval Role
- `retrieval_role_arn`: ARN of the IAM retrieval role
- `retrieval_role_id`: Name of the retrieval role
- `retrieval_role_unique_id`: Stable unique identifier for the retrieval role
- `retrieval_role_name`: Name of the retrieval role

### IAM Retrieval Role Policy
- `retrieval_role_policy_arn`: ARN of the retrieval role policy
- `retrieval_role_policy_id`: ID of the policy
- `retrieval_role_policy_name`: Name of the policy
- `retrieval_role_policy_policy`: Policy document
- `retrieval_role_policy_policy_id`: Policy ID

## Usage Examples

### Basic AppConfig Application with Feature Flags

```hcl
module "appconfig_basic" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name        = "my-application"
  description = "Application configuration management"

  # Create development and production environments
  environments = {
    dev = {
      name        = "development"
      description = "Development environment"
    }
    prod = {
      name        = "production"
      description = "Production environment"
    }
  }

  # Feature flag configuration profile
  config_profile_name        = "feature-flags"
  config_profile_description = "Application feature flags"
  config_profile_type        = "AWS.AppConfig.FeatureFlags"

  # Hosted configuration with feature flags
  hosted_config_version_content = jsonencode({
    flags = {
      new_ui = {
        name        = "new_ui"
        description = "Enable new user interface"
      }
      beta_features = {
        name        = "beta_features"
        description = "Enable beta features"
      }
    }
    values = {
      new_ui = {
        enabled = false
      }
      beta_features = {
        enabled = false
      }
    }
    version = "1"
  })
  hosted_config_version_content_type = "application/json"

  tags = {
    Environment = "multi"
    Application = "my-app"
  }
}
```

### AppConfig with JSON Schema Validator

```hcl
module "appconfig_validated" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name = "validated-config"

  environments = {
    prod = {
      name = "production"
    }
  }

  # Freeform configuration profile with validation
  config_profile_name        = "app-settings"
  config_profile_description = "Application settings"
  config_profile_location_uri = "hosted"

  # JSON Schema validator
  config_profile_validator = [
    {
      type = "JSON_SCHEMA"
      content = jsonencode({
        "$schema" = "http://json-schema.org/draft-04/schema#"
        type      = "object"
        properties = {
          max_connections = {
            type    = "integer"
            minimum = 1
            maximum = 1000
          }
          timeout_seconds = {
            type    = "integer"
            minimum = 1
            maximum = 300
          }
          api_endpoint = {
            type    = "string"
            pattern = "^https://.*"
          }
        }
        required             = ["max_connections", "timeout_seconds"]
        additionalProperties = false
      })
    }
  ]

  # Configuration content
  hosted_config_version_content = jsonencode({
    max_connections = 100
    timeout_seconds = 30
    api_endpoint    = "https://api.example.com"
  })
  hosted_config_version_content_type = "application/json"

  tags = {
    Environment = "production"
    Validated   = "true"
  }
}
```

### AppConfig with Lambda Validator

```hcl
module "appconfig_lambda_validated" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name = "custom-validated-config"

  environments = {
    prod = {
      name = "production"
    }
  }

  config_profile_name = "database-settings"

  # Lambda validator for custom validation logic
  config_profile_validator = [
    {
      type    = "LAMBDA"
      content = aws_lambda_function.config_validator.arn
    }
  ]

  hosted_config_version_content = jsonencode({
    connection_pool_size = 50
    query_timeout        = 5000
    retry_attempts       = 3
  })
  hosted_config_version_content_type = "application/json"

  tags = {
    Environment = "production"
  }
}

# Lambda function for custom validation
resource "aws_lambda_function" "config_validator" {
  filename      = "validator.zip"
  function_name = "appconfig-validator"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 15

  environment {
    variables = {
      VALIDATION_RULES = "custom"
    }
  }
}
```

### AppConfig with Custom Deployment Strategy

```hcl
module "appconfig_custom_strategy" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name = "gradual-rollout-app"

  environments = {
    prod = {
      name        = "production"
      description = "Production with monitoring"
      monitors = [
        {
          alarm_arn      = aws_cloudwatch_metric_alarm.app_errors.arn
          alarm_role_arn = aws_iam_role.appconfig_monitor.arn
        }
      ]
    }
  }

  config_profile_name = "app-config"

  hosted_config_version_content      = jsonencode({ setting = "value" })
  hosted_config_version_content_type = "application/json"

  # Create custom deployment strategy
  create_deployment_strategy                           = true
  deployment_strategy_name                             = "conservative-linear"
  deployment_strategy_description                      = "10% every 10 minutes with 20 minute bake"
  deployment_strategy_deployment_duration_in_minutes   = 60
  deployment_strategy_growth_type                      = "LINEAR"
  deployment_strategy_growth_factor                    = 10
  deployment_strategy_final_bake_time_in_minutes       = 20
  deployment_strategy_replicate_to                     = "NONE"

  tags = {
    Environment        = "production"
    DeploymentStrategy = "conservative"
  }
}
```

### AppConfig with S3 Configuration Source

```hcl
module "appconfig_s3_source" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name = "s3-backed-config"

  environments = {
    prod = {
      name = "production"
    }
  }

  config_profile_name        = "external-config"
  config_profile_location_uri = "s3://${aws_s3_bucket.config.id}/config.json"

  # IAM role for retrieving configuration from S3
  create_retrieval_role       = true
  retrieval_role_name         = "appconfig-s3-retrieval"
  retrieval_role_description  = "Role for AppConfig to access S3 configuration"

  create_retrieval_role_policy = true
  retrieval_role_policy_statements = {
    s3_read = {
      effect = "Allow"
      actions = [
        "s3:GetObject",
        "s3:GetObjectVersion"
      ]
      resources = [
        "${aws_s3_bucket.config.arn}/*"
      ]
    }
  }

  config_profile_retrieval_role_arn = module.appconfig_s3_source.retrieval_role_arn

  tags = {
    ConfigSource = "s3"
  }
}

resource "aws_s3_bucket" "config" {
  bucket = "my-app-config-bucket"
}
```

### AppConfig with SSM Parameter Store Source

```hcl
module "appconfig_ssm_source" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name = "ssm-backed-config"

  environments = {
    prod = {
      name = "production"
    }
  }

  config_profile_name        = "ssm-config"
  config_profile_location_uri = "ssm-parameter://${aws_ssm_parameter.app_config.name}"

  # IAM role for retrieving configuration from SSM
  create_retrieval_role      = true
  retrieval_role_name        = "appconfig-ssm-retrieval"

  create_retrieval_role_policy = true
  retrieval_role_policy_statements = {
    ssm_read = {
      effect = "Allow"
      actions = [
        "ssm:GetParameter",
        "ssm:GetParameters"
      ]
      resources = [
        aws_ssm_parameter.app_config.arn
      ]
    }
  }

  config_profile_retrieval_role_arn = module.appconfig_ssm_source.retrieval_role_arn

  tags = {
    ConfigSource = "ssm"
  }
}

resource "aws_ssm_parameter" "app_config" {
  name  = "/myapp/config"
  type  = "String"
  value = jsonencode({
    feature_enabled = true
    max_retries     = 3
  })
}
```

### Multi-Environment AppConfig with Deployments

```hcl
module "appconfig_multi_env" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name = "multi-environment-app"

  environments = {
    dev = {
      name        = "development"
      description = "Development environment"
    }
    staging = {
      name        = "staging"
      description = "Staging environment"
    }
    prod = {
      name        = "production"
      description = "Production environment with monitoring"
      monitors = [
        {
          alarm_arn      = aws_cloudwatch_metric_alarm.prod_errors.arn
          alarm_role_arn = aws_iam_role.appconfig_monitor.arn
        }
      ]
    }
  }

  config_profile_name = "application-config"

  hosted_config_version_content = jsonencode({
    version     = "1.0.0"
    api_timeout = 5000
    max_retries = 3
    feature_flags = {
      new_feature = true
    }
  })
  hosted_config_version_content_type = "application/json"
  hosted_config_version_description  = "Initial configuration v1.0.0"

  # Create custom deployment strategy
  create_deployment_strategy                         = true
  deployment_strategy_name                           = "staged-rollout"
  deployment_strategy_deployment_duration_in_minutes = 30
  deployment_strategy_growth_type                    = "LINEAR"
  deployment_strategy_growth_factor                  = 20
  deployment_strategy_final_bake_time_in_minutes     = 10

  # Deploy to environments
  deployments = {
    dev_deployment = {
      environment_key        = "dev"
      deployment_strategy_id = module.appconfig_multi_env.deployment_strategy_id
      configuration_version  = module.appconfig_multi_env.hosted_configuration_version_version_number
      description            = "Deploy to development"
    }
  }

  tags = {
    ManagedBy = "terraform"
  }
}
```

### AppConfig with Dual Validators

```hcl
module "appconfig_dual_validators" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name = "strictly-validated-config"

  environments = {
    prod = {
      name = "production"
    }
  }

  config_profile_name = "critical-settings"

  # Use both JSON Schema and Lambda validators
  config_profile_validator = [
    {
      type = "JSON_SCHEMA"
      content = jsonencode({
        "$schema" = "http://json-schema.org/draft-04/schema#"
        type      = "object"
        properties = {
          database_connections = {
            type    = "integer"
            minimum = 10
            maximum = 500
          }
          cache_ttl = {
            type    = "integer"
            minimum = 60
          }
        }
        required = ["database_connections", "cache_ttl"]
      })
    },
    {
      type    = "LAMBDA"
      content = aws_lambda_function.business_rules_validator.arn
    }
  ]

  hosted_config_version_content = jsonencode({
    database_connections = 100
    cache_ttl            = 300
  })
  hosted_config_version_content_type = "application/json"

  tags = {
    Validation = "strict"
  }
}
```

## Best Practices

### Environment and Configuration Design

1. **Separate Environments**: Create distinct environments (dev, staging, prod) matching CI/CD pipeline stages for safe configuration testing.
2. **Prefer Hosted Configuration**: Use AppConfig hosted configuration store for new deployments—offers best features, versioning, and AWS enhancements.
3. **Use Feature Flags for Toggles**: Use `AWS.AppConfig.FeatureFlags` type for binary enable/disable decisions; freeform for complex settings.
4. **Separate Sensitive Data**: Store secrets in AWS Secrets Manager, not AppConfig. Reference from application code.

### Validation

5. **Always Validate Production**: Implement at least one validator (JSON Schema or Lambda) for all production configuration profiles.
6. **JSON Schema for Structure**: Enforce data types, required fields, value ranges with JSON Schema 4.X validators.
7. **Lambda for Business Logic**: Use Lambda validators (max 15s) for cross-field validation or external system checks.
8. **Dual Validation for Critical**: Use both validators for mission-critical configurations requiring structural and business logic validation.

### Deployment Strategies

9. **Conservative for Production**: Use 10-20% linear growth with 10-30 minute bake time for production deployments.
10. **Fast for Non-Production**: Use 50%+ growth or AllAtOnce for development environments.
11. **Exponential for High-Risk**: Start at 2-4% and double for high-risk configuration changes.
12. **Integrate CloudWatch Alarms**: Associate alarms with production environments for automatic rollback on detected issues.

### Security

13. **Use Retrieval Roles**: Create dedicated IAM retrieval roles with least-privilege permissions (GetConfiguration, StartConfigurationSession).
14. **Encrypt with KMS**: Use KMS encryption for configurations containing PII or compliance-sensitive data.
15. **Separate Production Access**: Use dedicated IAM roles/policies for production with stricter controls.
16. **Audit Changes**: Enable CloudTrail logging for all AppConfig API calls.

### Feature Flags

17. **Default to Safe State**: Configure flags to default to "disabled" to prevent issues if retrieval fails.
18. **Remove Obsolete Flags**: Delete feature flags and code once fully rolled out to prevent technical debt.
19. **Use Consistent Naming**: Follow conventions like "enable_new_checkout" or "beta_ai_features".

### Cost Optimization

20. **Use AppConfig Agent**: Deploy as Lambda extension or sidecar container to cache configs and reduce API calls by 90%+.
21. **Consolidate Profiles**: Group related configurations to reduce managed profiles and simplify retrieval.
22. **Clean Up Unused Resources**: Regularly delete unused applications, environments, and configuration profiles.

## Additional Resources

- **Module GitHub**: https://github.com/terraform-aws-modules/terraform-aws-appconfig
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/appconfig/aws/latest
- **AWS AppConfig Documentation**: https://docs.aws.amazon.com/appconfig/
- **Feature Flags Guide**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile-feature-flags.html
- **Deployment Strategies**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-deployment-strategy.html
- **Configuration Validators**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile-validators.html
- **AppConfig Agent (Lambda Extension)**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-integration-lambda-extensions.html
- **AppConfig Pricing**: https://aws.amazon.com/systems-manager/pricing/#AWS_AppConfig

## Notes for AI Agents

### When to Use This Module
- **Use AppConfig** for dynamic configuration changes without redeployment, feature flags, or gradual rollouts with validation
- **Use SSM Parameter Store** for simple key-value storage without deployment strategies or validation
- **Use Secrets Manager** for credentials, API keys requiring automatic rotation
- **Use S3** for large configuration files or static content

### Quick Start Patterns

**Basic Feature Flags**:
```hcl
module "appconfig" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name                       = "my-app"
  environments               = { prod = { name = "production" } }
  config_profile_type        = "AWS.AppConfig.FeatureFlags"
  use_hosted_configuration   = true
  hosted_config_version_content_type = "application/json"
  hosted_config_version_content = jsonencode({
    version = "1"
    flags   = { feature_x = { name = "feature_x" } }
    values  = { feature_x = { enabled = false } }
  })
}
```

**Production with Gradual Rollout**:
```hcl
module "appconfig" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name = "prod-app"
  environments = {
    prod = {
      name     = "production"
      monitors = [{ alarm_arn = aws_cloudwatch_metric_alarm.errors.arn, alarm_role_arn = aws_iam_role.monitor.arn }]
    }
  }

  use_hosted_configuration                           = true
  hosted_config_version_content_type                 = "application/json"
  hosted_config_version_content                      = jsonencode({ setting = "value" })
  deployment_strategy_name                           = "conservative"
  deployment_strategy_deployment_duration_in_minutes = 60
  deployment_strategy_growth_type                    = "LINEAR"
  deployment_strategy_growth_factor                  = 10
  deployment_strategy_final_bake_time_in_minutes     = 20
}
```

### Deployment Strategy Quick Reference
| Strategy | Growth | Duration | Bake Time | Use Case |
|----------|--------|----------|-----------|----------|
| AllAtOnce | 100% | 0 min | 0 min | Dev/emergency only |
| Fast Linear | 50% | 10 min | 5 min | Non-production |
| Conservative | 10% | 60 min | 20 min | Production |
| Exponential | 2% double | 30 min | 15 min | High-risk changes |

### Common Mistakes to Avoid
1. **No validators in production**: Always add JSON Schema or Lambda validators
2. **Credentials in AppConfig**: Store in Secrets Manager, reference from code
3. **Missing CloudWatch alarms**: Production environments need alarm integration for rollback
4. **No bake time**: Always set 10-30 minute bake time for production deployments
5. **Ignoring retrieval role**: Create least-privilege IAM roles for configuration access

### Cost Estimation
- ~$0.10 per 10,000 configuration requests
- First 50,000 requests/month free
- Use AppConfig Agent caching to reduce costs by 90%+
