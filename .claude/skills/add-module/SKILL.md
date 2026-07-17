---
name: add-module
description: Maintainer skill for this repository — onboard a new Terraform module into the search catalog from a Terraform Registry URL or module address. Writes the doc, curates keywords, rebuilds the index, and verifies the module is searchable.
---

# Add a module to the catalog

Input: a Terraform Registry URL (or `namespace/name/provider` address).

## 0. Eligibility gate — capability-unique catalog (READ AND APPLY FIRST)

**One capability = one module. Do NOT onboard a module whose capability the
catalog already covers.** Add a module only when it fills a genuine capability
gap. This gate runs before anything else; if the module fails it, stop — do not
write a doc.

- **Capability granularity, not service granularity.** "Two VPC modules from two
  vendors" is a duplicate — reject the second. But genuinely distinct
  capabilities are separate even for the same service: API Gateway REST (v1) and
  HTTP (v2) are two capabilities; both may live in the catalog. A mechanism
  variant (e.g. EKS IRSA/OIDC vs EKS Pod Identity) is an editorial call — default
  to reject unless a real, stated need distinguishes it.
- **Why this is load-bearing.** `search_modules` returns ONE canonical answer and
  the confidence verdict is built on "does the single top-1 assert the asked
  capability." If two modules from two vendors both answer one query, the top-1
  becomes an arbitrary ranker tie, the verdict layer's one-canonical-answer
  invariant breaks, and the user is silently forced to choose a provider per
  query. That is exactly the registry-dump failure mode the curated catalog
  exists to avoid — measured in the A/B eval: a weak consumer picks by
  popularity, not fit, when a query returns modules from many publishers.
- **The catalog may be vendor-heterogeneous, but never capability-ambiguous.**
  Sourcing a gap-filler from a second vendor (e.g. Cloud Posse for `config`,
  `security-hub`, `cloudtrail`, `ses`, `vpc-peering`) is fine — precisely because
  each fills a capability `terraform-aws-modules` lacks, so no query ever returns
  two candidates. Because there is only ever one module per capability, a
  consumer never has to force a provider.
- **Provenance stays honest.** The `## Module Information` **Source** / **Module
  ID** bullet MUST carry the module's true registry namespace (e.g.
  `cloudposse/config/aws`), never re-badged as `terraform-aws-modules`. The
  `modules/terraform-aws-modules/` directory is just the catalog location, not a
  vendor claim.
- **Isolate opinionated conventions.** If a second-vendor module bakes in a house
  convention (e.g. Cloud Posse's `context`/`label` namespace/stage/name layer),
  say so in the doc's **Notes for AI Agents** so a consumer does NOT propagate
  that convention to the other (differently-styled) modules in the same project.

1. **Fetch and write the doc.** Use a `terraform-module-reader` agent to read
   the registry page + GitHub README, then write
   `modules/terraform-aws-modules/<name>.md` following
   `modules/module_template.md`:
   - YAML front-matter: `module_name` (normalized: lowercase, hyphens,
     no `terraform-` prefix), `keywords`
   - `## Module Information` section (parsed by `ModuleDocumentParser`)
   - current latest version; inputs/outputs/examples valid for that version
2. **Curate keywords** (10-20): the AWS service name and abbreviation, the
   canonical long form (`application-load-balancer`-style — these carry
   keyword search for full-name queries), core features, common synonyms a
   user would type. Check for collisions: a keyword that dominates another
   module's queries will shift rankings.
3. **Rebuild the index**:

   ```bash
   python src/tfmod_search_cli.py index \
     --docs_dir ./modules/terraform-aws-modules \
     --index_path ./model/tfmod_e5_small_index.pkl
   ```

4. **Verify searchability.** `tests/integration/test_all_modules_searchable.py`
   parametrizes over the corpus — run it and confirm the new module appears
   in its cases and passes (exact name top-1; keyword and natural-language
   top-3). Then the full suite: e2e tests pin the catalog size (search for
   the old count, e.g. `== 54`, in `tests/` and README) — update those
   counts.
5. **Update docs**: README "Indexed Modules" section + module count,
   CHANGELOG entry. Rebuild ships the module inside the wheel automatically
   (force-include of `modules/terraform-aws-modules/`).
