# Development Guide

## Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

## Pre-commit Hooks (Optional)

```bash
pre-commit install
pre-commit run --all-files
```

## Common Commands

| Command             | Description                           |
|---------------------|---------------------------------------|
| `make install`      | Install dependencies                  |
| `make test`         | Run tests with coverage report        |
| `make lint`         | Run code linting                     |
| `make build`        | Build package                         |
| `make release-*`    | Bump version & release (patch/minor/major) |


## Running Tests
To run all tests:

```bash
make test
```
If you want to see skipped tests (e.g., Streamlit viewer test when Streamlit is not installed):

```bash
pytest -rs
```


## Running Demo Apps

```bash
cd examples/flask_demo
python app.py

cd examples/fastapi_demo
uvicorn main:app --reload

cd examples/django_demo
python manage.py runserver
```