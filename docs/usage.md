# Usage

Tracelite can be used in multiple ways:

---

## 1. CLI Viewer

You can view and export logs directly from the command line.

### View Recent Logs

```bash
tracelite view
```

### Export Options

You can export logs to JSON, CSV, or Table formats:

```bash
tracelite export --format json
tracelite export --format csv
```

### Filter Options

You can filter logs by any field:

```bash
tracelite view --filter "status=500"
tracelite view --filter "method=POST" --filter "status=200"
```
Supports exact match only.

## 2. Middleware Integration

### Flask Example

```python
from flask import Flask
from tracelite.middleware.flask import TraceliteMiddleware

app = Flask()
app.wsgi_app = TraceliteMiddleware(app.wsgi_app)
```

### FastAPI Example

```python
from fastapi import FastAPI
from tracelite.middleware.fastapi import TraceliteMiddleware

app = FastAPI()
app.add_middleware(TraceliteMiddleware)
```

### Django Example

```python
MIDDLEWARE = [
    # ... other middleware ...
    "tracelite.middleware.django.TraceliteMiddleware",
]
```

## 3. Streamlit Viewer

If Streamlit is installed:

```bash
tracelite view --ui
```

**Note:** Streamlit viewer is optional.