# README.md
# Tracelite

**Lightweight request & response tracing for your Flask, Django, or FastAPI dev server**

Tracelite logs incoming HTTP requests and outgoing responses in a structured format. It's ideal for local development and debugging.

## Features
- 🔍 Logs method, path, status, duration, client IP, headers, body
- ⚙️ Configurable masking and path exclusion (via `tracelite.toml`)
- 📦 SQLite-based local storage
- 📊 Pretty CLI output using `rich`

## Installation
```bash
pip install tracelite[flask]
```

## Usage
### CLI
```bash
tracelite view
tracelite export --format json
```

### Flask Integration
```python
from flask import Flask
from tracelite.middleware.flask import TraceliteMiddleware
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.core.config import load_config

app = Flask(__name__)
config = load_config()
storage = SQLiteStorage(db_path=config.db_path)

app.wsgi_app = TraceliteMiddleware(app.wsgi_app, storage, config)
```

## Configuration (tracelite.toml)
```toml
[storage]
type = "sqlite"
path = "tracelite.db"

[filter]
exclude_paths = ["/static", "/favicon.ico"]
mask_keys = ["password", "token"]
```

## Testing
```bash
poetry install --with dev
pytest
```

## Coverage Report
```bash
open htmlcov/index.html
```

## Requirementsgit add .
git commit -m "release: v0.1.0"
git push origin main
git tag v0.1.0
git push origin v0.1.0

- Python 3.9+
- Flask 3.x

---

MIT © Yeongseon Choe
