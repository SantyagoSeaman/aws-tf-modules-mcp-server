"""Argument parsing for the tfmodsearch server, kept import-light on purpose.

This module must import NOTHING heavy (no tfmod_search_lib, no
sentence_transformers/torch): the lightweight proxy entry path
(tfmod_entry -> tfmod_proxy) parses arguments through it before deciding
whether the full server module ever loads.
"""

import argparse
import os
import sys

# Help-text copy of tfmod_search_lib.BGE_QUERY_INSTRUCTION. Duplicated as a
# literal because importing tfmod_search_lib here would pull the whole ML stack
# into the proxy path; the lib constant stays authoritative for behavior.
BGE_QUERY_INSTRUCTION_HELP = "Represent this sentence for searching relevant passages: "


def _env_default(name: str, fallback: str) -> str:
    """Environment fallback for a CLI default (empty/unset -> fallback)."""
    value = os.environ.get(name, "").strip()
    return value if value else fallback


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse and return command-line arguments.

    Returns:
        Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="TFModSearch MCP Server - Terraform module search over stdio",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--index_path",
        type=str,
        help="Path to the search index file (.pkl). Defaults to './model/tfmod_e5_small_index.pkl'",
    )
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to YAML config file")
    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument("--w_kw", type=float, help="Override weight for keyword matching")
    parser.add_argument("--w_exact", type=float, help="Override weight for exact module name match")
    parser.add_argument("--w_bm25", type=float, help="Override weight for BM25 text relevance")
    parser.add_argument("--w_sem", type=float, help="Override weight for semantic similarity")
    parser.add_argument(
        "--query-instruction",
        dest="query_instruction",
        type=str,
        default=None,
        help=f"Optional query instruction prefix for BGE models. Use '{BGE_QUERY_INSTRUCTION_HELP}' for improved short query retrieval",
    )
    parser.add_argument(
        "--warmup",
        action="store_true",
        help="Load the index and embedding model (downloading the model if needed), run a test query, and exit",
    )
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "http"],
        default=_env_default("TFMODSEARCH_TRANSPORT", "stdio"),
        help="MCP transport: stdio (default, one process per client) or http "
        "(streamable HTTP shared instance at /mcp). Env fallback: TFMODSEARCH_TRANSPORT",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=_env_default("TFMODSEARCH_HOST", "127.0.0.1"),
        help="Bind address for --transport http. Env fallback: TFMODSEARCH_HOST",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=_env_default("TFMODSEARCH_PORT", "8765"),
        help="Bind port for --transport http. Env fallback: TFMODSEARCH_PORT",
    )
    parser.add_argument(
        "--proxy-url",
        dest="proxy_url",
        type=str,
        default=None,
        help="Run as a stdio proxy forwarding to a remote streamable HTTP MCP server "
        "(e.g. http://127.0.0.1:8765/mcp). Implies stdio; loads no index and no "
        "embedding model. Index/weight flags are accepted but ignored in this mode.",
    )

    args = parser.parse_args(argv)
    # argparse does not validate string defaults against choices, so a bad
    # TFMODSEARCH_TRANSPORT value would otherwise slip through silently.
    if args.transport not in ("stdio", "http"):
        parser.error(f"invalid transport {args.transport!r} (check TFMODSEARCH_TRANSPORT): choose stdio or http")
    if args.proxy_url:
        # Only an explicit CLI --transport http is a real conflict; an env-derived
        # http fallback (TFMODSEARCH_TRANSPORT exported globally) is silently
        # overridden because the proxy is by definition a stdio-side helper.
        cli_argv = sys.argv[1:] if argv is None else argv
        transport_given_explicitly = any(a == "--transport" or a.startswith("--transport=") for a in cli_argv)
        if transport_given_explicitly and args.transport == "http":
            parser.error("--proxy-url runs a stdio-side proxy and cannot be combined with --transport http")
        if args.warmup:
            parser.error("--proxy-url loads no model, so there is nothing to warm up; drop --warmup")
        args.transport = "stdio"
    return args
