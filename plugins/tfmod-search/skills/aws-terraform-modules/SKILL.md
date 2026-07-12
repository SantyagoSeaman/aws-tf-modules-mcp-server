---
name: aws-terraform-modules
description: Use when writing new or modifying existing Terraform code for AWS. Finds the right community terraform-aws-modules module and its current variable names, defaults, and version via the tfmod-search MCP server, instead of relying on memorized module APIs, which are frequently stale. (Dedicated skills exist for diffs/PRs, module version audits, converting raw resources, and diagnosing terraform errors — this one is for authoring.)
---

# Writing Terraform with AWS community modules

The tfmod-search MCP server provides current documentation for all 54 community
terraform-aws-modules, indexed for hybrid search. Module APIs change between
major versions, so memorized variable names and defaults are unreliable — always
work from the retrieved documentation.

## Workflow

1. **Search first.** Before writing any `module` block or `aws_*` resource, call
   `search_modules` with a descriptive query for the component you are about to
   write, e.g. "vpc with private subnets and nat gateway", "rds postgres multi-az",
   "s3 bucket with lifecycle rules and encryption".
2. **Read the documentation.** Call `get_module` for the best match. The document
   contains the current major version, complete inputs and outputs, usage
   examples, and available submodules.
3. **Write from the doc, not from memory.**
   - Use exact variable names as documented. Modules rename variables between
     major versions (for example, security-group v6 rearchitected per-rule
     resources; eks v21 renamed many cluster inputs).
   - Pin the module `version` to the version shown in the documentation.
   - Set only the variables the requirement needs; do not restate defaults.
4. **Prefer the community module** over hand-written `aws_*` resources when it
   covers the use case — modules encode hardening, tagging, and edge cases.
   Fall back to raw resources only when the module does not support the required
   configuration (verify in the documentation first) or would over-abstract a
   single trivial resource.
5. **Verify.** After writing, cross-check every variable used against the
   documentation. When you are unsure a variable exists, or the project pins an
   older major than the doc describes, confirm it with `grep_module_docs` — an
   exact quote from the live registry docs at that version — instead of
   shipping the uncertainty. Run `terraform validate` and `terraform fmt` when
   available.

## Notes

- `modules_list` returns the full catalog when it is unclear which module fits.
- Search returns the top-3 matches by default; pass `top_k` (up to 10) for
  ambiguous queries, and if nothing fits, retry with different terms before
  concluding no module exists.
- `get_module` returns the full document by default; pass `sections`
  (e.g. `["inputs", "examples"]`, or a heading substring like `"karpenter"`)
  to keep the response small — version pins, agent notes, and gotchas are
  always included.
- The curated corpus covers the terraform-aws-modules organization only, so
  `search_modules`/`get_module` will not find other namespaces (cloudposse,
  project-specific). You are not stuck: `grep_module_docs` greps the live
  registry docs of *any* module — derive its `module_id` from the block's
  `source` and grep the variable you need. Say the module is outside the
  curated catalog, then verify against its live docs rather than guessing.
