---
module_name: ecr
keywords: [ecr, elastic-container-registry, container-registry, docker, container-images, image-repository, private-registry, public-registry, image-scanning, vulnerability-scanning, lifecycle-policy, image-retention, image-tagging, tag-mutability, immutable-tags, mutable-tags, kms-encryption, aes256-encryption, repository-policy, registry-policy, iam-access, cross-account-access, replication, multi-region, pull-through-cache, upstream-registry, dockerhub, image-pull, image-push, registry-scanning, continuous-scanning, scan-on-push, ecr-public, repository-template, force-delete, catalog-data, operating-systems, architectures]
---

# Terraform AWS ECR Module

## Module Information

- **Module Name**: `ecr`
- **Source**: `terraform-aws-modules/ecr/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ecr
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ecr/aws/latest
- **Latest Version**: 3.1.0
- **Purpose**: Terraform module that creates and manages AWS Elastic Container Registry (ECR) repositories for storing Docker and OCI container images
- **Service**: AWS ECR (Elastic Container Registry)
- **Category**: Container Management, DevOps, CI/CD
- **Keywords**: ecr, elastic-container-registry, container-registry, docker, container-images, image-repository, private-registry, public-registry, image-scanning, vulnerability-scanning, lifecycle-policy, image-retention, image-tagging, tag-mutability, immutable-tags, mutable-tags, kms-encryption, aes256-encryption, repository-policy, registry-policy, iam-access, cross-account-access, replication, multi-region, pull-through-cache, upstream-registry, dockerhub, image-pull, image-push, registry-scanning, continuous-scanning, scan-on-push, ecr-public, repository-template, force-delete, catalog-data, operating-systems, architectures
- **Use For**: container image storage, Docker image hosting, Kubernetes container registry, CI/CD pipelines, microservices deployments, multi-region image distribution, container vulnerability scanning, image lifecycle management, private container registries, public container sharing, cross-account image access, container image caching

## Description

AWS Elastic Container Registry (ECR) is a fully managed container registry service that makes it easy to store, manage, share, and deploy container images and artifacts. This Terraform module provides a comprehensive solution for creating and managing both private and public ECR repositories with extensive configuration options for security, lifecycle management, replication, and access control. The module simplifies the setup of container registries while providing the flexibility needed for enterprise-grade container image management across development, staging, and production environments.

The module supports a wide range of ECR features including image scanning for vulnerabilities, lifecycle policies for automatic image cleanup, cross-region replication for high availability, and pull-through cache rules for upstream registries like DockerHub and public ECR. It enables fine-grained access control through repository policies and IAM integration, supports both mutable and immutable image tags, and provides encryption options using AWS KMS or AES256. The module can create both private repositories (for internal use) and public repositories (for sharing images with the community), with full support for catalog metadata, architecture specifications, and operating system compatibility declarations.

This module is essential for organizations running containerized workloads on AWS, particularly those using Amazon ECS, EKS, or Fargate. It integrates seamlessly with CI/CD pipelines, supports multi-account and multi-region architectures, and provides the building blocks for implementing container security best practices. The module's support for pull-through cache rules enables efficient caching of images from external registries, reducing bandwidth costs and improving deployment reliability. With comprehensive tagging, monitoring, and lifecycle management capabilities, this module serves as the foundation for scalable and secure container image management in AWS.

## Key Features

- **Private Repository Creation**: Create private ECR repositories for storing proprietary container images with access control
- **Public Repository Support**: Create public ECR repositories for sharing container images with the broader community
- **Image Tag Mutability**: Configure repositories as mutable (tags can be overwritten) or immutable (tags are write-once) with tag exclusion filters
- **Image Scanning on Push**: Automatically scan container images for vulnerabilities immediately after push using enhanced or basic scanning
- **Continuous Image Scanning**: Enable ongoing vulnerability scanning of images to detect newly discovered CVEs
- **Lifecycle Policies**: Define automated image retention rules based on age, count, or tag patterns to manage storage costs
- **KMS Encryption**: Encrypt repository images at rest using AWS KMS customer-managed keys for enhanced security
- **AES256 Encryption**: Use AWS-managed encryption (AES256) as the default encryption method for images
- **Repository Policies**: Configure fine-grained IAM policies for controlling push, pull, and administrative access to repositories
- **Registry Policies**: Implement registry-level policies for cross-account access and organization-wide permissions
- **Cross-Region Replication**: Automatically replicate images to multiple AWS regions for disaster recovery and reduced latency
- **Pull-Through Cache Rules**: Cache images from upstream registries (DockerHub, public ECR, private registries) to reduce pull times and costs
- **Registry Scanning Configuration**: Configure advanced scanning options including scan frequency, scan filters, and scan types (basic vs enhanced)
- **Repository Templates**: Use predefined templates for standardized repository configurations across teams and projects
- **Force Delete Option**: Enable force deletion of repositories even when they contain images for infrastructure automation
- **Catalog Metadata**: Add descriptions, usage instructions, logo images, and architecture details for public repositories
- **Access Control Lists**: Define read-only and read-write access ARNs for simplified IAM integration
- **Tagging Support**: Comprehensive tagging for resource organization, cost allocation, and compliance tracking
- **Multi-Account Access**: Support for cross-account repository access using IAM policies and resource policies
- **Integration with ECS/EKS**: Native integration with Amazon ECS, EKS, and Fargate for seamless container deployments

## Main Use Cases

1. **CI/CD Container Image Storage**: Store application container images built by CI/CD pipelines for automated deployments
2. **Microservices Image Management**: Manage container images for microservices architectures with multiple services and versions
3. **Kubernetes Cluster Registry**: Serve as the container registry for Amazon EKS clusters and self-managed Kubernetes
4. **Multi-Region Application Deployment**: Replicate images across regions for global application deployments with low latency
5. **Container Security Scanning**: Automatically scan images for vulnerabilities and compliance issues before production deployment
6. **Image Lifecycle Management**: Automatically clean up old or unused images to optimize storage costs
7. **Cross-Account Image Sharing**: Share container images across AWS accounts for multi-account architectures
8. **Public Image Distribution**: Host and distribute open-source or community container images via public repositories
9. **DockerHub Caching**: Cache frequently used DockerHub images to reduce pull times and avoid rate limits
10. **Development Environment Standardization**: Provide standardized base images and development tools across engineering teams

## Best Practices

### Repository Configuration

1. **Use Immutable Tags for Production**: Enable immutable tags for production repositories to prevent accidental tag overwrites and ensure deployment consistency
2. **Configure Tag Exclusion Patterns**: Use tag mutability exclusions for development tags (e.g., "latest", "dev-*") while keeping production tags immutable
3. **Enable Force Delete Carefully**: Only enable force delete for development/test repositories; never for production to prevent accidental data loss
4. **Use Descriptive Repository Names**: Name repositories clearly using patterns like `{service-name}`, `{team}/{service}`, or `{environment}/{application}`
5. **Separate Repositories by Environment**: Consider separate repositories for dev, staging, and production images for better access control and lifecycle management

### Security and Access Control

1. **Enable Image Scanning**: Always enable scan-on-push for automated vulnerability detection; add continuous scanning for ongoing security monitoring
2. **Use Enhanced Scanning**: Enable enhanced scanning (Amazon Inspector integration) for deeper vulnerability analysis and OS package CVE detection
3. **Encrypt with KMS**: Use KMS encryption for sensitive images to maintain full control over encryption keys and meet compliance requirements
4. **Implement Least Privilege Access**: Configure repository policies granting minimum necessary permissions to users, roles, and services
5. **Use Private Repositories by Default**: Create public repositories only when explicitly needed for community sharing or open-source projects
6. **Enable VPC Endpoints**: Use VPC endpoints for ECR to keep image pull/push traffic within AWS network and reduce data transfer costs
7. **Rotate Access Credentials**: Regularly rotate IAM credentials and access keys used for ECR authentication
8. **Monitor Unauthorized Access**: Enable CloudTrail logging and set up alarms for unauthorized push/pull attempts
9. **Scan Before Production**: Implement gates in CI/CD pipelines to block deployment of images with critical vulnerabilities
10. **Use IAM Roles**: Prefer IAM roles over IAM users for ECS tasks, Lambda functions, and EC2 instances accessing ECR

### Lifecycle and Retention

1. **Implement Lifecycle Policies**: Define lifecycle rules to automatically remove old images and reduce storage costs
2. **Keep Recent Images**: Configure lifecycle policies to retain the last N images (e.g., 30) or images from the last N days (e.g., 90)
3. **Protect Production Tags**: Use lifecycle policy rules that preserve images with production tags (e.g., "prod-*", "v*.*.*")
4. **Clean Untagged Images**: Create rules to delete untagged images after a short period (e.g., 1-7 days) to prevent storage bloat
5. **Test Lifecycle Policies**: Validate lifecycle policies in non-production environments before applying to production repositories
6. **Monitor Image Count**: Set up CloudWatch alarms for repository image counts to detect lifecycle policy issues
7. **Document Retention Requirements**: Clearly document retention requirements for compliance and disaster recovery purposes

### Replication and Availability

1. **Enable Cross-Region Replication**: Replicate images to multiple regions for disaster recovery, reduced latency, and compliance requirements
2. **Use Replication Filters**: Apply prefix or tag filters to replicate only necessary images and reduce replication costs
3. **Monitor Replication Status**: Track replication lag and failures using CloudWatch metrics and set up alerts for issues
4. **Replicate to DR Regions**: Ensure production images are replicated to disaster recovery regions for business continuity
5. **Consider Replication Costs**: Balance availability needs with data transfer costs when designing multi-region replication strategies
6. **Test Cross-Region Failover**: Regularly test application deployments using replicated images from secondary regions

### Pull-Through Cache

1. **Cache External Registries**: Configure pull-through cache rules for DockerHub and other registries to reduce latency and avoid rate limits
2. **Monitor Cache Hit Rates**: Track cache hit rates to optimize cache rules and reduce upstream registry costs
3. **Secure Upstream Credentials**: Store upstream registry credentials in AWS Secrets Manager for pull-through cache authentication
4. **Update Cache Rules**: Regularly review and update cache rules as external registry requirements change
5. **Use for Base Images**: Prioritize caching frequently used base images (e.g., Alpine, Ubuntu, Node) to maximize benefit

### Monitoring and Observability

1. **Enable CloudWatch Metrics**: Monitor repository metrics including push/pull counts, image sizes, and scan findings
2. **Set Up Scan Finding Alarms**: Create alarms for critical vulnerability findings to trigger immediate remediation
3. **Track Storage Usage**: Monitor repository storage usage and set budgets to control costs
4. **Log API Calls**: Enable CloudTrail logging for all ECR API calls for security auditing and troubleshooting
5. **Dashboard Key Metrics**: Create CloudWatch dashboards showing image push/pull rates, scan results, and repository health
6. **Monitor Replication Lag**: Track cross-region replication delays to ensure images are available when needed
7. **Alert on Failed Scans**: Set up notifications for failed image scans to prevent deploying unscanned images

### Cost Optimization

1. **Implement Lifecycle Policies**: Use aggressive lifecycle policies to remove unused images and minimize storage costs
2. **Right-Size Repositories**: Avoid over-provisioning repositories; create only what's needed for your workloads
3. **Monitor Storage Costs**: Regularly review ECR storage costs by repository and implement cleanup for high-cost repositories
4. **Use Pull-Through Cache**: Reduce data transfer costs by caching external images rather than repeatedly pulling from the internet
5. **Optimize Image Sizes**: Encourage developers to create smaller images using multi-stage builds and minimal base images
6. **Clean Up Test Images**: Implement automation to delete ephemeral test images created during CI/CD runs
7. **Review Public Repository Usage**: Monitor public repository bandwidth usage to avoid unexpected charges from excessive pulls

### Development and Deployment

1. **Integrate with CI/CD**: Automate image builds, tagging, pushing, and scanning as part of CI/CD pipelines
2. **Use Semantic Versioning**: Tag production images with semantic versions (e.g., "v1.2.3") for clear version tracking
3. **Implement Multi-Stage Builds**: Use Docker multi-stage builds to reduce final image size and minimize attack surface
4. **Tag with Git Commit SHA**: Include git commit SHA in image tags for traceability between code and deployed images
5. **Test Images Locally**: Validate images work correctly before pushing to ECR to reduce failed deployments
6. **Use Consistent Tagging**: Establish and enforce consistent tagging conventions across teams (e.g., "environment-version-sha")
7. **Automate Vulnerability Response**: Implement automated workflows to rebuild and redeploy images when vulnerabilities are patched
8. **Document Image Contents**: Maintain documentation of what's included in each image and its intended use cases

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-ecr
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ecr/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-ecr/tree/master/examples
- **AWS ECR Documentation**: https://docs.aws.amazon.com/ecr/latest/userguide/what-is-ecr.html
- **AWS ECR API Reference**: https://docs.aws.amazon.com/ecr/latest/APIReference/Welcome.html
- **ECR Image Scanning**: https://docs.aws.amazon.com/ecr/latest/userguide/image-scanning.html
- **ECR Lifecycle Policies**: https://docs.aws.amazon.com/ecr/latest/userguide/LifecyclePolicies.html
- **ECR Replication**: https://docs.aws.amazon.com/ecr/latest/userguide/replication.html
- **ECR Pull Through Cache**: https://docs.aws.amazon.com/ecr/latest/userguide/pull-through-cache.html
- **ECR Best Practices**: https://docs.aws.amazon.com/ecr/latest/userguide/best-practices.html
- **ECR Security**: https://docs.aws.amazon.com/ecr/latest/userguide/security.html
- **ECR Pricing**: https://aws.amazon.com/ecr/pricing/
- **ECR Public Gallery**: https://gallery.ecr.aws/
- **Container Image Security**: https://aws.amazon.com/blogs/containers/amazon-ecr-enhanced-scanning/

## Notes for AI Agents

When using this module in automated workflows:

1. **Choose Repository Type**: Determine if private or public repository is needed based on image sharing requirements
2. **Enable Security Features**: Always enable image scanning and use KMS encryption for sensitive workloads
3. **Configure Lifecycle Policies**: Implement lifecycle rules to automatically manage image retention and reduce costs
4. **Set Tag Mutability**: Use immutable tags for production repositories; allow mutable tags for development environments
5. **Implement Access Controls**: Configure repository policies with least privilege access for users and services
6. **Enable Replication**: Set up cross-region replication for production images to ensure high availability
7. **Use Pull-Through Cache**: Configure cache rules for external registries to improve reliability and reduce costs
8. **Monitor Scan Results**: Integrate vulnerability scan results into CI/CD gates to prevent deploying vulnerable images
9. **Tag Resources**: Apply comprehensive tags for cost tracking, ownership, and automation purposes
10. **Plan for Scale**: Design repository structure and naming conventions to support growth across teams and services
11. **Automate Image Cleanup**: Use lifecycle policies and automation to prevent storage bloat from unused images
12. **Document Conventions**: Maintain clear documentation of tagging conventions, lifecycle policies, and access patterns
