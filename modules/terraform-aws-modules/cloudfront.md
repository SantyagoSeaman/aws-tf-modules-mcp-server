# Terraform AWS CloudFront Module

## Module Information

- **Module Name**: `cloudfront`
- **Module ID**: `terraform-aws-modules/cloudfront/aws`
- **Source**: `terraform-aws-modules/cloudfront/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-cloudfront
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/cloudfront/aws/latest
- **Latest Version**: 6.7.0
- **Purpose**: Creates and manages AWS CloudFront CDN distributions with full support for origins, cache behaviors, edge compute, mTLS, logging, and security features
- **Service**: AWS CloudFront (Content Delivery Network)
- **Category**: Networking, Content Delivery, Performance
- **Keywords**: cloudfront, cdn, distribution, s3-origin, custom-origin, vpc-origin, origin-access-control, cache-policy, cache-behavior, cloudfront-functions, lambda-edge, waf, response-headers-policy, mtls, trust-store, v2-logging, geo-restriction, origin-failover
- **Use For**: static website hosting, dynamic content/API acceleration, video streaming, software distribution, multi-origin failover, private/signed content delivery, edge computing, WAF-backed security layer, private VPC origin access, mutual TLS (mTLS) client authentication, IP allow-listing via Anycast static IPs

## Description

This Terraform module creates and manages AWS CloudFront distributions for global content delivery. CloudFront caches content at edge locations worldwide, reducing latency for websites, APIs, video streaming, and static assets. The module exposes nearly every argument of the `aws_cloudfront_distribution` resource, giving full control over origins, cache behaviors, security, and integration with other AWS services, while also directly creating supporting resources such as origin access controls, cache/origin-request/response-headers policies, and CloudFront Functions.

The module supports multiple origin types: S3 buckets with Origin Access Control (OAC), custom HTTP/HTTPS origins, and VPC origins for routing to private ALB/NLB/EC2 resources (including cross-account VPC origins). It handles cache behaviors with path pattern matching and managed or module-created cache/origin-request policies, SSL/TLS certificates via ACM, origin groups for automatic failover, and security features including geo-restrictions, AWS WAF integration, and viewer mutual TLS (mTLS) authentication backed by a dedicated `trust_store` submodule. Modern protocols HTTP/2, HTTP/3, and gRPC are supported.

Key capabilities include CloudFront Functions and Lambda@Edge for edge computing, response headers policies for CORS and security headers, cache-tag extraction for tag-based invalidation, V2 logging with CloudWatch Logs or S3 Parquet format, real-time CloudWatch metrics, Anycast static IP association, and (limited-availability) CloudFront Connection Functions for connection-level customization. The module manages viewer certificates and supports continuous deployment policies for blue/green deployments. Legacy Origin Access Identity (OAI) is **not** supported — OAC is the only supported S3 access mechanism since v6.0.0.

## Key Features

- **Multiple Origin Types**: S3 buckets, custom HTTP/HTTPS origins, and VPC origins for private resources
- **Origin Access Control (OAC)**: Modern S3 access with SigV4 signing; legacy OAI was removed in v6.0.0 (breaking change)
- **VPC Origins**: Route traffic to private ALB/NLB/EC2 resources without public exposure, including cross-account origins via `owner_account_id`
- **Origin Groups & Origin Shield**: Automatic failover between origins on HTTP errors; extra caching layer to reduce origin load
- **Cache Behaviors**: Default and ordered behaviors with path pattern matching, gRPC support, and managed or module-created cache/origin-request policies
- **Module-Managed Policies**: Create `cache_policies`, `origin_request_policies`, and `response_headers_policies` directly and reference them by key, alongside AWS-managed policies by name
- **CloudFront Functions**: Lightweight JavaScript edge compute with KeyValueStore associations
- **Lambda@Edge**: Full Lambda functions for complex viewer/origin request/response processing
- **Viewer mTLS**: Enforce mutual TLS client-certificate authentication using the bundled `trust_store` submodule
- **Cache Tag Config**: Extract a cache-tag header from origin responses for tag-based invalidation
- **V2 Logging**: CloudWatch Logs or S3 with Parquet format for cost-effective log analysis (CloudWatch destinations must be in `us-east-1`)
- **Real-Time Metrics & Monitoring Subscription**: Minute-level CloudWatch metrics
- **AWS WAF Integration**: Attach Web ACLs for DDoS protection and request filtering
- **Geo-Restrictions**: Whitelist or blacklist content by country code
- **Anycast Static IPs**: Associate a dedicated Anycast IP list for allow-listing scenarios
- **Connection Functions**: Limited-availability connection-level customization (default service quota is 0; requires a quota increase)
- **Custom Error Responses & Continuous Deployment**: Custom error pages and blue/green deployments with staging distributions

## Main Use Cases

1. **Static Website Hosting**: Serve S3-hosted websites with global caching and custom domains
2. **API Acceleration**: Reduce latency for API Gateway or custom API backends
3. **Video Streaming**: Distribute streaming content with adaptive bitrate and geo-restrictions
4. **Software Distribution**: Deliver downloads and updates with high availability
5. **Multi-Origin Failover**: Automatic failover between origins for high availability
6. **Private Content Delivery**: Signed URLs/cookies for premium or restricted content
7. **Edge Computing**: Request/response transformation with CloudFront Functions or Lambda@Edge
8. **Security Layer**: DDoS protection, WAF integration, and viewer mTLS for web applications
9. **VPC Origin Access**: Serve content from private (or cross-account) resources without public exposure
10. **IP Allow-Listing**: Provide partners/firewalls a dedicated Anycast static IP range

## Submodules

### 1. trust_store
- **Purpose**: Create an `aws_cloudfront_trust_store` populated from a CA certificate bundle stored in S3, for use with viewer mTLS
- **Source**: `terraform-aws-modules/cloudfront/aws//modules/trust_store`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/cloudfront/aws/latest/submodules/trust_store
- **Key Features**: CA certificate bundle loaded from S3 (with optional object version pinning), single-resource wrapper, tagging support
- **Use Cases**: Viewer mutual TLS (mTLS) client authentication, zero-trust CDN access, B2B/partner API endpoints requiring client certificates

## Submodule 1: trust_store

### Description
Creates a CloudFront Trust Store, which stores a bundle of CA certificates used to validate client certificates presented during viewer mTLS handshakes. The CA certificate bundle (PEM) must be uploaded to an S3 object; the submodule references it by bucket/key/region (and optionally a specific object version).

### Key Features
- Single `aws_cloudfront_trust_store` resource, ready to reference from the root module's `viewer_mtls_config.trust_store_config.trust_store_id`
- Reads the CA certificate bundle from an existing S3 object (bucket/key/region/version)
- Supports tagging

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether the trust store is created |
| `name` | `string` | `null` | Name of the trust store (forces replacement if changed) |
| `ca_cert_bucket` | `string` | `null` | S3 bucket name containing the CA certificates bundle |
| `ca_cert_key` | `string` | `null` | S3 object key for the CA certificates bundle |
| `ca_cert_region` | `string` | `null` | AWS region of the S3 bucket |
| `ca_cert_version` | `string` | `null` | S3 object version ID for the CA certificates bundle |
| `tags` | `map(string)` | `{}` | Tags to apply to the trust store |

### Main Outputs

| Output | Description |
|--------|-------------|
| `id` | The ID of the trust store |
| `arn` | The ARN of the trust store |
| `etag` | ETag of the trust store |
| `number_of_ca_certificates` | Number of CA certificates in the trust store |

### Usage Example

```hcl
module "trust_store" {
  source = "terraform-aws-modules/cloudfront/aws//modules/trust_store"

  name = "example-mtls-trust-store"

  ca_cert_bucket = module.ca_certificates.s3_bucket_id
  ca_cert_key    = aws_s3_object.ca_bundle.key
  ca_cert_region = "us-east-1"

  tags = { Environment = "production" }
}

module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "~> 6.0"

  # ... origin/cache_behavior config omitted ...

  viewer_mtls_config = {
    mode = "required"
    trust_store_config = {
      trust_store_id                 = module.trust_store.id
      advertise_trust_store_ca_names = true
      ignore_certificate_expiry      = false
    }
  }
}
```

## Main Module: CloudFront Distribution

### Description
The root module creates the `aws_cloudfront_distribution` and its directly-attached resources: origin access controls, VPC origins, cache/origin-request/response-headers policies, CloudFront Functions, a monitoring subscription, and (optionally) a connection function. It is the primary entry point for provisioning a CDN in front of S3, custom HTTP(S), or VPC-based origins.

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether resources are created |
| `default_cache_behavior` | `object` | **Required** | Default cache behavior configuration |
| `aliases` | `list(string)` | `null` | Alternate domain names (CNAMEs) for the distribution |
| `comment` | `string` | `null` | Distribution description/comment |
| `enabled` | `bool` | `true` | Whether distribution accepts end user requests |
| `is_ipv6_enabled` | `bool` | `true` | Enable IPv6 support |
| `http_version` | `string` | `"http2"` | Maximum HTTP version (`http1.1`, `http2`, `http2and3`, `http3`) |
| `price_class` | `string` | `null` | Price class (`PriceClass_All`, `PriceClass_200`, `PriceClass_100`) |
| `default_root_object` | `string` | `null` | Object returned for root URL (e.g., `index.html`) |
| `anycast_ip_list_id` | `string` | `null` | ID of an Anycast static IP list to associate with the distribution |
| `origin` | `map(object)` | `{}` | Map of origins (S3, custom HTTP/HTTPS, or VPC — VPC origins support cross-account via `vpc_origin_config.owner_account_id`) |
| `origin_access_control` | `map(object)` | S3 default | Origin access control settings with SigV4 signing (OAC only; OAI is not supported) |
| `vpc_origin` | `map(object)` | `null` | VPC origin configurations for private ALB/NLB/EC2 resources |
| `origin_group` | `map(object)` | `null` | Origin group failover configurations |
| `ordered_cache_behavior` | `list(object)` | `[]` | Ordered list of cache behaviors by path pattern |
| `cache_policies` | `map(object)` | `null` | Cache policies to create and reference via `cache_policy_key` |
| `origin_request_policies` | `map(object)` | `null` | Origin request policies to create and reference via `origin_request_policy_key` |
| `response_headers_policies` | `map(object)` | `null` | Response headers policies to create (CORS, security headers, custom headers) |
| `cloudfront_functions` | `map(object)` | `null` | CloudFront Functions to create and associate via `function_key` |
| `cache_tag_config` | `object` | `null` | Enables cache-tag extraction from an origin response header for tag-based invalidation |
| `viewer_certificate` | `object` | `{}` | SSL/TLS certificate configuration; ACM certificate must be in `us-east-1` |
| `viewer_mtls_config` | `object` | `null` | Viewer mutual TLS (mTLS) configuration referencing a `trust_store_id` |
| `restrictions` | `object` | `{restriction_type = "none"}` | Geo-restriction configuration |
| `custom_error_response` | `list(object)` | `null` | Custom error response pages |
| `logging_config` | `object` | `null` | Legacy (v1) S3 access logging configuration |
| `enable_v2_logging` | `bool` | `false` | Enable V2 logging (CloudWatch Logs or S3 Parquet) |
| `v2_logging` | `object` | `null` | V2 logging destination configuration (CloudWatch destinations must be `us-east-1`) |
| `web_acl_id` | `string` | `null` | AWS WAF Web ACL ARN/ID to attach (must exist in the CloudFront/global scope) |
| `create_connection_function` | `bool` | `false` | Create a CloudFront Connection Function (limited availability; default service quota is 0) |
| `create_monitoring_subscription` | `bool` | `false` | Enable CloudWatch monitoring subscription (minute-level metrics) |
| `continuous_deployment_policy_id` | `string` | `null` | ID of a continuous deployment policy for blue/green rollout (set only on the production distribution) |
| `staging` | `bool` | `null` | Mark as a staging distribution (used with continuous deployment) |
| `wait_for_deployment` | `bool` | `null` | Wait for distribution deployment to reach `Deployed` status |
| `retain_on_delete` | `bool` | `null` | Disable instead of delete on removal |
| `tags` | `map(string)` | `{}` | Tags for all resources |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cloudfront_distribution_id` | The identifier for the distribution |
| `cloudfront_distribution_arn` | The ARN for the distribution |
| `cloudfront_distribution_domain_name` | The CloudFront domain name (e.g., `d111111abcdef8.cloudfront.net`) |
| `cloudfront_distribution_hosted_zone_id` | Route 53 zone ID for Alias records |
| `cloudfront_distribution_status` | Distribution deployment status |
| `cloudfront_distribution_etag` | Current version of the distribution config |
| `cloudfront_origin_access_controls` | Created origin access controls |
| `cloudfront_vpc_origins` | Created VPC origins |
| `cloudfront_cache_policies` | Created cache policies |
| `cloudfront_origin_request_policies` | Created origin request policies |
| `cloudfront_response_headers_policies` | Created response headers policies |
| `cloudfront_functions` | Created CloudFront Functions |
| `cloudfront_monitoring_subscription_id` | CloudWatch monitoring subscription ID |
| `connection_function_arn` | ARN of the created connection function (if enabled) |

### Usage Examples

#### Example 1: S3 Origin with Origin Access Control (OAC)

```hcl
module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "~> 6.0"

  comment             = "Static website CDN"
  enabled             = true
  is_ipv6_enabled     = true
  http_version        = "http2and3"
  price_class         = "PriceClass_100"
  default_root_object = "index.html"

  aliases = ["cdn.example.com"]

  # Origin Access Control (default S3 config is automatically created)
  origin_access_control = {
    s3 = {
      description      = "CloudFront access to S3"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  origin = {
    s3_bucket = {
      domain_name               = module.s3_bucket.s3_bucket_bucket_regional_domain_name
      origin_access_control_key = "s3" # References OAC key above
    }
  }

  default_cache_behavior = {
    target_origin_id       = "s3_bucket"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods         = ["GET", "HEAD", "OPTIONS"]
    cached_methods          = ["GET", "HEAD"]
    compress                = true
    cache_policy_name       = "Managed-CachingOptimized"
  }

  viewer_certificate = {
    acm_certificate_arn = module.acm.acm_certificate_arn # must be in us-east-1
    ssl_support_method  = "sni-only"
  }

  tags = {
    Environment = "production"
  }
}
```

#### Example 2: Multi-Origin with Failover and V2 Logging

```hcl
module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "~> 6.0"

  aliases         = ["app.example.com"]
  comment         = "Multi-origin CDN with failover"
  enabled         = true
  http_version    = "http2and3"
  is_ipv6_enabled = true

  create_monitoring_subscription = true

  # V2 Logging to S3 in Parquet format (use a CloudWatch destination only in us-east-1)
  v2_logging = {
    name            = "cdn-logs"
    destination_arn = "${module.log_bucket.s3_bucket_arn}/cloudfront"
    output_format   = "parquet"
    s3_delivery_configuration = {
      enable_hive_compatible_path = true
      suffix_path                 = "{DistributionId}/{yyyy}/{MM}/{dd}/{HH}"
    }
  }

  origin_access_control = {
    s3 = {
      description      = "CloudFront access to S3"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  origin = {
    # API backend with Origin Shield
    api = {
      domain_name = "api.example.com"
      custom_origin_config = {
        http_port              = 80
        https_port              = 443
        origin_protocol_policy  = "https-only"
        origin_ssl_protocols    = ["TLSv1.2"]
      }
      origin_shield = {
        enabled              = true
        origin_shield_region = "us-east-1"
      }
    }
    # S3 for static assets
    s3_static = {
      domain_name               = module.s3.s3_bucket_bucket_regional_domain_name
      origin_access_control_key = "s3"
    }
  }

  # Origin group for automatic failover
  origin_group = {
    api_failover = {
      failover_criteria = {
        status_codes = [403, 404, 500, 502]
      }
      member = [
        { origin_id = "api" },
        { origin_id = "s3_static" }
      ]
    }
  }

  default_cache_behavior = {
    target_origin_id       = "api_failover"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods         = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods          = ["GET", "HEAD"]
    cache_policy_name       = "Managed-CachingDisabled"
  }

  ordered_cache_behavior = [
    {
      path_pattern            = "/static/*"
      target_origin_id        = "s3_static"
      viewer_protocol_policy  = "redirect-to-https"
      allowed_methods          = ["GET", "HEAD"]
      cached_methods           = ["GET", "HEAD"]
      cache_policy_name        = "Managed-CachingOptimized"
    }
  ]

  custom_error_response = [
    {
      error_code         = 404
      response_code      = 404
      response_page_path = "/errors/404.html"
    }
  ]

  viewer_certificate = {
    acm_certificate_arn = module.acm.acm_certificate_arn
    ssl_support_method  = "sni-only"
  }

  tags = {
    Environment = "production"
  }
}
```

#### Example 3: WAF Integration and Geo-Restrictions

```hcl
module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "~> 6.0"

  aliases = ["secure.example.com"]
  comment = "Secure CDN with WAF and geo-restrictions"
  enabled = true

  origin_access_control = {
    s3 = {
      description      = "Secure S3 access"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  origin = {
    secure_content = {
      domain_name               = module.s3.s3_bucket_bucket_regional_domain_name
      origin_access_control_key = "s3"
    }
  }

  default_cache_behavior = {
    target_origin_id       = "secure_content"
    viewer_protocol_policy = "https-only"
    allowed_methods         = ["GET", "HEAD"]
    cached_methods           = ["GET", "HEAD"]
    compress                 = true
    cache_policy_name        = "Managed-CachingOptimized"
  }

  # Geo-restrictions
  restrictions = {
    geo_restriction = {
      restriction_type = "whitelist"
      locations        = ["US", "CA", "GB", "DE"]
    }
  }

  # AWS WAF Web ACL (must exist in the CloudFront/global scope, i.e. us-east-1)
  web_acl_id = aws_wafv2_web_acl.cloudfront.arn

  viewer_certificate = {
    acm_certificate_arn = module.acm.acm_certificate_arn
    ssl_support_method  = "sni-only"
  }

  create_monitoring_subscription = true

  tags = {
    Environment = "production"
    Security    = "high"
  }
}

# WAF Web ACL (must be in us-east-1 for CloudFront)
resource "aws_wafv2_web_acl" "cloudfront" {
  provider = aws.us_east_1
  name     = "cloudfront-waf"
  scope    = "CLOUDFRONT"

  default_action { allow {} }

  rule {
    name     = "RateLimit"
    priority = 1
    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }
    action { block {} }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimit"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "CloudFrontWAF"
    sampled_requests_enabled   = true
  }
}
```

#### Example 4: CloudFront Functions with Module-Managed Cache & Origin Request Policies

```hcl
module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "~> 6.0"

  aliases = ["app.example.com"]
  comment = "CDN with CloudFront Functions and custom cache policies"
  enabled = true

  origin_access_control = {
    s3 = {
      description      = "S3 access"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  origin = {
    s3_bucket = {
      domain_name               = module.s3.s3_bucket_bucket_regional_domain_name
      origin_access_control_key = "s3"
    }
  }

  # Create CloudFront Functions
  cloudfront_functions = {
    url_rewrite = {
      name    = "url-rewrite"
      runtime = "cloudfront-js-2.0"
      code    = <<-EOF
        function handler(event) {
          var request = event.request;
          var uri = request.uri;
          if (uri.endsWith('/')) {
            request.uri += 'index.html';
          } else if (!uri.includes('.')) {
            request.uri += '/index.html';
          }
          return request;
        }
      EOF
    }
  }

  # Create a custom cache policy (in addition to AWS-managed ones)
  cache_policies = {
    spa_assets = {
      name        = "SpaAssetsCachePolicy"
      comment     = "Cache policy for SPA static assets"
      min_ttl     = 1
      default_ttl = 86400
      max_ttl     = 31536000

      parameters_in_cache_key_and_forwarded_to_origin = {
        enable_accept_encoding_brotli = true
        enable_accept_encoding_gzip   = true
        cookies_config = { cookie_behavior = "none" }
        headers_config = { header_behavior = "none" }
        query_strings_config = { query_string_behavior = "none" }
      }
    }
  }

  # Create Response Headers Policy
  response_headers_policies = {
    security_headers = {
      name    = "security-headers"
      comment = "Security headers for SPA"
      security_headers_config = {
        strict_transport_security = {
          access_control_max_age_sec = 31536000
          include_subdomains         = true
          preload                    = true
        }
        content_type_options = { override = true }
        frame_options        = { frame_option = "DENY" }
        xss_protection       = { mode_block = true, protection = true }
      }
    }
  }

  default_cache_behavior = {
    target_origin_id            = "s3_bucket"
    viewer_protocol_policy      = "redirect-to-https"
    allowed_methods              = ["GET", "HEAD"]
    cached_methods                = ["GET", "HEAD"]
    cache_policy_key              = "spa_assets" # references cache_policies key above
    response_headers_policy_key   = "security_headers"

    function_association = {
      viewer-request = {
        function_key = "url_rewrite"
      }
    }
  }

  viewer_certificate = {
    acm_certificate_arn = module.acm.acm_certificate_arn
    ssl_support_method  = "sni-only"
  }

  tags = {
    Environment = "production"
  }
}
```

#### Example 5: Lambda@Edge Integration

```hcl
module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "~> 6.0"

  aliases = ["api.example.com"]
  comment = "CDN with Lambda@Edge"
  enabled = true

  origin = {
    api = {
      domain_name = "origin.example.com"
      custom_origin_config = {
        http_port              = 80
        https_port              = 443
        origin_protocol_policy  = "https-only"
        origin_ssl_protocols    = ["TLSv1.2"]
      }
    }
  }

  default_cache_behavior = {
    target_origin_id       = "api"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods         = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    cache_policy_name        = "Managed-CachingDisabled"

    lambda_function_association = {
      viewer-request = {
        lambda_arn   = aws_lambda_function.auth.qualified_arn
        include_body = false
      }
    }
  }

  viewer_certificate = {
    acm_certificate_arn = module.acm.acm_certificate_arn
    ssl_support_method  = "sni-only"
  }

  tags = {
    Environment = "production"
  }
}

# Lambda@Edge must be in us-east-1 and published (not $LATEST)
resource "aws_lambda_function" "auth" {
  provider      = aws.us_east_1
  filename      = "auth.zip"
  function_name = "cloudfront-auth"
  role          = aws_iam_role.lambda_edge.arn
  handler       = "index.handler"
  runtime       = "nodejs20.x"
  publish       = true
  timeout       = 5
  memory_size   = 128
}
```

#### Example 6: Viewer mTLS with Trust Store

```hcl
module "trust_store" {
  source = "terraform-aws-modules/cloudfront/aws//modules/trust_store"

  name = "example-mtls-trust-store"

  ca_cert_bucket = module.ca_certificates.s3_bucket_id
  ca_cert_key    = aws_s3_object.ca_bundle.key
  ca_cert_region = "us-east-1"

  tags = { Environment = "production" }
}

module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "~> 6.0"

  comment             = "CloudFront distribution with mTLS"
  default_root_object = "index.html"
  aliases             = ["secure-api.example.com"]

  viewer_certificate = {
    acm_certificate_arn = module.acm.acm_certificate_arn
    ssl_support_method  = "sni-only"
  }

  # Require clients to present a certificate signed by a CA in the trust store
  viewer_mtls_config = {
    mode = "required"
    trust_store_config = {
      trust_store_id                 = module.trust_store.id
      advertise_trust_store_ca_names = true
      ignore_certificate_expiry      = false
    }
  }

  origin_access_control = {
    s3 = {
      description      = "CloudFront access to S3"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  origin = {
    s3 = {
      domain_name               = module.s3.s3_bucket_bucket_regional_domain_name
      origin_access_control_key = "s3"
    }
  }

  default_cache_behavior = {
    target_origin_id       = "s3"
    viewer_protocol_policy = "redirect-to-https"
    cache_policy_id         = "658327ea-f89d-4fab-a63d-7e88639e58f6" # Managed-CachingOptimized
  }

  restrictions = {
    geo_restriction = { restriction_type = "none" }
  }

  tags = { Environment = "production" }
}
```

## Best Practices

### Security

1. **Use Origin Access Control (OAC)**: Only OAC is supported for S3 origins (legacy OAI was removed in v6.0.0) - supports SSE-KMS encryption
2. **Enforce HTTPS**: Use `viewer_protocol_policy = "redirect-to-https"` or `"https-only"`
3. **Use TLSv1.2 minimum**: Default `minimum_protocol_version` is `TLSv1.2_2025`; avoid pinning to older protocols
4. **Implement AWS WAF**: Attach a Web ACL for DDoS protection and request filtering
5. **Add security headers**: Use response headers policies for HSTS, X-Frame-Options, CSP
6. **Geo-restrictions**: Restrict content by country when required
7. **Signed URLs/cookies**: Use trusted key groups for private content access
8. **Viewer mTLS**: Require client certificates (`viewer_mtls_config.mode = "required"`) for zero-trust or B2B endpoints; rotate the CA bundle in the `trust_store` submodule before expiry
9. **Secure custom origins**: Use `origin_protocol_policy = "https-only"` with TLSv1.2

### Performance

1. **Enable compression**: Set `compress = true` in cache behaviors
2. **Use HTTP/2 or HTTP/3**: Configure `http_version = "http2and3"`
3. **Use managed cache policies**: `Managed-CachingOptimized` for static, `Managed-CachingDisabled` for dynamic; create custom `cache_policies`/`origin_request_policies` when managed ones don't fit
4. **Enable Origin Shield**: Additional caching layer reduces origin load
5. **Configure origin groups**: Automatic failover on HTTP errors (403, 404, 500, 502)
6. **Choose price class wisely**: `PriceClass_100` for US/Europe, `PriceClass_200` for most global use cases
7. **Use gRPC when needed**: Enable `grpc_config.enabled = true` in a cache behavior for gRPC-based backends

### Cost Optimization

1. **Optimize cache hit ratio**: Higher hit ratio = lower origin costs
2. **Avoid invalidations**: Use versioned file names or cache-busting query strings; use `cache_tag_config` for targeted tag-based invalidation instead of broad wildcard invalidations
3. **Enable V2 logging with Parquet**: More cost-effective than standard logging for analytics
4. **Consolidate distributions**: Use multiple origins in one distribution when possible

### Monitoring

1. **Enable monitoring subscription**: Minute-level CloudWatch metrics
2. **Use V2 logging**: CloudWatch Logs or S3 with Parquet for efficient log analysis; CloudWatch destinations must be created in `us-east-1`
3. **Create CloudWatch alarms**: Monitor error rates, origin latency, cache hit ratio
4. **Track function metrics**: Monitor CloudFront Functions and Lambda@Edge invocations

### Edge Computing

1. **CloudFront Functions vs Lambda@Edge**: Use Functions for lightweight operations (<1ms), Lambda@Edge for complex logic
2. **Lambda@Edge in us-east-1**: Must be created in us-east-1 and published (not `$LATEST`)
3. **Respect limits**: Functions have 5s viewer/30s origin timeout limits
4. **Connection Functions are limited-availability**: Default service quota is 0; request a quota increase before setting `create_connection_function = true`
5. **Test thoroughly**: Edge code runs on every request globally

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-cloudfront
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/cloudfront/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-cloudfront/tree/master/examples
- **CloudFront Developer Guide**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/
- **Origin Access Control**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html
- **CloudFront Functions**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-functions.html
- **Lambda@Edge**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-edge.html
- **Viewer mTLS / Trust Stores**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/mutual-authentication.html
- **Anycast Static IPs**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/request-static-ips.html
- **CloudFront Pricing**: https://aws.amazon.com/cloudfront/pricing/

## Notes for AI Agents

When using this module:

1. **Use OAC for S3, never OAI**: Set `origin_access_control_key` to reference an OAC; OAI resources were removed from the module in v6.0.0
2. **Minimum provider version**: Requires AWS provider `>= 6.46` and Terraform `>= 1.5.7` — pin `version = "~> 6.0"` for this module
3. **Use managed or module-created cache policies**: Reference by name (`cache_policy_name = "Managed-CachingOptimized"`) or by key (`cache_policy_key = "..."`) when creating one via `cache_policies`
4. **ACM certificates**: Must be issued in `us-east-1` for CloudFront
5. **Lambda@Edge**: Functions must be in `us-east-1` and published (not `$LATEST`)
6. **Geo-restrictions**: Use `restrictions.geo_restriction` (not a top-level `geo_restriction` argument)
7. **Origin groups for failover**: Configure `failover_criteria.status_codes` for automatic failover
8. **V2 logging recommended**: Use `v2_logging` with Parquet format for cost-effective analytics; CloudWatch log delivery destinations must be in `us-east-1`
9. **Viewer mTLS requires the `trust_store` submodule**: Upload a CA bundle to S3 first, create the trust store, then reference its `id` in `viewer_mtls_config.trust_store_config.trust_store_id`
10. **Cross-account VPC origins**: Set `vpc_origin_config.owner_account_id` when the VPC origin resource lives in a different account
11. **Connection Functions have a default quota of 0**: Only set `create_connection_function = true` after requesting a service quota increase
12. **Deployment time**: Changes take 5-15 minutes to propagate globally
13. **S3 bucket policy**: Must allow CloudFront OAC access (the module does not create the bucket policy)
14. **Route 53 alias**: Use `cloudfront_distribution_hosted_zone_id` for Alias records
