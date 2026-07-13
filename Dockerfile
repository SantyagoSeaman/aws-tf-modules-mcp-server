# TFModSearch MCP server — stdio-in-container.
#
# `docker run -i --rm <image>` speaks the same stdio JSON-RPC as `tfmodsearch` (uvx). Never pass
# `-t`/`--tty`: a pseudo-TTY corrupts the stdio byte stream.
#
# Every asset that would otherwise trigger a runtime network call is baked in at build time:
# the intfloat/e5-small-v2 embedding model, the NLTK punkt_tab tokenizer, the prebuilt search
# index, and the module docs corpus (the last two are already force-included in the wheel).
# Runtime env below (HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE/NLTK_DATA) enforces zero network calls;
# verify with `docker run --network none -i --rm <image> --warmup`.

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
COPY --from=builder /opt/hf /opt/hf
COPY --from=builder /opt/nltk_data /opt/nltk_data

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
    chown -R app:app /opt/hf /opt/nltk_data \
      /usr/local/lib/python3.12/site-packages/nltk_data /usr/local/lib/python3.12/logs

# pip/setuptools and bytecode caches aren't needed at runtime; trim what's cheap to trim (the
# CPU-only torch wheel itself is the size floor here — a few hundred MB is not on the table
# without swapping the embedding backend, which is out of scope).
RUN rm -rf /usr/local/lib/python3.12/site-packages/pip \
           /usr/local/lib/python3.12/site-packages/setuptools \
           /usr/local/lib/python3.12/site-packages/pip-*.dist-info \
           /usr/local/lib/python3.12/site-packages/setuptools-*.dist-info && \
    find /usr/local/lib/python3.12/site-packages -type d -name "__pycache__" -exec rm -rf {} +

USER app
WORKDIR /home/app

ENTRYPOINT ["tfmodsearch"]
