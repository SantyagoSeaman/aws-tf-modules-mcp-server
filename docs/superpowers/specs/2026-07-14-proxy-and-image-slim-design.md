# 0.18.0 Design: Plugin Proxy Mode + Docker Image Slimming

**Date**: 2026-07-14
**Status**: Draft — awaiting maintainer review
**Target release**: 0.18.0 (minor)

Two independent improvements shipped together because both are small and both close gaps
surfaced by the 0.16.0 HTTP-transport rollout:

1. **Proxy mode** — let plugin users point the bundled stdio server at a shared HTTP daemon
   without disabling the plugin (today they must choose: skills OR shared daemon).
2. **Image slimming** — the Docker image is 1.69 GB uncompressed (~600 MB pull); ~350 MB of
   that is dead weight removable with zero behavior change.

---

## Part 1: Proxy mode (`--proxy-url` / `TFMODSEARCH_URL`)

### Problem

Since 0.16.0 the shared HTTP daemon is the answer to "N subagents × 600 MB model load", but
the migration path costs plugin users their workflow layer: `claude plugin disable
tfmod-search` removes the eight skills and two subagents along with the stdio server. The
"skills + shared daemon" combination is currently impossible.

### Solution

A stdio→HTTP proxy mode in the server, selected by the plugin launcher via one env var. The
plugin stays enabled (skills intact); its MCP server becomes a lightweight forwarder to the
daemon.

FastMCP 3.4.4 (already our dependency, version verified in the dev venv) ships this natively:
`FastMCP.as_proxy(url)` returns a server that transparently forwards the MCP handshake and
all tool calls to a remote backend. No new dependencies.

### Server changes (`src/tfmod_mcp_server.py`)

New CLI flag:

```
--proxy-url URL    Run as a stdio proxy forwarding to a remote Streamable HTTP
                   MCP server (e.g. http://127.0.0.1:8765/mcp). Implies stdio;
                   loads no index and no embedding model.
```

- The proxy branch runs **before** any index/model/NLTK loading in `main()`:

  ```python
  if args.proxy_url:
      proxy = FastMCP.as_proxy(args.proxy_url)
      proxy.run()  # stdio
      return
  ```

  Startup is sub-second and the process footprint is a few tens of MB — the whole point.
  The 600 MB model lives only in the daemon.

- **Flag validation** (post-parse, same pattern as the existing transport checks):
  - `--proxy-url` + `--transport http` → error (a proxy is a stdio client-side helper;
    proxying into another HTTP server is not a supported topology).
  - `--proxy-url` + `--warmup` → error (nothing to warm; the daemon owns the model).
  - `--index_path`/weights flags are accepted but ignored in proxy mode (they arrive from
    generic launch wrappers; erroring on them would break composability). Ignoring is
    silent — documented, not warned, to keep stderr clean for stdio clients.
- **Update-check thread**: not started (existing rule: stdio mode never starts it). The
  daemon runs its own check; `update_notice` fields in tool responses pass through the
  proxy untouched, so plugin users still see update notices — an improvement over today's
  stdio path, which has no channel at all.
- No env-var fallback on the server side for the URL: the flag is the single server-side
  interface. Env handling lives in the launcher (below), which is the component that owns
  env-based backend selection today (`TFMODSEARCH_DOCKER`, `TFMODSEARCH_IMAGE`).

### Launcher changes (`plugins/tfmod-search/bin/tfmodsearch_launch.py`)

New env var, extending the existing `select_backend()` decision table:

- `TFMODSEARCH_URL=<url>` → proxy mode targeting `<url>`.
- `TFMODSEARCH_URL=1` (or `true`/`yes`/`on`, case-insensitive) → proxy mode targeting the
  default `http://127.0.0.1:8765/mcp`. This removes the "what port was it again?" step for
  the default setup: `docker compose up -d` + `TFMODSEARCH_URL=1` and done.
- Unset or falsy (`""`/`0`/`false`/`no`/`off` — reuse `_FALSY`) → existing behavior
  (uvx or Docker per `TFMODSEARCH_DOCKER`).

**Precedence**: `TFMODSEARCH_URL` wins over `TFMODSEARCH_DOCKER`. If both are set truthy,
print a one-line stderr notice ("TFMODSEARCH_URL takes precedence; ignoring
TFMODSEARCH_DOCKER") and proceed with the proxy. Rationale: URL expresses "do not run a
local backend at all", which subsumes the backend-selection question.

**Preflight + graceful fallback** (mirrors the existing docker-not-on-PATH fallback):

1. Derive the health URL from the target: same scheme/host/port, path `/health`
   (`urllib.parse`, stdlib only — the launcher must stay dependency-free).
2. `GET` it with a 3-second timeout.
3. 200 → `os.execvp("uvx", ["uvx", "tfmodsearch", "--proxy-url", url])`.
4. Anything else (refused, timeout, non-200) → stderr warning
   ("tfmodsearch_launch: TFMODSEARCH_URL is set but <url> is not responding; falling back
   to a local server.") and fall through to the existing uvx/Docker selection. The agent
   session keeps working either way; an operator mistake degrades to the slow path instead
   of a dead MCP server.

The preflight deliberately checks `/health` (cheap, no MCP handshake) rather than `/mcp`.
Note the window: the daemon can die after preflight but before/while the session runs —
the proxy then surfaces connection errors on tool calls. Accepted; same failure mode as
any remote MCP server, and the next session falls back cleanly.

### User-facing configuration (the whole story)

```jsonc
// ~/.claude/settings.json
{ "env": { "TFMODSEARCH_URL": "1" } }          // default daemon on 127.0.0.1:8765
// or
{ "env": { "TFMODSEARCH_URL": "http://127.0.0.1:9000/mcp" } }  // custom port
```

Plus a running daemon (`docker compose up -d` or the README one-liner). Plugin stays
enabled; skills, subagents, and auto-search workflow all keep working. Rollback: unset the
var.

### Security notes

- The proxy inherits the daemon's trust model: no auth, loopback-only by convention. The
  proxy adds no new listening surface (it serves stdio to its parent process only).
- The launcher execs a fixed argv (`uvx tfmodsearch --proxy-url <url>`); the URL is passed
  as a single argv element, never shell-interpreted (existing `os.execvp` pattern, no shell).
- A hostile `TFMODSEARCH_URL` pointing at an attacker server means the attacker controls
  tool responses — identical trust position to `TFMODSEARCH_IMAGE` today (env vars are
  already in the user's trust boundary). Documented, not mitigated.

### Testing

- **Unit (launcher)**: `select_backend()` matrix — URL absent/falsy/truthy-default/full-URL,
  URL+DOCKER precedence notice, preflight-failure fallback (health fetch injected as a
  parameter, no real network; same injection style as `test_registry_docs.py`).
- **Unit (server)**: argparse — `--proxy-url` accepted; conflicts with `--transport http`
  and `--warmup` rejected with clear messages.
- **E2E** (extends `tests/e2e/test_mcp_http_e2e.py` fixtures): spawn the HTTP daemon on an
  ephemeral port, spawn `tfmodsearch --proxy-url` as a stdio subprocess, run a real MCP
  session through the proxy: initialize, `tools/list` shows all four tools, `search_modules`
  returns results, `get_module` returns the orientation head. Assert proxy process RSS stays
  far below model size (sanity: < 300 MB) or assert startup-to-ready under a few seconds —
  whichever proves "no model load" more robustly on CI.
- **E2E (fallback)**: launcher with `TFMODSEARCH_URL` pointing at a dead port falls back and
  still produces a working stdio server (reuse the existing launcher e2e harness).

### Docs

- README: new subsection under "Shared HTTP instance" — "Keeping the plugin (proxy mode)",
  presented as the recommended migration for plugin users; demote the
  `plugin disable` path to "plugin-less setups". Update the trade-off sentence (it currently
  says skills loss is unavoidable).
- Plugin launcher docstring; `docs/docker-container-support.md` §HTTP; CHANGELOG.

---

## Part 2: Docker image slimming

### Why 1.69 GB? (measured on 0.17.0, arm64; amd64 within a few %)

| Component | Uncompressed | Notes |
|---|---|---|
| `torch` (CPU wheel) | 580 MB | `lib/` 326 · **`test/` 90 · `include/` 63 · `bin/` 48** · rest ~53 |
| `scipy` (+`scipy.libs`) | 120 MB | dependency of scikit-learn |
| duplicated `chown -R` layer | 150 MB | re-copies `/opt/hf` + `/opt/nltk_data` into a new layer |
| HF model cache (`/opt/hf`) | 135 MB | e5-small-v2 fp32 |
| python:3.12-slim base | ~145 MB | |
| `transformers` | 52 MB | |
| `numpy` (+libs) | 54 MB | |
| `sklearn` | 40 MB | dependency of sentence-transformers |
| `sympy` | 30 MB | dependency of torch |
| everything else | ~180 MB | tokenizers, cryptography, nltk, fastmcp, index, docs corpus, … |

Pull (compressed) size today: **617 MB amd64 / 578 MB arm64**.

Root causes, in order of leverage:

1. **The torch CPU wheel ships its own test suite, C++ headers, and build binaries** —
   `torch/test` (90 MB), `torch/include` (63 MB), `torch/bin` (48 MB) are never touched by
   inference. ~200 MB of pure dead weight.
2. **`chown -R` in the runtime stage duplicates every chowned file into a new 150 MB
   layer** — classic Docker layer semantics; `COPY --chown` avoids it entirely.
3. **The sentence-transformers dependency chain** hauls in scipy + scikit-learn (~160 MB)
   that the query path never imports, and torch hauls sympy + networkx (~40 MB). Removing
   packages that are hard import-time dependencies is fragile — this is the boundary between
   Tier 1 and Tier 2.
4. **fp32 model weights** (135 MB) — quantization is possible but couples to the Tier 2
   backend question.

### Tier 1 — ship in 0.18.0 (zero behavior change, ~-350 MB)

1. Replace the runtime-stage `chown -R` of `/opt/hf` and `/opt/nltk_data` with
   `COPY --from=builder --chown=app:app`. (The `mkdir` + `chown` for the two writable dirs
   `site-packages/nltk_data` and `logs` stays — those are empty, cost nothing.)
   **Saves 150 MB.**
2. In the builder stage, after `pip install`, delete `torch/test` and `torch/include`
   (and re-run the existing `__pycache__` sweep). **Saves ~150 MB.**
   *(Implementation finding: `torch/bin` is NOT removable — `torch/__init__.py`
   unconditionally resolves `torch/bin/torch_shm_manager` at import time and raises
   `RuntimeError` without it. The original ~200 MB estimate included it.)*
   Guard: the release gate already runs `docker run --network none -i --rm <rc> --warmup`
   plus a real HTTP-mode tool call — both would catch a missing-file import error. Add one
   explicit smoke assertion to the checklist: a `search_modules` call against the slimmed rc
   returns results (exercises the full encode path).
3. Do **not** touch scipy/sklearn/sympy/networkx in this release: they are declared
   dependencies with plausible import-time coupling; savings (~200 MB) do not justify the
   fragility without the Tier 2 restructuring.

Expected result: **~1.69 → 1.42 GB uncompressed (measured on the rc build); pull
~600 → ~430-500 MB (estimate, verified at release).**

### Tier 2 — investigate separately (not in 0.18.0): ONNX encode path

The structural fix. Query-side embedding via `onnxruntime` (+`tokenizers`) instead of
torch/sentence-transformers would drop torch + scipy + sklearn + sympy + networkx
(~800 MB uncompressed) for an ~50 MB runtime, landing the image around **500-600 MB
uncompressed / ~250 MB pull**. Optionally int8-quantized weights shrink the model
135 → ~35 MB.

Why it is not in 0.18.0:

- sentence-transformers hard-requires torch, so this means a custom encode path
  (tokenize → ORT session → mean-pool → normalize) behind an abstraction in
  `tfmod_search_lib.py`, with index building staying on torch (dev-only concern).
- **Embedding drift risk**: the pickled index embeddings were produced by torch; ONNX fp32
  typically matches to ~1e-6 but "typically" is not the golden set. The full
  54-module/162-query golden set at 100% top-3 is the gate, same rule as any index-touching
  change (see the standing index-drift policy). int8 quantization raises the drift risk
  substantially and gets evaluated only after fp32-ONNX proves clean.
- It deserves its own spec, spike, and benchmark (latency should improve, but verify).

Decision: 0.18.0 ships Tier 1; Tier 2 becomes a candidate spec once there is a concrete
pull-size complaint or the next natural window.

### Non-goals

- Swapping the embedding model (settled by the 5-model benchmark in 0.11.0).
- Changing the base image (distroless/alpine): incompatible-libc and debugging costs for
  ~100 MB; not worth it while Tier 2 offers 800 MB.
- Any change to wheel/uvx distribution — this part is Docker-only.

---

## Rollout

- Version bump: standard list per CLAUDE.md Release Process step 3 (pyproject, two plugin
  manifests, `DEFAULT_IMAGE` in the launcher, docker-compose tag, README current-release
  tags, CHANGELOG).
- Implementation: Sonnet subagents, one per plan task, sequential, TDD. Review: independent
  Opus subagent over the full branch diff. The proxy touches the plugin launch path
  (user-facing surface) → add the blind persona-walkthrough review, per the standing
  convention.
- Release gate additions on top of the standard one: proxy e2e green; slimmed-image rc
  verified in **both** modes + `--network none --warmup` + one real `search_modules` through
  HTTP; image size measured and recorded in the CHANGELOG entry.

## Acceptance criteria

1. Plugin user with a running daemon sets `TFMODSEARCH_URL=1`, restarts Claude Code: skills
   still listed, all four tools work, no model load in the client-side process, tool
   responses carry `update_notice` when the daemon knows of a newer version.
2. Same user with the daemon stopped: session still gets a working (local, slow-path) server;
   a single clear stderr warning explains why.
3. `tfmodsearch --proxy-url http://127.0.0.1:8765/mcp` from any MCP client config works
   without the plugin.
4. `--proxy-url --transport http` and `--proxy-url --warmup` fail fast with clear errors.
5. Image: both transports work from the slimmed image; offline warmup passes; uncompressed
   size ≤ 1.45 GB and pull size ≤ 500 MB on both architectures (revised from 1.4 GB after
   the torch/bin finding above).
6. stdio default path (no env vars set) remains byte-identical in behavior to 0.17.0.
