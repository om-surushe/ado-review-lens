"""Configuration helpers for AdoReviewLens MCP."""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

from .errors import MissingConfigurationError
from .models import MCPConfig


def load_config() -> MCPConfig:
    """Load configuration from environment variables."""

    # Load values from a local .env file if present.
    load_dotenv()

    organization_url = os.getenv("AZDO_ORG_URL")
    pat = os.getenv("AZDO_PAT")
    default_project = os.getenv("AZDO_PROJECT")
    default_repository = os.getenv("AZDO_REPO")

    if not organization_url:
        raise MissingConfigurationError("AZDO_ORG_URL is required")

    if not pat:
        raise MissingConfigurationError("AZDO_PAT is required")

    return MCPConfig(
        organization_url=organization_url.rstrip("/"),
        personal_access_token=pat,
        default_project=default_project,
        default_repository=default_repository,
    )


def env_override(value: Optional[str], env_var: str) -> Optional[str]:
    """Return `value` if provided, otherwise lookup `env_var`."""

    return value if value else os.getenv(env_var)
