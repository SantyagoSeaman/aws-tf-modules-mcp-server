# Terraform AWS Transit Gateway Module

## Module Information

- **Module Name**: `transit-gateway`
- **Source**: `terraform-aws-modules/transit-gateway/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-transit-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/transit-gateway/aws/latest
- **Latest Version**: 3.0.0
- **Purpose**: Terraform module that creates and manages AWS Transit Gateway resources for interconnecting VPCs and on-premises networks through a centralized network hub
- **Service**: AWS Transit Gateway (Amazon VPC Transit Gateway)
- **Category**: Networking, Connectivity, Hub-and-Spoke
- **Keywords**: transit-gateway, tgw, aws-transit-gateway, vpc-interconnection, network-hub, vpc-peering, centralized-routing, multi-vpc, hybrid-cloud, vpc-attachments, route-tables, bgp, border-gateway-protocol, vpn-connection, direct-connect, site-to-site-vpn, inter-region-peering, cross-region, transit-gateway-peering, resource-access-manager, ram, multi-account, cross-account, shared-services, network-segmentation, transit-routing, centralized-egress, centralized-ingress, inspection-vpc, network-firewall-integration, route-propagation, static-routes, dynamic-routes, dns-support, ipv6-support, multicast, ecmp, equal-cost-multipath, appliance-mode, sd-wan, network-appliances, mtu, jumbo-frames, encryption, inter-az-traffic, availability-zones, high-availability, disaster-recovery, multi-region, global-network, autonomous-system-number, asn, network-topology, hub-and-spoke, mesh-network, centralized-security, shared-vpc, transit-vpc, network-transit-hub, vpc-routing, route-table-association, route-table-propagation, attachment-subnet, network-acl, security-group-referencing, blackhole-routes, packet-inspection, traffic-filtering, egress-vpc, ingress-vpc
- **Use For**: multi-VPC connectivity, centralized network routing, hybrid cloud networking, on-premises to AWS connectivity, inter-region networking, shared services architecture, network segmentation, centralized egress/ingress, inspection VPC architectures, SD-WAN integration, multi-account networking, disaster recovery networking, global network infrastructure

## Description

AWS Transit Gateway is a network transit hub that enables organizations to interconnect thousands of VPCs and on-premises networks through a single, centrally managed gateway. This Terraform module simplifies the deployment and management of Transit Gateway resources, including the gateway itself, VPC attachments, route tables, route propagation rules, and cross-account sharing configurations via AWS Resource Access Manager (RAM). The module eliminates the complexity of managing point-to-point VPC peering connections and provides a scalable, hub-and-spoke network architecture that reduces operational overhead while improving network visibility and control.

The module supports comprehensive Transit Gateway features including multiple attachment types (VPCs, VPN connections, Direct Connect gateways, Transit Gateway peering), custom route table configurations for network segmentation, BGP route propagation for dynamic routing, and DNS resolution across connected networks. It enables advanced networking patterns such as centralized egress through inspection VPCs, shared services architectures where common resources are accessed from multiple VPCs, and multi-account networking where Transit Gateways are shared across AWS accounts in an organization. The module handles complex configurations such as route table associations, route propagation settings, and subnet mappings across multiple availability zones.

Built for enterprise-scale deployments, the module provides features essential for production environments including automatic encryption of inter-region traffic, support for jumbo frames (8500 byte MTU), IPv6 addressing, multicast traffic distribution, and ECMP (Equal-Cost Multi-Path) routing for high-throughput VPN connections. It integrates seamlessly with AWS Resource Access Manager for secure cross-account sharing, supports inter-region peering for global network connectivity, and enables appliance mode for stateful network appliances like firewalls and load balancers. With comprehensive tagging, conditional resource creation, and flexible routing configurations, this module serves as the foundation for building scalable, secure, and highly available network architectures in AWS.

## Key Features

- **Centralized Network Hub**: Create single transit hub connecting thousands of VPCs and on-premises networks
- **VPC Attachments**: Attach multiple VPCs to Transit Gateway with customizable subnet and availability zone configurations
- **Multi-Account Sharing**: Share Transit Gateway across AWS accounts using Resource Access Manager (RAM)
- **Custom Route Tables**: Create multiple route tables for network segmentation and traffic isolation
- **Route Propagation**: Enable automatic route propagation from VPC attachments, VPN connections, and Direct Connect gateways
- **Static Route Configuration**: Define static routes for precise traffic control and blackhole routes for traffic blocking
- **BGP Support**: Leverage Border Gateway Protocol for dynamic route exchange with on-premises networks
- **VPN Attachments**: Connect Site-to-Site VPN connections for secure hybrid cloud connectivity
- **Direct Connect Integration**: Attach Direct Connect gateways for high-bandwidth, low-latency on-premises connectivity
- **Inter-Region Peering**: Establish peering connections between Transit Gateways in different AWS regions
- **DNS Support**: Enable DNS hostname resolution across all attached VPCs for seamless service discovery
- **IPv6 Support**: Full support for IPv6 addressing and routing across the Transit Gateway
- **Multicast Support**: Distribute multicast traffic across multiple VPCs for streaming and messaging applications
- **ECMP Support**: Enable Equal-Cost Multi-Path routing for VPN connections to increase bandwidth
- **Appliance Mode**: Support for stateful network appliances requiring symmetric traffic flow
- **Security Group Referencing**: Reference security groups across VPC attachments for simplified security rules
- **Auto-Accept Shared Attachments**: Automatically accept VPC attachment requests from shared accounts
- **Default Route Table**: Configure default route table for standard traffic routing patterns
- **Association and Propagation**: Fine-grained control over route table associations and propagations per attachment
- **Blackhole Routes**: Define blackhole routes to drop specific traffic patterns
- **High MTU Support**: Support for 8500-byte MTU for high-throughput applications (jumbo frames)
- **Automatic Encryption**: Traffic between AWS regions automatically encrypted using AWS-managed keys
- **Resource Tagging**: Comprehensive tagging for Transit Gateway and all attachment resources
- **Conditional Creation**: Flexible resource creation flags for modular deployment patterns
- **Multi-AZ Resilience**: Automatic deployment across availability zones for fault tolerance

## Main Use Cases

1. **Multi-VPC Connectivity**: Simplify network connectivity by connecting hundreds of VPCs through single Transit Gateway hub
2. **Hybrid Cloud Networking**: Extend on-premises networks to AWS using VPN or Direct Connect through Transit Gateway
3. **Centralized Internet Egress**: Route all outbound internet traffic through centralized egress VPC with security controls
4. **Shared Services Architecture**: Provide centralized services (Active Directory, monitoring) accessible from all VPCs
5. **Network Segmentation**: Isolate production, development, and testing environments using separate route tables
6. **Multi-Account Networking**: Connect VPCs across multiple AWS accounts in Organizations with centralized management
7. **Inspection VPC Architectures**: Route all inter-VPC traffic through central inspection VPC with network firewalls
8. **Disaster Recovery**: Establish inter-region Transit Gateway peering for cross-region failover scenarios
9. **SD-WAN Integration**: Connect SD-WAN appliances to AWS networks through Transit Gateway VPN attachments
10. **Global Network Infrastructure**: Build worldwide network using inter-region peering and global routing tables

## Best Practices

### Design and Architecture

1. **Hub-and-Spoke Topology**: Use Transit Gateway as central hub with VPCs as spokes for simplified network management
2. **Separate Attachment Subnets**: Dedicate separate subnets in each VPC specifically for Transit Gateway attachments
3. **Small CIDR Blocks for Attachments**: Use /28 CIDR blocks for Transit Gateway subnets to conserve IP address space
4. **Multi-AZ Attachments**: Deploy attachment subnets across at least two availability zones for high availability
5. **Centralized Architecture**: Deploy single Transit Gateway per region rather than multiple Transit Gateways for simplicity
6. **Region-Specific Transit Gateways**: Use one Transit Gateway per region for disaster recovery; connect via inter-region peering
7. **Unique ASN per Transit Gateway**: Assign unique Autonomous System Numbers to each Transit Gateway for BGP routing

### Route Table Configuration

1. **Limit Route Tables**: Minimize the number of route tables; use only what's necessary for segmentation
2. **Default Route Table Strategy**: Use default route table for standard connectivity; create custom tables only for isolation
3. **Segment by Environment**: Create separate route tables for production, development, and testing environments
4. **Enable Route Propagation**: Enable automatic route propagation for Direct Connect and VPN attachments
5. **Static Routes for Control**: Use static routes when precise control over traffic paths is required
6. **Blackhole Routes for Security**: Define blackhole routes to explicitly block traffic to specific destinations
7. **Document Routing Logic**: Maintain clear documentation of route table purposes and traffic flow patterns
8. **Route Table Associations**: Explicitly associate VPC attachments with appropriate route tables for traffic control

### VPC Attachment Configuration

1. **Consistent Subnet Strategy**: Use consistent subnet sizing and naming across all VPC attachments
2. **Open Network ACLs**: Keep network ACLs associated with Transit Gateway subnets fully open for unrestricted traffic flow
3. **Single Network ACL**: Use single network ACL for all Transit Gateway subnets in a VPC
4. **Same Route Table**: Associate same VPC route table with all Transit Gateway subnets in a VPC
5. **DNS Support Enablement**: Enable DNS support on attachments for hostname resolution across VPCs
6. **IPv6 When Needed**: Enable IPv6 support if any VPCs require IPv6 connectivity
7. **Appliance Mode for Firewalls**: Enable appliance mode for attachments to inspection VPCs with stateful appliances

### Security and Access Control

1. **Resource Access Manager**: Use RAM for secure, controlled sharing of Transit Gateway across accounts
2. **Least Privilege Sharing**: Share Transit Gateway only with specific AWS accounts or organizational units (OUs)
3. **Auto-Accept for Trusted Accounts**: Enable auto-accept shared attachments only for accounts within your organization
4. **Security Group Referencing**: Leverage security group referencing to simplify cross-VPC security rules
5. **Network Segmentation**: Use route tables to enforce network segmentation and prevent unauthorized east-west traffic
6. **Inspection VPC Pattern**: Route all inter-VPC traffic through central inspection VPC with Network Firewall
7. **Audit Attachments**: Regularly audit VPC attachments to identify and remove unused connections
8. **CloudTrail Logging**: Enable CloudTrail to log all Transit Gateway API calls for security auditing

### VPN and Hybrid Connectivity

1. **Use BGP for VPN**: Configure Site-to-Site VPN with BGP for dynamic route exchange and automatic failover
2. **ECMP for Throughput**: Enable ECMP support and deploy multiple VPN tunnels for increased bandwidth
3. **Unique ASN**: Use unique ASN for each on-premises customer gateway for proper BGP routing
4. **Direct Connect Preferred**: Use Direct Connect over VPN when consistent high bandwidth and low latency are required
5. **Redundant Connections**: Deploy redundant VPN or Direct Connect connections for high availability
6. **BGP Route Propagation**: Enable route propagation on Transit Gateway for automatic route updates from on-premises
7. **MTU Considerations**: Be aware of MTU limitations (1500 bytes for VPN) when migrating from VPC peering

### Performance and Optimization

1. **Monitor Transit Gateway Metrics**: Track bytes in/out, packet loss, and attachment count in CloudWatch
2. **Right-Size Attachments**: Deploy attachments only in AZs where workloads exist to reduce costs
3. **ECMP for Load Distribution**: Use ECMP to distribute traffic across multiple VPN connections
4. **Jumbo Frames**: Leverage 8500-byte MTU for high-throughput workloads between VPCs
5. **Minimize Hop Count**: Design network topology to minimize hops through Transit Gateway
6. **Regional Deployments**: Keep frequently communicating workloads in same region to minimize inter-region costs
7. **Connection Limits**: Understand Transit Gateway limits (5000 attachments per gateway) and plan architecture accordingly

### Cost Optimization

1. **Consolidate Transit Gateways**: Use single Transit Gateway per region to minimize per-attachment hourly costs
2. **Monitor Data Transfer**: Track data transfer through Transit Gateway to optimize traffic patterns
3. **Regional Traffic**: Keep traffic within same region when possible to avoid inter-region transfer charges
4. **Shared Services**: Centralize shared services to reduce duplication and attachment count
5. **Remove Unused Attachments**: Regularly audit and remove VPC attachments that are no longer needed
6. **VPN vs Direct Connect**: Evaluate cost-benefit of VPN vs Direct Connect based on bandwidth requirements
7. **Inter-Region Peering Costs**: Factor in data transfer costs when designing multi-region architectures

### Monitoring and Observability

1. **Enable CloudWatch Metrics**: Monitor Transit Gateway metrics including bytes, packets, and packet drop count
2. **VPC Flow Logs**: Enable VPC Flow Logs on attachment subnets for traffic analysis and troubleshooting
3. **Set Up Alarms**: Create CloudWatch alarms for packet loss, high traffic volume, and attachment failures
4. **Route Table Monitoring**: Regularly review route tables to ensure routes are propagating correctly
5. **BGP Session Monitoring**: Monitor BGP session status for VPN and Direct Connect attachments
6. **Network Performance**: Use VPC Reachability Analyzer to validate connectivity between VPCs
7. **Dashboard Creation**: Build CloudWatch dashboards showing Transit Gateway traffic patterns and health

### High Availability and Disaster Recovery

1. **Multi-AZ Deployment**: Transit Gateway automatically deploys across multiple AZs; ensure VPC attachments do the same
2. **No Additional Gateways Needed**: Single Transit Gateway per region provides high availability; multiple gateways aren't necessary
3. **Inter-Region Peering**: Use Transit Gateway peering for disaster recovery between regions
4. **Backup Route Tables**: Export and document route table configurations for rapid recovery
5. **Test Failover**: Regularly test failover scenarios including AZ failures and region failures
6. **Redundant Hybrid Connections**: Deploy multiple VPN or Direct Connect connections for on-premises redundancy
7. **Health Checks**: Implement application-level health checks to validate end-to-end connectivity

### Multi-Account and Organizational Deployment

1. **Centralized Network Account**: Deploy Transit Gateway in dedicated network account for separation of concerns
2. **RAM Sharing Strategy**: Share Transit Gateway with specific accounts or organizational units based on security requirements
3. **Attachment Approval Process**: Implement approval workflow for VPC attachment requests in shared environments
4. **Tag-Based Access Control**: Use resource tags and IAM policies to control who can create and manage attachments
5. **Cross-Account Routing**: Design route tables to properly handle cross-account traffic flows
6. **Service Control Policies**: Use SCPs to restrict unauthorized Transit Gateway operations
7. **Audit Multi-Account Usage**: Regularly review which accounts are using shared Transit Gateway

### Deployment and Operations

1. **Infrastructure as Code**: Manage all Transit Gateway resources through Terraform for consistency
2. **Version Control**: Store Transit Gateway configurations in Git for change tracking and rollback
3. **Modular Deployment**: Use separate Terraform modules for Transit Gateway and VPC attachments
4. **Staged Rollouts**: Test Transit Gateway configurations in development before production deployment
5. **Change Management**: Require approval for production Transit Gateway and route table changes
6. **Tag Consistently**: Apply comprehensive tags including environment, cost-center, and network-zone
7. **Module Version Pinning**: Pin module version in production: `version = "~> 3.0"` for stability
8. **Documentation**: Maintain network diagrams showing Transit Gateway topology and traffic flows
9. **Automation**: Automate VPC attachment creation as part of VPC provisioning workflows
10. **Migration Planning**: Plan careful migration from VPC peering to Transit Gateway to minimize disruption

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-transit-gateway
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/transit-gateway/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-transit-gateway/tree/master/examples
- **AWS Transit Gateway Documentation**: https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html
- **Transit Gateway API Reference**: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/OperationList-query-tgw.html
- **Best Design Practices**: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-best-design-practices.html
- **Transit Gateway Routing**: https://docs.aws.amazon.com/vpc/latest/tgw/how-transit-gateways-work.html
- **VPC Attachments**: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-vpc-attachments.html
- **Inter-Region Peering**: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-peering.html
- **Resource Access Manager**: https://docs.aws.amazon.com/ram/latest/userguide/what-is.html
- **VPN Attachments**: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-vpn-attachments.html
- **Direct Connect Gateway**: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-dcg-attachments.html
- **Transit Gateway Pricing**: https://aws.amazon.com/transit-gateway/pricing/
- **Monitoring Transit Gateway**: https://docs.aws.amazon.com/vpc/latest/tgw/transit-gateway-cloudwatch-metrics.html
- **Network Architecture Examples**: https://docs.aws.amazon.com/vpc/latest/tgw/transit-gateway-examples.html

## Notes for AI Agents

When using this module in automated workflows:

1. **VPC Subnet Requirements**: Ensure dedicated subnets exist in VPCs for Transit Gateway attachments before deployment
2. **CIDR Planning**: Use /28 CIDR blocks for attachment subnets to conserve IP space
3. **Multi-AZ Configuration**: Define subnet_ids spanning at least two availability zones for high availability
4. **Route Table Strategy**: Decide between using default route table or creating custom tables for segmentation
5. **DNS Support**: Enable `dns_support = true` for hostname resolution across attached VPCs
6. **RAM Sharing**: Configure `ram_principals` with AWS account IDs or organizational unit ARNs for cross-account sharing
7. **Auto-Accept**: Set `auto_accept_shared_attachments = true` to automatically accept attachment requests
8. **Route Propagation**: Enable route propagation for VPN and Direct Connect attachments for dynamic routing
9. **ECMP Support**: Enable `vpn_ecmp_support = true` if using multiple VPN tunnels for increased throughput
10. **IPv6 Consideration**: Enable `ipv6_support = true` only if IPv6 addressing is required
11. **Tagging Strategy**: Apply consistent tags for environment, network-zone, and cost-center tracking
12. **BGP ASN**: Use unique ASN values for each Transit Gateway (default is 64512)
13. **Monitoring**: Set up CloudWatch alarms for bytes in/out and packet drop metrics
14. **Route Tables**: Plan route table architecture before deployment (default, custom, or segmented)
15. **Testing**: Validate connectivity between VPCs after attachment using VPC Reachability Analyzer
