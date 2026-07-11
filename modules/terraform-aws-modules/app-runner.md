# Terraform AWS App Runner Module

## Module Information

- **Module Name**: `app-runner`
- **Source**: `terraform-aws-modules/app-runner/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-app-runner
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/app-runner/aws/latest
- **Latest Version**: 1.2.2 (Terraform >= 1.0, AWS Provider >= 4.51)
- **Purpose**: Terraform module that creates and configures AWS App Runner services, auto-scaling configurations, VPC networking, IAM roles, custom domains, and observability for deploying containerized web applications
- **Service**: AWS App Runner (Fully Managed Container Application Service)
- **Category**: Compute, Serverless, Container Orchestration
- **⚠️ Service Status**: AWS closed App Runner to **new customers as of April 30, 2026**. Only AWS accounts that already used App Runner before that date can create new services; AWS plans no new features and recommends **Amazon ECS Express Mode** for new container deployments. See [Important Notes](#important-gotchas) before using this module for a brand-new account or workload.
- **Keywords**: app-runner, container, serverless, paas, auto-scaling, github, ecr, vpc-connector, custom-domain, observability, ci-cd, web-application, deprecated, ecs-express-mode
- **Use For**: deploying containerized web APIs and microservices on *existing* App Runner-enabled accounts, code-based deployments that auto-build from GitHub on commit, image-based deployments from ECR, private internal services reachable only from a VPC, egress connectivity to RDS/ElastiCache via VPC Connector, custom-domain public APIs with managed TLS, multi-service architectures sharing GitHub connections and auto-scaling configurations, migrating legacy VM workloads to managed containers without adopting ECS/EKS

## Description

AWS App Runner is a fully managed container application service that builds, deploys, scales, and load-balances containerized web applications and APIs directly from source code or container images, without requiring users to provision servers, clusters, or orchestration infrastructure. **AWS closed App Runner to new customers on April 30, 2026** — existing App Runner customers can continue creating and managing services normally and this module remains fully functional for them, but AWS does not plan further feature investment and is directing new workloads toward Amazon ECS Express Mode. Confirm the target AWS account already has App Runner access before generating new infrastructure with this module.

For accounts that can still use the service, this module provides a declarative Terraform interface over App Runner's two deployment models: code-based services that connect to a GitHub repository via an `aws_apprunner_connection` and rebuild automatically on commit, and image-based services that deploy pre-built container images from Amazon ECR (private or public). It manages instance sizing (CPU/memory), request-based auto-scaling configurations, health checks, and two distinct IAM roles — an access role used by App Runner to pull code or private ECR images, and an instance role used by the running application for AWS API calls — both supporting custom policy attachments and permissions boundaries.

The module also covers App Runner's networking and platform integrations: VPC Connectors for egress to private resources such as RDS or ElastiCache, VPC Ingress Connections for making a service reachable only from within a VPC, custom domain associations with ACM-backed certificate validation, KMS encryption configuration, and AWS X-Ray observability. Reusable top-level resources — GitHub `connections` and named `auto_scaling_configurations` — can be created once (with `create_service = false`) and shared by reference (ARN) across multiple service module calls, a common pattern for multi-service architectures. The module has no submodules; every resource is created in the root module and toggled through `create_*` feature flags.

## Key Features

- **Code-based Deployments**: Connects to a GitHub repository via a managed connection and auto-builds/deploys on commit
- **Image-based Deployments**: Deploys pre-built container images from private or public Amazon ECR repositories
- **Auto-scaling Configurations**: Request-based scaling with configurable min/max instance count and max concurrency; definable once and shared across services
- **Instance Configuration**: CPU and memory sizing per service, expressed in App Runner's vCPU/MB units
- **VPC Connector**: Egress connectivity from the service to private VPC resources (RDS, ElastiCache, internal APIs)
- **VPC Ingress Connection**: Restricts a service to be reachable only from within specified VPCs (no public endpoint)
- **Custom Domain Association**: Associates a custom domain and returns the ACM certificate validation CNAME records
- **Dual IAM Roles**: Separate, independently configurable access role (image/code pull) and instance role (runtime permissions), each supporting custom policy statements and permissions boundaries
- **Health Check Configuration**: Configurable path, protocol, interval, timeout, and healthy/unhealthy thresholds
- **X-Ray Observability**: Optional observability configuration for distributed tracing, enabled by default
- **Encryption Configuration**: Optional KMS key for encrypting service configuration and data
- **Secrets Integration**: `runtime_environment_secrets` wires AWS Secrets Manager or SSM Parameter Store values into the container as environment variables
- **Shared Connections & Configs**: Create GitHub connections and auto-scaling configurations independently of any service (`create_service = false`) and reference them by ARN from multiple service instances
- **Conditional Resource Creation**: Fine-grained `create_*` flags for the service, each IAM role, VPC connector, ingress connection, and custom domain association
- **No Submodules**: All functionality lives in the root module behind feature flags — simple to reason about and compose

## Main Use Cases

1. **Serverless Web APIs**: Deploy RESTful or GraphQL APIs without managing servers or container orchestration
2. **Microservices Architecture**: Run independently scaling containerized services, optionally sharing auto-scaling configs
3. **GitHub-driven CI/CD**: Auto-deploy on every commit to a connected repository without a separate build pipeline
4. **Internal Tools**: Deploy VPC Ingress-only services for internal team applications with no public exposure
5. **Multi-tenant SaaS**: Provision isolated App Runner services per tenant with dedicated scaling and networking
6. **Rapid Prototyping**: Stand up a containerized proof-of-concept quickly on an already-eligible account
7. **Database-backed Services**: Use a VPC Connector for egress to RDS, ElastiCache, or other private VPC resources
8. **Custom-domain Public APIs**: Serve production traffic on a branded domain with automatic TLS validation

## Submodules

This module has **no submodules**. All resources — service, auto-scaling configuration, VPC connector, VPC ingress connection, custom domain association, access/instance IAM roles, observability configuration, and connections — are created directly in the root module and toggled via `create_*` feature flags.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether any resources are created |
| `create_service` | `bool` | `true` | Controls whether the App Runner service itself is created (set `false` for shared connections/auto-scaling-config-only calls) |
| `service_name` | `string` | `""` | Name of the App Runner service (required when `create_service = true`) |
| `source_configuration` | `any` | `{}` | Source configuration: either `code_repository` (GitHub) or `image_repository` (ECR) block |
| `auto_scaling_configuration_arn` | `string` | `null` | ARN of an existing auto-scaling configuration to associate; App Runner's default is used if omitted |
| `instance_configuration` | `any` | `{}` | Instance `cpu`/`memory` sizing for the service |
| `health_check_configuration` | `any` | `{}` | Health check path, protocol, interval, timeout, thresholds |
| `network_configuration` | `any` | `{}` | Ingress (`is_publicly_accessible`) and egress (`egress_type`, VPC connector ARN) configuration |
| `encryption_configuration` | `any` | `{}` | KMS key ARN for encrypting service data |
| `observability_configuration` | `any` | `{}` | X-Ray observability configuration reference |
| `create_access_iam_role` | `bool` | `false` | Create the IAM role App Runner uses to pull private code/images |
| `private_ecr_arn` | `string` | `null` | ARN of a private ECR repository to grant the access role pull permissions on |
| `access_iam_role_policies` | `map(string)` | `{}` | Additional IAM policy ARNs to attach to the access role |
| `create_instance_iam_role` | `bool` | `true` | Create the IAM role assumed by the running application |
| `instance_iam_role_policies` | `map(string)` | `{}` | Additional IAM policy ARNs to attach to the instance role |
| `instance_policy_statements` | `any` | `{}` | Map of inline IAM policy statements for custom instance-role permissions |
| `create_vpc_connector` | `bool` | `false` | Create a VPC Connector for egress to private VPC resources |
| `vpc_connector_subnets` | `list(string)` | `[]` | Subnets for the VPC Connector (private subnets with NAT/internet route) |
| `vpc_connector_security_groups` | `list(string)` | `[]` | Security groups for the VPC Connector |
| `create_ingress_vpc_connection` | `bool` | `false` | Create a VPC Ingress Connection to restrict the service to private access |
| `ingress_vpc_id` | `string` | `""` | VPC ID for the ingress configuration |
| `ingress_vpc_endpoint_id` | `string` | `""` | VPC endpoint ID (`com.amazonaws.<region>.apprunner.requests`) for the ingress configuration |
| `create_custom_domain_association` | `bool` | `false` | Create a custom domain association |
| `domain_name` | `string` | `""` | Custom domain (base or subdomain) to associate |
| `enable_www_subdomain` | `bool` | `null` | Also associate the `www` subdomain (App Runner default is `true`) |
| `connections` | `any` | `{}` | Map of reusable connection definitions (e.g., GitHub) to create |
| `auto_scaling_configurations` | `any` | `{}` | Map of reusable auto-scaling configuration definitions (`max_concurrency`, `max_size`, `min_size`) to create |
| `enable_observability_configuration` | `bool` | `true` | Create and assign an X-Ray observability configuration |
| `tags` | `map(string)` | `{}` | Tags to add to all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `service_arn` | ARN of the App Runner service |
| `service_id` | Unique alphanumeric ID generated by App Runner |
| `service_url` | Full HTTPS URL to access the service |
| `service_status` | Current state of the App Runner service |
| `access_iam_role_arn` / `access_iam_role_name` | Identifiers of the access IAM role |
| `instance_iam_role_arn` / `instance_iam_role_name` | Identifiers of the instance IAM role |
| `vpc_connector_arn` | ARN of the VPC connector |
| `vpc_connector_status` | Current state of the VPC connector |
| `vpc_ingress_connection_arn` | ARN of the VPC Ingress Connection |
| `vpc_ingress_connection_domain_name` | Domain name associated with the VPC Ingress Connection |
| `custom_domain_association_id` | `domain_name` and `service_arn` separated by a comma |
| `custom_domain_association_certificate_validation_records` | CNAME records to create in DNS for certificate validation |
| `custom_domain_association_dns_target` | App Runner subdomain that the custom domain should map to |
| `connections` | Map of attribute maps for all connections created |
| `auto_scaling_configurations` | Map of attribute maps for all auto-scaling configurations created |
| `observability_configuration_arn` | ARN of the observability configuration |

## Usage Examples

### Example 1: Shared Configurations (Connections and Auto-Scaling)

```hcl
module "app_runner_shared_configs" {
  source  = "terraform-aws-modules/app-runner/aws"
  version = "~> 1.2"

  create_service = false

  connections = {
    github = {
      provider_type = "GITHUB"
    }
  }

  auto_scaling_configurations = {
    mini = {
      name            = "mini"
      max_concurrency = 20
      max_size        = 5
      min_size        = 1
    }
  }

  tags = {
    Environment = "dev"
  }
}
```

### Example 2: Code Repository-Based Service (GitHub)

```hcl
module "app_runner_code_base" {
  source  = "terraform-aws-modules/app-runner/aws"
  version = "~> 1.2"

  service_name = "example-code-base"

  auto_scaling_configuration_arn = module.app_runner_shared_configs.auto_scaling_configurations["mini"].arn

  source_configuration = {
    authentication_configuration = {
      connection_arn = module.app_runner_shared_configs.connections["github"].arn
    }
    auto_deployments_enabled = false
    code_repository = {
      code_configuration = {
        configuration_source = "REPOSITORY"
      }
      repository_url = "https://github.com/aws-containers/hello-app-runner"
      source_code_version = {
        type  = "BRANCH"
        value = "main"
      }
    }
  }

  tags = {
    Environment = "dev"
  }
}
```

> **Note**: After Terraform creates a GitHub `connection`, you must manually complete the OAuth handshake in the App Runner console before it can be used by a service.

### Example 3: Image-Based Service with VPC Connector

```hcl
module "app_runner_image_base" {
  source  = "terraform-aws-modules/app-runner/aws"
  version = "~> 1.2"

  service_name = "example-image-base"

  instance_policy_statements = {
    GetSecretValue = {
      actions   = ["secretsmanager:GetSecretValue"]
      resources = [aws_secretsmanager_secret.this.arn]
    }
  }

  source_configuration = {
    auto_deployments_enabled = false
    image_repository = {
      image_configuration = {
        port = 8000
        runtime_environment_variables = {
          MY_VARIABLE = "hello!"
        }
        runtime_environment_secrets = {
          MY_SECRET = aws_secretsmanager_secret.this.arn
        }
      }
      image_identifier      = "public.ecr.aws/aws-containers/hello-app-runner:latest"
      image_repository_type = "ECR_PUBLIC"
    }
  }

  create_vpc_connector          = true
  vpc_connector_subnets         = ["subnet-abcde012", "subnet-bcde012a"]
  vpc_connector_security_groups = ["sg-12345678"]

  network_configuration = {
    egress_configuration = {
      egress_type = "VPC"
    }
  }

  enable_observability_configuration = true

  tags = {
    Environment = "dev"
  }
}
```

### Example 4: Private Service (VPC Ingress + Egress)

```hcl
module "app_runner_private" {
  source  = "terraform-aws-modules/app-runner/aws"
  version = "~> 1.2"

  service_name = "example-private"

  source_configuration = {
    auto_deployments_enabled = false
    image_repository = {
      image_configuration = {
        port = 8080
      }
      image_identifier      = "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest"
      image_repository_type = "ECR"
    }
  }

  # Access role for private ECR
  create_access_iam_role = true
  private_ecr_arn        = "arn:aws:ecr:us-east-1:123456789012:repository/my-app"

  # Ingress (private access only via VPC endpoint)
  create_ingress_vpc_connection = true
  ingress_vpc_id                = "vpc-12345678"
  ingress_vpc_endpoint_id       = "vpce-01234567890123456"

  # Egress (VPC connector for private resources)
  create_vpc_connector          = true
  vpc_connector_subnets         = ["subnet-abcde012", "subnet-bcde012a"]
  vpc_connector_security_groups = ["sg-12345678"]

  network_configuration = {
    ingress_configuration = {
      is_publicly_accessible = false
    }
    egress_configuration = {
      egress_type = "VPC"
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 5: Service with Custom Domain

```hcl
module "app_runner_with_domain" {
  source  = "terraform-aws-modules/app-runner/aws"
  version = "~> 1.2"

  service_name = "example-api"

  source_configuration = {
    auto_deployments_enabled = false
    image_repository = {
      image_configuration = {
        port = 8080
      }
      image_identifier      = "public.ecr.aws/aws-containers/hello-app-runner:latest"
      image_repository_type = "ECR_PUBLIC"
    }
  }

  instance_configuration = {
    cpu    = "1024" # 1 vCPU
    memory = "2048" # 2 GB
  }

  health_check_configuration = {
    healthy_threshold   = 1
    interval            = 10
    path                = "/health"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 5
  }

  create_custom_domain_association = true
  domain_name                      = "api.example.com"
  enable_www_subdomain             = false

  tags = {
    Environment = "production"
  }
}

# DNS validation records (output from module)
# Use custom_domain_association_certificate_validation_records
# to create Route53 CNAME records for certificate validation
```

## Best Practices

### Service & Instance Configuration
1. **Right-size Instances**: Start with the smallest CPU/memory pair that meets load-test results; only specific CPU/memory pairs are valid (e.g., 0.25 vCPU pairs with 0.5–2 GB, 1 vCPU with 2–4+ GB) — verify against the current AWS App Runner instance-configuration matrix before hardcoding values
2. **Stateless Design**: Keep application instances stateless; use RDS, DynamoDB, or ElastiCache for session/shared state, since instances are replaced during deploys and scaling events
3. **Graceful Shutdown**: Handle `SIGTERM` so in-flight requests complete before App Runner replaces an instance
4. **Port Alignment**: Ensure the container listens on the port declared in `image_configuration.port` / `code_configuration`
5. **Health Check Design**: Point the health check at a lightweight endpoint that validates critical dependencies without heavy computation
6. **Auto-deployments**: Set `auto_deployments_enabled = true` only when you want every push/image tag update to trigger an automatic redeploy; keep `false` for controlled releases via CI/CD

### Auto-scaling Strategy
1. **Understand the Knobs**: `max_concurrency` triggers scale-out per instance, `max_size` caps instance count, `min_size` sets the always-provisioned floor
2. **Reserve Capacity Cost Model**: Instances between the active count and `min_size` sit as a warm reserve — you pay for their memory but not their CPU, so a higher `min_size` improves cold-start latency at a partial cost, not the full instance cost
3. **Share Configurations Deliberately**: Define `auto_scaling_configurations` once with `create_service = false` and reference the ARN from multiple services that should share scaling behavior
4. **Load Test Before Tuning**: Set `max_concurrency` based on measured per-instance capacity, not a guess; too high delays scale-out, too low over-provisions
5. **Cost vs Availability**: Use `min_size = 0` (via a dedicated low-cost configuration) for dev/test; use `min_size >= 2` for production availability

### Networking (VPC Connector & Ingress)
1. **VPC Connector for Egress Only**: Use `create_vpc_connector` when the service must reach RDS, ElastiCache, or other private VPC/on-prem resources; it is not required for public-only services
2. **NAT/Route Requirement**: Subnets passed to `vpc_connector_subnets` need a route to any required internet destinations (e.g., NAT Gateway) since App Runner does not provide one
3. **Multi-AZ Subnets**: Provide subnets across multiple availability zones for VPC connector resiliency
4. **VPC Ingress Prerequisite**: `create_ingress_vpc_connection` requires an existing VPC endpoint for `com.amazonaws.<region>.apprunner.requests`; create it before or alongside this module
5. **Security Group Scoping**: Restrict `vpc_connector_security_groups` to only the ports/CIDRs the application actually needs to reach

### Security
1. **Least-privilege Instance Role**: Grant `instance_policy_statements` / `instance_iam_role_policies` only the permissions the application needs at runtime
2. **Secrets, Not Env Vars**: Use `runtime_environment_secrets` (Secrets Manager/SSM) for credentials instead of plain-text `runtime_environment_variables`
3. **Private Images in Production**: Prefer `ECR` (private) over `ECR_PUBLIC` for production images, and set `create_access_iam_role` + `private_ecr_arn` for pull permissions
4. **Private Services**: Combine `create_ingress_vpc_connection` with `is_publicly_accessible = false` for internal-only applications
5. **Permissions Boundaries**: Set `access_iam_role_permissions_boundary` / `instance_iam_role_permissions_boundary` where organizational policy requires them
6. **Encrypt Sensitive Configs**: Set `encryption_configuration` with a customer-managed KMS key when compliance requires encryption beyond the AWS-managed default
7. **HTTPS by Default**: App Runner terminates TLS for you; custom domains additionally require ACM validation via the module's certificate-validation output

### Observability & Cost
1. **Enable X-Ray in Production**: Keep `enable_observability_configuration = true` for distributed tracing; disable for low-value dev/test services to reduce noise
2. **CloudWatch Log Retention**: App Runner ships logs to CloudWatch automatically — set a retention policy on the created log groups to control storage cost
3. **Scale-to-zero for Non-prod**: Use a dedicated low-`min_size` auto-scaling configuration for development environments
4. **Consolidate Behind One Domain**: For many small services, evaluate whether a shared connection/auto-scaling-config pattern reduces duplicated resource overhead

## Additional Resources

- **⚠️ AWS App Runner Availability Change & ECS Express Mode Migration Guide**: https://docs.aws.amazon.com/apprunner/latest/dg/apprunner-availability-change.html
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-app-runner
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/app-runner/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-app-runner/tree/master/examples
- **AWS App Runner Developer Guide**: https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html
- **App Runner Source Configuration**: https://docs.aws.amazon.com/apprunner/latest/dg/service-source-code.html
- **App Runner VPC Networking**: https://docs.aws.amazon.com/apprunner/latest/dg/network.html
- **App Runner Auto-scaling**: https://docs.aws.amazon.com/apprunner/latest/dg/manage-autoscaling.html
- **App Runner Custom Domains**: https://docs.aws.amazon.com/apprunner/latest/dg/manage-custom-domains.html
- **App Runner Security**: https://docs.aws.amazon.com/apprunner/latest/dg/security.html
- **Amazon ECS Express Mode (recommended for new deployments)**: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/express-getting-started-console.html

## Important Gotchas

- **⚠️ Closed to New Customers**: AWS announced on March 31, 2026 that App Runner would stop accepting new customers effective April 30, 2026. Existing customers keep full functionality (including creating new services), but AWS plans no new App Runner features and is steering new workloads to Amazon ECS Express Mode. The Terraform AWS provider maintainers have flagged eventual removal of all `aws_apprunner_*` resources in a future major version once App Runner reaches end of support (tracked in `hashicorp/terraform-provider-aws#47162`) — pin provider versions carefully for long-lived App Runner deployments.
- **No Submodules**: All functionality is in the root module, controlled by `create_*` flags.
- **GitHub Connection Handshake**: A GitHub `connection` created by Terraform is left in `PENDING_HANDSHAKE` state until a human completes OAuth authorization in the App Runner console; automation cannot fully replace this manual step.
- **VPC Connector Networking**: VPC connector subnets need their own route to any required internet destinations (e.g., a NAT Gateway); App Runner does not provide one.
- **VPC Ingress Prerequisite**: Requires a pre-existing VPC endpoint for `com.amazonaws.<region>.apprunner.requests`.

## Notes for AI Agents

When using this module in automated workflows:

1. **Check Eligibility First**: Before generating *new* App Runner infrastructure, confirm the target AWS account already had App Runner access before April 30, 2026. For brand-new accounts/workloads, tell the user App Runner is closed to new customers and propose Amazon ECS Express Mode (or ECS/Fargate) instead, unless they explicitly confirm the account is already eligible.
2. **Deployment Model Selection**: Use `code_repository` for GitHub-connected services needing build-on-commit; use `image_repository` for pre-built containers from ECR.
3. **Instance Sizing**: Start around 1 vCPU / 2 GB for typical web APIs and adjust from load-test data; only specific CPU/memory pairs are valid — do not invent arbitrary combinations.
4. **Auto-scaling Defaults**: A reasonable production starting point is `min_size = 2`, `max_size = 10`, `max_concurrency = 100`; use `min_size = 0` for non-production via a separate shared configuration.
5. **VPC Networking**: Only add `create_vpc_connector` when the service needs to reach private VPC resources (RDS, ElastiCache, internal APIs); skip it for purely public services.
6. **IAM Roles**: Create the access role only when pulling from a private ECR repo or a code repository; always create the instance role and scope `instance_policy_statements` to least privilege.
7. **Secrets**: Wire credentials through `runtime_environment_secrets` (Secrets Manager/SSM ARNs), never through plain `runtime_environment_variables`.
8. **GitHub Connections**: Remind the user that a manual console step is required after `terraform apply` to complete the OAuth handshake before a code-based service can build.
9. **Custom Domains**: When `create_custom_domain_association = true`, surface `custom_domain_association_certificate_validation_records` so the caller can create the DNS records needed for ACM validation.
10. **Provider Pinning**: Given the announced provider-removal plan for `aws_apprunner_*` resources, pin the AWS provider version explicitly in generated configurations rather than using an open-ended constraint.
