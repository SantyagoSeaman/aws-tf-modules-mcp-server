# 0.20.0 Orientation Quick Wins Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship three server-only output-shaping wins — combined-heading section over-fetch fix, inline compact root inputs in the default orientation head, and broaden the grep hint to shapes/types — as 0.20.0, with the index and corpus untouched.

**Architecture:** All logic lives in `src/tfmod_mcp_server.py`. Change 1 adds an H3 sub-section extractor and two keyword-only params (`interface_scope`, `silent_keys`) to `filter_module_sections`. Change 2 wires the head to inline root inputs best-effort. Change 3 is wording only. Tests extend `tests/integration/test_mcp_server.py`.

**Tech Stack:** Python 3.12+, FastMCP, pytest.

## Global Constraints

- Index pickle and `modules/**` docs MUST NOT change (embedding drift breaks the golden set).
- No new dependency, no network in these code paths.
- `sections=["all"|"full"|"everything"]` MUST still return the complete document verbatim.
- Core sections (Description, Module Information, Notes for AI Agents, Important Gotchas) plus front-matter remain always-included.
- Split-toplevel interface docs (e.g. autoscaling, redshift) MUST be byte-identical for `sections=['inputs']` before and after (their exact alias already resolved; the fallback never fired).
- Commit messages: plain content-only, no attribution trailers, NO apostrophes/contractions.
- Run `pytest tests/integration/test_mcp_server.py -q` after each task; run full `pytest tests/ -q` before the version bump.

---

### Task 1: H3 sub-section extractor for combined bundles

**Files:**
- Modify: `src/tfmod_mcp_server.py` (add helper near `_split_h2_sections`, ~line 970; add an interface-key→H3-prefix map near `_SECTION_ALIASES`, ~line 862)
- Test: `tests/integration/test_mcp_server.py`

**Interfaces:**
- Consumes: nothing new.
- Produces:
  - `_INTERFACE_H3_PREFIXES: dict[str, tuple[str, ...]]` mapping each interface key to the lowercase H3-title prefixes it matches: `{"inputs": ("main input variables",), "variables": ("main input variables",), "outputs": ("main output",), "examples": ("usage example",), "usage": ("usage example",)}`.
- `_extract_interface_h3(block: str, keys: set[str]) -> str` — given one combined H2 bundle `block` (heading line + body) and a set of interface keys, return the bundle's H2 heading line followed by only the H3 sub-sections whose lowercased title starts with any prefix for those keys; return `""` if none match. An H3 sub-block runs from its `### ` line to the next `^### ` or `^## ` or end of block.

- [ ] **Step 1: Write the failing test**

Add to `tests/integration/test_mcp_server.py`:

```python
from tfmod_mcp_server import _extract_interface_h3


def test_extract_interface_h3_inputs_only():
    block = (
        "## Root Module: S3 Bucket\n\n"
        "### Description\n\nThe root module.\n\n"
        "### Main Input Variables\n\n| Variable | Type |\n|---|---|\n| `bucket` | `string` |\n\n"
        "### Main Outputs\n\n| Output | Description |\n|---|---|\n| `s3_bucket_id` | id |\n\n"
        "### Usage Examples\n\n#### Example 1\n\n```hcl\nx = 1\n```\n"
    )
    out = _extract_interface_h3(block, {"inputs"})
    assert "## Root Module: S3 Bucket" in out
    assert "### Main Input Variables" in out
    assert "`bucket`" in out
    assert "### Main Outputs" not in out
    assert "### Description" not in out
    assert "### Usage Examples" not in out


def test_extract_interface_h3_examples_matches_singular_and_carries_children():
    block = (
        "## Submodule 1: notification\n\n"
        "### Main Input Variables\n\n| Variable | Type |\n|---|---|\n| `bucket_id` | `string` |\n\n"
        "### Usage Example\n\n#### Example A\n\n```hcl\ny = 2\n```\n"
    )
    out = _extract_interface_h3(block, {"examples"})
    assert "### Usage Example" in out
    assert "#### Example A" in out
    assert "y = 2" in out
    assert "### Main Input Variables" not in out


def test_extract_interface_h3_no_match_returns_empty():
    block = "## Root Module: X\n\n### Description\n\nnothing here.\n"
    assert _extract_interface_h3(block, {"inputs"}) == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_mcp_server.py -k extract_interface_h3 -q`
Expected: FAIL with `ImportError` / `cannot import name '_extract_interface_h3'`.

- [ ] **Step 3: Write minimal implementation**

Near `_SECTION_ALIASES` add:

```python
# Interface key -> lowercase H3 sub-heading prefixes to extract from a combined
# "## Root Module:"/"## Submodule N:" bundle. Prefix (startswith) match absorbs
# singular/plural ("Usage Example"/"Usage Examples") and the "Main ..." phrasing.
_INTERFACE_H3_PREFIXES: dict[str, tuple[str, ...]] = {
    "inputs": ("main input variables",),
    "variables": ("main input variables",),
    "outputs": ("main output",),
    "examples": ("usage example",),
    "usage": ("usage example",),
}

_H3_RE = re.compile(r"^### .+$", re.MULTILINE)
```

Near `_split_h2_sections` add:

```python
def _extract_interface_h3(block: str, keys: set[str]) -> str:
    """
    From one combined H2 bundle, return its heading line plus only the H3
    sub-sections whose title matches the requested interface keys.

    Args:
        block: A single "## Root Module:"/"## Submodule N:" bundle (heading + body).
        keys: Interface keys (subset of _INTERFACE_H3_PREFIXES).

    Returns:
        The H2 heading line followed by the matching "### ..." sub-blocks in
        document order, or "" when no sub-section matches.
    """
    prefixes = tuple(p for k in keys for p in _INTERFACE_H3_PREFIXES.get(k, ()))
    if not prefixes:
        return ""
    matches = list(_H3_RE.finditer(block))
    if not matches:
        return ""
    heading_line = block[: matches[0].start()].splitlines()[0] if block.strip() else ""
    kept: list[str] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
        title = m.group(0)[4:].strip().lower()
        if title.startswith(prefixes):
            kept.append(block[m.start() : end].rstrip())
    if not kept:
        return ""
    return heading_line.rstrip() + "\n\n" + "\n\n".join(kept)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_mcp_server.py -k extract_interface_h3 -q`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add src/tfmod_mcp_server.py tests/integration/test_mcp_server.py
git commit -m "Add combined-bundle H3 interface sub-section extractor"
```

---

### Task 2: Wire the extractor into `filter_module_sections` (fix the over-fetch) + `interface_scope`

**Files:**
- Modify: `src/tfmod_mcp_server.py` — `filter_module_sections` (signature + fallback + emit loop), ~lines 973-1063
- Test: `tests/integration/test_mcp_server.py`

**Interfaces:**
- Consumes: `_extract_interface_h3`, `_matches_combined_interface`, `_INTERFACE_KEYS`, `_INTERFACE_H3_PREFIXES` from Task 1 and existing code.
- Produces: `filter_module_sections(text, requested, *, extra_exact_titles=(), interface_scope="all", silent_keys=frozenset())`. `interface_scope in {"all","root"}`: `"root"` restricts combined-bundle extraction to `## Root Module:`/`## Main Module:` bundles (skip `## Submodule N:`). `silent_keys` handled in Task 3.

- [ ] **Step 1: Write the failing test**

```python
from tfmod_mcp_server import filter_module_sections


def _combined_doc():
    return (
        "---\nmodule_name: demo\n---\n\n"
        "## Module Information\n\n- **Module ID**: x/demo/aws\n\n"
        "## Description\n\nDemo.\n\n"
        "## Root Module: Demo\n\n"
        "### Main Input Variables\n\n| V | T |\n|---|---|\n| `root_in` | `string` |\n\n"
        "### Main Outputs\n\n| O | D |\n|---|---|\n| `root_out` | x |\n\n"
        "## Submodule 1: sub\n\n"
        "### Main Input Variables\n\n| V | T |\n|---|---|\n| `sub_in` | `string` |\n\n"
        "### Main Outputs\n\n| O | D |\n|---|---|\n| `sub_out` | y |\n\n"
        "## Notes for AI Agents\n\nNote.\n"
    )


def test_inputs_extracts_h3_not_whole_bundle_all_scope():
    out = filter_module_sections(_combined_doc(), ["inputs"])
    assert "`root_in`" in out and "`sub_in`" in out          # inputs from root AND submodule
    assert "root_out" not in out and "sub_out" not in out    # outputs NOT dragged in
    assert "Requested sections not found" not in out          # matched, not unmatched


def test_inputs_root_scope_excludes_submodule():
    out = filter_module_sections(_combined_doc(), ["inputs"], interface_scope="root")
    assert "`root_in`" in out
    assert "`sub_in`" not in out
    assert "root_out" not in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_mcp_server.py -k "extracts_h3 or root_scope" -q`
Expected: FAIL — current code returns whole bundles (`sub_out`/`root_out` present) and rejects `interface_scope` kwarg (`TypeError`).

- [ ] **Step 3: Write minimal implementation**

Change the signature:

```python
def filter_module_sections(
    text: str,
    requested: list[str],
    *,
    extra_exact_titles: tuple[str, ...] = (),
    interface_scope: str = "all",
    silent_keys: frozenset[str] = frozenset(),
) -> str:
```

Replace the fallback block (currently lines ~1023-1027) and the emit loop so interface-key fallbacks accumulate into a per-bundle-title extraction map instead of adding whole titles to `wanted`. Concretely, before the request loop add:

```python
    # Interface keys that found no exact H2 alias fall back to extracting their
    # H3 sub-section(s) from the combined "Root/Main Module:"/"Submodule N:"
    # bundles, rather than dragging in the whole bundle (the BUG-1 over-fetch).
    fallback_keys: set[str] = set()
```

In the request loop, replace the old `if not matched and key in _INTERFACE_KEYS:` block with:

```python
        if not matched and key in _INTERFACE_KEYS:
            for title, block in sections:
                tl = title.lower()
                if not _matches_combined_interface(tl):
                    continue
                if interface_scope == "root" and tl.startswith("submodule"):
                    continue
                if _extract_interface_h3(block, {key}):
                    fallback_keys.add(key)
                    matched = True
```

Then change the emit section so combined bundles contribute extracted H3s when any `fallback_keys` are active:

```python
    parts = [preamble.rstrip()] if preamble.strip() else []
    for title, block in sections:
        if title in wanted:
            parts.append(block.rstrip())
            continue
        tl = title.lower()
        if fallback_keys and _matches_combined_interface(tl):
            if interface_scope == "root" and tl.startswith("submodule"):
                continue
            extracted = _extract_interface_h3(block, fallback_keys)
            if extracted:
                parts.append(extracted)
```

Leave the footer computation as-is EXCEPT: `omitted`/`all_titles` still derive from `wanted` only; combined bundles that contributed a partial extraction are neither fully "wanted" nor cleanly "omitted". Keep them listed in the footer inventory (they ARE still requestable in full) — i.e. do not add partial-extraction titles to `wanted`. This is acceptable: the footer remains a complete menu.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_mcp_server.py -k "extracts_h3 or root_scope" -q`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/tfmod_mcp_server.py tests/integration/test_mcp_server.py
git commit -m "Extract H3 interface sub-sections instead of whole combined bundles"
```

---

### Task 3: `silent_keys` — suppress "not found" for server-injected keys

**Files:**
- Modify: `src/tfmod_mcp_server.py` — `filter_module_sections` unmatched bookkeeping
- Test: `tests/integration/test_mcp_server.py`

**Interfaces:**
- Consumes: the `silent_keys` param declared in Task 2.
- Produces: keys whose lowercased form is in `silent_keys` are dropped from the "Requested sections not found" footer line when unmatched (still matched normally when present).

- [ ] **Step 1: Write the failing test**

```python
def test_silent_keys_suppress_not_found():
    doc = (
        "---\nm: x\n---\n\n## Module Information\n\n- **Module ID**: x/y/aws\n\n"
        "## Description\n\nd\n\n## Submodule 1: only\n\n### Main Input Variables\n\n| V | T |\n|---|---|\n| `a` | `s` |\n\n"
        "## Notes for AI Agents\n\nn\n"
    )
    # 'features' absent here; as a silent key it must not appear in "not found"
    out = filter_module_sections(doc, ["features"], silent_keys=frozenset({"features"}))
    assert "Requested sections not found" not in out
    # without silent_keys, it IS reported
    out2 = filter_module_sections(doc, ["features"])
    assert "Requested sections not found: features" in out2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_mcp_server.py -k silent_keys -q`
Expected: FAIL — `features` reported in both, or `TypeError` if the loop ignores the param.

- [ ] **Step 3: Write minimal implementation**

In the request loop, when appending to `unmatched`, skip silent keys:

```python
        if not matched and key not in silent_keys:
            unmatched.append(entry)
```

(The `key` local is already the lowercased entry.)

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_mcp_server.py -k silent_keys -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tfmod_mcp_server.py tests/integration/test_mcp_server.py
git commit -m "Add silent_keys to suppress not-found footer for injected keys"
```

---

### Task 4: Inline compact root inputs into the orientation head

**Files:**
- Modify: `src/tfmod_mcp_server.py` — `orientation_head`, ~lines 1188-1208
- Test: `tests/integration/test_mcp_server.py`

**Interfaces:**
- Consumes: `filter_module_sections(..., interface_scope="root", silent_keys=...)` from Tasks 2-3, `_ORIENTATION_KEYS`.
- Produces: `orientation_head` unchanged signature; now inlines root inputs.

- [ ] **Step 1: Write the failing test**

```python
from tfmod_mcp_server import orientation_head


def test_head_inlines_root_inputs_combined():
    out = orientation_head(_combined_doc())  # helper from Task 2 test
    assert "### Main Input Variables" in out
    assert "`root_in`" in out
    assert "`sub_in`" not in out            # submodule inputs stay out of the head
    assert "Requested sections not found" not in out


def test_head_no_inputs_noise_for_collection_doc():
    # collection doc: only a submodule bundle, no root inputs
    doc = (
        "---\nm: coll\n---\n\n## Module Information\n\n- **Module ID**: x/coll/aws\n\n"
        "## Description\n\nd\n\n## Key Features\n\n- f\n\n## Main Use Cases\n\n- u\n\n"
        "## Submodule 1: only\n\n### Main Input Variables\n\n| V | T |\n|---|---|\n| `a` | `s` |\n\n"
        "## Notes for AI Agents\n\nn\n"
    )
    out = orientation_head(doc)
    assert "Requested sections not found" not in out
    assert "`a`" not in out                 # submodule inputs not inlined in a collection head
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_mcp_server.py -k "head_inlines_root or head_no_inputs" -q`
Expected: FAIL — current head omits inputs (`root_in` absent).

- [ ] **Step 3: Write minimal implementation**

```python
    body = filter_module_sections(
        text,
        [*_ORIENTATION_KEYS, "inputs"],
        extra_exact_titles=("Submodules",),
        interface_scope="root",
        silent_keys=frozenset({*_ORIENTATION_KEYS, "inputs"}),
    )
```

Update the `orientation_head` docstring to note root inputs are inlined. `_ORIENTATION_KEYS` entries are the alias keys `"features"`, `"use-cases"`; add `"inputs"`. Note `silent_keys` compares lowercased entries, and these keys are already lowercase.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_mcp_server.py -k "head_inlines_root or head_no_inputs" -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tfmod_mcp_server.py tests/integration/test_mcp_server.py
git commit -m "Inline compact root inputs into the default orientation head"
```

---

### Task 5: Real-corpus regression tests (over-fetch + head, on shipped docs)

**Files:**
- Test: `tests/integration/test_mcp_server.py`

**Interfaces:**
- Consumes: `get_module_impl` / server fixtures already used in this test file (reuse the existing state/fixture pattern in the file — do not invent a new one).

- [ ] **Step 1: Write the tests**

The file uses the module-scoped `server_state` fixture and calls
`get_module_impl("vpc", server_state, sections=[...])` (see `TestGetModuleSections`,
~line 280). Add, in that class or a sibling:

```python
@pytest.mark.parametrize("mod", ["s3-bucket", "ecr", "lambda"])
def test_sections_inputs_examples_no_overfetch_real_docs(self, server_state, mod):
    out = get_module_impl(mod, server_state, sections=["inputs", "examples"])
    assert "Requested sections not found" not in out
    # not the whole bundle: a root ### Main Outputs sub-section must not be dragged in
    assert "### Main Outputs" not in out
    full = get_module_impl(mod, server_state, sections=["all"])
    assert len(out) < len(full)


@pytest.mark.parametrize("mod", ["vpc", "redshift"])
def test_default_head_has_root_inputs_real_docs(self, server_state, mod):
    out = get_module_impl(mod, server_state)
    assert "Main Input Variables" in out
    assert "Requested sections not found" not in out


def test_collection_head_no_inputs_noise_real_doc(self, server_state):
    out = get_module_impl("iam", server_state)
    assert "Requested sections not found" not in out
```

`redshift` is split-toplevel (its `## Main Input Variables` H2 resolves via exact alias);
`vpc` is combined. `s3-bucket`/`ecr`/`lambda` are the report's named BUG-1 repros. `pytest`
is already imported in this file.

**Then run the whole `TestGetModuleSections` class** — its existing tests were traced to
survive these changes (the extractor keeps the `## Root/Submodule …` heading line, so the
`"## Root Module: S3 Bucket" in filtered` and `"## Main Input Variables" in filtered`
substring assertions still hold; `iam` is a collection doc so its head is unchanged). If any
existing test fails, fix it to match the new intended behavior in the spec — do NOT weaken an
assertion to hide a real regression.

- [ ] **Step 2: Run tests**

Run: `pytest tests/integration/test_mcp_server.py -k "no_overfetch_real or default_head_has_root or collection_head_no_inputs" -q`
Expected: PASS. If `ecr` or `lambda` has no `### Main Outputs` heading at all, the "whole bundle" assertion still holds; if a real doc surprises the assertion, adjust to assert absence of a concrete non-requested row instead — but first confirm against the actual doc, do not weaken silently.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_mcp_server.py
git commit -m "Add real-corpus regression tests for section over-fetch and head inputs"
```

---

### Task 6: Broaden the grep hint to shapes/types (wording)

**Files:**
- Modify: `src/tfmod_mcp_server.py` — footer honest-limits sentence in `filter_module_sections` (~line 1046-1052) and the `grep_module_docs` tool description
- Audit: `plugins/tfmod-search/skills/tf-module/SKILL.md` (edit only if it phrases grep as names-only)
- Test: `tests/integration/test_mcp_server.py`

**Interfaces:** none.

- [ ] **Step 1: Write the failing test**

```python
def test_footer_grep_hint_mentions_shapes():
    doc = (
        "---\nm: x\n---\n\n## Module Information\n\n- **Module ID**: x/y/aws\n\n"
        "## Description\n\nd\n\n## Notes for AI Agents\n\nn\n"
    )
    out = filter_module_sections(doc, [])
    low = out.lower()
    assert "shape" in low or "type" in low  # grep-for-shapes guidance present
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_mcp_server.py -k footer_grep_hint_mentions_shapes -q`
Expected: FAIL (current footer says "type" already? confirm — if it already contains "type", strengthen the assertion to require the explicit shape/verify phrasing added below, e.g. `assert "exact type/shape" in out`).

- [ ] **Step 3: Write the wording change**

In the footer honest-limits sentence, extend the grep pointer to name shape/type verification, e.g. append to the existing sentence: "Use `grep_module_docs` not only to confirm resource/variable NAMES but to verify the exact TYPE/SHAPE of a `map(object)`/`any`-typed input (its nested field structure) before writing it." Mirror the same emphasis in the `grep_module_docs` tool description string. Audit the `tf-module` skill; if it says grep is for names, widen it to names and shapes. Make the test assertion match the exact phrase you commit.

**Constraint:** `test_response_carries_escalation_pointer` (existing) asserts the footer still
contains the literal substrings `"grep_module_docs"`, `"COMPLETE inputs/outputs"`, and
`"module source"`. Preserve all three phrases verbatim — append your shape/type sentence, do
not rewrite them away.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_mcp_server.py -k footer_grep_hint_mentions_shapes -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "Broaden grep hint from names to names and shapes"
```

---

### Task 7: Full suite + version bump + CHANGELOG

**Files:**
- Modify: `pyproject.toml`, `plugins/tfmod-search/.claude-plugin/plugin.json`, `plugins/tfmod-search/.codex-plugin/plugin.json`, `plugins/tfmod-search/bin/tfmodsearch_launch.py` (`DEFAULT_IMAGE`), `docker-compose.yml`, `README.md` (current-release image tags), `CHANGELOG.md`

- [ ] **Step 1: Run the full suite**

Run: `pytest tests/ -q`
Expected: all pass (opt-in live tests skip without `RUN_REGISTRY_BENCHMARK=1`). The known `TestClaudeCliLive` local shadow flake may fail — that is environment, not this change.

- [ ] **Step 2: Bump the version everywhere**

Run to find all sites: `grep -rn "0\.19\.1" pyproject.toml plugins/ README.md docker-compose.yml`
Set each to `0.20.0`: `pyproject.toml` `version`, both plugin `plugin.json`, `DEFAULT_IMAGE` in `plugins/tfmod-search/bin/tfmodsearch_launch.py`, `docker-compose.yml` image tag, README current-release image tags (quick-install `.mcp.json`, `TFMODSEARCH_IMAGE` example, offline-verify command). Leave historical CHANGELOG/doc version mentions untouched.

- [ ] **Step 3: Add the CHANGELOG entry**

Match the existing format (link line, summary, Added/Changed/Unchanged). Summary: combined-heading section over-fetch fix, compact root inputs inlined in the default orientation head, grep hint broadened to shapes/types; index and corpus unchanged; stdio/HTTP behavior otherwise unchanged.

- [ ] **Step 4: Verify and commit**

Run: `pytest tests/ -q` once more.

```bash
git add -A
git commit -m "Release 0.20.0: orientation quick wins (section over-fetch fix, head inputs, grep hint)"
```

---

## Self-Review notes

- Spec coverage: Change 1 → Tasks 1-2 + 5; Change 2 → Tasks 3-4 + 5; Change 3 → Task 6; release plumbing → Task 7. All spec changes have a task.
- Type consistency: `interface_scope: str`, `silent_keys: frozenset[str]`, `_extract_interface_h3(block, keys: set[str]) -> str`, `_INTERFACE_H3_PREFIXES: dict[str, tuple[str, ...]]` used consistently across tasks.
- The `_combined_doc()` helper defined in Task 2's test is reused by Task 4's test — keep it module-level in the test file.
