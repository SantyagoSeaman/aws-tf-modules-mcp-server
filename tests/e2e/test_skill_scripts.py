"""
End-to-end tests for helper scripts shipped inside plugin skills.

The tf-troubleshoot skill ships scripts/extract_tf_errors.py — a
deterministic prefilter that reduces terraform logs of any size to just
the diagnostic blocks. These tests run the script as a real subprocess
against a fixture log covering the human-readable block format, the
-json line format, and the bare fallback format.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPT = PROJECT_ROOT / "plugins" / "tfmod-search" / "skills" / "tf-troubleshoot" / "scripts" / "extract_tf_errors.py"
FIXTURE = Path(__file__).parent / "fixtures" / "terraform_apply_errors.log"


def _run(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.mark.e2e
def test_extracts_errors_as_json():
    proc = _run(str(FIXTURE), "--json")
    assert proc.returncode == 0, proc.stderr
    findings = json.loads(proc.stdout)

    # 3 errors: two ╷│╵ blocks, one -json diagnostic line, plus the bare
    # "Error: Process completed..." CI fallback line
    errors = [f for f in findings if f["severity"] == "error"]
    assert len(errors) == 4

    by_summary = {f["summary"]: f for f in errors}

    unsupported = by_summary["Unsupported argument"]
    assert unsupported["file"] == "main.tf"
    assert unsupported["line"] == 42
    assert "web_sg" in unsupported["modules"]
    assert "ingress_with_cidr_blocks" in unsupported["detail"]

    missing = by_summary["Missing required argument"]
    assert missing["file"] == "eks.tf"
    assert "eks" in missing["modules"]

    json_diag = by_summary["Invalid value for variable"]
    assert json_diag["file"] == "eks.tf"
    assert json_diag["line"] == 12
    assert "eks" in json_diag["modules"]


@pytest.mark.e2e
def test_warnings_flag_includes_deprecations():
    proc = _run(str(FIXTURE), "--json", "--warnings")
    assert proc.returncode == 0, proc.stderr
    findings = json.loads(proc.stdout)
    warnings = [f for f in findings if f["severity"] == "warning"]
    assert len(warnings) == 1
    assert warnings[0]["summary"] == "Argument is deprecated"
    assert "db" in warnings[0]["modules"]


@pytest.mark.e2e
def test_text_output_and_stdin():
    log_text = FIXTURE.read_text()
    proc = _run("-", stdin=log_text)
    assert proc.returncode == 0, proc.stderr
    assert "Unsupported argument" in proc.stdout
    assert "main.tf:42" in proc.stdout
    # noise lines from the log must not leak into the output
    assert "Refreshing state" not in proc.stdout
    assert "Initializing the backend" not in proc.stdout


@pytest.mark.e2e
def test_clean_log_produces_no_findings():
    proc = _run("-", stdin="Plan: 3 to add, 0 to change, 0 to destroy.\nApply complete!\n")
    assert proc.returncode == 0
    assert "No terraform diagnostics found" in proc.stdout
