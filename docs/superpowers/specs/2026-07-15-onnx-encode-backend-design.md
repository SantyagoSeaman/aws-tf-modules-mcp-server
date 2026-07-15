# 0.19.0 Design: ONNX Encode Backend (Tier 2 Image Slimming)

**Date**: 2026-07-15
**Status**: Spike validated — implementation authorized, release gated on the golden set
**Target release**: 0.19.0 (minor)
**Predecessor**: Tier 2 of `2026-07-14-proxy-and-image-slim-design.md` (deferred there)

## Spike results (measured 2026-07-15, before this spec)

e5-small-v2 exported to ONNX fp32 via `optimum-cli export onnx --task feature-extraction`
(optimum-onnx, torch only at export time). Custom inference path: `tokenizers` tokenizer
(truncation at the ST `max_seq_length` of 512) → `onnxruntime` CPU session → attention-masked
mean pooling → L2 normalization — replicating exactly what sentence-transformers does for this
model (its module stack is Transformer → Pooling(mean) → Normalize; the search lib passes
`query_instruction=None` by default, no e5 prefixes are used anywhere today).

Against all 162 golden queries (54 modules × name/keyword/natural-language):

| Metric | Value |
|---|---|
| cosine(ST, ONNX) | min **0.99999988**, mean 1.00000000 |
| max abs elementwise diff | **4.06e-07** |
| encode wall time (CPU) | ST batch 2.34 s vs ONNX one-at-a-time loop **0.42 s** (~5.5x faster) |

Conclusion: numerically interchangeable at float32 precision; the pickled index embeddings
(torch-produced) can be queried by ONNX vectors without an index rebuild — the standing
index-drift policy is respected by construction. Bonus: query latency improves.

## Problem

The Docker image is 1.42 GB because inference rides on torch (580 MB) plus its dependency
train (scipy 120 + sklearn 40 + sympy 30 + networkx 9 via sentence-transformers/torch).
`uvx tfmodsearch` first-run pays the same in download time. The model itself needs none of
that at inference time: it is a 33M-parameter encoder that onnxruntime (~40-60 MB) runs
faster than torch does.

## Design

### Encoder abstraction (`src/tfmod_search_lib.py`)

A minimal backend seam at the two existing `encode()` call sites (index build + query):

```python
class Encoder(Protocol):
    def encode(self, texts: list[str], prompt: str | None = None) -> np.ndarray: ...
    # returns (N, D) float32, L2-normalized
```

- `_get_encoder(model_name, logger)` replaces direct `_get_sentence_transformer` usage at
  call sites and dispatches on `TFMODSEARCH_EMBED_BACKEND`:
  - `auto` (default): torch backend if `sentence_transformers` imports, else ONNX backend if
    ONNX assets are found, else a clear RuntimeError naming both options.
  - `torch`: current behavior, unchanged (ST model, `prompt=` passthrough).
  - `onnx`: the new `OnnxEncoder`.
- **Lazy ST import**: `from sentence_transformers import SentenceTransformer` moves from
  module top-level into the torch loader, so the lib imports cleanly in an image that does
  not ship torch. (NLTK/BM25/numpy stay top-level — present in both variants.)
- `_MODEL_CACHE`/`_MODEL_LOCK` semantics preserved for both backends (construction and
  encode serialized exactly as today; ORT run() is thread-safe but keeping one lock keeps
  the concurrency story identical to 0.16.0).
- `prompt` semantics: ST prepends the prompt string to each text; `OnnxEncoder` replicates
  with `f"{prompt}{text}"` when prompt is not None (config default is null — low traffic,
  still tested).

### `src/tfmod_onnx_encoder.py` (new, in the wheel)

- `OnnxEncoder(model_dir: Path)`: loads `tokenizer.json` (tokenizers lib, truncation 512)
  and `model.onnx` (onnxruntime, CPUExecutionProvider). `encode()` runs one text at a time
  (spike shows the loop already beats ST batch; no padding complexity), attention-masked
  mean pooling, L2 normalize, float32.
- Asset discovery (`resolve_onnx_model_dir()`): `TFMODSEARCH_ONNX_MODEL_DIR` env var if
  set, else `<project_root>/onnx/e5-small-v2` (covers the Docker layout, where assets are
  baked next to the wheel-installed code), else None.
- Dependencies: `onnxruntime` + `tokenizers`, shipped as a new optional extra
  `tfmodsearch[onnx]`. **Core dependencies are unchanged** — `uvx tfmodsearch` keeps
  torch/ST as today (flipping the PyPI default is a possible later release, after the
  Docker variant bakes in production).

### Export tooling (`scripts/export_onnx_model.py`)

Dev/build-time helper (NOT in the wheel): exports `intfloat/e5-small-v2` to a target dir via
optimum-onnx and prints the parity numbers against ST when both are installed. Used by the
Dockerfile builder stage and by developers regenerating assets. Pinned in the Dockerfile,
not in pyproject (torch-side tooling stays out of the package metadata).

### Docker image switches to ONNX

- **Builder stage** (keeps torch): installs the project as today, additionally installs
  pinned `optimum-onnx[onnxruntime]`, exports `/opt/onnx/e5-small-v2` (model.onnx +
  tokenizer.json + configs), and pre-fetches NLTK punkt_tab as today. The HF model cache
  (`/opt/hf`) is no longer copied to runtime (ONNX replaces it).
- **Runtime stage**: installs the built wheel with `--no-deps` plus an explicit dependency
  list (core deps minus `sentence-transformers`, plus `onnxruntime` and `tokenizers`).
  The explicit list is a documented duplication of pyproject, guarded by the release gate
  (offline warmup + real query exercise every import). Sets
  `TFMODSEARCH_EMBED_BACKEND=onnx` and `TFMODSEARCH_ONNX_MODEL_DIR=/opt/onnx/e5-small-v2`.
  `HF_HUB_OFFLINE`/`TRANSFORMERS_OFFLINE`/`HF_HOME` env vars drop (nothing imports HF at
  runtime anymore).
- Expected size: base ~145 + numpy ~54 + onnxruntime ~50 + tokenizers ~10 + fastmcp/nltk/
  misc ~80 + model.onnx 133 + punkt 15 + index/docs ~15 → **~500-650 MB uncompressed,
  ~200-300 MB pull** (vs 1.42 GB / ~450 MB today). Exact numbers measured at the gate and
  recorded in the CHANGELOG.

### What does NOT change

- PyPI/uvx install: same dependency set, same torch default, byte-identical behavior.
- The pickled index: NOT rebuilt (drift policy). ONNX queries hit torch-built doc vectors —
  the spike proves this is sound at 4e-07 precision.
- stdio/HTTP transports, proxy mode, update check, plugin, tools, index format.
- Embedding model choice (e5-small-v2) and search weights.

## Quality gate (hard, blocks the release)

1. **Golden set on ONNX**: `TFMODSEARCH_EMBED_BACKEND=onnx pytest
   tests/integration/test_all_modules_searchable.py` — must be 100% (169 tests), using the
   existing index pickle and local ONNX assets.
2. **Full suite on the default backend** — unchanged green (838+).
3. **Image gate**: `--network none --warmup` + real `search_modules` over HTTP against the
   rc image; the same golden-set run inside the image variant is a stretch goal (a
   container-exec run of the searchable tests) — at minimum the warmup + 3 spot queries.
4. Parity unit test (skipif assets/deps absent) pinned at cosine ≥ 0.9999 per query on a
   10-query sample, so future dependency bumps surface drift.

## Testing

- `tests/integration/test_encoder_backends.py` (new): backend selection matrix (env unset /
  torch / onnx / auto-fallback / error case with neither available — mocked imports);
  OnnxEncoder unit behavior (normalization, float32, prompt prepend, truncation) — skipif
  onnxruntime or assets missing; the 10-query parity test vs ST.
- Golden set via env switch (gate item 1) — run locally/release gate, not added to the CI
  matrix in this release (CI has no ONNX assets; a cached-assets CI job is a follow-up).
- Existing suite guards the torch path and the lazy-import refactor everywhere else.

## Risks and mitigations

- **Explicit runtime dep list in Dockerfile drifts from pyproject** → release-gate warmup +
  query exercises every import; comment in both files cross-referencing.
- **optimum-onnx export changes across versions** → pinned version in the Dockerfile;
  parity unit test catches semantic drift when assets are regenerated.
- **onnxruntime wheel availability for linux/arm64 py3.12** → verified present on PyPI
  (ORT ships manylinux aarch64 wheels); the GHCR arm64 leg builds under QEMU as today.
- **ST `prompt` semantics mismatch** → replicated and unit-tested (prefix concatenation).

## Rollout

Standard release process per CLAUDE.md: version bump list, Sonnet subagent implementation
(sequential, TDD), Opus review + blind persona review (search quality + image/ops focus),
PR, CI, Copilot threads, merge, tag, PyPI/GHCR verification, local daemon upgrade.
