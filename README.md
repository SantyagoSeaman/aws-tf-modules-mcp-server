# TFModSearch MCP Server

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **Model Context Protocol (MCP)** server that provides intelligent search capabilities for Terraform AWS module documentation using hybrid search (keyword matching, BM25, and semantic embeddings).

**Ready to Use**: Includes a pre-built search index with embeddings for 54 curated Terraform AWS modules. Install and run the MCP server immediately—no index building required!

## 🚀 Features

- **Hybrid Search Engine**: Combines keyword matching (IDF-weighted), BM25 text relevance, exact module name matching, and semantic similarity for accurate results
- **MCP Integration**: Seamlessly integrates with Claude Desktop and other MCP clients
- **Fast & Efficient**: Pre-built search index with CPU-only inference using `thenlper/gte-small` model
- **Ready to Use**: Includes pre-built index (`model/tfmod_gte_small_index.pkl`) with embeddings from `thenlper/gte-small` model and curated Terraform AWS module documentation
- **Comprehensive Catalog**: Access to terraform-aws-modules documentation compiled from official sources with rich metadata
- **Security-First**: Built-in path validation and access controls for safe file operations
- **Configurable Weights**: Fine-tune search scoring through YAML config or CLI arguments

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
  - [Building the Index](#1-building-the-index)
  - [CLI Search](#2-cli-search-standalone)
  - [MCP Server](#3-mcp-server)
- [MCP Tools](#-mcp-tools)
- [Configuration](#️-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [Architecture](#-architecture)
  - [Indexed Modules](#indexed-modules)
- [Contributing](#-contributing)
- [License](#-license)

## 📦 Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/SantyagoSeaman/aws-tf-modules-mcp-server.git
cd aws-tf-modules-mcp-server

# Create virtual environment and install dependencies
uv venv --python 3.13
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r pyproject.toml
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/SantyagoSeaman/aws-tf-modules-mcp-server.git
cd aws-tf-modules-mcp-server

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r pyproject.toml
```

**Ready to Go**: The repository includes a pre-built search index, so you can skip the index building step and run the MCP server immediately after installation!

## 🏃 Quick Start

### 1. Build the Search Index (Optional)

**Note**: This repository includes a pre-built search index at `model/tfmod_gte_small_index.pkl` with embeddings for 54 curated Terraform AWS modules. You can skip this step and proceed directly to testing or running the server if you want to use the included modules.

To rebuild the index or create a new one with additional modules:

```bash
python src/tfmod_search_cli.py index \
  --docs_dir ./modules/terraform-aws-modules \
  --model thenlper/gte-small
```

**Note**: The first run will download the `thenlper/gte-small` model (~134MB).

### 2. Test the Search (CLI)

Test the search functionality using the command-line interface:

```bash
python src/tfmod_search_cli.py search \
  --query "s3 bucket with kms encryption and versioning" \
  --top_k 5
```

### 3. Run the MCP Server

Start the MCP server for integration with Claude Desktop or other MCP clients:

```bash
python src/tfmod_mcp_server.py --index_path ./model/tfmod_gte_small_index.pkl
```

## 📖 Usage

### 1. Building the Index

**Note**: The repository includes a pre-built index—you only need to build a new index if you want to add more modules or customize the existing ones.

Build or rebuild the search index from your module documentation:

```bash
python src/tfmod_search_cli.py index \
  --docs_dir ./modules/terraform-aws-modules \
  --index_path ./model/tfmod_gte_small_index.pkl \
  --model thenlper/gte-small
```

**Options**:
- `--docs_dir`: Directory containing Terraform module markdown files (required)
- `--index_path`: Output path for the pickled index file (required)
- `--model`: Sentence transformer model to use (default: `thenlper/gte-small`)

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
```

### 3. MCP Server

#### Running the Server

**Note**: The repository includes a pre-built index, so you can run the server immediately without rebuilding.

```bash
# Using default index path (./model/tfmod_gte_small_index.pkl) - uses pre-built index
python src/tfmod_mcp_server.py

# With custom index path
python src/tfmod_mcp_server.py --index_path /path/to/tfmod_gte_small_index.pkl

# With custom configuration file
python src/tfmod_mcp_server.py --config /path/to/config.yaml

# With CLI weight overrides (overrides config.yaml)
python src/tfmod_mcp_server.py \
  --index_path ./model/tfmod_gte_small_index.pkl \
  --w_kw 2.5 \
  --w_exact 4.0 \
  --w_bm25 1.5 \
  --w_sem 1.0
```

#### Claude Desktop Integration

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "terraform-modules": {
      "command": "/absolute/path/to/aws-tf-modules-mcp-server/.venv/bin/python",
      "args": [
        "/absolute/path/to/aws-tf-modules-mcp-server/src/tfmod_mcp_server.py"
      ]
    }
  }
}
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

## ⚙️ Configuration

### Search Weights Configuration

Create a `config.yaml` file in the project root to customize search scoring weights:

```yaml
search_weights:
  w_kw: 2.0      # Keyword overlap weight (IDF-weighted)
  w_exact: 3.0   # Exact module name match boost
  w_bm25: 1.0    # BM25 text relevance weight
  w_sem: 1.0     # Semantic similarity weight
```

**Configuration Precedence** (highest to lowest):
1. CLI arguments (`--w_kw`, `--w_exact`, etc.)
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
git clone https://github.com/SantyagoSeaman/aws-tf-modules-mcp-server.git
cd aws-tf-modules-mcp-server

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
pytest tests/integration/test_mcp_server.py -v        # MCP server tests (17 tests)
pytest tests/integration/test_parse_markdown.py -v    # Parsing tests (12 tests)
pytest tests/integration/test_cli_index.py -v         # CLI index tests (4 tests)

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

### Test Coverage

- **MCP Server** (17 tests): `search_modules` tool, `get_module` resource, security validation, integration workflows
- **Markdown Parsing** (12 tests): YAML front-matter parsing, description extraction, normalization
- **CLI Index Building** (4 tests): Index creation, validation, search integration

**Total**: 33 integration tests

## 🏗️ Architecture

### Included Content

This repository includes:

- **Pre-built Search Index** (`model/tfmod_gte_small_index.pkl`):
  - Ready-to-use search index with pre-computed embeddings using `thenlper/gte-small` model
  - Contains BM25 corpus, semantic vectors, and keyword IDF scores
  - Includes 54 curated Terraform AWS modules
  - File size: ~4.36 MB

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

**Networking & Content Delivery:**
- `cloudfront` - CloudFront CDN
- `global-accelerator` - Global Accelerator for performance
- `network-firewall` - AWS Network Firewall
- `route53` - DNS and domain management

**Developer Tools & Automation:**
- `appconfig` - Application configuration management
- `atlantis` - Terraform pull request automation
- `notify-slack` - Slack notification integration
- `ssm-parameter` - Systems Manager Parameter Store

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
- Open an issue on [GitHub Issues](https://github.com/SantyagoSeaman/aws-tf-modules-mcp-server/issues)
- Check existing issues for common problems and solutions

---
