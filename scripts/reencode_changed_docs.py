#!/usr/bin/env python3
"""Drift-safe re-encode helper: refresh only the changed docs in the index.

Rebuilding the whole index (`build_index`) re-encodes every document and
perturbs embeddings for docs that were not touched, which breaks the golden
retrieval set. This script instead loads the existing pickled `SearchIndex`,
replaces the `DocRecord`/tokens/vector row for each CHANGED doc only, rebuilds
the corpus-wide BM25 and keyword-IDF structures (cheap, deterministic given
the token/keyword inputs), and saves back in place. Unchanged docs keep their
`doc_vectors` row byte-identical.

Usage: python scripts/reencode_changed_docs.py <index_path> <changed_doc_path> [<changed_doc_path> ...]
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tfmod_search_lib import (  # noqa: E402 -- sys.path must be set up first
    BM25Okapi,
    _get_encoder,
    compute_kw_idf,
    initialize_nltk,
    load_index,
    parse_markdown_file,
    save_index,
    tokenize,
)


def reencode(index_path: str, changed_paths: list[str], logger: logging.Logger) -> None:
    """Re-encode only the docs whose path matches one of `changed_paths`.

    Unchanged docs' `doc_vectors` rows are left byte-identical: this function
    never re-encodes or overwrites a row it did not match.
    """
    # tokenize() needs the punkt_tab resource; prepend the project nltk_data to
    # NLTK's search path exactly as the CLI/build path does, so this runs
    # standalone (not only under a pytest session that already initialized it).
    initialize_nltk()
    index = load_index(index_path, logger)

    changed_resolved = {Path(p).resolve() for p in changed_paths}
    changed_names = {Path(p).name for p in changed_paths}

    matched_indices = []
    for i, doc in enumerate(index.docs):
        doc_path = Path(doc.path)
        if doc_path.resolve() in changed_resolved or doc_path.name in changed_names:
            matched_indices.append(i)

    if not matched_indices:
        logger.info("reencode: no docs matched the given changed paths; nothing to re-encode")
    else:
        texts = []
        for i in matched_indices:
            doc_path = Path(index.docs[i].path)
            rec = parse_markdown_file(doc_path, logger)
            if rec is None:
                raise RuntimeError(f"reencode: failed to re-parse {doc_path}")
            index.docs[i] = rec
            index.module_names[i] = rec.module_name
            index.doc_kw_sets[i] = set(rec.keywords)
            index.bm25_corpus_tokens[i] = tokenize(rec.text)
            texts.append(rec.text)

        encoder = _get_encoder(index.model_name, logger)
        new_vectors = encoder.encode(texts)
        for row, i in enumerate(matched_indices):
            index.doc_vectors[i] = new_vectors[row]

        logger.info(
            f"reencode: re-encoded {len(matched_indices)} doc(s): {[index.docs[i].path for i in matched_indices]}"
        )

    index.bm25 = BM25Okapi(index.bm25_corpus_tokens)
    index.kw_idf = compute_kw_idf(index.docs)

    save_index(index, index_path, logger)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    index_path = sys.argv[1]
    changed_paths = sys.argv[2:]
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("reencode_changed_docs")
    reencode(index_path, changed_paths, logger)


if __name__ == "__main__":
    main()
