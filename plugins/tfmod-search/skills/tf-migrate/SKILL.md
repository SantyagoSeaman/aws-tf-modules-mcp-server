---
name: tf-migrate
description: Use when a project contains hand-written aws_* resources that a community terraform-aws-modules module might replace (security group + rules, VPC + subnets + NAT, S3 bucket + policies, IAM role + policies), or when the user asks whether existing resources can be converted to a module. Finds the covering module, verifies coverage attribute-by-attribute, and proposes a replacement — never applies it.
---

# Replace hand-written AWS resources with a community module

The goal is a *trustworthy* replacement proposal: either the module covers
everything the existing resources do — proven attribute-by-attribute — or the
gaps are stated plainly. A replacement that silently drops functionality is
worse than no replacement.

## Workflow

1. **Identify the cluster.** Group the related resources (e.g. one
   `aws_security_group` plus its `aws_security_group_rule`s; a VPC with
   subnets, route tables, NAT, IGW; a bucket with policy/encryption/lifecycle
   resources). List every resource and every attribute they set.
2. **Search from several angles.** Describe the cluster functionally and run
   `search_modules` more than once with different aspects
   ("security group with http ingress rules", "vpc private subnets nat
   gateway", "s3 bucket lifecycle encryption"). One query is not enough. A
   `"low"` confidence verdict on every phrasing is a real signal there is no
   covering module — but a single `"low"` is not; try another angle before
   moving to "poor fit" in step 5.
3. **Read the winner.** `get_module` for the best candidate, pulling
   `sections=["inputs", "submodules"]` for the interface (the default response
   is a compact head); note its current major version.
4. **Coverage check — the critical step.** Build an explicit mapping table:
   every attribute of every existing resource → the module input that
   expresses it. Anything you cannot map goes into a "not covered" list.
   Never claim coverage from memory; only from the retrieved doc. When an
   input's existence is uncertain (the curated head is a summary), confirm it
   with `get_module(name, sections=["inputs", "outputs"])` — the complete
   root-scope interface in one offline call: quote the matched row in the
   mapping table, or move the attribute to "not covered" on a confirmed miss.
5. **Decide honestly.**
   - Full coverage → propose the `module` block (pinned version, exact
     documented variable names) plus the mapping table.
   - Partial coverage → show the gap; recommend hybrid (module + remaining
     raw resources) or keeping the current code.
   - Poor fit → say so plainly and stop.
6. **Migration caveat, always.** Replacing live resources changes state
   addresses: the proposal must mention `moved` blocks /
   `terraform state mv` / `import`, and that a `terraform plan` after the
   rewrite must show no destroy/create churn before anyone applies. Propose;
   never rewrite the files or touch state without explicit approval.

## Output

- Candidate module, pinned version, one-line rationale
- Mapping table: existing resource.attribute → module input
- "Not covered" list (may be empty — say "none")
- Proposed module block (only if coverage supports it)
- State-migration checklist
