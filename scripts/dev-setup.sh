#!/bin/bash
# Development setup script for MCP Shared Library
# This script sets up the development environment and validates the installation

set -e

PROJECT_NAME="MCP Shared Library"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🚀 Setting up development environment for $PROJECT_NAME"
echo "📁 Project directory: $PROJECT_DIR"

cd "$PROJECT_DIR"

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first: https://python-poetry.org/docs/#installation"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git first"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo "🐍 Found Python $PYTHON_VERSION"

# Install dependencies
echo "📦 Installing dependencies..."
poetry install --with test,dev

# Install pre-commit hooks
echo "🔒 Setting up pre-commit hooks..."
poetry run pre-commit install

# Run initial validation
echo "🧪 Running initial validation..."

# Check code style
echo "  - Running code style checks..."
poetry run black --check src/ tests/ || {
    echo "⚠️  Code style issues found. Running black to fix..."
    poetry run black src/ tests/
}

# Check linting
echo "  - Running linter..."
poetry run ruff check src/ tests/

# Check type annotations
echo "  - Running type checker..."
poetry run mypy src/

# Run fast tests
echo "  - Running unit tests..."
poetry run pytest tests/ -m "unit and not slow" -v

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "📚 Common development commands:"
echo "  poetry run pytest tests/                    # Run all tests"
echo "  poetry run pytest -m 'unit and not slow'   # Run fast unit tests"
echo "  poetry run pre-commit run --all-files      # Run all code quality checks"
echo "  poetry run black src/ tests/               # Format code"
echo "  poetry run ruff check src/ tests/          # Lint code"
echo "  poetry run mypy src/                       # Type check"
echo ""
echo "🎯 Ready for development! Check CONTRIBUTING.md for detailed guidelines."