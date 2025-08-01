"""
Shared test fixtures and utilities for the MCP ecosystem.

This module provides common fixtures and utilities that can be used across
all MCP projects (shared_lib, local_repo_analyzer, pr_recommender).
"""

import json
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Union
from unittest.mock import Mock

import pytest

try:
    from git import GitCommandError, Repo

    HAS_GIT = True
except ImportError:
    HAS_GIT = False

# Configuration for pytest plugins
pytest_plugins = []


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def shared_temp_dir():
    """Temporary directory for test session."""
    temp_dir = Path(tempfile.mkdtemp(prefix="mcp_tests_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_dir(shared_temp_dir):
    """Individual temporary directory for each test."""
    test_dir = shared_temp_dir / f"test_{uuid.uuid4().hex[:8]}"
    test_dir.mkdir(parents=True, exist_ok=True)
    yield test_dir
    # Cleanup handled by shared_temp_dir


@pytest.fixture
def mock_git_repo():
    """Mock git repository data with common structure."""
    return {
        "modified_files": ["src/main.py", "tests/test_main.py", "README.md"],
        "untracked_files": ["new_feature.py", "temp_file.tmp"],
        "staged_files": ["docs/api.md", "config/settings.json"],
        "commits": [
            {
                "hash": "abc123def456",
                "message": "feat: add new feature for user authentication",
                "author": "John Doe",
                "email": "john@example.com",
                "timestamp": datetime.now() - timedelta(hours=2),
                "files_changed": ["src/auth.py", "tests/test_auth.py"],
            },
            {
                "hash": "def456ghi789",
                "message": "fix: resolve memory leak in data processing",
                "author": "Jane Smith",
                "email": "jane@example.com",
                "timestamp": datetime.now() - timedelta(hours=6),
                "files_changed": ["src/processor.py"],
            },
            {
                "hash": "ghi789jkl012",
                "message": "docs: update installation instructions",
                "author": "Bob Wilson",
                "email": "bob@example.com",
                "timestamp": datetime.now() - timedelta(days=1),
                "files_changed": ["README.md", "docs/install.md"],
            },
        ],
        "branches": {
            "current": "feature/auth-improvements",
            "all": [
                "main",
                "develop",
                "feature/auth-improvements",
                "hotfix/security-patch",
            ],
        },
        "remote_url": "https://github.com/example/test-repo.git",
        "stashes": [
            {"message": "WIP: experimental changes", "files": ["src/experimental.py"]}
        ],
    }


@pytest.fixture
def sample_config():
    """Sample configuration for testing MCP components."""
    return {
        "git": {
            "default_branch": "main",
            "ignore_patterns": ["*.log", "*.tmp", "node_modules/", ".env"],
            "max_file_size_mb": 10,
            "excluded_extensions": [".bin", ".exe", ".dll"],
        },
        "analysis": {
            "max_file_size": 1000000,
            "risk_threshold": 0.8,
            "complexity_threshold": 10,
            "line_count_threshold": 500,
        },
        "mcp": {
            "server_name": "test-server",
            "version": "1.0.0",
            "timeout": 30,
            "max_tools": 50,
        },
        "pr_recommendation": {
            "max_files_per_pr": 15,
            "similarity_threshold": 0.7,
            "min_pr_size": 3,
            "max_pr_size": 20,
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    }


@pytest.fixture
def sample_file_changes():
    """Sample file changes for testing analysis and recommendation logic."""
    return [
        {
            "file_path": "src/models/user.py",
            "change_type": "modified",
            "lines_added": 15,
            "lines_removed": 3,
            "risk_score": 0.4,
            "complexity_change": 2,
            "test_coverage": 0.85,
        },
        {
            "file_path": "src/models/auth.py",
            "change_type": "added",
            "lines_added": 120,
            "lines_removed": 0,
            "risk_score": 0.7,
            "complexity_change": 8,
            "test_coverage": 0.0,
        },
        {
            "file_path": "tests/test_user.py",
            "change_type": "modified",
            "lines_added": 25,
            "lines_removed": 5,
            "risk_score": 0.2,
            "complexity_change": 1,
            "test_coverage": 1.0,
        },
        {
            "file_path": "tests/test_auth.py",
            "change_type": "added",
            "lines_added": 80,
            "lines_removed": 0,
            "risk_score": 0.1,
            "complexity_change": 3,
            "test_coverage": 1.0,
        },
        {
            "file_path": "docs/authentication.md",
            "change_type": "added",
            "lines_added": 45,
            "lines_removed": 0,
            "risk_score": 0.0,
            "complexity_change": 0,
            "test_coverage": None,
        },
        {
            "file_path": "config/database.json",
            "change_type": "modified",
            "lines_added": 2,
            "lines_removed": 1,
            "risk_score": 0.9,
            "complexity_change": 0,
            "test_coverage": None,
        },
    ]


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for testing."""
    server = Mock()
    server.name = "test-mcp-server"
    server.version = "1.0.0"
    server.tools = [
        {
            "name": "analyze_changes",
            "description": "Analyze git repository changes",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                    "include_untracked": {"type": "boolean", "default": False},
                },
            },
        },
        {
            "name": "recommend_prs",
            "description": "Recommend PR groupings",
            "parameters": {
                "type": "object",
                "properties": {
                    "changes": {"type": "array"},
                    "max_prs": {"type": "integer", "default": 5},
                },
            },
        },
    ]

    # Mock tool execution
    def mock_execute_tool(tool_name: str, params: dict[str, Any]):
        if tool_name == "analyze_changes":
            return {
                "status": "success",
                "data": {
                    "modified_files": ["src/main.py"],
                    "untracked_files": ["new_file.py"],
                    "risk_assessment": 0.5,
                },
            }
        elif tool_name == "recommend_prs":
            return {
                "status": "success",
                "data": {
                    "recommendations": [
                        {
                            "title": "Add authentication features",
                            "files": ["src/auth.py", "tests/test_auth.py"],
                            "description": "New authentication system",
                        }
                    ]
                },
            }
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    server.execute_tool = Mock(side_effect=mock_execute_tool)
    return server


@pytest.fixture
def sample_analysis_result():
    """Sample analysis result for testing."""
    return {
        "timestamp": datetime.now(),
        "status": "success",
        "summary": "Repository analysis completed successfully",
        "details": {
            "total_files_changed": 6,
            "lines_added": 287,
            "lines_removed": 9,
            "average_risk_score": 0.42,
            "high_risk_files": ["config/database.json", "src/models/auth.py"],
            "test_coverage": 0.68,
            "recommendation": "Consider splitting changes into multiple PRs",
        },
        "risk_assessment": {
            "overall_risk": 0.6,
            "factors": {
                "large_files": True,
                "config_changes": True,
                "new_features": True,
                "missing_tests": False,
            },
        },
        "file_groups": [
            {
                "group_id": "auth_features",
                "files": [
                    "src/models/auth.py",
                    "tests/test_auth.py",
                    "docs/authentication.md",
                ],
                "description": "Authentication feature implementation",
                "risk_score": 0.4,
            },
            {
                "group_id": "user_updates",
                "files": ["src/models/user.py", "tests/test_user.py"],
                "description": "User model updates",
                "risk_score": 0.3,
            },
            {
                "group_id": "config_changes",
                "files": ["config/database.json"],
                "description": "Configuration updates",
                "risk_score": 0.9,
            },
        ],
    }


@pytest.fixture
def mock_fastmcp_server():
    """Mock FastMCP server instance for testing."""
    from unittest.mock import AsyncMock

    server = Mock()
    server.name = "TestAnalyzer"
    server.version = "1.0.0"
    server.tools = {}

    # Mock async methods
    server.start = AsyncMock()
    server.stop = AsyncMock()
    server.list_tools = AsyncMock(return_value=[])
    server.call_tool = AsyncMock()

    # Mock tool registration
    def mock_tool_decorator(func):
        tool_name = func.__name__
        server.tools[tool_name] = {
            "function": func,
            "name": tool_name,
            "description": getattr(func, "__doc__", ""),
        }
        return func

    server.tool = mock_tool_decorator
    return server


@pytest.fixture
def create_test_files():
    """Factory fixture for creating test files in a directory."""

    def _create_files(base_dir: Path, file_structure: dict[str, Union[str, dict]]):
        """
        Create files and directories based on a nested dictionary structure.

        Args:
            base_dir: Base directory to create files in
            file_structure: Dict where keys are file/dir names and values are:
                - str: file content
                - dict: subdirectory structure
        """
        for name, content in file_structure.items():
            path = base_dir / name

            if isinstance(content, dict):
                # Create subdirectory and recurse
                path.mkdir(parents=True, exist_ok=True)
                _create_files(path, content)
            else:
                # Create file with content
                path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(content, str):
                    path.write_text(content)
                else:
                    # Handle binary content if needed
                    path.write_bytes(content)

    return _create_files


@pytest.fixture
def sample_project_structure():
    """Sample project structure for testing."""
    return {
        "src": {
            "main.py": "#!/usr/bin/env python3\nprint('Hello, World!')\n",
            "models": {
                "__init__.py": "",
                "user.py": "class User:\n    def __init__(self, name):\n        self.name = name\n",
                "auth.py": "def authenticate(user, password):\n    return True\n",
            },
            "utils": {
                "__init__.py": "",
                "helpers.py": "def format_name(name):\n    return name.title()\n",
            },
        },
        "tests": {
            "__init__.py": "",
            "test_main.py": "def test_main():\n    assert True\n",
            "models": {
                "__init__.py": "",
                "test_user.py": "def test_user_creation():\n    assert True\n",
            },
        },
        "docs": {
            "README.md": "# Test Project\n\nThis is a test project.\n",
            "api.md": "# API Documentation\n\n## Endpoints\n",
        },
        "config": {
            "settings.json": json.dumps(
                {
                    "database": {"host": "localhost", "port": 5432},
                    "api": {"version": "v1", "timeout": 30},
                },
                indent=2,
            ),
            "development.env": "DEBUG=true\nLOG_LEVEL=debug\n",
        },
        ".gitignore": "*.pyc\n__pycache__/\n.env\n",
        "pyproject.toml": '[tool.poetry]\nname = "test-project"\nversion = "0.1.0"\n',
        "README.md": "# Test Project\n\nMain readme file.\n",
    }


@pytest.fixture
def json_config_file(temp_dir):
    """Create a JSON configuration file for testing."""
    config_data = {
        "test_setting": "test_value",
        "nested": {"key": "value", "number": 42},
    }
    config_file = temp_dir / "test_config.json"
    config_file.write_text(json.dumps(config_data, indent=2))
    return config_file


@pytest.fixture
def mock_git_operations():
    """Mock common git operations for testing."""
    operations = Mock()

    operations.get_modified_files = Mock(
        return_value=["src/main.py", "tests/test_main.py"]
    )
    operations.get_untracked_files = Mock(return_value=["new_file.py"])
    operations.get_staged_files = Mock(return_value=["README.md"])
    operations.get_current_branch = Mock(return_value="feature/test-branch")
    operations.get_commit_history = Mock(
        return_value=[
            {"hash": "abc123", "message": "Test commit", "author": "Test User"}
        ]
    )
    operations.has_uncommitted_changes = Mock(return_value=True)
    operations.has_unpushed_commits = Mock(return_value=True)
    operations.get_repo_root = Mock(return_value="/path/to/repo")

    return operations


@pytest.fixture
def environment_variables():
    """Manage environment variables for testing."""
    original_env = dict(os.environ)
    test_env = {
        "MCP_LOG_LEVEL": "DEBUG",
        "MCP_TEST_MODE": "true",
        "GIT_AUTHOR_NAME": "Test User",
        "GIT_AUTHOR_EMAIL": "test@example.com",
    }

    # Set test environment variables
    os.environ.update(test_env)

    yield test_env

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Conditional fixtures for git operations (only if git is available)
if HAS_GIT:

    @pytest.fixture
    def temp_git_repo(temp_dir, environment_variables):
        """Create a temporary git repository for testing."""
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()

        # Initialize git repo
        repo = Repo.init(repo_path)

        # Configure git user for this repo
        with repo.config_writer() as git_config:
            git_config.set_value("user", "name", "Test User")
            git_config.set_value("user", "email", "test@example.com")

        # Create initial files
        readme = repo_path / "README.md"
        readme.write_text("# Test Repository\n\nThis is a test repository.")

        src_dir = repo_path / "src"
        src_dir.mkdir()
        main_file = src_dir / "main.py"
        main_file.write_text("print('Hello, World!')")

        # Initial commit
        repo.index.add([str(readme), str(main_file)])
        repo.index.commit("Initial commit")

        yield repo_path

    @pytest.fixture
    def repo_with_changes(temp_git_repo):
        """Git repository with various types of changes."""
        repo = Repo(temp_git_repo)

        # Modify existing file
        main_file = temp_git_repo / "src" / "main.py"
        main_file.write_text("print('Hello, Modified World!')")

        # Create new untracked file
        new_file = temp_git_repo / "new_feature.py"
        new_file.write_text("def new_feature():\n    pass")

        # Create and stage a file
        staged_file = temp_git_repo / "staged_file.py"
        staged_file.write_text("def staged_function():\n    return 'staged'")
        repo.index.add([str(staged_file)])

        # Create a stash
        stash_file = temp_git_repo / "stash_test.py"
        stash_file.write_text("def stash_function():\n    pass")
        repo.index.add([str(stash_file)])
        repo.git.stash("save", "test stash")

        return temp_git_repo

else:

    @pytest.fixture
    def temp_git_repo(temp_dir):
        """Fallback fixture when git is not available."""
        pytest.skip("Git not available for testing")

    @pytest.fixture
    def repo_with_changes(temp_dir):
        """Fallback fixture when git is not available."""
        pytest.skip("Git not available for testing")


# Utility functions for tests
def assert_file_exists(file_path: Path, message: str = None):
    """Assert that a file exists with optional custom message."""
    if message is None:
        message = f"Expected file {file_path} to exist"
    assert file_path.exists() and file_path.is_file(), message


def assert_dir_exists(dir_path: Path, message: str = None):
    """Assert that a directory exists with optional custom message."""
    if message is None:
        message = f"Expected directory {dir_path} to exist"
    assert dir_path.exists() and dir_path.is_dir(), message


def assert_file_content_contains(file_path: Path, content: str, message: str = None):
    """Assert that a file contains specific content."""
    if message is None:
        message = f"Expected file {file_path} to contain '{content}'"
    assert file_path.exists(), f"File {file_path} does not exist"
    file_content = file_path.read_text()
    assert content in file_content, message


def create_mock_tool_result(
    status: str = "success", data: Any = None, error: str = None
):
    """Create a standardized mock tool result."""
    result = {"status": status}
    if data is not None:
        result["data"] = data
    if error is not None:
        result["error"] = error
    return result


# Make utility functions available as fixtures
@pytest.fixture
def file_assertions():
    """Provide file assertion utilities."""
    return {
        "assert_file_exists": assert_file_exists,
        "assert_dir_exists": assert_dir_exists,
        "assert_file_content_contains": assert_file_content_contains,
    }


@pytest.fixture
def mock_tool_result():
    """Factory for creating mock tool results."""
    return create_mock_tool_result


# Export fixtures for use in other test modules
__all__ = [
    "test_data_dir",
    "shared_temp_dir",
    "temp_dir",
    "mock_git_repo",
    "sample_config",
    "sample_file_changes",
    "mock_mcp_server",
    "sample_analysis_result",
    "mock_fastmcp_server",
    "create_test_files",
    "sample_project_structure",
    "json_config_file",
    "mock_git_operations",
    "environment_variables",
    "temp_git_repo",
    "repo_with_changes",
    "file_assertions",
    "mock_tool_result",
]
