# Terraform AWS Batch Module

## Module Information

- **Module Name**: `batch`
- **Source**: `terraform-aws-modules/batch/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-batch
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/batch/aws/latest
- **Latest Version**: 3.1.0
- **Purpose**: Terraform module that creates and manages AWS Batch resources for running batch computing workloads at scale
- **Service**: AWS Batch (Amazon Batch)
- **Category**: Compute, Batch Processing
- **Keywords**: batch, aws-batch, compute-environment, job-queue, job-definition, fargate, eks, spot-instances, container-jobs, hpc, parallel-computing, job-scheduling, machine-learning, etl, data-processing
- **Use For**: machine learning model training, scientific simulations, financial risk modeling, genomic analysis, video rendering, ETL data processing, log analysis, image processing pipelines, high-performance computing workloads

## Description

AWS Batch is a fully managed service that enables developers, scientists, and engineers to run batch computing workloads of any scale without managing infrastructure. This Terraform module simplifies deployment of AWS Batch resources including compute environments (EC2, Spot, Fargate, EKS), job queues with priority scheduling, job definitions with container configurations, and associated IAM roles.

The module supports multiple compute environment types: managed EC2, managed Spot, Fargate, Fargate Spot, unmanaged EC2, and EKS-based compute. It enables complex job scheduling through job queues with configurable priorities and fair-share scheduling policies for equitable resource distribution. Job definitions support container, ECS, EKS, and multi-node parallel configurations with retry strategies and timeout controls.

Built for production deployments, the module provides automatic IAM role creation for instances, services, and Spot Fleet, along with comprehensive tagging capabilities. It handles the complete lifecycle of batch resources including automatic scaling from zero to thousands of vCPUs based on job queue depth.

## Key Features

- **Managed Compute Environments**: Automatically provision and manage EC2 instances for batch workloads
- **Fargate Compute Support**: Execute serverless batch jobs on AWS Fargate without managing servers
- **EKS Compute Support**: Run Kubernetes-based batch jobs on Amazon EKS clusters
- **Spot Instance Integration**: Leverage EC2 Spot instances for cost savings with configurable allocation strategies
- **Job Queue Management**: Create multiple job queues with priority-based ordering
- **Fair Share Scheduling**: Implement scheduling policies for equitable resource distribution across users
- **Job Definitions**: Define containerized batch jobs with resource requirements and retry strategies
- **Multi-Node Parallel Jobs**: Run tightly coupled HPC workloads across multiple nodes
- **IAM Role Automation**: Automatically create instance, service, and Spot Fleet IAM roles
- **Dynamic Scaling**: Automatically scale compute capacity from zero based on job demand

## Main Use Cases

1. **Machine Learning Training**: Train ML models at scale using GPU or CPU instances
2. **Scientific Simulations**: Run complex scientific simulations requiring massive parallel compute
3. **Financial Risk Modeling**: Execute Monte Carlo simulations and risk analysis workloads
4. **Genomic Analysis**: Process genomic sequencing data for bioinformatics
5. **Video Rendering**: Render video frames in parallel for media production
6. **ETL Data Processing**: Transform large datasets using containerized ETL jobs
7. **Log Analysis**: Aggregate and analyze log files from distributed systems
8. **Image Processing**: Process large volumes of images for computer vision applications

## Submodules

This module has no submodules. All functionality is provided by the root module.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls if resources should be created |
| `compute_environments` | `map(any)` | `{}` | Map of compute environment definitions |
| `job_queues` | `map(any)` | `{}` | Map of job queue definitions |
| `job_definitions` | `map(any)` | `{}` | Map of job definition configurations |
| `create_instance_iam_role` | `bool` | `true` | Create IAM role for EC2 instances |
| `create_service_iam_role` | `bool` | `true` | Create IAM role for Batch service |
| `create_spot_fleet_iam_role` | `bool` | `false` | Create IAM role for Spot Fleet |
| `instance_iam_role_additional_policies` | `map(string)` | `{}` | Additional policies for instance IAM role |
| `tags` | `map(string)` | `{}` | Tags to add to all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `compute_environments` | Map of compute environments created and their attributes |
| `job_queues` | Map of job queues created and their attributes |
| `job_definitions` | Map of job definitions created and their attributes |
| `scheduling_policies` | Map of scheduling policies created and their attributes |
| `instance_iam_role_arn` | ARN of the instance IAM role |
| `instance_iam_instance_profile_arn` | ARN of the instance profile |
| `service_iam_role_arn` | ARN of the Batch service IAM role |
| `spot_fleet_iam_role_arn` | ARN of the Spot Fleet IAM role |

## Usage Examples

### EC2 Compute Environment

```hcl
module "batch" {
  source  = "terraform-aws-modules/batch/aws"
  version = "~> 3.1"

  compute_environments = {
    ec2_main = {
      name_prefix = "ec2"
      compute_resources = {
        type           = "EC2"
        min_vcpus      = 0
        max_vcpus      = 16
        instance_types = ["m5.large", "r5.large"]
        subnets        = ["subnet-xxx", "subnet-yyy"]
        security_group_ids = ["sg-xxx"]
      }
    }
  }

  job_queues = {
    default = {
      name     = "default-queue"
      state    = "ENABLED"
      priority = 1
      compute_environment_order = {
        0 = { compute_environment_key = "ec2_main" }
      }
    }
  }

  job_definitions = {
    example_job = {
      name = "example-job"
      container_properties = jsonencode({
        image   = "public.ecr.aws/runecast/busybox:1.33.1"
        command = ["echo", "hello"]
        resourceRequirements = [
          { type = "VCPU", value = "1" },
          { type = "MEMORY", value = "1024" }
        ]
      })
    }
  }

  tags = {
    Environment = "dev"
  }
}
```

### Spot Instances for Cost Savings

```hcl
module "batch_spot" {
  source  = "terraform-aws-modules/batch/aws"
  version = "~> 3.1"

  create_spot_fleet_iam_role = true

  compute_environments = {
    spot_main = {
      name_prefix = "spot"
      compute_resources = {
        type                = "SPOT"
        allocation_strategy = "SPOT_CAPACITY_OPTIMIZED"
        bid_percentage      = 100
        min_vcpus           = 0
        max_vcpus           = 64
        instance_types      = ["m5.large", "m5.xlarge", "c5.large", "r5.large"]
        subnets             = ["subnet-xxx", "subnet-yyy"]
        security_group_ids  = ["sg-xxx"]
      }
    }
  }

  job_queues = {
    spot_queue = {
      name     = "spot-queue"
      state    = "ENABLED"
      priority = 1
      compute_environment_order = {
        0 = { compute_environment_key = "spot_main" }
      }
    }
  }

  tags = {
    Environment = "dev"
  }
}
```

### Fargate Compute Environment

```hcl
module "batch_fargate" {
  source  = "terraform-aws-modules/batch/aws"
  version = "~> 3.1"

  compute_environments = {
    fargate = {
      name_prefix = "fargate"
      compute_resources = {
        type      = "FARGATE"
        max_vcpus = 4
        subnets   = ["subnet-xxx"]
        security_group_ids = ["sg-xxx"]
      }
    }
  }

  job_queues = {
    fargate_queue = {
      name     = "fargate-queue"
      state    = "ENABLED"
      priority = 1
      compute_environment_order = {
        0 = { compute_environment_key = "fargate" }
      }
    }
  }

  job_definitions = {
    fargate_job = {
      name                  = "fargate-job"
      platform_capabilities = ["FARGATE"]
      container_properties = jsonencode({
        image   = "public.ecr.aws/runecast/busybox:1.33.1"
        command = ["echo", "hello"]
        fargatePlatformConfiguration = { platformVersion = "LATEST" }
        resourceRequirements = [
          { type = "VCPU", value = "1" },
          { type = "MEMORY", value = "2048" }
        ]
        executionRoleArn = "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole"
      })
    }
  }
}
```

### Job Definition with Retry Strategy

```hcl
module "batch" {
  source  = "terraform-aws-modules/batch/aws"
  version = "~> 3.1"

  # ... compute_environments and job_queues ...

  job_definitions = {
    job_with_retry = {
      name = "job-with-retry"
      retry_strategy = {
        attempts = 3
        evaluate_on_exit = {
          exit_code = {
            action       = "RETRY"
            on_exit_code = 1
          }
          timeout = {
            action    = "EXIT"
            on_reason = "TIMEOUT"
          }
        }
      }
      timeout = {
        attempt_duration_seconds = 3600
      }
      container_properties = jsonencode({
        image   = "my-app:latest"
        command = ["./process.sh"]
        resourceRequirements = [
          { type = "VCPU", value = "2" },
          { type = "MEMORY", value = "4096" }
        ]
      })
    }
  }
}
```

### Fair Share Scheduling

```hcl
module "batch" {
  source  = "terraform-aws-modules/batch/aws"
  version = "~> 3.1"

  # ... compute_environments ...

  job_queues = {
    shared_queue = {
      name     = "shared-queue"
      state    = "ENABLED"
      priority = 1
      fair_share_policy = {
        compute_reservation = 0
        share_decay_seconds = 3600
        share_distribution = {
          team_a = { share_identifier = "team-a", weight_factor = 0.5 }
          team_b = { share_identifier = "team-b", weight_factor = 0.3 }
          team_c = { share_identifier = "team-c", weight_factor = 0.2 }
        }
      }
      compute_environment_order = {
        0 = { compute_environment_key = "ec2_main" }
      }
    }
  }
}
```

## Best Practices

### Compute Environment Configuration

1. **Use Managed Environments**: Prefer managed compute environments for automatic scaling and maintenance
2. **Configure Min vCPUs to Zero**: Set `min_vcpus = 0` to scale down when no jobs are queued
3. **Set Appropriate Max vCPUs**: Configure `max_vcpus` based on maximum expected concurrent workload
4. **Use Multiple Instance Types**: Specify multiple instance types to increase Spot availability
5. **Enable Spot for Fault-Tolerant Workloads**: Use Spot instances for up to 90% cost savings

### Job Queue Design

1. **Separate Queues by Priority**: Create separate job queues for different priority levels
2. **Order Environments Strategically**: Place preferred compute environments first (lower order number)
3. **Implement Fair Share Scheduling**: Use fair-share policies in multi-tenant scenarios
4. **Set Appropriate Priorities**: Higher priority values indicate more important queues

### Job Definition Optimization

1. **Right-Size Resources**: Request only the vCPUs and memory actually needed
2. **Use ECR for Container Images**: Store Docker images in Amazon ECR for fast pulls
3. **Configure Retry Strategies**: Define retry logic with exit code evaluation
4. **Set Appropriate Timeouts**: Configure `attempt_duration_seconds` to prevent runaway jobs

### Security

1. **Least Privilege IAM**: Grant minimum necessary permissions to IAM roles
2. **Use Private Subnets**: Deploy compute environments in private subnets with NAT
3. **Configure Security Groups**: Restrict network access with least privilege rules
4. **Secure Secrets**: Store sensitive data in Secrets Manager, not environment variables

### Cost Optimization

1. **Maximize Spot Usage**: Use `SPOT_CAPACITY_OPTIMIZED` allocation strategy
2. **Scale to Zero**: Configure `min_vcpus = 0` to eliminate idle compute costs
3. **Use Fargate for Small Jobs**: Consider Fargate for short-duration jobs
4. **Track Costs by Tags**: Use cost allocation tags to track spending

## Important Notes

1. **Tag Changes Force Replacement**: Modifying tags on `compute_resources` forces compute environment replacement, which can cause job queue conflicts
2. **Fargate Memory Minimum**: Fargate requires minimum 2048 MB memory for job definitions
3. **Execution Role Required for Fargate**: Fargate job definitions require `executionRoleArn` in container properties (not created by this module)
4. **Compute Environment Order**: The map key in `compute_environment_order` determines order (0 = first priority)
5. **Name Fallbacks**: Resources use the map key as name if `name` attribute is not specified

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-batch
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/batch/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-batch/tree/master/examples
- **AWS Batch Documentation**: https://docs.aws.amazon.com/batch/latest/userguide/what-is-batch.html
- **Compute Environments**: https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html
- **Job Queues**: https://docs.aws.amazon.com/batch/latest/userguide/job_queues.html
- **Job Definitions**: https://docs.aws.amazon.com/batch/latest/userguide/job_definitions.html
- **Best Practices**: https://docs.aws.amazon.com/batch/latest/userguide/best-practices.html
- **AWS Batch Pricing**: https://aws.amazon.com/batch/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Compute Environment Type**: Choose `EC2`, `SPOT`, `FARGATE`, or `FARGATE_SPOT` based on workload requirements
2. **Instance Configuration**: Specify `instance_types` as list for EC2/SPOT (e.g., `["m5.large", "c5.large"]`)
3. **vCPU Settings**: Set `min_vcpus = 0` for cost savings, `max_vcpus` based on workload
4. **Spot Configuration**: Enable Spot with `type = "SPOT"`, `allocation_strategy = "SPOT_CAPACITY_OPTIMIZED"`, `create_spot_fleet_iam_role = true`
5. **VPC Configuration**: Provide `subnets` (preferably private) and `security_group_ids`
6. **Job Queue Priority**: Higher `priority` values indicate higher priority queues
7. **Job Resources**: Specify `resourceRequirements` with `VCPU` and `MEMORY` in container properties
8. **Fargate Jobs**: Require `platform_capabilities = ["FARGATE"]`, minimum 2048 MB memory, and `executionRoleArn`
9. **ECR Integration**: Use ECR image URIs: `"ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/image:tag"`
10. **Map Key Usage**: Compute environment keys referenced in `compute_environment_order` must match keys in `compute_environments`
