---
name: tf-module
description: Look up a Terraform AWS community module and generate a ready-to-paste usage snippet with current variable names. Invoke with a module name or requirement, e.g. "s3 bucket with lifecycle rules" or "eks".
disable-model-invocation: true
---

# Terraform AWS module lookup

Look up Terraform AWS community module documentation for: $ARGUMENTS

1. Call `search_modules` with the query above. List the top-3 hits, one line
   each: module name — short description — relevance score. For ambiguous
   queries pass `top_k` (up to 10) to widen the candidate list. Also note the
   `confidence` verdict: `"high"` means the top hit's own name/keywords/
   description assert the asked capability — trust it. `"low"` means the
   capability is not clearly asserted; it can still be the right module under
   unfamiliar phrasing, so read the top-3 descriptions before deciding whether
   to expand the top hit (step 2) or fall to step 4 (ask instead of guessing).
2. Call `get_module` for the best match. It returns a compact orientation head
   by default, so pull the interface for the block: `sections=["inputs",
   "examples"]` (version pins and gotchas are always included). If a variable
   you need is missing from the curated table or you need its exact type/
   default, `get_module(name, sections=["inputs", "outputs"])` renders the
   module's **complete** root-scope interface in one offline call; for a
   submodule's interface, call `get_module("<name>//modules/<submodule>",
   sections=[...])`.
3. Reply with:
   - The module source and current version, pinned.
   - A minimal working `module` block for the stated requirement, using exact
     documented variable names: all required inputs plus the optional inputs
     relevant to the request. For any nested/complex (`any`/`object(...)`)
     input, check `sections=["examples"]` for the exact shape — a
     bare bool vs an object, a map keyed by a NUMBER vs a name, a plural vs
     singular field — before writing it; never leave a required nested block
     as a prose comment or TODO.
   - A short list of gotchas worth knowing: recently renamed variables,
     deprecations, notable submodules, or defaults that commonly surprise.
4. If the query is ambiguous, confidence is `"low"`, or nothing fits well, do
   not guess — show the top-3 candidates with one-line descriptions and ask
   which to expand. A `"low"` verdict is not proof the module is missing from
   the catalog; try a different phrasing before telling the user it does not
   exist.
5. If the request is really about one specific variable, default, or output
   ("what's the default of `X` in vpc?") rather than a whole module, skip the
   orientation head and go straight to `get_module(name, sections=["inputs",
   "outputs"])` for the complete interface, then quote the exact row.
