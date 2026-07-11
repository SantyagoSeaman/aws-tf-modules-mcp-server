---
name: tf-module-upgrade
description: Use when the user asks to audit, update, or upgrade terraform-aws-modules usage in an existing project — checking pinned module versions and variable usage against current documentation for drift, renames, removals, and changed defaults. Produces an upgrade report; does not rewrite code unasked.
---

# Audit module usage against current documentation

Module APIs break between majors (security-group v6 rearchitected rules; eks
v21 renamed core inputs). This audit finds what will break — or silently
change — *before* a version bump or `terraform plan` does.

## Workflow

1. **Inventory.** Scan `*.tf` files for `module` blocks whose `source` is
   `terraform-aws-modules/...`. For each block record: file:line, source,
   pinned `version` (or its absence), and every variable set.
2. **Ground truth.** For each distinct module: `get_module` → current version
   and input schema. One call per module, reused across blocks. Passing
   `sections=["inputs", "outputs"]` keeps responses small — version pins and
   gotchas are always included.
3. **Compare, per block:**
   - **Version drift** — pinned version vs current; flag major-version gaps
     loudest; flag missing pins.
   - **Dead variables** — variables set that do not appear in the current
     doc. Treat as *suspicious, not proven dead*: the docs are curated
     summaries; confirm via the registry link in the doc before reporting as
     removed, and mark unconfirmed cases as such.
   - **Deprecations** — arguments the doc notes as deprecated/renamed, with
     the replacement.
   - **Default drift** — variables the block omits whose documented defaults
     differ from the historical behavior the code likely relied on (call
     these out as behavior-change-on-upgrade).
4. **Report, don't rewrite.** Group findings by module, severity ranked:
   breaking rename/removal > missing required on target version > default
   drift > version lag. Each finding: file:line, what, why it matters, the
   exact fix with current variable names.
5. **State warning.** Where an upgrade rearchitects internal resources
   (per-rule security-group resources, renamed internal addresses), note that
   applying it needs `moved` blocks or `terraform state mv`, and that the
   post-upgrade `terraform plan` must be reviewed for destroy/create churn.
6. Apply fixes only on explicit approval — one module at a time, running
   `terraform validate` (and plan, when available) between steps.

On Claude Code, for large projects, delegate steps 1-3 to the
`tf-diff-reviewer` agent with the scope "all *.tf files" so the inventory
does not flood the conversation; elsewhere do it inline with targeted greps.
