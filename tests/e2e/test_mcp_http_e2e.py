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
import urllib.error
import urllib.request
from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

PROJECT_ROOT = Path(__file__).parent.parent.parent
SERVER_SCRIPT = PROJECT_ROOT / "src" / "tfmod_mcp_server.py"
EXPECTED_TOOLS = {"modules_list", "search_modules", "get_module"}
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
        env={**os.environ, "TFMODSEARCH_UPDATE_CHECK": "0"},
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
    assert health["latest_version"] is None
    assert health["update_available"] is False


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
async def test_modules_list_over_http_no_path_required_union(http_server):
    """Regression (0.23.1): over the real HTTP transport, the advertised
    modules_list output-item schema must carry NO anyOf and must NOT require
    `path`, and BOTH the compact default and detail=full must return cleanly.

    A strict MCP output-schema validator (the plugin proxy / host client)
    mis-resolved the prior ``list[Compact] | list[Full]`` union into requiring
    `path`, so the compact default failed with "'path' is a required property".
    The stdio e2e path never exercised this. Guard the wire schema here."""
    port, _ = http_server
    async with streamablehttp_client(f"http://127.0.0.1:{port}/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            ml = next(t for t in tools.tools if t.name == "modules_list")
            out_schema = ml.outputSchema
            modules = out_schema["properties"]["modules"]
            # the modules field itself must not be a union of arrays
            assert "anyOf" not in modules, f"modules field must not be a union: {modules}"
            items = modules["items"]
            # the advertised item schema may be inlined or a $ref into $defs/definitions;
            # resolve it before asserting, so the check is not a trivial false-positive
            if "$ref" in items:
                ref = items["$ref"].split("/")[-1]
                defs = out_schema.get("$defs") or out_schema.get("definitions") or {}
                items = defs[ref]
            assert "anyOf" not in items, f"modules item schema must not be a union: {items}"
            assert "path" not in (items.get("required") or []), "path must be optional in the advertised item schema"

            compact = json.loads(_result_text(await session.call_tool("modules_list", {})))
            assert compact["count"] > 0 and compact["modules"], "compact modules_list empty over HTTP"
            assert "path" not in compact["modules"][0], "compact item must stay lean (no path)"
            assert "purpose" in compact["modules"][0]

            full = json.loads(_result_text(await session.call_tool("modules_list", {"detail": "full"})))
            assert full["count"] == compact["count"]
            assert "path" in full["modules"][0]


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
@pytest.mark.timeout(180)
def test_cross_origin_request_rejected(http_server):
    """DNS-rebinding guard: a browser-style cross-origin POST must be rejected.

    host_origin_protection="auto" installs FastMCP Host/Origin validation; SDK
    clients and curl send no Origin header and pass (covered by the other tests).
    """
    port, _ = http_server
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "t", "version": "1"},
            },
        }
    ).encode()
    req = urllib.request.Request(  # noqa: S310 (trusted local host)
        f"http://127.0.0.1:{port}/mcp",
        data=body,
        headers={
            "Origin": "http://evil.example",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    with pytest.raises(urllib.error.HTTPError) as excinfo:
        urllib.request.urlopen(req, timeout=10)  # noqa: S310 (trusted local host)
    assert excinfo.value.code == 403


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


@pytest.mark.e2e
@pytest.mark.timeout(240)
def test_env_fallback_serves_http():
    port = _free_port()
    env = {
        **os.environ,
        "TFMODSEARCH_TRANSPORT": "http",
        "TFMODSEARCH_PORT": str(port),
        "TFMODSEARCH_UPDATE_CHECK": "0",
    }
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
