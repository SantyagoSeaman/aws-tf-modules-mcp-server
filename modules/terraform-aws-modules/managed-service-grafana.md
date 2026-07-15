# Terraform AWS Managed Service for Grafana Module

## Module Information

- **Module Name**: `managed-service-grafana`
- **Module ID**: `terraform-aws-modules/managed-service-grafana/aws`
- **Source**: `terraform-aws-modules/managed-service-grafana/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-grafana
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/managed-service-grafana/aws/latest
- **Latest Version**: 2.3.1
- **Purpose**: Terraform module that creates and configures an AWS Managed Grafana (AMG) workspace together with its IAM role, security group, SAML configuration, API keys, service accounts, role associations, and license association
- **Service**: AWS Managed Grafana (Amazon Managed Service for Grafana)
- **Category**: Monitoring, Observability
- **Keywords**: grafana, amg, workspace, dashboard, visualization, cloudwatch, prometheus, x-ray, sso, saml, iam-role, security-group, vpc, api-key, service-account, license
- **Use For**: centralized metrics/logs/traces dashboards, multi-source observability platforms, EKS and infrastructure monitoring, SSO/SAML-authenticated Grafana access, private VPC-connected Grafana deployments, CI/CD dashboard automation via service accounts, organization-wide cross-account monitoring, compliance and SOC dashboards

## Description

This Terraform module provisions and configures an Amazon Managed Grafana (AMG) workspace, a fully managed, auto-scaling Grafana service that removes the operational burden of installing, patching, and scaling Grafana servers. Beyond the `aws_grafana_workspace` resource itself, the module can optionally create the IAM role and policy the workspace assumes to reach AWS data sources, a dedicated security group for VPC-based connectivity, SAML identity-provider configuration, API keys, service accounts and their tokens, AWS SSO role associations, and an Enterprise or Enterprise-free-trial license association. It can also attach configuration to an existing workspace (`create_workspace = false`) rather than creating a new one.

AMG lets teams query, correlate, and visualize metrics, logs, and traces from CloudWatch, Amazon Managed Service for Prometheus, X-Ray, Amazon OpenSearch Service, Redshift, Athena, IoT SiteWise, and Timestream, as well as self-managed and third-party data sources, from a single workspace. The module supports both `SERVICE_MANAGED` permissions, where AWS automatically creates and attaches the IAM policies required for the selected data sources, and `CUSTOMER_MANAGED` permissions for teams that bring their own IAM role. Authentication can be delegated to AWS SSO (IAM Identity Center), SAML 2.0, or both, with role assignment handled through `role_associations` (AWS SSO users/groups) or SAML assertion-to-role mapping.

The module is a single, flat module with no submodules; every resource group it manages -- workspace, IAM role, security group, SAML configuration, API keys, service accounts, and license -- is toggled independently through `create_*` boolean flags, allowing partial adoption (for example, bringing your own IAM role while letting the module manage API keys). For data sources that live inside a VPC, `vpc_configuration` attaches the workspace to specified subnets and security groups, while `network_access_control` restricts workspace network access to specific IP prefix lists or VPC endpoints. For AWS Organizations-wide deployments, `stack_set_name` and `organizational_units` let AMG provision the cross-account IAM roles it needs via CloudFormation StackSets.

## Key Features

- **Workspace Lifecycle**: Create a new AMG workspace or layer configuration onto an existing one via `workspace_id`
- **Multi-Source Data Integration**: Native support for `CLOUDWATCH`, `PROMETHEUS`, `XRAY`, `AMAZON_OPENSEARCH_SERVICE`, `ATHENA`, `REDSHIFT`, `SITEWISE`, and `TIMESTREAM` data sources
- **Dual Authentication**: AWS SSO (IAM Identity Center) and SAML 2.0, usable individually or together
- **SAML Configuration**: Full assertion mapping (email, login, name, org, role, groups) with admin/editor role-value mapping and either metadata URL or inline XML
- **AWS SSO Role Associations**: Assign SSO users and groups to `ADMIN`, `EDITOR`, or `VIEWER` roles via `role_associations`
- **Flexible Permission Models**: `SERVICE_MANAGED` (auto-created IAM policies) or `CUSTOMER_MANAGED` (bring your own IAM role)
- **IAM Role Management**: Optional workspace IAM role with custom path, permissions boundary, session duration, and extra policy attachments
- **Organization-Wide Access**: `stack_set_name` and `organizational_units` provision cross-account IAM roles via CloudFormation StackSets for `ORGANIZATION` account access
- **VPC Connectivity**: `vpc_configuration` attaches the workspace to private subnets/security groups to reach VPC-only data sources
- **Network Access Control**: Restrict workspace access to specific IP prefix lists or VPC endpoints
- **Security Group Management**: Auto-created security group with customizable ingress/egress rules
- **API Keys and Service Accounts**: Provision role-scoped API keys or service accounts with tokens for automation and CI/CD
- **Enterprise Licensing**: Associate `ENTERPRISE` or `ENTERPRISE_FREE_TRIAL` licenses using a Grafana Labs `grafana_token`
- **Alerting Permissions**: `enable_alerts` grants the IAM permissions Grafana-managed alerting needs to reach data sources
- **Notification Destinations**: Configure SNS as an alert notification destination
- **Unified Alerting / Plugin Configuration**: JSON-encoded `configuration` block to enable unified alerting or restrict plugin administration
- **Conditional Resource Creation**: Every resource group (workspace, IAM role, security group, SAML config, license) is independently toggled with `create_*` flags
- **Comprehensive Tagging**: Independent tag maps for the workspace, IAM role, and security group

## Main Use Cases

1. **Centralized Observability Dashboards**: Unify CloudWatch, Prometheus, X-Ray, and OpenSearch data in one workspace
2. **EKS/Kubernetes Monitoring**: Visualize cluster and workload metrics from Amazon Managed Service for Prometheus
3. **Application Performance Monitoring**: Correlate traces (X-Ray), metrics (CloudWatch), and logs (OpenSearch) per request
4. **Organization-Wide Monitoring**: Deploy one workspace with `ORGANIZATION` access type and StackSet-provisioned roles across member accounts
5. **Private/VPC-Isolated Deployments**: Reach self-managed data sources in private subnets via `vpc_configuration`
6. **SSO/SAML-Governed Access**: Enforce enterprise identity provider authentication with role-based dashboard permissions
7. **CI/CD and Automation Dashboards**: Provision service accounts/tokens for pipelines to publish or query dashboards programmatically
8. **Compliance and Security Operations Dashboards**: Aggregate security telemetry with restricted network access controls
9. **Cross-Account Shared Monitoring**: Use `CUSTOMER_MANAGED` permissions with pre-built cross-account IAM roles for shared platforms

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `create_workspace` | `bool` | `true` | Whether to create a workspace or use an existing one |
| `workspace_id` | `string` | `""` | ID of existing workspace when `create_workspace = false` |
| `name` | `string` | `null` | Grafana workspace name |
| `description` | `string` | `null` | Workspace description |
| `account_access_type` | `string` | `"CURRENT_ACCOUNT"` | `CURRENT_ACCOUNT` or `ORGANIZATION` |
| `authentication_providers` | `list(string)` | `["AWS_SSO"]` | `AWS_SSO`, `SAML`, or both |
| `permission_type` | `string` | `"SERVICE_MANAGED"` | `SERVICE_MANAGED` or `CUSTOMER_MANAGED` |
| `data_sources` | `list(string)` | `[]` | `AMAZON_OPENSEARCH_SERVICE`, `ATHENA`, `CLOUDWATCH`, `PROMETHEUS`, `REDSHIFT`, `SITEWISE`, `TIMESTREAM`, `XRAY` |
| `notification_destinations` | `list(string)` | `[]` | Notification destinations; only `SNS` is supported |
| `grafana_version` | `string` | `null` | Grafana version to run in the workspace |
| `configuration` | `string` | `null` | JSON-encoded workspace config (unified alerting, plugins) |
| `vpc_configuration` | `any` | `{}` | `subnet_ids` / `security_group_ids` for private data source access |
| `network_access_control` | `any` | `{}` | `prefix_list_ids` / `vpce_ids` to restrict workspace network access |
| `stack_set_name` | `string` | `null` | CloudFormation StackSet name that provisions cross-account IAM roles |
| `organizational_units` | `list(string)` | `[]` | AWS Organizations OUs authorized to use data sources |
| `create_iam_role` | `bool` | `true` | Whether to create the workspace IAM role |
| `iam_role_arn` | `string` | `null` | Existing IAM role ARN (required if `create_iam_role = false`) |
| `iam_role_name` | `string` | `null` | Name for the workspace IAM role |
| `iam_role_path` | `string` | `null` | IAM role path |
| `iam_role_policy_arns` | `list(string)` | `[]` | Additional IAM policy ARNs to attach to the workspace role |
| `iam_role_permissions_boundary` | `string` | `null` | Permissions boundary ARN for the IAM role |
| `iam_role_max_session_duration` | `number` | `null` | Max session duration (seconds) for the IAM role |
| `enable_alerts` | `bool` | `false` | Grant IAM permissions required for Grafana-managed alerting |
| `create_security_group` | `bool` | `true` | Whether to create a security group for the workspace |
| `security_group_rules` | `any` | `{}` | Ingress/egress rules to add to the created security group — keys (from examples): `description`, `from_port`, `to_port`, `protocol`, `cidr_blocks` |
| `workspace_api_keys` | `any` | `{}` | Map of API keys to create (`VIEWER`/`EDITOR`/`ADMIN`) |
| `workspace_service_accounts` | `any` | `{}` | Map of service accounts to create — keys (from examples): `name`, `grafana_role` |
| `workspace_service_account_tokens` | `any` | `{}` | Map of tokens to create for service accounts — keys (from examples): `service_account_key`, `name`, `seconds_to_live` |
| `create_saml_configuration` | `bool` | `true` | Whether to create the SAML configuration resource |
| `saml_idp_metadata_url` | `string` | `null` | SAML IdP metadata URL (mutually exclusive with `saml_idp_metadata_xml`) |
| `saml_admin_role_values` / `saml_editor_role_values` | `list(string)` | `[]` | SAML assertion values mapped to Admin/Editor roles |
| `saml_allowed_organizations` | `list(string)` | `[]` | SAML organizations allowed to authenticate |
| `role_associations` | `any` | `{}` | Map of role -> `user_ids`/`group_ids` for AWS SSO role assignment |
| `associate_license` | `bool` | `true` | Whether to associate a Grafana Enterprise license |
| `license_type` | `string` | `"ENTERPRISE"` | `ENTERPRISE` or `ENTERPRISE_FREE_TRIAL` |
| `grafana_token` | `string` | `null` | Grafana Labs token required for `ENTERPRISE` license association |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `workspace_id` | The ID of the Grafana workspace |
| `workspace_arn` | The Amazon Resource Name (ARN) of the Grafana workspace |
| `workspace_endpoint` | The endpoint of the Grafana workspace |
| `workspace_grafana_version` | The version of Grafana running on the workspace |
| `workspace_api_keys` | The workspace API keys created, including their attributes |
| `workspace_service_accounts` | The workspace service accounts created, including their attributes |
| `workspace_service_account_tokens` | The workspace service account tokens created, including their attributes |
| `workspace_iam_role_name` / `workspace_iam_role_arn` | Name and ARN of the workspace IAM role |
| `workspace_iam_role_unique_id` | Stable and unique string identifying the IAM role |
| `workspace_iam_role_policy_arn` / `workspace_iam_role_policy_name` / `workspace_iam_role_policy_id` | Identifiers of the IAM policy attached to the workspace role |
| `security_group_id` / `security_group_arn` | ID and ARN of the security group created for the workspace |
| `saml_configuration_status` | Status of the SAML configuration |
| `license_expiration` | Expiration date of the `ENTERPRISE` license |
| `license_free_trial_expiration` | Expiration date of the `ENTERPRISE_FREE_TRIAL` license |

## Usage Examples

### Minimal Example

```hcl
module "grafana" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name              = "my-grafana"
  associate_license = false  # Skip Enterprise licensing for the free tier

  tags = { Environment = "dev" }
}
```

### Example 1: AWS SSO Workspace with Role Associations

```hcl
module "grafana" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                     = "team-grafana"
  description              = "Grafana workspace for the platform team"
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"

  data_sources               = ["CLOUDWATCH", "PROMETHEUS", "XRAY"]
  notification_destinations  = ["SNS"]

  # Assign AWS SSO users/groups to Grafana roles
  role_associations = {
    ADMIN  = { group_ids = ["1111111111-abcdefgh-1234-5678-abcd-999999999999"] }
    EDITOR = { user_ids  = ["2222222222-abcdefgh-1234-5678-abcd-999999999999"] }
  }

  tags = {
    Environment = "production"
    Team        = "platform"
  }
}
```

### Example 2: Private VPC Workspace with Network Access Control

```hcl
module "grafana" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                     = "secure-grafana"
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"
  data_sources             = ["CLOUDWATCH", "PROMETHEUS"]

  # Reach data sources living in private subnets
  vpc_configuration = {
    subnet_ids = module.vpc.private_subnets
  }

  security_group_rules = {
    egress_prometheus = {
      description = "Allow egress to self-managed Prometheus"
      from_port   = 9090
      to_port     = 9090
      protocol    = "tcp"
      cidr_blocks = module.vpc.private_subnets_cidr_blocks
    }
  }

  # Restrict console/API access to the corporate network
  network_access_control = {
    prefix_list_ids = [aws_ec2_managed_prefix_list.corporate.id]
  }

  tags = { Environment = "production" }
}
```

### Example 3: SAML-Authenticated Workspace

```hcl
module "grafana" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                     = "saml-grafana"
  authentication_providers = ["SAML"]
  permission_type          = "SERVICE_MANAGED"
  data_sources             = ["CLOUDWATCH", "PROMETHEUS"]

  saml_idp_metadata_url      = "https://idp.example.com/metadata"
  saml_admin_role_values     = ["admin"]
  saml_editor_role_values    = ["editor"]
  saml_email_assertion       = "mail"
  saml_login_assertion       = "mail"
  saml_name_assertion        = "displayName"
  saml_role_assertion        = "role"
  saml_org_assertion         = "org"
  saml_allowed_organizations = ["example-corp"]

  tags = { Authentication = "saml" }
}
```

### Example 4: API Keys and Service Accounts for Automation

```hcl
module "grafana" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name         = "automation-grafana"
  data_sources = ["CLOUDWATCH", "PROMETHEUS", "XRAY"]

  # Short-lived, role-scoped API keys
  workspace_api_keys = {
    viewer = { key_name = "viewer-key", key_role = "VIEWER", seconds_to_live = 2592000 }
    admin  = { key_name = "admin-key", key_role = "ADMIN", seconds_to_live = 604800 }
  }

  # Preferred over API keys for CI/CD pipelines
  workspace_service_accounts = {
    cicd = { name = "cicd-service-account", grafana_role = "EDITOR" }
  }

  workspace_service_account_tokens = {
    cicd = { service_account_key = "cicd", name = "cicd-token", seconds_to_live = 2592000 }
  }

  tags = { Purpose = "automation" }
}
```

### Example 5: Organization-Wide, Production Workspace

```hcl
module "grafana" {
  source  = "terraform-aws-modules/managed-service-grafana/aws"
  version = "~> 2.3"

  name                 = "prod-observability"
  grafana_version      = "10.4"
  account_access_type  = "ORGANIZATION"
  stack_set_name       = "prod-observability" # Provisions cross-account IAM roles
  organizational_units = ["ou-abcd-12345678"]

  authentication_providers  = ["AWS_SSO"]
  permission_type           = "SERVICE_MANAGED"
  data_sources               = ["CLOUDWATCH", "PROMETHEUS", "XRAY", "AMAZON_OPENSEARCH_SERVICE", "TIMESTREAM"]
  notification_destinations  = ["SNS"]

  # Enable unified alerting, disable plugin self-service
  configuration = jsonencode({
    unifiedAlerting = { enabled = true }
    plugins         = { pluginAdminEnabled = false }
  })

  create_iam_role                = true
  iam_role_name                  = "ProductionGrafanaRole"
  iam_role_path                  = "/observability/"
  iam_role_max_session_duration  = 43200 # 12 hours
  iam_role_policy_arns = [
    "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess",
    "arn:aws:iam::aws:policy/AmazonPrometheusQueryAccess",
    "arn:aws:iam::aws:policy/AWSXRayReadOnlyAccess",
  ]

  associate_license = true
  license_type      = "ENTERPRISE"
  grafana_token     = var.grafana_labs_token

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
```

## Best Practices

### Authentication and Access Control

1. **Prefer AWS SSO Over SAML**: Use AWS SSO (IAM Identity Center) unless you already have an external IdP requiring SAML federation.
2. **Map SAML Roles Explicitly**: Configure `saml_admin_role_values` / `saml_editor_role_values` and restrict `saml_allowed_organizations` to trusted realms; unmapped users default to Viewer.
3. **Assign Roles via `role_associations`**: Manage AWS SSO user/group-to-role mapping in Terraform instead of the console for auditability.
4. **Start Service-Managed**: Use `permission_type = "SERVICE_MANAGED"` by default; switch to `CUSTOMER_MANAGED` only when you need a pre-existing or cross-account IAM role.

### IAM and Permissions

1. **Grant Least Privilege**: Attach only the IAM permissions needed for the configured `data_sources`, preferring AWS managed read-only policies (`CloudWatchReadOnlyAccess`, `AWSXRayReadOnlyAccess`, `AmazonPrometheusQueryAccess`).
2. **Use Permissions Boundaries**: Set `iam_role_permissions_boundary` in delegated or multi-team accounts to cap privilege escalation.
3. **Provision Org-Wide Access Deliberately**: Use `stack_set_name` with `organizational_units` only when the workspace genuinely needs `ORGANIZATION`-wide access; it provisions IAM roles into every member account via CloudFormation StackSets.
4. **Bound Session Duration**: Keep `iam_role_max_session_duration` aligned with your organization's session policy (typically 1-12 hours).

### Network Security

1. **Span Multiple AZs**: Set `vpc_configuration.subnet_ids` across at least two availability zones when reaching VPC-only data sources.
2. **Restrict Network Access**: Use `network_access_control` with `prefix_list_ids`/`vpce_ids` to limit workspace access to corporate networks or VPC endpoints; once any list is set, all other traffic is denied.
3. **Scope Security Group Egress**: Limit `security_group_rules` to the specific ports/CIDRs of the data sources being queried rather than allowing all outbound traffic.

### API Keys and Service Accounts

1. **Prefer Service Accounts**: Use `workspace_service_accounts` + `workspace_service_account_tokens` over `workspace_api_keys` for CI/CD and automation; AWS/Grafana favor service accounts going forward.
2. **Scope and Expire Tokens**: Set the minimum required `key_role`/`grafana_role` and a short `seconds_to_live`, especially for `ADMIN`-level access.
3. **Capture Secrets Immediately**: API keys and tokens are only available in the Terraform output at creation time; move them into Secrets Manager during apply since they cannot be retrieved later.

### Licensing

1. **Trial Before Committing**: Use `license_type = "ENTERPRISE_FREE_TRIAL"` to evaluate Enterprise plugins/data sources before purchasing.
2. **Supply the Grafana Labs Token**: Set `grafana_token` (from your Grafana Labs account) when associating an `ENTERPRISE` license.
3. **Monitor Expiration**: Track the `license_expiration` / `license_free_trial_expiration` outputs to avoid unplanned loss of Enterprise features.

### Operational Excellence

1. **Pin Versions**: Pin both the module version (`version = "~> 2.3"`) and `grafana_version` to avoid unplanned upgrades.
2. **Tag Consistently**: Apply consistent tags (Environment, Team, CostCenter) across the workspace, IAM role, and security group for cost allocation and governance.
3. **Manage Dashboards Separately**: This module manages the workspace, not dashboard content; store dashboard JSON in version control and provision it via the Grafana API/provider.
4. **Enable Unified Alerting Deliberately**: Understand that the `configuration` block's `unifiedAlerting` setting changes alert evaluation across all data sources in the workspace.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-grafana
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/managed-service-grafana/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-grafana/tree/main/examples
- **AWS Managed Grafana Documentation**: https://docs.aws.amazon.com/grafana/latest/userguide/what-is-Amazon-Managed-Service-Grafana.html
- **AWS Managed Grafana Permissions**: https://docs.aws.amazon.com/grafana/latest/userguide/AMG-manage-permissions.html
- **AWS Managed Grafana Data Sources**: https://docs.aws.amazon.com/grafana/latest/userguide/AMG-data-sources.html
- **AWS Managed Grafana Authentication**: https://docs.aws.amazon.com/grafana/latest/userguide/authentication-in-AMG.html
- **AWS Managed Grafana API Reference**: https://docs.aws.amazon.com/grafana/latest/APIReference/Welcome.html
- **AWS Managed Grafana Pricing**: https://aws.amazon.com/grafana/pricing/
- **Grafana Documentation**: https://grafana.com/docs/grafana/latest/

## Notes for AI Agents

When using this module in automated workflows:

1. **No Submodules**: This is a standalone, flat module; every resource group is controlled through top-level `create_*` flags rather than nested submodules.
2. **Data Source Enum**: The correct value for the OpenSearch data source is `AMAZON_OPENSEARCH_SERVICE`, not `OPENSEARCH_SERVICE`; invalid enum values fail plan/apply.
3. **Authentication First**: Ensure the AWS SSO instance or SAML identity provider is configured before creating a workspace with that `authentication_providers` value.
4. **IAM Role Prerequisites**: Verify the workspace IAM role (created or existing via `iam_role_arn`) has permissions for every entry in `data_sources` before the workspace becomes fully operational.
5. **VPC Prerequisites**: When setting `vpc_configuration`, ensure the subnets and any referenced security groups already exist and have correct routing.
6. **Organization Access Caveats**: `account_access_type = "ORGANIZATION"` requires a management or delegated administrator account and typically pairs with `stack_set_name`/`organizational_units`.
7. **`role_associations` Gotcha**: This feature has known upstream AWS SDK/provider limitations around idempotency and drift; test carefully and check the module's example (which comments it out with linked provider issues) before relying on it in production.
8. **Service Account Tokens Are One-Time**: `workspace_service_account_tokens` values are generated once; capture them from Terraform state/output during apply and store them securely.
9. **License Costs**: `ENTERPRISE` licenses incur per-active-user charges; use `ENTERPRISE_FREE_TRIAL` for testing and non-production environments, and supply `grafana_token` only when required.
10. **Disruptive Updates**: Changing `authentication_providers` or `account_access_type` typically forces workspace recreation or re-authentication; plan for user-facing downtime.
11. **Security Group Dependency**: If `create_security_group = false`, supply existing `security_group_ids` inside `vpc_configuration`.
12. **Version Pinning**: Specify `grafana_version` in production to prevent unexpected Grafana version upgrades during workspace updates.
