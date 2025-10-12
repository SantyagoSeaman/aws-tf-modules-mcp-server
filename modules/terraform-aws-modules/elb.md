---
module_name: elb
keywords: access-logs, availability-zone, classic-load-balancer, connection-draining, cross-zone-load-balancing, elb, health-check, http, https, idle-timeout, instance-attachment, layer-4, layer-7, listener, load-balancer, monitoring, previous-generation, route53, security-group, ssl, ssl-certificate, ssl-policy, sticky-sessions, subnet, tagging, tcp, tls, traffic-distribution, zone-id
---

# Terraform AWS ELB Module

## Module Information

- **Module Name**: `elb`
- **Source**: `terraform-aws-modules/elb/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-elb
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/elb/aws/latest
- **Latest Version**: 4.0.2
- **Purpose**: Terraform module that creates Classic Load Balancer (ELB) resources on AWS
- **Service**: AWS Elastic Load Balancing - Classic Load Balancer (ELB)
- **Category**: Networking, Load Balancing, Legacy
- **Keywords**: access-logs, availability-zone, classic-load-balancer, connection-draining, cross-zone-load-balancing, elb, health-check, http, https, idle-timeout, instance-attachment, layer-4, layer-7, listener, load-balancer, monitoring, previous-generation, route53, security-group, ssl, ssl-certificate, ssl-policy, sticky-sessions, subnet, tagging, tcp, tls, traffic-distribution, zone-id
- **Use For**: legacy application support, maintaining existing Classic Load Balancer infrastructure, TCP/SSL load balancing for specific requirements, backward compatibility with older AWS deployments, simple HTTP/HTTPS load balancing for non-containerized applications, migrating from Classic to Application Load Balancer, supporting applications requiring instance-level load balancing, cross-zone traffic distribution for EC2 instances

## Description

The AWS ELB Terraform module provides a declarative way to create and manage AWS Classic Load Balancers, also known as Elastic Load Balancers (ELB). Classic Load Balancer is AWS's previous-generation load balancing service that distributes incoming application traffic across multiple EC2 instances in multiple Availability Zones to increase application fault tolerance and availability. While AWS recommends using Application Load Balancer (ALB) or Network Load Balancer (NLB) for new deployments, this module remains essential for maintaining existing infrastructure and supporting legacy applications that depend on Classic Load Balancer features.

The module abstracts the complexity of ELB configuration by providing a simplified interface for defining listeners, health checks, security groups, and instance attachments. It supports both internet-facing and internal load balancers, with configurable options for cross-zone load balancing, connection draining, idle timeouts, and access logging. The module handles critical operational concerns such as SSL/TLS certificate attachment, health check configuration with customizable thresholds, and security group management for controlling inbound and outbound traffic.

Classic Load Balancers operate at both Layer 4 (TCP) and Layer 7 (HTTP/HTTPS), making them suitable for applications that require basic load balancing across EC2 instances without the advanced routing capabilities of modern load balancers. The module includes a separate submodule for managing instance attachments, enabling dynamic scaling scenarios where instances are added or removed from the load balancer pool. With built-in support for Route 53 integration via zone IDs, SSL policy configuration, and comprehensive tagging, this module enables teams to maintain existing Classic Load Balancer deployments with infrastructure-as-code best practices.

## Key Features

- **Classic Load Balancer Creation**: Creates AWS Classic Load Balancers with configurable names and network placement
- **Multiple Listener Support**: Configure multiple listeners for different protocols (HTTP, HTTPS, TCP, SSL) and port combinations
- **Health Check Configuration**: Customizable health checks with configurable protocols, intervals, thresholds, and timeout values
- **Cross-Zone Load Balancing**: Enable traffic distribution across instances in all configured Availability Zones
- **Connection Draining**: Gracefully remove instances from service with configurable draining timeout periods
- **SSL/TLS Support**: Attach SSL certificates and configure SSL security policies for HTTPS and SSL listeners
- **Access Logging**: Optional S3 bucket logging for detailed request analysis and compliance requirements
- **Internal and External Load Balancers**: Support for both internet-facing and internal (VPC-only) load balancers
- **Security Group Management**: Attach security groups to control inbound and outbound traffic to the load balancer
- **Instance Attachment**: Directly attach EC2 instances to the load balancer pool or use separate attachment submodule
- **Idle Timeout Configuration**: Customize connection idle timeout values from 1 to 4000 seconds
- **Route 53 Integration**: Outputs canonical hosted zone ID for creating Route 53 alias records
- **Tagging Support**: Comprehensive tagging for cost allocation, resource organization, and compliance tracking
- **Multi-AZ Deployment**: Deploy load balancers across multiple subnets in different Availability Zones
- **Dynamic Instance Management**: Submodule for programmatically attaching and detaching instances
- **Conditional Creation**: Control resource creation with create_elb flag for flexible module usage

## Main Use Cases

1. **Legacy Application Support**: Maintain existing Classic Load Balancer infrastructure for applications not yet migrated to ALB/NLB
2. **TCP/SSL Load Balancing**: Distribute TCP or SSL traffic when Layer 4 load balancing is required without HTTP-specific features
3. **Simple HTTP Load Balancing**: Basic HTTP/HTTPS load balancing for traditional EC2-based web applications
4. **Backward Compatibility**: Support applications with hard dependencies on Classic Load Balancer behavior
5. **Migration Planning**: Gradual migration from Classic to Application/Network Load Balancers with parallel deployments
6. **Cost Optimization**: Maintain Classic Load Balancers where migration costs exceed operational benefits
7. **Instance-Level Load Balancing**: Distribute traffic directly to EC2 instances without container or IP-based routing
8. **Cross-Zone High Availability**: Ensure traffic distribution across multiple Availability Zones for fault tolerance
9. **SSL Termination**: Offload SSL/TLS encryption from backend instances to the load balancer
10. **Health-Based Routing**: Automatically route traffic only to healthy instances based on configurable health checks

## Submodules

This module contains the following submodules:

### 1. elb_attachment

- **Purpose**: Manages the attachment of EC2 instances to an existing Classic Load Balancer
- **Source**: `terraform-aws-modules/elb/aws//modules/elb_attachment`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/elb/aws/latest/submodules/elb_attachment
- **Key Features**: Dynamic instance attachment, conditional creation control, supports multiple instances
- **Use Cases**: Auto-scaling group integration, blue-green deployments, gradual instance rollouts, dynamic capacity management

## Submodule 1: elb_attachment

### Description

The elb_attachment submodule provides a dedicated resource for attaching EC2 instances to an existing Classic Load Balancer. This submodule is particularly useful in scenarios where the load balancer and instances are managed separately, such as auto-scaling groups, blue-green deployments, or when instances need to be dynamically added or removed from the load balancer pool independently of the load balancer lifecycle.

### Key Features

- Attach one or multiple EC2 instances to an existing Classic Load Balancer
- Conditional attachment creation with `create_attachment` flag
- Supports dynamic instance lists for scaling scenarios
- Independent lifecycle management from the main ELB resource
- Useful for programmatic instance management in automation workflows

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `elb` | `string` | Required | Name of the ELB to attach instances to |
| `instances` | `list(string)` | Required | List of instance IDs to attach to the ELB pool |
| `number_of_instances` | `number` | Required | Number of instances to attach |
| `create_attachment` | `bool` | `true` | Whether to create the attachment resource |

### Main Outputs

This submodule does not expose any outputs.

### Usage Example

```hcl
# Create the ELB first
module "web_elb" {
  source = "terraform-aws-modules/elb/aws"

  name = "web-elb"

  subnets         = ["subnet-12345678", "subnet-87654321"]
  security_groups = ["sg-12345678"]
  internal        = false

  listener = [
    {
      instance_port     = 80
      instance_protocol = "HTTP"
      lb_port           = 80
      lb_protocol       = "HTTP"
    }
  ]

  health_check = {
    target              = "HTTP:80/"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
  }

  tags = {
    Environment = "production"
  }
}

# Attach instances separately using the submodule
module "elb_instance_attachment" {
  source = "terraform-aws-modules/elb/aws//modules/elb_attachment"

  elb                 = module.web_elb.elb_name
  instances           = ["i-1234567890abcdef0", "i-0987654321fedcba0"]
  number_of_instances = 2
}

# Example: Conditional attachment based on environment
module "elb_conditional_attachment" {
  source = "terraform-aws-modules/elb/aws//modules/elb_attachment"

  create_attachment = var.environment == "production"

  elb                 = module.web_elb.elb_name
  instances           = var.instance_ids
  number_of_instances = length(var.instance_ids)
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_elb` | `bool` | `true` | Whether to create the load balancer or not |
| `name` | `string` | `null` | The name of the ELB |
| `name_prefix` | `string` | `null` | The prefix name of the ELB |
| `subnets` | `list(string)` | Required | List of subnet IDs to attach to the ELB |
| `security_groups` | `list(string)` | Required | List of security group IDs to assign to the ELB |
| `internal` | `bool` | `false` | If true, ELB will be an internal ELB |
| `listener` | `list(map(string))` | Required | List of listener blocks (instance_port, instance_protocol, lb_port, lb_protocol, ssl_certificate_id) |
| `health_check` | `map(string)` | Required | Health check block (target, interval, healthy_threshold, unhealthy_threshold, timeout) |
| `instances` | `list(string)` | `[]` | List of instance IDs to place in the ELB pool |
| `number_of_instances` | `number` | `0` | Number of instances to attach to ELB |
| `cross_zone_load_balancing` | `bool` | `true` | Enable cross-zone load balancing |
| `idle_timeout` | `number` | `60` | The time in seconds that the connection is allowed to be idle |
| `connection_draining` | `bool` | `false` | Boolean to enable connection draining |
| `connection_draining_timeout` | `number` | `300` | The time in seconds to allow for connections to drain |
| `access_logs` | `map(string)` | `{}` | Access logs block (bucket, bucket_prefix, interval, enabled) |
| `tags` | `map(string)` | `{}` | A mapping of tags to assign to the resource |

## Main Outputs

| Output | Description |
|--------|-------------|
| `elb_id` | The name of the ELB |
| `elb_arn` | The ARN of the ELB |
| `elb_name` | The name of the ELB |
| `elb_dns_name` | The DNS name of the ELB |
| `elb_instances` | The list of instances in the ELB |
| `elb_source_security_group_id` | The ID of the security group for inbound rules for load balancer's back-end application instances |
| `elb_zone_id` | The canonical hosted zone ID of the ELB (for use in a Route 53 Alias record) |

## Usage Examples

### Example 1: Basic HTTP Load Balancer

```hcl
module "elb_http" {
  source = "terraform-aws-modules/elb/aws"

  name = "web-elb"

  subnets         = ["subnet-12345678", "subnet-87654321"]
  security_groups = ["sg-12345678"]
  internal        = false

  listener = [
    {
      instance_port     = 80
      instance_protocol = "HTTP"
      lb_port           = 80
      lb_protocol       = "HTTP"
    }
  ]

  health_check = {
    target              = "HTTP:80/health"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
  }

  tags = {
    Owner       = "DevOps"
    Environment = "production"
  }
}
```

### Example 2: HTTPS Load Balancer with SSL Certificate

```hcl
module "elb_https" {
  source = "terraform-aws-modules/elb/aws"

  name = "secure-web-elb"

  subnets         = module.vpc.public_subnets
  security_groups = [module.elb_security_group.security_group_id]
  internal        = false

  listener = [
    {
      instance_port      = 443
      instance_protocol  = "HTTPS"
      lb_port            = 443
      lb_protocol        = "HTTPS"
      ssl_certificate_id = "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012"
    },
    {
      instance_port     = 80
      instance_protocol = "HTTP"
      lb_port           = 80
      lb_protocol       = "HTTP"
    }
  ]

  health_check = {
    target              = "HTTPS:443/"
    interval            = 30
    healthy_threshold   = 3
    unhealthy_threshold = 2
    timeout             = 5
  }

  cross_zone_load_balancing   = true
  idle_timeout                = 120
  connection_draining         = true
  connection_draining_timeout = 300

  tags = {
    Name        = "secure-web-elb"
    Environment = "production"
    Terraform   = "true"
  }
}
```

### Example 3: Internal Load Balancer with Access Logs

```hcl
module "elb_internal" {
  source = "terraform-aws-modules/elb/aws"

  name = "internal-app-elb"

  subnets         = module.vpc.private_subnets
  security_groups = [aws_security_group.internal_elb.id]
  internal        = true

  listener = [
    {
      instance_port     = 8080
      instance_protocol = "HTTP"
      lb_port           = 8080
      lb_protocol       = "HTTP"
    }
  ]

  health_check = {
    target              = "HTTP:8080/healthcheck"
    interval            = 15
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 10
  }

  access_logs = {
    bucket        = "my-elb-logs-bucket"
    bucket_prefix = "internal-app-elb"
    interval      = 60
    enabled       = true
  }

  cross_zone_load_balancing = true

  tags = {
    Name        = "internal-app-elb"
    Environment = "production"
    Internal    = "true"
  }
}
```

### Example 4: TCP Load Balancer for Database Connections

```hcl
module "elb_tcp" {
  source = "terraform-aws-modules/elb/aws"

  name = "database-proxy-elb"

  subnets         = module.vpc.private_subnets
  security_groups = [aws_security_group.db_proxy.id]
  internal        = true

  listener = [
    {
      instance_port     = 5432
      instance_protocol = "TCP"
      lb_port           = 5432
      lb_protocol       = "TCP"
    }
  ]

  health_check = {
    target              = "TCP:5432"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
  }

  cross_zone_load_balancing   = true
  connection_draining         = true
  connection_draining_timeout = 60

  tags = {
    Name        = "database-proxy-elb"
    Environment = "production"
    Service     = "postgresql"
  }
}
```

### Example 5: Load Balancer with Instance Attachment

```hcl
module "elb_with_instances" {
  source = "terraform-aws-modules/elb/aws"

  name = "app-elb-with-instances"

  subnets         = module.vpc.public_subnets
  security_groups = [module.elb_sg.security_group_id]
  internal        = false

  listener = [
    {
      instance_port     = 80
      instance_protocol = "HTTP"
      lb_port           = 80
      lb_protocol       = "HTTP"
    },
    {
      instance_port      = 443
      instance_protocol  = "HTTPS"
      lb_port            = 443
      lb_protocol        = "HTTPS"
      ssl_certificate_id = data.aws_acm_certificate.main.arn
    }
  ]

  health_check = {
    target              = "HTTP:80/health"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
  }

  # Attach instances directly
  number_of_instances = 3
  instances = [
    aws_instance.web[0].id,
    aws_instance.web[1].id,
    aws_instance.web[2].id
  ]

  cross_zone_load_balancing   = true
  idle_timeout                = 60
  connection_draining         = true
  connection_draining_timeout = 300

  tags = {
    Name        = "app-elb"
    Environment = "production"
  }
}
```

### Example 6: Multi-Protocol Load Balancer

```hcl
module "elb_multi_protocol" {
  source = "terraform-aws-modules/elb/aws"

  name = "multi-protocol-elb"

  subnets         = module.vpc.public_subnets
  security_groups = [aws_security_group.elb.id]
  internal        = false

  listener = [
    {
      instance_port     = 80
      instance_protocol = "HTTP"
      lb_port           = 80
      lb_protocol       = "HTTP"
    },
    {
      instance_port      = 443
      instance_protocol  = "HTTPS"
      lb_port            = 443
      lb_protocol        = "HTTPS"
      ssl_certificate_id = aws_acm_certificate.cert.arn
    },
    {
      instance_port     = 8080
      instance_protocol = "HTTP"
      lb_port           = 8080
      lb_protocol       = "HTTP"
    }
  ]

  health_check = {
    target              = "HTTP:80/"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
  }

  cross_zone_load_balancing   = true
  idle_timeout                = 90
  connection_draining         = true
  connection_draining_timeout = 300

  tags = {
    Name        = "multi-protocol-elb"
    Environment = "staging"
  }
}
```

### Example 7: Load Balancer with Custom Health Check

```hcl
module "elb_custom_healthcheck" {
  source = "terraform-aws-modules/elb/aws"

  name = "custom-health-elb"

  subnets         = module.vpc.public_subnets
  security_groups = [aws_security_group.elb.id]
  internal        = false

  listener = [
    {
      instance_port     = 8080
      instance_protocol = "HTTP"
      lb_port           = 80
      lb_protocol       = "HTTP"
    }
  ]

  # Custom health check with aggressive settings
  health_check = {
    target              = "HTTP:8080/api/health"
    interval            = 10
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
  }

  cross_zone_load_balancing   = true
  idle_timeout                = 300
  connection_draining         = true
  connection_draining_timeout = 60

  tags = {
    Name        = "custom-health-elb"
    Environment = "production"
    Monitoring  = "enhanced"
  }
}
```

### Example 8: Conditional ELB Creation

```hcl
module "elb_conditional" {
  source = "terraform-aws-modules/elb/aws"

  create_elb = var.environment == "production"

  name = "conditional-elb"

  subnets         = module.vpc.public_subnets
  security_groups = [aws_security_group.elb.id]
  internal        = false

  listener = [
    {
      instance_port     = 80
      instance_protocol = "HTTP"
      lb_port           = 80
      lb_protocol       = "HTTP"
    }
  ]

  health_check = {
    target              = "HTTP:80/"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
  }

  tags = {
    Name        = "conditional-elb"
    Environment = var.environment
  }
}
```

## Best Practices

### Migration and Modernization

1. **Plan Migration to ALB/NLB**: For new deployments, use Application Load Balancer (ALB) or Network Load Balancer (NLB) instead of Classic Load Balancer
2. **Evaluate Migration Path**: Assess existing Classic Load Balancers for migration opportunities to modern load balancer types
3. **Document Dependencies**: Identify and document applications with hard dependencies on Classic Load Balancer behavior before migration
4. **Parallel Deployment**: Run ALB/NLB in parallel with Classic ELB during migration to validate functionality
5. **Feature Comparison**: Review ALB/NLB features that may benefit your application (path-based routing, WebSocket, HTTP/2, etc.)
6. **Cost Analysis**: Compare costs between Classic ELB and modern load balancers for your traffic patterns

### Listener Configuration

1. **Use HTTPS for Production**: Always use HTTPS listeners with valid SSL certificates for production traffic
2. **Configure SSL Policies**: Use the latest TLS policies (ELBSecurityPolicy-TLS-1-2-2017-01 or newer) for secure connections
3. **Separate HTTP and HTTPS**: Configure both HTTP (port 80) and HTTPS (port 443) listeners with HTTP redirecting to HTTPS at application level
4. **Match Instance Protocols**: Ensure instance_protocol matches the actual protocol your instances are listening on
5. **Validate Port Mapping**: Double-check that lb_port and instance_port are correctly mapped for your application architecture
6. **Limit Listener Count**: Use only necessary listeners; each listener adds complexity and potential attack surface

### Health Check Configuration

1. **Use Dedicated Health Endpoints**: Create specific health check endpoints (e.g., /health, /healthcheck) rather than checking root paths
2. **Set Appropriate Intervals**: Use 15-30 second intervals for most applications; shorter intervals for critical services
3. **Balance Thresholds**: Set healthy_threshold to 2-3 and unhealthy_threshold to 2-3 based on your tolerance for false positives/negatives
4. **Match Health Check Protocol**: Use the same protocol for health checks as your primary listener when possible
5. **Optimize Timeout Values**: Set health check timeout to less than the interval (typically 5-10 seconds)
6. **Test Health Endpoints**: Ensure health check endpoints respond quickly (under 1 second) to avoid unnecessary instance removal
7. **Monitor Health Check Failures**: Set up CloudWatch alarms for unhealthy instance counts to detect application issues

### Network Configuration

1. **Enable Cross-Zone Load Balancing**: Always enable cross_zone_load_balancing for even traffic distribution across AZs
2. **Deploy Multi-AZ**: Place load balancers in at least two Availability Zones for high availability
3. **Use Private Subnets for Internal ELBs**: Deploy internal load balancers in private subnets to prevent direct internet access
4. **Validate Subnet Routing**: Ensure subnets have appropriate route tables for internet-facing or internal load balancers
5. **Security Group Best Practices**: Create dedicated security groups for ELBs separate from instance security groups
6. **Restrict Source IPs**: For internal ELBs, limit security group ingress to specific CIDR blocks or VPC ranges

### Security

1. **Implement Least Privilege**: Use restrictive security group rules allowing only necessary ports and protocols
2. **Use ACM for Certificates**: Leverage AWS Certificate Manager for SSL certificate provisioning and automatic renewal
3. **Enable Access Logs**: Configure access logging to S3 for security auditing and troubleshooting
4. **Encrypt Logs**: Enable S3 bucket encryption for access log storage
5. **Regular Certificate Rotation**: Monitor certificate expiration and rotate before expiry
6. **Implement Backend Encryption**: Use HTTPS/SSL for both listener and instance protocols when handling sensitive data
7. **Review Security Policies**: Regularly review and update SSL security policies to address new vulnerabilities

### Performance Optimization

1. **Configure Appropriate Idle Timeout**: Set idle_timeout based on your application's connection patterns (60-300 seconds typical)
2. **Enable Connection Draining**: Always enable connection_draining with appropriate timeout (60-300 seconds) for graceful instance removal
3. **Optimize Health Check Frequency**: Balance health check frequency with instance overhead; more frequent checks increase load
4. **Monitor Connection Metrics**: Track ELB connection metrics to identify bottlenecks or scaling needs
5. **Pre-Warm for Traffic Spikes**: Contact AWS support to pre-warm ELBs before expected traffic increases
6. **Use Keep-Alive**: Configure backend instances to support HTTP keep-alive for connection reuse

### Cost Optimization

1. **Evaluate ELB Necessity**: Assess if Classic ELB is required or if a modern load balancer offers better cost efficiency
2. **Right-Size Capacity**: Monitor traffic patterns and ensure you're not over-provisioned
3. **Clean Up Unused ELBs**: Regularly audit and remove load balancers with no traffic or attached instances
4. **Optimize Data Transfer**: Minimize cross-AZ data transfer by understanding traffic patterns
5. **Use Internal ELBs**: For internal services, use internal ELBs to avoid internet gateway charges
6. **Monitor Costs**: Set up AWS Cost Explorer alerts for ELB costs to detect unexpected increases

### High Availability

1. **Multi-AZ Deployment**: Deploy across at least two Availability Zones for fault tolerance
2. **Health Check Redundancy**: Configure health checks to quickly detect and remove unhealthy instances
3. **Connection Draining**: Enable connection draining to gracefully handle instance termination during deployments
4. **Auto Scaling Integration**: Integrate with Auto Scaling groups for automatic capacity management
5. **Route 53 Integration**: Use Route 53 alias records with health checks for DNS-level failover
6. **Monitor ELB Health**: Set up CloudWatch alarms for ELB health metrics (healthy host count, HTTP errors, etc.)

### Operational Excellence

1. **Implement Comprehensive Tagging**: Use consistent tags for cost allocation, environment identification, and automation
2. **Document Configuration**: Maintain documentation of listener configurations, health check settings, and security groups
3. **Use Infrastructure as Code**: Manage all ELB configuration through Terraform for reproducibility and version control
4. **Automate Deployments**: Integrate ELB creation/updates into CI/CD pipelines
5. **Regular Backups**: Export Terraform state and configuration to version control
6. **Change Management**: Use Terraform plan before applying changes to production load balancers
7. **Monitoring and Alerting**: Configure CloudWatch dashboards and alarms for ELB metrics

### Logging and Monitoring

1. **Enable Access Logs**: Configure access_logs to S3 for detailed request analysis
2. **Set Appropriate Log Intervals**: Use 5 or 60-minute intervals based on traffic volume and analysis needs
3. **Implement Log Lifecycle**: Configure S3 lifecycle policies to transition or delete old logs for cost management
4. **CloudWatch Metrics**: Monitor key metrics like HealthyHostCount, UnHealthyHostCount, RequestCount, Latency
5. **Set Up Alarms**: Create CloudWatch alarms for critical metrics (unhealthy hosts, high latency, 5xx errors)
6. **Log Analysis**: Use CloudWatch Insights or Athena to analyze access logs for security and performance insights
7. **Integrate with SIEM**: Forward logs to security information and event management (SIEM) systems for compliance

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-elb
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/elb/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-elb/tree/master/examples
- **AWS Classic Load Balancer Documentation**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/introduction.html
- **Classic Load Balancer User Guide**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/
- **ELB Health Checks**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-healthchecks.html
- **SSL Security Policies**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-security-policy-table.html
- **Migration to Application Load Balancer**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-migrate.html
- **ELB Access Logs**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/access-log-collection.html
- **Classic Load Balancer Pricing**: https://aws.amazon.com/elasticloadbalancing/pricing/
- **AWS Certificate Manager**: https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html
- **ELB Best Practices**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/best-practices.html
- **Troubleshooting Classic Load Balancers**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-troubleshooting.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Legacy Service**: Classic Load Balancer is a previous-generation service; prefer ALB or NLB for new deployments
2. **Subnet Requirements**: Ensure subnets are in different Availability Zones for high availability configurations
3. **Health Check Validation**: Verify health check endpoints return 200 status codes before deploying to production
4. **SSL Certificate Management**: Use ACM module or data sources to reference SSL certificates; never hardcode certificate IDs
5. **Listener Protocol Matching**: Ensure instance_protocol matches what instances actually listen on to avoid connection failures
6. **Security Group Coordination**: Create ELB security groups before the ELB and instance security groups referencing ELB SG
7. **Connection Draining Timing**: Set connection_draining_timeout based on longest expected request duration (typically 60-300s)
8. **Access Log Bucket**: If enabling access_logs, ensure S3 bucket exists, has proper ELB permissions, and is in the same region
9. **Instance Attachment Timing**: When using instances parameter, ensure instances exist before ELB creation or use depends_on
10. **Cross-Zone Data Transfer**: Enabling cross_zone_load_balancing incurs cross-AZ data transfer costs; factor into budget
11. **Health Check Tuning**: Calculate health check response time as interval × unhealthy_threshold to understand failure detection time
12. **Route 53 Integration**: Use elb_zone_id output for creating Route 53 alias records instead of CNAME records
13. **Conditional Creation**: Use create_elb flag for environment-specific deployments or migration scenarios
14. **Idle Timeout for WebSockets**: Increase idle_timeout to 3600 seconds for applications using WebSockets or long-polling
15. **Migration Strategy**: When migrating to ALB, run both load balancers in parallel, gradually shifting traffic using Route 53 weighted routing
