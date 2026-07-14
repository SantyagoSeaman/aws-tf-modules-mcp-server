"""Update check: PyPI latest-version fetch and version comparison."""

import json
import logging

import pytest
from fastmcp import Client

import tfmod_mcp_server
from tests.integration import PROJECT_ROOT
from tfmod_mcp_server import (
    SearchWeights,
    ServerStateManager,
    _run_update_check_once,
    _update_check_enabled,
    _update_notice,
    app,
    health,
)
from tfmod_registry_docs import fetch_latest_pypi_version, is_newer_version
from tfmod_search_lib import load_index


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


@pytest.fixture(scope="module")
def _update_check_index():
    """Load the real search index once per module (reused by initialized_state)."""
    logger = logging.getLogger(__name__)
    index_path = PROJECT_ROOT / "model" / "tfmod_e5_small_index.pkl"
    if not index_path.exists():
        pytest.skip(f"Index file not found at {index_path}")
    return load_index(str(index_path), logger)


@pytest.fixture
def initialized_state(_update_check_index):
    """Initialize ServerStateManager with the real index for in-process Client calls.

    Mirrors the server_state fixture pattern in test_mcp_server.py: reset before
    initializing (so re-initialization across tests never raises "already
    initialized"), yield, then reset again for cleanup.
    """
    logger = logging.getLogger(__name__)
    index_path = PROJECT_ROOT / "model" / "tfmod_e5_small_index.pkl"
    weights = SearchWeights(w_kw=2.0, w_exact=3.0, w_bm25=1.0, w_sem=1.0)

    ServerStateManager.reset()
    try:
        state = ServerStateManager.initialize(
            index=_update_check_index, weights=weights, index_path=index_path, logger=logger
        )
    except RuntimeError:
        ServerStateManager.reset()
        state = ServerStateManager.initialize(
            index=_update_check_index, weights=weights, index_path=index_path, logger=logger
        )

    yield state

    ServerStateManager.reset()


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

    # /health is an async handler; invoke it directly to avoid HTTP plumbing.
    response = await health(None)
    body = json.loads(response.body)
    assert body["latest_version"] == "9.9.9"
    assert body["update_available"] is True
