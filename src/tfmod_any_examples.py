"""
Pure, offline extraction of `type = any` variable examples and observed field
names from a Terraform module's own source (fetched by
tfmod_registry_docs.fetch_module_source).

Design: evals/specs/2026-07-20-consolidated-interface-any-overlay-design.md
("examples-primary" - serve the module maintainer's own apply-verified
example HCL, plus a names-only observed-field checklist, rather than
reconstructing a shape tree). No HCL parser: stdlib regex over a
string/heredoc/comment-aware balanced-bracket scanner. Never raises on
malformed input - a parse hazard degrades to "no result found", never a
crash, matching the honest-any fallback the caller then serves.

Exports:
- find_any_vars(source_dir) -> list[(scope, var_name)]
- extract_examples(source_dir, scope, var_name) -> list[str]
- observed_field_names(source_dir, scope, var_name) -> list[str]
- coverage_report(source_dir) -> dict
"""

import re
from pathlib import Path

# --------------------------------------------------------------------------- #
# Low-level, string/heredoc/comment-aware balanced-bracket scanning.
#
# Every one of the idioms in evals/specs/2026-07-20-review-panel-evidence.md
# (commented-out blocks with braces, multiline RHS, nested for-expressions)
# breaks a naive `text.index("}")`/regex approach, so every block-boundary
# helper below goes through the same three primitives.
# --------------------------------------------------------------------------- #

_PAIRS = {"{": "}", "[": "]", "(": ")"}
_CLOSERS = (")", "]", "}")
_HEREDOC_START_RE = re.compile(r"<<-?(\w+)")
_NOT_WORD_BEFORE = r"(?<![A-Za-z0-9_])"
_NOT_WORD_AFTER = r"(?![A-Za-z0-9_])"


def _skip_string(text: str, i: int) -> int:
    """text[i] == '"'; return the index just past the matching close quote."""
    j = i + 1
    n = len(text)
    while j < n:
        if text[j] == "\\":
            j += 2
            continue
        if text[j] == '"':
            return j + 1
        j += 1
    return n


def _skip_heredoc(text: str, i: int, match: re.Match) -> int:
    """text[i:] starts a `<<EOT`/`<<-EOT` heredoc; return the index just past
    the terminator line (or end of text if unterminated)."""
    identifier = match.group(1)
    dashed = text[i : i + 3].startswith("<<-")
    nl = text.find("\n", i)
    if nl == -1:
        return len(text)
    pos = nl + 1
    indent = r"[ \t]*" if dashed else ""
    term_re = re.compile(r"^" + indent + re.escape(identifier) + r"[ \t]*$", re.MULTILINE)
    m = term_re.search(text, pos)
    return m.end() if m else len(text)


def _skip_noncode(text: str, i: int) -> int:
    """If text[i] opens a string, heredoc, or comment, return the index to
    resume scanning at; otherwise return i unchanged."""
    if i >= len(text):
        return i
    c = text[i]
    if c == '"':
        return _skip_string(text, i)
    if c == "#" or text[i : i + 2] == "//":
        nl = text.find("\n", i)
        return nl if nl != -1 else len(text)
    if text[i : i + 2] == "/*":
        end = text.find("*/", i + 2)
        return end + 2 if end != -1 else len(text)
    if text[i : i + 2] == "<<":
        m = _HEREDOC_START_RE.match(text, i)
        if m:
            return _skip_heredoc(text, i, m)
    return i


def _grab_balanced(text: str, open_idx: int) -> tuple[str, int]:
    """Given the index of an opening `{`, `[`, or `(`, return
    (inner_text, index_of_matching_close). String/heredoc/comment-aware;
    bracket kinds are balanced together (a `[` found while scanning for a
    `{`'s close still increments/decrements the same depth counter), which
    is a safe simplification for well-formed HCL and avoids having to track
    a bracket-kind stack."""
    depth = 0
    i = open_idx
    n = len(text)
    while i < n:
        j = _skip_noncode(text, i)
        if j != i:
            i = j
            continue
        c = text[i]
        if c in _PAIRS:
            depth += 1
        elif c in _CLOSERS:
            depth -= 1
            if depth == 0:
                return text[open_idx + 1 : i], i
        i += 1
    return text[open_idx + 1 :], n


def _grab_rhs(text: str, start_idx: int) -> tuple[str, int]:
    """From start_idx (just after a `=`), grab a full expression: a single
    line, or - while bracket/paren/brace depth stays > 0 - multiple lines.
    Stops at the first top-level (depth <= 0) newline. Returns
    (rhs_text_stripped, end_index_exclusive_of_the_newline)."""
    i = start_idx
    n = len(text)
    while i < n and text[i] in " \t":
        i += 1
    depth = 0
    start = i
    while i < n:
        j = _skip_noncode(text, i)
        if j != i:
            i = j
            continue
        c = text[i]
        if c in _PAIRS:
            depth += 1
        elif c in _CLOSERS:
            depth -= 1
        elif c == "\n" and depth <= 0:
            return text[start:i].strip(), i
        i += 1
    return text[start:i].strip(), i


def _split_top_level(text: str, sep: str = ",") -> list[str]:
    """Split text on `sep` at depth 0 only (string/heredoc/comment-aware)."""
    parts = []
    depth = 0
    start = 0
    i = 0
    n = len(text)
    while i < n:
        j = _skip_noncode(text, i)
        if j != i:
            i = j
            continue
        c = text[i]
        if c in _PAIRS:
            depth += 1
        elif c in _CLOSERS:
            depth -= 1
        elif c == sep and depth == 0:
            parts.append(text[start:i])
            start = i + 1
        i += 1
    parts.append(text[start:i])
    return parts


_ASSIGNMENT_KEY_RE = re.compile(r'[ \t]*"?([A-Za-z_][\w-]*)"?[ \t]*=(?!=)')


def _iter_top_level_assignments(body: str):
    """Yield (key, rhs_text, key_start_idx, rhs_end_idx) for each top-level
    `key = value` assignment in a flat block body (a locals block, a
    module-call body, or an object-literal argument) - skipping comments/
    blank lines and resyncing to the next line on anything that is not a
    recognizable assignment. The index pair lets a caller slice the
    ORIGINAL text verbatim (`body[key_start_idx:rhs_end_idx]`) instead of
    reconstructing formatting from the parsed (key, rhs_text) pair.

    Tries an assignment-key match FIRST, before any string/comment skip: a
    quoted key (`"name" = i`, as merge()-injected object literals use) must
    not be mistaken for a stray string value and skipped over."""
    i = 0
    n = len(body)
    while i < n:
        c = body[i]
        if c in " \t\r\n":
            i += 1
            continue
        m = _ASSIGNMENT_KEY_RE.match(body, i)
        if m:
            key = m.group(1)
            rhs, end_idx = _grab_rhs(body, m.end())
            yield key, rhs, m.start(1), end_idx
            i = end_idx
            continue
        j = _skip_noncode(body, i)
        if j != i:
            i = j
            continue
        nl = body.find("\n", i)
        i = nl + 1 if nl != -1 else n


# --------------------------------------------------------------------------- #
# find_any_vars
# --------------------------------------------------------------------------- #

_VARIABLE_BLOCK_RE = re.compile(r'\bvariable\s+"([A-Za-z_][\w-]*)"\s*\{')
_TYPE_ANY_RE = re.compile(r"(?m)^[ \t]*type[ \t]*=[ \t]*any\b")


def _find_any_vars_in_text(text: str) -> list[str]:
    names = []
    for vm in _VARIABLE_BLOCK_RE.finditer(text):
        body, _ = _grab_balanced(text, vm.end() - 1)
        if _TYPE_ANY_RE.search(body):
            names.append(vm.group(1))
    return names


def find_any_vars(source_dir: str | Path) -> list[tuple[str, str]]:
    """
    Every `type = any` variable in the module's root and each real submodule
    (`modules/*`, excluding `wrappers/*`). Comment-tolerant: `type = any  #
    map(string)` still counts (idiom N14).

    Returns a list of (scope, var_name) where scope is "root" or the
    submodule's directory name.
    """
    source_dir = Path(source_dir)
    result: list[tuple[str, str]] = []

    root_vf = source_dir / "variables.tf"
    if root_vf.is_file():
        text = root_vf.read_text(encoding="utf-8", errors="replace")
        result.extend(("root", name) for name in _find_any_vars_in_text(text))

    modules_dir = source_dir / "modules"
    if modules_dir.is_dir():
        for sub in sorted(p for p in modules_dir.iterdir() if p.is_dir()):
            if sub.name == "wrappers":
                continue
            vf = sub / "variables.tf"
            if not vf.is_file():
                continue
            text = vf.read_text(encoding="utf-8", errors="replace")
            result.extend((sub.name, name) for name in _find_any_vars_in_text(text))

    return result


# --------------------------------------------------------------------------- #
# extract_examples - source-attribution-aware example extraction
# --------------------------------------------------------------------------- #

_MODULE_BLOCK_RE = re.compile(r'\bmodule\s+"([^"]+)"\s*\{')
_SOURCE_ATTR_RE = re.compile(r'(?m)^[ \t]*source[ \t]*=[ \t]*"([^"]*)"')
_TRIVIAL_BARE_RE = re.compile(r'^(?:var|local|module)\.[\w.\[\]"*-]+$')


def _route_source(source: str) -> str | None:
    """Classify a `module "x" { source = ... }` block's source string ->
    "root", a submodule name, or None (an external helper - e.g. a registry
    id or a different local path - to be skipped)."""
    s = source.strip()
    if s in ("../..", "../../"):
        return "root"
    m = re.match(r"^\.\./\.\./modules/([^/]+)/?$", s)
    return m.group(1) if m else None


def _strip_line_comment(s: str) -> str:
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '"':
            i = _skip_string(s, i)
            continue
        if c == "#" or s[i : i + 2] == "//":
            return s[:i].rstrip()
        i += 1
    return s.rstrip()


def _is_trivial(raw_assignment: str) -> bool:
    _, _, rhs = raw_assignment.partition("=")
    rhs = _strip_line_comment(rhs).strip()
    compact = re.sub(r"\s+", "", rhs)
    if compact in ("[]", "{}", "null"):
        return True
    return bool(_TRIVIAL_BARE_RE.match(rhs))


def _collect_assignments(source_dir: Path, scope: str, var_name: str) -> list[tuple[str, bool]]:
    """Every `var_name = <rhs>` assignment inside a `module` block in
    examples/**/*.tf that routes (by `source`) to `scope`. Returns
    (raw_verbatim_text, is_trivial) pairs, in file/discovery order."""
    examples_dir = Path(source_dir) / "examples"
    if not examples_dir.is_dir():
        return []

    results: list[tuple[str, bool]] = []
    for tf_file in sorted(examples_dir.rglob("*.tf")):
        try:
            text = tf_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for mm in _MODULE_BLOCK_RE.finditer(text):
            body, _ = _grab_balanced(text, mm.end() - 1)
            src_m = _SOURCE_ATTR_RE.search(body)
            if not src_m:
                continue
            if _route_source(src_m.group(1)) != scope:
                continue
            # Top-level assignments only (not _SOURCE_ATTR_RE-style line
            # search over the whole body): a nested object argument could
            # otherwise coincidentally carry a key equal to var_name.
            for key, _rhs, key_start, end_idx in _iter_top_level_assignments(body):
                if key != var_name:
                    continue
                raw = body[key_start:end_idx].rstrip()
                results.append((raw, _is_trivial(raw)))
    return results


def _touched_field_names(rhs_text: str) -> set[str]:
    """Shallow (any-depth, flat) set of `key =` names appearing in an
    example block - used only to decide whether a second, larger example
    contributes new coverage (its field-union differs)."""
    return set(re.findall(r'(?:^|[\s{,\[])"?([A-Za-z_][\w-]*)"?[ \t]*=(?!=)', rhs_text, re.MULTILINE))


def _select_covering(raw_texts: list[str]) -> list[str]:
    """Pick the smallest non-trivial covering block; keep additional blocks
    only when they contribute field names the smaller ones do not."""
    seen: dict[str, str] = {}
    for t in raw_texts:
        key = re.sub(r"\s+", " ", t).strip()
        seen.setdefault(key, t)
    unique = sorted(seen.values(), key=len)

    selected: list[str] = []
    covered_fields: set[str] = set()
    for t in unique:
        fields = _touched_field_names(t)
        if not selected or not fields.issubset(covered_fields):
            selected.append(t)
            covered_fields |= fields
    return selected


def extract_examples(source_dir: str | Path, scope: str, var_name: str) -> list[str]:
    """
    The verbatim HCL block(s) from `examples/**/*.tf` that assign `var_name`
    on the module identified by `scope` ("root" or a submodule name).

    Source-attribution-aware: a `module "x" { source = ... }` block only
    counts if its `source` routes to `scope` (`../..`/`../../` -> root,
    `../../modules/X` -> submodule X); any other source (a registry id, a
    different local path) is a helper module and is skipped, so a
    same-named argument on a helper is never misattributed.

    Trivial assignments (`[]`, `{}`, `null`, a bare `var./local./module.`
    passthrough) are skipped. Returns the smallest non-trivial covering
    block, plus any additional block whose assigned-field set differs.
    """
    assignments = _collect_assignments(Path(source_dir), scope, var_name)
    non_trivial = [raw for raw, trivial in assignments if not trivial]
    return _select_covering(non_trivial)


# --------------------------------------------------------------------------- #
# observed_field_names - union-of-ALL-consumers field-NAME scan
# --------------------------------------------------------------------------- #


def _known_base_pattern(bases: set[str]) -> re.Pattern | None:
    if not bases:
        return None
    alts = sorted(bases, key=len, reverse=True)
    return re.compile(_NOT_WORD_BEFORE + r"(?:" + "|".join(re.escape(b) for b in alts) + r")" + _NOT_WORD_AFTER)


def _references_any_base(expr: str, bases: set[str]) -> bool:
    pattern = _known_base_pattern(bases)
    return bool(pattern.search(expr)) if pattern else False


def _direct_fields_for_base(text: str, base: str) -> set[str]:
    """Field names read directly off `base`: `<base>.<field>`,
    `<base>["<field>"]`, `lookup(<base>, "<field>")` (attribute-chain heads
    only - one segment past the base, never a deeper nested chain)."""
    b = re.escape(base)
    lb = _NOT_WORD_BEFORE
    fields = set(re.findall(lb + b + r"\.([A-Za-z_]\w*)", text))
    fields |= set(re.findall(lb + b + r'\[\s*"([A-Za-z_][\w-]*)"\s*\]', text))
    fields |= set(re.findall(r"lookup\(\s*" + lb + b + r'\s*,\s*"([A-Za-z_][\w-]*)"', text))
    return fields


def _for_each_rhs(body: str) -> str | None:
    m = re.search(r"(?m)^[ \t]*for_each[ \t]*=(?!=)", body)
    if not m:
        return None
    rhs, _ = _grab_rhs(body, m.end())
    return rhs


_FOR_EXPR_RE = re.compile(r"\bfor\s+(?:([A-Za-z_]\w*)\s*,\s*)?([A-Za-z_]\w*)\s+in\s+([^:{}\[\]]+?)\s*:")


def _enclosing_bracket_body(text: str, pos: int, max_back: int = 4000) -> str | None:
    """Best-effort: find the nearest enclosing `{...}`/`[...]` around
    text[pos] by scanning backward for an unmatched opener, then grab its
    balanced body. Bounds the backward scan so a pathological file cannot
    make this O(n^2); returns None (safe no-op) if nothing is found within
    the budget."""
    depth = 0
    i = pos - 1
    floor = max(0, pos - max_back)
    while i >= floor:
        c = text[i]
        if c in _CLOSERS:
            depth += 1
        elif c in _PAIRS:
            if depth == 0:
                body, _ = _grab_balanced(text, i)
                return body
            depth -= 1
        i -= 1
    return None


def _generic_for_expr_fields(text: str, bases: set[str]) -> set[str]:
    """Best-effort support for a bare for-expression loop var reading fields
    directly (`[for r in var.X : r.field]`), bounded to the comprehension's
    own enclosing bracket so a reused loop-var name (`v`, `k`) elsewhere in
    the file cannot bleed fields from an unrelated var."""
    fields: set[str] = set()
    for fm in _FOR_EXPR_RE.finditer(text):
        expr = fm.group(3)
        if not _references_any_base(expr, bases):
            continue
        loopvar = fm.group(2)
        body = _enclosing_bracket_body(text, fm.start())
        if body is None:
            continue
        fields |= _direct_fields_for_base(body, loopvar)
    return fields


def _scan_scope_for_var(text: str, bases: set[str]) -> set[str]:
    """Recursively scan `text` (a file, or a nested dynamic/resource block
    body) for direct field access on any current base, plus dynamic/
    resource/data blocks whose `for_each` references a current base -
    scoping any newly-discovered iterator base (`<label>.value`/
    `each.value`) to that block's own body so same-named iterators in
    unrelated blocks never leak fields into each other."""
    fields: set[str] = set()
    for base in bases:
        fields |= _direct_fields_for_base(text, base)
    fields |= _generic_for_expr_fields(text, bases)

    for dm in re.finditer(r'dynamic\s+"([A-Za-z_][\w-]*)"\s*\{', text):
        label = dm.group(1)
        body, _ = _grab_balanced(text, dm.end() - 1)
        fe_rhs = _for_each_rhs(body)
        if fe_rhs is not None and _references_any_base(fe_rhs, bases):
            fields |= _scan_scope_for_var(body, bases | {f"{label}.value"})

    for rm in re.finditer(r'(?:resource|data)\s+"[^"]+"\s+"[^"]+"\s*\{', text):
        body, _ = _grab_balanced(text, rm.end() - 1)
        fe_rhs = _for_each_rhs(body)
        if fe_rhs is not None and _references_any_base(fe_rhs, bases):
            fields |= _scan_scope_for_var(body, bases | {"each.value"})

    return fields


def _merge_injected_keys(rhs: str) -> set[str]:
    """N2 idiom: `merge(x, {"name" = i})` injects a synthetic key ("name")
    onto every element of a var-derived comprehension. Scan an alias RHS for
    `merge(...)` calls and collect the literal top-level keys of any
    object-literal argument, so callers can subtract them from the final
    field-name set (an injected key is never part of the user-supplied
    shape, even though a downstream consumer legitimately reads it)."""
    keys: set[str] = set()
    for mm in re.finditer(r"merge\s*\(", rhs):
        open_idx = mm.end() - 1
        args_text, _ = _grab_balanced(rhs, open_idx)
        for arg in _split_top_level(args_text, ","):
            arg = arg.strip()
            if arg.startswith("{"):
                inner, _ = _grab_balanced(arg, 0)
                keys.update(key for key, *_rest in _iter_top_level_assignments(inner))
    return keys


def _scope_files(source_dir: Path, scope: str) -> list[Path]:
    if scope == "root":
        return sorted(source_dir.glob("*.tf"))
    return sorted((source_dir / "modules" / scope).glob("*.tf"))


def observed_field_names(source_dir: str | Path, scope: str, var_name: str) -> list[str]:
    """
    Union, across every `.tf` file in `scope` ("root" or a submodule name),
    of the field NAMES the module's own code reads off `var_name` (or a
    locals alias single-derived from it, e.g. `try(jsondecode(var.X),
    var.X)`): `<iter>.value.<field>` (dynamic blocks), `each.value.<field>`
    (resource/data `for_each`), `lookup(<iter>, "<field>")`, and
    for-expression loop-var `<v>.<field>`.

    NAMES ONLY - no nesting/tree reconstruction, so a field nested two
    levels deep and a top-level field of the same name are not
    distinguished; the checklist answers "does field X exist somewhere",
    not "where". Merge()-injected synthetic keys (idiom N2) are subtracted.
    Not a schema.
    """
    source_dir = Path(source_dir)
    files = _scope_files(source_dir, scope)
    texts = []
    for f in files:
        try:
            texts.append(f.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue

    bases = {f"var.{var_name}"}
    synthetic: set[str] = set()
    for text in texts:
        for lm in re.finditer(r"locals\s*\{", text):
            body, _ = _grab_balanced(text, lm.end() - 1)
            for key, rhs, *_rest in _iter_top_level_assignments(body):
                refs = set(re.findall(r"var\.([A-Za-z_]\w*)", rhs))
                if refs == {var_name}:
                    bases.add(f"local.{key}")
                    synthetic |= _merge_injected_keys(rhs)

    fields: set[str] = set()
    for text in texts:
        fields |= _scan_scope_for_var(text, bases)

    return sorted(fields - synthetic)


# --------------------------------------------------------------------------- #
# coverage_report
# --------------------------------------------------------------------------- #


def coverage_report(source_dir: str | Path) -> dict:
    """
    Of this module's `any`-typed vars: how many have >=1 non-trivial example
    (covered), trivial-only assignments, or none at all. Returns
    {"covered": int, "trivial_only": int, "none": int,
     "vars": {"<scope>::<var>": "covered"|"trivial_only"|"none"}}.
    """
    source_dir = Path(source_dir)
    counts = {"covered": 0, "trivial_only": 0, "none": 0}
    var_status: dict[str, str] = {}
    for scope, var_name in find_any_vars(source_dir):
        assignments = _collect_assignments(source_dir, scope, var_name)
        non_trivial = [raw for raw, trivial in assignments if not trivial]
        if non_trivial:
            status = "covered"
        elif assignments:
            status = "trivial_only"
        else:
            status = "none"
        counts[status] += 1
        var_status[f"{scope}::{var_name}"] = status
    return {**counts, "vars": var_status}
