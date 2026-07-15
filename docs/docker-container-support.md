# Feature spec — Run TFModSearch as a Docker container (stdio-in-container)

Status: implemented, shipped in 0.15.0 (see section 8 for implementation notes and deviations
from the skeleton below); the shared HTTP daemon mode described in section 9 shipped separately
in 0.16.0 (see `docs/superpowers/specs/2026-07-14-http-transport-design.md`); the image switched
its encode backend from torch/sentence-transformers to ONNX in 0.19.0, which supersedes the
torch/HF-cache internals described in sections 4.2-4.5 for the current image — see section 10
and `docs/superpowers/specs/2026-07-15-onnx-encode-backend-design.md`.
Audience: maintainers of this repository (GitHub: `SantyagoSeaman/tfmodsearch`)

---

## 1. Problem / motivation

**This is an additive distribution feature, not a fix for a specific bug.** A concurrent-spawn
handshake-timeout failure was observed during testing (details in the Appendix, kept for
context/evidence), but that is not what this feature is scoped to solve — it should be evaluated
independently, e.g. via lazy/async model loading that answers the MCP handshake before the
embedding model finishes loading. **Do not use "fixes the concurrent-timeout bug" as the
acceptance bar for this feature; do not chase a specific cold-start-time target as evidence of
success.**

The actual goal: give TFModSearch an **official Docker image** as a second, opt-in distribution
channel alongside `uvx tfmodsearch`, for users/environments that prefer or require it:

- Air-gapped / offline environments where an image with the model, index, and NLTK data baked in
  and zero runtime network calls is a hard requirement, not a nice-to-have.
- CI runners or sandboxes without a Python/`uv` toolchain but with Docker available.
- Users who standardize MCP server deployment on containers (matches the pattern used by
  HashiCorp's `terraform-mcp-server`, launched via `docker run -i --rm
  hashicorp/terraform-mcp-server` — stdio-in-container).

Non-requirement: this does NOT need to be faster than `uvx`, and does NOT replace it — `uvx` stays
the documented default (see §4.6). Docker is an opt-in alternative, evaluated on its own merits
(offline guarantee, portability, no local Python toolchain needed), not on cold-start speed.

## 2. Goal

Ship an official Docker image so the server can be launched as:

```jsonc
// MCP client config (plugin .claude-plugin/plugin.json → mcpServers)
{ "command": "docker", "args": ["run", "-i", "--rm", "ghcr.io/santyagoseaman/tfmodsearch:<tag>"] }
```

with the embedding model, prebuilt index, and NLTK data **baked into the image** and **zero
runtime network calls**, giving fast, deterministic startup that survives concurrent spawns.

## 3. Non-goals (read carefully)

- **Do NOT change the transport.** Stay stdio. `docker run -i` IS stdio: the container's
  stdin/stdout is the JSON-RPC pipe (`-i` keeps stdin open). Do NOT add HTTP/SSE/streamable-http.
  The existing `app.run(transport="stdio")` (`src/tfmod_mcp_server.py:1889`) runs unchanged inside
  the container.
- **Do NOT** rebuild the index at runtime, change search behaviour, tool signatures, or the
  catalog contents.
- **Do NOT** remove or break the existing `uvx tfmodsearch` launch path — Docker is an added
  option, not a replacement.
- **Do NOT treat the concurrent-spawn handshake-timeout observation (Appendix) as this feature's
  problem to solve.** It's background evidence for why a Docker path is generally useful, not an
  acceptance criterion — don't optimize the image or the workflow chasing that specific number.

## 4. Design

### 4.1 Entrypoint / transport
- Container `ENTRYPOINT` runs the existing console script `tfmodsearch`
  (`[project.scripts] tfmodsearch = "tfmod_mcp_server:main"`), which starts the stdio MCP server.
- Client invokes `docker run -i --rm <image>`. **Never pass `-t`/`--tty`** — a TTY corrupts the
  JSON-RPC byte stream. Only `-i`.
- CLI flags still pass through (e.g. `docker run -i --rm <image> --warmup`) since they are argv to
  `tfmodsearch`.

### 4.2 Bake in every asset that currently triggers a network call or slow resolve
1. **Embedding model `intfloat/e5-small-v2`** — pre-download into the image's HF cache at BUILD
   time (a build step that instantiates `SentenceTransformer("intfloat/e5-small-v2")` so the
   weights land in `~/.cache/huggingface` / `HF_HOME`), then set at runtime:
   `ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`. Runtime must never reach huggingface.co.
2. **Search index `model/tfmod_e5_small_index.pkl`** (~4.3 MB) — already force-included into the
   wheel (`pyproject.toml` `[tool.hatch.build.targets.wheel.force-include]`). Confirm it lands in
   site-packages and `resolve_index_path` finds it in-container. No runtime rebuild.
3. **NLTK data (`punkt_tab`)** — bake it in and point `initialize_nltk()` at it so it does NOT
   call `nltk.download` at runtime. Set `ENV NLTK_DATA=<path>` and/or ensure the bundled
   `nltk_data/` dir (`_NLTK_DATA_DIR = _PROJECT_ROOT / "nltk_data"`, `src/tfmod_search_lib.py:57`)
   is present at that project-root location in the image. **Bundle only `punkt_tab`** (a few MB),
   not the repo's full 64 MB `nltk_data/`.
4. **`modules/terraform-aws-modules` corpus + `config.yaml`** — already force-included in the
   wheel; confirm present at runtime.

### 4.3 Image
- Base: `python:3.12-slim` (repo `.python-version` = 3.12; classifiers cover 3.12/3.13).
- **CPU-only torch is mandatory** — `sentence-transformers` pulls `torch`; the default wheel is
  multi-GB (CUDA). Install the CPU wheel first so sentence-transformers reuses it:
  `pip install torch --index-url https://download.pytorch.org/whl/cpu`. This is the single biggest
  image-size lever (multi-GB → a few hundred MB).
- Multi-stage build: a builder stage installs deps + pre-downloads the model; the final stage
  copies site-packages + HF cache + nltk data. Run as a **non-root** user.
- Install the package from the built wheel (`dist/`) or `pip install .`.
- Runtime deps to satisfy (`pyproject.toml`): `fastmcp>=3.2,<4`, `nltk>=3.9.4`, `numpy>=2.4.1`,
  `pyyaml>=6.0.3`, `rank-bm25>=0.2.2`, `sentence-transformers>=5.2.0`.

### 4.4 Env baked into the image
```
ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    NLTK_DATA=/app/nltk_data \
    HF_HOME=/app/.cache/huggingface
```
(adjust paths to wherever assets are copied).

### 4.5 Publish (CI)
- GitHub Actions workflow: on git tag / release, `docker buildx` build + push to **GHCR**
  (`ghcr.io/santyagoseaman/tfmodsearch:<version>` and `:latest`).
- **v1 scope was `linux/amd64` only**; `linux/arm64` added in 0.15.1 once Apple-Silicon demand was
  confirmed (the maintainer's own dev machine). `docker/setup-qemu-action` + `platforms:
  linux/amd64,linux/arm64` on `docker/build-push-action` — QEMU emulates the arm64 leg on the
  amd64 GitHub-hosted runner (roughly doubles build time vs. amd64-only), which was an accepted
  cost once the platform was actually needed rather than speculative.
- Tag the image with the same version as the PyPI package/plugin.
- **GHCR package visibility**: images pushed via `GITHUB_TOKEN` from a public repo may still land
  as a **private** package on first push. After the first tag-triggered publish, check
  `github.com/SantyagoSeaman?tab=packages` and set the `tfmodsearch` package visibility to
  **public** (one-time manual step, or via the GitHub API) — otherwise `docker pull` fails for
  external users with an auth error that looks like a broken image.
- **Image signing** — not required for v1, but worth a follow-up once the image is public: this
  repo already has an OIDC/Trusted-Publishing pattern for PyPI and a Scorecard-driven security
  posture (SHA-pinned Actions); `cosign sign --keyless` in the publish workflow would extend that
  same posture to the image. Track as a fast-follow, not a blocker.

### 4.6 Plugin config — dual-mode via a bundled launcher (uvx default, Docker opt-in)

Requirement: **one plugin** that defaults to the existing local `uvx` launch and *optionally*
uses Docker — no second plugin, no hard swap. A plugin `mcpServers` entry has a single
`command`/`args`, so point it at a small launcher script bundled in the plugin that selects the
backend by an env flag.

`plugins/tfmod-search/.claude-plugin/plugin.json`:
```json
"mcpServers": {
  "tfmod-search": {
    "command": "python3",
    "args": ["${CLAUDE_PLUGIN_ROOT}/bin/tfmodsearch_launch.py"]
  }
}
```
(`${CLAUDE_PLUGIN_ROOT}` = plugin install dir, interpolated by Claude Code per the plugin spec.
Keep the server key `tfmod-search` unchanged — the tool-name prefix
`mcp__plugin_tfmod-search_tfmod-search__*` depends on it.)

**Codex plugin scope note (verified during implementation):** Codex CLI does not reliably
interpolate `${CLAUDE_PLUGIN_ROOT}` in a plugin's `.mcp.json` (open upstream issue), and relative
paths there resolve against the Codex process's cwd, not the plugin root — there is currently no
portable way to point the Codex plugin's `mcp.json` at a bundled launcher script. **Scope
decision: the dual-mode launcher applies to the Claude Code plugin only.** The Codex plugin's
`codex/mcp.json` stays `{"command": "uvx", "args": ["tfmodsearch"]}` unchanged (uvx-only for now);
revisit if/when Codex CLI fixes plugin-root interpolation.

`plugins/tfmod-search/bin/tfmodsearch_launch.py` (ship in the plugin):
```python
#!/usr/bin/env python3
import os, sys
if os.environ.get("TFMODSEARCH_DOCKER", "0") != "0":
    img = os.environ.get("TFMODSEARCH_IMAGE", "ghcr.io/santyagoseaman/tfmodsearch:0.19.0")
    os.execvp("docker", ["docker", "run", "-i", "--rm", img])   # opt-in
else:
    os.execvp("uvx", ["uvx", "tfmodsearch", *sys.argv[1:]])      # DEFAULT (local, unchanged)
```
Behaviour: env unset → `uvx tfmodsearch` (current default, nobody notices). `TFMODSEARCH_DOCKER=1`
→ `docker run -i --rm <image>` (tag overridable via `TFMODSEARCH_IMAGE`). `os.execvp` **replaces**
the launcher process so the stdio pipe is inherited transparently (no extra layer between client
and server).

- **Opt-in mechanism (user side):** set `TFMODSEARCH_DOCKER=1` in `~/.claude/settings.json` `env`
  block, or export it in the shell before launching Claude Code. Default (unset) = local uvx.
- **Pin an explicit image tag, not `:latest`**, in the default (reproducibility — mirrors the
  earlier "unpinned `uvx tfmodsearch` served a stale build" lesson).
- **Optional hardening:** if `TFMODSEARCH_DOCKER` is set but `docker` is not on PATH, the launcher
  could `shutil.which("docker")`-check and fall back to uvx with a stderr warning, instead of
  hard-failing `execvp`. Nice-to-have, not required.
- **Portability:** python launcher chosen over a shell script so it works uniformly on
  macOS/Linux/Windows (no exec-bit / shebang / `.cmd` split). `python3` is already implied by the
  toolchain. If a python-free launcher is wanted, ship `sh` + a `.cmd` twin instead.
- **Third mode (0.18.0): `TFMODSEARCH_URL`** — stdio proxy to a shared HTTP daemon. Set
  `TFMODSEARCH_URL=1` for the default `http://127.0.0.1:8765/mcp`, or a full URL for a custom
  target (a bare origin like `http://127.0.0.1:8765` gets `/mcp` appended automatically). The
  launcher checks that uvx is on PATH and health-checks the daemon's `/health` endpoint first
  (3 second timeout); if either check fails, it falls back to the normal local uvx/Docker path
  with a stderr warning instead of failing the session. When set, this mode takes precedence over
  `TFMODSEARCH_DOCKER`. Under the hood it execs `uvx --from "tfmodsearch>=0.18.0" tfmodsearch
  --proxy-url <url>` (version floor: older releases lack the flag), which dispatches through the
  torch-free `tfmod_entry` path — no index, no embedding model, ~90 MB RSS and sub-second startup
  per session; the daemon owns the heavy parts. This is the recommended way for plugin users to
  point at a shared daemon without losing the plugin's skills and subagents.
- README: document the default (local uvx, unchanged), the `TFMODSEARCH_DOCKER=1` opt-in, the
  `TFMODSEARCH_URL` proxy opt-in, the Docker prerequisite, and the offline / no-network-at-runtime
  property of the image.

## 5. Dockerfile skeleton (starting point — refine)

```dockerfile
# --- builder ---
FROM python:3.12-slim AS builder
ENV PIP_NO_CACHE_DIR=1 HF_HOME=/opt/hf
WORKDIR /build
# CPU-only torch first so sentence-transformers reuses it
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
COPY . .
RUN pip install .            # installs tfmodsearch + deps (bundled index/modules/config)
# pre-download the embedding model into HF cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/e5-small-v2')"
# pre-fetch only punkt_tab into a slim nltk_data dir
RUN python -c "import nltk; nltk.download('punkt_tab', download_dir='/opt/nltk_data')"

# --- runtime ---
FROM python:3.12-slim
RUN useradd -m app
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
    HF_HOME=/opt/hf NLTK_DATA=/opt/nltk_data
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/tfmodsearch /usr/local/bin/tfmodsearch
COPY --from=builder /opt/hf /opt/hf
COPY --from=builder /opt/nltk_data /opt/nltk_data
USER app
ENTRYPOINT ["tfmodsearch"]
```
(The implementing agent should verify `resolve_index_path` finds the packaged pkl in
site-packages, and that `initialize_nltk()` is satisfied by `NLTK_DATA=/opt/nltk_data` — adjust
if the code expects nltk_data at project root.)

## 6. Acceptance criteria / verification

1. **Build succeeds**; final image size recorded. Target **< ~1.5 GB** with CPU-only torch (flag
   if larger — likely a CUDA-torch leak).
2. **Offline proof** — `docker run --network none -i --rm <image> --warmup` **succeeds** and prints
   `Warmup complete: index (55 modules) and embedding model loaded, test query returned 3 results.`
   With `--network none` this proves zero runtime network dependency (HF + nltk both satisfied
   offline). This is the feature's core value proposition — treat it as the primary pass/fail
   criterion.
3. **Startup time — record, don't gate on it.** Measure cold-start-to-ready for one container and
   for 6 concurrent `docker run … --warmup` runs, and report both numbers in the PR description.
   This is informational (useful context for users deciding uvx vs Docker); it is explicitly NOT a
   pass/fail target and NOT evidence this feature "fixes" the concurrent-spawn timeout — that's a
   separate, unscoped problem (see §1, Appendix).
4. **MCP handshake** — wire the image as an MCP server (`docker run -i --rm`) in a real client and
   confirm all four tools respond: `search_modules`, `get_module`, `grep_module_docs`,
   `modules_list`. Confirm no `-t` in the args.
5. **Platform** — image runs on `linux/amd64` and `linux/arm64` (multi-arch since 0.15.1; see §4.5).
6. **No regression** — `uvx tfmodsearch` path still works unchanged; existing tests pass.
7. **Dual-mode launcher** — with the plugin installed: env unset → server comes up via `uvx`
   (default, tools respond); `TFMODSEARCH_DOCKER=1` → same server comes up via `docker run -i --rm`
   (tools respond identically). Both use the single `tfmod-search` server key (tool names
   unchanged). `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin dir at launch.

## 7. Risks / notes

- `--rm` + per-call `docker run` = a fresh container per client connection (same model as
  HashiCorp's server). A long-lived shared container is explicitly **out of scope** (it
  complicates the stdio-per-client contract).
- **CPU-only torch is not optional** for a shippable image size.
- **No `-t`** in `docker run` args — a pseudo-TTY corrupts the JSON-RPC stdio stream.
- Pin the image tag in shipped config (not `:latest`).
- Keep `uvx` as the documented default for users without Docker; Docker is an opt-in distribution
  alternative evaluated on offline/portability merits, not a performance fix (see §1).

## 8. Implementation notes (found during the build, not predicted by this spec)

- **nltk 3.10's path-security sandbox silently no-ops the punkt_tab download unless `NLTK_DATA`
  is already set at build time.** `nltk.download(..., download_dir="/opt/nltk_data")` validates
  the write target against `nltk.data.path` + the `NLTK_DATA` env var (`nltk/pathsec.py`); with
  neither set, it raises internally but `nltk.download()` swallows that into a `False` return
  instead of an exception — so the Dockerfile `RUN` step exits 0 with an *empty* nltk_data dir
  baked in. Fix: set `ENV NLTK_DATA=/opt/nltk_data` in the **builder** stage before the download
  step (not only in the runtime stage), and assert the download's return value explicitly
  (`sys.exit(0 if nltk.download(...) else 1)`) plus a `test -d .../punkt_tab` sanity check, so a
  regression fails the build loudly instead of shipping a silently-broken offline image.
- **Two paths the server computes relative to its own module file land in the wrong (root-owned)
  place under the wheel-installed layout.** `tfmod_search_lib.py` sits directly in site-packages
  in the installed layout (vs. a `src/` subdirectory in development), so `Path(__file__).parent`
  (used by `initialize_nltk()` for its own always-`mkdir(exist_ok=True)`'d local nltk_data dir) and
  `Path(__file__).parent.parent` (used by `setup_logging()` for `startup.log`/`mcp_server.log`)
  both resolve one level higher than in dev — into `.../site-packages/nltk_data` and
  `.../site-packages/../logs` respectively, both owned by root from the build. Under the non-root
  runtime user this is a `PermissionError` on first write. Fixed by pre-creating both directories
  and `chown`ing them to the runtime user in the image (see the Dockerfile) rather than patching
  the app's path resolution — this is an environment-level accommodation, not a behavior change.
  (This is latent, not Docker-specific: a real `uvx`/pip-installed run on a locked-down/read-only
  Python environment would hit the same thing; it just never surfaces for a single-user local
  install where the venv is fully owned by the invoking user.)
- **Verification actually performed**: `docker build` (~1.7 GB, over the <1.5 GB aspirational
  target — see below), `docker run --network none -i --rm <image> --warmup` (offline proof,
  passed), and a real `mcp` Python SDK `ClientSession` (`stdio_client` over
  `docker run -i --rm --network none <image>`) driving `initialize` → `list_tools` (all four
  tools present) → `call_tool` for `search_modules`/`modules_list`/`get_module` (all three
  succeeded fully offline; `grep_module_docs` intentionally not exercised offline — it's the one
  tool designed to hit the network). A raw JSON-RPC-over-stdin-file smoke test does NOT work for
  this: closing stdin after writing the request races the async tool-call response and silently
  drops it — use a real stdio client that keeps the pipe open, as above.
- **Image size (1.7 GB) exceeds the spec's <1.5 GB target.** Breakdown: `torch` (635 MB, even
  CPU-only) + `scipy`/`scikit-learn` (~175 MB combined, pulled in transitively by
  `sentence-transformers`, not a direct dependency of this project) + `transformers` (108 MB) +
  `sympy` (74 MB, a `torch` dependency) account for nearly all of it. Trimmed `pip`/`setuptools`
  and bytecode caches from the runtime image (cheap, safe); did not chase further — the floor here
  is `sentence-transformers`' own dependency footprint, and shedding it would mean swapping the
  embedding backend, which is out of scope (no new deps, no behavior change). Recorded as a known
  finding, not a blocker (see §6 criterion 1: "flag if larger").
- **Independent review (Opus) caught two real gaps, both fixed**: (1) the Claude Code plugin now
  requires `python3` on `PATH` in addition to `uv`/`uvx`, since the launch goes through the bundled
  launcher rather than calling `uvx` directly — not a concern on a typical macOS/Linux box, flagged
  for Windows where bare `python3` may not resolve; documented in README/CHANGELOG. (2) the
  "zero network calls" framing was scoped too absolutely — `search_modules`/`get_module`/
  `modules_list` are offline, `grep_module_docs` is explicitly not (it's the live-registry tool by
  design); wording corrected everywhere it appeared.
- **`${CLAUDE_PLUGIN_ROOT}` interpolation verified live, not just asserted in a unit test.**
  Installed the plugin via `claude plugin marketplace add`/`install` into a scratch
  `CLAUDE_CONFIG_DIR`, then ran `claude mcp list`: both the default path (env unset → `python3
  .../tfmodsearch_launch.py` → `uvx tfmodsearch`) and the opt-in path (`TFMODSEARCH_DOCKER=1`
  against a locally-built image tagged to match `DEFAULT_IMAGE`) showed `✔ Connected`. This is the
  strongest possible confirmation of acceptance criterion 7 short of a real end-user session.
- **0.15.1 — multi-arch (`linux/arm64` added)**: demand confirmed (the maintainer's own machine is
  Apple Silicon, and pulling the v1 `linux/amd64`-only image without `--platform` failed with "no
  matching manifest"). Before touching CI, sanity-checked locally that the build itself is
  arm64-safe: `docker build --platform linux/arm64 .` succeeded natively (no cross-compilation
  needed on an Apple Silicon host) and `docker run --platform linux/arm64 --network none -i --rm
  <image> --warmup` passed — confirming `pip install torch --index-url
  .../whl/cpu` actually serves a `manylinux_..._aarch64` wheel (it does; this was the one real risk
  worth checking before committing to the CI change, since that index is easy to assume is
  x86_64-only). CI change is `docker/setup-qemu-action` + `platforms: linux/amd64,linux/arm64` on
  the existing `build-push-action` step — the runner itself is amd64, so QEMU emulates the arm64
  leg (slower than a native arm64 runner, accepted rather than adding new runner infra).

## 9. HTTP mode (shared daemon)

Same image, second opt-in mode, shipped in 0.16.0 (design: `docs/superpowers/specs/2026-07-14-http-transport-design.md`).
No second Dockerfile, no second stage, no second entrypoint — `--transport http` is just an
argv passed to the same `ENTRYPOINT ["tfmodsearch"]`.

**Recipe** (identical to the README's "Shared HTTP instance" section):
```bash
docker run -d --name tfmodsearch-http --restart unless-stopped \
  -p 127.0.0.1:8765:8765 \
  ghcr.io/santyagoseaman/tfmodsearch:0.19.0 \
  --transport http --host 0.0.0.0 --port 8765
```

Or via the repo-root `docker-compose.yml` (service `tfmodsearch-http`, pinned image tag, loopback
port mapping, `restart: unless-stopped`, a healthcheck against `/health`, and a named volume over
`/home/app/.cache` so the `grep_module_docs` registry-doc cache survives recreates/upgrades):
```bash
docker compose up -d
```

**Plugin users**: do not disable the plugin to reach this daemon — set `TFMODSEARCH_URL=1` (see
§4.6) and the plugin's bundled launcher becomes a stdio proxy to it, keeping the skills and
subagents working.

**DNS-rebinding guard**: the server runs HTTP mode with FastMCP `host_origin_protection="auto"` —
browser-initiated cross-origin requests to `/mcp` (a foreign `Origin` header) are rejected with
403, so a malicious web page cannot script the loopback daemon. MCP SDK clients and curl send no
`Origin` header and pass untouched. This is orthogonal to the no-auth stance: Origin validation
is not authentication.

**Why the container binds `0.0.0.0` and that is fine**: `--host 0.0.0.0` inside the recipe above
looks like exactly the non-loopback bind the server warns about (`_is_loopback` logs a WARNING for
any non-loopback host). That warning is expected and correct *inside a container* — if the server
bound `127.0.0.1` inside the container's own network namespace, the published port mapping
(`-p 127.0.0.1:8765:8765`) would have nothing to forward to, and the daemon would be unreachable
from the host entirely. The actual security boundary is the **host** side of the port mapping:
`-p 127.0.0.1:8765:8765` means Docker only forwards traffic arriving on the host's loopback
interface into the container. Do not "fix" the warning by changing `--host`; do not publish the
port on a non-loopback host address (`-p 8765:8765` or `-p 0.0.0.0:8765:8765`) without a reverse
proxy that adds authentication in front — there is no auth or TLS in the server itself.

**Update notifications** (since 0.17.0): because the daemon runs a pinned image tag indefinitely,
the server itself checks PyPI once a day (HTTP mode only) and reports what it finds through
`GET /health` (`latest_version`/`update_available`), a `docker logs` WARNING once per cycle while
stale, and an `update_notice` field on `search_modules`/`modules_list`/`grep_module_docs`
responses that is absent entirely when there is nothing to report. There is no auto-update — the
operator still bumps the tag and runs `docker compose pull && docker compose up -d`. Set
`TFMODSEARCH_UPDATE_CHECK=0` to disable the check for air-gapped deployments; the only network
call it makes is one anonymous GET to the public PyPI JSON API.

## 10. ONNX encode backend (image switch, 0.19.0)

Same entrypoint, same tools, different internals: shipped in 0.19.0 (design:
`docs/superpowers/specs/2026-07-15-onnx-encode-backend-design.md`). The runtime image no longer
ships torch/sentence-transformers or a baked Hugging Face model cache. It bakes `model.onnx` +
`tokenizer.json` (exported at build time by `scripts/export_onnx_model.py`) and runs queries
through `onnxruntime` + `tokenizers` instead — this **supersedes** the "Bake in every asset" /
"Env baked into the image" / Dockerfile-skeleton descriptions in sections 4.2-4.5 and 5 above,
which describe the pre-0.19.0 (torch) image and are kept as-is for history.

**What changed in the image**:
- Builder stage: still installs CPU-only torch, but only to run the export tooling
  (`optimum-onnx`) that produces `/opt/onnx/e5-small-v2/{model.onnx,tokenizer.json}`; torch itself
  is not carried into the runtime stage.
- Runtime stage: `pip install --no-deps` on the built wheel plus an explicit torch-free
  dependency list (core deps minus `sentence-transformers`, plus `onnxruntime`/`tokenizers`).
  `HF_HUB_OFFLINE`, `TRANSFORMERS_OFFLINE`, and `HF_HOME` are gone — nothing imports Hugging Face
  at runtime anymore. In their place: `TFMODSEARCH_EMBED_BACKEND=onnx` and
  `TFMODSEARCH_ONNX_MODEL_DIR=/opt/onnx/e5-small-v2`.
- The offline guarantee (`docker run --network none -i --rm <image> --warmup`) is unchanged in
  spirit — it now proves the ONNX path loads and encodes fully offline instead of the HF-cache
  path.

**Measured** (golden set: all 162 queries, 54-module catalog at spike time):
- Image size: **1.42 GB → 559 MB uncompressed** (pull size verified post-release).
- Parity vs. the previous torch/sentence-transformers backend: min cosine **0.99999988**, max
  elementwise diff **4.06e-07**.
- Query encode: ~5x faster than torch on CPU.
- Golden set: 172/172 on both backends against the untouched index pickle (the index is not
  rebuilt — the standing index-drift policy in `CLAUDE.md` applies; ONNX queries the same
  torch-produced embeddings the pickle always had).

**Unaffected**: `uvx tfmodsearch` / PyPI installs — the core dependency set is unchanged and still
defaults to torch (`TFMODSEARCH_EMBED_BACKEND=auto` picks torch whenever
`sentence-transformers` is importable). The ONNX backend is available there too as the opt-in
`tfmodsearch[onnx]` extra, but nothing changes for an install that does not ask for it. Transports,
tools, the plugin, and the shared-HTTP-daemon mode in section 9 are all unaffected — `--transport
http` is still just an argv to the same `ENTRYPOINT ["tfmodsearch"]`, now running on top of the
ONNX backend instead of torch when using the official image.

---

### Appendix — background evidence (measured 2026-07-13, context only — not this feature's acceptance bar)
- Solo `uvx tfmodsearch --warmup`: 8.2 s. Six concurrent: 11.5 s each.
- Warmup log confirms the HF network call: `GET https://huggingface.co/api/models/intfloat/e5-small-v2`.
- `initialize_nltk()` downloads `punkt_tab` on first run (`src/tfmod_search_lib.py:107,114`).
- Index is a prebuilt artifact, not built at runtime (`model/tfmod_e5_small_index.pkl`, 4.3 MB,
  force-included in the wheel).
