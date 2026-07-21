# TFModSearch MCP server — stdio-in-container, or a shared HTTP daemon.
#
# `docker run -i --rm <image>` speaks the same stdio JSON-RPC as `tfmodsearch` (uvx). Never pass
# `-t`/`--tty`: a pseudo-TTY corrupts the stdio byte stream. stdio stays the default and is what
# runs when no arguments are given.
#
# The same image also serves `--transport http` as a shared daemon: one long-lived instance,
# one embedding-model load, many clients over http://host:8765/mcp (see docker-compose.yml and
# README's "Shared HTTP instance" section for the run recipe).
#
# Since 0.19.0 this image runs the ONNX encode backend instead of torch/sentence-transformers:
# the embedding model is exported to ONNX at build time and queried with onnxruntime + tokenizers,
# numerically interchangeable with the torch path (min cosine 0.99999988 across the full 162-query
# golden set — see docs/superpowers/specs/2026-07-15-onnx-encode-backend-design.md). There is no
# HF cache and no HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE env at runtime: nothing imports HuggingFace
# code at runtime, so those knobs no longer apply. Every asset that would otherwise trigger a
# runtime network call is still baked in at build time: the ONNX model + tokenizer, the NLTK
# punkt_tab tokenizer, the prebuilt search index, and the module docs corpus (the last two are
# already force-included in the wheel). Verify with `docker run --network none -i --rm <image>
# --warmup`. There are no networked TOOLS (grep_module_docs was removed in 0.27.0); the only
# network use anywhere in the server is the opt-in daily PyPI update check in HTTP mode.

# --- builder ---
# --platform=$BUILDPLATFORM: run the builder natively even when cross-building the
# arm64 image. Everything copied out of it is architecture-independent (pure-python
# wheel, model.onnx, nltk_data), and the torch->ONNX export would be 10-30x slower
# under QEMU -- and would produce a separately exported, never parity-checked model
# per architecture. Exporting once natively gives both images identical assets.
FROM --platform=$BUILDPLATFORM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    NLTK_DATA=/opt/nltk_data

WORKDIR /build

# CPU-only torch first, so the ONNX export tooling below (which needs torch to trace the model)
# does not pull the CUDA wheel (multi-GB vs a few hundred MB). Builder-only: this layer is not
# copied to the runtime stage.
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Export tooling (builder-only; version pinned for reproducible exports) + nltk for punkt_tab,
# plus hatchling/build to build the wheel in this same stage.
RUN pip install "optimum-onnx[onnxruntime]==0.1.0" "nltk>=3.9.4" hatchling build

COPY pyproject.toml README.md ./
COPY src/ src/
COPY config.yaml ./
COPY model/ model/
COPY modules/ modules/
COPY scripts/ scripts/

# Export the embedding model to ONNX -- this is what replaces torch at runtime. The parity check
# inside the script is skipped here (sentence-transformers is not installed in this stage); parity
# is already gated by the release process against the real golden set (see the spec).
RUN python scripts/export_onnx_model.py /opt/onnx/e5-small-v2

# Build the wheel (contains src modules + index + docs corpus + config). --no-isolation reuses the
# hatchling/build already installed above instead of re-downloading a build venv.
RUN python -m build --wheel --outdir /build/dist --no-isolation

# Pre-fetch only punkt_tab (a few MB) into a slim nltk_data dir, not the repo's full nltk_data/.
# nltk.download() returns False (not an exception) on failure, so assert it explicitly —
# NLTK_DATA must already be set above or nltk's path-security sandbox silently rejects the
# write target ("Security Violation ... Unauthorized path") and the RUN step exits 0 anyway.
RUN python -c "import nltk, sys; sys.exit(0 if nltk.download('punkt_tab', download_dir='/opt/nltk_data') else 1)"
RUN test -d /opt/nltk_data/tokenizers/punkt_tab

# --- runtime ---
FROM python:3.12-slim

RUN useradd --create-home --home-dir /home/app app

# ONNX backend only: no torch, no sentence-transformers, no HF cache, no HF offline env
# (nothing imports HuggingFace code at runtime anymore).
ENV TFMODSEARCH_EMBED_BACKEND=onnx \
    TFMODSEARCH_ONNX_MODEL_DIR=/opt/onnx/e5-small-v2 \
    NLTK_DATA=/opt/nltk_data \
    PIP_NO_CACHE_DIR=1

# Explicit torch-free dependency list: core deps from pyproject minus sentence-transformers, plus
# the [onnx] extra (onnxruntime, tokenizers). A documented duplication of pyproject -- the release
# gate (offline warmup + real queries) exercises every import so drift cannot silently ship.
RUN pip install "fastmcp>=3.2.0,<4" "nltk>=3.9.4" "numpy>=2.4.1" "pyyaml>=6.0.3" \
    "rank-bm25>=0.2.2" "onnxruntime>=1.20" "tokenizers>=0.21"

COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-deps /tmp/*.whl && rm /tmp/*.whl

COPY --from=builder --chown=app:app /opt/onnx /opt/onnx
COPY --from=builder --chown=app:app /opt/nltk_data /opt/nltk_data

# Two of the server's paths are computed relative to tfmod_search_lib.py's own location
# (src/tfmod_search_lib.py), which in the wheel-installed layout sits directly in site-packages
# rather than in a src/ subdir as in development — so both land one level up from where they do
# in dev, inside the root-owned Python install tree:
#   - initialize_nltk() always mkdir(exist_ok=True)s <project_root>/nltk_data and prepends it to
#     nltk.data.path, regardless of NLTK_DATA (real data lives at NLTK_DATA=/opt/nltk_data, found
#     next in the search path — this one stays empty).
#   - setup_logging() writes startup.log/mcp_server.log under <site-packages>/../logs.
# Pre-create both, owned by the runtime user, instead of patching the app's path resolution.
# /home/app/.cache is created app-owned IN THE IMAGE so that a fresh named volume
# mounted over it (docker-compose.yml) initializes with this ownership instead of
# root:root -- Docker copies content AND ownership from the image only when the
# volume is empty on first mount. Historically backed grep_module_docs's registry-doc
# cache (found live on 0.19.0); that tool was removed in 0.27.0, so this directory is
# currently unused, but is kept app-owned for forward compatibility with any future
# on-disk cache.
RUN mkdir -p /usr/local/lib/python3.12/site-packages/nltk_data /usr/local/lib/python3.12/logs \
             /home/app/.cache && \
    chown app:app /usr/local/lib/python3.12/site-packages/nltk_data /usr/local/lib/python3.12/logs \
                  /home/app/.cache

# pip/setuptools and bytecode caches aren't needed at runtime; trim what's cheap to trim.
RUN rm -rf /usr/local/lib/python3.12/site-packages/pip \
           /usr/local/lib/python3.12/site-packages/setuptools \
           /usr/local/lib/python3.12/site-packages/pip-*.dist-info \
           /usr/local/lib/python3.12/site-packages/setuptools-*.dist-info && \
    find /usr/local/lib/python3.12/site-packages -type d -name "__pycache__" -exec rm -rf {} +

USER app
WORKDIR /home/app

# HTTP mode only (docs): `docker run -d -p 127.0.0.1:8765:8765 <image> --transport http --host 0.0.0.0`.
# stdio mode ignores this. EXPOSE is documentation, not a port publication.
EXPOSE 8765

ENTRYPOINT ["tfmodsearch"]
