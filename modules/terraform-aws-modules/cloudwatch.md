# Terraform AWS CloudWatch Module

## Module Information

- **Module Name**: `cloudwatch`
- **Source**: `terraform-aws-modules/cloudwatch/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-cloudwatch
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest
- **Latest Version**: 5.7.1
- **Purpose**: Terraform module that creates and manages AWS CloudWatch resources including log groups, metric alarms, metric filters, and advanced monitoring capabilities
- **Service**: AWS CloudWatch (Monitoring and Observability)
- **Category**: Monitoring, Observability, Logging, Security
- **Keywords**: cloudwatch, monitoring, metrics, alarms, logs, log-groups, log-streams, metric-filters, metric-alarms, composite-alarms, cis-benchmark, security-monitoring, observability, dashboards, log-analytics, metric-stream, anomaly-detection, log-subscription, kinesis, firehose, lambda, sns, cloudtrail, application-monitoring, infrastructure-monitoring, performance-monitoring, resource-monitoring, threshold-alarms, log-retention, kms-encryption, log-data-protection, query-definition, log-insights, metric-math, alarm-actions, sns-notifications, email-alerts, pagerduty, opsgenie, datadog, splunk, elasticsearch, time-series, aggregation, statistics, percentiles, cloudwatch-agent, container-insights, lambda-insights, application-insights, synthetics, service-lens, x-ray, distributed-tracing
- **Use For**: Application performance monitoring, infrastructure health tracking, log aggregation and analysis, security event detection, compliance monitoring, cost optimization through metrics, automated incident response, real-time alerting and notifications, anomaly detection, trend analysis, capacity planning, SLA monitoring

## Description

This comprehensive Terraform module provides a complete solution for managing AWS CloudWatch resources, enabling organizations to implement robust monitoring, logging, and observability capabilities across their AWS infrastructure. The module supports the full spectrum of CloudWatch functionality through 13 specialized submodules, each designed to handle specific monitoring and logging requirements. From basic log group creation to advanced composite alarms and CIS security benchmark implementation, this module provides the building blocks for enterprise-grade observability solutions.

The module excels at managing CloudWatch Log Groups for centralized log storage with configurable retention policies and KMS encryption, creating sophisticated metric alarms with customizable thresholds and actions, implementing log metric filters to extract custom metrics from log data, and establishing metric streams for real-time data export to external monitoring platforms. It also provides specialized capabilities for security monitoring through CIS AWS Foundations Controls implementation, protecting sensitive data through log data protection policies, and detecting anomalies in log patterns using machine learning-based anomaly detectors.

Key architectural advantages include modular design allowing selective use of only required components, comprehensive tagging support for resource organization and cost allocation, flexible integration with SNS topics for multi-channel alerting, and support for modern monitoring patterns such as composite alarms for complex conditions and metric streams for hybrid cloud observability. The module follows AWS best practices for monitoring and logging, making it suitable for regulated industries requiring compliance with standards like HIPAA, PCI-DSS, and SOC2.

## Key Features

- **13 Specialized Submodules**: Comprehensive coverage of CloudWatch capabilities through dedicated submodules for each resource type
- **Log Group Management**: Create and manage CloudWatch log groups with configurable retention periods and encryption
- **Metric Alarms**: Set up metric-based alarms with customizable thresholds, evaluation periods, and comparison operators
- **Log Metric Filters**: Extract custom metrics from log events using filter patterns for enhanced observability
- **Composite Alarms**: Create complex alarm conditions by combining multiple individual alarm states
- **CIS Security Benchmarks**: Pre-configured metric filters and alarms for AWS CIS Foundations security controls
- **Log Data Protection**: Implement data masking and protection policies for sensitive information in logs
- **Log Subscription Filters**: Stream logs in real-time to Lambda, Kinesis, or other AWS services for processing
- **Metric Streams**: Export CloudWatch metrics to external destinations like Datadog, Splunk, or New Relic
- **Query Definitions**: Define reusable CloudWatch Logs Insights queries for standardized log analysis
- **Log Anomaly Detection**: Automatically detect unusual patterns in log data using machine learning
- **Log Account Policies**: Manage account-level log policies for centralized governance
- **KMS Encryption Support**: Encrypt log data at rest using AWS KMS keys for enhanced security
- **Log Classes**: Support for STANDARD and INFREQUENT_ACCESS log classes for cost optimization
- **Flexible Retention**: Configure log retention from 1 day to indefinite retention based on requirements
- **SNS Integration**: Connect alarms to SNS topics for email, SMS, or webhook notifications
- **Multiple Dimensions**: Create similar alarms with different dimension values for resource families
- **Alarm Actions**: Configure actions for OK, ALARM, and INSUFFICIENT_DATA states
- **Metric Math**: Support for complex metric calculations and transformations in alarms
- **Cross-Account Logging**: Enable log aggregation across multiple AWS accounts
- **Resource Tagging**: Comprehensive tagging support for all CloudWatch resources
- **Conditional Creation**: Use create flags to conditionally manage resources
- **Output Format Flexibility**: Support for JSON and OpenTelemetry metric stream formats
- **Actions Suppressor**: Temporarily suppress alarm actions during maintenance windows

## Main Use Cases

1. **Application Performance Monitoring**: Track application metrics, response times, error rates, and throughput for performance optimization
2. **Infrastructure Health Tracking**: Monitor EC2 instances, containers, Lambda functions, and other AWS services for operational health
3. **Security Event Detection**: Implement CIS security controls to detect unauthorized access, policy changes, and security violations
4. **Log Aggregation and Analysis**: Centralize logs from multiple sources for troubleshooting and forensic analysis
5. **Cost Optimization Monitoring**: Track resource utilization metrics to identify over-provisioned resources and reduce costs
6. **Automated Incident Response**: Trigger automated remediation actions through Lambda functions when alarms fire
7. **Compliance Auditing**: Maintain audit logs with appropriate retention periods for regulatory compliance requirements
8. **Real-Time Alerting**: Send immediate notifications to operations teams via SNS, PagerDuty, or Opsgenie when issues occur
9. **Capacity Planning**: Analyze historical metrics and trends to forecast future resource requirements
10. **SLA Monitoring**: Track service level indicators and create alarms when SLAs are at risk of breach
11. **Anomaly Detection**: Automatically identify unusual patterns in logs or metrics that may indicate problems
12. **Hybrid Cloud Observability**: Stream metrics to external platforms for unified monitoring across cloud providers

## Submodules

### 1. log-group

- **Purpose**: Creates and manages CloudWatch log groups for centralized log storage
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-group
- **Key Features**: KMS encryption support, configurable retention periods, log class configuration (STANDARD/INFREQUENT_ACCESS), skip_destroy option
- **Use Cases**: Application logging, AWS service logs, audit trails, debugging

### 2. log-stream

- **Purpose**: Creates log streams within CloudWatch log groups for organizing log events
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-stream`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-stream
- **Key Features**: Automatic log stream creation, integration with log groups, resource tagging
- **Use Cases**: Segregating logs by instance, container log organization, application component logging

### 3. log-metric-filter

- **Purpose**: Creates metric filters to extract custom metrics from log events
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-metric-filter`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-metric-filter
- **Key Features**: Pattern-based metric extraction, custom metric transformations, dimension support, default values
- **Use Cases**: Error rate tracking, custom business metrics, log-based KPIs, pattern matching alerts

### 4. metric-alarm

- **Purpose**: Creates CloudWatch metric alarms for monitoring and alerting on AWS metrics
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/metric-alarm`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/metric-alarm
- **Key Features**: Multiple comparison operators, configurable thresholds, SNS integration, metric math support
- **Use Cases**: CPU utilization alerts, disk space monitoring, error rate alarms, latency tracking

### 5. metric-alarms-by-multiple-dimensions

- **Purpose**: Creates multiple similar alarms with different dimension values efficiently
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/metric-alarms-by-multiple-dimensions`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/metric-alarms-by-multiple-dimensions
- **Key Features**: Bulk alarm creation, dimension templating, consistent alarm configuration
- **Use Cases**: Fleet-wide monitoring, multi-instance alarms, auto-scaling group monitoring

### 6. cis-alarms

- **Purpose**: Implements CloudWatch metric filters and alarms for AWS CIS Foundations security benchmarks
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/cis-alarms`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/cis-alarms
- **Key Features**: Pre-configured CIS controls, selectively disable controls, automated security monitoring, compliance reporting
- **Use Cases**: Security compliance monitoring, unauthorized access detection, policy change tracking, root account usage alerts

### 7. log-data-protection

- **Purpose**: Implements data protection policies to mask or block sensitive information in logs
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-data-protection`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-data-protection
- **Key Features**: PII detection and masking, custom data identifiers, audit findings
- **Use Cases**: GDPR compliance, PCI-DSS log protection, sensitive data masking, privacy compliance

### 8. log-subscription-filter

- **Purpose**: Streams CloudWatch logs to other AWS services for real-time processing
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-subscription-filter`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-subscription-filter
- **Key Features**: Lambda integration, Kinesis streaming, filter patterns, cross-account subscriptions
- **Use Cases**: Real-time log processing, log forwarding to SIEM, centralized logging, log transformation

### 9. metric-stream

- **Purpose**: Exports CloudWatch metrics to external monitoring platforms in near real-time
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/metric-stream`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/metric-stream
- **Key Features**: Kinesis Firehose integration, JSON and OpenTelemetry formats, namespace filtering, metric include/exclude
- **Use Cases**: Hybrid cloud monitoring, third-party tool integration, unified observability, metric data lake

### 10. query-definition

- **Purpose**: Creates reusable CloudWatch Logs Insights query definitions
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/query-definition`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/query-definition
- **Key Features**: Pre-defined queries, multi-log-group queries, query sharing
- **Use Cases**: Standardized troubleshooting queries, team query sharing, common log analysis patterns

### 11. composite-alarm

- **Purpose**: Creates composite alarms that combine multiple alarm states using logical operators
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/composite-alarm`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/composite-alarm
- **Key Features**: AND/OR/NOT logic, alarm suppressor, complex conditions, reduced alarm fatigue
- **Use Cases**: Multi-signal alerting, correlated failures, service health checks, complex monitoring scenarios

### 12. log-account-policy

- **Purpose**: Manages account-level CloudWatch Logs policies for centralized governance
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-account-policy`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-account-policy
- **Key Features**: Account-wide policy enforcement, data protection policies, subscription filter policies
- **Use Cases**: Organization-wide log compliance, centralized data protection, standardized log handling

### 13. log-anomaly-detector

- **Purpose**: Detects anomalous patterns in CloudWatch Logs using machine learning
- **Source**: `terraform-aws-modules/cloudwatch/aws//modules/log-anomaly-detector`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest/submodules/log-anomaly-detector
- **Key Features**: Machine learning-based detection, automatic baseline learning, anomaly scoring
- **Use Cases**: Proactive issue detection, unusual pattern identification, security threat detection

## Submodule 1: log-group

### Description

The log-group submodule provides comprehensive management of CloudWatch log groups, which serve as containers for log streams from applications, AWS services, and infrastructure components. This submodule supports advanced features such as KMS encryption for data at rest, flexible retention policies ranging from 1 day to indefinite retention, and log class configuration for cost optimization through infrequent access storage tiers.

### Key Features

- Create and manage CloudWatch log groups with customizable names or name prefixes
- Configure retention periods from 1 day to indefinite retention (0 = never expire)
- Enable KMS encryption for logs at rest with custom KMS key support
- Support for STANDARD and INFREQUENT_ACCESS log classes for cost optimization
- Skip destroy option to prevent accidental log group deletion
- Comprehensive tagging support for resource organization
- Conditional creation flag for environment-specific deployments

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the log group |
| `name` | `string` | `""` | Name of the log group |
| `name_prefix` | `string` | `null` | Creates unique name beginning with prefix |
| `retention_in_days` | `number` | `null` | Log retention period (1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653, or 0 for never expire) |
| `kms_key_id` | `string` | `null` | ARN of KMS key to use for log encryption |
| `log_group_class` | `string` | `null` | Log class of the log group (STANDARD or INFREQUENT_ACCESS) |
| `skip_destroy` | `bool` | `null` | Set to true to prevent log group deletion when resource is destroyed |
| `tags` | `map(string)` | `{}` | Map of tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_log_group_name` | Name of the CloudWatch log group |
| `cloudwatch_log_group_arn` | ARN of the CloudWatch log group |

### Usage Example

```hcl
module "application_log_group" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-group"

  name              = "/aws/application/my-app"
  retention_in_days = 30
  kms_key_id        = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  log_group_class   = "STANDARD"

  tags = {
    Environment = "production"
    Application = "my-app"
    Team        = "platform"
  }
}

# Example 2: Cost-optimized log group for infrequent access
module "archive_log_group" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-group"

  name              = "/aws/archive/historical-logs"
  retention_in_days = 365
  log_group_class   = "INFREQUENT_ACCESS"  # Reduced cost for infrequent access
  skip_destroy      = true  # Prevent accidental deletion

  tags = {
    Environment = "production"
    Purpose     = "long-term-archive"
  }
}
```

## Submodule 2: log-stream

### Description

The log-stream submodule creates individual log streams within CloudWatch log groups, providing logical segregation of log events from different sources such as application instances, containers, or Lambda invocations. Log streams enable organized log management and facilitate efficient querying and analysis of logs from specific sources.

### Key Features

- Create log streams within existing log groups
- Support for custom log stream naming
- Automatic log stream management
- Integration with CloudWatch Logs agent and AWS services
- Conditional resource creation

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the log stream |
| `name` | `string` | `""` | Name of the log stream |
| `log_group_name` | `string` | `""` | Name of the log group to create the stream in |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_log_stream_name` | Name of the CloudWatch log stream |

### Usage Example

```hcl
module "application_log_stream" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-stream"

  name           = "app-server-instance-i-1234567890abcdef0"
  log_group_name = module.application_log_group.cloudwatch_log_group_name
}

# Example 2: Multiple log streams for container instances
module "container_log_streams" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-stream"

  for_each = toset(["container-1", "container-2", "container-3"])

  name           = each.key
  log_group_name = "/aws/ecs/my-cluster"
}
```

## Submodule 3: log-metric-filter

### Description

The log-metric-filter submodule creates CloudWatch metric filters that scan log events in real-time and extract numeric values or count occurrences of specific patterns, converting them into CloudWatch metrics. This enables monitoring and alarming on application-specific events, errors, or business metrics that are captured in logs but not natively available as CloudWatch metrics.

### Key Features

- Pattern-based metric extraction from log events
- Custom metric transformation with configurable values
- Support for metric dimensions for granular tracking
- Default value assignment for non-matching events
- Integration with CloudWatch alarms for alerting
- Metric unit configuration

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the metric filter |
| `log_group_name` | `string` | `""` | Name of the log group to attach the filter to |
| `name` | `string` | `""` | Name of the metric filter |
| `pattern` | `string` | `""` | CloudWatch Logs filter pattern for extracting metric data |
| `metric_transformation_name` | `string` | `""` | Name of the CloudWatch metric |
| `metric_transformation_namespace` | `string` | `""` | Destination namespace for the CloudWatch metric |
| `metric_transformation_value` | `string` | `"1"` | Value to publish to the CloudWatch metric |
| `metric_transformation_default_value` | `number` | `null` | Value to emit when filter pattern does not match |
| `metric_transformation_unit` | `string` | `null` | Unit to assign to the metric |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_log_metric_filter_id` | The name of the metric filter |

### Usage Example

```hcl
module "error_metric_filter" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-metric-filter"

  log_group_name = "/aws/lambda/my-function"
  name           = "error-count"
  pattern        = "[ERROR]"

  metric_transformation_name      = "ErrorCount"
  metric_transformation_namespace = "MyApplication"
  metric_transformation_value     = "1"
  metric_transformation_unit      = "Count"
}

# Example 2: Extract latency values from logs
module "latency_metric_filter" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-metric-filter"

  log_group_name = "/aws/application/api"
  name           = "api-latency"
  pattern        = "[timestamp, request_id, method, path, status, latency]"

  metric_transformation_name      = "APILatency"
  metric_transformation_namespace = "MyApplication/API"
  metric_transformation_value     = "$latency"
  metric_transformation_unit      = "Milliseconds"
  metric_transformation_default_value = 0
}
```

## Submodule 4: metric-alarm

### Description

The metric-alarm submodule creates CloudWatch metric alarms that monitor specific metrics and trigger actions when metric values breach defined thresholds. Alarms support various comparison operators, configurable evaluation periods, and flexible action configurations for different alarm states, making them essential for proactive monitoring and automated incident response.

### Key Features

- Configurable comparison operators (GreaterThanThreshold, LessThanThreshold, GreaterThanOrEqualToThreshold, etc.)
- Multiple evaluation periods and datapoints to alarm
- Support for metric math expressions
- Configurable alarm actions for ALARM, OK, and INSUFFICIENT_DATA states
- Treat missing data options for handling gaps in metrics
- Anomaly detection threshold support
- Extended statistics (percentiles) support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_metric_alarm` | `bool` | `true` | Whether to create the metric alarm |
| `alarm_name` | `string` | `""` | Descriptive name for the alarm |
| `comparison_operator` | `string` | `""` | Arithmetic operation to use when comparing statistic and threshold |
| `evaluation_periods` | `number` | `null` | Number of periods over which to evaluate the alarm |
| `threshold` | `number` | `null` | Value against which the statistic is compared |
| `metric_name` | `string` | `null` | Name of the metric to alarm on |
| `namespace` | `string` | `null` | Namespace of the metric |
| `period` | `number` | `null` | Period in seconds over which the statistic is applied |
| `statistic` | `string` | `null` | Statistic to apply (SampleCount, Average, Sum, Minimum, Maximum) |
| `alarm_description` | `string` | `null` | Description for the alarm |
| `alarm_actions` | `list(string)` | `[]` | List of ARNs to notify when alarm transitions to ALARM state |
| `ok_actions` | `list(string)` | `[]` | List of ARNs to notify when alarm transitions to OK state |
| `insufficient_data_actions` | `list(string)` | `[]` | List of ARNs to notify when alarm transitions to INSUFFICIENT_DATA |
| `treat_missing_data` | `string` | `"missing"` | How to treat missing data (missing, notBreaching, breaching, ignore) |
| `datapoints_to_alarm` | `number` | `null` | Number of datapoints that must be breaching to trigger alarm |
| `dimensions` | `map(string)` | `{}` | Dimensions for the metric |
| `tags` | `map(string)` | `{}` | Map of tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_metric_alarm_arn` | ARN of the CloudWatch metric alarm |
| `cloudwatch_metric_alarm_id` | ID of the CloudWatch metric alarm |

### Usage Examples

#### Example 1: CPU Utilization Alarm

```hcl
module "cpu_alarm" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/metric-alarm"

  alarm_name          = "high-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 80

  metric_name = "CPUUtilization"
  namespace   = "AWS/EC2"
  period      = 300
  statistic   = "Average"

  dimensions = {
    InstanceId = "i-1234567890abcdef0"
  }

  alarm_description = "This metric monitors EC2 CPU utilization"
  alarm_actions     = [aws_sns_topic.alerts.arn]
  ok_actions        = [aws_sns_topic.alerts.arn]

  tags = {
    Environment = "production"
    Severity    = "high"
  }
}
```

#### Example 2: Lambda Error Rate Alarm

```hcl
module "lambda_error_alarm" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/metric-alarm"

  alarm_name          = "lambda-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  threshold           = 5
  datapoints_to_alarm = 1

  metric_name = "Errors"
  namespace   = "AWS/Lambda"
  period      = 60
  statistic   = "Sum"

  dimensions = {
    FunctionName = "my-critical-function"
  }

  alarm_description      = "Alert when Lambda function has more than 5 errors per minute"
  alarm_actions          = [aws_sns_topic.critical_alerts.arn]
  treat_missing_data     = "notBreaching"

  tags = {
    Environment = "production"
    Severity    = "critical"
    Team        = "backend"
  }
}
```

## Submodule 5: metric-alarms-by-multiple-dimensions

### Description

The metric-alarms-by-multiple-dimensions submodule efficiently creates multiple similar alarms with different dimension values, ideal for monitoring fleets of resources such as Auto Scaling groups, ECS services, or Lambda functions. This submodule reduces configuration duplication and ensures consistent alarm settings across all monitored resources.

### Key Features

- Bulk alarm creation with consistent configuration
- Support for multiple dimension value combinations
- Reduces Terraform configuration complexity
- Maintains uniform alarm thresholds across resources
- Simplifies alarm management for resource fleets

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `alarm_name` | `string` | `""` | Base name for the alarms (dimension values appended) |
| `comparison_operator` | `string` | `""` | Comparison operator for all alarms |
| `evaluation_periods` | `number` | `null` | Evaluation periods for all alarms |
| `threshold` | `number` | `null` | Threshold value for all alarms |
| `metric_name` | `string` | `null` | Metric name for all alarms |
| `namespace` | `string` | `null` | Namespace for all alarms |
| `period` | `number` | `null` | Period for all alarms |
| `statistic` | `string` | `null` | Statistic for all alarms |
| `dimensions` | `map(list(string))` | `{}` | Map of dimension names to lists of dimension values |
| `alarm_actions` | `list(string)` | `[]` | Alarm actions for all alarms |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_metric_alarm_arns` | List of ARNs of the created metric alarms |
| `cloudwatch_metric_alarm_ids` | List of IDs of the created metric alarms |

### Usage Example

```hcl
module "instance_cpu_alarms" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/metric-alarms-by-multiple-dimensions"

  alarm_name          = "high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 80

  metric_name = "CPUUtilization"
  namespace   = "AWS/EC2"
  period      = 300
  statistic   = "Average"

  # Creates separate alarms for each instance
  dimensions = {
    InstanceId = ["i-1234567890abcdef0", "i-0987654321fedcba0", "i-abcdef1234567890"]
  }

  alarm_actions = [aws_sns_topic.ops_alerts.arn]
}

# Example 2: Monitor multiple Lambda functions
module "lambda_duration_alarms" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/metric-alarms-by-multiple-dimensions"

  alarm_name          = "lambda-high-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  threshold           = 5000

  metric_name = "Duration"
  namespace   = "AWS/Lambda"
  period      = 60
  statistic   = "Average"

  dimensions = {
    FunctionName = ["api-handler", "data-processor", "event-consumer"]
  }

  alarm_actions = [aws_sns_topic.lambda_alerts.arn]
}
```

## Submodule 6: cis-alarms

### Description

The cis-alarms submodule implements CloudWatch metric filters and alarms aligned with AWS CIS (Center for Internet Security) Foundations Benchmark security controls. This submodule provides pre-configured monitoring for critical security events such as unauthorized API calls, console login failures, IAM policy changes, network configuration changes, and root account usage, helping organizations maintain security compliance and detect potential threats.

### Key Features

- Pre-configured CIS Benchmark security monitoring controls
- Automatic metric filter and alarm creation for security events
- Selectively disable specific controls based on requirements
- CloudTrail log group integration for security event monitoring
- SNS notification integration for security alerts
- Customizable alarm namespaces and naming conventions
- Comprehensive coverage of CIS AWS Foundations controls

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create CIS alarms |
| `log_group_name` | `string` | `""` | CloudTrail log group name to monitor |
| `alarm_actions` | `list(string)` | `[]` | List of ARNs to notify when alarms trigger |
| `namespace` | `string` | `"CISBenchmark"` | CloudWatch namespace for CIS metrics |
| `disabled_controls` | `list(string)` | `[]` | List of CIS control IDs to disable |
| `use_random_name_prefix` | `bool` | `false` | Add random prefix to resource names |
| `tags` | `map(string)` | `{}` | Tags to apply to all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_metric_alarm_arns` | Map of CIS control IDs to alarm ARNs |
| `cloudwatch_metric_alarm_ids` | Map of CIS control IDs to alarm IDs |
| `cloudwatch_log_metric_filter_ids` | Map of CIS control IDs to metric filter IDs |

### Usage Example

```hcl
# Create SNS topic for security alerts
resource "aws_sns_topic" "cis_alerts" {
  name = "cis-security-alerts"
}

resource "aws_sns_topic_subscription" "security_team" {
  topic_arn = aws_sns_topic.cis_alerts.arn
  protocol  = "email"
  endpoint  = "security-team@example.com"
}

# Implement CIS security monitoring
module "cis_alarms" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/cis-alarms"

  log_group_name = "aws-cloudtrail-logs"
  alarm_actions  = [aws_sns_topic.cis_alerts.arn]
  namespace      = "CISBenchmark"

  # Optionally disable specific controls
  disabled_controls = [
    # "unauthorized-api-calls",  # Example: disable if needed
    # "console-login-without-mfa"
  ]

  tags = {
    Environment = "production"
    Compliance  = "CIS"
    Owner       = "security-team"
  }
}

# Example 2: Multiple environments with different control sets
module "cis_alarms_dev" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/cis-alarms"

  log_group_name = "aws-cloudtrail-logs-dev"
  alarm_actions  = [aws_sns_topic.dev_alerts.arn]

  # Disable some controls in development environment
  disabled_controls = [
    "console-login-without-mfa",
    "root-account-usage"
  ]

  tags = {
    Environment = "development"
    Compliance  = "CIS"
  }
}
```

## Submodule 7: log-data-protection

### Description

The log-data-protection submodule implements CloudWatch Logs data protection policies that automatically detect and mask sensitive information such as personally identifiable information (PII), credit card numbers, and other confidential data in log streams. This helps organizations maintain compliance with privacy regulations like GDPR, HIPAA, and PCI-DSS by preventing sensitive data exposure in logs.

### Key Features

- Automatic detection of sensitive data patterns
- Support for custom data identifiers
- Data masking and redaction capabilities
- Audit findings for detected sensitive data
- Integration with CloudWatch Logs
- Compliance with privacy regulations

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the data protection policy |
| `log_group_name` | `string` | `""` | Name of the log group to apply policy to |
| `policy_document` | `string` | `""` | JSON policy document defining data protection rules |

### Main Outputs

| Output | Description |
|--------|-------------|
| `log_data_protection_policy_log_group_name` | Name of the log group with data protection policy |

### Usage Example

```hcl
module "log_data_protection" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-data-protection"

  log_group_name = "/aws/application/payment-processor"

  policy_document = jsonencode({
    Name    = "PII-Protection-Policy"
    Version = "2021-06-01"
    Statement = [
      {
        Sid = "Audit"
        DataIdentifier = [
          "arn:aws:dataprotection::aws:data-identifier/EmailAddress",
          "arn:aws:dataprotection::aws:data-identifier/CreditCardNumber",
          "arn:aws:dataprotection::aws:data-identifier/SSN"
        ]
        Operation = {
          Audit = {
            FindingsDestination = {}
          }
        }
      },
      {
        Sid = "Redact"
        DataIdentifier = [
          "arn:aws:dataprotection::aws:data-identifier/CreditCardNumber",
          "arn:aws:dataprotection::aws:data-identifier/SSN"
        ]
        Operation = {
          Deidentify = {
            MaskConfig = {}
          }
        }
      }
    ]
  })
}
```

## Submodule 8: log-subscription-filter

### Description

The log-subscription-filter submodule creates real-time subscriptions to CloudWatch log groups, streaming log events to destinations such as Lambda functions, Kinesis streams, or Kinesis Data Firehose for immediate processing, analysis, or archival. This enables real-time log processing pipelines, SIEM integration, and centralized logging architectures.

### Key Features

- Real-time log streaming to multiple destinations
- Support for Lambda, Kinesis, and Kinesis Firehose
- Filter patterns to stream only relevant logs
- Cross-account log streaming support
- Role-based access control for subscriptions

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the subscription filter |
| `name` | `string` | `""` | Name of the subscription filter |
| `log_group_name` | `string` | `""` | Name of the log group to subscribe to |
| `filter_pattern` | `string` | `""` | Valid CloudWatch Logs filter pattern for subscribing |
| `destination_arn` | `string` | `""` | ARN of the destination (Lambda, Kinesis, or Firehose) |
| `role_arn` | `string` | `null` | ARN of IAM role for Kinesis/Firehose destinations |
| `distribution` | `string` | `null` | Distribution method (ByLogStream or Random) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_log_subscription_filter_name` | Name of the subscription filter |

### Usage Example

```hcl
# Stream logs to Lambda for processing
module "lambda_log_subscription" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-subscription-filter"

  name            = "error-logs-to-lambda"
  log_group_name  = "/aws/application/api"
  filter_pattern  = "[ERROR]"
  destination_arn = aws_lambda_function.log_processor.arn
}

# Stream all logs to Kinesis Firehose for archival
module "firehose_log_subscription" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-subscription-filter"

  name            = "all-logs-to-s3"
  log_group_name  = "/aws/application/api"
  filter_pattern  = ""  # Empty pattern streams all logs
  destination_arn = aws_kinesis_firehose_delivery_stream.logs.arn
  role_arn        = aws_iam_role.log_subscription_role.arn
}
```

## Submodule 9: metric-stream

### Description

The metric-stream submodule creates CloudWatch Metric Streams that continuously export CloudWatch metrics to external destinations via Kinesis Data Firehose, enabling near real-time metric delivery to third-party monitoring platforms like Datadog, Splunk, New Relic, or custom data lakes. This supports hybrid cloud observability and unified monitoring across multiple platforms.

### Key Features

- Near real-time metric streaming via Kinesis Data Firehose
- Support for JSON and OpenTelemetry 0.7 output formats
- Namespace-level include and exclude filters
- Metric filtering for cost optimization
- Integration with popular monitoring platforms

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the metric stream |
| `name` | `string` | `null` | Name of the metric stream |
| `name_prefix` | `string` | `null` | Name prefix for the metric stream |
| `firehose_arn` | `string` | `""` | ARN of Kinesis Data Firehose delivery stream |
| `role_arn` | `string` | `""` | ARN of IAM role for CloudWatch to assume |
| `output_format` | `string` | `""` | Output format (json or opentelemetry0.7) |
| `include_filter` | `list(object)` | `[]` | List of namespaces to include |
| `exclude_filter` | `list(object)` | `[]` | List of namespaces to exclude |
| `statistics_configuration` | `list(object)` | `[]` | Additional statistics to stream |
| `tags` | `map(string)` | `{}` | Tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_metric_stream_arn` | ARN of the metric stream |
| `cloudwatch_metric_stream_state` | State of the metric stream |
| `cloudwatch_metric_stream_creation_date` | Date the metric stream was created |
| `cloudwatch_metric_stream_last_update_date` | Date the metric stream was last updated |

### Usage Example

```hcl
# Create IAM role for metric stream
resource "aws_iam_role" "metric_stream" {
  name = "cloudwatch-metric-stream-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "streams.metrics.cloudwatch.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

# Stream metrics to Datadog via Firehose
module "datadog_metric_stream" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/metric-stream"

  name           = "datadog-metrics"
  firehose_arn   = aws_kinesis_firehose_delivery_stream.datadog.arn
  role_arn       = aws_iam_role.metric_stream.arn
  output_format  = "opentelemetry0.7"

  # Include only specific namespaces to reduce costs
  include_filter = [
    { namespace = "AWS/EC2" },
    { namespace = "AWS/RDS" },
    { namespace = "AWS/Lambda" }
  ]

  tags = {
    Environment = "production"
    Destination = "datadog"
  }
}

# Stream all metrics except specific namespaces
module "comprehensive_metric_stream" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/metric-stream"

  name          = "all-metrics-stream"
  firehose_arn  = aws_kinesis_firehose_delivery_stream.s3.arn
  role_arn      = aws_iam_role.metric_stream.arn
  output_format = "json"

  # Exclude high-volume, low-value namespaces
  exclude_filter = [
    { namespace = "AWS/Usage" },
    { namespace = "AWS/Billing" }
  ]

  tags = {
    Environment = "production"
    Purpose     = "data-lake"
  }
}
```

## Submodule 10: query-definition

### Description

The query-definition submodule creates reusable CloudWatch Logs Insights query definitions that can be saved, shared across teams, and quickly accessed from the CloudWatch console. This standardizes log analysis approaches, reduces query errors, and accelerates troubleshooting by providing pre-built queries for common investigation scenarios.

### Key Features

- Create reusable log query templates
- Support for multi-log-group queries
- Save complex queries for team sharing
- Quick access from CloudWatch console
- Standardized troubleshooting approaches

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the query definition |
| `name` | `string` | `""` | Name of the query definition |
| `query_string` | `string` | `""` | CloudWatch Logs Insights query string |
| `log_group_names` | `list(string)` | `[]` | List of log groups to query |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_query_definition_id` | ID of the query definition |

### Usage Example

```hcl
module "error_query" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/query-definition"

  name = "Find-Application-Errors"

  log_group_names = [
    "/aws/application/api",
    "/aws/application/worker"
  ]

  query_string = <<-EOQ
    fields @timestamp, @message, @logStream
    | filter @message like /ERROR/
    | sort @timestamp desc
    | limit 100
  EOQ
}

# Example 2: Latency analysis query
module "latency_query" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/query-definition"

  name            = "API-Latency-P99"
  log_group_names = ["/aws/application/api"]

  query_string = <<-EOQ
    fields @timestamp, requestId, path, latency
    | filter latency > 0
    | stats avg(latency) as avg_latency,
            pct(latency, 50) as p50,
            pct(latency, 90) as p90,
            pct(latency, 99) as p99 by bin(5m)
    | sort @timestamp desc
  EOQ
}
```

## Submodule 11: composite-alarm

### Description

The composite-alarm submodule creates CloudWatch composite alarms that combine multiple individual alarm states using logical operators (AND, OR, NOT), enabling sophisticated monitoring scenarios that reduce alarm fatigue and provide more accurate alerting based on correlated conditions. Composite alarms are essential for implementing service health checks and multi-signal alerting strategies.

### Key Features

- Combine multiple alarm states with AND/OR/NOT logic
- Reduce false positives through correlated alarming
- Support for actions suppressor to prevent notification storms
- Flexible alarm rule expressions
- Separate actions for different alarm states

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the composite alarm |
| `alarm_name` | `string` | `""` | Name of the composite alarm |
| `alarm_description` | `string` | `null` | Description of the composite alarm |
| `alarm_rule` | `string` | `""` | Expression that specifies which alarm states trigger the composite alarm |
| `actions_enabled` | `bool` | `true` | Whether actions should be executed during state changes |
| `alarm_actions` | `list(string)` | `[]` | Actions to execute when alarm transitions to ALARM |
| `ok_actions` | `list(string)` | `[]` | Actions to execute when alarm transitions to OK |
| `insufficient_data_actions` | `list(string)` | `[]` | Actions to execute when alarm transitions to INSUFFICIENT_DATA |
| `actions_suppressor` | `object` | `null` | Configuration for actions suppressor |
| `tags` | `map(string)` | `{}` | Tags to assign to the resource |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_composite_alarm_arn` | ARN of the composite alarm |
| `cloudwatch_composite_alarm_id` | ID of the composite alarm |

### Usage Example

```hcl
# Create individual alarms first
module "cpu_alarm" {
  source = "terraform-aws-modules/cloudwatch/aws//modules/metric-alarm"

  alarm_name          = "high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 80
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  statistic           = "Average"
  period              = 300
}

module "memory_alarm" {
  source = "terraform-aws-modules/cloudwatch/aws//modules/metric-alarm"

  alarm_name          = "high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 90
  metric_name         = "MemoryUtilization"
  namespace           = "CWAgent"
  statistic           = "Average"
  period              = 300
}

# Composite alarm triggers only when both CPU and memory are high
module "resource_pressure_alarm" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/composite-alarm"

  alarm_name        = "critical-resource-pressure"
  alarm_description = "Both CPU and memory are critically high"

  alarm_rule = "ALARM(${module.cpu_alarm.cloudwatch_metric_alarm_id}) AND ALARM(${module.memory_alarm.cloudwatch_metric_alarm_id})"

  alarm_actions = [aws_sns_topic.critical_alerts.arn]
  ok_actions    = [aws_sns_topic.critical_alerts.arn]

  tags = {
    Environment = "production"
    Severity    = "critical"
  }
}

# Example 2: Service health check with multiple conditions
module "service_health_alarm" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/composite-alarm"

  alarm_name = "service-unhealthy"

  # Alarm if error rate is high OR (latency is high AND throughput is low)
  alarm_rule = "ALARM(${module.error_rate_alarm.cloudwatch_metric_alarm_id}) OR (ALARM(${module.latency_alarm.cloudwatch_metric_alarm_id}) AND ALARM(${module.low_throughput_alarm.cloudwatch_metric_alarm_id}))"

  alarm_actions = [aws_sns_topic.service_alerts.arn]

  # Suppress during maintenance window
  actions_suppressor = {
    alarm     = module.maintenance_window_alarm.cloudwatch_metric_alarm_id
    extension_period = 300
    wait_period      = 60
  }

  tags = {
    Service     = "api"
    Environment = "production"
  }
}
```

## Submodule 12: log-account-policy

### Description

The log-account-policy submodule manages account-level CloudWatch Logs policies that apply governance and compliance rules across all log groups in an AWS account. This enables centralized policy management for data protection, subscription filters, and other log-related configurations without requiring individual log group modifications.

### Key Features

- Account-wide policy enforcement
- Centralized governance for log groups
- Support for data protection policies
- Subscription filter policies
- Simplified compliance management

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the account policy |
| `policy_name` | `string` | `""` | Name of the account policy |
| `policy_type` | `string` | `""` | Type of policy (DATA_PROTECTION_POLICY or SUBSCRIPTION_FILTER_POLICY) |
| `policy_document` | `string` | `""` | JSON policy document |
| `scope` | `string` | `null` | Scope for the policy (ALL or specific log groups) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_log_account_policy_id` | ID of the account policy |

### Usage Example

```hcl
module "account_data_protection" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-account-policy"

  policy_name = "account-wide-pii-protection"
  policy_type = "DATA_PROTECTION_POLICY"
  scope       = "ALL"

  policy_document = jsonencode({
    Name    = "Account-PII-Protection"
    Version = "2021-06-01"
    Statement = [{
      Sid = "AuditPII"
      DataIdentifier = [
        "arn:aws:dataprotection::aws:data-identifier/EmailAddress",
        "arn:aws:dataprotection::aws:data-identifier/SSN"
      ]
      Operation = {
        Audit = {
          FindingsDestination = {}
        }
      }
    }]
  })
}
```

## Submodule 13: log-anomaly-detector

### Description

The log-anomaly-detector submodule creates CloudWatch Logs anomaly detectors that use machine learning to automatically identify unusual patterns in log data. After a learning period, the detector establishes baseline behavior and alerts when log patterns deviate significantly from normal, enabling proactive issue detection without manually defined thresholds.

### Key Features

- Machine learning-based anomaly detection
- Automatic baseline learning
- Pattern deviation scoring
- Proactive issue identification
- No manual threshold configuration required

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the anomaly detector |
| `detector_name` | `string` | `null` | Name of the anomaly detector |
| `log_group_arn_list` | `list(string)` | `[]` | List of log group ARNs to monitor |
| `evaluation_frequency` | `string` | `null` | Frequency of evaluation (ONE_MIN, FIVE_MIN, TEN_MIN, FIFTEEN_MIN, THIRTY_MIN, ONE_HOUR) |
| `filter_pattern` | `string` | `null` | Optional filter pattern to apply before anomaly detection |
| `kms_key_id` | `string` | `null` | KMS key ID for encryption |
| `enabled` | `bool` | `true` | Whether the detector is enabled |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudwatch_log_anomaly_detector_arn` | ARN of the anomaly detector |
| `cloudwatch_log_anomaly_detector_id` | ID of the anomaly detector |

### Usage Example

```hcl
module "application_anomaly_detector" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-anomaly-detector"

  detector_name        = "app-log-anomaly-detector"
  evaluation_frequency = "FIVE_MIN"

  log_group_arn_list = [
    aws_cloudwatch_log_group.application.arn,
    aws_cloudwatch_log_group.api.arn
  ]

  # Optional: focus on error logs only
  filter_pattern = "[ERROR]"

  enabled = true
}
```

## Best Practices

### Monitoring and Alerting Strategy

1. **Implement Layered Monitoring**: Use a combination of metric alarms, composite alarms, and log metric filters to create comprehensive monitoring coverage for applications and infrastructure.
2. **Define Clear Alert Severity Levels**: Categorize alarms as critical, high, medium, or low severity, and route them to appropriate notification channels to reduce alert fatigue.
3. **Use Composite Alarms for Complex Scenarios**: Reduce false positives by combining multiple signals with AND/OR logic to create more accurate alerts that require correlated conditions.
4. **Set Appropriate Evaluation Periods**: Configure evaluation periods and datapoints-to-alarm to balance between quick detection and avoiding transient spike alerts.
5. **Implement Alarm Actions for All States**: Configure actions not just for ALARM state but also for OK and INSUFFICIENT_DATA to track alarm lifecycle and detect monitoring gaps.
6. **Use Metric Math for Advanced Calculations**: Leverage metric math expressions to create sophisticated derived metrics like error rates, percentages, or ratios.
7. **Test Alarms Before Production**: Validate alarm thresholds in non-production environments and adjust based on actual behavior patterns.

### Log Management and Retention

1. **Define Retention Policies by Log Type**: Set appropriate retention periods based on compliance requirements, operational needs, and cost considerations (e.g., 7 days for debug logs, 90 days for application logs, 365+ days for audit logs).
2. **Use Log Classes for Cost Optimization**: Move infrequently accessed logs to INFREQUENT_ACCESS log class to reduce storage costs by up to 50%.
3. **Implement Log Aggregation**: Use log subscription filters to aggregate logs from multiple sources into centralized log groups or external systems for unified analysis.
4. **Enable KMS Encryption**: Encrypt all log groups containing sensitive information using AWS KMS for compliance with data protection regulations.
5. **Use Structured Logging**: Emit logs in JSON format to enable more powerful querying and analysis with CloudWatch Logs Insights.
6. **Implement Log Sampling**: For extremely high-volume logs, consider sampling techniques to reduce costs while maintaining observability.
7. **Set Up Log Data Protection**: Use data protection policies to automatically detect and mask PII, credit card numbers, and other sensitive data.

### Security and Compliance

1. **Implement CIS Security Benchmarks**: Deploy the cis-alarms submodule to monitor critical security events and maintain compliance with AWS CIS Foundations Benchmark.
2. **Monitor CloudTrail Logs**: Create metric filters on CloudTrail logs to detect unauthorized API calls, privilege escalation, and security configuration changes.
3. **Enable Multi-Channel Alerting**: Send critical security alarms to multiple channels (SNS, email, PagerDuty, Slack) to ensure timely response.
4. **Use IAM Least Privilege**: Grant CloudWatch permissions following least privilege principle, limiting who can modify alarms, delete log groups, or change retention policies.
5. **Implement Log Immutability**: Use skip_destroy flag on critical audit log groups to prevent accidental deletion and maintain forensic evidence.
6. **Regular Security Audits**: Review CloudWatch configurations, alarm effectiveness, and log retention policies quarterly to ensure continued compliance.
7. **Enable Cross-Account Log Aggregation**: For organizations with multiple AWS accounts, centralize security logs in a dedicated logging account for better visibility and protection.

### Cost Optimization

1. **Right-Size Log Retention**: Regularly review and adjust log retention periods to balance operational needs with storage costs, using Data Lifecycle Manager for automated transitions.
2. **Use Metric Filters Instead of Log Queries**: Extract important metrics once using metric filters rather than repeatedly querying logs with Insights queries.
3. **Implement Namespace Filtering for Metric Streams**: When using metric streams, include only necessary namespaces to reduce Kinesis Firehose costs.
4. **Leverage INFREQUENT_ACCESS Log Class**: Migrate log groups with low query frequency to INFREQUENT_ACCESS class for significant cost savings.
5. **Monitor Unused Alarms**: Regularly audit and delete alarms that are no longer needed or haven't fired in extended periods.
6. **Batch Log Processing**: Use log subscription filters with Kinesis or Lambda for batch processing rather than real-time for non-critical logs.
7. **Set Up Cost Allocation Tags**: Tag all CloudWatch resources with cost center, environment, and application tags for accurate cost attribution and optimization opportunities.

### Operational Excellence

1. **Document Alarm Runbooks**: For each alarm, maintain runbooks documenting investigation steps, common causes, and remediation procedures.
2. **Implement Progressive Alarm Thresholds**: Use multiple alarms with escalating severity (warning at 70%, critical at 85%) to provide early warnings before critical failures.
3. **Create Standardized Query Definitions**: Use the query-definition submodule to share common troubleshooting queries across teams and reduce mean time to resolution.
4. **Enable Auto-Recovery Actions**: Where possible, configure alarm actions to trigger automated remediation through Lambda functions or Systems Manager Automation.
5. **Regular Alarm Tuning**: Review alarm history quarterly and adjust thresholds to reduce false positives while maintaining sensitivity to real issues.
6. **Use Anomaly Detection for Unknown Unknowns**: Deploy log anomaly detectors to discover issues that wouldn't be caught by threshold-based alarms.
7. **Implement Dashboard Visualization**: Create CloudWatch dashboards that display key metrics, alarm states, and trends for at-a-glance operational health.

### High Availability and Resilience

1. **Monitor Multi-AZ Resources**: Create separate alarms for each Availability Zone to detect zone-specific issues before they impact overall service.
2. **Implement Health Check Alarms**: Use composite alarms to create service-level health indicators that combine multiple infrastructure and application metrics.
3. **Set Up Cross-Region Monitoring**: For multi-region deployments, replicate critical alarms in each region and aggregate to a central monitoring account.
4. **Use Treat Missing Data Carefully**: Configure treat_missing_data appropriately (notBreaching for expected gaps, breaching for availability monitoring).
5. **Enable Actions Suppressor**: Use actions suppressors in composite alarms to prevent notification storms during planned maintenance or cascading failures.
6. **Monitor Backup and Recovery**: Create alarms for backup job failures, snapshot creation delays, and disaster recovery metric SLAs.

### Integration and Automation

1. **Integrate with Incident Management**: Connect CloudWatch alarms to PagerDuty, Opsgenie, or ServiceNow for automated incident creation and escalation.
2. **Use EventBridge for Complex Workflows**: Route alarm state changes through EventBridge to trigger sophisticated multi-step remediation workflows.
3. **Implement ChatOps Integration**: Send alarm notifications to Slack or Microsoft Teams channels for collaborative incident response.
4. **Automate Alarm Creation**: Use Terraform modules with for_each or count to automatically create alarms when new resources are provisioned.
5. **Stream Metrics to Data Lakes**: Use metric streams to build historical metric data lakes for long-term trend analysis and machine learning.
6. **Integrate with APM Tools**: Use metric streams and log subscriptions to feed data into Datadog, New Relic, Splunk, or Dynatrace for unified observability.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-cloudwatch
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/cloudwatch/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-cloudwatch/tree/master/examples
- **AWS CloudWatch Documentation**: https://docs.aws.amazon.com/cloudwatch/
- **CloudWatch Logs Documentation**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/
- **CloudWatch Alarms User Guide**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html
- **CloudWatch Logs Insights Query Syntax**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html
- **CloudWatch Pricing**: https://aws.amazon.com/cloudwatch/pricing/
- **CIS AWS Foundations Benchmark**: https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-cis-controls.html
- **CloudWatch Metric Streams**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Metric-Streams.html
- **CloudWatch Anomaly Detection**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Anomaly_Detection.html
- **Log Data Protection**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/mask-sensitive-log-data.html
- **CloudWatch Composite Alarms**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Create_Composite_Alarm.html
- **AWS Well-Architected Framework - Observability**: https://docs.aws.amazon.com/wellarchitected/latest/framework/a-observability.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Start with Log Groups**: Always create log groups before setting up metric filters, alarms, or subscription filters that depend on them
2. **Use Metric Filters for Custom Metrics**: Extract application-specific metrics from logs rather than instrumenting code, especially for legacy applications
3. **Implement Progressive Monitoring**: Start with basic metric alarms, then add log metric filters, then composite alarms as monitoring matures
4. **Tag Everything**: Consistently tag all CloudWatch resources with Environment, Application, Team, and CostCenter for organization and billing
5. **Test Alarm Thresholds**: Start with conservative thresholds and tune based on actual behavior to avoid alarm fatigue
6. **Use Submodules Selectively**: Only include submodules needed for your use case to keep Terraform state manageable
7. **Enable CIS Alarms for Security**: For production accounts, always implement cis-alarms submodule for security compliance monitoring
8. **Protect Sensitive Data**: Use log-data-protection submodule for any log groups that might contain PII or confidential information
9. **Plan for Scale**: When monitoring large resource fleets, use metric-alarms-by-multiple-dimensions to avoid Terraform configuration explosion
10. **Integrate with Incident Response**: Connect alarms to SNS topics that integrate with your incident management platform
11. **Document Dependencies**: Clearly document relationships between log groups, metric filters, and alarms for maintainability
12. **Version Pin the Module**: Always specify module version in Terraform to prevent unexpected changes from module updates
