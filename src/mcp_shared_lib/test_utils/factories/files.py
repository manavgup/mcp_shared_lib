"""
File-related test data factories.

This module provides factories for creating realistic file changes,
file metadata, and file system structures.
"""

import random
from datetime import datetime, timedelta
from typing import Any

from .base import BaseFactory, Faker


class FileChangeFactory(BaseFactory):
    """Factory for creating realistic file change objects."""

    @staticmethod
    def file_path() -> str:
        """Generate a realistic file path."""
        # Different file types with appropriate extensions
        file_types = {
            "python": [".py"],
            "javascript": [".js", ".ts", ".jsx", ".tsx"],
            "markup": [".html", ".xml"],
            "stylesheet": [".css", ".scss", ".sass"],
            "config": [".json", ".yaml", ".yml", ".toml", ".ini"],
            "documentation": [".md", ".rst", ".txt"],
            "database": [".sql"],
            "shell": [".sh", ".bash", ".zsh"],
            "docker": ["Dockerfile", ".dockerignore"],
            "ci": [".yml", ".yaml"],
        }

        # Choose file type based on realistic distribution
        type_weights = {
            "python": 40,
            "javascript": 20,
            "config": 15,
            "documentation": 10,
            "stylesheet": 5,
            "markup": 4,
            "database": 3,
            "shell": 2,
            "docker": 1,
        }

        file_type = Faker.weighted_choice(
            list(type_weights.keys()), list(type_weights.values())
        )

        extensions = file_types[file_type]
        extension = random.choice(extensions)

        # Generate appropriate path based on file type
        if file_type == "python":
            return Faker.file_path(
                depth=random.randint(2, 4), extension=extension.lstrip(".")
            )
        elif file_type in ["config", "docker"]:
            return Faker.file_path(depth=1, extension=extension.lstrip("."))
        elif file_type == "documentation":
            if random.random() < 0.5:
                return Faker.file_path(depth=1, extension=extension.lstrip("."))
            else:
                return (
                    f"docs/{Faker.file_path(depth=1, extension=extension.lstrip('.'))}"
                )
        else:
            return Faker.file_path(
                depth=random.randint(1, 3), extension=extension.lstrip(".")
            )

    @staticmethod
    def change_type() -> str:
        """Generate change type with realistic distribution."""
        return Faker.weighted_choice(
            ["modified", "added", "deleted", "renamed"],
            [70, 20, 5, 5],  # Most changes are modifications
        )

    @staticmethod
    def lines_added() -> int:
        """Generate lines added with realistic distribution."""
        # Most changes are small, some are medium, few are large
        size_type = Faker.weighted_choice(["small", "medium", "large"], [70, 25, 5])

        if size_type == "small":
            return Faker.random_int(1, 20)
        elif size_type == "medium":
            return Faker.random_int(21, 100)
        else:  # large
            return Faker.random_int(101, 500)

    @staticmethod
    def lines_removed() -> int:
        """Generate lines removed (usually less than added)."""
        return Faker.random_int(0, 50)

    @staticmethod
    def risk_score() -> float:
        """Generate risk score with realistic distribution."""
        # Most changes are low-medium risk
        return Faker.weighted_choice(
            [Faker.pyfloat(0.0, 0.3), Faker.pyfloat(0.3, 0.7), Faker.pyfloat(0.7, 1.0)],
            [60, 30, 10],
        )

    @staticmethod
    def complexity_change() -> int:
        """Generate complexity change."""
        return Faker.random_int(-5, 15)

    @staticmethod
    def test_coverage() -> float:
        """Generate test coverage percentage."""
        return Faker.pyfloat(0.0, 1.0)

    @staticmethod
    def file_size_bytes() -> int:
        """Generate file size in bytes."""
        return Faker.random_int(100, 50000)

    @staticmethod
    def last_modified() -> datetime:
        """Generate last modified timestamp."""
        return Faker.date_time()

    @staticmethod
    def language() -> str:
        """Determine programming language from file path."""
        languages = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".kt": "kotlin",
            ".swift": "swift",
            ".md": "markdown",
            ".html": "html",
            ".css": "css",
            ".sql": "sql",
            ".sh": "shell",
            ".yaml": "yaml",
            ".json": "json",
        }
        return random.choice(list(languages.values()))

    @classmethod
    def create(cls, **kwargs) -> dict[str, Any]:
        """Create file change with computed properties."""
        change = super().create(**kwargs)

        # Compute derived properties
        change["net_lines"] = change["lines_added"] - change["lines_removed"]
        change["change_size"] = abs(change["net_lines"])

        # Adjust risk based on file characteristics
        if change["file_path"].endswith((".json", ".yaml", ".yml", ".toml")):
            change["risk_score"] = min(change["risk_score"] + 0.2, 1.0)
        elif "test" in change["file_path"].lower():
            change["risk_score"] = max(change["risk_score"] - 0.3, 0.0)

        return change

    # Trait methods for different file types and scenarios
    @classmethod
    def trait_high_risk(cls) -> dict[str, Any]:
        """Trait for high-risk file changes."""
        critical_files = [
            "setup.py",
            "pyproject.toml",
            "requirements.txt",
            "package.json",
            "Dockerfile",
            "docker-compose.yml",
            ".github/workflows/ci.yml",
            "config/production.json",
            "src/core/auth.py",
            "migrations/001_initial.sql",
        ]

        return {
            "file_path": random.choice(critical_files),
            "risk_score": Faker.pyfloat(0.7, 1.0),
            "lines_added": Faker.random_int(10, 100),
            "complexity_change": Faker.random_int(3, 10),
        }

    @classmethod
    def trait_low_risk(cls) -> dict[str, Any]:
        """Trait for low-risk file changes."""
        safe_files = [
            "README.md",
            "CHANGELOG.md",
            "docs/api.md",
            "docs/tutorial.md",
            "tests/test_utils.py",
            "tests/fixtures/sample_data.json",
            ".gitignore",
            "LICENSE",
        ]

        return {
            "file_path": random.choice(safe_files),
            "risk_score": Faker.pyfloat(0.0, 0.3),
            "lines_added": Faker.random_int(1, 30),
            "complexity_change": Faker.random_int(-2, 2),
        }

    @classmethod
    def trait_source_code(cls) -> dict[str, Any]:
        """Trait for source code files."""
        source_files = [
            "src/analyzer.py",
            "src/processor.py",
            "src/utils.py",
            "src/models/base.py",
            "src/services/git_service.py",
            "src/api/endpoints.py",
            "src/cli/commands.py",
        ]

        return {
            "file_path": random.choice(source_files),
            "language": "python",
            "risk_score": Faker.pyfloat(0.3, 0.8),
            "complexity_change": Faker.random_int(0, 8),
        }

    @classmethod
    def trait_test_file(cls) -> dict[str, Any]:
        """Trait for test files."""
        test_files = [
            "tests/test_analyzer.py",
            "tests/test_processor.py",
            "tests/unit/test_models.py",
            "tests/integration/test_workflow.py",
            "tests/fixtures/sample_data.py",
        ]

        return {
            "file_path": random.choice(test_files),
            "language": "python",
            "risk_score": Faker.pyfloat(0.0, 0.4),
            "test_coverage": 1.0,
            "complexity_change": Faker.random_int(0, 5),
        }

    @classmethod
    def trait_documentation(cls) -> dict[str, Any]:
        """Trait for documentation files."""
        doc_files = [
            "README.md",
            "docs/api.md",
            "docs/tutorial.md",
            "docs/setup.md",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
        ]

        return {
            "file_path": random.choice(doc_files),
            "language": "markdown",
            "risk_score": Faker.pyfloat(0.0, 0.2),
            "complexity_change": 0,
            "lines_added": Faker.random_int(5, 100),
        }

    @classmethod
    def trait_configuration(cls) -> dict[str, Any]:
        """Trait for configuration files."""
        config_files = [
            "pyproject.toml",
            "setup.cfg",
            "tox.ini",
            ".pre-commit-config.yaml",
            "docker-compose.yml",
            "Dockerfile",
            ".github/workflows/test.yml",
            "config/development.json",
            "config/production.yaml",
        ]

        return {
            "file_path": random.choice(config_files),
            "risk_score": Faker.pyfloat(0.6, 1.0),
            "lines_added": Faker.random_int(2, 50),
            "complexity_change": Faker.random_int(0, 3),
        }

    @classmethod
    def trait_large_change(cls) -> dict[str, Any]:
        """Trait for large file changes."""
        return {
            "lines_added": Faker.random_int(200, 1000),
            "lines_removed": Faker.random_int(50, 300),
            "complexity_change": Faker.random_int(5, 20),
            "risk_score": Faker.pyfloat(0.5, 0.9),
        }

    @classmethod
    def trait_small_change(cls) -> dict[str, Any]:
        """Trait for small file changes."""
        return {
            "lines_added": Faker.random_int(1, 10),
            "lines_removed": Faker.random_int(0, 5),
            "complexity_change": Faker.random_int(-1, 2),
            "risk_score": Faker.pyfloat(0.0, 0.4),
        }


class FileMetadataFactory(BaseFactory):
    """Factory for creating file metadata objects."""

    @staticmethod
    def file_path() -> str:
        """File path."""
        return FileChangeFactory.file_path()

    @staticmethod
    def size_bytes() -> int:
        """File size in bytes."""
        return Faker.random_int(100, 100000)

    @staticmethod
    def line_count() -> int:
        """Number of lines in file."""
        return Faker.random_int(10, 1000)

    @staticmethod
    def language() -> str:
        """Programming language."""
        return FileChangeFactory.language()

    @staticmethod
    def encoding() -> str:
        """File encoding."""
        return Faker.weighted_choice(["utf-8", "ascii", "latin-1"], [90, 8, 2])

    @staticmethod
    def permissions() -> str:
        """File permissions (Unix-style)."""
        return random.choice(["644", "755", "600", "664"])

    @staticmethod
    def created_date() -> datetime:
        """File creation date."""
        return datetime.now() - timedelta(days=Faker.random_int(1, 365))

    @staticmethod
    def modified_date() -> datetime:
        """Last modified date."""
        return Faker.date_time()

    @staticmethod
    def checksum() -> str:
        """File checksum/hash."""
        return Faker.hex_string(32)  # MD5-style hash

    @staticmethod
    def mime_type() -> str:
        """MIME type."""
        mime_types = {
            "python": "text/x-python",
            "javascript": "application/javascript",
            "json": "application/json",
            "yaml": "application/x-yaml",
            "markdown": "text/markdown",
            "html": "text/html",
            "css": "text/css",
            "sql": "application/sql",
            "shell": "application/x-sh",
        }
        return random.choice(list(mime_types.values()))


# Convenience functions for creating file-related collections
def create_file_changes(
    count: int = 5,
    risk_distribution: str = "mixed",
    change_types: list[str] = None,
    **kwargs,
) -> list[dict[str, Any]]:
    """
    Create a list of realistic file changes.

    Args:
        count: Number of file changes to create
        risk_distribution: 'low', 'high', or 'mixed'
        change_types: List of allowed change types
        **kwargs: Additional arguments passed to factory

    Returns:
        List of file change dictionaries
    """
    if change_types is None:
        change_types = ["modified", "added", "deleted"]

    changes = []

    for i in range(count):
        # Determine risk level
        if risk_distribution == "low":
            change = FileChangeFactory.with_traits("low_risk", **kwargs)
        elif risk_distribution == "high":
            change = FileChangeFactory.with_traits("high_risk", **kwargs)
        else:  # mixed
            risk_type = Faker.weighted_choice(
                ["low_risk", "medium", "high_risk"], [60, 30, 10]
            )
            if risk_type == "low_risk":
                change = FileChangeFactory.with_traits("low_risk", **kwargs)
            elif risk_type == "high_risk":
                change = FileChangeFactory.with_traits("high_risk", **kwargs)
            else:
                change = FileChangeFactory.create(**kwargs)

        # Override change type if specified
        if change_types:
            change["change_type"] = random.choice(change_types)

        changes.append(change)

    return changes


def create_file_tree(depth: int = 3, files_per_dir: int = 5) -> dict[str, Any]:
    """Create a realistic file tree structure."""

    def _create_directory(current_depth: int, max_depth: int) -> dict[str, Any]:
        if current_depth >= max_depth:
            return {}

        directory = {}

        # Add files to this directory
        for _ in range(random.randint(1, files_per_dir)):
            file_meta = FileMetadataFactory.create()
            filename = file_meta["file_path"].split("/")[-1]
            directory[filename] = file_meta

        # Add subdirectories
        subdir_count = random.randint(0, 3) if current_depth < max_depth - 1 else 0
        for i in range(subdir_count):
            subdir_name = f"subdir_{i}"
            directory[subdir_name] = _create_directory(current_depth + 1, max_depth)

        return directory

    return _create_directory(0, depth)


def create_diff_summary(file_changes: list[dict[str, Any]]) -> dict[str, Any]:
    """Create a summary of file changes (like git diff --stat)."""
    total_files = len(file_changes)
    total_additions = sum(change.get("lines_added", 0) for change in file_changes)
    total_deletions = sum(change.get("lines_removed", 0) for change in file_changes)

    # Categorize changes by type
    change_types = {}
    for change in file_changes:
        change_type = change.get("change_type", "modified")
        change_types[change_type] = change_types.get(change_type, 0) + 1

    # Find largest changes
    largest_changes = sorted(
        file_changes,
        key=lambda c: c.get("lines_added", 0) + c.get("lines_removed", 0),
        reverse=True,
    )[:5]

    return {
        "total_files": total_files,
        "total_additions": total_additions,
        "total_deletions": total_deletions,
        "net_change": total_additions - total_deletions,
        "change_types": change_types,
        "largest_changes": [
            {
                "file_path": change["file_path"],
                "total_lines": change.get("lines_added", 0)
                + change.get("lines_removed", 0),
            }
            for change in largest_changes
        ],
        "binary_files": [
            change["file_path"]
            for change in file_changes
            if change.get("file_path", "").endswith((".png", ".jpg", ".pdf", ".exe"))
        ],
    }


def create_file_changes_by_category() -> dict[str, list[dict[str, Any]]]:
    """Create file changes organized by category."""
    return {
        "source_code": [
            FileChangeFactory.with_traits("source_code")
            for _ in range(Faker.random_int(2, 8))
        ],
        "tests": [
            FileChangeFactory.with_traits("test_file")
            for _ in range(Faker.random_int(1, 5))
        ],
        "documentation": [
            FileChangeFactory.with_traits("documentation")
            for _ in range(Faker.random_int(0, 3))
        ],
        "configuration": [
            FileChangeFactory.with_traits("configuration")
            for _ in range(Faker.random_int(0, 2))
        ],
    }
