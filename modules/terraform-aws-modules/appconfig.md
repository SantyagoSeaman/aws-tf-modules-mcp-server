# Terraform AWS AppConfig Module

## Module Information

- **Module Name**: `appconfig`
- **Module ID**: `terraform-aws-modules/appconfig/aws`
- **Source**: `terraform-aws-modules/appconfig/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-appconfig
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/appconfig/aws/latest
- **Latest Version**: 2.0.2
- **Terraform**: >= 1.0
- **AWS Provider**: >= 5.0
- **Purpose**: Create and manage an AWS AppConfig application, its environments, configuration profile, deployment strategy, and deployments for dynamic configuration and feature flag delivery
- **Service**: AWS AppConfig (Application Configuration)
- **Category**: Configuration Management, Feature Flags, DevOps
- **Keywords**: appconfig, feature-flags, configuration-management, deployment-strategy, hosted-configuration, canary-deployment, gradual-rollout, configuration-profile, environment, rollback, json-schema-validator, lambda-validator
- **Use For**: dynamic feature flag rollout, safe production configuration changes, canary/gradual configuration deployments, application settings decoupled from code, externalized config sourced from S3/SSM/Secrets Manager, automated rollback on CloudWatch alarms, multi-environment config management, operational toggles and kill switches

## Description

This Terraform module creates a single AWS AppConfig "unit of work": one application, one or more environments, one configuration profile (with optional validators), an optional hosted configuration version, a deployment strategy, and an IAM retrieval role for non-hosted configuration sources. AWS AppConfig lets applications pull configuration and feature-flag data at runtime and change it safely in production without a code deployment, using deployment strategies that roll changes out gradually and can roll back automatically on CloudWatch alarms.

The module supports two configuration profile types — `AWS.AppConfig.FeatureFlags` for boolean/multi-variant feature flags, and `AWS.Freeform` for general application settings — and five configuration sources: the AppConfig hosted store, Amazon S3, AWS Systems Manager Parameter Store, SSM Documents, and (indirectly) CodePipeline. It supports up to two validators per configuration profile (JSON Schema and/or a Lambda function) to catch malformed or semantically invalid configuration before it is deployed. Deployment strategies control the pace of rollout via linear or exponential growth, deployment duration, and a final "bake time" during which CloudWatch alarms are monitored before the rollout is considered complete.

For non-hosted sources (S3, SSM Parameter, SSM Document), the module can create a dedicated IAM "retrieval role" that AppConfig assumes to read the underlying configuration data; the role's policy is generated automatically from which source is enabled (S3 read/list, `ssm:GetParameter`, or `ssm:GetDocument`) — it is not user-authorable. No retrieval role is needed (or created) when using the hosted configuration store. The module does not ship any submodules; every resource is created directly by the root module, and it is designed to be instantiated once per application/configuration-profile combination — multiple invocations are used to manage multiple applications or multiple profiles within one application.

## Key Features

- **Application & Environment Management**: Creates the AppConfig application and one or more environments (e.g., nonprod, prod) from a single `environments` map
- **Configuration Profiles**: Supports both `AWS.AppConfig.FeatureFlags` and `AWS.Freeform` profile types
- **Multiple Configuration Sources**: Hosted store, Amazon S3, SSM Parameter Store, or SSM Document as the backing store for configuration data
- **Hosted Configuration Versions**: Creates and versions configuration content directly in AppConfig's hosted store (JSON, YAML, or free text)
- **Dual Validation**: Up to two validators per profile — JSON Schema (draft-04) and/or a Lambda function (15-second execution limit)
- **Configurable Deployment Strategy**: Linear or exponential growth, deployment duration, growth factor, and final bake time, or reference an existing/predefined AWS strategy by ID
- **Automatic Retrieval IAM Role**: Auto-generates a least-privilege IAM role + policy scoped to the enabled configuration source (S3, SSM Parameter, or SSM Document) — not created for hosted configuration
- **Automatic Rollback via CloudWatch**: Environments accept `monitor` blocks (CloudWatch alarm ARN + optional alarm role ARN) so AppConfig can halt/roll back a deployment automatically
- **Deploy-to-All-Environments Deployment**: Setting `deployment_configuration_version` triggers a deployment of the configuration to every environment defined in `environments`
- **Toggleable Creation**: `create = false` disables all resource creation for conditional module instantiation
- **Comprehensive Tagging**: Per-resource tag maps (`config_profile_tags`, `deployment_strategy_tags`, `retrieval_role_tags`, `deployment_tags`) merge with the global `tags`

## Main Use Cases

1. **Feature Flag Management**: Enable/disable application features dynamically without code deployments
2. **A/B Testing & Experimentation**: Roll multi-variant feature flags out to user segments via hosted feature-flag profiles
3. **Runtime Configuration Tuning**: Adjust timeouts, thresholds, and performance parameters in production without redeployment
4. **Canary / Gradual Deployments**: Roll configuration changes out to a small percentage of consumers first, using linear or exponential deployment strategies
5. **Automatic Rollback**: Attach CloudWatch alarms to environments so AppConfig halts a bad deployment automatically
6. **Environment Parity**: Maintain isolated dev/staging/prod configuration profiles and deployment strategies from one module call
7. **Externalized Configuration Sources**: Serve configuration already stored in S3, SSM Parameter Store, or SSM Documents through AppConfig's deployment and validation pipeline
8. **Access Control / Kill Switches**: Dynamically update IP allow-lists, operational toggles, or emergency kill switches
9. **Compliance-Validated Configuration**: Enforce structural (JSON Schema) and business-rule (Lambda) validation before any configuration reaches production

## Submodules

This module does not include submodules. It provides a single root module that creates one application, its environments, one configuration profile, an optional hosted configuration version, a deployment strategy, deployments, and (conditionally) a retrieval IAM role — instantiate the module multiple times to manage multiple applications or profiles.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether any resources are created |
| `name` | `string` | `""` | Name of the AppConfig application (1-64 chars); also used as fallback for profile/role/strategy names |
| `description` | `string` | `null` | Description of the application (max 1024 chars) |
| `environments` | `map(any)` | `{}` | Map of environments to create; each value supports `name`, `description`, `tags`, and `monitor` (map of `{ alarm_arn, alarm_role_arn }`) |
| `config_profile_name` | `string` | `null` | Configuration profile name (falls back to `name`) |
| `config_profile_type` | `string` | `null` | `AWS.AppConfig.FeatureFlags` or `AWS.Freeform` |
| `config_profile_location_uri` | `string` | `"hosted"` | Configuration location: `"hosted"`, `s3://bucket/key`, `ssm-parameter://name`, or `ssm-document://name` |
| `config_profile_retrieval_role_arn` | `string` | `null` | Existing retrieval role ARN to use instead of the module-created one |
| `config_profile_validator` | `list(map(any))` | `[]` | Up to 2 validators: `{ type = "JSON_SCHEMA" \| "LAMBDA", content = ... }` |
| `use_hosted_configuration` | `bool` | `false` | Use the AppConfig hosted store (no retrieval role created) |
| `use_s3_configuration` | `bool` | `false` | Use S3 as the configuration source |
| `use_ssm_parameter_configuration` | `bool` | `false` | Use an SSM Parameter as the configuration source |
| `use_ssm_document_configuration` | `bool` | `false` | Use an SSM Document as the configuration source |
| `s3_configuration_bucket_arn` | `string` | `null` | S3 bucket ARN (required when `use_s3_configuration = true`) |
| `s3_configuration_object_key` | `string` | `"*"` | S3 object key pattern the retrieval policy is scoped to |
| `ssm_parameter_configuration_arn` | `string` | `null` | SSM Parameter ARN (required when `use_ssm_parameter_configuration = true`) |
| `ssm_document_configuration_arn` | `string` | `null` | SSM Document ARN (required when `use_ssm_document_configuration = true`) |
| `hosted_config_version_content` | `string` | `null` | Content of the hosted configuration version |
| `hosted_config_version_content_type` | `string` | `null` | MIME type of the content (e.g., `application/json`) |
| `hosted_config_version_description` | `string` | `null` | Description of the hosted configuration version |
| `create_deployment_strategy` | `bool` | `true` | Whether to create a deployment strategy |
| `deployment_strategy_id` | `string` | `null` | Existing deployment strategy ID (used when `create_deployment_strategy = false`) |
| `deployment_strategy_name` | `string` | `null` | Deployment strategy name (falls back to `name`) |
| `deployment_strategy_deployment_duration_in_minutes` | `number` | `0` | Total rollout duration, 0-1440 minutes |
| `deployment_strategy_growth_factor` | `number` | `100` | Percentage of targets per growth interval, 1-100 |
| `deployment_strategy_growth_type` | `string` | `null` | `LINEAR` or `EXPONENTIAL` (defaults to `LINEAR` in AWS) |
| `deployment_strategy_final_bake_time_in_minutes` | `number` | `0` | Post-deployment monitoring window before rollout is final |
| `deployment_strategy_replicate_to` | `string` | `"NONE"` | `NONE` or `SSM_DOCUMENT` |
| `deployment_configuration_version` | `string` | `null` | Setting this (non-null) deploys the configuration to **every** environment in `environments`; for hosted configuration the actual hosted version number is used regardless of this value — it only acts as the trigger |
| `deployment_description` | `string` | `null` | Description applied to all created deployments |
| `create_retrieval_role` | `bool` | `true` | Whether to create the IAM retrieval role/policy (ignored — no role created — when `use_hosted_configuration = true`) |
| `retrieval_role_name` | `string` | `""` | Retrieval role name (falls back to `name`) |
| `retrieval_role_use_name_prefix` | `bool` | `true` | Use `name_prefix` instead of a fixed `name` for the role/policy |
| `retrieval_role_permissions_boundary` | `string` | `null` | Permissions boundary ARN for the retrieval role |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

**Note**: The retrieval role's IAM policy is generated automatically from the `use_s3_configuration` / `use_ssm_parameter_configuration` / `use_ssm_document_configuration` flags — there is no variable to supply custom policy statements. To attach custom permissions, create the role/policy outside the module and pass its ARN via `config_profile_retrieval_role_arn` with `create_retrieval_role = false`.

## Main Outputs

| Output | Description |
|--------|-------------|
| `application_arn` | ARN of the AppConfig application |
| `application_id` | ID of the AppConfig application |
| `environments` | Map of created `aws_appconfig_environment` resources |
| `configuration_profile_arn` | ARN of the configuration profile |
| `configuration_profile_id` | Configuration profile ID and application ID joined by `:` |
| `configuration_profile_configuration_profile_id` | Configuration profile ID alone |
| `hosted_configuration_version_arn` | ARN of the hosted configuration version (if created) |
| `hosted_configuration_version_version_number` | Version number of the hosted configuration (used when deploying) |
| `deployment_strategy_arn` | ARN of the deployment strategy |
| `deployment_strategy_id` | ID of the deployment strategy |
| `deployments` | Map of created `aws_appconfig_deployment` resources, keyed by environment |
| `retrieval_role_arn` | ARN of the created (or passed-through) retrieval role |
| `retrieval_role_name` | Name of the retrieval role |
| `retrieval_role_policy_arn` | ARN of the auto-generated retrieval role policy |

## Usage Examples

### Basic Feature Flags (Hosted Configuration)

```hcl
module "appconfig" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name        = "my-application"
  description = "Application configuration management"

  environments = {
    nonprod = {
      name        = "nonprod"
      description = "Non-production environment"
    }
    prod = {
      name        = "prod"
      description = "Production environment"
    }
  }

  config_profile_type = "AWS.AppConfig.FeatureFlags"

  use_hosted_configuration           = true
  hosted_config_version_content_type = "application/json"
  hosted_config_version_content = jsonencode({
    flags = {
      new_ui        = { name = "new_ui", description = "Enable new user interface" }
      beta_features = { name = "beta_features", description = "Enable beta features" }
    }
    values = {
      new_ui        = { enabled = false }
      beta_features = { enabled = false }
    }
    version = "1"
  })

  tags = {
    Environment = "multi"
    Application = "my-app"
  }
}
```

### Freeform Config with JSON Schema + Lambda Validation and a Conservative Rollout

```hcl
module "appconfig" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name        = "validated-config"
  description = "Application settings with dual validation"

  environments = {
    prod = {
      name = "prod"
      monitor = {
        errors = {
          alarm_arn      = aws_cloudwatch_metric_alarm.app_errors.arn
          alarm_role_arn = aws_iam_role.appconfig_monitor.arn
        }
      }
    }
  }

  config_profile_name = "app-settings"
  config_profile_type = "AWS.Freeform"

  config_profile_validator = [
    {
      type = "JSON_SCHEMA"
      content = jsonencode({
        "$schema" = "http://json-schema.org/draft-04/schema#"
        type      = "object"
        properties = {
          max_connections = { type = "integer", minimum = 1, maximum = 1000 }
          timeout_seconds = { type = "integer", minimum = 1, maximum = 300 }
        }
        required             = ["max_connections", "timeout_seconds"]
        additionalProperties = false
      })
    },
    {
      type    = "LAMBDA"
      content = aws_lambda_function.config_validator.arn
    }
  ]

  use_hosted_configuration           = true
  hosted_config_version_content_type = "application/json"
  hosted_config_version_content = jsonencode({
    max_connections = 100
    timeout_seconds = 30
  })

  # Conservative production rollout: 10% every 60 min, 20 min bake time
  deployment_strategy_name                           = "conservative-linear"
  deployment_strategy_deployment_duration_in_minutes = 60
  deployment_strategy_growth_type                    = "LINEAR"
  deployment_strategy_growth_factor                  = 10
  deployment_strategy_final_bake_time_in_minutes     = 20

  # Setting this deploys to every environment above
  deployment_configuration_version = "1"

  tags = {
    Environment = "production"
    Validated   = "true"
  }
}
```

### Configuration Sourced From S3

```hcl
module "appconfig" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name = "s3-backed-config"

  environments = {
    prod = { name = "prod" }
  }

  config_profile_name         = "external-config"
  config_profile_location_uri = "s3://${aws_s3_bucket.config.id}/config.json"

  use_s3_configuration        = true
  s3_configuration_bucket_arn = aws_s3_bucket.config.arn
  s3_configuration_object_key = "config.json"

  # Retrieval role + policy are created automatically, scoped to this bucket/key
  create_retrieval_role      = true
  retrieval_role_description = "Role for AppConfig to read S3 configuration"

  deployment_configuration_version = aws_s3_object.config.version_id

  tags = { ConfigSource = "s3" }
}

resource "aws_s3_bucket" "config" {
  bucket = "my-app-config-bucket"
}
```

### Configuration Sourced From SSM Parameter Store

```hcl
module "appconfig" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name = "ssm-backed-config"

  environments = {
    prod = { name = "prod" }
  }

  config_profile_name         = "ssm-config"
  config_profile_location_uri = "ssm-parameter://${aws_ssm_parameter.app_config.name}"

  use_ssm_parameter_configuration = true
  ssm_parameter_configuration_arn = aws_ssm_parameter.app_config.arn

  deployment_configuration_version = aws_ssm_parameter.app_config.version

  tags = { ConfigSource = "ssm" }
}

resource "aws_ssm_parameter" "app_config" {
  name  = "/myapp/config"
  type  = "String"
  value = jsonencode({ feature_enabled = true, max_retries = 3 })
}
```

## Important Gotchas

1. **No custom retrieval-role policy input**: The retrieval role's IAM policy is derived entirely from `use_s3_configuration` / `use_ssm_parameter_configuration` / `use_ssm_document_configuration`. There is no variable for arbitrary policy statements — bring your own role via `config_profile_retrieval_role_arn` + `create_retrieval_role = false` if you need custom permissions.
2. **No retrieval role for hosted configuration**: When `use_hosted_configuration = true`, `create_retrieval_role` is effectively ignored and no role/policy is created — AppConfig does not need one to read its own hosted store.
3. **`deployment_configuration_version` deploys to ALL environments**: There is no per-environment deployment map. Setting this variable to any non-null value creates a deployment for every key in `environments` using the same strategy/version. For hosted configuration, the value you pass is only used as a boolean trigger — the actual deployed version is always the current hosted configuration version.
4. **Environment `monitor` key is singular and a map**: Use `monitor = { <key> = { alarm_arn = ..., alarm_role_arn = ... } }` inside an environment object, not `monitors = [...]`.
5. **`local-exec` provisioners with `sleep`**: The module runs `sleep 5` after creating the retrieval IAM role (to allow IAM propagation) and `sleep 10` after creating the application (waiting on the retrieval role's policy attachment). This requires a shell capable of running `sleep` on the machine executing `terraform apply` and adds latency to every apply.
6. **`name` has no enforced requirement**: `name` defaults to `""` (not `null`), so Terraform will not error if it is omitted — but AWS will reject an empty application name. Always set it explicitly.
7. **Max 2 validators**: `config_profile_validator` accepts at most 2 entries (one JSON Schema, one Lambda, or two of the same type up to the limit AWS enforces).
8. **Lambda validator timeout**: AppConfig invokes Lambda validators with a hard 15-second execution limit — validator functions must complete (and return quickly) within that window.

## Best Practices

### Environment and Configuration Design

1. **Separate Environments**: Create distinct environments (e.g., nonprod, prod) matching your deployment pipeline stages for safe configuration testing.
2. **Prefer Hosted Configuration for New Work**: Use the AppConfig hosted store unless you have an existing S3/SSM source of truth — it avoids retrieval-role management entirely.
3. **Use Feature Flags for Toggles**: Use `AWS.AppConfig.FeatureFlags` for binary enable/disable decisions; use `AWS.Freeform` for structured settings.
4. **Keep Secrets Out of AppConfig**: Store credentials and API keys in AWS Secrets Manager and reference them from application code, not in AppConfig content.

### Validation

5. **Always Validate Production Profiles**: Attach at least one validator (JSON Schema or Lambda) to every production configuration profile.
6. **JSON Schema for Structure**: Enforce types, required fields, and value ranges with a JSON Schema (draft-04) validator.
7. **Lambda for Business Rules**: Use a Lambda validator (must finish within 15 seconds) for cross-field or external-system validation that JSON Schema cannot express.
8. **Dual Validation for Critical Configs**: Combine both validator types for mission-critical settings.

### Deployment Strategy

9. **Conservative Growth in Production**: Use 10-20% linear growth with a 10-30 minute bake time for production rollouts.
10. **Faster Iteration in Non-Production**: Use higher growth factors (50%+) or `AllAtOnce`-style rollouts (duration `0`, growth `100`) for dev/test.
11. **Exponential Growth for High-Risk Changes**: Start small (2-4%) and double each interval for changes with significant blast radius.
12. **Attach CloudWatch Alarms**: Add `monitor` blocks to production environments so AppConfig can halt or roll back automatically on error-rate/latency alarms.

### Security

13. **Least-Privilege Retrieval**: Let the module scope the retrieval role's policy to the exact configuration source rather than granting broad S3/SSM access elsewhere.
14. **Restrict S3/SSM Resource ARNs**: Set `s3_configuration_object_key` and use narrowly-scoped `ssm_parameter_configuration_arn` / `ssm_document_configuration_arn` values rather than wildcards.
15. **Audit with CloudTrail**: Enable CloudTrail logging for `appconfig:*` API calls to track who changed configuration and when.

### Feature Flags

16. **Default to Safe/Disabled State**: Configure new flags to default to `enabled = false` so a retrieval failure fails safe.
17. **Remove Obsolete Flags**: Delete flags (and the code branches guarding them) once a feature is fully and permanently rolled out.
18. **Use Consistent Naming**: Adopt a convention such as `enable_new_checkout` or `beta_ai_features` across all flags.

### Cost and Operations

19. **Cache with the AppConfig Agent/Extension**: Deploy the AppConfig Lambda extension or agent sidecar to cache retrieved configuration and cut `GetLatestConfiguration` API calls significantly.
20. **Consolidate Profiles**: Group related settings into fewer configuration profiles to simplify retrieval and reduce management overhead.
21. **Account for the `sleep` Provisioners**: Expect every `terraform apply` that creates a new application/retrieval role to take at least ~15 extra seconds due to the module's built-in IAM-propagation delays.

## Additional Resources

- **Module GitHub**: https://github.com/terraform-aws-modules/terraform-aws-appconfig
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-appconfig/tree/master/examples
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/appconfig/aws/latest
- **AWS AppConfig Documentation**: https://docs.aws.amazon.com/appconfig/
- **Feature Flags Guide**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile-feature-flags.html
- **Deployment Strategies**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-deployment-strategy.html
- **Configuration Validators**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile-validators.html
- **AppConfig Agent/Lambda Extension**: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-integration-lambda-extensions.html
- **AppConfig Pricing**: https://aws.amazon.com/systems-manager/pricing/#AWS_AppConfig

## Notes for AI Agents

### When to Use This Module
- **Use AppConfig** for dynamic configuration/feature-flag changes that need gradual rollout, validation, and automatic rollback without redeploying code.
- **Use SSM Parameter Store directly** for simple key-value storage with no deployment strategy or validation requirements.
- **Use Secrets Manager** for credentials or API keys that require automatic rotation.
- **Use S3** for large static files or content not needing AppConfig's deployment/validation pipeline.

### Quick Start Pattern

```hcl
module "appconfig" {
  source  = "terraform-aws-modules/appconfig/aws"
  version = "~> 2.0"

  name         = "my-app"
  environments = { prod = { name = "prod" } }

  config_profile_type                = "AWS.AppConfig.FeatureFlags"
  use_hosted_configuration           = true
  hosted_config_version_content_type = "application/json"
  hosted_config_version_content = jsonencode({
    version = "1"
    flags   = { feature_x = { name = "feature_x" } }
    values  = { feature_x = { enabled = false } }
  })

  # Omit deployment_configuration_version to only create the version
  # without deploying it yet; set it to trigger a deployment.
  deployment_configuration_version = "1"
}
```

### Deployment Strategy Quick Reference

| Strategy | Growth | Duration | Bake Time | Use Case |
|----------|--------|----------|-----------|----------|
| AllAtOnce | 100% | 0 min | 0 min | Dev / emergency only |
| Fast Linear | 50% | 10 min | 5 min | Non-production |
| Conservative | 10% | 60 min | 20 min | Production |
| Exponential | 2% doubling | 30 min | 15 min | High-risk changes |

### Common Mistakes to Avoid
1. Assuming a `deployments` map or custom retrieval-policy variable exists — neither does; see "Critical Warnings and Gotchas" above.
2. Forgetting `monitor` on production environments, leaving no path to automatic rollback.
3. Setting `hosted_config_version_content` without also setting `use_hosted_configuration = true` (the version resource is only created when that flag is set).
4. Omitting `deployment_configuration_version`, which silently skips creating any deployment (the configuration version exists but is never rolled out).
5. Storing credentials in AppConfig content instead of Secrets Manager.

### Cost Estimation
- Roughly $0.10 per 10,000 configuration requests via the AppConfig API; polling clients should use the AppConfig Agent/Lambda extension to cache results and cut request volume significantly.
