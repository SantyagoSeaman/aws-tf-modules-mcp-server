# Terraform AWS ALB Module

## Module Information

- **Module Name**: `alb`
- **Source**: `terraform-aws-modules/alb/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-alb
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/latest
- **Latest Version**: 10.0.0
- **Purpose**: Terraform module for creating and managing AWS Application Load Balancers (ALB) and Network Load Balancers (NLB) with comprehensive configuration options
- **Service**: AWS ELB (Elastic Load Balancing)
- **Category**: Networking, Compute, Security
- **Keywords**: alb, application-load-balancer, nlb, network-load-balancer, elastic-load-balancing, load-balancer, layer-7, layer-4, target-group, listener, listener-rules, routing, http, https, tcp, udp, tls, ssl-termination, traffic-distribution, high-availability, auto-scaling, health-check, security-group, waf, web-application-firewall, cognito, oidc, authentication, access-logs, cloudwatch, route53, dns, http-redirect, https-redirect, path-based-routing, host-based-routing, sticky-sessions, cross-zone, vpc, subnet, internet-facing, internal, mutual-tls, mtls, trust-store, certificate-revocation
- **Use For**: distributing incoming traffic across multiple targets, implementing high availability for web applications, enabling SSL/TLS termination for secure connections, routing traffic based on URL paths and hostnames, implementing user authentication with Cognito or OIDC, load balancing containerized applications and microservices, supporting auto-scaling groups with health checks, protecting applications with AWS WAF integration, handling millions of requests with low latency, implementing blue-green or canary deployments, securing internal services with private load balancers, enabling mutual TLS authentication for enhanced security

## Description

This Terraform module provides a comprehensive solution for creating and managing AWS Application Load Balancers (ALB) and Network Load Balancers (NLB) with extensive configuration flexibility. Application Load Balancers operate at Layer 7 (application layer) and provide advanced HTTP/HTTPS traffic routing capabilities based on URL paths, hostnames, headers, query parameters, and source IP addresses. Network Load Balancers operate at Layer 4 (transport layer) and are designed for ultra-high performance, handling millions of requests per second with ultra-low latency while supporting TCP, UDP, and TLS protocols.

The module handles all aspects of load balancer configuration including listeners, target groups, listener rules, security groups, and access logging. It supports complex routing scenarios with multiple target groups, weighted target group routing, and sophisticated listener rules. The module integrates seamlessly with other AWS services including Route53 for DNS management, AWS WAF for application security, CloudWatch for monitoring and logging, and AWS Certificate Manager for SSL/TLS certificate management. Authentication capabilities include support for Amazon Cognito user pools and OIDC-compliant identity providers, enabling secure access control at the load balancer level.

Built with operational excellence in mind, the module provides conditional resource creation, comprehensive tagging support, and flexible security group management. It includes a specialized submodule for managing trust stores and certificate revocation lists for mutual TLS authentication scenarios. The module supports both internet-facing and internal load balancers, cross-zone load balancing, connection draining, sticky sessions, and detailed access logging. It outputs all essential information including load balancer DNS names, ARNs, listener configurations, target group details, and security group IDs for integration with other infrastructure components.

## Key Features

- **Application Load Balancer (ALB)**: Layer 7 load balancer with advanced HTTP/HTTPS routing and application-level traffic management
- **Network Load Balancer (NLB)**: Layer 4 load balancer for ultra-high performance TCP/UDP/TLS traffic handling with static IP support
- **Flexible Listener Configuration**: Define multiple listeners for different protocols (HTTP, HTTPS, TCP, UDP, TLS) with customizable ports
- **Target Group Management**: Create and configure multiple target groups with health check settings and routing algorithms
- **Advanced Routing Rules**: Implement sophisticated listener rules based on path patterns, hostnames, headers, query strings, and source IPs
- **HTTP to HTTPS Redirect**: Automatic redirection from HTTP to HTTPS for enforcing secure connections
- **Authentication Integration**: Built-in support for Amazon Cognito and OIDC authentication at the load balancer level
- **Security Group Management**: Automated security group creation and configuration with customizable ingress and egress rules
- **AWS WAF Integration**: Associate Web Application Firewall (WAF) ACLs for advanced threat protection and filtering
- **SSL/TLS Termination**: Terminate SSL/TLS connections at the load balancer with ACM certificate integration
- **Mutual TLS (mTLS) Support**: Implement client certificate authentication using trust stores and certificate revocation lists
- **Access Logging**: Enable detailed access logs to S3 for security auditing, compliance, and traffic analysis
- **Route53 Integration**: Automatic creation of Route53 DNS records pointing to the load balancer
- **Health Check Configuration**: Comprehensive health check settings for monitoring target availability and responsiveness
- **Sticky Sessions**: Support for session affinity using application-controlled or load balancer-generated cookies
- **Cross-Zone Load Balancing**: Distribute traffic evenly across targets in multiple Availability Zones
- **Connection Draining**: Graceful handling of in-flight requests during target deregistration
- **Internal and Internet-Facing**: Support for both public-facing and private internal load balancers
- **Conditional Resource Creation**: Control resource creation through feature flags for modular deployments
- **Comprehensive Tagging**: Apply consistent tags across all resources for cost allocation and resource management
- **CloudWatch Metrics**: Automatic integration with CloudWatch for monitoring performance and health metrics
- **Weighted Target Groups**: Distribute traffic across target groups with configurable weights for canary deployments
- **IP Address Targeting**: Register targets by IP address for flexibility in multi-environment architectures
- **Lambda Function Targets**: Route traffic to AWS Lambda functions for serverless application architectures

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
  version = "~> 9.0"

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
| `name` | `string` | `null` | Name of the load balancer |
| `load_balancer_type` | `string` | `"application"` | Type of load balancer (application or network) |
| `internal` | `bool` | `null` | If true, the load balancer will be internal |
| `vpc_id` | `string` | `null` | VPC ID where the load balancer will be created |
| `subnets` | `list(string)` | `null` | List of subnet IDs to attach to the load balancer |
| `listeners` | `any` | `{}` | Map of listener configurations to create |
| `target_groups` | `any` | `{}` | Map of target group configurations to create |
| `security_group_ingress_rules` | `any` | `{}` | Security group ingress rules to add to the security group |
| `security_group_egress_rules` | `any` | `{}` | Security group egress rules to add to the security group |
| `create_security_group` | `bool` | `true` | Determines whether to create a security group |
| `access_logs` | `map(string)` | `{}` | Map containing access logs configuration |
| `associate_web_acl` | `bool` | `false` | Indicates whether a Web ACL should be associated |
| `enable_deletion_protection` | `bool` | `null` | If true, deletion protection will be enabled |
| `enable_cross_zone_load_balancing` | `bool` | `null` | If true, cross-zone load balancing is enabled |
| `tags` | `map(string)` | `{}` | Map of tags to assign to resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `id` | The ID and ARN of the load balancer |
| `arn` | The ID and ARN of the load balancer |
| `arn_suffix` | ARN suffix for use with CloudWatch metrics |
| `dns_name` | The DNS name of the load balancer |
| `zone_id` | The zone ID of the load balancer for Route53 records |
| `listeners` | Map of listeners created and their attributes |
| `listener_rules` | Map of listener rules created and their attributes |
| `target_groups` | Map of target groups created and their attributes |
| `security_group_arn` | Amazon Resource Name (ARN) of the security group |
| `security_group_id` | ID of the security group |
| `route53_records` | Route53 records created and attached to the load balancer |

## Usage Examples

### Example 1: Complete Application Load Balancer with HTTPS

```hcl
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 9.0"

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
  version = "~> 9.0"

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
  version = "~> 9.0"

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
  version = "~> 9.0"

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

### Load Balancer Design and Architecture

1. **Choose the Right Load Balancer Type**: Use ALB for HTTP/HTTPS with advanced routing needs; use NLB for ultra-high performance TCP/UDP traffic or when static IPs are required
2. **Multi-AZ Deployment**: Always deploy load balancers across at least two Availability Zones for high availability and fault tolerance
3. **Subnet Selection**: Use public subnets for internet-facing load balancers and private subnets for internal load balancers
4. **Target Group Strategy**: Create separate target groups for different application tiers, environments, or microservices
5. **Health Check Configuration**: Configure health checks with appropriate intervals, thresholds, and timeout values based on application characteristics
6. **Connection Draining**: Enable connection draining (deregistration delay) to complete in-flight requests during deployment or scaling
7. **Cross-Zone Load Balancing**: Enable cross-zone load balancing to distribute traffic evenly across all registered targets in all enabled AZs
8. **Idle Timeout Configuration**: Adjust idle timeout settings based on application requirements (default 60 seconds for ALB)

### Security Configuration

1. **Security Group Design**: Create dedicated security groups for load balancers with minimal required ingress/egress rules
2. **SSL/TLS Policies**: Use modern TLS policies (TLS 1.2 or 1.3 only) such as `ELBSecurityPolicy-TLS13-1-2-2021-06` for enhanced security
3. **Certificate Management**: Use AWS Certificate Manager (ACM) for SSL/TLS certificates with automatic renewal
4. **HTTP to HTTPS Redirect**: Implement automatic HTTP to HTTPS redirection to enforce encrypted connections
5. **WAF Integration**: Associate AWS WAF with ALBs to protect against common web exploits and attacks
6. **Deletion Protection**: Enable deletion protection for production load balancers to prevent accidental deletion
7. **Private Load Balancers**: Use internal load balancers for backend services that should not be directly accessible from the internet
8. **Authentication at Load Balancer**: Leverage Cognito or OIDC authentication at the load balancer level to offload authentication from applications
9. **Mutual TLS (mTLS)**: Implement client certificate authentication using trust stores for B2B APIs or high-security applications
10. **Security Group Source Restrictions**: Limit ingress rules to known CIDR ranges or security groups rather than allowing 0.0.0.0/0 when possible

### Listener and Routing Configuration

1. **Default Actions**: Always configure a default action for listeners to handle requests that don't match any rules
2. **Rule Priority Management**: Assign rule priorities strategically, with most specific rules having lower priority numbers
3. **Path-Based Routing**: Use path-based routing to route different URL paths to different target groups or microservices
4. **Host-Based Routing**: Implement host-based routing to serve multiple domains from a single load balancer
5. **Header-Based Routing**: Leverage header-based routing for A/B testing, canary deployments, or API versioning
6. **Fixed Response Actions**: Configure fixed response actions for maintenance pages or simple redirects without backend targets
7. **Redirect Actions**: Use redirect actions for URL normalization, domain consolidation, or HTTP to HTTPS enforcement
8. **Weighted Target Groups**: Implement weighted target group routing for gradual traffic shifting during blue-green or canary deployments

### Target Group and Health Check Best Practices

1. **Health Check Path Selection**: Use dedicated health check endpoints that verify all critical application dependencies
2. **Health Check Thresholds**: Balance healthy and unhealthy thresholds to avoid flapping (recommended: 3 healthy, 2-3 unhealthy)
3. **Health Check Intervals**: Set intervals based on application startup time and desired recovery speed (10-30 seconds typical)
4. **Health Check Timeouts**: Configure timeouts shorter than intervals but long enough for realistic response times
5. **HTTP Status Code Matching**: Use specific HTTP status codes (200) or ranges (200-299) for health check success criteria
6. **Deregistration Delay**: Set deregistration delay to allow in-flight requests to complete (30-300 seconds depending on application)
7. **Sticky Sessions**: Enable sticky sessions only when necessary; use application-controlled cookies for better control
8. **Target Type Selection**: Choose appropriate target type (instance, IP, Lambda) based on your architecture and flexibility needs
9. **Slow Start Mode**: Enable slow start mode for targets that require warm-up time before handling full request load
10. **Target Group Attributes**: Configure appropriate attributes like connection termination, preserve client IP, and proxy protocol

### Monitoring and Logging

1. **Access Logging**: Enable access logs to S3 for security analysis, compliance, and troubleshooting (note: S3 storage costs apply)
2. **CloudWatch Metrics**: Monitor key metrics including request count, target response time, healthy host count, and HTTP status codes
3. **CloudWatch Alarms**: Create alarms for unhealthy target count, high response times, and elevated 4xx/5xx error rates
4. **Target Group Metrics**: Monitor target-level metrics to identify performance issues with specific backend instances
5. **Connection Metrics**: Track active connection counts, connection errors, and rejected connections for capacity planning
6. **Request Tracing**: Enable request tracing headers (X-Amzn-Trace-Id) for distributed tracing in microservices architectures
7. **Log Analysis**: Regularly analyze access logs for security threats, performance issues, and usage patterns
8. **Metric Filters**: Create CloudWatch log metric filters for custom metrics based on access log patterns

### Performance Optimization

1. **Connection Multiplexing**: ALBs automatically use HTTP/2 and connection multiplexing to reduce latency and improve throughput
2. **Keep-Alive Connections**: Enable keep-alive on backend targets to reuse connections and reduce connection overhead
3. **Compression**: Enable compression on backend applications to reduce data transfer and improve response times
4. **Response Caching**: Implement caching at the application or CloudFront layer in front of ALB for static content
5. **Request Routing**: Use efficient routing rules to minimize evaluation time and reduce latency
6. **Target Capacity**: Ensure adequate target capacity to handle traffic spikes and maintain low response times
7. **Geographic Distribution**: Use multiple load balancers in different regions with Route53 latency-based routing for global applications
8. **WebSocket Support**: Leverage ALB's native WebSocket support for real-time applications without additional infrastructure

### Cost Optimization

1. **Right-Sizing**: Choose appropriate load balancer type and size based on actual traffic requirements
2. **Cross-Zone Load Balancing Costs**: Understand data transfer costs for cross-zone load balancing (free for ALB, charged for NLB)
3. **Access Logging Costs**: Consider S3 storage costs when enabling access logging; implement lifecycle policies to manage log retention
4. **Idle Load Balancers**: Identify and remove idle or underutilized load balancers to reduce costs
5. **LCU Optimization**: Monitor Load Balancer Capacity Units (LCUs) and optimize to avoid unnecessary charges
6. **Target Group Consolidation**: Consolidate target groups where possible to reduce complexity and potential costs
7. **NLB Static IPs**: Use NLB when static IPs are required instead of Elastic IPs attached to instances

### Operational Excellence

1. **Infrastructure as Code**: Manage all load balancer configurations through Terraform for version control and reproducibility
2. **Naming Conventions**: Use consistent, descriptive naming conventions for load balancers, target groups, and listeners
3. **Tagging Strategy**: Apply comprehensive tags for cost allocation, environment identification, and resource management
4. **Change Management**: Test load balancer configuration changes in non-production environments before production deployment
5. **Documentation**: Document load balancer architecture, routing logic, and operational procedures
6. **Backup and DR**: Implement multi-region load balancer deployments for disaster recovery scenarios
7. **Regular Reviews**: Conduct periodic reviews of load balancer configurations, security groups, and listener rules
8. **Automation**: Automate target registration/deregistration with auto-scaling groups or container orchestration platforms

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-alb
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-alb/tree/master/examples
- **AWS ALB Documentation**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html
- **AWS NLB Documentation**: https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html
- **Elastic Load Balancing User Guide**: https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html
- **ALB Listener Rules**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-update-rules.html
- **Target Group Routing**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html
- **Health Checks**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html
- **Authentication with Cognito**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html
- **WAF Integration**: https://docs.aws.amazon.com/waf/latest/developerguide/waf-chapter.html
- **Access Logs**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-access-logs.html
- **CloudWatch Metrics**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html
- **Mutual TLS Authentication**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/mutual-authentication.html
- **ELB Pricing**: https://aws.amazon.com/elasticloadbalancing/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Load Balancer Type Selection**: Choose `application` for HTTP/HTTPS Layer 7 routing; choose `network` for Layer 4 TCP/UDP traffic with ultra-high performance requirements
2. **Multi-AZ Deployment**: Always specify at least two subnets in different Availability Zones for high availability
3. **Security Group Management**: Use `create_security_group = true` and define explicit ingress/egress rules; avoid overly permissive rules
4. **Listener Configuration**: Define listeners with appropriate protocols (HTTP, HTTPS, TCP, TLS) and port numbers; use HTTPS with ACM certificates for secure connections
5. **Target Group Health Checks**: Configure realistic health check parameters based on application behavior; include path, interval, timeout, and thresholds
6. **HTTPS Enforcement**: Implement HTTP to HTTPS redirect rules to enforce encrypted connections for web applications
7. **Access Logging**: Enable access logs for production environments for security analysis and compliance; ensure S3 bucket exists with proper permissions
8. **Tagging Strategy**: Apply consistent tags including Environment, Application, ManagedBy, and CostCenter for resource management and cost allocation
9. **Route53 Integration**: Use the `route53_records` configuration to automatically create DNS records pointing to the load balancer
10. **Deletion Protection**: Enable deletion protection for production load balancers using `enable_deletion_protection = true`
11. **WAF Association**: For internet-facing ALBs handling untrusted traffic, associate AWS WAF ACL using `associate_web_acl = true` and provide `web_acl_arn`
12. **Output Usage**: Export load balancer DNS name, ARN, and target group ARNs for integration with other resources like Route53 and Auto Scaling Groups
