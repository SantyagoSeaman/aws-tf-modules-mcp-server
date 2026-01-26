# Terraform AWS Atlantis Module

## Module Information

- **Module Name**: `atlantis`
- **Source**: `terraform-aws-modules/atlantis/aws`
- **Version**: 5.1.0
- **Terraform**: >= 1.10
- **AWS Provider**: >= 6.28
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-atlantis
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/atlantis/aws/latest
- **Purpose**: Deploy Atlantis on AWS Fargate for automated Terraform workflow management through pull requests
- **Service**: AWS ECS Fargate, Application Load Balancer, EFS
- **Category**: DevOps, CI/CD, Infrastructure Automation
- **Keywords**: atlantis, terraform-automation, gitops, ecs-fargate, alb, webhook, github, gitlab, pull-request, infrastructure-as-code, ci-cd, secrets-manager, efs

## Description

This module deploys Atlantis on AWS using Amazon ECS Fargate for automated Terraform workflow management through pull requests. Atlantis enables teams to collaborate on infrastructure changes by automatically running Terraform plan and apply operations directly from pull requests in GitHub, GitLab, or Bitbucket Cloud. The module creates a complete infrastructure stack including an Application Load Balancer, ECS Fargate cluster and service, optional EFS storage for persistent plan files, ACM certificates, Route53 DNS records, and IAM roles.

Version 5.x introduces a redesigned configuration model using object-based parameters (`atlantis`, `service`, `alb`, `cluster`, `efs`) instead of flat variables. This provides better organization and allows reusing existing infrastructure components (ECS clusters, ALBs) via `create_cluster: false` and `create_alb: false` flags. The module integrates with AWS Secrets Manager for secure credential handling and supports multi-VCS providers through webhook submodules.

## Key Features

- **ECS Fargate Deployment**: Serverless container deployment with automatic scaling and no server management
- **Application Load Balancer**: HTTPS load balancer with SSL/TLS termination, health checks, and optional WAF integration
- **Multi-VCS Support**: Integration with GitHub, GitLab, and Bitbucket Cloud through webhook configuration
- **EFS Persistent Storage**: Optional Amazon EFS for persistent Terraform plan storage across container restarts
- **Secrets Management**: AWS Secrets Manager integration for GitHub/GitLab tokens and webhook secrets
- **ACM Certificate Support**: Automatic certificate creation and validation via Route53 DNS
- **Route53 Integration**: Automatic DNS record creation for custom domain names
- **Existing Infrastructure Reuse**: Support for existing ECS clusters and ALBs via feature flags
- **Object-Based Configuration**: Organized configuration through `atlantis`, `service`, `alb`, `cluster`, `efs` objects
- **Auto-Planning**: Automatic Terraform plan generation on pull request events
- **Plan Locking**: Prevents concurrent infrastructure modifications through project locking
- **CloudWatch Logs**: Container logs integration for monitoring and debugging

## Use Cases

1. **Pull Request-Based Infrastructure Changes**: Automate Terraform workflows where changes are proposed, reviewed, and applied through Git pull requests
2. **Collaborative Infrastructure Management**: Enable teams to safely propose and review infrastructure changes with approval workflows
3. **GitOps Implementation**: Use Git as the single source of truth for infrastructure state and changes
4. **Centralized Terraform Execution**: Provide consistent Terraform execution environment with standardized versions and configurations
5. **Multi-Repository Infrastructure**: Manage Terraform code across multiple repositories with centralized execution
6. **Infrastructure Code Review**: Facilitate code review with automatic plan generation showing exact infrastructure impacts
7. **Compliance and Auditability**: Create audit trails through Git history and pull request approvals
8. **Multi-Account Terraform Management**: Centralize Atlantis with cross-account IAM roles for managing multiple AWS accounts

## Submodules

### 1. github-repository-webhook

Creates GitHub repository webhooks for Atlantis integration.

**Purpose**: Automate GitHub webhook creation to trigger Atlantis on pull request events.

**Requirements**: GitHub Provider >= 5.0

**Key Variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create webhooks |
| `repositories` | `list(string)` | `[]` | List of repository names |
| `webhook_url` | `string` | `""` | Atlantis webhook URL (e.g., `${module.atlantis.url}/events`) |
| `webhook_secret` | `string` | `""` | Webhook secret for authentication |

**Output**: `repository_webhook_urls` - Map of repository names to webhook URLs

**Usage Example**:

```hcl
module "github_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/github-repository-webhook"

  repositories   = ["infrastructure-prod", "infrastructure-staging"]
  webhook_url    = "${module.atlantis.url}/events"
  webhook_secret = random_password.webhook_secret.result
}

provider "github" {
  token = var.github_token
  owner = "myorg"
}
```

### 2. gitlab-repository-webhook

Creates GitLab project webhooks for Atlantis integration.

**Purpose**: Automate GitLab webhook creation to trigger Atlantis on merge request events.

**Requirements**: GitLab Provider >= 16.0

**Key Variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create webhooks |
| `repositories` | `list(string)` | `[]` | List of project names |
| `webhook_url` | `string` | `""` | Atlantis webhook URL |
| `webhook_secret` | `string` | `""` | Webhook secret for authentication |

**Output**: `repository_webhook_urls` - Map of project names to webhook URLs

**Usage Example**:

```hcl
module "gitlab_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/gitlab-repository-webhook"

  repositories   = ["infrastructure/prod", "infrastructure/staging"]
  webhook_url    = "${module.atlantis.url}/events"
  webhook_secret = random_password.webhook_secret.result
}

provider "gitlab" {
  token    = var.gitlab_token
  base_url = "https://gitlab.example.com/api/v4/"
}
```

## Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls resource creation |
| `name` | `string` | `"atlantis"` | Common name for all resources |
| `vpc_id` | `string` | **required** | VPC ID for resource provisioning |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

### Atlantis Container Configuration

The `atlantis` object configures the container:

| Property | Type | Description |
|----------|------|-------------|
| `cpu` | `number` | CPU units (default: 512) |
| `memory` | `number` | Memory in MiB (default: 1024) |
| `image` | `string` | Docker image (default: official Atlantis image) |
| `environment` | `list(object)` | Environment variables (`name`, `value` pairs) |
| `secrets` | `list(object)` | Secrets from Secrets Manager (`name`, `valueFrom` pairs) |
| `command` | `list(string)` | Override container command |
| `entrypoint` | `list(string)` | Override container entrypoint |

### ECS Cluster Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_cluster` | `bool` | `true` | Create ECS cluster or use existing |
| `cluster_arn` | `string` | `""` | Existing cluster ARN (required if `create_cluster` is false) |
| `cluster` | `object` | `{}` | Cluster settings, logging, capacity providers |

### ECS Service Configuration

The `service` object configures the ECS service:

| Property | Type | Description |
|----------|------|-------------|
| `subnet_ids` | `list(string)` | Subnets for ECS tasks (typically private) |
| `task_exec_secret_arns` | `list(string)` | Secret ARNs for task execution role |
| `tasks_iam_role_policies` | `map(string)` | IAM policies for task role |
| `desired_count` | `number` | Number of tasks to run |
| `enable_execute_command` | `bool` | Enable ECS Exec for debugging |

### Application Load Balancer Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_alb` | `bool` | `true` | Create ALB or use existing |
| `alb_target_group_arn` | `string` | `""` | Existing target group ARN |
| `alb_security_group_id` | `string` | `""` | Existing ALB security group ID |

The `alb` object configures the ALB:

| Property | Type | Description |
|----------|------|-------------|
| `subnet_ids` | `list(string)` | Subnets for ALB (typically public) |
| `enable_deletion_protection` | `bool` | Prevent accidental deletion |
| `access_logs` | `object` | S3 bucket for access logs |
| `security_group_ingress_rules` | `map` | Custom ingress rules |

### Certificate and DNS Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_certificate` | `bool` | `true` | Create ACM certificate |
| `certificate_arn` | `string` | `""` | Existing certificate ARN |
| `certificate_domain_name` | `string` | `""` | Domain for certificate |
| `validate_certificate` | `bool` | `true` | Validate via Route53 DNS |
| `create_route53_records` | `bool` | `true` | Create Route53 A/AAAA records |
| `route53_zone_id` | `string` | `""` | Route53 zone ID |
| `route53_record_name` | `string` | `null` | DNS record name |

### EFS Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `enable_efs` | `bool` | `false` | Create EFS filesystem |
| `efs` | `object` | `{}` | EFS settings including mount targets |

## Outputs

| Output | Description |
|--------|-------------|
| `url` | URL of the Atlantis instance |
| `alb` | ALB and all associated outputs (ARN, DNS name, security groups) |
| `cluster` | ECS cluster and all associated outputs (ARN, name) |
| `service` | ECS service and all associated outputs (ARN, task definition) |
| `efs` | EFS and all associated outputs (file system ID, DNS name) |

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
    cpu    = 1024
    memory = 2048

    environment = [
      {
        name  = "ATLANTIS_GH_USER"
        value = "atlantis-bot"
      },
      {
        name  = "ATLANTIS_REPO_ALLOWLIST"
        value = "github.com/myorg/*"
      },
      {
        name  = "ATLANTIS_DEFAULT_TF_VERSION"
        value = "1.6.0"
      },
    ]

    secrets = [
      {
        name      = "ATLANTIS_GH_TOKEN"
        valueFrom = aws_secretsmanager_secret.github_token.arn
      },
      {
        name      = "ATLANTIS_GH_WEBHOOK_SECRET"
        valueFrom = aws_secretsmanager_secret.webhook_secret.arn
      },
    ]
  }

  # ECS service configuration
  service = {
    subnet_ids = module.vpc.private_subnets

    task_exec_secret_arns = [
      aws_secretsmanager_secret.github_token.arn,
      aws_secretsmanager_secret.webhook_secret.arn,
    ]

    # IAM policies for Terraform operations
    tasks_iam_role_policies = {
      AdministratorAccess = "arn:aws:iam::aws:policy/AdministratorAccess"
    }
  }

  # ALB configuration
  alb = {
    subnet_ids                 = module.vpc.public_subnets
    enable_deletion_protection = false
  }

  # DNS and certificate
  certificate_domain_name = "atlantis.example.com"
  route53_zone_id         = data.aws_route53_zone.this.id

  # Enable EFS for persistent storage
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

# GitHub webhooks
module "github_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/github-repository-webhook"

  repositories   = ["myorg/infrastructure", "myorg/terraform-modules"]
  webhook_url    = "${module.atlantis.url}/events"
  webhook_secret = random_password.webhook_secret.result
}

# Secrets
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

### Using Existing ECS Cluster and ALB

```hcl
module "atlantis" {
  source  = "terraform-aws-modules/atlantis/aws"
  version = "~> 5.1"

  name   = "atlantis"
  vpc_id = module.vpc.vpc_id

  # Use existing ECS cluster
  create_cluster = false
  cluster_arn    = aws_ecs_cluster.existing.arn

  # Use existing ALB
  create_alb            = false
  alb_target_group_arn  = aws_lb_target_group.atlantis.arn
  alb_security_group_id = aws_security_group.alb.id

  # Use existing certificate
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

### GitLab Integration

```hcl
module "atlantis" {
  source  = "terraform-aws-modules/atlantis/aws"
  version = "~> 5.1"

  name   = "atlantis"
  vpc_id = module.vpc.vpc_id

  atlantis = {
    environment = [
      { name = "ATLANTIS_GITLAB_USER", value = "atlantis-bot" },
      { name = "ATLANTIS_GITLAB_HOSTNAME", value = "gitlab.example.com" },
      { name = "ATLANTIS_REPO_ALLOWLIST", value = "gitlab.example.com/mygroup/*" },
    ]
    secrets = [
      { name = "ATLANTIS_GITLAB_TOKEN", valueFrom = aws_secretsmanager_secret.gitlab_token.arn },
      { name = "ATLANTIS_GITLAB_WEBHOOK_SECRET", valueFrom = aws_secretsmanager_secret.webhook_secret.arn },
    ]
  }

  service = {
    subnet_ids            = module.vpc.private_subnets
    task_exec_secret_arns = [
      aws_secretsmanager_secret.gitlab_token.arn,
      aws_secretsmanager_secret.webhook_secret.arn,
    ]
    tasks_iam_role_policies = {
      AdministratorAccess = "arn:aws:iam::aws:policy/AdministratorAccess"
    }
  }

  alb = {
    subnet_ids = module.vpc.public_subnets
  }

  certificate_domain_name = "atlantis.example.com"
  route53_zone_id         = data.aws_route53_zone.this.id

  tags = {
    Environment = "production"
    GitProvider = "gitlab"
  }
}

module "gitlab_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/gitlab-repository-webhook"

  repositories   = ["mygroup/infrastructure", "mygroup/terraform-modules"]
  webhook_url    = "${module.atlantis.url}/events"
  webhook_secret = random_password.webhook_secret.result
}

provider "gitlab" {
  token    = var.gitlab_token
  base_url = "https://gitlab.example.com/api/v4/"
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
    cpu    = 2048
    memory = 4096

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
    subnet_ids            = module.vpc.private_subnets
    task_exec_secret_arns = [
      aws_secretsmanager_secret.github_token.arn,
      aws_secretsmanager_secret.webhook_secret.arn,
    ]

    # Cross-account assume role permissions
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

1. **Use Private Subnets for ECS**: Deploy Atlantis tasks in private subnets with NAT gateway for security
2. **Enable EFS for Production**: Use EFS persistent storage to prevent plan file loss during container restarts
3. **Deploy Multi-AZ**: Configure ALB across multiple AZs for high availability
4. **Size Resources Appropriately**: Start with 1024 CPU and 2048 MB memory; scale for concurrent plans

### Security

5. **Use Secrets Manager**: Store GitHub/GitLab tokens and webhook secrets in Secrets Manager, not environment variables
6. **Configure Repository Allowlist**: Always set `ATLANTIS_REPO_ALLOWLIST` to restrict unauthorized repository access
7. **Use HTTPS Only**: Always use ACM certificates; never expose Atlantis over HTTP
8. **Implement Webhook Secrets**: Always configure webhook secrets to validate incoming requests
9. **Restrict ALB Ingress**: Limit ALB ingress to specific IP ranges when possible
10. **Scope IAM Permissions**: Apply least-privilege to task role; avoid AdministratorAccess in production

### Terraform State

11. **Grant S3 State Access**: Provide task role with read/write access to S3 state buckets
12. **Configure DynamoDB Lock Access**: Grant permissions to DynamoDB lock tables
13. **Enable KMS Access**: If using encrypted state, grant decrypt/encrypt permissions

### Configuration

14. **Set Default Terraform Version**: Configure `ATLANTIS_DEFAULT_TF_VERSION` for consistency
15. **Configure Apply Requirements**: Require pull request approvals before allowing applies
16. **Enable Parallel Execution**: Set `ATLANTIS_PARALLEL_PLAN` and `ATLANTIS_PARALLEL_APPLY` for faster processing

### Operations

17. **Run Multiple Tasks for HA**: Configure desired_count of 2+ for high availability
18. **Enable CloudWatch Logs**: Monitor container logs for debugging and auditing
19. **Implement Comprehensive Tagging**: Apply tags for environment, cost center, and owner
20. **Test in Non-Production First**: Validate upgrades and configuration changes before production

## Additional Resources

- **Atlantis Documentation**: https://www.runatlantis.io/docs/
- **Module GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-atlantis
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/atlantis/aws/latest
- **Atlantis Server Configuration**: https://www.runatlantis.io/docs/server-configuration.html
- **Repository Configuration**: https://www.runatlantis.io/docs/repo-level-atlantis-yaml.html
- **Custom Workflows**: https://www.runatlantis.io/docs/custom-workflows.html
- **Security Best Practices**: https://www.runatlantis.io/docs/security.html
- **AWS ECS Best Practices**: https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/

## Notes for AI Agents

### Module Selection

- **Use this module** for collaborative, pull request-based Terraform workflows with automated planning
- **Use AWS CodePipeline** for fully automated CI/CD without pull request interaction
- **Use Terraform Cloud/Enterprise** for HashiCorp-managed solution with similar capabilities

### Architecture Patterns

- **Small teams (1-10)**: Single instance, 1024 CPU, 2048 MB, EFS enabled, private subnets
- **Medium teams (10-50)**: 2048 CPU, 4096 MB, 2+ tasks, multi-AZ, separate instances per environment
- **Large organizations (50+)**: Multiple instances per team, custom workflows, policy checking
- **Multi-account**: Atlantis in central account with cross-account IAM roles

### Required Environment Variables

**GitHub**:
- `ATLANTIS_GH_USER`: GitHub username for Atlantis bot
- `ATLANTIS_GH_TOKEN`: GitHub personal access token (via secrets)
- `ATLANTIS_GH_WEBHOOK_SECRET`: Webhook secret (via secrets)
- `ATLANTIS_REPO_ALLOWLIST`: Allowed repositories pattern

**GitLab**:
- `ATLANTIS_GITLAB_USER`: GitLab username
- `ATLANTIS_GITLAB_TOKEN`: GitLab access token (via secrets)
- `ATLANTIS_GITLAB_WEBHOOK_SECRET`: Webhook secret (via secrets)
- `ATLANTIS_GITLAB_HOSTNAME`: GitLab hostname (for self-hosted)
- `ATLANTIS_REPO_ALLOWLIST`: Allowed repositories pattern

### IAM Permissions

**Task Execution Role** (automatic):
- SecretsManager:GetSecretValue for configured secrets
- CloudWatch Logs permissions
- ECR image pull (if using custom image)

**Task Role** (configure via `tasks_iam_role_policies`):
- S3 read/write on state buckets
- DynamoDB read/write on lock tables
- KMS decrypt/encrypt for encrypted state
- sts:AssumeRole for cross-account access
- Terraform resource permissions (varies by infrastructure)

### Cost Estimation

- **Fargate**: ~$30-50/month for single task (1024 CPU, 2048 MB); double for HA
- **ALB**: ~$20-30/month base cost plus LCU charges
- **EFS**: ~$0.30/GB-month (typically $1-5/month for plan storage)
- **Total**: $50-100/month basic, $100-200/month HA production

### Troubleshooting

- **Webhooks not received**: Check ALB security group, Route53 DNS, GitHub/GitLab webhook delivery logs
- **Plans failing with auth**: Verify GitHub token permissions, check Secrets Manager access
- **Apply stuck**: Check apply requirements, verify PR approval, check plan locks
- **Tasks restarting**: Check CloudWatch Logs, memory limits, health checks, IAM permissions
- **State access errors**: Verify S3 permissions, bucket policy, KMS key policy
