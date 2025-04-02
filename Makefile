VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
CHANGELOG=CHANGELOG.md
VERSION=$(shell grep '^version =' pyproject.toml | sed -E 's/version = "(.*)"/\1/')

.PHONY: help venv install format lint test clean build precommit publish changelog bump-version-patch bump-version-minor bump-version-major release-patch release-minor release-major commit init-config

help:
	@echo "Makefile commands:"
	@echo "  make venv              - Create virtualenv"
	@echo "  make install           - Install dependencies"
	@echo "  make format            - Run black & isort"
	@echo "  make lint              - Run pre-commit"
	@echo "  make test              - Run tests"
	@echo "  make build             - Build package"
	@echo "  make clean             - Remove build artifacts"
	@echo "  make precommit         - Install pre-commit hooks"
	@echo "  make publish           - Publish to PyPI"
	@echo "  make changelog         - Generate CHANGELOG.md"
	@echo "  make release-patch     - Create a patch release"
	@echo "  make release-minor     - Create a minor release"
	@echo "  make release-major     - Create a major release"
	@echo "  make commit m='msg'    - Add, commit, and push changes"
	@echo "  make init-config       - Copy sample config to tracelite.toml"

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev,fastapi,flask,django,streamlit]"
	$(PIP) install build twine
	$(PIP) install git-changelog toml

format:
	$(VENV)/bin/black src tests examples
	$(VENV)/bin/isort src tests examples

lint:
	$(VENV)/bin/pre-commit run --all-files

test:
	$(VENV)/bin/pytest --cov=src --cov-report=term --cov-report=html

build:
	$(PYTHON) -m build

clean:
	rm -rf dist build *.egg-info .pytest_cache .coverage htmlcov

precommit:
	$(VENV)/bin/pre-commit install

publish: build
	$(VENV)/bin/twine upload dist/*

commit:
	git add .
	git commit -m "$(m)"
	git push origin main

changelog:
	$(VENV)/bin/git-changelog --output $(CHANGELOG) --template angular

bump-version-patch:
	$(PYTHON) scripts/bump_version.py patch

bump-version-minor:
	$(PYTHON) scripts/bump_version.py minor

bump-version-major:
	$(PYTHON) scripts/bump_version.py major

release-patch: changelog bump-version-patch
	git add pyproject.toml $(CHANGELOG)
	git commit -m "chore: release v$(VERSION)"
	git tag v$(VERSION)
	git push origin main
	git push --tags

release-minor: changelog bump-version-minor
	git add pyproject.toml $(CHANGELOG)
	git commit -m "chore: release v$(VERSION)"
	git tag v$(VERSION)
	git push origin main
	git push --tags

release-major: changelog bump-version-major
	git add pyproject.toml $(CHANGELOG)
	git commit -m "chore:

init-config:
	cp tracelite.toml.sample tracelite.toml
