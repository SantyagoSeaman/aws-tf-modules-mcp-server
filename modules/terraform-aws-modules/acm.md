# Terraform AWS ACM Module

## Module Information

- **Module Name**: `acm`
- **Source**: `terraform-aws-modules/acm/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-acm
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/acm/aws/latest
- **Latest Version**: 6.3.0
- **Purpose**: Creates and validates AWS Certificate Manager (ACM) certificates using DNS or email validation
- **Service**: AWS ACM (AWS Certificate Manager)
- **Category**: Security, Networking
- **Keywords**: acm, certificate, ssl, tls, https, dns-validation, route53, cloudfront, wildcard-certificate, alb, nlb, api-gateway, private-ca, certificate-renewal
- **Use For**: securing web applications with HTTPS, protecting API Gateway custom domains, enabling SSL/TLS for CloudFront distributions, securing ALB/NLB load balancers, implementing wildcard certificates, cross-account certificate/DNS provisioning, automating certificate lifecycle management

## Description

This Terraform module creates and manages AWS Certificate Manager (ACM) certificates for securing AWS resources with SSL/TLS encryption. ACM handles the complexity of issuing, storing, and automatically renewing public and private X.509 certificates, eliminating manual certificate management. The module supports both DNS validation (recommended, via Route53) and email validation, and issues either public certificates or private certificates through AWS Private Certificate Authority.

The module provides flexible certificate topologies: single domain names, multiple domains via Subject Alternative Names (SANs), and wildcard certificates. It integrates natively with Route53 to auto-create DNS validation records, or supports external DNS providers (Cloudflare, etc.) by disabling internal record creation and supplying validation FQDNs manually. For cross-account setups, the module can be invoked twice with `create_certificate = false` on one instance and `create_route53_records_only = true` on the other, splitting certificate issuance and DNS validation across separate AWS providers/accounts without hand-written `aws_route53_record` resources. For CloudFront distributions, the module supports the mandatory US East (N. Virginia) region via provider aliases or the `region` argument.

Additional capabilities include configurable validation timeouts (the underlying AWS provider defaults to a 45-minute wait), certificate transparency logging control, exportable certificates (subject to additional AWS charges), key algorithm selection (RSA/ECDSA), and conditional resource creation via feature flags — a workaround for Terraform's lack of `count` support on module blocks. The module outputs certificate ARNs and validation details for direct consumption by ALB, NLB, CloudFront, and API Gateway resources.

## Key Features

- **DNS Validation**: Automatic certificate validation using Route53 DNS records
- **Email Validation**: Certificate validation via email, including validation domain override
- **Route53 Integration**: Automated DNS record creation and cleanup for validation
- **External DNS Support**: Works with external DNS providers (Cloudflare, etc.) via manually supplied FQDNs
- **Subject Alternative Names (SANs)**: Multiple domains and wildcards in a single certificate
- **Wildcard Certificates**: Secure all subdomains under a domain with one certificate
- **CloudFront Compatibility**: US East (N. Virginia) region support via provider alias or `region` argument
- **Private CA Support**: Issue private certificates via AWS Private Certificate Authority
- **Cross-Account Splitting**: `create_route53_records_only` mode lets a second module instance create only the validation records under a separate provider/account
- **Exportable Certificates**: Optional certificate/key export (`export = "ENABLED"`), subject to extra AWS charges
- **Conditional Creation**: Feature flags (`create_certificate`, `validate_certificate`) to control resource creation, working around module `count` limitations
- **Validation Timeout Control**: Configurable timeout for validation completion (AWS default is 45 minutes)
- **Certificate Transparency Logging**: Toggle certificate transparency log inclusion
- **Key Algorithm Selection**: Choose RSA or ECDSA key algorithms

## Main Use Cases

1. **Web Application Security**: Secure web applications with HTTPS/TLS certificates
2. **API Gateway Protection**: SSL/TLS for API Gateway custom domain names
3. **CloudFront Distribution Security**: HTTPS certificates for CloudFront CDN
4. **Load Balancer Encryption**: TLS termination for ALB and NLB
5. **Multi-Domain Certificates**: Single certificate covering multiple domains with SANs
6. **Wildcard Domain Coverage**: Secure all subdomains with wildcard certificates
7. **Automated Certificate Lifecycle**: Infrastructure as Code for certificate provisioning and renewal
8. **Cross-Account Deployments**: Split certificate issuance and DNS validation across AWS accounts
9. **Private/Internal PKI**: Issue private certificates via AWS Private CA for internal services

## Submodules

This module does not contain submodules. All functionality is provided by the root module (the "cross-account" pattern reuses the same root module twice with different input flags, not a dedicated submodule).

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_certificate` | `bool` | `true` | Whether to create the ACM certificate |
| `domain_name` | `string` | `""` | Domain name for which the certificate should be issued |
| `subject_alternative_names` | `list(string)` | `[]` | List of domains that should be SANs in the certificate |
| `validation_method` | `string` | `null` | Validation method: `DNS` or `EMAIL` |
| `zone_id` | `string` | `""` | Route53 hosted zone ID for DNS validation |
| `zones` | `map(string)` | `{}` | Map of Route53 zone IDs for additional/SAN domains |
| `validate_certificate` | `bool` | `true` | Whether to validate the certificate by creating Route53 record(s) |
| `create_route53_records` | `bool` | `true` | Create DNS validation records internally via Route53; set `false` for external DNS |
| `create_route53_records_only` | `bool` | `false` | Create only the Route53 validation records (second instance in cross-account pattern) |
| `distinct_domain_names` | `list(string)` | `[]` | Distinct domains/SANs to validate (used with `create_route53_records_only`) |
| `acm_certificate_domain_validation_options` | `any` | `{}` | Domain validation options from the ACM certificate (used with `create_route53_records_only`) |
| `validation_record_fqdns` | `list(string)` | `[]` | External DNS validation record FQDNs (when `create_route53_records = false`) |
| `wait_for_validation` | `bool` | `true` | Whether to wait for validation to complete before returning |
| `validation_timeout` | `string` | `null` | Maximum timeout for validation completion (AWS default: 45m) |
| `validation_allow_overwrite_records` | `bool` | `true` | Allow overwrite of existing Route53 validation records |
| `dns_ttl` | `number` | `60` | TTL for DNS validation records |
| `certificate_transparency_logging_preference` | `bool` | `true` | Add certificate to the certificate transparency log |
| `key_algorithm` | `string` | `null` | Key algorithm (e.g. `RSA_2048`, `EC_secp384r1`) |
| `export` | `string` | `null` | Whether the certificate can be exported: `ENABLED` or `DISABLED`; incurs additional AWS charges |
| `private_authority_arn` | `string` | `null` | Private CA ARN for issuing private certificates |
| `region` | `string` | `null` | AWS region override for created resources (alternative to provider alias) |
| `tags` | `map(string)` | `{}` | Tags to assign to the certificate |

## Main Outputs

| Output | Description |
|--------|-------------|
| `acm_certificate_arn` | The ARN of the certificate |
| `acm_certificate_status` | Status of the certificate |
| `acm_certificate_domain_validation_options` | Attributes for completing certificate validation (feed into downstream/cross-account instances) |
| `validation_route53_record_fqdns` | List of FQDNs for validation records |
| `distinct_domain_names` | List of distinct domain names used for validation |
| `validation_domains` | List of domain validation options (useful for wildcard SANs) |
| `acm_certificate_validation_emails` | Addresses that received validation email (EMAIL validation only) |

## Usage Examples

### Example 1: DNS Validation with Route53

```hcl
module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 6.0"

  domain_name = "example.com"
  zone_id     = "Z2ES7B9AZ6SHAE"

  subject_alternative_names = [
    "*.example.com",
    "app.example.com"
  ]

  validation_method   = "DNS"
  wait_for_validation = true

  tags = {
    Name        = "example.com"
    Environment = "production"
  }
}

# Use certificate with ALB
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = module.acm.acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}
```

### Example 2: CloudFront Certificate (US East Region)

```hcl
provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

module "acm_cloudfront" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 6.0"

  providers = {
    aws = aws.us-east-1
  }

  domain_name = "cdn.example.com"
  zone_id     = "Z2ES7B9AZ6SHAE"

  subject_alternative_names = ["*.cdn.example.com"]
  validation_method         = "DNS"

  tags = {
    Name    = "CloudFront Certificate"
    Service = "CDN"
  }
}

resource "aws_cloudfront_distribution" "main" {
  # ... other configuration ...

  viewer_certificate {
    acm_certificate_arn      = module.acm_cloudfront.acm_certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}
```

### Example 3: External DNS (Cloudflare, etc.)

```hcl
module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 6.0"

  domain_name               = "example.com"
  subject_alternative_names = ["*.example.com"]

  validation_method      = "DNS"
  create_route53_records = false
  wait_for_validation    = false

  tags = {
    Name = "External DNS Certificate"
  }
}

# Output validation records to create in external DNS
output "validation_records" {
  description = "DNS records to create for certificate validation"
  value       = module.acm.acm_certificate_domain_validation_options
}
```

### Example 4: Cross-Account (Separate ACM and Route53 Providers)

```hcl
provider "aws" {
  alias = "acm"
  # ACM account credentials
}

provider "aws" {
  alias = "route53"
  # Route53 account credentials
}

# Issue the certificate in the ACM account; do not create Route53 records here
module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 6.0"

  providers = {
    aws = aws.acm
  }

  domain_name = "example.com"
  subject_alternative_names = [
    "*.example.com",
  ]

  validation_method = "DNS"

  create_route53_records  = false
  validation_record_fqdns = module.route53_records.validation_route53_record_fqdns
}

# Create only the validation records, in the Route53 account
module "route53_records" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 6.0"

  providers = {
    aws = aws.route53
  }

  create_certificate          = false
  create_route53_records_only = true

  validation_method = "DNS"

  zone_id                = "Z2ES7B9AZ6SHAE"
  distinct_domain_names  = module.acm.distinct_domain_names

  acm_certificate_domain_validation_options = module.acm.acm_certificate_domain_validation_options
}
```

## Best Practices

### Certificate Design

1. **Use DNS Validation**: Prefer DNS validation for automated certificate lifecycle and renewal
2. **Plan SANs Upfront**: Include all required domains when creating the certificate; they cannot be added after creation without replacing the certificate
3. **CloudFront Region**: Always create CloudFront certificates in the US East (N. Virginia) region (via provider alias or `region` argument)
4. **Wildcard Strategy**: Use wildcard certificates for subdomains to reduce certificate count
5. **Private CA for Internal Services**: Use `private_authority_arn` with AWS Private CA for internal/service-mesh TLS instead of public certificates

### Security

1. **Certificate Transparency**: Keep `certificate_transparency_logging_preference = true` for public trust requirements
2. **Modern TLS Policies**: Use TLS 1.2+ policies on load balancers (e.g., `ELBSecurityPolicy-TLS13-1-2-2021-06`)
3. **Avoid Certificate Pinning**: Don't pin ACM certificates due to automatic renewal; pin to Amazon root CAs if needed
4. **Restrict Exportability**: Leave `export = null` (disabled) unless the certificate/key genuinely needs to leave ACM; exportable certificates cost more and widen the exposure surface
5. **CloudTrail Monitoring**: Enable CloudTrail to audit certificate lifecycle events

### Operations

1. **Keep Validation Records**: Maintain DNS validation records permanently — ACM re-validates them for automatic renewal
2. **Wait for Validation**: Use `wait_for_validation = true` in production to ensure certificates are valid before dependent resources are created
3. **CI/CD Pipelines**: Set `wait_for_validation = false` to avoid blocking pipelines on the default 45-minute AWS validation timeout
4. **Validation Timeout**: Set `validation_timeout` explicitly if DNS propagation is slow or the default 45-minute wait is too short/long for your workflow
5. **Infrastructure as Code**: Manage certificates through Terraform for reproducibility and audit trails

### Cost

1. **Free Certificates**: ACM public certificates are free; you pay only for the resources that use them
2. **Use SNI**: Always use SNI for CloudFront to avoid dedicated IP charges ($600/month)
3. **Consolidate with Wildcards**: Use wildcard certificates to cover multiple subdomains efficiently
4. **Exportable Certificates Cost Extra**: Avoid `export = "ENABLED"` unless required — it incurs additional AWS charges

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-acm
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/acm/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-acm/tree/master/examples
- **AWS ACM Documentation**: https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html
- **ACM Best Practices**: https://docs.aws.amazon.com/acm/latest/userguide/acm-bestpractices.html
- **DNS Validation**: https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html
- **CloudFront and ACM**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html
- **AWS Private CA**: https://docs.aws.amazon.com/privateca/latest/userguide/PcaWelcome.html

## Notes for AI Agents

When using this module in automated workflows:

1. **DNS Validation Preferred**: Always use DNS validation with Route53 for fully automated certificate management
2. **Wait for Validation**: Set `wait_for_validation = true` to ensure certificates are valid before dependent resources; set it `false` in CI/CD to avoid the 45-minute default timeout blocking pipelines
3. **CloudFront Region**: Use a US East (N. Virginia) provider alias or the `region` argument for CloudFront certificates
4. **Keep Validation Records**: DNS validation records must remain in place for automatic renewal to work
5. **Plan SANs**: Include all domains upfront; certificates cannot be modified in place after creation
6. **External DNS**: Set `create_route53_records = false` and supply `validation_record_fqdns` for external DNS providers (e.g. Cloudflare)
7. **Certificate ARN**: Always surface `acm_certificate_arn` as a module output for use in ALB, CloudFront, and API Gateway resources
8. **Cross-Account**: Use two module instances — one with `create_route53_records = false` (issues the certificate) and one with `create_route53_records_only = true` (creates only the validation records) — each under a distinct provider alias, rather than hand-writing `aws_route53_record` resources
9. **Exportable Certificates**: Only set `export = "ENABLED"` when the certificate/key must leave ACM; it adds cost and security exposure
