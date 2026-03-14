# TraceLite Development Roadmap

This roadmap outlines the development plan for TraceLite — DevTools for your backend APIs. TraceLite evolves through `0.x` versions to build core features. Once all planned features are complete and stable, **v1.0.0** will be officially released.

---

## Milestones & Features

### v0.4.x — Foundation & CLI Usability

> The initial foundation release. TraceLite started as a CLI-first tool for viewing and exporting HTTP request logs from a local SQLite database. This version established the core storage format and command-line interface.

- [x] Basic `view` command implementation — display recent request logs in a Rich-formatted terminal table
- [x] Add `--columns` option to control output fields — allow developers to select which columns appear in the table
- [ ] Improve `--help` descriptions and CLI UX — more descriptive help text and error messages
- [ ] Add basic input validation and friendly error messages — handle missing database, invalid arguments

---

### v0.5.x — Web-First DevTools (Current)

> The transformation from CLI-first to web-first. This release adds an embedded web dashboard, full request and response body capture, sensitive data masking, response diffing, request replay, and SQL query tracing. TraceLite becomes a complete DevTools experience for backend APIs with one-line setup.

- [x] One-line setup API: `enable_tracing(app)` — auto-detect FastAPI, Flask, or Django and apply middleware + dashboard in a single call
- [x] Embedded web dashboard at `/_tracelite` — dark-themed, DevTools-style UI with real-time request inspection, search, and method filtering
- [x] Response body capture for all frameworks — ASGI streaming capture, WSGI response wrapping, Django middleware body capture
- [x] Request body capture with sensitive data masking — recursive dictionary traversal, case-insensitive key matching
- [x] Body masking — mask sensitive fields in both headers and JSON bodies with configurable key list
- [x] Response diff (`diff_responses()`, `diff_responses_text()`) — compare responses from the same endpoint to identify changes
- [x] Request replay via curl generation (`generate_curl()`) — generate and copy complete curl commands from captured requests
- [x] Query string capture and display — parse and store query parameters separately from the path
- [x] `fetch_by_path()` storage method — path-based log retrieval for the diff feature
- [x] Framework support: FastAPI, Flask, Django — all framework dependencies are optional extras
- [x] TOML config support with `[capture]`, `[dashboard]`, `[slow]`, and `[filter]` sections
- [x] Dashboard mount helpers for Starlette, Flask, Django — framework-specific dashboard integration
- [x] Example projects: basic setup, debugging workflows, performance analysis, security/masking, testing
- [ ] Publish v0.5.0 to PyPI

---

### v0.6.x — Advanced Query & Export

> Make TraceLite more powerful for querying and exporting trace data. This version adds SQL-like filtering, regex search, and additional export formats for integration with other tools.

- [ ] SQL-like query options — support `WHERE`, `ORDER BY`, `LIMIT` style filtering on stored logs
- [ ] Wildcard and regex search — pattern matching on paths, headers, and body content
- [ ] Enhanced `export` command — filtering options to export specific time ranges, status codes, or paths
- [ ] Additional output formats — JSON, CSV, NDJSON for streaming export
- [ ] Field anonymization on export — strip or mask sensitive fields when sharing exported data

---

### v0.7.x — Log Management Features

> Enable persistent log storage management. As TraceLite databases grow, developers need tools to manage retention, rotation, and cleanup of stored trace data.

- [ ] Log rotation — size-based and date-based rotation policies
- [ ] Retention policy configuration — automatically delete logs older than a configurable threshold
- [ ] `clear` command — manual log cleanup with optional filters (older than, matching path, etc.)
- [ ] Storage directory configuration — configure where TraceLite stores its database files

---

### v0.8.x — Interactive Mode & Dashboard Enhancements

> Enhance the embedded dashboard with real-time capabilities and add interactive features for deeper inspection.

- [ ] Statistics command — `tracelite stats` showing total requests, error ratio, average duration, unique paths
- [ ] WebSocket real-time updates — push new requests to the dashboard without polling
- [ ] Session-based log separation — isolate logs per development session for cleaner debugging
- [ ] `session list` and `session delete` commands — manage and clean up individual sessions

---

### v0.9.x — External Integration & Extensibility

> Connect TraceLite to external systems and provide extensibility points for custom workflows.

- [ ] Plugin architecture — register custom log post-processing handlers
- [ ] Python API for programmatic log access — query and analyze stored traces from Python code
- [ ] Webhook integration — send alerts to Slack, Discord, or custom webhooks for specific conditions
- [ ] Notification throttle — prevent alert spamming with configurable cooldown periods

---

## v1.0.0 — Stable Release

> The first stable release with a complete, polished feature set. API stability guaranteed from this point forward.

- [ ] Complete documentation and usage examples
- [ ] Test coverage exceeds 90%
- [ ] Automated release workflow (GitHub Actions → PyPI)
- [ ] Refined CLI UX and output consistency
- [ ] Contribution guide and issue templates
- [ ] Public API review and stabilization for long-term maintenance

---

## Future Ideas

The following enhancements may be considered for future development. Each will be evaluated carefully to ensure TraceLite remains lightweight and developer-friendly.

### Possible Enhancements

- Multi-source log monitoring
- Log session replay
- Log snapshot and sharing
- CLI history and bookmarks
- Alternative storage backends (PostgreSQL, etc.)

### Out of Scope

TraceLite is intentionally scoped to local development tooling. The following features are explicitly out of scope:

- Remote log streaming over the network
- Centralized log storage and team collaboration
- Integration with Prometheus, Grafana, or production monitoring systems
- Machine learning-based anomaly detection

---

**Philosophy:**
TraceLite is the **SQLite of tracing** — minimal, embedded, and useful by default. Like Chrome DevTools for backend APIs, it provides instant visibility into HTTP traffic with zero setup cost. Heavyweight features that require server infrastructure are excluded to maintain simplicity.
