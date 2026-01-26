# Terraform AWS EC2 Instance Module

## Module Information

- **Module Name**: `ec2-instance`
- **Source**: `terraform-aws-modules/ec2-instance/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ec2-instance
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ec2-instance/aws/latest
- **Latest Version**: 6.2.0
- **Purpose**: Terraform module that creates AWS EC2 instance(s) with comprehensive configuration for compute, networking, storage, and IAM
- **Service**: AWS EC2 (Elastic Compute Cloud)
- **Category**: Compute, Infrastructure
- **Keywords**: ec2, instance, compute, spot-instance, ami, ebs, iam-role, security-group, vpc, subnet, user-data, metadata, imdsv2, elastic-ip, network-interface, hibernation
- **Use For**: Application hosting, web servers, API backends, batch processing, development environments, database servers, CI/CD runners, microservices, bastion hosts, machine learning workloads

## Description

This Terraform module provides a flexible and comprehensive way to create and manage AWS EC2 instances with extensive configuration options. The module supports both single and multiple instance deployments (using `for_each`), on-demand and spot instances, and integrates seamlessly with other AWS services such as IAM, VPC, security groups, and EBS volumes. It abstracts the complexity of EC2 instance configuration while providing granular control over instance settings, networking, storage, and security parameters.

The module handles common EC2 deployment patterns from simple single-instance deployments to complex architectures with custom networking and IAM configurations. It supports advanced features such as spot instance requests for cost optimization, built-in IAM instance profile creation, multiple network interfaces, flexible EBS volume attachments, and Elastic IP management. The module also handles AMI selection through direct AMI IDs or SSM parameters for dynamic, up-to-date AMI selection.

Key architectural features include IMDSv2 enabled by default for enhanced security, conditional resource creation for environment-specific deployments, comprehensive tagging support, and detailed metadata configuration. The module is actively maintained to support the latest Terraform and AWS provider versions.

## Key Features

- **Single and Multiple Instance Support**: Create one or many EC2 instances with consistent configuration using `for_each`
- **Spot Instance Support**: Enable spot instances for cost-optimized workloads with configurable pricing and interruption behavior
- **Flexible AMI Selection**: Use direct AMI IDs or SSM parameters for dynamic AMI selection with optional ignore changes
- **Built-in IAM Integration**: Create IAM instance profiles and roles directly within the module with customizable policy attachments
- **Security Group Management**: Create and configure security groups with customizable ingress/egress rules
- **Elastic IP Support**: Optionally create and associate Elastic IPs with instances
- **Network Configuration**: Configure VPC, subnets, security groups, and multiple network interfaces with IPv6 support
- **EBS Volume Management**: Attach and configure root and additional EBS volumes with encryption and KMS support
- **IMDSv2 by Default**: Enhanced security with Instance Metadata Service v2 required by default
- **User Data Support**: Execute initialization scripts and cloud-init configurations with optional replace-on-change behavior
- **Monitoring and Logging**: Enable detailed CloudWatch monitoring
- **Tenancy and Placement**: Support for default, dedicated, and host tenancy with placement group configuration
- **CPU Configuration**: Configure CPU credits (standard/unlimited) and CPU options (core count, threads per core)
- **Hibernation Support**: Enable instance hibernation for faster start times
- **Termination Protection**: Enable termination and stop protection to prevent accidental deletion
- **Comprehensive Tagging**: Support for instance, volume, IAM, and security group tags
- **Conditional Creation**: Granular resource creation control via feature flags

## Main Use Cases

1. **Web Application Hosting**: Deploy web servers and application backends with load balancer integration
2. **Microservices Architecture**: Run containerized or standalone microservices with service discovery
3. **Development and Testing**: Create isolated development, staging, and testing environments
4. **Database Servers**: Host self-managed database instances with EBS-backed persistent storage
5. **CI/CD Runners**: Deploy build agents and continuous integration runners for automated pipelines
6. **Batch Processing**: Run scheduled batch jobs and data processing workloads on spot instances
7. **API Backends**: Host RESTful APIs and GraphQL services with auto-scaling capabilities
8. **Machine Learning Training**: Provision GPU or CPU instances for ML model training workloads
9. **Bastion Hosts**: Create secure jump boxes for accessing private VPC resources
10. **Session Manager Access**: Deploy instances with private network access via AWS Systems Manager

## Submodules

This module does not include submodules. It provides a single root module for EC2 instance creation and management.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create an instance |
| `name` | `string` | `""` | Name to be used on EC2 instance created |
| `ami` | `string` | `null` | ID of AMI to use for the instance |
| `ami_ssm_parameter` | `string` | `"/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"` | SSM parameter name for the AMI ID |
| `ignore_ami_changes` | `bool` | `false` | Whether changes to the AMI ID should be ignored by Terraform |
| `instance_type` | `string` | `"t3.micro"` | The type of instance to start |
| `availability_zone` | `string` | `null` | AZ to start the instance in |
| `subnet_id` | `string` | `null` | The VPC Subnet ID to launch in |
| `vpc_security_group_ids` | `list(string)` | `[]` | A list of security group IDs to associate with |
| `key_name` | `string` | `null` | Key name of the Key Pair to use for the instance |
| `monitoring` | `bool` | `null` | If true, enables detailed CloudWatch monitoring |
| `associate_public_ip_address` | `bool` | `null` | Whether to associate a public IP address with an instance in a VPC |
| `private_ip` | `string` | `null` | Private IP address to associate with the instance in a VPC |
| `user_data` | `string` | `null` | The user data to provide when launching the instance |
| `user_data_base64` | `string` | `null` | Base64-encoded user data to provide when launching the instance |
| `user_data_replace_on_change` | `bool` | `null` | Trigger a destroy and recreate when user_data changes |
| `metadata_options` | `object` | `{http_endpoint="enabled", http_put_response_hop_limit=1, http_tokens="required"}` | Customize the metadata options (IMDSv2 required by default) |
| `root_block_device` | `object` | `null` | Customize root block device (encryption, size, type, IOPS, throughput, KMS key) |
| `ebs_volumes` | `map(object)` | `null` | Additional EBS volumes to attach to the instance |
| `enable_volume_tags` | `bool` | `true` | Whether to enable volume tags (conflicts with root_block_device tags) |
| `disable_api_termination` | `bool` | `null` | If true, enables EC2 Instance Termination Protection |
| `disable_api_stop` | `bool` | `null` | If true, enables EC2 Instance Stop Protection |
| `ebs_optimized` | `bool` | `null` | If true, the launched EC2 instance will be EBS-optimized |
| `hibernation` | `bool` | `null` | If true, the launched EC2 instance will support hibernation |
| `cpu_credits` | `string` | `null` | The credit option for CPU usage (unlimited or standard) |
| `cpu_options` | `object` | `null` | CPU options (core_count, threads_per_core, amd_sev_snp) |
| `tenancy` | `string` | `null` | Instance tenancy (default, dedicated, host) |
| `placement_group` | `string` | `null` | The Placement Group to start the instance in |
| `tags` | `map(string)` | `{}` | A mapping of tags to assign to the resource |

**Spot Instance Variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_spot_instance` | `bool` | `false` | Depicts if the instance is a spot instance |
| `spot_price` | `string` | `null` | The maximum price to request on the spot market |
| `spot_type` | `string` | `null` | one-time or persistent |
| `spot_instance_interruption_behavior` | `string` | `null` | terminate, stop, or hibernate |
| `spot_wait_for_fulfillment` | `bool` | `null` | Wait for Spot Request to be fulfilled |

**IAM Instance Profile Variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `iam_instance_profile` | `string` | `null` | IAM Instance Profile name to launch the instance with (existing) |
| `create_iam_instance_profile` | `bool` | `false` | Determines whether an IAM instance profile is created |
| `iam_role_name` | `string` | `null` | Name to use on IAM role created |
| `iam_role_policies` | `map(string)` | `{}` | Policies attached to the IAM role |
| `iam_role_permissions_boundary` | `string` | `null` | ARN of the policy for permissions boundary |

**Security Group Variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_security_group` | `bool` | `true` | Determines whether a security group will be created |
| `security_group_name` | `string` | `null` | Name to use on security group created |
| `security_group_vpc_id` | `string` | `null` | VPC ID to create the security group in |
| `security_group_ingress_rules` | `map(object)` | `null` | Ingress rules to add to the security group |
| `security_group_egress_rules` | `map(object)` | `{allow_all_ipv4, allow_all_ipv6}` | Egress rules (defaults to allow all traffic) |

**Elastic IP Variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_eip` | `bool` | `false` | Determines whether a public EIP will be created and associated |
| `eip_domain` | `string` | `"vpc"` | Indicates if this EIP is for use in VPC |

## Main Outputs

| Output | Description |
|--------|-------------|
| `id` | The ID of the instance |
| `arn` | The ARN of the instance |
| `instance_state` | The state of the instance |
| `ami` | AMI ID that was used to create the instance |
| `availability_zone` | The availability zone of the created instance |
| `public_dns` | The public DNS name assigned to the instance |
| `public_ip` | The public IP address assigned to the instance (includes EIP if created) |
| `private_dns` | The private DNS name assigned to the instance |
| `private_ip` | The private IP address assigned to the instance |
| `ipv6_addresses` | The IPv6 address assigned to the instance |
| `primary_network_interface_id` | The ID of the instance's primary network interface |
| `root_block_device` | Root block device information |
| `ebs_block_device` | EBS block device information |
| `ebs_volumes` | Map of EBS volumes created and their attributes |
| `spot_bid_status` | The current bid status of the Spot Instance Request |
| `spot_request_state` | The current request state of the Spot Instance Request |
| `spot_instance_id` | The Instance ID fulfilling the Spot Instance request |
| `iam_role_name` | The name of the IAM role |
| `iam_role_arn` | The ARN of the IAM role |
| `iam_instance_profile_arn` | ARN assigned by AWS to the instance profile |
| `iam_instance_profile_id` | Instance profile's ID |
| `security_group_arn` | Amazon Resource Name (ARN) of the security group |
| `security_group_id` | ID of the security group |
| `tags_all` | A map of tags assigned to the resource |

## Usage Examples

### Example 1: Basic EC2 Instance

```hcl
module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 6.0"

  name = "my-web-server"

  instance_type          = "t3.micro"
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
  version = "~> 6.0"

  for_each = toset(["web-1", "web-2", "web-3"])

  name = "web-server-${each.key}"

  instance_type          = "t3.small"
  key_name               = "my-key-pair"
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id              = "subnet-eddcdzz4"

  enable_volume_tags = false
  root_block_device = {
    volume_type = "gp3"
    volume_size = 20
    encrypted   = true
  }

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
  version = "~> 6.0"

  name = "batch-processor"

  # Spot instance configuration
  create_spot_instance                 = true
  spot_price                           = "0.05"
  spot_type                            = "persistent"
  spot_instance_interruption_behavior  = "stop"

  instance_type     = "c5.xlarge"
  ami_ssm_parameter = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
  subnet_id         = "subnet-eddcdzz4"

  # Create IAM instance profile
  create_iam_instance_profile = true
  iam_role_name               = "batch-processor-role"
  iam_role_policies = {
    S3Access = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  }

  # User data for initialization
  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    systemctl start docker
    systemctl enable docker
  EOF

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
  version = "~> 6.0"

  name = "database-server"

  instance_type          = "m5.large"
  ami                    = "ami-0c55b159cbfafe1f0"
  key_name               = "my-key-pair"
  monitoring             = true
  vpc_security_group_ids = ["sg-database"]
  subnet_id              = "subnet-private-1"

  # Root volume configuration
  enable_volume_tags = false
  root_block_device = {
    volume_type           = "gp3"
    volume_size           = 50
    encrypted             = true
    delete_on_termination = true
  }

  # Additional data volumes
  ebs_volumes = {
    "/dev/sdf" = {
      volume_type           = "gp3"
      volume_size           = 100
      iops                  = 3000
      throughput            = 125
      encrypted             = true
      delete_on_termination = false
      tags = {
        MountPoint = "/mnt/data"
      }
    }
  }

  tags = {
    Terraform   = "true"
    Environment = "production"
    Purpose     = "database"
  }
}
```

### Example 5: Complete Instance with Security Group and EIP

```hcl
module "ec2_complete" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 6.0"

  name = "secure-application-server"

  instance_type = "t3.medium"
  ami           = "ami-0c55b159cbfafe1f0"
  key_name      = "my-key-pair"
  monitoring    = true
  subnet_id     = "subnet-private"

  # Create Elastic IP
  create_eip = true

  # Create security group with custom rules
  create_security_group  = true
  security_group_name    = "app-server-sg"
  security_group_vpc_id  = "vpc-12345678"
  security_group_ingress_rules = {
    https = {
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      cidr_ipv4   = "10.0.0.0/8"
      description = "HTTPS from internal"
    }
  }

  # IMDSv2 is enabled by default - this is the default config
  # metadata_options = {
  #   http_endpoint               = "enabled"
  #   http_tokens                 = "required"
  #   http_put_response_hop_limit = 1
  # }

  # Create IAM role with specific permissions
  create_iam_instance_profile = true
  iam_role_name               = "app-server-role"
  iam_role_policies = {
    SecretsManager = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
    SSM            = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  }

  # Encrypted root volume with custom KMS key
  enable_volume_tags = false
  root_block_device = {
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
    kms_key_id  = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
    tags = {
      Name = "app-server-root"
    }
  }

  # Enable termination protection
  disable_api_termination = true

  tags = {
    Terraform   = "true"
    Environment = "production"
    Security    = "high"
  }
}
```

### Example 6: Session Manager Access (No SSH Keys)

```hcl
module "ec2_ssm" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 6.0"

  name = "ssm-managed-instance"

  instance_type = "t3.micro"
  subnet_id     = "subnet-private"  # Private subnet

  # No key_name needed - access via Session Manager
  # No public IP needed
  associate_public_ip_address = false

  # IAM role for Systems Manager
  create_iam_instance_profile = true
  iam_role_name               = "ssm-instance-role"
  iam_role_policies = {
    SSMManagedInstance = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  }

  tags = {
    Terraform   = "true"
    Environment = "production"
  }
}
```

## Best Practices

### Security and Access Control

1. **IMDSv2 Is Default**: The module enables IMDSv2 by default (`http_tokens = "required"`). Do not disable this unless absolutely necessary.
2. **Use IAM Roles Over Keys**: Use `create_iam_instance_profile = true` with `iam_role_policies` instead of hardcoding credentials.
3. **Enable Encryption**: Always encrypt EBS volumes using `encrypted = true` in `root_block_device` and `ebs_volumes`, especially for production.
4. **Use KMS Keys**: For regulated workloads, specify `kms_key_id` for customer-managed encryption keys.
5. **Restrict Security Groups**: Use specific security group rules with minimal required ports. Create security groups with `create_security_group = true` and define `security_group_ingress_rules`.
6. **Use Session Manager**: For secure shell access without SSH keys, attach `AmazonSSMManagedInstanceCore` policy and use AWS Systems Manager Session Manager.
7. **Disable Public IPs**: For private workloads, set `associate_public_ip_address = false` and use NAT gateways or VPC endpoints.
8. **Enable Termination Protection**: Set `disable_api_termination = true` on critical instances to prevent accidental deletion.

### Spot Instance Considerations

1. **Grant KMS Access**: For spot instances with encrypted volumes, grant the `AWSServiceRoleForEC2Spot` service-linked role access to your KMS keys.
2. **Configure Interruption Behavior**: Set `spot_instance_interruption_behavior` to `stop` or `hibernate` for stateful workloads.
3. **Use Persistent Requests**: Set `spot_type = "persistent"` for workloads that should automatically restart after interruption.

### Monitoring and Observability

1. **Enable Detailed Monitoring**: Set `monitoring = true` to enable CloudWatch monitoring at 1-minute intervals.
2. **Implement CloudWatch Alarms**: Create alarms for CPU utilization, disk usage, memory pressure, and status checks.
3. **Use Comprehensive Tags**: Implement tagging strategy including Environment, Owner, CostCenter, and Application for cost allocation and organization.

### Cost Optimization

1. **Right-Size Instances**: Start with smaller instance types and scale up based on actual usage patterns.
2. **Use Spot Instances**: For fault-tolerant workloads, enable `create_spot_instance = true` to reduce costs by up to 90%.
3. **Use GP3 Volumes**: Configure `volume_type = "gp3"` in block device settings for better performance-to-cost ratio.
4. **Ignore AMI Changes**: Set `ignore_ami_changes = true` to prevent instance replacement during automated AMI updates.

### High Availability and Disaster Recovery

1. **Multi-AZ Deployment**: Deploy instances across multiple Availability Zones using `for_each` with different `subnet_id` values.
2. **Regular Backups**: Implement automated EBS snapshot policies using AWS Backup or Data Lifecycle Manager.
3. **Use Auto Recovery**: Enable auto recovery for EC2 instances through CloudWatch alarms with EC2 actions.

### Configuration Management

1. **Use User Data Carefully**: Keep user data scripts idempotent and minimal. Set `user_data_replace_on_change = true` only when instance replacement is acceptable.
2. **Version Control AMIs**: Maintain versioned AMIs; use `ignore_ami_changes = true` for production instances with automated AMI updates.
3. **Use SSM Parameters for AMIs**: Leverage `ami_ssm_parameter` for dynamic AMI selection from AWS-provided latest AMIs.
4. **Volume Tags Conflict**: Set `enable_volume_tags = false` when using custom tags in `root_block_device` to avoid conflicts.

### Important Gotchas

1. **Network Interface Conflict**: `network_interface` cannot be specified together with `vpc_security_group_ids`, `associate_public_ip_address`, or `subnet_id`. Choose one approach.
2. **Hibernation vs Enclaves**: Only one of `hibernation` or `enclave_options_enabled` can be enabled at a time.
3. **Spot KMS Failures**: Check spot request failures with `aws ec2 describe-spot-instance-requests` - often caused by missing KMS permissions for the EC2 Spot service role.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ec2-instance
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ec2-instance/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-ec2-instance/tree/master/examples
- **AWS EC2 Documentation**: https://docs.aws.amazon.com/ec2/
- **AWS EC2 Instance Types**: https://aws.amazon.com/ec2/instance-types/
- **EC2 Pricing**: https://aws.amazon.com/ec2/pricing/
- **EC2 Best Practices**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-best-practices.html
- **IMDSv2 Documentation**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **EBS Volume Types**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volume-types.html
- **EC2 Spot Instances**: https://aws.amazon.com/ec2/spot/
- **AWS Systems Manager**: https://docs.aws.amazon.com/systems-manager/
- **AWS SSM AMI Parameters**: https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-public-parameters-ami.html

## Notes for AI Agents

When using this module in automated workflows:

1. **IMDSv2 by Default**: The module requires IMDSv2 by default - no additional configuration needed for enhanced security
2. **Use IAM Roles Over Keys**: Prefer `create_iam_instance_profile = true` with `iam_role_policies` over SSH keys or hardcoded credentials
3. **Encrypt Everything**: Use `encrypted = true` for all EBS volumes in production environments
4. **Create Security Groups**: Use `create_security_group = true` with `security_group_ingress_rules` for controlled network access
5. **Tag Consistently**: Implement comprehensive tagging including Environment, Owner, CostCenter, and Application tags
6. **Use Spot Wisely**: Enable `create_spot_instance = true` for stateless, fault-tolerant workloads with appropriate interruption behavior
7. **Grant Spot KMS Access**: For encrypted spot instances, ensure `AWSServiceRoleForEC2Spot` has access to KMS keys
8. **Session Manager for SSH**: Use `AmazonSSMManagedInstanceCore` policy for secure shell access without SSH keys
9. **Handle AMI Updates**: Set `ignore_ami_changes = true` for production instances with automated AMI patching
10. **Volume Tags Conflict**: Set `enable_volume_tags = false` when defining custom tags in `root_block_device`
11. **Monitor Spot Requests**: Check `spot_bid_status` and `spot_request_state` outputs for spot instance debugging
12. **Use SSM for AMIs**: Leverage `ami_ssm_parameter` for dynamic, up-to-date AMI selection from AWS
