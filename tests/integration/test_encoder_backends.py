"""Encoder backend selection and the ONNX encoder.

ONNX asset-dependent tests are gated on TFMODSEARCH_ONNX_TEST_ASSETS pointing
at an exported e5-small-v2 ONNX dir (model.onnx + tokenizer.json); they skip
when the var is unset (e.g. in CI, which has no assets).
"""

import logging
import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tfmod_onnx_encoder import OnnxEncoder, resolve_onnx_model_dir

import tfmod_search_lib as lib

ASSETS = os.environ.get("TFMODSEARCH_ONNX_TEST_ASSETS", "")
needs_assets = pytest.mark.skipif(
    not (ASSETS and (Path(ASSETS) / "model.onnx").is_file()),
    reason="TFMODSEARCH_ONNX_TEST_ASSETS not set or has no model.onnx",
)
logger = logging.getLogger("test-encoder")


def test_resolve_backend_default_is_torch_when_st_available():
    assert lib._resolve_backend({}) == "torch"


def test_resolve_backend_explicit_values():
    assert lib._resolve_backend({"TFMODSEARCH_EMBED_BACKEND": "torch"}) == "torch"
    assert lib._resolve_backend({"TFMODSEARCH_EMBED_BACKEND": "onnx"}) == "onnx"
    assert lib._resolve_backend({"TFMODSEARCH_EMBED_BACKEND": " ONNX "}) == "onnx"


def test_resolve_backend_rejects_unknown():
    with pytest.raises(ValueError):
        lib._resolve_backend({"TFMODSEARCH_EMBED_BACKEND": "tensorflow"})


def test_resolve_onnx_model_dir_env_and_missing(tmp_path):
    assert resolve_onnx_model_dir(project_root=tmp_path) is None
    d = tmp_path / "onnx" / "e5-small-v2"
    d.mkdir(parents=True)
    (d / "model.onnx").write_bytes(b"x")
    assert resolve_onnx_model_dir(project_root=tmp_path) == d


def test_lib_module_has_no_toplevel_sentence_transformers_import():
    import ast

    tree = ast.parse(Path(lib.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import | ast.ImportFrom) and node.col_offset == 0:
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module]
            assert "sentence_transformers" not in names, "ST import must be lazy"


@needs_assets
def test_onnx_encoder_shape_dtype_norm():
    enc = OnnxEncoder(Path(ASSETS))
    vecs = enc.encode(["s3 bucket", "kubernetes cluster"])
    assert vecs.shape[0] == 2 and vecs.dtype == np.float32
    np.testing.assert_allclose(np.linalg.norm(vecs, axis=1), 1.0, rtol=1e-5)


@needs_assets
def test_onnx_encoder_prompt_prepends():
    enc = OnnxEncoder(Path(ASSETS))
    with_prompt = enc.encode(["vpc"], prompt="query: ")[0]
    manual = enc.encode(["query: vpc"])[0]
    np.testing.assert_allclose(with_prompt, manual, atol=1e-6)


@needs_assets
def test_onnx_parity_with_sentence_transformers():
    queries = [
        "vpc",
        "s3 bucket with encryption",
        "kubernetes cluster",
        "serverless function execution",
        "managed relational database",
        "content delivery network",
        "iam roles and policies",
        "dns hosted zone",
        "message queue",
        "web application firewall",
    ]
    st_vecs = (
        lib._get_sentence_transformer(lib.DEFAULT_MODEL_NAME, logger)
        .encode(queries, convert_to_numpy=True, normalize_embeddings=True)
        .astype(np.float32)
    )
    onnx_vecs = OnnxEncoder(Path(ASSETS)).encode(queries)
    cos = (st_vecs * onnx_vecs).sum(axis=1)
    assert cos.min() >= 0.9999, f"parity broken: min cosine {cos.min()}"


@needs_assets
def test_compute_scores_with_onnx_backend(monkeypatch):
    monkeypatch.setenv("TFMODSEARCH_EMBED_BACKEND", "onnx")
    monkeypatch.setenv("TFMODSEARCH_ONNX_MODEL_DIR", ASSETS)
    lib._MODEL_CACHE.clear()
    index = lib.load_index(str(lib.get_default_index_path()), logger)
    results = lib.compute_scores(index, "s3 bucket with encryption and versioning", top_k=3, logger=logger)
    assert results
    top_score, top_idx = results[0]
    assert index.docs[top_idx].module_name == "s3-bucket"
    lib._MODEL_CACHE.clear()
