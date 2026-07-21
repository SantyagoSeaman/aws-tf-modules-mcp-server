---
name: tf-review
description: Use when reviewing a Terraform change — a git diff, branch, or pull request that touches .tf files. Verifies changed module blocks against current terraform-aws-modules documentation (variables, required inputs, version pinning, deprecations) and flags hand-written resources a community module could replace. Review only; never edits.
---

# Review a Terraform change against current module documentation

Scope discipline: this reviews **module usage in the change**, not style,
naming, or general Terraform hygiene — other tooling owns those.

## Workflow

1. **Establish the diff scope**: the branch/PR the user names, or
   `git diff main...HEAD -- '*.tf'` by default. Only `.tf` hunks matter.
2. **Delegate the reading.** On Claude Code, launch the `tf-diff-reviewer`
   agent with the scope — it reads the diff in its own context, verifies
   every touched module block via `get_module`, and returns a findings
   table; relay that table. Where subagents are unavailable, do the same
   inline: read only the `.tf` hunks, then for each touched
   terraform-aws-modules block check against the current doc:
   - every variable set exists in the current inputs (absence in the compact
     head = *suspicious*, not proof — confirm with `get_module(name,
     sections=["inputs", "outputs"])`, the module's complete root-scope
     interface, before calling it dead)
   - required inputs present, `version` pinned and not a major behind
   - deprecated arguments per the doc's notes
   Blocks whose `source` is outside the curated catalog are verified the same
   way — against their live docs via your other Terraform Registry tooling —
   rather than skipped.
3. **Raw-resource suggestion.** New clusters of hand-written `aws_*`
   resources that a catalog module covers get flagged as a `suggestion`
   with the module name (the full replacement analysis belongs to the
   tf-migrate flow — reference it, don't inline it).
4. **Report**: findings table, most severe first —
   `| # | Severity | File:line | Module | Finding | Fix |` with severities
   `blocker` / `major` / `suggestion` — followed by a 2-3 sentence
   assessment. No findings → say exactly that; do not invent nitpicks.
   Never edit files as part of a review.
