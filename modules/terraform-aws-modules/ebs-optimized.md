# Terraform AWS EBS Optimized Module

## Module Information

- **Module Name**: `ebs-optimized`
- **Module ID**: `terraform-aws-modules/ebs-optimized/aws`
- **Source**: `terraform-aws-modules/ebs-optimized/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ebs-optimized
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ebs-optimized/aws/latest
- **Latest Version**: 0.2.1 (final release)
- **Status**: **ARCHIVED** — read-only since November 23, 2021; not maintained
- **Purpose**: Static lookup utility that returns whether a given EC2 instance type supports the `ebs_optimized` flag
- **Service**: AWS EC2 (Elastic Compute Cloud)
- **Category**: Utility, Compute
- **Keywords**: ebs-optimized, ebs, ec2, storage, optimization, instance-type, launch-configuration, autoscaling-group, deprecated, archived, lookup-table, hardcoded-map, ebs-optimized-flag, instance-compatibility
- **Use For**: maintaining legacy Terraform code that already depends on this module, historical reference — for all new code, use the `aws_ec2_instance_type` data source instead (see notice below)

## Important Notice — Prefer the Data Source for New Code

> This module is **archived** and has not been updated since November 2021. Its hardcoded lookup table stops at the instance families available at that time and does **not** include anything released since (`c6a`, `c7g`, `c7i`, `m6a`, `m7g`, `m7i`, `r6i`, `r7g`, `p5`, `trn1`, Graviton3/4 families, etc.). For every unlisted type the module silently returns `0` (unsupported) — a safe-sounding but likely **incorrect** answer, since virtually all current-generation instances support EBS optimization.
>
> **Use the `aws_ec2_instance_type` data source instead** (requires AWS provider >= 3.74):
>
> ```hcl
> data "aws_ec2_instance_type" "this" {
>   instance_type = var.instance_type
> }
>
> resource "aws_instance" "example" {
>   ami           = var.ami_id
>   instance_type = var.instance_type
>   ebs_optimized = data.aws_ec2_instance_type.this.ebs_optimized_support != "unsupported"
> }
> ```
>
> This always reflects AWS's current instance catalog, requires no extra module dependency, and needs no maintenance.

## Description

Terraform AWS EBS Optimized is a single-purpose utility module — it creates no AWS resources — that answers one question: does a given EC2 instance type support EBS optimization? It holds a hardcoded Terraform map of roughly 430 instance type strings to `true`/`false` and exposes the result through a single `answer` output as an integer (`1` or `0`), suitable for direct use in the `ebs_optimized` argument of `aws_instance`, `aws_launch_configuration`, `aws_launch_template`, or `aws_autoscaling_group` resources.

The module exists to prevent a specific failure mode: setting `ebs_optimized = true` on an instance type that doesn't support it. On a plain EC2 instance this fails at apply time; on launch configurations and Auto Scaling Groups the configuration is accepted but instances then fail to launch silently, which is much harder to debug. By centralizing the compatibility check, calling code can pass a variable instance type and always get a safe integer result instead of hand-writing conditionals per instance family.

Because the module was archived in November 2021, its lookup table is frozen at that point — it correctly covers every family through the c6/m6/r6 generation but has no entries for c7/m7/r7, Graviton3+, Trainium/Inferentia2, or anything released since. Unknown instance types (including all newer ones) default to `0`, which never breaks a deployment but can needlessly disable EBS optimization on instances that fully support it. New Terraform code should use the `aws_ec2_instance_type` data source instead (see Important Notice above).

## Key Features

- **Static Lookup Table**: Hardcoded Terraform map covering ~430 instance type strings (409 map to `true`, 21 to `false`)
- **Integer Boolean Output**: Returns `1`/`0`, directly assignable to any `ebs_optimized` argument without a conversion
- **No AWS API Calls**: Pure local computation — no provider credentials needed, no data source round-trip, instant plan
- **Safe Unknown-Type Default**: Instance types not in the map (including everything released after 2021) resolve to `0`, never causing an apply-time failure
- **Minimal Interface**: Single required input (`instance_type`), single output (`answer`)
- **Legacy-Friendly**: Fits patterns built around `aws_launch_configuration` that predate provider-level instance-type introspection

## Main Input Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `instance_type` | `string` | Yes | EC2 instance type to check for EBS optimization support (e.g., `"m5.large"`) |

## Main Outputs

| Output | Description |
|--------|-------------|
| `answer` | `1` if the instance type supports EBS optimization, `0` otherwise (including unknown/newer types) |

## Usage Examples

```hcl
module "ebs_optimized" {
  source  = "terraform-aws-modules/ebs-optimized/aws"
  version = "0.2.1"

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

The lookup table contains 430 entries, frozen as of the November 2021 archive date:

- **Unsupported (`0`), 21 entries**: `c1.medium`, `c3.large`, `c3.8xlarge`, `cc2.8xlarge`, `g2.8xlarge`, `i2.8xlarge`, `m1.medium`, `m1.small`, `m2.xlarge`, `m3.medium`, `m3.large`, `r3.large`, `r3.8xlarge`, `t1.micro`, and every `t2.*` size (`nano` through `2xlarge`)
- **Supported (`1`), 409 entries**: nearly every other family through the c6/m6/r6 generation — `a1`, `c4`/`c5`/`c5a`/`c5ad`/`c5d`/`c5n`/`c6g`/`c6gd`/`c6gn`/`c6i`, `d2`/`d3`/`d3en`, `f1`, `g3`/`g4ad`/`g4dn`/`g5`, `h1`, `i3`/`i3en`, `inf1`, `m4`/`m5`/`m5a`/`m5ad`/`m5d`/`m5dn`/`m5n`/`m5zn`/`m6g`/`m6gd`/`m6i`, `p2`/`p3`/`p3dn`/`p4d`, `r4`/`r5`/`r5a`/`r5ad`/`r5b`/`r5d`/`r5dn`/`r5n`/`r6g`/`r6gd`, `t3`/`t3a`/`t4g`, `x1`/`x1e`/`x2gd`, `z1d`, plus the `u-*`, `mac1`, and `vt1` families
- **Not in the table (defaults to `0`)**: any family released after ~late 2021 — `c6a`, `c6in`, `c7g`/`c7gd`/`c7gn`/`c7i`, `hpc6a`/`hpc6id`/`hpc7g`, `i4i`, `im4gn`/`is4gen`, `m6a`/`m6idn`/`m6in`, `m7g`/`m7i`, `p5`, `r6a`/`r6i`/`r6idn`/`r6in`, `r7g`/`r7iz`, `trn1`, and later generations — even though almost all current-generation instances support EBS optimization

Within older, mixed families (`c1`, `c3`, `m1`, `m2`, `m3`, `r3`), support varies by size — always check the exact size string rather than assuming a whole family behaves uniformly.

## Best Practices

1. **Do not use in new code**: use the `aws_ec2_instance_type` data source instead (see Important Notice above)
2. **Pin the version** if this module must be kept for legacy compatibility: `version = "0.2.1"`, its final release
3. **Treat an `answer` of `0` as ambiguous** for any family newer than c6/m6/r6 — it may mean "genuinely unsupported" or simply "not in the 2021 table"
4. **No credentials required**: safe to evaluate in any context (CI, offline plans) since it performs no AWS API calls, but this is not a reason to prefer it over the data source

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ebs-optimized
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ebs-optimized/aws/latest
- **AWS EBS-Optimized Instances Documentation**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-optimized.html
- **`aws_ec2_instance_type` Data Source (recommended replacement)**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ec2_instance_type
- **AWS EC2 Instance Types Reference**: https://aws.amazon.com/ec2/instance-types/

## Notes for AI Agents

When assisting with Terraform code:

1. **Recommend the data source, not this module**: for any new code, generate `aws_ec2_instance_type` plus `ebs_optimized_support != "unsupported"` instead of calling this module
2. **Flag existing usage**: if this module appears in code being modified, suggest migrating to the data source
3. **Newer instance types give a false negative**: `c6a`, `c7g`, `c7i`, `m6a`, `m7g`, `m7i`, `r6i`, `r7g`, `p5`, `trn1`, and other post-2021 families are not in the table and will incorrectly resolve to `0`
4. **No AWS credentials needed**: the module performs pure local computation, so it works in credential-less/offline contexts — but this is not a reason to prefer it over the data source
5. **If retained for legacy reasons, pin to `0.2.1`**: it is the final and only stable release
