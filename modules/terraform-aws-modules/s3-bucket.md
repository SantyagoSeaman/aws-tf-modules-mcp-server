# Terraform AWS S3 Bucket Module

## Module Information

- **Module Name**: `s3-bucket`
- **Module ID**: `terraform-aws-modules/s3-bucket/aws`
- **Source**: `terraform-aws-modules/s3-bucket/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-s3-bucket
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest
- **Latest Version**: 5.15.1
- **Purpose**: Terraform module that creates and configures AWS S3 buckets (standard, S3 Express directory buckets, S3 Table buckets, and S3 Vectors buckets) with nearly all features exposed by the AWS provider
- **Service**: AWS S3 (Simple Storage Service)
- **Category**: Storage, Object Storage
- **Keywords**: s3, bucket, object-storage, versioning, encryption, kms, lifecycle, replication, static-website, logging, object-lock, public-access-block, directory-bucket, table-bucket, s3-vectors, notifications, cors
- **Use For**: static website hosting, centralized log aggregation (ELB/ALB/CloudFront/WAF/CloudTrail), application data and user-upload storage, backup and archival with tiered lifecycle rules, cross-region disaster recovery via replication, compliance/immutable (WORM) storage, event-driven processing via S3 notifications, low-latency S3 Express One Zone workloads, analytics data lakes via S3 Table Buckets, vector embedding storage for AI/ML similarity search

## Description

This module provisions and configures an AWS S3 bucket along with (almost) every S3 sub-resource exposed by the Terraform AWS provider: versioning, server-side encryption, object lock, lifecycle rules, replication (CRR/SRR), static website hosting, CORS, access logging, transfer acceleration, request payer, analytics/inventory/intelligent-tiering/metrics configurations, public access blocking, ACLs/grants, and a large library of pre-built bucket policies (deny insecure transport, require latest TLS, ELB/ALB/WAF/CloudTrail/S3 log delivery, and more). A single `bucket` resource block is configured through dozens of composable input variables so that simple and highly complex bucket configurations share the same interface.

Beyond the standard bucket, the root module also manages **S3 Directory Buckets** (S3 Express One Zone, set via `is_directory_bucket = true`) for high-throughput, single-digit-millisecond-latency workloads. Four additional resource types — bucket notifications, bucket objects, account-level public access blocks, S3 Table Buckets, and S3 Vectors vector buckets — live in dedicated submodules so they can be created and versioned independently of the bucket itself.

The module ships secure defaults: all four public access block settings (`block_public_acls`, `block_public_policy`, `ignore_public_acls`, `restrict_public_buckets`) default to `true`, and `object_ownership` defaults to `BucketOwnerEnforced` (ACLs disabled, bucket owner always owns objects). It also supports `create_bucket = false` for conditional creation across environments (Terraform does not allow `count` directly on a `module` block), and Terragrunt-friendly `jsonencode()` string inputs for `any`-typed variables such as `lifecycle_rule` and `cors_rule`.

## Key Features

- **Near-Complete AWS Provider Coverage**: Manages almost every `aws_s3_bucket_*` resource through one root module
- **Secure by Default**: All public access block settings default to `true`; `object_ownership` defaults to `BucketOwnerEnforced` (ACLs disabled)
- **Server-Side Encryption**: SSE-S3, SSE-KMS, and dual-layer (DSSE-KMS) encryption with `bucket_key_enabled` to cut KMS API costs
- **Versioning & Object Lock**: Versioning with optional MFA delete, plus WORM compliance/governance retention via Object Lock
- **Lifecycle Management**: Storage class transitions, expirations, non-current version cleanup, and incomplete multipart upload abort rules
- **Cross-Region & Same-Region Replication**: CRR/SRR with replica KMS re-encryption, Replication Time Control (RTC), and replication metrics
- **Pre-Built Log Delivery Policies**: One-line attachment of ELB, ALB/NLB, WAF, CloudTrail, and S3 access log delivery bucket policies
- **Security Policy Helpers**: `attach_deny_insecure_transport_policy`, `attach_require_latest_tls_policy`, deny-incorrect-KMS-SSE, and deny-unencrypted-upload policy variables
- **Static Website Hosting**: Index/error documents, redirect rules, and CORS configuration
- **S3 Directory Buckets**: S3 Express One Zone support via `is_directory_bucket`, `availability_zone_id`/`location_type`, and `data_redundancy`
- **Account-Regional Namespace**: `bucket_namespace = "account-regional"` for AWS's account-scoped bucket naming
- **Observability**: S3 Analytics, Inventory, Intelligent-Tiering, and CloudWatch request metric configurations
- **S3 Metadata Configuration**: Journal and live inventory metadata tables (`create_metadata_configuration`)
- **Conditional Creation**: `create_bucket = false` to skip resources per environment without breaking `for_each`/module composition
- **Five Focused Submodules**: `notification`, `object`, `account-public-access`, `table-bucket`, and `vectors`

## Main Use Cases

1. **Static Website Hosting**: Host static sites, SPAs, and documentation with CloudFront in front
2. **Centralized Log Storage**: Aggregate ELB, ALB/NLB, CloudFront, WAF, CloudTrail, and S3 access logs
3. **Application Data Storage**: Store user uploads, configuration files, and application assets securely
4. **Backup and Archival**: Automate lifecycle transitions to IA, Glacier, and Deep Archive for cost savings
5. **Cross-Region Disaster Recovery**: Replicate critical data across regions/accounts for RTO/RPO targets
6. **Event-Driven Processing**: Trigger Lambda, SQS, SNS, or EventBridge from object create/delete events
7. **Compliance and Immutable Storage**: Enforce WORM retention with Object Lock for regulated data
8. **Low-Latency Workloads**: Use S3 Express One Zone directory buckets for high-throughput, low-latency access
9. **Analytics Data Lakes**: Store and query tabular data (Iceberg) with S3 Table Buckets
10. **Vector Search / AI Workloads**: Store and query embeddings at scale with S3 Vectors buckets and indexes

## Submodules

### 1. notification
- **Purpose**: Configure S3 bucket event notifications to Lambda, SQS, SNS, and EventBridge
- **Source**: `terraform-aws-modules/s3-bucket/aws//modules/notification`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest/submodules/notification
- **Key Features**: Lambda permission auto-management, SQS/SNS policy creation, EventBridge integration, prefix/suffix filtering
- **Use Cases**: Event-driven processing, real-time file pipelines, audit trail generation, fan-out notifications

### 2. object
- **Purpose**: Create and manage individual S3 objects (from file or literal content)
- **Source**: `terraform-aws-modules/s3-bucket/aws//modules/object`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest/submodules/object
- **Key Features**: File or inline content upload, storage class selection, SSE/KMS encryption, metadata and tags
- **Use Cases**: Seeding configuration files, deploying static assets, bootstrapping bucket contents in IaC

### 3. account-public-access
- **Purpose**: Manage the account-level S3 Public Access Block (one per AWS account)
- **Source**: `terraform-aws-modules/s3-bucket/aws//modules/account-public-access`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest/submodules/account-public-access
- **Key Features**: Block public ACLs/policies, ignore public ACLs, restrict public bucket policies account-wide
- **Use Cases**: Organization-wide security baseline, guardrails against accidental public exposure

### 4. table-bucket
- **Purpose**: Create and manage S3 Table Buckets and Tables (Apache Iceberg) for analytics workloads
- **Source**: `terraform-aws-modules/s3-bucket/aws//modules/table-bucket`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest/submodules/table-bucket
- **Key Features**: Table bucket + table creation, encryption configuration, maintenance/compaction settings, resource-based policies
- **Use Cases**: Data lake / lakehouse storage, analytics query engines, metadata catalogs

### 5. vectors
- **Purpose**: Create and manage S3 Vectors vector buckets, bucket policies, and vector indexes
- **Source**: `terraform-aws-modules/s3-bucket/aws//modules/vectors`
- **Documentation Link**: https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest/submodules/vectors
- **Key Features**: Vector bucket + index creation, per-index encryption (SSE-KMS), resource policies, non-filterable metadata keys
- **Use Cases**: Storing and querying vector embeddings, semantic/similarity search, RAG pipelines built directly on S3

## Root Module: S3 Bucket

### Description

The root module creates the S3 bucket itself (standard or S3 Express directory bucket) and every bucket-scoped sub-resource: encryption, versioning, object lock, lifecycle, replication, logging, website, CORS, public access block, ownership controls, ACLs/grants, policies, and analytics/inventory/metrics/intelligent-tiering configurations.

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `bucket` / `bucket_prefix` | `string` | `null` | Bucket name (forces new resource) or a name prefix; omit for a random unique name |
| `create_bucket` | `bool` | `true` | Whether to create the bucket (use `false` for conditional creation) |
| `force_destroy` | `bool` | `false` | Delete all objects when destroying the bucket (irreversible) |
| `bucket_namespace` | `string` | `null` | `account-regional` or `global` bucket naming scope |
| `versioning` | `any` | `{}` | `{ enabled = bool, mfa_delete = bool }` |
| `server_side_encryption_configuration` | `any` | `{}` | SSE-S3 / SSE-KMS / dual-layer encryption — keys (from examples): `rule` > `apply_server_side_encryption_by_default` > { `sse_algorithm`, `kms_master_key_id` }, `bucket_key_enabled` |
| `object_lock_enabled` | `bool` | `false` | Enable Object Lock (requires versioning) |
| `object_lock_configuration` | `any` | `{}` | Default retention mode (`GOVERNANCE`/`COMPLIANCE`) and period |
| `lifecycle_rule` | `any` | `[]` | List of lifecycle rules (transitions, expirations, abort incomplete uploads) — keys (from examples): `id`, `status`, `transition`, `expiration`, `abort_incomplete_multipart_upload_days` |
| `replication_configuration` | `any` | `{}` | Cross-region/same-region replication rules, role, RTC, metrics — keys (from examples): `role`, `rules` |
| `website` | `any` | `{}` | Static website hosting (index/error documents, redirects) — keys (from examples): `index_document`, `error_document` |
| `logging` | `any` | `{}` | Server access logging target bucket/prefix |
| `cors_rule` | `any` | `[]` | Cross-origin resource sharing rules — keys (from examples): `allowed_methods`, `allowed_origins`, `allowed_headers`, `expose_headers`, `max_age_seconds` |
| `block_public_acls` / `block_public_policy` / `ignore_public_acls` / `restrict_public_buckets` | `bool` | `true` | Bucket-level public access block (secure by default) |
| `control_object_ownership` | `bool` | `false` | Whether to manage Object Ownership Controls |
| `object_ownership` | `string` | `"BucketOwnerEnforced"` | `BucketOwnerEnforced` (ACLs disabled), `BucketOwnerPreferred`, or `ObjectWriter` |
| `acl` / `grant` / `owner` | `string` / `any` / `map(string)` | `null` / `[]` / `{}` | Canned ACL or explicit grants (require `object_ownership != BucketOwnerEnforced`); `acl` conflicts with `grant` |
| `attach_policy` / `policy` | `bool` / `string` | `false` / `null` | Attach a custom bucket policy JSON (supports `_S3_BUCKET_ID_`, `_S3_BUCKET_ARN_`, `_AWS_ACCOUNT_ID_` placeholders) |
| `attach_elb_log_delivery_policy` / `attach_lb_log_delivery_policy` / `attach_waf_log_delivery_policy` / `attach_cloudtrail_log_delivery_policy` / `attach_access_log_delivery_policy` | `bool` | `false` | Pre-built log delivery bucket policies |
| `attach_deny_insecure_transport_policy` / `attach_require_latest_tls_policy` | `bool` | `false` | Deny non-HTTPS / outdated TLS requests |
| `is_directory_bucket` | `bool` | `false` | Create an S3 Express One Zone directory bucket instead of a standard bucket |
| `availability_zone_id` / `location_type` / `data_redundancy` | `string` | `null` | Placement for directory buckets (required when `is_directory_bucket = true`) |
| `intelligent_tiering` / `inventory_configuration` / `analytics_configuration` / `metric_configuration` | `any` | `{}` / `{}` / `{}` / `[]` | Storage analytics, inventory reports, intelligent tiering, request metrics |
| `acceleration_status` | `string` | `null` | Transfer Acceleration: `Enabled` or `Suspended` |
| `request_payer` | `string` | `null` | `BucketOwner` or `Requester` |
| `tags` | `map(string)` | `{}` | Tags applied to the bucket |

### Main Outputs

| Output | Description |
|--------|-------------|
| `s3_bucket_id` | Name of the bucket |
| `s3_bucket_arn` | ARN of the bucket (`arn:aws:s3:::bucketname`) |
| `s3_bucket_region` | AWS region the bucket resides in |
| `s3_bucket_bucket_domain_name` | Bucket domain name |
| `s3_bucket_bucket_regional_domain_name` | Region-specific bucket domain name (preferred for CloudFront origins) |
| `s3_bucket_hosted_zone_id` | Route 53 hosted zone ID for the bucket's region |
| `s3_bucket_website_endpoint` / `s3_bucket_website_domain` | Website endpoint/domain (if `website` is configured) |
| `s3_bucket_policy` | The bucket policy JSON, if attached |
| `s3_bucket_lifecycle_configuration_rules` | The effective lifecycle rules |
| `aws_s3_bucket_versioning_status` | `Enabled`, `Suspended`, or `Disabled` |
| `s3_directory_bucket_arn` / `s3_directory_bucket_name` | ARN/name of a directory bucket (if `is_directory_bucket = true`) |

### Usage Examples

#### Example 1: Private Bucket with Versioning and KMS Encryption

Public access is blocked by default, so no extra variables are needed to keep this bucket private.

```hcl
module "private_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 5.0"

  bucket        = "my-private-data-bucket"
  force_destroy = false

  versioning = {
    enabled = true
  }

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        kms_master_key_id = aws_kms_key.s3.arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }

  tags = {
    Environment = "production"
  }
}
```

#### Example 2: Static Website Hosting

```hcl
module "website_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 5.0"

  bucket = "my-static-website"

  control_object_ownership = true
  object_ownership          = "ObjectWriter"

  website = {
    index_document = "index.html"
    error_document = "error.html"
  }

  cors_rule = [
    {
      allowed_methods = ["GET", "HEAD"]
      allowed_origins = ["https://example.com"]
      allowed_headers = ["*"]
      expose_headers  = ["ETag"]
      max_age_seconds = 3000
    }
  ]

  # Explicitly relax the secure defaults to allow public read access
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false

  attach_policy = true
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "_S3_BUCKET_ARN_/*"
      }
    ]
  })
}
```

#### Example 3: Centralized Log Bucket with Lifecycle Rules

```hcl
module "log_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 5.0"

  bucket        = "centralized-logs-bucket"
  force_destroy = true

  control_object_ownership = true

  attach_elb_log_delivery_policy        = true
  attach_lb_log_delivery_policy         = true
  attach_waf_log_delivery_policy        = true
  attach_cloudtrail_log_delivery_policy = true

  lifecycle_rule = [
    {
      id     = "transition-old-logs"
      status = "Enabled"

      transition = [
        { days = 30, storage_class = "STANDARD_IA" },
        { days = 90, storage_class = "GLACIER" },
      ]

      expiration = {
        days = 365
      }

      abort_incomplete_multipart_upload_days = 7
    }
  ]

  tags = {
    Purpose = "centralized-logging"
  }
}
```

#### Example 4: Cross-Region Replication

```hcl
module "primary_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 5.0"

  bucket = "primary-data-bucket"

  versioning = {
    enabled = true
  }

  replication_configuration = {
    role = aws_iam_role.replication.arn

    rules = [
      {
        id       = "replicate-all"
        status   = "Enabled"
        priority = 10

        filter = {
          prefix = ""
        }

        destination = {
          bucket        = module.replica_bucket.s3_bucket_arn
          storage_class = "STANDARD_IA"

          replica_kms_key_id = aws_kms_key.replica.arn

          replication_time = {
            status = "Enabled"
            time   = { minutes = 15 }
          }

          metrics = {
            status           = "Enabled"
            event_threshold  = { minutes = 15 }
          }
        }

        delete_marker_replication = {
          status = "Enabled"
        }
      }
    ]
  }
}

module "replica_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 5.0"

  providers = { aws = aws.replica_region }

  bucket = "replica-data-bucket"

  versioning = {
    enabled = true
  }
}
```

#### Example 5: S3 Express One Zone Directory Bucket

```hcl
data "aws_availability_zones" "available" {
  state = "available"
}

module "directory_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 5.0"

  is_directory_bucket  = true
  bucket               = "my-express-bucket"
  availability_zone_id = data.aws_availability_zones.available.zone_ids[0]

  server_side_encryption_configuration = {
    rule = {
      bucket_key_enabled = true # required for directory buckets
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }
}
```

#### Example 6: Compliance Bucket with Object Lock

```hcl
module "compliance_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 5.0"

  bucket = "compliance-records-bucket"

  versioning = {
    enabled    = true
    mfa_delete = true
  }

  object_lock_enabled = true
  object_lock_configuration = {
    rule = {
      default_retention = {
        mode = "COMPLIANCE"
        days = 2555 # 7 years
      }
    }
  }

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        kms_master_key_id = aws_kms_key.compliance.arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }

  tags = {
    Compliance = "required"
    Retention  = "7-years"
  }
}
```

## Submodule 1: notification

### Description

Creates S3 bucket notification configurations that trigger Lambda functions, SQS queues, SNS topics, or EventBridge when specific object events occur, managing the required Lambda permissions and SQS/SNS policies automatically.

### Key Features

- Lambda function notifications with automatic `aws_lambda_permission` management
- SQS queue and SNS topic notifications with auto-generated access policies
- EventBridge integration for advanced, cross-service event routing
- Prefix/suffix filtering and multiple event types per notification target

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `bucket` | `string` | `""` | Name of the S3 bucket to configure notifications on |
| `bucket_arn` | `string` | `null` | ARN of the bucket (used in generated policies) |
| `create` | `bool` | `true` | Whether to create the notification resource |
| `eventbridge` | `bool` | `null` | Enable EventBridge notifications for the bucket |
| `lambda_notifications` | `any` | `{}` | Map of `{ function_arn, events, filter_prefix, filter_suffix }` |
| `sqs_notifications` | `any` | `{}` | Map of `{ queue_arn, events, filter_prefix, filter_suffix }` |
| `sns_notifications` | `any` | `{}` | Map of `{ topic_arn, events, filter_prefix, filter_suffix }` |
| `create_sns_policy` / `create_sqs_policy` | `bool` | `true` | Whether to create the SNS/SQS resource policy for S3 |

### Main Outputs

| Output | Description |
|--------|-------------|
| `s3_bucket_notification_id` | ID of the S3 bucket notification configuration |

### Usage Example

```hcl
module "s3_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 5.0"

  bucket = "my-event-bucket"

  versioning = {
    enabled = true
  }
}

module "s3_notifications" {
  source  = "terraform-aws-modules/s3-bucket/aws//modules/notification"
  version = "~> 5.0"

  bucket = module.s3_bucket.s3_bucket_id

  eventbridge = true

  lambda_notifications = {
    json_processor = {
      function_arn  = module.lambda_processor.lambda_function_arn
      events        = ["s3:ObjectCreated:Put", "s3:ObjectCreated:Post"]
      filter_prefix = "uploads/"
      filter_suffix = ".json"
    }
  }

  sqs_notifications = {
    csv_queue = {
      queue_arn     = aws_sqs_queue.csv_processor.arn
      events        = ["s3:ObjectCreated:*"]
      filter_prefix = "data/"
      filter_suffix = ".csv"
    }
  }
}
```

## Submodule 2: object

### Description

Creates and manages individual S3 objects from a local file or literal string content, with control over storage class, encryption, metadata, and caching behavior. Useful for seeding configuration files or static assets as part of an IaC deployment.

### Key Features

- Upload from `file_source`, inline `content`, or base64 `content_base64`
- Storage class selection (`STANDARD`, `INTELLIGENT_TIERING`, `GLACIER`, `DEEP_ARCHIVE`, etc.)
- SSE-S3/SSE-KMS encryption with optional `bucket_key_enabled`
- Custom metadata, tags, cache-control, and content-type/disposition headers
- Object Lock mode/retention/legal-hold controls per object

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `bucket` | `string` | `""` | Target bucket name or S3 access point ARN |
| `key` | `string` | `""` | Object key within the bucket |
| `file_source` | `string` | `null` | Path to a local file to upload |
| `content` | `string` | `null` | Literal UTF-8 string content |
| `content_type` | `string` | `null` | MIME type of the object |
| `storage_class` | `string` | `null` | Storage class (defaults to `STANDARD`) |
| `server_side_encryption` | `string` | `null` | `AES256` or `aws:kms` |
| `kms_key_id` | `string` | `null` | KMS key ARN for encryption |
| `metadata` | `map(string)` | `{}` | Custom `x-amz-meta-*` metadata |
| `tags` | `map(string)` | `{}` | Tags for the object |

### Main Outputs

| Output | Description |
|--------|-------------|
| `s3_object_id` | Key of the S3 object |
| `s3_object_etag` | ETag (MD5 hash) of the object |
| `s3_object_version_id` | Version ID, if bucket versioning is enabled |

### Usage Example

```hcl
module "app_config" {
  source  = "terraform-aws-modules/s3-bucket/aws//modules/object"
  version = "~> 5.0"

  bucket      = module.config_bucket.s3_bucket_id
  key         = "config/app-config.json"
  file_source = "${path.module}/configs/app-config.json"

  content_type = "application/json"

  metadata = {
    environment = "production"
    version     = "1.0.0"
  }
}
```

## Submodule 3: account-public-access

### Description

Manages the S3 account-level Public Access Block, a single, account-wide setting that overrides bucket- and object-level ACLs/policies to prevent accidental public exposure. Only one configuration can exist per AWS account.

### Key Features

- Account-wide `block_public_acls`, `block_public_policy`, `ignore_public_acls`, `restrict_public_buckets`
- Overrides bucket-level settings for a consistent security baseline
- Typically applied once per account via a dedicated root module or security-baseline stack

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the account public access block |
| `account_id` | `string` | `null` | AWS account ID (defaults to the current account) |
| `block_public_acls` / `block_public_policy` / `ignore_public_acls` / `restrict_public_buckets` | `bool` | `false` | Account-level public access block settings (**default `false`** here — unlike the root module's bucket-level defaults) |

### Main Outputs

| Output | Description |
|--------|-------------|
| `s3_account_public_access_block_id` | AWS account ID of the public access block configuration |

### Usage Example

```hcl
module "s3_account_public_access_block" {
  source  = "terraform-aws-modules/s3-bucket/aws//modules/account-public-access"
  version = "~> 5.0"

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

## Submodule 4: table-bucket

### Description

Creates S3 Table Buckets and Tables (Apache Iceberg format) for analytics workloads, including encryption, maintenance/compaction configuration, and resource-based bucket/table policies.

### Key Features

- Table bucket creation with configurable name and encryption (SSE-S3/SSE-KMS)
- Define multiple Iceberg-format tables per bucket via the `tables` map
- Maintenance configuration for automated compaction and snapshot management
- Resource-based `table_bucket_policy` / `table_bucket_policy_statements` for access control

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create table bucket resources |
| `table_bucket_name` | `string` | `null` | Name of the table bucket (3-63 characters) |
| `tables` | `any` | `{}` | Map of table configurations (`name`, `namespace`, `format`, `metadata`) |
| `encryption_configuration` | `any` | `null` | Encryption configuration for the table bucket — keys (from examples): `sse_s3` |
| `maintenance_configuration` | `any` | `null` | Maintenance/compaction configuration — keys (from examples): `iceberg_compaction` |
| `table_bucket_policy` | `string` | `null` | Resource-based JSON policy for the table bucket |

### Main Outputs

| Output | Description |
|--------|-------------|
| `s3_table_bucket_arn` | ARN of the S3 table bucket |
| `s3_table_arns` | ARNs of the created tables |
| `s3_table_warehouse_locations` | S3 URIs pointing to the table data |

### Usage Example

```hcl
module "analytics_table_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws//modules/table-bucket"
  version = "~> 5.0"

  table_bucket_name = "analytics-data-tables"

  encryption_configuration = {
    sse_s3 = {}
  }

  tables = {
    customers = {
      name      = "customers"
      namespace = "analytics"
      format    = "ICEBERG"
    }
  }

  maintenance_configuration = {
    iceberg_compaction = {
      enabled  = true
      settings = { target_file_size_mb = 512 }
    }
  }
}
```

## Submodule 5: vectors

### Description

Manages Amazon S3 Vectors vector buckets, bucket policies, and vector indexes — a native S3 capability for storing, querying, and managing vector embeddings at scale for AI/ML similarity search and RAG workloads.

### Key Features

- Vector bucket creation with optional SSE-KMS encryption
- One or more vector indexes per bucket (`dimension`, `distance_metric`, per-index encryption)
- Resource-based bucket policy support (`create_policy` + `policy`)
- Non-filterable metadata keys per index for query optimization

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the vector bucket |
| `vector_bucket_name` | `string` | `null` | Name of the S3 Vectors vector bucket |
| `encryption_configuration` | `object` | `null` | `{ sse_type, kms_key_arn }` |
| `indexes` | `map(object)` | `{}` | Map of `{ index_name, dimension, distance_metric, data_type, encryption_configuration, metadata_configuration }` |
| `create_policy` / `policy` | `bool` / `string` | `false` / `null` | Attach a resource policy JSON to the vector bucket |
| `force_destroy` | `bool` | `false` | Delete all indexes/vectors when destroying the bucket |

### Main Outputs

| Output | Description |
|--------|-------------|
| `vector_bucket_arn` | ARN of the S3 Vectors vector bucket |
| `index_arns` | ARNs of the created vector indexes |

### Usage Example

```hcl
module "vector_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws//modules/vectors"
  version = "~> 5.0"

  vector_bucket_name = "my-vector-bucket"

  encryption_configuration = {
    sse_type    = "aws:kms"
    kms_key_arn = aws_kms_key.this.arn
  }

  indexes = {
    my_index = {
      index_name      = "my-index"
      dimension       = 1536
      distance_metric = "cosine"
    }
  }
}
```

## Best Practices

### Security and Access Control

1. **Keep the Default Public Access Block**: Leave `block_public_acls`, `block_public_policy`, `ignore_public_acls`, and `restrict_public_buckets` at their default `true` unless a bucket genuinely needs public access (e.g., static website hosting).
2. **Prefer CloudFront OAC over Public Buckets**: For web content, front the bucket with CloudFront using Origin Access Control instead of relaxing the public access block.
3. **Leave ACLs Disabled**: Keep the default `object_ownership = "BucketOwnerEnforced"`; only set `control_object_ownership = true` with `ObjectWriter`/`BucketOwnerPreferred` when a specific integration (e.g., CloudFront legacy log delivery) requires ACL grants.
4. **Encrypt Everything**: Always set `server_side_encryption_configuration`, preferring SSE-KMS with `bucket_key_enabled = true` for sensitive data requiring audit trails.
5. **Enable Versioning**: Protect against accidental deletion/overwrite; required before enabling Object Lock or replication.
6. **Enforce Transport Security**: Use `attach_deny_insecure_transport_policy` and `attach_require_latest_tls_policy` to reject plaintext/outdated-TLS requests.
7. **Use Object Lock for Regulated Data**: Enable `object_lock_enabled` with `COMPLIANCE` mode retention for immutable, audit-grade storage.
8. **Least-Privilege Policies**: Scope custom `policy` documents narrowly and use the `_S3_BUCKET_ARN_`/`_AWS_ACCOUNT_ID_` placeholders to avoid plan drift from generated names.

### Replication and Disaster Recovery

1. **Enable Cross-Region Replication**: Replicate critical buckets to a secondary region/account for business continuity.
2. **Use Replication Time Control**: Set `replication_time.status = "Enabled"` for a 15-minute replication SLA on compliance-sensitive data.
3. **Replicate Delete Markers**: Set `delete_marker_replication.status = "Enabled"` to keep source/replica consistent.
4. **Use Separate KMS Keys per Region**: Configure `replica_kms_key_id` on the destination rather than sharing keys across regions.

### Cost and Performance Optimization

1. **Use Bucket Keys for KMS**: Set `bucket_key_enabled = true` to reduce KMS API call costs by up to 99%.
2. **Tier Storage with Lifecycle Rules**: Transition older objects to `STANDARD_IA`, `GLACIER`, and `DEEP_ARCHIVE`; abort incomplete multipart uploads after 7 days.
3. **Use Intelligent-Tiering for Unpredictable Access**: Configure `intelligent_tiering` when access patterns are unknown or changing.
4. **Enable Transfer Acceleration for Global Uploads**: Set `acceleration_status = "Enabled"` for latency-sensitive, geographically distributed clients.
5. **Consider S3 Express One Zone**: Use `is_directory_bucket = true` for latency-critical, high-throughput single-AZ workloads.
6. **Requester Pays for Shared Datasets**: Set `request_payer = "Requester"` to shift bandwidth costs to consumers of shared/public datasets.

### Logging and Operational Excellence

1. **Use the Built-In Log Delivery Policies**: Prefer `attach_elb_log_delivery_policy`, `attach_lb_log_delivery_policy`, `attach_waf_log_delivery_policy`, and `attach_cloudtrail_log_delivery_policy` over hand-written policies.
2. **Separate Log Buckets from Data Buckets**: Keep centralized logging destinations distinct from application data buckets.
3. **Tag Consistently**: Apply `Environment`, `Owner`, and `Purpose` tags for cost allocation and governance.
4. **Use `create_bucket = false` for Conditional Deployments**: Toggle bucket creation per environment/feature flag without `count` on the module block.
5. **Guard `force_destroy`**: Only set `force_destroy = true` in non-production or explicitly disposable buckets — it permanently deletes all objects on destroy.
6. **Pin the Module Version**: Use `version = "~> 5.0"` (or a tighter constraint) since minor versions add features regularly (S3 Vectors, directory-bucket metrics, `bucket_namespace`, etc.).

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-s3-bucket
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-s3-bucket/tree/master/examples
- **Changelog**: https://github.com/terraform-aws-modules/terraform-aws-s3-bucket/blob/master/CHANGELOG.md
- **AWS S3 User Guide**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/
- **S3 Security Best Practices**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html
- **S3 Replication**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html
- **S3 Object Lock**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
- **S3 Express One Zone (Directory Buckets)**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-express-Endpoints.html
- **S3 Table Buckets**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html
- **Amazon S3 Vectors**: https://aws.amazon.com/s3-vectors/
- **S3 Storage Classes**: https://aws.amazon.com/s3/storage-classes/

## Notes for AI Agents

When generating Terraform code with this module:

1. **Public Access Is Blocked by Default**: `block_public_acls`/`block_public_policy`/`ignore_public_acls`/`restrict_public_buckets` all default to `true` — only set them to `false` when the use case genuinely requires public access (e.g., static websites), and prefer CloudFront OAC instead when possible.
2. **ACLs Are Disabled by Default**: `object_ownership` defaults to `"BucketOwnerEnforced"`. If a workload needs canned ACLs or `grant` blocks (e.g., legacy CloudFront log delivery via `grant`), set `control_object_ownership = true` and `object_ownership = "ObjectWriter"` or `"BucketOwnerPreferred"`; `acl` and `grant` are mutually exclusive.
3. **Versioning Is a Prerequisite**: Enable `versioning.enabled = true` before configuring `object_lock_enabled` or `replication_configuration`.
4. **Prefer Bucket Keys**: Always pair SSE-KMS with `bucket_key_enabled = true` to reduce KMS costs, except for S3 Express directory buckets where it is *required*.
5. **Directory Buckets Need Placement**: When `is_directory_bucket = true`, you must also supply `availability_zone_id` (or `location_type`/`data_redundancy` for Dedicated Local Zones); most standard-bucket features (grants, some lifecycle options) don't apply.
6. **Use the Log Delivery Policy Toggles**: Prefer `attach_elb_log_delivery_policy`, `attach_lb_log_delivery_policy`, `attach_waf_log_delivery_policy`, `attach_cloudtrail_log_delivery_policy`, and `attach_access_log_delivery_policy` instead of writing custom log-delivery policy JSON.
7. **`force_destroy` Is Destructive**: Only set `force_destroy = true` for buckets that are explicitly disposable (tests, ephemeral environments) — it deletes all objects, including versions, on `terraform destroy`.
8. **Conditional Creation Pattern**: Use `create_bucket = false` (not `count` on the module block) to skip bucket creation per environment.
9. **Submodules Reference the Bucket by ID/ARN**: `notification` and `object` take the parent bucket's `s3_bucket_id`/`s3_bucket_arn`; `table-bucket` and `vectors` create entirely separate resource types (S3 Tables / S3 Vectors) and do **not** wrap a standard `aws_s3_bucket`.
10. **Pin a Version Constraint**: Requires Terraform `>= 1.5.7` and AWS provider `>= 6.42`; pin the module with `version = "~> 5.0"` in generated code since new minor versions land frequently.
11. **Policy Placeholders Avoid Drift**: When writing custom `policy` JSON, use the `_S3_BUCKET_ID_`, `_S3_BUCKET_ARN_`, and `_AWS_ACCOUNT_ID_` placeholders (especially with `bucket_prefix`) instead of interpolating values that may cause perpetual plan diffs.
12. **`any`-Typed Variables Accept `jsonencode()`**: `lifecycle_rule`, `cors_rule`, `server_side_encryption_configuration`, etc. also accept a `jsonencode()`-string, which is useful for Terragrunt `inputs`.
