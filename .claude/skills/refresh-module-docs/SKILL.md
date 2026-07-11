---
name: refresh-module-docs
description: Maintainer skill for this repository — refresh all module docs in modules/terraform-aws-modules/ from current upstream sources, rebuild the search index, verify searchability, and prepare a release. Use when the catalog is stale (module versions moved upstream) or the user asks to update the module documentation.
---

# Refresh the module documentation catalog

This codifies the pipeline used for the 0.3.0 release (54 docs refreshed via
multi-agent workflows). Budget: roughly one agent per module.

## Pipeline

1. **Pilot first.** Refresh 5-10 representative modules (mix of large: vpc,
   eks, rds; and small: sns, vpn-gateway) and review the diffs before
   committing to the full run.
2. **Per module**: spawn a `terraform-module-reader` agent (or a Workflow
   pipeline over all modules) that fetches the module's current Terraform
   Registry page + GitHub README and rewrites the doc following
   `modules/module_template.md`. Non-negotiables per doc:
   - YAML front-matter: `module_name`, `keywords` (10-20 terms, keep
     canonical service names like `application-load-balancer`,
     `relational-database` — they carry keyword search)
   - current latest version stated; variable names/defaults/examples valid
     for that version — this is the whole point of the refresh
   - `## Module Information` section parseable by
     `ModuleDocumentParser` (src/tfmod_search_lib.py)
3. **Rebuild the index** (the production index is git-tracked):

   ```bash
   python src/tfmod_search_cli.py index \
     --docs_dir ./modules/terraform-aws-modules \
     --index_path ./model/tfmod_e5_small_index.pkl
   ```

4. **Run the suite**, searchability first:

   ```bash
   pytest tests/integration/test_all_modules_searchable.py -q && pytest tests/ -q
   ```

   Leaner docs shift BGE embeddings and can flip keyword-ranking tests.
   Fix corpus-side (add a canonical keyword to the affected module), never by
   re-tuning weights: an exhaustive 864-combo grid search (2026-07) proved
   weight changes cannot fix ranking regressions the corpus causes. Watch
   for keyword edits breaking the module's natural-language test in return —
   re-run both.
5. **Release**: bump version in `pyproject.toml` AND both plugin manifests
   (`plugins/tfmod-search/.claude-plugin/plugin.json`,
   `.codex-plugin/plugin.json` — e2e tests assert they match), add a
   CHANGELOG entry, single plain commit (no attribution trailers), tag
   `vX.Y.Z`, push after explicit approval — the tag push publishes to PyPI —
   then `gh release create --verify-tag` with notes from the CHANGELOG.
