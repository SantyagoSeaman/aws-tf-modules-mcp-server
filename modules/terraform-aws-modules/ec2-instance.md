# Terraform AWS EC2 Instance Module

## Module Information

- **Module Name**: `ec2-instance`
- **Module ID**: `terraform-aws-modules/ec2-instance/aws`
- **Source**: `terraform-aws-modules/ec2-instance/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ec2-instance
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ec2-instance/aws/latest
- **Latest Version**: 6.4.0
- **Terraform Version**: >= 1.5.7
- **AWS Provider Version**: >= 6.37
- **Purpose**: Terraform module that creates a single AWS EC2 instance (on-demand or spot) with optional security group, IAM instance profile/role, Elastic IP, and EBS/ephemeral volume attachments
- **Service**: AWS EC2 (Elastic Compute Cloud)
- **Category**: Compute, Infrastructure
- **Keywords**: ec2, instance, compute, spot-instance, ami, ebs, iam-role, security-group, imdsv2, elastic-ip, network-interface, capacity-reservation, launch-template, hibernation
- **Use For**: application/web servers, API backends, batch processing nodes, development and staging environments, self-managed database servers, CI/CD runners, bastion/jump hosts, Session Manager-managed instances, GPU/ML training instances

## Description

This module provisions a single AWS EC2 instance (use Terraform's `for_each` at the calling site to create multiples) with fine-grained control over compute, networking, storage, and identity configuration. It creates the `aws_instance` (or `aws_spot_instance_request` when spot is enabled) resource plus a set of optional, feature-flagged companion resources: a security group with VPC-style ingress/egress rule maps, an IAM role and instance profile with attachable managed/customer policies, an Elastic IP, additional `aws_ebs_volume`/`aws_volume_attachment` resources, and ephemeral (instance-store) block devices.

AMI selection can be explicit (`ami`) or dynamic via an SSM public parameter (`ami_ssm_parameter`, defaulting to the latest Amazon Linux 2023 AMI), with `ignore_ami_changes` to prevent Terraform from replacing running instances when the upstream AMI is patched. The module supports advanced EC2 features including On-Demand Capacity Reservations (`capacity_reservation_specification`), Capacity Blocks/Spot via the generic `instance_market_options` (which overrides the simpler `create_spot_instance` flags), Launch Template association, dedicated hosts/tenancy, placement groups and partitions, primary/secondary IPv6 addressing, multiple secondary network interfaces, Nitro Enclaves, and hibernation.

Security is opinionated by default: IMDSv2 (`http_tokens = "required"`) is enforced out of the box, and the security group's egress defaults to allow-all IPv4/IPv6 (overridable). Every sub-resource (security group, IAM role, EIP, EBS volumes) is independently toggled with a `create_*` boolean, so the module can be used minimally (just an instance) or as a fully self-contained deployment unit. This module has no submodules; multi-instance and composite patterns are shown via the repository's `examples/` directory instead.

## Key Features

- **Single-Instance Resource Model**: Creates one instance per module call; combine with `for_each`/`count` at the call site for fleets
- **On-Demand or Spot**: Toggle `create_spot_instance` for a simple spot request, or use `instance_market_options` for full control (spot or capacity-block market type), which takes precedence
- **Flexible AMI Resolution**: Use a fixed `ami` ID or the built-in `ami_ssm_parameter` data source (defaults to latest Amazon Linux 2023); `ignore_ami_changes` prevents unwanted replacement
- **Built-in IAM Instance Profile**: Optionally creates an IAM role, assume-role policy, and instance profile with `iam_role_policies` map for managed/custom policy attachments and a permissions boundary
- **Security Group Management**: Optionally creates a security group with `security_group_ingress_rules`/`security_group_egress_rules` maps (modern `aws_vpc_security_group_*_rule` resources); egress defaults to allow-all
- **IMDSv2 Enforced by Default**: `metadata_options` defaults to `http_tokens = "required"`, `http_put_response_hop_limit = 1`
- **EBS & Ephemeral Storage**: Configure `root_block_device`, attach arbitrary additional `ebs_volumes` (encryption, KMS, IOPS, throughput, multi-attach, initialization rate), and instance-store `ephemeral_block_device`
- **Elastic IP**: Optional `create_eip` to allocate and associate a public EIP
- **Capacity Reservations & Launch Templates**: `capacity_reservation_specification` targets open or specific capacity reservations; `launch_template` associates an existing launch template (module-set arguments override it)
- **Advanced Networking**: Primary/secondary IPv6 addresses, multiple `secondary_network_interface` attachments, custom `network_interface` blocks (mutually exclusive with `subnet_id`/`vpc_security_group_ids`/`associate_public_ip_address`)
- **Placement Control**: Tenancy (default/dedicated/host), dedicated host targeting, placement groups and partition numbers
- **CPU & Performance Tuning**: `cpu_credits` (T-family burstable), `cpu_options` (core count, threads per core, AMD SEV-SNP, nested virtualization)
- **Hibernation & Nitro Enclaves**: Mutually exclusive `hibernation` and `enclave_options_enabled` flags
- **Protection Flags**: `disable_api_termination`, `disable_api_stop`, and `force_destroy` to override protections on destroy
- **Granular Conditional Creation**: Every sub-resource group (`create`, `create_spot_instance`, `create_iam_instance_profile`, `create_security_group`, `create_eip`) is independently togglable

## Main Use Cases

1. **Web Application Hosting**: Deploy web servers and application backends behind a load balancer
2. **Microservices/API Backends**: Run standalone service instances with dedicated security groups and IAM roles
3. **Development and Testing Environments**: Spin up isolated, disposable dev/staging instances
4. **Self-Managed Database Servers**: Host databases on EBS-backed storage with encrypted, tagged volumes
5. **CI/CD Runners**: Deploy build agents, optionally on spot capacity for cost savings
6. **Batch/Data Processing**: Run fault-tolerant batch jobs on spot instances with `instance_market_options`
7. **Machine Learning Workloads**: Provision GPU/CPU instances, optionally targeting Capacity Reservations for guaranteed capacity
8. **Bastion / Jump Hosts**: Create secure access points into private VPC subnets
9. **Session Manager-Managed Instances**: Deploy instances with no public IP or SSH key, managed via AWS Systems Manager
10. **Instances Requiring Guaranteed Capacity**: Target On-Demand Capacity Reservations for critical, capacity-constrained workloads

## Submodules

This module does not include submodules (registry shows "No modules" under Modules). It is a single root module for creating one EC2 instance; the repository ships example configurations (`examples/complete`, `examples/session-manager`) instead of reusable submodules.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create an instance and its associated resources |
| `name` | `string` | `""` | Name to be used on the EC2 instance (used as the `Name` tag) |
| `ami` | `string` | `null` | ID of AMI to use for the instance |
| `ami_ssm_parameter` | `string` | `"/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"` | SSM parameter name for the AMI ID, used when `ami` is not set |
| `ignore_ami_changes` | `bool` | `false` | Ignore changes to the AMI ID (avoids replacement on AMI updates) |
| `instance_type` | `string` | `"t3.micro"` | The type of instance to start |
| `availability_zone` | `string` | `null` | AZ to start the instance in |
| `subnet_id` | `string` | `null` | The VPC Subnet ID to launch in |
| `vpc_security_group_ids` | `list(string)` | `[]` | Existing security group IDs to associate (in addition to any created by this module) |
| `key_name` | `string` | `null` | Key Pair name for SSH access |
| `monitoring` | `bool` | `null` | Enable detailed (1-minute) CloudWatch monitoring |
| `associate_public_ip_address` | `bool` | `null` | Whether to associate a public IP address |
| `private_ip` | `string` | `null` | Private IP address to assign in a VPC |
| `user_data` / `user_data_base64` | `string` | `null` | Instance boot/user-data script (plain or base64) |
| `user_data_replace_on_change` | `bool` | `null` | Destroy/recreate instance when user data changes |
| `metadata_options` | `object` | `{http_endpoint="enabled", http_put_response_hop_limit=1, http_tokens="required"}` | IMDS options; IMDSv2 required by default — fields: `http_endpoint`, `http_protocol_ipv6`, `http_put_response_hop_limit`, `http_tokens`, `instance_metadata_tags` |
| `root_block_device` | `object` | `null` | Root volume config: size, type, IOPS, throughput, `encrypted`, `kms_key_id`, `delete_on_termination`, `tags` |
| `ebs_volumes` | `map(object)` | `null` | Additional EBS volumes keyed by name/device, with attachment options — fields: `encrypted`, `final_snapshot`, `iops`, `kms_key_id`, `multi_attach_enabled`, `outpost_arn`, `size`, `snapshot_id`, … (8 shown; see grep_module_docs) |
| `ephemeral_block_device` | `map(object)` | `null` | Instance-store (ephemeral) volume mappings — fields: `device_name`, `no_device`, `virtual_name` |
| `enable_volume_tags` | `bool` | `true` | Enable volume tags (conflicts with tags set directly in `root_block_device`) |
| `disable_api_termination` | `bool` | `null` | Enable EC2 termination protection |
| `disable_api_stop` | `bool` | `null` | Enable EC2 stop protection |
| `force_destroy` | `bool` | `null` | Force-destroy instance even if termination/stop protection is enabled |
| `ebs_optimized` | `bool` | `null` | Launch as EBS-optimized |
| `hibernation` | `bool` | `null` | Enable hibernation support (mutually exclusive with Nitro Enclaves) |
| `enclave_options_enabled` | `bool` | `null` | Enable Nitro Enclaves (mutually exclusive with hibernation) |
| `cpu_credits` | `string` | `null` | Burstable CPU credit option (`standard` or `unlimited`) |
| `cpu_options` | `object` | `null` | `core_count`, `threads_per_core`, `amd_sev_snp`, `nested_virtualization` |
| `tenancy` | `string` | `null` | `default`, `dedicated`, or `host` |
| `host_id` / `host_resource_group_arn` | `string` | `null` | Target a specific dedicated host or host resource group |
| `placement_group` / `placement_group_id` / `placement_partition_number` | `string`/`number` | `null` | Placement group targeting |
| `capacity_reservation_specification` | `object` | `null` | Target an open or specific On-Demand Capacity Reservation — fields: `capacity_reservation_preference`, `capacity_reservation_target` |
| `launch_template` | `object({id, name, version})` | `null` | Associate a Launch Template; module-set args override its values |
| `instance_market_options` | `object` | `null` | Full market/spot options; overrides `create_spot_instance` when set |
| `network_interface` | `map(object)` | `null` | Custom NIC attachments (mutually exclusive with `subnet_id`/`vpc_security_group_ids`/`associate_public_ip_address`) |
| `secondary_network_interface` | `map(object)` | `null` | Additional secondary ENIs on separate network cards — fields: `delete_on_termination`, `device_index`, `interface_type`, `network_card_index`, `private_ip_address_count`, `private_ip_addresses`, `secondary_subnet_id` |
| `enable_primary_ipv6` | `bool` | `null` | Assign a primary IPv6 GUA in a dual-stack/IPv6-only subnet |
| `region` | `string` | `null` | AWS region override (defaults to provider region) |
| `tags` | `map(string)` | `{}` | Tags applied to all resources created by the module |

**Spot Instance Variables** (simple path; superseded by `instance_market_options` if both are set):

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_spot_instance` | `bool` | `false` | Create the instance as a spot request |
| `spot_price` | `string` | `null` | Max price to bid (defaults to on-demand price) |
| `spot_type` | `string` | `null` | `one-time` or `persistent` |
| `spot_instance_interruption_behavior` | `string` | `null` | `terminate`, `stop`, or `hibernate` |
| `spot_wait_for_fulfillment` | `bool` | `null` | Wait (up to 10m) for the spot request to be fulfilled |
| `spot_launch_group` | `string` | `null` | Group spot instances to launch/terminate together |
| `spot_valid_from` / `spot_valid_until` | `string` | `null` | RFC3339 validity window for the spot request |

**IAM Instance Profile Variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `iam_instance_profile` | `string` | `null` | Name of an existing IAM instance profile to attach |
| `create_iam_instance_profile` | `bool` | `false` | Create a new IAM role + instance profile |
| `iam_role_name` | `string` | `null` | Name for the created IAM role (used as prefix unless `iam_role_use_name_prefix = false`) |
| `iam_role_policies` | `map(string)` | `{}` | Map of policy ARNs to attach to the created role |
| `iam_role_permissions_boundary` | `string` | `null` | ARN of the permissions boundary policy |
| `iam_role_path` | `string` | `null` | Path for the IAM role |

**Security Group Variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_security_group` | `bool` | `true` | Create a security group for the instance |
| `security_group_name` | `string` | `null` | Name (used as prefix by default) |
| `security_group_vpc_id` | `string` | `null` | VPC ID (defaults to the default VPC if unset) |
| `security_group_ingress_rules` | `map(object)` | `null` | Ingress rules (cidr/prefix-list/referenced-SG, port range, protocol) — fields: `cidr_ipv4`, `cidr_ipv6`, `description`, `from_port`, `ip_protocol`, `prefix_list_id`, `referenced_security_group_id`, `tags`, … (8 shown; see grep_module_docs) |
| `security_group_egress_rules` | `map(object)` | allow-all IPv4 + IPv6 | Egress rules; **override to restrict outbound traffic** — fields: `cidr_ipv4`, `cidr_ipv6`, `description`, `from_port`, `ip_protocol`, `prefix_list_id`, `referenced_security_group_id`, `tags`, … (8 shown; see grep_module_docs) |

**Elastic IP Variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_eip` | `bool` | `false` | Create and associate a public Elastic IP |
| `eip_domain` | `string` | `"vpc"` | EIP domain scope |
| `eip_tags` | `map(string)` | `{}` | Additional tags for the EIP |

## Main Outputs

| Output | Description |
|--------|-------------|
| `id` | The ID of the instance |
| `arn` | The ARN of the instance |
| `instance_state` | The state of the instance |
| `ami` | AMI ID that was used to create the instance |
| `availability_zone` | The availability zone of the created instance |
| `capacity_reservation_specification` | Capacity reservation specification of the instance |
| `public_dns` / `public_ip` | Public DNS/IP (IP includes associated EIP if created) |
| `private_dns` / `private_ip` | Private DNS/IP address |
| `ipv6_addresses` | IPv6 addresses assigned to the instance |
| `primary_network_interface_id` | ID of the instance's primary network interface |
| `root_block_device` | Root block device information |
| `ebs_block_device` / `ebs_volumes` | Attached EBS block devices and additional volume attributes |
| `ephemeral_block_device` | Ephemeral (instance-store) block device information |
| `spot_bid_status` / `spot_request_state` / `spot_instance_id` | Spot request status and resulting instance ID |
| `iam_role_name` / `iam_role_arn` / `iam_role_unique_id` | IAM role identifiers |
| `iam_instance_profile_arn` / `iam_instance_profile_id` / `iam_instance_profile_unique` | IAM instance profile identifiers |
| `security_group_id` / `security_group_arn` | Created security group identifiers |
| `password_data` | Encrypted Windows administrator password (only if `get_password_data = true`) |
| `tags_all` | All tags assigned to the resource, including provider default tags |

## Usage Examples

### Example 1: Basic EC2 Instance

```hcl
module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 6.0"

  name = "my-web-server"

  instance_type          = "t3.micro"
  key_name               = "my-key-pair"
  monitoring              = true
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id               = "subnet-eddcdzz4"

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
  subnet_id               = "subnet-eddcdzz4"

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

### Example 3: Spot Instance with IAM Role and User Data

```hcl
module "ec2_spot" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 6.0"

  name = "batch-processor"

  # Spot instance configuration
  create_spot_instance                = true
  spot_price                          = "0.05"
  spot_type                           = "persistent"
  spot_instance_interruption_behavior = "stop"

  instance_type     = "c5.xlarge"
  ami_ssm_parameter = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
  subnet_id         = "subnet-eddcdzz4"

  # Create IAM instance profile
  create_iam_instance_profile = true
  iam_role_name                = "batch-processor-role"
  iam_role_policies = {
    S3Access = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  }

  user_data = <<-EOF
    #!/bin/bash
    dnf update -y
    dnf install -y docker
    systemctl enable --now docker
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

  instance_type           = "m5.large"
  ami                     = "ami-0c55b159cbfafe1f0"
  key_name                = "my-key-pair"
  monitoring              = true
  vpc_security_group_ids  = ["sg-database"]
  subnet_id                = "subnet-private-1"

  # Root volume configuration
  enable_volume_tags = false
  root_block_device = {
    volume_type           = "gp3"
    volume_size           = 50
    encrypted              = true
    delete_on_termination = true
  }

  # Additional data volume
  ebs_volumes = {
    data = {
      device_name           = "/dev/sdf"
      volume_type           = "gp3"
      volume_size           = 100
      iops                  = 3000
      throughput            = 125
      encrypted              = true
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

### Example 5: Complete Instance with Security Group, EIP, and Capacity Reservation

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
  create_security_group = true
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
  # Restrict egress instead of using the module's allow-all default
  security_group_egress_rules = {
    https_out = {
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      cidr_ipv4   = "0.0.0.0/0"
      description = "HTTPS out"
    }
  }

  # IMDSv2 is enabled by default; shown here for clarity only
  # metadata_options = {
  #   http_endpoint               = "enabled"
  #   http_tokens                 = "required"
  #   http_put_response_hop_limit = 1
  # }

  # Create IAM role with specific permissions
  create_iam_instance_profile = true
  iam_role_name                = "app-server-role"
  iam_role_policies = {
    SecretsManager = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
    SSM            = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  }

  # Target an existing On-Demand Capacity Reservation
  capacity_reservation_specification = {
    capacity_reservation_target = {
      capacity_reservation_id = "cr-0123456789abcdef0"
    }
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

### Example 6: Session Manager Access (No SSH Keys, No Public IP)

```hcl
module "ec2_ssm" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 6.0"

  name = "ssm-managed-instance"

  instance_type = "t3.micro"
  subnet_id     = "subnet-private" # Private subnet

  # No key_name needed - access via Session Manager
  associate_public_ip_address = false

  # IAM role for Systems Manager
  create_iam_instance_profile = true
  iam_role_name                = "ssm-instance-role"
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
2. **Use IAM Roles Over Keys**: Use `create_iam_instance_profile = true` with `iam_role_policies` instead of hardcoding credentials or relying solely on SSH key pairs.
3. **Enable Encryption**: Always encrypt EBS volumes using `encrypted = true` in `root_block_device` and `ebs_volumes`, especially for production.
4. **Use KMS Keys**: For regulated workloads, specify `kms_key_id` for customer-managed encryption keys.
5. **Restrict Security Groups**: Define specific `security_group_ingress_rules`, and override `security_group_egress_rules` (the module default is allow-all outbound) when a workload needs restricted egress.
6. **Use Session Manager**: For shell access without SSH keys or open inbound ports, attach the `AmazonSSMManagedInstanceCore` policy and use AWS Systems Manager Session Manager.
7. **Disable Public IPs**: For private workloads, set `associate_public_ip_address = false` and rely on NAT gateways or VPC endpoints for outbound access.
8. **Enable Termination Protection**: Set `disable_api_termination = true` on critical instances; use `force_destroy = true` explicitly when Terraform genuinely needs to destroy a protected instance.

### Spot Instance Considerations

1. **Grant KMS Access**: For spot instances with encrypted volumes, grant the `AWSServiceRoleForEC2Spot` service-linked role access to your KMS keys, or spot requests fail with `bad parameters`.
2. **Configure Interruption Behavior**: Set `spot_instance_interruption_behavior` to `stop` or `hibernate` for stateful workloads instead of the default `terminate`.
3. **Prefer `instance_market_options` for Complex Cases**: It overrides `create_spot_instance`/`spot_*` variables and supports additional market types.

### Monitoring and Observability

1. **Enable Detailed Monitoring**: Set `monitoring = true` for 1-minute CloudWatch metric granularity.
2. **Implement CloudWatch Alarms**: Create alarms for CPU utilization, disk usage, and instance status checks outside this module.
3. **Tag Consistently**: Use `tags` for Environment, Owner, CostCenter, and Application to support cost allocation and automation.

### Cost Optimization

1. **Right-Size Instances**: Start with smaller instance types and scale based on observed usage.
2. **Use Spot Instances**: For fault-tolerant workloads, enable `create_spot_instance = true` (or `instance_market_options`) to reduce costs by up to 90%.
3. **Use GP3 Volumes**: Configure `volume_type = "gp3"` for a better price/performance ratio than `gp2`.
4. **Ignore AMI Changes**: Set `ignore_ami_changes = true` to avoid unwanted instance replacement when the referenced AMI (especially via SSM parameter) is patched upstream.

### High Availability and Disaster Recovery

1. **Multi-AZ Deployment**: Deploy instances across multiple Availability Zones using `for_each` with different `subnet_id`/`availability_zone` values at the call site.
2. **Use Capacity Reservations**: For workloads that cannot tolerate capacity shortfalls, target an On-Demand Capacity Reservation via `capacity_reservation_specification`.
3. **Regular Backups**: Implement automated EBS snapshot policies via AWS Backup or Data Lifecycle Manager (outside this module's scope).

### Configuration Management

1. **Keep User Data Idempotent**: Set `user_data_replace_on_change = true` only when instance replacement on user-data change is acceptable.
2. **Use SSM Parameters for AMIs**: Prefer `ami_ssm_parameter` over a hardcoded `ami` for automatic, up-to-date AMI selection, combined with `ignore_ami_changes` in production.
3. **Volume Tags Conflict**: Set `enable_volume_tags = false` when defining custom `tags` inside `root_block_device`/`ebs_volumes` to avoid a Terraform conflict.

### Important Gotchas

1. **Network Interface Conflict**: `network_interface` cannot be specified together with `vpc_security_group_ids`, `associate_public_ip_address`, or `subnet_id`. Choose one approach.
2. **Hibernation vs Enclaves**: Only one of `hibernation` or `enclave_options_enabled` can be enabled at a time.
3. **`instance_market_options` Overrides Spot Variables**: If both are set, `instance_market_options` takes precedence over `create_spot_instance`/`spot_*` variables.
4. **Spot KMS Failures**: Debug spot request failures with `aws ec2 describe-spot-instance-requests`; failures are often caused by missing KMS permissions for the EC2 Spot service-linked role.
5. **No Encrypted-AMI Support Out of the Box**: To launch from an encrypted AMI, first create one with `aws_ami_copy` (`encrypted = true`) and reference the resulting AMI ID.
6. **This Module Creates One Instance**: There is no `instance_count`/multi-instance submodule; use `for_each`/`count` on the module block itself for fleets.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ec2-instance
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ec2-instance/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-ec2-instance/tree/master/examples
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-ec2-instance/blob/master/CHANGELOG.md
- **AWS EC2 Documentation**: https://docs.aws.amazon.com/ec2/
- **AWS EC2 Instance Types**: https://aws.amazon.com/ec2/instance-types/
- **EC2 Best Practices**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-best-practices.html
- **IMDSv2 Documentation**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **EBS Volume Types**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volume-types.html
- **EC2 Spot Instances**: https://aws.amazon.com/ec2/spot/
- **On-Demand Capacity Reservations**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-reservations.html
- **AWS Systems Manager Session Manager**: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html
- **AWS SSM AMI Parameters**: https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-public-parameters-ami.html

## Notes for AI Agents

When using this module in automated workflows:

1. **One Instance per Call**: This module creates exactly one instance; use `for_each`/`count` on the module block for multiple instances, not a module input.
2. **IMDSv2 by Default**: No extra configuration is needed for IMDSv2 — it's on by default via `metadata_options`.
3. **Use IAM Roles Over Keys**: Prefer `create_iam_instance_profile = true` with `iam_role_policies` over SSH keys or hardcoded credentials.
4. **Encrypt Everything**: Set `encrypted = true` for all EBS volumes (`root_block_device` and `ebs_volumes`) in production.
5. **Create Security Groups Deliberately**: Use `create_security_group = true` with explicit `security_group_ingress_rules`; remember the default egress is allow-all and may need restricting.
6. **Prefer `instance_market_options` for Advanced Spot/Capacity Needs**: It supersedes the simpler `create_spot_instance`/`spot_*` inputs when both are present.
7. **Grant Spot KMS Access**: For encrypted spot instances, ensure `AWSServiceRoleForEC2Spot` has access to the relevant KMS keys.
8. **Session Manager for Shell Access**: Attach `AmazonSSMManagedInstanceCore` instead of provisioning SSH keys/public IPs where possible.
9. **Handle AMI Updates**: Set `ignore_ami_changes = true` for production instances relying on `ami_ssm_parameter` to avoid surprise replacement.
10. **Volume Tags Conflict**: Set `enable_volume_tags = false` whenever custom `tags` are defined inside `root_block_device`/`ebs_volumes`.
11. **Monitor Spot/Reservation State**: Use `spot_bid_status`/`spot_request_state` outputs for spot debugging, and `capacity_reservation_specification` output to confirm reservation targeting.
12. **Mutual Exclusivity Checks**: Never combine `network_interface` with `subnet_id`/`vpc_security_group_ids`/`associate_public_ip_address`, and never enable both `hibernation` and `enclave_options_enabled`.
