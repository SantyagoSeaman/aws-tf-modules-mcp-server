# Terraform AWS DynamoDB Table Module

## Module Information

- **Module Name**: `dynamodb-table`
- **Source**: `terraform-aws-modules/dynamodb-table/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/dynamodb-table/aws/latest
- **Latest Version**: 5.1.0
- **Purpose**: Terraform module that creates and manages AWS DynamoDB tables with comprehensive configuration options for NoSQL database workloads
- **Service**: AWS DynamoDB (NoSQL Database Service)
- **Category**: Database, Storage, Serverless
- **Keywords**: dynamodb, nosql, database, table, key-value, document-store, partition-key, sort-key, hash-key, range-key, global-secondary-index, gsi, local-secondary-index, lsi, autoscaling, provisioned-capacity, on-demand, pay-per-request, billing-mode, read-capacity, write-capacity, throughput, point-in-time-recovery, pitr, backup, restore, encryption, kms, server-side-encryption, sse, dynamodb-streams, stream, kinesis, lambda-trigger, ttl, time-to-live, attribute, projection, eventual-consistency, strong-consistency, global-table, multi-region, replication, cross-region, table-class, standard, infrequent-access, deletion-protection, resource-policy, transactional-reads, transactional-writes, batch-operations, query, scan, partition, item, capacity-units, rcu, wcu
- **Use For**: Web and mobile application backends, session management, user profiles storage, real-time analytics, IoT data collection, gaming leaderboards, serverless application data stores, event-driven architectures, caching layer, shopping carts, content management, time-series data storage

## Description

This Terraform module provides a comprehensive solution for creating and managing AWS DynamoDB tables, Amazon's fully managed NoSQL database service that delivers single-digit millisecond performance at any scale. DynamoDB is designed for applications that require consistent, low-latency data access with virtually unlimited throughput and storage. The module supports both key-value and document data models, making it suitable for a wide range of use cases from simple session storage to complex multi-item transactional applications. It abstracts the complexity of DynamoDB table configuration while providing fine-grained control over capacity management, indexing strategies, and operational features.

The module handles essential DynamoDB features including flexible billing modes (provisioned capacity with autoscaling or on-demand pay-per-request), global and local secondary indexes for efficient query patterns, and DynamoDB Streams for change data capture and event-driven architectures. It supports advanced operational capabilities such as point-in-time recovery for disaster recovery scenarios, time-to-live (TTL) for automatic item expiration, and server-side encryption using AWS KMS for data protection at rest. The module also manages autoscaling policies for provisioned capacity tables, automatically adjusting read and write capacity units based on actual traffic patterns to optimize costs while maintaining performance.

Key architectural features include support for global tables enabling multi-region, fully replicated tables for global applications with local read and write access, table class selection for cost optimization (standard vs. infrequent access), and deletion protection to prevent accidental data loss. The module integrates seamlessly with other AWS services through DynamoDB Streams (compatible with Kinesis), enabling real-time processing with AWS Lambda, data pipelines with Kinesis Data Streams, and analytics workflows. Whether deploying a simple single-table design or complex multi-index structures for advanced query patterns, this module simplifies DynamoDB management while maintaining the flexibility and power required for production workloads.

## Key Features

- **Flexible Billing Modes**: Support for both PROVISIONED capacity with granular control and PAY_PER_REQUEST (on-demand) for unpredictable workloads
- **Autoscaling Configuration**: Automatic scaling of read and write capacity units based on utilization metrics for provisioned tables
- **Hash and Range Keys**: Configure partition keys (hash keys) and optional sort keys (range keys) for flexible data organization
- **Attribute Definitions**: Define table attributes with support for String (S), Number (N), and Binary (B) data types
- **Global Secondary Indexes (GSI)**: Create up to 20 GSIs per table for alternative query patterns with different partition and sort keys
- **Local Secondary Indexes (LSI)**: Define LSIs for alternative sort key queries using the same partition key as the base table
- **Point-in-Time Recovery (PITR)**: Enable continuous backups for the last 35 days with second-level restore granularity
- **Server-Side Encryption**: Encrypt data at rest using AWS managed keys or customer-managed KMS keys for enhanced security
- **DynamoDB Streams**: Enable change data capture for real-time processing with Lambda triggers or Kinesis integration
- **Time-to-Live (TTL)**: Automatic deletion of expired items to reduce storage costs without consuming write capacity
- **Table Class Selection**: Choose between STANDARD and STANDARD_INFREQUENT_ACCESS for cost-optimized storage of infrequently accessed data
- **Global Tables**: Configure multi-region replication for globally distributed applications with local read/write access
- **Deletion Protection**: Prevent accidental table deletion by enabling deletion protection flag
- **Resource Policies**: Attach resource-based policies for fine-grained access control to DynamoDB tables
- **Stream View Types**: Configure stream records to include KEYS_ONLY, NEW_IMAGE, OLD_IMAGE, or NEW_AND_OLD_IMAGES
- **Projection Types**: Control which attributes are projected into secondary indexes (ALL, KEYS_ONLY, INCLUDE)
- **Transactional Support**: Built-in support for ACID transactions across multiple items and tables
- **Batch Operations**: Enable efficient batch read and write operations for high-throughput scenarios
- **Capacity Reservations**: Reserve read and write capacity for predictable workload patterns at discounted rates
- **CloudWatch Integration**: Automatic metrics publishing for monitoring table performance and capacity utilization
- **Import from S3**: Support for importing data from S3 into DynamoDB tables during or after creation
- **Table Restoration**: Create tables from point-in-time recovery backups or on-demand backups with cross-region support
- **Contributor Insights**: Enable detailed monitoring of most accessed and throttled items for optimization
- **Tagging Support**: Comprehensive tagging for cost allocation, resource organization, and governance

## Main Use Cases

1. **User Session Management**: Store and retrieve user session data with sub-10ms latency for web and mobile applications
2. **User Profile Storage**: Maintain user profiles, preferences, and account information with flexible schema design
3. **Real-Time Analytics**: Collect and query time-series data, metrics, and events with DynamoDB Streams integration
4. **IoT Data Collection**: Ingest and store IoT sensor data, device states, and telemetry at massive scale
5. **Gaming Leaderboards**: Manage game scores, player statistics, and real-time leaderboards with sorted data access
6. **Shopping Carts**: Store shopping cart data with item-level atomicity and transactional consistency
7. **Content Management**: Store and deliver content metadata, articles, and user-generated content with flexible queries
8. **Serverless Backends**: Power serverless applications with Lambda functions using DynamoDB as the primary data store
9. **Mobile Sync**: Synchronize mobile application data across devices with conflict resolution and offline support
10. **Cache Layer**: Implement high-performance caching layer with automatic expiration using TTL
11. **Event Sourcing**: Store event streams for event-driven architectures with DynamoDB Streams triggering downstream processing
12. **Metadata Storage**: Store configuration data, feature flags, and application metadata with low-latency access

## Submodules

This module does not include submodules. It provides a single root module for DynamoDB table creation and management.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_table` | `bool` | `true` | Controls if DynamoDB table should be created |
| `name` | `string` | `null` | Name of the DynamoDB table |
| `billing_mode` | `string` | `"PAY_PER_REQUEST"` | Controls billing for read/write throughput (PROVISIONED or PAY_PER_REQUEST) |
| `hash_key` | `string` | `null` | The attribute to use as the hash (partition) key |
| `range_key` | `string` | `null` | The attribute to use as the range (sort) key |
| `attributes` | `list(map(string))` | `[]` | List of nested attribute definitions for hash and range keys (name and type) |
| `read_capacity` | `number` | `null` | Number of read units for this table (only with PROVISIONED billing mode) |
| `write_capacity` | `number` | `null` | Number of write units for this table (only with PROVISIONED billing mode) |
| `global_secondary_indexes` | `any` | `[]` | List of global secondary index configurations |
| `local_secondary_indexes` | `any` | `[]` | List of local secondary index configurations |
| `ttl_enabled` | `bool` | `false` | Indicates whether time-to-live is enabled |
| `ttl_attribute_name` | `string` | `""` | The name of the table attribute to store the TTL timestamp in |
| `point_in_time_recovery_enabled` | `bool` | `false` | Whether to enable point-in-time recovery |
| `server_side_encryption_enabled` | `bool` | `false` | Enable encryption at rest using AWS managed KMS customer master key |
| `server_side_encryption_kms_key_arn` | `string` | `null` | The ARN of the CMK that should be used for encryption |
| `stream_enabled` | `bool` | `false` | Indicates whether Streams are to be enabled (true) or disabled (false) |
| `stream_view_type` | `string` | `null` | When stream is enabled, defines the information written (KEYS_ONLY, NEW_IMAGE, OLD_IMAGE, NEW_AND_OLD_IMAGES) |
| `table_class` | `string` | `null` | The storage class of the table (STANDARD or STANDARD_INFREQUENT_ACCESS) |
| `deletion_protection_enabled` | `bool` | `null` | Enables deletion protection for table |
| `autoscaling_enabled` | `bool` | `false` | Whether or not to enable autoscaling |
| `autoscaling_read` | `map(string)` | `{}` | Map of read autoscaling settings (scale_in_cooldown, scale_out_cooldown, target_value, max_capacity, min_capacity) |
| `autoscaling_write` | `map(string)` | `{}` | Map of write autoscaling settings |
| `autoscaling_indexes` | `map(any)` | `{}` | Map of autoscaling settings for global secondary indexes |
| `replica_regions` | `list(string)` | `[]` | List of regions to create replica tables (for global tables) |
| `tags` | `map(string)` | `{}` | A map of tags to add to all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `dynamodb_table_arn` | ARN of the DynamoDB table |
| `dynamodb_table_id` | ID (name) of the DynamoDB table |
| `dynamodb_table_stream_arn` | The ARN of the Table Stream (only available when stream_enabled is true) |
| `dynamodb_table_stream_label` | A timestamp in ISO 8601 format of the Table Stream (only when stream_enabled is true) |
| `dynamodb_table_hash_key` | The hash key of the table |
| `dynamodb_table_range_key` | The range key of the table |

## Usage Examples

### Example 1: Simple On-Demand Table

```hcl
module "dynamodb_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

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

  # Enable server-side encryption
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
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "orders"
  hash_key = "order_id"
  range_key = "created_at"

  attributes = [
    {
      name = "order_id"
      type = "S"
    },
    {
      name = "created_at"
      type = "N"
    },
    {
      name = "customer_id"
      type = "S"
    }
  ]

  # Provisioned billing mode
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  # Enable autoscaling
  autoscaling_enabled = true

  autoscaling_read = {
    scale_in_cooldown  = 50
    scale_out_cooldown = 40
    target_value       = 70  # Target 70% utilization
    max_capacity       = 100
    min_capacity       = 5
  }

  autoscaling_write = {
    scale_in_cooldown  = 50
    scale_out_cooldown = 40
    target_value       = 70
    max_capacity       = 100
    min_capacity       = 5
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

  autoscaling_indexes = {
    CustomerIndex = {
      read = {
        scale_in_cooldown  = 50
        scale_out_cooldown = 40
        target_value       = 70
        max_capacity       = 50
        min_capacity       = 5
      }
      write = {
        scale_in_cooldown  = 50
        scale_out_cooldown = 40
        target_value       = 70
        max_capacity       = 50
        min_capacity       = 5
      }
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
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "events-stream"
  hash_key = "event_id"
  range_key = "timestamp"

  attributes = [
    {
      name = "event_id"
      type = "S"
    },
    {
      name = "timestamp"
      type = "N"
    }
  ]

  billing_mode = "PAY_PER_REQUEST"

  # Enable DynamoDB Streams for Lambda triggers
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"  # Capture both old and new item images

  # Enable TTL for automatic item expiration
  ttl_enabled        = true
  ttl_attribute_name = "expiration_time"

  # Enable encryption with customer-managed KMS key
  server_side_encryption_enabled = true
  server_side_encryption_kms_key_arn = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"

  point_in_time_recovery_enabled = true

  tags = {
    Terraform   = "true"
    Environment = "production"
    Application = "event-processor"
  }
}

# Example Lambda function triggered by DynamoDB Stream
resource "aws_lambda_function" "stream_processor" {
  filename      = "lambda_function.zip"
  function_name = "dynamodb-stream-processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"

  environment {
    variables = {
      STREAM_ARN = module.dynamodb_events.dynamodb_table_stream_arn
    }
  }
}

# Lambda event source mapping for DynamoDB Stream
resource "aws_lambda_event_source_mapping" "dynamodb_stream" {
  event_source_arn  = module.dynamodb_events.dynamodb_table_stream_arn
  function_name     = aws_lambda_function.stream_processor.arn
  starting_position = "LATEST"

  # Optional: configure batch size and retry behavior
  batch_size                         = 100
  maximum_batching_window_in_seconds = 5
  maximum_retry_attempts             = 3
  bisect_batch_on_function_error     = true
}
```

### Example 4: Table with Multiple Global Secondary Indexes

```hcl
module "dynamodb_products" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "products"
  hash_key = "product_id"

  attributes = [
    {
      name = "product_id"
      type = "S"
    },
    {
      name = "category"
      type = "S"
    },
    {
      name = "price"
      type = "N"
    },
    {
      name = "brand"
      type = "S"
    },
    {
      name = "created_at"
      type = "N"
    }
  ]

  billing_mode = "PAY_PER_REQUEST"

  # Multiple GSIs for different query patterns
  global_secondary_indexes = [
    # Query by category and price
    {
      name            = "CategoryPriceIndex"
      hash_key        = "category"
      range_key       = "price"
      projection_type = "ALL"
    },
    # Query by brand and creation date
    {
      name            = "BrandDateIndex"
      hash_key        = "brand"
      range_key       = "created_at"
      projection_type = "INCLUDE"
      non_key_attributes = ["product_name", "description", "image_url"]
    },
    # Query by category only
    {
      name            = "CategoryIndex"
      hash_key        = "category"
      projection_type = "KEYS_ONLY"  # Minimal projection for cost efficiency
    }
  ]

  # Use infrequent access table class for cost optimization
  table_class = "STANDARD_INFREQUENT_ACCESS"

  # Enable deletion protection
  deletion_protection_enabled = true

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
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "global-users"
  hash_key = "user_id"

  attributes = [
    {
      name = "user_id"
      type = "S"
    }
  ]

  billing_mode = "PAY_PER_REQUEST"

  # Enable global table replication to multiple regions
  replica_regions = [
    "eu-west-1",
    "ap-southeast-1",
    "us-west-2"
  ]

  # Enable streams (required for global tables)
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  # Point-in-time recovery in all regions
  point_in_time_recovery_enabled = true

  # Encryption in all regions
  server_side_encryption_enabled = true

  tags = {
    Terraform    = "true"
    Environment  = "production"
    Application  = "global-user-service"
    GlobalTable  = "true"
  }
}
```

## Best Practices

### Data Modeling and Design

1. **Choose the Right Partition Key**: Select a partition key with high cardinality that evenly distributes read and write traffic across partitions to avoid hot partitions and throttling.
2. **Design for Access Patterns**: Model your table schema based on your application's query patterns rather than normalized relational design - denormalization is encouraged.
3. **Use Composite Keys**: Combine partition key and sort key to enable hierarchical data organization and range queries within partitions.
4. **Minimize Global Secondary Indexes**: Each GSI doubles your costs for storage and capacity - only create indexes for essential query patterns you cannot satisfy with the base table.
5. **Use Sparse Indexes**: For GSIs where not all items have the indexed attributes, take advantage of sparse indexing to reduce costs and improve performance.
6. **Implement Single-Table Design**: For complex applications, consider single-table design patterns to reduce costs, improve performance, and simplify management.
7. **Choose Appropriate Attribute Types**: Use the most efficient data type - Number (N) for numeric values rather than String (S), as it uses less storage and enables numeric operations.
8. **Avoid Large Items**: Keep item sizes under 400KB (DynamoDB limit) and preferably much smaller for better performance - store large objects in S3 and reference them.
9. **Plan for Growth**: Design partition keys that will continue to distribute traffic evenly as your table grows to billions of items.
10. **Use Sort Key Overloading**: Store different entity types in the same table by encoding the entity type in the sort key for flexible queries.

### Capacity and Performance

1. **Choose the Right Billing Mode**: Use PAY_PER_REQUEST for unpredictable or spiky workloads, PROVISIONED with autoscaling for consistent traffic patterns to optimize costs.
2. **Enable Autoscaling**: For provisioned tables, always enable autoscaling to automatically adjust capacity based on demand and prevent throttling.
3. **Set Appropriate Autoscaling Targets**: Configure autoscaling target utilization between 60-80% to balance cost efficiency with performance headroom for traffic spikes.
4. **Monitor Throttled Requests**: Set CloudWatch alarms for throttled read/write requests and adjust provisioned capacity or investigate hot partition issues.
5. **Use Burst Capacity Wisely**: DynamoDB provides burst capacity, but don't rely on it for consistent traffic - design for your sustained throughput requirements.
6. **Batch Operations**: Use BatchGetItem and BatchWriteItem for multiple items to reduce API calls and improve efficiency, processing up to 25 items per batch.
7. **Implement Exponential Backoff**: Implement exponential backoff with jitter in your application for handling throttled requests and transient errors.
8. **Consider Read Consistency**: Use eventually consistent reads (default) instead of strongly consistent reads when possible - they consume half the capacity and cost less.
9. **Optimize Query Patterns**: Use Query instead of Scan operations whenever possible - Scans read entire table and consume significant capacity.
10. **Monitor Capacity Metrics**: Regularly review consumed vs provisioned capacity metrics to identify optimization opportunities and prevent over-provisioning.

### Security and Compliance

1. **Enable Encryption at Rest**: Always enable server-side encryption, preferably with customer-managed KMS keys for enhanced security and compliance control.
2. **Use IAM Policies**: Implement least privilege IAM policies that grant only necessary DynamoDB actions to specific tables and indexes.
3. **Enable Encryption in Transit**: Always use HTTPS endpoints for DynamoDB API calls and enable VPC endpoints for private connectivity.
4. **Implement Fine-Grained Access Control**: Use IAM conditions to restrict access to specific items or attributes based on partition key values or request parameters.
5. **Enable CloudTrail Logging**: Log all DynamoDB API calls to CloudTrail for security auditing, compliance, and troubleshooting.
6. **Use VPC Endpoints**: Deploy VPC endpoints for DynamoDB to keep traffic within AWS network and reduce data transfer costs.
7. **Implement Resource Policies**: For cross-account access scenarios, use resource-based policies on tables to control access from other AWS accounts.
8. **Protect Sensitive Data**: For highly sensitive attributes, consider client-side encryption before storing data in DynamoDB.
9. **Enable Deletion Protection**: Set `deletion_protection_enabled = true` for production tables to prevent accidental deletion.
10. **Tag for Compliance**: Implement comprehensive tagging including Owner, Environment, DataClassification, and ComplianceScope for governance.

### Backup and Recovery

1. **Enable Point-in-Time Recovery**: Always enable PITR for production tables to enable restore to any point within the last 35 days with second-level granularity.
2. **Create On-Demand Backups**: Supplement PITR with on-demand backups for important milestones, before major changes, or for long-term retention beyond 35 days.
3. **Test Recovery Procedures**: Regularly test table restoration from backups to validate your disaster recovery processes and RPO/RTO targets.
4. **Backup Across Regions**: For critical tables, create periodic on-demand backups and copy them to other regions for geographic redundancy.
5. **Automate Backup Processes**: Use AWS Backup service to automate backup schedules, retention policies, and cross-region copy for DynamoDB tables.
6. **Document Backup Strategy**: Maintain documentation of your backup retention policies, recovery procedures, and responsible personnel.
7. **Monitor Backup Status**: Set up CloudWatch alarms to monitor backup job failures and ensure backup policies are executing successfully.
8. **Consider Global Tables**: For mission-critical applications, use global tables for active-active multi-region replication rather than relying solely on backups.

### Cost Optimization

1. **Use On-Demand Pricing Wisely**: PAY_PER_REQUEST is more expensive per request but eliminates waste from over-provisioning - ideal for new or unpredictable workloads.
2. **Right-Size Provisioned Capacity**: For provisioned tables, analyze actual usage patterns and adjust capacity to match actual needs with appropriate buffer.
3. **Enable TTL**: Use time-to-live to automatically delete expired items without consuming write capacity, reducing storage costs.
4. **Use Table Classes**: For infrequently accessed data (accessed less than twice per month), use STANDARD_INFREQUENT_ACCESS table class for 50% storage cost reduction.
5. **Optimize GSI Projections**: Use KEYS_ONLY or INCLUDE projections instead of ALL when possible to reduce index storage and capacity costs.
6. **Delete Unused Indexes**: Remove global secondary indexes that are no longer queried to eliminate unnecessary storage and capacity costs.
7. **Monitor Read/Write Patterns**: Use CloudWatch metrics and Contributor Insights to identify optimization opportunities and eliminate waste.
8. **Use Reserved Capacity**: For predictable, sustained workloads, purchase reserved capacity commitments for up to 53% savings over on-demand pricing.
9. **Implement Efficient Access Patterns**: Optimize application code to minimize reads and writes - use batch operations, caching, and efficient query patterns.
10. **Archive Old Data**: Move historical data to S3 or S3 Glacier for long-term storage at significantly lower cost than keeping it in DynamoDB.

### Monitoring and Operations

1. **Monitor Key Metrics**: Track consumed capacity, throttled requests, user errors, system errors, and latency metrics in CloudWatch.
2. **Set Up CloudWatch Alarms**: Create alarms for throttled requests, error rates, and capacity utilization to detect issues before they impact users.
3. **Enable Contributor Insights**: Use DynamoDB Contributor Insights to identify most accessed items and attributes for optimization opportunities.
4. **Use CloudWatch Logs Insights**: Analyze CloudTrail logs with Logs Insights to understand usage patterns, identify issues, and audit access.
5. **Monitor Stream Processing**: For tables with streams, monitor Lambda function metrics, error rates, and iterator age to ensure timely processing.
6. **Implement Health Checks**: Build application-level health checks that verify DynamoDB table accessibility and performance.
7. **Track Item Count and Size**: Monitor table size metrics to understand growth patterns and plan for capacity and cost management.
8. **Use AWS X-Ray**: Enable X-Ray tracing in your application to analyze DynamoDB call performance and identify optimization opportunities.
9. **Regular Performance Reviews**: Conduct quarterly reviews of DynamoDB usage, costs, and performance to identify optimization opportunities.
10. **Document Operations**: Maintain runbooks for common operational tasks including scaling, recovery, troubleshooting, and optimization procedures.

### DynamoDB Streams and Event Processing

1. **Choose Appropriate Stream View**: Select KEYS_ONLY for minimal data transfer, NEW_IMAGE or OLD_IMAGE for specific use cases, or NEW_AND_OLD_IMAGES for full audit trails.
2. **Implement Idempotent Processing**: Design Lambda functions or stream processors to handle duplicate records gracefully as DynamoDB Streams provides at-least-once delivery.
3. **Configure Appropriate Batch Size**: Balance Lambda concurrency and cost by configuring appropriate batch sizes (1-1000 records) for stream event source mappings.
4. **Monitor Iterator Age**: Set alarms for high iterator age, which indicates stream processing lag and potential data backlog.
5. **Handle Failures Gracefully**: Implement dead-letter queues and error handling in stream processors to prevent data loss from processing failures.
6. **Use Kinesis Adapter**: For complex stream processing, consider using Kinesis Client Library with DynamoDB Streams Kinesis Adapter for advanced features.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/dynamodb-table/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table/tree/master/examples
- **AWS DynamoDB Documentation**: https://docs.aws.amazon.com/dynamodb/
- **DynamoDB Developer Guide**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/
- **DynamoDB Best Practices**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html
- **DynamoDB Pricing**: https://aws.amazon.com/dynamodb/pricing/
- **Data Modeling Guide**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/data-modeling.html
- **DynamoDB Streams**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html
- **Global Tables**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GlobalTables.html
- **Capacity Planning**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/capacity-planning.html
- **Security Best Practices**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/security-best-practices.html
- **Performance Optimization**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PerformanceOptimization.html
- **Terraform AWS Provider DynamoDB**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table
- **AWS Well-Architected Framework**: https://aws.amazon.com/architecture/well-architected/

## Notes for AI Agents

When using this module in automated workflows:

1. **Choose Billing Mode Carefully**: Use PAY_PER_REQUEST for unpredictable workloads, PROVISIONED with autoscaling for steady traffic patterns
2. **Enable PITR by Default**: Always enable point-in-time recovery for production tables to prevent data loss
3. **Design Partition Keys Wisely**: Select high-cardinality partition keys that distribute traffic evenly across partitions
4. **Minimize Global Secondary Indexes**: Each GSI adds cost - only create indexes for essential query patterns
5. **Enable Encryption**: Always enable server-side encryption, preferably with customer-managed KMS keys
6. **Use Appropriate Table Class**: Consider STANDARD_INFREQUENT_ACCESS for data accessed less than twice per month
7. **Enable TTL for Temporary Data**: Use time-to-live for automatic expiration of temporary items without consuming write capacity
8. **Monitor Throttled Requests**: Set up alarms for throttled requests to detect capacity issues early
9. **Tag Consistently**: Implement comprehensive tagging including Environment, Application, Owner, and DataClassification
10. **Test Before Production**: Always test DynamoDB schema and capacity settings in non-production environments first
11. **Document Access Patterns**: Clearly document all access patterns and query requirements to validate table design
12. **Plan for Scale**: Design tables to handle 10x current load to avoid costly schema changes later
