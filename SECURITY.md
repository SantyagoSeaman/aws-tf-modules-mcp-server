# Security Policy

## Supported Versions

Only the latest published minor release receives security fixes.

| Version | Supported |
| ------- | --------- |
| 0.9.x   | ✅        |
| < 0.9   | ❌        |

## Reporting a Vulnerability

Please report suspected vulnerabilities privately — do **not** open a public issue.

- **Preferred:** use GitHub's [Private Vulnerability Reporting](https://github.com/SantyagoSeaman/tfmodsearch/security/advisories/new) ("Report a vulnerability" on the repository's Security tab).
- **Fallback:** email makeev.alex@gmail.com.

You can expect an acknowledgement within a few days. This is a volunteer-maintained
open-source project, so fixes are best-effort; we will keep you informed of progress
and coordinate disclosure once a fix is available.

## Scope

`tfmodsearch` runs locally and is offline by design, with one exception:
`src/tfmod_registry_docs.py` makes outbound HTTPS requests to the public
Terraform Registry API (`registry.terraform.io`) for the `grep_module_docs`
tool. Reports concerning that network path, the registry documentation cache,
or the `get_module` path-traversal guards are especially welcome.
