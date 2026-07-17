---
name: aws-terraform-modules
description: Use when writing new or modifying existing Terraform code for AWS. Finds the right community terraform-aws-modules module and its current variable names, defaults, and version via the tfmod-search MCP server, instead of relying on memorized module APIs, which are frequently stale. (Dedicated skills exist for diffs/PRs, module version audits, converting raw resources, and diagnosing terraform errors — this one is for authoring.)
---

# Writing Terraform with AWS community modules

The tfmod-search MCP server provides current documentation for the community
terraform-aws-modules catalog, indexed for hybrid search. Module APIs change
between major versions, so memorized variable names and defaults are
unreliable — always work from the retrieved documentation.

## Workflow

1. **Search first.** Before writing any `module` block or `aws_*` resource, call
   `search_modules` with a descriptive query for the component you are about to
   write, e.g. "vpc with private subnets and nat gateway", "rds postgres multi-az",
   "s3 bucket with lifecycle rules and encryption".
2. **Orient, then pull what you need.** Call `get_module` for the best match. By
   default it returns a compact **orientation head** — what the module is, the
   current version and exact pin, gotchas, key features, and a menu of the other
   sections. It is a **curated subset**, not the whole doc. To write the block,
   pull the interface: `get_module(name, sections=["inputs", "examples"])` (add
   `"outputs"` when wiring modules together, `"submodules"` when you need one).
3. **Match the documentation depth to the question — use the least that answers it.**
   - **Greenfield, common case** (defaults are fine): the curated inputs/examples
     sections are usually enough. Go no deeper.
   - **Reproducing an existing resource** (migration/brownfield), or you need an
     input that is **not in the curated table**, an input's **exact type or
     default**, the **complete** inputs/outputs, or a concrete shape of a complex
     (`any`/`object(...)`) input: the curated table is a subset — get the exact,
     complete answer from the live registry doc with `grep_module_docs` (grep by
     the variable name, or the `examples` section). Never assert an exact default,
     type, or that an input exists from the summary or from memory when a wrong
     value would break `apply`.
4. **Write from the doc, not from memory.**
   - Use exact variable names as documented. Modules rename variables between
     major versions (for example, security-group v6 rearchitected per-rule
     resources; eks v21 renamed many cluster inputs).
   - Pin the module `version` to the version shown in the documentation.
   - Set only the variables the requirement needs; do not restate defaults.
   - For any nested/complex (`any`/`object(...)`) input, check the `examples`
     section before writing it — a bare bool vs an object, a map keyed by a
     NUMBER vs a name, a plural vs singular field, or a sub-block that
     defaults ON is usually visible only there, not in the inputs table. Never
     leave a required nested block as a prose comment or TODO; write the
     exact shape the doc/examples show.
5. **Prefer the community module** over hand-written `aws_*` resources when it
   covers the use case — modules encode hardening, tagging, and edge cases.
   Fall back to raw resources only when the module does not support the required
   configuration (verify in the documentation first) or would over-abstract a
   single trivial resource.
6. **Verify.** After writing, cross-check every variable used against the
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
- `search_modules` also returns a `confidence` verdict. `"high"` — the top
  hit's own name/keywords/description assert the asked capability; trust it.
  `"low"` — the capability is not clearly asserted; this does NOT mean "not in
  catalog" by itself, it can still be the right module under unfamiliar
  phrasing, so rephrase and/or check `get_module`/`modules_list` before
  concluding no module exists. An exclusion-phrased query ("X without Y") is
  not evaluated as a negation and can grade `"high"` on the excluded
  technology — read the description before trusting that verdict.
- `get_module` returns a compact orientation head by default; pass `sections`
  (e.g. `["inputs", "examples"]`, or a heading substring like `"karpenter"`)
  to pull the parts you need, or `sections=["all"]` for the whole curated doc.
  Version pins, agent notes, and gotchas are always included. The head and
  `sections=[...]` responses carry a footer that names every available section
  and points to `grep_module_docs` for the complete, exact inputs/outputs; the
  `sections=["all"]` escape hatch returns the curated doc verbatim (no footer).
- The curated corpus covers the terraform-aws-modules organization only, so
  `search_modules`/`get_module` will not find other namespaces (cloudposse,
  project-specific). You are not stuck: `grep_module_docs` greps the live
  registry docs of *any* module — derive its `module_id` from the block's
  `source` and grep the variable you need. Say the module is outside the
  curated catalog, then verify against its live docs rather than guessing.
