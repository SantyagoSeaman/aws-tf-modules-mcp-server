---
module_name: terraform-aws-wafv2
keywords: [waf, wafv2, web-application-firewall, web-acl, firewall, application-firewall, rate-limiting, managed-rules, owasp, bot-control, ip-set, regex-pattern-set, rule-group, cloudfront, alb, api-gateway, appsync, ddos-protection, layer7, security]
---

# Terraform AWS WAF v2 Module

## Module Information

- **Module Name**: `wafv2`
- **Module ID**: `terraform-aws-modules/wafv2/aws`
- **Source**: `terraform-aws-modules/wafv2/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-wafv2
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/wafv2/aws/latest
- **Latest Version**: 2.1.0
- **Purpose**: Terraform module that creates and manages AWS WAF v2 resources (Web ACL, rule groups, IP sets, regex pattern sets, logging configuration, and resource associations) for protecting web applications against common exploits and unwanted Layer 7 traffic
- **Service**: AWS WAF (AWS Web Application Firewall) v2
- **Category**: Security, Networking, Firewall
- **Keywords**: waf, wafv2, web-application-firewall, web-acl, firewall, rate-limiting, managed-rules, owasp, bot-control, ip-set, regex-pattern-set, rule-group, cloudfront, alb, api-gateway, ddos-protection, layer7
- **Use For**: web application firewall protection, blocking OWASP Top 10 exploits (SQL injection, XSS), rate limiting and DDoS mitigation, bot control, geo-blocking, IP allow/deny lists, ALB/CloudFront/API Gateway protection, AWS managed rule groups, custom rule authoring, request logging to Kinesis Firehose/CloudWatch/S3

## Description

AWS WAF v2 is a web application firewall that protects HTTP(S) applications against common web exploits, malicious bots, and volumetric Layer 7 attacks by inspecting incoming requests against a configurable set of rules. This Terraform module creates and wires together the resources that make up a working deployment: a Web ACL (the root resource that holds the ordered list of rules and the default action), the rules themselves (custom rules plus references to AWS-managed and custom rule groups), IP sets and regex pattern sets used as reusable match conditions, an optional logging configuration, and the associations that attach a Web ACL to protected resources such as an Application Load Balancer, API Gateway stage, AppSync API, Cognito user pool, or (in `CLOUDFRONT` scope) a CloudFront distribution.

The root module builds a single `aws_wafv2_web_acl` from a declarative `rules` map, where each entry describes a rule's priority, action (allow / block / count / captcha / challenge), statement (rate-based, geo-match, IP-set reference, byte-match, SQLi/XSS match, or a managed/custom rule-group reference), and per-rule visibility configuration. A `scope` argument selects between `REGIONAL` (ALB, API Gateway, AppSync, Cognito, App Runner) and `CLOUDFRONT` (global edge) deployments. For advanced or generated configurations a `rule_json` escape hatch accepts a raw JSON rules document, and `custom_response_bodies`, `captcha_config`, `challenge_config`, and `association_config` cover custom responses, CAPTCHA/challenge immunity, and per-resource body-inspection size limits.

Around the root Web ACL the module ships eight composable submodules — `ip-set`, `regex-pattern-set`, `rule-group`, `logging-configuration`, `web-acl-association`, `web-acl-rule`, `web-acl-rule-group-association`, and `api-key` — each wrapping a single WAF v2 resource so that IP sets, regex sets, custom rule groups, and associations can be created and shared independently of the Web ACL lifecycle. The module supports request logging to Amazon Kinesis Data Firehose, CloudWatch Log Groups, or S3 (with redacted fields and logging filters), CloudWatch visibility metrics per rule, and consistent tagging across all resources, making it a building block for defense-in-depth application security on AWS.

## Key Features

- **Declarative Web ACL Rules**: Author the ordered rule set through a single `rules` map keyed by rule name, each with priority, action, statement, and visibility configuration
- **Eight Composable Submodules**: `ip-set`, `regex-pattern-set`, `rule-group`, `logging-configuration`, `web-acl-association`, `web-acl-rule`, `web-acl-rule-group-association`, and `api-key` for independent lifecycle management
- **AWS Managed Rule Groups**: Reference AWS-managed rule groups (Core rule set, Known Bad Inputs, SQL database, Bot Control, Account Takeover Prevention, IP reputation) with per-rule overrides
- **Rate-Based Rules**: Throttle abusive clients by request rate, with aggregation by IP, forwarded IP, or custom keys for DDoS and brute-force mitigation
- **Managed & Custom Statements**: SQL-injection and XSS match, byte/size-constraint match, geo-match, IP-set reference, regex-pattern-set reference, label-match, and rule-group references
- **Dual Scope**: `REGIONAL` scope for ALB / API Gateway / AppSync / Cognito / App Runner and `CLOUDFRONT` scope for global edge protection
- **Reusable IP Sets & Regex Sets**: Create allow/deny IP sets (IPv4/IPv6) and regex pattern sets once and reference them across multiple rules
- **Custom Rule Groups**: Build reusable `aws_wafv2_rule_group` bundles with their own WCU capacity and reference them from Web ACLs
- **CAPTCHA & Challenge Actions**: Enforce CAPTCHA puzzles or silent challenges with configurable immunity times to separate humans from bots
- **Bot Control & Fraud Prevention**: Integrate AWS Bot Control and Account Takeover Prevention (ATP) managed groups, with an SDK integration URL output
- **Custom Responses**: Define custom response bodies and per-rule custom response status codes for blocked requests
- **Request Logging**: Stream inspected requests to Kinesis Data Firehose, CloudWatch Logs, or S3 with logging filters and redacted fields for sensitive data
- **Resource Associations**: Attach the Web ACL to ALBs, API Gateway stages, AppSync APIs, Cognito user pools, and more via `association_resource_arns` or the `web-acl-association` submodule
- **JSON Escape Hatch**: Supply a raw `rule_json` document for complex or externally generated rule sets that outgrow the typed `rules` map
- **Data Protection & Token Domains**: Configure data protection for logged fields and accepted token domains for challenge/CAPTCHA cookies
- **Conditional Creation**: A `create` flag on the root module and every submodule for environment-specific toggling
- **Comprehensive Tagging**: Consistent tagging across the Web ACL, IP sets, regex sets, rule groups, and logging configuration

## Main Use Cases

1. **Web Application Protection**: Block common exploits from the OWASP Top 10, including SQL injection and cross-site scripting
2. **Rate Limiting & DDoS Mitigation**: Throttle abusive clients and absorb volumetric Layer 7 floods with rate-based rules
3. **Bot Control**: Detect and manage scrapers, crawlers, and automated abuse with AWS Bot Control managed rules
4. **Managed Rule Deployment**: Roll out AWS-managed rule groups (Core rule set, Known Bad Inputs, IP reputation) with minimal configuration
5. **IP Allow/Deny Lists**: Enforce IP-based access control using reusable IPv4/IPv6 IP sets
6. **Geo-Blocking**: Allow or block traffic by country using geo-match statements for compliance or licensing
7. **API Gateway & ALB Protection**: Attach a regional Web ACL to REST/HTTP APIs and Application Load Balancers
8. **CloudFront Edge Protection**: Deploy a `CLOUDFRONT`-scoped Web ACL to filter traffic at the global edge
9. **Account Takeover Prevention**: Protect login endpoints with the ATP managed rule group and credential-stuffing detection
10. **Security Monitoring & Compliance**: Log inspected requests to Firehose/CloudWatch/S3 and emit CloudWatch metrics for auditing and alerting

## Usage Examples

### Example 1: Regional Web ACL for an ALB with AWS managed rules and rate limiting

```hcl
module "waf" {
  source  = "terraform-aws-modules/wafv2/aws"
  version = "~> 2.0"

  name  = "app-regional-acl"
  scope = "REGIONAL"

  default_action = "allow"

  rules = {
    aws-common = {
      name     = "aws-common-rule-set"
      priority = 1
      override_action = "none"

      statement = {
        managed_rule_group_statement = {
          name        = "AWSManagedRulesCommonRuleSet"
          vendor_name = "AWS"
        }
      }

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "aws-common-rule-set"
        sampled_requests_enabled   = true
      }
    }

    rate-limit = {
      name     = "rate-limit"
      priority = 2
      action   = "block"

      statement = {
        rate_based_statement = {
          limit              = 2000
          aggregate_key_type = "IP"
        }
      }

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "rate-limit"
        sampled_requests_enabled   = true
      }
    }
  }

  # Attach to an Application Load Balancer
  association_resource_arns = {
    alb = aws_lb.this.arn
  }

  visibility_config = {
    cloudwatch_metrics_enabled = true
    metric_name                = "app-regional-acl"
    sampled_requests_enabled   = true
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 2: CloudFront-scoped Web ACL with an IP deny list and logging

```hcl
module "waf_blocklist" {
  source  = "terraform-aws-modules/wafv2/aws//modules/ip-set"
  version = "~> 2.0"

  name               = "blocked-ips"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = ["192.0.2.0/24", "198.51.100.44/32"]
}

module "waf" {
  source  = "terraform-aws-modules/wafv2/aws"
  version = "~> 2.0"

  name  = "edge-acl"
  scope = "CLOUDFRONT" # must be provisioned in us-east-1

  default_action = "allow"

  rules = {
    block-ips = {
      name     = "block-ips"
      priority = 1
      action   = "block"

      statement = {
        ip_set_reference_statement = {
          arn = module.waf_blocklist.aws_wafv2_ip_set_arn
        }
      }

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "block-ips"
        sampled_requests_enabled   = true
      }
    }
  }

  create_logging_configuration    = true
  logging_log_destination_configs = [aws_kinesis_firehose_delivery_stream.waf.arn]

  visibility_config = {
    cloudwatch_metrics_enabled = true
    metric_name                = "edge-acl"
    sampled_requests_enabled   = true
  }
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `null` | Friendly name of the Web ACL (mutually exclusive with `name_prefix`) |
| `name_prefix` | `string` | `null` | Creates a unique name beginning with this prefix |
| `scope` | `string` | `"REGIONAL"` | `REGIONAL` (ALB/API Gateway/AppSync/Cognito) or `CLOUDFRONT` (global edge; provision in us-east-1) |
| `default_action` | `any` | `"allow"` | Action when no rule matches: `allow` or `block` |
| `rules` | `any` | `{}` | Map of rule configurations keyed by rule name (priority, action, statement, visibility) — see the `web-acl-rule` submodule for the typed shape |
| `rule_json` | `string` | `null` | Escape hatch: raw JSON string of WAF rules for complex/generated configurations |
| `visibility_config` | `object` | `{}` | CloudWatch metrics + sampled-requests configuration for the Web ACL — fields: `cloudwatch_metrics_enabled`, `metric_name`, `sampled_requests_enabled` |
| `custom_response_bodies` | `map(object)` | `{}` | Map of custom response body configurations referenced by blocking rules — fields: `content`, `content_type` |
| `captcha_config` | `object` | `null` | CAPTCHA immunity-time configuration for the Web ACL — fields: `immunity_time_property` |
| `challenge_config` | `object` | `null` | Challenge immunity-time configuration for the Web ACL — fields: `immunity_time_property` |
| `association_config` | `map(object)` | `{}` | Per-resource-type request body inspection size limits |
| `token_domains` | `list(string)` | `[]` | Domains AWS WAF should accept in challenge/CAPTCHA request tokens |
| `association_resource_arns` | `map(string)` | `{}` | Map of resource ARNs (ALB, API Gateway, etc.) to associate with the Web ACL |
| `create_logging_configuration` | `bool` | `false` | Controls creation of the Web ACL logging configuration |
| `logging_log_destination_configs` | `list(string)` | `[]` | Kinesis Firehose, CloudWatch Log Group, or S3 bucket ARNs for request logging |
| `logging_filter` | `object` | `null` | Filter specifying which requests are kept in the logs — fields: `default_behavior`, `filters` |
| `logging_redacted_fields` | `list(object)` | `[]` | Request fields to keep out of the logs |
| `data_protection_config` | `any` | `null` | Data protection configuration for sensitive logged fields |
| `description` | `string` | `null` | Friendly description of the Web ACL |
| `tags` | `map(string)` | `{}` | Map of tags to add to all resources |
| `create` | `bool` | `true` | Controls whether resources are created |

## Main Outputs

| Output | Description |
|--------|-------------|
| `web_acl_id` | The ID of the Web ACL |
| `web_acl_arn` | The ARN of the Web ACL (use to associate resources) |
| `web_acl_name` | The name of the Web ACL |
| `web_acl_capacity` | Web ACL capacity units (WCUs) currently consumed |
| `web_acl_lock_token` | Token used for optimistic locking |
| `web_acl_application_integration_url` | URL for SDK integrations with managed rule groups (Bot Control / ATP) |
| `web_acl_association_ids` | Map of Web ACL association IDs |
| `web_acl_rule_names` | List of rule names in the Web ACL |
| `web_acl_visibility_config` | The visibility configuration of the Web ACL |
| `logging_configuration_id` | The ID of the WAF logging configuration |

## Submodules

### 1. ip-set

- **Purpose**: Creates an `aws_wafv2_ip_set` — a reusable list of IPv4/IPv6 CIDRs referenced by IP-set-reference rule statements
- **Source**: `terraform-aws-modules/wafv2/aws//modules/ip-set`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/wafv2/aws/latest/submodules/ip-set
- **Key Features**: IPv4/IPv6 address versions, allow/deny lists, scope-aware (REGIONAL/CLOUDFRONT), shared across Web ACLs
- **Use Cases**: IP allow/deny lists, blocking known-bad IP ranges, allow-listing office/partner networks

### 2. regex-pattern-set

- **Purpose**: Creates an `aws_wafv2_regex_pattern_set` — a reusable set of regular expressions referenced by regex-match rule statements
- **Source**: `terraform-aws-modules/wafv2/aws//modules/regex-pattern-set`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/wafv2/aws/latest/submodules/regex-pattern-set
- **Key Features**: Multiple regex strings per set, scope-aware, reusable across rules and Web ACLs
- **Use Cases**: Matching URI/header/query patterns, blocking suspicious user agents, path-based filtering

### 3. rule-group

- **Purpose**: Creates a custom `aws_wafv2_rule_group` — a reusable bundle of rules with its own WCU capacity, referenced from Web ACLs
- **Source**: `terraform-aws-modules/wafv2/aws//modules/rule-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/wafv2/aws/latest/submodules/rule-group
- **Key Features**: Custom rule bundles, dedicated WCU capacity, reusable across multiple Web ACLs, per-rule visibility metrics
- **Use Cases**: Standardized org-wide rule bundles, sharing common rule sets across applications, modular rule management

### 4. logging-configuration

- **Purpose**: Creates an `aws_wafv2_web_acl_logging_configuration` decoupled from the Web ACL lifecycle
- **Source**: `terraform-aws-modules/wafv2/aws//modules/logging-configuration`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/wafv2/aws/latest/submodules/logging-configuration
- **Key Features**: Kinesis Firehose / CloudWatch / S3 destinations, logging filters, redacted fields
- **Use Cases**: Centralized WAF request logging, compliance auditing, redacting sensitive fields from logs

### 5. web-acl-association

- **Purpose**: Creates an `aws_wafv2_web_acl_association` attaching a Web ACL to a regional resource (ALB, API Gateway, AppSync, Cognito)
- **Source**: `terraform-aws-modules/wafv2/aws//modules/web-acl-association`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/wafv2/aws/latest/submodules/web-acl-association
- **Key Features**: Regional resource attachment, independent association lifecycle, works with externally managed Web ACLs
- **Use Cases**: Attaching a shared Web ACL to multiple ALBs/APIs, decoupling association from Web ACL creation

### 6. web-acl-rule

- **Purpose**: Creates an individual `aws_wafv2_web_acl_rule` for managing a single rule outside the root `rules` map
- **Source**: `terraform-aws-modules/wafv2/aws//modules/web-acl-rule`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/wafv2/aws/latest/submodules/web-acl-rule
- **Key Features**: Single-rule granularity, independent lifecycle, composable with an externally managed Web ACL
- **Use Cases**: Adding rules to a Web ACL managed elsewhere, per-team rule ownership, incremental rule rollout

### 7. web-acl-rule-group-association

- **Purpose**: Creates an `aws_wafv2_web_acl_rule_group_association` binding a custom rule group into a Web ACL
- **Source**: `terraform-aws-modules/wafv2/aws//modules/web-acl-rule-group-association`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/wafv2/aws/latest/submodules/web-acl-rule-group-association
- **Key Features**: Attaches a custom rule group to a Web ACL, priority/override control, independent lifecycle
- **Use Cases**: Wiring shared rule groups into multiple Web ACLs, decoupled rule-group management

### 8. api-key

- **Purpose**: Creates an `aws_wafv2_api_key` used by the WAF integration SDK for CAPTCHA/challenge client-side integration
- **Source**: `terraform-aws-modules/wafv2/aws//modules/api-key`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/wafv2/aws/latest/submodules/api-key
- **Key Features**: Token-domain-scoped API keys, scope-aware, used with the JavaScript integration SDK
- **Use Cases**: Client-side CAPTCHA/challenge integration, single-page-app WAF token issuance

## Best Practices

### Rule Design and Ordering

1. **Start in Count Mode**: Deploy new rules with the `count` action first and inspect sampled requests/metrics before switching to `block` to avoid false positives.
2. **Order by Priority Deliberately**: Lower `priority` numbers evaluate first — place high-confidence deny rules (IP blocklists, geo-blocks) before broad managed rule groups.
3. **Layer Managed Rule Groups**: Combine `AWSManagedRulesCommonRuleSet`, `AWSManagedRulesKnownBadInputsRuleSet`, and `AWSManagedRulesAmazonIpReputationList` as a baseline, then add app-specific custom rules.
4. **Watch WCU Capacity**: Each Web ACL has a 1500 WCU budget — check `web_acl_capacity` and consolidate rules or use rule groups when approaching the limit.

### Rate Limiting and Bot Control

1. **Tune Rate Limits per Endpoint**: Set rate-based limits appropriate to legitimate traffic; use scope-down statements to apply limits only to sensitive paths (e.g., `/login`).
2. **Protect Login Flows**: Add the Account Takeover Prevention (ATP) managed group and challenge actions to authentication endpoints.
3. **Use Challenge Before Block**: Prefer `challenge`/`captcha` actions over hard `block` for suspected bots to reduce impact on legitimate users.

### Logging and Monitoring

1. **Enable Request Logging**: Set `create_logging_configuration = true` with a Kinesis Firehose or CloudWatch destination for forensics and tuning.
2. **Redact Sensitive Fields**: Use `logging_redacted_fields` to keep authorization headers and cookies out of logs.
3. **Filter Noise**: Use `logging_filter` to log only blocked/counted requests when volume or cost is a concern.
4. **Alarm on CloudWatch Metrics**: Enable `cloudwatch_metrics_enabled` per rule and alarm on blocked-request spikes.

### Scope and Deployment

1. **Provision CLOUDFRONT ACLs in us-east-1**: `CLOUDFRONT`-scoped Web ACLs and their IP/regex sets must be created in the `us-east-1` region.
2. **Reuse IP and Regex Sets**: Create IP sets and regex pattern sets via submodules once and reference them across Web ACLs to keep conditions DRY.
3. **Decouple Associations**: Use the `web-acl-association` submodule when the Web ACL and the protected resource are managed in separate stacks.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-wafv2
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/wafv2/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-wafv2/tree/master/examples
- **AWS WAF Documentation**: https://docs.aws.amazon.com/waf/latest/developerguide/waf-chapter.html
- **AWS Managed Rule Groups**: https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-list.html
- **WAF Bot Control**: https://docs.aws.amazon.com/waf/latest/developerguide/waf-bot-control.html
- **Rate-Based Rules**: https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-statement-type-rate-based.html
- **aws_wafv2_web_acl Resource**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/wafv2_web_acl
- **AWS WAF Pricing**: https://aws.amazon.com/waf/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Choose Scope Deliberately**: Use `REGIONAL` for ALB/API Gateway/AppSync/Cognito/App Runner and `CLOUDFRONT` for CloudFront distributions — `CLOUDFRONT` resources must be created in `us-east-1`.
2. **Roll Out in Count Mode**: Deploy new or managed rules with the `count` action first; only switch to `block` after reviewing sampled requests and CloudWatch metrics.
3. **Mind WCU Capacity**: The Web ACL has a 1500 WCU limit; check the `web_acl_capacity` output and offload rules into custom rule groups if needed.
4. **Associate via ARN**: Attach protected resources with `association_resource_arns` (a map of friendly key → resource ARN) or the `web-acl-association` submodule; the `web_acl_arn` output is the association target.
5. **Enable Logging Early**: Set `create_logging_configuration = true` with a Firehose/CloudWatch/S3 destination and redact sensitive fields for compliance and tuning.
6. **Prefer the Typed `rules` Map**: Use the structured `rules` map for maintainability; fall back to `rule_json` only for complex or externally generated configurations.
7. **Reuse Match Conditions**: Create `ip-set` and `regex-pattern-set` submodules once and reference their ARNs from multiple rules and Web ACLs.
8. **Use Challenge/CAPTCHA for Bots**: Prefer `challenge` or `captcha` actions over hard blocks to reduce false-positive impact on legitimate users.
9. **Verify Managed Rule Names**: Confirm exact managed rule group names and vendor via `grep_module_docs` or the AWS managed-rules documentation before pinning them in rules.
10. **Pin the Module Version**: Use an explicit `version = "~> 2.0"` (latest `2.1.0`) constraint for reproducible deployments.
11. **`override_action` vs `action` Are Mutually Exclusive**: a rule whose `statement` is a `managed_rule_group_statement` or a `rule_group_reference_statement` takes `override_action` (`"none"` or `"count"` — see the `aws-common` rule in Example 1, which sets `override_action = "none"` on a `managed_rule_group_statement`); a rule with a standalone match statement (`rate_based_statement`, `ip_set_reference_statement`, byte-match, geo-match, etc.) takes `action` instead (`"allow"`/`"block"`/`"count"`/`"captcha"`/`"challenge"` — see `rate-limit` in Example 1 and `block-ips` in Example 2, both of which set `action` on a non-rule-group statement). Setting both, or setting the wrong one for the statement type, is rejected by the WAF v2 API.
