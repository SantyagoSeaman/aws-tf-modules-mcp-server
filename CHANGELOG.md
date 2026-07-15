# Changelog

## [0.20.0] - 2026-07-15

[0.20.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.20.0

Three server-only output-shaping wins from the v4 post-testing log analysis: `get_module(sections=['inputs'])` no longer over-fetches on combined-heading modules, the default orientation head now inlines the module's root inputs (removing a measured second call), and the grep escalation hint now steers agents to verify input TYPE/SHAPE, not just names. The search index and the module docs corpus are untouched — search results are byte-identical to 0.19.1.

### Changed

- **`get_module(sections=['inputs'|'outputs'|'examples'])` on combined-heading modules returns only the requested interface sub-sections, not the whole bundle.** The BUG-1 fix had fallen back to the entire `## Root Module:` / `## Submodule N:` block; asking for just inputs pulled the whole root plus every submodule (measured ~2.3-2.4x larger, e.g. s3-bucket 13.5K to 30.9K chars). The section filter now extracts only the matching `### Main Input Variables` / `### Main Outputs` / `### Usage Examples` H3 sub-sections. Docs with a non-standard interface layout (e.g. network-firewall, whose interface lives under a `## Submodules` inventory) still resolve via a whole-section safety net, so every interface key resolves on every doc as before.
- **The default orientation head inlines the compact ROOT input table.** `get_module(mod)` with no `sections` now includes the root module's `Main Input Variables` alongside the existing features / use-cases / submodule-inventory / version-pin content, removing the measured `get_module(mod)` then `get_module(mod, sections=['inputs'])` double-fetch. Submodule inputs stay out of the head; pure submodule-collection docs with no root inputs add nothing (no spurious "not found").
- **The grep escalation hint (get_module footer + `grep_module_docs` description) now names TYPE/SHAPE verification**, directing agents to grep the live doc to confirm the nested field structure of a `map(object)`/`any`-typed input before writing it, not only to confirm resource/variable names.

### Unchanged

- **The search index is not rebuilt and no module doc changed** — search ranking and results are byte-identical to 0.19.1; the golden set is unaffected by construction.
- **No network, no new dependency, no tool-schema change.** All changes are in `tfmod_mcp_server.py` response shaping plus tests.
- `sections=["all"|"full"|"everything"]` still returns the complete document verbatim; core sections remain always-included; split-heading docs (e.g. autoscaling, redshift) are byte-identical for `sections=['inputs']`.
- Transports, the ONNX/torch backends, the shared-HTTP-daemon and proxy modes, and the Docker image build are all unaffected.

## [0.19.1] - 2026-07-15

[0.19.1]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.19.1

Hotfix: `grep_module_docs` failed with `[Errno 13] Permission denied` in compose deployments — the named volume mounted over `/home/app/.cache` is created root-owned by Docker when the image has no such directory, and the cache write path treated that as fatal. Found live within hours of 0.19.0 by a real plugin session.

### Fixed

- **Cache writes are now best-effort**: an unwritable registry-doc cache dir (root-owned volume, read-only rootfs) degrades to uncached fetches with a single WARNING naming the fix, instead of failing the tool call. The cache is an optimization, not a dependency.
- **The image now bakes an app-owned `/home/app/.cache`**, so a FRESH named volume initializes with the right ownership (Docker copies content and ownership from the image on first mount of an empty volume). Volumes created by older images stay root-owned — one-off fix documented in `docker-compose.yml`: `docker exec -u root tfmodsearch-http chown app:app /home/app/.cache`.

### Unchanged

- Everything else from 0.19.0: ONNX backend, image size, PyPI dependency set, index, tools, transports.

## [0.19.0] - 2026-07-15

[0.19.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.19.0

Adds a selectable ONNX encode backend and switches the official Docker image to it, cutting the
image from 1.42 GB to 559 MB uncompressed with numerically interchangeable search results and
faster query encoding; PyPI/uvx installs are unaffected and keep torch by default.

### Added

- **Encoder backend seam** (`src/tfmod_search_lib.py`): index-build and query encode calls now go through `_get_encoder`, which dispatches on `TFMODSEARCH_EMBED_BACKEND` (`auto` default, `torch`, or `onnx`). `auto` uses the torch/sentence-transformers backend when it is importable, else the ONNX backend when ONNX assets are found, else a RuntimeError naming both options. The `sentence-transformers` import is now lazy (moved out of module top-level into the torch loader) so the library imports cleanly without torch installed. Model/encoder caching and the existing concurrency lock are preserved for both backends.
- **New module `src/tfmod_onnx_encoder.py`**: `OnnxEncoder` — a `tokenizers` tokenizer (truncation at 512 tokens) plus an `onnxruntime` CPU session, replicating sentence-transformers attention-masked mean pooling and L2 normalization for `intfloat/e5-small-v2`. `resolve_onnx_model_dir()` locates assets via `TFMODSEARCH_ONNX_MODEL_DIR` or `<project_root>/onnx/e5-small-v2`.
- **New optional extra `tfmodsearch[onnx]`**: `onnxruntime>=1.20`, `tokenizers>=0.21`. Core dependencies are unchanged — this is opt-in.
- **New env vars**: `TFMODSEARCH_EMBED_BACKEND` (`auto`/`torch`/`onnx`) and `TFMODSEARCH_ONNX_MODEL_DIR`.
- **Export script** `scripts/export_onnx_model.py` (not shipped in the wheel): exports `intfloat/e5-small-v2` to ONNX via `optimum-cli`, then runs a parity check against sentence-transformers when both are installed. Used by the Dockerfile builder stage and by developers regenerating assets.
- **Docker image now runs the ONNX backend**: the builder stage exports ONNX assets and builds the wheel; the runtime stage installs the wheel with `--no-deps` plus an explicit torch-free dependency list (core deps minus `sentence-transformers`, plus `onnxruntime`/`tokenizers`), and sets `TFMODSEARCH_EMBED_BACKEND=onnx` / `TFMODSEARCH_ONNX_MODEL_DIR=/opt/onnx/e5-small-v2`. `HF_HUB_OFFLINE`/`TRANSFORMERS_OFFLINE`/`HF_HOME` are gone from the runtime image — nothing imports Hugging Face at runtime anymore. **Measured: 1.42 GB to 559 MB uncompressed** (pull size verified post-release), offline `--warmup` and a real HTTP `search_modules` call both verified against the rc image.
- Design + plan committed under `docs/superpowers/{specs,plans}/2026-07-15-onnx-encode-backend-*`.
- README documents the new "Embedding backends" configuration and the Docker image's backend switch; `docs/docker-container-support.md` gains a new section 10 describing the image internals change, with the pre-0.19.0 torch/HF-cache description in sections 4.2-4.5 kept for history.

### Unchanged

- **PyPI dependency set is unchanged** — `uvx tfmodsearch` and any pip/PyPI install keep sentence-transformers/torch as the default backend; nothing to opt into for a normal local install.
- **The pickled search index is not rebuilt.** ONNX queries the same torch-produced embeddings the index has always had — validated at cosine ≥ 0.99999988 (max elementwise diff 4.06e-07) against sentence-transformers across all 162 golden queries.
- **Golden set is 100% on both backends**: 172/172 tests against the untouched index pickle, torch and ONNX alike. (172 is the full current searchable suite over 55 modules; the 162 above is the 54-module x 3-query embedding-parity scope measured at spike time.)
- **Transports, tools, and the plugin are untouched.** stdio/HTTP transport behavior, the four MCP tools, the shared-HTTP-daemon and proxy modes, and the plugin's default `uvx` launch path are all unaffected.

## [0.18.0] - 2026-07-14

[0.18.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.18.0

Adds a stdio proxy mode so plugin users can point at a shared HTTP daemon without giving up the
plugin's skills and subagents, plus a slimmed Docker image with the torch wheel's dead weight
removed.

### Added

- **`--proxy-url` server flag**: runs the server as a lightweight stdio-to-HTTP forwarder (fastmcp `create_proxy`) that never touches NLTK, config, index, or embedding-model initialization — the daemon at the given URL owns all of that. Implies stdio; conflicts with an explicit `--transport http` and with `--warmup` (nothing to warm up). Index/weight flags are accepted but ignored in this mode.
- **Launcher `TFMODSEARCH_URL` env var** (`plugins/tfmod-search/bin/tfmodsearch_launch.py`): set `TFMODSEARCH_URL=1` for the default daemon (`http://127.0.0.1:8765/mcp`), or a full URL for a custom target, and the plugin's bundled server becomes a stdio proxy to it via `uvx --from "tfmodsearch>=0.18.0" tfmodsearch --proxy-url <url>` (the version floor keeps a stale uv cache from resolving a release without the flag). A bare-origin URL (no path) is defaulted to `/mcp` automatically. A uvx-on-PATH check and a `/health` preflight (3s timeout) gate the switch; if uvx is missing or the daemon does not respond, the launcher falls back to the normal local uvx/Docker path with a stderr warning instead of failing the session. Takes precedence over `TFMODSEARCH_DOCKER` when both are set (with a notice printed to stderr when the proxy actually launches).
- **Torch-free proxy entry path**: the `tfmodsearch` console command now dispatches through a lightweight `tfmod_entry` module — `--proxy-url` invocations run via `tfmod_proxy`/`tfmod_server_args` without ever importing the ML stack. Measured: ~0.8s startup and ~90 MB RSS per proxy process versus ~5s and ~460 MB if the full server module were imported; guarded by a subprocess import test and a 10s-bound e2e session through the dispatcher.
- **E2E proxy coverage** (`tests/e2e/test_mcp_proxy_e2e.py`): spawns a real HTTP daemon plus a real stdio proxy subprocess, drives a full MCP session through the proxy (tool discovery, `search_modules`, `get_module`) with a nonexistent index path and an empty offline HF cache, proving no index or model load ever happens on the proxy side.
- **Docker image slimmed from 1.69 GB to 1.42 GB**: the builder stage now removes the CPU torch wheel's `test/` and `include/` directories (its own test suite and C++ headers, neither touched at inference time), and the runtime stage uses `COPY --from=builder --chown=app:app` for the baked HF/NLTK assets instead of a layer-duplicating `chown -R` pass. `torch/bin` stays in the image — `torch` resolves `torch/bin/torch_shm_manager` unconditionally at import time, so removing it breaks the image. Verified with an offline `--warmup` run and a real `search_modules` call over the HTTP transport against the slimmed image.
- README and `docs/docker-container-support.md` document the new proxy mode (recommended path for plugin users who also want a shared daemon) alongside the existing `TFMODSEARCH_DOCKER` opt-in.
- Design + plan committed under `docs/superpowers/{specs,plans}/2026-07-14-proxy-and-image-slim-*`.

### Unchanged

- **stdio default path is behaviorally identical to 0.17.0** when no new env vars or flags are set — same tools, same startup sequence, no launcher behavior change; the existing test suite passes unmodified. (Internally, argument parsing moved to the import-light `tfmod_server_args` module and the console entry point now goes through `tfmod_entry`.)
- **No new dependencies.** fastmcp `create_proxy` was already available in the existing `fastmcp` dependency; the launcher stays stdlib-only.
- **The plugin remains stdio by default.** `TFMODSEARCH_URL` and `TFMODSEARCH_DOCKER` are both opt-in; nothing changes for a user who sets neither.
- **No index rebuild, no changes to search behavior, tool signatures, or the module catalog.**

## [0.17.0] - 2026-07-14

[0.17.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.17.0

Adds a daily PyPI update check for the shared HTTP daemon (since 0.16.0) so long-lived,
pinned-image installs learn when a newer release ships, surfaced through `/health`, a log
WARNING, and an agent-visible `update_notice` field on JSON tool responses. stdio remains
completely unaffected.

### Added

- **Daily PyPI update check** (HTTP mode only): a background daemon thread checks `https://pypi.org/pypi/tfmodsearch/json` once at startup and every 24h thereafter (`fetch_latest_pypi_version`/`is_newer_version` in `tfmod_registry_docs.py`), comparing the published version against the running one with a self-contained, fail-closed int-tuple compare (no `packaging` dependency; rc/dev suffixes intentionally produce no notice). Failures (network, malformed response) are silent at DEBUG and keep the previous state; the check runs in its own thread with a 5s timeout and never blocks a request.
- **`GET /health` gains `latest_version`/`update_available`** (additive; existing fields unchanged) — `latest_version` is `null` until the first successful check.
- **Log WARNING once per 24h cycle** while a newer version is known, naming the exact operator action (bump the image tag in `docker-compose.yml`, then `docker compose pull && docker compose up -d`) — visible in `docker logs`.
- **Agent-visible `update_notice` field** on the JSON-returning tools (`search_modules`, `modules_list`, `grep_module_docs`) when an update is available; absent entirely (not `null`) otherwise, so there is zero output noise in the common case. `get_module`'s curated markdown output is untouched.
- **Kill switch `TFMODSEARCH_UPDATE_CHECK`** (falsy: empty string, `0`, `false`, `no`, `off`, case-insensitive) disables the checker thread entirely, for air-gapped deployments. Default: enabled in HTTP mode.
- Design + plan committed under `docs/superpowers/{specs,plans}/2026-07-14-update-check-*`.

### Unchanged

- **stdio remains byte-identical to 0.16.0** — no checker thread, no new fields, no notice; the checker only starts in the HTTP branch of `main()`. The existing test suite passes unmodified.
- **No auto-update.** The server never pulls images or restarts itself; the operator stays in control of when to upgrade.
- **No telemetry.** The check is one anonymous GET to the public PyPI JSON API; nothing about the customer, host, or usage is sent.
- **No new runtime dependencies, no index rebuild, no change to the plugin or the module catalog.**

## [0.16.0] - 2026-07-14

[0.16.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.16.0

Adds an opt-in Streamable HTTP transport so the server can run as a single long-lived shared instance instead of one process per client — the fix for fan-out scenarios where N subagents each pay for their own embedding-model load. stdio remains the default and is unchanged; the plugin remains stdio-only; the index and search behavior are untouched.

### Added

- **Streamable HTTP transport** (`--transport http`, default `--transport stdio` — full backward compatibility with no flags). `--host`/`--port` (default `127.0.0.1`/`8765`) with env fallbacks `TFMODSEARCH_TRANSPORT`/`TFMODSEARCH_HOST`/`TFMODSEARCH_PORT`; precedence CLI > env > default. Serves Streamable HTTP (never legacy SSE) at `http://<host>:<port>/mcp` via FastMCP's `app.run(transport="http", ...)`.
- **`GET /health` endpoint** (HTTP mode only): returns 200 with `{"status": "ok", "version": ..., "modules": <count>}` — a cheap liveness/readiness probe for `docker run -d` and scripted setups with no MCP handshake needed. The port only starts listening after warm-once startup completes, so a readiness poller sees connection-refused during startup, then 200 (a defensive 503 `{"status": "initializing"}` branch exists but is unreachable in normal operation).
- **Warm-once startup for HTTP mode**: the embedding model loads exactly once, deterministically, before the server starts serving (reuses the existing `--warmup` search path); a `READY on http://host:port/mcp` log line marks readiness. stdio mode keeps its existing lazy load, unchanged.
- **Non-loopback bind warning**: binding a `--host` that isn't loopback (e.g. `0.0.0.0`) logs a prominent WARNING — the transport has no authentication, so anyone who can reach the address can query the server.
- **DNS-rebinding protection**: the HTTP transport runs with FastMCP `host_origin_protection="auto"`, rejecting browser-initiated cross-origin requests (`Origin: http://evil.example` → 403) so a malicious web page cannot script the loopback daemon. SDK clients and curl send no Origin header and are unaffected; guarded by an e2e regression test.
- **`EXPOSE 8765`** added to the existing Dockerfile (documentation only, no structural change) and a new repo-root **`docker-compose.yml`** encoding the shared-daemon recipe: pinned image tag, `restart: unless-stopped`, loopback-only port mapping (`127.0.0.1:8765:8765`), a healthcheck against `/health`, and a named volume over `/home/app/.cache` so the `grep_module_docs` registry-doc cache survives container recreates and image upgrades.
- **E2E test suite for HTTP transport** (`tests/e2e/test_mcp_http_e2e.py`): spawns the real server with `--transport http`, waits on `/health`, then drives a full MCP session over `mcp.client.streamable_http` — handshake, tool discovery, `search_modules`/`get_module` calls, an 8-way concurrent-call burst, and an env-fallback variant.
- **Python 3.14 in the CI test matrix** (now `["3.12", "3.13", "3.14"]`) and in the trove classifiers. Verified locally first: the full dependency stack (torch 2.13, sentence-transformers 5.6, fastmcp) installs on cp314 and the integration suite passes (703 tests).
- Design + plan committed under `docs/superpowers/{specs,plans}/2026-07-14-http-transport-*`.

### Changed / Hardened

- **Model load and query encode serialized with a lock.** `SentenceTransformer` construction and the query-embedding `encode()` call in `tfmod_search_lib.py` are now guarded by a module-level `threading.Lock` — `SentenceTransformer.encode()` isn't guaranteed thread-safe, and the HTTP transport can serve genuinely concurrent tool calls (stdio never contended on this). Query encode is ~10 ms, so contention is negligible; verified with an 8-thread concurrent-load test that the model constructs exactly once.
- **Registry doc-cache writes are now atomic.** `_write_cache_entry` in `tfmod_registry_docs.py` writes via a temp file plus `os.replace` (atomic on POSIX) instead of a direct write, so concurrent `grep_module_docs` calls racing on the same cache entry can no longer corrupt it — worst case under a race is a harmless duplicate fetch.

### Unchanged

- **stdio remains the default transport** with no flags — behavior is byte-identical to before this release; the full pre-existing test suite passes unmodified.
- **The Claude Code/Codex plugin is unchanged** and stays stdio-only (`uvx tfmodsearch` / Docker opt-in via `TFMODSEARCH_DOCKER`, per 0.15.x) — HTTP is an operator-managed mode configured via the documented `claude mcp add --transport http` recipe, not a plugin feature.
- **No index rebuild, no changes to search behavior, tool signatures, or the module catalog.**

## [0.15.1] - 2026-07-13

[0.15.1]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.15.1

Adds `linux/arm64` to the Docker image published in 0.15.0 (Apple-Silicon demand confirmed). No other changes.

### Added

- **`linux/arm64` image variant**, published alongside `linux/amd64` under the same tags (`ghcr.io/santyagoseaman/tfmodsearch:0.15.1`, `:latest`). `docker-publish.yml` now runs `docker/setup-qemu-action` before the build/push step and builds both platforms via buildx; the amd64 GitHub-hosted runner emulates the arm64 leg via QEMU. Verified locally before the CI change: `docker build --platform linux/arm64 .` builds natively on Apple Silicon and `docker run --platform linux/arm64 --network none -i --rm <image> --warmup` passes offline — confirming the CPU-only `torch` install serves a real `aarch64` wheel from `download.pytorch.org/whl/cpu`, not just x86_64.

## [0.15.0] - 2026-07-13

[0.15.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.15.0

Adds an official Docker image as a second, opt-in distribution channel alongside `uvx tfmodsearch` — for air-gapped/offline environments, CI runners without a Python/uv toolchain, or teams standardizing MCP deployment on containers. `uvx` remains the documented default; nothing about search behavior, the index, or existing tool signatures changed.

### Added

- **Docker image, published to GHCR** (`ghcr.io/santyagoseaman/tfmodsearch`, `linux/amd64` for v1). Multi-stage build bakes in the `intfloat/e5-small-v2` embedding model, the prebuilt search index, the module docs corpus, and the NLTK `punkt_tab` tokenizer at build time — **`search_modules`/`get_module`/`modules_list` make zero network calls at runtime**, verified with `docker run --network none -i --rm <image> --warmup` and a live MCP session (`grep_module_docs` is the one tool designed to reach the live Terraform Registry and is unaffected by the offline build; it just needs real network when called). CPU-only `torch` (not the CUDA wheel) keeps the image in the few-hundred-MB-to-low-GB range instead of multi-GB. Runs as a non-root user. `docker run -i --rm <image>` speaks the same stdio JSON-RPC as `uvx tfmodsearch` — never pass `-t`/`--tty`, it corrupts the stream.
- **`.github/workflows/docker-publish.yml`**: on `v*` tag push, builds and pushes `ghcr.io/santyagoseaman/tfmodsearch:<version>` and `:latest` after the full CI suite passes.
- **Dual-mode launcher for the Claude Code plugin** (`plugins/tfmod-search/bin/tfmodsearch_launch.py`): defaults to `uvx tfmodsearch`; set `TFMODSEARCH_DOCKER=1` to switch to `docker run -i --rm <image>` instead (tag overridable via `TFMODSEARCH_IMAGE`). Falls back to `uvx` with a warning if Docker is requested but not on `PATH`. Verified live with the `claude` CLI (`claude mcp list`) that both the default and `TFMODSEARCH_DOCKER=1` paths actually connect. The Codex plugin stays `uvx`-only — Codex CLI doesn't yet reliably interpolate a plugin-relative path in its `mcp.json`.

### Changed

- **Claude Code plugin now requires `python3` on `PATH`**, in addition to `uv`/`uvx` — the MCP server launch now goes through the bundled launcher script rather than calling `uvx` directly. Not a concern on a typical macOS/Linux dev box; flagged for Windows users where bare `python3` may not resolve.

### Known limitations

- Image size is ~1.7 GB, over the spec's aspirational <1.5 GB — the floor is `sentence-transformers`' own `torch`/`scipy`/`scikit-learn`/`transformers` dependency footprint; not chased further since shedding it means swapping the embedding backend (out of scope).
- `linux/arm64` is not built in v1 (real QEMU build-time cost); add to come only if Apple-Silicon demand shows up.
- GHCR package visibility may default to private on first push — see `docs/docker-container-support.md` §4.5 for the one-time manual fix.

## [0.14.2] - 2026-07-13

[0.14.2]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.14.2

Agent-guidance tuning (tool descriptions only — no index, schema, or behavior change), from field observation of a weaker model's tool-call transcript. Reduces redundant `grep_module_docs` re-verification and zero-match greps.

### Changed

- **New "Call economy" section in the server instructions.** Explicit budget guidance: call `get_module("<name>")` directly for an obvious service (skip `search_modules`); one `get_module(sections=["inputs"])` is the authoritative current variable table — do not re-verify names with `grep_module_docs`; a curated-catalog requirement should cost ~1–2 calls, not 3–4 (the observed source of ~19 redundant calls / a 45-vs-26 call blowup on a weaker model).
- **`get_module` — "trust the head".** The head/`sections` values are stated as the current authoritative doc values so agents use them directly instead of re-confirming with `grep_module_docs`.
- **`grep_module_docs` — input rendering hint.** Documents that assembled inputs are markdown LIST items (`- <name> | <type> | <default> | <description>`), not pipe-table rows; match the bare identifier and do not anchor with `^` or assume a leading `|` (the observed source of zero-match greps on present variables).
- **`search_modules` Search Tips — score disambiguation.** Added guidance to prefer the higher-scored match on the more specific requirement term and to read both descriptions for the distinguishing use-case (e.g. memory-db vs elasticache).
- **Server instructions — dropped the hardcoded catalog count** ("54 community terraform-aws-modules" → "community terraform-aws-modules") so it can no longer go stale as the catalog grows.

## [0.14.1] - 2026-07-13

[0.14.1]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.14.1

Catalog coverage: adds the `wafv2` (AWS WAF v2) module, closing a real gap where the right answer — a web application firewall — existed as an official `terraform-aws-modules/wafv2/aws` module on the registry but was absent from the curated catalog, so `search_modules`/`modules_list` could not surface it.

### Added

- **`wafv2` module (55th in the catalog).** Curated documentation for `terraform-aws-modules/wafv2/aws` (v2.1.0): Web ACL root module (declarative `rules` map, `REGIONAL`/`CLOUDFRONT` scope, managed rule groups, rate-based rules, CAPTCHA/challenge, logging) plus its eight submodules (`ip-set`, `regex-pattern-set`, `rule-group`, `logging-configuration`, `web-acl-association`, `web-acl-rule`, `web-acl-rule-group-association`, `api-key`). Searchable by keyword (`web-application-firewall`, `waf`), exact name, and natural language ("web application firewall protecting against sql injection and xss").

### Changed

- **Search index extended incrementally, not rebuilt.** The new doc's embedding was appended to the shipped index; the existing 54 embeddings are byte-identical, so the tuned golden set is unaffected (no e5 drift — the failure mode that gates every full rebuild). Catalog size references (README, e2e/count assertions) updated 54 → 55.

### Tests

- Full suite: 775 tests (752 passing; 23 skip — 6 opt-in live without `RUN_REGISTRY_BENCHMARK=1`, plus 17 docs with no submodule inventory skipped by the schema guard; `wafv2` carries an inventory so it is not among them).
- `wafv2` added to the searchability golden set (now 55 × 3 = 165 labeled queries, still 100% top-3) and to the per-doc schema guards; catalog-count assertions bumped to 55.

## [0.14.0] - 2026-07-13

[0.14.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.14.0

Submodule reachability: closes the recurring gap where the right answer is a submodule (e.g. an IAM role assumable via GitHub OIDC → `iam//modules/iam-role`) that `search_modules` — one record per top-level module — can never return directly. Both changes reuse data the curated docs already carry; the index is untouched, so there is no embedding drift.

### Added

- **Submodule inventory inline in the orientation head (A1).** For a module that carries submodules, the default `get_module` head now inlines the compact `## Submodules` inventory — each submodule's name, purpose, and pinnable source string (`terraform-aws-modules/iam/aws//modules/iam-role`) — so the moment search lands on the parent, the head answers "here are the submodules, pick one, here's the source to pin." Only the compact inventory is inlined; the far larger `## Submodule N:` deep-dive sections stay out of the head (request one by name, or via the submodule address below). Implemented as a head-assembly change (`extra_exact_titles` on `filter_module_sections`); no index change.
- **`get_module` accepts a submodule address (A3).** `get_module("iam//modules/iam-role")` (or the full `terraform-aws-modules/iam/aws//modules/iam-role`) returns an orientation head **scoped to that submodule's section** — parent core context plus the one submodule — instead of the whole 895-line parent doc. An unknown submodule degrades gracefully to core context plus a footer listing the real submodule titles.

### Changed

- Server `instructions`, the `get_module` tool description, `module_identifier` field, and docstrings document the submodule-address form and the inline inventory.

### Deferred

- **Parent keyword-enrichment did not ship.** The plan gated it behind a control rebuild of the search index; that rebuild — with **zero** doc changes — drifted the e5 embeddings enough to drop one golden-set target (`lambda` by keyword), confirming the committed index is not bit-reproducible from current deps. Rather than ship a drifted index, enrichment is deferred to a dedicated, separately-validated index migration. A1 and A3 need no rebuild and are unaffected.

### Tests

- Full suite: 765 tests (742 passing; 23 skip — 6 opt-in live without `RUN_REGISTRY_BENCHMARK=1`, plus 17 docs with no submodule inventory skipped by the new schema guard).
- New: A1 inventory-in-head + `extra_exact_titles` exactness; A3 `_parse_submodule_address` table + scoped-head / full-id / graceful-miss; a per-doc schema guard that every doc with a `## Submodules` inventory surfaces it in the head.

## [0.13.0] - 2026-07-13

[0.13.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.13.0

Documentation-escalation guidance: makes the compact → full → source tier boundary a mechanical decision instead of a guess, and corrects the skills' description of `get_module`'s 0.12.0 default.

### Added

- **Honest-limits pointer in every `get_module` response.** The footer now states that the curated doc is a selected subset and points to the completeness/exactness tier explicitly: complete inputs/outputs (every variable, exact type & default) and examples → `grep_module_docs` (with the Module ID shown above); resource-creation conditions (`count`/`for_each` gating) → module source. It also warns not to assert an exact default/type/existence from the summary or from memory when a wrong value would break `apply`. This converts "false confidence" into a cheap, explicit escalation decision (design §5.4).

### Changed

- **Skills aligned with the 0.12.0 orientation-head default.** `aws-terraform-modules` and `tf-module` no longer describe `get_module` as returning "the full document / complete inputs and outputs" by default — they orient on the compact head, pull `sections=["inputs", ...]` for the interface, and escalate to `grep_module_docs` for completeness/exactness and when reproducing an existing resource (greenfield-vs-brownfield prior; never assert an exact default/type from the summary or memory). `tf-stack`, `tf-migrate`, and `tf-module-upgrade` got the same one-line correction. All already referenced `grep_module_docs`; this fixes their `get_module` mental model.

### Tests

- Full suite: 692 tests, green (686 passing; 6 opt-in live tests skip without `RUN_REGISTRY_BENCHMARK=1`).

## [0.12.0] - 2026-07-13

[0.12.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.12.0

Retrieval-efficiency & orientation release, driven by a field experiment running `get_module`/`grep_module_docs` through a 14-module refactoring. Changes `get_module`'s **default response shape** (see **Changed**).

### Changed

- **`get_module` returns a compact orientation head by default** instead of the full document. The head carries the always-included core sections (Description, Module Information, Notes for AI Agents, and Important Gotchas where the doc has it) plus Key Features, Main Use Cases, an actionable exact **version-pin hint**, and a footer with the **full section inventory** — an explicit menu of the logical keys and every heading in the doc — so the next call knows exactly what it can request. ~9–10k chars even for the largest modules (vs 34–50k full), so a first orientation call never overflows the client. Pass `sections=["all"]` (or `"full"`/`"everything"`) for the complete document, or scoped keys for specific parts. **Behavior change**: callers that relied on full-document-by-default should now pass `sections=["all"]`.

### Fixed

- **`get_module(sections=[...])` now resolves `inputs`/`outputs`/`examples` on every doc** (previously failed on 15/54). Docs that bundle their interface into a combined `Main Module:`/`Root Module:` section (e.g. `s3-bucket`, `lambda`, `vpc`) or spread it across submodules (e.g. `iam`, `cloudwatch`, `fsx`) reported these keys as "not found", causing a wasteful full-document re-fetch. The keys now fall back to the doc's interface-bearing sections.
- **`get_module` surfaces the exact latest version as an actionable pin** in the orientation head, so an agent pins `= X.Y.Z` instead of copying a `~> X.0` range from a usage example.
- **`sns.md`**: rewrote the `create_topic_policy`/`topic_policy` documentation to spell out the two distinct policy mechanisms — a generated standalone `aws_sns_topic_policy` when `create_topic_policy = true` (in which branch `topic_policy` is ignored) vs the inline `aws_sns_topic.policy = var.topic_policy` when `false`; a custom full policy goes through `source_topic_policy_documents` + `enable_default_topic_policy = false`. The previous wording read as self-contradictory and led agents to silently drop a custom policy. Verified against the module's `main.tf`.

### Tests

- New `tests/integration/test_doc_schema.py`: schema-integrity guards over all 54 curated docs — universal core headings present and unique (now including Key Features + Main Use Cases, the two headings the orientation head itself requests), a recognised interface scheme (split / combined `Main Module:` / submodule-only), `inputs`/`outputs`/`examples` resolving for every doc, and the orientation head reporting no missing sections. Fails CI the moment a future doc's headings would break `get_module` section filtering.
- Added a `Main Use Cases` section to `ebs-optimized.md` (the only doc that lacked one) so the orientation head is clean on all 54 docs.
- Full suite: 691 tests, green (685 passing; 6 opt-in live tests skip without `RUN_REGISTRY_BENCHMARK=1`).

## [0.11.1] - 2026-07-12

[0.11.1]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.11.1

Data-quality patch: corrects the `Latest Version` of every curated module doc against the Terraform Registry and rebuilds the search index. Every `Module ID` was verified valid.

### Fixed

- Corrected four docs that claimed a **non-existent newer version**: `batch` 3.1.0→3.0.3, `dms` 2.6.1→2.6.0, `global-accelerator` 3.0.1→3.0.0, `lambda` 8.8.1→8.8.0.
- Added the missing `Latest Version` bullet to `atlantis` (5.1.0).
- Stripped trailing annotation text from 18 `Latest Version` bullets so the value the server reports (and chains into `grep_module_docs`) is a clean version number; compatibility details remain in the dedicated `Compatibility` bullet.
- Refreshed the `latest_version` metadata in `model/tfmod_e5_small_index.pkl` **in place** (embeddings/BM25 untouched — a full rebuild with the upgraded sentence-transformers/transformers drifts semantic rankings and would need the golden set re-tuned); all 54 docs now carry a valid `Module ID` and a `Latest Version` matching the registry.

## [0.11.0] - 2026-07-12

[0.11.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.11.0

Compatibility release: lowers the Python floor to 3.12 and moves to FastMCP 3.x — the latter genuinely fixes the three FastMCP advisories that 0.10.0 could only triage as unreachable. No runtime API changes.

### Changed

- **Python floor 3.13 → 3.12** (`requires-python = ">=3.12"`). `numpy`'s own `>=3.12` floor makes 3.12 the lowest viable version; CI now runs the test suite on a `["3.12", "3.13"]` matrix. mypy target and trove classifiers updated (ruff already targeted py312).
- **FastMCP 2.x → 3.x** (`fastmcp>=3.2.0,<4`). The `<3` pin existed only because FastMCP 3.x used to fail on import (breaking fresh installs); that is resolved upstream (3.4.4 imports cleanly). The upgrade needed **no code changes** — the full suite passes on 3.x — and it closes the FastMCP OpenAPI/OAuth advisories (fixed in 3.2.0) and drops the transitively-flagged `diskcache`/`lupa` from the dependency tree.

### Tests

- Full suite: 361 tests, green on Python 3.12 and 3.13 with FastMCP 3.4.4 (6 opt-in live tests skip without `RUN_REGISTRY_BENCHMARK=1`; the 2 live `claude`-CLI e2e tests skip when the `claude` CLI is absent, e.g. in CI).

## [0.10.0] - 2026-07-12

[0.10.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.10.0

Security & supply-chain hardening release: adds a proportionate, GitHub-native security baseline and sweeps the dependency tree for known vulnerabilities. No runtime API changes.

### Security

- **Dependabot**: weekly version-updates for GitHub Actions plus repo-level security-updates for Python dependencies (auto-PRs on known vulnerabilities).
- **CodeQL default setup**: GitHub-managed SAST over the Python code on pull requests and a weekly schedule.
- **ruff `S` (flake8-bandit)** security lint enforced in CI; the single networked path (`tfmod_registry_docs.py`) now refuses any non-`https` URL before opening it.
- **Least-privilege `GITHUB_TOKEN`**: both workflows declare top-level `permissions: contents: read` (publish keeps job-scoped `id-token: write` for OIDC).
- **`SECURITY.md`** disclosure policy with GitHub Private Vulnerability Reporting enabled.

### Dependencies

- Upgraded pinned GitHub Actions to current majors: `checkout` v4→v7, `setup-uv` v5→v7 (with `activate-environment: true` for the v6+ implicit-venv change), `cache` v4→v6, `upload-artifact` v4→v7, `download-artifact` v4→v8 — the last clears the deprecated Node 20 warning in the publish job.
- Refreshed `uv.lock` to pull security-patched transitive dependencies (transformers 5.x, sentence-transformers, starlette, authlib, cryptography, …); raised the direct `nltk` floor to `>=3.9.4`.
- Triaged every open Dependabot alert against the server's actual runtime (MCP **stdio** transport, no auth provider configured, fixed embedding model, single hardcoded-host HTTPS fetch): none were reachable in an executed, attacker-influenced code path — the flagged web/auth stack (Starlette/Authlib/PyJWT/python-multipart) and model-download TLS libraries sit in code paths this server never runs.

### Tests

- Full suite: 361 tests (355 pass, 6 opt-in live tests skip unless `RUN_REGISTRY_BENCHMARK=1`), verified against the upgraded dependency set. Added `tests/integration/test_security_config.py` — asserts the Dependabot config, SECURITY.md reporting policy, both workflows' least-privilege permissions, and that the publish job retains its OIDC `id-token: write` grant.

## [0.9.0] - 2026-07-12

[0.9.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.9.0

The skills-integration release: 0.8.0 shipped `grep_module_docs` but left every plugin skill on pre-0.8.0 guidance. This release teaches the skills and subagents **when to escalate** from the compact curated `get_module` doc to an exact, version-pinnable quote from the live registry docs — and adds a direct `/tf-grep` command.

### Added

- **New user-invoked skill `/tf-grep <module> <pattern>`** — grep the live registry documentation of any module (version-pinnable, non-AWS namespaces too) for an exact quote. Resolves a bare name to a `module_id` via `search_modules` or takes a full `namespace/name/provider` coordinate directly, detects an optional pinned version, and returns the matched lines with section label, line number, and context. Ships a Codex binding.
- **Grep-escalation guidance across all seven skills and both subagents**, driven by one shared model (compact doc = overview → `grep_module_docs` = proof) with four canonical triggers:
  - A variable is **absent from the curated doc** → grep the name before calling it dead. This replaces the pre-0.8.0 "confirm via the registry link in the doc" cop-out in `tf-review`, `tf-module-upgrade`, `tf-migrate`, `tf-diff-reviewer`, and `tf-log-analyst` — an agent cannot follow a link mid-review, so those findings previously stayed permanently "unconfirmed".
  - The **project pins an older version** → grep at that `version`, not latest. Upgrade audits now grep both the pinned and the latest version; that diff is the audit.
  - The **module is outside the curated AWS catalog** (cloudposse, any namespace) → grep its live docs instead of surrendering with "not indexed".
  - A claim **rests on an exact default/type** → quote the line (`scope=["inputs"]` / `["outputs"]`) instead of paraphrasing from memory.
- **`verified-against-live-doc`** confidence level in the `tf-log-analyst` subagent, between `verified-against-doc` and `inferred-from-error`.
- **Contract regression tests** (`test_model_invoked_skills_reference_grep_tool`, `test_agents_reference_grep_tool`) asserting every model-invoked skill and both subagents reference `grep_module_docs`, so a future skill edit cannot silently drop the integration.

### Changed

- README skills table: "Seven skills" → "Eight skills" with the `/tf-grep` entry; test counts refreshed.

### Tests

- Full suite: 355 tests (349 pass, 6 opt-in live tests skip unless `RUN_REGISTRY_BENCHMARK=1`).

## [0.8.0] - 2026-07-12

[0.8.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.8.0

The live-registry release: the server reaches beyond its curated offline catalog. A new grep tool pinpoints lines in the full, current documentation of **any** Terraform Registry module — version-pinnable, cached, and returning matches with context instead of dumping 100k-token documents into the agent's context window.

### Added

- **New MCP tool `grep_module_docs(module_id, pattern, version=None, case_sensitive=False, context_lines=2, scope=None, max_matches=50, refresh=False)`** — regex-greps the live documentation of any Terraform Registry module (`namespace/name/provider`), not just the curated AWS catalog. Fetches the module detail from the registry API, assembles README + inputs/outputs/resources rows + every submodule and example into one greppable text, and returns only the matching lines with section label, line number, and surrounding context. A zero-match response includes `available_sections` for follow-up queries. Built for surgical lookups: an exact variable default in a pinned older version, a submodule input, a non-AWS module.
- **Disk cache for assembled registry docs**: pinned versions are immutable and cached forever; `latest` is cached for `doc_cache_ttl_hours` (default 24h). Location `${TFMODSEARCH_CACHE_DIR:-${XDG_CACHE_HOME:-~/.cache}}/tfmodsearch/registry_docs`, overridable via `config.yaml` (`doc_cache_dir`, `doc_cache_ttl_hours`); `refresh=True` bypasses the cache.
- **`module_id` and `latest_version` fields on `search_modules` and `modules_list` results** — registry coordinates parsed from a new explicit `**Module ID**` header bullet backfilled into all 54 curated docs (with a fallback to the root `**Source**` bullet), so an agent can chain `search_modules → grep_module_docs` without guessing coordinates. Index rebuilt with the new fields.
- **Two new source modules** with a strict boundary: `src/tfmod_registry_docs.py` (registry client: fetch + document assembly + disk cache — the **only** networked module, stdlib `urllib` only, zero new dependencies) and `src/tfmod_doc_grep.py` (pure offline grep engine). The curated `search_modules`/`get_module`/`modules_list` tools remain fully offline.
- **Registry Search Comparison benchmark** in the README: top-1/top-3 retrieval on the full 54-module/162-query golden set vs. the public Terraform Registry search API (the same endpoint HashiCorp's `terraform-mcp-server` wraps). TFModSearch: 92% top-1 / 100% top-3 overall; registry keyword search: 42.6% / 42.6% (official namespace) — the gap is entirely in descriptive queries, where semantic search finds modules that keyword search never surfaces. Reproducible via `RUN_REGISTRY_BENCHMARK=1 pytest tests/integration/test_registry_comparison.py`.

### Tests

- 16 new tests for the grep feature: pure grep engine (regex, case-insensitivity, context lines, section labeling, `scope`, `max_matches` cap, invalid-regex error), registry client + cache semantics with an injected fetcher — no real network (pinned-forever, latest-TTL, `refresh`), tool wiring, a header invariant (every curated doc's `Module ID` equals its root registry `Source`), and a 2-test opt-in live smoke test against the real registry.
- Full suite: 345 tests (6 opt-in live tests skip unless `RUN_REGISTRY_BENCHMARK=1`).

## [0.7.0] - 2026-07-11

[0.7.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.7.0

Driven by field feedback from a real agent session: search ranking and doc freshness earned their keep, but full-document `get_module` responses were heavier than needed and top-3 was tight for ambiguous queries.

### Added

- **`top_k` parameter on `search_modules`** (1–10, default 3) — raise it for ambiguous queries like `"iam"` where three results are too tight to disambiguate.
- **`sections` parameter on `get_module`** — fetch only the parts you need instead of the full document (large modules run to 10k+ tokens in full; `s3-bucket` with `sections=["inputs"]` is ~5x smaller). Accepts logical keys (`inputs`, `outputs`, `examples`, `submodules`, `features`, `use-cases`, `best-practices`, `resources`) or case-insensitive heading substrings (e.g. `"karpenter"` for a single EKS submodule). Core context — description, pinned versions, notes for AI agents, gotchas — is always included regardless of the request, and every filtered response ends with a footer listing the omitted sections, so nothing is silently hidden and the agent can request more.

### Changed

- **Normalized H2 headings across 14 module docs** to the canonical template names (`Main Input Variables`, `Main Outputs`, `Usage Examples`, `Best Practices`, `Important Gotchas`), eliminating naming variants (`Variables`, `Input Variables`, `Key Outputs`, `Critical Warnings and Gotchas`, `Important Notes`, `Recommendations`, `Complete Module Usage`, and two others). Heading renames only — no content changed; intra-doc anchor links updated; index rebuilt and the full searchability suite re-verified with no ranking regressions. This gives section extraction a single canonical heading set to key on.

## [0.6.0] - 2026-07-11

[0.6.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.6.0

The efficiency release: a smaller, faster embedding model matches the previous default's retrieval quality exactly, backed by a full-catalog benchmark and two keyword-matching fixes.

### Changed

- **Default embedding model switched from `BAAI/bge-base-en-v1.5` to `intfloat/e5-small-v2`**: benchmarked 5 candidate models against the full 54-module/162-query golden set (exact-name, keyword, and natural-language queries per module) using production search weights. `e5-small-v2` is the only smaller candidate that matches the old default's 100% success rate — at ~3x smaller (~138 MB vs ~419 MB) and ~3x lower query latency (~8ms vs ~23ms), with no weight retuning or query/passage prompt-prefix convention needed (both were tried; neither moved the needle on this corpus). See the "Embedding Model Comparison" section in README.md for the full comparison table, including the other candidates evaluated (`gte-small`, `bge-small-en-v1.5`, `all-MiniLM-L12-v2`) and why they weren't selected.
- **Pre-built index renamed**: `model/tfmod_bge_base_index.pkl` → `model/tfmod_e5_small_index.pkl`, consistent with the existing gte-small→bge-base rename precedent.
- **`test_model_comparison.py` extended** to a 3-way comparison (`gte-small`, `bge-base-en-v1.5`, `e5-small-v2`); the pairwise summary logic was generalized to N models.

### Fixed

- **Closed 3 keyword-matching gaps** found during the model comparison: added `virtual-private-cloud` to `vpc.md`, `automation` + `workflow` to `atlantis.md`, and `storage` + `optimization` to `ebs-optimized.md`. These were queries whose tokenized form (e.g. two space-separated words) never matched an existing hyphenated compound keyword (e.g. `terraform-automation`), so the keyword-scoring component silently contributed nothing and the query relied on embedding quality alone. The fix benefits every embedding model uniformly, not just the new default.

## [0.5.0] - 2026-07-11

[0.5.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.5.0

The skills release: the plugin grows from two skills to a full toolkit — seven skills and two subagents covering the whole lifecycle of working with community modules: author, scaffold, migrate, upgrade, review, and troubleshoot.

### Added

- **`tf-migrate` skill** — detects clusters of hand-written `aws_*` resources that a community module covers (security group + rules, VPC + subnets + NAT, S3 + policies) and proposes a replacement: multiple search angles, attribute-by-attribute coverage mapping against the current doc, an explicit "not covered" list, and state-migration caveats (`moved` blocks / `terraform state mv`). Proposal only — never rewrites.
- **`tf-module-upgrade` skill** — audits existing module blocks against current documentation: version drift, dead/renamed variables, deprecations, changed defaults. Severity-ranked report with exact fixes; applies changes only on approval.
- **`tf-review` skill** — reviews a git diff/branch/PR's module usage: variables exist, required inputs present, versions pinned, deprecations; flags raw-resource clusters a module could replace. Review only, scope-disciplined (no style nits).
- **`tf-stack` skill** (user-invoked) — scaffolds a multi-module stack from a requirement with correct output→input wiring (vpc subnets → rds/alb inputs), pinned versions, and an explicit list of what was left out.
- **`tf-troubleshoot` skill** — diagnoses `terraform plan/apply/init` failures against current module documentation, with a bundled prefilter script.
- **`scripts/extract_tf_errors.py`** (inside tf-troubleshoot) — stdlib-only prefilter that reduces terraform logs of any size to structured diagnostics (severity, summary, file:line, module addresses); handles human-readable `╷│╵` blocks, `-json` output, and bare CI error lines.
- **Two plugin subagents** (Claude Code): `tf-log-analyst` (log forensics: prefilter → verify each finding via get_module → compact root-cause report) and `tf-diff-reviewer` (reads the diff in its own context, returns a findings table). Large logs and diffs never enter the main conversation; skills degrade gracefully to inline analysis on Codex.
- **Maintainer skills** in `.claude/skills/` (now committed via a `.gitignore` exception): `refresh-module-docs` (the multi-agent corpus refresh pipeline, codified) and `add-module` (onboard a new module: doc, keywords, index rebuild, searchability verification).
- **CI workflow** (`.github/workflows/ci.yml`): lint (pre-commit, all files) and the full test suite on every push and pull request, with dependency and embedding-model caching. The publish workflow now calls it as its first job — **PyPI publication is gated on a green test run**. CI status badge added to the README.

### Changed

- **Narrowed the `aws-terraform-modules` skill trigger to authoring** — reviewing, upgrading, migrating, and troubleshooting now have dedicated skills; an e2e test enforces that trigger keywords (reviewing, pull request, upgrade, fails) are claimed by exactly one model-invoked skill.

### Fixed

- **Pinned `fastmcp<3`**: fastmcp 3.x (released upstream) fails on import with the current MCP SDK, which broke fresh `uvx tfmodsearch` installs of 0.4.0 (the dependency was unbounded). Caught by the new CI gate before publication; the server targets the fastmcp 2.x API.

### Tests

- E2E suite grew from 20 to 49 tests: prefilter script tests against a fixture log (all three formats), plugin agent contracts, per-skill Codex binding checks, user-invoked vs model-invoked invariants, trigger-disjointness check, maintainer-skill checks (including that they are not gitignored), and live-install verification extended to all seven skills and the shipped agent files. Full suite: 288 tests passing.

## [0.4.0] - 2026-07-11

[0.4.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.4.0

The distribution release: the project is renamed to **tfmodsearch**, published to PyPI, and ships plugins for Claude Code and Codex CLI that bundle the MCP server with agent workflow skills.

### Changed

- **Project renamed to `tfmodsearch`** (repository, PyPI package, and primary command). The GitHub repository moved to `SantyagoSeaman/tfmodsearch`; old `aws-tf-modules-mcp-server` URLs redirect automatically.
- **New console commands**: `tfmodsearch` (MCP server) and `tfmodsearch-cli` (indexing/search CLI). The previous `aws-tf-modules-mcp-server` and `tfmod-search-cli` commands are kept as deprecated aliases.
- **Trimmed the published wheel** from ~11 MB to ~1.6 MB: it now ships only the production index (`model/tfmod_bge_base_index.pkl`) and the curated `modules/terraform-aws-modules/` docs, excluding the legacy gte-small index, work-in-progress docs, and internal templates.
- **Rewrote the MCP server `instructions`**: corrected the stale catalog size, fixed grammar, and added explicit workflow steering ("search before writing Terraform; use documented variable names, not memorized ones"). The advertised server version now derives from the installed package metadata instead of a hardcoded string.

### Added

- **PyPI publication** with Trusted Publishing: a `publish.yml` GitHub Actions workflow builds and publishes to PyPI on version tags via OIDC (no API tokens), with a tag-vs-version consistency check.
- **Claude Code plugin** (`/plugin marketplace add SantyagoSeaman/tfmodsearch` → `/plugin install tfmod-search@tfmodsearch`): auto-configures the MCP server via `uvx tfmodsearch` and ships two skills.
- **Codex CLI plugin** with the same two-command install, plus an `agents/openai.yaml` declaring the MCP tool dependency for implicit skill invocation.
- **Skills** (portable SKILL.md format, shared by both plugins):
  - `aws-terraform-modules` — auto-invoked when writing/reviewing Terraform for AWS: search first, write from current docs, pin module versions, prefer community modules.
  - `tf-module` — user-invoked lookup (`/tf-module s3 bucket with lifecycle rules`) returning a ready-to-paste module block with current variable names.
- **`--warmup` flag** for the MCP server: pre-downloads the embedding model (~220 MB), loads the index, runs a test query, and exits — keeps first server startup within MCP client timeouts.

### Fixed

- **`get_module` no longer guesses**: unknown module names previously fell through to hybrid search and silently returned the highest-scoring module's documentation (a hallucinated name could return the lambda docs). Name lookup is now exact-match first, then unique-substring; unknown or ambiguous names return an error listing the closest matches and directing the caller to `search_modules`.

### Tests

- **New end-to-end suite** (`tests/e2e/`, 20 tests): full MCP stdio protocol sessions against a spawned server process (initialize handshake, tool discovery, all three tools, security rejections, `--warmup`), wheel payload/metadata/entry-point verification, a `uvx` packaged-server smoke test from a foreign directory, plugin manifest and skill contract checks for both the Claude Code and Codex layouts, and a live `claude plugin` install into an isolated config. Full suite: 259 tests passing.

### Documentation

- README: new plugin-first installation section, Codex CLI integration guide (with `startup_timeout_sec` note), `claude mcp add` one-liner, AGENTS.md/CLAUDE.md steering snippet, and a PyPI badge. All install configs now use the published `tfmodsearch` package instead of `git+https` URLs.

## [0.3.0] - 2026-07-11

[0.3.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.3.0

This release refreshes the entire module catalog against the latest upstream `terraform-aws-modules` versions, rebuilds the pre-built search index, and overhauls the README. It also rolls up the previously unreleased 0.2.1 changes.

### Changed

- **Full documentation refresh for all 54 modules**: Every document in `modules/terraform-aws-modules/` was regenerated from the current Terraform Registry / GitHub source. Notable version and API updates include:
  - `security-group` → 6.0.0 — major rearchitecture: per-rule `aws_vpc_security_group_ingress_rule`/`egress_rule` resources replace inline rule blocks
  - `eks` → 21.24.0 — post-v21 variable names (`name`, `kubernetes_version`, `addons`, `compute_config`); no default add-ons are bootstrapped
  - `lambda` → 8.8.1, `s3-bucket` → 5.14.1 (new `vectors` submodule), `iam` → 6.6.1, `rds` → 7.2.0, `ec2-instance` → 6.4.0, `alb` → 10.5.0, `apigateway-v2` → 6.1.0, `vpc` → 6.6.1, and others
  - Corrected stale or incorrect variable names, defaults, and examples that could have produced invalid Terraform (e.g. EKS pre-v21 variables, Lambda Function URL configuration, RDS `create_db_subnet_group`/`storage_type` defaults, IAM `iam-role` trust-policy variables)
  - Re-curated keyword lists to the 10–20 most relevant terms per module
- **Rebuilt the pre-built search index** (`model/tfmod_bge_base_index.pkl`) to reflect the refreshed documentation.

### Added

- Canonical service-name keywords to improve retrieval for common full-name queries: `application-load-balancer` (alb), `relational-database` (rds), `simple-notification-service` (sns), `identity`/`access-management` (iam), and `vpn` (vpn-gateway).

### Fixed

- **README accuracy**: corrected the pre-built index filename (`tfmod_bge_base_index.pkl`, previously shown as `tfmod_index.pkl` in several places), the catalog module count (added the missing `emr` module — now a consistent 54), the local-install commands (`pip install -e .` / `uv pip install -e .`), stale test counts, and the `get_module` tool terminology.

### Documentation

- Added a "Why TFModSearch?" value-proposition section, an end-to-end `search_modules` → `get_module` workflow example, an explicit note that the pre-built index and module docs ship inside the installable package, and clarification of the default search weights.

### Tests

- Relaxed `test_module_searchable_by_keyword` to assert the target module appears in the **top-3** results — matching `search_modules`'s documented top-3 return contract and the existing natural-language test — rather than strictly ranking #1. A few semantically adjacent module pairs (e.g. security-group vs network-firewall for "firewall rules") legitimately rank a sibling first while keeping the target in the top-3. Full suite: 239 tests passing.

## [0.2.1] - 2026-01-26

[0.2.1]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.2.1

### Added

- **Configurable Log Level**: New `log_level` option in `config.yaml` (default: INFO)
  - Configurable via config file or CLI `--log_level` argument
  - New `ConfigLoader.load_log_level()` method with standard precedence (CLI > YAML > default)

- **Quick Install via uvx**: Added simplified installation method using `uvx`
  - No repository cloning required
  - Single config line: `"command": "uvx", "args": ["git+https://github.com/..."]`
  - Added uv installation instructions

### Fixed

- **Silenced Noisy Third-Party Loggers**: FastMCP internal loggers now set to WARNING
  - `fakeredis`, `docket`, `asyncio` no longer spam DEBUG output
  - Server startup is now clean and quiet

### Documentation

- Updated README with `uvx` as recommended installation method
- Added troubleshooting note for full path to `uvx` when not in PATH
- Updated CLAUDE.md with new `log_level` config option

## [0.2.0] - 2026-01-25

[0.2.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.2.0

### Changed

- **Embedding Model Upgrade**: Switched default model from `thenlper/gte-small` to `BAAI/bge-base-en-v1.5`
  - Better retrieval performance with 768-dimensional embeddings (vs 384)
  - Improved similarity distribution (addresses narrow clustering issue)
  - BGE v1.5 specifically optimized for retrieval tasks with hard negatives training
  - Model size: ~220MB (vs ~67MB for gte-small)

- **Optional Query Instruction Support**: Added configurable query instruction prefix for BGE models
  - New `query_instruction` parameter in `compute_scores()` function
  - Configurable via `config.yaml` or CLI `--query-instruction` argument
  - Uses modern sentence-transformers `prompt` parameter in `model.encode()`
  - Disabled by default (BGE v1.5 works well without instruction)
  - Instruction: `"Represent this sentence for searching relevant passages: "`

- **Default Index Path**: Changed from `tfmod_gte_small_index.pkl` to `tfmod_bge_base_index.pkl`
  - All references updated across codebase, CLI, and tests
  - Pre-built index now included at `model/tfmod_bge_base_index.pkl`

- **Module List Description**: `modules_list` tool now uses `extract_purpose()` for cleaner descriptions
  - Extracts Purpose field from Module Information section
  - More concise and relevant module descriptions in catalog listing

- **Dependency Updates**:
  - Updated `numpy` from `>=2.3.3` to `>=2.4.1`
  - Updated `sentence-transformers` from `>=5.1.1` to `>=5.2.0`

### Added

- **Integration Guides**: Comprehensive setup instructions in README
  - Claude Code CLI integration with `claude mcp add` command
  - Claude Desktop configuration for macOS
  - GitHub Copilot integration for VS Code (requires VS Code 1.99+)
  - Step-by-step setup and troubleshooting commands

- **New Search Library Functions**:
  - `extract_purpose(text, max_length)`: Extract Purpose field from Module Information section
  - `DEFAULT_MODEL_NAME` constant: Default embedding model identifier
  - `BGE_QUERY_INSTRUCTION` constant: Optional query prefix for BGE models

- **Configuration Loader**: New `ConfigLoader.load_query_instruction()` method
  - Supports precedence: CLI > YAML > default (None)
  - Proper logging for configuration source

- **Build Configuration**: Added hatch wheel build settings in `pyproject.toml`
  - Configured `tool.hatch.build.targets.wheel` for proper package distribution
  - Source mapping from `src/` directory

- **Model Comparison Tests**: New test file `tests/integration/test_model_comparison.py`
  - Compares embedding model performance (gte-small vs bge-base-en-v1.5)
  - Tests across different query types (1-word to long natural language)
  - Timing measurements and success rate analysis

### Fixed

- **ServerState Initialization**: Added `query_instruction` parameter support
  - Properly passed through `ServerStateManager.initialize()`
  - Included in state logging output

### Documentation

- **Module Documentation Updates**: Refreshed all 54 Terraform AWS module docs
  - Updated module versions and feature descriptions
  - Improved formatting and consistency across modules
  - Enhanced best practices and use case sections

- **README Improvements**:
  - Reorganized Quick Start section with integration-specific guides
  - Updated all code examples to use new model and index paths
  - Added GitHub Copilot and VS Code MCP documentation links

- **Configuration Comments**: Enhanced `config.yaml` with detailed comments
  - Documented query instruction usage and BGE model notes
  - Added model configuration guidance

### Notes

- **Index Rebuild Required**: After upgrading, rebuild the search index with the new model
- **Index Size**: Increased from ~4.5MB to ~9MB due to larger embedding dimensions (768 vs 384)
- **Performance**: First query ~2-3s (model loading), subsequent queries ~0.02s
- **Breaking Change**: Default index path changed - update any hardcoded paths

## [0.1.2] - 2025-10-13

[0.1.2]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.1.2

### Changed

- **Parser Architecture Refactoring**: Complete rewrite of document parsing system
  - Removed YAML frontmatter dependency in favor of pure regex-based parsing
  - Created `ModuleDocumentParser` class with two-strategy parsing approach:
    1. "## Module Information" section parsing (preferred)
    2. Inline keywords search (fallback)
  - Fixed module name parsing to strip backticks from Markdown formatting
  - Removed YAML frontmatter blocks from 46 module documentation files
  - Simplified codebase by eliminating `yaml` library dependency

- **Search Algorithm Improvements**: Enhanced hybrid search for better ranking accuracy
  - **Minmax Normalization for Semantic Search**: Added min-max normalization to cosine similarities
    - Spreads small embedding differences (0.89-0.92) into full 0-1 range for better discrimination
    - Addresses limitation of `thenlper/gte-small` model's narrow similarity clustering
    - All scoring components now equally normalized (keywords, BM25, semantic, exact match)
  - **Adaptive Query Scaling**: Implemented logarithmic scaling for BM25 and semantic scores
    - Formula: `log(len(matched_keywords) + 1, base=3)` dampens scores for short queries
    - Reduces BM25 noise on 1-2 word keyword queries where lexical matching is unreliable
    - Improves ranking for precise keyword searches (e.g., "tgw", "firewall", "ssh-keys")

- **Search Index**: Rebuilt index with refactored parser
  - Index size optimized from 4.58MB → 4.51MB (1.5% reduction)
  - All 54 modules now use consistent text-based parsing
  - Maintains 1,529 unique keywords across corpus

### Added

- **Comprehensive Test Suite**: Created extensive integration tests for search quality
  - New file: `tests/integration/test_all_modules_searchable.py` (387 lines, 169 tests)
  - **ModuleTestCase Dataclass**: Explicit document→query triple linkage
    - Each module linked to: keyword query, exact name query, natural language query
    - Clear traceability for test failures with document paths and query types
  - **Parametrized Tests**: 162 tests (54 modules × 3 query types)
    - `test_module_searchable_by_keyword`: Verifies keyword-based search
    - `test_module_searchable_by_name`: Validates exact module name matching
    - `test_module_searchable_by_natural_language`: Tests semantic search quality
  - **Quality Validation Tests**: 7 additional tests
    - Module completeness (keywords, names, content)
    - Data integrity (no duplicates, sufficient keyword vocabulary)
    - Search quality metrics (average keyword count, vocabulary size)
  - **NLTK Initialization**: Created `tests/conftest.py` for pytest setup
    - Automatic NLTK data initialization before test session
    - Eliminates `punkt_tab` resource errors
  - **Test Results**: 160/169 passing (94.7% pass rate)
    - 9 failures due to expected search quality variations (keyword collisions, semantic ambiguity)

### Fixed

- **Module Name Parsing**: Resolved backtick capture in regex patterns
  - Changed pattern from `(.+?)` to `([^`]+?)` to exclude backticks from capture group
  - All module names now parse correctly without Markdown formatting artifacts
- **Parser Fallback Logic**: Improved reliability with dual-strategy approach
  - Primary strategy: Structured "## Module Information" section
  - Fallback strategy: Inline keyword search in document body
  - More resilient to documentation format variations

### Documentation

- **Test Coverage**: Added inline documentation for all test classes and methods
  - Detailed docstrings explaining test purpose and validation criteria
  - Examples of query types and expected behavior
- **Parser Documentation**: Enhanced ModuleDocumentParser class documentation
  - Strategy descriptions with regex patterns
  - Normalization and deduplication logic explained
- **Search Algorithm Notes**: Added comments explaining scoring improvements
  - Minmax normalization rationale and impact
  - Logarithmic scaling formula and use cases

## [0.1.1] - 2025-10-12

[0.1.1]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.1.1

### Changed
- **Expanded Module Catalog**: Search index now includes 54 Terraform AWS modules
- **Search Index**: Rebuilt index with all 54 modules
  - 1,535 unique keywords indexed
  - Enhanced semantic search coverage across AWS services

### Documentation
- Each new module includes:
  - Comprehensive descriptions with 2-3 paragraphs
  - 10-25 key features per module
  - 8-10 real-world use cases
  - 20-70+ best practices across multiple categories
  - Integration examples and code snippets
  - Links to official AWS documentation
  - AI agent implementation notes

## [0.1.0] - 2025-10-11

[0.1.0]: https://github.com/SantyagoSeaman/tfmodsearch/releases/tag/v0.1.0

### Added
- Initial release of TFModSearch MCP Server
- Hybrid search engine combining semantic embeddings, BM25, and keyword matching
- FastMCP-based server with stdio transport
- Three MCP tools: `search_modules`, `get_module`, `modules_list`
- CLI interface with `index` and `search` subcommands
- Support for Terraform AWS modules documentation
- Configurable search weights via YAML config
- Security features: path validation, access controls
- Comprehensive test suite (39 integration tests)
- Documentation with examples and integration guides
- Pre-commit hooks for code quality (ruff, mypy)
- Claude Desktop integration support

### Features
- **Hybrid Search**: Combines 4 scoring signals for accurate module discovery
- **CPU-Only Inference**: Uses `thenlper/gte-small` model for semantic embeddings
- **Fast Indexing**: Pre-built search index with BM25 and embeddings
- **Type Safety**: Full type hints with mypy checking
- **Comprehensive Documentation**: README, tests documentation, inline comments
