# Terraform AWS API Gateway v2 Module

## Module Information

- **Module Name**: `apigateway-v2`
- **Source**: `terraform-aws-modules/apigateway-v2/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/latest
- **Latest Version**: 6.1.0
- **Purpose**: Terraform module to create AWS API Gateway v2 (HTTP and WebSocket APIs) with support for custom domains, authorizers, VPC links, and integrations
- **Service**: AWS API Gateway v2 (HTTP APIs and WebSocket APIs)
- **Category**: Serverless, API Management, Integration
- **Keywords**: api-gateway, http-api, websocket-api, lambda-integration, jwt-authorizer, cors, custom-domain, vpc-link, serverless, api-routing, access-logging, throttling, mutual-tls, route53, acm

## Description

AWS API Gateway v2 is Amazon's managed API service for creating HTTP and WebSocket APIs at scale. This Terraform module provides a comprehensive solution for deploying API Gateway v2 resources with both protocol types. HTTP APIs offer up to 71% cost savings compared to REST APIs and support features like JWT authorizers, CORS, and Lambda integrations. WebSocket APIs enable real-time bidirectional communication for chat applications, streaming, and live updates.

The module supports multiple integration types: AWS Lambda function invocations via AWS_PROXY, HTTP proxy integrations to backend services, and VPC link integrations for private resource access. It provides flexible authentication through JWT authorizers (Cognito, Auth0), custom Lambda authorizers, and AWS IAM. The module handles the complete lifecycle including stage management, deployment automation, access logging, and custom domain mapping with Route 53 and ACM certificate integration.

Built as part of the serverless.tf framework, this module follows AWS best practices and provides advanced features such as mutual TLS authentication, throttling and rate limiting, stage variables for environment-specific configurations, and CloudWatch integration for monitoring. The module supports multi-environment deployments with conditional resource creation and extensive tagging capabilities.

## Key Features

- **HTTP API Support**: Cost-effective HTTP APIs with up to 71% savings compared to REST APIs
- **WebSocket API Support**: Real-time bidirectional communication for chat, gaming, streaming
- **Lambda Integration**: Seamless AWS_PROXY integration with Lambda functions
- **HTTP Proxy Integration**: Route requests to backend HTTP services
- **VPC Link Integration**: Private integrations to internal ALB/NLB without public exposure
- **JWT Authorizers**: Built-in JWT validation for OAuth2/OpenID Connect (Cognito, Auth0)
- **Custom Lambda Authorizers**: REQUEST authorizers for custom authorization logic
- **CORS Configuration**: Flexible cross-origin resource sharing settings
- **Custom Domain Names**: Route 53 integration with ACM certificate management
- **Mutual TLS**: Client certificate validation with S3-stored truststore
- **Route Configuration**: HTTP methods, route keys, and per-route settings
- **Stage Management**: Stage-specific configurations, variables, and throttling
- **Auto Deployment**: Automatic API deployment on configuration changes
- **Access Logging**: CloudWatch Logs integration with customizable log formats
- **Throttling**: Request rate limiting at stage and route levels
- **Conditional Creation**: Fine-grained control over which resources to create

## Main Use Cases

1. **Serverless REST APIs**: RESTful APIs backed by Lambda functions
2. **Microservices Gateway**: Unified API gateway routing to multiple services
3. **WebSocket Applications**: Real-time bidirectional communication (chat, gaming)
4. **API Consolidation**: Multiple backend services behind single endpoint
5. **Mobile App Backends**: Secure API endpoints with JWT authentication
6. **Private API Access**: Expose private VPC resources via VPC links
7. **Multi-Tenant APIs**: Custom domain mapping with tenant isolation
8. **Event-Driven Architectures**: WebSocket connections for real-time notifications

## Submodules

### 1. wrappers

- **Purpose**: Manage multiple API Gateway instances without duplicating configuration
- **Source**: `terraform-aws-modules/apigateway-v2/aws//wrappers`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/latest/submodules/wrappers
- **Key Features**: Bulk API creation, shared defaults, Terragrunt compatibility
- **Use Cases**: Multi-environment deployments, multi-tenant SaaS APIs

#### Usage Example

```hcl
module "api_gateways" {
  source  = "terraform-aws-modules/apigateway-v2/aws//wrappers"
  version = "~> 6.1"

  defaults = {
    protocol_type = "HTTP"
    tags = {
      Terraform = "true"
    }
  }

  items = {
    api-dev = {
      name        = "my-api-dev"
      description = "Development API"
    }
    api-prod = {
      name        = "my-api-prod"
      description = "Production API"
    }
  }
}
```

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | - | **Required**. API name (max 128 chars) |
| `protocol_type` | `string` | `"HTTP"` | API protocol: `HTTP` or `WEBSOCKET` |
| `description` | `string` | `null` | API description (max 1024 chars) |
| `cors_configuration` | `object` | `null` | CORS settings: allow_origins, allow_methods, allow_headers |
| `domain_name` | `string` | `""` | Custom domain name for the API |
| `hosted_zone_name` | `string` | `null` | Route 53 hosted zone for domain records |
| `create_certificate` | `bool` | `true` | Create ACM certificate for custom domain |
| `domain_name_certificate_arn` | `string` | `null` | Existing ACM certificate ARN |
| `authorizers` | `map(object)` | `{}` | Map of JWT/REQUEST authorizers |
| `routes` | `map(object)` | `{}` | Map of routes with integrations |
| `stage_name` | `string` | `"$default"` | Stage name (1-128 chars) |
| `stage_variables` | `map(string)` | `{}` | Stage-specific variables |
| `stage_access_log_settings` | `object` | `{}` | CloudWatch access logging config |
| `stage_default_route_settings` | `object` | `{}` | Default throttling and metrics |
| `vpc_links` | `map(object)` | `{}` | VPC Link definitions for private integrations |
| `mutual_tls_authentication` | `map(string)` | `{}` | mTLS config with S3 truststore |
| `disable_execute_api_endpoint` | `bool` | `null` | Force traffic through custom domain |
| `create` | `bool` | `true` | Control resource creation |
| `tags` | `map(string)` | `{}` | Tags for all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `api_id` | The API identifier |
| `api_endpoint` | URI of the API (https:// for HTTP, wss:// for WebSocket) |
| `api_arn` | The ARN of the API |
| `api_execution_arn` | ARN prefix for Lambda permissions |
| `stage_id` | The stage identifier |
| `stage_invoke_url` | URL to invoke the API via stage |
| `domain_name_target_domain_name` | Target domain for Route 53/CloudFront |
| `acm_certificate_arn` | Created ACM certificate ARN |
| `authorizers` | Map of created authorizers |
| `integrations` | Map of created integrations |
| `routes` | Map of created routes |
| `vpc_links` | Map of created VPC links |

## Usage Examples

### Basic HTTP API

```hcl
module "api_gateway" {
  source  = "terraform-aws-modules/apigateway-v2/aws"
  version = "~> 6.1"

  name          = "my-http-api"
  description   = "My HTTP API Gateway"
  protocol_type = "HTTP"

  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}
```

### HTTP API with Lambda Integration and JWT Auth

```hcl
module "api_gateway" {
  source  = "terraform-aws-modules/apigateway-v2/aws"
  version = "~> 6.1"

  name          = "my-http-api"
  description   = "HTTP API with Lambda backend"
  protocol_type = "HTTP"

  # CORS Configuration
  cors_configuration = {
    allow_headers = ["content-type", "x-amz-date", "authorization"]
    allow_methods = ["GET", "POST", "PUT", "DELETE"]
    allow_origins = ["https://example.com"]
  }

  # Custom Domain
  domain_name      = "api.example.com"
  hosted_zone_name = "example.com"

  # Access Logging
  stage_access_log_settings = {
    create_log_group            = true
    log_group_retention_in_days = 7
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      responseLength = "$context.responseLength"
    })
  }

  # Throttling
  stage_default_route_settings = {
    detailed_metrics_enabled = true
    throttling_burst_limit   = 100
    throttling_rate_limit    = 100
  }

  # JWT Authorizer (Cognito)
  authorizers = {
    cognito = {
      authorizer_type  = "JWT"
      identity_sources = ["$request.header.Authorization"]
      name             = "cognito-authorizer"
      jwt_configuration = {
        audience = ["my-client-id"]
        issuer   = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxx"
      }
    }
  }

  # Routes with Integrations
  routes = {
    "POST /items" = {
      authorizer_key = "cognito"
      integration = {
        uri                    = module.lambda_create.lambda_function_arn
        payload_format_version = "2.0"
        timeout_milliseconds   = 12000
      }
    }

    "GET /items/{id}" = {
      authorizer_key = "cognito"
      integration = {
        uri                    = module.lambda_get.lambda_function_arn
        payload_format_version = "2.0"
      }
    }

    "GET /public" = {
      authorization_type = "NONE"
      integration = {
        uri = module.lambda_public.lambda_function_arn
      }
    }

    "$default" = {
      integration = {
        uri = module.lambda_default.lambda_function_arn
      }
    }
  }

  tags = {
    Environment = "production"
  }
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gw" {
  for_each = toset(["create", "get", "public", "default"])

  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module["lambda_${each.key}"].lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${module.api_gateway.api_execution_arn}/*/*"
}
```

### HTTP API with VPC Link (Private Integration)

```hcl
module "api_gateway" {
  source  = "terraform-aws-modules/apigateway-v2/aws"
  version = "~> 6.1"

  name          = "vpc-link-http-api"
  description   = "HTTP API with VPC Link to internal ALB"
  protocol_type = "HTTP"

  # VPC Link Definition
  vpc_links = {
    my-vpc = {
      name               = "my-vpc-link"
      security_group_ids = [aws_security_group.api_gateway.id]
      subnet_ids         = module.vpc.private_subnets
    }
  }

  # Routes with VPC Link Integration
  routes = {
    "ANY /api/{proxy+}" = {
      integration = {
        connection_type = "VPC_LINK"
        vpc_link_key    = "my-vpc"
        uri             = aws_lb_listener.internal.arn
        type            = "HTTP_PROXY"
        method          = "ANY"
      }
    }

    "$default" = {
      integration = {
        uri = module.lambda_default.lambda_function_arn
      }
    }
  }

  tags = {
    Environment = "dev"
  }
}
```

### WebSocket API

```hcl
module "websocket_api" {
  source  = "terraform-aws-modules/apigateway-v2/aws"
  version = "~> 6.1"

  name                       = "my-websocket-api"
  description                = "WebSocket API for real-time communication"
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"

  # Access Logging
  stage_access_log_settings = {
    create_log_group            = true
    log_group_retention_in_days = 7
  }

  stage_default_route_settings = {
    detailed_metrics_enabled = true
    throttling_burst_limit   = 100
    throttling_rate_limit    = 100
  }

  # WebSocket Routes
  routes = {
    "$connect" = {
      integration = {
        uri = module.lambda_connect.lambda_function_arn
      }
    }

    "$disconnect" = {
      integration = {
        uri = module.lambda_disconnect.lambda_function_arn
      }
    }

    "sendmessage" = {
      integration = {
        uri = module.lambda_send.lambda_function_arn
      }
      route_response = {
        key = "$default"
      }
    }

    "$default" = {
      integration = {
        uri = module.lambda_default.lambda_function_arn
      }
    }
  }

  tags = {
    Environment = "dev"
  }
}
```

## Best Practices

### API Configuration

1. **Choose HTTP APIs for Cost Efficiency**: Use HTTP APIs instead of REST APIs for 71% cost savings when advanced features aren't required
2. **Use WebSocket for Bidirectional**: Deploy WebSocket APIs for real-time communication rather than polling HTTP endpoints
3. **Design RESTful Routes**: Follow conventions like `GET /users`, `POST /users`, `GET /users/{id}`
4. **Implement API Versioning**: Use path-based versioning (`/v1/`, `/v2/`) for major API changes
5. **Configure CORS Appropriately**: Use specific allowed origins in production, not wildcards

### Integration Configuration

1. **Prefer AWS_PROXY for Lambda**: Automatically passes request context and simplifies response handling
2. **Use Payload Format 2.0**: Simplified event structure for Lambda integrations
3. **Set Appropriate Timeouts**: Configure based on backend response times (default 30s for HTTP, 29s for Lambda)
4. **Use VPC Links for Private Resources**: Keep backend resources off the public internet

### Security

1. **Enable JWT Authorizers**: Use for OAuth2/OpenID Connect authentication (Cognito, Auth0)
2. **Implement Least Privilege**: Configure authorizer scopes to grant minimum permissions per route
3. **Use Mutual TLS**: Enable mTLS for APIs requiring client certificate validation
4. **Disable Execute API Endpoint**: Set `disable_execute_api_endpoint = true` to force traffic through custom domain
5. **Apply Throttling**: Configure `throttling_burst_limit` and `throttling_rate_limit` to prevent abuse
6. **Enable Access Logging**: Always enable for security auditing and threat detection

### Monitoring

1. **Enable Access Logging**: Configure with request ID, IP, method, route, status, response length
2. **Use Structured Logging**: Format logs in JSON for easier parsing with log analytics tools
3. **Set Up CloudWatch Alarms**: Monitor 4XX/5XX errors, latency, and throttled requests
4. **Enable X-Ray Tracing**: Use for distributed tracing across API Gateway and Lambda

### Cost Optimization

1. **Choose HTTP APIs Over REST**: Up to 71% cost savings
2. **Use Regional Endpoints**: Cheaper than edge-optimized and suitable for most use cases
3. **Optimize Logging**: Set appropriate CloudWatch log retention periods
4. **Batch API Calls**: Design clients to batch operations to reduce request count

### Deployment

1. **Enable Auto-Deployment for Dev**: Streamlines testing workflows
2. **Use Stage Variables**: Parameterize backend endpoints across dev, staging, production
3. **Version Pin Module**: Use `version = "~> 6.1"` to prevent unexpected changes
4. **Grant Lambda Permissions**: Add `aws_lambda_permission` for each Lambda integration

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2/tree/master/examples
- **AWS API Gateway v2 Documentation**: https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html
- **HTTP APIs Documentation**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html
- **WebSocket APIs Documentation**: https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api.html
- **JWT Authorizers**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html
- **VPC Links**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vpc-links.html
- **API Gateway Pricing**: https://aws.amazon.com/api-gateway/pricing/
- **Serverless.tf Framework**: https://serverless.tf/

## Notes for AI Agents

When using this module in automated workflows:

1. **Protocol Selection**: Use `protocol_type = "HTTP"` for REST APIs, `protocol_type = "WEBSOCKET"` for bidirectional communication
2. **Integration Type**: Use `AWS_PROXY` for Lambda (default), `HTTP_PROXY` for backend HTTP services
3. **Payload Format**: Set `payload_format_version = "2.0"` for Lambda integrations
4. **Route Format**: Define routes as `"{METHOD} {path}"` (e.g., `"GET /users"`, `"POST /orders/{id}"`)
5. **Lambda Permissions**: Always add `aws_lambda_permission` resources granting API Gateway invoke access
6. **CORS in Production**: Configure specific origins, methods, and headers rather than wildcards
7. **Authorizer Reference**: Use `authorizer_key` in routes to reference authorizers defined in `authorizers` map
8. **VPC Link Reference**: Use `vpc_link_key` in integration to reference VPC links defined in `vpc_links` map
9. **Custom Domain**: Requires `domain_name`, `hosted_zone_name`, and either `create_certificate = true` or existing `domain_name_certificate_arn`
10. **Access Logging**: Set `stage_access_log_settings.create_log_group = true` for automatic CloudWatch log group creation
11. **Throttling**: Configure both `stage_default_route_settings` (stage-level) and per-route `throttling_*` settings
12. **WebSocket Routes**: Must include `$connect`, `$disconnect`, and `$default` routes at minimum
13. **Certificate for Private Zones**: Use existing certificate ARN when `private_zone = true` (validation fails for private zones)
14. **Multi-Region**: Deploy identical configurations to multiple regions for high availability
