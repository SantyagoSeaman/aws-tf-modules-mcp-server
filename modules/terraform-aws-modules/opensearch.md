# AWS OpenSearch Terraform Module

## Module Information

- **Source**: `terraform-aws-modules/opensearch/aws`
- **Version**: 2.5.0
- **Terraform**: >= 1.5.7
- **AWS Provider**: >= 6.28
- **License**: Apache-2.0
- **Keywords**: opensearch, elasticsearch, search, log-analytics, observability, cluster, domain, serverless, vpc, encryption, saml, cognito, dashboards

## Description

Terraform module that creates AWS OpenSearch Service domains and collections for search, log analytics, and real-time application monitoring. OpenSearch is a distributed, community-driven search and analytics suite derived from Apache 2.0 licensed Elasticsearch. This module supports both OpenSearch and legacy Elasticsearch versions, enabling comprehensive configuration of domains with advanced security, networking, encryption, monitoring, and auto-tuning capabilities. It also provides serverless collection support through a dedicated submodule.

## Key Features

- **OpenSearch Domain Creation**: Create and manage OpenSearch Service domains with custom configurations
- **Serverless Collections**: Dedicated submodule for auto-scaled OpenSearch Serverless (SEARCH, TIMESERIES, VECTORSEARCH types)
- **Cluster Configuration**: Flexible cluster setup with instance types, counts, dedicated masters, and coordinating nodes
- **Multi-AZ Deployment**: Zone-aware replication across 2-3 Availability Zones for high availability
- **Advanced Security Options**: Fine-grained access control enabled by default, SAML and IAM Identity Center authentication
- **VPC Integration**: Deploy domains within VPCs with custom security groups and VPC endpoints
- **Encryption by Default**: Encryption at rest, node-to-node encryption, and TLS 1.2+ all enabled by default
- **EBS Storage Configuration**: gp3 volumes by default with configurable IOPS and throughput
- **Auto-Tuning**: Automatic performance tuning enabled by default with off-peak maintenance windows
- **CloudWatch Logging**: Log publishing for INDEX_SLOW_LOGS and SEARCH_SLOW_LOGS by default
- **Software Update Management**: Automated software updates enabled by default
- **AI/ML Options**: Natural language query generation capabilities
- **Dual-Stack Endpoints**: IPv4 and IPv4/IPv6 endpoint support
- **Cross-Cluster Connections**: Outbound connections to external OpenSearch domains

## Use Cases

- **Log Analytics**: Centralized log aggregation and analysis from applications, infrastructure, and security tools
- **Application Monitoring**: Real-time monitoring of application performance metrics and traces
- **Security Analytics**: SIEM (Security Information and Event Management) for threat detection and investigation
- **Full-Text Search**: Enterprise search capabilities for documents, products, and content
- **Clickstream Analysis**: Real-time analysis of user behavior and clickstream data
- **Business Intelligence**: Interactive dashboards and visualizations for business metrics
- **IoT Analytics**: Time-series data analysis from IoT devices and sensors
- **E-commerce Search**: Product catalog search with faceted filtering and recommendations
- **Document Management**: Searchable document repositories with metadata indexing
- **Observability Platform**: Unified platform for logs, metrics, and traces from distributed systems

## Submodules

### collection

Creates AWS OpenSearch Serverless collections for on-demand, auto-scaling search and analytics workloads.

**Source**: `terraform-aws-modules/opensearch/aws//modules/collection`

**Purpose**: Provision serverless OpenSearch collections without managing infrastructure, with automatic scaling and pay-per-use pricing.

**Collection Types**:
- `SEARCH`: General-purpose search workloads
- `TIMESERIES`: Time-series data and log analytics
- `VECTORSEARCH`: Vector embeddings and similarity search (ML/AI applications)

**Key Variables**:
| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | string | `""` | Collection identifier (required) |
| `type` | string | `null` | Collection type: SEARCH, TIMESERIES, or VECTORSEARCH |
| `description` | string | `null` | Collection description |
| `standby_replicas` | string | `null` | ENABLED or DISABLED for backup replicas |
| `create_access_policy` | bool | `true` | Create access control policy |
| `access_policy_principals` | list(string) | `[]` | IAM principals with access |
| `access_policy_index_permissions` | list(string) | `["aoss:*"]` | Index-level permissions |
| `access_policy_collection_permissions` | list(string) | `["aoss:*"]` | Collection-level permissions |
| `create_encryption_policy` | bool | `true` | Create encryption policy |
| `create_network_policy` | bool | `false` | Create network access policy |
| `network_policy` | any | `null` | VPC endpoint and public access settings |
| `tags` | map(string) | `{}` | Resource tags |

**Outputs**:
- `arn`: Amazon Resource Name of the collection
- `id`: Unique identifier for the collection
- `endpoint`: API endpoint for index/search requests
- `dashboard_endpoint`: OpenSearch Dashboards endpoint
- `kms_key_arn`: ARN of the KMS key used for encryption
- `name`: Collection name

**Usage Example**:
```hcl
module "opensearch_serverless" {
  source  = "terraform-aws-modules/opensearch/aws//modules/collection"
  version = "~> 2.5"

  name        = "my-collection"
  type        = "SEARCH"
  description = "Product catalog search"

  # Access policy (created by default)
  access_policy_principals = [
    "arn:aws:iam::123456789012:role/SearchAppRole"
  ]

  # Network policy for VPC-only access
  create_network_policy = true
  network_policy = {
    AllowFromPublic = false
    SourceVPCEs     = ["vpce-xxxxx"]
  }

  # Enable standby replicas for HA
  standby_replicas = "ENABLED"

  tags = {
    Environment = "production"
  }
}
```

## Variables

### Required
- `domain_name` (string): Name of the OpenSearch domain (required for domain creation)

### Domain Configuration
- `create` (bool): Whether to create OpenSearch domain resources (default: `true`)
- `engine_version` (string): OpenSearch or Elasticsearch engine version (e.g., `"OpenSearch_2.13"`)
- `ip_address_type` (string): Endpoint addressing - `"ipv4"` or `"dualstack"` (default: `null`)

### Cluster Settings
- `cluster_config` (any): Cluster configuration (default: `{dedicated_master_enabled: true}`)
  - `instance_type`: Instance type for data nodes
  - `instance_count`: Number of instances in the cluster
  - `dedicated_master_enabled`: Whether to enable dedicated master nodes (default: true)
  - `dedicated_master_type`: Instance type for dedicated master nodes
  - `dedicated_master_count`: Number of dedicated master nodes
  - `zone_awareness_enabled`: Enable multi-AZ deployment
  - `zone_awareness_config.availability_zone_count`: Number of Availability Zones (2 or 3)

### Storage
- `ebs_options` (any): EBS volume configuration (default: `{ebs_enabled: true, volume_size: 64, volume_type: "gp3"}`)
  - `ebs_enabled`: Whether to enable EBS volumes
  - `volume_type`: EBS volume type (gp3, gp2, io1)
  - `volume_size`: Size of EBS volumes in GiB
  - `iops`: Provisioned IOPS for gp3/io1 volumes
  - `throughput`: Throughput for gp3 volumes in MiB/s

### Security (Secure Defaults)
- `advanced_security_options` (any): Fine-grained access control (default: `{enabled: true, anonymous_auth_enabled: false}`)
  - `enabled`: Enable advanced security options (default: true)
  - `anonymous_auth_enabled`: Enable anonymous authentication (default: false)
  - `internal_user_database_enabled`: Use internal user database
  - `master_user_options`: Master user credentials or ARN
- `encrypt_at_rest` (any): Encryption at rest (default: `{enabled: true}`)
- `node_to_node_encryption` (any): Node-to-node encryption (default: `{enabled: true}`)
- `domain_endpoint_options` (any): HTTPS enforcement (default: `{enforce_https: true, tls_security_policy: "Policy-Min-TLS-1-2-2019-07"}`)
- `create_saml_options` (bool): Enable SAML authentication (default: `false`)
- `saml_options` (any): SAML provider configuration
- `identity_center_options` (object): IAM Identity Center integration (default: `null`)

### Networking
- `vpc_options` (any): VPC configuration for domain deployment (default: `{}`)
  - `subnet_ids`: List of subnet IDs for multi-AZ deployment
- `create_security_group` (bool): Whether to create a security group (default: `true`)
- `security_group_rules` (any): Custom security group rules (default: `{}` - **no ingress rules by default**)

### Access Control
- `create_access_policy` (bool): Generate IAM access policy (default: `true`)
- `access_policy_statements` (any): Custom IAM policy statements (default: `{}`)

### Monitoring and Logging
- `log_publishing_options` (any): CloudWatch logging (default: `[{log_type: "INDEX_SLOW_LOGS"}, {log_type: "SEARCH_SLOW_LOGS"}]`)
- `cloudwatch_log_group_retention_in_days` (number): Log retention period (default: `60`)
- `cloudwatch_log_group_kms_key_id` (string): KMS key for log encryption
- `auto_tune_options` (any): Auto-tuning configuration (default: `{desired_state: "ENABLED", rollback_on_disable: "NO_ROLLBACK"}`)

### Advanced Options
- `cognito_options` (any): Amazon Cognito authentication for Dashboards
- `software_update_options` (any): Automated updates (default: `{auto_software_update_enabled: true}`)
- `off_peak_window_options` (any): Maintenance window (default: `{enabled: true, off_peak_window: {hours: 7}}`)
- `aiml_options` (object): AI/ML natural language query settings (default: `null`)
- `package_associations` (map(string)): OpenSearch package mappings (default: `{}`)
- `vpc_endpoints` (any): VPC endpoint configurations (default: `{}`)
- `outbound_connections` (any): Cross-cluster outbound connections (default: `{}`)

### Resource Management
- `tags` (map(string)): Tags to apply to all resources (default: `{}`)
- `timeouts` (map(string)): Resource operation timeouts

## Outputs

### Domain Information
- `domain_arn`: ARN of the OpenSearch domain
- `domain_id`: Unique identifier for the domain
- `domain_name`: Name of the OpenSearch domain

### Endpoints
- `domain_endpoint`: Primary API endpoint for index/search/upload requests
- `domain_endpoint_v2`: Dual-stack (IPv4/IPv6) API endpoint
- `domain_dashboard_endpoint`: OpenSearch Dashboards endpoint (without https scheme)
- `domain_dashboard_endpoint_v2`: Dual-stack Dashboards endpoint
- `domain_endpoint_v2_hosted_zone_id`: Hosted zone ID for dual-stack endpoint

### Infrastructure
- `security_group_arn`: ARN of the security group (if created)
- `security_group_id`: ID of the security group (if created)
- `cloudwatch_logs`: Map of CloudWatch log groups and their properties
- `vpc_endpoints`: Map of VPC endpoints and their attributes
- `package_associations`: Map of package associations
- `outbound_connections`: Map of outbound connections to external domains

## Usage Examples

### Basic OpenSearch Domain

```hcl
module "opensearch_basic" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.5"

  domain_name    = "my-opensearch-domain"
  engine_version = "OpenSearch_2.13"

  cluster_config = {
    instance_type  = "t3.small.search"
    instance_count = 1
  }

  ebs_options = {
    ebs_enabled = true
    volume_size = 10
    volume_type = "gp3"
  }

  tags = {
    Environment = "development"
  }
}
```

### Production OpenSearch Domain with Multi-AZ

```hcl
module "opensearch_production" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.5"

  domain_name    = "prod-search-domain"
  engine_version = "OpenSearch_2.13"

  cluster_config = {
    instance_type              = "r6g.large.search"
    instance_count             = 3
    dedicated_master_enabled   = true
    dedicated_master_type      = "c6g.large.search"
    dedicated_master_count     = 3
    zone_awareness_enabled     = true
    availability_zone_count    = 3
  }

  ebs_options = {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 100
    iops        = 3000
    throughput  = 125
  }

  advanced_security_options = {
    enabled                        = true
    anonymous_auth_enabled         = false
    internal_user_database_enabled = true
    master_user_options = {
      master_user_name     = "admin"
      master_user_password = random_password.master_password.result
    }
  }

  encrypt_at_rest = {
    enabled    = true
    kms_key_id = aws_kms_key.opensearch.id
  }

  node_to_node_encryption = {
    enabled = true
  }

  domain_endpoint_options = {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  tags = {
    Environment = "production"
    Application = "log-analytics"
  }
}

resource "random_password" "master_password" {
  length  = 16
  special = true
}
```

### OpenSearch in VPC with CloudWatch Logging

```hcl
module "opensearch_vpc" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.5"

  domain_name    = "vpc-search-domain"
  engine_version = "OpenSearch_2.11"

  cluster_config = {
    instance_type           = "r6g.xlarge.search"
    instance_count          = 2
    zone_awareness_enabled  = true
    availability_zone_count = 2
  }

  ebs_options = {
    ebs_enabled = true
    volume_size = 50
    volume_type = "gp3"
  }

  vpc_options = {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [aws_security_group.opensearch.id]
  }

  advanced_security_options = {
    enabled = true
    master_user_options = {
      master_user_arn = aws_iam_role.opensearch_master.arn
    }
  }

  log_publishing_options = {
    INDEX_SLOW_LOGS = {
      enabled                  = true
      cloudwatch_log_group_arn = aws_cloudwatch_log_group.index_slow_logs.arn
    }
    SEARCH_SLOW_LOGS = {
      enabled                  = true
      cloudwatch_log_group_arn = aws_cloudwatch_log_group.search_slow_logs.arn
    }
    ES_APPLICATION_LOGS = {
      enabled                  = true
      cloudwatch_log_group_arn = aws_cloudwatch_log_group.application_logs.arn
    }
  }

  tags = {
    Environment = "production"
    VPC         = "enabled"
  }
}
```

### OpenSearch with Auto-Tune and Software Updates

```hcl
module "opensearch_autotuned" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.5"

  domain_name    = "autotuned-domain"
  engine_version = "OpenSearch_2.13"

  cluster_config = {
    instance_type  = "r6g.large.search"
    instance_count = 3
  }

  ebs_options = {
    ebs_enabled = true
    volume_size = 75
    volume_type = "gp3"
  }

  auto_tune_options = {
    enabled                       = true
    rollback_on_disable           = "DEFAULT_ROLLBACK"
    use_off_peak_window           = true
  }

  off_peak_window_options = {
    enabled = true
    off_peak_window = {
      hours = 3
    }
  }

  software_update_options = {
    auto_software_update_enabled = true
  }

  tags = {
    AutoTune = "enabled"
  }
}
```

### OpenSearch with SAML Authentication

```hcl
module "opensearch_saml" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.5"

  domain_name    = "saml-auth-domain"
  engine_version = "OpenSearch_2.11"

  cluster_config = {
    instance_type  = "r6g.large.search"
    instance_count = 2
  }

  ebs_options = {
    ebs_enabled = true
    volume_size = 50
    volume_type = "gp3"
  }

  advanced_security_options = {
    enabled                        = true
    anonymous_auth_enabled         = false
    internal_user_database_enabled = false

    master_user_options = {
      master_user_arn = aws_iam_role.opensearch_master.arn
    }

    saml_options = {
      enabled = true
      idp = {
        entity_id        = "https://idp.example.com/metadata"
        metadata_content = file("${path.module}/saml-metadata.xml")
      }
      master_backend_role = "admins"
      roles_key           = "roles"
      subject_key         = "email"
      session_timeout_minutes = 60
    }
  }

  domain_endpoint_options = {
    enforce_https = true
  }

  tags = {
    Authentication = "SAML"
  }
}
```

### OpenSearch with Cognito Authentication

```hcl
module "opensearch_cognito" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.5"

  domain_name    = "cognito-auth-domain"
  engine_version = "OpenSearch_2.11"

  cluster_config = {
    instance_type  = "r6g.large.search"
    instance_count = 2
  }

  ebs_options = {
    ebs_enabled = true
    volume_size = 50
    volume_type = "gp3"
  }

  cognito_options = {
    enabled          = true
    user_pool_id     = aws_cognito_user_pool.opensearch.id
    identity_pool_id = aws_cognito_identity_pool.opensearch.id
    role_arn         = aws_iam_role.cognito_opensearch.arn
  }

  advanced_security_options = {
    enabled = true
    master_user_options = {
      master_user_arn = aws_iam_role.opensearch_master.arn
    }
  }

  tags = {
    Authentication = "Cognito"
  }
}
```

### OpenSearch Serverless Collection

```hcl
module "opensearch_serverless_timeseries" {
  source  = "terraform-aws-modules/opensearch/aws//modules/collection"
  version = "~> 2.5"

  name        = "metrics-timeseries"
  type        = "TIMESERIES"
  description = "Time-series collection for application metrics"

  create_access_policy = true
  access_policy = {
    rules = [
      {
        resource_type = "collection"
        permissions = [
          "aoss:CreateCollectionItems",
          "aoss:UpdateCollectionItems",
          "aoss:DescribeCollectionItems"
        ]
        principals = [
          aws_iam_role.metrics_writer.arn,
          aws_iam_role.metrics_reader.arn
        ]
      },
      {
        resource_type = "index"
        resource      = ["index/metrics-timeseries/*"]
        permissions   = ["aoss:*"]
        principals    = [aws_iam_role.metrics_admin.arn]
      }
    ]
  }

  create_network_policy = true
  network_policy = {
    AllowFromPublic = false
    SourceVPCEs     = [aws_opensearchserverless_vpc_endpoint.metrics.id]
  }

  create_encryption_policy = true
  encryption_policy = {
    kms_key_arn = aws_kms_key.opensearch_serverless.arn
  }

  standby_replicas = "ENABLED"

  tags = {
    Environment = "production"
    Type        = "timeseries"
  }
}
```

### OpenSearch with Custom Access Policies

```hcl
module "opensearch_custom_access" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.5"

  domain_name    = "custom-access-domain"
  engine_version = "OpenSearch_2.13"

  cluster_config = {
    instance_type  = "r6g.large.search"
    instance_count = 2
  }

  ebs_options = {
    ebs_enabled = true
    volume_size = 50
    volume_type = "gp3"
  }

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = [
            aws_iam_role.app_role.arn,
            aws_iam_role.admin_role.arn
          ]
        }
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPost",
          "es:ESHttpPut"
        ]
        Resource = "arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/custom-access-domain/*"
      },
      {
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.admin_role.arn
        }
        Action = "es:*"
        Resource = "arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/custom-access-domain/*"
      }
    ]
  })

  advanced_security_options = {
    enabled = true
    master_user_options = {
      master_user_arn = aws_iam_role.admin_role.arn
    }
  }

  tags = {
    AccessControl = "custom-policy"
  }
}
```

## Best Practices

### Security

- **Enable Fine-Grained Access Control**: Always enable advanced security options with fine-grained access control for production domains to implement authentication and authorization at the index and document level.
- **Deploy Within VPC**: Place OpenSearch domains inside VPCs with private subnets to prevent direct internet access and control network traffic through security groups.
- **Use Dedicated Master Nodes**: Enable dedicated master nodes (preferably 3) in production to improve cluster stability and prevent data node disruptions from affecting cluster management.
- **Enable Encryption at Rest**: Use AWS KMS encryption for data at rest on all production domains to meet compliance requirements and protect sensitive data.
- **Enable Node-to-Node Encryption**: Configure TLS encryption for inter-node communication to secure data in transit within the cluster.
- **Enforce HTTPS**: Set `enforce_https = true` and use TLS 1.2 or higher (`Policy-Min-TLS-1-2-2019-07`) for all client connections.
- **Implement Least Privilege Access**: Use IAM policies and fine-grained access control to grant minimum necessary permissions to users and applications.
- **Avoid Master User Passwords**: Prefer IAM role-based authentication over password-based master users for better security and credential management.
- **Enable Audit Logging**: Configure audit logs to track authentication, authorization, and data access events for security monitoring and compliance.
- **Rotate Credentials Regularly**: If using password-based authentication, implement regular password rotation policies and use AWS Secrets Manager.
- **Use VPC Endpoints**: Create VPC endpoints for OpenSearch to enable private connectivity from other AWS services without internet gateway.
- **Restrict Security Group Rules**: Configure security groups with specific IP ranges and ports (443 for HTTPS) rather than allowing broad access.
- **Enable AWS Security Hub**: Integrate with Security Hub to continuously monitor domain security posture and receive automated security alerts.
- **Implement Network Segmentation**: Use separate subnets for OpenSearch domains and application tiers to isolate network traffic.
- **Monitor IAM Activity**: Track IAM policy changes and access attempts to OpenSearch domains using AWS CloudTrail.

### High Availability and Disaster Recovery

- **Deploy Across Multiple AZs**: Enable zone awareness and deploy across at least 2-3 Availability Zones to ensure high availability during AZ failures.
- **Use Dedicated Master Nodes**: Deploy 3 dedicated master nodes across different AZs to maintain quorum and cluster stability during failures.
- **Implement Automated Snapshots**: Configure automated snapshots to S3 for point-in-time recovery, with appropriate retention policies.
- **Test Snapshot Restoration**: Regularly test snapshot restoration procedures to validate backup integrity and recovery time objectives (RTOs).
- **Use Cross-Region Replication**: For critical workloads, implement cross-region replication using outbound connections to maintain geo-redundant copies.
- **Monitor Cluster Health**: Set up CloudWatch alarms for cluster status, node health, and shard allocation to detect issues early.
- **Plan for Capacity**: Maintain at least 25% free storage capacity to allow for shard rebalancing and temporary data growth.
- **Document Recovery Procedures**: Maintain detailed runbooks for disaster recovery scenarios including domain restoration and data migration.
- **Implement Blue-Green Deployments**: Use blue-green deployment strategy for major version upgrades to minimize downtime and enable quick rollback.
- **Configure Maintenance Windows**: Use off-peak window options to schedule maintenance during low-traffic periods.
- **Test Failover Scenarios**: Regularly conduct disaster recovery drills to validate failover procedures and identify gaps.
- **Use Standby Replicas**: For OpenSearch Serverless collections, enable standby replicas for automatic failover capabilities.

### Performance Optimization

- **Right-Size Instance Types**: Choose instance types based on workload characteristics - compute-optimized for query-heavy, memory-optimized for data-heavy workloads.
- **Enable Auto-Tune**: Use Auto-Tune to automatically analyze performance and apply optimal JVM heap size and memory settings.
- **Optimize Shard Strategy**: Maintain 25 shards or fewer per GiB of Java heap memory to prevent resource exhaustion.
- **Use gp3 EBS Volumes**: Leverage gp3 volumes for better price-performance with configurable IOPS and throughput independent of volume size.
- **Tune Refresh Intervals**: Set index refresh intervals to 30+ seconds for write-heavy workloads to reduce indexing overhead.
- **Implement Index Lifecycle Management**: Use Index State Management (ISM) policies to automate transitions between hot, warm, and cold storage tiers.
- **Optimize Bulk Requests**: Keep bulk request sizes between 3-5 MiB for optimal throughput without overwhelming the cluster.
- **Enable Compression**: Use gzip compression for API requests to reduce network bandwidth and improve transfer speeds.
- **Monitor JVM Memory Pressure**: Set CloudWatch alarms for JVM memory pressure above 80% to prevent OutOfMemory errors.
- **Use UltraWarm Storage**: Migrate older, less-frequently accessed data to UltraWarm storage for cost-effective log retention.
- **Optimize Query Patterns**: Use filters instead of queries where possible, leverage caching, and avoid wildcard queries at the beginning of terms.
- **Configure Circuit Breakers**: Adjust circuit breaker settings to prevent queries from consuming excessive memory and destabilizing the cluster.
- **Implement Index Templates**: Create index templates with optimal mapping and settings to ensure consistent performance across indices.
- **Monitor Slow Logs**: Enable and regularly review index and search slow logs to identify and optimize problematic queries.
- **Use Dedicated Coordinator Nodes**: For large clusters with heavy query loads, consider dedicated coordinator nodes to offload search coordination.

### Cost Optimization

- **Use Latest Generation Instances**: Choose current generation instance families (r6g, c6g) for better price-performance compared to previous generations.
- **Right-Size Storage**: Regularly review storage utilization and adjust EBS volume sizes to avoid over-provisioning.
- **Leverage Storage Tiers**: Use UltraWarm and cold storage for log data that doesn't require hot storage performance.
- **Delete Unused Indices**: Implement automated index deletion policies to remove old indices that are no longer needed.
- **Consider Reserved Instances**: Purchase Reserved Instances for production workloads with predictable usage to reduce costs by up to 50%.
- **Use Graviton Instances**: Choose ARM-based Graviton2 instances (r6g, c6g) for 20-30% better price-performance than x86 instances.
- **Optimize Replica Count**: Balance availability needs with cost by using appropriate replica counts (1 replica for most production workloads).
- **Monitor Data Transfer Costs**: Minimize cross-AZ and cross-region data transfer by co-locating applications with OpenSearch domains.
- **Implement Data Retention Policies**: Define clear data retention policies and automate deletion to prevent unbounded storage growth.
- **Use Compression**: Enable index compression to reduce storage requirements for older, less-frequently accessed data.
- **Evaluate Serverless for Variable Workloads**: Consider OpenSearch Serverless for unpredictable workloads to pay only for actual usage.
- **Review CloudWatch Logs**: Evaluate the necessity of all enabled CloudWatch log types to reduce logging costs.
- **Optimize Shard Count**: Avoid over-sharding which increases overhead and memory consumption without performance benefits.
- **Use Lifecycle Policies**: Automate data transitions and deletions using ISM policies to optimize storage costs over time.

### Monitoring and Observability

- **Enable All Log Types**: Configure CloudWatch log publishing for index slow logs, search slow logs, application logs, and audit logs.
- **Set Up Critical Alarms**: Create CloudWatch alarms for cluster status (red/yellow), free storage space, JVM memory pressure, and CPU utilization.
- **Monitor Indexing Rate**: Track write throughput and indexing latency to detect performance degradation or bottlenecks.
- **Monitor Search Latency**: Set up alerts for increased search latency to identify query performance issues or resource constraints.
- **Track Shard Allocation**: Monitor unassigned shards and shard relocation activity to detect cluster instability.
- **Review Slow Logs Daily**: Regularly analyze slow logs to identify inefficient queries and indexing operations.
- **Monitor JVM Garbage Collection**: Track GC duration and frequency to detect memory pressure issues before they impact performance.
- **Set Storage Thresholds**: Alert when free storage drops below 25% to allow time for capacity expansion.
- **Monitor Node Count**: Track master and data node availability to ensure cluster quorum and data redundancy.
- **Use OpenSearch Dashboards**: Create operational dashboards in OpenSearch Dashboards (Kibana) for real-time cluster monitoring.
- **Enable Service Health Dashboard**: Monitor AWS service health events that may affect OpenSearch availability.
- **Track API Errors**: Monitor HTTP 4xx and 5xx error rates to detect authentication, authorization, or application issues.
- **Monitor Snapshot Status**: Set up alerts for failed automated snapshots to ensure backup coverage.
- **Implement Custom Metrics**: Export custom application metrics to CloudWatch for correlated analysis with OpenSearch metrics.
- **Use AWS X-Ray**: Integrate X-Ray for distributed tracing of queries across your application stack.

### Operational Excellence

- **Keep Current with Versions**: Regularly upgrade to the latest OpenSearch version to benefit from performance improvements, security patches, and new features.
- **Test in Non-Production First**: Always test configuration changes, version upgrades, and new features in development/staging environments before production.
- **Use Infrastructure as Code**: Manage all OpenSearch infrastructure using Terraform to ensure consistency, version control, and repeatability.
- **Implement GitOps**: Store Terraform configurations in Git with proper branching strategy and pull request reviews.
- **Create Index Templates**: Define index templates for consistent mapping, settings, and lifecycle policies across related indices.
- **Document Domain Configuration**: Maintain detailed documentation of domain settings, access patterns, and operational procedures.
- **Implement Change Management**: Use formal change management process for production domain modifications with rollback plans.
- **Automate Operational Tasks**: Script routine operations like snapshot management, index rotation, and performance tuning.
- **Use Tagging Strategy**: Apply comprehensive tags for cost allocation, environment identification, and resource management.
- **Monitor Domain Upgrade Status**: Track the progress of software updates and be prepared to troubleshoot upgrade issues.
- **Implement Runbooks**: Create operational runbooks for common scenarios like cluster recovery, scaling, and troubleshooting.
- **Conduct Regular Reviews**: Periodically review domain configuration, costs, and performance to identify optimization opportunities.
- **Plan for Scaling**: Understand your data growth patterns and plan vertical (instance size) or horizontal (node count) scaling in advance.
- **Use Configuration Management**: Store OpenSearch cluster settings and mappings in version control for disaster recovery.
- **Implement Alerting Workflows**: Configure automated responses to common alerts where appropriate (e.g., auto-scaling policies).

### Data Management

- **Define Index Lifecycle**: Implement ISM policies to automate index rollover, deletion, and migration between storage tiers.
- **Use Index Rollover**: Configure automatic index rollover based on size, document count, or age to maintain optimal shard sizes.
- **Optimize Mapping**: Define explicit mappings to control how data is indexed rather than relying on dynamic mapping.
- **Use Doc Values**: Enable doc values for fields used in aggregations and sorting to reduce heap memory usage.
- **Implement Time-Based Indices**: For time-series data, create daily or weekly indices for easier management and lifecycle control.
- **Control Field Explosion**: Limit the number of fields per index to prevent mapping explosion and memory issues.
- **Use Nested and Parent-Child Carefully**: Be cautious with nested objects and parent-child relationships as they increase memory usage.
- **Implement Index Aliases**: Use aliases to abstract index names from applications, enabling zero-downtime reindexing and migrations.
- **Compress Source Fields**: Enable source compression for indices with large documents to reduce storage requirements.
- **Review Field Data Usage**: Monitor and limit field data cache usage for text fields to prevent memory exhaustion.
- **Use Frozen Indices**: For long-term data retention, consider frozen indices (if available) for rarely accessed data.
- **Implement Reindexing Strategy**: Plan for periodic reindexing to update mappings, optimize storage, and remove deleted documents.
- **Monitor Index Size**: Track individual index sizes and shard distribution to maintain balanced cluster performance.
- **Use Curator or ISM**: Automate index management tasks using OpenSearch ISM or elasticsearch-curator for consistent operations.
- **Validate Data Quality**: Implement data validation before indexing to prevent incorrect mappings and data inconsistencies.

## Additional Resources

### Official Documentation
- [AWS OpenSearch Service Documentation](https://docs.aws.amazon.com/opensearch-service/)
- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [Terraform AWS OpenSearch Module GitHub](https://github.com/terraform-aws-modules/terraform-aws-opensearch)
- [Terraform Registry - AWS OpenSearch Module](https://registry.terraform.io/modules/terraform-aws-modules/opensearch/aws)

### Best Practices and Guides
- [AWS OpenSearch Service Best Practices](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/bp.html)
- [OpenSearch Service Sizing Guidance](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/sizing-domains.html)
- [OpenSearch Performance Tuning](https://opensearch.org/docs/latest/tuning-your-cluster/)

### Tools and Utilities
- [OpenSearch Dashboards](https://opensearch.org/docs/latest/dashboards/index/)
- [OpenSearch CLI](https://github.com/opensearch-project/opensearch-cli)
- [OpenSearch Benchmark](https://github.com/opensearch-project/OpenSearch-Benchmark)

### AWS Service Integration
- [Using Amazon OpenSearch Service with CloudWatch](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/monitoring-cloudwatch.html)
- [OpenSearch Service with VPC](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/vpc.html)
- [Fine-Grained Access Control](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/fgac.html)

### Community Resources
- [OpenSearch Forum](https://forum.opensearch.org/)
- [AWS re:Post - OpenSearch Service](https://repost.aws/tags/TA4IvCeWI1TE-q7Dbu2SuWig/amazon-open-search-service)

## Notes for AI Agents

### Important Gotchas
- **No default ingress rules**: The module creates a security group but does NOT add ingress rules by default. You MUST specify `security_group_rules` to allow access.
- **Domain names are immutable**: Changing `domain_name` forces resource replacement.
- **Internal user database change**: Changing `advanced_security_options.internal_user_database_enabled` from `true` to `false` requires domain replacement.
- **Master user passwords**: Never hardcode passwords in Terraform. Use AWS Secrets Manager or `random_password` resource.
- **Access policy is open by default**: When `create_access_policy = true`, it creates a permissive policy. Use `access_policy_statements` to restrict access.
- **Downtime on scaling**: Reducing instance count or changing instance types may cause downtime.

### Secure Defaults in v2.5+
This module has secure defaults enabled:
- `encrypt_at_rest.enabled = true`
- `node_to_node_encryption.enabled = true`
- `advanced_security_options.enabled = true`
- `advanced_security_options.anonymous_auth_enabled = false`
- `domain_endpoint_options.enforce_https = true`
- `domain_endpoint_options.tls_security_policy = "Policy-Min-TLS-1-2-2019-07"`
- `auto_tune_options.desired_state = "ENABLED"`
- `software_update_options.auto_software_update_enabled = true`

### When to Use Serverless vs Provisioned
| Use Case | Recommendation |
|----------|----------------|
| Variable/unpredictable workloads | Serverless collection |
| Development/testing | Serverless or small provisioned domain |
| Predictable sustained workloads | Provisioned domain |
| Need UltraWarm/cold storage | Provisioned domain only |
| Cost-sensitive, low traffic | Serverless (pay-per-use) |
| High-throughput, consistent load | Provisioned domain |

### Common Configuration Patterns
- **Development**: Single node, `t3.small.search`, 10-20GB gp3, basic security
- **Small Production**: 2-3 nodes (`r6g.large.search`), 50-100GB per node, multi-AZ, dedicated masters
- **Medium Production**: 3-6 nodes (`r6g.xlarge.search`), 100-500GB per node, 3 dedicated masters
- **Large Production**: 6+ data nodes (`r6g.2xlarge.search`+), UltraWarm nodes, dedicated coordinators

### Minimal Production Example
```hcl
module "opensearch" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.5"

  domain_name    = "my-domain"
  engine_version = "OpenSearch_2.13"

  cluster_config = {
    instance_type            = "r6g.large.search"
    instance_count           = 3
    dedicated_master_enabled = true
    dedicated_master_type    = "r6g.large.search"
    dedicated_master_count   = 3
    zone_awareness_enabled   = true
    zone_awareness_config    = { availability_zone_count = 3 }
  }

  ebs_options = {
    volume_type = "gp3"
    volume_size = 100
    iops        = 3000
    throughput  = 125
  }

  vpc_options = {
    subnet_ids = module.vpc.private_subnets
  }

  # REQUIRED: Add ingress rules (none by default)
  security_group_rules = {
    ingress_443 = {
      type        = "ingress"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = [module.vpc.vpc_cidr_block]
    }
  }

  # Fine-grained access control with IAM role
  advanced_security_options = {
    enabled = true
    master_user_options = {
      master_user_arn = aws_iam_role.opensearch_admin.arn
    }
  }

  tags = { Environment = "production" }
}
```

### Troubleshooting Quick Reference
| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Red cluster status | Unassigned shards, low storage | Check storage, add nodes |
| Yellow cluster status | Missing replicas | Add nodes for replica count |
| Access denied | IAM/FGAC misconfiguration | Check policies and roles |
| Connection timeout | Security group missing rules | Add `security_group_rules` |
| High JVM memory pressure | Too many shards, large queries | Scale up or optimize queries |
