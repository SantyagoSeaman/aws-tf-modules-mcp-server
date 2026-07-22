# Terraform AWS Backup Module

## Module Information

- **Module Name**: `backup`
- **Module ID**: `cloudposse/backup/aws`
- **Source**: `cloudposse/backup/aws`
- **GitHub Repository**: https://github.com/cloudposse/terraform-aws-backup
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/backup/aws/latest
- **Latest Version**: 1.1.1
- **Purpose**: Terraform module that provisions AWS Backup — a backup vault, a backup plan built from cron-scheduled rules, a tag/ARN-based backup selection, and the IAM role AWS Backup needs — to centralize and automate backup of EBS volumes, EC2 instances, RDS databases, DynamoDB tables, EFS file systems, and Storage Gateway volumes
- **Service**: AWS Backup
- **Category**: Disaster Recovery, Data Protection, Compliance
- **Keywords**: aws-backup, backup-plan, backup-vault, backup-selection, disaster-recovery, retention-policy, cross-region-backup, point-in-time-recovery, backup-vault-lock, continuous-backup, lifecycle-policy, cold-storage, ebs-backup, rds-backup, dynamodb-backup, efs-backup, compliance-mode, governance-mode
- **Use For**: centralizing backup schedules for EBS/EC2/RDS/DynamoDB/EFS/Storage Gateway resources, tag-based or ARN-based resource selection for a backup plan, disaster-recovery runbooks via cross-region/cross-account copy actions, compliance-driven immutable retention via Backup Vault Lock, continuous backup (point-in-time recovery) for supported resources like RDS/Aurora, cold-storage tiering to reduce long-term retention cost, scheduled daily/weekly/monthly backup rules with cron expressions, org-wide backup governance baselines, automated IAM role provisioning for the AWS Backup service, multi-environment vault/plan naming via the Cloud Posse context convention

## Description

AWS Backup is a fully managed service that centralizes and automates data protection across AWS services. This Terraform module wires together a complete, working deployment: a Backup Vault (`aws_backup_vault`) that stores recovery points, a Backup Plan (`aws_backup_plan`) built from one or more schedule `rule` blocks, a Backup Selection (`aws_backup_selection`) that assigns resources to the plan by explicit ARN/pattern, tag, or condition, and an IAM Role with the two AWS-managed policies (`AWSBackupServiceRolePolicyForBackup`, `AWSBackupServiceRolePolicyForS3Backup`) AWS Backup needs to read and back up resources on your behalf. Every resource is optional and independently toggleable (`vault_enabled`, `plan_enabled`, `iam_role_enabled`), so the module can create everything from scratch or attach a plan/selection to an already-existing vault or IAM role looked up by name.

The `rules` variable is the heart of the module: a list of objects, each describing one schedule in the plan — a `name`, a `schedule` cron expression, `start_window`/`completion_window` timing in minutes, an optional `enable_continuous_backup` flag (turns on point-in-time-recovery-style continuous backup for resource types that support it, currently RDS/Aurora), a `lifecycle` block (`cold_storage_after`/`delete_after` retention transitions, plus `opt_in_to_archive_for_supported_resources`), and an optional `copy_action` block that replicates each recovery point to a `destination_vault_arn` — the mechanism this module uses for cross-region and cross-account disaster recovery, since the destination vault itself is not created by this module and must already exist (in the target region/account) with a resource policy that authorizes the copy. Resource selection is equally flexible: `backup_resources`/`not_resources` take explicit ARNs or match patterns, `selection_tags` filters by tag equality, and `selection_conditions` (`string_equals`/`string_like`/`string_not_equals`/`string_not_like`) layers additional `aws:ResourceTag/*` conditions on top.

For compliance and governance workloads, `backup_vault_lock_configuration` enables AWS Backup Vault Lock: an immutable retention floor that even account root users cannot delete backups within. Omitting `changeable_for_days` creates a `governance`-mode lock (revocable by IAM users with the `backup:BypassGovernanceRetention` permission); setting `min_retention_days`/`max_retention_days` without `changeable_for_days` creates an irrevocable `compliance`-mode lock. Like every Cloud Posse module, resource naming and tagging are driven by the shared `namespace`/`stage`/`name`/`tags`/`context` label convention (via an internal `cloudposse/label/null` dependency) rather than a project-level submodule — this module ships no submodules of its own.

## Key Features

- **Backup Vault**: Creates an `aws_backup_vault` to store recovery points, optionally encrypted with a customer-managed KMS key via `kms_key_arn`
- **Backup Plan with Multiple Rules**: `rules` builds one `aws_backup_plan` with a `dynamic "rule"` block per schedule entry — cron `schedule`, `start_window`, `completion_window`
- **Continuous Backup (Point-in-Time Recovery)**: `enable_continuous_backup` per rule turns on point-in-time recovery for resource types that support it (RDS/Aurora)
- **Lifecycle Transitions**: Per-rule `lifecycle.cold_storage_after`/`delete_after` move recovery points to cold storage and expire them on a retention schedule
- **Cross-Region / Cross-Account Copy**: Per-rule `copy_action.destination_vault_arn` (+ its own nested `lifecycle`) replicates recovery points to another vault — the module's disaster-recovery mechanism
- **Backup Selection by ARN, Tag, or Condition**: `backup_resources`/`not_resources` (explicit ARNs or match patterns), `selection_tags` (tag equality), and `selection_conditions` (`string_equals`/`string_like`/`string_not_equals`/`string_not_like`) combine to define what gets backed up
- **Backup Vault Lock**: `backup_vault_lock_configuration` enables immutable retention — governance mode (omit `changeable_for_days`) or compliance mode (`min_retention_days`/`max_retention_days`)
- **Advanced Backup Setting**: `advanced_backup_setting` passes resource-type-specific options (e.g. Windows VSS for EC2) straight to the backup plan
- **Managed IAM Role**: `iam_role_enabled` provisions an IAM role trusted by `backup.amazonaws.com` with `AWSBackupServiceRolePolicyForBackup` and `AWSBackupServiceRolePolicyForS3Backup` attached
- **Bring-Your-Own Vault or Role**: Set `vault_enabled`/`iam_role_enabled` to `false` and supply `vault_name`/`iam_role_name` to look up and reuse existing resources instead of creating new ones
- **Permissions Boundary Support**: `permissions_boundary` applies an IAM permissions boundary to the created backup role
- **Cloud Posse Label Convention**: Consistent resource naming/tagging via `namespace`/`stage`/`name`/`context` inputs shared across every Cloud Posse module
- **Conditional Creation**: The `enabled` flag (part of the Cloud Posse `context`) toggles whether the module creates any resources at all

## Main Use Cases

1. **Centralized Backup Automation**: Schedule and retain backups for EBS, EC2, RDS, DynamoDB, EFS, and Storage Gateway resources from one Terraform-managed plan
2. **Disaster Recovery**: Replicate recovery points to a vault in another region or account via `copy_action.destination_vault_arn`
3. **Point-in-Time Recovery**: Enable `enable_continuous_backup` on RDS/Aurora rules for restore-to-any-second recovery within the retention window
4. **Compliance-Grade Immutable Retention**: Lock a vault in `compliance` mode so backups cannot be deleted before their retention period expires, even by the account root
5. **Governance Baselines**: Apply `governance`-mode vault lock as a revocable-with-permission safety net against accidental or malicious deletion
6. **Tag-Driven Backup Assignment**: Assign resources to a backup plan automatically as they are tagged, instead of maintaining an ARN allow-list by hand
7. **Cost-Optimized Long-Term Retention**: Transition older recovery points to cold storage via `lifecycle.cold_storage_after` before final expiration
8. **Multi-Rule Backup Plans**: Combine a daily short-retention rule with a weekly/monthly long-retention rule in a single plan
9. **Bring-Your-Own Vault/Role Adoption**: Attach a new backup plan/selection to a vault or IAM role that already exists (shared across teams or created outside Terraform)
10. **Audit Evidence Retention**: Retain durable, tamper-evident recovery points for SOC2/PCI/HIPAA backup-evidence requirements

## Usage Examples

### Example 1: Single-region backup plan for EFS with daily/weekly rules and tag-based selection

```hcl
module "backup" {
  source  = "cloudposse/backup/aws"
  version = "1.1.1"

  namespace = "acme"
  stage     = "prod"
  name      = "backup"

  vault_enabled    = true
  plan_enabled     = true
  iam_role_enabled = true

  kms_key_arn = module.backup_kms_key.key_arn

  # Assign resources both by explicit ARN and by tag
  backup_resources = [module.efs.arn]
  selection_tags = [
    {
      type  = "STRINGEQUALS"
      key   = "backup"
      value = "true"
    }
  ]

  rules = [
    {
      name               = "daily"
      schedule           = "cron(0 5 ? * * *)"
      start_window       = 320   # 60 * 8   minutes
      completion_window  = 10080 # 60 * 24 * 7 minutes
      lifecycle = {
        cold_storage_after = 30
        delete_after       = 35
      }
    },
    {
      name               = "weekly"
      schedule           = "cron(0 5 ? * SAT *)"
      start_window       = 320
      completion_window  = 10080
      lifecycle = {
        delete_after = 90
      }
    }
  ]

  tags = {
    Environment = "prod"
  }
}
```

### Example 2: Cross-region disaster recovery with continuous backup and a compliance-mode vault lock

```hcl
# Destination vault must already exist in the DR region/account and grant
# this account permission to copy recovery points into it (this module does
# not create the destination vault).
data "aws_backup_vault" "dr" {
  provider = aws.dr_region
  name     = "acme-dr-security-backup"
}

module "backup" {
  source  = "cloudposse/backup/aws"
  version = "1.1.1"

  namespace = "acme"
  stage     = "prod"
  name      = "rds-backup"

  backup_resources = [aws_db_instance.primary.arn]

  rules = [
    {
      name                     = "continuous-and-cross-region"
      schedule                 = "cron(0 */4 * * ? *)"
      enable_continuous_backup = true # point-in-time recovery for RDS/Aurora
      start_window             = 60
      completion_window        = 480
      lifecycle = {
        delete_after = 35
      }
      copy_action = {
        destination_vault_arn = data.aws_backup_vault.dr.arn
        lifecycle = {
          delete_after = 365
        }
      }
    }
  ]

  # Irrevocable compliance-mode lock: min/max retention set, changeable_for_days omitted
  backup_vault_lock_configuration = {
    min_retention_days = 35
    max_retention_days = 365
  }

  tags = {
    Environment = "prod"
    Compliance  = "hipaa"
  }
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `kms_key_arn` | `string` | `null` | The server-side encryption key (KMS key ARN) that protects the backup vault's recovery points |
| `rules` | `list(object)` | `[]` | Backup plan schedule rules — fields: `name`, `schedule`, `enable_continuous_backup`, `start_window`, `completion_window`, `lifecycle` (nested: `cold_storage_after`, `delete_after`, `opt_in_to_archive_for_supported_resources`), `copy_action` (nested: `destination_vault_arn`, `lifecycle`) — see Notes for AI Agents for the full shape |
| `advanced_backup_setting` | `object` | `null` | Resource-type-specific backup options (e.g. Windows VSS) — fields: `backup_options` (`map(string)`), `resource_type` |
| `backup_resources` | `list(string)` | `[]` | ARNs or match patterns of resources to include in the backup selection |
| `not_resources` | `list(string)` | `[]` | ARNs or match patterns of resources to exclude from the backup selection |
| `selection_tags` | `list(object)` | `[]` | Tag-based selection conditions — fields: `type` (e.g. `STRINGEQUALS`), `key`, `value` |
| `selection_conditions` | `object` | `{}` | Additional `aws:ResourceTag/*` conditions ANDed with `selection_tags` — fields: `string_equals`, `string_like`, `string_not_equals`, `string_not_like` (each a list of `key`/`value` objects) |
| `plan_name_suffix` | `string` | `null` | String appended to the computed backup plan name |
| `vault_name` | `string` | `null` | Override the target vault name; REQUIRED (used for an existing-vault data-source lookup) when `vault_enabled = false` |
| `vault_enabled` | `bool` | `true` | Create a new Backup Vault; set `false` to reference an existing vault via `vault_name` |
| `plan_enabled` | `bool` | `true` | Create a new Backup Plan and Backup Selection |
| `iam_role_enabled` | `bool` | `true` | Create a new IAM Role and attach the AWS Backup service policies |
| `iam_role_name` | `string` | `null` | Override the target IAM Role name; REQUIRED (used for an existing-role data-source lookup) when `iam_role_enabled = false` |
| `permissions_boundary` | `string` | `null` | IAM permissions boundary ARN applied to the created backup IAM role |
| `backup_vault_lock_configuration` | `object` | `null` | Enables AWS Backup Vault Lock — fields: `changeable_for_days` (governance mode when set, omit for compliance mode), `max_retention_days`, `min_retention_days` |
| `enabled` | `bool` | `null` | Set to `false` to prevent the module from creating any resources |
| `namespace` | `string` | `null` | ID element — organization abbreviation, e.g. `eg` or `cp` |
| `stage` | `string` | `null` | ID element — e.g. `prod`, `staging`, `dev` |
| `name` | `string` | `null` | ID element — the component or solution name |
| `tags` | `map(string)` | `{}` | Additional tags applied to all resources |
| `context` | `any` | `{ "enabled": true, ... }` | Cloud Posse context object bundling namespace/stage/name/tags/etc. — see Notes for AI Agents for the full field list |

## Main Outputs

| Output | Description |
|--------|-------------|
| `backup_vault_id` | Backup Vault ID |
| `backup_vault_arn` | Backup Vault ARN |
| `backup_plan_arn` | Backup Plan ARN |
| `backup_plan_version` | Unique, randomly generated, Unicode UTF-8 string that serves as the version ID of the backup plan |
| `backup_selection_id` | Backup Selection ID |
| `role_name` | The name of the IAM role created |
| `role_arn` | The ARN of the IAM role created |

## Best Practices

### Schedule and Retention Design

1. **Layer Short and Long Retention Rules**: Combine a daily rule with a short `delete_after` and a weekly/monthly rule with a longer one in the same `rules` list, rather than one rule trying to serve both purposes.
2. **Size Windows Generously**: `start_window`/`completion_window` are in minutes — undersizing them on large volumes (EFS, big RDS instances) causes missed or incomplete backup jobs; the module's own examples use 320/10080 (~5h20m start, 7-day completion) as a safe baseline.
3. **Use Cold Storage for Long Retention**: Set `lifecycle.cold_storage_after` on rules with a `delete_after` well beyond 90 days to cut storage cost instead of leaving everything in warm storage.

### Disaster Recovery and Continuous Backup

1. **Pre-Provision the Destination Vault**: `copy_action.destination_vault_arn` must reference a vault that already exists in the target region/account with a resource policy authorizing the copy — this module does not create it.
2. **Enable Continuous Backup Only Where Supported**: `enable_continuous_backup` (point-in-time recovery) currently only takes effect for RDS/Aurora; setting it on unsupported resource types is silently ignored by AWS Backup, not rejected by this module.
3. **Give Cross-Region Copies Their Own Lifecycle**: The nested `copy_action.lifecycle` is independent of the rule's own `lifecycle` — set both explicitly rather than assuming the copy inherits the source retention.

### Compliance and Vault Lock

1. **Choose Governance vs. Compliance Deliberately**: Omit `changeable_for_days` for a compliance-mode lock (irrevocable, even by the root account) instead of accidentally leaving a governance-mode escape hatch on a regulated workload.
2. **One Lock Per Vault**: A vault can have only one `backup_vault_lock_configuration` — plan the final retention bounds before applying, since compliance mode cannot be loosened afterward.
3. **Pin the Module Version**: Use an explicit `version = "1.1.1"` — the backup schedule syntax changed in `0.14.0` and deprecated variables were removed entirely in `1.x`, so pre-1.x examples found online will not apply cleanly.

### IAM and Bring-Your-Own Resources

1. **Both Backup Policies Are Always Attached**: `iam_role_enabled = true` attaches `AWSBackupServiceRolePolicyForBackup` AND `AWSBackupServiceRolePolicyForS3Backup` unconditionally, regardless of whether S3 is actually in `backup_resources` — bring your own role via `iam_role_name`/`iam_role_enabled = false` if a narrower policy set is required.
2. **Name, Not ARN, for Existing Resources**: `vault_name`/`iam_role_name` are used for existing-resource data-source lookups by name when `vault_enabled`/`iam_role_enabled` are `false` — an ARN or a non-existent name fails the lookup, not just the reference.

## Additional Resources

- **Module Repository**: https://github.com/cloudposse/terraform-aws-backup
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/backup/aws/latest
- **Module Example**: https://github.com/cloudposse/terraform-aws-backup/tree/main/examples/complete
- **0.13.x to 0.14.x+ Migration Guide**: https://github.com/cloudposse/terraform-aws-backup/blob/main/docs/migration-0.13.x-0.14.x+.md
- **AWS Backup Developer Guide**: https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html
- **AWS Backup Vault Lock**: https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html
- **AWS Backup Continuous Backup (Point-in-Time Recovery)**: https://docs.aws.amazon.com/aws-backup/latest/devguide/point-in-time-recovery.html
- **aws_backup_plan Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/backup_plan
- **aws_backup_selection Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/backup_selection

## Notes for AI Agents

This module is published by Cloud Posse (namespace `cloudposse`), not the `terraform-aws-modules` org. It uses Cloud Posse's `context`/`label` convention — inputs like `namespace`, `stage`, `name`, `environment`, `tenant`, `attributes`, `tags` and a `context` object drive resource naming/tagging across every Cloud Posse module. Do NOT propagate this convention onto other (differently-styled) modules in the same project; set the label inputs this module needs and leave other vendors' modules alone.

When using this module in automated workflows:

1. **`rules[].name` Is Required, Despite `main.tf`'s Fallback**: The `rules` variable's type constrains `name` as a required (non-optional) string even though the root module's `dynamic "rule"` block reads it via `lookup(rule.value, "name", "${module.this.id}-${rule.key}")` — omitting `name` from a rule object is a type error at plan time, not a silently-applied default.
2. **Vault + Plan + Selection Are Three Separate Toggles**: `vault_enabled`, `plan_enabled`, and `iam_role_enabled` are independent — creating a plan/selection against an existing vault or role requires setting the corresponding `_enabled` flag to `false` AND supplying `vault_name`/`iam_role_name` for the data-source lookup; leaving the name unset while disabling creation breaks the lookup.
3. **Cross-Region/Cross-Account DR Needs a Pre-Existing Destination Vault**: `copy_action.destination_vault_arn` is the module's only cross-region/cross-account mechanism — it does not create, and cannot target, a vault that does not already exist with a resource policy authorizing the copy from this account.
4. **Continuous Backup Is Resource-Type-Gated**: `enable_continuous_backup` (AWS Backup's point-in-time-recovery mechanism) only takes effect for resource types AWS supports it for (RDS/Aurora at the time of writing) — verify current AWS support before relying on it for other resource types.
5. **Governance vs. Compliance Vault Lock Are Mutually Exclusive Outcomes**: `backup_vault_lock_configuration` with `changeable_for_days` set creates a revocable governance-mode lock; omitting it while setting `min_retention_days`/`max_retention_days` creates an irrevocable compliance-mode lock — there is no in-between, and a vault supports only one lock configuration.
6. **Both Backup IAM Policies Attach Unconditionally**: When `iam_role_enabled = true`, the module always attaches `AWSBackupServiceRolePolicyForBackup` and `AWSBackupServiceRolePolicyForS3Backup` — there is no input to attach only one; use `iam_role_enabled = false` with a hand-authored role to narrow this.
7. **Selection Combines ARNs, Tags, and Conditions**: `backup_resources`/`not_resources` (ARNs/patterns), `selection_tags` (tag equality), and `selection_conditions` (`string_equals`/`string_like`/`string_not_equals`/`string_not_like`) are all applied together on the same `aws_backup_selection` — they narrow the selection jointly, not as alternatives.
8. **No Submodules Ship With This Module**: Unlike some Cloud Posse modules, `terraform-aws-backup` has no `//modules/*` submodules — the `cloudposse/label/null` dependency seen in its source is an internal naming helper, not a usable submodule.
9. **Pre-1.x Examples May Use Removed Syntax**: The backup-schedule declaration syntax changed in `0.14.0`, and the deprecated pre-0.14.0 variables were removed entirely as of `1.x` — verify any copied example against the pinned `1.1.1` docs rather than an older blog post or Stack Overflow answer.
10. **Pin the Module Version**: Use an explicit `version = "1.1.1"` constraint for reproducible deployments; Cloud Posse's own usage examples intentionally omit a version pin, which is not a pattern to copy into real infrastructure.
