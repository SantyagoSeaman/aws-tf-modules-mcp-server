"""Torch-free stdio->HTTP proxy runner for --proxy-url.

Deliberately imports neither tfmod_search_lib nor tfmod_mcp_server (whose
import pulls sentence_transformers/torch, hundreds of MB of RSS and multiple
seconds of startup): the whole point of proxy mode is a lightweight
per-session process while the shared HTTP daemon owns the model and index.
Logging goes to stderr only -- stdout belongs to the MCP JSON-RPC stream.
"""

import logging
import sys


def _redact_userinfo(url: str) -> str:
    """Strip user:password@ credentials from a URL before it reaches any log."""
    from urllib.parse import urlsplit, urlunsplit

    parts = urlsplit(url)
    if parts.username is None and parts.password is None:
        return url
    netloc = parts.hostname or ""
    if parts.port:
        netloc = f"{netloc}:{parts.port}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def run_proxy(proxy_url: str, log_level: str = "INFO") -> None:
    """Serve stdio MCP, transparently forwarding everything to proxy_url."""
    logging.basicConfig(
        stream=sys.stderr,
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info(f"Proxy mode: forwarding stdio to {_redact_userinfo(proxy_url)}")

    from fastmcp.server import create_proxy

    proxy = create_proxy(proxy_url)
    proxy.run(transport="stdio")
