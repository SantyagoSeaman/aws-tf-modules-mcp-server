# 0.18.0 Proxy Mode + Image Slimming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Post-execution corrections** (this plan is a historical execution artifact; the code and
> the spec addendum are authoritative where they differ): (1) the proxy uses fastmcp
> `create_proxy`, not the deprecated `FastMCP.as_proxy` shown in Task 1; (2) proxy mode is
> dispatched through the import-light `tfmod_entry` -> `tfmod_proxy` path (blind-review MAJOR-1
> fix), so the Task 1 snippet that sets up startup.log logging inside tfmod_mcp_server main()
> is superseded; (3) Task 4 step 1 as written removes `torch/bin` — do NOT: torch resolves
> `torch/bin/torch_shm_manager` unconditionally at import time, only `torch/test` and
> `torch/include` are removable (see the Dockerfile comment and the spec addendum).

**Goal:** Let plugin users target the shared HTTP daemon without losing the plugin's skills (stdio→HTTP proxy mode), and cut ~350 MB of dead weight from the Docker image.

**Architecture:** A `--proxy-url` flag on the server runs `FastMCP.as_proxy(url)` before any index/model loading; the plugin launcher gains a `TFMODSEARCH_URL` env var with a `/health` preflight and graceful fallback to the existing uvx/Docker selection. The Dockerfile drops the torch wheel's test/include/bin dirs in the builder stage and replaces the layer-duplicating `chown -R` with `COPY --chown`.

**Tech Stack:** Python 3.13 dev venv, FastMCP 3.4.4 (`FastMCP.as_proxy` — already a dependency), stdlib-only launcher, pytest, Docker.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-14-proxy-and-image-slim-design.md`.
- The launcher (`plugins/tfmod-search/bin/tfmodsearch_launch.py`) must stay **stdlib-only**.
- No new package dependencies anywhere.
- stdio default path (no new env vars set) must remain behaviorally identical to 0.17.0.
- Commit messages: plain content-only, NO apostrophes/contractions (heredoc gotcha), no attribution trailers.
- Run commands from the repo root with the venv active: `source .venv/bin/activate`.
- Falsy env values everywhere: `{"", "0", "false", "no", "off"}` (case-insensitive, stripped).

---

### Task 1: Server `--proxy-url` flag, validation, and proxy branch

**Files:**
- Modify: `src/tfmod_mcp_server.py` (`parse_arguments` ~line 1845, `main()` ~line 2027)
- Test: `tests/integration/test_transport_args.py`

**Interfaces:**
- Produces: `parse_arguments` returns namespace with `proxy_url: str | None`; proxy mode forces `args.transport == "stdio"`. Task 3 spawns `python src/tfmod_mcp_server.py --proxy-url <url>` and expects a working stdio MCP server that loads no index and no model.

- [ ] **Step 1: Write the failing tests**

Append to `tests/integration/test_transport_args.py`:

```python
def test_proxy_url_default_is_none():
    args = parse_arguments([])
    assert args.proxy_url is None


def test_proxy_url_accepted_and_forces_stdio():
    args = parse_arguments(["--proxy-url", "http://127.0.0.1:8765/mcp"])
    assert args.proxy_url == "http://127.0.0.1:8765/mcp"
    assert args.transport == "stdio"


def test_proxy_url_overrides_env_transport(monkeypatch):
    # A globally exported TFMODSEARCH_TRANSPORT=http must not break proxy mode:
    # the env fallback is ignored, only an EXPLICIT --transport http conflicts.
    monkeypatch.setenv("TFMODSEARCH_TRANSPORT", "http")
    args = parse_arguments(["--proxy-url", "http://127.0.0.1:8765/mcp"])
    assert args.transport == "stdio"


def test_proxy_url_conflicts_with_explicit_http_transport():
    with pytest.raises(SystemExit):
        parse_arguments(["--proxy-url", "http://127.0.0.1:8765/mcp", "--transport", "http"])


def test_proxy_url_conflicts_with_warmup():
    with pytest.raises(SystemExit):
        parse_arguments(["--proxy-url", "http://127.0.0.1:8765/mcp", "--warmup"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integration/test_transport_args.py -v -k proxy`
Expected: 5 FAIL (`unrecognized arguments: --proxy-url`).

- [ ] **Step 3: Implement flag + validation**

In `parse_arguments` in `src/tfmod_mcp_server.py`, add after the `--port` argument:

```python
    parser.add_argument(
        "--proxy-url",
        dest="proxy_url",
        type=str,
        default=None,
        help="Run as a stdio proxy forwarding to a remote streamable HTTP MCP server "
        "(e.g. http://127.0.0.1:8765/mcp). Implies stdio; loads no index and no "
        "embedding model. Index/weight flags are accepted but ignored in this mode.",
    )
```

Replace the post-parse validation block (currently just the transport-choices check) with:

```python
    args = parser.parse_args(argv)
    # argparse does not validate string defaults against choices, so a bad
    # TFMODSEARCH_TRANSPORT value would otherwise slip through silently.
    if args.transport not in ("stdio", "http"):
        parser.error(f"invalid transport {args.transport!r} (check TFMODSEARCH_TRANSPORT): choose stdio or http")
    if args.proxy_url:
        # Only an explicit CLI --transport http is a real conflict; an env-derived
        # http fallback (TFMODSEARCH_TRANSPORT exported globally) is silently
        # overridden because the proxy is by definition a stdio-side helper.
        cli_argv = sys.argv[1:] if argv is None else argv
        transport_given_explicitly = any(a == "--transport" or a.startswith("--transport=") for a in cli_argv)
        if transport_given_explicitly and args.transport == "http":
            parser.error("--proxy-url runs a stdio-side proxy and cannot be combined with --transport http")
        if args.warmup:
            parser.error("--proxy-url loads no model, so there is nothing to warm up; drop --warmup")
        args.transport = "stdio"
    return args
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/integration/test_transport_args.py -v`
Expected: all PASS (8 pre-existing + 5 new).

- [ ] **Step 5: Add the proxy branch to `main()`**

`main()` currently starts with `initialize_nltk()` then `parse_arguments()`. Reorder so parsing comes first and the proxy branch exits before NLTK/config/index/model ever load. Replace the top of the `try:` block:

```python
    try:
        # Parse command-line arguments first (needed for config path, and so
        # proxy mode can exit before any index/model/NLTK initialization).
        args = parse_arguments()

        if args.proxy_url:
            # Lightweight stdio->HTTP forwarder: no NLTK, no config, no index,
            # no embedding model. The daemon at proxy_url owns all of that.
            logger = setup_logging("startup.log", log_level=args.log_level)
            logger.info("=" * 80)
            logger.info(f"Proxy mode: forwarding stdio to {args.proxy_url}")
            proxy = FastMCP.as_proxy(args.proxy_url)
            proxy.run(transport="stdio")
            return

        # Initialize NLTK before any search operations
        initialize_nltk()
```

(The rest of `main()` — config loading, `setup_logging`, `initialize_server`, warmup, transport dispatch — stays exactly as is, minus the old `initialize_nltk()` first line and the duplicate `args = parse_arguments()` line.)

- [ ] **Step 6: Sanity-run the module import and full integration suite**

Run: `python -c "import sys; sys.path.insert(0, 'src'); import tfmod_mcp_server"` then `pytest tests/integration/ -q`
Expected: import clean; suite green (proxy branch itself is exercised e2e in Task 3).

- [ ] **Step 7: Commit**

```bash
git add src/tfmod_mcp_server.py tests/integration/test_transport_args.py
git commit -m "Add --proxy-url flag: stdio proxy to a remote HTTP MCP daemon"
```

---

### Task 2: Launcher `TFMODSEARCH_URL` support with health preflight

**Files:**
- Modify: `plugins/tfmod-search/bin/tfmodsearch_launch.py`
- Test: `tests/e2e/test_docker_launcher.py`

**Interfaces:**
- Consumes: server flag `--proxy-url <url>` from Task 1.
- Produces (module-level, tested directly): `DEFAULT_PROXY_URL = "http://127.0.0.1:8765/mcp"`, `resolve_proxy_url(env: Mapping[str, str]) -> str | None`, `health_url_for(mcp_url: str) -> str`, `daemon_healthy(url: str, timeout: float = 3.0, fetcher=None) -> bool`, and `main(env: Mapping[str, str] | None = None) -> None`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/e2e/test_docker_launcher.py`:

```python
# --- TFMODSEARCH_URL proxy mode (0.18.0) ---


@pytest.mark.e2e
def test_resolve_proxy_url_unset_and_falsy_return_none():
    for env in ({}, {"TFMODSEARCH_URL": ""}, {"TFMODSEARCH_URL": "0"}, {"TFMODSEARCH_URL": "off"}):
        assert launcher.resolve_proxy_url(env) is None


@pytest.mark.e2e
@pytest.mark.parametrize("value", ["1", "true", "True", "yes", "on", " 1 "])
def test_resolve_proxy_url_truthy_shorthand_gives_default(value):
    assert launcher.resolve_proxy_url({"TFMODSEARCH_URL": value}) == launcher.DEFAULT_PROXY_URL


@pytest.mark.e2e
def test_resolve_proxy_url_full_url_passes_through():
    url = "http://127.0.0.1:9000/mcp"
    assert launcher.resolve_proxy_url({"TFMODSEARCH_URL": url}) == url


@pytest.mark.e2e
def test_health_url_for_replaces_path():
    assert launcher.health_url_for("http://127.0.0.1:9000/mcp") == "http://127.0.0.1:9000/health"
    assert launcher.health_url_for(launcher.DEFAULT_PROXY_URL) == "http://127.0.0.1:8765/health"


@pytest.mark.e2e
def test_daemon_healthy_true_on_200_false_otherwise():
    assert launcher.daemon_healthy("http://x/health", fetcher=lambda u, t: 200) is True
    assert launcher.daemon_healthy("http://x/health", fetcher=lambda u, t: 503) is False

    def boom(u, t):
        raise OSError("refused")

    assert launcher.daemon_healthy("http://x/health", fetcher=boom) is False


@pytest.mark.e2e
def test_main_proxy_healthy_execs_proxy(monkeypatch):
    calls = []
    monkeypatch.setattr(launcher.os, "execvp", lambda cmd, argv: calls.append((cmd, argv)))
    monkeypatch.setattr(launcher, "daemon_healthy", lambda url: True)
    monkeypatch.setattr(launcher.sys, "argv", ["tfmodsearch_launch.py"])
    launcher.main(env={"TFMODSEARCH_URL": "1"})
    assert calls == [("uvx", ["uvx", "tfmodsearch", "--proxy-url", launcher.DEFAULT_PROXY_URL])]


@pytest.mark.e2e
def test_main_proxy_precedence_notice_over_docker(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(launcher.os, "execvp", lambda cmd, argv: calls.append((cmd, argv)))
    monkeypatch.setattr(launcher, "daemon_healthy", lambda url: True)
    monkeypatch.setattr(launcher.sys, "argv", ["tfmodsearch_launch.py"])
    launcher.main(env={"TFMODSEARCH_URL": "1", "TFMODSEARCH_DOCKER": "1"})
    assert "TFMODSEARCH_URL takes precedence" in capsys.readouterr().err
    assert calls[0][0] == "uvx"
    assert "--proxy-url" in calls[0][1]


@pytest.mark.e2e
def test_main_proxy_unhealthy_falls_back_to_local(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(launcher.os, "execvp", lambda cmd, argv: calls.append((cmd, argv)))
    monkeypatch.setattr(launcher, "daemon_healthy", lambda url: False)
    monkeypatch.setattr(launcher.sys, "argv", ["tfmodsearch_launch.py"])
    launcher.main(env={"TFMODSEARCH_URL": "http://127.0.0.1:9999/mcp"})
    assert "not responding" in capsys.readouterr().err
    assert calls == [("uvx", ["uvx", "tfmodsearch"])]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/e2e/test_docker_launcher.py -v -k "proxy or resolve or health or daemon"`
Expected: FAIL with `AttributeError: ... has no attribute 'resolve_proxy_url'` etc.

- [ ] **Step 3: Implement in the launcher**

In `plugins/tfmod-search/bin/tfmodsearch_launch.py`:

Update the module docstring to document the third mode. Replace its first paragraph block with:

```python
"""Multi-mode launcher for the tfmod-search MCP server plugin.

Default (env unset): `uvx tfmodsearch` — unchanged local launch path.
Opt-in (`TFMODSEARCH_DOCKER=1`): `docker run -i --rm <image>` — the official,
offline Docker image (tag overridable via `TFMODSEARCH_IMAGE`). If Docker is
requested but not on PATH, falls back to uvx with a warning instead of failing.
Opt-in (`TFMODSEARCH_URL=<url>` or `TFMODSEARCH_URL=1` for the default
http://127.0.0.1:8765/mcp): stdio proxy to a shared HTTP daemon — `uvx
tfmodsearch --proxy-url <url>`. Takes precedence over TFMODSEARCH_DOCKER.
The daemon is health-checked first (3 s); if it is not responding, falls back
to the local uvx/Docker path with a warning so the session keeps working.

`os.execvp` replaces this process so the stdio pipe is inherited transparently
between the MCP client and whichever backend is selected.
"""
```

Add after the `_FALSY` constant:

```python
DEFAULT_PROXY_URL = "http://127.0.0.1:8765/mcp"
_TRUTHY_SHORTHAND = {"1", "true", "yes", "on"}


def resolve_proxy_url(env: Mapping[str, str]) -> str | None:
    """Return the proxy target URL, the default URL for shorthand truthy values, or None."""
    raw = env.get("TFMODSEARCH_URL", "").strip()
    if raw.lower() in _FALSY:
        return None
    if raw.lower() in _TRUTHY_SHORTHAND:
        return DEFAULT_PROXY_URL
    return raw


def health_url_for(mcp_url: str) -> str:
    """Derive the /health URL on the same origin as the MCP endpoint."""
    from urllib.parse import urlsplit, urlunsplit

    parts = urlsplit(mcp_url)
    return urlunsplit((parts.scheme, parts.netloc, "/health", "", ""))


def daemon_healthy(url: str, timeout: float = 3.0, fetcher=None) -> bool:
    """True if GET <url> returns 200 within timeout; False on any error."""
    if fetcher is None:

        def fetcher(u: str, t: float) -> int:
            import urllib.request

            with urllib.request.urlopen(u, timeout=t) as resp:  # noqa: S310 -- loopback daemon health probe
                return resp.status

    try:
        return fetcher(url, timeout) == 200
    except Exception:
        return False
```

Replace `main()` with:

```python
def main(env: Mapping[str, str] | None = None) -> None:
    if env is None:
        env = os.environ
    proxy_url = resolve_proxy_url(env)
    if proxy_url is not None:
        if env.get("TFMODSEARCH_DOCKER", "").strip().lower() not in _FALSY:
            print(
                "tfmodsearch_launch: TFMODSEARCH_URL takes precedence; ignoring TFMODSEARCH_DOCKER.",
                file=sys.stderr,
            )
        if daemon_healthy(health_url_for(proxy_url)):
            os.execvp("uvx", ["uvx", "tfmodsearch", "--proxy-url", proxy_url])  # noqa: S606 -- no shell by design
            return
        print(
            f"tfmodsearch_launch: TFMODSEARCH_URL is set but {proxy_url} is not responding; "
            "falling back to a local server.",
            file=sys.stderr,
        )
    command, argv, docker_unavailable = select_backend(env, sys.argv[1:])
    if docker_unavailable:
        print(
            "tfmodsearch_launch: TFMODSEARCH_DOCKER is set but 'docker' is not on PATH; " "falling back to uvx.",
            file=sys.stderr,
        )
    os.execvp(command, argv)  # noqa: S606 -- no shell by design, argv is not shell-interpreted
```

Note: `select_backend()` is untouched. The existing behavior with no new env vars set is byte-identical.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/e2e/test_docker_launcher.py -v`
Expected: all PASS (existing suite + 8 new).

- [ ] **Step 5: Commit**

```bash
git add plugins/tfmod-search/bin/tfmodsearch_launch.py tests/e2e/test_docker_launcher.py
git commit -m "Launcher: TFMODSEARCH_URL proxy mode with health preflight and fallback"
```

---

### Task 3: Proxy end-to-end tests

**Files:**
- Create: `tests/e2e/test_mcp_proxy_e2e.py`

**Interfaces:**
- Consumes: `--proxy-url` (Task 1); patterns from `tests/e2e/test_mcp_http_e2e.py` (ephemeral port, `/health` readiness poll).

- [ ] **Step 1: Write the e2e tests**

Create `tests/e2e/test_mcp_proxy_e2e.py`:

```python
"""
End-to-end tests for --proxy-url: a stdio proxy forwarding to a real HTTP daemon.

Spawns the HTTP daemon on an ephemeral port, then spawns the proxy as a stdio
subprocess and speaks MCP through it via the official SDK client. The proxy is
launched with a nonexistent index path and an empty offline HF cache, proving
it loads neither the index nor the embedding model.
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
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).parent.parent.parent
SERVER_SCRIPT = PROJECT_ROOT / "src" / "tfmod_mcp_server.py"
EXPECTED_TOOLS = {"modules_list", "search_modules", "get_module", "grep_module_docs"}
READY_TIMEOUT = 120  # first start loads the embedding model


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_healthy(port: int, proc: subprocess.Popen) -> None:
    deadline = time.time() + READY_TIMEOUT
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"daemon exited early with code {proc.returncode}")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as resp:  # noqa: S310 (trusted local host)
                if resp.status == 200:
                    return
        except OSError:
            pass
        time.sleep(0.5)
    raise TimeoutError("daemon did not become healthy in time")


@pytest.fixture(scope="module")
def http_daemon():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT), "--transport", "http", "--port", str(port)],
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "TFMODSEARCH_UPDATE_CHECK": "0"},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_healthy(port, proc)
        yield port
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def _proxy_params(port: int, tmp_path: Path) -> StdioServerParameters:
    # A nonexistent index and an empty offline HF cache make any accidental
    # index/model load in proxy mode fail loudly instead of passing silently.
    empty_hf = tmp_path / "hf-empty"
    empty_hf.mkdir(exist_ok=True)
    return StdioServerParameters(
        command=sys.executable,
        args=[
            str(SERVER_SCRIPT),
            "--proxy-url",
            f"http://127.0.0.1:{port}/mcp",
            "--index_path",
            "/nonexistent/never-loaded.pkl",
        ],
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "HF_HOME": str(empty_hf), "HF_HUB_OFFLINE": "1"},
    )


@pytest.mark.e2e
@pytest.mark.timeout(240)
@pytest.mark.asyncio
async def test_proxy_full_session_without_index_or_model(http_daemon, tmp_path):
    async with stdio_client(_proxy_params(http_daemon, tmp_path)) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            assert {t.name for t in tools.tools} == EXPECTED_TOOLS

            result = await session.call_tool("search_modules", {"query": "s3 bucket", "top_k": 3})
            payload = json.loads(result.content[0].text)
            assert payload["results"], "search through proxy returned no results"
            assert payload["results"][0]["module_name"]
            # Daemon runs with update check disabled -> the field must be absent,
            # and the proxy must pass that absence through untouched.
            assert "update_notice" not in payload

            doc = await session.call_tool("get_module", {"module_identifier": "vpc"})
            assert "## Module Information" in doc.content[0].text


@pytest.mark.e2e
@pytest.mark.timeout(240)
@pytest.mark.asyncio
async def test_proxy_starts_fast(http_daemon, tmp_path):
    # Not a model-load proof (the env guards above are), just a regression
    # tripwire: proxy startup must stay far below model-load territory.
    start = time.monotonic()
    async with stdio_client(_proxy_params(http_daemon, tmp_path)) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
    assert time.monotonic() - start < 20
```

- [ ] **Step 2: Run the new e2e tests**

Run: `pytest tests/e2e/test_mcp_proxy_e2e.py -v`
Expected: 2 PASS (first run waits for the daemon model load, up to ~2 min).

- [ ] **Step 3: Run the full e2e suite to catch interference**

Run: `pytest tests/e2e/ -q`
Expected: green (known local-only flake: `TestClaudeCliLive` if a stale `/usr/local/bin/claude` shadows `~/.local/bin/claude` — pre-existing, not this change).

- [ ] **Step 4: Commit**

```bash
git add tests/e2e/test_mcp_proxy_e2e.py
git commit -m "E2E: proxy session against a live HTTP daemon proves no index or model load"
```

---

### Task 4: Dockerfile Tier 1 slimming

**Files:**
- Modify: `Dockerfile`

**Interfaces:**
- Consumes: nothing from other tasks (independent).
- Produces: image `tfmodsearch:0.18.0-rc` used by the release gate in Task 6.

- [ ] **Step 1: Strip torch dead weight in the builder stage**

In `Dockerfile`, after the `RUN pip install .` line and before the model pre-download, add:

```dockerfile
# The CPU torch wheel ships ~200 MB that inference never touches: its own test
# suite, C++ headers, and build binaries. Verified safe by the release gate
# (offline --warmup + a real search_modules call exercise the full encode path).
RUN rm -rf /usr/local/lib/python3.12/site-packages/torch/test \
           /usr/local/lib/python3.12/site-packages/torch/include \
           /usr/local/lib/python3.12/site-packages/torch/bin
```

- [ ] **Step 2: Replace the duplicating `chown -R` with `COPY --chown`**

Replace the two asset COPY lines in the runtime stage:

```dockerfile
COPY --from=builder --chown=app:app /opt/hf /opt/hf
COPY --from=builder --chown=app:app /opt/nltk_data /opt/nltk_data
```

and shrink the big `RUN mkdir ... chown -R ...` layer to only the two empty writable dirs (keep the existing explanatory comment above it about the path quirks):

```dockerfile
RUN mkdir -p /usr/local/lib/python3.12/site-packages/nltk_data /usr/local/lib/python3.12/logs && \
    chown app:app /usr/local/lib/python3.12/site-packages/nltk_data /usr/local/lib/python3.12/logs
```

Also update the size comment on the pip/setuptools cleanup RUN: torch is still the size floor, but now without test/include/bin.

- [ ] **Step 3: Build the rc image and measure**

```bash
docker build -t tfmodsearch:0.18.0-rc .
docker images tfmodsearch:0.18.0-rc --format '{{.Size}}'
```

Expected: build succeeds; size ≤ 1.4 GB (was 1.69 GB).

- [ ] **Step 4: Verify both modes against the rc image**

```bash
# stdio, fully offline (proves torch still imports and encodes without test/include/bin)
docker run --network none -i --rm tfmodsearch:0.18.0-rc --warmup
# HTTP daemon + a real tool call through the SDK
docker run -d --name slim-rc-test -p 127.0.0.1:18765:8765 tfmodsearch:0.18.0-rc --transport http --host 0.0.0.0
# wait for /health 200, then:
python - <<'PYEOF'
import asyncio, json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def check():
    async with streamablehttp_client("http://127.0.0.1:18765/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool("search_modules", {"query": "s3 bucket encryption"})
            payload = json.loads(res.content[0].text)
            assert payload["results"], "no results from slimmed image"
            print("OK:", payload["results"][0]["module_name"])

asyncio.run(check())
PYEOF
docker rm -f slim-rc-test
```

Expected: warmup prints `Warmup complete: index (55 modules) ...`; SDK call prints `OK: s3-bucket`.

- [ ] **Step 5: Commit**

```bash
git add Dockerfile
git commit -m "Slim Docker image: strip torch test/include/bin and drop duplicating chown layer"
```

---

### Task 5: Docs + version bump to 0.18.0

**Files:**
- Modify: `pyproject.toml`, `plugins/tfmod-search/.claude-plugin/plugin.json`, `plugins/tfmod-search/.codex-plugin/plugin.json`, `plugins/tfmod-search/bin/tfmodsearch_launch.py` (`DEFAULT_IMAGE`), `docker-compose.yml`, `README.md`, `docs/docker-container-support.md`, `CHANGELOG.md`

- [ ] **Step 1: Version bump sweep**

Run `grep -rn "0\.17\.0" pyproject.toml plugins/ README.md docker-compose.yml docs/docker-container-support.md` and bump every **current-release** occurrence to `0.18.0`: `pyproject.toml` version, both plugin.json versions, `DEFAULT_IMAGE` in the launcher, the compose image tag, README quick-install/`TFMODSEARCH_IMAGE`/offline-verify tags. Historical mentions in CHANGELOG/specs stay untouched.

- [ ] **Step 2: README — proxy subsection**

In README's "Shared HTTP instance (opt-in)" section, insert a new subsection **before** the existing "Migrating from the plugin (stdio)" paragraph:

```markdown
**Keeping the plugin (proxy mode, recommended since 0.18.0)**: plugin users do not have to
choose between the skills and the shared daemon anymore. Set one env var and the plugin's
bundled server becomes a lightweight stdio proxy to the daemon — skills, subagents, and the
auto-search workflow all keep working, and the 600 MB model loads only once, in the daemon:

```jsonc
// ~/.claude/settings.json
{ "env": { "TFMODSEARCH_URL": "1" } }               // default daemon on 127.0.0.1:8765
// or a custom target:
{ "env": { "TFMODSEARCH_URL": "http://127.0.0.1:9000/mcp" } }
```

The launcher health-checks the daemon first (3 s): if it is not responding, it falls back to
the normal local server with a stderr warning, so a stopped daemon never breaks the session.
`TFMODSEARCH_URL` takes precedence over `TFMODSEARCH_DOCKER`. Rollback: unset the var.
Any MCP client can use the same mode without the plugin: `tfmodsearch --proxy-url <url>`.
```

Reword the following paragraph's opening to demote it: "**Migrating from the plugin (plugin-less setups)**: if you do not want the plugin at all, make sure only one `tfmod-search` server is registered..." — and delete the "and its skills, which is the trade-off" clause (no longer true as a forced trade-off; proxy mode above is the answer).

- [ ] **Step 3: docker-container-support.md + CHANGELOG**

- `docs/docker-container-support.md`: in the launcher/env-var section (§4.6) document `TFMODSEARCH_URL` (shorthand `1`, full URL, precedence, preflight+fallback); in the HTTP section add one line pointing plugin users at proxy mode.
- `CHANGELOG.md`: new `## [0.18.0]` entry, matching the existing format (link line, one-sentence summary, Added / Changed / Unchanged). Added: `--proxy-url`, `TFMODSEARCH_URL`, image slimming with measured before/after sizes (fill in the real numbers from Task 4 step 3). Unchanged: stdio default byte-identical, no new dependencies, plugin still stdio by default.

- [ ] **Step 4: Run the full test suite**

Run: `pytest tests/ -q`
Expected: green (e2e plugin-manifest tests validate the bumped versions; wheel/packaging tests unaffected).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml plugins/ docker-compose.yml README.md docs/docker-container-support.md CHANGELOG.md
git commit -m "Bump version to 0.18.0; document proxy mode and slimmed image"
```

---

### Task 6: Final gate (run by the orchestrator, not a subagent)

- [ ] Full suite green: `pytest tests/ -q` (opt-in live tests skip without `RUN_REGISTRY_BENCHMARK=1`).
- [ ] Rebuild the rc image from the final tree (`docker build -t tfmodsearch:0.18.0-rc .`) and re-run Task 4 step 4 verification (offline warmup + HTTP SDK call). Record final measured sizes into the CHANGELOG entry if they differ.
- [ ] Live proxy smoke test against the running 0.17.0 daemon on this machine: `TFMODSEARCH_URL=1` through the launcher path.
- [ ] Opus review of the full branch diff against the spec; blind persona review (proxy touches the user-facing plugin launch path).
- [ ] Push, PR, CI, resolve Copilot threads, merge, tag `v0.18.0`, post-release verification per CLAUDE.md Release Process steps 5-7.
