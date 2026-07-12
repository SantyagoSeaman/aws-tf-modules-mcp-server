# Terraform AWS IAM Module

## Module Information

- **Module Name**: `iam`
- **Module ID**: `terraform-aws-modules/iam/aws`
- **Source**: `terraform-aws-modules/iam/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-iam
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest
- **Latest Version**: 6.6.1
- **Terraform Version**: >= 1.5.7
- **AWS Provider Version**: >= 6.28
- **Purpose**: Creates and manages AWS IAM resources — account settings, users, groups, roles with flexible trust policies, custom/read-only policies, OIDC providers, and EKS IRSA roles — through 8 focused, independently-usable submodules
- **Service**: AWS IAM (Identity and Access Management)
- **Category**: Security, Identity Management, Access Control
- **Keywords**: iam, identity, access-management, iam-role, iam-user, iam-group, iam-policy, trust-policy, oidc, saml, irsa, eks-service-accounts, github-actions-oidc, password-policy, permissions-boundary, cross-account-access, least-privilege
- **Use For**: federated/OIDC and SAML identity access, GitHub Actions and Bitbucket CI/CD keyless authentication, EKS workload identity (IRSA), cross-account role assumption, IAM user/group administration, account password policy enforcement, least-privilege custom policy creation, read-only audit roles, permissions-boundary-scoped delegated administration

## Description

This module is a collection of 8 independent, single-purpose Terraform submodules for managing AWS IAM resources — there is no root module to call directly; each resource type (account settings, users, groups, roles, policies, OIDC providers, IRSA roles) is provisioned via its own submodule path. This design lets consumers pull in only the pieces they need and compose them together (e.g. an OIDC provider plus multiple roles that trust it).

As of major version 6.0 (the current major line), the module consolidated several previously separate role submodules (`iam-assumable-role`, `iam-assumable-role-with-oidc`, `iam-assumable-role-with-saml`, `iam-github-oidc-role`, etc.) into a single, more flexible `iam-role` submodule. Trust policies are now expressed through a generic `trust_policy_permissions` map of IAM policy statements rather than dedicated variables like the old `trusted_role_arns`/`trusted_role_services`; convenience toggles (`enable_github_oidc`, `enable_bitbucket_oidc`, `enable_saml`, `enable_oidc`) remain for common federation patterns. Policy attachment across role/group/user submodules is unified under a single `policies` map of `{name = arn}` pairs, and most submodules now support inline policies via `create_inline_policy`/`inline_policy_permissions`.

The `iam-role-for-service-accounts` submodule (IRSA) ships pre-built, regularly-updated IAM policies for common EKS controllers and CSI drivers (Load Balancer Controller, EBS/EFS/FSx CSI, External DNS, Cert-Manager, External Secrets, VPC CNI, Cluster Autoscaler, Velero, and more), toggled with `attach_<service>_policy` booleans, avoiding hand-written least-privilege JSON for well-known add-ons. AWS now recommends EKS Pod Identity over IRSA for new workloads (a separate `terraform-aws-eks-pod-identity` module exists for that), and Karpenter's controller IAM role has moved to the `karpenter` submodule of `terraform-aws-eks`.

## Key Features

- **Eight Independent Submodules**: iam-account, iam-user, iam-group, iam-role, iam-policy, iam-read-only-policy, iam-oidc-provider, iam-role-for-service-accounts — no root module, use only what you need
- **Unified Trust Policy Engine**: `trust_policy_permissions` accepts arbitrary IAM policy statements (actions, principals, conditions) for any custom trust relationship, replacing older single-purpose variables
- **Built-in Federation Shortcuts**: One-flag trust policies for GitHub Actions OIDC, GitHub Enterprise Server, Bitbucket Pipelines OIDC, generic OIDC, and SAML 2.0
- **IRSA for EKS**: 17 pre-built, regularly-updated AWS service policies for common EKS controllers and CSI drivers via `attach_*_policy` flags
- **Unified Policy Attachment**: `policies` map (`{name = arn}`) for attaching managed or custom policies consistently across role/group/user submodules
- **Inline Policy Support**: `create_inline_policy` + `inline_policy_permissions` (or source/override policy documents) available on role, user, and IRSA submodules
- **Auto-Generated Read-Only Policies**: Service-specific read access addressing gaps and over-permissiveness in AWS managed read-only policies
- **Account-Level Security Baseline**: Password complexity, expiration, reuse prevention, and account alias configuration
- **Group-Based Access Control**: MFA enforcement and self-service credential management permissions at the group level
- **PGP-Encrypted Credentials**: IAM user login passwords and access keys can be PGP-encrypted before being written to state
- **Multi-Cluster IRSA**: A single IAM role assumable from multiple EKS clusters/namespaces via the `oidc_providers` map
- **Permissions Boundaries**: Supported on role, user, and IRSA submodules for delegated administration guardrails

## Main Use Cases

1. **Federated Identity Access**: Configure OIDC or SAML providers for enterprise SSO integration
2. **GitHub Actions / Bitbucket CI/CD Authentication**: Keyless, short-lived credential authentication for CI/CD pipelines
3. **EKS Workload Identity**: Implement IRSA (or migrate to EKS Pod Identity) for pods to access AWS services securely
4. **Cross-Account Role Management**: Create roles trusted by other AWS accounts, users, or services via custom trust statements
5. **User and Group Administration**: Organize IAM users into groups with MFA enforcement and scoped permissions
6. **Service Account Automation**: Configure IAM roles for AWS services, EC2 instance profiles, and applications
7. **Password Policy Enforcement**: Implement organization-wide password security standards
8. **Least-Privilege Policy Creation**: Generate and attach minimal, custom, or auto-generated read-only permission policies
9. **Temporary Credential Management**: Enable assume-role and federation patterns instead of long-lived access keys
10. **Security Audit and Compliance**: Track and version-control IAM resource configuration through infrastructure as code

## Submodules

### 1. iam-account
- **Purpose**: Configure account alias and password policy (instantiate once per AWS account)
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-account`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-account
- **Key Features**: Account alias, password complexity/length/expiration, reuse prevention, hard expiry option
- **Use Cases**: Organizational security baseline, password standards enforcement

### 2. iam-user
- **Purpose**: Create an IAM user with login profile, access key, SSH key, and inline/managed policies
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-user`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-user
- **Key Features**: PGP-encrypted credential outputs, SES SMTP password derivation, SSH key upload, inline policy support, permissions boundary
- **Use Cases**: Human user accounts, service API credentials, CodeCommit SSH access

### 3. iam-group
- **Purpose**: Create an IAM group with users and attached policies
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-group`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-group
- **Key Features**: User membership, managed/custom policy attachment, MFA enforcement, credential self-management permissions
- **Use Cases**: Role-based access control, team permissions, delegated credential management

### 4. iam-role
- **Purpose**: Create a single IAM role with a fully customizable trust policy and optional instance profile
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-role`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-role
- **Key Features**: Generic `trust_policy_permissions` statements, GitHub/Bitbucket/generic OIDC, SAML 2.0, inline policies, EC2 instance profiles
- **Use Cases**: GitHub Actions CI/CD, cross-account access, federated SSO, EC2 instance roles

### 5. iam-policy
- **Purpose**: Create a custom IAM policy from a JSON document
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-policy`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-policy
- **Key Features**: JSON policy definition, name or name_prefix, path configuration, tagging
- **Use Cases**: Custom permissions, least-privilege policies, reusable policy definitions

### 6. iam-read-only-policy
- **Purpose**: Auto-generate a read-only policy scoped to specified AWS services
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-read-only-policy`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-read-only-policy
- **Key Features**: Service-specific read access, CloudWatch Logs Insights querying, web console browsing support, predefined STS actions
- **Use Cases**: Audit roles, monitoring access, read-only developer access

### 7. iam-oidc-provider
- **Purpose**: Create an OIDC provider for external identity federation (one per URL per account)
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-oidc-provider`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-oidc-provider
- **Key Features**: GitHub Actions default URL, Bitbucket Pipelines, GitHub Enterprise Server, custom providers, automatic TLS thumbprint retrieval
- **Use Cases**: CI/CD authentication, external identity federation

### 8. iam-role-for-service-accounts (IRSA)
- **Purpose**: Create an IAM role for EKS service accounts with pre-built policies for common controllers/CSI drivers
- **Source**: `terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts`
- **Documentation**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-role-for-service-accounts
- **Key Features**: Multi-cluster/namespace `oidc_providers` map, 17 pre-built controller/CSI policies, custom policy and inline policy support
- **Supported Services**: Cert-Manager, Cluster Autoscaler, EBS/EFS/FSx Lustre/FSx OpenZFS/Mountpoint S3 CSI, External DNS, External Secrets, Load Balancer Controller (+ TargetGroupBinding-only variant), Node Termination Handler, VPC CNI, Velero, AWS Gateway API Controller, Amazon Managed Service for Prometheus, CloudWatch Observability
- **Note**: Karpenter's controller role now lives in the `karpenter` submodule of `terraform-aws-eks`, not here. AWS recommends EKS Pod Identity (`terraform-aws-eks-pod-identity`) over IRSA for new deployments
- **Use Cases**: Kubernetes pod AWS access, EKS controller authentication, multi-cluster service accounts

## Submodule 1: iam-account

### Description
Configures account-level IAM settings — the AWS account alias and password policy. Instantiate once per AWS account to establish baseline security standards for user authentication.

### Key Features
- Custom AWS account alias for account identification
- Password complexity rules (uppercase, lowercase, numbers, symbols)
- Password expiration with configurable maximum age
- Password reuse prevention with configurable history
- Hard expiry option (forces admin reset after expiration)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `account_alias` | `string` | n/a (required) | AWS IAM account alias for this account |
| `create_account_password_policy` | `bool` | `true` | Whether to create the password policy |
| `max_password_age` | `number` | `0` | Days until password expires (0 = never) |
| `minimum_password_length` | `number` | `8` | Minimum password length |
| `require_uppercase_characters` | `bool` | `true` | Require uppercase characters |
| `require_lowercase_characters` | `bool` | `true` | Require lowercase characters |
| `require_numbers` | `bool` | `true` | Require numbers |
| `require_symbols` | `bool` | `true` | Require symbols |
| `password_reuse_prevention` | `number` | `null` | Number of previous passwords to block |
| `hard_expiry` | `bool` | `false` | Force admin reset after expiration |
| `allow_users_to_change_password` | `bool` | `true` | Whether users can change their own password |

### Main Outputs

| Output | Description |
|--------|-------------|
| `iam_account_password_policy_expire_passwords` | Whether passwords expire (`true` if `max_password_age` > 0) |

### Usage Example

```hcl
module "iam_account" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-account"
  version = "~> 6.0"

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

**Note**: If an account alias already exists (from the Console or AWS Organizations), applying will fail with an "already exists" error. Import the resource first: `terraform import "module.iam_account.aws_iam_account_alias.this[0]" this`.

## Submodule 2: iam-user

### Description
Creates an individual IAM user with a login profile, access key, SSH public key (for CodeCommit), and inline/managed policies. Supports PGP encryption for secure credential distribution and can derive an SES SMTP password from the access key secret.

### Key Features
- Console login profiles with encrypted passwords
- Access keys for programmatic access (API/CLI)
- SES SMTP password derived from the access key (Sigv4 conversion)
- SSH public keys for CodeCommit
- PGP encryption for all credential outputs
- Inline and managed policy attachment
- Permissions boundary support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | IAM user name |
| `create_login_profile` | `bool` | `true` | Create console login profile |
| `create_access_key` | `bool` | `true` | Create access key |
| `create_ssh_key` | `bool` | `false` | Upload SSH public key |
| `create_inline_policy` | `bool` | `false` | Create inline policy |
| `inline_policy_permissions` | `map(object)` | `null` | Inline policy statements (actions, resources, effect, principals, conditions) |
| `pgp_key` | `string` | `null` | PGP key (`keybase:username` or base64-encoded) |
| `password_reset_required` | `bool` | `true` | Require password reset on first login |
| `force_destroy` | `bool` | `false` | Destroy even with non-Terraform-managed keys/profile |
| `permissions_boundary` | `string` | `null` | Permissions boundary policy ARN |
| `policies` | `map(string)` | `{}` | Policies to attach, `{name = arn}` |

### Main Outputs

| Output | Description |
|--------|-------------|
| `name` | IAM user name |
| `arn` | User ARN |
| `access_key_id` | Access key ID |
| `access_key_encrypted_secret` | PGP-encrypted access key secret (base64) |
| `access_key_encrypted_ses_smtp_password_v4` | PGP-encrypted SES SMTP password |
| `login_profile_encrypted_password` | PGP-encrypted console password (base64) |
| `ssh_key_public_key_id` | SSH public key ID |

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

  policies = {
    ReadOnly = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  }

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

**Security Note**: Always set `pgp_key` to prevent plaintext credentials from being written to Terraform state.

## Submodule 3: iam-group

### Description
Creates an IAM group for organizing users and managing permissions at scale. Supports managed policy attachment, custom inline-style permission statements, MFA enforcement, and self-management capabilities.

### Key Features
- User membership management (optionally across a different AWS account)
- AWS managed and custom policy attachment
- MFA enforcement at the group level
- Self-management permissions for credentials/MFA
- Custom permission statements merged into the group's generated policy

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Group name |
| `users` | `list(string)` | `[]` | IAM users to add to the group |
| `users_account_id` | `string` | `null` | Alternate AWS account ID where the users reside |
| `create_policy` | `bool` | `true` | Create an IAM policy for the group |
| `permissions` | `map(object)` | `null` | Custom policy statements (actions, resources, effect, principals, conditions) |
| `policies` | `map(string)` | `{}` | Managed/custom policy ARNs to attach, `{name = arn}` |
| `enable_self_management_permissions` | `bool` | `true` | Allow credential/MFA self-management |
| `enable_mfa_enforcement` | `bool` | `true` | Require MFA for actions |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Group ARN |
| `name` | Group name |
| `users` | List of users in the group |
| `policy_arn` | Attached (generated) policy ARN |

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

  # Custom permissions merged into the group policy
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
Creates a single IAM role with a fully customizable trust policy and an optional EC2 instance profile. Since v6.0, dedicated trust variables (`trusted_role_arns`, `trusted_role_services`, `custom_role_trust_policy`, etc.) have been replaced by a generic `trust_policy_permissions` map of IAM policy statements, alongside convenience toggles for common federation patterns (GitHub OIDC, Bitbucket OIDC, generic OIDC, SAML 2.0).

### Key Features
- `trust_policy_permissions`: arbitrary trust statements (principals, actions, conditions) for any custom trust relationship, including cross-account access
- GitHub Actions OIDC (`enable_github_oidc`) and GitHub Enterprise Server support
- Bitbucket Pipelines OIDC (`enable_bitbucket_oidc`)
- Generic OIDC trust (`enable_oidc` + `oidc_provider_urls`/`oidc_subjects`/`oidc_audiences`) for any provider
- SAML 2.0 federation (`enable_saml`, e.g. Okta, OneLogin)
- Inline policy support (`create_inline_policy` + `inline_policy_permissions`)
- EC2 instance profile creation
- Permissions boundary support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `null` | Role name |
| `use_name_prefix` | `bool` | `true` | Use `name` as a prefix (adds a random suffix) rather than an exact name |
| `trust_policy_permissions` | `map(object)` | `null` | Custom trust policy statements (actions, principals, conditions) |
| `trust_policy_conditions` | `list(object)` | `[]` | Additional conditions applied to all enabled trust statements |
| `enable_github_oidc` | `bool` | `false` | Enable GitHub Actions OIDC trust |
| `oidc_wildcard_subjects` | `list(string)` | `[]` | GitHub repo/branch subjects with wildcards (e.g. `"org/repo:*"`) |
| `enable_bitbucket_oidc` | `bool` | `false` | Enable Bitbucket Pipelines OIDC trust |
| `enable_oidc` | `bool` | `false` | Enable a generic OIDC provider trust |
| `enable_saml` | `bool` | `false` | Enable SAML provider trust |
| `saml_provider_ids` | `list(string)` | `[]` | SAML provider ARNs |
| `policies` | `map(string)` | `{}` | Policy ARNs to attach, `{name = arn}` |
| `create_instance_profile` | `bool` | `false` | Create an EC2 instance profile |
| `create_inline_policy` | `bool` | `false` | Create an inline policy |
| `permissions_boundary` | `string` | `null` | Permissions boundary ARN |
| `max_session_duration` | `number` | `null` | Session duration in seconds (1–12 hours; AWS default 3600 if unset) |

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

#### Cross-Account / User Assume Role (custom trust policy)

```hcl
module "cross_account_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role"
  version = "~> 6.0"

  name = "cross-account-auditor"

  trust_policy_permissions = {
    TrustRoleAndServiceToAssume = {
      actions = [
        "sts:AssumeRole",
        "sts:TagSession",
      ]
      principals = [
        {
          type = "AWS"
          identifiers = [
            "arn:aws:iam::111111111111:root",
            "arn:aws:iam::222222222222:role/auditor",
          ]
        }
      ]
      condition = [{
        test     = "StringEquals"
        variable = "sts:ExternalId"
        values   = ["some-secret-id"]
      }]
    }
  }

  policies = {
    ReadOnly = "arn:aws:iam::aws:policy/ReadOnlyAccess"
    Security = "arn:aws:iam::aws:policy/SecurityAudit"
  }
}
```

**Gotcha**: `use_name_prefix` defaults to `true`, so `name = "cross-account-auditor"` produces a role named `cross-account-auditor-<random-suffix>`. Set `use_name_prefix = false` for an exact name.

## Submodule 5: iam-policy

### Description
Creates a custom IAM policy from a JSON document. Essential for implementing least-privilege access patterns and reusable permission sets shared across roles, users, and groups.

### Key Features
- JSON policy document support
- `name` or `name_prefix` (mutually exclusive)
- Configurable policy path
- Resource tagging

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the policy |
| `name` | `string` | `null` | Policy name (conflicts with `name_prefix`) |
| `name_prefix` | `string` | `null` | Name prefix for an auto-generated name |
| `description` | `string` | `null` | Policy description |
| `path` | `string` | `null` | IAM hierarchy path |
| `policy` | `string` | `""` | JSON policy document (required in practice) |
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
module "app_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role"
  version = "~> 6.0"

  name = "app-role"

  policies = {
    S3ReadOnly = module.s3_readonly_policy.arn
  }
}
```

## Submodule 6: iam-read-only-policy

### Description
Auto-generates a read-only IAM policy scoped to a specified list of AWS services. Addresses gaps and over-permissiveness in AWS managed read-only policies (`ReadOnlyAccess`, `ViewOnlyAccess`) by enabling granular, service-specific `Get`/`List`/`Describe`/`View` permissions.

### Key Features
- Service-specific read-only access (specify IAM service prefixes)
- CloudWatch Logs Insights query support
- Web console browsing support (resource-groups, tag, health, ce)
- Predefined STS actions (caller identity, session token)
- Can generate the policy JSON without creating the policy resource (`create_policy = false`)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `null` | Policy name |
| `allowed_services` | `list(string)` | `[]` | AWS service IAM prefixes to grant read access for (required in practice) |
| `allow_cloudwatch_logs_query` | `bool` | `true` | Enable CloudWatch Logs querying |
| `allow_predefined_sts_actions` | `bool` | `true` | Allow caller identity/session token actions |
| `allow_web_console_services` | `bool` | `true` | Enable console browsing services |
| `create_policy` | `bool` | `true` | Whether to create the policy resource (vs. JSON only) |
| `use_name_prefix` | `bool` | `true` | Use `name` as a prefix |
| `path` | `string` | `null` | IAM hierarchy path |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Policy ARN |
| `name` | Policy name |
| `policy` | Policy document |
| `policy_json` | Policy document as JSON |

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

  trust_policy_permissions = {
    TrustAccountRoot = {
      actions    = ["sts:AssumeRole"]
      principals = [{ type = "AWS", identifiers = ["arn:aws:iam::123456789012:root"] }]
    }
  }

  policies = {
    ReadOnly = module.audit_readonly_policy.arn
  }
}
```

## Submodule 7: iam-oidc-provider

### Description
Creates an OpenID Connect (OIDC) provider for external identity federation, enabling keyless authentication for CI/CD pipelines. **AWS limits one OIDC provider per unique URL per account** — provision once per account/URL and trust it from multiple roles.

### Key Features
- Pre-configured default for GitHub Actions
- Bitbucket Pipelines support
- GitHub Enterprise Server / custom OIDC provider URLs
- Automatic TLS certificate thumbprint retrieval

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the provider |
| `url` | `string` | `"https://token.actions.githubusercontent.com"` | OIDC provider URL |
| `client_id_list` | `list(string)` | `[]` | Audience identifiers (defaults to STS service if empty) |
| `tags` | `map(string)` | `{}` | Resource tags |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Provider ARN |
| `url` | Identity provider URL (matches the `iss` claim) |

### Usage Examples

#### GitHub Actions (Default)

```hcl
module "github_oidc_provider" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-oidc-provider"
  version = "~> 6.0"

  # Defaults to GitHub Actions URL
  tags = { Purpose = "GitHub Actions" }
}

# Create a role that trusts this provider
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

  tags = { Purpose = "Bitbucket Pipelines" }
}
```

## Submodule 8: iam-role-for-service-accounts (IRSA)

### Description
Creates an IAM role for Amazon EKS service accounts (the IRSA pattern) with pre-built policies for common EKS controllers and CSI drivers. Enables Kubernetes pods to access AWS services using temporary, automatically-rotated credentials without embedded access keys.

**AWS now recommends EKS Pod Identity over IRSA for new deployments** (see `terraform-aws-eks-pod-identity`). Karpenter's controller IAM role now lives in the `karpenter` submodule of `terraform-aws-eks`, not in this submodule.

### Key Features
- Multi-cluster/multi-namespace OIDC trust via the `oidc_providers` map
- 17 pre-built controller/CSI driver policies, each toggled with an `attach_*_policy` flag
- Custom policy and inline policy attachment for application-specific permissions
- Service-specific ARN scoping (hosted zones, buckets, KMS keys, etc.) for least privilege

### Supported AWS Services (Pre-Built Policies)

| Category | Services |
|----------|----------|
| **Autoscaling** | Cluster Autoscaler, Node Termination Handler |
| **Storage** | EBS CSI, EFS CSI, FSx Lustre CSI, FSx OpenZFS CSI, Mountpoint S3 CSI |
| **Networking** | External DNS, VPC CNI, Load Balancer Controller (+ TargetGroupBinding-only), AWS Gateway API Controller |
| **Secrets** | External Secrets (Secrets Manager, SSM Parameter Store) |
| **Certificates** | Cert-Manager |
| **Monitoring** | CloudWatch Observability, Amazon Managed Service for Prometheus |
| **Backup** | Velero |

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | IAM role name |
| `use_name_prefix` | `bool` | `true` | Use `name`/`policy_name` as a prefix |
| `oidc_providers` | `map(object)` | `{}` | Map with `provider_arn` and `namespace_service_accounts` per entry |
| `attach_<service>_policy` | `bool` | `false` | Enable a pre-built policy for a given service (e.g. `attach_load_balancer_controller_policy`) |
| `cert_manager_hosted_zone_arns` | `list(string)` | `[]` | Route53 zones for cert management |
| `ebs_csi_kms_cmk_arns` | `list(string)` | `[]` | KMS keys for encrypted EBS volumes |
| `external_dns_hosted_zone_arns` | `list(string)` | `[]` | Route53 zones for External DNS |
| `external_secrets_secrets_manager_arns` | `list(string)` | `[]` | Secrets Manager ARNs for External Secrets |
| `mountpoint_s3_csi_bucket_arns` | `list(string)` | `[]` | S3 bucket ARNs (required if `attach_mountpoint_s3_csi_policy = true`) |
| `velero_s3_bucket_arns` | `list(string)` | `[]` | S3 buckets for Velero backup |
| `cluster_autoscaler_cluster_names` | `list(string)` | `[]` | EKS cluster names to scope autoscaler permissions to |
| `policies` | `map(string)` | `{}` | Custom policy ARNs to attach, `{name = arn}` |
| `create_inline_policy` | `bool` | `false` | Create an inline policy for application-specific permissions |
| `permissions_boundary` | `string` | `null` | Permissions boundary ARN |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | IAM role ARN |
| `name` | IAM role name |
| `iam_policy_arn` | ARN of the generated policy attached to the role |

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

#### VPC CNI (IPv4)

```hcl
module "vpc_cni_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts"
  version = "~> 6.0"

  name = "vpc-cni"

  attach_vpc_cni_policy = true
  vpc_cni_enable_ipv4   = true

  oidc_providers = {
    this = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-node"]
    }
  }

  tags = { Application = "VPC CNI" }
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

1. **Use Temporary Credentials**: Prefer OIDC, SAML, or assume-role patterns over long-lived IAM user access keys
2. **PGP-Encrypt User Credentials**: Always set `pgp_key` when creating IAM users to prevent plaintext secrets in state
3. **Enable MFA Enforcement**: Use `enable_mfa_enforcement` on groups for privileged access
4. **Implement Strong Password Policies**: Minimum 14+ characters, full complexity, 90-day expiration, block reuse of the last 5 passwords
5. **Use IRSA or Pod Identity for EKS**: Never embed AWS credentials in pods
6. **Use OIDC for CI/CD**: GitHub Actions, Bitbucket — eliminates long-lived secrets in pipelines

### Permission Management

1. **Apply Least Privilege**: Start minimal, add incrementally; validate with IAM Access Analyzer
2. **Use Permissions Boundaries**: Cap the maximum permissions grantable via delegated IAM administration
3. **Scope OIDC Trust Narrowly**: Use specific repo/branch subjects (e.g. `org/repo:ref:refs/heads/main`), not broad wildcards
4. **Namespace-Scope IRSA**: Always specify the namespace in `namespace_service_accounts` (`namespace:sa-name`)
5. **Use Pre-Built Controller Policies**: Prefer `attach_*_policy` flags over hand-written JSON for standard EKS add-ons
6. **One IRSA/Pod Identity Role per Application**: Don't share roles across unrelated workloads

### Configuration

1. **Pin Module Versions**: Use `version = "~> 6.0"` in production
2. **Understand `use_name_prefix`**: Defaults to `true` on `iam-role`, `iam-read-only-policy`, and `iam-role-for-service-accounts` — the created resource name gets a random suffix unless set to `false`
3. **Set the Account Alias**: Configure via `iam-account` for easier account identification
4. **Import Pre-Existing Resources**: Check for existing account alias/IAM resources before creating new ones
5. **One OIDC Provider per URL**: AWS limits one per unique URL per account; reuse the same provider across multiple roles
6. **Tag Consistently**: Include `Environment`, `Application`, `Team` tags on all resources

### Operational

1. **Review `terraform plan` Carefully**: IAM changes can break production access
2. **Enable CloudTrail**: Log all IAM actions for auditing
3. **Test Trust Policy Changes in Non-Prod First**: Especially for OIDC/SAML trust conditions
4. **Regular Permission Audits**: Use IAM Access Analyzer to identify unused permissions

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-iam
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-iam/tree/master/examples
- **v5.x → v6.x Upgrade Guide**: https://github.com/terraform-aws-modules/terraform-aws-iam/blob/master/docs/UPGRADE-6.0.md
- **AWS IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **IAM Access Analyzer**: https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html
- **IRSA Documentation**: https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
- **EKS Pod Identity (IRSA alternative)**: https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html
- **GitHub Actions OIDC**: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services

## Notes for AI Agents

When generating Terraform code with this module:

1. **Always pin version**: Use `version = "~> 6.0"` in module blocks (current line is 6.x; v5.x and earlier used entirely different submodule names/variables — do not mix the two)
2. **`iam-role` has no `trusted_role_arns`**: Cross-account/user trust is expressed via `trust_policy_permissions` statements with `principals`, not a flat ARN list (this changed in v6.0)
3. **Prefer roles over users**: Use OIDC/SAML/IRSA instead of creating IAM users with long-lived access keys
4. **PGP for user credentials**: If creating users, always set `pgp_key` to prevent plaintext secrets in state
5. **Scope OIDC trust narrowly**: Use specific repo/branch patterns like `org/repo:ref:refs/heads/main`
6. **One OIDC provider per URL**: Reuse existing providers; don't create duplicates for the same URL
7. **Namespace-scope IRSA**: Always include the namespace in `namespace_service_accounts`, format `namespace:sa-name`
8. **Use pre-built controller policies**: Prefer `attach_load_balancer_controller_policy = true` etc. over custom-written policy JSON for standard EKS add-ons
9. **Watch `use_name_prefix`**: Defaults to `true` on `iam-role`, `iam-read-only-policy`, and `iam-role-for-service-accounts` — set it to `false` if the exact resource name matters (e.g. it's referenced elsewhere by literal name)
10. **Tag all resources**: Include at minimum `tags = { ManagedBy = "terraform" }`
11. **Import before create**: Check if IAM resources (especially the account alias) already exist before creating new ones
12. **Karpenter and EKS Pod Identity**: Do not use this module's `iam-role-for-service-accounts` for Karpenter (use the `karpenter` submodule of `terraform-aws-eks`); for new EKS workloads generally, prefer EKS Pod Identity (`terraform-aws-eks-pod-identity`) over IRSA
