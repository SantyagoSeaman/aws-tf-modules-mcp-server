# Terraform AWS EKS Pod Identity Module

## Module Information

- **Module Name**: `eks-pod-identity`
- **Source**: `terraform-aws-modules/eks-pod-identity/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-eks-pod-identity
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eks-pod-identity/aws/latest
- **Latest Version**: 1.4.1
- **Purpose**: Terraform module that creates IAM roles and Pod Identity associations for Amazon EKS clusters, enabling fine-grained IAM permissions for Kubernetes pods
- **Service**: AWS EKS (Elastic Kubernetes Service)
- **Category**: Container Orchestration, Security, Identity and Access Management
- **Keywords**: eks, pod-identity, iam, kubernetes, service-account, rbac, irsa, oidc, cluster-autoscaler, external-dns, external-secrets, load-balancer-controller, cert-manager, ebs-csi, efs-csi, vpc-cni, aws-gateway-controller, cloudwatch-observability, velero, node-termination-handler, app-mesh, prometheus, mountpoint-s3, least-privilege, credential-management, pod-security, aws-sdk, daemon-set
- **Use For**: Kubernetes pod IAM authentication, least privilege access control for pods, secure AWS service access from EKS, credential isolation between containers, Kubernetes add-on IAM configuration, service account to IAM role mapping, cluster autoscaler permissions, external DNS IAM setup, load balancer controller authentication, CSI driver permissions, CloudWatch integration for EKS, Velero backup permissions, multi-tenant EKS security

## Description

This Terraform module provides comprehensive management of AWS EKS Pod Identity associations and IAM roles, enabling Kubernetes pods to securely access AWS services with fine-grained permissions. The module creates and manages IAM roles specifically designed for EKS Pod Identity, automatically configuring trust relationships and attaching appropriate policies for various AWS services and Kubernetes add-ons. It supports a wide range of pre-configured integrations including Cluster Autoscaler, External DNS, Load Balancer Controller, CSI drivers (EBS, EFS, Mountpoint S3), CloudWatch Observability, Velero, and many other popular Kubernetes tools.

AWS EKS Pod Identity is a modern credential management feature that allows associating IAM roles directly with Kubernetes service accounts in specific namespaces. This provides better security through credential isolation, improved auditability via CloudTrail logging, and simpler setup compared to traditional OIDC-based IRSA (IAM Roles for Service Accounts). The Pod Identity Agent runs as a DaemonSet on cluster nodes and injects temporary AWS credentials into pods based on their service account associations, ensuring each pod has only the permissions it needs.

The module offers flexible configuration options including custom policy attachments, trust policy conditions, support for multiple policy sources (inline statements, source documents, override documents), and the ability to manage multiple Pod Identity associations across different EKS clusters. It follows AWS best practices for least privilege access and provides a standardized approach to managing Kubernetes workload identities across EKS environments.

## Key Features

- **Pre-configured Policy Attachments**: Built-in support for 15+ AWS services and Kubernetes add-ons including VPC CNI, Cluster Autoscaler, External DNS, Load Balancer Controller, CSI drivers, and more
- **Custom Policy Support**: Attach custom IAM policies via inline policy statements, source policy documents, or override policy documents
- **Multiple Policy Attachments**: Support for attaching multiple additional IAM policy ARNs to a single role
- **Flexible Trust Policies**: Configure custom trust policy conditions and statements for advanced security requirements
- **Pod Identity Associations**: Manage multiple Pod Identity associations across different clusters, namespaces, and service accounts
- **Service-Specific Configurations**: Granular configuration options for each supported service (e.g., Route53 zones for External DNS, SSM parameters for External Secrets)
- **VPC CNI Integration**: Full support for AWS VPC CNI with optional CloudWatch logs, IPv4 and IPv6 addressing
- **Cluster Autoscaler**: Pre-configured IAM policies for Cluster Autoscaler with customizable cluster name patterns
- **External DNS**: Route53 integration with hosted zone ARN specification
- **Load Balancer Controller**: Complete IAM policy for AWS Load Balancer Controller
- **CSI Driver Support**: Pre-built policies for EBS CSI, EFS CSI, and Mountpoint S3 CSI drivers
- **CloudWatch Observability**: IAM permissions for CloudWatch Container Insights and log forwarding
- **Backup and Recovery**: Velero integration with S3 bucket ARN specification
- **Certificate Management**: Cert Manager integration with Route53 for DNS-01 challenges
- **Secrets Management**: External Secrets Operator support with SSM Parameter Store and Secrets Manager
- **App Mesh Integration**: AWS App Mesh Envoy proxy and controller policies
- **Prometheus Integration**: Amazon Managed Service for Prometheus permissions
- **Gateway Controller**: AWS Gateway Controller for Kubernetes Gateway API support
- **Node Termination Handler**: IAM policies for handling EC2 spot instance interruptions
- **Tagging Support**: Comprehensive tagging for all created IAM resources
- **Name Prefix Option**: Flexible naming with optional name prefixes for IAM roles and policies
- **Conditional Creation**: Control resource creation with a create flag
- **Association Defaults**: Define default values for all Pod Identity associations

## Main Use Cases

1. **Kubernetes Add-on IAM Configuration**: Configure IAM permissions for EKS cluster add-ons and controllers
2. **Least Privilege Pod Security**: Grant minimal required AWS permissions to individual pods or deployments
3. **Service Account Authentication**: Map Kubernetes service accounts to IAM roles for AWS SDK authentication
4. **Multi-tenant EKS Security**: Isolate credentials between different applications and namespaces
5. **CSI Driver Permissions**: Configure IAM for persistent volume provisioning via EBS, EFS, or S3 CSI drivers
6. **Ingress Controller Setup**: Provide Load Balancer Controller with permissions to manage ALBs and NLBs
7. **DNS Automation**: Enable External DNS to manage Route53 records for Kubernetes services
8. **Cluster Autoscaling**: Configure Cluster Autoscaler with permissions to modify Auto Scaling Groups
9. **Observability Integration**: Set up CloudWatch Container Insights and log forwarding from EKS
10. **Backup and Disaster Recovery**: Configure Velero for automated EKS backup and restore operations

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Determines whether resources will be created |
| `name` | `string` | `""` | Name of the IAM role |
| `use_name_prefix` | `bool` | `true` | Determines if role/policy names use prefix |
| `path` | `string` | `"/"` | Path of IAM role |
| `tags` | `map(string)` | `{}` | Tags to add to all resources |
| `attach_custom_policy` | `bool` | `false` | Whether to attach a custom IAM policy |
| `policy_statements` | `list(any)` | `[]` | List of IAM policy statements for inline policy |
| `source_policy_documents` | `list(string)` | `[]` | List of source policy documents to merge |
| `override_policy_documents` | `list(string)` | `[]` | List of override policy documents |
| `additional_policy_arns` | `map(string)` | `{}` | Map of additional IAM policy ARNs to attach |
| `trust_policy_conditions` | `list(any)` | `[]` | Conditions to add to role trust policy |
| `trust_policy_statements` | `any` | `null` | IAM policy statements for role trust policy |
| `attach_aws_vpc_cni_policy` | `bool` | `false` | Attach VPC CNI IAM policy |
| `attach_cluster_autoscaler_policy` | `bool` | `false` | Attach Cluster Autoscaler IAM policy |
| `attach_external_dns_policy` | `bool` | `false` | Attach External DNS IAM policy |
| `attach_load_balancer_controller_policy` | `bool` | `false` | Attach Load Balancer Controller IAM policy |
| `attach_cert_manager_policy` | `bool` | `false` | Attach Cert Manager IAM policy |
| `attach_ebs_csi_policy` | `bool` | `false` | Attach EBS CSI driver IAM policy |
| `attach_efs_csi_policy` | `bool` | `false` | Attach EFS CSI driver IAM policy |
| `attach_external_secrets_policy` | `bool` | `false` | Attach External Secrets Operator IAM policy |
| `attach_velero_policy` | `bool` | `false` | Attach Velero IAM policy |
| `attach_cloudwatch_observability_policy` | `bool` | `false` | Attach CloudWatch Observability IAM policy |
| `cluster_autoscaler_cluster_names` | `list(string)` | `[]` | List of cluster names for Cluster Autoscaler |
| `external_dns_hosted_zone_arns` | `list(string)` | `[]` | Route53 Hosted Zone ARNs for External DNS |
| `cert_manager_hosted_zone_arns` | `list(string)` | `[]` | Route53 Hosted Zone ARNs for Cert Manager |
| `external_secrets_ssm_parameter_arns` | `list(string)` | `["arn:aws:ssm:*:*:parameter/*"]` | SSM Parameter ARNs for External Secrets |
| `external_secrets_secrets_manager_arns` | `list(string)` | `["arn:aws:secretsmanager:*:*:secret:*"]` | Secrets Manager ARNs for External Secrets |
| `velero_s3_bucket_arns` | `list(string)` | `[]` | S3 bucket ARNs for Velero |
| `associations` | `any` | `{}` | Map of Pod Identity associations to create |
| `association_defaults` | `any` | `{}` | Default values for Pod Identity associations |

## Main Outputs

| Output | Description |
|--------|-------------|
| `iam_role_arn` | ARN of the IAM role |
| `iam_role_name` | Name of the IAM role |
| `iam_role_path` | Path of the IAM role |
| `iam_role_unique_id` | Unique ID of the IAM role |
| `iam_policy_arn` | ARN of the IAM policy |
| `iam_policy_name` | Name of the IAM policy |
| `iam_policy_id` | ID of the IAM policy |
| `associations` | Map of Pod Identity associations created |

## Usage Examples

### Example 1: Cluster Autoscaler

```hcl
module "cluster_autoscaler_pod_identity" {
  source = "terraform-aws-modules/eks-pod-identity/aws"

  name = "cluster-autoscaler"

  attach_cluster_autoscaler_policy    = true
  cluster_autoscaler_cluster_names    = ["my-eks-cluster"]

  # Create Pod Identity association
  associations = {
    cluster_autoscaler = {
      cluster_name    = "my-eks-cluster"
      namespace       = "kube-system"
      service_account = "cluster-autoscaler"
    }
  }

  tags = {
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}
```

### Example 2: External DNS with Route53

```hcl
module "external_dns_pod_identity" {
  source = "terraform-aws-modules/eks-pod-identity/aws"

  name = "external-dns"

  attach_external_dns_policy   = true
  external_dns_hosted_zone_arns = [
    "arn:aws:route53:::hostedzone/Z1234567890ABC",
    "arn:aws:route53:::hostedzone/Z0987654321XYZ"
  ]

  associations = {
    external_dns = {
      cluster_name    = "my-eks-cluster"
      namespace       = "external-dns"
      service_account = "external-dns"
    }
  }

  tags = {
    Application = "external-dns"
  }
}
```

### Example 3: AWS Load Balancer Controller

```hcl
module "load_balancer_controller_pod_identity" {
  source = "terraform-aws-modules/eks-pod-identity/aws"

  name = "aws-load-balancer-controller"

  attach_load_balancer_controller_policy = true

  associations = {
    alb_controller = {
      cluster_name    = "my-eks-cluster"
      namespace       = "kube-system"
      service_account = "aws-load-balancer-controller"
    }
  }

  tags = {
    Component = "ingress-controller"
  }
}
```

### Example 4: EBS CSI Driver

```hcl
module "ebs_csi_pod_identity" {
  source = "terraform-aws-modules/eks-pod-identity/aws"

  name = "ebs-csi-controller"

  attach_ebs_csi_policy = true

  associations = {
    ebs_csi = {
      cluster_name    = "my-eks-cluster"
      namespace       = "kube-system"
      service_account = "ebs-csi-controller-sa"
    }
  }

  tags = {
    Component = "storage"
  }
}
```

### Example 5: Cert Manager with Route53

```hcl
module "cert_manager_pod_identity" {
  source = "terraform-aws-modules/eks-pod-identity/aws"

  name = "cert-manager"

  attach_cert_manager_policy     = true
  cert_manager_hosted_zone_arns  = ["arn:aws:route53:::hostedzone/Z1234567890ABC"]

  associations = {
    cert_manager = {
      cluster_name    = "my-eks-cluster"
      namespace       = "cert-manager"
      service_account = "cert-manager"
    }
  }

  tags = {
    Application = "cert-manager"
  }
}
```

### Example 6: External Secrets Operator

```hcl
module "external_secrets_pod_identity" {
  source = "terraform-aws-modules/eks-pod-identity/aws"

  name = "external-secrets"

  attach_external_secrets_policy = true
  external_secrets_ssm_parameter_arns = [
    "arn:aws:ssm:us-east-1:123456789012:parameter/myapp/*"
  ]
  external_secrets_secrets_manager_arns = [
    "arn:aws:secretsmanager:us-east-1:123456789012:secret:myapp/*"
  ]

  associations = {
    external_secrets = {
      cluster_name    = "my-eks-cluster"
      namespace       = "external-secrets"
      service_account = "external-secrets"
    }
  }

  tags = {
    Application = "external-secrets"
  }
}
```

### Example 7: Custom Policy with Multiple Associations

```hcl
module "custom_pod_identity" {
  source = "terraform-aws-modules/eks-pod-identity/aws"

  name = "custom-app"

  attach_custom_policy = true
  policy_statements = [
    {
      sid = "S3Access"
      actions = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ]
      resources = [
        "arn:aws:s3:::my-app-bucket",
        "arn:aws:s3:::my-app-bucket/*"
      ]
    },
    {
      sid = "DynamoDBAccess"
      actions = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query"
      ]
      resources = [
        "arn:aws:dynamodb:us-east-1:123456789012:table/my-app-table"
      ]
    }
  ]

  # Associate with multiple clusters
  associations = {
    prod_cluster = {
      cluster_name    = "prod-eks-cluster"
      namespace       = "my-app"
      service_account = "my-app-sa"
    }
    staging_cluster = {
      cluster_name    = "staging-eks-cluster"
      namespace       = "my-app"
      service_account = "my-app-sa"
    }
  }

  tags = {
    Application = "my-app"
    Environment = "multi-cluster"
  }
}
```

### Example 8: Velero for Backup and Restore

```hcl
module "velero_pod_identity" {
  source = "terraform-aws-modules/eks-pod-identity/aws"

  name = "velero"

  attach_velero_policy = true
  velero_s3_bucket_arns = [
    "arn:aws:s3:::eks-backup-bucket",
    "arn:aws:s3:::eks-backup-bucket/*"
  ]

  associations = {
    velero = {
      cluster_name    = "my-eks-cluster"
      namespace       = "velero"
      service_account = "velero"
    }
  }

  tags = {
    Component = "backup"
  }
}
```

## Best Practices

### Security and Access Control

1. **Apply Least Privilege Principle**: Grant only the minimum permissions required for each pod's specific function. Use service-specific policy attachments instead of overly broad custom policies.
2. **Use Scoped Resource ARNs**: When configuring policies for services like External DNS or Velero, specify exact Route53 zone ARNs or S3 bucket ARNs rather than using wildcards.
3. **Implement Trust Policy Conditions**: Add conditions to trust policies (e.g., `aws:PrincipalOrgID`) to restrict which entities can assume the role.
4. **Separate Roles by Function**: Create individual IAM roles for each Kubernetes workload or add-on rather than sharing roles across multiple services.
5. **Enable CloudTrail Logging**: Monitor IAM role usage and API calls made by pods through CloudTrail for audit and security analysis.
6. **Avoid Wildcard Permissions**: Minimize use of `*` in IAM policy actions and resources; specify exact actions and ARNs when possible.
7. **Regular Permission Audits**: Periodically review and update IAM policies to remove unused permissions and ensure alignment with current requirements.

### Configuration and Deployment

1. **Use Name Prefixes**: Enable `use_name_prefix = true` to avoid naming conflicts and support easier updates to IAM resources.
2. **Implement Consistent Tagging**: Apply comprehensive tags including Environment, Application, ManagedBy, and Component for resource tracking and cost allocation.
3. **Version Pin the Module**: Specify an exact module version in production to ensure consistent deployments and controlled updates.
4. **Validate Before Production**: Test Pod Identity configurations in non-production environments before applying to production clusters.
5. **Document Custom Policies**: When using custom policy statements, include inline comments explaining the purpose and required resources.
6. **Use Association Defaults**: Define `association_defaults` for common configuration across multiple Pod Identity associations to reduce duplication.

### Operational Excellence

1. **Monitor Pod Identity Agent**: Ensure the EKS Pod Identity Agent DaemonSet is running healthy on all nodes; check logs if pods fail to authenticate.
2. **Handle Eventual Consistency**: Account for potential delays in Pod Identity association propagation; implement retry logic in applications if needed.
3. **Test Credential Access**: After creating associations, verify pods can successfully obtain credentials by checking environment variables and testing AWS SDK calls.
4. **Plan for Association Limits**: Be aware of the 5,000 Pod Identity association limit per cluster; consolidate roles where appropriate for large clusters.
5. **Configure Proxy Settings**: If using HTTP proxies, ensure proxy environment variables don't interfere with Pod Identity Agent communication.
6. **Implement Health Checks**: Add readiness probes that verify AWS credential availability before marking pods as ready.

### Service-Specific Best Practices

1. **Cluster Autoscaler Configuration**: Specify exact cluster names in `cluster_autoscaler_cluster_names` to prevent cross-cluster permission issues.
2. **External DNS Zone Restrictions**: Limit `external_dns_hosted_zone_arns` to only zones the service should manage to prevent unauthorized DNS modifications.
3. **CSI Driver Separation**: Use separate IAM roles for EBS CSI, EFS CSI, and Mountpoint S3 CSI drivers to maintain permission boundaries.
4. **VPC CNI CloudWatch Logs**: Enable `aws_vpc_cni_enable_cloudwatch_logs` only when actively monitoring CNI logs to avoid unnecessary CloudWatch costs.
5. **External Secrets Scoping**: Use specific path prefixes in `external_secrets_ssm_parameter_arns` to limit secret access to required paths only.
6. **Load Balancer Controller Permissions**: Review the pre-built Load Balancer Controller policy regularly as AWS adds new features requiring additional permissions.

### High Availability and Disaster Recovery

1. **Multi-Cluster Associations**: For critical workloads, create Pod Identity associations across multiple clusters using the same IAM role for consistency.
2. **Backup IAM Configurations**: Store Terraform state in version-controlled, backed-up remote state (S3 with versioning) to recover IAM configurations.
3. **Plan for Region Failures**: Ensure IAM roles are global resources; Pod Identity associations can be quickly recreated in different regions if needed.
4. **Test Failover Scenarios**: Regularly test that applications can authenticate and access AWS services after cluster failover or disaster recovery events.

### Cost Optimization

1. **Consolidate When Appropriate**: For non-production environments, consider sharing IAM roles across similar workloads to reduce IAM entity count and management overhead.
2. **Remove Unused Associations**: Regularly audit and remove Pod Identity associations for deleted or unused Kubernetes service accounts.
3. **Optimize Policy Complexity**: Simpler IAM policies with fewer statements reduce policy evaluation time and potential performance impact.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-eks-pod-identity
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eks-pod-identity/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-eks-pod-identity/tree/master/examples
- **AWS EKS Pod Identity Documentation**: https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html
- **AWS EKS Pod Identity Agent**: https://docs.aws.amazon.com/eks/latest/userguide/pod-id-agent-setup.html
- **AWS EKS User Guide**: https://docs.aws.amazon.com/eks/latest/userguide/
- **IAM Roles for Service Accounts (IRSA)**: https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
- **Kubernetes Service Accounts**: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
- **AWS IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **EKS Best Practices Guide**: https://aws.github.io/aws-eks-best-practices/
- **AWS Security Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **Cluster Autoscaler on AWS**: https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/README.md
- **External DNS Documentation**: https://kubernetes-sigs.github.io/external-dns/
- **AWS Load Balancer Controller**: https://kubernetes-sigs.github.io/aws-load-balancer-controller/
- **EBS CSI Driver**: https://github.com/kubernetes-sigs/aws-ebs-csi-driver
- **EFS CSI Driver**: https://github.com/kubernetes-sigs/aws-efs-csi-driver
- **External Secrets Operator**: https://external-secrets.io/

## Notes for AI Agents

When using this module in automated workflows:

1. **Security First**: Always apply least privilege principle when configuring IAM policies
2. **Use Pre-built Policies**: Leverage service-specific policy attachments (e.g., `attach_cluster_autoscaler_policy`) instead of creating custom policies when possible
3. **Verify Cluster Support**: Ensure EKS clusters are on supported versions and have the Pod Identity Agent installed
4. **Test Associations**: After creating Pod Identity associations, verify pods can successfully authenticate by checking AWS SDK credential resolution
5. **Scope Resources**: Always specify exact resource ARNs (hosted zones, S3 buckets, parameter paths) rather than using wildcards
6. **Tag Consistently**: Apply comprehensive tags including Environment, Application, Component, and ManagedBy for resource tracking
7. **Monitor Limits**: Track the number of Pod Identity associations per cluster (max 5,000) and consolidate roles if approaching limits
8. **Handle Eventual Consistency**: Implement retry logic in applications to handle potential delays in association propagation
9. **Separate Production Roles**: Use distinct IAM roles for production and non-production environments to maintain security boundaries
10. **Enable Audit Logging**: Ensure CloudTrail is enabled to track IAM role usage and API calls from pods
11. **Version Control**: Pin module versions in production and test updates in non-production environments first
12. **Document Custom Policies**: When creating custom policy statements, include clear comments explaining required permissions and resources
13. **Review Service Updates**: Regularly check for updates to pre-built service policies as AWS services add new features
14. **Plan for Multi-Cluster**: Design IAM roles to support Pod Identity associations across multiple clusters when needed for high availability
15. **Validate Permissions**: Use IAM policy simulator or actual testing to validate policies grant required permissions without over-privileging
