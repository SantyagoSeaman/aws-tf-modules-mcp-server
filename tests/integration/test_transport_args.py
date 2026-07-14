"""Transport argument parsing: defaults, env fallbacks, CLI precedence."""

import pytest

from tfmod_mcp_server import _is_loopback, parse_arguments


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


def test_is_loopback_true_cases():
    assert _is_loopback("127.0.0.1")
    assert _is_loopback("::1")
    assert _is_loopback("localhost")
    assert _is_loopback("LOCALHOST")


def test_is_loopback_false_cases():
    assert not _is_loopback("0.0.0.0")
    assert not _is_loopback("192.168.1.10")
    assert not _is_loopback("example.com")


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
