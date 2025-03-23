.PHONY: setup test build check install clean help typecheck metrics

# Define Python and pip executables
PYTHON := python3
PIP := pip3
PKG_NAME := ptodo


# Default target
.DEFAULT_GOAL := help

setup: ## Install development dependencies
	$(PIP) install -e ".[dev]"
	$(PIP) install -e ".[test]"

test: ## Run tests with pytest
	pytest

coverage: ## Run tests with coverage report
	pytest --cov=$(PKG_NAME) --cov-report=term-missing --cov-report=xml

lint: ## Run linting checks
	flake8 $(PKG_NAME) tests
	isort --check-only --profile black $(PKG_NAME) tests
	black --check $(PKG_NAME) tests

format: ## Format code using black and isort
	isort --profile black $(PKG_NAME) tests
	black $(PKG_NAME) tests

typecheck: ## Run type checking with mypy
	mypy $(PKG_NAME) tests

build: clean ## Build the package
	$(PYTHON) -m build

check: ## Run linting, type checking, metrics, and tests to verify code quality
	$(PYTHON) checks/version_check.py
	$(MAKE) test
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) metrics

install: build ## Install the package
	$(PIP) install .

uninstall: ## Uninstall the package
	$(PIP) uninstall -y $(PKG_NAME)

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

metrics: ## Run code metrics (complexity and maintainability) using radon
	radon cc $(PKG_NAME) tests
	radon mi $(PKG_NAME) tests

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'


