# Terraform AWS Managed Service for Prometheus Module

## Module Information

- **Module Name**: `managed-service-prometheus`
- **Module ID**: `terraform-aws-modules/managed-service-prometheus/aws`
- **Source**: `terraform-aws-modules/managed-service-prometheus/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-prometheus
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/managed-service-prometheus/aws/latest
- **Latest Version**: 4.3.1
- **Purpose**: Terraform module that creates and manages AWS Managed Service for Prometheus (AMP) workspaces, workspace configuration (retention/cardinality limits), Alert Manager definitions, rule group namespaces, and resource policies
- **Service**: AWS Managed Service for Prometheus (Amazon Managed Prometheus / AMP)
- **Category**: Monitoring, Observability, Container Management
- **Keywords**: prometheus, amp, monitoring, observability, metrics, kubernetes, eks, alertmanager, recording-rules, alerting-rules, rule-groups, workspace, promql, kms-encryption, cardinality-limits, resource-policy
- **Use For**: Kubernetes/EKS cluster monitoring, container workload observability, microservices metric aggregation, application performance monitoring, alerting and notification routing, recording rule automation, long-term metrics retention, cross-account/Grafana metric sharing

## Description

This Terraform module manages AWS Managed Service for Prometheus (AMP) resources: workspaces, workspace configuration (metric retention and per-label-set cardinality limits), Alert Manager definitions, rule group namespaces (recording/alerting rules), CloudWatch log groups, and IAM resource policies. It is a single flat module with no submodules — every resource type is toggled through boolean `create_*` flags and optional input objects, and the same module block can either provision a brand-new workspace or attach rules/alerts to an existing one via `workspace_id`.

AWS Managed Service for Prometheus is a fully managed, serverless, Multi-AZ, Prometheus-compatible monitoring backend for metrics ingestion (via `remote_write`, typically from a Prometheus agent, the OpenTelemetry Collector/ADOT, or the EKS add-on), storage, and PromQL querying at scale — commonly paired with Amazon Managed Grafana or self-hosted Grafana (SigV4-authenticated) for visualization. It removes the operational burden of running and scaling Prometheus servers while remaining fully compatible with the Prometheus data model, PromQL, and the Alertmanager configuration format.

The module encodes several AWS-side defaults that matter for correct usage: it creates a workspace, an Alert Manager definition (with a built-in no-op default config), and a resource policy (granting the caller's own account full access plus read-only access for Amazon Managed Grafana) unless explicitly disabled. Retention/cardinality limits and the resource policy are only provisioned alongside a **newly created** workspace (`create_workspace = true`); they cannot be attached to an externally supplied `workspace_id`. See "Common Pitfalls" below for the exact conditions.

## Key Features

- **Workspace Creation**: Automated creation of AMP workspaces with a custom `alias`, or reuse of an existing workspace via `workspace_id` + `create_workspace = false`
- **Workspace Configuration**: Configurable metric `retention_period_in_days` and per-label-set cardinality limits (`limits_per_label_set`) to bound active series and control cost — provisioned via a separate `aws_prometheus_workspace_configuration` resource
- **Alert Manager Definition**: Declarative Alertmanager YAML config for routing/receivers (SNS, etc.); created by default with a minimal no-op config even if not overridden
- **Rule Group Namespaces**: Any number of namespaces (`rule_group_namespaces`) holding Prometheus recording and alerting rule groups, addable to new or existing workspaces
- **Resource Policy**: IAM resource policy for the workspace; when enabled without custom statements, defaults to full read/write for the caller's own account and read-only for the Amazon Managed Grafana service principal
- **CloudWatch Logging**: Optional log group creation/attachment for workspace request logging, with configurable name, name-prefix mode, log class (`STANDARD`/`INFREQUENT_ACCESS`), retention, and KMS key
- **KMS Encryption**: Customer-managed KMS key support for both workspace data at rest (`kms_key_arn`) and CloudWatch log group encryption (`cloudwatch_log_group_kms_key_id`)
- **Region Override**: Per-module-call `region` variable to target a region other than the provider default (multi-region root modules)
- **Conditional Creation**: Every resource type is gated by its own `create_*` boolean flag, plus a top-level `create` kill switch

## Main Use Cases

1. **Kubernetes/EKS Cluster Monitoring**: Ingest and query metrics scraped from EKS or self-managed Kubernetes clusters
2. **Container Workload Observability**: Monitor containerized application performance and resource utilization
3. **Microservices Monitoring**: Track metrics across distributed microservices architectures
4. **Multi-Cluster Aggregation**: Centralize metrics from multiple clusters/regions into one or more workspaces
5. **Alerting and Notification**: Route metric-based alerts to SNS and other Alertmanager receivers
6. **Recording Rule Automation**: Precompute expensive PromQL aggregations for faster dashboards and cheaper queries
7. **Long-Term Metrics Retention**: Retain infrastructure/application metrics beyond typical scrape-target lifetimes
8. **Cross-Account / Grafana Access**: Share a workspace with other accounts or Amazon Managed Grafana via resource policy

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Top-level switch; when `false`, no resources are created |
| `region` | `string` | `null` | AWS region for this module's resources; defaults to the provider's region |
| `tags` | `map(string)` | `{}` | Tags applied to workspace and log group resources |
| `create_workspace` | `bool` | `true` | Create a new workspace, or attach to an existing one via `workspace_id` |
| `workspace_id` | `string` | `""` | ID of an existing workspace (required when `create_workspace = false`) |
| `workspace_alias` | `string` | `null` | Alias for the Prometheus workspace |
| `kms_key_arn` | `string` | `null` | KMS key ARN for workspace encryption at rest |
| `logging_configuration` | `object` | `null` | `{ create_log_group, log_group_arn }`; attaches CloudWatch logging to the workspace |
| `retention_period_in_days` | `number` | `null` | Metric retention; only takes effect when `limits_per_label_set` is also non-null |
| `limits_per_label_set` | `list(object)` | `null` | Per-label-set cardinality limits (`label_set`, `limits.max_series`); non-null (even `[]`) is required to create the workspace configuration resource |
| `create_resource_policy` | `bool` | `true` | Create an IAM resource policy for the workspace (new workspaces only) |
| `resource_policy_statements` | `map(object)` | `null` | Custom IAM statements; overrides the module's default statements — fields: `sid`, `actions`, `not_actions`, `effect`, `resources`, `not_resources`, `principals`, `not_principals`, … (8 shown; call get_module with sections=["inputs","outputs"] for the complete list) |
| `cloudwatch_log_group_name` | `string` | `null` | Custom log group name; defaults to `/aws/prometheus/<workspace_alias>` |
| `cloudwatch_log_group_use_name_prefix` | `bool` | `false` | Use `cloudwatch_log_group_name` as a name prefix instead of exact name |
| `cloudwatch_log_group_class` | `string` | `null` | `STANDARD` or `INFREQUENT_ACCESS` |
| `cloudwatch_log_group_retention_in_days` | `number` | `30` | Days to retain CloudWatch logs (`0` = indefinite) |
| `cloudwatch_log_group_kms_key_id` | `string` | `null` | KMS key ARN for log group encryption |
| `create_alert_manager` | `bool` | `true` | Create an Alert Manager definition |
| `alert_manager_definition` | `string` | minimal no-op config | Alertmanager configuration in YAML |
| `rule_group_namespaces` | `map(object)` | `null` | Map of `{ name, data }` rule group namespace definitions |

## Main Outputs

| Output | Description |
|--------|-------------|
| `workspace_arn` | Amazon Resource Name (ARN) of the workspace |
| `workspace_id` | Identifier of the workspace |
| `workspace_prometheus_endpoint` | Prometheus remote-write/query endpoint for this workspace |

## Usage Examples

### Example 1: Basic Workspace

```hcl
module "prometheus" {
  source  = "terraform-aws-modules/managed-service-prometheus/aws"
  version = "~> 4.3"

  workspace_alias = "production-metrics"

  tags = {
    Environment = "production"
    Application = "monitoring"
    ManagedBy   = "Terraform"
  }
}
```

### Example 2: Workspace with CloudWatch Logging

```hcl
module "prometheus" {
  source  = "terraform-aws-modules/managed-service-prometheus/aws"
  version = "~> 4.3"

  workspace_alias = "production-metrics"

  # Must be set explicitly - the workspace does NOT get a logging_configuration
  # block unless this object is provided (see Common Pitfalls)
  logging_configuration = {
    create_log_group = true
  }

  cloudwatch_log_group_retention_in_days = 14

  tags = {
    Environment = "production"
    Application = "monitoring"
  }
}
```

### Example 3: Retention and Cardinality Limits

```hcl
module "prometheus" {
  source  = "terraform-aws-modules/managed-service-prometheus/aws"
  version = "~> 4.3"

  workspace_alias = "eks-monitoring"

  # retention_period_in_days is silently ignored unless limits_per_label_set
  # is also set (non-null) - both belong to the same workspace_configuration resource
  retention_period_in_days = 60

  limits_per_label_set = [
    {
      label_set = { environment = "dev" }
      limits    = { max_series = 100000 }
    },
    {
      label_set = { environment = "prod" }
      limits    = { max_series = 400000 }
    }
  ]

  logging_configuration = {
    create_log_group = true
  }

  tags = {
    Environment = "production"
    Application = "eks-monitoring"
  }
}
```

### Example 4: Alert Manager and Rule Groups

```hcl
module "prometheus" {
  source  = "terraform-aws-modules/managed-service-prometheus/aws"
  version = "~> 4.3"

  workspace_alias = "eks-monitoring"

  create_alert_manager     = true
  alert_manager_definition = <<-EOT
  alertmanager_config: |
    route:
      receiver: 'default'
      group_by: ['alertname', 'cluster']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 12h
      routes:
        - receiver: 'critical'
          match:
            severity: 'critical'
    receivers:
      - name: 'default'
        sns_configs:
          - topic_arn: 'arn:aws:sns:us-east-1:123456789012:prometheus-default'
      - name: 'critical'
        sns_configs:
          - topic_arn: 'arn:aws:sns:us-east-1:123456789012:prometheus-critical'
  EOT

  rule_group_namespaces = {
    recording_rules = {
      name = "eks-recording-rules"
      data = <<-EOT
      groups:
        - name: cpu_usage_recording
          interval: 30s
          rules:
            - record: cluster:cpu_usage:rate5m
              expr: sum(rate(container_cpu_usage_seconds_total{image!=""}[5m])) by (cluster)
            - record: namespace:cpu_usage:rate5m
              expr: sum(rate(container_cpu_usage_seconds_total{image!=""}[5m])) by (namespace)
      EOT
    }

    alerting_rules = {
      name = "eks-alerting-rules"
      data = <<-EOT
      groups:
        - name: resource_alerts
          rules:
            - alert: HighCPUUsage
              expr: cluster:cpu_usage:rate5m > 0.8
              for: 5m
              labels:
                severity: warning
              annotations:
                summary: "High CPU usage detected"
                description: "Cluster {{ $labels.cluster }} CPU usage is above 80%"
      EOT
    }
  }

  tags = {
    Environment = "production"
    Application = "eks-monitoring"
  }
}
```

### Example 5: Cross-Account / Grafana Resource Policy

```hcl
module "prometheus" {
  source  = "terraform-aws-modules/managed-service-prometheus/aws"
  version = "~> 4.3"

  workspace_alias = "shared-metrics"

  # Overrides the module's default statements (own-account RW + Grafana RO)
  create_resource_policy = true
  resource_policy_statements = {
    read_access = {
      sid     = "CrossAccountReadAccess"
      actions = [
        "aps:QueryMetrics",
        "aps:GetSeries",
        "aps:GetLabels",
        "aps:GetMetricMetadata"
      ]
      effect    = "Allow"
      resources = ["*"]
      principals = [{
        type        = "AWS"
        identifiers = ["arn:aws:iam::ACCOUNT_ID:root"]
      }]
    }
  }

  tags = {
    Environment = "production"
    Purpose     = "cross-account-monitoring"
  }
}
```

### Example 6: Adding Rules to an Existing Workspace

```hcl
module "prometheus_rules" {
  source  = "terraform-aws-modules/managed-service-prometheus/aws"
  version = "~> 4.3"

  create_workspace = false
  workspace_id     = "ws-12345678-1234-1234-1234-123456789012"

  # Only alert_manager_definition and rule_group_namespaces can target an
  # existing workspace - retention/limits, resource policy, and CloudWatch
  # logging require create_workspace = true (see Common Pitfalls)
  rule_group_namespaces = {
    custom_metrics = {
      name = "application-metrics"
      data = <<-EOT
      groups:
        - name: application_recording
          rules:
            - record: app:request_duration:p95
              expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
      EOT
    }
  }

  tags = {
    Environment = "production"
    Type        = "custom-rules"
  }
}
```

### Example 7: KMS-Encrypted Workspace

```hcl
resource "aws_kms_key" "prometheus" {
  description             = "KMS key for Prometheus workspace encryption"
  deletion_window_in_days = 10
}

module "prometheus" {
  source  = "terraform-aws-modules/managed-service-prometheus/aws"
  version = "~> 4.3"

  workspace_alias = "encrypted-metrics"
  kms_key_arn     = aws_kms_key.prometheus.arn

  logging_configuration = {
    create_log_group = true
  }
  cloudwatch_log_group_kms_key_id = aws_kms_key.prometheus.arn

  tags = {
    Environment = "production"
    Encrypted   = "true"
  }
}
```

## Best Practices

### Common Pitfalls & Non-Obvious Behavior

1. **Retention Requires Cardinality Limits to Be Set**: `retention_period_in_days` is applied by the `aws_prometheus_workspace_configuration` resource, which is only created when `limits_per_label_set` is non-null. Setting `retention_period_in_days` alone (without `limits_per_label_set`) is silently ignored — pass `limits_per_label_set = []` if you want custom retention without cardinality limits.
2. **Logging Must Be Explicitly Attached**: Leaving `logging_configuration` at its default (`null`) still creates a standalone CloudWatch log group, but it is **not** attached to the workspace, because the workspace's `logging_configuration` block only renders when the variable is explicitly set. Always pass `logging_configuration = { create_log_group = true }` (or an existing `log_group_arn`) to actually enable workspace request logging.
3. **Existing Workspaces Get Fewer Resources**: When `create_workspace = false` (attaching to an existing `workspace_id`), only the Alert Manager definition and rule group namespaces can be managed by this module call. Workspace configuration (retention/limits), the resource policy, and the CloudWatch log group are all gated on `create_workspace = true` and are skipped for externally supplied workspaces.
4. **A Resource Policy Is Created by Default**: `create_resource_policy` defaults to `true`. Without `resource_policy_statements`, the module attaches a default policy granting the caller's own account full read/write (`aps:RemoteWrite`, `QueryMetrics`, `GetSeries`, `GetLabels`, `GetMetricMetadata`) plus read-only access for the Amazon Managed Grafana service principal. Set `create_resource_policy = false` if no resource policy should exist at all.
5. **Alert Manager Is Always Created**: `create_alert_manager` defaults to `true` with a built-in minimal (no-op) Alertmanager config, so a bare-bones module call still creates a working-but-unrouted Alert Manager definition. Override `alert_manager_definition` to add real receivers.

### Security and Access Control

1. **Enable KMS Encryption**: Use customer-managed KMS keys (`kms_key_arn`) for encrypting metrics at rest to maintain control over key policies and meet compliance requirements.
2. **Scope Resource Policy Statements**: Replace the default full-access statement with least-privilege `resource_policy_statements` scoped to specific principals and actions (e.g., `aps:QueryMetrics` only for read-only consumers).
3. **Encrypt CloudWatch Logs**: Set `cloudwatch_log_group_kms_key_id` to encrypt workspace request logs.
4. **Use VPC Endpoints**: Deploy interface VPC endpoints for AMP so remote-write/query traffic stays within the AWS network.

### Configuration and Management

1. **Use Descriptive Workspace Aliases**: Apply meaningful `workspace_alias` values indicating environment, purpose, and team ownership.
2. **Organize Rule Groups Logically**: Separate recording rules and alerting rules into different `rule_group_namespaces` entries.
3. **Version Control Rule/Alert Configurations**: Store Alert Manager definitions and rule group YAML in version control alongside the Terraform code.
4. **Pin the Module Version**: Use a version constraint like `version = "~> 4.3"` for stability; note that v4.0.0 bumped the minimum Terraform version to `1.5.7` and AWS provider to `6.0` (breaking change).

### Performance and Cost Optimization

1. **Set Appropriate Retention**: Configure `retention_period_in_days` (paired with `limits_per_label_set`) based on actual query needs; longer retention increases cost.
2. **Configure Cardinality Limits**: Use `limits_per_label_set` per environment/team to prevent cardinality explosions from driving up ingestion cost.
3. **Design Efficient Recording Rules**: Precompute expensive PromQL aggregations to speed up dashboards and reduce ad-hoc query cost.
4. **Use Infrequent-Access Log Class**: For rarely queried logs, set `cloudwatch_log_group_class = "INFREQUENT_ACCESS"` to reduce CloudWatch cost.

### Alerting Best Practices

1. **Configure Alert Grouping**: Use `group_by` in the Alert Manager config to reduce notification noise.
2. **Implement Severity Routing**: Use severity labels (critical, warning, info) with distinct receivers/routes.
3. **Test Alert Rules Before Deploy**: Validate PromQL expressions and Alertmanager YAML (`amtool check-config`) before applying.

### Operational Excellence

1. **Enable CloudWatch Logging**: Explicitly set `logging_configuration` for audit trails and remote-write troubleshooting.
2. **Manage Everything as Code**: Keep workspace, rules, and Alert Manager config under Terraform to avoid console drift.
3. **Tag Comprehensively**: Apply consistent `Environment`, `Application`, and `Team` tags for cost allocation.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-prometheus
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/managed-service-prometheus/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-prometheus/tree/master/examples
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-prometheus/blob/master/CHANGELOG.md
- **AWS Managed Prometheus Documentation**: https://docs.aws.amazon.com/prometheus/latest/userguide/what-is-Amazon-Managed-Service-Prometheus.html
- **Alert Manager Configuration**: https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-alert-manager.html
- **Recording and Alerting Rules**: https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-rules.html
- **AMP Pricing**: https://aws.amazon.com/prometheus/pricing/
- **PromQL Documentation**: https://prometheus.io/docs/prometheus/latest/querying/basics/

## Notes for AI Agents

When using this module in automated workflows:

1. **Pin Version**: Use `version = "~> 4.3"`; v4.0.0 raised the minimum Terraform to `1.5.7` and AWS provider to `6.0` — a breaking change for older configurations.
2. **Set Retention Correctly**: To apply `retention_period_in_days`, always also pass `limits_per_label_set` (use `[]` if no cardinality limits are needed) — otherwise retention is silently ignored.
3. **Attach Logging Explicitly**: Set `logging_configuration = { create_log_group = true }` (or a `log_group_arn`) whenever workspace request logging is required; the default `null` does not attach logging to the workspace even though it still creates an orphaned log group.
4. **Know What Existing Workspaces Support**: With `create_workspace = false`, only `alert_manager_definition` and `rule_group_namespaces` apply — do not expect `retention_period_in_days`, `limits_per_label_set`, `logging_configuration`, or resource policies to take effect.
5. **Review the Default Resource Policy**: `create_resource_policy = true` (the default) grants the caller's account full read/write plus Grafana read-only automatically; set `resource_policy_statements` or `create_resource_policy = false` when that default is not desired.
6. **Enable Encryption for Production**: Specify `kms_key_arn` for workspace encryption and `cloudwatch_log_group_kms_key_id` for log encryption.
7. **Override the Alert Manager Default**: The built-in `alert_manager_definition` is a no-op receiver; supply real receivers (SNS topic ARNs, etc.) for production alerting.
8. **Tag Resources**: Apply comprehensive tags including Environment, Application, and Team.
9. **No Submodules**: This is a standalone flat module with no nested submodules.
