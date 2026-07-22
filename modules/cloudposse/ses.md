# Terraform AWS SES Module

## Module Information

- **Module Name**: `ses`
- **Module ID**: `cloudposse/ses/aws`
- **Source**: `cloudposse/ses/aws`
- **GitHub Repository**: https://github.com/cloudposse/terraform-aws-ses
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/ses/aws/latest
- **Latest Version**: 0.25.2
- **Purpose**: Terraform module that provisions an AWS SES (Simple Email Service) domain identity together with an IAM user/group for sending, and optionally creates the Route 53 DNS records needed for domain, DKIM, and SPF verification plus a custom MAIL FROM subdomain
- **Service**: AWS SES (Simple Email Service)
- **Category**: Messaging, Security
- **Keywords**: ses, simple-email-service, email, smtp, dkim, spf, domain-identity, transactional-email, mail-from, route53, dns-verification, iam-user, smtp-credentials, sender-authentication, email-sending, cloudposse
- **Use For**: transactional email sending, marketing/notification email deliverability setup, verified sending domains for SaaS applications, DKIM/SPF-authenticated outbound mail, custom MAIL FROM bounce-domain alignment, per-environment SES identities, automated SMTP credential provisioning, least-privilege IAM policies for email sending, Route53-automated domain verification, multi-tenant transactional email platforms

## Description

This Cloud Posse module provisions an AWS SES (Simple Email Service) domain identity (`aws_ses_domain_identity`) and its DKIM configuration (`aws_ses_domain_dkim`), and — when a Route 53 hosted zone is supplied — the DNS records needed to verify that identity: a TXT record proving domain ownership, three CNAME records for DKIM, an optional SPF TXT record, and an optional custom MAIL FROM subdomain (`aws_ses_domain_mail_from`) with its matching MX record. Alongside the identity, it optionally provisions an IAM user (via the `cloudposse/iam-system-user/aws` submodule) and/or IAM group whose policy is scoped to sending email only from the domain identity this module creates, plus an SES SMTP username/password pair (via the `cloudposse/awsutils` provider) so applications get ready-to-use SMTP credentials rather than just an SES API identity.

SES requires proving domain ownership and, for good inbox placement, publishing DKIM/SPF DNS records; doing this by hand for every environment is repetitive and error-prone. The module gates all Route 53 record creation behind a single `zone_id` input, so a project can adopt SES incrementally — create the identity now and wire up verification once the hosted zone is known, or fully automate verification end-to-end when the zone is also Terraform-managed. It builds on Cloud Posse's `null-label` naming/tagging convention (`context`/`namespace`/`stage`/`name`/`tags`), so multiple SES identities — one per environment, tenant, or application — get consistent, collision-free IAM resource names and tags.

Identity creation, DNS verification, and IAM credential provisioning are three independently toggleable concerns: `ses_user_enabled`/`ses_group_enabled` control the IAM side, `verify_domain`/`verify_dkim`/`create_spf_record` control which Route 53 records get created, and `custom_from_subdomain` opts into a dedicated MAIL FROM domain for bounce/complaint handling. Every AWS account starts SES in a sending "sandbox" — this module does not, and cannot, request production access; that remains a manual AWS Support step.

## Key Features

- **SES Domain Identity**: Creates the `aws_ses_domain_identity` root resource that SES sending is authorized against
- **DKIM Signing**: Enables `aws_ses_domain_dkim` and, when `verify_dkim = true`, publishes the three required CNAME tokens to Route 53
- **Domain Ownership Verification**: When `verify_domain = true`, publishes the `_amazonses.<domain>` TXT record Route 53 needs to prove ownership
- **SPF Record**: Optional `create_spf_record` publishes a `v=spf1 include:amazonses.com -all` TXT record for the sending (or custom MAIL FROM) domain
- **Custom MAIL FROM Subdomain**: `custom_from_subdomain` creates `aws_ses_domain_mail_from` plus its MX record, aligning the bounce/complaint domain with the sending domain for better deliverability
- **MX-Failure Behavior Control**: `custom_from_behavior_on_mx_failure` selects `UseDefaultValue` or `RejectMessage` if the custom MAIL FROM MX record is missing
- **IAM Sending User**: Optional IAM user (via `cloudposse/iam-system-user/aws`) scoped to sending email through this domain identity
- **IAM Sending Group**: Optional IAM group with a shared sending policy, so multiple users/roles can be attached without duplicating the policy
- **Least-Privilege IAM Policy**: The generated policy's `resources` defaults to just the created domain identity ARN, extendable via `iam_allowed_resources`
- **Configurable IAM Actions**: `iam_permissions` defaults to `["ses:SendRawEmail"]` but accepts any SES IAM action
- **SES SMTP Credential Generation**: Derives an SES SMTP username/password pair from the IAM access key via the `awsutils` provider — no manual SigV4 conversion needed
- **Optional Credential Material**: `iam_create_access_key`/`iam_create_ses_smtp_password` let you provision the IAM user without writing key material to state
- **Cloud Posse Context/Label Convention**: `namespace`/`environment`/`stage`/`name`/`attributes`/`tenant`/`tags`/`context` drive consistent, collision-free resource naming and tagging
- **Conditional Creation**: A module-wide `enabled` flag (via `context`) toggles every resource for environment-specific rollout
- **Route53 Automation Opt-In**: All Route 53 record creation is gated behind a non-empty `zone_id`, so identity creation and DNS verification can be adopted independently
- **Region-Aware MX Target**: Uses `data.aws_region.current` to build the correct `feedback-smtp.<region>.amazonses.com` MX target for the custom MAIL FROM domain

## Main Use Cases

1. **Transactional Email Sending**: Send receipts, password resets, and notifications from application backends via SES SMTP or API
2. **Sending Domain Verification**: Verify a company or product domain for SES and publish its DKIM keys in one apply
3. **Deliverability Hardening**: Align SPF and a custom MAIL FROM subdomain with the sending domain to reduce spam-folder placement
4. **Per-Environment Email Identities**: Provision separate SES identities and SMTP credentials per `namespace`/`stage` (dev/staging/prod)
5. **Automated Application Credentials**: Generate an IAM user, access key, and SES SMTP password ready to drop into application configuration/secrets
6. **Least-Privilege Sending IAM**: Restrict an application's IAM policy to `ses:SendRawEmail` against a single domain identity ARN
7. **Route53-Managed Verification**: Fully automate domain + DKIM + SPF verification when the sending domain's hosted zone is Terraform-managed
8. **Shared Sending Group**: Attach multiple existing IAM users to one SES-sending IAM group instead of duplicating the sending policy
9. **Migrating Off Third-Party ESPs**: Stand up an SES SMTP endpoint and credentials as a drop-in relay for apps already speaking SMTP

## Usage Examples

### Example 1: Minimal — SES identity with an IAM sending user (no Route53 verification)

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    awsutils = {
      source  = "cloudposse/awsutils"
      version = ">= 0.11.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Required even when SMTP credentials are not used directly: the module's
# child modules declare this provider unconditionally.
provider "awsutils" {
  region = "us-east-1"
}

module "ses" {
  source  = "cloudposse/ses/aws"
  version = "0.25.2"

  namespace = "eg"
  stage     = "prod"
  name      = "notifications"

  domain = "mail.example.com"

  # zone_id left at its default ("") -- no Route53 records are created,
  # so the identity stays "pending verification" until you publish the
  # aws_ses_domain_identity_verification_token/ses_dkim_tokens outputs
  # (or the equivalent records) with your DNS provider.
}

output "ses_smtp_username" {
  value = module.ses.access_key_id
}

output "ses_smtp_password" {
  value     = module.ses.ses_smtp_password
  sensitive = true
}
```

### Example 2: Complete — Route53-verified domain with DKIM, SPF, and a custom MAIL FROM domain

```hcl
resource "aws_route53_zone" "mail" {
  name = "mail.example.com"
}

module "ses" {
  source  = "cloudposse/ses/aws"
  version = "0.25.2"

  namespace = "eg"
  stage     = "prod"
  name      = "notifications"

  domain  = "mail.example.com"
  zone_id = aws_route53_zone.mail.zone_id

  verify_domain     = true
  verify_dkim       = true
  create_spf_record = true

  # Dedicated bounce/complaint domain, aligned with the sending domain
  custom_from_subdomain          = ["bounce"]
  custom_from_dns_record_enabled = true

  iam_permissions = ["ses:SendRawEmail", "ses:SendEmail"]

  tags = {
    Environment = "prod"
    Team        = "platform"
  }
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `domain` | `string` | n/a (required) | The domain to create the SES identity for |
| `zone_id` | `string` | `""` | Route53 parent zone ID; if non-empty, the module creates the Route53 DNS records used for verification |
| `verify_domain` | `bool` | `false` | If `true`, creates the Route53 TXT record used for domain ownership verification (requires `zone_id`) |
| `verify_dkim` | `bool` | `false` | If `true`, creates the three Route53 CNAME records used for DKIM verification (requires `zone_id`) |
| `create_spf_record` | `bool` | `false` | If `true`, creates a Route53 SPF TXT record for `domain` (or the custom MAIL FROM domain, if set) |
| `custom_from_subdomain` | `list(string)` | `[]` | If provided (single-element list), creates a custom MAIL FROM subdomain for the `From` address |
| `custom_from_dns_record_enabled` | `bool` | `true` | If enabled, creates the Route53 MX record required by the custom MAIL FROM subdomain |
| `custom_from_behavior_on_mx_failure` | `string` | `"UseDefaultValue"` | Behavior of the custom MAIL FROM subdomain when its MX record is not found: `UseDefaultValue` or `RejectMessage` |
| `ses_user_enabled` | `bool` | `true` | Creates an IAM user with permission to send email from the SES domain |
| `ses_group_enabled` | `bool` | `true` | Creates an IAM group with permission to send email from the SES domain |
| `ses_group_name` | `string` | `""` | Name of the IAM group to create; if empty, calculated from `context` (recommended) |
| `ses_group_path` | `string` | `"/"` | The IAM path of the group to create |
| `iam_permissions` | `list(string)` | `["ses:SendRawEmail"]` | IAM actions granted to the sending user/group |
| `iam_allowed_resources` | `list(string)` | `[]` | Additional resource ARNs (wildcards accepted) enabled for `iam_permissions`, beyond the created domain identity |
| `iam_create_access_key` | `bool` | `true` | Create an AWS IAM access key, stored in Terraform state (not recommended for long-lived state without encryption) |
| `iam_create_ses_smtp_password` | `bool` | `true` | Create an SES SMTP password (derived via the `awsutils` provider), stored in Terraform state |
| `enabled` | `bool` | `null` | Set to `false` to prevent the module from creating any resources |
| `namespace` | `string` | `null` | ID element — usually an abbreviation of your organization name (Cloud Posse label convention) |
| `stage` | `string` | `null` | ID element — usually `prod`, `staging`, `dev`, etc. (Cloud Posse label convention) |
| `name` | `string` | `null` | ID element — usually the component or solution name, e.g. `notifications` |
| `environment` | `string` | `null` | ID element — usually a region or role abbreviation (Cloud Posse label convention) |
| `attributes` | `list(string)` | `[]` | ID element — additional attributes appended to `id` (Cloud Posse label convention) |
| `tags` | `map(string)` | `{}` | Additional tags; neither keys nor values are modified by the module |
| `context` | `any` | `{ "enabled": true, "namespace": null, "stage": null, "name": null, ... }` | Single object for setting the entire Cloud Posse label context at once — see the `namespace`/`stage`/`name`/`tags` inputs above for the individual fields it bundles; non-null individual variables override the corresponding `context` field |

## Main Outputs

| Output | Description |
|--------|-------------|
| `ses_domain_identity_arn` | The ARN of the SES domain identity |
| `ses_domain_identity_verification_token` | The code to add as a TXT record to verify domain ownership (needed if you manage DNS outside this module) |
| `ses_dkim_tokens` | The three DKIM tokens to add as CNAME records for DKIM verification (needed if you manage DNS outside this module) |
| `spf_record` | The FQDN of the created SPF TXT record |
| `custom_from_domain` | The custom MAIL FROM domain, if `custom_from_subdomain` is set |
| `ses_group_name` | The IAM group name |
| `user_name` | Normalized IAM user name |
| `user_arn` | The ARN assigned by AWS for the IAM user |
| `user_unique_id` | The unique ID assigned by AWS for the IAM user |
| `access_key_id` | The SMTP username (IAM access key ID) |
| `secret_access_key` | The IAM secret access key; sensitive, written to state in plain text |
| `ses_smtp_password` | The SES SMTP password derived from the IAM secret; sensitive, written to state in plain text |

## Best Practices

### Domain Verification and Deliverability

1. **Verify Both Domain and DKIM**: Set `verify_domain = true` and `verify_dkim = true` together — DKIM-only verification still leaves the domain identity in "pending verification".
2. **Align a Custom MAIL FROM Domain**: Set `custom_from_subdomain` and `create_spf_record = true` so bounce/complaint handling and SPF both reference a domain you control, improving inbox placement.
3. **Expect DNS Propagation Delay**: Domain and DKIM verification are asynchronous after `apply` — AWS can take minutes up to 72 hours to detect published records; do not gate a deploy pipeline on immediate `verified` status.
4. **Check Regional Availability**: SES is not available in every AWS region — confirm in the AWS General Reference before picking a region for the identity.

### Sandbox and Production Access

1. **Plan for Sandbox by Default**: Every new AWS account's SES starts in the sandbox — sending is restricted to verified recipient addresses/domains until AWS approves a production-access request. This module cannot request that access; file it via AWS Support before relying on unrestricted sending.
2. **Verify Recipients in Sandbox Testing**: While in the sandbox, verify test recipient addresses in the SES console/API so pre-production `terraform apply` runs can exercise real sends.

### Security and Credential Management

1. **Scope IAM to This Identity**: Leave `iam_allowed_resources` empty unless another SES identity genuinely needs to share the sending policy — the default already scopes to the domain identity this module creates.
2. **Treat State as Sensitive**: `secret_access_key` and `ses_smtp_password` are written to Terraform state in plain text even though they are marked `sensitive` in output; use encrypted remote state with restricted access, not local state files.
3. **Skip Access Keys When Not Needed**: Set `iam_create_access_key = false` and `iam_create_ses_smtp_password = false` if the sending application authenticates via an attached IAM role instead of long-lived SMTP credentials.

### Multi-Environment Naming

1. **Use `namespace`/`stage`/`environment` Consistently**: Let the Cloud Posse label convention (or a shared `context` object) generate distinct, collision-free IAM user/group names per environment instead of hand-rolled naming.
2. **One Identity per Environment**: Provision a separate module call (and typically a separate subdomain) per `stage` so a dev/staging mistake cannot affect the production sending domain's reputation.

## Additional Resources

- **Module Repository**: https://github.com/cloudposse/terraform-aws-ses
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/ses/aws/latest
- **Module Example**: https://github.com/cloudposse/terraform-aws-ses/tree/main/examples/complete
- **AWS SES Developer Guide**: https://docs.aws.amazon.com/ses/latest/dg/Welcome.html
- **Moving Out of the SES Sandbox**: https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html
- **SES Domain Verification (DKIM)**: https://docs.aws.amazon.com/ses/latest/dg/send-email-authentication-dkim.html
- **SES Custom MAIL FROM Domain**: https://docs.aws.amazon.com/ses/latest/dg/mail-from.html
- **SES SMTP Credentials**: https://docs.aws.amazon.com/ses/latest/dg/smtp-credentials.html
- **SES Region Availability**: https://docs.aws.amazon.com/general/latest/gr/ses.html
- **Cloud Posse `null-label` Module (context/label convention)**: https://github.com/cloudposse/terraform-null-label
- **`awsutils` Provider**: https://registry.terraform.io/providers/cloudposse/awsutils/latest

## Important Gotchas

- **Domain/DKIM Verification Is Required Before Sending**: Creating the SES identity does not make it usable — `verify_domain`/`verify_dkim` (or manually publishing the `ses_domain_identity_verification_token`/`ses_dkim_tokens` outputs with your DNS provider) must complete before AWS will accept mail from the domain, and even then the account remains sandboxed until AWS grants production access.
- **`zone_id` Wiring Gates All DNS Automation**: `verify_domain`, `verify_dkim`, and `create_spf_record` all write directly to `zone_id` — if it is left at the default `""` while those flags are `true`, `apply` fails on an invalid/empty Route53 zone. `zone_id` must be the hosted zone that actually serves the `domain` (or its parent), not an unrelated zone.
- **Requires a Second Provider (`awsutils`)**: This module's `required_providers` includes `cloudposse/awsutils` (>= 0.11.0) in addition to `hashicorp/aws` — it is used to derive the SES SMTP password from the IAM secret access key. A caller that only configures the `aws` provider will fail with a missing-provider-configuration error; add an `awsutils` provider block (see Example 1) even if you plan to disable SMTP password creation later.
- **Secrets Land in State**: `secret_access_key` and `ses_smtp_password` are marked `sensitive` but are still written to Terraform state in plain text (per their own descriptions) — protect state storage accordingly, or set `iam_create_access_key`/`iam_create_ses_smtp_password` to `false` if the consuming application uses an IAM role instead.
- **`custom_from_subdomain` Takes Only One Value**: The variable is typed `list(string)` but the module reads only its first element (`one(var.custom_from_subdomain)`); passing more than one entry raises an error at plan time.
- **Sandbox Applies to Recipients Too**: Until AWS approves production access, SES rejects mail to any recipient address/domain that is not itself verified — a working `apply` does not imply a test email will actually deliver.

## Notes for AI Agents

When using this module in automated workflows:

1. **Cloud Posse Namespace and Convention**: This module is published by Cloud Posse (namespace `cloudposse`), not the `terraform-aws-modules` org. It uses Cloud Posse's `context`/`label` convention — inputs like `namespace`, `stage`, `name`, `environment`, `tenant`, `attributes`, `tags` and a `context` object drive resource naming/tagging across every Cloud Posse module. Do NOT propagate this convention onto other (differently-styled) modules in the same project; set the label inputs this module needs and leave other vendors' modules alone.
2. **Always Configure the `awsutils` Provider**: Add a `provider "awsutils" {}` block alongside `aws` (see Example 1) — its absence is a common apply-time failure for this module, independent of which optional features are enabled.
3. **Gate Verification on `zone_id`**: Only set `verify_domain`/`verify_dkim`/`create_spf_record` to `true` once a real `zone_id` for the sending domain's hosted zone is available; setting them against the default empty `zone_id` breaks the apply.
4. **Do Not Assume Immediate Sendability**: After `apply`, treat the identity as "verification pending" until DNS propagation completes and, separately, confirm the AWS account has production SES access before assuming arbitrary recipients can receive mail.
5. **Prefer IAM Roles Over Long-Lived Keys When Possible**: If the consuming compute already has an IAM role, set `iam_create_access_key = false` and `iam_create_ses_smtp_password = false` to avoid writing sending credentials into Terraform state.
6. **Verify Exact Variable Names via `get_module`**: Cloud Posse modules rename/add label inputs across minor versions occasionally — confirm `iam_permissions`/`custom_from_*`/`zone_id` names and defaults with `get_module(sections=["inputs","outputs"])` against the pinned `0.25.2` docs before relying on memorized values.
7. **Pin the Module Version**: Use an explicit `version = "0.25.2"` constraint for reproducible deployments; Cloud Posse's own examples deliberately omit pinning, which is appropriate for their docs but not for production usage.
