# Terraform AWS S3 Bucket Module

## Module Information

- **Module Name**: terraform-aws-s3-bucket
- **Source**: `terraform-aws-modules/s3-bucket/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-s3-bucket
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest
- **Latest Version**: Check registry for current version
- **Purpose**: Terraform module that creates and manages AWS S3 buckets with comprehensive configuration options for security, replication, lifecycle management, and notifications
- **Service**: AWS S3 (Simple Storage Service)
- **Category**: Storage, Object Storage, Data Management
- **Keywords**: s3, bucket, object-storage, versioning, encryption, lifecycle, replication, cors, logging, static-website, kms, sse, acl, bucket-policy, public-access-block, server-access-logging, object-lock, mfa-delete, intelligent-tiering, glacier, cross-region-replication, crr, same-region-replication, srr, s3-notifications, lambda-trigger, sns, sqs, eventbridge, s3-analytics, s3-inventory, storage-class, transfer-acceleration, request-payer, website-hosting, redirect, cloudfront, cloudtrail, elb-logs, alb-logs, waf-logs, table-bucket, directory-bucket
- **Use For**: Storing application data and backups, hosting static websites and SPAs, centralized log aggregation, serving media files and assets, data lake storage, compliance and archival storage, cross-region data replication, event-driven architectures with S3 triggers, CloudFront origin buckets, versioned configuration storage, disaster recovery backups, analytics data warehousing

## Description

This Terraform module provides comprehensive management of AWS S3 buckets with support for nearly all features available in the AWS Terraform provider. It simplifies the creation and configuration of S3 buckets while offering extensive customization options for security, access control, lifecycle management, replication, and event notifications. The module is designed to handle both simple and complex S3 bucket configurations through a consistent and well-documented interface.

The module addresses common S3 management challenges by providing pre-configured patterns for scenarios such as static website hosting, centralized logging for AWS services (ELB, ALB, NLB, CloudFront, WAF), cross-region replication for disaster recovery, and object lifecycle management for cost optimization. It includes built-in support for advanced security features like server-side encryption with KMS, object locking for compliance, public access blocking, and versioning with MFA delete protection.

Key architectural capabilities include support for multiple bucket types (standard, directory, and table buckets), conditional bucket creation for environment-specific deployments, comprehensive tagging strategies, and modular notification configurations. The module integrates seamlessly with other AWS services through dedicated submodules for notifications (Lambda, SNS, SQS, EventBridge), object management, account-level public access controls, and specialized table bucket configurations for analytics workloads.

## Key Features

- **Four Specialized Submodules**: Modular architecture with notification, object, account-public-access, and table-bucket submodules
- **Comprehensive Bucket Configuration**: Support for all major S3 bucket features through a single module
- **Server-Side Encryption**: Built-in support for SSE-S3, SSE-KMS, and dual-layer encryption with customer-managed keys
- **Versioning Control**: Enable versioning with optional MFA delete protection for critical buckets
- **Object Lock Support**: WORM (Write-Once-Read-Many) compliance mode and governance mode for regulatory requirements
- **Lifecycle Rules**: Automate object transitions, expirations, and deletions based on age, prefix, or tags
- **Cross-Region Replication**: Replicate objects across regions with support for KMS encryption and storage class override
- **Same-Region Replication**: Replicate within the same region for compliance or aggregation use cases
- **Public Access Block**: Account and bucket-level controls to prevent accidental public exposure
- **Static Website Hosting**: Configure index and error documents with routing rules and redirects
- **Access Logging**: Enable server access logging to track bucket requests and access patterns
- **CORS Configuration**: Define cross-origin resource sharing rules for web applications
- **Request Payer Configuration**: Transfer bandwidth costs to requesters for shared datasets
- **Transfer Acceleration**: Enable fast, secure transfers over long distances using CloudFront edge locations
- **Event Notifications**: Trigger Lambda functions, SQS queues, SNS topics, or EventBridge on object events
- **Bucket Policies**: Attach custom IAM policies for fine-grained access control
- **Log Delivery Policies**: Pre-configured policies for ELB, ALB/NLB, CloudFront, CloudTrail, and WAF logs
- **Intelligent Tiering**: Automatic cost optimization by moving objects between access tiers
- **S3 Analytics**: Configure storage class analysis to optimize lifecycle policies
- **S3 Inventory**: Generate reports of object metadata for auditing and analytics
- **Object Ownership Controls**: Configure ACL behavior and enforce bucket owner ownership
- **Conditional Creation**: Create or skip bucket creation based on variables for multi-environment deployments
- **Comprehensive Tagging**: Support for resource tags across buckets and objects
- **Directory Buckets**: Support for S3 directory buckets for high-performance workloads
- **Table Buckets**: Create and manage S3 table buckets and tables for analytics use cases
- **Multiple Bucket Types**: Standard, directory, and table bucket support in a single module

## Main Use Cases

1. **Static Website Hosting**: Host static websites, single-page applications, and documentation sites
2. **Centralized Log Storage**: Aggregate logs from ELB, ALB, CloudFront, WAF, and application servers
3. **Application Data Storage**: Store user uploads, configuration files, and application assets
4. **Backup and Archival**: Implement automated backup solutions with lifecycle transitions to Glacier
5. **Media and Content Distribution**: Serve images, videos, and files with CloudFront integration
6. **Data Lake Storage**: Store raw and processed data for analytics and machine learning workflows
7. **Cross-Region Disaster Recovery**: Replicate critical data across regions for business continuity
8. **Event-Driven Architectures**: Trigger serverless workflows based on S3 object events
9. **Compliance and Audit Storage**: Store immutable records with object lock and versioning
10. **DevOps Artifact Storage**: Store Terraform state files, deployment packages, and build artifacts

## Requirements

### Terraform Version
- **Terraform**: >= 1.5.7

### Provider Requirements
- **AWS Provider**: >= 6.5

## Submodules

### 1. notification
- **Purpose**: Configure S3 bucket event notifications to Lambda, SNS, SQS, and EventBridge
- **Source**: `terraform-aws-modules/s3-bucket/aws//modules/notification`
- **Key Features**: Lambda triggers, SNS topic notifications, SQS queue delivery, EventBridge integration
- **Use Cases**: Event-driven processing, real-time file processing, data pipeline triggers, audit trail generation

### 2. object
- **Purpose**: Create and manage S3 objects with extensive configuration options
- **Source**: `terraform-aws-modules/s3-bucket/aws//modules/object`
- **Key Features**: Object creation, metadata management, storage class selection, encryption configuration
- **Use Cases**: Uploading configuration files, creating initial objects, managing static content, deploying application assets

### 3. account-public-access
- **Purpose**: Configure account-level S3 public access block settings
- **Source**: `terraform-aws-modules/s3-bucket/aws//modules/account-public-access`
- **Key Features**: Block public ACLs, block public policies, ignore public ACLs, restrict public buckets
- **Use Cases**: Organization-wide security baseline, preventing data leaks, compliance enforcement, security guardrails

### 4. table-bucket
- **Purpose**: Create and manage S3 table buckets and tables for analytics workloads
- **Source**: `terraform-aws-modules/s3-bucket/aws//modules/table-bucket`
- **Key Features**: Table bucket creation, encryption configuration, maintenance settings, table management
- **Use Cases**: Analytics data storage, tabular data management, data warehouse integration, metadata catalogs

## Submodule 1: notification

### Description

The notification submodule creates S3 bucket notification configurations that trigger actions when specific events occur in an S3 bucket. It supports all major AWS notification targets including Lambda functions for serverless processing, SQS queues for decoupled message processing, SNS topics for fan-out patterns, and EventBridge for complex event routing. This submodule automatically manages the necessary permissions and policies required for S3 to invoke the target services.

### Key Features

- Support for Lambda function notifications with automatic permission management
- SQS queue notifications with configurable event types
- SNS topic notifications for pub/sub patterns
- EventBridge integration for advanced event routing
- Event filtering by object key prefix and suffix
- Multiple notification configurations per bucket
- Configurable event types (ObjectCreated, ObjectRemoved, ObjectRestore, etc.)

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `bucket` | `string` | `""` | Name of the S3 bucket to configure notifications |
| `create` | `bool` | `true` | Whether to create the S3 bucket notification resource |
| `eventbridge` | `bool` | `false` | Enable Amazon EventBridge notifications for the bucket |
| `lambda_notifications` | `map(object)` | `{}` | Map of Lambda notification configurations with function_arn, events, filter_prefix, filter_suffix |
| `sqs_notifications` | `map(object)` | `{}` | Map of SQS notification configurations with queue_arn, events, filter_prefix, filter_suffix |
| `sns_notifications` | `map(object)` | `{}` | Map of SNS notification configurations with topic_arn, events, filter_prefix, filter_suffix |
| `create_sns_policy` | `bool` | `true` | Whether to create SNS topic policy for S3 notifications |
| `create_sqs_policy` | `bool` | `true` | Whether to create SQS queue policy for S3 notifications |

### Main Outputs

| Output | Description |
|--------|-------------|
| `s3_bucket_notification_id` | ID of the S3 bucket notification configuration |

### Usage Example

```hcl
# Create S3 bucket
module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "my-event-bucket"

  versioning = {
    enabled = true
  }
}

# Create Lambda function for processing
module "lambda_processor" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "s3-object-processor"
  handler       = "index.handler"
  runtime       = "python3.11"

  source_path = "./lambda"
}

# Configure S3 notifications
module "s3_notifications" {
  source = "terraform-aws-modules/s3-bucket/aws//modules/notification"

  bucket = module.s3_bucket.s3_bucket_id

  # Enable EventBridge for advanced routing
  eventbridge = true

  # Lambda notifications for JSON files
  lambda_notifications = {
    json_processor = {
      function_arn  = module.lambda_processor.lambda_function_arn
      events        = ["s3:ObjectCreated:Put", "s3:ObjectCreated:Post"]
      filter_prefix = "uploads/"
      filter_suffix = ".json"
    }
  }

  # SQS notifications for CSV files
  sqs_notifications = {
    csv_queue = {
      queue_arn     = aws_sqs_queue.csv_processor.arn
      events        = ["s3:ObjectCreated:*"]
      filter_prefix = "data/"
      filter_suffix = ".csv"
    }
  }

  # SNS notifications for deletions
  sns_notifications = {
    deletion_alerts = {
      topic_arn     = aws_sns_topic.s3_deletions.arn
      events        = ["s3:ObjectRemoved:*"]
      filter_prefix = "critical/"
    }
  }
}
```

## Submodule 2: object

### Description

The object submodule creates and manages individual S3 objects with comprehensive configuration options. It supports uploading files from the local filesystem, creating objects from literal string content, and configuring object-level properties such as storage class, encryption, metadata, and caching headers. This submodule is particularly useful for deploying static configuration files, initial application data, or managing objects as part of infrastructure deployments.

### Key Features

- Create objects from file sources or literal content
- Configure storage classes (STANDARD, INTELLIGENT_TIERING, GLACIER, etc.)
- Set server-side encryption (SSE-S3, SSE-KMS)
- Define custom metadata and tags
- Configure caching and content encoding
- Set ACLs and object lock settings
- Manage content type and disposition headers

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `bucket` | `string` | `""` | Name of the S3 bucket or access point ARN |
| `key` | `string` | `""` | Name of the object within the bucket |
| `file_source` | `string` | `null` | Path to file for object content |
| `content` | `string` | `null` | Literal string content for the object |
| `content_type` | `string` | `null` | MIME type of the object |
| `storage_class` | `string` | `"STANDARD"` | Storage class for the object |
| `server_side_encryption` | `string` | `null` | Server-side encryption algorithm (AES256 or aws:kms) |
| `kms_key_id` | `string` | `null` | KMS key ID for encryption |
| `acl` | `string` | `null` | Canned ACL to apply |
| `metadata` | `map(string)` | `{}` | Custom metadata key-value pairs |
| `tags` | `map(string)` | `{}` | Tags for the object |

### Main Outputs

| Output | Description |
|--------|-------------|
| `s3_object_id` | Key of the S3 object |
| `s3_object_etag` | ETag (MD5 hash) of the object |
| `s3_object_version_id` | Version ID if bucket versioning is enabled |

### Usage Example

```hcl
# Create S3 bucket for configuration files
module "config_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "app-configuration"

  versioning = {
    enabled = true
  }

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }
}

# Upload configuration file from local filesystem
module "app_config" {
  source = "terraform-aws-modules/s3-bucket/aws//modules/object"

  bucket      = module.config_bucket.s3_bucket_id
  key         = "config/app-config.json"
  file_source = "${path.module}/configs/app-config.json"

  content_type = "application/json"
  storage_class = "STANDARD"

  metadata = {
    environment = "production"
    version     = "1.0.0"
  }

  tags = {
    Type        = "Configuration"
    Application = "MyApp"
  }
}

# Create object from literal content
module "readme" {
  source = "terraform-aws-modules/s3-bucket/aws//modules/object"

  bucket  = module.config_bucket.s3_bucket_id
  key     = "README.txt"
  content = "This bucket contains application configuration files."

  content_type = "text/plain"

  tags = {
    Type = "Documentation"
  }
}
```

## Submodule 3: account-public-access

### Description

The account-public-access submodule manages S3 account-level public access block configuration, which provides centralized control over public access settings for all S3 buckets in an AWS account. This is a critical security feature that helps prevent accidental data exposure by blocking public access at the account level, regardless of individual bucket or object settings. Only one public access block configuration can exist per AWS account.

### Key Features

- Account-level public access controls
- Block public ACLs on buckets and objects
- Block public bucket policies
- Ignore existing public ACLs
- Restrict public bucket policies
- Centralized security baseline enforcement
- Override protection for bucket-level settings

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create the account public access block |
| `account_id` | `string` | `null` | AWS account ID (defaults to current account) |
| `block_public_acls` | `bool` | `false` | Block public ACLs on buckets and objects |
| `block_public_policy` | `bool` | `false` | Block public bucket policies |
| `ignore_public_acls` | `bool` | `false` | Ignore all public ACLs on buckets and objects |
| `restrict_public_buckets` | `bool` | `false` | Restrict public bucket policies |

### Main Outputs

| Output | Description |
|--------|-------------|
| `s3_account_public_access_block_id` | AWS account ID of the public access block configuration |

### Usage Example

```hcl
# Enable comprehensive account-level public access blocking
module "s3_account_public_access_block" {
  source = "terraform-aws-modules/s3-bucket/aws//modules/account-public-access"

  # Block all public access at account level
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# This configuration ensures:
# 1. No new public ACLs can be applied to buckets or objects
# 2. No new public bucket policies can be created
# 3. All existing public ACLs are ignored
# 4. Public bucket policies are restricted from granting access
```

## Submodule 4: table-bucket

### Description

The table-bucket submodule creates and manages S3 table buckets and tables, which are specialized S3 resources designed for storing and querying tabular data. Table buckets provide optimized storage and access patterns for analytics workloads, with support for metadata catalogs, encryption configurations, and maintenance operations. This submodule is ideal for data lake architectures and analytics pipelines that require structured data storage with S3 integration.

### Key Features

- Create S3 table buckets with configurable names
- Define and manage multiple tables within buckets
- Configure encryption for table data
- Set maintenance configurations
- Manage table-level access policies
- Track table metadata and versions
- Support for warehouse locations and metadata configurations

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `create` | `bool` | `true` | Whether to create table bucket resources |
| `table_bucket_name` | `string` | `""` | Name of the table bucket (3-63 characters) |
| `tables` | `map(object)` | `{}` | Map of table configurations with name, namespace, format, and metadata |
| `encryption_configuration` | `any` | `{}` | Encryption configuration for the table bucket |
| `maintenance_configuration` | `any` | `{}` | Maintenance configuration for automated operations |
| `table_bucket_policy` | `string` | `null` | IAM policy JSON for table bucket access |

### Main Outputs

| Output | Description |
|--------|-------------|
| `s3_table_bucket_arn` | ARN of the S3 table bucket |
| `s3_table_bucket_name` | Name of the table bucket |
| `s3_tables` | Map of created table resources with ARNs and metadata |
| `s3_table_creation_dates` | Creation timestamps for tables |

### Usage Example

```hcl
module "analytics_table_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws//modules/table-bucket"

  table_bucket_name = "analytics-data-tables"

  # Configure encryption for table bucket
  encryption_configuration = {
    sse_s3 = {}
  }

  # Define tables for analytics workloads
  tables = {
    customer_data = {
      name      = "customers"
      namespace = "analytics"
      format    = "ICEBERG"

      metadata = {
        description = "Customer dimension table"
        owner       = "data-team"
      }
    }

    transactions = {
      name      = "transactions"
      namespace = "analytics"
      format    = "ICEBERG"

      metadata = {
        description = "Transaction fact table"
        owner       = "data-team"
      }
    }
  }

  # Maintenance configuration for automated operations
  maintenance_configuration = {
    iceberg_compaction = {
      enabled = true
      settings = {
        target_file_size_mb = 512
      }
    }
  }
}
```

## Main Module: S3 Bucket

### Description

The main S3 bucket module provides comprehensive bucket creation and configuration with support for all major S3 features. This is the primary module for creating standard S3 buckets with full control over security, lifecycle, replication, logging, and access settings.

### Key Features

- Complete bucket lifecycle management
- Versioning with MFA delete support
- Server-side encryption (SSE-S3, SSE-KMS, dual-layer)
- Object lock for compliance
- Cross-region and same-region replication
- Lifecycle rules for cost optimization
- Static website hosting
- Access logging and request metrics
- CORS configuration
- Public access blocking
- Bucket policies and ACLs

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `bucket` | `string` | `""` | Name of the bucket (must be globally unique) |
| `create_bucket` | `bool` | `true` | Whether to create the bucket |
| `force_destroy` | `bool` | `false` | Allow destroying bucket with objects |
| `versioning` | `object` | `{}` | Versioning configuration with enabled and mfa_delete |
| `server_side_encryption_configuration` | `any` | `{}` | Server-side encryption rules |
| `object_lock_enabled` | `bool` | `false` | Enable object lock (requires versioning) |
| `object_lock_configuration` | `any` | `{}` | Object lock retention rules |
| `lifecycle_rule` | `list(any)` | `[]` | List of lifecycle rules |
| `replication_configuration` | `any` | `{}` | Cross-region or same-region replication config |
| `website` | `map(string)` | `{}` | Static website hosting configuration |
| `logging` | `map(string)` | `{}` | Access logging configuration |
| `cors_rule` | `list(any)` | `[]` | CORS rules for cross-origin access |
| `acceleration_status` | `string` | `null` | Transfer acceleration status (Enabled or Suspended) |
| `request_payer` | `string` | `"BucketOwner"` | Who pays for requests and data transfer |

### Main Outputs

| Output | Description |
|--------|-------------|
| `s3_bucket_id` | Name of the bucket |
| `s3_bucket_arn` | ARN of the bucket |
| `s3_bucket_region` | AWS region of the bucket |
| `s3_bucket_domain_name` | Bucket domain name |
| `s3_bucket_regional_domain_name` | Regional domain name |
| `s3_bucket_hosted_zone_id` | Route 53 hosted zone ID |
| `s3_bucket_website_endpoint` | Website endpoint (if configured) |

### Usage Examples

#### Example 1: Private Bucket with Versioning and Encryption

```hcl
module "private_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "my-private-data-bucket"

  # Prevent accidental deletion
  force_destroy = false

  # Enable versioning for data protection
  versioning = {
    enabled = true
  }

  # Server-side encryption with KMS
  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        kms_master_key_id = aws_kms_key.s3.arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }

  # Block all public access
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  tags = {
    Environment = "production"
    Compliance  = "required"
  }
}
```

#### Example 2: Static Website Hosting

```hcl
module "website_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "my-static-website"

  # Enable static website hosting
  website = {
    index_document = "index.html"
    error_document = "error.html"
  }

  # CORS for API calls from website
  cors_rule = [
    {
      allowed_methods = ["GET", "HEAD"]
      allowed_origins = ["https://example.com"]
      allowed_headers = ["*"]
      expose_headers  = ["ETag"]
      max_age_seconds = 3000
    }
  ]

  # Public read access for website content
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false

  # Bucket policy for public read
  attach_policy = true
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "arn:aws:s3:::my-static-website/*"
      }
    ]
  })

  tags = {
    Purpose = "Static Website"
  }
}
```

#### Example 3: Log Bucket with Lifecycle Management

```hcl
module "log_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "centralized-logs-bucket"

  # Allow ELB/ALB to write logs
  attach_elb_log_delivery_policy = true
  attach_lb_log_delivery_policy  = true

  # Enable access logging for the log bucket itself
  logging = {
    target_bucket = "audit-logs-bucket"
    target_prefix = "s3-access-logs/"
  }

  # Lifecycle rules for cost optimization
  lifecycle_rule = [
    {
      id      = "transition-old-logs"
      enabled = true

      transition = [
        {
          days          = 30
          storage_class = "STANDARD_IA"
        },
        {
          days          = 90
          storage_class = "GLACIER"
        },
        {
          days          = 180
          storage_class = "DEEP_ARCHIVE"
        }
      ]

      expiration = {
        days = 365
      }
    },
    {
      id      = "delete-incomplete-uploads"
      enabled = true

      abort_incomplete_multipart_upload = {
        days_after_initiation = 7
      }
    }
  ]

  # Object ownership for log delivery
  control_object_ownership = true
  object_ownership         = "BucketOwnerPreferred"

  tags = {
    Purpose = "Centralized Logging"
  }
}
```

#### Example 4: Cross-Region Replication

```hcl
# Primary bucket in us-east-1
module "primary_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  providers = {
    aws = aws.us-east-1
  }

  bucket = "primary-data-bucket"

  # Versioning required for replication
  versioning = {
    enabled = true
  }

  # Replication configuration
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

          # Replicate with encryption
          encryption_configuration = {
            replica_kms_key_id = aws_kms_key.replica.arn
          }

          # Replication time control for compliance
          replication_time = {
            status = "Enabled"
            time = {
              minutes = 15
            }
          }

          metrics = {
            status = "Enabled"
            event_threshold = {
              minutes = 15
            }
          }
        }

        delete_marker_replication = {
          status = "Enabled"
        }
      }
    ]
  }

  tags = {
    Environment = "production"
    Replication = "source"
  }
}

# Replica bucket in us-west-2
module "replica_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  providers = {
    aws = aws.us-west-2
  }

  bucket = "replica-data-bucket"

  versioning = {
    enabled = true
  }

  tags = {
    Environment = "production"
    Replication = "destination"
  }
}
```

#### Example 5: Compliance Bucket with Object Lock

```hcl
module "compliance_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "compliance-records-bucket"

  # Object lock requires versioning
  versioning = {
    enabled = true
  }

  # Enable object lock
  object_lock_enabled = true

  # Object lock configuration for compliance
  object_lock_configuration = {
    rule = {
      default_retention = {
        mode = "COMPLIANCE"
        days = 2555  # 7 years
      }
    }
  }

  # Server-side encryption
  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        kms_master_key_id = aws_kms_key.compliance.arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }

  # Block all public access
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  # Enable MFA delete for versioning
  versioning = {
    enabled    = true
    mfa_delete = true
  }

  tags = {
    Compliance  = "required"
    Retention   = "7-years"
    DataType    = "Financial Records"
  }
}
```

## Best Practices

### Security and Access Control

1. **Enable Public Access Block**: Always enable all four public access block settings by default unless you have a specific requirement for public access (e.g., static website hosting).
2. **Use Server-Side Encryption**: Enable server-side encryption for all buckets, preferring SSE-KMS for sensitive data that requires audit trails and key rotation.
3. **Enable Bucket Versioning**: Protect against accidental deletions and modifications by enabling versioning on buckets containing important data.
4. **Implement Object Lock for Compliance**: Use object lock in compliance mode for regulatory requirements that mandate immutable storage (WORM).
5. **Use Least Privilege Bucket Policies**: Grant only the minimum permissions required and use conditions to restrict access by IP, VPC endpoint, or MFA requirement.
6. **Enable MFA Delete**: For critical buckets, enable MFA delete in versioning configuration to prevent unauthorized permanent deletions.
7. **Block Public ACLs**: Set `block_public_acls = true` and `ignore_public_acls = true` to prevent misconfigured ACLs from exposing data.
8. **Use VPC Endpoints**: Configure bucket policies to require access through VPC endpoints to prevent data exfiltration over the internet.

### Data Protection and Backup

1. **Enable Cross-Region Replication**: Replicate critical data to a secondary region for disaster recovery and business continuity.
2. **Configure Lifecycle Rules**: Implement lifecycle policies to transition older data to cheaper storage classes (IA, Glacier, Deep Archive) based on access patterns.
3. **Use Intelligent Tiering**: Enable intelligent tiering for data with unknown or changing access patterns to automatically optimize costs.
4. **Enable Access Logging**: Configure server access logging to track all requests and detect unusual access patterns or security incidents.
5. **Set Up Replication Time Control**: For compliance requirements, use replication time control (RTC) to guarantee 15-minute replication SLAs.
6. **Delete Incomplete Uploads**: Create lifecycle rules to abort incomplete multipart uploads after 7 days to avoid storage costs.
7. **Version Expiration**: For versioned buckets, configure noncurrent version expiration to clean up old versions and reduce costs.

### Performance and Cost Optimization

1. **Enable Transfer Acceleration**: For global data uploads, enable transfer acceleration to use CloudFront edge locations for faster uploads.
2. **Use Multipart Upload**: For objects larger than 100MB, use multipart upload for better performance and reliability.
3. **Choose Appropriate Storage Classes**: Select storage classes based on access frequency - STANDARD for hot data, IA for infrequent access, Glacier for archival.
4. **Configure S3 Analytics**: Enable storage class analysis to understand access patterns and optimize lifecycle policies.
5. **Use Bucket Keys**: Enable bucket keys for KMS encryption to reduce KMS API costs by up to 99%.
6. **Implement Request Payer**: For shared datasets, use requester-pays buckets to transfer bandwidth costs to data consumers.
7. **Optimize Object Key Structure**: Use random prefixes for high request rates to distribute load across S3 partitions (though less critical with newer S3 performance).
8. **Set Appropriate Cache Headers**: For static content, configure proper Cache-Control headers to maximize CloudFront caching efficiency.

### Operational Excellence

1. **Use Consistent Tagging**: Implement comprehensive tagging strategy with Environment, Owner, Application, and CostCenter for resource tracking.
2. **Enable CloudTrail Integration**: Log all S3 API calls to CloudTrail for security auditing and compliance.
3. **Set Up S3 Inventory**: Configure S3 inventory reports for regular audits of object metadata, encryption status, and storage classes.
4. **Use Conditional Creation**: Leverage `create_bucket` variable to conditionally create buckets based on environment or feature flags.
5. **Implement Event Notifications**: Set up EventBridge or direct notifications for critical events like deletions or unauthorized access attempts.
6. **Configure Object Ownership**: Use `control_object_ownership = true` and `object_ownership = "BucketOwnerPreferred"` for consistent ACL behavior.
7. **Monitor with CloudWatch**: Set up CloudWatch alarms for metrics like 4xx/5xx errors, replication failures, and request count anomalies.
8. **Use Terraform State Locking**: When storing Terraform state in S3, always enable versioning and use DynamoDB for state locking.

### Website Hosting and Content Delivery

1. **Use CloudFront with S3**: Always front static website buckets with CloudFront for better performance, HTTPS support, and DDoS protection.
2. **Configure CORS Properly**: Set restrictive CORS rules that only allow necessary origins, methods, and headers.
3. **Implement Cache Invalidation**: Use CloudFront invalidations or versioned file names for cache busting when content changes.
4. **Set Content-Type Headers**: Ensure correct content-type headers are set for all objects to prevent browser rendering issues.
5. **Use Origin Access Identity**: Configure CloudFront Origin Access Identity (OAI) or Origin Access Control (OAC) to prevent direct S3 access.

### Logging and Compliance

1. **Separate Log Buckets**: Use dedicated buckets for storing logs separate from application data buckets.
2. **Configure Log Retention**: Implement lifecycle rules on log buckets to transition to Glacier and eventually delete old logs per retention policy.
3. **Enable Multiple Log Types**: Configure server access logging, CloudTrail data events, and replication metrics for comprehensive visibility.
4. **Attach Log Delivery Policies**: Use built-in `attach_elb_log_delivery_policy`, `attach_lb_log_delivery_policy` for AWS service log delivery.
5. **Protect Log Integrity**: Enable object lock on log buckets to ensure logs cannot be tampered with or deleted prematurely.
6. **Centralize Logs**: Use a single account or region as a centralized logging destination for multi-account or multi-region architectures.

### Replication and Disaster Recovery

1. **Enable Replication Metrics**: Use replication metrics to monitor replication lag and ensure RTO/RPO requirements are met.
2. **Replicate Delete Markers**: Enable delete marker replication to maintain consistency between source and destination.
3. **Use Separate KMS Keys**: Use different KMS keys for source and replica to maintain regional key isolation.
4. **Test Failover Procedures**: Regularly test accessing data from replica buckets to validate disaster recovery procedures.
5. **Configure Bidirectional Replication**: For active-active scenarios, set up bidirectional replication with careful conflict resolution planning.

## Additional Resources

- **Module Repository**: https://github.com/terraform-aws-modules/terraform-aws-s3-bucket
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-s3-bucket/tree/master/examples
- **AWS S3 Documentation**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/
- **S3 Security Best Practices**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html
- **S3 Lifecycle Configuration**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html
- **S3 Replication**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html
- **S3 Encryption**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/serv-side-encryption.html
- **S3 Versioning**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html
- **S3 Object Lock**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
- **S3 Storage Classes**: https://aws.amazon.com/s3/storage-classes/
- **S3 Event Notifications**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html
- **S3 Bucket Policies**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-policies.html
- **S3 Access Points**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-points.html
- **S3 Intelligent-Tiering**: https://aws.amazon.com/s3/storage-classes/intelligent-tiering/

## Notes for AI Agents

When using this module in automated workflows:

1. **Security First**: Always enable public access block and encryption by default
2. **Enable Versioning**: Protect against accidental deletions and modifications
3. **Use KMS Encryption**: Prefer KMS over SSE-S3 for sensitive data requiring audit trails
4. **Configure Lifecycle Rules**: Implement lifecycle policies to optimize storage costs
5. **Enable Access Logging**: Track all bucket access for security and compliance
6. **Tag Consistently**: Apply comprehensive tags including Environment, Owner, Purpose
7. **Use Replication**: Implement cross-region replication for critical data
8. **Object Lock for Compliance**: Enable object lock for regulatory compliance requirements
9. **Monitor Costs**: Set up S3 Analytics and Intelligent Tiering for cost optimization
10. **Use Bucket Keys**: Enable bucket_key_enabled for KMS to reduce API costs
11. **Separate Concerns**: Use separate buckets for different purposes (data, logs, backups)
12. **Configure Notifications**: Set up EventBridge or direct notifications for critical events
13. **Test Disaster Recovery**: Regularly validate replication and backup procedures
14. **Review Permissions**: Use IAM Access Analyzer to review bucket policies
15. **Use VPC Endpoints**: Restrict access through VPC endpoints when possible
16. **MFA Delete**: Enable MFA delete for critical production buckets
17. **Conditional Creation**: Use create_bucket variable for environment-specific deployments
18. **Object Ownership**: Set control_object_ownership = true for consistent ACL behavior
