"""Core data models for AdoReviewLens MCP."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PullRequestTarget(BaseModel):
    """Resolved target information for a pull request lookup."""


    model_config = ConfigDict(populate_by_name=True)

    organization: str
    project: str
    repository: str
    pull_request_id: int = Field(alias="pullRequestId")


class CommentModel(BaseModel):
    """Normalized comment representation returned by the MCP."""


    model_config = ConfigDict(populate_by_name=True)

    comment_id: str = Field(alias="commentId")
    thread_id: int = Field(alias="threadId")
    comment_text: str = Field(alias="commentText")
    file_path: Optional[str] = Field(default=None, alias="filePath")
    line_range: Optional[str] = Field(default=None, alias="lineRange")
    author_display_name: str = Field(alias="authorDisplayName")
    author_id: str = Field(alias="authorId")
    timestamp: str
    status: str
    is_deleted: bool = Field(alias="isDeleted")
    resolved_by: Optional[str] = Field(default=None, alias="resolvedBy")
    external_id: Optional[str] = Field(default=None, alias="externalId")


class CommentsResponse(BaseModel):
    """Top-level response envelope for CLI and HTTP outputs."""


    model_config = ConfigDict(populate_by_name=True)

    pr: Optional[int] = None
    repo: Optional[str] = None
    active_threads: int = Field(default=0, alias="activeThreads")
    comments: list[CommentModel] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Standardized error payload."""


    model_config = ConfigDict(populate_by_name=True)

    error: str
    status: int
    detail: Optional[str] = None


class FetchRequest(BaseModel):
    """Request payload for the HTTP API."""


    model_config = ConfigDict(populate_by_name=True)

    pr_id: Optional[int] = Field(default=None, alias="prId")
    pr_url: Optional[str] = Field(default=None, alias="prUrl")
    project: Optional[str] = None
    repo: Optional[str] = None
    allow_cross_project: bool = Field(default=False, alias="allowCrossProject")


class MCPConfig(BaseModel):
    """Runtime configuration sourced from environment variables."""


    model_config = ConfigDict(populate_by_name=True)

    organization_url: str
    default_project: Optional[str] = None
    default_repository: Optional[str] = None
    personal_access_token: str
