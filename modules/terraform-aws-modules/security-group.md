# Terraform AWS Security Group Module

## Module Information

- **Module Name**: terraform-aws-security-group
- **Source**: `terraform-aws-modules/security-group/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-security-group
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest
- **Latest Version**: Check registry for current version
- **Purpose**: Terraform module that creates AWS VPC security groups with support for predefined rules for common services and custom rule configurations
- **Service**: AWS VPC Security Groups (Virtual Private Cloud Security Groups)
- **Category**: Networking, Security, Firewall
- **Keywords**: security-group, sg, firewall, vpc, network-security, ingress, egress, inbound-rules, outbound-rules, cidr-blocks, source-security-group, ipv4, ipv6, prefix-list, network-acl, stateful-firewall, tcp, udp, icmp, ssh, http, https, mysql, postgresql, redis, kafka, elasticsearch, rabbitmq, mongodb, rdp, winrm, ntp, smtp, ldap, docker, kubernetes, prometheus, grafana, consul, vault, openvpn, squid, nginx, apache, tomcat, custom-rules, predefined-rules, rule-groups
- **Use For**: Web server access control, database security hardening, SSH bastion host configuration, microservices network isolation, API gateway security, load balancer security groups, container orchestration networking, monitoring system access, VPN endpoint security, multi-tier application segmentation, compliance and regulatory requirements, zero-trust network architecture

## Description

This Terraform module provides comprehensive management of AWS VPC security groups, which act as virtual firewalls controlling inbound and outbound traffic for AWS resources such as EC2 instances, RDS databases, and load balancers. The module offers two primary approaches: over 50 predefined submodules for common services (HTTP, HTTPS, SSH, MySQL, PostgreSQL, Redis, Kafka, etc.) with sensible default rules, and a flexible main module for creating custom security groups with tailored rule configurations. This dual approach enables rapid deployment of standard security patterns while maintaining full flexibility for complex networking requirements.

The module addresses common security group management challenges by providing standardized rule definitions, support for computed values in rule configuration, and conditional security group creation. It supports all AWS security group features including IPv4/IPv6 CIDR blocks, VPC endpoint prefix lists, security group references for service-to-service communication, and detailed rule descriptions for documentation. The module's predefined rules eliminate the need to remember port numbers and protocols for common services, reducing configuration errors and improving consistency across environments.

Key architectural capabilities include support for dynamic rule generation, multiple rule sources (CIDR blocks, source security groups, prefix lists), egress and ingress rule management, and integration with Terraform's computed values. The module handles the complexity of AWS security group quotas, rule prioritization, and stateful connection tracking while providing a simple, declarative interface. With support for Terraform versions from 0.11 to 1.0+, the module enables teams to standardize security group configurations across diverse infrastructure deployments while maintaining backward compatibility.

## Key Features

- **50+ Predefined Service Modules**: Pre-configured security groups for common services like HTTP, SSH, MySQL, PostgreSQL, Redis, Kafka, Elasticsearch
- **Custom Rule Configuration**: Flexible main module for creating security groups with custom ingress and egress rules
- **IPv4 and IPv6 Support**: CIDR block configuration for both IPv4 and IPv6 addresses
- **Security Group References**: Allow traffic from other security groups for service-to-service communication
- **VPC Endpoint Prefix Lists**: Support for managed prefix lists from VPC endpoints
- **Conditional Creation**: Create or skip security group creation based on variables
- **Named Rules**: Pre-defined named rules for common protocols and ports (ssh, http-80, https-443, mysql, etc.)
- **Rule Groups**: Combine multiple named rules in single configuration
- **Computed Values Support**: Handle dynamic and computed values in security group rules
- **Multiple Rule Sources**: Configure rules from CIDR blocks, source security groups, self-references, and prefix lists
- **Ingress and Egress Rules**: Complete control over inbound and outbound traffic
- **Rule Descriptions**: Add descriptive comments to rules for documentation
- **Port Range Support**: Specify single ports or port ranges in rules
- **Protocol Flexibility**: Support for TCP, UDP, ICMP, and all protocols (-1)
- **Self-Reference Rules**: Enable communication within the same security group
- **Comprehensive Tagging**: Apply tags to security groups for organization and cost allocation
- **Revoke Rules on Delete**: Automatically revoke rules when security group is deleted
- **Number of Rules Configuration**: Control rule creation count for dynamic scenarios
- **Terraform Version Compatibility**: Support for Terraform 0.11, 0.12, 0.13, and 1.0+

## Main Use Cases

1. **Web Application Security**: Configure HTTP/HTTPS access for web servers and load balancers
2. **Database Access Control**: Restrict database access to specific application security groups
3. **SSH Bastion Hosts**: Secure SSH access from specific IP ranges or VPN endpoints
4. **Microservices Communication**: Enable service-to-service communication using security group references
5. **API Gateway Protection**: Control access to API endpoints with IP whitelisting
6. **Container Orchestration**: Configure security groups for Kubernetes, Docker Swarm, or ECS clusters
7. **Monitoring Infrastructure**: Secure access to Prometheus, Grafana, and logging systems
8. **VPN and Remote Access**: Configure OpenVPN, RDP, or WinRM security groups
9. **Message Queue Security**: Secure Kafka, RabbitMQ, and messaging infrastructure
10. **Compliance Requirements**: Implement network segmentation for regulatory compliance

## Requirements

### Terraform Version
- **Terraform**: >= 1.0 (for latest versions)
- **Terraform 0.13-0.15**: Use v4.5.0 or newer
- **Terraform 0.12**: Use v3.* to v4.4.0
- **Terraform 0.11**: Use v2.*

### Provider Requirements
- **AWS Provider**: >= 3.29

## Modules Overview

This security group module includes 50+ predefined service modules and a main module for custom configurations. Below are the major categories:

### Web and Application Services
- **http-80**: HTTP access on port 80
- **http-8080**: HTTP access on port 8080
- **https-443**: HTTPS access on port 443
- **https-8443**: HTTPS access on port 8443

### Database Services
- **mysql**: MySQL/Aurora database access (port 3306)
- **postgresql**: PostgreSQL database access (port 5432)
- **mongodb**: MongoDB database access (port 27017)
- **redis**: Redis cache access (port 6379)
- **mssql**: Microsoft SQL Server access (port 1433)
- **oracle-db**: Oracle database access (port 1521)
- **redshift**: AWS Redshift access (port 5439)

### Remote Access
- **ssh**: SSH access (port 22)
- **rdp**: Remote Desktop Protocol (port 3389)
- **winrm**: Windows Remote Management (port 5985-5986)

### Messaging and Queue Services
- **kafka**: Apache Kafka (port 9092)
- **rabbitmq**: RabbitMQ messaging (port 5672, 15672)
- **activemq**: Apache ActiveMQ (port 8161, 61616)

### Monitoring and Logging
- **prometheus**: Prometheus monitoring (port 9090)
- **grafana**: Grafana dashboards (port 3000)
- **elasticsearch**: Elasticsearch (port 9200, 9300)
- **kibana**: Kibana (port 5601)
- **zabbix**: Zabbix monitoring (port 10050-10051)

### Distributed Systems
- **consul**: HashiCorp Consul (port 8300-8302, 8500, 8600)
- **vault**: HashiCorp Vault (port 8200)
- **etcd**: etcd key-value store (port 2379-2380)
- **zookeeper**: Apache ZooKeeper (port 2181, 2888, 3888)
- **kubernetes-api**: Kubernetes API server (port 6443)

### Other Services
- **openvpn**: OpenVPN access (port 1194)
- **ldap**: LDAP directory (port 389)
- **ldaps**: LDAPS secure (port 636)
- **ntp**: Network Time Protocol (port 123)
- **smtp**: Email SMTP (port 25)
- **smtps**: Email SMTPS (port 465)

## Main Module: Custom Security Groups

### Description

The main security group module provides complete flexibility for creating custom security groups with tailored ingress and egress rules. This module is ideal when predefined service modules don't meet specific requirements or when creating security groups for custom applications with non-standard ports. It supports all AWS security group features including multiple rule sources, computed values, and complex rule configurations.

### Key Features

- Complete control over all ingress and egress rules
- Support for multiple rule configuration methods
- Dynamic rule generation with computed values
- Integration with all AWS security group features
- Flexible rule descriptions and documentation
- Conditional security group creation

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of security group |
| `description` | `string` | `"Security Group managed by Terraform"` | Security group description |
| `vpc_id` | `string` | `null` | VPC ID where security group is created |
| `create` | `bool` | `true` | Whether to create security group |
| `ingress_rules` | `list(string)` | `[]` | List of predefined ingress rule names |
| `ingress_with_cidr_blocks` | `list(map(string))` | `[]` | Ingress rules with CIDR blocks |
| `ingress_with_source_security_group_id` | `list(map(string))` | `[]` | Ingress rules with source security group |
| `egress_rules` | `list(string)` | `[]` | List of predefined egress rule names |
| `egress_with_cidr_blocks` | `list(map(string))` | `[]` | Egress rules with CIDR blocks |
| `tags` | `map(string)` | `{}` | Tags to apply to security group |

### Main Outputs

| Output | Description |
|--------|-------------|
| `security_group_id` | ID of the security group |
| `security_group_arn` | ARN of the security group |
| `security_group_name` | Name of the security group |
| `security_group_vpc_id` | VPC ID of the security group |

### Usage Examples

#### Example 1: Web Application Security Group

```hcl
module "web_server_sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "web-server"
  description = "Security group for web servers"
  vpc_id      = "vpc-12345678"

  # Ingress rules using predefined names
  ingress_rules = ["http-80-tcp", "https-443-tcp", "ssh-tcp"]

  # Allow HTTP from specific CIDR
  ingress_with_cidr_blocks = [
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      description = "HTTP from VPC"
      cidr_blocks = "10.0.0.0/16"
    }
  ]

  # Egress to all
  egress_rules = ["all-all"]

  tags = {
    Environment = "production"
    Application = "web"
  }
}
```

#### Example 2: Application with Multiple Custom Ports

```hcl
module "application_sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "application-server"
  description = "Security group for custom application"
  vpc_id      = module.vpc.vpc_id

  # Custom port ranges
  ingress_with_cidr_blocks = [
    {
      from_port   = 8080
      to_port     = 8090
      protocol    = "tcp"
      description = "Application API ports"
      cidr_blocks = "10.0.0.0/16"
    },
    {
      from_port   = 9000
      to_port     = 9000
      protocol    = "tcp"
      description = "Monitoring port"
      cidr_blocks = "10.0.100.0/24"
    }
  ]

  # Allow outbound to specific destinations
  egress_with_cidr_blocks = [
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      description = "HTTPS to internet"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 3306
      to_port     = 3306
      protocol    = "tcp"
      description = "MySQL to RDS subnet"
      cidr_blocks = "10.0.20.0/24"
    }
  ]

  tags = {
    Terraform   = "true"
    Environment = "staging"
  }
}
```

#### Example 3: Microservices with Security Group References

```hcl
# Frontend security group
module "frontend_sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "frontend"
  description = "Frontend service security group"
  vpc_id      = module.vpc.vpc_id

  # Allow HTTP/HTTPS from ALB
  ingress_with_source_security_group_id = [
    {
      from_port                = 8080
      to_port                  = 8080
      protocol                 = "tcp"
      description              = "HTTP from ALB"
      source_security_group_id = module.alb_sg.security_group_id
    }
  ]

  # Allow outbound to backend
  egress_with_source_security_group_id = [
    {
      from_port                = 8081
      to_port                  = 8081
      protocol                 = "tcp"
      description              = "Backend API"
      source_security_group_id = module.backend_sg.security_group_id
    }
  ]
}

# Backend security group
module "backend_sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "backend"
  description = "Backend service security group"
  vpc_id      = module.vpc.vpc_id

  # Allow from frontend
  ingress_with_source_security_group_id = [
    {
      from_port                = 8081
      to_port                  = 8081
      protocol                 = "tcp"
      description              = "API from frontend"
      source_security_group_id = module.frontend_sg.security_group_id
    }
  ]

  # Allow outbound to database
  egress_with_source_security_group_id = [
    {
      from_port                = 5432
      to_port                  = 5432
      protocol                 = "tcp"
      description              = "PostgreSQL database"
      source_security_group_id = module.database_sg.security_group_id
    }
  ]
}
```

#### Example 4: Using Predefined Service Modules

```hcl
# MySQL database security group
module "mysql_sg" {
  source = "terraform-aws-modules/security-group/aws//modules/mysql"

  name        = "mysql-db"
  description = "MySQL database security group"
  vpc_id      = module.vpc.vpc_id

  # Allow from application servers
  ingress_cidr_blocks = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]

  tags = {
    Database = "MySQL"
  }
}

# SSH bastion security group
module "ssh_bastion_sg" {
  source = "terraform-aws-modules/security-group/aws//modules/ssh"

  name        = "ssh-bastion"
  description = "SSH bastion host"
  vpc_id      = module.vpc.vpc_id

  # Allow SSH from office IP
  ingress_cidr_blocks = ["203.0.113.0/24"]

  tags = {
    Purpose = "Bastion"
  }
}

# Redis cache security group
module "redis_sg" {
  source = "terraform-aws-modules/security-group/aws//modules/redis"

  name        = "redis-cache"
  description = "Redis ElastiCache"
  vpc_id      = module.vpc.vpc_id

  # Allow from application security group
  computed_ingress_with_source_security_group_id = [
    {
      rule                     = "redis-tcp"
      source_security_group_id = module.application_sg.security_group_id
    }
  ]

  number_of_computed_ingress_with_source_security_group_id = 1
}
```

#### Example 5: IPv6 and Prefix List Support

```hcl
module "ipv6_sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "ipv6-enabled"
  description = "Security group with IPv6 support"
  vpc_id      = module.vpc.vpc_id

  # IPv4 ingress
  ingress_with_cidr_blocks = [
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      description = "HTTPS IPv4"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  # IPv6 ingress
  ingress_with_ipv6_cidr_blocks = [
    {
      from_port        = 443
      to_port          = 443
      protocol         = "tcp"
      description      = "HTTPS IPv6"
      ipv6_cidr_blocks = "::/0"
    }
  ]

  # VPC endpoint prefix list
  ingress_prefix_list_ids = [
    {
      from_port       = 443
      to_port         = 443
      protocol        = "tcp"
      description     = "S3 VPC Endpoint"
      prefix_list_ids = data.aws_prefix_list.s3.id
    }
  ]

  egress_rules = ["all-all"]
}
```

#### Example 6: Conditional Creation

```hcl
module "conditional_sg" {
  source = "terraform-aws-modules/security-group/aws"

  # Only create in production
  create = var.environment == "production"

  name        = "conditional-sg"
  description = "Created only in production"
  vpc_id      = module.vpc.vpc_id

  ingress_rules       = ["https-443-tcp"]
  ingress_cidr_blocks = ["0.0.0.0/0"]

  egress_rules = ["all-all"]

  tags = {
    Environment = var.environment
  }
}
```

## Best Practices

### Security Group Design

1. **Use Principle of Least Privilege**: Only open ports and protocols that are absolutely necessary for application functionality.
2. **Create Purpose-Specific Security Groups**: Design security groups for specific functions (web, app, database) rather than creating monolithic groups.
3. **Use Descriptive Names**: Apply clear, descriptive names and descriptions to security groups for easy identification.
4. **Leverage Predefined Modules**: Use predefined service modules (http-80, mysql, etc.) for common services to reduce errors.
5. **Document with Descriptions**: Add meaningful descriptions to all rules explaining their purpose.
6. **Avoid 0.0.0.0/0 for Ingress**: Restrict ingress CIDR blocks to known IP ranges; use 0.0.0.0/0 sparingly and only when necessary.
7. **Use Security Group References**: Reference other security groups instead of CIDR blocks for service-to-service communication.
8. **Plan for IPv6**: If using IPv6, configure both IPv4 and IPv6 rules to maintain consistent security posture.

### Rule Configuration

1. **Specify Minimum Port Ranges**: Use specific port numbers instead of broad ranges to minimize attack surface.
2. **Use Named Rules**: Leverage predefined named rules (ssh, http-80-tcp) for consistency and reduced configuration errors.
3. **Separate Concerns**: Create distinct ingress and egress rules rather than using "all-all" unless truly required.
4. **Add Rule Comments**: Use description fields in all rules for documentation and compliance auditing.
5. **Review Egress Rules**: Don't default to "all-all" egress; restrict outbound traffic to required destinations.
6. **Limit SSH/RDP Access**: Restrict administrative access (SSH, RDP) to specific IP ranges or VPN endpoints.
7. **Use Stateful Nature**: Remember that security groups are stateful; return traffic is automatically allowed.
8. **Avoid Overlapping Rules**: Ensure rules don't conflict or overlap unnecessarily; AWS processes all matching rules.

### Infrastructure as Code

1. **Version Pin Modules**: Use specific module versions in production (e.g., `version = "~> 5.0"`) to prevent unexpected changes.
2. **Use Variables for CIDRs**: Define CIDR blocks as variables for easier updates and environment-specific configurations.
3. **Implement Tagging Strategy**: Apply consistent tags including Environment, Owner, Application, and CostCenter.
4. **Handle Computed Values**: Use `computed_*` input variables when working with dynamic or computed values.
5. **Test Before Production**: Validate security group changes in development/staging before applying to production.
6. **Use Terraform Workspaces**: Separate security group configurations by environment using workspaces or separate state files.
7. **Enable Conditional Creation**: Use `create = false` for environment-specific security groups.
8. **Document Dependencies**: Clearly document security group dependencies and references in code comments.

### Security and Compliance

1. **Enable VPC Flow Logs**: Use VPC Flow Logs to monitor traffic patterns and detect anomalous access.
2. **Regular Security Audits**: Periodically review security groups to remove unnecessary rules and unused groups.
3. **Implement Defense in Depth**: Combine security groups with NACLs, WAF, and other security controls.
4. **Use AWS Config**: Enable AWS Config rules to detect non-compliant security group configurations.
5. **Restrict IAM Permissions**: Limit who can create and modify security groups using IAM policies.
6. **Monitor Changes**: Set up CloudWatch alarms for security group modifications.
7. **Follow Compliance Standards**: Align security group configurations with frameworks (CIS, PCI-DSS, HIPAA).
8. **Avoid Default Security Groups**: Don't use VPC default security groups; create explicit security groups instead.

### Operational Excellence

1. **Name with Purpose**: Use naming conventions that indicate purpose, environment, and application (e.g., "prod-web-alb-sg").
2. **Maintain Documentation**: Document security group architecture, dependencies, and change history.
3. **Use Security Group Chaining**: Create layered security groups (ALB → Web → App → Database) for defense in depth.
4. **Monitor Unused Rules**: Identify and remove rules that aren't actively used to reduce complexity.
5. **Test Connectivity**: Validate security group rules using test instances before deploying applications.
6. **Plan for Scaling**: Consider AWS quotas (rules per group, groups per network interface) when designing architecture.
7. **Use Resource Tags**: Tag security groups for cost allocation, automation, and organizational purposes.
8. **Implement Change Control**: Require approval and peer review for production security group changes.

### High Availability and Resilience

1. **Multi-AZ Considerations**: Ensure security groups work across all availability zones in your VPC.
2. **Avoid Single Points of Failure**: Don't create dependencies where a single security group controls critical access paths.
3. **Plan for Disaster Recovery**: Include security group configurations in disaster recovery runbooks.
4. **Test Failover Scenarios**: Verify security groups function correctly during AZ or region failover.
5. **Document Critical Groups**: Maintain detailed documentation of security groups essential for business operations.

### Cost Optimization

1. **Consolidate Similar Rules**: Combine similar security groups to reduce management overhead.
2. **Remove Unused Security Groups**: Regularly audit and delete unused security groups to maintain cleanliness.
3. **Use Managed Prefix Lists**: Leverage managed prefix lists for AWS services to simplify updates.
4. **Optimize Rule Count**: Minimize the number of rules while maintaining security to stay within quotas.

### Network Architecture

1. **Segment by Tier**: Create separate security groups for each application tier (web, application, database).
2. **Use Private Subnets**: Place application and database tiers in private subnets with restrictive security groups.
3. **Control Egress Traffic**: Implement egress filtering to prevent data exfiltration and unauthorized outbound connections.
4. **Plan CIDR Blocks**: Coordinate security group CIDR blocks with VPC and subnet design.
5. **Use VPC Endpoints**: Combine security groups with VPC endpoints for private AWS service access.
6. **Implement Bastion Patterns**: Create dedicated bastion security groups for administrative access.
7. **Consider Peering**: Account for VPC peering when designing security group rules across VPCs.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-security-group
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-security-group/tree/master/examples
- **AWS Security Groups Documentation**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
- **Security Group Rules**: https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html
- **VPC Security Best Practices**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html
- **AWS Well-Architected Security Pillar**: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html
- **Security Group Limits**: https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html#vpc-limits-security-groups
- **VPC Flow Logs**: https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html
- **AWS Config for Security Groups**: https://docs.aws.amazon.com/config/latest/developerguide/security-group-rules.html
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
- **AWS Service Endpoints**: https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Choose Appropriate Module**: Use predefined service modules (http-80, mysql) for standard services, main module for custom configurations
2. **Restrict CIDR Blocks**: Never default to 0.0.0.0/0 for ingress unless explicitly required for public services
3. **Use Security Group References**: Prefer source_security_group_id over CIDR blocks for inter-service communication
4. **Tag Comprehensively**: Include Environment, Application, Owner, Purpose tags for all security groups
5. **Document All Rules**: Add descriptions to every rule explaining its purpose and justification
6. **Plan Port Ranges**: Use specific ports instead of broad ranges; know exact port requirements
7. **Separate Ingress/Egress**: Configure both ingress and egress rules explicitly; avoid "all-all" patterns
8. **Handle Computed Values**: Use computed_* variables when dealing with dynamic or unknown values at plan time
9. **Test Connectivity**: Validate security group rules before deploying applications
10. **Monitor Changes**: Enable CloudWatch Events or Config rules to track security group modifications
11. **Review Regularly**: Audit security groups quarterly to remove unused rules and groups
12. **Use Conditional Creation**: Leverage create = false for environment-specific deployments
13. **Version Pin**: Use specific module versions in production to prevent unexpected changes
14. **Follow Least Privilege**: Only open ports absolutely required for application functionality
15. **Enable Flow Logs**: Use VPC Flow Logs to monitor traffic and detect anomalies
16. **Avoid Default Groups**: Always create explicit security groups; don't rely on VPC defaults
17. **Plan for Scale**: Consider AWS quotas when designing security group architecture
18. **Implement Defense in Depth**: Combine security groups with NACLs and other security layers
