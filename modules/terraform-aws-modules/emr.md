# Terraform AWS EMR Module

## Module Information

- **Module Name**: `emr`
- **Source**: `terraform-aws-modules/emr/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-emr
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/emr/aws/latest
- **Latest Version**: 3.2.0
- **Terraform**: >= 1.5.7
- **AWS Provider**: >= 6.28
- **Purpose**: Creates and manages Amazon EMR resources for big data processing and analytics workloads
- **Service**: AWS EMR (Elastic MapReduce)
- **Category**: Analytics, Big Data, Compute
- **Keywords**: emr, elastic-mapreduce, spark, hadoop, hive, presto, big-data, analytics, instance-fleet, emr-serverless, emr-studio, emr-on-eks
- **Use For**: big data analytics, ETL pipelines, log processing, machine learning training, data lake processing, real-time streaming, batch processing, interactive data science

## Description

Terraform module that creates and manages Amazon EMR (Elastic MapReduce) resources for big data processing and analytics workloads. Amazon EMR is a managed cluster platform that simplifies running big data frameworks like Apache Hadoop, Apache Spark, Apache Hive, Presto, and Trino on AWS infrastructure. This module supports multiple deployment models including traditional EMR clusters with instance groups or instance fleets, EMR Serverless applications, EMR Studio for interactive development, and EMR on EKS (virtual clusters) for containerized workloads.

The module provides comprehensive configuration options for cluster topology, instance types, storage, networking, security, IAM roles, and application installations. It manages the complete lifecycle of EMR resources including master nodes, core nodes (for data storage and processing), and task nodes (for additional compute capacity). The module supports both long-running clusters for continuous data interaction and transient clusters that automatically terminate after job completion.

## Key Features

- **Instance Fleet Support**: Deploy clusters using instance fleets with flexible instance type configurations, spot/on-demand mix, and capacity-optimized allocation
- **Instance Group Support**: Traditional instance group deployment model with master, core, and task node groups
- **Multiple Applications**: Support for Spark, Hadoop, Hive, Presto, Trino, HBase, Flink, and 20+ big data frameworks
- **High Availability**: Configure clusters with 1 or 3 primary nodes for zero-downtime operation
- **Spot Instance Integration**: Use EC2 Spot Instances for cost-effective task nodes and optional core nodes
- **VPC Deployment**: Deploy clusters in public or private subnets with customizable security group configurations
- **Security Configuration**: Encryption at rest and in transit, Kerberos authentication, and fine-grained access control
- **IAM Role Management**: Automated creation of service roles, instance profiles, and autoscaling roles
- **Managed Scaling**: Auto-scaling policies for dynamic cluster capacity based on workload demands
- **Bootstrap Actions**: Execute custom scripts during cluster initialization
- **Step Execution**: Submit Spark jobs, Hive queries, and custom steps during cluster creation
- **S3 and CloudWatch Logging**: Log aggregation to S3 and CloudWatch Logs
- **Managed Security Groups**: Automatically create and configure security groups for master, slave, and service access
- **EMR Serverless**: Submodule for serverless Spark and Hive applications with automatic scaling
- **EMR Studio**: Submodule for interactive development environments with Jupyter notebooks
- **EMR on EKS**: Virtual cluster submodule for running EMR workloads on existing EKS clusters

## Main Use Cases

1. **Big Data Analytics**: Process and analyze petabyte-scale datasets using Hadoop, Spark, and Presto frameworks
2. **ETL Pipelines**: Extract, transform, and load data from multiple sources into data warehouses and data lakes
3. **Log Processing**: Analyze application logs, web server logs, and system logs at scale
4. **Machine Learning**: Train and deploy machine learning models using Spark MLlib on distributed infrastructure
5. **Real-time Streaming**: Process streaming data from Kinesis, Kafka using Spark Streaming or Flink
6. **Data Lake Processing**: Query and transform data stored in S3 data lakes using Spark SQL and Presto
7. **Batch Processing**: Run scheduled batch jobs with automatic cluster termination
8. **Interactive Data Science**: Provide scalable compute infrastructure for data scientists using EMR Studio notebooks

## Submodules

### 1. serverless

- **Purpose**: Creates EMR Serverless applications for running Spark or Hive workloads without managing cluster infrastructure
- **Source**: `terraform-aws-modules/emr/aws//modules/serverless`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/emr/aws/latest/submodules/serverless
- **Key Features**: Spark/Hive applications, auto-scaling, initial/maximum capacity, auto-start/stop, VPC networking, ARM64/X86_64 architectures
- **Use Cases**: Intermittent workloads, pay-per-use pricing, variable capacity needs, serverless ETL

### 2. studio

- **Purpose**: Creates EMR Studios for interactive development with Jupyter notebooks
- **Source**: `terraform-aws-modules/emr/aws//modules/studio`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/emr/aws/latest/submodules/studio
- **Key Features**: IAM/SSO authentication, workspace management, Git integration, S3 backup, session mappings, security groups
- **Use Cases**: Interactive analytics, data science workspaces, notebook development, collaborative data exploration

### 3. virtual-cluster

- **Purpose**: Creates EMR on EKS virtual clusters for running containerized EMR workloads on Amazon EKS
- **Source**: `terraform-aws-modules/emr/aws//modules/virtual-cluster`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/emr/aws/latest/submodules/virtual-cluster
- **Key Features**: Kubernetes namespace creation, IRSA support, job execution IAM role, CloudWatch logging, RBAC configuration
- **Use Cases**: Containerized EMR workloads, Kubernetes integration, multi-tenant environments, EKS-based data platforms

## Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls if resources should be created |
| `name` | `string` | - | Name of the EMR cluster/job flow (required) |
| `release_label` | `string` | `null` | EMR release version (e.g., "emr-7.0.0") |
| `applications` | `list(string)` | `[]` | Applications to install (e.g., ["spark", "trino", "hive"]) |
| `configurations_json` | `string` | `null` | JSON format application configuration overrides |
| `tags` | `map(string)` | `{}` | Tags to apply to all resources |

### Instance Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `master_instance_fleet` | `any` | `null` | Instance Fleet config for master nodes (flexible instance types) |
| `master_instance_group` | `any` | `null` | Instance Group config for master nodes (single instance type) |
| `core_instance_fleet` | `any` | `null` | Instance Fleet config for core nodes |
| `core_instance_group` | `any` | `null` | Instance Group config for core nodes |
| `task_instance_fleet` | `any` | `null` | Instance Fleet config for task nodes |
| `task_instance_group` | `any` | `null` | Instance Group config for task nodes |
| `ebs_root_volume_size` | `number` | `null` | EBS root volume size in GiB |
| `custom_ami_id` | `string` | `null` | Custom Amazon Linux AMI for cluster nodes |
| `managed_scaling_policy` | `any` | `null` | Compute limits for Managed Scaling |

### Networking

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_id` | `string` | `""` | VPC ID for security groups |
| `ec2_attributes` | `any` | `null` | EC2 instance attributes including subnet, VPC, and security groups |
| `is_private_cluster` | `bool` | `true` | Whether cluster is in private subnet |
| `create_managed_security_groups` | `bool` | `true` | Creates managed security groups |

### Security

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_security_configuration` | `bool` | `false` | Creates a security configuration resource |
| `security_configuration` | `string` | `null` | Security configuration to attach |
| `kerberos_attributes` | `any` | `null` | Kerberos configuration for cluster |
| `log_uri` | `string` | `null` | S3 bucket for job flow logs |
| `log_encryption_kms_key_id` | `string` | `null` | KMS key for encrypting logs |

### IAM

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_service_iam_role` | `bool` | `true` | Creates service IAM role |
| `service_iam_role_arn` | `string` | `null` | Existing service role ARN to use |
| `create_autoscaling_iam_role` | `bool` | `true` | Creates autoscaling IAM role |
| `create_iam_instance_profile` | `bool` | `true` | Creates EC2 IAM instance profile |
| `iam_role_permissions_boundary` | `string` | `null` | Permissions boundary policy ARN |

### Cluster Lifecycle

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `termination_protection` | `bool` | `null` | Prevents accidental cluster termination |
| `keep_job_flow_alive_when_no_steps` | `bool` | `null` | Keep cluster running without active steps |
| `auto_termination_policy` | `any` | `null` | Automatic termination after idle time |
| `step_concurrency_level` | `number` | `null` | Number of steps executable concurrently (max 256) |
| `bootstrap_action` | `list(any)` | `null` | Bootstrap actions before Hadoop starts |
| `step` | `list(any)` | `null` | Steps to run during cluster creation |

## Outputs

| Output | Description |
|--------|-------------|
| `cluster_id` | The ID of the EMR cluster |
| `cluster_arn` | The ARN of the EMR cluster |
| `cluster_master_public_dns` | Master node DNS name |
| `cluster_core_instance_group_id` | Core node Instance Group ID |
| `cluster_master_instance_group_id` | Master node Instance Group ID |
| `security_configuration_id` | The ID of the security configuration |
| `security_configuration_name` | The name of the security configuration |
| `service_iam_role_name` | Service IAM role name |
| `service_iam_role_arn` | Service IAM role ARN |
| `autoscaling_iam_role_name` | Autoscaling IAM role name |
| `autoscaling_iam_role_arn` | Autoscaling IAM role ARN |
| `iam_instance_profile_arn` | ARN of the instance profile |
| `iam_instance_profile_iam_role_arn` | Instance profile IAM role ARN |
| `managed_master_security_group_id` | ID of the managed master security group |
| `managed_slave_security_group_id` | ID of the managed slave security group |
| `managed_service_access_security_group_id` | ID of the managed service access security group |

## Usage Examples

### Basic EMR Cluster with Instance Fleet

```hcl
module "emr_cluster" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 3.2"

  name          = "analytics-cluster"
  release_label = "emr-7.0.0"
  applications  = ["spark", "hadoop"]

  vpc_id = module.vpc.vpc_id

  master_instance_fleet = {
    name                      = "master-fleet"
    target_on_demand_capacity = 1
    instance_type_configs = [{
      instance_type = "m5.xlarge"
    }]
  }

  core_instance_fleet = {
    name                      = "core-fleet"
    target_on_demand_capacity = 2
    target_spot_capacity      = 2
    instance_type_configs = [{
      instance_type     = "m5.xlarge"
      weighted_capacity = 1
      bid_price_as_percentage_of_on_demand_price = 100
    }]
  }

  ec2_attributes = {
    subnet_id = module.vpc.private_subnets[0]
  }

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/logs/"

  tags = {
    Environment = "production"
  }
}
```

### EMR Cluster with Instance Groups and Spot Task Nodes

```hcl
module "emr_spot" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 3.2"

  name          = "cost-optimized-cluster"
  release_label = "emr-7.0.0"
  applications  = ["spark"]

  vpc_id = module.vpc.vpc_id

  master_instance_group = {
    instance_type = "m5.xlarge"
  }

  core_instance_group = {
    instance_count = 2
    instance_type  = "m5.xlarge"
    ebs_config = [{
      size                 = 200
      type                 = "gp3"
      volumes_per_instance = 1
    }]
  }

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

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/spot-cluster/"

  tags = {
    Environment   = "development"
    CostOptimized = "true"
  }
}
```

### EMR Cluster with Bootstrap Actions and Steps

```hcl
module "emr_etl" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 3.2"

  name          = "etl-cluster"
  release_label = "emr-7.0.0"
  applications  = ["spark"]

  vpc_id = module.vpc.vpc_id

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

  step_concurrency_level = 3

  ec2_attributes = {
    subnet_id = module.vpc.private_subnets[0]
  }

  # Terminate cluster after steps complete
  keep_job_flow_alive_when_no_steps = false

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/etl/"

  tags = {
    Environment = "production"
    Workload    = "etl"
  }
}
```

### EMR Serverless Application

```hcl
module "emr_serverless" {
  source  = "terraform-aws-modules/emr/aws//modules/serverless"
  version = "~> 3.2"

  name          = "spark-analytics"
  type          = "spark"
  release_label = "emr-7.0.0"
  architecture  = "X86_64"

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

  maximum_capacity = {
    cpu    = "48 vCPU"
    memory = "144 GB"
    disk   = "1000 GB"
  }

  network_configuration = {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [aws_security_group.emr_serverless.id]
  }

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

### EMR Studio

```hcl
module "emr_studio" {
  source  = "terraform-aws-modules/emr/aws//modules/studio"
  version = "~> 3.2"

  name                = "data-science-studio"
  auth_mode           = "SSO"
  default_s3_location = "s3://${aws_s3_bucket.notebooks.id}/studios/"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  idp_auth_url                   = "https://my-idp.com/auth"
  idp_relay_state_parameter_name = "RelayState"

  session_mappings = {
    data_scientists = {
      identity_type      = "GROUP"
      identity_id        = "data-scientists-group-id"
      session_policy_arn = aws_iam_policy.data_scientist_policy.arn
    }
  }

  service_role_s3_bucket_arns = [aws_s3_bucket.notebooks.arn]
  user_role_s3_bucket_arns    = [aws_s3_bucket.notebooks.arn]

  tags = {
    Environment = "production"
    Team        = "data-science"
  }
}
```

### EMR on EKS Virtual Cluster

```hcl
module "emr_eks" {
  source  = "terraform-aws-modules/emr/aws//modules/virtual-cluster"
  version = "~> 3.2"

  name                  = "emr-on-eks"
  namespace             = "emr-spark"
  eks_cluster_name      = module.eks.cluster_name
  eks_oidc_provider_arn = module.eks.oidc_provider_arn

  create_namespace       = true
  create_kubernetes_role = true
  create_iam_role        = true

  s3_bucket_arns = [
    "arn:aws:s3:::my-data-lake",
    "arn:aws:s3:::my-data-lake/*",
    "arn:aws:s3:::my-logs-bucket",
    "arn:aws:s3:::my-logs-bucket/*"
  ]

  create_cloudwatch_log_group            = true
  cloudwatch_log_group_retention_in_days = 7

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
```

## Best Practices

### Cluster Planning

1. **Choose Deployment Model**: Use instance fleets for flexible capacity and spot/on-demand mix; use instance groups for simpler single instance type configurations
2. **Right-Size Instances**: Use m5/m6i for balanced workloads, r5/r6i for memory-intensive (Spark), c5/c6i for compute-intensive
3. **Use Private Clusters**: Deploy in private subnets with NAT gateway or VPC endpoints for S3 and EMR
4. **Plan Storage**: Core nodes provide HDFS storage; configure EBS volumes based on data volume and replication factor

### Cost Optimization

5. **Use Spot Instances**: Configure task nodes with spot instances for up to 90% cost savings
6. **Enable Auto-Termination**: Set `auto_termination_policy` or `keep_job_flow_alive_when_no_steps = false` for batch jobs
7. **Use Managed Scaling**: Enable `managed_scaling_policy` for automatic capacity adjustment
8. **Consider EMR Serverless**: For intermittent workloads, EMR Serverless provides pay-per-use pricing
9. **Use Graviton Instances**: m6g/r6g instances provide 20-30% better price-performance

### Security

10. **Enable Encryption**: Use security configuration for encryption at rest and in transit
11. **Tag VPC Resources**: VPC and subnets must have tag `"for-use-with-amazon-emr-managed-policies" = true` when using managed security groups
12. **Restrict Security Groups**: Default egress allows all traffic; restrict based on requirements
13. **Enable Termination Protection**: Set `termination_protection = true` for production clusters
14. **Use KMS Encryption**: Configure `log_encryption_kms_key_id` for encrypted logs

### Operations

15. **Enable Logging**: Always configure `log_uri` for S3 log aggregation
16. **Use Bootstrap Actions**: Install dependencies and configure software before Hadoop starts
17. **Set Step Concurrency**: Configure `step_concurrency_level` for parallel step execution
18. **Monitor with CloudWatch**: Enable CloudWatch metrics and set alarms for cluster health

## Important Notes

1. **Instance Fleet vs Instance Group**: Cannot mix fleets and groups in the same cluster. Fleets offer more flexibility; groups are simpler.

2. **VPC Tagging Required**: When using managed security groups, tag VPC and subnets with:
   ```
   "for-use-with-amazon-emr-managed-policies" = true
   ```

3. **Termination Protection**: If enabled, must be disabled before `terraform destroy` will succeed.

4. **Security Group Defaults**: All managed security groups allow unrestricted egress (`0.0.0.0/0`) by default.

5. **Release Label**: Use specific version (e.g., `"emr-7.0.0"`) or `release_label_filters` for automatic selection.

6. **IAM Policies**: Module uses AWS managed policies (`AmazonEMRServicePolicy_v2`, `AmazonElasticMapReduceforEC2Role`) by default.

## Additional Resources

- **AWS EMR Documentation**: https://docs.aws.amazon.com/emr/
- **Terraform Registry - EMR Module**: https://registry.terraform.io/modules/terraform-aws-modules/emr/aws
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-emr
- **EMR Release Guide**: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/
- **EMR Best Practices**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan.html
- **EMR Security Guide**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-security.html
- **EMR Serverless**: https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/
- **EMR on EKS**: https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/
- **EMR Studio**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-studio.html
- **EMR Pricing**: https://aws.amazon.com/emr/pricing/

## Notes for AI Agents

### Module Selection

- **Use main EMR module** for traditional Hadoop/Spark clusters with persistent HDFS storage
- **Use EMR Serverless** for intermittent workloads with automatic scaling and pay-per-use pricing
- **Use EMR Studio** for interactive notebook environments for data scientists
- **Use EMR on EKS** for containerized workloads on existing Kubernetes infrastructure

### Common Configuration Patterns

- **Development**: Single master m5.xlarge, 2 core m5.xlarge, auto-terminate after 1 hour idle
- **Production**: 3 master m5.xlarge (HA), 5+ core r5.xlarge, termination protection enabled
- **Batch ETL**: 1 master, 2-3 core nodes, terminate after steps complete
- **Cost-Optimized**: On-demand master/core, spot task nodes with fallback to on-demand

### Instance Type Selection

- **Master nodes**: m5.xlarge (small), m5.2xlarge (medium), m5.4xlarge (large clusters)
- **Spark workloads**: r5/r6i (memory-optimized) for in-memory processing
- **Compute-intensive**: c5/c6i family for CPU-heavy transformations
- **Cost optimization**: Graviton m6g/r6g for 20-30% savings

### Troubleshooting

- **Cluster stuck in STARTING**: Check VPC/subnet configuration, NAT gateway, EMR service role permissions
- **Steps failing**: Review logs in S3 `log_uri`, check S3 bucket permissions
- **Out of memory**: Increase executor memory, use larger instance types, enable dynamic allocation
- **Security group issues**: Ensure managed security groups allow master/core/task communication
