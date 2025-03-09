.PHONY: setup test build install clean help

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

build: clean ## Build the package
	$(PYTHON) -m build

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

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

