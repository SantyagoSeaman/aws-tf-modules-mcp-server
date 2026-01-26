# Terraform AWS MSK Kafka Cluster Module

## Module Information

- **Module Name**: `msk-kafka-cluster`
- **Source**: `terraform-aws-modules/msk-kafka-cluster/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-msk-kafka-cluster
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/msk-kafka-cluster/aws/latest
- **Latest Version**: 3.1.0
- **Purpose**: Terraform module to create AWS Managed Streaming for Apache Kafka (MSK) clusters with provisioned and serverless configurations
- **Service**: AWS Managed Streaming for Apache Kafka (Amazon MSK)
- **Category**: Streaming, Data Integration, Messaging
- **Keywords**: msk, kafka, kafka-cluster, streaming, event-streaming, message-broker, sasl-scram, sasl-iam, schema-registry, msk-connect, serverless, encryption, monitoring, autoscaling, vpc-connectivity
- **Use For**: real-time data streaming pipelines, event-driven microservices architectures, log aggregation and analysis, change data capture (CDC) for databases, IoT data ingestion, clickstream analytics, financial transaction processing, social media feed processing, distributed system event buses, data lake ingestion, message queue replacement, application activity tracking

## Description

The AWS MSK Kafka Cluster Terraform module provides a comprehensive solution for creating and managing fully managed Apache Kafka clusters on AWS. Amazon Managed Streaming for Apache Kafka (MSK) is a fully managed service that enables building and running applications that use Apache Kafka to process streaming data without the operational complexity of managing Kafka infrastructure. The module supports both provisioned clusters with customizable broker configurations and serverless clusters with automatic capacity management, making it suitable for various streaming data workloads from development to enterprise-scale production deployments.

This module abstracts the complexity of MSK cluster configuration by providing a declarative interface for defining broker nodes, storage volumes, encryption settings, monitoring configurations, and authentication mechanisms. It handles critical operational aspects including multi-AZ deployment for high availability, automatic broker node recovery, ZooKeeper or KRaft controller management, and integration with AWS services like CloudWatch for logging, KMS for encryption, Secrets Manager for credential management, and Glue for schema registries. The module supports advanced Kafka features including SASL/SCRAM and IAM authentication, tiered storage for cost-effective data retention, and VPC connectivity for private network access.

The module includes comprehensive support for operational excellence through configurable monitoring with JMX and Node exporters for Prometheus integration, structured logging to CloudWatch, S3, and Kinesis Firehose, and storage autoscaling to handle dynamic workload requirements. With built-in submodule support for serverless MSK deployments, schema registry management, Kafka Connect worker configurations, and custom plugin integration, this module enables organizations to deploy production-ready Kafka infrastructure using infrastructure-as-code best practices while maintaining compatibility with existing Apache Kafka applications and tooling.

## Key Features

- **Provisioned and Serverless Clusters**: Support for both provisioned clusters with specific broker configurations and serverless clusters with automatic scaling
- **Multi-AZ High Availability**: Deploy broker nodes across multiple Availability Zones for fault tolerance and automatic recovery
- **Flexible Kafka Versions**: Choose from multiple Apache Kafka versions including support for KRaft mode (ZooKeeper-free)
- **Broker Node Configuration**: Customizable instance types, storage volumes, and EBS volume configurations for broker nodes
- **Storage Autoscaling**: Automatic EBS volume expansion based on utilization thresholds with configurable capacity targets
- **Tiered Storage**: Cost-effective unlimited storage with automatic data tiering between high-performance and low-cost storage
- **Comprehensive Encryption**: Encryption at rest with KMS, encryption in transit with TLS, and configurable client-broker encryption modes
- **Multiple Authentication Methods**: Support for SASL/SCRAM, SASL/IAM, and mTLS client authentication
- **Enhanced Monitoring**: Integration with CloudWatch for metrics, JMX Exporter, and Prometheus Node Exporter for comprehensive observability
- **Structured Logging**: Stream broker logs to CloudWatch Logs, S3 buckets, and Kinesis Firehose for centralized log management
- **VPC Connectivity**: Multi-VPC and cross-account access with VPC peering connections and cluster policies
- **Schema Registry Integration**: AWS Glue Schema Registry support for schema management and validation
- **Kafka Connect Support**: MSK Connect configurations with custom plugins for streaming data integrations
- **Security Group Management**: Configurable security groups for controlling network access to broker nodes
- **Bootstrap Broker Endpoints**: Multiple connection endpoints for plaintext, TLS, SASL/SCRAM, SASL/IAM, and public access scenarios
- **Cluster Policies**: IAM-based cluster policies for cross-account access and fine-grained permission control
- **Custom Configuration**: Support for custom Kafka broker configurations and server properties
- **Open Monitoring**: Integration with Prometheus and Grafana for cluster and broker-level metrics
- **Public Access**: Optional public internet access to brokers for hybrid cloud and external client scenarios
- **Serverless Submodule**: Dedicated submodule for serverless MSK deployments with simplified configuration

## Main Use Cases

1. **Real-Time Data Streaming Pipelines**: Build high-throughput data pipelines for real-time analytics and event processing
2. **Event-Driven Microservices**: Implement asynchronous communication between microservices using Kafka as the event bus
3. **Log Aggregation**: Centralize application and system logs from distributed services for analysis and monitoring
4. **Change Data Capture (CDC)**: Stream database changes to downstream systems for data synchronization and analytics
5. **IoT Data Ingestion**: Collect and process high-volume sensor and device data from IoT deployments
6. **Clickstream Analytics**: Capture and analyze user behavior data from web and mobile applications in real-time
7. **Financial Transaction Processing**: Process payment transactions, stock trades, and banking events with high reliability
8. **Social Media Feed Processing**: Aggregate and process social media posts, comments, and interactions at scale
9. **Data Lake Ingestion**: Stream operational data into S3 data lakes for long-term storage and batch processing
10. **Application Activity Tracking**: Monitor user actions, system events, and application metrics for observability and debugging

## Submodules

This module contains the following submodules:

### 1. serverless

- **Purpose**: Creates AWS MSK Serverless clusters with automatic capacity management and pay-per-use pricing
- **Source**: `terraform-aws-modules/msk-kafka-cluster/aws//modules/serverless`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/msk-kafka-cluster/aws/latest/submodules/serverless
- **Key Features**: Automatic scaling, simplified configuration, no broker management, cluster policies for cross-account access
- **Use Cases**: Variable workloads, development/testing environments, applications with unpredictable traffic, cost-optimized deployments

## Submodule 1: serverless

### Description

The serverless submodule provides a simplified interface for creating MSK Serverless clusters, which automatically scale compute and storage capacity based on workload demands without requiring capacity planning or broker node management. MSK Serverless uses a consumption-based pricing model, making it ideal for applications with variable or unpredictable streaming workloads where provisioned clusters may result in over-provisioning or under-utilization.

### Key Features

- Automatic compute and storage scaling based on workload demand
- No broker node or instance type configuration required
- Built-in high availability across multiple Availability Zones
- Support for IAM authentication and VPC networking
- Cluster policy configuration for cross-account and multi-VPC access
- Simplified configuration with minimal required parameters

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether serverless cluster resources will be created |
| `name` | `string` | `null` | Name of the MSK serverless cluster |
| `subnet_ids` | `list(string)` | `null` | List of subnets in at least two different Availability Zones |
| `security_group_ids` | `list(string)` | `null` | Up to five security groups controlling inbound and outbound traffic |
| `create_cluster_policy` | `bool` | `false` | Determines whether to create an MSK cluster policy |
| `cluster_policy_statements` | `any` | `null` | Map of policy statements for cluster policy |
| `cluster_source_policy_documents` | `list(string)` | `null` | Source policy documents for cluster policy |
| `cluster_override_policy_documents` | `list(string)` | `null` | Override policy documents for cluster policy |
| `tags` | `map(string)` | `{}` | Map of tags to assign to the resources created |

### Main Outputs

| Output | Description |
|--------|-------------|
| `serverless_arn` | The ARN of the serverless cluster |
| `serverless_cluster_uuid` | UUID of the serverless cluster for use in IAM policies |

### Usage Example

```hcl
module "msk_serverless" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws//modules/serverless"
  version = "~> 3.1"

  name = "dev-kafka-serverless"

  # Network configuration
  subnet_ids         = module.vpc.private_subnets
  security_group_ids = [module.kafka_sg.security_group_id]

  # Cluster policy for cross-account access
  create_cluster_policy = true
  cluster_policy_statements = {
    consumer = {
      sid        = "AllowConsumerAccess"
      principals = [{ type = "AWS", identifiers = ["arn:aws:iam::123456789012:root"] }]
      actions    = ["kafka:DescribeCluster", "kafka:GetBootstrapBrokers"]
    }
  }

  tags = {
    Environment = "development"
    Type        = "serverless"
  }
}

output "kafka_bootstrap_servers" {
  description = "Bootstrap servers for Kafka clients"
  value       = module.msk_serverless.serverless_arn
}
```

## Main Input Variables

### Required Variables

| Variable | Type | Description |
|----------|------|-------------|
| `broker_node_client_subnets` | `list(string)` | Subnets for client VPC connectivity (broker count must be multiple of subnet count) |
| `broker_node_instance_type` | `string` | EC2 instance type for Kafka brokers (e.g., `kafka.m5.large`) |
| `kafka_version` | `string` | Desired Kafka software version (e.g., `"3.5.1"`) |
| `number_of_broker_nodes` | `number` | Total broker nodes (must be multiple of subnets count, minimum 3 for production) |

### Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether cluster resources will be created |
| `name` | `string` | `"msk"` | Name of the MSK cluster |
| `broker_node_security_groups` | `list(string)` | `[]` | Security groups to associate with broker nodes |
| `broker_node_storage_info` | `object` | `null` | Storage volume config (EBS with optional throughput/provisioned IOPS) |
| `broker_node_az_distribution` | `string` | `null` | Distribution of broker nodes across availability zones |
| `enhanced_monitoring` | `string` | `null` | CloudWatch monitoring level (e.g., `PER_TOPIC_PER_PARTITION`) |
| `encryption_at_rest_kms_key_arn` | `string` | `null` | KMS key ARN for data encryption at rest |
| `encryption_in_transit_client_broker` | `string` | `null` | Client-broker encryption: `TLS`, `TLS_PLAINTEXT`, or `PLAINTEXT` |
| `encryption_in_transit_in_cluster` | `bool` | `null` | Whether broker-to-broker communication is encrypted |
| `client_authentication` | `object` | `null` | Authentication settings object with `sasl` and `tls` blocks |
| `configuration_name` | `string` | `null` | Name of the configuration to use for the cluster |
| `configuration_description` | `string` | `null` | Description of the configuration |
| `configuration_server_properties` | `map(string)` | `{}` | Custom Kafka broker properties (e.g., `auto.create.topics.enable`) |
| `jmx_exporter_enabled` | `bool` | `false` | Enable JMX Exporter for Prometheus metrics |
| `node_exporter_enabled` | `bool` | `false` | Enable Node Exporter for Prometheus metrics |
| `cloudwatch_logs_enabled` | `bool` | `false` | Stream broker logs to CloudWatch Logs |
| `cloudwatch_log_group` | `string` | `null` | Name of the CloudWatch Log Group |
| `firehose_logs_enabled` | `bool` | `false` | Stream broker logs to Kinesis Data Firehose |
| `firehose_delivery_stream` | `string` | `null` | Name of the Kinesis Data Firehose delivery stream |
| `s3_logs_enabled` | `bool` | `false` | Stream broker logs to S3 |
| `s3_logs_bucket` | `string` | `null` | Name of the S3 bucket for logs |
| `s3_logs_prefix` | `string` | `null` | Prefix for S3 log objects |
| `storage_mode` | `string` | `null` | Storage mode: `LOCAL` or `TIERED` |
| `enable_storage_autoscaling` | `bool` | `true` | Enable automatic storage scaling |
| `scaling_max_capacity` | `number` | `250` | Maximum storage capacity in GB for auto-scaling |
| `scaling_target_value` | `number` | `70` | Storage utilization percentage trigger for scaling |
| `create_scram_secret_association` | `bool` | `false` | Create SASL/SCRAM secret association |
| `scram_secret_association_secret_arn_list` | `list(string)` | `[]` | AWS Secrets Manager ARNs for SCRAM authentication |
| `vpc_connections` | `map(object)` | `{}` | VPC connections with authentication and security settings |
| `create_cluster_policy` | `bool` | `false` | Create MSK cluster policy for cross-account access |
| `schema_registries` | `map(object)` | `{}` | Glue schema registries configuration |
| `schemas` | `map(object)` | `{}` | Schemas within registry (name, format, compatibility, definition) |
| `connect_custom_plugins` | `map(object)` | `{}` | MSK Connect custom plugin configs |
| `rebalancing` | `object` | `null` | Intelligent rebalancing configuration |
| `timeouts` | `map(string)` | `{}` | Terraform resource management timeouts |
| `tags` | `map(string)` | `{}` | Tags to assign to all created resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | Amazon Resource Name (ARN) of the MSK cluster |
| `bootstrap_brokers` | Comma separated list of one or more hostname:port pairs of Kafka brokers |
| `bootstrap_brokers_plaintext` | Comma separated list of one or more DNS names (or IP addresses) and plaintext port pairs |
| `bootstrap_brokers_sasl_iam` | One or more DNS names (or IP addresses) and SASL IAM port pairs |
| `bootstrap_brokers_sasl_scram` | One or more DNS names (or IP addresses) and SASL SCRAM port pairs |
| `bootstrap_brokers_tls` | One or more DNS names (or IP addresses) and TLS port pairs |
| `bootstrap_brokers_public_plaintext` | One or more DNS names (or IP addresses) and public plaintext port pairs |
| `bootstrap_brokers_public_sasl_iam` | One or more DNS names (or IP addresses) and public SASL IAM port pairs |
| `bootstrap_brokers_public_sasl_scram` | One or more DNS names (or IP addresses) and public SASL SCRAM port pairs |
| `bootstrap_brokers_public_tls` | One or more DNS names (or IP addresses) and public TLS port pairs |
| `bootstrap_brokers_vpc_connectivity_plaintext` | One or more DNS names (or IP addresses) and VPC connectivity plaintext port pairs |
| `bootstrap_brokers_vpc_connectivity_sasl_iam` | One or more DNS names (or IP addresses) and VPC connectivity SASL IAM port pairs |
| `bootstrap_brokers_vpc_connectivity_sasl_scram` | One or more DNS names (or IP addresses) and VPC connectivity SASL SCRAM port pairs |
| `bootstrap_brokers_vpc_connectivity_tls` | One or more DNS names (or IP addresses) and VPC connectivity TLS port pairs |
| `cluster_name` | The cluster name of the MSK cluster |
| `cluster_uuid` | UUID of the MSK cluster, for use in IAM policies |
| `current_version` | Current version of the MSK Cluster |
| `zookeeper_connect_string` | A comma separated list of one or more hostname:port pairs to connect to the Apache Zookeeper cluster |
| `zookeeper_connect_string_tls` | A comma separated list of one or more hostname:port pairs to connect to the Apache Zookeeper cluster via TLS |
| `configuration_arn` | Amazon Resource Name (ARN) of the configuration |
| `configuration_latest_revision` | Latest revision of the configuration |
| `scram_secret_association_id` | Amazon Resource Name (ARN) of the MSK cluster |
| `appautoscaling_policy_arn` | ARN assigned by AWS to the scaling policy |
| `appautoscaling_policy_name` | Scaling policy's name |
| `appautoscaling_policy_policy_type` | Scaling policy's type |
| `cloudwatch_log_group_arn` | The Amazon Resource Name (ARN) specifying the log group |
| `cloudwatch_log_group_name` | Name of CloudWatch Log Group |
| `schema_registry_arn` | Amazon Resource Name (ARN) of Glue Schema Registry |
| `schema_registry_id` | Amazon Resource Name (ARN) of Glue Schema Registry |
| `schema_registry_name` | The name of the Glue Schema Registry |

## Usage Examples

### Example 1: Basic MSK Cluster

```hcl
module "msk_kafka_cluster" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.1"

  name                   = "my-kafka-cluster"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.t3.small"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 100 }
  }

  encryption_in_transit_client_broker = "TLS"
  encryption_in_transit_in_cluster    = true

  tags = {
    Environment = "development"
    Team        = "data-platform"
  }
}
```

### Example 2: Production Cluster with SASL/SCRAM Authentication

```hcl
# Create secret for SCRAM authentication (name must start with "AmazonMSK_")
resource "aws_secretsmanager_secret" "kafka_user" {
  name = "AmazonMSK_kafka_user"
}

resource "aws_secretsmanager_secret_version" "kafka_user" {
  secret_id = aws_secretsmanager_secret.kafka_user.id
  secret_string = jsonencode({
    username = "kafka_user"
    password = random_password.kafka_user.result
  })
}

resource "random_password" "kafka_user" {
  length  = 32
  special = true
}

module "msk_production" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.1"

  name                   = "prod-kafka"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 6  # 2 brokers per AZ across 3 AZs

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.xlarge"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 500 }
  }

  # Enhanced monitoring
  enhanced_monitoring = "PER_TOPIC_PER_BROKER"

  # Authentication using new object structure (v3.x)
  client_authentication = {
    sasl = { scram = true }
  }
  create_scram_secret_association          = true
  scram_secret_association_secret_arn_list = [aws_secretsmanager_secret.kafka_user.arn]

  # Encryption
  encryption_at_rest_kms_key_arn      = module.kms.key_arn
  encryption_in_transit_client_broker = "TLS"
  encryption_in_transit_in_cluster    = true

  # Logging
  cloudwatch_logs_enabled = true
  s3_logs_enabled         = true
  s3_logs_bucket          = module.s3_logs.s3_bucket_id
  s3_logs_prefix          = "kafka-logs/"

  # Storage autoscaling
  enable_storage_autoscaling = true
  scaling_max_capacity       = 1024
  scaling_target_value       = 80

  tags = {
    Environment = "production"
    Compliance  = "required"
  }
}
```

### Example 3: Cluster with Monitoring and Observability

```hcl
module "msk_monitored" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.1"

  name                   = "monitored-kafka"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.large"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 200 }
  }

  # Enhanced monitoring with per-partition detail
  enhanced_monitoring = "PER_TOPIC_PER_PARTITION"

  # Prometheus exporters for Grafana integration
  jmx_exporter_enabled  = true
  node_exporter_enabled = true

  # Multi-destination logging
  cloudwatch_logs_enabled = true
  cloudwatch_log_group    = "/aws/msk/monitored-kafka"

  firehose_logs_enabled    = true
  firehose_delivery_stream = aws_kinesis_firehose_delivery_stream.kafka_logs.name

  s3_logs_enabled = true
  s3_logs_bucket  = module.s3_logs.s3_bucket_id
  s3_logs_prefix  = "kafka/broker-logs/"

  encryption_in_transit_client_broker = "TLS"
  encryption_in_transit_in_cluster    = true

  tags = {
    Environment = "production"
    Monitoring  = "enhanced"
  }
}
```

### Example 4: Cluster with Schema Registry

```hcl
module "msk_with_schema_registry" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.1"

  name                   = "kafka-with-schemas"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.large"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 100 }
  }

  # Schema Registries (v3.x uses map structure)
  schema_registries = {
    main = {
      name        = "kafka-schemas"
      description = "Schema registry for Kafka topics"
    }
  }

  schemas = {
    user_events = {
      schema_registry_name = "kafka-schemas"
      schema_name          = "UserEvents"
      description          = "Schema for user event data"
      compatibility        = "BACKWARD"
      data_format          = "AVRO"
      schema_definition    = file("${path.module}/schemas/user_events.avsc")
    }
    order_events = {
      schema_registry_name = "kafka-schemas"
      schema_name          = "OrderEvents"
      description          = "Schema for order event data"
      compatibility        = "FORWARD"
      data_format          = "AVRO"
      schema_definition    = file("${path.module}/schemas/order_events.avsc")
    }
  }

  encryption_in_transit_client_broker = "TLS"
  encryption_in_transit_in_cluster    = true

  tags = {
    Environment      = "production"
    SchemaManagement = "enabled"
  }
}
```

### Example 5: Cluster with IAM Authentication

```hcl
module "msk_iam_auth" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.1"

  name                   = "kafka-iam-auth"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.large"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 100 }
  }

  # Enable IAM authentication (v3.x object structure)
  client_authentication = {
    sasl = { iam = true }
  }

  encryption_in_transit_client_broker = "TLS"
  encryption_in_transit_in_cluster    = true

  tags = {
    Environment    = "production"
    Authentication = "iam"
  }
}

# IAM policy for Kafka client applications
resource "aws_iam_policy" "kafka_client" {
  name = "kafka-client-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["kafka-cluster:Connect", "kafka-cluster:DescribeCluster"]
        Resource = module.msk_iam_auth.arn
      },
      {
        Effect   = "Allow"
        Action   = ["kafka-cluster:*Topic*", "kafka-cluster:WriteData", "kafka-cluster:ReadData"]
        Resource = "arn:aws:kafka:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic/${module.msk_iam_auth.cluster_uuid}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["kafka-cluster:AlterGroup", "kafka-cluster:DescribeGroup"]
        Resource = "arn:aws:kafka:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:group/${module.msk_iam_auth.cluster_uuid}/*"
      }
    ]
  })
}
```

### Example 6: Cluster with VPC Connectivity

```hcl
module "msk_vpc_connectivity" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.1"

  name                   = "kafka-vpc-peering"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.large"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 100 }
  }

  # Enable VPC connectivity for multi-VPC/cross-account access
  vpc_connections = {
    peered_vpc = {
      authentication     = "SASL_IAM"
      client_subnets     = module.client_vpc.private_subnets
      security_groups    = [module.client_sg.security_group_id]
      target_cluster_arn = module.msk_vpc_connectivity.arn
      vpc_id             = module.client_vpc.vpc_id
    }
  }

  client_authentication = {
    sasl = { iam = true }
  }

  encryption_in_transit_client_broker = "TLS"
  encryption_in_transit_in_cluster    = true

  tags = {
    Environment  = "production"
    Connectivity = "multi-vpc"
  }
}
```

### Example 7: Serverless MSK Cluster

```hcl
module "msk_serverless" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws//modules/serverless"
  version = "~> 3.1"

  name = "serverless-kafka"

  subnet_ids         = module.vpc.private_subnets
  security_group_ids = [module.kafka_sg.security_group_id]

  # Cluster policy for cross-account access
  create_cluster_policy = true
  cluster_policy_statements = {
    producer_access = {
      sid        = "AllowProducerAccess"
      principals = [{ type = "AWS", identifiers = ["arn:aws:iam::111111111111:role/KafkaProducer"] }]
      actions    = ["kafka-cluster:Connect", "kafka-cluster:WriteData", "kafka-cluster:CreateTopic"]
      resources  = ["*"]
    }
    consumer_access = {
      sid        = "AllowConsumerAccess"
      principals = [{ type = "AWS", identifiers = ["arn:aws:iam::222222222222:role/KafkaConsumer"] }]
      actions    = ["kafka-cluster:Connect", "kafka-cluster:ReadData", "kafka-cluster:DescribeTopic"]
      resources  = ["*"]
    }
  }

  tags = {
    Environment = "development"
    Type        = "serverless"
  }
}
```

### Example 8: Cluster with Tiered Storage

```hcl
module "msk_tiered_storage" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.1"

  name                   = "kafka-tiered"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.2xlarge"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 1000 }
  }

  # Enable tiered storage for cost-effective unlimited retention
  storage_mode = "TIERED"

  # Custom Kafka broker configuration
  configuration_name        = "tiered-storage-config"
  configuration_description = "Configuration for tiered storage"
  configuration_server_properties = {
    "auto.create.topics.enable"  = "true"
    "default.replication.factor" = "3"
    "min.insync.replicas"        = "2"
    "num.io.threads"             = "8"
    "num.network.threads"        = "5"
    "num.partitions"             = "1"
  }

  encryption_in_transit_client_broker = "TLS"
  encryption_in_transit_in_cluster    = true

  tags = {
    Environment = "production"
    Storage     = "tiered"
  }
}
```

## Best Practices

### Cluster Sizing and Configuration

1. **Choose Appropriate Instance Types**: Use m5 instances for balanced workloads, r5 for memory-intensive consumers, t3 for development/testing only
2. **Plan Broker Node Count**: Deploy at least 3 broker nodes across 3 AZs for production; use multiples of AZ count for even distribution
3. **Size Storage Appropriately**: Calculate retention requirements considering message size, throughput, and retention period; start with 500GB for production
4. **Enable Storage Autoscaling**: Set scaling_max_capacity to 2-3x initial capacity with target utilization of 70-80% for headroom
5. **Select Kafka Version Carefully**: Use the latest stable version for new clusters; test upgrades in non-production before applying to production
6. **Consider KRaft Mode**: For new deployments, evaluate KRaft (ZooKeeper-free) Kafka versions for simplified operations
7. **Distribute Across AZs**: Use broker_node_az_distribution = "DEFAULT" to evenly distribute brokers across Availability Zones

### Security and Authentication

1. **Enable Encryption at Rest**: Always use KMS encryption for data at rest; use custom KMS keys for audit trail and key rotation control
2. **Enforce TLS for Transit**: Set encryption_in_transit_client_broker = "TLS" and encryption_in_transit_in_cluster = true for all production clusters
3. **Use IAM Authentication**: Prefer SASL/IAM over SCRAM for better integration with AWS services and credential management
4. **Implement SCRAM Correctly**: Store SCRAM credentials in Secrets Manager with automatic rotation; never hardcode credentials
5. **Apply Security Groups**: Restrict ingress to Kafka ports (9092, 9094, 9096) from only necessary sources; use security group references
6. **Enable mTLS When Required**: Use client_authentication_tls_certificate_authority_arns for mutual TLS when client certificate validation is needed
7. **Avoid Unauthenticated Access**: Never enable client_authentication_unauthenticated in production environments
8. **Implement Cluster Policies**: Use cluster policies for cross-account access instead of overly permissive security groups

### Monitoring and Observability

1. **Enable Enhanced Monitoring**: Use "PER_TOPIC_PER_BROKER" level for production to get detailed metrics on topic and partition performance
2. **Configure Prometheus Exporters**: Enable both jmx_exporter and node_exporter for integration with Prometheus and Grafana
3. **Stream Logs to CloudWatch**: Enable cloudwatch_logs with appropriate retention periods for troubleshooting and audit compliance
4. **Set Up Log Archival**: Use s3_logs for long-term log retention and cost-effective storage with lifecycle policies
5. **Monitor Key Metrics**: Track under-replicated partitions, offline partitions, consumer lag, broker CPU, memory, and disk utilization
6. **Create CloudWatch Alarms**: Set alarms for critical metrics like broker down, offline partitions, high consumer lag, and storage usage
7. **Use Kafka Lag Exporter**: Deploy external lag monitoring tools for consumer group lag visibility and alerting

### Performance Optimization

1. **Optimize Topic Configurations**: Set appropriate replication factor (3 for production), min.insync.replicas (2), and partition count based on throughput
2. **Tune Broker Settings**: Use custom configurations for num.io.threads, num.network.threads based on workload characteristics
3. **Configure Producer Settings**: Set appropriate acks, compression.type, batch.size, and linger.ms for latency vs throughput tradeoff
4. **Optimize Consumer Groups**: Size consumer groups based on partition count; avoid over-subscription or under-subscription
5. **Enable Compression**: Use compression.type = "snappy" or "lz4" for balanced compression ratio and CPU usage
6. **Monitor Replication Lag**: Track replica.lag.time.max.ms and adjust based on network latency and data volume
7. **Use Tiered Storage**: Enable storage_mode = "TIERED" for topics with long retention to reduce costs while maintaining performance

### Cost Optimization

1. **Right-Size Broker Instances**: Start with smaller instance types and scale up based on actual metrics; avoid over-provisioning
2. **Use Serverless for Variable Workloads**: Consider MSK Serverless for development, testing, or applications with unpredictable traffic patterns
3. **Implement Data Retention Policies**: Set appropriate retention periods; don't retain data longer than necessary
4. **Enable Tiered Storage**: Use tiered storage for cost-effective long-term retention without deleting data
5. **Optimize Storage Autoscaling**: Set conservative target values (70-80%) to avoid over-provisioning while maintaining headroom
6. **Delete Unused Topics**: Regularly audit and remove unused topics to free storage and reduce complexity
7. **Monitor Data Transfer Costs**: Keep producers and consumers in the same region as the MSK cluster to minimize cross-AZ/cross-region charges

### High Availability and Disaster Recovery

1. **Deploy Multi-AZ**: Always distribute brokers across at least 3 Availability Zones for fault tolerance
2. **Set Replication Factor**: Use replication.factor = 3 for critical topics to ensure data durability
3. **Configure min.insync.replicas**: Set to 2 for production topics to balance durability and availability
4. **Plan for Broker Failures**: MSK automatically recovers failed brokers; ensure client retry logic handles temporary unavailability
5. **Monitor Partition Health**: Track under-replicated and offline partitions; investigate and resolve quickly
6. **Test Failover Scenarios**: Regularly test application behavior during broker failures and AZ outages
7. **Implement Client-Side Resilience**: Configure producer retries, consumer rebalance listeners, and exponential backoff

### Operational Excellence

1. **Use Infrastructure as Code**: Manage all MSK resources through Terraform for reproducibility and version control
2. **Implement Tagging Strategy**: Apply consistent tags for cost allocation, environment identification, and resource management
3. **Document Configuration Changes**: Maintain documentation of custom configurations and their rationale
4. **Plan Capacity Ahead**: Monitor growth trends and plan capacity upgrades before hitting limits
5. **Automate Operational Tasks**: Use automation for topic creation, consumer group management, and cluster upgrades
6. **Version Control Schemas**: Store schema definitions in version control and use schema registry for validation
7. **Implement Change Management**: Use Terraform plan before applying changes; test in non-production first

### Schema Management

1. **Use Schema Registry**: Enable schema registry for structured data to enforce data contracts and compatibility
2. **Define Compatibility Rules**: Choose appropriate compatibility mode (BACKWARD, FORWARD, FULL) based on evolution requirements
3. **Version Schemas**: Increment schema versions for changes; never modify existing schema versions
4. **Validate Before Production**: Test schema changes in development with realistic data before deploying to production
5. **Document Schemas**: Include descriptions and examples in schema definitions for developer clarity

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-msk-kafka-cluster
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/msk-kafka-cluster/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-msk-kafka-cluster/tree/master/examples
- **AWS MSK Documentation**: https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html
- **AWS MSK Developer Guide**: https://docs.aws.amazon.com/msk/latest/developerguide/
- **MSK Encryption**: https://docs.aws.amazon.com/msk/latest/developerguide/msk-encryption.html
- **MSK Monitoring**: https://docs.aws.amazon.com/msk/latest/developerguide/monitoring.html
- **MSK Connect**: https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect.html
- **MSK Serverless**: https://docs.aws.amazon.com/msk/latest/developerguide/serverless.html
- **Apache Kafka Documentation**: https://kafka.apache.org/documentation/
- **AWS MSK Best Practices**: https://docs.aws.amazon.com/msk/latest/developerguide/best-practices.html
- **AWS MSK Pricing**: https://aws.amazon.com/msk/pricing/
- **Kafka Client Configuration**: https://kafka.apache.org/documentation/#configuration
- **MSK IAM Access Control**: https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html

## Notes for AI Agents

When using this module in automated workflows:

### Critical Configuration Rules
1. **Broker Node Count**: `number_of_broker_nodes` MUST be a multiple of `broker_node_client_subnets` count (e.g., 3 subnets → 3, 6, 9 brokers)
2. **Subnet Requirements**: MSK requires subnets in at least 2 AZs; use 3 AZs for production high availability
3. **Authentication Object (v3.x)**: Use `client_authentication = { sasl = { iam = true } }` instead of deprecated `client_authentication_sasl_iam = true`
4. **SCRAM Secret Naming**: Secrets Manager secret names MUST start with `"AmazonMSK_"` for SCRAM authentication

### Common Patterns
5. **Storage Sizing**: Use 100+ GiB for development, 500+ GiB for production; enable `enable_storage_autoscaling = true` with `scaling_max_capacity`
6. **Security Group Ports**: Allow 9092 (plaintext), 9094 (TLS), 9096 (SASL/IAM), 9098 (SASL/SCRAM) based on auth method
7. **Bootstrap Brokers**: Select output based on authentication: `bootstrap_brokers_sasl_iam`, `bootstrap_brokers_sasl_scram`, `bootstrap_brokers_tls`
8. **Schema Registry**: Use `schema_registries` map (v3.x) instead of `create_schema_registry`/`schema_registry_name`

### Limitations and Gotchas
9. **Encryption Changes**: Changing encryption settings requires cluster recreation; plan data migration
10. **Serverless Limitations**: MSK Serverless doesn't support custom configurations, tiered storage, or public access
11. **Configuration Updates**: Some `configuration_server_properties` changes require cluster restart
12. **Autoscaling Behavior**: Storage autoscaling is gradual; don't rely on it for sudden traffic spikes

### Version-Specific Notes
13. **Module Version**: v3.x uses `client_authentication` object; v2.x used separate boolean flags
14. **Kafka Version**: Use 3.5.1+ for latest features; verify client library compatibility
15. **KRaft Mode**: Kafka 3.3.1+ supports ZooKeeper-free operation but may have limited tooling support

### Cost Considerations
16. **Pricing Model**: MSK charges by broker-hour + storage GB-month + data transfer; estimate before deployment
