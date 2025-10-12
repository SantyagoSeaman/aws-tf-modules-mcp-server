---
module_name: terraform-aws-appconfig
keywords: [appconfig, configuration-management, feature-flags, dynamic-configuration, deployment-strategy, configuration-profile, application-configuration, hosted-configuration, validators, json-schema, lambda-validator, rollout, gradual-deployment, environment, canary-deployment, blue-green, configuration-validation, runtime-configuration, application-tuning, feature-toggles, a-b-testing]
---

# AWS AppConfig Terraform Module

## Module Information

- **Source**: `terraform-aws-modules/appconfig/aws`
- **Version**: 2.0.1
- **Terraform**: >= 1.0
- **AWS Provider**: >= 5.0
- **License**: Apache-2.0

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

### Configuration Profile Settings
- `config_profile_name` (string): Name of the configuration profile (default: null)
- `config_profile_description` (string): Description of the configuration profile (default: null)
- `config_profile_type` (string): Configuration type (e.g., "AWS.AppConfig.FeatureFlags") (default: null)
- `config_profile_location_uri` (string): Configuration location URI (default: "hosted")
  - Options: "hosted", S3 URI, SSM Parameter name, SSM Document ARN, Secrets Manager ARN
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
- `create_deployment_strategy` (bool): Whether to create a deployment strategy (default: false)
- `deployment_strategy_id` (string): ID of existing deployment strategy (default: null)
- `deployment_strategy_name` (string): Name of the deployment strategy (default: null)
- `deployment_strategy_description` (string): Description of the deployment strategy (default: null)
- `deployment_strategy_deployment_duration_in_minutes` (number): Deployment duration in minutes (default: null)
- `deployment_strategy_final_bake_time_in_minutes` (number): Bake time after 100% deployment (default: 0)
- `deployment_strategy_growth_factor` (number): Growth factor for exponential deployment (default: null)
- `deployment_strategy_growth_type` (string): Growth type ("LINEAR" or "EXPONENTIAL") (default: null)
- `deployment_strategy_replicate_to` (string): Replication target (default: "NONE")

### Deployment Configuration
- `deployments` (any): Map of deployment configurations for environments (default: {})
  - Each deployment specifies:
    - `deployment_strategy_id`: Strategy to use for deployment
    - `configuration_version`: Version to deploy
    - `description`: Deployment description
    - `kms_key_identifier`: KMS key for encryption

### IAM Retrieval Role
- `create_retrieval_role` (bool): Whether to create IAM retrieval role (default: false)
- `retrieval_role_name` (string): Name of the retrieval role (default: null)
- `retrieval_role_use_name_prefix` (bool): Use name prefix for role (default: false)
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

### Application and Environment Design

1. **Use Descriptive Names**: Choose clear, descriptive names for applications, environments, and configuration profiles that reflect their purpose and make them easily identifiable across teams.
2. **Separate Environments**: Create distinct environments (dev, staging, production) to enable safe testing of configuration changes before production deployment.
3. **Align with Deployment Pipeline**: Structure AppConfig environments to match your CI/CD pipeline stages for seamless integration and consistent deployment workflows.
4. **Logical Application Grouping**: Group related configuration profiles under a single application to simplify management and improve organization.
5. **Environment-Specific Monitoring**: Configure CloudWatch alarms for production environments to enable automatic rollback when issues are detected.
6. **Use Tags Consistently**: Apply comprehensive tagging strategy including environment, application, owner, and cost center for effective resource management and cost allocation.

### Configuration Profile Management

7. **Choose Appropriate Configuration Type**: Use feature flags for binary enable/disable decisions and freeform configurations for complex application settings and parameters.
8. **Prefer Hosted Configuration**: Use AppConfig hosted configuration store for new deployments as it offers the most features, versioning, and enhancements compared to external sources.
9. **Version Configuration Changes**: Increment version numbers or use semantic versioning in configuration content to track changes and enable easy rollback.
10. **Document Configuration Schema**: Maintain clear documentation of configuration structure, expected values, and impact of changes for team collaboration.
11. **Use External Sources Strategically**: Leverage S3, SSM Parameter Store, or Secrets Manager when configurations are already managed there or require specific access patterns.
12. **Separate Sensitive Data**: Store secrets and credentials in AWS Secrets Manager rather than AppConfig, referencing them from application code securely.

### Validation Strategy

13. **Always Use Validators**: Implement at least one validator (JSON Schema or Lambda) for all production configuration profiles to prevent deployment of invalid configurations.
14. **JSON Schema for Structure**: Use JSON Schema validators to enforce data types, required fields, value ranges, and structural correctness.
15. **Lambda for Business Logic**: Implement Lambda validators for complex validation rules that cannot be expressed in JSON Schema, such as cross-field validation or external system checks.
16. **Keep Lambda Validators Fast**: Ensure Lambda validators complete within the 15-second timeout by optimizing code and avoiding unnecessary external calls.
17. **Dual Validation for Critical Configs**: Use both JSON Schema and Lambda validators for mission-critical configurations requiring structural and business logic validation.
18. **Test Validators Thoroughly**: Test validation logic with both valid and invalid inputs before production use to prevent blocking legitimate configuration changes.
19. **Fail Fast on Validation**: Configure validators to fail immediately on detection of invalid configuration to prevent deployment of problematic changes.

### Deployment Strategy Selection

20. **Conservative for Production**: Use slower, more conservative deployment strategies (10-20% growth) for production environments to minimize blast radius of configuration issues.
21. **Aggressive for Non-Production**: Use faster deployment strategies (50%+ growth) for development and testing environments to accelerate testing cycles.
22. **Linear for Predictability**: Choose linear deployment strategies when consistent, predictable rollout timing is important for coordination with other activities.
23. **Exponential for Caution**: Use exponential deployment strategies to start with very small percentages (2-4%) for high-risk configuration changes.
24. **Configure Adequate Bake Time**: Set final bake time to 10-30 minutes for production deployments to allow sufficient monitoring before considering rollout complete.
25. **Align Duration with Change Window**: Match deployment duration to your maintenance windows and operational requirements for change management.
26. **Reuse Predefined Strategies**: Leverage AWS-provided predefined deployment strategies for common scenarios before creating custom strategies.

### Monitoring and Rollback

27. **Integrate CloudWatch Alarms**: Configure CloudWatch alarms monitoring critical application metrics and associate them with production environments for automatic rollback.
28. **Monitor Deployment Progress**: Track deployment status through AWS Console, CLI, or API to identify issues early during rollout.
29. **Set Appropriate Alarm Thresholds**: Configure alarm thresholds that detect real issues without triggering false positives that unnecessarily rollback valid changes.
30. **Test Rollback Procedures**: Regularly test automatic and manual rollback procedures to ensure they work correctly when needed.
31. **Enable Detailed Logging**: Activate CloudWatch Logs for AppConfig API calls through CloudTrail to maintain audit trail of all configuration changes.
32. **Review Deployment History**: Regularly review deployment logs and history to identify patterns, issues, and opportunities for improvement.

### Security and Access Control

33. **Use IAM Roles for Retrieval**: Create dedicated IAM retrieval roles with least-privilege permissions for applications to access configuration data.
34. **Restrict Configuration Updates**: Limit AppConfig write permissions (CreateConfigurationProfile, StartDeployment) to authorized personnel and CI/CD systems only.
35. **Enable Encryption in Transit**: Use HTTPS/TLS for all AppConfig API calls to protect configuration data during transmission.
36. **Encrypt Sensitive Configurations**: Use KMS encryption for configuration data containing sensitive information or credentials.
37. **Implement Permissions Boundaries**: Apply IAM permissions boundaries to retrieval roles to enforce maximum permission limits for additional security.
38. **Audit Configuration Changes**: Review CloudTrail logs regularly to audit who made configuration changes and when they were deployed.
39. **Separate Production Access**: Use separate IAM roles and policies for production configuration access with stricter controls than non-production.

### Operational Excellence

40. **Automate Configuration Deployments**: Integrate AppConfig deployments into CI/CD pipelines using Terraform, AWS CLI, or SDK for consistent, repeatable deployments.
41. **Infrastructure as Code**: Manage all AppConfig resources through Terraform to ensure version control, peer review, and reproducibility.
42. **Test in Lower Environments First**: Always test configuration changes in development and staging environments before deploying to production.
43. **Document Configuration Impact**: Maintain documentation describing what each configuration parameter controls and the impact of changing it.
44. **Implement Change Control**: Require peer review and approval for production configuration changes through pull request workflows.
45. **Use Feature Flags for Releases**: Decouple code deployments from feature releases using feature flags to enable/disable functionality independently.
46. **Gradual Feature Rollout**: Enable new features for small user segments first using multi-variant feature flags before full rollout.
47. **Monitor Application Metrics**: Track application-specific metrics (latency, error rates, resource usage) during and after configuration deployments to detect issues.

### Cost Optimization

48. **Optimize Retrieval Frequency**: Use AppConfig Agent with caching to reduce API calls and minimize retrieval costs for high-frequency access patterns.
49. **Consolidate Configuration Profiles**: Group related configurations into single profiles where appropriate to reduce the number of managed profiles and simplify retrieval.
50. **Right-Size Deployment Duration**: Balance deployment safety with cost by using appropriate deployment durations that don't unnecessarily extend monitoring periods.
51. **Clean Up Unused Resources**: Regularly review and delete unused applications, environments, and configuration profiles to avoid unnecessary costs.
52. **Use Appropriate Configuration Sources**: Choose configuration sources (hosted vs. S3 vs. SSM) based on access patterns and cost considerations for your use case.

### Feature Flag Best Practices

53. **Use Boolean Flags Correctly**: Implement simple enable/disable feature flags as boolean values for clarity and ease of management.
54. **Multi-Variant for Complex Scenarios**: Use multi-variant feature flags when testing multiple variations of a feature or implementing A/B tests.
55. **Remove Obsolete Flags**: Delete feature flags and associated code once features are fully rolled out to prevent technical debt accumulation.
56. **Document Flag Purpose**: Maintain clear documentation of what each feature flag controls, expected states, and rollout status.
57. **Default to Safe State**: Configure feature flags to default to safe, conservative values (usually "disabled") to prevent issues if retrieval fails.
58. **Flag Naming Conventions**: Use consistent naming conventions for feature flags (e.g., "enable_new_checkout", "beta_ai_features") for easy identification.

## Additional Resources

### Official Documentation
- **AWS AppConfig Documentation**: https://docs.aws.amazon.com/appconfig/
- **Terraform AWS AppConfig Module GitHub**: https://github.com/terraform-aws-modules/terraform-aws-appconfig
- **Terraform Registry - AppConfig Module**: https://registry.terraform.io/modules/terraform-aws-modules/appconfig/aws

### User Guides
- **Getting Started with AppConfig**: https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html
- **Creating Configuration and Profile**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile.html
- **Deployment Strategies**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-deployment-strategy.html
- **Configuration Validators**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile-validators.html

### Integration and Tools
- **AppConfig Agent**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-integration-lambda-extensions.html
- **AWS SDKs for AppConfig**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-integration.html
- **Feature Flags Reference**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile-feature-flags.html

### API and CLI Reference
- **AppConfig API Reference**: https://docs.aws.amazon.com/appconfig/2019-10-09/APIReference/
- **AWS CLI AppConfig Commands**: https://docs.aws.amazon.com/cli/latest/reference/appconfig/

### Best Practices and Architecture
- **AppConfig Pricing**: https://aws.amazon.com/systems-manager/pricing/#AWS_AppConfig
- **AWS Well-Architected Framework**: https://aws.amazon.com/architecture/well-architected/

### Related Services
- **AWS Systems Manager**: https://docs.aws.amazon.com/systems-manager/
- **AWS Secrets Manager**: https://docs.aws.amazon.com/secretsmanager/
- **Amazon CloudWatch**: https://docs.aws.amazon.com/cloudwatch/

## Notes for AI Agents

### Module Selection Guidance
- **Use AppConfig** when applications need dynamic configuration changes without redeployment, feature flag management, or gradual configuration rollouts with validation and rollback.
- **Use SSM Parameter Store** for simple key-value configuration storage without deployment strategies, validation, or gradual rollout requirements.
- **Use Secrets Manager** specifically for credentials, API keys, and sensitive data requiring automatic rotation and audit trails.
- **Use S3** for large configuration files, static content, or when configuration is already managed as files in version control.

### Architecture Recommendations
- For **production applications**: Always use separate environments (dev, staging, prod), implement validators, configure deployment strategies with bake time, and integrate CloudWatch alarms for automatic rollback.
- For **feature flags**: Use AppConfig.FeatureFlags configuration type with hosted configuration store, implement boolean flags for simple toggles and multi-variant for A/B testing.
- For **high-frequency retrieval**: Deploy AppConfig Agent as Lambda extension or sidecar container to cache configurations and reduce API calls and costs.
- For **multi-region applications**: Create separate AppConfig applications per region or use cross-region replication strategies for configuration synchronization.
- For **microservices**: Consider creating separate configuration profiles per service or use shared profiles with service-specific sections.

### Common Configuration Patterns
- **Development**: Single environment, fast deployment strategy (5 minutes, linear 50%), hosted configuration, JSON Schema validation.
- **Staging**: Separate environment, moderate deployment (15 minutes, linear 25%), CloudWatch alarm testing, dual validators.
- **Production**: Multiple environments, conservative deployment (60 minutes, linear 10%, 20-minute bake), CloudWatch alarms enabled, dual validators, monitoring integration.
- **Feature Flags**: Hosted feature flags configuration, immediate deployment to dev, gradual rollout (2-4 hours) to production, boolean or multi-variant based on use case.

### Deployment Strategy Selection
- **AllAtOnce** (AWS predefined): Deploy to all targets immediately; use only for development environments or emergency fixes.
- **Linear50PercentEvery30Seconds** (AWS predefined): Fast rollout for non-critical changes in non-production.
- **Canary10Percent20Minutes** (AWS predefined): Start with 10% for 20 minutes, then complete; good for production testing.
- **Custom Linear 10%**: Deploy 10% every interval; conservative approach for critical production configurations.
- **Custom Exponential 2%**: Start at 2% and double; most conservative, use for high-risk changes.

### Validator Recommendations
- **JSON Schema validators**: Use for all freeform configurations to enforce structure, data types, required fields, and value ranges.
- **Lambda validators**: Implement for business logic validation like checking database connectivity, validating against external services, or complex cross-field rules.
- **No validators**: Only acceptable for development environments and non-critical feature flags; always validate production configurations.
- **Validator performance**: Keep Lambda validators under 10 seconds execution time; optimize by caching external API calls when possible.

### Security Best Practices
- **Never hardcode credentials** in AppConfig configurations; reference Secrets Manager ARNs or SSM Parameter Store secure strings from application code.
- **Use retrieval roles** with least-privilege permissions; grant only GetConfiguration and StartConfigurationSession actions for specific applications.
- **Enable encryption** using KMS for configurations containing PII, business-critical settings, or compliance-sensitive data.
- **Audit all changes** by enabling CloudTrail logging for AppConfig API calls; review logs regularly for unauthorized access attempts.
- **Separate production access** with dedicated IAM roles, policies, and potentially separate AWS accounts for production AppConfig resources.

### Troubleshooting Tips
- **Validation failures**: Check CloudWatch Logs for detailed validation errors; test configurations locally using JSON Schema validators or Lambda invocations.
- **Deployment stuck**: Verify CloudWatch alarms are not in ALARM state; check IAM permissions for alarm monitoring role if configured.
- **Configuration not updating**: Confirm application is polling AppConfig API or AppConfig Agent cache is refreshing; check retrieval role permissions.
- **Rollback not triggering**: Verify CloudWatch alarm is associated with environment, alarm role has necessary permissions, and alarm thresholds are correctly configured.
- **Lambda validator timeout**: Optimize validator code, reduce external API calls, increase Lambda memory allocation, or consider moving to JSON Schema for structural validation.

### Cost Estimation
- **Configuration requests**: $0.10 per 10,000 requests for GetConfiguration and StartConfigurationSession API calls.
- **Feature flag requests**: $0.0001 per request for feature flag evaluations.
- **Configuration data**: First 50,000 requests free each month; costs scale with request volume.
- **Deployment overhead**: No separate charge for deployments; costs based on configuration retrievals during deployment.
- **Cost optimization**: Use AppConfig Agent caching (reduces requests by 90%+), consolidate configuration profiles, implement appropriate polling intervals (30-60 seconds typical).

### Integration Patterns
- **Lambda function**: Use AppConfig Lambda extension for cached configuration retrieval with automatic refresh.
- **ECS/EKS containers**: Deploy AppConfig Agent as sidecar container to provide local caching HTTP endpoint (localhost:2772).
- **EC2 instances**: Install AppConfig Agent as system daemon for local configuration caching and retrieval.
- **CI/CD pipeline**: Use AWS CLI or SDK to trigger configuration deployments as part of deployment workflow after code deployment.
- **Application code**: Implement AppConfig SDK integration with local caching layer for resilience to API throttling or outages.
- **Multi-account**: Use cross-account IAM roles to allow applications in one account to retrieve configurations from AppConfig in another account.
