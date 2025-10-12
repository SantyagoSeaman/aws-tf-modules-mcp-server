---
module_name: cloudfront
keywords: [cloudfront, cdn, content-delivery-network, edge-locations, distribution, origin, cache-behavior, ssl, tls, certificate, acm, viewer-protocol, s3-origin, custom-origin, lambda-edge, cloudfront-functions, geo-restriction, waf, web-application-firewall, origin-access-identity, origin-access-control, oac, oai, cache-policy, origin-request-policy, response-headers-policy, real-time-logs, logging, field-level-encryption, http2, http3, ipv6, price-class, ttl, time-to-live, invalidation, aliases, cname, domain-name, route53, dns, https, compression, gzip, brotli, custom-error-response, signed-urls, signed-cookies, trusted-signers, trusted-key-groups, viewer-certificate, minimum-protocol-version, security-policy, standard-logging, monitoring-subscription, realtime-metrics]
---

# Terraform AWS CloudFront Module

## Module Information

- **Module Name**: `cloudfront`
- **Source**: `terraform-aws-modules/cloudfront/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-cloudfront
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/cloudfront/aws/latest
- **Latest Version**: 5.0.0
- **Purpose**: Terraform module that creates and manages AWS CloudFront distributions for content delivery with comprehensive configuration options
- **Service**: AWS CloudFront (Content Delivery Network)
- **Category**: Networking, Content Delivery, Performance
- **Keywords**: cloudfront, cdn, content-delivery-network, edge-locations, distribution, origin, cache-behavior, ssl, tls, certificate, acm, viewer-protocol, s3-origin, custom-origin, lambda-edge, cloudfront-functions, geo-restriction, waf, web-application-firewall, origin-access-identity, origin-access-control, oac, oai, cache-policy, origin-request-policy, response-headers-policy, real-time-logs, logging, field-level-encryption, http2, http3, ipv6, price-class, ttl, time-to-live, invalidation, aliases, cname, domain-name, route53, dns, https, compression, gzip, brotli, custom-error-response, signed-urls, signed-cookies, trusted-signers, trusted-key-groups, viewer-certificate, minimum-protocol-version, security-policy, standard-logging, monitoring-subscription, realtime-metrics
- **Use For**: Global content delivery, static website acceleration, dynamic content delivery, API acceleration, video streaming distribution, software distribution, mobile application content delivery, multi-region application performance, DDoS protection, secure content delivery with access controls, reducing origin load, improving user experience with edge caching

## Description

This Terraform module provides a comprehensive solution for creating and managing AWS CloudFront distributions, Amazon's global content delivery network (CDN) service. CloudFront accelerates the delivery of websites, APIs, video content, and other web assets by caching content at edge locations around the world, reducing latency and improving user experience. The module supports virtually all features provided by the Terraform AWS provider for CloudFront, offering granular control over distribution configuration, caching behaviors, security settings, and integration with other AWS services.

The module handles complex CloudFront configurations including multiple origins (S3 buckets, custom HTTP/HTTPS origins, and media streaming origins), flexible cache behaviors with path pattern matching, SSL/TLS certificate integration through AWS Certificate Manager, and advanced security features such as origin access control, geo-restrictions, and AWS WAF integration. It supports modern protocols including HTTP/2 and HTTP/3, automatic content compression, and custom error responses. The module also manages origin access identities and origin access controls for securing S3 bucket content, ensuring that objects can only be accessed through CloudFront distributions.

Key architectural capabilities include support for Lambda@Edge and CloudFront Functions for edge computing scenarios, real-time logging for monitoring and analytics, field-level encryption for protecting sensitive data, and integration with AWS Shield Standard for DDoS protection. The module provides flexible configuration for cache policies, origin request policies, and response headers policies, allowing fine-tuned control over content delivery behavior. Whether deploying a simple static website CDN or a complex multi-origin distribution with custom caching logic, this module simplifies CloudFront management while maintaining the flexibility required for production workloads.

## Key Features

- **Multiple Origin Support**: Configure S3 buckets, custom HTTP/HTTPS origins, and media streaming origins in a single distribution
- **Origin Access Control (OAC)**: Modern authentication method for securing S3 origins with enhanced security over legacy OAI
- **Origin Access Identity (OAI)**: Legacy method for securing S3 bucket content access through CloudFront
- **Custom Domain Support**: Configure multiple aliases (CNAMEs) for custom domain names with your distribution
- **SSL/TLS Integration**: Seamless integration with AWS Certificate Manager for HTTPS support with custom certificates
- **Cache Behavior Configuration**: Define default and multiple ordered cache behaviors with path pattern matching
- **Viewer Protocol Policies**: Control HTTP to HTTPS redirects, HTTPS-only access, or allow both protocols
- **Cache Policies**: Configure TTL settings, cache key composition, and header/cookie/query string handling
- **Origin Request Policies**: Control which headers, cookies, and query strings are forwarded to origins
- **Response Headers Policies**: Add security and custom headers to responses from CloudFront
- **Compression Support**: Automatic Gzip and Brotli compression for compatible content types
- **Custom Error Responses**: Define custom error pages and response codes for origin errors
- **Geo-Restriction**: Implement geographic content restrictions with whitelist or blacklist configurations
- **AWS WAF Integration**: Attach Web Application Firewall for advanced security and filtering
- **Lambda@Edge Support**: Execute Lambda functions at CloudFront edge locations for custom logic
- **CloudFront Functions**: Deploy lightweight JavaScript functions for high-scale edge customizations
- **Real-Time Logging**: Stream detailed request logs to Kinesis Data Streams for real-time analytics
- **Standard Logging**: Configure access logs to S3 buckets for historical analysis
- **IPv6 Support**: Enable IPv6 for global accessibility and future-proof deployments
- **HTTP/2 and HTTP/3**: Support for modern HTTP protocols for improved performance
- **Price Class Selection**: Choose edge location coverage to balance performance and cost
- **Field-Level Encryption**: Protect sensitive data at the edge before forwarding to origins
- **Signed URLs and Cookies**: Implement private content distribution with time-limited access
- **Trusted Signers and Key Groups**: Configure authentication for private content access
- **Monitoring Subscription**: Enable real-time metrics for enhanced monitoring and alerting
- **Continuous Deployment**: Support for blue/green deployments and traffic splitting

## Main Use Cases

1. **Static Website Hosting**: Serve static websites from S3 with global edge caching and custom domains
2. **Dynamic Content Acceleration**: Accelerate dynamic content and API responses with edge optimizations
3. **Video Streaming**: Distribute video content with adaptive bitrate streaming and geo-restrictions
4. **Software Distribution**: Deliver software downloads, updates, and patches with high availability
5. **Mobile Application Content**: Serve mobile app assets, APIs, and media with low latency
6. **E-commerce Platforms**: Deliver product images, videos, and dynamic content for online stores
7. **SaaS Application Delivery**: Accelerate SaaS applications with edge caching and custom logic
8. **Media and Gaming**: Distribute game assets, patches, and streaming content globally
9. **Enterprise Content Distribution**: Deliver internal applications and content to distributed workforce
10. **API Gateway Acceleration**: Reduce API latency with CloudFront in front of API Gateway or custom APIs
11. **Security Enhancement**: Add DDoS protection and WAF capabilities to web applications
12. **Multi-Region Failover**: Implement origin failover for high availability architectures

## Submodules

This module does not include submodules. It provides a single root module for CloudFront distribution creation and management.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_distribution` | `bool` | `true` | Controls if CloudFront distribution should be created |
| `create_origin_access_identity` | `bool` | `false` | Controls if CloudFront origin access identity should be created |
| `origin_access_identities` | `map(string)` | `{}` | Map of CloudFront origin access identities (value as a comment) |
| `create_origin_access_control` | `bool` | `false` | Controls if CloudFront origin access control should be created |
| `origin_access_control` | `map(object)` | `{}` | Map of CloudFront origin access control configurations |
| `aliases` | `list(string)` | `[]` | Extra CNAMEs (alternate domain names) for this distribution |
| `comment` | `string` | `""` | Any comments you want to include about the distribution |
| `enabled` | `bool` | `true` | Whether the distribution is enabled to accept end user requests |
| `is_ipv6_enabled` | `bool` | `null` | Whether IPv6 is enabled for the distribution |
| `price_class` | `string` | `"PriceClass_All"` | Price class for this distribution (PriceClass_All, PriceClass_200, PriceClass_100) |
| `http_version` | `string` | `"http2"` | Maximum HTTP version to support on the distribution (http2, http2and3, http1.1) |
| `default_root_object` | `string` | `null` | Object that you want CloudFront to return when an end user requests the root URL |
| `origin` | `any` | `{}` | One or more origins for this distribution (S3, custom HTTP/HTTPS) |
| `origin_group` | `any` | `{}` | One or more origin groups for this distribution (for failover) |
| `default_cache_behavior` | `any` | `null` | Default cache behavior for this distribution |
| `ordered_cache_behavior` | `any` | `[]` | Ordered list of cache behaviors resource for this distribution |
| `viewer_certificate` | `any` | `{}` | SSL configuration for this distribution |
| `geo_restriction` | `any` | `{}` | Restriction configuration for this distribution |
| `logging_config` | `any` | `{}` | Logging configuration that controls how logs are written to your distribution |
| `web_acl_id` | `string` | `null` | AWS WAF web ACL ARN to associate with this distribution |
| `custom_error_response` | `any` | `[]` | Custom error response elements (multiples allowed) |
| `retain_on_delete` | `bool` | `false` | Disables the distribution instead of deleting it when destroying |
| `wait_for_deployment` | `bool` | `true` | Wait for the distribution status to change from InProgress to Deployed |
| `create_monitoring_subscription` | `bool` | `false` | If enabled, the resource for monitoring subscription will be created |
| `realtime_metrics_subscription_status` | `string` | `"Enabled"` | Status of real-time metrics subscription (Enabled or Disabled) |
| `tags` | `map(string)` | `{}` | A map of tags to assign to the resource |

## Main Outputs

| Output | Description |
|--------|-------------|
| `cloudfront_distribution_id` | The identifier for the distribution |
| `cloudfront_distribution_arn` | The ARN (Amazon Resource Name) for the distribution |
| `cloudfront_distribution_status` | The current status of the distribution (Deployed, InProgress) |
| `cloudfront_distribution_domain_name` | The domain name corresponding to the distribution |
| `cloudfront_distribution_hosted_zone_id` | The CloudFront Route 53 zone ID for Alias Resource Record Sets |
| `cloudfront_distribution_caller_reference` | Internal value used by CloudFront for future updates |
| `cloudfront_distribution_etag` | The current version of the distribution's information |
| `cloudfront_distribution_last_modified_time` | The date and time the distribution was last modified |
| `cloudfront_distribution_in_progress_validation_batches` | The number of invalidation batches currently in progress |
| `cloudfront_distribution_trusted_signers` | List of nested attributes for active trusted signers |
| `cloudfront_origin_access_identity_ids` | IDs of the origin access identities created |
| `cloudfront_origin_access_identity_iam_arns` | IAM ARNs of the origin access identities |
| `cloudfront_origin_access_control_ids` | IDs of the origin access controls created |
| `cloudfront_monitoring_subscription_id` | ID of the CloudFront monitoring subscription |

## Usage Examples

### Example 1: S3 Origin with Origin Access Control (OAC)

```hcl
module "cloudfront_s3_cdn" {
  source = "terraform-aws-modules/cloudfront/aws"

  aliases = ["cdn.example.com", "www.example.com"]
  comment = "CloudFront distribution for S3 static website"
  enabled = true
  is_ipv6_enabled = true
  http_version = "http2and3"
  price_class = "PriceClass_100"  # Use only North America and Europe

  # Create Origin Access Control for S3
  create_origin_access_control = true
  origin_access_control = {
    s3_oac = {
      description      = "CloudFront access to S3"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  # S3 origin configuration
  origin = {
    s3_bucket = {
      domain_name              = "my-static-website.s3.amazonaws.com"
      origin_access_control_id = "s3_oac"  # Reference to OAC above
    }
  }

  # Default cache behavior
  default_cache_behavior = {
    target_origin_id       = "s3_bucket"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods  = ["GET", "HEAD"]
    compress        = true

    cache_policy_id            = data.aws_cloudfront_cache_policy.caching_optimized.id
    origin_request_policy_id   = data.aws_cloudfront_origin_request_policy.cors_s3.id
    response_headers_policy_id = data.aws_cloudfront_response_headers_policy.security_headers.id
  }

  # SSL certificate configuration
  viewer_certificate = {
    acm_certificate_arn      = "arn:aws:acm:us-east-1:123456789012:certificate/example"
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  # Enable logging
  logging_config = {
    bucket          = "my-cloudfront-logs.s3.amazonaws.com"
    prefix          = "cdn/"
    include_cookies = false
  }

  tags = {
    Terraform   = "true"
    Environment = "production"
    Purpose     = "static-website-cdn"
  }
}

# Reference managed cache policies
data "aws_cloudfront_cache_policy" "caching_optimized" {
  name = "Managed-CachingOptimized"
}

data "aws_cloudfront_origin_request_policy" "cors_s3" {
  name = "Managed-CORS-S3Origin"
}

data "aws_cloudfront_response_headers_policy" "security_headers" {
  name = "Managed-SecurityHeadersPolicy"
}
```

### Example 2: Multi-Origin with Custom Cache Behaviors

```hcl
module "cloudfront_multi_origin" {
  source = "terraform-aws-modules/cloudfront/aws"

  aliases = ["app.example.com"]
  comment = "Multi-origin CloudFront for web application"
  enabled = true
  is_ipv6_enabled = true
  default_root_object = "index.html"

  # Multiple origins: S3 for static assets, ALB for dynamic content
  origin = {
    # Static assets from S3
    static_assets = {
      domain_name              = "my-assets.s3.amazonaws.com"
      origin_access_control_id = "s3_oac"

      custom_header = [
        {
          name  = "X-Custom-Header"
          value = "static-assets"
        }
      ]
    }

    # Dynamic content from Application Load Balancer
    api_backend = {
      domain_name = "api-alb-123456789.us-east-1.elb.amazonaws.com"

      custom_origin_config = {
        http_port              = 80
        https_port             = 443
        origin_protocol_policy = "https-only"
        origin_ssl_protocols   = ["TLSv1.2"]
        origin_read_timeout    = 30
        origin_keepalive_timeout = 5
      }
    }
  }

  # Default cache behavior for static content
  default_cache_behavior = {
    target_origin_id       = "static_assets"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods  = ["GET", "HEAD"]
    compress        = true

    min_ttl     = 0
    default_ttl = 3600    # 1 hour
    max_ttl     = 86400   # 24 hours

    forwarded_values = {
      query_string = false
      headers      = ["Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers"]

      cookies = {
        forward = "none"
      }
    }
  }

  # Ordered cache behaviors for specific paths
  ordered_cache_behavior = [
    # API paths - no caching, pass everything to origin
    {
      path_pattern           = "/api/*"
      target_origin_id       = "api_backend"
      viewer_protocol_policy = "https-only"

      allowed_methods = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
      cached_methods  = ["GET", "HEAD"]
      compress        = true

      min_ttl     = 0
      default_ttl = 0
      max_ttl     = 0

      forwarded_values = {
        query_string = true
        headers      = ["*"]

        cookies = {
          forward = "all"
        }
      }
    },

    # Static JS/CSS with longer TTL
    {
      path_pattern           = "/static/*"
      target_origin_id       = "static_assets"
      viewer_protocol_policy = "redirect-to-https"

      allowed_methods = ["GET", "HEAD"]
      cached_methods  = ["GET", "HEAD"]
      compress        = true

      min_ttl     = 86400    # 1 day
      default_ttl = 604800   # 1 week
      max_ttl     = 31536000 # 1 year

      forwarded_values = {
        query_string = false

        cookies = {
          forward = "none"
        }
      }
    }
  ]

  # Custom error responses
  custom_error_response = [
    {
      error_code            = 404
      response_code         = 404
      response_page_path    = "/404.html"
      error_caching_min_ttl = 300
    },
    {
      error_code            = 403
      response_code         = 404
      response_page_path    = "/404.html"
      error_caching_min_ttl = 300
    }
  ]

  viewer_certificate = {
    acm_certificate_arn      = "arn:aws:acm:us-east-1:123456789012:certificate/example"
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  # Origin Access Control for S3
  create_origin_access_control = true
  origin_access_control = {
    s3_oac = {
      description      = "CloudFront access to S3"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  tags = {
    Terraform   = "true"
    Environment = "production"
  }
}
```

### Example 3: CloudFront with WAF and Geo-Restrictions

```hcl
module "cloudfront_secure_cdn" {
  source = "terraform-aws-modules/cloudfront/aws"

  aliases = ["secure.example.com"]
  comment = "Secure CloudFront distribution with WAF and geo-restrictions"
  enabled = true
  is_ipv6_enabled = true

  origin = {
    secure_content = {
      domain_name = "secure-bucket.s3.amazonaws.com"
      origin_access_control_id = "s3_oac"
    }
  }

  default_cache_behavior = {
    target_origin_id       = "secure_content"
    viewer_protocol_policy = "https-only"  # HTTPS only, no redirect

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]
    compress        = true

    cache_policy_id = data.aws_cloudfront_cache_policy.caching_optimized.id
  }

  # Geographic restrictions - only allow specific countries
  geo_restriction = {
    restriction_type = "whitelist"
    locations        = ["US", "CA", "GB", "DE", "FR"]  # ISO 3166-1-alpha-2 codes
  }

  # Attach AWS WAF Web ACL for additional security
  web_acl_id = aws_wafv2_web_acl.cloudfront_waf.arn

  viewer_certificate = {
    acm_certificate_arn      = "arn:aws:acm:us-east-1:123456789012:certificate/example"
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  # Enable real-time monitoring
  create_monitoring_subscription = true
  realtime_metrics_subscription_status = "Enabled"

  # Origin Access Control
  create_origin_access_control = true
  origin_access_control = {
    s3_oac = {
      description      = "Secure S3 access"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  tags = {
    Terraform   = "true"
    Environment = "production"
    Security    = "high"
  }
}

# Example WAF Web ACL
resource "aws_wafv2_web_acl" "cloudfront_waf" {
  name  = "cloudfront-waf"
  scope = "CLOUDFRONT"  # Must be CLOUDFRONT for CloudFront distributions

  default_action {
    allow {}
  }

  rule {
    name     = "RateLimitRule"
    priority = 1

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    action {
      block {}
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
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

### Example 4: Private Content with Signed URLs

```hcl
module "cloudfront_private_content" {
  source = "terraform-aws-modules/cloudfront/aws"

  aliases = ["private.example.com"]
  comment = "Private content distribution with signed URLs"
  enabled = true

  origin = {
    private_bucket = {
      domain_name = "private-content.s3.amazonaws.com"
      origin_access_control_id = "s3_oac"
    }
  }

  default_cache_behavior = {
    target_origin_id       = "private_bucket"
    viewer_protocol_policy = "https-only"

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]

    # Configure trusted key groups for signed URLs/cookies
    trusted_key_groups = [aws_cloudfront_key_group.private_content.id]

    cache_policy_id = data.aws_cloudfront_cache_policy.caching_optimized.id
  }

  viewer_certificate = {
    acm_certificate_arn      = "arn:aws:acm:us-east-1:123456789012:certificate/example"
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  create_origin_access_control = true
  origin_access_control = {
    s3_oac = {
      description      = "Private content S3 access"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  tags = {
    Terraform   = "true"
    Environment = "production"
    ContentType = "private"
  }
}

# CloudFront key group for signed URLs
resource "aws_cloudfront_key_group" "private_content" {
  name    = "private-content-key-group"
  comment = "Key group for private content distribution"
  items   = [aws_cloudfront_public_key.private_content.id]
}

# Public key for signed URLs (private key kept secure)
resource "aws_cloudfront_public_key" "private_content" {
  name        = "private-content-public-key"
  encoded_key = file("${path.module}/public_key.pem")
  comment     = "Public key for signed URL verification"
}
```

### Example 5: CloudFront with Lambda@Edge

```hcl
module "cloudfront_lambda_edge" {
  source = "terraform-aws-modules/cloudfront/aws"

  aliases = ["dynamic.example.com"]
  comment = "CloudFront with Lambda@Edge for dynamic content"
  enabled = true
  is_ipv6_enabled = true

  origin = {
    web_server = {
      domain_name = "origin.example.com"

      custom_origin_config = {
        http_port              = 80
        https_port             = 443
        origin_protocol_policy = "https-only"
        origin_ssl_protocols   = ["TLSv1.2"]
      }
    }
  }

  default_cache_behavior = {
    target_origin_id       = "web_server"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods  = ["GET", "HEAD"]
    compress        = true

    cache_policy_id = data.aws_cloudfront_cache_policy.caching_disabled.id

    # Lambda@Edge function associations
    lambda_function_association = [
      # Viewer request - modify request before cache lookup
      {
        event_type   = "viewer-request"
        lambda_arn   = aws_lambda_function.viewer_request.qualified_arn
        include_body = false
      },
      # Origin response - modify response from origin
      {
        event_type   = "origin-response"
        lambda_arn   = aws_lambda_function.origin_response.qualified_arn
        include_body = false
      }
    ]
  }

  viewer_certificate = {
    acm_certificate_arn      = "arn:aws:acm:us-east-1:123456789012:certificate/example"
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  tags = {
    Terraform   = "true"
    Environment = "production"
    EdgeCompute = "true"
  }
}

# Example Lambda@Edge function (must be in us-east-1)
resource "aws_lambda_function" "viewer_request" {
  provider      = aws.us_east_1  # Lambda@Edge must be in us-east-1

  filename      = "lambda_edge_viewer_request.zip"
  function_name = "cloudfront-viewer-request"
  role          = aws_iam_role.lambda_edge.arn
  handler       = "index.handler"
  runtime       = "nodejs18.x"
  publish       = true  # Must publish for Lambda@Edge

  # Lambda@Edge has specific limits
  timeout     = 5
  memory_size = 128
}

resource "aws_lambda_function" "origin_response" {
  provider      = aws.us_east_1

  filename      = "lambda_edge_origin_response.zip"
  function_name = "cloudfront-origin-response"
  role          = aws_iam_role.lambda_edge.arn
  handler       = "index.handler"
  runtime       = "nodejs18.x"
  publish       = true

  timeout     = 5
  memory_size = 128
}

data "aws_cloudfront_cache_policy" "caching_disabled" {
  name = "Managed-CachingDisabled"
}
```

## Best Practices

### Security and Access Control

1. **Use Origin Access Control (OAC)**: Prefer OAC over the legacy Origin Access Identity (OAI) for S3 origins as it provides better security including support for SSE-KMS encryption and additional AWS services.
2. **Enforce HTTPS**: Always use `viewer_protocol_policy = "redirect-to-https"` or `"https-only"` to ensure encrypted communication between viewers and CloudFront.
3. **Use Latest TLS Version**: Set `minimum_protocol_version = "TLSv1.2_2021"` or higher to disable outdated SSL/TLS protocols and prevent security vulnerabilities.
4. **Implement AWS WAF**: Attach AWS WAF Web ACL to CloudFront distributions to protect against common web exploits, SQL injection, XSS, and DDoS attacks.
5. **Enable Field-Level Encryption**: For sensitive data like credit card numbers or personal information, use field-level encryption to protect data at the edge.
6. **Configure Geo-Restrictions**: Use geographic restrictions to comply with content licensing requirements or to block traffic from high-risk regions.
7. **Implement Signed URLs or Cookies**: For private content, use signed URLs or signed cookies with trusted key groups to control access with time-based or IP-based restrictions.
8. **Secure Origin Communication**: For custom origins, use HTTPS with `origin_protocol_policy = "https-only"` and configure appropriate SSL protocols and ciphers.
9. **Restrict S3 Bucket Access**: Configure S3 bucket policies to deny direct access and only allow access through CloudFront OAC/OAI.
10. **Add Security Headers**: Use Response Headers Policies to add security headers like Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, and Content-Security-Policy.

### Performance Optimization

1. **Enable Compression**: Set `compress = true` in cache behaviors to automatically compress compatible content types (text, JavaScript, CSS) for faster delivery.
2. **Use HTTP/2 and HTTP/3**: Configure `http_version = "http2and3"` to take advantage of modern protocol features like multiplexing and header compression.
3. **Optimize Cache Policies**: Use AWS Managed Cache Policies or create custom policies that balance cache hit ratio with content freshness requirements.
4. **Configure Appropriate TTLs**: Set TTL values based on content type - longer for static assets (images, fonts), shorter for dynamic content or APIs.
5. **Leverage Cache Key Normalization**: Use cache policies to normalize query strings, headers, and cookies to improve cache hit ratios.
6. **Choose Correct Price Class**: Select `PriceClass_100` (North America/Europe), `PriceClass_200` (adds Asia/Africa), or `PriceClass_All` based on your audience distribution.
7. **Implement Origin Failover**: Configure origin groups with primary and secondary origins for automatic failover and higher availability.
8. **Optimize Image Delivery**: Consider using CloudFront Functions to implement image optimization like format conversion, resizing, or quality adjustment.
9. **Use Regional Edge Caches**: CloudFront automatically uses Regional Edge Caches for less popular content, but ensure your origin can handle requests efficiently.
10. **Monitor Cache Hit Ratio**: Regularly review CloudFront metrics in CloudWatch to identify opportunities to improve cache efficiency.

### Cost Optimization

1. **Select Appropriate Price Class**: Use `PriceClass_100` for US/Europe-only traffic or `PriceClass_200` for most global scenarios to reduce costs while maintaining good coverage.
2. **Optimize Cache Hit Ratio**: Higher cache hit ratios reduce origin requests and data transfer costs - optimize cache policies and TTLs accordingly.
3. **Use Compression**: Enabling compression reduces data transfer volumes and associated costs, especially for text-based content.
4. **Implement Cache Control Headers**: Configure proper Cache-Control and Expires headers at your origin to maximize caching efficiency.
5. **Monitor Data Transfer**: Use CloudWatch and Cost Explorer to track data transfer patterns and identify opportunities for optimization.
6. **Avoid Unnecessary Invalidations**: CloudFront invalidations are limited and can incur costs - prefer versioned file names or use cache-busting query strings.
7. **Optimize Origin Access**: Reduce the number of requests that miss the cache and hit the origin by configuring appropriate cache behaviors.
8. **Use Origin Shield**: For origins with high request rates or expensive data transfer, consider enabling Origin Shield to add an additional caching layer.
9. **Consolidate Distributions**: When possible, use a single distribution with multiple origins and cache behaviors rather than multiple distributions.
10. **Review Unused Distributions**: Regularly audit and disable or delete CloudFront distributions that are no longer needed.

### Monitoring and Observability

1. **Enable Standard Logging**: Configure `logging_config` to send access logs to S3 for historical analysis, troubleshooting, and compliance auditing.
2. **Use Real-Time Logs**: For immediate insights, enable real-time logs to Kinesis Data Streams for monitoring, alerting, and real-time analytics.
3. **Enable Monitoring Subscription**: Set `create_monitoring_subscription = true` to get additional CloudWatch metrics updated every minute for faster issue detection.
4. **Create CloudWatch Alarms**: Set up alarms for key metrics like error rates (4xx/5xx), origin latency, cache hit ratio, and bytes downloaded.
5. **Monitor Cache Performance**: Track cache hit ratio, cache miss rate, and origin response times to identify performance bottlenecks.
6. **Track Error Rates**: Monitor 4xx and 5xx error rates to quickly identify issues with origins, permissions, or configuration.
7. **Use AWS X-Ray**: Enable X-Ray tracing for Lambda@Edge functions to debug and analyze performance issues at the edge.
8. **Implement Custom Metrics**: Use CloudFront Functions or Lambda@Edge to generate custom metrics for application-specific monitoring.
9. **Set Up SNS Notifications**: Configure CloudWatch alarms to send notifications via SNS for critical issues requiring immediate attention.
10. **Regular Log Analysis**: Analyze CloudFront access logs to understand traffic patterns, popular content, geographic distribution, and user behavior.

### Configuration Management

1. **Use Managed Policies**: Leverage AWS Managed Cache Policies, Origin Request Policies, and Response Headers Policies for common scenarios to simplify configuration.
2. **Version Control Configuration**: Store all Terraform configurations in version control with proper branching, review, and approval processes.
3. **Implement Staged Rollouts**: Test CloudFront configuration changes in development/staging environments before deploying to production.
4. **Document Cache Behaviors**: Clearly document the purpose and configuration of each cache behavior, especially path patterns and their routing logic.
5. **Use Meaningful Comments**: Set descriptive `comment` values for distributions to help team members understand their purpose.
6. **Tag Consistently**: Implement comprehensive tagging including Environment, Owner, Application, CostCenter for organization and cost allocation.
7. **Plan for Deployment Time**: Set `wait_for_deployment = true` (default) in Terraform to ensure distribution is fully deployed before proceeding.
8. **Use Retain on Delete**: For production distributions, consider `retain_on_delete = true` to disable rather than delete distributions as a safety measure.
9. **Modularize Configuration**: Break complex configurations into separate Terraform modules for origins, cache behaviors, and security settings.
10. **Automate Invalidations**: When needed, automate cache invalidations as part of deployment pipelines rather than manual processes.

### High Availability and Disaster Recovery

1. **Configure Origin Groups**: Use origin groups with primary and secondary origins to implement automatic failover for higher availability.
2. **Multi-Region Origins**: Place origins in multiple AWS regions and use Route 53 health checks or CloudFront origin groups for failover.
3. **Health Check Configuration**: Configure appropriate origin health check settings including intervals, timeouts, and failure thresholds.
4. **Test Failover Scenarios**: Regularly test origin failover to ensure it works as expected during actual outages.
5. **Use Multiple Origins**: Design distributions with multiple origins to isolate failures and provide redundancy for critical content.
6. **Implement Graceful Degradation**: Use custom error responses to serve fallback content (cached versions, maintenance pages) during origin failures.
7. **Monitor Origin Health**: Set up CloudWatch alarms for origin errors and latency to quickly detect and respond to issues.
8. **Document Recovery Procedures**: Maintain runbooks for common failure scenarios including origin outages, certificate expiration, and configuration errors.
9. **Regular Backup**: Back up critical CloudFront configurations and maintain documentation of distribution settings for disaster recovery.
10. **Plan for Certificate Renewal**: Implement automated ACM certificate renewal and monitoring to prevent HTTPS service disruptions.

### Lambda@Edge and CloudFront Functions

1. **Choose the Right Tool**: Use CloudFront Functions for lightweight viewer request/response modifications (<1ms), Lambda@Edge for complex logic requiring more CPU time or network calls.
2. **Optimize Function Performance**: Keep functions lightweight and fast - every millisecond of execution time adds latency to every request.
3. **Handle Errors Gracefully**: Implement proper error handling in edge functions to prevent failures from impacting user experience.
4. **Test Thoroughly**: Test edge functions extensively before deployment as they execute for every request and bugs can impact all users.
5. **Monitor Function Metrics**: Track invocation counts, errors, and duration in CloudWatch to identify performance issues.
6. **Use Appropriate Memory**: For Lambda@Edge, allocate sufficient memory (128MB minimum) but avoid over-provisioning as it increases costs.
7. **Implement Caching**: When possible, cache results within functions or use CloudFront cache to reduce function invocations.
8. **Deploy in us-east-1**: Lambda@Edge functions must be created in the us-east-1 region but will be replicated globally automatically.
9. **Version and Publish**: Always publish Lambda function versions for Lambda@Edge as CloudFront requires a qualified ARN with version.
10. **Respect Quotas and Limits**: Be aware of Lambda@Edge limits including maximum execution time (5s for viewer events, 30s for origin events) and package size.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-cloudfront
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/cloudfront/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-cloudfront/tree/master/examples
- **AWS CloudFront Documentation**: https://docs.aws.amazon.com/cloudfront/
- **CloudFront Developer Guide**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/
- **CloudFront Pricing**: https://aws.amazon.com/cloudfront/pricing/
- **Cache Policies**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-the-cache-key.html
- **Origin Access Control**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html
- **Lambda@Edge**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-edge.html
- **CloudFront Functions**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-functions.html
- **AWS WAF and CloudFront**: https://docs.aws.amazon.com/waf/latest/developerguide/cloudfront-features.html
- **Security Best Practices**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/security-best-practices.html
- **Performance Best Practices**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/ConfiguringCaching.html
- **CloudFront Monitoring**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/monitoring-using-cloudwatch.html
- **Terraform AWS Provider CloudFront**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudfront_distribution

## Notes for AI Agents

When using this module in automated workflows:

1. **Security First**: Always enforce HTTPS and use the latest TLS protocols (TLSv1.2 or higher)
2. **Use OAC Over OAI**: Prefer Origin Access Control over Origin Access Identity for S3 origins for enhanced security
3. **Enable Compression**: Always set `compress = true` for better performance and reduced costs
4. **Choose Appropriate Price Class**: Balance cost and performance by selecting the right price class for your user base
5. **Implement Proper Caching**: Configure cache policies and TTLs appropriate for content type (static vs dynamic)
6. **Tag Consistently**: Implement comprehensive tagging including Environment, Owner, Application, and CostCenter
7. **Monitor Cache Hit Ratio**: Track cache performance metrics and optimize configurations to maximize cache hits
8. **Test Configuration Changes**: Always test CloudFront configuration changes in non-production environments first
9. **Use Managed Policies**: Leverage AWS Managed Policies for cache, origin requests, and response headers when possible
10. **Enable Logging**: Configure standard logging to S3 for compliance, troubleshooting, and traffic analysis
11. **Plan for Deployment Time**: CloudFront changes can take 15-30 minutes to propagate globally - plan accordingly
12. **Document Complex Behaviors**: Clearly document path patterns, cache behaviors, and their purposes for team understanding
