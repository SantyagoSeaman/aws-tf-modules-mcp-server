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
import logging
import os
import re
import sys
import threading
from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Annotated, Any

import yaml
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field, field_serializer

import tfmod_registry_docs
from tfmod_doc_grep import grep_document
from tfmod_registry_docs import get_assembled_docs
from tfmod_search_lib import (
    _PROJECT_ROOT,
    BGE_QUERY_INSTRUCTION,
    SearchIndex,
    compute_scores,
    extract_description,
    extract_purpose,
    initialize_nltk,
    load_index,
    normalize_modname,
    resolve_index_path,
    setup_logging,
    switch_log_file,
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

## Curated AWS catalog (offline, compact) — 54 community terraform-aws-modules

1. `search_modules(query, top_k=3)` — find the right module. Returns the
   top-ranked matches (default 3, up to 10) with name, path, keywords,
   description, relevance score, and `module_id`/`latest_version` (registry
   coordinates for chaining into `grep_module_docs`). Query by functionality
   ("s3 bucket with encryption and versioning"), technology ("kubernetes
   cluster"), or exact module name ("vpc", "eks").
2. `get_module(module_identifier, sections=None)` — orient on the chosen
   module. Accepts a module name ("vpc") or a relative doc path
   ("modules/terraform-aws-modules/vpc.md"). By default returns a compact
   orientation head — description, module info, exact version pin, agent
   notes, any gotchas, key features, use cases — plus a footer with the full
   section inventory (an explicit menu of logical keys + headings). Pass
   `sections` (e.g. ["inputs", "examples"]) to pull specific parts, or
   `sections=["all"]` for the full document; prefer scoped `sections` over
   "all" on large modules.
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

## Search Tips

- Descriptive queries beat single words: "object storage with versioning" > "storage"
- Include key requirements: "vpc with multiple availability zones"
- Exact module names work too: "vpc", "s3-bucket", "rds"
- If results are too broad, add specific terms; too narrow, use broader ones
""",
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


class SearchOutput(BaseModel):
    results: list[SearchHit] = Field(..., description="Top-ranked Terraform modules matching the query.")


class ModuleListItem(BaseModel):
    module_name: str = Field(..., description="Terraform module name (e.g., 'eks', 's3-bucket').")
    path: str = Field(..., description="File path to module documentation.")
    description: str = Field(..., description="Module description extracted from documentation text.")
    keywords: list[str] = Field(..., description="Module keywords/tags.")
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


class ModulesListOutput(BaseModel):
    modules: list[ModuleListItem] = Field(..., description="Complete list of all available Terraform modules.")
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


class CacheInfo(BaseModel):
    hit: bool = Field(..., description="Whether the assembled document was served from the on-disk/memory cache.")
    fetched_at: str = Field(..., description="ISO-8601 timestamp of the underlying registry fetch.")
    policy: str = Field(
        ..., description="Cache policy applied: 'pinned' (immutable, cached forever) or 'latest-ttl' (TTL-based)."
    )


class GrepOutput(BaseModel):
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


def _matches_combined_interface(title_lower: str) -> bool:
    """True for headings that carry the interface outside the split scheme."""
    return title_lower.startswith(_COMBINED_INTERFACE_PREFIXES)


def _version_pin_hint(text: str) -> str | None:
    """
    Build an actionable exact-pin line from the doc's `**Latest Version**` bullet.

    Agents that read only the module body tend to copy the `~> X.0` range shown
    in usage examples and pin a floor instead of the exact latest release. This
    surfaces the concrete version up front so an exact pin is the obvious choice.
    Returns None when the doc carries no parseable Latest Version bullet.
    """
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


def filter_module_sections(text: str, requested: list[str]) -> str:
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

    Returns:
        Filtered document text; the original text if it has no H2 sections
    """
    preamble, sections = _split_h2_sections(text)
    if not sections:
        return text

    wanted: set[str] = {title for title, _ in sections if title in _CORE_SECTIONS}
    unmatched: list[str] = []
    for entry in requested:
        key = entry.strip().lower()
        if not key:
            continue
        canonical = _SECTION_ALIASES.get(key)
        matched = False
        for title, _ in sections:
            if canonical is not None:
                hit = title == canonical or (canonical == "Submodules" and title.lower().startswith("submodule"))
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
            for title, _ in sections:
                if _matches_combined_interface(title.lower()):
                    wanted.add(title)
                    matched = True
        if not matched:
            unmatched.append(entry)

    parts = [preamble.rstrip()] if preamble.strip() else []
    parts.extend(block.rstrip() for title, block in sections if title in wanted)

    # Always advertise the complete section inventory so the agent has an explicit
    # menu for follow-up get_module(sections=[...]) calls — not just what was
    # omitted from this particular response.
    all_titles = [title for title, _ in sections]
    omitted = [title for title in all_titles if title not in wanted]

    footer_lines = [
        "---",
        # Honest-limits pointer: the curated doc is a hand-picked SUBSET. Anything
        # requiring completeness or exactness lives one tier down (live registry),
        # and resource-creation conditions live in module source. Keeps the
        # compact→full→source escalation a mechanical decision, not a guess.
        "This is TFModSearch's curated summary (a selected subset of the module's inputs/"
        "outputs). For the COMPLETE inputs/outputs — every variable with its exact type and "
        "default — plus all examples, grep the live registry doc with `grep_module_docs` "
        "using the Module ID above. Resource-creation conditions (whether an input gates a "
        "`count`/`for_each` resource) live in the module source, not the rendered doc. Do "
        "not assert an exact default, type, or that an input exists from this summary or from "
        "memory when a wrong value would break `apply` — confirm it in the full doc first.",
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


def search_modules_impl(query: str, state: ServerState, top_k: int = 3) -> SearchOutput:
    """
    Helper function to search for modules.

    This function is testable (not decorated) and can be called directly
    with a ServerState instance for testing.

    Args:
        query: Search query string
        state: Server state containing index and configuration
        top_k: Number of results to return (clamped to 1..10, default 3)

    Returns:
        SearchOutput with top-k ranked results

    See search_modules() tool documentation for full details.
    """
    assert state.logger is not None, "ServerState must have a logger"  # noqa: S101

    top_k = max(1, min(int(top_k), 10))

    # Use configured weights from state
    weights = state.weights
    results = compute_scores(
        state.index,
        query,
        w_kw=weights.w_kw,
        w_exact=weights.w_exact,
        w_bm25=weights.w_bm25,
        w_sem=weights.w_sem,
        top_k=top_k,
        query_instruction=state.query_instruction,
        logger=state.logger,
    )

    out: list[SearchHit] = []
    for score, i in results:
        d = state.index.docs[i]
        # Extract description from document text
        description = extract_description(d.text)

        out.append(
            SearchHit(
                module_name=d.module_name or "",
                path=d.path,
                keywords=d.keywords or [],
                description=description,
                score=float(score),
                module_id=getattr(d, "module_id", ""),
                latest_version=getattr(d, "latest_version", ""),
            )
        )

    state.logger.debug(f"Search for '{query}' returned {len(out)} results")
    return SearchOutput(results=out)


def orientation_head(text: str) -> str:
    """
    Build the compact orientation view returned by get_module by default.

    Combines the always-included core sections (Description, Module Information,
    Notes for AI Agents, and Important Gotchas where the doc has it) with Key
    Features and Main Use Cases, prepends an actionable exact-version pin hint,
    and appends a footer listing
    every omitted section as a table of contents. Keeps a first orientation call
    small — what the module is plus how to reach the rest — instead of returning
    the full body, which runs to ~12k tokens for the largest modules.
    """
    body = filter_module_sections(text, list(_ORIENTATION_KEYS))
    hint = _version_pin_hint(text)
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

    See get_module() tool documentation for full details.
    """
    content = get_module_documentation(module_identifier, state)
    if sections:
        if any(entry.strip().lower() in _FULL_DOC_KEYS for entry in sections):
            return content
        return filter_module_sections(content, sections)
    return orientation_head(content)


def modules_list_impl(state: ServerState) -> ModulesListOutput:
    """
    Helper function to list all available modules.

    This function is testable (not decorated) and can be called directly
    with a ServerState instance for testing.

    Args:
        state: Server state containing index and configuration

    Returns:
        ModulesListOutput with complete catalog of all modules

    See modules_list() tool documentation for full details.
    """
    assert state.logger is not None, "ServerState must have a logger"  # noqa: S101

    state.logger.debug(f"Listing all modules: {len(state.index.docs)} documents")

    modules: list[ModuleListItem] = []
    for doc in state.index.docs:
        # Extract purpose from Module Information section
        description = extract_purpose(doc.text)

        modules.append(
            ModuleListItem(
                module_name=doc.module_name or "",
                path=doc.path,
                description=description,
                keywords=doc.keywords or [],
                module_id=getattr(doc, "module_id", ""),
                latest_version=getattr(doc, "latest_version", ""),
            )
        )

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
        GrepMatch(section=m.section, line_number=m.line_number, line=m.line, before=m.before, after=m.after)
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
        "Returns complete list of modules with names, paths, descriptions, and keywords. "
        "Use this to discover what modules are available before searching or retrieving documentation. "
        "If there are no required module, please search in Terraform Registry (https://registry.terraform.io/)."
    ),
    tags={"catalog", "list", "terraform", "aws", "modules"},
    annotations=ToolAnnotations(title="List all available Terraform modules"),
)
def modules_list() -> ModulesListOutput:
    """
    List all available Terraform modules in the catalog.

    Returns a complete catalog of all indexed Terraform modules with their
    metadata (name, path, description, keywords). This tool requires no
    parameters and provides a full directory listing of available modules.

    Returns:
        ModulesListOutput: Complete catalog with:
            - modules: List of all modules with metadata
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
    return modules_list_impl(state)


@app.tool(
    description=(
        "Search for Terraform AWS modules by keywords, exact name, or free-text query. "
        "Returns top-ranked results (top_k, default 3) with module name, path, keywords, "
        "description, and relevance score. "
        "After finding modules, use get_module tool to retrieve brief documentation."
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

    Returns:
        SearchOutput: Container with top-k ranked results. Each result includes:
            - module_name: Normalized module identifier (e.g., "s3-bucket", "eks")
            - path: Relative path to module documentation file
            - keywords: List of extracted module keywords/tags
            - description: Extracted module description (up to 200 chars)
            - score: Combined relevance score (higher = more relevant)

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
    return search_modules_impl(query, state, top_k=top_k)


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
            description="Module identifier: either module name (e.g., 'vpc', 's3-bucket') "
            "or relative path (e.g., 'modules/terraform-aws-modules/vpc.md')"
        ),
    ],
    sections: Annotated[
        list[str] | None,
        Field(
            description="Optional list of sections to return. Accepts logical keys — inputs, "
            "outputs, examples, submodules, features, use-cases, best-practices, resources — "
            "or case-insensitive substrings of section headings (e.g. 'karpenter' for a single "
            "EKS submodule); the inputs/outputs/examples keys also resolve on modules that bundle "
            "them into a combined section. Core context (description, module info, version pin, "
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
        module_identifier: Either:
            - Module name (e.g., "vpc", "s3-bucket", "eks")
            - Relative path to module file (e.g., "modules/terraform-aws-modules/vpc.md")
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

        Typical workflow:
            1. search_modules("s3 encryption") → get top result path
            2. get_module(path) → orient (compact head)
            3. get_module(path, sections=["inputs"]) → pull the details you need
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
        "default without guessing from training data."
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
        GrepOutput: matches (with section label, line number, and context),
            total_matches/returned_matches/truncated, resolved_version,
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
    return grep_module_docs_impl(
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


# -----------------------------
# Initialization and Entry Point
# -----------------------------


def parse_arguments() -> argparse.Namespace:
    """
    Parse and return command-line arguments.

    Returns:
        Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="TFModSearch MCP Server - Terraform module search over stdio",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--index_path",
        type=str,
        help="Path to the search index file (.pkl). Defaults to './model/tfmod_e5_small_index.pkl'",
    )
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to YAML config file")
    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument("--w_kw", type=float, help="Override weight for keyword matching")
    parser.add_argument("--w_exact", type=float, help="Override weight for exact module name match")
    parser.add_argument("--w_bm25", type=float, help="Override weight for BM25 text relevance")
    parser.add_argument("--w_sem", type=float, help="Override weight for semantic similarity")
    parser.add_argument(
        "--query-instruction",
        dest="query_instruction",
        type=str,
        default=None,
        help=f"Optional query instruction prefix for BGE models. Use '{BGE_QUERY_INSTRUCTION}' for improved short query retrieval",
    )
    parser.add_argument(
        "--warmup",
        action="store_true",
        help="Load the index and embedding model (downloading the model if needed), run a test query, and exit",
    )

    return parser.parse_args()


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
        # Initialize NLTK before any operations
        initialize_nltk()

        # Parse command-line arguments first (needed for config path)
        args = parse_arguments()

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
