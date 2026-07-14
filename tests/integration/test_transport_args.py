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
