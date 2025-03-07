.PHONY: setup clean install dev-install test build publish

# Default Python interpreter
PYTHON = python
# Path to uv
UV = uv
# Path to the main package
PACKAGE = eikon_api_wrapper

# Create and set up virtual environment
setup:
	$(UV) venv .venv
	$(UV) pip install --requirement pyproject.toml

# Install the package in development mode
install:
	$(UV) pip install -e .

# Install dev dependencies
dev-install:
	$(UV) pip install --extras dev -e .

# Clean build artifacts and cache files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf $(PACKAGE).egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run tests
test:
	$(PYTHON) -m pytest

# Build package distribution
build: clean
	$(UV) build

# Publish package to PyPI
publish: build
	$(PYTHON) -m twine upload dist/*

# Install all dependencies (including dev)
all: setup dev-install

# Update dependencies
update:
	$(UV) pip install --upgrade --requirement pyproject.toml
	$(UV) pip install --extras dev --upgrade -e .

upgrade-dev:
	@echo "Upgrading dev dependencies in root package..."
	$(UV) sync --upgrade --extra dev
