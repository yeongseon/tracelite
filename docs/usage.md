# Usage

TraceLite can be used in multiple ways:

---

## 1. One-Line Setup (Recommended)

The easiest way to get started is with `enable_tracing()`:

```python
from tracelite import enable_tracing

app = FastAPI()  # or Flask(__name__) or Django WSGI app
enable_tracing(app)
```

Then open `http://localhost:8000/_tracelite` to see the dashboard.

---

## 2. CLI Viewer

You can view and export logs directly from the command line.

### View Recent Logs

```bash
tracelite view
```

### Export Options

You can export logs to JSON or CSV formats:

```bash
tracelite export --format json
tracelite export --format csv
```

### Column Selection

You can select specific columns to display:

```bash
tracelite view --columns method,path,status_code
```

---

## 3. Middleware Integration

### FastAPI Example

```python
from fastapi import FastAPI
from tracelite.middleware.fastapi import TraceliteMiddleware
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.core.config import load_config

app = FastAPI()
app.add_middleware(TraceliteMiddleware, storage=SQLiteStorage(), config=load_config())
```

### Flask Example

```python
from flask import Flask
from tracelite.middleware.flask import TraceliteMiddleware
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.core.config import load_config

app = Flask(__name__)
app.wsgi_app = TraceliteMiddleware(app.wsgi_app, SQLiteStorage(), load_config())
```

### Django Example

```python
from tracelite import enable_tracing

# In your Django WSGI application
enable_tracing(application)
```
