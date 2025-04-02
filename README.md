# Tracelite

[![CI](https://github.com/yeongseon/tracelite/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/yeongseon/tracelite/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/tracelite.svg)](https://pypi.org/project/tracelite/)
[![Coverage Status](https://coveralls.io/repos/github/yeongseon/tracelite/badge.svg?branch=main)](https://coveralls.io/github/yeongseon/tracelite?branch=main)

---

**Lightweight HTTP request & response tracing for Flask, Django, and FastAPI.**  
Tracelite logs incoming HTTP requests and outgoing responses in a structured format.  
Ideal for local development and debugging.

---

## ✨ Features

- 🔍 Request & Response logging
- ⚙️ Configurable filtering & masking
- 📦 SQLite-based local storage
- 📊 CLI & Streamlit UI Viewer
- 🧩 Optional dependency support

---

## 🚀 Quick Start

### Installation

```bash
pip install tracelite
```

### Usage Example (FastAPI)

```python
from fastapi import FastAPI
from tracelite.middleware.fastapi import TraceliteMiddleware

app = FastAPI()
app.add_middleware(TraceliteMiddleware)
```

### CLI Viewer

```bash
tracelite view
```

---

## 🧩 Examples

Example projects are available in the examples/ folder:

- Flask Demo
- FastAPI Demo
- Django Demo


## 📄 Documentation

For full documentation, refer to the [`docs/`](./docs) folder:

- [Installation Guide](./docs/installation.md)
- [Usage Guide](./docs/usage.md)
- [Configuration Guide](./docs/configuration.md)
- [Development Guide](./docs/development.md)
- [Contributing](./docs/contributing.md)

---

## 📄 License

MIT © Yeongseon Choe