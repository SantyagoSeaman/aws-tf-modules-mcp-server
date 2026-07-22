# Terraform AWS Security Hub Module

## Module Information

- **Module Name**: `security-hub`
- **Module ID**: `cloudposse/security-hub/aws`
- **Source**: `cloudposse/security-hub/aws`
- **GitHub Repository**: https://github.com/cloudposse/terraform-aws-security-hub
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/security-hub/aws/latest
- **Latest Version**: 0.13.0
- **Purpose**: Terraform module that enables AWS Security Hub in a single account/region, subscribes it to security standards (AWS Foundational Security Best Practices, CIS AWS Foundations Benchmark, PCI DSS), optionally aggregates findings across regions, and optionally routes imported findings to an SNS topic
- **Service**: AWS Security Hub
- **Category**: Security, Compliance
- **Keywords**: security-hub, aws-security-hub, findings-aggregation, finding-aggregator, security-standards, compliance-standards, cis-aws-foundations, cis-benchmark, aws-foundational-security-best-practices, pci-dss, standards-subscription, security-score, security-posture, findings-notifications, cross-region-findings-aggregation
- **Use For**: enabling AWS Security Hub in an account/region, subscribing to the CIS AWS Foundations Benchmark / AWS Foundational Security Best Practices / PCI DSS standards, aggregating Security Hub findings from multiple regions into one home region, routing imported findings to Slack/PagerDuty/Opsgenie/email via an SNS topic, filtering findings notifications by severity, suppressing duplicate per-region CIS controls in a centralized-logging multi-account estate, security posture and compliance-standards reporting

## Description

AWS Security Hub is a findings-aggregation and security-posture service: it does not itself detect threats, but instead collects, normalizes, and scores findings produced by other AWS security services (GuardDuty, Inspector, Macie, IAM Access Analyzer, and its own compliance checks) and by third-party tools, and evaluates a subscribed account against curated security-standards rule catalogs. This Terraform module wires together a working single-account, single-region Security Hub deployment: an `aws_securityhub_account` resource that enables the service for the calling account/region, and one or more `aws_securityhub_standards_subscription` resources that subscribe the account to compliance-standards rule sets — either the AWS-recommended defaults (`enable_default_standards`, which enables AWS Foundational Security Best Practices) or an explicit list (`enabled_standards`) that can add the CIS AWS Foundations Benchmark v1.2 (`ruleset/cis-aws-foundations-benchmark/v/1.2.0`) or PCI DSS v3.2.1 (`standards/pci-dss/v/3.2.1`).

Beyond standards subscription, the module can create an `aws_securityhub_finding_aggregator` (`finding_aggregator_enabled`) so that a single home region collects findings generated across every other region in the account, with the aggregation scope controlled by `finding_aggregator_linking_mode` (`ALL_REGIONS`, `ALL_REGIONS_EXCEPT_SPECIFIED`, or `SPECIFIED_REGIONS` plus `finding_aggregator_regions`). It also wires an imported-findings notification path: a CloudWatch Event Rule/Target watching for the `Security Hub Findings - Imported` detail-type (configurable via `cloudwatch_event_rule_pattern_detail_type`, filterable by `finding_severity_labels`) that forwards matching events into an SNS topic — either a new one built with the companion `cloudposse/sns-topic/aws` module and a dedicated KMS CMK (`create_sns_topic` + `subscribers`), or an existing topic referenced by `imported_findings_notification_arn`.

A separate `control-disablements` submodule addresses a distinct problem: some CIS 1.2 controls (e.g. verifying an account-level IAM configuration, or CloudTrail settings collected centrally) only need evaluating once per account, not once per region per account. The submodule holds a static, curated catalog of such controls and outputs the list of control ARNs to disable in non-collector regions/accounts; it does not disable anything itself — that requires the separate `awsutils` provider's `awsutils_security_hub_control_disablement` resource, applied with `depends_on` on this module's account enablement. Like every Cloud Posse module, the root module builds resource names and tags through the shared `label`/`context` convention.

## Key Features

- **Security Hub Account Enablement**: Creates the `aws_securityhub_account` resource that turns on Security Hub for the calling account/region
- **Default Standards Subscription**: `enable_default_standards` (default `true`) subscribes the account to AWS Foundational Security Best Practices automatically
- **Explicit Standards List**: `enabled_standards` subscribes to specific standard/ruleset ARN-suffix strings — CIS AWS Foundations Benchmark v1.2, PCI DSS v3.2.1, or AWS Foundational Security Best Practices by name
- **Cross-Region Finding Aggregation**: `finding_aggregator_enabled` creates an `aws_securityhub_finding_aggregator` collecting findings from other regions into this one
- **Configurable Aggregation Scope**: `finding_aggregator_linking_mode` (`ALL_REGIONS` / `ALL_REGIONS_EXCEPT_SPECIFIED` / `SPECIFIED_REGIONS`) plus `finding_aggregator_regions` controls exactly which regions feed the aggregator
- **Imported-Findings Event Routing**: A CloudWatch Event Rule/Target matches `Security Hub Findings - Imported` events (detail-type configurable via `cloudwatch_event_rule_pattern_detail_type`) and forwards them to SNS
- **Severity-Filtered Notifications**: `finding_severity_labels` restricts forwarded notifications to specific `Severity.Label` values (e.g. `["CRITICAL", "HIGH"]`); empty forwards all severities
- **New SNS Topic Creation**: `create_sns_topic` provisions a findings-notification SNS topic (via `cloudposse/sns-topic/aws`) with configurable `subscribers`, encrypted with a dedicated KMS CMK the module also provisions
- **Existing SNS Topic Support**: `imported_findings_notification_arn` routes findings to an already-existing SNS topic instead of creating a new one
- **Control-Disablements Submodule**: Computes the list of CIS 1.2 control ARNs that should be disabled outside the designated global/CloudTrail collector region or centralized-logging account
- **Cloud Posse Label Convention**: Consistent resource naming/tagging via `namespace`/`stage`/`name`/`context` inputs shared across every Cloud Posse module
- **Conditional Creation**: The `enabled` flag (part of the Cloud Posse `context`) toggles whether the module creates any resources at all

## Main Use Cases

1. **Baseline Security Hub Enablement**: Turn on Security Hub for an account/region as a security-posture prerequisite
2. **AWS Foundational Security Best Practices**: Adopt the AWS-recommended default standard with `enable_default_standards`
3. **CIS AWS Foundations Benchmark Compliance**: Subscribe to `ruleset/cis-aws-foundations-benchmark/v/1.2.0` via `enabled_standards` for baseline hardening checks
4. **PCI DSS Standard Subscription**: Subscribe to `standards/pci-dss/v/3.2.1` for regulated cardholder-data workloads
5. **Multi-Region Finding Aggregation**: Collect findings from every active region into one home/security region via `finding_aggregator_enabled`
6. **Findings Notifications**: Route imported findings to Slack/PagerDuty/Opsgenie/email through an SNS topic built by this module or an existing one
7. **Severity-Filtered Alerting**: Notify only on `CRITICAL`/`HIGH` findings to avoid paging on informational noise
8. **Multi-Account/Region Centralized Logging**: Suppress duplicate per-region CIS controls (IAM, CloudTrail) outside the designated collector region using the `control-disablements` submodule
9. **Security Posture and Compliance-Standards Reporting**: Feed a standards-subscription security score into governance dashboards
10. **Landing Zone / Account-Vending Security Baseline**: Bootstrap Security Hub enablement and standards subscription as part of new-account provisioning

## Usage Examples

### Example 1: Enable Security Hub with default standards and SNS findings notifications

```hcl
module "security_hub" {
  source  = "cloudposse/security-hub/aws"
  version = "0.13.0"

  namespace = "acme"
  stage     = "security"
  name      = "security-hub"

  enable_default_standards = true
  enabled_standards = [
    "ruleset/cis-aws-foundations-benchmark/v/1.2.0",
  ]

  create_sns_topic = true
  subscribers = {
    opsgenie = {
      protocol               = "https"
      endpoint               = "https://api.opsgenie.example.com/v1/"
      endpoint_auto_confirms = true
      raw_message_delivery   = false
    }
  }

  finding_severity_labels = ["CRITICAL", "HIGH"]
}
```

### Example 2: Cross-region finding aggregator plus per-region CIS control disablement

```hcl
module "security_hub" {
  source  = "cloudposse/security-hub/aws"
  version = "0.13.0"

  namespace = "acme"
  stage     = "security"
  name      = "security-hub"

  # Apply this block only in the designated aggregation home region
  finding_aggregator_enabled      = true
  finding_aggregator_linking_mode = "ALL_REGIONS"

  imported_findings_notification_arn = module.central_findings_topic.sns_topic_arn
}

module "control_disablements" {
  source  = "cloudposse/security-hub/aws//modules/control-disablements"
  version = "0.13.0"

  namespace = "acme"
  stage     = "security"
  name      = "security-hub"

  global_resource_collector_region = "us-east-1"
  central_logging_account          = "111111111111"
}

# Requires the separate `awsutils` Terraform provider (not part of this module)
resource "awsutils_security_hub_control_disablement" "global" {
  for_each    = toset(module.control_disablements.controls)
  control_arn = each.key
  reason      = "Global and CloudTrail resources are not collected in this account/region"

  depends_on = [
    module.security_hub
  ]
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `enabled` | `bool` | `null` | Set to false to prevent the module from creating any resources |
| `namespace` | `string` | `null` | ID element — organization abbreviation, e.g. `eg` or `cp` |
| `stage` | `string` | `null` | ID element — e.g. `prod`, `staging`, `security` |
| `name` | `string` | `null` | ID element — the component or solution name |
| `tags` | `map(string)` | `{}` | Additional tags applied to all resources |
| `context` | `any` | `{ "enabled": true, ... }` | Cloud Posse context object bundling namespace/stage/name/tags/etc. — see Notes for AI Agents for the full field list |
| `enable_default_standards` | `bool` | `true` | Enables the AWS-recommended default standard (AWS Foundational Security Best Practices) when true |
| `enabled_standards` | `list(any)` | `[]` | Explicit standard/ruleset ARN-suffix strings to subscribe to, e.g. `standards/aws-foundational-security-best-practices/v/1.0.0`, `ruleset/cis-aws-foundations-benchmark/v/1.2.0`, `standards/pci-dss/v/3.2.1` |
| `finding_aggregator_enabled` | `bool` | `false` | Creates an `aws_securityhub_finding_aggregator` to aggregate findings from other regions into this one |
| `finding_aggregator_linking_mode` | `string` | `"ALL_REGIONS"` | Aggregation scope: `ALL_REGIONS`, `ALL_REGIONS_EXCEPT_SPECIFIED`, or `SPECIFIED_REGIONS` |
| `finding_aggregator_regions` | `list(string)` | `[]` | Regions to aggregate from (`SPECIFIED_REGIONS`) or exclude (`ALL_REGIONS_EXCEPT_SPECIFIED`); only used when `finding_aggregator_enabled = true` |
| `create_sns_topic` | `bool` | `false` | Creates a new SNS topic (via the `sns-topic` module) for imported-findings notifications — provide `subscribers` when true |
| `subscribers` | `map(object)` | `{}` | SNS topic subscriptions for the findings topic — fields: `protocol`, `endpoint`, `endpoint_auto_confirms`, `raw_message_delivery` |
| `imported_findings_notification_arn` | `string` | `null` | ARN of an existing SNS topic to notify instead of `create_sns_topic` |
| `finding_severity_labels` | `list(string)` | `[]` | Restrict forwarded-finding notifications to these `Severity.Label` values (e.g. `["CRITICAL", "HIGH"]`); empty forwards all severities |
| `cloudwatch_event_rule_pattern_detail_type` | `string` | `"Security Hub Findings - Imported"` | CloudWatch Events `detail-type` pattern matched to trigger the SNS notification |

## Main Outputs

| Output | Description |
|--------|-------------|
| `enabled_subscriptions` | A list of the standards subscriptions (ARNs) that were enabled |
| `sns_topic` | The SNS topic created for findings notifications (set only when `create_sns_topic = true`) |
| `sns_topic_subscriptions` | The SNS topic subscriptions created for the findings topic |

## Submodules

### 1. control-disablements

- **Purpose**: Computes the list of CIS 1.2 control ARNs that should be disabled in a non-collector account/region (controls that only need checking once per account, not once per region per account) — returns the list via the `controls` output; does not disable anything itself
- **Source**: `cloudposse/security-hub/aws//modules/control-disablements`
- **Documentation Link**: https://registry.terraform.io/modules/cloudposse/security-hub/aws/latest/submodules/control-disablements
- **Key Features**: static CIS 1.2 control catalog scoped by the caller's current account/region/partition, `central_logging_account` + `global_resource_collector_region` inputs mirror the AWS Config module's collector-region convention, `controls` output pairs with the separate `awsutils` provider's `awsutils_security_hub_control_disablement` resource
- **Use Cases**: multi-region deployments where the same account applies the root module once per active region — suppress duplicate global/CloudTrail-scoped CIS controls outside the designated collector region/account

## Best Practices

### Standards Subscription

1. **Understand Default vs. Explicit**: `enable_default_standards = true` (the default) subscribes only to AWS Foundational Security Best Practices; add `enabled_standards` entries to also (or, with `enable_default_standards = false`, instead) subscribe to CIS AWS Foundations Benchmark v1.2 or PCI DSS.
2. **Verify Standard ARN Strings**: `enabled_standards` entries are exact ARN-suffix strings (e.g. `ruleset/cis-aws-foundations-benchmark/v/1.2.0`) — confirm current values via the AWS Security Hub standards reference rather than guessing versions.
3. **Account Enablement Precedes Standards Subscription**: the module's `aws_securityhub_account` resource must exist before `aws_securityhub_standards_subscription` can apply; this ordering is handled automatically inside the module, but if Security Hub was enabled outside Terraform, check `terraform plan` for drift before applying.

### Multi-Region Aggregation

1. **Aggregate Into One Home Region**: Set `finding_aggregator_enabled = true` in exactly one region per account — the intended aggregation target — not in every region the module is applied to.
2. **Choose the Right Linking Mode**: `ALL_REGIONS` auto-includes future regions with no maintenance; `SPECIFIED_REGIONS`/`ALL_REGIONS_EXCEPT_SPECIFIED` require keeping `finding_aggregator_regions` current by hand.
3. **Pair With `control-disablements` in Multi-Account/Region Estates**: apply the submodule per non-collector region/account to suppress duplicate CIS checks for global/CloudTrail-scoped controls.

### Notifications

1. **Reuse an Existing Topic When Possible**: set `imported_findings_notification_arn` instead of `create_sns_topic = true` when a shared compliance-notifications topic already exists.
2. **Filter Noisy Severities**: set `finding_severity_labels = ["CRITICAL", "HIGH"]` to avoid paging on `LOW`/`INFORMATIONAL` findings.
3. **Mind the `raw_message_delivery` Flag**: leave it `false` for subscribers (e.g. PagerDuty, Opsgenie) that expect the SNS JSON envelope rather than the raw message body.

### General

1. **Pin the Module Version**: use an explicit `version = "0.13.0"` — Cloud Posse's own usage snippet intentionally omits a version pin, so do not copy it verbatim into production code.
2. **One Root Call per Account/Region**: apply the root module once per account per active region; use the `control-disablements` submodule (not a second root call) to handle "once per account" controls.

## Additional Resources

- **Module Repository**: https://github.com/cloudposse/terraform-aws-security-hub
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/security-hub/aws/latest
- **Module Examples**: https://github.com/cloudposse/terraform-aws-security-hub/tree/master/examples/complete
- **Control Disablements Submodule**: https://registry.terraform.io/modules/cloudposse/security-hub/aws/latest/submodules/control-disablements
- **AWS Security Hub User Guide**: https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html
- **AWS Security Hub Standards Reference**: https://docs.aws.amazon.com/securityhub/latest/userguide/standards-reference.html
- **aws_securityhub_standards_subscription Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/securityhub_standards_subscription
- **aws_securityhub_finding_aggregator Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/securityhub_finding_aggregator
- **CIS AWS Foundations Benchmark**: https://docs.aws.amazon.com/audit-manager/latest/userguide/CIS-1-2.html

## Notes for AI Agents

This module is published by Cloud Posse (namespace `cloudposse`), not the `terraform-aws-modules` org. It uses Cloud Posse's `context`/`label` convention — inputs like `namespace`, `stage`, `name`, `environment`, `tenant`, `attributes`, `tags` and a `context` object drive resource naming/tagging across every Cloud Posse module. Do NOT propagate this convention onto other (differently-styled) modules in the same project; set the label inputs this module needs and leave other vendors' modules alone.

When using this module in automated workflows:

1. **Findings Aggregation, Not Threat Detection**: This module is the security-standards/compliance-findings-aggregation layer — standards subscription (CIS AWS Foundations Benchmark, AWS Foundational Security Best Practices, PCI DSS) plus an optional cross-region `finding_aggregator`. It does NOT generate threat-intel findings itself; GuardDuty (a separate `guardduty` module in this catalog) is the threat-detection/anomaly-detection source many of the findings Security Hub aggregates originate from. Security Hub aggregates and scores findings — including GuardDuty's — it does not replace GuardDuty.
2. **Account Enablement Precedes Standards Subscription**: the module creates `aws_securityhub_account` before subscribing standards. If Security Hub was already enabled for the account outside Terraform, review `terraform plan` for drift before applying.
3. **Default Standards Is Not "None"**: `enable_default_standards` defaults to `true` (AWS Foundational Security Best Practices); to run only explicit `enabled_standards` entries, set `enable_default_standards = false`.
4. **Aggregator Region Discipline**: set `finding_aggregator_enabled = true` in exactly one region (the intended aggregation target) per account — enabling it in multiple regions creates multiple aggregators each expecting to be "the" home region.
5. **`control-disablements` Is Advisory, Not Enforcing**: the submodule only computes a `controls` list output; actually disabling controls requires the separate `awsutils` Terraform provider's `awsutils_security_hub_control_disablement` resource (not part of this Cloud Posse module), wired with `depends_on = [module.security_hub]` against this module's account enablement.
6. **Only Three Root Outputs**: `enabled_subscriptions`, `sns_topic`, `sns_topic_subscriptions` — there is no account-ARN/id output; use the AWS provider directly if a downstream resource needs the Security Hub account's identifier.
7. **`subscribers` Shape**: `subscribers` (`map(object)`) needs `protocol`, `endpoint`, `endpoint_auto_confirms`, `raw_message_delivery` — the same object shape as `cloudposse/sns-topic/aws`; keep `raw_message_delivery = false` for subscribers expecting the SNS JSON envelope.
8. **Pin the Module Version**: use an explicit `version = "0.13.0"` for reproducible deployments; Cloud Posse's own usage examples intentionally omit a version pin, which is not a pattern to copy into real infrastructure.
