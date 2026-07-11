---
name: aws-terraform-modules
description: Use when writing, reviewing, refactoring, or upgrading Terraform code for AWS. Finds the right community terraform-aws-modules module and its current variable names, defaults, and version via the tfmod-search MCP server, instead of relying on memorized module APIs, which are frequently stale.
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
   documentation. Run `terraform validate` and `terraform fmt` when available.

## Notes

- `modules_list` returns the full catalog when it is unclear which module fits.
- Search returns the top-3 matches; if none fits, retry with different terms
  before concluding no module exists.
- The corpus covers the terraform-aws-modules organization only. Modules from
  other namespaces (cloudposse, project-specific) are not indexed — say so
  rather than guessing their APIs.
