# Terraform AWS Route53 Module

## Module Information

- **Module Name**: `route53`
- **Source**: `terraform-aws-modules/route53/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-route53
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/route53/aws/latest
- **Latest Version**: 6.5.0
- **Purpose**: Terraform module that creates and manages AWS Route53 hosted zones, DNS records, DNSSEC signing, delegation sets, resolver endpoints, and resolver firewall rule groups
- **Service**: AWS Route 53 (Domain Name System)
- **Category**: Networking, DNS Management, Security
- **Keywords**: route53, dns, hosted-zone, dns-records, routing-policy, alias-record, private-zone, dnssec, cross-account, resolver-endpoint, resolver-firewall, hybrid-dns, delegation-set, failover, geolocation
- **Use For**: multi-region traffic routing, DNS-based failover and disaster recovery, hybrid cloud DNS resolution, private internal DNS for VPCs, cross-account DNS management, DNS security/domain filtering, weighted/canary traffic shifting, geolocation and latency-based content delivery, DNSSEC-signed public zones, service discovery for microservices

## Description

The Terraform AWS Route53 module provisions AWS Route53 hosted zones (public or private) together with their DNS records, and optionally enables DNSSEC signing backed by a dedicated KMS key. It supports every major record type (A, AAAA, CNAME, MX, TXT, SRV, PTR, NS, CAA) and all Route53 routing policies — simple, weighted, latency-based, failover, geolocation, geoproximity, multivalue-answer, and CIDR-based — expressed through a single `records` map. Alias records to AWS services (S3 website endpoints, CloudFront, ALB/NLB, API Gateway, another record in the same zone) are supported natively.

For private zones, the module manages VPC associations, including the cross-account pattern where `aws_route53_vpc_association_authorization` is created by the zone-owning account while the actual `aws_route53_zone_association` is applied separately by the VPC-owning account. An `ignore_vpc` flag lets a zone's VPC associations be managed entirely outside Terraform (e.g. via `aws_route53_zone_association` resources) without producing disruptive diffs — switching this flag requires a `terraform state mv`/`moved` block between two zone resources because Terraform does not support conditional `lifecycle` blocks. The module can also look up an existing zone (`create_zone = false`) instead of creating one, and optionally enables Route 53 Accelerated Recovery (60-minute RTO for DNS management if us-east-1 is unavailable) on public zones.

Three independent submodules extend the root module: `delegation-sets` for reusable name-server collections shared across multiple zones, `resolver-endpoint` for hybrid DNS resolution (inbound/outbound) between AWS and on-premises networks with an auto-managed security group, and `resolver-firewall-rule-group` for DNS-level allow/block/alert filtering with optional cross-account sharing via AWS RAM. Together these cover public/private DNS, secure DNS (DNSSEC), hybrid connectivity, and DNS security in one module family.

## Key Features

- **Public & Private Hosted Zones**: Create new zones or look up existing ones (`create_zone = false`) for internet-facing or VPC-internal DNS
- **All Routing Policies**: Weighted, latency, failover, geolocation, geoproximity (region or lat/long with bias), multivalue-answer, and CIDR-collection routing via one `records` map
- **Alias Records**: Native aliasing to AWS services (S3, CloudFront, ELB/ALB/NLB, API Gateway) and same-zone self-references, with `evaluate_target_health`
- **DNSSEC with Managed KMS Key**: `enable_dnssec` provisions `aws_route53_key_signing_key` + `aws_route53_hosted_zone_dnssec`, optionally creating a dedicated KMS key (module `terraform-aws-modules/kms/aws`) or accepting an existing `dnssec_kms_key_arn`; key name is configurable via `dnssec_key_signing_key_name`
- **Route 53 Accelerated Recovery**: `enable_accelerated_recovery` gives public zones a 60-minute RTO if `us-east-1` is unavailable
- **Cross-Account VPC Association**: `vpc_association_authorizations` creates authorizations for external accounts/VPCs; `ignore_vpc` decouples zone VPC state from externally-managed associations
- **Delegation Sets Submodule**: Reusable, stable name-server sets assignable to multiple public zones via `delegation_set_id`
- **Resolver Endpoint Submodule**: Inbound/outbound Route53 Resolver endpoints, IPv4/IPv6/dual-stack, Do53/DoH/DoH-FIPS protocols, auto-created security group with port-53 TCP/UDP rules, and resolver rules + VPC associations
- **Resolver Firewall Submodule**: DNS firewall rule groups with ALLOW/BLOCK/ALERT actions, NODATA/NXDOMAIN/OVERRIDE block responses, domain lists, and RAM sharing across accounts
- **Flexible Timeouts & Tagging**: Per-record and per-zone `timeouts` blocks; consistent `tags` propagation across all resources

## Main Use Cases

1. **Multi-Region Application Routing**: Distribute traffic using latency-based or geolocation routing policies
2. **DNS-Based Failover**: Automatic failover to backup resources using health checks and PRIMARY/SECONDARY failover routing
3. **Hybrid Cloud DNS Resolution**: Resolve DNS between AWS VPCs and on-premises networks via inbound/outbound resolver endpoints
4. **Private VPC DNS**: Internal namespaces for service-to-service resolution within one or more VPCs
5. **Cross-Account DNS Management**: Centralize zones/resolver rules in a hub account and authorize associations from spoke accounts
6. **Canary/Blue-Green Deployments**: Shift traffic gradually with weighted routing policies
7. **DNS Security & Filtering**: Block malicious or unauthorized domains, alert on suspicious queries, using resolver firewall rule groups
8. **DNSSEC-Signed Public Zones**: Protect public domains against spoofing/cache poisoning with signed DNSKEY/DS records
9. **Domain Portfolio Management**: Keep consistent name servers across many zones using delegation sets
10. **Disaster Recovery for DNS Management**: Enable Accelerated Recovery so record changes keep working during a `us-east-1` outage

## Submodules

### 1. delegation-sets

- **Purpose**: Creates reusable AWS Route53 delegation sets (name-server collections) assignable to multiple hosted zones
- **Source**: `terraform-aws-modules/route53/aws//modules/delegation-sets`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/route53/aws/latest/submodules/delegation-sets
- **Key Features**: Reusable name servers, optional reference names, tag support
- **Use Cases**: Consistent DNS delegation across a domain portfolio, simplified registrar configuration, DNS migration

### 2. resolver-endpoint

- **Purpose**: Creates a Route53 Resolver endpoint (inbound or outbound) plus its security group for hybrid DNS resolution
- **Source**: `terraform-aws-modules/route53/aws//modules/resolver-endpoint`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/route53/aws/latest/submodules/resolver-endpoint
- **Key Features**: Inbound/outbound endpoints, IPv4/IPv6/dual-stack, Do53/DoH/DoH-FIPS protocols, auto-managed security group, resolver rules + associations
- **Use Cases**: On-premises-to-AWS DNS queries, AWS-to-on-premises forwarding, multi-VPC/multi-cloud DNS integration

### 3. resolver-firewall-rule-group

- **Purpose**: Creates a Route53 Resolver firewall rule group with domain lists and rules for DNS-level security filtering
- **Source**: `terraform-aws-modules/route53/aws//modules/resolver-firewall-rule-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/route53/aws/latest/submodules/resolver-firewall-rule-group
- **Key Features**: ALLOW/BLOCK/ALERT rules, NODATA/NXDOMAIN/OVERRIDE block responses, priority-based evaluation, cross-account sharing via RAM
- **Use Cases**: Malicious-domain blocking, DNS exfiltration prevention, compliance-driven DNS filtering

## Root Module: Hosted Zones and Records

### Description

The root module creates (or looks up) an AWS Route53 hosted zone and manages its DNS records, VPC associations, and DNSSEC configuration.

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Hosted zone domain name |
| `create_zone` | `bool` | `true` | Create a new zone; set `false` to look up an existing zone (with `private_zone`/`vpc_id`) |
| `comment` | `string` | `null` | Zone comment (defaults to "Managed by Terraform") |
| `records` | `map(object)` | `{}` | DNS records keyed by name/subdomain, each with type, ttl/records or alias, and an optional routing policy block |
| `vpc` | `map(object({vpc_id, vpc_region}))` | `null` | VPC(s) to associate for a private hosted zone; conflicts with `delegation_set_id` |
| `vpc_association_authorizations` | `map(object({vpc_id, vpc_region}))` | `null` | Cross-account VPC association authorizations to create |
| `ignore_vpc` | `bool` | `false` | Ignore VPC changes post-creation so externally managed associations don't cause diffs (destructive to toggle — requires a `moved`/`state mv`) |
| `delegation_set_id` | `string` | `null` | Reusable delegation set ID for a public zone; conflicts with `vpc` |
| `enable_dnssec` | `bool` | `false` | Enable DNSSEC signing for the zone |
| `create_dnssec_kms_key` | `bool` | `true` | Create a dedicated KMS key for DNSSEC signing (via `terraform-aws-modules/kms/aws`) |
| `dnssec_kms_key_arn` | `string` | `null` | Existing KMS key ARN to use for DNSSEC; required when `create_dnssec_kms_key = false` |
| `dnssec_key_signing_key_name` | `string` | `null` | Name of the KSK; defaults to the zone name (useful for importing/adopting an existing KSK) |
| `enable_accelerated_recovery` | `bool` | `null` | Enable Route 53 Accelerated Recovery (60-min RTO) for public zones |
| `force_destroy` | `bool` | `null` | Delete all records (including externally managed ones) when destroying the zone |
| `timeouts` | `object` | `null` | Create/update/delete timeouts for the zone |
| `tags` | `map(string)` | `{}` | Tags applied to all created resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `id` | Hosted zone ID |
| `arn` | Zone ARN |
| `name_servers` | Authoritative name servers for the zone |
| `primary_name_server` | The name server that created the SOA record |
| `records` | Map of created DNS records |
| `dnssec_signing_key_ds_record` | DS record to register with the parent zone/registrar |
| `dnssec_signing_key_dnskey_record` | DNSKEY record |
| `dnssec_kms_key_arn` | ARN of the KMS key used for DNSSEC signing |

### Usage Examples

#### Example 1: Public Hosted Zone with Routing Policies

```hcl
module "zone" {
  source  = "terraform-aws-modules/route53/aws"
  version = "~> 6.5"

  name    = "example.com"
  comment = "Public zone for example.com"

  records = {
    s3 = {
      name = "s3-bucket.example.com"
      type = "A"
      alias = {
        name    = "s3-website-eu-west-1.amazonaws.com"
        zone_id = "Z1BKCTXD74EZPE"
      }
    }
    mail = {
      full_name = "example.com"
      type      = "MX"
      ttl       = 3600
      records   = ["10 mail.example.com"]
    }
    blue = {
      name           = "app"
      type           = "CNAME"
      ttl            = 5
      records        = ["blue.example.com."]
      set_identifier = "blue"
      weighted_routing_policy = {
        weight = 90
      }
    }
    green = {
      name           = "app"
      type           = "CNAME"
      ttl            = 5
      records        = ["green.example.com."]
      set_identifier = "green"
      weighted_routing_policy = {
        weight = 10
      }
    }
    failover-primary = {
      type            = "A"
      set_identifier  = "failover-primary"
      health_check_id = "d641c34c-a992-4edd-8a63-c540a4b18d0a"
      alias = {
        name    = "d3778kt32cqdww.cloudfront.net"
        zone_id = "EF3T6981F7M1"
      }
      failover_routing_policy = {
        type = "PRIMARY"
      }
    }
  }

  tags = {
    Environment = "production"
  }
}
```

#### Example 2: Private Hosted Zone with Cross-Account VPC Association

```hcl
module "zone" {
  source  = "terraform-aws-modules/route53/aws"
  version = "~> 6.5"

  name    = "internal.example.com"
  comment = "Private zone for internal.example.com"

  # Ignore VPC changes after creation to avoid disruptive diffs from
  # externally applied aws_route53_zone_association resources
  ignore_vpc = true
  vpc = {
    default = {
      vpc_id     = "vpc-0123456789abcdef0"
      vpc_region = "eu-west-1"
    }
  }

  # Authorize other accounts'/regions' VPCs to associate with this zone;
  # the association itself must be created in the VPC-owning account
  vpc_association_authorizations = {
    external_account = {
      vpc_id     = "vpc-0987654321fedcba"
      vpc_region = "eu-west-1"
    }
  }

  records = {
    db = {
      type    = "A"
      ttl     = 300
      records = ["10.0.1.100"]
    }
  }

  tags = {
    Environment = "production"
    Visibility  = "private"
  }
}
```

#### Example 3: DNSSEC-Enabled Zone with Accelerated Recovery

```hcl
module "zone" {
  source  = "terraform-aws-modules/route53/aws"
  version = "~> 6.5"

  name    = "secure.example.com"

  enable_dnssec               = true
  enable_accelerated_recovery = true

  records = {
    www = {
      type    = "A"
      ttl     = 3600
      records = ["192.168.1.1"]
    }
  }

  tags = {
    Environment = "production"
    Security    = "dnssec-enabled"
  }
}

# Publish the DS record with the domain registrar / parent zone
output "ds_record" {
  value = module.zone.dnssec_signing_key_ds_record
}
```

## Submodule 1: delegation-sets

### Description

Creates AWS Route53 delegation sets — reusable collections of four authoritative name servers — that can be assigned to multiple public hosted zones via the root module's `delegation_set_id` input, keeping name servers stable across zone re-creation or multi-domain setups.

### Key Features

- Reusable name-server collections for multiple hosted zones
- Optional reference names for identification
- Tag support
- Outputs delegation set IDs and their name servers

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the delegation set resources |
| `delegation_sets` | `map(object({reference_name}))` | `{}` | Map of delegation sets to create, keyed by a logical name |
| `tags` | `map(string)` | `{}` | Tags applied to delegation set resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `route53_delegation_set_id` | Map of delegation set IDs |
| `route53_delegation_set_name_servers` | Map of name servers per delegation set |
| `route53_delegation_set_reference_name` | Map of reference names per delegation set |

### Usage Example

```hcl
module "delegation_sets" {
  source = "terraform-aws-modules/route53/aws//modules/delegation-sets"

  delegation_sets = {
    myapp1 = {
      reference_name = "myapp1"
    }
  }

  tags = {
    Environment = "production"
  }
}

module "zone" {
  source = "terraform-aws-modules/route53/aws"

  name              = "myapp1.com"
  delegation_set_id = module.delegation_sets.route53_delegation_set_id["myapp1"]

  tags = {
    Environment = "production"
  }
}
```

## Submodule 2: resolver-endpoint

### Description

Creates a Route53 Resolver endpoint (inbound or outbound) along with a security group scoped to DNS traffic (TCP/UDP port 53), and optionally resolver rules with VPC associations for outbound forwarding to on-premises or other networks.

### Key Features

- Inbound and outbound resolver endpoints
- IPv4, IPv6, and dual-stack (`type`) with Do53, DoH, and DoH-FIPS (`protocols`)
- Auto-created security group with granular ingress/egress rule maps, or bring-your-own via `security_group_ids`
- Resolver rules (`FORWARD`/`SYSTEM`) with target IPs and VPC associations, created via the `rules` map
- Multiple subnet/IP addresses per endpoint (`ip_address` list)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `direction` | `string` | `"INBOUND"` | `INBOUND` or `OUTBOUND` |
| `type` | `string` | `null` | `IPV4`, `IPV6`, or `DUALSTACK` |
| `protocols` | `list(string)` | `[]` | DNS protocols: `Do53`, `DoH`, `DoH-FIPS` |
| `ip_address` | `list(object({subnet_id, ip, ipv6}))` | `[]` | Subnets (and optional static IPs) the endpoint uses |
| `vpc_id` | `string` | `null` | VPC ID for the auto-created security group |
| `create_security_group` | `bool` | `true` | Whether to create the security group |
| `security_group_ingress_rules` / `security_group_egress_rules` | `map(object)` | `{}` | Port-53 TCP/UDP rules added to the created security group |
| `security_group_ids` | `list(string)` | `[]` | Existing security group IDs to use instead of creating one |
| `rules` | `map(object({domain_name, rule_type, target_ip, vpc_id, ...}))` | `{}` | Resolver rules and their VPC associations (outbound only) |
| `name` | `string` | `null` | Endpoint name |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Resolver endpoint ARN |
| `id` | Resolver endpoint ID |
| `ip_addresses` | IP addresses assigned to the endpoint |
| `host_vpc_id` | VPC ID hosting the endpoint |
| `security_group_id` / `security_group_ids` | Security group(s) protecting the endpoint |
| `rules` | Resolver rules created |

### Usage Examples

#### Example 1: Inbound Resolver Endpoint

```hcl
module "resolver_endpoint" {
  source = "terraform-aws-modules/route53/aws//modules/resolver-endpoint"

  name      = "inbound-resolver"
  direction = "INBOUND"
  type      = "IPV4"
  protocols = ["Do53", "DoH"]

  vpc_id = "vpc-0123456789abcdef0"
  ip_address = [
    { subnet_id = "subnet-0123456789abcdef0" },
    { subnet_id = "subnet-0123456789abcdef1" },
  ]

  security_group_ingress_rules = {
    from_onprem = {
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

#### Example 2: Outbound Resolver Endpoint with Forwarding Rule

```hcl
module "resolver_endpoint" {
  source = "terraform-aws-modules/route53/aws//modules/resolver-endpoint"

  name      = "outbound-resolver"
  direction = "OUTBOUND"
  type      = "IPV4"
  protocols = ["Do53"]

  vpc_id = "vpc-0123456789abcdef0"
  ip_address = [
    { subnet_id = "subnet-0123456789abcdef0" },
    { subnet_id = "subnet-0123456789abcdef1" },
  ]

  security_group_egress_rules = {
    to_onprem = {
      cidr_ipv4   = "10.0.0.0/8"
      description = "Allow DNS queries to on-premises DNS servers"
    }
  }

  rules = {
    forward_onprem = {
      domain_name = "onprem.example.com."
      rule_type   = "FORWARD"
      target_ip   = [{ ip = "10.1.2.3" }]
      vpc_id      = "vpc-0123456789abcdef0"
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

Creates a Route53 Resolver firewall rule group with its domain lists and rules, providing DNS-level security filtering (block, allow, or alert on domain queries). Rule groups can be shared with other AWS accounts or across an organization via AWS Resource Access Manager (RAM).

### Key Features

- `ALLOW`, `BLOCK`, and `ALERT` rule actions with priority-based evaluation
- `NODATA`, `NXDOMAIN`, and `OVERRIDE` (with custom DNS record) block responses
- Domain lists created inline per rule (`domains`), or reference an existing/managed `firewall_domain_list_id`
- Cross-account and cross-organization sharing via `ram_resource_associations`

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Firewall rule group name |
| `rules` | `map(object({action, priority, domains, block_response, ...}))` | `{}` | Rules and their domain lists, keyed by a logical name |
| `ram_resource_associations` | `map(object({resource_share_arn}))` | `{}` | RAM resource shares to associate the rule group with |
| `tags` | `map(string)` | `{}` | Tags applied to created resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `id` | Firewall rule group ID |
| `arn` | Firewall rule group ARN |
| `domain_lists` | Map of created domain lists |
| `rules` | Map of created firewall rules |
| `share_status` | `NOT_SHARED`, `SHARED_BY_ME`, or `SHARED_WITH_ME` |

### Usage Example

```hcl
module "dns_firewall" {
  source = "terraform-aws-modules/route53/aws//modules/resolver-firewall-rule-group"

  name = "security-dns-firewall"

  rules = {
    block_malicious = {
      name           = "block-malicious-domains"
      priority       = 110
      action         = "BLOCK"
      block_response = "NXDOMAIN"
      domains        = ["malicious-site.com.", "phishing-domain.net."]
    }

    block_override = {
      priority                = 120
      action                  = "BLOCK"
      block_response          = "OVERRIDE"
      block_override_dns_type = "CNAME"
      block_override_domain   = "blocked.example.com"
      block_override_ttl      = 60
      domains                 = ["file-sharing-site.com."]
    }

    allow_corporate = {
      priority = 130
      action   = "ALLOW"
      domains  = ["corporate.example.com.", "*.internal.example.com."]
    }
  }

  ram_resource_associations = {
    share_with_org = {
      resource_share_arn = "arn:aws:ram:us-east-1:123456789012:resource-share/example-share"
    }
  }

  tags = {
    Environment   = "production"
    SecurityLevel = "high"
  }
}
```

## Best Practices

### Hosted Zone Management

1. **Use private zones for internal resources**: Keep internal application DNS in private hosted zones so internal resource names are never exposed publicly.
2. **Separate zones by environment**: Maintain distinct zones (or delegated subdomains) for production, staging, and development to prevent cross-environment record collisions.
3. **Use delegation sets for multi-domain portfolios**: Assign a shared `delegation_set_id` when many public zones must keep consistent, stable name servers at the registrar.
4. **Prefer `create_zone = false` for existing zones**: When a zone already exists outside Terraform (e.g., root domain owned by another team), look it up instead of re-creating it to avoid ownership conflicts.
5. **Enable `force_destroy` only where deletion is expected**: Set it explicitly so zone teardown in ephemeral environments does not fail on leftover records, but avoid it on production zones.

### DNS Record Configuration

1. **Prefer alias records for AWS targets**: Use `alias` instead of CNAME for AWS resources (S3, CloudFront, ELB) — no extra query charge and works at the zone apex.
2. **Set TTLs to match change frequency**: Use short TTLs (60-300s) for records that may fail over or change often, longer TTLs (3600s+) for stable records to reduce resolver load.
3. **Attach health checks for automated failover**: Pair `failover_routing_policy` or `latency_routing_policy` with `health_check_id` so unhealthy targets are automatically removed from rotation.
4. **Use `set_identifier` consistently**: Every record participating in a routing policy (weighted, failover, latency, geolocation, geoproximity, multivalue, CIDR) needs a unique `set_identifier` within its record set.
5. **Avoid unmanaged wildcard records in production**: Prefer explicit record names for auditability; use routing policies rather than round-robin lists for controlled traffic shifting.

### DNSSEC

1. **Enable DNSSEC only on zones you fully control**: Enabling and later disabling DNSSEC on a live zone can cause temporary resolution failures if the parent-zone DS record isn't updated in sync.
2. **Publish the DS record promptly**: After `enable_dnssec = true`, retrieve `dnssec_signing_key_ds_record` and register it with the domain registrar/parent zone without delay.
3. **Reuse an existing KSK name when adopting DNSSEC**: Set `dnssec_key_signing_key_name` to match an already-published key name to avoid an unnecessary key rollover.
4. **Bring your own KMS key for centralized key management**: Set `create_dnssec_kms_key = false` and supply `dnssec_kms_key_arn` when KMS keys are managed by a separate security/platform team.

### Resolver Endpoint Configuration

1. **Deploy across at least two subnets/AZs**: Provide two or more entries in `ip_address` for high availability of the resolver endpoint.
2. **Restrict security group rules to DNS traffic and trusted CIDRs**: Never allow `0.0.0.0/0`; scope ingress/egress rules to the specific on-premises or peer VPC CIDR ranges.
3. **Use DoH where clients support it**: Prefer `DoH`/`DoH-FIPS` protocols for encrypted DNS in transit when the resolver clients support it.
4. **Keep outbound resolver rules scoped**: Use specific `domain_name` values per `FORWARD` rule instead of overly broad forwarding to limit blast radius of misconfiguration.

### DNS Firewall Configuration

1. **Start new rule groups in `ALERT` mode**: Validate real DNS query patterns against a rule group before switching key rules to `BLOCK`, to avoid breaking legitimate traffic.
2. **Order rules by priority deliberately**: Lower `priority` values are evaluated first; put explicit `ALLOW` rules ahead of broader `BLOCK` rules when exceptions are required.
3. **Use `OVERRIDE` for monitored redirection**: Redirect blocked queries to a logging/sinkhole domain via `block_override_domain` instead of silent `NODATA` when investigating threats.
4. **Share centrally via RAM**: Manage one authoritative rule group per organization/account boundary and distribute it with `ram_resource_associations` rather than duplicating rules per account.

### Cross-Account and Hybrid DNS

1. **Split authorization and association across accounts correctly**: Create `vpc_association_authorizations` in the module (zone-owning account); create the actual `aws_route53_zone_association` resource in the VPC-owning account's Terraform config — this module intentionally does not manage that resource.
2. **Use `ignore_vpc` when associations are managed outside this module's state**: Set it to avoid Terraform trying to revert VPC associations created by `aws_route53_zone_association` elsewhere; remember that toggling this value requires a `moved` block/`state mv` between `aws_route53_zone.this` and `aws_route53_zone.ignore_vpc`.
3. **Centralize DNS with a hub-and-spoke model**: Manage shared zones and resolver rules in a central DNS/network account and distribute access via authorizations and RAM shares.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-route53
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/route53/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-route53/tree/master/examples
- **AWS Route53 Documentation**: https://docs.aws.amazon.com/route53/
- **Route53 Developer Guide**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html
- **Route53 Resolver Documentation**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html
- **DNSSEC in Route53**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring-dnssec.html
- **Route53 Resolver DNS Firewall**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall.html
- **Route53 Health Checks and Failover**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html
- **Route53 Accelerated Recovery**: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/accelerated-recovery.html
- **Route53 Pricing**: https://aws.amazon.com/route53/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Create zones before records**: The `records` map is applied against the zone created (or looked up) in the same module call; private zones require at least one `vpc` entry unless `ignore_vpc` associations are managed externally.
2. **Every routing-policy record needs `set_identifier`**: Omitting it when using `weighted_routing_policy`, `failover_routing_policy`, `latency_routing_policy`, `geolocation_routing_policy`, `geoproximity_routing_policy`, `multivalue_answer_routing_policy`, or `cidr_routing_policy` will fail to apply.
3. **Don't mix `vpc` and `delegation_set_id`**: They are mutually exclusive — delegation sets only apply to public zones.
4. **Cross-account VPC association is two-step**: Generate the authorization here (`vpc_association_authorizations`), then create `aws_route53_zone_association` in the VPC-owning account's own configuration — this module never creates that resource itself.
5. **Treat `ignore_vpc` changes as state-migration events**: Never flip this flag without also emitting the corresponding `moved` block or running `terraform state mv`, or Terraform will plan to destroy and recreate the zone.
6. **DNSSEC changes are sensitive**: After setting `enable_dnssec = true`, surface `dnssec_signing_key_ds_record` to the caller so it can be published at the registrar; do not disable DNSSEC on a live zone without first removing the DS record upstream.
7. **Restrict resolver endpoint security groups by default**: Never generate `security_group_ingress_rules`/`security_group_egress_rules` with `0.0.0.0/0`; scope to explicit CIDRs for hybrid DNS traffic.
8. **Roll out DNS firewall rules safely**: Default new `resolver-firewall-rule-group` rules to `action = "ALERT"` before switching to `BLOCK` in generated configurations, unless the user explicitly requests immediate blocking.
9. **Pin a version constraint**: Always include `version = "~> 6.5"` (or the current major) in generated `module` blocks to avoid unintended upgrades.
10. **Tag consistently**: Propagate a common `tags` map across the root module and any submodules used together (e.g., `resolver-endpoint` + `resolver-firewall-rule-group`) for cost allocation and ownership tracking.
