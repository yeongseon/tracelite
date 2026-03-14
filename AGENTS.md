# PROJECT KNOWLEDGE BASE

**Project:** TraceLite — DevTools for your backend APIs
**Stack:** Python 3.9+, Pydantic, SQLite, Typer/Rich CLI
**Vision:** The SQLite of tracing — zero-friction embedded HTTP inspection

## STRUCTURE

```
tracelite/
├── src/tracelite/
│   ├── __init__.py          # Public API: enable_tracing()
│   ├── core/
│   │   ├── models.py        # RequestLog dataclass
│   │   ├── config.py        # TraceliteConfig (pydantic) + load_config()
│   │   ├── filters.py       # should_exclude(), mask_sensitive(), mask_body()
│   │   ├── diff.py          # Response diff logic
│   │   ├── replay.py        # curl command generation
│   │   └── storage/
│   │       ├── base.py      # ILoggerStorage ABC
│   │       └── sqlite.py    # SQLiteStorage implementation
│   ├── middleware/
│   │   ├── fastapi.py       # ASGI middleware (Starlette BaseHTTPMiddleware)
│   │   ├── flask.py         # WSGI middleware
│   │   └── django.py        # Django MiddlewareMixin
│   ├── ui/
│   │   ├── dashboard.py     # Embedded web dashboard (/_tracelite)
│   │   └── viewer.py        # Streamlit viewer (legacy)
│   └── cli/
│       └── main.py          # Typer CLI: view, export, view_ui
├── examples/
│   ├── basic/               # Framework setup examples
│   ├── debugging/           # Debugging workflow examples
│   └── security/            # Masking examples
├── tests/                   # pytest suite
└── docs/                    # Documentation + PRD
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new capture field | `core/models.py` → `core/storage/sqlite.py` | Update dataclass + DB schema together |
| Add framework support | `middleware/` | Follow existing pattern: capture → RequestLog → storage.store() |
| Change config options | `core/config.py` + `tracelite.toml.sample` | Pydantic model + TOML mapping |
| Modify filtering/masking | `core/filters.py` | Pure functions, no side effects |
| Change dashboard UI | `ui/dashboard.py` | Embedded HTML, no external deps |
| Add CLI command | `cli/main.py` | Typer app, Rich tables |
| Add storage backend | `core/storage/` | Implement ILoggerStorage ABC |

## CONVENTIONS

- **Formatter:** black (line-length=88), isort (profile=black)
- **Type hints:** All public functions must have type annotations
- **Docstrings:** Google style with Args/Returns sections on middleware
- **Config:** Pydantic BaseModel for validation, TOML for file config
- **Storage:** ABC-first — always define interface in base.py before implementation
- **Middleware pattern:** capture start_time → call next → build RequestLog → storage.store(log)
- **Tests:** pytest, fixtures for app/client/storage, `:memory:` SQLite for test isolation

## ANTI-PATTERNS

- **Never** make framework deps (flask, fastapi, django) required — they must be optional
- **Never** suppress response body capture — PRD requires it for diff feature
- **Never** use `datetime.utcnow()` — deprecated in Python 3.12, use `datetime.now(timezone.utc)`
- **Never** skip masking on body content — headers AND bodies must be masked
- **Never** build SQL with f-strings without whitelist validation

## DEPENDENCY STRATEGY

```
pip install tracelite              # core only (pydantic, typer, rich, tomli)
pip install tracelite[fastapi]     # + starlette, fastapi, httpx
pip install tracelite[flask]       # + flask, werkzeug
pip install tracelite[django]      # + django
```

## COMMANDS

```bash
make install        # Install with all optional deps
make test           # pytest --cov
make format         # black + isort
make lint           # pre-commit run --all-files
make build          # python -m build
tracelite view      # CLI log viewer
tracelite export    # Export logs (json/csv)
```

## KEY DESIGN DECISIONS

1. **Embedded dashboard** (`/_tracelite`) served from the same app server — no external process
2. **SQLite default storage** — zero config, portable, embedded
3. **One-line setup:** `enable_tracing(app)` auto-detects framework
4. **Response body capture** is mandatory — enables diff feature
5. **Config hierarchy:** TOML file → app_config dict → defaults
