---
module_name: ec2-instance
keywords: [ec2, instance, virtual-machine, compute, spot-instance, on-demand, ami, ebs, elastic-block-store, instance-profile, iam-role, security-group, vpc, subnet, public-ip, private-ip, elastic-ip, network-interface, user-data, metadata, monitoring, tags, key-pair, ssh, linux, windows, t3, t2, m5, c5, instance-type, availability-zone, placement-group, tenancy, cpu-credits, ebs-optimized, source-dest-check, termination-protection, hibernation, capacity-reservation, ipv6, secondary-ip, elastic-network-interface, root-volume, additional-volumes, encrypted-volumes, kms, spot-price, spot-request, launch-template, associate-public-ip]
---

# Terraform AWS EC2 Instance Module

## Module Information

- **Module Name**: `ec2-instance`
- **Source**: `terraform-aws-modules/ec2-instance/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ec2-instance
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ec2-instance/aws/latest
- **Latest Version**: 6.1.1
- **Purpose**: Terraform module that creates AWS EC2 instance(s) resources with comprehensive configuration options
- **Service**: AWS EC2 (Elastic Compute Cloud)
- **Category**: Compute, Infrastructure
- **Keywords**: ec2, instance, virtual-machine, compute, spot-instance, on-demand, ami, ebs, elastic-block-store, instance-profile, iam-role, security-group, vpc, subnet, public-ip, private-ip, elastic-ip, network-interface, user-data, metadata, monitoring, tags, key-pair, ssh, linux, windows, t3, t2, m5, c5, instance-type, availability-zone, placement-group, tenancy, cpu-credits, ebs-optimized, source-dest-check, termination-protection, hibernation, capacity-reservation, ipv6, secondary-ip, elastic-network-interface, root-volume, additional-volumes, encrypted-volumes, kms, spot-price, spot-request, launch-template, associate-public-ip
- **Use For**: Application hosting, web servers, API backends, batch processing workloads, development and testing environments, database servers, continuous integration runners, microservices deployment, containerized applications, data processing pipelines, machine learning training instances, game servers

## Description

This Terraform module provides a flexible and comprehensive way to create and manage AWS EC2 instances with extensive configuration options. The module supports both single and multiple instance deployments, on-demand and spot instances, and integrates seamlessly with other AWS services such as IAM, VPC, security groups, and EBS volumes. It abstracts the complexity of EC2 instance configuration while providing granular control over instance settings, networking, storage, and security parameters.

The module is designed to handle common EC2 deployment patterns and use cases, from simple single-instance deployments to complex multi-instance architectures with custom networking and IAM configurations. It supports advanced features such as spot instance requests for cost optimization, custom IAM instance profiles for secure access to AWS services, multiple network interfaces for complex networking scenarios, and flexible EBS volume attachments for persistent storage. The module also handles AMI selection through direct AMI IDs or SSM parameters, making it easy to use the latest AWS-provided AMIs.

Key architectural features include conditional resource creation for environment-specific deployments, comprehensive tagging support for resource organization and cost allocation, and detailed metadata configuration for enhanced security and monitoring. The module is regularly maintained to support the latest Terraform and AWS provider versions, ensuring compatibility with modern infrastructure-as-code practices and AWS service features.

## Key Features

- **Single and Multiple Instance Support**: Create one or many EC2 instances with consistent configuration
- **Spot Instance Support**: Enable spot instances for cost-optimized workloads with configurable pricing
- **Flexible AMI Selection**: Use direct AMI IDs or SSM parameters for dynamic AMI selection
- **IAM Integration**: Create and attach IAM instance profiles for secure service access
- **Network Configuration**: Configure VPC, subnets, security groups, and multiple network interfaces
- **EBS Volume Management**: Attach and configure root and additional EBS volumes with encryption support
- **Public IP Assignment**: Control public IP allocation and Elastic IP association
- **IPv6 Support**: Enable and configure IPv6 addresses for instances
- **User Data Support**: Execute initialization scripts and cloud-init configurations
- **Monitoring and Logging**: Enable detailed CloudWatch monitoring and instance metadata options
- **Security Group Management**: Associate multiple security groups for layered security
- **Key Pair Configuration**: Configure SSH key pairs for instance access
- **Tenancy Options**: Support for default, dedicated, and host tenancy configurations
- **Placement Groups**: Configure placement groups for low-latency networking
- **CPU Credits**: Configure T-series instance CPU credit options (standard/unlimited)
- **EBS Optimization**: Enable EBS optimization for enhanced storage performance
- **Termination Protection**: Enable termination protection to prevent accidental deletion
- **Source/Destination Checks**: Configure network source/destination checking
- **Hibernation Support**: Enable instance hibernation for faster start times
- **Capacity Reservations**: Utilize EC2 capacity reservations for guaranteed availability
- **Comprehensive Tagging**: Support for instance, volume, and network interface tags
- **Conditional Creation**: Use the create flag to conditionally create resources
- **Metadata Service Configuration**: Configure IMDSv2 and metadata options for enhanced security
- **Credit Specification**: Configure CPU credit behavior for burstable instance types
- **Launch Templates**: Support for launch template configurations

## Main Use Cases

1. **Web Application Hosting**: Deploy web servers and application backends with load balancer integration
2. **Microservices Architecture**: Run containerized or standalone microservices with service discovery
3. **Development and Testing**: Create isolated development, staging, and testing environments
4. **Database Servers**: Host self-managed database instances with EBS-backed persistent storage
5. **CI/CD Runners**: Deploy build agents and continuous integration runners for automated pipelines
6. **Batch Processing**: Run scheduled batch jobs and data processing workloads on spot instances
7. **API Backends**: Host RESTful APIs and GraphQL services with auto-scaling capabilities
8. **Machine Learning Training**: Provision GPU or CPU instances for ML model training workloads
9. **Game Servers**: Deploy dedicated game servers with persistent storage and public IPs
10. **Data Processing Pipelines**: Run ETL jobs and data transformation workloads with temporary compute
11. **Legacy Application Migration**: Lift-and-shift traditional applications to AWS cloud infrastructure
12. **Bastion Hosts**: Create secure jump boxes for accessing private VPC resources

## Submodules

This module does not include submodules. It provides a single root module for EC2 instance creation and management.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create an instance |
| `name` | `string` | `""` | Name to be used on EC2 instance created |
| `ami` | `string` | `null` | ID of AMI to use for the instance |
| `ami_ssm_parameter` | `string` | `"/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"` | SSM parameter name for the AMI ID |
| `instance_type` | `string` | `"t3.micro"` | The type of instance to start |
| `availability_zone` | `string` | `null` | AZ to start the instance in |
| `subnet_id` | `string` | `null` | The VPC Subnet ID to launch in |
| `vpc_security_group_ids` | `list(string)` | `null` | A list of security group IDs to associate with |
| `key_name` | `string` | `null` | Key name of the Key Pair to use for the instance |
| `monitoring` | `bool` | `null` | If true, the launched EC2 instance will have detailed monitoring enabled |
| `associate_public_ip_address` | `bool` | `null` | Whether to associate a public IP address with an instance in a VPC |
| `private_ip` | `string` | `null` | Private IP address to associate with the instance in a VPC |
| `iam_instance_profile` | `string` | `null` | IAM Instance Profile to launch the instance with |
| `create_iam_instance_profile` | `bool` | `false` | Determines whether an IAM instance profile is created or to use an existing IAM instance profile |
| `iam_role_name` | `string` | `null` | Name to use on IAM role created |
| `iam_role_policies` | `map(string)` | `{}` | IAM policies to attach to the IAM role |
| `user_data` | `string` | `null` | The user data to provide when launching the instance |
| `user_data_base64` | `string` | `null` | Base64-encoded user data to provide when launching the instance |
| `user_data_replace_on_change` | `bool` | `null` | When used in combination with user_data will trigger a destroy and recreate when set to true |
| `enable_volume_tags` | `bool` | `true` | Whether to enable volume tags (if enabled it conflicts with root_block_device tags) |
| `root_block_device` | `list(any)` | `[]` | Customize details about the root block device of the instance |
| `ebs_block_device` | `list(any)` | `[]` | Additional EBS block devices to attach to the instance |
| `create_spot_instance` | `bool` | `false` | Depicts if the instance is a spot instance |
| `spot_price` | `string` | `null` | The maximum price to request on the spot market |
| `spot_type` | `string` | `null` | If set to one-time, after the instance is terminated, the spot request will be closed |
| `metadata_options` | `map(string)` | `{}` | Customize the metadata options of the instance |
| `enclave_options_enabled` | `bool` | `null` | Whether Nitro Enclaves will be enabled on the instance |
| `tags` | `map(string)` | `{}` | A mapping of tags to assign to the resource |

## Main Outputs

| Output | Description |
|--------|-------------|
| `id` | The ID of the instance |
| `arn` | The ARN of the instance |
| `instance_state` | The state of the instance |
| `public_dns` | The public DNS name assigned to the instance |
| `public_ip` | The public IP address assigned to the instance, if applicable |
| `private_dns` | The private DNS name assigned to the instance |
| `private_ip` | The private IP address assigned to the instance |
| `ipv6_addresses` | The IPv6 address assigned to the instance, if applicable |
| `primary_network_interface_id` | The ID of the instance's primary network interface |
| `availability_zone` | The availability zone of the created instance |
| `ami` | AMI ID that was used to create the instance |
| `spot_bid_status` | The current bid status of the Spot Instance Request |
| `spot_request_state` | The current request state of the Spot Instance Request |
| `spot_instance_id` | The Instance ID (if any) that is currently fulfilling the Spot Instance request |
| `iam_role_name` | The name of the IAM role |
| `iam_role_arn` | The Amazon Resource Name (ARN) specifying the IAM role |
| `iam_instance_profile_arn` | ARN assigned by AWS to the instance profile |
| `iam_instance_profile_id` | Instance profile's ID |
| `tags_all` | A map of tags assigned to the resource |

## Usage Examples

### Example 1: Basic EC2 Instance

```hcl
module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  name = "my-web-server"

  instance_type          = "t3.micro"
  ami                    = "ami-0c55b159cbfafe1f0"
  key_name               = "my-key-pair"
  monitoring             = true
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id              = "subnet-eddcdzz4"

  tags = {
    Terraform   = "true"
    Environment = "dev"
    Application = "web-server"
  }
}
```

### Example 2: Multiple Instances with for_each

```hcl
module "ec2_multiple" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  for_each = toset(["web-1", "web-2", "web-3"])

  name = "web-server-${each.key}"

  instance_type          = "t3.small"
  ami                    = "ami-0c55b159cbfafe1f0"
  key_name               = "my-key-pair"
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id              = "subnet-eddcdzz4"

  root_block_device = [{
    volume_type = "gp3"
    volume_size = 20
    encrypted   = true
  }]

  tags = {
    Terraform   = "true"
    Environment = "production"
  }
}
```

### Example 3: Spot Instance with IAM Role

```hcl
module "ec2_spot" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  name = "batch-processor"

  # Spot instance configuration
  create_spot_instance = true
  spot_price           = "0.05"
  spot_type            = "persistent"

  instance_type          = "c5.xlarge"
  ami_ssm_parameter      = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id              = "subnet-eddcdzz4"

  # Create IAM instance profile
  create_iam_instance_profile = true
  iam_role_name               = "batch-processor-role"
  iam_role_policies = {
    S3Access = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  }

  # User data for initialization
  user_data = base64encode(<<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    systemctl start docker
    systemctl enable docker
  EOF
  )

  tags = {
    Terraform   = "true"
    Environment = "production"
    Workload    = "batch-processing"
  }
}
```

### Example 4: Instance with Additional EBS Volumes

```hcl
module "ec2_database" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  name = "database-server"

  instance_type          = "m5.large"
  ami                    = "ami-0c55b159cbfafe1f0"
  key_name               = "my-key-pair"
  monitoring             = true
  vpc_security_group_ids = ["sg-database"]
  subnet_id              = "subnet-private-1"

  # Root volume configuration
  root_block_device = [{
    volume_type           = "gp3"
    volume_size           = 50
    encrypted             = true
    delete_on_termination = true
  }]

  # Additional data volume for database files
  ebs_block_device = [
    {
      device_name           = "/dev/sdf"
      volume_type           = "gp3"
      volume_size           = 100
      iops                  = 3000
      throughput            = 125
      encrypted             = true
      delete_on_termination = false
    }
  ]

  tags = {
    Terraform   = "true"
    Environment = "production"
    Purpose     = "database"
  }
}
```

### Example 5: Instance with Enhanced Security (IMDSv2)

```hcl
module "ec2_secure" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  name = "secure-application-server"

  instance_type          = "t3.medium"
  ami                    = "ami-0c55b159cbfafe1f0"
  key_name               = "my-key-pair"
  monitoring             = true
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id              = "subnet-private"

  # Enhanced metadata security (IMDSv2 only)
  metadata_options = {
    http_endpoint               = "enabled"
    http_tokens                 = "required"  # IMDSv2 only
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  # Create IAM role with specific permissions
  create_iam_instance_profile = true
  iam_role_name               = "app-server-role"
  iam_role_policies = {
    SecretsManager = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
    SSM            = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  }

  # Encrypted root volume
  root_block_device = [{
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
    kms_key_id  = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  }]

  tags = {
    Terraform   = "true"
    Environment = "production"
    Security    = "high"
  }
}
```

## Best Practices

### Security and Access Control

1. **Use IMDSv2**: Enable IMDSv2 (Instance Metadata Service Version 2) for enhanced security by setting `http_tokens = "required"` in metadata_options to prevent SSRF attacks.
2. **Implement IAM Roles**: Use IAM instance profiles instead of hardcoding credentials for accessing AWS services, following the principle of least privilege.
3. **Enable Encryption**: Always encrypt EBS volumes at rest using AWS KMS, especially for production workloads and sensitive data.
4. **Restrict Security Groups**: Use specific security group rules with minimal required ports and source IP ranges, avoiding 0.0.0.0/0 where possible.
5. **SSH Key Management**: Use unique SSH key pairs per environment and rotate them regularly, never sharing keys across environments.
6. **Enable Systems Manager**: Attach the `AmazonSSMManagedInstanceCore` policy to enable AWS Systems Manager Session Manager for secure shell access without SSH keys.
7. **Disable Public IPs**: For private workloads, avoid associating public IPs and use NAT gateways or VPC endpoints for outbound connectivity.
8. **Enable Termination Protection**: Set termination protection on critical instances to prevent accidental deletion.

### Monitoring and Observability

1. **Enable Detailed Monitoring**: Set `monitoring = true` to enable detailed CloudWatch monitoring for better visibility into instance metrics at 1-minute intervals.
2. **Implement CloudWatch Alarms**: Create alarms for key metrics such as CPU utilization, disk usage, memory pressure, and status checks.
3. **Configure CloudWatch Logs**: Use CloudWatch Logs agent to collect application and system logs for centralized monitoring and troubleshooting.
4. **Enable VPC Flow Logs**: Capture network traffic information for security analysis and troubleshooting.
5. **Use AWS CloudTrail**: Enable CloudTrail logging to track all API calls and changes to EC2 instances for audit and compliance.
6. **Tag All Resources**: Implement comprehensive tagging strategy including Environment, Owner, CostCenter, and Application for cost allocation and resource organization.

### Cost Optimization

1. **Right-Size Instances**: Start with smaller instance types and scale up based on actual usage patterns rather than overprovisioning.
2. **Use Spot Instances**: For fault-tolerant and flexible workloads, use spot instances to reduce costs by up to 90% compared to on-demand pricing.
3. **Enable EBS Optimization**: For workloads with high I/O requirements, enable EBS optimization to ensure consistent performance without additional network traffic.
4. **Use GP3 Volumes**: Migrate from GP2 to GP3 volumes for better performance-to-cost ratio with independent IOPS and throughput configuration.
5. **Implement Auto-Scaling**: Use Auto Scaling groups to automatically adjust capacity based on demand, terminating unused instances.
6. **Schedule Non-Production Instances**: Stop development and testing instances during off-hours to reduce costs.
7. **Use Reserved Instances**: For predictable workloads, purchase Reserved Instances or Savings Plans for significant cost savings over on-demand pricing.

### High Availability and Disaster Recovery

1. **Multi-AZ Deployment**: Deploy instances across multiple Availability Zones for high availability and fault tolerance.
2. **Regular Backups**: Implement automated EBS snapshot policies using AWS Backup or Data Lifecycle Manager for disaster recovery.
3. **Use Auto Recovery**: Enable auto recovery for EC2 instances to automatically recover from system status check failures.
4. **Implement Load Balancing**: Distribute traffic across multiple instances using Application Load Balancer or Network Load Balancer.
5. **Configure Health Checks**: Implement application-level health checks to detect and replace unhealthy instances automatically.
6. **Document Recovery Procedures**: Maintain runbooks for incident response and disaster recovery scenarios.

### Performance and Optimization

1. **Choose Appropriate Instance Types**: Select instance types optimized for your workload (compute-optimized, memory-optimized, storage-optimized, or general-purpose).
2. **Use Enhanced Networking**: For network-intensive applications, choose instances with enhanced networking support (ENA) for higher bandwidth and lower latency.
3. **Configure Placement Groups**: Use cluster placement groups for HPC workloads requiring low-latency network communication between instances.
4. **Optimize EBS Performance**: For databases and high-performance applications, use provisioned IOPS (io1/io2) volumes with appropriate IOPS configuration.
5. **Enable EBS-Optimized**: Ensure EBS-optimized is enabled for consistent storage performance, especially for production databases.
6. **Use Latest Generation Instances**: Migrate to the latest generation instance types (e.g., T3 instead of T2, M6i instead of M5) for better performance-to-cost ratio.

### Configuration Management

1. **Use User Data Carefully**: Keep user data scripts idempotent and minimal, preferring configuration management tools like Ansible, Chef, or Puppet for complex configurations.
2. **Separate Concerns**: Use separate modules for different components (compute, networking, storage) to maintain clean architecture and reusability.
3. **Implement Immutable Infrastructure**: Prefer creating new instances with updated AMIs rather than modifying running instances for consistency and reliability.
4. **Version Control AMIs**: Maintain versioned AMIs with required software and configurations for faster and consistent instance launches.
5. **Use Launch Templates**: Consider using launch templates for complex configurations that need to be reused across Auto Scaling groups and spot fleets.
6. **Validate Configurations**: Test instance configurations in non-production environments before deploying to production.

### Compliance and Governance

1. **Implement Tagging Policies**: Enforce mandatory tags using AWS Organizations tag policies or AWS Config rules for governance and cost allocation.
2. **Use AWS Config**: Enable AWS Config to continuously monitor and record resource configurations for compliance auditing.
3. **Regular Security Audits**: Conduct periodic security assessments using AWS Security Hub, Trusted Advisor, and third-party security tools.
4. **Patch Management**: Implement automated patching using AWS Systems Manager Patch Manager to keep instances up-to-date with security patches.
5. **Enable Encryption Everywhere**: Use KMS keys for EBS encryption and enforce encryption at rest and in transit for all data.
6. **Document Compliance Requirements**: Maintain documentation of compliance requirements (HIPAA, PCI-DSS, SOC2) and how the infrastructure meets them.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ec2-instance
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ec2-instance/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-ec2-instance/tree/master/examples
- **AWS EC2 Documentation**: https://docs.aws.amazon.com/ec2/
- **AWS EC2 Instance Types**: https://aws.amazon.com/ec2/instance-types/
- **EC2 Pricing**: https://aws.amazon.com/ec2/pricing/
- **EC2 Best Practices**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-best-practices.html
- **EC2 Security Best Practices**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security.html
- **IMDSv2**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **EBS Volume Types**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volume-types.html
- **EC2 Spot Instances**: https://aws.amazon.com/ec2/spot/
- **AWS Systems Manager**: https://docs.aws.amazon.com/systems-manager/
- **AWS Well-Architected Framework**: https://aws.amazon.com/architecture/well-architected/
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

## Notes for AI Agents

When using this module in automated workflows:

1. **Security First**: Always apply least privilege principle when creating IAM roles and security groups
2. **Use IAM Roles Over Keys**: Prefer IAM instance profiles with temporary credentials over SSH keys or hardcoded credentials
3. **Encrypt Everything**: Use KMS encryption for all EBS volumes, especially in production environments
4. **Enable IMDSv2**: Always configure `http_tokens = "required"` in metadata_options for enhanced security
5. **Tag Consistently**: Implement comprehensive tagging including Environment, Owner, CostCenter, and Application tags
6. **Monitor Usage**: Enable detailed monitoring and set up CloudWatch alarms for critical metrics
7. **Use Spot Wisely**: For cost optimization, use spot instances for stateless, fault-tolerant workloads with appropriate fallback strategies
8. **Test Before Production**: Always test instance configurations in development or staging environments before deploying to production
9. **Document Dependencies**: Clearly document dependencies on VPCs, security groups, subnets, and other resources
10. **Implement Backups**: Set up automated EBS snapshot schedules using AWS Backup or Data Lifecycle Manager
11. **Version Control**: Store all Terraform configurations in version control with proper branching and review processes
12. **Regular Audits**: Review and rotate credentials regularly, audit IAM policies, and perform security assessments
