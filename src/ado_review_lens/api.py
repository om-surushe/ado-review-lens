"""HTTP API for AdoReviewLens MCP."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .errors import AzureDevOpsRequestError, MCPUserError, MissingConfigurationError
from .models import CommentsResponse, ErrorResponse, FetchRequest
from .service import fetch_comments

app = FastAPI(title="AdoReviewLens API")


@app.post("/api/v1/pr/comments", response_model=CommentsResponse)
async def get_pr_comments(request: FetchRequest) -> CommentsResponse:
    try:
        return fetch_comments(
            pr_id=request.pr_id,
            pr_url=request.pr_url,
            allow_cross_project=request.allow_cross_project,
            project=request.project,
            repo=request.repo,
        )
    except MCPUserError as exc:
        raise HTTPException(status_code=exc.status, detail=ErrorResponse(error=str(exc), status=exc.status).model_dump())
    except MissingConfigurationError as exc:
        raise HTTPException(status_code=400, detail=ErrorResponse(error=str(exc), status=400).model_dump())
    except AzureDevOpsRequestError as exc:
        raise HTTPException(status_code=exc.status, detail=ErrorResponse(error=str(exc), status=exc.status).model_dump())
