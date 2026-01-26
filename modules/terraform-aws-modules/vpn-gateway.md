# Terraform AWS VPN Gateway Module

## Module Information

- **Module Name**: `vpn-gateway`
- **Source**: `terraform-aws-modules/vpn-gateway/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-vpn-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/vpn-gateway/aws/latest
- **Latest Version**: 4.0.0
- **Purpose**: Terraform module that creates AWS Site-to-Site VPN connections between Virtual Private Gateways or Transit Gateways and Customer Gateways
- **Service**: AWS Site-to-Site VPN (Virtual Private Network)
- **Category**: Networking, Hybrid Cloud Connectivity, Security
- **Keywords**: vpn-gateway, site-to-site-vpn, customer-gateway, transit-gateway, ipsec, vpn-connection, bgp, static-routes, hybrid-cloud, on-premises, encryption, route-propagation, high-availability, vpn-tunnel
- **Use For**: Hybrid cloud connectivity, connecting on-premises data centers to AWS, secure site-to-site network connections, extending corporate networks to VPC, disaster recovery connectivity, multi-cloud networking, branch office connectivity to AWS, secure remote access infrastructure, network migration to cloud, dev/test environment access from corporate networks, compliance-required encrypted connectivity, backup connectivity for Direct Connect

## Description

This Terraform module creates and manages AWS Site-to-Site VPN connections, establishing secure IPsec tunnels between AWS infrastructure and on-premises networks or remote sites. The module handles VPN connection creation, tunnel configuration, route propagation, and gateway attachments for both Virtual Private Gateway (VGW) and Transit Gateway scenarios. It does not create the VPN Gateway or Customer Gateway resources themselves, but focuses on establishing and configuring the VPN connection between existing gateways with comprehensive tunnel parameter customization.

AWS Site-to-Site VPN provides encrypted network connectivity between AWS VPCs and remote networks using industry-standard IPsec protocol. Each VPN connection consists of two redundant tunnels for high availability, supporting both static routing and dynamic Border Gateway Protocol (BGP) routing. The service enables organizations to extend their on-premises infrastructure into AWS securely, implement hybrid cloud architectures, and maintain encrypted communication channels without requiring dedicated physical connections like AWS Direct Connect.

The module offers extensive configuration flexibility including custom tunnel inside CIDR ranges, preshared keys, IKE versions, encryption and integrity algorithms for both Phase 1 and Phase 2, Dead Peer Detection (DPD) settings, and optional acceleration for improved performance. It supports integration with VPC route tables for automatic route propagation, CloudWatch logging for tunnel activity monitoring, and both IPv4 and IPv6 network configurations. The module works seamlessly with the terraform-aws-modules/vpc module and supports modern Transit Gateway architectures for connecting multiple VPCs and on-premises networks through a central hub.

## Key Features

- **VPN Connection Creation**: Establishes Site-to-Site VPN connections between AWS gateways and Customer Gateways
- **Dual Gateway Support**: Compatible with both Virtual Private Gateways (VPC-attached) and Transit Gateways (multi-VPC hub)
- **Redundant Tunnel Configuration**: Creates two VPN tunnels per connection for high availability and automatic failover
- **Static and Dynamic Routing**: Supports static route configuration and BGP-based dynamic routing
- **Custom Tunnel Parameters**: Full control over tunnel inside CIDR ranges for both tunnels
- **Encryption Configuration**: Customizable Phase 1 and Phase 2 encryption algorithms (AES128, AES256, AES128-GCM-16, AES256-GCM-16)
- **Integrity Algorithms**: Configurable Phase 1 and Phase 2 integrity algorithms (SHA1, SHA2-256, SHA2-384, SHA2-512)
- **IKE Version Selection**: Support for IKEv1 and IKEv2 protocols
- **Preshared Key Management**: Custom preshared keys for tunnel authentication
- **DPD Configuration**: Dead Peer Detection timeout and action customization
- **Lifetime Settings**: Configurable Phase 1 and Phase 2 lifetime values
- **Route Propagation**: Automatic route propagation to VPC subnet route tables
- **VPN Connection Acceleration**: Optional acceleration for improved throughput and reduced latency
- **CloudWatch Logging**: Tunnel activity logging to CloudWatch Logs with customizable formats
- **IPv4 and IPv6 Support**: Configuration for both IPv4 and IPv6 network CIDRs (local and remote)
- **NAT Traversal**: Built-in support for NAT traversal (NAT-T)
- **Gateway Attachment Control**: Optional VPN Gateway attachment to VPC
- **Transit Gateway Integration**: Seamless connection to Transit Gateway for multi-VPC architectures
- **Flexible Tagging**: Comprehensive tagging support for VPN connection resources
- **Conditional Creation**: Control VPN connection creation with boolean flags
- **Startup Action**: Configurable tunnel startup behavior (add/start)
- **Rekey Margin and Fuzz**: Advanced tunnel rekey timing configuration
- **Tunnel Lifecycle Control**: Manage tunnel endpoint startup and shutdown behavior

## Main Use Cases

1. **Hybrid Cloud Connectivity**: Connect on-premises data centers to AWS VPCs for hybrid infrastructure
2. **Corporate Network Extension**: Extend enterprise networks into AWS for seamless resource access
3. **Disaster Recovery Links**: Establish backup connectivity for DR sites and failover scenarios
4. **Multi-Site Connectivity**: Connect multiple remote offices to centralized AWS resources
5. **Direct Connect Backup**: Provide redundant connectivity as backup for AWS Direct Connect
6. **Secure Remote Access**: Enable secure access to AWS resources from corporate headquarters
7. **Cloud Migration Support**: Facilitate network connectivity during phased cloud migrations
8. **Development Environment Access**: Connect development teams to AWS dev/test environments
9. **Compliance and Encryption**: Meet regulatory requirements for encrypted data transmission
10. **Multi-Cloud Networking**: Bridge AWS infrastructure with other cloud providers or data centers

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_vpn_connection` | `bool` | `true` | Set to false to prevent creation of VPN connection |
| `vpn_gateway_id` | `string` | `null` | ID of the VPN Gateway |
| `transit_gateway_id` | `string` | `null` | ID of the Transit Gateway |
| `customer_gateway_id` | `string` | required | ID of the Customer Gateway |
| `vpc_id` | `string` | `null` | ID of the VPC where VPN Gateway lives |
| `connect_to_transit_gateway` | `bool` | `false` | Attach VPN connection to Transit Gateway instead of VGW |
| `create_vpn_gateway_attachment` | `bool` | `true` | Attach VPN Gateway to VPC |
| `vpn_connection_static_routes_only` | `bool` | `false` | Use static routes exclusively (no BGP) |
| `vpn_connection_static_routes_destinations` | `list(string)` | `[]` | CIDR blocks for static route destinations |
| `vpn_connection_enable_acceleration` | `bool` | `null` | Enable acceleration for VPN connection (TGW only) |
| `vpc_subnet_route_table_ids` | `list(string)` | `[]` | VPC subnet route table IDs for route propagation |
| `vpc_subnet_route_table_count` | `number` | `0` | Number of subnet route table IDs |
| `tunnel_inside_ip_version` | `string` | `"ipv4"` | IP version for tunnel inside addresses (ipv4 or ipv6) |
| `local_ipv4_network_cidr` | `string` | `"0.0.0.0/0"` | Local IPv4 network CIDR |
| `remote_ipv4_network_cidr` | `string` | `"0.0.0.0/0"` | Remote IPv4 network CIDR |
| `local_ipv6_network_cidr` | `string` | `null` | Local IPv6 network CIDR |
| `remote_ipv6_network_cidr` | `string` | `null` | Remote IPv6 network CIDR |
| `tunnel1_inside_cidr` | `string` | `null` | Inside CIDR for tunnel 1 |
| `tunnel2_inside_cidr` | `string` | `null` | Inside CIDR for tunnel 2 |
| `tunnel1_preshared_key` | `string` | `null` | Preshared key for tunnel 1 |
| `tunnel2_preshared_key` | `string` | `null` | Preshared key for tunnel 2 |
| `tunnel1_dpd_timeout_action` | `string` | `null` | DPD timeout action for tunnel 1 (clear, none, restart) |
| `tunnel2_dpd_timeout_action` | `string` | `null` | DPD timeout action for tunnel 2 (clear, none, restart) |
| `tunnel1_dpd_timeout_seconds` | `number` | `null` | DPD timeout in seconds for tunnel 1 |
| `tunnel2_dpd_timeout_seconds` | `number` | `null` | DPD timeout in seconds for tunnel 2 |
| `tunnel1_ike_versions` | `list(string)` | `null` | IKE versions for tunnel 1 (ikev1, ikev2) |
| `tunnel2_ike_versions` | `list(string)` | `null` | IKE versions for tunnel 2 (ikev1, ikev2) |
| `tunnel1_phase1_encryption_algorithms` | `list(string)` | `null` | Phase 1 encryption algorithms for tunnel 1 |
| `tunnel2_phase1_encryption_algorithms` | `list(string)` | `null` | Phase 1 encryption algorithms for tunnel 2 |
| `tunnel1_phase1_integrity_algorithms` | `list(string)` | `null` | Phase 1 integrity algorithms for tunnel 1 |
| `tunnel2_phase1_integrity_algorithms` | `list(string)` | `null` | Phase 1 integrity algorithms for tunnel 2 |
| `tunnel1_phase2_encryption_algorithms` | `list(string)` | `null` | Phase 2 encryption algorithms for tunnel 1 |
| `tunnel2_phase2_encryption_algorithms` | `list(string)` | `null` | Phase 2 encryption algorithms for tunnel 2 |
| `tunnel1_phase2_integrity_algorithms` | `list(string)` | `null` | Phase 2 integrity algorithms for tunnel 1 |
| `tunnel2_phase2_integrity_algorithms` | `list(string)` | `null` | Phase 2 integrity algorithms for tunnel 2 |
| `tunnel1_log_options` | `map(any)` | `{}` | CloudWatch log options for tunnel 1 |
| `tunnel2_log_options` | `map(any)` | `{}` | CloudWatch log options for tunnel 2 |
| `tunnel1_startup_action` | `string` | `null` | Tunnel 1 startup action (add, start) |
| `tunnel2_startup_action` | `string` | `null` | Tunnel 2 startup action (add, start) |
| `tunnel1_enable_tunnel_lifecycle_control` | `bool` | `null` | Enable lifecycle control for tunnel 1 |
| `tunnel2_enable_tunnel_lifecycle_control` | `bool` | `null` | Enable lifecycle control for tunnel 2 |
| `tags` | `map(string)` | `{}` | Tags for VPN Connection resource |

## Main Outputs

| Output | Description |
|--------|-------------|
| `vpn_connection_id` | VPN Connection ID |
| `vpn_connection_tunnel1_address` | Public IP address of first VPN tunnel |
| `vpn_connection_tunnel1_cgw_inside_address` | RFC 6890 link-local address of first tunnel (Customer Gateway side) |
| `vpn_connection_tunnel1_vgw_inside_address` | RFC 6890 link-local address of first tunnel (VPN Gateway side) |
| `vpn_connection_tunnel2_address` | Public IP address of second VPN tunnel |
| `vpn_connection_tunnel2_cgw_inside_address` | RFC 6890 link-local address of second tunnel (Customer Gateway side) |
| `vpn_connection_tunnel2_vgw_inside_address` | RFC 6890 link-local address of second tunnel (VPN Gateway side) |
| `vpn_connection_transit_gateway_attachment_id` | Transit Gateway attachment ID (sensitive) |
| `vpn_connection_customer_gateway_configuration` | Customer gateway XML configuration for on-premises device (sensitive) |
| `tunnel1_preshared_key` | Pre-shared key for tunnel 1 (sensitive) |
| `tunnel2_preshared_key` | Pre-shared key for tunnel 2 (sensitive) |

## Usage Examples

### Example 1: Basic VPN Gateway Connection with BGP

```hcl
# Create Customer Gateway
resource "aws_customer_gateway" "main" {
  bgp_asn    = 65000
  ip_address = "203.0.113.12"
  type       = "ipsec.1"

  tags = {
    Name = "main-customer-gateway"
  }
}

# Create VPC with VPN Gateway
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "vpn-enabled-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_vpn_gateway = true

  tags = {
    Environment = "production"
  }
}

# Create VPN Connection
module "vpn_gateway" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = aws_customer_gateway.main.id

  vpc_id                       = module.vpc.vpc_id
  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(module.vpc.private_subnets)

  # Network configuration
  local_ipv4_network_cidr  = "0.0.0.0/0"
  remote_ipv4_network_cidr = "192.168.0.0/16"

  tags = {
    Name        = "main-vpn-connection"
    Environment = "production"
  }
}
```

### Example 2: VPN Connection with Static Routes

```hcl
resource "aws_customer_gateway" "office" {
  bgp_asn    = 65000
  ip_address = "198.51.100.25"
  type       = "ipsec.1"

  tags = {
    Name = "office-customer-gateway"
  }
}

module "vpn_gateway_static" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = aws_customer_gateway.office.id

  vpc_id = module.vpc.vpc_id

  # Use static routing instead of BGP
  vpn_connection_static_routes_only = true

  # Network CIDRs
  local_ipv4_network_cidr  = "10.0.0.0/16"
  remote_ipv4_network_cidr = "192.168.10.0/24"

  # Route propagation
  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(module.vpc.private_subnets)

  tags = {
    Name = "office-vpn-static"
    Type = "static-routes"
  }
}
```

### Example 3: Transit Gateway VPN Connection

```hcl
# Create Transit Gateway
resource "aws_ec2_transit_gateway" "main" {
  description = "Main Transit Gateway"

  default_route_table_association = "enable"
  default_route_table_propagation = "enable"

  tags = {
    Name = "main-tgw"
  }
}

# Attach VPC to Transit Gateway
resource "aws_ec2_transit_gateway_vpc_attachment" "vpc" {
  subnet_ids         = module.vpc.private_subnets
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = module.vpc.vpc_id

  tags = {
    Name = "vpc-attachment"
  }
}

# Customer Gateways
resource "aws_customer_gateway" "site_a" {
  bgp_asn    = 65001
  ip_address = "203.0.113.100"
  type       = "ipsec.1"

  tags = {
    Name = "site-a-cgw"
  }
}

# VPN Connection to Transit Gateway
module "vpn_tgw" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  connect_to_transit_gateway = true
  transit_gateway_id         = aws_ec2_transit_gateway.main.id
  customer_gateway_id        = aws_customer_gateway.site_a.id

  # Network configuration
  local_ipv4_network_cidr  = "0.0.0.0/0"
  remote_ipv4_network_cidr = "10.50.0.0/16"

  tags = {
    Name        = "tgw-vpn-site-a"
    Environment = "production"
  }
}
```

### Example 4: VPN with Custom Tunnel Configuration

```hcl
resource "aws_customer_gateway" "datacenter" {
  bgp_asn    = 65100
  ip_address = "198.51.100.50"
  type       = "ipsec.1"

  tags = {
    Name = "datacenter-cgw"
  }
}

module "vpn_custom_tunnels" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = aws_customer_gateway.datacenter.id
  vpc_id              = module.vpc.vpc_id

  # Custom tunnel inside CIDRs
  tunnel1_inside_cidr = "169.254.10.0/30"
  tunnel2_inside_cidr = "169.254.10.4/30"

  # Preshared keys
  tunnel1_preshared_key = "supersecurekey123456789012345678"
  tunnel2_preshared_key = "anothersecurekey12345678901234567"

  # IKE configuration
  tunnel1_ike_versions = ["ikev2"]
  tunnel2_ike_versions = ["ikev2"]

  # Phase 1 encryption and integrity
  tunnel1_phase1_encryption_algorithms = ["AES256"]
  tunnel2_phase1_encryption_algorithms = ["AES256"]
  tunnel1_phase1_integrity_algorithms  = ["SHA2-256"]
  tunnel2_phase1_integrity_algorithms  = ["SHA2-256"]

  # Phase 2 encryption and integrity
  tunnel1_phase2_encryption_algorithms = ["AES256"]
  tunnel2_phase2_encryption_algorithms = ["AES256"]
  tunnel1_phase2_integrity_algorithms  = ["SHA2-256"]
  tunnel2_phase2_integrity_algorithms  = ["SHA2-256"]

  # DPD configuration
  tunnel1_dpd_timeout_action  = "restart"
  tunnel2_dpd_timeout_action  = "restart"
  tunnel1_dpd_timeout_seconds = 30
  tunnel2_dpd_timeout_seconds = 30

  # Network CIDRs
  local_ipv4_network_cidr  = "10.0.0.0/16"
  remote_ipv4_network_cidr = "172.16.0.0/12"

  # Route propagation
  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(module.vpc.private_subnets)

  tags = {
    Name        = "datacenter-vpn-custom"
    Environment = "production"
  }
}
```

### Example 5: Accelerated VPN with CloudWatch Logging

```hcl
# CloudWatch Log Groups for VPN tunnels
resource "aws_cloudwatch_log_group" "tunnel1" {
  name              = "/aws/vpn/tunnel1"
  retention_in_days = 30

  tags = {
    Name = "vpn-tunnel1-logs"
  }
}

resource "aws_cloudwatch_log_group" "tunnel2" {
  name              = "/aws/vpn/tunnel2"
  retention_in_days = 30

  tags = {
    Name = "vpn-tunnel2-logs"
  }
}

resource "aws_customer_gateway" "hq" {
  bgp_asn    = 65200
  ip_address = "203.0.113.200"
  type       = "ipsec.1"

  tags = {
    Name = "hq-customer-gateway"
  }
}

module "vpn_accelerated" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = aws_customer_gateway.hq.id
  vpc_id              = module.vpc.vpc_id

  # Enable acceleration for improved performance
  vpn_connection_enable_acceleration = true

  # CloudWatch logging configuration
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

  # Network configuration
  local_ipv4_network_cidr  = "0.0.0.0/0"
  remote_ipv4_network_cidr = "10.100.0.0/16"

  # Route propagation
  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(module.vpc.private_subnets)

  tags = {
    Name        = "hq-vpn-accelerated"
    Environment = "production"
    Monitoring  = "enabled"
  }
}
```

### Example 6: Dual VPN Connections for High Availability

```hcl
# Customer Gateway 1
resource "aws_customer_gateway" "primary" {
  bgp_asn    = 65300
  ip_address = "198.51.100.10"
  type       = "ipsec.1"

  tags = {
    Name = "primary-cgw"
    Role = "primary"
  }
}

# Customer Gateway 2
resource "aws_customer_gateway" "secondary" {
  bgp_asn    = 65300
  ip_address = "198.51.100.20"
  type       = "ipsec.1"

  tags = {
    Name = "secondary-cgw"
    Role = "secondary"
  }
}

# Primary VPN Connection
module "vpn_primary" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = aws_customer_gateway.primary.id
  vpc_id              = module.vpc.vpc_id

  local_ipv4_network_cidr  = "0.0.0.0/0"
  remote_ipv4_network_cidr = "192.168.0.0/16"

  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(module.vpc.private_subnets)

  tags = {
    Name = "primary-vpn"
    Role = "primary"
  }
}

# Secondary VPN Connection for redundancy
module "vpn_secondary" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = aws_customer_gateway.secondary.id
  vpc_id              = module.vpc.vpc_id

  local_ipv4_network_cidr  = "0.0.0.0/0"
  remote_ipv4_network_cidr = "192.168.0.0/16"

  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(module.vpc.private_subnets)

  tags = {
    Name = "secondary-vpn"
    Role = "secondary"
  }
}
```

### Example 7: IPv6 VPN Connection with Transit Gateway

```hcl
resource "aws_customer_gateway" "ipv6_site" {
  bgp_asn    = 65400
  ip_address = "2001:db8::1"
  type       = "ipsec.1"

  tags = {
    Name = "ipv6-customer-gateway"
  }
}

module "vpn_ipv6" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 4.0"

  connect_to_transit_gateway = true
  transit_gateway_id         = aws_ec2_transit_gateway.main.id
  customer_gateway_id        = aws_customer_gateway.ipv6_site.id

  # Enable IPv6 for tunnel inside addresses
  tunnel_inside_ip_version = "ipv6"

  # IPv6 network configuration
  local_ipv6_network_cidr  = "::/0"
  remote_ipv6_network_cidr = "2001:db8:1234::/48"

  # Custom tunnel inside IPv6 CIDRs
  tunnel1_inside_cidr = "fd00:1234:5678:1::/126"
  tunnel2_inside_cidr = "fd00:1234:5678:2::/126"

  tags = {
    Name       = "ipv6-vpn-tgw"
    IPVersion  = "IPv6"
    Environment = "production"
  }
}
```

## Best Practices

### Security and Encryption

1. **Use Strong Preshared Keys**: Generate complex preshared keys with at least 32 characters using cryptographically secure random generators for tunnel authentication.
2. **Enable IKEv2**: Configure `tunnel_ike_versions = ["ikev2"]` for both tunnels to use the more secure and efficient IKEv2 protocol.
3. **Use AES-256 Encryption**: Specify `phase1_encryption_algorithms = ["AES256"]` and `phase2_encryption_algorithms = ["AES256"]` for maximum security.
4. **Implement SHA2-256 or Higher**: Configure integrity algorithms to use SHA2-256, SHA2-384, or SHA2-512 instead of SHA1 for better cryptographic security.
5. **Rotate Preshared Keys**: Establish a schedule to rotate preshared keys every 90-180 days to minimize exposure risk.
6. **Use Secrets Manager**: Store preshared keys in AWS Secrets Manager rather than hardcoding them in Terraform configurations.
7. **Enable CloudWatch Logging**: Configure tunnel logging to monitor connection activity and detect potential security issues.

### High Availability and Redundancy

1. **Deploy Dual VPN Connections**: Create two separate VPN connections to different customer gateway devices to ensure continuous connectivity during failures.
2. **Use BGP Routing**: Prefer BGP over static routing (`vpn_connection_static_routes_only = false`) for automatic failover and dynamic path selection.
3. **Configure Both Tunnels**: Ensure both tunnels in each VPN connection are actively configured on customer gateway devices for tunnel-level redundancy.
4. **Implement DPD**: Set `tunnel_dpd_timeout_action = "restart"` and `tunnel_dpd_timeout_seconds = 30` to quickly detect and recover from tunnel failures.
5. **Monitor Tunnel Status**: Create CloudWatch alarms for `TunnelState` and `TunnelDataIn/Out` metrics to detect tunnel failures promptly.
6. **Test Failover Regularly**: Periodically test VPN failover by shutting down primary tunnels to verify automatic switchover works correctly.

### Performance and Optimization

1. **Enable Acceleration**: Use `vpn_connection_enable_acceleration = true` for improved throughput and reduced latency in supported regions.
2. **Optimize MTU Settings**: Configure customer gateway devices with appropriate MTU values (typically 1400 bytes) to avoid fragmentation.
3. **Use Transit Gateway for Multi-VPC**: Leverage Transit Gateway instead of multiple VPN connections when connecting to multiple VPCs for better performance and management.
4. **Configure Appropriate Phase Lifetimes**: Adjust Phase 1 and Phase 2 lifetime values based on traffic patterns to balance security and performance.
5. **Monitor Bandwidth Utilization**: Track VPN bandwidth usage and plan for multiple connections if approaching VPN Gateway limits (1.25 Gbps per tunnel).
6. **Optimize BGP Timers**: Configure BGP keepalive and hold timers on customer gateway devices for faster convergence during network changes.

### Network Configuration

1. **Use Non-Overlapping CIDRs**: Ensure local and remote network CIDRs do not overlap to prevent routing conflicts.
2. **Specify Custom Tunnel Inside CIDRs**: Define specific /30 CIDR blocks for tunnel inside addresses (169.254.x.x/30) to avoid conflicts with other VPN connections.
3. **Enable Route Propagation**: Configure `vpc_subnet_route_table_ids` to automatically propagate VPN routes to VPC route tables.
4. **Plan BGP ASN Carefully**: Use private ASN ranges (64512-65534) for customer gateways and ensure ASN uniqueness across your network.
5. **Document IP Addressing**: Maintain clear documentation of all tunnel inside CIDRs, customer gateway IPs, and network CIDRs for troubleshooting.

### Monitoring and Observability

1. **Enable CloudWatch Logs**: Configure CloudWatch log delivery for both tunnels with JSON format for easier parsing and analysis.
2. **Create CloudWatch Alarms**: Set up alarms for tunnel state changes, low data transfer, and connection failures.
3. **Monitor Tunnel Metrics**: Track `TunnelState`, `TunnelDataIn`, `TunnelDataOut` metrics to identify connectivity and performance issues.
4. **Use VPC Flow Logs**: Enable VPC Flow Logs to analyze traffic patterns and troubleshoot routing issues.
5. **Implement Log Retention**: Set appropriate CloudWatch log retention (7-30 days) to balance compliance requirements and costs.
6. **Review Logs Regularly**: Establish processes for regular review of VPN logs to identify anomalies and security incidents.

### Cost Optimization

1. **Consolidate with Transit Gateway**: Use Transit Gateway for multi-VPC connectivity instead of multiple VPN connections to reduce costs.
2. **Right-Size VPN Connections**: Evaluate whether acceleration is needed; disable it if performance requirements don't justify the additional cost.
3. **Monitor Data Transfer**: Track data transfer costs and optimize application traffic patterns to minimize VPN data transfer charges.
4. **Use Direct Connect for High Volume**: Consider AWS Direct Connect for consistently high bandwidth requirements as it may be more cost-effective than VPN.
5. **Review Idle Connections**: Identify and remove unused VPN connections to eliminate unnecessary hourly charges.

### Operational Excellence

1. **Use Infrastructure as Code**: Manage all VPN configurations through Terraform to ensure consistency and enable version control.
2. **Implement Comprehensive Tagging**: Apply tags for Environment, Owner, CostCenter, and Project to all VPN resources for tracking and management.
3. **Document Customer Gateway Configuration**: Maintain detailed documentation of customer gateway device configurations for disaster recovery.
4. **Automate Testing**: Implement automated testing of VPN connectivity as part of change management processes.
5. **Establish Change Control**: Use Terraform workspaces or separate state files for different environments to prevent accidental production changes.
6. **Plan Maintenance Windows**: Schedule VPN connection updates during off-peak hours and communicate changes to stakeholders.
7. **Keep Configurations Updated**: Regularly review and update encryption algorithms and IKE versions to align with current security standards.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-vpn-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/vpn-gateway/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-vpn-gateway/tree/master/examples
- **AWS Site-to-Site VPN Documentation**: https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html
- **VPN Connection Configuration**: https://docs.aws.amazon.com/vpn/latest/s2svpn/how_it_works.html
- **VPN Redundancy and Failover**: https://docs.aws.amazon.com/vpn/latest/s2svpn/vpn-redundant-connection.html
- **Customer Gateway Devices**: https://docs.aws.amazon.com/vpn/latest/s2svpn/your-cgw.html
- **VPN Monitoring**: https://docs.aws.amazon.com/vpn/latest/s2svpn/monitoring-overview-vpn.html
- **VPN Troubleshooting**: https://docs.aws.amazon.com/vpn/latest/s2svpn/Troubleshooting.html
- **Transit Gateway VPN**: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-vpn-attachments.html
- **VPN Pricing**: https://aws.amazon.com/vpn/pricing/
- **VPN CloudWatch Metrics**: https://docs.aws.amazon.com/vpn/latest/s2svpn/monitoring-cloudwatch-vpn.html
- **Accelerated Site-to-Site VPN**: https://docs.aws.amazon.com/vpn/latest/s2svpn/accelerated-vpn.html
- **AWS VPN Best Practices**: https://docs.aws.amazon.com/whitepapers/latest/aws-vpc-connectivity-options/aws-site-to-site-vpn.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Requires Pre-existing Gateways**: Module does not create VPN Gateway or Customer Gateway; ensure these resources exist before using the module
2. **Use BGP When Possible**: Prefer BGP routing over static routes for automatic failover and dynamic routing capabilities
3. **Configure Both Tunnels**: Always configure both tunnels on customer gateway devices to leverage AWS's redundant tunnel architecture
4. **Enable Acceleration Selectively**: VPN acceleration improves performance but increases cost; enable only when needed
5. **Use Strong Security**: Configure IKEv2, AES-256 encryption, and SHA2-256 integrity algorithms for production deployments
6. **Implement CloudWatch Logging**: Enable tunnel logging for monitoring and troubleshooting capabilities
7. **Plan IP Addressing**: Define custom tunnel inside CIDRs to avoid conflicts with other VPN connections
8. **Tag Resources**: Apply comprehensive tags for cost allocation, resource tracking, and automation
9. **Monitor Tunnel Health**: Set up CloudWatch alarms for tunnel state changes and data transfer anomalies
10. **Use Transit Gateway for Scale**: Deploy Transit Gateway instead of multiple VPN connections when connecting to multiple VPCs
11. **Document Configuration**: Maintain detailed documentation of preshared keys, tunnel parameters, and customer gateway configurations
12. **Test Failover**: Regularly test VPN failover scenarios to ensure high availability configurations work correctly
13. **Rotate Secrets**: Implement preshared key rotation using AWS Secrets Manager integration
14. **Optimize for Cost**: Consolidate VPN connections through Transit Gateway and disable acceleration if not required
15. **Enable Route Propagation**: Configure automatic route propagation to VPC route tables for seamless connectivity
