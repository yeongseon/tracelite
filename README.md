# TraceLite

[![CI](https://github.com/yeongseon/tracelite/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/yeongseon/tracelite/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/tracelite.svg)](https://pypi.org/project/tracelite/)
[![Coverage Status](https://coveralls.io/repos/github/yeongseon/tracelite/badge.svg?branch=main)](https://coveralls.io/github/yeongseon/tracelite?branch=main)

**DevTools for your backend APIs.** The SQLite of tracing — zero-friction embedded HTTP inspection.

---

## Executive Summary

- **One-line setup.** Add `enable_tracing(app)` and start inspecting HTTP traffic immediately — no agents, no collectors, no config files.
- **Embedded dashboard.** A dark-themed, DevTools-style web UI is served directly from your application server at `/_tracelite`. No external process required.
- **Full payload capture.** Every request header, request body, response header, and response body is captured and stored for inspection, diffing, and replay.
- **Zero-config storage.** All trace data is stored in a local SQLite database. No infrastructure. No setup. Just a single file.
- **Framework support.** TraceLite works with FastAPI, Flask, and Django. All framework dependencies are optional — install only what you need.

---

## What is TraceLite?

TraceLite gives your backend the same network inspection experience that Chrome DevTools gives your frontend. Every HTTP request and response flowing through your API is captured, stored, and made available through an embedded web dashboard and a terminal CLI.

TraceLite is designed for **local development and debugging**. It is not a replacement for production observability platforms like OpenTelemetry, Datadog, or Jaeger. Instead, TraceLite focuses on the developer workflow: install, configure nothing, and immediately see what your API is doing.

The name reflects the philosophy: **trace** (HTTP inspection) + **lite** (lightweight, embedded, minimal). Like SQLite is to databases, TraceLite is to tracing — the zero-friction embedded option that works out of the box.

No agents. No collectors. No YAML files. Just `pip install` and go.

---

## Quick Start

### 1. Install

```bash
pip install tracelite[fastapi]   # or tracelite[flask] / tracelite[django]
```

### 2. Add one line of code

```python
from tracelite import enable_tracing

app = FastAPI()  # or Flask(__name__) or Django WSGI app
enable_tracing(app)
```

### 3. Open the dashboard

Start your application and navigate to:

```
http://localhost:8000/_tracelite
```

Every request your API receives is now captured and visible in the dashboard. You can inspect headers, bodies, query parameters, status codes, and response times — all in real time.

---

## Features

### Embedded Web Dashboard

TraceLite serves a dark-themed, DevTools-style web dashboard directly from your application server at `/_tracelite`. The dashboard displays a live list of captured requests with search, method filtering, and auto-refresh every 5 seconds. Click any request to open a detail panel showing headers, bodies, query parameters, SQL queries, and timing information. No external server, no separate process, no additional port.

### Request and Response Body Capture

Every request and response payload is captured in full. This enables the response diff feature and allows you to inspect exactly what your API received and returned. Body capture is enabled by default and can be disabled via configuration if needed.

### Sensitive Data Masking

TraceLite automatically masks sensitive fields in both headers and bodies. By default, fields named `password`, `token`, `authorization`, and `secret` are replaced with `*****`. Masking uses recursive dictionary traversal with case-insensitive key matching, so nested JSON payloads are handled correctly. You can configure the list of masked keys via TOML config or the Python API.

### Response Diff

Compare two responses from the same endpoint to identify what changed. TraceLite provides `diff_responses()` for structured comparison and `diff_responses_text()` for unified text diff output. The dashboard includes an inline diff viewer that compares the current response with the previous response for the same path.

### Request Replay

Generate a `curl` command from any captured request using `generate_curl()`. The dashboard provides a one-click copy button that places the full curl command on your clipboard, including method, headers, and body. This makes it trivial to replay any request from your terminal.

### SQL Query Capture

TraceLite can trace SQL queries executed during each request. When enabled, it uses Python's `contextvars` to associate queries with the request that triggered them, and hooks into SQLAlchemy's event system to capture query text and execution time. SQL queries appear in the dashboard's request detail panel.

### Slow Request Highlighting

Requests that exceed a configurable duration threshold are highlighted with a warning icon in the dashboard. The default threshold is 1000ms and can be adjusted via the `slow_threshold_ms` configuration option.

### SQLite Storage

All trace data is stored in a local SQLite database file (`tracelite.db` by default). The schema includes 14 columns covering request metadata, headers, bodies, query parameters, and SQL queries. There is no external database to configure — TraceLite creates the file automatically on first run.

### One-Line Setup

The `enable_tracing(app)` function auto-detects whether your application is FastAPI, Flask, or Django, applies the appropriate middleware, and mounts the dashboard — all in a single call.

### CLI Viewer

TraceLite includes a terminal-based log viewer built with Typer and Rich. Use `tracelite view` to inspect recent requests in your terminal, and `tracelite export` to export logs as JSON or CSV.

---

## Configuration

TraceLite can be configured via a TOML file, via the Python API, or both. The configuration hierarchy is: **TOML file → app_config dict → defaults**.

### TOML Configuration

Create a `tracelite.toml` file in your project root:

```toml
[tracelite]
enabled = true

[storage]
type = "sqlite"
path = "tracelite.db"

[filter]
exclude_paths = ["/static", "/favicon.ico", "/_tracelite"]
mask_keys = ["password", "token", "authorization", "secret"]

[capture]
capture_body = true
# Enable SQL query capture (requires SQLAlchemy or Django ORM hooks)
capture_sql = false

[dashboard]
path = "/_tracelite"

[slow]
# Highlight requests slower than this threshold (in milliseconds)
threshold_ms = 1000

[view]
# Columns to display in 'tracelite view' output
columns = ["timestamp", "client_ip", "method", "path", "status", "duration"]
```

### Programmatic Configuration

```python
from tracelite import enable_tracing
from tracelite.core.config import TraceliteConfig

config = TraceliteConfig(
    enabled=True,
    db_path="my_traces.db",
    exclude_paths=["/_tracelite", "/health", "/metrics"],
    mask_keys=["password", "token", "authorization", "secret", "api_key"],
    capture_body=True,
    capture_sql=False,
    slow_threshold_ms=1000,
    dashboard_path="/_tracelite",
)
enable_tracing(app, config=config)
```

### Configuration Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `True` | Enable or disable tracing globally |
| `db_path` | str | `"tracelite.db"` | Path to the SQLite database file |
| `capture_body` | bool | `True` | Capture request and response bodies |
| `capture_sql` | bool | `False` | Capture SQL queries per request |
| `dashboard_path` | str | `"/_tracelite"` | URL path for the embedded dashboard |
| `exclude_paths` | list | `["/static", "/favicon.ico"]` | Paths to exclude from tracing |
| `mask_keys` | list | `["password", "token", "authorization", "secret"]` | Field names to mask in headers and bodies |
| `slow_threshold_ms` | int | `1000` | Duration threshold (ms) for slow request highlighting |
| `view_columns` | list | `["timestamp", "client_ip", "method", "path", "status", "duration"]` | Columns shown in CLI viewer |

---

## Framework Support

TraceLite supports three Python web frameworks. All framework dependencies are optional — install only the extra you need.

### FastAPI / Starlette

```bash
pip install tracelite[fastapi]
```

```python
from fastapi import FastAPI
from tracelite import enable_tracing

app = FastAPI()
enable_tracing(app)
```

Or with manual middleware setup:

```python
from fastapi import FastAPI
from tracelite.middleware.fastapi import TraceliteMiddleware
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.core.config import load_config

app = FastAPI()
app.add_middleware(TraceliteMiddleware, storage=SQLiteStorage(), config=load_config())
```

### Flask

```bash
pip install tracelite[flask]
```

```python
from flask import Flask
from tracelite import enable_tracing

app = Flask(__name__)
enable_tracing(app)
```

Or with manual middleware setup:

```python
from flask import Flask
from tracelite.middleware.flask import TraceliteMiddleware
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.core.config import load_config

app = Flask(__name__)
app.wsgi_app = TraceliteMiddleware(app.wsgi_app, SQLiteStorage(), load_config())
```

### Django

```bash
pip install tracelite[django]
```

```python
from tracelite import enable_tracing

# In your Django WSGI application
enable_tracing(application)
```

---

## CLI

TraceLite provides a command-line interface built with Typer and Rich for terminal-based inspection and export.

```bash
# View recent request logs in a Rich table
tracelite view

# Select specific columns
tracelite view --columns method,path,status_code

# Export logs as JSON
tracelite export --format json > logs.json

# Export logs as CSV
tracelite export --format csv > logs.csv
```

---

## Installation Options

```bash
pip install tracelite              # Core only (CLI, storage, config)
pip install tracelite[fastapi]     # + FastAPI/Starlette support
pip install tracelite[flask]       # + Flask support
pip install tracelite[django]      # + Django support
```

**Python version:** 3.9 or later.

**Core dependencies:** pydantic, typer, rich, tomli. All framework dependencies (fastapi, flask, django) are optional extras.

---

## Examples

The [`examples/`](./examples) directory contains runnable examples organized by use case:

| Directory | Description |
|-----------|-------------|
| [`examples/basic/`](./examples/basic/) | FastAPI, Flask, and Django setup with `enable_tracing()` |
| [`examples/debugging/`](./examples/debugging/) | Auth header inspection, payload debugging, response diff |
| [`examples/security/`](./examples/security/) | Sensitive data masking configuration |
| [`examples/performance/`](./examples/performance/) | Slow request detection, SQLAlchemy query tracing |
| [`examples/testing/`](./examples/testing/) | Debugging failing tests with captured traces |

Each example is self-contained and can be run independently. See the README in each directory for instructions.

---

## Architecture

TraceLite operates as an embedded middleware layer inside your application:

```
┌─────────────────────────────────────────────┐
│                  Your App                   │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │        Capture Layer                │    │
│  │   (HTTP middleware per framework)   │    │
│  └──────────┬──────────────────────────┘    │
│             │                               │
│  ┌──────────▼──────────────────────────┐    │
│  │        TraceLite Core               │    │
│  │  ┌──────────┐  ┌────────────────┐   │    │
│  │  │ Storage  │  │  API Layer     │   │    │
│  │  │ (SQLite) │  │ (trace query)  │   │    │
│  │  └──────────┘  └───────┬────────┘   │    │
│  │                        │            │    │
│  │  ┌─────────────────────▼────────┐   │    │
│  │  │      Web UI (/_tracelite)    │   │    │
│  │  │   embedded dashboard         │   │    │
│  │  └──────────────────────────────┘   │    │
│  └─────────────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

**How it works:**

1. The HTTP middleware intercepts every request and response.
2. Request metadata, headers, bodies, and query parameters are extracted into a `RequestLog` dataclass.
3. The `RequestLog` is stored in a SQLite database via the `SQLiteStorage` backend.
4. The embedded dashboard reads from the same database and serves a web UI at `/_tracelite`.
5. The CLI reads from the same database for terminal-based inspection and export.

---

## Documentation

- [Product Requirements Document](./docs/PRD.md)
- [Development Roadmap](./ROADMAP.md)
- [Changelog](./CHANGELOG.md)

---

## Development

```bash
make install        # Install with all optional deps
make test           # pytest --cov
make format         # black + isort
make lint           # pre-commit run --all-files
make build          # python -m build
```

---

## Philosophy

TraceLite is the **SQLite of tracing**.

SQLite succeeded because it is minimal, embedded, and useful by default. It requires no server, no configuration, and no administration. You add it to your project and it works.

TraceLite applies the same philosophy to HTTP tracing. There is no agent to deploy, no collector to configure, no dashboard server to run. You add one line of code and your API becomes observable. The dashboard is embedded. The storage is embedded. Everything runs inside your application process.

Like Chrome DevTools gives frontend developers instant visibility into network traffic, TraceLite gives backend developers the same experience — without leaving their development environment.

Heavyweight features that require server infrastructure are explicitly out of scope. TraceLite is for developers, during development, on their local machine.

---

## License

MIT © Yeongseon Choe
