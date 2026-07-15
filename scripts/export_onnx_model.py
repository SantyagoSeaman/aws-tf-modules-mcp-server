#!/usr/bin/env python3
"""Export intfloat/e5-small-v2 to ONNX for the tfmodsearch onnx backend.

Usage: python scripts/export_onnx_model.py <output_dir>

Requires optimum-onnx[onnxruntime] (plus torch) in the CURRENT environment --
these are export-time-only tools, deliberately not part of the package
metadata. The Dockerfile builder stage runs this; developers only need it when
regenerating assets. When sentence-transformers is also importable, a 5-query
parity check runs afterwards and fails the script below cosine 0.9999.
"""

import subprocess
import sys
from pathlib import Path

MODEL = "intfloat/e5-small-v2"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    subprocess.run(  # noqa: S603 -- fixed argv, no shell
        ["optimum-cli", "export", "onnx", "--model", MODEL, "--task", "feature-extraction", str(out)],  # noqa: S603, S607 -- fixed argv, optimum-cli resolved via PATH
        check=True,
    )
    if not ((out / "model.onnx").is_file() and (out / "tokenizer.json").is_file()):
        sys.exit("export produced no model.onnx/tokenizer.json")
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer

        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from tfmod_onnx_encoder import OnnxEncoder

        queries = ["vpc", "s3 bucket encryption", "kubernetes cluster", "serverless function", "dns zone"]
        ref = SentenceTransformer(MODEL).encode(queries, convert_to_numpy=True, normalize_embeddings=True)
        cos = (ref.astype(np.float32) * OnnxEncoder(out).encode(queries)).sum(axis=1)
        print(f"parity: min cosine {cos.min():.8f}")
        if cos.min() < 0.9999:
            sys.exit("ONNX export drifted from sentence-transformers")
    except ImportError:
        print("parity check skipped (sentence-transformers not installed)")


if __name__ == "__main__":
    main()
