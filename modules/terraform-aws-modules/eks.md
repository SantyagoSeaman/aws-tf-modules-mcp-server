# Terraform AWS EKS Module

## Module Information

- **Module Name**: `eks`
- **Source**: `terraform-aws-modules/eks/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-eks
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest
- **Latest Version**: 21.15.1
- **Purpose**: Creates Amazon EKS clusters with comprehensive support for EKS Auto Mode, managed/self-managed node groups, Fargate profiles, hybrid on-premises nodes, and Karpenter autoscaling
- **Service**: AWS EKS (Elastic Kubernetes Service)
- **Category**: Container Orchestration, Compute, Kubernetes
- **Keywords**: eks, kubernetes, k8s, managed-node-group, fargate, karpenter, irsa, oidc, eks-auto-mode, hybrid-nodes, spot-instances, bottlerocket, al2023, efa, eks-addons, kms-encryption, access-entry, control-plane
- **Use For**: Running containerized applications at scale, microservices deployment on Kubernetes, cloud-native application hosting, CI/CD pipeline execution, machine learning model training and serving, big data processing workloads, multi-tenant Kubernetes platforms, hybrid cloud deployments, cost-optimized compute with Spot instances, serverless workloads with Fargate, high-performance computing with EFA

## Description

This Terraform module provides comprehensive management of AWS Elastic Kubernetes Service (EKS) clusters, enabling creation of production-ready Kubernetes environments on AWS. The module supports multiple compute options: EKS Auto Mode for fully managed infrastructure where AWS handles both control plane and compute nodes, EKS managed node groups for simplified node lifecycle management with automated updates and patching, self-managed node groups for maximum control over instance configuration, Fargate profiles for serverless container execution, and hybrid nodes for on-premises or edge deployments connected to EKS control plane.

The module handles the complete EKS cluster lifecycle including control plane configuration with provisioned capacity tiers (standard through tier-4xl for production workloads), IAM role management, security group setup, KMS-based secret encryption, and add-on deployment. It provides pre-configured patterns for cluster access management via access entries (replacing aws-auth ConfigMap), automatic OIDC provider setup for IAM Roles for Service Accounts (IRSA), Pod Identity associations, and flexible authentication modes (CONFIG_MAP, API, or API_AND_CONFIG_MAP).

The module includes six specialized submodules: eks-managed-node-group for AWS-managed instances with spot/on-demand support, self-managed-node-group for custom AutoScaling Groups with full launch template control, fargate-profile for serverless execution with namespace/label selectors, karpenter for dynamic autoscaling infrastructure, hybrid-node-role for on-premises node authentication via SSM or IAM Roles Anywhere, and kms for encryption key management. All submodules can be used independently or composed together for complex cluster architectures.

## Key Features

- **Six Specialized Submodules**: Modular architecture with eks-managed-node-group, self-managed-node-group, fargate-profile, karpenter, hybrid-node-role, and kms submodules
- **EKS Auto Mode**: Fully managed infrastructure where AWS manages both control plane and compute nodes with general-purpose or system node pools
- **Provisioned Control Plane**: Enhanced capacity tiers (standard, tier-xl, tier-2xl, tier-4xl) for production workloads requiring guaranteed API server performance
- **Managed Node Groups**: AWS-managed EC2 instances with automated provisioning, lifecycle management, auto-repair, and rolling updates
- **Self-Managed Node Groups**: Complete control over node configuration with custom launch templates, AMIs, and AutoScaling policies
- **Fargate Profiles**: Serverless container execution with namespace/label selectors and automated pod execution roles
- **Hybrid Node Support**: On-premises or edge Kubernetes nodes connected to EKS control plane via SSM or IAM Roles Anywhere
- **Kubernetes 1.33 Support**: Latest Kubernetes version with EKS Capabilities feature support
- **Access Entries**: Fine-grained cluster access control replacing aws-auth ConfigMap with better security and auditability
- **IRSA (IAM Roles for Service Accounts)**: Automatic OIDC provider creation for pod-level IAM permissions
- **KMS Encryption**: Auto-created or bring-your-own-key encryption for Kubernetes secrets at rest
- **EKS Add-ons**: Managed deployment of VPC-CNI, CoreDNS, kube-proxy, EBS CSI driver with `before_compute` dependency ordering
- **Spot and On-Demand Mix**: Cost optimization through mixed capacity types in node groups
- **EFA Support**: Elastic Fabric Adapter for high-performance computing with automatic placement group configuration
- **Multiple AMI Types**: AL2023_x86_64_STANDARD, Bottlerocket, Ubuntu, and custom AMIs
- **CloudWatch Integration**: Control plane logging (audit, api, authenticator) with configurable retention
- **Security Defaults**: Public endpoint disabled by default, KMS encryption enabled, separate control plane subnets supported

## Main Use Cases

1. **Microservices Deployment**: Run containerized microservices with service mesh integration
2. **CI/CD Pipeline Execution**: Execute build and deployment pipelines in ephemeral containers
3. **Machine Learning Workloads**: Train and serve ML models with GPU-enabled node groups
4. **Big Data Processing**: Run Spark, Hadoop, and data processing frameworks on Kubernetes
5. **Event-Driven Applications**: Deploy serverless event processors using Fargate
6. **Cost-Optimized Compute**: Leverage Spot instances for fault-tolerant batch workloads
7. **High-Performance Computing**: Run HPC workloads with EFA-enabled instance types
8. **Multi-Tenant Platforms**: Build shared Kubernetes platforms with namespace isolation
9. **Hybrid Cloud Deployments**: Connect on-premises nodes to EKS control plane
10. **Auto-Scaling Applications**: Dynamically scale workloads with Karpenter or Cluster Autoscaler

## Submodules

### 1. eks-managed-node-group
- **Purpose**: Create AWS-managed node groups with automated lifecycle management, auto-repair, and rolling updates
- **Source**: `terraform-aws-modules/eks/aws//modules/eks-managed-node-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/eks-managed-node-group
- **Key Features**: Launch template support, Spot/On-Demand instances, EFA support, auto-scaling with `update_config.update_strategy`
- **Use Cases**: Production workloads, managed updates, simplified operations, multi-AZ deployments

### 2. self-managed-node-group
- **Purpose**: Create self-managed node groups with complete control over AutoScaling Groups and launch templates
- **Source**: `terraform-aws-modules/eks/aws//modules/self-managed-node-group`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/self-managed-node-group
- **Key Features**: Custom launch templates, user data scripts, AL2023/Bottlerocket AMIs, scaling policies
- **Use Cases**: Custom configurations, specialized workloads, advanced customization, legacy compatibility

### 3. fargate-profile
- **Purpose**: Create Fargate profiles for serverless container execution with namespace/label selectors
- **Source**: `terraform-aws-modules/eks/aws//modules/fargate-profile`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/fargate-profile
- **Key Features**: Namespace selectors, label selectors, automated pod execution role, subnet configuration
- **Use Cases**: Serverless workloads, batch processing, kube-system components, cost-efficient small workloads

### 4. karpenter
- **Purpose**: Create IAM resources and infrastructure for Karpenter cluster autoscaler
- **Source**: `terraform-aws-modules/eks/aws//modules/karpenter`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/karpenter
- **Key Features**: IAM roles, Pod Identity, SQS queue for Spot termination, EventBridge rules
- **Use Cases**: Dynamic autoscaling, diverse instance types, cost optimization, rapid scaling

### 5. hybrid-node-role
- **Purpose**: Create IAM roles for on-premises or edge nodes connecting to EKS control plane
- **Source**: `terraform-aws-modules/eks/aws//modules/hybrid-node-role`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/hybrid-node-role
- **Key Features**: SSM authentication, IAM Roles Anywhere support, edge computing integration
- **Use Cases**: Hybrid cloud, edge deployments, on-premises Kubernetes nodes, distributed infrastructure

### 6. kms
- **Purpose**: Create and manage KMS keys for cluster secret encryption
- **Source**: `terraform-aws-modules/eks/aws//modules/kms`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest/submodules/kms
- **Key Features**: Auto-rotation, key policies, alias management, bring-your-own-key support
- **Use Cases**: Secret encryption at rest, compliance requirements, key management separation

## Submodule 1: eks-managed-node-group

### Description

The eks-managed-node-group submodule creates AWS-managed node groups that automate the provisioning and lifecycle management of EC2 instances for EKS clusters. AWS handles node updates, patching, and termination, automatically draining pods during updates to ensure application availability. This submodule simplifies operations by managing Auto Scaling Groups, launch templates, and IAM roles while providing flexibility for instance type selection, capacity types (On-Demand/Spot), and custom configurations.

### Key Features

- AWS-managed node lifecycle with automated updates and patching
- Support for custom launch templates with user data
- Configurable instance types and capacity types (On-Demand/Spot)
- Auto Scaling Group integration with min/max/desired size
- Kubernetes labels and taints for pod scheduling
- Custom AMI support including Amazon Linux 2, Bottlerocket, Ubuntu
- IAM role and security group management
- Multi-AZ deployment support
- Remote access configuration with SSH keys
- Disk size and type customization

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the EKS managed node group |
| `cluster_name` | `string` | `""` | Name of the EKS cluster |
| `cluster_version` | `string` | `null` | Kubernetes version for the node group |
| `subnet_ids` | `list(string)` | `[]` | List of subnet IDs for node placement |
| `min_size` | `number` | `1` | Minimum number of nodes |
| `max_size` | `number` | `3` | Maximum number of nodes |
| `desired_size` | `number` | `1` | Desired number of nodes |
| `instance_types` | `list(string)` | `["t3.medium"]` | List of instance types |
| `capacity_type` | `string` | `"ON_DEMAND"` | Capacity type (ON_DEMAND or SPOT) |
| `labels` | `map(string)` | `{}` | Kubernetes labels for nodes |
| `taints` | `list(object)` | `[]` | Kubernetes taints for nodes |

### Main Outputs

| Output | Description |
|--------|-------------|
| `node_group_arn` | ARN of the EKS managed node group |
| `node_group_id` | ID of the EKS managed node group |
| `node_group_status` | Status of the EKS managed node group |
| `iam_role_arn` | ARN of the IAM role |
| `node_group_autoscaling_group_names` | List of Auto Scaling Group names |
| `launch_template_id` | ID of the launch template |

### Usage Example

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  cluster_name    = "production-eks"
  cluster_version = "1.33"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Enable cluster access
  enable_cluster_creator_admin_permissions = true

  # Managed node groups
  eks_managed_node_groups = {
    # General purpose node group
    general = {
      name           = "general-purpose"
      instance_types = ["t3.large"]
      capacity_type  = "ON_DEMAND"

      min_size     = 2
      max_size     = 10
      desired_size = 3

      labels = {
        role        = "general"
        environment = "production"
      }

      tags = {
        NodeGroup = "general-purpose"
      }
    }

    # Spot instance node group for batch workloads
    spot_batch = {
      name           = "spot-batch"
      instance_types = ["t3.large", "t3a.large", "t3.xlarge"]
      capacity_type  = "SPOT"

      min_size     = 0
      max_size     = 20
      desired_size = 0

      labels = {
        role     = "batch"
        spot     = "true"
      }

      taints = [
        {
          key    = "batch"
          value  = "true"
          effect = "NoSchedule"
        }
      ]

      tags = {
        NodeGroup = "spot-batch"
      }
    }

    # GPU-enabled node group for ML workloads
    gpu = {
      name           = "gpu-ml"
      instance_types = ["g4dn.xlarge"]
      ami_type       = "AL2_x86_64_GPU"

      min_size     = 0
      max_size     = 5
      desired_size = 1

      labels = {
        role        = "ml"
        gpu         = "true"
        nvidia-gpu  = "true"
      }

      taints = [
        {
          key    = "nvidia.com/gpu"
          value  = "true"
          effect = "NoSchedule"
        }
      ]

      tags = {
        NodeGroup = "gpu-ml"
      }
    }
  }

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

# Standalone managed node group
module "separate_node_group" {
  source = "terraform-aws-modules/eks/aws//modules/eks-managed-node-group"

  name            = "additional-nodes"
  cluster_name    = module.eks.cluster_name
  cluster_version = "1.33"

  subnet_ids = module.vpc.private_subnets

  # Custom launch template
  create_launch_template = true
  launch_template_name   = "additional-nodes-lt"

  # Bottlerocket OS
  ami_type = "BOTTLEROCKET_x86_64"

  instance_types = ["m5.xlarge"]
  capacity_type  = "ON_DEMAND"

  min_size     = 1
  max_size     = 5
  desired_size = 2

  # Custom user data
  enable_bootstrap_user_data = true
  bootstrap_extra_args       = "--container-runtime containerd"

  # Disk configuration
  block_device_mappings = {
    xvda = {
      device_name = "/dev/xvda"
      ebs = {
        volume_size           = 100
        volume_type           = "gp3"
        iops                  = 3000
        throughput            = 150
        delete_on_termination = true
      }
    }
  }

  labels = {
    os   = "bottlerocket"
    role = "application"
  }

  tags = {
    NodeGroup = "additional"
  }
}
```

## Submodule 2: self-managed-node-group

### Description

The self-managed-node-group submodule creates EC2-based node groups that provide complete control over instance configuration, launch templates, and user data scripts. Unlike managed node groups, self-managed groups require manual management of node lifecycle, updates, and scaling but offer maximum flexibility for custom configurations, legacy compatibility, and specialized workloads. This submodule creates an Auto Scaling Group, launch template, IAM role, and security group with full customization capabilities.

### Key Features

- Complete control over EC2 instance configuration
- Custom launch templates with advanced settings
- User data script customization for bootstrapping
- Support for any EC2 AMI including custom builds
- Auto Scaling Group with detailed configuration
- Mixed instance types and purchase options
- Placement group support for HPC workloads
- Instance metadata service configuration
- Detailed monitoring and CloudWatch integration

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the self-managed node group |
| `cluster_name` | `string` | `""` | Name of the EKS cluster |
| `kubernetes_version` | `string` | `null` | Kubernetes version for node configuration |
| `subnet_ids` | `list(string)` | `[]` | List of subnet IDs for node placement |
| `min_size` | `number` | `0` | Minimum number of nodes |
| `max_size` | `number` | `3` | Maximum number of nodes |
| `desired_size` | `number` | `1` | Desired number of nodes |
| `instance_type` | `string` | `"t3.medium"` | EC2 instance type |
| `ami_id` | `string` | `""` | AMI ID for instances |
| `user_data_template_path` | `string` | `""` | Path to custom user data template |

### Main Outputs

| Output | Description |
|--------|-------------|
| `autoscaling_group_id` | ID of the Auto Scaling Group |
| `autoscaling_group_arn` | ARN of the Auto Scaling Group |
| `iam_role_arn` | ARN of the IAM role |
| `launch_template_id` | ID of the launch template |
| `security_group_id` | ID of the security group |

### Usage Example

```hcl
module "self_managed_nodes" {
  source = "terraform-aws-modules/eks/aws//modules/self-managed-node-group"

  name                = "custom-nodes"
  cluster_name        = module.eks.cluster_name
  kubernetes_version  = "1.33"

  subnet_ids = module.vpc.private_subnets

  # Auto Scaling configuration
  min_size     = 2
  max_size     = 10
  desired_size = 3

  # Instance configuration
  instance_type = "m5.large"

  # Use latest EKS optimized AMI
  use_latest_ami_release_version = true
  ami_type                       = "AL2023_x86_64_STANDARD"

  # Custom user data
  pre_bootstrap_user_data = <<-EOT
    #!/bin/bash
    # Install custom packages
    yum install -y amazon-cloudwatch-agent

    # Custom configurations
    echo "Custom node configuration"
  EOT

  post_bootstrap_user_data = <<-EOT
    #!/bin/bash
    # Post-bootstrap configurations
    echo "Node bootstrapped successfully"
  EOT

  # Enable detailed monitoring
  enable_monitoring = true

  # Instance metadata service v2
  metadata_options = {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  # Block device configuration
  block_device_mappings = {
    xvda = {
      device_name = "/dev/xvda"
      ebs = {
        volume_size           = 100
        volume_type           = "gp3"
        iops                  = 3000
        encrypted             = true
        delete_on_termination = true
      }
    }
  }

  # IAM instance profile
  create_iam_instance_profile = true
  iam_role_additional_policies = {
    AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    CloudWatchAgentServer        = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  }

  tags = {
    NodeType = "self-managed"
    Purpose  = "custom-workloads"
  }
}
```

## Submodule 3: fargate-profile

### Description

The fargate-profile submodule creates Fargate profiles that enable serverless container execution on EKS without managing EC2 instances. Fargate automatically provisions and scales compute resources based on pod requirements, charging only for the resources consumed by running pods. This submodule configures namespace and label selectors to determine which pods run on Fargate, manages IAM roles for pod execution, and handles subnet selection for Fargate infrastructure.

### Key Features

- Serverless container execution without EC2 management
- Namespace and label-based pod selectors
- Automatic resource provisioning and scaling
- Pay-per-pod pricing model
- IAM role management for pod execution
- Subnet configuration for Fargate ENIs
- Support for multiple selectors per profile
- Integration with EKS cluster security

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | `""` | Name of the Fargate profile |
| `cluster_name` | `string` | `""` | Name of the EKS cluster |
| `subnet_ids` | `list(string)` | `[]` | List of subnet IDs for Fargate |
| `selectors` | `list(object)` | `[]` | Namespace and label selectors for pods |
| `create_iam_role` | `bool` | `true` | Whether to create IAM role |
| `iam_role_arn` | `string` | `null` | Existing IAM role ARN to use |
| `tags` | `map(string)` | `{}` | Tags for the Fargate profile |

### Main Outputs

| Output | Description |
|--------|-------------|
| `fargate_profile_arn` | ARN of the Fargate profile |
| `fargate_profile_id` | ID of the Fargate profile |
| `fargate_profile_status` | Status of the Fargate profile |
| `iam_role_arn` | ARN of the IAM role |

### Usage Example

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  cluster_name    = "fargate-eks"
  cluster_version = "1.33"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Fargate profiles
  fargate_profiles = {
    # Default profile for kube-system
    kube_system = {
      name = "kube-system"
      selectors = [
        {
          namespace = "kube-system"
          labels = {
            k8s-app = "kube-dns"
          }
        }
      ]

      # Use only private subnets for Fargate
      subnet_ids = module.vpc.private_subnets

      tags = {
        Profile = "kube-system"
      }
    }

    # Application profile
    applications = {
      name = "applications"
      selectors = [
        {
          namespace = "app-*"
        },
        {
          namespace = "backend"
          labels = {
            fargate = "enabled"
          }
        }
      ]

      subnet_ids = module.vpc.private_subnets

      tags = {
        Profile = "applications"
      }
    }

    # Batch processing profile
    batch = {
      name = "batch-processing"
      selectors = [
        {
          namespace = "batch"
        }
      ]

      subnet_ids = module.vpc.private_subnets

      # Custom IAM role
      create_iam_role = true
      iam_role_additional_policies = {
        S3Access = aws_iam_policy.batch_s3_access.arn
      }

      tags = {
        Profile = "batch"
      }
    }
  }

  tags = {
    Environment = "production"
  }
}

# Standalone Fargate profile
module "separate_fargate_profile" {
  source = "terraform-aws-modules/eks/aws//modules/fargate-profile"

  name         = "ml-workloads"
  cluster_name = module.eks.cluster_name

  subnet_ids = module.vpc.private_subnets

  selectors = [
    {
      namespace = "ml-training"
      labels = {
        compute = "fargate"
        workload = "ml"
      }
    },
    {
      namespace = "ml-inference"
    }
  ]

  tags = {
    Workload = "ML"
    Compute  = "Fargate"
  }
}
```

## Submodule 4: karpenter

### Description

The karpenter submodule creates the AWS infrastructure required for Karpenter, an open-source Kubernetes cluster autoscaler that provisions right-sized compute resources based on pod requirements. Unlike traditional cluster autoscaling that manages node groups, Karpenter directly provisions individual instances, enabling faster scaling and better resource utilization. This submodule sets up IAM roles, Pod Identity associations, SQS queues for Spot termination handling, and EventBridge rules for integration with AWS services.

### Key Features

- IAM role creation for Karpenter controller
- Node IAM role with necessary permissions
- Pod Identity association for controller authentication
- SQS queue for Spot instance interruption notifications
- EventBridge rules for EC2 state changes
- Access entry configuration for node registration
- Support for reusing existing IAM roles
- Native Spot termination handling

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `cluster_name` | `string` | `""` | Name of the EKS cluster |
| `create_node_iam_role` | `bool` | `true` | Whether to create node IAM role |
| `node_iam_role_arn` | `string` | `null` | Existing node IAM role ARN |
| `node_iam_role_additional_policies` | `map(string)` | `{}` | Additional IAM policies for nodes |
| `enable_spot_termination` | `bool` | `true` | Enable native Spot termination handling |
| `queue_name` | `string` | `null` | Custom name for SQS queue |

### Main Outputs

| Output | Description |
|--------|-------------|
| `iam_role_arn` | ARN of the Karpenter controller IAM role |
| `iam_role_name` | Name of the Karpenter controller IAM role |
| `node_iam_role_arn` | ARN of the node IAM role |
| `node_iam_role_name` | Name of the node IAM role |
| `queue_arn` | ARN of the SQS interruption queue |
| `queue_name` | Name of the SQS interruption queue |
| `node_access_entry_arn` | ARN of the node access entry |

### Usage Examples

#### Example 1: Default Karpenter Setup

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  cluster_name    = "karpenter-eks"
  cluster_version = "1.33"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  enable_cluster_creator_admin_permissions = true

  tags = {
    Environment = "production"
  }
}

# Karpenter module
module "karpenter" {
  source = "terraform-aws-modules/eks/aws//modules/karpenter"

  cluster_name = module.eks.cluster_name

  # Additional IAM policies for nodes
  node_iam_role_additional_policies = {
    AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  }

  tags = {
    Environment = "production"
  }
}

# Karpenter Helm installation
resource "helm_release" "karpenter" {
  namespace        = "karpenter"
  create_namespace = true

  name       = "karpenter"
  repository = "oci://public.ecr.aws/karpenter"
  chart      = "karpenter"
  version    = "1.0.0"

  values = [
    <<-EOT
    settings:
      clusterName: ${module.eks.cluster_name}
      clusterEndpoint: ${module.eks.cluster_endpoint}
      interruptionQueue: ${module.karpenter.queue_name}
    serviceAccount:
      annotations:
        eks.amazonaws.com/role-arn: ${module.karpenter.iam_role_arn}
    EOT
  ]

  depends_on = [module.eks]
}

# Karpenter NodePool
resource "kubectl_manifest" "karpenter_node_pool" {
  yaml_body = <<-YAML
    apiVersion: karpenter.sh/v1
    kind: NodePool
    metadata:
      name: default
    spec:
      template:
        spec:
          requirements:
            - key: kubernetes.io/arch
              operator: In
              values: ["amd64"]
            - key: kubernetes.io/os
              operator: In
              values: ["linux"]
            - key: karpenter.sh/capacity-type
              operator: In
              values: ["spot", "on-demand"]
            - key: karpenter.k8s.aws/instance-category
              operator: In
              values: ["c", "m", "r"]
            - key: karpenter.k8s.aws/instance-generation
              operator: Gt
              values: ["2"]
          nodeClassRef:
            group: karpenter.k8s.aws
            kind: EC2NodeClass
            name: default
      limits:
        cpu: 1000
      disruption:
        consolidationPolicy: WhenEmpty
        consolidateAfter: 30s
  YAML

  depends_on = [helm_release.karpenter]
}

# Karpenter EC2NodeClass
resource "kubectl_manifest" "karpenter_node_class" {
  yaml_body = <<-YAML
    apiVersion: karpenter.k8s.aws/v1
    kind: EC2NodeClass
    metadata:
      name: default
    spec:
      amiFamily: AL2
      role: ${module.karpenter.node_iam_role_name}
      subnetSelectorTerms:
        - tags:
            karpenter.sh/discovery: ${module.eks.cluster_name}
      securityGroupSelectorTerms:
        - tags:
            karpenter.sh/discovery: ${module.eks.cluster_name}
      amiSelectorTerms:
        - alias: al2@latest
  YAML

  depends_on = [helm_release.karpenter]
}
```

#### Example 2: Karpenter with Existing Node Role

```hcl
module "karpenter" {
  source = "terraform-aws-modules/eks/aws//modules/karpenter"

  cluster_name = module.eks.cluster_name

  # Reuse existing node IAM role from managed node group
  create_node_iam_role = false
  node_iam_role_arn    = module.eks.eks_managed_node_groups["initial"].iam_role_arn

  # Custom queue name
  queue_name = "karpenter-interruption-${module.eks.cluster_name}"

  tags = {
    Component = "Karpenter"
  }
}
```

## Main Module: EKS Cluster

### Description

The main EKS module provides comprehensive creation and configuration of AWS Elastic Kubernetes Service clusters with complete control over cluster settings, compute resources, networking, and security. This module handles the entire EKS cluster lifecycle including control plane creation, IAM role management, security group configuration, cluster add-ons, and various node group types.

### Key Features

- Complete EKS cluster lifecycle management
- Multiple node group types (managed, self-managed, Fargate)
- Cluster access management with authentication modes
- OIDC provider for IRSA
- Pod Identity associations
- Cluster encryption with KMS
- VPC and subnet integration
- Security group configuration
- EKS add-ons management
- CloudWatch logging integration
- IPv4 and IPv6 support

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `cluster_name` | `string` | `""` | Name of the EKS cluster (required) |
| `cluster_version` | `string` | `null` | Kubernetes version (e.g., "1.33") |
| `vpc_id` | `string` | `""` | VPC ID where cluster will be deployed (required) |
| `subnet_ids` | `list(string)` | `[]` | Subnets for node provisioning (must have proper k8s tags) |
| `control_plane_subnet_ids` | `list(string)` | `[]` | Separate subnets for control plane ENIs |
| `cluster_endpoint_public_access` | `bool` | `false` | Enable public API endpoint access |
| `cluster_endpoint_private_access` | `bool` | `true` | Enable private API endpoint access |
| `enable_cluster_creator_admin_permissions` | `bool` | `false` | Grant admin permissions to Terraform identity |
| `authentication_mode` | `string` | `"API_AND_CONFIG_MAP"` | Authentication mode (API, CONFIG_MAP, or API_AND_CONFIG_MAP) |
| `create_kms_key` | `bool` | `true` | Create KMS key for secret encryption |
| `cluster_enabled_log_types` | `list(string)` | `["audit","api","authenticator"]` | Control plane log types |
| `compute_config` | `object` | `null` | EKS Auto Mode config (enabled, node_pools) |
| `eks_managed_node_groups` | `map(any)` | `{}` | Map of managed node group definitions |
| `self_managed_node_groups` | `map(any)` | `{}` | Map of self-managed node group definitions |
| `fargate_profiles` | `map(any)` | `{}` | Map of Fargate profile definitions |
| `access_entries` | `map(any)` | `{}` | Map of access entries for cluster access |

### Main Outputs

| Output | Description |
|--------|-------------|
| `cluster_name` | The EKS cluster identifier |
| `cluster_arn` | Full ARN reference for the cluster |
| `cluster_endpoint` | Kubernetes API server endpoint URL |
| `cluster_version` | Kubernetes version running on the cluster |
| `cluster_certificate_authority_data` | Base64-encoded certificate for authentication |
| `cluster_iam_role_arn` | IAM role used by the EKS cluster |
| `cluster_security_group_id` | Security group attached to control plane |
| `node_security_group_id` | Security group ID for node communication |
| `oidc_provider_arn` | OIDC provider ARN for IRSA |
| `cluster_oidc_issuer_url` | OIDC issuer URL for the cluster |
| `eks_managed_node_groups` | Map of managed node group attributes |
| `self_managed_node_groups` | Map of self-managed node group attributes |
| `fargate_profiles` | Map of Fargate profile attributes |
| `cluster_addons` | Map of cluster add-on attributes |

### Usage Examples

#### Example 1: Complete Production EKS Cluster

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  cluster_name    = "production-eks"
  cluster_version = "1.33"

  # VPC configuration
  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.intra_subnets

  # Cluster endpoint access
  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  # Cluster access configuration
  enable_cluster_creator_admin_permissions = true
  authentication_mode                      = "API_AND_CONFIG_MAP"

  # Cluster encryption
  cluster_encryption_config = {
    resources        = ["secrets"]
    provider_key_arn = aws_kms_key.eks.arn
  }

  # CloudWatch logging
  cluster_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  # EKS add-ons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent              = true
      before_compute           = true
      service_account_role_arn = module.vpc_cni_irsa.iam_role_arn
      configuration_values = jsonencode({
        env = {
          ENABLE_PREFIX_DELEGATION = "true"
          ENABLE_POD_ENI           = "true"
          POD_SECURITY_GROUP_ENFORCING_MODE = "standard"
        }
        enableNetworkPolicy = "true"
      })
    }
    aws-ebs-csi-driver = {
      most_recent              = true
      service_account_role_arn = module.ebs_csi_irsa.iam_role_arn
    }
  }

  # EKS managed node groups
  eks_managed_node_groups = {
    # Critical system workloads
    system = {
      name           = "system"
      instance_types = ["m5.large"]
      capacity_type  = "ON_DEMAND"

      min_size     = 2
      max_size     = 4
      desired_size = 2

      labels = {
        role = "system"
      }

      taints = [
        {
          key    = "CriticalAddonsOnly"
          value  = "true"
          effect = "NoSchedule"
        }
      ]

      tags = {
        NodeGroup = "system"
      }
    }

    # Application workloads
    applications = {
      name           = "applications"
      instance_types = ["m5.xlarge", "m5a.xlarge", "m5n.xlarge"]
      capacity_type  = "ON_DEMAND"

      min_size     = 3
      max_size     = 20
      desired_size = 5

      labels = {
        role = "application"
      }

      tags = {
        NodeGroup = "applications"
      }
    }

    # Spot instances for batch workloads
    batch = {
      name           = "batch"
      instance_types = ["m5.2xlarge", "m5a.2xlarge", "m5n.2xlarge"]
      capacity_type  = "SPOT"

      min_size     = 0
      max_size     = 50
      desired_size = 0

      labels = {
        role = "batch"
        spot = "true"
      }

      taints = [
        {
          key    = "spot"
          value  = "true"
          effect = "NoSchedule"
        }
      ]

      tags = {
        NodeGroup = "batch"
      }
    }
  }

  # Fargate profiles
  fargate_profiles = {
    kube_system = {
      name = "kube-system"
      selectors = [
        {
          namespace = "kube-system"
        }
      ]
    }
  }

  # Cluster access entries
  access_entries = {
    admin = {
      principal_arn = "arn:aws:iam::123456789012:role/AdminRole"
      policy_associations = {
        admin = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
      }
    }
  }

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

# KMS key for cluster encryption
resource "aws_kms_key" "eks" {
  description             = "EKS cluster encryption key"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "eks-cluster-encryption"
  }
}

# VPC CNI IRSA
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

# EBS CSI IRSA
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

#### Example 2: EKS with Auto Mode

```hcl
module "eks_auto_mode" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  cluster_name    = "auto-mode-eks"
  cluster_version = "1.33"

  # VPC configuration
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Enable Auto Mode (fully managed infrastructure)
  # AWS manages both control plane and compute nodes
  compute_config = {
    enabled    = true
    node_pools = ["general-purpose"]  # or ["system"] for system workloads only
  }

  # Cluster access
  enable_cluster_creator_admin_permissions = true

  # Auto Mode handles node provisioning automatically
  # No need to define eks_managed_node_groups or self_managed_node_groups

  tags = {
    Mode = "Auto"
  }
}
```

#### Example 3: EKS with Karpenter

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  cluster_name    = "karpenter-cluster"
  cluster_version = "1.33"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  enable_cluster_creator_admin_permissions = true

  # Minimal initial node group for Karpenter controller
  eks_managed_node_groups = {
    karpenter = {
      name           = "karpenter-bootstrap"
      instance_types = ["t3.medium"]

      min_size     = 2
      max_size     = 3
      desired_size = 2

      labels = {
        role = "karpenter"
      }

      taints = [
        {
          key    = "karpenter.sh/controller"
          value  = "true"
          effect = "NoSchedule"
        }
      ]
    }
  }

  tags = {
    "karpenter.sh/discovery" = "karpenter-cluster"
  }
}

# Tag subnets for Karpenter discovery
resource "aws_ec2_tag" "karpenter_subnet_tags" {
  for_each = toset(module.vpc.private_subnets)

  resource_id = each.value
  key         = "karpenter.sh/discovery"
  value       = module.eks.cluster_name
}

# Tag security groups for Karpenter discovery
resource "aws_ec2_tag" "karpenter_sg_tags" {
  resource_id = module.eks.cluster_security_group_id
  key         = "karpenter.sh/discovery"
  value       = module.eks.cluster_name
}

# Karpenter module
module "karpenter" {
  source = "terraform-aws-modules/eks/aws//modules/karpenter"

  cluster_name = module.eks.cluster_name

  enable_spot_termination = true

  node_iam_role_additional_policies = {
    AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  }
}
```

## Best Practices

### Cluster Design and Architecture

1. **Use Latest Kubernetes Version**: Deploy clusters on the latest stable Kubernetes version supported by EKS for security patches and new features.
2. **Plan for Multi-AZ Deployment**: Distribute control plane ENIs and node groups across at least three availability zones for high availability.
3. **Separate Node Groups by Workload**: Create distinct node groups for system components, applications, and batch workloads with appropriate taints and labels.
4. **Use Private Subnets for Nodes**: Deploy all worker nodes in private subnets and use NAT gateways or VPC endpoints for outbound connectivity.
5. **Enable Both Public and Private Endpoints**: Set `cluster_endpoint_public_access = true` and `cluster_endpoint_private_access = true` for flexible access patterns.
6. **Plan CIDR Blocks Carefully**: Ensure VPC has sufficient IP addresses for pod networking (consider using VPC CNI prefix delegation or secondary CIDRs).
7. **Use Dedicated Subnets for Control Plane**: Specify `control_plane_subnet_ids` separate from node subnets for better network isolation.
8. **Document Cluster Architecture**: Maintain clear documentation of node groups, add-ons, IRSA roles, and networking configuration.

### Node Group Management

1. **Use Managed Node Groups for Standard Workloads**: Prefer EKS managed node groups for simplified operations and automated updates.
2. **Implement Auto Scaling**: Configure appropriate `min_size`, `max_size`, and `desired_size` based on workload patterns.
3. **Mix Capacity Types**: Use On-Demand instances for critical workloads and Spot instances for fault-tolerant batch jobs.
4. **Use Multiple Instance Types**: Specify multiple instance types in `instance_types` for better Spot instance availability.
5. **Apply Taints for Specialized Nodes**: Use taints to dedicate node groups for specific workloads (GPU, batch, system).
6. **Use Launch Templates**: Create custom launch templates for advanced configurations like larger disk sizes or custom user data.
7. **Deploy Karpenter for Dynamic Scaling**: Implement Karpenter for workloads requiring rapid scaling or diverse instance type selection.
8. **Right-Size Node Groups**: Choose instance types that balance CPU, memory, and network performance based on application requirements.

### Security and Access Control

1. **Enable Cluster Encryption**: Use KMS encryption for cluster secrets with `cluster_encryption_config`.
2. **Use IAM Roles for Service Accounts**: Implement IRSA for all pods requiring AWS permissions instead of node-level IAM roles.
3. **Enable Cluster Creator Admin**: Set `enable_cluster_creator_admin_permissions = true` for initial cluster access.
4. **Use Access Entries**: Define explicit access entries with appropriate policies rather than relying on aws-auth ConfigMap.
5. **Implement Network Policies**: Enable VPC CNI network policies to control pod-to-pod communication.
6. **Use Pod Security Standards**: Implement Pod Security admission controller for cluster-wide security policies.
7. **Enable CloudWatch Logs**: Configure all control plane log types for security auditing and troubleshooting.
8. **Rotate Credentials**: Regularly rotate IAM role credentials and update access entries.
9. **Use Private Endpoints**: For production clusters, disable public endpoint access after initial setup if possible.
10. **Implement Security Groups for Pods**: Use security groups for pods feature to apply EC2 security groups directly to pods.

### Add-ons and Extensions

1. **Use Latest Add-on Versions**: Enable `most_recent = true` for EKS add-ons to receive updates automatically.
2. **Deploy Core Add-ons**: Always deploy vpc-cni, kube-proxy, and coredns for cluster functionality.
3. **Install EBS CSI Driver**: Deploy aws-ebs-csi-driver add-on for persistent volume support.
4. **Use IRSA for Add-ons**: Configure `service_account_role_arn` for add-ons that require AWS permissions.
5. **Deploy Add-ons Before Compute**: Set `before_compute = true` for vpc-cni to ensure networking is ready.
6. **Enable Prefix Delegation**: Use VPC CNI prefix delegation to increase pod density per node.
7. **Configure Add-on Settings**: Customize add-on configurations using `configuration_values` for optimal performance.
8. **Monitor Add-on Health**: Track add-on status and version through cluster add-ons outputs.

### Cost Optimization

1. **Use Spot Instances**: Leverage Spot instances for fault-tolerant workloads to reduce costs by up to 90%.
2. **Right-Size Nodes**: Use Karpenter or horizontal pod autoscaler to match capacity with demand.
3. **Scale to Zero**: Configure node groups with `min_size = 0` for workloads that don't run continuously.
4. **Use Fargate for Small Workloads**: Consider Fargate for low-traffic services to avoid paying for idle nodes.
5. **Enable Cluster Autoscaler**: Deploy cluster autoscaler or Karpenter to automatically adjust node count.
6. **Use Graviton Instances**: Consider ARM64-based Graviton instances for cost-performance optimization.
7. **Implement Pod Resource Limits**: Set resource requests and limits to enable efficient bin-packing.
8. **Use Savings Plans**: Purchase EC2 savings plans or reserved instances for predictable workloads.
9. **Monitor Costs**: Use AWS Cost Explorer and tag resources for cost allocation and tracking.
10. **Clean Up Unused Resources**: Regularly audit and remove unused node groups, load balancers, and persistent volumes.

### High Availability and Resilience

1. **Multi-AZ Node Distribution**: Ensure node groups span multiple availability zones with balanced instance counts.
2. **Use Pod Disruption Budgets**: Define PDBs for critical applications to maintain availability during disruptions.
3. **Implement Health Checks**: Configure readiness and liveness probes for all application pods.
4. **Use Topology Spread Constraints**: Distribute pods across nodes and AZs using topology spread constraints.
5. **Enable Auto-Repair**: Managed node groups automatically replace unhealthy nodes.
6. **Test Failure Scenarios**: Regularly test AZ failures, node terminations, and rolling updates.
7. **Use Multiple Node Groups**: Don't rely on a single node group - spread workloads across multiple groups.
8. **Configure Update Strategy**: Set appropriate `max_unavailable` and `max_surge` for rolling updates.

### Operational Excellence

1. **Use Terraform State Locking**: Store EKS Terraform state in S3 with DynamoDB locking.
2. **Version Pin the Module**: Use specific module versions (e.g., `version = "~> 21.0"`) in production.
3. **Tag Everything**: Apply comprehensive tags including Environment, Owner, Application, CostCenter.
4. **Enable CloudWatch Container Insights**: Deploy Container Insights for cluster and application monitoring.
5. **Implement GitOps**: Use tools like Flux or ArgoCD for declarative application deployment.
6. **Use Namespaces**: Organize workloads into logical namespaces with resource quotas.
7. **Monitor Cluster Metrics**: Track control plane metrics, node status, and pod health.
8. **Implement Backup Strategy**: Use Velero or AWS Backup for cluster and application backups.
9. **Document IRSA Roles**: Maintain clear documentation of all service account to IAM role mappings.
10. **Test in Non-Production**: Always test cluster updates and configuration changes in development first.

### Networking and Connectivity

1. **Use VPC Endpoints**: Deploy VPC endpoints for ECR, S3, and other AWS services to reduce NAT costs.
2. **Plan IP Address Space**: Ensure sufficient IP addresses for maximum pod density using CIDR calculations.
3. **Use Network Load Balancers**: Deploy NLB for high-throughput services requiring low latency.
4. **Implement Ingress Controllers**: Use AWS Load Balancer Controller for advanced ingress capabilities.
5. **Enable Flow Logs**: Configure VPC flow logs for network troubleshooting and security analysis.
6. **Use Security Groups Carefully**: Minimize custom security group rules and rely on EKS-managed groups when possible.
7. **Plan for Service Mesh**: Consider AWS App Mesh or Istio for advanced traffic management.
8. **Use Private Link**: Implement PrivateLink for private connectivity to third-party services.

### Monitoring and Observability

1. **Deploy Metrics Server**: Install metrics-server for horizontal pod autoscaling.
2. **Use Prometheus and Grafana**: Deploy monitoring stack for custom metrics and dashboards.
3. **Enable Control Plane Logging**: Log all control plane components to CloudWatch Logs.
4. **Implement Distributed Tracing**: Use AWS X-Ray or Jaeger for application tracing.
5. **Set Up Alerting**: Configure CloudWatch alarms for critical cluster metrics.
6. **Monitor Node Health**: Track node conditions, disk pressure, and memory pressure.
7. **Log Application Logs**: Use Fluent Bit or CloudWatch agent for container log aggregation.

### Upgrade and Maintenance

1. **Plan Regular Upgrades**: Upgrade Kubernetes versions within the AWS support window (typically annually).
2. **Test Add-on Compatibility**: Verify add-on compatibility before upgrading cluster version.
3. **Update Node Groups Separately**: Upgrade managed node groups after control plane upgrade completes.
4. **Use Blue-Green for Updates**: Create new node groups and drain old ones for major updates.
5. **Monitor During Upgrades**: Watch cluster metrics and application health during upgrade process.
6. **Maintain Update Documentation**: Document upgrade procedures and rollback plans.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-eks
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-eks/tree/master/examples
- **AWS EKS Documentation**: https://docs.aws.amazon.com/eks/latest/userguide/
- **EKS User Guide**: https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html
- **EKS Best Practices Guide**: https://aws.github.io/aws-eks-best-practices/
- **Kubernetes Documentation**: https://kubernetes.io/docs/home/
- **EKS Managed Node Groups**: https://docs.aws.amazon.com/eks/latest/userguide/managed-node-groups.html
- **EKS Fargate**: https://docs.aws.amazon.com/eks/latest/userguide/fargate.html
- **Karpenter Documentation**: https://karpenter.sh/
- **IAM Roles for Service Accounts**: https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
- **EKS Add-ons**: https://docs.aws.amazon.com/eks/latest/userguide/eks-add-ons.html
- **EKS Security**: https://docs.aws.amazon.com/eks/latest/userguide/security.html
- **VPC CNI Plugin**: https://github.com/aws/amazon-vpc-cni-k8s
- **AWS Load Balancer Controller**: https://kubernetes-sigs.github.io/aws-load-balancer-controller/
- **EKS Pricing**: https://aws.amazon.com/eks/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Specify Kubernetes Version**: Always set `cluster_version` explicitly (e.g., "1.33") for production clusters
2. **Endpoint Access Defaults**: Public endpoint is disabled by default (`cluster_endpoint_public_access = false`); enable if kubectl access needed from outside VPC
3. **Enable Cluster Creator Admin**: Set `enable_cluster_creator_admin_permissions = true` for Terraform identity to access cluster
4. **Use Access Entries**: Prefer access entries over aws-auth ConfigMap for cluster access management
5. **Subnet Tagging Required**: Subnets must have `kubernetes.io/cluster/<CLUSTER_NAME>` tags for node registration
6. **Deploy Add-ons with Dependencies**: Use `before_compute = true` for vpc-cni to ensure networking is ready before nodes
7. **EKS Auto Mode**: Simplest setup - use `compute_config = { enabled = true, node_pools = ["general-purpose"] }` for fully managed nodes
8. **Managed Node Groups Preferred**: Prefer EKS managed node groups over self-managed for standard workloads
9. **KMS Encryption Enabled**: `create_kms_key = true` by default; secrets are encrypted at rest
10. **Autoscaling Note**: Module ignores `desired_size` changes to support external autoscalers (Karpenter, Cluster Autoscaler)
11. **Karpenter Tags**: If using Karpenter, tag subnets and security groups with `karpenter.sh/discovery = <cluster_name>`
12. **Version Pin Module**: Use specific version (e.g., `version = "~> 21.0"`) to prevent unexpected changes
13. **Core Add-ons**: Always include vpc-cni, kube-proxy, coredns; add aws-ebs-csi-driver for persistent volumes
14. **Private Subnets**: Deploy nodes in private subnets with NAT gateway or VPC endpoints for outbound access
15. **Multi-AZ Deployment**: Distribute nodes across at least three availability zones for HA
16. **EFA Minimum Nodes**: EFA deployments require minimum 2 nodes; placement groups auto-configured
