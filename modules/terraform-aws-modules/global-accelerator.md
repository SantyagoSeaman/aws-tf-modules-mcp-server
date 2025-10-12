---
module_name: terraform-aws-global-accelerator
keywords: [global-accelerator, anycast, static-ip, edge-network, low-latency, high-availability, traffic-routing, endpoint-groups, listeners, health-checks, flow-logs, tcp, udp, dual-stack, ipv4, ipv6, byoip, client-affinity, custom-routing, multi-region, traffic-distribution, disaster-recovery, failover, performance-optimization, aws-edge-locations]
---

# AWS Global Accelerator Terraform Module

## Module Information

- **Source**: `terraform-aws-modules/global-accelerator/aws`
- **Version**: 3.0.0
- **Terraform**: >= 1.0
- **AWS Provider**: >= 5.84
- **License**: Apache-2.0

## Description

Terraform module that creates and manages AWS Global Accelerator resources for improving application performance and availability across global users. AWS Global Accelerator is a network service that provides static IP addresses as fixed entry points to applications and routes traffic over the AWS global network to optimize performance, reduce latency, and increase throughput. The service uses anycast routing from AWS edge locations to direct user traffic to the nearest healthy endpoint, continuously monitoring endpoint health and instantly rerouting traffic when failures are detected.

This module supports creating standard accelerators for automatic traffic routing based on geography and endpoint health, as well as custom routing accelerators for application-specific routing logic. It manages the complete lifecycle of Global Accelerator resources including accelerator configuration, listeners for TCP and UDP protocols, endpoint groups spanning multiple AWS regions, and individual endpoint configurations. The module provides comprehensive health check configuration, traffic distribution controls with endpoint weighting, client IP preservation options, and flow logging for traffic analysis.

Global Accelerator integrates with Application Load Balancers, Network Load Balancers, EC2 instances, and Elastic IP addresses as endpoints, supporting both IPv4 and dual-stack (IPv4/IPv6) configurations. The module simplifies multi-region deployments with automatic failover, enables Bring Your Own IP (BYOIP) for using existing IP addresses, and supports fine-grained traffic control through port overrides and client affinity settings. This makes it ideal for applications requiring consistent performance, high availability, and simplified global traffic management.

## Key Features

- **Standard Accelerator**: Create Global Accelerators that automatically route traffic to optimal endpoints based on geography and health
- **Static Anycast IP Addresses**: Provides two static IPv4 addresses (or four with dual-stack) as permanent entry points to applications
- **Dual-Stack Support**: IPv4 and IPv6 address support with dual-stack DNS names for modern networking requirements
- **Bring Your Own IP (BYOIP)**: Use your own IP address ranges with Global Accelerator for brand consistency and IP reputation preservation
- **Multiple Listeners**: Configure TCP and UDP listeners with flexible port ranges and protocol-specific settings
- **Client Affinity**: Support for SOURCE_IP affinity to maintain persistent connections to the same endpoint
- **Endpoint Groups**: Define endpoint groups spanning multiple AWS regions for geographic distribution and failover
- **Multi-Region Support**: Deploy endpoints across multiple AWS regions with automatic health-based routing
- **Health Check Configuration**: Customizable health check intervals, thresholds, and protocols for endpoint monitoring
- **Traffic Distribution**: Configure traffic dial percentage and endpoint weights for granular traffic control
- **Endpoint Types**: Support for Application Load Balancers, Network Load Balancers, EC2 instances, and Elastic IP addresses
- **Client IP Preservation**: Option to preserve client IP addresses for Application Load Balancer and EC2 endpoints
- **Port Overrides**: Override default endpoint ports for flexible traffic routing configurations
- **Flow Logs**: Enable VPC Flow Logs to S3 for traffic analysis and security monitoring
- **Custom Routing Accelerator**: Dedicated submodule for application-specific routing with VPC subnet endpoints
- **Automatic Failover**: Instant traffic rerouting when endpoint health checks fail
- **Timeouts Configuration**: Customizable create, update, and delete timeouts for listeners and endpoint groups
- **Conditional Creation**: Control resource creation with feature flags for flexible deployment patterns
- **Tag Support**: Comprehensive tagging for cost allocation and resource management

## Use Cases

- **Global Application Delivery**: Provide consistent low-latency performance for applications serving users across multiple continents and regions
- **Disaster Recovery and Failover**: Implement multi-region failover with instant automatic traffic rerouting when primary endpoints become unhealthy
- **Gaming and Real-Time Applications**: Reduce latency and jitter for gaming, VoIP, and other latency-sensitive applications using custom routing
- **IoT and Edge Computing**: Route IoT device traffic to nearest processing endpoints for reduced latency and improved response times
- **API Gateway Performance**: Improve API response times for globally distributed clients accessing RESTful or GraphQL APIs
- **Content Delivery**: Accelerate dynamic content delivery that cannot be cached at edge locations like personalized web applications
- **Multi-Region Load Balancing**: Distribute traffic across Application Load Balancers or Network Load Balancers in multiple AWS regions
- **Blue-Green Deployments**: Implement zero-downtime deployments by shifting traffic between endpoint groups with traffic dial controls
- **Hybrid Cloud Connectivity**: Provide consistent IP addresses for applications spanning AWS and on-premises data centers
- **DDoS Protection**: Benefit from AWS Shield Standard protection at AWS edge locations for improved application security

## Submodules

### custom-routing

Creates AWS Global Accelerator custom routing accelerators for application-specific traffic routing with granular control over destination selection.

**Purpose**: Provision custom routing accelerators that allow applications to use custom logic to direct specific users to particular destinations among many potential endpoints, ideal for gaming, VoIP, and specialized routing requirements.

**Key Features**:
- Support for application-specific routing logic to VPC subnet endpoints
- Static anycast IP addresses with AWS global network routing
- Custom port range configuration for destination endpoints
- VPC subnet endpoint types (EC2 instances within subnets)
- Flow logs support for traffic analysis
- Dual-stack IPv4/IPv6 support
- BYOIP (Bring Your Own IP) support
- Listener and endpoint group configuration similar to standard accelerators
- Custom routing allows mapping specific users to specific destinations
- Ideal for multiplayer gaming servers and voice/video applications

**Variables** (key ones):
- `name` (string): Name of the custom routing accelerator
- `enabled` (bool): Whether the accelerator is enabled (default: true)
- `ip_address_type` (string): Address type - "IPV4" or "DUAL_STACK" (default: "IPV4")
- `ip_addresses` (list(string)): IP addresses for BYOIP accelerators (default: [])
- `flow_logs_enabled` (bool): Enable flow logs (default: false)
- `flow_logs_s3_bucket` (string): S3 bucket for flow logs
- `flow_logs_s3_prefix` (string): S3 prefix for flow log files
- `listeners` (any): Map of listener configurations with port ranges and protocols
- `create_listeners` (bool): Whether to create listeners (default: true)
- `listeners_timeouts` (map(string)): Timeout configuration for listener operations
- `endpoint_groups_timeouts` (map(string)): Timeout configuration for endpoint group operations
- `tags` (map(string)): Tags to apply to resources

**Outputs**:
- `id`: ID (ARN) of the custom routing accelerator
- `arn`: Amazon Resource Name of the custom routing accelerator
- `dns_name`: DNS name of the custom routing accelerator
- `hosted_zone_id`: Route 53 zone ID for alias record creation
- `ip_sets`: IP address sets associated with the accelerator
- `listeners`: Map of created listeners and their attributes
- `endpoint_groups`: Map of created endpoint groups and their attributes

**Usage Example**:
```hcl
module "global_accelerator_custom_routing" {
  source = "terraform-aws-modules/global-accelerator/aws//modules/custom-routing"

  name                = "gaming-accelerator"
  enabled             = true
  ip_address_type     = "IPV4"
  flow_logs_enabled   = true
  flow_logs_s3_bucket = aws_s3_bucket.flow_logs.id
  flow_logs_s3_prefix = "custom-routing/"

  # Custom routing listeners
  listeners = {
    game_servers = {
      port_ranges = [
        {
          from_port = 7000
          to_port   = 7999
        }
      ]
    }
  }

  tags = {
    Environment = "production"
    Application = "gaming"
    Type        = "custom-routing"
  }
}

# VPC subnet endpoint group for custom routing
resource "aws_globalaccelerator_custom_routing_endpoint_group" "game_servers" {
  listener_arn = module.global_accelerator_custom_routing.listeners["game_servers"].arn

  endpoint_configuration {
    endpoint_id = aws_subnet.game_servers.id
  }

  destination_configuration {
    from_port = 7000
    to_port   = 7999
    protocols = ["UDP"]
  }
}
```

## Variables

### Core Accelerator Configuration
- `create` (bool): Controls if resources should be created (default: true)
- `tags` (map(string)): Map of tags to add to all resources (default: {})
- `name` (string): Name of the accelerator (required)
- `enabled` (bool): Indicates whether the accelerator is enabled (default: true)
- `ip_address_type` (string): Address type - "IPV4" or "DUAL_STACK" (default: "IPV4")
- `ip_addresses` (list(string)): IP addresses to use for BYOIP accelerators (default: [])

### Flow Logs Configuration
- `flow_logs_enabled` (bool): Indicates whether flow logs are enabled (default: false)
- `flow_logs_s3_bucket` (string): Name of Amazon S3 bucket for flow logs (default: null)
- `flow_logs_s3_prefix` (string): Prefix for location in S3 bucket for flow logs (default: null)

### Listener Configuration
- `create_listeners` (bool): Controls if listeners should be created (default: true)
- `listeners` (any): Map of listener definitions to create (default: {})
  - Each listener can specify:
    - `port_ranges`: List of port range objects with `from_port` and `to_port`
    - `protocol`: "TCP" or "UDP"
    - `client_affinity`: "NONE" or "SOURCE_IP"
    - `endpoint_group`: Endpoint group configuration (see below)
- `listeners_timeouts` (map(string)): Create, update, and delete timeout configurations for listeners (default: {})

### Endpoint Group Configuration
Within each listener's `endpoint_group` block:
- `health_check_interval_seconds` (number): Health check interval in seconds (default: 30)
- `health_check_path` (string): Path for HTTP/HTTPS health checks (default: "/")
- `health_check_port` (number): Port for health checks (default: listener port)
- `health_check_protocol` (string): Protocol for health checks - "TCP", "HTTP", or "HTTPS" (default: "TCP")
- `threshold_count` (number): Number of consecutive health checks before status change (default: 3)
- `traffic_dial_percentage` (number): Percentage of traffic to dial to endpoint group (default: 100)
- `endpoint_configuration`: List of endpoint configurations
  - `endpoint_id`: ID of endpoint (ALB, NLB, EC2, or EIP)
  - `weight` (number): Endpoint weight for traffic distribution (default: 100)
  - `client_ip_preservation_enabled` (bool): Preserve client IP address (default: false)
- `port_override`: List of port override configurations
  - `endpoint_port`: Destination port on endpoint
  - `listener_port`: Source port from listener

### Timeouts
- `endpoint_groups_timeouts` (map(string)): Create, update, and delete timeout configurations for endpoint groups (default: {})

## Outputs

### Accelerator Information
- `id`: Amazon Resource Name (ARN) of the accelerator
- `arn`: Amazon Resource Name (ARN) of the accelerator
- `dns_name`: DNS name of the accelerator (e.g., a1234567890abcdef.awsglobalaccelerator.com)
- `dual_stack_dns_name`: DNS name that points to both IPv4 and IPv6 addresses of the accelerator
- `hosted_zone_id`: Global Accelerator Route 53 zone ID for creating alias records

### IP Addresses
- `ip_sets`: IP address set associated with the accelerator
  - Contains `ip_addresses` list and `ip_family` (IPv4 or IPv6)

### Listener Information
- `listeners`: Map of created listeners and their attributes
  - Includes ARN, client affinity, protocol, and port ranges for each listener

### Endpoint Groups
- `endpoint_groups`: Map of created endpoint groups and their attributes
  - Includes ARN, endpoint configurations, health check settings, and traffic dial percentage

## Usage Examples

### Basic Global Accelerator

```hcl
module "global_accelerator_basic" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name    = "my-accelerator"
  enabled = true

  listeners = {
    http = {
      port_ranges = [
        {
          from_port = 80
          to_port   = 80
        }
      ]
      protocol        = "TCP"
      client_affinity = "SOURCE_IP"

      endpoint_group = {
        health_check_protocol = "HTTP"
        health_check_path     = "/health"

        endpoint_configuration = [
          {
            endpoint_id = aws_lb.main.arn
            weight      = 100
          }
        ]
      }
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Multi-Region Global Accelerator

```hcl
module "global_accelerator_multi_region" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name                = "multi-region-app"
  enabled             = true
  ip_address_type     = "IPV4"
  flow_logs_enabled   = true
  flow_logs_s3_bucket = aws_s3_bucket.logs.id
  flow_logs_s3_prefix = "global-accelerator/"

  listeners = {
    https = {
      port_ranges = [
        {
          from_port = 443
          to_port   = 443
        }
      ]
      protocol        = "TCP"
      client_affinity = "SOURCE_IP"

      # Primary endpoint group in us-east-1
      endpoint_group = {
        endpoint_group_region         = "us-east-1"
        health_check_interval_seconds = 30
        health_check_protocol         = "HTTPS"
        health_check_path             = "/health"
        threshold_count               = 3
        traffic_dial_percentage       = 100

        endpoint_configuration = [
          {
            endpoint_id                    = aws_lb.us_east.arn
            weight                         = 100
            client_ip_preservation_enabled = true
          }
        ]
      }
    }

    # Secondary endpoint group configuration
    https_secondary = {
      port_ranges = [
        {
          from_port = 443
          to_port   = 443
        }
      ]
      protocol        = "TCP"
      client_affinity = "SOURCE_IP"

      endpoint_group = {
        endpoint_group_region         = "eu-west-1"
        health_check_interval_seconds = 30
        health_check_protocol         = "HTTPS"
        health_check_path             = "/health"
        threshold_count               = 3
        traffic_dial_percentage       = 50  # 50% traffic to secondary region

        endpoint_configuration = [
          {
            endpoint_id                    = aws_lb.eu_west.arn
            weight                         = 100
            client_ip_preservation_enabled = true
          }
        ]
      }
    }
  }

  tags = {
    Environment = "production"
    MultiRegion = "true"
  }
}
```

### Global Accelerator with Multiple Endpoints

```hcl
module "global_accelerator_multiple_endpoints" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name    = "multi-endpoint-accelerator"
  enabled = true

  listeners = {
    app = {
      port_ranges = [
        {
          from_port = 80
          to_port   = 80
        },
        {
          from_port = 443
          to_port   = 443
        }
      ]
      protocol = "TCP"

      endpoint_group = {
        health_check_protocol         = "TCP"
        health_check_interval_seconds = 10
        threshold_count               = 2

        endpoint_configuration = [
          {
            endpoint_id = aws_lb.primary.arn
            weight      = 70  # 70% of traffic
          },
          {
            endpoint_id = aws_lb.secondary.arn
            weight      = 30  # 30% of traffic
          }
        ]
      }
    }
  }

  tags = {
    Environment     = "production"
    LoadDistribution = "weighted"
  }
}
```

### Dual-Stack Global Accelerator

```hcl
module "global_accelerator_dual_stack" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name            = "dual-stack-accelerator"
  enabled         = true
  ip_address_type = "DUAL_STACK"  # Provides both IPv4 and IPv6

  listeners = {
    web = {
      port_ranges = [
        {
          from_port = 443
          to_port   = 443
        }
      ]
      protocol = "TCP"

      endpoint_group = {
        health_check_protocol = "HTTPS"
        health_check_path     = "/health"

        endpoint_configuration = [
          {
            endpoint_id                    = aws_lb.main.arn
            weight                         = 100
            client_ip_preservation_enabled = true
          }
        ]
      }
    }
  }

  tags = {
    Environment = "production"
    IPVersion   = "dual-stack"
  }
}

# Create Route 53 alias records for both IPv4 and IPv6
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

### Global Accelerator with Port Override

```hcl
module "global_accelerator_port_override" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name    = "port-override-accelerator"
  enabled = true

  listeners = {
    custom_ports = {
      port_ranges = [
        {
          from_port = 80
          to_port   = 80
        },
        {
          from_port = 8080
          to_port   = 8080
        }
      ]
      protocol = "TCP"

      endpoint_group = {
        endpoint_configuration = [
          {
            endpoint_id = aws_lb.main.arn
            weight      = 100
          }
        ]

        # Override ports for specific endpoints
        port_override = [
          {
            endpoint_port = 8443  # Backend listens on 8443
            listener_port = 80    # Client connects to 80
          },
          {
            endpoint_port = 8443  # Backend listens on 8443
            listener_port = 8080  # Client connects to 8080
          }
        ]
      }
    }
  }

  tags = {
    Environment  = "production"
    PortOverride = "enabled"
  }
}
```

### Global Accelerator with UDP Protocol

```hcl
module "global_accelerator_udp" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name    = "udp-accelerator"
  enabled = true

  listeners = {
    dns = {
      port_ranges = [
        {
          from_port = 53
          to_port   = 53
        }
      ]
      protocol = "UDP"

      endpoint_group = {
        health_check_protocol         = "TCP"
        health_check_port             = 53
        health_check_interval_seconds = 10
        threshold_count               = 2

        endpoint_configuration = [
          {
            endpoint_id = aws_eip.dns_server_1.id
            weight      = 50
          },
          {
            endpoint_id = aws_eip.dns_server_2.id
            weight      = 50
          }
        ]
      }
    }

    gaming = {
      port_ranges = [
        {
          from_port = 7000
          to_port   = 7100
        }
      ]
      protocol = "UDP"

      endpoint_group = {
        endpoint_configuration = [
          {
            endpoint_id = aws_instance.game_server.id
            weight      = 100
          }
        ]
      }
    }
  }

  tags = {
    Environment = "production"
    Protocol    = "UDP"
  }
}
```

### Global Accelerator with BYOIP

```hcl
module "global_accelerator_byoip" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name         = "byoip-accelerator"
  enabled      = true
  ip_addresses = [
    aws_eip.byoip_1.id,
    aws_eip.byoip_2.id
  ]

  listeners = {
    web = {
      port_ranges = [
        {
          from_port = 443
          to_port   = 443
        }
      ]
      protocol = "TCP"

      endpoint_group = {
        endpoint_configuration = [
          {
            endpoint_id = aws_lb.main.arn
            weight      = 100
          }
        ]
      }
    }
  }

  tags = {
    Environment = "production"
    BYOIP       = "true"
  }
}

# BYOIP Elastic IPs (requires prior BYOIP setup)
resource "aws_eip" "byoip_1" {
  domain               = "vpc"
  public_ipv4_pool     = "ipv4pool-ec2-012345abcde67890f"
  network_border_group = "us-west-2"
}

resource "aws_eip" "byoip_2" {
  domain               = "vpc"
  public_ipv4_pool     = "ipv4pool-ec2-012345abcde67890f"
  network_border_group = "us-west-2"
}
```

### Blue-Green Deployment with Global Accelerator

```hcl
module "global_accelerator_blue_green" {
  source  = "terraform-aws-modules/global-accelerator/aws"
  version = "~> 3.0"

  name    = "blue-green-accelerator"
  enabled = true

  listeners = {
    app = {
      port_ranges = [
        {
          from_port = 443
          to_port   = 443
        }
      ]
      protocol        = "TCP"
      client_affinity = "SOURCE_IP"

      endpoint_group = {
        # Gradually shift traffic from blue to green
        traffic_dial_percentage = 50  # Adjust this to shift traffic

        endpoint_configuration = [
          {
            endpoint_id = aws_lb.blue.arn
            weight      = 90  # Blue environment - decreasing traffic
          },
          {
            endpoint_id = aws_lb.green.arn
            weight      = 10  # Green environment - increasing traffic
          }
        ]
      }
    }
  }

  tags = {
    Environment    = "production"
    DeploymentType = "blue-green"
  }
}
```

## Best Practices

### Architecture and Design

1. **Use Global Accelerator for Global Applications**: Deploy Global Accelerator when serving users across multiple geographic regions to reduce latency and improve availability through AWS's global network.
2. **Combine with Route 53**: Create Route 53 alias records pointing to Global Accelerator DNS names for branded domain names while maintaining static IP benefits.
3. **Multi-Region Endpoint Strategy**: Deploy endpoints across at least two AWS regions to ensure high availability and automatic failover capabilities.
4. **Choose Appropriate Endpoint Types**: Use Application Load Balancers for HTTP/HTTPS traffic, Network Load Balancers for TCP/UDP, and EC2/EIP for specialized applications.
5. **Standard vs Custom Routing**: Use standard accelerators for most applications with automatic routing; reserve custom routing for specialized use cases like gaming or VoIP requiring application-specific destination selection.
6. **Client IP Preservation Planning**: Enable client IP preservation for Application Load Balancers and EC2 instances when applications need source IP for logging, security, or compliance.

### Listener Configuration

7. **Consolidate Port Ranges**: Group related ports into single listeners with multiple port ranges to simplify management and reduce resource count.
8. **Use Client Affinity Appropriately**: Enable SOURCE_IP client affinity for applications requiring session persistence to the same endpoint, such as WebSocket connections or stateful applications.
9. **Protocol Selection**: Choose TCP for connection-oriented traffic (HTTP, HTTPS, database connections) and UDP for connectionless traffic (DNS, gaming, VoIP, streaming).
10. **Avoid Overlapping Port Ranges**: Ensure port ranges across listeners don't overlap to prevent routing conflicts and undefined behavior.

### Endpoint Group Management

11. **Configure Health Checks Properly**: Set health check intervals (10-30 seconds) and thresholds (2-3) appropriate for your application's failure detection and recovery requirements.
12. **Use HTTP/HTTPS Health Checks**: For web applications, use HTTP or HTTPS health checks with specific paths (e.g., "/health") for more accurate endpoint health assessment than TCP checks.
13. **Adjust Traffic Dial Carefully**: Use traffic dial percentage for gradual rollouts, blue-green deployments, or A/B testing; change values incrementally (10-20% steps) to monitor impact.
14. **Weight Endpoints Strategically**: Distribute traffic proportionally across endpoints using weights based on capacity, cost, or performance testing results.
15. **Group Endpoints by Region**: Create separate endpoint groups for each region to enable region-level traffic control and failover strategies.
16. **Monitor Endpoint Health**: Set up CloudWatch alarms for unhealthy endpoint counts to receive notifications when endpoints fail and traffic shifts.

### Performance Optimization

17. **Enable Client IP Preservation**: For Application Load Balancers, enable client IP preservation to allow backend applications to see original client IPs without parsing X-Forwarded-For headers.
18. **Use Port Overrides for Flexibility**: Configure port overrides when backend services listen on different ports than client-facing ports for security or architectural reasons.
19. **Optimize Health Check Settings**: Balance health check frequency and threshold count - more frequent checks (10s) with lower thresholds (2) provide faster failover but increase network overhead.
20. **Co-locate with Endpoints**: Deploy Global Accelerator endpoints in regions closest to your actual application infrastructure to minimize hops within AWS network.
21. **Test Failover Timing**: Regularly test endpoint failure scenarios to validate failover happens within expected timeframes (typically 30-60 seconds based on health check settings).

### Security and Compliance

22. **Enable Flow Logs**: Activate flow logs to S3 for security analysis, traffic pattern analysis, compliance auditing, and troubleshooting connectivity issues.
23. **Use VPC Endpoints When Possible**: For internal applications, deploy endpoints in VPCs rather than exposing them to internet to reduce attack surface.
24. **Implement Defense in Depth**: Combine Global Accelerator with AWS Shield Standard (included), AWS WAF (for ALB endpoints), and VPC security groups for comprehensive protection.
25. **Rotate BYOIP Addresses**: If using BYOIP, maintain rotation schedules and have procedures to switch between address pools for security or reputation management.
26. **Restrict Flow Log Access**: Apply least-privilege IAM policies to S3 buckets containing flow logs; enable bucket encryption and access logging.
27. **Monitor for Anomalies**: Use CloudWatch Logs Insights or Athena to analyze flow logs for traffic anomalies, DDoS attempts, or suspicious patterns.

### High Availability and Disaster Recovery

28. **Deploy Three or More Endpoints**: Configure at least three endpoints across multiple regions to maintain service even if entire regions become unavailable.
29. **Test Regional Failover**: Regularly simulate regional failures by marking endpoints unhealthy to validate Global Accelerator reroutes traffic correctly to healthy regions.
30. **Set Appropriate Threshold Counts**: Use threshold count of 2-3 for production to avoid false positives from transient network issues while maintaining quick failure detection.
31. **Maintain Sufficient Capacity**: Ensure endpoints in secondary regions can handle full traffic load if primary region fails; avoid over-reliance on traffic dial percentage.
32. **Document Failover Procedures**: Create runbooks for manual intervention scenarios, including how to adjust traffic dial, add/remove endpoints, or disable accelerator.
33. **Use Multiple Availability Zones**: Deploy Application Load Balancers and Network Load Balancers across multiple AZs within each region for intra-region resilience.

### Cost Optimization

34. **Understand Pricing Model**: Global Accelerator charges hourly for accelerator and data transfer; review pricing for standard vs. custom routing accelerators as costs differ.
35. **Consolidate Accelerators**: Share single accelerator across multiple applications using different listener ports to reduce hourly charges.
36. **Use Traffic Dial for Cost Control**: Reduce traffic dial percentage to secondary regions during normal operations, increasing only during primary region issues.
37. **Monitor Data Transfer Costs**: Track data transfer OUT from AWS per GB; use CloudWatch metrics and cost allocation tags to monitor and optimize.
38. **Right-Size Flow Logs**: Enable flow logs selectively for production accelerators or specific time periods rather than continuously for all environments.
39. **Disable Unused Accelerators**: Set `enabled = false` or destroy accelerators not actively serving traffic to avoid hourly charges.
40. **Evaluate Cost vs Benefit**: Compare Global Accelerator costs against benefits (performance improvement, simplified management) for your specific use case.

### Operational Excellence

41. **Use Infrastructure as Code**: Manage all Global Accelerator resources through Terraform for version control, peer review, and reproducible deployments.
42. **Implement Comprehensive Tagging**: Apply tags for environment, application, cost center, owner, and purpose to all accelerators for cost allocation and resource management.
43. **Monitor Key Metrics**: Track CloudWatch metrics including processed bytes, new flows, active flows, and endpoint health to understand traffic patterns.
44. **Set Up CloudWatch Alarms**: Create alarms for critical metrics like unhealthy endpoint count, flow count anomalies, or unexpected endpoint group changes.
45. **Version Control Configuration**: Store all Terraform configurations in Git with proper branching strategy and require peer review for production changes.
46. **Document Accelerator Purpose**: Maintain clear documentation of what each accelerator serves, which applications depend on it, and contact information for owners.
47. **Test in Non-Production First**: Validate all configuration changes (health check intervals, traffic dial, endpoint weights) in development or staging before production.
48. **Plan Maintenance Windows**: Schedule endpoint maintenance during low-traffic periods; use traffic dial to gracefully shift traffic before taking endpoints offline.

### Monitoring and Observability

49. **Enable CloudWatch Metrics**: Monitor all available CloudWatch metrics including new connections per second, active connections, and data processed to establish baselines.
50. **Create Custom Dashboards**: Build CloudWatch dashboards visualizing accelerator health, endpoint status, traffic distribution, and performance metrics.
51. **Analyze Flow Logs Regularly**: Use Athena or CloudWatch Logs Insights to query flow logs for traffic patterns, top talkers, geographic distribution, and security analysis.
52. **Set Up SNS Notifications**: Configure CloudWatch alarms to send SNS notifications to operations teams when endpoint health degrades or traffic patterns anomalies occur.
53. **Track Configuration Changes**: Enable AWS Config to track Global Accelerator resource changes over time for compliance and troubleshooting.
54. **Correlate with Application Metrics**: Compare Global Accelerator metrics with application-level metrics (latency, error rates) to identify performance issues.

## Additional Resources

### Official Documentation
- **AWS Global Accelerator Documentation**: https://docs.aws.amazon.com/global-accelerator/
- **Terraform AWS Global Accelerator Module GitHub**: https://github.com/terraform-aws-modules/terraform-aws-global-accelerator
- **Terraform Registry - Global Accelerator Module**: https://registry.terraform.io/modules/terraform-aws-modules/global-accelerator/aws

### User Guides
- **What is AWS Global Accelerator**: https://docs.aws.amazon.com/global-accelerator/latest/dg/what-is-global-accelerator.html
- **How Global Accelerator Works**: https://docs.aws.amazon.com/global-accelerator/latest/dg/introduction-how-it-works.html
- **Custom Routing Accelerators**: https://docs.aws.amazon.com/global-accelerator/latest/dg/about-custom-routing-accelerators.html
- **Endpoints for Standard Accelerators**: https://docs.aws.amazon.com/global-accelerator/latest/dg/about-endpoints.html

### Configuration and Management
- **Creating an Accelerator**: https://docs.aws.amazon.com/global-accelerator/latest/dg/about-accelerators.html
- **Listeners in Global Accelerator**: https://docs.aws.amazon.com/global-accelerator/latest/dg/about-listeners.html
- **Endpoint Groups**: https://docs.aws.amazon.com/global-accelerator/latest/dg/about-endpoint-groups.html
- **Preserve Client IP Addresses**: https://docs.aws.amazon.com/global-accelerator/latest/dg/preserve-client-ip-address.html

### Monitoring and Logging
- **Flow Logs**: https://docs.aws.amazon.com/global-accelerator/latest/dg/monitoring-global-accelerator.flow-logs.html
- **CloudWatch Metrics**: https://docs.aws.amazon.com/global-accelerator/latest/dg/cloudwatch-monitoring.html
- **CloudWatch Alarms**: https://docs.aws.amazon.com/global-accelerator/latest/dg/cloudwatch-alarms.html

### Advanced Features
- **Bring Your Own IP (BYOIP)**: https://docs.aws.amazon.com/global-accelerator/latest/dg/using-byoip.html
- **Client Affinity**: https://docs.aws.amazon.com/global-accelerator/latest/dg/about-listeners.html#about-listeners-client-affinity

### Pricing and Support
- **Global Accelerator Pricing**: https://aws.amazon.com/global-accelerator/pricing/
- **AWS Global Accelerator FAQ**: https://aws.amazon.com/global-accelerator/faqs/

## Notes for AI Agents

### Module Selection Guidance
- **Use Global Accelerator** when applications serve global users and require consistent low latency, static IP addresses, instant failover, or simplified multi-region traffic management.
- **Use CloudFront** instead for caching static content, CDN distribution, or when edge caching provides sufficient performance improvement.
- **Use Route 53** alone for DNS-based routing with geographic or latency-based policies when static IPs and AWS network acceleration aren't required.
- **Use ALB/NLB directly** for single-region applications where global traffic management and static anycast IPs provide no benefit.

### Architecture Recommendations
- For **global web applications**: Use standard accelerator with Application Load Balancers in 2-3 regions, enable client IP preservation, configure HTTPS health checks.
- For **gaming/VoIP applications**: Use custom routing accelerator with UDP protocol, VPC subnet endpoints, and application-specific destination selection logic.
- For **API services**: Standard accelerator with NLBs or ALBs, multiple endpoint groups, weighted traffic distribution for canary testing.
- For **disaster recovery**: Deploy endpoints in geographically diverse regions (US, Europe, Asia-Pacific), set aggressive health check intervals (10s), use traffic dial for controlled failover.
- For **hybrid cloud**: Combine Global Accelerator with AWS PrivateLink or Site-to-Site VPN for seamless connectivity between AWS and on-premises endpoints.

### Common Configuration Patterns
- **Basic Production**: Single listener (port 443), 2 endpoint groups (primary + secondary region), ALB endpoints, traffic dial 100%/50%, client IP preservation enabled.
- **High Availability**: Multiple listeners, 3+ endpoint groups across regions, equal endpoint weights, aggressive health checks (10s interval, threshold 2).
- **Blue-Green Deployment**: Single endpoint group with 2 endpoints (blue/green), adjust weights gradually (90/10 → 50/50 → 10/90), SOURCE_IP affinity.
- **Multi-Protocol**: TCP listener (ports 80, 443) for web traffic, UDP listener (port 53) for DNS, separate endpoint groups per protocol.
- **Custom Routing**: Gaming/VoIP with UDP listeners, VPC subnet endpoints, port ranges matching game server ports (7000-7999).

### Endpoint Type Selection
- **Application Load Balancer**: Best for HTTP/HTTPS traffic, supports client IP preservation, path-based routing at ALB level, integrates with AWS WAF.
- **Network Load Balancer**: Ideal for TCP/UDP traffic requiring extreme performance, static IPs at NLB level, connection-based load balancing.
- **EC2 Instance**: Direct-to-instance routing for specialized applications, requires public Elastic IP, suitable for custom protocols or appliances.
- **Elastic IP**: Similar to EC2 but more flexible for different instance types; useful when instances frequently change but IPs must remain static.

### Health Check Configuration
- **Web applications**: Use HTTP/HTTPS health checks with specific paths (/health, /status), 30s interval, threshold 3 for balanced detection.
- **TCP applications**: Use TCP health checks, 10-15s interval, threshold 2 for faster failover detection.
- **Production systems**: 30s interval, threshold 3 for stability; aggressive requirements may cause false positives during network blips.
- **Development/staging**: 60s interval, threshold 5 for cost savings and reduced check overhead.

### Security Best Practices
- **Always enable flow logs** for production accelerators to maintain audit trails and enable security analysis.
- **Use AWS Shield** (included automatically) for DDoS protection; consider Shield Advanced for additional protection and cost protection guarantees.
- **Implement WAF** on Application Load Balancer endpoints for application-layer protection against common attacks (SQL injection, XSS).
- **Restrict endpoint access** using security groups that only allow traffic from Global Accelerator IP ranges (not general internet).
- **Encrypt in transit** by using HTTPS listeners and HTTPS backends; Global Accelerator terminates and re-establishes connections at edge.

### Troubleshooting Tips
- **Endpoints showing unhealthy**: Check security group rules allow health check traffic, verify health check path returns 200 OK, confirm endpoint is actually healthy.
- **High latency**: Verify endpoints are in multiple regions close to users, check endpoint application performance, review CloudWatch metrics for bottlenecks.
- **Traffic not routing**: Confirm accelerator is enabled, check listener port ranges match client requests, verify endpoint group has healthy endpoints.
- **Failover not working**: Review threshold count and health check interval, ensure multiple endpoints exist, check CloudWatch alarms for endpoint health.
- **Client IP not preserved**: Verify endpoint type supports preservation (ALB or EC2), check client_ip_preservation_enabled is true, confirm application reads correct header.

### Cost Estimation
- **Hourly charge**: ~$0.025/hour per accelerator (varies by region) = ~$18/month per accelerator base cost.
- **Data transfer**: $0.015-0.020 per GB for data transfer out from AWS through Global Accelerator (varies by destination region).
- **Flow logs**: Additional S3 storage costs for logs (varies by volume); typical production accelerator generates 1-10 GB/day.
- **Endpoints**: Separate charges for underlying resources (ALB, NLB, EC2, data transfer); Global Accelerator adds overhead but provides value through performance improvement.
- **Optimization**: Share accelerators across applications, disable unused accelerators, use traffic dial to reduce secondary region data transfer.

### Integration Patterns
- **Route 53 + Global Accelerator**: Create alias records pointing to accelerator DNS for branded domains while maintaining static IPs.
- **ALB + Global Accelerator**: ALB handles path-based routing and host-based routing, Global Accelerator handles multi-region traffic management.
- **CloudWatch + Global Accelerator**: Monitor accelerator metrics, endpoint health, create alarms for unhealthy endpoints, analyze flow logs.
- **Terraform + Global Accelerator**: Manage all configuration as code, use workspaces for multi-environment deployments, implement CI/CD for changes.
- **Multi-account**: Create accelerator in central networking account, use cross-account ALB/NLB endpoints via resource sharing.
