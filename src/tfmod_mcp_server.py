#!/usr/bin/env python3
"""
TFModSearch MCP Server (stdio) using fastmcp.

Tools exposed:
- modules_list() -> complete catalog of indexed modules
- search_modules(query: str) -> top-3 ranked hits
- get_module(module_identifier: str) -> full module documentation
- grep_module_docs(module_id: str, pattern: str) -> regex-grepped live registry documentation

The server requires an index file specified via --index_path argument or uses default location.
Search scoring weights are loaded from config.yaml and can be overridden via CLI arguments.
"""

import argparse
import ipaddress
import json
import logging
import os
import re
import sys
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Annotated, Any

import yaml
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field, GetJsonSchemaHandler, field_serializer, model_serializer
from pydantic.json_schema import JsonSchemaValue
from starlette.requests import Request
from starlette.responses import JSONResponse

# parse_arguments lives in the import-light tfmod_server_args module so the
# proxy entry path (tfmod_entry) can use it without pulling the ML stack;
# re-exported here for backward compatibility (tests and external callers).
from tfmod_server_args import _env_default, parse_arguments  # noqa: E402, F401

import tfmod_registry_docs
from tfmod_doc_grep import grep_document
from tfmod_registry_docs import fetch_latest_pypi_version, get_assembled_docs, is_newer_version
from tfmod_search_lib import (
    _PROJECT_ROOT,
    ModuleDocumentParser,
    ScoredHit,
    SearchIndex,
    compute_scores,
    compute_scores_detailed,
    extract_description,
    extract_purpose,
    initialize_nltk,
    load_index,
    normalize_modname,
    resolve_index_path,
    setup_logging,
    switch_log_file,
    tokenize,
)

try:
    _SERVER_VERSION = package_version("tfmodsearch")
except PackageNotFoundError:
    _SERVER_VERSION = "0.0.0.dev0"

app = FastMCP(
    name="tfmod-search",
    version=_SERVER_VERSION,
    instructions="""
# TFModSearch — Terraform Module Documentation Search & Live Registry Grep

Two complementary tool families. Module APIs change between major versions;
memorized variable names are frequently stale. Before writing or modifying
Terraform, ALWAYS retrieve current documentation rather than relying on
training data.

## Curated AWS catalog (offline, compact) — community terraform-aws-modules

1. `search_modules(query, top_k=3)` — find the right module. Returns the
   top-ranked matches (default 3, up to 10) with name, path, keywords,
   description, relevance score, and `module_id`/`latest_version` (registry
   coordinates for chaining into `grep_module_docs`). Query by functionality
   ("s3 bucket with encryption and versioning"), technology ("kubernetes
   cluster"), or exact module name ("vpc", "eks").
   Each result also carries a `confidence` verdict: `"high"` means the top
   hit's own name/keywords/Description assert the asked capability — trust
   it, and its orientation head is inlined as `top_module_doc`. `"low"` means
   the capability is not clearly asserted by the top hit; a `"low"` does NOT
   by itself mean "not in catalog" — it can still be the right module under
   unfamiliar phrasing. On a `"low"`, rephrase by capability and/or check
   `get_module`/`modules_list` BEFORE concluding no module exists. Caveat: a
   query phrased as an exclusion ("X without Y") is not evaluated as a
   negation and can grade `"high"` on the very technology it asked to avoid —
   read the description before trusting a `"high"` on that kind of query.
2. `get_module(module_identifier, sections=None)` — orient on the chosen
   module. Accepts a module name ("vpc"), a relative doc path
   ("modules/terraform-aws-modules/vpc.md"), or a submodule address
   ("iam//modules/iam-role"). By default returns a compact orientation head —
   description, module info, exact version pin, agent notes, any gotchas, key
   features, use cases — plus a footer with the full section inventory (an
   explicit menu of logical keys + headings). For a module WITH submodules the
   head also inlines the submodule inventory (each submodule's name, purpose,
   and pinnable source), so the right answer is often a submodule: pin its
   source, or call `get_module("<name>//modules/<sub>")` for its scoped head.
   Pass `sections` (e.g. ["inputs", "examples"]) to pull specific parts, or
   `sections=["all"]` for the full document; prefer scoped `sections` over
   "all" on large modules. A nested/complex leaf shape — a bare bool vs an
   object, a map keyed by a NUMBER vs a name, a plural vs singular field, a
   sub-block that defaults ON — is usually visible only in `examples`: check
   `get_module(name, sections=["examples"])` (or grep) before writing any
   nested/complex (`any`/`object(...)`) input. Never leave a required nested
   block as a prose comment or TODO — write the exact shape the doc shows.
3. Use the exact variable names, defaults, and pinned version shown in the
   retrieved documentation — not values recalled from training data.

`modules_list()` returns the full catalog (names, paths, descriptions,
keywords, module_id, latest_version) when browsing is preferable to search.

## Live registry grep (any module, any provider ecosystem, version-pinnable)

4. `grep_module_docs(module_id, pattern, version=None, ...)` — fetch the
   full, current documentation for ANY Terraform Registry module (not just
   the curated AWS catalog) — optionally pinned to an exact `version` — and
   regex-grep it, returning only matching lines with a few lines of context
   (like the Grep tool), not the whole document. Use this when: the module
   isn't in the curated catalog; you need a specific/older version's exact
   variable names or defaults; or you want to pinpoint one detail (e.g. "what
   is the default of the NAT-gateway variable in 6.6.1?") without flooding
   context with a 10k+ token document. Results are disk-cached: pinned
   versions forever, `latest` for `doc_cache_ttl_hours` (default 24h, or pass
   `refresh=true` to bypass). Zero matches still returns `available_sections`
   so you can refine `pattern`/`scope`.

## Tool Boundaries

- Curated AWS module, general usage/examples/inputs → `search_modules` +
  `get_module` (fast, offline, hand-curated).
- Any registry module (AWS or not), a specific/older version, or a pinpoint
  variable/default lookup → `grep_module_docs` (live, version-aware, regex).
- Chain them: `search_modules` results carry `module_id`/`latest_version` —
  feed those straight into `grep_module_docs` without guessing coordinates.

## Call economy — spend the fewest calls

- If you already know the module name (an obvious AWS service), call
  `get_module("<name>")` DIRECTLY — skip `search_modules`. Search is for when
  the module is NOT obvious from the requirement.
- ONE `get_module("<name>", sections=["inputs"])` returns the authoritative
  CURRENT variable table. Do NOT then call `grep_module_docs` to re-verify names you
  already have — that is a wasted call. `grep_module_docs` is ONLY for modules
  outside the curated catalog, a specific/older version, or a pinpoint lookup
  the head/sections don't carry.
- Budget: a curated-catalog requirement should cost ~1–2 calls total
  (an optional search + one get_module), not 3–4.

## Search Tips

- Descriptive queries beat single words: "object storage with versioning" > "storage"
- Include key requirements: "vpc with multiple availability zones"
- Exact module names work too: "vpc", "s3-bucket", "rds"
- If results are too broad, add specific terms; too narrow, use broader ones
- When two results are close, the higher-scored match on the more specific
  requirement term is usually the better fit — but read BOTH descriptions:
  the curated description states the distinguishing use-case (e.g. "durable
  primary datastore" ⇒ memory-db, not the higher-familiarity elasticache)
""",
)


@app.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    """Liveness/readiness probe for the HTTP transport (no MCP handshake needed)."""
    try:
        state = ServerStateManager.get()
    except RuntimeError:
        return JSONResponse({"status": "initializing"}, status_code=503)
    update_state = _UPDATE_STATE  # local snapshot: both keys come from one consistent dict
    return JSONResponse(
        {
            "status": "ok",
            "version": _SERVER_VERSION,
            "modules": len(state.index.docs),
            "latest_version": update_state["latest_version"],
            "update_available": update_state["update_available"],
        }
    )


# -----------------------------
# Configuration and State Management
# -----------------------------


@dataclass
class SearchWeights:
    """
    Search scoring weights configuration with validation.

    Attributes:
        w_kw: Weight for keyword overlap with IDF weighting (default: 2.0)
        w_exact: Weight for exact module name match boost (default: 3.0)
        w_bm25: Weight for BM25 text relevance (default: 1.0)
        w_sem: Weight for semantic similarity (default: 1.0)
    """

    w_kw: float = 2.0
    w_exact: float = 3.0
    w_bm25: float = 1.0
    w_sem: float = 1.0

    def __post_init__(self):
        """Validate that all weights are non-negative."""
        for field_name, value in asdict(self).items():
            if value < 0:
                raise ValueError(f"{field_name} must be non-negative, got {value}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SearchWeights":
        """
        Create SearchWeights from dictionary.

        Args:
            data: Dictionary containing weight values

        Returns:
            SearchWeights instance with values from dict
        """
        valid_fields = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_fields)

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return asdict(self)


class ConfigLoader:
    """Handles loading and merging configuration from multiple sources."""

    @staticmethod
    def load_weights(
        config_path: Path | None = None,
        cli_overrides: dict[str, float | None] | None = None,
        logger: logging.Logger | None = None,
    ) -> SearchWeights:
        """
        Load search weights with precedence: CLI > YAML > defaults.

        Args:
            config_path: Path to YAML configuration file
            cli_overrides: Dictionary of CLI argument overrides
            logger: Logger instance for logging operations

        Returns:
            SearchWeights instance with merged configuration
        """
        # Start with defaults
        weights_dict = {}

        # Load from YAML if exists
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    if config and "search_weights" in config:
                        weights_dict = config["search_weights"]
                        if logger:
                            logger.info(f"Loaded weights from config: {config_path}")
            except Exception as e:
                if logger:
                    logger.warning(f"Error loading config from {config_path}: {e}, using defaults")
        elif config_path:
            if logger:
                logger.warning(f"Config file not found at {config_path}, using defaults")

        # Create weights with YAML values
        weights = SearchWeights.from_dict(weights_dict) if weights_dict else SearchWeights()

        # Apply CLI overrides
        if cli_overrides:
            overrides_applied = {}
            for key, value in cli_overrides.items():
                if value is not None and hasattr(weights, key):
                    setattr(weights, key, value)
                    overrides_applied[key] = value
            if overrides_applied and logger:
                logger.info(f"Applied CLI overrides: {overrides_applied}")

        return weights

    @staticmethod
    def load_query_instruction(
        config_path: Path | None = None,
        cli_override: str | None = None,
        logger: logging.Logger | None = None,
    ) -> str | None:
        """
        Load query instruction with precedence: CLI > YAML > default (None).

        Args:
            config_path: Path to YAML configuration file
            cli_override: CLI argument override for query_instruction
            logger: Logger instance for logging operations

        Returns:
            Query instruction string or None if disabled
        """
        query_instruction = None

        # Load from YAML if exists
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    if config and "query_instruction" in config:
                        query_instruction = config["query_instruction"]
                        if logger and query_instruction:
                            logger.info(f"Loaded query_instruction from config: {config_path}")
            except Exception as e:
                if logger:
                    logger.warning(f"Error loading query_instruction from {config_path}: {e}")

        # Apply CLI override (takes precedence)
        if cli_override is not None:
            query_instruction = cli_override if cli_override else None
            if logger:
                logger.info(f"Applied CLI override for query_instruction: {'set' if query_instruction else 'disabled'}")

        return query_instruction

    @staticmethod
    def load_log_level(
        config_path: Path | None = None,
        cli_override: str | None = None,
        logger: logging.Logger | None = None,
    ) -> str:
        """
        Load log level with precedence: CLI > YAML > default (INFO).

        Args:
            config_path: Path to YAML configuration file
            cli_override: CLI argument override for log_level
            logger: Logger instance for logging operations

        Returns:
            Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        log_level = "INFO"  # Default

        # Load from YAML if exists
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    if config and "log_level" in config:
                        log_level = config["log_level"]
                        if logger:
                            logger.info(f"Loaded log_level from config: {config_path}")
            except Exception as e:
                if logger:
                    logger.warning(f"Error loading log_level from {config_path}: {e}")

        # Apply CLI override (takes precedence)
        if cli_override is not None:
            log_level = cli_override
            if logger:
                logger.info(f"Applied CLI override for log_level: {log_level}")

        return log_level.upper()

    @staticmethod
    def load_doc_cache(
        config_path: Path | None = None,
        cli_overrides: dict[str, Any] | None = None,
        logger: logging.Logger | None = None,
    ) -> tuple[Path, int]:
        """
        Load registry-docs cache configuration with precedence: CLI > YAML > defaults.

        Args:
            config_path: Path to YAML configuration file
            cli_overrides: Dict with optional 'doc_cache_dir' (str) and
                'doc_cache_ttl_hours' (int) overrides
            logger: Logger instance for logging operations

        Returns:
            Tuple of (cache_dir, ttl_hours) for grep_module_docs's registry-docs cache.
            Default cache_dir: $TFMODSEARCH_CACHE_DIR or $XDG_CACHE_HOME or ~/.cache,
            joined with "tfmodsearch/registry_docs". Default ttl_hours: 24.
        """
        default_cache_root = Path(
            os.environ.get("TFMODSEARCH_CACHE_DIR") or os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
        )
        cache_dir = default_cache_root / "tfmodsearch" / "registry_docs"
        ttl_hours = 24

        # Load from YAML if exists
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    if config:
                        if config.get("doc_cache_dir"):
                            cache_dir = Path(config["doc_cache_dir"])
                            if logger:
                                logger.info(f"Loaded doc_cache_dir from config: {config_path}")
                        if config.get("doc_cache_ttl_hours") is not None:
                            ttl_hours = int(config["doc_cache_ttl_hours"])
                            if logger:
                                logger.info(f"Loaded doc_cache_ttl_hours from config: {config_path}")
            except Exception as e:
                if logger:
                    logger.warning(f"Error loading doc cache config from {config_path}: {e}, using defaults")
        elif config_path:
            if logger:
                logger.warning(f"Config file not found at {config_path}, using doc cache defaults")

        # Apply CLI overrides (take precedence)
        if cli_overrides:
            if cli_overrides.get("doc_cache_dir"):
                cache_dir = Path(cli_overrides["doc_cache_dir"])
                if logger:
                    logger.info(f"Applied CLI override for doc_cache_dir: {cache_dir}")
            if cli_overrides.get("doc_cache_ttl_hours") is not None:
                ttl_hours = int(cli_overrides["doc_cache_ttl_hours"])
                if logger:
                    logger.info(f"Applied CLI override for doc_cache_ttl_hours: {ttl_hours}")

        return cache_dir, ttl_hours


class ServerState:
    """
    Encapsulates all MCP server state and configuration.

    This class holds the search index, configuration weights, and provides
    thread-safe access to server state.

    Attributes:
        _index: The loaded search index
        _weights: Search scoring weights configuration
        _index_path: Path to the index file
        _query_instruction: Optional query instruction prefix for BGE models
        _doc_cache_dir: Disk cache directory for grep_module_docs registry documents
        _doc_cache_ttl_hours: TTL (hours) for "latest" registry doc cache entries
    """

    def __init__(
        self,
        index: SearchIndex | None,
        weights: SearchWeights,
        index_path: Path,
        query_instruction: str | None = None,
        logger: logging.Logger | None = None,
        doc_cache_dir: Path | None = None,
        doc_cache_ttl_hours: int = 24,
    ):
        """
        Initialize server state.

        Args:
            index: Loaded search index (can be None for testing)
            weights: Search weights configuration
            index_path: Path to index file
            query_instruction: Optional query instruction prefix for BGE models
            logger: Logger instance for logging operations
            doc_cache_dir: Disk cache directory for grep_module_docs registry documents
                (None until resolved by initialize_server/ConfigLoader.load_doc_cache;
                grep_module_docs falls back to the default location if still None)
            doc_cache_ttl_hours: TTL (hours) for "latest" (unpinned) registry doc cache
                entries; pinned versions are always cached forever regardless
        """
        self._index = index
        self._weights = weights
        self._index_path = index_path
        self._query_instruction = query_instruction
        self._lock = threading.RLock()
        self._logger = logger
        self._doc_cache_dir = doc_cache_dir
        self._doc_cache_ttl_hours = doc_cache_ttl_hours

        doc_count = len(index.docs) if index is not None else 0
        if self._logger:
            self._logger.info(
                f"ServerState initialized: index_path={index_path}, "
                f"docs={doc_count}, weights={weights.to_dict()}, "
                f"query_instruction={'set' if query_instruction else 'disabled'}, "
                f"doc_cache_dir={doc_cache_dir}, doc_cache_ttl_hours={doc_cache_ttl_hours}"
            )

    @property
    def index(self) -> SearchIndex:
        """Get the search index."""
        if self._index is None:
            raise RuntimeError("Index is not loaded")
        return self._index

    @property
    def weights(self) -> SearchWeights:
        """Get search weights configuration."""
        return self._weights

    @property
    def index_path(self) -> Path:
        """Get index file path."""
        return self._index_path

    @property
    def logger(self) -> logging.Logger | None:
        """Get logger instance."""
        return self._logger

    @property
    def query_instruction(self) -> str | None:
        """Get optional query instruction prefix for BGE models."""
        return self._query_instruction

    @property
    def doc_cache_dir(self) -> Path | None:
        """Get the disk cache directory for grep_module_docs registry documents."""
        return self._doc_cache_dir

    @property
    def doc_cache_ttl_hours(self) -> int:
        """Get the TTL (hours) for 'latest' (unpinned) registry doc cache entries."""
        return self._doc_cache_ttl_hours

    def reload_index(self, new_index_path: Path | None = None) -> None:
        """
        Reload index from file (thread-safe).

        Args:
            new_index_path: Path to new index file (uses current path if None)

        Raises:
            ValueError: If index file not found or invalid
        """
        assert self._logger is not None, "ServerState must have a logger"  # noqa: S101
        path = new_index_path or self._index_path
        try:
            self._logger.info(f"Reloading index from: {path}")
            new_index = load_index(str(path), self._logger)
            with self._lock:
                self._index = new_index
                self._index_path = path
            self._logger.info(f"Index reloaded successfully: {len(new_index.docs)} documents")
        except Exception as e:
            self._logger.error(f"Failed to reload index from {path}: {e}")
            raise ValueError(f"Failed to reload index: {e}") from e

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ServerState(index_path={self._index_path}, "
            f"docs={len(self._index.docs) if self._index else 0}, "
            f"weights={self._weights})"
        )


class ServerStateManager:
    """
    Manages singleton server state instance with thread-safe access.

    This class implements the singleton pattern to ensure only one server
    state exists and provides clean initialization/access patterns.
    """

    _instance: ServerState | None = None
    _lock = threading.Lock()

    @classmethod
    def initialize(
        cls,
        index: SearchIndex,
        weights: SearchWeights,
        index_path: Path,
        query_instruction: str | None = None,
        logger: logging.Logger | None = None,
        doc_cache_dir: Path | None = None,
        doc_cache_ttl_hours: int = 24,
    ) -> ServerState:
        """
        Initialize the server state singleton.

        This should be called once at server startup.

        Args:
            index: Loaded search index
            weights: Search weights configuration
            index_path: Path to index file
            query_instruction: Optional query instruction prefix for BGE models
            logger: Logger instance for logging operations
            doc_cache_dir: Disk cache directory for grep_module_docs registry documents
            doc_cache_ttl_hours: TTL (hours) for "latest" registry doc cache entries

        Returns:
            Initialized ServerState instance

        Raises:
            RuntimeError: If already initialized
        """
        with cls._lock:
            if cls._instance is not None:
                raise RuntimeError("ServerState already initialized")
            cls._instance = ServerState(
                index, weights, index_path, query_instruction, logger, doc_cache_dir, doc_cache_ttl_hours
            )
            if logger:
                logger.info("ServerStateManager initialized")
            return cls._instance

    @classmethod
    def get(cls) -> ServerState:
        """
        Get the initialized server state.

        Returns:
            Current ServerState instance

        Raises:
            RuntimeError: If not initialized
        """
        if cls._instance is None:
            raise RuntimeError("ServerState not initialized. Call initialize() first.")
        return cls._instance

    @classmethod
    def reset(cls, logger: logging.Logger | None = None) -> None:
        """
        Reset state (primarily for testing).

        This allows tests to create new state instances.

        Args:
            logger: Logger instance for logging operations
        """
        with cls._lock:
            cls._instance = None
            if logger:
                logger.debug("ServerStateManager reset")


# -----------------------------
# Pydantic models for tool I/O
# -----------------------------
class SearchHit(BaseModel):
    module_name: str = Field(..., description="Terraform module name (e.g., 'eks', 's3-bucket').")
    path: str = Field(
        ..., description="File path to module documentation (e.g., 'modules/terraform-aws-modules/vpc.md')."
    )
    keywords: list[str] = Field(..., description="Module keywords/tags extracted from documentation.")
    description: str = Field(..., description="Module description extracted from documentation text.")
    score: float = Field(..., description="Combined relevance score from hybrid search.")
    module_id: str = Field(
        ...,
        description="Terraform Registry coordinates 'namespace/name/provider' (e.g., "
        "'terraform-aws-modules/vpc/aws'). Pass this to grep_module_docs to grep the "
        "live, current registry documentation for this module.",
    )
    latest_version: str = Field(
        ...,
        description="Latest version known at doc-curation time (a hint, not a live guarantee). "
        "Pass as `version` to grep_module_docs to pin that snapshot, or omit to resolve the true latest.",
    )

    @field_serializer("score")
    def serialize_score(self, value: float) -> float:
        """Round score to 2 decimal places for JSON output."""
        return round(value, 2)


class UpdateNoticeMixin(BaseModel):
    """Adds an optional update_notice that vanishes from output when None.

    Also drops any other field named `hint` or `top_module_doc` when falsy
    (None or empty string) for the same reason -- SearchOutput.hint (L2/L7/L8/
    T3 confidence signal) is only meaningful for a "low" verdict, and
    SearchOutput.top_module_doc (L3 expand_top, default-on) is
    only populated on a high-confidence search. Only SearchOutput currently
    defines these fields, so this is a harmless no-op on every other model
    built on this mixin.

    FastMCP serializes pydantic None fields as JSON null; the spec requires
    the field to be entirely absent when no update is known, hence the
    wrap-mode serializer (verified against FastMCP 3.4.4).

    Side effect: a model_serializer(mode="wrap") makes pydantic unable to
    statically describe the serialization-mode JSON schema of the model (it
    cannot know what the wrap function returns), so
    `model_json_schema(mode="serialization")` collapses to `{}`. FastMCP
    publishes exactly that serialization-mode schema as a tool's
    `outputSchema`, so every model built on this mixin advertised an empty
    schema in `list_tools` -- a real contract regression, even though the
    actual JSON payload was unaffected.

    `__get_pydantic_json_schema__` below works around this: the emptiness is
    specific to serialization mode (validation mode is unaffected by the
    serializer and already renders the real properties, including
    `update_notice` as an optional field), so when asked for a
    serialization-mode schema we temporarily flip the live
    `GenerateJsonSchema` instance to validation mode for the duration of this
    model's own schema generation, then restore it. `GenerateJsonSchema.mode`
    has no public setter, hence the `_mode` write; verified against
    pydantic 2.13.4. This only affects the advertised schema shape -- actual
    JSON serialization (None absent, set value present) is untouched.
    """

    update_notice: str | None = Field(
        default=None,
        description="Present only when a newer tfmodsearch release exists; relay it to the user.",
    )

    @model_serializer(mode="wrap")
    def _drop_none_notice(self, handler: Any) -> Any:
        data = handler(self)
        if isinstance(data, dict):
            if data.get("update_notice") is None:
                data.pop("update_notice", None)
            if not data.get("hint"):
                data.pop("hint", None)
            if not data.get("top_module_doc"):
                data.pop("top_module_doc", None)
        return data

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        generator = handler.generate_json_schema  # type: ignore[attr-defined]
        original_mode = generator.mode
        if original_mode == "serialization":
            generator._mode = "validation"
        try:
            return handler(core_schema)
        finally:
            generator._mode = original_mode


class SearchOutput(UpdateNoticeMixin):
    results: list[SearchHit] = Field(..., description="Top-ranked Terraform modules matching the query.")
    confidence: str = Field(
        ...,
        description="Search confidence verdict: 'high' (trust the top hit) or 'low' "
        "(no confident catalog match -- likely absent). Always present.",
    )
    hint: str | None = Field(
        default=None,
        description="Actionable follow-up guidance, present only when confidence is "
        "'low'; absent entirely (not null) when confidence is 'high'.",
    )
    top_module_doc: str | None = Field(
        default=None,
        description="The top-1 module orientation head (L3), present by default whenever "
        "confidence is 'high' -- collapses the confident search->get_module pair into one "
        "call. Pass expand_top=False to suppress it. Absent entirely (not null) when "
        "expand_top=False or confidence is 'low'.",
    )


class ModuleListItem(BaseModel):
    """One catalog entry, covering BOTH modules_list detail levels with a single,
    union-free schema.

    Compact mode (the default) populates ``purpose``; full mode (``detail=full``)
    populates ``path``/``description``/``keywords`` instead. Every mode-specific
    field is optional, so the advertised output-item schema requires only the
    always-present fields and NOT ``path``. This is load-bearing: a strict MCP
    output-schema validator (the host client that drives the plugin) rejected the
    previous heterogeneous ``list[Compact] | list[Full]`` union with
    "'path' is a required property" because it mis-resolved the union to require
    ``path`` on compact items. A single model with optional fields carries no
    union for the validator to mis-resolve. Unset fields are dropped on
    serialization so the compact default stays byte-lean (no ``path: null`` noise).
    """

    module_name: str = Field(..., description="Terraform module name (e.g., 'eks', 's3-bucket').")
    module_id: str = Field(
        ...,
        description="Terraform Registry coordinates 'namespace/name/provider' (e.g., "
        "'terraform-aws-modules/vpc/aws'). Pass this to grep_module_docs to grep the "
        "live, current registry documentation for this module.",
    )
    latest_version: str = Field(
        ...,
        description="Latest version known at doc-curation time (a hint, not a live guarantee). "
        "Pass as `version` to grep_module_docs to pin that snapshot, or omit to resolve the true latest.",
    )
    purpose: str | None = Field(
        None, description="One-line purpose of the module (clipped). Present in the compact default."
    )
    path: str | None = Field(None, description="File path to module documentation. Present with detail=full.")
    description: str | None = Field(
        None, description="Module description extracted from documentation text. Present with detail=full."
    )
    keywords: list[str] | None = Field(None, description="Module keywords/tags. Present with detail=full.")

    @model_serializer
    def _drop_unset(self) -> dict[str, object]:
        # Emit only the fields the active detail level populated, so the compact
        # default carries no null path/description/keywords and full carries no
        # null purpose. Preserves the pre-0.23.1 byte-identical output shape.
        return {k: v for k, v in self.__dict__.items() if v is not None}


# Back-compat alias: modules_list previously built a distinct compact model. The
# compact/full split is now the same model with optional fields (see above).
ModuleListItemCompact = ModuleListItem


class ModulesListOutput(UpdateNoticeMixin):
    modules: list[ModuleListItem] = Field(
        ..., description="List of all available Terraform modules (compact by default, full metadata when detail=full)."
    )
    count: int = Field(..., description="Total number of modules in the catalog.")


class GrepMatch(BaseModel):
    section: str = Field(
        ...,
        description="Section label the match was found in, e.g. 'root/readme', 'root/inputs', "
        "'submodule:flow-log/readme', 'example:complete/readme'.",
    )
    line_number: int = Field(..., description="1-based line number within the assembled document.")
    line: str = Field(..., description="The matching line's text.")
    before: list[str] = Field(..., description="Up to context_lines lines immediately preceding the match.")
    after: list[str] = Field(..., description="Up to context_lines lines immediately following the match.")
    enclosing: str | None = Field(
        default=None,
        description="The nearest enclosing '- <name> | ...' list-item row (e.g. an input/output/"
        "resource header) when the match landed on a continuation line of a multi-line row (a "
        "type or description that spans multiple lines) -- so the container name/key is never "
        "lost. None when the matched line is itself a list-item row, or none was found in section.",
    )


class CacheInfo(BaseModel):
    hit: bool = Field(..., description="Whether the assembled document was served from the on-disk/memory cache.")
    fetched_at: str = Field(..., description="ISO-8601 timestamp of the underlying registry fetch.")
    policy: str = Field(
        ..., description="Cache policy applied: 'pinned' (immutable, cached forever) or 'latest-ttl' (TTL-based)."
    )


class GrepOutput(UpdateNoticeMixin):
    module_id: str = Field(..., description="Terraform Registry coordinates 'namespace/name/provider' requested.")
    resolved_version: str = Field(
        ..., description="Concrete version actually served (never the literal string 'latest')."
    )
    source_url: str = Field(..., description="Terraform Registry URL of the resolved module version.")
    total_matches: int = Field(..., description="Total logical matches found before the max_matches cap.")
    returned_matches: int = Field(..., description="Number of matches actually returned (<= max_matches).")
    truncated: bool = Field(..., description="True when total_matches exceeds max_matches.")
    cache: CacheInfo = Field(..., description="Cache status for the underlying document fetch.")
    matches: list[GrepMatch] = Field(..., description="Matching lines with section labels and surrounding context.")
    available_sections: list[str] = Field(
        ...,
        description="Full ordered list of section labels present in the assembled document, so pattern/scope "
        "can be refined — especially useful when total_matches is 0.",
    )


# -----------------------------
# Helper Functions (Testable, not decorated)
# -----------------------------


def _validate_and_resolve_module_path(path_str: str) -> Path:
    """
    Validate and resolve a module file path with security checks.

    Args:
        path_str: Relative path string to validate

    Returns:
        Resolved absolute Path object

    Raises:
        ValueError: If path is invalid, absolute, or outside modules/ directory
    """
    module_path = Path(path_str)

    # Security check: ensure path is relative
    if module_path.is_absolute():
        raise ValueError(f"Absolute paths are not allowed for security reasons: {path_str}")

    # Resolve path relative to project root
    full_path = (_PROJECT_ROOT / module_path).resolve()

    # Security check: ensure resolved path is under project_root/modules/
    modules_dir = (_PROJECT_ROOT / "modules").resolve()
    try:
        full_path.relative_to(modules_dir)
    except ValueError as err:
        raise ValueError(f"Access denied: Path must be under 'modules/' directory. Attempted: {path_str}") from err

    return full_path


def _read_module_file(file_path: Path, identifier: str, logger: logging.Logger) -> str:
    """
    Read module documentation file with error handling.

    Args:
        file_path: Absolute path to the module file
        identifier: Original identifier (for error messages)
        logger: Logger for debug logging

    Returns:
        File content as string

    Raises:
        ValueError: If file doesn't exist or cannot be read
    """
    if not file_path.exists():
        raise ValueError(f"Module file not found: {identifier}")

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        logger.debug(f"Read module documentation: {identifier}")
        return content
    except Exception as e:
        raise ValueError(f"Failed to read module file {identifier}: {e}") from e


# Logical section keys accepted by get_module's `sections` parameter, mapped
# to the canonical H2 headings used across the module documentation corpus.
_SECTION_ALIASES: dict[str, str] = {
    "description": "Description",
    "module-info": "Module Information",
    "features": "Key Features",
    "use-cases": "Main Use Cases",
    "examples": "Usage Examples",
    "usage": "Usage Examples",
    "inputs": "Main Input Variables",
    "variables": "Main Input Variables",
    "outputs": "Main Outputs",
    "submodules": "Submodules",
    "best-practices": "Best Practices",
    "gotchas": "Important Gotchas",
    "ai-notes": "Notes for AI Agents",
    "resources": "Additional Resources",
}

# Sections always included in a filtered get_module response: short, high-value
# context (version pins, agent guidance, gotchas) that must not be trimmed away.
_CORE_SECTIONS = ("Description", "Module Information", "Notes for AI Agents", "Important Gotchas")

# Logical keys whose canonical heading may be absent in docs that bundle the
# module interface differently (combined "Main Module:"/"Root Module:" sections,
# or pure submodule-collection docs). When such a key finds no exact heading,
# resolution falls back to the doc's interface-bearing section(s).
_INTERFACE_KEYS = frozenset({"inputs", "variables", "outputs", "examples", "usage"})

# Headings that carry a module's interface when the split scheme is not used:
# a combined root/main section, or numbered submodule sections.
_COMBINED_INTERFACE_PREFIXES = ("main module", "root module", "submodule")

# Passed in `sections` to bypass the compact orientation head and return the
# complete document (the pre-orientation default behaviour).
_FULL_DOC_KEYS = frozenset({"all", "full", "everything"})

# Default sections for the compact orientation head returned by get_module when
# no `sections` are requested: short, high-signal context. Core sections are
# always added on top by filter_module_sections; the footer lists the rest as a
# table of contents the agent can request next.
_ORIENTATION_KEYS = ("features", "use-cases")

_LATEST_VERSION_RE = re.compile(r"^\s*[-*]\s*\*\*Latest Version\*\*:\s*`?([^`\s]+)`?", re.MULTILINE)

_H2_RE = re.compile(r"^## .+$", re.MULTILINE)

# Interface key -> lowercase H3 sub-heading prefixes to extract from a combined
# "## Root Module:"/"## Submodule N:" bundle. Prefix (startswith) match absorbs
# singular/plural ("Usage Example"/"Usage Examples") and the "Main ..." phrasing.
# Outputs carry two house styles across the corpus: "Main Outputs" and "Key
# Outputs" (ecs) -- both must resolve.
_INTERFACE_H3_PREFIXES: dict[str, tuple[str, ...]] = {
    "inputs": ("main input variables",),
    "variables": ("main input variables",),
    "outputs": ("main output", "key output"),
    "examples": ("usage example",),
    "usage": ("usage example",),
}

_H3_RE = re.compile(r"^### .+$", re.MULTILINE)

# Valid values for filter_module_sections(interface_scope=...): "all" extracts
# interface H3s from every combined bundle (root + submodules); "root" restricts
# to the root/main bundle (used by the compact orientation head).
_INTERFACE_SCOPES = frozenset({"all", "root"})


def _matches_combined_interface(title_lower: str) -> bool:
    """True for headings that carry the interface outside the split scheme."""
    return title_lower.startswith(_COMBINED_INTERFACE_PREFIXES)


# Terraform's submodule-address separator: "<source>//modules/<sub>".
_SUBMODULE_SEP = "//"


def _parse_submodule_address(module_identifier: str) -> tuple[str, str] | None:
    """
    Parse a Terraform submodule address into ``(parent_name, submodule_name)``.

    Accepts the double-slash submodule form used in module sources so an agent
    can orient on a submodule in one call:

    - ``"iam//modules/iam-role"``                          -> ``("iam", "iam-role")``
    - ``"terraform-aws-modules/iam/aws//modules/iam-role"`` -> ``("iam", "iam-role")``
    - ``"iam//iam-role"``                                  -> ``("iam", "iam-role")``

    The left side may be a bare module name or a full ``ns/name/provider`` module
    id (its middle component is the name). The right side's last path component is
    the submodule name. Returns ``None`` when the identifier is not a submodule
    address (no ``//``), leaving normal name/path resolution unchanged.
    """
    if _SUBMODULE_SEP not in module_identifier:
        return None
    left, _, right = module_identifier.partition(_SUBMODULE_SEP)
    sub = right.strip().rstrip("/").split("/")[-1].strip()
    left = left.strip()
    # "modules" is the conventional submodule directory, never a submodule name —
    # reject "iam//modules" / "iam//modules/" so they fall back to normal resolution
    # instead of scoping to a bogus section.
    if not left or not sub or sub == "modules":
        return None
    if "/" in left:
        parts = [p for p in left.split("/") if p]
        # "ns/name/provider" -> the name is the middle component; fall back to last.
        parent = parts[1] if len(parts) >= 3 else parts[-1]
    else:
        parent = left
    return (parent, sub) if parent else None


def _version_pin_hint(text: str, version_override: str | None = None) -> str | None:
    """
    Build an actionable exact-pin line from the doc's `**Latest Version**` bullet.

    Agents that read only the module body tend to copy the `~> X.0` range shown
    in usage examples and pin a floor instead of the exact latest release. This
    surfaces the concrete version up front so an exact pin is the obvious choice.
    Returns None when the doc carries no parseable Latest Version bullet and no
    version_override was given.

    Args:
        text: The module document body.
        version_override: When truthy, used verbatim as the pinned version
            instead of re-parsing the body bullet (single-snapshot
            version consistency -- lets a caller thread in the same metadata
            field it also reports elsewhere, so the two can never contradict
            each other in one response).
    """
    if version_override:
        version = version_override.strip()
    else:
        m = _LATEST_VERSION_RE.search(text)
        if not m:
            return None
        version = m.group(1).strip()
    major = version.split(".")[0]
    return (
        f"> **Version pin** — latest release is `{version}`. For an exact pin use "
        f'`version = "{version}"`; use a range like `~> {major}.0` only when you '
        f"deliberately want automatic minor-version updates."
    )


def _reconcile_body_version(text: str, resolved: str | None) -> str:
    """Rewrite every body ``**Latest Version**`` bullet to the resolved snapshot.

    Single-snapshot consistency, applied to ALL version mentions: the pin
    banner is synced with the caller-threaded metadata ``latest_version``,
    but the curated doc body still carries its own ``**Latest Version**`` bullet
    that can be stale and contradict both the banner and ``results[].latest_version``
    in the same response. When a caller threads a resolved snapshot, rewrite the
    body bullet's version token to match it so one response never self-contradicts.

    Drift-safe by construction: this rewrites the *emitted* text only -- the
    indexed document body (and therefore the embeddings) is untouched. No-op when
    ``resolved`` is falsy or the text carries no parseable bullet.
    """
    if not resolved:
        return text
    resolved = resolved.strip()

    def _sub(m: re.Match[str]) -> str:
        # Replace only the captured version token within the matched bullet span,
        # leaving the bullet's markup and any backticks intact.
        return m.group(0).replace(m.group(1), resolved)

    return _LATEST_VERSION_RE.sub(_sub, text)


def _split_h2_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Split a module document into preamble and H2 sections.

    Args:
        text: Full markdown document text

    Returns:
        Tuple of (preamble, sections). Preamble is everything before the first
        H2 heading (front-matter, title, keywords). Sections is a list of
        (heading_title, block_text) in document order, where block_text
        includes the heading line and runs until the next H2 or end of file.
    """
    matches = list(_H2_RE.finditer(text))
    if not matches:
        return text, []
    preamble = text[: matches[0].start()]
    sections: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        title = m.group(0)[3:].strip()
        sections.append((title, text[m.start() : end]))
    return preamble, sections


def _extract_interface_h3(block: str, keys: set[str]) -> str:
    """
    From one combined H2 bundle, return its heading line plus only the H3
    sub-sections whose title matches the requested interface keys.

    Args:
        block: A single "## Root Module:"/"## Submodule N:" bundle (heading + body).
        keys: Interface keys (subset of _INTERFACE_H3_PREFIXES).

    Returns:
        The H2 heading line followed by the matching "### ..." sub-blocks in
        document order, or "" when no sub-section matches.
    """
    prefixes = tuple(p for k in keys for p in _INTERFACE_H3_PREFIXES.get(k, ()))
    if not prefixes:
        return ""
    matches = list(_H3_RE.finditer(block))
    if not matches:
        return ""
    # The bundle's "## ..." heading is whatever precedes the first H3; empty when
    # the block itself starts with an H3 (no enclosing H2 preamble).
    pre = block[: matches[0].start()].splitlines()
    heading_line = pre[0] if pre else ""
    kept: list[str] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
        title = m.group(0)[4:].strip().lower()
        if title.startswith(prefixes):
            kept.append(block[m.start() : end].rstrip())
    if not kept:
        return ""
    return heading_line.rstrip() + "\n\n" + "\n\n".join(kept)


def filter_module_sections(
    text: str,
    requested: list[str],
    *,
    extra_exact_titles: tuple[str, ...] = (),
    interface_scope: str = "all",
    silent_keys: frozenset[str] = frozenset(),
) -> str:
    """
    Reduce a module document to core sections plus the requested ones.

    Each requested entry is either a logical key from _SECTION_ALIASES
    (e.g. "inputs", "examples", "submodules") or a free-form case-insensitive
    substring matched against H2 headings (e.g. "karpenter" to fetch a single
    EKS submodule section). Core sections — front-matter, Description,
    Module Information, Notes for AI Agents, and Important Gotchas (the last
    only on docs that carry that heading) — are always included regardless of
    the request. A footer lists the omitted sections (serving as a table of
    contents) and any requested entries that matched nothing.

    Args:
        text: Full markdown document text
        requested: Section keys or heading substrings to include
        extra_exact_titles: Additional H2 titles to always include, matched by
            case-insensitive equality (not substring/prefix). Used by the
            orientation head to inline the exact ``## Submodules`` inventory
            heading without dragging in the ``## Submodule N:`` deep-dives.
        interface_scope: "all" (default) or "root". When an interface key
            (inputs/variables/outputs/examples/usage) falls back to extracting
            H3 sub-sections from combined bundles, "root" restricts that
            extraction to the ``## Root Module:``/``## Main Module:`` bundle
            and skips ``## Submodule N:`` bundles.
        silent_keys: Requested keys (lowercased) that should not be reported
            in the "Requested sections not found" footer line when unmatched.

    Returns:
        Filtered document text; the original text if it has no H2 sections

    Raises:
        ValueError: If interface_scope is not "all" or "root"
    """
    if interface_scope not in _INTERFACE_SCOPES:
        raise ValueError(f"interface_scope must be one of {sorted(_INTERFACE_SCOPES)}, got {interface_scope!r}")
    preamble, sections = _split_h2_sections(text)
    if not sections:
        return text

    extra_lower = {t.lower() for t in extra_exact_titles}
    wanted: set[str] = {title for title, _ in sections if title in _CORE_SECTIONS or title.lower() in extra_lower}
    unmatched: list[str] = []
    # Interface keys that found no exact H2 alias fall back to extracting their
    # H3 sub-section(s) from the combined "Root/Main Module:"/"Submodule N:"
    # bundles, rather than dragging in the whole bundle (the BUG-1 over-fetch).
    fallback_keys: set[str] = set()
    # L5: when the caller explicitly asks for the submodules inventory, the
    # interface-key H3 fallback below must not re-expand "## Submodule N:"
    # bundles either. The compact inventory answers "what submodules exist"; a
    # specific submodule interface is reached by its "<name>//modules/<sub>"
    # address or by naming its heading. Full exclusion of the deep-dives.
    submodules_requested = any(_SECTION_ALIASES.get(e.strip().lower()) == "Submodules" for e in requested)
    for entry in requested:
        key = entry.strip().lower()
        if not key:
            continue
        canonical = _SECTION_ALIASES.get(key)
        matched = False
        for title, _ in sections:
            if canonical is not None:
                # L5: the "submodules" key resolves to the compact "## Submodules"
                # inventory by EXACT title match only. Matching "## Submodule N:"
                # deep-dives here was the over-fetch -- a specific submodule is
                # reached by heading substring or the "<name>//modules/<sub>"
                # address instead.
                hit = title == canonical
            else:
                hit = key in title.lower()
            if hit:
                wanted.add(title)
                matched = True
        # Fallback: the corpus is heterogeneous — some docs bundle inputs/outputs/
        # examples into a combined "Main Module:"/"Root Module:" section or spread
        # them across numbered submodule sections instead of the split scheme the
        # aliases target. When an interface key resolves to no exact heading, fall
        # back to those interface-bearing sections rather than reporting it missing.
        if not matched and key in _INTERFACE_KEYS:
            combined_titles: list[str] = []
            for title, block in sections:
                tl = title.lower()
                if not _matches_combined_interface(tl):
                    continue
                if (interface_scope == "root" or submodules_requested) and tl.startswith("submodule"):
                    continue
                combined_titles.append(title)
                if _extract_interface_h3(block, {key}):
                    fallback_keys.add(key)
                    matched = True
            # Safety net: a combined-interface section exists but carries no
            # matching H3 sub-section (e.g. network-firewall documents its
            # interface as H3 entries under "## Submodules", not as a
            # "### Main Input Variables" table). Include those section(s) whole so
            # the standard interface key still resolves rather than reporting
            # missing. Well-structured combined docs never reach here — their H3
            # extraction above succeeds, so no whole-bundle over-fetch returns.
            if not matched and combined_titles:
                wanted.update(combined_titles)
                matched = True
        if not matched and key not in silent_keys:
            unmatched.append(entry)

    parts = [preamble.rstrip()] if preamble.strip() else []
    for title, block in sections:
        if title in wanted:
            parts.append(block.rstrip())
            continue
        tl = title.lower()
        if fallback_keys and _matches_combined_interface(tl):
            if (interface_scope == "root" or submodules_requested) and tl.startswith("submodule"):
                continue
            extracted = _extract_interface_h3(block, fallback_keys)
            if extracted:
                parts.append(extracted)

    # Always advertise the complete section inventory so the agent has an explicit
    # menu for follow-up get_module(sections=[...]) calls — not just what was
    # omitted from this particular response.
    all_titles = [title for title, _ in sections]
    omitted = [title for title in all_titles if title not in wanted]

    footer_lines = [
        "---",
        # Compact honest-limits pointer. The curated doc is a hand-picked
        # SUBSET; anything requiring completeness/exactness escalates one tier to
        # the live registry, and resource-creation conditions live in module
        # source. Keeps the compact→full→source escalation a mechanical decision,
        # not a guess, without repeating a long paragraph verbatim on every call.
        "Curated subset. For the COMPLETE inputs/outputs (exact types/defaults, nested "
        "map(object)/any TYPE/SHAPE) or to confirm a name exists, grep the live doc via "
        "`grep_module_docs` using the Module ID above. Resource-creation (`count`/`for_each`) "
        "conditions live in the module source, not here.",
        "Available sections (request any via `get_module`'s `sections` parameter — "
        "logical keys: inputs, outputs, examples, submodules, features, use-cases, "
        "best-practices, resources; or a case-insensitive heading substring): " + "; ".join(all_titles),
    ]
    if omitted:
        footer_lines.append("Not included above (request to expand): " + "; ".join(omitted))
    if unmatched:
        footer_lines.append("Requested sections not found: " + ", ".join(unmatched))
    parts.append("\n".join(footer_lines))

    return "\n\n".join(parts) + "\n"


def get_module_documentation(module_identifier: str, state: ServerState) -> str:
    """
    Helper function to retrieve module documentation.

    This function is testable (not decorated) and can be called directly
    with a ServerState instance for testing.

    Args:
        module_identifier: Module name or relative file path
        state: Server state containing index and configuration

    Returns:
        Full module documentation text

    Raises:
        ValueError: If module not found or path invalid/insecure

    See get_module() resource documentation for full details.
    """
    assert state.logger is not None, "ServerState must have a logger"  # noqa: S101

    # Determine strategy based on identifier format
    is_path = "/" in module_identifier or module_identifier.endswith(".md")

    if is_path:
        # Strategy 1: Direct file path access
        full_path = _validate_and_resolve_module_path(module_identifier)
        return _read_module_file(full_path, module_identifier, state.logger)

    # Strategy 2: Lookup by module name — exact match first, then a unique
    # substring match. Unknown names raise with suggestions instead of
    # silently returning the highest-scoring search hit.
    identifier = normalize_modname(module_identifier)
    named_docs = [doc for doc in state.index.docs if doc.module_name]

    matches = [doc for doc in named_docs if doc.module_name == identifier]
    if not matches:
        matches = [doc for doc in named_docs if identifier in doc.module_name or doc.module_name in identifier]

    if len(matches) != 1:
        weights = state.weights
        results = compute_scores(
            state.index,
            module_identifier,
            w_kw=weights.w_kw,
            w_exact=weights.w_exact,
            w_bm25=weights.w_bm25,
            w_sem=weights.w_sem,
            top_k=3,
            query_instruction=state.query_instruction,
            logger=state.logger,
        )
        suggestions = ", ".join(state.index.docs[doc_idx].module_name or "?" for _, doc_idx in results)
        kind = "Ambiguous" if matches else "No"
        raise ValueError(
            f"{kind} module name: '{module_identifier}'. Closest matches: {suggestions}. "
            f"Use search_modules to find the right module, then call get_module "
            f"with its exact name or path."
        )

    doc = matches[0]
    full_path = (_PROJECT_ROOT / doc.path).resolve()
    return _read_module_file(full_path, doc.module_name or doc.path, state.logger)


def _clip_blurb(text: str, max_length: int = 140) -> str:
    """Clip a description to its first sentence, capped at max_length chars.

    Used for non-top-1 search hits (L6): enough to recognize the module, without
    re-billing the full description on every later turn.
    """
    text = text.strip()
    if not text:
        return text
    period = text.find(". ")
    if 0 < period + 1 <= max_length:
        return text[: period + 1]
    if len(text) <= max_length:
        return text
    # Clip on a word boundary, never mid-word. A hard char cut left a
    # dangling partial word in every non-top-1 result row.
    clipped = text[: max_length - 1].rstrip()
    return clipped.rsplit(" ", 1)[0] + "…"


# Floor on the raw (pre-min-max) semantic similarity - the secondary
# demoter behind the capability-coverage check. It catches the
# incidental-keyword case: an unrelated module lists the query term in its
# own keyword line, earning full coverage without the query being covered
# semantically. Measured on production weights: genuine matches and
# marginal catalog gaps overlap near this value, so it is a PARTIAL
# signal - do not raise it to chase gaps; coverage and the score floor
# carry the wrong-domain load.
SEARCH_SEM_FLOOR = 0.88

# Floor on the combined (displayed) score. SEARCH_SCORE_FLOOR = 2.9.
# Derivation: golden-set score distribution, 2026-07-17.
#
# Under production weights, the ranker's min-max normalization pins the
# top-1 combined score at >= 3.0 in both the no-keyword-match branch and
# the multi-keyword-match branch, so this floor can fire only in the
# single-matched-keyword branch (the one branch whose normalization can
# legitimately land as low as 3.0 for a genuinely correct match). The
# primary guard for no-evidence queries is the out-of-vocabulary rule in
# _capability_coverage (an unknown, uncovered term now participates at the
# corpus's maximum IDF weight instead of being dropped, so it can drag
# coverage below theta on its own); the raw-semantic floor above is the
# secondary guard. This floor is retained as a conjunct for non-default
# weight configurations and for the single-keyword branch, where it still
# has room to act. A residual low-score false-high class (an incidental
# keyword line that is not a real capability) stays a known, documented
# limitation -- coverage and the sem floor carry that load, not this one.
SEARCH_SCORE_FLOOR = 2.9

# Generic infrastructure words that can score a high IDF in a Terraform
# catalog yet carry no capability signal -- never treat one as the query's
# central capability term when deciding capability coverage.
_CAPABILITY_STOPWORDS = frozenset(
    {
        "aws",
        "terraform",
        "module",
        "modules",
        "resource",
        "resources",
        "infrastructure",
        "cloud",
        "service",
        "services",
    }
)

# General English function words: connectors, prepositions, pronouns, and
# politeness filler that carry no capability signal in any domain. Filtered
# out of the capability-coverage token set alongside _CAPABILITY_STOPWORDS
# (catalog-domain filler) so a query's incidental "and"/"for"/"with" cannot
# be mistaken for -- or incidentally match -- a real capability term.
_ENGLISH_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "but",
        "by",
        "can",
        "do",
        "for",
        "from",
        "has",
        "have",
        "how",
        "i",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "up",
        "us",
        "use",
        "using",
        "via",
        "want",
        "was",
        "we",
        "what",
        "when",
        "where",
        "which",
        "who",
        "will",
        "with",
        "without",
        "you",
        "your",
        "need",
    }
)


# Two-tier capability evidence weights. A term asserted in a capability
# field (module name, keywords, or the module's own "## Description"
# section) counts in full; a term that only appears somewhere in the doc
# body is a mention, not a capability, and counts at a fraction. Coverage
# below the threshold means the candidate does not assert the asked
# capability.
_COVERAGE_ALPHA = 0.3
_COVERAGE_THETA = 0.5


def _field_parts(*field_strings: str) -> set[str]:
    """Lowercase alphanumeric runs from capability field strings.

    "jwt-authorizer" contributes {"jwt", "authorizer"}; "in-memory"
    contributes {"in", "memory"}. Splitting keywords and names into parts
    lets split query tokens match hyphenated catalog vocabulary.
    """
    parts: set[str] = set()
    for s in field_strings:
        run = ""
        for ch in s.lower():
            if ch.isalnum():
                run += ch
            elif run:
                parts.add(run)
                run = ""
        if run:
            parts.add(run)
    return parts


def _token_matches_parts(token: str, parts: set[str]) -> bool:
    """Token-vs-field-part match: equality, trailing-plural tolerance, or
    prefix tolerance for tokens/parts of length >= 5 (no mid-word
    substrings - "ui" must not match inside "guide").

    The plural-strip equality only fires when the stripped token has length
    >= 3, so short function words are never conflated with a shorter stem
    ("as" -> "a", "its" -> "it"). The prefix tolerance requires both sides
    to be at least 5 characters (raised from 4): at 4 chars it let unrelated
    words absorb each other ("base"/"based", "data"/"database",
    "auto"/"automatic", "with"/"without").

    Hyphenated-compound symmetry: _field_parts already splits FIELD strings
    ("jwt-authorizer" -> {"jwt", "authorizer"}) into alnum runs, but a query
    TOKEN that is itself a hyphenated compound written as one tokenizer
    token ("auto-scaling-group" -- tokenize() does not split on hyphens)
    never got the same treatment, so it could only ever strong-match via
    the prefix-tolerance branch matching one run at a time -- exactly what
    the old, since-tightened 4-char prefix bound was accidentally providing.
    When the token contains punctuation, it is split into its own alnum
    runs (len >= 2) and matches only when EVERY run matches `parts` via
    these same rules -- a partial compound match ("data-warehouse" against
    just "data") is not evidence of coverage.
    """
    if token in parts:
        return True
    singular = token.rstrip("s")
    for part in parts:
        if len(singular) >= 3 and singular == part.rstrip("s"):
            return True
        if len(token) >= 5 and len(part) >= 5 and (token.startswith(part) or part.startswith(token)):
            return True
    if any(not ch.isalnum() for ch in token):
        runs = {r for r in _field_parts(token) if len(r) >= 2}
        if runs and all(_token_matches_parts(r, parts) for r in runs):
            return True
    return False


def _capability_description_text(text: str) -> str:
    """Text of the module's own ``## Description`` H2 section, for capability
    coverage's strong-evidence field.

    ``extract_description()`` (tfmod_search_lib) is a header-skip-then-
    first-N-chars heuristic tuned for the search-result blurb. On every
    catalog doc the ``## Module Information`` bullets precede
    ``## Description`` and consume its 200-char budget before the real
    prose is ever reached (measured: 0/55 docs), making it an inert, noisy
    strong-evidence source for coverage specifically. This helper instead
    reads the actual ``## Description`` section body via
    ``_split_h2_sections`` (exact-title match, the same idiom
    ``_CORE_SECTIONS`` uses) -- a genuine capability-asserting source.

    This is a coverage-mechanism-only fix: the search-result ``description``
    field (the response body) still uses ``extract_description`` directly
    and is untouched.

    Falls back to ``extract_description(text)`` when the doc has no exact
    ``## Description`` H2 heading, preserving the prior fail-open behavior
    on non-standard docs.
    """
    _, sections = _split_h2_sections(text)
    for title, block in sections:
        if title == "Description":
            body = block.split("\n", 1)[1] if "\n" in block else ""
            return body.strip()
    return extract_description(text)


def _capability_coverage(query: str, index: SearchIndex, doc_index: int) -> float:
    """IDF-weighted fraction of the query's capability terms the candidate
    doc asserts.

    Evidence strength per content token: 1.0 when it matches the module
    name, keywords, or the module's ``## Description`` section text (fields
    that assert capability); _COVERAGE_ALPHA when it only appears somewhere
    in the body on a word boundary (a mention is not a capability); 0.0 when
    absent. Weighted by corpus IDF so rare, query-defining terms dominate.

    Out-of-corpus tokens (idf <= 0, i.e. absent from the corpus IDF table)
    are NOT dropped: they participate at the corpus's MEAN IDF weight (C1
    calibration, 2026-07-17 -- capped down from the corpus max), since an
    unknown term is exactly the kind of query-defining vocabulary the
    catalog may not serve -- if it matches nothing, that is evidence of a
    miss, not a reason to discount it entirely. The mean, not the max, is
    the principled prior for an unknown word's rarity ("typical", not "as
    rare as the single rarest word in the whole corpus"): weighting at the
    max measurably overweighed a single informal/slang/typo token enough to
    demote otherwise-correct, otherwise-fully-covered queries ("pls create
    s3 bucket", "hey i need a postgres database asap") to a false "low".

    Two conditions are checked before scoring, in order:
    1. An empty/absent corpus IDF table (degraded index) -- cannot judge
       coverage either way, so this fails OPEN to 1.0.
    2. An empty content-token set after filtering stopwords (a contentless
       query: "", "?", "please help", "aws terraform") -- no evidence to
       trust, so this fails CLOSED to 0.0. The whole-query-exact check in
       _classify_confidence (rule step 1) still catches a bare module name
       before coverage ever runs, so this cannot demote that case.
    """
    tokens = {
        t
        for t in tokenize(query)
        if len(t) >= 2
        and t not in _CAPABILITY_STOPWORDS
        and t not in _ENGLISH_STOPWORDS
        and any(c.isalnum() for c in t)
    }
    idf = getattr(index.bm25, "idf", None) or {}
    if not idf:
        return 1.0
    if not tokens:
        return 0.0
    mean_idf = sum(idf.values()) / len(idf)
    weighted = [(t, idf.get(t, 0.0) if idf.get(t, 0.0) > 0.0 else mean_idf) for t in tokens]
    doc = index.docs[doc_index]
    strong = _field_parts(doc.module_name or "", *(doc.keywords or []), _capability_description_text(doc.text))
    body = doc.text.lower()
    total = 0.0
    covered = 0.0
    for t, w in weighted:
        total += w
        if _token_matches_parts(t, strong):
            covered += w
        elif re.search(rf"\b{re.escape(t)}\b", body):
            covered += w * _COVERAGE_ALPHA
    return covered / total


def _classify_confidence(query: str, hits: list[ScoredHit], index: SearchIndex) -> str:
    """Classify a search into the confidence verdict that also decides the inline.

    Two-verdict design ("high" / "low"); the caller inlines the top-1
    orientation head iff the verdict is "high", so "high => doc inlined"
    holds by construction.

    Decision (top-1 only):
    0. No hits -> "high" (nothing to contest; the caller inlines nothing).
    1. The whole normalized query IS the top-1 module name -> "high".
       Typing exactly a module name is the strongest assertion of intent.
    2. Capability coverage below _COVERAGE_THETA -> "low": the module does
       not assert the asked capability in its name, keywords, or
       description (body-only mentions count fractionally).
    3. Raw semantic similarity below SEARCH_SEM_FLOOR -> "low": guards the
       incidental-keyword case where coverage passes on a foreign keyword.
    4. Combined score below SEARCH_SCORE_FLOOR -> "low": low-scoring
       candidates do not earn an inline even with plausible coverage.
    5. Otherwise -> "high".

    The verdict deliberately does NOT depend on whether the query contains
    the module name as one of its words: a capability search from a user
    who does not know the module name is exactly the case the verdict
    exists for, and a name token inside a longer query proves nothing
    about the remaining terms.
    """
    if not hits:
        return "high"
    top1 = hits[0]
    if index.docs[top1.doc_index].module_name == normalize_modname(query):
        return "high"
    if _capability_coverage(query, index, top1.doc_index) < _COVERAGE_THETA:
        return "low"
    if top1.sem_sim < SEARCH_SEM_FLOOR:
        return "low"
    if top1.score < SEARCH_SCORE_FLOOR:
        return "low"
    return "high"


def search_modules_impl(query: str, state: ServerState, top_k: int = 3, expand_top: bool = True) -> SearchOutput:
    """
    Helper function to search for modules.

    This function is testable (not decorated) and can be called directly
    with a ServerState instance for testing.

    Args:
        query: Search query string
        state: Server state containing index and configuration
        top_k: Number of results to return (clamped to 1..10, default 3)
        expand_top: When True AND the search is high confidence, inline the
            top-1 module orientation head into the response (L3) -- collapses
            a confident search->get_module pair into one call. Defaults to
            True: leaving this opt-in left the one clearly right-direction
            lever mostly unused, and the residency cost of the ~1.5K-char
            head is small next to the cost of spending a whole extra turn on
            a follow-up get_module call. Pass expand_top=False to suppress it
            (pure-browse searches). Inlined iff the verdict is "high"
            (verdict and inline are one decision -- the capability-aware
            classifier demotes a wrong-domain top hit to "low" before it can
            drag its doc into context, so "high" reliably means the inlined
            doc is on-target).

    Returns:
        SearchOutput with top-k ranked results plus a confidence verdict
        (L2/L7/L8/T3): "high" (trust the top hit) or "low" (no confident
        catalog match). A hint accompanies a "low" verdict and is absent from
        the JSON output when confidence is "high". top_module_doc (L3) is
        populated by default whenever confidence == "high"; absent from the JSON
        output when expand_top=False or confidence is "low".

    See search_modules() tool documentation for full details.
    """
    assert state.logger is not None, "ServerState must have a logger"  # noqa: S101

    top_k = max(1, min(int(top_k), 10))

    # Use configured weights from state
    weights = state.weights
    # Always fetch at least 2 hits internally even when the caller asked for
    # top_k=1, so a rank-2 hit is available to callers/tests that inspect the
    # raw hits list. The confidence classifier reads only hits[0] (whole-query
    # exact-name match, capability coverage, sem_sim, and score of the top
    # doc) -- there is no ratio against rank-2.
    fetch_k = max(top_k, 2)
    hits = compute_scores_detailed(
        state.index,
        query,
        w_kw=weights.w_kw,
        w_exact=weights.w_exact,
        w_bm25=weights.w_bm25,
        w_sem=weights.w_sem,
        top_k=fetch_k,
        query_instruction=state.query_instruction,
        logger=state.logger,
    )

    confidence = _classify_confidence(query, hits, state.index)
    if hits:
        if state.logger.isEnabledFor(logging.DEBUG):
            cov = _capability_coverage(query, state.index, hits[0].doc_index)
            state.logger.debug(
                f"top1 sem_sim={hits[0].sem_sim:.4f} score={hits[0].score:.3f} "
                f"coverage={cov:.3f} verdict={confidence} inline={confidence == 'high'}"
            )
    else:
        state.logger.debug(f"no hits verdict={confidence}")
    hint: str | None = None
    if hits and confidence == "low":
        top1_name = state.index.docs[hits[0].doc_index].module_name or "?"
        hint = (
            f"No confident catalog match (top score {hits[0].score:.1f}). Confirm absence with "
            f"modules_list, or try grep_module_docs on the nearest module '{top1_name}' for the "
            f"capability keyword."
        )

    # L3: inline the top-1 orientation head iff the verdict is "high". The
    # verdict itself (capability coverage, semantic floor, score floor) now
    # decides both the reported confidence and the inline -- one signal, so
    # the "high => doc inlined" contract in the docstring holds and a
    # wrong-domain top hit is demoted to "low" before it can drag its doc
    # into context.
    top_module_doc: str | None = None
    if expand_top and confidence == "high" and hits:
        top_doc = state.index.docs[hits[0].doc_index]
        # Thread the same metadata field reported in results[].latest_version
        # into the head's version pin, so the two can never contradict each other in
        # one response (the body-bullet re-parse and the metadata field can drift
        # apart after a metadata-only patch).
        top_module_doc = orientation_head(top_doc.text, version_override=top_doc.latest_version)

    results = hits[:top_k]

    out: list[SearchHit] = []
    for rank, hit in enumerate(results):
        score, i = hit.score, hit.doc_index
        d = state.index.docs[i]
        # L6: only the top hit carries the full keyword array and description.
        # Lower ranks re-bill on every later turn but nothing reads their keyword
        # arrays, so they get an empty list and a first-sentence-clipped blurb.
        if rank == 0:
            keywords = d.keywords or []
            description = extract_description(d.text)
        else:
            keywords = []
            description = _clip_blurb(extract_description(d.text))

        out.append(
            SearchHit(
                module_name=d.module_name or "",
                path=d.path,
                keywords=keywords,
                description=description,
                score=float(score),
                module_id=getattr(d, "module_id", ""),
                latest_version=getattr(d, "latest_version", ""),
            )
        )

    state.logger.debug(f"Search for '{query}' returned {len(out)} results (confidence={confidence})")
    return SearchOutput(results=out, confidence=confidence, hint=hint, top_module_doc=top_module_doc)


_INPUT_TABLE_HEADING_RE = re.compile(r"^### Main Input Variables[ \t]*$", re.MULTILINE)
_TABLE_ROW_RE = re.compile(r"^\|.*\|[ \t]*$")
_TABLE_SEPARATOR_RE = re.compile(r"^\|[ \t:-]+\|[ \t:|:-]*$")
_MIN_HEAD_TABLE_ROWS = 8


def _split_table_row(row: str) -> list[str]:
    """Split a Markdown pipe-table row into stripped cells (drops the outer pipes)."""
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def _cell_marks_required(cell: str) -> bool:
    """True when a Default-column cell signals the input has no default (required)."""
    bare = cell.strip().strip("*").strip("`").strip().lower()
    return bare in ("", "-", "—", "n/a") or "required" in bare


def _cell_marks_required_column(cell: str) -> bool:
    """True when a Required-column cell signals the input is required."""
    bare = cell.strip().strip("*").strip("`").strip().lower()
    return bare in ("yes", "true", "required")


def _cap_head_input_table(head_text: str) -> str:
    """
    Cap the FIRST inlined ``### Main Input Variables`` table to a bounded sample.

    L4: the 0.20.0 double-fetch fix inlined the whole root input table into the
    default orientation head, growing it substantially on modules with wide
    interfaces. The kept sample is the first ``_MIN_HEAD_TABLE_ROWS`` rows (the
    terraform-aws-modules docs front-load the inputs that matter) PLUS any row
    the doc explicitly marks required that falls outside that window, so a
    required input is never hidden. A pointer to the full table is appended and
    rows keep document order.

    Note on the corpus: almost every terraform-aws-modules input carries a
    concrete or ``null`` default, so the required-row detection (an empty/``-``/
    ``n/a`` Default cell, a ``Required``/``*required*`` marker, or a ``Yes`` in a
    separate Required column) only adds rows on the handful of docs that mark
    inputs required — for the rest this is simply the leading-N sample. Either
    way the head stays small and never empty, and the complete table is one
    ``sections=["inputs"]`` call away.

    This is a pure post-process on already-rendered Markdown: on any parse
    ambiguity (no heading, no recognizable pipe table, no identifiable
    Default/Required column) it returns ``head_text`` unchanged rather than
    guessing. Only the first occurrence of the heading is touched — a doc that
    happens to inline more than one is left alone past the first.
    """
    heading_match = _INPUT_TABLE_HEADING_RE.search(head_text)
    if heading_match is None:
        return head_text

    lines = head_text.splitlines(keepends=True)
    # Locate the heading's line index.
    heading_line_idx = head_text.count("\n", 0, heading_match.start())

    # Scan forward for the first non-blank line after the heading — it must be
    # the table header row, else this is not the table shape we recognize.
    idx = heading_line_idx + 1
    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1
    if idx >= len(lines) or not _TABLE_ROW_RE.match(lines[idx].rstrip("\n")):
        return head_text
    header_line_idx = idx
    header_cells = _split_table_row(lines[header_line_idx])

    sep_idx = header_line_idx + 1
    if sep_idx >= len(lines) or not _TABLE_SEPARATOR_RE.match(lines[sep_idx].rstrip("\n")):
        return head_text

    # Identify the Default/Required column via the header, never a hardcoded index.
    lower_headers = [c.lower() for c in header_cells]
    if "default" in lower_headers:
        col_idx = lower_headers.index("default")
        is_required = _cell_marks_required
    elif "required" in lower_headers:
        col_idx = lower_headers.index("required")
        is_required = _cell_marks_required_column
    else:
        return head_text

    # Collect contiguous data rows following the separator.
    row_start = sep_idx + 1
    row_end = row_start
    data_rows: list[str] = []
    while row_end < len(lines) and _TABLE_ROW_RE.match(lines[row_end].rstrip("\n")):
        data_rows.append(lines[row_end])
        row_end += 1

    if not data_rows:
        return head_text

    required_rows = []
    for row in data_rows:
        cells = _split_table_row(row)
        if col_idx >= len(cells):
            continue
        if is_required(cells[col_idx]):
            required_rows.append(row)

    # Bounded orientation sample: the leading rows, plus any required rows the doc
    # marks that fall outside that window (so a required input is never hidden),
    # in document order. On docs that mark nothing required this is exactly the
    # leading-N sample.
    keep_set = set(data_rows[:_MIN_HEAD_TABLE_ROWS]) | set(required_rows)
    kept_rows = [row for row in data_rows if row in keep_set]

    dropped = len(data_rows) - len(kept_rows)
    if dropped <= 0:
        return head_text

    pointer_line = f'_(+{dropped} more inputs — get_module(sections=["inputs"]) for the full table)_\n'
    new_lines = lines[:row_start] + kept_rows + [pointer_line] + lines[row_end:]
    return "".join(new_lines)


# --------------------------------------------------------------------------- #
# any-shape overlay (examples-primary) -- serve the committed per-module
# any-var overlay (model/any_overlay/<id>.json, built by
# scripts/build_any_overlay.py) on the EXISTING serve path, without touching
# the render subsystem (filter_module_sections/_split_h2_sections/the head
# caps above are all untouched). Design (authoritative for the mechanics
# below): evals/specs/2026-07-20-consolidated-interface-any-overlay-design.md,
# "Integration" section.
#
# Committed overlay = static build-time data -> a plain file read, never a
# network call. get_module's network-decoupled contract is preserved by
# construction: live Registry access stays confined to grep_module_docs.
# --------------------------------------------------------------------------- #

_ANY_OVERLAY_DIR = _PROJECT_ROOT / "model" / "any_overlay"

# Per-var example cap (spec token policy: "smallest-covering example, per-var
# cap ~2k chars, fuller example -> grep_module_docs trailer").
_ANY_OVERLAY_EXAMPLE_CHAR_CAP = 2000

# Cell-substitution-only pointer for the default orientation HEAD (never the
# example/field-list themselves -- that would blow the head's token budget).
# No "below" wording: the head has nothing "below" it to point at.
_ANY_TYPE_HEAD_POINTER = 'any — see sections=["inputs"]'

# Reused for module_id resolution straight from raw doc text (an explicit
# Module ID bullet, falling back to the root Source bullet) -- the exact same
# fallback get_module/search_modules already rely on for module_id/
# latest_version, so any-overlay filename lookup can never disagree with
# those fields. A logger is required by the constructor, but
# parse_module_info() itself never logs.
_ANY_OVERLAY_INFO_PARSER = ModuleDocumentParser(logging.getLogger(__name__))


def _resolve_overlay_module_id(text: str) -> str:
    """Best-effort module_id parsed straight from `text`, for any-overlay
    filename resolution only. Pure text parsing -- no network, no index/state
    dependency -- so this works uniformly whether the doc arrived via
    name/path/submodule-address lookup. Empty string when unparseable."""
    return _ANY_OVERLAY_INFO_PARSER.parse_module_info(text).module_id


def _any_overlay_path(module_id: str) -> Path:
    return _ANY_OVERLAY_DIR / (module_id.replace("/", "__") + ".json")


def _load_any_overlay(module_id: str) -> dict[str, Any] | None:
    """
    Read the committed any-overlay JSON for `module_id`, if one exists.

    Static file read only (scripts/build_any_overlay.py's committed output) --
    never a network call. Fails closed to None on anything unexpected: no
    module_id, missing file, unreadable, malformed JSON, or the wrong shape --
    the caller then serves the honest `any` exactly as it did before this
    feature existed. A broken/missing overlay is never a hard error for
    get_module; only ~30 of the 63 catalog modules have any `any` inputs at
    all, so None is the overwhelmingly common case.
    """
    if not module_id:
        return None
    path = _any_overlay_path(module_id)
    try:
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("vars"), dict):
        return None
    return data


def _cap_any_overlay_example(example: str) -> tuple[str, bool]:
    """Cap one example block to _ANY_OVERLAY_EXAMPLE_CHAR_CAP chars (token
    policy). Returns (possibly-truncated text, whether it was truncated)."""
    if len(example) <= _ANY_OVERLAY_EXAMPLE_CHAR_CAP:
        return example, False
    return example[:_ANY_OVERLAY_EXAMPLE_CHAR_CAP].rstrip(), True


def _render_any_overlay_var_block(scope_var: str, entry: dict[str, Any], built_from_version: str) -> str:
    """
    One appendix block for a single overlay var: the verbatim example(s) as
    fenced HCL, the observed-field-name list, and a provenance tag. Rendered
    regardless of provenance -- even "honest-any" (no example, no names)
    still gets a block, carrying its note -- so no overlay var is ever
    silently dropped.

    The SHARED honesty labels (the example-provenance sentence, the
    field-name disclaimer, and the version-skew notice -- mandatory per the
    design's "Honesty labels" section) are identical for every var in one
    module (same built_from_version, same doc pin), so they are rendered
    ONCE in the appendix intro instead (see _render_any_overlay_appendix)
    rather than repeated here -- on a module with ~20 any-vars (e.g.
    s3-bucket) that repetition was the dominant token cost of the appendix.
    No honesty loss: every label still appears, just once per appendix
    instead of once per var.
    """
    scope, _, var_name = scope_var.partition("::")
    scope = scope or "root"
    provenance = entry.get("provenance")
    header = f"**any-overlay `{var_name}`** (scope: {scope}; type = `any`"
    header += f"; provenance: {provenance})" if provenance else ")"
    lines = [header + ":"]

    examples = entry.get("examples") or []
    field_names = entry.get("field_names") or []

    for example in examples:
        capped, truncated = _cap_any_overlay_example(example)
        lines.append(f"```hcl\n{capped}\n```")
        if truncated:
            lines.append(
                f"_(truncated at {_ANY_OVERLAY_EXAMPLE_CHAR_CAP} chars -- fuller example in "
                "examples/<dir> -- grep_module_docs)_"
            )

    if field_names:
        lines.append("Field names: " + ", ".join(field_names))

    if not examples and not field_names:
        lines.append(
            entry.get("note") or "Honest `any` -- no example or observed field names found in the module source."
        )

    return "\n\n".join(lines)


def _render_any_overlay_appendix(overlay: dict[str, Any], doc_version: str | None) -> str:
    """
    The full any-overlay appendix for one module: a ONE-TIME intro carrying
    the mandatory honesty labels (design's "Honesty labels" section), plus
    one block per overlay var, keyed by var name, appended REGARDLESS of
    whether a matching table row exists in the served document
    (appendix-anchored, not row-anchored -- curated docs are a subset and
    table schemes vary across the corpus). Sorted by var key for
    deterministic output.

    The example-provenance sentence, the field-name usage note, and the
    version-skew notice are IDENTICAL for every var in one module (same
    built_from_version, same doc_version), so they are rendered ONCE here
    rather than once per var -- on s3-bucket's ~20 any-vars the repeated
    ~230-char example sentence alone was the dominant cost. No honesty loss:
    every label still appears, just once instead of per-block.

    2026-07-21 discoverability fix: both labels below were reworded away from
    "confirm shapes via grep_module_docs" phrasing, which measurably invited
    the very grep round-trip the overlay exists to remove (an A/B eval worker
    read a field list this label was attached to and still went to grep
    "to confirm" it). The field-name label now says the names are directly
    usable input fields; grep_module_docs is reserved for inspecting a
    complex field's own nested sub-shape, not for re-confirming what this
    label already states.
    """
    built_from_version = overlay.get("built_from_version", "")
    vars_obj = overlay.get("vars") or {}
    if not vars_obj:
        return ""

    intro_lines = [
        "**any-typed input overlay** -- committed example HCL / observed field names for this "
        "module's `any`-typed inputs, appended here regardless of whether the input table above "
        "has a matching row; each block is keyed by var name and tagged with its provenance."
    ]
    if any(entry.get("examples") for entry in vars_obj.values()):
        intro_lines.append(
            f"Apply-verified example from `{built_from_version}`; references resources defined in "
            "that example; shown form is one accepted form -- copy and adapt this; consult "
            "`grep_module_docs` only for fields beyond this example."
        )
    if any(entry.get("field_names") for entry in vars_obj.values()):
        intro_lines.append(
            f"Field names read by the module source `@{built_from_version}` -- these are the "
            "accepted input fields; use them directly. Use `grep_module_docs` only to inspect "
            "the deep nested sub-shape of a specific complex field."
        )
    if doc_version and built_from_version and doc_version.strip() != built_from_version.strip():
        intro_lines.append(
            f"Version skew: example/fields from `{built_from_version}`, doc pins `{doc_version}` -- verify."
        )

    blocks = [_render_any_overlay_var_block(key, entry, built_from_version) for key, entry in sorted(vars_obj.items())]
    return "\n\n".join(["\n\n".join(intro_lines), *blocks])


# The exact prefix filter_module_sections emits for its own generated footer
# (see its footer_lines: "---" followed immediately by "Curated subset. For
# the COMPLETE inputs/outputs ..."). Distinctive on purpose: a bare "\n\n---\n"
# also matches any decorative horizontal rule a module doc happens to carry
# in its body (e.g. cloudwatch.md's mid-document "---" ahead of its first
# numbered submodule section), which used to make the appendix land there
# instead of at the real footer / the true end of the document.
_FILTER_FOOTER_MARKER = "\n\n---\nCurated subset."


def _insert_before_footer(rendered: str, appendix: str, *, is_filtered: bool) -> str:
    """
    Insert `appendix` as the final content block of `rendered`.

    Deliberately appendix-anchored rather than heading-anchored: the corpus's
    heading scheme varies (split "## Main Input Variables" vs combined
    "## Root Module:"/"## Submodule N:" bundles), and guessing at a specific
    H2/H3 boundary would risk exactly the shape-mismatch class
    _cap_head_input_table's docstring warns about.

    `is_filtered` distinguishes the two shapes get_module_impl passes in:
    - True: `rendered` is a filter_module_sections(...) result, which always
      carries its own generated footer. The appendix is inserted immediately
      before that footer (anchored on _FILTER_FOOTER_MARKER, NOT a bare
      "\\n\\n---\\n" -- a kept section's own body content could otherwise carry
      a decorative rule that gets mistaken for the real footer).
    - False: `rendered` is the RAW, unfiltered full document (the
      sections=["all"/"full"/"everything"] escape hatch) -- it carries no
      generated footer at all, and a bare "---" search can misfire on a
      decorative rule anywhere in the document body (cloudwatch.md's rule
      ahead of "## Submodule 1: log-group", about 16% through the file, used
      to pull the appendix there instead of after all 13 real submodules).
      The appendix is always appended at the strict end instead.
    """
    if not appendix:
        return rendered
    if not is_filtered:
        return rendered.rstrip("\n") + "\n\n" + appendix + "\n"
    idx = rendered.rfind(_FILTER_FOOTER_MARKER)
    if idx == -1:
        # Defensive: filter_module_sections always emits this footer today.
        # On an unforeseen shape change, fail safe to a strict end-append
        # rather than guessing at a bare "---".
        return rendered.rstrip("\n") + "\n\n" + appendix + "\n"
    return rendered[:idx] + "\n\n" + appendix + rendered[idx:]


# Logical keys whose presence in a get_module `sections` request means the
# response includes (or resolves to) the inputs view -- the only view the
# any-overlay appendix is spliced into (a request for unrelated sections, e.g.
# sections=["outputs"], must not gain input-var content it never asked for).
_ANY_OVERLAY_INPUT_KEYS = frozenset({"inputs", "variables"})


def _sections_request_inputs(sections: list[str]) -> bool:
    return any(entry.strip().lower() in _ANY_OVERLAY_INPUT_KEYS for entry in sections)


def _with_any_overlay_appendix(served_text: str, content: str, *, is_filtered: bool, scope: str | None = None) -> str:
    """
    Splice the any-overlay appendix into `served_text` (a
    filter_module_sections(...) result, or the raw full document) when
    `content` (the raw, unfiltered doc -- always used for module_id/version
    resolution regardless of how `served_text` was produced) resolves to a
    module with a committed overlay. A pure no-op (byte-identical
    `served_text` returned unchanged) when the module has no overlay file --
    the common case.

    `is_filtered` is forwarded to _insert_before_footer verbatim -- callers
    MUST pass True for a filter_module_sections(...) result and False for the
    raw full document, so the appendix is anchored correctly in either shape.

    `scope`, when given (a submodule name), restricts the appendix to that
    submodule's own `<scope>::`-prefixed overlay vars only -- used when
    serving a submodule-address request, so a submodule's inputs view never
    gains root-scope or a different submodule's overlay vars. A scope with
    zero matching vars is treated the same as "no overlay" (served_text
    returned unchanged).
    """
    module_id = _resolve_overlay_module_id(content)
    overlay = _load_any_overlay(module_id)
    if not overlay:
        return served_text
    if scope is not None:
        prefix = f"{scope}::"
        scoped_vars = {key: entry for key, entry in overlay.get("vars", {}).items() if key.startswith(prefix)}
        if not scoped_vars:
            return served_text
        overlay = {**overlay, "vars": scoped_vars}
    version_match = _LATEST_VERSION_RE.search(content)
    doc_version = version_match.group(1).strip() if version_match else None
    appendix = _render_any_overlay_appendix(overlay, doc_version)
    return _insert_before_footer(served_text, appendix, is_filtered=is_filtered)


def _cell_var_name(cell: str) -> str:
    """The bare variable name inside a Variable-column table cell, stripping
    the Markdown backticks the corpus always wraps names in (e.g.
    "`lifecycle_rule`" -> "lifecycle_rule")."""
    match = re.search(r"`([A-Za-z_][\w-]*)`", cell)
    return match.group(1) if match else cell.strip()


def _root_any_overlay_entries(text: str) -> dict[str, dict[str, Any]]:
    """Root-scope overlay entries (examples/field_names/provenance/note) from
    `text`'s committed overlay, keyed by the bare var name (the "root::"
    prefix stripped) -- both the eligibility set AND the content source for
    the head's pointer-only substitution (_substitute_any_type_head_cells)
    and the inline field-name hint (_inline_any_overlay_input_cells, Fix 1 of
    the 2026-07-21 table-discoverability fix). Empty when the module has no
    overlay."""
    overlay = _load_any_overlay(_resolve_overlay_module_id(text))
    if not overlay:
        return {}
    return {key.split("::", 1)[1]: entry for key, entry in overlay.get("vars", {}).items() if key.startswith("root::")}


def _root_any_var_names(text: str) -> frozenset[str]:
    """Root-scope any-var names from `text`'s committed overlay (if any) --
    used only to decide which head Type cells are eligible for the
    sections=["inputs"] pointer substitution. Empty when the module has no
    overlay."""
    return frozenset(_root_any_overlay_entries(text))


# Field names shown inline in a Type cell before falling back to a "+N more"
# tail (Fix 1 of the 2026-07-21 table-discoverability fix) -- long enough to
# be useful at the point of need, short enough to keep one table row one line.
_ANY_OVERLAY_CELL_FIELD_CAP = 6


def _format_any_overlay_cell_hint(entry: dict[str, Any]) -> str | None:
    """
    Build the inline Type-cell replacement for one any-typed input row from
    its root-scope overlay entry (Fix 1 of the 2026-07-21 table-
    discoverability fix): an A/B eval measured that a worker reading the
    input TABLE saw a bare `any` Type cell and greped `grep_module_docs` for
    the field names anyway, never connecting the row to the any-overlay
    appendix block below it. The field-name signal now lives AT the row,
    the point of need.

    - field_names present: ``"any -- fields: f1, f2, ..., f6[, +N more]"``,
      capped at ``_ANY_OVERLAY_CELL_FIELD_CAP`` names, plus ``"; example
      below"`` ONLY when the entry also carries an example -- never claim an
      example is "below" when the appendix block will not actually render
      one for this var.
    - no field_names but an example exists: ``"any -- see any-overlay
      example below"``.
    - honest-any (neither field_names nor an example): ``None`` -- the
      caller leaves the cell as bare ``any``, exactly as before this fix.

    Always a single line with no literal ``|``; overlay field names are
    plain identifiers in the corpus today so this holds by construction, but
    the caller (``_substitute_input_table_cells``) still verifies it before
    writing the cell rather than trusting this blindly.
    """
    field_names = entry.get("field_names") or []
    has_example = bool(entry.get("examples"))
    if field_names:
        shown = field_names[:_ANY_OVERLAY_CELL_FIELD_CAP]
        hint = "any -- fields: " + ", ".join(shown)
        remaining = len(field_names) - len(shown)
        if remaining > 0:
            hint += f", +{remaining} more"
        if has_example:
            hint += "; example below"
        return hint
    if has_example:
        return "any -- see any-overlay example below"
    return None


def _substitute_input_table_cells(text: str, cell_for_row: Callable[[str, str], str | None]) -> str:
    """
    Walk EVERY ``### Main Input Variables`` table in `text` -- a document can
    carry more than one on the combined-scheme corpus (one per "## Root
    Module:"/"## Submodule N:" bundle, e.g. elasticache) -- and, for each
    data row, ask ``cell_for_row(var_name, type_cell)`` for a replacement
    Type-cell string. Returning ``None`` from the callback leaves that row's
    Type cell untouched.

    Shared by the head's pointer-only substitution
    (``_substitute_any_type_head_cells``, which only ever sees a single table
    since the head is scoped to ``interface_scope="root"``) and the inline
    field-name hint (``_inline_any_overlay_input_cells``, which can see
    several tables in one call).

    Reuses exactly the heading/header/separator detection
    ``_cap_head_input_table`` relies on, so whenever that cap correctly
    identifies a table, this substitution does too -- and on any parse
    mismatch for one OCCURRENCE (no header row immediately after the
    heading, no separator, no Variable/Type column) that occurrence is left
    unchanged rather than guessing, the same fail-safe contract the cap
    function documents; other occurrences in the same document are still
    processed independently. A callback replacement containing a literal
    ``|`` or a newline is rejected (that row left unchanged) so a malformed
    hint can never corrupt the table shape.
    """
    lines = text.splitlines(keepends=True)
    changed = False
    for heading_match in _INPUT_TABLE_HEADING_RE.finditer(text):
        heading_line_idx = text.count("\n", 0, heading_match.start())

        idx = heading_line_idx + 1
        while idx < len(lines) and lines[idx].strip() == "":
            idx += 1
        if idx >= len(lines) or not _TABLE_ROW_RE.match(lines[idx].rstrip("\n")):
            continue
        header_line_idx = idx
        header_cells = _split_table_row(lines[header_line_idx])

        sep_idx = header_line_idx + 1
        if sep_idx >= len(lines) or not _TABLE_SEPARATOR_RE.match(lines[sep_idx].rstrip("\n")):
            continue

        lower_headers = [c.lower() for c in header_cells]
        if "variable" not in lower_headers or "type" not in lower_headers:
            continue
        var_idx = lower_headers.index("variable")
        type_idx = lower_headers.index("type")

        row_idx = sep_idx + 1
        while row_idx < len(lines) and _TABLE_ROW_RE.match(lines[row_idx].rstrip("\n")):
            row = lines[row_idx]
            cells = _split_table_row(row)
            if len(cells) > max(var_idx, type_idx):
                replacement = cell_for_row(_cell_var_name(cells[var_idx]), cells[type_idx])
                if replacement is not None and "|" not in replacement and "\n" not in replacement:
                    cells[type_idx] = replacement
                    newline = "\n" if row.endswith("\n") else ""
                    lines[row_idx] = "| " + " | ".join(cells) + " |" + newline
                    changed = True
            row_idx += 1

    return "".join(lines) if changed else text


def _substitute_any_type_head_cells(head_text: str, any_var_names: frozenset[str]) -> str:
    """
    Cell-substitution ONLY, for the default orientation HEAD's inlined
    ``### Main Input Variables`` table: when a row's Variable name is in
    `any_var_names` (a module WITH a committed overlay) and its Type cell is
    exactly ``any``, replace that Type cell with a pointer to
    ``sections=["inputs"]``. Never inlines the example/field-list themselves
    (token budget) and never adds "below" wording (nothing is "below" in the
    head). Emits a pipe-table-compatible cell (same column count, no literal
    ``|``/newline) and MUST run before ``_cap_head_input_table`` so the cap's
    own row/column parsing is unaffected.

    Delegates to ``_substitute_input_table_cells`` (the fail-safe multi-table
    walker also used by ``_inline_any_overlay_input_cells``) -- the head text
    only ever carries a single ``### Main Input Variables`` table
    (``interface_scope="root"`` excludes submodule bundles), so walking
    "every" table here is equivalent to the previous single-table
    implementation. A module with no overlay (``any_var_names`` empty)
    short-circuits to a no-op without even attempting to locate the table.
    """
    if not any_var_names:
        return head_text

    def _cell_for_row(var_name: str, type_cell: str) -> str | None:
        if var_name not in any_var_names or type_cell.strip().strip("`").strip().lower() != "any":
            return None
        return _ANY_TYPE_HEAD_POINTER

    return _substitute_input_table_cells(head_text, _cell_for_row)


def _inline_any_overlay_input_cells(rendered: str, content: str) -> str:
    """
    Fix 1 of the 2026-07-21 table-discoverability fix: for a non-head view
    (a ``sections=["inputs"]`` response, or the full-document escape hatch),
    inline the overlay's field-name (or example-only) hint directly into the
    Type cell of every ``any``-typed input row whose var name has a
    root-scope overlay entry -- AT the row, across every ``### Main Input
    Variables`` table `rendered` carries (a combined-scheme doc like
    elasticache has one such table per submodule bundle plus the root/main
    one; only the root-scope table's rows are eligible, but matching is by
    var name so no heading-scoping is needed to find it).

    An A/B eval measured the any-overlay appendix as not landing on its own:
    a worker read the input table, saw a bare ``any`` Type cell, and grepped
    ``grep_module_docs`` for the fields anyway rather than connecting the row
    to the appendix block below it. This closes that gap at the point of
    need. The appendix (``_with_any_overlay_appendix``) still runs
    afterward and remains the source of the full example HCL / field list;
    this substitution is only ever a same-row pointer into it.

    Root-scope only (see ``_root_any_overlay_entries``) and matched purely by
    var name against every table row in `rendered`, regardless of which H2
    bundle it lives under -- like the head substitution, this trusts that
    the corpus's submodule variable namespaces do not collide with the
    root's. Must run BEFORE ``_with_any_overlay_appendix`` (the appendix is
    what a row's "below" wording now points at). A no-op when the module has
    no overlay, or none of its root-scope any-vars have a matching table row
    (the common case: no overlay).
    """
    entries = _root_any_overlay_entries(content)
    if not entries:
        return rendered

    def _cell_for_row(var_name: str, type_cell: str) -> str | None:
        if type_cell.strip().strip("`").strip().lower() != "any":
            return None
        entry = entries.get(var_name)
        if entry is None:
            return None
        return _format_any_overlay_cell_hint(entry)

    return _substitute_input_table_cells(rendered, _cell_for_row)


def orientation_head(text: str, version_override: str | None = None) -> str:
    """
    Build the compact orientation view returned by get_module by default.

    Combines the always-included core sections (Description, Module Information,
    Notes for AI Agents, and Important Gotchas where the doc has it) with Key
    Features and Main Use Cases, prepends an actionable exact-version pin hint,
    and appends a footer listing
    every omitted section as a table of contents. Keeps a first orientation call
    small — what the module is plus how to reach the rest — instead of returning
    the full body, which runs to ~12k tokens for the largest modules.

    For modules that carry submodules, the compact ``## Submodules`` inventory
    (each submodule's name, purpose, and pinnable source string) is inlined so a
    single orientation call surfaces which submodule to reach for — without
    expanding the far larger ``## Submodule N:`` deep-dive sections (request one
    by name, or via ``get_module("<name>//modules/<sub>")``).

    Also inlines the root module's compact ``### Main Input Variables`` H3 (when
    the doc has one), scoped to the root/main bundle only — submodule inputs stay
    out of the head so a collection doc with no root inputs gets no extra noise.
    That inlined table is further capped to essential (required) rows by
    ``_cap_head_input_table`` (L4) — the full table remains one
    ``sections=["inputs"]`` call away.

    For a module with a committed any-shape overlay (``model/any_overlay/``),
    any root-scope ``any``-typed row's Type cell is substituted with a
    pointer to ``sections=["inputs"]`` (cell-substitution only, BEFORE the
    cap below — never the example/field-list themselves, which would blow the
    head's token budget; see ``_substitute_any_type_head_cells``).

    Args:
        text: The module document body.
        version_override: Forwarded to ``_version_pin_hint`` verbatim (single-
            snapshot version consistency). None (default) re-parses the
            body's ``**Latest Version**`` bullet as before.
    """
    body = filter_module_sections(
        text,
        [*_ORIENTATION_KEYS, "inputs"],
        extra_exact_titles=("Submodules",),
        interface_scope="root",
        silent_keys=frozenset({*_ORIENTATION_KEYS, "inputs"}),
    )
    body = _substitute_any_type_head_cells(body, _root_any_var_names(text))
    body = _cap_head_input_table(body)
    # When a snapshot is threaded in, reconcile the body's own
    # **Latest Version** bullet to it so the inlined head cannot contradict the
    # pin banner / results[].latest_version. No override -> body bullet is the
    # snapshot, so this is a no-op and the head stays self-consistent as before.
    body = _reconcile_body_version(body, version_override)
    hint = _version_pin_hint(text, version_override=version_override)
    return f"{hint}\n\n{body}" if hint else body


def get_module_impl(module_identifier: str, state: ServerState, sections: list[str] | None = None) -> str:
    """
    Helper function to get module documentation.

    This function is testable (not decorated) and can be called directly
    with a ServerState instance for testing.

    Args:
        module_identifier: Module name or relative file path
        state: Server state containing index and configuration
        sections: Optional section keys or heading substrings. When omitted, a
            compact orientation head is returned (core sections + features/use-
            cases + a section-index footer + version-pin hint). Pass explicit
            keys to add sections, or one of {"all", "full", "everything"} to get
            the complete document.

    Returns:
        The compact orientation head by default, a filtered subset when specific
        sections are requested, or the full document when an all/full key is given

    For a module with a committed any-shape overlay (``model/any_overlay/``),
    a non-head response (an explicit ``sections`` request that resolves to
    the inputs view, or the full-document escape hatch) gets TWO things: (1)
    each root-scope ``any``-typed input row whose var has an overlay entry
    gets its Type cell inlined with a field-name (or example-only) hint, AT
    the row (see ``_inline_any_overlay_input_cells`` — Fix 1 of the
    2026-07-21 table-discoverability fix: the appendix alone measured as not
    landing, because a worker reads the row, sees bare ``any``, and greps
    instead of scrolling to the appendix), and (2) an appendix-anchored block
    per overlay var appended to the end of the response, regardless of
    whether a matching input-table row exists (see
    ``_with_any_overlay_appendix``). The default orientation head instead
    gets only a cell-substitution pointer (see ``orientation_head``) — never
    the example/field-list content. A module with no overlay is unaffected.

    See get_module() tool documentation for full details.
    """
    # A submodule address ("iam//modules/iam-role") resolves to the parent doc,
    # scoped to that submodule's section — a one-call submodule orientation.
    sub_address = _parse_submodule_address(module_identifier)
    if sub_address is not None:
        parent_name, sub = sub_address
        content = get_module_documentation(parent_name, state)
        # Honor the full-doc escape hatch (all/full/everything) the same way the
        # name/path branch does — return the complete parent document verbatim,
        # with the full (unscoped) any-overlay appendix, exactly like the
        # non-submodule full-doc branch below.
        if sections and any(entry.strip().lower() in _FULL_DOC_KEYS for entry in sections):
            served = _inline_any_overlay_input_cells(content, content)
            return _with_any_overlay_appendix(served, content, is_filtered=False)
        body = filter_module_sections(content, [sub, *(sections or [])])
        # A module WITH a committed any-shape overlay can have submodule-scoped
        # any-vars (e.g. fsx has all 19 of its any-vars submodule-scoped) — an
        # explicit inputs/variables request here must get its OWN appendix,
        # scope-filtered to this submodule's `<sub>::` keys only so a different
        # submodule's or the root's overlay vars never leak in. The root-scope
        # inline cell hint (Fix 1) runs unconditionally here too — harmless
        # no-op unless this submodule body happens to also carry the root's
        # own inputs table (e.g. sections=["inputs"] on top of the submodule
        # address).
        if _sections_request_inputs(sections or []):
            body = _inline_any_overlay_input_cells(body, content)
            body = _with_any_overlay_appendix(body, content, is_filtered=True, scope=sub)
        hint = _version_pin_hint(content)
        return f"{hint}\n\n{body}" if hint else body

    content = get_module_documentation(module_identifier, state)
    if sections:
        if any(entry.strip().lower() in _FULL_DOC_KEYS for entry in sections):
            served = _inline_any_overlay_input_cells(content, content)
            return _with_any_overlay_appendix(served, content, is_filtered=False)
        rendered = filter_module_sections(content, sections)
        if _sections_request_inputs(sections):
            rendered = _inline_any_overlay_input_cells(rendered, content)
            rendered = _with_any_overlay_appendix(rendered, content, is_filtered=True)
        return rendered
    return orientation_head(content)


def modules_list_impl(state: ServerState, detail: str = "compact") -> ModulesListOutput:
    """
    Helper function to list all available modules.

    This function is testable (not decorated) and can be called directly
    with a ServerState instance for testing.

    Args:
        state: Server state containing index and configuration
        detail: "compact" (default) returns name + purpose + registry coordinates
            only; "full" restores the path, full description, and keyword arrays.

    Returns:
        ModulesListOutput with the catalog of all modules

    See modules_list() tool documentation for full details.
    """
    assert state.logger is not None, "ServerState must have a logger"  # noqa: S101

    state.logger.debug(f"Listing all modules: {len(state.index.docs)} documents (detail={detail})")

    modules: list[ModuleListItem]
    if detail == "full":
        # L1: full metadata on demand. The 12-18-item keyword arrays and long
        # descriptions this restores are the bulk of the byte-identical dump the
        # compact default drops.
        full_items: list[ModuleListItem] = []
        for doc in state.index.docs:
            full_items.append(
                ModuleListItem(
                    module_name=doc.module_name or "",
                    path=doc.path,
                    description=extract_purpose(doc.text),
                    keywords=doc.keywords or [],
                    module_id=getattr(doc, "module_id", ""),
                    latest_version=getattr(doc, "latest_version", ""),
                )
            )
        modules = full_items
    else:
        compact_items: list[ModuleListItemCompact] = []
        for doc in state.index.docs:
            compact_items.append(
                ModuleListItemCompact(
                    module_name=doc.module_name or "",
                    # 117 leaves room for extract_purpose's 3-char "..." suffix so
                    # the clipped purpose never exceeds the 120-char budget.
                    purpose=extract_purpose(doc.text, max_length=117),
                    module_id=getattr(doc, "module_id", ""),
                    latest_version=getattr(doc, "latest_version", ""),
                )
            )
        modules = compact_items

    state.logger.debug(f"Modules list generated: {len(modules)} items")

    return ModulesListOutput(modules=modules, count=len(modules))


def grep_module_docs_impl(
    module_id: str,
    pattern: str,
    *,
    version: str | None = None,
    case_sensitive: bool = False,
    context_lines: int = 2,
    scope: list[str] | None = None,
    max_matches: int = 50,
    refresh: bool = False,
    cache_dir: Path,
    ttl_hours: int = 24,
) -> GrepOutput:
    """
    Helper function to fetch, cache, and grep live Terraform Registry module documentation.

    This function is testable (not decorated) and can be called directly with an
    explicit cache_dir, independent of ServerState/ServerStateManager.

    Args:
        module_id: Terraform Registry coordinates "namespace/name/provider".
        pattern: Python regex to search for.
        version: Exact version to pin, or None to resolve the current latest.
        case_sensitive: Case-sensitive match (default False).
        context_lines: Lines of context before/after each match, clamped to 0..20.
        scope: Optional list restricting the grep to specific document parts
            (root, inputs, outputs, resources, submodules, examples).
        max_matches: Cap on returned matches, clamped to >= 1.
        refresh: Bypass the cache and refetch from the registry.
        cache_dir: Disk cache directory for assembled registry documents.
        ttl_hours: TTL (hours) for "latest" (unpinned) cache entries.

    Returns:
        GrepOutput with matches, cache status, and available section labels.

    Raises:
        ValueError: If module_id is malformed (propagated from parse_module_id
            via get_assembled_docs) or pattern is not a valid regex.

    See grep_module_docs() tool documentation for full details.
    """
    context_lines = max(0, min(int(context_lines), 20))
    max_matches = max(1, int(max_matches))

    # Look up tfmod_registry_docs._http_fetch on the module at call time (rather than
    # relying on get_assembled_docs's bound default) so tests that monkeypatch
    # tfmod_registry_docs._http_fetch are honored without any real network access.
    assembled_text, resolved_version, source_url, cache_hit, fetched_at = get_assembled_docs(
        module_id,
        version,
        cache_dir=cache_dir,
        ttl_hours=ttl_hours,
        refresh=refresh,
        fetch=tfmod_registry_docs._http_fetch,
    )

    doc_matches, total, available_sections = grep_document(
        assembled_text,
        pattern,
        case_sensitive=case_sensitive,
        context_lines=context_lines,
        scope=scope,
        max_matches=max_matches,
    )

    matches = [
        GrepMatch(
            section=m.section,
            line_number=m.line_number,
            line=m.line,
            before=m.before,
            after=m.after,
            enclosing=m.enclosing,
        )
        for m in doc_matches
    ]

    return GrepOutput(
        module_id=module_id,
        resolved_version=resolved_version,
        source_url=source_url,
        total_matches=total,
        returned_matches=len(matches),
        truncated=total > max_matches,
        cache=CacheInfo(hit=cache_hit, fetched_at=fetched_at, policy="pinned" if version else "latest-ttl"),
        matches=matches,
        available_sections=available_sections,
    )


# -----------------------------
# MCP Tools
# -----------------------------


@app.tool(
    description=(
        "List all available Terraform modules in the catalog. "
        "Compact by default: each entry carries the module name, a one-line purpose, and the "
        'registry coordinates (module_id, latest_version). Pass detail="full" to also get each '
        "module's path, full description, and keyword arrays. "
        "Use this to discover what modules are available before searching or retrieving documentation. "
        "If there are no required module, please search in Terraform Registry (https://registry.terraform.io/)."
    ),
    tags={"catalog", "list", "terraform", "aws", "modules"},
    annotations=ToolAnnotations(title="List all available Terraform modules"),
)
def modules_list(detail: str = "compact") -> ModulesListOutput:
    """
    List all available Terraform modules in the catalog.

    Returns the catalog of all indexed Terraform modules. By default (detail=
    "compact") each entry carries only the module name, a one-line purpose, and
    the registry coordinates (module_id, latest_version) needed to chain into
    grep_module_docs - the whole catalog stays small enough to read on every
    call. Pass detail="full" to also get each module's path, full description,
    and keyword arrays.

    Args:
        detail: "compact" (default) or "full".

    Returns:
        ModulesListOutput: Catalog with:
            - modules: List of all modules (compact or full metadata)
            - count: Total number of modules

    Raises:
        RuntimeError: If server state is not initialized

    Use Cases:
        - Discover what modules are available before searching
        - Browse the complete catalog of Terraform modules
        - Get an overview of all indexed documentation
        - Find modules by reviewing descriptions and keywords

    Example Output:
        {
          "modules": [
            {
              "module_name": "vpc",
              "path": "modules/terraform-aws-modules/vpc.md",
              "description": "Terraform module to create AWS VPC resources...",
              "keywords": ["vpc", "subnet", "networking", "aws"]
            },
            ...
          ],
          "count": 6
        }

    Typical Workflow:
        1. Call modules_list() to see all available modules
        2. Review module names, descriptions, and keywords
        3. Use search_modules() for specific queries
        4. Use get_module() to retrieve full documentation
    """
    state = ServerStateManager.get()
    result = modules_list_impl(state, detail=detail)
    result.update_notice = _update_notice()
    return result


@app.tool(
    description=(
        "Search for Terraform AWS modules by keywords, exact name, or free-text query. "
        "Returns top-ranked results (top_k, default 3) with module name, path, keywords, "
        "description, relevance score, and a confidence verdict (high/low). On a "
        "high-confidence result the top-1 module orientation head is inlined by default "
        "(top_module_doc) -- pass expand_top=False to suppress it for a pure-browse search."
    ),
    tags={"search", "terraform", "aws", "modules"},
    annotations=ToolAnnotations(title="Search for Terraform AWS modules by keywords, exact name, or free-text query."),
)
def search_modules(
    query: Annotated[
        str,
        Field(
            description="Free-text query for Terraform module search. "
            "May include keywords, module names, or natural language descriptions."
        ),
    ],
    top_k: Annotated[
        int,
        Field(
            ge=1,
            le=10,
            description="Number of results to return (1-10). Default 3 suits most queries; "
            "raise it for ambiguous queries like 'iam'.",
        ),
    ] = 3,
    expand_top: Annotated[
        bool,
        Field(
            description="When True AND the search is high confidence, inline the top-1 "
            "module orientation head into the response (top_module_doc) -- collapses a "
            "confident search->get_module pair into one call. Default True: a confident "
            "search is almost always followed by fetching that module, so the head comes "
            "along for free. Pass expand_top=False to suppress it for a pure-browse search. "
            "Inlined iff the verdict is 'high' (the capability-aware classifier demotes a "
            "wrong-domain top hit to 'low' first).",
        ),
    ] = True,
) -> SearchOutput:
    """
    Search for Terraform AWS modules using hybrid search.

    Performs a hybrid search combining keyword matching, exact module name matching,
    BM25 text relevance, and semantic similarity to find the most relevant Terraform
    modules based on the user's query.

    The search uses pre-configured weights (from config.yaml or CLI arguments) to
    balance different scoring components:
    - Keyword overlap (IDF-weighted)
    - Exact module name match
    - BM25 statistical text relevance
    - Semantic similarity using neural embeddings

    Args:
        query: Free-text query for Terraform module search. May include
               keywords (e.g., "s3 encryption"), module names (e.g., "vpc"),
               or natural language descriptions (e.g., "object storage with versioning").
        top_k: Number of results to return (1-10, default 3).
        expand_top: When True and the search is high confidence, inline the
               top-1 module orientation head into top_module_doc (L3) -- one
               call instead of search then get_module. Default True.
               Populated iff the verdict is "high" (verdict and inline
               are one decision), so a wrong-domain top hit is never inlined.

    Returns:
        SearchOutput: Container with top-k ranked results plus a confidence
            verdict. Each result includes:
            - module_name: Normalized module identifier (e.g., "s3-bucket", "eks")
            - path: Relative path to module documentation file
            - keywords: List of extracted module keywords/tags
            - description: Extracted module description (up to 200 chars)
            - score: Combined relevance score (higher = more relevant)
            Plus on the container itself:
            - confidence: "high" / "low" -- always present
            - hint: actionable follow-up guidance, present only for "low"
            - top_module_doc: the top-1 orientation head, present by default whenever
              confidence == "high" (absent when expand_top=False or confidence == "low")

    Raises:
        RuntimeError: If server state is not initialized.

    Examples:
        Query by exact module name:
            Input: "vpc"
            Output: Returns VPC module as top result

        Query by functionality:
            Input: "s3 bucket with encryption"
            Output: Returns S3 bucket module with encryption features

        Query by natural language:
            Input: "kubernetes cluster management"
            Output: Returns EKS module as top result

    Notes:
        - Returns top_k results (default 3, or fewer if index has fewer modules)
        - Results are ranked by combined score from multiple search components
        - Search weights are configured server-wide and cannot be changed per-query
        - Empty queries return empty results
    """
    state = ServerStateManager.get()
    result = search_modules_impl(query, state, top_k=top_k, expand_top=expand_top)
    result.update_notice = _update_notice()
    return result


@app.tool(
    description=(
        "Get compacted documentation for a specific Terraform module. "
        "Use this tool after search_modules to orient on the chosen module. "
        "By default returns a compact orientation head — description, module info, exact "
        "version pin, agent notes, any gotchas, key features, and use cases — plus a footer "
        "with the full section inventory: an explicit menu of the logical keys (inputs, "
        "outputs, examples, submodules, ...) and every heading in the doc. "
        "Pass `sections` to fetch specific parts you need, or `sections=['all']` "
        "for the complete document (prefer scoped sections on large modules — they run to "
        "10k+ tokens in full). "
        "The variable names, defaults, and version in the head and in `sections` are the "
        "authoritative values from the curated catalog — use them directly; you do not need to "
        "re-confirm them with grep_module_docs. "
        "To get original documentation including full lists of inputs/outputs for each sub-module, "
        "use direct links to registry.terraform.io from documentation."
    ),
    tags={"documentation", "terraform", "aws", "modules"},
    annotations=ToolAnnotations(title="Get compacted documentation for a Terraform module"),
)
def get_module(
    module_identifier: Annotated[
        str,
        Field(
            description="Module identifier: a module name (e.g., 'vpc', 's3-bucket'), a relative "
            "path (e.g., 'modules/terraform-aws-modules/vpc.md'), or a submodule address "
            "(e.g., 'iam//modules/iam-role') to orient on a single submodule in one call. The "
            "default head of a module with submodules inlines their inventory (name + source)."
        ),
    ],
    sections: Annotated[
        list[str] | None,
        Field(
            description="Optional list of sections to return. Accepts logical keys — inputs, "
            "outputs, examples, submodules, features, use-cases, best-practices, resources — "
            "or case-insensitive substrings of section headings (e.g. 'karpenter' for a single "
            "EKS submodule); the inputs/outputs/examples keys also resolve on modules that bundle "
            "them into a combined section. The 'submodules' key returns only the compact submodule "
            "inventory (names, purposes, pinnable sources) -- which is already inlined in the default "
            "head -- so an existence or name check never needs a sections call; reach a specific "
            "submodule's full interface by naming its heading or via the '<name>//modules/<sub>' address. "
            "Core context (description, module info, version pin, "
            "notes for AI agents, and any Important Gotchas the doc carries) is always included, and omitted sections are listed in "
            "a footer so you can request them later. Omit this parameter for the compact "
            "orientation head; pass ['all'] (or 'full') for the complete document."
        ),
    ] = None,
) -> str:
    """
    Get compacted documentation for a specific Terraform module.

    Retrieves documentation for a Terraform module identified by either its name
    or file path. By default returns a compact orientation head; the full body
    is available on request via `sections`.

    Args:
        module_identifier: One of:
            - Module name (e.g., "vpc", "s3-bucket", "eks")
            - Relative path to module file (e.g., "modules/terraform-aws-modules/vpc.md")
            - Submodule address (e.g., "iam//modules/iam-role" or the full
              "terraform-aws-modules/iam/aws//modules/iam-role") — returns an
              orientation head scoped to that submodule's section
        sections: Optional list of section keys or heading substrings. When
            omitted, a compact orientation head is returned — the core sections
            (front-matter, Description, Module Information, Notes for AI Agents,
            and Important Gotchas where the doc has it) plus Key Features, Main
            Use Cases, an exact version-pin hint, and a footer listing every
            omitted section as a
            table of contents. When given, the response is those core sections
            plus the requested ones (same footer). Pass one of {"all", "full",
            "everything"} to return the complete document.

    Returns:
        str: The compact orientation head by default, a filtered subset when
            specific sections are requested, or the full documentation text when
            an all/full key is given

    Raises:
        ValueError: If module not found or path is invalid/insecure
        RuntimeError: If server state is not initialized

    Resolution Logic:
        1. If identifier looks like a path (contains "/" or ends with ".md"):
           - Validates path is under "modules/" directory (security check)
           - Verifies file exists
           - Reads and returns complete file content
        2. Otherwise, treats identifier as module name:
           - Searches index for matching module
           - Returns top-1 result's documentation
           - Raises ValueError if no matches found

    Security:
        - File paths MUST be under "modules/" directory
        - Absolute paths and path traversal attempts are rejected
        - Only reads from indexed module documentation

    Examples:
        Get module by name (compact orientation head):
            Input: "vpc"
            Returns: VPC orientation head + section index

        Get the full document:
            Input: "s3-bucket", sections=["all"]
            Returns: Complete S3 bucket module documentation

        Get only specific sections:
            Input: "s3-bucket", sections=["inputs", "examples"]
            Returns: Core sections plus input variables and usage examples

        Orient on a single submodule in one call:
            Input: "iam//modules/iam-role"
            Returns: Core context + the iam-role submodule section, scoped

        Typical workflow:
            1. search_modules("s3 encryption") → get top result path
            2. get_module(path) → orient (compact head; submodule inventory inline)
            3. get_module(path, sections=["inputs"]) → pull the details you need
               (or get_module("<name>//modules/<sub>") for a submodule)
    """
    state = ServerStateManager.get()
    return get_module_impl(module_identifier, state, sections=sections)


@app.tool(
    description=(
        "Grep the full, current documentation for ANY Terraform Registry module (not limited to the "
        "curated AWS catalog), optionally pinned to a specific version. Fetches root readme/inputs/"
        "outputs/resources plus submodules and examples, assembles them into one document, caches it on "
        "disk, and returns only matching lines with a few lines of context — like the Grep tool, not a "
        "document dump. Use search_modules/get_module for curated AWS modules; use this tool for any "
        "registry module, live/version-pinned lookups, or to pinpoint an exact current variable name or "
        "default without guessing from training data. "
        "The assembled doc renders inputs as markdown LIST items — "
        "`- <name> | <type> | <default> | <description>` — NOT pipe-table rows. Match the bare "
        "identifier (e.g. `enable_nat_gateway`); do NOT anchor with `^` or assume a leading `|`, or "
        "you will get zero matches on a name that is present."
    ),
    tags={"grep", "registry", "terraform", "live", "documentation"},
    annotations=ToolAnnotations(title="Grep live Terraform Registry module documentation"),
)
def grep_module_docs(
    module_id: Annotated[
        str,
        Field(
            description="Terraform Registry module coordinates 'namespace/name/provider', e.g. "
            "'terraform-aws-modules/vpc/aws'. Get this from search_modules/modules_list results "
            "(module_id field) or from a registry.terraform.io URL."
        ),
    ],
    pattern: Annotated[
        str,
        Field(description="Python regex to search for, e.g. 'enable_nat_gateway' or 'nat.*gateway'."),
    ],
    version: Annotated[
        str | None,
        Field(
            description="Exact version to pin (e.g. '6.6.1'), cached forever once fetched. Omit to "
            "resolve and use the true current latest, which is refetched once the cache entry is "
            "older than doc_cache_ttl_hours (default 24h)."
        ),
    ] = None,
    case_sensitive: Annotated[
        bool, Field(description="Case-sensitive match. Default False (case-insensitive).")
    ] = False,
    context_lines: Annotated[
        int,
        Field(
            ge=0,
            le=20,
            description="Lines of context before AND after each match (0-20, like grep -C). Default 2.",
        ),
    ] = 2,
    scope: Annotated[
        list[str] | None,
        Field(
            description="Restrict the grep to specific parts of the assembled document: 'root', "
            "'inputs', 'outputs', 'resources', 'submodules', 'examples'. Default: search everything."
        ),
    ] = None,
    max_matches: Annotated[
        int, Field(ge=1, description="Cap on returned matches, to manage token budget. Default 50.")
    ] = 50,
    refresh: Annotated[
        bool, Field(description="Bypass the cache and refetch from the registry. Default False.")
    ] = False,
) -> GrepOutput:
    """
    Grep the live, current documentation for any Terraform Registry module.

    Fetches the module's full detail from the Terraform Registry API (root readme,
    inputs, outputs, resources, submodules, examples), assembles it into one
    deterministic, section-marked text, caches it on disk, and runs a regex grep
    over it — returning only matching lines with surrounding context rather than
    the whole (often 10k+ token) document.

    Use this not only to confirm resource/variable NAMES but to verify the exact
    TYPE/SHAPE of a `map(object)`/`any`-typed input (its nested field structure)
    before writing it — the curated doc's table often abbreviates these.

    Args:
        module_id: Terraform Registry coordinates "namespace/name/provider".
        pattern: Python regex to search for.
        version: Exact version to pin, or None to resolve the current latest.
        case_sensitive: Case-sensitive match (default False).
        context_lines: Lines of context before/after each match (0-20, default 2).
        scope: Optional list restricting the grep to specific document parts.
        max_matches: Cap on returned matches (default 50).
        refresh: Bypass the cache and refetch from the registry.

    Returns:
        GrepOutput: matches (with section label, line number, context, and an
            `enclosing` breadcrumb naming the nearest '- <name> | ...' row when
            the match landed on a continuation line of a multi-line row --
            e.g. a nested object/map type -- so the container name is never
            lost), total_matches/returned_matches/truncated, resolved_version,
            source_url, cache status, and available_sections (useful to refine
            pattern/scope, especially when total_matches is 0).

    Raises:
        ValueError: If module_id is not exactly "namespace/name/provider", or
            pattern is not a valid regex.
        RuntimeError: If server state is not initialized.

    Examples:
        Pin an exact version and find a variable's default:
            Input: module_id="terraform-aws-modules/vpc/aws", pattern="enable_nat_gateway", version="6.6.1"
            Output: matching input row(s) from root/inputs with context

        Look up a module not in the curated catalog:
            Input: module_id="hashicorp/consul/aws", pattern="cluster_size"

    Typical Workflow:
        1. search_modules("s3 bucket") → note the module_id/latest_version of the hit
        2. grep_module_docs(module_id, "encryption", version=latest_version) → pinpoint details
    """
    state = ServerStateManager.get()
    cache_dir = state.doc_cache_dir
    ttl_hours = state.doc_cache_ttl_hours
    if cache_dir is None:
        cache_dir, ttl_hours = ConfigLoader.load_doc_cache()
    result = grep_module_docs_impl(
        module_id,
        pattern,
        version=version,
        case_sensitive=case_sensitive,
        context_lines=context_lines,
        scope=scope,
        max_matches=max_matches,
        refresh=refresh,
        cache_dir=cache_dir,
        ttl_hours=ttl_hours,
    )
    result.update_notice = _update_notice()
    return result


# -----------------------------
# Initialization and Entry Point
# -----------------------------


def _is_loopback(host: str) -> bool:
    """True when host is a loopback address or the literal localhost."""
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host.lower() == "localhost"


UPDATE_CHECK_INTERVAL_HOURS = 24
_UPDATE_CHECK_FALSY = {"", "0", "false", "no", "off"}
_UPDATE_NOTICE_TEMPLATE = (
    "tfmodsearch {latest} is available (this shared daemon runs {current}). "
    "Ask the operator to update: bump the image tag in docker-compose.yml, "
    "then docker compose pull && docker compose up -d."
)
# Replaced atomically (single assignment) by the checker thread; readers
# (health route, tool wrappers) never see a torn value thanks to the GIL.
_UPDATE_STATE: dict[str, Any] = {"latest_version": None, "update_available": False}


def _update_check_enabled(env: Mapping[str, str]) -> bool:
    """Kill switch: TFMODSEARCH_UPDATE_CHECK in the falsy set disables the check."""
    return env.get("TFMODSEARCH_UPDATE_CHECK", "1").strip().lower() not in _UPDATE_CHECK_FALSY


def _run_update_check_once(fetcher: Any = None) -> None:
    """One check cycle: fetch latest from PyPI, compare, publish state, log.

    Failures leave the previous state untouched (fetch returns None).
    """
    global _UPDATE_STATE
    logger = logging.getLogger(__name__)
    latest = fetch_latest_pypi_version(fetcher=fetcher) if fetcher else fetch_latest_pypi_version()
    if latest is None:
        logger.debug("Update check failed; keeping previous state")
        return
    newer = is_newer_version(latest, _SERVER_VERSION)
    _UPDATE_STATE = {"latest_version": latest, "update_available": newer}
    if newer:
        logger.warning(_UPDATE_NOTICE_TEMPLATE.format(latest=latest, current=_SERVER_VERSION))


def _update_notice() -> str | None:
    """Agent-facing notice string, or None when no update is known."""
    state = _UPDATE_STATE  # local snapshot: both keys come from one consistent dict
    if state["update_available"]:
        return _UPDATE_NOTICE_TEMPLATE.format(latest=state["latest_version"], current=_SERVER_VERSION)
    return None


def _start_update_checker_thread() -> threading.Thread:
    """Daily update check in a daemon thread (HTTP mode only; see main())."""

    def _loop() -> None:
        while True:
            try:
                _run_update_check_once()
            except Exception:
                # The check must never kill the thread for the daemon lifetime;
                # a failed cycle is retried on the next one.
                logging.getLogger(__name__).debug("Update check cycle failed", exc_info=True)
            time.sleep(UPDATE_CHECK_INTERVAL_HOURS * 3600)

    thread = threading.Thread(target=_loop, name="tfmodsearch-update-check", daemon=True)
    thread.start()
    return thread


def resolve_config_path(config_arg: str) -> Path | None:
    """
    Resolve configuration file path.

    Tries multiple locations:
    1. Absolute path if provided
    2. Relative to project root (handles both dev and installed layouts)
    3. Relative to current directory

    Args:
        config_arg: Config path from command line arguments

    Returns:
        Resolved Path to config file, or None if not found
    """
    config_path = Path(config_arg)

    if config_path.is_absolute():
        return config_path if config_path.exists() else None

    # Try relative to project root (uses detected root for both dev/installed)
    project_root_config = _PROJECT_ROOT / config_path
    if project_root_config.exists():
        return project_root_config

    # Try relative to current directory
    cwd_config = Path.cwd() / config_path
    if cwd_config.exists():
        return cwd_config

    return None


def initialize_server(args: argparse.Namespace, logger: logging.Logger) -> ServerState:
    """
    Initialize server state from parsed arguments.

    Args:
        args: Parsed command-line arguments
        logger: Logger instance for logging operations

    Returns:
        Initialized ServerState instance

    Raises:
        SystemExit: If initialization fails
    """
    try:
        # Resolve configuration file path
        config_path = resolve_config_path(args.config)

        # Load search weights with precedence: CLI > YAML > defaults
        weights = ConfigLoader.load_weights(
            config_path=config_path,
            cli_overrides={"w_kw": args.w_kw, "w_exact": args.w_exact, "w_bm25": args.w_bm25, "w_sem": args.w_sem},
            logger=logger,
        )

        logger.info(f"Search weights: {weights.to_dict()}")

        # Load query instruction with precedence: CLI > YAML > default (None)
        query_instruction = ConfigLoader.load_query_instruction(
            config_path=config_path,
            cli_override=args.query_instruction,
            logger=logger,
        )

        logger.info(f"Query instruction: {'enabled' if query_instruction else 'disabled'}")

        # Resolve registry-docs cache config (grep_module_docs) with precedence: YAML > defaults
        doc_cache_dir, doc_cache_ttl_hours = ConfigLoader.load_doc_cache(
            config_path=config_path,
            logger=logger,
        )

        logger.info(f"Doc cache: dir={doc_cache_dir}, ttl_hours={doc_cache_ttl_hours}")

        # Resolve index path using shared logic from tfmod_search_lib
        index_path = resolve_index_path(args.index_path)

        # Check if index file exists
        if not index_path.exists():
            logger.error(
                f"Index file not found at: {index_path}\n"
                f"Please specify a valid path using --index_path argument or ensure "
                f"the default index exists at ./model/tfmod_e5_small_index.pkl"
            )
            sys.exit(1)

        # Load the index
        logger.info(f"Loading index from: {index_path}")
        index = load_index(str(index_path), logger)
        logger.info(f"Index loaded successfully: {len(index.docs)} documents")

        # Initialize server state
        state = ServerStateManager.initialize(
            index=index,
            weights=weights,
            index_path=index_path,
            query_instruction=query_instruction,
            logger=logger,
            doc_cache_dir=doc_cache_dir,
            doc_cache_ttl_hours=doc_cache_ttl_hours,
        )

        logger.info(f"Server initialized successfully: {state}")
        return state

    except Exception as e:
        logger.error(f"Failed to initialize server: {e}", exc_info=True)
        sys.exit(1)


def main() -> None:
    """Main entry point for the MCP server."""
    logger = None
    try:
        # Parse command-line arguments first (needed for config path, and so
        # proxy mode can exit before any index/model/NLTK initialization).
        args = parse_arguments()

        if args.proxy_url:
            # Lightweight stdio->HTTP forwarder: no NLTK, no config, no index,
            # no embedding model. The daemon at proxy_url owns all of that.
            # (The truly light path is tfmod_entry, which dispatches here-equivalent
            # logic without ever importing this module and its ML stack.)
            from tfmod_proxy import run_proxy

            run_proxy(args.proxy_url, log_level=args.log_level)
            return

        # Initialize NLTK before any search operations
        initialize_nltk()

        # Load log level from config with CLI override
        config_path = Path(args.config) if args.config else None
        log_level = ConfigLoader.load_log_level(
            config_path=config_path,
            cli_override=args.log_level,
        )

        # Set up logging to startup.log with configured level
        logger = setup_logging("startup.log", log_level=log_level)
        logger.info("=" * 80)
        logger.info("MCP Server starting up...")

        # Initialize server state (all startup errors go to startup.log)
        state = initialize_server(args, logger)

        if args.warmup:
            logger.info("Warmup requested: loading embedding model via test query")
            result = search_modules_impl("vpc networking", state)
            logger.info(f"Warmup complete: test query returned {len(result.results)} results")
            print(
                f"Warmup complete: index ({len(state.index.docs)} modules) and "
                f"embedding model loaded, test query returned {len(result.results)} results."
            )
            return

        # Switch to operational logging after successful initialization
        logger.info("Initialization complete, switching to mcp_server.log")
        switch_log_file("mcp_server.log")
        logger = logging.getLogger(__name__)
        logger.info("=" * 80)
        logger.info("MCP Server operational logging started")

        # Start FastMCP server
        if args.transport == "http":
            if not _is_loopback(args.host):
                logger.warning(
                    f"Binding non-loopback host {args.host} with NO authentication - anyone who can "
                    "reach this address can query the server. Intended only inside a container whose "
                    "host port mapping restricts exposure (e.g. -p 127.0.0.1:8765:8765)."
                )
            # Warm once, BEFORE serving: the whole point of the shared instance is a
            # single deterministic model load; stdio keeps its lazy load untouched.
            logger.info("HTTP mode: warming up embedding model before serving")
            warm = search_modules_impl("vpc networking", state)
            logger.info(f"Warmup complete: test query returned {len(warm.results)} results")
            logger.info(f"READY on http://{args.host}:{args.port}/mcp")
            if _update_check_enabled(os.environ):
                logger.info("Update check enabled: daily PyPI version check (TFMODSEARCH_UPDATE_CHECK=0 to disable)")
                _start_update_checker_thread()
            else:
                logger.info("Update check disabled via TFMODSEARCH_UPDATE_CHECK")
            # host_origin_protection="auto" installs FastMCP Host/Origin validation
            # (rejects browser-initiated cross-origin requests -> DNS-rebinding guard).
            # Orthogonal to auth: SDK clients and curl send no Origin and pass.
            app.run(transport="http", host=args.host, port=args.port, host_origin_protection="auto")
        else:
            logger.info("Starting MCP server (stdio transport)")
            app.run(transport="stdio")

    except KeyboardInterrupt:
        if logger:
            logger.info("Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        else:
            # Fallback if logging wasn't set up yet
            print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
