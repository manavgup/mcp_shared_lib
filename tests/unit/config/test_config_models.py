"""Unit tests for configuration models in mcp_shared_lib (current schema)."""

import pytest

from mcp_shared_lib.config.git_analyzer import GitAnalyzerSettings

# Treat all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestGitAnalyzerSettings:
    """Test git analyzer configuration settings."""

    def test_git_analyzer_default_settings(self):
        """Defaults match current GitAnalyzerSettings fields and constraints."""
        settings = GitAnalyzerSettings()

        assert settings.log_level == "INFO"
        assert settings.max_diff_lines == 1000
        assert settings.max_commits_to_analyze == 50
        assert settings.include_binary_files is False
        assert settings.large_file_threshold == 1000
        assert "pyproject.toml" in settings.critical_file_patterns

    def test_git_analyzer_custom_settings(self):
        """Custom values within bounds are respected."""
        settings = GitAnalyzerSettings(
            log_level="DEBUG",
            max_diff_lines=5000,
            max_commits_to_analyze=100,
            include_binary_files=True,
            large_file_threshold=2000,
            critical_file_patterns=["*.env", "Dockerfile"],
        )

        assert settings.log_level == "DEBUG"
        assert settings.max_diff_lines == 5000
        assert settings.max_commits_to_analyze == 100
        assert settings.include_binary_files is True
        assert settings.large_file_threshold == 2000
        assert settings.critical_file_patterns == ["*.env", "Dockerfile"]

    def test_git_analyzer_invalid_bounds(self):
        """Exceeding bounds raises validation errors."""
        with pytest.raises(Exception):
            GitAnalyzerSettings(max_diff_lines=20000)  # > le=10000
        with pytest.raises(Exception):
            GitAnalyzerSettings(max_commits_to_analyze=0)  # < ge=1
        with pytest.raises(Exception):
            GitAnalyzerSettings(large_file_threshold=50)  # < ge=100


class TestSettingsIntegration:
    """Test settings serialization and extreme valid values."""

    def test_settings_with_extreme_values(self):
        settings = GitAnalyzerSettings(
            max_diff_lines=10,  # lower bound
            max_commits_to_analyze=1,  # lower bound
            large_file_threshold=100,  # lower bound
        )

        assert settings.max_diff_lines == 10
        assert settings.max_commits_to_analyze == 1
        assert settings.large_file_threshold == 100

    def test_settings_with_large_values(self):
        settings = GitAnalyzerSettings(
            max_diff_lines=10000,  # upper bound
            max_commits_to_analyze=500,  # upper bound
            large_file_threshold=10000,  # upper bound
        )

        assert settings.max_diff_lines == 10000
        assert settings.max_commits_to_analyze == 500
        assert settings.large_file_threshold == 10000

    def test_settings_model_validation_and_json(self):
        settings = GitAnalyzerSettings(log_level="DEBUG")

        data = settings.model_dump()
        assert isinstance(data, dict)
        assert data["log_level"] == "DEBUG"

        json_str = settings.model_dump_json()
        assert isinstance(json_str, str)
        assert "DEBUG" in json_str

        roundtrip = GitAnalyzerSettings.model_validate_json(json_str)
        assert roundtrip.log_level == "DEBUG"
