# Terraform AWS DynamoDB Table Module

## Module Information

- **Module Name**: `dynamodb-table`
- **Source**: `terraform-aws-modules/dynamodb-table/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/dynamodb-table/aws/latest
- **Latest Version**: 5.5.0 (2026-01-08)
- **Minimum Versions**: Terraform >= 1.5.7, AWS Provider >= 6.28
- **Purpose**: Terraform module that creates and manages a single AWS DynamoDB table with its indexes, autoscaling policies, streams, and (optionally) global-table replicas
- **Service**: AWS DynamoDB (NoSQL Database Service)
- **Category**: Database, Storage, Serverless
- **Keywords**: dynamodb, nosql, database, key-value, partition-key, sort-key, gsi, lsi, autoscaling, on-demand, provisioned, pitr, kms-encryption, streams, ttl, global-table, multi-region, table-class
- **Use For**: web/mobile application backends, session storage, user profile stores, real-time analytics, IoT telemetry ingestion, gaming leaderboards, serverless data stores, event-driven architectures with Lambda/Kinesis, shopping carts, single-table design microservices

## Description

This Terraform module creates and configures a single AWS DynamoDB table, Amazon's fully managed NoSQL database service that delivers single-digit-millisecond performance at virtually any scale. It wraps the `aws_dynamodb_table` resource (plus the associated `aws_appautoscaling_target`/`aws_appautoscaling_policy` and `aws_dynamodb_resource_policy` resources) to expose a simpler, opinionated interface for the most common table configurations, while still allowing full control over capacity, indexing, and operational features through pass-through variables.

The module supports both billing modes (`PROVISIONED` with optional application autoscaling, or `PAY_PER_REQUEST` on-demand), hash/range key schemas, up to 20 Global Secondary Indexes and Local Secondary Indexes for alternative query patterns, and DynamoDB Streams for change-data-capture integrations with Lambda or Kinesis. It manages point-in-time recovery (PITR), time-to-live (TTL) item expiration, server-side encryption (AWS-owned, AWS-managed, or customer-managed KMS keys), table class selection (`STANDARD` vs `STANDARD_INFREQUENT_ACCESS`), deletion protection, and resource-based policies for cross-account access.

Distinctive architectural features include multi-region global tables via `replica_regions` (with per-replica KMS keys, PITR, and tag propagation), the newer Multi-Region Strong Consistency mode via `global_table_witness`, S3 data import at table-creation time, table restoration from point-in-time or on-demand backups (including cross-region restores), and warm-throughput / on-demand-throughput controls for predictable performance and cost caps. Internally the module implements the table as one of three mutually-exclusive resources (plain, autoscaled, or autoscaled-with-GSI-changes-ignored) selected via `autoscaling_enabled` and `ignore_changes_global_secondary_index`, which has important state-migration implications covered below. It does not define nested submodules, but ships Terragrunt-style module wrappers for creating many similar tables via `for_each`.

## Key Features

- **Flexible Billing Modes**: `PROVISIONED` capacity with granular read/write units, or `PAY_PER_REQUEST` on-demand for unpredictable workloads
- **Autoscaling**: Application Auto Scaling policies for table-level and per-GSI read/write capacity, with configurable target utilization and cooldowns
- **Global Secondary Indexes (GSI)**: Up to 20 GSIs per table, each with its own partition/sort key, projection type, and optional dedicated capacity or on-demand/warm throughput
- **Local Secondary Indexes (LSI)**: Alternative sort-key queries sharing the base table's partition key (allocatable only at table creation)
- **Point-in-Time Recovery (PITR)**: Continuous backups with configurable retention (1-35 days, default 35) and second-level restore granularity
- **Server-Side Encryption**: AWS-owned key (default), AWS-managed KMS key, or a customer-managed CMK via `server_side_encryption_kms_key_arn`
- **DynamoDB Streams**: Change-data-capture with configurable `stream_view_type` for Lambda triggers or Kinesis-compatible consumers
- **Time-to-Live (TTL)**: Automatic expiration/deletion of items without consuming write capacity
- **Global Tables**: Multi-region active-active replication via `replica_regions`, with per-replica KMS key, PITR, tag propagation, and consistency mode
- **Global Table Witness**: Multi-Region Strong Consistency using a witness region (requires exactly one replica set to `consistency_mode = "STRONG"`)
- **Table Class Selection**: `STANDARD` or `STANDARD_INFREQUENT_ACCESS` for cost-optimized storage of rarely accessed data
- **Deletion Protection**: `deletion_protection_enabled` guards the table (and, for non-autoscaled tables, individual replicas) against accidental deletion
- **Resource-Based Policies**: Attach a JSON resource policy via `aws_dynamodb_resource_policy`, with automatic `__DYNAMODB_TABLE_ARN__` placeholder substitution to avoid circular references
- **S3 Table Import**: Bulk-load data from S3 (CSV, DynamoDB JSON, or Amazon Ion) into a new table at creation time
- **Table Restore**: Restore from PITR (`restore_to_latest_time` / `restore_date_time`) or from a source table/backup ARN, including cross-region restores
- **On-Demand / Warm Throughput**: Cap maximum RCU/WCU for on-demand tables and pre-warm capacity for provisioned/GSI throughput
- **Per-Resource Region Override**: `region` argument to manage a table in a region different from the default provider region
- **Module Wrappers**: Terragrunt-friendly `wrappers/` directory for creating multiple table instances via `for_each` without duplicating module blocks

## Main Use Cases

1. **User Session Management**: Store and retrieve session data with single-digit-millisecond latency
2. **User Profile Storage**: Maintain user profiles and preferences with flexible, schemaless attributes
3. **Real-Time Analytics**: Capture and react to item-level changes via DynamoDB Streams
4. **IoT Data Collection**: Ingest high-volume sensor/device telemetry at massive scale
5. **Gaming Leaderboards**: Manage scores and rankings using sorted partition/sort-key access
6. **Shopping Carts**: Store cart items with per-item atomicity and transactional consistency
7. **Serverless Backends**: Pair with Lambda and API Gateway as the primary data store
8. **Event Sourcing**: Feed event streams to downstream processors via Streams + Lambda/Kinesis
9. **Cache Layer**: Implement a durable cache with automatic TTL-based expiration
10. **Globally Distributed Applications**: Serve low-latency reads/writes from multiple regions using global tables
11. **Metadata / Feature-Flag Storage**: Store configuration and feature flags with low-latency lookups
12. **Data Archival Migration**: Import historical data from S3 into a new table for one-time backfills

## Submodules

This module does not define nested/child submodules — it manages a single root-level DynamoDB table (selecting between plain, autoscaled, and autoscaled-with-GSI-ignore resource variants internally based on your inputs). For provisioning many similar tables without repeating module blocks, use Terraform's native `for_each` on the module call, or the pre-built Terragrunt wrappers in the [`wrappers/`](https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table/tree/master/wrappers) directory of the repository.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_table` | `bool` | `true` | Controls if the DynamoDB table and associated resources are created |
| `name` | `string` | `null` | Name of the DynamoDB table |
| `billing_mode` | `string` | `"PAY_PER_REQUEST"` | `PROVISIONED` or `PAY_PER_REQUEST` |
| `hash_key` | `string` | `null` | Partition key attribute name (must also appear in `attributes`) |
| `range_key` | `string` | `null` | Sort key attribute name (must also appear in `attributes`) |
| `attributes` | `list(map(string))` | `[]` | Attribute definitions (`name`, `type`); only key attributes used by the table or its indexes need to be listed |
| `read_capacity` / `write_capacity` | `number` | `null` | RCU/WCU when `billing_mode = "PROVISIONED"` (must be > 0); also used as the autoscaling `min_capacity` |
| `global_secondary_indexes` | `any` | `[]` | List of GSI objects: `name`, `hash_key`, `range_key`, `projection_type`, `non_key_attributes`, `read_capacity`, `write_capacity`, `on_demand_throughput`, `warm_throughput` |
| `local_secondary_indexes` | `any` | `[]` | List of LSI objects: `name`, `range_key`, `projection_type`, `non_key_attributes` (immutable after creation) |
| `ttl_enabled` / `ttl_attribute_name` | `bool` / `string` | `false` / `""` | Enable TTL and name the attribute holding the epoch expiration timestamp |
| `point_in_time_recovery_enabled` | `bool` | `false` | Enable continuous backups (PITR) |
| `point_in_time_recovery_period_in_days` | `number` | `null` | PITR retention window, 1-35 (defaults to 35 when PITR is enabled) |
| `server_side_encryption_enabled` | `bool` | `false` | `true` uses the AWS-managed KMS key (`alias/aws/dynamodb`) or a custom CMK; `false` uses the AWS-owned key (data is still encrypted at rest either way) |
| `server_side_encryption_kms_key_arn` | `string` | `null` | ARN of a customer-managed CMK (only needed if different from the default DynamoDB managed key) |
| `stream_enabled` / `stream_view_type` | `bool` / `string` | `false` / `null` | Enable Streams and set view type: `KEYS_ONLY`, `NEW_IMAGE`, `OLD_IMAGE`, `NEW_AND_OLD_IMAGES` |
| `table_class` | `string` | `null` | `STANDARD` or `STANDARD_INFREQUENT_ACCESS` |
| `deletion_protection_enabled` | `bool` | `null` | Prevents accidental table deletion |
| `autoscaling_enabled` | `bool` | `false` | Enables application autoscaling (switches to a different underlying resource — see Gotchas) |
| `autoscaling_defaults` | `map(string)` | `{scale_in_cooldown=0, scale_out_cooldown=0, target_value=70}` | Fallback values applied when not overridden per read/write/index |
| `autoscaling_read` / `autoscaling_write` | `map(string)` | `{}` | Only `max_capacity` is required; `min_capacity` always comes from `read_capacity`/`write_capacity`, not from this map |
| `autoscaling_indexes` | `map(map(string))` | `{}` | Per-GSI autoscaling keyed by index name, each with `read_max_capacity`, `read_min_capacity`, `write_max_capacity`, `write_min_capacity` (flat keys, not nested `read`/`write` blocks) |
| `replica_regions` | `any` | `[]` | Global table replicas: `region_name`, `kms_key_arn`, `propagate_tags`, `point_in_time_recovery`, `consistency_mode` (`deletion_protection_enabled` only applies when `autoscaling_enabled = false`) |
| `global_table_witness` | `object({region_name})` | `null` | Witness region for Multi-Region Strong Consistency; requires exactly one replica with `consistency_mode = "STRONG"`; only supported when `autoscaling_enabled = false` |
| `on_demand_throughput` | `any` | `{}` | `max_read_request_units` / `max_write_request_units` cap for `PAY_PER_REQUEST` tables |
| `warm_throughput` | `any` | `{}` | `read_units_per_second` / `write_units_per_second` to pre-warm table throughput |
| `import_table` | `any` | `{}` | S3 import config: `input_format`, `input_compression_type`, `bucket`, `key_prefix`, `input_format_options` |
| `ignore_changes_global_secondary_index` | `bool` | `false` | Ignore GSI/capacity drift in Terraform lifecycle (requires out-of-band GSI/capacity management) |
| `resource_policy` | `string` | `null` | JSON resource-based policy; use the literal token `__DYNAMODB_TABLE_ARN__` to self-reference the table's ARN |
| `region` | `string` | `null` | Overrides the provider's default region for this table |
| `restore_source_name` / `restore_source_table_arn` | `string` | `null` | Restore from an existing table (same-region) or a table/backup ARN (required for cross-region restore) |
| `restore_to_latest_time` / `restore_date_time` | `bool` / `string` | `null` | Restore to the latest PITR point, or to a specific timestamp |
| `timeouts` | `map(string)` | `{create="10m", update="60m", delete="10m"}` | Resource operation timeouts |
| `tags` | `map(string)` | `{}` | Tags applied to all created resources (module also injects a `Name` tag) |

## Main Outputs

| Output | Description |
|--------|-------------|
| `dynamodb_table_arn` | ARN of the DynamoDB table |
| `dynamodb_table_id` | ID (name) of the DynamoDB table |
| `dynamodb_table_stream_arn` | ARN of the table stream (empty string when `stream_enabled = false`) |
| `dynamodb_table_stream_label` | ISO 8601 timestamp label of the table stream |
| `dynamodb_table_replicas` | Map of replica objects keyed by region (full replica attributes) |
| `dynamodb_table_replica_arns` | Map of replica table ARNs keyed by region |
| `dynamodb_table_replica_stream_arns` | Map of replica stream ARNs keyed by region |
| `dynamodb_table_replica_stream_labels` | Map of replica stream timestamp labels keyed by region |

Note: there are no `dynamodb_table_hash_key` / `dynamodb_table_range_key` outputs — reference the `hash_key` / `range_key` input values directly if needed elsewhere.

## Usage Examples

### Example 1: Simple On-Demand Table

```hcl
module "dynamodb_table" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "~> 5.0"

  name     = "users-table"
  hash_key = "user_id"

  attributes = [
    {
      name = "user_id"
      type = "S"  # String
    }
  ]

  # On-demand billing mode (default)
  billing_mode = "PAY_PER_REQUEST"

  # Enable point-in-time recovery
  point_in_time_recovery_enabled = true

  # Use the AWS-managed KMS key instead of the AWS-owned default key
  server_side_encryption_enabled = true

  tags = {
    Terraform   = "true"
    Environment = "production"
    Application = "user-service"
  }
}
```

### Example 2: Provisioned Table with Autoscaling

```hcl
module "dynamodb_orders" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "~> 5.0"

  name      = "orders"
  hash_key  = "order_id"
  range_key = "created_at"

  attributes = [
    { name = "order_id", type = "S" },
    { name = "created_at", type = "N" },
    { name = "customer_id", type = "S" }
  ]

  # Provisioned billing mode
  billing_mode   = "PROVISIONED"
  read_capacity  = 5   # also used as autoscaling min_capacity
  write_capacity = 5

  # Enable autoscaling (only `max_capacity` is read from these maps)
  autoscaling_enabled = true

  autoscaling_read = {
    scale_in_cooldown  = 50
    scale_out_cooldown = 40
    target_value       = 70  # target 70% utilization
    max_capacity        = 100
  }

  autoscaling_write = {
    scale_in_cooldown  = 50
    scale_out_cooldown = 40
    target_value       = 70
    max_capacity        = 100
  }

  # Global Secondary Index with autoscaling
  global_secondary_indexes = [
    {
      name            = "CustomerIndex"
      hash_key        = "customer_id"
      range_key       = "created_at"
      projection_type = "ALL"
      read_capacity   = 5
      write_capacity  = 5
    }
  ]

  # Flat keys, NOT nested read/write objects
  autoscaling_indexes = {
    CustomerIndex = {
      read_max_capacity  = 50
      read_min_capacity  = 5
      write_max_capacity = 50
      write_min_capacity = 5
    }
  }

  point_in_time_recovery_enabled = true
  server_side_encryption_enabled = true

  tags = {
    Terraform   = "true"
    Environment = "production"
    Application = "order-service"
  }
}
```

### Example 3: Table with DynamoDB Streams and TTL

```hcl
module "dynamodb_events" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "~> 5.0"

  name      = "events-stream"
  hash_key  = "event_id"
  range_key = "timestamp"

  attributes = [
    { name = "event_id", type = "S" },
    { name = "timestamp", type = "N" }
  ]

  billing_mode = "PAY_PER_REQUEST"

  # Enable DynamoDB Streams for Lambda triggers
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"  # capture both old and new item images

  # Enable TTL for automatic item expiration
  ttl_enabled        = true
  ttl_attribute_name = "expiration_time"

  # Encrypt with a customer-managed KMS key
  server_side_encryption_enabled     = true
  server_side_encryption_kms_key_arn = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"

  point_in_time_recovery_enabled = true

  tags = {
    Terraform   = "true"
    Environment = "production"
    Application = "event-processor"
  }
}

resource "aws_lambda_event_source_mapping" "dynamodb_stream" {
  event_source_arn  = module.dynamodb_events.dynamodb_table_stream_arn
  function_name     = aws_lambda_function.stream_processor.arn
  starting_position = "LATEST"

  batch_size                         = 100
  maximum_batching_window_in_seconds = 5
  maximum_retry_attempts             = 3
  bisect_batch_on_function_error     = true
}
```

### Example 4: Table with Multiple Global Secondary Indexes

```hcl
module "dynamodb_products" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "~> 5.0"

  name     = "products"
  hash_key = "product_id"

  attributes = [
    { name = "product_id", type = "S" },
    { name = "category", type = "S" },
    { name = "price", type = "N" },
    { name = "brand", type = "S" },
    { name = "created_at", type = "N" }
  ]

  billing_mode = "PAY_PER_REQUEST"

  global_secondary_indexes = [
    # Query by category and price
    {
      name            = "CategoryPriceIndex"
      hash_key        = "category"
      range_key       = "price"
      projection_type = "ALL"
    },
    # Query by brand and creation date, projecting only select attributes
    {
      name                = "BrandDateIndex"
      hash_key            = "brand"
      range_key           = "created_at"
      projection_type     = "INCLUDE"
      non_key_attributes  = ["product_name", "description", "image_url"]
    },
    # Query by category only, minimal projection for cost efficiency
    {
      name            = "CategoryIndex"
      hash_key        = "category"
      projection_type = "KEYS_ONLY"
    }
  ]

  table_class                    = "STANDARD_INFREQUENT_ACCESS"
  deletion_protection_enabled    = true
  point_in_time_recovery_enabled = true
  server_side_encryption_enabled = true

  tags = {
    Terraform   = "true"
    Environment = "production"
    Application = "product-catalog"
  }
}
```

### Example 5: Global Table with Multi-Region Replication

```hcl
module "dynamodb_global_table" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "~> 5.0"

  name     = "global-users"
  hash_key = "user_id"

  attributes = [
    { name = "user_id", type = "S" }
  ]

  billing_mode = "PAY_PER_REQUEST"

  # Streams are REQUIRED for global tables
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  replica_regions = [
    {
      region_name            = "eu-west-1"
      point_in_time_recovery = true
      propagate_tags         = true
    },
    {
      region_name            = "ap-southeast-1"
      point_in_time_recovery = true
      propagate_tags         = true
    }
  ]

  point_in_time_recovery_enabled = true
  server_side_encryption_enabled = true

  tags = {
    Terraform   = "true"
    Environment = "production"
    Application = "global-user-service"
  }
}
```

### Example 6: Global Table with Witness Region (Strong Consistency)

```hcl
module "dynamodb_strong_consistency" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "~> 5.0"

  name     = "strong-consistency-table"
  hash_key = "id"

  attributes = [
    { name = "id", type = "S" }
  ]

  billing_mode = "PAY_PER_REQUEST"

  # Streams required for global tables; autoscaling must stay disabled
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  # Exactly one replica with STRONG consistency is required for a witness
  replica_regions = [
    {
      region_name            = "eu-west-1"
      point_in_time_recovery = true
      consistency_mode       = "STRONG"
    }
  ]

  global_table_witness = {
    region_name = "ap-southeast-1"
  }

  point_in_time_recovery_enabled = true
  server_side_encryption_enabled = true

  tags = {
    Terraform   = "true"
    Environment = "production"
  }
}
```

### Example 7: Table with a Self-Referencing Resource Policy

```hcl
module "dynamodb_shared_table" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "~> 5.0"

  name     = "shared-catalog"
  hash_key = "item_id"

  attributes = [
    { name = "item_id", type = "S" }
  ]

  billing_mode = "PAY_PER_REQUEST"

  # __DYNAMODB_TABLE_ARN__ is substituted with the table's own ARN,
  # avoiding a circular dependency on the module's own output
  resource_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowReadFromPartnerAccount"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::999999999999:root" }
        Action    = ["dynamodb:GetItem", "dynamodb:Query"]
        Resource  = "__DYNAMODB_TABLE_ARN__"
      }
    ]
  })

  tags = {
    Terraform   = "true"
    Environment = "production"
  }
}
```

## Important Gotchas

**IMPORTANT**: Read these before generating configuration for this module — several are non-obvious and will cause plan/apply failures or silently ignored settings:

1. **Autoscaling state management**: Toggling `autoscaling_enabled` switches the underlying resource (`aws_dynamodb_table.this` <-> `.autoscaled`) and **causes table recreation**. Migrate state instead:
   ```bash
   terraform state mv module.dynamodb_table.aws_dynamodb_table.this \
     module.dynamodb_table.aws_dynamodb_table.autoscaled
   ```
2. **`ignore_changes_global_secondary_index` also swaps resources**: Enabling/disabling it while `autoscaling_enabled = true` switches between `.autoscaled` and `.autoscaled_gsi_ignore`, which also forces recreation unless migrated:
   ```bash
   terraform state mv module.dynamodb_table.aws_dynamodb_table.autoscaled \
     module.dynamodb_table.aws_dynamodb_table.autoscaled_gsi_ignore
   ```
3. **GSI capacity resets under autoscaling**: Applying changes while an autoscaled GSI is scaled up resets it to the configured base capacity (known AWS provider limitation). Set `ignore_changes_global_secondary_index = true` to prevent this — but then GSI/capacity changes must be made outside Terraform.
4. **`autoscaling_read`/`autoscaling_write` do not set `min_capacity`**: `min_capacity` is always taken from `read_capacity`/`write_capacity`; only `max_capacity` (and optional cooldowns/target) is read from these maps. Setting a `min_capacity` key in the map has no effect.
5. **`autoscaling_indexes` uses flat keys**: Each entry is `{ read_max_capacity, read_min_capacity, write_max_capacity, write_min_capacity }` — not nested `read {}` / `write {}` blocks.
6. **LSI immutability**: Local Secondary Indexes can only be defined at table creation and **cannot be added, changed, or removed afterward** without recreating the table.
7. **PROVISIONED mode requires capacity**: When `billing_mode = "PROVISIONED"`, both `read_capacity` and `write_capacity` must be greater than 0.
8. **`attributes` should only list key attributes**: Only attributes used as a table or index hash/range key need an entry — DynamoDB is schemaless for all other item attributes.
9. **Encryption is always on, but the default key is not customer-visible**: `server_side_encryption_enabled = false` (module default) still encrypts data at rest, using the AWS-owned key. Set it to `true` to use the AWS-managed `alias/aws/dynamodb` key (or a custom CMK via `server_side_encryption_kms_key_arn`) if you need visibility/rotation control in your account.
10. **Global tables require streams**: `replica_regions` requires `stream_enabled = true` and `stream_view_type = "NEW_AND_OLD_IMAGES"`.
11. **`global_table_witness` is incompatible with autoscaling**: The witness block is only implemented on the non-autoscaled resource; it requires `autoscaling_enabled = false` and exactly one replica region with `consistency_mode = "STRONG"`.
12. **Replica `deletion_protection_enabled` only applies without autoscaling**: This per-replica setting is only wired up on the non-autoscaled table resource.
13. **No hash/range-key outputs**: The module does not expose `dynamodb_table_hash_key` / `dynamodb_table_range_key` outputs — reuse your own `hash_key`/`range_key` input values instead.
14. **Self-referencing resource policies**: Use the literal string `__DYNAMODB_TABLE_ARN__` inside `resource_policy` JSON instead of interpolating `module.<name>.dynamodb_table_arn`, which would create a circular dependency.

## Best Practices

### Data Modeling and Design
1. **Choose a High-Cardinality Partition Key**: Distribute read/write traffic evenly across partitions to avoid hot partitions and throttling.
2. **Design for Access Patterns**: Model the schema around query patterns rather than normalized relational design — denormalization is expected.
3. **Use Composite Keys**: Combine partition and sort keys for hierarchical data organization and range queries within a partition.
4. **Minimize GSIs**: Each GSI adds its own storage and (for provisioned tables) capacity cost — only add indexes for access patterns the base table can't serve.
5. **Use Sparse Indexes**: Omit the indexed attribute on items that shouldn't appear in a GSI to reduce its size and cost.
6. **Consider Single-Table Design**: For complex applications, a single-table design can reduce cost and simplify capacity management.
7. **Prefer Efficient Attribute Types**: Use Number (`N`) rather than String (`S`) for numeric values to save storage and enable numeric sort ordering.
8. **Keep Items Small**: DynamoDB items are capped at 400KB; store large blobs in S3 and reference them by key.

### Capacity and Performance
1. **Match Billing Mode to Traffic Shape**: `PAY_PER_REQUEST` for spiky/unpredictable workloads, `PROVISIONED` + autoscaling for steady, forecastable traffic.
2. **Always Enable Autoscaling for Provisioned Tables**: Prevents throttling and manual capacity tuning; set `autoscaling_read`/`autoscaling_write` with a sensible `max_capacity`.
3. **Target 60-80% Utilization**: Balances cost efficiency against burst headroom in `target_value`.
4. **Alarm on Throttled Requests**: Watch `ReadThrottleEvents`/`WriteThrottleEvents` and investigate hot partitions or raise capacity.
5. **Prefer Query Over Scan**: `Scan` reads the entire table and consumes far more capacity than a targeted `Query`.
6. **Use Eventually Consistent Reads by Default**: They cost half of strongly consistent reads; reserve strong consistency for cases that need it.
7. **Batch Requests**: Use `BatchGetItem`/`BatchWriteItem` (up to 25 items) to reduce round trips.

### Security and Compliance
1. **Prefer Customer-Managed KMS Keys for Regulated Data**: Set `server_side_encryption_enabled = true` with `server_side_encryption_kms_key_arn` for auditable, rotatable encryption.
2. **Apply Least-Privilege IAM Policies**: Scope `dynamodb:*` actions to specific table/index ARNs and, where possible, specific attributes via IAM condition keys.
3. **Use VPC Endpoints**: Keep DynamoDB traffic on the AWS network and avoid NAT gateway costs.
4. **Enable CloudTrail Logging**: Capture DynamoDB control-plane and data-plane API calls for auditing.
5. **Use Resource Policies for Cross-Account Access**: Prefer `resource_policy` over broad IAM trust relationships when sharing a table across accounts.
6. **Enable Deletion Protection in Production**: Set `deletion_protection_enabled = true` to prevent accidental `terraform destroy`/console deletion.

### Backup and Recovery
1. **Enable PITR for Production Tables**: Restore to any second within the retention window (up to 35 days).
2. **Supplement PITR with On-Demand Backups**: For retention beyond 35 days or before major schema/data changes.
3. **Test Restores Regularly**: Validate `restore_source_name`/`restore_to_latest_time` workflows against your RTO/RPO targets.
4. **Use Global Tables for Active-Active DR**: For mission-critical workloads, multi-region replication is stronger than backup/restore alone.

### Cost Optimization
1. **Use TTL to Expire Data**: Deletes via TTL don't consume write capacity, unlike explicit deletes.
2. **Switch Cold Tables to `STANDARD_INFREQUENT_ACCESS`**: ~50% lower storage cost for data accessed less than roughly twice a month.
3. **Minimize GSI Projections**: Use `KEYS_ONLY` or `INCLUDE` instead of `ALL` unless the extra attributes are actually queried through the index.
4. **Cap On-Demand Spend**: Use `on_demand_throughput` to bound `max_read_request_units`/`max_write_request_units` on `PAY_PER_REQUEST` tables.
5. **Review Contributor Insights**: Identify hot keys and unused indexes to eliminate wasted capacity.

### DynamoDB Streams and Event Processing
1. **Pick the Narrowest Stream View That Works**: `KEYS_ONLY` for minimal payloads, `NEW_AND_OLD_IMAGES` for full audit/diff trails.
2. **Design Idempotent Consumers**: Streams provide at-least-once delivery; downstream Lambda/Kinesis consumers must tolerate duplicates.
3. **Tune Batch Size and Retries**: Balance Lambda concurrency and latency against processing failures via `batch_size`, `maximum_retry_attempts`, and DLQs.
4. **Alarm on Iterator Age**: A rising iterator age signals consumer lag or repeated processing failures.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/dynamodb-table/aws/latest
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table/blob/master/CHANGELOG.md
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table/tree/master/examples
- **AWS Provider `aws_dynamodb_table` Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table
- **AWS DynamoDB Developer Guide**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/
- **DynamoDB Best Practices**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html
- **DynamoDB Streams**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html
- **DynamoDB Global Tables**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GlobalTables.html
- **DynamoDB Pricing**: https://aws.amazon.com/dynamodb/pricing/

## Notes for AI Agents

When generating Terraform code with this module:

1. **Set `name`, `hash_key`, and `attributes` at minimum** — `attributes` must include an entry for every key referenced by `hash_key`, `range_key`, and any GSI/LSI, and nothing else.
2. **Default to production-safe settings** unless told otherwise:
   ```hcl
   point_in_time_recovery_enabled = true
   server_side_encryption_enabled = true
   deletion_protection_enabled    = true
   ```
3. **Pick billing mode deliberately**: use `PAY_PER_REQUEST` unless the user specifies steady, predictable traffic — then use `PROVISIONED` with `autoscaling_enabled = true` and a `max_capacity` in both `autoscaling_read` and `autoscaling_write`.
4. **Never put `min_capacity` in `autoscaling_read`/`autoscaling_write`** — it is ignored; set `read_capacity`/`write_capacity` instead.
5. **Use flat keys for `autoscaling_indexes`** (`read_max_capacity`, `read_min_capacity`, `write_max_capacity`, `write_min_capacity`), not nested blocks.
6. **For global tables**, always pair `replica_regions` with `stream_enabled = true` and `stream_view_type = "NEW_AND_OLD_IMAGES"`; never combine `global_table_witness` with `autoscaling_enabled = true`.
7. **Warn the user** before generating a config that flips `autoscaling_enabled` or `ignore_changes_global_secondary_index` on an existing table — both require a `terraform state mv` to avoid recreation.
8. **Do not self-reference the module's own ARN output inside `resource_policy`** — use the `__DYNAMODB_TABLE_ARN__` placeholder token instead.
9. **Tag consistently** (`Environment`, `Application`, `Terraform = "true"`, plus any org-mandated cost/ownership tags).
10. **Pin the module version** (e.g., `version = "~> 5.0"`) to avoid unexpected breaking changes across major versions.
