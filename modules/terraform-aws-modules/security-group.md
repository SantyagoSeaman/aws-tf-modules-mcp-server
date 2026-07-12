# Terraform AWS Security Group Module

## Module Information

- **Module Name**: `security-group`
- **Module ID**: `terraform-aws-modules/security-group/aws`
- **Source**: `terraform-aws-modules/security-group/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-security-group
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest
- **Latest Version**: 6.0.0 (major rewrite, released 2026-06-03; requires Terraform >= 1.5.7 and AWS provider >= 6.29)
- **Purpose**: Creates an AWS VPC security group and its ingress/egress rules as individual `aws_vpc_security_group_*_rule` resources, with 53 curated preset submodules for common services
- **Service**: AWS VPC Security Groups
- **Category**: Networking, Security
- **Keywords**: security-group, vpc, firewall, ingress, egress, cidr-ipv4, cidr-ipv6, prefix-list, referenced-security-group, self-reference, exclusive-rules, ports, protocol, ec2, rds, network-security
- **Use For**: web server access control, database security groups, SSH/RDP bastion access, microservices security-group chaining, load balancer security, container/cluster networking, VPN and IPSec endpoint security, multi-tier application segmentation, RAM-shared cross-VPC security groups, prefix-list-based access control

## Description

This module manages a single AWS VPC security group and its rules. As of v6.0.0 it has been fully rewritten on top of AWS provider v6's per-rule resources — `aws_vpc_security_group_ingress_rule` and `aws_vpc_security_group_egress_rule` — replacing the legacy `aws_security_group_rule` resource and inline `ingress`/`egress` blocks used in v5. Every rule now has exactly one traffic source/destination: `cidr_ipv4`, `cidr_ipv6`, `prefix_list_id`, or `referenced_security_group_id`. Rules are declared as a structured map (`ingress_rules` / `egress_rules`), where each map key becomes the rule's identifier and default `Name` tag.

The root module is a primitive: it accepts only structured rule maps and no longer understands v5-style named presets (e.g. `"https-443-tcp"`). All preset convenience now lives in 53 dedicated submodules under `modules/<service>/` (one per common service — HTTP, PostgreSQL, Redis, Kafka, Consul, etc.), each of which wraps the root module with a curated set of preset ports and exposes simple `map(string)` inputs (`ingress_cidr_ipv4`, `ingress_cidr_ipv6`, `ingress_prefix_list_id`, `ingress_referenced_security_group_id`) so a single submodule call can still open its preset ports to multiple sources.

Unlike v5, the module no longer injects implicit rules: there is no default allow-all egress and no default self-referencing ingress — both must be declared explicitly. By default (`enable_exclusive_rules = true`) the module also owns the complete rule set on the security group via `aws_vpc_security_group_rules_exclusive`, reverting any rule added out-of-band (console, other Terraform state) on the next apply. The module also supports associating the security group with additional VPCs via `vpc_associations` (used for RAM-shared security groups) and per-resource `timeouts`.

## Key Features

- **Provider v6 Rule Resources**: built on `aws_vpc_security_group_ingress_rule` / `aws_vpc_security_group_egress_rule` instead of legacy inline blocks or `aws_security_group_rule`
- **Structured Rule Maps**: `ingress_rules` / `egress_rules` as `map(object({...}))`; each entry is exactly one rule with exactly one source type
- **53 Preset Service Submodules**: curated port/protocol presets for databases, messaging, monitoring, remote access, and orchestration tooling
- **Four Composable Source Types**: `cidr_ipv4`, `cidr_ipv6`, `prefix_list_id`, `referenced_security_group_id` — one per rule, freely combined across rules in the same map
- **Self-Reference Sentinel**: `referenced_security_group_id = "self"` is rewritten at apply time to the security group's own ID, enabling cluster-internal rules without a circular reference
- **Exclusive Rule Enforcement**: `enable_exclusive_rules` (default `true`) provisions `aws_vpc_security_group_rules_exclusive` so the module is the sole source of truth for rules on the SG
- **Multi-VPC Association**: `vpc_associations` attaches the security group to additional VPCs (e.g. RAM-shared security groups)
- **Per-Rule Tagging**: each rule object accepts its own `tags`; the `Name` tag defaults to the map key
- **No Implicit Rules**: no default allow-all egress and no default self-ingress — every rule, including outbound internet access, must be declared
- **Configurable Timeouts**: optional `create`/`delete` timeout overrides for the security group resource
- **Create-Before-Destroy Lifecycle**: the security group uses `create_before_destroy`; combine with `use_name_prefix = true` (default) to allow zero-downtime replacement

## Main Use Cases

1. **Web Application Security**: Open HTTP/HTTPS ports for web servers and ALBs with explicit CIDR sources
2. **Database Access Control**: Restrict database ports to specific VPC CIDRs or application security groups via `referenced_security_group_id`
3. **SSH/RDP Bastion Hosts**: Grant remote-access ports only from known IP ranges or VPN CIDRs
4. **Microservices Communication**: Chain security groups (ALB -> App -> DB) using `referenced_security_group_id`
5. **Cluster Internal Communication**: Use the `"self"` sentinel to allow traffic between members of the same security group
6. **Container/Orchestration Networking**: Configure security groups for ECS, EKS, Nomad, or Docker Swarm clusters
7. **VPN/IPSec Endpoints**: Secure OpenVPN and IPSec (ISAKMP/NAT-T) endpoints with the dedicated preset submodules
8. **Cross-VPC Security Groups**: Associate one security group with multiple VPCs via `vpc_associations` (RAM sharing)
9. **Prefix-List-Based Access**: Scope ingress/egress to AWS-managed or customer-managed prefix lists instead of raw CIDRs
10. **Monitoring/Observability Stacks**: Secure Prometheus, Grafana, Elasticsearch/Kibana, and Loki endpoints with matching presets

## Submodules

Every preset submodule (`modules/<service>/`) shares the same interface: it wraps the root module, adds a fixed `preset_ingress_rules` catalog for that service, and exposes simple source-mapping inputs so callers don't have to write structured rule objects for standard ports.

### Common Submodule Interface

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the security group |
| `description` | `string` | `"Security Group managed by Terraform"` | Security group description |
| `vpc_id` | `string` | `null` | VPC ID where the security group is created (required in practice) |
| `ingress_cidr_ipv4` | `map(string)` | `{}` | Key = user label, value = IPv4 CIDR; one ingress rule is created per preset rule per entry |
| `ingress_cidr_ipv6` | `map(string)` | `{}` | Same, for IPv6 CIDRs |
| `ingress_prefix_list_id` | `map(string)` | `{}` | Same, for managed prefix list IDs |
| `ingress_referenced_security_group_id` | `map(string)` | `{}` | Same, for source security group IDs; use value `"self"` to reference the SG this submodule creates |
| `preset_ingress_rules` | `map(object({from_port,to_port,ip_protocol,description}))` | curated per-service set | Override or disable (`{}`) the built-in preset catalog |
| `ingress_rules` | `map(object({...}))` | `{}` | Additional ad-hoc ingress rules merged with the preset rules |
| `egress_rules` | `map(object({...}))` | `{}` | Egress rules (same object shape as root module); empty by default |
| `tags`, `use_name_prefix`, `enable_exclusive_rules`, `vpc_associations`, `timeouts`, `create`, `region`, `revoke_rules_on_delete` | — | — | Same as root module (see below) |

**Outputs** (identical across all submodules): `id`, `arn`, `name`, `owner_id`, `vpc_id`.

**Renamed/removed since v5**: `dax-cluster` -> `dynamodb-dax`, `oracle-db` -> `oracle`, `carbon-relay-ng` -> `carbon-relay`; `kubernetes-api`, `smtp`, `smtps`, `smtp-submission`, `web`, and `zookeeper` submodules were removed. Single-protocol preset rule keys dropped their `-tcp` suffix (e.g. `postgresql-tcp` -> `postgresql`); rules covering both TCP and UDP keep the suffix.

### Web

| Submodule | Preset Ports (protocol) |
|-----------|--------------------------|
| `http-80` | 80/tcp |
| `http-8080` | 8080/tcp |
| `https-443` | 443/tcp |
| `https-8443` | 8443/tcp |

### Databases & Storage

| Submodule | Preset Ports (protocol) |
|-----------|--------------------------|
| `mysql` | 3306/tcp (MySQL/Aurora) |
| `postgresql` | 5432/tcp |
| `oracle` | 1521/tcp |
| `mssql` | 1433/tcp server, 1434/udp browser, 2383/tcp analytics, 4022/tcp broker |
| `mongodb` | 27017/tcp, 27018/tcp shard, 27019/tcp config-server |
| `redis` | 6379/tcp |
| `redshift` | 5439/tcp |
| `cassandra` | 9042/tcp clients, 7000/tcp gossip, 7001/tcp gossip-tls, 7199/tcp jmx, 9160/tcp thrift |
| `dynamodb-dax` | 8111/tcp unencrypted, 9111/tcp encrypted |
| `memcached` | 11211/tcp |
| `minio` | 9000/tcp |
| `solr` | 8983-8987/tcp |

### Remote Access & VPN

| Submodule | Preset Ports (protocol) |
|-----------|--------------------------|
| `ssh` | 22/tcp |
| `rdp` | 3389/tcp+udp |
| `winrm` | 5985/tcp http, 5986/tcp https |
| `openvpn` | 1194/udp, 943/tcp, 443/tcp https |
| `ipsec-500` | 500/udp (ISAKMP) |
| `ipsec-4500` | 4500/udp (NAT-T) |

### Messaging & Streaming

| Submodule | Preset Ports (protocol) |
|-----------|--------------------------|
| `kafka` | 9092/tcp plaintext, 9094/tcp tls, 9096/tcp sasl-scram, 9098/tcp sasl-iam, 9194/9196/9198 public MSK variants, 11001/11002 exporters |
| `rabbitmq` | 5672/tcp amqp, 5671/tcp amqp-tls, 4369/tcp epmd, 25672/tcp internode, 15672/tcp mgmt, 15671/tcp mgmt-tls |
| `activemq` | 5671/tcp amqp, 8883/tcp mqtt, 61617/tcp openwire, 61614/tcp stomp, 61619/tcp websocket |
| `zipkin` | 9411/tcp query, 8080/tcp web, 9901/tcp admin-query, 9990/tcp admin, 9991/tcp admin-web |

### Monitoring & Observability

| Submodule | Preset Ports (protocol) |
|-----------|--------------------------|
| `prometheus` | 9090/tcp, 9091/tcp pushgateway, 9100/tcp node-exporter |
| `alertmanager` | 9093/tcp, 9094/tcp cluster |
| `grafana` | 3000/tcp |
| `elasticsearch` | 9200/tcp rest, 9300/tcp java |
| `kibana` | 5601/tcp |
| `loki` | 3100/tcp, 9095/tcp grpc |
| `promtail` | 9080/tcp |
| `logstash` | 5044/tcp |
| `graphite-statsd` | 80/tcp webui, 2003/tcp receiver, 2004/tcp receiver-serializer, 2023/2024/tcp aggregator, 8080/tcp gunicorn, 8125/tcp+udp statsd, 8126/tcp statsd-admin |
| `carbon-relay` | 2003/tcp+udp line-in, 2004/tcp admin, 2013/tcp+udp serializer, 8081/tcp gui |
| `splunk` | 8000/tcp web, 8088/tcp hec, 8089/tcp splunkd, 9997/tcp indexer |
| `wazuh` | 443/tcp dashboard, 514/tcp+udp syslog, 1514/tcp+udp agent-conn, 1515/tcp enrollment, 1516/tcp cluster-daemon, 9200/tcp indexer-api, 55000/tcp restful-api |
| `zabbix` | 10050/tcp agent, 10051/tcp server/proxy |

### Orchestration & Coordination

| Submodule | Preset Ports (protocol) |
|-----------|--------------------------|
| `consul` | 8300/tcp server, 8301/8302/tcp+udp serf, 8500/8501/tcp webui, 8502/8503/tcp grpc, 8600/tcp+udp dns |
| `vault` | 8200/tcp |
| `etcd` | 2379/tcp client, 2380/tcp peer |
| `nomad` | 4646/tcp http, 4647/tcp rpc, 4648/tcp+udp serf |
| `docker-swarm` | 2377/tcp mgmt, 4789/udp overlay, 7946/tcp+udp node |
| `saltstack` | 4505-4506/tcp |
| `puppet` | 8140/tcp puppet, 8081/tcp puppetdb |

### Other Network & Infra Protocols

| Submodule | Preset Ports (protocol) |
|-----------|--------------------------|
| `ldap` | 389/tcp |
| `ldaps` | 636/tcp |
| `ntp` | 123/udp |
| `nfs` | 2049/tcp (NFS/EFS) |
| `squid` | 3128/tcp |
| `jmx` | 1099/tcp |
| `storm` | 6627/tcp nimbus, 6700-6703/tcp supervisor, 8080/tcp ui |

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_id` | `string` | `null` | VPC ID where the security group is created (required in practice) |
| `name` | `string` | `""` | Name of the security group |
| `description` | `string` | `null` | Description of the security group |
| `ingress_rules` | `map(object({...}))` | `{}` | Structured ingress rules; see rule object schema below |
| `egress_rules` | `map(object({...}))` | `{}` | Structured egress rules (same object shape); no egress is allowed by default |
| `enable_exclusive_rules` | `bool` | `true` | Enforce the module owns all rules on the SG via `aws_vpc_security_group_rules_exclusive`; reverts out-of-band rule changes |
| `use_name_prefix` | `bool` | `true` | Use `name` as a prefix with a random suffix; required to keep `create_before_destroy` replacements working |
| `revoke_rules_on_delete` | `bool` | `false` | Revoke all rules before destroying the security group |
| `vpc_associations` | `map(object({vpc_id=string}))` | `{}` | Associate the security group with additional VPCs (e.g. RAM-shared security groups) |
| `timeouts` | `object({create,delete})` | `null` | Create/delete timeout overrides for the security group resource |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |
| `create` | `bool` | `true` | Whether to create the security group and its rule resources |
| `region` | `string` | `null` | AWS region override (defaults to the provider's region) |

### Rule Object Schema (`ingress_rules` / `egress_rules` entries)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ip_protocol` | `string` | `"tcp"` | Protocol (`tcp`, `udp`, `icmp`, or `-1` for all protocols) |
| `from_port` | `number` | — | Start of port range |
| `to_port` | `number` | — | End of port range; if only one of `from_port`/`to_port` is set, the other defaults to it |
| `cidr_ipv4` | `string` | `null` | IPv4 CIDR source/destination |
| `cidr_ipv6` | `string` | `null` | IPv6 CIDR source/destination |
| `prefix_list_id` | `string` | `null` | Managed prefix list ID |
| `referenced_security_group_id` | `string` | `null` | Source/destination security group ID; use `"self"` to reference the SG created by this module |
| `description` | `string` | `null` | Rule description |
| `name` | `string` | `null` | Overrides the default `Name` tag (which otherwise defaults to the map key) |
| `tags` | `map(string)` | `{}` | Per-rule tags |

**Exactly one** of `cidr_ipv4`, `cidr_ipv6`, `prefix_list_id`, `referenced_security_group_id` must be set per rule — the AWS provider v6 resources no longer accept plural CIDR lists on a single rule.

## Main Outputs

| Output | Description |
|--------|-------------|
| `id` | ID of the security group (was `security_group_id` in v5) |
| `arn` | ARN of the security group (was `security_group_arn` in v5) |
| `name` | Name of the security group (was `security_group_name` in v5) |
| `vpc_id` | VPC ID of the security group (was `security_group_vpc_id` in v5) |
| `owner_id` | AWS account ID that owns the security group (was `security_group_owner_id` in v5) |

## Usage Examples

### Example 1: Root Module — Explicit Rules with Self-Reference

```hcl
module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 6.0"

  name        = "web-server"
  description = "Security group for web servers"
  vpc_id      = module.vpc.vpc_id

  ingress_rules = {
    https = {
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      cidr_ipv4   = "0.0.0.0/0"
      description = "HTTPS from internet"
    }
    self-all = {
      ip_protocol                  = "-1"
      referenced_security_group_id = "self"
      description                  = "All traffic between members of this SG"
    }
  }

  # No implicit egress in v6 - must be declared explicitly
  egress_rules = {
    all = {
      ip_protocol = "-1"
      cidr_ipv4   = "0.0.0.0/0"
      description = "All outbound"
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 2: Preset Submodule — Single Source

```hcl
module "postgresql_sg" {
  source  = "terraform-aws-modules/security-group/aws//modules/postgresql"
  version = "~> 6.0"

  name        = "postgresql"
  description = "PostgreSQL access from app subnets"
  vpc_id      = module.vpc.vpc_id

  ingress_cidr_ipv4 = {
    app_subnets = "10.0.1.0/24"
  }

  egress_rules = {
    all = {
      ip_protocol = "-1"
      cidr_ipv4   = "0.0.0.0/0"
    }
  }

  tags = {
    Database = "PostgreSQL"
  }
}
```

### Example 3: Combining Multiple Source Types in One Call

```hcl
module "app_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 6.0"

  name        = "application"
  description = "Application security group"
  vpc_id      = module.vpc.vpc_id

  ingress_rules = {
    https-from-vpc = {
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      cidr_ipv4   = "10.0.0.0/16"
      description = "HTTPS from VPC"
    }

    http-from-ipv6 = {
      from_port   = 80
      to_port     = 80
      ip_protocol = "tcp"
      cidr_ipv6   = "2001:db8::/64"
      description = "HTTP from IPv6"
    }

    dns-from-prefix-list = {
      from_port      = 53
      to_port        = 53
      ip_protocol    = "udp"
      prefix_list_id = aws_ec2_managed_prefix_list.dns.id
      description    = "DNS from prefix list"
    }

    single-port-shorthand = {
      from_port   = 8080
      ip_protocol = "tcp"
      cidr_ipv4   = "10.0.0.0/16"
      description = "to_port defaults to from_port when omitted"
    }
  }

  egress_rules = {
    all = {
      ip_protocol = "-1"
      cidr_ipv4   = "0.0.0.0/0"
    }
  }

  tags = { Environment = "production" }
}
```

### Example 4: Layered Security Groups (ALB -> App -> DB)

```hcl
# ALB security group
module "alb_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 6.0"

  name   = "alb"
  vpc_id = module.vpc.vpc_id

  ingress_rules = {
    https = {
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      cidr_ipv4   = "0.0.0.0/0"
      description = "HTTPS from internet"
    }
  }

  egress_rules = {
    all = { ip_protocol = "-1", cidr_ipv4 = "0.0.0.0/0" }
  }
}

# Application security group - allow from ALB only
module "app_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 6.0"

  name   = "application"
  vpc_id = module.vpc.vpc_id

  ingress_rules = {
    http-from-alb = {
      from_port                    = 8080
      to_port                      = 8080
      ip_protocol                  = "tcp"
      referenced_security_group_id = module.alb_sg.id
      description                  = "HTTP from ALB"
    }
  }

  egress_rules = {
    all = { ip_protocol = "-1", cidr_ipv4 = "0.0.0.0/0" }
  }
}

# Database security group - allow from app only
module "db_sg" {
  source  = "terraform-aws-modules/security-group/aws//modules/postgresql"
  version = "~> 6.0"

  name   = "database"
  vpc_id = module.vpc.vpc_id

  ingress_referenced_security_group_id = {
    app = module.app_sg.id
  }
}
```

### Example 5: Preset Submodule Combining CIDR and Referenced Security Group

```hcl
module "consul_sg" {
  source  = "terraform-aws-modules/security-group/aws//modules/consul"
  version = "~> 6.0"

  name        = "consul"
  description = "Consul access from VPC and app tier"
  vpc_id      = module.vpc.vpc_id

  ingress_cidr_ipv4 = {
    primary = "10.0.0.0/16"
  }

  ingress_referenced_security_group_id = {
    app = module.app_sg.id
  }

  tags = { Cluster = "consul" }
}
```

### Example 6: Multi-VPC Association and Custom Timeouts

```hcl
module "shared_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 6.0"

  name        = "shared-services"
  description = "Security group shared across VPCs via RAM"
  vpc_id      = module.vpc.vpc_id

  vpc_associations = {
    secondary = {
      vpc_id = module.vpc_secondary.vpc_id
    }
  }

  ingress_rules = {
    https = {
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      cidr_ipv4   = "10.0.0.0/8"
      description = "HTTPS from internal networks"
    }
  }

  egress_rules = {
    all = { ip_protocol = "-1", cidr_ipv4 = "0.0.0.0/0" }
  }

  timeouts = {
    create = "5m"
    delete = "10m"
  }
}
```

## Best Practices

### Security Design

1. **Least Privilege**: Only declare rules for ports that are strictly necessary; there are no implicit rules to fall back on in v6
2. **Prefer Referenced Security Groups**: Use `referenced_security_group_id` over CIDR blocks for inter-service communication so access tracks instance membership automatically
3. **Avoid `0.0.0.0/0` Ingress**: Restrict ingress to known CIDRs or prefix lists; reserve open ingress for public-facing load balancers
4. **Declare Egress Explicitly**: v6 has no default egress rule — decide and declare what outbound traffic is allowed rather than defaulting to `-1`/`0.0.0.0/0`
5. **Use Preset Submodules for Standard Services**: Leverage the 53 service submodules for consistent, audited port configurations instead of hand-writing common ports

### Rule Configuration

1. **One Source Per Rule**: Each rule object must set exactly one of `cidr_ipv4`, `cidr_ipv6`, `prefix_list_id`, `referenced_security_group_id`; split multiple sources into multiple map entries
2. **Add Descriptions**: Document every rule with `description` for auditing and console readability
3. **Layer Security Groups**: Create separate security groups per tier (ALB -> App -> DB) and chain them with `referenced_security_group_id`
4. **Self-Reference for Clusters**: Use `referenced_security_group_id = "self"` for cluster-internal communication instead of hardcoding the SG's own CIDR or ID
5. **Understand `enable_exclusive_rules`**: With the default `true`, any rule added outside this module's state (console, other Terraform configs) is removed on the next apply — set to `false` if another process must also manage rules on the same SG

### Operations

1. **Version Pin**: Use `version = "~> 6.0"` in module blocks; v5 configurations are not compatible with v6 inputs
2. **Keep `use_name_prefix = true`**: The security group uses `create_before_destroy`; a static `name` (`use_name_prefix = false`) will fail to replace because AWS disallows duplicate names in the same VPC
3. **Tagging**: Apply Environment, Owner, and Application tags at the module level; use per-rule `tags` for rule-specific metadata
4. **Regular Audits**: Review security groups periodically to remove unused rules, especially after refactors
5. **No Built-In "Manage Existing SG" Mode**: Unlike v5 (`create_sg = false` + `security_group_id`), v6's root module always creates the security group itself — there is no supported way to only attach rules to an SG created outside this module

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-security-group
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest
- **Complete Example**: https://github.com/terraform-aws-modules/terraform-aws-security-group/tree/master/examples/complete
- **v5 -> v6 Upgrade Guide**: https://github.com/terraform-aws-modules/terraform-aws-security-group/blob/master/docs/UPGRADE-6.0.md
- **AWS Security Groups Docs**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
- **AWS Security Group Rules Docs**: https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html
- **VPC Security Best Practices**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html
- **`aws_vpc_security_group_ingress_rule` Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_security_group_ingress_rule
- **`aws_vpc_security_group_egress_rule` Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_security_group_egress_rule
- **`aws_vpc_security_group_rules_exclusive` Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_security_group_rules_exclusive

## Notes for AI Agents

When using this module in Terraform code generation:

1. **This Is v6, Not v5**: Do not generate v5-style inputs (`ingress_rules = ["https-443-tcp"]`, `ingress_with_cidr_blocks`, `ingress_cidr_blocks`, `computed_*`, `number_of_computed_*`, `create_sg`, `security_group_id`) — none of these exist in v6; the root module now takes only `ingress_rules`/`egress_rules` as `map(object({...}))`
2. **Always Declare Egress**: There is no default allow-all egress in v6 — include an explicit `egress_rules` block whenever outbound traffic is needed
3. **One Source Field Per Rule**: Never set more than one of `cidr_ipv4`, `cidr_ipv6`, `prefix_list_id`, `referenced_security_group_id` on the same rule object; use separate map entries for multiple sources
4. **Never Default to `0.0.0.0/0`**: Always ask for or infer specific CIDR ranges for ingress unless the resource is explicitly public-facing (e.g. an internet-facing ALB)
5. **Use `"self"` for Cluster Rules**: Set `referenced_security_group_id = "self"` rather than trying to reference the module's own output within the same rule map (this would create a cycle)
6. **Prefer Preset Submodules for Named Services**: Use `modules/<service>/` (e.g. `modules/postgresql`, `modules/redis`) for standard ports; use the root module only for custom or multi-service security groups
7. **Reference New Output Names**: Use `.id`, `.arn`, `.name`, `.vpc_id`, `.owner_id` — NOT the v5 `security_group_id`/`security_group_arn`/etc.
8. **Keep `use_name_prefix = true`**: Only set it to `false` if the caller can guarantee the name never changes, since replacements will otherwise fail
9. **Mind `enable_exclusive_rules`**: Leave it `true` (default) unless the security group is intentionally shared with another rule-managing process
10. **Version Pin**: Always specify `version = "~> 6.0"` in module blocks
11. **Tag Comprehensively**: Include Environment, Application, and Owner tags at the module or per-rule level
12. **No "Attach Rules to Existing SG" Mode**: If the user needs to manage rules on a security group created elsewhere, this module cannot do that in v6 — use `aws_vpc_security_group_ingress_rule`/`egress_rule` resources directly instead
