# Makefile for MCP Shared Library
# Development automation for the foundation library

.PHONY: help install test test-fast test-coverage lint format type-check quality-check clean dev-setup serve docs

# Default target
help: ## Show this help message
	@echo "MCP Shared Library - Development Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup and Installation
install: ## Install all dependencies
	poetry install --with test,dev

dev-setup: ## Set up development environment
	@if [ -f scripts/dev-setup.sh ]; then \
		./scripts/dev-setup.sh; \
	else \
		echo "Running inline dev setup..."; \
		poetry install --with test,dev; \
		poetry run pre-commit install; \
		poetry run pytest tests/ -m "unit and not slow" -v; \
		echo "✅ Development environment ready!"; \
	fi

# Testing
test: ## Run all tests
	poetry run pytest tests/ -v

test-fast: ## Run fast unit tests only
	@if [ -f scripts/test-quick.sh ]; then \
		./scripts/test-quick.sh; \
	else \
		poetry run pytest tests/ -m "unit and not slow" -v; \
	fi

test-unit: ## Run unit tests
	poetry run pytest tests/ -m "unit" -v

test-integration: ## Run integration tests
	poetry run pytest tests/ -m "integration" -v

test-slow: ## Run slow tests
	poetry run pytest tests/ -m "slow" -v

test-coverage: ## Run tests with coverage report
	poetry run pytest tests/ --cov=src/mcp_shared_lib --cov-report=html --cov-report=term-missing --cov-report=xml

# Code Quality
lint: ## Run linter
	poetry run ruff check src/ tests/

format: ## Format code
	poetry run black src/ tests/
	poetry run ruff check src/ tests/ --fix

type-check: ## Run type checker
	poetry run mypy src/

pre-commit: ## Run pre-commit checks
	poetry run pre-commit run --all-files

quality-check: pre-commit type-check ## Run all quality checks

# Maintenance
clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Documentation
docs: ## Generate documentation
	@echo "📚 Documentation located in:"
	@echo "  - README.md: Project overview and setup"
	@echo "  - CONTRIBUTING.md: Development guidelines"
	@echo "  - TRANSPORT_GUIDE.md: Transport configuration"
	@echo "  - docs/: Additional documentation"

# Build and Distribution
build: clean ## Build package
	poetry build

# Development server (if applicable)
serve: ## Information about running services
	@echo "ℹ️  MCP Shared Library is a foundation library."
	@echo "   To run MCP servers, use the analyzer or recommender projects:"
	@echo "   - cd ../mcp_local_repo_analyzer && make serve"
	@echo "   - cd ../mcp_pr_recommender && make serve"
	@echo "   - cd ../mcp_auto_pr && make serve-all"

# Update dependencies
update-deps: ## Update all dependencies
	poetry update

# Git helpers
git-clean: ## Clean git working directory
	git clean -fd
	git reset --hard HEAD

# CI/CD helpers
ci-test: ## Run tests as in CI
	poetry run pytest tests/ --cov=src/mcp_shared_lib --cov-report=xml --junitxml=pytest.xml

# Debug and troubleshooting
debug-env: ## Show environment information
	@echo "🔍 Environment Information"
	@echo "========================"
	@echo "Python version: $$(python3 --version)"
	@echo "Poetry version: $$(poetry --version)"
	@echo "Project path: $$(pwd)"
	@echo "Virtual env: $$(poetry env info --path)"
	@echo ""
	@echo "📦 Installed packages:"
	@poetry show --tree

# Validation
validate: quality-check test-fast ## Run validation checks (quality + fast tests)