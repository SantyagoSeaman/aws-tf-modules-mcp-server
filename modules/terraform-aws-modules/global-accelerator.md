# AWS Global Accelerator Terraform Module

## Module Information

- **Module Name**: `global-accelerator`
- **Source**: `terraform-aws-modules/global-accelerator/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-global-accelerator
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/global-accelerator/aws/latest
- **Latest Version**: 3.0.1
- **Terraform**: >= 1.0
- **AWS Provider**: >= 5.84
- **Purpose**: Creates AWS Global Accelerator standard accelerators (listeners + multi-region endpoint groups) and, via a submodule, custom routing accelerators
- **Service**: AWS Global Accelerator
- **Category**: Networking, Performance, High Availability
- **Keywords**: global-accelerator, anycast, static-ip, multi-region, failover, latency, load-balancer, endpoint-group, health-check, custom-routing, byoip, dual-stack, client-affinity, flow-logs, tcp-udp
- **Use For**: global application delivery, multi-region active-active/active-passive failover, latency reduction for internet-facing apps, blue-green/canary traffic shifting, gaming and VoIP custom routing, API performance optimization, static-IP entry point for allowlisting/hybrid connectivity, DDoS-resilient edge entry point

## Description

This Terraform module creates and manages AWS Global Accelerator resources: an `aws_globalaccelerator_accelerator`, one or more `aws_globalaccelerator_listener` resources, and the `aws_globalaccelerator_endpoint_group` resources nested under each listener. Global Accelerator is a networking service that provides static anycast IP addresses as fixed entry points to an application, then routes client traffic over the AWS global network backbone to the closest healthy endpoint — reducing latency and jitter and providing near-instant failover when an endpoint group becomes unhealthy, without requiring DNS TTL expiry.

The module exposes `listeners` as a single nested map input: each listener defines its protocol (TCP/UDP), port ranges, and client affinity, and contains its own `endpoint_groups` map with health-check settings, traffic dial percentage, weighted `endpoint_configuration` entries (ALB/NLB ARNs, EC2 instance IDs, or EIP allocation IDs), and optional `port_override` mappings. Endpoint groups can target different AWS regions (`endpoint_group_region`), which is how the module implements multi-region routing and failover. The root module supports static IPv4 or dual-stack (IPv4 + IPv6) addressing, Bring Your Own IP (BYOIP), and VPC Flow-Logs-style traffic logging to S3.

A dedicated `custom-routing` submodule wraps the parallel `aws_globalaccelerator_custom_routing_*` resources for custom routing accelerators, which map specific client connections to specific destinations (VPC subnet endpoints) rather than health-based load balancing — the pattern used for gaming servers, VoIP, and other workloads that need deterministic per-flow destination selection. Both accelerator types integrate with Route 53 alias records via their `dns_name`/`hosted_zone_id` outputs and benefit automatically from AWS Shield Standard DDoS protection at the edge.

## Key Features

- **Standard Accelerator**: Health-based routing to the nearest healthy endpoint using anycast IPs and the AWS global network
- **Static Anycast IPs**: Two static IPv4 addresses (four with `DUAL_STACK`: two IPv4 + two IPv6)
- **Dual-Stack Support**: `ip_address_type = "DUAL_STACK"` exposes both `dns_name` and `dual_stack_dns_name`
- **Bring Your Own IP (BYOIP)**: Supply 1-2 IPv4 addresses from your own BYOIP pool via `ip_addresses`
- **Nested Listener/Endpoint-Group Map**: Single `listeners` input defines protocol, port ranges, client affinity, and per-listener endpoint groups in one structure
- **Multi-Region Endpoint Groups**: `endpoint_group_region` on each endpoint group routes traffic to endpoints in different AWS regions for geographic failover
- **Weighted, Multi-Endpoint Traffic Distribution**: `endpoint_configuration` list with per-endpoint `weight` for canary/blue-green/weighted routing
- **Health Checks**: Configurable interval (10s or 30s), protocol (TCP/HTTP/HTTPS), path, port, and a single `threshold_count` (no separate healthy/unhealthy thresholds)
- **Client IP Preservation**: `client_ip_preservation_enabled` per endpoint (ALB/EC2 endpoints only)
- **Port Overrides**: `port_override` maps a listener-facing port to a different backend `endpoint_port`
- **Traffic Dial**: `traffic_dial_percentage` per endpoint group for gradual regional traffic shifting
- **Flow Logs**: `flow_logs_enabled` + `flow_logs_s3_bucket`/`flow_logs_s3_prefix` for traffic analysis
- **Custom Routing Submodule**: Dedicated `modules/custom-routing` for deterministic per-flow routing to VPC subnet endpoints
- **Cross-Account Endpoints**: `attachment_arn` support on `endpoint_configuration` for cross-account attachment endpoints
- **Configurable Timeouts**: Separate `listeners_timeouts` and `endpoint_groups_timeouts` (create/update/delete)
- **Conditional Creation**: `create` and `create_listeners` feature flags for staged/conditional deployments

## Main Use Cases

1. **Global Application Delivery**: Consistent, low-latency access for internet-facing apps serving users across regions/continents
2. **Multi-Region Failover / Disaster Recovery**: Automatic, near-instant rerouting from an unhealthy region's endpoint group to a healthy one
3. **Blue-Green and Canary Deployments**: Shift traffic gradually between endpoint weights or between endpoint groups via `traffic_dial_percentage`
4. **Gaming and Real-Time / VoIP Applications**: Use the `custom-routing` submodule for UDP traffic that needs deterministic client-to-destination mapping
5. **API and Microservice Performance**: Reduce latency and improve throughput for globally distributed API clients
6. **Static-IP Allowlisting**: Provide fixed anycast IPs that downstream firewalls/partners can allowlist even as backend infrastructure changes
7. **Hybrid Cloud Connectivity**: Stable entry point in front of infrastructure spanning AWS regions and on-premises data centers
8. **Multi-Protocol Ingress**: A single accelerator fronting TCP (HTTP/HTTPS) and UDP (DNS, gaming) listeners on different ports
9. **DDoS-Resilient Edge Entry**: Benefit from AWS Shield Standard protection at AWS edge locations in front of ALB/NLB/EC2 origins

## Submodules

### custom-routing

- **Purpose**: Provisions a custom routing accelerator that maps client connections to specific destinations inside VPC subnets, instead of health-based load balancing — for workloads (gaming, VoIP) that need deterministic per-flow destination selection.
- **Source**: `terraform-aws-modules/global-accelerator/aws//modules/custom-routing`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/global-accelerator/aws/latest/submodules/custom-routing
- **Key Features**: Static anycast IPs (IPv4/dual-stack), BYOIP support, flow logs, per-listener `destination_configuration` (port range + protocol) and `endpoint_configuration` pointing at VPC subnet IDs; **no health checks and no `client_affinity`/`protocol` on listeners** (unlike the standard accelerator)
- **Use Cases**: Multiplayer game server fleets, VoIP/media servers, IoT fleets requiring per-connection destination selection within a VPC subnet

**Variables** (key ones — same accelerator-level inputs as the root module: `create`, `name`, `ip_address_type`, `ip_addresses`, `enabled`, `flow_logs_enabled`, `flow_logs_s3_bucket`, `flow_logs_s3_prefix`, `create_listeners`, `tags`):

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `listeners` | `any` | `{}` | Map of listeners; each entry has `port_ranges` and an `endpoint_groups` map |
| `listeners_timeouts` | `map(string)` | `{}` | Create/update/delete timeouts for listeners |
| `endpoint_groups_timeouts` | `map(string)` | `{}` | Create/delete timeouts for endpoint groups (no `update`) |

Each `endpoint_groups` entry supports: `endpoint_group_region` (optional cross-region target), `destination_configuration` (list of `{ from_port, to_port, protocols }`), and `endpoint_configuration` (list of `{ endpoint_id }` — a VPC subnet ID).

**Outputs**:

| Output | Description |
|--------|-------------|
| `id` / `arn` | ARN of the custom routing accelerator |
| `dns_name` | DNS name of the accelerator |
| `hosted_zone_id` | Route 53 zone ID for alias records |
| `ip_sets` | IP address set associated with the accelerator |
| `listeners` | Map of created listeners and attributes |
| `endpoint_groups` | Map of created endpoint groups and attributes |

**Usage Example**:

```hcl
module "global_accelerator_custom_routing" {
  source  = "terraform-aws-modules/global-accelerator/aws//modules/custom-routing"
  version = "~> 3.0"

  name = "gaming-accelerator"

  flow_logs_enabled   = true
  flow_logs_s3_bucket = aws_s3_bucket.flow_logs.id
  flow_logs_s3_prefix = "custom-routing/"

  listeners = {
    game_servers = {
      port_ranges = [
        { from_port = 7000, to_port = 7999 }
      ]

      endpoint_groups = {
        primary = {
          destination_configuration = [
            { from_port = 7000, to_port = 7999, protocols = ["UDP"] }
          ]

          # endpoint_id must be a VPC subnet ID for custom routing
          endpoint_configuration = [for subnet in module.vpc.private_subnets : { endpoint_id = subnet }]
        }
      }
    }
  }

  tags = {
    Environment = "production"
    Application = "gaming"
  }
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the accelerator (blank by default — set explicitly) |
| `create` | `bool` | `true` | Controls if resources should be created |
| `enabled` | `bool` | `true` | Whether the accelerator is enabled |
| `ip_address_type` | `string` | `"IPV4"` | `IPV4` or `DUAL_STACK` |
| `ip_addresses` | `list(string)` | `[]` | 1-2 IPv4 addresses for BYOIP accelerators |
| `flow_logs_enabled` | `bool` | `false` | Enable flow logs |
| `flow_logs_s3_bucket` | `string` | `null` | S3 bucket name for flow logs (required if enabled) |
| `flow_logs_s3_prefix` | `string` | `null` | S3 key prefix for flow logs (required if enabled) |
| `create_listeners` | `bool` | `true` | Controls if listeners (and their endpoint groups) should be created |
| `listeners` | `any` | `{}` | Map of listener definitions — see schema below |
| `listeners_timeouts` | `map(string)` | `{}` | `create`/`update`/`delete` timeouts for listeners |
| `endpoint_groups_timeouts` | `map(string)` | `{}` | `create`/`update`/`delete` timeouts for endpoint groups |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

### Listener Object Schema (`listeners` map entries)

| Key | Type | Description |
|-----|------|-------------|
| `protocol` | `string` | `TCP` or `UDP` |
| `client_affinity` | `string` | `NONE` (default) or `SOURCE_IP` |
| `port_ranges` | `list(object({from_port,to_port}))` | Listener port range(s) |
| `endpoint_groups` | `map(object)` | Nested endpoint groups for this listener (schema below) |

### Endpoint Group Object Schema (`endpoint_groups` entries, nested under a listener)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `endpoint_group_region` | `string` | listener's region | AWS region where this endpoint group's endpoints live (enables multi-region) |
| `health_check_protocol` | `string` | `TCP` | `TCP`, `HTTP`, or `HTTPS` |
| `health_check_port` | `number` | listener port | Port used for health checks |
| `health_check_path` | `string` | `"/"` | Path for HTTP/HTTPS health checks |
| `health_check_interval_seconds` | `number` | `30` | `10` or `30` |
| `threshold_count` | `number` | `3` | Consecutive checks to flip health state (single value — no separate healthy/unhealthy count) |
| `traffic_dial_percentage` | `number` | `100` | Percentage of listener traffic sent to this endpoint group |
| `endpoint_configuration` | `list(object)` | `[]` | List of `{ endpoint_id, weight, client_ip_preservation_enabled, attachment_arn }` — `endpoint_id` is an ALB/NLB ARN, EC2 instance ID, or EIP allocation ID |
| `port_override` | `list(object({endpoint_port,listener_port}))` | `[]` | Maps a listener-facing port to a different backend port |

## Main Outputs

| Output | Description |
|--------|-------------|
| `id` / `arn` | ARN of the accelerator |
| `dns_name` | DNS name of the accelerator (e.g. `a1234567890abcdef.awsglobalaccelerator.com`) |
| `dual_stack_dns_name` | DNS name resolving to both IPv4 and IPv6 addresses (dual-stack accelerators only) |
| `hosted_zone_id` | Route 53 zone ID for alias records pointing at the accelerator |
| `ip_sets` | IP address set(s) associated with the accelerator |
| `listeners` | Map of created listeners and their attributes |
| `endpoint_groups` | Map of created endpoint groups and their attributes |

## Usage Examples

### Example 1: Basic Accelerator with Weighted ALB Endpoints

```hcl
module "global_accelerator" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name = "my-accelerator"

  listeners = {
    web = {
      client_affinity = "SOURCE_IP"
      protocol        = "TCP"
      port_ranges = [
        { from_port = 80, to_port = 80 }
      ]

      endpoint_groups = {
        primary = {
          health_check_protocol = "HTTP"
          health_check_path     = "/health"

          endpoint_configuration = [
            {
              endpoint_id                     = aws_lb.blue.arn
              weight                          = 90
              client_ip_preservation_enabled  = true
            },
            {
              endpoint_id                     = aws_lb.green.arn
              weight                          = 10
              client_ip_preservation_enabled  = true
            }
          ]
        }
      }
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 2: Multi-Region Failover

```hcl
module "global_accelerator_multi_region" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name = "multi-region-app"

  flow_logs_enabled   = true
  flow_logs_s3_bucket = aws_s3_bucket.logs.id
  flow_logs_s3_prefix = "global-accelerator/"

  listeners = {
    https = {
      protocol        = "TCP"
      client_affinity = "SOURCE_IP"
      port_ranges = [
        { from_port = 443, to_port = 443 }
      ]

      endpoint_groups = {
        us_east = {
          endpoint_group_region  = "us-east-1"
          health_check_protocol  = "HTTPS"
          health_check_path      = "/health"
          traffic_dial_percentage = 100

          endpoint_configuration = [
            { endpoint_id = aws_lb.us_east.arn, weight = 100, client_ip_preservation_enabled = true }
          ]
        }

        eu_west = {
          endpoint_group_region  = "eu-west-1"
          health_check_protocol  = "HTTPS"
          health_check_path      = "/health"
          traffic_dial_percentage = 100

          endpoint_configuration = [
            { endpoint_id = aws_lb.eu_west.arn, weight = 100, client_ip_preservation_enabled = true }
          ]
        }
      }
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 3: Dual-Stack Accelerator with Route 53 Alias Records

```hcl
module "global_accelerator_dual_stack" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name            = "dual-stack-accelerator"
  ip_address_type = "DUAL_STACK"

  listeners = {
    web = {
      protocol = "TCP"
      port_ranges = [
        { from_port = 443, to_port = 443 }
      ]

      endpoint_groups = {
        primary = {
          health_check_protocol = "HTTPS"
          health_check_path     = "/health"

          endpoint_configuration = [
            { endpoint_id = aws_lb.main.arn, weight = 100, client_ip_preservation_enabled = true }
          ]
        }
      }
    }
  }

  tags = {
    Environment = "production"
  }
}

resource "aws_route53_record" "ipv4" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "app.example.com"
  type    = "A"

  alias {
    name                   = module.global_accelerator_dual_stack.dns_name
    zone_id                = module.global_accelerator_dual_stack.hosted_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "ipv6" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "app.example.com"
  type    = "AAAA"

  alias {
    name                   = module.global_accelerator_dual_stack.dual_stack_dns_name
    zone_id                = module.global_accelerator_dual_stack.hosted_zone_id
    evaluate_target_health = true
  }
}
```

### Example 4: Multi-Protocol Listeners (TCP + UDP) with Port Override

```hcl
module "global_accelerator_multi_protocol" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name = "multi-protocol-accelerator"

  listeners = {
    web = {
      protocol = "TCP"
      port_ranges = [
        { from_port = 80, to_port = 80 },
        { from_port = 8080, to_port = 8080 }
      ]

      endpoint_groups = {
        primary = {
          endpoint_configuration = [
            { endpoint_id = aws_lb.main.arn, weight = 100 }
          ]

          # Backend listens on 8443; clients connect on 80 or 8080
          port_override = [
            { endpoint_port = 8443, listener_port = 80 },
            { endpoint_port = 8443, listener_port = 8080 }
          ]
        }
      }
    }

    dns = {
      protocol = "UDP"
      port_ranges = [
        { from_port = 53, to_port = 53 }
      ]

      endpoint_groups = {
        dns_servers = {
          health_check_protocol = "TCP"
          health_check_port     = 53

          endpoint_configuration = [
            { endpoint_id = aws_eip.dns_1.id, weight = 50 },
            { endpoint_id = aws_eip.dns_2.id, weight = 50 }
          ]
        }
      }
    }
  }

  tags = {
    Environment = "production"
  }
}
```

## Best Practices

### Architecture and Endpoint Selection

1. **Use Global Accelerator for Global, Health-Sensitive Traffic**: Deploy it when users are geographically distributed and need low latency plus fast, automatic failover — not for pure static-content caching (use CloudFront instead).
2. **Prefer Standard Routing Unless You Need Deterministic Destinations**: Reserve the `custom-routing` submodule for gaming/VoIP/IoT workloads that require mapping specific client flows to specific VPC subnet destinations; use the standard accelerator for everything else.
3. **Choose Endpoint Types Deliberately**: Use ALB for HTTP/HTTPS, NLB for high-performance TCP/UDP, and EC2/EIP endpoints only for specialized or legacy workloads.
4. **Combine with Route 53**: Point Route 53 alias records at the accelerator's `dns_name` (and `dual_stack_dns_name` for `DUAL_STACK`) to keep a branded domain while retaining the static anycast IPs.
5. **Deploy Across at Least Two Regions**: Use `endpoint_group_region` on separate endpoint groups so Global Accelerator can fail over automatically if an entire region degrades.

### Listener and Health Check Configuration

6. **Consolidate Port Ranges per Listener**: Group related ports into one listener with multiple `port_ranges` entries instead of creating many single-port listeners.
7. **Set `client_affinity = "SOURCE_IP"`** for stateful/WebSocket workloads that need session persistence to the same endpoint; leave it `NONE` for stateless HTTP APIs.
8. **Match Protocol to Traffic**: `TCP` for connection-oriented traffic, `UDP` for connectionless traffic (DNS, gaming, streaming).
9. **Use HTTP/HTTPS Health Checks for Web Endpoints**: A specific `health_check_path` (e.g. `/health`) is more reliable than a bare TCP check for detecting application-level failures.
10. **Tune `health_check_interval_seconds` and `threshold_count` Together**: `10s`/`2` gives faster failover at the cost of more health-check traffic and a higher chance of false positives; `30s`/`3` is the safer production default. Remember there is only one `threshold_count`, not separate healthy/unhealthy counters like ALB target groups.
11. **Avoid Overlapping Port Ranges** across listeners on the same accelerator to prevent undefined routing behavior.

### Traffic Management

12. **Use `traffic_dial_percentage` for Regional Rollouts**: Shift traffic into a new region gradually (e.g. 10% -> 50% -> 100%) rather than switching all at once.
13. **Weight Endpoints Proportionally to Capacity**: Set `weight` on each `endpoint_configuration` entry based on real capacity/performance testing, not arbitrary splits.
14. **Blue-Green via Weights**: Model blue-green or canary deployments as two `endpoint_configuration` entries in the same endpoint group and shift `weight` over time.
15. **Use `port_override` for Backend/Frontend Port Mismatches** instead of standing up extra listeners just to translate ports.

### Security

16. **Enable Flow Logs** (`flow_logs_enabled = true`) for production accelerators to support traffic analysis, auditing, and incident response.
17. **Enable `client_ip_preservation_enabled` Carefully**: It's needed for backends that rely on the real client IP, but AWS creates an unmanaged `GlobalAccelerator` security group in the target VPC that must be deleted manually before that VPC can be destroyed — Terraform will otherwise hang/retry on `terraform destroy`.
18. **Layer Defenses**: Global Accelerator includes AWS Shield Standard automatically; add AWS WAF on ALB endpoints and security groups that restrict origin traffic for defense in depth.
19. **Secure Flow Log Storage**: Apply least-privilege bucket policies and default encryption to the S3 bucket used for `flow_logs_s3_bucket`.
20. **Rotate BYOIP Ranges Deliberately**: If using `ip_addresses` (BYOIP), maintain a documented process for switching pools without breaking allowlists downstream.

### High Availability and Operations

21. **Test Failover Regularly**: Simulate endpoint or region failure (e.g., temporarily point health checks at a bad path) to validate failover timing matches your health-check settings.
22. **Maintain Spare Capacity in Secondary Regions**: Secondary endpoint groups must be able to absorb full traffic if the primary region fails — don't rely on `traffic_dial_percentage` alone for capacity planning.
23. **Tag Everything**: Apply consistent `tags` (environment, application, owner) for cost allocation and operational tracking.
24. **Manage Configuration as Code**: Keep `listeners`/`endpoint_groups` maps in version control with peer review; changes to health checks or weights should go through the same review process as other infrastructure changes.
25. **Consolidate Accelerators Where Sensible**: Share a single accelerator across multiple applications using different listener ports/protocols to reduce the number of hourly-billed accelerators.
26. **Disable, Don't Delete, for Temporary Pauses**: Use `enabled = false` (or `create = false`) to stop routing traffic without losing the anycast IPs and configuration.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-global-accelerator
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/global-accelerator/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-global-accelerator/tree/master/examples
- **What is AWS Global Accelerator**: https://docs.aws.amazon.com/global-accelerator/latest/dg/what-is-global-accelerator.html
- **How Global Accelerator Works**: https://docs.aws.amazon.com/global-accelerator/latest/dg/introduction-how-it-works.html
- **Custom Routing Accelerators**: https://docs.aws.amazon.com/global-accelerator/latest/dg/about-custom-routing-accelerators.html
- **Endpoints for Standard Accelerators**: https://docs.aws.amazon.com/global-accelerator/latest/dg/about-endpoints.html
- **Preserve Client IP Addresses**: https://docs.aws.amazon.com/global-accelerator/latest/dg/preserve-client-ip-address.html
- **Bring Your Own IP (BYOIP)**: https://docs.aws.amazon.com/global-accelerator/latest/dg/using-byoip.html
- **Flow Logs**: https://docs.aws.amazon.com/global-accelerator/latest/dg/monitoring-global-accelerator.flow-logs.html
- **CloudWatch Metrics**: https://docs.aws.amazon.com/global-accelerator/latest/dg/cloudwatch-monitoring.html
- **Global Accelerator Pricing**: https://aws.amazon.com/global-accelerator/pricing/
- **`aws_globalaccelerator_endpoint_group` Resource Reference**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/globalaccelerator_endpoint_group

## Notes for AI Agents

### Module Selection Guidance
- **Use Global Accelerator** for global, health-based routing with static anycast IPs and instant regional failover.
- **Use the `custom-routing` submodule** only when the workload needs deterministic per-flow routing to specific VPC subnet destinations (gaming/VoIP) — it has no health checks and no `client_affinity`/`protocol` on listeners.
- **Use CloudFront** instead for cacheable static/dynamic content delivery via edge caching.
- **Use Route 53 alone** for pure DNS-based geo/latency routing when static IPs and AWS backbone acceleration aren't required.
- **Use ALB/NLB directly** for single-region applications with no global traffic management need.

### Schema Gotchas (root module)
- `listeners` is a nested map: listener-level keys are `protocol`, `client_affinity`, `port_ranges`; each listener also carries its own `endpoint_groups` map.
- `endpoint_configuration` is a **list** of objects (`endpoint_id`, `weight`, `client_ip_preservation_enabled`, `attachment_arn`), not a map keyed by name.
- The port-mapping field is `port_override` (singular), a list of `{ endpoint_port, listener_port }` objects.
- Health check has a single `threshold_count` — there is no separate `healthy_threshold_count`/`unhealthy_threshold_count` as with ALB/NLB target groups.
- `name` defaults to `""`; always set it explicitly.
- `endpoint_group_region` is what makes an endpoint group multi-region — omit it to keep the endpoint group in the accelerator's default region context.

### Schema Gotchas (custom-routing submodule)
- Endpoint groups use `destination_configuration` (list of `{ from_port, to_port, protocols }`) and `endpoint_configuration` (list of `{ endpoint_id }` where `endpoint_id` is a **VPC subnet ID**, not an ALB/EC2/EIP identifier).
- No health-check fields and no `client_affinity`/`protocol` at the listener level.
- `endpoint_groups_timeouts` supports only `create`/`delete` (no `update`), unlike the root module's `endpoint_groups_timeouts`.

### Operational Gotchas
- Enabling `client_ip_preservation_enabled = true` on an ALB/EC2 endpoint causes AWS to create an unmanaged `GlobalAccelerator` security group in the target VPC; that SG must be deleted manually before the VPC can be destroyed, or `terraform destroy` will stall with a `DependencyViolation`.
- `endpoint_id` accepts an ALB/NLB ARN, an EC2 instance ID, or an Elastic IP allocation ID — the resource type must match what the endpoint actually is.
- Weight is a relative value (0-255) across the endpoints in one endpoint group, not a percentage; use `traffic_dial_percentage` to control the share of traffic reaching an entire endpoint group.
