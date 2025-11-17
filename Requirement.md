# AdoReviewLens — Azure DevOps PR Comment MCP (Python)

*This MCP will be implemented in **Python** for simplicity, portability, and strong ecosystem support.*

A lightweight MCP designed to fetch and present **active pull-request comments** from Azure DevOps. The goal is to provide a clean, reliable interface for extracting unresolved review conversations for faster code review and automation workflows.

---

## 1. Purpose

This MCP retrieves active comment threads from a specified Azure DevOps pull request, normalizes them into a consistent data model, and outputs structured JSON suitable for tooling, automation, or review dashboards.

---

## 2. Acceptance Criteria

### Success Cases

* For a valid PR and valid authentication, the MCP exits with code `0` and returns JSON containing:

  * `pr`, `repo`, `activeThreads`, and `comments` (an array of comment objects).
  * Each comment includes: `commentText`, `filePath`, `lineRange` or `lineNumber`, `authorDisplayName`, `authorId`, `timestamp`, and `threadId`.

### No Active Threads

* Exits `0` with:

  ```json
  { "activeThreads": 0, "comments": [] }
  ```

### Error Cases

* **Invalid PR / Not Found:** non‑zero exit, JSON `{ "error": "PR not found", "status": 404 }`.
* **Auth Failure:** non‑zero exit, JSON `{ "error": "Insufficient permissions", "status": 401 }`.

---

## 3. Definition of “Active Comments”

Active comments are **unresolved**, **non-deleted** comments within pull‑request threads. A flag may later allow including resolved items.

---

## 4. Inputs and Validation

The MCP supports both simple numeric PR identifiers and full Azure DevOps PR URLs.

### Accepted Formats

* **Numeric PR ID** (e.g., `123`).
* **Full PR URL**, such as:
  `https://dev.azure.com/{org}/{project}/_git/{repo}/pullrequest/{id}`

### Normalization Rules

* When both `--repo`/`--project` flags and numeric ID are provided, flags take precedence.
* For URLs, org/project/repo parsed from the URL override all defaults.

### Missing Context

* For numeric PR IDs, `AZDO_PROJECT` (and repo if required) must be available.
* Missing context triggers:

  ```json
  { "error": "Missing project or repo context", "status": 400 }
  ```

### Cross-Project Handling

* By default, the MCP rejects PRs outside the configured project/repo.
* Override via `--allow-cross-project` or API field `allowCrossProject: true`.

### Org Validation

If URL org does not match `AZDO_ORG_URL`:

```json
{ "error": "Organization mismatch", "status": 400 }
```

### URL Parsing Failures

Malformed URLs produce:

```json
{ "error": "Invalid PR URL", "status": 400 }
```

---

## 5. Authentication and Token Setup

The MCP uses a **read‑only Azure DevOps Personal Access Token (PAT)**. No service principal or Entra-based authentication is used.

### Required Scopes

* `Code (read)`
* `Pull Requests (read)`

### Environment Variables

* `AZDO_PAT` — read‑only PAT
* `AZDO_ORG_URL` — `https://dev.azure.com/{org}`
* `AZDO_PROJECT` — default project name (optional)

### Storage & Rotation

* PATs should be short‑lived and rotated every 30–90 days.
* CI systems should pull the PAT from secure secret stores.
* Token values must never appear in logs.

### Auth Error Response

```json
{ "error": "Insufficient permissions", "status": 401, "detail": "missing scope: Code (read)" }
```

---

## 6. CLI Interface

* `mcp fetch --pr 123 --repo service-a`
* `mcp fetch --url "https://dev.azure.com/acme/ops/_git/web/pullrequest/456"`
* `mcp fetch --pr 789 --allow-cross-project`

---

## 7. HTTP API Interface

* `POST /api/v1/pr/comments` with body:

  ```json
  { "prId": 123 }
  ```
* Using a URL:

  ```json
  { "prUrl": "https://dev.azure.com/org/proj/_git/repo/pullrequest/456" }
  ```
* Enabling cross-project:

  ```json
  { "prId": 123, "allowCrossProject": true }
  ```

---

## 8. Data Model for Comments

The MCP outputs comments in a stable, structured format.

### Fields

* `commentId` — unique ID
* `threadId` — thread grouping identifier
* `commentText` — full comment body
* `filePath` — file where comment appears (or null)
* `lineRange` — e.g., `45-47` (or single line number)
* `authorDisplayName`
* `authorId`
* `timestamp` — ISO 8601
* `status` — `active` or `resolved`
* `isDeleted` — boolean
* `resolvedBy` — who resolved (optional)
* `externalId` — optional linkage for future update workflows

### Example

```json
{
  "commentId": "cmt-1001",
  "threadId": 2001,
  "commentText": "Please fix the null check",
  "filePath": "src/app.js",
  "lineRange": "45-47",
  "authorDisplayName": "Alice",
  "authorId": "alice@org",
  "timestamp": "2025-11-16T14:22:00Z",
  "status": "active",
  "isDeleted": false,
  "externalId": null
}
```

### Mapping & Updates

* Use `threadId` + `commentId` as stable keys.
* Only active comments are included unless a flag explicitly broadens scope.

---

## 9. Example Success Response

```json
{
  "pr": 123,
  "repo": "service-a",
  "activeThreads": 2,
  "comments": [ /* comment objects */ ]
}
```

---

## 10. Test Checklist

* [ ] JSON shape matches spec
* [ ] Supports both numeric ID and URL input
* [ ] Handles zero active threads
* [ ] Correctly rejects cross-project access unless allowed
* [ ] Provides clear error messages
* [ ] Enforces minimal PAT scopes

---

A clean, consistent specification ensures this MCP behaves predictably, integrates smoothly with automation, and remains easy to maintain and extend.
