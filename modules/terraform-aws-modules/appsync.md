# Terraform AWS AppSync Module

## Module Information

- **Module Name**: `appsync`
- **Module ID**: `terraform-aws-modules/appsync/aws`
- **Source**: `terraform-aws-modules/appsync/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-appsync
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/appsync/aws/latest
- **Latest Version**: 4.1.0 (released 2026-01-08)
- **Purpose**: Terraform module that creates an AWS AppSync GraphQL API together with its datasources, resolvers, pipeline functions, caching, custom domain, and supporting IAM roles
- **Service**: AWS AppSync (Managed GraphQL Service)
- **Category**: Serverless, API Management, Application Integration
- **Keywords**: appsync, graphql, api, serverless, resolver, pipeline-resolver, datasource, lambda, dynamodb, cognito, oidc, iam, api-key, real-time-subscriptions, caching, custom-domain, javascript-resolver, vtl
- **Use For**: building GraphQL APIs for mobile and web applications, real-time data synchronization and subscriptions, aggregating multiple data sources (Lambda, DynamoDB, RDS, HTTP, EventBridge) behind one GraphQL endpoint, serverless backend APIs, GraphQL gateway in front of microservices, event-driven mutations into EventBridge, REST-to-GraphQL migration, multi-tenant SaaS APIs with Cognito-based tenant isolation, private/internal GraphQL APIs, IoT device management APIs

## Description

The AWS AppSync module provisions a fully configured GraphQL API on top of Amazon AppSync, a managed service that removes the operational burden of building and scaling a GraphQL backend. In a single module call it creates the `aws_appsync_graphql_api` resource plus every dependent resource commonly needed around it: datasources (Lambda, DynamoDB, OpenSearch/Elasticsearch, EventBridge, RDS Data API, HTTP, or local `NONE`), unit and pipeline resolvers, reusable pipeline functions, API keys, an ElastiCache-backed response cache, a custom domain association, and the IAM service roles each datasource needs to be invoked by AppSync.

The module supports every AppSync authentication mode — API Key, AWS IAM, Amazon Cognito User Pools, OpenID Connect, and AWS Lambda authorizers — including up to four additional authentication providers alongside the primary one, which is the common pattern for public read access combined with authenticated writes. Resolvers can be written as classic VTL request/response mapping templates or as modern JavaScript (`APPSYNC_JS`) resolvers, and can be chained into `PIPELINE` resolvers that invoke one or more `aws_appsync_function` resources in sequence. IAM roles for each datasource type are created automatically with sensible least-privilege default policies (overridable per datasource or globally per type), and a role for pushing field/request logs to CloudWatch is created when logging is enabled.

Because `datasources` and `resolvers` are expressed as maps keyed by name, the module scales cleanly from a minimal single-resolver API to a large schema with dozens of datasources, pipeline functions, and fine-grained resolver-level caching — all through plain Terraform variables rather than hand-written resource blocks. It is part of the [serverless.tf](https://serverless.tf) framework and ships a `wrappers/` directory for Terragrunt-style `for_each` usage, but otherwise has no separate submodules.

## Key Features

- **All AppSync Authentication Modes**: API Key, AWS IAM, Amazon Cognito User Pools, OpenID Connect, and AWS Lambda authorizers, plus up to 4 additional authentication providers on the same API
- **Broad Datasource Support**: HTTP, AWS Lambda, Amazon DynamoDB, Amazon OpenSearch Service, Elasticsearch (legacy), Amazon EventBridge, RDS/Aurora via the Data API, and local (`NONE`) datasources
- **Automatic IAM Role Creation**: Per-datasource service roles with type-specific default policies (`*_allowed_actions` variables); bring your own role via `service_role_arn` or disable creation with `create_service_role = false`
- **Unit & Pipeline Resolvers**: Direct field resolvers or multi-step pipeline resolvers composed of reusable `functions`
- **VTL and JavaScript Runtimes**: Classic Velocity Template Language mapping templates or `APPSYNC_JS` resolver/function code
- **Direct Lambda Integration**: Built-in default request/response VTL templates (`direct_lambda = true`) to skip writing mapping templates for simple Lambda resolvers
- **Response Caching**: Full-request or per-resolver ElastiCache-backed caching with configurable TTL and at-rest/in-transit encryption
- **Custom Domain Names**: `aws_appsync_domain_name` + association with an ACM certificate; outputs the AppSync-provided domain and Route 53 hosted zone ID for you to wire into your own DNS records
- **Conflict Resolution**: Optimistic concurrency (`sync_config`) on pipeline functions with `AUTOMERGE`, `OPTIMISTIC_CONCURRENCY`, or Lambda-based conflict handlers
- **Enhanced Metrics**: Per-datasource, per-resolver, and per-operation CloudWatch metrics via `enhanced_metrics_config`
- **CloudWatch Logging & X-Ray**: Field-level/request-level logging with an auto-created logs IAM role, and X-Ray tracing toggle
- **Query Guardrails**: `query_depth_limit`, `resolver_count_limit`, and `introspection_config` to harden public APIs
- **GLOBAL/PRIVATE Visibility**: Native AppSync API visibility control (private APIs still require a VPC interface endpoint set up outside this module)
- **Conditional Creation**: Single `create_graphql_api` flag to disable every resource in the module (useful for `count`-free conditional modules)
- **Per-resource Region Override**: `region` variable applied to every resource for multi-region provider setups

## Main Use Cases

1. **Mobile & Web Backend APIs**: Serverless GraphQL backend for iOS, Android, and web apps with offline sync
2. **Real-time Collaboration**: Chat, live dashboards, and collaborative editing via GraphQL subscriptions
3. **Multi-datasource Aggregation**: Unify DynamoDB, RDS, Lambda, and HTTP APIs behind one GraphQL endpoint
4. **Microservices GraphQL Gateway**: Route fields to different backend services through per-field resolvers
5. **Event-driven Architectures**: Trigger workflows by writing AppSync mutations into an EventBridge datasource
6. **IoT Device Management**: Device status/command APIs with real-time subscription updates
7. **Headless CMS**: Flexible content queries backed by DynamoDB or HTTP datasources
8. **Multi-tenant SaaS Platforms**: Tenant isolation via Cognito User Pools and resolver-level authorization
9. **REST-to-GraphQL Migration**: Wrap existing REST APIs with HTTP datasources and custom resolvers
10. **Private/Internal APIs**: `PRIVATE` visibility GraphQL APIs restricted to a VPC for internal tooling

## Submodules

This module has **no separate submodules** — all resources are created from the root module. A `wrappers/` directory is included for Terragrunt-style patterns that need to manage multiple instances with `for_each`/`create` semantics.

## Main Input Variables

Note: `name` and `schema` default to `""` (not marked `required` by terraform-docs), but the API is non-functional without them — treat them as required in practice.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the GraphQL API — set this |
| `schema` | `string` | `""` | GraphQL SDL schema definition (e.g. `file("schema.graphql")`) — set this |
| `create_graphql_api` | `bool` | `true` | Set `false` to disable every resource in the module |
| `authentication_type` | `string` | `"API_KEY"` | Primary auth type: `API_KEY`, `AWS_IAM`, `OPENID_CONNECT`, `AMAZON_COGNITO_USER_POOLS`, `AWS_LAMBDA` |
| `additional_authentication_provider` | `any` | `{}` | Map of extra auth providers (max 4) with their own OIDC/Cognito/Lambda config |
| `visibility` | `string` | `null` | `GLOBAL` or `PRIVATE` |
| `api_keys` | `map(string)` | `{}` | Map of API key description → expiry date (or `null` for the default 7-day expiry) |
| `user_pool_config`, `openid_connect_config`, `lambda_authorizer_config` | `map(string)` | `{}` | Config for the corresponding primary auth type |
| `datasources` | `any` | `{}` | Map of datasource name → config object (`type` + type-specific attributes, optional `service_role_arn`/`create_service_role`/`policy_actions`) |
| `resolvers` | `any` | `{}` | Map keyed `"Type.field"` → resolver config (`data_source`, `direct_lambda`, `request_template`/`response_template`, `runtime`, `code`, `functions`, `caching_keys`, `max_batch_size`) |
| `functions` | `any` | `{}` | Map of pipeline function name → config (`data_source`, `runtime`, `code` or VTL templates, `sync_config`) |
| `direct_lambda_request_template` / `direct_lambda_response_template` | `string` | built-in VTL | Default templates used when a resolver sets `direct_lambda = true` |
| `logging_enabled` | `bool` | `false` | Enable CloudWatch logging on the API |
| `create_logs_role` | `bool` | `true` | Auto-create the IAM role for CloudWatch logs (else supply `log_cloudwatch_logs_role_arn`) |
| `log_field_log_level` | `string` | `null` | `ALL`, `ERROR`, or `NONE` |
| `xray_enabled` | `bool` | `false` | Enable AWS X-Ray tracing |
| `enhanced_metrics_config` | `map(string)` | `{}` | `data_source_level_metrics_behavior`, `operation_level_metrics_config`, `resolver_level_metrics_behavior` |
| `caching_enabled` | `bool` | `false` | Create an ElastiCache-backed API cache |
| `caching_behavior` | `string` | `"FULL_REQUEST_CACHING"` | `FULL_REQUEST_CACHING` or `PER_RESOLVER_CACHING` |
| `cache_type` | `string` | `"SMALL"` | Cache instance size (`SMALL` … `LARGE2X`, etc.) |
| `cache_ttl` | `number` | `1` | Cache TTL in seconds |
| `resolver_caching_ttl` | `number` | `60` | Default per-resolver caching TTL when a resolver sets `caching_keys` without its own `caching_ttl` |
| `cache_at_rest_encryption_enabled` / `cache_transit_encryption_enabled` | `bool` | `false` | Cache encryption toggles |
| `domain_name` | `string` | `""` | Custom domain name for the API |
| `domain_name_association_enabled` | `bool` | `false` | Create the domain name + association resources |
| `certificate_arn` | `string` | `""` | ACM certificate ARN for the custom domain (must be in `us-east-1` for edge use) |
| `query_depth_limit` / `resolver_count_limit` | `number` | `null` | Per-request query depth / resolver count guardrails |
| `introspection_config` | `string` | `null` | `ENABLED`/`DISABLED` |
| `dynamodb_allowed_actions`, `lambda_allowed_actions`, `eventbridge_allowed_actions`, `elasticsearch_allowed_actions`, `opensearchservice_allowed_actions`, `relational_database_allowed_actions`, `secrets_manager_allowed_actions` | `list(string)` | service-specific defaults | Default IAM actions granted to each auto-created datasource service role; override globally here or per-datasource with `policy_actions` |
| `iam_permissions_boundary` | `string` | `null` | Permissions boundary ARN applied to every IAM role the module creates |
| `region` | `string` | `null` | Override the provider region per-resource |
| `tags` | `map(string)` | `{}` | Tags applied to all resources (roles, cache, domain, etc.) |
| `graphql_api_tags` | `map(string)` | `{}` | Extra tags applied only to the GraphQL API resource |

## Main Outputs

| Output | Description |
|--------|-------------|
| `appsync_graphql_api_id` | GraphQL API ID |
| `appsync_graphql_api_arn` | GraphQL API ARN |
| `appsync_graphql_api_uris` | Map of URIs (includes the `GRAPHQL` and `REALTIME` endpoints) |
| `appsync_graphql_api_fqdns` | Map of FQDNs extracted from the URIs (no protocol/path) |
| `appsync_datasource_arn` | Map of datasource ARNs, keyed by datasource name |
| `appsync_resolver_arn` | Map of resolver ARNs, keyed by `"Type.field"` |
| `appsync_function_arn` / `appsync_function_id` / `appsync_function_function_id` | Function ARNs, Terraform resource IDs, and AppSync `function_id`s (the value used inside `resolvers[*].functions`) |
| `appsync_api_key_id` | Map of API key IDs (`ApiId:Key` format) |
| `appsync_api_key_key` | Map of API key values (**sensitive**) |
| `appsync_domain_id` | Custom domain name resource ID |
| `appsync_domain_name` | AppSync-provided domain name — point your own DNS `CNAME`/alias at this |
| `appsync_domain_hosted_zone_id` | Route 53 hosted zone ID associated with the AppSync domain |

## Supported Data Source Types

| Type | Required config | Notes |
|------|------------------|-------|
| `AWS_LAMBDA` | `function_arn` | Use `direct_lambda = true` on the resolver to skip templates |
| `AMAZON_DYNAMODB` | `table_name`, `region` | Optional `use_caller_credentials` |
| `AMAZON_OPENSEARCH_SERVICE` | `endpoint`, `region` | Successor to the legacy Elasticsearch type |
| `AMAZON_ELASTICSEARCH` | `endpoint`, `region` | Legacy; prefer OpenSearch Service |
| `AMAZON_EVENTBRIDGE` | `event_bus_arn` | For event-driven mutations |
| `RELATIONAL_DATABASE` | `cluster_arn`, `secret_arn`, `database_name`, `schema` | RDS/Aurora via the Data API |
| `HTTP` | `endpoint` | External REST/HTTP APIs |
| `NONE` | — | Local resolver, no external call (e.g. pipeline "passthrough" steps) |

## Usage Examples

### Basic GraphQL API with a Lambda Data Source

```hcl
module "appsync" {
  source  = "terraform-aws-modules/appsync/aws"
  version = "~> 4.1"

  name   = "my-graphql-api"
  schema = file("schema.graphql")

  api_keys = {
    default = null # expires in 7 days
  }

  datasources = {
    lambda_posts = {
      type         = "AWS_LAMBDA"
      function_arn = aws_lambda_function.posts.arn
    }
  }

  resolvers = {
    "Query.getPosts" = {
      data_source   = "lambda_posts"
      direct_lambda = true
    }
  }

  tags = {
    Environment = "development"
  }
}
```

### Multi-auth Production API with Caching, Pipeline Resolvers, and Observability

```hcl
module "appsync" {
  source  = "terraform-aws-modules/appsync/aws"
  version = "~> 4.1"

  name   = "prod-graphql-api"
  schema = file("schema.graphql")

  # Primary authentication
  authentication_type = "AMAZON_COGNITO_USER_POOLS"
  user_pool_config = {
    default_action = "ALLOW"
    user_pool_id   = aws_cognito_user_pool.this.id
  }

  # Additional authentication providers
  additional_authentication_provider = {
    iam = {
      authentication_type = "AWS_IAM"
    }
    api_key = {
      authentication_type = "API_KEY"
    }
  }

  # Datasources
  datasources = {
    dynamodb_posts = {
      type       = "AMAZON_DYNAMODB"
      table_name = aws_dynamodb_table.posts.name
      region     = "us-east-1"
    }
    lambda_users = {
      type         = "AWS_LAMBDA"
      function_arn = aws_lambda_function.users.arn
    }
    none = {
      type = "NONE"
    }
  }

  # Pipeline function + pipeline resolver (JavaScript runtime)
  functions = {
    validateInput = {
      data_source = "none"
      runtime     = { name = "APPSYNC_JS" }
      code        = file("functions/validate-input.js")
    }
  }

  resolvers = {
    "Query.getPost" = {
      data_source       = "dynamodb_posts"
      request_template  = file("templates/getPost-request.vtl")
      response_template = file("templates/getPost-response.vtl")
      caching_keys      = ["$context.identity.sub", "$context.arguments.id"]
    }
    "Query.getUser" = {
      data_source   = "lambda_users"
      direct_lambda = true
    }
    "Mutation.createPost" = {
      kind    = "PIPELINE"
      type    = "Mutation"
      field   = "createPost"
      runtime = { name = "APPSYNC_JS" }
      code    = file("resolvers/create-post.js")
      functions = ["validateInput"]
    }
  }

  # Caching
  caching_enabled                  = true
  caching_behavior                 = "PER_RESOLVER_CACHING"
  cache_type                       = "SMALL"
  cache_ttl                        = 60
  cache_at_rest_encryption_enabled = true
  cache_transit_encryption_enabled = true

  # Observability
  logging_enabled     = true
  log_field_log_level = "ERROR"
  xray_enabled        = true
  enhanced_metrics_config = {
    data_source_level_metrics_behavior = "PER_DATA_SOURCE_METRICS"
    operation_level_metrics_config     = "ENABLED"
    resolver_level_metrics_behavior    = "FULL_REQUEST_RESOLVER_METRICS"
  }

  # Guardrails
  query_depth_limit    = 10
  resolver_count_limit = 100
  introspection_config = "DISABLED"

  tags = {
    Environment = "production"
    Team        = "platform"
  }
}
```

### Custom Domain Name

```hcl
module "appsync" {
  source  = "terraform-aws-modules/appsync/aws"
  version = "~> 4.1"

  name   = "custom-domain-api"
  schema = file("schema.graphql")

  api_keys = {
    default = null
  }

  domain_name                     = "graphql.example.com"
  domain_name_association_enabled = true
  certificate_arn                 = aws_acm_certificate_validation.graphql.certificate_arn

  datasources = {
    none = {
      type = "NONE"
    }
  }

  resolvers = {
    "Query.hello" = {
      data_source       = "none"
      request_template  = "{\"version\": \"2017-02-28\"}"
      response_template = "$util.toJson({\"message\": \"Hello World\"})"
    }
  }
}

# Point your own DNS at the AppSync-provided domain
resource "aws_route53_record" "graphql" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = "graphql.example.com"
  type    = "CNAME"
  ttl     = 300
  records = [module.appsync.appsync_domain_name]
}
```

## Best Practices

### Schema & Resolver Design
1. **Schema-first**: Author the SDL schema (`schema.graphql`) before wiring resolvers, and keep it under version control alongside the Terraform code.
2. **Prefer JavaScript over VTL for new resolvers**: `APPSYNC_JS` resolvers/functions are easier to test and debug than VTL mapping templates; reserve VTL for simple, stable mappings.
3. **Use `direct_lambda = true`** for straightforward Lambda-backed fields instead of hand-writing pass-through VTL request/response templates.
4. **Use pipeline resolvers** (`kind = "PIPELINE"` + `functions`) only when a field genuinely needs multiple sequential steps (auth checks, validation, multiple datasource calls); prefer `UNIT` resolvers otherwise.
5. **Cursor-based pagination**: For list fields, implement Relay-style cursor pagination to avoid large unbounded scans on DynamoDB/RDS datasources.

### Authentication & Authorization
1. **Match auth type to access pattern**: `API_KEY` for prototyping/public read, `AMAZON_COGNITO_USER_POOLS` for end-user apps, `AWS_IAM` for service-to-service, `OPENID_CONNECT`/Lambda authorizer for external IdP/custom logic.
2. **Combine primary + `additional_authentication_provider`** rather than building separate APIs when you need e.g. public API-key reads plus authenticated Cognito writes.
3. **Rotate and scope API keys**: Set explicit expirations in `api_keys` (avoid relying on the default 7-day expiry silently rolling) and avoid using API keys for write/mutation-heavy production traffic.
4. **Field-level authorization**: Enforce fine-grained access in resolver/function code (Lambda authorizer context, `$ctx.identity`) rather than relying solely on API-level auth.

### IAM & Data Source Access
1. **Use the module's per-type `*_allowed_actions` variables** to tighten default datasource IAM policies instead of granting broad service access; override per datasource with `policy_actions` when a specific datasource needs less (or more).
2. **Bring your own role when needed**: Set `service_role_arn` and `create_service_role = false` on a datasource to reuse an existing, already-audited IAM role.
3. **Apply `iam_permissions_boundary`** in accounts where a permissions boundary is mandated for all roles created by automation.
4. **Static ARNs for datasources**: Prefer literal/data-sourced ARNs over dynamic references from freshly-created Lambda/DynamoDB resources in the same apply when possible — the module's docs note that same-apply dynamic references to `function_arn`/`table_name` can cause ordering issues; create datasource-backing resources first or use `-target` when renaming datasource keys.

### Caching & Performance
1. **Enable caching for read-heavy, slowly-changing fields**: Use `PER_RESOLVER_CACHING` with explicit `caching_keys` per resolver rather than `FULL_REQUEST_CACHING` for APIs with a mix of cacheable and per-user data.
2. **Tune `cache_ttl`/`resolver_caching_ttl`** to balance freshness against datasource load; both cache encryption flags should be `true` for anything handling sensitive data.
3. **Batch Lambda resolvers**: Set `max_batch_size` on Lambda-backed resolvers/functions to reduce per-item invocation overhead (AppSync's built-in DataLoader-style batching).

### Observability & Security
1. **Enable `logging_enabled` + `xray_enabled` during development**; move `log_field_log_level` to `ERROR` and rely on `enhanced_metrics_config` in production to control CloudWatch cost.
2. **Set `query_depth_limit`, `resolver_count_limit`, and `introspection_config = "DISABLED"`** on any public production API to reduce the blast radius of malicious or malformed queries.
3. **Front public GraphQL endpoints with AWS WAF** (attached to the AppSync API ARN) for rate limiting and common web-exploit protection — this is configured outside the module via `aws_wafv2_web_acl_association`.
4. **Use `PRIVATE` visibility** for internal-only APIs, paired with a VPC interface endpoint for `appsync-api`, instead of exposing an internal API publicly and relying on auth alone.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-appsync
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/appsync/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-appsync/tree/master/examples/complete
- **CHANGELOG**: https://github.com/terraform-aws-modules/terraform-aws-appsync/blob/master/CHANGELOG.md
- **AWS AppSync Developer Guide**: https://docs.aws.amazon.com/appsync/latest/devguide/welcome.html
- **GraphQL Schema Design**: https://docs.aws.amazon.com/appsync/latest/devguide/designing-a-graphql-api.html
- **Resolver Mapping Template Reference (VTL)**: https://docs.aws.amazon.com/appsync/latest/devguide/resolver-mapping-template-reference.html
- **JavaScript Resolver Reference**: https://docs.aws.amazon.com/appsync/latest/devguide/resolver-reference-js.html
- **Real-time Subscriptions**: https://docs.aws.amazon.com/appsync/latest/devguide/aws-appsync-real-time-data.html
- **AppSync Caching**: https://docs.aws.amazon.com/appsync/latest/devguide/enabling-caching.html
- **AppSync Security**: https://docs.aws.amazon.com/appsync/latest/devguide/security.html
- **AppSync Monitoring**: https://docs.aws.amazon.com/appsync/latest/devguide/monitoring.html
- **AppSync Pricing**: https://aws.amazon.com/appsync/pricing/
- **serverless.tf framework**: https://serverless.tf

## Notes for AI Agents

When generating Terraform code with this module:

1. **Provider/Terraform floor is recent**: v4.x requires Terraform `>= 1.5.7` and AWS provider `>= 6.28` — check the target codebase's provider constraint before pinning `~> 4.1`; older provider pins will conflict.
2. **`name` and `schema` have empty-string defaults** but are effectively required — always set both explicitly.
3. **Datasource keys are referenced by name in `resolvers`/`functions`**: keep `datasources`, `functions`, and `resolvers` map keys consistent; renaming a datasource key requires a two-step `-target` apply (see module README) to avoid resolver breakage.
4. **Resolver map keys use `"Type.field"` syntax** (e.g. `"Query.getPost"`, `"Mutation.createPost"`) — the module derives `type`/`field` from the key unless overridden.
5. **`direct_lambda = true`** is the fastest path for simple Lambda resolvers; only write custom VTL/JS when you need request shaping.
6. **Use `APPSYNC_JS` runtime for new code**; `code = file(...)` is required when `runtime.name == "APPSYNC_JS"`.
7. **Default to least privilege**: override `*_allowed_actions` or per-datasource `policy_actions` rather than accepting broad defaults for production datasources.
8. **This module does not manage Route 53 records**: `appsync_domain_name` output must be wired into a `aws_route53_record`/alias by the caller.
9. **`create_graphql_api = false`** is the idiomatic way to conditionally disable the whole module (Terraform `count` on a `module` block with `for_each`-style sources is otherwise unavailable in older Terraform).
10. **Merged APIs / VPC-hosted private networking are not built by this module**: `visibility = "PRIVATE"` only sets the AppSync API attribute — the VPC interface endpoint must be created separately.
