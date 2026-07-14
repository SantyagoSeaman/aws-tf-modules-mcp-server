# HTTP Transport (Streamable HTTP) + Shared Container Daemon — Design

**Date**: 2026-07-14
**Status**: Approved
**Target release**: 0.16.0 (minor)
**Supersedes/incorporates**: the maintainer draft `docs/http-transport-shared-container.md`
(2026-07-13); decisions confirmed interactively 2026-07-14.

## 1. Problem / Motivation

The server is stdio-only today (`app.run(transport="stdio")`, `src/tfmod_mcp_server.py:1889`).
stdio is one server process per client: the MCP client spawns the process and owns its lifecycle.
When a task fans out across N subagents, each spawns its own server → N processes → N embedding
model loads (~8 s each, each holding e5-small-v2 in RAM). The cost multiplies with fan-out; 6
concurrent cold starts have tripped the MCP handshake timeout in practice.

Streamable HTTP transport inverts the model: **one long-lived server, many clients connect by
URL**. The model + index load once; the main session and every subagent share that single
instance. This is instance-sharing that stdio structurally cannot provide.

Primary scenario (confirmed): **one local shared instance** on the developer's machine. Remote /
team deployment and auth are out of scope.

## 2. Decisions (confirmed interactively)

| Question | Decision |
|---|---|
| Transport flavor | **Streamable HTTP only** (`transport="http"` in FastMCP). Legacy HTTP+SSE is deprecated in the MCP spec since 2025-03 and is NOT implemented. |
| Mode selection | **CLI flags**, `--transport {stdio,http}` with default `stdio` (full backward compatibility), plus env fallbacks for container ergonomics. |
| Docker packaging | **One Dockerfile, one image, one tag.** `ENTRYPOINT ["tfmodsearch"]` already forwards run-time args; HTTP mode is `docker run <image> --transport http ...`. |
| Agent-side config | **Plugin stays stdio-only.** HTTP is an operator-managed mode configured via documented recipe (`claude mcp add --transport http ...`). No launcher bridge, no auto-start. |
| Default port | **8765** (draft's 8080 was marked "e.g."; 8080 collides with common dev services). |

## 3. Non-goals

- No change to the stdio default: no flag → behaves exactly as today. stdio stays the zero-ops
  default and the plugin default.
- No auth / TLS. The daemon binds loopback by default; remote exposure is separate security work.
- No change to search behaviour, tool signatures, the index, or the catalog.
- No legacy SSE transport.
- The daemon is NOT managed by the MCP client or the plugin — no auto-spawn, no launcher bridge.
- No changes to `plugins/tfmod-search/` (manifests keep their version bump only).

## 4. Part A — HTTP transport in the server

### 4.1 CLI / env configuration

`parse_arguments()` (`src/tfmod_mcp_server.py`) gains:

- `--transport {stdio,http}` — default from `TFMODSEARCH_TRANSPORT` env, else `stdio`
- `--host` — default from `TFMODSEARCH_HOST`, else `127.0.0.1`
- `--port` (int) — default from `TFMODSEARCH_PORT`, else `8765`

Precedence: CLI flag > env var > hardcoded default (consistent with the existing CLI > yaml >
default scheme; transport is a launch property, so config.yaml is deliberately not involved).

FastMCP 3.4.4 verified: `app.run(transport="http", host=..., port=...)` serves Streamable HTTP at
path **`/mcp`** (`fastmcp.settings.streamable_http_path`). The client URL is
`http://<host>:<port>/mcp`.

### 4.2 main() wiring

The entire initialization path (NLTK, config, index load, `ServerStateManager`, `--warmup`) stays
transport-agnostic. Only the final start branches:

```python
if args.transport == "http":
    # warm-once: load the embedding model BEFORE serving (see 4.3)
    search_modules_impl("vpc networking", state)
    logger.info(f"READY on http://{args.host}:{args.port}/mcp")
    app.run(transport="http", host=args.host, port=args.port)
else:
    app.run(transport="stdio")
```

Bind failure (port in use) surfaces as a clear error and non-zero exit.

### 4.3 Warm-once at startup

The embedding model loads lazily today (`_get_sentence_transformer` → `_MODEL_CACHE`). In HTTP
mode the model is warmed **once at startup, before `app.run()`**, by reusing the existing warmup
path (`search_modules_impl` test query), so the first client request is fast and the model loads
exactly once, deterministically. A `READY on http://host:port/mcp` log line marks readiness.
stdio mode keeps today's lazy behaviour (unchanged).

### 4.4 Concurrency safety (main code risk)

The HTTP server serves concurrent requests. After load, the index, BM25 corpus, and `_MODEL_CACHE`
are read-only → safe. Two write paths need care:

1. **`SentenceTransformer.encode()`** is not guaranteed thread-safe under concurrent calls →
   guard the query-embedding call with a `threading.Lock` (module-level in `tfmod_search_lib.py`,
   held only around `encode()`; negligible contention — query encode is ~10 ms).
2. **`grep_module_docs` disk cache** (`tfmod_registry_docs.py`): concurrent writes of the same
   cache file must not corrupt it → write via `tempfile` + `os.replace` (atomic on POSIX) if not
   already atomic. Worst case allowed: duplicate fetch; corruption is not allowed.

Acceptance gate: ~8 concurrent tool calls against one daemon all succeed with correct results and
exactly one model resident (see §7).

### 4.5 Binding / security posture

- Default bind `127.0.0.1`. Never default to `0.0.0.0`.
- If `--host` resolves to a non-loopback address, log a prominent WARNING (no auth — anyone
  routable can query). Binding `0.0.0.0` is intended only *inside* a container whose host port
  mapping restricts exposure (§5.2).

### 4.6 `/health` endpoint

`@app.custom_route("/health", methods=["GET"])` (verified available in FastMCP 3.4.4) returns
HTTP 200 with JSON: `{"status": "ok", "version": <package version>, "modules": <index doc count>}`.
Purpose: cheap liveness/readiness probe for `docker run -d` and scripted setups without an MCP
handshake. Served only in HTTP mode (custom routes are part of the HTTP app; stdio is unaffected).

## 5. Part B — Container + deployment recipe

### 5.1 Image: one Dockerfile, zero structural changes

- Add `EXPOSE 8765` (documentation-only) to the existing Dockerfile. No second stage, no second
  entrypoint, no new tag. `docker run -i --rm <image>` (stdio) keeps working identically.
- All baked assets (model, index, punkt_tab, `HF_HUB_OFFLINE=1`) apply to both modes — HTTP
  startup makes zero huggingface.co calls.

### 5.2 The daemon run command (documented recipe)

```bash
docker run -d --name tfmodsearch-http --restart unless-stopped \
  -p 127.0.0.1:8765:8765 \
  ghcr.io/santyagoseaman/tfmodsearch:0.16.0 \
  --transport http --host 0.0.0.0 --port 8765
```

- Inside the container the server binds `0.0.0.0` (binding loopback inside the container would
  make the published port unreachable); the security boundary is the host mapping
  `-p 127.0.0.1:8765:8765` — reachable only from the host's loopback. The §4.5 non-loopback
  warning is expected and documented as suppress-by-understanding in this context.
- Pin the image tag in shipped configs (not `:latest`).
- Readiness: poll `http://127.0.0.1:8765/health` or watch `docker logs` for the `READY` line.

### 5.3 docker-compose.yml

Ship a top-level `docker-compose.yml` encoding the §5.2 recipe (service `tfmodsearch-http`,
pinned image tag, restart policy, loopback port mapping, optional healthcheck hitting `/health`),
so the operator doesn't hand-write the run command. launchd/systemd units: out of scope (README
mentions `--restart unless-stopped` as the crash/reboot answer).

### 5.4 MCP client config (URL, not command)

```bash
claude mcp add --transport http --scope user tfmod-search http://127.0.0.1:8765/mcp
```

or in `.mcp.json` / client config:

```json
"mcpServers": {
  "tfmod-search": { "type": "http", "url": "http://127.0.0.1:8765/mcp" }
}
```

- Keep the server key `tfmod-search` when replacing the plugin entry so tool names
  (`mcp__tfmod-search__*`) are unchanged; do not run both the plugin stdio entry and the HTTP
  entry simultaneously (duplicate toolsets confuse agents) — documented explicitly.
- Lifecycle ownership stated plainly in docs: the operator owns the daemon; if it's down, clients
  fail to connect — no auto-spawn. That's the trade-off for instance sharing.

## 6. Documentation updates

- **README.md**: new "Shared HTTP instance" section — motivation (one model load for N sessions),
  the two-command recipe (docker run + claude mcp add), non-Docker variant
  (`tfmodsearch --transport http`), lifecycle ownership, localhost-only warning.
- **docs/docker-container-support.md**: HTTP mode section (same recipe, compose file pointer,
  0.0.0.0-inside/loopback-outside explanation).
- **docs/http-transport-shared-container.md**: replaced by this spec (draft removed from the
  working tree; content incorporated here).
- **CHANGELOG.md**: 0.16.0 entry.
- **CLAUDE.md**: transport paragraph in the MCP server section.

## 7. Acceptance criteria

1. **Backward compat**: no flag / `--transport stdio` → behaves exactly as today; the full
   existing test suite passes unmodified.
2. **HTTP serves**: `tfmodsearch --transport http --port <P>` starts; an MCP SDK
   `streamablehttp_client` session completes handshake, lists 4 tools, and gets correct results
   from `search_modules`, `get_module`, `modules_list` (and `grep_module_docs` wiring verified
   offline-safely).
3. **Warm-once**: model loads once at startup before serving; `READY` line logged; first request
   fast.
4. **Concurrency**: ~8 concurrent `search_modules` calls against one server all return correct,
   uncorrupted results; exactly one model instance loaded.
5. **/health**: returns 200 + version + module count while serving.
6. **Env fallbacks**: `TFMODSEARCH_TRANSPORT=http TFMODSEARCH_PORT=<P> tfmodsearch` serves HTTP;
   CLI flags override env.
7. **Non-loopback warning**: `--host 0.0.0.0` logs the warning; `127.0.0.1` doesn't.
8. **Docker**: the single image runs both modes (stdio smoke + HTTP daemon with `/health` and a
   real tool call over the published loopback port) — manual pre-release verification, same
   pattern as 0.15.x.
9. **Docs**: README + docker doc updated; compose file present and valid
   (`docker compose config`).

## 8. Testing plan

- **Unit/integration** (offline, no model): argument parsing (defaults, env fallback, CLI-over-env
  precedence), non-loopback warning logic, atomic cache write behaviour.
- **E2E** (`tests/e2e/`, real processes, pattern of existing stdio e2e): spawn
  `tfmodsearch --transport http --port <ephemeral>`, poll `/health`, then over
  `mcp.client.streamable_http`: handshake, tool discovery, `search_modules`, `get_module`,
  concurrent-calls test (8 parallel), env-fallback variant, and a default-invocation-is-stdio
  guard. Reuses the packaged-server spawn helpers where possible.
- **Docker**: manual pre-release check (build once, run stdio smoke + HTTP daemon + `/health` +
  tool call via SDK).

## 9. Risks / notes

- `SentenceTransformer.encode()` thread-safety — mitigated by the lock (§4.4.1); load-tested (§7.4).
- Registry doc-cache concurrent writes — mitigated by atomic replace (§4.4.2).
- No auth — mitigated by loopback-only default + warning + docs; never bind routable interfaces
  without a reverse proxy (documented).
- Single point of failure in shared mode — operator-owned; `--restart unless-stopped` in the
  recipe and compose file.
- FastMCP specifics pinned and verified against 3.4.4 (transport name `http`, `host`/`port`
  kwargs, `/mcp` path, `custom_route` availability); the dependency constraint `fastmcp>=3.2.0,<4`
  already bounds the API surface.
