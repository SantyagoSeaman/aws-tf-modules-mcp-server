---
module_name: route53
keywords: [route53, dns, hosted-zone, domain, nameserver, records, routing-policy, geolocation, weighted-routing, failover, latency-routing, alias-records, private-zone, public-zone, dnssec, delegation-sets, resolver-endpoint, resolver-firewall, cross-account, vpc-association, mx-records, cname, a-record, aaaa-record, txt-record, srv-record, ptr-record, ns-record, soa-record, caa-record, multivalue-routing, geoproximity-routing, health-checks, traffic-management, dns-query-logging, domain-registration, subdomain, zone-association, resolver-rules, dns-filtering, inbound-resolver, outbound-resolver, hybrid-dns, on-premises-dns, dns-firewall, domain-list, query-routing, do53, doh, dns-over-https, ipv4, ipv6, dual-stack, kms-encryption, ram-sharing]
---

# Terraform AWS Route53 Module

## Module Information

- **Module Name**: `route53`
- **Source**: `terraform-aws-modules/route53/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-route53
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/route53/aws/latest
- **Latest Version**: 6.1.0
- **Purpose**: Terraform module that creates and manages AWS Route53 resources including hosted zones, DNS records, resolver endpoints, and firewall rules
- **Service**: AWS Route 53 (Domain Name System)
- **Category**: Networking, DNS Management, Security
- **Keywords**: route53, dns, hosted-zone, domain, nameserver, records, routing-policy, geolocation, weighted-routing, failover, latency-routing, alias-records, private-zone, public-zone, dnssec, delegation-sets, resolver-endpoint, resolver-firewall, cross-account, vpc-association, dns-query-logging, resolver-rules, dns-filtering, hybrid-dns, dns-firewall
- **Use For**: Multi-region application routing, domain name management, hybrid cloud DNS resolution, DNS-based failover and disaster recovery, geolocation-based content delivery, weighted traffic distribution, private internal DNS for VPCs, cross-account DNS management, DNS security and filtering, microservices service discovery, blue-green deployments, canary releases

## Description

The Terraform AWS Route53 module provides comprehensive infrastructure-as-code capabilities for managing AWS Route53 DNS services. It enables creation and management of both public and private hosted zones, DNS records with advanced routing policies, DNSSEC configurations, and Route53 Resolver components. The module supports complex DNS architectures including hybrid cloud scenarios where on-premises networks need to resolve AWS resources and vice versa.

This module simplifies DNS management by abstracting the complexity of Route53 configurations while providing flexibility for advanced use cases. It supports all major DNS record types (A, AAAA, CNAME, MX, TXT, SRV, PTR, NS, CAA) and advanced routing policies including geolocation, weighted, failover, latency-based, multivalue, and geoproximity routing. The module also handles VPC associations for private zones, enabling secure internal DNS resolution within AWS networks.

The module includes three specialized submodules for managing delegation sets (reusable name server collections), resolver endpoints (for hybrid DNS resolution between AWS and on-premises networks), and resolver firewall rule groups (for DNS-based security filtering). These components work together to provide enterprise-grade DNS infrastructure with support for cross-account sharing, DNSSEC for enhanced security, and flexible traffic management capabilities.

## Key Features

- **Public Hosted Zones**: Create and manage publicly accessible DNS zones for internet-facing domains
- **Private Hosted Zones**: Set up internal DNS zones associated with specific VPCs for private resource resolution
- **Advanced Routing Policies**: Support for geolocation, weighted, failover, latency-based, multivalue, and geoproximity routing
- **DNSSEC Support**: Enable DNS Security Extensions with KMS key management for enhanced DNS security
- **Alias Records**: Native support for AWS service aliases (CloudFront, ELB, S3, API Gateway)
- **Cross-Account Zone Association**: Authorize and associate hosted zones across different AWS accounts
- **VPC Associations**: Flexible VPC association management for private hosted zones
- **Delegation Sets**: Reusable name server collections for consistent DNS delegation across multiple zones
- **Resolver Endpoints**: Inbound and outbound DNS resolution for hybrid cloud architectures
- **Resolver Firewall**: DNS-level security filtering with customizable allow, block, and override rules
- **Multiple Record Types**: Full support for A, AAAA, CNAME, MX, TXT, SRV, PTR, NS, SOA, CAA records
- **Health Checks**: Integrate Route53 health checks with routing policies for automated failover
- **DNS Query Logging**: Enable query logging for auditing and troubleshooting
- **Resource Access Manager (RAM) Integration**: Share resolver firewall rules across accounts and organizations
- **Dual-Stack Support**: IPv4, IPv6, and dual-stack configurations for resolver endpoints
- **DNS Protocols**: Support for Do53 (DNS over port 53) and DoH (DNS over HTTPS)
- **Flexible Tagging**: Comprehensive tag management for cost allocation and resource organization
- **Customizable Timeouts**: Configure timeouts for create, update, and delete operations
- **Security Group Management**: Automated security group creation for resolver endpoints with customizable rules

## Main Use Cases

1. **Multi-Region Application Routing**: Distribute traffic across multiple regions using latency-based or geolocation routing policies
2. **DNS-Based Failover**: Implement automatic failover to backup resources using health checks and failover routing
3. **Hybrid Cloud DNS Resolution**: Enable seamless DNS resolution between AWS and on-premises data centers using resolver endpoints
4. **Microservices Service Discovery**: Provide internal DNS for service-to-service communication in containerized environments
5. **Traffic Distribution and Load Balancing**: Use weighted routing policies for gradual rollouts, canary deployments, or A/B testing
6. **DNS Security and Filtering**: Block malicious domains and enforce DNS-based security policies using resolver firewall
7. **Private VPC DNS Management**: Create isolated internal DNS namespaces for private resources within VPCs
8. **Cross-Account DNS Management**: Centralize DNS management while sharing zones and resolver rules across multiple AWS accounts
9. **Geolocation-Based Content Delivery**: Route users to region-specific endpoints based on geographic location
10. **DNSSEC-Enabled Secure DNS**: Implement cryptographically signed DNS responses to prevent DNS spoofing and cache poisoning

## Submodules

### 1. delegation-sets

- **Purpose**: Creates AWS Route53 delegation sets for reusable name server collections across multiple hosted zones
- **Source**: `terraform-aws-modules/route53/aws//modules/delegation-sets`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/route53/aws/latest/submodules/delegation-sets
- **Key Features**: Reusable name servers, reference name assignment, tag support, delegation set ID and name server outputs
- **Use Cases**: Consistent DNS delegation across domains, simplified multi-domain management, domain registrar configuration, DNS migration strategies

### 2. resolver-endpoint

- **Purpose**: Creates Route53 Resolver endpoints for hybrid DNS resolution between AWS and on-premises networks
- **Source**: `terraform-aws-modules/route53/aws//modules/resolver-endpoint`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/route53/aws/latest/submodules/resolver-endpoint
- **Key Features**: Inbound/outbound endpoints, dual-stack support, DoH and Do53 protocols, automated security group creation
- **Use Cases**: Hybrid cloud DNS resolution, on-premises to AWS DNS queries, AWS to on-premises DNS forwarding, multi-cloud DNS integration

### 3. resolver-firewall-rule-group

- **Purpose**: Creates Route53 Resolver firewall rule groups for DNS-based security filtering and domain blocking
- **Source**: `terraform-aws-modules/route53/aws//modules/resolver-firewall-rule-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/route53/aws/latest/submodules/resolver-firewall-rule-group
- **Key Features**: Block/allow/override rules, domain lists, cross-account sharing via RAM, priority-based rule evaluation
- **Use Cases**: Malicious domain blocking, DNS exfiltration prevention, compliance-driven DNS filtering, parental controls

## Submodule 1: delegation-sets

### Description

The delegation-sets submodule creates and manages AWS Route53 delegation sets, which are collections of authoritative name servers that can be reused across multiple hosted zones. Delegation sets ensure consistent name server assignments when managing multiple domains, simplifying DNS configuration at domain registrars and providing a stable DNS infrastructure for domain migrations or multi-domain architectures.

### Key Features

- Reusable name server collections for multiple hosted zones
- Optional reference names for easier identification and management
- Support for custom tagging for resource organization
- Outputs delegation set IDs and associated name servers
- Enables consistent DNS delegation across domain portfolios
- Simplifies domain registrar configuration with stable name servers

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether delegation set resources should be created |
| `delegation_sets` | `map(object)` | `{}` | Map of delegation set configurations with optional reference names |
| `tags` | `map(string)` | `{}` | Map of tags to assign to delegation set resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `route53_delegation_set_id` | Unique identifier for the created delegation set |
| `route53_delegation_set_name_servers` | List of authoritative name servers in the delegation set |
| `route53_delegation_set_reference_name` | Reference name assigned to the delegation set |

### Usage Example

```hcl
module "delegation_sets" {
  source = "terraform-aws-modules/route53/aws//modules/delegation-sets"

  delegation_sets = {
    "production_domains" = {
      reference_name = "prod-dns"
    }
    "staging_domains" = {
      reference_name = "staging-dns"
    }
  }

  tags = {
    Environment = "production"
    Project     = "dns-infrastructure"
    ManagedBy   = "terraform"
  }
}

# Output the name servers for domain registrar configuration
output "prod_name_servers" {
  description = "Name servers for production domain delegation"
  value       = module.delegation_sets.route53_delegation_set_name_servers["production_domains"]
}
```

## Submodule 2: resolver-endpoint

### Description

The resolver-endpoint submodule creates AWS Route53 Resolver endpoints that enable hybrid DNS resolution between AWS VPCs and on-premises networks. It supports both inbound endpoints (allowing on-premises systems to resolve AWS-hosted DNS names) and outbound endpoints (allowing AWS resources to resolve on-premises DNS names). The submodule includes automated security group creation with customizable ingress and egress rules, and supports modern DNS protocols including DNS over HTTPS (DoH).

### Key Features

- Inbound and outbound resolver endpoint creation
- IPv4, IPv6, and dual-stack support
- DNS over port 53 (Do53) and DNS over HTTPS (DoH) protocols
- Automated security group creation with customizable rules
- Multiple IP address configuration per endpoint
- Integration with resolver rules for outbound query forwarding
- VPC subnet association management
- Comprehensive tagging support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether resolver endpoint resources should be created |
| `direction` | `string` | `""` | Direction of DNS queries (INBOUND or OUTBOUND) |
| `type` | `string` | `"IPV4"` | IP address type (IPV4, IPV6, or DUALSTACK) |
| `protocols` | `list(string)` | `["Do53"]` | List of DNS protocols (Do53, DoH) |
| `ip_address` | `map(object)` | `{}` | Map of subnet IDs and optional IP addresses for endpoint network interfaces |
| `security_group_ingress_rules` | `map(object)` | `{}` | Security group ingress rules for inbound traffic |
| `security_group_egress_rules` | `map(object)` | `{}` | Security group egress rules for outbound traffic |
| `vpc_id` | `string` | `""` | VPC ID where the resolver endpoint will be created |
| `name` | `string` | `""` | Name identifier for the resolver endpoint |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Amazon Resource Name (ARN) of the resolver endpoint |
| `id` | Unique identifier of the resolver endpoint |
| `ip_addresses` | List of IP addresses assigned to the resolver endpoint |
| `security_group_id` | ID of the security group created for the resolver endpoint |
| `host_vpc_id` | VPC ID where the resolver endpoint is deployed |

### Usage Examples

#### Example 1: Inbound Resolver Endpoint

```hcl
module "inbound_resolver" {
  source = "terraform-aws-modules/route53/aws//modules/resolver-endpoint"

  name      = "inbound-resolver"
  direction = "INBOUND"
  type      = "IPV4"
  protocols = ["Do53", "DoH"]

  vpc_id = "vpc-0123456789abcdef0"

  ip_address = {
    subnet_1 = {
      subnet_id = "subnet-0123456789abcdef0"
    }
    subnet_2 = {
      subnet_id = "subnet-0123456789abcdef1"
    }
  }

  security_group_ingress_rules = {
    allow_dns_from_onprem = {
      from_port   = 53
      to_port     = 53
      ip_protocol = "udp"
      cidr_ipv4   = "10.0.0.0/8"
      description = "Allow DNS queries from on-premises network"
    }
  }

  tags = {
    Environment = "production"
    Purpose     = "hybrid-dns"
  }
}
```

#### Example 2: Outbound Resolver Endpoint

```hcl
module "outbound_resolver" {
  source = "terraform-aws-modules/route53/aws//modules/resolver-endpoint"

  name      = "outbound-resolver"
  direction = "OUTBOUND"
  type      = "IPV4"
  protocols = ["Do53"]

  vpc_id = "vpc-0123456789abcdef0"

  ip_address = {
    subnet_1 = {
      subnet_id = "subnet-0123456789abcdef0"
    }
    subnet_2 = {
      subnet_id = "subnet-0123456789abcdef1"
    }
  }

  security_group_egress_rules = {
    allow_dns_to_onprem = {
      from_port   = 53
      to_port     = 53
      ip_protocol = "udp"
      cidr_ipv4   = "10.0.0.0/8"
      description = "Allow DNS queries to on-premises DNS servers"
    }
  }

  tags = {
    Environment = "production"
    Purpose     = "hybrid-dns-forwarding"
  }
}
```

## Submodule 3: resolver-firewall-rule-group

### Description

The resolver-firewall-rule-group submodule creates and manages Route53 Resolver firewall rule groups that provide DNS-level security filtering. It enables organizations to block, allow, or override DNS responses for specific domains, protecting against malicious domains, data exfiltration, and enforcing compliance policies. The submodule supports cross-account sharing via AWS Resource Access Manager (RAM), allowing centralized DNS security policies across multiple accounts and organizational units.

### Key Features

- DNS domain allow, block, and override rules
- Customizable domain lists for flexible rule management
- Priority-based rule evaluation
- Cross-account and cross-organization sharing via AWS RAM
- NODATA, NXDOMAIN, and OVERRIDE block response types
- Custom DNS override responses
- Comprehensive tagging for policy organization
- Integration with VPC resolver associations

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether firewall rule group resources should be created |
| `name` | `string` | `""` | Name identifier for the firewall rule group |
| `rules` | `map(object)` | `{}` | Map of firewall rule configurations including action, priority, and domains |
| `ram_resource_associations` | `map(object)` | `{}` | Configuration for sharing rule groups via AWS RAM |
| `tags` | `map(string)` | `{}` | Map of tags to assign to firewall resources |

**Rules Object Structure**:
- `name`: Rule name
- `priority`: Rule evaluation priority (100-9900)
- `action`: Action to take (ALLOW, BLOCK, ALERT, OVERRIDE)
- `block_response`: Response type for BLOCK action (NODATA, NXDOMAIN, OVERRIDE)
- `block_override_domain`: Custom domain for OVERRIDE block response
- `block_override_ttl`: TTL for OVERRIDE response
- `domains`: List of domain names or domain list IDs

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Amazon Resource Name (ARN) of the firewall rule group |
| `id` | Unique identifier of the firewall rule group |
| `domain_lists` | Map of created resolver firewall domain lists |
| `rules` | Map of created resolver firewall rules |
| `share_status` | Sharing status of the rule group when shared via RAM |

### Usage Examples

#### Example 1: Basic Firewall Rule Group

```hcl
module "dns_firewall" {
  source = "terraform-aws-modules/route53/aws//modules/resolver-firewall-rule-group"

  name = "security-dns-firewall"

  rules = {
    block_malicious = {
      name           = "block-malicious-domains"
      priority       = 100
      action         = "BLOCK"
      block_response = "NXDOMAIN"
      domains = [
        "malicious-site.com.",
        "phishing-domain.net.",
        "cryptominer.org."
      ]
    }

    allow_corporate = {
      name     = "allow-corporate-domains"
      priority = 200
      action   = "ALLOW"
      domains = [
        "corporate.example.com.",
        "*.internal.example.com."
      ]
    }

    alert_suspicious = {
      name     = "alert-suspicious-domains"
      priority = 300
      action   = "ALERT"
      domains = [
        "suspicious-domain.com."
      ]
    }
  }

  tags = {
    Environment = "production"
    SecurityLevel = "high"
    ManagedBy = "security-team"
  }
}
```

#### Example 2: Firewall with Cross-Account Sharing

```hcl
module "shared_dns_firewall" {
  source = "terraform-aws-modules/route53/aws//modules/resolver-firewall-rule-group"

  name = "organization-dns-firewall"

  rules = {
    block_data_exfiltration = {
      name           = "block-data-exfiltration"
      priority       = 110
      action         = "BLOCK"
      block_response = "OVERRIDE"
      block_override_domain = "blocked.example.com."
      block_override_ttl = 60
      domains = [
        "file-sharing-site.com.",
        "paste-bin.com.",
        "anonymous-upload.net."
      ]
    }
  }

  ram_resource_associations = {
    share_with_organization = {
      resource_share_arn = "arn:aws:ram:us-east-1:123456789012:resource-share/example-share"
    }
  }

  tags = {
    Environment = "organization-wide"
    SecurityPolicy = "dns-filtering"
  }
}
```

## Best Practices

### Hosted Zone Management

1. **Use Private Zones for Internal Resources**: Create private hosted zones for internal application DNS to prevent exposure of internal resource names to the public internet
2. **Enable DNSSEC for Public Zones**: Implement DNSSEC with KMS key management for public zones to protect against DNS spoofing and cache poisoning attacks
3. **Separate Zones by Environment**: Maintain separate hosted zones for production, staging, and development environments to prevent configuration errors
4. **Use Delegation Sets for Multi-Domain Management**: When managing multiple domains, use delegation sets to maintain consistent name server assignments across zones
5. **Document Zone Purpose**: Use descriptive names and comprehensive tags to document the purpose and ownership of each hosted zone

### DNS Record Configuration

1. **Use Alias Records for AWS Resources**: Prefer Route53 alias records over CNAME records when pointing to AWS services (ELB, CloudFront, S3) for better performance and no additional cost
2. **Set Appropriate TTL Values**: Use shorter TTLs (60-300 seconds) for records that may change frequently, and longer TTLs (3600+ seconds) for stable records to reduce query costs
3. **Implement Health Checks for Critical Records**: Attach Route53 health checks to critical DNS records to enable automatic failover and improve availability
4. **Avoid Wildcard Records in Production**: Use specific record names instead of wildcards (*) in production to maintain better control and security
5. **Use Routing Policies for Traffic Management**: Leverage weighted, latency-based, or geolocation routing policies instead of simple DNS round-robin for better traffic distribution

### Resolver Endpoint Configuration

1. **Deploy Endpoints in Multiple Subnets**: Create resolver endpoints in at least two subnets across different availability zones for high availability
2. **Use Static IP Addresses for On-Premises Integration**: Specify static IP addresses for resolver endpoints when configuring on-premises DNS forwarders for consistency
3. **Restrict Security Group Rules**: Limit security group rules to only allow DNS traffic (port 53 UDP/TCP) from trusted networks, not 0.0.0.0/0
4. **Enable DoH for Enhanced Security**: Use DNS over HTTPS (DoH) protocol when supported by clients to encrypt DNS queries in transit
5. **Monitor Resolver Query Metrics**: Enable CloudWatch metrics and logging for resolver endpoints to track query volume, latency, and failures

### DNS Firewall Configuration

1. **Implement Layered Security Rules**: Use a combination of BLOCK, ALLOW, and ALERT rules with appropriate priorities to create defense-in-depth DNS security
2. **Start with Alert Mode**: Initially deploy firewall rules in ALERT mode to understand DNS query patterns before enforcing BLOCK actions
3. **Maintain Centralized Domain Lists**: Create reusable domain lists for common security categories (malware, phishing, data exfiltration) and share via RAM
4. **Use OVERRIDE for Monitoring**: Configure OVERRIDE block responses to redirect blocked queries to a logging endpoint for security analysis
5. **Regular Rule Updates**: Regularly update domain lists with newly discovered threats from threat intelligence feeds and security advisories

### Cross-Account and Hybrid DNS

1. **Use VPC Authorization for Private Zone Sharing**: When sharing private zones across accounts, always use explicit VPC authorization instead of making zones public
2. **Implement Conditional Forwarding Rules**: Create resolver rules to forward specific domain queries to appropriate DNS servers (AWS or on-premises)
3. **Centralize DNS Management**: Use a hub-and-spoke model with a central DNS account managing shared zones and resolver rules distributed via RAM
4. **Document Domain Ownership**: Maintain clear documentation of which teams or accounts own specific DNS domains and zones
5. **Test Cross-Account Access**: Always test DNS resolution from target accounts/VPCs after configuring cross-account associations

### Security and Compliance

1. **Enable Query Logging**: Enable Route53 query logging to CloudWatch Logs or S3 for security auditing and troubleshooting
2. **Use IAM Policies for Access Control**: Implement least-privilege IAM policies for Route53 operations, restricting who can modify critical zones
3. **Encrypt Sensitive DNS Data**: Use DNSSEC for public zones and VPC-level encryption for private zones to protect DNS data integrity
4. **Regular Security Audits**: Periodically review DNS records, resolver rules, and firewall configurations for unauthorized changes or misconfigurations
5. **Implement Resource Tags**: Apply consistent tagging to all Route53 resources for cost allocation, compliance tracking, and automated governance

### Performance and Cost Optimization

1. **Use Geo-Proximity Routing for Global Applications**: Implement geoproximity routing with bias values to optimize latency for global user bases
2. **Optimize Health Check Frequency**: Balance health check frequency with cost by using appropriate intervals based on application criticality
3. **Monitor Query Metrics**: Use CloudWatch metrics to track query counts and identify opportunities for TTL optimization or caching improvements
4. **Consolidate Zones Where Possible**: Reduce the number of hosted zones by using subdomains within existing zones to minimize costs
5. **Use Resolver Endpoints Efficiently**: Share resolver endpoints across multiple VPCs using VPC associations instead of creating redundant endpoints

### Operational Excellence

1. **Implement Infrastructure as Code**: Always use Terraform to manage Route53 resources for version control, peer review, and disaster recovery
2. **Use Module Variables for Flexibility**: Parameterize zone names, VPC IDs, and other environment-specific values using Terraform variables
3. **Test DNS Changes in Non-Production**: Validate all DNS changes in staging environments before applying to production zones
4. **Monitor Resolver Health**: Set up CloudWatch alarms for resolver endpoint availability, query failure rates, and latency thresholds
5. **Document DNS Architecture**: Maintain architecture diagrams showing DNS hierarchy, resolver flows, and cross-account relationships

### High Availability and Disaster Recovery

1. **Implement Multi-Region Failover**: Use Route53 health checks with failover routing to automatically route traffic away from failed regions
2. **Backup DNS Configurations**: Export zone files or maintain Terraform state in version control for disaster recovery scenarios
3. **Use Calculated Health Checks**: Combine multiple health checks using calculated health checks for more sophisticated failover logic
4. **Test Failover Procedures**: Regularly test DNS failover by simulating endpoint failures to validate configuration
5. **Maintain Secondary DNS Providers**: For critical public domains, consider maintaining secondary DNS providers outside AWS for resilience

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-route53
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/route53/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-route53/tree/master/examples
- **AWS Route53 Documentation**: https://docs.aws.amazon.com/route53/
- **Route53 Developer Guide**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html
- **Route53 Resolver Documentation**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html
- **DNSSEC in Route53**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring-dnssec.html
- **Route53 Resolver DNS Firewall**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall.html
- **Route53 Health Checks**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html
- **Route53 Traffic Policies**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/traffic-policies.html
- **Route53 Pricing**: https://aws.amazon.com/route53/pricing/
- **AWS Well-Architected - Reliability**: https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html
- **Hybrid Cloud DNS Architecture**: https://aws.amazon.com/blogs/networking-and-content-delivery/hybrid-cloud-dns-solutions-for-amazon-vpc/
- **Route53 Best Practices**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/best-practices.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Start with Zone Structure**: Begin by creating hosted zones before adding records; private zones require VPC associations
2. **Use Conditional Logic**: Leverage the `create` variable to conditionally create resources based on environment or feature flags
3. **Implement Staged Deployments**: For record changes, consider using weighted routing policies to gradually shift traffic
4. **Validate DNS Propagation**: After creating or updating records, implement wait conditions or checks for DNS propagation before proceeding
5. **Secure Resolver Endpoints**: Always specify restrictive security group rules for resolver endpoints, never use 0.0.0.0/0 for ingress
6. **Test Firewall Rules**: Deploy DNS firewall rules in ALERT mode first, monitor for false positives, then switch to BLOCK
7. **Handle Cross-Account Dependencies**: When sharing zones or resolver rules across accounts, ensure RAM resource shares are created first
8. **Monitor Health Check Status**: For failover configurations, verify health check status before declaring deployment successful
9. **Use Terraform State Locking**: Implement state locking to prevent concurrent modifications to DNS resources
10. **Document Domain Delegation**: When creating delegation sets, output name servers for configuration at domain registrars
11. **Implement Proper Tagging**: Apply consistent tags for cost allocation, environment identification, and automated governance
12. **Validate Routing Policies**: When using complex routing policies (geolocation, weighted), verify expected behavior through testing
