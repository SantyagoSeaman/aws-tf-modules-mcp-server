# Terraform AWS ECS Module

## Module Information

- **Module Name**: `ecs`
- **Source**: `terraform-aws-modules/ecs/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ecs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest
- **Latest Version**: 7.3.0
- **Purpose**: Terraform module that creates AWS ECS (Elastic Container Service) resources including clusters, services, task definitions, and capacity providers
- **Service**: AWS ECS (Elastic Container Service)
- **Category**: Compute, Containers, Orchestration
- **Keywords**: ecs, elastic-container-service, containers, fargate, cluster, service, task-definition, capacity-provider, autoscaling, service-connect, load-balancer, alb, nlb, container-insights, microservices, fargate-spot, ecr, secrets-manager, efs
- **Use For**: Microservices deployment, containerized application hosting, API backend services, batch processing workloads, scheduled tasks, event-driven architectures, container orchestration, scalable web applications, service mesh implementations, continuous deployment pipelines, hybrid workloads with Fargate and EC2

## Description

This comprehensive Terraform module provides a complete solution for deploying and managing AWS Elastic Container Service (ECS) infrastructure, enabling organizations to run containerized applications at scale using either serverless Fargate compute or traditional EC2 instances. The module abstracts the complexity of ECS resource creation while providing granular control over cluster configuration, service definitions, task specifications, capacity providers, and networking. It offers four composable submodules: cluster (infrastructure), service (full-featured deployment), container-definition (reusable container specs), and express-service (simplified deployment). It supports both modern serverless patterns with Fargate and cost-optimized EC2-based deployments with Auto Scaling groups, making it suitable for diverse workload requirements from development environments to production-scale microservices architectures.

The module excels at managing ECS clusters with multiple capacity provider strategies, allowing mixed workloads that combine Fargate, Fargate Spot, and EC2 capacity for optimal cost and performance balance. It provides sophisticated service management capabilities including blue-green deployments, canary releases, circuit breaker configurations, and integration with Application Load Balancers and Network Load Balancers for traffic management. The service submodule handles complex container definitions with support for environment variables, secrets from AWS Secrets Manager or Systems Manager Parameter Store, volume mounts for persistent storage using EFS or EBS, and health check configurations for robust application monitoring.

Key architectural advantages include integrated CloudWatch Logs configuration for centralized logging, IAM role management for task execution and application permissions following least privilege principles, Service Connect integration for simplified service-to-service communication, and comprehensive auto-scaling support based on CPU, memory, or custom CloudWatch metrics. The module supports advanced ECS features such as ECS Exec for interactive debugging, Container Insights for enhanced observability, placement constraints for fine-grained task scheduling, and multi-architecture support for ARM-based Graviton processors. This makes it ideal for organizations adopting containerization strategies, migrating from Kubernetes to ECS, or building cloud-native microservices architectures on AWS.

## Key Features

- **Dual Compute Support**: Deploy containers using serverless AWS Fargate or EC2 instances with Auto Scaling groups
- **Capacity Provider Strategies**: Configure multiple capacity providers with weights and base allocations for cost optimization
- **Fargate and Fargate Spot**: Mix on-demand and spot capacity for cost-effective serverless container execution
- **Service Management**: Comprehensive ECS service creation with deployment configuration, rolling updates, and circuit breaker support
- **Task Definitions**: Define containerized applications with CPU, memory, networking, and storage specifications
- **Container Definitions**: Configure containers with images, environment variables, secrets, port mappings, and health checks
- **Load Balancer Integration**: Seamless integration with Application Load Balancers (ALB) and Network Load Balancers (NLB)
- **Service Discovery**: Built-in support for AWS Cloud Map service discovery and Service Connect for service mesh capabilities
- **Auto Scaling**: Configure target tracking and step scaling policies based on CloudWatch metrics
- **IAM Role Management**: Automatic creation and management of task execution roles and task roles with custom policies
- **CloudWatch Logs**: Integrated logging with configurable log groups, retention periods, and encryption
- **Secrets Management**: Inject secrets from AWS Secrets Manager or Systems Manager Parameter Store into containers
- **EFS and EBS Volumes**: Attach persistent storage volumes to tasks for stateful applications
- **Network Modes**: Support for awsvpc, bridge, and host network modes with security group management
- **ECS Exec**: Enable interactive shell access to running containers for debugging
- **Container Insights**: Enable enhanced monitoring and observability for containerized applications
- **Placement Strategies**: Configure task placement with spread, binpack, or random strategies
- **Placement Constraints**: Define constraints based on instance attributes, AZ, or custom expressions
- **Blue-Green Deployments**: Support for CodeDeploy integration for safe deployment strategies
- **Circuit Breaker**: Automatic rollback on deployment failures to maintain service stability
- **Spot Instance Support**: Use EC2 spot instances as capacity providers for cost savings
- **Multi-Architecture**: Support for x86_64 and ARM64 (Graviton) processor architectures
- **Conditional Creation**: Use create flags to conditionally manage resources across environments
- **Comprehensive Tagging**: Tag all resources for organization, cost allocation, and governance

## Main Use Cases

1. **Microservices Deployment**: Deploy and orchestrate microservices architectures with service discovery and load balancing
2. **API Backend Services**: Run scalable RESTful APIs and GraphQL services with auto-scaling capabilities
3. **Web Application Hosting**: Host containerized web applications with session persistence and SSL termination
4. **Batch Processing Workloads**: Execute scheduled or event-driven batch jobs using ECS tasks
5. **Event-Driven Architectures**: Build serverless architectures triggered by EventBridge, SQS, or SNS events
6. **CI/CD Pipeline Workers**: Run build agents and deployment workers for continuous integration pipelines
7. **Data Processing Pipelines**: Process streaming or batch data with containerized ETL workloads
8. **Machine Learning Inference**: Deploy ML models for real-time or batch inference with GPU support
9. **Legacy Application Modernization**: Containerize and migrate traditional applications to ECS
10. **Multi-Tenant SaaS Platforms**: Build isolated tenant environments using ECS task-level security
11. **Development and Testing Environments**: Spin up ephemeral environments for development teams
12. **Hybrid Fargate/EC2 Workloads**: Mix serverless and EC2-based compute for cost and performance optimization

## Submodules

### 1. cluster

- **Purpose**: Creates ECS cluster infrastructure with capacity providers, IAM roles, and CloudWatch logging
- **Source**: `terraform-aws-modules/ecs/aws//modules/cluster`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest/submodules/cluster
- **Key Features**: Fargate/EC2/ECS Managed Instances capacity providers, Container Insights, execute command configuration
- **Use Cases**: Creating ECS clusters, configuring capacity strategies, setting up cluster-level logging

### 2. service

- **Purpose**: Deploys ECS services with task definitions, autoscaling, and load balancer integration (Fargate-focused)
- **Source**: `terraform-aws-modules/ecs/aws//modules/service`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest/submodules/service
- **Key Features**: Task definition management, auto-scaling (enabled by default), load balancer integration, Service Connect
- **Use Cases**: Deploying containerized applications, configuring service auto-scaling, integrating with ALB/NLB

### 3. container-definition

- **Purpose**: Generates container definition JSON with integrated CloudWatch or FireLens logging
- **Source**: `terraform-aws-modules/ecs/aws//modules/container-definition`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest/submodules/container-definition
- **Key Features**: CloudWatch logging by default, FireLens support, secrets management, health checks
- **Use Cases**: Creating reusable container definitions, configuring logging drivers, managing environment variables and secrets

### 4. express-service

- **Purpose**: Simplified ECS service deployment with automatic infrastructure provisioning
- **Source**: `terraform-aws-modules/ecs/aws//modules/express-service`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest/submodules/express-service
- **Key Features**: Minimal configuration required, automatic security group creation, built-in health checks
- **Use Cases**: Rapid API deployment, prototyping, services with standard configuration needs

## Submodule 1: cluster

### Description

The cluster submodule creates AWS ECS cluster resources that serve as logical groupings for ECS services and tasks. This submodule manages cluster configuration including capacity provider strategies for Fargate and EC2 Auto Scaling groups, CloudWatch log group creation for cluster-level logging, and execute command configuration for interactive container access. It supports both serverless Fargate deployments and traditional EC2-based clusters with fine-grained control over capacity allocation and scaling behavior.

### Key Features

- Create ECS clusters with customizable names and configuration
- Configure Fargate and Fargate Spot capacity providers with weights and base allocations
- Manage EC2 Auto Scaling Group capacity providers with managed scaling
- Enable Container Insights for enhanced monitoring and observability
- Configure execute command logging for ECS Exec sessions
- Create CloudWatch log groups with encryption and retention policies
- Support for cluster configuration settings including encryption and logging
- Conditional resource creation for multi-environment deployments
- Comprehensive tagging support for resource organization

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `cluster_name` | `string` | `""` | Name of the cluster (up to 255 letters, numbers, hyphens, and underscores) |
| `cluster_configuration` | `any` | `{}` | Execute command and managed storage configuration |
| `cluster_settings` | `map(string)` | `{}` | Configuration block with cluster settings (e.g., Container Insights) |
| `default_capacity_provider_strategy` | `any` | `{}` | Default capacity provider strategy for the cluster |
| `fargate_capacity_providers` | `any` | `{}` | Map of Fargate capacity provider definitions |
| `autoscaling_capacity_providers` | `any` | `{}` | Map of EC2 Auto Scaling capacity provider definitions |
| `create_cloudwatch_log_group` | `bool` | `true` | Determines whether a log group is created for the cluster |
| `cloudwatch_log_group_name` | `string` | `null` | Name of CloudWatch log group for cluster logging |
| `cloudwatch_log_group_retention_in_days` | `number` | `90` | Number of days to retain log events |
| `cloudwatch_log_group_kms_key_id` | `string` | `null` | KMS key ID for log group encryption |
| `tags` | `map(string)` | `{}` | A map of tags to add to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cluster_arn` | ARN that identifies the cluster |
| `cluster_id` | ID that identifies the cluster |
| `cluster_name` | Name that identifies the cluster |
| `cluster_capacity_providers` | Map of cluster capacity providers attributes |
| `autoscaling_capacity_providers` | Map of autoscaling capacity providers created and their attributes |
| `cloudwatch_log_group_name` | Name of CloudWatch log group created |
| `cloudwatch_log_group_arn` | ARN of CloudWatch log group created |

### Usage Examples

#### Example 1: Fargate Cluster with Spot

```hcl
module "ecs_cluster" {
  source  = "terraform-aws-modules/ecs/aws//modules/cluster"
  version = "~> 7.3"

  cluster_name = "production-fargate"

  # Enable Container Insights
  cluster_settings = {
    name  = "containerInsights"
    value = "enabled"
  }

  # Configure Fargate capacity providers
  fargate_capacity_providers = {
    FARGATE = {
      default_capacity_provider_strategy = {
        weight = 50
        base   = 20
      }
    }
    FARGATE_SPOT = {
      default_capacity_provider_strategy = {
        weight = 50
      }
    }
  }

  # Enable execute command logging
  cluster_configuration = {
    execute_command_configuration = {
      logging = "OVERRIDE"
      log_configuration = {
        cloud_watch_log_group_name = "/aws/ecs/cluster/production-fargate"
      }
    }
  }

  # CloudWatch logging configuration
  cloudwatch_log_group_retention_in_days = 30
  cloudwatch_log_group_kms_key_id        = aws_kms_key.ecs_logs.id

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
```

#### Example 2: EC2 Cluster with Auto Scaling

```hcl
module "ecs_cluster_ec2" {
  source  = "terraform-aws-modules/ecs/aws//modules/cluster"
  version = "~> 7.3"

  cluster_name = "production-ec2"

  # EC2 Auto Scaling capacity provider
  autoscaling_capacity_providers = {
    main = {
      auto_scaling_group_arn = aws_autoscaling_group.ecs.arn

      managed_scaling = {
        maximum_scaling_step_size = 5
        minimum_scaling_step_size = 1
        status                    = "ENABLED"
        target_capacity           = 60
      }

      default_capacity_provider_strategy = {
        weight = 100
        base   = 1
      }

      managed_termination_protection = "ENABLED"
    }
  }

  cluster_settings = {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = "production"
    ComputeType = "ec2"
  }
}
```

## Submodule 2: service

### Description

The service submodule creates and manages ECS services, which maintain running task instances and optionally register them with load balancers. This submodule handles the complete lifecycle of ECS services including task definition creation with container specifications, auto-scaling configuration, load balancer target group associations, Service Connect setup for service mesh capabilities, and IAM role management for task execution and application permissions. It provides comprehensive support for both Fargate and EC2 launch types with sensible defaults optimized for Fargate deployments.

**Important**: Autoscaling is enabled by default in v7.x. The `desired_count` parameter is always ignored in favor of autoscaling policies. Set `enable_autoscaling = false` if you need static task counts.

### Key Features

- Create ECS services with desired count and deployment configuration
- Define task definitions with CPU, memory, and network mode specifications
- Configure multiple containers with images, environment variables, and secrets
- Integrate with Application Load Balancers and Network Load Balancers
- Set up Service Connect for service-to-service communication
- Configure auto-scaling with target tracking or step scaling policies
- Manage task execution IAM roles and task IAM roles with custom policies
- Create and configure security groups for task networking
- Support for EFS and EBS volume attachments
- Enable ECS Exec for interactive debugging
- Configure deployment circuit breaker for automatic rollback
- Set up CloudWatch Logs with custom log groups and retention
- Define health checks and grace periods for load balancer integration
- Configure placement constraints and strategies for EC2 launch type
- Support for blue-green and canary deployment patterns

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `name` | `string` | `""` | Name of the service (up to 255 letters, numbers, hyphens, and underscores) |
| `cluster_arn` | `string` | `""` | ARN of the ECS cluster where the service will be deployed |
| `cpu` | `number` | `1024` | Number of CPU units used by the task (1024 = 1 vCPU) |
| `memory` | `number` | `2048` | Amount of memory (in MiB) used by the task |
| `launch_type` | `string` | `null` | Launch type on which to run service (FARGATE, EC2, or EXTERNAL) |
| `desired_count` | `number` | `1` | Initial task count (ignored when autoscaling is enabled, which is the default) |
| `deployment_minimum_healthy_percent` | `number` | `100` | Lower limit of running tasks during deployment |
| `deployment_maximum_percent` | `number` | `200` | Upper limit of running tasks during deployment |
| `enable_execute_command` | `bool` | `false` | Enable ECS Exec for the service |
| `container_definitions` | `any` | `{}` | Map of container definitions to create |
| `load_balancer` | `any` | `{}` | Load balancer configuration for the service |
| `service_connect_configuration` | `any` | `{}` | Service Connect configuration for the service |
| `subnet_ids` | `list(string)` | `[]` | Subnets for task placement (required for awsvpc network mode) |
| `security_group_ids` | `list(string)` | `[]` | Security groups to associate with the task |
| `assign_public_ip` | `bool` | `false` | Assign a public IP address to the task ENI |
| `enable_autoscaling` | `bool` | `true` | Enable autoscaling for the service |
| `autoscaling_min_capacity` | `number` | `1` | Minimum number of tasks |
| `autoscaling_max_capacity` | `number` | `10` | Maximum number of tasks |
| `autoscaling_policies` | `any` | `{}` | Map of autoscaling policies to create |
| `create_task_exec_iam_role` | `bool` | `true` | Create task execution IAM role |
| `task_exec_iam_role_policies` | `map(string)` | `{}` | IAM policies to attach to task execution role |
| `create_task_iam_role` | `bool` | `false` | Create task IAM role |
| `task_iam_role_policies` | `map(string)` | `{}` | IAM policies to attach to task role |
| `volumes` | `any` | `{}` | Map of volume definitions for the task |
| `tags` | `map(string)` | `{}` | A map of tags to add to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `id` | ARN that identifies the service |
| `name` | Name of the service |
| `task_definition_arn` | Full ARN of the task definition (including revision) |
| `task_definition_family` | Family of the task definition |
| `task_definition_revision` | Revision of the task definition |
| `iam_role_arn` | ARN of IAM role used by service |
| `task_exec_iam_role_arn` | ARN of task execution IAM role |
| `task_iam_role_arn` | ARN of task IAM role |
| `security_group_id` | ID of security group created for the service |
| `autoscaling_policies` | Map of autoscaling policies created |
| `container_definitions` | Container definitions created |

### Usage Examples

#### Example 1: Basic Fargate Service with ALB

```hcl
module "ecs_service" {
  source  = "terraform-aws-modules/ecs/aws//modules/service"
  version = "~> 7.3"

  name        = "web-application"
  cluster_arn = module.ecs_cluster.cluster_arn

  # Task sizing
  cpu    = 1024
  memory = 2048

  # Fargate configuration
  launch_type = "FARGATE"
  subnet_ids  = module.vpc.private_subnets

  # Container definition
  container_definitions = {
    web = {
      image = "nginx:latest"
      port_mappings = [{
        name          = "web"
        containerPort = 80
        protocol      = "tcp"
      }]

      # Environment variables
      environment = [
        {
          name  = "ENVIRONMENT"
          value = "production"
        }
      ]

      # CloudWatch Logs
      log_configuration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/web-application"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "web"
        }
      }
    }
  }

  # Load balancer integration
  load_balancer = {
    service = {
      target_group_arn = aws_lb_target_group.web.arn
      container_name   = "web"
      container_port   = 80
    }
  }

  # Enable auto-scaling
  enable_autoscaling      = true
  autoscaling_min_capacity = 2
  autoscaling_max_capacity = 10

  autoscaling_policies = {
    cpu = {
      policy_type = "TargetTrackingScaling"

      target_tracking_scaling_policy_configuration = {
        predefined_metric_specification = {
          predefined_metric_type = "ECSServiceAverageCPUUtilization"
        }
        target_value = 70.0
      }
    }
  }

  tags = {
    Environment = "production"
    Application = "web"
  }
}
```

#### Example 2: Service with Secrets and EFS Volume

```hcl
module "ecs_service_with_secrets" {
  source  = "terraform-aws-modules/ecs/aws//modules/service"
  version = "~> 7.3"

  name        = "api-service"
  cluster_arn = module.ecs_cluster.cluster_arn

  cpu    = 2048
  memory = 4096

  desired_count = 3

  # Enable ECS Exec for debugging
  enable_execute_command = true

  container_definitions = {
    api = {
      image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/api:latest"

      port_mappings = [{
        name          = "api"
        containerPort = 8080
        protocol      = "tcp"
      }]

      # Secrets from Secrets Manager
      secrets = [
        {
          name      = "DATABASE_PASSWORD"
          valueFrom = "arn:aws:secretsmanager:us-east-1:123456789012:secret:db-password"
        },
        {
          name      = "API_KEY"
          valueFrom = "arn:aws:secretsmanager:us-east-1:123456789012:secret:api-key"
        }
      ]

      # Environment variables from Parameter Store
      secrets_from_parameter_store = [
        {
          name      = "DATABASE_HOST"
          valueFrom = "arn:aws:ssm:us-east-1:123456789012:parameter/db-host"
        }
      ]

      # Mount EFS volume
      mount_points = [{
        sourceVolume  = "efs-storage"
        containerPath = "/mnt/efs"
        readOnly      = false
      }]

      # Health check
      health_check = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  }

  # EFS volume configuration
  volumes = {
    efs-storage = {
      efs_volume_configuration = {
        file_system_id          = aws_efs_file_system.app_data.id
        transit_encryption      = "ENABLED"
        authorization_config = {
          access_point_id = aws_efs_access_point.app.id
          iam             = "ENABLED"
        }
      }
    }
  }

  # Task IAM role with custom policies
  create_task_iam_role = true
  task_iam_role_policies = {
    s3_access = aws_iam_policy.s3_access.arn
    dynamodb  = "arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess"
  }

  # Task execution role with Secrets Manager access
  task_exec_iam_role_policies = {
    secrets = aws_iam_policy.secrets_access.arn
  }

  subnet_ids         = module.vpc.private_subnets
  security_group_ids = [aws_security_group.api.id]

  # Circuit breaker for safe deployments
  deployment_circuit_breaker = {
    enable   = true
    rollback = true
  }

  tags = {
    Environment = "production"
    Service     = "api"
  }
}
```

#### Example 3: Service Connect for Microservices

```hcl
module "orders_service" {
  source  = "terraform-aws-modules/ecs/aws//modules/service"
  version = "~> 7.3"

  name        = "orders-service"
  cluster_arn = module.ecs_cluster.cluster_arn

  cpu    = 512
  memory = 1024

  container_definitions = {
    orders = {
      image = "orders-api:latest"
      port_mappings = [{
        name          = "orders-api"
        containerPort = 8080
        protocol      = "tcp"
      }]
    }
  }

  # Service Connect configuration
  service_connect_configuration = {
    enabled   = true
    namespace = aws_service_discovery_http_namespace.microservices.arn

    service = {
      client_alias = {
        port     = 8080
        dns_name = "orders"
      }
      port_name      = "orders-api"
      discovery_name = "orders"
    }
  }

  subnet_ids = module.vpc.private_subnets

  tags = {
    Environment = "production"
    Service     = "orders"
  }
}
```

## Submodule 3: container-definition

### Description

The container-definition submodule generates container definition JSON configurations for use with ECS task definitions. It provides a structured way to define container specifications with integrated CloudWatch logging by default, or FireLens for advanced log routing. This submodule is useful for creating reusable container definitions that can be shared across multiple services.

### Key Features

- Generate container definition JSON with proper formatting
- CloudWatch Logs integration enabled by default
- FireLens support for advanced log routing
- Secrets Manager and Parameter Store integration
- Health check configuration
- Read-only root filesystem by default for security
- Environment variables and secrets management

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Container identifier (up to 255 characters) |
| `image` | `string` | `""` | Docker image URI with optional tag/digest |
| `cpu` | `number` | `null` | CPU units to allocate |
| `memory` | `number` | `null` | Memory (MiB) to allocate |
| `essential` | `bool` | `true` | Container failure stops task |
| `portMappings` | `list(any)` | `[]` | Port exposure configuration |
| `environment` | `list(map(string))` | `[]` | Environment variables |
| `secrets` | `list(map(string))` | `[]` | AWS Secrets Manager references |
| `readonlyRootFilesystem` | `bool` | `true` | Enable read-only root filesystem |
| `logConfiguration` | `any` | `null` | Custom logging driver configuration |
| `healthCheck` | `any` | `null` | Health monitoring configuration |
| `cloudwatch_log_group_retention_in_days` | `number` | `14` | Log retention period |

### Main Outputs

| Output | Description |
|--------|-------------|
| `container_definition` | Structured container configuration object |
| `container_definition_json` | JSON-formatted container definition |
| `cloudwatch_log_group_arn` | CloudWatch log group ARN |
| `cloudwatch_log_group_name` | CloudWatch log group name |

### Usage Example

```hcl
module "container_definition" {
  source  = "terraform-aws-modules/ecs/aws//modules/container-definition"
  version = "~> 7.3"

  name  = "api"
  image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/api:latest"

  cpu    = 256
  memory = 512

  portMappings = [{
    containerPort = 8080
    protocol      = "tcp"
  }]

  environment = [
    { name = "ENV", value = "production" },
    { name = "LOG_LEVEL", value = "info" }
  ]

  secrets = [
    {
      name      = "DATABASE_URL"
      valueFrom = "arn:aws:secretsmanager:us-east-1:123456789012:secret:db-url"
    }
  ]

  healthCheck = {
    command     = ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
    interval    = 30
    timeout     = 5
    retries     = 3
    startPeriod = 60
  }

  # Security: read-only root filesystem enabled by default
  readonlyRootFilesystem = true

  cloudwatch_log_group_retention_in_days = 30
}

# Use with task definition (wrap with jsonencode)
resource "aws_ecs_task_definition" "app" {
  family                = "app"
  container_definitions = jsonencode([module.container_definition.container_definition])
  # ... other configuration
}
```

## Submodule 4: express-service

### Description

The express-service submodule provides a simplified interface for deploying ECS services with minimal configuration. It automatically provisions required infrastructure including security groups, IAM roles, and CloudWatch logging. This submodule is ideal for rapid API deployment, prototyping, or services that follow standard configuration patterns.

### Key Features

- Minimal configuration required for deployment
- Automatic security group creation and management
- Built-in health check endpoint configuration
- Automatic IAM role provisioning
- Integrated autoscaling with sensible defaults
- Service URL output for easy access

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Service identifier |
| `vpc_id` | `string` | `""` | VPC identifier for security group |
| `cpu` | `number` | `256` | Task CPU (256-4096, powers of 2) |
| `memory` | `number` | `512` | Task memory (512-8192 MiB) |
| `cluster` | `string` | `"default"` | ECS cluster name or ARN |
| `network_configuration` | `object` | `{}` | VPC subnets for task placement |
| `primary_container` | `object` | `{}` | Container specs including image and port |
| `scaling_target` | `object` | `{}` | Autoscaling configuration |
| `health_check_path` | `string` | `"/ping"` | Health check endpoint path |
| `security_group_ingress_rules` | `map(any)` | `{}` | Ingress rules |
| `security_group_egress_rules` | `map(any)` | `{}` | Egress rules |

### Main Outputs

| Output | Description |
|--------|-------------|
| `service_arn` | ECS service ARN |
| `service_url` | Service endpoint URL |
| `security_group_id` | Created security group ID |
| `task_exec_iam_role_arn` | Task execution IAM role ARN |
| `tasks_iam_role_arn` | Task IAM role ARN |
| `cloudwatch_log_group_name` | CloudWatch log group name |

### Usage Example

```hcl
module "express_api" {
  source  = "terraform-aws-modules/ecs/aws//modules/express-service"
  version = "~> 7.3"

  name   = "my-api"
  vpc_id = module.vpc.vpc_id

  cpu    = 512
  memory = 1024

  cluster = module.ecs_cluster.arn

  network_configuration = {
    subnets = module.vpc.private_subnets
  }

  primary_container = {
    image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-api:latest"
    port  = 3000
  }

  scaling_target = {
    min_capacity = 2
    max_capacity = 10
  }

  health_check_path = "/health"

  # Allow inbound traffic from ALB
  security_group_ingress_rules = {
    alb = {
      type                     = "ingress"
      from_port                = 3000
      to_port                  = 3000
      protocol                 = "tcp"
      source_security_group_id = module.alb.security_group_id
    }
  }

  tags = {
    Environment = "production"
    Service     = "my-api"
  }
}
```

## Best Practices

### Cluster Configuration and Capacity Planning

1. **Use Fargate for Simplicity**: Start with Fargate for most workloads to eliminate server management, patching, and capacity planning overhead unless specific EC2 requirements exist.
2. **Mix Fargate and Fargate Spot**: Configure capacity provider strategies with 50% Fargate and 50% Fargate Spot for cost optimization while maintaining availability.
3. **Enable Container Insights**: Always enable Container Insights for production clusters to gain visibility into resource utilization and performance metrics.
4. **Right-Size Capacity Providers**: For EC2-based clusters, set target capacity between 70-80% to balance cost efficiency with scaling headroom.
5. **Use Cluster Auto Scaling**: Configure managed scaling for EC2 capacity providers to automatically adjust cluster capacity based on task requirements.
6. **Separate Environments**: Create separate ECS clusters for development, staging, and production to isolate workloads and prevent resource contention.

### Service Deployment and Configuration

1. **Define Resource Limits**: Always specify explicit CPU and memory requirements for tasks to ensure proper scheduling and prevent resource exhaustion.
2. **Use Deployment Circuit Breaker**: Enable circuit breaker with rollback to automatically revert failed deployments and maintain service stability.
3. **Configure Health Checks**: Implement container health checks and set appropriate health check grace periods to prevent premature task termination during startup.
4. **Set Deployment Constraints**: Configure minimum healthy percent (100%) and maximum percent (200%) for zero-downtime rolling deployments.
5. **Use Service Connect**: Leverage Service Connect instead of traditional service discovery for simplified service-to-service communication and automatic traffic management.
6. **Implement Readiness and Liveness Probes**: Define separate health check commands for readiness (traffic routing) and liveness (container restart) scenarios.
7. **Version Task Definitions**: Use infrastructure-as-code to version control task definitions and enable easy rollback capabilities.

### Security and Access Control

1. **Use Task IAM Roles**: Always create separate task IAM roles with least privilege permissions instead of using instance roles or hardcoded credentials.
2. **Separate Execution and Task Roles**: Use task execution roles for ECS agent operations (pulling images, CloudWatch logs) and task roles for application permissions.
3. **Store Secrets Securely**: Use AWS Secrets Manager or Systems Manager Parameter Store for sensitive data; never embed secrets in container images or environment variables.
4. **Enable Secrets Encryption**: Ensure secrets are encrypted at rest using KMS and transmitted securely to tasks.
5. **Use Private Subnets**: Deploy ECS tasks in private subnets without public IPs, using NAT gateways or VPC endpoints for outbound connectivity.
6. **Restrict Security Groups**: Create dedicated security groups for ECS tasks with minimal required ingress/egress rules following least privilege principle.
7. **Enable ECS Exec Carefully**: Only enable ECS Exec on development/staging environments or temporarily for production troubleshooting, and audit all exec sessions.
8. **Use Private ECR Repositories**: Store container images in private Amazon ECR repositories with image scanning enabled for vulnerability detection.

### Monitoring and Observability

1. **Centralize Logs with CloudWatch**: Configure awslogs log driver to send all container logs to CloudWatch Logs for centralized analysis and troubleshooting.
2. **Set Appropriate Retention**: Define log retention periods based on compliance requirements (30 days for development, 90+ days for production).
3. **Use Structured Logging**: Emit logs in JSON format to enable powerful querying with CloudWatch Logs Insights and easier integration with log analytics tools.
4. **Monitor Key Metrics**: Create CloudWatch alarms for CPU utilization, memory utilization, task count, and deployment failures.
5. **Enable X-Ray Tracing**: Integrate AWS X-Ray for distributed tracing across microservices to identify performance bottlenecks and failures.
6. **Use Container Insights Metrics**: Leverage Container Insights for detailed task and container-level metrics beyond standard CloudWatch metrics.
7. **Implement Application-Level Health Endpoints**: Expose /health and /ready endpoints in applications for load balancer health checks and monitoring.

### Auto Scaling and Performance

1. **Enable Target Tracking Scaling**: Use target tracking auto-scaling with CPU or memory utilization targets (70-80%) for automatic capacity adjustment.
2. **Set Realistic Scaling Limits**: Define minimum capacity to handle baseline load and maximum capacity to prevent runaway costs from scaling events.
3. **Use Multiple Scaling Policies**: Combine CPU-based and custom metric-based scaling for more responsive and accurate scaling behavior.
4. **Configure Scale-In Protection**: Set appropriate cooldown periods to prevent thrashing during scale-in operations.
5. **Right-Size Task Resources**: Start with conservative CPU/memory allocations and adjust based on CloudWatch metrics and Container Insights data.
6. **Use Fargate for Variable Workloads**: Fargate automatically handles host-level scaling, making it ideal for workloads with unpredictable or variable traffic patterns.
7. **Leverage Spot for Batch Workloads**: Use Fargate Spot or EC2 spot instances for fault-tolerant batch processing and scheduled tasks to reduce costs by up to 70%.

### Networking and Load Balancing

1. **Use awsvpc Network Mode**: Always use awsvpc network mode for task-level network isolation and security group enforcement.
2. **Implement Load Balancing**: Place services behind Application Load Balancers for HTTP/HTTPS traffic or Network Load Balancers for TCP/UDP traffic.
3. **Configure Target Group Health Checks**: Set health check paths, intervals, and thresholds appropriate for application startup time and responsiveness.
4. **Enable Connection Draining**: Configure deregistration delay to allow in-flight requests to complete during task termination.
5. **Use Service Connect for Microservices**: Implement Service Connect for simplified service mesh capabilities without additional infrastructure.
6. **Plan IP Address Space**: Ensure VPC subnets have sufficient IP addresses for awsvpc network mode (each task consumes one IP address).
7. **Enable VPC Flow Logs**: Capture network traffic information for security analysis and troubleshooting connectivity issues.

### Cost Optimization

1. **Choose the Right Compute**: Use Fargate for variable workloads and EC2 for steady-state workloads with high utilization to optimize costs.
2. **Leverage Savings Plans**: Purchase Compute Savings Plans or Fargate Savings Plans for predictable workloads to save up to 50% compared to on-demand pricing.
3. **Use Fargate Spot**: Configure Fargate Spot with appropriate capacity provider strategies for fault-tolerant workloads to save up to 70%.
4. **Right-Size Tasks**: Regularly review CloudWatch metrics to identify over-provisioned tasks and reduce CPU/memory allocations.
5. **Optimize Container Images**: Use slim base images, multi-stage builds, and image layer caching to reduce image size and pull times.
6. **Implement Log Filtering**: Use log filtering at the container level to reduce log volume and CloudWatch Logs costs.
7. **Use Scheduled Scaling**: Scale down non-production environments during off-hours using scheduled scaling policies or Lambda functions.
8. **Monitor Task Churn**: High task churn indicates potential issues and increases costs; investigate and resolve underlying causes.

### High Availability and Disaster Recovery

1. **Deploy Across Multiple AZs**: Place tasks in subnets across at least three Availability Zones for high availability.
2. **Use Capacity Provider Spreading**: Configure spreading strategies to distribute tasks across AZs and capacity providers.
3. **Implement Circuit Breakers**: Enable deployment circuit breakers to automatically roll back failed deployments and maintain service availability.
4. **Set Appropriate Task Counts**: Run minimum two tasks per service for high availability and configure auto-scaling for peak loads.
5. **Plan for Spot Interruptions**: For Fargate Spot, implement graceful shutdown handling and set capacity provider weights to maintain on-demand baseline capacity.
6. **Use Blue-Green Deployments**: Implement CodeDeploy with ECS for safer deployments with automatic rollback capabilities.
7. **Maintain Disaster Recovery Plan**: Document recovery procedures, maintain infrastructure-as-code in version control, and regularly test recovery processes.
8. **Backup Task Definitions**: Store task definition revisions and maintain infrastructure-as-code to enable rapid recovery.

### Development and Deployment Workflow

1. **Use Infrastructure as Code**: Manage all ECS resources with Terraform to enable version control, code review, and consistent deployments.
2. **Implement CI/CD Pipelines**: Automate container builds, image scanning, and ECS deployments using CodePipeline, GitHub Actions, or GitLab CI.
3. **Tag Images Semantically**: Use semantic versioning for container image tags instead of "latest" for reproducible deployments.
4. **Test Before Production**: Deploy to development and staging clusters first, validate functionality, and then promote to production.
5. **Use Deployment Strategies**: Implement canary or blue-green deployments for critical services to minimize blast radius of issues.
6. **Enable Rollback Capabilities**: Maintain previous task definition revisions and automate rollback procedures for rapid recovery.
7. **Document Service Dependencies**: Maintain clear documentation of service dependencies, required resources, and deployment order.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ecs
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest
- **AWS ECS Documentation**: https://docs.aws.amazon.com/ecs/
- **ECS Best Practices Guide**: https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/intro.html
- **AWS Fargate Documentation**: https://docs.aws.amazon.com/AmazonECS/latest/userguide/what-is-fargate.html
- **ECS Task Definitions**: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html
- **ECS Service Connect**: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect.html
- **Container Insights**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html
- **ECS Pricing**: https://aws.amazon.com/ecs/pricing/
- **Fargate Pricing**: https://aws.amazon.com/fargate/pricing/
- **ECS Exec**: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html
- **ECS Auto Scaling**: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html
- **AWS Well-Architected Framework - Containers**: https://docs.aws.amazon.com/wellarchitected/latest/framework/a-container.html
- **Amazon ECR**: https://docs.aws.amazon.com/ecr/

## Notes for AI Agents

When using this module in automated workflows:

1. **Version 7.x Breaking Change**: Autoscaling is enabled by default; `desired_count` is ignored. Set `enable_autoscaling = false` for static task counts
2. **Start with Fargate**: Default to Fargate launch type unless specific EC2 requirements exist (GPU, specific instance types, cost optimization for steady workloads)
3. **Choose the Right Submodule**: Use `express-service` for rapid deployment, `service` for full control, `container-definition` for reusable container configs
4. **Resource Sizing**: CPU must be powers of 2 (256-4096), memory 512-8192 MiB. Start conservative and tune based on CloudWatch metrics
5. **IAM Roles are Critical**: Module creates task execution roles and task roles automatically; customize with `task_exec_iam_role_policies` and `task_iam_role_policies`
6. **Secrets Management**: Use `secrets` parameter in container definitions to inject from Secrets Manager or Parameter Store
7. **Network Mode**: Always use awsvpc network mode (default for Fargate) for security group enforcement and task-level network isolation
8. **Container Definition Output**: When using container-definition submodule, wrap output with `jsonencode()` when passing to task definitions
9. **Load Balancer Integration**: For web services, integrate with ALB; for TCP services, use NLB; configure appropriate health checks
10. **Container Health Checks**: Define health checks in container definitions for proper task lifecycle management
11. **Security Default**: Container definitions default to `readonlyRootFilesystem = true` for enhanced security
12. **Log Retention**: Main module defaults to 90 days, container-definition defaults to 14 days; adjust based on compliance requirements
13. **Test Deployments**: Use circuit breaker and deployment configuration to enable safe, automated rollbacks
14. **Tag Everything**: Tag all resources with Environment, Service, Team, and CostCenter for organization and cost allocation
