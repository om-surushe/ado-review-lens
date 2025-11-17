# AdoReviewLens
<!-- mcp-name: io.github.om-surushe/ado-review-lens -->

Utilities for fetching active Azure DevOps PR comments via MCP interface.

## Requirements

- Python 3.10+
- Azure DevOps Personal Access Token with Code (read) and Pull Requests (read)

## Installation

### Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
# edit .env with your AZDO_ORG_URL, AZDO_PAT, AZDO_PROJECT, AZDO_REPO
```

Alternatively, if you prefer [uv](https://docs.astral.sh/uv/):

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
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

The official MCP tooling expects `uv` to be available:

```bash
uv tool install mcp

# Register the server with an MCP client (e.g., Claude Desktop)
uv run mcp install src/ado_review_lens/server.py --name "ADO Review Lens"

# Launch the MCP Inspector for interactive testing
uv run mcp dev src/ado_review_lens/server.py --with-editable .
```

The install command accepts `-v KEY=value` or `-f .env` flags if you want to supply Azure DevOps environment variables during registration.

### Manual MCP client registration

Some MCP clients accept explicit stdio configurations:

```json
{
  "mcpServers": {
    "ado-review-lens": {
      "command": "python", // or "python3" or path to python interpreter
      "args": [
        "-m",
        "ado_review_lens.server"
      ],
      "env": {
        "AZDO_ORG_URL": "https://dev.azure.com/<org>",
        "AZDO_PAT": "<personal_access_token>",
        "AZDO_PROJECT": "<default_project>",
        "AZDO_REPO": "<default_repo>"
      }
    }
  }
}
```

Merge this snippet with existing definitions as needed, then restart or refresh your client so it discovers the server.

### Other MCP clients

The repository ships with a `server.json` definition describing the PyPI package and stdio transport. Any MCP-compatible client that accepts `server.json` entries can load the server by either:

1. Copying `server.json` into the client’s configuration directory, or
2. Merging the `io.github.om-surushe/ado-review-lens` entry into an existing MCP registry file.

The critical values to replicate are:

```json
{
  "name": "io.github.om-surushe/ado-review-lens",
  "transport": {
    "type": "stdio",
    "command": ["python", "-m", "ado_review_lens.server"]
  }
}
```

Ensure the environment variables required by Azure DevOps (PAT, org URL, project, repo) are set in the client before launching the server process.
