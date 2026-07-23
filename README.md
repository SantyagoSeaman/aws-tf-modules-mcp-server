# TFModSearch MCP Server

[![CI](https://github.com/SantyagoSeaman/tfmodsearch/actions/workflows/ci.yml/badge.svg)](https://github.com/SantyagoSeaman/tfmodsearch/actions/workflows/ci.yml)
[![CodeQL](https://github.com/SantyagoSeaman/tfmodsearch/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/SantyagoSeaman/tfmodsearch/security/code-scanning)
[![mypy](https://img.shields.io/badge/mypy-checked-2a6db2.svg)](https://mypy-lang.org/)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/SantyagoSeaman/tfmodsearch/badge)](https://securityscorecards.dev/viewer/?uri=github.com/SantyagoSeaman/tfmodsearch)
[![PyPI](https://img.shields.io/pypi/v/tfmodsearch)](https://pypi.org/project/tfmodsearch/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> ## 📦 Archived
>
> **This project is archived.** It set out to be a better Terraform-module lookup surface for AI coding
> agents than the alternatives — faster discovery, and a compact response format carrying just enough
> detail to keep an agent cheap and accurate. So we did the honest thing and **built a real testing
> environment to check whether it actually worked**: machine-graded A/B eval harnesses that pit this
> server head-to-head against HashiCorp's official Terraform MCP server, with `terraform validate` and
> a module-agnostic capability rubric as the oracle.
>
> **The verdict: parity.** Across three independent task families (capability reconstruction,
> refactor-in-place, and greenfield-from-requirements), a capable agent using this server and one using
> the official HashiCorp MCP reach the same outcomes — both produce valid, correctly-scoped Terraform.
> And the headline bet — a compact, curated response format to cut token cost — **de-facto failed**:
> the token optimizations were real engineering against the tool's own older self, but they
> produced no cost or quality edge over the baseline MCP, and on the greenfield task the richer
> responses made this server *measurably more expensive*.
>
> That is a genuinely great outcome — for the experiment, not the product. **The real value here was
> building a valid way to test the hypothesis instead of trusting that "compact + smarter search must
> help."** It did not, and only a machine-graded A/B harness could show that. Blind faith would have
> shipped a story; the harness shipped the truth.
>
> So that's it. The server works and is honest about what it does — but it does not beat the free,
> official tool it was meant to beat, so it goes into the archive. Thanks for reading. 🙏
>
> The full experiment history is below.

A **Model Context Protocol (MCP)** server that provides intelligent search capabilities for Terraform AWS module documentation using hybrid search (keyword matching, BM25, and semantic embeddings).

## 🧪 The experiment: what we tried, and what testing showed

The project ran as a long series of attempts to make an AI agent write *better* Terraform by
improving the doc-lookup tool it uses. The improvements were real and shipped; the surprise was that
none of them beat the baseline once we measured properly.

**What we tried, to change quality and cost:**

- **Retrieval quality** — swapped the embedding model twice (`gte-small` → `bge-base-en-v1.5` →
  `intfloat/e5-small-v2`), tuned the 4-signal hybrid score (keyword-IDF / exact-name / BM25 /
  semantic), and closed keyword gaps so every module is findable by intent, exact name, and natural
  language. A frozen golden set guarded against regressions.
- **Response shaping (the token bet)** — added a compact **orientation head** for `get_module` (core
  sections + key features + a version-pin hint + an honest "here is what is omitted, escalate with one
  call" footer) instead of dumping 10k+ token documents; a `sections` filter; submodule reachability
  so a search lands directly on the right submodule; and a search-confidence verdict. The thesis:
  *find fast, return just enough, spend fewer expensive model cycles.*
- **Interface completeness** — served every module's COMPLETE Registry-declared inputs/outputs (not a
  hand-picked subset that often hid most of the real interface), added apply-verified example HCL for
  `type = any` inputs, **collapsed oversized `object({...})` type expressions** to their first-level
  keys to keep the payload small, and shipped curated **gotchas** (e.g. the two EKS cluster
  security-group outputs that are named alike but are not interchangeable).
- **Infrastructure / footprint** — an opt-in shared **HTTP daemon** so N agents share one warm model
  instead of each paying a ~600 MB load; a torch-free **proxy mode**; an **ONNX** encode backend that
  cut the Docker image from ~1.7 GB to ~560 MB and daemon RSS from ~1 GB to ~300 MB. A live-registry
  `grep` tool was added and later removed as a measured cost sink.

**How we tested it (the part that mattered):**

Rather than trusting that these helped, we built machine-graded A/B evaluation harnesses. A worker
agent (fixed model, both arms) is given a real task and ONE documentation tool — either this server or
HashiCorp's official Terraform MCP — and must produce Terraform that passes `terraform validate`. We
scored the result, not the process: does it validate, does it deliver the required capabilities
(checked module-agnostically, so any vendor's module or raw resources count), and does it cost. Three
task families, matched fleets, several workers per cell:

- **Reconstruction** — given a capability, pick and configure the right registry module.
- **Refactor-in-place** — convert a real raw-`aws_*` production directory into modules and rewire it.
- **Greenfield-from-requirements** — author a whole stack from capability requirements with no module
  names given, including a few requirements whose module is deliberately *not* obvious from the text.

**What the testing showed:**

- **Parity on outcomes, every time.** With a validation loop (or result-only grading), both tools reach
  valid, correctly-covered Terraform. The gap the tool appeared to have in naive one-shot tests
  evaporated the moment the agent could self-correct — which is how agents actually work.
- **The token bet did not pay off.** The compact head and type-collapse are real, but the dominant cost
  is the agent re-reading its own working context, not the tool's response — so the savings were noise
  where a large substrate dominated, and on greenfield (no substrate to hide behind) this server's
  heavier responses made it the *more* expensive of the two.
- **Smarter search bought nothing on outcomes.** Even on requirements whose module was non-obvious, a
  competent agent infers the AWS service from the description and reaches the same module the semantic
  search found — so the discovery advantage never became an outcome advantage.
- **The tool's remaining edges are friction-level, not outcome-level** (it introspects submodule
  interfaces and serves very large modules where the baseline errors out) — real, but a capable agent
  routes around the baseline's gaps, and those gaps are the kind a competitor closes in a release.
- **Running it found real bugs.** The first greenfield run surfaced two grading bugs (a block parser
  that mis-split HCL with braces inside strings; a duplicate-provider composition error) that clean
  fixtures never triggered — the clearest possible proof that you cannot know a thing works until you
  test it on real output.

**The lesson.** The valuable artifact was not the server — it was the discipline of building a valid,
machine-graded environment to test the hypothesis instead of believing it. The hypothesis ("compact,
curated, smarter search makes agents cheaper and better") was intuitive, plausible, and wrong, and
only the harness could tell us so. That is the whole point of testing.

**Ready to Use**: Includes a pre-built search index with embeddings for 63 curated Terraform AWS modules. Install and run the MCP server immediately—no index building required!

## 🤔 Why TFModSearch?

When an AI assistant writes Terraform, it often guesses at module names, invents variables that don't exist, or reaches for outdated syntax. TFModSearch gives your assistant a **curated, versioned, offline knowledge base** of the official [`terraform-aws-modules`](https://github.com/terraform-aws-modules) — plus a set of vendor-maintained [Cloud Posse](https://github.com/cloudposse) modules that fill gaps the official set does not cover — so it can:

- **Find the right module from intent** — "I need a Redis cache" resolves to `elasticache`, not a hallucinated module name.
- **Ground generated code in real inputs/outputs** — the assistant pulls the full, current module documentation (submodules, variables, outputs, examples) on demand instead of improvising.
- **Stay fast, private, and deterministic** — the whole server runs locally on CPU against a pre-built index, fully offline. No external API calls, no rate limits, no network round-trips.
- **Get the complete interface, not a curated excerpt** — `get_module`'s inputs/outputs views return the module's COMPLETE Registry-declared interface in one call, so you never have to guess whether an omitted variable is real.

Think of it as an always-available, searchable reference card for every terraform-aws-modules module — kept accurate and shipped ready to run.

## 🚀 Features

- **Hybrid Search Engine**: Combines keyword matching (IDF-weighted), BM25 text relevance, exact module name matching, and semantic similarity for accurate results
- **Complete Inputs/Outputs for Every Module**: `get_module`'s inputs/outputs views serve the module's COMPLETE Registry-sourced interface for all 63 catalog modules — not a curated subset — from a committed per-module artifact (`model/any_overlay/`); the 22 modules with `type = any` inputs additionally get the module maintainers' own apply-verified example HCL and observed field names per `any`-typed variable — all offline and honestly labeled as an example rather than a schema
- **Fully Offline**: no networked tools — every response is served from the local pre-built index and committed per-module artifacts; the only network use anywhere in the server is an opt-in daily PyPI update check in HTTP mode
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
  - [Docker (opt-in)](#-docker-opt-in)
  - [Shared HTTP instance (opt-in)](#-shared-http-instance-opt-in)
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
- [Security](#-security)
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
- The **tfmod-search MCP server** (runs via `uvx tfmodsearch` by default — [uv](https://github.com/astral-sh/uv) required; the Claude Code plugin can optionally run it via Docker instead, see [Docker](#-docker-opt-in) below)
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

> **Bundled and ready**: The pre-built search index and all 63 module docs ship *inside* the package, so `uvx` fetches, installs, and runs the server with nothing to clone or rebuild. (The `intfloat/e5-small-v2` embedding model — ~130 MB — is downloaded automatically on the first search to encode your query, then cached for subsequent queries.)

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

### 🐳 Docker (opt-in)

`uvx tfmodsearch` stays the documented default. An official Docker image is also published to
GHCR for environments that prefer or require a container — air-gapped/offline setups, CI runners
without a Python/uv toolchain, or teams that standardize MCP server deployment on Docker. The
image bakes in the embedding model, the search index, and the NLTK tokenizer data at build time,
so **all three tools — `search_modules`, `get_module`, and `modules_list` — make zero network
calls at runtime**; a `--network none` run works for every tool call, not just the warmup.

> **Since 0.19.0, the image runs the ONNX encode backend instead of torch**: `model.onnx` +
> `tokenizer.json` are baked in at build time (see "Embedding backends" below) instead of the
> torch/sentence-transformers stack and its HF model cache. Measured: **1.42 GB → 559 MB
> uncompressed** (pull size verified post-release), same search results — validated at cosine
> ≥ 0.99999988 (max elementwise diff 4.06e-07) against sentence-transformers across all 162
> golden queries, plus ~5x faster query encoding on CPU. `uvx tfmodsearch` / PyPI installs are
> unaffected — they keep torch by default.

**Any MCP client**, launch the image directly (never add `-t`/`--tty` — it corrupts the stdio
JSON-RPC stream):
```json
{
  "mcpServers": {
    "terraform-modules": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "ghcr.io/santyagoseaman/tfmodsearch:0.26.0"]
    }
  }
}
```

**Claude Code plugin**, the bundled launcher defaults to `uvx` and switches to Docker when
`TFMODSEARCH_DOCKER=1` is set (in `~/.claude/settings.json`'s `env` block, or exported before
launching Claude Code):
```bash
export TFMODSEARCH_DOCKER=1
# optional: pin a different tag
export TFMODSEARCH_IMAGE=ghcr.io/santyagoseaman/tfmodsearch:0.26.0
```
If Docker is requested but not on `PATH`, the launcher falls back to `uvx` with a warning instead
of failing. This dual-mode launcher currently applies to the **Claude Code plugin only** — the
Codex plugin stays `uvx`-only (Codex CLI doesn't yet reliably resolve a plugin-relative path in
its `mcp.json`).

> **Note**: the Claude Code plugin now launches via a bundled `python3` launcher script instead of
> calling `uvx` directly, so a `python3` interpreter on `PATH` is a prerequisite for the plugin
> (in addition to `uv`/`uvx`) — on macOS/Linux this is normally already present; on Windows, make
> sure `python3` (not just `python`/the `py` launcher) resolves on `PATH`.

Verify the offline property yourself:
```bash
docker run --network none -i --rm ghcr.io/santyagoseaman/tfmodsearch:0.26.0 --warmup
```

### 🌐 Shared HTTP instance (opt-in)

stdio is one server process per client session: every MCP client (and every subagent it spawns)
starts its own process, and each process loads the ~600 MB embedding model on its own. Fan a task
out across N subagents and you pay for N model loads — the cost multiplies with fan-out.
Streamable HTTP transport (since 0.16.0) inverts that: **one long-lived shared instance**, many
clients connect to it by URL. The model and index load once; the main session and every subagent
share that single instance.

This is an **operator-managed opt-in mode** — stdio via `uvx tfmodsearch` remains the default for
both the plugin and every install path above. Reach for HTTP only when you want one daemon shared
across sessions/subagents on a machine.

**Quickstart (Docker)**:
```bash
docker run -d --name tfmodsearch-http --restart unless-stopped \
  -p 127.0.0.1:8765:8765 \
  ghcr.io/santyagoseaman/tfmodsearch:0.26.0 \
  --transport http --host 0.0.0.0 --port 8765
```

Or with the bundled `docker-compose.yml` (same recipe, one command):
```bash
docker compose up -d
```

**Quickstart (no Docker)**:
```bash
tfmodsearch --transport http
```

Then point Claude Code at the running daemon (URL, not a command):
```bash
claude mcp add --transport http --scope user tfmod-search http://127.0.0.1:8765/mcp
```

**Keeping the plugin (proxy mode, recommended since 0.18.0)**: plugin users do not have to
choose between the skills and the shared daemon anymore. Set one env var and the plugin's
bundled server becomes a lightweight stdio proxy to the daemon — skills, subagents, and the
auto-search workflow all keep working, and the 600 MB model loads only once, in the daemon:

```jsonc
// ~/.claude/settings.json
{ "env": { "TFMODSEARCH_URL": "1" } }               // default daemon on 127.0.0.1:8765
// or a custom target:
{ "env": { "TFMODSEARCH_URL": "http://127.0.0.1:9000/mcp" } }
```

The launcher health-checks the daemon first (3 s): if it is not responding — including while
the daemon is still warming up after a restart — the session falls back to the normal local
server with a stderr warning, so a stopped daemon never breaks the session (that fallback pays
the full local model load; retry once the daemon reports healthy). A bare origin like
`http://127.0.0.1:8765` works too — the `/mcp` path is added automatically. The proxy runs via
`uvx --from "tfmodsearch>=0.18.0"`, so uv must be able to resolve that release (first use needs
network or a warm uv cache). Point `TFMODSEARCH_URL` only at a daemon you trust: the proxy
forwards every tool call there verbatim. `TFMODSEARCH_URL` takes precedence over
`TFMODSEARCH_DOCKER`. Rollback: unset the var. Any MCP client can use the same mode without
the plugin: `tfmodsearch --proxy-url <url>`.

**Migrating from the plugin (plugin-less setups)**: if you do not want the plugin at all, make
sure only one `tfmod-search` server is registered. Disable the plugin, then add the HTTP entry:
```bash
claude plugin disable tfmod-search
claude mcp add --transport http --scope user tfmod-search http://127.0.0.1:8765/mcp
```
The HTTP daemon exposes the exact same three tools, so agent workflows keep working. To go back:
`claude mcp remove tfmod-search` and re-enable the plugin.

**Codex CLI**: the plugin stays stdio-only, but recent Codex CLI versions can connect to a
streamable HTTP MCP server directly in `~/.codex/config.toml`:
```toml
[mcp_servers.tfmod-search]
url = "http://127.0.0.1:8765/mcp"
```
(Check your Codex version supports HTTP MCP servers; remove the plugin's stdio entry first, same
one-server rule as above.)

**Readiness**: poll the health endpoint (no MCP handshake needed). The server loads the index
and warms the embedding model *before* it starts listening, so expect connection-refused during
startup, then 200 once the port is up:
```bash
curl -s http://127.0.0.1:8765/health
# {"status": "ok", "version": "0.26.0", "modules": 63,
#  "latest_version": null, "update_available": false}
```

**Configuration** (CLI flags take precedence over env vars, which take precedence over the
defaults below):

| Setting | Flag | Env var | Default |
|---|---|---|---|
| Transport | `--transport {stdio,http}` | `TFMODSEARCH_TRANSPORT` | `stdio` |
| Host | `--host` | `TFMODSEARCH_HOST` | `127.0.0.1` |
| Port | `--port` | `TFMODSEARCH_PORT` | `8765` |

**Lifecycle ownership**: the operator owns the daemon — start it, keep it running (`--restart
unless-stopped` / the compose healthcheck), and stop it. MCP clients never auto-start or manage
it; if the daemon is down, Claude Code shows the `tfmod-search` server as failed/disconnected and
its tools disappear until the daemon is back. That's the trade-off for sharing one instance
across sessions.

**Managing the daemon**:
```bash
docker compose down                # stop (or: docker rm -f tfmodsearch-http)
docker logs -f tfmodsearch-http    # server + uvicorn logs (READY line, warnings, tracebacks)
# upgrade when a new release ships: bump the pinned tag in docker-compose.yml, then
docker compose pull && docker compose up -d
```
The compose file mounts a named volume (`tfmodsearch-cache`) over `/home/app/.cache`; this
historically persisted the now-removed `grep_module_docs` registry-doc cache and is currently
unused, kept for forward compatibility with any future on-disk cache. Running the non-Docker
variant as a daemon is on you (a terminal multiplexer, `nohup`, or a launchd/systemd unit) — the
server itself is just a foreground process.

**Update notifications** (since 0.17.0): a pinned image tag means the daemon otherwise runs
forever with no signal that a newer release exists. In HTTP mode the server checks PyPI once a
day and surfaces what it finds through three channels — `curl /health` gains `latest_version`/
`update_available` fields, a WARNING lands in `docker logs` once per cycle while stale, and an
`update_notice` field appears on `search_modules`/`modules_list` responses (absent entirely when
there is nothing to report) so your agent can relay it directly. Nothing
auto-updates — the operator still owns bumping the tag and running
`docker compose pull && docker compose up -d`. Set `TFMODSEARCH_UPDATE_CHECK=0` to disable the check entirely
(air-gapped deployments).
Privacy: the check is one anonymous GET to the public PyPI JSON API — nothing about you or your
host is sent.

> **Do not run both the plugin's stdio entry and the HTTP entry at the same time.** Two
> `tfmod-search` MCP servers registered simultaneously present duplicate toolsets and confuse
> agents about which one to call. Remove or disable the plugin's stdio entry before adding the
> HTTP entry (or vice versa).

**Security**: the HTTP transport has **no authentication and no TLS**. Keep the port
loopback-only (`127.0.0.1:8765:8765`, not `0.0.0.0:8765:8765`) and never expose it directly to a
network without a reverse proxy in front that adds auth. Binding `0.0.0.0` *inside* the container
is expected and fine — the container's own loopback would make the published port unreachable —
the actual security boundary is the host port mapping (`-p 127.0.0.1:8765:8765`), which restricts
reachability to the host's loopback interface.

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Local Installation (For Development)

```bash
# Clone the repository
git clone https://github.com/SantyagoSeaman/tfmodsearch.git
cd tfmodsearch

# Create virtual environment and install dependencies
uv venv --python 3.12
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

**Note**: This repository includes a pre-built search index at `model/tfmod_e5_small_index.pkl` with embeddings for 63 curated Terraform AWS modules. You can skip this step and proceed directly to testing or running the server if you want to use the included modules.

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

The MCP server exposes three tools for Terraform module discovery and documentation retrieval —
fully offline, no networked tools:

### `modules_list()`

List all available Terraform modules in the catalog.

**Parameters**: None

**Returns**: Complete list of modules with names, paths, descriptions, keywords, and registry coordinates (`module_id`, `latest_version`).

**Example**:
```json
{
  "modules": [
    {
      "module_name": "vpc",
      "path": "modules/terraform-aws-modules/vpc.md",
      "description": "Terraform module to create AWS VPC resources...",
      "keywords": ["vpc", "subnet", "networking", "aws"],
      "module_id": "terraform-aws-modules/vpc/aws",
      "latest_version": "6.6.1"
    }
  ],
  "count": 63
}
```

### `search_modules(query: str, top_k: int = 3)`

Search for Terraform modules using keywords, exact names, or natural language queries.

**Parameters**:
- `query` (string): Free-text search query
- `top_k` (int, optional): Number of results to return, 1–10 (default 3). Raise it for ambiguous queries like `"iam"`.

**Returns**: Top-ranked modules with metadata and relevance scores. Each hit also carries `module_id` (the registry coordinate, e.g. `terraform-aws-modules/vpc/aws`) and `latest_version` for reference.

**Example queries**:
- `"vpc"` - Find VPC module by exact name
- `"object storage with encryption"` - Natural language search
- `"kubernetes cluster management"` - Find EKS module
- `"serverless functions"` - Find Lambda module

### `get_module(module_identifier: str, sections: list[str] | None = None)`

Get documentation for a specific Terraform module. **By default returns a compact orientation head** — not the full document — so a first orientation call stays small (large modules run to 10k+ tokens in full).

**Parameters**:
- `module_identifier` (string): Module name (e.g., `"vpc"`), relative path (e.g., `"modules/terraform-aws-modules/vpc.md"`), or **submodule address** (e.g., `"iam//modules/iam-role"`, or the full `"terraform-aws-modules/iam/aws//modules/iam-role"`) — returns an orientation head **scoped to that submodule's section** in one call, instead of the whole parent doc.
- `sections` (list of strings, optional): Control what comes back.
  - **Omitted** → the **orientation head**: description, module info, an exact **version-pin hint**, notes for AI agents, any Important Gotchas the doc carries, key features, use cases, plus a footer with the **full section inventory** — an explicit menu of the logical keys and every heading in the doc — so the next call knows exactly what it can request. The footer also flags that the curated prose (description, examples, best practices) is a hand-picked subset and points to module source for resource-creation conditions and for a `map(object)`/`any` field's nested type/shape; the inputs/outputs table itself is already the module's complete Registry-declared interface (see below), so `get_module(sections=["inputs", "outputs"])` is the exhaustive-confirmation / name-exists check, in one offline call. For a module **with submodules**, the head also inlines the compact submodule **inventory** — each submodule's name, purpose, and pinnable source string — so when the right answer is a submodule you can pin its source or drill in via the submodule address above.
  - **Logical keys or heading substrings** → those sections added on top of the always-included core. Accepts `inputs`, `outputs`, `examples`, `submodules`, `features`, `use-cases`, `best-practices`, `resources`, or case-insensitive substrings of headings (e.g. `"karpenter"` for a single EKS submodule). The `inputs`/`outputs`/`examples` keys also resolve on modules that bundle their interface into a combined `Main Module:`/`Root Module:` section or spread it across submodules.
  - **`["all"]`** (or `"full"`/`"everything"`) → the complete document verbatim.

**Returns**: The compact orientation head by default, a filtered subset when specific sections are requested, or the complete markdown document when an `all`/`full` key is given.

**Complete inputs/outputs interface**: `get_module`'s inputs and outputs views (`sections=["inputs"]`/`["outputs"]`, an `all`/`full` request, or a submodule-scoped request) serve the module's COMPLETE Registry-declared interface — every input (name, type, required, default, description) and every output (name, description) — for all 63 catalog modules, superseding the curated Markdown table wherever that table was only a hand-picked subset. For example, `rds` curates 41 of its 111 root-level inputs (238 across all submodules) in the doc body; the complete table now surfaces all of them in one call. `sections=["inputs"]`/`["outputs"]`/`["inputs", "outputs"]` render the **root scope only** by default; a submodule's complete interface is one more call away via the submodule address (`get_module("eks//modules/karpenter", sections=["inputs"])`), and the root response's footer lists the available submodule scopes by name. This is sourced from a committed per-module artifact, `model/any_overlay/<id>.json` (built by `scripts/build_any_overlay.py` from the Terraform Registry API detail at the doc's own pinned version) — a plain file read at serve time, so `get_module` stays fully offline.

**Any-typed input overlay**: on top of the complete table, some Registry inputs are declared `type = any`, where the type string alone does not describe the shape. The 22 catalog modules with at least one such input additionally get, per `any`-typed variable, the module maintainers' own apply-verified example HCL for that variable (pulled from the module's own `examples/`) plus a list of field names observed in the module source. Every appendix is honestly labeled: an apply-verified example from a named module version, explicitly **not a schema** — for the field's exact nested type/shape beyond the example, consult the module source directly — with a version-skew note when the overlay's source version differs from the doc's pinned version. The default orientation head only gets a lightweight pointer (`any — see sections=["inputs"]`) rather than the full appendix, to keep the head small. The other 41 modules — no `any`-typed input — still get the complete table above; they carry no example/field-name appendix since none of their inputs need one.

**Security**: Only files under the `modules/` directory are accessible. Absolute paths and path traversal attempts are rejected.

### Typical Workflow

A coding assistant discovers and uses a module in two steps:

1. **Search by intent** — the assistant turns a natural-language need into a module:

   ```
   search_modules("managed kubernetes cluster with node groups")
   → eks (score 8.9), eks-pod-identity (2.1), autoscaling (1.7)
   ```

2. **Orient, then drill in** — it pulls a compact orientation head, then requests the parts it needs:

   ```
   get_module("iam")
   → IAM orientation head: what it is, exact version pin + the submodule inventory
     inline (iam-role, iam-policy, iam-oidc-provider, … each with a pinnable source)
   get_module("iam//modules/iam-role")
   → head scoped to the iam-role submodule (its trust policy, OIDC, inputs) in one call
   ```

The assistant then writes Terraform using real variable names and current syntax — instead of guessing. `search_modules` returns the top 3 candidates by default (raise `top_k` for broader queries) so the assistant can disambiguate between closely related modules (e.g. `alb` vs `elb`, `rds` vs `rds-aurora`) before committing. `get_module` returns a small orientation head by default so the first call never overflows; scoped `sections=["inputs", "examples"]` pull only what's needed, and `sections=["all"]` returns the complete document when the whole thing is genuinely wanted.

For a **pinpoint lookup** — the exact name/default of one variable, or how a specific feature is wired — `get_module(name, sections=["inputs", "outputs"])` renders the module's complete root-scope interface in one offline call:

```
get_module("eks", sections=["inputs", "outputs"])
→ the exact input row + its default + every other declared input/output — no full-document dump
```

**Tool boundaries**: `search_modules` finds the right AWS module; `get_module` returns its curated, compact, offline doc, or the module's complete interface on request. A module **outside the curated AWS catalog** or at a **specific older version** falls outside these three tools' scope — use your other Terraform Registry tooling for those.

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

### Embedding backends

Query and index encoding go through a small backend seam, selected via `TFMODSEARCH_EMBED_BACKEND`:

| Value | Behavior |
|---|---|
| `auto` (default) | Use the torch/sentence-transformers backend if `sentence-transformers` is importable; otherwise fall back to the ONNX backend if ONNX assets are found; otherwise a clear error naming both options. |
| `torch` | Force the sentence-transformers path (unchanged since prior releases). |
| `onnx` | Force the ONNX path: a `tokenizers` tokenizer plus an `onnxruntime` CPU session, replicating sentence-transformers mean pooling + L2 normalization for `intfloat/e5-small-v2`. Validated at cosine ≥ 0.99999988 (max elementwise diff 4.06e-07) against sentence-transformers across all 162 golden queries, and ~5x faster to encode a query on CPU. |

`TFMODSEARCH_ONNX_MODEL_DIR` points the ONNX backend at a directory containing `model.onnx` + `tokenizer.json` (defaults to `<project_root>/onnx/e5-small-v2` if unset, which is where the official Docker image bakes them).

**`uvx tfmodsearch` / PyPI installs keep torch** — the core dependency set is unchanged, so nothing to opt into for a normal local install. The ONNX bits are an optional extra: `pip install "tfmodsearch[onnx]"` (adds `onnxruntime>=1.20` and `tokenizers>=0.21`), plus ONNX assets — `python scripts/export_onnx_model.py <output_dir>` exports `intfloat/e5-small-v2` (requires `optimum-onnx`/torch at export time only, and the script lives in the repo, not the wheel — clone the repo to run it) and prints a parity check against sentence-transformers when both are installed. Note the extra **adds** packages, it cannot remove torch from a pip install (Python extras only add): the torch-free ~559 MB footprint is a property of the official Docker image, which is built without sentence-transformers entirely. The extra is mainly useful if you want the ONNX code path outside that image.

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
# Run linter (includes flake8-bandit `S` security rules)
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
pytest tests/integration/test_all_modules_searchable.py -v  # Searchability, all 63 modules (196 tests)
pytest tests/integration/test_model_comparison.py -v -s     # Model comparison (31 tests)
pytest tests/integration/test_mcp_server.py -v              # MCP server tools (40 tests)
pytest tests/integration/test_registry_docs.py -v          # parse_module_id + overlay-build fetch helpers
pytest tests/integration/test_parse_markdown.py -v          # Markdown parsing (14 tests)
pytest tests/integration/test_cli_index.py -v               # CLI index building (4 tests)
pytest tests/integration/test_security_config.py -v         # Security config contract (5 tests)

# Run the opt-in live tests (real calls to the public Terraform Registry)
RUN_REGISTRY_BENCHMARK=1 pytest tests/integration/test_registry_comparison.py -v -s

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

### Test Coverage

- **All Modules Searchable** (196 tests): every one of the 63 modules is verified findable by keyword, exact name, and natural-language query (target in top-3), plus catalog metadata and search-quality checks
- **Model Comparison** (31 tests): embedding model performance comparison with timing analysis
- **MCP Server** (65 tests): `search_modules`, `get_module`, and `modules_list` tools, `top_k` and `sections` parameters (orientation-head default, inline submodule inventory, submodule-address scoped head, `all`/`full` escape hatch, combined/submodule interface-key resolution, version-pin hint), `module_id`/`latest_version` fields, security validation, integration workflows
- **Doc Schema** (441 tests): schema-integrity guards over all 63 curated docs — universal core headings present and unique (incl. the orientation head's own Key Features + Main Use Cases), a recognised interface scheme (split / combined `Main Module:` / submodule-only), `inputs`/`outputs`/`examples` resolving on every doc, a clean orientation head, and every doc's submodule inventory surfaced in the head — so `get_module` section filtering can't silently break
- **End-to-End** (59 tests): real MCP stdio protocol sessions against a spawned server process, wheel payload and entry-point verification, `uvx` packaged-server smoke test, plugin manifest/skill/agent contracts for Claude Code and Codex, skill-script tests (terraform log prefilter), live plugin install via the `claude` CLI
- **Module ID header** (1 test): every curated doc carries a `Module ID` bullet equal to its root registry `Source`
- **Markdown Parsing** (14 tests): `## Module Information` parsing (name, keywords, `module_id`, `latest_version`), description extraction, normalization
- **CLI Index Building** (4 tests): index creation, validation, search integration
- **Security Config** (5 tests): the Dependabot config, `SECURITY.md` reporting policy, both workflows' least-privilege `permissions`, and the publish job's retained OIDC `id-token: write` grant
- **Registry Comparison** (5 tests): top-1/top-3 retrieval benchmark vs. the public Terraform Registry (see [Registry Search Comparison](#registry-search-comparison-vs-terraform-registry--hashicorp-mcp)); one network-free guard runs always, the four live tests are opt-in via `RUN_REGISTRY_BENCHMARK=1`

**Total**: 1130 tests (integration + e2e; 1103 passing, 27 skipped — 6 opt-in live tests unless `RUN_REGISTRY_BENCHMARK=1`, plus docs with no submodule inventory skipped by the schema guard)

## 🔒 Security

TFModSearch is a local, CPU-only server with no networked tools — every response comes from the local pre-built index and committed per-module artifacts. The only network use anywhere in the server is an opt-in daily PyPI update check in HTTP mode (see "Update notifications" above). Supply-chain and code hygiene are enforced with GitHub-native tooling:

- **Vulnerability reporting**: see [`SECURITY.md`](SECURITY.md) — please use GitHub Private Vulnerability Reporting rather than a public issue.
- **CodeQL** default setup runs static analysis on every pull request and on a weekly schedule.
- **Dependabot** opens weekly GitHub Actions version-updates and automatic security-update PRs for vulnerable dependencies.
- **Secret scanning + push protection** are enabled on the repository.
- **ruff `S` (flake8-bandit)** security lint runs in CI, and the registry fetch refuses any non-`https` URL.
- **Least-privilege CI**: workflows run with `permissions: contents: read`; PyPI publishing uses OIDC Trusted Publishing (no long-lived token) with PEP 740 attestations.

## 🏗️ Architecture

### Included Content

This repository includes:

- **Pre-built Search Index** (`model/tfmod_e5_small_index.pkl`):
  - Ready-to-use search index with pre-computed embeddings using `intfloat/e5-small-v2` model
  - Contains BM25 corpus, semantic vectors, and keyword IDF scores
  - Includes 63 curated Terraform AWS modules
  - File size: ~4.87 MB

- **Curated Module Documentation** (`modules/terraform-aws-modules/` + `modules/cloudposse/`):
  - Compiled documentation for 63 Terraform AWS modules covering compute, storage, networking, databases, security, and more
  - 55 sourced from the official [terraform-aws-modules](https://github.com/terraform-aws-modules) project, plus 8 vendor-maintained [Cloud Posse](https://github.com/cloudposse) gap-fillers (aws-config, ses, vpc-peering, security-hub, guardduty, cloudtrail, backup, sso); provenance is preserved in each doc's Module ID / Source
  - Formatted as Markdown with a `## Module Information` metadata block
  - Each module includes comprehensive documentation with best practices, use cases, and examples

### Indexed Modules

The search index includes 63 Terraform AWS modules across multiple service categories. Each module is documented with comprehensive descriptions, best practices, use cases, and integration examples.

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
- `wafv2` - AWS WAF v2 web application firewall

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

**Cloud Posse (vendor-maintained gap-fillers, `modules/cloudposse/`):**
- `config` - AWS Config compliance rules and multi-account aggregation
- `ses` - Simple Email Service domains and SMTP credentials
- `vpc-peering` - Same-account VPC peering connections
- `security-hub` - Security Hub findings aggregation and security standards
- `guardduty` - GuardDuty threat detection
- `cloudtrail` - CloudTrail API-activity logging into an encrypted S3 bucket
- `backup` - AWS Backup plans, vaults, and selections
- `sso` - IAM Identity Center (AWS SSO) permission sets and account assignments

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

### Registry Search Comparison (vs. Terraform Registry / HashiCorp MCP)

How does hybrid-semantic search actually compare to a plain keyword lookup against the public Terraform Registry? The registry endpoint used below — `GET /v1/modules/search?q=…&provider=aws` — is exactly the API that the official [`hashicorp/terraform-mcp-server`](https://github.com/hashicorp/terraform-mcp-server)'s `search_modules` tool wraps, so this doubles as an apples-to-apples comparison against that competitor's module search.

The benchmark reuses the same **golden set** as the searchability tests: all 54 modules, each queried 3 ways (exact name, keyword, natural language) — 162 labeled queries — asking *"is the expected module in the top-1 / top-3 results?"*. Registry results are scored two ways: `official` (hit only if the match comes from the `terraform-aws-modules` namespace — the same module we document) and `any-author` (hit if any namespace returns a name-matching module — deliberately generous to the registry).

| Query type | System | Top-1 | Top-3 |
|---|---|---:|---:|
| **keyword** (n=54) | **TFModSearch** (semantic, AWS curated) | **94.4%** | **100.0%** |
| | Registry — official `terraform-aws-modules` | 22.2% | 22.2% |
| | Registry — any-author aws module | 29.6% | 38.9% |
| **exact-name** (n=54) | **TFModSearch** | 100.0% | 100.0% |
| | Registry — official | 100.0% | 100.0% |
| | Registry — any-author | 100.0% | 100.0% |
| **natural-lang** (n=54) | **TFModSearch** | **81.5%** | **100.0%** |
| | Registry — official | 5.6% | 5.6% |
| | Registry — any-author | 13.0% | 14.8% |
| **OVERALL** (n=162) | **TFModSearch** | **92.0%** | **100.0%** |
| | Registry — official | 42.6% | 42.6% |
| | Registry — any-author | 47.5% | 51.2% |

**Takeaways:**

- **This is a retrieval-quality story, not a coverage story.** All **54/54** curated modules exist as standalone official `terraform-aws-modules` entries in the registry — the registry *can* return every one; it just doesn't surface them from a descriptive query.
- **Semantic search dominates on natural language.** For free-text queries (e.g. `managed kubernetes cluster` → `eks`, `serverless function execution` → `lambda`), TFModSearch keeps **100% top-3** while the official registry search lands **5.6%** (misses 51 of 54). Keyword search only matches when the query already contains the module's terms.
- **The registry's failure mode is "not in results at all," not mis-ranking.** Its official top-1 equals top-3 in every row — when the right module appears it's already #1 (download counts float it up); the problem is that for descriptive queries it doesn't appear.
- **Parity only on exact names.** If you already know the module name (`vpc`, `s3-bucket`), keyword search is fine — the entire value of semantic search is in the other two rows, where a user describes a *task* rather than a *name*.
- **Caveats (in the registry's favor):** the natural-language queries were authored alongside this corpus (mild home-turf bias, though they are generic task descriptions), and `any-author` credits the registry for same-named modules from *any* author — yet it still trails at 51.2% top-3 vs. our 100%.

Reproduce it yourself (opt-in, makes live calls to the public registry):

```bash
RUN_REGISTRY_BENCHMARK=1 pytest tests/integration/test_registry_comparison.py -v -s
```

The comparison is committed as `tests/integration/test_registry_comparison.py`. It stays hermetic in normal CI (live tests skip unless `RUN_REGISTRY_BENCHMARK=1`, and skip gracefully if the registry is unreachable); a network-free guard test pins the "100% top-3" figure on our side.

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
