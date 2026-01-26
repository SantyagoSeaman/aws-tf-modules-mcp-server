# Terraform AWS Transit Gateway Module

## Module Information

- **Module Name**: `transit-gateway`
- **Source**: `terraform-aws-modules/transit-gateway/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-transit-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/transit-gateway/aws/latest
- **Latest Version**: 3.0.0
- **Purpose**: Terraform module to create and manage AWS Transit Gateway resources with VPC attachments, routing, and cross-account sharing via Resource Access Manager (RAM)
- **Service**: AWS Transit Gateway (Amazon VPC Transit Gateway)
- **Category**: Networking, Connectivity, Hub-and-Spoke
- **Keywords**: transit-gateway, tgw, vpc-interconnection, network-hub, vpc-attachments, route-tables, vpn-connection, direct-connect, multi-account, cross-account, ram, resource-access-manager, hybrid-cloud, centralized-routing, network-segmentation
- **Use For**: multi-VPC connectivity, centralized network routing, hybrid cloud networking, on-premises to AWS connectivity, shared services architecture, network segmentation, multi-account networking, cross-account resource sharing

## Description

AWS Transit Gateway is a network transit hub that enables organizations to interconnect thousands of VPCs and on-premises networks through a single, centrally managed gateway. This Terraform module simplifies the deployment and management of Transit Gateway resources, including the gateway itself, VPC attachments, route tables, route propagation rules, and cross-account sharing configurations via AWS Resource Access Manager (RAM). The module eliminates the complexity of managing point-to-point VPC peering connections and provides a scalable, hub-and-spoke network architecture.

The module supports comprehensive Transit Gateway features including VPC attachments with subnet associations, custom route table configurations for network segmentation, BGP route propagation for dynamic routing, DNS resolution across connected networks, and security group referencing across attached VPCs. It enables advanced networking patterns such as centralized egress, shared services architectures, and multi-account networking where Transit Gateways are shared across AWS accounts in an organization.

Built for enterprise-scale deployments, the module provides features essential for production environments including IPv6 support, multicast traffic distribution, ECMP (Equal-Cost Multi-Path) routing for VPN connections, and blackhole routing for traffic filtering. With comprehensive tagging, conditional resource creation, and flexible routing configurations, this module serves as the foundation for building scalable, secure, and highly available network architectures in AWS.

## Key Features

- **Centralized Network Hub**: Create single transit hub connecting thousands of VPCs and on-premises networks
- **VPC Attachments**: Attach multiple VPCs with customizable subnet and availability zone configurations
- **Multi-Account Sharing**: Share Transit Gateway across AWS accounts using Resource Access Manager (RAM)
- **Custom Route Tables**: Create route tables for network segmentation and traffic isolation
- **Route Propagation**: Enable automatic route propagation from VPC attachments and VPN connections
- **Static and Blackhole Routes**: Define static routes for precise traffic control and blackhole routes for traffic blocking
- **DNS Support**: Enable DNS hostname resolution across all attached VPCs
- **IPv6 Support**: Full support for IPv6 addressing and routing
- **Multicast Support**: Distribute multicast traffic across multiple VPCs
- **ECMP Support**: Enable Equal-Cost Multi-Path routing for VPN connections
- **Security Group Referencing**: Reference security groups across VPC attachments
- **Auto-Accept Attachments**: Automatically accept VPC attachment requests from shared accounts
- **Flexible Tagging**: Comprehensive tagging at Transit Gateway, route table, attachment, and RAM levels
- **Conditional Creation**: Control resource creation with `create_tgw` and `create_tgw_routes` flags

## Main Use Cases

1. **Multi-VPC Connectivity**: Connect hundreds of VPCs through single Transit Gateway hub
2. **Hybrid Cloud Networking**: Extend on-premises networks to AWS using VPN or Direct Connect
3. **Centralized Internet Egress**: Route outbound traffic through centralized egress VPC
4. **Shared Services Architecture**: Provide centralized services accessible from all VPCs
5. **Network Segmentation**: Isolate environments using separate route tables
6. **Multi-Account Networking**: Connect VPCs across AWS accounts with centralized management
7. **Cross-Account Resource Sharing**: Share Transit Gateway via RAM with specific accounts or OUs
8. **Traffic Filtering**: Use blackhole routes to drop traffic to specific destinations

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Resource identifier used across all assets |
| `description` | `string` | `null` | EC2 Transit Gateway description |
| `amazon_side_asn` | `string` | `null` | Autonomous System Number for BGP (64512-65534 or 4200000000-4294967294) |
| `create_tgw` | `bool` | `true` | Controls whether Transit Gateway is created |
| `create_tgw_routes` | `bool` | `true` | Controls whether route table and routes are created |
| `enable_dns_support` | `bool` | `true` | Enable DNS resolution within Transit Gateway |
| `enable_multicast_support` | `bool` | `false` | Enable multicast traffic capabilities |
| `enable_vpn_ecmp_support` | `bool` | `true` | Enable VPN Equal Cost Multipath Protocol |
| `enable_auto_accept_shared_attachments` | `bool` | `false` | Automatically accept resource attachment requests |
| `enable_default_route_table_association` | `bool` | `true` | Auto-associate with default route table |
| `enable_default_route_table_propagation` | `bool` | `true` | Auto-propagate routes to default table |
| `enable_sg_referencing_support` | `bool` | `true` | Enable security group referencing across VPCs |
| `transit_gateway_cidr_blocks` | `list(string)` | `[]` | IPv4/IPv6 CIDR blocks (min /24 for IPv4, /64 for IPv6) |
| `transit_gateway_route_table_id` | `string` | `null` | Existing route table ID to reuse |
| `vpc_attachments` | `any` | `{}` | Map of VPC attachment configurations |
| `share_tgw` | `bool` | `true` | Share Transit Gateway via RAM |
| `ram_allow_external_principals` | `bool` | `false` | Allow principals outside organization |
| `ram_name` | `string` | `""` | Resource Access Manager share name |
| `ram_principals` | `list(string)` | `[]` | Account IDs, Org ARNs, or OU ARNs to share with |
| `ram_resource_share_arn` | `string` | `""` | Existing RAM share ARN to use |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |
| `tgw_tags` | `map(string)` | `{}` | Transit Gateway-specific tags |
| `tgw_route_table_tags` | `map(string)` | `{}` | Route table-specific tags |
| `tgw_vpc_attachment_tags` | `map(string)` | `{}` | VPC attachment tags |
| `ram_tags` | `map(string)` | `{}` | RAM resource share tags |

### VPC Attachments Structure

```hcl
vpc_attachments = {
  [attachment_name] = {
    vpc_id                                          = string           # Required: VPC ID to attach
    subnet_ids                                      = list(string)     # Required: Subnet IDs for attachment
    dns_support                                     = bool             # Optional: Enable DNS support
    ipv6_support                                    = bool             # Optional: Enable IPv6 support
    security_group_referencing_support              = bool             # Optional: Enable SG referencing
    transit_gateway_default_route_table_association = bool             # Optional: Associate with default RT
    transit_gateway_default_route_table_propagation = bool             # Optional: Propagate to default RT
    tgw_routes = list(object({                                         # Optional: Static routes
      destination_cidr_block = string                                  # Required: Destination CIDR
      blackhole              = bool                                    # Optional: Create blackhole route
    }))
    tags = map(string)                                                 # Optional: Attachment-specific tags
  }
}
```

## Main Outputs

| Output | Description |
|--------|-------------|
| `ec2_transit_gateway_id` | Transit Gateway identifier |
| `ec2_transit_gateway_arn` | Transit Gateway ARN |
| `ec2_transit_gateway_owner_id` | AWS account ID owning the Transit Gateway |
| `ec2_transit_gateway_association_default_route_table_id` | Default association route table ID |
| `ec2_transit_gateway_propagation_default_route_table_id` | Default propagation route table ID |
| `ec2_transit_gateway_route_table_id` | Route table identifier |
| `ec2_transit_gateway_vpc_attachment_ids` | List of VPC attachment IDs |
| `ec2_transit_gateway_vpc_attachment` | Map of VPC attachment attributes |
| `ec2_transit_gateway_route_table_association_ids` | List of route table association IDs |
| `ec2_transit_gateway_route_table_propagation_ids` | List of route table propagation IDs |
| `ec2_transit_gateway_route_ids` | List of route table IDs with destinations |
| `ram_resource_share_id` | RAM resource share ARN |
| `ram_principal_association_id` | RAM principal association ARN |

## Usage Examples

### Basic Transit Gateway

```hcl
module "tgw" {
  source  = "terraform-aws-modules/transit-gateway/aws"
  version = "~> 3.0"

  name        = "my-tgw"
  description = "My Transit Gateway"

  enable_auto_accept_shared_attachments = true

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}
```

### Transit Gateway with VPC Attachment

```hcl
module "tgw" {
  source  = "terraform-aws-modules/transit-gateway/aws"
  version = "~> 3.0"

  name        = "my-tgw"
  description = "Transit Gateway with VPC attachment"

  enable_auto_accept_shared_attachments = true
  enable_dns_support                    = true

  vpc_attachments = {
    vpc1 = {
      vpc_id     = module.vpc.vpc_id
      subnet_ids = module.vpc.private_subnets

      dns_support  = true
      ipv6_support = false

      tgw_routes = [
        {
          destination_cidr_block = "10.10.0.0/16"
        },
        {
          destination_cidr_block = "10.20.0.0/16"
          blackhole              = true
        }
      ]

      tags = {
        Name = "vpc1-attachment"
      }
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Transit Gateway with RAM Sharing

```hcl
module "tgw" {
  source  = "terraform-aws-modules/transit-gateway/aws"
  version = "~> 3.0"

  name        = "shared-tgw"
  description = "Transit Gateway shared with multiple accounts"

  enable_auto_accept_shared_attachments = true

  vpc_attachments = {
    vpc = {
      vpc_id     = "vpc-1234556abcdef"
      subnet_ids = ["subnet-abcde012", "subnet-bcde012a"]

      dns_support  = true
      ipv6_support = true
    }
  }

  # RAM sharing configuration
  share_tgw                     = true
  ram_allow_external_principals = true
  ram_principals                = ["123456789012", "234567890123"]
  ram_name                      = "shared-transit-gateway"

  ram_tags = {
    Purpose = "Cross-account networking"
  }

  tags = {
    Environment = "production"
  }
}
```

### Transit Gateway with Multiple VPC Attachments

```hcl
module "tgw" {
  source  = "terraform-aws-modules/transit-gateway/aws"
  version = "~> 3.0"

  name        = "multi-vpc-tgw"
  description = "Transit Gateway connecting multiple VPCs"

  amazon_side_asn                       = 64512
  enable_auto_accept_shared_attachments = true
  enable_dns_support                    = true
  enable_vpn_ecmp_support               = true

  vpc_attachments = {
    production = {
      vpc_id     = module.vpc_prod.vpc_id
      subnet_ids = module.vpc_prod.private_subnets
      dns_support = true

      tgw_routes = [
        { destination_cidr_block = "10.0.0.0/8" }
      ]

      tags = { Environment = "production" }
    }

    development = {
      vpc_id     = module.vpc_dev.vpc_id
      subnet_ids = module.vpc_dev.private_subnets
      dns_support = true

      tgw_routes = [
        { destination_cidr_block = "172.16.0.0/12" }
      ]

      tags = { Environment = "development" }
    }

    shared_services = {
      vpc_id     = module.vpc_shared.vpc_id
      subnet_ids = module.vpc_shared.private_subnets
      dns_support = true

      tags = { Environment = "shared" }
    }
  }

  tags = {
    Terraform = "true"
  }
}
```

## Best Practices

### Design and Architecture

1. **Hub-and-Spoke Topology**: Use Transit Gateway as central hub with VPCs as spokes for simplified network management
2. **Separate Attachment Subnets**: Dedicate separate subnets in each VPC specifically for Transit Gateway attachments
3. **Small CIDR Blocks for Attachments**: Use /28 CIDR blocks for Transit Gateway subnets to conserve IP address space
4. **Multi-AZ Attachments**: Deploy attachment subnets across at least two availability zones for high availability
5. **Unique ASN per Transit Gateway**: Assign unique Autonomous System Numbers to each Transit Gateway for BGP routing

### Route Table Configuration

1. **Limit Route Tables**: Minimize the number of route tables; use only what's necessary for segmentation
2. **Segment by Environment**: Create separate route tables for production, development, and testing environments
3. **Enable Route Propagation**: Enable automatic route propagation for Direct Connect and VPN attachments
4. **Blackhole Routes for Security**: Define blackhole routes to explicitly block traffic to specific destinations

### Security and Access Control

1. **Resource Access Manager**: Use RAM for secure, controlled sharing of Transit Gateway across accounts
2. **Auto-Accept for Trusted Accounts**: Enable auto-accept shared attachments only for accounts within your organization
3. **Security Group Referencing**: Leverage security group referencing to simplify cross-VPC security rules
4. **Network Segmentation**: Use route tables to enforce network segmentation and prevent unauthorized east-west traffic

### Cost Optimization

1. **Consolidate Transit Gateways**: Use single Transit Gateway per region to minimize per-attachment hourly costs
2. **Regional Traffic**: Keep traffic within same region when possible to avoid inter-region transfer charges
3. **Remove Unused Attachments**: Regularly audit and remove VPC attachments that are no longer needed

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-transit-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/transit-gateway/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-transit-gateway/tree/master/examples
- **AWS Transit Gateway Documentation**: https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html
- **Best Design Practices**: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-best-design-practices.html
- **Transit Gateway Routing**: https://docs.aws.amazon.com/vpc/latest/tgw/how-transit-gateways-work.html
- **VPC Attachments**: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-vpc-attachments.html
- **Resource Access Manager**: https://docs.aws.amazon.com/ram/latest/userguide/what-is.html
- **Transit Gateway Pricing**: https://aws.amazon.com/transit-gateway/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **No Submodules**: This is a standalone module with no submodules
2. **All Variables Optional**: All input variables have defaults; `vpc_attachments` is the main configuration
3. **VPC Attachment Requirements**: Each attachment needs `vpc_id` and `subnet_ids` (list of subnet IDs in different AZs)
4. **DNS Support**: Enable `dns_support = true` in attachments for hostname resolution across VPCs
5. **RAM Sharing**: Set `share_tgw = true` and provide `ram_principals` for cross-account sharing
6. **Auto-Accept**: Set `enable_auto_accept_shared_attachments = true` for automatic attachment acceptance
7. **Blackhole Routes**: Use `blackhole = true` in `tgw_routes` to drop traffic to specific CIDRs
8. **Tagging Strategy**: Use `tags` for all resources, plus specific tags (`tgw_tags`, `ram_tags`, etc.)
9. **Existing Route Table**: Use `transit_gateway_route_table_id` to reuse an existing route table
10. **Security Group Referencing**: Enabled by default via `enable_sg_referencing_support = true`
11. **Version Pinning**: Use `version = "~> 3.0"` for stability
12. **Output References**: Use `ec2_transit_gateway_id` to reference in VPC route tables
