"""Corpus completeness guard.

Fails if any collapsed/opaque-typed input row is neither expanded (its shape
named in the Description or the Type cell) nor listed in the reviewed allowlist.
Keeps the completeness pass from silently regressing: a new module or edit must
either name its composite inputs' shapes or add a reasoned allowlist entry.
Offline -- operates on the local module docs only.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import lint_doc_completeness as lint  # noqa: E402 -- sys.path must be set up first

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "modules/terraform-aws-modules"
ALLOWLIST = ROOT / "tests/fixtures/doc_completeness_allowlist.txt"


def _allowlist() -> set[str]:
    out: set[str] = set()
    for line in ALLOWLIST.read_text().splitlines():
        entry = line.split("#", 1)[0].strip()
        if entry:
            out.add(entry)
    return out


def test_no_unlisted_opaque_rows() -> None:
    unresolved = lint.check_corpus(str(DOCS), _allowlist())
    assert unresolved == [], f"opaque input rows not expanded and not allowlisted: {unresolved}"


def test_allowlist_has_no_stale_entries() -> None:
    flagged = set(lint.check_corpus(str(DOCS), set()))
    stale = _allowlist() - flagged
    assert stale == set(), f"allowlist entries that are no longer flagged (remove them): {stale}"
