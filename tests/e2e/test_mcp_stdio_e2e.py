"""
End-to-end tests for the MCP server over real stdio transport.

Spawns the actual server process (src/tfmod_mcp_server.py) and speaks the
MCP protocol through the official client SDK: initialize handshake,
tools/list discovery, tools/call for all three tools, security rejections,
and the --warmup maintenance flag.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).parent.parent.parent
SERVER_SCRIPT = PROJECT_ROOT / "src" / "tfmod_mcp_server.py"

EXPECTED_TOOLS = {"modules_list", "search_modules", "get_module", "grep_module_docs"}


def _server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
        cwd=str(PROJECT_ROOT),
    )


def _result_text(result) -> str:
    assert result.content, "tool result has no content"
    return result.content[0].text


@pytest.mark.e2e
@pytest.mark.timeout(180)
@pytest.mark.asyncio
async def test_full_stdio_protocol_session():
    """One full client session: handshake, discovery, and every tool."""
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            # --- initialize handshake ---
            init = await session.initialize()
            assert init.serverInfo.name == "tfmod-search"
            assert init.serverInfo.version, "version must derive from package metadata"
            assert init.instructions, "server must advertise instructions"
            assert "search_modules" in init.instructions
            assert "get_module" in init.instructions

            # --- tools/list ---
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            assert names == EXPECTED_TOOLS
            for tool in tools.tools:
                assert tool.description, f"{tool.name} missing description"
                assert tool.inputSchema is not None, f"{tool.name} missing input schema"

            # --- modules_list (compact default) ---
            result = await session.call_tool("modules_list", {})
            assert not result.isError
            payload = json.loads(_result_text(result))
            assert payload["count"] == 63
            assert len(payload["modules"]) == 63
            sample = payload["modules"][0]
            assert set(sample) >= {"module_name", "purpose", "module_id", "latest_version"}
            assert "keywords" not in sample, "compact default must omit keyword arrays"

            # --- modules_list (detail=full) ---
            result = await session.call_tool("modules_list", {"detail": "full"})
            assert not result.isError
            full_payload = json.loads(_result_text(result))
            full_sample = full_payload["modules"][0]
            assert set(full_sample) >= {"module_name", "path", "description", "keywords"}

            # --- search_modules ---
            result = await session.call_tool("search_modules", {"query": "vpc networking"})
            assert not result.isError
            hits = json.loads(_result_text(result))["results"]
            assert 1 <= len(hits) <= 3
            assert any(h["module_name"] == "vpc" for h in hits)
            for hit in hits:
                assert set(hit) >= {"module_name", "path", "keywords", "description", "score"}
                assert isinstance(hit["score"], int | float)
            scores = [h["score"] for h in hits]
            assert scores == sorted(scores, reverse=True), "results must be ranked by score"

            # --- get_module by name ---
            result = await session.call_tool("get_module", {"module_identifier": "vpc"})
            assert not result.isError
            doc = _result_text(result)
            assert "vpc" in doc.lower()
            assert len(doc) > 1000, "full documentation expected, not a stub"

            # --- get_module by path ---
            result = await session.call_tool(
                "get_module", {"module_identifier": "modules/terraform-aws-modules/s3-bucket.md"}
            )
            assert not result.isError
            assert "s3" in _result_text(result).lower()


@pytest.mark.e2e
@pytest.mark.timeout(120)
@pytest.mark.asyncio
async def test_get_module_rejects_unsafe_and_unknown_identifiers():
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for bad in (
                "/etc/passwd",
                "../../etc/passwd",
                "modules/../../../etc/passwd",
                "no-such-module-xyz",
            ):
                result = await session.call_tool("get_module", {"module_identifier": bad})
                text = _result_text(result).lower()
                assert result.isError or "not found" in text, f"expected rejection for {bad!r}, got: {text[:200]}"


@pytest.mark.e2e
@pytest.mark.timeout(120)
@pytest.mark.asyncio
async def test_get_module_name_lookup_is_lenient_but_not_fuzzy():
    """Prefixed and unique-substring names resolve; garbage errors with suggestions."""
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # normalization: terraform-aws- prefix strips to the canonical name
            result = await session.call_tool("get_module", {"module_identifier": "terraform-aws-vpc"})
            assert not result.isError
            assert "terraform-aws-modules/vpc/aws" in _result_text(result)

            # unique substring resolves ("s3" only matches s3-bucket)
            result = await session.call_tool("get_module", {"module_identifier": "s3"})
            assert not result.isError
            assert "s3-bucket" in _result_text(result)

            # unknown names must error with suggestions, not return a random module
            result = await session.call_tool("get_module", {"module_identifier": "no-such-module-xyz"})
            assert result.isError
            assert "search_modules" in _result_text(result)


@pytest.mark.e2e
@pytest.mark.timeout(300)
def test_warmup_flag_loads_everything_and_exits():
    proc = subprocess.run(
        [sys.executable, str(SERVER_SCRIPT), "--warmup"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=280,
    )
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert "Warmup complete" in proc.stdout
    assert "63 modules" in proc.stdout
