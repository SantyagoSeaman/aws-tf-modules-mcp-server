# Terraform AWS ACM Module

## Module Information

- **Module Name**: `acm`
- **Source**: `terraform-aws-modules/acm/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-acm
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/acm/aws/latest
- **Latest Version**: 6.1.0
- **Purpose**: Terraform module for creating and managing AWS Certificate Manager (ACM) certificates with DNS or email validation methods
- **Service**: AWS ACM (AWS Certificate Manager)
- **Category**: Security, Networking
- **Keywords**: acm, certificate, ssl, tls, x509, https, dns-validation, email-validation, route53, cloudfront, domain-validation, certificate-authority, public-certificate, private-certificate, subject-alternative-names, sans, wildcard-certificate, multi-domain, encryption, transport-layer-security, secure-sockets-layer, certificate-renewal, certificate-management, domain-verification, certificate-transparency, api-gateway, load-balancer, alb, nlb, elastic-load-balancing
- **Use For**: securing web applications with HTTPS, protecting API Gateway endpoints, enabling SSL/TLS for CloudFront distributions, securing Application Load Balancers and Network Load Balancers, implementing wildcard certificates for subdomains, managing multi-domain certificates, automating certificate provisioning and renewal, securing custom domain names, enabling end-to-end encryption, meeting compliance requirements for encrypted data in transit

## Description

This Terraform module simplifies the creation and management of AWS Certificate Manager (ACM) certificates for securing AWS resources. ACM handles the complexity of creating, storing, and automatically renewing public SSL/TLS X.509 certificates and keys that protect AWS websites and applications. The module supports both DNS and email validation methods, with particular emphasis on DNS validation through AWS Route53 for automated certificate validation and renewal workflows.

The module provides comprehensive certificate management capabilities including support for single domain names, multiple specific domains through Subject Alternative Names (SANs), and wildcard domains. It integrates seamlessly with Route53 for automated DNS validation record creation, eliminating manual validation steps. The module also supports external DNS providers when Route53 is not used, offering flexibility for various infrastructure configurations. Regional certificate deployment is fully supported, with special handling for CloudFront distributions that require certificates in the US East (N. Virginia) region.

Built with operational excellence in mind, the module includes configurable validation timeouts, certificate transparency logging controls, and conditional resource creation flags. It outputs essential certificate information including ARNs, validation status, and domain validation options for integration with other Terraform resources. The module follows AWS best practices for certificate management while providing the flexibility needed for diverse use cases ranging from simple single-domain certificates to complex multi-domain configurations with automated validation and renewal.

## Key Features

- **DNS Validation**: Automatic certificate validation using Route53 DNS records with configurable validation options
- **Email Validation**: Support for email-based certificate validation with customizable validation domains
- **Route53 Integration**: Seamless integration with AWS Route53 for automated DNS record creation and management
- **Subject Alternative Names (SANs)**: Support for multiple domain names and wildcard domains in a single certificate
- **CloudFront Compatibility**: Special support for creating certificates in US East (N. Virginia) region for CloudFront distributions
- **External DNS Providers**: Ability to manage certificates with DNS validation using external DNS providers (Cloudflare, etc.)
- **Conditional Certificate Creation**: Control certificate creation through feature flags for flexible module usage
- **Validation Record Management**: Automated creation and management of validation records with overwrite protection
- **Configurable Validation Timeout**: Customizable timeout periods for certificate validation completion
- **Certificate Transparency Logging**: Control over certificate transparency log inclusion with configurable preferences
- **Multiple Provider Support**: Support for multiple AWS provider configurations for cross-region certificate deployment
- **Validation Status Tracking**: Comprehensive outputs for monitoring certificate validation status and domain validation options
- **Wait for Validation Control**: Option to wait for validation completion or proceed asynchronously
- **Regional Certificate Support**: Deploy certificates in any AWS region based on resource requirements
- **Wildcard Certificate Support**: Create wildcard certificates for securing all subdomains under a domain
- **Certificate ARN Output**: Export certificate ARN for use with other AWS resources (ALB, CloudFront, API Gateway)
- **Domain Validation Options Export**: Detailed validation information for integration with external DNS systems
- **Validation Record FQDN Tracking**: Track fully qualified domain names for validation records
- **Distinct Domain Names Handling**: Intelligent handling of duplicate domains in SANs and primary domain

## Main Use Cases

1. **Web Application Security**: Secure web applications with HTTPS/TLS certificates for encrypted client connections
2. **API Gateway Protection**: Enable SSL/TLS encryption for AWS API Gateway custom domain names
3. **CloudFront Distribution Security**: Provision certificates for CloudFront distributions to serve content over HTTPS
4. **Load Balancer Encryption**: Secure Application Load Balancers (ALB) and Network Load Balancers (NLB) with TLS termination
5. **Multi-Domain Applications**: Manage certificates covering multiple domains and subdomains with Subject Alternative Names
6. **Wildcard Domain Coverage**: Deploy wildcard certificates to secure all subdomains under a parent domain
7. **Compliance Requirements**: Meet regulatory compliance requirements for encrypted data in transit (PCI-DSS, HIPAA, SOC 2)
8. **Automated Certificate Lifecycle**: Automate certificate provisioning, validation, and renewal workflows with Infrastructure as Code
9. **Cross-Region Deployments**: Deploy certificates across multiple AWS regions for geographically distributed applications
10. **Custom Domain Names**: Enable custom domain names for AWS services like Elastic Beanstalk, CloudFront, and API Gateway

## Submodules

This module does not contain submodules. All functionality is provided by the root module.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_certificate` | `bool` | `true` | Whether to create ACM certificate |
| `validate_certificate` | `bool` | `true` | Whether to validate certificate by creating Route53 records |
| `wait_for_validation` | `bool` | `true` | Whether to wait for the validation to complete |
| `domain_name` | `string` | `""` | A domain name for which the certificate should be issued |
| `subject_alternative_names` | `list(string)` | `[]` | A list of domains that should be SANs in the issued certificate |
| `validation_method` | `string` | `"DNS"` | Which method to use for validation (DNS or EMAIL) |
| `zone_id` | `string` | `""` | The ID of the hosted zone to contain validation records |
| `validation_timeout` | `string` | `null` | Define maximum timeout to wait for validation to complete |
| `validation_allow_overwrite_records` | `bool` | `true` | Whether to allow overwrite of Route53 records |
| `certificate_transparency_logging_preference` | `bool` | `true` | Specifies whether certificate details should be added to a certificate transparency log |
| `create_route53_records_only` | `bool` | `false` | Whether to create only Route53 records (useful for external DNS) |
| `tags` | `map(string)` | `{}` | A mapping of tags to assign to the resource |

## Main Outputs

| Output | Description |
|--------|-------------|
| `acm_certificate_arn` | The ARN of the certificate |
| `acm_certificate_status` | Status of the certificate |
| `acm_certificate_domain_validation_options` | A list of attributes to feed into other resources to complete certificate validation |
| `validation_route53_record_fqdns` | List of FQDNs built using the zone domain and name |
| `distinct_domain_names` | List of distinct domain names used for the validation |
| `validation_domains` | List of distinct domain validation options (useful for wildcard SANs) |
| `acm_certificate_validation_emails` | A list of addresses that received a validation email (EMAIL validation only) |

## Usage Examples

### Example 1: Complete DNS Validation with Route53

```hcl
module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 4.0"

  domain_name  = "example.com"
  zone_id      = "Z2ES7B9AZ6SHAE"

  subject_alternative_names = [
    "*.example.com",
    "app.example.com",
    "api.example.com"
  ]

  wait_for_validation = true
  validation_method   = "DNS"

  tags = {
    Name        = "example.com"
    Environment = "production"
  }
}

# Use the certificate with an ALB
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
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
# Create a provider for US East (required for CloudFront certificates)
provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

module "acm_cloudfront" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 4.0"

  providers = {
    aws = aws.us-east-1
  }

  domain_name  = "cdn.example.com"
  zone_id      = "Z2ES7B9AZ6SHAE"

  subject_alternative_names = [
    "*.cdn.example.com"
  ]

  validation_method = "DNS"

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

### Example 3: External DNS Validation (Non-Route53)

```hcl
module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 4.0"

  domain_name  = "example.com"

  subject_alternative_names = [
    "*.example.com"
  ]

  # Don't create Route53 records - will validate externally
  create_route53_records_only = false
  validation_method           = "DNS"

  # Don't wait for validation (will be done externally)
  wait_for_validation = false

  tags = {
    Name = "External DNS Certificate"
  }
}

# Output the validation records to create in external DNS
output "certificate_validation_records" {
  description = "DNS records to create for certificate validation"
  value       = module.acm.acm_certificate_domain_validation_options
}
```

### Example 4: Email Validation

```hcl
module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 4.0"

  domain_name       = "example.com"
  validation_method = "EMAIL"

  subject_alternative_names = [
    "www.example.com"
  ]

  # Email validation doesn't require waiting
  wait_for_validation = false

  tags = {
    Name           = "Email Validated Certificate"
    ValidationMethod = "EMAIL"
  }
}

# Check validation emails
output "validation_emails" {
  description = "Addresses that received validation emails"
  value       = module.acm.acm_certificate_validation_emails
}
```

## Best Practices

### Certificate Design and Planning

1. **Use DNS Validation**: Prefer DNS validation over email validation for automated certificate lifecycle management and renewal
2. **Wildcard Certificates for Testing**: Use wildcard certificates in non-production environments to reduce certificate count and simplify management
3. **Regional Certificate Planning**: Request certificates in each region where your resources are deployed; certificates are regional resources
4. **CloudFront Region Requirement**: Always create CloudFront certificates in the US East (N. Virginia) region, regardless of your resource location
5. **Subject Alternative Names Strategy**: Include all required domains and subdomains in SANs when requesting the certificate; you cannot modify existing certificates
6. **Certificate Naming Convention**: Use consistent, descriptive naming and tagging for certificates to track their purpose and associated resources
7. **Validation Method Selection**: Choose DNS validation for automated renewal; use email validation only when DNS control is not available
8. **Domain Name Planning**: Validate all domain names when requesting certificates; revalidation in each region is required

### Security and Access Control

1. **Account-Level Separation**: Use separate AWS accounts to control certificate access for different environments or teams
2. **IAM Permission Management**: Restrict certificate signing permissions by denying `kms:CreateGrant` for users who shouldn't create certificates
3. **Encryption Context Keys**: Limit certificate access using encryption context condition keys in IAM policies
4. **CloudTrail Monitoring**: Enable AWS CloudTrail to monitor all ACM API calls and track certificate lifecycle events
5. **Certificate Pinning Avoidance**: Do not pin ACM-managed certificates due to automatic renewal; pin to Amazon root certificates or imported certificates instead
6. **Private Certificate Authority**: Use AWS Private CA for internal certificates requiring custom certificate chains or extended validation periods
7. **Certificate Transparency Logging**: Understand implications of certificate transparency logging; opt-out doesn't guarantee certificates won't be logged
8. **Access Logging**: Enable access logging on resources using certificates (ALB, CloudFront) for security monitoring and compliance

### Certificate Lifecycle Management

1. **Automatic Renewal**: ACM automatically renews certificates before expiration; ensure DNS validation records remain in place for renewal
2. **Validation Record Persistence**: Keep DNS validation records in place permanently to enable automatic certificate renewal
3. **Certificate Replacement**: Request new certificates to add or remove domains; existing certificates cannot be modified
4. **Validation Timeout Configuration**: Set appropriate validation timeouts based on your DNS propagation times and operational requirements
5. **Monitoring Certificate Status**: Regularly monitor certificate status and validation state through CloudWatch or ACM console
6. **Domain Ownership Verification**: Maintain domain ownership and control to prevent certificate validation failures during renewal
7. **Certificate Expiration Alerts**: Set up CloudWatch alarms for certificate expiration warnings (ACM sends notifications at 45, 30, 15, 7, and 1 day before expiration)
8. **Testing Validation Process**: Test certificate validation process in non-production environments before production deployment

### Operational Excellence

1. **Infrastructure as Code**: Manage certificates through Terraform for version control, reproducibility, and audit trails
2. **Validation Record Management**: Use `validation_allow_overwrite_records = true` to handle validation record updates during re-creation
3. **Wait for Validation Setting**: Use `wait_for_validation = true` in production to ensure certificates are valid before resource creation
4. **Certificate Transparency Control**: Configure certificate transparency logging preference based on your security and privacy requirements
5. **Resource Tagging**: Apply comprehensive tags to certificates for cost allocation, ownership tracking, and lifecycle management
6. **Route53 Integration**: Leverage Route53 for DNS validation to automate validation record creation and removal
7. **External DNS Handling**: When using external DNS providers, export validation records and document the manual validation process
8. **Multiple Provider Strategy**: Use multiple AWS provider aliases for cross-region certificate deployment in a single Terraform configuration

### Integration and Usage

1. **Certificate ARN References**: Use certificate ARN outputs to reference certificates in ALB listeners, CloudFront distributions, and API Gateway configurations
2. **ALB Security Policy**: Specify modern TLS policies (e.g., `ELBSecurityPolicy-TLS13-1-2-2021-06`) when attaching certificates to load balancers
3. **CloudFront SNI Support**: Use Server Name Indication (SNI) for CloudFront distributions to avoid dedicated IP charges
4. **API Gateway Custom Domains**: Create certificates matching your API Gateway custom domain names before configuring the custom domain
5. **Certificate Sharing**: Share certificates across resources in the same region; multiple resources can use the same certificate
6. **Minimum TLS Version**: Configure minimum TLS version requirements on resources using certificates (prefer TLS 1.2 or higher)
7. **HTTPS Redirect**: Implement HTTP to HTTPS redirects on load balancers and CloudFront to enforce encrypted connections
8. **Certificate Validation in CI/CD**: Integrate certificate validation checks in CI/CD pipelines to catch configuration issues early

### Cost Optimization

1. **Free Certificate Management**: ACM certificates are free; you only pay for associated AWS resources using the certificates
2. **Wildcard Certificate Consolidation**: Use wildcard certificates to cover multiple subdomains and reduce certificate count
3. **Certificate Reuse**: Reuse certificates across multiple resources in the same region to minimize management overhead
4. **SNI vs Dedicated IP**: Always use SNI for CloudFront distributions to avoid $600/month dedicated IP charges
5. **Regional Certificate Strategy**: Create certificates only in regions where resources require them to reduce management complexity
6. **Unused Certificate Cleanup**: Regularly audit and delete unused certificates to maintain a clean certificate inventory
7. **Validation Method Cost**: DNS validation has no additional cost; email validation is also free but requires manual intervention

### Compliance and Governance

1. **Certificate Transparency Logging**: Enable certificate transparency logging for compliance and public certificate trust requirements
2. **Audit Trail Maintenance**: Use CloudTrail logs to maintain audit trails of certificate lifecycle events for compliance reporting
3. **Encryption Standards**: Ensure certificates meet organizational and regulatory encryption standards (key length, algorithm)
4. **Data Residency**: Deploy certificates in regions that comply with data residency requirements for your organization
5. **Certificate Policy Documentation**: Document certificate request, validation, and renewal procedures for compliance audits
6. **Regular Security Reviews**: Conduct periodic reviews of certificate usage, access controls, and security configurations
7. **Compliance Framework Alignment**: Align certificate management practices with relevant compliance frameworks (PCI-DSS, HIPAA, SOC 2, ISO 27001)

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-acm
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/acm/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-acm/tree/master/examples
- **AWS Certificate Manager Documentation**: https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html
- **ACM Best Practices**: https://docs.aws.amazon.com/acm/latest/userguide/acm-bestpractices.html
- **DNS Validation**: https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html
- **Email Validation**: https://docs.aws.amazon.com/acm/latest/userguide/email-validation.html
- **ACM Certificate Characteristics**: https://docs.aws.amazon.com/acm/latest/userguide/acm-certificate.html
- **Managed Renewal**: https://docs.aws.amazon.com/acm/latest/userguide/managed-renewal.html
- **CloudFront and ACM**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html
- **API Gateway Custom Domains**: https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-custom-domains.html
- **ACM API Reference**: https://docs.aws.amazon.com/acm/latest/APIReference/Welcome.html
- **AWS Private CA**: https://docs.aws.amazon.com/privateca/latest/userguide/PcaWelcome.html
- **Certificate Transparency**: https://docs.aws.amazon.com/acm/latest/userguide/acm-concepts.html#concept-transparency

## Notes for AI Agents

When using this module in automated workflows:

1. **DNS Validation Preferred**: Always use DNS validation with Route53 when possible for fully automated certificate lifecycle management
2. **Wait for Validation**: Set `wait_for_validation = true` in production to ensure certificates are valid before dependent resources are created
3. **CloudFront Region**: Remember to use US East (N. Virginia) region provider for CloudFront certificates
4. **Validation Records Persistence**: Ensure DNS validation records remain in place for automatic certificate renewal
5. **Subject Alternative Names**: Plan and include all required domains upfront; certificates cannot be modified after creation
6. **Regional Awareness**: Create certificates in the same region as the resources that will use them (except CloudFront)
7. **External DNS Handling**: When using external DNS, set `create_route53_records_only = false` and `wait_for_validation = false`
8. **Certificate ARN Output**: Always output certificate ARN for use in dependent resources like ALB listeners and CloudFront distributions
9. **Tagging Strategy**: Implement consistent tagging for certificate tracking, cost allocation, and lifecycle management
10. **Validation Timeout**: Adjust validation timeout based on DNS propagation times (default is usually sufficient)
11. **Wildcard Usage**: Use wildcard certificates strategically for subdomains but be aware of security implications
12. **Error Handling**: Implement proper error handling for certificate creation failures, validation timeouts, and DNS record conflicts
