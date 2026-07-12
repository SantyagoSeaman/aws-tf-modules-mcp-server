# Terraform AWS EKS Pod Identity Module

## Module Information

- **Module Name**: `eks-pod-identity`
- **Module ID**: `terraform-aws-modules/eks-pod-identity/aws`
- **Source**: `terraform-aws-modules/eks-pod-identity/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-eks-pod-identity
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eks-pod-identity/aws/latest
- **Latest Version**: 2.8.1 (Terraform >= 1.5.7, AWS provider >= 6.28)
- **Purpose**: Terraform module that creates an IAM role plus one or more `aws_eks_pod_identity_association` resources, so Kubernetes service accounts can assume the role via AWS EKS Pod Identity
- **Service**: AWS EKS (Elastic Kubernetes Service) - Pod Identity
- **Category**: Container Orchestration, Security, Identity and Access Management
- **Keywords**: eks, pod-identity, iam-role, kubernetes, service-account, irsa-alternative, cluster-autoscaler, external-dns, load-balancer-controller, ebs-csi, efs-csi, vpc-cni, velero, external-secrets, cert-manager, cloudwatch-observability
- **Use For**: Kubernetes pod IAM authentication, least-privilege access control for pods, secure AWS service access from EKS, credential isolation between namespaces, EKS add-on/controller IAM setup (Load Balancer Controller, External DNS, CSI drivers), cluster autoscaler permissions, CloudWatch/Prometheus observability roles, Velero backup permissions, cross-account access via role chaining, multi-cluster IAM role reuse

## Description

This module manages a single IAM role plus one or more AWS EKS Pod Identity associations, allowing Kubernetes service accounts to obtain temporary, automatically-rotated AWS credentials without configuring an OIDC identity provider. It replaces the older IRSA (IAM Roles for Service Accounts) pattern with a simpler mechanism: the EKS Pod Identity Agent (a DaemonSet running on cluster nodes) injects credentials into pods based on their namespace/service-account association, and the same IAM role can be reused across multiple clusters via the `associations` map.

The module ships with 20 pre-built, parameterized IAM policies for the most common EKS controllers and add-ons - Cluster Autoscaler, External DNS, cert-manager, AWS Load Balancer Controller (full and TargetGroupBinding-only variants), CSI drivers (EBS, EFS, FSx for Lustre, Mountpoint S3), AWS VPC CNI (IPv4/IPv6), CloudWatch Observability, Amazon Managed Prometheus, Velero, External Secrets, App Mesh (Controller and Envoy Proxy), Gateway Controller, Node Termination Handler, Private CA Issuer, and PGAnalyze. Each policy is toggled with an `attach_<service>_policy` boolean and scoped with service-specific ARN inputs (S3 buckets, Route53 zones, KMS keys, SQS queues, ACM PCA authorities, etc.), so no wildcard resource access is required by default.

Beyond the built-in policies, the module supports fully custom IAM permissions via `policy_statements`, `source_policy_documents`, and `override_policy_documents`, custom trust-policy statements/conditions (e.g. restrict `sts:AssumeRole` to a specific AWS Organization), and per-association overrides for role chaining (`target_role_arn`), disabling automatic session tags, or assigning association-level tags. It follows AWS Well-Architected security guidance by defaulting every `attach_*_policy` flag to `false` and requiring explicit, resource-scoped ARNs wherever permissions are granted.

## Key Features

- **20 Pre-built IAM Policies**: One flag each (`attach_<service>_policy`) for common Kubernetes controllers and AWS integrations - no policy JSON to write
- **Multi-Cluster Role Reuse**: The `associations` map lets one IAM role be associated with service accounts across many EKS clusters
- **Association Defaults**: `association_defaults` shares namespace/service_account/tags across associations to avoid repetition
- **Least-Privilege Scoping**: Dedicated `*_arns` variables scope permissions to specific S3 buckets, Route53 zones, KMS keys, SQS queues, ACM PCA authorities, target groups, and AMP workspaces
- **Role Chaining & Cross-Account**: Per-association `target_role_arn` chains to a second IAM role (e.g. in another account); `disable_session_tags` and `role_arn` are also overridable per association
- **Trust Policy Customization**: `trust_policy_conditions` and `trust_policy_statements` restrict or extend who can assume the role (e.g. `aws:PrincipalOrgID`)
- **Custom Policy Support**: Attach fully custom permissions via `policy_statements`, `source_policy_documents`, or `override_policy_documents`, combinable with the built-in policies
- **Custom Policy/Role Naming**: `policy_name_prefix`, `use_name_prefix`, and per-service `*_policy_name` overrides for predictable resource names
- **Regional Resources**: Optional `region` input to manage the role/associations in a Region other than the provider default

## Main Use Cases

1. **Kubernetes Add-on IAM Configuration**: Grant IAM permissions to EKS add-ons and controllers without OIDC setup
2. **Least Privilege Pod Security**: Give individual pods/deployments only the AWS permissions they need
3. **Service Account Authentication**: Map Kubernetes service accounts to IAM roles for AWS SDK/CLI credentials
4. **Multi-Cluster / Multi-Tenant Security**: Reuse one role across clusters, or isolate credentials per namespace
5. **CSI Driver Permissions**: Configure IAM for persistent volumes via EBS, EFS, FSx Lustre, or Mountpoint S3 CSI
6. **Ingress Controller Setup**: Give the Load Balancer Controller permissions to manage ALBs/NLBs/target groups
7. **DNS & Certificate Automation**: Let External DNS and cert-manager manage Route53 records for DNS-01 challenges
8. **Cluster Autoscaling**: Grant Cluster Autoscaler permission to modify specific Auto Scaling Groups
9. **Observability Integration**: Set up CloudWatch Container Insights or Amazon Managed Prometheus ingestion
10. **Backup, DR & Cross-Account Access**: Configure Velero backups or role-chain into another account's IAM role

## Main Input Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls whether resources will be created |
| `name` | `string` | `""` | IAM role name |
| `use_name_prefix` | `string`/`bool` | `true` | Use `name` as a prefix instead of the exact name for role and policies |
| `path` | `string` | `"/"` | IAM role path |
| `description` | `string` | `null` | IAM role description |
| `max_session_duration` | `number` | `null` | CLI/API session duration (3600-43200 seconds) |
| `permissions_boundary_arn` | `string` | `null` | Permissions boundary ARN attached to the IAM role |
| `region` | `string` | `null` | AWS Region to manage resources in (defaults to the provider Region) |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

### Pod Identity Associations

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `associations` | `map(object)` | `{}` | Map of Pod Identity associations to create (map key is arbitrary; each value maps a cluster/namespace/service account to the role) |
| `association_defaults` | `object` | `{}` | Default values merged into every entry in `associations` |

**Association object fields** (`cluster_name`, `namespace`, `service_account` are effectively required per association - either directly or via `association_defaults`):

```hcl
associations = {
  my-cluster = {
    cluster_name         = "my-eks-cluster"
    namespace             = "kube-system"
    service_account       = "my-service-account"
    role_arn              = null   # optional: override the role created by this module
    target_role_arn       = null   # optional: chain to a second IAM role (e.g. cross-account)
    disable_session_tags  = false  # optional: disable EKS-managed session tags
    tags                  = {}     # optional: tags on this specific association
  }
}
```

### Custom Policy & Trust Policy Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `attach_custom_policy` | `bool` | `false` | Attach a custom IAM policy built from `policy_statements`/`source_policy_documents`/`override_policy_documents` |
| `policy_statements` | `list(object)` | `null` | IAM policy statements (sid, actions, resources, effect, condition, principals, ...) |
| `source_policy_documents` | `list(string)` | `[]` | JSON policy documents merged into the custom policy |
| `override_policy_documents` | `list(string)` | `[]` | JSON policy documents that override the merged custom policy |
| `custom_policy_description` | `string` | `"Custom IAM Policy"` | Description of the custom IAM policy |
| `policy_name_prefix` | `string` | `"AmazonEKS_"` | Prefix used for all generated IAM policy names |
| `additional_policy_arns` | `map(string)` | `{}` | Map of existing IAM policy ARNs to attach to the role |
| `trust_policy_statements` | `list(object)` | `null` | Custom statements added to the role's assume-role (trust) policy |
| `trust_policy_conditions` | `list(object)` | `[]` | Conditions added to the default trust policy (e.g. restrict by `aws:PrincipalOrgID`) |

### Service-Specific Policy Attachments

Every built-in policy follows the pattern `attach_<service>_policy` (bool, default `false`) plus optional `<service>_policy_name` (custom name) and service-specific scoping variables:

| Attach Flag | Key Scoping Variable(s) | Notes |
|-------------|--------------------------|-------|
| `attach_aws_ebs_csi_policy` | `aws_ebs_csi_kms_arns` | KMS ARNs required for encrypted EBS volumes |
| `attach_aws_efs_csi_policy` | - | - |
| `attach_aws_fsx_lustre_csi_policy` | `aws_fsx_lustre_csi_service_role_arns` | For FSx-managed service-linked roles |
| `attach_mountpoint_s3_csi_policy` | `mountpoint_s3_csi_bucket_arns`, `mountpoint_s3_csi_bucket_path_arns` | Both bucket and path ARNs are required |
| `attach_aws_lb_controller_policy` | - | Full AWS Load Balancer Controller permissions |
| `attach_aws_lb_controller_targetgroup_binding_only_policy` | `aws_lb_controller_targetgroup_arns` | Minimal permissions when nodes register directly |
| `attach_external_dns_policy` | `external_dns_hosted_zone_arns` | Route53 hosted zone ARNs |
| `attach_cert_manager_policy` | `cert_manager_hosted_zone_arns` | Route53 hosted zone ARNs for DNS-01 challenges |
| `attach_cluster_autoscaler_policy` | `cluster_autoscaler_cluster_names` | Scopes ASG permissions to named clusters |
| `attach_aws_vpc_cni_policy` | `aws_vpc_cni_enable_ipv4`, `aws_vpc_cni_enable_ipv6`, `aws_vpc_cni_enable_cloudwatch_logs` | Enable only the IP version(s) in use |
| `attach_external_secrets_policy` | `external_secrets_ssm_parameter_arns`, `external_secrets_secrets_manager_arns`, `external_secrets_kms_key_arns`, `external_secrets_create_permission` | `create_permission` defaults `false` (read-only) |
| `attach_velero_policy` | `velero_s3_bucket_arns`, `velero_s3_bucket_path_arns`, `velero_kms_arns` | Both bucket and path ARNs are required |
| `attach_aws_cloudwatch_observability_policy` | - | AWS-managed CloudWatch Observability add-on |
| `attach_amazon_managed_service_prometheus_policy` | `amazon_managed_service_prometheus_workspace_arns` | AMP workspace ARNs |
| `attach_aws_appmesh_controller_policy` | - | App Mesh Controller |
| `attach_aws_appmesh_envoy_proxy_policy` | - | App Mesh Envoy Proxy |
| `attach_aws_gateway_controller_policy` | - | Gateway API Controller (`aws-application-networking-k8s`) |
| `attach_aws_privateca_issuer_policy` | `aws_privateca_issuer_acmca_arns` | ACM Private CA authority ARNs |
| `attach_aws_node_termination_handler_policy` | `aws_node_termination_handler_sqs_queue_arns` | SQS queues carrying termination events |
| `attach_pganalyze_policy` | - | pganalyze RDS/Aurora monitoring |

## Main Outputs

| Output | Description |
|--------|-------------|
| `iam_role_arn` | ARN of the IAM role |
| `iam_role_name` | Name of the IAM role |
| `iam_role_path` | Path of the IAM role |
| `iam_role_unique_id` | Unique ID of the IAM role |
| `iam_policy_arn` | ARN of the custom IAM policy (when `attach_custom_policy = true`) |
| `iam_policy_name` | Name of the custom IAM policy |
| `iam_policy_id` | ID of the custom IAM policy |
| `associations` | Map of Pod Identity associations created (includes `association_arn`, `association_id`, `external_id`) |

## Usage Examples

### Example 1: EBS CSI Driver with KMS Encryption

```hcl
module "ebs_csi_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.8"

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
  version = "~> 2.8"

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

  # Multiple cluster associations (only cluster_name differs)
  associations = {
    prod-us-east-1 = { cluster_name = "prod-cluster-us-east-1" }
    prod-us-west-2 = { cluster_name = "prod-cluster-us-west-2" }
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
  version = "~> 2.8"

  name = "aws-load-balancer-controller"

  attach_aws_lb_controller_policy = true
  # For minimal permissions when nodes self-register with target groups, use instead:
  # attach_aws_lb_controller_targetgroup_binding_only_policy = true
  # aws_lb_controller_targetgroup_arns                       = ["arn:aws:elasticloadbalancing:...:targetgroup/foo/bar"]

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
  version = "~> 2.8"

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
  version = "~> 2.8"

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
  version = "~> 2.8"

  name = "custom-app"

  attach_custom_policy = true
  policy_statements = [
    {
      sid       = "AllowS3Access"
      effect    = "Allow"
      actions   = ["s3:GetObject", "s3:PutObject"]
      resources = ["arn:aws:s3:::my-app-bucket/*"]
    },
    {
      sid       = "AllowDynamoDB"
      effect    = "Allow"
      actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:Query"]
      resources = ["arn:aws:dynamodb:us-east-1:123456789012:table/my-app-table"]
    }
  ]

  # Restrict who can assume the role to principals in this AWS Organization
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
  version = "~> 2.8"

  name = "velero"

  attach_velero_policy       = true
  velero_s3_bucket_arns      = ["arn:aws:s3:::eks-backup-bucket"]
  velero_s3_bucket_path_arns = ["arn:aws:s3:::eks-backup-bucket/*"]
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
  version = "~> 2.8"

  name = "vpc-cni"

  attach_aws_vpc_cni_policy          = true
  aws_vpc_cni_enable_ipv4            = true
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

### Example 9: Cross-Account Role Chaining

```hcl
module "cross_account_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.8"

  name = "cross-account-app"

  attach_custom_policy = true
  policy_statements = [
    {
      sid       = "AllowAssumeTarget"
      effect    = "Allow"
      actions   = ["sts:AssumeRole"]
      resources = ["arn:aws:iam::999999999999:role/target-role"]
    }
  ]

  associations = {
    my-cluster = {
      cluster_name     = "my-eks-cluster"
      namespace        = "my-app"
      service_account  = "my-app-sa"
      target_role_arn  = "arn:aws:iam::999999999999:role/target-role"
    }
  }

  tags = {
    Application = "cross-account-app"
  }
}
```

## Best Practices

### Security

1. **Apply Least Privilege**: Prefer the service-specific `attach_*_policy` flags over broad custom policies whenever a built-in policy covers the use case.
2. **Scope Resource ARNs**: Always pass exact ARNs for Route53 zones, S3 buckets, KMS keys, SQS queues, and ACM PCA authorities instead of wildcards.
3. **Use Trust Policy Conditions**: Add `trust_policy_conditions` with `aws:PrincipalOrgID` (or similar) to restrict who can assume the role.
4. **KMS for Encrypted Volumes**: Always set `aws_ebs_csi_kms_arns` when EBS volumes are encrypted, and `velero_kms_arns` when Velero backups use KMS-encrypted buckets.
5. **External Secrets Read-Only**: Leave `external_secrets_create_permission = false` unless workloads explicitly need to create/delete secrets.
6. **Separate Roles by Function**: Create one IAM role per controller/service rather than sharing a broad role across many workloads.

### Configuration

1. **Use Association Defaults**: Set `association_defaults` for the shared `namespace`/`service_account` when the same role is associated across many clusters.
2. **Pin the Module Version**: Use `version = "~> 2.8"` to avoid unexpected changes to generated IAM policies.
3. **Keep Name Prefixes On**: Leave `use_name_prefix = true` (default) so the same module can be deployed multiple times per account/region without name collisions.
4. **Consistent Tagging**: Apply `Environment`, `Application`, and `Component` tags for cost allocation and resource tracking.
5. **Cluster Name Scoping**: Always set `cluster_autoscaler_cluster_names` to restrict Cluster Autoscaler's ASG permissions to specific clusters.
6. **IPv4 vs IPv6**: Enable only the IP version(s) the cluster actually uses via `aws_vpc_cni_enable_ipv4`/`aws_vpc_cni_enable_ipv6`.

### Operational

1. **Verify Associations**: After apply, run `aws eks list-pod-identity-associations --cluster-name <cluster>` to confirm.
2. **Associations Can Precede Service Accounts**: EKS Pod Identity associations can be created before the Kubernetes service account exists; this is safe.
3. **Path ARNs Required for S3-based Policies**: Mountpoint S3 CSI and Velero both require *both* `*_bucket_arns` and `*_bucket_path_arns`.
4. **Route53 Zone ARN Format**: Use `arn:aws:route53:::hostedzone/<ZONE_ID>` - note the triple colon `:::`.
5. **TargetGroupBinding-Only Mode**: Use `attach_aws_lb_controller_targetgroup_binding_only_policy` with `aws_lb_controller_targetgroup_arns` for minimal Load Balancer Controller permissions when nodes self-register.
6. **Cross-Account Access**: Use per-association `target_role_arn` for STS role chaining instead of granting the base role direct cross-account permissions.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-eks-pod-identity
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eks-pod-identity/aws/latest
- **Complete Example**: https://github.com/terraform-aws-modules/terraform-aws-eks-pod-identity/tree/master/examples/complete
- **AWS EKS Pod Identity Documentation**: https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html
- **AWS EKS Pod Identity Agent Setup**: https://docs.aws.amazon.com/eks/latest/userguide/pod-id-agent-setup.html
- **`aws_eks_pod_identity_association` Resource Reference**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_pod_identity_association
- **EKS Best Practices Guide**: https://aws.github.io/aws-eks-best-practices/
- **AWS Load Balancer Controller**: https://kubernetes-sigs.github.io/aws-load-balancer-controller/
- **External Secrets Operator**: https://external-secrets.io/

## Notes for AI Agents

When generating Terraform code with this module:

1. **Use Pre-built Policies**: Prefer `attach_*_policy` booleans over custom policies when a service is on the supported list (20 built-in integrations).
2. **Always Specify Resource ARNs**: For S3, Route53, KMS, SQS, ACM PCA - never use wildcards, always provide exact ARNs.
3. **KMS for Encrypted Volumes**: EBS CSI with encrypted volumes requires `aws_ebs_csi_kms_arns`.
4. **S3 Path ARNs Required**: For Mountpoint S3 CSI and Velero, both `*_bucket_arns` and `*_bucket_path_arns` must be set.
5. **Association Object Structure**: Each entry in `associations` needs `cluster_name`, `namespace`, `service_account` (directly or via `association_defaults`); optional fields are `role_arn`, `target_role_arn`, `disable_session_tags`, `tags`.
6. **Use Association Defaults for Multi-Cluster**: When the same role/service is deployed to multiple clusters, set `association_defaults` and let each `associations` entry only specify `cluster_name`.
7. **Route53 Zone ARN Format**: Use `arn:aws:route53:::hostedzone/<ZONE_ID>` (triple colon `:::`).
8. **Version Pinning**: Always include `version = "~> 2.8"` in the module block.
9. **Cluster Name Scoping**: Always set `cluster_autoscaler_cluster_names` when `attach_cluster_autoscaler_policy = true`.
10. **External Secrets Read-Only by Default**: `external_secrets_create_permission = false` is correct for most cases; only set `true` if the workload creates/deletes secrets.
11. **Cross-Account Access**: Use `target_role_arn` on the association (role chaining) rather than embedding cross-account trust in the base role.
12. **Exact Attach-Flag Name**: The CloudWatch Observability flag is `attach_aws_cloudwatch_observability_policy` (not `attach_cloudwatch_observability_policy`).
