# Terraform AWS MSK Kafka Cluster Module

## Module Information

- **Module Name**: `msk-kafka-cluster`
- **Source**: `terraform-aws-modules/msk-kafka-cluster/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-msk-kafka-cluster
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/msk-kafka-cluster/aws/latest
- **Latest Version**: 3.3.0
- **Purpose**: Terraform module to create AWS Managed Streaming for Apache Kafka (MSK) provisioned and serverless clusters, including topics, Kafka Connect resources, schema registries, and cluster policies
- **Service**: AWS Managed Streaming for Apache Kafka (Amazon MSK)
- **Category**: Streaming, Data Integration, Messaging
- **Keywords**: msk, kafka, kafka-cluster, streaming, event-streaming, message-broker, sasl-scram, sasl-iam, mtls, schema-registry, msk-connect, msk-topic, serverless, tiered-storage, kraft, encryption, vpc-connectivity
- **Use For**: real-time data streaming pipelines, event-driven microservices architectures, log aggregation and analysis, change data capture (CDC) for databases, IoT data ingestion, clickstream analytics, financial transaction processing, data lake ingestion, cross-account/multi-VPC Kafka access

## Description

The AWS MSK Kafka Cluster Terraform module provisions and manages fully managed Apache Kafka clusters on AWS, abstracting the operational complexity of running Kafka infrastructure. Amazon Managed Streaming for Apache Kafka (MSK) is a fully managed service for building streaming-data applications, and this module exposes a declarative interface for broker node sizing, storage, encryption, authentication, connectivity, monitoring, and logging. It supports both provisioned clusters with customizable broker configurations and, via the bundled `serverless` submodule, pay-per-use MSK Serverless clusters with automatic capacity management. The current major version (3.x) requires the AWS provider `>= 6.40` and Terraform `>= 1.5.7`, a breaking change introduced in v3.0.0 for prior v2.x users.

Beyond the cluster itself, the module manages the full surrounding footprint: MSK configurations (with support for reusing an externally created configuration via `configuration_arn`/`configuration_revision`), broker connectivity (`broker_node_connectivity_info` for public access, VPC connectivity, and network type), SASL/SCRAM and SASL/IAM and mTLS client authentication, KMS-encrypted data at rest and TLS in transit, multi-VPC/cross-account access via `aws_msk_vpc_connection` resources and IAM-based cluster policies, and a self-managed CloudWatch Log Group (created by default, or an externally supplied one can be referenced) alongside S3 and Kinesis Data Firehose log destinations. AWS Glue Schema Registry integration and Kafka Connect resources (custom plugins and worker configurations) are built directly into the root module — there is no separate Connect submodule.

Operationally, the module supports EBS storage autoscaling, tiered storage for cost-effective long-term retention, JMX/Node Prometheus exporters for open monitoring, and — as of v3.3.0 — native Kafka topic management through the `topics` variable (backed by `aws_msk_topic`, which requires Kafka version > 3.6 and is not available for serverless clusters). This makes it possible to manage an entire Kafka platform — cluster, topics, schemas, connectors, and cross-account policies — as a single Terraform-managed unit while remaining compatible with standard Apache Kafka clients and tooling.

## Key Features

- **Provisioned and Serverless Clusters**: Root module for provisioned clusters plus a dedicated `serverless` submodule for auto-scaling, pay-per-use clusters
- **Multi-AZ High Availability**: Deploy broker nodes across multiple Availability Zones with automatic broker recovery
- **Flexible Kafka Versions**: Choose any supported Apache Kafka version, including KRaft-capable (ZooKeeper-free) releases
- **Configurable Broker Connectivity**: `broker_node_connectivity_info` controls public access, VPC connectivity (with its own client authentication), and `network_type` per broker node group
- **Native Topic Management**: Create and manage Kafka topics declaratively via the `topics` variable (`aws_msk_topic`, Kafka > 3.6, provisioned clusters only)
- **Built-in Kafka Connect Support**: Custom plugins (`connect_custom_plugins`) and worker configurations (`connect_worker_config_*`) are managed directly by the root module
- **Reusable MSK Configuration**: Create a new configuration or reference an externally created one via `configuration_arn`/`configuration_revision`
- **Storage Autoscaling**: Automatic EBS volume expansion based on configurable utilization thresholds and max capacity
- **Tiered Storage**: Cost-effective, effectively unlimited storage with automatic tiering between high-performance and low-cost storage
- **Comprehensive Encryption**: KMS encryption at rest and configurable TLS/plaintext encryption in transit (client-broker and broker-broker)
- **Multiple Authentication Methods**: SASL/SCRAM, SASL/IAM, and mTLS client authentication via a single `client_authentication` object
- **Self-Managed CloudWatch Log Group**: Module creates and KMS-encrypts its own log group by default (`create_cloudwatch_log_group`), or an existing one can be reused
- **Multi-Destination Logging**: Stream broker logs to CloudWatch Logs, S3, and Kinesis Data Firehose simultaneously
- **Enhanced Monitoring & Open Monitoring**: CloudWatch enhanced monitoring levels plus JMX Exporter and Node Exporter for Prometheus/Grafana
- **VPC Connections & Cluster Policies**: Multi-VPC/cross-account access via `aws_msk_vpc_connection` and IAM-based cluster policies
- **Schema Registry Integration**: AWS Glue Schema Registry and schema management with a toggle (`create_schema_registry`) to disable it entirely
- **Bootstrap Broker Endpoints**: Consolidated outputs for plaintext, TLS, SASL/SCRAM, SASL/IAM, public, and VPC-connectivity broker endpoints
- **Provider Region Override**: `region` variable supports the AWS provider's per-resource region override (provider `>= 6.40`)

## Main Use Cases

1. **Real-Time Data Streaming Pipelines**: Build high-throughput data pipelines for real-time analytics and event processing
2. **Event-Driven Microservices**: Implement asynchronous communication between microservices using Kafka as the event bus
3. **Log Aggregation**: Centralize application and system logs from distributed services for analysis and monitoring
4. **Change Data Capture (CDC)**: Stream database changes to downstream systems using MSK Connect connectors (e.g., Debezium)
5. **IoT Data Ingestion**: Collect and process high-volume sensor and device data from IoT deployments
6. **Clickstream Analytics**: Capture and analyze user behavior data from web and mobile applications in real-time
7. **Financial Transaction Processing**: Process payment transactions, stock trades, and banking events with high reliability
8. **Data Lake Ingestion**: Stream operational data into S3 data lakes for long-term storage and batch processing
9. **Cross-Account / Multi-VPC Kafka Access**: Expose a shared cluster to other accounts or VPCs using cluster policies and VPC connections
10. **Variable/Unpredictable Workloads**: Use MSK Serverless for development, testing, or bursty traffic without capacity planning

## Submodules

This module contains the following submodule:

### 1. serverless

- **Purpose**: Creates AWS MSK Serverless clusters with automatic capacity management and pay-per-use pricing
- **Source**: `terraform-aws-modules/msk-kafka-cluster/aws//modules/serverless`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/msk-kafka-cluster/aws/latest/submodules/serverless
- **Key Features**: Automatic scaling, no broker/instance-type management, cluster policies for cross-account access, IAM authentication only
- **Use Cases**: Variable workloads, development/testing environments, applications with unpredictable traffic, cost-optimized deployments

> Note: Kafka Connect (custom plugins, worker configurations) and native topic management are **not** separate submodules — they are managed directly by the root module's variables (`connect_custom_plugins`, `connect_worker_config_*`, `topics`).

## Submodule 1: serverless

### Description

The `serverless` submodule provides a simplified interface for creating MSK Serverless clusters, which automatically scale compute and storage capacity based on workload demand without capacity planning or broker node management. It uses consumption-based pricing, making it ideal for applications with variable or unpredictable streaming workloads. Serverless clusters support IAM authentication only and do not support custom configurations, tiered storage, native topic management (`topics`), or public access.

### Key Features

- Automatic compute and storage scaling based on workload demand
- No broker node or instance type configuration required
- Built-in high availability across multiple Availability Zones
- IAM authentication and standard VPC networking only
- Cluster policy configuration for cross-account and multi-VPC access
- Minimal required configuration (name, subnets, security groups)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether serverless cluster resources will be created |
| `name` | `string` | `null` | Name of the MSK serverless cluster |
| `region` | `string` | `null` | Region where resources are managed (defaults to provider region) |
| `subnet_ids` | `list(string)` | `null` | List of subnets in at least two different Availability Zones |
| `security_group_ids` | `list(string)` | `null` | Up to five security groups controlling inbound and outbound traffic |
| `create_cluster_policy` | `bool` | `false` | Determines whether to create an MSK cluster policy |
| `cluster_policy_statements` | `map(object)` | `null` | Map of policy statements for the cluster policy |
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
  version = "~> 3.3"

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

output "kafka_serverless_arn" {
  value = module.msk_serverless.serverless_arn
}
```

## Main Input Variables

### Required (Functionally) Variables

These have no meaningful default and must be set to produce a working provisioned cluster:

| Variable | Type | Description |
|----------|------|-------------|
| `broker_node_client_subnets` | `list(string)` | Subnets for client VPC connectivity (broker count must be a multiple of subnet count) |
| `broker_node_instance_type` | `string` | EC2 instance type for Kafka brokers (e.g., `kafka.m5.large`) |
| `kafka_version` | `string` | Desired Kafka software version (e.g., `"3.9.x"`) |
| `number_of_broker_nodes` | `number` | Total broker nodes (must be a multiple of subnet count, minimum 3 for production) |

### Key Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether cluster resources will be created |
| `region` | `string` | `null` | Region where resources are managed (defaults to provider region) |
| `name` | `string` | `"msk"` | Name of the MSK cluster |
| `broker_node_security_groups` | `list(string)` | `[]` | Security groups to associate with broker node ENIs |
| `broker_node_storage_info` | `object` | `null` | EBS storage config (`volume_size`, optional `provisioned_throughput`) |
| `broker_node_az_distribution` | `string` | `null` | Broker distribution across AZs (currently only `DEFAULT`) |
| `broker_node_connectivity_info` | `object` | `null` | Public access (`type`), VPC connectivity (`client_authentication`), and `network_type` |
| `enhanced_monitoring` | `string` | `null` | CloudWatch monitoring level (e.g., `PER_TOPIC_PER_PARTITION`) |
| `encryption_at_rest_kms_key_arn` | `string` | `null` | KMS key ARN for data encryption at rest |
| `encryption_in_transit_client_broker` | `string` | `null` | Client-broker encryption: `TLS`, `TLS_PLAINTEXT`, or `PLAINTEXT` (AWS default `TLS`) |
| `encryption_in_transit_in_cluster` | `bool` | `null` | Whether broker-to-broker communication is encrypted |
| `client_authentication` | `object` | `null` | `sasl { iam, scram }`, `tls { certificate_authority_arns }`, `unauthenticated` |
| `create_configuration` | `bool` | `true` | Create a new MSK configuration; set `false` to reuse `configuration_arn`/`configuration_revision` |
| `configuration_arn` / `configuration_revision` | `string` / `number` | `null` | Externally created configuration to use when `create_configuration = false` |
| `configuration_name` / `configuration_description` | `string` | `null` | Name/description for a module-created configuration |
| `configuration_server_properties` | `map(string)` | `{}` | Custom `server.properties` values (e.g., `auto.create.topics.enable`) |
| `jmx_exporter_enabled` / `node_exporter_enabled` | `bool` | `false` | Enable Prometheus JMX / Node exporters |
| `create_cloudwatch_log_group` | `bool` | `true` | Module creates and manages its own CloudWatch Log Group |
| `cloudwatch_log_group_name` | `string` | `null` | Log group name (created if `create_cloudwatch_log_group = true`, else referenced) |
| `cloudwatch_log_group_retention_in_days` | `number` | `0` | Retention period for the module-created log group |
| `cloudwatch_log_group_kms_key_id` | `string` | `null` | KMS key ARN to encrypt the log group |
| `cloudwatch_logs_enabled` | `bool` | `false` | Stream broker logs to CloudWatch Logs |
| `firehose_logs_enabled` / `firehose_delivery_stream` | `bool` / `string` | `false` / `null` | Stream broker logs to Kinesis Data Firehose |
| `s3_logs_enabled` / `s3_logs_bucket` / `s3_logs_prefix` | `bool` / `string` / `string` | `false` / `null` / `null` | Stream broker logs to S3 |
| `storage_mode` | `string` | `null` | `LOCAL` or `TIERED` |
| `enable_storage_autoscaling` | `bool` | `true` | Enable automatic storage scaling |
| `scaling_max_capacity` / `scaling_target_value` | `number` | `250` / `70` | Max storage (GB) and utilization % that trigger scaling |
| `create_scram_secret_association` | `bool` | `false` | Associate SASL/SCRAM secrets (requires `client_authentication.sasl.scram = true`) |
| `scram_secret_association_secret_arn_list` | `list(string)` | `[]` | AWS Secrets Manager ARNs for SCRAM authentication |
| `vpc_connections` | `map(object)` | `{}` | Multi-VPC/cross-account `aws_msk_vpc_connection` definitions |
| `create_cluster_policy` | `bool` | `false` | Create an MSK cluster resource policy |
| `cluster_policy_statements` | `map(object)` | `null` | IAM policy statements for the cluster policy |
| `create_schema_registry` | `bool` | `true` | Toggle to disable Glue schema registry/schema creation entirely |
| `schema_registries` / `schemas` | `map(object)` | `{}` | Glue Schema Registry registries and schemas |
| `topics` | `map(object)` | `{}` | Native Kafka topics (`aws_msk_topic`) — Kafka > 3.6 only, not for serverless |
| `connect_custom_plugins` | `map(object)` | `{}` | MSK Connect custom plugin definitions (S3-hosted JAR/ZIP) |
| `create_connect_worker_configuration` | `bool` | `false` | Create an MSK Connect worker configuration |
| `connect_worker_config_name` / `_description` / `_properties_file_content` | `string` | `null` | Worker configuration name, description, and `connect-distributed.properties` content |
| `rebalancing` | `object` | `null` | Intelligent rebalancing (`status`); Provisioned clusters with Express brokers only |
| `timeouts` | `object` | `null` | Create/update/delete timeout overrides |
| `tags` | `map(string)` | `{}` | Tags to assign to all created resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | ARN of the MSK cluster |
| `cluster_name` / `cluster_uuid` | Cluster name and UUID (used in IAM policy resource ARNs) |
| `current_version` | Current version of the MSK cluster, used for in-place updates |
| `bootstrap_brokers` | Combined bootstrap broker string (plaintext/SASL-IAM/SASL-SCRAM/TLS, whichever apply) |
| `bootstrap_brokers_plaintext` | Plaintext bootstrap brokers (when `encryption_in_transit_client_broker` allows plaintext) |
| `bootstrap_brokers_sasl_iam` / `bootstrap_brokers_sasl_scram` / `bootstrap_brokers_tls` | Auth-specific bootstrap broker endpoints |
| `bootstrap_brokers_public` | Combined public bootstrap brokers (SASL-IAM/SASL-SCRAM/TLS) |
| `bootstrap_brokers_public_sasl_iam` / `_sasl_scram` / `_tls` | Public bootstrap broker endpoints by auth method |
| `bootstrap_brokers_vpc_connectivity` | Combined VPC-connectivity bootstrap brokers (SASL-IAM/SASL-SCRAM/TLS) |
| `bootstrap_brokers_vpc_connectivity_sasl_iam` / `_sasl_scram` / `_tls` | VPC-connectivity bootstrap broker endpoints by auth method |
| `zookeeper_connect_string` / `zookeeper_connect_string_tls` | ZooKeeper connection strings (plaintext/TLS) |
| `configuration_arn` / `configuration_latest_revision` | ARN and revision of the (created or referenced) MSK configuration |
| `scram_secret_association_id` | ID of the SASL/SCRAM secret association |
| `log_group_arn` | ARN of the module-created CloudWatch Log Group |
| `appautoscaling_policy_arn` / `_name` / `_policy_type` | Storage autoscaling policy attributes |
| `vpc_connections` | Map of created `aws_msk_vpc_connection` resource attributes, keyed by input map key |
| `schema_registries` / `schemas` | Maps of created Glue Schema Registry registries and schemas, keyed by input map key |
| `topics` | Map of created `aws_msk_topic` resource attributes, keyed by input map key |
| `connect_custom_plugins` | Map of created MSK Connect custom plugin attributes, keyed by input map key |
| `connect_worker_configuration_arn` / `_latest_revision` | ARN and revision of the MSK Connect worker configuration |

## Usage Examples

### Example 1: Basic MSK Cluster

```hcl
module "msk_kafka_cluster" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.3"

  name                   = "my-kafka-cluster"
  kafka_version          = "3.9.x"
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
# Secret for SCRAM authentication (name must start with "AmazonMSK_")
resource "aws_secretsmanager_secret" "kafka_user" {
  name       = "AmazonMSK_kafka_user"
  kms_key_id = module.kms.key_id
}

resource "aws_secretsmanager_secret_version" "kafka_user" {
  secret_id = aws_secretsmanager_secret.kafka_user.id
  secret_string = jsonencode({
    username = "kafka_user"
    password = random_password.kafka_user.result
  })
}

resource "aws_secretsmanager_secret_policy" "kafka_user" {
  secret_arn = aws_secretsmanager_secret.kafka_user.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "AWSKafkaResourcePolicy"
      Effect    = "Allow"
      Principal = { Service = "kafka.amazonaws.com" }
      Action    = "secretsmanager:getSecretValue"
      Resource  = aws_secretsmanager_secret.kafka_user.arn
    }]
  })
}

resource "random_password" "kafka_user" {
  length  = 32
  special = true
}

module "msk_production" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.3"

  name                   = "prod-kafka"
  kafka_version          = "3.9.x"
  number_of_broker_nodes = 6 # 2 brokers per AZ across 3 AZs

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.xlarge"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 500 }
  }

  enhanced_monitoring = "PER_TOPIC_PER_BROKER"

  client_authentication = {
    sasl = { scram = true }
  }
  create_scram_secret_association          = true
  scram_secret_association_secret_arn_list = [aws_secretsmanager_secret.kafka_user.arn]

  encryption_at_rest_kms_key_arn      = module.kms.key_arn
  encryption_in_transit_client_broker = "TLS"
  encryption_in_transit_in_cluster    = true

  cloudwatch_logs_enabled                = true
  cloudwatch_log_group_retention_in_days = 30
  cloudwatch_log_group_kms_key_id        = module.kms.key_arn
  s3_logs_enabled                        = true
  s3_logs_bucket                         = module.s3_logs.s3_bucket_id
  s3_logs_prefix                         = "kafka-logs/"

  enable_storage_autoscaling = true
  scaling_max_capacity       = 1024
  scaling_target_value       = 80

  tags = {
    Environment = "production"
    Compliance  = "required"
  }
}
```

### Example 3: Cluster with Enhanced Monitoring and Observability

```hcl
module "msk_monitored" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.3"

  name                   = "monitored-kafka"
  kafka_version          = "3.9.x"
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.large"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 200 }
  }

  enhanced_monitoring = "PER_TOPIC_PER_PARTITION"

  # Prometheus exporters for Grafana integration
  jmx_exporter_enabled  = true
  node_exporter_enabled = true

  # Multi-destination logging
  cloudwatch_logs_enabled = true
  cloudwatch_log_group_name = "/aws/msk/monitored-kafka"

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
  version = "~> 3.3"

  name                   = "kafka-with-schemas"
  kafka_version          = "3.9.x"
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.large"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 100 }
  }

  schema_registries = {
    team_a = {
      name        = "team_a"
      description = "Schema registry for Team A"
    }
  }

  schemas = {
    user_events = {
      schema_registry_name = "team_a"
      schema_name = "UserEvents"
      description = "Schema for user event data"
      compatibility = "BACKWARD"
      data_format = "AVRO"
      schema_definition = file("${path.module}/schemas/user_events.avsc")
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

### Example 5: Cluster with IAM Authentication and Public/VPC Connectivity

```hcl
module "msk_iam_auth" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.3"

  name                   = "kafka-iam-auth"
  kafka_version          = "3.9.x"
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.large"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 100 }
  }

  # Controls both public access and VPC connectivity for the broker node group
  broker_node_connectivity_info = {
    public_access = {
      type = "DISABLED"
    }
    vpc_connectivity = {
      client_authentication = {
        sasl = { iam = true }
      }
    }
  }

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

### Example 6: Cluster with Native Topic Management

```hcl
module "msk_with_topics" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.3"

  name                   = "kafka-native-topics"
  kafka_version          = "3.9.x" # topics require Kafka version > 3.6
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.large"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 200 }
  }

  # Native Kafka topic management (aws_msk_topic) - not supported for serverless clusters
  topics = {
    orders = {
      partition_count    = 6
      replication_factor = 3
      configs            = jsonencode({ "retention.ms" = "604800000" })
    }
    events = {
      partition_count    = 3
      replication_factor = 3
    }
  }

  encryption_in_transit_client_broker = "TLS"
  encryption_in_transit_in_cluster    = true

  tags = {
    Environment = "production"
  }
}
```

### Example 7: Kafka Connect — Custom Plugin and Worker Configuration

```hcl
module "msk_connect" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.3"

  name                   = "kafka-connect-cdc"
  kafka_version          = "3.9.x"
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.t3.small"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  # MSK Connect custom plugin (e.g., Debezium CDC connector JAR staged in S3)
  connect_custom_plugins = {
    debezium = {
      name         = "debezium-postgresql"
      description  = "Debezium PostgreSQL connector"
      content_type = "JAR"

      s3_bucket_arn     = module.s3_bucket.s3_bucket_arn
      s3_file_key       = "debezium-connector-postgres/debezium-connector-postgres.jar"
      s3_object_version = aws_s3_object.debezium_connector.version_id

      timeouts = {
        create = "20m"
      }
    }
  }

  # MSK Connect worker configuration
  create_connect_worker_configuration = true
  connect_worker_config_name          = "kafka-connect-cdc"
  connect_worker_config_description   = "Worker configuration for CDC connectors"
  connect_worker_config_properties_file_content = <<-EOT
    key.converter=org.apache.kafka.connect.storage.StringConverter
    value.converter=org.apache.kafka.connect.storage.StringConverter
  EOT

  tags = {
    Environment = "production"
    UseCase     = "cdc"
  }
}
```

### Example 8: Serverless MSK Cluster

```hcl
module "msk_serverless" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws//modules/serverless"
  version = "~> 3.3"

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

### Example 9: Cluster with Tiered Storage

```hcl
module "msk_tiered_storage" {
  source  = "terraform-aws-modules/msk-kafka-cluster/aws"
  version = "~> 3.3"

  name                   = "kafka-tiered"
  kafka_version          = "3.9.x"
  number_of_broker_nodes = 3

  broker_node_client_subnets  = module.vpc.private_subnets
  broker_node_instance_type   = "kafka.m5.2xlarge"
  broker_node_security_groups = [module.kafka_sg.security_group_id]

  broker_node_storage_info = {
    ebs_storage_info = { volume_size = 1000 }
  }

  # Enable tiered storage for cost-effective unlimited retention
  storage_mode = "TIERED"

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
4. **Enable Storage Autoscaling**: Set `scaling_max_capacity` to 2-3x initial capacity with target utilization of 70-80% for headroom
5. **Select Kafka Version Carefully**: Use the latest stable version for new clusters; test upgrades in non-production before applying to production
6. **Consider KRaft Mode**: For new deployments, evaluate KRaft (ZooKeeper-free) Kafka versions for simplified operations
7. **Distribute Across AZs**: Use `broker_node_az_distribution = "DEFAULT"` to evenly distribute brokers across Availability Zones

### Security and Authentication

1. **Enable Encryption at Rest**: Always use KMS encryption for data at rest; use custom KMS keys for audit trail and key rotation control
2. **Enforce TLS for Transit**: Set `encryption_in_transit_client_broker = "TLS"` and `encryption_in_transit_in_cluster = true` for all production clusters
3. **Use IAM Authentication**: Prefer SASL/IAM over SCRAM for better integration with AWS services and credential management
4. **Implement SCRAM Correctly**: Store SCRAM credentials in Secrets Manager with automatic rotation; secret names MUST start with `"AmazonMSK_"` and never be hardcoded
5. **Apply Security Groups**: Restrict ingress to Kafka ports (9092, 9094, 9096, 9098) from only necessary sources; use security group references
6. **Enable mTLS When Required**: Use `client_authentication.tls.certificate_authority_arns` for mutual TLS when client certificate validation is needed
7. **Avoid Unauthenticated Access**: Never set `client_authentication.unauthenticated = true` in production environments
8. **Control Public/VPC Access Explicitly**: Set `broker_node_connectivity_info.public_access.type = "DISABLED"` unless public access is a deliberate requirement
9. **Implement Cluster Policies**: Use `create_cluster_policy` for cross-account access instead of overly permissive security groups
10. **Encrypt Log Group**: Set `cloudwatch_log_group_kms_key_id` when `create_cloudwatch_log_group = true` and logs may contain sensitive data

### Monitoring and Observability

1. **Enable Enhanced Monitoring**: Use `"PER_TOPIC_PER_BROKER"` level for production to get detailed metrics on topic and partition performance
2. **Configure Prometheus Exporters**: Enable both `jmx_exporter_enabled` and `node_exporter_enabled` for integration with Prometheus and Grafana
3. **Stream Logs to CloudWatch**: Enable `cloudwatch_logs_enabled` with appropriate `cloudwatch_log_group_retention_in_days` for troubleshooting and audit compliance
4. **Set Up Log Archival**: Use `s3_logs_enabled` for long-term log retention and cost-effective storage with lifecycle policies
5. **Monitor Key Metrics**: Track under-replicated partitions, offline partitions, consumer lag, broker CPU, memory, and disk utilization
6. **Create CloudWatch Alarms**: Set alarms for critical metrics like broker down, offline partitions, high consumer lag, and storage usage
7. **Use Kafka Lag Exporter**: Deploy external lag monitoring tools for consumer group lag visibility and alerting

### Cost Optimization

1. **Right-Size Broker Instances**: Start with smaller instance types and scale up based on actual metrics; avoid over-provisioning
2. **Use Serverless for Variable Workloads**: Consider the `serverless` submodule for development, testing, or applications with unpredictable traffic patterns
3. **Implement Data Retention Policies**: Set appropriate retention periods via `topics.configs` or `configuration_server_properties`; don't retain data longer than necessary
4. **Enable Tiered Storage**: Use `storage_mode = "TIERED"` for cost-effective long-term retention without deleting data
5. **Optimize Storage Autoscaling**: Set conservative `scaling_target_value` (70-80%) to avoid over-provisioning while maintaining headroom
6. **Monitor Data Transfer Costs**: Keep producers and consumers in the same region as the MSK cluster to minimize cross-AZ/cross-region charges

### High Availability and Disaster Recovery

1. **Deploy Multi-AZ**: Always distribute brokers across at least 3 Availability Zones for fault tolerance
2. **Set Replication Factor**: Use `replication_factor = 3` for critical topics (via `topics` or client-side topic creation) to ensure data durability
3. **Configure min.insync.replicas**: Set to 2 for production topics to balance durability and availability
4. **Plan for Broker Failures**: MSK automatically recovers failed brokers; ensure client retry logic handles temporary unavailability
5. **Monitor Partition Health**: Track under-replicated and offline partitions; investigate and resolve quickly
6. **Test Failover Scenarios**: Regularly test application behavior during broker failures and AZ outages

### Operational Excellence

1. **Use Infrastructure as Code**: Manage all MSK resources (cluster, topics, schemas, connectors, policies) through this module for reproducibility
2. **Implement Tagging Strategy**: Apply consistent tags for cost allocation, environment identification, and resource management
3. **Reuse Configurations Deliberately**: Set `create_configuration = false` with `configuration_arn`/`configuration_revision` to share a configuration across clusters
4. **Version Control Schemas**: Store schema definitions in version control and use `schemas`/`schema_registries` for validation; set `create_schema_registry = false` if not needed
5. **Plan Kafka Connect Deployments**: Stage plugin artifacts in S3 before referencing them in `connect_custom_plugins`; use `timeouts.create` for large plugin uploads
6. **Implement Change Management**: Run `terraform plan` before applying changes; test in non-production first

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-msk-kafka-cluster
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/msk-kafka-cluster/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-msk-kafka-cluster/tree/master/examples
- **Module CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-msk-kafka-cluster/blob/master/CHANGELOG.md
- **AWS MSK Documentation**: https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html
- **MSK Encryption**: https://docs.aws.amazon.com/msk/latest/developerguide/msk-encryption.html
- **MSK Monitoring**: https://docs.aws.amazon.com/msk/latest/developerguide/monitoring.html
- **MSK Connect**: https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect.html
- **MSK Serverless**: https://docs.aws.amazon.com/msk/latest/developerguide/serverless.html
- **AWS MSK Best Practices**: https://docs.aws.amazon.com/msk/latest/developerguide/best-practices.html
- **AWS MSK Pricing**: https://aws.amazon.com/msk/pricing/
- **MSK IAM Access Control**: https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html
- **Apache Kafka Documentation**: https://kafka.apache.org/documentation/

## Notes for AI Agents

When using this module in automated workflows:

### Critical Configuration Rules
1. **Broker Node Count**: `number_of_broker_nodes` MUST be a multiple of `broker_node_client_subnets` count (e.g., 3 subnets → 3, 6, 9 brokers)
2. **Subnet Requirements**: MSK requires subnets in at least 2 AZs; use 3 AZs for production high availability
3. **Authentication Object**: Use `client_authentication = { sasl = { iam = true } }` / `{ scram = true }` — the older separate boolean flags (`client_authentication_sasl_iam`, etc.) do not exist in v3.x
4. **Connectivity Object**: Public access and VPC connectivity are configured together via `broker_node_connectivity_info` (`public_access.type`, `vpc_connectivity.client_authentication`, `network_type`), not separate top-level variables
5. **SCRAM Secret Naming**: Secrets Manager secret names MUST start with `"AmazonMSK_"` for SCRAM authentication

### Common Patterns
6. **Storage Sizing**: Use 100+ GiB for development, 500+ GiB for production; enable `enable_storage_autoscaling = true` with `scaling_max_capacity`
7. **Security Group Ports**: Allow 9092 (plaintext), 9094 (TLS), 9096 (SASL/IAM), 9098 (SASL/SCRAM) based on auth method
8. **Bootstrap Brokers**: Select the output matching the authentication/connectivity path, e.g. `bootstrap_brokers_sasl_iam`, `bootstrap_brokers_public`, `bootstrap_brokers_vpc_connectivity`
9. **Schema Registry**: Use the `schema_registries`/`schemas` maps; set `create_schema_registry = false` to skip Glue resources entirely. Outputs `schema_registries`/`schemas` are full resource maps, not scalar ARN/ID/name
10. **Native Topics**: `topics` variable requires Kafka version > 3.6 and is only supported for provisioned clusters (not serverless)
11. **Kafka Connect**: Custom plugins and worker configuration are root-module variables (`connect_custom_plugins`, `create_connect_worker_configuration`), not a separate submodule

### Limitations and Gotchas
12. **Encryption Changes**: Changing encryption settings requires cluster recreation; plan data migration
13. **Serverless Limitations**: MSK Serverless doesn't support custom configurations, tiered storage, native topic management, or public access
14. **Configuration Updates**: Some `configuration_server_properties` changes require a cluster restart
15. **Autoscaling Behavior**: Storage autoscaling is gradual; don't rely on it for sudden traffic spikes
16. **CloudWatch Log Group Output**: The output is `log_group_arn` (not `cloudwatch_log_group_arn`); there is no `cloudwatch_log_group_name` output — reference `var.cloudwatch_log_group_name` or the ARN instead

### Version-Specific Notes
17. **v3.0.0 Breaking Change**: Requires AWS provider `>= 6.40` and Terraform `>= 1.5.7`; v2.x users must upgrade the provider before adopting v3.x
18. **v3.2.0**: Added `broker_node_connectivity_info.network_type` support
19. **v3.3.0 (latest)**: Added native MSK topic management via the `topics` variable / `aws_msk_topic`
20. **Kafka Version**: Use a recent stable release (e.g., `3.9.x`) for new clusters; verify client library compatibility and topic-management version requirements (> 3.6)

### Cost Considerations
21. **Pricing Model**: MSK charges by broker-hour + storage GB-month + data transfer; estimate before deployment
