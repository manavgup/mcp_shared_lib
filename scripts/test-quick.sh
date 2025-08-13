#!/bin/bash
# Quick test script for MCP Shared Library
# Runs fast tests for development cycle

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "⚡ Running quick tests for MCP Shared Library..."

# Run pre-commit checks
echo "🔒 Running pre-commit checks..."
poetry run pre-commit run --all-files

# Run fast unit tests
echo "🧪 Running fast unit tests..."
poetry run pytest tests/ -m "unit and not slow" -v --tb=short

# Check test coverage for core modules
echo "📊 Checking test coverage..."
poetry run pytest tests/ -m "unit and not slow" --cov=src/mcp_shared_lib --cov-report=term-missing --cov-fail-under=80

echo ""
echo "✅ Quick tests passed! Ready for development."
echo ""
echo "💡 To run full test suite: poetry run pytest tests/"
echo "💡 To run integration tests: poetry run pytest tests/ -m integration"
