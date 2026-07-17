"""Tests for the drift-safe append helper (scripts/append_new_docs.py).

The load-bearing guarantee: appending a NEW module doc must leave every EXISTING
doc's embedding row byte-for-byte identical (only the new doc is encoded), while
growing the corpus and rebuilding the corpus-global BM25 / keyword-IDF tables.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

from append_new_docs import append_docs  # noqa: E402

from tfmod_search_lib import build_index, initialize_nltk, load_index, save_index  # noqa: E402

logger = logging.getLogger("test_append")


def _doc(name: str, keywords: str, body: str) -> str:
    return (
        f"---\nmodule_name: terraform-aws-{name}\nkeywords: [{keywords}]\n---\n"
        f"# Terraform AWS {name} Module\n\n"
        f"## Module Information\n\n"
        f"- **Module Name**: `{name}`\n"
        f"- **Module ID**: `cloudposse/{name}/aws`\n"
        f"- **Source**: `cloudposse/{name}/aws`\n"
        f"- **Latest Version**: `1.0.0`\n\n"
        f"## Description\n\n{body}\n"
    )


@pytest.fixture
def mini_index(tmp_path):
    initialize_nltk()
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "alpha.md").write_text(_doc("alpha", "alpha, storage, bucket", "Object storage for alpha things."))
    (docs / "beta.md").write_text(_doc("beta", "beta, network, vpc", "Virtual network for beta things."))
    idx_path = tmp_path / "mini.pkl"
    index = build_index(str(docs), logger=logger)
    save_index(index, str(idx_path), logger)
    return tmp_path, docs, str(idx_path)


def test_append_grows_corpus_and_keeps_existing_vectors_byte_identical(mini_index):
    tmp_path, docs, idx_path = mini_index
    before = load_index(idx_path, logger)
    n_before = len(before.docs)
    old_vectors = before.doc_vectors.copy()

    new = docs / "gamma.md"
    new.write_text(_doc("gamma", "gamma, email, ses", "Managed email sending for gamma things."))
    append_docs(idx_path, [str(new)], logger)

    after = load_index(idx_path, logger)
    # corpus grew by exactly one
    assert len(after.docs) == n_before + 1
    assert after.doc_vectors.shape[0] == old_vectors.shape[0] + 1
    # THE guarantee: every pre-existing embedding row is byte-for-byte identical
    assert np.array_equal(after.doc_vectors[:n_before], old_vectors), "existing embeddings drifted on append"
    # the new module is present and searchable structures updated
    assert "gamma" in after.module_names
    assert after.bm25_corpus_tokens[-1], "new doc has no BM25 tokens"
    assert any("email" in kw or "ses" in kw for kw in after.kw_idf), "new keywords not in IDF table"
    assert len(after.doc_kw_sets) == n_before + 1


def test_append_is_idempotent(mini_index):
    tmp_path, docs, idx_path = mini_index
    new = docs / "gamma.md"
    new.write_text(_doc("gamma", "gamma, email, ses", "Managed email sending for gamma things."))
    append_docs(idx_path, [str(new)], logger)
    once = load_index(idx_path, logger)
    append_docs(idx_path, [str(new)], logger)  # same doc again
    twice = load_index(idx_path, logger)
    assert len(twice.docs) == len(once.docs), "re-appending an existing doc must be a no-op"
    assert np.array_equal(twice.doc_vectors, once.doc_vectors)
