"""Update check: PyPI latest-version fetch and version comparison."""

import tfmod_mcp_server
from tfmod_mcp_server import (
    _run_update_check_once,
    _update_check_enabled,
    _update_notice,
)
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
