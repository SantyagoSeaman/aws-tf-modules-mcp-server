# Security Policy

## Supported Versions

Only the **latest published minor release** (see [Releases](https://github.com/SantyagoSeaman/tfmodsearch/releases)) receives security fixes; all older versions are unsupported.

## Reporting a Vulnerability

Please report suspected vulnerabilities privately — do **not** open a public issue.

Use GitHub's [Private Vulnerability Reporting](https://github.com/SantyagoSeaman/tfmodsearch/security/advisories/new) ("Report a vulnerability" on the repository's Security tab).

You can expect an acknowledgement within a few days. This is a volunteer-maintained
open-source project, so fixes are best-effort; we will keep you informed of progress
and coordinate disclosure once a fix is available.

## Scope

`tfmodsearch` has no networked tools — `search_modules`, `get_module`, and
`modules_list` are fully offline, served from the local pre-built index and
committed per-module artifacts. The one exception is a background thread,
default-on in HTTP transport mode (opt-out via `TFMODSEARCH_UPDATE_CHECK=0`),
that checks the public PyPI JSON API (`pypi.org`) once a day for a newer
release. Reports concerning that network path or the `get_module`
path-traversal guards are especially welcome.
