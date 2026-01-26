# Terraform AWS EBS Optimized Module

## Module Information

- **Module Name**: `ebs-optimized`
- **Source**: `terraform-aws-modules/ebs-optimized/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ebs-optimized
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ebs-optimized/aws/latest
- **Latest Version**: 0.2.1
- **Status**: **ARCHIVED** (November 23, 2021) - Read-only, no longer maintained
- **Purpose**: Utility module that determines whether an EC2 instance type supports EBS optimization
- **Service**: AWS EC2 (Elastic Compute Cloud)
- **Category**: Utility, Compute
- **Keywords**: ebs-optimized, ebs, ec2, instance-type, storage-performance, validation, helper-module, launch-configuration, auto-scaling, compute

## Important Notice

> **This module was archived on November 23, 2021 and is no longer maintained.**
>
> **Recommended Alternative**: Use the `aws_ec2_instance_type` data source (AWS provider v3.74+) instead:
> ```hcl
> data "aws_ec2_instance_type" "this" {
>   instance_type = "m5.large"
> }
>
> resource "aws_instance" "example" {
>   ami           = "ami-12345678"
>   instance_type = "m5.large"
>   ebs_optimized = data.aws_ec2_instance_type.this.ebs_optimized_support != "unsupported"
> }
> ```

## Description

The AWS EBS Optimized module is a lightweight utility that determines whether a specific EC2 instance type supports EBS optimization by looking up the instance type in a hardcoded map of 600+ instance types. It returns `1` (true) or `0` (false) that can be directly used in the `ebs_optimized` parameter of EC2 resources.

This module solves a problem where launch configurations or auto-scaling groups might be created successfully but fail when instances attempt to launch due to incompatible EBS optimization settings. However, since the module was archived in November 2021, it does not include newer instance types (c6i, c7g, m6i, m7g, r6i, r7g, Graviton3, etc.).

## Key Features

- **EBS Optimization Lookup**: Returns 1 (true) or 0 (false) for direct use in Terraform resources
- **600+ Instance Types**: Covers instance families available through 2021
- **Safe Defaults**: Unknown instance types return 0 (false) to prevent launch failures
- **Zero Dependencies**: No AWS API calls, uses only local variables
- **Simple Interface**: Single input (`instance_type`) and single output (`answer`)

## Input Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `instance_type` | `string` | Yes | EC2 instance type to check for EBS optimization support |

## Outputs

| Output | Description |
|--------|-------------|
| `answer` | Returns `1` if instance type supports EBS optimization, `0` otherwise |

## Usage Example

```hcl
module "ebs_optimized" {
  source  = "terraform-aws-modules/ebs-optimized/aws"
  version = "~> 0.2.1"

  instance_type = "m5.large"
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "m5.large"
  ebs_optimized = module.ebs_optimized.answer
}

resource "aws_launch_configuration" "app" {
  image_id      = data.aws_ami.ubuntu.id
  instance_type = "m5.large"
  ebs_optimized = module.ebs_optimized.answer
}
```

## Instance Type Coverage

**Supported (returns 1)**: c5, c5a, c5d, c5n, c6g, m5, m5a, m5d, m5n, m6g, r5, r5a, r5b, r5d, r6g, t3, t4g, g4dn, i3en, p3, p4d

**Unsupported (returns 0)**: t2 (all sizes), c1, c3.large, m1, m3.medium, m3.large, r3.large

**Unknown types**: Default to 0 (false)

## Limitations

1. **Outdated Data**: Missing instance types released after November 2021 (c6i, c7g, m6i, m7g, r7g, Graviton3, newer GPU instances)
2. **No Validation**: Does not verify if instance type actually exists in AWS
3. **Integer Output**: Returns 0/1 instead of boolean

## Modern Alternative (Recommended)

Use the `aws_ec2_instance_type` data source instead of this archived module:

```hcl
# Modern approach - always up-to-date
data "aws_ec2_instance_type" "this" {
  instance_type = var.instance_type
}

resource "aws_instance" "example" {
  ami           = var.ami_id
  instance_type = var.instance_type
  ebs_optimized = data.aws_ec2_instance_type.this.ebs_optimized_support != "unsupported"
}
```

This approach:
- Queries AWS API for current instance type data
- Supports all instance types including newest families
- No maintenance required

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ebs-optimized
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ebs-optimized/aws/latest
- **AWS EBS-Optimized Instances**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-optimized.html
- **aws_ec2_instance_type Data Source**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ec2_instance_type

## Notes for AI Agents

When assisting with Terraform code:

1. **Recommend Alternative**: Suggest `aws_ec2_instance_type` data source instead of this archived module for new projects
2. **Archive Status**: This module was archived in 2021 and lacks newer instance types
3. **Safe Default**: The module returns 0 for unknown types, which may incorrectly mark newer EBS-optimized instances as unsupported
4. **Simple Migration**: Replace module call with data source lookup for up-to-date results
5. **Version Pin**: If using this module, pin to version `0.2.1` (final release)
6. **No API Calls**: Module uses hardcoded map, no AWS credentials required
