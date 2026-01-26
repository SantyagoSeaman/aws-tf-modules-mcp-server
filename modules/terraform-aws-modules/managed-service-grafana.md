# Terraform AWS Managed Service for Grafana Module

## Module Information

- **Module Name**: `managed-service-grafana`
- **Source**: `terraform-aws-modules/managed-service-grafana/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-grafana
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/managed-service-grafana/aws/latest
- **Latest Version**: 2.3.1
- **Purpose**: Terraform module that creates and manages AWS Managed Service for Grafana (AMG) workspaces and related resources
- **Service**: AWS Managed Grafana (Amazon Managed Service for Grafana)
- **Category**: Monitoring, Observability, Analytics
- **Keywords**: grafana, amg, grafana-workspace, monitoring, observability, dashboard, visualization, cloudwatch, prometheus, x-ray, aws-sso, saml, api-key, service-account, vpc-configuration, data-source
- **Use For**: centralized metrics visualization, multi-source dashboard creation, CloudWatch metrics analysis, Prometheus data visualization, distributed tracing with X-Ray, enterprise observability platforms, team collaboration dashboards, IoT data monitoring, log analytics visualization, application performance monitoring, infrastructure monitoring, business intelligence dashboards

## Description

The AWS Managed Service for Grafana Terraform module provides a comprehensive solution for deploying and managing fully managed Grafana workspaces in AWS. Amazon Managed Grafana is a fully managed service that allows you to query, correlate, and visualize operational metrics, logs, and traces from multiple data sources without the operational overhead of managing Grafana servers. The module handles all aspects of workspace configuration including authentication providers, data source integrations, network access controls, IAM role management, and license management.

This module simplifies the deployment of Grafana workspaces by providing declarative configuration for critical features such as AWS SSO and SAML authentication, VPC integration, security group management, and API key provisioning. It supports both service-managed and customer-managed permission models, allowing organizations to choose the appropriate level of control for their security requirements. The module also handles workspace service accounts and tokens, enabling programmatic access for automation and CI/CD workflows.

The module integrates seamlessly with AWS native data sources including CloudWatch, Managed Service for Prometheus, X-Ray, OpenSearch Service, IoT SiteWise, and Timestream, while also supporting open-source and third-party data sources. It provides comprehensive IAM role and policy management, automatically creating and configuring the necessary permissions for Grafana to access your AWS resources. With built-in support for enterprise licensing, network access controls, and security best practices, this module enables organizations to quickly deploy production-ready Grafana environments that meet corporate governance and compliance requirements.

## Key Features

- **Workspace Management**: Complete lifecycle management of AWS Managed Grafana workspaces with customizable names, descriptions, and Grafana versions
- **Authentication Providers**: Support for AWS SSO (IAM Identity Center) and SAML 2.0 authentication with detailed configuration options
- **Data Source Integration**: Native support for CloudWatch, Prometheus, X-Ray, OpenSearch, Timestream, IoT SiteWise, and third-party data sources
- **Permission Models**: Flexible permission management with service-managed (single account and organization) and customer-managed options
- **IAM Role Management**: Automatic creation and configuration of IAM roles with customizable policies, paths, and permission boundaries
- **Network Access Control**: Configurable network access restrictions with support for IP ranges and VPN/Direct Connect integration
- **VPC Configuration**: Private subnet integration with custom security group rules for secure workspace deployment
- **Security Group Management**: Automated security group creation with customizable ingress and egress rules
- **API Key Management**: Support for creating multiple workspace API keys with different permission levels (viewer, editor, admin)
- **Service Accounts**: Workspace service account and token management for programmatic access and automation
- **SAML Configuration**: Comprehensive SAML 2.0 configuration with support for assertion attributes, role mapping, and allowed organizations
- **License Management**: Support for ENTERPRISE, ENTERPRISE_FREE_TRIAL license types with automatic association
- **Notification Destinations**: Configuration for SNS notifications and other alert destinations
- **Account Access Control**: Support for CURRENT_ACCOUNT, ORGANIZATION, and cross-account access patterns
- **Tagging Support**: Comprehensive tagging for workspaces, IAM roles, security groups, and related resources
- **Workspace Versioning**: Ability to specify and manage specific Grafana versions
- **CloudWatch Integration**: Built-in CloudWatch metrics and logging for workspace monitoring
- **Multi-Region Support**: Deploy workspaces across multiple AWS regions for disaster recovery and compliance
- **Role Association**: Configure Grafana user and group role assignments for fine-grained access control
- **Session Configuration**: Customizable IAM role session duration for security and user experience balance

## Main Use Cases

1. **Centralized Metrics Visualization**: Create unified dashboards aggregating metrics from CloudWatch, Prometheus, and custom data sources
2. **Multi-Account Observability**: Deploy organization-wide Grafana workspaces with cross-account data source access
3. **Application Performance Monitoring**: Visualize application traces from X-Ray, metrics from CloudWatch, and logs from OpenSearch
4. **Infrastructure Monitoring**: Monitor AWS infrastructure across multiple services with real-time dashboards
5. **IoT Data Visualization**: Create dashboards for IoT SiteWise industrial data and time-series analytics
6. **Team Collaboration Platforms**: Deploy shared Grafana workspaces with SSO authentication for engineering teams
7. **Security Operations Centers**: Build SOC dashboards aggregating security metrics, GuardDuty findings, and CloudTrail logs
8. **Business Intelligence**: Visualize business metrics from Timestream and other data sources for executive reporting
9. **DevOps Automation**: Provision API keys and service accounts for CI/CD pipelines and infrastructure automation
10. **Compliance Monitoring**: Create compliance dashboards with audit trails, network access controls, and SAML authentication

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `create_workspace` | `bool` | `true` | Determines whether to create Grafana workspace |
| `name` | `string` | `null` | Name of the Grafana workspace |
| `description` | `string` | `null` | Description of the Grafana workspace |
| `account_access_type` | `string` | `"CURRENT_ACCOUNT"` | Type of account access (CURRENT_ACCOUNT, ORGANIZATION) |
| `authentication_providers` | `list(string)` | `["AWS_SSO"]` | List of authentication providers (AWS_SSO, SAML) |
| `permission_type` | `string` | `"SERVICE_MANAGED"` | Permission type (SERVICE_MANAGED, CUSTOMER_MANAGED) |
| `data_sources` | `list(string)` | `[]` | List of data sources (CLOUDWATCH, PROMETHEUS, XRAY, ATHENA, OPENSEARCH_SERVICE, REDSHIFT, SITEWISE, TIMESTREAM) |
| `notification_destinations` | `list(string)` | `[]` | List of notification destinations (SNS) |
| `grafana_version` | `string` | `null` | Version of Grafana to support |
| `network_access_control` | `any` | `{}` | Network access control configuration |
| `vpc_configuration` | `any` | `{}` | VPC configuration for the workspace |
| `create_iam_role` | `bool` | `true` | Whether to create IAM role for workspace |
| `iam_role_name` | `string` | `null` | Name to use for IAM role |
| `iam_role_arn` | `string` | `null` | Existing IAM role ARN (required if create_iam_role = false) |
| `iam_role_policy_arns` | `list(string)` | `[]` | ARNs of IAM policies to attach to workspace role |
| `enable_alerts` | `bool` | `false` | Enable alerting permissions for workspace IAM role |
| `create_security_group` | `bool` | `true` | Whether to create security group for workspace |
| `security_group_rules` | `any` | `{}` | Security group rules to add |
| `workspace_api_keys` | `any` | `{}` | Map of workspace API keys to create |
| `workspace_service_accounts` | `any` | `{}` | Map of workspace service accounts to create |
| `workspace_service_account_tokens` | `any` | `{}` | Map of workspace service account tokens to create |
| `associate_license` | `bool` | `true` | Whether to associate a license with workspace |
| `license_type` | `string` | `"ENTERPRISE"` | Type of license (ENTERPRISE, ENTERPRISE_FREE_TRIAL) |
| `saml_idp_metadata_url` | `string` | `null` | SAML identity provider metadata URL |
| `saml_admin_role_values` | `list(string)` | `[]` | SAML assertion values for admin role |
| `saml_editor_role_values` | `list(string)` | `[]` | SAML assertion values for editor role |
| `configuration` | `string` | `null` | JSON-encoded workspace configuration (unified alerting, plugins) |
| `tags` | `map(string)` | `{}` | Map of tags to assign to resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `workspace_id` | The ID of the Grafana workspace |
| `workspace_arn` | The Amazon Resource Name (ARN) of the Grafana workspace |
| `workspace_endpoint` | The endpoint of the Grafana workspace |
| `workspace_grafana_version` | The version of Grafana running on the workspace |
| `workspace_api_keys` | The workspace API keys created including their attributes |
| `workspace_service_accounts` | The workspace service accounts created including their attributes |
| `workspace_service_account_tokens` | The workspace service account tokens created including their attributes |
| `workspace_iam_role_name` | IAM role name of the Grafana workspace |
| `workspace_iam_role_arn` | IAM role ARN of the Grafana workspace |
| `workspace_iam_role_unique_id` | Stable and unique string identifying the IAM role |
| `workspace_iam_role_policy_arn` | IAM Policy ARN of the Grafana workspace IAM role |
| `security_group_id` | ID of the security group |
| `security_group_arn` | Amazon Resource Name (ARN) of the security group |
| `saml_configuration_status` | Status of the SAML configuration |
| `license_expiration` | Expiration date of the enterprise license |

## Usage Examples

### Minimal Example

```hcl
module "grafana" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name              = "my-grafana"
  associate_license = false  # Set to true for Enterprise features

  tags = { Environment = "dev" }
}
```

### Example 1: Basic Workspace with AWS SSO

```hcl
module "grafana_basic" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                     = "team-grafana"
  description              = "Grafana workspace for engineering team"
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"

  data_sources = [
    "CLOUDWATCH",
    "PROMETHEUS",
    "XRAY"
  ]

  notification_destinations = ["SNS"]

  tags = {
    Environment = "production"
    Team        = "platform"
  }
}
```

### Example 2: Workspace with VPC Configuration

```hcl
module "grafana_vpc" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                     = "secure-grafana"
  description              = "Grafana workspace in private VPC"
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"

  data_sources = ["CLOUDWATCH", "PROMETHEUS"]

  # VPC configuration for private deployment
  vpc_configuration = {
    subnet_ids         = ["subnet-abc123", "subnet-def456"]
    security_group_ids = [aws_security_group.grafana.id]
  }

  # Custom security group rules
  create_security_group = true
  security_group_rules = {
    ingress_https = {
      type        = "ingress"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["10.0.0.0/8"]
      description = "HTTPS from corporate network"
    }
    egress_all = {
      type        = "egress"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
      description = "Allow all outbound"
    }
  }

  tags = {
    Environment = "production"
    Compliance  = "required"
  }
}
```

### Example 3: Workspace with API Keys and Service Accounts

```hcl
module "grafana_automation" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                     = "automation-grafana"
  description              = "Grafana workspace with API keys for automation"
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"

  data_sources = ["CLOUDWATCH", "PROMETHEUS", "XRAY"]

  # Create API keys for different access levels
  workspace_api_keys = {
    viewer = {
      key_name = "viewer-key"
      key_role = "VIEWER"
      seconds_to_live = 2592000  # 30 days
    }
    editor = {
      key_name = "editor-key"
      key_role = "EDITOR"
      seconds_to_live = 2592000
    }
    admin = {
      key_name = "admin-key"
      key_role = "ADMIN"
      seconds_to_live = 604800  # 7 days
    }
  }

  # Create service accounts for CI/CD
  workspace_service_accounts = {
    cicd = {
      name         = "cicd-service-account"
      grafana_role = "EDITOR"
      tokens = {
        main = {
          name = "cicd-token"
          seconds_to_live = 2592000
        }
      }
    }
  }

  tags = {
    Environment = "production"
    Purpose     = "automation"
  }
}
```

### Example 4: Organization-Wide Workspace

```hcl
module "grafana_organization" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                     = "org-wide-grafana"
  description              = "Organization-wide Grafana workspace"
  account_access_type      = "ORGANIZATION"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"

  data_sources = [
    "CLOUDWATCH",
    "PROMETHEUS",
    "XRAY",
    "OPENSEARCH_SERVICE",
    "TIMESTREAM"
  ]

  notification_destinations = ["SNS"]

  # Custom IAM role configuration
  create_iam_role = true
  iam_role_name   = "GrafanaOrganizationRole"
  iam_role_path   = "/grafana/"

  iam_role_policy_arns = [
    "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
  ]

  tags = {
    Environment  = "production"
    Organization = "enabled"
    CostCenter   = "platform"
  }
}
```

### Example 5: SAML-Authenticated Workspace

```hcl
module "grafana_saml" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                     = "saml-grafana"
  description              = "Grafana workspace with SAML authentication"
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["SAML"]
  permission_type          = "SERVICE_MANAGED"

  data_sources = ["CLOUDWATCH", "PROMETHEUS"]

  # SAML configuration
  saml_idp_metadata_url      = "https://idp.example.com/metadata"
  saml_admin_role_values     = ["admin"]
  saml_editor_role_values    = ["editor"]
  saml_email_assertion       = "email"
  saml_login_assertion       = "username"
  saml_name_assertion        = "displayName"
  saml_role_assertion        = "role"
  saml_org_assertion         = "organization"
  saml_login_validity_duration = 1440  # 24 hours

  tags = {
    Environment    = "production"
    Authentication = "saml"
  }
}
```

### Example 6: Customer-Managed Permissions

```hcl
# Create custom IAM role separately
resource "aws_iam_role" "grafana_custom" {
  name = "CustomGrafanaRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "grafana.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "grafana_cloudwatch" {
  role       = aws_iam_role.grafana_custom.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
}

module "grafana_custom_permissions" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                     = "custom-perm-grafana"
  description              = "Grafana workspace with customer-managed permissions"
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "CUSTOMER_MANAGED"

  data_sources = ["CLOUDWATCH"]

  # Use existing IAM role
  create_iam_role = false
  iam_role_arn    = aws_iam_role.grafana_custom.arn

  tags = {
    Environment = "production"
    Permissions = "customer-managed"
  }
}
```

### Example 7: Workspace with Network Access Control

```hcl
module "grafana_restricted" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                     = "restricted-grafana"
  description              = "Grafana workspace with IP restrictions"
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"

  data_sources = ["CLOUDWATCH", "PROMETHEUS"]

  # Restrict access to specific IP ranges
  network_access_control = {
    prefix_list_ids = [aws_ec2_managed_prefix_list.corporate.id]
    vpce_ids        = [aws_vpc_endpoint.grafana.id]
  }

  tags = {
    Environment = "production"
    Security    = "restricted"
  }
}

resource "aws_ec2_managed_prefix_list" "corporate" {
  name           = "corporate-ip-ranges"
  address_family = "IPv4"
  max_entries    = 10

  entry {
    cidr        = "203.0.113.0/24"
    description = "Office network"
  }
}
```

### Example 8: Complete Production Setup

```hcl
module "grafana_production" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                = "prod-observability"
  description         = "Production observability platform with Grafana"
  grafana_version     = "10.4"
  account_access_type = "CURRENT_ACCOUNT"

  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"

  # Enable unified alerting
  configuration = jsonencode({
    unifiedAlerting = { enabled = true }
    plugins = { pluginAdminEnabled = false }
  })

  # All supported data sources
  data_sources = [
    "CLOUDWATCH",
    "PROMETHEUS",
    "XRAY",
    "ATHENA",
    "OPENSEARCH_SERVICE",
    "REDSHIFT",
    "SITEWISE",
    "TIMESTREAM"
  ]

  notification_destinations = ["SNS"]

  # VPC configuration for security
  vpc_configuration = {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [aws_security_group.grafana.id]
  }

  # IAM role with custom policies
  create_iam_role = true
  iam_role_name   = "ProductionGrafanaRole"
  iam_role_path   = "/observability/"

  iam_role_policy_arns = [
    "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess",
    "arn:aws:iam::aws:policy/AmazonPrometheusQueryAccess",
    "arn:aws:iam::aws:policy/AWSXRayReadOnlyAccess"
  ]

  iam_role_max_session_duration = 43200  # 12 hours

  # API keys for different teams
  workspace_api_keys = {
    platform_team = {
      key_name        = "platform-admin"
      key_role        = "ADMIN"
      seconds_to_live = 2592000
    }
    dev_team = {
      key_name        = "dev-editor"
      key_role        = "EDITOR"
      seconds_to_live = 2592000
    }
    readonly = {
      key_name        = "readonly-viewer"
      key_role        = "VIEWER"
      seconds_to_live = 7776000  # 90 days
    }
  }

  # Service accounts for automation
  workspace_service_accounts = {
    terraform = {
      name         = "terraform-automation"
      grafana_role = "ADMIN"
      tokens = {
        main = {
          name            = "terraform-token"
          seconds_to_live = 2592000
        }
      }
    }
  }

  # Enterprise license
  associate_license = true
  license_type      = "ENTERPRISE"

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
    CostCenter  = "platform"
    Compliance  = "required"
  }
}
```

## Best Practices

### Workspace Configuration

1. **Use Descriptive Names**: Give workspaces clear, descriptive names that reflect their purpose and environment (e.g., "prod-observability", "dev-team-metrics")
2. **Specify Grafana Version**: Pin to specific Grafana versions in production to ensure consistent behavior and controlled upgrades
3. **Enable Required Data Sources Only**: Configure only the data sources your teams actually use to minimize IAM permissions and reduce attack surface
4. **Set Appropriate Notification Destinations**: Configure SNS topics for alerting to ensure critical alerts reach the right teams
5. **Use Organization Account Type for Multi-Account**: When monitoring across AWS accounts, use ORGANIZATION account access type with proper delegation
6. **Document Workspace Purpose**: Provide clear descriptions explaining the workspace's intended use, data sources, and responsible teams

### Authentication and Access Control

1. **Prefer AWS SSO Over SAML**: Use AWS SSO (IAM Identity Center) for simpler setup and better AWS integration unless you have specific SAML requirements
2. **Implement SAML for Enterprise SSO**: Configure SAML authentication for organizations with existing identity providers (Okta, Azure AD, etc.)
3. **Use Service-Managed Permissions by Default**: Start with SERVICE_MANAGED permission type for simpler setup; switch to CUSTOMER_MANAGED only when you need fine-grained control
4. **Configure SAML Role Mapping**: Map SAML assertion attributes to Grafana roles (Admin, Editor, Viewer) based on your IdP group membership
5. **Set Reasonable Session Durations**: Balance security and user experience with IAM role session durations (4-12 hours typically)
6. **Restrict Allowed Organizations**: When using SAML, limit allowed_organizations to specific business units or teams that should have access
7. **Audit Authentication Events**: Enable CloudTrail logging for all authentication events to workspace for security monitoring

### IAM and Permissions

1. **Use Least Privilege IAM Policies**: Grant only the minimum permissions needed for your configured data sources (e.g., ReadOnly policies where possible)
2. **Separate Roles by Environment**: Create distinct IAM roles for dev, staging, and production workspaces with appropriate permission scopes
3. **Set IAM Role Paths**: Use iam_role_path to organize Grafana roles (e.g., "/grafana/" or "/observability/") for better IAM organization
4. **Attach Managed Policies**: Prefer AWS managed policies (CloudWatchReadOnlyAccess, etc.) over inline policies for easier maintenance
5. **Use Permission Boundaries**: Apply permission boundaries to IAM roles in delegated environments to prevent privilege escalation
6. **Cross-Account Access Pattern**: For multi-account architectures, use customer-managed permissions with cross-account IAM role trust relationships
7. **Rotate Service Account Tokens**: Set reasonable seconds_to_live for service account tokens (30 days) and rotate them regularly
8. **Monitor IAM Role Usage**: Enable CloudWatch metrics and CloudTrail logging for IAM role assumption by Grafana workspaces

### Network Security

1. **Deploy in Private Subnets**: Use VPC configuration to deploy Grafana endpoints in private subnets for enhanced security
2. **Implement Network Access Controls**: Use network_access_control with prefix lists to restrict workspace access to corporate IP ranges or VPN
3. **Use VPC Endpoints**: Configure VPC endpoints (vpce_ids) for private connectivity without internet gateway traversal
4. **Custom Security Groups**: Create tailored security group rules limiting ingress to specific ports and sources
5. **Enable HTTPS Only**: Ensure all workspace endpoints use HTTPS; AWS Managed Grafana enforces this by default
6. **Restrict Egress Traffic**: Configure security group egress rules to allow only necessary outbound connections to data sources
7. **Use Transit Gateway**: For multi-VPC architectures, connect through AWS Transit Gateway for centralized network management

### API Keys and Service Accounts

1. **Create Role-Based API Keys**: Provision separate API keys for different access levels (VIEWER, EDITOR, ADMIN) based on use cases
2. **Set Short Expiration for Admin Keys**: Limit admin API key lifetime to 7 days; use longer periods (30-90 days) for read-only keys
3. **Use Service Accounts for Automation**: Prefer service accounts over API keys for CI/CD pipelines and infrastructure automation
4. **Rotate Keys Regularly**: Implement a process to rotate API keys and service account tokens every 30-90 days
5. **Store Keys Securely**: Store API keys and tokens in AWS Secrets Manager or Parameter Store, never in code repositories
6. **Monitor Key Usage**: Track API key and service account usage through CloudWatch logs to detect anomalies
7. **Limit Token Scope**: Create multiple service accounts with narrow scopes rather than one with broad permissions
8. **Name Keys Descriptively**: Use clear naming conventions for API keys and service accounts indicating their purpose and owner

### License Management

1. **Start with Free Trial**: Use ENTERPRISE_FREE_TRIAL for testing before committing to paid licenses
2. **Monitor License Expiration**: Set up CloudWatch alarms to alert before license expiration dates
3. **Plan for Active Users**: ENTERPRISE licenses charge per active user; monitor workspace usage to forecast costs
4. **Associate Licenses Explicitly**: Set associate_license = true and specify license_type to avoid unexpected charges
5. **Review License Type**: Understand the difference between free tier and ENTERPRISE features to choose appropriately

### Monitoring and Observability

1. **Enable CloudWatch Logs**: Configure CloudWatch Logs groups for workspace audit logs and authentication events
2. **Set Up CloudWatch Alarms**: Create alarms for workspace errors, authentication failures, and API throttling
3. **Monitor Workspace Health**: Track workspace_grafana_version and endpoint availability through automated health checks
4. **Track API Usage**: Monitor API key usage patterns and set alerts for unusual activity
5. **Log SAML Authentication**: Enable detailed logging for SAML authentication attempts and failures for security auditing
6. **Dashboard Performance Monitoring**: Use CloudWatch metrics to track dashboard query performance and identify slow data sources

### Cost Optimization

1. **Right-Size Active Users**: ENTERPRISE pricing is per active user; remove inactive users promptly to reduce costs
2. **Use Free Tier When Sufficient**: Evaluate if the free tier meets your needs before upgrading to ENTERPRISE
3. **Consolidate Workspaces**: Use fewer, shared workspaces with proper RBAC rather than many single-purpose workspaces
4. **Monitor Data Transfer Costs**: Track data transfer between Grafana and data sources, especially cross-region queries
5. **Clean Up Unused API Keys**: Regularly audit and delete unused API keys and service accounts
6. **Optimize Query Frequency**: Configure dashboard refresh rates appropriately; avoid overly aggressive polling of data sources
7. **Use CloudWatch Contributor Insights**: Identify top API key users and data source query patterns to optimize usage

### High Availability and Disaster Recovery

1. **Deploy Across Multiple AZs**: Use subnet_ids spanning multiple availability zones for VPC-deployed workspaces
2. **Export Dashboards Regularly**: Use Terraform or API automation to backup Grafana dashboard configurations
3. **Document Data Source Configurations**: Maintain infrastructure-as-code for all data source connections and credentials
4. **Plan for Region Failure**: For critical workspaces, maintain parallel deployments in different regions
5. **Test Recovery Procedures**: Periodically test workspace recreation from Terraform state and dashboard backups
6. **Version Control Dashboards**: Store Grafana dashboard JSON in version control systems alongside Terraform code

### Tagging and Governance

1. **Implement Consistent Tagging**: Apply tags for Environment, CostCenter, Team, ManagedBy across all resources
2. **Use AWS Organizations Tags**: Leverage tag policies in AWS Organizations to enforce tagging standards
3. **Tag for Cost Allocation**: Include cost allocation tags to track Grafana expenses by team or project
4. **Automate Tag Compliance**: Use AWS Config rules to detect and alert on untagged or improperly tagged resources
5. **Document Tag Schema**: Maintain documentation of required and optional tags for Grafana resources

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-grafana
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/managed-service-grafana/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-grafana/tree/master/examples
- **AWS Managed Grafana Documentation**: https://docs.aws.amazon.com/grafana/latest/userguide/what-is-Amazon-Managed-Service-Grafana.html
- **AWS Managed Grafana User Guide**: https://docs.aws.amazon.com/grafana/latest/userguide/
- **Grafana Documentation**: https://grafana.com/docs/grafana/latest/
- **AWS Managed Grafana Permissions**: https://docs.aws.amazon.com/grafana/latest/userguide/AMG-manage-permissions.html
- **AWS Managed Grafana Data Sources**: https://docs.aws.amazon.com/grafana/latest/userguide/AMG-data-sources.html
- **AWS Managed Grafana Authentication**: https://docs.aws.amazon.com/grafana/latest/userguide/authentication-in-AMG.html
- **AWS Managed Grafana API Reference**: https://docs.aws.amazon.com/grafana/latest/APIReference/Welcome.html
- **AWS Managed Grafana Pricing**: https://aws.amazon.com/grafana/pricing/
- **Grafana Best Practices**: https://grafana.com/docs/grafana/latest/best-practices/
- **AWS Managed Grafana Workshop**: https://catalog.workshops.aws/observability/en-US/aws-managed-oss/amp-amg
- **CloudWatch Data Source Plugin**: https://grafana.com/grafana/plugins/cloudwatch/
- **Prometheus Data Source Plugin**: https://grafana.com/docs/grafana/latest/datasources/prometheus/

## Notes for AI Agents

When using this module in automated workflows:

1. **Authentication First**: Ensure AWS SSO or SAML identity provider is configured before creating workspaces with those authentication types
2. **Data Source Permissions**: Verify IAM role has appropriate permissions for all specified data sources before workspace becomes operational
3. **VPC Prerequisites**: When using vpc_configuration, ensure subnets exist and have proper routing/security groups configured
4. **License Costs**: ENTERPRISE licenses incur costs; use ENTERPRISE_FREE_TRIAL for testing and development environments
5. **API Key Lifetime**: Plan for API key rotation; keys expire after seconds_to_live and require recreation through Terraform
6. **SAML Metadata**: Ensure idp_metadata_url is accessible from AWS endpoints; test SAML configuration before production deployment
7. **Network Access Timing**: Network access controls take effect immediately; coordinate changes with user teams to avoid disruption
8. **Service Account Tokens**: Tokens are generated once; capture outputs during apply and store securely in secrets manager
9. **Organization Scope**: ORGANIZATION account access requires management or delegated administrator account; validate account role
10. **Security Group Dependencies**: If using create_security_group = false, ensure security_group_ids are provided in vpc_configuration
11. **Cross-Account Patterns**: For customer-managed permissions with cross-account access, configure trust relationships before workspace creation
12. **Workspace Updates**: Changing authentication_providers or account_access_type requires workspace recreation; plan for downtime
13. **Version Pinning**: Specify grafana_version in production to prevent unexpected upgrades during workspace updates
14. **Tagging Strategy**: Apply consistent tags across workspace, IAM roles, and security groups for unified cost tracking and compliance
15. **Monitoring Setup**: Configure CloudWatch alarms and log groups immediately after workspace creation to avoid gaps in observability
