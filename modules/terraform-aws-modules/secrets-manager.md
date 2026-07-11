# Terraform AWS Secrets Manager Module

## Module Information

- **Module Name**: `secrets-manager`
- **Source**: `terraform-aws-modules/secrets-manager/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-secrets-manager
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/secrets-manager/aws/latest
- **Latest Version**: 2.1.0 (2026-01-08)
- **Minimum Versions**: Terraform >= 1.11, AWS Provider >= 6.28, random Provider >= 3.7
- **Purpose**: Terraform module that creates and manages a single AWS Secrets Manager secret — its current version/value, resource policy, cross-region replicas, and Lambda-based rotation schedule
- **Service**: AWS Secrets Manager
- **Category**: Security, Secrets Management
- **Keywords**: secrets-manager, secret-rotation, kms-encryption, cross-region-replication, resource-policy, ephemeral-resource, write-only-argument, random-password, database-credentials, api-keys, lambda-rotation, iam-policy-document, block-public-policy, secret-version, multi-region
- **Use For**: database password storage, API key/token management, structured JSON application credentials, multi-region secret replication for disaster recovery, automated Lambda-based password rotation, CI/CD pipeline secrets, cross-account secret sharing via resource policies, ephemeral non-state-persisted credential generation, conditional/per-environment secret provisioning

## Description

This Terraform module creates and configures a single AWS Secrets Manager secret. It wraps `aws_secretsmanager_secret`, `aws_secretsmanager_secret_version`, `aws_secretsmanager_secret_policy` (with an `aws_iam_policy_document` data source), and `aws_secretsmanager_secret_rotation` to expose a simpler, opinionated interface for the most common secret-management scenarios, while still allowing full control over encryption, access policy, replication, and rotation through pass-through variables. It does not define nested child submodules — it manages one root-level secret — but ships a Terragrunt-style `wrappers/` module for creating many similar secrets via `for_each`.

The module supports plaintext (`secret_string`), binary (`secret_binary`), and write-only (`secret_string_wo`) secret content, KMS encryption using either the AWS-owned default key or a customer-managed key (`kms_key_id`), and a configurable deletion recovery window. It can auto-generate a random password using an **ephemeral** `random_password` resource whose value is fed into the write-only `secret_string_wo` argument — meaning generated passwords are never written to Terraform state and are not exposed via any module output. Resource-based access control is provided through `policy_statements` (translated into an `aws_iam_policy_document`), with optional Zelkova validation (`block_public_policy`) to prevent accidental public exposure. Cross-region replication (`replica`) creates read-only replicas in one or more regions, each with its own optional KMS key. Automated rotation is supported via `enable_rotation`, `rotation_lambda_arn`, and `rotation_rules`, which routes the secret version through a lifecycle-`ignore_changes` resource so Terraform does not fight the Lambda-managed rotation.

AWS Secrets Manager itself is a fully managed service for storing, encrypting, and rotating credentials, API keys, and other sensitive values, avoiding hardcoded secrets in application code or Terraform state where possible.

## Key Features

- **Single Secret Resource**: Manages one `aws_secretsmanager_secret` plus its current version, with `name` or `name_prefix` naming
- **Multiple Content Types**: Plaintext (`secret_string`), base64 binary (`secret_binary`), or write-only (`secret_string_wo`, never persisted to state)
- **Ephemeral Random Password Generation**: `create_random_password = true` uses an ephemeral `random_password` resource (requires the `random` provider) whose result is written straight into `secret_string_wo` — the generated value is never stored in state or exposed as an output
- **KMS Encryption**: AWS-owned default key, or a customer-managed CMK via `kms_key_id`
- **Resource Policies**: Fine-grained access control via `policy_statements` (principals, actions, conditions), merged with `source_policy_documents`/`override_policy_documents`, with optional public-access validation (`block_public_policy`)
- **Cross-Region Replication**: `replica` map creates replicas per region, each with an optional dedicated KMS key; `force_overwrite_replica_secret` handles name collisions in the destination region
- **Lambda-Based Rotation**: `enable_rotation` + `rotation_lambda_arn` + `rotation_rules` (schedule or interval-based); `rotate_immediately` controls whether rotation fires on apply or waits for the next window
- **Externally-Managed Value Support**: `ignore_secret_changes` (and rotation, automatically) makes Terraform ignore drift on `secret_string`/`secret_binary`/`version_stages` so an external rotator or app can own the live value
- **Recovery Window**: `recovery_window_in_days` — `0` for immediate deletion or `7`-`30` days of recoverability
- **Per-Resource Region Override**: `region` argument to manage the secret in a region different from the default provider region
- **Module Wrappers**: `wrappers/` directory for creating multiple secret instances via `for_each` without duplicating module blocks

## Main Use Cases

1. **Database Credential Management**: Store JSON-structured RDS/Aurora credentials and rotate them with a Lambda function
2. **API Key / Token Storage**: Securely store third-party API keys, optionally with an auto-generated random value
3. **Cross-Account Secret Sharing**: Grant read access to other AWS accounts/roles via `policy_statements`
4. **Multi-Region Disaster Recovery**: Replicate secrets to standby regions with `replica`, each optionally encrypted with its own CMK
5. **CI/CD Pipeline Secrets**: Provide deployment credentials to pipelines without hardcoding them in source
6. **Ephemeral Credential Generation**: Create a secret whose initial value is a strong random password that is never written to Terraform state
7. **Externally Rotated Secrets**: Create the secret container in Terraform while letting a Lambda function or application own the live value (`ignore_secret_changes` / `enable_rotation`)
8. **Environment Toggling**: Conditionally create (or skip) a secret per environment using `create = false`

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created (affects all resources) |
| `name` | `string` | `null` | Friendly name of the secret (mutually exclusive with `name_prefix`); allows `/_+=.@-` |
| `name_prefix` | `string` | `null` | Creates a unique name beginning with the specified prefix |
| `description` | `string` | `null` | A description of the secret |
| `kms_key_id` | `string` | `null` | ARN or ID of a customer-managed KMS key; defaults to the AWS-owned `aws/secretsmanager` key when unset |
| `recovery_window_in_days` | `number` | `null` (AWS default `30`) | Deletion grace period: `0` (force immediate delete) or `7`-`30` days |
| `replica` | `map(object)` | `null` | Cross-region replicas keyed by region (or with explicit `region`/`kms_key_id` per entry) |
| `force_overwrite_replica_secret` | `bool` | `null` | Overwrite an existing secret with the same name in the destination replica region |
| `region` | `string` | `null` | Region for all created resources; defaults to the provider's configured region |
| `secret_string` | `string` | `null` | Plaintext secret content; required if `secret_binary`/`secret_string_wo` and `create_random_password` are unset |
| `secret_binary` | `string` | `null` | Base64-encoded binary secret content |
| `secret_string_wo` | `string` | `null` | Write-only plaintext secret content — never stored in Terraform state |
| `secret_string_wo_version` | `string` | `null` | Version marker paired with `secret_string_wo`; **must be incremented** to push a new write-only value to AWS |
| `version_stages` | `list(string)` | `null` | Staging labels for this version (e.g. `AWSCURRENT`); defaults to AWS auto-managing `AWSCURRENT` |
| `create_random_password` | `bool` | `false` | Auto-generate an ephemeral random password fed into `secret_string_wo` (requires `random` provider) |
| `random_password_length` | `number` | `32` | Length of the generated random password |
| `random_password_override_special` | `string` | `"!@#$%&*()-_=+[]{}<>:?"` | Special characters used when generating the random password |
| `ignore_secret_changes` | `bool` | `false` | Ignore Terraform drift on `secret_string`/`secret_binary`/`version_stages` (irreversible without a destructive change) |
| `create_policy` | `bool` | `false` | Create an `aws_secretsmanager_secret_policy` from `policy_statements` |
| `policy_statements` | `map(object)` | `null` | IAM policy statements (`sid`, `actions`, `effect`, `resources`, `principals`, `condition`, etc.) |
| `source_policy_documents` / `override_policy_documents` | `list(string)` | `[]` | Additional JSON policy documents merged into (or overriding statements in) the generated policy |
| `block_public_policy` | `bool` | `null` | Calls AWS Zelkova to validate the policy does not grant broad/public access |
| `enable_rotation` | `bool` | `false` | Create an `aws_secretsmanager_secret_rotation`; automatically routes the secret version through the ignore-changes resource |
| `rotation_lambda_arn` | `string` | `""` | ARN of the Lambda function that performs rotation |
| `rotation_rules` | `object` | `null` | `automatically_after_days`, `duration`, and/or `schedule_expression` for the rotation schedule |
| `rotate_immediately` | `bool` | `null` | Rotate immediately on apply vs. wait for the next scheduled rotation window |
| `tags` | `map(string)` | `{}` | Tags applied to all created resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `secret_arn` | The ARN of the secret |
| `secret_id` | The ID of the secret |
| `secret_name` | The friendly name of the secret |
| `secret_replica` | Attributes of the replica(s) created |
| `secret_string` | The secret's plaintext value (sensitive) — `null` when the value was supplied via `secret_string_wo` or `create_random_password` |
| `secret_binary` | The secret's binary value (sensitive) — `null` when the value was supplied via `secret_string_wo`/`secret_string` |
| `secret_version_id` | The unique identifier of the current secret version |

**Note**: There is no output for a `create_random_password`/`secret_string_wo`-generated value. Write-only arguments and ephemeral resources are never persisted to Terraform state or exposed as outputs by design — retrieve the generated value out-of-band (AWS CLI, console, or the consuming application calling `GetSecretValue`).

## Usage Examples

### Example 1: Basic Secret with JSON Credentials

```hcl
module "secrets_manager" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name_prefix             = "myapp-db-"
  description             = "Database credentials for MyApp"
  recovery_window_in_days = 30

  secret_string = jsonencode({
    username = "admin"
    password = "changeme"
  })

  tags = {
    Environment = "production"
    Application = "myapp"
  }
}
```

### Example 2: Ephemeral Auto-Generated Password

```hcl
module "secrets_manager" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name = "api-key"

  # Generates the value via an ephemeral random_password resource and writes
  # it through secret_string_wo. The value is NOT stored in state and is NOT
  # available as a module output — read it back from Secrets Manager directly.
  create_random_password           = true
  random_password_length           = 64
  random_password_override_special = "!@#$%^&*"

  # Bump this to force AWS to accept a newly generated password on a later apply;
  # leaving it unset means the initial value is written once and never changes.
  # secret_string_wo_version = "2"

  tags = {
    Team = "platform"
  }
}
```

### Example 3: Multi-Region Replication

```hcl
module "secrets_manager" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name          = "cross-region-secret"
  secret_string = "sensitive-data"

  replica = {
    us-east-1 = {
      kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/abc123"
    }
    dr = {
      region = "us-west-2" # explicit region since key name isn't a region
    }
  }

  tags = {
    Replicated = "true"
  }
}
```

### Example 4: With Resource Policy

```hcl
module "secrets_manager" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name                = "shared-secret"
  create_policy       = true
  block_public_policy = true

  policy_statements = {
    read = {
      sid    = "AllowCrossAccountRead"
      effect = "Allow"
      actions = [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ]
      resources = ["*"]
      principals = [{
        type        = "AWS"
        identifiers = ["arn:aws:iam::123456789012:root"]
      }]
    }
  }

  secret_string = jsonencode({
    api_key = "secret-value"
  })
}
```

### Example 5: With Lambda Rotation

```hcl
module "rotated_secret" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name          = "db-credentials"
  description   = "RDS credentials with automatic rotation"
  create_policy = true

  policy_statements = {
    lambda_rotation = {
      sid    = "AllowLambdaRotation"
      effect = "Allow"
      actions = [
        "secretsmanager:DescribeSecret",
        "secretsmanager:GetSecretValue",
        "secretsmanager:PutSecretValue",
        "secretsmanager:UpdateSecretVersionStage",
      ]
      resources = ["*"]
      principals = [{
        type        = "AWS"
        identifiers = [aws_lambda_function.rotation.arn]
      }]
    }
  }

  # Initial value only — rotation keeps the live value in sync out-of-band,
  # and enable_rotation automatically makes Terraform ignore drift on it.
  secret_string = jsonencode({
    engine   = "mysql"
    host     = "db.example.com"
    username = "admin"
    password = "initial-password"
    dbname   = "mydb"
    port     = 3306
  })

  enable_rotation     = true
  rotation_lambda_arn = aws_lambda_function.rotation.arn
  rotation_rules = {
    automatically_after_days = 30
  }
}
```

### Example 6: Custom KMS Encryption

```hcl
module "secrets_manager" {
  source  = "terraform-aws-modules/secrets-manager/aws"
  version = "~> 2.0"

  name       = "encrypted-secret"
  kms_key_id = aws_kms_key.secrets.arn

  secret_string = jsonencode({
    sensitive_data = "encrypted-with-cmk"
  })

  tags = {
    Compliance = "PCI-DSS"
  }
}
```

## Critical Warnings and Gotchas

**IMPORTANT**: Read these before generating configuration for this module — several are non-obvious and can cause failed applies or silently ignored settings:

1. **`create_random_password` never produces a readable value**: The generated password is produced by an **ephemeral** `random_password` resource (Terraform 1.10+ ephemeral resources) and written into the write-only `secret_string_wo` argument. Ephemeral and write-only values are never stored in Terraform state, so there is no `secret_string`/`secret_binary` output containing the generated password. Retrieve it via AWS CLI/SDK (`GetSecretValue`) or have the consuming application read it directly.
2. **`secret_string_wo` requires managing `secret_string_wo_version` yourself**: AWS only re-applies a write-only value when `secret_string_wo_version` changes. If left unset (`null`), the value is written once on creation and subsequent `terraform apply` runs will **not** push a new value even if the underlying content changed — increment the version to force an update.
3. **Requires Terraform >= 1.11**: Write-only arguments require Terraform 1.11+, and ephemeral resources require 1.10+. Pin the module and check the executing Terraform CLI version if `create_random_password`/`secret_string_wo` fail unexpectedly.
4. **Exactly one content source per secret**: Supply exactly one of `secret_string`, `secret_binary`, `secret_string_wo`, or set `create_random_password = true`. Supplying none leaves the secret version empty; supplying more than one is redundant/conflicting.
5. **`name` and `name_prefix` are mutually exclusive**: Specify one or the other, not both, when naming the secret.
6. **`enable_rotation` implicitly ignores drift on the secret value**: When rotation is enabled (or `ignore_secret_changes = true`), the module routes the version through a resource with `lifecycle { ignore_changes = [secret_string, secret_binary, version_stages] }`. Terraform will not detect or correct changes made by the rotation Lambda — this is intentional, not a bug.
7. **Replica deletion ordering**: Cross-region replicas created via `replica` must be removed before the primary secret can be deleted; plan destroy operations accordingly (remove replicas first, or accept a two-step `terraform apply`).
8. **`block_public_policy` requires `create_policy = true`**: It only takes effect on the `aws_secretsmanager_secret_policy` resource, which is only created when `create_policy = true` and `policy_statements` (or source/override documents) are supplied.
9. **`random` provider is required**: `create_random_password = true` needs the `hashicorp/random` provider (>= 3.7) declared in the root module, in addition to `hashicorp/aws`.
10. **No true submodules**: This module has no nested submodules to select between — for provisioning many secrets, use Terraform's native `for_each` on the module call or the pre-built wrapper in [`wrappers/`](https://github.com/terraform-aws-modules/terraform-aws-secrets-manager/tree/master/wrappers).

## Best Practices

### Security
1. **Use Customer-Managed KMS Keys for Regulated Data**: Set `kms_key_id` to a CMK for production/compliance-sensitive secrets rather than relying on the AWS-owned default key.
2. **Always Validate Policies**: Set `block_public_policy = true` whenever `create_policy = true` to catch overly broad resource policies before they're applied.
3. **Apply Least Privilege**: Scope `policy_statements` actions and `principals` as narrowly as possible (specific roles/accounts, specific `secretsmanager:*` actions).
4. **Access Over VPC Endpoints**: Use a Secrets Manager VPC interface endpoint to keep secret retrieval traffic off the public internet.
5. **Enable CloudTrail Auditing**: Monitor `GetSecretValue` and other API calls against sensitive secrets.

### Secret Management
1. **Use JSON for Multi-Field Secrets**: Store related credentials (host, username, password, port) together via `jsonencode()` for easier consumption.
2. **Prefer `name_prefix` for Reusable Modules**: Avoids naming collisions when the same module block is instantiated across environments/stacks.
3. **Set an Explicit Recovery Window**: Use `recovery_window_in_days = 30` in production and `0` only in throwaway/test environments where immediate deletion is safe.
4. **Tag Consistently**: Apply `Environment`, `Application`/`Owner`, and any compliance tags to every secret.

### Rotation
1. **Grant Minimal Lambda Permissions**: The rotation Lambda's execution role needs exactly `DescribeSecret`, `GetSecretValue`, `PutSecretValue`, and `UpdateSecretVersionStage` on the target secret.
2. **Use AWS-Provided Rotation Templates**: Start from AWS's rotation Lambda templates for RDS/Aurora/DocumentDB engines rather than writing rotation logic from scratch.
3. **Test in Non-Production First**: Validate a rotation schedule and Lambda logic before enabling `enable_rotation` on production secrets.
4. **Monitor Rotation Failures**: Alert on Lambda errors/CloudWatch metrics for the rotation function; a failed rotation can leave a secret in a partially rotated state.

### Replication and Disaster Recovery
1. **Replicate Only Critical Secrets**: Cross-region replication has cost and operational overhead — reserve it for secrets required by DR-active workloads.
2. **Use Region-Specific KMS Keys**: Set a distinct `kms_key_id` per replica entry when regional key isolation is required for compliance.
3. **Test Failover Paths**: Periodically validate that DR applications can actually read the replicated secret in the failover region.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-secrets-manager
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/secrets-manager/aws/latest
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-secrets-manager/blob/master/CHANGELOG.md
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-secrets-manager/tree/master/examples
- **AWS Provider `aws_secretsmanager_secret_version` (write-only argument docs)**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version
- **AWS Secrets Manager User Guide**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- **Secret Rotation**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html
- **Rotation Lambda Templates**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/reference_available-rotation-templates.html
- **Secrets Manager Best Practices**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html
- **Terraform Ephemeral Resources & Write-Only Arguments**: https://developer.hashicorp.com/terraform/language/resources/ephemeral
- **Pricing**: https://aws.amazon.com/secrets-manager/pricing/

## Notes for AI Agents

When generating Terraform code with this module:

1. **Set either `name` or `name_prefix`, never both** — prefer `name_prefix` for reusable/multi-environment modules.
2. **Set exactly one content source**: `secret_string`, `secret_binary`, `secret_string_wo`, or `create_random_password = true`.
3. **Never assume a generated-password output exists**: `create_random_password`/`secret_string_wo` values are ephemeral/write-only and are not readable from Terraform state or module outputs.
4. **When using `secret_string_wo` directly, manage `secret_string_wo_version`** — set it and increment it whenever the value must change; otherwise updates are silently skipped.
5. **Default to production-safe settings** unless told otherwise:
   ```hcl
   recovery_window_in_days = 30
   kms_key_id               = aws_kms_key.secrets.arn
   block_public_policy      = true
   ```
6. **When enabling rotation, always set both `rotation_lambda_arn` and `rotation_rules`**, and grant the Lambda's role read/write access via `policy_statements`.
7. **Don't fight rotation with Terraform**: once `enable_rotation = true`, don't expect `terraform plan` to show/correct drift on the secret's live value — that's by design.
8. **Delete replicas before the primary secret** when planning a `terraform destroy` that includes `replica` entries.
9. **Declare the `random` provider** (>= 3.7) alongside `aws` whenever `create_random_password = true` is used.
10. **Pin the module version** (e.g., `version = "~> 2.0"`) and require Terraform `>= 1.11` in the root module's `required_version` to support write-only arguments.
11. **Tag consistently** (`Environment`, `Application`/`Owner`, plus any org-mandated compliance tags).
