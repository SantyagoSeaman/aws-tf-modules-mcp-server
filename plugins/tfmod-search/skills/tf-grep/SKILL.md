---
name: tf-grep
description: Grep the full, live documentation of any Terraform Registry module for an exact quote — a variable's real default, a submodule input, an output name — optionally at a pinned version. Invoke with a module and a pattern, e.g. "vpc enable_nat_gateway" or "cloudposse/label/null context".
disable-model-invocation: true
---

# Grep live Terraform module documentation

Pull an exact quote from a module's current registry documentation for:
$ARGUMENTS

`get_module` gives a compact curated overview of the 54 AWS catalog modules;
this skill is for the *exact line* — the real default, the precise type, an
output name, a submodule input — from the **live** registry docs of **any**
module, including non-AWS ones and specific older versions.

## Workflow

1. **Resolve the module to a `module_id`** (`namespace/name/provider`):
   - If an argument already looks like `namespace/name/provider` (two slashes,
     e.g. `cloudposse/label/null`), use it directly.
   - Otherwise treat the first argument as a module name and call
     `search_modules`; take the top hit's `module_id`. `search_modules` only
     covers the AWS catalog, so if the target is a non-AWS module and no hit is
     relevant, ask the user for the full `namespace/name/provider` coordinate
     rather than grepping the wrong module.
2. **Detect an optional version.** If an argument looks like a semver
   (`6.6.1`, `20.8.4`), pass it as `version`; otherwise omit it and the latest
   is used.
3. **Build the pattern and grep.** The remaining argument(s) are the search
   intent. For a literal variable/output name, use it as-is (escape regex
   metacharacters such as `.` if the name contains them). Call
   `grep_module_docs` with `module_id`, `pattern`, and `version` when given.
   Narrow with `scope=["inputs"]` / `scope=["outputs"]` when the intent is
   clearly a variable or an output.
4. **Reply with the exact matches** — each with its section label, line number,
   and surrounding context — plus the resolved version and source URL. Do not
   paraphrase; the quote is the deliverable.
5. **Zero matches:** show the `available_sections` the tool returned, broaden
   the pattern once (drop `scope`, loosen the regex) and retry; if it is still
   empty, report that and point at the closest sections to look in.

## Notes

- The pattern is a regex, case-insensitive by default.
- For a module pinned to an older major in a project, pass that version so the
  quote reflects what the code actually targets — the latest docs may have
  moved on.
- `module_id` also appears in every `search_modules` / `modules_list` result
  and in each curated doc's `Module ID` header, so you rarely have to guess it.
- `refresh=true` bypasses the disk cache when you suspect a stale `latest`.
