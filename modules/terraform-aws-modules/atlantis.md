---
module_name: terraform-aws-atlantis
keywords: [atlantis, terraform-automation, pull-request-automation, infrastructure-as-code, ci-cd, ecs, fargate, alb, application-load-balancer, github-integration, gitlab-integration, bitbucket-integration, webhook, terraform-plan, terraform-apply, collaboration, code-review, efs, persistent-storage, secrets-manager, iam-roles, container, docker, devops, gitops]
---

# AWS Atlantis Terraform Module

## Module Information

- **Source**: `terraform-aws-modules/atlantis/aws`
- **Version**: 4.4.0
- **Terraform**: >= 1.0
- **AWS Provider**: >= 5.0
- **License**: Apache-2.0

## Description

Terraform module that deploys Atlantis on AWS using Amazon ECS Fargate for automated Terraform workflow management through pull requests. Atlantis is an open-source application that enables teams to collaborate on infrastructure changes by automatically running Terraform plan and apply operations directly from pull requests in GitHub, GitLab, or Bitbucket Cloud. This module creates a complete infrastructure stack including an Application Load Balancer for HTTPS termination, ECS Fargate cluster and service for running Atlantis containers, optional EFS storage for persistent Terraform plan files, and comprehensive IAM roles and policies for secure AWS resource access.

The module simplifies Atlantis deployment on AWS by handling all infrastructure provisioning including VPC integration, security groups, load balancer listeners, SSL/TLS certificates, container definitions, task execution roles, and webhook configuration. It supports multiple deployment patterns from complete infrastructure provisioning to integration with existing AWS resources. The module manages Atlantis configuration through environment variables, supports secrets management via AWS Secrets Manager for sensitive credentials like GitHub tokens and webhook secrets, and provides flexible customization of compute resources, networking, and storage options.

Atlantis deployed through this module enables teams to implement GitOps workflows where infrastructure changes are proposed, reviewed, and approved through standard pull request processes. The application automatically generates Terraform plans when pull requests are opened, maintains plan locks to prevent concurrent modifications, and executes applies when pull requests are merged or explicitly approved. This creates a centralized, auditable, and collaborative approach to infrastructure management that integrates seamlessly with existing development workflows and code review processes.

## Key Features

- **ECS Fargate Deployment**: Serverless container deployment for Atlantis with automatic scaling and no server management
- **Application Load Balancer**: HTTPS load balancer with SSL/TLS termination and health checks for Atlantis service
- **Multi-Git Provider Support**: Integration with GitHub, GitLab, and Bitbucket Cloud through webhook configuration
- **EFS Persistent Storage**: Optional Amazon EFS file system for persistent Terraform plan storage across container restarts
- **Secrets Management**: AWS Secrets Manager integration for storing GitHub/GitLab tokens, webhook secrets, and sensitive credentials
- **IAM Role Management**: Automated creation of task execution roles and task roles with appropriate permissions
- **VPC Integration**: Deployment into specified VPC subnets with configurable public or private subnet placement
- **ACM Certificate Support**: Integration with AWS Certificate Manager for HTTPS certificates on custom domains
- **Route 53 Integration**: Optional Route 53 alias record creation for custom domain names
- **Security Groups**: Managed security groups for ALB and ECS service with configurable ingress/egress rules
- **Container Customization**: Configurable Atlantis container image, version, CPU, memory, and environment variables
- **GitHub Webhook Submodule**: Automated GitHub repository webhook creation for multiple repositories
- **GitLab Webhook Submodule**: Automated GitLab project webhook configuration for multiple repositories
- **Repository Allowlist**: Configure allowed repositories that Atlantis can interact with for security
- **Custom Atlantis Configuration**: Support for atlantis.yaml, repo configuration, and custom workflows
- **Auto-Planning**: Automatic Terraform plan generation on pull request creation and updates
- **Plan Locking**: Prevents concurrent infrastructure modifications through project locking mechanism
- **CloudWatch Logs Integration**: Container logs sent to CloudWatch Logs for monitoring and debugging
- **Flexible Tagging**: Comprehensive resource tagging for cost allocation and resource management
- **Conditional Resource Creation**: Control creation of individual components (ALB, ECS, EFS) through feature flags

## Use Cases

- **Pull Request-Based Infrastructure Changes**: Automate Terraform workflows where infrastructure changes are proposed, reviewed, and applied through Git pull requests
- **Collaborative Infrastructure Management**: Enable multiple team members to safely propose and review infrastructure changes with visibility and approval workflows
- **GitOps Implementation**: Implement GitOps practices where Git becomes the single source of truth for infrastructure state and changes
- **Centralized Terraform Execution**: Provide consistent Terraform execution environment with standardized versions, providers, and configurations
- **Multi-Repository Infrastructure**: Manage Terraform code across multiple repositories with centralized execution and state management
- **Infrastructure Code Review**: Facilitate code review of Terraform changes with automatic plan generation showing exact infrastructure impacts
- **Compliance and Auditability**: Create audit trails of infrastructure changes through Git history and pull request approvals
- **Development Environment Management**: Allow developers to safely test infrastructure changes in isolated environments before production
- **Automated Testing**: Integrate infrastructure testing by running Terraform plan on every pull request to validate syntax and logic
- **State Management**: Centralize Terraform state management with consistent backend configuration and locking

## Submodules

### github-repository-webhook

Creates GitHub repository webhooks for Atlantis integration, enabling automatic webhook configuration across multiple repositories.

**Purpose**: Automate GitHub webhook creation to trigger Atlantis on pull request events (open, update, comment) for Terraform automation workflows.

**Key Features**:
- Bulk webhook creation across multiple GitHub repositories
- Configurable webhook URL pointing to Atlantis endpoint
- Webhook secret support for secure event verification
- Conditional webhook creation with feature flag
- Supports GitHub API v3 authentication
- Automatic cleanup when repositories are removed

**Variables** (key ones):
- `create` (bool): Whether to create webhooks (default: true)
- `repositories` (list(string)): List of repository names to add webhooks (e.g., ["org/repo1", "org/repo2"])
- `webhook_url` (string): Atlantis webhook URL (e.g., "https://atlantis.example.com/events")
- `webhook_secret` (string): Optional webhook secret for request validation (default: "")

**Outputs**:
- `repository_webhook_urls`: Map of repository names to their webhook URLs

**Usage Example**:
```hcl
module "atlantis_github_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/github-repository-webhook"

  repositories = [
    "myorg/infrastructure-prod",
    "myorg/infrastructure-staging",
    "myorg/infrastructure-dev"
  ]

  webhook_url    = "https://atlantis.example.com/events"
  webhook_secret = random_password.webhook_secret.result
}

resource "random_password" "webhook_secret" {
  length  = 32
  special = true
}

# GitHub provider configuration required
provider "github" {
  token = var.github_token
  owner = "myorg"
}
```

### gitlab-repository-webhook

Creates GitLab project webhooks for Atlantis integration, enabling automatic webhook configuration across multiple GitLab projects.

**Purpose**: Automate GitLab webhook creation to trigger Atlantis on merge request events (open, update, comment) for Terraform automation workflows.

**Key Features**:
- Bulk webhook creation across multiple GitLab projects
- Configurable webhook URL pointing to Atlantis endpoint
- Webhook token support for secure event verification
- Conditional webhook creation with feature flag
- Supports GitLab API v4 authentication
- Merge request event filtering

**Variables** (key ones):
- `create` (bool): Whether to create webhooks (default: true)
- `repositories` (list(string)): List of project names/IDs to add webhooks (e.g., ["group/project1", "group/project2"])
- `webhook_url` (string): Atlantis webhook URL (e.g., "https://atlantis.example.com/events")
- `webhook_secret` (string): Optional webhook secret for request validation (default: "")

**Outputs**:
- `repository_webhook_urls`: Map of project names to their webhook URLs

**Usage Example**:
```hcl
module "atlantis_gitlab_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/gitlab-repository-webhook"

  repositories = [
    "infrastructure/prod",
    "infrastructure/staging",
    "infrastructure/dev"
  ]

  webhook_url    = "https://atlantis.example.com/events"
  webhook_secret = random_password.webhook_secret.result
}

resource "random_password" "webhook_secret" {
  length  = 32
  special = true
}

# GitLab provider configuration required
provider "gitlab" {
  token = var.gitlab_token
}
```

## Variables

### Core Configuration
- `create` (bool): Controls if resources should be created (default: true)
- `tags` (map(string)): Map of tags to add to all resources (default: {})
- `name` (string): Common name to use on all resources (default: "atlantis")

### Atlantis Container Configuration
- `atlantis` (any): Map of values passed to Atlantis container definition (default: {})
  - `environment`: List of environment variables for Atlantis configuration
  - `image`: Docker image for Atlantis (default: uses latest official image)
  - `cpu`: CPU units for Atlantis task (default: 512)
  - `memory`: Memory in MiB for Atlantis task (default: 1024)
  - `command`: Override default Atlantis command
  - `entrypoint`: Override default entrypoint
- `atlantis_gid` (number): GID of the atlantis user (default: 1000)
- `atlantis_uid` (number): UID of the atlantis user (default: 100)

### Networking
- `vpc_id` (string): ID of the VPC where resources will be provisioned (required)
- `service_subnets` (list(string)): Subnets for ECS service deployment
- `alb_subnets` (list(string)): Subnets for Application Load Balancer
- `certificate_arn` (string): ARN of ACM certificate for HTTPS

### Application Load Balancer
- `alb` (any): Map of ALB configuration options
  - `security_group_ingress_rules`: Custom ingress rules for ALB
  - `security_group_egress_rules`: Custom egress rules for ALB
  - `access_logs`: S3 bucket configuration for ALB access logs
  - `listener_port`: HTTPS listener port (default: 443)
  - `listener_protocol`: Listener protocol (default: "HTTPS")

### ECS Configuration
- `ecs_cluster` (any): ECS cluster configuration options
- `ecs_service` (any): ECS service configuration options
  - `desired_count`: Number of Atlantis tasks to run (default: 1)
  - `deployment_configuration`: Deployment settings
  - `enable_execute_command`: Enable ECS Exec for debugging

### EFS Storage
- `enable_efs` (bool): Create EFS file system for persistent storage (default: false)
- `efs` (any): EFS configuration options
  - `encrypted`: Enable encryption at rest
  - `kms_key_id`: KMS key for encryption
  - `throughput_mode`: Throughput mode (bursting or provisioned)

### Secrets and IAM
- `task_execution_secrets` (list(any)): Secrets to pass to task execution role
- `task_execution_policies` (map(string)): Additional IAM policies for task execution role
- `task_role_policies` (map(string)): Additional IAM policies for task role

### Route 53
- `route53_zone_id` (string): Route 53 hosted zone ID for creating DNS records
- `route53_record_name` (string): Route 53 record name for Atlantis

## Outputs

### Service Information
- `url`: URL of Atlantis service (HTTPS endpoint)

### Infrastructure Components
- `alb`: Application Load Balancer created and all associated outputs
  - Includes ALB ARN, DNS name, security group IDs, listener ARNs, target group ARNs
- `ecs_cluster`: ECS cluster created and all associated outputs
  - Includes cluster ARN, cluster name, cluster ID
- `ecs_service`: ECS service created and all associated outputs
  - Includes service ARN, service name, task definition ARN, security group IDs
- `efs`: EFS created and all associated outputs (if enabled)
  - Includes file system ID, file system ARN, DNS name, mount target information

## Usage Examples

### Basic Atlantis Deployment with GitHub

```hcl
module "atlantis" {
  source  = "terraform-aws-modules/atlantis/aws"
  version = "~> 4.4"

  name = "atlantis"

  # VPC Configuration
  vpc_id          = module.vpc.vpc_id
  service_subnets = module.vpc.private_subnets
  alb_subnets     = module.vpc.public_subnets

  # SSL Certificate
  certificate_arn = aws_acm_certificate.atlantis.arn

  # Atlantis Configuration
  atlantis = {
    environment = [
      {
        name  = "ATLANTIS_GH_USER"
        value = "atlantis-bot"
      },
      {
        name  = "ATLANTIS_GH_TOKEN"
        value = var.github_token
      },
      {
        name  = "ATLANTIS_GH_WEBHOOK_SECRET"
        value = random_password.webhook_secret.result
      },
      {
        name  = "ATLANTIS_REPO_ALLOWLIST"
        value = "github.com/myorg/*"
      }
    ]
  }

  tags = {
    Environment = "production"
  }
}

resource "random_password" "webhook_secret" {
  length  = 32
  special = true
}
```

### Complete Atlantis with EFS and Secrets Manager

```hcl
module "atlantis" {
  source  = "terraform-aws-modules/atlantis/aws"
  version = "~> 4.4"

  name = "atlantis-prod"

  # VPC Configuration
  vpc_id          = module.vpc.vpc_id
  service_subnets = module.vpc.private_subnets
  alb_subnets     = module.vpc.public_subnets

  # SSL Certificate
  certificate_arn = aws_acm_certificate.atlantis.arn

  # Route 53 Custom Domain
  route53_zone_id    = data.aws_route53_zone.main.zone_id
  route53_record_name = "atlantis"

  # Enable EFS for persistent storage
  enable_efs = true
  efs = {
    encrypted = true
    kms_key_id = aws_kms_key.efs.id
    throughput_mode = "bursting"
  }

  # Atlantis Container Configuration
  atlantis = {
    cpu    = 1024
    memory = 2048
    image  = "ghcr.io/runatlantis/atlantis:v0.25.0"

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
        name  = "ATLANTIS_LOG_LEVEL"
        value = "info"
      },
      {
        name  = "ATLANTIS_DEFAULT_TF_VERSION"
        value = "1.6.0"
      }
    ]
  }

  # Secrets from Secrets Manager
  task_execution_secrets = [
    {
      name      = "ATLANTIS_GH_TOKEN"
      valueFrom = aws_secretsmanager_secret.github_token.arn
    },
    {
      name      = "ATLANTIS_GH_WEBHOOK_SECRET"
      valueFrom = aws_secretsmanager_secret.webhook_secret.arn
    }
  ]

  # Additional IAM Policies for Terraform State Access
  task_role_policies = {
    s3_state_access = aws_iam_policy.terraform_state_access.arn
    dynamodb_lock   = aws_iam_policy.terraform_lock_access.arn
  }

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Secrets Manager Resources
resource "aws_secretsmanager_secret" "github_token" {
  name = "atlantis/github-token"
}

resource "aws_secretsmanager_secret" "webhook_secret" {
  name = "atlantis/webhook-secret"
}

# GitHub Webhooks
module "github_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/github-repository-webhook"

  repositories = [
    "myorg/infrastructure",
    "myorg/terraform-modules"
  ]

  webhook_url    = module.atlantis.url
  webhook_secret = aws_secretsmanager_secret_version.webhook_secret.secret_string
}
```

### Atlantis with GitLab Integration

```hcl
module "atlantis_gitlab" {
  source  = "terraform-aws-modules/atlantis/aws"
  version = "~> 4.4"

  name = "atlantis-gitlab"

  # VPC Configuration
  vpc_id          = module.vpc.vpc_id
  service_subnets = module.vpc.private_subnets
  alb_subnets     = module.vpc.public_subnets

  # SSL Certificate
  certificate_arn = aws_acm_certificate.atlantis.arn

  # Atlantis Configuration for GitLab
  atlantis = {
    environment = [
      {
        name  = "ATLANTIS_GITLAB_USER"
        value = "atlantis-bot"
      },
      {
        name  = "ATLANTIS_GITLAB_TOKEN"
        value = var.gitlab_token
      },
      {
        name  = "ATLANTIS_GITLAB_WEBHOOK_SECRET"
        value = random_password.webhook_secret.result
      },
      {
        name  = "ATLANTIS_GITLAB_HOSTNAME"
        value = "gitlab.example.com"
      },
      {
        name  = "ATLANTIS_REPO_ALLOWLIST"
        value = "gitlab.example.com/mygroup/*"
      }
    ]
  }

  tags = {
    Environment = "production"
    GitProvider = "gitlab"
  }
}

# GitLab Webhooks
module "gitlab_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/gitlab-repository-webhook"

  repositories = [
    "mygroup/infrastructure",
    "mygroup/terraform-modules"
  ]

  webhook_url    = module.atlantis_gitlab.url
  webhook_secret = random_password.webhook_secret.result
}

provider "gitlab" {
  token    = var.gitlab_token
  base_url = "https://gitlab.example.com/api/v4/"
}
```

### Atlantis with Custom Workflows

```hcl
module "atlantis_custom" {
  source  = "terraform-aws-modules/atlantis/aws"
  version = "~> 4.4"

  name = "atlantis-custom"

  # VPC Configuration
  vpc_id          = module.vpc.vpc_id
  service_subnets = module.vpc.private_subnets
  alb_subnets     = module.vpc.public_subnets

  # SSL Certificate
  certificate_arn = aws_acm_certificate.atlantis.arn

  # Atlantis Container with Custom Config
  atlantis = {
    cpu    = 1024
    memory = 2048

    environment = [
      {
        name  = "ATLANTIS_GH_USER"
        value = "atlantis-bot"
      },
      {
        name  = "ATLANTIS_GH_TOKEN"
        value = var.github_token
      },
      {
        name  = "ATLANTIS_GH_WEBHOOK_SECRET"
        value = random_password.webhook_secret.result
      },
      {
        name  = "ATLANTIS_REPO_ALLOWLIST"
        value = "github.com/myorg/*"
      },
      # Custom Atlantis Configuration
      {
        name  = "ATLANTIS_REPO_CONFIG_JSON"
        value = jsonencode({
          repos = [
            {
              id                     = "/.*/",
              branch                 = "/.*/",
              apply_requirements     = ["approved", "mergeable"],
              workflow               = "custom",
              allowed_overrides      = ["apply_requirements"],
              allow_custom_workflows = true
            }
          ]
          workflows = {
            custom = {
              plan = {
                steps = [
                  "init",
                  "plan"
                ]
              }
              apply = {
                steps = [
                  "apply"
                ]
              }
            }
          }
        })
      }
    ]
  }

  tags = {
    Environment = "production"
    Workflow    = "custom"
  }
}
```

### Atlantis with Multiple Repositories and Advanced IAM

```hcl
module "atlantis_multi_repo" {
  source  = "terraform-aws-modules/atlantis/aws"
  version = "~> 4.4"

  name = "atlantis-multi"

  # VPC Configuration
  vpc_id          = module.vpc.vpc_id
  service_subnets = module.vpc.private_subnets
  alb_subnets     = module.vpc.public_subnets

  # SSL Certificate
  certificate_arn = aws_acm_certificate.atlantis.arn

  # Enable EFS for plan storage
  enable_efs = true

  # Atlantis Configuration
  atlantis = {
    cpu    = 2048
    memory = 4096

    environment = [
      {
        name  = "ATLANTIS_GH_USER"
        value = "atlantis-bot"
      },
      {
        name  = "ATLANTIS_REPO_ALLOWLIST"
        value = "github.com/myorg/infra-*,github.com/myorg/terraform-*"
      },
      {
        name  = "ATLANTIS_PARALLEL_PLAN"
        value = "true"
      },
      {
        name  = "ATLANTIS_PARALLEL_APPLY"
        value = "true"
      }
    ]
  }

  # Secrets from Secrets Manager
  task_execution_secrets = [
    {
      name      = "ATLANTIS_GH_TOKEN"
      valueFrom = aws_secretsmanager_secret.github_token.arn
    },
    {
      name      = "ATLANTIS_GH_WEBHOOK_SECRET"
      valueFrom = aws_secretsmanager_secret.webhook_secret.arn
    }
  ]

  # IAM Policies for Multi-Account Terraform State Access
  task_role_policies = {
    # Access to Terraform state buckets
    state_access = aws_iam_policy.terraform_state.arn
    # Assume roles in other accounts
    cross_account = aws_iam_policy.assume_terraform_roles.arn
    # DynamoDB lock table access
    lock_table = aws_iam_policy.dynamodb_lock.arn
    # KMS key access for state encryption
    kms_access = aws_iam_policy.state_kms.arn
  }

  tags = {
    Environment = "production"
    Scope       = "multi-account"
  }
}

# IAM Policy for Cross-Account Access
resource "aws_iam_policy" "assume_terraform_roles" {
  name = "atlantis-assume-terraform-roles"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Resource = [
          "arn:aws:iam::111111111111:role/terraform",
          "arn:aws:iam::222222222222:role/terraform",
          "arn:aws:iam::333333333333:role/terraform"
        ]
      }
    ]
  })
}

# GitHub Webhooks for Multiple Repositories
module "github_webhooks" {
  source = "terraform-aws-modules/atlantis/aws//modules/github-repository-webhook"

  repositories = [
    "myorg/infra-production",
    "myorg/infra-staging",
    "myorg/infra-development",
    "myorg/terraform-modules",
    "myorg/terraform-policies"
  ]

  webhook_url    = module.atlantis_multi_repo.url
  webhook_secret = aws_secretsmanager_secret_version.webhook_secret.secret_string
}
```

### Atlantis with ALB Access Logs and Enhanced Monitoring

```hcl
module "atlantis_monitored" {
  source  = "terraform-aws-modules/atlantis/aws"
  version = "~> 4.4"

  name = "atlantis-monitored"

  # VPC Configuration
  vpc_id          = module.vpc.vpc_id
  service_subnets = module.vpc.private_subnets
  alb_subnets     = module.vpc.public_subnets

  # SSL Certificate
  certificate_arn = aws_acm_certificate.atlantis.arn

  # ALB Configuration with Access Logs
  alb = {
    access_logs = {
      bucket  = aws_s3_bucket.alb_logs.id
      prefix  = "atlantis"
      enabled = true
    }
    security_group_ingress_rules = {
      https = {
        from_port   = 443
        to_port     = 443
        ip_protocol = "tcp"
        cidr_ipv4   = "0.0.0.0/0"
        description = "HTTPS access"
      }
    }
  }

  # ECS Service Configuration
  ecs_service = {
    desired_count = 2  # Run 2 tasks for availability
    enable_execute_command = true  # Enable ECS Exec for debugging

    deployment_configuration = {
      minimum_healthy_percent = 50
      maximum_percent         = 200
    }
  }

  # Atlantis Configuration
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
        name  = "ATLANTIS_LOG_LEVEL"
        value = "debug"
      },
      {
        name  = "ATLANTIS_WRITE_GIT_CREDS"
        value = "true"
      }
    ]
  }

  # Secrets
  task_execution_secrets = [
    {
      name      = "ATLANTIS_GH_TOKEN"
      valueFrom = aws_secretsmanager_secret.github_token.arn
    },
    {
      name      = "ATLANTIS_GH_WEBHOOK_SECRET"
      valueFrom = aws_secretsmanager_secret.webhook_secret.arn
    }
  ]

  tags = {
    Environment = "production"
    Monitoring  = "enhanced"
  }
}

# S3 Bucket for ALB Access Logs
resource "aws_s3_bucket" "alb_logs" {
  bucket = "atlantis-alb-logs-${data.aws_caller_identity.current.account_id}"
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "atlantis_cpu_high" {
  alarm_name          = "atlantis-cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors Atlantis CPU utilization"

  dimensions = {
    ClusterName = module.atlantis_monitored.ecs_cluster.cluster_name
    ServiceName = module.atlantis_monitored.ecs_service.name
  }
}
```

## Best Practices

### Deployment and Architecture

1. **Use Private Subnets for ECS Service**: Deploy Atlantis ECS tasks in private subnets with NAT gateway for internet access to enhance security while maintaining GitHub/GitLab connectivity.
2. **Enable EFS for Production**: Always enable EFS persistent storage for production deployments to prevent plan file loss during container restarts or deployments.
3. **Deploy in Multiple Availability Zones**: Configure ALB across multiple AZs and use multi-AZ EFS for high availability and fault tolerance.
4. **Size Resources Appropriately**: Start with 1024 CPU and 2048 MB memory for moderate usage; scale to 2048 CPU and 4096 MB for multiple concurrent plans.
5. **Use Custom Domain with Route 53**: Configure custom domain names with Route 53 for professional endpoints and easier webhook configuration.
6. **Enable ALB Access Logs**: Store ALB access logs in S3 for security auditing, troubleshooting, and compliance requirements.

### Security and Access Control

7. **Use Secrets Manager for Credentials**: Store GitHub tokens, GitLab tokens, and webhook secrets in AWS Secrets Manager rather than plain environment variables.
8. **Configure Repository Allowlist**: Set strict ATLANTIS_REPO_ALLOWLIST to prevent unauthorized repository access; use specific patterns like "github.com/myorg/infra-*".
9. **Enable SSL/TLS with ACM**: Use AWS Certificate Manager certificates for HTTPS endpoints; never expose Atlantis over HTTP in production.
10. **Implement Webhook Secrets**: Always configure webhook secrets to validate incoming requests and prevent unauthorized webhook triggers.
11. **Restrict ALB Security Group**: Limit ALB ingress to specific IP ranges (office IPs, VPN) rather than 0.0.0.0/0 when possible for enhanced security.
12. **Use IAM Roles for AWS Access**: Configure task roles with least-privilege permissions for Terraform state access rather than embedding AWS credentials.
13. **Enable ECS Exec Conditionally**: Enable ECS Exec only in non-production environments or temporarily for debugging; disable in production for security.
14. **Rotate Secrets Regularly**: Implement rotation schedules for GitHub tokens, webhook secrets, and other credentials using Secrets Manager rotation.

### Terraform State Management

15. **Grant S3 State Access**: Provide task role with read/write access to S3 buckets containing Terraform state files for all managed repositories.
16. **Configure DynamoDB Lock Access**: Grant permissions to DynamoDB lock tables to prevent concurrent Terraform executions and state corruption.
17. **Enable KMS Access for Encrypted State**: If using KMS-encrypted state buckets, grant task role decrypt/encrypt permissions for state file access.
18. **Use Backend Configuration**: Standardize backend configuration across repositories to ensure consistent state management and locking behavior.
19. **Implement State Bucket Versioning**: Enable S3 versioning on state buckets to allow state recovery and rollback if needed.

### Atlantis Configuration

20. **Set Default Terraform Version**: Configure ATLANTIS_DEFAULT_TF_VERSION to match your primary Terraform version for consistency across projects.
21. **Configure Apply Requirements**: Use atlantis.yaml or server-side config to require pull request approvals before allowing applies for safety.
22. **Enable Parallel Execution**: Set ATLANTIS_PARALLEL_PLAN and ATLANTIS_PARALLEL_APPLY for faster processing of multiple projects or workspaces.
23. **Implement Custom Workflows**: Define custom workflows in atlantis.yaml for advanced scenarios like policy checks, pre-plan hooks, or custom validation.
24. **Use Project-Level Configuration**: Configure project-specific settings in atlantis.yaml for different Terraform versions, workflows, or apply requirements.
25. **Configure Auto-Planning**: Enable auto-planning (default behavior) to automatically run plans when pull requests are opened or updated.
26. **Set Appropriate Log Levels**: Use "info" for production, "debug" for troubleshooting; avoid "debug" in production to reduce log volume.

### High Availability and Reliability

27. **Run Multiple ECS Tasks**: Configure desired_count of 2 or more with ALB for high availability; use minimum_healthy_percent of 50 for zero-downtime deployments.
28. **Configure Health Checks**: Ensure ALB health checks are properly configured to route traffic only to healthy Atlantis containers.
29. **Use Deployment Circuit Breakers**: Enable ECS deployment circuit breakers to automatically roll back failed deployments.
30. **Monitor ECS Service Metrics**: Set up CloudWatch alarms for CPU utilization, memory utilization, and task count to detect issues early.
31. **Implement Graceful Shutdown**: Configure appropriate stop_timeout in ECS task definition to allow Atlantis to complete in-flight operations.
32. **Test Disaster Recovery**: Regularly test EFS restore procedures and validate Atlantis can recover plan files after failures.

### Operational Excellence

33. **Use Infrastructure as Code**: Manage all Atlantis infrastructure through Terraform for version control, peer review, and reproducibility.
34. **Implement Comprehensive Tagging**: Apply tags for environment, application, cost center, and owner to all resources for tracking and cost allocation.
35. **Enable CloudWatch Container Insights**: Monitor detailed container metrics, logs, and performance data through Container Insights.
36. **Configure Log Retention**: Set appropriate CloudWatch Logs retention periods (7-90 days) to balance observability needs with costs.
37. **Document Atlantis Configuration**: Maintain documentation of repository configuration, workflows, apply requirements, and operational procedures.
38. **Version Control atlantis.yaml**: Store atlantis.yaml in repository root and version control for transparency and change tracking.
39. **Test in Non-Production First**: Validate Atlantis upgrades, configuration changes, and new workflows in non-production environments before production.
40. **Monitor Webhook Delivery**: Check GitHub/GitLab webhook delivery logs to ensure events are reaching Atlantis successfully.

### Webhook Management

41. **Centralize Webhook Creation**: Use webhook submodules to manage webhooks as code rather than manual configuration for consistency.
42. **Validate Webhook URLs**: Ensure webhook URLs are publicly accessible from GitHub/GitLab before creating webhooks to avoid delivery failures.
43. **Use HTTPS for Webhooks**: Always configure webhook URLs with HTTPS to protect webhook payloads in transit.
44. **Monitor Webhook Failures**: Set up alerts for webhook delivery failures in GitHub/GitLab to detect connectivity or authentication issues.
45. **Clean Up Unused Webhooks**: Remove webhooks from repositories that no longer need Atlantis integration to reduce noise and potential security risks.

### Cost Optimization

46. **Right-Size ECS Tasks**: Monitor actual CPU and memory usage; reduce allocation if consistently below 50% to optimize costs.
47. **Use EFS Lifecycle Policies**: Configure EFS Intelligent-Tiering to move infrequently accessed plan files to cheaper storage classes.
48. **Consolidate Atlantis Instances**: Share single Atlantis deployment across multiple teams or projects rather than deploying per team.
49. **Configure ALB Deletion Protection**: Enable deletion protection on production ALBs to prevent accidental deletion but disable for non-production.
50. **Review CloudWatch Logs Costs**: Regularly review log volume and retention; reduce retention periods for non-production environments.

### Compliance and Governance

51. **Enable AWS Config**: Track Atlantis infrastructure changes over time for compliance and governance requirements.
52. **Implement Change Approval**: Require pull request approvals and apply requirements to enforce change management processes.
53. **Maintain Audit Trails**: Leverage Git history, CloudWatch Logs, and ALB access logs for comprehensive audit trails of infrastructure changes.
54. **Use Separate Environments**: Deploy separate Atlantis instances for production and non-production to isolate permissions and state.
55. **Review IAM Policies Regularly**: Audit task role permissions quarterly to ensure least-privilege access and remove unused permissions.

## Additional Resources

### Official Documentation
- **Atlantis Documentation**: https://www.runatlantis.io/docs/
- **Terraform AWS Atlantis Module GitHub**: https://github.com/terraform-aws-modules/terraform-aws-atlantis
- **Terraform Registry - Atlantis Module**: https://registry.terraform.io/modules/terraform-aws-modules/atlantis/aws
- **Atlantis GitHub Repository**: https://github.com/runatlantis/atlantis

### Deployment and Configuration
- **Atlantis Deployment Guide**: https://www.runatlantis.io/docs/deployment.html
- **Atlantis Server Configuration**: https://www.runatlantis.io/docs/server-configuration.html
- **Repository Configuration**: https://www.runatlantis.io/docs/repo-level-atlantis-yaml.html
- **Custom Workflows**: https://www.runatlantis.io/docs/custom-workflows.html

### Integration Guides
- **GitHub Integration**: https://www.runatlantis.io/docs/access-credentials.html#github
- **GitLab Integration**: https://www.runatlantis.io/docs/access-credentials.html#gitlab
- **Bitbucket Integration**: https://www.runatlantis.io/docs/access-credentials.html#bitbucket-cloud

### Security and Best Practices
- **Security Best Practices**: https://www.runatlantis.io/docs/security.html
- **AWS ECS Best Practices**: https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/
- **Atlantis Apply Requirements**: https://www.runatlantis.io/docs/apply-requirements.html

### Advanced Features
- **Policy Checking**: https://www.runatlantis.io/docs/policy-checking.html
- **Pre Workflow Hooks**: https://www.runatlantis.io/docs/pre-workflow-hooks.html
- **Post Workflow Hooks**: https://www.runatlantis.io/docs/post-workflow-hooks.html
- **Using Slack Hooks**: https://www.runatlantis.io/docs/using-slack-hooks.html

### Troubleshooting and Support
- **Atlantis Troubleshooting**: https://www.runatlantis.io/docs/troubleshooting.html
- **Atlantis Frequently Asked Questions**: https://www.runatlantis.io/docs/faq.html

## Notes for AI Agents

### Module Selection Guidance
- **Use this module** when teams need collaborative, pull request-based Terraform workflows with automated planning and centralized execution.
- **Use AWS CodePipeline** instead for fully automated CI/CD pipelines without pull request interaction or when integrating with CodeBuild/CodeDeploy.
- **Use Terraform Cloud/Enterprise** for official HashiCorp-managed solution with similar capabilities but different deployment and pricing model.
- **Use Jenkins/GitLab CI** for organizations requiring full control over CI/CD pipelines and custom Terraform execution logic.

### Architecture Recommendations
- For **small teams (1-10 people)**: Single Atlantis instance with 1024 CPU, 2048 MB memory, EFS enabled, deployed in private subnets.
- For **medium teams (10-50 people)**: Atlantis with 2048 CPU, 4096 MB memory, 2+ ECS tasks, multi-AZ deployment, separate instances per environment.
- For **large organizations (50+ people)**: Multiple Atlantis instances per team/product, custom workflows, policy checking integration, dedicated monitoring.
- For **multi-account setups**: Atlantis in central account with cross-account IAM roles for accessing state and resources in other accounts.

### Common Configuration Patterns
- **Basic GitHub**: Single subnet, 1 task, EFS disabled, GitHub integration, allowlist "github.com/myorg/*", default workflows.
- **Production GitHub**: Multi-AZ, 2+ tasks, EFS enabled, custom domain, Secrets Manager, apply requirements, ALB access logs, CloudWatch alarms.
- **Multi-Repo**: Multiple webhook configurations, IAM policies for multiple state buckets, parallel execution enabled, enhanced logging.
- **GitLab Self-Hosted**: Custom GitLab hostname, self-signed certificates, VPC peering to GitLab server, custom webhook URL.

### Environment Variable Configuration
- **Required for GitHub**: ATLANTIS_GH_USER, ATLANTIS_GH_TOKEN, ATLANTIS_GH_WEBHOOK_SECRET, ATLANTIS_REPO_ALLOWLIST
- **Required for GitLab**: ATLANTIS_GITLAB_USER, ATLANTIS_GITLAB_TOKEN, ATLANTIS_GITLAB_WEBHOOK_SECRET, ATLANTIS_REPO_ALLOWLIST
- **Recommended for all**: ATLANTIS_LOG_LEVEL=info, ATLANTIS_DEFAULT_TF_VERSION, ATLANTIS_WRITE_GIT_CREDS=true
- **Optional but useful**: ATLANTIS_PARALLEL_PLAN=true, ATLANTIS_PARALLEL_APPLY=true, ATLANTIS_REPO_CONFIG_JSON for server-side config

### IAM Permission Recommendations
- **Minimum task role**: S3 read/write on state buckets, DynamoDB read/write on lock tables, KMS decrypt/encrypt for encrypted state
- **Typical task role**: Above plus assume role for cross-account, EC2 describe for networking, CloudWatch PutMetricData for custom metrics
- **Full task role**: Above plus broad permissions matching what Terraform needs to provision (varies by infrastructure)
- **Task execution role**: SecretsManager GetSecretValue, CloudWatch CreateLogGroup/CreateLogStream/PutLogEvents, ECR image pull

### Security Best Practices
- **Never commit secrets**: Use Secrets Manager for tokens, webhook secrets; never hardcode in environment variables or Terraform code
- **Restrict network access**: Deploy in private subnets, use security groups limiting ALB ingress to known IPs, enable VPC Flow Logs
- **Enable MFA for destructive operations**: Configure apply requirements requiring approvals from multiple team members for production
- **Audit all changes**: Enable CloudTrail for API calls, review Git history for infrastructure changes, monitor CloudWatch Logs for suspicious activity
- **Rotate credentials**: Set up automatic rotation for GitHub/GitLab tokens in Secrets Manager, use short-lived assume role sessions

### Troubleshooting Tips
- **Atlantis not receiving webhooks**: Check ALB security group allows ingress, verify Route 53 record resolves, check GitHub webhook delivery logs
- **Plans failing with auth errors**: Verify GitHub token has repo permissions, check ATLANTIS_GH_TOKEN is correctly set, test token with GitHub API
- **Apply stuck or not working**: Check apply requirements configured, verify PR is approved, ensure plan lock is not held by another PR
- **ECS tasks restarting**: Check CloudWatch Logs for errors, verify memory not exceeded, check health check is passing, validate IAM permissions
- **State access errors**: Verify task role has S3 permissions, check bucket policy allows task role, confirm KMS key policy includes task role

### Cost Estimation
- **Fargate costs**: ~$30-50/month for single task (1024 CPU, 2048 MB) running continuously; double for HA setup with 2 tasks
- **ALB costs**: ~$16-20/month base cost plus $0.008/LCU-hour (typically $5-10/month for light usage)
- **EFS costs**: ~$0.30/GB-month for standard storage; typical plan storage 1-10 GB = $0.30-3/month
- **Data transfer**: Minimal for normal usage; webhook payloads and Terraform state files are small
- **Total estimate**: $50-100/month for basic deployment, $100-200/month for HA production setup with monitoring

### Integration Patterns
- **Atlantis + GitHub Actions**: Use Atlantis for plan/apply, GitHub Actions for tests, linting, policy checks before Atlantis execution
- **Atlantis + Terraform Cloud**: Use Atlantis for execution, Terraform Cloud for remote state backend and sentinel policy enforcement
- **Atlantis + OPA**: Integrate Open Policy Agent for policy checks using post_workflow_hooks to validate plans before apply
- **Atlantis + Slack**: Configure webhook notifications to Slack for plan/apply results, failures, and lock status updates
- **Atlantis + Datadog/New Relic**: Ship CloudWatch Logs to observability platform for centralized monitoring and alerting
- **Multi-account**: Atlantis in hub account assumes roles in spoke accounts via cross-account IAM roles for Terraform execution
