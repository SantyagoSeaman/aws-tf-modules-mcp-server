#!/usr/bin/env python3
import argparse
import logging

from tfmod_search_lib import (
    BGE_QUERY_INSTRUCTION,
    DEFAULT_MODEL_NAME,
    build_index,
    compute_scores,
    initialize_nltk,
    load_index,
    resolve_index_path,
    save_index,
    setup_logging,
)


def cmd_index(args, logger: logging.Logger):
    """
    Build and persist a search index from Terraform module documentation.

    This command scans a directory for Markdown files, extracts module information
    (module names and keywords), generates semantic embeddings using a sentence
    transformer model, builds a BM25 index, and saves everything to a pickle file.

    The created index contains:
    - Document records with parsed metadata
    - BM25 corpus for text relevance scoring
    - Semantic embeddings (L2-normalized vectors)
    - Keyword IDF (Inverse Document Frequency) scores
    - Module names and keyword sets for fast lookup

    Args:
        args: Namespace object with the following attributes:
            - docs_dir (str): Directory containing .md files to index
            - index_path (str): Output path for the pickled index file
            - model (str): Sentence transformer model name (default: intfloat/e5-small-v2)

    Returns:
        None. Prints summary and saves index to disk.

    Example:
        $ python tfmod_search_cli.py index \\
            --docs_dir ./modules/terraform-aws-modules \\
            --index_path ./model/tfmod_e5_small_index.pkl \\
            --model intfloat/e5-small-v2
    """
    logger.info("Starting index command")
    logger.info(f"  docs_dir: {args.docs_dir}")
    logger.info(f"  index_path: {args.index_path}")
    logger.info(f"  model: {args.model}")

    try:
        idx = build_index(args.docs_dir, model_name=args.model, logger=logger)
        save_index(idx, args.index_path, logger=logger)
        logger.info("Index command completed successfully")
        print(f"Indexed {len(idx.docs)} documents → {args.index_path}")
    except Exception as e:
        logger.error(f"Index command failed: {e}")
        raise


def cmd_search(args, logger: logging.Logger):
    """
    Query the search index with natural language and display ranked results.

    This command loads a prebuilt search index and performs hybrid search using
    four scoring components:
    1. Keyword overlap (IDF-weighted)
    2. Exact module name matching
    3. BM25 text relevance
    4. Semantic similarity (cosine similarity of embeddings)

    Each component can be weighted independently to tune search behavior.

    Args:
        args: Namespace object with the following attributes:
            - index_path (str): Path to pickled search index file
            - query (str): Natural language search query
            - top_k (int): Number of results to return (default: 10)
            - w_kw (float): Weight for keyword overlap scoring (default: 2.0)
            - w_exact (float): Weight for exact module name match (default: 3.0)
            - w_bm25 (float): Weight for BM25 text relevance (default: 1.0)
            - w_sem (float): Weight for semantic similarity (default: 1.0)
            - query_instruction (str|None): Optional query instruction prefix for BGE models

    Returns:
        None. Prints ranked search results to stdout.

    Output Format:
        For each result, displays:
        - Rank and combined score
        - Module name
        - Keywords
        - File path
        - Text preview (first non-empty line)

    Example:
        $ python tfmod_search_cli.py search \\
            --index_path ./model/tfmod_e5_small_index.pkl \\
            --query "s3 bucket with encryption" \\
            --top_k 5
    """
    logger.info("Starting search command")
    logger.info(f"  index_path: {args.index_path}")
    logger.info(f"  query: {args.query}")
    logger.info(f"  top_k: {args.top_k}")
    logger.info(f"  weights: kw={args.w_kw}, exact={args.w_exact}, bm25={args.w_bm25}, sem={args.w_sem}")
    logger.info(f"  query_instruction: {args.query_instruction}")

    try:
        idx = load_index(args.index_path, logger=logger)
        results = compute_scores(
            idx,
            args.query,
            w_kw=args.w_kw,
            w_exact=args.w_exact,
            w_bm25=args.w_bm25,
            w_sem=args.w_sem,
            top_k=args.top_k,
            query_instruction=args.query_instruction,
            logger=logger,
        )
        logger.info(f"Search command completed successfully, displaying {len(results)} results")

        print(f"Query: {args.query}\n")
        for rank, (score, i) in enumerate(results, 1):
            d = idx.docs[i]
            print(f"[{rank}] score={score:.3f}")
            print(f"  module_name : {d.module_name or '(n/a)'}")
            print(f"  keywords    : {', '.join(d.keywords) if d.keywords else '(n/a)'}")
            print(f"  path        : {d.path}")
            snippet = d.text.strip().splitlines()[0:3]
            for line in snippet:
                if line.strip():
                    print(f"  preview     : {line[:160]}")
                    break
            print()
    except Exception as e:
        logger.error(f"Search command failed: {e}")
        raise


def build_argparser():
    p = argparse.ArgumentParser(description="TFModSearch CLI - Hybrid search tool for Terraform module documentation")
    p.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )
    sub = p.add_subparsers(dest="cmd", required=True, help="Available commands")

    # Index subcommand - Build search index from documentation
    p_idx = sub.add_parser("index", help="Build and persist the search index from Markdown documentation")
    p_idx.add_argument(
        "--docs_dir", required=True, help="Directory containing Terraform module documentation (.md files)"
    )
    p_idx.add_argument(
        "--index_path",
        type=str,
        help="Output path for the pickled search index file. If not specified, uses './model/tfmod_e5_small_index.pkl'",
    )
    p_idx.add_argument(
        "--model",
        default=DEFAULT_MODEL_NAME,
        help=f"Sentence transformer model name for semantic embeddings (default: {DEFAULT_MODEL_NAME})",
    )
    p_idx.set_defaults(func=cmd_index)

    # Search subcommand - Query the index
    p_s = sub.add_parser("search", help="Query the search index with natural language")
    p_s.add_argument(
        "--index_path",
        type=str,
        help="Path to the pickled search index file. If not specified, uses './model/tfmod_e5_small_index.pkl'",
    )
    p_s.add_argument("--query", required=True, help="Natural language search query (e.g., 's3 bucket with encryption')")
    p_s.add_argument("--top_k", type=int, default=10, help="Number of top results to return (default: 10)")
    p_s.add_argument("--w_kw", type=float, default=2.0, help="Weight for keyword overlap scoring (default: 2.0)")
    p_s.add_argument("--w_exact", type=float, default=3.0, help="Weight for exact module name match (default: 3.0)")
    p_s.add_argument("--w_bm25", type=float, default=1.0, help="Weight for BM25 text relevance scoring (default: 1.0)")
    p_s.add_argument("--w_sem", type=float, default=1.0, help="Weight for semantic similarity scoring (default: 1.0)")
    p_s.add_argument(
        "--query-instruction",
        dest="query_instruction",
        type=str,
        default=None,
        help=f"Optional query instruction prefix for BGE models. Use '{BGE_QUERY_INSTRUCTION}' for improved short query retrieval",
    )
    p_s.set_defaults(func=cmd_search)
    return p


def main():
    parser = build_argparser()
    args = parser.parse_args()

    # Initialize NLTK before any operations
    initialize_nltk()

    # Set up logging
    logger = setup_logging("cli.log", args.log_level)

    # Resolve index_path using shared logic from tfmod_search_lib
    index_path = resolve_index_path(args.index_path)

    # Ensure parent directory exists for index command
    if args.cmd == "index":
        index_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert resolved path back to string for compatibility
    args.index_path = str(index_path)

    args.func(args, logger)


if __name__ == "__main__":
    main()
