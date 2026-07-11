---
name: tf-troubleshoot
description: Use when terraform plan, apply, init, or validate fails — an error in Terraform output, a CI log, or a pasted error message mentioning a module or variable. Extracts the diagnostics from logs of any size and diagnoses them against current module documentation with exact fixes.
---

# Diagnose a Terraform failure

Terraform logs run to thousands of lines; the diagnostics are a handful of
delimited blocks. Never read a large log directly — extract first.

## Workflow

1. **Get the log.** A file path, CI output saved to a file, or the pasted
   error. If the user has only a terminal scrollback, ask them to save it to
   a file (or re-run piped to one).
2. **Prefilter.** Run the bundled script (it lives next to this skill):

   ```bash
   python3 scripts/extract_tf_errors.py <logfile> --json --warnings
   ```

   It reduces any log to structured findings (severity, summary, file:line,
   module addresses, detail) and handles human-readable blocks, `-json`
   output, and bare CI error lines. For a short pasted error (a screenful),
   skip the script and work directly.
3. **Analyze in isolation.** On Claude Code, launch the `tf-log-analyst`
   agent with the log path and the script path — it verifies each finding
   against current docs and returns a compact report; relay it. Where
   subagents are unavailable, analyze the extracted findings inline:
   for every finding naming a terraform-aws-modules module, `get_module`
   and check the failing variable against the documented inputs — renamed,
   removed, type mismatch, missing required, or deprecated.
4. **Non-module failures** (provider auth, state locks, quotas) — say so
   and diagnose from the error text; do not force a module explanation.
5. **Report per finding**: root cause (verified against the doc where
   possible, marked as inferred otherwise), the exact fix with current
   variable names, and what to run to confirm (`terraform validate`,
   re-plan). Apply fixes only on user approval.
