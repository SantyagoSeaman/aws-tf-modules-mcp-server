# Terraform AWS Managed Service for Prometheus Module

## Module Information

- **Module Name**: `managed-service-prometheus`
- **Source**: `terraform-aws-modules/managed-service-prometheus/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-prometheus
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/managed-service-prometheus/aws/latest
- **Latest Version**: 4.3.1
- **Purpose**: Terraform module that creates and manages AWS Managed Service for Prometheus (AMP) workspaces, alert managers, and rule groups for serverless Prometheus-compatible monitoring
- **Service**: AWS Managed Service for Prometheus (Amazon Managed Prometheus)
- **Category**: Monitoring, Observability, Container Management
- **Keywords**: prometheus, amp, monitoring, observability, metrics, kubernetes, eks, alertmanager, recording-rules, alerting-rules, rule-groups, workspace, promql, kms-encryption, high-availability
- **Use For**: Kubernetes cluster monitoring, container workload observability, EKS metrics collection, microservices performance monitoring, multi-cluster metric aggregation, application performance monitoring, alerting and notification systems, recording rule automation, long-term metrics retention

## Description

This Terraform module provides comprehensive management of AWS Managed Service for Prometheus (AMP) resources including workspaces, Alert Manager configurations, and rule group namespaces. The module simplifies the creation and configuration of serverless, Prometheus-compatible monitoring infrastructure for containerized applications and Kubernetes environments. It supports workspace creation with custom aliases, CloudWatch logging integration, KMS encryption for data at rest, configurable metric retention periods, per-label-set cardinality limits, and resource policies for cross-account access control.

AWS Managed Service for Prometheus is a fully managed, serverless monitoring service that provides automatic scaling for metric ingestion, storage, and querying of Prometheus metrics at scale. It eliminates the operational burden of managing Prometheus servers while maintaining full compatibility with the standard Prometheus data model and PromQL query language. The service is designed for container environments, particularly Amazon EKS and self-managed Kubernetes clusters, offering high availability through Multi-AZ deployments and secure integration with AWS security services.

The module enables teams to quickly establish production-grade Prometheus monitoring infrastructure with minimal configuration, supporting multiple rule group namespaces for organizing recording and alerting rules, customizable Alert Manager definitions for notification routing, and optional CloudWatch logging for workspace activity monitoring. Version 4.x introduced resource policies for fine-grained access control and per-label-set limits to prevent cardinality explosions.

## Key Features

- **Workspace Creation**: Automated creation of AMP workspaces with custom aliases for organization
- **Existing Workspace Integration**: Option to use existing workspaces by providing workspace ID
- **Alert Manager Configuration**: Declarative Alert Manager definitions for notification routing and receiver configuration
- **Rule Group Namespaces**: Support for multiple rule group namespaces containing recording and alerting rules
- **CloudWatch Logging**: Optional integration with CloudWatch Logs with automatic log group creation
- **KMS Encryption**: Support for customer-managed KMS keys for both workspace and log group encryption
- **Metric Retention**: Configurable retention period for stored metrics (up to 1095 days)
- **Cardinality Limits**: Per-label-set metric limits to prevent cardinality explosions and control costs
- **Resource Policies**: IAM resource policies for cross-account access and Grafana integration
- **Automatic Scaling**: Serverless architecture that automatically scales based on metric ingestion and query load
- **PromQL Compatibility**: Full support for standard Prometheus Query Language (PromQL)
- **Multi-AZ High Availability**: Built-in high availability with Multi-AZ deployments
- **Tagging Support**: Comprehensive resource tagging for organization and cost allocation
- **Conditional Creation**: Control resource creation with boolean flags

## Main Use Cases

1. **Kubernetes Cluster Monitoring**: Collect and analyze metrics from Amazon EKS or self-managed Kubernetes clusters
2. **Container Workload Observability**: Monitor containerized application performance and resource utilization
3. **Microservices Monitoring**: Track metrics across distributed microservices architectures
4. **Multi-Cluster Aggregation**: Centralize metrics from multiple Kubernetes clusters in different regions
5. **Application Performance Monitoring**: Monitor application-level metrics using Prometheus exporters
6. **Infrastructure Metrics Storage**: Long-term storage and analysis of infrastructure and system metrics
7. **Alerting and Notification**: Configure automated alerting based on metric thresholds and conditions
8. **Recording Rule Automation**: Precompute aggregations and expensive queries for improved query performance
9. **Cross-Account Monitoring**: Share metrics across AWS accounts using resource policies

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `tags` | `map(string)` | `{}` | Map of tags to add to all resources |
| `create_workspace` | `bool` | `true` | Create a new workspace or use existing |
| `workspace_id` | `string` | `""` | ID of existing workspace (when `create_workspace = false`) |
| `workspace_alias` | `string` | `null` | Alias for the Prometheus workspace |
| `logging_configuration` | `object` | `null` | Logging configuration with `create_log_group` and `log_group_arn` |
| `kms_key_arn` | `string` | `null` | ARN of KMS key for workspace encryption at rest |
| `retention_period_in_days` | `number` | `null` | Number of days to retain metric data |
| `limits_per_label_set` | `list(object)` | `null` | Cardinality limits per label set with `max_series` |
| `create_resource_policy` | `bool` | `true` | Whether to create resource policy for cross-account access |
| `resource_policy_statements` | `map(object)` | `null` | IAM policy statements for workspace access control |
| `cloudwatch_log_group_retention_in_days` | `number` | `30` | Days to retain CloudWatch logs |
| `cloudwatch_log_group_kms_key_id` | `string` | `null` | KMS Key for log group encryption |
| `create_alert_manager` | `bool` | `true` | Create Alert Manager definition |
| `alert_manager_definition` | `string` | Default config | Alert Manager configuration in YAML format |
| `rule_group_namespaces` | `map(object)` | `null` | Map of rule group namespace definitions with `name` and `data` |

## Main Outputs

| Output | Description |
|--------|-------------|
| `workspace_arn` | Amazon Resource Name (ARN) of the workspace |
| `workspace_id` | Identifier of the workspace |
| `workspace_prometheus_endpoint` | Prometheus endpoint available for this workspace |

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

  # Automatic log group creation
  logging_configuration = {
    create_log_group = true
    log_group_arn    = null
  }

  cloudwatch_log_group_retention_in_days = 14

  tags = {
    Environment = "production"
    Application = "monitoring"
  }
}
```

### Example 3: Complete Configuration with Retention and Cardinality Limits

```hcl
module "prometheus" {
  source  = "terraform-aws-modules/managed-service-prometheus/aws"
  version = "~> 4.3"

  workspace_alias = "eks-monitoring"

  # Metric retention
  retention_period_in_days = 60

  # Cardinality limits per environment
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

  # CloudWatch logging
  logging_configuration = {
    create_log_group = true
    log_group_arn    = null
  }

  tags = {
    Environment = "production"
    Application = "eks-monitoring"
  }
}
```

### Example 4: Configuration with Alert Manager and Rule Groups

```hcl
module "prometheus" {
  source  = "terraform-aws-modules/managed-service-prometheus/aws"
  version = "~> 4.3"

  workspace_alias = "eks-monitoring"

  # Alert Manager configuration
  create_alert_manager = true
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

  # Rule group namespaces
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

### Example 5: Cross-Account Access with Resource Policy

```hcl
module "prometheus" {
  source  = "terraform-aws-modules/managed-service-prometheus/aws"
  version = "~> 4.3"

  workspace_alias = "shared-metrics"

  # Resource policy for cross-account access
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

### Example 6: Using Existing Workspace

```hcl
module "prometheus_rules" {
  source  = "terraform-aws-modules/managed-service-prometheus/aws"
  version = "~> 4.3"

  create_workspace = false
  workspace_id     = "ws-12345678-1234-1234-1234-123456789012"

  # Add rule groups to existing workspace
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

### Example 7: KMS Encrypted Workspace

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

  # Encrypted CloudWatch logs
  logging_configuration = {
    create_log_group = true
    log_group_arn    = null
  }
  cloudwatch_log_group_kms_key_id = aws_kms_key.prometheus.arn

  tags = {
    Environment = "production"
    Encrypted   = "true"
  }
}
```

## Best Practices

### Security and Access Control

1. **Enable KMS Encryption**: Use customer-managed KMS keys for encrypting metrics at rest to maintain control over encryption keys and meet compliance requirements.
2. **Implement IAM Least Privilege**: Grant IAM principals only the minimum required permissions for remote write, query, and management operations.
3. **Use VPC Endpoints**: Deploy VPC endpoints for AMP to keep metric traffic within AWS network.
4. **Configure Resource Policies**: Use `resource_policy_statements` for fine-grained cross-account access control.
5. **Encrypt CloudWatch Logs**: Set `cloudwatch_log_group_kms_key_id` to encrypt workspace logs.

### Configuration and Management

1. **Use Descriptive Workspace Aliases**: Apply meaningful aliases indicating environment, purpose, and team ownership.
2. **Organize Rule Groups Logically**: Separate recording rules and alerting rules into different namespaces.
3. **Tag Comprehensively**: Apply consistent tags including Environment, Application, Team, and CostCenter.
4. **Version Control Configurations**: Store Alert Manager definitions and rule group configurations in version control.
5. **Pin Module Version**: Use version constraints like `version = "~> 4.3"` for stability.

### Performance and Cost Optimization

1. **Set Appropriate Retention**: Configure `retention_period_in_days` based on actual needs; longer retention increases costs.
2. **Configure Cardinality Limits**: Use `limits_per_label_set` to prevent cardinality explosions and control costs.
3. **Design Efficient Recording Rules**: Precompute expensive queries to improve dashboard performance and reduce query costs.
4. **Monitor Ingestion Volume**: Track metric ingestion rate and active series count to identify cost drivers.

### Alerting Best Practices

1. **Configure Alert Grouping**: Use `group_by` in Alert Manager to reduce notification noise.
2. **Implement Severity Levels**: Use severity labels (critical, warning, info) to route alerts appropriately.
3. **Test Alert Rules**: Validate PromQL expressions and Alert Manager configurations before production deployment.
4. **Document Alert Runbooks**: Include clear annotations explaining conditions and remediation steps.

### Operational Excellence

1. **Enable CloudWatch Logging**: Configure logging for audit trails and troubleshooting.
2. **Use Infrastructure as Code**: Manage all AMP resources through Terraform for consistency.
3. **Regular Rule Review**: Periodically review alerting and recording rules for relevance.
4. **Leverage Multi-AZ**: Take advantage of built-in Multi-AZ deployment for high availability.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-prometheus
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/managed-service-prometheus/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-prometheus/tree/master/examples
- **AWS Managed Prometheus Documentation**: https://docs.aws.amazon.com/prometheus/latest/userguide/what-is-Amazon-Managed-Service-Prometheus.html
- **Alert Manager Configuration**: https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-alertmanager.html
- **Recording and Alerting Rules**: https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-rules.html
- **AMP Pricing**: https://aws.amazon.com/prometheus/pricing/
- **PromQL Documentation**: https://prometheus.io/docs/prometheus/latest/querying/basics/

## Notes for AI Agents

When using this module in automated workflows:

1. **Use Descriptive Aliases**: Always provide meaningful `workspace_alias` values for easy identification
2. **Enable Encryption**: Specify `kms_key_arn` for production workspaces to encrypt metrics at rest
3. **Configure Logging**: Set up CloudWatch logging with `logging_configuration` for audit and troubleshooting
4. **Set Cardinality Limits**: Use `limits_per_label_set` to prevent runaway costs from high-cardinality metrics
5. **Configure Retention**: Set `retention_period_in_days` based on compliance and cost requirements
6. **Tag Resources**: Apply comprehensive tags including Environment, Application, Team, and Owner
7. **Organize Rule Groups**: Use separate rule group namespaces for recording rules and alerting rules
8. **Test Configurations**: Validate PromQL expressions and Alert Manager YAML before deployment
9. **Pin Version**: Use `version = "~> 4.3"` to avoid unexpected breaking changes
10. **Cross-Account Access**: Use `resource_policy_statements` for sharing metrics across accounts
11. **Grafana Integration**: Resource policies support automatic IAM permissions for Grafana service principals
12. **No Submodules**: This is a standalone module without nested submodules
