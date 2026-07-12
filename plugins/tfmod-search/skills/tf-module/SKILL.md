---
name: tf-module
description: Look up a Terraform AWS community module and generate a ready-to-paste usage snippet with current variable names. Invoke with a module name or requirement, e.g. "s3 bucket with lifecycle rules" or "eks".
disable-model-invocation: true
---

# Terraform AWS module lookup

Look up Terraform AWS community module documentation for: $ARGUMENTS

1. Call `search_modules` with the query above. List the top-3 hits, one line
   each: module name — short description — relevance score. For ambiguous
   queries pass `top_k` (up to 10) to widen the candidate list.
2. Call `get_module` for the best match. If only part of the document is
   needed, pass `sections` (e.g. `["inputs", "examples"]`) — version pins and
   gotchas are always included.
3. Reply with:
   - The module source and current version, pinned.
   - A minimal working `module` block for the stated requirement, using exact
     documented variable names: all required inputs plus the optional inputs
     relevant to the request.
   - A short list of gotchas worth knowing: recently renamed variables,
     deprecations, notable submodules, or defaults that commonly surprise.
4. If the query is ambiguous or nothing fits well, do not guess — show the
   top-3 candidates with one-line descriptions and ask which to expand.
5. If the request is really about one specific variable, default, or output
   ("what's the default of `X` in vpc?") rather than a whole module, skip the
   full doc and answer with an exact `grep_module_docs` quote — that is what
   the `/tf-grep` command is for, and you can call the same tool here.
