# Terraform AWS ECR Module

## Module Information

- **Module Name**: `ecr`
- **Module ID**: `terraform-aws-modules/ecr/aws`
- **Source**: `terraform-aws-modules/ecr/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ecr
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ecr/aws/latest
- **Latest Version**: 3.2.0
- **Compatibility**: Terraform >= 1.5.7, AWS provider >= 6.28 (root module and `repository-template` submodule). Since v3.0.0 the module requires AWS provider v6.x and added tag-mutability exclusion filters — a breaking change from v2.x; pin `~> 3.0` when generating configs.
- **Purpose**: Terraform module that creates and manages AWS Elastic Container Registry (ECR) private/public repositories, registry-level policies, replication, pull-through cache rules, and repository creation templates
- **Service**: AWS ECR (Elastic Container Registry)
- **Category**: Container Management, DevOps, CI/CD
- **Keywords**: ecr, container-registry, docker, oci-images, image-scanning, lifecycle-policy, kms-encryption, repository-policy, cross-region-replication, pull-through-cache, vulnerability-scanning, public-registry, repository-creation-template, tag-immutability
- **Use For**: container image storage for ECS/EKS/Fargate workloads, CI/CD image publishing pipelines, multi-region image replication for disaster recovery, automated vulnerability scanning of container images, image lifecycle and retention automation, DockerHub/public-registry pull-through caching to avoid rate limits, cross-account image sharing via registry policy, public open-source image distribution, auto-provisioning per-prefix repositories via creation templates, registry-wide security governance

## Description

Amazon Elastic Container Registry (ECR) is AWS's fully managed Docker/OCI container registry for storing, scanning, and distributing container images and artifacts. This module provisions both private (`aws_ecr_repository`) and public (`aws_ecrpublic_repository`) repositories along with their access policies, lifecycle policies, and image-scanning configuration, plus registry-wide resources that apply across an entire AWS account/region: registry policies for cross-account access, pull-through cache rules that proxy upstream registries (Docker Hub, public ECR, other private ECR registries), registry scanning configuration, and cross-region replication configuration.

Repository access can be granted either through simple ARN lists (`repository_read_access_arns`, `repository_read_write_access_arns`, `repository_lambda_read_access_arns`) that the module turns into a generated IAM policy document, through fully structured `repository_policy_statements` objects for fine-grained rules (custom actions, conditions, deny statements), or by supplying a raw JSON `repository_policy`. Image tags can be `MUTABLE`, `IMMUTABLE`, or either mode with exclusion filters so specific prefixes (e.g., `latest*`, `dev-*`) stay mutable while the rest of the repository remains immutable. Images can be encrypted with AWS-managed AES256 or a customer-managed KMS key, and vulnerability scanning can run on push (`BASIC`) or continuously registry-wide (`ENHANCED`).

The module ships one submodule, `repository-template`, which manages `aws_ecr_repository_creation_template` resources — templates that tell ECR how to auto-provision repositories matching a name prefix whenever an image is pulled through a pull-through cache rule and/or replicated into the registry, optionally creating the IAM role AWS needs to tag or KMS-encrypt those auto-created repositories. This is the recommended approach for registries that dynamically mirror many upstream images without pre-creating a repository per image.

## Key Features

- **Private & Public Repositories**: single `repository_type` toggle between `aws_ecr_repository` (private) and `aws_ecrpublic_repository` (public)
- **Flexible Access Control**: ARN-list-based auto-generated policies, structured `repository_policy_statements`, or a fully custom `repository_policy` JSON document
- **Tag Mutability with Exclusions**: `MUTABLE` / `IMMUTABLE` / `*_WITH_EXCLUSION` plus filter lists to carve out prefixes like `latest` or `dev-*`
- **Vulnerability Scanning**: per-repository scan-on-push plus registry-wide `BASIC`/`ENHANCED` scanning configuration with frequency and repository filters
- **Encryption at Rest**: AES256 (default) or a customer-managed KMS key per repository
- **Lifecycle Policies**: JSON-based rules to expire images by age, count, or tag pattern
- **Registry Policies**: account-level policy for cross-account replication/pull permissions
- **Pull-Through Cache Rules**: proxy and cache images from Docker Hub, public ECR, or other private ECR registries, with optional Secrets Manager credentials and custom IAM role
- **Cross-Region Replication**: up to 10 replication rules with per-rule destination regions/registries and repository filters
- **Repository Creation Templates (submodule)**: auto-provision repositories for pull-through-cache/replication with independent tag mutability, encryption, and lifecycle settings
- **Public Repository Catalog Data**: description, usage text, logo, architectures, and OS metadata for the AWS Public ECR Gallery
- **Registry-Only Mode**: `create_repository = false` manages just the registry-level resources (policy, replication, scanning, pull-through cache) from the same module call
- **Multi-Region Provider Targeting**: per-resource `region` argument to manage resources in a non-default provider region

## Main Use Cases

1. **CI/CD Container Image Storage**: store application images built and pushed by CI/CD pipelines
2. **Kubernetes/ECS/Fargate Cluster Registry**: serve as the container registry backing EKS, ECS, or Fargate workloads
3. **Multi-Region Image Replication**: replicate production images across regions for disaster recovery and low-latency pulls
4. **Container Vulnerability Scanning**: automatically scan images on push or continuously for CVEs before deployment
5. **Image Lifecycle Management**: automatically expire old or untagged images to control storage costs
6. **Cross-Account Image Sharing**: grant other AWS accounts pull or replication access via a registry policy
7. **DockerHub/Public-ECR Pull-Through Caching**: cache upstream images to avoid Docker Hub rate limits and reduce pull latency
8. **Public Image Distribution**: host open-source container images on the AWS Public ECR Gallery
9. **Automated Repository Provisioning**: auto-create per-prefix repositories for pull-through cache or replication via the `repository-template` submodule
10. **Registry-Wide Security Governance**: enforce scanning configuration and registry policy consistently across an account

## Submodules

### 1. repository-template
- **Purpose**: Create `aws_ecr_repository_creation_template` resources that auto-provision repositories matching a prefix for pull-through-cache and/or replication, with an optional IAM role for KMS/tag support
- **Source**: `terraform-aws-modules/ecr/aws//modules/repository-template`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/ecr/aws/latest/submodules/repository-template
- **Key Features**: pull-through-cache rule creation, `PULL_THROUGH_CACHE`/`REPLICATION` targeting via `applied_for`, auto-created IAM role for the repository-creation service role, tag-mutability exclusion filters, per-template lifecycle policy
- **Use Cases**: Docker Hub/public-ECR mirroring without pre-creating repos, per-prefix governance for replicated production images, KMS-encrypted auto-provisioned repositories

## Submodule 1: repository-template

### Description

Creates an `aws_ecr_repository_creation_template` that tells ECR how to configure repositories it auto-creates for a given name prefix — used together with pull-through cache rules (images pulled from an upstream registry) and/or registry replication (images replicated into this registry). It can optionally provision the associated `aws_ecr_pull_through_cache_rule` and an IAM role/policy that ECR assumes when it needs to tag or KMS-encrypt the auto-created repository.

### Key Features

- Applies to `PULL_THROUGH_CACHE`, `REPLICATION`, or both (`applied_for`)
- Optional built-in `aws_ecr_pull_through_cache_rule` creation (`create_pull_through_cache_rule`)
- Auto-provisions an IAM role/policy for repository creation when KMS encryption or tags are needed on auto-created repos (`create_iam_role`)
- Same tag-mutability, exclusion-filter, encryption, and lifecycle-policy controls as the root module, applied to every repository the template creates
- Same `repository_policy_statements` / `repository_policy` / ARN-list access-control model as the root module

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `prefix` | `string` | `""` | Repository name prefix to match (required); use `ROOT` to match any prefix not covered by another template |
| `description` | `string` | `null` | Description for the template |
| `applied_for` | `list(string)` | `["PULL_THROUGH_CACHE"]` | Features this template applies to: `PULL_THROUGH_CACHE`, `REPLICATION`, or both |
| `create_pull_through_cache_rule` | `bool` | `false` | Whether to create the associated pull-through cache rule |
| `upstream_registry_url` | `string` | `null` | Upstream registry URL for the pull-through cache rule |
| `credential_arn` | `string` | `null` | Secrets Manager ARN for upstream registry authentication |
| `custom_role_arn` | `string` | `null` | Custom IAM role ARN for repository creation (required if using tags or KMS without `create_iam_role`) |
| `create_iam_role` | `bool` | `true` | Whether to create the ECR service IAM role for repository creation |
| `image_tag_mutability` | `string` | `"IMMUTABLE"` | `MUTABLE`, `IMMUTABLE`, `MUTABLE_WITH_EXCLUSION`, or `IMMUTABLE_WITH_EXCLUSION` |
| `image_tag_mutability_exclusion_filter` | `list(object)` | `null` | Filters for tags exempt from the default mutability setting — fields: `filter`, `filter_type` |
| `encryption_type` | `string` | `"AES256"` | `AES256` or `KMS` for repositories created from this template |
| `kms_key_arn` | `string` | `null` | KMS key ARN used when `encryption_type = "KMS"` |
| `lifecycle_policy` | `string` | `null` | Lifecycle policy JSON applied to created repositories |
| `repository_policy_statements` | `map(object)` | `null` | Structured IAM policy statements merged into the generated repository policy — fields: `sid`, `actions`, `not_actions`, `effect`, `resources`, `not_resources`, `principals`, `not_principals`, … (8 shown; call get_module with sections=["inputs","outputs"] for the complete list) |
| `resource_tags` | `map(string)` | `{}` | Tags applied to repositories created from this template |
| `tags` | `map(string)` | `{}` | Tags applied to the template's own resources (IAM role, etc.) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `iam_role_arn` | ARN of the IAM role created for repository creation |
| `iam_role_name` | Name of the IAM role created |
| `iam_role_unique_id` | Stable unique ID of the IAM role |

### Usage Example

```hcl
# Auto-provision repositories that cache Docker Hub images on first pull
resource "aws_secretsmanager_secret" "dockerhub" {
  name = "ecr-pullthroughcache/dockerhub-credentials"
}

resource "aws_secretsmanager_secret_version" "dockerhub" {
  secret_id     = aws_secretsmanager_secret.dockerhub.id
  secret_string = jsonencode({ username = "example", accessToken = "..." })
}

module "dockerhub_repository_template" {
  source  = "terraform-aws-modules/ecr/aws//modules/repository-template"
  version = "~> 3.0"

  description = "Pull-through cache repository template for Docker Hub artifacts"
  prefix      = "docker-hub"

  create_pull_through_cache_rule = true
  upstream_registry_url          = "registry-1.docker.io"
  credential_arn                 = aws_secretsmanager_secret.dockerhub.arn

  image_tag_mutability = "MUTABLE_WITH_EXCLUSION"
  image_tag_mutability_exclusion_filter = [
    { filter = "latest*", filter_type = "WILDCARD" }
  ]

  tags = {
    Environment = "shared"
  }
}
```

## Main Module: ECR Repository & Registry

### Description

The root module manages the repository itself (private or public) plus every account/registry-level ECR resource: repository and registry policies, lifecycle policies, pull-through cache rules, registry scanning configuration, and cross-region replication configuration. Most consumers call it directly for a single repository, and call it again with `create_repository = false` to manage registry-wide resources independently of any specific repository.

### Key Features

- `repository_type` toggle between `private` (`aws_ecr_repository`) and `public` (`aws_ecrpublic_repository`)
- Generated repository policy from `repository_read_access_arns` / `repository_read_write_access_arns` / `repository_lambda_read_access_arns` / `repository_policy_statements`, or a fully custom `repository_policy`
- `create_repository = false` mode to manage only registry-level resources (policy, replication, scanning, pull-through cache) from the same module
- Registry-wide pull-through cache rules, replication rules (up to 10), and `BASIC`/`ENHANCED` scanning configuration with per-rule filters
- Feature-flag composition: `create`, `create_repository`, `create_repository_policy`, `attach_repository_policy`, `create_lifecycle_policy`, `create_registry_policy`, `manage_registry_scanning_configuration`, `create_registry_replication_configuration`

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `repository_name` | `string` | `""` | Name of the repository (required when `create_repository = true`) |
| `repository_type` | `string` | `"private"` | `private` or `public` |
| `create_repository` | `bool` | `true` | Whether to create the repository; set `false` to manage only registry-level resources |
| `repository_image_tag_mutability` | `string` | `"IMMUTABLE"` | `MUTABLE`, `IMMUTABLE`, `MUTABLE_WITH_EXCLUSION`, or `IMMUTABLE_WITH_EXCLUSION` |
| `repository_image_tag_mutability_exclusion_filter` | `list(object)` | `null` | Filters exempting specific tags from the mutability setting — fields: `filter`, `filter_type` |
| `repository_encryption_type` | `string` | `null` (`AES256` behavior) | `KMS` or `AES256` |
| `repository_kms_key` | `string` | `null` | KMS key ARN used when `repository_encryption_type = "KMS"` |
| `repository_image_scan_on_push` | `bool` | `true` | Scan images for vulnerabilities on push |
| `repository_force_delete` | `bool` | `null` (`false` behavior) | Delete the repository even if it still contains images |
| `attach_repository_policy` | `bool` | `true` | Whether to create/attach the private repository's `aws_ecr_repository_policy` |
| `create_repository_policy` | `bool` | `true` | Auto-generate the policy from access-ARN variables and `repository_policy_statements`; set `false` to use `repository_policy` verbatim |
| `repository_policy_statements` | `map(object)` | `null` | Structured IAM statements (sid, actions, resources, principals, conditions) merged into the generated policy — fields: `sid`, `actions`, `not_actions`, `effect`, `resources`, `not_resources`, `principals`, `not_principals`, … (8 shown; call get_module with sections=["inputs","outputs"] for the complete list) |
| `repository_policy` | `string` | `null` | Raw JSON policy used when `create_repository_policy = false` |
| `repository_read_access_arns` | `list(string)` | `[]` | IAM principal ARNs granted pull-only access |
| `repository_read_write_access_arns` | `list(string)` | `[]` | IAM principal ARNs granted pull/push access |
| `repository_lambda_read_access_arns` | `list(string)` | `[]` | Lambda service role ARNs granted pull-only access |
| `public_repository_catalog_data` | `object` | `null` | Description, about/usage text, logo, architectures, OS for public repositories — fields: `about_text`, `architectures`, `description`, `logo_image_blob`, `operating_systems`, `usage_text` |
| `create_lifecycle_policy` | `bool` | `true` | Whether to create a lifecycle policy |
| `repository_lifecycle_policy` | `string` | `""` | Lifecycle policy JSON document |
| `create_registry_policy` | `bool` | `false` | Create a registry-level (account-wide) policy |
| `registry_policy` | `string` | `null` | Registry policy JSON document |
| `registry_pull_through_cache_rules` | `map(object)` | `{}` | Pull-through cache rules (prefix, upstream URL, credential ARN, custom role, region) — fields: `ecr_repository_prefix`, `upstream_registry_url`, `credential_arn`, `custom_role_arn`, `upstream_repository_prefix`, `region` |
| `manage_registry_scanning_configuration` | `bool` | `false` | Manage the registry-wide scanning configuration |
| `registry_scan_type` | `string` | `"ENHANCED"` | `ENHANCED` or `BASIC` |
| `registry_scan_rules` | `list(object)` | `null` | Scan-frequency and repository-filter rules for registry scanning — fields: `scan_frequency`, `filter` |
| `create_registry_replication_configuration` | `bool` | `false` | Create a cross-region/cross-account replication configuration |
| `registry_replication_rules` | `list(object)` | `null` | Replication destinations and repository filters (max 10 rules) — fields: `destinations`, `repository_filters` |
| `region` | `string` | `null` | Override the provider's default region for this module's resources |
| `tags` | `map(string)` | `{}` | Tags applied to all created resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `repository_name` | Name of the created repository |
| `repository_arn` | Full ARN of the repository |
| `repository_registry_id` | Registry/AWS account ID where the repository was created |
| `repository_url` | Full repository URL used for `docker login`/`push`/`pull` |

### Usage Examples

#### Example 1: Private Repository with Lifecycle Policy and CI/CD Access

```hcl
module "ecr" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 3.0"

  repository_name = "my-app"

  repository_read_write_access_arns = [
    "arn:aws:iam::012345678901:role/ci-cd-role"
  ]

  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 30 tagged images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 30
        }
        action = { type = "expire" }
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
        action = { type = "expire" }
      }
    ]
  })

  tags = {
    Environment = "production"
    Team        = "platform"
  }
}
```

#### Example 2: KMS-Encrypted Repository with Fine-Grained Policy Statements

```hcl
module "ecr_secure" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 3.0"

  repository_name = "secure-app"

  repository_encryption_type      = "KMS"
  repository_kms_key              = aws_kms_key.ecr.arn
  repository_image_tag_mutability = "IMMUTABLE"

  # Structured statements instead of a hand-written JSON policy
  repository_policy_statements = {
    ci_push = {
      sid     = "CIPush"
      effect  = "Allow"
      actions = ["ecr:PutImage", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload"]
      principals = [{
        type        = "AWS"
        identifiers = ["arn:aws:iam::012345678901:role/ci-cd-role"]
      }]
    }
  }

  manage_registry_scanning_configuration = true
  registry_scan_type                     = "ENHANCED"
  registry_scan_rules = [
    {
      scan_frequency = "CONTINUOUS_SCAN"
      filter         = [{ filter = "*", filter_type = "WILDCARD" }]
    }
  ]

  tags = {
    Environment = "production"
    Security    = "high"
  }
}
```

#### Example 3: Registry-Wide Pull-Through Cache and Multi-Region Replication

```hcl
module "ecr_registry" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 3.0"

  create_repository = false # this call manages only registry-level resources

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

  create_registry_replication_configuration = true
  registry_replication_rules = [
    {
      destinations = [
        { region = "us-west-2", registry_id = "012345678901" },
        { region = "eu-west-1", registry_id = "012345678901" }
      ]
      repository_filters = [
        { filter = "prod-", filter_type = "PREFIX_MATCH" }
      ]
    }
  ]

  tags = {
    Environment = "production"
  }
}
```

#### Example 4: Public Repository with Catalog Data

```hcl
module "public_ecr" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 3.0"

  repository_name = "my-public-image"
  repository_type = "public"

  repository_read_write_access_arns = ["arn:aws:iam::012345678901:role/ci-cd-role"]

  public_repository_catalog_data = {
    description       = "Docker container for my application"
    about_text        = file("${path.module}/files/ABOUT.md")
    usage_text        = file("${path.module}/files/USAGE.md")
    architectures     = ["x86-64", "ARM 64"]
    operating_systems = ["Linux"]
  }

  tags = {
    Visibility = "public"
  }
}
```

#### Example 5: Tag Mutability with Exclusions for Dev Repositories

```hcl
module "ecr_dev" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 3.0"

  repository_name = "dev-app"

  repository_image_tag_mutability = "IMMUTABLE_WITH_EXCLUSION"
  repository_image_tag_mutability_exclusion_filter = [
    { filter = "latest", filter_type = "EQUALS" },
    { filter = "dev-*", filter_type = "PREFIX_MATCH" }
  ]

  repository_force_delete = true # dev only - never enable in production

  repository_read_write_access_arns = [data.aws_iam_role.developers.arn]

  tags = {
    Environment = "development"
  }
}
```

## Best Practices

### Repository Configuration
1. **Use Immutable Tags for Production**: enable `IMMUTABLE` for production repositories, and use the `*_WITH_EXCLUSION` variants when only a few tags need to stay mutable (e.g., `latest`, `dev-*`) instead of disabling immutability entirely.
2. **Enable Force Delete Only in Non-Production**: `repository_force_delete = true` deletes a repository even if it still contains images — never set this on a production repository.
3. **Name Repositories Predictably**: use a `{team}/{service}` or `{service-name}` naming scheme so lifecycle/replication/pull-through-cache prefix filters can target groups of repositories cleanly.
4. **Separate Registry-Level Calls from Repository Calls**: use `create_repository = false` in a dedicated module call to manage registry policy, replication, scanning, and pull-through cache independently of any single repository's lifecycle.

### Security and Access Control
1. **Prefer `repository_policy_statements` Over Hand-Written JSON**: use the structured variable for custom rules so Terraform validates the policy shape instead of hand-rolling `jsonencode`/raw JSON via `repository_policy`.
2. **Always Enable Image Scanning**: keep `repository_image_scan_on_push = true`, and enable registry-wide `ENHANCED` continuous scanning for production repositories.
3. **Encrypt Sensitive Images with KMS**: set `repository_encryption_type = "KMS"` with a customer-managed key when workloads require full control over the encryption key (rotation, cross-account grants, CloudTrail key-usage auditing).
4. **Grant Least-Privilege Push/Pull Access**: scope `repository_read_access_arns`/`repository_read_write_access_arns` to specific CI/CD roles rather than broad account principals.
5. **Remember Public Repository Policies Are Always Attached**: `attach_repository_policy` only gates the policy resource for private repositories — public repositories (`repository_type = "public"`) always get a policy attached based on `create_repository_policy`/`repository_policy`.
6. **Use IAM Roles, Not Long-Lived Users**: reference IAM roles (ECS task roles, EKS IRSA, Lambda execution roles, CI/CD OIDC roles) in the access-ARN variables instead of IAM user ARNs.

### Lifecycle and Retention
1. **Always Define a Lifecycle Policy**: leave `create_lifecycle_policy = true` and supply `repository_lifecycle_policy` to bound storage costs; the default empty `repository_lifecycle_policy = ""` has no effect until rules are supplied.
2. **Expire Untagged Images Quickly**: remove untagged images after 1-14 days — they accumulate from every `docker build` and rarely need retention.
3. **Bound Tagged Image Counts**: keep the last N images per prefix (e.g., 30-50) using `tagPrefixList` + `imageCountMoreThan` rather than relying on manual cleanup.
4. **Protect Release Tags**: give production/release tag patterns (`v*`, `prod-*`) their own lower-priority rule so they are not caught by a broader untagged/dev cleanup rule.

### Replication and Pull-Through Cache
1. **Filter Replication by Prefix**: use `repository_filters` on each `registry_replication_rules` entry so only production-tagged repositories replicate cross-region, keeping dev traffic and cost local.
2. **Store Upstream Credentials in Secrets Manager**: pass a Secrets Manager ARN via `credential_arn` for authenticated pull-through cache rules (e.g., Docker Hub) rather than embedding credentials elsewhere.
3. **Use the `repository-template` Submodule for Auto-Provisioned Repos**: when pulling through cache or replicating into many auto-created repositories, use `repository-template` so every auto-created repository gets consistent tag-mutability, encryption, and lifecycle settings instead of relying on ECR defaults.
4. **Cache Frequently Used Base Images**: prioritize Docker Hub/public ECR pull-through cache rules for common base images (Alpine, Ubuntu, Node, Python) to reduce upstream rate-limit exposure and pull latency.

### Operational Excellence
1. **Pin the Module Version**: use `version = "~> 3.0"`; upgrading from v2.x is a breaking change (AWS provider minimum raised to v6.x).
2. **Tag Comprehensively**: apply the shared `tags` map (and the submodule's `resource_tags` for auto-created repositories) for cost allocation and ownership tracking.
3. **Use `region` for Multi-Region Registry Management**: pass the `region` argument instead of a second provider alias block when only the ECR resources in a module call need to target a non-default region.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-ecr
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ecr/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-ecr/tree/master/examples
- **Repository Template Submodule**: https://registry.terraform.io/modules/terraform-aws-modules/ecr/aws/latest/submodules/repository-template
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-ecr/blob/master/CHANGELOG.md
- **AWS ECR Documentation**: https://docs.aws.amazon.com/ecr/latest/userguide/what-is-ecr.html
- **ECR Image Scanning**: https://docs.aws.amazon.com/ecr/latest/userguide/image-scanning.html
- **ECR Lifecycle Policies**: https://docs.aws.amazon.com/ecr/latest/userguide/LifecyclePolicies.html
- **ECR Replication**: https://docs.aws.amazon.com/ecr/latest/userguide/replication.html
- **ECR Pull Through Cache**: https://docs.aws.amazon.com/ecr/latest/userguide/pull-through-cache.html
- **ECR Repository Creation Templates**: https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-creation-templates.html
- **ECR Best Practices**: https://docs.aws.amazon.com/ecr/latest/userguide/best-practices.html
- **ECR Pricing**: https://aws.amazon.com/ecr/pricing/

## Notes for AI Agents

When generating Terraform using this module:

1. **Pin the module version** (`version = "~> 3.0"`) and use AWS provider `>= 6.28` — v3.0.0 raised the provider minimum and is a breaking change from v2.x.
2. **Default to `repository_type = "private"`**; use `"public"` only when the user explicitly wants a Public ECR Gallery-listed image.
3. **Prefer `repository_policy_statements` over a hand-written `repository_policy` JSON string** when generating custom access rules — it's structurally validated Terraform, not a string blob.
4. **Always set a lifecycle policy** (`repository_lifecycle_policy`) for any repository the agent creates; an unset policy leaves images accumulating indefinitely.
5. **Use `IMMUTABLE` tag mutability by default** (the module default); switch to `*_WITH_EXCLUSION` only for repositories that need a few mutable tags (e.g., `latest`, `dev-*`).
6. **Use `create_repository = false`** for module calls whose only purpose is registry-level configuration (registry policy, replication, scanning, pull-through cache) — do not create a throwaway repository just to attach registry resources.
7. **Use the `repository-template` submodule** (`//modules/repository-template`), not the root module, when the goal is to auto-provision many repositories for pull-through cache or replication by prefix.
8. **Never set `repository_force_delete = true`** on a repository the agent believes is production.
9. **Remember `attach_repository_policy` only controls the private-repository policy resource** — public repositories always get a policy attached when `create_repository = true`.
10. **Enable registry-wide `ENHANCED` scanning** (`manage_registry_scanning_configuration = true`, `registry_scan_type = "ENHANCED"`) for any workload where the user mentions security, compliance, or vulnerability scanning.
