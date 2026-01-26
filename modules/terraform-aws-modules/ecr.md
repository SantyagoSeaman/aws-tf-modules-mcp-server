# Terraform AWS ECR Module

## Module Information

- **Module Name**: `ecr`
- **Source**: `terraform-aws-modules/ecr/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ecr
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ecr/aws/latest
- **Latest Version**: 2.3.1
- **Purpose**: Terraform module that creates and manages AWS Elastic Container Registry (ECR) repositories for storing Docker and OCI container images
- **Service**: AWS ECR (Elastic Container Registry)
- **Category**: Container Management, DevOps, CI/CD
- **Keywords**: ecr, container-registry, docker, container-images, image-scanning, lifecycle-policy, kms-encryption, repository-policy, replication, pull-through-cache, vulnerability-scanning, private-registry, public-registry, cross-account-access
- **Use For**: container image storage, Docker image hosting, Kubernetes container registry, CI/CD pipelines, microservices deployments, multi-region image distribution, container vulnerability scanning, image lifecycle management

## Description

AWS Elastic Container Registry (ECR) is a fully managed container registry service that makes it easy to store, manage, share, and deploy container images and artifacts. This Terraform module provides a comprehensive solution for creating and managing both private and public ECR repositories with extensive configuration options for security, lifecycle management, replication, and access control.

The module supports image scanning for vulnerabilities (basic and enhanced), lifecycle policies for automatic image cleanup, cross-region replication for high availability, and pull-through cache rules for upstream registries like DockerHub. It enables fine-grained access control through repository policies and IAM integration, supports both mutable and immutable image tags with exclusion filters, and provides encryption options using AWS KMS or AES256.

This module is essential for organizations running containerized workloads on AWS, particularly those using Amazon ECS, EKS, or Fargate. It integrates seamlessly with CI/CD pipelines and supports multi-account and multi-region architectures.

## Key Features

- **Private Repository Creation**: Create private ECR repositories with access control
- **Public Repository Support**: Create public ECR repositories for community image sharing
- **Image Tag Mutability**: Configure MUTABLE, IMMUTABLE, or with exclusion filters for specific tags
- **Image Scanning**: Enable BASIC or ENHANCED vulnerability scanning on push or continuously
- **Lifecycle Policies**: Define automated image retention rules based on age, count, or tag patterns
- **KMS/AES256 Encryption**: Encrypt repository images at rest using KMS or AWS-managed encryption
- **Repository Policies**: Configure fine-grained IAM policies for push, pull, and administrative access
- **Registry Policies**: Implement registry-level policies for cross-account access
- **Cross-Region Replication**: Automatically replicate images to multiple AWS regions (up to 10 rules)
- **Pull-Through Cache Rules**: Cache images from DockerHub, public ECR, and private registries
- **Force Delete Option**: Enable force deletion of repositories containing images
- **Catalog Metadata**: Add descriptions, architectures, and OS compatibility for public repositories
- **Lambda Integration**: Built-in support for Lambda service role read access

## Main Use Cases

1. **CI/CD Container Image Storage**: Store application container images built by CI/CD pipelines
2. **Microservices Image Management**: Manage container images for microservices architectures
3. **Kubernetes Cluster Registry**: Serve as container registry for Amazon EKS clusters
4. **Multi-Region Application Deployment**: Replicate images across regions for global deployments
5. **Container Security Scanning**: Automatically scan images for vulnerabilities before deployment
6. **Image Lifecycle Management**: Automatically clean up old images to optimize storage costs
7. **Cross-Account Image Sharing**: Share container images across AWS accounts
8. **Public Image Distribution**: Host open-source container images via public repositories
9. **DockerHub Caching**: Cache DockerHub images to avoid rate limits and reduce latency

## Submodules

This module has **no submodules**. All functionality is available through the root module with feature flags.

## Main Input Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Master toggle for all resources |
| `create_repository` | `bool` | `true` | Whether to create the repository |
| `repository_name` | `string` | `""` | The name of the repository (required) |
| `repository_type` | `string` | `"private"` | Repository type: `private` or `public` |
| `tags` | `map(string)` | `{}` | Tags to apply to all resources |

### Repository Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `repository_image_tag_mutability` | `string` | `"IMMUTABLE"` | Tag mutability: `MUTABLE`, `IMMUTABLE`, `MUTABLE_WITH_EXCLUSION`, `IMMUTABLE_WITH_EXCLUSION` |
| `repository_encryption_type` | `string` | `null` | Encryption type: `KMS` or `AES256` |
| `repository_kms_key` | `string` | `null` | KMS key ARN for encryption |
| `repository_image_scan_on_push` | `bool` | `true` | Enable vulnerability scanning on push |
| `repository_force_delete` | `bool` | `null` | Delete repository even if it contains images |

### Access Control

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `attach_repository_policy` | `bool` | `true` | Attach policy to repository |
| `create_repository_policy` | `bool` | `true` | Create repository policy |
| `repository_read_access_arns` | `list(string)` | `[]` | IAM ARNs with read (pull) access |
| `repository_read_write_access_arns` | `list(string)` | `[]` | IAM ARNs with read/write (pull/push) access |
| `repository_lambda_read_access_arns` | `list(string)` | `[]` | Lambda service role ARNs with read access |
| `repository_policy` | `string` | `null` | Custom repository policy JSON |

### Lifecycle Policy

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_lifecycle_policy` | `bool` | `true` | Create lifecycle policy |
| `repository_lifecycle_policy` | `string` | `""` | Lifecycle policy JSON document |

### Registry Features

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_registry_policy` | `bool` | `false` | Create registry-level policy |
| `registry_pull_through_cache_rules` | `map(object)` | `{}` | Pull-through cache rules configuration |
| `manage_registry_scanning_configuration` | `bool` | `false` | Manage registry scanning configuration |
| `registry_scan_type` | `string` | `"ENHANCED"` | Scan type: `ENHANCED` or `BASIC` |
| `create_registry_replication_configuration` | `bool` | `false` | Create replication configuration |
| `registry_replication_rules` | `list(object)` | `null` | Replication rules (max 10) |

## Main Outputs

| Output | Description |
|--------|-------------|
| `repository_name` | Name of the created repository |
| `repository_arn` | Full ARN of the repository |
| `repository_registry_id` | AWS account ID where the repository was created |
| `repository_url` | Full repository URL for Docker operations (push/pull) |

## Usage Examples

### Example 1: Private Repository with Lifecycle Policy

```hcl
module "ecr" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 2.3"

  repository_name = "my-app"

  repository_read_write_access_arns = [
    "arn:aws:iam::012345678901:role/ci-cd-role"
  ]

  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 30 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 30
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Expire untagged images older than 14 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 14
        }
        action = {
          type = "expire"
        }
      }
    ]
  })

  tags = {
    Environment = "production"
    Team        = "platform"
  }
}
```

### Example 2: Public Repository with Catalog Data

```hcl
module "public_ecr" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 2.3"

  repository_name = "my-public-image"
  repository_type = "public"

  public_repository_catalog_data = {
    description       = "Docker container for my application"
    about_text        = "Detailed information about this container"
    usage_text        = "docker pull public.ecr.aws/xxx/my-public-image:latest"
    architectures     = ["x86-64", "ARM 64"]
    operating_systems = ["Linux"]
  }

  tags = {
    Visibility = "public"
  }
}
```

### Example 3: Repository with KMS Encryption and Enhanced Scanning

```hcl
module "ecr_secure" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 2.3"

  repository_name = "secure-app"

  # KMS encryption
  repository_encryption_type = "KMS"
  repository_kms_key         = aws_kms_key.ecr.arn

  # Immutable tags for production
  repository_image_tag_mutability = "IMMUTABLE"

  # Enable enhanced scanning at registry level
  manage_registry_scanning_configuration = true
  registry_scan_type                     = "ENHANCED"
  registry_scan_rules = [
    {
      scan_frequency = "CONTINUOUS_SCAN"
      filter = [{
        filter      = "*"
        filter_type = "WILDCARD"
      }]
    }
  ]

  repository_read_write_access_arns = [
    data.aws_iam_role.ci_cd.arn
  ]

  tags = {
    Environment = "production"
    Security    = "high"
  }
}
```

### Example 4: Pull-Through Cache and Multi-Region Replication

```hcl
module "ecr_enterprise" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 2.3"

  repository_name = "enterprise-app"

  # Pull-through cache for Docker Hub
  registry_pull_through_cache_rules = {
    docker_hub = {
      ecr_repository_prefix = "docker-hub"
      upstream_registry_url = "registry-1.docker.io"
      credential_arn        = aws_secretsmanager_secret.dockerhub.arn
    }
    ecr_public = {
      ecr_repository_prefix = "ecr-public"
      upstream_registry_url = "public.ecr.aws"
    }
  }

  # Multi-region replication
  create_registry_replication_configuration = true
  registry_replication_rules = [
    {
      destinations = [
        { region = "us-west-2" },
        { region = "eu-west-1" }
      ]
      repository_filters = [
        {
          filter      = "prod-*"
          filter_type = "PREFIX_MATCH"
        }
      ]
    }
  ]

  repository_lifecycle_policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 50 production images"
      selection = {
        tagStatus     = "tagged"
        tagPrefixList = ["prod-"]
        countType     = "imageCountMoreThan"
        countNumber   = 50
      }
      action = { type = "expire" }
    }]
  })

  tags = {
    Environment = "production"
    Tier        = "enterprise"
  }
}
```

### Example 5: Tag Mutability with Exclusions

```hcl
module "ecr_dev" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 2.3"

  repository_name = "dev-app"

  # Immutable tags except for 'latest' and 'dev-*'
  repository_image_tag_mutability = "IMMUTABLE_WITH_EXCLUSION"
  repository_image_tag_mutability_exclusion_filter = [
    {
      filter      = "latest"
      filter_type = "EQUALS"
    },
    {
      filter      = "dev-*"
      filter_type = "PREFIX_MATCH"
    }
  ]

  repository_read_write_access_arns = [
    data.aws_iam_role.developers.arn
  ]

  tags = {
    Environment = "development"
  }
}
```

## Best Practices

### Repository Configuration

1. **Use Immutable Tags for Production**: Enable immutable tags for production repositories to prevent accidental tag overwrites
2. **Configure Tag Exclusion Patterns**: Use exclusion filters for development tags (e.g., "latest", "dev-*") while keeping production tags immutable
3. **Enable Force Delete Carefully**: Only enable for development/test repositories; never for production
4. **Use Descriptive Repository Names**: Use patterns like `{service-name}` or `{team}/{service}` for clarity

### Security and Access Control

1. **Enable Image Scanning**: Always enable scan-on-push; add ENHANCED scanning for production
2. **Encrypt with KMS**: Use KMS encryption for sensitive images to maintain full control over encryption keys
3. **Implement Least Privilege Access**: Configure repository policies granting minimum necessary permissions
4. **Use IAM Roles over Users**: Prefer IAM roles for ECS tasks, Lambda functions, and EC2 instances
5. **Enable VPC Endpoints**: Use VPC endpoints for ECR to keep traffic within AWS network

### Lifecycle and Retention

1. **Implement Lifecycle Policies**: Define rules to automatically remove old images and reduce costs
2. **Keep Recent Images**: Retain the last N images (e.g., 30) or images from the last N days (e.g., 90)
3. **Protect Production Tags**: Use rules that preserve images with production tags (e.g., "prod-*", "v*.*.*")
4. **Clean Untagged Images**: Delete untagged images after 1-14 days to prevent storage bloat

### Replication and Availability

1. **Enable Cross-Region Replication**: Replicate images to multiple regions for disaster recovery
2. **Use Replication Filters**: Apply prefix or tag filters to replicate only necessary images
3. **Test Cross-Region Failover**: Regularly test deployments using replicated images from secondary regions

### Pull-Through Cache

1. **Cache External Registries**: Configure for DockerHub to avoid rate limits and reduce latency
2. **Secure Upstream Credentials**: Store credentials in AWS Secrets Manager
3. **Use for Base Images**: Prioritize caching frequently used base images (Alpine, Ubuntu, Node)

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-ecr
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ecr/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-ecr/tree/master/examples
- **AWS ECR Documentation**: https://docs.aws.amazon.com/ecr/latest/userguide/what-is-ecr.html
- **ECR Image Scanning**: https://docs.aws.amazon.com/ecr/latest/userguide/image-scanning.html
- **ECR Lifecycle Policies**: https://docs.aws.amazon.com/ecr/latest/userguide/LifecyclePolicies.html
- **ECR Replication**: https://docs.aws.amazon.com/ecr/latest/userguide/replication.html
- **ECR Pull Through Cache**: https://docs.aws.amazon.com/ecr/latest/userguide/pull-through-cache.html
- **ECR Best Practices**: https://docs.aws.amazon.com/ecr/latest/userguide/best-practices.html
- **ECR Pricing**: https://aws.amazon.com/ecr/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Choose Repository Type**: Use `repository_type = "private"` (default) for internal images, `"public"` for community sharing
2. **Enable Security Features**: Always enable image scanning; use KMS encryption for sensitive workloads
3. **Configure Lifecycle Policies**: Implement rules to automatically manage image retention and reduce costs
4. **Set Tag Mutability**: Use `IMMUTABLE` for production; use `*_WITH_EXCLUSION` for dev environments needing mutable tags
5. **Implement Access Controls**: Use `repository_read_access_arns` and `repository_read_write_access_arns` for IAM-based access
6. **Enable Replication**: Set `create_registry_replication_configuration = true` for production images requiring high availability
7. **Use Pull-Through Cache**: Configure `registry_pull_through_cache_rules` for external registries to improve reliability
8. **Tag Resources**: Apply comprehensive tags for cost tracking and ownership
9. **Note No Submodules**: All features are in the root module; use feature flags like `create_repository`, `create_lifecycle_policy`, etc.
