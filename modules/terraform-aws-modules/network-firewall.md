# Terraform AWS Network Firewall Module

## Module Information

- **Module Name**: `network-firewall`
- **Module ID**: `terraform-aws-modules/network-firewall/aws`
- **Source**: `terraform-aws-modules/network-firewall/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-network-firewall
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/network-firewall/aws/latest
- **Latest Version**: 2.1.0 (requires Terraform >= 1.5.7; submodules require AWS provider >= 6.28)
- **Purpose**: Terraform module that creates and manages AWS Network Firewall resources (firewall, firewall policy, and rule groups) for stateful/stateless traffic inspection and intrusion detection/prevention in VPCs and Transit Gateways
- **Service**: AWS Network Firewall (Amazon Network Firewall)
- **Category**: Security, Networking, Firewall
- **Keywords**: network-firewall, stateful-firewall, stateless-firewall, suricata, ids, ips, firewall-policy, rule-group, domain-filtering, deep-packet-inspection, transit-gateway, egress-filtering, perimeter-security, resource-sharing, ram
- **Use For**: VPC perimeter security, intrusion detection and prevention, egress traffic filtering, internet gateway protection, domain-based filtering, application-layer inspection, compliance enforcement (PCI-DSS, HIPAA), centralized firewall management, multi-account rule sharing, Transit Gateway traffic inspection

## Description

AWS Network Firewall is a managed, stateful network firewall and intrusion detection/prevention service that provides fine-grained traffic filtering for VPCs and Transit Gateways. This Terraform module creates and wires together the three resource types that make up a working deployment: a firewall (the inspection endpoint attached to a VPC or Transit Gateway), a firewall policy (the set of default actions and rule group references applied to traffic), and rule groups (the actual stateful/stateless rules, powered by the Suricata IPS engine for signature-based detection, domain filtering, and 5-tuple packet matching).

The module is split into three independent, composable submodules — `firewall`, `policy`, and `rule-group` — each of which can be used on its own (useful when rule groups or policies need to be shared across accounts via AWS RAM and resource policies) or through the root module, which creates a firewall and its policy together while rule groups are created and referenced separately by ARN. Firewalls can attach to a VPC via subnet mapping (one endpoint per subnet/AZ) or directly to a Transit Gateway via availability-zone mapping, enabling both classic single-VPC perimeter inspection and centralized hub-and-spoke inspection architectures.

The module implements AWS best practices out of the box: independent KMS encryption configuration for each resource type, dual-destination logging (CloudWatch Logs and/or S3, for both ALERT and FLOW log types), granular change-protection flags (delete, subnet, availability-zone, and policy protection), resource policies plus RAM associations for cross-account rule/policy sharing, and per-call region overrides for multi-region deployments. With comprehensive tagging support and `create` flags on every submodule, it serves as the foundation for defense-in-depth network security architectures on AWS.

## Key Features

- **Three Composable Submodules**: `firewall`, `policy`, and `rule-group` can be deployed together via the root module or independently for advanced sharing topologies
- **Stateful & Stateless Rule Groups**: Author rules via Suricata-compatible rule strings (`rules`), structured 5-tuple stateless rules, or native stateful rule blocks (`rule_group`)
- **Suricata IPS Engine**: Signature-based intrusion detection/prevention with connection tracking and protocol-aware inspection
- **Domain List Filtering**: Allow/deny traffic by FQDN using `rules_source_list` with `HTTP_HOST`/`TLS_SNI` target types
- **Deep Threat Inspection & Rule Overrides**: `stateful_rule_group_reference` supports `deep_threat_inspection` and `override.action` for tuning AWS-managed rule groups (e.g., downgrading DROP to ALERT)
- **Dual Attachment Modes**: Attach a firewall to a VPC via `subnet_mapping` (per-subnet endpoints) or directly to a Transit Gateway via `availability_zone_mapping`
- **Multi-AZ High Availability**: Deploy inspection endpoints across multiple availability zones with optional `availability_zone_change_protection`
- **Independent KMS Encryption**: Configure customer-managed key encryption separately for the firewall, policy, and each rule group
- **Dual-Destination Logging**: Stream `ALERT` and `FLOW` logs to CloudWatch Logs and/or S3 (1-2 destinations per firewall)
- **Traffic Analysis Metrics**: Enable `TLS_SNI`/`HTTP_HOST` analysis types for domain-level visibility without full logging
- **Resource Policies & RAM Sharing**: Share policies and rule groups across accounts using resource policies and AWS RAM associations
- **Granular Change Protection**: Independent flags for delete, subnet, availability-zone, and policy-change protection
- **Custom Stateless Actions**: Define custom pass/drop/forward actions with CloudWatch metric-publishing dimensions
- **Policy Variables**: Override default Suricata settings with custom IP sets and rule variables at the policy or rule-group level
- **Region Override**: Per-module `region` argument for multi-region deployments without duplicating provider blocks
- **Conditional Creation**: `create` flag on the root module and every submodule for environment-specific toggling
- **Comprehensive Tagging**: Consistent tagging across firewall, policy, and rule-group resources, plus a policy-specific `policy_tags` merge

## Main Use Cases

1. **VPC Perimeter Security**: Inspect all traffic entering and leaving a VPC through internet or NAT gateways
2. **Egress Traffic Filtering**: Control and monitor outbound traffic to prevent data exfiltration and malware callbacks
3. **Intrusion Detection and Prevention**: Detect and block known attack patterns using Suricata signatures
4. **Compliance Enforcement**: Implement network controls required for PCI-DSS, HIPAA, SOC 2, and similar frameworks
5. **Domain-Based Filtering**: Block malicious domains and enforce acceptable-use policies via FQDN rules
6. **Centralized/Multi-Account Inspection**: Share firewall policies and rule groups across accounts via AWS RAM and resource policies
7. **Transit Gateway Inspection Architecture**: Attach firewalls directly to a Transit Gateway for centralized hub-and-spoke inspection of inter-VPC traffic
8. **Managed Rule Group Tuning**: Use `deep_threat_inspection` and rule overrides to adjust AWS-managed rule group behavior without forking rules
9. **VPN and Direct Connect Security**: Inspect traffic from on-premises networks entering via VPN or Direct Connect
10. **Standalone Rule/Policy Sharing**: Deploy the `rule-group` or `policy` submodule independently to build reusable, shareable security building blocks

## Submodules

### 1. firewall

- **Purpose**: Creates the `aws_networkfirewall_firewall` resource (VPC subnet or Transit Gateway attachment) with encryption and logging configuration
- **Source**: `terraform-aws-modules/network-firewall/aws//modules/firewall`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/network-firewall/aws/latest/submodules/firewall
- **Key Features**: VPC subnet or Transit Gateway AZ attachment, multi-AZ endpoints, KMS encryption, CloudWatch/S3 logging, delete/subnet/AZ/policy change protection
- **Use Cases**: VPC perimeter inspection endpoint, centralized Transit Gateway inspection VPC, standalone firewall decoupled from policy lifecycle

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Friendly firewall name (required in practice) |
| `firewall_policy_arn` | `string` | `""` | ARN of the associated firewall policy (required in practice) |
| `vpc_id` | `string` | `null` | VPC ID for subnet-based attachment |
| `subnet_mapping` | `map(object)` | `null` | Public subnets (one per AZ) where firewall endpoints are created |
| `transit_gateway_id` | `string` | `null` | Transit Gateway ID for TGW-attached firewalls (alternative to `vpc_id`) |
| `availability_zone_mapping` | `list(object({availability_zone_id=string}))` | `null` | Required for TGW-attached firewalls; AZs where endpoints are created |
| `delete_protection` | `bool` | `true` | Prevents accidental firewall deletion |
| `subnet_change_protection` | `bool` | `true` | Blocks subnet mapping modifications |
| `availability_zone_change_protection` | `bool` | `null` | Blocks AZ configuration changes for TGW-attached firewalls |
| `firewall_policy_change_protection` | `bool` | `null` | Blocks changes to the associated firewall policy |
| `encryption_configuration` | `object({key_id, type})` | `null` | KMS encryption settings |
| `create_logging_configuration` | `bool` | `false` | Controls creation of the logging configuration |
| `logging_configuration_destination_config` | `list(object)` | `null` | 1-2 CloudWatch Logs/S3 logging destinations (ALERT/FLOW) |
| `enabled_analysis_types` | `list(string)` | `[]` | Traffic analysis metrics: `TLS_SNI`, `HTTP_HOST` |
| `region` | `string` | `null` | Region override for the resources (defaults to provider region) |

#### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Firewall resource ARN |
| `id` | Firewall resource ID (ARN) |
| `status` | Nested list with operational state and endpoint info per AZ |
| `update_token` | Version-control token required for modifications |
| `logging_configuration_id` | ARN associated with the logging configuration |

#### Usage Example

```hcl
module "firewall" {
  source  = "terraform-aws-modules/network-firewall/aws//modules/firewall"
  version = "~> 2.0"

  name                = "example-firewall"
  vpc_id              = "vpc-1234556abcdef"
  firewall_policy_arn = module.firewall_policy.arn

  # Deploy across multiple AZs for high availability
  subnet_mapping = {
    subnet1 = { subnet_id = "subnet-abcde012", ip_address_type = "IPV4" }
    subnet2 = { subnet_id = "subnet-bcde012a", ip_address_type = "IPV4" }
  }

  # Enable protection controls
  delete_protection         = true
  subnet_change_protection  = true

  # Configure logging
  create_logging_configuration = true
  logging_configuration_destination_config = [
    {
      log_destination      = { logGroup = "/aws/network-firewall/example" }
      log_destination_type = "CloudWatchLogs"
      log_type             = "ALERT"
    },
    {
      log_destination      = { bucketName = "my-firewall-logs", prefix = "flow" }
      log_destination_type = "S3"
      log_type             = "FLOW"
    }
  ]

  tags = {
    Environment = "production"
  }
}
```

### 2. policy

- **Purpose**: Creates the `aws_networkfirewall_firewall_policy` resource with stateful/stateless rule group references, custom actions, and an optional cross-account resource policy
- **Source**: `terraform-aws-modules/network-firewall/aws//modules/policy`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/network-firewall/aws/latest/submodules/policy
- **Key Features**: Stateful/stateless rule group references with deep threat inspection overrides, custom stateless actions, KMS encryption, resource policies + RAM associations for cross-account sharing
- **Use Cases**: Shared firewall policies across accounts, centralized policy management, multi-VPC security policies

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Policy name (required in practice) |
| `stateful_rule_group_reference` | `map(object)` | `null` | Stateful rule groups by ARN, with optional `priority`, `deep_threat_inspection`, `override.action` |
| `stateless_rule_group_reference` | `map(object({priority, resource_arn}))` | `null` | Stateless rule groups by ARN with evaluation priority |
| `stateless_default_actions` | `list(string)` | `["aws:pass"]` | Default action for unmatched packets (`aws:drop`, `aws:pass`, `aws:forward_to_sfe`) |
| `stateless_fragment_default_actions` | `list(string)` | `["aws:pass"]` | Default action for unmatched fragmented packets |
| `stateful_default_actions` | `list(string)` | `[]` | Fallback actions for unmatched stateful rules (requires `STRICT_ORDER`) |
| `stateful_engine_options` | `object` | `null` | Flow timeouts, `rule_order` (e.g. `STRICT_ORDER`), `stream_exception_policy` |
| `stateless_custom_action` | `map(object)` | `null` | Custom actions with metric-publishing dimensions |
| `policy_variables` | `object` | `null` | Suricata setting overrides with custom IP set definitions |
| `encryption_configuration` | `object({key_id, type})` | `null` | KMS encryption settings |
| `create_resource_policy` / `attach_resource_policy` | `bool` | `false` | Create/attach a resource policy for cross-account access |
| `resource_policy_principals` / `resource_policy_actions` | `list(string)` | `[]` | IAM principals and actions allowed by the resource policy |
| `ram_resource_associations` | `map(string)` | `{}` | AWS RAM share associations for the policy |

#### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Policy resource ARN |
| `id` | Policy resource ID (ARN) |
| `update_token` | Policy modification token |
| `resource_policy_id` | ARN of the associated resource policy |

#### Usage Example

```hcl
module "firewall_policy" {
  source  = "terraform-aws-modules/network-firewall/aws//modules/policy"
  version = "~> 2.0"

  name        = "example-policy"
  description = "Network firewall policy with stateful inspection"

  # Default actions for unmatched traffic
  stateless_default_actions          = ["aws:forward_to_sfe"]
  stateless_fragment_default_actions = ["aws:drop"]

  # Stateful engine options
  stateful_engine_options = {
    rule_order              = "STRICT_ORDER"
    stream_exception_policy = "DROP"
  }

  # Reference existing rule groups (own or shared via RAM)
  stateful_rule_group_reference = {
    domain-filtering = {
      priority     = 100
      resource_arn = module.rule_group_domain_filtering.arn
    }
    managed-threat-signatures = {
      priority                = 200
      resource_arn            = "arn:aws:network-firewall:us-east-1:aws-managed:stateful-rulegroup/ThreatSignaturesEmergingEventsStrictOrder"
      deep_threat_inspection  = true
      override                = { action = "DROP_TO_ALERT" }
    }
  }

  # Enable cross-account sharing
  create_resource_policy     = true
  attach_resource_policy     = true
  resource_policy_principals = ["arn:aws:iam::123456789012:root"]
  resource_policy_actions = [
    "network-firewall:ListFirewallPolicies",
    "network-firewall:DescribeFirewallPolicy"
  ]

  tags = {
    Environment = "production"
  }
}
```

### 3. rule-group

- **Purpose**: Creates an `aws_networkfirewall_rule_group` resource (stateful or stateless) with an optional cross-account resource policy for RAM sharing
- **Source**: `terraform-aws-modules/network-firewall/aws//modules/rule-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/network-firewall/aws/latest/submodules/rule-group
- **Key Features**: Suricata rule-string import (`rules`) or structured `rule_group` blocks, stateless 5-tuple rules with custom actions, stateful domain-list filtering, rule variables (IP/port sets) and reference sets, resource policy + RAM sharing
- **Use Cases**: Reusable, shareable rule groups referenced by one or more firewall policies; standalone rule authoring decoupled from policy/firewall lifecycle

#### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Rule group name (required in practice) |
| `type` | `string` | `"STATELESS"` | `STATEFUL` or `STATELESS` |
| `capacity` | `number` | `100` | Max operating resources the rule group can use (sum of rule capacities) |
| `rule_group` | `object` | `null` | Structured rule definition (`rules_source`, `rule_variables`, `reference_sets`, `stateful_rule_options`); required unless `rules` is set |
| `rules` | `string` | `null` | Suricata-format rule strings (one rule per line); required unless `rule_group` is set |
| `encryption_configuration` | `object({key_id, type})` | `null` | KMS encryption settings |
| `create_resource_policy` / `attach_resource_policy` | `bool` | `false` | Create/attach a resource policy for cross-account access |
| `resource_policy_principals` / `resource_policy_actions` | `list(string)` | `[]` | IAM principals and actions allowed by the resource policy |
| `ram_resource_associations` | `map(string)` | `{}` | AWS RAM share associations for the rule group |

#### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Rule group resource ARN |
| `id` | Rule group resource ID (ARN) |
| `resource_policy_id` | ARN of the associated resource policy |
| `update_token` | Rule group modification token |

#### Usage Examples

##### Example 1: Stateful domain deny-list

```hcl
module "rule_group_stateful" {
  source  = "terraform-aws-modules/network-firewall/aws//modules/rule-group"
  version = "~> 2.0"

  name        = "example-stateful"
  description = "Stateful inspection for denying access to a domain"
  type        = "STATEFUL"
  capacity    = 100

  rule_group = {
    rules_source = {
      rules_source_list = {
        generated_rules_type = "DENYLIST"
        target_types         = ["HTTP_HOST"]
        targets               = ["test.example.com"]
      }
    }
  }

  # Share with other accounts via resource policy
  create_resource_policy     = true
  attach_resource_policy     = true
  resource_policy_principals = ["arn:aws:iam::123456789012:root"]

  tags = {
    Environment = "production"
  }
}
```

##### Example 2: Stateless 5-tuple rule with a custom action

```hcl
module "rule_group_stateless" {
  source  = "terraform-aws-modules/network-firewall/aws//modules/rule-group"
  version = "~> 2.0"

  name        = "example-stateless"
  description = "Stateless inspection with a custom action"
  type        = "STATELESS"
  capacity    = 100

  rule_group = {
    rules_source = {
      stateless_rules_and_custom_actions = {
        custom_action = [{
          action_name = "ExampleMetricsAction"
          action_definition = {
            publish_metric_action = {
              dimension = [{ value = "2" }]
            }
          }
        }]
        stateless_rule = [{
          priority = 1
          rule_definition = {
            actions = ["aws:pass", "ExampleMetricsAction"]
            match_attributes = {
              source           = [{ address_definition = "1.2.3.4/32" }]
              source_port      = [{ from_port = 443, to_port = 443 }]
              destination      = [{ address_definition = "124.1.1.5/32" }]
              destination_port = [{ from_port = 443, to_port = 443 }]
              protocols        = [6]
              tcp_flag         = [{ flags = ["SYN"], masks = ["SYN", "ACK"] }]
            }
          }
        }]
      }
    }
  }

  tags = {
    Environment = "production"
  }
}
```

## Usage Examples

```hcl
# Rule groups are created independently and referenced by ARN
module "rule_group_stateful" {
  source  = "terraform-aws-modules/network-firewall/aws//modules/rule-group"
  version = "~> 2.0"

  name     = "example-stateful"
  type     = "STATEFUL"
  capacity = 100

  rule_group = {
    rules_source = {
      rules_source_list = {
        generated_rules_type = "DENYLIST"
        target_types         = ["HTTP_HOST"]
        targets               = ["test.example.com"]
      }
    }
  }

  tags = { Environment = "production" }
}

module "network_firewall" {
  source  = "terraform-aws-modules/network-firewall/aws"
  version = "~> 2.0"

  # Firewall
  name        = "example"
  description = "Example network firewall"
  vpc_id      = "vpc-1234556abcdef"

  # Subnet mapping across different AZs
  subnet_mapping = {
    subnet1 = { subnet_id = "subnet-abcde012", ip_address_type = "IPV4" }
    subnet2 = { subnet_id = "subnet-bcde012a", ip_address_type = "IPV4" }
  }

  # Protection controls
  delete_protection                 = true
  subnet_change_protection          = true
  firewall_policy_change_protection = true

  # Logging configuration
  create_logging_configuration = true
  logging_configuration_destination_config = [
    {
      log_destination      = { logGroup = "/aws/network-firewall/example" }
      log_destination_type = "CloudWatchLogs"
      log_type             = "ALERT"
    },
    {
      log_destination      = { bucketName = "s3-example-bucket", prefix = "example" }
      log_destination_type = "S3"
      log_type             = "FLOW"
    }
  ]

  # Policy (created together with the firewall by the root module)
  policy_name                               = "example"
  policy_stateless_default_actions          = ["aws:forward_to_sfe"]
  policy_stateless_fragment_default_actions = ["aws:drop"]

  policy_stateful_engine_options = {
    rule_order              = "STRICT_ORDER"
    stream_exception_policy = "DROP"
  }

  policy_stateful_rule_group_reference = {
    one = {
      priority     = 100
      resource_arn = module.rule_group_stateful.arn
    }
  }

  tags = {
    Terraform   = "true"
    Environment = "production"
  }
}
```

> Note: The root module creates a `firewall` + `policy` pair only. Rule groups must always be created via the `rule-group` submodule (or `aws_networkfirewall_rule_group` directly) and referenced by ARN. To share a policy or rule group across accounts, use the standalone `policy`/`rule-group` submodules with `create_resource_policy`/`ram_resource_associations` instead of the root module.

## Best Practices

### Firewall Deployment and Architecture

1. **Deploy in a Dedicated Inspection VPC**: Create a centralized inspection VPC with Network Firewall for hub-and-spoke architectures
2. **Multi-AZ Deployment**: Always deploy firewall endpoints in at least two availability zones for high availability
3. **Dedicated Endpoint Subnets**: Allocate dedicated subnets for firewall endpoints in each AZ, separate from workload subnets
4. **Choose the Right Attachment Mode**: Use `subnet_mapping` for VPC-attached firewalls; use `transit_gateway_id` + `availability_zone_mapping` for Transit Gateway-attached, centralized inspection
5. **Separate Inspection and Application VPCs**: Isolate firewall infrastructure from application workloads for security and blast-radius isolation
6. **Route Table Configuration**: Configure route tables to direct traffic through firewall endpoints for inspection
7. **Asymmetric Routing Prevention**: Design routing so both directions of a traffic flow pass through the same firewall endpoint

### Rule Configuration and Management

1. **Start with Deny-All**: Begin with a default deny-all policy and explicitly allow required traffic
2. **Use Stateful Rules for Connections**: Apply stateful rules for connection-oriented protocols (TCP, HTTP, HTTPS)
3. **Stateless for High-Performance**: Use stateless rules for simple, high-throughput packet filtering
4. **Domain Lists for Egress**: Use `rules_source_list` domain filtering to control outbound HTTPS traffic by FQDN
5. **Organize with Rule Groups**: Create reusable rule groups by function (web, database, admin) via the `rule-group` submodule
6. **Rule Evaluation Order**: Use `STRICT_ORDER` for precise, priority-based control; default action order for simpler policies
7. **Tune Managed Rule Groups**: Use `deep_threat_inspection` and `override.action` on `stateful_rule_group_reference` to adjust AWS-managed rule group behavior instead of forking rules
8. **Suricata Rule Syntax**: Use Suricata-compatible rule strings (`rules` variable) for advanced IDS/IPS capabilities
9. **Regular Rule Updates**: Keep Suricata signatures and managed rule groups current to protect against new threats
10. **Document Rule Purpose**: Set `description` on rule groups and policies explaining business justification

### Security and Compliance

1. **Enable Delete Protection**: Set `delete_protection = true` for production firewalls
2. **Use KMS Encryption**: Set `encryption_configuration` on firewall, policy, and rule-group resources for compliance requirements
3. **Enable Both Log Types**: Log `ALERT` and `FLOW` types to CloudWatch and/or S3 for comprehensive monitoring
4. **Implement Resource Policies**: Use `create_resource_policy`/`resource_policy_principals` to control cross-account sharing of policies and rule groups
5. **Least Privilege Resource Policy Actions**: Scope `resource_policy_actions` to only the API calls consuming accounts need
6. **Network Segmentation**: Use the firewall to enforce segmentation boundaries between security zones
7. **Regularly Review Rules**: Periodically audit firewall rules and remove obsolete or unused rule groups
8. **Enable Policy Change Protection**: Set `firewall_policy_change_protection = true` for production firewalls
9. **Compliance-Driven Retention**: Retain firewall logs per compliance requirements (commonly 90 days to 7 years)
10. **Audit Trail**: Enable CloudTrail logging for all Network Firewall API calls

### Performance and Optimization

1. **Right-Size Rule Groups**: Set `capacity` based on actual rule count/complexity; over-provisioning wastes quota, under-provisioning blocks updates
2. **Use Stateless for Volume**: Apply stateless rules for high-volume, simple filtering to reduce processing overhead
3. **Optimize Rule Order**: In `STRICT_ORDER` policies, place the most frequently matched rules first
4. **Avoid Over-Inspection**: Don't route trusted internal traffic through deep packet inspection unnecessarily
5. **Monitor Firewall Metrics**: Track CloudWatch metrics for dropped/packet-loss indicators and scale endpoints accordingly
6. **Distributed Deployment**: For very high throughput, deploy multiple firewalls across VPCs or regions

### Logging and Monitoring

1. **Enable Dual Logging Destinations**: Send logs to both CloudWatch (near real-time analysis) and S3 (long-term storage) where the `1-2 destinations` limit allows
2. **Structured Log Analysis**: Use CloudWatch Logs Insights to query and analyze firewall logs
3. **Set Up CloudWatch Alarms**: Alert on blocked-traffic spikes, rule violations, and firewall health metrics
4. **Flow Logs for Forensics**: Enable flow logs for network forensics and connectivity troubleshooting
5. **Alert Logs for Threats**: Continuously monitor alert logs for IDS/IPS signature hits
6. **Log Retention Policies**: Set retention periods aligned with compliance requirements
7. **Integrate with SIEM**: Forward logs to a SIEM for correlation with other security telemetry
8. **Correlate with GuardDuty/Security Hub**: Combine Network Firewall alerts with GuardDuty findings and Security Hub for centralized triage

### Deployment and Operations

1. **Infrastructure as Code**: Manage all firewall, policy, and rule-group resources through Terraform for consistency
2. **Version Control Policies**: Store rule definitions in Git for change tracking and rollback
3. **Staged Rollouts**: Deploy rule changes to development, then staging, then production
4. **Change Management**: Require approval workflows for production policy/rule-group changes
5. **Consistent Tagging**: Apply tags for environment, application, cost-center, and compliance scope across all three resource types
6. **Pin Module Versions**: Pin the module version in production, e.g. `version = "~> 2.0"`, to avoid unexpected changes
7. **Use `create` Flags for Environments**: Toggle `create`/`create_policy`/submodule `create` flags to disable resources per environment without removing configuration
8. **Separate Firewall Accounts**: Consider dedicated security/network accounts for shared firewall infrastructure in multi-account setups

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-network-firewall
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/network-firewall/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-network-firewall/tree/master/examples
- **AWS Network Firewall Documentation**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/what-is-aws-network-firewall.html
- **Network Firewall API Reference**: https://docs.aws.amazon.com/network-firewall/latest/APIReference/Welcome.html
- **Suricata Documentation**: https://suricata.io/documentation/
- **Stateful Rule Groups**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/stateful-rule-groups-suricata.html
- **Stateless Rule Groups**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/stateless-rule-groups.html
- **Domain Filtering**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/stateful-rule-groups-domain-names.html
- **Logging Configuration**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/firewall-logging.html
- **Deployment Architectures**: https://docs.aws.amazon.com/network-firewall/latest/developerguide/architectures.html
- **AWS Firewall Manager**: https://docs.aws.amazon.com/waf/latest/developerguide/fms-chapter.html
- **AWS RAM (Resource Access Manager)**: https://docs.aws.amazon.com/ram/latest/userguide/what-is.html
- **Network Firewall Pricing**: https://aws.amazon.com/network-firewall/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Root Module Scope**: The root module only creates the `firewall` + `policy` pair. Always create rule groups separately via the `rule-group` submodule and reference them by ARN in `policy_stateful_rule_group_reference`/`policy_stateless_rule_group_reference`
2. **Attachment Mode Choice**: Use `vpc_id` + `subnet_mapping` for standard VPC attachment, or `transit_gateway_id` + `availability_zone_mapping` for Transit Gateway attachment — these are mutually exclusive modes
3. **Logging Setup**: Enable `create_logging_configuration = true` with both `ALERT` and `FLOW` destinations for comprehensive monitoring; the destination list allows a maximum of 2 entries
4. **KMS Encryption**: Set `encryption_configuration` on firewall, policy, and rule-group resources independently for production/compliance workloads
5. **Multi-AZ Deployment**: Configure at least two AZs in `subnet_mapping` or `availability_zone_mapping` for high availability
6. **Delete/Change Protection**: Enable `delete_protection`, `subnet_change_protection`, and `firewall_policy_change_protection` for production firewalls
7. **Rule Evaluation Order**: Set `stateful_engine_options.rule_order = "STRICT_ORDER"` when using `priority` on stateful rule group references; otherwise use default action order
8. **Managed Rule Group Tuning**: Use `deep_threat_inspection`/`override.action` on `stateful_rule_group_reference` when referencing AWS-managed rule groups instead of writing custom rules
9. **Cross-Account Sharing**: Use `create_resource_policy`, `resource_policy_principals`, `resource_policy_actions`, and `ram_resource_associations` on the `policy`/`rule-group` submodules — not available at the root module level
10. **Conditional Deployment**: Use the `create` variable (root and every submodule) to toggle resource creation per environment without deleting configuration
11. **Routing Configuration**: Remember to update VPC route tables separately to direct traffic through firewall endpoints — this module does not manage routes
12. **Region Overrides**: Use the `region` variable when a resource must be created in a different region than the default provider region
13. **Version Pinning**: Always pin `version = "~> 2.0"` (or tighter) in generated code to avoid breaking changes from major version bumps
14. **Capacity Planning**: Set `capacity` on rule groups to match actual rule count/complexity — increasing it later requires recreating the rule group
