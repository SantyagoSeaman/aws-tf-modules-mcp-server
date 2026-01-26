# Terraform AWS ALB Module

## Module Information

- **Module Name**: `alb`
- **Source**: `terraform-aws-modules/alb/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-alb
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/latest
- **Latest Version**: 10.5.0
- **Purpose**: Creates Application Load Balancers (ALB), Network Load Balancers (NLB), and Gateway Load Balancers with listeners, target groups, security groups, and Route53 integration
- **Service**: AWS ELB (Elastic Load Balancing)
- **Category**: Networking, Compute, Security
- **Keywords**: alb, nlb, load-balancer, target-group, listener, routing, https, tls, health-check, security-group, waf, cognito, oidc, authentication, path-routing, host-routing, mutual-tls, access-logs
- **Use For**: distributing traffic across multiple targets, high availability for web applications, SSL/TLS termination, path-based and host-based routing, user authentication with Cognito/OIDC, load balancing containers and microservices, auto-scaling integration, WAF protection, blue-green and canary deployments, mutual TLS authentication

## Description

This module creates and manages AWS Application Load Balancers (ALB), Network Load Balancers (NLB), and Gateway Load Balancers with comprehensive configuration options. ALBs operate at Layer 7 providing advanced HTTP/HTTPS routing based on paths, hostnames, headers, and query parameters. NLBs operate at Layer 4 for ultra-high performance TCP/UDP/TLS traffic with static IP support. Gateway Load Balancers enable deployment of third-party virtual appliances for traffic inspection.

The module manages all load balancer components: listeners with routing rules, target groups with health checks, security groups, and access logging. It supports weighted routing for canary deployments, authentication via Cognito/OIDC, WAF integration, and Route53 DNS record creation. Advanced features include mutual TLS (mTLS) authentication with trust stores and certificate revocation lists, header manipulation (add/remove request/response headers), and URL rewriting.

Key defaults prioritize security: deletion protection is enabled, invalid HTTP headers are dropped, and cross-zone load balancing is enabled. The module outputs DNS names, ARNs, listener configurations, target group details, and security group IDs for integration with other infrastructure.

## Key Features

- **Multi-Type Load Balancer Support**: Application (ALB), Network (NLB), and Gateway Load Balancers in a single module
- **Advanced Routing Rules**: Path patterns, hostnames, headers, query strings, HTTP methods, and source IP conditions
- **Authentication Integration**: Amazon Cognito, OIDC providers, and JWT validation at the load balancer level
- **Mutual TLS (mTLS)**: Client certificate authentication with trust stores and certificate revocation lists via submodule
- **Header Manipulation**: Add/remove request and response headers, URL rewriting, and host header preservation
- **Security Group Management**: Automated creation with customizable ingress/egress rules or attach existing groups
- **AWS WAF Integration**: Associate Web Application Firewall ACLs with `associate_web_acl` parameter
- **Comprehensive Logging**: Access logs, connection logs, and health check logs to S3
- **Route53 Integration**: Automatic creation of A and AAAA DNS records
- **Target Types**: Instance, IP, Lambda, and ALB targets with configurable health checks
- **Load Balancing Algorithms**: Round robin, least outstanding requests, and weighted random for canary deployments
- **SSL/TLS Termination**: ACM certificate integration with modern TLS 1.3 policies
- **Static IPs (NLB)**: Subnet mapping with Elastic IP allocation for predictable IP addresses
- **Zonal Shift Support**: Route 53 Application Recovery Controller integration for AZ failover

## Main Use Cases

1. **Web Application Load Balancing**: Distribute HTTP/HTTPS traffic across multiple web servers for high availability and scalability
2. **Microservices Traffic Routing**: Route requests to different microservices based on URL paths, hostnames, or headers
3. **SSL/TLS Offloading**: Terminate SSL/TLS connections at the load balancer to reduce compute overhead on backend servers
4. **User Authentication**: Implement centralized authentication using Cognito or OIDC before routing to backend applications
5. **High-Performance TCP/UDP Applications**: Use Network Load Balancer for gaming servers, IoT applications, or real-time streaming
6. **Blue-Green Deployments**: Route traffic between multiple target groups with weighted routing for zero-downtime deployments
7. **API Gateway Load Balancing**: Distribute API traffic across multiple backend services with path-based routing
8. **Container Orchestration**: Load balance containerized applications running on ECS, EKS, or EC2 instances
9. **Multi-Tenant Applications**: Route traffic to different application instances based on hostname or URL patterns
10. **Security and Compliance**: Integrate with WAF for threat protection and enable access logging for audit trails

## Submodules

### 1. lb_trust_store

- **Purpose**: Create and manage trust stores and certificate revocation lists for mutual TLS authentication
- **Source**: `terraform-aws-modules/alb/aws//modules/lb_trust_store`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/latest/submodules/lb_trust_store
- **Key Features**: CA certificate bundle management from S3, certificate revocation list (CRL) support, multiple revocation list configurations, S3-based certificate storage
- **Use Cases**: Implementing mutual TLS authentication for B2B APIs, securing service-to-service communication with client certificates, managing certificate revocation for compromised certificates, meeting compliance requirements for certificate-based authentication

## Submodule 1: lb_trust_store

### Description

The `lb_trust_store` submodule creates and manages AWS Application Load Balancer trust stores for implementing mutual TLS (mTLS) authentication. Trust stores contain CA certificate bundles that validate client certificates during the TLS handshake process. This submodule also supports configuring certificate revocation lists (CRLs) to invalidate compromised or expired client certificates, providing comprehensive client certificate authentication infrastructure.

### Key Features

- CA certificate bundle management from S3 buckets
- Support for multiple certificate revocation lists (CRLs)
- S3 object versioning support for certificate updates
- Conditional trust store and revocation resource creation
- Comprehensive tagging support for resource management
- ARN and name outputs for integration with load balancer listeners

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls if resources should be created |
| `name` | `string` | `null` | Name of the trust store (max 32 characters) |
| `name_prefix` | `string` | `null` | Creates a unique name beginning with the specified prefix |
| `ca_certificates_bundle_s3_bucket` | `string` | `null` | S3 bucket name holding the client certificate CA bundle |
| `ca_certificates_bundle_s3_key` | `string` | `null` | S3 object key holding the client certificate CA bundle |
| `ca_certificates_bundle_s3_object_version` | `string` | `null` | Version ID of CA bundle S3 object (if versioned) |
| `create_trust_store_revocation` | `bool` | `false` | Whether to create trust store revocation resources |
| `revocation_lists` | `map(object)` | `null` | Map of revocation list configurations with S3 bucket/key |
| `tags` | `map(string)` | `{}` | Map of tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `trust_store_id` | ARN of the trust store |
| `trust_store_arn` | ARN of the trust store (matches id) |
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

# Upload certificate revocation lists to S3
resource "aws_s3_object" "crl_1" {
  bucket = aws_s3_bucket.certificates.id
  key    = "crl/revoked-certificates-1.pem"
  source = "path/to/crl-1.pem"
  etag   = filemd5("path/to/crl-1.pem")
}

# Create trust store with revocation lists
module "trust_store" {
  source = "terraform-aws-modules/alb/aws//modules/lb_trust_store"
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
| `create` | `bool` | `true` | Controls if resources should be created |
| `name` | `string` | `null` | Name of the load balancer (max 32 characters) |
| `load_balancer_type` | `string` | `"application"` | Type: `application`, `network`, or `gateway` |
| `internal` | `bool` | `null` | If true, creates internal (private) load balancer |
| `vpc_id` | `string` | `null` | VPC ID (required when creating security group) |
| `subnets` | `list(string)` | `null` | Subnet IDs to attach to the load balancer |
| `listeners` | `map(any)` | `{}` | Listener configurations with rules |
| `target_groups` | `map(any)` | `null` | Target group configurations |
| `create_security_group` | `bool` | `true` | Create a new security group for the LB |
| `security_groups` | `list(string)` | `[]` | Existing security group IDs to attach |
| `security_group_ingress_rules` | `map(any)` | `null` | Ingress rules for created security group |
| `security_group_egress_rules` | `map(any)` | `null` | Egress rules for created security group |
| `access_logs` | `object` | `null` | Access logging config: `{bucket, enabled, prefix}` |
| `connection_logs` | `object` | `null` | Connection logging config (NLB only) |
| `associate_web_acl` | `bool` | `false` | Associate WAF Web ACL |
| `web_acl_arn` | `string` | `null` | WAF Web ACL ARN to associate |
| `enable_deletion_protection` | `bool` | `true` | Prevent deletion via API (default enabled!) |
| `enable_cross_zone_load_balancing` | `bool` | `true` | Distribute traffic across AZs |
| `drop_invalid_header_fields` | `bool` | `true` | Drop invalid HTTP headers (security default) |
| `preserve_host_header` | `bool` | `null` | Preserve Host header to targets |
| `idle_timeout` | `number` | `null` | Connection idle timeout in seconds (ALB) |
| `subnet_mapping` | `list(object)` | `null` | Subnet mapping with EIP allocation (NLB static IPs) |
| `route53_records` | `map(any)` | `null` | Route53 DNS records to create |
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

  # HTTP to HTTPS redirect listener
  listeners = {
    http = {
      port     = 80
      protocol = "HTTP"

      forward = {
        target_group_key = "web_app"
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
      name_prefix      = "web-"
      protocol         = "HTTP"
      port             = 80
      target_type      = "instance"

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

  # Enable cross-zone load balancing
  enable_cross_zone_load_balancing = true

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
      deregistration_delay          = 30
      preserve_client_ip            = true
      proxy_protocol_v2             = false
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
            type             = "forward"
            target_group_key = "api_service"
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
            type             = "forward"
            target_group_key = "admin_service"
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
            type             = "forward"
            target_group_key = "static_service"
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

      # Cognito authentication before forwarding
      rules = {
        authenticate = {
          priority = 1
          actions = [
            {
              type = "authenticate-cognito"
              authenticate_cognito = {
                user_pool_arn       = "arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_ABC123"
                user_pool_client_id = "client-id-123"
                user_pool_domain    = "my-app-domain"
              }
            },
            {
              type             = "forward"
              target_group_key = "authenticated_app"
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

## Best Practices

### Architecture and Design

1. **Load Balancer Type Selection**: ALB for HTTP/HTTPS Layer 7 routing; NLB for TCP/UDP with static IPs or ultra-high performance; Gateway LB for network appliances
2. **Multi-AZ Deployment**: Always use at least 2 subnets in different AZs for high availability
3. **Subnet Placement**: Public subnets for internet-facing; private subnets for internal load balancers
4. **Listener Rules**: Every rule's actions must end with `forward`, `redirect`, or `fixed-response` action
5. **Rule Priority**: Lower numbers = higher priority; put most specific rules first

### Security

1. **TLS Policies**: Use `ELBSecurityPolicy-TLS13-1-2-2021-06` or newer for modern TLS 1.3 support
2. **Deletion Protection**: Enabled by default - explicitly disable only for dev/test environments
3. **HTTP to HTTPS**: Always redirect HTTP to HTTPS using listener redirect action
4. **WAF Integration**: Associate WAF ACL for internet-facing ALBs via `associate_web_acl = true`
5. **Security Groups**: Define explicit ingress/egress rules; avoid 0.0.0.0/0 when possible
6. **mTLS**: Use `lb_trust_store` submodule for client certificate authentication on B2B APIs

### Target Groups and Health Checks

1. **Target Types**: `instance` for EC2, `ip` for containers/ECS, `lambda` for serverless
2. **Health Check Path**: Use dedicated endpoint that validates application dependencies
3. **Recommended Thresholds**: 3 healthy, 2-3 unhealthy checks; 10-30s interval; timeout < interval
4. **Deregistration Delay**: 30-300s depending on request duration; allows in-flight requests to complete
5. **Load Balancing Algorithms**: `round_robin` (default), `least_outstanding_requests`, `weighted_random` (canary)

### Logging and Monitoring

1. **Access Logs**: Enable for production; requires S3 bucket with ELB write permissions
2. **Connection Logs**: Available for NLB; useful for debugging TLS issues
3. **CloudWatch Alarms**: Monitor `UnHealthyHostCount`, `HTTPCode_ELB_5XX`, `TargetResponseTime`

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-alb
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-alb/tree/master/examples
- **AWS ALB Documentation**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/
- **AWS NLB Documentation**: https://docs.aws.amazon.com/elasticloadbalancing/latest/network/
- **Mutual TLS Authentication**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/mutual-authentication.html

## Notes for AI Agents

**Critical defaults to be aware of:**
- `enable_deletion_protection = true` - Must explicitly disable for dev/test environments
- `drop_invalid_header_fields = true` - Security default, usually keep enabled
- `enable_cross_zone_load_balancing = true` - Usually desired for even distribution

**Common patterns:**

1. **Simple ALB with HTTPS**: Use `listeners` with HTTP→HTTPS redirect and HTTPS forward to target group
2. **Path-based routing**: Define `rules` within listener with `path_pattern` conditions
3. **Host-based routing**: Use `host_header` conditions in listener rules
4. **NLB with static IPs**: Use `subnet_mapping` with `allocation_id` for Elastic IPs
5. **Weighted routing (canary)**: Use `forward.stickiness` and `forward.target_groups` with weights

**Required parameters by use case:**
- All: `name`, `vpc_id`, `subnets`, `listeners`, `target_groups`
- Internet-facing: `internal = false` (or omit), public subnets
- Internal: `internal = true`, private subnets
- HTTPS: `certificate_arn` in listener, port 443, protocol "HTTPS"
- WAF: `associate_web_acl = true`, `web_acl_arn`
- mTLS: Use `lb_trust_store` submodule, set `mutual_authentication` in listener

**Output usage:**
- `dns_name` - For Route53 alias records or direct access
- `zone_id` - Required for Route53 alias record configuration
- `target_groups["key"].arn` - For ASG attachment or ECS service
- `security_group_id` - For target security group ingress rules
