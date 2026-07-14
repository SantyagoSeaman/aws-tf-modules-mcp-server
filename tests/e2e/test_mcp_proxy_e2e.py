"""
End-to-end tests for --proxy-url: a stdio proxy forwarding to a real HTTP daemon.

Spawns the HTTP daemon on an ephemeral port, then spawns the proxy as a stdio
subprocess and speaks MCP through it via the official SDK client. The proxy is
launched with a nonexistent index path and an empty offline HF cache, proving
it loads neither the index nor the embedding model.
"""

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
ENTRY_SCRIPT = PROJECT_ROOT / "src" / "tfmod_entry.py"
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


@pytest.mark.e2e
@pytest.mark.timeout(240)
@pytest.mark.asyncio
async def test_entry_dispatcher_serves_proxy_light(http_daemon, tmp_path):
    # The console-script path: tfmod_entry dispatches --proxy-url to the
    # torch-free proxy module. Same offline guards as above, plus a startup
    # bound tight enough (10s) that a torch import would trip it.
    empty_hf = tmp_path / "hf-empty-entry"
    empty_hf.mkdir(exist_ok=True)
    params = StdioServerParameters(
        command=sys.executable,
        args=[
            str(ENTRY_SCRIPT),
            "--proxy-url",
            f"http://127.0.0.1:{http_daemon}/mcp",
            "--index_path",
            "/nonexistent/never-loaded.pkl",
        ],
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "HF_HOME": str(empty_hf), "HF_HUB_OFFLINE": "1"},
    )
    start = time.monotonic()
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            assert time.monotonic() - start < 10
            result = await session.call_tool("search_modules", {"query": "vpc networking", "top_k": 1})
            payload = json.loads(result.content[0].text)
            assert payload["results"][0]["module_name"]
