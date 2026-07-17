"""Drift-safe append helper: add NEW module docs to an existing index.

Rebuilding the whole index (`build_index`) re-encodes EVERY document. Even with
a deterministic model, re-encoding existing docs produces tiny float differences
across library/hardware versions that flip knife-edge rankings and break the
frozen golden retrieval set. This script instead:

- loads the existing pickled `SearchIndex`,
- encodes ONLY the new docs (existing `doc_vectors` rows are reused byte-for-byte
  and re-stacked, never re-encoded),
- reuses the existing per-doc BM25 token lists for old docs and tokenizes only
  the new ones,
- rebuilds the corpus-global structures that MUST change when the corpus grows
  (BM25Okapi over the full token set, and the keyword IDF table) — this is the
  unavoidable "aggregate drift" that the golden-set gate must re-verify after an
  append,
- appends the new docs at the end (search scores every doc independently, so doc
  order does not affect results) and saves back in place.

Companion to `reencode_changed_docs.py` (which refreshes docs already in the
index); this one ADDS docs that are not yet present.

Usage:
    python scripts/append_new_docs.py <index_path> <new_doc_path> [<new_doc_path> ...]
"""

import logging
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tfmod_search_lib import (  # noqa: E402 -- sys.path set up above
    BM25Okapi,
    SearchIndex,
    _get_encoder,
    compute_kw_idf,
    initialize_nltk,
    load_index,
    parse_markdown_file,
    save_index,
    tokenize,
)


def append_docs(index_path: str, new_paths: list[str], logger: logging.Logger) -> None:
    """Append the docs at `new_paths` to the index at `index_path`, drift-safely.

    Existing docs' embedding rows and BM25 token lists are preserved verbatim;
    only the new docs are encoded/tokenized. BM25 and keyword IDF are rebuilt
    over the full corpus (they are corpus-global). A path already present in the
    index (matched by file name) is skipped, so re-running is idempotent.
    """
    initialize_nltk()
    index = load_index(index_path, logger)

    existing_names = {Path(d.path).name for d in index.docs}
    new_recs = []
    for p in new_paths:
        rec = parse_markdown_file(Path(p), logger)
        if rec is None:
            raise RuntimeError(f"append: failed to parse {p}")
        if Path(rec.path).name in existing_names:
            logger.warning(f"append: {rec.path} already in index; skipping")
            continue
        new_recs.append(rec)

    if not new_recs:
        logger.info("append: no new docs to add; nothing changed")
        return

    logger.info(f"append: encoding {len(new_recs)} new doc(s) (existing rows reused byte-for-byte)")
    encoder = _get_encoder(index.model_name, logger)
    new_vectors = encoder.encode([r.text for r in new_recs]).astype(np.float32, copy=False)

    all_docs = list(index.docs) + new_recs
    # old token lists verbatim; tokenize only the new docs
    corpus_tokens = list(index.bm25_corpus_tokens) + [tokenize(r.text) for r in new_recs]
    doc_vectors = np.vstack([index.doc_vectors, new_vectors]).astype(np.float32, copy=False)

    new_index = SearchIndex(
        model_name=index.model_name,
        docs=all_docs,
        bm25_corpus_tokens=corpus_tokens,
        bm25=BM25Okapi(corpus_tokens),
        doc_vectors=doc_vectors,
        kw_idf=compute_kw_idf(all_docs),
        module_names=[d.module_name for d in all_docs],
        doc_kw_sets=[set(d.keywords) for d in all_docs],
    )
    logger.info(f"append: corpus grew {len(index.docs)} -> {len(all_docs)} docs; saving")
    save_index(new_index, index_path, logger)


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("append_new_docs")
    append_docs(sys.argv[1], sys.argv[2:], logger)


if __name__ == "__main__":
    main()
