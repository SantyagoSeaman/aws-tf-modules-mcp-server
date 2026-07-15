import logging
import pickle
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import reencode_changed_docs as rc  # noqa: E402 -- sys.path must be set up first

from tfmod_search_lib import load_index  # noqa: E402 -- sys.path must be set up first

ROOT = Path(__file__).resolve().parents[2]
REAL_INDEX = str(ROOT / "model/tfmod_e5_small_index.pkl")


def _copy_index(tmp_path: Path) -> str:
    dest = tmp_path / "index.pkl"
    shutil.copy(REAL_INDEX, dest)
    return str(dest)


def test_reencode_noop_leaves_vectors_byte_identical(tmp_path):
    log = logging.getLogger("t")
    with open(REAL_INDEX, "rb") as f:
        before = pickle.load(f)  # noqa: S301 -- our own trusted local artifact

    copy_path = _copy_index(tmp_path)
    rc.reencode(copy_path, [], log)
    after = load_index(copy_path, log)

    assert np.array_equal(before.doc_vectors, after.doc_vectors), "no-op reencode must not perturb any vector"
    assert [d.path for d in before.docs] == [d.path for d in after.docs]


def test_reencode_real_file_only_changes_target_row(tmp_path):
    log = logging.getLogger("t")
    with open(REAL_INDEX, "rb") as f:
        before = pickle.load(f)  # noqa: S301 -- our own trusted local artifact

    target_i = next(i for i, d in enumerate(before.docs) if d.module_name == "vpc")
    target_path = before.docs[target_i].path

    copy_path = _copy_index(tmp_path)
    rc.reencode(copy_path, [target_path], log)
    after = load_index(copy_path, log)

    for i in range(len(before.docs)):
        if i == target_i:
            continue
        assert np.array_equal(before.doc_vectors[i], after.doc_vectors[i]), f"row {i} should be untouched"

    assert np.allclose(
        before.doc_vectors[target_i], after.doc_vectors[target_i], atol=1e-5
    ), "re-encoding the unchanged real file should reproduce (approximately) the same vector"

    # index-wide structures were rebuilt but must remain internally consistent
    assert len(after.bm25_corpus_tokens) == len(after.docs)
    assert after.doc_vectors.shape == before.doc_vectors.shape

    # the real index on disk must remain untouched by this test
    with open(REAL_INDEX, "rb") as f:
        real_after = pickle.load(f)  # noqa: S301 -- our own trusted local artifact
    assert np.array_equal(before.doc_vectors, real_after.doc_vectors)
