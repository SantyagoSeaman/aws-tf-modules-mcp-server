# 0.19.0 ONNX Encode Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> This plan is an execution artifact; where the merged code differs, the code and the spec
> (`docs/superpowers/specs/2026-07-15-onnx-encode-backend-design.md`) are authoritative.

**Goal:** Query/index encoding via onnxruntime as a selectable backend, and a Docker image that ships ONNX instead of torch (~1.42 GB → ~0.6 GB).

**Architecture:** A small `Encoder` seam in `tfmod_search_lib` (env-selected: auto/torch/onnx) with the sentence-transformers import made lazy; a new `tfmod_onnx_encoder` module (tokenizers + onnxruntime + mean-pool + L2 norm); the Dockerfile builder exports ONNX with optimum and the runtime stage installs the wheel with an explicit torch-free dependency list.

**Tech Stack:** onnxruntime, tokenizers (new optional extra `tfmodsearch[onnx]`); optimum-onnx (Docker builder only); existing pickled index untouched.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-15-onnx-encode-backend-design.md`. Spike numbers: cosine min 0.99999988, max diff 4.06e-07 across all 162 golden queries.
- **PyPI/uvx dependency set unchanged** — sentence-transformers stays a core dependency; onnx bits are an optional extra.
- **The index pickle is NOT rebuilt** (standing drift policy).
- Default behavior with no new env vars set must be identical to 0.18.0 (torch path).
- Commit messages: plain content-only, NO apostrophes/contractions, no attribution trailers.
- Venv: `source .venv/bin/activate` (onnxruntime + tokenizers already installed there for the spike).
- Local ONNX assets for tests/gate: `/private/tmp/claude-501/-Users-alexandermakeev-Work-aws-tf-modules-mcp-server/df34f2bc-ab98-4a73-97b9-a8c6d4842cb6/scratchpad/e5-small-v2-onnx` (exported during the spike; contains model.onnx + tokenizer.json).

---

### Task 1: Encoder seam in tfmod_search_lib (lazy ST import, backend selection)

**Files:**
- Modify: `src/tfmod_search_lib.py`
- Create: `src/tfmod_onnx_encoder.py`
- Test: `tests/integration/test_encoder_backends.py` (new)
- Modify: `pyproject.toml` (optional extra + wheel packages list)

**Interfaces (produced):**
- `tfmod_search_lib._resolve_backend(env: Mapping[str, str] | None = None) -> str` — returns `"torch"` or `"onnx"`; raises `ValueError` on unknown value, `RuntimeError` when auto finds neither.
- `tfmod_search_lib._get_encoder(model_name: str, logger) -> Encoder` — cached (key `f"{backend}:{model_name}"`), lock-guarded construction.
- `Encoder.encode(texts: list[str], prompt: str | None = None) -> np.ndarray` — (N, D) float32 L2-normalized.
- `tfmod_onnx_encoder.OnnxEncoder(model_dir: Path, max_seq_length: int = 512)`; `tfmod_onnx_encoder.resolve_onnx_model_dir(project_root: Path | None = None) -> Path | None`.

- [ ] **Step 1: Write failing tests** — create `tests/integration/test_encoder_backends.py`:

```python
"""Encoder backend selection and the ONNX encoder.

ONNX asset-dependent tests are gated on TFMODSEARCH_ONNX_TEST_ASSETS pointing
at an exported e5-small-v2 ONNX dir (model.onnx + tokenizer.json); they skip
when the var is unset (e.g. in CI, which has no assets).
"""

import logging
import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import tfmod_search_lib as lib
from tfmod_onnx_encoder import OnnxEncoder, resolve_onnx_model_dir

ASSETS = os.environ.get("TFMODSEARCH_ONNX_TEST_ASSETS", "")
needs_assets = pytest.mark.skipif(
    not (ASSETS and (Path(ASSETS) / "model.onnx").is_file()),
    reason="TFMODSEARCH_ONNX_TEST_ASSETS not set or has no model.onnx",
)
logger = logging.getLogger("test-encoder")


def test_resolve_backend_default_is_torch_when_st_available():
    assert lib._resolve_backend({}) == "torch"


def test_resolve_backend_explicit_values():
    assert lib._resolve_backend({"TFMODSEARCH_EMBED_BACKEND": "torch"}) == "torch"
    assert lib._resolve_backend({"TFMODSEARCH_EMBED_BACKEND": "onnx"}) == "onnx"
    assert lib._resolve_backend({"TFMODSEARCH_EMBED_BACKEND": " ONNX "}) == "onnx"


def test_resolve_backend_rejects_unknown():
    with pytest.raises(ValueError):
        lib._resolve_backend({"TFMODSEARCH_EMBED_BACKEND": "tensorflow"})


def test_resolve_onnx_model_dir_env_and_missing(tmp_path):
    assert resolve_onnx_model_dir(project_root=tmp_path) is None
    d = tmp_path / "onnx" / "e5-small-v2"
    d.mkdir(parents=True)
    (d / "model.onnx").write_bytes(b"x")
    assert resolve_onnx_model_dir(project_root=tmp_path) == d


def test_lib_module_has_no_toplevel_sentence_transformers_import():
    import ast

    tree = ast.parse(Path(lib.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)) and node.col_offset == 0:
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module]
            assert "sentence_transformers" not in names, "ST import must be lazy"


@needs_assets
def test_onnx_encoder_shape_dtype_norm():
    enc = OnnxEncoder(Path(ASSETS))
    vecs = enc.encode(["s3 bucket", "kubernetes cluster"])
    assert vecs.shape[0] == 2 and vecs.dtype == np.float32
    np.testing.assert_allclose(np.linalg.norm(vecs, axis=1), 1.0, rtol=1e-5)


@needs_assets
def test_onnx_encoder_prompt_prepends():
    enc = OnnxEncoder(Path(ASSETS))
    with_prompt = enc.encode(["vpc"], prompt="query: ")[0]
    manual = enc.encode(["query: vpc"])[0]
    np.testing.assert_allclose(with_prompt, manual, atol=1e-6)


@needs_assets
def test_onnx_parity_with_sentence_transformers():
    queries = [
        "vpc", "s3 bucket with encryption", "kubernetes cluster",
        "serverless function execution", "managed relational database",
        "content delivery network", "iam roles and policies",
        "dns hosted zone", "message queue", "web application firewall",
    ]
    st_vecs = lib._get_sentence_transformer(lib.DEFAULT_MODEL_NAME, logger).encode(
        queries, convert_to_numpy=True, normalize_embeddings=True
    ).astype(np.float32)
    onnx_vecs = OnnxEncoder(Path(ASSETS)).encode(queries)
    cos = (st_vecs * onnx_vecs).sum(axis=1)
    assert cos.min() >= 0.9999, f"parity broken: min cosine {cos.min()}"


@needs_assets
def test_hybrid_search_with_onnx_backend(monkeypatch):
    monkeypatch.setenv("TFMODSEARCH_EMBED_BACKEND", "onnx")
    monkeypatch.setenv("TFMODSEARCH_ONNX_MODEL_DIR", ASSETS)
    lib._MODEL_CACHE.clear()
    index = lib.load_index(str(Path(lib.__file__).parent.parent / "model" / "tfmod_e5_small_index.pkl"), logger)
    results = lib.hybrid_search("s3 bucket with encryption and versioning", index, logger=logger, top_k=3)
    assert results and results[0].doc.module_name == "s3-bucket"
    lib._MODEL_CACHE.clear()
```

Note on `load_index` signature: check the actual signature in the lib before writing (it may take (path, logger) or a config object) and adapt this test accordingly — the assertion contract (top-1 s3-bucket via ONNX backend on the real index) is what matters. Same for the `hybrid_search` signature (weights may be required arguments; use the defaults the MCP server uses).

- [ ] **Step 2: Run to verify failures** — `TFMODSEARCH_ONNX_TEST_ASSETS=<scratchpad assets dir> pytest tests/integration/test_encoder_backends.py -v` → failures (no `_resolve_backend`, no `tfmod_onnx_encoder` module).

- [ ] **Step 3: Create `src/tfmod_onnx_encoder.py`:**

```python
"""ONNX encode backend for tfmodsearch: tokenizers + onnxruntime, no torch.

Replicates exactly what sentence-transformers does for intfloat/e5-small-v2
(Transformer -> attention-masked mean pooling -> L2 normalize), validated at
4e-07 max elementwise diff across the full golden query set. Dependencies come
from the optional extra `tfmodsearch[onnx]`.
"""

import os
from pathlib import Path

import numpy as np

DEFAULT_MAX_SEQ_LENGTH = 512


def resolve_onnx_model_dir(project_root: Path | None = None) -> Path | None:
    """Locate ONNX assets: env var first, then <project_root>/onnx/e5-small-v2."""
    env = os.environ.get("TFMODSEARCH_ONNX_MODEL_DIR", "").strip()
    if env:
        p = Path(env)
        return p if (p / "model.onnx").is_file() else None
    if project_root is not None:
        p = project_root / "onnx" / "e5-small-v2"
        if (p / "model.onnx").is_file():
            return p
    return None


class OnnxEncoder:
    """Drop-in encode() replacement for the SentenceTransformer path."""

    def __init__(self, model_dir: Path, max_seq_length: int = DEFAULT_MAX_SEQ_LENGTH):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        self._tokenizer = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
        self._tokenizer.enable_truncation(max_length=max_seq_length)
        self._session = ort.InferenceSession(
            str(model_dir / "model.onnx"), providers=["CPUExecutionProvider"]
        )
        self._needs_token_type = any(i.name == "token_type_ids" for i in self._session.get_inputs())

    def encode(self, texts: list[str], prompt: str | None = None) -> np.ndarray:
        """Encode texts to (N, D) float32 L2-normalized vectors.

        One text per session run: the spike showed the loop already beats the
        torch batch path on CPU, and it sidesteps padding entirely.
        """
        if prompt:
            texts = [f"{prompt}{t}" for t in texts]
        out = []
        for text in texts:
            enc = self._tokenizer.encode(text)
            ids = np.array([enc.ids], dtype=np.int64)
            mask = np.array([enc.attention_mask], dtype=np.int64)
            feeds = {"input_ids": ids, "attention_mask": mask}
            if self._needs_token_type:
                feeds["token_type_ids"] = np.zeros_like(ids)
            hidden = self._session.run(None, feeds)[0]
            m = mask[..., None].astype(np.float32)
            vec = (hidden * m).sum(axis=1) / m.sum(axis=1)
            vec = vec / np.linalg.norm(vec, axis=1, keepdims=True)
            out.append(vec[0].astype(np.float32))
        return np.array(out, dtype=np.float32)
```

- [ ] **Step 4: Rewire `src/tfmod_search_lib.py`:**

1. Delete the top-level `from sentence_transformers import SentenceTransformer` (line ~36).
2. `_MODEL_CACHE: dict[str, Any] = {}` (type loosened; add `Any` to typing imports; keep the docstring).
3. Inside `_get_sentence_transformer`, first line of the locked block: `from sentence_transformers import SentenceTransformer` (lazy). Fix the type annotation (`-> "SentenceTransformer"` string or `-> Any`).
4. Add after `_get_sentence_transformer`:

```python
def _resolve_backend(env: Mapping[str, str] | None = None) -> str:
    """Pick the embedding backend: TFMODSEARCH_EMBED_BACKEND = auto|torch|onnx."""
    if env is None:
        env = os.environ
    backend = env.get("TFMODSEARCH_EMBED_BACKEND", "auto").strip().lower() or "auto"
    if backend not in ("auto", "torch", "onnx"):
        raise ValueError(f"invalid TFMODSEARCH_EMBED_BACKEND {backend!r}: choose auto, torch, or onnx")
    if backend != "auto":
        return backend
    try:
        import sentence_transformers  # noqa: F401

        return "torch"
    except ImportError:
        pass
    from tfmod_onnx_encoder import resolve_onnx_model_dir

    if resolve_onnx_model_dir(project_root=_PROJECT_ROOT) is not None:
        return "onnx"
    raise RuntimeError(
        "No embedding backend available: install sentence-transformers (torch backend) "
        "or install tfmodsearch[onnx] and provide ONNX assets via TFMODSEARCH_ONNX_MODEL_DIR"
    )


class _TorchEncoder:
    """Adapter giving SentenceTransformer the minimal Encoder interface."""

    def __init__(self, model):
        self._model = model

    def encode(self, texts: list[str], prompt: str | None = None) -> "np.ndarray":
        return self._model.encode(
            texts, prompt=prompt, batch_size=64, convert_to_numpy=True, normalize_embeddings=True
        ).astype(np.float32, copy=False)


def _get_encoder(model_name: str, logger: logging.Logger):
    """Get a cached Encoder for the selected backend (torch or onnx)."""
    backend = _resolve_backend()
    cache_key = f"{backend}:{model_name}"
    if backend == "torch":
        if cache_key not in _MODEL_CACHE:
            _MODEL_CACHE[cache_key] = _TorchEncoder(_get_sentence_transformer(model_name, logger))
        return _MODEL_CACHE[cache_key]
    with _MODEL_LOCK:
        if cache_key not in _MODEL_CACHE:
            from tfmod_onnx_encoder import OnnxEncoder, resolve_onnx_model_dir

            model_dir = resolve_onnx_model_dir(project_root=_PROJECT_ROOT)
            if model_dir is None:
                raise RuntimeError(
                    "TFMODSEARCH_EMBED_BACKEND=onnx but no ONNX assets found: set "
                    "TFMODSEARCH_ONNX_MODEL_DIR to a dir containing model.onnx + tokenizer.json"
                )
            logger.info(f"Loading ONNX encoder from {model_dir}")
            _MODEL_CACHE[cache_key] = OnnxEncoder(model_dir)
        return _MODEL_CACHE[cache_key]
```

5. Index-build call site (~line 805): replace the `_get_sentence_transformer` + `model.encode(...)` pair with:

```python
    encoder = _get_encoder(model_name, logger)
    logger.info(f"Generating semantic embeddings for {len(docs)} documents (this may take a few minutes)...")
    doc_vecs = encoder.encode([d.text for d in docs])
```

6. Query call site in `hybrid_search` (~line 1012): replace the `_get_sentence_transformer` + locked `model.encode(...)` with:

```python
    encoder = _get_encoder(index.model_name, logger)
    with _MODEL_LOCK:
        q_vec = encoder.encode([q], prompt=query_instruction)[0]
```

(Keep the surrounding comments about the lock; note the ONNX construction path also takes `_MODEL_LOCK` — construction happens in `_get_encoder` BEFORE this `with` block, so there is no nested acquisition. Verify that by reading the final code.)

- [ ] **Step 5: pyproject** — add:

```toml
[project.optional-dependencies]
onnx = ["onnxruntime>=1.20", "tokenizers>=0.21"]
```

and append `"src/tfmod_onnx_encoder.py"` to `[tool.hatch.build.targets.wheel] packages`.

- [ ] **Step 6: Run tests** — `TFMODSEARCH_ONNX_TEST_ASSETS=<assets> pytest tests/integration/test_encoder_backends.py -v` → all pass; then `pytest tests/integration/ -q` (torch default path regression) → green.

- [ ] **Step 7: Commit** — `Add encoder backend seam: lazy sentence-transformers import, ONNX encoder module, TFMODSEARCH_EMBED_BACKEND selection`

---

### Task 2: Export script

**Files:**
- Create: `scripts/export_onnx_model.py` (NOT in the wheel)

- [ ] **Step 1:** Create the script:

```python
#!/usr/bin/env python3
"""Export intfloat/e5-small-v2 to ONNX for the tfmodsearch onnx backend.

Usage: python scripts/export_onnx_model.py <output_dir>

Requires optimum-onnx[onnxruntime] (plus torch) in the CURRENT environment --
these are export-time-only tools, deliberately not part of the package
metadata. The Dockerfile builder stage runs this; developers only need it when
regenerating assets. When sentence-transformers is also importable, a 5-query
parity check runs afterwards and fails the script below cosine 0.9999.
"""

import subprocess
import sys
from pathlib import Path

MODEL = "intfloat/e5-small-v2"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    subprocess.run(
        ["optimum-cli", "export", "onnx", "--model", MODEL, "--task", "feature-extraction", str(out)],
        check=True,
    )
    assert (out / "model.onnx").is_file() and (out / "tokenizer.json").is_file()
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer

        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from tfmod_onnx_encoder import OnnxEncoder

        queries = ["vpc", "s3 bucket encryption", "kubernetes cluster", "serverless function", "dns zone"]
        ref = SentenceTransformer(MODEL).encode(queries, convert_to_numpy=True, normalize_embeddings=True)
        cos = (ref.astype(np.float32) * OnnxEncoder(out).encode(queries)).sum(axis=1)
        print(f"parity: min cosine {cos.min():.8f}")
        assert cos.min() >= 0.9999, "ONNX export drifted from sentence-transformers"
    except ImportError:
        print("parity check skipped (sentence-transformers not installed)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2:** Smoke it against the existing spike assets env (re-export into a tmp dir is allowed but slow; acceptable to verify only `--help`/arg error path locally plus rely on the Docker build). Commit: `Add ONNX export script for build-time asset generation`

---

### Task 3: Golden set gate on ONNX (THE gate)

- [ ] Run: `TFMODSEARCH_EMBED_BACKEND=onnx TFMODSEARCH_ONNX_MODEL_DIR=<assets> pytest tests/integration/test_all_modules_searchable.py -v` — **must be 100% (169 passed)** against the untouched index pickle. If ANY test fails: STOP the release, record the failing queries and scores in the spec, report.
- [ ] Also run the model-comparison suite guard on the default path: `pytest tests/integration/test_all_modules_searchable.py -q` (no env) → green, proving the seam did not disturb torch.
- [ ] No commit (nothing changes); paste both summaries into the task report.

---

### Task 4: Dockerfile — ONNX runtime image

**Files:**
- Modify: `Dockerfile`

- [ ] **Step 1:** Rewrite (keep the top comment block, updating the offline story: HF env vars are gone because nothing imports HF at runtime; the ONNX assets are baked in). New structure:

```dockerfile
# --- builder ---
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    NLTK_DATA=/opt/nltk_data

WORKDIR /build

# CPU-only torch first so the export tooling below does not pull the CUDA wheel.
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Export tooling (builder-only; version pinned for reproducible exports) + nltk for punkt.
RUN pip install "optimum-onnx[onnxruntime]==<PIN>" "nltk>=3.9.4" hatchling build

COPY pyproject.toml README.md ./
COPY src/ src/
COPY config.yaml ./
COPY model/ model/
COPY modules/ modules/
COPY scripts/ scripts/

# Export the embedding model to ONNX (this is what replaces torch at runtime).
RUN python scripts/export_onnx_model.py /opt/onnx/e5-small-v2

# Build the wheel (contains src modules + index + docs corpus + config).
RUN python -m build --wheel --outdir /build/dist

# punkt_tab fetch (same gotchas as before: assert success, NLTK_DATA already set).
RUN python -c "import nltk, sys; sys.exit(0 if nltk.download('punkt_tab', download_dir='/opt/nltk_data') else 1)"
RUN test -d /opt/nltk_data/tokenizers/punkt_tab

# --- runtime ---
FROM python:3.12-slim

RUN useradd --create-home --home-dir /home/app app

# ONNX backend only: no torch, no sentence-transformers, no HF cache.
ENV TFMODSEARCH_EMBED_BACKEND=onnx \
    TFMODSEARCH_ONNX_MODEL_DIR=/opt/onnx/e5-small-v2 \
    NLTK_DATA=/opt/nltk_data \
    PIP_NO_CACHE_DIR=1

# Explicit torch-free dependency list: core deps from pyproject minus
# sentence-transformers, plus the [onnx] extra. A documented duplication --
# the release gate (offline warmup + real queries) exercises every import.
RUN pip install "fastmcp>=3.2.0,<4" "nltk>=3.9.4" "numpy>=2.4.1" "pyyaml>=6.0.3" \
    "rank-bm25>=0.2.2" "onnxruntime>=1.20" "tokenizers>=0.21"

COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-deps /tmp/*.whl && rm /tmp/*.whl

COPY --from=builder --chown=app:app /opt/onnx /opt/onnx
COPY --from=builder --chown=app:app /opt/nltk_data /opt/nltk_data

# (keep the existing nltk_data/logs writable-dir quirk RUN, and the
#  pip/setuptools/__pycache__ cleanup RUN, both unchanged from 0.18.0)

USER app
WORKDIR /home/app
EXPOSE 8765
ENTRYPOINT ["tfmodsearch"]
```

Resolve `<PIN>` to the version installed in the spike venv (`uv pip list | grep optimum` in `/private/tmp/.../scratchpad/onnx-export-venv`). Note the console script `tfmodsearch` comes from the wheel (`tfmod_entry:main`) — no separate copy needed. Check whether pip warns about the entry point installing fine with --no-deps (it does; scripts are generated from the wheel metadata).

- [ ] **Step 2:** Build and measure: `docker build -t tfmodsearch:0.19.0-rc .` then `docker images tfmodsearch:0.19.0-rc --format '{{.Size}}'`. Expected ≤ 700 MB (target ~550-650).
- [ ] **Step 3:** Verify both modes: `docker run --network none -i --rm tfmodsearch:0.19.0-rc --warmup` (expected: 55 modules, 3 results — this proves the whole ONNX path offline); HTTP mode on port 18766 + `/health` + an SDK `search_modules` call returning `s3-bucket` (same snippet as the 0.18.0 gate, port changed). Also spot-check 3 queries via a stdio MCP session if convenient.
- [ ] **Step 4:** Commit: `Docker image ships the ONNX encode backend instead of torch`

---

### Task 5: Docs + version bump 0.19.0

**Files:** `pyproject.toml`, both plugin manifests, `DEFAULT_IMAGE` in the launcher, `PROXY_PACKAGE_SPEC` stays `>=0.18.0` (do NOT bump — 0.18.0 proxy still works), `docker-compose.yml`, README current-release tags, `docs/docker-container-support.md`, `CHANGELOG.md`, `config.yaml` comments if they mention the model loading.

- [ ] Version sweep: `grep -rn "0\.18\.0" pyproject.toml plugins/ README.md docker-compose.yml docs/docker-container-support.md` — bump current-release occurrences to 0.19.0 EXCEPT `PROXY_PACKAGE_SPEC = "tfmodsearch>=0.18.0"` (a floor, not a current-release tag) and historical "since 0.18.0" mentions.
- [ ] README: in the Docker section, note the image now runs the ONNX backend (smaller, faster queries, same results — cite the parity numbers); add a short "Embedding backends" paragraph under Configuration documenting `TFMODSEARCH_EMBED_BACKEND` (auto/torch/onnx) and `TFMODSEARCH_ONNX_MODEL_DIR`, stating uvx/PyPI installs keep torch by default and `[onnx]` is opt-in.
- [ ] CHANGELOG 0.19.0 entry (existing format): Added (onnx backend, extra, export script, image switch with measured sizes), Unchanged (PyPI deps, index untouched + parity numbers, golden set 100% on both backends, transports/tools).
- [ ] Full suite: `pytest tests/ -q` → green. Commit: `Bump version to 0.19.0; document the ONNX encode backend`

---

### Task 6: Gate + release (orchestrator)

- [ ] Full suite (default backend) green; golden set on ONNX 100% (Task 3 re-run on the final tree).
- [ ] Rebuild rc from final tree; offline warmup + HTTP SDK call + size recorded in CHANGELOG.
- [ ] Opus review (full diff vs spec) + blind persona review (search-quality + image/ops focus).
- [ ] Push, PR, CI, Copilot threads, merge, tag `v0.19.0`, PyPI/GHCR verification, GitHub Release, upgrade the local daemon, live smoke.
