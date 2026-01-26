# Terraform AWS Customer Gateway Module

## Module Information

- **Module Name**: `customer-gateway`
- **Source**: `terraform-aws-modules/customer-gateway/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-customer-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/customer-gateway/aws/latest
- **Latest Version**: 3.1.1
- **Purpose**: Creates AWS Customer Gateway resources for Site-to-Site VPN connections between on-premises networks and AWS VPCs
- **Service**: AWS VPN (Virtual Private Network) - Customer Gateway Component
- **Category**: Networking, Hybrid Cloud, Security
- **Keywords**: customer-gateway, cgw, site-to-site-vpn, vpn, ipsec, bgp, hybrid-cloud, on-premises, transit-gateway, virtual-private-gateway, vpn-tunnel, datacenter-connectivity
- **Use For**: Connecting on-premises data centers to AWS VPCs, establishing hybrid cloud networking, extending corporate networks to AWS securely, creating redundant VPN connections for high availability, building multi-region hybrid architectures

## Description

The AWS Customer Gateway Terraform module simplifies the creation and management of AWS Customer Gateway resources, which represent the customer side of a Site-to-Site VPN connection between an on-premises network and Amazon VPC. A Customer Gateway is an AWS resource that contains information about your customer gateway device—the physical or software appliance on your side of the VPN connection, including its public IP address, BGP Autonomous System Number (ASN), and optional certificate-based authentication.

Site-to-Site VPN connections provide secure, encrypted IPsec tunnels between on-premises infrastructure and AWS. The module supports creating multiple customer gateways simultaneously through a map-based configuration approach, making it ideal for organizations with multiple data centers or branch offices. It integrates seamlessly with VPC, Virtual Private Gateway, and Transit Gateway modules for complete hybrid networking solutions.

## Key Features

- **Multiple Customer Gateways**: Create multiple customer gateway resources in a single module using map-based configuration
- **BGP Configuration**: Specify BGP Autonomous System Number (ASN) for dynamic routing
- **External IP Definition**: Configure the public IP address of on-premises VPN devices
- **Certificate Authentication**: Support for certificate-based authentication via `certificate_arn`
- **Device Naming**: Optional device name identifier for better resource identification
- **Conditional Creation**: Control resource creation using the `create` flag
- **Comprehensive Tagging**: Apply custom tags to all resources
- **Output Integration**: Provides gateway IDs and full attributes for VPN connection configurations

## Main Use Cases

1. **Hybrid Cloud Connectivity**: Connect on-premises data centers to AWS VPCs for hybrid architectures
2. **Disaster Recovery**: Establish VPN connections for DR scenarios with persistent connectivity
3. **Branch Office Integration**: Connect multiple branch office locations to centralized AWS infrastructure
4. **Multi-Region Hybrid**: Create customer gateways in multiple regions for global deployments
5. **Migration Workflows**: Maintain on-premises connectivity during phased cloud migration
6. **Transit Gateway Hub**: Create customer gateways as spokes connecting to AWS Transit Gateway

## Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create Customer Gateway resources |
| `name` | `string` | `""` | Name prefix for all created resources |
| `customer_gateways` | `map(map(any))` | `{}` | Map of Customer Gateway configurations |
| `tags` | `map(string)` | `{}` | Tags to assign to all resources |

### Customer Gateway Map Structure

Each entry in the `customer_gateways` map supports:

| Attribute | Type | Description |
|-----------|------|-------------|
| `bgp_asn` | `number` | BGP autonomous system number (use 64512-65534 for private ASN) |
| `ip_address` | `string` | Public IP address of the on-premises VPN device |
| `certificate_arn` | `string` | ARN for certificate-based authentication (optional) |
| `device_name` | `string` | Name identifier for the device (optional) |

## Outputs

| Output | Description |
|--------|-------------|
| `ids` | List of IDs of created Customer Gateway resources |
| `customer_gateway` | Map of Customer Gateway attributes (full resource details) |

## Usage Examples

### Basic Single Customer Gateway

```hcl
module "cgw" {
  source  = "terraform-aws-modules/customer-gateway/aws"
  version = "~> 3.1"

  name = "datacenter-cgw"

  customer_gateways = {
    primary = {
      bgp_asn    = 65112
      ip_address = "203.0.113.10"
    }
  }

  tags = {
    Environment = "production"
    Project     = "vpn-connectivity"
  }
}
```

### Multiple Customer Gateways for Redundancy

```hcl
module "cgw" {
  source  = "terraform-aws-modules/customer-gateway/aws"
  version = "~> 3.1"

  name = "multi-site-cgw"

  customer_gateways = {
    datacenter_primary = {
      bgp_asn    = 65112
      ip_address = "203.0.113.10"
    }
    datacenter_secondary = {
      bgp_asn    = 65112
      ip_address = "203.0.113.20"
    }
    branch_office = {
      bgp_asn    = 65113
      ip_address = "198.51.100.5"
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Complete VPN Setup with VPC Integration

```hcl
# Customer Gateways
module "cgw" {
  source  = "terraform-aws-modules/customer-gateway/aws"
  version = "~> 3.1"

  name = "production-cgw"

  customer_gateways = {
    datacenter1 = {
      bgp_asn    = 65112
      ip_address = "203.0.113.10"
    }
    datacenter2 = {
      bgp_asn    = 65112
      ip_address = "203.0.113.20"
    }
  }

  tags = {
    Environment = "production"
  }
}

# VPC with VPN Gateway
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "production-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]

  enable_vpn_gateway = true
}

# VPN Connections
module "vpn_gateway" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 3.0"

  for_each = module.cgw.customer_gateway

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = each.value.id

  vpc_id                       = module.vpc.vpc_id
  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(module.vpc.private_route_table_ids)
}
```

### Certificate-Based Authentication

```hcl
module "cgw" {
  source  = "terraform-aws-modules/customer-gateway/aws"
  version = "~> 3.1"

  name = "cert-auth-cgw"

  customer_gateways = {
    secure_gateway = {
      bgp_asn         = 65112
      ip_address      = "203.0.113.10"
      certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/abc123"
      device_name     = "cisco-asa-primary"
    }
  }

  tags = {
    Environment = "production"
    Security    = "high"
  }
}
```

## Best Practices

### Customer Gateway Configuration

1. **Use Static Public IPs**: Configure customer gateways with static public IP addresses to prevent connection disruptions
2. **BGP ASN Selection**: Use private BGP ASN range (64512-65534) unless you own a public ASN
3. **Avoid AWS Reserved ASNs**: Do not use 7224, 9059, 10124, or 17493 as these are AWS-reserved
4. **Unique ASNs**: Assign unique BGP ASN values for each customer gateway unless they're part of the same routing domain
5. **Descriptive Naming**: Use names that identify location or purpose (e.g., "datacenter-us-east", "branch-london")
6. **Multiple Gateways for HA**: Create separate customer gateways for each redundant VPN device

### Security

1. **Certificate Authentication**: Use certificate-based authentication via `certificate_arn` for enhanced security
2. **Firewall Rules**: Ensure on-premises firewall allows UDP 500 (IKE), UDP 4500 (NAT-T), and IP Protocol 50 (ESP)
3. **Audit Logging**: Enable CloudTrail logging for all customer gateway API calls
4. **Principle of Least Privilege**: Limit on-premises network routes advertised to AWS

### Integration

1. **VPN Gateway Module**: Use terraform-aws-modules/vpn-gateway module to create VPN connections
2. **Transit Gateway**: Use Transit Gateway for scalable hub-and-spoke architectures with multiple VPCs
3. **Route Propagation**: Enable route propagation on VPC route tables to receive on-premises routes via BGP

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-customer-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/customer-gateway/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-customer-gateway/tree/master/examples
- **AWS Customer Gateway Documentation**: https://docs.aws.amazon.com/vpn/latest/s2svpn/your-cgw.html
- **AWS Site-to-Site VPN**: https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html
- **VPN Pricing**: https://aws.amazon.com/vpn/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Minimal Configuration**: Only `customer_gateways` map is required; all other variables have sensible defaults
2. **Map Structure**: Define `customer_gateways` as a map where keys are identifiers and values contain `bgp_asn` and `ip_address`
3. **BGP ASN**: Use values in private range (64512-65534) for standard deployments
4. **Public IP Requirement**: The `ip_address` must be the public-facing IP of the on-premises VPN device
5. **Integration Required**: Customer gateway alone does not establish connectivity; must be paired with VPN connection resources
6. **Use Outputs**: Reference `module.cgw.customer_gateway` for VPN connection module configurations using `for_each`
7. **No Submodules**: This is a simple standalone module with no nested submodules
8. **Version Pinning**: Use `version = "~> 3.1"` for stability
