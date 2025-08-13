"""Unit tests for analysis models in mcp_shared_lib."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from mcp_shared_lib.models.analysis.categorization import (
    ChangeCategorization,
)
from mcp_shared_lib.models.analysis.repository import (
    BranchStatus,
    RepositoryStatus,
)
from mcp_shared_lib.models.analysis.risk import (
    RiskAssessment,
)
from mcp_shared_lib.models.git.changes import StagedChanges, WorkingDirectoryChanges
from mcp_shared_lib.models.git.commits import UnpushedCommit
from mcp_shared_lib.models.git.files import FileStatus
from mcp_shared_lib.models.git.repository import LocalRepository


@pytest.mark.unit
@pytest.mark.unit
class TestCategorizationModels:
    """Test categorization-related models."""

    def test_change_categorization_creation(self):
        """Test creating ChangeCategorization instance."""
        categorization = ChangeCategorization(
            critical_files=["config.py", "main.py"],
            source_code=["src/auth.py", "src/utils.py"],
            documentation=["README.md", "docs/api.md"],
            tests=["tests/test_auth.py"],
            configuration=["pyproject.toml"],
            other=["scripts/deploy.sh"],
        )

        assert len(categorization.critical_files) == 2
        assert len(categorization.source_code) == 2
        assert len(categorization.documentation) == 2
        assert len(categorization.tests) == 1
        assert len(categorization.configuration) == 1
        assert len(categorization.other) == 1
        assert categorization.total_files == 9
        assert categorization.has_critical_changes is True

    def test_change_categorization_empty(self):
        """Test empty ChangeCategorization."""
        categorization = ChangeCategorization()

        assert categorization.total_files == 0
        assert categorization.has_critical_changes is False
        assert len(categorization.critical_files) == 0
        assert len(categorization.source_code) == 0


@pytest.mark.unit
class TestRiskModels:
    """Test risk assessment models."""

    def test_risk_assessment_low_risk(self):
        """Test creating low-risk RiskAssessment."""
        assessment = RiskAssessment(
            risk_level="low",
            risk_factors=["small_changes"],
            large_changes=[],
            potential_conflicts=[],
            binary_changes=[],
        )

        assert assessment.risk_level == "low"
        assert assessment.is_high_risk is False
        assert assessment.risk_score == 2
        assert len(assessment.risk_factors) == 1

    def test_risk_assessment_high_risk(self):
        """Test creating high-risk RiskAssessment."""
        assessment = RiskAssessment(
            risk_level="high",
            risk_factors=["large_change", "critical_file", "no_tests"],
            large_changes=["core.py", "auth.py"],
            potential_conflicts=["config.py"],
            binary_changes=["image.png"],
        )

        assert assessment.risk_level == "high"
        assert assessment.is_high_risk is True
        assert assessment.risk_score == 9  # 8 base + 1 for conflicts
        assert len(assessment.large_changes) == 2
        assert len(assessment.potential_conflicts) == 1

    def test_risk_assessment_many_large_changes(self):
        """Test risk score with many large changes."""
        large_files = [f"file_{i}.py" for i in range(8)]  # >5 large changes

        assessment = RiskAssessment(
            risk_level="medium",
            large_changes=large_files,
            potential_conflicts=["conflict.py"],
        )

        # 5 (medium) + 1 (>5 large) + 1 (conflicts) = 7
        assert assessment.risk_score == 7


@pytest.mark.unit
class TestRepositoryModels:
    """Test repository analysis models."""

    def test_branch_status_up_to_date(self):
        """Test BranchStatus when up to date."""
        status = BranchStatus(
            current_branch="main",
            upstream_branch="origin/main",
            ahead_by=0,
            behind_by=0,
            is_up_to_date=True,
            needs_push=False,
            needs_pull=False,
        )

        assert status.current_branch == "main"
        assert status.is_up_to_date is True
        assert status.sync_status == "up to date"

    def test_branch_status_ahead(self):
        """Test BranchStatus when ahead."""
        status = BranchStatus(
            current_branch="feature",
            upstream_branch="origin/feature",
            ahead_by=3,
            behind_by=0,
            is_up_to_date=False,
            needs_push=True,
            needs_pull=False,
        )

        assert status.ahead_by == 3
        assert status.needs_push is True
        assert "3 commit(s) ahead" in status.sync_status

    def test_branch_status_diverged(self):
        """Test BranchStatus when diverged."""
        status = BranchStatus(
            current_branch="feature",
            upstream_branch="origin/feature",
            ahead_by=2,
            behind_by=1,
            is_up_to_date=False,
            needs_push=True,
            needs_pull=True,
        )

        assert "diverged" in status.sync_status
        assert "2 ahead, 1 behind" in status.sync_status

    def test_repository_status_with_changes(self):
        """Test RepositoryStatus with various changes."""
        # Create a temporary directory for the repository
        import tempfile
        temp_dir = tempfile.mkdtemp()
        git_dir = Path(temp_dir) / ".git"
        git_dir.mkdir()

        try:
            repo = LocalRepository(
                path=Path(temp_dir),
                name="test-repo",
                current_branch="main",
                head_commit="abc123",
            )

            working_dir = WorkingDirectoryChanges(
                modified_files=[
                    FileStatus(path="src/main.py", status_code="M")
                ],
                added_files=[
                    FileStatus(path="src/new.py", status_code="A")
                ],
            )

            staged_changes = StagedChanges(
                staged_files=[
                    FileStatus(path="src/staged.py", status_code="A", staged=True)
                ]
            )

            unpushed_commits = [
                UnpushedCommit(
                    sha="commit1",
                    message="Test commit",
                    author="Test Author",
                    author_email="test@example.com",
                    date=datetime.now(timezone.utc),
                    insertions=10,
                    deletions=5,
                )
            ]

            branch_status = BranchStatus(
                current_branch="main",
                upstream_branch="origin/main",
                ahead_by=1,
                behind_by=0,
                is_up_to_date=False,
                needs_push=True,
                needs_pull=False,
            )

            repo_status = RepositoryStatus(
                repository=repo,
                working_directory=working_dir,
                staged_changes=staged_changes,
                unpushed_commits=unpushed_commits,
                stashed_changes=[],
                branch_status=branch_status,
            )

            assert repo_status.has_outstanding_work is True
            assert repo_status.total_outstanding_changes == 4  # 2 working + 1 staged + 1 unpushed
            assert repo_status.working_directory.total_files == 2
            assert repo_status.staged_changes.total_staged == 1
            assert len(repo_status.unpushed_commits) == 1

        finally:
            # Clean up
            import shutil
            shutil.rmtree(temp_dir)

    def test_repository_status_clean(self):
        """Test RepositoryStatus with no changes."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        git_dir = Path(temp_dir) / ".git"
        git_dir.mkdir()

        try:
            repo = LocalRepository(
                path=Path(temp_dir),
                name="clean-repo",
                current_branch="main",
                head_commit="abc123",
            )

            working_dir = WorkingDirectoryChanges()
            staged_changes = StagedChanges()

            branch_status = BranchStatus(
                current_branch="main",
                upstream_branch="origin/main",
                ahead_by=0,
                behind_by=0,
                is_up_to_date=True,
                needs_push=False,
                needs_pull=False,
            )

            repo_status = RepositoryStatus(
                repository=repo,
                working_directory=working_dir,
                staged_changes=staged_changes,
                unpushed_commits=[],
                stashed_changes=[],
                branch_status=branch_status,
            )

            assert repo_status.has_outstanding_work is False
            assert repo_status.total_outstanding_changes == 0

        finally:
            import shutil
            shutil.rmtree(temp_dir)


@pytest.mark.unit
class TestModelIntegration:
    """Test integration between analysis models."""

    def test_models_serialization(self):
        """Test that models can be serialized and deserialized."""
        assessment = RiskAssessment(
            risk_level="medium",
            risk_factors=["test_factor"],
            large_changes=["test_file.py"],
        )

        # Should be able to convert to dict
        data = assessment.model_dump()
        assert isinstance(data, dict)
        assert data["risk_level"] == "medium"

        # Should be able to create from dict
        new_assessment = RiskAssessment(**data)
        assert new_assessment.risk_level == assessment.risk_level
        assert new_assessment.risk_factors == assessment.risk_factors

    def test_categorization_and_risk_integration(self):
        """Test categorization with risk assessment."""
        categorization = ChangeCategorization(
            critical_files=["core.py"],
            source_code=["feature.py"],
            tests=["test_feature.py"],
        )

        risk = RiskAssessment(
            risk_level="medium",
            risk_factors=["critical_file_change"],
            large_changes=["feature.py"],
        )

        # Both models should work together
        assert categorization.has_critical_changes
        assert risk.is_high_risk is False
        assert len(risk.large_changes) == 1

        # Can be used to determine if extra validation needed
        needs_extra_validation = (
            categorization.has_critical_changes or risk.is_high_risk
        )
        assert needs_extra_validation is True
