"""Lightweight console entry point for the tfmodsearch command.

Dispatches --proxy-url invocations to the torch-free proxy path BEFORE
tfmod_mcp_server (whose import pulls sentence_transformers/torch: hundreds of
MB of RSS, seconds of startup) ever loads. Every other invocation delegates to
the full server module unchanged.
"""

import sys


def main() -> None:
    argv = sys.argv[1:]
    if any(a == "--proxy-url" or a.startswith("--proxy-url=") for a in argv):
        from tfmod_server_args import parse_arguments

        args = parse_arguments(argv)

        from tfmod_proxy import run_proxy

        run_proxy(args.proxy_url, log_level=args.log_level)
        return

    from tfmod_mcp_server import main as server_main

    server_main()


if __name__ == "__main__":
    main()
