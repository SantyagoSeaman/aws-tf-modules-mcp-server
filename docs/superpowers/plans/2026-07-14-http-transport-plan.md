# HTTP Transport (Streamable HTTP) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in Streamable HTTP transport (`--transport http`) to the MCP server, keeping stdio as the untouched default, with one Docker image serving both modes and a documented shared-daemon recipe.

**Architecture:** Only the final `app.run(...)` call in `main()` branches on transport; all initialization stays transport-agnostic. Concurrency hardening (encode lock, atomic cache writes) makes the shared instance safe. Packaging is unchanged except `EXPOSE` + a compose file; the plugin stays stdio-only.

**Tech Stack:** Python 3.12+, FastMCP 3.4.4 (`app.run(transport="http", host, port)`, path `/mcp`, `custom_route`), starlette (transitive dep), `mcp` SDK `streamablehttp_client` for e2e.

**Spec:** `docs/superpowers/specs/2026-07-14-http-transport-design.md`

## Global Constraints

- Default behavior with no flags MUST be byte-identical to today (stdio); the existing test suite passes unmodified.
- Transport flavor: Streamable HTTP only — never `transport="sse"`.
- Defaults: `--transport stdio`, `--host 127.0.0.1`, `--port 8765`. Env fallbacks `TFMODSEARCH_TRANSPORT`/`TFMODSEARCH_HOST`/`TFMODSEARCH_PORT`; precedence CLI > env > default.
- No auth/TLS; never default to `0.0.0.0`; WARNING on non-loopback bind.
- One Dockerfile, one image, one tag. No plugin behavior changes (version bumps only).
- No index rebuild, no changes to search behavior or tool signatures.
- Release: 0.16.0. Version bump touches pyproject.toml + 2 plugin manifests + `DEFAULT_IMAGE` in `plugins/tfmod-search/bin/tfmodsearch_launch.py`.
- Commit style: plain content-only messages, no attribution trailers, no apostrophes/contractions in messages. Push/PR only after explicit user approval.

---

### Task 1: Transport CLI args + env fallbacks

**Files:**
- Modify: `src/tfmod_mcp_server.py` (`parse_arguments`, ~line 1688)
- Test: `tests/integration/test_transport_args.py` (create)

**Interfaces:**
- Produces: `parse_arguments(argv: list[str] | None = None)` returning namespace with `.transport` (`"stdio"|"http"`), `.host` (str), `.port` (int). Helper `_env_default(name: str, fallback: str) -> str`.

- [ ] **Step 1: Write the failing tests**

```python
"""Transport argument parsing: defaults, env fallbacks, CLI precedence."""

import pytest

from tfmod_mcp_server import parse_arguments


def test_default_transport_is_stdio(monkeypatch):
    for var in ("TFMODSEARCH_TRANSPORT", "TFMODSEARCH_HOST", "TFMODSEARCH_PORT"):
        monkeypatch.delenv(var, raising=False)
    args = parse_arguments([])
    assert args.transport == "stdio"
    assert args.host == "127.0.0.1"
    assert args.port == 8765


def test_cli_selects_http():
    args = parse_arguments(["--transport", "http", "--host", "0.0.0.0", "--port", "9000"])
    assert args.transport == "http"
    assert args.host == "0.0.0.0"
    assert args.port == 9000


def test_env_fallbacks(monkeypatch):
    monkeypatch.setenv("TFMODSEARCH_TRANSPORT", "http")
    monkeypatch.setenv("TFMODSEARCH_HOST", "0.0.0.0")
    monkeypatch.setenv("TFMODSEARCH_PORT", "9001")
    args = parse_arguments([])
    assert args.transport == "http"
    assert args.host == "0.0.0.0"
    assert args.port == 9001


def test_cli_overrides_env(monkeypatch):
    monkeypatch.setenv("TFMODSEARCH_TRANSPORT", "http")
    monkeypatch.setenv("TFMODSEARCH_PORT", "9001")
    args = parse_arguments(["--transport", "stdio", "--port", "8123"])
    assert args.transport == "stdio"
    assert args.port == 8123


def test_invalid_env_transport_rejected(monkeypatch):
    monkeypatch.setenv("TFMODSEARCH_TRANSPORT", "carrier-pigeon")
    with pytest.raises(SystemExit):
        parse_arguments([])


def test_invalid_cli_transport_rejected():
    with pytest.raises(SystemExit):
        parse_arguments(["--transport", "sse"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/integration/test_transport_args.py -v`
Expected: FAIL — `parse_arguments() takes 0 positional arguments` / missing attributes.

- [ ] **Step 3: Implement**

In `src/tfmod_mcp_server.py`, add near the other module-level helpers:

```python
def _env_default(name: str, fallback: str) -> str:
    """Environment fallback for a CLI default (empty/unset -> fallback)."""
    value = os.environ.get(name, "").strip()
    return value if value else fallback
```

(`import os` is already present.) Change the signature `def parse_arguments() -> argparse.Namespace:` to `def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:` and the final line to use `argv`. Add arguments after `--warmup`:

```python
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "http"],
        default=_env_default("TFMODSEARCH_TRANSPORT", "stdio"),
        help="MCP transport: stdio (default, one process per client) or http "
        "(streamable HTTP shared instance at /mcp). Env fallback: TFMODSEARCH_TRANSPORT",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=_env_default("TFMODSEARCH_HOST", "127.0.0.1"),
        help="Bind address for --transport http. Env fallback: TFMODSEARCH_HOST",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=_env_default("TFMODSEARCH_PORT", "8765"),
        help="Bind port for --transport http. Env fallback: TFMODSEARCH_PORT",
    )

    args = parser.parse_args(argv)
    # argparse does not validate string defaults against choices, so a bad
    # TFMODSEARCH_TRANSPORT value would otherwise slip through silently.
    if args.transport not in ("stdio", "http"):
        parser.error(f"invalid transport {args.transport!r} (check TFMODSEARCH_TRANSPORT): choose stdio or http")
    return args
```

(Replace the existing `return parser.parse_args()`.) Note: argparse applies `type=int` to the string default, so a garbage `TFMODSEARCH_PORT` fails with a clean argparse error.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/integration/test_transport_args.py -v`
Expected: 6 PASS.

- [ ] **Step 5: Regression check + commit**

Run: `.venv/bin/pytest tests/integration/test_mcp_server.py -q`
Expected: all pass.

```bash
git add src/tfmod_mcp_server.py tests/integration/test_transport_args.py
git commit -m "Add --transport/--host/--port args with env fallbacks (stdio default)"
```

---

### Task 2: Thread-safe model load and query encode

**Files:**
- Modify: `src/tfmod_search_lib.py` (`_get_sentence_transformer` ~line 97, query encode ~line 1006)
- Test: `tests/integration/test_encode_lock.py` (create)

**Interfaces:**
- Produces: module-level `_MODEL_LOCK: threading.Lock` in `tfmod_search_lib`; `_get_sentence_transformer` loads each model exactly once under concurrency; the query `encode()` call in `hybrid_search` is serialized by the same lock.

- [ ] **Step 1: Write the failing test**

```python
"""Concurrent model loading must construct the model exactly once."""

import threading

import tfmod_search_lib


class _SlowFakeModel:
    constructions = 0
    construction_lock = threading.Lock()

    def __init__(self, name, device=None):
        with _SlowFakeModel.construction_lock:
            _SlowFakeModel.constructions += 1
        # widen the race window: yield to other threads mid-construction
        import time

        time.sleep(0.05)

    def encode(self, *a, **kw):
        raise NotImplementedError


def test_concurrent_get_model_loads_once(monkeypatch):
    monkeypatch.setattr(tfmod_search_lib, "SentenceTransformer", _SlowFakeModel)
    monkeypatch.setattr(tfmod_search_lib, "_MODEL_CACHE", {})
    _SlowFakeModel.constructions = 0

    threads = [
        threading.Thread(target=tfmod_search_lib._get_sentence_transformer, args=("fake-model", None))
        for _ in range(8)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert _SlowFakeModel.constructions == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/integration/test_encode_lock.py -v`
Expected: FAIL — `constructions == 8` (or flaky >1) because the check-then-set has no lock.

- [ ] **Step 3: Implement**

In `src/tfmod_search_lib.py`: add `import threading` to the imports; next to `_MODEL_CACHE` add:

```python
# Serializes model construction AND SentenceTransformer.encode(), neither of
# which is guaranteed thread-safe. Only matters for the HTTP transport, where
# tool calls run concurrently; stdio never contends. Query encode is ~10 ms,
# so contention is negligible.
_MODEL_LOCK = threading.Lock()
```

Wrap the body of `_get_sentence_transformer`'s cache check-and-load:

```python
    with _MODEL_LOCK:
        if model_name not in _MODEL_CACHE:
            ...existing load code...
        return _MODEL_CACHE[model_name]
```

In `hybrid_search`, wrap the query embedding call (keep everything else outside the lock):

```python
    with _MODEL_LOCK:
        q_vec = model.encode(
            [q],
            prompt=query_instruction,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0].astype(np.float32, copy=False)
```

Do NOT touch the index-build `encode` (~line 800) — the CLI indexer is single-threaded.

- [ ] **Step 4: Run tests**

Run: `.venv/bin/pytest tests/integration/test_encode_lock.py tests/integration/test_cli_index.py -v`
Expected: PASS (lock test + no indexer regression).

- [ ] **Step 5: Commit**

```bash
git add src/tfmod_search_lib.py tests/integration/test_encode_lock.py
git commit -m "Serialize model load and query encode with a lock for concurrent HTTP use"
```

---

### Task 3: Atomic registry doc-cache writes

**Files:**
- Modify: `src/tfmod_registry_docs.py` (`_write_cache_entry`, ~line 182)
- Test: extend `tests/integration/test_registry_docs.py`

**Interfaces:**
- Produces: `_write_cache_entry(path, entry)` writes via temp file + `os.replace` (atomic on POSIX); no `.tmp-*` residue after success.

- [ ] **Step 1: Write the failing test** (append to `tests/integration/test_registry_docs.py`, reusing its existing fixtures/imports style)

```python
def test_write_cache_entry_is_atomic_and_leaves_no_tmp(tmp_path):
    from tfmod_registry_docs import _write_cache_entry

    target = tmp_path / "ns--name--prov--1.0.0.json"
    _write_cache_entry(target, {"document": "x", "fetched_at": 0})

    assert target.exists()
    assert json.loads(target.read_text())["document"] == "x"
    leftovers = [p for p in tmp_path.iterdir() if p.name != target.name]
    assert leftovers == [], f"temp files left behind: {leftovers}"
```

- [ ] **Step 2: Run test**

Run: `.venv/bin/pytest tests/integration/test_registry_docs.py -v -k atomic`
Expected: PASS trivially for residue but the point is pinning behavior — if it already passes, continue (the implementation change below is still required; the test guards it).

- [ ] **Step 3: Implement**

In `src/tfmod_registry_docs.py` (add `import os` and `import threading` if absent):

```python
def _write_cache_entry(path: Path, entry: dict[str, Any]) -> None:
    """Atomically write a cache entry (temp file + rename).

    Concurrent HTTP tool calls may write the same entry simultaneously;
    os.replace guarantees readers never observe a partially written file.
    Worst case under a race is a duplicate fetch, never corruption.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}-{threading.get_ident()}")
    tmp.write_text(json.dumps(entry))
    os.replace(tmp, path)
```

- [ ] **Step 4: Run the registry/grep suites**

Run: `.venv/bin/pytest tests/integration/test_registry_docs.py tests/integration/test_grep_module_docs.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tfmod_registry_docs.py tests/integration/test_registry_docs.py
git commit -m "Write registry doc cache entries atomically via temp file and os.replace"
```

---

### Task 4: main() HTTP branch, warm-once, non-loopback warning, /health

**Files:**
- Modify: `src/tfmod_mcp_server.py` (imports; new `_is_loopback` helper; `/health` route near `app = FastMCP(...)`; `main()` final branch ~line 1887)
- Test: `tests/integration/test_transport_args.py` (extend with `_is_loopback` tests)

**Interfaces:**
- Consumes: `args.transport/.host/.port` (Task 1); `search_modules_impl(query, state)` (existing warmup path); `ServerStateManager.get()` (raises `RuntimeError` when uninitialized); `_SERVER_VERSION`.
- Produces: `_is_loopback(host: str) -> bool`; GET `/health` → 200 `{"status": "ok", "version": ..., "modules": N}` (503 `{"status": "initializing"}` before init); server serves Streamable HTTP at `http://host:port/mcp`.

- [ ] **Step 1: Write the failing tests** (append to `tests/integration/test_transport_args.py`)

```python
from tfmod_mcp_server import _is_loopback


def test_is_loopback_true_cases():
    assert _is_loopback("127.0.0.1")
    assert _is_loopback("::1")
    assert _is_loopback("localhost")
    assert _is_loopback("LOCALHOST")


def test_is_loopback_false_cases():
    assert not _is_loopback("0.0.0.0")
    assert not _is_loopback("192.168.1.10")
    assert not _is_loopback("example.com")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/integration/test_transport_args.py -v -k loopback`
Expected: FAIL — no `_is_loopback`.

- [ ] **Step 3: Implement**

In `src/tfmod_mcp_server.py`:

Imports: add `import ipaddress` (top-level with the other stdlib imports) and

```python
from starlette.requests import Request
from starlette.responses import JSONResponse
```

Helper (near `_env_default`):

```python
def _is_loopback(host: str) -> bool:
    """True when host is a loopback address or the literal localhost."""
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host.lower() == "localhost"
```

Health route (module level, after the `app = FastMCP(...)` block — custom routes are only served by the HTTP app, stdio is unaffected):

```python
@app.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    """Liveness/readiness probe for the HTTP transport (no MCP handshake needed)."""
    try:
        state = ServerStateManager.get()
    except RuntimeError:
        return JSONResponse({"status": "initializing"}, status_code=503)
    return JSONResponse({"status": "ok", "version": _SERVER_VERSION, "modules": len(state.index.docs)})
```

(Confirm `ServerStateManager.get()` raises `RuntimeError` when uninitialized — if it returns None instead, adapt to `state is None`.)

`main()` — replace the two lines

```python
        logger.info("Starting MCP server (stdio transport)")
        app.run(transport="stdio")
```

with:

```python
        if args.transport == "http":
            if not _is_loopback(args.host):
                logger.warning(
                    f"Binding non-loopback host {args.host} with NO authentication - anyone who can "
                    "reach this address can query the server. Intended only inside a container whose "
                    "host port mapping restricts exposure (e.g. -p 127.0.0.1:8765:8765)."
                )
            # Warm once, BEFORE serving: the whole point of the shared instance is a
            # single deterministic model load; stdio keeps its lazy load untouched.
            logger.info("HTTP mode: warming up embedding model before serving")
            warm = search_modules_impl("vpc networking", state)
            logger.info(f"Warmup complete: test query returned {len(warm.results)} results")
            logger.info(f"READY on http://{args.host}:{args.port}/mcp")
            app.run(transport="http", host=args.host, port=args.port)
        else:
            logger.info("Starting MCP server (stdio transport)")
            app.run(transport="stdio")
```

- [ ] **Step 4: Run tests + quick manual smoke**

Run: `.venv/bin/pytest tests/integration/test_transport_args.py tests/integration/test_mcp_server.py -q`
Expected: all PASS.

Manual smoke (backgrounded, ~15 s for model load):

```bash
.venv/bin/python src/tfmod_mcp_server.py --transport http --port 8891 &
sleep 20 && curl -s http://127.0.0.1:8891/health && kill %1
```

Expected: `{"status":"ok","version":"...","modules":55}`.

- [ ] **Step 5: Commit**

```bash
git add src/tfmod_mcp_server.py tests/integration/test_transport_args.py
git commit -m "Add streamable HTTP transport branch with warm-once startup and /health"
```

---

### Task 5: E2E tests over real HTTP transport

**Files:**
- Create: `tests/e2e/test_mcp_http_e2e.py`

**Interfaces:**
- Consumes: server CLI from Tasks 1+4; `mcp.client.streamable_http.streamablehttp_client`; `/health`.

- [ ] **Step 1: Write the e2e suite**

```python
"""
End-to-end tests for the MCP server over real streamable HTTP transport.

Spawns the actual server process with --transport http on an ephemeral port,
waits for /health readiness, then speaks MCP through the official SDK client:
handshake, tool discovery, tool calls, and an 8-way concurrency burst.
"""

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

PROJECT_ROOT = Path(__file__).parent.parent.parent
SERVER_SCRIPT = PROJECT_ROOT / "src" / "tfmod_mcp_server.py"
EXPECTED_TOOLS = {"modules_list", "search_modules", "get_module", "grep_module_docs"}
READY_TIMEOUT = 120  # first start loads the embedding model


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_healthy(port: int, proc: subprocess.Popen) -> dict:
    deadline = time.time() + READY_TIMEOUT
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early with code {proc.returncode}")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as resp:
                if resp.status == 200:
                    return json.loads(resp.read())
        except OSError:
            pass
        time.sleep(0.5)
    raise TimeoutError("server did not become healthy in time")


@pytest.fixture(scope="module")
def http_server():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT), "--transport", "http", "--port", str(port)],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        health = _wait_healthy(port, proc)
        yield port, health
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def _result_text(result) -> str:
    assert result.content, "tool result has no content"
    return result.content[0].text


@pytest.mark.e2e
@pytest.mark.timeout(180)
def test_health_reports_version_and_modules(http_server):
    _, health = http_server
    assert health["status"] == "ok"
    assert health["version"]
    assert health["modules"] > 50


@pytest.mark.e2e
@pytest.mark.timeout(180)
@pytest.mark.asyncio
async def test_full_http_protocol_session(http_server):
    port, _ = http_server
    async with streamablehttp_client(f"http://127.0.0.1:{port}/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            assert init.serverInfo.name == "tfmod-search"

            tools = await session.list_tools()
            assert {t.name for t in tools.tools} == EXPECTED_TOOLS

            result = await session.call_tool("search_modules", {"query": "vpc networking"})
            payload = json.loads(_result_text(result))
            assert payload["results"][0]["module_name"] == "vpc"

            result = await session.call_tool("get_module", {"module_identifier": "vpc"})
            assert "## Module Information" in _result_text(result)


@pytest.mark.e2e
@pytest.mark.timeout(180)
@pytest.mark.asyncio
async def test_concurrent_tool_calls(http_server):
    port, _ = http_server
    queries = ["vpc", "s3 bucket", "kubernetes cluster", "lambda", "rds database", "iam role", "cloudfront cdn", "sqs queue"]

    async def one_call(query: str) -> dict:
        async with streamablehttp_client(f"http://127.0.0.1:{port}/mcp") as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("search_modules", {"query": query})
                return json.loads(_result_text(result))

    payloads = await asyncio.gather(*(one_call(q) for q in queries))
    assert len(payloads) == 8
    for payload in payloads:
        assert payload["results"], "concurrent call returned empty results"
        for r in payload["results"]:
            assert set(r) >= {"module_name", "path", "score"}


@pytest.mark.e2e
@pytest.mark.timeout(240)
def test_env_fallback_serves_http():
    port = _free_port()
    env = {**os.environ, "TFMODSEARCH_TRANSPORT": "http", "TFMODSEARCH_PORT": str(port)}
    proc = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT)],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        health = _wait_healthy(port, proc)
        assert health["status"] == "ok"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
```

(Default-invocation-is-stdio is already guarded by the whole existing `test_mcp_stdio_e2e.py` suite, which spawns the server with no transport flag.)

- [ ] **Step 2: Run the new e2e suite**

Run: `.venv/bin/pytest tests/e2e/test_mcp_http_e2e.py -v`
Expected: 4 PASS (module-scoped server spawns once; env-fallback test spawns its own). If `streamablehttp_client` yields a different tuple arity in the installed SDK, adapt the unpacking (check `mcp.client.streamable_http` signature).

- [ ] **Step 3: Run the stdio e2e suite for regression**

Run: `.venv/bin/pytest tests/e2e/test_mcp_stdio_e2e.py -v`
Expected: all PASS unchanged.

- [ ] **Step 4: Commit**

```bash
git add tests/e2e/test_mcp_http_e2e.py
git commit -m "Add e2e tests for streamable HTTP transport including concurrency burst"
```

---

### Task 6: Dockerfile EXPOSE + docker-compose.yml

**Files:**
- Modify: `Dockerfile` (runtime stage, before `ENTRYPOINT`)
- Create: `docker-compose.yml` (repo root)

**Interfaces:**
- Produces: `docker-compose.yml` service `tfmodsearch-http` encoding the documented daemon recipe.

- [ ] **Step 1: Dockerfile**

Add before `ENTRYPOINT ["tfmodsearch"]`:

```dockerfile
# HTTP mode only (docs): `docker run -d -p 127.0.0.1:8765:8765 <image> --transport http --host 0.0.0.0`.
# stdio mode ignores this. EXPOSE is documentation, not a port publication.
EXPOSE 8765
```

Also update the header comment block (lines 1-12) to mention the second mode: same image serves `--transport http` as a shared daemon; stdio remains the default.

- [ ] **Step 2: docker-compose.yml**

```yaml
# Shared HTTP daemon for the TFModSearch MCP server.
#
#   docker compose up -d
#   claude mcp add --transport http --scope user tfmod-search http://127.0.0.1:8765/mcp
#
# One long-lived instance, one embedding-model load, shared by every MCP
# client/session on this machine. Loopback-only by design: the server has no
# auth, so the host port mapping is the security boundary. Inside the
# container the server must bind 0.0.0.0 or the published port is unreachable.
services:
  tfmodsearch-http:
    image: ghcr.io/santyagoseaman/tfmodsearch:0.16.0
    container_name: tfmodsearch-http
    restart: unless-stopped
    ports:
      - "127.0.0.1:8765:8765"
    command: ["--transport", "http", "--host", "0.0.0.0", "--port", "8765"]
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8765/health', timeout=5).status == 200 else 1)"]
      interval: 30s
      timeout: 10s
      start_period: 90s
      retries: 3
```

- [ ] **Step 3: Validate compose file**

Run: `docker compose config -q && echo OK`
Expected: `OK` (no schema errors).

- [ ] **Step 4: Commit**

```bash
git add Dockerfile docker-compose.yml
git commit -m "Add EXPOSE 8765 and docker-compose recipe for the shared HTTP daemon"
```

---

### Task 7: Documentation

**Files:**
- Modify: `README.md` (new "Shared HTTP instance" section, after the Docker section)
- Modify: `docs/docker-container-support.md` (new HTTP-mode section)
- Modify: `CLAUDE.md` (MCP server component description + transport paragraph)
- Modify: `CHANGELOG.md` (0.16.0 entry, top)

**Interfaces:** none (prose).

- [ ] **Step 1: README section** — cover, in this order: motivation (N sessions/subagents share ONE model load vs stdio's process-per-client); quickstart:

```bash
# 1. start the daemon (Docker)
docker run -d --name tfmodsearch-http --restart unless-stopped \
  -p 127.0.0.1:8765:8765 \
  ghcr.io/santyagoseaman/tfmodsearch:0.16.0 \
  --transport http --host 0.0.0.0 --port 8765
# ...or without Docker:
tfmodsearch --transport http

# 2. point Claude Code at it
claude mcp add --transport http --scope user tfmod-search http://127.0.0.1:8765/mcp
```

plus: readiness via `curl http://127.0.0.1:8765/health`; env-var table (`TFMODSEARCH_TRANSPORT/HOST/PORT`); lifecycle ownership (operator owns the daemon, no auto-spawn); do-not-run-both note (disable the plugin stdio entry when using the HTTP entry, duplicate toolsets confuse agents); security note (no auth — keep it loopback; never expose without a reverse proxy).

- [ ] **Step 2: docs/docker-container-support.md** — add an "HTTP mode (shared daemon)" section: same recipe, `docker-compose.yml` pointer, and the 0.0.0.0-inside/loopback-mapping-outside explanation (why the in-container bind warning is expected there).

- [ ] **Step 3: CLAUDE.md** — in the MCP Server component bullet list, document: `--transport {stdio,http}` (+ `--host/--port`, env fallbacks, default stdio), warm-once HTTP startup, `/health`, and the one-image-two-modes Docker story.

- [ ] **Step 4: CHANGELOG.md** — 0.16.0 entry: Added (streamable HTTP transport, env fallbacks, /health, compose file, EXPOSE), Fixed/Hardened (encode lock, atomic cache writes), Unchanged (stdio default, plugin, index).

- [ ] **Step 5: Commit**

```bash
git add README.md docs/docker-container-support.md CLAUDE.md CHANGELOG.md
git commit -m "Document shared HTTP instance mode across README, docker doc, CLAUDE.md, changelog"
```

---

### Task 8: Version bump 0.16.0 + full verification

**Files:**
- Modify: `pyproject.toml` (`version = "0.16.0"`)
- Modify: `plugins/tfmod-search/.claude-plugin/plugin.json` (`"version": "0.16.0"`)
- Modify: `.agents/plugins/marketplace.json` or the Codex manifest carrying a version (locate with `grep -rn "0\.15\.1" plugins/ .claude-plugin/ .agents/`)
- Modify: `plugins/tfmod-search/bin/tfmodsearch_launch.py` (`DEFAULT_IMAGE = ".../tfmodsearch:0.16.0"`)

**Interfaces:** none.

- [ ] **Step 1: Bump versions**

Run `grep -rn "0\.15\.1" pyproject.toml plugins/ .claude-plugin/ .agents/ docker-compose.yml` and update every version occurrence to `0.16.0` (pyproject, both plugin manifests, `DEFAULT_IMAGE`). Check e2e tests for hardcoded image tags (`grep -rn "0\.15" tests/`) and update if any.

- [ ] **Step 2: Full test suite**

Run: `.venv/bin/pytest tests/ -q`
Expected: everything passes (~360+ tests; 6 opt-in live tests skip without `RUN_REGISTRY_BENCHMARK=1`). Investigate ANY failure — do not proceed with red tests. Known local flake: `TestClaudeCliLive` can fail if the stale `/usr/local/bin/claude` shadows `~/.local/bin/claude` (pre-existing, not this change).

- [ ] **Step 3: Lint/type gates**

Run: `.venv/bin/ruff check src/ tests/ && .venv/bin/ruff format --check src/ tests/ && .venv/bin/mypy src/`
Expected: clean (match pre-commit).

- [ ] **Step 4: Docker verification (manual, pre-release)**

```bash
docker build -t tfmodsearch:0.16.0-rc .
# stdio smoke (unchanged behavior):
docker run --network none -i --rm tfmodsearch:0.16.0-rc --warmup
# HTTP daemon:
docker run -d --name tfm-http-rc -p 127.0.0.1:8765:8765 tfmodsearch:0.16.0-rc --transport http --host 0.0.0.0 --port 8765
sleep 60 && curl -s http://127.0.0.1:8765/health
# real tool call through the SDK against the container:
.venv/bin/python - <<'PY'
import asyncio, json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("http://127.0.0.1:8765/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool("search_modules", {"query": "vpc"})
            print(json.loads(res.content[0].text)["results"][0]["module_name"])

asyncio.run(main())
PY
docker rm -f tfm-http-rc
```

Expected: warmup OK offline; health `{"status":"ok",...}`; tool call prints `vpc`.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml plugins/ docker-compose.yml
git commit -m "Bump version to 0.16.0"
```

---

### Task 9: Independent review + release prep (repo convention)

- [ ] Spawn an independent Opus subagent to review the full branch diff (`git diff master...HEAD`) against the spec; fix real findings.
- [ ] Present results to the user; push branch + open PR **only after explicit user approval** (master is branch-protected, PR-only; Copilot auto-review threads must be resolved before merge; release = merge → tag `v0.16.0` → CI publishes to PyPI + GHCR).
