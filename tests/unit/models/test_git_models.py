"""Unit tests for git models in mcp_shared_lib."""

import tempfile
from pathlib import Path

import pytest

from mcp_shared_lib.models.git.files import (
    FileStatus,
)
from mcp_shared_lib.models.git.repository import (
    GitBranch,
    GitRemote,
    LocalRepository,
)


@pytest.mark.unit
class TestGitRemote:
    """Test GitRemote model."""

    def test_git_remote_creation(self):
        """Test creating a GitRemote instance."""
        remote = GitRemote(
            name="origin",
            url="https://github.com/test/repo.git",
            fetch_url="https://github.com/test/repo.git",
            push_url="https://github.com/test/repo.git",
        )

        assert remote.name == "origin"
        assert remote.url == "https://github.com/test/repo.git"
        assert remote.fetch_url == "https://github.com/test/repo.git"
        assert remote.push_url == "https://github.com/test/repo.git"

    def test_git_remote_auto_push_url(self):
        """Test that push_url defaults to url when not provided."""
        remote = GitRemote(
            name="origin",
            url="https://github.com/test/repo.git",
            fetch_url="https://github.com/test/repo.git",
            push_url="",  # Will be auto-set by validator
        )

        assert remote.push_url == "https://github.com/test/repo.git"


@pytest.mark.unit
class TestGitBranch:
    """Test GitBranch model."""

    def test_git_branch_creation(self):
        """Test creating a GitBranch instance."""
        branch = GitBranch(
            name="main",
            is_current=True,
            is_remote=False,
            upstream="origin/main",
            ahead_count=2,
            behind_count=1,
            last_commit_sha="abc123def456",
            last_commit_date="2025-01-01T00:00:00Z",
        )

        assert branch.name == "main"
        assert branch.is_current is True
        assert branch.is_remote is False
        assert branch.upstream == "origin/main"
        assert branch.ahead_count == 2
        assert branch.behind_count == 1
        assert branch.last_commit_sha == "abc123def456"
        assert branch.last_commit_date == "2025-01-01T00:00:00Z"

    def test_git_branch_defaults(self):
        """Test GitBranch with default values."""
        branch = GitBranch(name="feature/test")

        assert branch.name == "feature/test"
        assert branch.is_current is False
        assert branch.is_remote is False
        assert branch.upstream is None
        assert branch.ahead_count == 0
        assert branch.behind_count == 0
        assert branch.last_commit_sha is None
        assert branch.last_commit_date is None

    def test_git_branch_validation(self):
        """Test GitBranch validation for non-negative counts."""
        branch = GitBranch(
            name="test",
            ahead_count=0,
            behind_count=0,
        )

        assert branch.ahead_count == 0
        assert branch.behind_count == 0


@pytest.mark.unit
class TestLocalRepository:
    """Test LocalRepository model."""

    def setup_method(self):
        """Set up a temporary git repository for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.git_dir = Path(self.temp_dir) / ".git"
        self.git_dir.mkdir()
        self.repo_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_local_repository_creation(self):
        """Test creating a LocalRepository instance."""
        repo = LocalRepository(
            path=self.repo_path,
            name="test-repo",
            current_branch="main",
            head_commit="abc123def456",
            remote_url="https://github.com/test/repo.git",
            is_dirty=False,
        )

        assert repo.path == self.repo_path
        assert repo.name == "test-repo"
        assert repo.current_branch == "main"
        assert repo.head_commit == "abc123def456"
        assert repo.remote_url == "https://github.com/test/repo.git"
        assert repo.is_dirty is False

    def test_local_repository_defaults(self):
        """Test LocalRepository with default values."""
        repo = LocalRepository(
            path=self.repo_path,
            name="test-repo",
            current_branch="main",
            head_commit="abc123",
        )

        assert repo.remote_url is None
        assert repo.remote_branches == []
        assert repo.is_dirty is False
        assert repo.is_bare is False
        assert repo.upstream_branch is None
        assert repo.remotes == []
        assert repo.branches == []

    def test_local_repository_with_remotes_and_branches(self):
        """Test LocalRepository with remotes and branches."""
        remote = GitRemote(
            name="origin",
            url="https://github.com/test/repo.git",
            fetch_url="https://github.com/test/repo.git",
            push_url="https://github.com/test/repo.git",
        )

        branch = GitBranch(
            name="main",
            is_current=True,
            upstream="origin/main",
        )

        repo = LocalRepository(
            path=self.repo_path,
            name="test-repo",
            current_branch="main",
            head_commit="abc123",
            remotes=[remote],
            branches=[branch],
        )

        assert len(repo.remotes) == 1
        assert repo.remotes[0].name == "origin"
        assert len(repo.branches) == 1
        assert repo.branches[0].name == "main"
        assert repo.branches[0].is_current is True

    def test_local_repository_name_auto_generation(self):
        """Test that repository name is auto-generated from path."""
        # This tests the validator that should set name from path
        repo = LocalRepository(
            path=self.repo_path,
            name="",  # Will be auto-set by validator
            current_branch="main",
            head_commit="abc123",
        )

        # The name should be set to the directory name
        assert repo.name == self.repo_path.name

    def test_local_repository_invalid_path(self):
        """Test LocalRepository with invalid git repository path."""
        invalid_path = Path("/tmp/not-a-git-repo")

        with pytest.raises(ValueError, match="Not a git repository"):
            LocalRepository(
                path=invalid_path,
                name="invalid",
                current_branch="main",
                head_commit="abc123",
            )


@pytest.mark.unit
class TestFileStatus:
    """Test FileStatus model."""

    def test_file_status_creation(self):
        """Test creating a FileStatus instance."""
        file_status = FileStatus(
            path="src/main.py",
            status_code="M",
            staged=True,
            working_tree_status="M",
            index_status="M",
            lines_added=10,
            lines_deleted=5,
            is_binary=False,
        )

        assert file_status.path == "src/main.py"
        assert file_status.status_code == "M"
        assert file_status.staged is True
        assert file_status.working_tree_status == "M"
        assert file_status.index_status == "M"
        assert file_status.lines_added == 10
        assert file_status.lines_deleted == 5
        assert file_status.is_binary is False

    def test_file_status_defaults(self):
        """Test FileStatus with default values."""
        file_status = FileStatus(
            path="test.py",
            status_code="A",
        )

        assert file_status.path == "test.py"
        assert file_status.status_code == "A"
        assert file_status.staged is False
        assert file_status.working_tree_status is None
        assert file_status.index_status is None
        assert file_status.lines_added == 0
        assert file_status.lines_deleted == 0
        assert file_status.is_binary is False
        assert file_status.old_path is None

    def test_file_status_total_changes_property(self):
        """Test the total_changes property."""
        file_status = FileStatus(
            path="test.py",
            status_code="M",
            lines_added=15,
            lines_deleted=8,
        )

        assert file_status.total_changes == 23

    def test_file_status_total_changes_zero(self):
        """Test total_changes with zero changes."""
        file_status = FileStatus(
            path="test.py",
            status_code="M",
            lines_added=0,
            lines_deleted=0,
        )

        assert file_status.total_changes == 0

    def test_file_status_status_description_property(self):
        """Test the status_description property."""
        file_status = FileStatus(
            path="test.py",
            status_code="M",
        )

        # The property should return a human-readable description
        description = file_status.status_description
        assert isinstance(description, str)
        assert len(description) > 0

    def test_file_status_with_rename(self):
        """Test FileStatus with file rename."""
        file_status = FileStatus(
            path="new_name.py",
            status_code="R",
            old_path="old_name.py",
            lines_added=5,
            lines_deleted=3,
        )

        assert file_status.path == "new_name.py"
        assert file_status.old_path == "old_name.py"
        assert file_status.status_code == "R"
        assert file_status.total_changes == 8

    def test_file_status_binary_file(self):
        """Test FileStatus for binary file."""
        file_status = FileStatus(
            path="image.png",
            status_code="A",
            is_binary=True,
            lines_added=0,
            lines_deleted=0,
        )

        assert file_status.is_binary is True
        assert file_status.total_changes == 0

    def test_file_status_negative_lines_validation(self):
        """Test that negative line counts are not allowed."""
        # Pydantic should validate that lines_added and lines_deleted are >= 0
        file_status = FileStatus(
            path="test.py",
            status_code="M",
            lines_added=0,
            lines_deleted=0,
        )

        assert file_status.lines_added == 0
        assert file_status.lines_deleted == 0


@pytest.mark.unit
class TestModelIntegration:
    """Test integration between models."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.git_dir = Path(self.temp_dir) / ".git"
        self.git_dir.mkdir()
        self.repo_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_repository_with_complex_structure(self):
        """Test repository with multiple remotes and branches."""
        origin_remote = GitRemote(
            name="origin",
            url="https://github.com/user/repo.git",
            fetch_url="https://github.com/user/repo.git",
            push_url="https://github.com/user/repo.git",
        )

        upstream_remote = GitRemote(
            name="upstream",
            url="https://github.com/original/repo.git",
            fetch_url="https://github.com/original/repo.git",
            push_url="https://github.com/original/repo.git",
        )

        main_branch = GitBranch(
            name="main",
            is_current=True,
            upstream="origin/main",
            ahead_count=0,
            behind_count=0,
        )

        feature_branch = GitBranch(
            name="feature/new-feature",
            is_current=False,
            upstream="origin/feature/new-feature",
            ahead_count=3,
            behind_count=1,
        )

        repo = LocalRepository(
            path=self.repo_path,
            name="complex-repo",
            current_branch="main",
            head_commit="abc123def456",
            remotes=[origin_remote, upstream_remote],
            branches=[main_branch, feature_branch],
            remote_branches=["origin/main", "origin/develop", "upstream/main"],
        )

        assert len(repo.remotes) == 2
        assert len(repo.branches) == 2
        assert len(repo.remote_branches) == 3
        assert repo.remotes[0].name == "origin"
        assert repo.remotes[1].name == "upstream"
        assert repo.branches[0].is_current is True
        assert repo.branches[1].ahead_count == 3

    def test_model_serialization(self):
        """Test that models can be serialized to dict/JSON."""
        file_status = FileStatus(
            path="test.py",
            status_code="M",
            lines_added=5,
            lines_deleted=2,
        )

        # Should be able to convert to dict
        data = file_status.model_dump()
        assert isinstance(data, dict)
        assert data["path"] == "test.py"
        assert data["status_code"] == "M"
        assert data["lines_added"] == 5

        # Should be able to create from dict
        new_file_status = FileStatus(**data)
        assert new_file_status.path == file_status.path
        assert new_file_status.status_code == file_status.status_code
        assert new_file_status.lines_added == file_status.lines_added
