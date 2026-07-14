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
# Every asset that would otherwise trigger a runtime network call is baked in at build time:
# the intfloat/e5-small-v2 embedding model, the NLTK punkt_tab tokenizer, the prebuilt search
# index, and the module docs corpus (the last two are already force-included in the wheel).
# Runtime env below (HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE/NLTK_DATA) makes search_modules/
# get_module/modules_list fully offline; verify with `docker run --network none -i --rm <image>
# --warmup`. grep_module_docs is the one tool designed to reach the live Terraform Registry and
# still needs real network when called -- that is by design, not a gap in this offline setup.

# --- builder ---
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/hf \
    NLTK_DATA=/opt/nltk_data

WORKDIR /build

# CPU-only torch first, so sentence-transformers reuses it instead of pulling the CUDA wheel
# (multi-GB vs a few hundred MB — the single biggest image-size lever).
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY pyproject.toml README.md ./
COPY src/ src/
COPY config.yaml ./
COPY model/ model/
COPY modules/ modules/

RUN pip install .

# The CPU torch wheel ships dead weight that inference never touches: its own test
# suite and C++ headers. NOTE: torch/bin is NOT dead weight -- torch/__init__.py
# unconditionally resolves torch/bin/torch_shm_manager at import time (shared-memory
# manager init) and raises RuntimeError if it is missing, so it must stay. Verified
# safe by the release gate (offline --warmup + a real search_modules call exercise
# the full encode path).
RUN rm -rf /usr/local/lib/python3.12/site-packages/torch/test \
           /usr/local/lib/python3.12/site-packages/torch/include

# Pre-download the embedding model into the HF cache baked into the image.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/e5-small-v2')"

# Pre-fetch only punkt_tab (a few MB) into a slim nltk_data dir, not the repo's full nltk_data/.
# nltk.download() returns False (not an exception) on failure, so assert it explicitly —
# NLTK_DATA must already be set above or nltk's path-security sandbox silently rejects the
# write target ("Security Violation ... Unauthorized path") and the RUN step exits 0 anyway.
RUN python -c "import nltk, sys; sys.exit(0 if nltk.download('punkt_tab', download_dir='/opt/nltk_data') else 1)"
RUN test -d /opt/nltk_data/tokenizers/punkt_tab

# --- runtime ---
FROM python:3.12-slim

RUN useradd --create-home --home-dir /home/app app

ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    HF_HOME=/opt/hf \
    NLTK_DATA=/opt/nltk_data

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/tfmodsearch /usr/local/bin/tfmodsearch
COPY --from=builder --chown=app:app /opt/hf /opt/hf
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
RUN mkdir -p /usr/local/lib/python3.12/site-packages/nltk_data /usr/local/lib/python3.12/logs && \
    chown app:app /usr/local/lib/python3.12/site-packages/nltk_data /usr/local/lib/python3.12/logs

# pip/setuptools and bytecode caches aren't needed at runtime; trim what's cheap to trim (the
# CPU-only torch wheel, now stripped of its test/include dirs above, is still the size floor
# here — the remainder is not on the table without swapping the embedding backend, which is out
# of scope).
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
