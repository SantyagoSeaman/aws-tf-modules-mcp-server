# Terraform AWS EKS Pod Identity Module

## Module Information

- **Module Name**: `eks-pod-identity`
- **Source**: `terraform-aws-modules/eks-pod-identity/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-eks-pod-identity
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eks-pod-identity/aws/latest
- **Latest Version**: 2.7.0
- **Purpose**: Terraform module that creates IAM roles and Pod Identity associations for Amazon EKS clusters, enabling fine-grained IAM permissions for Kubernetes pods
- **Service**: AWS EKS (Elastic Kubernetes Service)
- **Category**: Container Orchestration, Security, Identity and Access Management
- **Keywords**: eks, pod-identity, iam, kubernetes, service-account, cluster-autoscaler, external-dns, load-balancer-controller, ebs-csi, efs-csi, vpc-cni, velero, external-secrets, cert-manager, cloudwatch-observability
- **Use For**: Kubernetes pod IAM authentication, least privilege access control for pods, secure AWS service access from EKS, credential isolation between containers, Kubernetes add-on IAM configuration, service account to IAM role mapping, cluster autoscaler permissions, external DNS IAM setup, load balancer controller authentication, CSI driver permissions, CloudWatch integration for EKS, Velero backup permissions, multi-tenant EKS security

## Description

This Terraform module provides comprehensive management of AWS EKS Pod Identity associations and IAM roles, enabling Kubernetes pods to securely access AWS services with fine-grained permissions. The module creates and manages IAM roles specifically designed for EKS Pod Identity, automatically configuring trust relationships and attaching appropriate policies for various AWS services and Kubernetes add-ons. It provides 20+ pre-built IAM policies for common controllers including Cluster Autoscaler, External DNS, AWS Load Balancer Controller, CSI drivers (EBS, EFS, FSx Lustre, Mountpoint S3), CloudWatch Observability, Velero, External Secrets, cert-manager, AWS VPC CNI, App Mesh, Gateway Controller, Node Termination Handler, and Amazon Managed Prometheus.

AWS EKS Pod Identity is a modern credential management feature that allows associating IAM roles directly with Kubernetes service accounts in specific namespaces. This provides better security through credential isolation, improved auditability via CloudTrail logging, and simpler setup compared to traditional OIDC-based IRSA (IAM Roles for Service Accounts). The Pod Identity Agent runs as a DaemonSet on cluster nodes and injects temporary AWS credentials into pods based on their service account associations, ensuring each pod has only the permissions it needs.

The module offers flexible configuration options including custom policy attachments, trust policy conditions with organization-based constraints, support for multiple policy sources (inline statements, source documents, override documents), and the ability to manage multiple Pod Identity associations across different EKS clusters via the `associations` map with shared `association_defaults`. It follows AWS best practices for least privilege access with resource-specific ARN filtering for S3 buckets, Route53 zones, KMS keys, and other AWS resources.

## Key Features

- **20+ Pre-built IAM Policies**: Ready-to-use policies for common Kubernetes controllers and AWS service integrations
- **Multi-Cluster Support**: Configure the same IAM role across multiple EKS clusters via the `associations` map
- **Association Defaults**: Use `association_defaults` to share namespace/service account across clusters, reducing duplication
- **Least-Privilege Scoping**: Resource-specific ARN filtering for S3 buckets, Route53 zones, KMS keys, and other resources
- **Trust Policy Customization**: Add organization-based constraints and custom conditions to trust policies
- **Custom Policy Support**: Attach custom policies via inline statements, source documents, or override documents
- **Storage CSI Drivers**: EBS CSI, EFS CSI, FSx Lustre CSI, Mountpoint S3 CSI with KMS encryption support
- **Load Balancing**: AWS Load Balancer Controller with full or TargetGroupBinding-only permission modes
- **DNS & Certificates**: External DNS and cert-manager with Route53 hosted zone scoping
- **Networking**: AWS VPC CNI (IPv4/IPv6), App Mesh (Controller & Envoy Proxy), Gateway Controller
- **Observability**: CloudWatch Observability, Amazon Managed Service for Prometheus, PGAnalyze
- **Secrets Management**: External Secrets with SSM, Secrets Manager, and KMS integration
- **Backup & DR**: Velero with S3 bucket and KMS key scoping
- **Node Management**: AWS Node Termination Handler for spot instance interruptions
- **Security**: AWS Private CA Issuer, permissions boundaries support
- **Scaling**: Cluster Autoscaler with cluster name scoping

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

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether resources will be created |
| `name` | `string` | `""` | IAM role name |
| `use_name_prefix` | `bool` | `true` | Use name as prefix instead of exact name |
| `path` | `string` | `"/"` | IAM role path |
| `description` | `string` | `null` | IAM role description |
| `max_session_duration` | `number` | `null` | CLI/API session duration (3600-43200 seconds) |
| `permissions_boundary_arn` | `string` | `null` | Permissions boundary ARN |
| `tags` | `map(string)` | `{}` | Tags to apply to all resources |

### Pod Identity Associations

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `associations` | `map(object)` | `{}` | Map of Pod Identity associations (cluster → namespace/service account) |
| `association_defaults` | `object` | `{}` | Default values for all associations |

**Association object structure**:
```hcl
associations = {
  my-cluster = {
    cluster_name    = "my-eks-cluster"
    namespace       = "kube-system"
    service_account = "my-service-account"
  }
}
```

### Custom Policy Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `attach_custom_policy` | `bool` | `false` | Attach custom IAM policy to role |
| `policy_statements` | `list(object)` | `null` | IAM policy statements for custom permissions |
| `policy_name_prefix` | `string` | `"AmazonEKS_"` | Prefix for IAM policy names |
| `source_policy_documents` | `list(string)` | `[]` | Policy documents to merge together |
| `override_policy_documents` | `list(string)` | `[]` | Policy documents that override merged policies |
| `additional_policy_arns` | `map(string)` | `{}` | ARNs of additional policies to attach |

### Trust Policy Customization

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `trust_policy_statements` | `list(object)` | `null` | Custom trust policy statements |
| `trust_policy_conditions` | `list(object)` | `[]` | Trust policy conditions (e.g., organization restrictions) |

### Service-Specific Policy Attachments

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `attach_aws_ebs_csi_policy` | `bool` | `false` | Attach EBS CSI driver policy |
| `aws_ebs_csi_kms_arns` | `list(string)` | `[]` | KMS key ARNs for EBS encryption |
| `attach_aws_efs_csi_policy` | `bool` | `false` | Attach EFS CSI driver policy |
| `attach_aws_fsx_lustre_csi_policy` | `bool` | `false` | Attach FSx Lustre CSI driver policy |
| `attach_mountpoint_s3_csi_policy` | `bool` | `false` | Attach Mountpoint S3 CSI driver policy |
| `mountpoint_s3_csi_bucket_arns` | `list(string)` | `[]` | S3 bucket ARNs for Mountpoint |
| `mountpoint_s3_csi_bucket_path_arns` | `list(string)` | `[]` | S3 bucket path ARNs for Mountpoint |
| `attach_aws_lb_controller_policy` | `bool` | `false` | Attach Load Balancer Controller policy |
| `attach_aws_lb_controller_targetgroup_binding_only_policy` | `bool` | `false` | Attach minimal TargetGroupBinding-only policy |
| `attach_external_dns_policy` | `bool` | `false` | Attach External DNS policy |
| `external_dns_hosted_zone_arns` | `list(string)` | `[]` | Route53 hosted zone ARNs |
| `attach_cert_manager_policy` | `bool` | `false` | Attach cert-manager policy |
| `cert_manager_hosted_zone_arns` | `list(string)` | `[]` | Route53 hosted zone ARNs for DNS-01 |
| `attach_cluster_autoscaler_policy` | `bool` | `false` | Attach Cluster Autoscaler policy |
| `cluster_autoscaler_cluster_names` | `list(string)` | `[]` | Cluster names for ASG scoping |
| `attach_aws_vpc_cni_policy` | `bool` | `false` | Attach VPC CNI policy |
| `aws_vpc_cni_enable_ipv4` | `bool` | `false` | Enable IPv4 CNI permissions |
| `aws_vpc_cni_enable_ipv6` | `bool` | `false` | Enable IPv6 CNI permissions |
| `aws_vpc_cni_enable_cloudwatch_logs` | `bool` | `false` | Enable CloudWatch logs for CNI |
| `attach_external_secrets_policy` | `bool` | `false` | Attach External Secrets policy |
| `external_secrets_ssm_parameter_arns` | `list(string)` | `[]` | SSM parameter ARNs |
| `external_secrets_secrets_manager_arns` | `list(string)` | `[]` | Secrets Manager ARNs |
| `external_secrets_kms_key_arns` | `list(string)` | `[]` | KMS key ARNs for decryption |
| `external_secrets_create_permission` | `bool` | `false` | Allow creating/deleting secrets |
| `attach_velero_policy` | `bool` | `false` | Attach Velero backup policy |
| `velero_s3_bucket_arns` | `list(string)` | `[]` | S3 bucket ARNs for Velero |
| `velero_s3_bucket_path_arns` | `list(string)` | `[]` | S3 bucket path ARNs for Velero |
| `velero_kms_arns` | `list(string)` | `[]` | KMS key ARNs for Velero |
| `attach_cloudwatch_observability_policy` | `bool` | `false` | Attach CloudWatch Observability policy |
| `attach_aws_appmesh_controller_policy` | `bool` | `false` | Attach App Mesh Controller policy |
| `attach_aws_appmesh_envoy_proxy_policy` | `bool` | `false` | Attach App Mesh Envoy Proxy policy |
| `attach_aws_gateway_controller_policy` | `bool` | `false` | Attach Gateway Controller policy |
| `attach_aws_privateca_issuer_policy` | `bool` | `false` | Attach Private CA Issuer policy |
| `attach_node_termination_handler_policy` | `bool` | `false` | Attach Node Termination Handler policy |
| `attach_amazon_managed_service_prometheus_policy` | `bool` | `false` | Attach AMP policy |

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

### Example 1: EBS CSI Driver with KMS Encryption

```hcl
module "ebs_csi_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.7"

  name = "ebs-csi"

  attach_aws_ebs_csi_policy = true
  aws_ebs_csi_kms_arns      = ["arn:aws:kms:us-west-2:123456789012:key/abcd1234-..."]

  associations = {
    my-cluster = {
      cluster_name    = "my-eks-cluster"
      namespace       = "kube-system"
      service_account = "ebs-csi-controller-sa"
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 2: Multi-Cluster External DNS with Association Defaults

```hcl
module "external_dns_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.7"

  name = "external-dns"

  attach_external_dns_policy = true
  external_dns_hosted_zone_arns = [
    "arn:aws:route53:::hostedzone/Z1234567890ABC"
  ]

  # Shared defaults across clusters
  association_defaults = {
    namespace       = "external-dns"
    service_account = "external-dns"
  }

  # Multiple cluster associations
  associations = {
    prod-us-east-1 = {
      cluster_name = "prod-cluster-us-east-1"
    }
    prod-us-west-2 = {
      cluster_name = "prod-cluster-us-west-2"
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
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.7"

  name = "aws-load-balancer-controller"

  attach_aws_lb_controller_policy = true

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

### Example 4: Cluster Autoscaler with Cluster Name Scoping

```hcl
module "cluster_autoscaler_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.7"

  name = "cluster-autoscaler"

  attach_cluster_autoscaler_policy = true
  cluster_autoscaler_cluster_names = ["my-eks-cluster"]

  associations = {
    cluster_autoscaler = {
      cluster_name    = "my-eks-cluster"
      namespace       = "kube-system"
      service_account = "cluster-autoscaler"
    }
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 5: External Secrets with KMS Integration

```hcl
module "external_secrets_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.7"

  name = "external-secrets"

  attach_external_secrets_policy = true
  external_secrets_ssm_parameter_arns = [
    "arn:aws:ssm:us-east-1:123456789012:parameter/myapp/*"
  ]
  external_secrets_secrets_manager_arns = [
    "arn:aws:secretsmanager:us-east-1:123456789012:secret:myapp/*"
  ]
  external_secrets_kms_key_arns = [
    "arn:aws:kms:us-east-1:123456789012:key/abcd1234-..."
  ]
  external_secrets_create_permission = false  # Read-only access

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

### Example 6: Custom Policy with Organization Trust Constraint

```hcl
module "custom_app_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.7"

  name = "custom-app"

  attach_custom_policy = true
  policy_statements = [
    {
      sid    = "AllowS3Access"
      effect = "Allow"
      actions = [
        "s3:GetObject",
        "s3:PutObject"
      ]
      resources = ["arn:aws:s3:::my-app-bucket/*"]
    },
    {
      sid    = "AllowDynamoDB"
      effect = "Allow"
      actions = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query"
      ]
      resources = ["arn:aws:dynamodb:us-east-1:123456789012:table/my-app-table"]
    }
  ]

  # Organization-based trust policy constraint
  trust_policy_conditions = [
    {
      test     = "StringEquals"
      variable = "aws:PrincipalOrgID"
      values   = ["o-1234567890"]
    }
  ]

  associations = {
    my-cluster = {
      cluster_name    = "my-cluster"
      namespace       = "my-app"
      service_account = "my-app-sa"
    }
  }

  tags = {
    Application = "my-app"
  }
}
```

### Example 7: Velero Backup with S3 and KMS

```hcl
module "velero_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.7"

  name = "velero"

  attach_velero_policy = true
  velero_s3_bucket_arns = [
    "arn:aws:s3:::eks-backup-bucket"
  ]
  velero_s3_bucket_path_arns = [
    "arn:aws:s3:::eks-backup-bucket/*"
  ]
  velero_kms_arns = [
    "arn:aws:kms:us-east-1:123456789012:key/abcd1234-..."
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

### Example 8: VPC CNI with IPv4 and CloudWatch Logs

```hcl
module "vpc_cni_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.7"

  name = "vpc-cni"

  attach_aws_vpc_cni_policy        = true
  aws_vpc_cni_enable_ipv4          = true
  aws_vpc_cni_enable_cloudwatch_logs = true

  associations = {
    vpc_cni = {
      cluster_name    = "my-eks-cluster"
      namespace       = "kube-system"
      service_account = "aws-node"
    }
  }

  tags = {
    Component = "networking"
  }
}
```

## Best Practices

### Security

1. **Apply Least Privilege**: Use service-specific policy attachments (`attach_aws_ebs_csi_policy`, etc.) instead of overly broad custom policies.
2. **Scope Resource ARNs**: Always specify exact ARNs for Route53 zones, S3 buckets, KMS keys instead of wildcards.
3. **Use Trust Policy Conditions**: Add `trust_policy_conditions` with `aws:PrincipalOrgID` to restrict role assumption.
4. **KMS Key Requirements**: Always provide `*_kms_arns` when using encrypted volumes with EBS/EFS/S3 CSI drivers.
5. **External Secrets Read-Only**: Set `external_secrets_create_permission = false` unless workloads explicitly need to create/delete secrets.
6. **Separate Roles by Function**: Create individual IAM roles for each controller rather than sharing across services.

### Configuration

1. **Use Association Defaults**: Define `association_defaults` for shared namespace/service account when deploying across multiple clusters.
2. **Version Pin Module**: Use `version = "~> 2.7"` to ensure consistent deployments.
3. **Name Prefixes**: Keep `use_name_prefix = true` (default) to allow multiple deployments across regions/environments.
4. **Consistent Tagging**: Apply Environment, Application, Component tags for resource tracking.
5. **Cluster Name Scoping**: Always specify `cluster_autoscaler_cluster_names` to restrict ASG permissions.
6. **IPv4 vs IPv6**: Enable only the IP version(s) your cluster uses via `aws_vpc_cni_enable_ipv4`/`aws_vpc_cni_enable_ipv6`.

### Operational

1. **Verify Associations**: After deployment, run `aws eks list-pod-identity-associations --cluster-name <cluster>`.
2. **Handle Eventual Consistency**: Implement retry logic in applications for potential delays in association propagation.
3. **Service Account Timing**: EKS Pod Identity associations can be created before Kubernetes service accounts exist (safe).
4. **Path ARNs Required**: For S3-based services (Mountpoint S3 CSI, Velero), both `*_bucket_arns` and `*_bucket_path_arns` must be specified.
5. **Route53 Zone ARN Format**: Use `arn:aws:route53:::hostedzone/<ZONE_ID>` (note the triple colon `:::`).
6. **TargetGroupBinding-Only Mode**: Use `attach_aws_lb_controller_targetgroup_binding_only_policy` for minimal LB Controller permissions.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-eks-pod-identity
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eks-pod-identity/aws/latest
- **Complete Example**: https://github.com/terraform-aws-modules/terraform-aws-eks-pod-identity/tree/master/examples/complete
- **AWS EKS Pod Identity Documentation**: https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html
- **AWS EKS Pod Identity Agent Setup**: https://docs.aws.amazon.com/eks/latest/userguide/pod-id-agent-setup.html
- **EKS Best Practices Guide**: https://aws.github.io/aws-eks-best-practices/
- **AWS Load Balancer Controller**: https://kubernetes-sigs.github.io/aws-load-balancer-controller/
- **External Secrets Operator**: https://external-secrets.io/

## Notes for AI Agents

When generating Terraform code with this module:

1. **Use Pre-built Policies**: Prefer `attach_*_policy` booleans over custom policies when available (20+ services supported)
2. **Always Specify Resource ARNs**: For S3, Route53, KMS - never use wildcards, always provide exact ARNs
3. **KMS for Encrypted Volumes**: EBS CSI with encrypted volumes **requires** `aws_ebs_csi_kms_arns`
4. **S3 Path ARNs Required**: For Mountpoint S3 CSI and Velero, both `*_bucket_arns` and `*_bucket_path_arns` are required
5. **Association Object Structure**: Each association needs `cluster_name`, `namespace`, `service_account`
6. **Use Association Defaults**: When deploying to multiple clusters, use `association_defaults` for shared namespace/service_account
7. **Route53 Zone ARN Format**: Use `arn:aws:route53:::hostedzone/<ZONE_ID>` (triple colon `:::`)
8. **Version Pinning**: Always include `version = "~> 2.7"` in module source
9. **Cluster Name Scoping**: Always specify `cluster_autoscaler_cluster_names` for Cluster Autoscaler
10. **External Secrets Read-Only**: Default `external_secrets_create_permission = false` is correct for most cases
