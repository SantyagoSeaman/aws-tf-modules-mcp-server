# Terraform AWS AppSync Module

## Module Information

- **Module Name**: `appsync`
- **Source**: `terraform-aws-modules/appsync/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-appsync
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/appsync/aws/latest
- **Latest Version**: 4.1.0
- **Purpose**: Terraform module that creates AWS AppSync GraphQL API resources with flexible datasources, resolvers, and authentication configurations
- **Service**: AWS AppSync (Managed GraphQL Service)
- **Category**: Serverless, API Management, Application Integration
- **Keywords**: appsync, graphql, api, serverless, resolver, datasource, lambda, dynamodb, cognito, iam, api-key, subscription, real-time, caching, custom-domain, x-ray, vtl, javascript, pipeline-resolver
- **Use For**: Building GraphQL APIs for mobile and web applications, creating real-time data synchronization systems, implementing serverless backend APIs, aggregating multiple data sources through unified GraphQL interface, developing collaborative applications with subscriptions, migrating REST APIs to GraphQL, building microservices API gateways, implementing event-driven architectures with GraphQL mutations, creating multi-tenant SaaS platforms, developing IoT device management interfaces

## Description

The AWS AppSync Terraform module provides a comprehensive solution for creating and managing AWS AppSync GraphQL APIs with extensive configuration options for datasources, resolvers, and authentication. AppSync is a fully managed service that makes it easy to develop GraphQL APIs by handling the heavy lifting of securely connecting to data sources like AWS DynamoDB, Lambda, OpenSearch, RDS Aurora, HTTP endpoints, and Amazon EventBridge. The module abstracts the complexity of configuring GraphQL schemas, field resolvers, pipeline resolvers, and multiple authentication providers into a declarative Terraform interface.

This module supports all major AppSync features including API Key, IAM, Amazon Cognito User Pools, OpenID Connect (OIDC), and AWS Lambda authorizers for flexible authentication and authorization. It enables advanced capabilities such as real-time data synchronization through GraphQL subscriptions over WebSockets, response caching with Amazon ElastiCache, AWS X-Ray distributed tracing, custom domain names with SSL certificates, and field-level logging for comprehensive observability. The module supports both VTL (Velocity Template Language) and JavaScript resolvers, allowing developers to transform and manipulate data between GraphQL operations and datasources.

The module follows AWS best practices for serverless architectures and integrates seamlessly with the broader serverless.tf framework, making it ideal for building modern, scalable, event-driven applications. It provides fine-grained control over resolver configurations, caching behavior, authorization rules, and monitoring settings while maintaining a clean, maintainable Terraform codebase. The module handles IAM role creation for CloudWatch logging, supports merged APIs for federation scenarios, and allows for private API configurations within VPCs.

## Key Features

- **Multiple Authentication Providers**: Support for API Key, AWS IAM, Amazon Cognito User Pools, OpenID Connect (OIDC), and Lambda authorizers
- **Diverse Datasource Types**: Integration with HTTP endpoints, AWS Lambda, DynamoDB, Elasticsearch, OpenSearch, Amazon EventBridge, and RDS Aurora
- **GraphQL Schema Management**: Declarative schema definition with support for queries, mutations, subscriptions, and custom types
- **Field Resolvers**: Configure direct field resolvers with VTL or JavaScript mapping templates
- **Pipeline Resolvers**: Support for multi-step pipeline resolvers with functions for complex data transformation workflows
- **Real-time Subscriptions**: WebSocket-based GraphQL subscriptions for real-time data updates
- **Response Caching**: ElastiCache integration for API-level and resolver-level caching with configurable TTL
- **Custom Domain Names**: Route53 and ACM integration for custom domain configurations with SSL/TLS certificates
- **Authentication Types**: Granular per-resolver authentication configuration and authorization rules
- **AWS X-Ray Tracing**: Distributed tracing integration for performance monitoring and debugging
- **CloudWatch Logging**: Field-level and request-level logging with customizable log retention and IAM roles
- **JavaScript Resolvers**: Modern JavaScript runtime support for resolver logic (APPSYNC_JS)
- **VTL Resolvers**: Traditional Velocity Template Language support for request/response mapping
- **Enhanced Metrics**: CloudWatch metrics for API performance, error rates, and latency monitoring
- **Private APIs**: VPC-based private GraphQL APIs for internal applications
- **Merged APIs**: Support for federated GraphQL schemas and merged API configurations
- **IAM Role Management**: Automatic creation and configuration of service roles for logging and datasource access
- **Conflict Resolution**: Built-in conflict detection and resolution for offline/online data sync scenarios
- **API Keys**: Automated API key generation with configurable expiration and rotation

## Main Use Cases

1. **Mobile Backend APIs**: Build serverless GraphQL backends for iOS, Android, and React Native mobile applications with offline sync
2. **Real-time Collaboration**: Create collaborative editing tools, chat applications, and live dashboards with GraphQL subscriptions
3. **Multi-datasource Aggregation**: Unify data access across DynamoDB, RDS, Lambda functions, and HTTP APIs through single GraphQL endpoint
4. **Microservices API Gateway**: Implement GraphQL gateway pattern for microservices with resolver-level routing to different services
5. **Event-driven Architectures**: Trigger business workflows and event processing using AppSync mutations connected to EventBridge
6. **IoT Device Management**: Build device management interfaces with real-time status updates and command execution via GraphQL
7. **Content Management Systems**: Develop headless CMS platforms with flexible GraphQL queries for content retrieval and management
8. **Multi-tenant SaaS Platforms**: Implement tenant isolation using Cognito authentication and resolver-level authorization rules
9. **REST to GraphQL Migration**: Wrap existing REST APIs with GraphQL interface using HTTP datasources and custom resolvers
10. **Real-time Analytics Dashboards**: Stream metrics and events to web dashboards using subscriptions connected to DynamoDB Streams or EventBridge

## Submodules

This module does not have separate submodules. All functionality is contained in the root module. A `wrappers/` directory exists for use with Terragrunt patterns.

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | required | Name of the GraphQL API |
| `schema` | `string` | required | GraphQL schema definition in SDL format |
| `create_graphql_api` | `bool` | `true` | Whether to create the GraphQL API |
| `authentication_type` | `string` | `"API_KEY"` | Primary authentication type: API_KEY, AWS_IAM, OPENID_CONNECT, AMAZON_COGNITO_USER_POOLS, AWS_LAMBDA |
| `visibility` | `string` | `null` | API visibility: GLOBAL or PRIVATE |
| `api_keys` | `map(string)` | `{}` | Map of API keys to create |
| `additional_authentication_provider` | `any` | `{}` | Additional authentication providers |
| `datasources` | `any` | `{}` | Map of data source configurations |
| `resolvers` | `any` | `{}` | Map of resolver definitions |
| `functions` | `any` | `{}` | Map of AppSync function definitions for pipeline resolvers |
| `logging_enabled` | `bool` | `false` | Enable CloudWatch logging |
| `log_field_log_level` | `string` | `null` | Log level: ALL, ERROR, or NONE |
| `xray_enabled` | `bool` | `false` | Enable X-Ray tracing |
| `caching_enabled` | `bool` | `false` | Enable ElastiCache caching |
| `caching_behavior` | `string` | `"FULL_REQUEST_CACHING"` | FULL_REQUEST_CACHING or PER_RESOLVER_CACHING |
| `cache_type` | `string` | `"SMALL"` | Cache instance size: SMALL, MEDIUM, LARGE, XLARGE, etc. |
| `cache_ttl` | `number` | `1` | Cache TTL in seconds |
| `cache_at_rest_encryption_enabled` | `bool` | `false` | Enable cache encryption at rest |
| `cache_transit_encryption_enabled` | `bool` | `false` | Enable cache encryption in transit |
| `domain_name` | `string` | `""` | Custom domain name for the API |
| `domain_name_association_enabled` | `bool` | `false` | Enable domain name association |
| `certificate_arn` | `string` | `""` | ACM certificate ARN for custom domain |
| `query_depth_limit` | `number` | `null` | Maximum query depth allowed |
| `resolver_count_limit` | `number` | `null` | Maximum resolvers per request |
| `introspection_config` | `string` | `null` | Enable/disable schema introspection (ENABLED/DISABLED) |
| `user_pool_config` | `map(string)` | `{}` | Amazon Cognito User Pool configuration |
| `lambda_authorizer_config` | `map(string)` | `{}` | Lambda authorizer configuration |
| `openid_connect_config` | `map(string)` | `{}` | OpenID Connect configuration |
| `tags` | `map(string)` | `{}` | Tags to apply to all resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `appsync_graphql_api_id` | GraphQL API identifier |
| `appsync_graphql_api_arn` | GraphQL API ARN |
| `appsync_graphql_api_uris` | Map of URIs (includes GraphQL endpoint) |
| `appsync_graphql_api_fqdns` | Fully qualified domain names |
| `appsync_datasource_arn` | Map of data source ARNs by key |
| `appsync_resolver_arn` | Map of resolver ARNs by key |
| `appsync_function_arn` | Map of function ARNs by key |
| `appsync_function_id` | Map of function IDs by key |
| `appsync_api_key_id` | Map of API key IDs |
| `appsync_api_key_key` | Map of API key values (sensitive) |
| `appsync_domain_id` | Custom domain name ID |
| `appsync_domain_name` | AppSync-provided domain name |
| `appsync_domain_hosted_zone_id` | Route 53 hosted zone ID for domain |

## Supported Data Source Types

| Type | Description |
|------|-------------|
| `AWS_LAMBDA` | AWS Lambda function integration |
| `AMAZON_DYNAMODB` | DynamoDB table integration |
| `AMAZON_ELASTICSEARCH` | Elasticsearch domain (legacy) |
| `AMAZON_OPENSEARCH_SERVICE` | OpenSearch Service domain |
| `AMAZON_EVENTBRIDGE` | EventBridge event bus |
| `RELATIONAL_DATABASE` | RDS/Aurora via Data API |
| `HTTP` | External HTTP endpoints |
| `NONE` | Local resolvers (no external data source) |

## Usage Examples

### Basic GraphQL API with Lambda Data Source

```hcl
module "appsync" {
  source  = "terraform-aws-modules/appsync/aws"
  version = "~> 4.1"

  name   = "my-graphql-api"
  schema = file("schema.graphql")

  api_keys = {
    default = null  # Expires in 7 days
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

### Production API with Multiple Auth Providers and Caching

```hcl
module "appsync" {
  source  = "terraform-aws-modules/appsync/aws"
  version = "~> 4.1"

  name   = "prod-graphql-api"
  schema = file("schema.graphql")

  # Primary authentication
  authentication_type = "OPENID_CONNECT"
  openid_connect_config = {
    issuer    = "https://auth.example.com"
    client_id = "your-client-id"
  }

  # Additional authentication providers
  additional_authentication_provider = {
    iam = {
      authentication_type = "AWS_IAM"
    }
    cognito = {
      authentication_type = "AMAZON_COGNITO_USER_POOLS"
      user_pool_config = {
        user_pool_id = aws_cognito_user_pool.this.id
      }
    }
  }

  # Caching configuration
  caching_enabled                    = true
  caching_behavior                   = "PER_RESOLVER_CACHING"
  cache_type                         = "SMALL"
  cache_ttl                          = 60
  cache_at_rest_encryption_enabled   = true
  cache_transit_encryption_enabled   = true

  # Observability
  logging_enabled     = true
  log_field_log_level = "ERROR"
  xray_enabled        = true

  # Security limits
  query_depth_limit    = 10
  resolver_count_limit = 100
  introspection_config = "DISABLED"

  # Data sources
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
    http_external = {
      type     = "HTTP"
      endpoint = "https://api.example.com"
    }
  }

  # Resolvers
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
  }

  tags = {
    Environment = "production"
    Team        = "platform"
  }
}
```

### API with Custom Domain

```hcl
module "appsync" {
  source  = "terraform-aws-modules/appsync/aws"
  version = "~> 4.1"

  name   = "custom-domain-api"
  schema = file("schema.graphql")

  authentication_type = "API_KEY"
  api_keys = {
    default = null
  }

  # Custom domain configuration
  domain_name                     = "graphql.example.com"
  domain_name_association_enabled = true
  certificate_arn                 = aws_acm_certificate.graphql.arn

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
```

## Best Practices

### API Design and Schema Management

1. **Schema-First Design**: Define comprehensive GraphQL schemas before implementation, including input types, output types, and clear documentation
2. **Modular Schema Structure**: Break large schemas into logical domains and use schema stitching or merged APIs for federation
3. **Versioning Strategy**: Use field deprecation and schema evolution rather than breaking changes; maintain backward compatibility
4. **Input Validation**: Implement strict input type definitions with required fields and use custom scalars for specialized data types
5. **Error Handling**: Design consistent error responses with typed error objects and use GraphQL union types for expected errors
6. **Pagination Patterns**: Implement cursor-based pagination (Relay-style) for list queries to handle large result sets efficiently
7. **Rate Limiting**: Consider implementing custom rate limiting logic in resolvers for public APIs beyond AWS throttling limits
8. **Query Complexity Analysis**: Monitor and limit query depth and complexity to prevent resource exhaustion from malicious queries

### Authentication and Authorization

1. **Multi-auth Configuration**: Use appropriate authentication type per use case (API Key for public read, Cognito for user-specific data, IAM for service-to-service)
2. **Least Privilege Access**: Configure fine-grained IAM policies for datasource access with minimum required permissions
3. **API Key Rotation**: Implement regular API key rotation policies and use short expiration periods for sensitive applications
4. **Cognito Integration**: Leverage Cognito User Pools for user management with MFA, password policies, and account recovery workflows
5. **OIDC for SSO**: Use OpenID Connect authentication for enterprise SSO integration with external identity providers
6. **Lambda Authorizers**: Implement custom authorization logic in Lambda for complex business rules and external authorization systems
7. **Field-level Authorization**: Use resolver-level authentication settings and mapping template authorization checks for fine-grained access control
8. **Token Validation**: Ensure proper JWT token validation and refresh token handling in client applications

### Resolver Configuration and Performance

1. **Batching Strategy**: Use AWS Lambda datasources with batching to reduce function invocations and improve performance
2. **Caching Configuration**: Enable caching for frequently accessed, slowly-changing data with appropriate TTL values (300-3600 seconds)
3. **Resolver Type Selection**: Use unit resolvers for simple operations and pipeline resolvers for complex multi-step workflows
4. **JavaScript vs VTL**: Prefer JavaScript resolvers for complex logic and maintainability; use VTL for simple transformations
5. **Direct DynamoDB Access**: Use direct DynamoDB datasources with VTL templates for low-latency single-table operations
6. **Lambda Optimization**: Keep Lambda functions small and focused; use Lambda layers for shared dependencies
7. **Connection Pooling**: Configure RDS datasources with appropriate connection pooling and timeout settings
8. **HTTP Datasource Timeouts**: Set realistic timeout values for HTTP datasources and implement retry logic in resolvers
9. **Parallel Execution**: Leverage GraphQL's parallel field resolution by avoiding unnecessary dependencies between resolvers
10. **Request/Response Mapping**: Minimize data transformation in VTL/JavaScript; perform heavy computation in datasource layers

### Monitoring and Observability

1. **CloudWatch Logging**: Enable field-level logging for development and request-level logging for production to balance observability with cost
2. **X-Ray Tracing**: Enable AWS X-Ray for distributed tracing to identify performance bottlenecks across datasources
3. **Custom Metrics**: Publish custom CloudWatch metrics from Lambda resolvers for business-specific monitoring
4. **Alarm Configuration**: Create CloudWatch alarms for 4xx/5xx error rates, latency percentiles (p50, p95, p99), and throttling events
5. **Log Retention**: Set appropriate CloudWatch log retention periods (7-30 days for production) to manage costs
6. **Performance Baselines**: Establish resolver latency baselines and monitor for degradation over time
7. **Error Tracking**: Implement structured error logging with correlation IDs for request tracing across distributed systems
8. **Dashboard Creation**: Build CloudWatch dashboards showing API health, resolver performance, cache hit rates, and error distributions

### Security Best Practices

1. **Encryption in Transit**: Ensure all datasource connections use TLS/SSL; configure custom domain names with ACM certificates
2. **Encryption at Rest**: Enable encryption for all datasources (DynamoDB, RDS, OpenSearch) and use KMS customer-managed keys
3. **VPC Integration**: Deploy private AppSync APIs within VPCs for internal applications and sensitive workloads
4. **WAF Integration**: Use AWS WAF to protect public GraphQL APIs from common web exploits and DDoS attacks
5. **Secrets Management**: Store database credentials, API keys, and tokens in AWS Secrets Manager; access from Lambda resolvers
6. **CORS Configuration**: Configure appropriate CORS policies to restrict API access to authorized domains
7. **Query Depth Limiting**: Implement query complexity analysis and depth limiting to prevent resource exhaustion attacks
8. **Data Masking**: Implement field-level data masking in resolvers for sensitive information (PII, PHI)
9. **Audit Logging**: Enable CloudTrail logging for all AppSync API management operations and configuration changes
10. **DDoS Protection**: Use AWS Shield Standard (included) and consider Shield Advanced for critical public APIs

### Cost Optimization

1. **Caching Strategy**: Implement aggressive caching for read-heavy workloads to reduce query and datasource costs
2. **Query Optimization**: Design efficient queries that request only required fields; avoid over-fetching data
3. **Batching Requests**: Use GraphQL query batching to combine multiple operations into single requests
4. **Lambda Provisioned Concurrency**: Use provisioned concurrency only for Lambda resolvers with strict latency requirements
5. **DynamoDB On-Demand**: Consider DynamoDB on-demand billing for variable workloads instead of provisioned capacity
6. **HTTP Datasource Preference**: Use HTTP datasources for external APIs to avoid Lambda invocation costs when possible
7. **Log Filtering**: Implement selective field-level logging to reduce CloudWatch costs while maintaining observability
8. **API Key vs Cognito**: Use API keys for public read-only access to avoid Cognito MAU charges
9. **Cache TTL Tuning**: Balance cache hit rates with data freshness requirements to maximize caching benefits
10. **Reserved Capacity**: For predictable workloads, consider reserved capacity for DynamoDB and RDS datasources

### High Availability and Disaster Recovery

1. **Multi-region Strategy**: Deploy AppSync APIs in multiple regions with Route53 health checks for global applications
2. **Datasource Redundancy**: Use multi-AZ RDS deployments and DynamoDB global tables for datasource resilience
3. **Fallback Resolvers**: Implement graceful degradation in resolvers when datasources are unavailable
4. **Circuit Breaker Pattern**: Use circuit breakers in Lambda resolvers to prevent cascading failures
5. **Backup Strategy**: Implement regular backups for DynamoDB tables and RDS databases used as datasources
6. **Subscription Resilience**: Design subscription clients with automatic reconnection logic for WebSocket failures
7. **Schema Version Control**: Store GraphQL schemas in version control (Git) and implement IaC deployment workflows
8. **Testing Strategy**: Implement comprehensive integration tests for resolvers and end-to-end API tests
9. **Rollback Plan**: Maintain ability to quickly roll back schema changes and resolver updates
10. **Health Checks**: Implement health check queries for monitoring and automated recovery workflows

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-appsync
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/appsync/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-appsync/tree/master/examples
- **AWS AppSync Documentation**: https://docs.aws.amazon.com/appsync/latest/devguide/welcome.html
- **GraphQL Schema Design**: https://docs.aws.amazon.com/appsync/latest/devguide/designing-a-graphql-api.html
- **AppSync Resolver Tutorial**: https://docs.aws.amazon.com/appsync/latest/devguide/resolver-mapping-template-reference.html
- **JavaScript Resolvers**: https://docs.aws.amazon.com/appsync/latest/devguide/resolver-reference-js.html
- **Real-time Subscriptions**: https://docs.aws.amazon.com/appsync/latest/devguide/aws-appsync-real-time-data.html
- **AppSync Security**: https://docs.aws.amazon.com/appsync/latest/devguide/security.html
- **AppSync Pricing**: https://aws.amazon.com/appsync/pricing/
- **GraphQL Best Practices**: https://graphql.org/learn/best-practices/
- **Amplify AppSync Integration**: https://docs.amplify.aws/lib/graphqlapi/getting-started/q/platform/js/
- **AppSync Caching**: https://docs.aws.amazon.com/appsync/latest/devguide/enabling-caching.html
- **AppSync Monitoring**: https://docs.aws.amazon.com/appsync/latest/devguide/monitoring.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Schema Validation**: Always validate GraphQL schemas before deployment using GraphQL validation tools
2. **Authentication Strategy**: Choose authentication type based on use case (API Key for prototyping, Cognito for production user apps, IAM for service-to-service)
3. **Datasource Selection**: Select datasources based on access patterns (DynamoDB for key-value, RDS for relational, Lambda for custom logic, HTTP for external APIs)
4. **Resolver Complexity**: Start with simple unit resolvers and evolve to pipeline resolvers only when needed for multi-step operations
5. **Enable Monitoring**: Always enable CloudWatch logging and X-Ray tracing during development; adjust for production costs
6. **Caching Configuration**: Implement caching for read-heavy APIs with TTLs appropriate to data freshness requirements
7. **Security First**: Use least privilege IAM roles, encrypt datasources at rest, and implement field-level authorization
8. **Testing Approach**: Write integration tests for all resolvers and test subscription behavior with WebSocket clients
9. **Cost Awareness**: Monitor query/mutation costs and implement query complexity limits for public APIs
10. **Version Management**: Use Terraform workspaces or separate modules for dev/staging/production environments
11. **Schema Evolution**: Plan for schema evolution with field deprecation rather than breaking changes
12. **Custom Domains**: Configure custom domains with ACM certificates for production APIs for better branding and security
