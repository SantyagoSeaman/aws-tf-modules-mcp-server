#!/usr/bin/env python3
"""Multi-mode launcher for the tfmod-search MCP server plugin.

Default (env unset): `uvx tfmodsearch` — unchanged local launch path.
Opt-in (`TFMODSEARCH_DOCKER=1`): `docker run -i --rm <image>` — the official,
offline Docker image (tag overridable via `TFMODSEARCH_IMAGE`). If Docker is
requested but not on PATH, falls back to uvx with a warning instead of failing.
Opt-in (`TFMODSEARCH_URL=<url>` or `TFMODSEARCH_URL=1` for the default
http://127.0.0.1:8765/mcp): stdio proxy to a shared HTTP daemon — `uvx
tfmodsearch --proxy-url <url>`. Takes precedence over TFMODSEARCH_DOCKER.
The daemon is health-checked first (3 s); if it is not responding, falls back
to the local uvx/Docker path with a warning so the session keeps working.

`os.execvp` replaces this process so the stdio pipe is inherited transparently
between the MCP client and whichever backend is selected.
"""

import os
import shutil
import sys
from collections.abc import Mapping

DEFAULT_IMAGE = "ghcr.io/santyagoseaman/tfmodsearch:0.24.0"
_FALSY = {"", "0", "false", "no", "off"}
DEFAULT_PROXY_URL = "http://127.0.0.1:8765/mcp"
# --proxy-url exists only since 0.18.0; without this floor a stale uvx cache could
# resolve an older tfmodsearch and die on the unknown flag AFTER the exec (no fallback).
PROXY_PACKAGE_SPEC = "tfmodsearch>=0.18.0"
_TRUTHY_SHORTHAND = {"1", "true", "yes", "on"}


def resolve_proxy_url(env: Mapping[str, str]) -> str | None:
    """Return the proxy target URL, the default URL for shorthand truthy values, or None."""
    raw = env.get("TFMODSEARCH_URL", "").strip()
    if raw.lower() in _FALSY:
        return None
    if raw.lower() in _TRUTHY_SHORTHAND:
        return DEFAULT_PROXY_URL
    return _normalize_proxy_url(raw)


def _redact_userinfo(url: str) -> str:
    """Strip user:password@ credentials from a URL before printing it to stderr."""
    from urllib.parse import urlsplit, urlunsplit

    parts = urlsplit(url)
    if parts.username is None and parts.password is None:
        return url
    netloc = parts.hostname or ""
    if parts.port:
        netloc = f"{netloc}:{parts.port}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def _normalize_proxy_url(url: str) -> str:
    """Default a bare-origin http(s) URL to the /mcp endpoint path.

    Users plausibly set TFMODSEARCH_URL=http://127.0.0.1:8765 (the origin they
    curl for /health); without this the health preflight would pass but the
    proxy would then fail against the root path, AFTER the exec (no fallback).
    Non-http schemes are returned untouched and left to fail the preflight.
    """
    from urllib.parse import urlsplit, urlunsplit

    parts = urlsplit(url)
    if parts.scheme in ("http", "https") and parts.path in ("", "/"):
        return urlunsplit((parts.scheme, parts.netloc, "/mcp", parts.query, parts.fragment))
    return url


def health_url_for(mcp_url: str) -> str:
    """Derive the /health URL on the same origin as the MCP endpoint."""
    from urllib.parse import urlsplit, urlunsplit

    parts = urlsplit(mcp_url)
    return urlunsplit((parts.scheme, parts.netloc, "/health", "", ""))


def daemon_healthy(url: str, timeout: float = 3.0, fetcher=None) -> bool:
    """True if GET <url> returns 200 within timeout; False on any error."""
    if fetcher is None:

        def fetcher(u: str, t: float) -> int:
            import urllib.request

            with urllib.request.urlopen(u, timeout=t) as resp:  # noqa: S310 -- loopback daemon health probe
                return resp.status

    try:
        return fetcher(url, timeout) == 200
    except Exception:
        return False


def select_backend(env: Mapping[str, str], extra_args: list[str]) -> tuple[str, list[str], bool]:
    """Return (command, argv, docker_unavailable) for the backend selected by env.

    docker_unavailable is True when Docker was requested via TFMODSEARCH_DOCKER but
    is not on PATH, so the caller falls back to uvx and can warn about it.
    """
    if env.get("TFMODSEARCH_DOCKER", "").strip().lower() not in _FALSY:
        if shutil.which("docker") is None:
            return "uvx", ["uvx", "tfmodsearch", *extra_args], True
        image = env.get("TFMODSEARCH_IMAGE", DEFAULT_IMAGE)
        return "docker", ["docker", "run", "-i", "--rm", image, *extra_args], False
    return "uvx", ["uvx", "tfmodsearch", *extra_args], False


def main(env: Mapping[str, str] | None = None) -> None:
    if env is None:
        env = os.environ
    proxy_url = resolve_proxy_url(env)
    if proxy_url is not None:
        fallback_reason = None
        if shutil.which("uvx") is None:
            fallback_reason = "uvx is not on PATH"
        elif not daemon_healthy(health_url_for(proxy_url)):
            fallback_reason = f"{_redact_userinfo(proxy_url)} is not responding"
        if fallback_reason is None:
            # Printed only when the proxy actually launches: on fallback the
            # normal selection below DOES honor TFMODSEARCH_DOCKER.
            if env.get("TFMODSEARCH_DOCKER", "").strip().lower() not in _FALSY:
                print(
                    "tfmodsearch_launch: TFMODSEARCH_URL takes precedence; ignoring TFMODSEARCH_DOCKER.",
                    file=sys.stderr,
                )
            argv = ["uvx", "--from", PROXY_PACKAGE_SPEC, "tfmodsearch", "--proxy-url", proxy_url]
            os.execvp("uvx", argv)  # noqa: S606, S607 -- no shell by design, uvx resolved via PATH
            return  # type: ignore[unreachable]  # os.execvp is typed NoReturn but tests stub it out
        print(
            f"tfmodsearch_launch: TFMODSEARCH_URL is set but {fallback_reason}; " "falling back to a local server.",
            file=sys.stderr,
        )
    command, argv, docker_unavailable = select_backend(env, sys.argv[1:])
    if docker_unavailable:
        print(
            "tfmodsearch_launch: TFMODSEARCH_DOCKER is set but 'docker' is not on PATH; " "falling back to uvx.",
            file=sys.stderr,
        )
    os.execvp(command, argv)  # noqa: S606 -- no shell by design, argv is not shell-interpreted


if __name__ == "__main__":
    main()
