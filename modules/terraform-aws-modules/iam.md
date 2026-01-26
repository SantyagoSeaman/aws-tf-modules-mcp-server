# Terraform AWS IAM Module

## Module Information

- **Module Name**: `iam`
- **Source**: `terraform-aws-modules/iam/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-iam
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest
- **Latest Version**: 6.4.0
- **Terraform Version**: >= 1.5.7
- **AWS Provider Version**: >= 6.28
- **Purpose**: Creates and manages AWS IAM resources including users, groups, roles, policies, and OIDC providers with support for EKS IRSA and federated identity
- **Service**: AWS IAM (Identity and Access Management)
- **Category**: Security, Identity Management, Access Control
- **Keywords**: iam, users, groups, roles, policies, oidc, saml, irsa, eks-service-accounts, github-actions, mfa, password-policy, cross-account, federated-identity, least-privilege, temporary-credentials
- **Use For**: Managing AWS user authentication and authorization, implementing role-based access control, setting up federated identity access, configuring GitHub Actions OIDC authentication, managing EKS service account permissions (IRSA), enforcing password policies, creating cross-account access roles, implementing least-privilege security

## Description

This Terraform module provides a comprehensive solution for managing AWS Identity and Access Management (IAM) resources through 8 specialized submodules. Each submodule focuses on a specific IAM resource type: account settings, users, groups, roles, policies, read-only policies, OIDC providers, and EKS service account roles (IRSA).

The module addresses common IAM challenges by providing pre-configured patterns for federated identity access (GitHub Actions, Bitbucket, SAML 2.0), cross-account role assumption, and EKS IRSA with 20+ pre-built AWS service policies. It handles secure credential management through PGP encryption and supports modern authentication methods alongside traditional IAM user management.

Key features include account-level password policies, MFA enforcement at the group level, permissions boundaries for delegated administration, and automatic read-only policy generation. The IRSA submodule includes pre-configured policies for Cert-Manager, Cluster Autoscaler, External DNS, Load Balancer Controller, EBS/EFS/FSx CSI drivers, Karpenter, Velero, and more.

## Key Features

- **Eight Specialized Submodules**: iam-account, iam-user, iam-group, iam-role, iam-policy, iam-read-only-policy, iam-oidc-provider, iam-role-for-service-accounts
- **Account-Level Configuration**: Account alias and organization-wide password policies with complexity, expiration, and reuse prevention
- **IAM User Management**: Login profiles, access keys, SSH keys with PGP-encrypted credential outputs
- **Group-Based Access Control**: Policy attachment, MFA enforcement, self-management permissions for credentials
- **Federated Identity**: GitHub OIDC, GitHub Enterprise Server, Bitbucket Pipelines, SAML 2.0 providers
- **IRSA for EKS**: IAM roles for Kubernetes service accounts with 20+ pre-built AWS service policies
- **Pre-Built Controller Policies**: Cert-Manager, Cluster Autoscaler, External DNS, Load Balancer Controller, EBS/EFS/FSx CSI drivers, VPC CNI, Karpenter, Velero, Gateway API Controller
- **Custom Policy Creation**: JSON policy documents with path configuration and tagging
- **Auto-Generated Read-Only Policies**: Service-specific read access with console and CloudWatch support
- **Security Features**: Permissions boundaries, MFA enforcement, PGP encryption, cross-account external IDs
- **Multi-Cluster IRSA**: Single role assumable from multiple EKS clusters with namespace isolation

## Main Use Cases

1. **Federated Identity Access**: Configure OIDC or SAML providers for enterprise SSO integration
2. **GitHub Actions CI/CD Authentication**: Set up secure, keyless authentication for GitHub workflows
3. **EKS Workload Identity**: Implement IRSA for Kubernetes pods to access AWS services securely
4. **Cross-Account Role Management**: Create and manage roles for multi-account AWS organizations
5. **User and Group Administration**: Organize IAM users into groups with appropriate permission boundaries
6. **Service Account Automation**: Configure IAM roles for AWS services and applications
7. **Password Policy Enforcement**: Implement organization-wide password security standards
8. **Least-Privilege Policy Creation**: Generate and attach minimal permission policies using custom definitions
9. **Temporary Credential Management**: Enable assume-role patterns for short-lived credentials
10. **Security Audit and Compliance**: Track IAM resource creation and configuration through infrastructure as code

## Submodules

### 1. iam-account
- **Purpose**: Configure account alias and password policy (one per AWS account)
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-account`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-account
- **Key Features**: Account alias, password complexity/length/expiration, reuse prevention, hard expiry option
- **Use Cases**: Organizational security baseline, password standards enforcement

### 2. iam-user
- **Purpose**: Create IAM users with login profiles, access keys, SSH keys, and inline policies
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-user`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-user
- **Key Features**: PGP-encrypted credentials, access key generation, SSH key upload, inline policy support, permissions boundary
- **Use Cases**: Human user accounts, API credentials, CodeCommit SSH access

### 3. iam-group
- **Purpose**: Create IAM groups with users and attached policies
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-group`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-group
- **Key Features**: User membership, policy attachment, MFA enforcement, self-management permissions
- **Use Cases**: Role-based access control, team permissions, delegated credential management

### 4. iam-role
- **Purpose**: Create IAM roles with configurable trust policies for multiple authentication methods
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-role`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-role
- **Key Features**: GitHub OIDC, GitHub Enterprise Server, SAML 2.0, user assumption, instance profiles, permissions boundary
- **Use Cases**: GitHub Actions CI/CD, cross-account access, federated SSO, EC2 instance roles

### 5. iam-policy
- **Purpose**: Create custom IAM policies from JSON documents
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-policy`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-policy
- **Key Features**: JSON policy definition, path configuration, name prefix support, tagging
- **Use Cases**: Custom permissions, least-privilege policies, reusable policy definitions

### 6. iam-read-only-policy
- **Purpose**: Auto-generate read-only policies for specified AWS services
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-read-only-policy`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-read-only-policy
- **Key Features**: Service-specific read access, CloudWatch logs query, web console access, STS actions
- **Use Cases**: Audit roles, monitoring access, read-only developer access

### 7. iam-oidc-provider
- **Purpose**: Create OIDC providers for external identity federation (one per URL per account)
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-oidc-provider`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-oidc-provider
- **Key Features**: GitHub Actions (default), GitHub Enterprise Server, Bitbucket Pipelines, custom providers
- **Use Cases**: CI/CD authentication, external identity federation

### 8. iam-role-for-service-accounts (IRSA)
- **Purpose**: Create IAM roles for EKS service accounts with 20+ pre-built AWS service policies
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-role-for-service-accounts
- **Key Features**: Multi-cluster support, namespace isolation, pre-built policies for controllers and CSI drivers
- **Supported Services**: Cert-Manager, Cluster Autoscaler, External DNS, Load Balancer Controller, EBS/EFS/FSx CSI, VPC CNI, Karpenter, Velero, External Secrets, Gateway API Controller, CloudWatch Observability, Managed Prometheus
- **Use Cases**: Kubernetes pod AWS access, EKS controller authentication, multi-cluster service accounts

## Submodule 1: iam-account

### Description

Configures account-level IAM settings including the AWS account alias and password policy. Instantiate once per AWS account to establish baseline security standards for user authentication.

### Key Features

- Custom AWS account alias for account identification
- Password complexity rules (uppercase, lowercase, numbers, symbols)
- Password expiration with configurable maximum age
- Password reuse prevention with configurable history
- Hard expiry option (forces admin reset after expiration)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `account_alias` | `string` | `""` | AWS IAM account alias |
| `create_account_password_policy` | `bool` | `true` | Whether to create password policy |
| `max_password_age` | `number` | `0` | Days until password expires (0 = never) |
| `minimum_password_length` | `number` | `8` | Minimum password length |
| `require_uppercase_characters` | `bool` | `true` | Require uppercase |
| `require_lowercase_characters` | `bool` | `true` | Require lowercase |
| `require_numbers` | `bool` | `true` | Require numbers |
| `require_symbols` | `bool` | `true` | Require symbols |
| `password_reuse_prevention` | `number` | `null` | Number of previous passwords to block |
| `hard_expiry` | `bool` | `false` | Force admin reset after expiration |

### Main Outputs

| Output | Description |
|--------|-------------|
| `caller_identity_account_id` | AWS account ID |
| `iam_account_password_policy_expire_passwords` | Whether passwords expire |

### Usage Example

```hcl
module "iam_account" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-account"
  version = "~> 6.0"

  account_alias = "my-company-production"

  # Strong password policy
  max_password_age               = 90
  minimum_password_length        = 14
  require_uppercase_characters   = true
  require_lowercase_characters   = true
  require_numbers                = true
  require_symbols                = true
  password_reuse_prevention      = 5
  allow_users_to_change_password = true
}
```

**Note**: If account alias already exists (from Console/Organizations), import the resource before applying.

## Submodule 2: iam-user

### Description

Creates individual IAM users with login profiles, access keys, SSH keys for CodeCommit, and inline policies. Includes PGP encryption support for secure credential distribution.

### Key Features

- Console login profiles with encrypted passwords
- Access keys for programmatic access (API/CLI)
- SSH public keys for CodeCommit
- PGP encryption for credential outputs
- Inline policy support
- Permissions boundary support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | IAM user name |
| `create_login_profile` | `bool` | `true` | Create console login profile |
| `create_access_key` | `bool` | `true` | Create access key |
| `create_ssh_key` | `bool` | `false` | Upload SSH public key |
| `create_inline_policy` | `bool` | `false` | Create inline policy |
| `pgp_key` | `string` | `null` | PGP key (keybase:username or base64) |
| `password_reset_required` | `bool` | `true` | Require password reset on first login |
| `force_destroy` | `bool` | `false` | Destroy even with non-Terraform resources |
| `permissions_boundary` | `string` | `null` | Permissions boundary policy ARN |
| `policies` | `map` | `{}` | Map of policies to attach |

### Main Outputs

| Output | Description |
|--------|-------------|
| `iam_user_name` | IAM user name |
| `iam_user_arn` | User ARN |
| `iam_access_key_id` | Access key ID |
| `iam_access_key_encrypted_secret` | Encrypted access key secret |
| `login_profile_encrypted_password` | Encrypted console password |
| `iam_user_ssh_key_ssh_public_key_id` | SSH public key ID |

### Usage Example

```hcl
module "iam_user" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-user"
  version = "~> 6.0"

  name = "developer.user"

  # PGP-encrypted credentials (CRITICAL for security)
  create_login_profile    = true
  create_access_key       = true
  pgp_key                 = "keybase:devops_team"
  password_reset_required = true

  # SSH key for CodeCommit
  create_ssh_key = true
  ssh_public_key = file("~/.ssh/id_rsa.pub")

  tags = {
    Team = "engineering"
  }
}

# Decrypt: terraform output -raw user_password | base64 -d | keybase pgp decrypt
output "user_password" {
  value     = module.iam_user.login_profile_encrypted_password
  sensitive = true
}
```

**Security Note**: Always use PGP encryption to prevent plaintext credentials in Terraform state.

## Submodule 3: iam-group

### Description

Creates IAM groups for organizing users and managing permissions at scale. Supports managed policies, custom inline policies, MFA enforcement, and self-management capabilities.

### Key Features

- User membership management
- AWS managed and custom policy attachment
- MFA enforcement at group level
- Self-management permissions for credentials/MFA
- Cross-account user membership support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Group name |
| `users` | `list(string)` | `[]` | IAM users to add |
| `users_account_id` | `string` | `null` | Alternate AWS account for users |
| `create_policy` | `bool` | `true` | Create IAM policy for group |
| `permissions` | `map(object)` | `{}` | Custom inline policy statements |
| `policies` | `map(string)` | `{}` | Managed policy ARNs to attach |
| `enable_self_management_permissions` | `bool` | `true` | Allow credential/MFA self-management |
| `enable_mfa_enforcement` | `bool` | `true` | Require MFA for actions |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Group ARN |
| `name` | Group name |
| `users` | List of users in group |
| `policy_arn` | Attached policy ARN |

### Usage Example

```hcl
module "developers_group" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-group"
  version = "~> 6.0"

  name = "developers"

  users = [
    "alice.developer",
    "bob.engineer"
  ]

  enable_self_management_permissions = true
  enable_mfa_enforcement             = true

  # Attach AWS managed policies
  policies = {
    ReadOnly = "arn:aws:iam::aws:policy/ReadOnlyAccess"
    S3Access = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  }

  # Custom permissions
  permissions = {
    AssumeDevRole = {
      actions   = ["sts:AssumeRole"]
      resources = ["arn:aws:iam::123456789012:role/developer-role"]
    }
  }

  tags = { Team = "Engineering" }
}
```

## Submodule 4: iam-role

### Description

Creates IAM roles with configurable trust policies supporting GitHub OIDC, GitHub Enterprise Server, SAML 2.0, user assumption, and cross-account access. Includes instance profile creation option.

### Key Features

- GitHub Actions OIDC (token.actions.githubusercontent.com)
- GitHub Enterprise Server with custom OIDC URLs
- SAML 2.0 federation (Okta, OneLogin, etc.)
- User assumption with optional external ID
- EC2 instance profile creation
- Permissions boundary support
- Inline policy support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `null` | Role name |
| `enable_github_oidc` | `bool` | `false` | Enable GitHub OIDC trust |
| `oidc_wildcard_subjects` | `list(string)` | `[]` | GitHub repos with wildcards (e.g., "org/repo:*") |
| `enable_saml` | `bool` | `false` | Enable SAML provider trust |
| `saml_provider_ids` | `list(string)` | `[]` | SAML provider ARNs |
| `trusted_role_arns` | `list(string)` | `[]` | ARNs allowed to assume role |
| `policies` | `map(string)` | `{}` | Policy ARNs to attach {'name' = 'arn'} |
| `create_instance_profile` | `bool` | `false` | Create EC2 instance profile |
| `create_inline_policy` | `bool` | `false` | Create inline policy |
| `permissions_boundary` | `string` | `null` | Permissions boundary ARN |
| `max_session_duration` | `number` | `3600` | Session duration (seconds, 1-12 hours) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Role ARN |
| `name` | Role name |
| `unique_id` | Role unique ID |
| `instance_profile_arn` | Instance profile ARN (if created) |

### Usage Examples

#### GitHub Actions OIDC Role

```hcl
module "github_oidc_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role"
  version = "~> 6.0"

  name               = "github-actions-deploy"
  enable_github_oidc = true

  # Specific repo/branch restrictions
  oidc_wildcard_subjects = [
    "my-org/my-app:ref:refs/heads/main",
    "my-org/my-app:ref:refs/heads/release/*"
  ]

  policies = {
    ECRPush = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
    ECS     = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  }

  tags = { Purpose = "CICD" }
}
```

#### SAML Federation Role

```hcl
module "saml_admin_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role"
  version = "~> 6.0"

  name        = "sso-administrator"
  enable_saml = true

  saml_provider_ids = [
    "arn:aws:iam::123456789012:saml-provider/corporate-idp"
  ]

  policies = {
    Admin = "arn:aws:iam::aws:policy/AdministratorAccess"
  }

  max_session_duration = 43200  # 12 hours
}
```

#### Cross-Account Access Role

```hcl
module "cross_account_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role"
  version = "~> 6.0"

  name = "cross-account-auditor"

  trusted_role_arns = [
    "arn:aws:iam::111111111111:root",
    "arn:aws:iam::222222222222:role/auditor"
  ]

  policies = {
    ReadOnly = "arn:aws:iam::aws:policy/ReadOnlyAccess"
    Security = "arn:aws:iam::aws:policy/SecurityAudit"
  }
}
```

## Submodule 5: iam-policy

### Description

Creates custom IAM policies from JSON documents. Essential for implementing least-privilege access patterns and creating reusable permission sets.

### Key Features

- JSON policy document support
- Name or name_prefix options
- Configurable policy path
- Resource tagging

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create policy |
| `name` | `string` | `null` | Policy name (conflicts with name_prefix) |
| `name_prefix` | `string` | `null` | Name prefix for auto-generated name |
| `description` | `string` | `null` | Policy description |
| `path` | `string` | `"/"` | IAM hierarchy path |
| `policy` | `string` | required | JSON policy document |
| `tags` | `map(string)` | `{}` | Resource tags |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Policy ARN |
| `id` | Policy ID |
| `name` | Policy name |
| `policy` | Policy document |

### Usage Example

```hcl
module "s3_readonly_policy" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
  version = "~> 6.0"

  name        = "s3-specific-bucket-readonly"
  description = "Read-only access to specific S3 buckets"
  path        = "/custom-policies/"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "S3BucketReadAccess"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:ListBucket"]
        Resource = [
          "arn:aws:s3:::my-app-data",
          "arn:aws:s3:::my-app-data/*"
        ]
      }
    ]
  })

  tags = { Service = "S3", AccessLevel = "ReadOnly" }
}

# Attach to a role
resource "aws_iam_role_policy_attachment" "attach" {
  role       = aws_iam_role.app_role.name
  policy_arn = module.s3_readonly_policy.arn
}
```

## Submodule 6: iam-read-only-policy

### Description

Auto-generates read-only IAM policies for specified AWS services. Addresses limitations in AWS managed read-only policies by enabling granular, service-specific permissions.

### Key Features

- Service-specific read-only access (specify IAM service prefixes)
- CloudWatch logs query support
- Web console browsing support
- Predefined STS actions (caller identity, session token)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | required | Policy name |
| `allowed_services` | `list(string)` | required | AWS service prefixes for read access |
| `allow_cloudwatch_logs_query` | `bool` | `true` | Enable CloudWatch log querying |
| `allow_predefined_sts_actions` | `bool` | `true` | Allow caller identity/session token |
| `allow_web_console_services` | `bool` | `true` | Enable console browsing |
| `web_console_services` | `list(string)` | `["resource-groups", "tag", "health", "ce"]` | Console services |
| `use_name_prefix` | `bool` | `true` | Use name as prefix |
| `path` | `string` | `"/"` | IAM hierarchy path |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Policy ARN |
| `policy_json` | Policy as JSON |

### Usage Example

```hcl
module "audit_readonly_policy" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-read-only-policy"
  version = "~> 6.0"

  name = "audit-readonly"

  # Specify AWS service prefixes
  allowed_services = ["rds", "dynamodb", "ec2", "s3", "lambda"]

  allow_cloudwatch_logs_query = true
  allow_web_console_services  = true

  tags = { Team = "Security", AccessLevel = "ReadOnly" }
}

# Attach to audit role
module "audit_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role"
  version = "~> 6.0"

  name = "audit-role"

  trusted_role_arns = ["arn:aws:iam::123456789012:root"]

  policies = {
    ReadOnly = module.audit_readonly_policy.arn
  }
}
```

## Submodule 7: iam-oidc-provider

### Description

Creates OpenID Connect (OIDC) providers for external identity federation. Enables keyless authentication for CI/CD pipelines. **Note**: AWS limits one OIDC provider per unique URL per account.

### Key Features

- Pre-configured defaults for GitHub Actions
- GitHub Enterprise Server support
- Bitbucket Pipelines support
- Custom OIDC provider URLs
- Automatic TLS certificate thumbprint retrieval

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create provider |
| `url` | `string` | `"https://token.actions.githubusercontent.com"` | OIDC provider URL |
| `client_id_list` | `list(string)` | `[]` | Audience identifiers |
| `tags` | `map(string)` | `{}` | Resource tags |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Provider ARN |
| `url` | Identity provider URL (matches `iss` claim) |

### Usage Examples

#### GitHub Actions (Default)

```hcl
module "github_oidc_provider" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-oidc-provider"
  version = "~> 6.0"

  # Defaults to GitHub Actions URL
  tags = { Purpose = "GitHub Actions" }
}

# Create role that trusts this provider
module "github_actions_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role"
  version = "~> 6.0"

  depends_on         = [module.github_oidc_provider]
  name               = "github-actions-role"
  enable_github_oidc = true

  oidc_wildcard_subjects = ["my-org/my-repo:*"]

  policies = { Deploy = aws_iam_policy.deploy.arn }
}
```

#### Bitbucket Pipelines

```hcl
module "bitbucket_oidc_provider" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-oidc-provider"
  version = "~> 6.0"

  url = "https://api.bitbucket.org/2.0/workspaces/my-workspace/pipelines-config/identity/oidc"

  client_id_list = ["ari:cloud:bitbucket::workspace/my-workspace-uuid"]

  tags = { Purpose = "Bitbucket Pipelines" }
}
```

#### GitHub Enterprise Server

```hcl
module "ghe_oidc_provider" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-oidc-provider"
  version = "~> 6.0"

  url            = "https://github.mycompany.com/_services/token"
  client_id_list = ["https://github.mycompany.com/my-org"]
}
```

## Submodule 8: iam-role-for-service-accounts (IRSA)

### Description

Creates IAM roles for Amazon EKS service accounts (IRSA pattern) with 20+ pre-built AWS service policies. Enables Kubernetes pods to access AWS services using temporary credentials without embedded access keys.

**Note**: AWS recommends migrating to EKS Pod Identity (separate module available) for new deployments.

### Key Features

- Multi-cluster OIDC provider support
- Namespace-scoped service account permissions
- 20+ pre-built controller and CSI driver policies
- Custom policy attachment
- Service-specific ARN restrictions for least-privilege

### Supported AWS Services (Pre-Built Policies)

| Category | Services |
|----------|----------|
| **Autoscaling** | Cluster Autoscaler, Karpenter, Node Termination Handler |
| **Storage** | EBS CSI, EFS CSI, FSx Lustre CSI, FSx OpenZFS CSI, Mountpoint S3 CSI |
| **Networking** | External DNS, VPC CNI, Load Balancer Controller, Gateway API Controller |
| **Secrets** | External Secrets (Secrets Manager, SSM Parameter Store) |
| **Certificates** | Cert-Manager |
| **Monitoring** | CloudWatch Observability, Managed Prometheus |
| **Backup** | Velero |

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `null` | IAM role name |
| `oidc_providers` | `map(object)` | `{}` | Map with `provider_arn` and `namespace_service_accounts` |
| `attach_[service]_policy` | `bool` | `false` | Enable pre-built policy for service |
| `cert_manager_hosted_zone_arns` | `list(string)` | `[]` | Route53 zones for cert management |
| `ebs_csi_kms_cmk_arns` | `list(string)` | `[]` | KMS keys for encrypted EBS |
| `external_dns_hosted_zone_arns` | `list(string)` | `[]` | Route53 zones for External DNS |
| `external_secrets_secrets_manager_arns` | `list(string)` | `[]` | Secrets Manager ARNs |
| `velero_s3_bucket_arns` | `list(string)` | `[]` | S3 buckets for Velero backup |
| `cluster_autoscaler_cluster_names` | `list(string)` | `[]` | EKS cluster names for autoscaler |
| `policies` | `map(string)` | `{}` | Custom policy ARNs to attach |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | IAM role ARN |
| `name` | IAM role name |
| `iam_policy_arn` | AWS-assigned policy ARN |

### Usage Examples

#### AWS Load Balancer Controller

```hcl
data "aws_eks_cluster" "cluster" {
  name = "my-eks-cluster"
}

module "lb_controller_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts"
  version = "~> 6.0"

  name = "aws-load-balancer-controller"

  attach_load_balancer_controller_policy = true

  oidc_providers = {
    main = {
      provider_arn               = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }

  tags = { Application = "AWS Load Balancer Controller" }
}
```

#### External DNS (Multi-Cluster)

```hcl
module "external_dns_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts"
  version = "~> 6.0"

  name = "external-dns"

  attach_external_dns_policy    = true
  external_dns_hosted_zone_arns = [
    "arn:aws:route53:::hostedzone/Z1234567890ABC"
  ]

  oidc_providers = {
    prod = {
      provider_arn               = "arn:aws:iam::123456789012:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/PROD123"
      namespace_service_accounts = ["external-dns:external-dns"]
    }
    staging = {
      provider_arn               = "arn:aws:iam::123456789012:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/STAGE456"
      namespace_service_accounts = ["external-dns:external-dns"]
    }
  }
}
```

#### Cluster Autoscaler

```hcl
module "cluster_autoscaler_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts"
  version = "~> 6.0"

  name = "cluster-autoscaler"

  attach_cluster_autoscaler_policy = true
  cluster_autoscaler_cluster_names = ["my-eks-cluster"]

  oidc_providers = {
    main = {
      provider_arn               = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
      namespace_service_accounts = ["kube-system:cluster-autoscaler"]
    }
  }
}
```

#### Custom Application with EBS + S3

```hcl
resource "aws_iam_policy" "app_s3" {
  name   = "app-s3-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "arn:aws:s3:::my-app-bucket/*"
    }]
  })
}

module "app_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts"
  version = "~> 6.0"

  name = "my-application"

  attach_ebs_csi_policy = true

  policies = { S3Access = aws_iam_policy.app_s3.arn }

  oidc_providers = {
    main = {
      provider_arn               = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
      namespace_service_accounts = ["production:my-app", "staging:my-app"]
    }
  }
}
```

## Best Practices

### Security

1. **Use Temporary Credentials**: Prefer OIDC, SAML, or assume-role patterns over long-lived access keys
2. **PGP Encrypt User Credentials**: Always use `pgp_key` when creating IAM users to prevent plaintext in state
3. **Enable MFA Enforcement**: Use `enable_mfa_enforcement` in groups for privileged access
4. **Implement Password Policies**: Minimum 14 characters, complexity requirements, 90-day expiration, prevent last 5 reuse
5. **Use IRSA for EKS**: Never embed credentials in pods; use iam-role-for-service-accounts
6. **Use OIDC for CI/CD**: GitHub Actions, Bitbucket - eliminates long-lived secrets

### Permission Management

1. **Apply Least Privilege**: Start minimal, add incrementally; use IAM Access Analyzer
2. **Use Permissions Boundaries**: Set maximum permissions for delegated IAM administration
3. **Scope OIDC Trust**: Use specific repo/branch (e.g., `org/repo:ref:refs/heads/main`) not broad wildcards
4. **Namespace-Scope IRSA**: Always specify namespace in `namespace_service_accounts`
5. **Use Pre-Built Controller Policies**: Use `attach_*_policy` flags for standard EKS controllers
6. **One IRSA Role per Application**: Don't share roles across workloads

### Configuration

1. **Pin Module Versions**: Use `version = "~> 6.0"` in production
2. **Set Account Alias**: Configure via iam-account for easier identification
3. **Import Existing Resources**: Check for existing IAM resources before creating new ones
4. **One OIDC Provider per URL**: AWS limits one per unique URL per account; reuse for multiple roles
5. **Enable Self-Management**: Allow users to manage own credentials/MFA via groups
6. **Tag Consistently**: Include Environment, Application, Team tags on all resources

### Operational

1. **Review `terraform plan`**: IAM changes can break production access
2. **Enable CloudTrail**: Log all IAM actions for auditing
3. **Test in Non-Prod First**: Especially for trust policies and OIDC configurations
4. **Regular Permission Audits**: Use IAM Access Analyzer to identify unused permissions

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-iam
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-iam/tree/master/examples
- **AWS IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **IAM Access Analyzer**: https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html
- **IRSA Documentation**: https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
- **EKS Pod Identity** (IRSA alternative): https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html
- **GitHub Actions OIDC**: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services

## Notes for AI Agents

When generating Terraform code with this module:

1. **Always pin version**: Use `version = "~> 6.0"` in module blocks
2. **Prefer roles over users**: Use OIDC/SAML/IRSA instead of creating IAM users with access keys
3. **PGP for user credentials**: If creating users, always set `pgp_key` to prevent plaintext secrets in state
4. **Scope OIDC trust narrowly**: Use specific repo/branch patterns like `org/repo:ref:refs/heads/main`
5. **One OIDC provider per URL**: Reuse existing providers; don't create duplicates
6. **Namespace-scope IRSA**: Always include namespace in `namespace_service_accounts` format `namespace:sa-name`
7. **Use pre-built controller policies**: Prefer `attach_load_balancer_controller_policy = true` over custom policies
8. **Tag all resources**: Include at minimum `tags = { ManagedBy = "terraform" }`
9. **Import before create**: Check if IAM resources exist before creating new ones
10. **EKS Pod Identity**: For new EKS deployments, consider Pod Identity over IRSA
