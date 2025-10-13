# Terraform AWS App Runner Module

## Module Information

- **Module Name**: `app-runner`
- **Source**: `terraform-aws-modules/app-runner/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-app-runner
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/app-runner/aws/latest
- **Latest Version**: 1.2.1
- **Purpose**: Terraform module that creates and manages AWS App Runner services for deploying containerized web applications from source code or container images
- **Service**: AWS App Runner (Fully Managed Container Application Service)
- **Category**: Serverless, Compute, Platform-as-a-Service, Container Orchestration
- **Keywords**: app-runner, apprunner, container, containerized, docker, web-app, web-application, paas, platform-as-a-service, serverless, auto-scaling, autoscaling, github, ecr, source-code, deployment, ci-cd, continuous-deployment, vpc, vpc-connector, private-network, ingress, custom-domain, health-check, observability, x-ray, tracing, iam-role, encryption, kms, secrets-manager, environment-variables, instance-configuration, networking, load-balancer, managed-service, automated-deployment, scaling, cpu, memory, concurrency, connection, code-repository, image-repository, certificate, dns, route53
- **Use For**: Deploying containerized web APIs and microservices without managing infrastructure, building serverless web applications with automatic scaling, creating CI/CD pipelines for container-based applications, hosting internal services with private VPC networking, deploying GitHub repositories as web services with automatic builds, running container images from ECR with managed deployments, implementing auto-scaling web applications with custom domains, building multi-tenant SaaS platforms with isolated App Runner services, migrating web workloads to serverless without Kubernetes complexity, developing rapid prototypes with container-based deployments

## Description

The AWS App Runner Terraform module provides a comprehensive solution for deploying and managing containerized web applications on AWS without the operational overhead of managing servers, clusters, or container orchestration platforms. App Runner is a fully managed service that takes source code or container images as input and automatically builds, deploys, scales, and load balances web applications and APIs. The module abstracts the complexity of configuring App Runner services, auto-scaling policies, networking, observability, and IAM roles into a declarative Terraform interface with flexible configuration options for both simple and advanced deployment scenarios.

This module supports two primary deployment models: code-based services that connect directly to GitHub repositories and automatically build and deploy on code commits, and image-based services that deploy pre-built container images from Amazon ECR or public registries. It provides comprehensive control over instance configurations including CPU, memory, and concurrency limits, auto-scaling parameters for request-based scaling, health check settings for application monitoring, and network configurations for VPC integration. The module handles the creation and management of IAM roles for both the App Runner access role (for pulling code/images) and the instance role (for application runtime permissions), supporting custom policy attachments and permissions boundaries.

The module enables advanced networking scenarios including private App Runner services accessible only within VPCs via VPC Ingress Connections, VPC Connectors for egress traffic to private resources like RDS databases, and custom domain associations with automatic certificate management. It integrates with AWS X-Ray for distributed tracing and observability, supports encryption configuration with KMS keys, manages environment variables and AWS Secrets Manager integration, and provides multiple auto-scaling configuration profiles. The module follows infrastructure-as-code best practices with support for tagging, conditional resource creation, and modular reusable configurations for managing multiple App Runner services across different environments.

## Key Features

- **Code-based Deployments**: Direct integration with GitHub repositories for automatic build and deployment on code commits
- **Image-based Deployments**: Support for deploying pre-built container images from Amazon ECR or public container registries
- **Auto-scaling Configuration**: Request-based auto-scaling with configurable min/max instances and target concurrent requests
- **Instance Configuration**: Flexible CPU (0.25-4 vCPU) and memory (0.5-12 GB) configurations with concurrency limits
- **VPC Connector**: Egress connectivity to private VPC resources like RDS, ElastiCache, and internal APIs
- **VPC Ingress Connection**: Private App Runner services accessible only from within specified VPCs
- **Custom Domain Association**: Automatic SSL certificate provisioning and DNS configuration for custom domains
- **Health Check Configuration**: Configurable health check paths, intervals, timeouts, thresholds, and protocols
- **Observability Integration**: AWS X-Ray distributed tracing for performance monitoring and debugging
- **IAM Role Management**: Automatic creation of access roles (for ECR/GitHub) and instance roles (for runtime permissions)
- **Environment Variables**: Support for runtime environment variables and AWS Secrets Manager integration
- **Encryption Configuration**: KMS encryption for service data and configuration
- **GitHub Connections**: Managed GitHub connections for code repository authentication
- **Multiple Auto-scaling Profiles**: Support for defining and reusing multiple auto-scaling configurations
- **Connection Management**: Centralized management of GitHub connections across multiple services
- **Conditional Creation**: Fine-grained control over which resources are created (service, roles, VPC resources)
- **Custom IAM Policies**: Support for attaching additional IAM policies to instance roles
- **Service Status Monitoring**: Outputs for service status, URLs, and resource identifiers
- **Tagging Support**: Comprehensive tagging for cost allocation and resource management

## Main Use Cases

1. **Serverless Web APIs**: Deploy RESTful APIs and GraphQL endpoints without managing servers or container orchestration
2. **Microservices Architecture**: Build microservices applications with independent, auto-scaling container deployments
3. **CI/CD Integration**: Implement continuous deployment pipelines with GitHub integration for automatic updates on code commits
4. **Internal Tools and Services**: Deploy private web applications accessible only within VPCs for internal team use
5. **Multi-tenant SaaS Platforms**: Create isolated App Runner services per tenant with dedicated scaling and networking
6. **Rapid Prototyping**: Quickly deploy containerized applications for proof-of-concept and development environments
7. **Migration from VMs**: Simplify infrastructure by migrating traditional VM-based web applications to managed containers
8. **Event-driven Applications**: Build web applications that integrate with other AWS services using VPC connectivity
9. **Static Site Backends**: Deploy backend APIs for JAMstack applications with automatic scaling
10. **Container Modernization**: Migrate Docker-based applications from on-premises or ECS/EKS without Kubernetes complexity

## Best Practices

### Service Configuration and Design

1. **Instance Sizing**: Start with smaller instance sizes (0.25 vCPU, 0.5 GB memory) and scale up based on performance metrics
2. **Concurrency Settings**: Configure concurrent requests per instance based on application thread model and blocking I/O patterns
3. **Stateless Design**: Design applications to be stateless; use external data stores (RDS, DynamoDB, ElastiCache) for session state
4. **Health Check Endpoints**: Implement dedicated health check endpoints that verify application dependencies and return quickly
5. **Graceful Shutdown**: Handle SIGTERM signals for graceful shutdown when App Runner replaces instances during deployments
6. **Container Optimization**: Use multi-stage Docker builds to minimize image size and improve deployment times
7. **Port Configuration**: Ensure application listens on the port specified in instance configuration (default 8080)
8. **Startup Time**: Optimize application startup time to reduce deployment duration and improve scaling responsiveness

### Auto-scaling Strategy

1. **Min/Max Instances**: Set minimum instances to 1 for cost savings in non-production; use 2+ for production high availability
2. **Concurrent Request Tuning**: Set target concurrent requests based on application capacity testing (typically 50-100)
3. **Scale-up Aggressiveness**: Configure conservative concurrent request targets to ensure responsive scaling during traffic spikes
4. **Scale-down Behavior**: Account for 5-minute scale-down delay when planning for variable traffic patterns
5. **Load Testing**: Perform load testing to determine optimal concurrency settings and instance sizing
6. **Monitoring Scaling Metrics**: Track App Runner's active instance count and request metrics to tune auto-scaling parameters
7. **Cost vs Availability**: Balance minimum instance count with cost considerations; use 0 min instances for dev environments
8. **Regional Scaling**: For global applications, deploy App Runner services in multiple regions with Route53 routing

### Networking and Connectivity

1. **VPC Connector Use Cases**: Use VPC connectors for accessing private RDS databases, ElastiCache, internal APIs, and on-premises resources via VPN
2. **Private Services**: Deploy private App Runner services with VPC Ingress Connections for internal-only applications
3. **Security Group Configuration**: Configure security groups on VPC connectors to restrict outbound access to specific resources
4. **Subnet Selection**: Use private subnets for VPC connector configuration; require NAT Gateway for internet access
5. **Multi-AZ Subnets**: Specify subnets in multiple availability zones for VPC connector high availability
6. **Network Isolation**: Use separate VPC connectors for different security zones (production vs development databases)
7. **Connection Pooling**: Implement connection pooling in applications when accessing VPC resources to avoid connection exhaustion
8. **DNS Configuration**: Use Route53 for custom domain configuration with health checks and failover routing

### Security Best Practices

1. **IAM Least Privilege**: Grant instance roles only the minimum permissions required for application functionality
2. **Secrets Management**: Store sensitive configuration (database passwords, API keys) in AWS Secrets Manager, not environment variables
3. **Encryption at Rest**: Enable KMS encryption for App Runner configuration data and service logs
4. **Private Image Repositories**: Use private ECR repositories for production container images; avoid public registries
5. **GitHub Connection Security**: Use GitHub App connections with granular repository access permissions
6. **Network Segmentation**: Deploy sensitive applications as private services with VPC Ingress Connections
7. **IAM Permissions Boundaries**: Apply permissions boundaries to App Runner IAM roles for regulatory compliance
8. **Secrets Rotation**: Implement automatic secret rotation for database credentials and API keys accessed by App Runner services
9. **TLS Enforcement**: App Runner enforces HTTPS by default; ensure all traffic uses TLS 1.2+
10. **Access Logging**: Enable CloudWatch Logs for App Runner service requests for security auditing

### Monitoring and Observability

1. **X-Ray Tracing**: Enable AWS X-Ray integration for distributed tracing and performance bottleneck identification
2. **CloudWatch Logs**: Configure structured logging with JSON format for easier querying and analysis
3. **Metrics and Alarms**: Create CloudWatch alarms for 4xx/5xx error rates, request latency, and active instance count
4. **Health Check Configuration**: Set health check intervals (5-20 seconds) and thresholds based on application reliability needs
5. **Application Logs**: Use CloudWatch Logs Insights for querying application logs and identifying errors
6. **Performance Baselines**: Establish baseline metrics for request latency and error rates for anomaly detection
7. **Deployment Tracking**: Monitor deployment success rates and rollback events in CloudWatch Events
8. **Custom Metrics**: Publish custom application metrics to CloudWatch from within the application code

### Cost Optimization

1. **Right-sizing Instances**: Choose the smallest instance size that meets performance requirements; avoid over-provisioning
2. **Minimum Instance Count**: Set minimum instances to 0 for dev/test environments to eliminate idle costs
3. **Request Optimization**: Optimize application code to handle more concurrent requests per instance
4. **Efficient Builds**: For code-based deployments, optimize build times to reduce build compute costs
5. **Image Caching**: Use Docker layer caching effectively to speed up builds and reduce ECR storage costs
6. **Environment Consolidation**: Use service tags and environment variables to run multiple tenants per service where appropriate
7. **Reserved Capacity**: Consider AWS Savings Plans for predictable, long-term workloads
8. **Traffic Routing**: Use ALB in front of multiple App Runner services to consolidate requests and reduce per-service minimums
9. **Idle Service Deletion**: Automatically delete or pause unused development App Runner services
10. **CloudWatch Log Retention**: Set appropriate log retention periods (7-30 days) to manage storage costs

### Deployment and CI/CD

1. **Blue-Green Deployments**: App Runner performs rolling deployments automatically; leverage for zero-downtime updates
2. **Deployment Rollback**: Monitor deployment health and use previous image versions or Git commits for quick rollback
3. **Pre-deployment Testing**: Run integration tests before deploying to App Runner using CI/CD pipeline stages
4. **Environment Promotion**: Use consistent Terraform modules across dev/staging/prod with different variable files
5. **Version Tagging**: Use semantic versioning for container images and Git tags for code-based deployments
6. **Deployment Validation**: Implement post-deployment smoke tests to verify service health after updates
7. **Infrastructure as Code**: Manage all App Runner resources via Terraform for reproducibility and version control
8. **Terraform State Management**: Use remote state (S3 + DynamoDB) with state locking for team environments
9. **Automated Deployments**: Configure GitHub Actions or CodePipeline to trigger deployments on merge to main branch
10. **Configuration Drift Detection**: Regularly run terraform plan to detect manual configuration changes

### High Availability and Disaster Recovery

1. **Multi-Region Deployments**: Deploy App Runner services in multiple AWS regions with Route53 failover for global availability
2. **Health Check Tuning**: Configure health check parameters to balance between fast failure detection and false positives
3. **Database Failover**: Use RDS read replicas or Aurora Global Database for multi-region database availability
4. **Backup Strategy**: While App Runner is stateless, ensure backing data stores have automated backups and point-in-time recovery
5. **Disaster Recovery Testing**: Periodically test failover procedures and recovery time objectives (RTO)
6. **Connection Redundancy**: For critical services, configure multiple VPC connectors across availability zones
7. **Service Dependencies**: Design applications with circuit breakers and retry logic for resilient dependency communication
8. **Graceful Degradation**: Implement fallback mechanisms when downstream services are unavailable
9. **Monitoring and Alerting**: Set up PagerDuty or SNS alerts for service failures and health check failures
10. **Runbook Documentation**: Maintain operational runbooks for common failure scenarios and recovery procedures

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-app-runner
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/app-runner/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-app-runner/tree/master/examples
- **AWS App Runner Documentation**: https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html
- **App Runner Developer Guide**: https://docs.aws.amazon.com/apprunner/latest/dg/
- **App Runner Service Configuration**: https://docs.aws.amazon.com/apprunner/latest/dg/service-source-code.html
- **App Runner VPC Networking**: https://docs.aws.amazon.com/apprunner/latest/dg/network.html
- **App Runner Auto-scaling**: https://docs.aws.amazon.com/apprunner/latest/dg/manage-autoscaling.html
- **App Runner Custom Domains**: https://docs.aws.amazon.com/apprunner/latest/dg/manage-custom-domains.html
- **App Runner Observability**: https://docs.aws.amazon.com/apprunner/latest/dg/monitor.html
- **App Runner Security**: https://docs.aws.amazon.com/apprunner/latest/dg/security.html
- **App Runner Pricing**: https://aws.amazon.com/apprunner/pricing/
- **Container Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **AWS Well-Architected Framework**: https://aws.amazon.com/architecture/well-architected/

## Notes for AI Agents

When using this module in automated workflows:

1. **Deployment Model Selection**: Choose code-based deployment for GitHub repositories with CI/CD, image-based for pre-built containers from ECR
2. **Instance Configuration**: Start with 1 vCPU and 2 GB memory for typical web APIs; adjust based on load testing results
3. **Auto-scaling Setup**: Configure min=1, max=10, concurrent_requests=100 as starting point for production services
4. **VPC Networking**: Use VPC connector when application needs to access RDS, ElastiCache, or internal services; not required for public APIs
5. **IAM Roles**: Always create separate access and instance roles; attach custom policies to instance role for AWS service access
6. **Secrets Management**: Use AWS Secrets Manager for sensitive values; avoid plain-text environment variables for credentials
7. **Health Checks**: Configure health check path to an endpoint that validates critical dependencies without heavy computation
8. **Observability**: Enable X-Ray tracing in production; configure CloudWatch log retention based on compliance requirements
9. **Custom Domains**: Use custom_domain_association for production; validate DNS configuration and certificate status
10. **Cost Management**: Set min_size=0 for non-production environments; monitor active instance count and request metrics
11. **Security Posture**: Use private App Runner services with VPC Ingress for internal applications; encrypt with KMS
12. **Deployment Strategy**: Use Terraform workspaces or separate state files for multi-environment deployments
