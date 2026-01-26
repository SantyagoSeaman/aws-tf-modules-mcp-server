#!/usr/bin/env python3
"""
TFModSearch MCP Server (stdio) using fastmcp.

Tools exposed:
- search_modules(query: str) -> top-3 ranked hits
- get_module(module_identifier: str) -> full module documentation

The server requires an index file specified via --index_path argument or uses default location.
Search scoring weights are loaded from config.yaml and can be overridden via CLI arguments.
"""

import argparse
import logging
import sys
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Annotated, Any

import yaml
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field, field_serializer

from tfmod_search_lib import (
    _PROJECT_ROOT,
    BGE_QUERY_INSTRUCTION,
    SearchIndex,
    compute_scores,
    extract_description,
    extract_purpose,
    initialize_nltk,
    load_index,
    resolve_index_path,
    setup_logging,
    switch_log_file,
)

app = FastMCP(
    name="tfmod-search-mcp",
    version="0.1.0",
    instructions="""
# Terraform AWS Module Search Server

This MCP server provides intelligent search and retrieval for Terraform AWS modules documentation using hybrid search.

## Available Tools

### modules_list()
List all available Terraform modules in the catalog.

**When to use:**
- Discover what modules exist before searching
- Browse the complete catalog of available modules
- Get an overview of all indexed documentation

**Parameters:** None

**Returns:** Complete list of modules with names, paths, descriptions, and keywords.

### search_modules(query: str)
Search for Terraform AWS modules using natural language queries, keywords, or exact module names.

**When to use:**
- Finding modules by functionality: "s3 bucket with encryption"
- Searching by technology: "kubernetes cluster", "serverless functions"
- Locating modules by exact name: "vpc", "eks", "lambda"
- When user try to find Terraform resources by it may be more efficient to use module

**Returns:** Top-3 ranked modules with name, path, keywords, description, and relevance score.

**Best practices:**
- Use descriptive queries for better results: "object storage with versioning" > "storage"
- Include key requirements: "vpc with multiple availability zones"
- Try exact module names first if known: "vpc", "s3-bucket"
- Use direct links to documentation for sub-modules with full lists of inputs/outputs

## Available Tools (continued)

### get_module(module_identifier: str)
Retrieve full documentation for a specific Terraform module.

**When to use:**
- After search_modules to get complete documentation
- When you need detailed usage examples, inputs, outputs
- To understand module configuration options

**Accepts:**
- Module name: `"vpc"`, `"s3-bucket"`, `"eks"`
- File path: `"modules/terraform-aws-modules/vpc.md"`

**Returns:** Complete module documentation without truncation.

## Recommended Workflow

1. **Browse Catalog (Optional):** Use `modules_list` to see all available modules
   - Example: modules_list() → returns complete catalog with all 6 modules

2. **Search:** Use `search_modules` to find relevant modules
   - Example: search_modules("container orchestration") → returns EKS module

3. **Deep Dive:** Use `get_module` to get full documentation
   - Example: get_module("eks") → full EKS module docs with all inputs/outputs

4. **Iteration:** Refine search if needed
   - Too broad: Add more specific terms
   - Too narrow: Use broader/alternative terms

## Search Tips

- **Functionality-based:** "database subnet routing", "load balancer configuration"
- **Technology-based:** "kubernetes", "serverless", "nosql"
- **Feature-based:** "encryption", "monitoring", "high availability"
- **AWS service names:** "s3", "rds", "lambda", "vpc"
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
    """

    def __init__(
        self,
        index: SearchIndex | None,
        weights: SearchWeights,
        index_path: Path,
        query_instruction: str | None = None,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize server state.

        Args:
            index: Loaded search index (can be None for testing)
            weights: Search weights configuration
            index_path: Path to index file
            query_instruction: Optional query instruction prefix for BGE models
            logger: Logger instance for logging operations
        """
        self._index = index
        self._weights = weights
        self._index_path = index_path
        self._query_instruction = query_instruction
        self._lock = threading.RLock()
        self._logger = logger

        doc_count = len(index.docs) if index is not None else 0
        if self._logger:
            self._logger.info(
                f"ServerState initialized: index_path={index_path}, "
                f"docs={doc_count}, weights={weights.to_dict()}, "
                f"query_instruction={'set' if query_instruction else 'disabled'}"
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

    def reload_index(self, new_index_path: Path | None = None) -> None:
        """
        Reload index from file (thread-safe).

        Args:
            new_index_path: Path to new index file (uses current path if None)

        Raises:
            ValueError: If index file not found or invalid
        """
        assert self._logger is not None, "ServerState must have a logger"
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

        Returns:
            Initialized ServerState instance

        Raises:
            RuntimeError: If already initialized
        """
        with cls._lock:
            if cls._instance is not None:
                raise RuntimeError("ServerState already initialized")
            cls._instance = ServerState(index, weights, index_path, query_instruction, logger)
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

    @field_serializer("score")
    def serialize_score(self, value: float) -> float:
        """Round score to 2 decimal places for JSON output."""
        return round(value, 2)


class SearchOutput(BaseModel):
    results: list[SearchHit] = Field(..., description="Top-3 ranked Terraform modules matching the query.")


class ModuleListItem(BaseModel):
    module_name: str = Field(..., description="Terraform module name (e.g., 'eks', 's3-bucket').")
    path: str = Field(..., description="File path to module documentation.")
    description: str = Field(..., description="Module description extracted from documentation text.")
    keywords: list[str] = Field(..., description="Module keywords/tags.")


class ModulesListOutput(BaseModel):
    modules: list[ModuleListItem] = Field(..., description="Complete list of all available Terraform modules.")
    count: int = Field(..., description="Total number of modules in the catalog.")


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
        raise ValueError(f"Access denied: Path must be under 'modules/' directory. " f"Attempted: {path_str}") from err

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
    assert state.logger is not None, "ServerState must have a logger"

    # Determine strategy based on identifier format
    is_path = "/" in module_identifier or module_identifier.endswith(".md")

    if is_path:
        # Strategy 1: Direct file path access
        full_path = _validate_and_resolve_module_path(module_identifier)
        return _read_module_file(full_path, module_identifier, state.logger)

    # Strategy 2: Search by module name
    weights = state.weights
    results = compute_scores(
        state.index,
        module_identifier,
        w_kw=weights.w_kw,
        w_exact=weights.w_exact,
        w_bm25=weights.w_bm25,
        w_sem=weights.w_sem,
        top_k=1,
        query_instruction=state.query_instruction,
        logger=state.logger,
    )

    if not results:
        raise ValueError(f"No module found matching: {module_identifier}")

    # Get the top result and read its documentation
    _, doc_idx = results[0]
    doc = state.index.docs[doc_idx]

    # Validate and read the module file
    full_path = (_PROJECT_ROOT / doc.path).resolve()
    return _read_module_file(full_path, doc.module_name or doc.path, state.logger)


def search_modules_impl(query: str, state: ServerState) -> SearchOutput:
    """
    Helper function to search for modules.

    This function is testable (not decorated) and can be called directly
    with a ServerState instance for testing.

    Args:
        query: Search query string
        state: Server state containing index and configuration

    Returns:
        SearchOutput with top-3 ranked results

    See search_modules() tool documentation for full details.
    """
    assert state.logger is not None, "ServerState must have a logger"

    # Use configured weights from state
    weights = state.weights
    results = compute_scores(
        state.index,
        query,
        w_kw=weights.w_kw,
        w_exact=weights.w_exact,
        w_bm25=weights.w_bm25,
        w_sem=weights.w_sem,
        top_k=3,  # Always return top-3
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
            )
        )

    state.logger.debug(f"Search for '{query}' returned {len(out)} results")
    return SearchOutput(results=out)


def get_module_impl(module_identifier: str, state: ServerState) -> str:
    """
    Helper function to get module documentation.

    This function is testable (not decorated) and can be called directly
    with a ServerState instance for testing.

    Args:
        module_identifier: Module name or relative file path
        state: Server state containing index and configuration

    Returns:
        Full module documentation text

    See get_module() tool documentation for full details.
    """
    return get_module_documentation(module_identifier, state)


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
    assert state.logger is not None, "ServerState must have a logger"

    state.logger.debug(f"Listing all modules: {len(state.index.docs)} documents")

    modules: list[ModuleListItem] = []
    for doc in state.index.docs:
        # Extract purpose from Module Information section
        description = extract_purpose(doc.text)

        modules.append(
            ModuleListItem(
                module_name=doc.module_name or "", path=doc.path, description=description, keywords=doc.keywords or []
            )
        )

    state.logger.debug(f"Modules list generated: {len(modules)} items")

    return ModulesListOutput(modules=modules, count=len(modules))


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
        "Returns top-3 ranked results with module name, path, keywords, description, and relevance score. "
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

    Returns:
        SearchOutput: Container with top-3 ranked results. Each result includes:
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
        - Always returns exactly 3 results (or fewer if index has < 3 modules)
        - Results are ranked by combined score from multiple search components
        - Search weights are configured server-wide and cannot be changed per-query
        - Empty queries return empty results
    """
    state = ServerStateManager.get()
    return search_modules_impl(query, state)


@app.tool(
    description=(
        "Get compacted documentation for a specific Terraform module. "
        "Use this tool after search_modules to retrieve module documentation including "
        "usage examples, inputs, outputs, and configuration details. "
        "To get original documentation including full lists inputs/outputs for each sub-module, "
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
) -> str:
    """
    Get full documentation for a specific Terraform module.

    Retrieves the complete documentation text for a Terraform module identified
    by either its name or file path. This provides access to full module
    documentation without ranking or truncation.

    Args:
        module_identifier: Either:
            - Module name (e.g., "vpc", "s3-bucket", "eks")
            - Relative path to module file (e.g., "modules/terraform-aws-modules/vpc.md")

    Returns:
        str: Full documentation text from the module's Markdown file

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
        Get module by name:
            Input: "vpc"
            Returns: Full VPC module documentation

        Get module by path:
            Input: "modules/terraform-aws-modules/s3-bucket.md"
            Returns: Full S3 bucket module documentation

        Typical workflow:
            1. search_modules("s3 encryption") → get top result path
            2. get_module(path) → retrieve full documentation
    """
    state = ServerStateManager.get()
    return get_module_impl(module_identifier, state)


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
        help="Path to the search index file (.pkl). Defaults to './model/tfmod_bge_base_index.pkl'",
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

    return parser.parse_args()


def resolve_config_path(config_arg: str) -> Path | None:
    """
    Resolve configuration file path.

    Tries multiple locations:
    1. Absolute path if provided
    2. Relative to project root (parent of src/)
    3. Relative to current directory

    Args:
        config_arg: Config path from command line arguments

    Returns:
        Resolved Path to config file, or None if not found
    """
    script_dir = Path(__file__).parent
    config_path = Path(config_arg)

    if config_path.is_absolute():
        return config_path if config_path.exists() else None

    # Try relative to project root
    project_root_config = script_dir.parent / config_path
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

        # Resolve index path using shared logic from tfmod_search_lib
        index_path = resolve_index_path(args.index_path)

        # Check if index file exists
        if not index_path.exists():
            logger.error(
                f"Index file not found at: {index_path}\n"
                f"Please specify a valid path using --index_path argument or ensure "
                f"the default index exists at ./model/tfmod_bge_base_index.pkl"
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

        # Set up logging to startup.log first
        logger = setup_logging("startup.log", log_level=logging.getLevelName(logging.DEBUG))
        logger.info("=" * 80)
        logger.info("MCP Server starting up...")

        # Parse command-line arguments
        args = parse_arguments()

        # Initialize server state (all startup errors go to startup.log)
        initialize_server(args, logger)

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
