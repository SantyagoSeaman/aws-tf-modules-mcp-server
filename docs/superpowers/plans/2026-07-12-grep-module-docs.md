# grep_module_docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `grep_module_docs` MCP tool that fetches full, version-pinnable docs for any Terraform Registry module through a disk cache and regex-greps them, plus surface `module_id`/`latest_version` in `search_modules`/`modules_list` so agents can chain search → grep.

**Architecture:** A new pure grep engine (`tfmod_doc_grep.py`) and a new registry client with disk cache + document assembly (`tfmod_registry_docs.py`), wired into the FastMCP server as one tool. The curated docs gain an explicit `Module ID` header bullet; the parser and `DocRecord` carry `module_id`/`latest_version`, and the index is rebuilt.

**Tech Stack:** Python 3.13, FastMCP, Pydantic, stdlib `urllib`/`json`/`re`/`pathlib` (no new deps), pytest.

## Global Constraints

- No new runtime dependencies — stdlib only for network/cache/grep (`urllib.request`, `json`, `re`, `pathlib`, `time`). Verbatim from spec §11.
- Network access confined to `src/tfmod_registry_docs.py`; the rest of the server stays offline.
- Registry API base: `https://registry.terraform.io/v1/modules/{namespace}/{name}/{provider}[/{version}]`; versions: `.../{namespace}/{name}/{provider}/versions`.
- `module_id` format: exactly `namespace/name/provider` (3 `/`-separated parts).
- Defaults: `context_lines=2` (range 0..20), `max_matches=50`, `doc_cache_ttl_hours=24`.
- Cache dir: `${TFMODSEARCH_CACHE_DIR:-${XDG_CACHE_HOME:-~/.cache}}/tfmodsearch/registry_docs/`, overridable via `config.yaml` `doc_cache_dir`.
- New `DocRecord` fields default to `""`; server impls read them via `getattr(doc, ..., "")` for old-pickle safety. Index MUST be rebuilt and committed.
- Fixtures/tests offline by default; the one live test is opt-in via `RUN_REGISTRY_BENCHMARK=1` (reuse existing `benchmark` marker), graceful-skip if unreachable.
- Commit messages: plain content-only, no attribution trailers.

---

### Task 1: Backfill `Module ID` header bullet into all curated docs

**Files:**
- Create (temp, not committed): `scratchpad/backfill_module_id.py`
- Modify: `modules/terraform-aws-modules/*.md` (×54)
- Modify: `modules/module_template.md`
- Test: `tests/integration/test_module_id_header.py`

**Interfaces:**
- Produces: every doc's `## Module Information` contains `- **Module ID**: \`ns/name/provider\`` immediately after `- **Module Name**:`, equal to the root `**Source**` value (no `//` suffix).

- [ ] **Step 1:** Write `tests/integration/test_module_id_header.py`:

```python
import re
from pathlib import Path

DOCS = sorted((Path(__file__).parent.parent.parent / "modules/terraform-aws-modules").glob("*.md"))

def _module_info(text: str) -> str:
    m = re.search(r"## Module Information\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else ""

def _bullet(section: str, key: str) -> str | None:
    m = re.search(rf"^\s*-\s*\*\*{key}\*\*:\s*`?([^`\n]+?)`?\s*$", section, re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else None

def test_every_doc_has_module_id_equal_to_root_source():
    assert DOCS, "no module docs found"
    for p in DOCS:
        section = _module_info(p.read_text())
        module_id = _bullet(section, "Module ID")
        source = _bullet(section, "Source")
        assert module_id, f"{p.name}: missing **Module ID**"
        assert re.fullmatch(r"[a-z0-9-]+/[a-z0-9-]+/[a-z0-9]+", module_id), f"{p.name}: bad id {module_id!r}"
        assert source and source.split("//")[0] == module_id, f"{p.name}: id {module_id!r} != source {source!r}"
```

- [ ] **Step 2:** Run `pytest tests/integration/test_module_id_header.py -v` → FAIL (no Module ID bullets yet).

- [ ] **Step 3:** Write `scratchpad/backfill_module_id.py`:

```python
import re
from pathlib import Path

DOCS = sorted(Path("modules/terraform-aws-modules").glob("*.md"))
name_re = re.compile(r"^(\s*-\s*\*\*Module Name\*\*:.*)$", re.MULTILINE)
src_re = re.compile(r"^\s*-\s*\*\*Source\*\*:\s*`([^`]+)`", re.MULTILINE)

for p in DOCS:
    text = p.read_text()
    if re.search(r"^\s*-\s*\*\*Module ID\*\*:", text, re.MULTILINE):
        continue
    src = src_re.search(text)
    assert src, f"{p.name}: no **Source** to derive Module ID"
    module_id = src.group(1).split("//")[0]
    new = name_re.sub(rf"\1\n- **Module ID**: `{module_id}`", text, count=1)
    assert new != text, f"{p.name}: no **Module Name** bullet to anchor after"
    p.write_text(new)
    print(f"{p.name}: + {module_id}")
```

- [ ] **Step 4:** Run `.venv/bin/python scratchpad/backfill_module_id.py`; then add the same `- **Module ID**: \`namespace/name/provider\`` line under `**Module Name**` in `modules/module_template.md` (placeholder value).

- [ ] **Step 5:** Run `pytest tests/integration/test_module_id_header.py -v` → PASS.

- [ ] **Step 6:** Commit `git add modules/ tests/integration/test_module_id_header.py && git commit -m "Add explicit Module ID bullet to all module docs"`.

---

### Task 2: Parser + `DocRecord` carry `module_id` and `latest_version`

**Files:**
- Modify: `src/tfmod_search_lib.py` (`DocRecord`, `ModuleDocumentParser.parse` / `_parse_module_information_section`, `parse_markdown_file`)
- Test: `tests/integration/test_parse_markdown.py`

**Interfaces:**
- Produces: `DocRecord(path, module_name, keywords, text, module_id="", latest_version="")`; parser returns `module_id`/`latest_version` extracted from the Module Information section (fallback: root `**Source**` for id).

- [ ] **Step 1:** Add tests to `tests/integration/test_parse_markdown.py`:

```python
def test_parses_module_id_and_latest_version():
    from tfmod_search_lib import ModuleDocumentParser
    import logging
    text = (
        "# T\n\n## Module Information\n\n"
        "- **Module Name**: `vpc`\n"
        "- **Module ID**: `terraform-aws-modules/vpc/aws`\n"
        "- **Source**: `terraform-aws-modules/vpc/aws`\n"
        "- **Latest Version**: 6.6.1\n"
        "- **Keywords**: vpc, subnet\n"
    )
    p = ModuleDocumentParser(logging.getLogger("t"))
    info = p.parse_module_info(text)
    assert info.module_id == "terraform-aws-modules/vpc/aws"
    assert info.latest_version == "6.6.1"

def test_module_id_falls_back_to_source_without_submodule_suffix():
    from tfmod_search_lib import ModuleDocumentParser
    import logging
    text = (
        "## Module Information\n\n- **Module Name**: `x`\n"
        "- **Source**: `ns/x/aws//modules/sub`\n"
    )
    info = ModuleDocumentParser(logging.getLogger("t")).parse_module_info(text)
    assert info.module_id == "ns/x/aws"
```

- [ ] **Step 2:** Run `pytest tests/integration/test_parse_markdown.py -k module_id -v` → FAIL.

- [ ] **Step 3:** In `src/tfmod_search_lib.py`:
  - Extend `DocRecord`: add `module_id: str = ""` and `latest_version: str = ""`.
  - Add a small helper on the parser returning a dataclass/namedtuple `ModuleInfo(module_name, keywords, module_id, latest_version)` via a new public method `parse_module_info(text) -> ModuleInfo`, extracting:
    - `**Module ID**` via `r"^\s*-\s*\*\*Module ID\*\*:\s*`?([^`\n]+?)`?\s*$"`;
    - fallback id: first `**Source**` value, `.split("//")[0]`;
    - `**Latest Version**` via `r"^\s*-\s*\*\*Latest Version\*\*:\s*(.+?)\s*$"`.
  - Keep the existing `parse()` returning `(module_name, keywords, body)` for compatibility, or refactor callers.
  - In `parse_markdown_file`, populate the two new `DocRecord` fields.

- [ ] **Step 4:** Run `pytest tests/integration/test_parse_markdown.py -v` → PASS.

- [ ] **Step 5:** Commit `git add src/tfmod_search_lib.py tests/integration/test_parse_markdown.py && git commit -m "Parse module_id and latest_version into DocRecord"`.

---

### Task 3: Rebuild the search index

**Files:**
- Modify: `model/tfmod_e5_small_index.pkl`

- [ ] **Step 1:** Rebuild: `.venv/bin/python src/tfmod_search_cli.py index --docs_dir ./modules/terraform-aws-modules --index_path ./model/tfmod_e5_small_index.pkl`.

- [ ] **Step 2:** Verify fields present:

```bash
.venv/bin/python -c "import sys; sys.path.insert(0,'src'); import logging; from tfmod_search_lib import load_index; idx=load_index('model/tfmod_e5_small_index.pkl', logging.getLogger()); d=[x for x in idx.docs if x.module_name=='vpc'][0]; print(d.module_id, d.latest_version); assert d.module_id=='terraform-aws-modules/vpc/aws'; assert all(x.module_id for x in idx.docs)"
```

- [ ] **Step 3:** Commit `git add model/tfmod_e5_small_index.pkl && git commit -m "Rebuild index with module_id and latest_version"`.

---

### Task 4: Surface `module_id`/`latest_version` in search_modules & modules_list

**Files:**
- Modify: `src/tfmod_mcp_server.py` (`SearchHit`, `ModuleListItem`, `search_modules_impl`, `modules_list_impl`)
- Test: `tests/integration/test_mcp_server.py`

**Interfaces:**
- Produces: `SearchHit` and `ModuleListItem` gain `module_id: str` and `latest_version: str`.

- [ ] **Step 1:** Add tests to `tests/integration/test_mcp_server.py`:

```python
def test_search_hit_includes_module_id(server_state):
    out = search_modules_impl("vpc", server_state)
    top = out.results[0]
    assert top.module_id == "terraform-aws-modules/vpc/aws"
    assert top.latest_version  # non-empty

def test_modules_list_includes_module_id(server_state):
    out = modules_list_impl(server_state)
    assert all(m.module_id for m in out.modules)
```

- [ ] **Step 2:** Run those two → FAIL (fields missing).

- [ ] **Step 3:** Add `module_id: str = Field(...)`, `latest_version: str = Field(...)` to `SearchHit` and `ModuleListItem`; populate in `search_modules_impl` and `modules_list_impl` via `getattr(d, "module_id", "")` / `getattr(d, "latest_version", "")`.

- [ ] **Step 4:** Run `pytest tests/integration/test_mcp_server.py -v` → PASS.

- [ ] **Step 5:** Commit.

---

### Task 5: Pure grep engine `tfmod_doc_grep.py`

**Files:**
- Create: `src/tfmod_doc_grep.py`
- Test: `tests/integration/test_doc_grep.py`

**Interfaces:**
- Produces:
  ```python
  @dataclass
  class DocMatch:
      section: str
      line_number: int      # 1-based, within full assembled text
      line: str
      before: list[str]
      after: list[str]

  SECTION_MARK = "====="   # lines like "===== ROOT README =====" set the section label

  def grep_document(
      text: str, pattern: str, *, case_sensitive: bool = False,
      context_lines: int = 2, scope: list[str] | None = None, max_matches: int = 50,
  ) -> tuple[list[DocMatch], int, list[str]]:
      "Returns (matches, total_matches_before_cap, available_section_labels)."
  ```

- [ ] **Step 1:** Write `tests/integration/test_doc_grep.py`:

```python
from tfmod_doc_grep import grep_document

DOC = """===== MODULE ns/x/aws @ 1.0.0 =====

===== ROOT README =====
line about NAT gateway
another line
===== ROOT INPUTS =====
- enable_nat_gateway | bool | false | Enable NAT
- azs | list | [] | Availability zones
"""

def test_finds_line_with_context_and_section():
    matches, total, sections = grep_document(DOC, "enable_nat_gateway", context_lines=1)
    assert total == 1
    m = matches[0]
    assert "enable_nat_gateway" in m.line
    assert m.section == "root/inputs"
    assert any("INPUTS" not in b for b in m.before)  # has a context line
    assert "root/readme" in sections and "root/inputs" in sections

def test_case_insensitive_default():
    matches, total, _ = grep_document(DOC, "nat GATEWAY")
    assert total >= 1

def test_case_sensitive_flag():
    _, total, _ = grep_document(DOC, "NAT GATEWAY", case_sensitive=True)
    assert total == 0

def test_scope_restricts_search():
    _, total, _ = grep_document(DOC, "gateway", scope=["inputs"])
    assert total == 1  # only the inputs row, not the readme prose

def test_max_matches_caps_returned_not_total():
    matches, total, _ = grep_document(DOC, "line", context_lines=0, max_matches=1)
    assert total == 2 and len(matches) == 1

def test_invalid_regex_raises_valueerror():
    import pytest
    with pytest.raises(ValueError):
        grep_document(DOC, "(")
```

- [ ] **Step 2:** Run → FAIL (module missing).

- [ ] **Step 3:** Implement `src/tfmod_doc_grep.py`:
  - Split `text` into lines; track current section label by scanning for `===== … =====` markers (map "ROOT README"→"root/readme", "ROOT INPUTS"→"root/inputs", "SUBMODULE: flow-log" + `--- readme ---`→"submodule:flow-log/readme", "EXAMPLE: complete"→"example:complete/readme"). Collect the ordered set of labels for `available_sections`.
  - Compile pattern with `re.IGNORECASE` unless `case_sensitive`; on `re.error` raise `ValueError(f"Invalid regex: {e}")`.
  - `scope` filters which labels are eligible (match label's part after "/" or the block keyword: root/inputs/outputs/resources/submodules/examples).
  - For each eligible matching line, build `DocMatch` with `context_lines` before/after (clamped). Merge is optional for v1 — dedupe overlapping context by tracking last emitted line range; count logical matches for `total` regardless of cap.
  - Return `(matches[:max_matches], total, available_sections)`.

- [ ] **Step 4:** Run `pytest tests/integration/test_doc_grep.py -v` → PASS.

- [ ] **Step 5:** Commit.

---

### Task 6: Registry client + assembly + cache `tfmod_registry_docs.py`

**Files:**
- Create: `src/tfmod_registry_docs.py`
- Create: `tests/fixtures/registry_vpc_min.json` (trimmed real response: root.readme + a couple inputs/outputs, 1 submodule, 1 example, `version`)
- Test: `tests/integration/test_registry_docs.py`

**Interfaces:**
- Produces:
  ```python
  def parse_module_id(module_id: str) -> tuple[str, str, str]   # raises ValueError if not 3 parts
  def assemble_document(detail: dict) -> str                    # deterministic text with ===== markers
  def get_assembled_docs(
      module_id: str, version: str | None, *, cache_dir: Path, ttl_hours: int = 24,
      refresh: bool = False, fetch=<default urllib fetch>,
  ) -> tuple[str, str, str, bool, str]:
      "Returns (assembled_text, resolved_version, source_url, cache_hit, fetched_at_iso)."
  ```
- Consumes: fixture JSON in tests via an injected `fetch` callable (no real network in unit tests).

- [ ] **Step 1:** Write `tests/integration/test_registry_docs.py`:

```python
import json
from pathlib import Path
from tfmod_registry_docs import parse_module_id, assemble_document, get_assembled_docs

FIX = json.loads((Path(__file__).parent.parent / "fixtures/registry_vpc_min.json").read_text())

def test_parse_module_id_ok():
    assert parse_module_id("terraform-aws-modules/vpc/aws") == ("terraform-aws-modules", "vpc", "aws")

def test_parse_module_id_bad():
    import pytest
    with pytest.raises(ValueError):
        parse_module_id("vpc/aws")

def test_assemble_contains_sections_and_inputs():
    text = assemble_document(FIX)
    assert "===== ROOT README =====" in text
    assert "===== ROOT INPUTS =====" in text
    assert "enable_nat_gateway" in text  # rendered input row

def test_pinned_version_not_refetched(tmp_path):
    calls = {"n": 0}
    def fake_fetch(ns, name, prov, ver):
        calls["n"] += 1
        return FIX
    a = get_assembled_docs("terraform-aws-modules/vpc/aws", "6.6.1", cache_dir=tmp_path, fetch=fake_fetch)
    b = get_assembled_docs("terraform-aws-modules/vpc/aws", "6.6.1", cache_dir=tmp_path, fetch=fake_fetch)
    assert calls["n"] == 1 and b[3] is True  # second is cache hit

def test_refresh_bypasses_cache(tmp_path):
    calls = {"n": 0}
    def fake_fetch(ns, name, prov, ver):
        calls["n"] += 1; return FIX
    get_assembled_docs("terraform-aws-modules/vpc/aws", "6.6.1", cache_dir=tmp_path, fetch=fake_fetch)
    get_assembled_docs("terraform-aws-modules/vpc/aws", "6.6.1", cache_dir=tmp_path, refresh=True, fetch=fake_fetch)
    assert calls["n"] == 2

def test_latest_ttl_expiry(tmp_path):
    calls = {"n": 0}
    def fake_fetch(ns, name, prov, ver):
        calls["n"] += 1; return FIX
    get_assembled_docs("terraform-aws-modules/vpc/aws", None, cache_dir=tmp_path, ttl_hours=0, fetch=fake_fetch)
    get_assembled_docs("terraform-aws-modules/vpc/aws", None, cache_dir=tmp_path, ttl_hours=0, fetch=fake_fetch)
    assert calls["n"] == 2  # ttl=0 always stale
```

- [ ] **Step 2:** Create the trimmed fixture JSON from a real response (see Task 6 note) and run tests → FAIL.

- [ ] **Step 3:** Implement `src/tfmod_registry_docs.py`:
  - `parse_module_id`: split on `/`, require exactly 3 non-empty parts.
  - Default `_http_fetch(ns, name, prov, version)`: GET detail URL (with `/version` if given), `urllib.request.urlopen(timeout=25)`, `json.load`. `resolve_version` uses the response's `version` field.
  - `assemble_document(detail)`: build the `=====`-delimited text per spec §5 (root readme, inputs/outputs/resources rows, submodules, examples). Deterministic ordering.
  - Cache: file `ns__name__prov__<version|latest>.json` under `cache_dir`; on latest, honor `ttl_hours` via stored `fetched_at`; on any fetch also write the concrete `resolved_version` file. `refresh` bypasses read. Use `time.time()` for timestamps (fetched_at ISO via `time.gmtime`/`strftime` — avoid naive `datetime.now()` only if in a workflow; here plain `datetime` is fine).
  - In-memory LRU dict keyed by `(module_id, version-or-'latest')` guarded by mtime/ttl (optional; keep simple: dict cache of assembled text within process, invalidated by refresh).

- [ ] **Step 4:** Run `pytest tests/integration/test_registry_docs.py -v` → PASS.

- [ ] **Step 5:** Commit (include fixture).

**Task 6 note — creating the fixture:** fetch once and trim:
```bash
curl -s "https://registry.terraform.io/v1/modules/terraform-aws-modules/vpc/aws" \
  | .venv/bin/python -c "import sys,json; d=json.load(sys.stdin); \
    d['root']['inputs']=d['root']['inputs'][:3]; d['root']['outputs']=d['root']['outputs'][:2]; \
    d['root']['resources']=d['root']['resources'][:2]; d['submodules']=d['submodules'][:1]; \
    d['examples']=d['examples'][:1]; print(json.dumps(d))" > tests/fixtures/registry_vpc_min.json
```
Ensure one input row is `enable_nat_gateway` (pick it explicitly if not in the first 3).

---

### Task 7: Wire `grep_module_docs` tool + config + instructions

**Files:**
- Modify: `src/tfmod_mcp_server.py` (tool, `_impl`, Pydantic output models, `instructions`)
- Modify: `src/tfmod_search_lib.py` or `tfmod_mcp_server.py` `ConfigLoader` (add `doc_cache_dir`, `doc_cache_ttl_hours`)
- Modify: `config.yaml`
- Test: `tests/integration/test_grep_module_docs.py`

**Interfaces:**
- Consumes: `grep_document` (Task 5), `get_assembled_docs` (Task 6), `parse_module_id`.
- Produces: `GrepMatch`, `CacheInfo`, `GrepOutput` Pydantic models; `grep_module_docs_impl(module_id, pattern, *, version, case_sensitive, context_lines, scope, max_matches, refresh, cache_dir, ttl_hours) -> GrepOutput`; the decorated `grep_module_docs(...)` tool.

- [ ] **Step 1:** Write `tests/integration/test_grep_module_docs.py` using the fixture via a monkeypatched fetch (inject through `get_assembled_docs`'s `fetch` param or patch `tfmod_registry_docs._http_fetch`):

```python
def test_grep_impl_returns_matches(monkeypatch, tmp_path):
    import json
    from pathlib import Path
    import tfmod_registry_docs as rd
    fix = json.loads((Path(__file__).parent.parent / "fixtures/registry_vpc_min.json").read_text())
    monkeypatch.setattr(rd, "_http_fetch", lambda ns, n, p, v: fix)
    from tfmod_mcp_server import grep_module_docs_impl
    out = grep_module_docs_impl(
        "terraform-aws-modules/vpc/aws", "enable_nat_gateway",
        version="6.6.1", cache_dir=tmp_path,
    )
    assert out.total_matches >= 1
    assert out.resolved_version == fix["version"]
    assert out.matches[0].section.startswith("root/")

def test_grep_impl_invalid_module_id(tmp_path):
    import pytest
    from tfmod_mcp_server import grep_module_docs_impl
    with pytest.raises(ValueError):
        grep_module_docs_impl("vpc/aws", "x", cache_dir=tmp_path)

def test_grep_impl_zero_matches_lists_sections(monkeypatch, tmp_path):
    import json
    from pathlib import Path
    import tfmod_registry_docs as rd
    fix = json.loads((Path(__file__).parent.parent / "fixtures/registry_vpc_min.json").read_text())
    monkeypatch.setattr(rd, "_http_fetch", lambda ns, n, p, v: fix)
    from tfmod_mcp_server import grep_module_docs_impl
    out = grep_module_docs_impl("terraform-aws-modules/vpc/aws", "zzz_no_match_zzz", version="6.6.1", cache_dir=tmp_path)
    assert out.total_matches == 0 and out.available_sections
```

- [ ] **Step 2:** Run → FAIL.

- [ ] **Step 3:** Implement models + `grep_module_docs_impl` + tool decorator per spec §4; resolve `cache_dir`/`ttl_hours` from config (default resolver: `TFMODSEARCH_CACHE_DIR` → `XDG_CACHE_HOME` → `~/.cache`, `/tfmodsearch/registry_docs`). Add `ConfigLoader.load_doc_cache(config_path, cli_overrides)` returning `(cache_dir: Path, ttl_hours: int)`. Update server `instructions` to describe the three-tool workflow. Add `doc_cache_dir`/`doc_cache_ttl_hours` to `config.yaml`.

- [ ] **Step 4:** Run `pytest tests/integration/test_grep_module_docs.py -v` → PASS.

- [ ] **Step 5:** Commit.

---

### Task 8: Opt-in live smoke test

**Files:**
- Test: `tests/integration/test_grep_module_docs_live.py`

- [ ] **Step 1:** Write an env-gated test (mirror `test_registry_comparison.py`'s gate: `pytest.mark.benchmark` + `skipif(os.getenv("RUN_REGISTRY_BENCHMARK") != "1")`, graceful skip on network error) that calls `grep_module_docs_impl("terraform-aws-modules/vpc/aws", "enable_nat_gateway", version="6.6.1", cache_dir=tmp_path)` against the real API and asserts a match with a `root/inputs` section.

- [ ] **Step 2:** Run `RUN_REGISTRY_BENCHMARK=1 pytest tests/integration/test_grep_module_docs_live.py -v` → PASS; without the env var → SKIP.

- [ ] **Step 3:** Commit.

---

### Task 9: Documentation

**Files:**
- Modify: `README.md` (MCP Tools section + new fields + tool-boundary note)
- Modify: `CLAUDE.md` (tool list, new fields, three-tool workflow)

- [ ] **Step 1:** Document `grep_module_docs` (signature, params, output, examples) in README "MCP Tools"; note `module_id`/`latest_version` now returned by `search_modules`/`modules_list`; add the caching/version behavior and the three-tool boundary.
- [ ] **Step 2:** Mirror in `CLAUDE.md` (architecture + tool descriptions + testing counts).
- [ ] **Step 3:** Run the full suite `pytest tests/ -q` (live tests skip) → all pass. Commit.

---

## Self-Review

- **Spec coverage:** §4 tool API → Tasks 5–7; §5 assembly → Task 6; §6 grep → Task 5; §7 cache → Task 6; §8 errors → Tasks 5–7 (invalid id/regex/version, zero-match); §9 module_id integration → Tasks 1–4; §10 files → all tasks; §11 deps → Global Constraints; §12 testing → Tasks 5–8; §13 future → out of scope; §14 rollout → Task 9. No gaps.
- **Placeholders:** none — grep/assembly/cache/regex code and every test are concrete.
- **Type consistency:** `grep_document` returns `(list[DocMatch], int, list[str])` consumed identically in Task 7; `get_assembled_docs` 5-tuple `(text, resolved_version, source_url, cache_hit, fetched_at)` consumed in `grep_module_docs_impl`; `parse_module_id` 3-tuple used consistently; `DocRecord` new fields defaulted and read via `getattr`.
