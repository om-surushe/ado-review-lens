"""Utilities to resolve pull request identifiers."""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlparse

from .errors import MCPUserError
from .models import MCPConfig, PullRequestTarget

_PR_URL_PATTERN = re.compile(
    r"^https://dev\.azure\.com/(?P<org>[^/]+)/(?P<project>[^/]+)/_git/(?P<repo>[^/]+)/pullrequest/(?P<id>\d+)(?:/)?$",
    re.IGNORECASE,
)


def _extract_org_name(org_url: str) -> str:
    return org_url.rstrip("/").split("/")[-1]


def resolve_target(
    *,
    config: MCPConfig,
    pr_id: Optional[int],
    pr_url: Optional[str],
    allow_cross_project: bool,
    project_override: Optional[str],
    repo_override: Optional[str],
) -> PullRequestTarget:
    """Resolve pull request target information from inputs."""

    if pr_url:
        return _resolve_from_url(
            config=config,
            pr_url=pr_url,
            allow_cross_project=allow_cross_project,
        )

    if pr_id is None:
        raise MCPUserError("Missing prId or prUrl", status=400)

    project = project_override or config.default_project
    repository = repo_override or config.default_repository

    if not project or not repository:
        raise MCPUserError("Missing project or repo context", status=400)

    return _build_target(
        config=config,
        project=project,
        repository=repository,
        pull_request_id=pr_id,
        allow_cross_project=allow_cross_project,
    )


def _resolve_from_url(
    *,
    config: MCPConfig,
    pr_url: str,
    allow_cross_project: bool,
) -> PullRequestTarget:
    match = _PR_URL_PATTERN.match(pr_url)
    if not match:
        raise MCPUserError("Invalid PR URL", status=400)

    org_from_url = match.group("org")
    org_from_config = _extract_org_name(config.organization_url)
    if org_from_url.lower() != org_from_config.lower():
        raise MCPUserError("Organization mismatch", status=400)

    project = match.group("project")
    repo = match.group("repo")
    pr_id = int(match.group("id"))

    return _build_target(
        config=config,
        project=project,
        repository=repo,
        pull_request_id=pr_id,
        allow_cross_project=allow_cross_project,
    )


def _build_target(
    *,
    config: MCPConfig,
    project: str,
    repository: str,
    pull_request_id: int,
    allow_cross_project: bool,
) -> PullRequestTarget:
    default_project = config.default_project
    default_repository = config.default_repository

    if not allow_cross_project:
        if default_project and project.lower() != default_project.lower():
            raise MCPUserError("Cross-project access not allowed", status=400)
        if default_repository and repository.lower() != default_repository.lower():
            raise MCPUserError("Cross-project access not allowed", status=400)

    return PullRequestTarget(
        organization=_extract_org_name(config.organization_url),
        project=project,
        repository=repository,
        pullRequestId=pull_request_id,
    )
