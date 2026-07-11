# Terraform AWS EMR Module

## Module Information

- **Module Name**: `emr`
- **Source**: `terraform-aws-modules/emr/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-emr
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/emr/aws/latest
- **Latest Version**: 3.3.0
- **Terraform**: >= 1.5.7
- **AWS Provider**: >= 6.35 (root module and `serverless` submodule; `studio` and `virtual-cluster` submodules declare >= 6.28 but should be run with the same provider version as the root module). The `virtual-cluster` submodule also requires the Kubernetes provider >= 2.38.
- **Purpose**: Creates and manages Amazon EMR resources for big data processing and analytics workloads
- **Service**: AWS EMR (Elastic MapReduce)
- **Category**: Analytics, Big Data, Compute
- **Keywords**: emr, elastic-mapreduce, spark, hadoop, hive, presto, trino, big-data, analytics, instance-fleet, instance-group, hdfs, emr-serverless, emr-studio, emr-on-eks, eks, managed-scaling, spot-instances
- **Use For**: big data analytics, ETL pipelines, log processing, machine learning training, data lake processing, real-time streaming, batch processing, interactive data science, ad-hoc SQL on S3

## Description

Terraform module that creates and manages Amazon EMR (Elastic MapReduce) resources for big data processing and analytics workloads. Amazon EMR is a managed cluster platform that simplifies running big data frameworks like Apache Spark, Apache Hadoop, Apache Hive, Presto, and Trino on AWS infrastructure. The root module provisions traditional EMR clusters (`aws_emr_cluster`) using either instance fleets or instance groups, while three companion submodules cover EMR Serverless applications, EMR Studio workspaces, and EMR on EKS virtual clusters, letting a single module family cover every EMR deployment model.

The root module manages the full lifecycle of a cluster: master nodes, core nodes (HDFS storage + compute), and task nodes (compute-only), plus the supporting IAM service/autoscaling/instance-profile roles, managed security groups (master, slave, service-access) with fully customizable ingress/egress rules, security configurations (encryption at rest/in transit, Kerberos), managed scaling policies, bootstrap actions, and steps. It supports both long-running interactive clusters and transient clusters that auto-terminate after their steps complete. When `release_label` is left unset, the module can auto-select the newest matching EMR release via the `aws_emr_release_labels` data source and `release_label_filters` (default prefix `"emr-7"`).

The module follows terraform-aws-modules conventions: nearly every resource group can be toggled off with a `create_*` flag so existing IAM roles, security groups, or security configurations can be supplied externally, and security group rules use the modern `aws_vpc_security_group_ingress_rule` / `aws_vpc_security_group_egress_rule` resource types (split into separate `*_ingress_rules` / `*_egress_rules` map variables) rather than the legacy inline `aws_security_group` rule blocks.

## Key Features

- **Instance Fleet Support**: Flexible instance-type mixes with spot/on-demand target capacity and capacity-optimized allocation strategies
- **Instance Group Support**: Simpler, single-instance-type master/core/task node groups (mutually exclusive with fleets per node type)
- **Automatic Release Label Selection**: Looks up the latest EMR release via `aws_emr_release_labels` and `release_label_filters` when `release_label` is not pinned
- **Multiple Applications**: Spark, Hadoop, Hive, Presto, Trino, HBase, Flink, JupyterHub, Zeppelin, and other frameworks via `applications`
- **Managed Scaling**: Auto-scaling with compute-unit limits, `scaling_strategy`, and `utilization_performance_index`
- **Spot Instance Integration**: Cost-effective task/core capacity with configurable spot allocation strategy and timeout fallback to on-demand
- **VPC Deployment**: Public or private subnets, with granular ingress/egress security group rules for master, slave (core+task), and service-access security groups
- **Managed Security Groups**: Auto-created master/slave/service-access security groups (requires VPC/subnet tag `"for-use-with-amazon-emr-managed-policies" = true`)
- **Security Configuration & Encryption**: At-rest/in-transit encryption, Kerberos authentication, KMS-encrypted logs
- **IAM Role Automation**: Service role, autoscaling role, and EC2 instance profile created with sensible managed-policy defaults, or bring-your-own ARNs
- **Bootstrap Actions & Steps**: Run custom scripts before Hadoop starts and submit Spark/Hive/custom steps at cluster creation
- **Placement Groups & Custom AMIs**: Optional EC2 placement group configuration and custom Amazon Linux AMI per cluster
- **EMR Serverless Submodule**: Auto-scaling Spark/Hive applications with pay-per-use pricing, VPC connectivity, and job-level cost allocation tagging
- **EMR Studio Submodule**: IAM or SSO authenticated notebook workspaces with Git integration and session-based access control
- **EMR on EKS Submodule**: Virtual clusters on existing EKS clusters with namespace, RBAC, IRSA-style job execution role, and CloudWatch log group creation

## Main Use Cases

1. **Big Data Analytics**: Process and analyze large datasets using Hadoop, Spark, and Presto/Trino
2. **ETL Pipelines**: Extract, transform, and load data from multiple sources into data warehouses and data lakes
3. **Log Processing**: Analyze application, web server, and system logs at scale
4. **Machine Learning**: Train and deploy models using Spark MLlib on distributed infrastructure
5. **Real-time Streaming**: Process streaming data from Kinesis/Kafka using Spark Streaming or Flink
6. **Data Lake Processing**: Query and transform S3-resident data using Spark SQL, Presto, or Trino
7. **Batch Processing**: Run scheduled batch jobs on transient clusters that auto-terminate after steps complete
8. **Interactive Data Science**: Provide scalable notebook infrastructure via EMR Studio
9. **Containerized Big Data**: Run EMR jobs on existing Kubernetes/EKS infrastructure for multi-tenant, shared-cluster workloads

## Submodules

### 1. serverless

- **Purpose**: Creates EMR Serverless applications for running Spark or Hive workloads without managing cluster infrastructure
- **Source**: `terraform-aws-modules/emr/aws//modules/serverless`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/emr/aws/latest/submodules/serverless
- **Key Features**: Spark/Hive/HiveDriver+TezTask applications, initial/maximum capacity, auto-start/auto-stop, VPC networking, ARM64/X86_64 architecture, CloudWatch/S3/Prometheus monitoring, job-level cost allocation
- **Use Cases**: Intermittent workloads, pay-per-use pricing, variable capacity needs, serverless ETL

### 2. studio

- **Purpose**: Creates EMR Studios for interactive development with Jupyter notebooks
- **Source**: `terraform-aws-modules/emr/aws//modules/studio`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/emr/aws/latest/submodules/studio
- **Key Features**: IAM or SSO authentication, per-identity session mappings, S3-backed workspace storage, IdP federation, engine/workspace security groups
- **Use Cases**: Interactive analytics, data science workspaces, notebook development, collaborative data exploration

### 3. virtual-cluster

- **Purpose**: Creates EMR on EKS virtual clusters for running containerized EMR workloads on an existing Amazon EKS cluster
- **Source**: `terraform-aws-modules/emr/aws//modules/virtual-cluster`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/emr/aws/latest/submodules/virtual-cluster
- **Key Features**: Kubernetes namespace/RBAC role creation, IAM job execution role scoped to the namespace, S3 bucket access policy, dedicated CloudWatch log group
- **Use Cases**: Containerized EMR workloads, multi-tenant EKS-based data platforms, shared-cluster cost optimization

## Main Input Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Controls if resources should be created |
| `name` | `string` | `""` | Name of the job flow (cluster) |
| `release_label` | `string` | `null` | Explicit EMR release label (e.g., `"emr-7.9.0"`); if omitted, the module resolves one via `release_label_filters` |
| `release_label_filters` | `map(object)` | `{ default = { prefix = "emr-7" } }` | Filters used to auto-select the latest matching release label when `release_label` is not set |
| `applications` | `list(string)` | `[]` | Applications to install (e.g., `["spark", "trino", "hive"]`) |
| `configurations_json` | `string` | `null` | JSON string of application configuration overrides |
| `os_release_label` | `string` | `null` | Amazon Linux release used for cluster node AMIs |
| `region` | `string` | `null` | AWS region for the resources, if different from the provider region |
| `tags` | `map(string)` | `{}` | Tags applied to all resources |

### Instance Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `master_instance_fleet` / `master_instance_group` | `object` | `null` | Master node config; fleet = flexible instance types + spot mix, group = single instance type |
| `core_instance_fleet` / `core_instance_group` | `object` | `null` | Core node config (HDFS storage + compute); mutually exclusive with each other |
| `task_instance_fleet` / `task_instance_group` | `object` | `null` | Task node config (compute-only, no HDFS) |
| `ebs_root_volume_size` | `number` | `null` | EBS root volume size in GiB |
| `custom_ami_id` | `string` | `null` | Custom Amazon Linux AMI for cluster nodes |
| `managed_scaling_policy` | `object` | `null` | Managed Scaling compute limits, `scaling_strategy`, and `utilization_performance_index` |
| `placement_group_config` | `list(object)` | `null` | EC2 placement group strategy per instance role (master/core/task) |
| `unhealthy_node_replacement` | `bool` | `true` | Automatically replace degraded core nodes |

### Networking & Security Groups

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `vpc_id` | `string` | `""` | VPC ID used to create managed security groups |
| `ec2_attributes` | `object` | `null` | Subnet ID(s), key pair, and (optionally) existing security group/instance-profile overrides |
| `is_private_cluster` | `bool` | `true` | Deploy in private subnet(s); set `false` for a public cluster |
| `create_managed_security_groups` | `bool` | `true` | Create master/slave/service-access managed security groups |
| `master_security_group_egress_rules` / `master_security_group_ingress_rules` | `map(object)` | open egress / `null` | Extra rules on the managed master security group |
| `slave_security_group_egress_rules` / `slave_security_group_ingress_rules` | `map(object)` | open egress / `null` | Extra rules on the managed slave (core+task) security group |
| `service_security_group_egress_rules` / `service_security_group_ingress_rules` | `map(object)` | open egress / `null` | Extra rules on the managed service-access security group (private clusters) |

### Security & Encryption

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_security_configuration` | `bool` | `false` | Create an EMR security configuration resource |
| `security_configuration` | `string` | `null` | Security configuration JSON to create, or attach if `create_security_configuration = false` |
| `kerberos_attributes` | `object` | `null` | Kerberos realm/KDC configuration for the cluster |
| `log_uri` | `string` | `null` | S3 URI to write job flow logs |
| `log_encryption_kms_key_id` | `string` | `null` | KMS key ARN/ID used to encrypt logs |

### IAM

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create_service_iam_role` | `bool` | `true` | Create the EMR service IAM role |
| `service_iam_role_arn` | `string` | `null` | Existing service role ARN to use instead of creating one |
| `service_iam_role_policies` | `map(string)` | `{ AmazonEMRServicePolicy_v2 = ... }` | Managed policies attached to the service role |
| `create_autoscaling_iam_role` | `bool` | `true` | Create the autoscaling IAM role |
| `create_iam_instance_profile` | `bool` | `true` | Create the EC2 IAM role/instance profile |
| `iam_instance_profile_policies` | `map(string)` | `{ AmazonElasticMapReduceforEC2Role = ... }` | Managed policies attached to the instance profile role |
| `iam_role_permissions_boundary` | `string` | `null` | Permissions boundary ARN applied to all IAM roles created |

### Cluster Lifecycle

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `termination_protection` | `bool` | `null` | Prevent accidental termination; must be set to `false` before `terraform destroy` |
| `keep_job_flow_alive_when_no_steps` | `bool` | `null` | Keep the cluster running when there are no active steps |
| `auto_termination_policy` | `object({ idle_timeout })` | `null` | Automatic termination after N idle seconds |
| `step_concurrency_level` | `number` | `null` | Concurrently executable steps (max 256) |
| `bootstrap_action` | `list(object)` | `null` | Scripts run before Hadoop starts on cluster nodes |
| `step` | `list(object)` | `null` | Steps submitted at cluster creation |
| `scale_down_behavior` | `string` | `"TERMINATE_AT_TASK_COMPLETION"` | How EC2 instances terminate on scale-in |
| `visible_to_all_users` | `bool` | `null` (AWS default `true`) | Whether the job flow is visible to all IAM users in the account |
| `list_steps_states` | `list(string)` | `[]` | Step states used to filter the `steps` data returned by the provider |

## Main Outputs

| Output | Description |
|--------|-------------|
| `cluster_id` | The ID of the EMR cluster |
| `cluster_arn` | The ARN of the EMR cluster |
| `cluster_master_public_dns` | Master node DNS name (private DNS on private clusters) |
| `cluster_core_instance_group_id` | Core node Instance Group ID (when using Instance Groups) |
| `cluster_master_instance_group_id` | Master node Instance Group ID (when using Instance Groups) |
| `security_configuration_id` / `security_configuration_name` | ID/name of the security configuration |
| `service_iam_role_name` / `service_iam_role_arn` | Service IAM role name/ARN |
| `autoscaling_iam_role_name` / `autoscaling_iam_role_arn` | Autoscaling IAM role name/ARN |
| `iam_instance_profile_arn` / `iam_instance_profile_iam_role_arn` | Instance profile ARN / instance profile's IAM role ARN |
| `managed_master_security_group_id` | ID of the managed master security group |
| `managed_slave_security_group_id` | ID of the managed slave (core+task) security group |
| `managed_service_access_security_group_id` | ID of the managed service-access security group |

## Usage Examples

### Private Cluster with Instance Fleets (Spot Mix)

```hcl
module "emr" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 3.3"

  name          = "analytics-cluster"
  release_label = "emr-7.9.0"
  applications  = ["spark", "trino"]

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
      instance_type                              = "m5.xlarge"
      weighted_capacity                          = 1
      bid_price_as_percentage_of_on_demand_price = 100
    }]
    launch_specifications = {
      spot_specification = {
        allocation_strategy      = "capacity-optimized"
        timeout_action           = "SWITCH_TO_ON_DEMAND"
        timeout_duration_minutes = 5
      }
    }
  }

  ec2_attributes = {
    # Subnets must be tagged { "for-use-with-amazon-emr-managed-policies" = true }
    subnet_ids = module.vpc.private_subnets
  }

  auto_termination_policy = {
    idle_timeout = 3600
  }

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/logs/"

  tags = {
    Environment = "production"
  }
}
```

### Cluster with Instance Groups and Spot Task Nodes

```hcl
module "emr_spot" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 3.3"

  name          = "cost-optimized-cluster"
  release_label = "emr-7.9.0"
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

  task_instance_group = {
    instance_count = 5
    instance_type  = "m5.2xlarge"
    bid_price      = "0.30"
    ebs_config = [{
      size                 = 100
      type                 = "gp3"
      volumes_per_instance = 1
    }]
  }

  ec2_attributes = {
    # Instance groups only support one subnet/AZ
    subnet_id = module.vpc.private_subnets[0]
  }

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/spot-cluster/"

  tags = {
    Environment   = "development"
    CostOptimized = "true"
  }
}
```

### Bootstrap Actions and Steps (Transient ETL Cluster)

```hcl
module "emr_etl" {
  source  = "terraform-aws-modules/emr/aws"
  version = "~> 3.3"

  name          = "etl-cluster"
  release_label = "emr-7.9.0"
  applications  = ["spark"]

  vpc_id = module.vpc.vpc_id

  master_instance_group = {
    instance_type = "m5.xlarge"
  }

  core_instance_group = {
    instance_count = 3
    instance_type  = "m5.xlarge"
  }

  bootstrap_action = [{
    name = "Install Python packages"
    path = "s3://${aws_s3_bucket.scripts.id}/bootstrap/install-packages.sh"
    args = ["pandas", "numpy", "scikit-learn"]
  }]

  step = [{
    name              = "Process daily data"
    action_on_failure = "CONTINUE"
    hadoop_jar_step = {
      jar  = "command-runner.jar"
      args = [
        "spark-submit",
        "--deploy-mode", "cluster",
        "--master", "yarn",
        "s3://${aws_s3_bucket.scripts.id}/jobs/daily-etl.py"
      ]
    }
  }]

  step_concurrency_level             = 3
  keep_job_flow_alive_when_no_steps  = false # terminate once steps complete

  ec2_attributes = {
    subnet_id = module.vpc.private_subnets[0]
  }

  log_uri = "s3://${aws_s3_bucket.emr_logs.id}/etl/"

  tags = {
    Environment = "production"
    Workload    = "etl"
  }
}
```

### EMR Serverless Application (Spark)

```hcl
module "emr_serverless" {
  source  = "terraform-aws-modules/emr/aws//modules/serverless"
  version = "~> 3.3"

  name          = "spark-analytics"
  type          = "spark"
  release_label = "emr-7.9.0"
  architecture  = "X86_64"

  initial_capacity = {
    driver = {
      initial_capacity_type = "Driver"
      initial_capacity_config = {
        worker_count = 2
        worker_configuration = {
          cpu    = "4 vCPU"
          memory = "12 GB"
        }
      }
    }
    executor = {
      initial_capacity_type = "Executor"
      initial_capacity_config = {
        worker_count = 2
        worker_configuration = {
          cpu    = "8 vCPU"
          memory = "24 GB"
          disk   = "64 GB"
        }
      }
    }
  }

  maximum_capacity = {
    cpu    = "48 vCPU"
    memory = "144 GB"
  }

  network_configuration = {
    subnet_ids = module.vpc.private_subnets
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

### EMR Studio (SSO Authentication)

```hcl
module "emr_studio" {
  source  = "terraform-aws-modules/emr/aws//modules/studio"
  version = "~> 3.3"

  name                = "data-science-studio"
  auth_mode           = "SSO"
  default_s3_location = "s3://${aws_s3_bucket.notebooks.id}/studios/"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  session_mappings = {
    data_scientists = {
      identity_type = "GROUP"
      identity_id   = "012345678f-987a65b4-3210-4567-b5a6-12ab345c6d78"
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
module "emr_virtual_cluster" {
  source  = "terraform-aws-modules/emr/aws//modules/virtual-cluster"
  version = "~> 3.3"

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

1. **Choose Deployment Model**: Use instance fleets for flexible capacity and spot/on-demand mixes; use instance groups for simpler single-instance-type configurations
2. **Right-Size Instances**: `m5`/`m6i` for balanced workloads, `r5`/`r6i` for memory-intensive Spark, `c5`/`c6i` for compute-intensive transforms
3. **Use Private Clusters**: Deploy in private subnets with a NAT gateway or S3/EMR VPC endpoints
4. **Plan Storage**: Core nodes provide HDFS storage; size EBS volumes based on data volume and replication factor
5. **Pin Release Labels in Production**: Set `release_label` explicitly rather than relying on `release_label_filters` auto-selection, which can change between applies

### Cost Optimization

6. **Use Spot Instances**: Configure task (and optionally core) nodes with spot capacity for significant cost savings
7. **Enable Auto-Termination**: Set `auto_termination_policy` or `keep_job_flow_alive_when_no_steps = false` for batch/ETL jobs
8. **Use Managed Scaling**: Enable `managed_scaling_policy` for automatic capacity adjustment
9. **Consider EMR Serverless**: For intermittent workloads, EMR Serverless provides pay-per-use pricing without cluster management
10. **Use Graviton Instances**: `m6g`/`r6g` instances typically provide better price-performance than `m5`/`r5`

### Security

11. **Enable Encryption**: Use a security configuration (`create_security_configuration = true`) for encryption at rest and in transit
12. **Tag VPC Resources**: VPC and subnets must have `"for-use-with-amazon-emr-managed-policies" = true` when using managed security groups
13. **Restrict Egress**: Default managed security groups allow all outbound traffic (`0.0.0.0/0`); override via `*_security_group_egress_rules` to restrict
14. **Add Custom Ingress via Variables**: Use `master_security_group_ingress_rules` (e.g., SSH from a bastion) instead of managing separate `aws_security_group_rule` resources
15. **Enable Termination Protection**: Set `termination_protection = true` for production clusters
16. **Use KMS Encryption for Logs**: Configure `log_encryption_kms_key_id`

### Operations

17. **Enable Logging**: Always configure `log_uri` for S3 log aggregation
18. **Use Bootstrap Actions**: Install dependencies and configure software before Hadoop starts
19. **Set Step Concurrency**: Configure `step_concurrency_level` for parallel step execution
20. **Monitor with CloudWatch**: Enable CloudWatch metrics/log delivery and alarm on cluster health for long-running clusters

## Important Gotchas

1. **Instance Fleet vs Instance Group**: A node type (master/core/task) can use a fleet or a group, but not both; fleets offer more flexibility, groups are simpler.

2. **VPC Tagging Required for Managed Security Groups**:
   ```
   "for-use-with-amazon-emr-managed-policies" = true
   ```
   applied to the VPC and subnets used by the cluster.

3. **Termination Protection**: If enabled, it must be set to `false` and applied before `terraform destroy` will succeed.

4. **v3.0 Breaking Changes (upgrading from v2.x)**: Security group rule variables were split from `*_security_group_rules` into separate `*_security_group_ingress_rules` / `*_security_group_egress_rules` maps (root, `serverless`, and `studio` modules); the `virtual-cluster` submodule renamed `eks_cluster_id` -> `eks_cluster_name` and `oidc_provider_arn` -> `eks_oidc_provider_arn`; the `serverless` submodule renamed `release_label_prefix` -> `release_label_filters`; minimum Terraform is now `1.5.7` and minimum AWS provider `6.19`+ (root/serverless now require `6.35`+). See `docs/UPGRADE-3.0.md` in the GitHub repo for the full list.

5. **Release Label Resolution**: If `release_label` is `null`, the module resolves the latest release via `aws_emr_release_labels` using `release_label_filters` (default `prefix = "emr-7"`). Set `release_label` explicitly for reproducible cluster builds.

6. **Security Group Egress Defaults**: All managed security groups allow unrestricted egress (`0.0.0.0/0`) by default; tighten via the `*_egress_rules` variables if required.

7. **IAM Policies**: The module attaches AWS managed policies (`AmazonEMRServicePolicy_v2` for the service role, `AmazonElasticMapReduceforEC2Role` for the instance profile role) by default; override via `service_iam_role_policies` / `iam_instance_profile_policies`.

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-emr
- **Terraform Registry - EMR Module**: https://registry.terraform.io/modules/terraform-aws-modules/emr/aws
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-emr/tree/master/examples
- **v3.0 Upgrade Guide**: https://github.com/terraform-aws-modules/terraform-aws-emr/blob/master/docs/UPGRADE-3.0.md
- **AWS EMR Documentation**: https://docs.aws.amazon.com/emr/
- **EMR Release Guide**: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/
- **EMR Best Practices**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan.html
- **EMR Security Guide**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-security.html
- **EMR Serverless User Guide**: https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/
- **EMR on EKS Development Guide**: https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/
- **EMR Studio Guide**: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-studio.html
- **EMR Pricing**: https://aws.amazon.com/emr/pricing/

## Notes for AI Agents

### Module Selection

- **Use the root EMR module** for traditional Hadoop/Spark clusters with persistent HDFS storage
- **Use `//modules/serverless`** for intermittent workloads with automatic scaling and pay-per-use pricing
- **Use `//modules/studio`** for interactive notebook environments for data scientists
- **Use `//modules/virtual-cluster`** for containerized workloads on an existing EKS cluster

### Common Configuration Patterns

- **Development**: Single master `m5.xlarge`, 2 core `m5.xlarge`, `auto_termination_policy.idle_timeout` around 3600s
- **Production**: 3 master nodes for HA (via `master_instance_group.instance_count = 3` or fleet equivalent), 5+ core `r5.xlarge`, `termination_protection = true`
- **Batch ETL**: 1 master, 2-3 core nodes, `keep_job_flow_alive_when_no_steps = false`
- **Cost-Optimized**: On-demand master/core, spot task nodes with `timeout_action = "SWITCH_TO_ON_DEMAND"` fallback

### Instance Type Selection

- **Master nodes**: `m5.xlarge` (small), `m5.2xlarge` (medium), `m5.4xlarge` (large clusters)
- **Spark workloads**: `r5`/`r6i` (memory-optimized) for in-memory processing
- **Compute-intensive**: `c5`/`c6i` family for CPU-heavy transformations
- **Cost optimization**: Graviton `m6g`/`r6g` for better price-performance

### Version Pinning

- Pin the module with `version = "~> 3.3"` (or the current major) and set `release_label` explicitly rather than relying on `release_label_filters` for reproducible infrastructure.
- When generating code against this module, use the split `*_security_group_ingress_rules` / `*_security_group_egress_rules` variable names (not the legacy singular `*_security_group_rules`), and `eks_cluster_name` / `eks_oidc_provider_arn` for the `virtual-cluster` submodule.

### Troubleshooting

- **Cluster stuck in STARTING**: Check VPC/subnet configuration, NAT gateway, EMR service role permissions, and that subnets carry the `for-use-with-amazon-emr-managed-policies` tag
- **Steps failing**: Review logs in the S3 `log_uri` location, check S3 bucket permissions for the instance profile role
- **Out of memory**: Increase executor memory, use larger instance types, enable dynamic allocation
- **Security group issues**: Confirm managed security groups allow master/core/task inter-node communication; custom ingress rules are additive, not replacements
