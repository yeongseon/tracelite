# TraceLite — Product Requirements Document

> **TraceLite — DevTools for your backend APIs**
>
> *The SQLite of tracing*

---

## 1. Overview

TraceLite is a lightweight HTTP tracing and inspection tool for backend APIs.

Its goal is to become the **SQLite of tracing**: a minimal, zero-friction tool that developers can use locally to inspect API behavior without setting up heavy observability stacks.

TraceLite focuses on developer productivity during local development by providing a **DevTools-like experience for backend APIs**.

Instead of configuring complex tracing systems such as OpenTelemetry, Jaeger, or APM platforms, developers can quickly install TraceLite and immediately inspect incoming requests, responses, and behavior.

---

## 2. Vision

**Make backend debugging as easy as browser DevTools.**

Just like Chrome DevTools allows developers to inspect frontend network traffic, TraceLite provides a similar experience for backend APIs.

### Long-Term Positioning

| Analogy | Domain |
|---|---|
| SQLite | Databases |
| **TraceLite** | **Tracing** |

Core qualities:

- Minimal setup
- Lightweight
- Embedded
- Developer-friendly
- Useful by default

---

## 3. Problem Statement

Debugging backend APIs during development often requires multiple tools:

- Application logs
- Request logging middleware
- curl / Postman testing
- APM tools
- Distributed tracing systems

These solutions suffer from:

- High setup cost
- Too much configuration
- Lack of real-time inspection
- Fragmented debugging workflow
- Heavy infrastructure requirements

For small services and local development, these tools are often overkill.

Developers frequently resort to:

- `print()`
- `logging.debug()`
- Manual curl testing

This slows down development and makes debugging inconsistent.

---

## 4. Goals

### Primary Goals

- Provide instant visibility into HTTP traffic
- Enable fast debugging during development
- Require near-zero setup
- Provide visual inspection of requests and responses

### Success Metric

> A developer installs TraceLite and inspects requests **within 60 seconds**.

---

## 5. Non-Goals

TraceLite is **not** intended to replace:

- OpenTelemetry
- Datadog
- Jaeger / Zipkin
- Distributed tracing systems
- Production observability platforms

TraceLite focuses on:

- Local development
- Debugging
- Lightweight inspection

---

## 6. Target Users

### Primary Users

- Python backend developers
- API developers
- FastAPI / Flask / Django developers

### Typical Scenarios

- Debugging API responses
- Investigating regressions
- Comparing API responses
- Inspecting request payloads
- Verifying headers and authentication behavior

---

## 7. Key Principles

### Zero Friction

Developers should be able to start using TraceLite in seconds.

```python
from tracelite import enable_tracing
enable_tracing(app)
```

Then open:

```
http://localhost:8000/_tracelite
```

### Embedded UI

No external servers. The inspection dashboard is served **inside the same application server**.

Path: `/_tracelite`

### Lightweight Storage

Default storage backend: **SQLite**

- Zero configuration
- Embedded
- Fast
- Portable

### Developer Experience First

Focus on clarity, speed, and usefulness. Avoid complex configuration whenever possible.

---

## 8. Core Features (MVP)

### 8.1 Request Capture

TraceLite captures:

| Field | Description |
|---|---|
| HTTP method | GET, POST, PUT, DELETE, etc. |
| URL | Full request path |
| Headers | Request and response headers |
| Query parameters | Parsed separately from path |
| Request body | Decoded request payload |
| Response body | Captured response content |
| Status code | HTTP response status |
| Response time | Duration in milliseconds |

Example record:

```
POST /api/login
Status: 200
Duration: 34ms
```

### 8.2 Web Dashboard

Accessible at: `/_tracelite`

Features:

- Recent request list
- Search and filtering
- Request detail view
- Response inspection

Example:

```
Recent Requests
───────────────
GET  /users     200  12ms
POST /login     200  34ms
GET  /orders    200  89ms
```

### 8.3 Request Detail View

Displays:

- Headers (request + response)
- Query parameters
- Request body
- Response body
- Status code
- Duration

### 8.4 Response Diff

Compare responses from the same endpoint.

**Use case:** "Why did this API change behavior?"

Example:

```diff
Previous response:
  { "status": "active" }

Current response:
  { "status": "inactive" }

Diff:
- status: active
+ status: inactive
```

### 8.5 Sensitive Data Masking

Sensitive fields are automatically masked.

Default masked fields:

- `password`
- `token`
- `authorization`
- `secret`

Masking applies to:

- Request headers
- Response headers
- Request body
- Response body

Example output:

```
password: *****
authorization: *****
```

---

## 9. Additional Features (Phase 2)

### 9.1 SQL Query Capture

Capture SQL queries executed during a request.

```
SELECT * FROM users WHERE id=123
Duration: 12ms
```

Supported libraries:

- SQLAlchemy
- psycopg
- Django ORM

### 9.2 Slow Request Highlight

Automatically highlight slow requests in the dashboard.

```
⚠ GET /orders — 1.8s
```

### 9.3 Request Replay

Generate a curl command from any captured request.

```bash
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice"}'
```

---

## 10. Framework Support

### Initial Support

| Framework | Integration Type |
|---|---|
| FastAPI | ASGI middleware |
| Flask | WSGI middleware |
| Django | Django middleware |

### Dependency Strategy

Framework dependencies must be **optional**:

```bash
pip install tracelite              # core only
pip install tracelite[fastapi]     # with FastAPI support
pip install tracelite[flask]       # with Flask support
pip install tracelite[django]      # with Django support
```

---

## 11. Architecture

### Core Components

```
┌─────────────────────────────────────────────┐
│                  User App                    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │        Capture Layer                │    │
│  │   (HTTP middleware per framework)    │    │
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

---

## 12. Data Model

### Trace Record

| Field | Type | Description |
|---|---|---|
| id | integer | Auto-incrementing primary key |
| timestamp | datetime | Request timestamp |
| method | string | HTTP method |
| path | string | Request path |
| query | string | Query parameters (parsed) |
| headers | json | Request headers |
| request_body | text | Request payload |
| response_headers | json | Response headers |
| response_body | text | Response payload |
| status_code | integer | HTTP status code |
| duration_ms | float | Request duration in milliseconds |
| client_ip | string | Client IP address |
| user_agent | string | User-Agent header |

---

## 13. Storage Strategy

### Default

SQLite — zero configuration, embedded, portable.

### Future (optional)

- PostgreSQL
- Redis
- File-based logs

---

## 14. Security Considerations

### Sensitive Data Handling

- Automatic masking for configurable field names
- Masking applies to headers **and** bodies
- Optional: disable body capture entirely

Example configuration:

```toml
[filter]
mask_keys = ["password", "token", "authorization", "secret"]

[capture]
capture_body = false
```

---

## 15. Future Vision

Possible long-term expansions:

- OpenTelemetry export
- Distributed tracing compatibility
- API regression detection
- Request replay testing
- Dependency tracing

Core philosophy remains:

- Lightweight
- Minimal
- Developer-first

---

## 16. Success Metrics

### Quantitative

- GitHub stars
- pip downloads
- Developer adoption

### Qualitative

> Developers adopt TraceLite as their default API debugging tool during local development.

---

## 17. Tagline

> **TraceLite — DevTools for your backend APIs**

Alternative:

> *The SQLite of tracing*

---

---

# Part 2: Examples Strategy

## 18. Overview

TraceLite aims to become the SQLite of tracing, which means the project must provide **extensive examples and practical usage patterns**.

Examples play a critical role in:

- Developer adoption
- Discoverability
- Real-world usability
- SEO and documentation reach

TraceLite will prioritize a large collection of practical examples across frameworks, use cases, and debugging scenarios.

---

## 19. Example Design Principles

Examples must be:

- **Minimal** — shortest code that demonstrates the concept
- **Copy-paste friendly** — works out of the box
- **Runnable** — includes all necessary setup
- **Focused on real debugging scenarios** — not synthetic demos

Each example should demonstrate a specific debugging workflow.

Examples should answer questions like:

- "Why is my API returning different responses?"
- "Why is this request slow?"
- "What headers are being sent?"
- "What SQL queries happened during this request?"

---

## 20. Example Categories

### 20.1 Basic Setup Examples

Simple integrations for supported frameworks.

| Example | Description |
|---|---|
| `fastapi_app.py` | FastAPI basic tracing |
| `flask_app.py` | Flask basic tracing |
| `django_project/` | Django basic tracing |

Directory:

```
examples/basic/
    fastapi_app.py
    flask_app.py
    django_project/
```

### 20.2 Debugging Examples

Common debugging workflows.

| Example | Description |
|---|---|
| `response_diff.py` | Comparing API response changes |
| `auth_headers.py` | Debugging authentication headers |
| `payload_inspection.py` | Inspecting request payloads |

Directory:

```
examples/debugging/
    response_diff.py
    auth_headers.py
    payload_inspection.py
```

### 20.3 Performance Examples

Performance debugging workflows.

| Example | Description |
|---|---|
| `slow_requests.py` | Slow endpoint detection |
| `sqlalchemy_queries.py` | SQL query tracing |

Directory:

```
examples/performance/
    slow_requests.py
    sqlalchemy_queries.py
```

### 20.4 Security Examples

Safe tracing patterns.

| Example | Description |
|---|---|
| `masking_example.py` | Masking passwords, tokens, secrets |

Directory:

```
examples/security/
    masking_example.py
```

### 20.5 Testing Examples

TraceLite-assisted testing workflows.

| Example | Description |
|---|---|
| `pytest_debug.py` | Debugging failing tests |

Directory:

```
examples/testing/
    pytest_debug.py
```

---

## 21. Documentation Integration

Examples will be embedded in:

- `README.md`
- Official documentation (`docs/`)
- Blog tutorials
- Community articles

Every major feature should have **at least one runnable example**.

---

## 22. Long-Term Example Structure

Over time, the examples collection should grow into a comprehensive cookbook:

```
examples/
    basic/
        fastapi_app.py
        flask_app.py
        django_project/
    debugging/
        response_diff.py
        auth_headers.py
        payload_inspection.py
    performance/
        slow_requests.py
        sqlalchemy_queries.py
    security/
        masking_example.py
    testing/
        pytest_debug.py
```

This collection serves as:

- Documentation
- Tutorials
- Debugging recipes
- Developer onboarding

---

## 23. Success Criteria

The examples library should allow developers to:

- **Understand** TraceLite within 5 minutes
- **Integrate** tracing within 10 lines of code
- **Debug** common issues without reading full documentation
