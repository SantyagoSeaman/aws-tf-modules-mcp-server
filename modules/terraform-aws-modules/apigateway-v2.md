# Terraform AWS API Gateway v2 Module

## Module Information

- **Module Name**: `apigateway-v2`
- **Source**: `terraform-aws-modules/apigateway-v2/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/latest
- **Latest Version**: 6.1.0
- **Compatibility**: Terraform >= 1.5.7, AWS provider >= 6.28. Since v6.0.0 the module requires AWS provider v6.x — pin `~> 6.1` when generating configs.
- **Purpose**: Terraform module that creates AWS API Gateway v2 resources (HTTP APIs and WebSocket APIs) — the API, routes, integrations, authorizers, stage, custom domain, and VPC links
- **Service**: Amazon API Gateway v2 (HTTP APIs and WebSocket APIs)
- **Category**: Serverless, API Management, Networking
- **Keywords**: api-gateway, http-api, websocket-api, apigatewayv2, lambda-integration, jwt-authorizer, cors, custom-domain, vpc-link, route53, acm, mutual-tls, throttling, access-logging
- **Use For**: serverless REST/HTTP API backends, real-time WebSocket applications (chat, gaming, live dashboards), Lambda-backed microservices gateways, private VPC integrations to internal ALB/NLB, mobile app backends with JWT/Cognito auth, multi-tenant APIs with custom/wildcard subdomains, API consolidation behind one endpoint, event-driven notification systems

## Description

This module provisions Amazon API Gateway v2 resources for both HTTP APIs and WebSocket APIs (`protocol_type = "HTTP"` or `"WEBSOCKET"`). It manages the API itself, routes and their integrations (Lambda `AWS_PROXY`, `HTTP_PROXY`, private `VPC_LINK`, or an imported OpenAPI `body`), authorizers (`JWT` or `REQUEST`/Lambda), a deployment stage with access logging and throttling, VPC Links for reaching resources inside a VPC without exposing them publicly, and an optional custom domain name with Route 53 alias records and an ACM certificate (created internally via the `terraform-aws-modules/acm/aws` submodule, or supplied as an existing certificate ARN).

HTTP APIs are the modern, lower-cost replacement for REST APIs (up to ~71% cheaper) and support JWT authorizers, CORS, and simplified Lambda payload format 2.0. WebSocket APIs provide persistent, bidirectional connections identified by `$connect`/`$disconnect`/`$default`/custom routes, suited for chat, gaming, and streaming use cases. The module is part of the [serverless.tf](https://serverless.tf) framework and is commonly composed with the `terraform-aws-modules/lambda/aws` module for backend functions and `terraform-aws-modules/vpc/aws` / `security-group` modules for VPC Link integrations.

Every resource group (API, domain name, domain records, certificate, routes/integrations, stage) has its own `create_*` toggle for conditional creation, allowing the module to manage a subset of resources (e.g., routes only, or domain mapping onto an API managed elsewhere). Custom domains support wildcard subdomains (`*.example.com` with a `subdomains` list) and private-hosted-zone Route 53 records.

## Key Features

- **HTTP API and WebSocket API**: Single module handles both protocol types via `protocol_type`
- **Multiple Integration Types**: Lambda `AWS_PROXY`, `HTTP_PROXY` backend services, private `VPC_LINK` (ALB/NLB), and OpenAPI `body` import
- **JWT & Lambda Authorizers**: Built-in `JWT` authorizers (Cognito, Auth0, Azure AD) and `REQUEST` (custom Lambda) authorizers, referenced per-route via `authorizer_key`
- **VPC Links**: Private integration to internal load balancers without public exposure
- **Custom Domains**: Route 53 alias records, ACM certificate creation (or bring-your-own ARN), wildcard subdomains, private hosted zones
- **Mutual TLS**: Client-certificate validation via S3-hosted truststore on the domain name
- **CORS Configuration**: Full CORS control for HTTP APIs (`allow_origins`, `allow_methods`, `allow_headers`, credentials, max age)
- **Access Logging & Throttling**: CloudWatch access logs with custom JSON format, stage- and route-level throttling/detailed metrics
- **Quick Create**: `target`/`route_key` shortcut for a single catch-all route + integration + auto-deployed stage
- **Conditional Creation**: Independent `create_*` toggles for API, domain name, domain records, certificate, routes/integrations, and stage
- **Wrapper Submodule**: Bulk-create multiple API Gateways from a single module block (Terragrunt-friendly)

## Main Use Cases

1. **Serverless REST/HTTP APIs**: Lambda-backed HTTP APIs with JWT authentication
2. **Real-Time WebSocket Apps**: Chat, gaming, or live-notification backends
3. **Microservices Gateway**: Single entry point routing to multiple Lambda/HTTP backends
4. **Private VPC Integrations**: Expose an internal ALB/NLB through VPC Links without public IPs
5. **Multi-Tenant SaaS APIs**: Wildcard custom domains mapped to per-tenant subdomains
6. **Mobile/Web App Backends**: JWT-secured HTTP API with Cognito or Auth0
7. **API Consolidation**: Route legacy and new backend services behind one custom domain
8. **mTLS-Protected APIs**: Client-certificate authentication for B2B integrations

## Submodules

### 1. wrappers

- **Purpose**: Create and manage multiple API Gateway instances from one module block without duplicating configuration
- **Source**: `terraform-aws-modules/apigateway-v2/aws//wrappers`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/latest/submodules/wrappers
- **Key Features**: `for_each`-driven bulk creation, shared `defaults` merged per-item, Terragrunt-compatible (`for_each` is not natively supported by Terragrunt)
- **Use Cases**: Multi-environment API deployments, multi-tenant SaaS APIs, Terragrunt-managed infrastructure

## Main Module: API Gateway v2

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | API name (max 128 chars) |
| `protocol_type` | `string` | `"HTTP"` | API protocol: `HTTP` or `WEBSOCKET` |
| `description` | `string` | `null` | API description (max 1024 chars) |
| `body` | `string` | `null` | OpenAPI spec defining routes/integrations (HTTP APIs only) |
| `target` / `route_key` | `string` | `null` | Quick-create: single integration URI + catch-all route |
| `cors_configuration` | `object` | `null` | CORS settings: allow_origins, allow_methods, allow_headers, allow_credentials, max_age (HTTP APIs only) |
| `authorizers` | `map(object)` | `{}` | Map of `JWT`/`REQUEST` authorizers (`authorizer_type`, `identity_sources`, `jwt_configuration`, `authorizer_uri`) |
| `routes` | `map(object)` | `{}` | Map of `"{METHOD} {path}"` keys to route + integration config |
| `vpc_links` | `map(object)` | `{}` | VPC Link definitions (`name`, `security_group_ids`, `subnet_ids`) for private integrations |
| `stage_name` | `string` | `"$default"` | Stage name (1-128 chars) |
| `deploy_stage` | `bool` | `true` | Whether to deploy the stage (HTTP APIs auto-deploy) |
| `stage_variables` | `map(string)` | `{}` | Stage-specific variables |
| `stage_access_log_settings` | `object` | `{}` | CloudWatch access log config: `create_log_group`, `format`, `log_group_retention_in_days`, `log_group_kms_key_id` |
| `stage_default_route_settings` | `object` | `{}` | Default stage throttling/metrics: `throttling_burst_limit` (500), `throttling_rate_limit` (1000), `detailed_metrics_enabled` (true) |
| `domain_name` | `string` | `""` | Custom domain name for the API (supports wildcard `*.domain.com`) |
| `subdomains` | `list(string)` | `[]` | Subdomains to create when `domain_name` is a wildcard |
| `hosted_zone_name` | `string` | `null` | Route 53 hosted zone for domain records |
| `private_zone` | `bool` | `false` | Whether the hosted zone is private (certificate validation fails if `true`) |
| `create_certificate` | `bool` | `true` | Create an ACM certificate for the domain (ignored if `private_zone = true`) |
| `domain_name_certificate_arn` | `string` | `null` | Existing ACM certificate ARN (required when `private_zone = true` or `create_certificate = false`) |
| `mutual_tls_authentication` | `map(string)` | `{}` | mTLS config: `truststore_uri` (S3), `truststore_version` |
| `disable_execute_api_endpoint` | `bool` | `null` | Block the default `execute-api` endpoint; auto-`true` for HTTP APIs once a custom domain is created |
| `ip_address_type` | `string` | `null` | `ipv4` or `dualstack` for API invocation |
| `create` | `bool` | `true` | Master toggle for all resources |
| `create_domain_name` / `create_domain_records` / `create_certificate` / `create_routes_and_integrations` / `create_stage` | `bool` | `true` | Independent per-resource-group creation toggles |
| `tags` | `map(string)` | `{}` | Tags applied to API, stage, VPC link, and log group resources |

**`routes` map value shape** (per route key, e.g. `"POST /items"` or `"$connect"` for WebSocket):
```hcl
{
  authorizer_key      = optional(string)   # key into var.authorizers
  authorization_type   = optional(string)   # e.g. "AWS_IAM", "NONE"
  integration = {
    type                    = optional(string, "AWS_PROXY")  # or "HTTP_PROXY", "MOCK"
    uri                     = optional(string)                # Lambda ARN or backend URL
    connection_type         = optional(string)                # "VPC_LINK" for private integrations
    vpc_link_key            = optional(string)                # key into var.vpc_links
    payload_format_version  = optional(string)                # "2.0" recommended for Lambda
    timeout_milliseconds    = optional(number)
  }
}
```

### Main Outputs

| Output | Description |
|--------|-------------|
| `api_id` | The API identifier |
| `api_arn` | The ARN of the API |
| `api_endpoint` | URI of the API (`https://` for HTTP, `wss://` for WebSocket) |
| `api_execution_arn` | ARN prefix for `aws_lambda_permission` `source_arn` or IAM policies (`@connections` API) |
| `stage_id` / `stage_arn` | Stage identifier / ARN |
| `stage_invoke_url` | URL to invoke the API via the stage |
| `stage_execution_arn` | ARN prefix for stage-scoped Lambda permissions |
| `stage_domain_name` | Domain name of the stage (useful for CloudFront origin) |
| `stage_access_logs_cloudwatch_log_group_arn` / `_name` | Access log group ARN/name |
| `domain_name_id` / `domain_name_arn` | Custom domain name identifier/ARN |
| `domain_name_target_domain_name` | Target domain for Route 53/CloudFront alias records |
| `domain_name_hosted_zone_id` | Route 53 hosted zone ID of the API Gateway endpoint |
| `acm_certificate_arn` | ARN of the created ACM certificate |
| `authorizers` | Map of created authorizers and their attributes |
| `integrations` | Map of created integrations and their attributes |
| `routes` | Map of created routes and their attributes |
| `vpc_links` | Map of created VPC links and their attributes |

### Usage Examples

#### Example 1: Basic HTTP API

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

#### Example 2: HTTP API with Lambda Integration, JWT Auth, CORS, Custom Domain, and Logging

```hcl
module "api_gateway" {
  source  = "terraform-aws-modules/apigateway-v2/aws"
  version = "~> 6.1"

  name          = "my-http-api"
  description   = "HTTP API with Lambda backend"
  protocol_type = "HTTP"

  # CORS
  cors_configuration = {
    allow_headers = ["content-type", "x-amz-date", "authorization"]
    allow_methods = ["GET", "POST", "PUT", "DELETE"]
    allow_origins = ["https://example.com"]
  }

  # Custom domain (creates ACM cert + Route 53 alias record by default)
  domain_name      = "api.example.com"
  hosted_zone_name = "example.com"

  # Access logging
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

  # JWT authorizer (Cognito)
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

  # Routes with integrations
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

# Required: grant API Gateway permission to invoke each Lambda function
resource "aws_lambda_permission" "api_gw" {
  for_each = toset(["create", "get", "public", "default"])

  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module["lambda_${each.key}"].lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${module.api_gateway.api_execution_arn}/*/*"
}
```

#### Example 3: HTTP API with VPC Link (Private ALB Integration)

```hcl
module "api_gateway" {
  source  = "terraform-aws-modules/apigateway-v2/aws"
  version = "~> 6.1"

  name          = "vpc-link-http-api"
  description   = "HTTP API with VPC Link to internal ALB"
  protocol_type = "HTTP"

  create_domain_name = false

  vpc_links = {
    my-vpc = {
      name               = "my-vpc-link"
      security_group_ids = [module.api_gateway_security_group.security_group_id]
      subnet_ids         = module.vpc.public_subnets
    }
  }

  routes = {
    "ANY /api/{proxy+}" = {
      integration = {
        connection_type = "VPC_LINK"
        vpc_link_key    = "my-vpc"
        uri             = module.alb.listeners["default"].arn
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

#### Example 4: WebSocket API

```hcl
module "websocket_api" {
  source  = "terraform-aws-modules/apigateway-v2/aws"
  version = "~> 6.1"

  name                       = "my-websocket-api"
  description                = "WebSocket API for real-time communication"
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"

  stage_access_log_settings = {
    create_log_group            = true
    log_group_retention_in_days = 7
  }

  stage_default_route_settings = {
    detailed_metrics_enabled = true
    throttling_burst_limit   = 100
    throttling_rate_limit    = 100
  }

  # WebSocket routes: $connect, $disconnect, and $default are the minimum required
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

#### Example 5: Wrapper Submodule (Multiple APIs in One Block)

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

## Best Practices

### API Design

1. **Choose HTTP APIs Over REST APIs**: HTTP APIs cost up to ~71% less than REST APIs when advanced REST-API-only features (request validation, usage plans) aren't required
2. **Use WebSocket for Bidirectional Traffic**: Deploy WebSocket APIs for real-time communication instead of client-side polling
3. **Follow RESTful Route Conventions**: `GET /users`, `POST /users`, `GET /users/{id}`
4. **Version APIs via Path**: Use `/v1/`, `/v2/` prefixes for breaking changes rather than separate deployments

### Integrations

1. **Prefer `AWS_PROXY` for Lambda**: Passes full request context and simplifies response handling; it is the default `integration.type`
2. **Use Payload Format 2.0**: Simplified Lambda event/response structure — set `payload_format_version = "2.0"`
3. **Set Realistic Timeouts**: `timeout_milliseconds` should reflect backend latency (API Gateway max is 30s for HTTP APIs, 29s for Lambda integrations)
4. **Use VPC Links for Internal Resources**: Keep ALBs/NLBs off the public internet instead of exposing them directly

### Security

1. **Enable JWT Authorizers for OAuth2/OIDC**: Use Cognito, Auth0, or Azure AD as the JWT issuer
2. **Scope Authorizers per Route**: Reference the minimum-privilege authorizer via `authorizer_key` on each route
3. **Enable Mutual TLS for B2B/Partner APIs**: Configure `mutual_tls_authentication.truststore_uri` pointing at an S3-hosted CA bundle
4. **Force Traffic Through the Custom Domain**: HTTP APIs auto-set `disable_execute_api_endpoint = true` once a custom domain is created; explicitly set it for WebSocket APIs too if desired
5. **Apply Throttling at Stage and Route Level**: Configure `stage_default_route_settings` and per-route `throttling_burst_limit`/`throttling_rate_limit` to prevent abuse
6. **Always Enable Access Logging**: Required for security auditing, incident response, and threat detection

### Monitoring & Deployment

1. **Log Structured JSON**: Use `jsonencode()` for `stage_access_log_settings.format` with `$context.*` variables for easy log-analytics parsing
2. **Enable Detailed CloudWatch Metrics**: Set `detailed_metrics_enabled = true` to get per-route latency/error metrics
3. **Grant Lambda Invoke Permission**: Every Lambda integration needs a matching `aws_lambda_permission` with `source_arn = "${module.api_gateway.api_execution_arn}/*/*"`
4. **Pin the Module Version**: Use `version = "~> 6.1"` to avoid unexpected provider/behavior changes on `terraform init -upgrade`
5. **Use Independent `create_*` Toggles**: Disable `create_routes_and_integrations`/`create_stage`/`create_domain_name` individually when composing the API across multiple Terraform configurations

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2/tree/master/examples
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2/blob/master/CHANGELOG.md
- **AWS API Gateway Developer Guide**: https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html
- **HTTP APIs Documentation**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html
- **WebSocket APIs Documentation**: https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api.html
- **JWT Authorizers**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html
- **VPC Links for HTTP APIs**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vpc-links.html
- **API Gateway Pricing**: https://aws.amazon.com/api-gateway/pricing/
- **Serverless.tf Framework**: https://serverless.tf/

## Notes for AI Agents

1. **Protocol Selection**: `protocol_type = "HTTP"` (default) for REST-style APIs, `"WEBSOCKET"` for bidirectional/streaming
2. **Route Key Format**: `"{METHOD} {path}"` for HTTP APIs (e.g., `"GET /users"`, `"POST /orders/{id}"`, `"ANY /{proxy+}"`); free-form route keys (`"$connect"`, `"$disconnect"`, `"sendmessage"`) for WebSocket
3. **Integration Type**: Default is `AWS_PROXY` (Lambda). Use `HTTP_PROXY` for backend HTTP services and set `connection_type = "VPC_LINK"` with `vpc_link_key` for private targets
4. **Lambda Payload Version**: Always set `integration.payload_format_version = "2.0"` for Lambda integrations unless the function expects the legacy 1.0 event shape
5. **Lambda Permissions Are Not Automatic**: Always add a matching `aws_lambda_permission` resource with `source_arn = "${module.api_gateway.api_execution_arn}/*/*"` for every Lambda integration
6. **Authorizer/VPC Link References**: Use `authorizer_key` in a route to reference an entry in `authorizers`, and `integration.vpc_link_key` to reference an entry in `vpc_links` — these are module-local keys, not AWS IDs
7. **Custom Domain Requirements**: Set `domain_name` + `hosted_zone_name`, and either leave `create_certificate = true` (default, public zones only) or supply `domain_name_certificate_arn` for an existing certificate
8. **Private Hosted Zones**: Set `private_zone = true` and supply an existing `domain_name_certificate_arn` — ACM certificate validation fails automatically for private zones
9. **WebSocket Minimum Routes**: Always define `$connect`, `$disconnect`, and `$default` routes; omitting any of these breaks the connection lifecycle
10. **`disable_execute_api_endpoint` Auto-Behavior**: For HTTP APIs, this is forced to `true` automatically once a custom domain is created — do not rely on the default `execute-api` URL still being reachable in that case
11. **CORS in Production**: Set explicit `allow_origins`/`allow_methods`/`allow_headers` rather than `["*"]` wildcards
12. **Conditional Creation for Composition**: Use `create_routes_and_integrations = false`, `create_stage = false`, or `create_domain_name = false` when splitting API definition across multiple Terraform configs/workspaces
13. **Wrapper Submodule for Bulk APIs**: Use `//wrappers` with `defaults` + `items` maps when creating many near-identical API Gateways (e.g., per-tenant or per-environment), especially under Terragrunt where native `for_each` over modules isn't available
