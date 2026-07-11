# Terraform AWS Transit Gateway Module

## Module Information

- **Module Name**: `transit-gateway`
- **Source**: `terraform-aws-modules/transit-gateway/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-transit-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/transit-gateway/aws/latest
- **Latest Version**: 3.3.0
- **Compatibility**: Terraform >= 1.5.7, AWS provider >= 6.28. Since v3.0.0 the module requires AWS provider v6.x and adds the `region` argument — pin `~> 3.0` when generating configs.
- **Purpose**: Terraform module to create and manage an AWS EC2 Transit Gateway with VPC attachments, route tables/routes, and cross-account sharing via Resource Access Manager (RAM)
- **Service**: AWS Transit Gateway (Amazon VPC Transit Gateway)
- **Category**: Networking, Connectivity, Hub-and-Spoke
- **Keywords**: transit-gateway, tgw, hub-and-spoke, vpc-attachment, network-hub, route-table, cross-account, multi-account, ram, resource-access-manager, hybrid-cloud, multicast, ecmp, ipv6, blackhole-route
- **Use For**: multi-VPC connectivity, centralized network routing, hybrid cloud networking, on-premises to AWS connectivity via VPN/Direct Connect, shared services architecture, network segmentation, multi-account networking, cross-account resource sharing, centralized egress

## Description

AWS Transit Gateway is a network transit hub that lets an organization interconnect thousands of VPCs and on-premises networks through a single, centrally managed gateway, replacing complex meshes of point-to-point VPC peering connections. This module provisions the Transit Gateway itself along with its VPC attachments, route table, static/blackhole routes, route table associations and propagations, and — optionally — the AWS Resource Access Manager (RAM) resources needed to share the gateway with other AWS accounts, an organization, or specific organizational units.

The module is a single, standalone Terraform module with no submodules. Its central input, `vpc_attachments`, is a map of maps describing each VPC to attach (VPC ID, subnet IDs, DNS/IPv6/appliance-mode/security-group-referencing options, per-attachment static routes, and optional per-attachment route-table overrides), which the module expands into the corresponding `aws_ec2_transit_gateway_vpc_attachment`, route, association, and propagation resources. It also supports "attachment-only" deployments (`create_tgw = false`) that attach VPCs to a Transit Gateway owned and shared by another account, and can automatically inject routes into the attached VPCs' own route tables via `vpc_route_table_ids`/`tgw_destination_cidr`.

Built for production, enterprise-scale deployments, the module covers advanced Transit Gateway capabilities including IPv6 addressing, multicast traffic distribution, ECMP (Equal-Cost Multi-Path) routing for VPN connections, appliance-mode support for symmetric routing through network appliances, security group referencing across attached VPCs, and encryption-in-transit enforcement between attached VPCs. Comprehensive, resource-level tagging and conditional resource creation (`create_tgw`, `create_tgw_routes`, `share_tgw`) make it a flexible building block for hub-and-spoke, shared-services, and centralized-egress network architectures.

## Key Features

- **Centralized Network Hub**: Single Transit Gateway connecting thousands of VPCs and on-premises networks
- **VPC Attachments**: Attach multiple VPCs via a `vpc_attachments` map, each with its own subnets, routing, and tags
- **Multi-Account Sharing**: Share the Transit Gateway across accounts/OUs/organizations using Resource Access Manager (RAM), or attach to a gateway shared by another account (`create_tgw = false`)
- **Custom Route Table**: Dedicated route table with static and blackhole routes for network segmentation and traffic filtering
- **Route Propagation**: Automatic route propagation from VPC attachments to the default (or a custom) propagation route table
- **VPC Route Table Injection**: Automatically add routes to the attached VPC's own route tables pointing at the Transit Gateway (`vpc_route_table_ids` + `tgw_destination_cidr`)
- **DNS & IPv6 Support**: DNS hostname resolution and IPv4/IPv6 dual-stack routing across attached VPCs
- **Multicast Support**: Distribute multicast traffic across multiple VPCs
- **ECMP Support**: Equal-Cost Multi-Path routing for VPN connections with multiple tunnels
- **Appliance Mode**: Per-attachment `appliance_mode_support` for symmetric routing through network/security appliances
- **Security Group Referencing**: Reference security groups across attached VPCs (must be enabled at both the TGW and the attachment level)
- **Encryption Support**: `enable_encryption_support` enforces encryption-in-transit for traffic between attached VPCs
- **Auto-Accept Attachments**: Automatically accept VPC attachment requests from shared accounts, avoiding manual RAM acceptance
- **Multi-Region Provider Support**: `region` input targets a non-default provider region per module call
- **Flexible Tagging**: Comprehensive tagging at Transit Gateway, route table, default route table, VPC attachment, and RAM levels
- **Conditional Creation**: `create_tgw`, `create_tgw_routes`, and `share_tgw` flags control which resource groups are created

## Main Use Cases

1. **Multi-VPC Connectivity**: Connect hundreds of VPCs through a single Transit Gateway hub
2. **Hybrid Cloud Networking**: Extend on-premises networks to AWS using VPN or Direct Connect
3. **Centralized Internet Egress**: Route outbound traffic through a centralized egress VPC
4. **Shared Services Architecture**: Provide centralized services accessible from all attached VPCs
5. **Network Segmentation**: Isolate environments using separate route tables and blackhole routes
6. **Multi-Account Networking**: Connect VPCs across AWS accounts with centralized management
7. **Cross-Account Resource Sharing**: Share the Transit Gateway via RAM with specific accounts, an organization, or OUs; attach from the receiving account with `create_tgw = false`
8. **Traffic Filtering**: Use blackhole routes to drop traffic to specific destinations
9. **Appliance-Based Inspection**: Route inter-VPC traffic through firewall/inspection appliances using appliance mode

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Resource identifier used across all assets (also the TGW `Name` tag) |
| `description` | `string` | `null` | EC2 Transit Gateway description (defaults to `name` if unset) |
| `region` | `string` | `null` | Region for the resources; defaults to the provider's configured region |
| `amazon_side_asn` | `string` | `null` | Autonomous System Number for BGP (64512-65534 or 4200000000-4294967294) |
| `create_tgw` | `bool` | `true` | Controls whether the Transit Gateway is created (set `false` for attachment-only, cross-account use) |
| `create_tgw_routes` | `bool` | `true` | Controls whether the route table and routes are created |
| `enable_dns_support` | `bool` | `true` | Enable DNS resolution within the Transit Gateway |
| `enable_encryption_support` | `bool` | `false` | Enforce encryption-in-transit for traffic between attached VPCs |
| `enable_multicast_support` | `bool` | `false` | Enable multicast traffic capabilities |
| `enable_vpn_ecmp_support` | `bool` | `true` | Enable VPN Equal Cost Multipath Protocol |
| `enable_auto_accept_shared_attachments` | `bool` | `false` | Automatically accept resource attachment requests |
| `enable_default_route_table_association` | `bool` | `true` | Auto-associate attachments with the default route table |
| `enable_default_route_table_propagation` | `bool` | `true` | Auto-propagate routes to the default route table |
| `enable_sg_referencing_support` | `bool` | `true` | Enable security group referencing at the Transit Gateway level (each attachment must also opt in) |
| `transit_gateway_cidr_blocks` | `list(string)` | `[]` | IPv4/IPv6 CIDR blocks for the TGW (min /24 for IPv4, /64 for IPv6) |
| `transit_gateway_route_table_id` | `string` | `null` | Existing route table ID to reuse when `create_tgw = false` |
| `vpc_attachments` | `any` | `{}` | Map of VPC attachment configurations (see structure below) |
| `timeouts` | `object` | `null` | `create`/`update`/`delete` timeout overrides for the Transit Gateway |
| `share_tgw` | `bool` | `true` | Share the Transit Gateway via RAM (only when `create_tgw = true`) |
| `ram_allow_external_principals` | `bool` | `false` | Allow principals outside the organization |
| `ram_name` | `string` | `""` | Resource Access Manager share name (defaults to `name`) |
| `ram_principals` | `list(string)` | `[]` | Account IDs, Org ARNs, or OU ARNs to share with |
| `ram_resource_share_arn` | `string` | `""` | Existing RAM share ARN to accept when `create_tgw = false` |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |
| `tgw_tags` | `map(string)` | `{}` | Transit Gateway-specific tags |
| `tgw_route_table_tags` | `map(string)` | `{}` | Route table-specific tags |
| `tgw_default_route_table_tags` | `map(string)` | `{}` | Additional tags applied (via `aws_ec2_tag`) to the default association route table |
| `tgw_vpc_attachment_tags` | `map(string)` | `{}` | VPC attachment tags |
| `ram_tags` | `map(string)` | `{}` | RAM resource share tags |

### VPC Attachments Structure

```hcl
vpc_attachments = {
  [attachment_name] = {
    vpc_id                                          = string           # Required: VPC ID to attach
    subnet_ids                                      = list(string)     # Required: Subnet IDs for the attachment
    tgw_id                                          = string           # Optional: Existing TGW ID to attach to (only when create_tgw = false)
    dns_support                                     = bool             # Optional: Enable DNS support (default true)
    ipv6_support                                    = bool             # Optional: Enable IPv6 support (default false)
    appliance_mode_support                          = bool             # Optional: Enable symmetric routing for appliances (default false)
    security_group_referencing_support              = bool             # Optional: Enable SG referencing on this attachment (default false — opt in per attachment even if TGW-level enabled)
    transit_gateway_default_route_table_association = bool             # Optional: Associate with the default route table (default true)
    transit_gateway_default_route_table_propagation = bool             # Optional: Propagate to the default route table (default true)
    transit_gateway_route_table_id                  = string           # Optional: Route table to use instead of the default when association/propagation is disabled
    vpc_route_table_ids                             = list(string)     # Optional: VPC route table IDs to receive a route toward the TGW
    tgw_destination_cidr                            = string           # Optional: Destination CIDR injected into vpc_route_table_ids, targeting the TGW
    tgw_routes = list(object({                                         # Optional: Static routes on the TGW route table
      destination_cidr_block = string                                  # Required: Destination CIDR
      blackhole              = optional(bool)                          # Optional: Create a blackhole route instead of routing to this attachment
    }))
    tags = map(string)                                                 # Optional: Attachment-specific tags (resource Name defaults to "{name}-{attachment_key}")
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
| `ec2_transit_gateway_route_table_id` | Route table identifier created by this module |
| `ec2_transit_gateway_vpc_attachment_ids` | List of VPC attachment IDs |
| `ec2_transit_gateway_vpc_attachment` | Map of VPC attachment attributes |
| `ec2_transit_gateway_route_table_association_ids` | List of route table association IDs |
| `ec2_transit_gateway_route_table_propagation_ids` | List of route table propagation IDs |
| `ec2_transit_gateway_route_ids` | List of route table IDs combined with destination CIDR |
| `ram_resource_share_id` | ARN of the RAM resource share (pass to the consuming account as `ram_resource_share_arn`) |
| `ram_principal_association_id` | ARN of the RAM resource share + principal, comma-separated |

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

### Transit Gateway Shared with Other Accounts (RAM)

```hcl
module "tgw" {
  source  = "terraform-aws-modules/transit-gateway/aws"
  version = "~> 3.0"

  name        = "shared-tgw"
  description = "Transit Gateway shared with multiple accounts"

  amazon_side_asn                       = 64532
  enable_auto_accept_shared_attachments = true

  vpc_attachments = {
    vpc = {
      vpc_id       = "vpc-1234556abcdef"
      subnet_ids   = ["subnet-abcde012", "subnet-bcde012a"]
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

### Cross-Account Attachment (Consuming a Shared Transit Gateway)

Deployed in the receiving account/provider alias, this attaches a local VPC to a Transit Gateway owned and shared by another account, without creating a new gateway:

```hcl
module "tgw_peer" {
  source = "terraform-aws-modules/transit-gateway/aws"
  version = "~> 3.0"

  providers = { aws = aws.peer }

  name        = "tgw-peer"
  description = "Attachment-only TGW consumer"

  create_tgw              = false
  share_tgw                = true
  ram_resource_share_arn   = module.tgw.ram_resource_share_id
  enable_auto_accept_shared_attachments = true

  vpc_attachments = {
    vpc1 = {
      tgw_id       = module.tgw.ec2_transit_gateway_id
      vpc_id       = module.vpc1.vpc_id
      subnet_ids   = module.vpc1.private_subnets
      dns_support  = true
      ipv6_support = true

      transit_gateway_default_route_table_association = false
      transit_gateway_default_route_table_propagation  = false

      # Inject a default route toward the TGW into the VPC's own route tables
      vpc_route_table_ids  = module.vpc1.private_route_table_ids
      tgw_destination_cidr = "0.0.0.0/0"
    }
  }

  ram_allow_external_principals = true
  ram_principals                = [307990089504]

  tags = {
    Environment = "production"
  }
}
```

### Multiple VPC Attachments with Custom ASN and Timeouts

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
  enable_encryption_support             = true

  vpc_attachments = {
    production = {
      vpc_id      = module.vpc_prod.vpc_id
      subnet_ids  = module.vpc_prod.private_subnets
      dns_support = true

      tgw_routes = [
        { destination_cidr_block = "10.0.0.0/8" }
      ]

      tags = { Environment = "production" }
    }

    development = {
      vpc_id      = module.vpc_dev.vpc_id
      subnet_ids  = module.vpc_dev.private_subnets
      dns_support = true

      tgw_routes = [
        { destination_cidr_block = "172.16.0.0/12" }
      ]

      tags = { Environment = "development" }
    }

    shared_services = {
      vpc_id      = module.vpc_shared.vpc_id
      subnet_ids  = module.vpc_shared.private_subnets
      dns_support = true

      tags = { Environment = "shared" }
    }
  }

  timeouts = {
    create = "10m"
    update = "15m"
    delete = "15m"
  }

  tags = {
    Terraform = "true"
  }
}
```

## Best Practices

### Design and Architecture

1. **Hub-and-Spoke Topology**: Use Transit Gateway as the central hub with VPCs as spokes for simplified network management
2. **Separate Attachment Subnets**: Dedicate separate subnets in each VPC specifically for Transit Gateway attachments
3. **Small CIDR Blocks for Attachments**: Use /28 CIDR blocks for Transit Gateway subnets to conserve IP address space
4. **Multi-AZ Attachments**: Deploy attachment subnets across at least two availability zones for high availability
5. **Unique ASN per Transit Gateway**: Assign unique Autonomous System Numbers to each Transit Gateway for BGP routing

### Route Table Configuration

1. **Limit Route Tables**: Minimize the number of route tables; use only what's necessary for segmentation
2. **Segment by Environment**: Create separate route tables for production, development, and testing environments
3. **Enable Route Propagation**: Enable automatic route propagation for Direct Connect and VPN attachments
4. **Blackhole Routes for Security**: Define blackhole routes to explicitly block traffic to specific destinations
5. **VPC Route Injection for Simple Egress**: Use `vpc_route_table_ids` + `tgw_destination_cidr` instead of manually managing routes in consuming VPCs when attaching to a shared TGW

### Security and Access Control

1. **Resource Access Manager**: Use RAM for secure, controlled sharing of the Transit Gateway across accounts
2. **Auto-Accept for Trusted Accounts**: Enable auto-accept shared attachments only for accounts within your organization
3. **Security Group Referencing Opt-In**: Remember `enable_sg_referencing_support` at the TGW level does not enable it per attachment — set `security_group_referencing_support = true` on each attachment that needs it
4. **Network Segmentation**: Use route tables to enforce segmentation and prevent unauthorized east-west traffic
5. **Encryption in Transit**: Enable `enable_encryption_support = true` for workloads requiring encrypted inter-VPC traffic

### Cost Optimization

1. **Consolidate Transit Gateways**: Use a single Transit Gateway per region to minimize per-attachment hourly costs
2. **Regional Traffic**: Keep traffic within the same region when possible to avoid inter-region transfer charges
3. **Remove Unused Attachments**: Regularly audit and remove VPC attachments that are no longer needed

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-transit-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/transit-gateway/aws/latest
- **Complete Example**: https://github.com/terraform-aws-modules/terraform-aws-transit-gateway/tree/master/examples/complete
- **Multi-Account Example**: https://github.com/terraform-aws-modules/terraform-aws-transit-gateway/tree/master/examples/multi-account
- **AWS Transit Gateway Documentation**: https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html
- **Best Design Practices**: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-best-design-practices.html
- **Transit Gateway Routing**: https://docs.aws.amazon.com/vpc/latest/tgw/how-transit-gateways-work.html
- **VPC Attachments**: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-vpc-attachments.html
- **Resource Access Manager**: https://docs.aws.amazon.com/ram/latest/userguide/what-is.html
- **Transit Gateway Pricing**: https://aws.amazon.com/transit-gateway/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **No Submodules**: This is a standalone module with no submodules ("No modules." per its own docs)
2. **All Variables Optional**: All input variables have defaults; `vpc_attachments` is the main configuration surface
3. **VPC Attachment Requirements**: Each attachment needs `vpc_id` and `subnet_ids` (list of subnet IDs, ideally one per AZ)
4. **DNS Support**: Set `dns_support = true` per attachment for hostname resolution across VPCs (the TGW-level `enable_dns_support` must also stay `true`, which is the default)
5. **RAM Sharing**: Set `share_tgw = true` and provide `ram_principals` for cross-account sharing; the recipient account attaches with `create_tgw = false`, `ram_resource_share_arn`, and `tgw_id` set on its attachments
6. **Auto-Accept**: Set `enable_auto_accept_shared_attachments = true` to skip manual attachment acceptance in multi-account setups
7. **Blackhole Routes**: Use `blackhole = true` in an attachment's `tgw_routes` entry to drop traffic to specific CIDRs instead of routing it
8. **Security Group Referencing Gotcha**: TGW-level `enable_sg_referencing_support` defaults to `true`, but each attachment's `security_group_referencing_support` defaults to `false` — both must be true for SG referencing to work on a given attachment
9. **Tagging Strategy**: Use `tags` for all resources, plus resource-specific tags (`tgw_tags`, `tgw_route_table_tags`, `tgw_default_route_table_tags`, `tgw_vpc_attachment_tags`, `ram_tags`)
10. **Existing Route Table**: Use `transit_gateway_route_table_id` (module-level) to reuse an existing route table when `create_tgw = false`, or per-attachment to target a non-default route table
11. **Encryption Support**: Set `enable_encryption_support = true` (added in v3.3.0) to enforce encryption-in-transit between attached VPCs
12. **Version Pinning**: Use `version = "~> 3.0"`; v3.0.0 was a breaking change raising the minimum Terraform version to 1.5.7 and AWS provider to 6.0
13. **Multi-Region**: Use the `region` input to target a non-default provider region for the module's resources
14. **Output References**: Use `ec2_transit_gateway_id` to reference the gateway in VPC route tables or other attachments
