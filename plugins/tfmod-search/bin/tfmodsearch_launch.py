#!/usr/bin/env python3
"""Dual-mode launcher for the tfmod-search MCP server plugin.

Default (env unset): `uvx tfmodsearch` — unchanged local launch path.
Opt-in (`TFMODSEARCH_DOCKER=1`): `docker run -i --rm <image>` — the official,
offline Docker image (tag overridable via `TFMODSEARCH_IMAGE`). If Docker is
requested but not on PATH, falls back to uvx with a warning instead of failing.

`os.execvp` replaces this process so the stdio pipe is inherited transparently
between the MCP client and whichever backend is selected.
"""

import os
import shutil
import sys
from collections.abc import Mapping

DEFAULT_IMAGE = "ghcr.io/santyagoseaman/tfmodsearch:0.15.0"
_FALSY = {"", "0", "false", "no", "off"}


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


def main() -> None:
    command, argv, docker_unavailable = select_backend(os.environ, sys.argv[1:])
    if docker_unavailable:
        print(
            "tfmodsearch_launch: TFMODSEARCH_DOCKER is set but 'docker' is not on PATH; " "falling back to uvx.",
            file=sys.stderr,
        )
    os.execvp(command, argv)  # noqa: S606 -- no shell by design, argv is not shell-interpreted


if __name__ == "__main__":
    main()
