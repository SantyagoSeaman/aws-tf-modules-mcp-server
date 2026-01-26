# Terraform AWS CloudFront Module

## Module Information

- **Module Name**: `cloudfront`
- **Source**: `terraform-aws-modules/cloudfront/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-cloudfront
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/cloudfront/aws/latest
- **Latest Version**: 6.3.0
- **Purpose**: Creates AWS CloudFront CDN distributions with comprehensive support for origins, cache behaviors, edge functions, logging, and security features
- **Service**: AWS CloudFront (Content Delivery Network)
- **Category**: Networking, Content Delivery, Performance
- **Keywords**: cloudfront, cdn, distribution, s3-origin, custom-origin, vpc-origin, cache-behavior, origin-access-control, lambda-edge, cloudfront-functions, waf, response-headers-policy, v2-logging, origin-group, geo-restriction, https, http2, http3
- **Use For**: Static website hosting, dynamic content acceleration, API acceleration, video streaming, software distribution, multi-origin failover, edge computing, private content delivery, DDoS protection with WAF

## Description

This Terraform module creates and manages AWS CloudFront distributions for global content delivery. CloudFront caches content at edge locations worldwide, reducing latency for websites, APIs, video streaming, and static assets. The module provides full control over distribution configuration, caching behaviors, security, and integration with other AWS services.

The module supports multiple origin types: S3 buckets with Origin Access Control (OAC), custom HTTP/HTTPS origins, and VPC origins for routing to private EC2/ECS/EKS resources. It handles cache behaviors with path pattern matching, SSL/TLS certificates via ACM, origin groups for automatic failover, and security features including geo-restrictions and AWS WAF integration. Modern protocols HTTP/2 and HTTP/3 are supported.

Key capabilities include CloudFront Functions and Lambda@Edge for edge computing, response headers policies for CORS and security headers, V2 logging with CloudWatch Logs or S3 Parquet format, and real-time CloudWatch metrics. The module creates origin access controls, manages viewer certificates, and supports continuous deployment policies for blue/green deployments.

## Key Features

- **Multiple Origin Types**: S3 buckets, custom HTTP/HTTPS origins, and VPC origins for private resources
- **Origin Access Control (OAC)**: Modern S3 access with SigV4 signing (replaces legacy OAI)
- **VPC Origins**: Route traffic to private EC2/ECS/EKS resources without public exposure
- **Origin Groups**: Automatic failover between origins on HTTP errors (403, 404, 500, 502)
- **Origin Shield**: Additional caching layer to reduce origin load and improve cache hit ratio
- **Cache Behaviors**: Default and ordered behaviors with path pattern matching and managed policies
- **CloudFront Functions**: Lightweight JavaScript edge compute with KeyValueStore support
- **Lambda@Edge**: Full Lambda functions for complex viewer/origin request/response processing
- **Response Headers Policies**: CORS configuration, security headers, custom headers, header removal
- **V2 Logging**: CloudWatch Logs or S3 with Parquet format for cost-effective log analysis
- **Real-Time Metrics**: CloudWatch monitoring subscription for minute-level metrics
- **AWS WAF Integration**: Attach Web ACLs for DDoS protection and request filtering
- **Geo-Restrictions**: Whitelist or blacklist content by country code
- **HTTP/2 and HTTP/3**: Modern protocol support for improved performance
- **Custom Error Responses**: Custom error pages with configurable response codes and caching
- **Viewer Certificates**: ACM certificate integration with SNI support and TLS version control
- **Continuous Deployment**: Blue/green deployments with staging distributions and traffic splitting

## Main Use Cases

1. **Static Website Hosting**: Serve S3-hosted websites with global caching and custom domains
2. **API Acceleration**: Reduce latency for API Gateway or custom API backends
3. **Video Streaming**: Distribute streaming content with adaptive bitrate and geo-restrictions
4. **Software Distribution**: Deliver downloads and updates with high availability
5. **Multi-Origin Failover**: Automatic failover between origins for high availability
6. **Private Content Delivery**: Signed URLs/cookies for premium or restricted content
7. **Edge Computing**: Request/response transformation with CloudFront Functions or Lambda@Edge
8. **Security Layer**: DDoS protection and WAF integration for web applications
9. **VPC Origin Access**: Serve content from private resources without public exposure

## Submodules

This module does not include submodules. It provides a single root module for CloudFront distribution creation and management.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether resources are created |
| `aliases` | `list(string)` | `null` | Alternate domain names (CNAMEs) for the distribution |
| `comment` | `string` | `null` | Distribution description/comment |
| `enabled` | `bool` | `true` | Whether distribution accepts end user requests |
| `is_ipv6_enabled` | `bool` | `true` | Enable IPv6 support |
| `http_version` | `string` | `"http2"` | Maximum HTTP version (`http1.1`, `http2`, `http2and3`) |
| `price_class` | `string` | `null` | Price class (`PriceClass_All`, `PriceClass_200`, `PriceClass_100`) |
| `default_root_object` | `string` | `null` | Object returned for root URL (e.g., `index.html`) |
| `origin` | `map(object)` | `{}` | Map of origin configurations (S3, custom, VPC) |
| `origin_access_control` | `map(object)` | S3 default | Origin access control settings with SigV4 signing |
| `vpc_origin` | `map(object)` | `null` | VPC origin configurations for private resources |
| `origin_group` | `map(object)` | `null` | Origin group failover configurations |
| `default_cache_behavior` | `object` | **Required** | Default cache behavior configuration |
| `ordered_cache_behavior` | `list(object)` | `[]` | Ordered list of cache behaviors by path pattern |
| `viewer_certificate` | `object` | `{}` | SSL/TLS certificate configuration |
| `restrictions` | `object` | No restrictions | Geo-restriction configuration |
| `custom_error_response` | `list(object)` | `null` | Custom error response pages |
| `logging_config` | `object` | `null` | Legacy S3 logging configuration |
| `enable_v2_logging` | `bool` | `false` | Enable V2 logging (CloudWatch/S3 Parquet) |
| `v2_logging` | `object` | `null` | V2 logging destination configuration |
| `web_acl_id` | `string` | `null` | AWS WAF Web ACL ID to attach |
| `cloudfront_functions` | `map(object)` | `null` | CloudFront Functions to create |
| `response_headers_policies` | `map(object)` | `null` | Response headers policies to create |
| `create_monitoring_subscription` | `bool` | `false` | Enable CloudWatch monitoring subscription |
| `realtime_metrics_subscription_status` | `string` | `"Enabled"` | Real-time metrics status |
| `wait_for_deployment` | `bool` | `null` | Wait for distribution deployment to complete |
| `retain_on_delete` | `bool` | `null` | Disable instead of delete on removal |
| `staging` | `bool` | `null` | Mark as staging distribution |
| `tags` | `map(string)` | `{}` | Tags for all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `cloudfront_distribution_id` | The identifier for the distribution |
| `cloudfront_distribution_arn` | The ARN for the distribution |
| `cloudfront_distribution_domain_name` | The CloudFront domain name (e.g., `d111111abcdef8.cloudfront.net`) |
| `cloudfront_distribution_hosted_zone_id` | Route 53 zone ID for Alias records |
| `cloudfront_distribution_status` | Distribution deployment status |
| `cloudfront_distribution_etag` | Current version of the distribution config |
| `cloudfront_origin_access_controls` | Created origin access controls |
| `cloudfront_vpc_origins` | Created VPC origin IDs |
| `cloudfront_response_headers_policies` | Created response headers policies |
| `cloudfront_functions` | Created CloudFront Functions |
| `cloudfront_monitoring_subscription_id` | CloudWatch monitoring subscription ID |

## Usage Examples

### Example 1: S3 Origin with Origin Access Control (OAC)

```hcl
module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "6.3.0"

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
      origin_access_control_key = "s3"  # References OAC key above
    }
  }

  default_cache_behavior = {
    target_origin_id       = "s3_bucket"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true
    cache_policy_name      = "Managed-CachingOptimized"
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

### Example 2: Multi-Origin with Failover and V2 Logging

```hcl
module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "6.3.0"

  aliases         = ["app.example.com"]
  comment         = "Multi-origin CDN with failover"
  enabled         = true
  http_version    = "http2and3"
  is_ipv6_enabled = true

  create_monitoring_subscription = true

  # V2 Logging to S3 in Parquet format
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
        https_port             = 443
        origin_protocol_policy = "https-only"
        origin_ssl_protocols   = ["TLSv1.2"]
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
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_name      = "Managed-CachingDisabled"
  }

  ordered_cache_behavior = [
    {
      path_pattern           = "/static/*"
      target_origin_id       = "s3_static"
      viewer_protocol_policy = "redirect-to-https"
      allowed_methods        = ["GET", "HEAD"]
      cached_methods         = ["GET", "HEAD"]
      cache_policy_name      = "Managed-CachingOptimized"
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

### Example 3: WAF Integration and Geo-Restrictions

```hcl
module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "6.3.0"

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
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true
    cache_policy_name      = "Managed-CachingOptimized"
  }

  # Geo-restrictions
  restrictions = {
    geo_restriction = {
      restriction_type = "whitelist"
      locations        = ["US", "CA", "GB", "DE"]
    }
  }

  # AWS WAF Web ACL
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

### Example 4: Private Content with Signed URLs

```hcl
module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "6.3.0"

  aliases = ["private.example.com"]
  comment = "Private content with signed URLs"
  enabled = true

  origin_access_control = {
    s3 = {
      description      = "Private content S3 access"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  origin = {
    private_bucket = {
      domain_name               = module.s3.s3_bucket_bucket_regional_domain_name
      origin_access_control_key = "s3"
    }
  }

  default_cache_behavior = {
    target_origin_id       = "private_bucket"
    viewer_protocol_policy = "https-only"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    trusted_key_groups     = [aws_cloudfront_key_group.private.id]
    cache_policy_name      = "Managed-CachingOptimized"
  }

  viewer_certificate = {
    acm_certificate_arn = module.acm.acm_certificate_arn
    ssl_support_method  = "sni-only"
  }

  tags = {
    Environment = "production"
    ContentType = "private"
  }
}

# Key group for signed URLs
resource "aws_cloudfront_key_group" "private" {
  name  = "private-content-keys"
  items = [aws_cloudfront_public_key.private.id]
}

resource "aws_cloudfront_public_key" "private" {
  name        = "private-content-key"
  encoded_key = file("${path.module}/public_key.pem")
}
```

### Example 5: CloudFront Functions and Response Headers Policy

```hcl
module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "6.3.0"

  aliases = ["app.example.com"]
  comment = "CDN with CloudFront Functions"
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
    target_origin_id           = "s3_bucket"
    viewer_protocol_policy     = "redirect-to-https"
    allowed_methods            = ["GET", "HEAD"]
    cached_methods             = ["GET", "HEAD"]
    cache_policy_name          = "Managed-CachingOptimized"
    response_headers_policy_key = "security_headers"

    function_association = [
      {
        event_type   = "viewer-request"
        function_key = "url_rewrite"
      }
    ]
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

### Example 6: Lambda@Edge Integration

```hcl
module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "6.3.0"

  aliases = ["api.example.com"]
  comment = "CDN with Lambda@Edge"
  enabled = true

  origin = {
    api = {
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
    target_origin_id       = "api"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_name      = "Managed-CachingDisabled"

    lambda_function_association = [
      {
        event_type   = "viewer-request"
        lambda_arn   = aws_lambda_function.auth.qualified_arn
        include_body = false
      }
    ]
  }

  viewer_certificate = {
    acm_certificate_arn = module.acm.acm_certificate_arn
    ssl_support_method  = "sni-only"
  }

  tags = {
    Environment = "production"
  }
}

# Lambda@Edge must be in us-east-1 and published
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

## Best Practices

### Security

1. **Use Origin Access Control (OAC)**: Prefer OAC over legacy OAI for S3 origins - supports SSE-KMS encryption
2. **Enforce HTTPS**: Use `viewer_protocol_policy = "redirect-to-https"` or `"https-only"`
3. **Use TLSv1.2 minimum**: Default is TLSv1.2_2025; avoid older protocols
4. **Implement AWS WAF**: Attach Web ACL for DDoS protection and request filtering
5. **Add security headers**: Use response headers policies for HSTS, X-Frame-Options, CSP
6. **Geo-restrictions**: Restrict content by country when required
7. **Signed URLs/cookies**: Use trusted key groups for private content access
8. **Secure custom origins**: Use `origin_protocol_policy = "https-only"` with TLSv1.2

### Performance

1. **Enable compression**: Set `compress = true` in cache behaviors
2. **Use HTTP/2 or HTTP/3**: Configure `http_version = "http2and3"`
3. **Use managed cache policies**: `Managed-CachingOptimized` for static, `Managed-CachingDisabled` for dynamic
4. **Enable Origin Shield**: Additional caching layer reduces origin load
5. **Configure origin groups**: Automatic failover on HTTP errors (403, 404, 500, 502)
6. **Choose price class wisely**: `PriceClass_100` for US/Europe, `PriceClass_200` for most global use cases

### Cost Optimization

1. **Optimize cache hit ratio**: Higher hit ratio = lower origin costs
2. **Avoid invalidations**: Use versioned file names or cache-busting query strings
3. **Enable V2 logging with Parquet**: More cost-effective than standard logging for analytics
4. **Consolidate distributions**: Use multiple origins in one distribution when possible

### Monitoring

1. **Enable monitoring subscription**: Minute-level CloudWatch metrics
2. **Use V2 logging**: CloudWatch Logs or S3 with Parquet for efficient log analysis
3. **Create CloudWatch alarms**: Monitor error rates, origin latency, cache hit ratio
4. **Track function metrics**: Monitor CloudFront Functions and Lambda@Edge invocations

### Edge Computing

1. **CloudFront Functions vs Lambda@Edge**: Use Functions for lightweight operations (<1ms), Lambda@Edge for complex logic
2. **Lambda@Edge in us-east-1**: Must be created in us-east-1 and published (not $LATEST)
3. **Respect limits**: Functions have 5s viewer/30s origin timeout limits
4. **Test thoroughly**: Edge code runs on every request globally

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-cloudfront
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/cloudfront/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-cloudfront/tree/master/examples
- **CloudFront Developer Guide**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/
- **Origin Access Control**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html
- **CloudFront Functions**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-functions.html
- **Lambda@Edge**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-edge.html
- **CloudFront Pricing**: https://aws.amazon.com/cloudfront/pricing/

## Notes for AI Agents

When using this module:

1. **Use OAC for S3**: Set `origin_access_control_key` to reference an OAC (not OAI)
2. **Use managed cache policies**: Reference by name (`cache_policy_name = "Managed-CachingOptimized"`)
3. **ACM certificates**: Must be in `us-east-1` for CloudFront
4. **Lambda@Edge**: Functions must be in `us-east-1` and published (not `$LATEST`)
5. **Geo-restrictions**: Use `restrictions.geo_restriction` (not top-level `geo_restriction`)
6. **Origin groups for failover**: Configure `failover_criteria.status_codes` for automatic failover
7. **V2 logging recommended**: Use `v2_logging` with Parquet format for cost-effective analytics
8. **Deployment time**: Changes take 5-15 minutes to propagate globally
9. **S3 bucket policy**: Must allow CloudFront OAC access (module doesn't create bucket policy)
10. **Route 53 alias**: Use `cloudfront_distribution_hosted_zone_id` for Alias records
