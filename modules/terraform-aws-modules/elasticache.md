# Terraform AWS ElastiCache Module

## Module Information

- **Module Name**: `elasticache`
- **Source**: `terraform-aws-modules/elasticache/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-elasticache
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/elasticache/aws/latest
- **Latest Version**: 1.10.3
- **Purpose**: Terraform module that creates and manages AWS ElastiCache resources including Redis, Memcached, and Valkey clusters with support for replication groups, cluster mode, global replication, and serverless caches
- **Service**: AWS ElastiCache (Managed In-Memory Caching Service)
- **Category**: Database, Caching, Performance Optimization
- **Keywords**: elasticache, redis, memcached, valkey, cache, in-memory, replication-group, cluster-mode, serverless-cache, multi-az, automatic-failover, encryption, session-store, low-latency, sharding
- **Use For**: Session caching and management, database query result caching, application performance acceleration, real-time analytics and leaderboards, pub/sub messaging systems, gaming session state storage, API response caching, recommendation engine data storage, user profile caching, rate limiting and throttling, distributed locks and semaphores, real-time bidding platforms

## Description

This Terraform module provides comprehensive management of AWS ElastiCache resources, supporting multiple cache engines including Redis, Memcached, and Valkey (an open-source Redis alternative). The module enables creation and configuration of various ElastiCache deployment types including standalone clusters, replication groups with automatic failover, cluster mode for horizontal scaling, global replication groups for cross-region deployments, and serverless caches for on-demand scaling. It manages all associated resources such as security groups, subnet groups, parameter groups, user groups, and CloudWatch log delivery configurations.

AWS ElastiCache is a fully managed in-memory caching service that delivers sub-millisecond latency and high throughput for data-intensive applications. It eliminates the complexity of deploying, operating, and scaling distributed cache environments while providing features like automatic failover, backup and restore, and software patching. The service is ideal for reducing database load by caching frequently accessed data, storing ephemeral session data, implementing real-time leaderboards and analytics, and enabling high-performance pub/sub messaging patterns.

The module offers extensive configuration flexibility with support for encryption in transit and at rest, multi-AZ deployments for high availability, custom parameter groups for fine-tuning cache behavior, and comprehensive networking controls through VPC integration. It includes two specialized submodules for serverless cache deployments and user/group management, providing a complete solution for all ElastiCache deployment scenarios. The module follows AWS best practices for security, performance, and operational excellence while maintaining simplicity through sensible defaults and clear configuration options.

## Key Features

- **Multiple Cache Engines**: Support for Redis, Memcached, and Valkey cache engines with version-specific configurations
- **Seven Deployment Types**: Memcached cluster, Redis cluster, Redis cluster mode, Redis replication group, Redis global replication group, Valkey replication group, and serverless cache
- **Serverless Cache Support**: Automatic scaling with usage-based limits for storage and compute via dedicated submodule
- **User and Group Management**: Fine-grained access control through user authentication and authorization with dedicated submodule
- **Replication Groups**: Multi-node Redis deployments with automatic failover and read replica support
- **Cluster Mode**: Horizontal scaling with data sharding across multiple nodes for increased performance
- **Global Replication**: Cross-region replication groups for disaster recovery and low-latency global access
- **Multi-AZ Deployment**: Automatic failover support across multiple Availability Zones for high availability
- **Encryption Support**: Transit encryption (TLS) and at-rest encryption with AWS KMS integration
- **Security Group Management**: Automatic creation and configuration of VPC security groups with customizable rules
- **Subnet Group Configuration**: VPC subnet group creation for network isolation and placement control
- **Parameter Group Customization**: Custom cache engine parameters for performance tuning and behavior modification
- **Snapshot Management**: Automated and manual snapshot creation for backup and restore operations
- **CloudWatch Integration**: Log delivery to CloudWatch for slow logs and engine logs with configurable retention
- **Authentication Options**: Support for AUTH tokens, user-based authentication, and IAM authentication
- **Automatic Failover**: Configurable automatic promotion of read replicas in case of primary node failure
- **Maintenance Windows**: Scheduled maintenance window configuration for updates and patching
- **Notification Support**: SNS topic integration for cache events and notifications
- **Tag Propagation**: Comprehensive tagging support across all created resources
- **Node Type Flexibility**: Support for all ElastiCache instance types from micro to large memory-optimized instances
- **Preferred Availability Zones**: Control over cache node placement in specific Availability Zones
- **Auto Minor Version Upgrade**: Configurable automatic minor version upgrades during maintenance windows
- **Data Tiering**: Support for data tiering to optimize costs (Redis r6gd node types)
- **Log Delivery**: Engine log and slow log delivery to CloudWatch Logs or Kinesis Data Firehose
- **Network Mode**: Support for IPv4 and IPv6 network configurations

## Main Use Cases

1. **Database Query Result Caching**: Reduce database load by caching frequently accessed query results
2. **Session State Management**: Store and retrieve user session data for web applications with high concurrency
3. **Real-time Leaderboards and Analytics**: Maintain sorted sets for gaming scores, rankings, and live statistics
4. **API Response Caching**: Cache API responses to improve response times and reduce backend processing
5. **Pub/Sub Messaging**: Implement real-time messaging and notification systems using Redis pub/sub
6. **Rate Limiting and Throttling**: Track and enforce API rate limits and request throttling
7. **Distributed Locking**: Coordinate access to shared resources across distributed application instances
8. **Content Delivery Acceleration**: Cache static and dynamic content for faster delivery to end users
9. **Recommendation Engine Storage**: Store user preferences and recommendation data for quick retrieval
10. **Application Performance Optimization**: Reduce latency for data-intensive operations requiring sub-millisecond response times

## Submodules

### 1. serverless-cache

- **Purpose**: Creates AWS ElastiCache serverless cache resources with automatic scaling
- **Source**: `terraform-aws-modules/elasticache/aws//modules/serverless-cache`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/elasticache/aws/latest/submodules/serverless-cache
- **Key Features**: Automatic scaling based on usage limits, daily snapshot configuration, KMS encryption support, VPC security group integration
- **Use Cases**: Variable workload caching, development and testing environments, cost-optimized deployments, unpredictable traffic patterns

### 2. user-group

- **Purpose**: Creates and manages AWS ElastiCache users and user groups for authentication and authorization
- **Source**: `terraform-aws-modules/elasticache/aws//modules/user-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/elasticache/aws/latest/submodules/user-group
- **Key Features**: Multiple user creation, default user configuration, access control lists (ACL), password and IAM authentication
- **Use Cases**: Multi-tenant applications, role-based access control, secure Redis authentication, compliance requirements

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `tags` | `map(string)` | `{}` | Tags to add to all resources |
| `create_cluster` | `bool` | `false` | Enable ElastiCache cluster creation (Memcached or Redis without replication) |
| `create_replication_group` | `bool` | `true` | Enable ElastiCache replication group creation (Redis with replication) |
| `engine` | `string` | `"redis"` | Cache engine type: `memcached`, `redis`, or `valkey` |
| `engine_version` | `string` | `null` | Specific engine version (defaults to latest) |
| `node_type` | `string` | `null` | Instance class (e.g., `cache.t4g.small`, `cache.r7g.large`) |
| `num_cache_nodes` | `number` | `1` | Initial number of cache nodes (1-40 for Memcached) |
| `replicas_per_node_group` | `number` | `1` | Number of replica nodes in each node group |
| `num_node_groups` | `number` | `1` | Number of node groups (shards) for cluster mode |
| `multi_az_enabled` | `bool` | `false` | Enable Multi-AZ Support for replication groups |
| `automatic_failover_enabled` | `bool` | `null` | Enable automatic failover for replication groups |
| `transit_encryption_enabled` | `bool` | `true` | Enable encryption in-transit (TLS) |
| `at_rest_encryption_enabled` | `bool` | `true` | Enable encryption at rest |
| `auth_token` | `string` | `null` | Password used for authentication (Redis only) |
| `kms_key_id` | `string` | `null` | ARN of KMS key for at-rest encryption |
| `subnet_ids` | `list(string)` | `[]` | VPC Subnet IDs for ElastiCache subnet group |
| `security_group_ids` | `list(string)` | `[]` | VPC security groups associated with cluster |
| `preferred_availability_zones` | `list(string)` | `[]` | List of Availability Zones for cache nodes |
| `maintenance_window` | `string` | `null` | Weekly time range for system maintenance |
| `snapshot_retention_limit` | `number` | `null` | Number of days to retain automatic snapshots |
| `snapshot_window` | `string` | `null` | Daily time range for automatic snapshots |
| `final_snapshot_identifier` | `string` | `null` | Name of final snapshot before deletion |
| `parameter_group_name` | `string` | `null` | Name of parameter group to associate |
| `parameter_group_family` | `string` | `null` | Family of parameter group |
| `parameter_group_parameters` | `list(map(string))` | `[]` | List of parameter group parameters |
| `user_group_ids` | `list(string)` | `null` | List of user group IDs to associate |
| `auto_minor_version_upgrade` | `bool` | `null` | Enable automatic minor version upgrades |
| `data_tiering_enabled` | `bool` | `null` | Enable data tiering (r6gd node types only) |
| `log_delivery_configuration` | `map(any)` | `{}` | CloudWatch log delivery configuration |
| `apply_immediately` | `bool` | `null` | Apply changes immediately instead of during maintenance window |

## Main Outputs

| Output | Description |
|--------|-------------|
| `cluster_arn` | ARN of the ElastiCache Cluster |
| `cluster_engine_version_actual` | Actual running version of the cache engine |
| `cluster_cache_nodes` | List of node details (ID, address, port, availability zone) |
| `cluster_address` | DNS name without port (Memcached only) |
| `cluster_configuration_endpoint` | Configuration endpoint for host discovery (Memcached only) |
| `replication_group_arn` | ARN of the ElastiCache Replication Group |
| `replication_group_id` | Identifier of the Replication Group |
| `replication_group_primary_endpoint_address` | Primary node endpoint address |
| `replication_group_reader_endpoint_address` | Reader node endpoint address for read replicas |
| `replication_group_port` | Port of the primary node |
| `replication_group_member_clusters` | Identifiers of nodes in the replication group |
| `replication_group_configuration_endpoint_address` | Configuration endpoint when cluster mode is enabled |
| `global_replication_group_id` | Identifier of the Global Replication Group |
| `global_replication_group_arn` | ARN of the Global Replication Group |
| `global_replication_group_node_groups` | Set of node groups (shards) in global replication group |
| `parameter_group_arn` | ARN of the parameter group |
| `parameter_group_id` | ID of the parameter group |
| `subnet_group_name` | Name of the subnet group |
| `security_group_arn` | ARN of the security group |
| `security_group_id` | ID of the security group |
| `cloudwatch_log_groups` | Map of CloudWatch log groups created |

## Submodule 1: serverless-cache

### Description

The serverless-cache submodule creates AWS ElastiCache serverless cache resources that automatically scale based on application demand. This submodule eliminates the need to manually provision and manage cache node capacity by automatically adjusting compute and storage resources based on configured usage limits. It supports both Redis and Memcached engines and integrates with VPC networking, security groups, KMS encryption, and automated snapshot management for Redis deployments.

### Key Features

- Automatic scaling based on data storage and ElastiCache Processing Units (ECPU) limits
- Support for both Redis and Memcached serverless engines
- Daily snapshot scheduling for Redis with configurable retention
- KMS encryption for data at rest with customer-managed keys
- VPC subnet and security group integration for network isolation
- Snapshot restore capability for creating new caches from existing snapshots
- User group association for Redis authentication and authorization
- Configurable timeouts for resource creation, update, and deletion operations

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether serverless cache will be created |
| `cache_name` | `string` | `null` | Unique identifier for the serverless cache |
| `engine` | `string` | `"redis"` | Cache engine type: `memcached` or `redis` |
| `major_engine_version` | `string` | `null` | Major version of cache engine |
| `cache_usage_limits` | `map(any)` | `{}` | Cache usage limits for storage and ECPU |
| `subnet_ids` | `list(string)` | `[]` | VPC subnet IDs for cache deployment |
| `security_group_ids` | `list(string)` | `[]` | VPC security groups associated with cache |
| `kms_key_id` | `string` | `null` | ARN of KMS key for encryption at rest |
| `daily_snapshot_time` | `string` | `null` | Time when daily snapshots are created (Redis only) |
| `snapshot_retention_limit` | `number` | `null` | Number of snapshots to retain (Redis only) |
| `snapshot_arns_to_restore` | `list(string)` | `null` | Snapshot ARNs to restore from (Redis only) |
| `user_group_id` | `string` | `null` | User group ID for authentication (Redis only) |
| `description` | `string` | `null` | User-created description for the cache |
| `tags` | `map(string)` | `{}` | Tags to add to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `serverless_cache_arn` | ARN of the serverless cache |
| `serverless_cache_id` | Identifier of the serverless cache |
| `serverless_cache_endpoint` | Endpoint connection information |
| `serverless_cache_reader_endpoint` | Reader endpoint for read operations |
| `serverless_cache_status` | Current status of the serverless cache |
| `serverless_cache_create_time` | Creation timestamp |
| `serverless_cache_engine` | Cache engine type |
| `serverless_cache_major_engine_version` | Major engine version |

### Usage Example

```hcl
module "elasticache_serverless" {
  source = "terraform-aws-modules/elasticache/aws//modules/serverless-cache"

  cache_name = "my-serverless-redis"
  engine     = "redis"

  # Define usage limits
  cache_usage_limits = {
    data_storage = {
      maximum = 10  # GB
      unit    = "GB"
    }
    ecpu_per_second = {
      maximum = 5000
    }
  }

  # Network configuration
  subnet_ids         = ["subnet-12345678", "subnet-87654321"]
  security_group_ids = ["sg-12345678"]

  # Snapshot configuration (Redis only)
  daily_snapshot_time      = "03:00"
  snapshot_retention_limit = 7

  # Encryption
  kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"

  tags = {
    Environment = "production"
    Application = "api-cache"
  }
}
```

## Submodule 2: user-group

### Description

The user-group submodule creates and manages AWS ElastiCache users and user groups for Redis authentication and authorization. This submodule enables fine-grained access control by allowing creation of multiple users with specific access permissions (ACLs) and grouping them for association with ElastiCache replication groups or serverless caches. It supports both password-based and IAM authentication methods, providing flexible security options for Redis deployments.

### Key Features

- Create multiple users with individual access control lists (ACLs)
- Default user configuration with customizable authentication
- Support for password-based and IAM authentication modes
- User group creation for associating multiple users with caches
- Redis-specific access string configuration for command-level permissions
- Flexible authentication with support for multiple passwords per user
- User and group tagging for resource organization
- Optional user and group creation flags for granular control

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `create_group` | `bool` | `true` | Determines whether user group will be created |
| `user_group_id` | `string` | `""` | ID of the user group |
| `engine` | `string` | `"redis"` | Cache engine type (currently only `redis` supported) |
| `users` | `any` | `{}` | Map of users to create with their configurations |
| `create_default_user` | `bool` | `true` | Determines whether default user will be created |
| `default_user` | `any` | `{}` | Map of default user attributes |
| `default_user_id` | `string` | `"default"` | ID of the default user |
| `tags` | `map(string)` | `{}` | Tags to add to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `group_arn` | ARN of the user group |
| `group_id` | ID of the user group |
| `users` | Map of created users with their attributes |
| `user_arns` | Map of user ARNs |
| `user_ids` | Map of user IDs |

### Usage Example

```hcl
module "elasticache_users" {
  source = "terraform-aws-modules/elasticache/aws//modules/user-group"

  user_group_id = "production-redis-users"
  engine        = "redis"

  # Create default user with restricted access
  create_default_user = true
  default_user = {
    access_string = "off +get ~keys:*"
    passwords     = ["default-password-12345"]
  }

  # Create additional users
  users = {
    admin_user = {
      access_string = "on ~* &* +@all"
      passwords     = ["admin-password-12345", "admin-password-67890"]
      authentication_mode = {
        type      = "password"
        passwords = ["admin-password-12345", "admin-password-67890"]
      }
    }

    readonly_user = {
      access_string = "on ~* &* +@read"
      passwords     = ["readonly-password-12345"]
    }

    app_user = {
      access_string = "on ~app:* +@all -@dangerous"
      passwords     = ["app-password-12345"]
    }
  }

  tags = {
    Environment = "production"
    Application = "redis-cache"
  }
}

# Associate user group with ElastiCache replication group
module "elasticache_redis" {
  source = "terraform-aws-modules/elasticache/aws"

  # ... other configuration ...

  user_group_ids = [module.elasticache_users.group_id]
}
```

## Usage Examples

### Example 1: Memcached Cluster

```hcl
module "memcached" {
  source = "terraform-aws-modules/elasticache/aws"

  create_cluster = true

  cluster_id       = "my-memcached-cluster"
  engine           = "memcached"
  engine_version   = "1.6.17"
  node_type        = "cache.t4g.small"
  num_cache_nodes  = 3

  # Network configuration
  subnet_ids = ["subnet-12345678", "subnet-87654321"]

  # Security
  security_group_rules = {
    ingress_vpc = {
      cidr_ipv4   = "10.0.0.0/16"
      description = "Allow Memcached access from VPC"
    }
  }

  # Maintenance
  maintenance_window       = "sun:05:00-sun:06:00"
  preferred_availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

  tags = {
    Environment = "production"
    CacheType   = "memcached"
  }
}
```

### Example 2: Redis Replication Group with Multi-AZ

```hcl
module "redis_replication" {
  source = "terraform-aws-modules/elasticache/aws"

  create_replication_group = true

  replication_group_id       = "my-redis-cluster"
  replication_group_description = "Redis cluster with automatic failover"

  engine         = "redis"
  engine_version = "7.1"
  node_type      = "cache.r7g.large"

  # High availability configuration
  multi_az_enabled           = true
  automatic_failover_enabled = true
  replicas_per_node_group    = 2

  # Network configuration
  subnet_ids = ["subnet-12345678", "subnet-87654321", "subnet-11111111"]

  # Security
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true
  auth_token                 = "SecurePassword123456!"

  security_group_rules = {
    ingress_vpc = {
      cidr_ipv4   = "10.0.0.0/16"
      description = "Allow Redis access from VPC"
    }
  }

  # Backup configuration
  snapshot_retention_limit = 7
  snapshot_window         = "03:00-05:00"
  final_snapshot_identifier = "my-redis-final-snapshot"

  # Maintenance
  maintenance_window = "mon:05:00-mon:07:00"

  # Monitoring
  log_delivery_configuration = {
    slow_log = {
      destination      = aws_cloudwatch_log_group.redis_slow_log.name
      destination_type = "cloudwatch-logs"
      log_format       = "json"
    }
    engine_log = {
      destination      = aws_cloudwatch_log_group.redis_engine_log.name
      destination_type = "cloudwatch-logs"
      log_format       = "json"
    }
  }

  tags = {
    Environment = "production"
    Application = "session-store"
  }
}

resource "aws_cloudwatch_log_group" "redis_slow_log" {
  name              = "/aws/elasticache/redis/slow-log"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "redis_engine_log" {
  name              = "/aws/elasticache/redis/engine-log"
  retention_in_days = 7
}
```

### Example 3: Redis Cluster Mode for Horizontal Scaling

```hcl
module "redis_cluster_mode" {
  source = "terraform-aws-modules/elasticache/aws"

  create_replication_group = true

  replication_group_id          = "my-redis-sharded"
  replication_group_description = "Redis cluster mode for horizontal scaling"

  engine         = "redis"
  engine_version = "7.1"
  node_type      = "cache.r7g.xlarge"

  # Cluster mode configuration
  cluster_mode_enabled    = true
  num_node_groups         = 3  # 3 shards
  replicas_per_node_group = 2  # 2 replicas per shard

  # High availability
  multi_az_enabled           = true
  automatic_failover_enabled = true

  # Network configuration
  subnet_ids = ["subnet-12345678", "subnet-87654321", "subnet-11111111"]

  # Security
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true
  kms_key_id                 = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"

  # Parameter group for cluster mode
  create_parameter_group = true
  parameter_group_family = "redis7"
  parameter_group_parameters = [
    {
      name  = "cluster-enabled"
      value = "yes"
    },
    {
      name  = "maxmemory-policy"
      value = "allkeys-lru"
    }
  ]

  tags = {
    Environment = "production"
    Application = "leaderboard"
  }
}
```

### Example 4: Global Replication Group for Multi-Region

```hcl
# Primary region configuration
module "redis_global_primary" {
  source = "terraform-aws-modules/elasticache/aws"

  providers = {
    aws = aws.us_east_1
  }

  create_replication_group = true

  replication_group_id          = "global-redis-primary"
  replication_group_description = "Primary cluster for global replication"

  engine         = "redis"
  engine_version = "7.1"
  node_type      = "cache.r7g.large"

  multi_az_enabled           = true
  automatic_failover_enabled = true
  replicas_per_node_group    = 2

  subnet_ids                 = var.primary_subnet_ids
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true

  # Enable global datastore
  global_replication_group_id_suffix = "global"

  tags = {
    Environment = "production"
    Region      = "primary"
  }
}

# Secondary region configuration
module "redis_global_secondary" {
  source = "terraform-aws-modules/elasticache/aws"

  providers = {
    aws = aws.eu_west_1
  }

  create_replication_group = true

  replication_group_id          = "global-redis-secondary"
  replication_group_description = "Secondary cluster for global replication"

  # Reference global replication group from primary
  global_replication_group_id = module.redis_global_primary.global_replication_group_id

  node_type                  = "cache.r7g.large"
  replicas_per_node_group    = 1

  subnet_ids = var.secondary_subnet_ids

  tags = {
    Environment = "production"
    Region      = "secondary"
  }
}
```

### Example 5: Serverless Cache with Auto-Scaling

```hcl
module "redis_serverless" {
  source = "terraform-aws-modules/elasticache/aws//modules/serverless-cache"

  cache_name = "serverless-redis-cache"
  engine     = "redis"

  # Define auto-scaling limits
  cache_usage_limits = {
    data_storage = {
      maximum = 20
      unit    = "GB"
    }
    ecpu_per_second = {
      maximum = 10000
    }
  }

  # Network configuration
  subnet_ids         = ["subnet-12345678", "subnet-87654321"]
  security_group_ids = ["sg-12345678"]

  # Snapshot configuration
  daily_snapshot_time      = "04:00"
  snapshot_retention_limit = 14

  # Encryption
  kms_key_id = aws_kms_key.elasticache.arn

  # User authentication
  user_group_id = module.elasticache_users.group_id

  tags = {
    Environment = "staging"
    Application = "api-cache"
    CostCenter  = "engineering"
  }
}
```

### Example 6: Redis with User Group Authentication

```hcl
# Create user group
module "redis_user_group" {
  source = "terraform-aws-modules/elasticache/aws//modules/user-group"

  user_group_id = "app-redis-users"

  # Disable default user for security
  create_default_user = false

  # Create application users
  users = {
    admin = {
      access_string = "on ~* &* +@all"
      passwords     = [random_password.redis_admin.result]
    }

    app_readwrite = {
      access_string = "on ~app:* +@write +@read -@dangerous"
      passwords     = [random_password.redis_app.result]
    }

    monitoring = {
      access_string = "on ~* +@read +@slow +@connection"
      passwords     = [random_password.redis_monitoring.result]
    }
  }

  tags = {
    Environment = "production"
  }
}

# Create Redis cluster with user group
module "redis_with_users" {
  source = "terraform-aws-modules/elasticache/aws"

  create_replication_group = true

  replication_group_id = "secure-redis"
  replication_group_description = "Redis with user-based authentication"

  engine         = "redis"
  engine_version = "7.1"
  node_type      = "cache.r7g.large"

  multi_az_enabled           = true
  automatic_failover_enabled = true
  replicas_per_node_group    = 1

  # Associate user group
  user_group_ids = [module.redis_user_group.group_id]

  # Security
  subnet_ids                 = var.subnet_ids
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true

  tags = {
    Environment = "production"
    Security    = "high"
  }
}

resource "random_password" "redis_admin" {
  length  = 32
  special = true
}

resource "random_password" "redis_app" {
  length  = 32
  special = true
}

resource "random_password" "redis_monitoring" {
  length  = 32
  special = true
}
```

### Example 7: Redis with Custom Parameter Group

```hcl
module "redis_custom_params" {
  source = "terraform-aws-modules/elasticache/aws"

  create_replication_group = true

  replication_group_id = "redis-custom-config"
  replication_group_description = "Redis with custom parameters"

  engine         = "redis"
  engine_version = "7.1"
  node_type      = "cache.r7g.xlarge"

  replicas_per_node_group = 1

  # Custom parameter group
  create_parameter_group = true
  parameter_group_family = "redis7"
  parameter_group_parameters = [
    {
      name  = "maxmemory-policy"
      value = "allkeys-lru"
    },
    {
      name  = "timeout"
      value = "300"
    },
    {
      name  = "tcp-keepalive"
      value = "300"
    },
    {
      name  = "maxmemory-samples"
      value = "10"
    },
    {
      name  = "slowlog-log-slower-than"
      value = "10000"
    },
    {
      name  = "slowlog-max-len"
      value = "256"
    }
  ]

  # Network and security
  subnet_ids                 = var.subnet_ids
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true

  tags = {
    Environment = "production"
    Tuning      = "custom"
  }
}
```

### Example 8: Valkey Replication Group

```hcl
module "valkey_replication" {
  source = "terraform-aws-modules/elasticache/aws"

  create_replication_group = true

  replication_group_id = "valkey-cluster"
  replication_group_description = "Valkey open-source Redis alternative"

  engine         = "valkey"
  engine_version = "7.2"
  node_type      = "cache.r7g.large"

  multi_az_enabled           = true
  automatic_failover_enabled = true
  replicas_per_node_group    = 2

  # Network configuration
  subnet_ids = var.subnet_ids

  # Security
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true

  # Snapshots
  snapshot_retention_limit = 5
  snapshot_window         = "03:00-05:00"

  tags = {
    Environment = "production"
    Engine      = "valkey"
  }
}
```

## Best Practices

### Security and Access Control

1. **Encryption Enabled by Default**: Both `transit_encryption_enabled` and `at_rest_encryption_enabled` are `true` by default. Use KMS customer-managed keys via `kms_key_arn` for compliance requirements.
2. **Keep Encryption Enabled**: Do not disable encryption for production deployments; the secure defaults protect data in transit and at rest.
3. **Implement User-Based Authentication**: Use the user-group submodule to create fine-grained access control instead of relying on a single AUTH token.
4. **Use VPC Private Subnets**: Deploy ElastiCache clusters in private subnets with no direct internet access to minimize attack surface.
5. **Configure Security Groups Carefully**: Restrict ingress rules to only the specific CIDR blocks or security groups that need cache access.
6. **Rotate AUTH Tokens Regularly**: If using AUTH tokens, implement a rotation schedule and use AWS Secrets Manager for secure storage.
7. **Apply Least Privilege ACLs**: When creating users, grant only the minimum required Redis commands using access strings (e.g., `on ~app:* +@read +@write -@dangerous`).

### High Availability and Disaster Recovery

1. **Enable Multi-AZ**: Set `multi_az_enabled = true` for production replication groups to ensure automatic failover across Availability Zones.
2. **Configure Automatic Failover**: Use `automatic_failover_enabled = true` with at least one replica to minimize downtime during node failures.
3. **Implement Global Replication**: For mission-critical applications requiring disaster recovery, deploy global replication groups across multiple regions.
4. **Configure Snapshot Retention**: Set `snapshot_retention_limit` to retain 7-14 daily snapshots for point-in-time recovery.
5. **Use Final Snapshots**: Always specify `final_snapshot_identifier` to create a final backup before cluster deletion for recovery safety.
6. **Test Failover Procedures**: Regularly test automatic failover by simulating primary node failures in non-production environments.

### Performance and Optimization

1. **Choose Appropriate Node Types**: Select node types based on workload requirements; use r7g instances for memory-intensive workloads and t4g for development.
2. **Implement Cluster Mode for Scale**: Use cluster mode with multiple shards (`num_node_groups > 1`) for workloads exceeding single-node capacity.
3. **Configure Maxmemory Policy**: Set appropriate eviction policies via parameter groups (e.g., `allkeys-lru` for caching, `noeviction` for persistent data).
4. **Use Read Replicas**: Deploy multiple replicas (`replicas_per_node_group`) to distribute read traffic and improve performance.
5. **Enable Connection Pooling**: Configure application connection pools to reuse ElastiCache connections and reduce connection overhead.
6. **Optimize Key Design**: Use consistent key naming patterns and appropriate data structures for your access patterns (hashes for objects, sorted sets for leaderboards).
7. **Monitor Evictions**: Track `Evictions` metric in CloudWatch; high eviction rates indicate undersized nodes or poor key TTL configuration.
8. **Tune Timeout Settings**: Adjust `timeout` parameter to match application requirements and prevent resource exhaustion from idle connections.

### Monitoring and Observability

1. **Enable CloudWatch Log Delivery**: Configure `log_delivery_configuration` for slow logs and engine logs to identify performance issues.
2. **Set Up CloudWatch Alarms**: Create alarms for key metrics like CPUUtilization, DatabaseMemoryUsagePercentage, and EngineCPUUtilization.
3. **Monitor Cache Hit Ratio**: Track CacheHitRate metric; low hit rates (< 80%) indicate caching inefficiencies or improper TTL configuration.
4. **Track Connection Counts**: Monitor `CurrConnections` to detect connection leaks and ensure applications properly close connections.
5. **Use Enhanced Monitoring**: Enable detailed monitoring for granular visibility into cache performance and resource utilization.
6. **Implement Slow Log Analysis**: Regularly review slow logs to identify poorly performing commands and optimize application queries.

### Cost Optimization

1. **Right-Size Node Types**: Start with smaller instance types (t4g) for development and staging; use reserved instances for production to save costs.
2. **Use Serverless for Variable Workloads**: Deploy serverless caches for unpredictable workloads to pay only for actual usage.
3. **Optimize Snapshot Retention**: Balance retention requirements with storage costs; 7 days is typically sufficient for most use cases.
4. **Leverage Data Tiering**: Use r6gd node types with data tiering enabled to reduce costs for workloads with large datasets and skewed access patterns.
5. **Schedule Maintenance Appropriately**: Configure maintenance windows during low-traffic periods to minimize performance impact and potential revenue loss.
6. **Remove Unused Clusters**: Implement tagging and regular audits to identify and delete unused or test ElastiCache resources.

### Operational Excellence

1. **Use Infrastructure as Code**: Manage all ElastiCache resources through Terraform to ensure consistency and enable version control.
2. **Implement Tagging Strategy**: Apply comprehensive tags including Environment, Application, Owner, and CostCenter for resource management.
3. **Plan Maintenance Windows**: Set `maintenance_window` during low-traffic periods and communicate schedules to stakeholders.
4. **Test Before Applying Changes**: Use `apply_immediately = false` in production and test changes during scheduled maintenance windows.
5. **Document Parameter Customizations**: Clearly document why specific parameter group values were chosen and their expected impact.
6. **Implement Change Control**: Use separate Terraform workspaces or modules for different environments to prevent accidental production changes.
7. **Monitor Engine Version Updates**: Stay informed about new engine versions and plan upgrades to benefit from performance improvements and security patches.
8. **Create Runbooks**: Document operational procedures for common tasks like failover, scaling, and snapshot restoration.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-elasticache
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/elasticache/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-elasticache/tree/master/examples
- **AWS ElastiCache Documentation**: https://docs.aws.amazon.com/elasticache/
- **Redis Documentation**: https://redis.io/documentation
- **Memcached Documentation**: https://memcached.org/
- **ElastiCache for Redis User Guide**: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/
- **ElastiCache for Memcached User Guide**: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/
- **ElastiCache Serverless**: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/WhatIs-Serverless.html
- **ElastiCache Best Practices**: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/BestPractices.html
- **Choosing Between Redis and Memcached**: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/SelectEngine.html
- **ElastiCache Pricing**: https://aws.amazon.com/elasticache/pricing/
- **Redis Commands Reference**: https://redis.io/commands
- **ElastiCache CloudWatch Metrics**: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/CacheMetrics.html
- **Global Datastore for Redis**: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Redis-Global-Datastore.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Choose Engine Wisely**: Use Redis for complex data structures, persistence, and pub/sub; use Memcached for simple key-value caching with multi-threading
2. **Enable High Availability**: Always configure Multi-AZ and automatic failover for production deployments
3. **Encryption Defaults**: Transit and at-rest encryption are enabled by default; use `kms_key_arn` for KMS customer-managed keys
4. **Use User Groups**: Prefer user-group submodule over AUTH tokens for better security and auditability
5. **Configure Snapshots**: Set snapshot retention limits and windows for Redis to enable point-in-time recovery
6. **Monitor Performance**: Enable CloudWatch log delivery and set up alarms for CPU, memory, and cache hit ratio metrics
7. **Right-Size Nodes**: Start with appropriate node types based on workload; use r7g for memory-intensive, t4g for dev/test
8. **Plan for Scale**: Use cluster mode for horizontal scaling beyond single-node capacity
9. **Tag Resources**: Apply consistent tags including Environment, Application, and Owner for cost tracking and resource management
10. **Test Failover**: Regularly validate automatic failover in non-production environments
11. **Optimize Parameters**: Customize parameter groups for maxmemory-policy, timeout, and slow log settings based on workload
12. **Use Private Subnets**: Deploy in VPC private subnets with restrictive security groups
13. **Consider Serverless**: For variable or unpredictable workloads, use serverless-cache submodule for cost optimization
14. **Plan Maintenance**: Configure maintenance windows during low-traffic periods and test changes before production
15. **Document Configurations**: Maintain clear documentation of custom parameters, security settings, and architectural decisions
