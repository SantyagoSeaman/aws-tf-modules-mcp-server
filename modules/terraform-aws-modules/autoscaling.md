# Terraform AWS Auto Scaling Module

## Module Information

- **Module Name**: `autoscaling`
- **Source**: `terraform-aws-modules/autoscaling/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-autoscaling
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/autoscaling/aws/latest
- **Latest Version**: 8.0.1
- **Purpose**: Terraform module that creates and manages AWS Auto Scaling Groups with launch templates for dynamic infrastructure scaling
- **Service**: AWS Auto Scaling (Amazon EC2 Auto Scaling)
- **Category**: Compute, High Availability, Scalability
- **Keywords**: autoscaling, asg, ec2, scaling, launch-template, instance-refresh, mixed-instances, spot-instances, scaling-policy, target-tracking, load-balancer, warm-pool, lifecycle-hooks, iam-instance-profile, capacity-rebalancing
- **Use For**: Dynamic web application scaling, containerized application deployment, batch processing workloads, microservices architectures, cost optimization with spot instances, high availability application hosting, variable traffic handling, CI/CD auto-scaling environments

## Description

This Terraform module provides a comprehensive solution for creating and managing AWS Auto Scaling Groups (ASG) with modern launch template configurations. The module abstracts the complexity of ASG setup while providing extensive customization options for instance configuration, scaling policies, lifecycle management, and integration with other AWS services. It enables automated infrastructure scaling based on demand, ensuring applications maintain performance while optimizing costs through dynamic capacity management.

The module supports advanced features including mixed instances policies for combining on-demand and spot instances, instance refresh for zero-downtime deployments, lifecycle hooks for custom actions during instance launch and termination, and warm pools for faster scaling response. It creates and manages associated resources such as launch templates, IAM instance profiles, and integrates seamlessly with Elastic Load Balancers (ELB, ALB, NLB) for distributing traffic across dynamically scaled instances.

Built with AWS best practices in mind, the module implements security features like IMDSv2 enforcement for instance metadata protection (enabled by default), supports capacity rebalancing for spot instance workloads, and provides flexible configuration options for health checks, termination policies, and availability zone distribution.

## Key Features

- **Launch Template Management**: Creates and configures AWS launch templates with comprehensive EC2 instance settings including AMI, instance type, and user data
- **Auto Scaling Group Creation**: Manages ASG with configurable capacity settings (min, max, desired), availability zones, and VPC integration
- **Mixed Instances Policy**: Supports combining on-demand and spot instances with instance type weighting and allocation strategies for cost optimization
- **Instance Refresh**: Enables zero-downtime rolling updates with configurable refresh strategies, checkpoint percentages, and warmup periods
- **Lifecycle Hooks**: Configures custom actions during instance launch and termination for integration with external systems
- **Scaling Policies**: Supports target tracking, step scaling, and predictive scaling policies for dynamic capacity management
- **Scheduled Scaling**: Enables time-based scaling actions for predictable traffic patterns
- **Load Balancer Integration**: Seamless integration with Classic ELB, Application Load Balancer (ALB), and Network Load Balancer (NLB)
- **IAM Instance Profile**: Creates and attaches IAM roles and instance profiles for EC2 instance permissions
- **IMDSv2 Security**: Enforces token-based metadata service by default (AWS security best practice)
- **Health Check Configuration**: Configurable health check types (EC2, ELB), grace periods, and termination behavior
- **Capacity Rebalancing**: Automatic spot instance rebalancing to maintain availability during interruptions
- **Warm Pool Support**: Configure warm pools with pre-warmed stopped instances for faster scaling response times
- **Comprehensive Tagging**: Tag propagation to instances and volumes with flexible tagging strategies

## Main Use Cases

1. **Web Application Scaling**: Automatically scale web servers based on traffic patterns with ELB integration
2. **Microservices Deployment**: Deploy and scale containerized applications with ECS or Kubernetes integration
3. **Batch Processing**: Scale compute resources for data processing pipelines with scheduled scaling
4. **Cost Optimization**: Reduce infrastructure costs using mixed instances policy with spot and on-demand instances
5. **High Availability Applications**: Distribute instances across multiple availability zones with automatic failover
6. **CI/CD Build Agents**: Scale build and test infrastructure based on pipeline demand
7. **API Backend Services**: Scale API servers behind Application Load Balancers based on request metrics
8. **Disaster Recovery**: Maintain standby capacity with warm pools for rapid failover scenarios

## Submodules

This module does not have separate submodules. All functionality is contained in the root module.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | **Required** | Name used across all created resources |
| `min_size` | `number` | `null` | Minimum size of the Auto Scaling Group |
| `max_size` | `number` | `null` | Maximum size of the Auto Scaling Group |
| `desired_capacity` | `number` | `null` | Number of EC2 instances that should be running |
| `vpc_zone_identifier` | `list(string)` | `null` | List of subnet IDs to launch resources in |
| `health_check_type` | `string` | `null` | Health check type: `"EC2"` or `"ELB"` |
| `health_check_grace_period` | `number` | `null` | Seconds before health checks start after launch |
| `create_launch_template` | `bool` | `true` | Create launch template (false to use external) |
| `image_id` | `string` | `null` | AMI ID for EC2 instances |
| `instance_type` | `string` | `null` | EC2 instance type |
| `security_groups` | `list(string)` | `[]` | List of security group IDs |
| `user_data` | `string` | `null` | Base64-encoded user data script |
| `create_iam_instance_profile` | `bool` | `false` | Create IAM instance profile for EC2 instances |
| `iam_role_policies` | `map(string)` | `{}` | IAM policies to attach (map of name to ARN) |
| `use_mixed_instances_policy` | `bool` | `false` | Enable mixed instances policy |
| `mixed_instances_policy` | `object` | `null` | Mixed instances policy configuration |
| `instance_refresh` | `object` | `null` | Instance refresh configuration |
| `warm_pool` | `object` | `null` | Warm pool configuration |
| `scaling_policies` | `map(object)` | `null` | Map of scaling policy definitions |
| `schedules` | `map(object)` | `null` | Map of scheduled scaling actions |
| `capacity_rebalance` | `bool` | `null` | Enable capacity rebalancing for spot instances |
| `ignore_desired_capacity_changes` | `bool` | `false` | Ignore desired capacity changes in Terraform state |
| `tags` | `map(string)` | `{}` | Tags to apply to all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `autoscaling_group_id` | The autoscaling group ID |
| `autoscaling_group_arn` | The ARN of the AutoScaling Group |
| `autoscaling_group_name` | The autoscaling group name |
| `autoscaling_group_min_size` | Minimum size of the autoscale group |
| `autoscaling_group_max_size` | Maximum size of the autoscale group |
| `autoscaling_group_desired_capacity` | Desired number of instances |
| `launch_template_id` | The ID of the launch template |
| `launch_template_arn` | The ARN of the launch template |
| `launch_template_latest_version` | Latest version of the launch template |
| `iam_role_arn` | ARN of the IAM role |
| `iam_role_name` | Name of the IAM role |
| `iam_instance_profile_arn` | ARN of the instance profile |
| `autoscaling_policy_arns` | Map of scaling policy ARNs |
| `autoscaling_schedule_arns` | Map of schedule ARNs |

## Usage Examples

### Basic Auto Scaling Group

```hcl
module "asg" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "~> 8.0"

  name = "my-asg"

  min_size         = 0
  max_size         = 3
  desired_capacity = 1

  health_check_type = "EC2"
  vpc_zone_identifier = ["subnet-xxxxx", "subnet-yyyyy"]

  # Launch template configuration
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

```hcl
module "asg_mixed" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "~> 8.0"

  name = "mixed-instances-asg"

  min_size         = 0
  max_size         = 5
  desired_capacity = 2

  vpc_zone_identifier = ["subnet-xxxxx", "subnet-yyyyy"]
  health_check_type   = "EC2"
  capacity_rebalance  = true

  image_id = "ami-0123456789abcdef0"

  # Mixed instances policy for cost optimization
  use_mixed_instances_policy = true
  mixed_instances_policy = {
    instances_distribution = {
      on_demand_base_capacity                  = 1
      on_demand_percentage_above_base_capacity = 10
      spot_allocation_strategy                 = "capacity-optimized"
    }

    override = [
      { instance_type = "t3.micro", weighted_capacity = "1" },
      { instance_type = "t3.small", weighted_capacity = "2" },
      { instance_type = "t3.medium", weighted_capacity = "3" },
    ]
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
  version = "~> 8.0"

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

### Target Tracking Scaling Policy

```hcl
module "asg_scaling" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "~> 8.0"

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

    alb-request-count = {
      policy_type = "TargetTrackingScaling"
      target_tracking_configuration = {
        predefined_metric_specification = {
          predefined_metric_type = "ALBRequestCountPerTarget"
          resource_label         = "${module.alb.arn_suffix}/${module.alb.target_groups["ex"].arn_suffix}"
        }
        target_value = 1000.0
      }
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### ASG with IAM Instance Profile

```hcl
module "asg_with_iam" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "~> 8.0"

  name = "asg-with-iam"

  min_size         = 1
  max_size         = 3
  desired_capacity = 1

  vpc_zone_identifier = ["subnet-xxxxx"]
  image_id            = "ami-0123456789abcdef0"
  instance_type       = "t3.micro"

  # IAM instance profile creation
  create_iam_instance_profile = true
  iam_role_name               = "my-asg-role"
  iam_role_description        = "IAM role for ASG instances"
  iam_role_policies = {
    AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    CloudWatchAgentServerPolicy  = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  }

  tags = {
    Environment = "dev"
  }
}
```

## Best Practices

### Design and Architecture

1. **Multi-AZ Distribution**: Deploy instances across at least 3 availability zones for maximum availability and fault tolerance
2. **Right-Size Instance Types**: Use mixed instances policy with multiple instance types to balance performance and cost
3. **Separate ASGs by Function**: Create dedicated ASGs for different application tiers (web, app, worker) for independent scaling
4. **Use Launch Templates**: Always use launch templates (not launch configurations) for modern features and better management
5. **Capacity Planning**: Set minimum capacity to handle baseline load and maximum capacity with sufficient headroom for growth

### Scaling Configuration

1. **Target Tracking Policies**: Prefer target tracking scaling policies over step scaling for automatic and responsive scaling
2. **Appropriate Metrics**: Scale based on meaningful metrics (CPU utilization, request count, queue depth) aligned with application behavior
3. **Warmup Periods**: Configure appropriate warmup periods (typically 120-300 seconds) to allow instances to initialize before receiving traffic
4. **Cooldown Periods**: Set cooldown periods to prevent thrashing from rapid scale-out/scale-in cycles
5. **Scale-Out vs Scale-In**: Scale out aggressively (respond quickly to load) but scale in conservatively (avoid premature termination)
6. **Instance Protection**: Enable scale-in protection for instances handling long-running tasks or stateful operations

### Health Checks and Monitoring

1. **ELB Health Checks**: Use ELB health checks for load-balanced applications to ensure only healthy instances receive traffic
2. **Health Check Grace Period**: Set grace period (300-600 seconds) to allow adequate time for application initialization
3. **Detailed Monitoring**: Enable detailed CloudWatch monitoring (1-minute intervals) for responsive scaling decisions

### Security

1. **IMDSv2 Enforcement**: Module enforces IMDSv2 by default - do not disable unless absolutely necessary
2. **Minimal IAM Permissions**: Attach IAM instance profiles with least privilege principle
3. **Security Group Management**: Use dedicated security groups for ASG instances with minimal required ingress rules
4. **Private Subnets**: Launch instances in private subnets with NAT gateway for outbound internet access
5. **Encrypted Volumes**: Enable EBS encryption via `block_device_mappings` with `encrypted = true`

### Cost Optimization

1. **Spot Instances**: Leverage spot instances for fault-tolerant workloads with 50-90% cost savings
2. **Mixed Instances Policy**: Use 70/30 or 80/20 spot-to-on-demand ratio for cost-optimized availability
3. **Instance Family Diversification**: Specify multiple instance types in mixed instances policy for better spot availability
4. **Capacity Rebalancing**: Enable capacity rebalancing to proactively replace spot instances at risk of interruption
5. **Scheduled Scaling for Dev/Test**: Scale down or terminate non-production ASGs during off-hours

### Operational Excellence

1. **Instance Refresh Strategy**: Use instance refresh for rolling updates with minimum healthy percentage of 90% or higher
2. **Lifecycle Hook Integration**: Implement lifecycle hooks to deregister instances from service discovery and drain connections
3. **Comprehensive Tagging**: Apply consistent tags including environment, application, cost center, and owner
4. **Version Launch Templates**: Use versioned launch templates and explicitly reference versions for predictable deployments
5. **Warm Pool Configuration**: Configure warm pools for applications requiring fast scale-out response times (sub-60 seconds)

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-autoscaling
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/autoscaling/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-autoscaling/tree/master/examples
- **AWS Auto Scaling Documentation**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html
- **Launch Template Documentation**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-templates.html
- **Target Tracking Policies**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html
- **Instance Refresh Documentation**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html
- **Mixed Instances Policy**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-mixed-instances-groups.html
- **IMDSv2 Best Practices**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **Auto Scaling Best Practices**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-best-practices.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Required vs Practical Inputs**: Only `name` is technically required, but you typically need `min_size`, `max_size`, `vpc_zone_identifier`, and either `image_id`/`instance_type` or a launch template reference
2. **IAM Profile Creation**: Set `create_iam_instance_profile = true` explicitly - it defaults to `false`
3. **Instance Refresh with $Latest**: Using `launch_template_version = "$Latest"` won't trigger instance refresh when external template changes - use the launch template resource's `latest_version` output instead
4. **Lifecycle Hooks at Creation Only**: `initial_lifecycle_hooks` only apply during ASG creation; for updates, use separate `aws_autoscaling_lifecycle_hook` resources
5. **Desired Capacity Conflicts**: Set `ignore_desired_capacity_changes = true` if scaling policies or external systems should manage capacity without Terraform reverting changes
6. **Health Check Grace Period**: Always set appropriate `health_check_grace_period` to allow instances time to initialize before health checks begin
7. **Security Groups**: Configure security groups before ASG creation and ensure they allow required traffic patterns
8. **Subnet Selection**: Use `vpc_zone_identifier` with subnets across multiple availability zones for high availability
9. **IMDSv2 Default**: Module enforces IMDSv2 with single hop by default - this is AWS best practice, do not disable without understanding the security implications
10. **Target Groups**: When integrating with load balancers, ensure target groups are created before the ASG
11. **Monitoring**: Enable detailed CloudWatch monitoring for better visibility into ASG performance
12. **Spot Instance Strategy**: When using spot instances, specify multiple instance types and enable `capacity_rebalance = true`
13. **No Submodules**: This module has no submodules - all functionality is in the root module
14. **Version Pinning**: Always pin the module version (e.g., `version = "~> 8.0"`) for predictable deployments
