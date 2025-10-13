# Terraform AWS Network Firewall Module

## Module Information

- **Module Name**: `network-firewall`
- **Source**: `terraform-aws-modules/network-firewall/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-network-firewall
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/network-firewall/aws/latest
- **Latest Version**: 2.0.1
- **Purpose**: Terraform module that creates and manages AWS Network Firewall resources for stateful network traffic inspection and intrusion detection/prevention in VPCs
- **Service**: AWS Network Firewall (Amazon Network Firewall)
- **Category**: Security, Networking, Firewall
- **Keywords**: network-firewall, aws-network-firewall, vpc-firewall, stateful-firewall, stateless-firewall, intrusion-detection, intrusion-prevention, ids, ips, suricata, firewall-policy, firewall-rules, rule-groups, stateful-rules, stateless-rules, domain-filtering, ip-filtering, protocol-detection, deep-packet-inspection, dpi, network-security, vpc-security, perimeter-security, traffic-filtering, packet-inspection, firewall-logging, cloudwatch-logs, s3-logging, flow-logs, alert-logs, kms-encryption, resource-policy, subnet-mapping, availability-zones, firewall-endpoint, vpc-endpoint, nat-gateway-protection, internet-gateway-filtering, vpn-filtering, direct-connect-security, network-segmentation, micro-segmentation, threat-detection, threat-prevention, malware-detection, signature-based-detection, anomaly-detection, rule-evaluation, rule-order, rule-priority, stateful-inspection, connection-tracking, session-management, protocol-analysis, application-layer-filtering, network-layer-filtering, egress-filtering, ingress-filtering, east-west-traffic, north-south-traffic, centralized-firewall, distributed-firewall, firewall-manager, multi-account-firewall, cross-account-firewall, compliance, pci-dss, hipaa, network-monitoring, security-monitoring
- **Use For**: VPC perimeter security, intrusion detection and prevention, egress traffic filtering, internet gateway protection, malware detection, domain-based filtering, application-layer inspection, compliance enforcement (PCI-DSS, HIPAA), threat prevention, centralized firewall management, multi-account security, east-west traffic inspection, north-south traffic control, network segmentation enforcement

## Description

AWS Network Firewall is a stateful, managed network firewall and intrusion detection and prevention service that provides fine-grained network traffic filtering at the VPC level. This Terraform module simplifies the deployment and management of AWS Network Firewall resources, including firewall instances, firewall policies, rule groups, and logging configurations. The module leverages Suricata, an open-source intrusion prevention system, to provide deep packet inspection, stateful protocol detection, and advanced threat detection capabilities for protecting AWS VPC environments from network-based threats.

The module supports comprehensive traffic filtering scenarios including stateless rules for individual packet inspection and stateful rules for context-aware traffic flow analysis. It enables filtering of traffic at critical network boundaries including internet gateways, NAT gateways, VPN connections, and AWS Direct Connect, providing a centralized security enforcement point for both north-south (internet-facing) and east-west (inter-VPC) traffic patterns. The module handles complex configurations such as multi-subnet deployments across availability zones, custom domain filtering, IP-based access controls, and protocol-specific inspection rules.

Built for enterprise security requirements, the module provides extensive logging capabilities to CloudWatch Logs and Amazon S3 for both flow logs and alert logs, enabling comprehensive security monitoring and compliance reporting. It supports integration with AWS Firewall Manager for centralized policy management across multiple accounts and VPCs in AWS Organizations. The module implements AWS best practices including KMS encryption for firewall configurations, resource policies for access control, delete protection for production firewalls, and flexible subnet mapping strategies for high availability. With comprehensive tagging support, modular architecture, and conditional resource creation, this module serves as the foundation for implementing defense-in-depth network security architectures in AWS.

## Key Features

- **Stateful Firewall Inspection**: Deep packet inspection with connection tracking and session management for context-aware traffic filtering
- **Stateless Rule Processing**: Fast, individual packet inspection based on 5-tuple matching (source IP, destination IP, source port, destination port, protocol)
- **Suricata IPS Engine**: Built-in Suricata intrusion prevention system for signature-based threat detection and prevention
- **Domain Filtering**: Allow or deny traffic based on fully qualified domain names (FQDNs) and domain patterns
- **IP Address Filtering**: Configure IP-based rules for source and destination address filtering with CIDR notation support
- **Protocol Detection**: Automatic stateful protocol detection for common protocols (HTTP, TLS, DNS, SSH, etc.)
- **Deep Packet Inspection**: Application-layer inspection capabilities for detecting threats in encrypted and unencrypted traffic
- **Rule Groups**: Organize firewall rules into reusable, shareable rule groups for consistent policy enforcement
- **Stateful Rule Options**: Support for Suricata-compatible rule strings, domain lists, and 5-tuple stateful rules
- **Rule Evaluation Order**: Configurable rule evaluation order (default action order, strict order) for precise control
- **Subnet Mapping**: Deploy firewall endpoints across multiple subnets and availability zones for high availability
- **VPC Integration**: Seamless integration with VPC routing for transparent traffic interception and inspection
- **Multi-AZ Deployment**: Automatic deployment across availability zones for fault tolerance and high availability
- **Logging Configuration**: Comprehensive logging to CloudWatch Logs and S3 for ALERT and FLOW log types
- **CloudWatch Integration**: Native integration with CloudWatch for metrics, alarms, and log analysis
- **S3 Log Delivery**: Archive firewall logs to S3 buckets for long-term retention and compliance
- **KMS Encryption**: Customer-managed KMS key encryption for firewall configuration data at rest
- **Delete Protection**: Configurable delete protection to prevent accidental firewall deletion in production
- **Policy Change Protection**: Optional protection against accidental firewall policy modifications
- **Resource Policies**: Fine-grained access control using resource-based policies for cross-account sharing
- **Custom Actions**: Define custom actions for stateless rules (pass, drop, forward to stateful)
- **Default Actions**: Configure default actions for both stateless and stateful traffic processing
- **Firewall Manager Integration**: Centralized firewall policy management across AWS Organizations accounts
- **Tagging Support**: Comprehensive resource tagging for organization, cost allocation, and compliance tracking
- **Conditional Creation**: Flexible resource creation flags for modular deployment across environments
- **Modular Architecture**: Separate sub-modules for firewall, policy, and rule group resources

## Main Use Cases

1. **VPC Perimeter Security**: Protect VPC boundaries by inspecting all traffic entering and leaving through internet gateways
2. **Egress Traffic Filtering**: Control and monitor outbound traffic from VPCs to prevent data exfiltration and malware communication
3. **Intrusion Detection and Prevention**: Detect and block known attack patterns, exploits, and malicious traffic using Suricata signatures
4. **Compliance Enforcement**: Implement network security controls required for PCI-DSS, HIPAA, SOC 2, and other compliance frameworks
5. **Domain-Based Filtering**: Block access to malicious domains, enforce acceptable use policies, and prevent DNS-based attacks
6. **Multi-Account Security**: Deploy centralized firewall policies across multiple AWS accounts using AWS Firewall Manager
7. **Micro-Segmentation**: Inspect east-west traffic between VPCs, subnets, and workloads for internal threat detection
8. **Internet Gateway Protection**: Filter malicious traffic before it reaches EC2 instances and other VPC resources
9. **VPN and Direct Connect Security**: Inspect traffic from on-premises networks connecting via VPN or AWS Direct Connect
10. **Threat Intelligence Integration**: Block traffic from known malicious IP addresses and domains using threat intelligence feeds

## Best Practices

### Firewall Deployment and Architecture

1. **Deploy in Dedicated Inspection VPC**: Create a centralized inspection VPC with Network Firewall for hub-and-spoke architectures
2. **Multi-AZ Deployment**: Always deploy firewall endpoints in at least two availability zones for high availability
3. **Subnet Sizing**: Allocate dedicated /28 subnets for firewall endpoints in each AZ to ensure sufficient IP address space
4. **Centralized Architecture**: Use Transit Gateway with inspection VPC for centralized traffic inspection across multiple VPCs
5. **Separate Inspection and Application VPCs**: Isolate firewall infrastructure from application workloads for security and performance
6. **Route Table Configuration**: Configure route tables to direct traffic through firewall endpoints for inspection
7. **Asymmetric Routing Prevention**: Design routing to ensure both directions of traffic flow through the same firewall endpoint

### Rule Configuration and Management

1. **Start with Deny-All**: Begin with default deny-all policy and explicitly allow required traffic for security-first approach
2. **Use Stateful Rules for Connections**: Apply stateful rules for connection-oriented protocols (TCP, HTTP, HTTPS) for better performance
3. **Stateless for High-Performance**: Use stateless rules for simple packet filtering requiring maximum throughput
4. **Domain Lists for Egress**: Implement domain filtering using domain lists for controlling outbound HTTPS traffic
5. **Organize with Rule Groups**: Create reusable rule groups by function (web traffic, database access, admin access) for consistency
6. **Rule Evaluation Order**: Use strict order evaluation for precise control; default action order for simpler policies
7. **Test Rules in Non-Production**: Validate new rules in development/staging environments before deploying to production
8. **Suricata Rule Syntax**: Use Suricata-compatible rule strings for advanced IDS/IPS capabilities and threat detection
9. **Regular Rule Updates**: Keep Suricata signatures updated to protect against latest threats and vulnerabilities
10. **Document Rule Purpose**: Add descriptions to rules and rule groups explaining business justification and affected traffic

### Security and Compliance

1. **Enable Delete Protection**: Always enable delete protection for production firewalls to prevent accidental deletion
2. **Use KMS Encryption**: Encrypt firewall configuration data with customer-managed KMS keys for compliance requirements
3. **Enable All Logging**: Log both ALERT and FLOW types to CloudWatch and S3 for comprehensive security monitoring
4. **Implement Resource Policies**: Use resource policies to control which accounts can share and use rule groups
5. **Least Privilege Access**: Grant minimal IAM permissions required for firewall management and log access
6. **Network Segmentation**: Use firewall to enforce network segmentation boundaries between different security zones
7. **Regularly Review Rules**: Conduct quarterly reviews of firewall rules to remove obsolete rules and identify gaps
8. **Enable Policy Change Protection**: Protect production firewall policies from accidental modifications
9. **Compliance Logging**: Retain firewall logs for compliance-required periods (typically 90 days to 7 years)
10. **Audit Trail**: Enable CloudTrail logging for all Network Firewall API calls for security auditing

### Performance and Optimization

1. **Right-Size Throughput**: Monitor firewall metrics and scale throughput capacity based on traffic patterns
2. **Use Stateless for Volume**: Apply stateless rules for high-volume, simple filtering to reduce processing overhead
3. **Optimize Rule Order**: Place most frequently matched rules earlier in strict order evaluation for better performance
4. **Avoid Over-Inspection**: Don't inspect trusted internal traffic that doesn't require deep packet inspection
5. **Monitor Packet Loss**: Track packet loss metrics and increase firewall capacity if consistent loss is observed
6. **Distributed Deployment**: For very high throughput, deploy multiple firewalls across different VPCs or regions
7. **Connection Limits**: Understand connection limits (up to 30,000 concurrent connections per AZ) and plan capacity accordingly

### Logging and Monitoring

1. **Enable Dual Logging Destinations**: Send logs to both CloudWatch (real-time analysis) and S3 (long-term storage)
2. **Structured Log Analysis**: Use CloudWatch Logs Insights to query and analyze firewall logs for security events
3. **Set Up CloudWatch Alarms**: Create alarms for blocked traffic spikes, rule violations, and firewall health metrics
4. **Flow Logs for Forensics**: Enable flow logs for network forensics and troubleshooting connectivity issues
5. **Alert Logs for Threats**: Monitor alert logs continuously for IDS/IPS signatures indicating potential attacks
6. **Log Retention Policies**: Set appropriate retention periods based on compliance requirements (90-365 days typical)
7. **Integrate with SIEM**: Forward logs to security information and event management (SIEM) systems for correlation
8. **Dashboard Key Metrics**: Create dashboards showing blocked traffic, top sources/destinations, and rule hit counts
9. **Regular Log Review**: Schedule regular reviews of firewall logs to identify patterns and potential security issues

### Cost Optimization

1. **Right-Size Firewall Capacity**: Start with minimum required capacity and scale based on actual traffic patterns
2. **Optimize Rule Groups**: Consolidate similar rules to reduce complexity and potential processing overhead
3. **S3 Lifecycle Policies**: Apply S3 lifecycle policies to transition old logs to Glacier for cost-effective long-term storage
4. **CloudWatch Log Retention**: Set appropriate log retention to balance security needs with storage costs
5. **Centralized Deployment**: Use centralized inspection VPC to share firewall costs across multiple workload VPCs
6. **Monitor Unused Rules**: Regularly audit and remove rules that never match traffic to reduce policy complexity
7. **Evaluate Regional Costs**: Consider AWS Network Firewall pricing variations across regions for multi-region deployments

### High Availability and Disaster Recovery

1. **Multi-Region Deployment**: Deploy firewalls in multiple regions for disaster recovery and geographic distribution
2. **Backup Firewall Policies**: Export and store firewall policies and rule configurations in version control
3. **Automated Recovery**: Use Terraform to enable rapid firewall recreation in disaster recovery scenarios
4. **Health Monitoring**: Implement health checks and automatic alerting for firewall endpoint failures
5. **Capacity Buffer**: Maintain 20-30% capacity buffer to handle traffic spikes and AZ failures
6. **Test Failover**: Regularly test AZ failover scenarios to ensure routing and traffic flow work correctly
7. **Document Recovery Procedures**: Maintain detailed runbooks for firewall recovery and failover procedures

### Deployment and Operations

1. **Infrastructure as Code**: Manage all firewall resources through Terraform for consistency and reproducibility
2. **Version Control Policies**: Store firewall policies and rules in Git for change tracking and rollback capability
3. **Staged Rollouts**: Deploy rule changes to development, staging, then production environments progressively
4. **Change Management**: Require approval workflows for production firewall policy changes
5. **Tagging Strategy**: Apply consistent tags including environment, application, cost-center, and compliance-scope
6. **Module Version Pinning**: Pin module version in production: `version = "~> 2.0"` to prevent unexpected changes
7. **Automated Testing**: Implement automated tests to validate firewall rules allow expected traffic and block threats
8. **Firewall Manager for Scale**: Use AWS Firewall Manager to deploy and manage policies across multiple accounts
9. **Separate Firewall Accounts**: Consider dedicated security accounts for firewall resources in multi-account architectures
10. **Regular Updates**: Keep Terraform module and AWS provider versions updated for latest features and security fixes

### Integration Patterns

1. **Transit Gateway Integration**: Use TGW with inspection VPC for centralized inspection of inter-VPC traffic
2. **VPC Routing**: Configure route tables with firewall endpoint routes for transparent traffic interception
3. **Internet Gateway Protection**: Route all internet-bound traffic through firewall before reaching IGW
4. **NAT Gateway Placement**: Place NAT gateways behind firewall for egress traffic inspection
5. **VPN Integration**: Route VPN traffic through firewall for inspection of on-premises to AWS traffic
6. **Direct Connect Filtering**: Inspect Direct Connect traffic using firewall for hybrid cloud security
7. **GuardDuty Integration**: Correlate Network Firewall logs with GuardDuty findings for comprehensive threat detection
8. **Security Hub Integration**: Send firewall security findings to AWS Security Hub for centralized security monitoring

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-network-firewall
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/network-firewall/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-network-firewall/tree/master/examples
- **AWS Network Firewall Documentation**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/what-is-aws-network-firewall.html
- **Network Firewall API Reference**: https://docs.aws.amazon.com/network-firewall/latest/APIReference/Welcome.html
- **Suricata Documentation**: https://suricata.io/documentation/
- **Stateful Rules**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/stateful-rule-groups-suricata.html
- **Stateless Rules**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/stateless-rule-groups.html
- **Domain Filtering**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/stateful-rule-groups-domain-names.html
- **Logging Configuration**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/firewall-logging.html
- **Best Practices**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/best-practices.html
- **Deployment Architectures**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/architectures.html
- **AWS Firewall Manager**: https://docs.aws.amazon.com/waf/latest/developerguide/fms-chapter.html
- **Network Firewall Pricing**: https://aws.amazon.com/network-firewall/pricing/
- **Security Best Practices**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/security-best-practices.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Subnet Planning**: Ensure dedicated /28 subnets exist in each AZ for firewall endpoints before deployment
2. **Rule Configuration**: Define either stateful or stateless rule groups based on traffic inspection requirements
3. **Logging Setup**: Always enable both ALERT and FLOW logging to CloudWatch and S3 for comprehensive monitoring
4. **KMS Encryption**: Use customer-managed KMS keys for production firewalls to meet compliance requirements
5. **Multi-AZ Deployment**: Configure subnet mappings for at least two availability zones for high availability
6. **Delete Protection**: Enable delete protection for production firewalls to prevent accidental deletion
7. **Rule Evaluation Order**: Choose strict order for precise control or default action order for simpler policies
8. **Stateful vs Stateless**: Use stateful rules for connection-oriented traffic and stateless for high-throughput filtering
9. **Domain Filtering**: Implement domain lists for controlling outbound HTTPS traffic by FQDN
10. **Firewall Policy**: Create comprehensive firewall policy with appropriate default actions and rule group references
11. **Tagging Strategy**: Apply consistent tags for environment, application, compliance-scope, and cost tracking
12. **Routing Configuration**: Update VPC route tables to direct traffic through firewall endpoints for inspection
13. **Monitoring Setup**: Create CloudWatch alarms for blocked traffic, rule violations, and firewall health metrics
14. **Centralized Architecture**: Consider centralized inspection VPC with Transit Gateway for multi-VPC environments
15. **Testing**: Validate firewall rules in non-production environments before deploying to production
