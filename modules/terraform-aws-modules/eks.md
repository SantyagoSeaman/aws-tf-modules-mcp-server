# Terraform AWS EKS Module

## Module Information

- **Module Name**: `eks`
- **Module ID**: `terraform-aws-modules/eks/aws`
- **Source**: `terraform-aws-modules/eks/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-eks
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest
- **Latest Version**: 21.24.0
- **Purpose**: Creates and manages Amazon EKS clusters with support for EKS Auto Mode, Provisioned Control Plane, managed/self-managed node groups, Fargate profiles, hybrid on-premises nodes, Karpenter autoscaling infrastructure, and EKS Capabilities (ACK, ArgoCD, KRO)
- **Service**: AWS EKS (Elastic Kubernetes Service)
- **Category**: Container Orchestration, Compute, Kubernetes
- **Keywords**: eks, kubernetes, k8s, managed-node-group, fargate, karpenter, irsa, pod-identity, oidc, eks-auto-mode, hybrid-nodes, spot-instances, bottlerocket, al2023, efa, eks-addons, kms-encryption, access-entry, eks-capabilities
- **Use For**: Running containerized applications at scale, microservices deployment on Kubernetes, cloud-native application hosting, CI/CD pipeline execution, machine learning model training and serving, big data processing workloads, multi-tenant Kubernetes platforms, hybrid cloud deployments, cost-optimized compute with Spot instances, serverless workloads with Fargate, high-performance computing with EFA

## Description

This Terraform module provisions and manages Amazon Elastic Kubernetes Service (EKS) clusters, covering the full control-plane lifecycle: cluster creation, IAM roles, security groups, KMS-based secrets encryption, control plane logging, cluster add-ons, and cluster access management via access entries. It supports several compute models that can be mixed within the same cluster: EKS Auto Mode (AWS manages both control plane and compute nodes), EKS Provisioned Control Plane (guaranteed API server capacity tiers for large clusters), EKS managed node groups, self-managed node groups (EC2 Auto Scaling Groups with full launch-template control), Fargate profiles (serverless pods), and hybrid nodes (on-premises/edge nodes joined to an EKS control plane).

The module ships as a root module plus six purpose-built submodules — `eks-managed-node-group`, `self-managed-node-group`, `fargate-profile`, `karpenter`, `hybrid-node-role`, and `capability` — each usable independently or composed with the root module. Cluster access is managed exclusively through EKS access entries (the legacy `aws-auth` ConfigMap sub-module was removed in v21); OIDC-based IRSA and EKS Pod Identity are both supported for granting pods AWS permissions, with Pod Identity now the default mechanism used internally by the `karpenter` submodule.

Version 21 is a major breaking release: nearly every root-module variable that was previously prefixed with `cluster_` was renamed to drop that prefix (e.g. `cluster_name` → `name`, `cluster_version` → `kubernetes_version`, `cluster_endpoint_public_access` → `endpoint_public_access`, `cluster_addons` → `addons`). Outputs were **not** renamed and still use the `cluster_*` prefix (e.g. `cluster_name`, `cluster_version`). The module no longer auto-bootstraps default add-ons, so `vpc-cni`, `coredns`, `kube-proxy`, and (when using Pod Identity) `eks-pod-identity-agent` must be declared explicitly via the `addons` variable or the cluster will lack pod networking.

## Key Features

- **Six Specialized Submodules**: `eks-managed-node-group`, `self-managed-node-group`, `fargate-profile`, `karpenter`, `hybrid-node-role`, and `capability`, usable standalone or with the root module
- **EKS Auto Mode**: Fully AWS-managed control plane and compute nodes via `compute_config`, with support for custom node pools alongside built-in ones
- **EKS Provisioned Control Plane**: Enhanced API server capacity tiers (`standard`, `tier-xl`, `tier-2xl`, `tier-4xl`, `tier-8xl`) via `control_plane_scaling_config` for large/high-throughput clusters
- **EKS Capabilities**: The `capability` submodule provisions AWS-managed operators — ACK (AWS Controllers for Kubernetes), ArgoCD, and KRO (Kube Resource Orchestrator) — directly through the EKS API
- **Managed & Self-Managed Node Groups**: AWS-managed lifecycle with node auto-repair and rolling updates, or full control over launch templates/AMIs/ASG behavior
- **Fargate Profiles**: Serverless pod execution selected by namespace/label, with automated pod execution IAM roles
- **Hybrid Nodes**: On-premises/edge Kubernetes nodes join the control plane via SSM or IAM Roles Anywhere (the `hybrid-node-role` submodule)
- **Access Entries**: Fine-grained, auditable cluster access control that fully replaces the legacy `aws-auth` ConfigMap
- **IRSA and EKS Pod Identity**: Automatic OIDC provider creation for IRSA (`enable_irsa`); Karpenter and other submodules default to Pod Identity associations
- **KMS Secrets Encryption**: Auto-created or bring-your-own KMS key for envelope encryption of Kubernetes secrets (`encryption_config`, `create_kms_key`)
- **EKS Add-ons**: Declarative add-on management (`addons`) with `before_compute` ordering, Pod Identity association per add-on, and per-add-on namespace configuration — no default add-ons are bootstrapped
- **Node Auto Repair**: `node_repair_config` on EKS managed node groups automatically replaces unhealthy nodes
- **EFA Support**: Elastic Fabric Adapter with automatic interface exposure and placement-group configuration at both cluster and node-group level
- **Spot/On-Demand Mix and Multiple AMI Families**: AL2023 (default), Bottlerocket, Windows 2025, custom AMIs, mixed capacity types for cost optimization
- **Egress and Networking Controls**: `control_plane_egress_mode` (`AWS_MANAGED`/`CUSTOMER_ROUTED`), IPv4/IPv6 dual-stack, remote network config for hybrid nodes
- **CloudWatch Control Plane Logging**: Configurable log types (`api`, `audit`, `authenticator`, `controllerManager`, `scheduler`) with dedicated log group management
- **Security Defaults**: Public endpoint disabled by default, KMS encryption on by default, separate control-plane subnets supported

## Main Use Cases

1. **Microservices Deployment**: Run containerized microservices with service mesh integration
2. **CI/CD Pipeline Execution**: Execute build and deployment pipelines in ephemeral containers
3. **Machine Learning Workloads**: Train and serve ML models with GPU/EFA-enabled node groups
4. **Big Data Processing**: Run Spark, Hadoop, and data processing frameworks on Kubernetes
5. **Event-Driven Applications**: Deploy serverless event processors using Fargate
6. **Cost-Optimized Compute**: Leverage Spot instances and Karpenter consolidation for fault-tolerant batch workloads
7. **High-Performance Computing**: Run HPC/distributed-training workloads with EFA-enabled instance types
8. **Multi-Tenant Platforms**: Build shared Kubernetes platforms with namespace isolation and access entries
9. **Hybrid Cloud Deployments**: Connect on-premises or edge nodes to an EKS control plane
10. **Managed Platform Operators**: Deploy ACK, ArgoCD, or KRO as AWS-managed EKS Capabilities instead of self-hosted Helm charts
11. **Auto-Scaling Applications**: Dynamically scale workloads with Karpenter or EKS Auto Mode

## Submodules

### 1. eks-managed-node-group
- **Purpose**: Create AWS-managed node groups with automated lifecycle management, node auto-repair, and rolling updates
- **Source**: `terraform-aws-modules/eks/aws//modules/eks-managed-node-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/eks-managed-node-group
- **Key Features**: Custom launch templates, Spot/On-Demand, EFA support, `node_repair_config`, `update_config.update_strategy`
- **Use Cases**: Production workloads, managed updates, simplified operations, multi-AZ deployments

### 2. self-managed-node-group
- **Purpose**: Create self-managed node groups (EC2 Auto Scaling Groups) with complete control over launch templates and user data
- **Source**: `terraform-aws-modules/eks/aws//modules/self-managed-node-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/self-managed-node-group
- **Key Features**: Custom launch templates, user data scripts, AL2023/Bottlerocket AMIs, mixed instance policies
- **Use Cases**: Custom configurations, specialized workloads, advanced customization, legacy compatibility

### 3. fargate-profile
- **Purpose**: Create Fargate profiles for serverless container execution with namespace/label selectors
- **Source**: `terraform-aws-modules/eks/aws//modules/fargate-profile`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/fargate-profile
- **Key Features**: Namespace/label selectors, automated pod execution role, subnet configuration
- **Use Cases**: Serverless workloads, batch processing, kube-system components, cost-efficient low-traffic services

### 4. karpenter
- **Purpose**: Create IAM resources and supporting infrastructure for Karpenter, an open-source node autoscaler
- **Source**: `terraform-aws-modules/eks/aws//modules/karpenter`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/karpenter
- **Key Features**: Controller + node IAM roles, EKS Pod Identity association (default; IRSA removed in v21), SQS queue + EventBridge rules for interruption handling, node access entry
- **Use Cases**: Dynamic autoscaling, diverse instance type selection, cost optimization, rapid scaling

### 5. hybrid-node-role
- **Purpose**: Create IAM roles/policies for on-premises or edge nodes connecting to an EKS control plane
- **Source**: `terraform-aws-modules/eks/aws//modules/hybrid-node-role`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/hybrid-node-role
- **Key Features**: SSM-based authentication (default) or IAM Roles Anywhere (`enable_ira`), Pod Identity support
- **Use Cases**: Hybrid cloud, edge deployments, on-premises Kubernetes nodes, distributed infrastructure

### 6. capability
- **Purpose**: Provision AWS-managed EKS Capabilities — ACK, ArgoCD, or KRO — plus the IAM role/policy they require
- **Source**: `terraform-aws-modules/eks/aws//modules/capability`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/capability
- **Key Features**: Managed `aws_eks_capability` resource, per-capability IAM role/policy, ArgoCD AWS IAM Identity Center RBAC mapping
- **Use Cases**: AWS-managed GitOps (ArgoCD) without self-hosting, AWS resource orchestration via ACK/KRO controllers without managing their Helm lifecycle

## Submodule 1: eks-managed-node-group

### Description

Creates an EKS managed node group along with its IAM role, an optional dedicated security group, and (by default) a custom launch template. AWS handles node provisioning, patching, and termination, draining pods automatically during updates. `node_repair_config` enables automatic replacement of unhealthy nodes.

### Key Features

- AWS-managed node lifecycle with automated updates, patching, and node auto-repair
- Custom launch templates with user data (enabled by default; disable via `use_custom_launch_template = false` to use EKS's own default template)
- Configurable instance types and capacity types (`ON_DEMAND`/`SPOT`)
- Kubernetes labels and taints for pod scheduling
- AL2023 (default `ami_type`), Bottlerocket, Windows 2025, or custom AMI support
- EFA support with automatic interface exposure and placement group creation
- IMDSv2 enforced by default (`http_tokens = "required"`, hop limit `1`)
- Multi-AZ deployment support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the EKS managed node group |
| `cluster_name` | `string` | `""` | Name of the associated EKS cluster |
| `kubernetes_version` | `string` | `null` | Kubernetes version; defaults to the cluster's version |
| `subnet_ids` | `list(string)` | `null` | Subnet IDs for node placement (must carry `kubernetes.io/cluster/<name>` tag) |
| `min_size` / `max_size` / `desired_size` | `number` | `1` / `3` / `1` | Auto Scaling Group sizing |
| `instance_types` | `list(string)` | `["t3.medium"]` | Candidate EC2 instance types |
| `capacity_type` | `string` | `"ON_DEMAND"` | `ON_DEMAND` or `SPOT` |
| `ami_type` | `string` | `"AL2023_x86_64_STANDARD"` | AMI family/type |
| `labels` | `map(string)` | `null` | Kubernetes node labels |
| `taints` | `map(object)` | `null` | Kubernetes taints (map keyed by taint name) — fields: `key`, `value`, `effect` |
| `node_repair_config` | `object` | `null` | Enable/tune automatic unhealthy node replacement — fields: `enabled`, `max_parallel_nodes_repaired_count`, `max_parallel_nodes_repaired_percentage`, `max_unhealthy_node_threshold_count`, `max_unhealthy_node_threshold_percentage`, `node_repair_config_overrides` |
| `block_device_mappings` | `map(object)` | `null` | EBS volume configuration — fields: `device_name`, `ebs`, `no_device`, `virtual_name` |

### Main Outputs

| Output | Description |
|--------|-------------|
| `node_group_arn` | ARN of the EKS managed node group |
| `node_group_id` | `<cluster_name>:<node_group_name>` identifier |
| `node_group_status` | Status of the node group |
| `node_group_autoscaling_group_names` | Underlying Auto Scaling Group name(s) |
| `iam_role_arn` | ARN of the node IAM role |
| `launch_template_id` / `launch_template_latest_version` | Launch template identifiers |
| `security_group_id` | ID of the node group's dedicated security group (if created) |

### Usage Example

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = "production-eks"
  kubernetes_version = "1.33"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  endpoint_public_access = true

  # Adds the Terraform caller identity as a cluster admin via access entry
  enable_cluster_creator_admin_permissions = true

  addons = {
    coredns                = {}
    kube-proxy             = {}
    eks-pod-identity-agent = { before_compute = true }
    vpc-cni                = { before_compute = true }
  }

  eks_managed_node_groups = {
    general = {
      instance_types = ["m5.large"]
      capacity_type  = "ON_DEMAND"

      min_size     = 2
      max_size     = 10
      desired_size = 3

      labels = {
        role = "general"
      }

      tags = { NodeGroup = "general-purpose" }
    }

    spot_batch = {
      instance_types = ["m5.large", "m5a.large", "m5n.large"]
      capacity_type  = "SPOT"

      min_size     = 0
      max_size     = 20
      desired_size = 0

      labels = { role = "batch", spot = "true" }
      taints = {
        batch = {
          key    = "batch"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }

      tags = { NodeGroup = "spot-batch" }
    }
  }

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

# Standalone managed node group attached to an existing cluster
module "separate_node_group" {
  source = "terraform-aws-modules/eks/aws//modules/eks-managed-node-group"

  name                = "additional-nodes"
  cluster_name        = module.eks.cluster_name
  kubernetes_version  = module.eks.cluster_version
  subnet_ids          = module.vpc.private_subnets

  # Required when used outside of the parent EKS module context
  cluster_primary_security_group_id = module.eks.cluster_primary_security_group_id
  vpc_security_group_ids            = [module.eks.node_security_group_id]

  ami_type       = "BOTTLEROCKET_x86_64"
  instance_types = ["m5.xlarge"]
  capacity_type  = "ON_DEMAND"

  min_size     = 1
  max_size     = 5
  desired_size = 2

  block_device_mappings = {
    xvda = {
      device_name = "/dev/xvda"
      ebs = {
        volume_size           = 100
        volume_type           = "gp3"
        encrypted              = true
        delete_on_termination = true
      }
    }
  }

  labels = { os = "bottlerocket", role = "application" }
  tags   = { NodeGroup = "additional" }
}
```

## Submodule 2: self-managed-node-group

### Description

Creates a self-managed EC2 Auto Scaling Group node group with a launch template, IAM role, and (optionally) a dedicated security group. Unlike managed node groups, updates, patching, and termination are the operator's responsibility, but this submodule provides maximum flexibility for custom AMIs, bootstrap scripts, and instance settings.

### Key Features

- Complete control over EC2 instance configuration and launch template
- Pre/post-bootstrap user data and `cloudinit_pre_nodeadm`/`cloudinit_post_nodeadm` hooks
- Any EC2 AMI, including custom builds; `use_latest_ami_release_version` for auto-tracking EKS-optimized AMIs
- IMDSv2 enforced by default
- Placement group and EFA support for HPC workloads
- Detailed CloudWatch monitoring toggle

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the self-managed node group |
| `cluster_name` | `string` | `""` | Name of the associated EKS cluster |
| `kubernetes_version` | `string` | `null` | Kubernetes version used to resolve bootstrap/AMI data |
| `cluster_endpoint` / `cluster_auth_base64` | `string` | `null` | Required when used standalone (outside the root module) |
| `subnet_ids` | `list(string)` | `null` | Subnet IDs for node placement |
| `min_size` / `max_size` / `desired_size` | `number` | `0` / `3` / `1` | Auto Scaling Group sizing |
| `instance_type` | `string` | `null` | Single EC2 instance type (not a list) |
| `ami_id` | `string` | `null` | Custom AMI ID; omit to use the latest EKS-optimized AMI |
| `pre_bootstrap_user_data` / `post_bootstrap_user_data` | `string` | `null` | Custom user data injected around the bootstrap script |

### Main Outputs

| Output | Description |
|--------|-------------|
| `autoscaling_group_id` / `autoscaling_group_arn` | Auto Scaling Group identifiers |
| `iam_role_arn` | ARN of the node IAM role |
| `launch_template_id` | ID of the launch template |
| `security_group_id` | ID of the dedicated security group (if created) |

### Usage Example

```hcl
module "self_managed_nodes" {
  source = "terraform-aws-modules/eks/aws//modules/self-managed-node-group"

  name               = "custom-nodes"
  cluster_name       = module.eks.cluster_name
  kubernetes_version = module.eks.cluster_version

  # Required when used outside of the parent EKS module context
  vpc_security_group_ids = [
    module.eks.cluster_primary_security_group_id,
    module.eks.cluster_security_group_id,
  ]

  subnet_ids = module.vpc.private_subnets

  min_size     = 2
  max_size     = 10
  desired_size = 3

  instance_type = "m5.large"

  use_latest_ami_release_version = true
  ami_type                       = "AL2023_x86_64_STANDARD"

  pre_bootstrap_user_data = <<-EOT
    #!/bin/bash
    yum install -y amazon-cloudwatch-agent
  EOT

  enable_monitoring = true

  block_device_mappings = {
    xvda = {
      device_name = "/dev/xvda"
      ebs = {
        volume_size           = 100
        volume_type           = "gp3"
        encrypted              = true
        delete_on_termination = true
      }
    }
  }

  create_iam_instance_profile = true
  iam_role_additional_policies = {
    AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  }

  tags = { NodeType = "self-managed" }
}
```

## Submodule 3: fargate-profile

### Description

Creates a Fargate profile that enables serverless pod execution on EKS without managing EC2 instances. Namespace/label selectors determine which pods land on Fargate; the submodule manages the Fargate pod execution IAM role and subnet selection.

### Key Features

- Serverless pod execution without EC2 node management
- Namespace and label-based selectors (multiple selectors per profile)
- Automatic pod execution IAM role management
- Pay-per-pod pricing model

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the Fargate profile |
| `cluster_name` | `string` | `""` | Name of the associated EKS cluster |
| `subnet_ids` | `list(string)` | `[]` | Subnet IDs for Fargate pod ENIs (private subnets only) |
| `selectors` | `list(object({ namespace = string, labels = optional(map(string)) }))` | `null` | Namespace/label selectors for pods to run on Fargate |
| `create_iam_role` | `bool` | `true` | Whether to create the pod execution IAM role |

### Main Outputs

| Output | Description |
|--------|-------------|
| `fargate_profile_arn` | ARN of the Fargate profile |
| `fargate_profile_id` | `<cluster_name>:<profile_name>` identifier |
| `fargate_profile_status` | Status of the Fargate profile |
| `fargate_profile_pod_execution_role_arn` | ARN of the pod execution IAM role |

### Usage Example

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = "fargate-eks"
  kubernetes_version = "1.33"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  fargate_profiles = {
    kube_system = {
      selectors = [
        { namespace = "kube-system", labels = { k8s-app = "kube-dns" } }
      ]
    }
    applications = {
      selectors = [
        { namespace = "app-*" },
        { namespace = "backend", labels = { fargate = "enabled" } }
      ]
    }
  }

  tags = { Environment = "production" }
}

# Standalone Fargate profile
module "separate_fargate_profile" {
  source = "terraform-aws-modules/eks/aws//modules/fargate-profile"

  name         = "ml-workloads"
  cluster_name = module.eks.cluster_name
  subnet_ids   = module.vpc.private_subnets

  selectors = [
    { namespace = "ml-training", labels = { compute = "fargate" } },
    { namespace = "ml-inference" }
  ]

  tags = { Workload = "ML" }
}
```

## Submodule 4: karpenter

### Description

Creates the AWS-side infrastructure required to run Karpenter: a controller IAM role (using EKS Pod Identity by default; native IRSA support was removed in v21), a node IAM role plus access entry so provisioned nodes can join the cluster, and an SQS queue with EventBridge rules for Spot interruption/rebalance handling. Karpenter itself (the controller) is still installed separately via Helm.

### Key Features

- Controller IAM role with Pod Identity association (`create_pod_identity_association = true` by default)
- Node IAM role + automatic access entry for node registration
- SQS queue and EventBridge rules for native Spot interruption handling
- Support for reusing an existing node IAM role from a bootstrap managed node group

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `cluster_name` | `string` | `""` | Name of the associated EKS cluster |
| `create_node_iam_role` | `bool` | `true` | Whether to create the Karpenter node IAM role |
| `node_iam_role_arn` | `string` | `null` | Existing node IAM role ARN (when `create_node_iam_role = false`) |
| `create_access_entry` | `bool` | `true` | Whether to create the node access entry (set `false` if reusing a role that already has one) |
| `node_iam_role_additional_policies` | `map(string)` | `{}` | Extra policies attached to the node IAM role |
| `enable_spot_termination` | `bool` | `true` | Create SQS queue/EventBridge rules for interruption handling |
| `namespace` | `string` | `"kube-system"` | Namespace for the Pod Identity association |
| `service_account` | `string` | `"karpenter"` | Service account name for the Pod Identity association |

### Main Outputs

| Output | Description |
|--------|-------------|
| `iam_role_arn` | ARN of the Karpenter controller IAM role |
| `node_iam_role_arn` / `node_iam_role_name` | Node IAM role identifiers |
| `node_access_entry_arn` | ARN of the node access entry |
| `queue_name` / `queue_arn` | SQS interruption queue identifiers |

### Usage Example

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = "karpenter-eks"
  kubernetes_version = "1.33"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  addons = {
    eks-pod-identity-agent = {}
    coredns                = {}
    kube-proxy             = {}
    vpc-cni                = { before_compute = true }
  }

  enable_cluster_creator_admin_permissions = true

  # Minimal bootstrap node group to host the Karpenter controller
  eks_managed_node_groups = {
    karpenter = {
      instance_types = ["t3.medium"]
      min_size       = 2
      max_size       = 3
      desired_size   = 2

      taints = {
        karpenter = {
          key    = "karpenter.sh/controller"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
    }
  }

  tags = { "karpenter.sh/discovery" = "karpenter-eks" }
}

# Tag subnets/security group for Karpenter discovery
resource "aws_ec2_tag" "karpenter_subnet" {
  for_each    = toset(module.vpc.private_subnets)
  resource_id = each.value
  key         = "karpenter.sh/discovery"
  value       = module.eks.cluster_name
}

resource "aws_ec2_tag" "karpenter_sg" {
  resource_id = module.eks.cluster_security_group_id
  key         = "karpenter.sh/discovery"
  value       = module.eks.cluster_name
}

module "karpenter" {
  source = "terraform-aws-modules/eks/aws//modules/karpenter"

  cluster_name = module.eks.cluster_name

  node_iam_role_additional_policies = {
    AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  }
}

# Karpenter controller (uses Pod Identity - no IRSA annotation needed)
resource "helm_release" "karpenter" {
  namespace        = "kube-system"
  name             = "karpenter"
  repository       = "oci://public.ecr.aws/karpenter"
  chart            = "karpenter"
  version          = "1.12.0"

  values = [
    <<-EOT
    settings:
      clusterName: ${module.eks.cluster_name}
      clusterEndpoint: ${module.eks.cluster_endpoint}
      interruptionQueue: ${module.karpenter.queue_name}
    serviceAccount:
      name: karpenter
    EOT
  ]

  depends_on = [module.eks, module.karpenter]
}
```

## Submodule 5: hybrid-node-role

### Description

Creates the IAM role and policy that EKS Hybrid Nodes (on-premises or edge machines) use to authenticate to the control plane, either via AWS Systems Manager (default) or AWS IAM Roles Anywhere (`enable_ira = true`).

### Key Features

- SSM Hybrid Activations-based authentication by default
- IAM Roles Anywhere support for certificate-based authentication (trust anchor + profile)
- EKS Pod Identity enabled on the node role by default

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `"EKSHybridNode"` | Name of the IAM role |
| `enable_ira` | `bool` | `false` | Use IAM Roles Anywhere instead of SSM |
| `ira_trust_anchor_source_type` | `string` | `null` | Trust anchor source type (e.g. `CERTIFICATE_BUNDLE`) |
| `ira_trust_anchor_x509_certificate_data` | `string` | `null` | PEM certificate bundle for the trust anchor |
| `policies` | `map(string)` | `{}` | Additional IAM policies to attach |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | ARN of the hybrid node IAM role |
| `name` | Name of the hybrid node IAM role |

### Usage Example

```hcl
module "eks_hybrid_node_role" {
  source = "terraform-aws-modules/eks/aws//modules/hybrid-node-role"

  name = "hybrid"

  tags = { Environment = "production" }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = "hybrid-eks"
  kubernetes_version = "1.33"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  create_node_security_group = false
  security_group_additional_rules = {
    hybrid-all = {
      type        = "ingress"
      cidr_blocks = ["172.16.0.0/16"]
      from_port   = 0
      to_port     = 0
      protocol    = "all"
    }
  }

  compute_config = {
    enabled    = true
    node_pools = ["system"]
  }

  access_entries = {
    hybrid-node-role = {
      principal_arn = module.eks_hybrid_node_role.arn
      type          = "HYBRID_LINUX"
    }
  }

  remote_network_config = {
    remote_node_networks = { cidrs = ["172.16.0.0/18"] }
    remote_pod_networks  = { cidrs = ["172.16.64.0/18"] }
  }

  tags = { Environment = "production" }
}
```

## Submodule 6: capability

### Description

Creates an `aws_eks_capability` resource — an AWS-managed operator/controller running on the cluster — along with the IAM role/policy the capability needs. Supported types are `ACK` (AWS Controllers for Kubernetes), `ARGOCD`, and `KRO` (Kube Resource Orchestrator). AWS manages the lifecycle of the operator itself, removing the need to self-host it via Helm.

### Key Features

- Managed ACK, ArgoCD, or KRO deployment via the EKS API instead of self-hosted Helm charts
- Dedicated IAM role/policy per capability, scoped with `iam_role_policies` or `iam_policy_statements`
- ArgoCD-specific configuration for AWS IAM Identity Center RBAC role mapping

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the capability instance |
| `cluster_name` | `string` | `""` | Name of the associated EKS cluster |
| `type` | `string` | `""` | Capability type: `ACK`, `ARGOCD`, or `KRO` |
| `configuration` | `object` | `null` | Type-specific configuration (e.g. `argo_cd.aws_idc`, `argo_cd.rbac_role_mapping`) |
| `iam_role_policies` | `map(string)` | `{}` | Managed policy ARNs to attach to the capability's IAM role |
| `iam_policy_statements` | `map(object)` | `null` | Inline IAM policy statements for the capability's IAM role — fields: `sid`, `actions`, `not_actions`, `effect`, `resources`, `not_resources`, `principals`, `not_principals`, … (8 shown; call get_module("eks//modules/capability", sections=["inputs"]) for the complete list) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `arn` | ARN of the EKS Capability |
| `version` | Version of the deployed capability |
| `argocd_server_url` | URL of the Argo CD server (ArgoCD capability only) |
| `iam_role_arn` | ARN of the capability's IAM role |

### Usage Example

```hcl
module "ack_eks_capability" {
  source = "terraform-aws-modules/eks/aws//modules/capability"

  name         = "example-ack"
  cluster_name = module.eks.cluster_name
  type         = "ACK"

  iam_role_policies = {
    AdministratorAccess = "arn:aws:iam::aws:policy/AdministratorAccess"
  }

  tags = { Environment = "production" }
}

module "argocd_eks_capability" {
  source = "terraform-aws-modules/eks/aws//modules/capability"

  name         = "example-argocd"
  cluster_name = module.eks.cluster_name
  type         = "ARGOCD"

  configuration = {
    argo_cd = {
      aws_idc = {
        idc_instance_arn = "arn:aws:sso:::instance/ssoins-1234567890abcdef0"
      }
      namespace = "argocd"
      rbac_role_mapping = [{
        role     = "ADMIN"
        identity = [{ id = "686103e0-f051-7068-b225-e6392b959d9e", type = "SSO_GROUP" }]
      }]
    }
  }

  tags = { Environment = "production" }
}
```

## Main Module: EKS Cluster

### Description

The root module manages the complete EKS cluster lifecycle: control plane creation, IAM role, cluster/node security groups, KMS-based secret encryption, control plane logging, access entries, OIDC provider for IRSA, and cluster add-ons. It orchestrates the `eks-managed-node-group`, `self-managed-node-group`, and `fargate-profile` submodules internally via `eks_managed_node_groups`, `self_managed_node_groups`, and `fargate_profiles` map variables.

### Key Features

- Complete EKS cluster lifecycle management, including EKS Auto Mode and Provisioned Control Plane
- Multiple node compute types composable in a single cluster (managed, self-managed, Fargate, hybrid)
- Access-entry-based cluster access management (no `aws-auth` ConfigMap sub-module)
- OIDC provider for IRSA (`enable_irsa`, default `true`)
- KMS-based cluster secrets encryption (`encryption_config`, `create_kms_key`)
- Declarative EKS add-ons with `before_compute` dependency ordering — no add-ons are installed by default
- CloudWatch control plane logging with dedicated log group management
- IPv4/IPv6 dual-stack support (`ip_family`)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the EKS cluster (**renamed from `cluster_name` in v21**) |
| `kubernetes_version` | `string` | `null` | Kubernetes version, e.g. `"1.33"` (**renamed from `cluster_version`**) |
| `vpc_id` | `string` | `""` | VPC ID where the cluster will be deployed |
| `subnet_ids` | `list(string)` | `null` | Subnets for node/control-plane ENIs (must carry `kubernetes.io/cluster/<name>` tag) |
| `control_plane_subnet_ids` | `list(string)` | `[]` | Separate subnets for control-plane ENIs |
| `endpoint_public_access` | `bool` | `false` | Enable the public API endpoint (**renamed from `cluster_endpoint_public_access`**) |
| `endpoint_private_access` | `bool` | `true` | Enable the private API endpoint |
| `enable_cluster_creator_admin_permissions` | `bool` | `false` | Grant the Terraform caller identity cluster-admin via access entry |
| `authentication_mode` | `string` | `"API_AND_CONFIG_MAP"` | `API`, `CONFIG_MAP`, or `API_AND_CONFIG_MAP` |
| `access_entries` | `map(object)` | `{}` | Map of access entries + policy associations for cluster access — fields: `kubernetes_groups`, `principal_arn`, `type`, `user_name`, `tags`, `policy_associations` |
| `create_kms_key` | `bool` | `true` | Create a customer-managed KMS key for secret encryption |
| `encryption_config` | `object` | `{}` | `{}` uses/creates a customer KMS key; `null` uses AWS's default managed key; set `provider_key_arn` to BYO key |
| `enabled_log_types` | `list(string)` | `["audit","api","authenticator"]` | Control plane log types (**renamed from `cluster_enabled_log_types`**) |
| `compute_config` | `object` | `null` | EKS Auto Mode config: `{ enabled, node_pools, node_role_arn }` (**renamed from `cluster_compute_config`**) |
| `control_plane_scaling_config` | `object({ tier = string })` | `null` | Provisioned Control Plane tier: `standard`, `tier-xl`, `tier-2xl`, `tier-4xl`, `tier-8xl` |
| `control_plane_egress_mode` | `string` | `null` | `AWS_MANAGED` or `CUSTOMER_ROUTED` control plane egress |
| `addons` | `map(object)` | `null` | EKS add-ons to deploy (**renamed from `cluster_addons`; nothing is bootstrapped by default**) |
| `eks_managed_node_groups` | `map(object)` | `null` | Map of `eks-managed-node-group` submodule invocations |
| `self_managed_node_groups` | `map(object)` | `null` | Map of `self-managed-node-group` submodule invocations |
| `fargate_profiles` | `map(object)` | `null` | Map of `fargate-profile` submodule invocations |
| `remote_network_config` | `object` | `null` | Remote node/pod CIDR config for hybrid nodes — fields: `remote_node_networks`, `remote_pod_networks` |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cluster_name` | The EKS cluster identifier (output kept the `cluster_` prefix even though the input variable is `name`) |
| `cluster_arn` | Full ARN of the cluster |
| `cluster_endpoint` | Kubernetes API server endpoint URL |
| `cluster_version` | Kubernetes version running on the cluster |
| `cluster_certificate_authority_data` | Base64-encoded CA certificate for authentication |
| `cluster_iam_role_arn` | IAM role used by the EKS control plane |
| `cluster_security_group_id` | Security group attached to the control plane |
| `node_security_group_id` | Security group ID for node/pod communication |
| `oidc_provider_arn` | OIDC provider ARN for IRSA |
| `cluster_oidc_issuer_url` | OIDC issuer URL for the cluster |
| `eks_managed_node_groups` / `self_managed_node_groups` / `fargate_profiles` | Maps of full attribute sets per node group/profile created |
| `cluster_addons` | Map of deployed add-on attributes |
| `kms_key_arn` | ARN of the KMS key used for secret encryption |
| `access_entries` | Map of created access entries |

### Usage Examples

#### Example 1: Production EKS Cluster with Managed Node Groups

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = "production-eks"
  kubernetes_version = "1.33"

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.intra_subnets

  endpoint_public_access  = true
  endpoint_private_access = true

  enable_cluster_creator_admin_permissions = true
  authentication_mode                      = "API_AND_CONFIG_MAP"

  # KMS encryption uses a module-created customer-managed key by default
  # (encryption_config defaults to {}); override provider_key_arn to BYO key.

  enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  addons = {
    coredns                = {}
    kube-proxy              = {}
    eks-pod-identity-agent = { before_compute = true }
    vpc-cni = {
      before_compute            = true
      service_account_role_arn  = module.vpc_cni_irsa.iam_role_arn
      configuration_values = jsonencode({
        env = {
          ENABLE_PREFIX_DELEGATION = "true"
          ENABLE_POD_ENI           = "true"
        }
        enableNetworkPolicy = "true"
      })
    }
    aws-ebs-csi-driver = {
      service_account_role_arn = module.ebs_csi_irsa.iam_role_arn
    }
  }

  eks_managed_node_groups = {
    system = {
      instance_types = ["m5.large"]
      capacity_type  = "ON_DEMAND"

      min_size     = 2
      max_size     = 4
      desired_size = 2

      labels = { role = "system" }
      taints = {
        critical = {
          key    = "CriticalAddonsOnly"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }

      tags = { NodeGroup = "system" }
    }

    applications = {
      instance_types = ["m5.xlarge", "m5a.xlarge", "m5n.xlarge"]
      capacity_type  = "ON_DEMAND"

      min_size     = 3
      max_size     = 20
      desired_size = 5

      labels = { role = "application" }
      tags   = { NodeGroup = "applications" }
    }
  }

  fargate_profiles = {
    kube_system = {
      selectors = [{ namespace = "kube-system" }]
    }
  }

  access_entries = {
    admin = {
      principal_arn = "arn:aws:iam::123456789012:role/AdminRole"
      policy_associations = {
        admin = {
          policy_arn   = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = { type = "cluster" }
        }
      }
    }
  }

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

module "vpc_cni_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name             = "vpc-cni"
  attach_vpc_cni_policy = true
  vpc_cni_enable_ipv4   = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-node"]
    }
  }
}

module "ebs_csi_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name             = "ebs-csi"
  attach_ebs_csi_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:ebs-csi-controller-sa"]
    }
  }
}
```

#### Example 2: EKS Auto Mode (Simplest Setup)

```hcl
module "eks_auto_mode" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = "auto-mode-eks"
  kubernetes_version = "1.33"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  endpoint_public_access = true

  enable_cluster_creator_admin_permissions = true

  # AWS manages both control plane and compute nodes; no node groups needed
  compute_config = {
    enabled    = true
    node_pools = ["general-purpose"] # or ["system"] for system workloads only
  }

  tags = { Mode = "Auto" }
}
```

#### Example 3: EKS Provisioned Control Plane

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = "high-capacity-eks"
  kubernetes_version = "1.33"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  endpoint_public_access = true

  enable_cluster_creator_admin_permissions = true

  # Guaranteed API server capacity for large clusters / high API throughput
  control_plane_scaling_config = {
    tier = "tier-xl" # standard | tier-xl | tier-2xl | tier-4xl | tier-8xl
  }

  tags = { Environment = "production" }
}
```

## Best Practices

### Cluster Design and Architecture

1. **Pin the Kubernetes Version Explicitly**: Always set `kubernetes_version` (e.g. `"1.33"`); do not rely on the AWS default, which changes over time.
2. **Plan for Multi-AZ Deployment**: Distribute control-plane ENIs and node groups across at least three availability zones.
3. **Separate Node Groups by Workload**: Use distinct node groups for system components, applications, and batch workloads with taints/labels.
4. **Use Private Subnets for Nodes**: Deploy worker nodes in private subnets with NAT gateways or VPC endpoints for outbound connectivity.
5. **Use Dedicated Control Plane Subnets**: Set `control_plane_subnet_ids` separately from node subnets for better network isolation.
6. **Choose the Right Compute Model**: Use EKS Auto Mode for minimal operational overhead, Provisioned Control Plane for very large/high-throughput clusters, and managed/self-managed node groups when fine-grained control is required.

### Node Group Management

1. **Prefer Managed Node Groups**: Use `eks_managed_node_groups` for simplified operations, automated patching, and `node_repair_config`.
2. **Mix Capacity Types**: On-Demand for critical workloads, Spot for fault-tolerant/batch jobs; specify multiple `instance_types` to improve Spot availability.
3. **Apply Taints for Specialized Nodes**: Dedicate node groups (GPU, batch, system) with taints and matching tolerations.
4. **Deploy Karpenter for Dynamic Scaling**: Use the `karpenter` submodule when workloads need rapid, right-sized scaling across diverse instance types.
5. **Enable Node Auto Repair**: Set `node_repair_config.enabled = true` on managed node groups for automatic unhealthy-node replacement.

### Security and Access Control

1. **Encrypt Cluster Secrets**: Leave `create_kms_key = true` (default) or supply a customer KMS key via `encryption_config.provider_key_arn`; only set `encryption_config = null` to intentionally fall back to the AWS-managed key.
2. **Use IRSA or Pod Identity for Pod-Level AWS Access**: Never grant AWS permissions via the node IAM role; use `enable_irsa` + IAM roles for service accounts, or EKS Pod Identity associations.
3. **Manage Access via Access Entries**: Define `access_entries` explicitly; the `aws-auth` ConfigMap sub-module no longer exists in v21.
4. **Grant the Terraform Caller Admin Access Deliberately**: `enable_cluster_creator_admin_permissions` is a one-time convenience for initial cluster access — reassess before disabling it in production automation.
5. **Enable All Control Plane Log Types**: Set `enabled_log_types` to include `api`, `audit`, `authenticator`, `controllerManager`, and `scheduler` for full auditability.
6. **Disable the Public Endpoint After Bootstrap** where feasible, or restrict it via `endpoint_public_access_cidrs`.

### Add-ons

1. **Declare Add-ons Explicitly**: The module bootstraps nothing by default — always declare `vpc-cni`, `coredns`, `kube-proxy`, and `eks-pod-identity-agent` (if using Pod Identity anywhere in the cluster) in `addons`.
2. **Order Networking Add-ons First**: Set `before_compute = true` on `vpc-cni` (and `eks-pod-identity-agent` when nodes need Pod Identity at boot) so networking is ready before node groups join.
3. **Install the EBS/EFS CSI Driver** for persistent volume support, granting IAM permissions via `service_account_role_arn` (IRSA) or a Pod Identity association.
4. **Track Latest Versions Deliberately**: `most_recent` defaults to `true`; pin `addon_version` explicitly for reproducible/change-controlled environments.

### Cost Optimization

1. **Use Spot Instances** for fault-tolerant workloads to cut compute costs significantly.
2. **Scale to Zero** on node groups with `min_size = 0` for intermittent workloads.
3. **Use Karpenter Consolidation** to right-size and bin-pack nodes automatically.
4. **Use Fargate for Low-Traffic Services** to avoid paying for idle node capacity.
5. **Prefer EKS Auto Mode or Karpenter over static node groups** when workload shape is unpredictable, to avoid over-provisioning.

### High Availability and Resilience

1. **Multi-AZ Node Distribution**: Spread node groups and Fargate subnets across multiple AZs.
2. **Use Pod Disruption Budgets** for critical applications to preserve availability during node updates.
3. **Configure `update_config`** (`max_unavailable`/`max_unavailable_percentage`) to control the blast radius of managed node group rolling updates.
4. **Don't Rely on a Single Node Group**: Spread workloads across multiple groups so a bad rollout is contained.

### Upgrades

1. **Upgrade Within the AWS Support Window**: Plan Kubernetes version upgrades on a regular cadence.
2. **Verify Add-on/Version Compatibility** before bumping `kubernetes_version`.
3. **Upgrade the Control Plane Before Node Groups**, and monitor cluster health throughout.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-eks
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-eks/tree/master/examples
- **v20 → v21 Upgrade Guide**: https://github.com/terraform-aws-modules/terraform-aws-eks/blob/master/docs/UPGRADE-21.0.md
- **AWS EKS Documentation**: https://docs.aws.amazon.com/eks/latest/userguide/
- **EKS Best Practices Guide**: https://aws.github.io/aws-eks-best-practices/
- **EKS Managed Node Groups**: https://docs.aws.amazon.com/eks/latest/userguide/managed-node-groups.html
- **EKS Fargate**: https://docs.aws.amazon.com/eks/latest/userguide/fargate.html
- **EKS Hybrid Nodes**: https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-overview.html
- **Karpenter Documentation**: https://karpenter.sh/
- **IAM Roles for Service Accounts (IRSA)**: https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
- **EKS Pod Identity**: https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html
- **EKS Add-ons**: https://docs.aws.amazon.com/eks/latest/userguide/eks-add-ons.html
- **EKS Pricing**: https://aws.amazon.com/eks/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **v21 Renamed Root-Module Inputs**: `cluster_*`-prefixed variables lost that prefix. Use `name` (not `cluster_name`), `kubernetes_version` (not `cluster_version`), `endpoint_public_access`/`endpoint_private_access` (not `cluster_endpoint_*`), `addons` (not `cluster_addons`), `enabled_log_types` (not `cluster_enabled_log_types`), `compute_config` (not `cluster_compute_config`), `encryption_config` (not `cluster_encryption_config`), `identity_providers` (not `cluster_identity_providers`).
2. **Outputs Kept the `cluster_` Prefix**: `module.eks.cluster_name`, `module.eks.cluster_version`, etc. are still correct — only inputs were renamed.
3. **No Default Add-ons**: The module bootstraps nothing automatically. You must declare `addons = { coredns = {}, kube-proxy = {}, vpc-cni = { before_compute = true }, eks-pod-identity-agent = { before_compute = true } }` or pods will have no networking.
4. **Specify Kubernetes Version Explicitly**: Always set `kubernetes_version` for production clusters.
5. **Endpoint Access Defaults**: Public endpoint is disabled by default (`endpoint_public_access = false`); enable it for kubectl access from outside the VPC.
6. **Enable Cluster Creator Admin**: Set `enable_cluster_creator_admin_permissions = true` so the Terraform identity can access the cluster after creation.
7. **Subnet Tagging Required**: Subnets need `kubernetes.io/cluster/<CLUSTER_NAME>` tags for node registration.
8. **EKS Auto Mode Is the Simplest Path**: `compute_config = { enabled = true, node_pools = ["general-purpose"] }` requires no node group definitions at all.
9. **Karpenter Uses Pod Identity, Not IRSA**: The `karpenter` submodule creates a Pod Identity association by default; deploy the `eks-pod-identity-agent` add-on and do not add an IRSA annotation to the Karpenter service account.
10. **KMS Encryption Semantics**: `encryption_config = {}` (default) uses/creates a customer-managed KMS key; `encryption_config = null` explicitly falls back to the AWS-managed key; secrets encryption cannot be fully disabled.
11. **`desired_size` Changes Are Ignored by Terraform**: The module ignores lifecycle changes to `desired_size` on node groups so external autoscalers (Karpenter, Cluster Autoscaler) can manage it without Terraform drift.
12. **Karpenter Discovery Tags**: When using Karpenter, tag subnets and the cluster security group with `karpenter.sh/discovery = <cluster_name>`.
13. **Version Pin the Module**: Use `version = "~> 21.0"` to avoid unexpected upgrades; check the registry for the current patch release.
14. **Minimum Requirements**: Terraform `>= 1.5.7`, AWS provider `>= 6.52`.
15. **EFA Minimum Nodes**: EFA node groups require at least 2 nodes; placement groups are auto-configured when `enable_efa_support = true`.
16. **`aws-auth` ConfigMap Sub-module Removed**: If a project still needs it, pin the module to `~> 20.0` instead of upgrading to v21.
