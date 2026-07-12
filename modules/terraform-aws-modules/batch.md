# Terraform AWS Batch Module

## Module Information

- **Module Name**: `batch`
- **Module ID**: `terraform-aws-modules/batch/aws`
- **Source**: `terraform-aws-modules/batch/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-batch
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/batch/aws/latest
- **Latest Version**: 3.1.0
- **Purpose**: Terraform module that creates and manages AWS Batch compute environments, job queues, scheduling policies, job definitions, and their associated IAM roles for running containerized and multi-node batch workloads at scale
- **Service**: AWS Batch
- **Category**: Compute, Batch Processing, Containers
- **Keywords**: batch, aws-batch, compute-environment, job-queue, job-definition, fargate, eks, spot-instances, multi-node-parallel, fair-share-scheduling, hpc, ecs-properties, container-jobs, job-scheduling
- **Use For**: machine learning model training, scientific simulations, financial risk modeling, genomic analysis, video rendering, ETL data processing, log analysis, image processing pipelines, high-performance computing workloads

## Description

AWS Batch is a fully managed service that plans, schedules, and runs batch computing workloads across the full range of AWS compute options without requiring you to install or manage batch computing software. This Terraform module creates the complete set of AWS Batch resources — `aws_batch_compute_environment`, `aws_batch_job_queue`, `aws_batch_scheduling_policy`, and `aws_batch_job_definition` — plus the IAM roles (instance, service, and Spot Fleet) and instance profile that back them.

The module supports every AWS Batch compute model: managed EC2, managed Spot (with configurable allocation strategy and bid percentage), Fargate, Fargate Spot, and EKS-based compute environments that schedule Batch jobs as pods on an existing Amazon EKS cluster. Job definitions mirror this flexibility, supporting standard container jobs (`container_properties`), ECS task-style jobs with multiple dependent containers (`ecs_properties`), Kubernetes pod jobs (`eks_properties`), and tightly-coupled multi-node parallel (MNP) jobs for HPC workloads (`node_properties`). Job queues support priority ordering across multiple compute environments, fair-share scheduling policies for equitable multi-tenant resource distribution, and time-limit actions that automatically cancel or terminate jobs stuck in a given state.

Because `compute_environments`, `job_queues`, and `job_definitions` are all optional maps that default to `null`, the module can be used incrementally — e.g., to create only IAM roles, or only a subset of resources — and every resource name falls back to its map key when not explicitly set. This module has no submodules; all compute and job types are configured through root-module input variables.

## Key Features

- **Multiple Compute Types**: Managed EC2, managed Spot, Fargate, Fargate Spot, and EKS-based compute environments (jobs run as pods on an existing EKS cluster)
- **Multiple Job Definition Types**: Container (`container_properties`), ECS task-style multi-container (`ecs_properties`), Kubernetes pod (`eks_properties`), and multi-node parallel HPC jobs (`node_properties`)
- **Priority Job Queues**: Order multiple compute environments per queue via `compute_environment_order`, with independent queue priorities and enable/disable state
- **Fair-Share Scheduling**: Embedded `fair_share_policy` per job queue (compute reservation, share decay, weighted share distribution) automatically provisions an `aws_batch_scheduling_policy`
- **Job State Time Limit Actions**: Automatically cancel or terminate jobs that remain stuck in a state (e.g., `RUNNABLE`) beyond a configured duration
- **Compute Environment Update Policies**: Control whether in-flight jobs are terminated or allowed to finish when compute environment infrastructure is updated
- **Automated IAM Role Management**: Optionally create instance, Batch service, and Spot Fleet IAM roles (with instance profile) or bring your own via `service_role`/`instance_role`
- **Retry Strategies & Timeouts**: Per-job-definition retry logic with exit-code/status-reason evaluation and attempt-duration timeouts
- **Region Override**: `region` variable to target a specific AWS region independent of the provider default (requires AWS provider >= 6.0)
- **Granular Feature Flags**: `create`, `create_job_queues`, `create_instance_iam_role`, `create_service_iam_role`, `create_spot_fleet_iam_role` for partial/incremental deployments

## Main Use Cases

1. **Machine Learning Training**: Train ML models at scale using GPU or CPU EC2/Spot instances
2. **Scientific Simulations**: Run complex, tightly-coupled simulations using multi-node parallel jobs
3. **Financial Risk Modeling**: Execute Monte Carlo simulations and risk analysis workloads on Spot for cost efficiency
4. **Genomic Analysis**: Process genomic sequencing data for bioinformatics pipelines
5. **Video Rendering**: Render video frames in parallel across large Fargate or EC2 fleets
6. **ETL Data Processing**: Transform large datasets using containerized or Kubernetes-native ETL jobs
7. **Log Analysis**: Aggregate and analyze log files from distributed systems on a schedule
8. **Image Processing**: Process large volumes of images for computer vision applications
9. **Kubernetes-Native Batch**: Run Batch jobs as pods on an existing EKS cluster to share cluster resources and tooling

## Submodules

This module has **no submodules**. All compute environment types (EC2, Spot, Fargate, EKS) and job definition types (container, multi-node, ECS, EKS) are configured through root-module input variables.

## Main Input Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls if resources should be created (affects nearly all resources) |
| `region` | `string` | `null` | AWS region override for resources managed by this module |
| `compute_environments` | `map(object)` | `null` | Map of compute environment definitions (EC2, SPOT, FARGATE, FARGATE_SPOT, or EKS-based) |
| `create_job_queues` | `bool` | `true` | Determines whether to create job queues (and their embedded scheduling policies) |
| `job_queues` | `map(object)` | `null` | Map of job queue definitions, each optionally including a fair-share scheduling policy |
| `job_definitions` | `map(object)` | `null` | Map of job definition configurations (container, multi-node, ECS, or EKS-based) |
| `tags` | `map(string)` | `{}` | Tags to add to all resources |

### IAM Roles

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_instance_iam_role` | `bool` | `true` | Create IAM role and instance profile for EC2/Spot compute environment instances |
| `create_service_iam_role` | `bool` | `true` | Create the AWS Batch service IAM role |
| `create_spot_fleet_iam_role` | `bool` | `false` | Create the Spot Fleet IAM role (required whenever any compute environment uses `type = "SPOT"`) |
| `instance_iam_role_additional_policies` | `map(string)` | `{}` | Additional policy ARNs to attach to the instance IAM role |
| `service_iam_role_additional_policies` | `map(string)` | `{}` | Additional policy ARNs to attach to the service IAM role |
| `spot_fleet_iam_role_additional_policies` | `map(string)` | `{}` | Additional policy ARNs to attach to the Spot Fleet IAM role |
| `instance_iam_role_name` / `service_iam_role_name` / `spot_fleet_iam_role_name` | `string` | `null` | Custom name (or prefix, see `*_use_name_prefix`) for each generated IAM role |
| `instance_iam_role_permissions_boundary` / `service_iam_role_permissions_boundary` / `spot_fleet_iam_role_permissions_boundary` | `string` | `null` | ARN of the permissions boundary policy for each role |

### Variable Object Shapes

The three map variables above accept deeply nested objects; the map key is used as the resource name/order key when the corresponding `name` attribute is omitted.

**`compute_environments[key]`**
- `type` — `MANAGED` (default) or `UNMANAGED`; `state` — `ENABLED` (default) or `DISABLED`
- `compute_resources.type` — `EC2`, `SPOT`, `FARGATE`, or `FARGATE_SPOT`; omit entirely when using `eks_configuration`
- `compute_resources.{max_vcpus, min_vcpus, instance_types, subnets, security_group_ids}` — required sizing/networking (`max_vcpus` and `subnets` are always required)
- `compute_resources.{allocation_strategy, bid_percentage}` — Spot tuning, e.g. `allocation_strategy = "SPOT_CAPACITY_OPTIMIZED"`
- `eks_configuration.{eks_cluster_arn, kubernetes_namespace}` — use **instead of** `compute_resources` to run Batch jobs as pods on an existing EKS cluster
- `update_policy.{job_execution_timeout_minutes, terminate_jobs_on_update}` — behavior for in-flight jobs when compute environment infrastructure updates

**`job_queues[key]`**
- `priority` (required, higher value = higher priority), `state` (default `ENABLED`)
- `compute_environment_order` — map keyed by numeric order (`0` = first) to `{ compute_environment_key = "<key from compute_environments>" }`
- `fair_share_policy` — optional (`compute_reservation`, `share_decay_seconds`, `share_distribution = [{ share_identifier, weight_factor }]`); creates an `aws_batch_scheduling_policy` (toggle with `create_scheduling_policy`, default `true`)
- `job_state_time_limit_action` — map of rules: `{ max_time_seconds, state = "RUNNABLE", action = "CANCEL", reason }` to auto-cancel/terminate stuck jobs

**`job_definitions[key]`**
- `type` — `container` (default) or `multinode`; `platform_capabilities = ["FARGATE"]` required for Fargate-backed jobs
- `container_properties` — `jsonencode({...})` string; used for EC2/Spot/Fargate container jobs (mutually exclusive with the two below)
- `eks_properties.pod_properties.containers` — map of pod containers (`image`, `command`, `resources.{limits,requests}`) for EKS-based jobs; still requires `type = "container"`
- `ecs_properties` — `jsonencode({...})` string for ECS task-style jobs with multiple, potentially dependent containers
- `node_properties` — `jsonencode({...})` string for `multinode` type HPC jobs (main node index, node range properties, node count)
- `retry_strategy.{attempts, evaluate_on_exit}` and `timeout.attempt_duration_seconds` — retry and runaway-job protection

## Main Outputs

| Output | Description |
|--------|-------------|
| `compute_environments` | Map of compute environments created and their attributes (ARN, ECS cluster ARN, status) |
| `job_queues` | Map of job queues created and their attributes (ARN, ARN of associated scheduling policy) |
| `job_definitions` | Map of job definitions created and their attributes (ARN, revision) |
| `scheduling_policies` | Map of fair-share scheduling policies created and their attributes |
| `instance_iam_role_arn` / `instance_iam_role_name` | ARN/name of the EC2 instance IAM role |
| `instance_iam_instance_profile_arn` | ARN of the instance profile attached to compute instances |
| `service_iam_role_arn` | ARN of the AWS Batch service IAM role |
| `spot_fleet_iam_role_arn` | ARN of the Spot Fleet IAM role |

## Usage Examples

### Example 1: EC2 + Spot Compute with Priority Queues and Fair-Share Scheduling

```hcl
module "batch" {
  source  = "terraform-aws-modules/batch/aws"
  version = "~> 3.1"

  create_spot_fleet_iam_role = true

  compute_environments = {
    a_ec2 = {
      name_prefix = "ec2"
      compute_resources = {
        type           = "EC2"
        min_vcpus      = 0
        max_vcpus      = 16
        instance_types = ["m5.large", "r5.large"]
        subnets        = ["subnet-30ef7b3c", "subnet-1ecda77b"]
        security_group_ids = ["sg-f1d03a88"]
      }
    }

    b_ec2_spot = {
      name_prefix = "ec2_spot"
      compute_resources = {
        type                = "SPOT"
        allocation_strategy = "SPOT_CAPACITY_OPTIMIZED"
        bid_percentage      = 100
        min_vcpus           = 0
        max_vcpus           = 64
        instance_types      = ["m5.large", "m5.xlarge", "c5.large", "r5.large"]
        subnets             = ["subnet-30ef7b3c", "subnet-1ecda77b"]
        security_group_ids  = ["sg-f1d03a88"]
      }
    }
  }

  job_queues = {
    low_priority = {
      name     = "LowPriorityEc2"
      priority = 1
      compute_environment_order = {
        0 = { compute_environment_key = "b_ec2_spot" }
        1 = { compute_environment_key = "a_ec2" }
      }
    }

    high_priority = {
      name     = "HighPriorityEc2"
      priority = 99
      compute_environment_order = {
        0 = { compute_environment_key = "a_ec2" }
      }

      fair_share_policy = {
        compute_reservation = 1
        share_decay_seconds = 3600
        share_distribution = [
          { share_identifier = "team-a*", weight_factor = 0.1 },
          { share_identifier = "team-b", weight_factor = 0.2 }
        ]
      }

      job_state_time_limit_action = {
        cancel_stuck_runnable = {
          max_time_seconds = 600
          reason           = "Stuck in RUNNABLE for over 10 minutes"
        }
      }
    }
  }

  job_definitions = {
    example = {
      name = "example"
      container_properties = jsonencode({
        command = ["echo", "hello"]
        image   = "public.ecr.aws/runecast/busybox:1.33.1"
        resourceRequirements = [
          { type = "VCPU", value = "1" },
          { type = "MEMORY", value = "1024" }
        ]
      })

      retry_strategy = {
        attempts = 3
        evaluate_on_exit = {
          retry_error   = { action = "RETRY", on_exit_code = 1 }
          exit_success  = { action = "EXIT", on_exit_code = 0 }
        }
      }
      timeout = { attempt_duration_seconds = 3600 }
    }
  }

  tags = {
    Environment = "dev"
  }
}
```

### Example 2: Fargate Compute Environment

```hcl
module "batch_fargate" {
  source  = "terraform-aws-modules/batch/aws"
  version = "~> 3.1"

  compute_environments = {
    fargate = {
      name_prefix = "fargate"
      compute_resources = {
        type                = "FARGATE"
        max_vcpus           = 4
        subnets             = ["subnet-xxx"]
        security_group_ids  = ["sg-xxx"]
      }
    }
  }

  job_queues = {
    fargate_queue = {
      name     = "fargate-queue"
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
          { type = "MEMORY", value = "2048" } # Fargate minimum is 2048 MB
        ]
        # Not created by this module - must exist beforehand
        executionRoleArn = "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
      })
    }
  }

  tags = {
    Environment = "dev"
  }
}
```

### Example 3: EKS-Based Compute Environment

```hcl
module "batch_eks" {
  source  = "terraform-aws-modules/batch/aws"
  version = "~> 3.1"

  compute_environments = {
    eks_main = {
      name_prefix = "eks"
      eks_configuration = {
        eks_cluster_arn      = aws_eks_cluster.this.arn
        kubernetes_namespace = "aws-batch"
      }
    }
  }

  job_queues = {
    eks_queue = {
      name     = "eks-queue"
      priority = 1
      compute_environment_order = {
        0 = { compute_environment_key = "eks_main" }
      }
    }
  }

  job_definitions = {
    eks_job = {
      name = "eks-example"
      type = "container" # EKS-based jobs still use type = "container"
      eks_properties = {
        pod_properties = {
          containers = {
            main = {
              image   = "public.ecr.aws/amazonlinux/amazonlinux:2023"
              command = ["sleep", "60"]
              resources = {
                limits = {
                  cpu    = "1"
                  memory = "1024Mi"
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### Example 4: Multi-Node Parallel Job for HPC Workloads

```hcl
module "batch_hpc" {
  source  = "terraform-aws-modules/batch/aws"
  version = "~> 3.1"

  compute_environments = {
    hpc = {
      name_prefix = "hpc"
      compute_resources = {
        type           = "EC2"
        min_vcpus      = 0
        max_vcpus      = 256
        instance_types = ["c5n.18xlarge"]
        subnets        = ["subnet-xxx"]
        security_group_ids = ["sg-xxx"]
        placement_group = "hpc-cluster"
      }
    }
  }

  job_queues = {
    hpc_queue = {
      name     = "hpc-queue"
      priority = 1
      compute_environment_order = {
        0 = { compute_environment_key = "hpc" }
      }
    }
  }

  job_definitions = {
    mpi_job = {
      name = "mpi-simulation"
      type = "multinode"
      node_properties = jsonencode({
        mainNode = 0
        numNodes = 4
        nodeRangeProperties = [
          {
            targetNodes = "0:"
            container = {
              image  = "my-mpi-image:latest"
              vcpus  = 36
              memory = 65536
              command = ["/opt/run-simulation.sh"]
            }
          }
        ]
      })
    }
  }
}
```

## Best Practices

### Compute Environment Configuration
1. **Prefer Managed Environments**: Use `type = "MANAGED"` (the default) so AWS Batch handles scaling and instance lifecycle
2. **Scale to Zero**: Set `min_vcpus = 0` so idle compute environments incur no EC2 cost between job bursts
3. **Diversify Instance Types**: Specify several `instance_types` (or `["optimal"]`) to widen Spot capacity pools
4. **Use `SPOT_CAPACITY_OPTIMIZED`**: Prefer this `allocation_strategy` over `SPOT_CAPACITY_OPTIMIZED_PRIORITIZED`/bid-based strategies for interruption resilience
5. **Set an Update Policy**: Configure `update_policy.terminate_jobs_on_update` deliberately — `false` lets running jobs finish, `true` forces a clean cutover

### Job Queue & Scheduling Design
1. **Order Environments by Preference**: Lower `compute_environment_order` keys are tried first (e.g., Spot before on-demand)
2. **Separate Queues by Priority**: Use distinct queues with different `priority` values rather than one shared queue
3. **Apply Fair-Share Policies in Multi-Tenant Queues**: Use `fair_share_policy.share_distribution` so no single team/`share_identifier` starves others
4. **Guard Against Stuck Jobs**: Configure `job_state_time_limit_action` to auto-cancel jobs stuck in `RUNNABLE` beyond a reasonable window

### Job Definition Configuration
1. **Right-Size Resource Requirements**: Request only the `VCPU`/`MEMORY` actually needed in `resourceRequirements`
2. **Pick the Right Job Type**: `container_properties` for standard single-container jobs, `ecs_properties` for multi-container task-style jobs, `eks_properties` for Kubernetes-native jobs, `node_properties` + `type = "multinode"` for tightly-coupled HPC — these are mutually exclusive
3. **Always Set Retry & Timeout**: Define `retry_strategy.evaluate_on_exit` and `timeout.attempt_duration_seconds` to avoid runaway or silently-failing jobs
4. **Use ECR for Images**: Store container images in Amazon ECR for fast, reliable pulls from compute environments

### Security
1. **Least-Privilege IAM**: Grant only the policies each role needs via `instance_iam_role_additional_policies` / `service_iam_role_additional_policies`
2. **Use Private Subnets**: Deploy `compute_resources.subnets` in private subnets with NAT/VPC endpoint egress
3. **Store Secrets Externally**: Reference AWS Secrets Manager or SSM Parameter Store from `secrets`/environment injection rather than hardcoding values in `container_properties`
4. **Scope Execution Roles**: Fargate/ECS `executionRoleArn` and job `jobRoleArn` should be scoped to the minimum permissions the container needs

### Cost Optimization
1. **Maximize Spot Usage**: Combine `type = "SPOT"` with `SPOT_CAPACITY_OPTIMIZED` for fault-tolerant batch workloads
2. **Scale to Zero**: `min_vcpus = 0` on every compute environment eliminates idle spend
3. **Use Fargate for Short/Bursty Jobs**: Avoids EC2 instance warm-up latency for small, intermittent workloads
4. **Tag for Cost Allocation**: Apply consistent `tags` across the module call for cost tracking and chargeback

## Important Gotchas

1. **Nested Variables Default to `null`, Not `{}`**: `compute_environments`, `job_queues`, and `job_definitions` all default to `null` (module v3.x) — you must explicitly define at least one entry in each for the module to provision a working pipeline
2. **Tag Changes Force Replacement**: Modifying `compute_resources.tags` forces compute environment replacement, which can transiently disrupt job queues referencing it
3. **Fargate Requirements**: Fargate/`FARGATE_SPOT` job definitions require `platform_capabilities = ["FARGATE"]`, a minimum of 2048 MB memory, and an `executionRoleArn` — none of which is created by this module
4. **Job Property Blocks Are Mutually Exclusive**: Set exactly one of `container_properties`, `ecs_properties`, `eks_properties`, or `node_properties` per job definition, matching its `type`
5. **EKS Jobs Still Use `type = "container"`**: There is no separate `type = "eks"`; EKS-based jobs are container-type jobs that use `eks_properties` instead of `container_properties`
6. **Spot Requires the Spot Fleet Role**: Set `create_spot_fleet_iam_role = true` whenever any compute environment uses `type = "SPOT"`
7. **Map Keys Are Load-Bearing**: `compute_environment_order[n].compute_environment_key` must match a key in `compute_environments`; every resource's `name` falls back to its map key when omitted
8. **Version Compatibility**: Module v3.x requires Terraform >= 1.5.7 and AWS provider >= 6.28 (region override, ECS/EKS properties). For older AWS provider (< 6.0) setups, pin to the module's 2.x major version line instead

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-batch
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/batch/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-batch/tree/master/examples
- **Module Changelog**: https://github.com/terraform-aws-modules/terraform-aws-batch/blob/master/CHANGELOG.md
- **AWS Batch Documentation**: https://docs.aws.amazon.com/batch/latest/userguide/what-is-batch.html
- **Compute Environments**: https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html
- **AWS Batch on Amazon EKS**: https://docs.aws.amazon.com/batch/latest/userguide/batch-eks.html
- **Job Queues & Fair-Share Scheduling**: https://docs.aws.amazon.com/batch/latest/userguide/fair-share-scheduling.html
- **Job Definitions**: https://docs.aws.amazon.com/batch/latest/userguide/job_definitions.html
- **Multi-Node Parallel Jobs**: https://docs.aws.amazon.com/batch/latest/userguide/multi-node-parallel-jobs.html
- **AWS Batch Best Practices**: https://docs.aws.amazon.com/batch/latest/userguide/best-practices.html
- **AWS Batch Pricing**: https://aws.amazon.com/batch/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Choose the Compute Type Deliberately**: `EC2`/`SPOT` for full instance control, `FARGATE`/`FARGATE_SPOT` for serverless, or omit `compute_resources` and set `eks_configuration` to run on an existing EKS cluster
2. **Remember Defaults Are `null`**: You must populate `compute_environments`, `job_queues`, and `job_definitions` explicitly — an empty/omitted call creates only the optional IAM roles
3. **Spot Needs the Fleet Role**: Always pair `type = "SPOT"` compute resources with `create_spot_fleet_iam_role = true`
4. **Match Job Definition Fields to Type**: `container_properties` (default `container`), `ecs_properties` (`container` type, multi-container ECS-style), `eks_properties` (`container` type, EKS pods), or `node_properties` (`multinode` type, HPC) — never combine more than one
5. **Fargate Checklist**: `platform_capabilities = ["FARGATE"]`, `executionRoleArn` present, memory >= 2048 MB
6. **Job Queue Wiring**: `compute_environment_order` keys are numeric priority order (`0` = first); values reference `compute_environment_key` from `compute_environments`
7. **Multi-Tenant Fairness**: Add `fair_share_policy.share_distribution` on shared queues; add `job_state_time_limit_action` to bound stuck-job duration
8. **Resource Requirements Syntax**: In `container_properties`/`ecs_properties`, specify `resourceRequirements = [{ type = "VCPU", value = "1" }, { type = "MEMORY", value = "1024" }]`
9. **ECR Image References**: Use full URIs, e.g. `"123456789012.dkr.ecr.us-east-1.amazonaws.com/image:tag"`
10. **Name Fallbacks**: If a resource's `name` attribute is omitted, the map key is used — keep map keys meaningful
11. **Provider Version Gate**: `region` variable, `ecs_properties`, and `eks_configuration.image_kubernetes_version` require AWS provider >= 6.x; use module version `~> 2.x` for older provider pins
