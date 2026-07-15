"""ONNX encode backend for tfmodsearch: tokenizers + onnxruntime, no torch.

Replicates exactly what sentence-transformers does for intfloat/e5-small-v2
(Transformer -> attention-masked mean pooling -> L2 normalize), validated at
4e-07 max elementwise diff across the full golden query set. Dependencies come
from the optional extra `tfmodsearch[onnx]`.
"""

import os
from pathlib import Path

import numpy as np

DEFAULT_MAX_SEQ_LENGTH = 512


def resolve_onnx_model_dir(project_root: Path | None = None) -> Path | None:
    """Locate ONNX assets: env var first, then <project_root>/onnx/e5-small-v2.

    A SET but invalid TFMODSEARCH_ONNX_MODEL_DIR raises instead of returning
    None: silently falling through would mask the typo and produce an error
    telling the user to set the variable they already set.
    """
    env = os.environ.get("TFMODSEARCH_ONNX_MODEL_DIR", "").strip()
    if env:
        p = Path(env)
        for required in ("model.onnx", "tokenizer.json"):
            if not (p / required).is_file():
                raise ValueError(f"TFMODSEARCH_ONNX_MODEL_DIR is set to {p} but {p / required} does not exist")
        return p
    if project_root is not None:
        p = project_root / "onnx" / "e5-small-v2"
        if (p / "model.onnx").is_file() and (p / "tokenizer.json").is_file():
            return p
    return None


class OnnxEncoder:
    """Drop-in encode() replacement for the SentenceTransformer path."""

    def __init__(self, model_dir: Path, max_seq_length: int = DEFAULT_MAX_SEQ_LENGTH):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        self._tokenizer = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
        self._tokenizer.enable_truncation(max_length=max_seq_length)
        self._session = ort.InferenceSession(str(model_dir / "model.onnx"), providers=["CPUExecutionProvider"])
        self._needs_token_type = any(i.name == "token_type_ids" for i in self._session.get_inputs())

    def encode(self, texts: list[str], prompt: str | None = None) -> np.ndarray:
        """Encode texts to (N, D) float32 L2-normalized vectors.

        One text per session run: the spike showed the loop already beats the
        torch batch path on CPU, and it sidesteps padding entirely.
        """
        if prompt:
            texts = [f"{prompt}{t}" for t in texts]
        out = []
        for text in texts:
            enc = self._tokenizer.encode(text)
            ids = np.array([enc.ids], dtype=np.int64)
            mask = np.array([enc.attention_mask], dtype=np.int64)
            feeds = {"input_ids": ids, "attention_mask": mask}
            if self._needs_token_type:
                feeds["token_type_ids"] = np.zeros_like(ids)
            hidden = self._session.run(None, feeds)[0]
            m = mask[..., None].astype(np.float32)
            vec = (hidden * m).sum(axis=1) / m.sum(axis=1)
            vec = vec / np.linalg.norm(vec, axis=1, keepdims=True)
            out.append(vec[0].astype(np.float32))
        return np.array(out, dtype=np.float32)
