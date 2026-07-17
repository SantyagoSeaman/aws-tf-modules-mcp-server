# Terraform AWS SSO Module

## Module Information

- **Module Name**: `sso`
- **Module ID**: `cloudposse/sso/aws`
- **Source**: `cloudposse/sso/aws`
- **GitHub Repository**: https://github.com/cloudposse/terraform-aws-sso
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/sso/aws/latest
- **Latest Version**: 1.2.1
- **Purpose**: Terraform module that provisions AWS IAM Identity Center (AWS SSO) permission sets and assigns Identity Store users/groups to those permission sets in specific AWS accounts, for centralized multi-account single sign-on access
- **Service**: AWS IAM Identity Center (AWS Single Sign-On)
- **Category**: Security, Identity Management, Multi-Account Access
- **Keywords**: sso, aws-sso, iam-identity-center, identity-center, permission-sets, permission-set, account-assignments, account-assignment, single-sign-on, sso-groups, sso-users, ssoadmin, identitystore, aws-single-sign-on
- **Use For**: provisioning AWS SSO/IAM Identity Center permission sets, assigning IdP groups or users to AWS accounts via permission sets, centralized multi-account access management, mapping Administrators/Developers/ReadOnly groups to specific accounts, bootstrapping SSO across an AWS Organization landing zone, attaching AWS-managed/customer-managed/inline policies to a permission set, avoiding ResourceNotFoundException when assigning a Terraform-managed Identity Store group, single sign-on onboarding for a new AWS account

## Description

AWS IAM Identity Center (formerly "AWS Single Sign-On" / "AWS SSO") is AWS's centralized service for managing workforce access to multiple AWS accounts and business applications from one identity source. This Terraform module wires together the two building blocks that make up a working IAM Identity Center configuration: **permission sets** — the reusable, named bundles of IAM policy that define what a user can do once signed in to a given account — and **account assignments** — the bindings that grant a specific Identity Store user or group a specific permission set in a specific target AWS account. Critically, the **root module itself creates no resources and has no root-level input variables**; it exists purely as a namespace, and every real deployment calls one or both of its submodules directly via a `//modules/...` source suffix.

The `permission-sets` submodule creates one `aws_ssoadmin_permission_set` per entry in its `permission_sets` list, plus the associated `aws_ssoadmin_permission_set_inline_policy`, `aws_ssoadmin_managed_policy_attachment`, and `aws_ssoadmin_customer_managed_policy_attachment` resources for that entry's `inline_policy`, `policy_attachments` (AWS managed policy ARNs), and `customer_managed_policy_attachments` (customer-managed IAM policies by name/path). It resolves the target IAM Identity Center instance via the `aws_ssoadmin_instances` data source, so an instance must already exist in the account before `terraform apply`.

The `account-assignments` submodule creates one `aws_ssoadmin_account_assignment` per entry in its `account_assignments` list, binding a `GROUP` or `USER` principal (resolved by display name / username through `aws_identitystore_group` / `aws_identitystore_user` data sources) plus a `permission_set_arn` to a `target_id` (AWS account ID) with `target_type = "AWS_ACCOUNT"`. An optional `group_ids` map lets the caller pass already-known Identity Store group IDs directly — for groups the same Terraform run is creating — so the submodule skips the data-source lookup for those groups entirely, avoiding a `ResourceNotFoundException` when the group does not exist yet at plan time. An `identitystore_group_depends_on` input works around the fact that a module-level `depends_on` on this submodule would recreate all of its resources.

Like every Cloud Posse module, both submodules build resource names/tags through the shared `label`/`context` convention (`namespace`, `stage`, `name`, `tags`, `context`, `enabled`, etc.), even though — since the module creates IAM Identity Center resources, not conventionally-named/tagged infrastructure — the label output mainly threads through `tags`.

## Key Features

- **Two Independent Submodules**: `permission-sets` and `account-assignments`, callable separately or together — the root module has no resources of its own
- **Declarative Permission Sets**: Define any number of permission sets via a single `permission_sets` list, each with its own `name`, `description`, `relay_state`, `session_duration`, and `tags`
- **AWS Managed Policy Attachments**: Attach AWS managed IAM policies to a permission set via `policy_attachments` (a list of policy ARNs)
- **Customer Managed Policy Attachments**: Attach customer-managed IAM policies (by `name`/`path`) via `customer_managed_policy_attachments`
- **Inline Policy Support**: Attach a single inline IAM policy document per permission set via `inline_policy`
- **Declarative Account Assignments**: Bind principals to permission sets in target accounts via a single `account_assignments` list
- **GROUP or USER Principals**: `principal_type` selects whether a principal is resolved via `aws_identitystore_group` or `aws_identitystore_user`
- **`group_ids` Race-Condition Avoidance**: Pass known/Terraform-managed group display-name-to-ID mappings to skip the `aws_identitystore_group` data source lookup and avoid a plan-time `ResourceNotFoundException`
- **Depends-On Workaround**: `identitystore_group_depends_on` sequences the internal Identity Store data-source lookups without triggering resource recreation the way a module-level `depends_on` would
- **Auto-Discovered SSO Instance**: Both submodules resolve the IAM Identity Center instance ARN and Identity Store ID automatically via `aws_ssoadmin_instances` — no need to hardcode instance ARNs
- **Cloud Posse Label Convention**: Consistent tagging via `namespace`/`stage`/`name`/`context` inputs shared across every Cloud Posse module
- **Conditional Creation**: The `enabled` flag (part of the Cloud Posse `context`) toggles whether a submodule invocation creates any resources at all
- **Cross-Submodule Composition**: The `permission-sets` submodule's `permission_sets` output (containing each permission set's `arn`) feeds directly into the `account-assignments` submodule's `account_assignments` entries

## Main Use Cases

1. **Centralized Multi-Account Access**: Manage who can access which AWS account, and with what permissions, from one IAM Identity Center configuration
2. **Reusable Permission Sets**: Stand up job-function-based permission sets (AdministratorAccess, DeveloperAccess, ReadOnlyAccess) once and assign them to many accounts
3. **Group-Based Account Assignment**: Map an identity provider group (Administrators, Developers, Sandbox-Users) to a specific permission set in a specific account
4. **AWS Organizations Landing Zone Bootstrap**: Wire up baseline SSO access as part of new-account vending in an AWS Organization
5. **Mixed Policy Composition**: Combine AWS managed policies, customer-managed policies, and an inline policy on a single permission set
6. **Terraform-Managed Identity Store Groups**: Create an Identity Store group and immediately assign it to an account in the same apply, using `group_ids` to avoid a data-source race
7. **Migrating Off Per-Account IAM Users**: Replace long-lived IAM users/access keys in member accounts with centrally managed SSO access
8. **Attribute-/Role-Based Access Patterns**: Maintain distinct permission sets per job function and assign them narrowly per account, per least-privilege practice
9. **GitOps for IAM Identity Center**: Keep permission sets and account assignments in version control and code review instead of manual AWS SSO console changes
10. **Multi-Environment Reuse**: Apply the same permission set definitions across production, staging, and sandbox account groups with different `account_assignments` entries

## Usage Examples

### Example 1: Provision permission sets and assign them to accounts by group

```hcl
module "permission_sets" {
  source  = "cloudposse/sso/aws//modules/permission-sets"
  version = "1.2.1"

  permission_sets = [
    {
      name               = "AdministratorAccess"
      description        = "Allow full access to the account"
      relay_state        = ""
      session_duration   = ""
      tags               = {}
      inline_policy      = ""
      policy_attachments = ["arn:aws:iam::aws:policy/AdministratorAccess"]
      customer_managed_policy_attachments = []
    },
    {
      name               = "ReadOnlyAccess"
      description        = "Allow read-only access to the account"
      relay_state        = ""
      session_duration   = "PT4H"
      tags               = {}
      inline_policy      = ""
      policy_attachments = ["arn:aws:iam::aws:policy/ReadOnlyAccess"]
      customer_managed_policy_attachments = []
    }
  ]

  namespace = "acme"
  stage     = "sso"
  name      = "permission-sets"
}

module "sso_account_assignments" {
  source  = "cloudposse/sso/aws//modules/account-assignments"
  version = "1.2.1"

  account_assignments = [
    {
      account             = "111111111111" # "production" account
      permission_set_arn  = module.permission_sets.permission_sets["AdministratorAccess"].arn
      permission_set_name = "AdministratorAccess"
      principal_type      = "GROUP"
      principal_name      = "Administrators"
    },
    {
      account             = "222222222222" # "sandbox" account
      permission_set_arn  = module.permission_sets.permission_sets["ReadOnlyAccess"].arn
      permission_set_name = "ReadOnlyAccess"
      principal_type      = "GROUP"
      principal_name      = "Developers"
    },
  ]

  namespace = "acme"
  stage     = "sso"
  name      = "account-assignments"
}
```

### Example 2: Create an Identity Store group and assign it in the same apply (via `group_ids`)

```hcl
data "aws_ssoadmin_instances" "this" {}

resource "aws_identitystore_group" "platform_engineers" {
  identity_store_id = tolist(data.aws_ssoadmin_instances.this.identity_store_ids)[0]
  display_name      = "PlatformEngineers"
  description       = "Platform engineering team"
}

module "sso_account_assignments" {
  source  = "cloudposse/sso/aws//modules/account-assignments"
  version = "1.2.1"

  # Without group_ids, this would fail at plan time with a ResourceNotFoundException
  # because aws_identitystore_group.platform_engineers does not exist yet.
  group_ids = {
    (aws_identitystore_group.platform_engineers.display_name) = aws_identitystore_group.platform_engineers.group_id
  }

  account_assignments = [
    {
      account             = "333333333333"
      permission_set_arn  = module.permission_sets.permission_sets["AdministratorAccess"].arn
      permission_set_name = "AdministratorAccess"
      principal_type      = "GROUP"
      principal_name      = "PlatformEngineers"
    },
  ]

  namespace = "acme"
  stage     = "sso"
  name      = "account-assignments"
}
```

## Main Input Variables

The root module (`cloudposse/sso/aws`) has **no inputs of its own** — every input below belongs to one of the two submodules, called via a `//modules/permission-sets` or `//modules/account-assignments` source suffix.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `permission_sets` | `list(object)` | `[]` | (permission-sets submodule) List of permission sets to create — fields: `name`, `description`, `relay_state`, `session_duration`, `tags`, `inline_policy`, `policy_attachments` (list of AWS managed policy ARNs), `customer_managed_policy_attachments` (list of `{ name, path }`, `path` defaults to `/`) |
| `account_assignments` | `list(object)` | *(required)* | (account-assignments submodule) List of principal-to-permission-set-to-account bindings — fields: `account`, `permission_set_name`, `permission_set_arn`, `principal_name`, `principal_type` (`"GROUP"` or `"USER"`) |
| `group_ids` | `map(string)` | `{}` | (account-assignments submodule) Map of Identity Store group `DisplayName` to group ID; principals found here skip the `aws_identitystore_group` data-source lookup, avoiding a `ResourceNotFoundException` when the group is Terraform-managed and not yet created — see Notes for AI Agents |
| `identitystore_group_depends_on` | `list(string)` | `[]` | (account-assignments submodule) Values to trigger the submodule's internal `null_resource` dependency on — a workaround for sequencing the Identity Store data-source lookups without a module-level `depends_on` (which would recreate resources) |
| `namespace` | `string` | `null` | ID element — organization abbreviation, e.g. `eg` or `cp` (shared Cloud Posse context input, identical on both submodules) |
| `stage` | `string` | `null` | ID element — e.g. `prod`, `staging`, `sandbox` (shared context input) |
| `name` | `string` | `null` | ID element — the component or solution name (shared context input) |
| `tags` | `map(string)` | `{}` | Additional tags applied to resources created by whichever submodule is called (shared context input) |
| `context` | `any` | `{ "enabled": true, ... }` | Cloud Posse context object bundling namespace/stage/name/tags/etc. — identical shape accepted by both submodules; see Notes for AI Agents for the full field list |
| `enabled` | `bool` | `null` | Set to false to prevent a submodule invocation from creating any resources (shared context input) |

## Main Outputs

| Output | Description |
|--------|-------------|
| `permission_sets` | (permission-sets submodule) Map of permission-set name to its full `aws_ssoadmin_permission_set` resource attributes (`arn`, `id`, `name`, `description`, etc.) — feed `.arn` into `account_assignments` entries |
| `assignments` | (account-assignments submodule) Map of created `aws_ssoadmin_account_assignment` resources, keyed by `<account>-<G|U>-<principal_name>-<permission_set_name>` |

## Submodules

### 1. permission-sets

- **Purpose**: Creates `aws_ssoadmin_permission_set` resources (plus inline/managed/customer-managed policy attachments) — one permission set per entry in `permission_sets`
- **Source**: `cloudposse/sso/aws//modules/permission-sets`
- **Documentation Link**: https://registry.terraform.io/modules/cloudposse/sso/aws/latest/submodules/permission-sets
- **Key Features**: AWS managed policy attachments, customer-managed policy attachments, inline policy documents, per-set `relay_state`/`session_duration`
- **Use Cases**: standing up reusable AdministratorAccess/DeveloperAccess/ReadOnlyAccess permission sets before assigning them to accounts

### 2. account-assignments

- **Purpose**: Creates `aws_ssoadmin_account_assignment` resources binding a `GROUP` or `USER` principal and a permission set to a target AWS account
- **Source**: `cloudposse/sso/aws//modules/account-assignments`
- **Documentation Link**: https://registry.terraform.io/modules/cloudposse/sso/aws/latest/submodules/account-assignments
- **Key Features**: GROUP/USER principal resolution via Identity Store data sources, `group_ids` override to skip lookup for not-yet-created groups, `identitystore_group_depends_on` sequencing workaround
- **Use Cases**: mapping IdP groups (Administrators, Developers, ReadOnly) to specific permission sets in specific accounts across an AWS Organization

## Best Practices

### Permission Set Design

1. **Start with Job-Function Sets**: Define a small number of broad permission sets (Administrator, Developer, ReadOnly) before creating narrow, per-team sets.
2. **Prefer AWS Managed Policies First**: Use `policy_attachments` with AWS managed policy ARNs for common access patterns; reserve `inline_policy`/`customer_managed_policy_attachments` for gaps AWS managed policies do not cover.
3. **Populate Every Object Field**: `permission_sets` entries have no `optional()` fields — set unused string fields (`relay_state`, `session_duration`, `inline_policy`) to `""` rather than omitting them.
4. **Pin the Module Version**: Use an explicit `version = "1.2.1"` — Cloud Posse's own README usage snippets intentionally omit a version pin, which is not a pattern to copy into production code.

### Account Assignment Management

1. **Wire ARNs Across Submodules**: Pass `module.permission_sets.permission_sets["<name>"].arn` into each `account_assignments` entry's `permission_set_arn` rather than hardcoding a permission set ARN.
2. **Use `group_ids` for Terraform-Managed Groups**: When a group is created in the same run (e.g., via `aws_identitystore_group`), pass its display name/ID into `group_ids` to avoid a plan-time `ResourceNotFoundException` from the default data-source lookup.
3. **Set `principal_type` Explicitly and Correctly**: `"GROUP"` resolves through `aws_identitystore_group`; `"USER"` resolves through `aws_identitystore_user` — a mismatch fails to find the principal.
4. **Sequence With `identitystore_group_depends_on`, Not Module `depends_on`**: A module-level `depends_on` on this submodule recreates all of its resources; use `identitystore_group_depends_on` instead when ordering matters.

### Multi-Account Rollout

1. **Enable IAM Identity Center First**: This module cannot enable IAM Identity Center itself — it must already be active in the AWS Organizations management account or a registered delegated administrator account before `terraform apply`.
2. **Always Target a Submodule**: The root `cloudposse/sso/aws` source creates nothing — every real usage points at `//modules/permission-sets` and/or `//modules/account-assignments`.
3. **Reuse Permission Sets Across Accounts**: Define a permission set once and reference its `arn` from many `account_assignments` entries spanning different target accounts.

## Additional Resources

- **Module Repository**: https://github.com/cloudposse/terraform-aws-sso
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/sso/aws/latest
- **Module Examples**: https://github.com/cloudposse/terraform-aws-sso/tree/main/examples/complete
- **AWS IAM Identity Center User Guide**: https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html
- **Permission Sets Concept**: https://docs.aws.amazon.com/singlesignon/latest/userguide/permissionsetsconcept.html
- **Manage Your Identity Source**: https://docs.aws.amazon.com/singlesignon/latest/userguide/manage-your-identity-source.html
- **aws_ssoadmin_permission_set Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssoadmin_permission_set
- **aws_ssoadmin_account_assignment Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssoadmin_account_assignment
- **aws_identitystore_group Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/identitystore_group

## Notes for AI Agents

This module is published by Cloud Posse (namespace `cloudposse`), not the `terraform-aws-modules` org. It uses Cloud Posse's `context`/`label` convention — inputs like `namespace`, `stage`, `name`, `environment`, `tenant`, `attributes`, `tags` and a `context` object drive resource naming/tagging across every Cloud Posse module. Do NOT propagate this convention onto other (differently-styled) modules in the same project; set the label inputs this module needs and leave other vendors' modules alone.

When using this module in automated workflows:

1. **The Root Module Creates Nothing**: `cloudposse/sso/aws` has zero resources and zero inputs of its own — always target `//modules/permission-sets` and/or `//modules/account-assignments`; a bare `module "sso" { source = "cloudposse/sso/aws" }` block with no submodule suffix does nothing.
2. **IAM Identity Center Must Already Be Enabled**: Both submodules call `data "aws_ssoadmin_instances" "this" {}` and immediately do `tolist(data.aws_ssoadmin_instances.this.arns)[0]` — if IAM Identity Center is not enabled in the target account/organization, that list is empty and the `tolist(...)[0]` index fails at plan time. Enabling IAM Identity Center is a one-time, largely manual AWS Organizations action outside this module's scope.
3. **Run From the Management or Delegated Administrator Account**: The `aws_ssoadmin_*`/`aws_identitystore_*` data sources and resources this module uses only work with credentials for the IAM Identity Center management account or a registered delegated administrator account, regardless of which AWS account is the assignment's `target_id`.
4. **`GROUP` vs `USER` Principal Resolution**: `principal_type` in each `account_assignments` entry selects `aws_identitystore_group` or `aws_identitystore_user` for resolving `principal_name` — the display name/username must exist in the Identity Store (or, for groups, be supplied via `group_ids`).
5. **`group_ids` Avoids a Data-Source Race**: When an `account_assignments` entry references a group being created in the same Terraform run (e.g., via `aws_identitystore_group`), pass `{ <display_name> = <group_id> }` into `group_ids` so the submodule skips `aws_identitystore_group` for that principal instead of failing with `ResourceNotFoundException` on a group that does not exist at plan time.
6. **Cross-Submodule Wiring**: `account_assignments` entries need a `permission_set_arn` — this normally comes from `module.permission_sets.permission_sets["<name>"].arn`, the output of a separate `permission-sets` submodule call; provision permission sets before or alongside account assignments, not after.
7. **`permission_sets` Object Fields Are All Required**: The `permission_sets` variable's object type has no `optional()` fields — every entry must set `relay_state`, `session_duration`, `tags`, `inline_policy`, `policy_attachments`, and `customer_managed_policy_attachments` explicitly (use `""`/`{}`/`[]` for unused ones), or Terraform rejects the value.
8. **Pin the Module Version**: Use an explicit `version = "1.2.1"` constraint for reproducible deployments; Cloud Posse's own usage examples intentionally omit a version pin (and even use `?ref=master` in submodule READMEs), which is not a pattern to copy into real infrastructure.
9. **Naming: SSO vs IAM Identity Center**: AWS renamed "AWS Single Sign-On (AWS SSO)" to "AWS IAM Identity Center" in 2022; this module's name (`sso`) and its underlying Terraform resource types (`aws_ssoadmin_*`, `aws_identitystore_*`) still use the legacy SSO/SSO-admin naming — both names refer to the same current service.
10. **Not the `iam` Module**: This module does not create general-purpose IAM users/roles/policies — its `aws_ssoadmin_*` resources are scoped to IAM Identity Center permission sets and account assignments. For account-local IAM roles, trust policies, or OIDC/IRSA setup, use the existing `iam` module instead.
