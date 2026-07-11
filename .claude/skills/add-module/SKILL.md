---
name: add-module
description: Maintainer skill for this repository — onboard a new Terraform module into the search catalog from a Terraform Registry URL or module address. Writes the doc, curates keywords, rebuilds the index, and verifies the module is searchable.
---

# Add a module to the catalog

Input: a Terraform Registry URL (or `namespace/name/provider` address).

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
