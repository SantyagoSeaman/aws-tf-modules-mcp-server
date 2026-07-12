# Terraform AWS VPN Gateway Module

## Module Information

- **Module Name**: `vpn-gateway`
- **Module ID**: `terraform-aws-modules/vpn-gateway/aws`
- **Source**: `terraform-aws-modules/vpn-gateway/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-vpn-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/vpn-gateway/aws/latest
- **Latest Version**: 4.0.0
- **Compatibility**: Terraform >= 1.3, AWS provider >= 5.42
- **Purpose**: Creates an AWS Site-to-Site VPN connection (`aws_vpn_connection`) between an existing Virtual Private Gateway or Transit Gateway and an existing Customer Gateway, along with its attachment, route propagation, and static route resources
- **Service**: AWS Site-to-Site VPN (IPsec)
- **Category**: Networking, Hybrid Cloud Connectivity, Security
- **Keywords**: vpn, vpn-gateway, site-to-site-vpn, ipsec, customer-gateway, transit-gateway, bgp, vpn-tunnel, hybrid-cloud, vgw, static-routes, vpn-acceleration, dead-peer-detection, cloudwatch-logs, on-premises, ikev2
- **Use For**: hybrid cloud connectivity to on-premises data centers, extending corporate networks into a VPC, backup connectivity for AWS Direct Connect, disaster-recovery network paths, branch-office-to-AWS connectivity, Transit Gateway hub-and-spoke VPN architectures, compliance-mandated encrypted transit, multi-region hybrid networking, dev/test network access from on-premises

## Description

This module provisions a single AWS Site-to-Site VPN connection (`aws_vpn_connection`) linking an existing Virtual Private Gateway (VGW) or Transit Gateway (TGW) to an existing Customer Gateway (CGW). Depending on the mode, it also manages the supporting resources: VGW-to-VPC attachment (`aws_vpn_gateway_attachment`), route propagation to VPC subnet route tables (`aws_vpn_gateway_route_propagation`), static route entries (`aws_vpn_connection_route`), and — for Transit Gateway attachments — a tagging workaround (`aws_ec2_tag`) since the TGW attachment isn't tagged directly by the connection resource. The module deliberately does **not** create the VGW, TGW, or Customer Gateway; those are expected to already exist, typically provisioned via `terraform-aws-modules/vpc` (VGW), `terraform-aws-modules/transit-gateway`, or `terraform-aws-modules/customer-gateway` / a bare `aws_customer_gateway` resource.

AWS Site-to-Site VPN provides encrypted connectivity over the public internet using the IPsec protocol. Every connection consists of two redundant tunnels for high availability, and each tunnel independently negotiates IKE version (v1/v2), Phase 1/Phase 2 encryption and integrity algorithms, Diffie-Hellman groups, lifetimes, and Dead Peer Detection behavior. Routing can be static or dynamic via BGP, and Transit Gateway attachments additionally support IPv6 tunnel traffic and AWS VPN acceleration for improved throughput.

Architecturally, the module has no submodules and is a single flat set of resources, but it contains an important internal branch: it defines four near-identical `aws_vpn_connection` resources (`default`, `tunnel`, `preshared`, `tunnel_preshared`) and uses `count` to instantiate exactly one, chosen automatically based on whether `tunnel1_inside_cidr`/`tunnel2_inside_cidr` and/or `tunnel1_preshared_key`/`tunnel2_preshared_key` were supplied. This selection logic is a common source of configuration mistakes (see Notes for AI Agents) and should be understood before customizing tunnel parameters.

## Key Features

- **Dual Attachment Modes**: Connects to either a Virtual Private Gateway (`vpn_gateway_id`) or a Transit Gateway (`transit_gateway_id` with `connect_to_transit_gateway = true`)
- **Automatic Resource Variant Selection**: Internally picks between 4 `aws_vpn_connection` definitions based on which tunnel parameters (inside CIDR, preshared key) are set
- **Redundant Tunnels**: Every connection provisions two IPsec tunnels for automatic failover
- **Static or BGP Routing**: `vpn_connection_static_routes_only` toggles static routes vs. dynamic BGP-based routing
- **Route Propagation**: Automatic propagation of VGW routes into VPC subnet route tables (VGW mode only)
- **Static Route Management**: Creates `aws_vpn_connection_route` entries per destination CIDR when static routing is used (VGW mode only)
- **Full Per-Tunnel IKE/IPsec Tuning**: Independently configurable IKE version, Phase 1/Phase 2 encryption algorithms, integrity algorithms, Diffie-Hellman groups, and lifetimes for tunnel 1 and tunnel 2
- **Custom Tunnel Endpoints**: Optional custom `tunnel{1,2}_inside_cidr` and `tunnel{1,2}_preshared_key` instead of AWS-generated values
- **Dead Peer Detection Tuning**: Configurable DPD timeout and action (`clear`/`none`/`restart`) per tunnel
- **Rekey and Replay Controls**: Configurable rekey margin/fuzz percentage and IKE anti-replay window size per tunnel
- **Tunnel Startup Behavior**: Choose whether AWS (`start`) or the customer gateway device (`add`) initiates IKE negotiation
- **CloudWatch Tunnel Logging**: Per-tunnel `cloudwatch_log_options` for delivering VPN tunnel logs to CloudWatch Logs
- **VPN Acceleration**: Optional AWS Global Accelerator-backed acceleration (Transit Gateway attachments only)
- **IPv4 and IPv6 Tunnel Traffic**: `tunnel_inside_ip_version = "ipv6"` for IPv6 tunnels (Transit Gateway only)
- **Automatic TGW Attachment Tagging**: Works around a provider limitation by tagging the Transit Gateway VPN attachment via `aws_ec2_tag`
- **Conditional Creation**: `create_vpn_connection = false` skips creating the connection and all dependent resources
- **Sensitive Outputs**: Preshared keys and the customer gateway XML configuration are marked `sensitive` in outputs

## Main Use Cases

1. **Hybrid Cloud Connectivity**: Connect on-premises data centers to AWS VPCs over encrypted IPsec tunnels
2. **Corporate Network Extension**: Extend enterprise networks into AWS for seamless resource access
3. **Direct Connect Backup**: Provide redundant, lower-cost failover connectivity alongside AWS Direct Connect
4. **Disaster Recovery Links**: Establish backup network paths for DR sites and failover scenarios
5. **Transit Gateway Hub-and-Spoke**: Terminate multiple site VPNs onto a central Transit Gateway for multi-VPC connectivity
6. **Branch Office Connectivity**: Connect multiple remote offices to centralized AWS resources
7. **Compliance-Required Encryption**: Meet regulatory requirements for encrypted data transmission between sites
8. **Cloud Migration Support**: Provide interim or permanent network connectivity during phased cloud migrations
9. **IPv6 Hybrid Networking**: Extend IPv6 on-premises networks into AWS via Transit Gateway VPN attachments
10. **Development/Test Network Access**: Give corporate users secure access to AWS dev/test environments

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `customer_gateway_id` | `string` | required | ID of the Customer Gateway; required even when `create_vpn_connection = false` |
| `vpn_gateway_id` | `string` | `null` | ID of the Virtual Private Gateway (VGW mode) |
| `transit_gateway_id` | `string` | `null` | ID of the Transit Gateway (TGW mode, needs `connect_to_transit_gateway = true`) |
| `vpc_id` | `string` | `null` | VPC ID that owns the VGW; used only for `aws_vpn_gateway_attachment` |
| `create_vpn_connection` | `bool` | `true` | Set `false` to skip creating the VPN connection and all dependent resources |
| `create_vpn_gateway_attachment` | `bool` | `true` | Attach the VGW to `vpc_id`; set `false` in TGW mode or if the VPC module already attaches it |
| `connect_to_transit_gateway` | `bool` | `false` | Attach the connection to a Transit Gateway instead of a VGW |
| `vpn_connection_static_routes_only` | `bool` | `false` | Use static routing instead of BGP; required for devices that don't support BGP |
| `vpn_connection_static_routes_destinations` | `list(string)` | `[]` | Destination CIDRs for static routes (VGW mode only; ignored with Transit Gateway) |
| `vpn_connection_enable_acceleration` | `bool` | `null` | Enable AWS VPN acceleration; Transit Gateway attachments only |
| `vpc_subnet_route_table_ids` / `vpc_subnet_route_table_count` | `list(string)` / `number` | `[]` / `0` | Route tables that receive propagated VGW routes (VGW mode only); count works around a Terraform `count`-on-computed-value limitation |
| `tunnel_inside_ip_version` | `string` | `"ipv4"` | `"ipv4"` or `"ipv6"`; IPv6 requires Transit Gateway |
| `local_ipv4_network_cidr` / `remote_ipv4_network_cidr` | `string` | `null` | Customer-gateway-side / AWS-side IPv4 CIDR; AWS defaults to `0.0.0.0/0` when null |
| `local_ipv6_network_cidr` / `remote_ipv6_network_cidr` | `string` | `null` | IPv6 equivalents of the above |
| `tunnel1_inside_cidr`, `tunnel2_inside_cidr` | `string` | `""` | Custom `/30` tunnel-inside CIDR per tunnel — must set **both** or neither |
| `tunnel1_preshared_key`, `tunnel2_preshared_key` | `string` (sensitive) | `""` | Custom preshared key per tunnel — must set **both** or neither |
| `tunnel1_ike_versions`, `tunnel2_ike_versions` | `list(string)` | `null` | `ikev1` \| `ikev2` |
| `tunnel{1,2}_phase1_encryption_algorithms`, `tunnel{1,2}_phase2_encryption_algorithms` | `list(string)` | `null` | `AES128` \| `AES256` \| `AES128-GCM-16` \| `AES256-GCM-16` |
| `tunnel{1,2}_phase1_integrity_algorithms`, `tunnel{1,2}_phase2_integrity_algorithms` | `list(string)` | `null` | `SHA1` \| `SHA2-256` \| `SHA2-384` \| `SHA2-512` |
| `tunnel{1,2}_phase1_dh_group_numbers`, `tunnel{1,2}_phase2_dh_group_numbers` | `list(number)` | `null` | Permitted Diffie-Hellman group numbers per phase |
| `tunnel{1,2}_phase1_lifetime_seconds` | `number` | `null` | AWS default 28800s; valid range 900-28800 |
| `tunnel{1,2}_phase2_lifetime_seconds` | `number` | `null` | AWS default 3600s; valid range 900-3600 |
| `tunnel1_dpd_timeout_seconds`, `tunnel2_dpd_timeout_seconds` | `number` | `null` | AWS default 30s; **not applied when only preshared keys are set** (see Notes for AI Agents) |
| `tunnel1_dpd_timeout_action`, `tunnel2_dpd_timeout_action` | `string` | `null` | AWS default `clear`; `clear` \| `none` \| `restart` |
| `tunnel{1,2}_startup_action` | `string` | `null` | AWS default `add` (CGW initiates); `start` makes AWS initiate IKE negotiation |
| `tunnel{1,2}_rekey_margin_time_seconds`, `tunnel{1,2}_rekey_fuzz_percentage` | `number` | `null` | IKE rekey timing controls |
| `tunnel{1,2}_replay_window_size` | `number` | `null` | AWS default 1024; valid range 64-2048 |
| `tunnel{1,2}_enable_tunnel_lifecycle_control` | `bool` | `null` | Manual tunnel endpoint lifecycle control |
| `tunnel1_log_options`, `tunnel2_log_options` | `any` | `{}` | CloudWatch Logs delivery: `{ cloudwatch_log_options = { log_enabled, log_group_arn, log_output_format } }` |
| `tags` | `map(string)` | `{}` | Tags applied to the VPN Connection (and the TGW attachment, via `aws_ec2_tag`) |

## Main Outputs

| Output | Description |
|--------|-------------|
| `vpn_connection_id` | ID of the created VPN Connection (empty string if `create_vpn_connection = false`) |
| `vpn_connection_tunnel1_address` / `vpn_connection_tunnel2_address` | Public IP address of tunnel 1 / tunnel 2 |
| `vpn_connection_tunnel1_cgw_inside_address` / `vpn_connection_tunnel2_cgw_inside_address` | RFC 6890 link-local address of tunnel 1 / 2 on the Customer Gateway side |
| `vpn_connection_tunnel1_vgw_inside_address` / `vpn_connection_tunnel2_vgw_inside_address` | RFC 6890 link-local address of tunnel 1 / 2 on the VPN Gateway side |
| `vpn_connection_transit_gateway_attachment_id` | Transit Gateway attachment ID generated for this connection |
| `vpn_connection_customer_gateway_configuration` | Customer gateway XML configuration for the on-premises device (sensitive) |
| `tunnel1_preshared_key` / `tunnel2_preshared_key` | Effective preshared key for each tunnel — AWS-generated unless overridden (sensitive) |

## Usage Examples

### Example 1: Basic VGW Connection with BGP

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "vpn-enabled-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_vpn_gateway = true

  tags = { Environment = "production" }
}

resource "aws_customer_gateway" "main" {
  bgp_asn    = 65000
  ip_address = "203.0.113.12"
  type       = "ipsec.1"

  tags = { Name = "main-customer-gateway" }
}

module "vpn_gateway" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = aws_customer_gateway.main.id

  vpc_id                       = module.vpc.vpc_id
  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(module.vpc.private_route_table_ids)

  local_ipv4_network_cidr  = "0.0.0.0/0"
  remote_ipv4_network_cidr = "192.168.0.0/16"

  tags = {
    Name        = "main-vpn-connection"
    Environment = "production"
  }
}
```

### Example 2: VPN Connection with Static Routes (No BGP)

```hcl
resource "aws_customer_gateway" "office" {
  bgp_asn    = 65000
  ip_address = "198.51.100.25"
  type       = "ipsec.1"

  tags = { Name = "office-customer-gateway" }
}

module "vpn_gateway_static" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = aws_customer_gateway.office.id
  vpc_id              = module.vpc.vpc_id

  # Use static routing instead of BGP (required for CGW devices without BGP support)
  vpn_connection_static_routes_only         = true
  vpn_connection_static_routes_destinations = ["192.168.10.0/24"]

  local_ipv4_network_cidr  = "10.0.0.0/16"
  remote_ipv4_network_cidr = "192.168.10.0/24"

  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(module.vpc.private_route_table_ids)

  tags = { Name = "office-vpn-static", Type = "static-routes" }
}
```

### Example 3: Transit Gateway VPN with Acceleration and IPv6 Tunnels

```hcl
resource "aws_ec2_transit_gateway" "main" {
  description                     = "Main Transit Gateway"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"

  tags = { Name = "main-tgw" }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "vpc" {
  subnet_ids         = module.vpc.private_subnets
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id              = module.vpc.vpc_id
}

resource "aws_customer_gateway" "site_a" {
  bgp_asn    = 65001
  ip_address = "2001:db8::1"
  type       = "ipsec.1"

  tags = { Name = "site-a-cgw" }
}

module "vpn_tgw" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  connect_to_transit_gateway    = true
  create_vpn_gateway_attachment = false # attachment is TGW-managed, not VGW-managed
  transit_gateway_id            = aws_ec2_transit_gateway.main.id
  customer_gateway_id           = aws_customer_gateway.site_a.id

  vpn_connection_enable_acceleration = true # Transit Gateway attachments only

  tunnel_inside_ip_version = "ipv6" # IPv6 tunnels require Transit Gateway
  local_ipv6_network_cidr  = "::/0"
  remote_ipv6_network_cidr = "2001:db8:1234::/48"

  tags = {
    Name        = "tgw-vpn-site-a"
    Environment = "production"
  }
}
```

### Example 4: Custom Tunnel Security Parameters with CloudWatch Logging

```hcl
resource "aws_cloudwatch_log_group" "tunnel1" {
  name              = "/aws/vpn/tunnel1"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "tunnel2" {
  name              = "/aws/vpn/tunnel2"
  retention_in_days = 30
}

resource "aws_customer_gateway" "datacenter" {
  bgp_asn    = 65100
  ip_address = "198.51.100.50"
  type       = "ipsec.1"

  tags = { Name = "datacenter-cgw" }
}

module "vpn_custom_tunnels" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = aws_customer_gateway.datacenter.id
  vpc_id              = module.vpc.vpc_id

  # Custom tunnel-inside CIDRs and preshared keys - both tunnels MUST be set together
  tunnel1_inside_cidr    = "169.254.10.0/30"
  tunnel2_inside_cidr    = "169.254.10.4/30"
  tunnel1_preshared_key  = var.tunnel1_psk # supply via a secrets-manager-backed variable, never hardcode
  tunnel2_preshared_key  = var.tunnel2_psk

  tunnel1_ike_versions = ["ikev2"]
  tunnel2_ike_versions = ["ikev2"]

  tunnel1_phase1_encryption_algorithms = ["AES256"]
  tunnel2_phase1_encryption_algorithms = ["AES256"]
  tunnel1_phase1_integrity_algorithms  = ["SHA2-256"]
  tunnel2_phase1_integrity_algorithms  = ["SHA2-256"]

  tunnel1_phase2_encryption_algorithms = ["AES256"]
  tunnel2_phase2_encryption_algorithms = ["AES256"]
  tunnel1_phase2_integrity_algorithms  = ["SHA2-256"]
  tunnel2_phase2_integrity_algorithms  = ["SHA2-256"]

  tunnel1_dpd_timeout_action = "restart"
  tunnel2_dpd_timeout_action = "restart"

  tunnel1_log_options = {
    cloudwatch_log_options = {
      log_enabled       = true
      log_group_arn     = aws_cloudwatch_log_group.tunnel1.arn
      log_output_format = "json"
    }
  }
  tunnel2_log_options = {
    cloudwatch_log_options = {
      log_enabled       = true
      log_group_arn     = aws_cloudwatch_log_group.tunnel2.arn
      log_output_format = "json"
    }
  }

  local_ipv4_network_cidr  = "10.0.0.0/16"
  remote_ipv4_network_cidr = "172.16.0.0/12"

  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(module.vpc.private_route_table_ids)

  tags = { Name = "datacenter-vpn-custom", Environment = "production" }
}
```

## Best Practices

### Security and Encryption

1. **Generate Strong Preshared Keys**: Use a cryptographically secure generator for `tunnel{1,2}_preshared_key` (32+ characters) rather than hand-picked strings.
2. **Store Secrets Externally**: Pass preshared keys in via `var.` references backed by AWS Secrets Manager or a Terraform-native secret source — never hardcode them in `.tf` files.
3. **Prefer IKEv2**: Set `tunnel{1,2}_ike_versions = ["ikev2"]` for both tunnels for stronger negotiation and faster rekeys.
4. **Use AES-256 and SHA2-256+**: Set `tunnel{1,2}_phase{1,2}_encryption_algorithms = ["AES256"]` and integrity algorithms to `SHA2-256`/`SHA2-384`/`SHA2-512` instead of the legacy `SHA1`.
5. **Rotate Preshared Keys Periodically**: Establish a rotation schedule (e.g., every 90-180 days) and apply it through the secrets backend, not manual edits.
6. **Enable CloudWatch Tunnel Logging**: Configure `tunnel{1,2}_log_options` to capture negotiation and status events for security monitoring.

### High Availability and Routing

1. **Prefer BGP over Static Routes**: Leave `vpn_connection_static_routes_only = false` whenever the customer gateway device supports BGP, for automatic failover and dynamic path selection.
2. **Configure Both Tunnels on the CGW Device**: AWS always provisions two tunnels; configure both on the on-premises device to get tunnel-level redundancy, not just connection-level.
3. **Deploy a Second VPN Connection for Critical Links**: Create a second `vpn-gateway` module instance to a different customer gateway/device for full redundancy beyond AWS's built-in dual tunnels.
4. **Tune Dead Peer Detection**: Set `tunnel{1,2}_dpd_timeout_action = "restart"` for faster automatic recovery from a stalled tunnel (remember this is silently ignored in the preshared-key-only variant — see Notes for AI Agents).
5. **Use Transit Gateway for Multi-VPC Fan-Out**: Terminate VPNs on a Transit Gateway instead of multiple per-VPC VGWs when connecting many VPCs to the same on-premises sites.

### Network Configuration

1. **Avoid Overlapping CIDRs**: Ensure `local_*_network_cidr` and `remote_*_network_cidr` (or the on-prem/AWS-side networks they represent) never overlap.
2. **Set Both Tunnel Parameters Together**: Always set `tunnel1_inside_cidr`/`tunnel2_inside_cidr` and `tunnel1_preshared_key`/`tunnel2_preshared_key` in matching pairs — the module silently switches `aws_vpn_connection` resource variants if only one of a pair is set (see Notes for AI Agents).
3. **Use RFC 6890 `/30` Tunnel CIDRs**: When customizing `tunnel{1,2}_inside_cidr`, use link-local `169.254.x.x/30` blocks and keep them unique across all VPN connections in the account.
4. **Choose Private BGP ASNs**: Use the 64512-65534 private ASN range for customer gateways unless a public ASN is owned.
5. **Route Propagation Is VGW-Only**: `vpc_subnet_route_table_ids`/`vpc_subnet_route_table_count` and static routes only take effect in VGW mode; in Transit Gateway mode, manage routing through the TGW route tables instead.

### Performance and Cost

1. **Enable Acceleration Selectively**: `vpn_connection_enable_acceleration = true` improves throughput/latency for Transit Gateway attachments but adds cost — enable only where justified.
2. **Watch the Per-Tunnel Bandwidth Ceiling**: Each tunnel is limited to roughly 1.25 Gbps; plan multiple connections or Direct Connect for higher sustained throughput.
3. **Consolidate via Transit Gateway**: Reduce the number of discrete VPN connections (and their hourly charges) by hubbing through one Transit Gateway instead of per-VPC VGWs.
4. **Clean Up Idle Connections**: Remove unused `vpn-gateway` module instances (`create_vpn_connection = false` or delete) to stop the hourly connection charge.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-vpn-gateway
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-vpn-gateway/tree/master/examples
- **Related Module - Customer Gateway**: https://registry.terraform.io/modules/terraform-aws-modules/customer-gateway/aws/latest
- **Related Module - VPC** (creates the VGW via `enable_vpn_gateway`): https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest
- **Related Module - Transit Gateway**: https://registry.terraform.io/modules/terraform-aws-modules/transit-gateway/aws/latest
- **AWS Site-to-Site VPN Documentation**: https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html
- **VPN Redundancy and Failover**: https://docs.aws.amazon.com/vpn/latest/s2svpn/vpn-redundant-connection.html
- **Accelerated Site-to-Site VPN**: https://docs.aws.amazon.com/vpn/latest/s2svpn/accelerated-vpn.html
- **VPN CloudWatch Metrics**: https://docs.aws.amazon.com/vpn/latest/s2svpn/monitoring-cloudwatch-vpn.html
- **`aws_vpn_connection` Resource Reference**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpn_connection
- **VPN Pricing**: https://aws.amazon.com/vpn/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **No Submodules**: This is a single flat module (no `submodules/` directory) — do not reference `//modules/...` paths.
2. **Requires Pre-existing Gateways**: The module never creates the VGW, TGW, or Customer Gateway. Create the VGW via `terraform-aws-modules/vpc` (`enable_vpn_gateway = true`) or a TGW via `terraform-aws-modules/transit-gateway`/`aws_ec2_transit_gateway`, and the Customer Gateway via `terraform-aws-modules/customer-gateway` or `aws_customer_gateway`, before calling this module.
3. **`customer_gateway_id` Is Always Required**: It has no default and must be supplied even when `create_vpn_connection = false`.
4. **Resource-Variant Selection Gotcha**: Internally the module chooses between 4 `aws_vpn_connection` resources based on whether `tunnel{1,2}_inside_cidr` and `tunnel{1,2}_preshared_key` are set. Always set both members of each pair together (both CIDRs, or neither; both keys, or neither) — setting only one half is a no-op for that parameter because a different resource variant gets created instead.
5. **Known Quirk — `preshared`-only Variant Drops DPD Timeout**: When only `tunnel{1,2}_preshared_key` are set (no custom inside CIDRs), `tunnel1_dpd_timeout_seconds`/`tunnel2_dpd_timeout_seconds` are not wired into the underlying resource in module v4.0.0 and will be silently ignored; `tunnel{1,2}_dpd_timeout_action` still works. Set custom inside CIDRs too if precise DPD timeout control is required.
6. **VGW Mode vs. TGW Mode Wiring**: VGW mode needs `vpn_gateway_id` + `vpc_id` (+ `vpc_subnet_route_table_ids`/`_count` for route propagation). TGW mode needs `connect_to_transit_gateway = true` + `transit_gateway_id`, typically with `create_vpn_gateway_attachment = false`; route propagation must then be handled via the Transit Gateway's own route tables, not this module.
7. **Route Propagation and Static Routes Are VGW-Only**: `vpc_subnet_route_table_ids`, `vpc_subnet_route_table_count`, and `vpn_connection_static_routes_destinations` have no effect when `connect_to_transit_gateway = true`.
8. **IPv6 and Acceleration Require Transit Gateway**: `tunnel_inside_ip_version = "ipv6"` and `vpn_connection_enable_acceleration = true` are only supported on Transit Gateway attachments, not VGW attachments.
9. **Never Hardcode Preshared Keys**: Source `tunnel{1,2}_preshared_key` from a secrets manager or sensitive input variable; the module already marks the corresponding outputs `sensitive`.
10. **Prefer BGP and IKEv2/AES256/SHA2-256+**: Default to dynamic BGP routing and modern IKEv2 with AES-256/SHA2-256 (or higher) algorithms for production deployments unless the customer gateway device dictates otherwise.
11. **Tag for Cost Allocation**: `tags` propagates to the VPN connection and, for TGW mode, to the TGW attachment via an `aws_ec2_tag` workaround — always populate it for cost tracking.
12. **Version Pinning**: Use `version = "~> 4.0"`; v4.0.0 is a breaking change from v3.x (added acceleration support and raised the minimum Terraform/AWS provider versions).
