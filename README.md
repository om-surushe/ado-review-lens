# AdoReviewLens
<!-- mcp-name: io.github.om-surushe/ado-review-lens -->

Utilities for fetching active Azure DevOps PR comments via MCP interface.

## Requirements

- Python 3.10+
- Azure DevOps Personal Access Token with Code (read) and Pull Requests (read)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
# edit .env with your AZDO_ORG_URL, AZDO_PAT, AZDO_PROJECT, AZDO_REPO
```

Running `python -m ado_review_lens.cli --help` will confirm the CLI is available.

## CLI usage

```bash
source .venv/bin/activate
python -m ado_review_lens.cli --pr 123
python -m ado_review_lens.cli --url "https://dev.azure.com/org/project/_git/repo/pullrequest/123"
python -m ado_review_lens.cli --pr 123 --allow-cross-project
```

## HTTP API server

```bash
source .venv/bin/activate
uvicorn ado_review_lens.api:app --reload
# POST /api/v1/pr/comments with JSON {"prId": 123}
```

## MCP server

```bash
source .venv/bin/activate
python -m ado_review_lens.server
```

Use the resulting stdio endpoint with the Model Context Protocol client of your choice (e.g., Claude Desktop or MCP Inspector).

### Installing via `mcp`

If you use the official MCP tooling (requires `uv`):

```bash
uv tool install mcp

# From the project root
uv run mcp install src/ado_review_lens/server.py

# Or run in dev/inspect mode
uv run mcp dev src/ado_review_lens/server.py
```

This registers the server with Claude Desktop or launches the MCP Inspector for interactive testing.
