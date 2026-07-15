import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import lint_doc_completeness as lint


def _tbl(rows):
    head = "### Main Input Variables\n\n| Variable | Type | Default | Description |\n|---|---|---|---|\n"
    return head + "".join(rows)


def test_flags_opaque_row_without_hint():
    md = _tbl(["| `metadata_options` | `object` | `{}` | IMDS options; IMDSv2 required by default |\n"])
    flags = lint.find_opaque_rows(md)
    assert [f.variable for f in flags] == ["metadata_options"]


def test_does_not_flag_when_description_names_a_field():
    md = _tbl(["| `subscriptions` | `map(object)` | `{}` | each sets `protocol`, `endpoint` |\n"])
    assert lint.find_opaque_rows(md) == []


def test_does_not_flag_type_already_expanded():
    md = _tbl(["| `timeouts` | `object({create,delete})` | `{}` | timeout overrides |\n"])
    assert lint.find_opaque_rows(md) == []


def test_top_level_fields_from_object():
    t = 'object({\n  http_endpoint = optional(string, "enabled")\n  http_tokens = optional(string)\n})'
    assert lint.top_level_fields(t) == ["http_endpoint", "http_tokens"]


def test_top_level_fields_from_map_object():
    t = "map(object({\n  encrypted = optional(bool)\n  size = optional(number)\n}))"
    assert lint.top_level_fields(t) == ["encrypted", "size"]


def test_top_level_fields_empty_for_any():
    assert lint.top_level_fields("any") == []


def test_roster_capped():
    r = lint.roster([f"f{i}" for i in range(12)], cap=8)
    assert "f0" in r and "f7" in r and "f8" not in r
    assert "grep_module_docs" in r


def test_check_corpus_honors_allowlist(tmp_path):
    d = tmp_path / "modules"
    d.mkdir()
    (d / "x.md").write_text(_tbl(["| `foo` | `any` | `{}` | freeform passthrough |\n"]))
    assert lint.check_corpus(str(d), set()) == ["x.md::foo"]
    assert lint.check_corpus(str(d), {"x.md::foo"}) == []
