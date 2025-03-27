# Tracelite

[![PyPI version](https://img.shields.io/pypi/v/tracelite)](https://pypi.org/project/tracelite/)
[![Test](https://github.com/yeongseon/tracelite/actions/workflows/test.yml/badge.svg)](https://github.com/yeongseon/tracelite/actions/workflows/test.yml)

**Lightweight request & response tracing for your Flask, Django, or FastAPI dev server**

Tracelite logs incoming HTTP requests and outgoing responses in a structured format. It's ideal for local development and debugging.

## Features
- 🔍 Logs method, path, status, duration, client IP, headers, body
- ⚙️ Configurable masking and path exclusion (via `tracelite.toml`)
- 📦 SQLite-based local storage
- 📊 Pretty CLI output using `rich`

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

### Django Integration

In your Django `settings.py`, add:

```python
# settings.py
from tracelite.core.config import load_config
from tracelite.core.storage.sqlite import SQLiteStorage

TRACELITE_CONFIG = load_config()
TRACELITE_STORAGE = SQLiteStorage(db_path=TRACELITE_CONFIG.db_path)

MIDDLEWARE = [
    # ... other middleware ...
    "tracelite.middleware.django.TraceliteMiddleware",
]
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

## Development Setup

```bash
# Install Poetry if not installed
curl -sSL https://install.python-poetry.org | python3 -

# Clone the repository
git clone https://github.com/yeongseon/tracelite.git
cd tracelite

# Set Python version (e.g. 3.9)
poetry env use python3.9

# Install dependencies with all extras
touch pyproject.toml  # trigger poetry env rebuild if needed
poetry install --with dev

# Activate virtual environment
source $(poetry env info --path)/bin/activate
```

## Testing
```bash
pytest --cov=tracelite --cov-report=term --cov-report=html
```

---

MIT © Yeongseon Choe