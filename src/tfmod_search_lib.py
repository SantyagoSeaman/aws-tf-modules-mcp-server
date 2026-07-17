"""
Reusable library for hybrid search over Markdown docs describing Terraform modules.
CPU-only, sub-second queries for hundreds of docs.

Default embedding model: intfloat/e5-small-v2

Exports:
- initialize_nltk() -> None
- setup_logging(log_filename, log_level) -> Logger
- switch_log_file(new_log_filename) -> None
- build_index(docs_dir, model_name) -> SearchIndex
- save_index(index, path), load_index(path) -> SearchIndex
- compute_scores(index, query, ..., query_instruction) -> List[(score, idx)]
- compute_scores_detailed(index, query, ..., query_instruction) -> List[ScoredHit]
- ScoredHit: namedtuple(score, doc_index, exact_hit, kw_overlap, sem_sim)
- extract_description(text, max_length) -> str
- get_default_index_path() -> Path
- resolve_index_path(index_path) -> Path
- DEFAULT_MODEL_NAME: str (intfloat/e5-small-v2)
- BGE_QUERY_INSTRUCTION: str (optional query prefix for BGE models)
"""

import logging
import math
import os
import pickle
import re
import sys
import threading
from collections import defaultdict, namedtuple
from collections.abc import Mapping
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import nltk
import numpy as np
from nltk.tokenize import word_tokenize
from rank_bm25 import BM25Okapi


# Project root detection: handles both development (src/) and installed package layouts
def _detect_project_root() -> Path:
    """Detect project root for both development and installed package layouts."""
    # When installed as package: tfmod_search_lib.py is at package root
    # When in development: tfmod_search_lib.py is in src/ subdirectory
    parent = Path(__file__).parent.resolve()
    parent_parent = parent.parent.resolve()

    # Check if model/ exists at parent level (installed package)
    if (parent / "model").is_dir():
        return parent
    # Check if model/ exists at parent.parent level (development)
    if (parent_parent / "model").is_dir():
        return parent_parent
    # Fallback to parent.parent (original behavior)
    return parent_parent


_PROJECT_ROOT = _detect_project_root()
_NLTK_DATA_DIR = _PROJECT_ROOT / "nltk_data"

# Model cache to avoid reloading the embedding model on every query.
# Values are SentenceTransformer instances (torch backend) or Encoder-protocol
# instances (torch/onnx via _get_encoder); typed loosely so this module imports
# cleanly without sentence_transformers installed.
_MODEL_CACHE: dict[str, Any] = {}

# Serializes model construction AND SentenceTransformer.encode(), neither of
# which is guaranteed thread-safe. Only matters for the HTTP transport, where
# tool calls run concurrently; stdio never contends. Query encode is ~10 ms,
# so contention is negligible.
_MODEL_LOCK = threading.Lock()

# Default embedding model
DEFAULT_MODEL_NAME = "intfloat/e5-small-v2"

# Optional query instruction for BGE models (improves short query retrieval)
# BGE v1.5 works well without instruction, but this can provide slight improvement
BGE_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


def _get_sentence_transformer(model_name: str, logger: logging.Logger) -> Any:
    """
    Get or load a SentenceTransformer model with caching.

    This function maintains a module-level cache of loaded models to avoid:
    1. Re-downloading models from HuggingFace on every call
    2. Re-loading models from disk cache on every call
    3. HTTP validation requests on every instantiation

    Args:
        model_name: Name of the SentenceTransformer model (e.g., "thenlper/gte-small")
        logger: Logger for logging cache hits/misses

    Returns:
        Cached or newly loaded SentenceTransformer instance

    Notes:
        - Models are cached in memory for the lifetime of the process
        - Thread-safe for read access (models are immutable after loading)
        - First call downloads/loads model, subsequent calls use cache

    Example:
        >>> model = _get_sentence_transformer("thenlper/gte-small", logger)
        >>> # Subsequent calls return the same instance instantly
        >>> model2 = _get_sentence_transformer("thenlper/gte-small", logger)
        >>> assert model is model2
    """
    with _MODEL_LOCK:
        if model_name not in _MODEL_CACHE:
            from sentence_transformers import SentenceTransformer  # lazy: keeps this module importable without torch

            logger.debug(f"Loading SentenceTransformer model: {model_name} (not in cache)")
            _MODEL_CACHE[model_name] = SentenceTransformer(model_name, device="cpu")
            logger.debug(f"Model {model_name} loaded and cached")
        else:
            logger.debug(f"Using cached SentenceTransformer model: {model_name}")

        return _MODEL_CACHE[model_name]


def _resolve_backend(env: Mapping[str, str] | None = None) -> str:
    """Pick the embedding backend: TFMODSEARCH_EMBED_BACKEND = auto|torch|onnx."""
    if env is None:
        env = os.environ
    backend = env.get("TFMODSEARCH_EMBED_BACKEND", "auto").strip().lower() or "auto"
    if backend not in ("auto", "torch", "onnx"):
        raise ValueError(f"invalid TFMODSEARCH_EMBED_BACKEND {backend!r}: choose auto, torch, or onnx")
    if backend != "auto":
        return backend
    try:
        import sentence_transformers  # noqa: F401

        return "torch"
    except ImportError:
        pass
    from tfmod_onnx_encoder import resolve_onnx_model_dir

    if resolve_onnx_model_dir(project_root=_PROJECT_ROOT) is not None:
        return "onnx"
    raise RuntimeError(
        "No embedding backend available: install sentence-transformers (torch backend) "
        "or install tfmodsearch[onnx] and provide ONNX assets via TFMODSEARCH_ONNX_MODEL_DIR"
    )


class _TorchEncoder:
    """Adapter giving SentenceTransformer the minimal Encoder interface."""

    def __init__(self, model: Any):
        self._model = model

    def encode(self, texts: list[str], prompt: str | None = None) -> np.ndarray:
        return self._model.encode(
            texts, prompt=prompt, batch_size=64, convert_to_numpy=True, normalize_embeddings=True
        ).astype(np.float32, copy=False)


def _get_encoder(model_name: str, logger: logging.Logger) -> Any:
    """Get a cached Encoder (torch or onnx, per TFMODSEARCH_EMBED_BACKEND) for model_name."""
    backend = _resolve_backend()
    cache_key = f"{backend}:{model_name}"
    if backend == "torch":
        if cache_key not in _MODEL_CACHE:
            _MODEL_CACHE[cache_key] = _TorchEncoder(_get_sentence_transformer(model_name, logger))
        return _MODEL_CACHE[cache_key]
    with _MODEL_LOCK:
        if cache_key not in _MODEL_CACHE:
            from tfmod_onnx_encoder import OnnxEncoder, resolve_onnx_model_dir

            model_dir = resolve_onnx_model_dir(project_root=_PROJECT_ROOT)
            if model_dir is None:
                raise RuntimeError(
                    "TFMODSEARCH_EMBED_BACKEND=onnx but no ONNX assets found: set "
                    "TFMODSEARCH_ONNX_MODEL_DIR to a dir containing model.onnx + tokenizer.json"
                )
            logger.info(f"Loading ONNX encoder from {model_dir}")
            _MODEL_CACHE[cache_key] = OnnxEncoder(model_dir)
        return _MODEL_CACHE[cache_key]


def initialize_nltk() -> None:
    """
    Initialize NLTK data directory and download required resources.

    This function:
    1. Creates the project-local nltk_data directory if it doesn't exist
    2. Adds the directory to NLTK's search path (prepended for priority)
    3. Downloads required NLTK resources (punkt_tab tokenizer) on first run

    This should be called once at application startup before any NLTK
    operations are performed (e.g., tokenization).

    Returns:
        None

    Notes:
        - NLTK data is stored in <project_root>/nltk_data/
        - Downloads are performed quietly (no progress output)
        - Safe to call multiple times (idempotent)
        - Required for word_tokenize() function to work

    Example:
        >>> from tfmod_search_lib import initialize_nltk
        >>> initialize_nltk()  # Call once at startup
        >>> # Now NLTK tokenization will work
    """
    # Create NLTK data directory
    _NLTK_DATA_DIR.mkdir(exist_ok=True)

    # Add to NLTK search path (prepend to ensure it's checked first)
    if str(_NLTK_DATA_DIR) not in nltk.data.path:
        nltk.data.path.insert(0, str(_NLTK_DATA_DIR))

    # Download required NLTK data on first run
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", download_dir=str(_NLTK_DATA_DIR), quiet=True)


# -----------------------------
# Data structures
# -----------------------------
@dataclass
class DocRecord:
    path: str
    module_name: str  # normalized lower-case
    keywords: list[str]  # lower-case, unique
    text: str
    module_id: str = ""  # "namespace/name/provider", verbatim as parsed (old pickles default to "")
    latest_version: str = ""  # verbatim as parsed (old pickles default to "")


@dataclass
class ModuleInfo:
    module_name: str
    keywords: list[str]
    module_id: str
    latest_version: str


@dataclass
class SearchIndex:
    model_name: str
    docs: list[DocRecord]
    bm25_corpus_tokens: list[list[str]]
    bm25: BM25Okapi
    doc_vectors: np.ndarray  # (N, D), L2-normalized float32
    kw_idf: dict[str, float]
    module_names: list[str]
    doc_kw_sets: list[set]


class ModuleDocumentParser:
    """
    Parser for Terraform module documentation in Markdown format.

    Extracts module metadata (name, keywords) from structured Markdown sections
    using regex-based text parsing. Supports two strategies:
    1. Parse from "## Module Information" section (preferred)
    2. Search for "keywords:" anywhere in document body (fallback)
    """

    def __init__(self, logger: logging.Logger):
        """Initialize parser with logger."""
        self.logger = logger

    def parse(self, text: str, filename: str) -> tuple[str, list[str], str]:
        """
        Parse module documentation to extract metadata.

        Args:
            text: Full text content of the Markdown file
            filename: Name of the file being parsed (for logging)

        Returns:
            Tuple of (module_name, keywords, body_text)
            - module_name: Extracted module name (empty string if not found)
            - keywords: List of extracted keywords (empty list if not found)
            - body_text: Document body text (full text by default)
        """
        module_name = ""
        keywords: list[str] = []
        body = text
        parse_strategy = None

        # Strategy 1: Parse from "## Module Information" section
        module_info = self._parse_module_information_section(text)
        if module_info:
            module_name, keywords, parse_strategy = module_info

        # Strategy 2: Fallback - search for "keywords:" anywhere in body
        if not keywords:
            keywords_fallback = self._parse_inline_keywords(body)
            if keywords_fallback:
                keywords = keywords_fallback
                if not parse_strategy:
                    parse_strategy = "inline keywords search"

        # Log parsing result
        if module_name or keywords:
            self.logger.debug(
                f"Parsed {filename}: module={module_name}, keywords={len(keywords)}, strategy={parse_strategy}"
            )
        else:
            self.logger.warning(
                f"File {filename} missing module_name or keywords (name={module_name}, kw_count={len(keywords)})"
            )

        return module_name, keywords, body

    def _find_module_info_section(self, text: str) -> str | None:
        """
        Locate the raw text of the "## Module Information" section.

        Args:
            text: Full document text

        Returns:
            Section text (everything between the heading and the next "##" heading
            or end of document), or None if the section is not present.
        """
        module_info_match = re.search(r"## Module Information\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL | re.IGNORECASE)
        return module_info_match.group(1) if module_info_match else None

    def _extract_bullet(self, section: str, key: str) -> str | None:
        """
        Extract the value of a "- **Key**: value" bullet (with or without backticks).

        Args:
            section: Text to search (typically a "## Module Information" section)
            key: Bullet label to match, e.g. "Module Name" or "Module ID"

        Returns:
            Stripped bullet value, or None if the bullet is not present.
        """
        match = re.search(
            rf"^\s*-\s*\*\*{re.escape(key)}\*\*:\s*`?([^`\n]+?)`?\s*$", section, re.IGNORECASE | re.MULTILINE
        )
        return match.group(1).strip() if match else None

    def _parse_module_information_section(self, text: str) -> tuple[str, list[str], str] | None:
        """
        Parse module name and keywords from "## Module Information" section.

        Looks for:
        - **Module Name**: value
        - **Keywords**: comma, separated, values

        Args:
            text: Full document text

        Returns:
            Tuple of (module_name, keywords, strategy_name) or None if section not found
        """
        # Find the Module Information section
        module_info_section = self._find_module_info_section(text)

        if module_info_section is None:
            return None

        # Extract Module Name: look for "- **Module Name**: VALUE" (with or without backticks)
        module_name = self._extract_bullet(module_info_section, "Module Name") or ""

        # Extract Keywords: look for "- **Keywords**: comma, separated, values"
        keywords: list[str] = []
        kw_match = re.search(r"^\s*-\s*\*\*Keywords\*\*:\s*(.+?)$", module_info_section, re.IGNORECASE | re.MULTILINE)
        if kw_match:
            kw_text = kw_match.group(1).strip()
            # Split by commas
            parts = kw_text.split(",")
            keywords = [k.strip() for k in parts if k.strip()]

        if module_name or keywords:
            return module_name, keywords, "Module Information section"

        return None

    def parse_module_info(self, text: str) -> ModuleInfo:
        """
        Parse module_name, keywords, module_id, and latest_version from the
        "## Module Information" section.

        `module_id` is read from an explicit "**Module ID**" bullet; if that bullet
        is absent, it falls back to the first root "**Source**" bullet with any
        submodule suffix (the part from "//" onward) stripped.

        Args:
            text: Full document text

        Returns:
            ModuleInfo with best-effort extracted fields (empty string/list for any
            field that could not be found).
        """
        module_name = ""
        keywords: list[str] = []
        module_id = ""
        latest_version = ""

        module_info_section = self._find_module_info_section(text)
        if module_info_section is not None:
            parsed = self._parse_module_information_section(text)
            if parsed:
                module_name, keywords, _ = parsed

            module_id = self._extract_bullet(module_info_section, "Module ID") or ""
            if not module_id:
                source = self._extract_bullet(module_info_section, "Source")
                if source:
                    module_id = source.split("//")[0]

            latest_version = self._extract_bullet(module_info_section, "Latest Version") or ""

        return ModuleInfo(
            module_name=module_name, keywords=keywords, module_id=module_id, latest_version=latest_version
        )

    def _parse_inline_keywords(self, text: str) -> list[str] | None:
        """
        Search for "keywords:" anywhere in document and extract values.

        Args:
            text: Document text to search

        Returns:
            List of keywords or None if not found
        """
        km = re.search(r"(?im)^keywords?\s*:\s*(.+)$", text)
        if km:
            parts = re.split(r"[,|;/]+", km.group(1))
            keywords = [k.strip() for k in parts if k.strip()]
            return keywords
        return None


# -----------------------------
# Utils
# -----------------------------
def normalize_modname(name: str) -> str:
    """
    Normalize a Terraform module name to a canonical lowercase format.

    Performs the following transformations:
    1. Converts to lowercase
    2. Removes 'terraform-aws-' prefix (replaces with 'aws-')
    3. Removes 'terraform-' prefix
    4. Replaces underscores with hyphens
    5. Replaces multiple spaces with single hyphen

    Args:
        name: Raw module name string (e.g., "Terraform AWS VPC", "terraform-aws-vpc")

    Returns:
        Normalized module name in lowercase with hyphens (e.g., "aws-vpc", "vpc")

    Examples:
        >>> normalize_modname("Terraform AWS VPC")
        'aws-vpc'
        >>> normalize_modname("terraform-aws-s3-bucket")
        'aws-s3-bucket'
        >>> normalize_modname("my_custom_module")
        'my-custom-module'
    """
    n = name.lower().strip()
    n = n.replace("terraform-aws-", "")
    n = n.replace("terraform-", "")
    n = n.replace("Terraform AWS ", "")
    n = n.replace("_", "-")
    n = re.sub(r"\s+", "-", n)
    return n


def _punctuation_to_hyphen_boundaries(s: str) -> str:
    """Map every run of non-alphanumeric characters to a single hyphen and
    strip leading/trailing hyphens, so punctuation (commas, periods, colons,
    ...) becomes a hyphen boundary instead of defeating one."""
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def exact_name_match(module_name: str, normalized_query: str) -> bool:
    """
    Whether a normalized module name appears in the normalized query on
    hyphen boundaries.

    The exact-name scoring component must fire for "vpc" inside
    "vpc-with-private-subnets" (the user named the module) but not for
    "rds" inside "manage-dns-records-zones" (the name is an accidental
    substring of an unrelated word). normalize_modname joins phrases with
    hyphens, so wrapping both sides in sentinels reduces the check to a
    boundary-safe containment test.

    Punctuation tolerance: before the boundary check, every non-alphanumeric
    character on BOTH sides (module_name and normalized_query) is mapped to
    a hyphen and consecutive hyphens are collapsed, so a stray comma,
    period, or colon in either string ("vpc," / "vpc." / "eks: karpenter
    autoscaling") no longer defeats the hyphen-boundary test.
    """
    if not module_name:
        return False
    name = _punctuation_to_hyphen_boundaries(module_name)
    query = _punctuation_to_hyphen_boundaries(normalized_query)
    if not name:
        return False
    if name == query:
        return True
    return f"-{name}-" in f"-{query}-"


def tokenize(text: str) -> list[str]:
    """
    Tokenize text into lowercase words using NLTK's word_tokenize.

    Uses NLTK's punkt tokenizer to split text into individual words,
    then converts all tokens to lowercase for case-insensitive matching.

    Args:
        text: Input text to tokenize

    Returns:
        List of lowercase word tokens

    Examples:
        >>> tokenize("S3 bucket with KMS encryption")
        ['s3', 'bucket', 'with', 'kms', 'encryption']
    """
    return word_tokenize(text.lower())


def minmax(arr: np.ndarray) -> np.ndarray:
    """
    Min-max normalize an array to the range [0, 1].

    Scales values linearly so that the minimum becomes 0 and maximum becomes 1.
    If all values are equal or array is empty, returns zeros.

    Args:
        arr: NumPy array to normalize

    Returns:
        Normalized array with values in [0, 1] range

    Notes:
        - Returns zeros array if input is empty
        - Returns zeros array if all values are equal (max == min)
        - Formula: (x - min) / (max - min)
    """
    if arr.size == 0:
        return arr
    mn, mx = float(np.min(arr)), float(np.max(arr))
    if mx <= mn:
        return np.zeros_like(arr)
    return (arr - mn) / (mx - mn)


def cosine_sim_matrix(vec: np.ndarray, mat: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between a vector and multiple vectors (matrix).

    Assumes both vec and mat are already L2-normalized (unit vectors),
    so cosine similarity reduces to dot product.

    Args:
        vec: Query vector of shape (D,), L2-normalized
        mat: Document matrix of shape (N, D), L2-normalized

    Returns:
        Array of shape (N,) containing cosine similarities in range [-1, 1]

    Notes:
        - Both inputs must be L2-normalized beforehand
        - Result is mat @ vec, which is efficient dot product computation
        - Values range from -1 (opposite) to 1 (identical)
    """
    return mat @ vec  # both normalized


def _strip_yaml_frontmatter(text: str) -> str:
    """Drop a leading YAML front-matter block (``---`` ... ``---``) if present.

    Docs may open with a YAML front-matter block (``module_name`` /
    ``keywords``). ``extract_description`` treats the ``---`` delimiters as
    horizontal rules and skips them, but the block's key/value lines are not
    headers or rules, so they leaked verbatim into the search-result
    description. Strip the whole block first (opening ``---`` on the first
    non-empty line through the matching closing ``---``/``...``). No-op when the
    text does not start with a front-matter fence.
    """
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return text
    lines = stripped.splitlines()
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return "\n".join(lines[i + 1 :])
    # No closing fence -> not a well-formed block, leave the text untouched.
    return text


def extract_description(text: str, max_length: int = 200) -> str:
    """
    Extract a meaningful description from document text.

    Looks for the first paragraph or content section after any headers.
    Skips Markdown headers, horizontal rules, and empty lines to find
    the first meaningful content.

    Args:
        text: Document text (may include Markdown formatting)
        max_length: Maximum length of description in characters (default: 200)

    Returns:
        Extracted description string, truncated at word boundary if needed

    Notes:
        - Returns empty string if no content found
        - Skips lines starting with '#' (headers)
        - Skips horizontal rules (---, ***, ___)
        - Truncates at word boundaries with '...' suffix if needed

    Examples:
        >>> text = "# Title\\n\\nThis is a description.\\n\\n## Section\\nMore text."
        >>> extract_description(text, 50)
        'This is a description.'
    """
    if not text:
        return ""

    text = _strip_yaml_frontmatter(text)

    # Remove Markdown headers and extract first paragraph
    lines = text.strip().splitlines()
    description_lines = []

    for line in lines:
        stripped = line.strip()
        # Skip empty lines and markdown headers
        if not stripped or stripped.startswith("#"):
            continue
        # Skip horizontal rules
        if re.match(r"^[-*_]{3,}$", stripped):
            continue
        # Found content - add it
        description_lines.append(stripped)
        # Stop when we have enough content
        if len(" ".join(description_lines)) >= max_length:
            break

    # Join and truncate to max_length
    description = " ".join(description_lines)
    if len(description) > max_length:
        description = description[:max_length].rsplit(" ", 1)[0] + "..."

    return description


def extract_purpose(text: str, max_length: int = 200) -> str:
    """
    Extract the Purpose field from Module Information section.

    Looks for a line matching the pattern `- **Purpose**: <content>` in the
    document text and returns the purpose description.

    Args:
        text: Document text (may include Markdown formatting)
        max_length: Maximum length of purpose in characters (default: 200)

    Returns:
        Extracted purpose string, truncated at word boundary if needed.
        Returns empty string if no Purpose field found.

    Notes:
        - Returns empty string if no Purpose field found
        - Truncates at word boundaries with '...' suffix if needed

    Examples:
        >>> text = "## Module Information\\n- **Purpose**: Create VPC resources\\n"
        >>> extract_purpose(text, 50)
        'Create VPC resources'
    """
    if not text:
        return ""

    # Look for the Purpose field pattern
    purpose_pattern = r"^\s*-\s*\*\*Purpose\*\*:\s*(.+)$"
    match = re.search(purpose_pattern, text, re.MULTILINE)

    if not match:
        return ""

    purpose = match.group(1).strip()

    # Truncate to max_length if needed
    if len(purpose) > max_length:
        purpose = purpose[:max_length].rsplit(" ", 1)[0] + "..."

    return purpose


def get_default_index_path() -> Path:
    """
    Get the default index path relative to the project root.

    Returns the standard location for the search index file:
    `<project_root>/model/tfmod_e5_small_index.pkl`

    Returns:
        Path object pointing to the default index location

    Example:
        >>> default_path = get_default_index_path()
        >>> print(default_path)
        /path/to/project/model/tfmod_e5_small_index.pkl
    """
    return _PROJECT_ROOT / "model" / "tfmod_e5_small_index.pkl"


def resolve_index_path(index_path: str | None = None) -> Path:
    """
    Resolve index path, using default if not provided.

    If an index path is provided, it will be resolved to an absolute path.
    Relative paths are resolved relative to the current working directory.
    If no path is provided, returns the default index path.

    Args:
        index_path: Optional path to index file. Can be absolute or relative.
                   If None, uses the default path.

    Returns:
        Resolved Path object pointing to the index file

    Examples:
        >>> # Use default path
        >>> path = resolve_index_path()
        >>> print(path)
        /path/to/project/model/tfmod_e5_small_index.pkl

        >>> # Use custom absolute path
        >>> path = resolve_index_path("/custom/path/index.pkl")
        >>> print(path)
        /custom/path/index.pkl

        >>> # Use custom relative path (resolved from cwd)
        >>> path = resolve_index_path("my_index.pkl")
        >>> print(path)
        /current/working/directory/my_index.pkl
    """
    if index_path:
        path = Path(index_path)
        if not path.is_absolute():
            # Make relative paths relative to current directory
            return Path.cwd() / path
        return path
    else:
        # Use default path
        return get_default_index_path()


# -----------------------------
# Parse Markdown
# -----------------------------
def parse_markdown_file(p: Path, logger: logging.Logger) -> DocRecord | None:
    """
    Parse a Markdown file to extract module information.

    Uses ModuleDocumentParser with two strategies:
    1. Parse from "## Module Information" section (preferred)
    2. Search for "keywords:" anywhere in body (fallback)

    Args:
        p: Path to the markdown file
        logger: Logger instance for logging operations

    Returns:
        DocRecord with module metadata or None if parsing fails
    """
    logger.debug(f"Parsing markdown file: {p.name}")

    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"Failed to read file {p.name}: {e}")
        return None

    # Use ModuleDocumentParser to extract metadata
    parser = ModuleDocumentParser(logger)
    module_name, keywords, body = parser.parse(text, p.name)

    # Fallback to filename if module_name not found
    if not module_name:
        module_name = p.stem  # Use filename without extension
        logger.debug(f"Using filename as module name for {p.name}: {module_name}")

    # Normalize module name
    module_name = normalize_modname(module_name)

    # Normalize and deduplicate keywords
    keywords = sorted({k.lower() for k in keywords})

    # module_id/latest_version are stored verbatim as parsed (no normalization)
    module_info = parser.parse_module_info(text)

    # Validate we have content
    if not body.strip():
        logger.warning(f"File {p.name} has no content, skipping")
        return None

    return DocRecord(
        path=str(p),
        module_name=module_name,
        keywords=keywords,
        text=body,
        module_id=module_info.module_id,
        latest_version=module_info.latest_version,
    )


# -----------------------------
# Keyword IDF
# -----------------------------
def compute_kw_idf(docs: list[DocRecord]) -> dict[str, float]:
    """
    Compute Inverse Document Frequency (IDF) scores for all keywords.

    IDF measures how important a keyword is across the document collection.
    Keywords that appear in fewer documents get higher IDF scores, making
    them more valuable for distinguishing between documents.

    Uses BM25+ style IDF formula: log(1 + (N - df + 0.5) / (df + 0.5))
    where N is total documents and df is document frequency for each keyword.

    Args:
        docs: List of DocRecord objects with keywords

    Returns:
        Dictionary mapping each keyword to its IDF score (float)
        Returns empty dict if no keywords found

    Notes:
        - Higher scores indicate rarer, more distinctive keywords
        - Common keywords appearing in many documents get lower scores
        - Used to weight keyword matches during search
    """
    kw_docfreq: defaultdict[str, int] = defaultdict(int)
    all_kw = sorted({kw for d in docs for kw in d.keywords})
    if not all_kw:
        return {}
    for kw in all_kw:
        for d in docs:
            if kw in d.keywords:
                kw_docfreq[kw] += 1
    N = len(docs)
    return {kw: math.log(1 + (N - df + 0.5) / (df + 0.5)) for kw, df in kw_docfreq.items()}


# -----------------------------
# Build/Save/Load index
# -----------------------------
def build_index(
    docs_dir: str, model_name: str = DEFAULT_MODEL_NAME, logger: logging.Logger | None = None
) -> SearchIndex:
    """
    Build a complete search index from Terraform module documentation.

    Recursively scans a directory for Markdown files, parses each file to
    extract module metadata, and builds multiple search indices:
    1. BM25 index for text relevance ranking
    2. Semantic embeddings using sentence transformers
    3. Keyword IDF scores for keyword matching
    4. Module name and keyword lookup structures

    The process includes:
    - Parsing all .md files in the directory tree
    - Tokenizing document text for BM25
    - Generating L2-normalized embeddings (CPU-only)
    - Computing IDF scores for all keywords
    - Organizing data structures for fast search

    Args:
        docs_dir: Directory containing Terraform module .md files
        model_name: Sentence transformer model for embeddings
                   (default: intfloat/e5-small-v2)
        logger: Logger instance for logging operations

    Returns:
        SearchIndex object containing all indices and metadata

    Raises:
        RuntimeError: If no valid Markdown documents found in docs_dir

    Notes:
        - Downloads the embedding model on first use (~130MB for e5-small-v2)
        - All processing is CPU-only, no GPU required
        - Embedding generation may take 1-5 minutes for hundreds of documents
        - Files that fail to parse are silently skipped

    Example:
        >>> logger = logging.getLogger(__name__)
        >>> index = build_index("./modules/terraform-aws-modules", logger=logger)
        >>> print(f"Indexed {len(index.docs)} documents")
    """
    assert logger is not None, "Logger must not be None"  # noqa: S101
    logger.info(f"Building index from directory: {docs_dir}")
    logger.info(f"Using embedding model: {model_name}")

    paths = list(Path(docs_dir).rglob("*.md"))
    logger.info(f"Found {len(paths)} markdown files to process")

    docs: list[DocRecord] = []
    for p in paths:
        rec = parse_markdown_file(p, logger)
        if rec:
            docs.append(rec)

    logger.info(f"Successfully parsed {len(docs)} documents")

    if not docs:
        logger.error("No Markdown documents found or parsed successfully")
        raise RuntimeError("No Markdown documents found.")

    logger.info("Building BM25 index...")
    corpus_tokens = [tokenize(d.text) for d in docs]
    bm25 = BM25Okapi(corpus_tokens)
    logger.info(f"BM25 index built with {len(corpus_tokens)} tokenized documents")

    logger.info("Computing keyword IDF scores...")
    kw_idf = compute_kw_idf(docs)
    logger.info(f"Computed IDF for {len(kw_idf)} unique keywords")

    logger.info(f"Loading embedding model: {model_name}")
    encoder = _get_encoder(model_name, logger)

    logger.info(f"Generating semantic embeddings for {len(docs)} documents (this may take a few minutes)...")
    doc_vecs = encoder.encode([d.text for d in docs])
    logger.info(f"Generated embeddings with shape {doc_vecs.shape}")

    module_names = [d.module_name for d in docs]
    doc_kw_sets = [set(d.keywords) for d in docs]

    logger.info(f"Index building complete: {len(docs)} documents indexed")

    return SearchIndex(
        model_name=model_name,
        docs=docs,
        bm25_corpus_tokens=corpus_tokens,
        bm25=bm25,
        doc_vectors=doc_vecs,
        kw_idf=kw_idf,
        module_names=module_names,
        doc_kw_sets=doc_kw_sets,
    )


def save_index(index: SearchIndex, path: str, logger: logging.Logger) -> None:
    """
    Serialize and save a SearchIndex to disk using pickle.

    Saves the complete index including BM25 corpus, embeddings, IDF scores,
    and all metadata to a binary pickle file for fast loading later.

    Args:
        index: SearchIndex object to save
        path: Output file path (typically .pkl extension)
        logger: Logger instance for logging operations

    Returns:
        None

    Notes:
        - Uses highest pickle protocol for efficiency
        - File size typically 10-100MB depending on corpus size
        - Index can be loaded later with load_index()
        - Overwrites existing file at path

    Example:
        >>> logger = logging.getLogger(__name__)
        >>> save_index(index, "./model/tfmod_e5_small_index.pkl", logger)
    """
    logger.info(f"Saving index to {path}")
    with open(path, "wb") as f:
        pickle.dump(index, f, protocol=pickle.HIGHEST_PROTOCOL)

    # Log file size
    file_size = Path(path).stat().st_size
    size_mb = file_size / (1024 * 1024)
    logger.info(f"Index saved successfully ({size_mb:.2f} MB)")


def load_index(path: str, logger: logging.Logger) -> SearchIndex:
    """
    Load a previously saved SearchIndex from disk.

    Deserializes a pickled SearchIndex file, restoring all components
    including BM25 corpus, embeddings, and metadata.

    Args:
        path: Path to pickled index file (.pkl)
        logger: Logger instance for logging operations

    Returns:
        SearchIndex object ready for searching

    Raises:
        FileNotFoundError: If path doesn't exist
        pickle.UnpicklingError: If file is corrupted or incompatible

    Notes:
        - Loading is very fast (typically < 1 second)
        - No model download required (embeddings are in the file)
        - Compatible with indices created by build_index() and save_index()

    Example:
        >>> logger = logging.getLogger(__name__)
        >>> index = load_index("./model/tfmod_e5_small_index.pkl", logger)
        >>> print(f"Loaded {len(index.docs)} documents")
    """
    logger.info(f"Loading index from {path}")
    with open(path, "rb") as f:
        index = pickle.load(f)  # noqa: S301 - index is our own locally-built, trusted artifact

    logger.info(
        f"Index loaded successfully: {len(index.docs)} documents, {len(index.kw_idf)} keywords, model={index.model_name}"
    )
    return index


# -----------------------------
# Scoring
# -----------------------------
ScoredHit = namedtuple("ScoredHit", ["score", "doc_index", "exact_hit", "kw_overlap", "sem_sim"])
"""A single ranked search result with its scoring components exposed.

- score: combined weighted score (same value compute_scores returns)
- doc_index: index into index.docs array
- exact_hit: True when this doc earned the exact module-name-match component
- kw_overlap: True when this doc had any keyword-IDF overlap with the query
  (pre-normalization; a real lexical signal, not just a residual after minmax)
- sem_sim: the raw cosine similarity scaled to [0,1] (before the per-query
  min-max normalization) - comparable across queries, unlike the combined
  score or the min-maxed semantic component
"""


def compute_scores(
    index: SearchIndex,
    query: str,
    w_kw: float = 2.0,
    w_exact: float = 3.0,
    w_bm25: float = 1.0,
    w_sem: float = 1.0,
    top_k: int = 10,
    query_instruction: str | None = None,
    logger: logging.Logger | None = None,
) -> list[tuple[float, int]]:
    """
    Perform hybrid search and return ranked results.

    Thin wrapper over compute_scores_detailed() that drops the lexical-signal
    fields, kept for backward compatibility with existing callers (CLI, tests).
    See compute_scores_detailed() for the full docstring of the scoring
    algorithm and parameters.
    """
    hits = compute_scores_detailed(
        index,
        query,
        w_kw=w_kw,
        w_exact=w_exact,
        w_bm25=w_bm25,
        w_sem=w_sem,
        top_k=top_k,
        query_instruction=query_instruction,
        logger=logger,
    )
    return [(h.score, h.doc_index) for h in hits]


def compute_scores_detailed(
    index: SearchIndex,
    query: str,
    w_kw: float = 2.0,
    w_exact: float = 3.0,
    w_bm25: float = 1.0,
    w_sem: float = 1.0,
    top_k: int = 10,
    query_instruction: str | None = None,
    logger: logging.Logger | None = None,
) -> list[ScoredHit]:
    """
    Perform hybrid search and return ranked results with scoring components exposed.

    Combines four scoring components with configurable weights:
    1. Keyword overlap (IDF-weighted) - matches query terms to document keywords
    2. Exact module name match - boost for documents matching normalized query
    3. BM25 text relevance - statistical text matching across full document
    4. Semantic similarity - neural embedding cosine similarity

    Each component is min-max normalized to [0,1] before weighted combination.
    If no keyword matches are found, falls back to BM25 + semantic only.

    Scoring Algorithm:
    - Tokenize and normalize query
    - Match query tokens against document keywords (IDF-weighted)
    - Check for exact module name matches
    - Compute BM25 scores across document corpus
    - Generate query embedding and compute cosine similarity
    - Normalize all scores to [0,1]
    - Combine: final = w_kw*kw + w_exact*exact + w_bm25*bm25 + w_sem*semantic
    - Return top_k results by descending score

    Args:
        index: Prebuilt SearchIndex containing documents and indices
        query: Natural language search query string
        w_kw: Weight for keyword overlap component (default: 2.0)
        w_exact: Weight for exact module name match (default: 3.0)
        w_bm25: Weight for BM25 text relevance (default: 1.0)
        w_sem: Weight for semantic similarity (default: 1.0)
        top_k: Number of top results to return (default: 10)
        query_instruction: Optional instruction prefix for query embedding.
                          For BGE models, use BGE_QUERY_INSTRUCTION constant.
                          If None, no prefix is applied (default: None)
        logger: Logger instance for logging operations

    Returns:
        List of ScoredHit namedtuples, sorted by descending score. Each
        ScoredHit contains:
        - score (float): Combined weighted score
        - doc_index (int): Index into index.docs array
        - exact_hit (bool): True when the exact module-name-match component fired
        - kw_overlap (bool): True when there was any keyword-IDF overlap with the query
        - sem_sim (float): Raw cosine similarity scaled to [0,1], before the
          per-query min-max normalization - comparable across queries

        compute_scores() wraps this and returns plain (score, doc_index) tuples
        for backward compatibility.

    Notes:
        - Empty query returns empty list
        - Loads sentence transformer model for query encoding (cached)
        - All scoring components are normalized before combination
        - Higher weights increase component's influence on final ranking
        - Semantic similarity is scaled from [-1,1] to [0,1]

    Examples:
        >>> logger = logging.getLogger(__name__)
        >>> results = compute_scores_detailed(index, "s3 bucket encryption", logger=logger)
        >>> for hit in results[:3]:
        ...     print(f"{hit.score:.3f}: {index.docs[hit.doc_index].module_name}")
        6.934: s3-bucket
        1.921: eks
        1.764: iam

        >>> # Increase semantic weight for better conceptual matching
        >>> results = compute_scores_detailed(index, "object storage", w_sem=3.0, logger=logger)

        >>> # Only exact name matching
        >>> results = compute_scores_detailed(index, "vpc", w_kw=0, w_bm25=0, w_sem=0, w_exact=10.0, logger=logger)
    """
    assert logger is not None, "Logger must not be None"  # noqa: S101
    logger.info(f"Executing search query: '{query}'")
    logger.debug(f"Search weights: kw={w_kw}, exact={w_exact}, bm25={w_bm25}, sem={w_sem}, top_k={top_k}")

    q = query.strip()
    if not q:
        logger.warning("Empty query provided, returning empty results")
        return []

    q_tokens = tokenize(q)
    q_norm = normalize_modname(q)
    logger.debug(f"Query tokens: {q_tokens}")
    logger.debug(f"Normalized query: {q_norm}")

    # Direct keyword matching from query tokens
    known_keywords = set(index.kw_idf.keys())
    q_kw = {t for t in q_tokens if t in known_keywords}
    logger.debug(f"Query keywords matching index: {q_kw}")

    exact_hits = np.array([1.0 if exact_name_match(mn, q_norm) else 0.0 for mn in index.module_names], dtype=np.float32)
    exact_count = int(np.sum(exact_hits))
    if exact_count > 0:
        logger.debug(f"Found {exact_count} exact module name matches")

    logger.debug("Computing BM25 scores...")
    bm_raw = np.array(index.bm25.get_scores(q_tokens), dtype=np.float32)
    bm = minmax(bm_raw)

    logger.debug("Generating query embedding and computing semantic similarity...")
    # Use the same model as index (cached to avoid HTTP requests). Construction
    # (if any) happens inside _get_encoder before this lock is taken, so the
    # encode() call below is the only thing serialized here - no nested
    # _MODEL_LOCK acquisition.
    encoder = _get_encoder(index.model_name, logger)
    # Use prompt parameter for optional query instruction (e.g., for BGE models)
    with _MODEL_LOCK:
        q_vec = encoder.encode([q], prompt=query_instruction)[0].astype(np.float32, copy=False)
    if q_vec.shape[0] != index.doc_vectors.shape[1]:
        raise RuntimeError(
            f"embedding dimension mismatch: query encoder produced {q_vec.shape[0]}-dim vectors "
            f"but the index was built with {index.doc_vectors.shape[1]}-dim embeddings "
            f"({index.model_name}) - the active backend is serving a different model"
        )
    cos_raw = cosine_sim_matrix(q_vec, index.doc_vectors)
    cos_raw = (cos_raw + 1.0) / 2.0  # Scale from [-1, 1] to [0, 1]
    cos = minmax(cos_raw)  # Normalize to spread small differences

    if known_keywords:
        kw_vals = []
        for s in index.doc_kw_sets:
            inter = s.intersection(q_kw)
            if not inter:
                kw_vals.append(0.0)
            else:
                kw_vals.append(sum(index.kw_idf.get(k, 0.0) for k in inter))
        kw_arr = np.array(kw_vals, dtype=np.float32)
        kw = minmax(kw_arr)
    else:
        kw = np.zeros(len(index.docs), dtype=np.float32)
        kw_arr = kw

    if kw_arr.max() > 0:
        logger.debug("Using full hybrid scoring (keyword matches found)")
        final = (
            w_kw * kw
            + w_exact * exact_hits
            + w_bm25 * (math.log(len(q_kw) + 1, 3)) * bm
            + w_sem * (math.log(len(q_kw) + 1, 3)) * cos
        )
    else:
        logger.debug("No keyword matches, using BM25 + semantic only")
        final = w_bm25 * bm + w_sem * cos

    order = np.argsort(-final)[:top_k]
    results = [
        ScoredHit(
            score=float(final[i]),
            doc_index=int(i),
            exact_hit=bool(exact_hits[i] > 0),
            kw_overlap=bool(kw_arr[i] > 0),
            sem_sim=float(cos_raw[i]),
        )
        for i in order
    ]

    logger.info(f"Search complete: returning {len(results)} results")
    if results:
        top_score = results[0].score
        top_module = index.docs[results[0].doc_index].module_name
        logger.debug(f"Top result: {top_module} (score={top_score:.3f})")

    return results


# Configure logging - console + file
def setup_logging(log_filename: str = "lib.log", log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging to both console and rotating file.

    This function configures the root logger with both console and file handlers.
    It should be called once at application startup before any logging occurs.

    Args:
        log_filename: Name of the log file (default: "lib.log")
                     Will be created in the logs/ directory
        log_level: Logging level as string (default: "INFO")
                  Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL

    Returns:
        Configured logger instance for the calling module

    Features:
        - Logs to both console (stderr) and file simultaneously
        - Rotating file handler (10MB max, keeps 5 backups)
        - UTF-8 encoding for international characters
        - Consistent timestamp format
        - Configurable log level

    Notes:
        - If handlers are already configured, this function does nothing
        - Log directory is created automatically if it doesn't exist
        - All loggers inherit this configuration (uses root logger)

    Example:
        >>> from tfmod_search_lib import setup_logging
        >>> logger = setup_logging("mcp_server.log", "DEBUG")
        >>> logger.info("This goes to both console and file")
    """
    root_logger = logging.getLogger()

    # Skip if already configured (e.g., by another module)
    if root_logger.handlers:
        return logging.getLogger(__name__)

    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / log_filename

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)

    # File handler with rotation (10MB max, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # Configure root logger with specified level
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Silence noisy third-party loggers (FastMCP internals)
    for noisy_logger in ["fakeredis", "docket", "asyncio"]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    return logging.getLogger(__name__)


def switch_log_file(new_log_filename: str) -> None:
    """
    Switch the file handler to a new log file.

    This removes the old file handler and adds a new one pointing to a different file.
    Useful for switching from startup.log to operational logs after initialization.

    Args:
        new_log_filename: Name of the new log file in the logs/ directory

    Notes:
        - Console handler remains unchanged
        - Previous log file is closed properly
        - New file handler uses same formatter and settings
    """
    root_logger = logging.getLogger()

    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    new_log_file = log_dir / new_log_filename

    # Find and remove existing file handlers
    for handler in root_logger.handlers[:]:
        if isinstance(handler, RotatingFileHandler):
            handler.close()
            root_logger.removeHandler(handler)

    # Add new file handler
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    new_file_handler = RotatingFileHandler(
        new_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    new_file_handler.setFormatter(formatter)
    root_logger.addHandler(new_file_handler)
