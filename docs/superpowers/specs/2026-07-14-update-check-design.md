# Update Check for the Shared HTTP Daemon — Design

**Date**: 2026-07-14
**Status**: Approved (option 3 from the interactive discussion; Watchtower/auto-update explicitly
rejected as out of scope)
**Target release**: 0.17.0 (minor)

## 1. Problem / Motivation

Distribution channels update on different clocks:

- **Plugin / uvx (stdio)**: `uvx tfmodsearch` resolves a fresh version; docker-stdio gets a new
  pinned tag with every plugin update. Users ride the release train automatically.
- **Shared HTTP daemon (since 0.16.0)**: a long-lived, operator-managed container with a pinned
  image tag. **Nothing ever tells the operator a new version exists.** The daemon runs 0.16.0
  forever while the catalog, tools, and fixes move on.

The gap: a notification channel from the project to the daemon operator. Chosen approach: the
server checks for updates itself and surfaces the result where it will actually be seen —
including *through the agent* that is using the server.

## 2. Non-goals

- **No auto-update.** The server never pulls images or restarts itself; Watchtower-style
  automation is explicitly rejected. The operator stays in control.
- **No telemetry.** The check is a single anonymous GET to the public PyPI JSON API; nothing
  about the customer, host, or usage is sent anywhere.
- **No stdio-mode checks.** stdio processes are short-lived and version-managed by uvx/the
  plugin; a staleness notice there is noise. The feature activates in HTTP mode only.
- No new dependencies; no change to tool signatures (one additive, conditional response field).

## 3. Design

### 3.1 The check (in `tfmod_registry_docs.py` — the only networked module)

New function:

```python
def fetch_latest_pypi_version(package: str = "tfmodsearch", timeout: int = 5) -> str | None
```

- GET `https://pypi.org/pypi/<package>/json`, parse `info.version`. stdlib `urllib`, same scheme
  guard / `S310` pattern as the existing fetcher. Injectable fetcher for tests (same convention
  as `get_assembled_docs`).
- Any failure (network, JSON, status) → return `None`. Never raises.

Version comparison — minimal, self-contained (the project controls its own version format):

```python
def is_newer_version(latest: str, current: str) -> bool
```

`tuple(map(int, v.split(".")))` on both; any parse failure (rc/dev suffixes, unexpected format)
→ `False` (fail closed: no notice on uncertainty). No `packaging` dependency.

### 3.2 The checker loop (in `tfmod_mcp_server.py`)

- A single background `threading.Thread(daemon=True)`, started **only in the HTTP branch of
  `main()`**, after warm-once and before `app.run()`.
- Loop: run the check, store the result, sleep 24h (`UPDATE_CHECK_INTERVAL_HOURS = 24`), repeat.
  First check runs immediately at startup (the daemon just booted — freshest moment to know).
- Result state: a module-level dict `_UPDATE_STATE = {"latest_version": None, "update_available": False}`
  replaced atomically on each check (single assignment, GIL-safe; readers never see a torn value).
  A successful check that finds a newer version logs one WARNING per cycle:
  `Update available: tfmodsearch X.Y.Z (running A.B.C) — bump the image tag and docker compose pull && up -d`.
  Failures log at DEBUG and keep the previous state.

### 3.3 Kill switch

`TFMODSEARCH_UPDATE_CHECK` env var; values `{"", "0", "false", "no", "off"}` (case-insensitive,
same `_FALSY` convention as the plugin launcher) disable the checker thread entirely — required
for air-gapped deployments and used by the offline e2e/test suites. Default: enabled (in HTTP
mode). Env-only — this is a deployment property, not a per-query knob; no CLI flag, no
config.yaml key (YAGNI).

### 3.4 Surfacing — three channels

1. **`/health`** gains two fields (additive, existing fields unchanged):
   ```json
   {"status": "ok", "version": "0.17.0", "modules": 55,
    "latest_version": "0.18.0", "update_available": true}
   ```
   `latest_version` is `null` until the first successful check. Operator scripts/monitoring poll
   this for free (the compose healthcheck is unaffected — it only checks HTTP 200).

2. **Log WARNING** once per 24h cycle while stale (see §3.2) — visible in `docker logs`.

3. **Agent-visible notice**: when `update_available` is true, the JSON-returning tools
   (`search_modules`, `modules_list`, `grep_module_docs`) add one top-level field:
   ```json
   "update_notice": "tfmodsearch 0.18.0 is available (this shared daemon runs 0.17.0). Ask the operator to update: bump the image tag in docker-compose.yml, then docker compose pull && up -d."
   ```
   The field is **absent entirely** when no update is known — zero noise in the common case.
   `get_module` (markdown output) is excluded: its output is a curated document and the
   orientation-head footer is already contract-tested; polluting it is not worth the reach.
   Rationale for the channel: the notice lands exactly on the person actually using the daemon,
   at the moment of use — the agent reads the field and relays it — unlike logs nobody tails.
   Injection is gated on the checker being active (HTTP mode), so stdio output is byte-identical
   to 0.16.0.

## 4. Docs

- README "Shared HTTP instance": short "Update notifications" paragraph — how the daemon learns
  about updates, the three channels, `TFMODSEARCH_UPDATE_CHECK=0` for air-gapped, privacy note
  (one anonymous GET to public PyPI, nothing sent).
- `docs/docker-container-support.md` §9: same note, one paragraph.
- CHANGELOG 0.17.0; CLAUDE.md server-component bullets.

## 5. Acceptance criteria

1. HTTP daemon with a stubbed "newer version" answer: `/health` shows
   `latest_version`/`update_available: true`; `search_modules`/`modules_list`/`grep_module_docs`
   responses carry `update_notice`; `get_module` does not; WARNING logged.
2. Up-to-date (or check-failed) state: no `update_notice` field anywhere, `update_available:
   false`, `latest_version` set (or `null` after failures only).
3. `TFMODSEARCH_UPDATE_CHECK=0`: no checker thread, no PyPI request, fields report
   `latest_version: null` / `update_available: false`.
4. stdio mode: byte-identical output to 0.16.0 (no thread, no fields, no notice) — existing
   suites pass unmodified.
5. The check never blocks or fails a request: tool-call and `/health` latency unaffected by a
   hanging PyPI (checker runs in its own thread with a 5 s timeout).
6. No new runtime dependencies.

## 6. Testing

- **Unit**: `is_newer_version` (newer/equal/older/malformed/rc-suffix → False),
  `fetch_latest_pypi_version` with injected fetcher (success/404/garbage-JSON/timeout → None),
  notice-injection gating (state true/false, tool-by-tool), `_FALSY` kill-switch parsing.
- **Integration**: checker cycle with injected fetcher — state transition, single-WARNING
  behavior, failure keeps previous state.
- **E2E**: the existing HTTP e2e suite runs with `TFMODSEARCH_UPDATE_CHECK=0` so it stays
  offline and deterministic. One new e2e asserts the no-first-result state: daemon up, checker
  enabled but no successful check yet → `/health` shows `latest_version: null`,
  `update_available: false`, and tool responses carry no `update_notice`. A live check against
  real PyPI is opt-in under `RUN_REGISTRY_BENCHMARK=1`.

## 7. Risks / notes

- A hung PyPI response ties up only the checker thread (5 s timeout bounds it); state stays
  stale-but-valid. The thread is `daemon=True` so it never blocks shutdown.
- Version-parse fail-closed means a future non-numeric tag (e.g. `1.0.0rc1` on PyPI) produces no
  notice rather than a wrong one — acceptable: this project publishes plain `X.Y.Z`.
- The notice text names the exact operator action (bump tag, `compose pull && up -d`) — kept in
  one constant so docs and code cannot drift apart.
