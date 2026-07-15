# Terraform AWS VPC Module

## Module Information

- **Module Name**: `vpc`
- **Module ID**: `terraform-aws-modules/vpc/aws`
- **Source**: `terraform-aws-modules/vpc/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-vpc
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest
- **Latest Version**: 6.6.1
- **Compatibility**: Terraform >= 1.0, AWS provider >= 6.28 (root module and `vpc-endpoints` submodule); the `flow-log` submodule requires Terraform >= 1.5.7. Since v6.0.0 the module requires AWS provider v6.x — pin `~> 6.0` when generating configs.
- **Purpose**: Terraform module that creates and configures an AWS VPC and all its supporting networking resources (subnets, route tables, gateways, NACLs, DHCP options, VPN/customer gateways, IPAM CIDR allocation, VPC Block Public Access)
- **Service**: AWS VPC (Virtual Private Cloud)
- **Category**: Networking, Infrastructure
- **Keywords**: vpc, virtual-private-cloud, subnet, nat-gateway, internet-gateway, route-table, network-acl, ipv6, cidr, availability-zone, vpc-endpoints, flow-logs, ipam, vpn-gateway, transit-gateway, private-subnet, public-subnet, database-subnet
- **Use For**: multi-tier application hosting, microservices networking, hybrid cloud connectivity via VPN/Direct Connect, isolated database/cache/analytics subnet hosting, container orchestration networking (EKS/ECS), high-availability multi-AZ architectures, regulatory-compliance network segmentation (PCI-DSS, HIPAA), hub-and-spoke topologies with Transit Gateway, zero-trust networking with private subnets and VPC endpoints, IPAM-managed enterprise IP address space, dual-stack IPv4/IPv6 workloads, AWS Outposts hybrid infrastructure

## Description

This module provisions an AWS VPC (`aws_vpc.this`) and the full set of supporting networking resources needed to run production workloads: subnets distributed across availability zones (public, private, database, ElastiCache, Redshift, intra, and Outpost), route tables and associations, an Internet Gateway, NAT Gateways (with Elastic IP reuse support), an egress-only Internet Gateway for IPv6, network ACLs per subnet tier, DHCP option sets, VPN/customer gateways, and RDS/ElastiCache/Redshift subnet groups. It also manages the account's Default VPC when opted in, and can create or import Elastic IPs for NAT.

The module removes the boilerplate of hand-wiring dozens of interdependent networking resources while remaining highly configurable: three NAT Gateway deployment strategies (single, one-per-subnet, one-per-AZ), automatic or IPAM-driven CIDR allocation for IPv4 and IPv6 (including IPv6-only and dual-stack subnets), secondary CIDR blocks for VPC expansion, per-subnet-type NACL and route-table customization, and AWS VPC Block Public Access controls (with per-exclusion overrides) to prevent accidental internet exposure at the VPC level.

**VPC Flow Logs in the root module are deprecated** (`enable_flow_log` and related `flow_log_*`/`vpc_flow_log_*` variables) and will be removed in a future major version; use the dedicated `flow-log` submodule instead for all new flow log configurations. The module ships two submodules — `vpc-endpoints` for AWS PrivateLink/Gateway endpoint connectivity and `flow-log` for VPC/subnet/ENI/Transit Gateway traffic logging — which compose with the root module via its outputs (`vpc_id`, `private_subnets`, `private_route_table_ids`, etc.).

## Key Features

- **Multi-Tier Subnet Types**: Public, private, database, ElastiCache, Redshift, intra (no internet route), and Outpost subnets, each independently configurable
- **Multi-AZ Distribution**: Subnets and NAT Gateways spread automatically across the AZs passed via `azs`
- **Three NAT Gateway Strategies**: Single shared gateway, one per subnet (default), or one per availability zone; supports reusing existing Elastic IPs via `reuse_nat_ips`/`external_nat_ip_ids`
- **IPv4 and IPv6 Dual-Stack**: `enable_ipv6`, per-subnet IPv6 prefixes, IPv6-only subnets, egress-only Internet Gateway, and DNS64 support
- **IPAM Integration**: VPC and subnet CIDRs can be allocated from an AWS IP Address Manager pool (`ipv4_ipam_pool_id`/`ipv6_ipam_pool_id`)
- **Secondary CIDR Blocks**: Extend the VPC's IP space post-creation via `secondary_cidr_blocks`
- **VPC Block Public Access**: Native AWS VPC-level public access blocking with per-resource exclusions (`vpc_block_public_access_options`, `vpc_block_public_access_exclusions`)
- **Per-Subnet-Tier Network ACLs**: Dedicated NACL and inbound/outbound rule sets for each subnet type, or shared default NACL management
- **Route Table Flexibility**: Shared or per-subnet route tables (`create_multiple_public_route_tables`, `create_multiple_intra_route_tables`), custom NAT/IGW routes
- **VPN & Customer Gateways**: `enable_vpn_gateway`, `customer_gateways` map, and route-table VGW propagation for hybrid connectivity
- **Managed Subnet Groups**: Auto-creates RDS (`create_database_subnet_group`), ElastiCache, and Redshift subnet groups from the corresponding subnet lists
- **Default VPC / Default Resources Management**: Optionally adopt and manage the account's Default VPC, default security group, default route table, and default NACL
- **Multi-Region Provider Support**: `region` input allows targeting a non-default provider region per module call
- **Conditional Creation**: `create_vpc = false` skips all resource creation while keeping the module composable
- **Comprehensive Tagging**: Global `tags` plus per-resource-type tag maps (`vpc_tags`, `*_subnet_tags`, `*_route_table_tags`, etc.), including per-AZ subnet tags

## Main Use Cases

1. **Multi-Tier Web Applications**: Separate public, application, and database subnet tiers with independent routing
2. **Microservices/Container Networking**: Provide the VPC and subnets consumed by EKS, ECS, or Kubernetes cluster modules
3. **Hybrid Cloud Connectivity**: Connect on-premises networks via VPN Gateway, Customer Gateway, or Transit Gateway attachment
4. **Secure Data Tier Isolation**: Host RDS, ElastiCache, and Redshift in dedicated subnets with their own route tables and NACLs
5. **Serverless/Lambda Networking**: Use intra subnets (no NAT/internet route) for functions that only need internal or VPC-endpoint access
6. **High-Availability Deployments**: Distribute resources and NAT Gateways across 3+ availability zones
7. **Regulatory Compliance**: Implement network segmentation and flow-log auditing for PCI-DSS/HIPAA workloads
8. **Hub-and-Spoke / Transit Architectures**: Attach the VPC to `terraform-aws-modules/transit-gateway` for centralized routing
9. **IPAM-Managed Enterprise Networks**: Derive VPC/subnet CIDRs from centrally managed IPAM pools instead of hardcoded ranges
10. **Dual-Stack or IPv6-Only Workloads**: Enable IPv6 alongside or instead of IPv4 for modern networking requirements

## Submodules

### 1. vpc-endpoints
- **Purpose**: Create VPC Interface (PrivateLink) and Gateway endpoints for private connectivity to AWS services
- **Source**: `terraform-aws-modules/vpc/aws//modules/vpc-endpoints`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest/submodules/vpc-endpoints
- **Key Features**: Interface and Gateway endpoint support, optional shared security group creation, per-endpoint subnet/security-group overrides, endpoint policy documents
- **Use Cases**: Private S3/DynamoDB access without NAT, SSM/EC2 message endpoints for Session Manager, cost reduction by bypassing NAT Gateway traffic

### 2. flow-log (Recommended for all new flow log configurations)
- **Purpose**: Create a standalone AWS Flow Log for a VPC, subnet, ENI, or Transit Gateway attachment
- **Source**: `terraform-aws-modules/vpc/aws//modules/flow-log`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest/submodules/flow-log
- **Key Features**: CloudWatch Logs, S3, or Kinesis Data Firehose destinations; auto-created IAM role and CloudWatch log group; custom log format and aggregation interval; Transit Gateway flow logs
- **Use Cases**: Security monitoring and threat detection, connectivity troubleshooting, compliance auditing, cost-optimized S3 log archival
- **Note**: Requires Terraform >= 1.5.7 (higher than the root module's >= 1.0). Root-module flow log variables (`enable_flow_log`, `flow_log_*`) are deprecated — use this submodule instead.

## Submodule 1: vpc-endpoints

### Description

Creates `aws_vpc_endpoint` resources (Interface, backed by AWS PrivateLink, or Gateway) that let resources in private subnets reach AWS services without an Internet Gateway, NAT device, VPN, or Direct Connect. It can optionally create a shared security group applied to all Interface endpoints, or accept externally managed security group/subnet IDs per endpoint.

### Key Features

- Supports both Interface (PrivateLink) and Gateway endpoint types in a single `endpoints` map
- Optional shared security group (`create_security_group`) with custom `security_group_rules`
- Per-endpoint overrides for `subnet_ids`, `security_group_ids`, `private_dns_enabled`, and `policy`
- Gateway endpoints associate directly with `route_table_ids`
- Full tagging support per endpoint and on the shared security group

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_id` | `string` | `null` | VPC ID where endpoints will be created |
| `endpoints` | `any` | `{}` | Map of endpoint definitions (service, service_type, subnet_ids, security_group_ids, policy, tags, etc.) — keys (from examples): `service`, `service_type`, `route_table_ids`, `tags`, `private_dns_enabled`, `subnet_ids` |
| `create_security_group` | `bool` | `false` | Whether to create a shared security group for Interface endpoints |
| `security_group_ids` | `list(string)` | `[]` | Default security group IDs to attach to endpoints that don't specify their own |
| `security_group_rules` | `any` | `{}` | Rules to add to the created security group — keys (from examples): `description`, `cidr_blocks` |
| `subnet_ids` | `list(string)` | `[]` | Default subnet IDs for Interface endpoints that don't specify their own |
| `create` | `bool` | `true` | Whether to create VPC endpoint resources |
| `tags` | `map(string)` | `{}` | Tags applied to all endpoint resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `endpoints` | Map of created VPC endpoint resources with all attributes |
| `security_group_id` | ID of the security group created for VPC endpoints (if `create_security_group = true`) |
| `security_group_arn` | ARN of the security group created for VPC endpoints |

### Usage Example

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "production-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true

  tags = {
    Environment = "production"
  }
}

module "vpc_endpoints" {
  source = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"

  vpc_id = module.vpc.vpc_id

  create_security_group      = true
  security_group_name_prefix = "vpc-endpoints-"
  security_group_rules = {
    ingress_https = {
      description = "HTTPS from VPC"
      cidr_blocks = [module.vpc.vpc_cidr_block]
    }
  }

  endpoints = {
    # S3 Gateway Endpoint (free)
    s3 = {
      service         = "s3"
      service_type    = "Gateway"
      route_table_ids = flatten([
        module.vpc.private_route_table_ids,
        module.vpc.public_route_table_ids
      ])
      tags = { Name = "s3-gateway-endpoint" }
    }

    # DynamoDB Gateway Endpoint (free)
    dynamodb = {
      service         = "dynamodb"
      service_type    = "Gateway"
      route_table_ids = module.vpc.private_route_table_ids
      tags            = { Name = "dynamodb-gateway-endpoint" }
    }

    # SSM Interface Endpoints for Session Manager (no bastion needed)
    ssm = {
      service             = "ssm"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      tags                = { Name = "ssm-vpc-endpoint" }
    }
    ec2messages = {
      service             = "ec2messages"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
    }
    ssmmessages = {
      service             = "ssmmessages"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
    }
  }

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
```

## Submodule 2: flow-log (Recommended)

### Description

Creates an AWS `aws_flow_log` resource that captures IP traffic metadata for a VPC, subnet, ENI, or Transit Gateway (attachment). It supports CloudWatch Logs, S3, or Kinesis Data Firehose destinations and can create the CloudWatch log group and IAM delivery role automatically. This is the recommended way to configure flow logs; the root VPC module's flow-log variables are deprecated.

### Key Features

- Attach to a VPC, subnet, ENI, Transit Gateway, or Transit Gateway attachment (mutually exclusive targets)
- Three log destinations: CloudWatch Logs (default), S3, Kinesis Data Firehose
- Auto-creates IAM role and CloudWatch log group, or accepts an existing `iam_role_arn`/`log_destination`
- Custom `log_format` field selection and `max_aggregation_interval` (60s or 600s; 60s required for Transit Gateway)
- Optional cross-account log delivery via `deliver_cross_account_role`
- S3 destination options: Parquet/plain-text format, Hive-compatible partitions, per-hour partitioning

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_id` | `string` | `null` | VPC ID to attach flow logs to (mutually exclusive with `subnet_id`/`eni_id`/`transit_gateway_id`) |
| `subnet_id` | `string` | `null` | Subnet ID to attach flow logs to |
| `eni_id` | `string` | `null` | Elastic Network Interface ID to attach flow logs to |
| `transit_gateway_id` / `transit_gateway_attachment_id` | `string` | `null` | Transit Gateway (attachment) to attach flow logs to |
| `name` | `string` | `""` | Name used across created resources (IAM role, log group prefix) |
| `log_destination_type` | `string` | `"cloud-watch-logs"` | `cloud-watch-logs`, `s3`, or `kinesis-data-firehose` |
| `log_destination` | `string` | `null` | ARN of the logging destination (required for `s3`) |
| `traffic_type` | `string` | `"ALL"` | `ACCEPT`, `REJECT`, or `ALL` |
| `log_format` | `string` | `null` | Custom ordered list of log fields |
| `max_aggregation_interval` | `number` | `null` (AWS default `600`) | `60` or `600` seconds |
| `create_iam_role` | `bool` | `true` | Whether to create the flow log delivery IAM role |
| `create_cloudwatch_log_group` | `bool` | `true` | Whether to create a CloudWatch log group |
| `cloudwatch_log_group_retention_in_days` | `number` | `90` | Log retention period (`0` = indefinite) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `id` | ID of the VPC flow log |
| `arn` | ARN of the VPC flow log |
| `cloudwatch_log_group_name` / `cloudwatch_log_group_arn` | CloudWatch log group created (if applicable) |
| `iam_role_arn` / `iam_role_name` | IAM role created for log delivery |

### Usage Examples

#### Example 1: CloudWatch Logs Destination

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "production-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
}

module "vpc_flow_log" {
  source = "terraform-aws-modules/vpc/aws//modules/flow-log"

  name   = "production-vpc-flow-log"
  vpc_id = module.vpc.vpc_id

  log_destination_type                   = "cloud-watch-logs"
  cloudwatch_log_group_retention_in_days = 30
  traffic_type                           = "ALL"
  max_aggregation_interval               = 60

  tags = {
    Environment = "production"
  }
}
```

#### Example 2: S3 Destination for Cost-Effective Long-Term Storage

```hcl
resource "aws_s3_bucket" "flow_logs" {
  bucket = "my-vpc-flow-logs"
}

module "vpc_flow_log_s3" {
  source = "terraform-aws-modules/vpc/aws//modules/flow-log"

  name   = "vpc-flow-log-security"
  vpc_id = module.vpc.vpc_id

  log_destination_type = "s3"
  log_destination       = aws_s3_bucket.flow_logs.arn
  traffic_type           = "REJECT" # only capture rejected traffic for security monitoring

  tags = {
    Purpose = "security-monitoring"
  }
}
```

## Main Module: VPC

### Description

The root module creates the VPC itself plus every supporting networking resource: subnets (across all six subnet tiers), Internet/NAT/egress-only gateways, route tables and associations, network ACLs, DHCP options, VPN/customer gateways, and RDS/ElastiCache/Redshift subnet groups. It is the entry point most consumers use directly, and its outputs are the composition surface for the `vpc-endpoints` and `flow-log` submodules and for other modules (EKS, RDS, ALB, etc.) that need subnet or route-table IDs.

### Key Features

- Full VPC lifecycle: `create_vpc` toggle, CIDR from literal value or IPAM pool, secondary CIDR blocks
- Six independently configurable subnet tiers with per-tier NACL, route table, and tagging control
- Three NAT Gateway strategies plus Elastic IP reuse for stable outbound IPs across VPC recreation
- IPv4/IPv6 dual-stack with per-subnet IPv6 prefix assignment and DNS64/egress-only IGW support
- VPC Block Public Access (`vpc_block_public_access_options`/`_exclusions`) for account/VPC-level public-exposure guardrails
- Default VPC, default security group, default route table, and default NACL adoption/management flags

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name prefix applied to all resources |
| `cidr` | `string` | `"10.0.0.0/16"` | IPv4 CIDR block for the VPC (or derive from IPAM via `ipv4_ipam_pool_id`) |
| `azs` | `list(string)` | `[]` | Availability zone names/IDs to distribute subnets across |
| `public_subnets` | `list(string)` | `[]` | Public subnet CIDR blocks |
| `private_subnets` | `list(string)` | `[]` | Private subnet CIDR blocks |
| `database_subnets` | `list(string)` | `[]` | Database subnet CIDR blocks |
| `elasticache_subnets` | `list(string)` | `[]` | ElastiCache subnet CIDR blocks |
| `redshift_subnets` | `list(string)` | `[]` | Redshift subnet CIDR blocks |
| `intra_subnets` | `list(string)` | `[]` | Subnets with no NAT/internet route (e.g., internal Lambda) |
| `enable_nat_gateway` | `bool` | `false` | Provision NAT Gateway(s) for private networks |
| `single_nat_gateway` | `bool` | `false` | Use one shared NAT Gateway for all private networks |
| `one_nat_gateway_per_az` | `bool` | `false` | One NAT Gateway per AZ (requires `azs` set and enough public subnets) |
| `enable_vpn_gateway` | `bool` | `false` | Create and attach a VPN Gateway |
| `enable_ipv6` | `bool` | `false` | Request an Amazon-provided /56 IPv6 CIDR for the VPC |
| `ipv4_ipam_pool_id` / `ipv4_netmask_length` | `string` / `number` | `null` | Allocate the VPC CIDR from an IPAM pool |
| `secondary_cidr_blocks` | `list(string)` | `[]` | Additional CIDR blocks to associate with the VPC |
| `enable_dns_hostnames` / `enable_dns_support` | `bool` | `true` | DNS hostname/resolution support for the VPC |
| `manage_default_security_group` / `manage_default_network_acl` / `manage_default_route_table` | `bool` | `true` | Adopt and manage the VPC's default resources |
| `create_database_subnet_group` / `create_elasticache_subnet_group` / `create_redshift_subnet_group` | `bool` | `true` | Auto-create the corresponding subnet group |
| `vpc_block_public_access_options` | `map(string)` | `{}` | Account/VPC-level public access blocking mode |
| `vpc_block_public_access_exclusions` | `map(any)` | `{}` | Per-resource exclusions from block-public-access rules |
| `map_public_ip_on_launch` | `bool` | `false` | Auto-assign public IPs to instances launched in public subnets |
| `tags` | `map(string)` | `{}` | Tags applied to all resources (also see `vpc_tags`, `*_subnet_tags`, `*_route_table_tags`) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `vpc_id` | ID of the VPC |
| `vpc_arn` | ARN of the VPC |
| `vpc_cidr_block` | Primary IPv4 CIDR block of the VPC |
| `vpc_secondary_cidr_blocks` | List of secondary CIDR blocks associated with the VPC |
| `azs` | Availability zones specified as input |
| `private_subnets` / `public_subnets` / `database_subnets` / `elasticache_subnets` / `redshift_subnets` / `intra_subnets` / `outpost_subnets` | Subnet IDs per tier |
| `private_subnet_arns` / `public_subnet_arns` / etc. | Subnet ARNs per tier |
| `database_subnet_group` / `elasticache_subnet_group` / `redshift_subnet_group` | Subnet group IDs |
| `nat_ids` / `nat_public_ips` / `natgw_ids` | NAT Gateway Elastic IP allocation IDs, public IPs, and gateway IDs |
| `igw_id` / `egress_only_internet_gateway_id` | Internet Gateway and IPv6 egress-only gateway IDs |
| `private_route_table_ids` / `public_route_table_ids` / `database_route_table_ids` | Route table IDs per tier |
| `default_security_group_id` / `default_network_acl_id` / `default_route_table_id` | Default resource IDs (when managed) |
| `vgw_id` / `cgw_ids` | VPN Gateway and Customer Gateway IDs |

### Usage Examples

#### Example 1: Simple VPC with Public and Private Subnets

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = "simple-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

#### Example 2: Complete VPC with All Subnet Types (Production)

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = "complete-vpc"
  cidr = "10.0.0.0/16"

  azs                 = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets      = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  database_subnets    = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
  elasticache_subnets = ["10.0.31.0/24", "10.0.32.0/24", "10.0.33.0/24"]
  intra_subnets       = ["10.0.51.0/24", "10.0.52.0/24", "10.0.53.0/24"]

  # NAT Gateway - one per AZ for high availability
  enable_nat_gateway     = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  create_database_subnet_group   = true
  create_elasticache_subnet_group = true

  tags = {
    Owner       = "DevOps Team"
    Environment = "production"
    Terraform   = "true"
  }

  vpc_tags = {
    Name = "complete-vpc"
  }
}

# Flow logs and VPC endpoints are provisioned via the dedicated submodules,
# see the flow-log and vpc-endpoints usage examples above.
```

#### Example 3: IPv6 Dual-Stack VPC

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = "ipv6-vpc"
  cidr = "10.0.0.0/16"

  enable_ipv6 = true

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  public_subnet_ipv6_prefixes  = [0, 1, 2]
  private_subnet_ipv6_prefixes = [3, 4, 5]

  public_subnet_assign_ipv6_address_on_creation = true
  enable_ipv6_egress_only_internet_gateway      = true

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = {
    Name = "ipv6-dual-stack-vpc"
  }
}
```

#### Example 4: VPC CIDR from AWS IPAM

```hcl
data "aws_vpc_ipam_pool" "ipv4_example" {
  filter {
    name   = "description"
    values = ["*mypool*"]
  }
  filter {
    name   = "address-family"
    values = ["ipv4"]
  }
}

# CIDR must be known at plan time; preview it from the pool first
data "aws_vpc_ipam_preview_next_cidr" "previewed_cidr" {
  ipam_pool_id   = data.aws_vpc_ipam_pool.ipv4_example.id
  netmask_length = 24
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = "ipam-vpc"

  ipv4_ipam_pool_id = data.aws_vpc_ipam_pool.ipv4_example.id
  cidr              = data.aws_vpc_ipam_preview_next_cidr.previewed_cidr.cidr

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = { IPAM = "true" }
}
```

#### Example 5: VPC with VPC Block Public Access

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = "locked-down-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]

  # Block all bidirectional internet traffic at the VPC level by default
  vpc_block_public_access_options = {
    internet_gateway_block_mode = "block-bidirectional"
  }

  # Explicitly allow a specific resource to bypass the block
  vpc_block_public_access_exclusions = {
    exclude_vpc = {
      exclude_vpc                     = true
      internet_gateway_exclusion_mode = "allow-bidirectional"
    }
  }

  tags = { Security = "block-public-access" }
}
```

#### Example 6: Multi-Tier Application VPC with VPC Endpoints

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = "multi-tier-app-vpc"
  cidr = "10.0.0.0/16"

  azs               = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets   = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets    = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  database_subnets  = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]

  enable_nat_gateway     = true
  one_nat_gateway_per_az = true

  create_database_subnet_group = true

  tags = {
    Application = "multi-tier-app"
    Environment = "production"
  }
}

module "vpc_endpoints" {
  source = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"

  vpc_id = module.vpc.vpc_id

  create_security_group      = true
  security_group_name_prefix = "vpc-endpoints-"
  security_group_rules = {
    ingress_https = {
      description = "HTTPS from VPC"
      cidr_blocks = [module.vpc.vpc_cidr_block]
    }
  }

  endpoints = {
    s3 = {
      service         = "s3"
      service_type    = "Gateway"
      route_table_ids = module.vpc.private_route_table_ids
      tags            = { Name = "s3-vpc-endpoint" }
    }
    ssm = {
      service             = "ssm"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      tags                = { Name = "ssm-vpc-endpoint" }
    }
  }

  tags = { Environment = "production" }
}
```

## Best Practices

### VPC Design and CIDR Planning
1. **Plan CIDR blocks carefully**: Use RFC 1918 space (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) and ensure no overlap with on-premises networks, peered VPCs, or future expansion.
2. **Reserve IP space for growth**: A `/16` VPC with `/24` subnets leaves room to add subnet tiers later; use `secondary_cidr_blocks` rather than recreating the VPC when you run out of space.
3. **Spread across at least 3 AZs**: Set `azs` to three or more zones for production workloads to survive an AZ failure.
4. **Separate subnet tiers by function**: Use distinct public/private/database/intra subnets to implement defense in depth, not a single flat private subnet.
5. **Use intra subnets for internal-only workloads**: Lambda functions or internal services that only talk to VPC endpoints or internal resources belong in `intra_subnets` (no NAT route).
6. **Enable IPv6 at creation time**: Adding IPv6 later is more disruptive than enabling `enable_ipv6` up front if dual-stack is a future requirement.

### NAT Gateway Configuration
1. **Use one NAT Gateway per AZ in production**: `one_nat_gateway_per_az = true` avoids a single point of failure; requires `azs` to be set and enough public subnets.
2. **Use a single NAT Gateway for dev/test**: `single_nat_gateway = true` minimizes cost in non-production environments.
3. **Reuse Elastic IPs when IP stability matters**: Allocate `aws_eip` resources outside the module and pass them via `reuse_nat_ips`/`external_nat_ip_ids` so downstream firewall allow-lists survive VPC recreation.
4. **Offload AWS service traffic to VPC endpoints**: S3 and DynamoDB Gateway endpoints are free and reduce NAT Gateway data-processing costs.

### Security
1. **Enable VPC Block Public Access for sensitive VPCs**: Use `vpc_block_public_access_options` with `block-bidirectional` and add narrow `vpc_block_public_access_exclusions` only where required.
2. **Use the `flow-log` submodule, not root-module flow log variables**: The root module's `enable_flow_log`/`flow_log_*` variables are deprecated and slated for removal.
3. **Layer Network ACLs with security groups**: NACLs are stateless and subnet-wide; use `*_dedicated_network_acl` and `*_inbound_acl_rules`/`*_outbound_acl_rules` for an additional, coarse-grained layer of defense.
4. **Keep applications out of public subnets**: Deploy compute in private subnets and expose services via load balancers, not `map_public_ip_on_launch = true`.
5. **Manage default VPC resources deliberately**: Set `manage_default_security_group`/`manage_default_network_acl` to lock down the implicit default resources rather than leaving them permissive.

### Cost Optimization
1. **Right-size NAT Gateway count**: Single NAT for dev/test, one-per-AZ only where HA is required — NAT Gateways bill hourly plus per-GB data processing.
2. **Prefer Gateway endpoints over Interface endpoints for S3/DynamoDB**: Gateway endpoints have no hourly charge; Interface endpoints bill per-hour per-AZ.
3. **Route flow logs to S3 for long-term retention**: CloudWatch Logs storage costs more than S3 for high-volume, long-retention flow log data.

### Connectivity and Integration
1. **Use Transit Gateway for multi-VPC/hub-and-spoke**: VPC peering is non-transitive; Transit Gateway centralizes routing for complex topologies (see `terraform-aws-modules/transit-gateway`).
2. **Preview IPAM CIDRs before use**: Since the CIDR must be known at `terraform plan` time, use `aws_vpc_ipam_preview_next_cidr` to derive subnet CIDRs from an IPAM-allocated VPC CIDR.
3. **Use VPC endpoints for AWS PrivateLink SaaS integrations**: Keep third-party SaaS traffic off the public internet where the provider supports PrivateLink.

### Operational Excellence
1. **Pin the module version**: Use `version = "~> 6.0"` (or a tighter constraint) to avoid unexpected breaking changes — v6.0.0 raised the minimum AWS provider requirement to v6.x.
2. **Tag comprehensively**: Combine the global `tags` map with resource-specific tag maps (`vpc_tags`, `*_subnet_tags`, `nat_gateway_tags`, etc.) for cost allocation and ownership tracking.
3. **Store Terraform state remotely with locking**: Use S3 + DynamoDB (or equivalent) state backend given how many resources a single VPC apply touches.
4. **Test destructive changes in non-production first**: NAT Gateway strategy or CIDR changes can force subnet/route-table replacement — validate in staging before applying to production.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-vpc
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-vpc/tree/master/examples
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-vpc/blob/master/CHANGELOG.md
- **AWS VPC User Guide**: https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html
- **VPC Endpoints (PrivateLink)**: https://docs.aws.amazon.com/vpc/latest/privatelink/
- **VPC Flow Logs**: https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html
- **VPC Block Public Access**: https://docs.aws.amazon.com/vpc/latest/userguide/security-vpc-bpa.html
- **NAT Gateways**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html
- **AWS Transit Gateway**: https://docs.aws.amazon.com/vpc/latest/tgw/
- **AWS IP Address Manager (IPAM)**: https://docs.aws.amazon.com/vpc/latest/ipam/
- **VPC Security Best Practices**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html

## Notes for AI Agents

When generating Terraform using this module:

1. **Pin the module version** (e.g., `version = "~> 6.0"`) and remember AWS provider `>= 6.28` is required as of v6.0.0.
2. **Use the `flow-log` submodule for flow logs** — do not use the deprecated root-module `enable_flow_log`/`flow_log_*` variables in new code.
3. **Deploy across at least 3 AZs** for production; pass `azs` explicitly when `one_nat_gateway_per_az = true`.
4. **Default to `one_nat_gateway_per_az = true`** for production and `single_nat_gateway = true` for dev/test unless the user specifies otherwise.
5. **Place applications in private subnets**, not public ones; use `database_subnets`/`elasticache_subnets`/`redshift_subnets` for the corresponding managed data stores instead of generic private subnets.
6. **Always set `enable_dns_hostnames = true` and `enable_dns_support = true`** unless the user has a specific reason not to.
7. **Add S3/DynamoDB Gateway endpoints by default** via the `vpc-endpoints` submodule when NAT Gateway is enabled, to reduce NAT data-processing costs.
8. **Consider `vpc_block_public_access_options`** for any VPC that should not be internet-reachable, with narrow `vpc_block_public_access_exclusions` for exceptions.
9. **Use IPAM (`ipv4_ipam_pool_id`) instead of literal CIDRs** when the user mentions centralized/enterprise IP address management; remember the CIDR must be previewable at plan time.
10. **Tag every resource** with at minimum `Environment`, `Terraform = "true"`, and any org-specific ownership tags via the `tags` map.
11. **Reference module outputs for composition** (`vpc_id`, `private_subnets`, `private_route_table_ids`, `vpc_cidr_block`) rather than hardcoding IDs when wiring in other modules (EKS, RDS, ALB, endpoints, flow logs).
