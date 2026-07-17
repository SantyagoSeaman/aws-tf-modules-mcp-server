# Terraform AWS VPC Peering Module

## Module Information

- **Module Name**: `vpc-peering`
- **Module ID**: `cloudposse/vpc-peering/aws`
- **Source**: `cloudposse/vpc-peering/aws`
- **GitHub Repository**: https://github.com/cloudposse/terraform-aws-vpc-peering
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/vpc-peering/aws/latest
- **Latest Version**: 1.0.1
- **Purpose**: Terraform module that creates a same-account `aws_vpc_peering_connection` between a requestor and an acceptor VPC, plus the bidirectional routes needed for instances in each VPC to reach the other
- **Service**: AWS VPC (Virtual Private Cloud) Peering
- **Category**: Networking, Multi-VPC Connectivity
- **Keywords**: vpc-peering, peering-connection, cross-vpc, vpc-peer, same-account-peering, inter-vpc-connectivity, route-propagation, cidr-routing, dns-resolution, requestor-acceptor, private-connectivity, multi-vpc, auto-accept, route-table, vpc, cloudposse, context-label
- **Use For**: connecting two VPCs owned by the same AWS account, shared-services/hub VPC connectivity for multiple workload VPCs, bridging a legacy VPC into a newly Terraform-managed VPC, EKS or application VPC access to a shared-services VPC, selective route exposure via route-table tag filters, private cross-VPC DNS resolution, cost-effective two-VPC connectivity as a lighter alternative to Transit Gateway, environment segmentation with controlled connectivity

## Description

This module creates an `aws_vpc_peering_connection` between two VPCs in the same AWS account (the "requestor" and the "acceptor") and, because `auto_accept = true` is valid only when both VPCs belong to the same account, the connection is created and accepted in a single resource. Around that connection it looks up both VPCs — by ID (`requestor_vpc_id`/`acceptor_vpc_id`) or by tag match (`requestor_vpc_tags`/`acceptor_vpc_tags`) — via the `aws_vpc` data source, discovers every CIDR block associated with each VPC (including secondary/additional CIDR blocks, not just the primary one), and creates `aws_route` entries in both directions so that route tables in the requestor VPC gain routes to the acceptor's CIDRs and vice versa.

The module exists to remove the tedious, error-prone work of wiring up bidirectional routes by hand across every route table in two VPCs. It does this while still giving you control: `requestor_ignore_cidrs`/`acceptor_ignore_cidrs` exclude specific CIDR ranges (for example, overlapping or reserved blocks) from route creation, and `requestor_route_table_tags`/`acceptor_route_table_tags` scope route creation to only the route tables that match a given tag, rather than every route table the `aws_route_tables` data source finds in the VPC. DNS resolution across the peering (`requestor_allow_remote_vpc_dns_resolution`/`acceptor_allow_remote_vpc_dns_resolution`) and the peering connection's create/update/delete timeouts are independently configurable per side.

The module is published by Cloud Posse under the `cloudposse` namespace and uses Cloud Posse's `context`/`label` (`null-label`) convention for consistent resource naming and tagging (`namespace`, `stage`, `name`, `tags`, and a bundling `context` object) rather than the `terraform-aws-modules` conventions used elsewhere in this catalog. There are no submodules — it manages three resource types (`aws_vpc_peering_connection`, two `aws_route` resources) directly. A separate Cloud Posse module, `cloudposse/vpc-peering-multi-account/aws`, handles the cross-account case using multiple AWS provider aliases; it is not covered by this document.

## Key Features

- **Automatic Same-Account Acceptance**: `auto_accept = true` (default) creates and accepts the peering connection in one resource — valid only because both VPCs are in the same AWS account
- **VPC Lookup by ID or Tags**: Identify the requestor/acceptor VPC directly via `*_vpc_id`, or indirectly by tag match via `*_vpc_tags`, without needing to know the VPC ID up front
- **Bidirectional CIDR-Aware Routing**: Automatically creates `aws_route` entries in both directions for every CIDR block associated with each VPC, including secondary/additional CIDR block associations
- **Route Table Tag Filtering**: `requestor_route_table_tags`/`acceptor_route_table_tags` scope automatic route creation to only the route tables matching given tags, instead of every route table in the VPC
- **CIDR Block Exclusion**: `requestor_ignore_cidrs`/`acceptor_ignore_cidrs` skip specific CIDR ranges from route creation (e.g., overlapping or reserved ranges)
- **Independent DNS Resolution Toggles**: `requestor_allow_remote_vpc_dns_resolution`/`acceptor_allow_remote_vpc_dns_resolution` (default `true`) control private DNS resolution across the peering on each side separately
- **Configurable Operation Timeouts**: `create_timeout`/`update_timeout`/`delete_timeout` tune how long Terraform waits on the underlying `aws_vpc_peering_connection`
- **Cloud Posse Context/Label Convention**: Standardized `namespace`/`stage`/`name`/`tags`/`context` naming and tagging shared across all Cloud Posse modules
- **Conditional Creation**: `enabled` (via `context`) toggles all resources without removing the module block
- **Minimal Resource Footprint**: No submodules — a single peering connection plus data-source-driven route creation
- **Connection Status & ID Outputs**: `connection_id` and `accept_status` for chaining into downstream resources or validation

## Main Use Cases

1. **Same-Account Multi-VPC Connectivity**: Connect two VPCs owned by the same AWS account for shared service or data access
2. **Shared-Services Hub VPC**: Peer a shared-services VPC (CI/CD tooling, shared datastores) to one or more workload VPCs
3. **Environment Segmentation with Connectivity**: Keep dev/staging isolated in separate VPCs while allowing controlled, filtered peering to a shared VPC
4. **Legacy VPC Migration**: Bridge a legacy VPC (matched by tags) to a newly Terraform-managed VPC during a phased migration
5. **Selective Route Exposure**: Expose only specific route tables/subnets across the peering using route-table tag filters
6. **EKS/Application Cross-VPC Networking**: Connect an application or EKS VPC to a peer VPC hosting shared datastores or internal tooling
7. **Cost-Effective Alternative to Transit Gateway**: For simple two-VPC connectivity, avoid Transit Gateway's hourly and per-GB attachment charges
8. **Private Cross-VPC DNS Resolution**: Resolve private DNS hostnames (e.g., RDS, ElastiCache endpoints) across peered VPCs
9. **CIDR-Filtered Route Propagation**: Exclude overlapping or reserved CIDR ranges from automatic route creation between two VPCs

## Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `requestor_vpc_id` | `string` | `""` | Requestor VPC ID (use instead of `requestor_vpc_tags` to identify the VPC directly) |
| `acceptor_vpc_id` | `string` | `""` | Acceptor VPC ID (use instead of `acceptor_vpc_tags` to identify the VPC directly) |
| `requestor_vpc_tags` | `map(string)` | `{}` | Tags used to look up the requestor VPC when `requestor_vpc_id` is not set |
| `acceptor_vpc_tags` | `map(string)` | `{}` | Tags used to look up the acceptor VPC when `acceptor_vpc_id` is not set |
| `auto_accept` | `bool` | `true` | Automatically accept the peering connection; both VPCs must be in the same AWS account |
| `requestor_allow_remote_vpc_dns_resolution` | `bool` | `true` | Allow the requestor VPC to resolve public DNS hostnames to private IPs across the peering |
| `acceptor_allow_remote_vpc_dns_resolution` | `bool` | `true` | Allow the acceptor VPC to resolve public DNS hostnames to private IPs across the peering |
| `requestor_route_table_tags` | `map(string)` | `{}` | Only add peer routes to requestor VPC route tables matching these tags (empty = all route tables) |
| `acceptor_route_table_tags` | `map(string)` | `{}` | Only add peer routes to acceptor VPC route tables matching these tags (empty = all route tables) |
| `requestor_ignore_cidrs` | `list(string)` | `[]` | CIDR blocks from the requestor VPC to exclude from route creation |
| `acceptor_ignore_cidrs` | `list(string)` | `[]` | CIDR blocks from the acceptor VPC to exclude from route creation |
| `create_timeout` | `string` | `"3m"` | VPC peering connection create timeout |
| `update_timeout` | `string` | `"3m"` | VPC peering connection update timeout |
| `delete_timeout` | `string` | `"5m"` | VPC peering connection delete timeout |
| `namespace` | `string` | `null` | ID element: usually an abbreviation of the organization name (Cloud Posse label convention) |
| `stage` | `string` | `null` | ID element: usually the environment/role, e.g. `prod`, `staging`, `dev` (Cloud Posse label convention) |
| `name` | `string` | `null` | ID element: the component or solution name, e.g. `cluster` (Cloud Posse label convention) |
| `tags` | `map(string)` | `{}` | Additional tags merged onto all created resources |
| `context` | `any` | `{}` (see Cloud Posse `null-label` defaults) | Single object bundling the entire label context at once; see `namespace`, `stage`, `name`, `tags` above — leave those `null` to inherit from this object instead |
| `enabled` | `bool` | `null` | Set to `false` (or via `context.enabled`) to prevent the module from creating any resources |

## Main Outputs

| Output | Description |
|--------|-------------|
| `connection_id` | VPC peering connection ID |
| `accept_status` | The status of the VPC peering connection request |

## Usage Examples

### Example 1: Peering by VPC ID

```hcl
module "vpc_peering" {
  source  = "cloudposse/vpc-peering/aws"
  version = "1.0.1"

  namespace = "eg"
  stage     = "dev"
  name      = "cluster"

  requestor_vpc_id = "vpc-0123456789abcdef0"
  acceptor_vpc_id  = "vpc-0fedcba9876543210"

  tags = {
    Environment = "dev"
  }
}

# NOTE: if you change *_allow_remote_vpc_dns_resolution from its current live
# value, plan on running `terraform apply` twice — see Important Gotchas below.
```

### Example 2: Peering by VPC tags (bridging a legacy VPC)

```hcl
module "vpc_peering" {
  source  = "cloudposse/vpc-peering/aws"
  version = "1.0.1"

  namespace = "eg"
  stage     = "prod"
  name      = "shared-services"

  requestor_vpc_tags = {
    "kubernetes.io/cluster/my-k8s" = "owned"
  }
  acceptor_vpc_tags = {
    Name = "legacy-vpc"
  }

  tags = {
    Environment = "production"
  }
}
```

### Example 3: Selective routing with CIDR exclusion and one-sided DNS resolution

```hcl
module "vpc_peering" {
  source  = "cloudposse/vpc-peering/aws"
  version = "1.0.1"

  namespace = "eg"
  stage     = "prod"
  name      = "shared-datastore"

  requestor_vpc_id = module.workload_vpc.vpc_id
  acceptor_vpc_id  = module.shared_services_vpc.vpc_id

  # Only wire up routes on route tables tagged for this workload
  requestor_route_table_tags = {
    Tier = "private"
  }
  acceptor_route_table_tags = {
    Tier = "shared-services"
  }

  # Skip a reserved/overlapping CIDR block on the shared-services side
  acceptor_ignore_cidrs = ["100.64.0.0/16"]

  # Only the shared-services side needs to resolve the workload VPC's private DNS
  requestor_allow_remote_vpc_dns_resolution = false
  acceptor_allow_remote_vpc_dns_resolution  = true

  tags = {
    Environment = "production"
  }
}
```

## Important Gotchas

**IMPORTANT**: Read these before generating configuration for this module — they cause plan/apply convergence issues that are easy to misdiagnose:

1. **DNS resolution options need a second `apply` to converge**: the `accepter`/`requester` blocks that carry `*_allow_remote_vpc_dns_resolution` live directly on the `aws_vpc_peering_connection` resource, but AWS will not durably apply those options until the peering connection itself is active. On the very first `apply` (or any `apply` that changes these values from their current live state), Terraform can create/update the connection and report the DNS-resolution options as applied while AWS has not actually converged them yet — the fix is simply to run `terraform apply` again immediately after. Do not treat a second required `apply` on this module as a bug; budget for it in any one-shot CI pipeline.
2. **Same-account only**: `auto_accept = true` is only valid when both the requestor and acceptor VPCs are owned by the same AWS account. For cross-account peering, use the separate `cloudposse/vpc-peering-multi-account/aws` module (it uses multiple AWS provider aliases) — do not try to force this module across accounts.
3. **Route discovery includes secondary CIDR blocks**: routes are created for every CIDR block association the `aws_vpc` data source returns for each VPC — including secondary/additional CIDR blocks, not just the VPC's primary CIDR — so a VPC with multiple CIDR associations gets more routes per route table than a single-CIDR VPC. Use `requestor_ignore_cidrs`/`acceptor_ignore_cidrs` to exclude ranges you do not want routed (e.g., overlapping or reserved CIDRs).
4. **Route table discovery is broad by default**: with no `*_route_table_tags` set, the module targets every route table the `aws_route_tables` data source finds in each VPC — potentially many more route tables than expected in a VPC with several subnets/tiers. Set `requestor_route_table_tags`/`acceptor_route_table_tags` to scope this down deliberately.

## Best Practices

### Route Table Scope and CIDR Hygiene

1. **Tag Route Tables for Scoping**: Apply a consistent tag (e.g., `Tier = "private"`) to the route tables that should receive peer routes, and pass it via `requestor_route_table_tags`/`acceptor_route_table_tags`, rather than letting the module target every route table in the VPC.
2. **Exclude Overlapping CIDRs Explicitly**: If either VPC has secondary CIDR ranges that must not be routed across the peering (e.g., a CGNAT range used for pod networking), list them in `requestor_ignore_cidrs`/`acceptor_ignore_cidrs`.
3. **Verify No CIDR Overlap Before Peering**: AWS rejects (or silently blackholes traffic for) peering connections between VPCs with overlapping CIDR blocks — confirm non-overlapping ranges before applying.

### Convergence and Automation

1. **Expect Two Applies for DNS Options**: In CI/CD pipelines, run `terraform apply` twice (or re-run on first-apply drift) whenever `*_allow_remote_vpc_dns_resolution` changes, per the gotcha above.
2. **Pin the Module Version**: Use an explicit `version = "1.0.1"` (or `~> 1.0`) for reproducible deployments rather than tracking `latest`.
3. **Prefer Tag-Based Lookup for Cross-Team VPCs**: When the peer VPC is owned by a different team/module, `*_vpc_tags` avoids a hardcoded VPC ID dependency and tolerates VPC recreation as long as the tag persists.

### DNS and Connectivity

1. **Enable DNS Resolution for Private Service Discovery**: Set both `requestor_allow_remote_vpc_dns_resolution` and `acceptor_allow_remote_vpc_dns_resolution` to `true` when instances need to resolve private hostnames (e.g., RDS, ElastiCache) across the peering.
2. **Disable It Where Not Needed**: Turn off DNS resolution on the side that never needs to resolve the peer's private DNS records to reduce the attack surface.

### Same-Account Scope and Security

1. **Do Not Force Cross-Account Use**: Route cross-account requirements to `cloudposse/vpc-peering-multi-account/aws` instead of working around this module's same-account assumption.
2. **Scope Routes, Not Just Connections**: Peering grants network reachability; still rely on security groups and NACLs on both sides to restrict which resources can actually communicate over the peering.

### Naming and Tagging

1. **Use the Cloud Posse Context Object for Shared Defaults**: Pass a single `context` object (e.g., `module.this.context` from an upstream Cloud Posse module) so naming and tagging stay consistent with the rest of a Cloud Posse-managed stack.
2. **Set `name` to Describe the Relationship**: Use a descriptive `name` (e.g., `shared-services`, `legacy-bridge`) so the generated `id`/tags make the peering's purpose clear in the console and in `connection_id` references.

## Additional Resources

- **GitHub Repository**: https://github.com/cloudposse/terraform-aws-vpc-peering
- **Terraform Registry**: https://registry.terraform.io/modules/cloudposse/vpc-peering/aws/latest
- **Module Examples**: https://github.com/cloudposse/terraform-aws-vpc-peering/tree/main/examples/complete
- **Related Module - VPC (Cloud Posse)**: https://registry.terraform.io/modules/cloudposse/vpc/aws/latest
- **Related Module - VPC Peering, Multi-Account (Cloud Posse)**: https://registry.terraform.io/modules/cloudposse/vpc-peering-multi-account/aws/latest
- **AWS VPC Peering Documentation**: https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html
- **AWS VPC Peering Routing Options**: https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-routing.html
- **AWS VPC Peering DNS Resolution**: https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-dns.html
- **`aws_vpc_peering_connection` Resource Reference**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_peering_connection
- **Data Transfer Pricing (peering)**: https://aws.amazon.com/vpc/pricing/

## Notes for AI Agents

When using this module in automated workflows:

1. **Cloud Posse Provenance**: This module is published by Cloud Posse (namespace `cloudposse`), not the `terraform-aws-modules` org. It uses Cloud Posse's `context`/`label` convention — inputs like `namespace`, `stage`, `name`, `environment`, `tenant`, `attributes`, `tags` and a `context` object drive resource naming/tagging across every Cloud Posse module. Do NOT propagate this convention onto other (differently-styled) modules in the same project; set the label inputs this module needs and leave other vendors' modules alone.
2. **Plan for a Second `apply`**: Any change to `requestor_allow_remote_vpc_dns_resolution`/`acceptor_allow_remote_vpc_dns_resolution` (including the initial create) may not fully converge on the first `terraform apply` because AWS only accepts peering-connection option changes once the connection is active — re-run `apply` once more rather than treating a lingering diff as an error.
3. **Same-Account Assumption**: This module assumes both VPCs are in the same AWS account (`auto_accept = true`). If the task requires cross-account peering, use `cloudposse/vpc-peering-multi-account/aws` instead — do not attempt to adapt this module with multiple providers.
4. **VPC Lookup — ID vs. Tags**: Use `requestor_vpc_id`/`acceptor_vpc_id` when the VPC ID is already known; use `requestor_vpc_tags`/`acceptor_vpc_tags` when it should be resolved by tag match instead (never set both ID and tags for the same side).
5. **Scope Routes Deliberately**: Without `requestor_route_table_tags`/`acceptor_route_table_tags`, the module wires routes into every route table in both VPCs; set these tags whenever only specific tiers/subnets should gain peer routes.
6. **No Submodules**: This is a single-resource-group module (`aws_vpc_peering_connection` plus two `aws_route` resources) with no submodules or nested components.
7. **Version Pinning**: Use an explicit `version = "1.0.1"` constraint for reproducible deployments.
