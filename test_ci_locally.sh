#!/bin/bash

# Test CI commands locally before pushing
set -e  # Exit on first error

echo "🧪 Testing CI commands locally..."
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILED_TESTS=""

# Function to run a test
run_test() {
    local name="$1"
    local cmd="$2"

    echo -e "\n${YELLOW}Testing: $name${NC}"
    echo "Command: $cmd"

    if eval "$cmd"; then
        echo -e "${GREEN}✓ $name passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $name failed${NC}"
        FAILED_TESTS="$FAILED_TESTS\n  - $name"
        return 1
    fi
}

echo -e "\n📋 Testing from main CI workflow..."
echo "------------------------------------"

# Test commands from ci.yml
run_test "Ruff" "poetry run ruff check src/ tests/" || true
run_test "Black" "poetry run black --check src/ tests/" || true
run_test "isort" "poetry run isort --check-only src/ tests/" || true
run_test "MyPy" "poetry run mypy src/" || true
run_test "Pytest" "poetry run pytest -m 'unit and not slow' --maxfail=5" || true

echo -e "\n📋 Testing from lint.yml workflow..."
echo "-------------------------------------"

# Install tools if needed
echo -e "\n${YELLOW}Installing additional tools...${NC}"
pip install bandit safety vulture flake8 yamllint unimport > /dev/null 2>&1

# Test the exact Bandit command from lint.yml
run_test "Bandit (exact lint.yml command)" "bandit -r src/ --skip B101,B104,B105,B311,B601 -x src/mcp_shared_lib/test_utils/ -ll" || true

# Test other lint.yml commands that commonly fail
run_test "Flake8" "flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503,E501" || true
run_test "Vulture" "vulture src/ tests/ --min-confidence 80 --exclude='*git_client.py'" || true
run_test "Safety" "safety check --json || echo 'Safety check completed'" || true

echo -e "\n${YELLOW}Testing YAML files...${NC}"
run_test "YAML Lint" "yamllint -d relaxed .github/workflows/*.yml" || true

# Summary
echo -e "\n================================"
if [ -z "$FAILED_TESTS" ]; then
    echo -e "${GREEN}✅ All tests passed! Safe to push.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed:${NC}$FAILED_TESTS"
    echo -e "\n${YELLOW}Fix these issues before pushing to avoid CI failures.${NC}"
    exit 1
fi
