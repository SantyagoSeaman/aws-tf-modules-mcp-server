# Terraform AWS Atlantis Module

## Module Information

- **Module Name**: `atlantis`
- **Source**: `terraform-aws-modules/atlantis/aws`
- **Version**: 5.1.0
- **Terraform**: >= 1.10
- **AWS Provider**: >= 6.28
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-atlantis
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/atlantis/aws/latest
- **Purpose**: Deploy Atlantis as a single always-on ECS Fargate task, fronted by an ALB, for pull-request-driven Terraform plan/apply automation
- **Service**: AWS ECS Fargate, Application Load Balancer, ACM, Route53, EFS
- **Category**: DevOps, CI/CD, Infrastructure Automation
- **Keywords**: atlantis, terraform-automation, gitops, ecs-fargate, fargate, alb, webhook, github, gitlab, pull-request, infrastructure-as-code, ci-cd, secrets-manager, efs, terraform-plan

## Description

This module deploys [Atlantis](https://www.runatlantis.io/) on AWS using Amazon ECS Fargate to enable pull-request-driven Terraform workflows. Atlantis listens for GitHub, GitLab, or Bitbucket Cloud webhook events and automatically runs `terraform plan` (and, after approval, `terraform apply`) directly against pull requests, giving teams a collaborative, auditable way to review infrastructure changes before they are applied. The module provisions the full stack required to run it in production: an internet-facing Application Load Balancer with HTTPS listener and HTTP→HTTPS redirect, an ECS Fargate cluster and service running the official Atlantis container image, an ACM certificate validated via Route53 DNS, Route53 `A`/`AAAA` alias records, and (optionally) an EFS file system so Terraform plan output survives task restarts and redeployments.

Version 5.x uses an object-based configuration model (`atlantis`, `service`, `alb`, `cluster`, `efs`) instead of many flat top-level variables, mirroring the underlying `terraform-aws-modules/ecs`, `terraform-aws-modules/alb`, and `terraform-aws-modules/efs` submodules it composes. `create_cluster = false` and `create_alb = false` let an existing ECS cluster or ALB be reused instead of creating new ones, which is the common pattern for centralizing Atlantis with other services. Credentials (VCS tokens, webhook secrets) are expected to be stored in AWS Secrets Manager and injected into the container via the `secrets` block, never as plain environment variables.

Atlantis itself runs as **exactly one ECS task** — `desired_count` is hardcoded to `1` inside the module and is not exposed as a variable, because Atlantis relies on local file-based plan storage and locking and does not support horizontal scaling. High availability is achieved through fast, EFS-backed task replacement (Multi-AZ ALB, quick ECS-driven recovery) rather than running multiple concurrent tasks. Two small companion submodules (`github-repository-webhook`, `gitlab-repository-webhook`) automate creation of the VCS-side webhooks that point at the deployed Atlantis URL.

## Key Features

- **Single-Task ECS Fargate Deployment**: Serverless, always-on container running the official `ghcr.io/runatlantis/atlantis` image (ARM64 by default)
- **Application Load Balancer**: HTTPS listener with TLS 1.3 policy by default, automatic HTTP→HTTPS redirect, health check on `/healthz`
- **Multi-VCS Support**: GitHub, GitLab, and Bitbucket Cloud, configured purely through `ATLANTIS_*` environment variables/secrets (no code branching)
- **EFS Persistent Storage**: Optional EFS volume, auto-mounted at `/home/atlantis`, with an IAM-authorized access point scoped to the task role — survives task replacement/redeploys
- **Secrets Manager Integration**: VCS tokens, webhook secrets, and GitHub App keys are injected as ECS `secrets`, never as plain `environment` values
- **GitHub App Auth**: Supports GitHub App-based authentication (`ATLANTIS_GH_APP_ID`/`ATLANTIS_GH_APP_KEY`) as a more secure alternative to a personal access token
- **ACM + Route53 Automation**: Creates and DNS-validates an ACM certificate and creates the `A`/`AAAA` alias records automatically
- **Bring-Your-Own-Infrastructure**: `create_cluster = false` / `create_alb = false` / `create_certificate = false` reuse an existing ECS cluster, ALB, or ACM certificate
- **Object-Based Configuration**: `atlantis`, `service`, `alb`, `cluster`, `efs` objects pass straight through to the respective nested `terraform-aws-modules` submodules
- **Webhook Automation Submodules**: Dedicated submodules create GitHub/GitLab webhooks pointed at `${module.atlantis.url}/events`
- **CloudWatch Logs**: Container and ECS cluster logging enabled by default (14/90-day retention respectively)
- **Auto-Injected Runtime Config**: `ATLANTIS_PORT` and `ATLANTIS_ATLANTIS_URL` are computed and injected automatically — do not set them manually

## Main Use Cases

1. **Pull Request-Based Infrastructure Changes**: Automate `terraform plan`/`apply` triggered by pull/merge request events
2. **Collaborative Infrastructure Review**: Require peer approval before Terraform changes can be applied
3. **GitOps for Infrastructure**: Use Git history as the audit trail and source of truth for infrastructure state changes
4. **Centralized Terraform Execution**: Provide one consistent runner/version for Terraform across many repositories
5. **Multi-Repository Infrastructure Management**: Run one Atlantis instance serving several infrastructure repositories via `ATLANTIS_REPO_ALLOWLIST`
6. **Compliance and Auditability**: Generate a durable record of plan output, approvals, and applies tied to pull requests
7. **Multi-Account Terraform Management**: Run a central Atlantis with `sts:AssumeRole` permissions into target-account Terraform roles
8. **Self-Hosted Alternative to Terraform Cloud/HCP Terraform**: Keep plan/apply execution inside your own VPC instead of a SaaS runner

## Key Root Module Variables

### Core

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls creation of (nearly) all resources |
| `name` | `string` | `"atlantis"` | Common name applied to all resources |
| `vpc_id` | `string` | `""` (effectively required) | VPC ID for all networked resources |
| `region` | `string` | `null` | Region to manage resources in; defaults to provider's region |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

### `atlantis` object (container definition)

Passed to the ECS container-definition module; important properties:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `image` | `string` | `"ghcr.io/runatlantis/atlantis:latest"` | Container image |
| `cpu` | `number` | `2048` | Container CPU units |
| `memory` | `number` | `4096` | Container memory (MiB) |
| `port` | `number` | `4141` | Container port; also used for ALB target group and security group ingress |
| `environment` | `list(object)` | `[]` | `{ name, value }` plain env vars |
| `secrets` | `list(object)` | `[]` | `{ name, valueFrom }` — Secrets Manager/SSM-backed env vars |
| `command` / `entrypoint` | `list(string)` | `null` | Override container command/entrypoint |
| `healthCheck` | `object` | `null` | Optional ECS container health check (separate from ALB health check) |
| `cloudwatch_log_group_retention_in_days` | `number` | `14` | Container log retention |

### `service` object (ECS service/task definition)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `subnet_ids` | `list(string)` | `[]` | Subnets for ECS tasks (private, with NAT/VPC endpoints — tasks get no public IP by default) |
| `task_exec_secret_arns` | `list(string)` | `[]` | Secret ARNs the task **execution** role may read (needed for `atlantis.secrets`) |
| `tasks_iam_role_policies` | `map(string)` | `{}` | Policy ARNs attached to the task (application) role — grants Atlantis its actual AWS permissions |
| `cpu` / `memory` | `number` | `2048` / `4096` | Task-level CPU/memory (should match or exceed container-level values) |
| `runtime_platform` | `object` | `{ operating_system_family = "LINUX", cpu_architecture = "ARM64" }` | Override to `X86_64` if using a custom amd64-only image |
| `assign_public_ip` | `bool` | `false` | Tasks are not publicly addressable by default |
| `launch_type` | `string` | `"FARGATE"` | Compute engine |

**Not configurable**: `desired_count` is hardcoded to `1` and `enable_execute_command` is hardcoded to `false` (ECS Exec disabled) — neither is exposed as an override.

### `alb` object

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `subnet_ids` | `list(string)` | `[]` | Subnets for the ALB (public for internet-facing) |
| `internal` | `bool` | `false` (AWS default) | ALB is internet-facing unless set to `true` |
| `enable_deletion_protection` | `bool` | `true` | Prevents accidental `terraform destroy`; disable explicitly for throwaway/dev stacks |
| `security_group_ingress_rules` | `map` | `80/tcp` + `443/tcp` from `0.0.0.0/0` | **Public by default** — restrict this for private/internal deployments |
| `access_logs` / `connection_logs` | `object` | `null` | S3 bucket for ALB access/connection logs |
| `associate_web_acl` / `web_acl_arn` | `bool` / `string` | `false` / `null` | Attach an existing WAFv2 Web ACL |

### Certificate, DNS, cluster, and EFS

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_cluster` / `cluster_arn` | `bool` / `string` | `true` / `""` | Create a new ECS cluster or attach to an existing one |
| `create_alb` / `alb_target_group_arn` / `alb_security_group_id` | `bool` / `string` / `string` | `true` / `""` / `""` | Create a new ALB or reuse an existing target group + security group |
| `create_certificate` / `certificate_arn` | `bool` / `string` | `true` / `""` | Create+validate an ACM cert or bring your own |
| `certificate_domain_name` | `string` | `""` | Domain to request the ACM certificate for |
| `route53_zone_id` | `string` | `""` | Zone for ACM validation records and the `A`/`AAAA` alias records |
| `create_route53_records` / `route53_record_name` | `bool` / `string` | `true` / `null` | Toggle and name the Route53 alias records |
| `enable_efs` | `bool` | `false` | Mount an EFS volume at `/home/atlantis` for persistent plan storage |
| `efs` | `object` | `{}` | EFS settings — `mount_targets` (required per-AZ if enabled), encryption, lifecycle policy |

## Key Outputs

| Output | Description |
|--------|-------------|
| `url` | HTTPS URL of the Atlantis instance (used as the webhook base URL, `${url}/events`) |
| `alb` | Full ALB submodule output object (ARN, DNS name, security group ID, target groups, Route53 records) |
| `cluster` | Full ECS cluster submodule output object (ARN, name) |
| `service` | Full ECS service submodule output object (task role ARN, task exec role ARN, security group ID, task definition ARN) |
| `efs` | Full EFS submodule output object (file system ID, DNS name, access points) — only populated when `enable_efs = true` |

## Submodules

### 1. github-repository-webhook

**Purpose**: Creates GitHub repository webhooks pointed at the deployed Atlantis `/events` endpoint.
**Source**: `terraform-aws-modules/atlantis/aws//modules/github-repository-webhook`
**Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/atlantis/aws/latest/submodules/github-repository-webhook
**Requirements**: GitHub provider (`integrations/github`) >= 5.0
**Key Features**: Bulk webhook creation across repositories, configurable webhook secret, minimal single-resource (`github_repository_webhook`) implementation

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the webhooks |
| `repositories` | `list(string)` | `[]` | Repository names under the provider's configured `owner` |
| `webhook_url` | `string` | `""` | Atlantis webhook URL, e.g. `${module.atlantis.url}/events` |
| `webhook_secret` | `string` | `""` | Shared secret Atlantis uses to validate incoming webhook payloads |

**Output**: `repository_webhook_urls` — map of repository name to webhook URL

```hcl
provider "github" {
  token = var.github_token
  owner = "myorg"
}

module "github_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/github-repository-webhook"

  repositories   = ["infrastructure-prod", "infrastructure-staging"]
  webhook_url    = "${module.atlantis.url}/events"
  webhook_secret = random_password.webhook_secret.result
}
```

### 2. gitlab-repository-webhook

**Purpose**: Creates GitLab project webhooks pointed at the deployed Atlantis `/events` endpoint.
**Source**: `terraform-aws-modules/atlantis/aws//modules/gitlab-repository-webhook`
**Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/atlantis/aws/latest/submodules/gitlab-repository-webhook
**Requirements**: GitLab provider (`gitlabhq/gitlab`) >= 16.0
**Key Features**: Bulk webhook creation across projects, configurable webhook secret, supports self-hosted GitLab via provider `base_url`

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the webhooks |
| `repositories` | `list(string)` | `[]` | Project names/paths under the configured GitLab instance |
| `webhook_url` | `string` | `""` | Atlantis webhook URL |
| `webhook_secret` | `string` | `""` | Shared secret Atlantis uses to validate incoming webhook payloads |

**Output**: `repository_webhook_urls` — map of project name to webhook URL

```hcl
provider "gitlab" {
  token    = var.gitlab_token
  base_url = "https://gitlab.example.com/api/v4/"
}

module "gitlab_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/gitlab-repository-webhook"

  repositories   = ["infrastructure/prod", "infrastructure/staging"]
  webhook_url    = "${module.atlantis.url}/events"
  webhook_secret = random_password.webhook_secret.result
}
```

**Note**: Bitbucket Cloud is supported by Atlantis itself (via `ATLANTIS_BITBUCKET_*` env vars), but this module ships no `bitbucket-repository-webhook` submodule — the webhook must be created manually in Bitbucket.

## Usage Examples

### Complete GitHub Deployment

```hcl
module "atlantis" {
  source  = "terraform-aws-modules/atlantis/aws"
  version = "~> 5.1"

  name   = "atlantis"
  vpc_id = module.vpc.vpc_id

  # Atlantis container configuration
  atlantis = {
    environment = [
      { name = "ATLANTIS_GH_USER", value = "atlantis-bot" },
      { name = "ATLANTIS_REPO_ALLOWLIST", value = "github.com/myorg/*" },
      { name = "ATLANTIS_DEFAULT_TF_VERSION", value = "1.9.0" },
    ]

    secrets = [
      { name = "ATLANTIS_GH_TOKEN", valueFrom = aws_secretsmanager_secret.github_token.arn },
      { name = "ATLANTIS_GH_WEBHOOK_SECRET", valueFrom = aws_secretsmanager_secret.webhook_secret.arn },
    ]
  }

  # ECS service configuration
  service = {
    subnet_ids = module.vpc.private_subnets

    task_exec_secret_arns = [
      aws_secretsmanager_secret.github_token.arn,
      aws_secretsmanager_secret.webhook_secret.arn,
    ]

    # Permissions Atlantis itself needs to run terraform plan/apply
    tasks_iam_role_policies = {
      terraform_permissions = aws_iam_policy.atlantis_terraform.arn
    }
  }

  # ALB configuration
  alb = {
    subnet_ids = module.vpc.public_subnets
  }

  # DNS and certificate
  certificate_domain_name = "atlantis.example.com"
  route53_zone_id         = data.aws_route53_zone.this.id

  # Persist plan output across task restarts/redeploys
  enable_efs = true
  efs = {
    mount_targets = {
      "eu-west-1a" = { subnet_id = module.vpc.private_subnets[0] }
      "eu-west-1b" = { subnet_id = module.vpc.private_subnets[1] }
    }
  }

  tags = {
    Environment = "production"
  }
}

module "github_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/github-repository-webhook"

  repositories   = ["myorg/infrastructure", "myorg/terraform-modules"]
  webhook_url    = "${module.atlantis.url}/events"
  webhook_secret = random_password.webhook_secret.result
}

resource "aws_secretsmanager_secret" "github_token" {
  name = "atlantis/github-token"
}

resource "aws_secretsmanager_secret" "webhook_secret" {
  name = "atlantis/webhook-secret"
}

resource "random_password" "webhook_secret" {
  length  = 32
  special = true
}
```

### Using an Existing ECS Cluster and ALB

```hcl
module "atlantis" {
  source  = "terraform-aws-modules/atlantis/aws"
  version = "~> 5.1"

  name   = "atlantis"
  vpc_id = module.vpc.vpc_id

  create_cluster = false
  cluster_arn    = aws_ecs_cluster.existing.arn

  create_alb            = false
  alb_target_group_arn  = aws_lb_target_group.atlantis.arn
  alb_security_group_id = aws_security_group.alb.id

  create_certificate = false
  certificate_arn    = aws_acm_certificate.existing.arn

  atlantis = {
    environment = [
      { name = "ATLANTIS_GH_USER", value = "atlantis-bot" },
      { name = "ATLANTIS_REPO_ALLOWLIST", value = "github.com/myorg/*" },
    ]
    secrets = [
      { name = "ATLANTIS_GH_TOKEN", valueFrom = aws_secretsmanager_secret.github_token.arn },
    ]
  }

  service = {
    subnet_ids            = module.vpc.private_subnets
    task_exec_secret_arns = [aws_secretsmanager_secret.github_token.arn]
  }

  tags = {
    Environment = "production"
  }
}
```

### Multi-Account with Cross-Account IAM Roles

```hcl
module "atlantis" {
  source  = "terraform-aws-modules/atlantis/aws"
  version = "~> 5.1"

  name   = "atlantis"
  vpc_id = module.vpc.vpc_id

  atlantis = {
    environment = [
      { name = "ATLANTIS_GH_USER", value = "atlantis-bot" },
      { name = "ATLANTIS_REPO_ALLOWLIST", value = "github.com/myorg/infra-*" },
      { name = "ATLANTIS_PARALLEL_PLAN", value = "true" },
      { name = "ATLANTIS_PARALLEL_APPLY", value = "true" },
    ]
    secrets = [
      { name = "ATLANTIS_GH_TOKEN", valueFrom = aws_secretsmanager_secret.github_token.arn },
      { name = "ATLANTIS_GH_WEBHOOK_SECRET", valueFrom = aws_secretsmanager_secret.webhook_secret.arn },
    ]
  }

  service = {
    subnet_ids = module.vpc.private_subnets
    task_exec_secret_arns = [
      aws_secretsmanager_secret.github_token.arn,
      aws_secretsmanager_secret.webhook_secret.arn,
    ]

    # Cross-account assume-role permissions
    tasks_iam_role_policies = {
      cross_account = aws_iam_policy.assume_terraform_roles.arn
      state_access  = aws_iam_policy.terraform_state.arn
    }
  }

  alb = {
    subnet_ids = module.vpc.public_subnets
  }

  certificate_domain_name = "atlantis.example.com"
  route53_zone_id         = data.aws_route53_zone.this.id
  enable_efs              = true

  tags = {
    Environment = "production"
    Scope       = "multi-account"
  }
}

resource "aws_iam_policy" "assume_terraform_roles" {
  name = "atlantis-assume-terraform-roles"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "sts:AssumeRole"
        Resource = [
          "arn:aws:iam::111111111111:role/terraform",
          "arn:aws:iam::222222222222:role/terraform",
          "arn:aws:iam::333333333333:role/terraform",
        ]
      }
    ]
  })
}
```

## Best Practices

### Deployment

1. **Use Private Subnets for `service.subnet_ids`**: Tasks get no public IP by default (`assign_public_ip = false`); ensure private subnets have a NAT Gateway or VPC endpoints (`ecr.api`, `ecr.dkr`, `secretsmanager`, `logs`, `s3`) for image pulls and outbound calls
2. **Enable EFS in Production**: Without EFS, in-flight plan output is lost whenever the single task is replaced (deploys, crashes, AZ failure)
3. **Expect Brief Downtime on Deploy**: `desired_count` is fixed at 1 and deployment uses `minimum_healthy_percent = 0`, so the old task is stopped before the new one starts — plan a maintenance window or communicate expected blips
4. **Don't Try to Scale Horizontally**: Atlantis supports exactly one task; scale vertically (`atlantis.cpu`/`atlantis.memory`, `service.cpu`/`service.memory`) if plans are slow, not by increasing task count

### Security

5. **Store Credentials in Secrets Manager**: Pass VCS tokens and webhook secrets via `atlantis.secrets` (+ `service.task_exec_secret_arns`), never via `atlantis.environment`
6. **Prefer GitHub App Auth Over PAT**: Use `ATLANTIS_GH_APP_ID`/`ATLANTIS_GH_APP_KEY` where possible — scoped, revocable, and not tied to a human account
7. **Always Set `ATLANTIS_REPO_ALLOWLIST`**: Without it Atlantis will refuse to run, but an overly broad allowlist (`*`) exposes any repo with access to the webhook to plan/apply
8. **Always Configure a Webhook Secret**: Required to validate that inbound `/events` requests actually originate from your VCS
9. **The ALB is Public by Default**: `alb.security_group_ingress_rules` defaults to `0.0.0.0/0` on 80/443 — restrict to known CIDRs, put it behind a WAF (`alb.associate_web_acl`), or set `alb.internal = true` for VPN/private access
10. **Scope `tasks_iam_role_policies` Tightly**: This is the IAM identity Atlantis assumes to run `terraform apply` — grant only the state bucket, lock table, KMS key, and target-account `AssumeRole` permissions actually needed, not `AdministratorAccess`

### Terraform State Access

11. **Grant S3 State Access**: Task role needs read/write on the relevant state bucket(s)/prefixes
12. **Grant Lock Table Access**: DynamoDB (or S3-native locking) permissions for the backend in use
13. **Grant KMS Access**: `kms:Decrypt`/`kms:GenerateDataKey` if state or secrets are encrypted with a customer-managed key

### Configuration

14. **Pin `ATLANTIS_DEFAULT_TF_VERSION`**: Avoid surprise Terraform version drift between local dev and Atlantis
15. **Require Approvals Before Apply**: Configure `apply_requirements: [approved]` in the Atlantis server/repo config
16. **Enable Parallel Plan/Apply for Multi-Project Repos**: `ATLANTIS_PARALLEL_PLAN` / `ATLANTIS_PARALLEL_APPLY` speed up monorepos, but combine with tight `tasks_iam_role_policies` since applies can run concurrently
17. **Match `service.runtime_platform` to Your Image**: Default is ARM64; override `cpu_architecture = "X86_64"` if supplying a custom amd64-only image

### Operations

18. **Enable CloudWatch Logs (default on)**: Keep `atlantis.enable_cloudwatch_logging = true` for plan/apply auditability
19. **Tag Consistently**: Apply `tags` for environment, cost center, and owner across the module and reused resources
20. **Test Upgrades in Non-Production**: Validate new Atlantis image versions and module upgrades in a staging deployment before rolling to production

## Additional Resources

- **Atlantis Documentation**: https://www.runatlantis.io/docs/
- **Module GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-atlantis
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/atlantis/aws/latest
- **Supplemental Module Docs (GitHub App setup)**: https://github.com/terraform-aws-modules/terraform-aws-atlantis/blob/master/docs/README.md
- **Atlantis Server Configuration**: https://www.runatlantis.io/docs/server-configuration.html
- **Repository-Level `atlantis.yaml`**: https://www.runatlantis.io/docs/repo-level-atlantis-yaml.html
- **Custom Workflows**: https://www.runatlantis.io/docs/custom-workflows.html
- **Atlantis Security Guidance**: https://www.runatlantis.io/docs/security.html
- **AWS ECS Best Practices**: https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/

## Notes for AI Agents

### Module Selection

- **Use this module** for collaborative, pull-request-based Terraform workflows with automated planning and human-gated applies
- **Use AWS CodePipeline/CodeBuild** for fully automated CI/CD that doesn't need pull-request-triggered plans
- **Use Terraform Cloud/HCP Terraform** for a HashiCorp-managed SaaS equivalent instead of self-hosting on ECS

### Critical Constraints (do not design around these incorrectly)

- **`desired_count` is hardcoded to `1`** — do not expose it as a variable in generated code or assume multi-task HA is possible
- **`enable_execute_command` is hardcoded to `false`** — ECS Exec cannot be enabled through this module
- **`ATLANTIS_PORT` and `ATLANTIS_ATLANTIS_URL` are auto-injected** by the module — do not set them in `atlantis.environment`, they will be duplicated
- **The ALB is internet-facing and open to `0.0.0.0/0` on 80/443 by default** — flag this to the user and set `alb.security_group_ingress_rules` or `alb.internal = true` for anything beyond a public demo

### Sizing Guidance

- **Defaults**: `atlantis.cpu = 2048` / `atlantis.memory = 4096` (2 vCPU / 4 GB), ARM64 — sufficient for small-to-medium teams
- **Larger/parallel workloads**: increase `atlantis`/`service` `cpu`/`memory` (e.g., 4096/8192) and enable `ATLANTIS_PARALLEL_PLAN`/`ATLANTIS_PARALLEL_APPLY`, since there is only ever one task to absorb load
- **Multi-account**: keep Atlantis in a central "tooling" account with `tasks_iam_role_policies` granting `sts:AssumeRole` into per-account Terraform roles

### Required Environment Variables (via `atlantis.environment` / `atlantis.secrets`)

**GitHub (PAT)**: `ATLANTIS_GH_USER`, `ATLANTIS_GH_TOKEN` (secret), `ATLANTIS_GH_WEBHOOK_SECRET` (secret), `ATLANTIS_REPO_ALLOWLIST`
**GitHub (App, preferred)**: `ATLANTIS_GH_APP_ID` (secret), `ATLANTIS_GH_APP_KEY` (secret), `ATLANTIS_GH_WEBHOOK_SECRET` (secret), `ATLANTIS_REPO_ALLOWLIST`
**GitLab**: `ATLANTIS_GITLAB_USER`, `ATLANTIS_GITLAB_TOKEN` (secret), `ATLANTIS_GITLAB_WEBHOOK_SECRET` (secret), `ATLANTIS_GITLAB_HOSTNAME` (self-hosted only), `ATLANTIS_REPO_ALLOWLIST`
**Bitbucket Cloud**: `ATLANTIS_BITBUCKET_USER`, `ATLANTIS_BITBUCKET_TOKEN` (secret), `ATLANTIS_REPO_ALLOWLIST` — webhook must be created manually (no submodule)

### IAM Permissions

**Task execution role** (managed automatically): `secretsmanager:GetSecretValue` for the ARNs in `service.task_exec_secret_arns`, CloudWatch Logs write, ECR image pull
**Task (application) role** — configure via `service.tasks_iam_role_policies`: S3 read/write on state buckets, DynamoDB read/write on lock tables, KMS decrypt/encrypt for encrypted state, `sts:AssumeRole` for cross-account access, plus whatever AWS resource permissions the managed Terraform code itself needs

### Cost Estimation (rough, region-dependent, single task only — no HA multiplier)

- **Fargate compute** (default 2 vCPU / 4 GB, always-on): ~$70-90/month
- **ALB**: ~$20-25/month base + LCU usage charges
- **EFS**: ~$0.30/GB-month (typically a few dollars/month for plan storage)
- **Total baseline**: roughly $90-130/month

### Troubleshooting

- **Webhooks not received**: check ALB security group ingress, Route53 DNS resolution, and the VCS provider's webhook delivery logs
- **Plans failing with auth errors**: verify VCS token/App key validity and that `service.task_exec_secret_arns` includes the relevant secret ARNs
- **Apply stuck**: check `apply_requirements` (e.g., `approved`), confirm the PR is approved, and check for existing plan locks
- **Task restarting/unhealthy**: check CloudWatch Logs, container `healthCheck`/ALB target group health (`/healthz`), and CPU/memory limits
- **State access errors**: verify `tasks_iam_role_policies` grants S3/DynamoDB/KMS access matching the backend configuration
- **Plan output lost after redeploy**: `enable_efs` was likely `false` — enable it and provide `efs.mount_targets` for each AZ used by `service.subnet_ids`
