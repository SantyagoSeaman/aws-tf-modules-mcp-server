---
module_name: autoscaling
keywords: [autoscaling, asg, auto-scaling-group, ec2, scaling, launch-template, instance-refresh, lifecycle-hooks, mixed-instances, spot-instances, scaling-policy, target-tracking, scheduled-scaling, load-balancer, elb, alb, nlb, capacity, high-availability, elasticity, instance-lifecycle, health-check, warmup, cooldown, termination-policy, availability-zones, multi-az, instance-type, ami, user-data, tags, metrics, cloudwatch, monitoring, desired-capacity, min-size, max-size, scale-out, scale-in, cpu-utilization, network-traffic, application-load, instance-protection, capacity-rebalancing, hibernation, spot-fleet, on-demand, instance-weighting, launch-configuration, placement-group, suspended-processes, termination-protection, imdsv2, metadata-service, iam-instance-profile, security-groups, key-pair, ebs-optimized, detailed-monitoring, instance-maintenance, warm-pool, predictive-scaling]
---

# Terraform AWS Auto Scaling Module

## Module Information

- **Module Name**: `autoscaling`
- **Source**: `terraform-aws-modules/autoscaling/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-autoscaling
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/autoscaling/aws/latest
- **Latest Version**: 9.0.1
- **Purpose**: Terraform module that creates and manages AWS Auto Scaling Groups with launch templates for dynamic infrastructure scaling
- **Service**: AWS Auto Scaling (Amazon EC2 Auto Scaling)
- **Category**: Compute, High Availability, Scalability
- **Keywords**: autoscaling, asg, auto-scaling-group, ec2, scaling, launch-template, instance-refresh, lifecycle-hooks, mixed-instances, spot-instances, scaling-policy, target-tracking, scheduled-scaling, load-balancer, elb, alb, nlb, capacity, high-availability, elasticity, instance-lifecycle, health-check, warmup, cooldown, termination-policy, availability-zones, multi-az, instance-type, ami, user-data, tags, metrics, cloudwatch, monitoring, desired-capacity, min-size, max-size, scale-out, scale-in, cpu-utilization, network-traffic, application-load, instance-protection, capacity-rebalancing, hibernation, spot-fleet, on-demand, instance-weighting, launch-configuration, placement-group, suspended-processes, termination-protection, imdsv2, metadata-service, iam-instance-profile, security-groups, key-pair, ebs-optimized, detailed-monitoring, instance-maintenance, warm-pool, predictive-scaling
- **Use For**: Dynamic web application scaling, containerized application deployment, batch processing workloads, microservices architectures, cost optimization with spot instances, high availability application hosting, variable traffic handling, disaster recovery implementations, multi-tier application infrastructure, CI/CD auto-scaling environments, gaming server fleets, data processing pipelines

## Description

This Terraform module provides a comprehensive solution for creating and managing AWS Auto Scaling Groups (ASG) with modern launch template configurations. The module abstracts the complexity of ASG setup while providing extensive customization options for instance configuration, scaling policies, lifecycle management, and integration with other AWS services. It enables automated infrastructure scaling based on demand, ensuring applications maintain performance while optimizing costs through dynamic capacity management.

The module supports advanced features including mixed instances policies for combining on-demand and spot instances, instance refresh for zero-downtime deployments, lifecycle hooks for custom actions during instance launch and termination, and detailed monitoring configurations. It creates and manages associated resources such as launch templates, IAM instance profiles, and integrates seamlessly with Elastic Load Balancers (ELB, ALB, NLB) for distributing traffic across dynamically scaled instances.

Built with AWS best practices in mind, the module implements security features like IMDSv2 enforcement for instance metadata protection, supports capacity rebalancing for spot instance workloads, and provides flexible configuration options for health checks, termination policies, and availability zone distribution. The module's conditional resource creation capabilities and comprehensive tagging support make it suitable for both simple web application scaling and complex, multi-tier architectures requiring sophisticated scaling strategies.

## Key Features

- **Launch Template Management**: Creates and configures AWS launch templates with comprehensive EC2 instance settings including AMI, instance type, and user data
- **Auto Scaling Group Creation**: Manages ASG with configurable capacity settings (min, max, desired), availability zones, and VPC integration
- **Mixed Instances Policy**: Supports combining on-demand and spot instances with instance type weighting and allocation strategies for cost optimization
- **Instance Refresh**: Enables zero-downtime rolling updates with configurable refresh strategies, minimum healthy percentage, and warmup periods
- **Lifecycle Hooks**: Configures custom actions during instance launch and termination for integration with external systems
- **Scaling Policies**: Supports target tracking, step scaling, and simple scaling policies for dynamic capacity management
- **Scheduled Scaling**: Enables time-based scaling actions for predictable traffic patterns
- **Load Balancer Integration**: Seamless integration with Classic ELB, Application Load Balancer (ALB), and Network Load Balancer (NLB)
- **IAM Instance Profile**: Creates and attaches IAM roles and instance profiles for EC2 instance permissions
- **Security Configuration**: Implements IMDSv2 enforcement, security group attachment, and SSH key pair management
- **Health Check Configuration**: Configurable health check types (EC2, ELB), grace periods, and termination behavior
- **Capacity Rebalancing**: Automatic spot instance rebalancing to maintain availability during interruptions
- **Termination Policies**: Flexible termination policies (OldestInstance, NewestInstance, OldestLaunchTemplate, etc.)
- **Instance Protection**: Supports scale-in protection for specific instances
- **Detailed Monitoring**: CloudWatch detailed monitoring enablement for enhanced metrics
- **Placement Groups**: Configure cluster, partition, or spread placement groups for instance distribution
- **EBS Optimization**: Enable EBS-optimized instances for improved storage performance
- **Network Interface Configuration**: Detailed network interface settings including multiple ENIs, IPv6 support, and elastic IPs
- **User Data Management**: Flexible user data configuration with Base64 encoding support
- **Tagging Strategy**: Comprehensive tagging with propagation to instances and volumes
- **Warm Pool Support**: Configure warm pools for faster scaling response times
- **Suspended Processes**: Ability to suspend specific scaling processes (Launch, Terminate, HealthCheck, etc.)
- **Instance Hibernation**: Support for instance hibernation for stateful workloads
- **Conditional Creation**: Granular control over resource creation with boolean flags
- **Metadata Options**: Configure instance metadata service options including IMDSv2 enforcement and hop limits

## Main Use Cases

1. **Web Application Scaling**: Automatically scale web servers based on traffic patterns with ELB integration
2. **Microservices Deployment**: Deploy and scale containerized applications with ECS or Kubernetes integration
3. **Batch Processing**: Scale compute resources for data processing pipelines with scheduled scaling
4. **Cost Optimization**: Reduce infrastructure costs using mixed instances policy with spot and on-demand instances
5. **High Availability Applications**: Distribute instances across multiple availability zones with automatic failover
6. **CI/CD Build Agents**: Scale build and test infrastructure based on pipeline demand
7. **Gaming Server Fleets**: Dynamically scale gaming server capacity based on player demand
8. **API Backend Services**: Scale API servers behind Application Load Balancers based on request metrics
9. **Data Analytics Workloads**: Scale EMR or Spark clusters for variable data processing requirements
10. **Disaster Recovery**: Maintain standby capacity with warm pools for rapid failover scenarios

## Best Practices

### Design and Architecture

1. **Multi-AZ Distribution**: Deploy instances across at least 3 availability zones for maximum availability and fault tolerance
2. **Right-Size Instance Types**: Use mixed instances policy with multiple instance types to balance performance and cost
3. **Separate ASGs by Function**: Create dedicated ASGs for different application tiers (web, app, worker) for independent scaling
4. **Use Launch Templates**: Always use launch templates (not launch configurations) for modern features and better management
5. **Capacity Planning**: Set minimum capacity to handle baseline load and maximum capacity with sufficient headroom for growth
6. **Placement Strategy**: Use spread placement groups for critical applications requiring high availability

### Scaling Configuration

1. **Target Tracking Policies**: Prefer target tracking scaling policies over step scaling for automatic and responsive scaling
2. **Appropriate Metrics**: Scale based on meaningful metrics (CPU utilization, request count, queue depth) aligned with application behavior
3. **Warmup Periods**: Configure appropriate warmup periods (typically 120-300 seconds) to allow instances to initialize before receiving traffic
4. **Cooldown Periods**: Set cooldown periods to prevent thrashing from rapid scale-out/scale-in cycles
5. **Scale-Out vs Scale-In**: Scale out aggressively (respond quickly to load) but scale in conservatively (avoid premature termination)
6. **Scheduled Scaling**: Use scheduled scaling for predictable traffic patterns to pre-warm capacity before expected load increases
7. **Instance Protection**: Enable scale-in protection for instances handling long-running tasks or stateful operations

### Health Checks and Monitoring

1. **ELB Health Checks**: Use ELB health checks for load-balanced applications to ensure only healthy instances receive traffic
2. **Health Check Grace Period**: Set grace period (300-600 seconds) to allow adequate time for application initialization
3. **Detailed Monitoring**: Enable detailed CloudWatch monitoring (1-minute intervals) for responsive scaling decisions
4. **Custom Metrics**: Publish application-specific metrics to CloudWatch for domain-aware scaling policies
5. **Lifecycle Hooks for Monitoring**: Use lifecycle hooks to register instances with monitoring systems during launch
6. **Termination Notifications**: Configure lifecycle hooks to gracefully drain connections before instance termination

### Security

1. **IMDSv2 Enforcement**: Enforce IMDSv2 for instance metadata access to prevent SSRF attacks
2. **Minimal IAM Permissions**: Attach IAM instance profiles with least privilege principle following specific application needs
3. **Security Group Management**: Use dedicated security groups for ASG instances with minimal required ingress rules
4. **Private Subnets**: Launch instances in private subnets with NAT gateway for outbound internet access
5. **Encrypted Volumes**: Enable EBS encryption for all volumes using KMS keys
6. **SSH Key Management**: Use Systems Manager Session Manager instead of SSH keys when possible
7. **Instance Profile Rotation**: Regularly rotate IAM roles and review attached policies

### Cost Optimization

1. **Spot Instances**: Leverage spot instances for fault-tolerant workloads with 50-90% cost savings
2. **Mixed Instances Policy**: Use 70/30 or 80/20 spot-to-on-demand ratio for cost-optimized availability
3. **Instance Family Diversification**: Specify multiple instance types in mixed instances policy for better spot availability
4. **Capacity Rebalancing**: Enable capacity rebalancing to proactively replace spot instances at risk of interruption
5. **Right-Sizing**: Regularly review CloudWatch metrics and right-size instance types based on actual utilization
6. **Scheduled Scaling for Dev/Test**: Scale down or terminate non-production ASGs during off-hours
7. **Reserved Instances for Baseline**: Use reserved instances or savings plans for predictable baseline capacity

### Operational Excellence

1. **Instance Refresh Strategy**: Use instance refresh for rolling updates with minimum healthy percentage of 90% or higher
2. **Lifecycle Hook Integration**: Implement lifecycle hooks to deregister instances from service discovery and drain connections
3. **Comprehensive Tagging**: Apply consistent tags including environment, application, cost center, and owner for resource management
4. **Version Launch Templates**: Use versioned launch templates and explicitly reference versions for predictable deployments
5. **Testing Scaling Policies**: Test scaling policies in non-production environments before production deployment
6. **Suspended Processes**: Temporarily suspend processes (ReplaceUnhealthy, AZRebalance) during maintenance windows
7. **Warm Pool Configuration**: Configure warm pools for applications requiring fast scale-out response times (sub-60 seconds)
8. **Instance Refresh Checkpoints**: Use checkpoint delays during instance refresh to validate application health

### High Availability and Disaster Recovery

1. **Cross-AZ Distribution**: Ensure instances are balanced across availability zones using AZRebalance process
2. **Minimum Healthy Instances**: Configure instance refresh with minimum healthy percentage of 90% to maintain availability
3. **ELB Connection Draining**: Use lifecycle hooks and deregistration delay to gracefully terminate instances
4. **Health Check Redundancy**: Combine EC2 and ELB health checks for comprehensive instance health validation
5. **Termination Policies**: Use appropriate termination policies (OldestLaunchTemplate) to prioritize outdated instances
6. **AMI Update Strategy**: Regularly update AMIs with security patches using instance refresh for zero-downtime updates
7. **Backup Launch Templates**: Maintain previous launch template versions as rollback points

### Integration and Deployment

1. **Load Balancer Pre-Warming**: Pre-warm load balancers before major traffic events by contacting AWS support
2. **Service Discovery Integration**: Use lifecycle hooks to register instances with Consul, Eureka, or AWS Cloud Map
3. **CI/CD Integration**: Automate ASG updates using Terraform in CI/CD pipelines with proper state locking
4. **Blue-Green Deployments**: Maintain separate ASGs for blue-green deployment strategies with traffic shifting
5. **Container Orchestration**: Integrate ASGs with ECS capacity providers or Kubernetes cluster autoscaler
6. **DNS Updates**: Use Route 53 health checks and DNS failover for multi-region ASG deployments
7. **Notification Configuration**: Configure SNS notifications for scaling events and lifecycle hook timeouts

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-autoscaling
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/autoscaling/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-autoscaling/tree/master/examples
- **AWS Auto Scaling Documentation**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html
- **Launch Template Documentation**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-templates.html
- **Scaling Policies Guide**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-simple-step.html
- **Target Tracking Policies**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html
- **Instance Refresh Documentation**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html
- **Lifecycle Hooks Guide**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html
- **Mixed Instances Policy**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-mixed-instances-groups.html
- **Capacity Rebalancing**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-capacity-rebalancing.html
- **IMDSv2 Best Practices**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **Auto Scaling Best Practices**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-best-practices.html
- **AWS Auto Scaling Pricing**: https://aws.amazon.com/autoscaling/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Capacity Planning**: Always set reasonable min, max, and desired capacity values based on expected load patterns
2. **Launch Template Requirements**: Ensure AMI, instance type, and VPC configuration are provided for launch template creation
3. **Security Groups**: Configure security groups before ASG creation and ensure they allow required traffic patterns
4. **Subnet Selection**: Use vpc_zone_identifier to specify subnets across multiple availability zones for high availability
5. **Health Check Configuration**: Configure appropriate health check grace periods (typically 300-600 seconds) for application initialization
6. **IAM Permissions**: Ensure the Terraform execution role has permissions to create IAM instance profiles and launch templates
7. **Scaling Policies**: Implement target tracking scaling policies for automatic and responsive capacity management
8. **Load Balancer Integration**: When integrating with load balancers, ensure target groups are created before ASG
9. **Instance Refresh**: Use instance refresh with appropriate minimum healthy percentage (90%+) for zero-downtime updates
10. **Lifecycle Hooks**: Configure lifecycle hooks for graceful instance initialization and termination
11. **Monitoring**: Enable detailed CloudWatch monitoring for better visibility into ASG performance
12. **Tagging Strategy**: Apply comprehensive tags to ASGs for cost allocation, automation, and resource management
13. **Spot Instance Strategy**: When using spot instances, specify multiple instance types and enable capacity rebalancing
14. **Update Strategy**: Use versioned launch templates and explicit version references for predictable deployments
15. **Testing**: Test scaling policies and instance refresh in non-production environments before production deployment
