# TFModSearch MCP Server

[![CI](https://github.com/SantyagoSeaman/tfmodsearch/actions/workflows/ci.yml/badge.svg)](https://github.com/SantyagoSeaman/tfmodsearch/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tfmodsearch)](https://pypi.org/project/tfmodsearch/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **Model Context Protocol (MCP)** server that provides intelligent search capabilities for Terraform AWS module documentation using hybrid search (keyword matching, BM25, and semantic embeddings).

**Ready to Use**: Includes a pre-built search index with embeddings for 54 curated Terraform AWS modules. Install and run the MCP server immediately—no index building required!

## 🤔 Why TFModSearch?

When an AI assistant writes Terraform, it often guesses at module names, invents variables that don't exist, or reaches for outdated syntax. TFModSearch gives your assistant a **curated, versioned, offline knowledge base** of the official [`terraform-aws-modules`](https://github.com/terraform-aws-modules) so it can:

- **Find the right module from intent** — "I need a Redis cache" resolves to `elasticache`, not a hallucinated module name.
- **Ground generated code in real inputs/outputs** — the assistant pulls the full, current module documentation (submodules, variables, outputs, examples) on demand instead of improvising.
- **Stay fast, private, and deterministic** — search runs locally on CPU against a pre-built index. No external API calls, no rate limits, no network round-trips.

Think of it as an always-available, searchable reference card for every terraform-aws-modules module — kept accurate and shipped ready to run.

## 🚀 Features

- **Hybrid Search Engine**: Combines keyword matching (IDF-weighted), BM25 text relevance, exact module name matching, and semantic similarity for accurate results
- **MCP Integration**: Seamlessly integrates with Claude Desktop and other MCP clients
- **Fast & Efficient**: Pre-built search index with CPU-only inference using `intfloat/e5-small-v2` model
- **Ready to Use**: Includes pre-built index (`model/tfmod_e5_small_index.pkl`) with embeddings from `intfloat/e5-small-v2` model and curated Terraform AWS module documentation
- **Comprehensive Catalog**: Access to terraform-aws-modules documentation compiled from official sources with rich metadata
- **Security-First**: Built-in path validation and access controls for safe file operations
- **Configurable Weights**: Fine-tune search scoring through YAML config or CLI arguments

## 📋 Table of Contents

- [Why TFModSearch?](#-why-tfmodsearch)
- [Installation](#-installation)
  - [Plugin Install (Claude Code / Codex)](#plugin-install-claude-code--codex--recommended)
  - [Quick Install (Any MCP Client)](#quick-install-any-mcp-client)
- [Quick Start](#-quick-start)
  - [Claude Code CLI Integration](#claude-code-cli-integration)
  - [Claude Desktop Integration](#claude-desktop-integration)
  - [Codex CLI Integration](#codex-cli-integration)
  - [GitHub Copilot Integration](#github-copilot-integration-vs-code)
- [Usage](#-usage)
  - [Building the Index](#1-building-the-index)
  - [CLI Search](#2-cli-search-standalone)
- [MCP Tools](#-mcp-tools)
- [Configuration](#️-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [Architecture](#-architecture)
  - [Indexed Modules](#indexed-modules)
- [Contributing](#-contributing)
- [License](#-license)

## 📦 Installation

### Plugin Install (Claude Code / Codex — Recommended)

The plugin configures the MCP server automatically **and** adds workflow skills that make the agent search current module documentation before writing Terraform.

**Claude Code:**
```
/plugin marketplace add SantyagoSeaman/tfmodsearch
/plugin install tfmod-search@tfmodsearch
```

**Codex CLI:**
```
/plugin marketplace add SantyagoSeaman/tfmodsearch
/plugin install tfmod-search@tfmodsearch
```

Both bundle:
- The **tfmod-search MCP server** (runs via `uvx tfmodsearch` — [uv](https://github.com/astral-sh/uv) required)
- **Seven skills**:
  - `aws-terraform-modules` — auto-invoked when writing Terraform for AWS: search first, write from current docs, pin versions
  - `/tf-module <query>` — instant module lookup with a ready-to-paste snippet
  - `/tf-stack <requirement>` — scaffold a multi-module stack with correct output→input wiring
  - `tf-migrate` — replace hand-written `aws_*` resources with a covering module, verified attribute-by-attribute
  - `tf-module-upgrade` — audit pinned versions and variable usage against current docs
  - `tf-review` — review a diff or PR's module usage
  - `tf-troubleshoot` — diagnose terraform failures; ships a prefilter script that reduces logs of any size to just the diagnostics
- **Two subagents** (Claude Code): `tf-log-analyst` and `tf-diff-reviewer` analyze large logs and diffs in an isolated context, so your session only sees the findings

### Quick Install (Any MCP Client)

The server is on PyPI — no need to clone the repository.

**Install uv first** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then add to your MCP client config:

```json
{
  "mcpServers": {
    "terraform-modules": {
      "command": "uvx",
      "args": ["tfmodsearch"]
    }
  }
}
```

> **Tip**: Run `uvx tfmodsearch --warmup` once after installing — it pre-downloads the embedding model (~130 MB) and verifies the server end-to-end, so the first real query is instant.

> **Bundled and ready**: The pre-built search index and all 54 module docs ship *inside* the package, so `uvx` fetches, installs, and runs the server with nothing to clone or rebuild. (The `intfloat/e5-small-v2` embedding model — ~130 MB — is downloaded automatically on the first search to encode your query, then cached for subsequent queries.)

> **Note**: If you get "command not found" error, use the full path to `uvx`:
> ```bash
> # Find uvx location
> which uvx
> # Example output: /Users/username/.local/bin/uvx
> ```
> Then use the full path in your config:
> ```json
> "command": "/Users/username/.local/bin/uvx"
> ```

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Local Installation (For Development)

```bash
# Clone the repository
git clone https://github.com/SantyagoSeaman/tfmodsearch.git
cd tfmodsearch

# Create virtual environment and install dependencies
uv venv --python 3.13
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/SantyagoSeaman/tfmodsearch.git
cd tfmodsearch

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

**Ready to Go**: The repository includes a pre-built search index, so you can skip the index building step and run the MCP server immediately after installation!

## 🏃 Quick Start

### 1. Build the Search Index (Optional)

**Note**: This repository includes a pre-built search index at `model/tfmod_e5_small_index.pkl` with embeddings for 54 curated Terraform AWS modules. You can skip this step and proceed directly to testing or running the server if you want to use the included modules.

To rebuild the index or create a new one with additional modules:

```bash
python src/tfmod_search_cli.py index \
  --docs_dir ./modules/terraform-aws-modules
```

**Note**: The first run will download the `intfloat/e5-small-v2` model (~130MB).

### 2. Test the Search (CLI)

Test the search functionality using the command-line interface:

```bash
python src/tfmod_search_cli.py search \
  --query "s3 bucket with kms encryption and versioning" \
  --top_k 5
```

#### Claude Code CLI Integration

> **Prefer the [plugin install](#plugin-install-claude-code--codex--recommended)** — it configures the server and adds the workflow skills in two commands.

**Option 1: Using uvx (No Clone Required)**

```bash
claude mcp add terraform-modules -- uvx tfmodsearch
```

Or add to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "terraform-modules": {
      "command": "uvx",
      "args": ["tfmodsearch"]
    }
  }
}
```

> **Note**: If `uvx` is not found, use the full path (run `which uvx` to find it):
> ```json
> "command": "/Users/username/.local/bin/uvx"
> ```

**Option 2: Using Local Installation**

```bash
# Add the MCP server (replace with your actual path)
claude mcp add --transport stdio terraform-modules -- \
  /absolute/path/to/tfmodsearch/.venv/bin/python \
  /absolute/path/to/tfmodsearch/src/tfmod_mcp_server.py

# Verify the server was added
claude mcp list
```

Or manually add to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "terraform-modules": {
      "command": "/absolute/path/to/tfmodsearch/.venv/bin/python",
      "args": [
        "/absolute/path/to/tfmodsearch/src/tfmod_mcp_server.py"
      ]
    }
  }
}
```

#### Claude Desktop Integration

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

**Option 1: Using uvx (Recommended - No Clone Required)**

```json
{
  "mcpServers": {
    "terraform-modules": {
      "command": "uvx",
      "args": ["tfmodsearch"]
    }
  }
}
```

> **Note**: If `uvx` is not found, use the full path (run `which uvx` to find it):
> ```json
> "command": "/Users/username/.local/bin/uvx"
> ```

**Option 2: Using Local Installation**

```json
{
  "mcpServers": {
    "terraform-modules": {
      "command": "/absolute/path/to/tfmodsearch/.venv/bin/python",
      "args": [
        "/absolute/path/to/tfmodsearch/src/tfmod_mcp_server.py"
      ]
    }
  }
}
```

#### Codex CLI Integration

> **Prefer the [plugin install](#plugin-install-claude-code--codex--recommended)** — it configures the server and adds the workflow skills in two commands.

For manual setup, register the server globally:

```bash
codex mcp add tfmod-search -- uvx tfmodsearch
```

Or add to `~/.codex/config.toml` (global) or `.codex/config.toml` (per project):

```toml
[mcp_servers.tfmod-search]
command = "uvx"
args = ["tfmodsearch"]
startup_timeout_sec = 30   # default 10s is tight while the embedding model loads
```

> **First run**: execute `uvx tfmodsearch --warmup` once beforehand — it downloads the embedding model (~220 MB) so server startup stays well within the timeout.

To nudge Codex (or any agent) to use the server proactively, add a line to your project's `AGENTS.md` (or `CLAUDE.md` for Claude Code):

```markdown
Before writing Terraform that uses AWS, call the tfmod-search MCP server:
search_modules to find the module, then get_module for current variable
names and versions. Do not write module blocks from memory.
```

#### GitHub Copilot Integration (VS Code)

Add the MCP server to GitHub Copilot in VS Code (requires VS Code 1.99+):

**Step 1**: Create `.vscode/mcp.json` in your project root (or open user-level config via Command Palette: "MCP: Open User Configuration"):

**Option 1: Using uvx (Recommended - No Clone Required)**

```json
{
  "servers": {
    "terraform-modules": {
      "type": "stdio",
      "command": "uvx",
      "args": ["tfmodsearch"]
    }
  }
}
```

> **Note**: If `uvx` is not found, use the full path (run `which uvx` to find it).

**Option 2: Using Local Installation**

```json
{
  "servers": {
    "terraform-modules": {
      "type": "stdio",
      "command": "/absolute/path/to/tfmodsearch/.venv/bin/python",
      "args": [
        "/absolute/path/to/tfmodsearch/src/tfmod_mcp_server.py"
      ]
    }
  }
}
```

**Step 2**: Click the "Start" button that appears at the top of the `mcp.json` file to initialize the server.

**Step 3**: Open GitHub Copilot Chat, select **Agent** mode from the popup menu, and click the tools icon to verify the `terraform-modules` server and its tools are available.

**Alternative setup via Command Palette**:
1. Open Command Palette (`Cmd+Shift+P` on macOS / `Ctrl+Shift+P` on Windows/Linux)
2. Run "MCP: Add Server"
3. Select "stdio" as the server type
4. Enter `terraform-modules` as the server name
5. Enter the Python path as the command
6. Enter the script path as the argument

**Managing MCP Servers**:
- "MCP: List Servers" — view installed servers and available actions
- "MCP: Reset Cached Tools" — refresh tool discovery if tools don't appear
- "MCP: Show Output" — debug server connection issues

For more details, see [VS Code MCP documentation](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) and [GitHub Copilot MCP guide](https://docs.github.com/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp).

## 📖 Usage

### 1. Building the Index

**Note**: The repository includes a pre-built index—you only need to build a new index if you want to add more modules or customize the existing ones.

Build or rebuild the search index from your module documentation:

```bash
python src/tfmod_search_cli.py index \
  --docs_dir ./modules/terraform-aws-modules \
  --index_path ./model/tfmod_e5_small_index.pkl
```

**Options**:
- `--docs_dir`: Directory containing Terraform module markdown files (required)
- `--index_path`: Output path for the pickled index file (optional, defaults to `./model/tfmod_e5_small_index.pkl`)
- `--model`: Sentence transformer model to use (default: `intfloat/e5-small-v2`)

### 2. CLI Search (Standalone)

Search for modules without running the MCP server:

```bash
# Search by functionality
python src/tfmod_search_cli.py search \
  --query "kubernetes cluster management" \
  --top_k 3

# Search by exact module name
python src/tfmod_search_cli.py search \
  --query "vpc" \
  --top_k 5

# Search with custom weights
python src/tfmod_search_cli.py search \
  --query "object storage" \
  --w_kw 2.5 \
  --w_exact 4.0 \
  --w_bm25 1.5 \
  --w_sem 1.0

# Search with optional query instruction for BGE models
python src/tfmod_search_cli.py search \
  --query "s3" \
  --query-instruction "Represent this sentence for searching relevant passages: "
```

## 🛠️ MCP Tools

The MCP server exposes three tools for Terraform module discovery and documentation retrieval:

### `modules_list()`

List all available Terraform modules in the catalog.

**Parameters**: None

**Returns**: Complete list of modules with names, paths, descriptions, and keywords.

**Example**:
```json
{
  "modules": [
    {
      "module_name": "vpc",
      "path": "modules/terraform-aws-modules/vpc.md",
      "description": "Terraform module to create AWS VPC resources...",
      "keywords": ["vpc", "subnet", "networking", "aws"]
    }
  ],
  "count": 54
}
```

### `search_modules(query: str)`

Search for Terraform modules using keywords, exact names, or natural language queries.

**Parameters**:
- `query` (string): Free-text search query

**Returns**: Top-3 ranked modules with metadata and relevance scores.

**Example queries**:
- `"vpc"` - Find VPC module by exact name
- `"object storage with encryption"` - Natural language search
- `"kubernetes cluster management"` - Find EKS module
- `"serverless functions"` - Find Lambda module

### `get_module(module_identifier: str)`

Retrieve full documentation for a specific Terraform module.

**Parameters**:
- `module_identifier` (string): Module name (e.g., `"vpc"`) or relative path (e.g., `"modules/terraform-aws-modules/vpc.md"`)

**Returns**: Complete module documentation as markdown text.

**Security**: Only files under the `modules/` directory are accessible. Absolute paths and path traversal attempts are rejected.

### Typical Workflow

A coding assistant discovers and uses a module in two steps:

1. **Search by intent** — the assistant turns a natural-language need into a module:

   ```
   search_modules("managed kubernetes cluster with node groups")
   → eks (score 8.9), eks-pod-identity (2.1), autoscaling (1.7)
   ```

2. **Fetch the full docs** — it pulls the complete documentation to ground the generated code:

   ```
   get_module("eks")
   → full EKS module reference: inputs, outputs, submodules, and copy-paste HCL examples
   ```

The assistant then writes Terraform using real variable names and current syntax — instead of guessing. `search_modules` returns the top 3 candidates so the assistant can disambiguate between closely related modules (e.g. `alb` vs `elb`, `rds` vs `rds-aurora`) before committing.

## ⚙️ Configuration

### Search Weights Configuration

Create a `config.yaml` file in the project root to customize search scoring weights:

```yaml
# Optional query instruction for BGE models (improves short query retrieval)
# Set to null to disable (default), or use:
# query_instruction: "Represent this sentence for searching relevant passages: "
query_instruction: null

search_weights:
  w_kw: 1.0      # Keyword overlap weight (IDF-weighted)
  w_exact: 3.0   # Exact module name match boost
  w_bm25: 2.0    # BM25 text relevance weight
  w_sem: 3.0     # Semantic similarity weight
```

> The values above are the weights shipped in the repo's `config.yaml` (bundled with the package), so they are what the server uses out of the box.

**Configuration Precedence** (highest to lowest):
1. CLI arguments (`--w_kw`, `--w_exact`, `--query-instruction`, etc.)
2. `config.yaml` file
3. Built-in defaults

### Module Documentation Format

Terraform module documentation files should be Markdown with YAML front-matter:

```yaml
---
module_name: terraform-aws-vpc
keywords: [vpc, subnet, networking, aws]
---

# Terraform AWS VPC Module

Module description and documentation...
```

## 👩‍💻 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/SantyagoSeaman/tfmodsearch.git
cd tfmodsearch

# Install with development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Development Dependencies

The project includes the following development tools:
- **pytest**: Testing framework with async support
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker
- **pre-commit**: Git hooks for code quality

### Code Quality

```bash
# Run linter
ruff check src/ tests/

# Run formatter
ruff format src/ tests/

# Run type checker
mypy src/

# Run all checks (linter + formatter + type checker)
pre-commit run --all-files
```

## 🧪 Testing

The project includes comprehensive integration tests covering all major functionality.

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/integration/test_all_modules_searchable.py -v  # Searchability, all 54 modules (169 tests)
pytest tests/integration/test_model_comparison.py -v -s     # Model comparison (31 tests)
pytest tests/integration/test_mcp_server.py -v              # MCP server tools (23 tests)
pytest tests/integration/test_parse_markdown.py -v          # Markdown parsing (12 tests)
pytest tests/integration/test_cli_index.py -v               # CLI index building (4 tests)

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

### Test Coverage

- **All Modules Searchable** (169 tests): every one of the 54 modules is verified findable by keyword, exact name, and natural-language query (target in top-3), plus catalog metadata and search-quality checks
- **Model Comparison** (31 tests): embedding model performance comparison with timing analysis
- **MCP Server** (23 tests): `search_modules`, `get_module`, and `modules_list` tools, security validation, integration workflows
- **End-to-End** (49 tests): real MCP stdio protocol sessions against a spawned server process, wheel payload and entry-point verification, `uvx` packaged-server smoke test, plugin manifest/skill/agent contracts for Claude Code and Codex, skill-script tests (terraform log prefilter), live plugin install via the `claude` CLI
- **Markdown Parsing** (12 tests): YAML front-matter parsing, description extraction, normalization
- **CLI Index Building** (4 tests): index creation, validation, search integration

**Total**: 288 tests (integration + e2e)

## 🏗️ Architecture

### Included Content

This repository includes:

- **Pre-built Search Index** (`model/tfmod_e5_small_index.pkl`):
  - Ready-to-use search index with pre-computed embeddings using `intfloat/e5-small-v2` model
  - Contains BM25 corpus, semantic vectors, and keyword IDF scores
  - Includes 54 curated Terraform AWS modules
  - File size: ~4.27 MB

- **Curated Module Documentation** (`modules/terraform-aws-modules/`):
  - Compiled documentation for 54 Terraform AWS modules covering compute, storage, networking, databases, security, and more
  - Sourced from official [terraform-aws-modules](https://github.com/terraform-aws-modules) project
  - Formatted as Markdown with YAML front-matter metadata
  - Each module includes comprehensive documentation with best practices, use cases, and examples

### Indexed Modules

The search index includes 54 Terraform AWS modules across multiple service categories. Each module is documented with comprehensive descriptions, best practices, use cases, and integration examples.

**Compute & Containers:**
- `app-runner` - Containerized web application deployments
- `autoscaling` - EC2 Auto Scaling Groups
- `batch` - AWS Batch for batch computing workloads
- `ec2-instance` - EC2 virtual machines
- `ecs` - Elastic Container Service
- `eks` - Elastic Kubernetes Service
- `eks-pod-identity` - EKS Pod Identity configuration
- `lambda` - Serverless functions

**Networking:**
- `alb` - Application Load Balancer
- `customer-gateway` - VPN customer gateway
- `elb` - Classic Load Balancer
- `transit-gateway` - Transit Gateway for network hub
- `vpc` - Virtual Private Cloud
- `vpn-gateway` - VPN Gateway and Site-to-Site VPN

**Storage:**
- `ebs-optimized` - EBS optimization validation
- `ecr` - Elastic Container Registry
- `efs` - Elastic File System
- `fsx` - FSx file systems (Lustre, ONTAP, OpenZFS, Windows)
- `s3-bucket` - S3 object storage

**Databases:**
- `dms` - Database Migration Service
- `dynamodb-table` - DynamoDB NoSQL database
- `elasticache` - ElastiCache (Redis, Memcached)
- `memory-db` - MemoryDB for Redis
- `opensearch` - OpenSearch search and analytics
- `rds` - Relational Database Service
- `rds-aurora` - Aurora serverless databases
- `rds-proxy` - RDS Proxy for connection pooling
- `redshift` - Redshift data warehouse

**Security & Identity:**
- `acm` - AWS Certificate Manager
- `iam` - Identity and Access Management
- `key-pair` - EC2 key pairs
- `kms` - Key Management Service
- `secrets-manager` - Secrets Manager
- `security-group` - VPC security groups

**Monitoring & Logging:**
- `cloudwatch` - CloudWatch logs and metrics
- `datadog-forwarders` - Datadog log forwarding
- `managed-service-grafana` - Amazon Managed Grafana
- `managed-service-prometheus` - Amazon Managed Prometheus

**Application Integration:**
- `apigateway-v2` - API Gateway HTTP and WebSocket APIs
- `appsync` - GraphQL API service
- `eventbridge` - Event-driven architecture
- `msk-kafka-cluster` - Managed Streaming for Kafka
- `sns` - Simple Notification Service
- `sqs` - Simple Queue Service
- `step-functions` - Serverless workflow orchestration

**Content Delivery & Network Security:**
- `cloudfront` - CloudFront CDN
- `global-accelerator` - Global Accelerator for performance
- `network-firewall` - AWS Network Firewall
- `route53` - DNS and domain management

**Developer Tools & Automation:**
- `appconfig` - Application configuration management
- `atlantis` - Terraform pull request automation
- `notify-slack` - Slack notification integration
- `ssm-parameter` - Systems Manager Parameter Store

**Big Data & Analytics:**
- `emr` - Elastic MapReduce (Hadoop, Spark) for big data processing

All modules include detailed documentation with:
- Module metadata and version information
- Comprehensive feature descriptions
- Real-world use cases
- Security and operational best practices
- Integration examples and code snippets
- Links to official AWS documentation

### Components

1. **Search Library** (`src/tfmod_search_lib.py`)
   - Core search engine with hybrid scoring (keyword + BM25 + semantic)
   - Index building and management
   - Markdown parsing with YAML front-matter support

2. **CLI Tool** (`src/tfmod_search_cli.py`)
   - Command-line interface for index building and testing
   - Two subcommands: `index` and `search`

3. **MCP Server** (`src/tfmod_mcp_server.py`)
   - FastMCP-based stdio server
   - Exposes search and retrieval tools
   - Configuration management and logging

### Data Flow

```
Documentation (.md files)
    ↓
CLI builds index (parse + embed + BM25)
    ↓
Pickled index file (.pkl)
    ↓
MCP server loads index
    ↓
Tools: search_modules, get_module, modules_list
    ↓
Claude Desktop / MCP Clients
```

### Search Scoring Algorithm

The hybrid search combines four signals with configurable weights:

1. **Keyword Overlap** (`w_kw`): IDF-weighted keyword matching
2. **Exact Match** (`w_exact`): Boost for exact module name matches
3. **BM25** (`w_bm25`): Statistical text relevance (Okapi BM25)
4. **Semantic Similarity** (`w_sem`): Cosine similarity of neural embeddings

All scores are min-max normalized before weighted combination.

### Embedding Model Comparison

The project supports any sentence-transformers model via `--model`. The table below benchmarks 5 candidates against the **full catalog**: all 54 modules, each queried 3 ways (exact name, keyword, natural language) — 162 queries per model — using the production search weights from `config.yaml`.

| Model | Dim | Size | Build | Avg Query | Success Rate (top-3) |
|---|---:|---:|---:|---:|---:|
| **`intfloat/e5-small-v2`** ⭐ *(default, since 0.6.0)* | 384 | ~138 MB | ~4.1s | ~8 ms | **100.0%** |
| `BAAI/bge-base-en-v1.5` *(default through 0.5.0)* | 768 | ~419 MB | ~7.5s | ~23 ms | 100.0% |
| `thenlper/gte-small` | 384 | ~65 MB | ~3.9s | ~8 ms | 98.8% |
| `BAAI/bge-small-en-v1.5` | 384 | ~129 MB | ~4.1s | ~8 ms | 98.8% |
| `sentence-transformers/all-MiniLM-L12-v2` | 384 | ~129 MB | ~3.0s | ~8 ms | 98.1% |

**Why `e5-small-v2`**: it's the only smaller model that matches `bge-base-en-v1.5`'s 100% success rate on this corpus — at **~3x smaller** and **~3x faster per query**, with no weight retuning or query/passage prompt prefixes required (both were tried; neither moved the needle on this corpus). `gte-small` is the smallest option (~65 MB, ~6x smaller than the old default) and is a reasonable choice if binary size matters more than the last percentage point of recall — see `tests/integration/test_model_comparison.py` for a repo-committed, CI-run comparison across all three (`gte-small`, `bge-base-en-v1.5`, `e5-small-v2`). `bge-small-en-v1.5` and `all-MiniLM-L12-v2` were also evaluated and are documented here for completeness, but weren't selected: no clear edge over `gte-small`/`e5-small-v2` on either size or accuracy.

To use a different model, rebuild the index with `--model <name>` (see [Building the Index](#1-building-the-index)) and point `--index_path` / `config.yaml` at the new file.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and code quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines (enforced by `ruff`)
- Add type hints to all functions (checked by `mypy`)
- Write tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) - FastAPI-style MCP server framework
- Uses [sentence-transformers](https://www.sbert.net/) for semantic embeddings
- Terraform module documentation from [terraform-aws-modules](https://github.com/terraform-aws-modules)

## 📞 Support

For questions, issues, or feature requests:
- Open an issue on [GitHub Issues](https://github.com/SantyagoSeaman/tfmodsearch/issues)
- Check existing issues for common problems and solutions

---
