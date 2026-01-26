# Terraform AWS Security Group Module

## Module Information

- **Module Name**: `security-group`
- **Source**: `terraform-aws-modules/security-group/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-security-group
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest
- **Latest Version**: 5.3.1
- **Purpose**: Creates AWS VPC security groups with 157 predefined rules for 50+ services and flexible custom rule configuration
- **Service**: AWS VPC Security Groups
- **Category**: Networking, Security
- **Keywords**: security-group, vpc, firewall, ingress, egress, cidr-blocks, source-security-group, tcp, udp, predefined-rules, network-security
- **Use For**: Web server access control, database security, SSH bastion hosts, microservices isolation, load balancer security, container networking, VPN endpoint security, multi-tier application segmentation

## Description

This Terraform module manages AWS VPC security groups, which act as virtual firewalls controlling inbound and outbound traffic for EC2 instances, RDS databases, load balancers, and other VPC resources. The module provides two approaches: 57 predefined service submodules for common services (HTTP, MySQL, Redis, Kafka, etc.) with sensible defaults, and a flexible main module for custom security group configurations.

The module supports all AWS security group features including IPv4/IPv6 CIDR blocks, VPC endpoint prefix lists, security group references for service-to-service communication, self-referencing rules for cluster communication, and computed values for dynamic configurations. It includes 157 predefined named rules covering common protocols and ports, reducing configuration errors and ensuring consistency across environments.

## Key Features

- **57 Predefined Service Modules**: Ready-to-use submodules for HTTP, SSH, MySQL, PostgreSQL, Redis, Kafka, Elasticsearch, and more
- **157 Named Rules**: Predefined rules like `https-443-tcp`, `mysql-tcp`, `redis-tcp` for consistent port configurations
- **IPv4 and IPv6 Support**: Full CIDR block configuration for both address families
- **Security Group References**: Allow traffic from other security groups using `source_security_group_id`
- **Self-Referencing Rules**: Enable communication within the same security group for clusters
- **VPC Endpoint Prefix Lists**: Support for managed prefix lists from AWS services
- **Conditional Creation**: Create new security groups or manage rules for existing ones
- **Computed Values Support**: Handle dynamic values with `computed_*` variables
- **Flexible Rule Definition**: Use named rules, custom port ranges, or both

## Main Use Cases

1. **Web Application Security**: Configure HTTP/HTTPS access for web servers and ALBs
2. **Database Access Control**: Restrict database access to specific application security groups
3. **SSH Bastion Hosts**: Secure SSH access from specific IP ranges or VPN endpoints
4. **Microservices Communication**: Enable service-to-service communication using security group references
5. **Container Orchestration**: Configure security groups for ECS, EKS, or Docker Swarm clusters
6. **Monitoring Infrastructure**: Secure access to Prometheus, Grafana, and logging systems
7. **Message Queue Security**: Secure Kafka, RabbitMQ, and messaging infrastructure

## Predefined Service Modules

### Web Services
| Module | Port | Registry Link |
|--------|------|---------------|
| `http-80` | 80 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/http-80) |
| `http-8080` | 8080 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/http-8080) |
| `https-443` | 443 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/https-443) |
| `https-8443` | 8443 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/https-8443) |

### Databases
| Module | Port | Registry Link |
|--------|------|---------------|
| `mysql` | 3306 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/mysql) |
| `postgresql` | 5432 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/postgresql) |
| `mongodb` | 27017 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/mongodb) |
| `redis` | 6379 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/redis) |
| `mssql` | 1433 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/mssql) |
| `oracle-db` | 1521 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/oracle-db) |
| `redshift` | 5439 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/redshift) |
| `cassandra` | 9042 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/cassandra) |

### Remote Access
| Module | Port | Registry Link |
|--------|------|---------------|
| `ssh` | 22 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/ssh) |
| `rdp` | 3389 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/rdp) |
| `winrm` | 5985-5986 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/winrm) |
| `openvpn` | 1194 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/openvpn) |

### Messaging & Streaming
| Module | Port | Registry Link |
|--------|------|---------------|
| `kafka` | 9092 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/kafka) |
| `rabbitmq` | 5672 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/rabbitmq) |
| `activemq` | 61616 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/activemq) |

### Monitoring & Logging
| Module | Port | Registry Link |
|--------|------|---------------|
| `prometheus` | 9090 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/prometheus) |
| `grafana` | 3000 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/grafana) |
| `elasticsearch` | 9200 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/elasticsearch) |
| `kibana` | 5601 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/kibana) |

### Distributed Systems
| Module | Port | Registry Link |
|--------|------|---------------|
| `consul` | 8300-8600 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/consul) |
| `vault` | 8200 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/vault) |
| `etcd` | 2379-2380 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/etcd) |
| `zookeeper` | 2181 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/zookeeper) |
| `kubernetes-api` | 6443 | [Link](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/kubernetes-api) |

### Other Services
`dns`, `ldap`, `ldaps`, `ntp`, `smtp`, `smtps`, `memcached`, `minio`, `nfs`, `splunk`, `logstash`, `docker-swarm`, `nomad`, `puppet`, `solr`, `squid`, `storm`, `wazuh`, `zipkin`

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | required | Name of security group |
| `vpc_id` | `string` | required | VPC ID where security group is created |
| `description` | `string` | `"Security Group managed by Terraform"` | Security group description |
| `create` | `bool` | `true` | Whether to create security group and rules |
| `create_sg` | `bool` | `true` | Whether to create security group (false to manage existing) |
| `security_group_id` | `string` | `null` | ID of existing security group to manage |
| `use_name_prefix` | `bool` | `true` | Use name_prefix instead of fixed name |
| `ingress_rules` | `list(string)` | `[]` | List of predefined ingress rule names |
| `ingress_cidr_blocks` | `list(string)` | `[]` | IPv4 CIDR blocks for ingress rules |
| `ingress_with_cidr_blocks` | `list(map(string))` | `[]` | Custom ingress rules with CIDR blocks |
| `ingress_with_source_security_group_id` | `list(map(string))` | `[]` | Ingress rules with source security group |
| `ingress_with_self` | `list(map(string))` | `[]` | Self-referencing ingress rules |
| `egress_rules` | `list(string)` | `[]` | List of predefined egress rule names |
| `egress_cidr_blocks` | `list(string)` | `["0.0.0.0/0"]` | IPv4 CIDR blocks for egress rules |
| `egress_with_cidr_blocks` | `list(map(string))` | `[]` | Custom egress rules with CIDR blocks |
| `tags` | `map(string)` | `{}` | Tags to apply to security group |
| `revoke_rules_on_delete` | `bool` | `false` | Revoke rules before security group deletion |

## Main Outputs

| Output | Description |
|--------|-------------|
| `security_group_id` | ID of the security group |
| `security_group_arn` | ARN of the security group |
| `security_group_name` | Name of the security group |
| `security_group_vpc_id` | VPC ID of the security group |
| `security_group_owner_id` | Owner ID (AWS account) |

## Usage Examples

### Example 1: Web Server with Predefined Rules

```hcl
module "web_server_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = "web-server"
  description = "Security group for web servers"
  vpc_id      = module.vpc.vpc_id

  # Use predefined rules
  ingress_rules       = ["http-80-tcp", "https-443-tcp"]
  ingress_cidr_blocks = ["0.0.0.0/0"]

  egress_rules = ["all-all"]

  tags = {
    Environment = "production"
  }
}
```

### Example 2: Using Predefined Service Module

```hcl
module "mysql_sg" {
  source  = "terraform-aws-modules/security-group/aws//modules/mysql"
  version = "~> 5.0"

  name        = "mysql-db"
  description = "MySQL database security group"
  vpc_id      = module.vpc.vpc_id

  # Allow from application subnets
  ingress_cidr_blocks = ["10.0.1.0/24", "10.0.2.0/24"]

  tags = {
    Database = "MySQL"
  }
}
```

### Example 3: Custom Ports with CIDR Blocks

```hcl
module "app_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = "application"
  description = "Application security group"
  vpc_id      = module.vpc.vpc_id

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

  egress_with_cidr_blocks = [
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      description = "HTTPS outbound"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
}
```

### Example 4: Security Group References (Microservices)

```hcl
# ALB security group
module "alb_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name   = "alb"
  vpc_id = module.vpc.vpc_id

  ingress_rules       = ["http-80-tcp", "https-443-tcp"]
  ingress_cidr_blocks = ["0.0.0.0/0"]
  egress_rules        = ["all-all"]
}

# Application security group - allow from ALB only
module "app_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name   = "application"
  vpc_id = module.vpc.vpc_id

  ingress_with_source_security_group_id = [
    {
      from_port                = 8080
      to_port                  = 8080
      protocol                 = "tcp"
      description              = "HTTP from ALB"
      source_security_group_id = module.alb_sg.security_group_id
    }
  ]

  egress_rules = ["all-all"]
}

# Database security group - allow from app only
module "db_sg" {
  source  = "terraform-aws-modules/security-group/aws//modules/postgresql"
  version = "~> 5.0"

  name   = "database"
  vpc_id = module.vpc.vpc_id

  ingress_with_source_security_group_id = [
    {
      rule                     = "postgresql-tcp"
      source_security_group_id = module.app_sg.security_group_id
    }
  ]
}
```

### Example 5: Self-Referencing Rules (Cluster Communication)

```hcl
module "cluster_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = "cluster"
  description = "Cluster internal communication"
  vpc_id      = module.vpc.vpc_id

  # Allow all traffic between cluster members
  ingress_with_self = [
    {
      from_port   = 0
      to_port     = 65535
      protocol    = "tcp"
      description = "Cluster internal TCP"
    },
    {
      from_port   = 0
      to_port     = 65535
      protocol    = "udp"
      description = "Cluster internal UDP"
    }
  ]

  egress_rules = ["all-all"]
}
```

### Example 6: Managing Existing Security Group

```hcl
module "existing_sg_rules" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  create_sg         = false
  security_group_id = "sg-0123456789abcdef0"

  ingress_rules       = ["ssh-tcp", "https-443-tcp"]
  ingress_cidr_blocks = ["10.0.0.0/8"]

  egress_rules = ["all-all"]
}
```

### Example 7: SSH Bastion Host

```hcl
module "bastion_sg" {
  source  = "terraform-aws-modules/security-group/aws//modules/ssh"
  version = "~> 5.0"

  name        = "bastion"
  description = "SSH bastion host"
  vpc_id      = module.vpc.vpc_id

  # Allow SSH from office IP range only
  ingress_cidr_blocks = ["203.0.113.0/24"]

  tags = {
    Purpose = "Bastion"
  }
}
```

## Common Named Rules Reference

| Rule Name | Protocol | Port | Description |
|-----------|----------|------|-------------|
| `all-all` | -1 | all | Allow all traffic |
| `ssh-tcp` | tcp | 22 | SSH |
| `http-80-tcp` | tcp | 80 | HTTP |
| `https-443-tcp` | tcp | 443 | HTTPS |
| `mysql-tcp` | tcp | 3306 | MySQL/Aurora |
| `postgresql-tcp` | tcp | 5432 | PostgreSQL |
| `redis-tcp` | tcp | 6379 | Redis |
| `mongodb-27017-tcp` | tcp | 27017 | MongoDB |
| `kafka-broker-tcp` | tcp | 9092 | Kafka broker |
| `elasticsearch-rest-tcp` | tcp | 9200 | Elasticsearch |
| `rdp-tcp` | tcp | 3389 | RDP |
| `dns-tcp` / `dns-udp` | tcp/udp | 53 | DNS |
| `nfs-tcp` | tcp | 2049 | NFS |

Full list of 157 rules available in [rules.tf](https://github.com/terraform-aws-modules/terraform-aws-security-group/blob/master/rules.tf).

## Best Practices

### Security Design

1. **Least Privilege**: Only open ports that are necessary for application functionality
2. **Use Security Group References**: Prefer `source_security_group_id` over CIDR blocks for inter-service communication
3. **Avoid 0.0.0.0/0 Ingress**: Restrict ingress to known IP ranges; use only for public-facing load balancers
4. **Restrict Egress**: Don't default to `all-all` egress; limit outbound to required destinations
5. **Use Predefined Modules**: Leverage service modules (mysql, redis, etc.) for consistent port configurations

### Rule Configuration

1. **Add Descriptions**: Document every rule with meaningful descriptions for auditing
2. **Specific Port Ranges**: Use exact ports instead of broad ranges to minimize attack surface
3. **Layer Security**: Create separate security groups per tier (ALB → App → DB)
4. **Self-Referencing for Clusters**: Use `ingress_with_self` for cluster internal communication

### Operations

1. **Version Pin**: Use specific module versions (`version = "~> 5.0"`) in production
2. **Tagging**: Apply Environment, Owner, Application tags for management
3. **Regular Audits**: Review security groups quarterly to remove unused rules
4. **Test Changes**: Validate rules in staging before production deployment

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-security-group
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest
- **Examples**: https://github.com/terraform-aws-modules/terraform-aws-security-group/tree/master/examples
- **AWS Security Groups Docs**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
- **Security Group Rules**: https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html
- **VPC Security Best Practices**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html

## Notes for AI Agents

When using this module in Terraform code generation:

1. **Choose Right Approach**: Use predefined service modules (mysql, redis) for standard services; main module for custom configurations
2. **Never Default 0.0.0.0/0**: Always ask for specific CIDR ranges for ingress unless explicitly required for public services
3. **Prefer Security Group References**: Use `source_security_group_id` for inter-service communication instead of CIDR blocks
4. **Document All Rules**: Add `description` to every custom rule explaining its purpose
5. **Use Named Rules**: Leverage predefined rules (`https-443-tcp`, `mysql-tcp`) for common protocols
6. **Tag Comprehensively**: Include Environment, Application, Owner tags
7. **Version Pin**: Always specify `version = "~> 5.0"` in module blocks
8. **Layer Security Groups**: Create ALB → Application → Database security group chains
9. **Self-Reference for Clusters**: Use `ingress_with_self` for internal cluster communication
10. **Validate Before Apply**: Check security group rules don't conflict with existing configurations
