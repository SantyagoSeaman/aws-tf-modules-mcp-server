# Terraform AWS IAM Module

## Module Information

- **Module Name**: terraform-aws-iam
- **Source**: `terraform-aws-modules/iam/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-iam
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest
- **Latest Version**: Check registry for current version
- **Purpose**: Terraform module that creates and manages AWS IAM resources including users, groups, roles, policies, and OIDC providers
- **Service**: AWS IAM (Identity and Access Management)
- **Category**: Security, Identity Management, Access Control
- **Keywords**: iam, identity, access-management, users, groups, roles, policies, permissions, oidc, saml, authentication, authorization, federated-access, service-accounts, eks, irsa, github-actions, mfa, password-policy, account-alias, trust-policy, assume-role, cross-account, pgp-encryption, access-keys, ssh-keys, login-profile, inline-policy, managed-policy, custom-policy, read-only-policy, least-privilege, aws-security, compliance, audit, credential-management, temporary-credentials
- **Use For**: Managing AWS user authentication and authorization, implementing role-based access control, setting up federated identity access, configuring GitHub Actions authentication, managing EKS service account permissions, enforcing password policies across AWS accounts, creating cross-account access roles, managing user credentials securely, implementing least-privilege security, setting up CI/CD pipeline authentication, configuring SSO integrations, managing service-to-service authentication

## Description

This Terraform module provides a comprehensive solution for managing AWS Identity and Access Management (IAM) resources. It supports creating and configuring IAM accounts, users, groups, roles, policies, and OpenID Connect (OIDC) providers through a modular architecture. Each submodule focuses on a specific IAM resource type, enabling flexible and granular control over authentication and authorization in AWS environments.

The module addresses common IAM management challenges by providing pre-configured patterns for complex scenarios such as federated identity access, cross-account role assumption, EKS service account integration (IRSA), and GitHub Actions authentication. It supports modern authentication methods including OIDC and SAML federation, while also handling traditional IAM user management with secure credential handling through PGP encryption.

Key architectural features include support for multiple authentication providers, customizable password policies at the account level, flexible policy attachment mechanisms, and seamless integration with Kubernetes workloads running on Amazon EKS. The module follows AWS security best practices by enabling MFA enforcement, supporting temporary credentials, and facilitating implementation of the principle of least privilege through granular permission controls.

## Key Features

- **Eight Specialized Submodules**: Modular architecture with iam-account, iam-user, iam-group, iam-role, iam-policy, iam-read-only-policy, iam-oidc-provider, and iam-role-for-service-accounts
- **Account-Level Configuration**: Set account alias and enforce organization-wide password policies
- **Password Policy Enforcement**: Configure complexity requirements, expiration rules, and reuse prevention
- **IAM User Management**: Create users with login profiles, access keys, SSH keys, and PGP-encrypted credentials
- **Group-Based Access Control**: Organize users into groups with attached policies and self-management permissions
- **IAM Role Creation**: Support for service roles, cross-account access, and federated identity assumption
- **OIDC Provider Support**: Integration with GitHub, GitHub Enterprise Server, Bitbucket, and other OpenID Connect providers
- **SAML Federation**: Support for SAML 2.0 identity providers for enterprise SSO integration
- **GitHub Actions Authentication**: Native support for GitHub OIDC workflows with configurable trust policies
- **EKS Service Account Roles (IRSA)**: Create IAM roles for Kubernetes service accounts with pre-configured controller policies
- **Pre-Built Controller Policies**: Support for Cert-Manager, Cluster Autoscaler, External DNS, Load Balancer Controller, EBS/EFS CSI drivers, and more
- **Custom Policy Creation**: Build and attach custom IAM policies with JSON policy documents
- **Read-Only Policies**: Generate read-only access policies scoped to specific AWS services
- **Multi-Policy Attachment**: Attach multiple managed and custom policies to roles and groups
- **Inline Policy Support**: Define and attach inline policies directly to users and roles
- **MFA Enforcement**: Configure multi-factor authentication requirements at the group level
- **Self-Management Permissions**: Allow users to manage their own credentials and MFA devices
- **Cross-Account Access Patterns**: Simplified configuration for trusted account relationships
- **Credential Encryption**: Built-in PGP key support for encrypting sensitive outputs
- **Force Destroy Protection**: Configurable safeguards for user and resource deletion
- **Comprehensive Tagging**: Support for resource tagging across all IAM resources
- **Flexible Trust Policies**: Customizable trust relationships with wildcard and specific subject support
- **Multi-Cluster Support**: Single role can be assumed by service accounts across multiple EKS clusters
- **Namespace Isolation**: Configure service account permissions per Kubernetes namespace

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

## Requirements

### Terraform Version
- **Terraform**: >= 1.5.7

### Provider Requirements
- **AWS Provider**: >= 6.0
- **TLS Provider**: >= 3.0 (for OIDC provider submodule)

## Submodules

### 1. iam-account
- **Purpose**: Configure account-wide settings including account alias and password policy
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-account`
- **Key Features**: Account alias management, password complexity rules, password expiration settings, reuse prevention
- **Use Cases**: Setting organizational security baseline, enforcing password standards, configuring account identity

### 2. iam-user
- **Purpose**: Create IAM users with login profiles, access keys, and SSH keys
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-user`
- **Key Features**: PGP-encrypted credentials, access key generation, SSH key upload, inline policy support
- **Use Cases**: Creating human user accounts, generating API credentials, managing developer access, secure credential distribution

### 3. iam-group
- **Purpose**: Create IAM groups and assign users with attached policies
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-group`
- **Key Features**: User membership management, policy attachment, self-management permissions, MFA enforcement
- **Use Cases**: Role-based access control, team-based permissions, delegated credential management, department-level access

### 4. iam-role
- **Purpose**: Create IAM roles for service accounts, cross-account access, and federated identity
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-role`
- **Key Features**: GitHub OIDC support, SAML federation, custom trust policies, multi-policy attachment
- **Use Cases**: GitHub Actions authentication, service-to-service access, cross-account roles, federated SSO access

### 5. iam-policy
- **Purpose**: Create custom IAM policies with JSON policy documents
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-policy`
- **Key Features**: Custom policy definition, policy path configuration, tagging support
- **Use Cases**: Defining granular permissions, implementing least-privilege access, creating reusable policies

### 6. iam-read-only-policy
- **Purpose**: Generate read-only access policies for AWS services
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-read-only-policy`
- **Key Features**: Service-specific read access, configurable scope
- **Use Cases**: Audit access, monitoring roles, reporting accounts, read-only developer access

### 7. iam-oidc-provider
- **Purpose**: Create OpenID Connect providers for external identity integration
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-oidc-provider`
- **Key Features**: GitHub support, Bitbucket integration, custom OIDC provider URLs, client ID configuration
- **Use Cases**: GitHub Actions trust relationship, Bitbucket Pipelines authentication, third-party identity federation

### 8. iam-role-for-service-accounts
- **Purpose**: Create IAM roles for EKS service accounts with pre-configured controller policies
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts`
- **Key Features**: IRSA support, multiple cluster integration, pre-built controller policies, namespace-scoped permissions
- **Use Cases**: Kubernetes pod permissions, EKS controller authentication, multi-cluster service accounts, cloud-native application access

## Submodule 1: iam-account

### Description

The iam-account submodule configures account-level IAM settings including the AWS account alias and password policy. This submodule is designed to be instantiated once per AWS account to establish baseline security standards for user authentication. It enables centralized control over password requirements, expiration rules, and complexity standards that apply to all IAM users within the account.

### Key Features

- Set custom AWS account alias for easier account identification
- Configure minimum password length requirements
- Enforce password complexity rules (uppercase, lowercase, numbers, symbols)
- Set password expiration policies with configurable maximum age
- Implement password reuse prevention with configurable history
- Allow or restrict users from changing their own passwords
- Control password reset requirements for new users

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `account_alias` | `string` | `""` | AWS IAM account alias for the account |
| `max_password_age` | `number` | `0` | Number of days password is valid (0 = never expires) |
| `minimum_password_length` | `number` | `8` | Minimum length required for IAM user passwords |
| `require_uppercase_characters` | `bool` | `true` | Require at least one uppercase character |
| `require_lowercase_characters` | `bool` | `true` | Require at least one lowercase character |
| `require_numbers` | `bool` | `true` | Require at least one number |
| `require_symbols` | `bool` | `true` | Require at least one non-alphanumeric character |
| `password_reuse_prevention` | `number` | `null` | Number of previous passwords to prevent reuse |
| `allow_users_to_change_password` | `bool` | `true` | Allow users to change their own password |

### Main Outputs

| Output | Description |
|--------|-------------|
| `caller_identity_account_id` | AWS account ID |
| `iam_account_password_policy_expire_passwords` | Indicates whether passwords expire based on max_password_age |

### Usage Example

```hcl
module "iam_account" {
  source = "terraform-aws-modules/iam/aws//modules/iam-account"

  account_alias = "my-company-production"

  # Strong password policy
  max_password_age               = 90
  minimum_password_length        = 24
  require_uppercase_characters   = true
  require_lowercase_characters   = true
  require_numbers                = true
  require_symbols                = true
  password_reuse_prevention      = 5
  allow_users_to_change_password = true
}
```

## Submodule 2: iam-user

### Description

The iam-user submodule creates individual IAM users with flexible configuration options for authentication methods and credentials. It supports creating console login profiles with passwords, programmatic access keys for API/CLI usage, and SSH keys for AWS CodeCommit. The submodule includes built-in support for PGP encryption of sensitive credentials, ensuring secure distribution of passwords and access keys to end users.

### Key Features

- Create IAM users with customizable names
- Generate console login profiles with encrypted passwords
- Create access keys for programmatic access (API/CLI)
- Upload SSH public keys for CodeCommit access
- PGP encryption support for sensitive credential outputs
- Attach inline policies directly to users
- Force destroy option for users with non-Terraform managed resources
- Configurable password reset requirements
- Comprehensive tagging support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Desired name for the IAM user |
| `create_login_profile` | `bool` | `true` | Whether to create IAM user login profile |
| `create_access_key` | `bool` | `true` | Whether to create IAM access key |
| `pgp_key` | `string` | `""` | PGP key (keybase:username or base64-encoded) for credential encryption |
| `password_reset_required` | `bool` | `true` | Whether user must reset password on first login |
| `force_destroy` | `bool` | `false` | Destroy user even if it has non-Terraform-managed resources |
| `upload_ssh_key` | `bool` | `false` | Whether to upload SSH public key |
| `ssh_public_key` | `string` | `""` | SSH public key for CodeCommit |

### Main Outputs

| Output | Description |
|--------|-------------|
| `iam_user_name` | IAM user name |
| `iam_user_arn` | ARN assigned to the user |
| `iam_access_key_id` | Access key ID |
| `iam_access_key_encrypted_secret` | Encrypted secret for access key |
| `login_profile_encrypted_password` | Encrypted password for console login |
| `iam_user_ssh_key_ssh_public_key_id` | Unique identifier for SSH public key |
| `iam_user_ssh_key_fingerprint` | MD5 fingerprint of SSH key |

### Usage Example

```hcl
module "iam_user" {
  source = "terraform-aws-modules/iam/aws//modules/iam-user"

  name = "developer.user"

  # Create login profile with PGP-encrypted password
  create_login_profile    = true
  pgp_key                 = "keybase:devops_team"
  password_reset_required = true

  # Create access key for API access
  create_access_key = true

  # Optional: Upload SSH key for CodeCommit
  upload_ssh_key    = true
  ssh_public_key    = file("~/.ssh/id_rsa.pub")

  # Allow force destroy for development environments
  force_destroy = true

  tags = {
    Environment = "development"
    Team        = "engineering"
    ManagedBy   = "terraform"
  }
}

# Output the encrypted credentials
output "user_password" {
  value       = module.iam_user.login_profile_encrypted_password
  description = "Encrypted password - decrypt with: terraform output -raw user_password | base64 -d | keybase pgp decrypt"
  sensitive   = true
}
```

## Submodule 3: iam-group

### Description

The iam-group submodule creates IAM groups that serve as containers for organizing users and managing permissions at scale. Groups enable administrators to assign permissions to multiple users simultaneously rather than managing individual user permissions. The submodule supports attaching both AWS managed policies and custom policies, as well as enabling self-service capabilities like password changes and MFA device management.

### Key Features

- Create IAM groups with descriptive names
- Add multiple IAM users to groups
- Attach AWS managed policies by ARN
- Define custom permissions with inline policy statements
- Enable self-management permissions for users
- Enforce MFA requirements at the group level
- Support for multiple policy attachments
- Comprehensive resource tagging

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of IAM group |
| `users` | `list(string)` | `[]` | List of IAM users to add to the group |
| `permissions` | `map(object)` | `{}` | Map of inline policy statements with actions and resources |
| `policies` | `map(string)` | `{}` | Map of policy ARNs to attach to the group |
| `enable_self_management_permissions` | `bool` | `false` | Allow users to manage own credentials, MFA, and SSH keys |
| `enable_mfa_enforcement` | `bool` | `false` | Require MFA for all actions |
| `tags` | `map(string)` | `{}` | Tags to apply to IAM resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `iam_group_arn` | ARN of IAM group |
| `iam_group_name` | Name of IAM group |
| `iam_group_users` | List of IAM users in the group |
| `iam_policy_arn` | ARN of the custom group policy |

### Usage Example

```hcl
module "developers_group" {
  source = "terraform-aws-modules/iam/aws//modules/iam-group"

  name = "developers"

  # Add users to group
  users = [
    "alice.developer",
    "bob.engineer",
    "carol.coder"
  ]

  # Enable self-management
  enable_self_management_permissions = true

  # Attach AWS managed policies
  policies = {
    ReadOnly = "arn:aws:iam::aws:policy/ReadOnlyAccess"
    S3Access = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  }

  # Add custom permissions for specific resources
  permissions = {
    AssumeDevRole = {
      actions = ["sts:AssumeRole"]
      resources = [
        "arn:aws:iam::123456789012:role/developer-role"
      ]
    }
    EC2Describe = {
      actions = [
        "ec2:Describe*",
        "ec2:List*"
      ]
      resources = ["*"]
    }
  }

  tags = {
    Team        = "Engineering"
    Purpose     = "Development"
    Environment = "shared"
  }
}
```

## Submodule 4: iam-role

### Description

The iam-role submodule creates IAM roles that can be assumed by trusted entities including AWS services, other AWS accounts, or federated identity providers. It provides comprehensive support for modern authentication patterns including GitHub OIDC for CI/CD pipelines, SAML federation for enterprise SSO, and cross-account access. The submodule simplifies complex trust policy configuration while maintaining flexibility for custom trust relationships.

### Key Features

- Create IAM roles with configurable trust policies
- GitHub OIDC integration for GitHub Actions workflows
- GitHub Enterprise Server support with custom provider URLs
- SAML 2.0 federation support for enterprise identity providers
- Cross-account role assumption with trusted account configuration
- Service-linked roles for AWS services
- Attach multiple managed and custom policies
- Wildcard and specific subject patterns for OIDC trust
- Configurable session duration and conditions
- Support for external ID in trust policies

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `role_name` | `string` | `""` | Name of IAM role |
| `enable_github_oidc` | `bool` | `false` | Enable GitHub OIDC provider trust |
| `oidc_provider_urls` | `list(string)` | `["token.actions.githubusercontent.com"]` | List of OIDC provider URLs |
| `oidc_audiences` | `list(string)` | `["sts.amazonaws.com"]` | List of audiences for OIDC provider |
| `oidc_wildcard_subjects` | `list(string)` | `[]` | GitHub repositories allowed to assume role (e.g., "org/repo:*") |
| `enable_saml` | `bool` | `false` | Enable SAML provider trust |
| `saml_provider_ids` | `list(string)` | `[]` | List of SAML provider ARNs |
| `trusted_role_arns` | `list(string)` | `[]` | ARNs of AWS entities who can assume role |
| `policies` | `map(string)` | `{}` | Map of policy ARNs to attach |
| `max_session_duration` | `number` | `3600` | Maximum session duration in seconds |

### Main Outputs

| Output | Description |
|--------|-------------|
| `iam_role_arn` | ARN of IAM role |
| `iam_role_name` | Name of IAM role |
| `iam_role_unique_id` | Unique ID of IAM role |

### Usage Examples

#### Example 1: GitHub Actions OIDC Role

```hcl
module "github_oidc_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role"

  role_name = "github-actions-deploy"

  # Enable GitHub OIDC trust
  enable_github_oidc = true

  # Allow specific repositories to assume this role
  oidc_wildcard_subjects = [
    "terraform-aws-modules/terraform-aws-iam:*",
    "my-org/my-app:ref:refs/heads/main"
  ]

  # Attach policies for deployment
  policies = {
    S3Deploy       = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
    ECRPush        = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
    ECSTaskExec    = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  }

  tags = {
    Purpose = "CICD"
    Tool    = "GitHub Actions"
  }
}
```

#### Example 2: SAML Federation Role

```hcl
module "saml_sso_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role"

  role_name = "sso-administrator"

  # Enable SAML trust
  enable_saml = true
  saml_provider_ids = [
    "arn:aws:iam::123456789012:saml-provider/corporate-idp"
  ]

  # Attach administrator policy
  policies = {
    AdministratorAccess = "arn:aws:iam::aws:policy/AdministratorAccess"
  }

  max_session_duration = 43200  # 12 hours

  tags = {
    AccessType = "SSO"
    Level      = "Administrator"
  }
}
```

#### Example 3: Cross-Account Access Role

```hcl
module "cross_account_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role"

  role_name = "cross-account-auditor"

  # Trust specific accounts
  trusted_role_arns = [
    "arn:aws:iam::111111111111:root",
    "arn:aws:iam::222222222222:role/auditor"
  ]

  # Read-only access
  policies = {
    ReadOnly = "arn:aws:iam::aws:policy/ReadOnlyAccess"
    Security = "arn:aws:iam::aws:policy/SecurityAudit"
  }

  tags = {
    Purpose = "Security Audit"
    Access  = "Cross-Account"
  }
}
```

## Submodule 5: iam-policy

### Description

The iam-policy submodule creates custom IAM policies with user-defined permissions. It provides a streamlined interface for defining policies using JSON policy documents, enabling precise control over resource access permissions. The submodule is essential for implementing least-privilege access patterns and creating reusable permission sets that can be attached to users, groups, or roles.

### Key Features

- Create custom IAM policies with JSON documents
- Support for policy name and name_prefix options
- Configurable policy path for organizational hierarchy
- Optional policy descriptions for documentation
- Resource tagging support
- Conditional policy creation with create flag

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the IAM policy |
| `name` | `string` | `""` | Name of IAM policy (conflicts with name_prefix) |
| `name_prefix` | `string` | `""` | Name prefix for IAM policy |
| `description` | `string` | `""` | Description of the IAM policy |
| `path` | `string` | `"/"` | Path in which to create the policy |
| `policy` | `string` | `""` | JSON policy document |
| `tags` | `map(string)` | `{}` | Tags to apply to the policy |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | ARN of the IAM policy |
| `id` | ID of the IAM policy |
| `name` | Name of the IAM policy |
| `policy` | Policy document |

### Usage Example

```hcl
module "s3_readonly_policy" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name        = "s3-specific-bucket-readonly"
  description = "Policy for read-only access to specific S3 buckets"
  path        = "/custom-policies/"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3BucketReadAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:ListBucket",
          "s3:ListBucketVersions"
        ]
        Resource = [
          "arn:aws:s3:::my-app-data",
          "arn:aws:s3:::my-app-data/*"
        ]
      },
      {
        Sid      = "S3ListAllBuckets"
        Effect   = "Allow"
        Action   = "s3:ListAllMyBuckets"
        Resource = "*"
      }
    ]
  })

  tags = {
    PolicyType  = "Custom"
    Service     = "S3"
    AccessLevel = "ReadOnly"
  }
}

# Example: Attach to a role
resource "aws_iam_role_policy_attachment" "attach" {
  role       = aws_iam_role.app_role.name
  policy_arn = module.s3_readonly_policy.arn
}
```

## Submodule 6: iam-read-only-policy

### Description

The iam-read-only-policy submodule generates IAM policies that grant read-only access to AWS services. This submodule is particularly useful for creating auditor roles, monitoring accounts, or developer access that requires visibility without modification privileges. It provides a simplified interface for generating consistent read-only policies scoped to specific AWS services.

### Key Features

- Generate read-only access policies for AWS services
- Configurable scope for specific services or global read access
- Consistent read-only permission patterns
- Simplified policy creation without manual JSON authoring
- Support for tagging and organizational paths

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the read-only policy |
| `description` | `string` | `""` | Description of the policy |
| `path` | `string` | `"/"` | Path in which to create the policy |
| `tags` | `map(string)` | `{}` | Tags to apply to the policy |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | ARN of the read-only policy |
| `id` | ID of the policy |
| `name` | Name of the policy |

### Usage Example

```hcl
module "monitoring_readonly_policy" {
  source = "terraform-aws-modules/iam/aws//modules/iam-read-only-policy"

  name        = "monitoring-team-readonly"
  description = "Read-only access for monitoring and observability team"
  path        = "/department/monitoring/"

  tags = {
    Team        = "Monitoring"
    AccessLevel = "ReadOnly"
    Purpose     = "Observability"
  }
}

# Use with a role for monitoring team
module "monitoring_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role"

  role_name = "monitoring-team-role"

  trusted_role_arns = [
    "arn:aws:iam::123456789012:root"
  ]

  policies = {
    ReadOnly = module.monitoring_readonly_policy.arn
  }
}
```

## Submodule 7: iam-oidc-provider

### Description

The iam-oidc-provider submodule creates OpenID Connect (OIDC) providers that enable AWS to trust external identity providers such as GitHub, Bitbucket, and other OIDC-compliant services. This is essential for implementing keyless authentication patterns in CI/CD pipelines and enabling federated access without managing long-lived credentials. Note that AWS limits each account to one OIDC provider per unique URL.

### Key Features

- Create OIDC providers for external identity federation
- Pre-configured defaults for GitHub Actions
- Support for Bitbucket Pipelines and custom OIDC providers
- Configurable client ID lists (audiences)
- Automatic TLS certificate thumbprint retrieval
- Resource tagging support
- Conditional provider creation

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether to create the OIDC provider |
| `url` | `string` | `"https://token.actions.githubusercontent.com"` | URL of the OIDC identity provider |
| `client_id_list` | `list(string)` | `["sts.amazonaws.com"]` | List of client IDs (audiences) |
| `tags` | `map(string)` | `{}` | Tags to apply to the provider |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | ARN assigned by AWS to the OIDC provider |
| `url` | URL of the identity provider |

### Usage Examples

#### Example 1: GitHub Actions OIDC Provider

```hcl
module "github_oidc_provider" {
  source = "terraform-aws-modules/iam/aws//modules/iam-oidc-provider"

  # Default URL is already set for GitHub Actions
  # url = "https://token.actions.githubusercontent.com"

  tags = {
    Environment = "production"
    Purpose     = "GitHub Actions Authentication"
  }
}

# Use with a role to allow GitHub Actions access
module "github_actions_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role"

  depends_on = [module.github_oidc_provider]

  role_name          = "github-actions-role"
  enable_github_oidc = true

  oidc_wildcard_subjects = [
    "my-org/my-repo:*"
  ]

  policies = {
    Deploy = aws_iam_policy.deployment_policy.arn
  }
}
```

#### Example 2: Bitbucket Pipelines OIDC Provider

```hcl
module "bitbucket_oidc_provider" {
  source = "terraform-aws-modules/iam/aws//modules/iam-oidc-provider"

  url = "https://api.bitbucket.org/2.0/workspaces/my-workspace/pipelines-config/identity/oidc"

  client_id_list = [
    "ari:cloud:bitbucket::workspace/my-workspace-uuid"
  ]

  tags = {
    Environment = "production"
    Purpose     = "Bitbucket Pipelines Authentication"
  }
}
```

#### Example 3: GitHub Enterprise Server OIDC Provider

```hcl
module "github_enterprise_oidc_provider" {
  source = "terraform-aws-modules/iam/aws//modules/iam-oidc-provider"

  url = "https://github.mycompany.com/_services/token"

  client_id_list = [
    "https://github.mycompany.com/my-org"
  ]

  tags = {
    Environment = "production"
    Purpose     = "GitHub Enterprise Authentication"
    Managed     = "Internal IT"
  }
}
```

## Submodule 8: iam-role-for-service-accounts

### Description

The iam-role-for-service-accounts submodule creates IAM roles specifically designed for Amazon EKS (Elastic Kubernetes Service) service accounts, implementing the IAM Roles for Service Accounts (IRSA) pattern. This enables Kubernetes pods to securely access AWS services using temporary credentials without embedding long-lived access keys. The submodule includes pre-configured policies for popular Kubernetes controllers and operators, simplifying the setup of cloud-native applications.

### Key Features

- Create IAM roles for Kubernetes service accounts (IRSA pattern)
- Support multiple OIDC providers and EKS clusters simultaneously
- Namespace-scoped service account permissions
- Pre-built policies for common Kubernetes controllers
- Support for Cert-Manager, Cluster Autoscaler, External DNS, and Load Balancer Controller
- EBS CSI Driver, EFS CSI Driver, and FSx CSI Driver policies
- VPC CNI, Karpenter, and Velero backup policies
- Custom policy attachment support
- Multi-cluster service account configuration
- Comprehensive tagging for Kubernetes resource tracking

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the IAM role |
| `oidc_providers` | `map(object)` | `{}` | Map of OIDC providers with provider_arn and namespace_service_accounts |
| `attach_ebs_csi_policy` | `bool` | `false` | Attach policy for EBS CSI driver |
| `attach_efs_csi_policy` | `bool` | `false` | Attach policy for EFS CSI driver |
| `attach_external_dns_policy` | `bool` | `false` | Attach policy for External DNS |
| `attach_load_balancer_controller_policy` | `bool` | `false` | Attach policy for AWS Load Balancer Controller |
| `attach_cluster_autoscaler_policy` | `bool` | `false` | Attach policy for Cluster Autoscaler |
| `attach_cert_manager_policy` | `bool` | `false` | Attach policy for Cert-Manager |
| `attach_vpc_cni_policy` | `bool` | `false` | Attach policy for VPC CNI |
| `policies` | `map(string)` | `{}` | Map of custom policy ARNs to attach |

### Main Outputs

| Output | Description |
|--------|-------------|
| `iam_role_arn` | ARN of created IAM role |
| `iam_role_name` | Name of IAM role |
| `iam_role_unique_id` | Unique ID of IAM role |
| `iam_policy_arn` | ARN of the IAM policy (if created) |

### Usage Examples

#### Example 1: AWS Load Balancer Controller Role

```hcl
# First, get the EKS cluster OIDC provider ARN
data "aws_eks_cluster" "cluster" {
  name = "my-eks-cluster"
}

module "lb_controller_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts"

  name = "aws-load-balancer-controller"

  # Attach the pre-configured Load Balancer Controller policy
  attach_load_balancer_controller_policy = true

  oidc_providers = {
    main = {
      provider_arn               = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }

  tags = {
    Application = "AWS Load Balancer Controller"
    Environment = "production"
  }
}
```

#### Example 2: External DNS with Multiple Clusters

```hcl
module "external_dns_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts"

  name = "external-dns"

  # Attach External DNS policy
  attach_external_dns_policy = true
  external_dns_hosted_zone_arns = [
    "arn:aws:route53:::hostedzone/Z1234567890ABC",
    "arn:aws:route53:::hostedzone/Z0987654321XYZ"
  ]

  # Allow service accounts from multiple clusters
  oidc_providers = {
    prod_cluster = {
      provider_arn               = "arn:aws:iam::123456789012:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/PROD123"
      namespace_service_accounts = ["external-dns:external-dns"]
    }
    staging_cluster = {
      provider_arn               = "arn:aws:iam::123456789012:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/STAGE456"
      namespace_service_accounts = ["external-dns:external-dns"]
    }
  }

  tags = {
    Application = "External DNS"
    Purpose     = "DNS Management"
  }
}
```

#### Example 3: Custom Application with EBS and S3 Access

```hcl
# Create custom S3 policy
resource "aws_iam_policy" "app_s3_policy" {
  name        = "app-s3-access"
  description = "S3 access for application"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "arn:aws:s3:::my-app-bucket/*"
      }
    ]
  })
}

module "app_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts"

  name = "my-application"

  # Enable EBS CSI policy for persistent volumes
  attach_ebs_csi_policy = true

  # Attach custom S3 policy
  policies = {
    S3Access = aws_iam_policy.app_s3_policy.arn
  }

  oidc_providers = {
    main = {
      provider_arn = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
      namespace_service_accounts = [
        "production:my-app",
        "staging:my-app"
      ]
    }
  }

  tags = {
    Application = "MyApp"
    Managed     = "Terraform"
  }
}
```

#### Example 4: Cluster Autoscaler

```hcl
module "cluster_autoscaler_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts"

  name = "cluster-autoscaler"

  attach_cluster_autoscaler_policy = true
  cluster_autoscaler_cluster_names = ["my-eks-cluster"]

  oidc_providers = {
    main = {
      provider_arn               = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
      namespace_service_accounts = ["kube-system:cluster-autoscaler"]
    }
  }

  tags = {
    Application = "Cluster Autoscaler"
    Purpose     = "Auto Scaling"
  }
}
```

## Best Practices

### Security and Authentication

1. **Use Temporary Credentials**: Always prefer IAM roles with temporary credentials over long-lived access keys. Use OIDC, SAML, or assume-role patterns instead of creating IAM users with access keys.
2. **Enable Multi-Factor Authentication**: Use `enable_mfa_enforcement` in IAM groups for privileged access and require MFA for sensitive operations through policy conditions.
3. **Implement Strong Password Policies**: Configure account-level password policies with minimum 24 characters, complexity requirements, 90-day expiration, and prevent reuse of last 5 passwords.
4. **Encrypt Sensitive Outputs**: Always use PGP encryption (`pgp_key` parameter) when creating IAM users to securely distribute passwords and access keys.
5. **Rotate Credentials Regularly**: Set `max_password_age` to enforce password rotation and implement processes to rotate access keys every 90 days or less.
6. **Use IRSA for Kubernetes**: Implement IAM Roles for Service Accounts (IRSA) for all EKS workloads instead of using node instance profiles or embedding credentials.
7. **Leverage OIDC for CI/CD**: Use GitHub OIDC or similar federated identity for CI/CD pipelines to eliminate long-lived secrets in deployment workflows.
8. **Implement External ID for Cross-Account**: Use external IDs in trust policies when granting third-party access to prevent confused deputy attacks.

### Permission Management

1. **Apply Least Privilege**: Start with minimal permissions and incrementally add only what's needed. Use IAM Access Analyzer to generate least-privilege policies from CloudTrail logs.
2. **Use Policy Boundaries**: Implement permissions boundaries to set maximum permissions for delegated IAM administration and prevent privilege escalation.
3. **Separate Duties with Groups**: Organize users into groups by role (developers, operators, administrators) and assign permissions at the group level rather than to individual users.
4. **Prefer Managed Policies**: Start with AWS managed policies and create custom policies only when necessary for specific business requirements.
5. **Use Policy Conditions**: Add condition statements to policies to enforce additional security controls like source IP restrictions, MFA requirements, or time-based access.
6. **Scope Service Roles**: When creating service-linked roles, limit permissions to specific resources using conditions and resource ARNs rather than using wildcards.
7. **Regular Permission Audits**: Use AWS IAM Access Analyzer and CloudTrail to identify unused permissions and remove them to reduce security exposure.
8. **Document Custom Policies**: Always add descriptive `description` fields to custom policies explaining their purpose and use case for future maintenance.

### Role and OIDC Configuration

1. **Limit OIDC Trust Scope**: Use specific repository and branch references in `oidc_wildcard_subjects` rather than broad wildcards (prefer `org/repo:ref:refs/heads/main` over `org/*:*`).
2. **Set Appropriate Session Durations**: Configure `max_session_duration` based on actual needs - shorter durations (1-4 hours) for interactive access, longer for automated processes.
3. **Use Multiple Service Accounts per Cluster**: Create separate IRSA roles for each application or controller rather than sharing roles across workloads.
4. **Namespace Isolation**: Always specify namespace in `namespace_service_accounts` to prevent service accounts in other namespaces from assuming the role.
5. **Tag All Resources**: Implement comprehensive tagging strategy including Environment, Application, Owner, and CostCenter for resource tracking and cost allocation.
6. **Pre-configured Controller Policies**: Use built-in controller policies (`attach_load_balancer_controller_policy`, etc.) rather than creating custom policies for standard Kubernetes controllers.
7. **GitHub Enterprise Configuration**: For GitHub Enterprise Server, specify custom `oidc_provider_urls` and `oidc_audiences` matching your enterprise instance configuration.
8. **One OIDC Provider per URL**: Remember AWS limits one OIDC provider per unique URL per account. Reuse existing providers for multiple roles.

### Account and User Management

1. **Set Account Alias**: Always configure a descriptive account alias using iam-account module for easier account identification in console and CLI.
2. **Enable Self-Management**: Set `enable_self_management_permissions = true` in groups to allow users to manage their own passwords, MFA devices, and access keys without admin intervention.
3. **Force Password Reset**: Keep `password_reset_required = true` (default) for new users to ensure they set their own password on first login.
4. **Careful with Force Destroy**: Only set `force_destroy = true` in development/testing environments. Keep it false in production to prevent accidental user deletion with active resources.
5. **Use SSH Keys for CodeCommit**: When developers need CodeCommit access, use `upload_ssh_key` option instead of generating HTTPS credentials for better security.
6. **Limit Login Profile Creation**: Only create login profiles (`create_login_profile = true`) for users who need console access. Service accounts should use roles, not IAM users.
7. **User Naming Conventions**: Adopt consistent naming conventions (e.g., firstname.lastname or email prefix) for better user identification and management.

### Operational Excellence

1. **Infrastructure as Code**: Manage all IAM resources through Terraform rather than manual console changes to ensure consistency and auditability.
2. **Use Terraform Workspaces**: Separate IAM configurations by environment (dev, staging, prod) using workspaces or separate state files to prevent cross-environment permission leaks.
3. **Import Existing Resources**: Before creating new IAM resources, check for existing ones and use `terraform import` to bring them under management.
4. **Plan Before Apply**: Always run `terraform plan` and carefully review IAM changes before applying, as permission changes can break production access.
5. **Module Version Pinning**: Pin module versions in production (e.g., `version = "~> 5.0"`) to prevent unexpected changes from module updates.
6. **Enable CloudTrail**: Ensure CloudTrail is enabled to log all IAM actions for security auditing and compliance requirements.
7. **Monitor Access Patterns**: Use IAM Access Analyzer, CloudWatch, and AWS Config to continuously monitor IAM configurations and access patterns.
8. **Test in Non-Production**: Test IAM changes in development environments first, especially for complex role trust policies and OIDC configurations.

### High Availability and Disaster Recovery

1. **Multi-Region Considerations**: IAM is a global service, but OIDC providers and roles should be created in each account that needs them.
2. **Backup State Files**: Ensure Terraform state files containing IAM configurations are backed up and version controlled (using remote state with versioning).
3. **Document Emergency Access**: Maintain documented break-glass procedures for emergency access including root account MFA recovery.
4. **Cross-Account Backup Roles**: Create cross-account roles for backup and disaster recovery purposes with appropriate permissions boundaries.

### Compliance and Governance

1. **Enable AWS Config Rules**: Use AWS Config rules to continuously monitor IAM configurations for compliance with organizational policies.
2. **Regular Access Reviews**: Implement quarterly access reviews to verify users still need their assigned permissions and groups.
3. **Use AWS Organizations SCPs**: Implement Service Control Policies at the organization level to enforce guardrails that can't be overridden by IAM policies.
4. **Audit Trail Retention**: Retain CloudTrail logs of IAM actions for at least 90 days, or longer based on compliance requirements.
5. **Policy Validation**: Use IAM Access Analyzer policy validation before deploying new policies to identify syntax errors and security warnings.
6. **Separation of Duties**: Never grant both IAM administrative permissions and other resource permissions to the same role or user.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-iam
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-iam/tree/master/examples
- **AWS IAM Documentation**: https://docs.aws.amazon.com/IAM/latest/UserGuide/
- **IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **IAM Access Analyzer**: https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html
- **IRSA Documentation**: https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
- **GitHub Actions OIDC**: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services
- **AWS Security Token Service**: https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html
- **IAM Policy Reference**: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html
- **SAML Federation**: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_saml.html
- **AWS Organizations SCPs**: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html
- **IAM Roles Anywhere**: https://docs.aws.amazon.com/rolesanywhere/latest/userguide/introduction.html
- **AWS CloudTrail for IAM**: https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Security First**: Always apply least privilege principle when creating IAM resources
2. **Use Roles Over Users**: Prefer IAM roles with temporary credentials for all automation
3. **Encrypt Secrets**: Use PGP encryption for any sensitive outputs when IAM users are unavoidable
4. **Enable MFA**: Require MFA for privileged access through policy conditions
5. **Tag Consistently**: Implement comprehensive tagging with Environment, Application, Owner, ManagedBy tags
6. **Monitor Usage**: Enable CloudTrail and set up CloudWatch alarms for sensitive IAM actions
7. **Permissions Boundaries**: Use permissions boundaries when delegating IAM administration
8. **Session Duration**: Balance security and convenience - use shorter sessions for interactive, longer for automated
9. **Cross-Account Patterns**: Use roles with external IDs for secure cross-account access
10. **Modern Auth**: Leverage OIDC (GitHub, Bitbucket) and IRSA for CI/CD and Kubernetes workloads
11. **Policy Validation**: Use IAM Access Analyzer to validate policies before deployment
12. **Regular Audits**: Review and remove unused credentials, roles, and permissions quarterly
13. **OIDC Provider Limits**: Remember one OIDC provider per unique URL per account
14. **IRSA Best Practice**: Create separate roles per application/controller, not shared roles
15. **Namespace Isolation**: Always scope service account permissions to specific namespaces
16. **Version Pinning**: Pin module versions in production to prevent unexpected changes
17. **State Management**: Use remote state with encryption and versioning for IAM configurations
18. **Import Existing**: Check for and import existing IAM resources before creating new ones
