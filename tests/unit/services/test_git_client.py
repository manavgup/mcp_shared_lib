"""Unit tests for git client service."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_shared_lib.config.git_analyzer import GitAnalyzerSettings
from mcp_shared_lib.services.git.git_client import GitClient, GitCommandError


@pytest.fixture
def git_settings():
    """Create git analyzer settings for testing."""
    return GitAnalyzerSettings(
        max_diff_lines=1000,
        max_commits_to_analyze=50,
        include_binary_files=False,
        large_file_threshold=500,
        log_level="DEBUG",
    )


@pytest.fixture
def git_client(git_settings):
    """Create git client instance for testing."""
    return GitClient(git_settings)


@pytest.fixture
def mock_context():
    """Mock MCP context for testing."""
    ctx = AsyncMock()
    ctx.debug = AsyncMock()
    ctx.error = AsyncMock()
    ctx.info = AsyncMock()
    ctx.warning = AsyncMock()
    return ctx


@pytest.fixture
def temp_repo_path(tmp_path):
    """Create a temporary repository path."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    return repo_path


@pytest.mark.unit
class TestGitCommandError:
    """Test GitCommandError exception."""

    def test_git_command_error_creation(self):
        """Test GitCommandError creation with details."""
        command = ["git", "status"]
        return_code = 128
        stderr = "fatal: not a git repository"

        error = GitCommandError(command, return_code, stderr)

        assert error.command == command
        assert error.return_code == return_code
        assert error.stderr == stderr
        assert "Git command failed" in str(error)
        assert "git status" in str(error)
        assert stderr in str(error)


@pytest.mark.unit
class TestGitClient:
    """Test GitClient functionality."""

    def test_git_client_initialization(self, git_settings):
        """Test GitClient initialization."""
        client = GitClient(git_settings)

        assert client.settings == git_settings
        assert client.logger is not None
        assert hasattr(client, "execute_command")

    @pytest.mark.asyncio
    async def test_execute_command_success(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test successful command execution."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"output\n", b""))

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_process
        ) as mock_exec:
            result = await git_client.execute_command(
                temp_repo_path, ["status"], ctx=mock_context
            )

            assert result == "output"
            mock_exec.assert_called_once()
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_execute_command_failure(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test command execution failure."""
        mock_process = Mock()
        mock_process.returncode = 128
        mock_process.communicate = AsyncMock(
            return_value=(b"", b"fatal: not a git repository\n")
        )

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            with pytest.raises(GitCommandError) as exc_info:
                await git_client.execute_command(
                    temp_repo_path, ["status"], ctx=mock_context
                )

            # The execute_command may wrap the error differently
            assert exc_info.value.return_code in [128, -1]  # Could be either
            assert "not a git repository" in exc_info.value.stderr
            mock_context.error.assert_called()

    @pytest.mark.asyncio
    async def test_execute_command_no_check(self, git_client, temp_repo_path):
        """Test command execution without error checking."""
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b"", b"some error\n"))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            # Should not raise exception when check=False
            result = await git_client.execute_command(
                temp_repo_path, ["status"], check=False
            )
            assert result == ""

    @pytest.mark.asyncio
    async def test_execute_command_file_not_found(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test command execution when git is not found."""
        with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError()):
            with pytest.raises(GitCommandError) as exc_info:
                await git_client.execute_command(
                    temp_repo_path, ["status"], ctx=mock_context
                )

            assert "Git command not found" in exc_info.value.stderr
            assert exc_info.value.return_code == -1
            mock_context.error.assert_called()

    @pytest.mark.asyncio
    async def test_execute_command_unexpected_error(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test command execution with unexpected error."""
        with patch(
            "asyncio.create_subprocess_exec", side_effect=RuntimeError("Unexpected")
        ):
            with pytest.raises(GitCommandError) as exc_info:
                await git_client.execute_command(
                    temp_repo_path, ["status"], ctx=mock_context
                )

            assert "Unexpected" in exc_info.value.stderr
            assert exc_info.value.return_code == -1
            mock_context.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_status_success(self, git_client, temp_repo_path, mock_context):
        """Test successful git status retrieval."""
        status_output = " M file1.py\n?? file2.py\nA  file3.py"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(status_output.encode(), b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_status(temp_repo_path, mock_context)

            assert "files" in result
            assert len(result["files"]) == 3
            # Check file structure
            for file_info in result["files"]:
                assert "filename" in file_info
                assert "status_code" in file_info
                assert "index_status" in file_info or "working_status" in file_info
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_get_status_clean_repo(self, git_client, temp_repo_path):
        """Test git status on clean repository."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_status(temp_repo_path)

            assert len(result["files"]) == 0

    @pytest.mark.asyncio
    async def test_get_status_with_rename(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test git status with renamed files."""
        status_output = "R  old_name.py -> new_name.py\n M modified.py"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(status_output.encode(), b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_status(temp_repo_path, mock_context)

            assert len(result["files"]) == 2
            rename_file = next(
                f for f in result["files"] if f["filename"] == "new_name.py"
            )
            assert rename_file["index_status"] == "R"
            assert rename_file["working_status"] is None

    @pytest.mark.asyncio
    async def test_get_status_compact_format(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test git status with compact format (no space separator)."""
        status_output = "MMfile.py\nA file2.py"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(status_output.encode(), b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_status(temp_repo_path, mock_context)

            assert len(result["files"]) == 2
            mm_file = next(f for f in result["files"] if f["filename"] == "file.py")
            assert mm_file["index_status"] == "M"
            assert mm_file["working_status"] == "M"

    @pytest.mark.asyncio
    async def test_get_status_failure(self, git_client, temp_repo_path, mock_context):
        """Test git status failure."""
        mock_process = Mock()
        mock_process.returncode = 128
        mock_process.communicate = AsyncMock(
            return_value=(b"", b"fatal: not a git repository\n")
        )

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            with pytest.raises(GitCommandError):
                await git_client.get_status(temp_repo_path, mock_context)
            mock_context.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_status_file_not_found(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test git status when git is not found."""
        with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError()):
            with pytest.raises(GitCommandError) as exc_info:
                await git_client.get_status(temp_repo_path, mock_context)

            assert "Git command not found" in exc_info.value.stderr
            mock_context.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_status_unexpected_error(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test git status with unexpected error."""
        with patch(
            "asyncio.create_subprocess_exec", side_effect=RuntimeError("Unexpected")
        ):
            with pytest.raises(GitCommandError) as exc_info:
                await git_client.get_status(temp_repo_path, mock_context)

            assert "Unexpected" in exc_info.value.stderr
            mock_context.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_diff_success(self, git_client, temp_repo_path, mock_context):
        """Test successful diff retrieval."""
        diff_output = """diff --git a/file.py b/file.py
index 1234567..abcdefg 100644
--- a/file.py
+++ b/file.py
@@ -1,3 +1,4 @@
 def hello():
+    print("world")
     pass
"""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(diff_output.encode(), b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_diff(
                temp_repo_path, staged=False, file_path="file.py", ctx=mock_context
            )

            assert isinstance(result, str)
            assert "diff --git" in result
            assert "file.py" in result
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_get_diff_staged(self, git_client, temp_repo_path, mock_context):
        """Test staged diff retrieval."""
        diff_output = "diff --cached output"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(diff_output.encode(), b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_diff(
                temp_repo_path, staged=True, ctx=mock_context
            )

            assert result == diff_output
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_get_diff_no_changes(self, git_client, temp_repo_path):
        """Test diff retrieval with no changes."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_diff(temp_repo_path, staged=False)

            assert result == ""
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_diff_stats_success(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test successful diff stats retrieval."""
        # Mock the status check first
        status_output = " M test.py"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(status_output.encode(), b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_diff_stats(
                temp_repo_path, file_path="test.py", ctx=mock_context
            )

            assert "lines_added" in result
            assert "lines_deleted" in result
            assert "is_binary" in result
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_get_diff_stats_binary_file(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test diff stats for binary file."""
        # Mock numstat output for binary file
        numstat_output = "-\t-\tbinary_file.bin"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(
            return_value=(numstat_output.encode(), b"")
        )

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_diff_stats(
                temp_repo_path,
                file_path="binary_file.bin",
                staged=False,
                ctx=mock_context,
            )

            assert result["is_binary"] is True
            assert result["lines_added"] == 0
            assert result["lines_deleted"] == 0

    @pytest.mark.asyncio
    async def test_get_diff_stats_staged_file(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test diff stats for staged file."""
        # Mock status to indicate staged file
        status_output = "M  staged_file.py"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(status_output.encode(), b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_diff_stats(
                temp_repo_path, file_path="staged_file.py", ctx=mock_context
            )

            assert "lines_added" in result
            assert "lines_deleted" in result
            assert "is_binary" in result

    @pytest.mark.asyncio
    async def test_get_diff_stats_fallback_command(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test diff stats with fallback command."""

        # Mock first command to fail, second to succeed
        def create_mock_process(output, returncode=0):
            mock_process = Mock()
            mock_process.returncode = returncode
            mock_process.communicate = AsyncMock(return_value=(output.encode(), b""))
            return mock_process

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            # First command fails
            mock_exec.side_effect = [
                create_mock_process("", returncode=1),  # First command fails
                create_mock_process("10\t5\ttest.py"),  # Second command succeeds
            ]

            result = await git_client.get_diff_stats(
                temp_repo_path, file_path="test.py", staged=True, ctx=mock_context
            )

            assert result["lines_added"] == 10
            assert result["lines_deleted"] == 5
            assert result["is_binary"] is False

    @pytest.mark.asyncio
    async def test_get_diff_stats_no_output(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test diff stats with no output."""
        # Mock status to indicate file exists
        status_output = " M test.py"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(status_output.encode(), b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_diff_stats(
                temp_repo_path, file_path="test.py", ctx=mock_context
            )

            assert result["lines_added"] == 0
            assert result["lines_deleted"] == 0
            assert result["is_binary"] is False

    @pytest.mark.asyncio
    async def test_get_diff_stats_parse_error(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test diff stats with parsing error."""
        # Mock status to indicate file exists
        # Mock numstat output that can't be parsed
        numstat_output = "invalid\tformat\ttest.py"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(
            return_value=(numstat_output.encode(), b"")
        )

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_diff_stats(
                temp_repo_path, file_path="test.py", ctx=mock_context
            )

            assert result["lines_added"] == 0
            assert result["lines_deleted"] == 0
            assert result["is_binary"] is False
            mock_context.warning.assert_called()

    @pytest.mark.asyncio
    async def test_get_diff_stats_exception_handling(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test diff stats exception handling."""
        with patch(
            "asyncio.create_subprocess_exec", side_effect=RuntimeError("Test error")
        ):
            result = await git_client.get_diff_stats(
                temp_repo_path, file_path="test.py", ctx=mock_context
            )

            assert result["lines_added"] == 0
            assert result["lines_deleted"] == 0
            assert result["is_binary"] is False
            mock_context.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_unpushed_commits_success(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test successful unpushed commits retrieval."""
        # Mock current branch
        branch_output = "main"
        # Mock unpushed commits
        commits_output = '{"sha":"abc123","message":"Test commit","author":"Test User","email":"test@example.com","date":"2024-01-01"}'

        def create_mock_process(output):
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(output.encode(), b""))
            return mock_process

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.side_effect = [
                create_mock_process(branch_output),
                create_mock_process(commits_output),
            ]

            result = await git_client.get_unpushed_commits(
                temp_repo_path, remote="origin", ctx=mock_context
            )

            assert len(result) == 1
            assert result[0]["sha"] == "abc123"
            assert result[0]["message"] == "Test commit"
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_get_unpushed_commits_upstream_not_found(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test unpushed commits when upstream doesn't exist."""
        # Mock current branch
        branch_output = "feature"
        # Mock first command to fail (upstream not found)
        # Mock second command to succeed (recent commits)
        commits_output = '{"sha":"def456","message":"Recent commit","author":"User","email":"user@example.com","date":"2024-01-01"}'

        def create_mock_process(output, returncode=0):
            mock_process = Mock()
            mock_process.returncode = returncode
            mock_process.communicate = AsyncMock(return_value=(output.encode(), b""))
            return mock_process

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.side_effect = [
                create_mock_process(branch_output),
                create_mock_process("", returncode=1),  # Upstream check fails
                create_mock_process(commits_output),  # Recent commits
            ]

            result = await git_client.get_unpushed_commits(
                temp_repo_path, remote="origin", ctx=mock_context
            )

            assert len(result) == 1
            assert result[0]["sha"] == "def456"
            mock_context.warning.assert_called()

    @pytest.mark.asyncio
    async def test_get_unpushed_commits_json_parse_error(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test unpushed commits with JSON parse error."""
        # Mock current branch
        branch_output = "main"
        # Mock invalid JSON output
        commits_output = '{"invalid": json}'

        def create_mock_process(output):
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(output.encode(), b""))
            return mock_process

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.side_effect = [
                create_mock_process(branch_output),
                create_mock_process(commits_output),
            ]

            result = await git_client.get_unpushed_commits(
                temp_repo_path, remote="origin", ctx=mock_context
            )

            assert len(result) == 0
            mock_context.warning.assert_called()

    @pytest.mark.asyncio
    async def test_get_unpushed_commits_git_error(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test unpushed commits with git error."""
        with patch(
            "asyncio.create_subprocess_exec",
            side_effect=GitCommandError(["git", "log"], 1, "Error"),
        ):
            result = await git_client.get_unpushed_commits(
                temp_repo_path, remote="origin", ctx=mock_context
            )

            assert len(result) == 0
            mock_context.warning.assert_called()

    @pytest.mark.asyncio
    async def test_get_stash_list_success(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test successful stash list retrieval."""
        stash_output = "stash@{0}|WIP on main: 1234567 Last commit|2 hours ago\nstash@{1}|WIP on feature: abcdefg Feature work|1 day ago"

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(stash_output.encode(), b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_stash_list(temp_repo_path, ctx=mock_context)

            assert len(result) == 2
            assert result[0]["index"] == 0
            assert result[0]["name"] == "stash@{0}"
            assert result[0]["message"] == "WIP on main: 1234567 Last commit"
            assert result[0]["date"] == "2 hours ago"
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_get_stash_list_empty(self, git_client, temp_repo_path, mock_context):
        """Test stash list when no stashes exist."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.get_stash_list(temp_repo_path, ctx=mock_context)

            assert len(result) == 0
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_get_stash_list_git_error(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test stash list with git error."""
        with patch(
            "asyncio.create_subprocess_exec",
            side_effect=GitCommandError(["git", "stash"], 1, "Error"),
        ):
            result = await git_client.get_stash_list(temp_repo_path, ctx=mock_context)

            assert len(result) == 0
            mock_context.warning.assert_called()

    @pytest.mark.asyncio
    async def test_get_branch_info_success(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test successful branch info retrieval."""

        def create_mock_process(output):
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(output.encode(), b""))
            return mock_process

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.side_effect = [
                create_mock_process("main"),  # current branch
                create_mock_process("origin/main"),  # upstream branch
                create_mock_process("2 1"),  # ahead/behind counts
                create_mock_process("abc1234567890abcdef"),  # HEAD commit
            ]

            result = await git_client.get_branch_info(temp_repo_path, ctx=mock_context)

            assert result["current_branch"] == "main"
            assert result["upstream"] == "origin/main"
            assert result["ahead"] == 1
            assert result["behind"] == 2
            assert result["head_commit"] == "abc1234567890abcdef"
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_get_branch_info_no_upstream(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test branch info when no upstream is configured."""

        def create_mock_process(output, returncode=0):
            mock_process = Mock()
            mock_process.returncode = returncode
            mock_process.communicate = AsyncMock(return_value=(output.encode(), b""))
            return mock_process

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.side_effect = [
                create_mock_process("main"),  # current branch
                create_mock_process("", returncode=1),  # upstream check fails
                create_mock_process("abc1234567890abcdef"),  # HEAD commit
            ]

            result = await git_client.get_branch_info(temp_repo_path, ctx=mock_context)

            assert result["current_branch"] == "main"
            assert result["upstream"] is None
            assert result["ahead"] == 0
            assert result["behind"] == 0
            assert result["head_commit"] == "abc1234567890abcdef"
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_get_branch_info_ahead_behind_parse_error(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test branch info with ahead/behind parse error."""

        def create_mock_process(output, returncode=0):
            mock_process = Mock()
            mock_process.returncode = returncode
            mock_process.communicate = AsyncMock(return_value=(output.encode(), b""))
            return mock_process

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.side_effect = [
                create_mock_process("main"),  # current branch
                create_mock_process("origin/main"),  # upstream branch
                create_mock_process("invalid format"),  # invalid ahead/behind
                create_mock_process("abc1234567890abcdef"),  # HEAD commit
            ]

            result = await git_client.get_branch_info(temp_repo_path, ctx=mock_context)

            assert result["current_branch"] == "main"
            assert result["upstream"] == "origin/main"
            assert result["ahead"] == 0
            assert result["behind"] == 0
            assert result["head_commit"] == "abc1234567890abcdef"
            mock_context.warning.assert_called()

    @pytest.mark.asyncio
    async def test_get_branch_info_head_commit_error(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test branch info when HEAD commit retrieval fails."""

        def create_mock_process(output, returncode=0):
            mock_process = Mock()
            mock_process.returncode = returncode
            mock_process.communicate = AsyncMock(return_value=(output.encode(), b""))
            return mock_process

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.side_effect = [
                create_mock_process("main"),  # current branch
                create_mock_process("origin/main"),  # upstream branch
                create_mock_process("2 1"),  # ahead/behind counts
                create_mock_process("", returncode=1),  # HEAD commit fails
            ]

            result = await git_client.get_branch_info(temp_repo_path, ctx=mock_context)

            assert result["current_branch"] == "main"
            assert result["upstream"] == "origin/main"
            assert result["ahead"] == 1
            assert result["behind"] == 2
            assert result["head_commit"] == "unknown"
            mock_context.warning.assert_called()

    @pytest.mark.asyncio
    async def test_get_branch_info_git_error(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test branch info with git error."""
        with patch(
            "asyncio.create_subprocess_exec",
            side_effect=GitCommandError(["git", "branch"], 1, "Error"),
        ):
            result = await git_client.get_branch_info(temp_repo_path, ctx=mock_context)

            assert result["current_branch"] == "unknown"
            assert result["upstream"] is None
            assert result["ahead"] == 0
            assert result["behind"] == 0
            assert result["head_commit"] == "unknown"
            mock_context.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_repository_info_success(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test successful repository info retrieval."""

        def create_mock_process(output, returncode=0):
            mock_process = Mock()
            mock_process.returncode = returncode
            mock_process.communicate = AsyncMock(return_value=(output.encode(), b""))
            return mock_process

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            # Mock the bare repository check to fail (indicating non-bare repo)
            mock_exec.side_effect = [
                create_mock_process(
                    "false", returncode=1
                ),  # is-bare-repository (fails = non-bare)
                create_mock_process(
                    "origin\thttps://github.com/user/repo.git\t(fetch)\norigin\thttps://github.com/user/repo.git\t(push)"
                ),  # remote -v
                create_mock_process(" M file.py"),  # status --porcelain
            ]

            result = await git_client.get_repository_info(
                temp_repo_path, ctx=mock_context
            )

            assert result["is_bare"] is False
            assert result["is_dirty"] is True
            assert "origin" in result["remotes"]
            assert result["root_path"] == str(temp_repo_path)
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_get_repository_info_bare_repo(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test repository info for bare repository."""

        def create_mock_process(output, returncode=0):
            mock_process = Mock()
            mock_process.returncode = returncode
            mock_process.communicate = AsyncMock(return_value=(output.encode(), b""))
            return mock_process

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.side_effect = [
                create_mock_process("true"),  # is-bare-repository (success = bare)
                create_mock_process(""),  # no remotes
                create_mock_process(""),  # clean status
            ]

            result = await git_client.get_repository_info(
                temp_repo_path, ctx=mock_context
            )

            assert result["is_bare"] is True
            assert result["is_dirty"] is False
            assert len(result["remotes"]) == 0
            assert result["root_path"] == str(temp_repo_path)

    @pytest.mark.asyncio
    async def test_get_repository_info_no_remotes(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test repository info when no remotes are configured."""

        def create_mock_process(output, returncode=0):
            mock_process = Mock()
            mock_process.returncode = returncode
            mock_process.communicate = AsyncMock(return_value=(output.encode(), b""))
            return mock_process

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.side_effect = [
                create_mock_process(
                    "false", returncode=1
                ),  # is-bare-repository (fails = non-bare)
                create_mock_process("", returncode=1),  # remote -v fails
                create_mock_process(""),  # clean status
            ]

            result = await git_client.get_repository_info(
                temp_repo_path, ctx=mock_context
            )

            assert result["is_bare"] is False
            assert result["is_dirty"] is False
            assert len(result["remotes"]) == 0
            assert result["root_path"] == str(temp_repo_path)
            mock_context.debug.assert_called()

    @pytest.mark.asyncio
    async def test_get_repository_info_exception_handling(
        self, git_client, temp_repo_path, mock_context
    ):
        """Test repository info exception handling."""
        with patch(
            "asyncio.create_subprocess_exec", side_effect=RuntimeError("Test error")
        ):
            result = await git_client.get_repository_info(
                temp_repo_path, ctx=mock_context
            )

            assert result["is_bare"] is False
            assert result["is_dirty"] is False
            assert len(result["remotes"]) == 0
            assert result["root_path"] == str(temp_repo_path)
            mock_context.error.assert_called()

    @pytest.mark.asyncio
    async def test_command_with_timeout_handling(self, git_client, temp_repo_path):
        """Test command execution handles timeouts gracefully."""
        # Mock a process that times out
        mock_process = Mock()
        mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError())

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_process
        ), pytest.raises(GitCommandError):
            await git_client.execute_command(temp_repo_path, ["status"])

    @pytest.mark.asyncio
    async def test_context_logging(self, git_client, temp_repo_path, mock_context):
        """Test that context logging works properly."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"test output\n", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.execute_command(
                temp_repo_path, ["log", "--oneline", "-1"], ctx=mock_context
            )

            assert result == "test output"
            # Verify debug was called for command execution
            mock_context.debug.assert_called()
            debug_calls = [call.args[0] for call in mock_context.debug.call_args_list]
            assert any("Executing git command" in call for call in debug_calls)
            assert any("Git command output" in call for call in debug_calls)

    @pytest.mark.asyncio
    async def test_binary_output_handling(self, git_client, temp_repo_path):
        """Test handling of binary data in git output."""
        # Mock binary output (e.g., from git show on binary file)
        binary_output = b"\x00\x01\x02\xff\xfe\xfd some text\n"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(binary_output, b""))

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_process
        ), pytest.raises(GitCommandError):
            # Should raise GitCommandError due to decode failure
            await git_client.execute_command(
                temp_repo_path, ["show", "HEAD:binary.file"]
            )

    @pytest.mark.asyncio
    async def test_large_output_handling(self, git_client, temp_repo_path):
        """Test handling of large git command output."""
        # Simulate large output
        large_output = "line\n" * 10000  # 10k lines
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(large_output.encode(), b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await git_client.execute_command(
                temp_repo_path, ["log", "--oneline"]
            )

            assert len(result.split("\n")) > 5000  # Should handle large output
            assert result.endswith("line")  # Should preserve content


@pytest.mark.integration
class TestGitClientIntegration:
    """Integration tests for GitClient (requires actual git)."""

    @pytest.mark.asyncio
    async def test_real_git_status_clean(self, git_client, tmp_path):
        """Test with real git repository - clean status."""
        # Skip if git not available
        pytest.importorskip("subprocess")

        import subprocess

        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()

        try:
            # Initialize git repo
            subprocess.run(
                ["git", "init"], cwd=repo_path, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.email", "test@test.com"],
                cwd=repo_path,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True
            )

            # Test status on clean repo
            result = await git_client.get_status(repo_path)
            assert "files" in result
            assert len(result["files"]) == 0

        except subprocess.CalledProcessError:
            pytest.skip("Git not available or failed to setup test repo")
        except FileNotFoundError:
            pytest.skip("Git command not found")
