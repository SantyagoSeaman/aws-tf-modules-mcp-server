#!/usr/bin/env python3
"""
Extract error/warning diagnostics from Terraform output logs.

Terraform plan/apply logs on real projects run to thousands of lines; the
diagnostics an agent actually needs are a handful of delimited blocks.
This script reduces a log of any size to just those blocks, so no LLM has
to read the raw log.

Supported input formats (auto-detected per line):
- Human-readable output: diagnostic blocks delimited by U+2577 / U+2575
  box-drawing characters, i.e. lines between a lone "╷" and a lone "╵"
  containing "Error:" or "Warning:".
- Machine-readable output (terraform ... -json): one JSON object per line
  with "@level" of "error" or "warning" and an optional "diagnostic" object.
- Fallback: bare lines starting with "Error:" / "Warning:" (older Terraform
  or wrapped CI output), captured with a few lines of trailing context.

Usage:
    extract_tf_errors.py <logfile> [--json] [--warnings]
    terraform apply 2>&1 | extract_tf_errors.py - [--json]

Options:
    --json      Emit findings as a JSON array instead of text blocks.
    --warnings  Include warnings (default: errors only).

Output (text mode): one block per finding with severity, summary, the
file/line/module address when present, and the full diagnostic text.
Exit code: 0 if the log parsed (even with zero findings), 2 on bad usage.
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field

BLOCK_START = "╷"  # ╷
BLOCK_END = "╵"  # ╵
PIPE = "│"  # │

SEVERITY_RE = re.compile(r"^(Error|Warning):\s*(.*)")
LOCATION_RE = re.compile(r"^\s*on (\S+) line (\d+)(?:, in (.+?))?:?\s*$")
MODULE_ADDR_RE = re.compile(r'module\s+"([^"]+)"')
FALLBACK_CONTEXT_LINES = 4


@dataclass
class Finding:
    severity: str
    summary: str
    file: str | None = None
    line: int | None = None
    address: str | None = None
    modules: list[str] = field(default_factory=list)
    detail: str = ""


def _strip_pipe(line: str) -> str:
    stripped = line.lstrip()
    if stripped.startswith(PIPE):
        stripped = stripped[1:]
    return stripped.strip()


def _parse_block(lines: list[str]) -> Finding | None:
    """Parse one ╷…╵ block into a Finding, or None if it has no severity."""
    severity = None
    summary = ""
    file = None
    line_no = None
    address = None
    modules: list[str] = []
    detail_lines: list[str] = []

    for raw in lines:
        text = _strip_pipe(raw)
        detail_lines.append(text)

        sev_match = SEVERITY_RE.match(text)
        if sev_match and severity is None:
            severity = sev_match.group(1).lower()
            summary = sev_match.group(2).strip()
            continue

        loc_match = LOCATION_RE.match(text)
        if loc_match and file is None:
            file = loc_match.group(1)
            line_no = int(loc_match.group(2))
            address = (loc_match.group(3) or "").strip() or None

        modules.extend(m for m in MODULE_ADDR_RE.findall(text) if m not in modules)

    if severity is None:
        return None
    return Finding(
        severity=severity,
        summary=summary,
        file=file,
        line=line_no,
        address=address,
        modules=modules,
        detail="\n".join(detail_lines).strip(),
    )


def _parse_json_line(raw: str) -> Finding | None:
    """Parse one line of `terraform -json` output."""
    try:
        obj = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(obj, dict):
        return None
    level = obj.get("@level")
    if level not in ("error", "warning"):
        return None

    diag = obj.get("diagnostic") or {}
    rng = diag.get("range") or {}
    address = diag.get("address")
    summary = diag.get("summary") or obj.get("@message", "")
    detail = diag.get("detail") or ""
    modules = MODULE_ADDR_RE.findall(detail)
    if address:
        # address like "module.vpc.aws_subnet.private" carries the module name
        addr_modules = re.findall(r"module\.([\w-]+)", str(address))
        modules.extend(m for m in addr_modules if m not in modules)

    return Finding(
        severity=level,
        summary=summary,
        file=rng.get("filename"),
        line=(rng.get("start") or {}).get("line"),
        address=address,
        modules=modules,
        detail=detail or summary,
    )


def extract(stream, include_warnings: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    block: list[str] | None = None
    fallback: list[str] | None = None
    fallback_remaining = 0

    for raw in stream:
        line = raw.rstrip("\n")
        stripped = line.strip()

        # JSON log lines are self-contained
        if stripped.startswith("{"):
            finding = _parse_json_line(stripped)
            if finding:
                findings.append(finding)
            continue

        # Delimited human-readable blocks
        if stripped == BLOCK_START:
            block = []
            continue
        if stripped == BLOCK_END and block is not None:
            finding = _parse_block(block)
            if finding:
                findings.append(finding)
            block = None
            continue
        if block is not None:
            block.append(line)
            continue

        # Fallback: bare Error:/Warning: lines outside any block
        if fallback is not None:
            fallback.append(line)
            fallback_remaining -= 1
            if fallback_remaining <= 0:
                finding = _parse_block(fallback)
                if finding:
                    findings.append(finding)
                fallback = None
            continue
        if SEVERITY_RE.match(stripped):
            fallback = [line]
            fallback_remaining = FALLBACK_CONTEXT_LINES

    # Flush unterminated trailing state
    for pending in (block, fallback):
        if pending:
            finding = _parse_block(pending)
            if finding:
                findings.append(finding)

    if not include_warnings:
        findings = [f for f in findings if f.severity == "error"]
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Terraform diagnostics from a log of any size.")
    parser.add_argument("logfile", help="Path to the log file, or '-' for stdin")
    parser.add_argument("--json", action="store_true", help="Emit findings as JSON")
    parser.add_argument("--warnings", action="store_true", help="Include warnings, not just errors")
    args = parser.parse_args()

    if args.logfile == "-":
        findings = extract(sys.stdin, include_warnings=args.warnings)
    else:
        try:
            with open(args.logfile, encoding="utf-8", errors="replace") as stream:
                findings = extract(stream, include_warnings=args.warnings)
        except OSError as e:
            print(f"Cannot read {args.logfile}: {e}", file=sys.stderr)
            return 2

    if args.json:
        print(json.dumps([asdict(finding) for finding in findings], indent=2))
        return 0

    if not findings:
        print("No terraform diagnostics found in the log.")
        return 0

    print(f"{len(findings)} finding(s):\n")
    for i, finding in enumerate(findings, 1):
        location = f" ({finding.file}:{finding.line})" if finding.file else ""
        addr = f" in {finding.address}" if finding.address else ""
        mods = f" [modules: {', '.join(finding.modules)}]" if finding.modules else ""
        print(f"--- {i}. {finding.severity.upper()}: {finding.summary}{location}{addr}{mods}")
        print(finding.detail)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
