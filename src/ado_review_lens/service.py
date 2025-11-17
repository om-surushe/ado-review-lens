"""Service layer for fetching Azure DevOps pull request comments."""

from __future__ import annotations

from typing import Any, Dict, List

from .azure import AzureDevOpsClient
from .config import load_config
from .models import CommentModel, CommentsResponse
from .resolver import resolve_target


def fetch_comments(
    *,
    pr_id: int | None = None,
    pr_url: str | None = None,
    allow_cross_project: bool = False,
    project: str | None = None,
    repo: str | None = None,
) -> CommentsResponse:
    """Fetch active Azure DevOps pull request comments."""

    config = load_config()
    target = resolve_target(
        config=config,
        pr_id=pr_id,
        pr_url=pr_url,
        allow_cross_project=allow_cross_project,
        project_override=project,
        repo_override=repo,
    )

    with AzureDevOpsClient(config) as client:
        payload = client.list_threads(target)

    threads = payload.get("value", []) if isinstance(payload, dict) else []
    comments: List[CommentModel] = []
    active_thread_ids: set[int] = set()

    for thread in threads:
        if thread.get("isDeleted"):
            continue
        status = (thread.get("status") or "").lower()
        if status and status != "active":
            continue

        thread_comments = _normalize_thread_comments(thread)
        if thread_comments:
            thread_id = thread.get("id")
            if isinstance(thread_id, int):
                active_thread_ids.add(thread_id)
            comments.extend(thread_comments)

    return CommentsResponse(
        pr=target.pull_request_id,
        repo=target.repository,
        activeThreads=len(active_thread_ids),
        comments=comments,
    )


def _normalize_thread_comments(thread: Dict[str, Any]) -> List[CommentModel]:
    normalized: List[CommentModel] = []
    thread_id = thread.get("id")

    for comment in thread.get("comments", []):
        if comment.get("isDeleted"):
            continue
        if comment.get("commentType") == "system":
            continue

        content = comment.get("content")
        if not content:
            continue

        normalized.append(
            CommentModel(
                commentId=str(comment.get("id")),
                threadId=int(thread_id) if thread_id is not None else -1,
                commentText=content,
                filePath=_extract_file_path(thread),
                lineRange=_extract_line_range(thread),
                authorDisplayName=_extract_author_name(comment),
                authorId=_extract_author_id(comment),
                timestamp=_extract_timestamp(comment),
                status=thread.get("status") or "unknown",
                isDeleted=False,
                resolvedBy=_extract_resolved_by(thread),
                externalId=None,
            )
        )

    return normalized


def _extract_file_path(thread: Dict[str, Any]) -> str | None:
    thread_context = thread.get("threadContext") or {}
    file_path = thread_context.get("filePath")
    if isinstance(file_path, str):
        return file_path
    return None


def _extract_line_range(thread: Dict[str, Any]) -> str | None:
    thread_context = thread.get("threadContext") or {}
    start = thread_context.get("rightFileStart") or thread_context.get("leftFileStart")
    end = thread_context.get("rightFileEnd") or thread_context.get("leftFileEnd")

    if not isinstance(start, dict):
        return None

    start_line = start.get("line")
    if start_line is None:
        return None

    end_line = start_line
    if isinstance(end, dict):
        end_line = end.get("line", start_line)

    try:
        start_line = int(start_line)
        end_line = int(end_line)
    except (TypeError, ValueError):
        return None

    if start_line <= 0:
        return None

    if start_line == end_line:
        return str(start_line)

    return f"{start_line}-{end_line}"


def _extract_author_name(comment: Dict[str, Any]) -> str:
    author = comment.get("author") or {}
    name = author.get("displayName") or author.get("uniqueName") or "Unknown"
    return str(name)


def _extract_author_id(comment: Dict[str, Any]) -> str:
    author = comment.get("author") or {}
    identifier = author.get("id") or author.get("uniqueName") or "unknown"
    return str(identifier)


def _extract_timestamp(comment: Dict[str, Any]) -> str:
    return str(comment.get("lastUpdatedDate") or comment.get("publishedDate") or "")


def _extract_resolved_by(thread: Dict[str, Any]) -> str | None:
    properties = thread.get("properties") or {}
    resolved_by = properties.get("CodeReviewResolvedBy") or properties.get(
        "Microsoft.TeamFoundation.Discussion.ThreadResolvedBy"
    )

    if isinstance(resolved_by, dict):
        value = resolved_by.get("$value")
        if value:
            return str(value)
    elif resolved_by:
        return str(resolved_by)
    return None
