# Terraform AWS MemoryDB Module

## Module Information

- **Module Name**: `memory-db`
- **Source**: `terraform-aws-modules/memory-db/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-memory-db
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/memory-db/aws/latest
- **Latest Version**: 3.1.0
- **Purpose**: Terraform module to create AWS MemoryDB resources including clusters, users, ACLs, parameter groups, and subnet groups
- **Service**: AWS MemoryDB for Redis and Valkey
- **Category**: Database, In-Memory Database, Caching
- **Keywords**: memorydb, redis, valkey, in-memory-database, cluster, cache, high-availability, encryption, acl, snapshot, multi-az, shards, replicas, tls, kms, low-latency
- **Use For**: microservices primary database, real-time analytics, session storage, gaming leaderboards, financial transactions, IoT data processing, chat applications, ML feature stores

## Description

The AWS MemoryDB Terraform module provides a complete solution for creating and managing MemoryDB resources on AWS. Amazon MemoryDB is a durable, in-memory database service that delivers ultra-fast performance with microsecond read and single-digit millisecond write latency, making it ideal for modern microservices architectures. Unlike traditional caching solutions, MemoryDB can serve as a primary database with Multi-AZ data durability, eliminating the need to manage separate cache and database layers. The service is compatible with Redis OSS and Valkey APIs, allowing seamless migration of existing Redis applications without code changes.

This module simplifies the deployment and management of MemoryDB clusters by providing declarative configuration for cluster topology, user management, access control lists (ACLs), parameter groups, and subnet groups. It handles essential operational concerns including TLS encryption for data in transit, KMS encryption for data at rest, automated snapshots for backup and recovery, and maintenance window scheduling. The module supports flexible cluster configurations with customizable shard and replica counts for horizontal scaling, data tiering for cost optimization, and multi-AZ deployment for high availability and durability.

The module's design enables conditional resource creation, allowing users to manage existing resources or selectively provision components as needed. With built-in support for multiple users with different access levels, security group integration, and comprehensive tagging, this module provides enterprise-ready MemoryDB deployments following AWS best practices. The module outputs cluster endpoints, ARNs, and detailed resource information for integration with other infrastructure components, making it suitable for both simple development environments and complex production architectures requiring low-latency data access with strong consistency guarantees.

## Key Features

- **Cluster Management**: Create and configure MemoryDB clusters with customizable shard and replica topology
- **Multi-Engine Support**: Compatible with both Redis and Valkey engines with configurable versions
- **User Management**: Define multiple users with different access levels, passwords, and authentication methods
- **Access Control Lists (ACLs)**: Configure fine-grained access control with user associations and permissions
- **Parameter Groups**: Create custom parameter groups to tune engine behavior and performance characteristics
- **Subnet Groups**: Define VPC subnet groups for Multi-AZ deployment and network isolation
- **TLS Encryption**: Enable in-transit encryption for secure communication between clients and cluster nodes
- **KMS Encryption**: Configure encryption at rest using AWS KMS for data protection compliance
- **Automated Snapshots**: Schedule automatic backups with configurable retention periods and snapshot windows
- **Manual Snapshots**: Support for creating snapshots from specific points in time for disaster recovery
- **Snapshot Restore**: Initialize clusters from existing snapshots for cloning or recovery scenarios
- **Data Tiering**: Enable cost-effective storage with automatic data tiering between memory and SSD
- **Maintenance Windows**: Define preferred maintenance windows to control when updates are applied
- **Security Group Integration**: Associate VPC security groups to control inbound and outbound traffic
- **Multi-AZ Durability**: Automatic data replication across multiple Availability Zones for fault tolerance
- **Conditional Creation**: Flexible flags to selectively create or skip individual resource components
- **Comprehensive Tagging**: Apply tags across all resources for cost allocation and resource organization
- **SNS Notifications**: Configure SNS topic for cluster event notifications

## Compatibility

- **Terraform**: >= 1.5.7
- **AWS Provider**: >= 6.28
- **Submodules**: None (standalone root module)

## Main Use Cases

1. **Primary Database for Microservices**: Replace separate cache and database layers with single durable in-memory database
2. **Real-Time Analytics**: Process and analyze streaming data with microsecond latency for instant insights
3. **Session Management**: Store user sessions with high availability and automatic failover capabilities
4. **Gaming Leaderboards**: Maintain real-time rankings and player state with low-latency sorted set operations
5. **Financial Transactions**: Process high-frequency trading data and transaction records with strong consistency
6. **IoT Data Processing**: Ingest and process sensor data from millions of devices with sub-millisecond response
7. **Chat Applications**: Power real-time messaging with durable message queues and pub/sub capabilities
8. **Machine Learning Features**: Serve ML model features with ultra-low latency for real-time inference
9. **E-Commerce Platforms**: Manage shopping carts, inventory, and product catalogs with high performance
10. **Location Services**: Store and query geospatial data for ride-sharing, delivery, and navigation applications

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `name` | `string` | `""` | Name of the cluster |
| `use_name_prefix` | `bool` | `false` | Determines whether name is used as a prefix |
| `description` | `string` | `null` | Description of the cluster |
| `engine` | `string` | `null` | Name of the database engine (redis or valkey) |
| `engine_version` | `string` | `null` | Version number of the database engine |
| `node_type` | `string` | `null` | Compute and memory capacity of the nodes |
| `num_shards` | `number` | `null` | Number of shards in the cluster |
| `num_replicas_per_shard` | `number` | `null` | Number of replicas to apply to each shard |
| `port` | `number` | `null` | Port number on which cluster accepts connections |
| `parameter_group_name` | `string` | `null` | Name of the parameter group to associate |
| `security_group_ids` | `list(string)` | `null` | Set of VPC Security Group IDs to associate |
| `subnet_ids` | `list(string)` | `null` | Set of VPC Subnet IDs for the subnet group |
| `kms_key_arn` | `string` | `null` | ARN of the KMS key used to encrypt data at rest |
| `tls_enabled` | `bool` | `null` | Enable in-transit encryption |
| `maintenance_window` | `string` | `null` | Weekly time range for system maintenance |
| `snapshot_name` | `string` | `null` | Name of snapshot from which to restore data |
| `snapshot_arns` | `list(string)` | `null` | List of ARN-s identifying S3 objects with cluster data |
| `snapshot_retention_limit` | `number` | `null` | Number of days for which MemoryDB retains automatic snapshots |
| `snapshot_window` | `string` | `null` | Daily time range during which automated snapshots are created |
| `final_snapshot_name` | `string` | `null` | Name of the final cluster snapshot |
| `data_tiering` | `bool` | `null` | Enables data tiering for the cluster |
| `auto_minor_version_upgrade` | `bool` | `null` | When true, minor engine upgrades will be applied automatically |
| `sns_topic_arn` | `string` | `null` | ARN of SNS topic for cluster notifications |
| `create_users` | `bool` | `true` | Determines whether users will be created |
| `users` | `any` | `{}` | Map of users to create |
| `create_acl` | `bool` | `true` | Determines whether an ACL will be created |
| `acl_name` | `string` | `null` | Name of the ACL |
| `acl_user_names` | `list(string)` | `[]` | List of user names associated with the ACL |
| `create_parameter_group` | `bool` | `true` | Determines whether a parameter group will be created |
| `parameter_group_family` | `string` | `null` | Engine version for the parameter group |
| `parameter_group_parameters` | `list(map(string))` | `[]` | List of parameters to apply |
| `create_subnet_group` | `bool` | `true` | Determines whether a subnet group will be created |
| `tags` | `map(string)` | `{}` | Map of tags to assign to all created resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `cluster_id` | Name of the cluster |
| `cluster_arn` | ARN of the cluster |
| `cluster_endpoint_address` | DNS hostname of the cluster configuration endpoint |
| `cluster_endpoint_port` | Port number that the cluster configuration endpoint is listening on |
| `cluster_engine_patch_version` | Patch version number of the engine used by the cluster |
| `cluster_shards` | Set of shards in this cluster |
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

### Example 1: Basic MemoryDB Cluster

```hcl
module "memorydb_basic" {
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

  tags = {
    Environment = "development"
    Application = "cache"
  }
}
```

### Example 2: Production Cluster with Multiple Users

```hcl
module "memorydb_production" {
  source = "terraform-aws-modules/memory-db/aws"

  name        = "prod-redis"
  description = "Production MemoryDB cluster"

  engine         = "redis"
  engine_version = "7.0"
  node_type      = "db.r6gd.xlarge"

  num_shards             = 3
  num_replicas_per_shard = 2

  # Enable data tiering for cost optimization
  data_tiering = true

  # Encryption
  tls_enabled = true
  kms_key_arn = module.kms.key_arn

  # Backup configuration
  snapshot_retention_limit = 7
  snapshot_window          = "05:00-09:00"
  maintenance_window       = "sun:23:00-mon:01:30"

  # Networking
  subnet_ids         = module.vpc.database_subnets
  security_group_ids = [module.redis_sg.security_group_id]

  # User management
  users = {
    admin = {
      user_name     = "admin-user"
      access_string = "on ~* &* +@all"
      passwords     = [random_password.admin.result]

      tags = {
        Role = "admin"
      }
    }
    app = {
      user_name     = "app-user"
      access_string = "on ~app:* -@all +@read +@hash +@bitmap +@geo -@dangerous"
      passwords     = [random_password.app.result]

      tags = {
        Role = "application"
      }
    }
    readonly = {
      user_name     = "readonly-user"
      access_string = "on ~* -@all +@read"
      passwords     = [random_password.readonly.result]

      tags = {
        Role = "readonly"
      }
    }
  }

  # ACL configuration
  acl_name       = "prod-acl"
  acl_user_names = ["admin-user", "app-user", "readonly-user"]

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

resource "random_password" "admin" {
  length  = 32
  special = true
}

resource "random_password" "app" {
  length  = 32
  special = true
}

resource "random_password" "readonly" {
  length  = 32
  special = true
}
```

### Example 3: Cluster with Custom Parameters

```hcl
module "memorydb_custom" {
  source = "terraform-aws-modules/memory-db/aws"

  name        = "custom-redis"
  description = "MemoryDB cluster with custom parameters"

  engine         = "redis"
  engine_version = "7.0"
  node_type      = "db.r6g.large"

  num_shards             = 2
  num_replicas_per_shard = 1

  subnet_ids         = module.vpc.database_subnets
  security_group_ids = [module.redis_sg.security_group_id]

  # Custom parameter group
  create_parameter_group  = true
  parameter_group_family  = "memorydb_redis7"
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
      name  = "activedefrag"
      value = "yes"
    }
  ]

  tls_enabled = true

  tags = {
    Environment = "staging"
  }
}
```

### Example 4: Cluster Restored from Snapshot

```hcl
module "memorydb_restored" {
  source = "terraform-aws-modules/memory-db/aws"

  name        = "restored-cluster"
  description = "Cluster restored from snapshot"

  engine         = "redis"
  engine_version = "7.0"
  node_type      = "db.r6g.large"

  # Restore from snapshot
  snapshot_name = "my-cluster-backup-2024-01-01"

  subnet_ids         = module.vpc.database_subnets
  security_group_ids = [module.redis_sg.security_group_id]

  tls_enabled = true

  tags = {
    Environment = "recovery"
    Purpose     = "dr-test"
  }
}
```

### Example 5: Valkey Cluster

```hcl
module "memorydb_valkey" {
  source = "terraform-aws-modules/memory-db/aws"

  name        = "valkey-cluster"
  description = "MemoryDB cluster using Valkey engine"

  engine         = "valkey"
  engine_version = "7.3"
  node_type      = "db.r7g.large"

  num_shards             = 2
  num_replicas_per_shard = 2

  subnet_ids         = module.vpc.database_subnets
  security_group_ids = [module.valkey_sg.security_group_id]

  tls_enabled = true

  # Snapshot configuration
  snapshot_retention_limit = 14
  snapshot_window          = "03:00-05:00"

  # Automatic minor version upgrades
  auto_minor_version_upgrade = true

  tags = {
    Engine      = "valkey"
    Environment = "production"
  }
}
```

### Example 6: Using Existing Resources

```hcl
# Use existing subnet group and parameter group
module "memorydb_existing" {
  source = "terraform-aws-modules/memory-db/aws"

  name        = "existing-resources-cluster"
  description = "Cluster using existing subnet and parameter groups"

  engine         = "redis"
  engine_version = "7.0"
  node_type      = "db.t4g.medium"

  num_shards             = 1
  num_replicas_per_shard = 1

  # Use existing resources
  create_subnet_group   = false
  subnet_group_name     = "existing-subnet-group"

  create_parameter_group = false
  parameter_group_name   = "existing-parameter-group"

  create_acl        = false
  acl_name          = "existing-acl"

  create_users = false

  security_group_ids = [data.aws_security_group.existing.id]

  tls_enabled = true

  tags = {
    Environment = "testing"
  }
}
```

### Example 7: High Availability Cluster with Final Snapshot

```hcl
module "memorydb_ha" {
  source = "terraform-aws-modules/memory-db/aws"

  name        = "ha-redis-cluster"
  description = "High availability MemoryDB cluster"

  engine         = "redis"
  engine_version = "7.0"
  node_type      = "db.r6g.2xlarge"

  # Multi-shard, multi-replica configuration
  num_shards             = 5
  num_replicas_per_shard = 2

  data_tiering = true

  # Networking across multiple AZs
  subnet_ids         = module.vpc.database_subnets  # Subnets in 3 AZs
  security_group_ids = [module.redis_sg.security_group_id]

  # Encryption
  tls_enabled = true
  kms_key_arn = module.kms.key_arn

  # Backup and recovery
  snapshot_retention_limit = 30
  snapshot_window          = "03:00-05:00"
  final_snapshot_name      = "ha-cluster-final-snapshot"

  # Maintenance
  maintenance_window         = "sun:05:00-sun:07:00"
  auto_minor_version_upgrade = true

  # Users with different permissions
  users = {
    superuser = {
      user_name     = "superuser"
      access_string = "on ~* &* +@all"
      passwords     = [data.aws_secretsmanager_secret_version.superuser.secret_string]
    }
    application = {
      user_name     = "app"
      access_string = "on ~app:* -@all +@read +@write +@hash +@list +@set +@sortedset"
      passwords     = [data.aws_secretsmanager_secret_version.app.secret_string]
    }
  }

  acl_name       = "ha-acl"
  acl_user_names = ["superuser", "app"]

  tags = {
    Environment     = "production"
    HighAvailability = "true"
    Compliance      = "required"
  }
}
```

### Example 8: Development Cluster with Minimal Configuration

```hcl
module "memorydb_dev" {
  source = "terraform-aws-modules/memory-db/aws"

  name = "dev-redis"

  engine         = "redis"
  engine_version = "7.0"
  node_type      = "db.t4g.small"

  num_shards             = 1
  num_replicas_per_shard = 0  # No replicas for dev

  subnet_ids         = module.vpc.database_subnets
  security_group_ids = [module.redis_sg.security_group_id]

  # Minimal snapshot retention for dev
  snapshot_retention_limit = 1

  # Single admin user
  users = {
    admin = {
      user_name     = "admin"
      access_string = "on ~* &* +@all"
      passwords     = ["DevPassword123!"]
    }
  }

  tls_enabled = false  # Disable TLS for dev environment

  tags = {
    Environment = "development"
    AutoDelete  = "true"
  }
}
```

## Best Practices

### Cluster Design and Sizing

1. **Choose Appropriate Node Types**: Use R6g/R7g instances for memory-intensive workloads, T4g for development and low-traffic applications
2. **Plan Shard Count**: Start with 1-2 shards and scale horizontally as data grows; each shard can handle ~1TB with data tiering
3. **Configure Replicas for HA**: Use at least 1 replica per shard (2 replicas recommended) for production to ensure high availability
4. **Enable Data Tiering**: For cost optimization with large datasets, enable data tiering to automatically move less-accessed data to SSD
5. **Calculate Memory Requirements**: Account for dataset size plus 20-25% overhead for replication, fragmentation, and operations
6. **Consider Multi-AZ Deployment**: Distribute shards across at least 2 (preferably 3) Availability Zones for fault tolerance
7. **Monitor Memory Usage**: Set up CloudWatch alarms for memory usage >80% to plan for capacity increases

### Security and Compliance

1. **Enable TLS Encryption**: Always set tls_enabled = true for production to encrypt data in transit
2. **Use KMS for Data at Rest**: Configure kms_key_arn with customer-managed CMKs for encryption at rest and key rotation control
3. **Implement Least Privilege Access**: Create users with minimal required permissions using Redis ACL access strings
4. **Store Passwords Securely**: Never hardcode passwords; use AWS Secrets Manager with automatic rotation
5. **Restrict Network Access**: Use security groups to allow access only from application subnets; never expose to 0.0.0.0/0
6. **Enable VPC Endpoints**: Use PrivateLink for secure access from VPCs without internet gateway traversal
7. **Audit Access Patterns**: Enable CloudWatch logging and use CloudTrail to track API calls for compliance
8. **Implement RBAC**: Use ACLs to define role-based access control with different users for admin, application, and read-only access
9. **Regular Security Reviews**: Periodically audit user permissions, security group rules, and encryption settings

### Backup and Recovery

1. **Configure Automated Snapshots**: Set snapshot_retention_limit to 7-30 days based on recovery point objectives (RPO)
2. **Schedule Snapshot Windows**: Choose snapshot_window during low-traffic periods to minimize performance impact
3. **Enable Final Snapshots**: Always configure final_snapshot_name to create backup before cluster deletion
4. **Test Recovery Procedures**: Regularly restore snapshots to test clusters to validate backup integrity and recovery time
5. **Use Cross-Region Snapshots**: For disaster recovery, copy snapshots to different regions using AWS Backup
6. **Document Backup Strategy**: Maintain runbooks for recovery scenarios including cluster recreation and data restoration
7. **Monitor Snapshot Success**: Create CloudWatch alarms for failed snapshots and investigate immediately

### Performance Optimization

1. **Tune Parameter Groups**: Customize maxmemory-policy based on use case (allkeys-lru for cache, noeviction for database)
2. **Enable Pipelining**: Configure clients to use pipelining for batching multiple commands and reducing round trips
3. **Optimize Connection Pooling**: Maintain persistent connection pools sized for concurrent application threads
4. **Use Read Replicas**: Distribute read traffic across replicas; write operations go to primary nodes only
5. **Monitor Latency Metrics**: Track CommandLatency and SuccessfulReadRequestLatency metrics; investigate spikes >5ms
6. **Minimize Large Keys**: Avoid storing values >100KB; split large objects into smaller keys for better distribution
7. **Implement Client-Side Caching**: Use Redis client libraries with local caching for frequently accessed immutable data
8. **Profile Commands**: Use SLOWLOG to identify slow commands and optimize application queries

### Cost Optimization

1. **Right-Size Node Types**: Start with smaller instances and scale based on actual metrics; avoid over-provisioning
2. **Use Burstable Instances**: Consider T4g instances for development and variable workloads to reduce costs
3. **Enable Data Tiering**: For datasets >100GB, enable data tiering to reduce memory costs by up to 60%
4. **Optimize Replica Count**: Balance high availability needs with cost; 1 replica may be sufficient for non-critical workloads
5. **Clean Up Development Clusters**: Implement automated deletion of dev/test clusters outside business hours
6. **Monitor Reserved Capacity**: For long-running production clusters, consider reserved capacity for 30-50% cost savings
7. **Review Snapshot Retention**: Limit snapshot_retention_limit to actual recovery needs; longer retention increases storage costs
8. **Use Spot Instances**: Not applicable for MemoryDB; consider ElastiCache with spot instances for non-durable caching

### High Availability and Disaster Recovery

1. **Deploy Multi-AZ**: Always distribute replicas across multiple Availability Zones for automatic failover
2. **Plan for Shard Failures**: Understand that replica promotion is automatic; applications should handle brief connection interruptions
3. **Implement Client Retry Logic**: Configure exponential backoff for connection failures during failover events (typically 10-30 seconds)
4. **Monitor Node Health**: Track CPUUtilization, NetworkBytesIn/Out, and DatabaseMemoryUsagePercentage for anomaly detection
5. **Test Failover Scenarios**: Periodically simulate node failures in non-production to validate application resilience
6. **Document RTO/RPO**: Establish recovery time objectives (RTO: <1 minute for failover) and recovery point objectives (RPO: 0 for replicas)
7. **Use Health Checks**: Implement application-level health checks to verify cluster connectivity before processing requests

### Operational Excellence

1. **Schedule Maintenance Windows**: Define maintenance_window during low-traffic periods for non-disruptive updates
2. **Enable Auto Minor Upgrades**: Set auto_minor_version_upgrade = true for automatic security patches
3. **Implement Comprehensive Tagging**: Apply tags for Environment, Team, CostCenter, Application for organization and cost tracking
4. **Use Infrastructure as Code**: Manage all MemoryDB resources through Terraform for reproducibility and version control
5. **Monitor Key Metrics**: Track EngineCPUUtilization, DatabaseMemoryUsagePercentage, CommandsProcessed, and latency metrics
6. **Set Up Alerting**: Create CloudWatch alarms for critical metrics with SNS notifications to operations teams
7. **Document Cluster Architecture**: Maintain diagrams showing shard distribution, replica placement, and application connectivity
8. **Plan Capacity Growth**: Review usage trends monthly and plan shard additions before reaching 70% memory utilization
9. **Implement Change Management**: Use Terraform plan to preview changes; test in staging before production deployments

### User and Access Management

1. **Create Role-Based Users**: Define separate users for admin, application, read-only, and monitoring with appropriate access strings
2. **Use Descriptive User Names**: Name users clearly (e.g., "app-service", "analytics-readonly") for easier access auditing
3. **Rotate Passwords Regularly**: Implement 90-day password rotation policy using Secrets Manager
4. **Limit Super Users**: Minimize users with +@all permissions; most applications should have restricted command sets
5. **Test Access Strings**: Validate ACL access strings in development before applying to production users
6. **Monitor User Activity**: Track per-user command execution to identify unusual access patterns
7. **Document Permission Model**: Maintain clear documentation of which users/services have which access levels and why

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-memory-db
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/memory-db/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-memory-db/tree/master/examples
- **AWS MemoryDB Documentation**: https://docs.aws.amazon.com/memorydb/latest/devguide/what-is-memorydb-for-redis.html
- **AWS MemoryDB Developer Guide**: https://docs.aws.amazon.com/memorydb/latest/devguide/
- **MemoryDB Compliance**: https://docs.aws.amazon.com/memorydb/latest/devguide/memorydb-compliance.html
- **Redis Commands Reference**: https://redis.io/commands/
- **Valkey Documentation**: https://valkey.io/documentation/
- **AWS MemoryDB Pricing**: https://aws.amazon.com/memorydb/pricing/
- **MemoryDB Monitoring**: https://docs.aws.amazon.com/memorydb/latest/devguide/memorydb-monitoring.html
- **MemoryDB Security**: https://docs.aws.amazon.com/memorydb/latest/devguide/memorydb-security.html
- **Redis ACL Documentation**: https://redis.io/docs/management/security/acl/
- **AWS MemoryDB FAQs**: https://aws.amazon.com/memorydb/faqs/

## Notes for AI Agents

When using this module in automated workflows:

1. **Engine Selection**: Choose "redis" or "valkey" based on compatibility requirements; both are Redis-compatible but Valkey is newer
2. **Version Compatibility**: Ensure client libraries support the selected engine_version; test compatibility in dev first
3. **Shard Planning**: num_shards determines horizontal scalability; plan based on dataset size and throughput requirements
4. **Replica Requirements**: num_replicas_per_shard affects availability and read capacity; minimum 1 for production, 2 for critical workloads
5. **Subnet Distribution**: subnet_ids must span at least 2 AZs; MemoryDB distributes nodes across provided subnets automatically
6. **User Authentication**: Supports password-based and IAM authentication (type = "iam"); store passwords in Secrets Manager
7. **ACL Dependencies**: acl_user_names must reference created user names; ensure users exist before associating with ACL
8. **Snapshot Naming**: snapshot_name for restoration must be exact match; use data source to query available snapshots
9. **Parameter Group Family**: parameter_group_family must match engine version (e.g., "memorydb_redis7" for Redis 7.x)
10. **TLS Configuration**: When tls_enabled = true, clients must support TLS; when tls_enabled = false, acl_name must be "open-access"
11. **Data Tiering Compatibility**: data_tiering only available on R6gd and R7gd instance families; requires supported node types
12. **Final Snapshot Timing**: final_snapshot_name snapshot is created before deletion; plan for snapshot storage costs
13. **Conditional Creation**: Use create flags to manage existing resources; set create_subnet_group = false when using existing subnets
14. **Port Configuration**: Default port is 6379; if changing, ensure security group rules and client configurations are updated
15. **Monitoring Integration**: Configure CloudWatch alarms for DatabaseMemoryUsagePercentage, EngineCPUUtilization; use sns_topic_arn for notifications
16. **Engine Version Upgrades**: Downgrades are not supported; plan version upgrades carefully and test in non-production first
