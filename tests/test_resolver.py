"""Tests for pull request target resolution logic."""

import pytest

from ado_review_lens.errors import MCPUserError
from ado_review_lens.models import MCPConfig
from ado_review_lens.resolver import resolve_target


@pytest.fixture
def base_config() -> MCPConfig:
    return MCPConfig(
        organization_url="https://dev.azure.com/example",
        personal_access_token="token",
    )


def test_resolve_numeric_missing_context(base_config: MCPConfig) -> None:
    with pytest.raises(MCPUserError) as exc:
        resolve_target(
            config=base_config,
            pr_id=42,
            pr_url=None,
            allow_cross_project=False,
            project_override=None,
            repo_override=None,
        )

    assert "Missing project or repo context" in str(exc.value)


def test_resolve_url_success(base_config: MCPConfig) -> None:
    config = base_config.model_copy(update={"default_project": "team", "default_repository": "repo"})

    target = resolve_target(
        config=config,
        pr_id=None,
        pr_url="https://dev.azure.com/example/team/_git/repo/pullrequest/123",
        allow_cross_project=False,
        project_override=None,
        repo_override=None,
    )

    assert target.project == "team"
    assert target.repository == "repo"
    assert target.pull_request_id == 123


def test_resolve_url_cross_project_blocked(base_config: MCPConfig) -> None:
    config = base_config.model_copy(update={"default_project": "team", "default_repository": "repo"})

    with pytest.raises(MCPUserError) as exc:
        resolve_target(
            config=config,
            pr_id=None,
            pr_url="https://dev.azure.com/example/other/_git/repo/pullrequest/123",
            allow_cross_project=False,
            project_override=None,
            repo_override=None,
        )

    assert "Cross-project access not allowed" in str(exc.value)


def test_resolve_invalid_url(base_config: MCPConfig) -> None:
    with pytest.raises(MCPUserError) as exc:
        resolve_target(
            config=base_config,
            pr_id=None,
            pr_url="https://example.com/not/azure",
            allow_cross_project=False,
            project_override=None,
            repo_override=None,
        )

    assert "Invalid PR URL" in str(exc.value)
