# Terraform AWS GuardDuty Module

## Module Information

- **Module Name**: `guardduty`
- **Module ID**: `cloudposse/guardduty/aws`
- **Source**: `cloudposse/guardduty/aws`
- **GitHub Repository**: https://github.com/cloudposse/terraform-aws-guardduty
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/guardduty/aws/latest
- **Latest Version**: 1.0.0
- **Purpose**: Terraform module that enables and configures Amazon GuardDuty — continuous, ML-driven threat detection, intrusion detection, and anomaly detection for a single AWS account/region — with optional S3, EKS, EBS malware, Lambda, and runtime protection features plus SNS/CloudWatch findings notifications
- **Service**: Amazon GuardDuty
- **Category**: Security, Threat Detection, Monitoring
- **Keywords**: guardduty, aws-guardduty, threat-detection, intrusion-detection, anomaly-detection, malware-protection, threat-intelligence, security-monitoring, detector, ebs-malware-scan, s3-threat-monitoring, eks-audit-logs, runtime-monitoring, lambda-network-monitoring, findings-notifications, cloudposse
- **Use For**: enabling AWS GuardDuty threat detection in a single AWS account/region, detecting anomalous CloudTrail API activity and reconnaissance, malware scanning of EC2 EBS volumes, EKS/Kubernetes audit log threat analysis, Lambda function network threat monitoring, runtime threat detection for EC2/ECS/EKS workloads, routing GuardDuty findings to SNS/CloudWatch for alerting, security baseline for new AWS accounts, layering active threat detection alongside AWS Config/Security Hub compliance tooling

## Description

Amazon GuardDuty is a continuous threat detection service that uses machine learning, anomaly detection, and integrated threat intelligence to identify malicious or unauthorized activity — compromised credentials, reconnaissance, malware, and anomalous API behavior — by analyzing VPC Flow Logs, DNS logs, and CloudTrail management/data events without requiring any agents to be deployed for its baseline detection. This Cloud Posse module provisions a single `aws_guardduty_detector` and enables individual detection features on it through the current, non-deprecated `aws_guardduty_detector_feature` resource (replacing the older `datasources` block): S3 Data Events Protection, EKS Audit Logs, EBS Malware Protection, Lambda Network Logs, and either unified Runtime Monitoring (EC2/ECS/EKS) or standalone EKS Runtime Monitoring.

This module enables and configures GuardDuty for exactly **one region of one AWS account** — the detector resource itself is inherently regional, so protecting multiple regions or accounts means invoking this module once per region. As of v1.0.0 the module has **no submodule and no built-in mechanism for organization-wide administration** (delegated GuardDuty administrator, automatic member-account enrollment, or organization-wide RDS Login Events via `aws_guardduty_organization_configuration_feature`) — those concerns live outside this module's scope entirely; do not assume an `organization-settings` or similar submodule exists.

Alongside detection, the module optionally wires findings delivery: `create_sns_topic` provisions an SNS topic (via the companion `cloudposse/sns-topic/aws` module) with configurable `subscribers`, or `findings_notification_arn` routes findings to an already-existing topic; `enable_cloudwatch` creates an `aws_cloudwatch_event_rule` matching a configurable finding detail-type (default `"GuardDuty Finding"`) and targets it at the notification topic. Like every Cloud Posse module, resource naming and tagging flow through the shared `label`/`context` convention.

## Key Features

- **Central GuardDuty Detector**: Creates the single `aws_guardduty_detector` that every enabled detection feature attaches to
- **S3 Data Events Protection** (`s3_protection_enabled`): Monitors S3 data-plane operations (GetObject, PutObject, DeleteObject) for suspicious access patterns and potential data exfiltration
- **EKS Audit Logs** (`kubernetes_audit_logs_enabled`): Analyzes Kubernetes API server audit logs for suspicious kubectl commands, unauthorized access, and privilege escalation
- **EBS Malware Protection** (`malware_protection_scan_ec2_ebs_volumes_enabled`): Agentless malware scanning of EC2 instance EBS volumes via snapshots
- **Lambda Network Logs** (`lambda_network_logs_enabled`): Monitors Lambda function network connections for known-malicious IPs or unexpected network behavior
- **Runtime Monitoring** (`runtime_monitoring_enabled`): Unified runtime threat detection for EC2, ECS, and EKS resources, with agent-management toggles for each
- **EKS Runtime Monitoring** (`eks_runtime_monitoring_enabled`): Standalone, lighter-weight EKS-only runtime monitoring for when EC2/ECS coverage is not needed
- **Mutual-Exclusivity Guard**: A `lifecycle.precondition` blocks `apply` if both `runtime_monitoring_enabled` and `eks_runtime_monitoring_enabled` are `true` (Runtime Monitoring already covers EKS)
- **Runtime Agent Management**: `runtime_monitoring_additional_config` independently toggles EKS add-on, ECS Fargate agent, and EC2 agent management
- **Finding Publishing Frequency Control**: `finding_publishing_frequency` sets `FIFTEEN_MINUTES`/`ONE_HOUR`/`SIX_HOURS` for standalone/master accounts
- **Optional SNS Findings Topic**: `create_sns_topic` provisions an SNS topic (via `sns-topic`) with `subscribers` for findings notifications
- **Existing SNS Topic Support**: `findings_notification_arn` routes findings to an already-existing SNS topic instead of creating a new one
- **CloudWatch Events Integration**: `enable_cloudwatch` creates an `aws_cloudwatch_event_rule`/`aws_cloudwatch_event_target` pair matching GuardDuty finding events
- **Modern Detector-Feature Resources**: Uses `aws_guardduty_detector_feature` exclusively, not the deprecated `datasources` block
- **Cloud Posse Label Convention**: Consistent resource naming/tagging via `namespace`/`stage`/`name`/`context` inputs shared across every Cloud Posse module
- **Conditional Creation**: The `enabled` flag (part of the Cloud Posse `context`) toggles whether the module creates any resources at all

## Main Use Cases

1. **Baseline Threat Detection**: Continuous ML-based threat and anomaly detection for a new or existing AWS account/region
2. **Malicious API Activity & Reconnaissance Detection**: Detect anomalous CloudTrail management-event API calls indicative of compromised credentials or account reconnaissance
3. **S3 Data Exfiltration Detection**: Monitor S3 data-plane operations for suspicious access patterns via S3 Protection
4. **EKS/Kubernetes Threat Detection**: Analyze EKS audit logs for suspicious cluster activity
5. **EBS Malware Scanning**: Agentless malware detection on EC2 EBS volumes
6. **Lambda Network Threat Monitoring**: Detect Lambda functions communicating with known-malicious network destinations
7. **Runtime Threat Detection**: Monitor EC2/ECS/EKS runtime activity (file access, process execution, network connections) for active compromise
8. **Findings Alerting**: Route GuardDuty findings to SNS (email, HTTPS, SQS, Lambda) and/or CloudWatch Events for real-time alerting
9. **Security Baseline for New AWS Accounts**: Enable threat detection as part of an account-vending or landing-zone pipeline
10. **Complementing Compliance Tooling**: Layer active threat/intrusion detection alongside — not instead of — configuration-compliance tools like AWS Config or Security Hub's standards checks

## Usage Examples

### Example 1: Single-account, single-region GuardDuty with SNS notifications

```hcl
module "guardduty" {
  source  = "cloudposse/guardduty/aws"
  version = "1.0.0"

  namespace = "acme"
  stage     = "prod"
  name      = "guardduty"

  create_sns_topic = true
  subscribers = {
    opsgenie = {
      protocol               = "https"
      endpoint               = "https://api.example.com/v1/"
      endpoint_auto_confirms = true
      raw_message_delivery   = false
    }
  }
}
```

### Example 2: All detection features enabled, with CloudWatch Events and Runtime Monitoring

```hcl
module "guardduty" {
  source  = "cloudposse/guardduty/aws"
  version = "1.0.0"

  namespace = "acme"
  stage     = "prod"
  name      = "guardduty"

  # SNS and CloudWatch notifications
  create_sns_topic                          = true
  enable_cloudwatch                         = true
  cloudwatch_event_rule_pattern_detail_type = "GuardDuty Finding"
  finding_publishing_frequency              = "FIFTEEN_MINUTES"

  subscribers = {
    security-team = {
      protocol               = "https"
      endpoint               = "https://api.example.com/v1/guardduty"
      endpoint_auto_confirms = true
      raw_message_delivery   = false
    }
  }

  # Threat detection features
  s3_protection_enabled                           = true
  kubernetes_audit_logs_enabled                   = true
  malware_protection_scan_ec2_ebs_volumes_enabled = true
  lambda_network_logs_enabled                     = true

  # Runtime Monitoring for EC2, ECS, and EKS.
  # Do NOT also set eks_runtime_monitoring_enabled = true -- Runtime Monitoring
  # already includes EKS threat detection; enabling both fails a precondition.
  runtime_monitoring_enabled = true
  runtime_monitoring_additional_config = {
    eks_addon_management_enabled         = true
    ecs_fargate_agent_management_enabled = true
    ec2_agent_management_enabled         = true
  }
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_sns_topic` | `bool` | `false` | Creates an SNS topic for findings notifications (provide `subscribers` when true) |
| `subscribers` | `map(object)` | `{}` | A map of SNS subscription configurations for the findings topic — fields: `protocol`, `endpoint`, `endpoint_auto_confirms`, `raw_message_delivery` (see the `sns-topic` module) |
| `findings_notification_arn` | `string` | `null` | ARN of an existing SNS topic to send findings to instead of `create_sns_topic` |
| `finding_publishing_frequency` | `string` | `null` | Notification frequency for findings: `FIFTEEN_MINUTES`, `ONE_HOUR`, or `SIX_HOURS` — ignored on GuardDuty member accounts, where the master account controls it |
| `enable_cloudwatch` | `bool` | `false` | Creates a CloudWatch Events rule/target for GuardDuty findings (auto-enabled when notifications are configured) |
| `cloudwatch_event_rule_pattern_detail_type` | `string` | `"GuardDuty Finding"` | The CloudWatch Events `detail-type` pattern used to match findings events |
| `s3_protection_enabled` | `bool` | `false` | Enables S3 Data Events as a GuardDuty data source |
| `kubernetes_audit_logs_enabled` | `bool` | `false` | Enables Kubernetes audit logs as a data source for EKS threat detection |
| `malware_protection_scan_ec2_ebs_volumes_enabled` | `bool` | `false` | Enables agentless Malware Protection scanning of EC2 EBS volumes |
| `lambda_network_logs_enabled` | `bool` | `false` | Enables Lambda network logs as a data source for Lambda threat detection |
| `runtime_monitoring_enabled` | `bool` | `false` | Enables unified Runtime Monitoring for EC2, ECS, and EKS resources — mutually exclusive with `eks_runtime_monitoring_enabled` |
| `eks_runtime_monitoring_enabled` | `bool` | `false` | Enables standalone EKS-only Runtime Monitoring — mutually exclusive with `runtime_monitoring_enabled` |
| `runtime_monitoring_additional_config` | `object` | `{}` | Additional agent-management configuration for Runtime Monitoring — fields: `eks_addon_management_enabled`, `ecs_fargate_agent_management_enabled`, `ec2_agent_management_enabled` |
| `enabled` | `bool` | `null` | Set to `false` to prevent the module from creating any resources |
| `namespace` | `string` | `null` | ID element — organization abbreviation, e.g. `eg` or `cp` |
| `stage` | `string` | `null` | ID element — e.g. `prod`, `staging`, `dev` |
| `name` | `string` | `null` | ID element — the component or solution name |
| `environment` | `string` | `null` | ID element — usually used for region or role, e.g. `uw2`, `us-west-2`, `prod` |
| `attributes` | `list(string)` | `[]` | ID element — additional attributes appended to `id`, in order |
| `tags` | `map(string)` | `{}` | Additional tags applied to all resources |
| `context` | `any` | `{ "enabled": true, ... }` | Single object for setting the entire Cloud Posse context at once — see the `namespace`/`stage`/`name`/`tags` fields above for the individual values it bundles |

## Main Outputs

| Output | Description |
|--------|-------------|
| `guardduty_detector` | The `aws_guardduty_detector` resource (id, arn, account_id, finding_publishing_frequency, etc.); `null` when `enabled = false` |
| `sns_topic` | The SNS topic used for findings notifications; set only when `create_sns_topic = true` |
| `sns_topic_subscriptions` | The SNS topic subscriptions created for the findings topic (from the `sns-topic` submodule); set only when `create_sns_topic = true` |

## Best Practices

### Detector Rollout

1. **Enable Every Region You Operate In**: GuardDuty detectors are regional — apply this module once per region you run workloads in, not once per account.
2. **Start with the High-Signal Features**: Enable `s3_protection_enabled`, `kubernetes_audit_logs_enabled`, and `malware_protection_scan_ec2_ebs_volumes_enabled` first; add `lambda_network_logs_enabled` and Runtime Monitoring once findings volume is understood.
3. **Choose One Runtime Monitoring Mode**: Set either `runtime_monitoring_enabled` (EC2+ECS+EKS) or `eks_runtime_monitoring_enabled` (EKS only) — never both; the module enforces this at plan time via a precondition, so a mistaken configuration fails fast rather than silently.

### Findings Delivery

1. **Prefer an Existing Shared Topic**: Set `findings_notification_arn` instead of `create_sns_topic = true` when a shared security-notifications topic already exists.
2. **Tune `finding_publishing_frequency` Deliberately**: `FIFTEEN_MINUTES` gives the fastest alerting for standalone/master accounts; remember it has no effect on GuardDuty member accounts, where the master account's setting wins.
3. **Enable CloudWatch for Automation**: Set `enable_cloudwatch = true` when findings need to drive automated remediation (e.g. via EventBridge/Lambda) rather than just human alerting through SNS.

### Organization-Wide Deployments

1. **This Module Does Not Manage Organization Settings**: There is no submodule here for delegated administrator setup, member-account auto-enrollment, or org-wide RDS Login Events — apply this module independently in each account/region and handle organization-level GuardDuty administration through a separate mechanism (AWS Organizations console/API, a different Terraform component, or hand-authored `aws_guardduty_organization_configuration_feature` resources).
2. **RDS Login Events Needs Org-Level Config**: `RDS_LOGIN_EVENTS` can only be enabled via `aws_guardduty_organization_configuration_feature` at the organization level, not through any variable this module exposes.

## Additional Resources

- **Module Repository**: https://github.com/cloudposse/terraform-aws-guardduty
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/guardduty/aws/latest
- **Module Example**: https://github.com/cloudposse/terraform-aws-guardduty/tree/main/examples/complete
- **Companion SNS Topic Module**: https://registry.terraform.io/modules/cloudposse/sns-topic/aws/latest
- **Amazon GuardDuty User Guide**: https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html
- **aws_guardduty_detector_feature Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/guardduty_detector_feature
- **aws_guardduty_organization_configuration_feature Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/guardduty_organization_configuration_feature
- **GuardDuty Findings + CloudWatch Events**: https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings_cloudwatch.html
- **Cloud Posse `null-label` Module (context/label convention)**: https://github.com/cloudposse/terraform-null-label
- **Amazon GuardDuty Pricing**: https://aws.amazon.com/guardduty/pricing/

## Important Gotchas

- **No Organization-Settings Submodule**: As of v1.0.0 this module's repository contains only `main.tf`/`variables.tf`/`outputs.tf` (no `modules/` directory) — there is no submodule for organization administration, delegated admin, or member-account enrollment. Do not assume one exists; each region/account gets its own module call.
- **RDS Login Events Is Out of Scope**: `RDS_LOGIN_EVENTS` can only be configured via `aws_guardduty_organization_configuration_feature` at the organization level — this module has no input for it, even though every other detector feature is exposed.
- **Runtime Monitoring Flags Are Mutually Exclusive**: Setting both `runtime_monitoring_enabled = true` and `eks_runtime_monitoring_enabled = true` fails at `plan`/`apply` via an explicit `lifecycle.precondition` — this is enforced, not just documented.
- **`finding_publishing_frequency` Is Ignored on Member Accounts**: On a GuardDuty member account, this value is controlled by the GuardDuty master/administrator account and cannot be overridden here, even though Terraform will still show it as configured.
- **Detector-Per-Region**: GuardDuty detectors are regional resources — one `apply` of this module covers exactly one region of one account; there is no cross-region aggregation built into this module (unlike, e.g., the `config` module's aggregator).
- **Modern Resource Type**: The module uses `aws_guardduty_detector_feature` exclusively; if migrating from a hand-written GuardDuty setup that used the deprecated `datasources` block on `aws_guardduty_detector`, expect a resource-model change, not a drop-in replacement.
- **Pin the Module Version**: Use an explicit `version = "1.0.0"` — Cloud Posse's own README usage snippets intentionally omit a version pin, so do not copy them verbatim into production code.

## Notes for AI Agents

This module is published by Cloud Posse (namespace `cloudposse`), not the `terraform-aws-modules` org. It uses Cloud Posse's `context`/`label` convention — inputs like `namespace`, `stage`, `name`, `environment`, `tenant`, `attributes`, `tags` and a `context` object drive resource naming/tagging across every Cloud Posse module. Do NOT propagate this convention onto other (differently-styled) modules in the same project; set the label inputs this module needs and leave other vendors' modules alone.

When using this module in automated workflows:

1. **This Is Threat Detection, Not Findings Aggregation**: Keep this module's keywords/use cases distinct from a `security-hub` module — GuardDuty performs active threat detection, intrusion detection, anomaly detection, and malware scanning against live account activity; it does not aggregate findings across security tools or evaluate CIS/security-standards compliance (that is Security Hub's job, and `config`'s for resource-configuration compliance rules).
2. **One Detector, One Region, One Account**: This module enables and configures GuardDuty for exactly one region of one account — plan a separate module call per region, and do not expect any built-in multi-account/multi-region aggregation.
3. **No Organization-Settings Submodule Exists**: Do not reference or invent a submodule path (e.g. `cloudposse/guardduty/aws//modules/organization-settings`) for delegated-admin or member-account configuration — as of v1.0.0 none exists in this repository; that functionality must come from elsewhere (hand-authored `aws_guardduty_organization_configuration_feature` resources or a different component).
4. **RDS Login Events Needs a Different Mechanism**: If a task requires `RDS_LOGIN_EVENTS`, this module cannot provide it — it is an organization-level-only feature configured via `aws_guardduty_organization_configuration_feature`, outside this module's inputs.
5. **Never Enable Both Runtime Monitoring Modes**: Setting `runtime_monitoring_enabled` and `eks_runtime_monitoring_enabled` together will fail the module's `lifecycle.precondition` — pick exactly one.
6. **Member-Account Frequency Override**: Do not expect `finding_publishing_frequency` to take effect on a GuardDuty member account; the master/administrator account's setting always wins there.
7. **Verify Exact Variable Names via `get_module`**: Cloud Posse modules occasionally rename or add label inputs across versions — confirm `subscribers`/`runtime_monitoring_additional_config`/detection-toggle names and defaults with `get_module(sections=["inputs","outputs"])` against the pinned `1.0.0` docs before relying on memorized values.
8. **Pin the Module Version**: Use an explicit `version = "1.0.0"` constraint for reproducible deployments; Cloud Posse's own usage examples intentionally omit a version pin, which is not a pattern to copy into real infrastructure.
