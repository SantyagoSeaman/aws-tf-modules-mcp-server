# Terraform AWS Autoscaling Module

## Module Information

- **Module Name**: `autoscaling`
- **Module ID**: `terraform-aws-modules/autoscaling/aws`
- **Source**: `terraform-aws-modules/autoscaling/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-autoscaling
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/autoscaling/aws/latest
- **Latest Version**: 9.2.1
- **Purpose**: Terraform module that creates an AWS Auto Scaling Group (ASG) together with its EC2 launch template and optional IAM instance profile, scaling policies, schedules, and load balancer attachments
- **Service**: AWS Auto Scaling (Amazon EC2 Auto Scaling)
- **Category**: Compute, High Availability, Scalability
- **Keywords**: autoscaling, asg, ec2, launch-template, mixed-instances-policy, spot-instances, instance-refresh, scaling-policy, target-tracking, step-scaling, predictive-scaling, warm-pool, lifecycle-hooks, iam-instance-profile, imdsv2, capacity-rebalance, traffic-source-attachment, scheduled-scaling
- **Use For**: dynamic web application scaling, containerized/microservices deployment behind a load balancer, batch and CI/CD compute pools, cost optimization with spot/mixed-instances, zero-downtime rolling deployments via instance refresh, predictable time-based scaling, high-availability multi-AZ fleets, standby capacity with warm pools

## Description

This module provisions an AWS Auto Scaling Group and its associated `aws_launch_template`, wiring together instance configuration (AMI, instance type or attribute-based `instance_requirements`, block devices, network interfaces, metadata options), capacity settings, and health checks into a single resource graph. It can create a new launch template or attach the ASG to an externally managed one, and it optionally creates an IAM role and instance profile for the EC2 instances (`create_iam_instance_profile`).

Beyond the base group, the module manages the full lifecycle surface of Auto Scaling: mixed-instances policies for blending on-demand and spot capacity, instance refresh for rolling/zero-downtime updates, initial lifecycle hooks, warm pools, an instance maintenance policy, scheduled actions (`schedules`), and scaling policies (`scaling_policies`) covering target tracking, step scaling, and predictive scaling — all expressed as maps so multiple policies/schedules can be declared per group without extra `for_each` boilerplate in the caller. Load balancer/target-group and VPC Lattice integration is handled via the `traffic_source_attachments` map, which creates one `aws_autoscaling_traffic_source_attachment` resource per entry.

Security defaults follow AWS best practice: `metadata_options` enforces IMDSv2 (`http_tokens = "required"`, single-hop `http_put_response_hop_limit = 1`) out of the box. The module has no functional submodules — a `wrappers/` directory exists only for the standard terraform-aws-modules Terragrunt/`for_each` wrapper pattern and proxies all root variables without adding behavior. As of v9, this module requires Terraform >= 1.5.7 and AWS provider >= 6.33, and is maintained by Anton Babenko under the Apache 2.0 license.

## Key Features

- **Launch Template Management**: Creates and versions an `aws_launch_template` (AMI, instance type/`instance_requirements`, user data, EBS optimization, monitoring) or attaches to an externally created one
- **Two ASG Creation Modes**: Standard ASG, or one with `desired_capacity` changes ignored (`ignore_desired_capacity_changes`) so scaling policies/external tools can manage capacity without Terraform drift
- **Mixed Instances Policy**: Combines on-demand + spot capacity with instance-type overrides, weighted capacity, and allocation strategies (`use_mixed_instances_policy`, `mixed_instances_policy`)
- **Attribute-Based Instance Selection**: `instance_requirements` lets AWS pick instance types matching vCPU/memory/architecture constraints instead of a fixed `instance_type`
- **Instance Refresh**: Rolling updates with checkpoints, warmup, min/max healthy percentage, auto-rollback, and CloudWatch alarm-triggered rollback (`alarm_specification`)
- **Scaling Policies**: Target tracking, step scaling, and predictive scaling, all declared as a single `scaling_policies` map
- **Scheduled Scaling**: Time-based (cron or fixed start/end) capacity changes via the `schedules` map
- **Load Balancer / Traffic Source Integration**: `traffic_source_attachments` map attaches ALB/NLB target groups (`elbv2`) or VPC Lattice target groups to the ASG
- **Lifecycle Hooks & Warm Pools**: `initial_lifecycle_hooks` for launch/terminate automation; `warm_pool` for pre-provisioned standby instances
- **IAM Instance Profile**: Optionally creates an IAM role + instance profile and attaches managed policies (`iam_role_policies`)
- **IMDSv2 Enforced by Default**: `metadata_options` defaults to `http_tokens = "required"`, hop limit `1`
- **Capacity Rebalancing**: Proactively replaces at-risk spot instances (`capacity_rebalance`)
- **Fine-Grained Instance Config**: Block device mappings, network interfaces, placement, capacity reservations, CPU options, credit specification, Nitro Enclaves/hibernation options
- **Comprehensive Tagging**: Separate tag maps for the ASG, launch template, IAM role, and per-tag propagation control (`autoscaling_group_tags_not_propagate_at_launch`)

## Main Use Cases

1. **Web Application Scaling**: Scale web/API tiers behind an ALB using target-tracking on request count or CPU
2. **Microservices & Container Hosts**: Provide the underlying EC2 capacity for ECS/self-managed Kubernetes worker fleets
3. **Cost-Optimized Compute**: Blend spot and on-demand instances via `mixed_instances_policy` for 50-90% savings on fault-tolerant workloads
4. **Zero-Downtime Deployments**: Roll out new AMIs/launch template versions with `instance_refresh` and health-check gating
5. **Batch & CI/CD Build Fleets**: Scale build agents or batch workers up/down with schedules or queue-depth-based policies
6. **High Availability Fleets**: Distribute instances across multiple AZs/subnets via `vpc_zone_identifier`
7. **Predictable Traffic Patterns**: Use `schedules` to scale ahead of known daily/weekly load changes
8. **Disaster Recovery / Fast Scale-Out**: Maintain pre-warmed standby capacity with `warm_pool` for sub-minute scale response
9. **Forecast-Driven Scaling**: Use `PredictiveScaling` policies to scale ahead of forecasted load based on historical metrics

## Submodules

This module does not ship separate functional submodules. It includes a `wrappers/` module — the standard terraform-aws-modules wrapper that exposes the same variables/outputs through a single `for_each`-friendly interface for Terragrunt-style multi-instance usage. It adds no new resources or behavior, so it is not documented separately here; use the root module directly unless you specifically need the wrapper's `for_each` pattern.

## Main Input Variables

### Autoscaling Group Core

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | **Required** | Name used across all created resources |
| `create` | `bool` | `true` | Whether to create the autoscaling group |
| `min_size` / `max_size` / `desired_capacity` | `number` | `null` | ASG capacity bounds and target |
| `vpc_zone_identifier` | `list(string)` | `null` | Subnet IDs to launch into (conflicts with `availability_zones`) |
| `availability_zones` | `list(string)` | `null` | AZs to launch into when not using subnets |
| `health_check_type` | `string` | `null` | `"EC2"` or `"ELB"` |
| `health_check_grace_period` | `number` | `null` | Seconds before health checks start after launch |
| `ignore_desired_capacity_changes` | `bool` | `false` | Ignore `desired_capacity` drift so scaling policies/external tools own it |
| `capacity_rebalance` | `bool` | `null` | Proactively replace spot instances at risk of interruption |
| `protect_from_scale_in` | `bool` | `false` | Protect instances in this group from termination during scale-in |
| `termination_policies` | `list(string)` | `[]` | Order/strategy used to pick instances for termination |
| `suspended_processes` | `list(string)` | `[]` | ASG processes to suspend (e.g. `AZRebalance`) |
| `max_instance_lifetime` | `number` | `null` | Max seconds an instance may run before forced replacement |
| `tags` / `autoscaling_group_tags` | `map(string)` | `{}` | Tags on all resources / ASG-only tags |

### Launch Template & Instance Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_launch_template` | `bool` | `true` | Create a launch template (set `false` to use an external one via `launch_template_id`) |
| `image_id` | `string` | `null` | AMI ID |
| `instance_type` | `string` | `null` | EC2 instance type (mutually exclusive with `instance_requirements`) |
| `instance_requirements` | `object` | `null` | Attribute-based instance type selection (vCPU, memory, etc.) |
| `security_groups` | `list(string)` | `[]` | Security group IDs (omit if setting SGs per-interface in `network_interfaces`) |
| `user_data` | `string` | `null` | Base64-encoded user data script |
| `block_device_mappings` | `list(object)` | `null` | EBS/instance-store volumes to attach |
| `network_interfaces` | `list(object)` | `null` | Per-ENI network config (SGs, public IP, delete-on-termination) |
| `metadata_options` | `object` | IMDSv2 required, hop limit `1` | Instance metadata service options — **security-sensitive**, avoid loosening |
| `capacity_reservation_specification` | `object` | `null` | Target/open capacity reservations |
| `credit_specification` | `object` | `null` | Burstable (`t*`) instance CPU credit mode |
| `instance_market_options` | `object` | `null` | Spot market options (`market_type = "spot"`, max price, etc.) |
| `enable_monitoring` | `bool` | `true` | Detailed CloudWatch monitoring |
| `update_default_version` | `bool` | `null` | Update launch template default version on every change |

### IAM Role / Instance Profile

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_iam_instance_profile` | `bool` | `false` | Create a new IAM role + instance profile |
| `iam_instance_profile_arn` | `string` | `null` | Use an existing instance profile (when `create_iam_instance_profile = false`) |
| `iam_role_name` | `string` | `null` | IAM role name (used as prefix by default) |
| `iam_role_policies` | `map(string)` | `{}` | Map of policy name → ARN to attach to the created role |
| `iam_role_permissions_boundary` | `string` | `null` | Permissions boundary ARN for the created role |

### Scaling, Schedules, Refresh & Attachments

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `use_mixed_instances_policy` | `bool` | `false` | Enable mixed instances policy |
| `mixed_instances_policy` | `object` | `null` | Instance distribution + `launch_template.override` list (see v9 syntax note below) |
| `instance_refresh` | `object` | `null` | Rolling refresh strategy, preferences, and triggers |
| `instance_maintenance_policy` | `object` | `null` | Min/max healthy percentage during instance replacement |
| `warm_pool` | `object` | `null` | Warm pool size and reuse policy |
| `scaling_policies` | `map(object)` | `null` | Map of target-tracking / step / predictive scaling policies |
| `schedules` | `map(object)` | `null` | Map of scheduled capacity changes (cron or fixed start/end) |
| `traffic_source_attachments` | `map(object)` | `null` | Map attaching ALB/NLB target groups or VPC Lattice (`traffic_source_type`, default `"elbv2"`) |
| `initial_lifecycle_hooks` | `list(object)` | `null` | Lifecycle hooks applied **only at ASG creation** |

## Main Outputs

| Output | Description |
|--------|-------------|
| `autoscaling_group_id` | The autoscaling group ID |
| `autoscaling_group_arn` | The ARN of the autoscaling group |
| `autoscaling_group_name` | The autoscaling group name |
| `autoscaling_group_min_size` / `_max_size` / `_desired_capacity` | Current group sizing |
| `autoscaling_group_availability_zones` / `_vpc_zone_identifier` | Resolved AZ / subnet placement |
| `autoscaling_group_load_balancers` / `_target_group_arns` | Attached classic ELB names / target group ARNs |
| `autoscaling_group_health_check_type` / `_health_check_grace_period` | Effective health-check config |
| `launch_template_id` / `launch_template_arn` / `launch_template_name` | Launch template identifiers |
| `launch_template_latest_version` / `launch_template_default_version` | Launch template versions (use `latest_version` when referencing an external template for instance refresh triggers) |
| `iam_role_arn` / `iam_role_name` | Created IAM role identifiers |
| `iam_instance_profile_arn` / `iam_instance_profile_id` | Instance profile identifiers |
| `autoscaling_policy_arns` | Map of scaling policy name → ARN |
| `autoscaling_schedule_arns` | Map of schedule name → ARN |

## Usage Examples

### Basic Auto Scaling Group

```hcl
module "asg" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "~> 9.0"

  name = "my-asg"

  min_size         = 0
  max_size         = 3
  desired_capacity = 1

  health_check_type   = "EC2"
  vpc_zone_identifier = ["subnet-xxxxx", "subnet-yyyyy"]

  image_id      = "ami-0123456789abcdef0"
  instance_type = "t3.micro"

  security_groups = [module.security_group.security_group_id]

  tags = {
    Environment = "dev"
    Project     = "example"
  }
}
```

### Mixed Instances with Spot for Cost Optimization

Note: since v9, `override` moved under `mixed_instances_policy.launch_template` (it was a top-level key in v8).

```hcl
module "asg_mixed" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "~> 9.0"

  name = "mixed-instances-asg"

  min_size         = 0
  max_size         = 5
  desired_capacity = 2

  vpc_zone_identifier = ["subnet-xxxxx", "subnet-yyyyy"]
  health_check_type   = "EC2"
  capacity_rebalance  = true

  image_id = "ami-0123456789abcdef0"

  use_mixed_instances_policy = true
  mixed_instances_policy = {
    instances_distribution = {
      on_demand_base_capacity                  = 1
      on_demand_percentage_above_base_capacity = 10
      spot_allocation_strategy                 = "capacity-optimized"
    }

    launch_template = {
      override = [
        { instance_type = "t3.micro", weighted_capacity = "1" },
        { instance_type = "t3.small", weighted_capacity = "2" },
        { instance_type = "t3.medium", weighted_capacity = "3" },
      ]
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Instance Refresh for Zero-Downtime Updates

```hcl
module "asg_refresh" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "~> 9.0"

  name = "asg-with-refresh"

  min_size         = 2
  max_size         = 10
  desired_capacity = 4

  vpc_zone_identifier = ["subnet-xxxxx", "subnet-yyyyy"]
  image_id            = "ami-0123456789abcdef0"
  instance_type       = "t3.small"

  instance_refresh = {
    strategy = "Rolling"
    preferences = {
      checkpoint_delay             = 600
      checkpoint_percentages       = [35, 70, 100]
      instance_warmup              = 300
      min_healthy_percentage       = 50
      max_healthy_percentage       = 100
      auto_rollback                = true
      scale_in_protected_instances = "Refresh"
      standby_instances            = "Terminate"
    }
    triggers = ["tag"]
  }

  tags = {
    Environment = "production"
  }
}
```

### Target Tracking + Step Scaling Policies

```hcl
module "asg_scaling" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "~> 9.0"

  name = "asg-with-scaling"

  min_size         = 1
  max_size         = 10
  desired_capacity = 2

  vpc_zone_identifier = ["subnet-xxxxx", "subnet-yyyyy"]
  image_id            = "ami-0123456789abcdef0"
  instance_type       = "t3.small"

  scaling_policies = {
    cpu-target-tracking = {
      policy_type = "TargetTrackingScaling"
      target_tracking_configuration = {
        predefined_metric_specification = {
          predefined_metric_type = "ASGAverageCPUUtilization"
        }
        target_value = 50.0
      }
    }

    scale-out-step = {
      policy_type      = "StepScaling"
      adjustment_type  = "ChangeInCapacity"
      step_adjustment = [
        { scaling_adjustment = 1, metric_interval_lower_bound = 0, metric_interval_upper_bound = 10 },
        { scaling_adjustment = 2, metric_interval_lower_bound = 10 },
      ]
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### IAM Instance Profile + Load Balancer Attachment

```hcl
module "asg_with_alb" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "~> 9.0"

  name = "asg-with-alb"

  min_size         = 2
  max_size         = 6
  desired_capacity = 2

  vpc_zone_identifier = ["subnet-xxxxx", "subnet-yyyyy"]
  image_id            = "ami-0123456789abcdef0"
  instance_type       = "t3.micro"
  health_check_type   = "ELB"

  # Attach to an ALB target group
  traffic_source_attachments = {
    ex-alb = {
      traffic_source_identifier = module.alb.target_groups["ex_asg"].arn
      traffic_source_type       = "elbv2"
    }
  }

  create_iam_instance_profile = true
  iam_role_name                = "my-asg-role"
  iam_role_description         = "IAM role for ASG instances"
  iam_role_policies = {
    AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    CloudWatchAgentServerPolicy  = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  }

  block_device_mappings = [
    {
      device_name = "/dev/xvda"
      ebs = {
        delete_on_termination = true
        encrypted              = true
        volume_size            = 20
        volume_type             = "gp3"
      }
    }
  ]

  tags = {
    Environment = "production"
  }
}
```

## Best Practices

### Design and Architecture

1. **Multi-AZ Distribution**: Deploy across at least 3 availability zones (via `vpc_zone_identifier` with subnets in different AZs) for fault tolerance
2. **Launch Templates Only**: This module always uses launch templates (not launch configurations); do not mix in legacy launch configuration resources
3. **Separate ASGs by Function**: Create dedicated ASGs per application tier (web, app, worker) so they can scale independently
4. **Capacity Planning**: Set `min_size` to baseline load and `max_size` with enough headroom for spikes

### Scaling Configuration

1. **Prefer Target Tracking**: Use `TargetTrackingScaling` policies over `StepScaling` for automatic, self-correcting scaling
2. **Meaningful Metrics**: Scale on metrics aligned with application behavior (CPU, ALB request count per target, queue depth via custom metrics)
3. **Warmup Periods**: Set `instance_warmup`/`default_instance_warmup` (typically 120-300s) so new instances don't skew scaling metrics before they're ready
4. **Scale-Out vs Scale-In**: Scale out aggressively, scale in conservatively to avoid premature termination and flapping
5. **Instance Protection**: Set `protect_from_scale_in = true` for instances running long-lived or stateful work

### Health Checks and Monitoring

1. **ELB Health Checks**: Use `health_check_type = "ELB"` for load-balanced applications so only healthy instances receive traffic
2. **Grace Period**: Set `health_check_grace_period` (300-600s) to allow application startup before health checks begin
3. **Detailed Monitoring**: Set `enable_monitoring = true` (the default) for 1-minute CloudWatch metrics and more responsive scaling

### Security

1. **Do Not Loosen IMDSv2**: The default `metadata_options` (token required, hop limit 1) is an AWS security best practice — only override with a clear justification
2. **Least-Privilege IAM**: Attach only the managed/customer policies actually needed via `iam_role_policies`; use `iam_role_permissions_boundary` for delegated environments
3. **Private Subnets**: Launch instances in private subnets with a NAT gateway/instance for outbound access when they don't need public IPs
4. **Encrypt Volumes**: Set `encrypted = true` on every `block_device_mappings[].ebs` entry
5. **Dedicated Security Groups**: Use narrowly scoped security groups (via `security_groups` or per-`network_interfaces` entry) rather than reusing broad ones

### Cost Optimization

1. **Mixed Instances Policy**: Blend spot and on-demand via `mixed_instances_policy.instances_distribution` for 50-90% savings on fault-tolerant workloads
2. **Diversify Instance Types**: List multiple instance types under `mixed_instances_policy.launch_template.override` to improve spot capacity availability
3. **Capacity Rebalancing**: Set `capacity_rebalance = true` to proactively replace at-risk spot instances before interruption
4. **Scheduled Scaling for Non-Prod**: Use `schedules` to scale down/off dev and test ASGs outside business hours

### Operational Excellence

1. **Instance Refresh for Rollouts**: Use `instance_refresh` with `min_healthy_percentage >= 50` and `auto_rollback = true` (optionally tied to a CloudWatch alarm via `alarm_specification`) for safe rolling deployments
2. **Lifecycle Hooks**: Use `initial_lifecycle_hooks` for deregistration/draining automation at creation time; for hooks added later, manage a separate `aws_autoscaling_lifecycle_hook` resource outside this module
3. **Consistent Tagging**: Apply environment/application/owner tags via `tags`, and use `autoscaling_group_tags_not_propagate_at_launch` for ASG-only metadata that shouldn't land on instances
4. **Pin the Module Version**: Always pin (e.g. `version = "~> 9.0"`) — v9 introduced breaking changes vs v8 (see Notes for AI Agents)
5. **Warm Pools for Fast Scale-Out**: Configure `warm_pool` when sub-60-second scale-out response is required

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-autoscaling
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/autoscaling/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-autoscaling/tree/master/examples/complete
- **v8 → v9 Upgrade Guide**: https://github.com/terraform-aws-modules/terraform-aws-autoscaling/blob/master/docs/UPGRADE-9.0.md
- **AWS Auto Scaling Documentation**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html
- **Target Tracking Policies**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html
- **Instance Refresh Documentation**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html
- **Mixed Instances Policy**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-mixed-instances-groups.html
- **IMDSv2 Best Practices**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Required vs Practical Inputs**: Only `name` is technically required, but a working ASG needs `min_size`, `max_size`, `vpc_zone_identifier` (or `availability_zones`), and either `image_id` + `instance_type`/`instance_requirements`, or `create_launch_template = false` with `launch_template_id` pointing to an external template
2. **v9 Breaking Change — Mixed Instances Override**: `mixed_instances_policy.override` (v8) is now `mixed_instances_policy.launch_template.override` (v9+). Generating v8-style HCL against this module version will fail to validate
3. **No Direct LB Attributes**: There is no `target_group_arns`/`load_balancers` input on the ASG. Attach load balancers/target groups (or VPC Lattice) via the `traffic_source_attachments` map (`traffic_source_type` defaults to `"elbv2"`)
4. **IAM Profile Creation Is Opt-In**: `create_iam_instance_profile` defaults to `false`; set it explicitly `true` to create a role, or supply `iam_instance_profile_arn` to attach an existing one
5. **`instance_type` vs `instance_requirements`**: These are mutually exclusive — set exactly one
6. **External Launch Template + Instance Refresh**: Using `launch_template_version = "$Latest"` with an externally managed launch template will NOT trigger `instance_refresh` when that external template changes; reference the external `aws_launch_template` resource's `latest_version` output explicitly instead
7. **Lifecycle Hooks at Creation Only**: `initial_lifecycle_hooks` only applies when the ASG is first created; for hooks added to an existing ASG, use a standalone `aws_autoscaling_lifecycle_hook` resource
8. **Desired Capacity Conflicts**: Set `ignore_desired_capacity_changes = true` when scaling policies or external systems (not Terraform) should own `desired_capacity`, to avoid perpetual plan diffs
9. **IMDSv2 Default**: The module enforces IMDSv2 with a single hop by default — do not disable without understanding the security implications (this satisfies AWS Security Hub control `autoscaling.4`)
10. **Version Pinning**: Pin the module version (e.g. `version = "~> 9.0"`); Terraform >= 1.5.7 and AWS provider >= 6.33 are required
11. **No Real Submodules**: The only extra module in the repo is `wrappers/`, a generic `for_each` proxy with no independent behavior — reference the root module directly in generated code
12. **Cosmetic Variable**: `putin_khuylo` (default `true`) is a symbolic, non-functional variable present in all terraform-aws-modules repos; it has no effect on created resources and can be left at its default
