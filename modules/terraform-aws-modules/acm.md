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
- **Keywords**: acm, certificate, ssl, tls, https, dns-validation, route53, cloudfront, wildcard-certificate, alb, nlb, api-gateway, encryption, certificate-renewal, subject-alternative-names
- **Use For**: securing web applications with HTTPS, protecting API Gateway endpoints, enabling SSL/TLS for CloudFront distributions, securing ALB/NLB load balancers, implementing wildcard certificates, automating certificate provisioning and renewal

## Description

This Terraform module creates and manages AWS Certificate Manager (ACM) certificates for securing AWS resources with SSL/TLS encryption. ACM handles the complexity of creating, storing, and automatically renewing public and private X.509 certificates. The module supports both DNS validation (recommended, via Route53) and email validation methods.

The module provides flexible certificate management including single domain names, multiple domains through Subject Alternative Names (SANs), and wildcard certificates. It integrates with Route53 for automated DNS validation record creation, or supports external DNS providers (like Cloudflare) when Route53 is not used. For CloudFront distributions, the module supports creating certificates in the required US East (N. Virginia) region using provider aliases.

Key capabilities include configurable validation timeouts, certificate transparency logging controls, conditional resource creation, and support for AWS Private CA for issuing private certificates. The module outputs certificate ARNs and validation details for integration with ALB, NLB, CloudFront, and API Gateway resources.

## Key Features

- **DNS Validation**: Automatic certificate validation using Route53 DNS records
- **Email Validation**: Support for email-based certificate validation
- **Route53 Integration**: Automated DNS record creation for validation
- **External DNS Support**: Works with external DNS providers (Cloudflare, etc.) via manual FQDN input
- **Subject Alternative Names (SANs)**: Multiple domains and wildcards in a single certificate
- **Wildcard Certificates**: Secure all subdomains under a domain
- **CloudFront Compatibility**: US East (N. Virginia) region support via provider aliases
- **Private CA Support**: Issue private certificates via AWS Private Certificate Authority
- **Conditional Creation**: Feature flags to control certificate and validation creation
- **Multi-Provider Support**: Separate AWS providers for ACM and Route53 (cross-account scenarios)
- **Validation Timeout Control**: Configurable timeout for validation completion
- **Certificate Transparency Logging**: Control over certificate transparency log inclusion
- **Key Algorithm Selection**: Specify RSA or ECDSA key algorithms

## Main Use Cases

1. **Web Application Security**: Secure web applications with HTTPS/TLS certificates
2. **API Gateway Protection**: SSL/TLS for API Gateway custom domain names
3. **CloudFront Distribution Security**: HTTPS certificates for CloudFront CDN
4. **Load Balancer Encryption**: TLS termination for ALB and NLB
5. **Multi-Domain Certificates**: Single certificate covering multiple domains with SANs
6. **Wildcard Domain Coverage**: Secure all subdomains with wildcard certificates
7. **Automated Certificate Lifecycle**: Infrastructure as Code for certificate provisioning and renewal
8. **Cross-Account Deployments**: Separate certificate and DNS management across AWS accounts

## Submodules

This module does not contain submodules. All functionality is provided by the root module.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_certificate` | `bool` | `true` | Whether to create ACM certificate |
| `domain_name` | `string` | `""` | Domain name for which the certificate should be issued |
| `subject_alternative_names` | `list(string)` | `[]` | List of domains that should be SANs in the certificate |
| `validation_method` | `string` | `null` | Validation method: DNS or EMAIL |
| `zone_id` | `string` | `""` | Route53 hosted zone ID for DNS validation |
| `zones` | `map(string)` | `{}` | Map of Route53 Zone IDs for additional domains |
| `validate_certificate` | `bool` | `true` | Whether to validate certificate by creating Route53 records |
| `create_route53_records` | `bool` | `true` | Create DNS records internally (set false for external DNS) |
| `validation_record_fqdns` | `list(string)` | `[]` | External DNS validation record FQDNs |
| `wait_for_validation` | `bool` | `true` | Whether to wait for validation to complete |
| `validation_timeout` | `string` | `null` | Maximum timeout for validation completion |
| `validation_allow_overwrite_records` | `bool` | `true` | Allow overwrite of Route53 validation records |
| `dns_ttl` | `number` | `60` | TTL for DNS validation records |
| `certificate_transparency_logging_preference` | `bool` | `true` | Add certificate to transparency log |
| `key_algorithm` | `string` | `null` | Key algorithm (RSA_2048, ECDSA_P256, etc.) |
| `private_authority_arn` | `string` | `null` | Private CA ARN for private certificates |
| `tags` | `map(string)` | `{}` | Tags to assign to the certificate |

## Main Outputs

| Output | Description |
|--------|-------------|
| `acm_certificate_arn` | The ARN of the certificate |
| `acm_certificate_status` | Status of the certificate |
| `acm_certificate_domain_validation_options` | Attributes for completing certificate validation |
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
  alias  = "acm"
  region = "eu-west-1"
  # ACM account credentials
}

provider "aws" {
  alias  = "route53"
  region = "eu-west-1"
  # Route53 account credentials
}

module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 6.0"

  providers = {
    aws = aws.acm
  }

  domain_name       = "example.com"
  zone_id           = "Z2ES7B9AZ6SHAE"
  validation_method = "DNS"

  # Disable internal Route53 record creation
  create_route53_records = false
}

# Create validation records in separate account
resource "aws_route53_record" "validation" {
  provider = aws.route53

  for_each = {
    for dvo in module.acm.acm_certificate_domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = "Z2ES7B9AZ6SHAE"
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.record]
}
```

## Best Practices

### Certificate Design

1. **Use DNS Validation**: Prefer DNS validation for automated certificate lifecycle and renewal
2. **Plan SANs Upfront**: Include all required domains when creating certificates; they cannot be modified after creation
3. **CloudFront Region**: Always create CloudFront certificates in US East (N. Virginia) region
4. **Wildcard Strategy**: Use wildcard certificates for subdomains to reduce certificate count

### Security

1. **Certificate Transparency**: Enable transparency logging for public trust requirements
2. **Modern TLS Policies**: Use TLS 1.2+ policies on load balancers (e.g., `ELBSecurityPolicy-TLS13-1-2-2021-06`)
3. **Avoid Certificate Pinning**: Don't pin ACM certificates due to automatic renewal; pin to Amazon root CAs if needed
4. **CloudTrail Monitoring**: Enable CloudTrail to audit certificate lifecycle events

### Operations

1. **Keep Validation Records**: Maintain DNS validation records permanently for automatic renewal
2. **Wait for Validation**: Use `wait_for_validation = true` in production to ensure certificates are valid before use
3. **Validation Timeout**: Set appropriate validation timeout based on DNS propagation times
4. **Infrastructure as Code**: Manage certificates through Terraform for reproducibility and audit trails

### Cost

1. **Free Certificates**: ACM public certificates are free; you pay only for resources using them
2. **Use SNI**: Always use SNI for CloudFront to avoid dedicated IP charges ($600/month)
3. **Consolidate with Wildcards**: Use wildcard certificates to cover multiple subdomains efficiently

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-acm
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/acm/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-acm/tree/master/examples
- **AWS ACM Documentation**: https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html
- **ACM Best Practices**: https://docs.aws.amazon.com/acm/latest/userguide/acm-bestpractices.html
- **DNS Validation**: https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html
- **CloudFront and ACM**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html

## Notes for AI Agents

When using this module in automated workflows:

1. **DNS Validation Preferred**: Always use DNS validation with Route53 for fully automated certificate management
2. **Wait for Validation**: Set `wait_for_validation = true` to ensure certificates are valid before dependent resources
3. **CloudFront Region**: Use US East (N. Virginia) provider for CloudFront certificates
4. **Keep Validation Records**: DNS records must remain for automatic renewal to work
5. **Plan SANs**: Include all domains upfront; certificates cannot be modified after creation
6. **External DNS**: Set `create_route53_records = false` and `wait_for_validation = false` for external DNS
7. **Certificate ARN**: Always output certificate ARN for use in ALB, CloudFront, API Gateway
8. **Cross-Account**: Use separate provider aliases for ACM and Route53 in different accounts
