# Terraform AWS Customer Gateway Module

## Module Information

- **Module Name**: `customer-gateway`
- **Source**: `terraform-aws-modules/customer-gateway/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-customer-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/customer-gateway/aws/latest
- **Latest Version**: 3.1.1
- **Purpose**: Creates one or more `aws_customer_gateway` resources representing the on-premises side of AWS Site-to-Site VPN connections
- **Service**: AWS Site-to-Site VPN - Customer Gateway
- **Category**: Networking, Hybrid Cloud, Security
- **Keywords**: customer-gateway, cgw, site-to-site-vpn, vpn, ipsec, bgp, hybrid-cloud, on-premises, vpn-tunnel, transit-gateway, virtual-private-gateway, datacenter-connectivity
- **Use For**: connecting on-premises data centers to AWS, hybrid cloud networking, branch office VPN connectivity, disaster recovery links, multi-region hybrid architectures, redundant on-premises VPN endpoints, Transit Gateway spoke connections, phased cloud migration connectivity

## Description

This module creates AWS Customer Gateway resources (`aws_customer_gateway`), which register the customer side of a Site-to-Site VPN connection with AWS — the public IP address, BGP Autonomous System Number (ASN), and optional device identity/certificate of the on-premises or third-party VPN appliance. It was extracted from the `terraform-aws-modules/vpc` module because Customer Gateways are frequently reused across multiple VPCs, VPN Gateways, and Transit Gateways rather than being tied to a single network.

The module is intentionally minimal: it manages a single resource type (`aws_customer_gateway`) via a `for_each` over a map of gateway definitions, with the connection `type` fixed to `ipsec.1` (the only type AWS currently supports). It does not create the VPN connection itself, a VPC, a Virtual Private Gateway, or a Transit Gateway — it only registers the remote endpoint(s) that a subsequent VPN connection resource (e.g. `terraform-aws-modules/vpn-gateway`) will connect to.

Because the module accepts a map of gateway definitions, it can create any number of Customer Gateways in one call — useful for multiple data centers, branch offices, or redundant on-premises devices terminating separate tunnels. Each entry supports BGP ASN and IP address (required for a usable gateway), plus optional `certificate_arn` (certificate-based authentication) and `device_name` (identifies the physical/virtual appliance), both added in v3.1.0. There are no submodules.

## Key Features

- **Multiple Gateways in One Call**: Map-based `customer_gateways` input creates any number of `aws_customer_gateway` resources via `for_each`
- **BGP Support**: Configure a BGP ASN per gateway for dynamic routing over the resulting VPN connection
- **Static Public IP Registration**: Records the Internet-routable IP address of the on-premises/third-party VPN device
- **Certificate-Based Authentication**: Optional `certificate_arn` for private-certificate authentication instead of pre-shared keys (v3.1.0+)
- **Device Identification**: Optional `device_name` to label the physical or virtual appliance (v3.1.0+)
- **Conditional Creation**: `create = false` disables all resources in the module without removing the `module` block (works around Terraform's lack of `count` on modules)
- **Automatic Naming**: Each gateway is tagged `Name = "<name>-<map-key>"`, merged with any user-supplied `tags`
- **Standalone/Composable**: No dependency on VPC, VPN Gateway, or Transit Gateway modules — designed to be composed with them

## Main Use Cases

1. **Hybrid Cloud Connectivity**: Register on-premises data center endpoints for VPN connections into AWS VPCs
2. **Disaster Recovery**: Establish persistent VPN endpoints for DR failover sites
3. **Branch Office Integration**: Register multiple branch office VPN devices centrally
4. **Multi-Region Hybrid Architectures**: Create Customer Gateways per region for global hybrid deployments
5. **Transit Gateway Spokes**: Register on-premises endpoints that terminate VPN connections onto a Transit Gateway hub
6. **Redundant VPN Endpoints**: Create paired gateways (same or different ASN) for tunnel-level high availability
7. **Migration Workflows**: Maintain on-premises connectivity endpoints during phased cloud migration
8. **Reusable Gateway Registry**: Share the same Customer Gateway across multiple VPN Gateway/Transit Gateway attachments without recreating it

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `customer_gateways` | `map(map(any))` | `{}` | Map of Customer Gateway definitions; keys are arbitrary identifiers, values may contain `bgp_asn`, `ip_address`, `certificate_arn`, `device_name` |
| `create` | `bool` | `true` | Whether to create the Customer Gateway resources (set `false` for conditional creation) |
| `name` | `string` | `""` | Name prefix used to build each gateway's `Name` tag (`"<name>-<map-key>"`) |
| `tags` | `map(string)` | `{}` | Tags applied to all created resources |

### `customer_gateways` entry attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `bgp_asn` | `number` | BGP Autonomous System Number of the on-premises device (use private range 64512-65534 unless you own a public ASN) |
| `ip_address` | `string` | Internet-routable (public) IP address of the on-premises VPN device |
| `certificate_arn` | `string` | ACM Private CA certificate ARN for certificate-based authentication (optional) |
| `device_name` | `string` | Identifier for the customer gateway device (optional) |

## Main Outputs

| Output | Description |
|--------|-------------|
| `ids` | List of IDs of the created Customer Gateway resources (indexable, e.g. `module.cgw.ids[0]`) |
| `customer_gateway` | Full map of `aws_customer_gateway` resource attributes, keyed by the same keys as `customer_gateways` (useful for `for_each` in downstream VPN modules) |

## Usage Examples

### Example 1: Single Customer Gateway

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

### Example 2: Multiple Customer Gateways for Redundancy

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

### Example 3: Complete VPN Setup with VPC and VPN Gateway Modules

```hcl
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

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "production-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]

  enable_vpn_gateway = true
}

# One VPN connection per Customer Gateway, using the module's map output
module "vpn_gateway" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  for_each = module.cgw.customer_gateway

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = each.value.id

  vpc_id                       = module.vpc.vpc_id
  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(module.vpc.private_route_table_ids)
}
```

### Example 4: Certificate-Based Authentication

```hcl
module "cgw" {
  source  = "terraform-aws-modules/customer-gateway/aws"
  version = "~> 3.1"

  name = "cert-auth-cgw"

  customer_gateways = {
    secure_gateway = {
      bgp_asn         = 65112
      ip_address      = "203.0.113.10"
      certificate_arn = "arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/abc123/certificate/def456"
      device_name     = "cisco-asa-primary"
    }
  }

  tags = {
    Environment = "production"
    Security    = "high"
  }
}
```

### Example 5: Conditional Creation

```hcl
module "cgw" {
  source  = "terraform-aws-modules/customer-gateway/aws"
  version = "~> 3.1"

  create = var.enable_vpn # module creates nothing when false

  name = "optional-cgw"

  customer_gateways = {
    primary = {
      bgp_asn    = 65112
      ip_address = "203.0.113.10"
    }
  }
}
```

## Best Practices

### Customer Gateway Configuration

1. **Use Static Public IPs**: Configure `ip_address` with a static, Internet-routable public IP to avoid VPN disruptions if the on-premises device's address changes.
2. **Prefer Private BGP ASNs**: Use the private ASN range 64512-65534 unless the organization owns a public ASN; avoid AWS-reserved ASNs (7224, 9059, 10124, 17493).
3. **Assign Unique ASNs Per Gateway**: Give each Customer Gateway a distinct ASN unless multiple gateways intentionally belong to the same BGP routing domain.
4. **Name Gateways by Location/Purpose**: Use descriptive map keys and `name` values (e.g. `datacenter-us-east`, `branch-london`) so `ids`/`customer_gateway` outputs are self-explanatory downstream.
5. **Create One Gateway Per Physical Device**: For redundant on-premises hardware, define a separate map entry per device rather than reusing one Customer Gateway for multiple tunnels.

### Security

1. **Prefer Certificate Authentication**: Set `certificate_arn` (ACM Private CA) instead of relying solely on pre-shared keys where the on-premises device supports it.
2. **Open Only Required Firewall Ports**: Ensure on-premises firewalls allow UDP 500 (IKE), UDP 4500 (NAT-T), and IP protocol 50 (ESP) to the AWS VPN endpoints.
3. **Audit Gateway Changes**: Enable CloudTrail logging for `CreateCustomerGateway`/`DeleteCustomerGateway` API calls.
4. **Limit Advertised Routes**: Advertise only the necessary on-premises CIDRs over BGP to minimize the blast radius of the VPN connection.

### Integration

1. **Pair with `vpn-gateway` Module**: Use `module.cgw.customer_gateway` (map) or `module.cgw.ids` (list) as the `customer_gateway_id` input to `terraform-aws-modules/vpn-gateway/aws`.
2. **Use Transit Gateway for Multi-VPC Hubs**: Attach VPN connections built on these Customer Gateways to a Transit Gateway instead of per-VPC Virtual Private Gateways when connecting many VPCs.
3. **Enable Route Propagation**: Ensure the downstream VPN connection propagates BGP routes to the relevant VPC route tables so on-premises routes are usable.
4. **Reuse Across Networks**: Because the module is decoupled from VPC/VPN Gateway modules, define Customer Gateways once and reference the same `customer_gateway` output when building VPN connections to multiple VPCs.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-customer-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/customer-gateway/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-customer-gateway/tree/master/examples
- **Related Module - VPN Gateway**: https://registry.terraform.io/modules/terraform-aws-modules/vpn-gateway/aws/latest
- **Related Module - VPC**: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest
- **Related Module - Transit Gateway**: https://registry.terraform.io/modules/terraform-aws-modules/transit-gateway/aws/latest
- **AWS Customer Gateway Documentation**: https://docs.aws.amazon.com/vpn/latest/s2svpn/your-cgw.html
- **AWS Site-to-Site VPN Overview**: https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html
- **`aws_customer_gateway` Resource Reference**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/customer_gateway
- **VPN Pricing**: https://aws.amazon.com/vpn/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Minimal Required Config**: Only `customer_gateways` needs meaningful values; `create`, `name`, and `tags` all have safe defaults.
2. **Map Structure**: Define `customer_gateways` as `{ <key> = { bgp_asn = <number>, ip_address = "<public-ip>" } }`; `certificate_arn` and `device_name` are optional per-entry.
3. **BGP ASN Range**: Default to the private range 64512-65534 unless the user specifies a public ASN.
4. **`ip_address` Must Be Public**: This is the Internet-routable IP of the on-premises/third-party device, not an AWS resource IP.
5. **Not a Complete VPN by Itself**: This module only registers the Customer Gateway; it must be paired with a VPN connection module/resource (e.g. `terraform-aws-modules/vpn-gateway`) plus a VPC or Transit Gateway to establish actual connectivity.
6. **Use `customer_gateway` Output for Composition**: When wiring to `vpn-gateway`, iterate with `for_each = module.cgw.customer_gateway` and reference `each.value.id`; use `ids[n]` only when a fixed positional reference is acceptable.
7. **No Submodules**: This is a single-resource module (`aws_customer_gateway.this`) with no submodules or nested components.
8. **Version Pinning**: Use `version = "~> 3.1"` for stability; `device_name` and `certificate_arn` require >= 3.1.0.
