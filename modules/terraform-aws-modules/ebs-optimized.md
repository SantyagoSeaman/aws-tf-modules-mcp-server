---
module_name: ebs-optimized
keywords: [ebs-optimized, ebs, elastic-block-store, ec2, instance-type, storage, performance, throughput, iops, bandwidth, dedicated-bandwidth, instance-optimization, validation, helper-module, utility, lookup, compatibility, storage-optimization, volume-performance, general-purpose-ssd, provisioned-iops, gp3, io1, io2, instance-configuration, launch-configuration, auto-scaling, compute, ebs-volume]
---

# Terraform AWS EBS Optimized Module

## Module Information

- **Module Name**: `ebs-optimized`
- **Source**: `terraform-aws-modules/ebs-optimized/aws`
- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ebs-optimized
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ebs-optimized/aws/latest
- **Latest Version**: 0.2.1
- **Purpose**: Utility module that determines whether a given EC2 instance type supports EBS optimization to prevent configuration errors
- **Service**: AWS EC2 (Elastic Compute Cloud) - EBS Optimization
- **Category**: Utility, Storage, Compute
- **Keywords**: ebs-optimized, ebs, elastic-block-store, ec2, instance-type, storage, performance, throughput, iops, bandwidth, dedicated-bandwidth, instance-optimization, validation, helper-module, utility, lookup, compatibility, storage-optimization, volume-performance, general-purpose-ssd, provisioned-iops, gp3, io1, io2, instance-configuration, launch-configuration, auto-scaling, compute, ebs-volume
- **Use For**: Preventing launch configuration failures with unsupported EBS optimization settings, validating instance type EBS compatibility before deployment, automating EBS optimization configuration across multiple instance types, ensuring consistent EBS performance configuration in Terraform modules, avoiding manual lookup of EBS optimization support, simplifying auto-scaling group launch template configurations, standardizing EBS settings across environments, preventing silent instance launch failures

## Description

**Note: This repository was archived by the owner on November 23, 2021, and is now read-only. Consider using native Terraform data sources or AWS API calls for up-to-date instance type information.**

The AWS EBS Optimized Terraform module is a lightweight utility module designed to programmatically determine whether a specific EC2 instance type supports EBS optimization. EBS-optimized instances provide dedicated throughput to Amazon EBS volumes, minimizing contention between EBS I/O and other network traffic, which is critical for achieving consistent storage performance. This module solves a common problem in Terraform configurations where launch configurations or auto-scaling groups might be created successfully but fail silently when instances attempt to launch due to incompatible EBS optimization settings for certain instance types.

The module maintains a comprehensive lookup table mapping EC2 instance types to their EBS optimization support status, returning a boolean value (1 for true, 0 for false) that can be directly used in the `ebs_optimized` parameter of `aws_instance`, `aws_launch_template`, or `aws_launch_configuration` resources. This approach prevents runtime errors, eliminates the need for manual documentation lookups, and ensures that infrastructure code is self-validating. The module covers a wide range of instance families including general purpose (t2, t3, m5), compute optimized (c5, c6g), memory optimized (r5, x1), and storage optimized (i3, d2) instance types.

By using this module, teams can create dynamic, flexible Terraform configurations that automatically adjust EBS optimization settings based on instance type variables, making it easier to support multiple environments with different instance sizes or to parameterize instance selections without worrying about EBS compatibility. While the module is now archived and may not include the latest instance types introduced after 2021, it serves as a reference implementation for instance type validation patterns and can be forked or adapted for environments with compatible instance type requirements.

## Key Features

- **EBS Optimization Validation**: Determines if an EC2 instance type supports EBS-optimized configuration
- **Boolean Output**: Returns 1 (true) or 0 (false) for direct use in Terraform resource configurations
- **Comprehensive Instance Coverage**: Includes mappings for t1, t2, t3, m1, m2, m3, m4, m5, c1, c3, c4, c5, r3, r4, r5, i2, i3, d2, and many other instance families
- **Silent Failure Prevention**: Prevents launch configurations from creating successfully but failing when instances launch
- **Dynamic Configuration**: Enables parameterized instance type selection with automatic EBS optimization settings
- **Simple Interface**: Single input (instance_type) and single output (answer) for ease of use
- **Integration Ready**: Output can be directly used in aws_instance, aws_launch_template, and aws_launch_configuration resources
- **Zero Dependencies**: Standalone module with no external data source dependencies
- **Lightweight**: Minimal resource footprint using only local variables and outputs
- **Self-Documenting**: Provides implicit documentation of EBS optimization support across instance types

## Main Use Cases

1. **Launch Configuration Validation**: Prevent auto-scaling groups from creating with incompatible EBS optimization settings
2. **Dynamic Instance Selection**: Support variable-driven instance type selection with automatic EBS configuration
3. **Multi-Environment Deployments**: Standardize EBS optimization handling across dev, staging, and production with different instance sizes
4. **Infrastructure Modules**: Build reusable Terraform modules that adapt EBS settings based on instance type parameters
5. **Cost Optimization**: Ensure EBS optimization is only enabled for instance types that support it to avoid configuration errors
6. **Automated Compliance**: Validate that EBS-optimized instances are used where storage performance requirements dictate
7. **CI/CD Pipelines**: Integrate instance type validation into automated infrastructure deployment workflows
8. **Configuration Testing**: Test Terraform configurations against various instance types without manual EBS compatibility checks

## Best Practices

### Module Usage and Integration

1. **Use for Variable Instance Types**: Employ this module when instance types are parameterized or determined dynamically rather than hardcoded
2. **Validate Before Deployment**: Run terraform plan to verify EBS optimization settings before applying infrastructure changes
3. **Archive Status Awareness**: Recognize this module was archived in 2021 and may not include newer instance types (m6i, c7g, etc.)
4. **Consider Alternatives**: For production use with modern instance types, consider using AWS API calls or Terraform data sources
5. **Fork for Updates**: If using newer instance types, fork the module and update the instance type mapping table
6. **Documentation Reference**: Use the module as a quick reference for which older instance types support EBS optimization
7. **Combine with Validation**: Use Terraform validation rules alongside this module for comprehensive instance type checking
8. **Default to Safe Values**: For unknown instance types, default to ebs_optimized = false to prevent launch failures

### EBS Optimization Configuration

1. **Enable by Default for Modern Instances**: Most instance types launched after 2017 are EBS-optimized by default (c5, m5, r5 families)
2. **Understand Cost Implications**: Some older instance types incur additional charges for EBS optimization; newer instances include it free
3. **Match Workload Requirements**: Enable EBS optimization for I/O-intensive workloads, databases, and applications requiring consistent IOPS
4. **Throughput Planning**: Verify instance EBS bandwidth limits match or exceed aggregate attached volume performance requirements
5. **Volume Type Alignment**: Use EBS-optimized instances with gp3, io1, or io2 volumes for maximum performance benefit
6. **Avoid Over-Optimization**: Don't enable EBS optimization for workloads with minimal storage I/O requirements if it incurs additional cost
7. **Testing Performance**: Benchmark storage performance with and without EBS optimization to validate benefits for your workload
8. **Monitor Metrics**: Track CloudWatch metrics for EBS throughput, IOPS, and queue depth to ensure optimization is effective

### Instance Type Selection

1. **Choose Modern Families**: Prefer instance types from 5th generation or newer (m5, c5, r5) which are EBS-optimized by default
2. **Right-Size for IOPS**: Select instance types with sufficient baseline EBS throughput for your volume IOPS requirements
3. **Consider Network Bandwidth**: EBS traffic shares network bandwidth; choose instances with adequate network capacity
4. **Evaluate Burstable Instances**: Be cautious with t2/t3 instances for storage-intensive workloads as they may not support EBS optimization or have limited credits
5. **Storage-Optimized for High I/O**: Use i3, i4i, or d3 instance families for applications requiring local NVMe storage in addition to EBS
6. **Memory-Optimized for Databases**: R-family instances typically provide good EBS throughput for database workloads
7. **Compute-Optimized for Analytics**: C-family instances offer excellent EBS performance for data analytics and processing

### Terraform Code Organization

1. **Module Composition**: Include this module within larger infrastructure modules to handle EBS optimization automatically
2. **Variable Passing**: Pass instance_type variables through to this module rather than hardcoding values
3. **Output Naming**: Use descriptive names when referencing the module output (e.g., `ebs_optimization_supported`)
4. **Conditional Logic**: Combine module output with conditional expressions for complex configuration scenarios
5. **Version Pinning**: Pin module version in production to ensure consistent behavior (e.g., `version = "0.2.1"`)
6. **Documentation**: Comment why EBS optimization is being conditionally applied based on instance type
7. **Testing**: Include tests for various instance types to validate module integration and output handling

### Operational Considerations

1. **Migration Planning**: When upgrading instance types, verify EBS optimization support for target instance families
2. **Launch Template Updates**: Update launch templates to use module output when changing instance type parameters
3. **Auto-Scaling Groups**: Ensure ASG launch templates have correct EBS optimization settings to prevent instance launch failures
4. **Blue-Green Deployments**: Validate EBS settings when deploying new infrastructure with different instance types
5. **Disaster Recovery**: Document EBS optimization requirements in DR runbooks for manual instance provisioning scenarios
6. **Capacity Planning**: Factor in EBS throughput limits when sizing instances for projected I/O workload growth
7. **Cost Monitoring**: Track costs associated with EBS optimization on older instance types that charge additionally

## Additional Resources

- **GitHub Repository**: https://github.com/terraform-aws-modules/terraform-aws-ebs-optimized
- **Terraform Registry**: https://registry.terraform.io/modules/terraform-aws-modules/ebs-optimized/aws/latest
- **Module Examples**: https://github.com/terraform-aws-modules/terraform-aws-ebs-optimized/tree/master/examples
- **AWS EBS-Optimized Instances**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-optimized.html
- **EC2 Instance Types**: https://aws.amazon.com/ec2/instance-types/
- **EBS Volume Types**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volume-types.html
- **EBS Performance**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-performance.html
- **EC2 Instance Configuration**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/LaunchingAndUsingInstances.html
- **AWS Launch Templates**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-templates.html
- **Auto Scaling Groups**: https://docs.aws.amazon.com/autoscaling/ec2/userguide/auto-scaling-groups.html
- **CloudWatch EBS Metrics**: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using_cloudwatch_ebs.html

## Notes for AI Agents

When using this module in automated workflows:

1. **Archive Status**: This module was archived in November 2021 and no longer receives updates; newer instance types are not included
2. **Simple Integration**: Pass instance_type variable to module, use module.ebs_optimized.answer for ebs_optimized resource parameter
3. **Boolean Output**: Module returns 1 (true) or 0 (false), compatible with Terraform's boolean type coercion
4. **Use Case**: Best suited for infrastructure with parameterized instance types where EBS optimization needs dynamic configuration
5. **Modern Alternative**: Consider using Terraform's aws_ec2_instance_type data source for current instance type information
6. **Fallback Strategy**: For instance types not in the module's map, default to ebs_optimized = false to prevent launch failures
7. **Testing**: Validate module output matches AWS documentation for instance types you plan to use
8. **Coverage Limitation**: Module covers instance types available through ~2021; newer families (m6i, c7g, etc.) are not included
9. **No Runtime Dependencies**: Module uses only local variables, no API calls or data sources required
10. **Version Pinning**: Always pin to version 0.2.1 as this is the final release before archival
