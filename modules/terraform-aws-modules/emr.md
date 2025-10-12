---
module_name: terraform-aws-emr
keywords: [emr, elastic-mapreduce, hadoop, spark, hive, presto, trino, big-data, data-processing, analytics, mapreduce, instance-fleet, instance-group, cluster, master-node, core-node, task-node, spot-instances, serverless, studio, eks, virtual-cluster, emr-containers, notebook, data-lake, etl, batch-processing, distributed-computing, yarn, hdfs, s3]
---

# AWS EMR Terraform Module

## Module Information

- **Source**: `terraform-aws-modules/emr/aws`
- **Version**: 2.4.2
- **Terraform**: >= 1.0
- **AWS Provider**: >= 5.83
- **License**: Apache-2.0

## Description

Terraform module that creates and manages Amazon EMR (Elastic MapReduce) resources for big data processing and analytics workloads. Amazon EMR is a managed cluster platform that simplifies running big data frameworks like Apache Hadoop, Apache Spark, Apache Hive, Presto, and Trino on AWS infrastructure. This module supports multiple deployment models including traditional EMR clusters with instance groups or instance fleets, EMR Serverless applications, EMR Studio for interactive development, and EMR on EKS (virtual clusters) for containerized workloads.

The module provides comprehensive configuration options for cluster topology, instance types, storage, networking, security, IAM roles, and application installations. It manages the complete lifecycle of EMR resources including master nodes, core nodes (for data storage and processing), and task nodes (for additional compute capacity). The module supports both long-running clusters for continuous data interaction and transient clusters that automatically terminate after job completion, enabling cost-effective big data processing at any scale.

EMR integrates deeply with AWS services including S3 for data storage, CloudWatch for monitoring, IAM for access control, and VPC for network isolation. The module handles the complexity of security group management, IAM role creation, and cluster configuration, making it simple to deploy production-ready big data environments that follow AWS best practices.

## Key Features

- **Instance Fleet Support**: Deploy clusters using instance fleets with flexible instance type configurations and automatic provisioning
- **Instance Group Support**: Traditional instance group deployment model with master, core, and task node groups
- **Multiple Applications**: Support for Spark, Hadoop, Hive, Presto, Trino, HBase, Flink, and 20+ big data frameworks
- **High Availability**: Configure clusters with 1 or 3 primary nodes for zero-downtime operation
- **Spot Instance Integration**: Use EC2 Spot Instances for cost-effective task nodes and optional core nodes
- **VPC Deployment**: Deploy clusters in public or private subnets with customizable security group configurations
- **Security Configuration**: Encryption at rest and in transit, Kerberos authentication, and fine-grained access control
- **IAM Role Management**: Automated creation of service roles, instance profiles, and autoscaling roles
- **Managed Scaling**: Auto-scaling policies for dynamic cluster capacity based on workload demands
- **Bootstrap Actions**: Execute custom scripts during cluster initialization for software installation and configuration
- **Configuration Classification**: Override default application configurations (Hadoop, Spark, Hive, etc.)
- **Step Execution**: Submit Spark jobs, Hive queries, and custom steps during cluster creation
- **CloudWatch Logging**: Publish cluster logs to CloudWatch Logs for centralized monitoring
- **S3 Integration**: Log aggregation to S3 and seamless data access from S3 buckets
- **Custom AMIs**: Use custom Amazon Machine Images with pre-installed software and configurations
- **Managed Security Groups**: Automatically create and configure security groups for master, slave, and service access
- **EMR Serverless**: Dedicated submodule for serverless Spark and Hive applications with automatic scaling
- **EMR Studio**: Submodule for creating interactive development environments with Jupyter notebooks
- **EMR on EKS**: Virtual cluster submodule for running EMR workloads on existing EKS clusters
- **Tagging Support**: Comprehensive resource tagging for cost allocation and resource management

## Use Cases

- **Big Data Analytics**: Process and analyze petabyte-scale datasets using Hadoop, Spark, and Presto frameworks
- **ETL Pipelines**: Extract, transform, and load data from multiple sources into data warehouses and data lakes
- **Log Processing**: Analyze application logs, web server logs, and system logs at scale for insights and troubleshooting
- **Machine Learning**: Train and deploy machine learning models using Spark MLlib and TensorFlow on distributed infrastructure
- **Real-time Streaming**: Process streaming data from Kinesis, Kafka, or other sources using Spark Streaming or Flink
- **Data Lake Processing**: Query and transform data stored in S3 data lakes using Spark SQL and Presto
- **Genomics Analysis**: Process large-scale genomics datasets for research and pharmaceutical applications
- **Financial Analytics**: Perform risk analysis, fraud detection, and trading analytics on high-frequency data
- **Clickstream Analysis**: Analyze user behavior and website interaction patterns for product optimization
- **Data Science Workloads**: Provide scalable compute infrastructure for data scientists using EMR Studio notebooks

## Submodules

### serverless

Creates AWS EMR Serverless applications for running Spark and Hive workloads without managing cluster infrastructure.

**Purpose**: Provision serverless EMR applications with automatic scaling and pay-per-use pricing model.

**Key Features**:
- Support for Spark and Hive application types
- Configurable initial and maximum compute capacity
- Pre-initialized workers for faster job startup
- Network configuration with VPC and security group support
- Support for ARM64 and X86_64 processor architectures
- Auto-start and auto-stop configurations
- Worker disk and memory configuration per application type
- Application-level monitoring with CloudWatch
- S3 integration for input/output data access

**Variables** (key ones):
- `name` (string): Name of the EMR Serverless application
- `type` (string): Application type - "SPARK" or "HIVE" (default: "SPARK")
- `release_label` (string): EMR release version (e.g., "emr-6.9.0")
- `architecture` (string): CPU architecture - "ARM64" or "X86_64" (default: "X86_64")
- `initial_capacity` (any): Initial capacity configuration for driver and executor/task nodes
- `maximum_capacity` (any): Maximum CPU, memory, and storage limits
- `network_configuration` (any): VPC subnet and security group settings
- `auto_start_configuration` (any): Automatic application startup settings
- `auto_stop_configuration` (any): Idle timeout configuration for automatic shutdown
- `image_configuration` (any): Custom container image configuration
- `tags` (map(string)): Tags to apply to the application

**Outputs**:
- `application_id`: Unique identifier for the EMR Serverless application
- `application_arn`: ARN of the EMR Serverless application
- `iam_role_name`: Name of the IAM execution role
- `iam_role_arn`: ARN of the IAM execution role for job submission
- `security_group_id`: ID of the security group (if created)

**Usage Example**:
```hcl
module "emr_serverless_spark" {
  source = "terraform-aws-modules/emr/aws//modules/serverless"

  name          = "analytics-spark"
  type          = "SPARK"
  release_label = "emr-6.9.0"
  architecture  = "X86_64"

  # Initial capacity
  initial_capacity = {
    driver = {
      initial_capacity_type = "Driver"
      initial_capacity_config = {
        worker_count = 1
        worker_configuration = {
          cpu    = "2 vCPU"
          memory = "4 GB"
        }
      }
    }
    executor = {
      initial_capacity_type = "Executor"
      initial_capacity_config = {
        worker_count = 2
        worker_configuration = {
          cpu    = "4 vCPU"
          memory = "8 GB"
          disk   = "20 GB"
        }
      }
    }
  }

  # Maximum capacity limits
  maximum_capacity = {
    cpu    = "48 vCPU"
    memory = "144 GB"
    disk   = "1000 GB"
  }

  # Network configuration
  network_configuration = {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [aws_security_group.emr_serverless.id]
  }

  # Auto-stop after 15 minutes of idle time
  auto_stop_configuration = {
    enabled              = true
    idle_timeout_minutes = 15
  }

  tags = {
    Environment = "production"
    Application = "analytics"
  }
}
```

### studio

Creates AWS EMR Studio resources for interactive development with Jupyter notebooks and Spark applications.

**Purpose**: Provision web-based integrated development environments (IDEs) for data scientists and engineers to develop, visualize, and debug Spark applications.

**Key Features**:
- Support for IAM and SSO (Single Sign-On) authentication modes
- Workspace and engine security group management
- Git repository integration for version control
- S3 backup location for notebook persistence
- Session mapping for user and group access control
- Service role and user role creation
- Integration with EMR clusters and EMR on EKS
- Collaborative workspace sharing
- Custom subnet configuration for workspace isolation

**Variables** (key ones):
- `name` (string): Name of the EMR Studio
- `auth_mode` (string): Authentication mode - "IAM" or "SSO"
- `default_s3_location` (string): S3 bucket location for notebook backup
- `vpc_id` (string): VPC ID for the studio
- `subnet_ids` (list(string)): Subnet IDs for studio workspaces
- `workspace_security_group_id` (string): Security group for workspace (optional, auto-created if not specified)
- `engine_security_group_id` (string): Security group for EMR clusters accessed by studio
- `create_service_role` (bool): Whether to create service IAM role (default: true)
- `create_user_role` (bool): Whether to create user IAM role (default: true)
- `session_mappings` (any): User/group to IAM role mappings for access control
- `idp_auth_url` (string): Identity provider authentication URL for SSO
- `idp_relay_state_parameter_name` (string): Relay state parameter name for SSO
- `tags` (map(string)): Tags to apply to the studio

**Outputs**:
- `studio_id`: Unique identifier for the EMR Studio
- `studio_arn`: ARN of the EMR Studio
- `studio_url`: URL to access the EMR Studio interface
- `service_iam_role_name`: Name of the service IAM role
- `service_iam_role_arn`: ARN of the service IAM role
- `user_iam_role_name`: Name of the user IAM role
- `user_iam_role_arn`: ARN of the user IAM role
- `workspace_security_group_id`: ID of the workspace security group
- `engine_security_group_id`: ID of the engine security group

**Usage Example**:
```hcl
module "emr_studio" {
  source = "terraform-aws-modules/emr/aws//modules/studio"

  name                = "data-science-studio"
  auth_mode           = "SSO"
  default_s3_location = "s3://${aws_s3_bucket.notebooks.id}/studios/"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # SSO configuration
  idp_auth_url                   = "https://my-idp.com/auth"
  idp_relay_state_parameter_name = "RelayState"

  # Session mappings for user access
  session_mappings = {
    data_scientists = {
      identity_type = "GROUP"
      identity_name = "DataScientists"
      session_policy_arn = aws_iam_policy.data_scientist_policy.arn
    }
    admin = {
      identity_type = "USER"
      identity_name = "admin@example.com"
      session_policy_arn = aws_iam_policy.admin_policy.arn
    }
  }

  tags = {
    Environment = "production"
    Team        = "data-science"
  }
}
```

### virtual-cluster

Creates AWS EMR on EKS (Elastic Kubernetes Service) virtual clusters for running EMR workloads in containerized environments.

**Purpose**: Enable EMR workloads (Spark, Hive) to run on existing EKS clusters, leveraging Kubernetes for orchestration and resource management.

**Key Features**:
- Kubernetes namespace creation and configuration
- IAM roles for service accounts (IRSA) support
- Job execution role with fine-grained S3 access
- CloudWatch log group creation for job logs
- Integration with existing EKS clusters
- Kubernetes RBAC configuration
- Support for multiple virtual clusters per EKS cluster
- Glue Data Catalog integration for metadata management
- Cost isolation and resource allocation per namespace

**Variables** (key ones):
- `name` (string): Name of the EMR virtual cluster
- `namespace` (string): Kubernetes namespace for EMR workloads (default: "emr-containers")
- `eks_cluster_id` (string): EKS cluster identifier
- `create_namespace` (bool): Whether to create Kubernetes namespace (default: true)
- `create_iam_role` (bool): Whether to create job execution IAM role (default: true)
- `iam_role_name` (string): Name of the job execution IAM role
- `s3_bucket_arns` (list(string)): S3 bucket ARNs for job input/output access
- `iam_role_additional_policies` (map(string)): Additional IAM policies to attach
- `create_cloudwatch_log_group` (bool): Whether to create CloudWatch log group (default: true)
- `tags` (map(string)): Tags to apply to resources

**Outputs**:
- `virtual_cluster_id`: Unique identifier for the EMR virtual cluster
- `virtual_cluster_arn`: ARN of the EMR virtual cluster
- `virtual_cluster_name`: Name of the EMR virtual cluster
- `iam_role_name`: Name of the job execution IAM role
- `iam_role_arn`: ARN of the job execution IAM role
- `iam_role_unique_id`: Unique ID of the IAM role
- `namespace`: Kubernetes namespace used for EMR workloads
- `cloudwatch_log_group_name`: Name of the CloudWatch log group

**Usage Example**:
```hcl
module "emr_on_eks" {
  source = "terraform-aws-modules/emr/aws//modules/virtual-cluster"

  name           = "production-analytics"
  eks_cluster_id = module.eks.cluster_id
  namespace      = "emr-production"

  # Create namespace and configure RBAC
  create_namespace = true

  # Job execution IAM role
  create_iam_role = true
  iam_role_name   = "emr-eks-job-execution"

  # S3 access for data lakes
  s3_bucket_arns = [
    "arn:aws:s3:::my-data-lake",
    "arn:aws:s3:::my-data-lake/*",
    "arn:aws:s3:::my-logs-bucket",
    "arn:aws:s3:::my-logs-bucket/*"
  ]

  # Additional policies for Glue catalog access
  iam_role_additional_policies = {
    glue = aws_iam_policy.glue_catalog_access.arn
  }

  # CloudWatch logging
  create_cloudwatch_log_group       = true
  cloudwatch_log_group_retention_in_days = 7

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Submit Spark job to virtual cluster
resource "aws_emrcontainers_job_run" "spark_job" {
  name                      = "sample-spark-job"
  virtual_cluster_id        = module.emr_on_eks.virtual_cluster_id
  execution_role_arn        = module.emr_on_eks.iam_role_arn
  release_label             = "emr-6.9.0-latest"

  job_driver {
    spark_submit_job_driver {
      entry_point = "s3://my-data-lake/scripts/process-data.py"
      spark_submit_parameters = "--conf spark.executor.instances=2"
    }
  }

  configuration_overrides {
    application_configuration {
      classification = "spark-defaults"
      properties = {
        "spark.dynamicAllocation.enabled" = "false"
        "spark.executor.memory"           = "2G"
      }
    }
  }
}
```

## Variables

### Core Configuration
- `create` (bool): Whether to create EMR cluster resources (default: true)
- `name` (string): Name of the EMR cluster/job flow
- `release_label` (string): EMR release version (e.g., "emr-6.9.0", "emr-7.0.0")
- `applications` (list(string)): List of applications to install (e.g., ["Spark", "Hive", "Presto"])
- `tags` (map(string)): Tags to apply to all resources

### Cluster Topology - Instance Groups
- `master_instance_group` (any): Master node configuration
  - `instance_type`: EC2 instance type
  - `instance_count`: Number of master nodes (1 or 3 for HA)
  - `ebs_config`: EBS volume configuration
  - `bid_price`: Spot instance bid price (optional)
- `core_instance_group` (any): Core node configuration with same fields as master
- `task_instance_group` (list(any)): Task node configurations (optional, for additional compute)

### Cluster Topology - Instance Fleets
- `master_instance_fleet` (any): Master node fleet configuration
  - `target_on_demand_capacity`: On-demand instance units
  - `target_spot_capacity`: Spot instance units
  - `instance_type_configs`: List of instance types with weights and configurations
- `core_instance_fleet` (any): Core node fleet configuration
- `task_instance_fleet` (list(any)): Task node fleet configurations

### EC2 and Networking
- `ec2_attributes` (any): EC2 instance attributes
  - `subnet_id` or `subnet_ids`: Subnet for cluster deployment
  - `key_name`: EC2 key pair for SSH access
  - `instance_profile`: IAM instance profile ARN
  - `emr_managed_master_security_group`: Master node security group
  - `emr_managed_slave_security_group`: Core/task node security group
  - `service_access_security_group`: Service access security group
  - `additional_master_security_groups`: Additional security groups for master
  - `additional_slave_security_groups`: Additional security groups for core/task
- `vpc_id` (string): VPC ID for creating managed security groups
- `is_private_cluster` (bool): Whether cluster is in private subnet (default: true)

### Security
- `create_security_configuration` (bool): Create security configuration for encryption
- `security_configuration` (string): Name of existing security configuration
- `security_configuration_use_name_prefix` (bool): Use name prefix for security configuration
- `security_configuration_configuration` (any): Security configuration JSON
- `kerberos_attributes` (any): Kerberos authentication configuration

### IAM Roles
- `create_service_iam_role` (bool): Create EMR service role (default: true)
- `service_iam_role_arn` (string): ARN of existing service role
- `service_iam_role_name` (string): Name for service role
- `service_iam_role_policies` (map(string)): Additional policies for service role
- `create_iam_instance_profile` (bool): Create EC2 instance profile (default: true)
- `iam_instance_profile_name` (string): Name for instance profile
- `iam_instance_profile_policies` (map(string)): Additional policies for instance profile
- `create_autoscaling_iam_role` (bool): Create autoscaling role (default: true)
- `autoscaling_iam_role_name` (string): Name for autoscaling role

### Managed Security Groups
- `create_managed_security_groups` (bool): Create managed security groups
- `managed_master_security_group_name` (string): Name for master security group
- `managed_master_security_group_rules` (any): Additional security group rules for master
- `managed_slave_security_group_name` (string): Name for core/task security group
- `managed_slave_security_group_rules` (any): Additional security group rules for slaves
- `managed_service_access_security_group_name` (string): Name for service access security group

### Cluster Configuration
- `configurations_json` (string): JSON string of application configurations
- `bootstrap_action` (list(any)): Bootstrap actions to execute on cluster startup
- `step` (list(any)): Steps to execute after cluster is ready
- `step_concurrency_level` (number): Maximum number of steps to run concurrently

### Scaling and Auto-Termination
- `auto_termination_policy` (any): Automatic termination after idle time
- `keep_job_flow_alive_when_no_steps` (bool): Keep cluster running after steps complete (default: true)
- `termination_protection` (bool): Enable termination protection (default: false)

### Logging and Monitoring
- `log_uri` (string): S3 URI for log aggregation
- `log_encryption_kms_key_id` (string): KMS key for encrypting logs
- `visible_to_all_users` (bool): Whether cluster is visible to all IAM users (default: true)

### Advanced Options
- `custom_ami_id` (string): Custom AMI ID for cluster instances
- `ebs_root_volume_size` (number): Root volume size in GB
- `additional_info` (string): Additional JSON configuration for cluster
- `placement_group_config` (list(any)): Placement group configuration for HA

## Outputs

### Cluster Information
- `cluster_id`: Unique identifier for the EMR cluster
- `cluster_arn`: ARN of the EMR cluster
- `cluster_name`: Name of the EMR cluster
- `cluster_master_public_dns`: Public DNS name of the master node
- `cluster_core_instance_group_id`: Core instance group ID
- `cluster_master_instance_group_id`: Master instance group ID

### Security Configuration
- `security_configuration_id`: ID of the security configuration
- `security_configuration_name`: Name of the security configuration

### IAM Roles
- `service_iam_role_name`: Name of the EMR service IAM role
- `service_iam_role_arn`: ARN of the EMR service IAM role
- `service_iam_role_unique_id`: Unique ID of the service role
- `autoscaling_iam_role_name`: Name of the autoscaling IAM role
- `autoscaling_iam_role_arn`: ARN of the autoscaling IAM role
- `autoscaling_iam_role_unique_id`: Unique ID of the autoscaling role
- `iam_instance_profile_arn`: ARN of the EC2 instance profile
- `iam_instance_profile_id`: ID of the EC2 instance profile
- `iam_instance_profile_unique`: Unique ID of the instance profile
- `iam_instance_profile_iam_role_name`: Name of the instance profile IAM role
- `iam_instance_profile_iam_role_arn`: ARN of the instance profile IAM role
- `iam_instance_profile_iam_role_unique_id`: Unique ID of the instance profile role

### Security Groups
- `managed_master_security_group_arn`: ARN of the master node security group
- `managed_master_security_group_id`: ID of the master node security group
- `managed_slave_security_group_arn`: ARN of the core/task node security group
- `managed_slave_security_group_id`: ID of the core/task node security group
- `managed_service_access_security_group_arn`: ARN of the service access security group
- `managed_service_access_security_group_id`: ID of the service access security group

## Usage Examples

### Basic EMR Cluster with Instance Groups

```hcl
module "emr_basic" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 2.4"

  name          = "my-emr-cluster"
  release_label = "emr-6.9.0"
  applications  = ["Spark", "Hadoop"]

  master_instance_group = {
    instance_type = "m5.xlarge"
  }

  core_instance_group = {
    instance_type  = "m5.xlarge"
    instance_count = 2
    ebs_config = [{
      size                 = 100
      type                 = "gp3"
      volumes_per_instance = 1
    }]
  }

  ec2_attributes = {
    subnet_id = module.vpc.private_subnets[0]
    key_name  = aws_key_pair.emr.key_name
  }

  vpc_id = module.vpc.vpc_id

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/logs/"

  tags = {
    Environment = "development"
  }
}
```

### High Availability EMR Cluster

```hcl
module "emr_ha" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 2.4"

  name          = "ha-production-cluster"
  release_label = "emr-6.11.0"
  applications  = ["Spark", "Hadoop", "Hive", "Presto"]

  # 3 master nodes for high availability
  master_instance_group = {
    instance_count = 3
    instance_type  = "m5.2xlarge"
    ebs_config = [{
      size                 = 50
      type                 = "gp3"
      volumes_per_instance = 1
    }]
  }

  core_instance_group = {
    instance_count = 5
    instance_type  = "r5.2xlarge"
    ebs_config = [{
      size                 = 500
      type                 = "gp3"
      iops                 = 3000
      volumes_per_instance = 2
    }]
  }

  ec2_attributes = {
    subnet_ids = module.vpc.private_subnets
    key_name   = aws_key_pair.emr.key_name
  }

  # Use placement group for HA
  placement_group_config = [{
    instance_role      = "MASTER"
    placement_strategy = "SPREAD"
  }]

  vpc_id              = module.vpc.vpc_id
  is_private_cluster  = true

  # Enable termination protection
  termination_protection = true
  keep_job_flow_alive_when_no_steps = true

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/ha-cluster/"

  tags = {
    Environment = "production"
    HA          = "enabled"
  }
}
```

### EMR Cluster with Spot Instances

```hcl
module "emr_spot" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 2.4"

  name          = "cost-optimized-cluster"
  release_label = "emr-6.9.0"
  applications  = ["Spark"]

  # On-demand master node
  master_instance_group = {
    instance_type = "m5.xlarge"
  }

  # On-demand core nodes for data persistence
  core_instance_group = {
    instance_count = 2
    instance_type  = "m5.xlarge"
    ebs_config = [{
      size                 = 200
      type                 = "gp3"
      volumes_per_instance = 1
    }]
  }

  # Spot instances for task nodes
  task_instance_group = [{
    instance_count = 5
    instance_type  = "m5.2xlarge"
    bid_price      = "0.30"
    ebs_config = [{
      size                 = 100
      type                 = "gp3"
      volumes_per_instance = 1
    }]
  }]

  ec2_attributes = {
    subnet_id = module.vpc.private_subnets[0]
    key_name  = aws_key_pair.emr.key_name
  }

  vpc_id = module.vpc.vpc_id

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/spot-cluster/"

  tags = {
    Environment = "development"
    CostOptimized = "true"
  }
}
```

### EMR Cluster with Instance Fleet

```hcl
module "emr_fleet" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 2.4"

  name          = "fleet-cluster"
  release_label = "emr-6.9.0"
  applications  = ["Spark", "Hive"]

  master_instance_fleet = {
    target_on_demand_capacity = 1
    instance_type_configs = [
      {
        instance_type     = "m5.xlarge"
        weighted_capacity = 1
      },
      {
        instance_type     = "m5.2xlarge"
        weighted_capacity = 2
      }
    ]
  }

  core_instance_fleet = {
    target_on_demand_capacity = 2
    target_spot_capacity      = 4
    instance_type_configs = [
      {
        instance_type     = "r5.xlarge"
        weighted_capacity = 1
        ebs_config = [{
          size                 = 200
          type                 = "gp3"
          volumes_per_instance = 1
        }]
      },
      {
        instance_type     = "r5.2xlarge"
        weighted_capacity = 2
        ebs_config = [{
          size                 = 200
          type                 = "gp3"
          volumes_per_instance = 1
        }]
      }
    ]
    launch_specifications = {
      spot_specification = {
        allocation_strategy      = "capacity-optimized"
        timeout_action           = "SWITCH_TO_ON_DEMAND"
        timeout_duration_minutes = 10
      }
    }
  }

  ec2_attributes = {
    subnet_id = module.vpc.private_subnets[0]
    key_name  = aws_key_pair.emr.key_name
  }

  vpc_id = module.vpc.vpc_id

  tags = {
    Environment = "production"
    Fleet       = "enabled"
  }
}
```

### EMR Cluster with Security Configuration

```hcl
module "emr_secure" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 2.4"

  name          = "secure-cluster"
  release_label = "emr-6.9.0"
  applications  = ["Spark", "Hadoop"]

  # Enable security configuration
  create_security_configuration = true
  security_configuration_configuration = jsonencode({
    EncryptionConfiguration = {
      EnableInTransitEncryption = true
      EnableAtRestEncryption    = true
      InTransitEncryptionConfiguration = {
        TLSCertificateConfiguration = {
          CertificateProviderType = "PEM"
          S3Object                = "s3://${aws_s3_bucket.certificates.id}/certs/"
        }
      }
      AtRestEncryptionConfiguration = {
        S3EncryptionConfiguration = {
          EncryptionMode = "SSE-KMS"
          AwsKmsKey      = aws_kms_key.emr.arn
        }
        LocalDiskEncryptionConfiguration = {
          EncryptionKeyProviderType = "AwsKms"
          AwsKmsKey                 = aws_kms_key.emr.arn
        }
      }
    }
  })

  master_instance_group = {
    instance_type = "m5.xlarge"
  }

  core_instance_group = {
    instance_count = 2
    instance_type  = "m5.xlarge"
    ebs_config = [{
      size                 = 100
      type                 = "gp3"
      volumes_per_instance = 1
    }]
  }

  ec2_attributes = {
    subnet_id = module.vpc.private_subnets[0]
    key_name  = aws_key_pair.emr.key_name
  }

  vpc_id             = module.vpc.vpc_id
  is_private_cluster = true

  log_uri                    = "s3://${aws_s3_bucket.emr_logs.id}/secure/"
  log_encryption_kms_key_id  = aws_kms_key.emr.id

  tags = {
    Environment = "production"
    Security    = "enhanced"
  }
}
```

### EMR Cluster with Bootstrap Actions and Steps

```hcl
module "emr_with_steps" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 2.4"

  name          = "etl-cluster"
  release_label = "emr-6.9.0"
  applications  = ["Spark"]

  master_instance_group = {
    instance_type = "m5.xlarge"
  }

  core_instance_group = {
    instance_count = 3
    instance_type  = "m5.xlarge"
  }

  # Bootstrap action to install custom software
  bootstrap_action = [{
    name = "Install Python packages"
    path = "s3://${aws_s3_bucket.scripts.id}/bootstrap/install-packages.sh"
    args = ["pandas", "numpy", "scikit-learn"]
  }]

  # Submit Spark job as step
  step = [{
    name              = "Process daily data"
    action_on_failure = "CONTINUE"
    hadoop_jar_step = [{
      jar  = "command-runner.jar"
      args = [
        "spark-submit",
        "--deploy-mode", "cluster",
        "--master", "yarn",
        "s3://${aws_s3_bucket.scripts.id}/jobs/daily-etl.py"
      ]
    }]
  }]

  # Allow concurrent steps
  step_concurrency_level = 3

  ec2_attributes = {
    subnet_id = module.vpc.private_subnets[0]
    key_name  = aws_key_pair.emr.key_name
  }

  vpc_id = module.vpc.vpc_id

  # Terminate cluster after steps complete
  keep_job_flow_alive_when_no_steps = false

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/etl/"

  tags = {
    Environment = "production"
    Workload    = "etl"
  }
}
```

### EMR Cluster with Custom Configurations

```hcl
module "emr_configured" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 2.4"

  name          = "optimized-cluster"
  release_label = "emr-6.9.0"
  applications  = ["Spark", "Hadoop"]

  master_instance_group = {
    instance_type = "m5.2xlarge"
  }

  core_instance_group = {
    instance_count = 4
    instance_type  = "r5.2xlarge"
    ebs_config = [{
      size                 = 500
      type                 = "gp3"
      iops                 = 5000
      volumes_per_instance = 2
    }]
  }

  # Custom application configurations
  configurations_json = jsonencode([
    {
      Classification = "spark"
      Properties = {
        "maximizeResourceAllocation" = "true"
      }
    },
    {
      Classification = "spark-defaults"
      Properties = {
        "spark.dynamicAllocation.enabled" = "true"
        "spark.shuffle.service.enabled"   = "true"
        "spark.executor.memory"           = "8G"
        "spark.executor.cores"            = "4"
        "spark.driver.memory"             = "4G"
      }
    },
    {
      Classification = "hadoop-env"
      Configurations = [{
        Classification = "export"
        Properties = {
          "JAVA_HOME" = "/usr/lib/jvm/java-11-amazon-corretto"
        }
      }]
    }
  ])

  ec2_attributes = {
    subnet_id = module.vpc.private_subnets[0]
    key_name  = aws_key_pair.emr.key_name
  }

  vpc_id = module.vpc.vpc_id

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/optimized/"

  tags = {
    Environment = "production"
    Optimized   = "spark"
  }
}
```

### Transient EMR Cluster for Scheduled Jobs

```hcl
module "emr_transient" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 2.4"

  name          = "nightly-batch-${formatdate("YYYY-MM-DD", timestamp())}"
  release_label = "emr-6.9.0"
  applications  = ["Spark"]

  master_instance_group = {
    instance_type = "m5.xlarge"
  }

  core_instance_group = {
    instance_count = 2
    instance_type  = "m5.xlarge"
  }

  # Auto-terminate after 1 hour of idle time
  auto_termination_policy = {
    idle_timeout = 3600
  }

  # Submit batch job
  step = [{
    name              = "Nightly aggregation"
    action_on_failure = "TERMINATE_CLUSTER"
    hadoop_jar_step = [{
      jar  = "command-runner.jar"
      args = [
        "spark-submit",
        "--deploy-mode", "cluster",
        "s3://${aws_s3_bucket.scripts.id}/jobs/nightly-aggregation.py",
        "--date", formatdate("YYYY-MM-DD", timestamp())
      ]
    }]
  }]

  # Terminate when steps complete
  keep_job_flow_alive_when_no_steps = false

  ec2_attributes = {
    subnet_id = module.vpc.private_subnets[0]
    key_name  = aws_key_pair.emr.key_name
  }

  vpc_id = module.vpc.vpc_id

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/batch/"

  tags = {
    Environment = "production"
    JobType     = "batch"
    Date        = formatdate("YYYY-MM-DD", timestamp())
  }
}
```

## Best Practices

### Cluster Planning and Sizing

1. **Choose the Right Deployment Model**: Use instance groups for consistent workloads, instance fleets for flexible capacity, EMR Serverless for variable workloads, and EMR on EKS for containerized environments with existing Kubernetes infrastructure.
2. **Size Master Nodes Appropriately**: For clusters with 50 nodes or fewer, use m5.xlarge for master nodes; larger clusters require more powerful instances (m5.2xlarge or larger).
3. **Select Core Node Instance Types**: Choose instance types based on workload - general-purpose (m5) for balanced workloads, compute-optimized (c5) for CPU-intensive jobs, memory-optimized (r5) for in-memory processing, and storage-optimized (d3) for high-throughput data processing.
4. **Configure Adequate HDFS Storage**: Calculate core node storage requirements based on data size multiplied by replication factor (default: 3 for 10+ nodes, 2 for 4-9 nodes, 1 for 1-3 nodes).
5. **Use Task Nodes for Scaling**: Add task nodes for additional compute capacity without HDFS storage, enabling dynamic scaling based on workload demands.
6. **Plan for Data Locality**: Deploy clusters in the same region and availability zone as your S3 data to minimize data transfer costs and latency.
7. **Calculate Cluster Capacity**: Estimate required CPU, memory, and storage based on data volume, processing complexity, and SLA requirements before provisioning.
8. **Consider Workload Patterns**: Use long-running clusters for interactive queries and continuous data processing; use transient clusters for batch jobs to minimize costs.

### High Availability and Reliability

9. **Enable High Availability**: Configure 3 master nodes for production clusters to eliminate single points of failure and enable automatic failover.
10. **Use Placement Groups**: Configure EC2 placement groups with SPREAD strategy to ensure master nodes run on distinct hardware for true fault isolation.
11. **Enable Termination Protection**: Set termination protection to true for production clusters to prevent accidental deletion.
12. **Configure Automatic Backups**: Implement regular HDFS snapshots and export critical data to S3 for disaster recovery.
13. **Monitor Cluster Health**: Set up CloudWatch alarms for cluster state, node health, HDFS utilization, and application failures.
14. **Plan for Node Failures**: EMR automatically replaces failed core and task nodes; ensure sufficient capacity to handle temporary capacity reduction during replacement.
15. **Use Multiple Availability Zones**: For instance fleet clusters, specify subnets across multiple AZs to improve availability.
16. **Test Failover Procedures**: Regularly test master node failover and data recovery procedures to validate HA configuration.

### Security and Compliance

17. **Deploy in Private Subnets**: Always deploy EMR clusters in private subnets to prevent direct internet access and reduce attack surface.
18. **Enable Encryption at Rest**: Use security configurations to encrypt data on local disks and EBS volumes with AWS KMS encryption.
19. **Enable Encryption in Transit**: Configure TLS encryption for inter-node communication and client connections using security configurations.
20. **Implement Fine-Grained Access Control**: Use IAM roles and policies to control access to EMR APIs, S3 data, and cluster resources.
21. **Enable S3 Block Public Access**: Ensure S3 buckets used for logs and data have public access blocked at the bucket and account level.
22. **Use Security Groups Effectively**: Configure security groups to allow only necessary inbound traffic (typically only from known IP ranges for SSH).
23. **Enable Kerberos Authentication**: For enhanced security, configure Kerberos for strong authentication across cluster services.
24. **Rotate SSH Keys Regularly**: Use EC2 key pairs for SSH access and rotate keys periodically; consider disabling SSH entirely for production clusters.
25. **Implement Least Privilege**: Grant minimum necessary permissions to service roles, instance profiles, and job execution roles.
26. **Enable CloudTrail Logging**: Log all EMR API calls to CloudTrail for security auditing and compliance.
27. **Use Lake Formation for Data Access**: Integrate with AWS Lake Formation for centralized, fine-grained data access control.
28. **Scan for Vulnerabilities**: Regularly update EMR release versions and custom AMIs to patch security vulnerabilities.

### Cost Optimization

29. **Use Spot Instances for Task Nodes**: Configure task nodes as spot instances to reduce compute costs by up to 90% without risking data loss.
30. **Consider Spot for Core Nodes**: For non-critical workloads, use spot instances for core nodes with instance fleet fallback to on-demand.
31. **Enable Auto-Termination**: Configure idle timeout for development and transient clusters to automatically terminate when not in use.
32. **Right-Size Instance Types**: Use CloudWatch metrics to analyze CPU, memory, and I/O utilization and adjust instance types accordingly.
33. **Use Graviton Instances**: Choose ARM-based Graviton2 instances (m6g, r6g, c6g) for 20-30% better price-performance.
34. **Implement Managed Scaling**: Enable managed scaling policies to automatically add or remove instances based on YARN metrics.
35. **Leverage EMR Serverless**: For intermittent workloads, use EMR Serverless to pay only for actual job execution time.
36. **Optimize Storage Costs**: Use gp3 EBS volumes instead of gp2 for better price-performance; implement lifecycle policies for S3 log data.
37. **Terminate Idle Clusters**: Review cluster utilization regularly and terminate long-running clusters that are no longer needed.
38. **Use Savings Plans**: Purchase EC2 Savings Plans for predictable, long-running EMR workloads to reduce costs by up to 72%.
39. **Monitor EMR Costs**: Use AWS Cost Explorer with EMR-specific tags to track and allocate costs by team, project, or workload.
40. **Compress Data**: Enable compression for intermediate data and outputs to reduce storage costs and improve I/O performance.

### Performance Optimization

41. **Tune Spark Configurations**: Adjust spark.executor.memory, spark.executor.cores, and spark.dynamicAllocation settings based on workload characteristics.
42. **Enable Dynamic Allocation**: Use Spark dynamic allocation to automatically scale executors based on workload demands.
43. **Optimize Data Formats**: Use columnar formats (Parquet, ORC) for analytical workloads to improve query performance and reduce storage.
44. **Partition Data Effectively**: Partition large datasets by commonly queried dimensions (date, region) to enable partition pruning.
45. **Use Local Storage**: For I/O-intensive workloads, choose instance types with NVMe SSD instance storage (i3, i4i, d3).
46. **Enable Speculation**: Configure speculative execution for Spark jobs to mitigate the impact of slow tasks.
47. **Tune YARN Settings**: Adjust yarn.nodemanager.resource.memory-mb and yarn.scheduler.maximum-allocation-mb based on instance memory.
48. **Optimize Shuffle Operations**: Configure appropriate spark.sql.shuffle.partitions and spark.default.parallelism for your cluster size.
49. **Use Data Caching**: Leverage Spark caching and persistence for iterative algorithms and repeated dataset access.
50. **Enable Hive Metastore on RDS**: Use external metastore on Amazon RDS for better performance and shared metadata across clusters.

### Monitoring and Observability

51. **Enable Detailed Monitoring**: Turn on detailed instance-level metrics in CloudWatch for granular resource utilization tracking.
52. **Configure Log Publishing**: Send logs to S3 and CloudWatch Logs for centralized log aggregation and analysis.
53. **Set Up Critical Alarms**: Create CloudWatch alarms for cluster state RED, low HDFS capacity, high memory pressure, and failed steps.
54. **Monitor Application Metrics**: Track Spark, Hadoop, and YARN metrics through CloudWatch and application UIs.
55. **Use Application History Server**: Configure persistent application history server on S3 for post-mortem analysis of completed jobs.
56. **Track Job Duration**: Monitor step execution times to identify performance degradation and optimization opportunities.
57. **Enable Container Log Rotation**: Configure container log retention to prevent disk space issues on cluster nodes.
58. **Review Slow Queries**: Regularly analyze Spark UI and Ganglia metrics to identify and optimize slow-running queries.

### Operational Excellence

59. **Use Infrastructure as Code**: Manage all EMR infrastructure using Terraform for version control, consistency, and repeatability.
60. **Implement Tagging Strategy**: Apply comprehensive tags for environment, cost center, owner, and workload type to all EMR resources.
61. **Version Bootstrap Scripts**: Store bootstrap actions in version-controlled S3 buckets with proper versioning enabled.
62. **Test Configuration Changes**: Validate cluster configurations and application settings in development before applying to production.
63. **Document Cluster Configurations**: Maintain detailed documentation of cluster purposes, configurations, and operational runbooks.
64. **Use Consistent Naming**: Implement naming conventions for clusters, IAM roles, security groups, and other resources.
65. **Implement GitOps Workflows**: Use Git-based workflows with pull request reviews for Terraform configuration changes.
66. **Automate Cluster Provisioning**: Use CI/CD pipelines to automate EMR cluster creation and configuration for consistent deployments.
67. **Regular Security Patching**: Schedule regular EMR release version updates to apply security patches and feature improvements.
68. **Conduct Disaster Recovery Drills**: Periodically test cluster restoration from backups and failover procedures.

### Application and Workload Management

69. **Separate Workloads by Cluster**: Run different workload types (batch, interactive, streaming) on separate clusters for better resource isolation.
70. **Use Step Execution for Batch Jobs**: Submit jobs as EMR steps rather than SSH-ing into clusters for better tracking and automation.
71. **Implement Job Orchestration**: Use AWS Step Functions, Apache Airflow, or MWAA to orchestrate complex EMR workflows.
72. **Configure Application Dependencies**: Use bootstrap actions to install required libraries and ensure consistent application environments.
73. **Version Control Job Code**: Store Spark/Hive/Presto scripts in version control systems and reference specific versions in production.
74. **Implement Retry Logic**: Configure appropriate action_on_failure settings for steps to handle transient failures gracefully.
75. **Use Parameter Store for Secrets**: Store database passwords and API keys in AWS Systems Manager Parameter Store or Secrets Manager.

## Additional Resources

### Official Documentation
- **AWS EMR Documentation**: https://docs.aws.amazon.com/emr/
- **Terraform AWS EMR Module GitHub**: https://github.com/terraform-aws-modules/terraform-aws-emr
- **Terraform Registry - EMR Module**: https://registry.terraform.io/modules/terraform-aws-modules/emr/aws
- **EMR Release Guide**: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/

### Planning and Best Practices
- **EMR Best Practices**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan.html
- **Cluster Configuration Guidelines**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-instances-guidelines.html
- **EMR Security Guide**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-security.html
- **High Availability Configuration**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-ha.html

### Frameworks and Applications
- **Apache Spark on EMR**: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark.html
- **Apache Hadoop on EMR**: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-hadoop.html
- **Apache Hive on EMR**: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-hive.html
- **Presto on EMR**: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-presto.html

### Advanced Features
- **EMR Serverless**: https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/
- **EMR on EKS**: https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/
- **EMR Studio**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-studio.html
- **EMR Managed Scaling**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-managed-scaling.html

### Cost and Performance
- **EMR Pricing**: https://aws.amazon.com/emr/pricing/
- **EMR Cost Optimization**: https://aws.amazon.com/blogs/big-data/best-practices-for-cost-optimization-with-amazon-emr/
- **EMR Performance Tuning**: https://aws.amazon.com/blogs/big-data/best-practices-for-successfully-managing-memory-for-apache-spark-applications-on-amazon-emr/

## Notes for AI Agents

### Module Selection Guidance
- **Use main EMR module** when deploying traditional Hadoop/Spark clusters with persistent HDFS storage and long-running or batch workloads.
- **Use EMR Serverless submodule** for intermittent, unpredictable workloads where automatic scaling and pay-per-use pricing is preferred over cluster management.
- **Use EMR Studio submodule** when data scientists and analysts need interactive notebook environments for exploratory analysis and application development.
- **Use EMR on EKS submodule** when running EMR workloads on existing Kubernetes infrastructure or requiring containerized deployment patterns.

### Architecture Recommendations
- For **production batch processing**: Use instance groups with on-demand master/core nodes and spot task nodes, enable HA with 3 masters, deploy in private subnets with encryption.
- For **cost-sensitive workloads**: Use instance fleets with spot instances, implement capacity-optimized allocation strategy, configure auto-termination for idle clusters.
- For **interactive analysis**: Deploy EMR Studio with IAM or SSO authentication, use long-running clusters or EMR Serverless, enable CloudWatch logging.
- For **high-throughput streaming**: Use memory-optimized instances (r5, r6g), enable dynamic allocation, configure appropriate Spark streaming batch intervals.
- For **multi-tenant environments**: Use separate clusters per tenant or EMR on EKS with namespace isolation, implement fine-grained IAM policies.

### Common Configuration Patterns
- **Development**: Single master m5.xlarge, 2 core m5.xlarge nodes, auto-terminate after 1 hour idle, spot instances allowed.
- **Small Production**: 3 master m5.xlarge (HA), 5 core r5.xlarge, on-demand instances, termination protection enabled.
- **Large Production**: 3 master m5.2xlarge (HA), 10+ core r5.2xlarge, 20+ task r5.2xlarge spot, managed scaling enabled.
- **Transient Batch**: 1 master m5.xlarge, 2 core m5.xlarge, terminate after steps complete, submit jobs as EMR steps.

### Instance Type Selection
- **Master nodes**: m5.xlarge (small clusters <50 nodes), m5.2xlarge (medium clusters 50-200 nodes), m5.4xlarge (large clusters >200 nodes).
- **Spark workloads**: r5 family (memory-optimized) for in-memory processing, c5 family for compute-intensive transformations.
- **Hadoop MapReduce**: m5 family (balanced), d3 family for high-throughput sequential I/O workloads.
- **Presto/Hive queries**: r5 family for analytic queries with large working sets.
- **Cost optimization**: m6g/r6g Graviton instances for 20-30% savings, spot instances for task nodes.

### Security Best Practices
- **Always deploy in VPC** with private subnets; use NAT gateway for internet access if needed.
- **Enable encryption** at rest (EBS, S3) and in transit (TLS) using security configurations.
- **Use IAM roles** exclusively; never hardcode credentials in bootstrap scripts or application code.
- **Implement least privilege**: Grant only necessary S3 bucket access, restrict EMR API operations, limit cross-account access.
- **Block public access**: Ensure S3 block public access is enabled, configure security groups to deny inbound traffic except from known sources.

### Troubleshooting Tips
- **Cluster stuck in STARTING**: Check VPC subnet configuration, verify NAT gateway/internet gateway connectivity, review EMR service role permissions.
- **Steps failing**: Review step logs in S3, check CloudWatch Logs for application errors, verify S3 bucket permissions for input/output data.
- **Out of memory errors**: Increase executor memory, reduce executor cores, enable dynamic allocation, choose larger instance types.
- **Slow job performance**: Check for data skew, optimize partition count, enable speculation, review Spark UI for bottlenecks.
- **HDFS out of space**: Add EBS volumes to core nodes, delete unused data, enable S3 as primary storage layer.
- **Security group issues**: Ensure managed security groups allow communication between master and core/task nodes.

### Cost Estimation
- **Instance costs**: Primary cost driver, varies by instance type, region, and on-demand vs spot. EMR charges additional $0.03-0.27/hour per instance.
- **Storage costs**: EBS volumes attached to core nodes, S3 costs for logs and data, HDFS replication factor affects storage requirements.
- **Data transfer**: S3 to EMR data transfer is free within the same region, cross-region transfer incurs charges.
- **EMR Serverless costs**: Charged per vCPU-hour and GB-hour, 1-minute minimum per job, pre-initialized workers cost extra.
- Use AWS Pricing Calculator and review CloudWatch billing metrics to estimate and track EMR costs.

### Integration Patterns
- **Data ingestion**: S3 → EMR (Spark) → S3/Redshift/RDS
- **ETL pipelines**: Step Functions → EMR → Glue Data Catalog → Athena
- **Streaming**: Kinesis → EMR (Spark Streaming) → S3/DynamoDB/OpenSearch
- **Machine learning**: SageMaker → EMR (feature engineering) → S3 → SageMaker (training)
- **Data lake analytics**: S3 Data Lake → EMR (Spark SQL) → QuickSight/Tableau
- **Multi-account**: Cross-account S3 access via IAM role assumption with appropriate trust policies
