"""Command line interface for AdoReviewLens."""

from __future__ import annotations

import json
from typing import Optional

import typer

from .errors import AzureDevOpsRequestError, MCPUserError, MissingConfigurationError
from .service import fetch_comments

app = typer.Typer(help="Fetch Azure DevOps PR comments.")


@app.command()
def fetch(
    pr: Optional[int] = typer.Option(None, "--pr", help="Numeric pull request identifier"),
    url: Optional[str] = typer.Option(None, "--url", help="Full Azure DevOps PR URL"),
    allow_cross_project: bool = typer.Option(False, "--allow-cross-project", help="Allow fetching outside default project"),
    project: Optional[str] = typer.Option(None, "--project", help="Override project name"),
    repo: Optional[str] = typer.Option(None, "--repo", help="Override repository name"),
) -> None:
    """Fetch active pull request comments and print JSON."""

    try:
        response = fetch_comments(
            pr_id=pr,
            pr_url=url,
            allow_cross_project=allow_cross_project,
            project=project,
            repo=repo,
        )
        typer.echo(json.dumps(response.model_dump(by_alias=True), indent=2))
    except MCPUserError as exc:
        typer.echo(
            json.dumps({"error": str(exc), "status": exc.status}),
            err=True,
        )
        raise typer.Exit(code=1)
    except MissingConfigurationError as exc:
        typer.echo(
            json.dumps({"error": str(exc), "status": 400}),
            err=True,
        )
        raise typer.Exit(code=1)
    except AzureDevOpsRequestError as exc:
        typer.echo(
            json.dumps({"error": str(exc), "status": exc.status}),
            err=True,
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
