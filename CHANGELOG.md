# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.4] - 2025-03-29

### ✨ Added
- FastAPI demo app in `examples/fastapi_demo`
- Django demo app in `examples/django_demo`


---

## [0.2.3] - 2025-03-28

### ✨ Added
- Flask demo app in `examples/flask_demo`
- Streamlit log viewer CLI command (`tracelite view-ui`)

### 🐞 Fixed
- CLI log row unpacking bug (incorrect unpacking of log rows)

---

## [0.2.2] - 2025-03-27

### 🧹 Changed
- Code style and import order applied via Black & isort
- Added pytest coverage configuration

---

## [0.2.0] - 2025-03-27

### ✨ Added
- Django Middleware support
- FastAPI Middleware support
- CLI log viewer (`tracelite view` command)
- Initial Streamlit viewer scaffold

---

## [0.1.0] - 2025-03-26

### 🚀 Initial Release
- Flask Middleware support
- Request & Response tracing
- SQLite-based log storage
- Configurable filtering and masking
- Basic CLI commands
