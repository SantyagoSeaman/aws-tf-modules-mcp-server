# Update Check for the Shared HTTP Daemon — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The HTTP daemon checks PyPI daily for a newer tfmodsearch release and surfaces it via `/health`, a log WARNING, and an agent-visible `update_notice` field on JSON tool responses.

**Architecture:** A pure fetch+compare pair lives in `tfmod_registry_docs.py` (the only networked module). A background daemon thread in `tfmod_mcp_server.py` (HTTP mode only, env kill-switch) refreshes a module-level state dict; `/health` and the three JSON tool wrappers read it. A pydantic `model_serializer` mixin guarantees the `update_notice` field is entirely absent when `None` (verified: FastMCP otherwise serializes `null`).

**Tech Stack:** stdlib `urllib`/`threading`, pydantic v2 `model_serializer`, FastMCP 3.4.4.

**Spec:** `docs/superpowers/specs/2026-07-14-update-check-design.md`

## Global Constraints

- HTTP mode only: stdio output must stay **byte-identical** to 0.16.0 (no thread, no fields, no notice); existing suites pass unmodified.
- Kill switch `TFMODSEARCH_UPDATE_CHECK` with falsy set `{"", "0", "false", "no", "off"}` (case-insensitive); default enabled in HTTP mode.
- The check never blocks a request: own thread, 5 s timeout, failures are silent (DEBUG log) and keep prior state.
- No new runtime dependencies; no `packaging` — self-contained int-tuple version compare, fail-closed on parse errors.
- `update_notice` must be ABSENT (not `null`) when no update is known; `get_module` output is never touched.
- No telemetry: one anonymous GET to `https://pypi.org/pypi/tfmodsearch/json`.
- Release 0.17.0. Version bump per CLAUDE.md `## Release Process` step 3 (pyproject, both plugin manifests, `DEFAULT_IMAGE`, docker-compose.yml tag, README current-release tags).
- Commit style: plain content-only, no attribution trailers, no apostrophes/contractions. Push/PR only after explicit user approval.

---

### Task 1: Registry client — fetch latest version + compare

**Files:**
- Modify: `src/tfmod_registry_docs.py` (add two functions near `_http_fetch`, ~line 50)
- Test: `tests/integration/test_update_check.py` (create)

**Interfaces:**
- Produces: `fetch_latest_pypi_version(package: str = "tfmodsearch", timeout: int = 5, fetcher: Callable[[str, int], dict] | None = None) -> str | None` and `is_newer_version(latest: str, current: str) -> bool` in `tfmod_registry_docs`.

- [ ] **Step 1: Write the failing tests**

```python
"""Update check: PyPI latest-version fetch and version comparison."""

import pytest

from tfmod_registry_docs import fetch_latest_pypi_version, is_newer_version


class TestIsNewerVersion:
    def test_newer(self):
        assert is_newer_version("0.17.0", "0.16.0") is True
        assert is_newer_version("1.0.0", "0.99.99") is True

    def test_equal_and_older(self):
        assert is_newer_version("0.16.0", "0.16.0") is False
        assert is_newer_version("0.15.1", "0.16.0") is False

    def test_malformed_fails_closed(self):
        assert is_newer_version("1.0.0rc1", "0.16.0") is False
        assert is_newer_version("banana", "0.16.0") is False
        assert is_newer_version("0.17.0", "0.0.0.dev0") is False


class TestFetchLatestPypiVersion:
    def test_success_via_injected_fetcher(self):
        def fake_fetcher(url, timeout):
            assert url == "https://pypi.org/pypi/tfmodsearch/json"
            assert timeout == 5
            return {"info": {"version": "0.17.0"}}

        assert fetch_latest_pypi_version(fetcher=fake_fetcher) == "0.17.0"

    def test_fetch_error_returns_none(self):
        def failing_fetcher(url, timeout):
            raise OSError("network down")

        assert fetch_latest_pypi_version(fetcher=failing_fetcher) is None

    def test_garbage_payload_returns_none(self):
        assert fetch_latest_pypi_version(fetcher=lambda u, t: {"unexpected": True}) is None
        assert fetch_latest_pypi_version(fetcher=lambda u, t: {"info": {}}) is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/integration/test_update_check.py -v`
Expected: FAIL — `ImportError: cannot import name 'fetch_latest_pypi_version'`.

- [ ] **Step 3: Implement**

In `src/tfmod_registry_docs.py` (reuse existing imports; `urllib.request`, `json`, `Callable` are already there — verify):

```python
PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"


def _pypi_json_fetch(url: str, timeout: int) -> dict:
    if not url.startswith("https://"):
        raise ValueError(f"refusing non-https URL: {url}")
    with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 - scheme guarded above
        return json.loads(resp.read())


def fetch_latest_pypi_version(
    package: str = "tfmodsearch",
    timeout: int = 5,
    fetcher: Callable[[str, int], dict] | None = None,
) -> str | None:
    """Latest released version of *package* on PyPI, or None on any failure.

    Used by the HTTP daemon update check. One anonymous GET to the public
    PyPI JSON API; never raises — the caller treats None as "unknown".
    """
    fetch = fetcher or _pypi_json_fetch
    try:
        payload = fetch(PYPI_JSON_URL.format(package=package), timeout)
        version = payload["info"]["version"]
        return version if isinstance(version, str) and version else None
    except Exception:
        return None


def is_newer_version(latest: str, current: str) -> bool:
    """True when *latest* is strictly newer than *current*.

    Plain X.Y.Z int-tuple comparison; any parse failure returns False
    (fail closed: no update notice on uncertainty). This project publishes
    plain numeric versions, so rc/dev suffixes intentionally do not match.
    """
    try:
        return tuple(map(int, latest.split("."))) > tuple(map(int, current.split(".")))
    except (ValueError, AttributeError):
        return False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/integration/test_update_check.py -v`
Expected: 6 PASS. Also `.venv/bin/pytest tests/integration/test_registry_docs.py -q` — no regression.

- [ ] **Step 5: Commit**

```bash
git add src/tfmod_registry_docs.py tests/integration/test_update_check.py
git commit -m "Add PyPI latest-version fetch and fail-closed version compare"
```

---

### Task 2: Server-side state, check cycle, kill switch

**Files:**
- Modify: `src/tfmod_mcp_server.py` (module level, near `_env_default`/`_is_loopback`)
- Test: `tests/integration/test_update_check.py` (extend)

**Interfaces:**
- Consumes: `fetch_latest_pypi_version`, `is_newer_version` (Task 1); `_SERVER_VERSION` (existing).
- Produces (all in `tfmod_mcp_server`):
  - `_UPDATE_STATE: dict` with keys `latest_version: str | None`, `update_available: bool`
  - `UPDATE_CHECK_INTERVAL_HOURS = 24`
  - `_update_check_enabled(env: Mapping[str, str]) -> bool`
  - `_run_update_check_once(fetcher=None) -> None` (one cycle: fetch, compare, replace state, log)
  - `_update_notice() -> str | None` (message string when update available, else None)
  - `_start_update_checker_thread() -> threading.Thread` (daemon thread looping check+sleep)

- [ ] **Step 1: Write the failing tests** (append to `tests/integration/test_update_check.py`)

```python
import tfmod_mcp_server
from tfmod_mcp_server import (
    _run_update_check_once,
    _update_check_enabled,
    _update_notice,
)


def _reset_state():
    tfmod_mcp_server._UPDATE_STATE = {"latest_version": None, "update_available": False}


class TestUpdateCheckCycle:
    def test_newer_version_sets_state_and_notice(self, monkeypatch):
        _reset_state()
        monkeypatch.setattr(tfmod_mcp_server, "_SERVER_VERSION", "0.16.0")
        _run_update_check_once(fetcher=lambda u, t: {"info": {"version": "0.17.0"}})
        assert tfmod_mcp_server._UPDATE_STATE == {"latest_version": "0.17.0", "update_available": True}
        notice = _update_notice()
        assert "0.17.0" in notice and "0.16.0" in notice
        assert "docker compose pull" in notice

    def test_up_to_date_sets_state_no_notice(self, monkeypatch):
        _reset_state()
        monkeypatch.setattr(tfmod_mcp_server, "_SERVER_VERSION", "0.17.0")
        _run_update_check_once(fetcher=lambda u, t: {"info": {"version": "0.17.0"}})
        assert tfmod_mcp_server._UPDATE_STATE == {"latest_version": "0.17.0", "update_available": False}
        assert _update_notice() is None

    def test_failure_keeps_previous_state(self, monkeypatch):
        _reset_state()
        monkeypatch.setattr(tfmod_mcp_server, "_SERVER_VERSION", "0.16.0")
        _run_update_check_once(fetcher=lambda u, t: {"info": {"version": "0.17.0"}})
        before = dict(tfmod_mcp_server._UPDATE_STATE)

        def failing(u, t):
            raise OSError("down")

        _run_update_check_once(fetcher=failing)
        assert tfmod_mcp_server._UPDATE_STATE == before


class TestKillSwitch:
    def test_default_enabled(self):
        assert _update_check_enabled({}) is True

    def test_falsy_values_disable(self):
        for v in ("0", "false", "no", "off", "FALSE", "Off", ""):
            assert _update_check_enabled({"TFMODSEARCH_UPDATE_CHECK": v}) is False, v

    def test_truthy_values_enable(self):
        for v in ("1", "true", "yes", "on"):
            assert _update_check_enabled({"TFMODSEARCH_UPDATE_CHECK": v}) is True, v
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/integration/test_update_check.py -v -k "Cycle or KillSwitch"`
Expected: FAIL — `ImportError`.

- [ ] **Step 3: Implement**

In `src/tfmod_mcp_server.py`. Add `from tfmod_registry_docs import fetch_latest_pypi_version, is_newer_version` to the existing first-party imports, `from collections.abc import Mapping` if absent (`threading`, `os`, `time` — check; add `import time` if missing). Module level:

```python
UPDATE_CHECK_INTERVAL_HOURS = 24
_UPDATE_CHECK_FALSY = {"", "0", "false", "no", "off"}
_UPDATE_NOTICE_TEMPLATE = (
    "tfmodsearch {latest} is available (this shared daemon runs {current}). "
    "Ask the operator to update: bump the image tag in docker-compose.yml, "
    "then docker compose pull && up -d."
)
# Replaced atomically (single assignment) by the checker thread; readers
# (health route, tool wrappers) never see a torn value thanks to the GIL.
_UPDATE_STATE: dict[str, Any] = {"latest_version": None, "update_available": False}


def _update_check_enabled(env: Mapping[str, str]) -> bool:
    """Kill switch: TFMODSEARCH_UPDATE_CHECK in the falsy set disables the check."""
    return env.get("TFMODSEARCH_UPDATE_CHECK", "1").strip().lower() not in _UPDATE_CHECK_FALSY


def _run_update_check_once(fetcher: Any = None) -> None:
    """One check cycle: fetch latest from PyPI, compare, publish state, log.

    Failures leave the previous state untouched (fetch returns None).
    """
    global _UPDATE_STATE
    logger = logging.getLogger(__name__)
    latest = fetch_latest_pypi_version(fetcher=fetcher) if fetcher else fetch_latest_pypi_version()
    if latest is None:
        logger.debug("Update check failed; keeping previous state")
        return
    newer = is_newer_version(latest, _SERVER_VERSION)
    _UPDATE_STATE = {"latest_version": latest, "update_available": newer}
    if newer:
        logger.warning(_UPDATE_NOTICE_TEMPLATE.format(latest=latest, current=_SERVER_VERSION))


def _update_notice() -> str | None:
    """Agent-facing notice string, or None when no update is known."""
    if _UPDATE_STATE["update_available"]:
        return _UPDATE_NOTICE_TEMPLATE.format(
            latest=_UPDATE_STATE["latest_version"], current=_SERVER_VERSION
        )
    return None


def _start_update_checker_thread() -> threading.Thread:
    """Daily update check in a daemon thread (HTTP mode only; see main())."""

    def _loop() -> None:
        while True:
            _run_update_check_once()
            time.sleep(UPDATE_CHECK_INTERVAL_HOURS * 3600)

    thread = threading.Thread(target=_loop, name="tfmodsearch-update-check", daemon=True)
    thread.start()
    return thread
```

Note the `fetcher` passthrough in `_run_update_check_once`: `fetch_latest_pypi_version(fetcher=fetcher)` when given, plain call otherwise — keep exactly this shape so tests can inject.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/integration/test_update_check.py -v`
Expected: all PASS (Task 1 + Task 2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/tfmod_mcp_server.py tests/integration/test_update_check.py
git commit -m "Add update-check state, cycle, notice, and kill switch to the server"
```

---

### Task 3: Surfacing — /health fields and update_notice on JSON tools

**Files:**
- Modify: `src/tfmod_mcp_server.py` (`health` route ~line 148; `SearchOutput` ~line 639, `ModulesListOutput` ~line 661, `GrepOutput` ~line 686; tool wrappers `modules_list` ~line 1325, `search_modules` ~line 1381, `grep_module_docs` ~line 1589)
- Test: `tests/integration/test_update_check.py` (extend)

**Interfaces:**
- Consumes: `_UPDATE_STATE`, `_update_notice()` (Task 2).
- Produces: `UpdateNoticeMixin(BaseModel)` with optional `update_notice` field that is ABSENT from serialized output when `None`; `SearchOutput`/`ModulesListOutput`/`GrepOutput` inherit it; the three tool wrappers set `result.update_notice = _update_notice()` before returning; `/health` JSON gains `latest_version` and `update_available`.

- [ ] **Step 1: Write the failing tests** (append to `tests/integration/test_update_check.py`)

```python
import json

import pytest
from fastmcp import Client

from tfmod_mcp_server import app


def _set_state(available: bool, latest: str | None = "9.9.9"):
    tfmod_mcp_server._UPDATE_STATE = {"latest_version": latest, "update_available": available}


@pytest.mark.asyncio
async def test_update_notice_absent_when_no_update(initialized_state):
    _set_state(False, "0.16.0")
    async with Client(app) as client:
        result = await client.call_tool("search_modules", {"query": "vpc"})
        payload = json.loads(result.content[0].text)
        assert "update_notice" not in payload


@pytest.mark.asyncio
async def test_update_notice_present_on_json_tools(initialized_state):
    _set_state(True)
    async with Client(app) as client:
        for tool, args in [
            ("search_modules", {"query": "vpc"}),
            ("modules_list", {}),
        ]:
            result = await client.call_tool(tool, args)
            payload = json.loads(result.content[0].text)
            assert "9.9.9" in payload["update_notice"], tool


@pytest.mark.asyncio
async def test_get_module_never_carries_notice(initialized_state):
    _set_state(True)
    async with Client(app) as client:
        result = await client.call_tool("get_module", {"module_identifier": "vpc"})
        assert "update_notice" not in result.content[0].text


@pytest.mark.asyncio
async def test_health_reports_update_fields(initialized_state):
    _set_state(True)
    from starlette.testclient import TestClient  # if unavailable, call the handler directly

    # /health is an async handler; invoke it directly to avoid HTTP plumbing:
    from tfmod_mcp_server import health

    response = await health(None)
    body = json.loads(response.body)
    assert body["latest_version"] == "9.9.9"
    assert body["update_available"] is True
```

`initialized_state` fixture: reuse the pattern the existing `tests/integration/test_mcp_server.py` uses to initialize `ServerStateManager` with the real index (read that file first and copy its fixture approach — likely a module/session fixture calling `ServerStateManager.initialize(...)` guarded by "already initialized"). `grep_module_docs` requires network, so the notice-presence loop covers only the two offline JSON tools; grep gets the same injection code path (same one-liner) and is covered by inspection + the existing grep tool tests remaining green.

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/integration/test_update_check.py -v -k "notice or health_reports"`
Expected: FAIL — no `update_notice` attribute / missing fields.

- [ ] **Step 3: Implement**

In `src/tfmod_mcp_server.py`:

Add `model_serializer` to the pydantic import. Define above `SearchOutput`:

```python
class UpdateNoticeMixin(BaseModel):
    """Adds an optional update_notice that vanishes from output when None.

    FastMCP serializes pydantic None fields as JSON null; the spec requires
    the field to be entirely absent when no update is known, hence the
    wrap-mode serializer (verified against FastMCP 3.4.4).
    """

    update_notice: str | None = Field(
        default=None,
        description="Present only when a newer tfmodsearch release exists; relay it to the user.",
    )

    @model_serializer(mode="wrap")
    def _drop_none_notice(self, handler: Any) -> Any:
        data = handler(self)
        if isinstance(data, dict) and data.get("update_notice") is None:
            data.pop("update_notice", None)
        return data
```

Change `class SearchOutput(BaseModel):` → `class SearchOutput(UpdateNoticeMixin):`, same for `ModulesListOutput` and `GrepOutput` (they keep all their own fields; verify none of the three already defines a custom `model_serializer` — if one does, merge logic instead of overriding).

In each of the three tool wrappers (`search_modules`, `modules_list`, `grep_module_docs`), right before the final `return`:

```python
    result.update_notice = _update_notice()
    return result
```

(Adapt to the wrapper's actual local variable name; read each wrapper first. Do NOT touch `get_module`.)

Update the `health` route to read the state:

```python
    return JSONResponse(
        {
            "status": "ok",
            "version": _SERVER_VERSION,
            "modules": len(state.index.docs),
            "latest_version": _UPDATE_STATE["latest_version"],
            "update_available": _UPDATE_STATE["update_available"],
        }
    )
```

- [ ] **Step 4: Run tests + full server suite**

Run: `.venv/bin/pytest tests/integration/test_update_check.py tests/integration/test_mcp_server.py -q`
Expected: all PASS — notably the pre-existing `test_mcp_server.py` output-shape tests still pass (the mixin is invisible when state says no update, which is the default in tests).

- [ ] **Step 5: Commit**

```bash
git add src/tfmod_mcp_server.py tests/integration/test_update_check.py
git commit -m "Surface update availability via health fields and update_notice on JSON tools"
```

---

### Task 4: main() wiring + e2e

**Files:**
- Modify: `src/tfmod_mcp_server.py` (`main()` HTTP branch, ~line 1950)
- Modify: `tests/e2e/test_mcp_http_e2e.py` (fixture env + new assertions)

**Interfaces:**
- Consumes: `_update_check_enabled`, `_start_update_checker_thread` (Task 2); `/health` fields (Task 3).

- [ ] **Step 1: Wire the thread in main()** — in the HTTP branch, after the warm-once block and before `app.run(...)`:

```python
            if _update_check_enabled(os.environ):
                logger.info("Update check enabled: daily PyPI version check (TFMODSEARCH_UPDATE_CHECK=0 to disable)")
                _start_update_checker_thread()
            else:
                logger.info("Update check disabled via TFMODSEARCH_UPDATE_CHECK")
```

The stdio branch is untouched — no thread ever starts there.

- [ ] **Step 2: Make the e2e suite offline-deterministic and assert the disabled state**

In `tests/e2e/test_mcp_http_e2e.py`:
- The module-scoped `http_server` fixture and `test_env_fallback_serves_http` currently spawn the server without controlling the kill switch — add `TFMODSEARCH_UPDATE_CHECK=0` to both spawn environments (`http_server` uses no explicit env today: pass `env={**os.environ, "TFMODSEARCH_UPDATE_CHECK": "0"}` to its `subprocess.Popen`).
- Extend the existing `test_health_reports_version_and_modules` with the disabled-state observables:

```python
    assert health["latest_version"] is None
    assert health["update_available"] is False
```

- Add one new test asserting no notice leaks into tool output when disabled:

```python
@pytest.mark.e2e
@pytest.mark.timeout(180)
@pytest.mark.asyncio
async def test_no_update_notice_when_disabled(http_server):
    port, _ = http_server
    async with streamablehttp_client(f"http://127.0.0.1:{port}/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("search_modules", {"query": "vpc"})
            assert "update_notice" not in json.loads(_result_text(result))
```

- [ ] **Step 3: Run the e2e suites**

Run: `.venv/bin/pytest tests/e2e/test_mcp_http_e2e.py tests/e2e/test_mcp_stdio_e2e.py -v`
Expected: all PASS (http suite now 7 tests). The stdio suite passing unmodified is the byte-identical-stdio gate.

- [ ] **Step 4: Commit**

```bash
git add src/tfmod_mcp_server.py tests/e2e/test_mcp_http_e2e.py
git commit -m "Start the update checker thread in HTTP mode and pin e2e to the disabled state"
```

---

### Task 5: Docs + version bump 0.17.0 + full verification

**Files:**
- Modify: `README.md`, `docs/docker-container-support.md`, `CHANGELOG.md`, `CLAUDE.md`
- Modify: `pyproject.toml`, `plugins/tfmod-search/.claude-plugin/plugin.json`, `plugins/tfmod-search/.codex-plugin/plugin.json`, `plugins/tfmod-search/bin/tfmodsearch_launch.py`, `docker-compose.yml`

**Interfaces:** none (prose + metadata).

- [ ] **Step 1: Docs**
- README "Shared HTTP instance" section: add an "Update notifications" paragraph after "Managing the daemon" — the daemon checks PyPI once a day; you learn about updates from `curl /health` (`latest_version`/`update_available`), a WARNING in `docker logs`, and an `update_notice` field your agent will relay; disable with `TFMODSEARCH_UPDATE_CHECK=0` (air-gapped); privacy: one anonymous GET to the public PyPI JSON API, nothing about you or your host is sent.
- `docs/docker-container-support.md` §9: one equivalent paragraph.
- CHANGELOG.md: `## [0.17.0] - 2026-07-14` matching the 0.16.0 entry format (Added: update check + three surfacing channels + kill switch; Unchanged: stdio byte-identical, no auto-update, no telemetry, plugin/index untouched).
- CLAUDE.md: server-component bullet for the update check + a `### Recent Improvements (2026-07-14)` note; update the `## Release Process` step-3 grep example if it hardcodes `0.X.Y`.

- [ ] **Step 2: Version bump** — per CLAUDE.md Release Process step 3: `grep -rn "0\.16\.0" pyproject.toml plugins/ README.md docker-compose.yml docs/docker-container-support.md` and bump every **current-release** occurrence to `0.17.0` (pyproject `version`, both plugin manifest `version` fields, `DEFAULT_IMAGE`, compose image tag, README quick-install/`TFMODSEARCH_IMAGE`/offline-verify/HTTP-quickstart tags, docker doc recipe tags). Historical mentions (CHANGELOG 0.16.0 entry, spec files, release-history bullets) stay.

- [ ] **Step 3: Full suite + lint gates**

Run: `.venv/bin/pytest tests/ -q` (expect ~800 passed / 23 skipped; investigate any failure — known local flake: `TestClaudeCliLive` under two claude binaries).
Run: `.venv/bin/ruff check src/ tests/ && .venv/bin/mypy src/` (expect clean; 3 pre-existing nltk/rank_bm25 mypy notes are fine).

- [ ] **Step 4: Docker verification (both modes, per Release Process step 4)**

```bash
docker build -t tfmodsearch:0.17.0-rc .
docker run --network none -i --rm tfmodsearch:0.17.0-rc --warmup
docker run -d --name tfm-rc -p 127.0.0.1:8766:8766 -e TFMODSEARCH_UPDATE_CHECK=0 \
  tfmodsearch:0.17.0-rc --transport http --host 0.0.0.0 --port 8766
# poll http://127.0.0.1:8766/health until 200; assert latest_version null, update_available false
# then one enabled-path spot check (real PyPI):
docker rm -f tfm-rc
docker run -d --name tfm-rc -p 127.0.0.1:8766:8766 tfmodsearch:0.17.0-rc --transport http --host 0.0.0.0 --port 8766
# poll /health; within ~30s of startup expect latest_version to become non-null (real PyPI answer)
docker rm -f tfm-rc
```

- [ ] **Step 5: Commit**

```bash
git add README.md docs/docker-container-support.md CHANGELOG.md pyproject.toml plugins/ docker-compose.yml
git commit -m "Document update notifications and bump version to 0.17.0"
```

---

### Task 6: Independent review + release (repo convention)

- [ ] Opus subagent reviews `git diff master...HEAD` against the spec; fix real findings.
- [ ] Present to the user; push + PR **only after explicit approval**; then Copilot threads → merge → tag `v0.17.0` → CI publishes → post-release verification per CLAUDE.md `## Release Process` step 7.
