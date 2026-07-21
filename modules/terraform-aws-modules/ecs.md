# Terraform AWS ECS Module

## Module Information

- **Module Name**: `ecs`
- **Module ID**: `terraform-aws-modules/ecs/aws`
- **Source**: `terraform-aws-modules/ecs/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ecs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest
- **Latest Version**: 7.5.0
- **Compatibility**: Terraform >= 1.5.7, AWS provider >= 6.34. Pin `~> 7.0` when generating configs — v7 introduced a unified `capacity_providers` input (replacing the separate v6 `fargate_capacity_providers`/`autoscaling_capacity_providers`) and enabled service autoscaling by default (`desired_count` is ignored unless `enable_autoscaling = false`).
- **Purpose**: Terraform module that creates and manages AWS ECS (Elastic Container Service) clusters, services, task definitions, container definitions, capacity providers, and their supporting IAM roles/security groups
- **Service**: AWS ECS (Elastic Container Service)
- **Category**: Compute, Containers, Orchestration
- **Keywords**: ecs, fargate, containers, cluster, service, task-definition, capacity-provider, autoscaling, service-connect, load-balancer, container-insights, microservices, fargate-spot, managed-instances, express-service
- **Use For**: microservices deployment, containerized REST/GraphQL API backends, containerized web application hosting, batch and scheduled ECS tasks, event-driven container workloads, blue-green/canary service deployments, service-to-service communication via Service Connect, hybrid Fargate/EC2/ECS Managed Instances clusters, rapid API prototyping with express-service

## Description

This module provisions AWS ECS infrastructure through four composable submodules — `cluster`, `service`, `container-definition`, and `express-service` — plus a root/"integrated" module that wires a cluster together with one or more services in a single call. It creates the ECS cluster (`aws_ecs_cluster`), capacity providers (Fargate, Fargate Spot, EC2 Auto Scaling groups, or ECS Managed Instances), ECS services, task definitions, task sets, and all supporting resources: CloudWatch log groups, security groups, and the IAM roles ECS needs (infrastructure role, node role for Managed Instances, task execution role, and task role).

The module intentionally does not try to force a single opinionated pattern. Teams that want one call to stand up a cluster and its services use the root module with a `services` map; teams that need independent lifecycle management (e.g., cluster owned by a platform team, services owned by application teams) call `modules/cluster` and `modules/service` separately, passing the cluster's ARN into the service module's `cluster_arn` input. `modules/container-definition` produces a single container definition object/JSON that can be composed manually into `aws_ecs_task_definition.container_definitions` or reused across services outside of this module. `modules/express-service` wraps the newer `aws_ecs_express_gateway_service` resource for the simplest possible HTTP service deployment (no ALB, no manual target groups) with minimal required inputs.

Since v7.0, service autoscaling is enabled by default and `desired_count` is always ignored by the service and root modules (set `enable_autoscaling = false` to manage a static task count via `desired_count`/`scale`). Container definitions in the `service` and `container-definition` submodules use the raw ECS API shape (camelCase keys like `portMappings`, `logConfiguration`, `healthCheck`, `dependsOn`) rather than snake_case Terraform-style keys — this must be preserved exactly when generating HCL. The module supports Fargate, Fargate Spot, EC2 Auto Scaling, and ECS Managed Instances capacity providers (mixed via `default_capacity_provider_strategy`), Service Connect and VPC Lattice for service-to-service traffic, deployment circuit breaker/canary/linear deployment strategies, and EFS/EBS/Docker/FSx volumes.

## Key Features

- **Composable Architecture**: Root/integrated module for cluster+services in one call, or independent `cluster`/`service`/`container-definition`/`express-service` submodules for decoupled lifecycles
- **Multiple Capacity Provider Types**: Fargate, Fargate Spot, EC2 Auto Scaling groups, and ECS Managed Instances — mixable via a single `capacity_providers` map and `default_capacity_provider_strategy`
- **Full Task/Container Definition Support**: Raw ECS API-shaped container definitions (`portMappings`, `logConfiguration`, `healthCheck`, `dependsOn`, `firelensConfiguration`, `linuxParameters`, `restartPolicy`, etc.)
- **Autoscaling by Default**: Application Auto Scaling target tracking (CPU/memory predefined metrics by default), step scaling, predictive scaling, and scheduled actions for services
- **Deployment Strategies**: Deployment circuit breaker with rollback, canary/linear rolling deployment configuration, lifecycle hooks, and `deployment_controller` overrides
- **Service Connect & VPC Lattice**: Built-in Service Connect namespace/client-alias configuration and VPC Lattice target group association for service mesh-style discovery
- **Load Balancer Integration**: ALB/NLB target group registration per container/port, including blue/green "advanced configuration" for CodeDeploy-style listener rules
- **IAM Role Automation**: Automatically creates and scopes infrastructure role, node role (Managed Instances), task execution role (`AmazonECSTaskExecutionRolePolicy` equivalent + secrets/SSM access), and task role, each independently toggleable and extensible with custom policy statements
- **CloudWatch Logging**: Per-cluster and per-container CloudWatch log groups with configurable class (`STANDARD`/`INFREQUENT_ACCESS`), retention, and KMS encryption; FireLens supported as an alternative log router
- **Volumes**: Docker, EFS, FSx for Windows File Server, and "configured at launch" (Fargate-managed EBS) volume types
- **Security Groups**: Per-cluster (Managed Instances) and per-service security groups with declarative ingress/egress rule maps (referenced SG, CIDR, prefix list)
- **Execute Command / ECS Exec**: Cluster-level execute-command logging configuration and per-service/container `enable_execute_command` for interactive debugging
- **Express Service**: Simplified `aws_ecs_express_gateway_service`-based deployment with automatic execution/task/infrastructure IAM roles, security group, and health-check path — no ALB required
- **Conditional Creation**: `create`/`create_*` flags throughout to skip any sub-resource (cluster, service, task definition, IAM roles, security group) and bring your own existing resource instead

## Main Use Cases

1. **Microservices Platform**: Stand up an ECS cluster with mixed Fargate/Fargate Spot capacity and deploy multiple services with Service Connect for internal discovery
2. **Public API Backend**: Deploy a Fargate service behind an ALB with autoscaling on CPU/memory and a deployment circuit breaker for safe rollouts
3. **Rapid Prototyping**: Use `express-service` to ship an HTTP service with minimal configuration and no load balancer setup
4. **Cost-Optimized Batch/Steady-State Workloads**: Use EC2 Auto Scaling or ECS Managed Instances capacity providers instead of Fargate for cheaper steady-state compute
5. **Sidecar Log Routing**: Attach a FireLens (Fluent Bit) sidecar container alongside the application container for centralized log shipping to Kinesis Firehose/OpenSearch
6. **Stateful Workloads with EFS**: Mount an EFS access point into a task for shared, persistent storage across task replacements
7. **Platform/App Team Separation**: Create the cluster once via `modules/cluster` and let each application team own its own `modules/service` call scoped to that cluster ARN
8. **Reusable Container Definitions**: Build shared container definitions with `modules/container-definition` and compose them into custom `aws_ecs_task_definition` resources outside this module
9. **Blue/Green and Canary Deployments**: Configure `deployment_configuration` with canary/linear strategies and lifecycle hooks, or `deployment_controller` for CodeDeploy-managed rollouts
10. **Multi-Account Service Mesh**: Use VPC Lattice target group configuration on services to expose ECS workloads across accounts/VPCs

## Submodules

### 1. cluster

- **Purpose**: Creates the ECS cluster plus capacity providers (Fargate, Fargate Spot, EC2 ASG, ECS Managed Instances), cluster-level IAM roles, security group, and CloudWatch log group
- **Source**: `terraform-aws-modules/ecs/aws//modules/cluster`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest/submodules/cluster
- **Key Features**: Unified `capacity_providers` map for all provider types, Container Insights toggle, execute-command logging, infrastructure/node/task-exec IAM roles
- **Use Cases**: Standalone cluster provisioning shared across multiple independently-deployed services, EC2/Managed Instances capacity planning

### 2. service

- **Purpose**: Creates an ECS service, its task definition, task set, autoscaling policies, load balancer registrations, and service/task/task-exec IAM roles (Fargate-focused defaults, EC2/EXTERNAL also supported)
- **Source**: `terraform-aws-modules/ecs/aws//modules/service`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest/submodules/service
- **Key Features**: Autoscaling enabled by default (`desired_count` ignored), Service Connect/VPC Lattice configuration, deployment circuit breaker/canary strategies, EFS/EBS/Docker volumes
- **Use Cases**: Deploying an application onto an existing cluster, per-team service ownership, services requiring fine-grained deployment control

### 3. container-definition

- **Purpose**: Produces a single, standalone ECS container definition object/JSON (with its own CloudWatch log group) for composition into task definitions
- **Source**: `terraform-aws-modules/ecs/aws//modules/container-definition`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest/submodules/container-definition
- **Key Features**: CloudWatch logging enabled by default, FireLens support, read-only root filesystem by default, restart policy support
- **Use Cases**: Building reusable/shared container definitions, sidecar containers (e.g., Fluent Bit), manually assembling multi-container task definitions

### 4. express-service

- **Purpose**: Simplified ECS service deployment built on `aws_ecs_express_gateway_service`, with automatic execution/task/infrastructure IAM roles, security group, and scaling target — no manual ALB/target group wiring
- **Source**: `terraform-aws-modules/ecs/aws//modules/express-service`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest/submodules/express-service
- **Key Features**: Single `primary_container` block, built-in `/ping`-style health check path, automatic ingress paths and service URL output
- **Use Cases**: Rapid prototyping, simple HTTP APIs that don't need a dedicated load balancer, workshops/demos

## Root Module (Integrated Cluster + Services)

### Description

The root module (`terraform-aws-modules/ecs/aws`) wraps `modules/cluster` and `modules/service` to create a cluster and any number of services in one call via the `services` map. Internally it simply calls the `cluster` submodule once and the `service` submodule once per entry in `services`, passing through the cluster ARN. Its inputs are the union of the cluster submodule's inputs (cluster-scoped, e.g. `cluster_name`, `capacity_providers`) plus a `services` map whose value object mirrors nearly every input of the `service` submodule (container definitions, load balancer, autoscaling, IAM roles, security group, volumes, etc.).

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created (affects all resources) |
| `cluster_name` | `string` | `""` | Name of the cluster (up to 255 letters, numbers, hyphens, underscores) |
| `cluster_configuration` | `object` | execute-command logging enabled | Execute-command and managed-storage configuration for the cluster — fields: `execute_command_configuration`, `managed_storage_configuration` |
| `cluster_setting` | `list(object({name,value}))` | `[{name="containerInsights", value="enabled"}]` | Cluster settings block; commonly used to toggle Container Insights |
| `capacity_providers` | `map(object)` | `null` | Map of capacity provider definitions (`auto_scaling_group_provider` or `managed_instances_provider`) to create for the cluster |
| `cluster_capacity_providers` | `list(string)` | `[]` | Capacity provider names to associate with the cluster (e.g. `["FARGATE", "FARGATE_SPOT"]`); providers created above are auto-added |
| `default_capacity_provider_strategy` | `map(object({base,weight,name}))` | `null` | Default capacity provider strategy for the cluster |
| `create_cloudwatch_log_group` | `bool` | `true` | Whether to create the cluster's CloudWatch log group |
| `cloudwatch_log_group_retention_in_days` | `number` | `90` | Retention for the cluster log group |
| `services` | `map(object)` | `null` | Map of service definitions to create; each value mirrors the `service` submodule's inputs (see below) |
| `vpc_id` | `string` | `null` | VPC ID for the (cluster-level, Managed Instances) security group |
| `security_group_ingress_rules` / `security_group_egress_rules` | `map(object)` | egress: allow-all | Security group rules for the cluster-level security group — fields: `name`, `cidr_ipv4`, `cidr_ipv6`, `description`, `from_port`, `ip_protocol`, `prefix_list_id`, `referenced_security_group_id`, … (8 shown; call get_module with sections=["inputs","outputs"] for the complete list) |
| `create_task_exec_iam_role` | `bool` | `false` (root) | Whether to create a shared task execution IAM role at the cluster level (per-service roles are created by default instead) |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

### Key Outputs

| Output | Description |
|--------|-------------|
| `cluster_arn` | ARN of the ECS cluster |
| `cluster_id` | ID of the ECS cluster |
| `cluster_name` | Name of the ECS cluster |
| `cluster_capacity_providers` | Map of capacity providers attached to the cluster |
| `services` | Map of created services and their attributes (task definition ARN, IAM role ARNs, security group ID, etc.) |
| `task_exec_iam_role_arn` | ARN of the cluster-level task execution IAM role (if created) |

### Usage Example

```hcl
module "ecs" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "~> 7.5"

  cluster_name = "ecs-integrated"

  cluster_configuration = {
    execute_command_configuration = {
      logging = "OVERRIDE"
      log_configuration = {
        cloud_watch_log_group_name = "/aws/ecs/ecs-integrated"
      }
    }
  }

  # Mix Fargate and Fargate Spot
  cluster_capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  default_capacity_provider_strategy = {
    FARGATE = {
      weight = 50
      base   = 20
    }
    FARGATE_SPOT = {
      weight = 50
    }
  }

  services = {
    ecsdemo-frontend = {
      cpu    = 1024
      memory = 4096

      # Container definition(s) - keys follow the raw ECS API shape
      container_definitions = {
        ecs-sample = {
          cpu       = 512
          memory    = 1024
          essential = true
          image     = "public.ecr.aws/aws-containers/ecsdemo-frontend:776fd50"
          portMappings = [
            {
              name          = "ecs-sample"
              containerPort = 80
              protocol      = "tcp"
            }
          ]
          readonlyRootFilesystem = false
        }
      }

      load_balancer = {
        service = {
          target_group_arn = aws_lb_target_group.this.arn
          container_name   = "ecs-sample"
          container_port   = 80
        }
      }

      subnet_ids = module.vpc.private_subnets

      security_group_ingress_rules = {
        alb_http = {
          description                  = "Service port"
          from_port                    = 80
          ip_protocol                  = "tcp"
          referenced_security_group_id = module.alb.security_group_id
        }
      }
      security_group_egress_rules = {
        all = {
          ip_protocol = "-1"
          cidr_ipv4   = "0.0.0.0/0"
        }
      }
    }
  }

  tags = {
    Environment = "production"
    Project     = "example"
  }
}
```

## Submodule 1: cluster

### Description

Creates the `aws_ecs_cluster` resource plus capacity providers, the cluster's execute-command CloudWatch log group, the ECS infrastructure IAM role, and (for ECS Managed Instances) the node IAM role/instance profile and security group. Use this submodule directly when the cluster's lifecycle is managed separately from the services deployed onto it (e.g., a platform team owns the cluster, application teams own their own `service` submodule calls).

### Key Features

- Single `capacity_providers` map supports EC2 Auto Scaling groups (`auto_scaling_group_provider`) and ECS Managed Instances (`managed_instances_provider`) side by side
- `cluster_capacity_providers` + `default_capacity_provider_strategy` to also enable/weight `FARGATE`/`FARGATE_SPOT`
- Container Insights enabled by default via `setting`
- Execute-command (ECS Exec) CloudWatch/S3 logging configuration
- Managed-instances node IAM role, instance profile, and dedicated security group with declarative ingress/egress rule maps
- Infrastructure IAM role for cluster-managed load balancer/EBS/VPC Lattice attachment operations

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the cluster (up to 255 letters, numbers, hyphens, underscores) |
| `configuration` | `object` | execute-command logging enabled | Execute-command and managed-storage configuration for the cluster — fields: `execute_command_configuration`, `managed_storage_configuration` |
| `setting` | `list(object({name,value}))` | `[{name="containerInsights", value="enabled"}]` | Cluster settings (Container Insights, etc.) |
| `capacity_providers` | `map(object)` | `null` | Map of capacity provider definitions (`auto_scaling_group_provider` / `managed_instances_provider`) to create |
| `cluster_capacity_providers` | `list(string)` | `[]` | Capacity provider names associated with the cluster (e.g. Fargate/Fargate Spot) |
| `default_capacity_provider_strategy` | `map(object({base,weight,name}))` | `{}` | Default strategy across all capacity providers |
| `create_cloudwatch_log_group` | `bool` | `true` | Whether to create a log group for cluster/execute-command logs |
| `cloudwatch_log_group_retention_in_days` | `number` | `90` | Log retention in days |
| `create_infrastructure_iam_role` | `bool` | `true` | Whether to create the ECS infrastructure IAM role |
| `create_node_iam_instance_profile` | `bool` | `true` | Whether to create the Managed Instances node instance profile |
| `create_security_group` | `bool` | `true` | Whether to create a security group (Managed Instances) |
| `vpc_id` | `string` | `null` | VPC ID for the security group |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

### Key Outputs

| Output | Description |
|--------|-------------|
| `arn` | ARN of the cluster |
| `id` | ID of the cluster |
| `name` | Name of the cluster |
| `cluster_capacity_providers` | Map of capacity providers attached to the cluster |
| `capacity_providers` | Map of capacity providers created and their attributes |
| `infrastructure_iam_role_arn` | ARN of the ECS infrastructure IAM role |
| `node_iam_instance_profile_arn` | ARN of the Managed Instances node instance profile |

### Usage Examples

#### Example 1: Fargate + Fargate Spot cluster

```hcl
module "ecs_cluster" {
  source  = "terraform-aws-modules/ecs/aws//modules/cluster"
  version = "~> 7.5"

  name = "ecs-fargate"

  configuration = {
    execute_command_configuration = {
      logging = "OVERRIDE"
      log_configuration = {
        cloud_watch_log_group_name = "/aws/ecs/ecs-fargate"
      }
    }
  }

  cluster_capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  default_capacity_provider_strategy = {
    FARGATE = {
      weight = 50
      base   = 20
    }
    FARGATE_SPOT = {
      weight = 50
    }
  }

  tags = {
    Environment = "production"
  }
}
```

#### Example 2: EC2 Auto Scaling capacity providers

```hcl
module "ecs_cluster_ec2" {
  source  = "terraform-aws-modules/ecs/aws//modules/cluster"
  version = "~> 7.5"

  name = "ecs-ec2"

  default_capacity_provider_strategy = {
    one = {
      weight = 60
      base   = 20
    }
  }

  capacity_providers = {
    one = {
      auto_scaling_group_provider = {
        auto_scaling_group_arn         = aws_autoscaling_group.ecs.arn
        managed_draining               = "ENABLED"
        managed_termination_protection = "ENABLED"

        managed_scaling = {
          maximum_scaling_step_size = 5
          minimum_scaling_step_size = 1
          status                    = "ENABLED"
          target_capacity           = 60
        }
      }
    }
  }

  tags = {
    Environment = "production"
    ComputeType = "ec2"
  }
}
```

## Submodule 2: service

### Description

Creates an ECS service, its task definition (or task set, for external deployment controllers), autoscaling policies/scheduled actions, load balancer target group registrations, Service Connect/VPC Lattice configuration, and the service/task/task-execution IAM roles and security group. **`desired_count`/`scale` is always ignored** — the module manages capacity through Application Auto Scaling by default (disable with `enable_autoscaling = false`). Defaults target `FARGATE`; set `launch_type` and `requires_compatibilities` for EC2/EXTERNAL.

### Key Features

- Task definition with full raw-ECS-API container definitions (`container_definitions` map, each value shaped like the ECS `ContainerDefinition` API object)
- Autoscaling enabled by default with predefined CPU/memory target-tracking policies; also supports step scaling, predictive scaling, and scheduled actions
- `load_balancer` map for ALB/NLB target group registration, including blue/green `advanced_configuration` for listener-rule-based deployments
- `service_connect_configuration` and `vpc_lattice_configurations` for service-to-service discovery/traffic
- `deployment_circuit_breaker`, `deployment_configuration` (canary/linear strategies + lifecycle hooks) for safe rollouts
- Separate, independently toggleable IAM roles: service IAM role (load balancer registration), task execution role, and task role
- `volume` block supporting Docker, EFS, FSx for Windows, and Fargate `configure_at_launch` (managed EBS) volumes
- `ignore_task_definition_changes` to let an external CI/CD pipeline manage the running task definition without Terraform drift

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the service |
| `cluster_arn` | `string` | `""` | ARN of the ECS cluster to deploy into |
| `cpu` | `number` | `1024` | Task-level CPU units (required for Fargate) |
| `memory` | `number` | `2048` | Task-level memory in MiB (required for Fargate) |
| `launch_type` | `string` | `"FARGATE"` | `EC2`, `FARGATE`, or `EXTERNAL` |
| `requires_compatibilities` | `list(string)` | `["FARGATE"]` | Launch types required by the task |
| `network_mode` | `string` | `"awsvpc"` | `none`, `bridge`, `awsvpc`, or `host` |
| `container_definitions` | `map(object)` | `{}` | Map of container definitions (raw ECS API shape — `portMappings`, `logConfiguration`, `healthCheck`, `dependsOn`, etc.) |
| `desired_count` | `number` | `1` | Ignored in favor of autoscaling unless `enable_autoscaling = false` |
| `enable_autoscaling` | `bool` | `true` | Whether to create Application Auto Scaling target/policies |
| `autoscaling_min_capacity` / `autoscaling_max_capacity` | `number` | `1` / `10` | Task count bounds for autoscaling |
| `autoscaling_policies` | `map(object)` | CPU + memory target tracking | Autoscaling policies (target tracking, step, or predictive scaling) — fields: `name`, `policy_type`, `predictive_scaling_policy_configuration`, `step_scaling_policy_configuration`, `target_tracking_scaling_policy_configuration` |
| `load_balancer` | `map(object)` | `null` | Target group / container / port mappings for the service — fields: `container_name`, `container_port`, `elb_name`, `target_group_arn`, `advanced_configuration` |
| `service_connect_configuration` | `object` | `null` | Service Connect namespace/client-alias configuration — fields: `enabled`, `access_log_configuration`, `log_configuration`, `namespace`, `service` |
| `deployment_circuit_breaker` | `object({enable,rollback})` | `null` | Automatic rollback on failed deployments |
| `deployment_minimum_healthy_percent` / `deployment_maximum_percent` | `number` | `66` / `200` | Rolling deployment bounds |
| `subnet_ids` | `list(string)` | `[]` | Subnets for `awsvpc` network mode |
| `security_group_ids` | `list(string)` | `[]` | Additional security groups; module also creates its own by default |
| `security_group_ingress_rules` / `security_group_egress_rules` | `map(object)` | `{}` / allow-all | Rules for the service's security group — fields: `name`, `cidr_ipv4`, `cidr_ipv6`, `description`, `from_port`, `ip_protocol`, `prefix_list_id`, `referenced_security_group_id`, … (8 shown; call get_module with sections=["inputs","outputs"] for the complete list) |
| `assign_public_ip` | `bool` | `false` | Assign a public IP to the task ENI (Fargate) |
| `enable_execute_command` | `bool` | `false` | Enable ECS Exec for interactive debugging |
| `volume` | `map(object)` | `null` | Volume definitions (Docker/EFS/FSx/managed EBS) attached to the task — fields: `configure_at_launch`, `docker_volume_configuration`, `efs_volume_configuration`, `fsx_windows_file_server_volume_configuration`, `host_path`, `name` |
| `create_task_exec_iam_role` / `create_tasks_iam_role` | `bool` | `true` | Toggle creation of task execution / task IAM roles |
| `task_exec_iam_role_policies` / `tasks_iam_role_policies` | `map(string)` | `{}` | Extra managed policy ARNs to attach to those roles |
| `task_exec_secret_arns` / `task_exec_ssm_param_arns` | `list(string)` | `[]` | Secrets Manager / SSM ARNs the execution role may read |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

### Key Outputs

| Output | Description |
|--------|-------------|
| `id` | ARN that identifies the service |
| `name` | Name of the service |
| `task_definition_arn` | Full ARN of the task definition (family + revision) |
| `task_definition_family` / `task_definition_revision` | Task definition family name / revision number |
| `iam_role_arn` | Service IAM role ARN (load balancer management) |
| `task_exec_iam_role_arn` | Task execution IAM role ARN |
| `tasks_iam_role_arn` | Task IAM role ARN |
| `security_group_id` | ID of the security group created for the service |
| `autoscaling_policies` | Map of autoscaling policies created |
| `container_definitions` | Rendered container definitions |

### Usage Examples

#### Example 1: Basic Fargate service with ALB

```hcl
module "ecs_service" {
  source  = "terraform-aws-modules/ecs/aws//modules/service"
  version = "~> 7.5"

  name        = "web-application"
  cluster_arn = module.ecs_cluster.arn

  cpu    = 1024
  memory = 2048

  container_definitions = {
    web = {
      image     = "public.ecr.aws/nginx/nginx:latest"
      essential = true

      portMappings = [
        {
          name          = "web"
          containerPort = 80
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "ENVIRONMENT", value = "production" }
      ]

      readonlyRootFilesystem = false
    }
  }

  load_balancer = {
    service = {
      target_group_arn = aws_lb_target_group.web.arn
      container_name   = "web"
      container_port   = 80
    }
  }

  subnet_ids = module.vpc.private_subnets
  security_group_ingress_rules = {
    alb = {
      description                  = "ALB to service"
      from_port                    = 80
      ip_protocol                  = "tcp"
      referenced_security_group_id = module.alb.security_group_id
    }
  }
  security_group_egress_rules = {
    all = {
      ip_protocol = "-1"
      cidr_ipv4   = "0.0.0.0/0"
    }
  }

  # Autoscaling is enabled by default (CPU + memory target tracking).
  autoscaling_min_capacity = 2
  autoscaling_max_capacity = 10

  deployment_circuit_breaker = {
    enable   = true
    rollback = true
  }

  tags = {
    Environment = "production"
    Application = "web"
  }
}
```

#### Example 2: Service with secrets, EFS volume, and Service Connect

```hcl
module "ecs_service" {
  source  = "terraform-aws-modules/ecs/aws//modules/service"
  version = "~> 7.5"

  name        = "api-service"
  cluster_arn = module.ecs_cluster.arn

  cpu    = 2048
  memory = 4096

  enable_execute_command = true

  container_definitions = {
    api = {
      image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/api:latest"

      portMappings = [
        { name = "api", containerPort = 8080, protocol = "tcp" }
      ]

      secrets = [
        {
          name      = "DATABASE_PASSWORD"
          valueFrom = "arn:aws:secretsmanager:us-east-1:123456789012:secret:db-password"
        }
      ]

      mountPoints = [
        {
          sourceVolume  = "efs-storage"
          containerPath = "/mnt/efs"
          readOnly      = false
        }
      ]

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  }

  volume = {
    efs-storage = {
      efs_volume_configuration = {
        file_system_id     = aws_efs_file_system.app_data.id
        transit_encryption = "ENABLED"
        authorization_config = {
          access_point_id = aws_efs_access_point.app.id
          iam             = "ENABLED"
        }
      }
    }
  }

  service_connect_configuration = {
    namespace = "example"
    service = [
      {
        client_alias = {
          port     = 8080
          dns_name = "api"
        }
        port_name      = "api"
        discovery_name = "api"
      }
    ]
  }

  task_exec_secret_arns = [
    "arn:aws:secretsmanager:us-east-1:123456789012:secret:db-password",
  ]

  tasks_iam_role_policies = {
    dynamodb = "arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess"
  }

  subnet_ids = module.vpc.private_subnets

  tags = {
    Environment = "production"
    Service     = "api"
  }
}
```

## Submodule 3: container-definition

### Description

Renders a single ECS container definition (and, by default, its own CloudWatch log group) as both a Terraform object (`container_definition`) and pre-encoded JSON (`container_definition_json`). Useful for building reusable/shared container definitions (e.g., a common FireLens/Fluent Bit sidecar) or for composing `aws_ecs_task_definition.container_definitions` manually outside the `service` submodule.

### Key Features

- CloudWatch Logs integration enabled by default (`enable_cloudwatch_logging = true`); disable for FireLens or other custom log routing
- `readonlyRootFilesystem` defaults to `true` for security
- Container restart policy support (`restartPolicy`) to recover from transient failures faster
- All fields use the raw ECS `ContainerDefinition` API shape (camelCase keys)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `null` | Container name |
| `image` | `string` | `null` | Docker image URI (`repository-url/image:tag` or `@digest`) |
| `cpu` / `memory` / `memoryReservation` | `number` | `null` | Resource allocation for the container |
| `essential` | `bool` | `null` | If `true` and the container fails, all other containers in the task stop |
| `portMappings` | `list(object)` | `null` | Port exposure configuration — fields: `appProtocol`, `containerPort`, `containerPortRange`, `hostPort`, `name`, `protocol` |
| `environment` | `list(object({name,value}))` | `null` | Environment variables |
| `secrets` | `list(object({name,valueFrom}))` | `null` | Secrets Manager/SSM references injected as env vars |
| `readonlyRootFilesystem` | `bool` | `true` | Read-only root filesystem |
| `logConfiguration` | `object` | `{}` | Log driver configuration (defaults to CloudWatch when logging is enabled) — fields: `logDriver`, `options`, `secretOptions` |
| `healthCheck` | `object` | `null` | Container health check command/interval/retries — fields: `command`, `interval`, `retries`, `startPeriod`, `timeout` |
| `firelensConfiguration` | `object` | `null` | FireLens log router configuration — fields: `options`, `type` |
| `enable_cloudwatch_logging` | `bool` | `true` | Set `false` when using FireLens or another log driver |
| `cloudwatch_log_group_retention_in_days` | `number` | `14` | Log retention period |

### Key Outputs

| Output | Description |
|--------|-------------|
| `container_definition` | Container definition as a Terraform object |
| `container_definition_json` | Container definition pre-encoded as JSON (wrap in a list + `jsonencode()` for `aws_ecs_task_definition`) |
| `cloudwatch_log_group_arn` / `cloudwatch_log_group_name` | Log group created for this container |

### Usage Example

```hcl
module "fluentbit" {
  source  = "terraform-aws-modules/ecs/aws//modules/container-definition"
  version = "~> 7.5"

  name      = "fluent-bit"
  cpu       = 512
  memory    = 1024
  essential = true
  image     = "906394416424.dkr.ecr.us-west-2.amazonaws.com/aws-for-fluent-bit:stable"
  firelensConfiguration = {
    type = "fluentbit"
  }
  memoryReservation = 50
}

module "app_container" {
  source  = "terraform-aws-modules/ecs/aws//modules/container-definition"
  version = "~> 7.5"

  name      = "api"
  cpu       = 256
  memory    = 512
  essential = true
  image     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/api:latest"

  portMappings = [
    { containerPort = 8080, protocol = "tcp" }
  ]

  # Ship logs via the Fluent Bit sidecar instead of the default CloudWatch driver
  dependsOn = [
    { containerName = "fluent-bit", condition = "START" }
  ]
  enable_cloudwatch_logging = false
  logConfiguration = {
    logDriver = "awsfirelens"
    options = {
      Name            = "firehose"
      region          = "us-east-1"
      delivery_stream = "my-stream"
    }
  }
}

# Compose into a task definition manually
resource "aws_ecs_task_definition" "app" {
  family                   = "app"
  requires_compatibilities = ["FARGATE"]
  network_mode              = "awsvpc"
  cpu                        = 512
  memory                     = 1024
  container_definitions = jsonencode([
    module.fluentbit.container_definition,
    module.app_container.container_definition,
  ])
}
```

## Submodule 4: express-service

### Description

Deploys an `aws_ecs_express_gateway_service` — a simplified ECS service type that includes an integrated ingress/gateway without requiring a manually configured ALB and target groups. Automatically provisions the execution, task, and infrastructure IAM roles and the service's security group. Best suited for straightforward HTTP services and prototyping rather than services needing custom load balancer routing rules.

### Key Features

- Single `primary_container` block instead of a full `container_definitions` map
- Built-in `health_check_path` (defaults to `/ping`)
- Automatic execution/task/infrastructure IAM role creation, each independently toggleable
- `scaling_target` block for simple min/max task count + target metric autoscaling
- Outputs a ready-to-use `service_url` and `ingress_paths`

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Service name |
| `cluster` | `string` | `null` (`"default"`) | Name or ARN of the ECS cluster to deploy into |
| `cpu` | `string` | `null` | Task CPU units — powers of 2 between `256` and `4096` |
| `memory` | `string` | `null` | Task memory in MiB — between `512` and `8192` |
| `network_configuration` | `object({subnets,security_groups})` | `null` | Subnets (and optional extra security groups) for the task |
| `primary_container` | `object` | `null` | Primary container: `image`, `container_port`, `command`, `environment`, `secret`, `repository_credentials`, `aws_logs_configuration` |
| `scaling_target` | `object({auto_scaling_metric,auto_scaling_target_value,min_task_count,max_task_count})` | `null` | Autoscaling target configuration |
| `health_check_path` | `string` | `null` (`/ping`) | Path used for the service's health check |
| `vpc_id` | `string` | `null` | VPC ID for the security group |
| `security_group_ingress_rules` / `security_group_egress_rules` | `map(object)` | `{}` | Security group rule maps — fields: `name`, `cidr_ipv4`, `cidr_ipv6`, `description`, `from_port`, `ip_protocol`, `prefix_list_id`, `referenced_security_group_id`, … (8 shown; call get_module with sections=["inputs","outputs"] for the complete list) |
| `create_execution_iam_role` / `create_task_iam_role` / `create_infrastructure_iam_role` | `bool` | `true` | Toggle creation of each IAM role |

### Key Outputs

| Output | Description |
|--------|-------------|
| `service_arn` | ARN of the ECS Express Service |
| `service_url` | URL of the deployed service |
| `ingress_paths` | List of ingress paths associated with the service |
| `security_group_id` | ID of the security group created |
| `execution_iam_role_arn` / `task_iam_role_arn` / `infrastructure_iam_role_arn` | ARNs of the automatically created IAM roles |

### Usage Example

```hcl
module "ecs_express_service" {
  source  = "terraform-aws-modules/ecs/aws//modules/express-service"
  version = "~> 7.5"

  name = "my-api"

  cpu    = 1024
  memory = 4096

  network_configuration = {
    subnets = module.vpc.private_subnets
  }

  primary_container = {
    container_port = 3000
    image          = "public.ecr.aws/aws-containers/ecsdemo-frontend:776fd50"
  }

  scaling_target = {
    auto_scaling_metric       = "AVERAGE_CPU"
    auto_scaling_target_value = "80"
    min_task_count            = 1
    max_task_count            = 3
  }

  vpc_id = module.vpc.vpc_id
  security_group_egress_rules = {
    all = {
      ip_protocol = "-1"
      cidr_ipv4   = "0.0.0.0/0"
    }
  }

  tags = {
    Environment = "dev"
  }
}
```

## Best Practices

### Cluster and Capacity Planning
1. **Start with Fargate**: Default to Fargate to eliminate host patching/capacity management; move to EC2 Auto Scaling or ECS Managed Instances only for steady-state cost optimization or specific instance-type/GPU requirements.
2. **Mix Fargate and Fargate Spot**: Split `default_capacity_provider_strategy` (e.g., 50/50 or a Fargate `base` for a guaranteed floor plus Spot for burst) to reduce cost while retaining availability.
3. **Enable Container Insights**: Keep the default `setting`/`cluster_setting` with `containerInsights = enabled` for production clusters.
4. **Separate Clusters per Environment**: Use distinct clusters for dev/staging/production rather than namespacing services within one cluster.
5. **Decide Ownership Early**: Use the root/integrated module when one team owns cluster and services together; use `modules/cluster` + `modules/service` independently when cluster and application teams differ.

### Service Deployment
1. **Always Set CPU/Memory**: Task-level `cpu`/`memory` are required for Fargate and directly affect scheduling — never leave them at guesswork defaults for production.
2. **Enable the Deployment Circuit Breaker**: Set `deployment_circuit_breaker = { enable = true, rollback = true }` so failed deployments roll back automatically.
3. **Keep Autoscaling On**: `enable_autoscaling` defaults to `true` and ignores `desired_count`; only disable it for services needing a fixed task count, and remember to manage capacity another way if you do.
4. **Use Service Connect for Internal Traffic**: Prefer `service_connect_configuration` over manually wiring Cloud Map/ALB rules for service-to-service calls.
5. **Preserve Raw ECS Key Casing**: `container_definitions` fields (`portMappings`, `logConfiguration`, `healthCheck`, `dependsOn`, `mountPoints`, etc.) must use the exact camelCase ECS API key names — snake_case equivalents will not be recognized.

### Security
1. **Separate Execution and Task Roles**: The task execution role is for the ECS agent (pulling images, reading secrets at launch); the task role is for the application's own AWS API calls at runtime — never conflate the two.
2. **Grant Secrets Access Narrowly**: Use `task_exec_secret_arns`/`task_exec_ssm_param_arns` (or `execution_secret_arns` for express-service) to scope exactly which secrets the execution role may read, rather than broad policies.
3. **Default to Read-Only Root Filesystem**: `container-definition`'s `readonlyRootFilesystem` defaults to `true`; only disable it for images that genuinely need to write to their own filesystem.
4. **Keep Tasks in Private Subnets**: Pass private subnets to `subnet_ids`/`network_configuration.subnets` and leave `assign_public_ip = false` (the default) unless the task needs a public IP directly.
5. **Scope Security Group Rules**: Use `referenced_security_group_id` (e.g., pointing at an ALB's security group) in `security_group_ingress_rules` instead of open CIDR ranges.
6. **Restrict ECS Exec**: Only set `enable_execute_command = true` where interactive debugging is genuinely needed, and audit exec sessions via CloudTrail.

### Observability
1. **Set Log Retention Deliberately**: Cluster-level logs default to 90 days, container-definition logs to 14 days — align both with compliance requirements via `cloudwatch_log_group_retention_in_days`.
2. **Encrypt Logs with KMS**: Set `cloudwatch_log_group_kms_key_id` on cluster/service/container-definition log groups for sensitive workloads.
3. **Configure Container Health Checks**: Define `healthCheck` on each container and set `health_check_grace_period_seconds` on the service to avoid premature termination during slow startups.
4. **Use FireLens for Advanced Routing**: When logs need to go beyond CloudWatch (e.g., OpenSearch, Kinesis Firehose), disable `enable_cloudwatch_logging` and add a Fluent Bit sidecar via `firelensConfiguration`.

### Cost Optimization
1. **Combine Fargate Spot with a Guaranteed Base**: Set a small Fargate `base` alongside a larger Fargate Spot `weight` for fault-tolerant workloads.
2. **Right-Size Continuously**: Compare Container Insights CPU/memory utilization against configured `cpu`/`memory` and adjust — over-provisioned tasks are a common source of ECS spend.
3. **Consider EC2/Managed Instances for Steady-State Load**: For predictable, always-on workloads at scale, EC2 Auto Scaling or ECS Managed Instances capacity providers can be cheaper than Fargate.
4. **Scope Autoscaling Bounds**: Set `autoscaling_min_capacity`/`autoscaling_max_capacity` (or `scaling_target.min_task_count`/`max_task_count` for express-service) to realistic baselines and ceilings to avoid runaway scale-out costs.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ecs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest
- **Design Documentation**: https://github.com/terraform-aws-modules/terraform-aws-ecs/blob/master/docs/README.md
- **AWS ECS Developer Guide**: https://docs.aws.amazon.com/ecs/
- **ECS Best Practices Guide**: https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/intro.html
- **AWS Fargate Documentation**: https://docs.aws.amazon.com/AmazonECS/latest/userguide/what-is-fargate.html
- **ECS Service Connect**: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect.html
- **ECS Exec**: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html
- **ECS Service Auto Scaling**: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html
- **Container Insights**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Pick the Right Entry Point**: Root module for cluster+services together; `modules/cluster` + `modules/service` for independently owned lifecycles; `modules/express-service` for the simplest possible HTTP service; `modules/container-definition` only when composing custom `aws_ecs_task_definition` resources by hand.
2. **v7.x Breaking Changes**: `capacity_providers` replaced the separate v6 `fargate_capacity_providers`/`autoscaling_capacity_providers` inputs; autoscaling is on by default and `desired_count`/`scale` is ignored unless `enable_autoscaling = false`.
3. **Container Definitions Use Raw ECS API Keys**: Always camelCase (`portMappings`, `logConfiguration`, `healthCheck`, `mountPoints`, `dependsOn`, `firelensConfiguration`) — do not translate to snake_case.
4. **Fargate Sizing Constraints**: `cpu` must be a power of 2 between 256–4096; `memory` must pair with a valid Fargate CPU/memory combination (typically 512–16384 MiB depending on CPU).
5. **IAM Roles Are Created Per Service by Default**: Extend with `task_exec_iam_role_policies`/`task_exec_iam_statements` (execution role) or `tasks_iam_role_policies`/`tasks_iam_role_statements` (task role) rather than editing generated roles directly.
6. **Container Definition Output Needs `jsonencode()`**: When using the `container-definition` submodule standalone, wrap the output list with `jsonencode()` before passing it to `aws_ecs_task_definition.container_definitions`.
7. **Load Balancer Wiring**: Reference an existing `aws_lb_target_group.arn` in `load_balancer.<key>.target_group_arn`; the module does not create the ALB/target group itself.
8. **Network Mode**: Fargate requires `network_mode = "awsvpc"` (the service submodule default) with `subnet_ids` populated; EC2/`bridge` mode is only relevant for EC2 capacity providers.
9. **Version Pinning**: Pin `~> 7.0` (or the exact minor, e.g. `~> 7.5`) — v6→v7 changed several variable names/shapes as noted above.
