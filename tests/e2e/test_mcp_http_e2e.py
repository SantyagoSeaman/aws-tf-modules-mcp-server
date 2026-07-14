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
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as resp:  # noqa: S310 (trusted local host)
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
    queries = [
        "vpc",
        "s3 bucket",
        "kubernetes cluster",
        "lambda",
        "rds database",
        "iam role",
        "cloudfront cdn",
        "sqs queue",
    ]

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
