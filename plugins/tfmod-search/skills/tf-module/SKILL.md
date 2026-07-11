---
name: tf-module
description: Look up a Terraform AWS community module and generate a ready-to-paste usage snippet with current variable names. Invoke with a module name or requirement, e.g. "s3 bucket with lifecycle rules" or "eks".
disable-model-invocation: true
---

# Terraform AWS module lookup

Look up Terraform AWS community module documentation for: $ARGUMENTS

1. Call `search_modules` with the query above. List the top-3 hits, one line
   each: module name — short description — relevance score.
2. Call `get_module` for the best match.
3. Reply with:
   - The module source and current version, pinned.
   - A minimal working `module` block for the stated requirement, using exact
     documented variable names: all required inputs plus the optional inputs
     relevant to the request.
   - A short list of gotchas worth knowing: recently renamed variables,
     deprecations, notable submodules, or defaults that commonly surprise.
4. If the query is ambiguous or nothing fits well, do not guess — show the
   top-3 candidates with one-line descriptions and ask which to expand.
