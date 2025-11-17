"""Azure DevOps HTTP client utilities."""

from __future__ import annotations

from typing import Any, Dict

import requests

from .errors import AzureDevOpsRequestError, MCPUserError
from .models import MCPConfig, PullRequestTarget

_API_VERSION = "7.1"


class AzureDevOpsClient:
    """Lightweight Azure DevOps REST API client."""

    def __init__(self, config: MCPConfig) -> None:
        self._config = config
        self._base_url = config.organization_url.rstrip("/")
        self._session = requests.Session()
        self._session.auth = ("", config.personal_access_token)
        self._session.headers.update({"Content-Type": "application/json"})

    def list_threads(self, target: PullRequestTarget) -> Dict[str, Any]:
        """Return raw thread payload for a pull request."""

        url = (
            f"{self._base_url}/{target.project}/_apis/git/repositories/"
            f"{target.repository}/pullRequests/{target.pull_request_id}/threads"
        )
        response = self._session.get(url, params={"api-version": _API_VERSION})

        if response.status_code == 404:
            raise MCPUserError("PR not found", status=404)
        if response.status_code == 401:
            raise MCPUserError("Insufficient permissions", status=401)
        if response.status_code >= 400:
            raise AzureDevOpsRequestError(
                f"Azure DevOps request failed with {response.status_code}",
                status=response.status_code,
            )

        return response.json()

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "AzureDevOpsClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
