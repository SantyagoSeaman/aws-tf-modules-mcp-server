# Terraform AWS ELB Module

## Module Information

- **Module Name**: `elb`
- **Module ID**: `terraform-aws-modules/elb/aws`
- **Source**: `terraform-aws-modules/elb/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-elb
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/elb/aws/latest
- **Latest Version**: 4.0.2
- **Purpose**: Terraform module that creates Classic Load Balancer (ELB) resources on AWS
- **Service**: AWS Elastic Load Balancing - Classic Load Balancer (ELB)
- **Category**: Networking, Load Balancing, Legacy
- **Keywords**: elb, classic-load-balancer, load-balancer, health-check, listener, ssl, https, tcp, connection-draining, cross-zone, instance-attachment, access-logs, security-group, route53, layer4, layer7
- **Use For**: legacy application support, maintaining existing Classic Load Balancer infrastructure, TCP/SSL load balancing without HTTP-aware routing, backward compatibility with older AWS/EC2-Classic-era deployments, simple HTTP/HTTPS load balancing for non-containerized EC2 applications, staged migration from Classic to Application/Network Load Balancer, instance-level (not target-group) load balancing, cross-AZ traffic distribution for EC2 instances

## Description

The AWS ELB module provisions AWS Classic Load Balancers (the `aws_elb` resource), the previous-generation Elastic Load Balancing product that distributes TCP/SSL (Layer 4) or HTTP/HTTPS (Layer 7) traffic directly across EC2 instances in one or more Availability Zones. AWS now recommends Application Load Balancer (ALB) for HTTP/HTTPS workloads and Network Load Balancer (NLB) for TCP/UDP workloads for all new deployments — Classic Load Balancer is a legacy/maintenance-mode service. This module exists to manage existing Classic ELB infrastructure and applications with hard dependencies on Classic ELB semantics (e.g., instance-level health checks and registration rather than target groups) as code.

The module wraps two internal submodules: `modules/elb`, which creates the `aws_elb` resource itself (listeners, health check, access logs, cross-zone load balancing, idle timeout, connection draining), and `modules/elb_attachment`, which creates `aws_elb_attachment` resources to register EC2 instances with the load balancer. The root module composes both automatically — passing `instances`/`number_of_instances` at the root level attaches instances as part of the same `terraform apply`. The `elb_attachment` submodule can also be called independently to attach instances to an ELB created elsewhere (e.g., by an Auto Scaling group lifecycle hook or a separate Terraform state), decoupling instance registration from the load balancer's own lifecycle.

Because Classic ELB predates target groups, instances are registered directly by instance ID and health-checked individually rather than through a shared target group, and there is no native support for container/IP-based targets, path-based routing, or WebSocket-aware routing — those require ALB. The module supports internet-facing and internal (VPC-only) load balancers, multiple listeners per protocol/port combination, SSL certificate attachment (typically sourced from ACM), S3 access logging, and standard resource tagging, and it exposes the ELB's canonical hosted zone ID for Route 53 alias records.

## Key Features

- **Classic Load Balancer Creation**: Creates an `aws_elb` resource with configurable name/name_prefix and subnet placement
- **Multiple Listener Support**: Configure multiple listener blocks mixing HTTP, HTTPS, TCP, and SSL protocols/ports on one ELB
- **Instance-Level Health Checks**: Customizable health checks (target, interval, thresholds, timeout) evaluated per registered instance
- **Cross-Zone Load Balancing**: Enabled by default; evenly distributes traffic across instances in all attached AZs at no extra charge
- **Connection Draining**: Gracefully deregisters instances over a configurable timeout instead of dropping in-flight connections
- **SSL/TLS Termination**: Attach an SSL certificate (ACM ARN) per listener and terminate HTTPS/SSL at the load balancer
- **S3 Access Logging**: Optional per-request access logs delivered to an S3 bucket for auditing and troubleshooting
- **Internal or Internet-Facing**: Deploy as a public-facing ELB or restrict to a VPC-internal ELB via `internal = true`
- **Direct or Decoupled Instance Attachment**: Attach instances inline via `instances`/`number_of_instances`, or manage attachment independently with the `elb_attachment` submodule
- **Route 53 Ready**: Outputs the canonical hosted zone ID (`elb_zone_id`) needed for alias records
- **Conditional Creation**: `create_elb` flag (`count`-based) allows disabling the module entirely per environment without removing the block

## Main Use Cases

1. **Legacy Application Support**: Maintain existing Classic Load Balancer infrastructure not yet migrated to ALB/NLB
2. **TCP/SSL Load Balancing**: Distribute raw TCP or SSL traffic (e.g., non-HTTP protocols) at Layer 4
3. **Simple HTTP/HTTPS Load Balancing**: Basic web traffic distribution for traditional, non-containerized EC2 fleets
4. **Backward Compatibility**: Support applications or tooling with hard dependencies on Classic ELB instance registration behavior
5. **Migration Planning**: Run Classic ELB alongside a new ALB/NLB during a phased cutover, shifting traffic via Route 53 weighted routing
6. **Auto Scaling Group Backends**: Register EC2 instances launched by an ASG using the `elb_attachment` submodule
7. **Instance-Level Load Balancing**: Distribute traffic directly to EC2 instances without target groups or container-based routing
8. **Multi-AZ High Availability**: Spread traffic across instances in multiple Availability Zones for fault tolerance
9. **SSL Offload**: Terminate SSL/TLS at the load balancer to reduce CPU load on backend instances
10. **Health-Based Traffic Routing**: Automatically stop routing to instances that fail configurable health checks

## Submodules

This module contains the following submodules:

### 1. elb_attachment

- **Purpose**: Manages `aws_elb_attachment` resources to register EC2 instances with an existing Classic Load Balancer
- **Source**: `terraform-aws-modules/elb/aws//modules/elb_attachment`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/elb/aws/latest/submodules/elb_attachment
- **Key Features**: Attach one or many instances by ID, conditional creation via `create_attachment`, independent lifecycle from the ELB itself
- **Use Cases**: Auto Scaling group integration, blue-green deployments, gradual/rolling instance rollouts, attaching instances managed in a separate Terraform state

## Submodule 1: elb_attachment

### Description

The `elb_attachment` submodule creates `aws_elb_attachment` resources that register EC2 instances with an existing Classic Load Balancer by name/ID. It is used when instance registration must be managed separately from the ELB's own lifecycle — for example, when instances come from an Auto Scaling group, a separate Terraform configuration/state, or need to be attached/detached without touching the ELB resource itself. The root `elb` module already calls this submodule internally when `instances`/`number_of_instances` are set, so calling it directly is only needed for decoupled attachment scenarios.

### Key Features

- Attaches one or many EC2 instances to an existing Classic Load Balancer by ID
- `create_attachment` flag allows disabling attachment per environment without removing the block
- Accepts a dynamic instance list, suitable for scaling scenarios
- Independent lifecycle from the ELB resource — safe to apply/destroy separately

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `elb` | `string` | Required | Name/ID of the ELB to attach instances to |
| `instances` | `list(string)` | Required | List of EC2 instance IDs to attach to the ELB pool |
| `number_of_instances` | `number` | Required | Number of instances to attach (must match length used from `instances`) |
| `create_attachment` | `bool` | `true` | Whether to create the attachment resources |

### Main Outputs

This submodule does not expose any outputs.

### Usage Example

```hcl
# Attach instances to an ELB created elsewhere (e.g., a separate module/state)
module "elb_instance_attachment" {
  source = "terraform-aws-modules/elb/aws//modules/elb_attachment"

  elb                 = module.web_elb.elb_name
  instances           = ["i-1234567890abcdef0", "i-0987654321fedcba0"]
  number_of_instances = 2
}

# Conditional attachment, e.g. only in production
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
| `subnets` | `list(string)` | Required | List of subnet IDs to attach to the ELB |
| `security_groups` | `list(string)` | Required | List of security group IDs to assign to the ELB |
| `listener` | `list(map(string))` | Required | List of listener blocks: `instance_port`, `instance_protocol`, `lb_port`, `lb_protocol`, optional `ssl_certificate_id` |
| `health_check` | `map(string)` | Required | Health check block: `target`, `interval`, `healthy_threshold`, `unhealthy_threshold`, `timeout` |
| `create_elb` | `bool` | `true` | Whether to create the ELB (and its instance attachments) |
| `name` | `string` | `null` | The name of the ELB (also used as the `Name` tag) |
| `name_prefix` | `string` | `null` | Creates a unique name using this prefix instead of `name` |
| `internal` | `bool` | `false` | If `true`, creates a VPC-internal ELB instead of internet-facing |
| `instances` | `list(string)` | `[]` | List of instance IDs to register with the ELB pool directly |
| `number_of_instances` | `number` | `0` | Number of instances to attach from `instances` |
| `cross_zone_load_balancing` | `bool` | `true` | Enable cross-zone load balancing (free of charge; leave enabled) |
| `idle_timeout` | `number` | `60` | Idle connection timeout in seconds (1–4000); increase for WebSockets/long-polling |
| `connection_draining` | `bool` | `false` | Enable connection draining on deregistration |
| `connection_draining_timeout` | `number` | `300` | Seconds to allow in-flight connections to drain |
| `access_logs` | `map(string)` | `{}` | Access logs block: `bucket`, optional `bucket_prefix`, `interval`, `enabled` |
| `tags` | `map(string)` | `{}` | A mapping of tags to assign to the resource |

## Main Outputs

| Output | Description |
|--------|-------------|
| `elb_id` | The name of the ELB |
| `elb_arn` | The ARN of the ELB |
| `elb_name` | The name of the ELB |
| `elb_dns_name` | The DNS name of the ELB |
| `elb_instances` | The list of instance IDs currently registered with the ELB |
| `elb_source_security_group_id` | Security group ID to reference in backend instance security group ingress rules (VPC only) |
| `elb_zone_id` | Canonical hosted zone ID of the ELB, for use in a Route 53 alias record |

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
      ssl_certificate_id = module.acm.acm_certificate_arn
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
  }
}
```

### Example 3: Internal Load Balancer with Access Logs and Direct Instance Attachment

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

  # Attach instances inline — the module handles this via the elb_attachment submodule
  number_of_instances = 2
  instances            = [aws_instance.app[0].id, aws_instance.app[1].id]

  tags = {
    Name        = "internal-app-elb"
    Environment = "production"
  }
}
```

### Example 4: TCP Load Balancer for a Non-HTTP Service

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

  connection_draining         = true
  connection_draining_timeout = 60

  tags = {
    Name        = "database-proxy-elb"
    Environment = "production"
  }
}
```

## Best Practices

### When to Use Classic ELB

1. **Prefer ALB/NLB for New Work**: Use Application Load Balancer for HTTP/HTTPS and Network Load Balancer for TCP/UDP/TLS in all new deployments; only use Classic ELB to maintain existing infrastructure
2. **Document Hard Dependencies**: Before migrating, identify applications relying on Classic ELB-specific behavior (instance-level health checks, `X-Forwarded-For` handling, sticky session cookies)
3. **Migrate Incrementally**: Run the replacement ALB/NLB in parallel and shift traffic gradually with Route 53 weighted routing rather than a hard cutover

### Listener and SSL Configuration

1. **Terminate SSL with ACM**: Source `ssl_certificate_id` from the `terraform-aws-modules/acm` module or an `aws_acm_certificate` data source; never hardcode certificate ARNs
2. **Redirect HTTP to HTTPS at the App Layer**: Classic ELB cannot redirect protocols itself, so handle HTTP→HTTPS redirection in the application if both listeners are exposed
3. **Match Instance Protocol to Backend**: Ensure `instance_protocol` matches what the instance actually serves, or requests will fail after passing the health check
4. **Keep Listener Count Minimal**: Each additional listener/port increases the security group surface area that must be opened

### Health Checks

1. **Use a Dedicated Endpoint**: Point `target` at a lightweight, purpose-built health endpoint (e.g., `/health`) rather than `/`
2. **Balance Thresholds and Interval**: `healthy_threshold`/`unhealthy_threshold` of 2–3 with a 15–30s `interval` is a reasonable default; detection time is roughly `interval × unhealthy_threshold`
3. **Keep Timeout Below Interval**: Set `timeout` to less than `interval` (typically 5s) so checks don't overlap
4. **Match Health Check Protocol**: Use the same protocol as the primary listener where practical for the most representative signal

### Network and Security

1. **Use Private Subnets for Internal ELBs**: Set `internal = true` and place the ELB in private subnets to avoid public exposure
2. **Dedicated Security Group**: Give the ELB its own security group; reference `elb_source_security_group_id` in backend instance security group ingress rules rather than opening backend ports broadly
3. **Deploy Across Multiple AZs**: Pass subnets from at least two Availability Zones so cross-zone load balancing (enabled by default, at no extra cost) provides real fault tolerance

### Reliability and Performance

1. **Enable Connection Draining**: Set `connection_draining = true` with a timeout covering the longest expected in-flight request (60–300s typical) so deploys/scale-in don't drop active connections
2. **Tune Idle Timeout for Long-Lived Connections**: Raise `idle_timeout` toward 3600s for WebSocket or long-polling workloads; the default 60s is fine for typical request/response traffic
3. **Leave Cross-Zone Load Balancing Enabled**: It is free and improves distribution evenness across AZs — there is no cost reason to disable it
4. **Integrate with Auto Scaling**: Use the `elb_attachment` submodule (or an ASG's own load balancer attachment) so instances register/deregister automatically as the group scales

### Operational Excellence

1. **Tag Consistently**: Populate `tags` for cost allocation and ownership; the module always merges in a `Name` tag from `var.name`
2. **Enable Access Logs for Auditing**: Set `access_logs.bucket` to an S3 bucket with correct ELB log-delivery permissions in the same region
3. **Use `create_elb` for Environment Gating**: Toggle the whole module on/off per environment (e.g., `create_elb = var.environment == "production"`) instead of conditionally including the module block
4. **Reference, Don't Hardcode, Instance IDs**: Pass instance IDs from `aws_instance`/ASG resources or the `elb_attachment` submodule rather than literal strings, so attachment stays in sync with instance lifecycle

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-elb
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/elb/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-elb/tree/master/examples
- **AWS Classic Load Balancer Guide**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/introduction.html
- **ELB Health Checks**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-healthchecks.html
- **Cross-Zone Load Balancing**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-disable-crosszone-lb.html
- **SSL Security Policies**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-security-policy-table.html
- **Migrating to Application Load Balancer**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-migrate.html
- **ELB Access Logs**: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/access-log-collection.html
- **Elastic Load Balancing Pricing**: https://aws.amazon.com/elasticloadbalancing/pricing/
- **terraform-aws-modules/acm**: https://registry.terraform.io/modules/terraform-aws-modules/acm/aws/latest

## Notes for AI Agents

When using this module in automated workflows:

1. **Legacy Service**: Classic ELB is in maintenance mode; default to ALB (`terraform-aws-modules/alb`) or NLB for new HTTP/HTTPS or TCP workloads unless the user explicitly needs Classic ELB compatibility
2. **Requires Terraform >= 1.0 and AWS provider >= 4.0**
3. **Listener Blocks Are Maps, Not HCL Blocks**: `listener` and `health_check` are passed as `list(map(string))`/`map(string)` variables, not native `aws_elb` nested blocks — build them as Terraform lists/maps
4. **`ssl_certificate_id` Is Optional Per Listener**: Only include it on listeners that terminate SSL/HTTPS; omit it entirely for plain HTTP/TCP listeners
5. **Instance Attachment Timing**: Instances passed via `instances` must already exist (or use `depends_on`) — the module does not create EC2 instances itself
6. **Root vs. Submodule Attachment**: Only call `modules/elb_attachment` directly when attaching instances to an ELB not created by the same `elb` module call; otherwise pass `instances`/`number_of_instances` to the root module
7. **`name` vs `name_prefix`**: Provide exactly one; `name` also becomes the merged `Name` tag, `name_prefix` does not
8. **Cross-Zone Load Balancing Is Free**: Do not disable `cross_zone_load_balancing` for cost reasons — it incurs no additional data transfer charge
9. **Access Log Bucket Prerequisites**: The target S3 bucket must exist, be in the same region, and grant the ELB log-delivery principal write access (see `terraform-aws-modules/s3-bucket` `attach_elb_log_delivery_policy`)
10. **Route 53 Alias, Not CNAME**: Use the `elb_zone_id` and `elb_dns_name` outputs to create a Route 53 alias record rather than a CNAME
11. **`elb_source_security_group_id` Is VPC-Only**: This output is only meaningful for ELBs launched inside a VPC (the default for all modern accounts)
12. **`create_elb` Also Gates Attachment**: Setting `create_elb = false` disables both the ELB and its inline instance attachments in the same apply
