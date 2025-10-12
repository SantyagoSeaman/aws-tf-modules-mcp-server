---
module_name: customer-gateway
keywords: [customer-gateway, cgw, site-to-site-vpn, vpn, vpn-connection, hybrid-cloud, on-premises, ipsec, bgp, bgp-asn, border-gateway-protocol, virtual-private-gateway, vgw, transit-gateway, tgw, vpn-tunnel, encryption, secure-connection, network-integration, datacenter, private-connectivity, redundancy, failover, high-availability, ikev2, nat-traversal, routing, external-ip, gateway-device, vpn-appliance, networking]
---

# Terraform AWS Customer Gateway Module

## Module Information

- **Module Name**: `customer-gateway`
- **Source**: `terraform-aws-modules/customer-gateway/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-customer-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/customer-gateway/aws/latest
- **Latest Version**: 3.1.0
- **Purpose**: Terraform module that creates AWS Customer Gateway resources for Site-to-Site VPN connections between on-premises networks and AWS VPCs
- **Service**: AWS VPN (Virtual Private Network) - Customer Gateway Component
- **Category**: Networking, Hybrid Cloud, Security
- **Keywords**: customer-gateway, cgw, site-to-site-vpn, vpn, vpn-connection, hybrid-cloud, on-premises, ipsec, bgp, bgp-asn, border-gateway-protocol, virtual-private-gateway, vgw, transit-gateway, tgw, vpn-tunnel, encryption, secure-connection, network-integration, datacenter, private-connectivity, redundancy, failover, high-availability, ikev2, nat-traversal, routing, external-ip, gateway-device, vpn-appliance, networking
- **Use For**: Connecting on-premises data centers to AWS VPCs via Site-to-Site VPN, establishing hybrid cloud networking infrastructure, extending corporate networks to AWS securely, enabling secure communication between branch offices and AWS resources, implementing disaster recovery connectivity, creating redundant VPN connections for high availability, migrating workloads with persistent on-premises connectivity, building multi-region hybrid architectures

## Description

The AWS Customer Gateway Terraform module simplifies the creation and management of AWS Customer Gateway resources, which represent the customer side of a Site-to-Site VPN connection between an on-premises network and Amazon VPC. A Customer Gateway is an AWS resource that contains information about your customer gateway device—the physical or software appliance on your side of the VPN connection, including its public IP address and BGP (Border Gateway Protocol) Autonomous System Number (ASN). This module enables declarative infrastructure-as-code management of customer gateways, allowing teams to define multiple gateway configurations with specific BGP ASN values and external IP addresses in a single, reusable module.

Site-to-Site VPN connections provide secure, encrypted IPsec tunnels between on-premises infrastructure and AWS, enabling hybrid cloud architectures where workloads span both environments. Each VPN connection consists of two redundant VPN tunnels for high availability, and the Customer Gateway resource serves as the AWS-side representation of the on-premises VPN endpoint. The module supports creating multiple customer gateways simultaneously through a map-based configuration approach, making it ideal for organizations with multiple data centers, branch offices, or redundant VPN devices that need to establish connectivity to AWS.

The module integrates seamlessly with other AWS networking modules such as VPC, Virtual Private Gateway, and Transit Gateway modules, forming a complete hybrid networking solution. It provides a clean interface with conditional resource creation, comprehensive tagging support, and outputs that can be referenced by VPN connection modules. By abstracting the complexity of Customer Gateway resource management into a reusable module, it enables consistent, repeatable deployments of hybrid cloud networking infrastructure across multiple environments and regions.

## Key Features

- **Multiple Customer Gateways**: Create multiple customer gateway resources in a single module using map-based configuration
- **BGP Configuration**: Specify BGP Autonomous System Number (ASN) for dynamic routing with AWS
- **External IP Definition**: Configure the public IP address of on-premises VPN devices
- **Conditional Creation**: Control whether resources are created using the `create` flag for flexible deployment scenarios
- **Map-Based Configuration**: Define customer gateways using intuitive key-value map structure with bgp_asn and ip_address
- **Comprehensive Tagging**: Apply custom tags to all customer gateway resources for organization, cost allocation, and compliance
- **Output Integration**: Provides gateway IDs and attributes for use with VPN connection and routing configurations
- **Simple Interface**: Minimal required inputs (customer_gateways map) for quick deployment
- **Name Prefix Support**: Consistent resource naming using the `name` parameter across all created gateways
- **Terraform 1.0+ Compatible**: Works with modern Terraform versions (>= 1.0)
- **AWS Provider 4.40+**: Supports latest AWS provider features and customer gateway capabilities

## Main Use Cases

1. **Hybrid Cloud Connectivity**: Connect on-premises data centers to AWS VPCs for hybrid application architectures
2. **Disaster Recovery**: Establish VPN connections for DR scenarios with persistent network connectivity
3. **Branch Office Integration**: Connect multiple branch office locations to centralized AWS infrastructure
4. **Multi-Region Hybrid**: Create customer gateways in multiple regions for global hybrid cloud deployments
5. **Migration Workflows**: Maintain on-premises connectivity during phased cloud migration projects
6. **Development and Testing**: Provide developers with secure access to AWS resources from corporate networks
7. **Regulatory Compliance**: Enable secure, encrypted communication for workloads with data sovereignty requirements
8. **Transit Gateway Hub**: Create customer gateways as spokes connecting to AWS Transit Gateway hubs

## Best Practices

### Customer Gateway Configuration

1. **Use Static Public IPs**: Configure customer gateways with static public IP addresses to prevent connection disruptions
2. **BGP ASN Selection**: Use private BGP ASN range (64512-65534) unless you own a public ASN
3. **Unique ASNs**: Assign unique BGP ASN values for each customer gateway unless they're part of the same routing domain
4. **IP Address Validation**: Verify the external IP address is correct and reachable from AWS before creating VPN connections
5. **Naming Convention**: Use descriptive names that identify the location or purpose (e.g., "datacenter-us-east", "branch-london")
6. **Documentation**: Maintain documentation mapping customer gateway IDs to physical device locations and administrators
7. **Multiple Gateways for HA**: Create separate customer gateways for each redundant VPN device at a location
8. **NAT Considerations**: If the VPN device is behind NAT, use the NAT device's public IP address

### VPN Device Requirements

1. **Device Compatibility**: Ensure on-premises VPN device supports IPsec, IKEv2, and AWS VPN requirements
2. **Firmware Updates**: Keep VPN device firmware updated to support latest encryption and security features
3. **Redundant Devices**: Deploy redundant VPN devices on-premises for high availability
4. **Hardware Specifications**: Size VPN appliances appropriately for expected throughput (up to 1.25 Gbps per tunnel)
5. **Configuration Backup**: Regularly backup VPN device configurations for disaster recovery
6. **Monitoring Capability**: Ensure VPN devices support SNMP or other monitoring protocols for observability
7. **Certificate Management**: If using certificate-based authentication, implement proper certificate lifecycle management
8. **BGP Configuration**: Configure BGP on VPN devices when using dynamic routing for automatic failover

### Integration with VPN Connections

1. **Virtual Private Gateway**: Create VGW and attach to VPC before establishing VPN connections
2. **Transit Gateway Option**: Use Transit Gateway for scalable hub-and-spoke architectures with multiple VPCs
3. **Routing Propagation**: Enable route propagation on VPC route tables to receive on-premises routes via BGP
4. **Static Routes Alternative**: Use static routes if BGP is not available on customer gateway device
5. **VPN Connection Module**: Use terraform-aws-modules/vpn-gateway module or similar for VPN connection creation
6. **Tunnel Configuration**: Configure both VPN tunnels on customer device for redundancy
7. **Health Checks**: Implement health monitoring for VPN tunnels to detect failures quickly
8. **DPD Configuration**: Configure Dead Peer Detection (DPD) to detect tunnel failures promptly

### Security Best Practices

1. **Encryption Standards**: Use AES 256-bit encryption for VPN tunnels (AWS default)
2. **Perfect Forward Secrecy**: Enable PFS (Perfect Forward Secrecy) on VPN connections for enhanced security
3. **Pre-Shared Keys**: Use strong, randomly generated pre-shared keys for VPN tunnel authentication
4. **Key Rotation**: Implement regular rotation of pre-shared keys and certificates
5. **Access Control**: Restrict access to VPN device management interfaces using firewall rules
6. **Audit Logging**: Enable CloudTrail logging for all customer gateway and VPN connection API calls
7. **Network Segmentation**: Use security groups and NACLs to control traffic flow from VPN connections
8. **Principle of Least Privilege**: Limit on-premises network routes advertised to AWS to necessary subnets only

### High Availability and Reliability

1. **Dual Tunnels**: Always configure both VPN tunnels provided by AWS for automatic failover
2. **Active-Active Configuration**: Configure VPN devices to use both tunnels simultaneously for load balancing
3. **Multiple Customer Gateways**: Create multiple customer gateways for different physical devices for redundancy
4. **BGP Failover**: Use BGP for automatic failover between primary and backup VPN connections
5. **Monitoring and Alerting**: Set up CloudWatch alarms for VPN tunnel status and data transfer metrics
6. **Tunnel Maintenance**: Expect and plan for routine AWS maintenance that may affect one tunnel temporarily
7. **Geographic Diversity**: For critical connections, consider VPN endpoints in different AWS regions
8. **Testing Failover**: Regularly test VPN failover scenarios to validate high availability configuration

### Operational Excellence

1. **Infrastructure as Code**: Manage all customer gateways through Terraform for consistent, repeatable deployments
2. **Version Control**: Store module configurations in Git for change tracking and collaboration
3. **Module Versioning**: Pin module version in production (e.g., `version = "~> 3.1"`) for stability
4. **Tagging Strategy**: Implement comprehensive tagging for cost allocation, environment identification, and automation
5. **Change Management**: Use terraform plan to review changes before applying modifications to customer gateways
6. **Documentation**: Document the relationship between customer gateway resources and physical VPN devices
7. **Runbooks**: Create operational runbooks for common VPN connection troubleshooting scenarios
8. **Capacity Planning**: Monitor VPN throughput and plan for capacity increases or additional tunnels as needed

### Cost Optimization

1. **Connection Fees**: AWS charges hourly for each active VPN connection; consolidate connections where possible
2. **Data Transfer Costs**: Understand data transfer charges for traffic over VPN connections
3. **Unused Gateways**: Delete customer gateway resources that are no longer in use
4. **Direct Connect Alternative**: For high-bandwidth, consistent traffic, evaluate AWS Direct Connect as a cost-effective alternative
5. **Transit Gateway Consolidation**: Use Transit Gateway to consolidate multiple VPN connections and reduce costs
6. **Traffic Optimization**: Optimize application traffic patterns to minimize data transfer over VPN
7. **Monitoring Costs**: Track VPN usage and costs using AWS Cost Explorer with appropriate tags

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-customer-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/customer-gateway/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-customer-gateway/tree/master/examples
- **AWS Customer Gateway Documentation**: https://docs.aws.amazon.com/vpn/latest/s2svpn/your-cgw.html
- **AWS Site-to-Site VPN**: https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html
- **VPN Configuration Guides**: https://docs.aws.amazon.com/vpn/latest/s2svpn/Examples.html
- **BGP on AWS**: https://docs.aws.amazon.com/vpn/latest/s2svpn/cgw-dynamic-routing.html
- **VPN Monitoring**: https://docs.aws.amazon.com/vpn/latest/s2svpn/monitoring-overview-vpn.html
- **VPN Troubleshooting**: https://docs.aws.amazon.com/vpn/latest/s2svpn/Troubleshooting.html
- **Transit Gateway**: https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html
- **VPN Pricing**: https://aws.amazon.com/vpn/pricing/
- **AWS VPN CloudWatch Metrics**: https://docs.aws.amazon.com/vpn/latest/s2svpn/monitoring-cloudwatch-vpn.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Simplicity**: This is a straightforward module with minimal configuration—primarily requires customer_gateways map with bgp_asn and ip_address
2. **Map Structure**: Define customer_gateways as a map where keys are identifiers and values contain bgp_asn and ip_address attributes
3. **BGP ASN**: Use values in private range (64512-65534) for standard deployments unless you have a public ASN
4. **Public IP Requirement**: The ip_address must be the public-facing IP of the on-premises VPN device
5. **Integration**: Customer gateway alone does not establish connectivity; must be paired with VPN connection resources
6. **Multiple Gateways**: Can create multiple customer gateways in one module call by adding entries to the customer_gateways map
7. **Outputs**: Module outputs gateway IDs and attributes for use in VPN connection module configurations
8. **Naming**: The name parameter is used as a prefix for all created customer gateway resources
9. **Conditional Creation**: Use create = false to manage customer gateway lifecycle without destroying dependent resources
10. **Tagging**: Apply consistent tags for cost tracking, environment identification, and resource management
11. **No Submodules**: This module has no submodules; it's a simple wrapper for aws_customer_gateway resources
12. **VPN Device Configuration**: Remember that AWS Customer Gateway is just a representation; actual VPN device must be separately configured
