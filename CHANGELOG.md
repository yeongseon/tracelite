# TraceLite Changelog

All notable changes to TraceLite are documented in this file.

---

<!-- insertion marker -->
<a name="v0.5.0"></a>
## [v0.5.0](https://github.com/yeongseon/tracelite/compare/v0.4.0...v0.5.0) — Web-First DevTools Release

This release transforms TraceLite from a CLI-first prototype into a web-first DevTools experience. TraceLite now includes an embedded web dashboard, full request and response body capture, sensitive data masking, response diffing, request replay, SQL query tracing, and one-line setup for all three supported frameworks.

### New Features

- **Embedded Web Dashboard.** A dark-themed, DevTools-style web UI is now served directly from the application server at `/_tracelite`. The dashboard displays a real-time list of captured requests with search, HTTP method filtering, and auto-refresh every 5 seconds. Clicking any request opens a detail panel showing headers, bodies, query parameters, SQL queries, and timing information.

- **One-Line Setup API.** The new `enable_tracing(app)` function auto-detects whether the application is FastAPI, Flask, or Django, applies the appropriate middleware, and mounts the dashboard — all in a single call. This replaces the previous multi-step manual middleware configuration.

- **Response Body Capture.** All three framework middlewares (FastAPI/ASGI, Flask/WSGI, Django) now capture the full response body in addition to request bodies. This is required for the response diff feature and enables full payload inspection in the dashboard.

- **Sensitive Data Masking.** TraceLite automatically masks sensitive fields in both headers and bodies. Masking uses recursive dictionary traversal with case-insensitive key matching. Default masked fields: `password`, `token`, `authorization`, `secret`. Custom mask keys can be configured via TOML or the Python API.

- **Response Diff.** New `diff_responses()` and `diff_responses_text()` functions compare two response bodies from the same endpoint. The dashboard includes an inline diff viewer that compares the current response with the previous response for the same path, making it easy to spot changes.

- **Request Replay.** New `generate_curl()` function generates a complete curl command from any captured request, including method, headers, and body. The dashboard provides a one-click copy button that places the full curl command on the clipboard.

- **SQL Query Capture.** Per-request SQL query tracing via Python's `contextvars` with SQLAlchemy event hooks. When enabled, SQL queries and their execution times are associated with the HTTP request that triggered them and displayed in the dashboard's request detail panel.

- **Slow Request Highlighting.** Requests that exceed a configurable duration threshold are highlighted with a ⚠ icon in the dashboard. The default threshold is 1000ms and can be adjusted via the `slow_threshold_ms` configuration option.

- **Query String Capture.** Query parameters are now parsed and stored separately from the request path, allowing structured inspection in the dashboard.

- **Dashboard API Endpoint.** `/_tracelite/api/config` exposes dashboard configuration for the frontend.

### Enhancements

- Added `capture_sql` and `slow_threshold_ms` fields to `TraceliteConfig` with TOML mapping under `[capture]` and `[slow]` sections respectively.
- Added `sql_queries` field to the `RequestLog` data model and extended the SQLite schema to 14 columns.
- Added `fetch_by_path()` method to `ILoggerStorage` for path-based log retrieval, used by the diff feature to find previous responses for the same endpoint.
- Dashboard auto-refreshes every 5 seconds. Search and method filter state are preserved across refreshes.
- Toast notifications for clipboard copy actions in the dashboard.
- Backward-compatible schema handling supports 12, 13, and 14 column SQLite formats for seamless upgrades from older versions.

### Framework Support

- **FastAPI / Starlette** — ASGI middleware with streaming response body capture via `StreamingResponse` wrapping.
- **Flask** — WSGI middleware with full request and response body capture.
- **Django** — `MiddlewareMixin` with body and query parameter capture.
- All framework dependencies are optional: `pip install tracelite[fastapi]`, `pip install tracelite[flask]`, `pip install tracelite[django]`.

### Documentation

- Added `docs/PRD.md` — Product Requirements Document covering vision, features, architecture, and examples strategy.
- Added `AGENTS.md` — Project knowledge base for AI-assisted development.
- Rewrote `README.md` with comprehensive documentation, one-line setup instructions, and configuration reference.
- Realigned `ROADMAP.md` with PRD direction and updated milestone status.
- Added comprehensive example collection: basic framework setup, debugging workflows, performance analysis, security/masking configuration, and testing integration.

---

<a name="v0.4.0"></a>
## v0.4.0 — CLI Foundation

Initial CLI release with terminal-based log viewing and export.

- Basic `view` command for terminal log inspection.
- `--columns` option to control which fields are displayed.
- JSON and CSV export via `tracelite export`.

---

<a name="v0.1.0"></a>
## [v0.1.0](https://github.com/yeongseon/tracelite/compare/0c09570de567aa5c3a6d1b6fe0478e7a6cfde5db...v0.1.0) (2025-04-02)

Initial release. Core storage and middleware infrastructure.
