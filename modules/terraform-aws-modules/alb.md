# Terraform AWS ALB Module

## Module Information

- **Module Name**: `alb`
- **Source**: `terraform-aws-modules/alb/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-alb
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/latest
- **Latest Version**: 10.5.0
- **Purpose**: Creates Application Load Balancers (ALB), Network Load Balancers (NLB), and Gateway Load Balancers with listeners, listener rules, target groups, security groups, and Route53 DNS records
- **Service**: AWS ELB (Elastic Load Balancing)
- **Category**: Networking, Compute, Security
- **Keywords**: alb, application-load-balancer, nlb, load-balancer, gateway-load-balancer, target-group, listener, https, tls, mutual-tls, health-check, security-group, waf, cognito, oidc, jwt, canary-deployment, route53
- **Use For**: distributing HTTP/HTTPS traffic across web servers or containers, high availability for internet-facing and internal applications, SSL/TLS termination, path-based and host-based routing, centralized authentication with Cognito/OIDC/JWT, ultra-high-performance TCP/UDP load balancing with static IPs, canary and weighted/blue-green deployments, WAF-protected internet-facing endpoints, mutual TLS (mTLS) client-certificate authentication, third-party network appliance traffic inspection via Gateway Load Balancer

## Description

This module creates and manages AWS Application Load Balancers (ALB), Network Load Balancers (NLB), and Gateway Load Balancers (GWLB) through a single, unified interface driven by `listeners` and `target_groups` map variables. ALBs operate at Layer 7, providing HTTP/HTTPS routing based on paths, hostnames, headers, query strings, and source IP; NLBs operate at Layer 4 for ultra-high-throughput TCP/UDP/TLS traffic with support for static/Elastic IPs and PrivateLink; Gateway Load Balancers transparently distribute traffic to fleets of third-party virtual appliances (firewalls, IDS/IPS) using the GENEVE protocol, for which the module automatically omits port/protocol on listeners.

The module manages the full set of load balancer resources: the `aws_lb` itself, listeners with default actions, listener rules with ordered conditions/actions, target groups (instance, IP, Lambda, or ALB targets) with health checks and attachments, a security group (or attachment of existing ones), and optional Route53 alias records. Listener and rule actions support `forward`, `weighted_forward` (multiple target groups with per-group weights and stickiness, for canary/blue-green rollouts), `redirect`, `fixed_response`, `authenticate_cognito`, `authenticate_oidc`, and `jwt_validation` (JWT claim validation at the load balancer, added in v10.3). Listener rules also support `transform` blocks to rewrite the host header or request URL using regex before forwarding.

Security-conscious defaults are built in: deletion protection, cross-zone load balancing, and dropping of invalid HTTP header fields are all enabled by default, and the HTTPS listener SSL policy defaults to `ELBSecurityPolicy-TLS13-1-3-2021-06`. Additional capabilities include WAF Web ACL association, mutual TLS (mTLS) via the bundled `lb_trust_store` submodule, access/connection/health-check logging to S3, IPAM pool and dual-stack IP allocation, minimum load balancer capacity reservation (pre-warming), and Route 53 Application Recovery Controller zonal shift support for AZ failover. The module outputs DNS names, ARNs, listener/rule/target-group maps, and security group IDs for composition with ASG, ECS, EKS, and DNS resources.

## Key Features

- **Multi-Type Load Balancer Support**: Application (ALB), Network (NLB), and Gateway (GWLB) load balancers from one module
- **Declarative Listeners & Rules**: Define listeners, default actions, and prioritized rules with conditions (path, host, header, query string, HTTP method, source IP) as nested maps
- **Advanced Routing Actions**: `forward`, `weighted_forward` (canary/blue-green with per-target-group weights and stickiness), `redirect`, and `fixed_response`
- **Authentication Integration**: Amazon Cognito (`authenticate_cognito`) and OIDC (`authenticate_oidc`) authentication actions, plus JWT claim validation (`jwt_validation`) directly at the listener/rule level
- **Header & URL Rewriting**: `transform` blocks on listener rules for regex-based host-header rewrite and URL rewrite
- **Mutual TLS (mTLS)**: Client certificate authentication via `mutual_authentication` on HTTPS listeners, backed by the `lb_trust_store` submodule (trust stores + certificate revocation lists)
- **Security Group Management**: Automatic creation with granular ingress/egress rule maps, or attach existing security group IDs
- **AWS WAF Integration**: Associate a Web ACL via `associate_web_acl`/`web_acl_arn`, with optional fail-open behavior
- **Comprehensive Logging**: Access logs, connection logs (NLB), and health-check logs (ALB) to S3
- **Route53 Integration**: Automatic creation of A/AAAA alias records pointed at the load balancer
- **Flexible Target Types**: Instance, IP, Lambda, and ALB targets, with additional standalone target-group attachments and gRPC (`protocol_version = "GRPC"`) support
- **Target Group Health Routing**: `target_group_health` (DNS/AZ failover thresholds) and `target_health_state` (unhealthy connection draining)
- **Capacity & Addressing**: `minimum_load_balancer_capacity` for pre-warmed LCU reservation, IPAM pool allocation, and dual-stack (`ipv4`/`dualstack`) IP addressing
- **Static IPs (NLB)**: `subnet_mapping` with Elastic IP allocation or private IPv4 for predictable addresses
- **Zonal Shift Support**: Route 53 Application Recovery Controller integration for Availability Zone failover

## Main Use Cases

1. **Web Application Load Balancing**: Distribute HTTP/HTTPS traffic across multiple web servers for high availability and scalability
2. **Microservices Traffic Routing**: Route requests to different services based on URL path, hostname, header, or query string
3. **SSL/TLS Offloading**: Terminate SSL/TLS at the load balancer to reduce compute overhead on backend targets
4. **Centralized Authentication**: Enforce Cognito, OIDC, or JWT-based authentication/authorization before traffic reaches backend applications
5. **High-Performance TCP/UDP Applications**: Use NLB for gaming, IoT, or real-time streaming workloads needing static IPs or extreme throughput
6. **Canary and Blue-Green Deployments**: Split traffic between target groups using `weighted_forward` for progressive, zero-downtime rollouts
7. **Container and Serverless Load Balancing**: Balance traffic across ECS, EKS, EC2, or Lambda targets (including gRPC services)
8. **Network Appliance Traffic Inspection**: Use Gateway Load Balancer to transparently insert third-party firewalls/IDS-IPS appliances into traffic paths
9. **Mutual TLS for B2B/Service APIs**: Require client certificates via `lb_trust_store` for partner integrations or service-to-service authentication
10. **Security and Compliance**: Integrate WAF for threat protection and enable access/connection/health-check logging for audit trails

## Submodules

### 1. lb_trust_store

- **Purpose**: Create and manage trust stores and certificate revocation lists for mutual TLS authentication
- **Source**: `terraform-aws-modules/alb/aws//modules/lb_trust_store`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/latest/submodules/lb_trust_store
- **Key Features**: CA certificate bundle management from S3, certificate revocation list (CRL) support, multiple revocation list configurations, S3-based certificate storage
- **Use Cases**: Implementing mutual TLS authentication for B2B APIs, securing service-to-service communication with client certificates, managing certificate revocation for compromised certificates, meeting compliance requirements for certificate-based authentication

## Submodule 1: lb_trust_store

### Description

The `lb_trust_store` submodule creates and manages AWS Application Load Balancer trust stores for implementing mutual TLS (mTLS) authentication. Trust stores contain CA certificate bundles that validate client certificates during the TLS handshake. This submodule also supports configuring certificate revocation lists (CRLs) to invalidate compromised or expired client certificates, providing a complete client-certificate authentication pipeline that plugs into the `mutual_authentication` block of an ALB HTTPS listener.

### Key Features

- CA certificate bundle management from an S3 bucket/key (with optional object version pinning)
- Support for multiple, independently configured certificate revocation lists (CRLs)
- Conditional trust store and revocation resource creation via `create`/`create_trust_store_revocation`
- Comprehensive tagging support for resource management
- ARN and name outputs for direct use in `aws_lb_listener.mutual_authentication.trust_store_arn`

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls if resources should be created |
| `name` | `string` | `null` | Name of the trust store (max 32 characters) |
| `name_prefix` | `string` | `null` | Creates a unique name beginning with the specified prefix (max 6 characters) |
| `ca_certificates_bundle_s3_bucket` | `string` | `null` | S3 bucket name holding the client certificate CA bundle |
| `ca_certificates_bundle_s3_key` | `string` | `null` | S3 object key holding the client certificate CA bundle |
| `ca_certificates_bundle_s3_object_version` | `string` | `null` | Version ID of CA bundle S3 object (defaults to latest) |
| `create_trust_store_revocation` | `bool` | `false` | Whether to create trust store revocation resources |
| `revocation_lists` | `map(object)` | `null` | Map of revocation list configs (`revocations_s3_bucket`, `revocations_s3_key`, optional object version) |
| `tags` | `map(string)` | `{}` | Map of tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `trust_store_id` | ARN of the trust store (matches `trust_store_arn`) |
| `trust_store_arn` | ARN of the trust store |
| `trust_store_arn_suffix` | ARN suffix for use with CloudWatch metrics |
| `trust_store_name` | Name of the trust store |
| `revocation_lists` | Map of revocation lists and their attributes |

### Usage Example

```hcl
# Create S3 bucket for certificates (prerequisite)
resource "aws_s3_bucket" "certificates" {
  bucket = "my-certificates-bucket"

  tags = {
    Name = "TLS Certificates"
  }
}

# Upload CA certificate bundle to S3
resource "aws_s3_object" "ca_bundle" {
  bucket = aws_s3_bucket.certificates.id
  key    = "ca-certificates/root-ca.pem"
  source = "path/to/root-ca.pem"
  etag   = filemd5("path/to/root-ca.pem")
}

# Upload certificate revocation list to S3
resource "aws_s3_object" "crl_1" {
  bucket = aws_s3_bucket.certificates.id
  key    = "crl/revoked-certificates-1.pem"
  source = "path/to/crl-1.pem"
  etag   = filemd5("path/to/crl-1.pem")
}

# Create trust store with revocation lists
module "trust_store" {
  source  = "terraform-aws-modules/alb/aws//modules/lb_trust_store"
  version = "~> 10.0"

  name = "api-client-trust-store"

  ca_certificates_bundle_s3_bucket = aws_s3_bucket.certificates.id
  ca_certificates_bundle_s3_key    = aws_s3_object.ca_bundle.key

  create_trust_store_revocation = true

  revocation_lists = {
    primary_crl = {
      revocations_s3_bucket = aws_s3_bucket.certificates.id
      revocations_s3_key    = aws_s3_object.crl_1.key
    }
  }

  tags = {
    Environment = "production"
    Service     = "api-gateway"
    ManagedBy   = "terraform"
  }
}

# Use trust store in ALB listener for mutual TLS
resource "aws_lb_listener" "mtls_https" {
  load_balancer_arn = module.alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.main.arn

  mutual_authentication {
    mode            = "verify"
    trust_store_arn = module.trust_store.trust_store_arn
  }

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls if resources should be created (see gotcha in "Notes for AI Agents" regarding `putin_khuylo`) |
| `name` | `string` | `null` | Name of the load balancer (max 32 characters) |
| `load_balancer_type` | `string` | `"application"` | Type: `application`, `network`, or `gateway` |
| `internal` | `bool` | `null` | If `true`, creates an internal (private) load balancer; default is internet-facing |
| `vpc_id` | `string` | `null` | VPC ID (required when creating the security group) |
| `subnets` | `list(string)` | `null` | Subnet IDs to attach to the load balancer (use 2+ AZs) |
| `listeners` | `map(any)` | `{}` | Listener configs: `forward`/`redirect`/`fixed_response`/`authenticate_cognito`/`authenticate_oidc`/`jwt_validation`/`weighted_forward` default actions, plus a `rules` sub-map for conditional actions and `transform` (header/URL rewrite) |
| `target_groups` | `map(any)` | `null` | Target group configs: health checks, stickiness, target type, `target_group_health`, `target_health_state` |
| `additional_target_group_attachments` | `map(object)` | `null` | Extra targets attached to a target group created in `target_groups`, keyed by `target_group_key` |
| `create_security_group` | `bool` | `true` | Create a new security group for the load balancer |
| `security_groups` | `list(string)` | `[]` | Existing security group IDs to attach instead of/in addition to the created one |
| `security_group_ingress_rules` | `map(any)` | `null` | Ingress rules for the created security group |
| `security_group_egress_rules` | `map(any)` | `null` | Egress rules for the created security group |
| `access_logs` | `object` | `null` | Access logging config: `{bucket, enabled, prefix}` |
| `connection_logs` | `object` | `null` | Connection logging config (NLB) |
| `health_check_logs` | `object` | `null` | Health check logging config (ALB) |
| `associate_web_acl` | `bool` | `false` | Associate a WAF Web ACL |
| `web_acl_arn` | `string` | `null` | WAF Web ACL ARN to associate |
| `enable_waf_fail_open` | `bool` | `null` | Allow requests through if the load balancer cannot reach WAF. Defaults to `false` |
| `enable_deletion_protection` | `bool` | `true` | Prevent deletion via the API (enabled by default!) |
| `enable_cross_zone_load_balancing` | `bool` | `true` | Distribute traffic across AZs (always `true` for ALB) |
| `drop_invalid_header_fields` | `bool` | `true` | Drop invalid HTTP headers (ALB security default) |
| `preserve_host_header` | `bool` | `null` | Preserve the Host header when forwarding to targets |
| `idle_timeout` | `number` | `null` | Connection idle timeout in seconds (ALB). Default `60` |
| `client_keep_alive` | `number` | `null` | Client keep-alive in seconds, 60-604800. Default `3600` |
| `subnet_mapping` | `list(object)` | `null` | Subnet mapping with EIP/private IPv4 allocation (NLB static IPs) |
| `ip_address_type` | `string` | `null` | `ipv4` or `dualstack` |
| `minimum_load_balancer_capacity` | `object` | `null` | Pre-warm/reserve LCU capacity via `{ capacity_units = number }` |
| `route53_records` | `map(any)` | `null` | Route53 alias records to create (`zone_id`, `name`, `type`, `evaluate_target_health`) |
| `tags` | `map(string)` | `{}` | Tags for all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `id` | The ARN of the load balancer |
| `arn` | The ARN of the load balancer |
| `arn_suffix` | ARN suffix for CloudWatch metrics |
| `dns_name` | DNS name of the load balancer |
| `zone_id` | Hosted zone ID for Route53 alias records |
| `listeners` | Map of listeners and their attributes |
| `listener_rules` | Map of listener rules and their attributes |
| `target_groups` | Map of target groups and their attributes |
| `security_group_arn` | ARN of the created security group |
| `security_group_id` | ID of the created security group |
| `route53_records` | Route53 records created for the load balancer |

## Usage Examples

### Example 1: Complete Application Load Balancer with HTTPS

```hcl
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 10.0"

  name               = "web-app-alb"
  load_balancer_type = "application"
  vpc_id             = "vpc-12345678"
  subnets            = ["subnet-12345678", "subnet-87654321"]

  # Security group configuration
  create_security_group = true
  security_group_ingress_rules = {
    http = {
      from_port   = 80
      to_port     = 80
      ip_protocol = "tcp"
      cidr_ipv4   = "0.0.0.0/0"
      description = "Allow HTTP from anywhere"
    }
    https = {
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      cidr_ipv4   = "0.0.0.0/0"
      description = "Allow HTTPS from anywhere"
    }
  }
  security_group_egress_rules = {
    all = {
      ip_protocol = "-1"
      cidr_ipv4   = "0.0.0.0/0"
      description = "Allow all outbound traffic"
    }
  }

  # Access logging
  access_logs = {
    bucket  = "my-alb-logs-bucket"
    prefix  = "web-app-alb"
    enabled = true
  }

  # HTTP to HTTPS redirect, then HTTPS forward
  listeners = {
    http = {
      port     = 80
      protocol = "HTTP"

      redirect = {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }

    https = {
      port            = 443
      protocol        = "HTTPS"
      ssl_policy      = "ELBSecurityPolicy-TLS13-1-2-2021-06"
      certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/abc123"

      forward = {
        target_group_key = "web_app"
      }
    }
  }

  # Target group configuration
  target_groups = {
    web_app = {
      name_prefix = "web-"
      protocol    = "HTTP"
      port        = 80
      target_type = "instance"

      health_check = {
        enabled             = true
        interval            = 30
        path                = "/health"
        port                = "traffic-port"
        healthy_threshold   = 3
        unhealthy_threshold = 3
        timeout             = 6
        protocol            = "HTTP"
        matcher             = "200-299"
      }

      stickiness = {
        enabled         = true
        type            = "lb_cookie"
        cookie_duration = 86400
      }
    }
  }

  tags = {
    Environment = "production"
    Application = "web-app"
    ManagedBy   = "terraform"
  }
}

# Output the DNS name
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = module.alb.dns_name
}
```

### Example 2: Network Load Balancer for TCP Traffic

```hcl
module "nlb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 10.0"

  name               = "tcp-app-nlb"
  load_balancer_type = "network"
  vpc_id             = "vpc-12345678"
  subnets            = ["subnet-12345678", "subnet-87654321"]

  # TCP listener
  listeners = {
    tcp = {
      port     = 8080
      protocol = "TCP"

      forward = {
        target_group_key = "tcp_app"
      }
    }
  }

  # Target group for TCP traffic
  target_groups = {
    tcp_app = {
      name_prefix = "tcp-"
      protocol    = "TCP"
      port        = 8080
      target_type = "ip"

      health_check = {
        enabled             = true
        interval            = 10
        port                = 8080
        protocol            = "TCP"
        healthy_threshold   = 3
        unhealthy_threshold = 3
      }

      # Connection settings
      deregistration_delay = 30
      preserve_client_ip   = true
      proxy_protocol_v2    = false
    }
  }

  tags = {
    Environment = "production"
    Application = "tcp-app"
  }
}
```

### Example 3: ALB with Path-Based Routing

```hcl
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 10.0"

  name               = "microservices-alb"
  load_balancer_type = "application"
  vpc_id             = "vpc-12345678"
  subnets            = ["subnet-12345678", "subnet-87654321"]

  # HTTPS listener with path-based routing
  listeners = {
    https = {
      port            = 443
      protocol        = "HTTPS"
      ssl_policy      = "ELBSecurityPolicy-TLS13-1-2-2021-06"
      certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/abc123"

      # Default action
      forward = {
        target_group_key = "default_service"
      }

      # Listener rules for path-based routing
      rules = {
        api_service = {
          priority = 10
          actions = [{
            forward = {
              target_group_key = "api_service"
            }
          }]
          conditions = [{
            path_pattern = {
              values = ["/api/*"]
            }
          }]
        }

        admin_service = {
          priority = 20
          actions = [{
            forward = {
              target_group_key = "admin_service"
            }
          }]
          conditions = [{
            path_pattern = {
              values = ["/admin/*"]
            }
          }]
        }

        static_content = {
          priority = 30
          actions = [{
            forward = {
              target_group_key = "static_service"
            }
          }]
          conditions = [{
            path_pattern = {
              values = ["/static/*", "/images/*", "/css/*", "/js/*"]
            }
          }]
        }
      }
    }
  }

  # Multiple target groups for different services
  target_groups = {
    default_service = {
      name_prefix = "def-"
      protocol    = "HTTP"
      port        = 80
      target_type = "instance"

      health_check = {
        path    = "/health"
        matcher = "200"
      }
    }

    api_service = {
      name_prefix = "api-"
      protocol    = "HTTP"
      port        = 8080
      target_type = "ip"

      health_check = {
        path    = "/api/health"
        matcher = "200"
      }
    }

    admin_service = {
      name_prefix = "adm-"
      protocol    = "HTTP"
      port        = 8081
      target_type = "ip"

      health_check = {
        path    = "/admin/health"
        matcher = "200"
      }
    }

    static_service = {
      name_prefix = "sta-"
      protocol    = "HTTP"
      port        = 8082
      target_type = "instance"

      health_check = {
        path    = "/health"
        matcher = "200"
      }
    }
  }

  tags = {
    Environment = "production"
    Application = "microservices"
  }
}
```

### Example 4: ALB with Cognito Authentication

```hcl
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 10.0"

  name               = "authenticated-app-alb"
  load_balancer_type = "application"
  vpc_id             = "vpc-12345678"
  subnets            = ["subnet-12345678", "subnet-87654321"]

  listeners = {
    https = {
      port            = 443
      protocol        = "HTTPS"
      ssl_policy      = "ELBSecurityPolicy-TLS13-1-2-2021-06"
      certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/abc123"

      # Cognito authentication before forwarding (each action is a distinct
      # object key, e.g. `authenticate_cognito` / `forward` -- no `type` field)
      rules = {
        authenticate = {
          priority = 1
          actions = [
            {
              authenticate_cognito = {
                user_pool_arn       = "arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_ABC123"
                user_pool_client_id = "client-id-123"
                user_pool_domain    = "my-app-domain"
              }
            },
            {
              forward = {
                target_group_key = "authenticated_app"
              }
            }
          ]
          conditions = [{
            path_pattern = {
              values = ["/*"]
            }
          }]
        }
      }
    }
  }

  target_groups = {
    authenticated_app = {
      name_prefix = "auth-"
      protocol    = "HTTP"
      port        = 80
      target_type = "instance"

      health_check = {
        path    = "/health"
        matcher = "200"
      }
    }
  }

  tags = {
    Environment = "production"
    Security    = "cognito-auth"
  }
}
```

### Example 5: Canary Deployment with Weighted Target Groups

```hcl
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 10.0"

  name               = "canary-alb"
  load_balancer_type = "application"
  vpc_id             = "vpc-12345678"
  subnets            = ["subnet-12345678", "subnet-87654321"]

  listeners = {
    https = {
      port            = 443
      protocol        = "HTTPS"
      certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/abc123"

      # Send 90% of traffic to stable, 10% to canary; sticky sessions
      # keep a given client on the same target group for the session.
      weighted_forward = {
        target_groups = [
          {
            target_group_key = "app_stable"
            weight           = 90
          },
          {
            target_group_key = "app_canary"
            weight           = 10
          }
        ]
        stickiness = {
          enabled  = true
          duration = 3600
        }
      }
    }
  }

  target_groups = {
    app_stable = {
      name_prefix = "stb-"
      protocol    = "HTTP"
      port        = 80
      target_type = "instance"

      health_check = {
        path    = "/health"
        matcher = "200"
      }
    }

    app_canary = {
      name_prefix = "cnr-"
      protocol    = "HTTP"
      port        = 80
      target_type = "instance"

      health_check = {
        path    = "/health"
        matcher = "200"
      }
    }
  }

  tags = {
    Environment = "production"
    Strategy    = "canary"
  }
}
```

## Best Practices

### Architecture and Design

1. **Load Balancer Type Selection**: ALB for HTTP/HTTPS Layer 7 routing; NLB for TCP/UDP with static IPs or ultra-high performance; Gateway LB (`load_balancer_type = "gateway"`) for third-party network appliances using GENEVE (the module automatically omits port/protocol for GENEVE listeners)
2. **Multi-AZ Deployment**: Always use at least 2 subnets in different Availability Zones for high availability
3. **Subnet Placement**: Public subnets for internet-facing load balancers; private subnets for internal ones
4. **Listener/Rule Actions**: Each action is expressed as its own object key (`forward`, `redirect`, `fixed_response`, `authenticate_cognito`, `authenticate_oidc`, `jwt_validation`, `weighted_forward`) -- there is no `type` attribute in v10.x
5. **Rule Priority**: Lower numbers = higher priority; put the most specific rules first

### Security

1. **TLS Policies**: Defaults to `ELBSecurityPolicy-TLS13-1-3-2021-06`; set `ssl_policy` explicitly (e.g. `ELBSecurityPolicy-TLS13-1-2-2021-06`) if broader client compatibility is required
2. **Deletion Protection**: Enabled by default -- explicitly set `enable_deletion_protection = false` only for dev/test environments
3. **HTTP to HTTPS**: Always redirect HTTP to HTTPS using a `redirect` default action rather than forwarding plaintext traffic
4. **WAF Integration**: Associate a WAF ACL for internet-facing ALBs via `associate_web_acl = true` and `web_acl_arn`; consider `enable_waf_fail_open` carefully (defaults closed/blocking)
5. **Security Groups**: Define explicit ingress/egress rules; avoid `0.0.0.0/0` when possible
6. **mTLS**: Use the `lb_trust_store` submodule plus `mutual_authentication` on the listener for client certificate authentication on B2B/service APIs
7. **JWT/OIDC/Cognito**: Prefer `jwt_validation` or `authenticate_oidc`/`authenticate_cognito` at the load balancer to centralize authN/authZ ahead of application code

### Target Groups and Health Checks

1. **Target Types**: `instance` for EC2, `ip` for containers/ECS, `lambda` for serverless
2. **Health Check Path**: Use a dedicated endpoint that validates application dependencies
3. **Recommended Thresholds**: 3 healthy, 2-3 unhealthy checks; 10-30s interval; timeout less than interval
4. **Deregistration Delay**: 30-300s depending on request duration, to allow in-flight requests to complete
5. **Load Balancing Algorithms**: `round_robin` (default), `least_outstanding_requests`, or `weighted_random` for anomaly mitigation
6. **Canary/Weighted Routing**: Use `weighted_forward` (not `forward`) with a `target_groups` list of `{target_group_key, weight}` and optional `stickiness`, either as a listener default action or inside a rule's `actions`
7. **gRPC Services**: Set `protocol_version = "GRPC"` on the target group for gRPC-based backends
8. **AZ/DNS Failover**: Use `target_group_health.dns_failover` and `target_group_health.unhealthy_state_routing` to control DNS and routing behavior when targets in an AZ are unhealthy

### Logging and Monitoring

1. **Access Logs**: Enable for production; requires an S3 bucket with ELB write permissions
2. **Connection Logs**: Available for NLB; useful for debugging TLS handshake issues
3. **Health Check Logs**: Available for ALB (since v10.4); useful for diagnosing flapping health checks
4. **CloudWatch Alarms**: Monitor `UnHealthyHostCount`, `HTTPCode_ELB_5XX`, and `TargetResponseTime`

### Capacity and Performance

1. **Capacity Reservation**: Use `minimum_load_balancer_capacity` to pre-warm LCU capacity ahead of predictable traffic spikes (e.g. product launches) instead of relying solely on reactive auto-scaling
2. **Zonal Shift**: Enable `enable_zonal_shift` to allow fast failover away from an impaired AZ via Route 53 Application Recovery Controller

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-alb
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-alb/tree/master/examples
- **Usage Patterns**: https://github.com/terraform-aws-modules/terraform-aws-alb/blob/master/docs/patterns.md
- **AWS ALB Documentation**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/
- **AWS NLB Documentation**: https://docs.aws.amazon.com/elasticloadbalancing/latest/network/
- **AWS Gateway Load Balancer Documentation**: https://docs.aws.amazon.com/elasticloadbalancing/latest/gateway/
- **Mutual TLS Authentication**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/mutual-authentication.html
- **JWT Verification on ALB**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html

## Notes for AI Agents

**Critical defaults to be aware of:**
- `enable_deletion_protection = true` -- must explicitly disable for dev/test environments
- `drop_invalid_header_fields = true` -- security default, usually keep enabled
- `enable_cross_zone_load_balancing = true` -- usually desired for even distribution
- `ssl_policy` defaults to `ELBSecurityPolicy-TLS13-1-3-2021-06` on HTTPS/TLS listeners when not set
- **Gotcha**: `create = var.create && var.putin_khuylo`. The `putin_khuylo` variable defaults to `true` and is combined with `create` to gate resource creation. Do not set it to `false` -- it disables the entire module regardless of `create`.

**Syntax gotcha (v10.x)**: Listener/rule `actions` are lists of objects where each action is its own top-level key (`forward = {...}`, `redirect = {...}`, `authenticate_cognito = {...}`, `jwt_validation = {...}`, `weighted_forward = {...}`, `fixed_response = {...}`). There is **no** `type = "forward"` attribute -- that syntax was removed in the v9 -> v10 upgrade and will fail type validation.

**Common patterns:**

1. **Simple ALB with HTTPS**: `listeners` with an HTTP `redirect` to HTTPS and an HTTPS `forward` to a target group
2. **Path/host-based routing**: Define `rules` within a listener using `path_pattern` or `host_header` conditions
3. **NLB with static IPs**: Use `subnet_mapping` with `allocation_id` for Elastic IPs
4. **Weighted/canary routing**: Use `weighted_forward` (with `target_groups` weights and optional `stickiness`) as a listener default action or inside `rules.actions` -- do not use `forward` for this
5. **Header/URL rewriting**: Use `transform` inside a listener rule with `host_header_rewrite_config` or `url_rewrite_config`
6. **Gateway Load Balancer**: Set `load_balancer_type = "gateway"`; listener `protocol = "GENEVE"` and no `port` are required

**Required parameters by use case:**
- All: `name`, `vpc_id`, `subnets`, `listeners`, `target_groups`
- Internet-facing: `internal = false` (or omit), public subnets
- Internal: `internal = true`, private subnets
- HTTPS: `certificate_arn` in listener, port 443, protocol `HTTPS`
- WAF: `associate_web_acl = true`, `web_acl_arn`
- mTLS: use the `lb_trust_store` submodule, then set `mutual_authentication` on the listener

**Output usage:**
- `dns_name` -- for Route53 alias records or direct access
- `zone_id` -- required for Route53 alias record configuration
- `target_groups["key"].arn` -- for ASG attachment or ECS service registration
- `security_group_id` -- for target security group ingress rules
