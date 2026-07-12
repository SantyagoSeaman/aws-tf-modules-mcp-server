# Terraform AWS MemoryDB Module

## Module Information

- **Module Name**: `memory-db`
- **Module ID**: `terraform-aws-modules/memory-db/aws`
- **Source**: `terraform-aws-modules/memory-db/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-memory-db
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/memory-db/aws/latest
- **Latest Version**: 3.2.0
- **Purpose**: Terraform module to create AWS MemoryDB resources including the cluster, users, ACL, parameter group, and subnet group
- **Service**: AWS MemoryDB (for Redis OSS and Valkey)
- **Category**: Database, In-Memory Database, Caching
- **Keywords**: memorydb, redis, valkey, in-memory-database, cluster, cache, acl, snapshot, tls, kms, high-availability, multi-az, shards, replicas, low-latency
- **Use For**: microservices primary datastore, real-time analytics, session storage, gaming leaderboards, financial transaction processing, IoT data ingestion, chat/pub-sub applications, ML feature stores

## Description

The AWS MemoryDB Terraform module deploys and manages Amazon MemoryDB resources: the cluster itself along with its users, access control list (ACL), parameter group, and subnet group. Amazon MemoryDB is a durable, in-memory database service that delivers microsecond read and single-digit-millisecond write latency, and it is designed to be used as a primary database rather than just a cache — data is replicated synchronously across multiple Availability Zones and persisted with a Multi-AZ transactional log, so applications no longer need a separate cache layer in front of a durable datastore. The service exposes Redis OSS-compatible and Valkey-compatible APIs, so existing Redis/Valkey clients and commands work without application changes.

The module exposes every resource as independently toggleable via `create`, `create_users`, `create_acl`, `create_parameter_group`, and `create_subnet_group` flags, so it can create all resources from scratch, reuse pre-existing ACLs/parameter groups/subnet groups, or be disabled entirely. It covers cluster topology (shards, replicas per shard, node type, data tiering), networking (VPC subnet groups, security groups, IPv4/IPv6/dual-stack addressing via `network_type`/`ip_discovery`, and AWS multi-region clusters via `multi_region_cluster_name`), and encryption (TLS in transit, KMS at rest). It also manages user authentication — password-based or IAM — and ACLs that bind users to the cluster, along with automated/manual snapshot configuration for backup and point-in-time restore.

This module is best suited for teams who want a declarative, reusable way to stand up production-grade MemoryDB clusters with sensible security defaults (TLS and ACL-gated access), fine-grained access control via Redis ACL access strings, and clean composition with other Terraform modules (VPC, security-group, KMS) through its rich set of outputs (endpoints, ARNs, IDs). Because it is a single root module with no submodules, all resources are provisioned together in one `module` block, keeping configuration and state simple for both small dev clusters and multi-shard, multi-AZ production deployments.

## Key Features

- **Cluster Management**: Create and configure MemoryDB clusters with customizable shard and replica-per-shard topology
- **Multi-Engine Support**: Compatible with both `redis` and `valkey` engines with independently configurable `engine_version`
- **User Management**: Define multiple users with password or IAM (`type = "iam"`) authentication, each with its own Redis ACL access string
- **Access Control Lists (ACLs)**: Bind module-managed and/or externally created users (`acl_user_names`) to the cluster's ACL
- **Parameter Groups**: Create custom parameter groups (or reference existing ones) to tune engine behavior
- **Subnet Groups**: Define VPC subnet groups for Multi-AZ node placement and network isolation
- **TLS + KMS Encryption**: In-transit encryption (`tls_enabled`, default `true`) and at-rest encryption via customer-managed KMS keys (`kms_key_arn`)
- **Snapshot Lifecycle**: Automated daily snapshots with configurable retention/window, manual snapshot restore (`snapshot_name`/`snapshot_arns`), and a final snapshot on deletion (`final_snapshot_name`)
- **Data Tiering**: Cost-optimized storage on `r6gd`/`r7gd` node types that automatically tiers cold data to SSD
- **Multi-Region Clusters**: Associate a cluster with an AWS multi-region datastore via `multi_region_cluster_name`
- **Dual-Stack / IPv6 Networking**: Configure `network_type` (`ipv4`, `ipv6`, `dual_stack`) and `ip_discovery` for IPv6-enabled VPCs
- **Conditional & Composable Creation**: Independent `create_*` flags let each resource type be created fresh or point at an existing one
- **Name Prefixing**: Optional `use_name_prefix` on the cluster, ACL, parameter group, and subnet group avoids naming collisions
- **Per-Resource Tagging**: Dedicated tag maps for the cluster, users, ACL, parameter group, and subnet group in addition to global `tags`
- **Maintenance Windows**: Weekly maintenance window plus `auto_minor_version_upgrade` for automated patching
- **SNS Notifications**: Optional `sns_topic_arn` for cluster event notifications
- **Region Override**: Per-resource `region` argument to manage resources in a region other than the provider default

## Main Use Cases

1. **Primary Database for Microservices**: Replace separate cache and database layers with a single durable in-memory database
2. **Real-Time Analytics**: Process and analyze streaming data with microsecond latency for instant insights
3. **Session Management**: Store user sessions with high availability and automatic failover
4. **Gaming Leaderboards**: Maintain real-time rankings and player state with low-latency sorted-set operations
5. **Financial Transactions**: Process high-frequency trading data and transaction records with strong consistency
6. **IoT Data Processing**: Ingest and process sensor data from millions of devices with sub-millisecond response
7. **Chat / Pub-Sub Applications**: Power real-time messaging with durable data structures and pub/sub
8. **Machine Learning Feature Stores**: Serve ML model features with ultra-low latency for real-time inference
9. **E-Commerce Platforms**: Manage shopping carts, inventory, and product catalogs with high performance
10. **Disaster Recovery**: Restore clusters from automated or manual snapshots, or replicate via multi-region clusters

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created - affects all resources |
| `region` | `string` | `null` | Region where this resource will be managed; defaults to the provider region |
| `name` | `string` | `""` | Cluster name - also default name used on other resources if not overridden |
| `use_name_prefix` | `bool` | `false` | Determines whether `name` is used as a prefix for the cluster |
| `description` | `string` | `null` | Description for the cluster. Defaults to "Managed by Terraform" |
| `engine` | `string` | `null` | Engine that runs on the nodes: `redis` or `valkey` |
| `engine_version` | `string` | `null` | Engine version for the cluster (downgrades are not supported) |
| `node_type` | `string` | `null` | Compute/memory capacity of the nodes (e.g. `db.r7g.large`, `db.r6gd.xlarge` for data tiering) |
| `num_shards` | `number` | `null` | Number of shards in the cluster. Defaults to `1` |
| `num_replicas_per_shard` | `number` | `null` | Replicas per shard, up to 5. Defaults to `1` (2 nodes per shard) |
| `port` | `number` | `null` | Port on which nodes accept connections. Defaults to `6379` |
| `data_tiering` | `bool` | `null` | Must be `true` when using a data-tiering node type (`r6gd`/`r7gd`) |
| `auto_minor_version_upgrade` | `bool` | `null` | Automatically apply minor engine upgrades after launch. Defaults to `true` |
| `multi_region_cluster_name` | `string` | `null` | Multi region cluster identifier if this cluster is part of one |
| `network_type` | `string` | `null` | IP address type for the cluster: `ipv4`, `ipv6`, `dual_stack`. Defaults to `ipv4` |
| `ip_discovery` | `string` | `null` | IP discovery mechanism: `ipv4` or `ipv6`; requires `network_type` of `ipv6`/`dual_stack` for `ipv6` |
| `security_group_ids` | `list(string)` | `null` | VPC security group IDs to associate with the cluster |
| `tls_enabled` | `bool` | `null` | Enable in-transit (TLS) encryption. When `false`, `acl_name` must be `open-access`. Defaults to `true` |
| `kms_key_arn` | `string` | `null` | ARN of the KMS key used to encrypt data at rest |
| `maintenance_window` | `string` | `null` | Weekly maintenance window, format `ddd:hh24:mi-ddd:hh24:mi` |
| `sns_topic_arn` | `string` | `null` | ARN of the SNS topic for cluster event notifications |
| `snapshot_name` | `string` | `null` | Name of an existing snapshot to restore data from into the new cluster |
| `snapshot_arns` | `list(string)` | `null` | S3 object ARNs of RDB snapshot files used to populate the new cluster |
| `snapshot_retention_limit` | `number` | `null` | Days to retain automatic snapshots. `0` disables automatic backups; defaults to `0` |
| `snapshot_window` | `string` | `null` | Daily UTC time range for automatic snapshots, e.g. `05:00-09:00` |
| `final_snapshot_name` | `string` | `null` | Name of the final snapshot taken when the cluster is deleted |
| `create_users` | `bool` | `true` | Determines whether the users in `users` are created |
| `users` | `map(object)` | `{}` | Map of user definitions: `user_name`, `access_string`, `type` (`"password"` or `"iam"`), `passwords`, `tags` |
| `create_acl` | `bool` | `true` | Determines whether an ACL is created (vs. referencing an existing one via `acl_name`) |
| `acl_name` | `string` | `null` | Name of the ACL to create, or of an existing ACL when `create_acl = false` |
| `acl_use_name_prefix` | `bool` | `false` | Determines whether `acl_name` is used as a prefix |
| `acl_user_names` | `list(string)` | `[]` | Externally created user names to associate with the ACL (merged with `users`) |
| `create_parameter_group` | `bool` | `true` | Determines whether a parameter group is created (vs. referencing an existing one) |
| `parameter_group_name` | `string` | `null` | Name of the parameter group to create, or of an existing one when `create_parameter_group = false` |
| `parameter_group_family` | `string` | `null` | Engine version family the parameter group applies to, e.g. `memorydb_redis7`, `memorydb_valkey7` |
| `parameter_group_parameters` | `list(map(string))` | `[]` | List of `{ name, value }` parameter overrides to apply |
| `create_subnet_group` | `bool` | `true` | Determines whether a subnet group is created (vs. referencing an existing one) |
| `subnet_group_name` | `string` | `null` | Name of the subnet group to create, or of an existing one when `create_subnet_group = false` |
| `subnet_ids` | `list(string)` | `[]` | VPC subnet IDs for the subnet group; at least one subnet must be provided |
| `tags` | `map(string)` | `{}` | Tags applied to all resources created by the module |

## Main Outputs

| Output | Description |
|--------|-------------|
| `cluster_id` | Cluster name |
| `cluster_arn` | ARN of the cluster |
| `cluster_endpoint_address` | DNS hostname of the cluster configuration endpoint |
| `cluster_endpoint_port` | Port number the cluster configuration endpoint listens on |
| `cluster_engine_patch_version` | Patch version of the engine used by the cluster |
| `cluster_shards` | Set of shards in the cluster |
| `users` | Map of attributes for the users created (sensitive) |
| `acl_id` | Name of the ACL |
| `acl_arn` | ARN of the ACL |
| `acl_minimum_engine_version` | Minimum engine version supported by the ACL |
| `parameter_group_id` | Name of the parameter group |
| `parameter_group_arn` | ARN of the parameter group |
| `subnet_group_id` | Name of the subnet group |
| `subnet_group_arn` | ARN of the subnet group |
| `subnet_group_vpc_id` | VPC in which the subnet group exists |

## Usage Examples

### Example 1: Basic Redis Cluster

```hcl
module "memory_db" {
  source = "terraform-aws-modules/memory-db/aws"

  name        = "my-redis-cluster"
  description = "Basic MemoryDB cluster for development"

  engine         = "redis"
  engine_version = "7.0"
  node_type      = "db.t4g.small"

  num_shards             = 1
  num_replicas_per_shard = 1

  subnet_ids         = module.vpc.database_subnets
  security_group_ids = [module.redis_sg.security_group_id]

  tls_enabled = true

  users = {
    admin = {
      user_name     = "admin-user"
      access_string = "on ~* &* +@all"
      passwords     = [random_password.admin.result]
    }
  }

  tags = {
    Environment = "development"
  }
}

resource "random_password" "admin" {
  length  = 32
  special = true
}
```

### Example 2: Production Cluster with IAM Admin, Password Users, and Custom Sub-Resources

```hcl
module "memory_db" {
  source = "terraform-aws-modules/memory-db/aws"

  # Cluster
  name        = "prod-redis"
  description = "Production MemoryDB cluster"

  engine                     = "redis"
  engine_version             = "7.0"
  auto_minor_version_upgrade = true
  node_type                  = "db.r7g.xlarge"
  num_shards                 = 3
  num_replicas_per_shard     = 2

  tls_enabled         = true
  kms_key_arn         = module.kms.key_arn
  security_group_ids  = [module.redis_sg.security_group_id]
  maintenance_window  = "sun:23:00-mon:01:30"
  sns_topic_arn       = aws_sns_topic.memorydb_events.arn

  snapshot_retention_limit = 7
  snapshot_window          = "05:00-09:00"
  final_snapshot_name      = "prod-redis-final-snapshot"

  # Users - IAM auth for admins, password auth for app/readonly
  users = {
    admin = {
      user_name     = "admin-user"
      access_string = "on ~* &* +@all"
      type          = "iam"
      tags          = { Role = "admin" }
    }
    app = {
      user_name     = "app-user"
      access_string = "on ~app:* -@all +@read +@hash +@bitmap +@geo -@dangerous"
      passwords     = [random_password.app.result]
      tags          = { Role = "application" }
    }
    readonly = {
      user_name     = "readonly-user"
      access_string = "on ~* -@all +@read"
      passwords     = [random_password.readonly.result]
      tags          = { Role = "readonly" }
    }
  }

  # ACL
  acl_name = "prod-acl"
  acl_tags = { Component = "acl" }

  # Parameter group
  parameter_group_name        = "prod-param-group"
  parameter_group_description = "Production MemoryDB parameter group"
  parameter_group_family      = "memorydb_redis7"
  parameter_group_parameters = [
    {
      name  = "maxmemory-policy"
      value = "allkeys-lru"
    }
  ]

  # Subnet group
  subnet_group_name = "prod-subnet-group"
  subnet_ids         = module.vpc.database_subnets

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

resource "random_password" "app" {
  length  = 32
  special = true
}

resource "random_password" "readonly" {
  length  = 32
  special = true
}

resource "aws_sns_topic" "memorydb_events" {
  name = "prod-redis-events"
}
```

### Example 3: Valkey Cluster with Data Tiering

```hcl
module "memory_db" {
  source = "terraform-aws-modules/memory-db/aws"

  name        = "valkey-cluster"
  description = "MemoryDB cluster using the Valkey engine with data tiering"

  engine         = "valkey"
  engine_version = "7.3"
  node_type      = "db.r6gd.xlarge" # r6gd/r7gd required for data tiering
  data_tiering   = true

  num_shards             = 2
  num_replicas_per_shard = 2

  tls_enabled         = true
  subnet_ids          = module.vpc.database_subnets
  security_group_ids  = [module.valkey_sg.security_group_id]

  snapshot_retention_limit = 14
  snapshot_window          = "03:00-05:00"

  parameter_group_family = "memorydb_valkey7"

  tags = {
    Engine      = "valkey"
    Environment = "production"
  }
}
```

### Example 4: Cluster Restored From Snapshot

```hcl
module "memory_db" {
  source = "terraform-aws-modules/memory-db/aws"

  name        = "restored-cluster"
  description = "Cluster restored from an existing snapshot"

  engine         = "redis"
  engine_version = "7.0"
  node_type      = "db.r7g.large"

  # Restore from a named automatic/manual snapshot
  snapshot_name = "my-cluster-backup-2026-06-01"

  subnet_ids          = module.vpc.database_subnets
  security_group_ids  = [module.redis_sg.security_group_id]

  tls_enabled = true

  tags = {
    Environment = "recovery"
    Purpose     = "dr-test"
  }
}
```

### Example 5: Using Existing ACL, Parameter Group, and Subnet Group

```hcl
module "memory_db" {
  source = "terraform-aws-modules/memory-db/aws"

  name        = "existing-resources-cluster"
  description = "Cluster referencing pre-existing sub-resources"

  engine         = "redis"
  engine_version = "7.0"
  node_type      = "db.t4g.medium"

  num_shards             = 1
  num_replicas_per_shard = 1

  # Reference existing resources instead of creating new ones
  create_subnet_group  = false
  subnet_group_name    = "existing-subnet-group"

  create_parameter_group = false
  parameter_group_name   = "existing-parameter-group"

  create_acl = false
  acl_name   = "existing-acl"

  create_users = false

  security_group_ids = [data.aws_security_group.existing.id]

  tls_enabled = true

  tags = {
    Environment = "testing"
  }
}
```

## Best Practices

### Cluster Design and Sizing

1. **Choose Appropriate Node Types**: Use `r7g`/`r6g` for memory-intensive production workloads, `t4g` for development and low-traffic use cases, `r6gd`/`r7gd` when data tiering is required.
2. **Plan Shard Count**: Start with `num_shards = 1` and scale horizontally as data grows.
3. **Configure Replicas for HA**: Use at least 1 replica per shard (2 recommended for critical workloads) via `num_replicas_per_shard`.
4. **Enable Data Tiering for Large Datasets**: Set `data_tiering = true` with an `r6gd`/`r7gd` node type to move cold data to SSD and reduce memory costs.
5. **Distribute Across AZs**: Provide `subnet_ids` spanning at least 2 (preferably 3) Availability Zones; MemoryDB places shards/replicas across them automatically.
6. **Plan for Multi-Region**: Use `multi_region_cluster_name` when the cluster must participate in an AWS multi-region datastore for cross-region durability.

### Security and Access Control

1. **Keep TLS Enabled**: `tls_enabled` defaults to `true`; do not disable it for production. When disabled, `acl_name` must be `"open-access"`.
2. **Use KMS for Data at Rest**: Set `kms_key_arn` to a customer-managed key for encryption-at-rest and key-rotation control.
3. **Prefer IAM Authentication**: Set `type = "iam"` on users where possible to avoid managing long-lived passwords; use password auth only where IAM auth isn't viable.
4. **Store Passwords Securely**: Never hardcode passwords; generate with `random_password` or source from AWS Secrets Manager.
5. **Implement Least Privilege via ACL Access Strings**: Grant only the required command categories/key patterns, e.g. `on ~app:* -@all +@read +@hash -@dangerous`.
6. **Restrict Network Access**: Scope `security_group_ids` to application subnets only; never expose the cluster broadly.
7. **Separate Admin, Application, and Read-Only Users**: Define distinct `users` entries per role instead of sharing one super-user credential.

### Backup and Recovery

1. **Enable Automated Snapshots**: `snapshot_retention_limit` defaults to `0` (disabled) — explicitly set it (7-30 days) to enable automatic backups.
2. **Schedule Snapshot Windows**: Choose `snapshot_window` during low-traffic periods to minimize performance impact.
3. **Take a Final Snapshot Before Deletion**: Set `final_snapshot_name` so a backup is created automatically when the cluster is destroyed.
4. **Test Restore Procedures**: Periodically restore `snapshot_name`/`snapshot_arns` into a test cluster to validate backup integrity and recovery time.

### Performance Optimization

1. **Tune Parameter Groups**: Set `maxmemory-policy` appropriately for the workload (e.g. `allkeys-lru` for caching, `noeviction` for durable-database use).
2. **Match `parameter_group_family` to the Engine Version**: e.g. `memorydb_redis7` for Redis 7.x, `memorydb_valkey7` for Valkey 7.x.
3. **Distribute Reads Across Replicas**: Point read-heavy traffic at replica endpoints; writes always go to the shard primary.
4. **Monitor Latency Metrics**: Track `CommandLatency`/`SuccessfulReadRequestLatency` in CloudWatch and investigate sustained spikes.

### Operational Excellence

1. **Schedule Maintenance Windows**: Set `maintenance_window` during low-traffic periods for non-disruptive updates.
2. **Enable Auto Minor Version Upgrades**: `auto_minor_version_upgrade` defaults to `true`, applying security patches automatically; explicitly set `false` only when strict change control is required.
3. **Tag Consistently**: Use the global `tags` plus resource-specific tag maps (`acl_tags`, `parameter_group_tags`, `subnet_group_tags`, per-user `tags`) for cost allocation and ownership tracking.
4. **Notify on Cluster Events**: Set `sns_topic_arn` to route cluster events to an operations topic.
5. **Use Conditional Creation for Shared Resources**: Set the relevant `create_*` flag to `false` and pass the existing resource name when a parameter group, subnet group, or ACL is managed outside this module instance.
6. **Version-Pin the Module**: Pin `version` in the module block (e.g. `~> 3.0`) and review the CHANGELOG before upgrading, since some releases (e.g. `3.0.0`) bump minimum provider/Terraform versions as breaking changes.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-memory-db
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/memory-db/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-memory-db/tree/master/examples
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-memory-db/blob/master/CHANGELOG.md
- **AWS MemoryDB Documentation**: https://docs.aws.amazon.com/memorydb/latest/devguide/what-is-memorydb-for-redis.html
- **AWS MemoryDB Node Types**: https://docs.aws.amazon.com/memorydb/latest/devguide/nodes.supportedtypes.html
- **AWS MemoryDB Security**: https://docs.aws.amazon.com/memorydb/latest/devguide/memorydb-security.html
- **Redis ACL Documentation**: https://redis.io/docs/management/security/acl/
- **Valkey Documentation**: https://valkey.io/documentation/
- **AWS MemoryDB Pricing**: https://aws.amazon.com/memorydb/pricing/
- **AWS MemoryDB FAQs**: https://aws.amazon.com/memorydb/faqs/

## Notes for AI Agents

When using this module in automated workflows:

1. **Standalone Root Module**: This module has no submodules — cluster, users, ACL, parameter group, and subnet group are all managed from a single `module` block.
2. **Minimum Versions**: Requires Terraform >= 1.5.7 and AWS provider >= 6.34; pin `version = "~> 3.0"` (or later) on the module itself.
3. **Engine Selection**: `engine` must be `"redis"` or `"valkey"`; `engine_version` must be a version supported for that engine, and downgrades are not supported.
4. **Shard/Replica Planning**: `num_shards` drives horizontal scale; `num_replicas_per_shard` (up to 5) drives read capacity and availability — use at least 1 for production.
5. **Subnets Required**: `subnet_ids` defaults to `[]` but at least one subnet is required; provide subnets spanning multiple AZs.
6. **User Authentication Modes**: `users[*].type` is `"password"` (default, requires `passwords`) or `"iam"` (no `passwords` needed) — prefer IAM where the client supports it.
7. **ACL Dependencies**: `acl_user_names` and module-managed `users` are merged onto the ACL; ensure any externally referenced user names already exist.
8. **TLS/ACL Coupling**: If `tls_enabled = false`, `acl_name` must be `"open-access"` — do not combine disabled TLS with a custom ACL.
9. **Data Tiering Requires Compatible Node Types**: `data_tiering = true` is only valid on `r6gd`/`r7gd` node types.
10. **Snapshots Disabled by Default**: `snapshot_retention_limit` defaults to `0`; set it explicitly to enable automated backups.
11. **Conditional Creation for Existing Resources**: When pointing at pre-existing ACL/parameter group/subnet group, set the matching `create_*` flag to `false` and pass the existing resource name — do not leave `create_*` at its default `true`.
12. **Dual-Stack/IPv6 Networking**: To use IPv6, set `network_type` to `ipv6` or `dual_stack` before setting `ip_discovery = "ipv6"`.
13. **Port Default**: Default port is `6379`; if changed, update both `security_group_ids` rules and client configuration accordingly.
14. **Sensitive Output**: The `users` output contains authentication details and is marked `sensitive`; handle it accordingly in downstream modules/state.
