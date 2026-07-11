# Terraform AWS OpenSearch Module

## Module Information

- **Module Name**: `opensearch`
- **Source**: `terraform-aws-modules/opensearch/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-opensearch
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/opensearch/aws/latest
- **Latest Version**: 2.11.0
- **Compatibility**: Terraform >= 1.5.7, AWS provider >= 6.51 (root module and `collection` submodule). AWS provider v6 has been required since module v2.0.0 — pin `~> 2.11` (module) and `~> 6.0` (provider) when generating configs.
- **Purpose**: Terraform module that creates and configures AWS OpenSearch Service domains — and, via a dedicated submodule, OpenSearch Serverless collections — for search, log analytics, and observability workloads
- **Service**: AWS OpenSearch Service
- **Category**: Search & Analytics, Observability, Data Storage
- **Keywords**: opensearch, elasticsearch, search, log-analytics, observability, siem, domain, serverless-collection, vpc, encryption, fine-grained-access-control, saml, cognito, jwt-auth, vector-search, dashboards
- **Use For**: centralized log aggregation and analysis, full-text and e-commerce search, security information and event management (SIEM), application performance monitoring, business intelligence dashboards, IoT and time-series analytics, vector/similarity search for ML and RAG applications, clickstream and user-behavior analysis, searchable document repositories, unified logs/metrics/traces observability platform, pay-per-use serverless search workloads

## Description

This module provisions an AWS OpenSearch Service domain (`aws_opensearch_domain`) along with its supporting infrastructure: an optional VPC-scoped security group, IAM access policy, CloudWatch log groups and the resource policy that authorizes OpenSearch to write to them, VPC endpoints, cross-cluster outbound connections, and package associations. OpenSearch is a community-driven, Apache 2.0-licensed search and analytics suite derived from Elasticsearch; the module also supports legacy Elasticsearch engine versions for domains that have not yet migrated.

The module ships with secure-by-default settings — encryption at rest, node-to-node encryption, enforced HTTPS/TLS 1.2, and fine-grained access control (FGAC) are all enabled unless explicitly disabled — while remaining fully configurable for cluster topology (dedicated master and coordinator nodes, multi-AZ zone awareness), storage (gp3 EBS with configurable IOPS/throughput), and authentication (IAM master user, SAML, Amazon Cognito, IAM Identity Center SSO, or JWT/OIDC). It also exposes newer OpenSearch platform capabilities: AI/ML options (natural-language query generation, S3 Vectors engine, serverless vector acceleration), blue/green deployment strategies, Auto-Tune with scheduled maintenance windows, and automated software updates.

For on-demand, auto-scaling workloads that don't need a persistent provisioned cluster, the module ships a `collection` submodule that creates AWS OpenSearch Serverless collections (`SEARCH`, `TIMESERIES`, or `VECTORSEARCH` types), including access/network/encryption/lifecycle policies and optional collection groups with shared indexing/search capacity limits. The root domain module and the serverless submodule are independent and are typically chosen based on workload predictability rather than composed together.

## Key Features

- **Managed OpenSearch/Elasticsearch Domains**: Full lifecycle management of `aws_opensearch_domain` and its policy, VPC endpoint, and outbound-connection resources
- **OpenSearch Serverless Collections**: Dedicated `collection` submodule for auto-scaled, pay-per-use `SEARCH`, `TIMESERIES`, and `VECTORSEARCH` workloads, including collection groups with shared OCU capacity limits
- **Flexible Cluster Topology**: Instance type/count, dedicated master nodes, and coordinator-only nodes (via `cluster_config.node_options`), with multi-AZ zone awareness across 2-3 Availability Zones
- **Secure Defaults**: Encryption at rest, node-to-node encryption, enforced HTTPS with TLS 1.2+, and fine-grained access control all enabled out of the box
- **Multiple Authentication Methods**: IAM master user, internal user database, SAML, Amazon Cognito for Dashboards, IAM Identity Center SSO, and JWT/OIDC bearer-token authentication
- **AI/ML Options**: Natural-language query generation, S3 Vectors engine, and serverless vector acceleration for GPU-backed vector search
- **Blue/Green Deployment Strategy**: Configurable deployment strategy (`deployment_strategy_options`) to control how domain configuration changes are rolled out
- **Automated CloudWatch Logging**: Log group creation plus an auto-generated resource policy authorizing `es.amazonaws.com` to publish slow/application/audit logs
- **Auto-Tune & Maintenance Scheduling**: Automatic performance tuning with `desired_state`/`rollback_on_disable` and explicit `maintenance_schedule` windows, plus off-peak update windows
- **Software Update Automation**: `software_update_options` for automatic minor version/service software patching
- **Dual-Stack Endpoints**: IPv4-only or dual-stack (IPv4/IPv6) domain and dashboard endpoints (`ip_address_type`)
- **Cross-Cluster Connectivity**: Outbound connections to other OpenSearch domains (`outbound_connections`)
- **Flexible IAM Access Policies**: Build a policy from `access_policy_statements`, merge external `source`/`override` policy documents, or supply a raw `access_policies` JSON document
- **Bring-Your-Own or Managed Security Group**: Auto-created VPC security group (only when `vpc_options` is set) with fully customizable ingress/egress rules, or disable and supply your own
- **Package Associations & VPC Endpoints**: Associate custom dictionaries/plugins and create additional VPC endpoints for the domain
- **Multi-Region Provider Support**: `region` input targets a non-default provider region per module call

## Main Use Cases

1. **Log Analytics**: Centralized aggregation and analysis of application, infrastructure, and security logs
2. **Security Analytics / SIEM**: Threat detection, audit trails, and incident investigation dashboards
3. **Application Performance Monitoring**: Real-time tracing and metrics analysis for distributed systems
4. **Full-Text and E-Commerce Search**: Product catalog search, faceted filtering, and content search
5. **Business Intelligence**: Interactive OpenSearch Dashboards for operational and business metrics
6. **IoT and Time-Series Analytics**: High-volume sensor/metrics ingestion and time-series querying
7. **Vector / Similarity Search**: RAG and ML embedding search via `VECTORSEARCH` collections or domain vector engine options
8. **Clickstream Analysis**: Real-time analysis of user behavior and interaction events
9. **Document Management**: Searchable, metadata-indexed document repositories
10. **Variable-Workload Search**: Pay-per-use OpenSearch Serverless for unpredictable or spiky query/index load

## Submodules

### collection
- **Purpose**: Provision AWS OpenSearch Serverless collections without managing provisioned infrastructure
- **Source**: `terraform-aws-modules/opensearch/aws//modules/collection`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/opensearch/aws/latest/submodules/collection
- **Key Features**: `SEARCH`/`TIMESERIES`/`VECTORSEARCH` collection types, access/network/encryption/lifecycle policy management, collection groups with shared capacity limits
- **Use Cases**: Auto-scaling search/analytics without cluster sizing, vector search for ML/RAG, cost-sensitive/variable-traffic workloads

## Submodule 1: collection

### Description

Creates an `aws_opensearchserverless_collection` and its associated access, network, encryption, and lifecycle policies. OpenSearch Serverless automatically scales indexing and search compute (measured in OpenSearch Compute Units, OCUs) and bills per use, removing the need to size, patch, or manage a provisioned cluster.

### Key Features

- Three collection types: `SEARCH` (general purpose), `TIMESERIES` (logs/metrics, the AWS default when `type` is unset), and `VECTORSEARCH` (ML embeddings)
- Granular access policies scoped to collection- and index-level permissions with configurable IAM principals
- Network policies to restrict access to specific VPC endpoints (`SourceVPCEs`) instead of the public endpoint
- Optional collection groups (`create_collection_group`) that pool indexing/search capacity across collections; `NEXTGEN` generation requires `standby_replicas = "ENABLED"`
- Data lifecycle policies with minimum index retention windows (24h–3650d) or indefinite retention
- Vector search acceleration option (`vector_options.serverless_vector_acceleration`) for `VECTORSEARCH` collections

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the collection |
| `type` | `string` | `null` | `SEARCH`, `TIMESERIES`, or `VECTORSEARCH` (AWS defaults to `TIMESERIES` if unset) |
| `description` | `string` | `null` | Collection description |
| `standby_replicas` | `string` | `null` | `ENABLED` or `DISABLED` (AWS defaults to `ENABLED`) |
| `create_access_policy` | `bool` | `false` | Create an access policy for the collection |
| `access_policy_principals` | `list(string)` | `[]` | IAM principals granted access via the generated policy |
| `access_policy_collection_permissions` / `access_policy_index_permissions` | `list(string)` | `["aoss:*"]` | Collection- and index-level permissions granted |
| `create_network_policy` | `bool` | `false` | Create a network policy restricting collection access |
| `network_policy` | `any` | `{}` | Network rules (e.g., `AllowFromPublic`, `SourceVPCEs`) |
| `create_encryption_policy` | `bool` | `true` | Create a KMS encryption policy for the collection |
| `encryption_policy` | `any` | `{}` | Custom KMS key ARN and resource scoping for encryption |
| `create_lifecycle_policy` | `bool` | `false` | Create a data lifecycle (retention) policy |
| `lifecycle_policy_min_index_retention` | `string` | `null` | Minimum index retention, e.g. `"90d"` (`24h`–`3650d`) |
| `create_collection_group` | `bool` | `false` | Create a collection group with shared capacity limits |
| `collection_group_generation` | `string` | `null` | `CLASSIC` or `NEXTGEN` (`NEXTGEN` requires standby replicas enabled) |
| `collection_group_capacity_limits` | `object` | `null` | Min/max indexing and search OCU limits for the group |
| `vector_options` | `object` | `null` | `serverless_vector_acceleration` setting for `VECTORSEARCH` collections |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | ARN of the collection |
| `id` | Unique identifier of the collection |
| `name` | Name of the collection |
| `endpoint` | Endpoint used to submit index, search, and data upload requests |
| `dashboard_endpoint` | Endpoint used to access OpenSearch Dashboards |
| `kms_key_arn` | ARN of the KMS key used to encrypt the collection |
| `collection_group_arn` / `collection_group_id` | Identifiers of the collection group (if created) |

### Usage Example

```hcl
module "opensearch_serverless" {
  source  = "terraform-aws-modules/opensearch/aws//modules/collection"
  version = "~> 2.11"

  name        = "product-search"
  description = "Product catalog search"
  type        = "SEARCH"

  create_access_policy  = true
  access_policy_principals = [
    aws_iam_role.search_app.arn,
  ]

  create_network_policy = true
  network_policy = {
    AllowFromPublic = false
    SourceVPCEs     = [aws_opensearchserverless_vpc_endpoint.this.id]
  }

  standby_replicas = "ENABLED"

  tags = {
    Environment = "production"
  }
}

resource "aws_opensearchserverless_vpc_endpoint" "this" {
  name       = "product-search"
  subnet_ids = module.vpc.private_subnets
  vpc_id     = module.vpc.vpc_id
}
```

## Main Module: OpenSearch Domain

### Description

The root module creates the OpenSearch/Elasticsearch domain itself along with its access policy, security group, CloudWatch logging, VPC endpoints, outbound connections, and package associations. It is the entry point for provisioned (non-serverless) OpenSearch clusters and exposes composition outputs (`domain_endpoint`, `domain_arn`, `security_group_id`, etc.) consumed by application, DNS, and monitoring configurations.

### Key Features

- `cluster_config`, `ebs_options`, `advanced_security_options`, `auto_tune_options`, and several other complex arguments are typed `any` and passed through directly to the underlying `aws_opensearch_domain` resource, so any attribute supported by the AWS provider's corresponding block (including UltraWarm/cold storage or coordinator `node_options`) can be set
- Fine-grained access control is enabled by default — a master user (via `master_user_options`) or IAM Identity Center integration must be supplied or `apply` will fail
- No IAM access policy is attached unless `access_policy_statements`, `access_policy_source_policy_documents`, `access_policy_override_policy_documents`, or a raw `access_policies` document is provided
- Security group is created only when `vpc_options` is set, and has **no ingress rules by default**

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `domain_name` | `string` | `""` | Name of the domain — always set explicitly; empty string will fail domain creation |
| `create` | `bool` | `true` | Whether to create all domain-related resources |
| `engine_version` | `string` | `null` | Engine version, validated against `OpenSearch_X.Y` / `Elasticsearch_X.Y` format |
| `cluster_config` | `any` | `{dedicated_master_enabled: true}` | Instance type/count, dedicated master, coordinator `node_options`, zone awareness |
| `ebs_options` | `any` | `{ebs_enabled: true, volume_size: 64, volume_type: "gp3"}` | EBS volume type/size/IOPS/throughput |
| `vpc_options` | `any` | `{}` | `subnet_ids`/`security_group_ids` to deploy the domain inside a VPC |
| `advanced_security_options` | `any` | `{enabled: true, anonymous_auth_enabled: false}` | FGAC, `master_user_options`, `jwt_options` |
| `identity_center_options` | `object` | `null` | IAM Identity Center SSO integration |
| `encrypt_at_rest` | `any` | `{enabled: true}` | KMS encryption at rest (defaults to the AWS-managed key if no `kms_key_id` given) |
| `node_to_node_encryption` | `any` | `{enabled: true}` | Inter-node TLS encryption |
| `domain_endpoint_options` | `any` | `{enforce_https: true, tls_security_policy: "Policy-Min-TLS-1-2-2019-07"}` | HTTPS enforcement and TLS policy |
| `ip_address_type` | `string` | `null` | `ipv4` or `dualstack` endpoint addressing |
| `access_policy_statements` | `any` | `{}` | IAM statements used to build the domain access policy (required for the policy to be created) |
| `create_access_policy` / `enable_access_policy` | `bool` | `true` / `true` | Whether to build, and whether to attach, the computed access policy |
| `access_policies` | `string` | `null` | Raw IAM policy JSON, used when `create_access_policy = false` |
| `create_security_group` / `security_group_rules` | `bool` / `any` | `true` / `{}` | Security group for the domain (only created if `vpc_options` set); no ingress rules by default |
| `log_publishing_options` | `any` | `[{log_type: "INDEX_SLOW_LOGS"}, {log_type: "SEARCH_SLOW_LOGS"}]` | CloudWatch log types to publish |
| `create_cloudwatch_log_resource_policy` / `cloudwatch_log_resource_policy_name` | `bool` / `string` | `true` / `null` | Auto-create the resource policy allowing OpenSearch to write logs (named `opensearch-<domain_name>` by default) |
| `cloudwatch_log_group_retention_in_days` | `number` | `60` | Log retention period |
| `auto_tune_options` | `any` | `{desired_state: "ENABLED", rollback_on_disable: "NO_ROLLBACK"}` | Auto-Tune state, rollback behavior, `maintenance_schedule` |
| `off_peak_window_options` | `any` | `{enabled: true, off_peak_window: {hours: 7}}` | Off-peak update window |
| `software_update_options` | `any` | `{auto_software_update_enabled: true}` | Automatic service software updates |
| `deployment_strategy_options` | `object` | `null` | Blue/green vs. in-place deployment strategy |
| `aiml_options` | `object` | `null` | Natural-language query generation, S3 Vectors engine, serverless vector acceleration |
| `cognito_options` | `any` | `{}` | Cognito authentication for Dashboards |
| `create_saml_options` / `saml_options` | `bool` / `any` | `false` / `{}` | SAML authentication for Dashboards |
| `outbound_connections` | `any` | `{}` | Cross-cluster outbound connections to other domains |
| `vpc_endpoints` | `any` | `{}` | Additional VPC endpoints for the domain |
| `package_associations` | `map(string)` | `{}` | Package (dictionary/plugin) associations |
| `region` | `string` | `null` | Override the provider region for this module call |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `domain_arn` | ARN of the OpenSearch domain |
| `domain_id` | Unique identifier of the domain |
| `domain_name` | Name of the domain |
| `domain_endpoint` / `domain_endpoint_v2` | Primary and dual-stack (IPv4/IPv6) endpoints for index/search/upload requests |
| `domain_dashboard_endpoint` / `domain_dashboard_endpoint_v2` | Primary and dual-stack Dashboards endpoints (no `https` scheme) |
| `domain_endpoint_v2_hosted_zone_id` | Hosted zone ID for the dual-stack endpoint |
| `security_group_id` / `security_group_arn` | Identifiers of the security group created (if any) |
| `cloudwatch_logs` | Map of CloudWatch log groups created and their attributes |
| `vpc_endpoints` | Map of VPC endpoints created and their attributes |
| `outbound_connections` | Map of outbound connections created and their attributes |
| `package_associations` | Map of package associations created and their attributes |

### Usage Examples

#### Example 1: Basic Development Domain

```hcl
module "opensearch" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.11"

  domain_name    = "dev-search"
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

  # FGAC is enabled by default and requires a master user
  advanced_security_options = {
    enabled                        = true
    internal_user_database_enabled = true

    master_user_options = {
      master_user_name     = "admin"
      master_user_password = random_password.master.result
    }
  }

  tags = {
    Environment = "development"
  }
}

resource "random_password" "master" {
  length  = 16
  special = true
}
```

#### Example 2: Production Multi-AZ Domain in a VPC

```hcl
module "opensearch" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.11"

  domain_name    = "prod-search"
  engine_version = "OpenSearch_2.13"

  cluster_config = {
    instance_type            = "r6g.large.search"
    instance_count            = 3
    dedicated_master_enabled  = true
    dedicated_master_type     = "c6g.large.search"
    dedicated_master_count    = 3
    zone_awareness_enabled    = true
    zone_awareness_config     = { availability_zone_count = 3 }
  }

  ebs_options = {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 100
    iops        = 3000
    throughput  = 125
  }

  vpc_options = {
    subnet_ids = module.vpc.private_subnets
  }

  # Security group rules use the AWS provider v6 rule schema (ip_protocol / cidr_ipv4)
  security_group_rules = {
    ingress_https = {
      type        = "ingress"
      description = "HTTPS from VPC"
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      cidr_ipv4   = module.vpc.vpc_cidr_block
    }
  }

  advanced_security_options = {
    enabled = true
    master_user_options = {
      master_user_arn = aws_iam_role.opensearch_admin.arn
    }
  }

  encrypt_at_rest = {
    enabled    = true
    kms_key_id = aws_kms_key.opensearch.arn
  }

  log_publishing_options = [
    { log_type = "INDEX_SLOW_LOGS" },
    { log_type = "SEARCH_SLOW_LOGS" },
    { log_type = "ES_APPLICATION_LOGS" },
  ]

  tags = {
    Environment = "production"
    Application = "log-analytics"
  }
}
```

#### Example 3: Domain with SAML and JWT/OIDC Authentication

```hcl
module "opensearch_saml_jwt" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.11"

  domain_name    = "sso-search"
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

  advanced_security_options = {
    enabled = true

    master_user_options = {
      master_user_arn = aws_iam_role.opensearch_admin.arn
    }

    # JWT/OIDC bearer-token authentication (in addition to master user)
    jwt_options = {
      enabled     = true
      jwks_url    = "https://idp.example.com/.well-known/jwks.json"
      roles_key   = "roles"
      subject_key = "sub"
    }
  }

  # SAML for Dashboards sign-in
  create_saml_options = true
  saml_options = {
    enabled = true
    idp = {
      entity_id        = "https://idp.example.com/metadata"
      metadata_content = file("${path.module}/saml-metadata.xml")
    }
    master_backend_role = "admins"
    roles_key            = "roles"
    subject_key           = "email"
  }

  domain_endpoint_options = {
    enforce_https = true
  }

  tags = {
    Authentication = "saml-jwt"
  }
}
```

#### Example 4: Domain with AI/ML Options and Blue/Green Deployment

```hcl
module "opensearch_ai" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.11"

  domain_name    = "vector-search"
  engine_version = "OpenSearch_2.13"

  cluster_config = {
    instance_type  = "r6g.xlarge.search"
    instance_count = 3
  }

  ebs_options = {
    ebs_enabled = true
    volume_size = 200
    volume_type = "gp3"
  }

  aiml_options = {
    natural_language_query_generation_options = {
      desired_state = "ENABLED"
    }
    serverless_vector_acceleration = {
      enabled = true
    }
  }

  deployment_strategy_options = {
    deployment_strategy = "BLUE_GREEN"
  }

  advanced_security_options = {
    enabled = true
    master_user_options = {
      master_user_arn = aws_iam_role.opensearch_admin.arn
    }
  }

  tags = {
    Workload = "vector-search"
  }
}
```

## Best Practices

### Security

1. **Always supply a master user**: FGAC (`advanced_security_options.enabled = true`) is on by default and requires `master_user_options` (name/password or ARN) or `identity_center_options` — otherwise `terraform apply` fails.
2. **Deploy within a VPC**: Set `vpc_options.subnet_ids` to place the domain in private subnets; a security group is only created when `vpc_options` is set.
3. **Explicitly add ingress rules**: The auto-created security group has no ingress rules by default — use the `ip_protocol`/`cidr_ipv4` rule schema (AWS provider v6) in `security_group_rules`.
4. **Scope the access policy deliberately**: No IAM access policy is attached unless `access_policy_statements` (or a raw `access_policies` document) is supplied — for public (non-VPC) domains, always define one.
5. **Prefer IAM roles over passwords**: Use `master_user_arn` with an IAM role instead of `master_user_name`/`master_user_password` where possible; if passwords are required, generate them with `random_password` or source them from AWS Secrets Manager — never hardcode.
6. **Use dedicated master nodes**: Enable 3 dedicated master nodes in production to isolate cluster management from data-node load.
7. **Keep encryption at rest and node-to-node encryption enabled**: Both default to `enabled = true`; only disable for throwaway/test domains.
8. **Enforce HTTPS and modern TLS**: Keep `domain_endpoint_options.enforce_https = true` and `tls_security_policy = "Policy-Min-TLS-1-2-2019-07"` (the module default).
9. **Enable audit logs for compliance**: Add `AUDIT_LOGS` to `log_publishing_options` alongside slow/application logs to track authentication and data-access events.
10. **Use VPC endpoints for private connectivity**: Add entries to `vpc_endpoints` so other VPCs/services reach the domain without traversing the internet.

### High Availability and Disaster Recovery

1. **Enable zone awareness across 3 AZs**: Set `cluster_config.zone_awareness_enabled = true` with `zone_awareness_config.availability_zone_count = 3` for production.
2. **Run 3 dedicated master nodes**: Maintains quorum during node failure or maintenance.
3. **Configure automated snapshots**: OpenSearch automatically snapshots to a service-managed S3 location; validate restore procedures periodically.
4. **Use cross-cluster outbound connections for DR**: `outbound_connections` can replicate to a domain in another region/account for geo-redundancy.
5. **Monitor cluster health continuously**: Alarm on cluster status (red/yellow), free storage space, and unassigned shards.
6. **Use `off_peak_window_options` for maintenance**: Schedule software/config updates during low-traffic hours (default: 7-hour window starting at a service-chosen off-peak time).
7. **Consider `deployment_strategy_options = "BLUE_GREEN"`**: Reduces risk and downtime for major configuration or version changes versus in-place updates.

### Performance Optimization

1. **Right-size instances by workload**: Compute-optimized instances for query-heavy workloads, memory-optimized (`r6g`) for data/aggregation-heavy workloads.
2. **Use `gp3` EBS volumes**: Configure `iops`/`throughput` independently of volume size for better price-performance than `gp2`/`io1`.
3. **Keep Auto-Tune enabled**: `auto_tune_options.desired_state = "ENABLED"` (the default) lets AWS continuously tune JVM/memory settings.
4. **Use coordinator-only nodes for heavy query fan-out**: Configure dedicated coordinator nodes via `cluster_config.node_options` to offload search coordination from data nodes.
5. **Monitor and review slow logs regularly**: `INDEX_SLOW_LOGS`/`SEARCH_SLOW_LOGS` are published by default — use them to find and fix expensive queries/indexing patterns.
6. **Maintain free storage headroom**: Keep at least 20-25% free disk space per node to allow shard rebalancing.
7. **Avoid over-sharding**: Target roughly 25 shards or fewer per GiB of JVM heap to reduce overhead and memory pressure.

### Cost Optimization

1. **Use Graviton (ARM) instance families**: `r6g`/`c6g`/`m6g` instances offer better price-performance than equivalent x86 generations.
2. **Choose OpenSearch Serverless for variable workloads**: The `collection` submodule bills per OCU-hour, avoiding over-provisioned idle capacity.
3. **Right-size and monitor log retention**: `cloudwatch_log_group_retention_in_days` defaults to 60 days — reduce for non-critical log types.
4. **Consolidate CloudWatch log resource policies where possible**: AWS enforces an account/region-wide limit of 10 CloudWatch Logs resource policies; if deploying many domains, set `create_cloudwatch_log_resource_policy = false` (after the first) or share a `cloudwatch_log_resource_policy_name`.
5. **Evaluate Reserved Instances** for predictable, long-running production domains.
6. **Trim unused replicas**: Balance `standby_replicas`/replica counts against availability requirements instead of defaulting to the maximum.

### Operational Excellence

1. **Pin the module and provider versions**: Use `version = "~> 2.11"` for the module and `~> 6.0` for the AWS provider to avoid unexpected breaking changes.
2. **Validate `engine_version` format early**: The module enforces a regex (`OpenSearch_X.Y` / `Elasticsearch_X.Y`); malformed values fail at `plan` time rather than `apply`.
3. **Test upgrades in non-production first**: Engine version and cluster topology changes can trigger blue/green deployments or downtime — validate in staging.
4. **Use Infrastructure as Code end-to-end**: Manage index templates, ISM policies, and Dashboards objects alongside the domain definition where practical.
5. **Tag comprehensively**: Combine the global `tags` map with `security_group_tags` for cost allocation and ownership tracking.
6. **Reference module outputs for composition**: Use `domain_endpoint`, `domain_arn`, and `security_group_id` when wiring in application, DNS, or monitoring configuration rather than hardcoding values.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-opensearch
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/opensearch/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-opensearch/tree/master/examples
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-opensearch/blob/master/CHANGELOG.md
- **AWS OpenSearch Service Documentation**: https://docs.aws.amazon.com/opensearch-service/
- **AWS OpenSearch Service Best Practices**: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/bp.html
- **Fine-Grained Access Control**: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/fgac.html
- **OpenSearch Serverless Documentation**: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html
- **OpenSearch Project Documentation**: https://opensearch.org/docs/latest/
- **OpenSearch Dashboards**: https://opensearch.org/docs/latest/dashboards/index/

## Notes for AI Agents

### Important Gotchas

- **FGAC requires a master user by default**: `advanced_security_options` defaults to `{enabled: true, anonymous_auth_enabled: false}` with no master user — you MUST supply `master_user_options` (name/password or ARN) or `identity_center_options`, or the domain will fail to create.
- **No access policy is attached unless statements are given**: `create_access_policy = true` merely allows a policy to be built; without `access_policy_statements`/`access_policy_source_policy_documents`/`access_policy_override_policy_documents`/`access_policies`, no `aws_opensearch_domain_policy` resource is created at all — this is not "open by default," it simply relies on VPC placement and FGAC for access control.
- **Security group requires `vpc_options`**: `create_security_group = true` has no effect unless `vpc_options.subnet_ids` is also set; the group has no ingress rules by default.
- **Security group rule schema changed**: Rules use the AWS provider v6 attributes `ip_protocol`/`cidr_ipv4`/`cidr_ipv6` (separate `aws_vpc_security_group_ingress_rule`/`egress_rule` resources), not the legacy `protocol`/`cidr_blocks` schema.
- **`domain_name` defaults to an empty string**: Always set it explicitly; an empty domain name will fail at apply time.
- **`engine_version` is validated**: Must match `OpenSearch_X.Y` or `Elasticsearch_X.Y` (e.g., `OpenSearch_2.13`) — full service versions with dates/patches will fail validation.
- **CloudWatch Logs resource policy limit**: A resource policy named `opensearch-<domain_name>` is auto-created per domain by default (`create_cloudwatch_log_resource_policy = true`); AWS allows only 10 such policies per account/region, so deploying many domains requires disabling this after the first or sharing a policy name.
- **AWS provider v6 required**: Module v2.0.0+ requires AWS provider `>= 6.x` (currently `>= 6.51`), a breaking change from v1.x modules that supported provider v4/v5.
- **Domain names are immutable**: Changing `domain_name` forces resource replacement.
- **Downtime risk on scaling**: Reducing instance count, changing instance types, or toggling `internal_user_database_enabled` can trigger in-place reconfiguration or replacement — consider `deployment_strategy_options = "BLUE_GREEN"` for safer rollouts.

### When to Use Serverless vs Provisioned

| Use Case | Recommendation |
|----------|----------------|
| Variable/unpredictable workloads | `collection` submodule (Serverless) |
| Development/testing | Serverless or a small single-node domain |
| Predictable, sustained high-throughput workloads | Provisioned domain |
| Need UltraWarm/cold storage tiers | Provisioned domain only |
| Cost-sensitive, low/spiky traffic | Serverless (pay-per-OCU) |
| Vector/RAG search at scale | Either — use `VECTORSEARCH` collection type, or domain `aiml_options.serverless_vector_acceleration` |

### Minimal Production Example

```hcl
module "opensearch" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "~> 2.11"

  domain_name    = "my-domain"
  engine_version = "OpenSearch_2.13"

  cluster_config = {
    instance_type            = "r6g.large.search"
    instance_count            = 3
    dedicated_master_enabled  = true
    dedicated_master_type     = "r6g.large.search"
    dedicated_master_count    = 3
    zone_awareness_enabled    = true
    zone_awareness_config     = { availability_zone_count = 3 }
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

  # REQUIRED: add ingress rules (none by default)
  security_group_rules = {
    ingress_https = {
      type        = "ingress"
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      cidr_ipv4   = module.vpc.vpc_cidr_block
    }
  }

  # REQUIRED: FGAC is on by default and needs a master user
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
| Apply fails on domain creation | FGAC enabled without a master user | Set `advanced_security_options.master_user_options` or `identity_center_options` |
| Connection timeout to the domain | Security group missing ingress rules | Add `security_group_rules` (no default ingress) |
| Access denied on requests | No access policy + no FGAC identity match | Supply `access_policy_statements` and/or correct master user/IAM role |
| Red cluster status | Unassigned shards, low storage | Check free storage, add nodes/increase volume size |
| Yellow cluster status | Missing replicas across AZs | Increase node/replica count, verify `zone_awareness_config` |
| `ResourceLimitExceededException` on CloudWatch policy | Account-wide 10-policy limit for CloudWatch Logs resource policies | Set `create_cloudwatch_log_resource_policy = false` on subsequent domains or share a policy name |
| High JVM memory pressure | Too many shards or oversized queries | Scale up, reduce shard count, or add coordinator nodes |
