# Terraform AWS Managed Service for Prometheus Module

## Module Information

- **Module Name**: `managed-service-prometheus`
- **Source**: `terraform-aws-modules/managed-service-prometheus/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-prometheus
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/managed-service-prometheus/aws/latest
- **Latest Version**: 3.1.0
- **Purpose**: Terraform module that creates and manages AWS Managed Service for Prometheus (AMP) workspaces, alert managers, and rule groups for serverless Prometheus-compatible monitoring
- **Service**: AWS Managed Service for Prometheus (Amazon Managed Prometheus)
- **Category**: Monitoring, Observability, Container Management
- **Keywords**: prometheus, amp, amazon-managed-service-prometheus, monitoring, observability, metrics, container-monitoring, kubernetes, eks, time-series, promql, alertmanager, recording-rules, alerting-rules, rule-groups, workspace, serverless-monitoring, cloudwatch, kms-encryption, multi-az, high-availability, scalability, prometheus-compatible, metric-ingestion, metric-storage, prometheus-endpoint
- **Use For**: Kubernetes cluster monitoring, container workload observability, EKS metrics collection and analysis, microservices performance monitoring, multi-cluster metric aggregation, application performance monitoring, infrastructure metrics storage, alerting and notification systems, recording rule automation, long-term metrics retention, cloud-native application monitoring, serverless Prometheus deployment

## Description

This Terraform module provides comprehensive management of AWS Managed Service for Prometheus (AMP) resources including workspaces, Alert Manager configurations, and rule group namespaces. The module simplifies the creation and configuration of serverless, Prometheus-compatible monitoring infrastructure for containerized applications and Kubernetes environments. It supports workspace creation with custom aliases, CloudWatch logging integration, KMS encryption for data at rest, and flexible configuration of Alert Manager definitions and Prometheus recording and alerting rules.

AWS Managed Service for Prometheus is a fully managed, serverless monitoring service that provides automatic scaling for metric ingestion, storage, and querying of Prometheus metrics at scale. It eliminates the operational burden of managing Prometheus servers while maintaining full compatibility with the standard Prometheus data model and PromQL query language. The service is designed for container environments, particularly Amazon EKS and self-managed Kubernetes clusters, offering high availability through Multi-AZ deployments, secure integration with AWS security services, and flexible metric retention (150 days by default, configurable up to 1095 days).

The module enables teams to quickly establish production-grade Prometheus monitoring infrastructure with minimal configuration, supporting multiple rule group namespaces for organizing recording and alerting rules, customizable Alert Manager definitions for notification routing, and optional CloudWatch logging for workspace activity monitoring. It integrates seamlessly with existing Prometheus tooling and exporters, making it ideal for organizations migrating from self-managed Prometheus deployments or building new cloud-native observability platforms on AWS.

## Key Features

- **Workspace Creation**: Automated creation of AMP workspaces with custom aliases for organization
- **Existing Workspace Integration**: Option to use existing workspaces by providing workspace ID
- **Alert Manager Configuration**: Declarative Alert Manager definitions for notification routing and receiver configuration
- **Optional Alert Manager**: Ability to disable Alert Manager creation when not needed
- **Rule Group Namespaces**: Support for multiple rule group namespaces containing recording and alerting rules
- **Prometheus Recording Rules**: Define recording rules to precompute frequently used or expensive queries
- **Prometheus Alerting Rules**: Configure alerting rules with conditions and thresholds
- **CloudWatch Logging**: Optional integration with CloudWatch Logs for workspace activity monitoring
- **KMS Encryption**: Support for customer-managed KMS keys for encryption at rest
- **Automatic Scaling**: Serverless architecture that automatically scales based on metric ingestion and query load
- **PromQL Compatibility**: Full support for standard Prometheus Query Language (PromQL)
- **Multi-AZ High Availability**: Built-in high availability with Multi-AZ deployments
- **Long-term Retention**: Configurable metric retention up to 1095 days (3 years)
- **Tagging Support**: Comprehensive resource tagging for organization and cost allocation
- **Conditional Creation**: Control resource creation with boolean flags
- **Prometheus Endpoint**: Provides Prometheus remote write and query endpoints
- **AWS Security Integration**: Native integration with AWS IAM, VPC, and security services

## Main Use Cases

1. **Kubernetes Cluster Monitoring**: Collect and analyze metrics from Amazon EKS or self-managed Kubernetes clusters
2. **Container Workload Observability**: Monitor containerized application performance and resource utilization
3. **Microservices Monitoring**: Track metrics across distributed microservices architectures
4. **Multi-Cluster Aggregation**: Centralize metrics from multiple Kubernetes clusters in different regions
5. **Application Performance Monitoring**: Monitor application-level metrics using Prometheus exporters
6. **Infrastructure Metrics Storage**: Long-term storage and analysis of infrastructure and system metrics
7. **Alerting and Notification**: Configure automated alerting based on metric thresholds and conditions
8. **Cloud-Native Observability**: Build comprehensive observability platforms for cloud-native applications
9. **Recording Rule Automation**: Precompute aggregations and expensive queries for improved query performance
10. **Prometheus Migration**: Migrate from self-managed Prometheus to fully managed service

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `tags` | `map(string)` | `{}` | Map of tags to add to all resources |
| `create_workspace` | `bool` | `true` | Create a new workspace or use existing |
| `workspace_id` | `string` | `null` | ID of existing workspace (when `create_workspace = false`) |
| `workspace_alias` | `string` | `null` | Alias for the Prometheus workspace |
| `logging_configuration` | `map(any)` | `{}` | Logging configuration for the workspace |
| `kms_key_arn` | `string` | `null` | ARN of KMS key for encryption at rest |
| `create_alert_manager` | `bool` | `true` | Create Alert Manager definition |
| `alert_manager_definition` | `string` | Default config | Alert Manager configuration in YAML format |
| `rule_group_namespaces` | `map(any)` | `{}` | Map of rule group namespace definitions |

## Main Outputs

| Output | Description |
|--------|-------------|
| `workspace_arn` | Amazon Resource Name (ARN) of the workspace |
| `workspace_id` | Identifier of the workspace |
| `workspace_prometheus_endpoint` | Prometheus endpoint available for this workspace |

## Usage Examples

### Example 1: Basic Workspace

```hcl
module "prometheus_basic" {
  source = "terraform-aws-modules/managed-service-prometheus/aws"

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
# Create CloudWatch Log Group
resource "aws_cloudwatch_log_group" "prometheus" {
  name              = "/aws/prometheus/workspace"
  retention_in_days = 7

  tags = {
    Name        = "prometheus-workspace-logs"
    Environment = "production"
  }
}

# Create Prometheus workspace with logging
module "prometheus_with_logging" {
  source = "terraform-aws-modules/managed-service-prometheus/aws"

  workspace_alias = "production-metrics"

  logging_configuration = {
    log_group_arn = "${aws_cloudwatch_log_group.prometheus.arn}:*"
  }

  tags = {
    Environment = "production"
    Application = "monitoring"
  }
}
```

### Example 3: Workspace with KMS Encryption

```hcl
# Create KMS key for Prometheus encryption
resource "aws_kms_key" "prometheus" {
  description             = "KMS key for Prometheus workspace encryption"
  deletion_window_in_days = 10

  tags = {
    Name = "prometheus-workspace-key"
  }
}

resource "aws_kms_alias" "prometheus" {
  name          = "alias/prometheus-workspace"
  target_key_id = aws_kms_key.prometheus.key_id
}

# Create encrypted Prometheus workspace
module "prometheus_encrypted" {
  source = "terraform-aws-modules/managed-service-prometheus/aws"

  workspace_alias = "encrypted-metrics"
  kms_key_arn     = aws_kms_key.prometheus.arn

  tags = {
    Environment = "production"
    Encrypted   = "true"
  }
}
```

### Example 4: Complete Configuration with Alert Manager and Rule Groups

```hcl
module "prometheus_complete" {
  source = "terraform-aws-modules/managed-service-prometheus/aws"

  workspace_alias = "eks-monitoring"

  # CloudWatch logging
  logging_configuration = {
    log_group_arn = "${aws_cloudwatch_log_group.prometheus.arn}:*"
  }

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
        - receiver: 'warning'
          match:
            severity: 'warning'
    receivers:
      - name: 'default'
        sns_configs:
          - topic_arn: 'arn:aws:sns:us-east-1:123456789012:prometheus-default'
      - name: 'critical'
        sns_configs:
          - topic_arn: 'arn:aws:sns:us-east-1:123456789012:prometheus-critical'
      - name: 'warning'
        sns_configs:
          - topic_arn: 'arn:aws:sns:us-east-1:123456789012:prometheus-warning'
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
            - record: pod:cpu_usage:rate5m
              expr: sum(rate(container_cpu_usage_seconds_total{image!=""}[5m])) by (pod, namespace)
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

            - alert: CriticalCPUUsage
              expr: cluster:cpu_usage:rate5m > 0.95
              for: 2m
              labels:
                severity: critical
              annotations:
                summary: "Critical CPU usage detected"
                description: "Cluster {{ $labels.cluster }} CPU usage is above 95%"

            - alert: PodMemoryPressure
              expr: |
                sum(container_memory_working_set_bytes{image!=""}) by (pod, namespace)
                /
                sum(container_spec_memory_limit_bytes{image!=""}) by (pod, namespace) > 0.9
              for: 5m
              labels:
                severity: warning
              annotations:
                summary: "Pod memory pressure"
                description: "Pod {{ $labels.namespace }}/{{ $labels.pod }} memory usage is above 90%"
      EOT
    }
  }

  tags = {
    Environment = "production"
    Application = "eks-monitoring"
    ManagedBy   = "Terraform"
  }
}
```

### Example 5: Using Existing Workspace

```hcl
# Reference existing workspace
data "aws_prometheus_workspace" "existing" {
  workspace_id = "ws-12345678-1234-1234-1234-123456789012"
}

# Add rule groups to existing workspace
module "prometheus_rules_only" {
  source = "terraform-aws-modules/managed-service-prometheus/aws"

  create_workspace = false
  workspace_id     = data.aws_prometheus_workspace.existing.workspace_id

  # Add new rule groups to existing workspace
  rule_group_namespaces = {
    custom_metrics = {
      name = "application-metrics"
      data = <<-EOT
      groups:
        - name: application_recording
          rules:
            - record: app:request_duration:p95
              expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
            - record: app:error_rate:rate5m
              expr: sum(rate(http_requests_total{status=~"5.."}[5m])) by (service) / sum(rate(http_requests_total[5m])) by (service)
      EOT
    }
  }

  tags = {
    Environment = "production"
    Type        = "custom-rules"
  }
}
```

### Example 6: Workspace Without Alert Manager

```hcl
module "prometheus_no_alertmanager" {
  source = "terraform-aws-modules/managed-service-prometheus/aws"

  workspace_alias = "metrics-storage-only"

  # Disable Alert Manager
  create_alert_manager = false

  # Only define recording rules (no alerts)
  rule_group_namespaces = {
    aggregations = {
      name = "metric-aggregations"
      data = <<-EOT
      groups:
        - name: daily_aggregations
          interval: 1h
          rules:
            - record: daily:requests:sum
              expr: sum(increase(http_requests_total[24h]))
            - record: daily:errors:sum
              expr: sum(increase(http_requests_total{status=~"5.."}[24h]))
      EOT
    }
  }

  tags = {
    Environment = "analytics"
    Purpose     = "long-term-storage"
  }
}
```

### Example 7: Multi-Region Monitoring Setup

```hcl
# Primary region workspace
module "prometheus_us_east" {
  source = "terraform-aws-modules/managed-service-prometheus/aws"

  providers = {
    aws = aws.us_east_1
  }

  workspace_alias = "production-us-east-1"

  logging_configuration = {
    log_group_arn = "${aws_cloudwatch_log_group.prometheus_us_east.arn}:*"
  }

  create_alert_manager = true
  alert_manager_definition = file("${path.module}/alertmanager-config.yaml")

  rule_group_namespaces = {
    common_rules = {
      name = "common-recording-rules"
      data = file("${path.module}/recording-rules.yaml")
    }
  }

  tags = {
    Environment = "production"
    Region      = "us-east-1"
  }
}

# Secondary region workspace
module "prometheus_eu_west" {
  source = "terraform-aws-modules/managed-service-prometheus/aws"

  providers = {
    aws = aws.eu_west_1
  }

  workspace_alias = "production-eu-west-1"

  logging_configuration = {
    log_group_arn = "${aws_cloudwatch_log_group.prometheus_eu_west.arn}:*"
  }

  create_alert_manager = true
  alert_manager_definition = file("${path.module}/alertmanager-config.yaml")

  rule_group_namespaces = {
    common_rules = {
      name = "common-recording-rules"
      data = file("${path.module}/recording-rules.yaml")
    }
  }

  tags = {
    Environment = "production"
    Region      = "eu-west-1"
  }
}
```

### Example 8: Conditional Workspace Creation

```hcl
variable "create_prometheus" {
  description = "Whether to create Prometheus workspace"
  type        = bool
  default     = true
}

variable "environment" {
  description = "Environment name"
  type        = string
}

module "prometheus_conditional" {
  source = "terraform-aws-modules/managed-service-prometheus/aws"

  create = var.create_prometheus

  workspace_alias = "${var.environment}-monitoring"

  create_alert_manager = var.environment == "production" ? true : false

  alert_manager_definition = var.environment == "production" ? <<-EOT
  alertmanager_config: |
    route:
      receiver: 'production-alerts'
    receivers:
      - name: 'production-alerts'
        sns_configs:
          - topic_arn: 'arn:aws:sns:us-east-1:123456789012:prod-alerts'
  EOT : ""

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
```

## Best Practices

### Security and Access Control

1. **Enable KMS Encryption**: Use customer-managed KMS keys for encrypting metrics at rest to maintain control over encryption keys and meet compliance requirements.
2. **Implement IAM Least Privilege**: Grant IAM principals only the minimum required permissions for remote write, query, and management operations using resource-specific policies.
3. **Use VPC Endpoints**: Deploy VPC endpoints for AMP to keep metric traffic within AWS network and avoid exposure to the public internet.
4. **Enable CloudTrail Logging**: Monitor all AMP API calls through CloudTrail for audit trails and security analysis.
5. **Secure Alert Manager Receivers**: Use encrypted channels (SNS with encryption, HTTPS webhooks) for alert notifications to protect sensitive alert data.
6. **Rotate Access Credentials**: Regularly rotate IAM access keys and credentials used for Prometheus remote write and query operations.
7. **Implement Network Security**: Use security groups and network ACLs to restrict access to services sending metrics to AMP workspaces.

### Configuration and Management

1. **Use Descriptive Workspace Aliases**: Apply meaningful aliases that indicate environment, purpose, and team ownership for easy identification.
2. **Organize Rule Groups Logically**: Separate recording rules and alerting rules into different namespaces for better organization and maintenance.
3. **Tag Comprehensively**: Apply consistent tags including Environment, Application, Team, and CostCenter for resource tracking and cost allocation.
4. **Version Control Configurations**: Store Alert Manager definitions and rule group configurations in version control systems for change tracking.
5. **Document Rule Intent**: Add clear annotations to alerting rules explaining the condition, impact, and remediation steps.
6. **Use External Files**: Store complex Alert Manager and rule group configurations in separate YAML files using `file()` function for better readability.

### Performance and Optimization

1. **Design Efficient Recording Rules**: Create recording rules for frequently used or expensive queries to precompute results and improve query performance.
2. **Set Appropriate Intervals**: Configure rule evaluation intervals based on metric update frequency to balance timeliness and resource consumption.
3. **Optimize PromQL Queries**: Write efficient PromQL queries in recording and alerting rules to minimize evaluation time and resource usage.
4. **Use Aggregation**: Aggregate metrics at collection time when possible to reduce storage requirements and improve query performance.
5. **Monitor Ingestion Metrics**: Track metric ingestion rate and active series count to plan capacity and identify inefficient instrumentation.
6. **Implement Metric Relabeling**: Use relabeling rules in Prometheus scrape configurations to drop unnecessary labels and reduce cardinality.

### Alerting and Notifications

1. **Configure Alert Grouping**: Use `group_by` in Alert Manager to group related alerts and reduce notification noise.
2. **Set Appropriate Thresholds**: Define alert thresholds based on baseline performance data and acceptable deviation ranges.
3. **Implement Alert Severity Levels**: Use severity labels (critical, warning, info) to route alerts to appropriate receivers and response teams.
4. **Configure Repeat Intervals**: Set reasonable `repeat_interval` values to avoid alert fatigue while ensuring persistent issues remain visible.
5. **Use Alert Inhibition**: Configure inhibition rules to suppress redundant alerts when higher-priority alerts are already firing.
6. **Test Alert Rules**: Regularly test alerting rules in non-production environments before deploying to production.

### Cost Optimization

1. **Monitor Ingestion Costs**: Track metric ingestion volume and active time series to identify cost drivers and optimize instrumentation.
2. **Use Recording Rules**: Precompute expensive aggregations with recording rules to reduce query costs and improve dashboard performance.
3. **Implement Metric Filtering**: Filter out unnecessary metrics at scrape time to reduce ingestion and storage costs.
4. **Optimize Retention**: Use the default 150-day retention unless longer retention is required; avoid maximum retention unless necessary.
5. **Consolidate Workspaces**: Consider consolidating multiple small workspaces into fewer larger workspaces to simplify management and potentially reduce costs.
6. **Review Active Series**: Regularly audit active time series to identify and eliminate high-cardinality metrics from inefficient instrumentation.

### Operational Excellence

1. **Enable CloudWatch Logging**: Configure CloudWatch logging for workspace activity to track configuration changes and troubleshoot issues.
2. **Implement Monitoring for Monitoring**: Set up alerts for AMP workspace health, ingestion failures, and query performance.
3. **Document Alert Runbooks**: Create and maintain runbooks for each alert with investigation steps and remediation procedures.
4. **Use Infrastructure as Code**: Manage all AMP resources through Terraform to ensure consistency and enable version control.
5. **Implement Change Management**: Test rule group and Alert Manager changes in non-production workspaces before applying to production.
6. **Regular Rule Review**: Periodically review and update alerting and recording rules to ensure they remain relevant and effective.
7. **Plan for Scalability**: Design metric collection and rule evaluation strategies that scale with growing infrastructure and metric volume.

### High Availability and Disaster Recovery

1. **Leverage Multi-AZ**: Take advantage of built-in Multi-AZ deployment for high availability without additional configuration.
2. **Deploy Multi-Region**: For critical workloads, deploy AMP workspaces in multiple regions and configure application-level failover.
3. **Backup Configurations**: Export and version control Alert Manager definitions and rule groups for disaster recovery.
4. **Test Failover Scenarios**: Regularly test metric collection failover by simulating workspace unavailability.
5. **Document Recovery Procedures**: Maintain clear documentation for workspace recreation and configuration restoration procedures.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-prometheus
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/managed-service-prometheus/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-managed-service-prometheus/tree/master/examples
- **AWS Managed Prometheus Documentation**: https://docs.aws.amazon.com/prometheus/latest/userguide/what-is-Amazon-Managed-Service-Prometheus.html
- **Getting Started with AMP**: https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-getting-started.html
- **Alert Manager Configuration**: https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-alertmanager.html
- **Recording and Alerting Rules**: https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-rules.html
- **AMP Pricing**: https://aws.amazon.com/prometheus/pricing/
- **PromQL Documentation**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Prometheus Best Practices**: https://prometheus.io/docs/practices/naming/
- **AWS Security Best Practices**: https://docs.aws.amazon.com/prometheus/latest/userguide/security-best-practices.html
- **Monitoring AMP with CloudWatch**: https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-monitoring-cloudwatch.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Use Descriptive Aliases**: Always provide meaningful `workspace_alias` values for easy identification and management
2. **Enable Encryption**: Specify `kms_key_arn` for production workspaces to encrypt metrics at rest
3. **Configure Logging**: Set up CloudWatch logging with `logging_configuration` for audit and troubleshooting
4. **Organize Rule Groups**: Use separate rule group namespaces for recording rules and alerting rules
5. **Tag Resources**: Apply comprehensive tags including Environment, Application, Team, and Owner
6. **Version Control Rules**: Store Alert Manager and rule group configurations in version control
7. **Test Configurations**: Validate PromQL expressions and Alert Manager configurations before deployment
8. **Monitor Costs**: Track metric ingestion volume and active series to manage costs effectively
9. **Implement IAM Policies**: Create least-privilege IAM policies for remote write and query access
10. **Use Recording Rules**: Define recording rules for frequently used queries to improve performance
11. **Configure Alert Routing**: Set up appropriate Alert Manager routes and receivers for different severity levels
12. **Document Alerts**: Include clear annotations in alerting rules explaining conditions and remediation
13. **Plan for Scale**: Design metric collection and aggregation strategies that scale with infrastructure growth
14. **Enable Multi-AZ**: Leverage built-in Multi-AZ high availability for production workspaces
15. **Regular Reviews**: Periodically review and update alerting rules and recording rules for relevance
