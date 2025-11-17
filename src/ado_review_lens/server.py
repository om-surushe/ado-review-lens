"""Model Context Protocol server entrypoint."""

from __future__ import annotations

from typing import Optional

from mcp.server.fastmcp import FastMCP

from .errors import AzureDevOpsRequestError, MCPUserError, MissingConfigurationError
from .service import fetch_comments

mcp = FastMCP("AdoReviewLens")


@mcp.tool()
def fetch_pr_comments(
    pr: Optional[int] = None,
    url: Optional[str] = None,
    allow_cross_project: bool = False,
    project: Optional[str] = None,
    repo: Optional[str] = None,
) -> dict:
    """Fetch active Azure DevOps pull request comments."""

    try:
        response = fetch_comments(
            pr_id=pr,
            pr_url=url,
            allow_cross_project=allow_cross_project,
            project=project,
            repo=repo,
        )
        return response.model_dump(by_alias=True)
    except MissingConfigurationError as exc:
        raise ValueError(str(exc)) from exc
    except MCPUserError as exc:
        raise ValueError(f"{exc.status}: {exc}") from exc
    except AzureDevOpsRequestError as exc:
        raise RuntimeError(f"Azure DevOps error ({exc.status}): {exc}") from exc


def main() -> None:
    """Run the MCP server using stdio transport."""

    mcp.run()


if __name__ == "__main__":
    main()
