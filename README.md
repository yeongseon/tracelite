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
poetry install --with dev --extras "fastapi flask django"
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
config = load_config(app.config)
storage = SQLiteStorage(db_path=config.db_path)

app.wsgi_app = TraceliteMiddleware(app.wsgi_app, storage, config)
```

### FastAPI Integration
```python
from fastapi import FastAPI
from tracelite.middleware.fastapi import TraceliteMiddleware
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.core.config import load_config

app = FastAPI()
config = load_config()
storage = SQLiteStorage(db_path=config.db_path)

app.add_middleware(TraceliteMiddleware, storage=storage, config=config)
```

## Configuration (tracelite.toml)
```toml
[tracelite]
enabled = true

[storage]
type = "sqlite"
path = "tracelite.db"

[filter]
exclude_paths = ["/static", "/favicon.ico"]
mask_keys = ["password", "token"]
```

## Testing
```bash
pytest --cov=tracelite --cov-report=term --cov-report=html
```

---

MIT © Yeongseon Choe
