---
module_name: apigateway-v2
keywords: [api-gateway, apigateway-v2, http-api, websocket-api, serverless, rest-api, lambda-integration, api-management, jwt-authorizer, cors, custom-domain, route53, acm, ssl-certificate, oauth2, openid-connect, api-routing, vpc-link, private-integration, proxy-integration, http-proxy, aws-proxy, api-gateway-stage, access-logging, cloudwatch-logs, throttling, rate-limiting, request-validation, response-transformation, api-key, usage-plan, authorizer, lambda-authorizer, request-authorizer, mutual-tls, mtls, client-certificate, stage-variables, deployment, auto-deploy, api-versioning, subdomain, domain-mapping, route-configuration, integration-configuration, websocket-routes, websocket-integrations, event-driven, real-time-api, bidirectional-communication, serverless-api, microservices-api, api-security, api-observability, api-monitoring]
---

# Terraform AWS API Gateway v2 Module

## Module Information

- **Module Name**: `apigateway-v2`
- **Source**: `terraform-aws-modules/apigateway-v2/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/latest
- **Latest Version**: 5.3.1
- **Purpose**: Terraform module that creates and manages AWS API Gateway v2 resources for building HTTP and WebSocket APIs with serverless architectures
- **Service**: AWS API Gateway v2 (Amazon API Gateway HTTP APIs and WebSocket APIs)
- **Category**: Serverless, API Management, Integration
- **Keywords**: api-gateway, apigateway-v2, http-api, websocket-api, serverless, rest-api, lambda-integration, api-management, jwt-authorizer, cors, custom-domain, route53, acm, ssl-certificate, oauth2, openid-connect, api-routing, vpc-link, private-integration, proxy-integration, http-proxy, aws-proxy, api-gateway-stage, access-logging, cloudwatch-logs, throttling, rate-limiting, request-validation, response-transformation, api-key, usage-plan, authorizer, lambda-authorizer, request-authorizer, mutual-tls, mtls, client-certificate, stage-variables, deployment, auto-deploy, api-versioning, subdomain, domain-mapping, route-configuration, integration-configuration, websocket-routes, websocket-integrations, event-driven, real-time-api, bidirectional-communication, serverless-api, microservices-api, api-security, api-observability, api-monitoring
- **Use For**: serverless API backends, Lambda function APIs, microservices API gateway, WebSocket real-time applications, API consolidation and routing, OAuth2 and JWT authentication, custom domain API hosting, event-driven architectures, bidirectional communication APIs, multi-backend API orchestration, cost-optimized API solutions, RESTful service endpoints

## Description

AWS API Gateway v2 is Amazon's next-generation managed API service that enables developers to create, publish, maintain, monitor, and secure HTTP and WebSocket APIs at scale. This Terraform module provides a comprehensive solution for deploying API Gateway v2 resources with support for both HTTP APIs (RESTful) and WebSocket APIs (bidirectional communication). The module simplifies the configuration of complex API Gateway features including routes, integrations, authorizers, custom domains, and CORS policies, making it ideal for serverless architectures and microservices deployments.

The module supports multiple integration types including AWS Lambda function invocations, HTTP proxy integrations to backend services, and VPC link integrations for private resource access. It provides flexible authentication and authorization options through JWT authorizers, custom Lambda authorizers, and OAuth2/OpenID Connect integration. The module handles the complete lifecycle of API Gateway resources including stage management, deployment automation, access logging configuration, and custom domain name mapping with Route 53 and ACM certificate integration.

Built as part of the serverless.tf framework, this module follows AWS best practices for API Gateway deployments and provides advanced features such as mutual TLS authentication, throttling and rate limiting, stage variables for environment-specific configurations, and comprehensive CloudWatch integration for monitoring and observability. The module's design supports multi-environment deployments with conditional resource creation, flexible route and integration configurations, and extensive tagging capabilities for resource organization and cost allocation. It is particularly well-suited for building cost-effective, scalable API solutions that integrate seamlessly with AWS Lambda, containerized services, and external HTTP endpoints.

## Key Features

- **HTTP API Support**: Create lightweight, cost-effective HTTP APIs with up to 71% cost savings compared to REST APIs
- **WebSocket API Support**: Build real-time bidirectional communication APIs for chat applications, streaming, and live updates
- **Lambda Integration**: Seamless integration with AWS Lambda functions using AWS_PROXY integration type
- **HTTP Proxy Integration**: Route requests to HTTP endpoints and backend services with HTTP_PROXY integration
- **VPC Link Integration**: Connect to private resources in VPCs without exposing them to the public internet
- **JWT Authorizers**: Built-in JWT token validation for OAuth2 and OpenID Connect authentication flows
- **Custom Lambda Authorizers**: Implement custom authorization logic using Lambda functions for REQUEST authorizers
- **CORS Configuration**: Automatic cross-origin resource sharing support with flexible origin, method, and header controls
- **Custom Domain Names**: Map APIs to custom domains with Route 53 integration and ACM certificate management
- **Subdomain Support**: Configure multiple subdomains and wildcard domain mappings for multi-tenant architectures
- **Mutual TLS**: Enhanced security with client certificate validation using mutual TLS authentication
- **Route Configuration**: Define multiple API routes with HTTP methods, route keys, and route-specific settings
- **Integration Settings**: Configure timeout, payload format version, and connection type for each integration
- **Stage Management**: Create and manage deployment stages with stage-specific configurations and variables
- **Auto Deployment**: Automatic API deployment on configuration changes for streamlined development workflows
- **Access Logging**: Comprehensive request and response logging to CloudWatch Logs with customizable log formats
- **Throttling and Rate Limiting**: Configure request throttling at stage and route levels to protect backend services
- **Stage Variables**: Environment-specific configuration values accessible in integrations and authorizers
- **API Gateway v2 Features**: Leverage latest features including better performance, lower latency, and simplified pricing
- **Conditional Creation**: Fine-grained control over resource creation with boolean flags for flexible deployments
- **Comprehensive Tagging**: Apply consistent tags across all resources for organization, cost tracking, and governance
- **CloudWatch Integration**: Built-in metrics, logging, and monitoring for API performance and health tracking
- **Multiple API Support**: Create and manage multiple API Gateway instances from a single module configuration
- **Cost Optimization**: Benefit from simplified pricing model with no data transfer charges for HTTP APIs
- **Serverless Framework Integration**: Part of serverless.tf ecosystem for unified serverless infrastructure management

## Main Use Cases

1. **Serverless REST APIs**: Build RESTful APIs backed by AWS Lambda functions for serverless application backends
2. **Microservices Gateway**: Create unified API gateway for routing requests to multiple microservices
3. **WebSocket Applications**: Deploy real-time bidirectional communication for chat, gaming, and streaming applications
4. **API Consolidation**: Aggregate multiple backend services behind a single API endpoint with custom routing
5. **Mobile App Backends**: Provide secure, scalable API endpoints for mobile applications with JWT authentication
6. **Third-Party Integrations**: Proxy and transform requests to external HTTP APIs with rate limiting and caching
7. **Event-Driven Architectures**: Build event-driven systems using WebSocket connections for real-time notifications
8. **OAuth2 API Gateway**: Implement secure API access with OAuth2 and OpenID Connect authentication flows
9. **Multi-Tenant APIs**: Deploy multi-tenant SaaS APIs with custom domain mapping and tenant isolation
10. **Private API Access**: Expose private VPC resources through API Gateway using VPC links without public exposure

## Best Practices

### API Configuration and Design

1. **Choose HTTP APIs for Cost Efficiency**: Use HTTP APIs instead of REST APIs for 71% cost savings when advanced features aren't required
2. **Use WebSocket for Bidirectional**: Deploy WebSocket APIs for real-time, bidirectional communication rather than polling HTTP endpoints
3. **Design RESTful Routes**: Follow RESTful conventions for HTTP method and resource path combinations (GET /users, POST /users)
4. **Implement API Versioning**: Use path-based versioning (/v1/, /v2/) or custom domains for major API version changes
5. **Consolidate Routes**: Group related functionality under a single API Gateway to reduce management overhead and costs
6. **Use Descriptive API Names**: Name APIs clearly indicating environment, purpose, and protocol (e.g., "prod-user-service-http")
7. **Configure CORS Appropriately**: Set specific allowed origins rather than wildcards (*) in production for security

### Integration and Backend Configuration

1. **Prefer AWS_PROXY for Lambda**: Use AWS_PROXY integration type for Lambda to automatically pass request context and simplify response handling
2. **Set Appropriate Timeouts**: Configure integration timeouts based on backend response times (default 30s for HTTP, 29s for Lambda)
3. **Use Payload Format 2.0**: Leverage payload format version 2.0 for Lambda integrations for simplified event structure
4. **Implement Health Checks**: Add health check routes for monitoring backend service availability
5. **Configure VPC Links for Private Resources**: Use VPC links instead of public endpoints when accessing resources in VPCs
6. **Batch Operations**: Design APIs to support batch operations to reduce request count and improve performance
7. **Use Connection Reuse**: Enable connection reuse for HTTP integrations to backend services to improve latency

### Security and Authentication

1. **Enable JWT Authorizers**: Use JWT authorizers for OAuth2 and OpenID Connect authentication instead of custom Lambda authorizers when possible
2. **Implement Least Privilege**: Configure authorizer scopes to grant minimum necessary permissions for each route
3. **Use Mutual TLS**: Enable mutual TLS authentication for sensitive APIs requiring client certificate validation
4. **Secure Custom Domains**: Always use HTTPS with ACM certificates for custom domain configurations
5. **Rotate Client Certificates**: Establish regular rotation schedules for client certificates used in mutual TLS
6. **Validate JWT Claims**: Configure JWT authorizer to validate all required claims including issuer, audience, and scopes
7. **Implement Rate Limiting**: Apply throttling and rate limits at API and route levels to prevent abuse and DDoS attacks
8. **Restrict CORS Origins**: In production, specify exact allowed origins rather than using wildcard configurations
9. **Use WAF Integration**: Deploy AWS WAF in front of API Gateway for additional protection against common web exploits
10. **Enable Access Logging**: Always enable access logging to CloudWatch Logs for security auditing and threat detection

### Performance and Optimization

1. **Enable Caching**: Use API Gateway caching for frequently requested data to reduce backend load and improve latency
2. **Optimize Payload Size**: Keep request and response payloads small; use compression for large responses
3. **Configure Appropriate Throttling**: Set throttle limits based on backend capacity to prevent overwhelming downstream services
4. **Use Regional Endpoints**: Deploy regional API endpoints for lower latency compared to edge-optimized endpoints
5. **Minimize Integration Latency**: Place Lambda functions and backends in the same region as API Gateway
6. **Implement Connection Pooling**: Reuse database and HTTP connections in Lambda functions to reduce cold start impact
7. **Monitor Performance Metrics**: Track API latency, integration latency, and 4XX/5XX errors in CloudWatch
8. **Optimize Lambda Cold Starts**: Use provisioned concurrency for latency-sensitive Lambda integrations

### Cost Optimization

1. **Choose HTTP APIs Over REST**: Use HTTP APIs for up to 71% cost savings when REST API features aren't needed
2. **Implement Efficient Throttling**: Set throttle limits to prevent runaway costs from unexpected traffic spikes
3. **Use Regional Endpoints**: Regional endpoints are cheaper than edge-optimized endpoints and suitable for most use cases
4. **Optimize Logging**: Log only necessary information and set appropriate CloudWatch log retention periods
5. **Leverage Free Tier**: Take advantage of AWS Free Tier offering first 1 million API calls free per month
6. **Batch API Calls**: Design clients to batch multiple operations into single requests to reduce API call counts
7. **Monitor Usage Patterns**: Regularly review CloudWatch metrics to identify and optimize high-cost API routes
8. **Consolidate APIs**: Reduce number of APIs and stages where possible to minimize management overhead

### Monitoring and Observability

1. **Enable Access Logging**: Configure detailed access logs with request ID, caller IP, method, path, and response codes
2. **Use Structured Logging**: Format access logs in JSON for easier parsing and analysis with log analytics tools
3. **Set Up CloudWatch Alarms**: Create alarms for 4XX errors, 5XX errors, latency, and throttled requests
4. **Monitor Integration Latency**: Track integration latency separately from total latency to identify backend bottlenecks
5. **Enable X-Ray Tracing**: Use AWS X-Ray for distributed tracing across API Gateway and Lambda integrations
6. **Dashboard Key Metrics**: Create CloudWatch dashboards showing API request count, latency distribution, and error rates
7. **Log Retention Strategy**: Set CloudWatch log retention to 7-30 days for non-production, 90+ days for production
8. **Track Throttling Events**: Monitor throttled request metrics to identify capacity constraints and adjust limits

### Deployment and Operations

1. **Use Auto-Deployment**: Enable auto-deployment for development environments to streamline testing workflows
2. **Implement Blue-Green Deployments**: Use multiple stages (blue, green) for zero-downtime production deployments
3. **Stage Variables for Environments**: Use stage variables to parameterize backend endpoints across dev, staging, and production
4. **Version Control Configuration**: Store all API Gateway configuration in Terraform for version control and reproducibility
5. **Test in Staging First**: Deploy and test API changes in staging environment before promoting to production
6. **Implement Canary Releases**: Use stage deployment canary settings to gradually roll out changes to production
7. **Document API Contracts**: Maintain OpenAPI/Swagger specifications for API documentation and client SDK generation
8. **Automate Testing**: Implement integration tests that validate API functionality in CI/CD pipelines

### Custom Domain and DNS

1. **Use ACM Certificates**: Always use AWS Certificate Manager for SSL/TLS certificates with automatic renewal
2. **Configure Multiple Domains**: Use separate custom domains for different environments (api.example.com, api-staging.example.com)
3. **Implement Domain Mapping**: Map different API stages to different paths or subdomains for organized access
4. **Use Route 53 Alias Records**: Create Route 53 alias records pointing to API Gateway domain names for better performance
5. **Plan for Domain Changes**: Maintain backward compatibility when changing custom domains; use redirects if needed
6. **Enable Domain Validation**: Use DNS validation for ACM certificates for automated renewal
7. **Consider Wildcard Certificates**: Use wildcard certificates (*.api.example.com) for flexible subdomain management

### High Availability and Disaster Recovery

1. **Deploy in Multiple Regions**: For critical APIs, deploy to multiple regions with Route 53 failover routing
2. **Implement Health Checks**: Configure Route 53 health checks for multi-region failover detection
3. **Document Recovery Procedures**: Maintain runbooks for API Gateway disaster recovery scenarios
4. **Backup Configuration**: Store all API configurations in version-controlled Terraform code for rapid recreation
5. **Test Failover Scenarios**: Regularly test regional failover and recovery procedures
6. **Monitor Regional Health**: Set up cross-region monitoring to detect regional service issues
7. **Use Multiple Availability Zones**: API Gateway automatically uses multiple AZs within a region for high availability

### Development Best Practices

1. **Use Infrastructure as Code**: Manage all API Gateway resources through Terraform for consistency and repeatability
2. **Implement Local Testing**: Use tools like LocalStack or SAM Local for local API development and testing
3. **Modularize Configuration**: Break complex API configurations into reusable Terraform modules by feature or service
4. **Use For_Each for Multiple Routes**: Leverage Terraform for_each to define multiple routes and integrations efficiently
5. **Tag Comprehensively**: Apply consistent tags including environment, service, cost-center, and owner
6. **Separate Environments**: Use separate AWS accounts or isolated resources for dev, staging, and production APIs
7. **Version Pin Module**: Pin module version in production: `version = "~> 5.3"` to prevent unexpected changes
8. **Review API Changes**: Use terraform plan to review all API changes before applying to production

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-apigateway-v2/tree/master/examples
- **AWS API Gateway v2 Documentation**: https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html
- **HTTP APIs Documentation**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html
- **WebSocket APIs Documentation**: https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api.html
- **JWT Authorizers**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html
- **Lambda Integration**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
- **VPC Links**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vpc-links.html
- **Custom Domain Names**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-custom-domain-names.html
- **CORS Configuration**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-cors.html
- **Mutual TLS**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-mutual-tls.html
- **API Gateway Pricing**: https://aws.amazon.com/api-gateway/pricing/
- **Best Practices**: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-best-practices.html
- **Serverless.tf Framework**: https://serverless.tf/

## Notes for AI Agents

When using this module in automated workflows:

1. **Protocol Selection**: Choose `protocol_type = "HTTP"` for REST APIs or `protocol_type = "WEBSOCKET"` for bidirectional communication
2. **Integration Configuration**: Use `AWS_PROXY` for Lambda integrations and `HTTP_PROXY` for backend HTTP services
3. **Payload Format**: Set `payload_format_version = "2.0"` for Lambda integrations to use simplified event structure
4. **CORS Setup**: Configure CORS explicitly with specific origins, methods, and headers rather than using wildcards in production
5. **Authorizer Choice**: Prefer JWT authorizers for OAuth2/OIDC flows; use Lambda authorizers for custom logic
6. **Custom Domains**: Ensure ACM certificates are validated and in the same region as the API Gateway
7. **Route Definition**: Define routes using format `"{METHOD} {path}"` (e.g., `"GET /users"`, `"POST /orders"`)
8. **Stage Configuration**: Use stage variables to parameterize backend endpoints across environments
9. **Logging Configuration**: Always enable access logging with CloudWatch log group and appropriate retention
10. **Throttling Settings**: Configure throttle settings at both stage and route levels based on backend capacity
11. **Monitoring Setup**: Implement CloudWatch alarms for 4XX/5XX errors, latency, and throttled requests
12. **Tagging Strategy**: Apply comprehensive tags for environment, service, cost-center, and owner
13. **Multi-Region Deployment**: For high availability, deploy identical configurations to multiple regions
14. **VPC Links**: Create VPC links separately and reference them in private integrations
15. **Testing**: Validate API configurations in non-production environments before deploying to production
