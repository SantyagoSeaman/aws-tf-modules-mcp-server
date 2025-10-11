# Terraform AWS VPC Module

## Module Information

- **Module Name**: terraform-aws-vpc
- **Source**: `terraform-aws-modules/vpc/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-vpc
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest
- **Latest Version**: Check registry for current version
- **Purpose**: Terraform module that creates and manages AWS VPC resources including subnets, route tables, NAT gateways, internet gateways, and network configurations
- **Service**: AWS VPC (Virtual Private Cloud)
- **Category**: Networking, Infrastructure, Network Security
- **Keywords**: vpc, virtual-private-cloud, networking, subnets, public-subnet, private-subnet, nat-gateway, internet-gateway, route-table, network-acl, nacl, security-group, ipv4, ipv6, dual-stack, cidr, availability-zone, az, multi-az, vpn-gateway, customer-gateway, transit-gateway, vpc-peering, vpc-endpoints, flow-logs, dhcp-options, dns, elasticache-subnet, database-subnet, redshift-subnet, intra-subnet, outpost-subnet, ipam, ip-address-management, secondary-cidr, network-routing, bastion, egress, ingress, vpc-flow-logs, cloudwatch-logs
- **Use For**: Multi-tier application hosting, microservices networking, hybrid cloud connectivity, isolated development environments, secure database hosting, high-availability web applications, container orchestration networking, disaster recovery infrastructure, regulatory compliance networking, multi-region architectures, hub-and-spoke network topologies, zero-trust network architectures

## Description

This Terraform module provides comprehensive management of AWS Virtual Private Cloud (VPC) resources, enabling the creation of logically isolated virtual networks within AWS. It handles the complete lifecycle of VPC infrastructure including network topology design, subnet configuration across multiple availability zones, routing table management, internet connectivity through NAT and internet gateways, and advanced networking features like IPv6 support, VPC endpoints, and flow logs. The module abstracts the complexity of AWS networking while providing extensive customization options for enterprise-grade network architectures.

The module addresses common VPC design challenges by offering pre-configured patterns for various subnet types (public, private, database, ElastiCache, Redshift, intra, and outpost subnets) with automatic CIDR block calculation and distribution across availability zones. It supports multiple NAT gateway deployment strategies including single NAT gateway for cost optimization, one NAT gateway per availability zone for high availability, and one NAT gateway per subnet for maximum fault tolerance. The module also handles DNS configuration, DHCP options, and network access control lists (NACLs) for granular traffic control.

Key architectural capabilities include AWS IP Address Manager (IPAM) integration for centralized IP management, secondary CIDR block support for VPC expansion, VPC endpoints for private AWS service access, customer and VPN gateway configuration for hybrid connectivity, and comprehensive tagging strategies for resource organization. The module includes dedicated submodules for VPC endpoints and flow logs, enabling modular composition of network features while maintaining centralized state management and consistent configuration patterns.

## Key Features

- **Two Specialized Submodules**: Modular architecture with vpc-endpoints and flow-log submodules
- **Flexible Subnet Configuration**: Support for public, private, database, ElastiCache, Redshift, intra, and outpost subnet types
- **Multi-AZ Deployment**: Automatic subnet distribution across multiple availability zones for high availability
- **NAT Gateway Strategies**: Three deployment modes - single NAT, one per AZ, or one per subnet
- **Internet Gateway Management**: Automatic internet gateway creation and route table association
- **IPv4 and IPv6 Support**: Dual-stack networking with configurable IPv6 CIDR blocks and prefixes
- **IPAM Integration**: AWS IP Address Manager support for centralized IP address allocation
- **Secondary CIDR Blocks**: Extend VPC IP space with additional CIDR blocks
- **VPC Endpoints**: Private connectivity to AWS services without internet gateway traversal
- **VPN Gateway Support**: Customer gateway and VPN gateway configuration for hybrid cloud connectivity
- **Transit Gateway Integration**: Support for transit gateway attachments and routing
- **VPC Flow Logs**: Network traffic logging to CloudWatch Logs, S3, or Kinesis Data Firehose
- **Network ACLs**: Configurable network access control lists for subnet-level security
- **Route Table Management**: Separate route tables for each subnet type with customizable routes
- **DHCP Options**: Custom DHCP option sets for DNS and domain configuration
- **DNS Support**: Configurable DNS hostnames and DNS resolution settings
- **Default VPC Management**: Ability to manage and customize default VPC settings
- **Database Subnet Groups**: Automatic creation of RDS subnet groups from database subnets
- **ElastiCache Subnet Groups**: Automatic creation of ElastiCache subnet groups
- **Redshift Subnet Groups**: Automatic creation of Redshift subnet groups
- **Outpost Support**: Subnet configuration for AWS Outposts infrastructure
- **Public IP Assignment**: Configurable automatic public IP assignment for public subnets
- **Comprehensive Tagging**: Support for resource tags with tag merging and inheritance
- **Conditional Creation**: Create or skip VPC creation based on variables
- **Customer-Managed Prefix Lists**: Support for prefix lists in route tables
- **VPC Peering**: Integration support for VPC peering connections

## Main Use Cases

1. **Multi-Tier Web Applications**: Host web, application, and database tiers in separate subnets
2. **Microservices Architecture**: Provide network isolation and service-to-service communication
3. **Hybrid Cloud Connectivity**: Connect on-premises data centers with AWS via VPN or Direct Connect
4. **Secure Database Hosting**: Isolate databases in private subnets without direct internet access
5. **Development and Testing Environments**: Create isolated network environments per environment or team
6. **High Availability Deployments**: Distribute resources across multiple availability zones
7. **Container Orchestration**: Network infrastructure for ECS, EKS, or Kubernetes clusters
8. **Regulatory Compliance**: Implement network segmentation for compliance requirements (PCI-DSS, HIPAA)
9. **Hub-and-Spoke Topologies**: Central VPC for shared services with spoke VPCs for applications
10. **Zero-Trust Networking**: Implement micro-segmentation with private subnets and VPC endpoints

## Requirements

### Terraform Version
- **Terraform**: >= 1.0

### Provider Requirements
- **AWS Provider**: >= 6.0

## Submodules

### 1. vpc-endpoints
- **Purpose**: Create VPC endpoints for private connectivity to AWS services
- **Source**: `terraform-aws-modules/vpc/aws//modules/vpc-endpoints`
- **Key Features**: Interface and gateway endpoints, security group configuration, subnet association, tagging support
- **Use Cases**: Private S3 access, DynamoDB connectivity, SSM access without internet gateway, compliance requirements

### 2. flow-log
- **Purpose**: Create VPC flow logs for network traffic monitoring and analysis
- **Source**: `terraform-aws-modules/vpc/aws//modules/flow-log`
- **Key Features**: CloudWatch Logs integration, S3 logging, Kinesis Firehose support, custom log formats
- **Use Cases**: Security monitoring, troubleshooting connectivity issues, network analysis, compliance auditing

## Submodule 1: vpc-endpoints

### Description

The vpc-endpoints submodule creates VPC endpoints that enable private connectivity to AWS services without requiring an internet gateway, NAT device, VPN connection, or AWS Direct Connect. It supports both interface endpoints (powered by AWS PrivateLink) and gateway endpoints, allowing resources in private subnets to securely access AWS services while keeping traffic within the AWS network. The submodule handles security group creation, subnet associations, and endpoint policies for fine-grained access control.

### Key Features

- Support for interface endpoints (AWS PrivateLink) and gateway endpoints
- Automatic security group creation with customizable rules
- Configurable subnet associations for interface endpoints
- Route table associations for gateway endpoints
- Endpoint policy support for access control
- Private DNS enablement for interface endpoints
- Comprehensive tagging for all endpoint resources
- Flexible endpoint configuration with per-service customization

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_id` | `string` | `""` | VPC ID where endpoints will be created |
| `endpoints` | `map(object)` | `{}` | Map of endpoint definitions with service, type, and configuration |
| `security_group_ids` | `list(string)` | `[]` | Default security group IDs to associate with endpoints |
| `subnet_ids` | `list(string)` | `[]` | Default subnet IDs for interface endpoints |
| `create` | `bool` | `true` | Whether to create VPC endpoint resources |
| `tags` | `map(string)` | `{}` | Tags to apply to all endpoint resources |
| `timeouts` | `map(string)` | `{}` | Timeout configuration for endpoint operations |

### Main Outputs

| Output | Description |
|--------|-------------|
| `endpoints` | Map of created VPC endpoint resources with all attributes |
| `security_group_id` | ID of the security group created for VPC endpoints |
| `security_group_arn` | ARN of the security group created for VPC endpoints |

### Usage Example

```hcl
# Create VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "production-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Environment = "production"
  }
}

# Create VPC Endpoints
module "vpc_endpoints" {
  source = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"

  vpc_id = module.vpc.vpc_id

  # Default security group and subnets for interface endpoints
  security_group_ids = [aws_security_group.vpc_endpoints.id]
  subnet_ids         = module.vpc.private_subnets

  endpoints = {
    # S3 Gateway Endpoint
    s3 = {
      service         = "s3"
      service_type    = "Gateway"
      route_table_ids = flatten([
        module.vpc.private_route_table_ids,
        module.vpc.public_route_table_ids
      ])
      tags = {
        Name = "s3-gateway-endpoint"
      }
    }

    # DynamoDB Gateway Endpoint
    dynamodb = {
      service         = "dynamodb"
      service_type    = "Gateway"
      route_table_ids = module.vpc.private_route_table_ids
      tags = {
        Name = "dynamodb-gateway-endpoint"
      }
    }

    # EC2 Interface Endpoint
    ec2 = {
      service             = "ec2"
      private_dns_enabled = true
      tags = {
        Name = "ec2-interface-endpoint"
      }
    }

    # SSM Interface Endpoint
    ssm = {
      service             = "ssm"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      tags = {
        Name = "ssm-interface-endpoint"
      }
    }

    # ECR API Interface Endpoint
    ecr_api = {
      service             = "ecr.api"
      private_dns_enabled = true
      tags = {
        Name = "ecr-api-endpoint"
      }
    }

    # ECR DKR Interface Endpoint
    ecr_dkr = {
      service             = "ecr.dkr"
      private_dns_enabled = true
      tags = {
        Name = "ecr-dkr-endpoint"
      }
    }

    # Custom endpoint with policy
    custom_s3 = {
      service         = "s3"
      service_type    = "Interface"
      private_dns_enabled = false
      subnet_ids      = [module.vpc.private_subnets[0]]

      # Custom endpoint policy
      policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
          {
            Effect = "Allow"
            Principal = "*"
            Action = [
              "s3:GetObject",
              "s3:PutObject"
            ]
            Resource = "arn:aws:s3:::my-bucket/*"
          }
        ]
      })

      tags = {
        Name = "custom-s3-endpoint"
      }
    }
  }

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Security group for VPC endpoints
resource "aws_security_group" "vpc_endpoints" {
  name_prefix = "vpc-endpoints-"
  description = "Security group for VPC endpoints"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "HTTPS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "vpc-endpoints-sg"
  }
}
```

## Submodule 2: flow-log

### Description

The flow-log submodule creates VPC flow logs that capture information about IP traffic going to and from network interfaces in a VPC, subnet, or elastic network interface. Flow logs help monitor network traffic patterns, troubleshoot connectivity issues, detect security threats, and ensure compliance with network security policies. The submodule supports publishing flow log data to CloudWatch Logs, Amazon S3, or Amazon Kinesis Data Firehose with customizable log formats and aggregation intervals.

### Key Features

- Support for VPC, subnet, ENI, and transit gateway flow logs
- Multiple log destinations: CloudWatch Logs, S3, Kinesis Data Firehose
- Customizable log format with specific fields selection
- Configurable traffic type filtering (ACCEPT, REJECT, or ALL)
- IAM role automatic creation and management
- CloudWatch log group creation with retention policies
- Custom log aggregation intervals (60 or 600 seconds)
- Partition-based S3 logging for cost optimization
- Tagging support for flow log resources

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_id` | `string` | `null` | VPC ID to attach flow logs (required if not using subnet_id or eni_id) |
| `subnet_id` | `string` | `null` | Subnet ID to attach flow logs |
| `eni_id` | `string` | `null` | Elastic Network Interface ID to attach flow logs |
| `log_destination_type` | `string` | `"cloud-watch-logs"` | Type of log destination (cloud-watch-logs, s3, kinesis-data-firehose) |
| `log_destination` | `string` | `null` | ARN of the logging destination |
| `traffic_type` | `string` | `"ALL"` | Type of traffic to capture (ACCEPT, REJECT, or ALL) |
| `log_format` | `string` | `null` | Custom log format fields |
| `max_aggregation_interval` | `number` | `600` | Maximum aggregation interval in seconds (60 or 600) |
| `cloudwatch_log_group_name` | `string` | `null` | Name of CloudWatch log group |
| `cloudwatch_log_group_retention_in_days` | `number` | `null` | Log retention period in days |

### Main Outputs

| Output | Description |
|--------|-------------|
| `flow_log_id` | ID of the VPC flow log |
| `flow_log_arn` | ARN of the VPC flow log |
| `cloudwatch_log_group_name` | Name of CloudWatch log group (if applicable) |
| `cloudwatch_log_group_arn` | ARN of CloudWatch log group (if applicable) |
| `iam_role_arn` | ARN of the IAM role created for flow logs |

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

# VPC Flow Logs to CloudWatch
module "vpc_flow_logs_cloudwatch" {
  source = "terraform-aws-modules/vpc/aws//modules/flow-log"

  vpc_id = module.vpc.vpc_id

  # CloudWatch Logs destination
  log_destination_type = "cloud-watch-logs"

  # Custom log group name
  cloudwatch_log_group_name = "/aws/vpc/production-vpc-flow-logs"

  # Retention period
  cloudwatch_log_group_retention_in_days = 30

  # Capture all traffic
  traffic_type = "ALL"

  # 1-minute aggregation for faster visibility
  max_aggregation_interval = 60

  tags = {
    Name        = "production-vpc-flow-logs"
    Environment = "production"
  }
}
```

#### Example 2: S3 Destination with Custom Format

```hcl
# S3 bucket for flow logs
resource "aws_s3_bucket" "flow_logs" {
  bucket = "my-vpc-flow-logs"
}

resource "aws_s3_bucket_lifecycle_configuration" "flow_logs" {
  bucket = aws_s3_bucket.flow_logs.id

  rule {
    id     = "delete-old-logs"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    expiration {
      days = 90
    }
  }
}

# VPC Flow Logs to S3
module "vpc_flow_logs_s3" {
  source = "terraform-aws-modules/vpc/aws//modules/flow-log"

  vpc_id = module.vpc.vpc_id

  # S3 destination
  log_destination_type = "s3"
  log_destination      = aws_s3_bucket.flow_logs.arn

  # Custom log format with specific fields
  log_format = "$${version} $${account-id} $${interface-id} $${srcaddr} $${dstaddr} $${srcport} $${dstport} $${protocol} $${packets} $${bytes} $${start} $${end} $${action} $${log-status}"

  # Capture only rejected traffic for security monitoring
  traffic_type = "REJECT"

  tags = {
    Name    = "vpc-flow-logs-security"
    Purpose = "Security Monitoring"
  }
}
```

#### Example 3: Subnet-Specific Flow Logs

```hcl
# Flow logs for specific private subnet
module "private_subnet_flow_logs" {
  source = "terraform-aws-modules/vpc/aws//modules/flow-log"

  subnet_id = module.vpc.private_subnets[0]

  log_destination_type = "cloud-watch-logs"
  cloudwatch_log_group_name = "/aws/vpc/private-subnet-flow-logs"
  cloudwatch_log_group_retention_in_days = 7

  # Only capture accepted traffic
  traffic_type = "ACCEPT"

  tags = {
    Name   = "private-subnet-flow-logs"
    Subnet = "private-a"
  }
}
```

## Main Module: VPC

### Description

The main VPC module provides comprehensive creation and configuration of AWS Virtual Private Cloud resources with complete control over network topology, routing, and connectivity. This module handles the entire VPC lifecycle including subnet creation across availability zones, NAT and internet gateway management, route table configuration, and network ACL setup.

### Key Features

- Complete VPC lifecycle management with CIDR configuration
- Automatic subnet distribution across availability zones
- Multiple subnet types (public, private, database, ElastiCache, Redshift, intra, outpost)
- Flexible NAT gateway deployment strategies
- Internet gateway and route table management
- IPv4 and IPv6 dual-stack support
- IPAM integration for IP address management
- Secondary CIDR block support
- VPN and customer gateway configuration
- DHCP options customization
- DNS hostname and resolution settings

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name to be used on all resources as prefix |
| `cidr` | `string` | `"10.0.0.0/16"` | CIDR block for the VPC |
| `azs` | `list(string)` | `[]` | List of availability zones names or IDs |
| `public_subnets` | `list(string)` | `[]` | List of public subnet CIDR blocks |
| `private_subnets` | `list(string)` | `[]` | List of private subnet CIDR blocks |
| `database_subnets` | `list(string)` | `[]` | List of database subnet CIDR blocks |
| `elasticache_subnets` | `list(string)` | `[]` | List of ElastiCache subnet CIDR blocks |
| `redshift_subnets` | `list(string)` | `[]` | List of Redshift subnet CIDR blocks |
| `intra_subnets` | `list(string)` | `[]` | List of intra subnet CIDR blocks (no internet access) |
| `enable_nat_gateway` | `bool` | `false` | Provision NAT gateways for private networks |
| `single_nat_gateway` | `bool` | `false` | Use single NAT gateway for all private networks |
| `one_nat_gateway_per_az` | `bool` | `false` | Create one NAT gateway per availability zone |
| `enable_dns_hostnames` | `bool` | `true` | Enable DNS hostnames in the VPC |
| `enable_dns_support` | `bool` | `true` | Enable DNS support in the VPC |
| `enable_ipv6` | `bool` | `false` | Enable IPv6 support |
| `ipv4_ipam_pool_id` | `string` | `null` | IPAM pool ID for IPv4 CIDR allocation |

### Main Outputs

| Output | Description |
|--------|-------------|
| `vpc_id` | ID of the VPC |
| `vpc_arn` | ARN of the VPC |
| `vpc_cidr_block` | CIDR block of the VPC |
| `private_subnets` | List of IDs of private subnets |
| `public_subnets` | List of IDs of public subnets |
| `database_subnets` | List of IDs of database subnets |
| `database_subnet_group` | ID of database subnet group |
| `elasticache_subnets` | List of IDs of ElastiCache subnets |
| `elasticache_subnet_group` | ID of ElastiCache subnet group |
| `redshift_subnets` | List of IDs of Redshift subnets |
| `redshift_subnet_group` | ID of Redshift subnet group |
| `intra_subnets` | List of IDs of intra subnets |
| `nat_ids` | List of allocation IDs of Elastic IPs for NAT gateways |
| `nat_public_ips` | List of public Elastic IPs created for NAT gateways |
| `natgw_ids` | List of NAT gateway IDs |
| `igw_id` | ID of internet gateway |
| `private_route_table_ids` | List of IDs of private route tables |
| `public_route_table_ids` | List of IDs of public route tables |
| `azs` | List of availability zones specified as argument |

### Usage Examples

#### Example 1: Simple VPC with Public and Private Subnets

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "simple-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

#### Example 2: Complete VPC with All Subnet Types

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "complete-vpc"
  cidr = "10.0.0.0/16"

  azs                 = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets      = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  database_subnets    = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
  elasticache_subnets = ["10.0.31.0/24", "10.0.32.0/24", "10.0.33.0/24"]
  redshift_subnets    = ["10.0.41.0/24", "10.0.42.0/24", "10.0.43.0/24"]
  intra_subnets       = ["10.0.51.0/24", "10.0.52.0/24", "10.0.53.0/24"]

  # NAT Gateway - one per AZ for high availability
  enable_nat_gateway     = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = true

  # DNS settings
  enable_dns_hostnames = true
  enable_dns_support   = true

  # VPN Gateway
  enable_vpn_gateway = true

  # Database subnet group
  create_database_subnet_group = true
  database_subnet_group_name   = "complete-vpc-db"

  # ElastiCache subnet group
  create_elasticache_subnet_group = true
  elasticache_subnet_group_name   = "complete-vpc-cache"

  # Redshift subnet group
  create_redshift_subnet_group = true
  redshift_subnet_group_name   = "complete-vpc-redshift"

  # Custom tags
  tags = {
    Owner       = "DevOps Team"
    Environment = "production"
    Terraform   = "true"
  }

  # VPC tags
  vpc_tags = {
    Name = "complete-vpc"
  }

  # Subnet tags
  public_subnet_tags = {
    Type = "Public"
  }

  private_subnet_tags = {
    Type = "Private"
  }

  database_subnet_tags = {
    Type = "Database"
  }
}
```

#### Example 3: IPv6 Dual-Stack VPC

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "ipv6-vpc"
  cidr = "10.0.0.0/16"

  # Enable IPv6
  enable_ipv6 = true

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  # IPv6 subnet prefixes (assigned automatically if not specified)
  public_subnet_ipv6_prefixes  = [0, 1, 2]
  private_subnet_ipv6_prefixes = [3, 4, 5]

  # Enable IPv6 on creation
  public_subnet_assign_ipv6_address_on_creation = true

  # IPv6 egress-only internet gateway for private subnets
  enable_ipv6_egress_only_internet_gateway = true

  enable_nat_gateway = true
  single_nat_gateway = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "ipv6-dual-stack-vpc"
    IPv6Enabled = "true"
  }
}
```

#### Example 4: VPC with IPAM Integration

```hcl
# IPAM Pool (must be created separately)
resource "aws_vpc_ipam_pool" "main" {
  address_family = "ipv4"
  ipam_scope_id  = aws_vpc_ipam.main.private_default_scope_id
  locale         = "us-east-1"

  allocation_default_netmask_length = 16
  allocation_max_netmask_length     = 24
  allocation_min_netmask_length     = 16
}

resource "aws_vpc_ipam_pool_cidr" "main" {
  ipam_pool_id = aws_vpc_ipam_pool.main.id
  cidr         = "10.0.0.0/8"
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "ipam-vpc"

  # Use IPAM for CIDR allocation
  ipv4_ipam_pool_id   = aws_vpc_ipam_pool.main.id
  ipv4_netmask_length = 16

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = {
    IPAM = "true"
  }
}
```

#### Example 5: VPC with Custom Network ACLs

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "custom-nacl-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true

  # Manage default network ACL
  manage_default_network_acl = true
  default_network_acl_name   = "default-nacl"

  default_network_acl_ingress = [
    {
      rule_no    = 100
      protocol   = "tcp"
      action     = "allow"
      cidr_block = "0.0.0.0/0"
      from_port  = 443
      to_port    = 443
    },
    {
      rule_no    = 110
      protocol   = "tcp"
      action     = "allow"
      cidr_block = "0.0.0.0/0"
      from_port  = 80
      to_port    = 80
    },
    {
      rule_no    = 120
      protocol   = "tcp"
      action     = "allow"
      cidr_block = "10.0.0.0/16"
      from_port  = 0
      to_port    = 65535
    }
  ]

  default_network_acl_egress = [
    {
      rule_no    = 100
      protocol   = "-1"
      action     = "allow"
      cidr_block = "0.0.0.0/0"
      from_port  = 0
      to_port    = 0
    }
  ]

  # Public subnet Network ACL
  public_dedicated_network_acl = true
  public_inbound_acl_rules = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_block  = "0.0.0.0/0"
    },
    {
      rule_number = 110
      rule_action = "allow"
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_block  = "0.0.0.0/0"
    }
  ]

  public_outbound_acl_rules = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_block  = "0.0.0.0/0"
    }
  ]

  tags = {
    Security = "Custom-NACL"
  }
}
```

#### Example 6: Multi-Tier Application VPC with VPC Endpoints

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "multi-tier-app-vpc"
  cidr = "10.0.0.0/16"

  azs              = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets   = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  database_subnets = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]

  enable_nat_gateway     = true
  one_nat_gateway_per_az = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  create_database_subnet_group = true

  tags = {
    Application = "Multi-Tier-App"
    Environment = "production"
  }
}

# VPC Endpoints for private subnet access to AWS services
module "vpc_endpoints" {
  source = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"

  vpc_id             = module.vpc.vpc_id
  security_group_ids = [aws_security_group.vpc_endpoints.id]

  endpoints = {
    s3 = {
      service         = "s3"
      service_type    = "Gateway"
      route_table_ids = module.vpc.private_route_table_ids
      tags            = { Name = "s3-vpc-endpoint" }
    }
    dynamodb = {
      service         = "dynamodb"
      service_type    = "Gateway"
      route_table_ids = module.vpc.private_route_table_ids
      tags            = { Name = "dynamodb-vpc-endpoint" }
    }
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
  }
}

resource "aws_security_group" "vpc_endpoints" {
  name_prefix = "vpc-endpoints-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  tags = {
    Name = "vpc-endpoints-sg"
  }
}
```

## Best Practices

### VPC Design and Architecture

1. **Plan CIDR Blocks Carefully**: Choose CIDR blocks that won't overlap with on-premises networks, other VPCs, or future expansion needs. Use RFC 1918 address space (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16).
2. **Use Multiple Availability Zones**: Distribute subnets across at least three availability zones for high availability and fault tolerance.
3. **Reserve IP Space**: Leave room for growth by not allocating all available CIDR space initially. Consider using /16 for VPC and /24 for subnets.
4. **Separate Subnet Tiers**: Use distinct subnet types (public, private, database) to implement defense in depth and network segmentation.
5. **Use Intra Subnets for Management**: Deploy management tools, monitoring systems, or internal services in intra subnets with no internet access.
6. **Plan for IPv6 Early**: If IPv6 support is needed, enable it during VPC creation to avoid migration complexity later.
7. **Document Network Architecture**: Maintain clear documentation of CIDR allocations, subnet purposes, and routing designs.
8. **Use Consistent Naming**: Apply consistent naming conventions across VPCs, subnets, and resources for easier management.

### Subnet Configuration

1. **Right-Size Subnets**: Allocate subnet sizes based on expected resource count. Common practice is /24 (251 usable IPs) for most subnets.
2. **Distribute Evenly Across AZs**: Create equal numbers of each subnet type across all availability zones for balanced deployments.
3. **Use Database Subnets**: Always place databases in dedicated database subnets, not general-purpose private subnets.
4. **Enable Auto-Assign Public IP**: Set `map_public_ip_on_launch = true` only for public subnets where resources need direct internet access.
5. **Tag Subnets for EKS/ECS**: Use proper tags for Kubernetes subnet discovery (kubernetes.io/role/elb, kubernetes.io/role/internal-elb).
6. **Separate Cache Layers**: Use dedicated ElastiCache subnets for caching infrastructure to isolate from application tiers.
7. **Plan for Secondary CIDRs**: If you need to expand VPC address space, use secondary CIDR blocks rather than recreating the VPC.

### NAT Gateway Configuration

1. **Use One NAT Gateway Per AZ**: Set `one_nat_gateway_per_az = true` for production environments to ensure high availability.
2. **Single NAT for Development**: Use `single_nat_gateway = true` for development/test environments to reduce costs.
3. **Monitor NAT Gateway Metrics**: Set CloudWatch alarms for NAT gateway packet drops, connection errors, and bandwidth limits.
4. **Consider NAT Instances for Low Traffic**: For very low traffic environments, NAT instances may be more cost-effective than NAT gateways.
5. **Place NAT in Public Subnets**: Ensure NAT gateways are deployed in public subnets with proper internet gateway routes.
6. **Budget for NAT Costs**: NAT gateways have hourly charges plus data processing fees - monitor and optimize usage.
7. **Use VPC Endpoints to Reduce NAT Traffic**: Implement VPC endpoints for AWS services to bypass NAT gateway and reduce costs.

### Security and Access Control

1. **Enable VPC Flow Logs**: Always enable flow logs for security monitoring, troubleshooting, and compliance auditing.
2. **Use Network ACLs as Additional Layer**: Implement NACLs as stateless firewalls in addition to security groups for defense in depth.
3. **Block Public Access by Default**: Set default NACL rules to deny all traffic, then explicitly allow required traffic.
4. **Implement VPC Endpoints**: Use VPC endpoints (especially gateway endpoints for S3 and DynamoDB) to keep traffic within AWS network.
5. **Enable DNS Hostnames**: Set `enable_dns_hostnames = true` and `enable_dns_support = true` for proper DNS resolution.
6. **Use Private Subnets for Applications**: Deploy application servers in private subnets and use load balancers or bastion hosts for access.
7. **Restrict NACL Rules**: Create specific NACL rules rather than allowing all traffic. Use rule numbers strategically for future insertions.
8. **Enable GuardDuty VPC Integration**: Use Amazon GuardDuty with VPC flow logs for threat detection and security monitoring.

### High Availability and Resilience

1. **Deploy Across Multiple AZs**: Use at least three availability zones for critical workloads to survive AZ failures.
2. **Use Route 53 Health Checks**: Implement health checks and failover routing for critical endpoints.
3. **Enable Transit Gateway**: For multi-VPC architectures, use Transit Gateway instead of VPC peering for simplified management.
4. **Test Failover Scenarios**: Regularly test AZ failover and disaster recovery procedures to validate high availability.
5. **Monitor Resource Limits**: Track VPC resource limits (subnets, route tables, endpoints) and request increases before hitting limits.
6. **Use Elastic IPs Sparingly**: Allocate Elastic IPs only when static public IPs are absolutely required to avoid waste.

### Cost Optimization

1. **Right-Size NAT Gateways**: Use single NAT gateway for dev/test, one per AZ for production based on actual needs.
2. **Use Gateway Endpoints**: S3 and DynamoDB gateway endpoints are free - use them instead of interface endpoints or NAT.
3. **Monitor Data Transfer**: Track inter-AZ data transfer costs and optimize application architecture to minimize cross-AZ traffic.
4. **Clean Up Unused Resources**: Remove unused NAT gateways, VPN connections, and endpoints to avoid unnecessary charges.
5. **Use Interface Endpoints Strategically**: Interface endpoints cost $0.01/hour - only create them for services you actually use from private subnets.
6. **Optimize VPC Peering**: Use VPC peering for direct connections between VPCs instead of routing through NAT gateways.
7. **Review Flow Log Costs**: Flow logs to CloudWatch Logs can be expensive - use S3 destination for cost-effective long-term storage.

### Operational Excellence

1. **Use Terraform State Locking**: Store VPC Terraform state in S3 with DynamoDB locking to prevent concurrent modifications.
2. **Tag Everything**: Apply comprehensive tags including Environment, Owner, CostCenter, Application for resource organization.
3. **Version Pin the Module**: Use specific module versions (e.g., `version = "~> 5.0"`) in production to prevent unexpected changes.
4. **Implement Change Control**: Use pull requests and peer review for all VPC infrastructure changes.
5. **Monitor with CloudWatch**: Set up CloudWatch dashboards for VPC metrics, NAT gateway performance, and flow log analysis.
6. **Use AWS Config**: Enable AWS Config rules to monitor VPC compliance with organizational policies.
7. **Document Dependencies**: Clearly document which applications and services depend on each VPC resource.
8. **Test in Non-Production First**: Always test VPC changes in development or staging environments before applying to production.

### Connectivity and Integration

1. **Use VPN for Hybrid Cloud**: Implement VPN gateway and customer gateway for secure on-premises connectivity.
2. **Consider Direct Connect**: For high-bandwidth or low-latency requirements, use AWS Direct Connect instead of VPN.
3. **Enable Transit Gateway**: For hub-and-spoke or complex multi-VPC architectures, use Transit Gateway for centralized routing.
4. **Use VPC Peering Carefully**: VPC peering is non-transitive - use Transit Gateway for transitive routing requirements.
5. **Configure DHCP Options**: Set custom DHCP option sets for DNS servers, NTP servers, or domain names when needed.
6. **Enable VPN Monitoring**: Monitor VPN tunnel status and set up CloudWatch alarms for tunnel failures.
7. **Use PrivateLink**: Implement AWS PrivateLink for private connectivity to third-party SaaS applications.

### Compliance and Governance

1. **Enable VPC Flow Logs to S3**: Store flow logs in S3 with lifecycle policies for long-term compliance retention.
2. **Implement Resource Tagging Policies**: Use AWS Organizations tag policies to enforce consistent tagging across VPCs.
3. **Use Service Control Policies**: Implement SCPs to prevent unauthorized VPC modifications or public subnet creation.
4. **Enable AWS CloudTrail**: Log all VPC API calls to CloudTrail for audit trails and compliance reporting.
5. **Implement Network Segmentation**: Use separate VPCs or subnets for different compliance zones (PCI, HIPAA, etc.).
6. **Regular Security Audits**: Conduct quarterly reviews of NACL rules, security groups, and routing tables.
7. **Use AWS Security Hub**: Enable Security Hub to aggregate security findings and compliance checks across VPCs.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-vpc
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-vpc/tree/master/examples
- **AWS VPC Documentation**: https://docs.aws.amazon.com/vpc/latest/userguide/
- **AWS VPC User Guide**: https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html
- **VPC Peering**: https://docs.aws.amazon.com/vpc/latest/peering/
- **VPC Endpoints**: https://docs.aws.amazon.com/vpc/latest/privatelink/
- **VPC Flow Logs**: https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html
- **NAT Gateways**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html
- **AWS Transit Gateway**: https://docs.aws.amazon.com/vpc/latest/tgw/
- **VPN Connections**: https://docs.aws.amazon.com/vpn/latest/s2svpn/
- **AWS Direct Connect**: https://docs.aws.amazon.com/directconnect/latest/UserGuide/
- **VPC Security Best Practices**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html
- **AWS Well-Architected Framework**: https://aws.amazon.com/architecture/well-architected/
- **VPC Pricing**: https://aws.amazon.com/vpc/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Plan CIDR Carefully**: Always validate CIDR blocks don't overlap with existing networks
2. **Multi-AZ by Default**: Deploy across at least 3 availability zones for production
3. **Use Private Subnets**: Place applications in private subnets, not public
4. **Enable NAT Gateway**: Set one_nat_gateway_per_az = true for high availability
5. **Enable DNS Settings**: Always enable DNS hostnames and DNS support
6. **Tag Comprehensively**: Include Environment, Application, Owner, CostCenter tags
7. **Use VPC Endpoints**: Implement S3 and DynamoDB gateway endpoints to reduce NAT costs
8. **Enable Flow Logs**: Always enable VPC flow logs for security and troubleshooting
9. **Separate Database Subnets**: Use dedicated database subnets, not general private subnets
10. **Version Pin Module**: Use specific module versions to prevent unexpected changes
11. **Test AZ Failures**: Validate high availability by testing AZ failure scenarios
12. **Monitor NAT Costs**: Track NAT gateway data processing fees and optimize with endpoints
13. **Use Intra Subnets**: Deploy management tools in intra subnets for better isolation
14. **Enable IPv6 Early**: If needed, enable IPv6 during initial VPC creation
15. **Document Architecture**: Maintain clear documentation of network design and CIDR allocations
16. **Use IPAM**: Leverage AWS IPAM for centralized IP address management at scale
17. **Implement NACLs**: Add network ACLs as additional security layer beyond security groups
18. **Regular Audits**: Conduct quarterly reviews of routing, NACLs, and security configurations
