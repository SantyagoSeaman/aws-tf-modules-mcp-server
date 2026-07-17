---
name: tf-stack
description: Scaffold a multi-module Terraform stack for AWS from a requirement, wiring community modules together (outputs into inputs, pinned versions). Invoke with the stack description, e.g. "web app with postgres, a load balancer, and a private VPC".
disable-model-invocation: true
---

# Scaffold a Terraform stack

Scaffold a Terraform stack for: $ARGUMENTS

The hard part of multi-module Terraform is the wiring — vpc outputs into
subnet and security-group inputs of everything downstream. That wiring, with
current variable names, is the deliverable.

1. **Decompose** the requirement into components (network, compute, data,
   load balancing, storage, ...). For each, `search_modules` with a
   functional query; pick the best fit from the top-3. Check `confidence`
   first — on `"low"`, the top hit is not clearly asserted as covering that
   component; try a different phrasing for that component before picking it.
2. **Read before writing.** `get_module` for every chosen module, pulling the
   interface for the wiring: `sections=["inputs", "outputs"]` (the default
   response is a compact head). Blocks are written from the retrieved docs,
   never from memory. Pin each module's `version` to the documented current
   version. When you are unsure of an exact
   output or input name for the wiring, grep it with `grep_module_docs`
   (`scope=["outputs"]` for outputs) rather than guessing; a component with
   no catalog module (non-AWS, third-party) can still be wired from its live
   docs the same way.
3. **Produce one coherent configuration:**
   - `terraform` block with `required_providers` (aws provider version per
     the docs' compatibility notes)
   - module blocks in dependency order, wired explicitly:
     `module.vpc.private_subnets` → database/compute `subnet_ids`,
     security-group module IDs → instance/ALB inputs, and so on, using the
     exact documented output and input names
   - only the variables the requirement needs — do not restate defaults
   - a few root `variable`/`output` definitions where parametrization is
     obviously wanted (environment, CIDR, instance sizing)
4. **Explain briefly**: 3-5 bullets on module choices and wiring decisions,
   plus an explicit list of what was deliberately left out (state backend,
   CI, DNS, secrets) so the user knows the scaffold's edges.
5. Offer `terraform init && terraform validate` as the immediate next step.
