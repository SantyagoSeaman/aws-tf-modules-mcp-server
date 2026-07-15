# Terraform AWS ElastiCache Module

## Module Information

- **Module Name**: `elasticache`
- **Module ID**: `terraform-aws-modules/elasticache/aws`
- **Source**: `terraform-aws-modules/elasticache/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-elasticache
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/elasticache/aws/latest
- **Latest Version**: 1.11.0
- **Minimum Versions**: Terraform >= 1.0, AWS Provider >= 5.93, random Provider >= 3.0
- **Purpose**: Terraform module that creates and manages AWS ElastiCache resources — standalone clusters, Redis/Valkey replication groups (with optional cluster mode/sharding), and cross-region global replication groups — for the Redis, Memcached, and Valkey cache engines
- **Service**: AWS ElastiCache (Managed In-Memory Caching Service)
- **Category**: Database, Caching, Performance Optimization
- **Keywords**: elasticache, redis, valkey, memcached, in-memory-cache, replication-group, cluster-mode, global-datastore, serverless-cache, multi-az, automatic-failover, transit-encryption, at-rest-encryption, auth-token, user-group, sharding
- **Use For**: session caching, database query-result caching, real-time leaderboards and analytics, pub/sub messaging, rate limiting and throttling, distributed locks, gaming session state, API response caching, multi-region low-latency reads, cost-optimized variable-workload caching (serverless)

## Description

This Terraform module provisions AWS ElastiCache resources for the Redis, Memcached, and Valkey (an open-source Redis fork) cache engines. A single root module — selected through boolean toggles (`create_cluster`, `create_replication_group`, `create_primary_global_replication_group`, `create_secondary_global_replication_group`) — creates one of four deployment shapes: a standalone cache cluster, a Redis/Valkey replication group with automatic failover, a sharded (cluster mode) replication group, or a cross-region global replication group (Global Datastore). Alongside the primary cache resource, the module manages the ElastiCache subnet group, an optional customer-defined parameter group, a self-managed VPC security group (built from `vpc_id` + `security_group_rules`), and CloudWatch log groups for slow-log/engine-log delivery.

AWS ElastiCache is a fully managed, in-memory data store and cache that delivers sub-millisecond read/write latency and removes the operational burden of patching, monitoring, and failover for distributed caching infrastructure. It is commonly used to offload read-heavy database workloads, store ephemeral session and rate-limiting state, back real-time leaderboards and pub/sub messaging, and serve as a low-latency data layer for latency-sensitive applications.

The module ships as a root module plus two independent submodules: `serverless-cache`, for ElastiCache Serverless deployments that auto-scale storage and compute based on usage limits without any node sizing, and `user-group`, for creating Redis/Valkey ACL-based users and user groups used for fine-grained, password- or IAM-based authentication (an alternative to a single shared AUTH token). Both encryption in transit and encryption at rest are **enabled by default**, and slow-log CloudWatch delivery is auto-configured out of the box. Version 1.11.0 added a `default_user_arn` output to the `user-group` submodule; recent releases also added AUTH token rotation strategies, transit-encryption migration mode, and self-referencing security group rules for inter-node cluster communication.

## Key Features

- **Three Cache Engines**: `redis`, `memcached`, and `valkey`, selected via a single `engine` variable
- **Four Deployment Shapes**: standalone cluster (`create_cluster`), replication group with automatic failover (`create_replication_group`, default), sharded/cluster-mode replication group (`cluster_mode_enabled`), and cross-region global replication group (`create_primary_global_replication_group` / `create_secondary_global_replication_group`)
- **ElastiCache Serverless Submodule**: on-demand storage/ECPU auto-scaling with no node types to size, via `cache_usage_limits`
- **User/User-Group Submodule**: ACL-based Redis/Valkey users with password or IAM authentication, grouped and associated via `user_group_ids`
- **Cluster Mode Sharding**: `num_node_groups` (shards) × `replicas_per_node_group` (0-5 replicas per shard); the module auto-injects the `cluster-enabled = yes` parameter
- **Global Datastore**: cross-region active-passive replication for disaster recovery and low-latency reads close to users, configured via `global_replication_group_id_suffix`
- **Multi-AZ & Automatic Failover**: `multi_az_enabled` (or `cluster_mode_enabled`) forces `automatic_failover_enabled = true`
- **Self-Managed Security Group**: built from `vpc_id` + `security_group_rules`, including self-referencing ingress rules (`referenced_security_group_id = "self"`) for inter-node cluster mode traffic
- **Encryption On By Default**: `transit_encryption_enabled` and `at_rest_encryption_enabled` both default to `true`; `kms_key_arn` supplies a customer-managed key for at-rest encryption
- **AUTH Token Rotation**: `auth_token_update_strategy` (`SET`, `ROTATE`, `DELETE`) for zero-downtime AUTH token changes
- **Transit-Encryption Migration Mode**: `transit_encryption_mode` (`preferred`/`required`) allows migrating an existing unencrypted replication group to TLS without downtime
- **Parameter Group Management**: `create_parameter_group` + `parameter_group_family` + `parameters` for engine-level tuning (e.g. `maxmemory-policy`)
- **CloudWatch Log Delivery**: `log_delivery_configuration` defaults to delivering the slow log to an auto-created CloudWatch log group in JSON format
- **Snapshot Management**: automated snapshot window/retention, `final_snapshot_identifier` before deletion, and restore-from-snapshot via `snapshot_arns`/`snapshot_name`
- **Data Tiering**: `data_tiering_enabled` for `r6gd` node types, moving less-frequently-accessed data to SSD to reduce cost
- **Composable Outputs**: endpoints, ARNs, and IDs (security group, subnet group, parameter group, log groups) designed to feed downstream application/networking modules

## Main Use Cases

1. **Database Query Result Caching**: Reduce database load by caching frequently accessed query results
2. **Session State Management**: Store and retrieve user session data for web applications with high concurrency
3. **Real-time Leaderboards and Analytics**: Maintain sorted sets for gaming scores, rankings, and live statistics
4. **API Response Caching**: Cache API responses to improve response times and reduce backend processing
5. **Pub/Sub Messaging**: Implement real-time messaging and notification systems using Redis/Valkey pub/sub
6. **Rate Limiting and Throttling**: Track and enforce API rate limits and request throttling
7. **Distributed Locking**: Coordinate access to shared resources across distributed application instances
8. **Multi-Region Disaster Recovery**: Use global replication groups for cross-region failover and low-latency reads
9. **Variable/Unpredictable Workloads**: Use the `serverless-cache` submodule to auto-scale without capacity planning
10. **Secure Multi-Tenant Caching**: Use the `user-group` submodule for per-application ACLs instead of a shared AUTH token

## Submodules

### 1. serverless-cache

- **Purpose**: Creates an AWS ElastiCache Serverless cache that auto-scales storage and compute
- **Source**: `terraform-aws-modules/elasticache/aws//modules/serverless-cache`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/elasticache/aws/latest/submodules/serverless-cache
- **Key Features**: Usage-based scaling (`cache_usage_limits`), daily Redis snapshots, KMS encryption, snapshot restore, user-group association
- **Use Cases**: Variable/unpredictable traffic, dev/test environments, cost-optimized deployments without capacity planning

### 2. user-group

- **Purpose**: Creates AWS ElastiCache users and a user group for Redis/Valkey ACL-based authentication
- **Source**: `terraform-aws-modules/elasticache/aws//modules/user-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/elasticache/aws/latest/submodules/user-group
- **Key Features**: Multiple users with individual access strings, password or IAM authentication modes, default-user configuration
- **Use Cases**: Multi-tenant applications, role-based access control, compliance-driven per-application credentials

## Submodule 1: serverless-cache

### Description

Creates a single `aws_elasticache_serverless_cache` resource. ElastiCache Serverless removes node sizing entirely: AWS automatically scales storage and compute (measured in ElastiCache Processing Units, ECPUs) between the limits set in `cache_usage_limits`, and you pay only for what is consumed. Supports the `redis` and `memcached` engines (not Valkey); Redis-only features include daily automated snapshots and user-group authentication.

### Key Features

- Automatic scaling based on `cache_usage_limits.data_storage` and `cache_usage_limits.ecpu_per_second`
- Supports both `redis` and `memcached` serverless engines
- Daily snapshot scheduling with configurable retention (Redis only)
- KMS encryption for data at rest via `kms_key_id` (customer-managed key)
- VPC subnet and security group integration for network isolation
- Restore a new cache from existing snapshots via `snapshot_arns_to_restore`
- User-group association for Redis authentication via `user_group_id`

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether the serverless cache will be created |
| `cache_name` | `string` | `null` | Unique identifier for the serverless cache |
| `engine` | `string` | `"redis"` | Cache engine: `memcached` or `redis` |
| `major_engine_version` | `string` | `null` | Major engine version used to create the cache |
| `cache_usage_limits` | `map(any)` | `{}` | Usage limits for `data_storage` and `ecpu_per_second` |
| `subnet_ids` | `list(string)` | `[]` | Subnets where the cache's VPC endpoint is deployed |
| `security_group_ids` | `list(string)` | `[]` | VPC security groups associated with the cache |
| `kms_key_id` | `string` | `null` | ARN of the customer-managed KMS key for at-rest encryption |
| `daily_snapshot_time` | `string` | `null` | Daily snapshot time (Redis only) |
| `snapshot_retention_limit` | `number` | `null` | Number of snapshots retained (Redis only) |
| `snapshot_arns_to_restore` | `list(string)` | `null` | Snapshot ARN(s) to restore from (Redis only) |
| `user_group_id` | `string` | `null` | User group ID for authentication (Redis only) |
| `description` | `string` | `null` | User-created description for the cache |
| `tags` | `map(string)` | `{}` | Tags to add to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `serverless_cache_arn` | ARN of the serverless cache |
| `serverless_cache_endpoint` | Connection endpoint information |
| `serverless_cache_reader_endpoint` | Reader endpoint for read operations |
| `serverless_cache_status` | Current status (`CREATING`, `AVAILABLE`, `DELETING`, `CREATE-FAILED`, `MODIFYING`) |
| `serverless_cache_create_time` | Creation timestamp |
| `serverless_cache_full_engine_version` | Full engine name and version the cache is compatible with |
| `serverless_cache_major_engine_version` | Major engine version the cache is compatible with |

### Usage Example

```hcl
module "elasticache_serverless" {
  source = "terraform-aws-modules/elasticache/aws//modules/serverless-cache"

  engine     = "redis"
  cache_name = "my-serverless-redis"

  cache_usage_limits = {
    data_storage = {
      maximum = 10 # GB
      unit    = "GB"
    }
    ecpu_per_second = {
      maximum = 5000
    }
  }

  major_engine_version = "7"
  description           = "Serverless cache for API responses"

  # Network configuration
  subnet_ids         = module.vpc.private_subnets
  security_group_ids = [module.elasticache_sg.security_group_id]

  # Snapshot configuration (Redis only)
  daily_snapshot_time      = "03:00"
  snapshot_retention_limit = 7

  # Encryption
  kms_key_id = aws_kms_key.elasticache.arn

  # Authentication (optional)
  user_group_id = module.elasticache_users.group_id

  tags = {
    Environment = "production"
    Application = "api-cache"
  }
}
```

## Submodule 2: user-group

### Description

Creates `aws_elasticache_user` and `aws_elasticache_user_group` resources for Redis/Valkey ACL-based access control. Each user is defined with an `access_string` (Redis ACL syntax) and either `password` or `iam` authentication. Users are grouped into a single `aws_elasticache_user_group`, which is then attached to a replication group or serverless cache via `user_group_ids` / `user_group_id`. Currently only the `redis` engine value is supported by this submodule (it also applies to Valkey deployments, which share the Redis ACL model).

### Key Features

- Create multiple users, each with an individual ACL `access_string`
- Optional default user (`create_default_user`), independently toggleable
- Password-based or IAM authentication modes per user
- User group creation for associating multiple users with a cache
- `default_user_arn` output for referencing the default user's ARN (added in v1.11.0)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `create_group` | `bool` | `true` | Determines whether the user group will be created |
| `user_group_id` | `string` | `""` | ID of the user group |
| `engine` | `string` | `"redis"` | Cache engine; currently only `redis` is supported |
| `users` | `any` | `{}` | Map of users to create, each with `access_string` and `passwords`/`authentication_mode` |
| `create_default_user` | `bool` | `true` | Determines whether a default user will be created |
| `default_user` | `any` | `{}` | Map of default user attributes |
| `default_user_id` | `string` | `"default"` | ID of the default user |
| `tags` | `map(string)` | `{}` | Tags to add to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `group_arn` | ARN of the user group |
| `group_id` | ID of the user group |
| `default_user_arn` | ARN of the default user |
| `users` | Map of created users and their attributes |

### Usage Example

```hcl
module "elasticache_users" {
  source = "terraform-aws-modules/elasticache/aws//modules/user-group"

  user_group_id = "production-redis-users"

  # Disable default user for tighter security
  create_default_user = false

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
      access_string       = "on ~* +@read +@slow +@connection"
      authentication_mode = { type = "iam" }
    }
  }

  tags = {
    Environment = "production"
  }
}

resource "random_password" "redis_admin" {
  length  = 32
  special = false
}

resource "random_password" "redis_app" {
  length  = 32
  special = false
}

# Associate the user group with an ElastiCache replication group
module "elasticache_redis" {
  source = "terraform-aws-modules/elasticache/aws"

  # ... other configuration ...

  user_group_ids = [module.elasticache_users.group_id]
}
```

## Main Module: ElastiCache

### Description

The root module manages the full lifecycle of the primary cache resource — standalone cluster, replication group, or global replication group — plus its supporting infrastructure: subnet group, parameter group, security group, and CloudWatch log groups. Which resource is created is controlled entirely by boolean toggles (`create_cluster`, `create_replication_group`, `create_primary_global_replication_group`, `create_secondary_global_replication_group`); exactly one combination should be set to `true` per module call.

### Key Features

- Single-module interface for four deployment shapes (cluster, replication group, cluster-mode replication group, global replication group)
- VPC security group creation from `vpc_id` + `security_group_rules`, or bring-your-own via `security_group_ids`
- Encryption at rest and in transit both enabled by default
- Auto-created CloudWatch log group for the Redis/Valkey slow log by default
- Snapshot backup/restore and final-snapshot-on-deletion support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls creation of all resources |
| `create_cluster` | `bool` | `false` | Create a standalone (non-replicated) ElastiCache cluster |
| `create_replication_group` | `bool` | `true` | Create a Redis/Valkey replication group (default mode) |
| `create_primary_global_replication_group` | `bool` | `false` | Create a Global Datastore and make this replication group its primary |
| `create_secondary_global_replication_group` | `bool` | `false` | Join this replication group to an existing Global Datastore as a secondary |
| `cluster_id` | `string` | `""` | Identifier for the standalone cluster (used with `create_cluster = true`) |
| `replication_group_id` | `string` | `null` | Identifier for the replication group |
| `engine` | `string` | `"redis"` | Cache engine: `memcached`, `redis`, or `valkey` |
| `engine_version` | `string` | `null` | Engine version; defaults to the latest supported |
| `node_type` | `string` | `null` | Instance class, e.g. `cache.t4g.small`, `cache.r7g.large` |
| `num_cache_nodes` | `number` | `1` | Nodes for a standalone cluster (Memcached: 1-40; Redis/Valkey: 1) |
| `num_cache_clusters` | `number` | `null` | Total nodes (primary + replicas) for a non-cluster-mode replication group; conflicts with `num_node_groups` |
| `cluster_mode_enabled` | `bool` | `false` | Enable Redis/Valkey cluster mode (sharding); auto-sets the `cluster-enabled` parameter |
| `num_node_groups` | `number` | `null` | Number of shards when `cluster_mode_enabled = true` |
| `replicas_per_node_group` | `number` | `null` | Replicas per shard (0-5) |
| `multi_az_enabled` | `bool` | `false` | Enable Multi-AZ; forces `automatic_failover_enabled = true` |
| `automatic_failover_enabled` | `bool` | `null` | Auto-promote a read replica to primary on failure |
| `transit_encryption_enabled` | `bool` | `true` | Encrypt data in transit (TLS) |
| `transit_encryption_mode` | `string` | `null` | `preferred` or `required`; used for zero-downtime TLS migration |
| `at_rest_encryption_enabled` | `bool` | `true` | Encrypt data at rest |
| `kms_key_arn` | `string` | `null` | Customer-managed KMS key ARN for at-rest encryption |
| `auth_token` | `string` | `null` | AUTH password; requires `transit_encryption_enabled = true` |
| `auth_token_update_strategy` | `string` | `null` | `SET`, `ROTATE`, or `DELETE` for AUTH token rotation |
| `user_group_ids` | `list(string)` | `null` | Associates a user group (max one) created by the `user-group` submodule |
| `vpc_id` | `string` | `null` | VPC where the module-created security group is placed |
| `security_group_rules` | `any` | `{}` | Ingress/egress rules added to the module-created security group — keys (from examples): `description`, `cidr_ipv4`, `referenced_security_group_id` |
| `security_group_ids` | `list(string)` | `[]` | Additional externally managed security groups to attach |
| `subnet_ids` | `list(string)` | `[]` | Subnet IDs for the ElastiCache subnet group |
| `create_parameter_group` | `bool` | `false` | Create a custom parameter group |
| `parameter_group_family` | `string` | `""` | Parameter group family, e.g. `redis7`, `valkey7`, `memcached1.6` |
| `parameters` | `list(map(string))` | `[]` | Engine parameters to set (`name`/`value` pairs) |
| `snapshot_retention_limit` | `number` | `null` | Days to retain automatic snapshots (Redis/Valkey) |
| `snapshot_window` | `string` | `null` | Daily UTC window for automatic snapshots |
| `final_snapshot_identifier` | `string` | `null` | Name of the final snapshot taken before deletion |
| `maintenance_window` | `string` | `null` | Weekly maintenance window, format `ddd:hh24:mi-ddd:hh24:mi` |
| `log_delivery_configuration` | `any` | slow-log → CloudWatch, JSON | Slow-log/engine-log delivery to CloudWatch Logs or Kinesis Data Firehose |
| `data_tiering_enabled` | `bool` | `null` | Enable data tiering (`r6gd` node types only) |
| `apply_immediately` | `bool` | `null` | Apply changes immediately instead of during the maintenance window |
| `global_replication_group_id_suffix` | `string` | `null` | Suffix used when creating a new Global Datastore ID |
| `tags` | `map(string)` | `{}` | Tags applied to all created resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cluster_arn` | ARN of the ElastiCache standalone cluster |
| `cluster_engine_version_actual` | Actual running engine version (may differ from requested minor/patch) |
| `cluster_cache_nodes` | List of node objects (`id`, `address`, `port`, `availability_zone`) |
| `cluster_address` | DNS name without port (Memcached only) |
| `cluster_configuration_endpoint` | Configuration endpoint for auto-discovery (Memcached only) |
| `replication_group_arn` | ARN of the replication group |
| `replication_group_id` | Identifier of the replication group |
| `replication_group_engine_version_actual` | Actual running engine version of the replication group |
| `replication_group_primary_endpoint_address` | Primary node endpoint address (cluster mode disabled) |
| `replication_group_reader_endpoint_address` | Reader endpoint address (cluster mode disabled) |
| `replication_group_configuration_endpoint_address` | Configuration endpoint when cluster mode is enabled |
| `replication_group_port` | Port of the primary node |
| `replication_group_member_clusters` | Identifiers of all nodes in the replication group |
| `global_replication_group_id` | Identifier of the Global Replication Group (Global Datastore) |
| `global_replication_group_arn` | ARN of the Global Replication Group |
| `global_replication_group_node_groups` | Node groups (shards) on the global replication group |
| `parameter_group_arn` / `parameter_group_id` | ARN and name of the parameter group |
| `subnet_group_name` | Name of the ElastiCache subnet group |
| `security_group_arn` / `security_group_id` | ARN and ID of the module-created security group |
| `cloudwatch_log_groups` | Map of CloudWatch log groups created and their attributes |

### Usage Examples

#### Example 1: Memcached Cluster

```hcl
module "elasticache_memcached" {
  source = "terraform-aws-modules/elasticache/aws"

  cluster_id                = "example-memcached"
  create_cluster            = true
  create_replication_group  = false

  engine          = "memcached"
  engine_version  = "1.6.17"
  node_type       = "cache.t4g.small"
  num_cache_nodes = 2
  az_mode         = "cross-az"

  maintenance_window = "sun:05:00-sun:09:00"
  apply_immediately  = true

  # Security group (module creates and manages it)
  vpc_id = module.vpc.vpc_id
  security_group_rules = {
    ingress_vpc = {
      description = "VPC traffic"
      cidr_ipv4   = module.vpc.vpc_cidr_block
    }
  }

  # Subnet group
  subnet_ids = module.vpc.private_subnets

  # Parameter group
  create_parameter_group = true
  parameter_group_family = "memcached1.6"
  parameters = [
    {
      name  = "idle_timeout"
      value = 60
    }
  ]

  tags = {
    Environment = "dev"
  }
}
```

#### Example 2: Redis Replication Group with Multi-AZ

```hcl
module "elasticache_redis" {
  source = "terraform-aws-modules/elasticache/aws"

  replication_group_id = "example-redis-replication-group"
  description           = "Redis replication group with automatic failover"

  engine_version = "7.1"
  node_type      = "cache.r7g.large"

  # High availability
  multi_az_enabled           = true
  automatic_failover_enabled = true
  num_cache_clusters          = 3 # 1 primary + 2 replicas

  # Security
  transit_encryption_enabled = true
  auth_token                 = "PickSomethingMoreSecure123!"
  auth_token_update_strategy = "ROTATE"

  vpc_id = module.vpc.vpc_id
  security_group_rules = {
    ingress_vpc = {
      description = "VPC traffic"
      cidr_ipv4   = module.vpc.vpc_cidr_block
    }
  }

  # Subnet group
  subnet_ids = module.vpc.private_subnets

  # Parameter group
  create_parameter_group = true
  parameter_group_family = "redis7"
  parameters = [
    {
      name  = "latency-tracking"
      value = "yes"
    }
  ]

  # Backups
  snapshot_retention_limit  = 7
  snapshot_window           = "03:00-05:00"
  final_snapshot_identifier = "example-redis-final-snapshot"

  maintenance_window = "mon:05:00-mon:07:00"
  apply_immediately  = false

  tags = {
    Environment = "production"
    Application = "session-store"
  }
}
```

#### Example 3: Redis Cluster Mode (Sharded) for Horizontal Scaling

```hcl
module "elasticache_redis_cluster_mode" {
  source = "terraform-aws-modules/elasticache/aws"

  replication_group_id = "example-redis-cluster"
  description           = "Sharded Redis cluster for horizontal scaling"

  engine_version = "7.1"
  node_type      = "cache.r7g.xlarge"

  # Cluster mode (sharding)
  cluster_mode_enabled       = true
  num_node_groups            = 3 # 3 shards
  replicas_per_node_group    = 2 # 2 replicas per shard
  multi_az_enabled           = true
  automatic_failover_enabled = true

  transit_encryption_enabled = true
  kms_key_arn                = aws_kms_key.elasticache.arn

  vpc_id = module.vpc.vpc_id
  security_group_rules = {
    ingress_vpc = {
      description = "VPC traffic"
      cidr_ipv4   = module.vpc.vpc_cidr_block
    }
    # Allow inter-node traffic between shards/replicas
    ingress_self = {
      description                  = "Cluster inter-node traffic"
      referenced_security_group_id = "self"
    }
  }

  subnet_ids = module.vpc.private_subnets

  create_parameter_group = true
  parameter_group_family = "redis7"
  parameters = [
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

#### Example 4: Global Replication Group (Multi-Region)

```hcl
# Primary region
module "elasticache_global_primary" {
  source = "terraform-aws-modules/elasticache/aws"

  providers = { aws = aws.us_east_1 }

  replication_group_id                    = "global-redis-primary"
  create_primary_global_replication_group = true
  global_replication_group_id_suffix      = "global"

  engine_version = "7.1"
  node_type      = "cache.r7g.large"

  multi_az_enabled           = true
  automatic_failover_enabled = true
  replicas_per_node_group    = 2

  vpc_id     = module.vpc_primary.vpc_id
  subnet_ids = module.vpc_primary.private_subnets

  transit_encryption_enabled = true
  at_rest_encryption_enabled = true

  tags = {
    Environment = "production"
    Region      = "primary"
  }
}

# Secondary region
module "elasticache_global_secondary" {
  source = "terraform-aws-modules/elasticache/aws"

  providers = { aws = aws.eu_west_1 }

  replication_group_id                      = "global-redis-secondary"
  create_secondary_global_replication_group = true
  global_replication_group_id               = module.elasticache_global_primary.global_replication_group_id

  vpc_id     = module.vpc_secondary.vpc_id
  subnet_ids = module.vpc_secondary.private_subnets

  tags = {
    Environment = "production"
    Region      = "secondary"
  }
}
```

#### Example 5: Valkey Replication Group

```hcl
module "elasticache_valkey" {
  source = "terraform-aws-modules/elasticache/aws"

  replication_group_id = "example-valkey"
  description           = "Valkey (open-source Redis fork) replication group"

  engine         = "valkey"
  engine_version = "7.2"
  node_type      = "cache.t4g.small"

  transit_encryption_enabled = true
  auth_token                 = "PickSomethingMoreSecure123!"
  maintenance_window         = "sun:05:00-sun:09:00"
  apply_immediately          = true

  vpc_id = module.vpc.vpc_id
  security_group_rules = {
    ingress_vpc = {
      description = "VPC traffic"
      cidr_ipv4   = module.vpc.vpc_cidr_block
    }
  }

  subnet_ids = module.vpc.private_subnets

  create_parameter_group = true
  parameter_group_family = "valkey7"
  parameters = [
    {
      name  = "latency-tracking"
      value = "yes"
    }
  ]

  tags = {
    Environment = "production"
    Engine      = "valkey"
  }
}
```

## Best Practices

### Security and Access Control

1. **Keep Encryption Enabled**: `transit_encryption_enabled` and `at_rest_encryption_enabled` default to `true` — do not disable them for production deployments.
2. **Use a Customer-Managed KMS Key**: Set `kms_key_arn` (root module) / `kms_key_id` (serverless submodule) instead of relying on the AWS-owned default key when compliance requires key rotation control or auditability.
3. **Prefer User Groups Over a Shared AUTH Token**: Use the `user-group` submodule for per-application ACLs (`access_string`) rather than a single AUTH token shared by all clients.
4. **Rotate AUTH Tokens Safely**: If using `auth_token`, set `auth_token_update_strategy = "ROTATE"` and store the token in AWS Secrets Manager rather than plain Terraform variables.
5. **Migrate to TLS Without Downtime**: Use `transit_encryption_mode = "preferred"` first, update clients to use TLS, then switch to `"required"`.
6. **Restrict Security Group Ingress**: Scope `security_group_rules` to specific CIDR blocks or `referenced_security_group_id` values rather than broad VPC ranges.
7. **Deploy in Private Subnets**: Pass only private subnet IDs via `subnet_ids`; ElastiCache does not support public accessibility.

### High Availability and Disaster Recovery

1. **Enable Multi-AZ for Production**: Set `multi_az_enabled = true`, which also forces `automatic_failover_enabled = true`.
2. **Use Cluster Mode for Large Datasets**: Enable `cluster_mode_enabled` with multiple `num_node_groups` when a workload exceeds a single shard's memory/throughput.
3. **Add a Self-Referencing Ingress Rule in Cluster Mode**: Shards/replicas need to talk to each other; add `referenced_security_group_id = "self"` in `security_group_rules`.
4. **Use Global Replication Groups for DR**: Deploy a primary (`create_primary_global_replication_group`) and one or more secondaries (`create_secondary_global_replication_group`) across regions for cross-region failover.
5. **Set a Final Snapshot**: Always set `final_snapshot_identifier` so a backup is taken automatically before a Redis/Valkey resource is destroyed.
6. **Test Failover Regularly**: Validate automatic failover behavior in non-production environments before relying on it in an incident.

### Performance and Cost Optimization

1. **Choose Node Types by Workload**: `r7g`/`r6g` for memory-intensive workloads, `t4g` for dev/test and low-throughput caches.
2. **Use ElastiCache Serverless for Unpredictable Traffic**: The `serverless-cache` submodule avoids over-provisioning for spiky or unknown workloads.
3. **Tune Eviction Policy**: Set `maxmemory-policy` via `parameters` (e.g. `allkeys-lru` for pure caching, `noeviction` for data that must not be evicted).
4. **Use Data Tiering for Large, Cold Datasets**: `data_tiering_enabled = true` with `r6gd` node types moves infrequently accessed data to SSD to cut cost.
5. **Distribute Read Traffic**: Increase `num_cache_clusters` (non-cluster mode) or `replicas_per_node_group` (cluster mode) and read from the reader endpoint.
6. **Right-Size Snapshot Retention**: 7 days is typically sufficient; longer retention increases storage cost with diminishing recovery value.

### Operational Excellence

1. **Set `apply_immediately` Deliberately**: Leave it `false`/unset in production so parameter and node changes apply during the maintenance window, not immediately.
2. **Review the Default Slow-Log Delivery**: `log_delivery_configuration` auto-creates a CloudWatch log group for the slow log by default — set a `cloudwatch_log_group_retention_in_days` or disable it explicitly if that default doesn't fit your log-retention policy.
3. **Tag Consistently**: Apply `Environment`, `Application`, and `Owner` tags via `tags` for cost allocation and resource tracking.
4. **Document Parameter Group Customizations**: Record the rationale for non-default `parameters` values (eviction policy, timeouts, slowlog thresholds).
5. **Pin the Module Version**: Use `version = "~> 1.11"` to avoid unplanned upgrades; check the registry for the current patch release.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-elasticache
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/elasticache/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-elasticache/tree/master/examples
- **AWS ElastiCache Documentation**: https://docs.aws.amazon.com/elasticache/
- **ElastiCache for Redis/Valkey User Guide**: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/
- **ElastiCache for Memcached User Guide**: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/
- **ElastiCache Serverless**: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/WhatIs-Serverless.html
- **Global Datastore for Redis/Valkey**: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Redis-Global-Datastore.html
- **ElastiCache Best Practices**: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/BestPractices.html
- **Choosing Between Redis and Memcached**: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/SelectEngine.html
- **ElastiCache CloudWatch Metrics**: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/CacheMetrics.html
- **ElastiCache Pricing**: https://aws.amazon.com/elasticache/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Exactly One Creation Toggle**: Set exactly one of `create_cluster`, `create_replication_group` (default `true`), `create_primary_global_replication_group`, or `create_secondary_global_replication_group` to `true` per module call; standalone cluster creation requires explicitly setting `create_replication_group = false`.
2. **Variable Name Traps**: The engine tuning variable is `parameters` (a `list(map(string))`), **not** `parameter_group_parameters`. The root module's KMS variable is `kms_key_arn`; the `serverless-cache` submodule instead uses `kms_key_id` for the same purpose.
3. **Security Group Is Self-Managed**: Supply `vpc_id` + `security_group_rules` and the module creates and manages the security group; use `security_group_ids` only to attach additional, externally managed groups.
4. **Cluster Mode vs. Simple Replication**: `num_cache_clusters` (total nodes, non-cluster mode) and `num_node_groups`/`replicas_per_node_group` (cluster mode, sharded) are mutually exclusive — set `cluster_mode_enabled = true` before using `num_node_groups`.
5. **Encryption Defaults**: Both `transit_encryption_enabled` and `at_rest_encryption_enabled` default to `true`; `auth_token` requires `transit_encryption_enabled = true`.
6. **Slow-Log CloudWatch Delivery Is On by Default**: `log_delivery_configuration` defaults to a slow-log entry pointed at an auto-created CloudWatch log group — override or set to `{}` to disable if not wanted.
7. **Global Replication Group Wiring**: The primary sets `create_primary_global_replication_group = true`; secondaries set `create_secondary_global_replication_group = true` and reference `global_replication_group_id = module.<primary>.global_replication_group_id` in another AWS provider/region.
8. **Prefer `user-group` Submodule Over a Shared AUTH Token**: Associate via `user_group_ids` on the root module for auditable, per-application ACLs.
9. **Engine Coverage Differs by Submodule**: `serverless-cache` supports `redis`/`memcached` only (no Valkey); `user-group` currently only accepts `engine = "redis"` (applies to Valkey deployments too, since they share the Redis ACL model).
10. **Minimum Requirements**: Terraform `>= 1.0`, AWS provider `>= 5.93`, random provider `>= 3.0`.
