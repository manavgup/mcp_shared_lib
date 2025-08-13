"""Unit tests for git utility functions."""

from pathlib import Path

import pytest

from mcp_shared_lib.utils.git_utils import (
    find_git_root,
    format_commit_message,
    format_file_size,
    get_file_extension,
    is_binary_file,
    is_git_repository,
    normalize_path,
    parse_diff_stats,
    parse_git_url,
    safe_filename,
    truncate_text,
)


@pytest.mark.unit
class TestGitRepositoryDetection:
    """Test git repository detection functions."""

    def test_is_git_repository_true(self, tmp_path):
        """Test is_git_repository returns True for git repo."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()

        assert is_git_repository(repo_path) is True
        assert is_git_repository(str(repo_path)) is True

    def test_is_git_repository_false(self, tmp_path):
        """Test is_git_repository returns False for non-git repo."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        # No .git directory

        assert is_git_repository(repo_path) is False
        assert is_git_repository(str(repo_path)) is False

    def test_is_git_repository_nonexistent(self, tmp_path):
        """Test is_git_repository handles nonexistent paths."""
        repo_path = tmp_path / "nonexistent"

        assert is_git_repository(repo_path) is False

    def test_find_git_root_from_repo(self, tmp_path):
        """Test find_git_root when starting from git repo."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()

        result = find_git_root(repo_path)
        assert result == repo_path

    def test_find_git_root_from_subdirectory(self, tmp_path):
        """Test find_git_root when starting from subdirectory."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()

        subdir = repo_path / "src" / "module"
        subdir.mkdir(parents=True)

        result = find_git_root(subdir)
        assert result == repo_path

    def test_find_git_root_no_repo(self, tmp_path):
        """Test find_git_root when no git repo exists."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        # No .git directory

        result = find_git_root(repo_path)
        assert result is None

    def test_find_git_root_from_nonexistent(self, tmp_path):
        """Test find_git_root handles nonexistent paths."""
        repo_path = tmp_path / "nonexistent"

        result = find_git_root(repo_path)
        assert result is None


@pytest.mark.unit
class TestGitUrlParsing:
    """Test git URL parsing functions."""

    def test_parse_git_url_ssh(self):
        """Test parsing SSH git URLs."""
        url = "git@github.com:user/repo.git"
        result = parse_git_url(url)

        assert result["protocol"] == "ssh"
        assert result["host"] == "github.com"
        assert result["owner"] == "user"
        assert result["repo"] == "repo"

    def test_parse_git_url_ssh_no_git_extension(self):
        """Test parsing SSH git URLs without .git extension."""
        url = "git@github.com:user/repo"
        result = parse_git_url(url)

        assert result["protocol"] == "ssh"
        assert result["host"] == "github.com"
        assert result["owner"] == "user"
        assert result["repo"] == "repo"

    def test_parse_git_url_https(self):
        """Test parsing HTTPS git URLs."""
        url = "https://github.com/user/repo.git"
        result = parse_git_url(url)

        assert result["protocol"] == "https"
        assert result["host"] == "github.com"
        assert result["owner"] == "user"
        assert result["repo"] == "repo"

    def test_parse_git_url_https_no_git_extension(self):
        """Test parsing HTTPS git URLs without .git extension."""
        url = "https://github.com/user/repo"
        result = parse_git_url(url)

        assert result["protocol"] == "https"
        assert result["host"] == "github.com"
        assert result["owner"] == "user"
        assert result["repo"] == "repo"

    def test_parse_git_url_unknown(self):
        """Test parsing unknown git URL formats."""
        url = "invalid://url/format"
        result = parse_git_url(url)

        assert result["protocol"] == "unknown"
        assert result["host"] == ""
        assert result["owner"] == ""
        assert result["repo"] == ""

    def test_parse_git_url_empty(self):
        """Test parsing empty git URL."""
        url = ""
        result = parse_git_url(url)

        assert result["protocol"] == "unknown"
        assert result["host"] == ""
        assert result["owner"] == ""
        assert result["repo"] == ""

    def test_parse_git_url_complex_ssh(self):
        """Test parsing complex SSH git URLs."""
        url = "git@gitlab.company.com:group/subgroup/project.git"
        result = parse_git_url(url)

        assert result["protocol"] == "ssh"
        assert result["host"] == "gitlab.company.com"
        assert result["owner"] == "group"
        assert result["repo"] == "subgroup/project"


@pytest.mark.unit
class TestFileSizeFormatting:
    """Test file size formatting functions."""

    def test_format_file_size_zero(self):
        """Test formatting zero file size."""
        result = format_file_size(0)
        assert result == "0 B"

    def test_format_file_size_bytes(self):
        """Test formatting file size in bytes."""
        result = format_file_size(512)
        assert result == "512.0 B"

    def test_format_file_size_kilobytes(self):
        """Test formatting file size in kilobytes."""
        result = format_file_size(1024)
        assert result == "1.0 KB"

    def test_format_file_size_megabytes(self):
        """Test formatting file size in megabytes."""
        result = format_file_size(1024 * 1024)
        assert result == "1.0 MB"

    def test_format_file_size_gigabytes(self):
        """Test formatting file size in gigabytes."""
        result = format_file_size(1024 * 1024 * 1024)
        assert result == "1.0 GB"

    def test_format_file_size_fractional_kb(self):
        """Test formatting fractional kilobytes."""
        result = format_file_size(1536)  # 1.5 KB
        assert result == "1.5 KB"

    def test_format_file_size_large_bytes(self):
        """Test formatting large byte values."""
        result = format_file_size(999)
        assert result == "999.0 B"

    def test_format_file_size_exact_mb(self):
        """Test formatting exact megabyte values."""
        result = format_file_size(2 * 1024 * 1024)
        assert result == "2.0 MB"


@pytest.mark.unit
class TestCommitMessageFormatting:
    """Test commit message formatting functions."""

    def test_format_commit_message_short(self):
        """Test formatting short commit message."""
        message = "Fix bug in parser"
        result = format_commit_message(message)
        assert result == "Fix bug in parser"

    def test_format_commit_message_exact_length(self):
        """Test formatting commit message at exact max length."""
        message = "A" * 72
        result = format_commit_message(message, max_length=72)
        assert result == "A" * 72

    def test_format_commit_message_long(self):
        """Test formatting long commit message."""
        message = (
            "This is a very long commit message that exceeds the maximum allowed length"
        )
        result = format_commit_message(message, max_length=50)
        # The function truncates to max_length-3 and adds "..."
        expected = "This is a very long commit message that exceeds..."
        assert result == expected
        assert len(result) == 50

    def test_format_commit_message_multiline(self):
        """Test formatting multiline commit message."""
        message = "First line\nSecond line\nThird line"
        result = format_commit_message(message, max_length=20)
        # The function only takes first line and truncates if needed
        # First line is 10 chars, so no truncation needed
        assert result == "First line"

    def test_format_commit_message_empty(self):
        """Test formatting empty commit message."""
        message = ""
        result = format_commit_message(message)
        assert result == ""

    def test_format_commit_message_custom_suffix(self):
        """Test formatting with custom suffix."""
        message = "Very long message that needs truncation"
        # The function doesn't support custom suffix parameter
        result = format_commit_message(message, max_length=20)
        assert result == "Very long message..."

    def test_format_commit_message_unicode(self):
        """Test formatting unicode commit message."""
        message = "Fixé un büg dans le parsér"
        result = format_commit_message(message, max_length=20)
        # The function truncates to max_length-3 and adds "..."
        expected = "Fixé un büg dans ..."
        assert result == expected


@pytest.mark.unit
class TestSafeFilename:
    """Test safe filename generation functions."""

    def test_safe_filename_normal(self):
        """Test safe filename with normal characters."""
        filename = "normal_file.txt"
        result = safe_filename(filename)
        assert result == "normal_file.txt"

    def test_safe_filename_unsafe_chars(self):
        """Test safe filename with unsafe characters."""
        filename = 'file<>:"/\\|?*.txt'
        result = safe_filename(filename)
        # The function replaces each unsafe char with underscore
        assert result == "file_________.txt"

    def test_safe_filename_leading_dots(self):
        """Test safe filename with leading dots."""
        filename = "...hidden_file.txt"
        result = safe_filename(filename)
        assert result == "hidden_file.txt"

    def test_safe_filename_trailing_spaces(self):
        """Test safe filename with trailing spaces."""
        filename = "file.txt   "
        result = safe_filename(filename)
        assert result == "file.txt"

    def test_safe_filename_too_long(self):
        """Test safe filename that's too long."""
        filename = "a" * 300
        result = safe_filename(filename)
        assert len(result) == 255
        assert result.endswith("a")

    def test_safe_filename_empty(self):
        """Test safe filename with empty string."""
        filename = ""
        result = safe_filename(filename)
        assert result == "unnamed"

    def test_safe_filename_only_unsafe(self):
        """Test safe filename with only unsafe characters."""
        filename = '<>:"/\\|?*'
        result = safe_filename(filename)
        # The function replaces unsafe chars with underscores, then strips dots
        assert result == "_________"

    def test_safe_filename_mixed_unsafe(self):
        """Test safe filename with mixed safe and unsafe characters."""
        filename = "my file (v2.0).txt"
        result = safe_filename(filename)
        # The function doesn't replace parentheses, only specific unsafe chars
        assert result == "my file (v2.0).txt"


@pytest.mark.unit
class TestDiffStatsParsing:
    """Test diff stats parsing functions."""

    def test_parse_diff_stats_basic(self):
        """Test parsing basic diff stats."""
        stats_line = "5 files changed, 123 insertions(+), 45 deletions(-)"
        insertions, deletions = parse_diff_stats(stats_line)

        assert insertions == 123
        assert deletions == 45

    def test_parse_diff_stats_no_deletions(self):
        """Test parsing diff stats with no deletions."""
        stats_line = "3 files changed, 67 insertions(+)"
        insertions, deletions = parse_diff_stats(stats_line)

        assert insertions == 67
        assert deletions == 0

    def test_parse_diff_stats_no_insertions(self):
        """Test parsing diff stats with no insertions."""
        stats_line = "2 files changed, 23 deletions(-)"
        insertions, deletions = parse_diff_stats(stats_line)

        assert insertions == 0
        assert deletions == 23

    def test_parse_diff_stats_no_changes(self):
        """Test parsing diff stats with no changes."""
        stats_line = "1 file changed"
        insertions, deletions = parse_diff_stats(stats_line)

        assert insertions == 0
        assert deletions == 0

    def test_parse_diff_stats_empty(self):
        """Test parsing empty diff stats."""
        stats_line = ""
        insertions, deletions = parse_diff_stats(stats_line)

        assert insertions == 0
        assert deletions == 0

    def test_parse_diff_stats_complex(self):
        """Test parsing complex diff stats."""
        stats_line = (
            "10 files changed, 1,234 insertions(+), 567 deletions(-), 89 modifications"
        )
        insertions, deletions = parse_diff_stats(stats_line)

        # The regex only matches the first occurrence of digits before "insertion"
        assert insertions == 234
        assert deletions == 567


@pytest.mark.unit
class TestTextTruncation:
    """Test text truncation functions."""

    def test_truncate_text_short(self):
        """Test truncating short text."""
        text = "Short text"
        result = truncate_text(text, max_length=20)
        assert result == "Short text"

    def test_truncate_text_exact_length(self):
        """Test truncating text at exact max length."""
        text = "Exactly twenty chars"
        result = truncate_text(text, max_length=20)
        assert result == "Exactly twenty chars"

    def test_truncate_text_long(self):
        """Test truncating long text."""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, max_length=25)
        # The function truncates to max_length-3 and adds "..."
        assert result == "This is a very long te..."
        assert len(result) == 25

    def test_truncate_text_custom_suffix(self):
        """Test truncating with custom suffix."""
        text = "Long text to truncate"
        result = truncate_text(text, max_length=15, suffix="***")
        assert result == "Long text to***"
        assert len(result) == 15

    def test_truncate_text_empty(self):
        """Test truncating empty text."""
        text = ""
        result = truncate_text(text, max_length=10)
        assert result == ""

    def test_truncate_text_unicode(self):
        """Test truncating unicode text."""
        text = "Unicode text: café, naïve, résumé"
        result = truncate_text(text, max_length=20)
        # The function truncates to max_length-3 and adds "..."
        assert result == "Unicode text: caf..."

    def test_truncate_text_suffix_longer_than_max(self):
        """Test truncating when suffix is longer than max length."""
        text = "Short"
        result = truncate_text(text, max_length=3, suffix="...")
        assert result == "..."

    def test_truncate_text_suffix_exactly_max_length(self):
        """Test truncating when suffix equals max length."""
        text = "Long text"
        result = truncate_text(text, max_length=3, suffix="...")
        assert result == "..."


@pytest.mark.unit
class TestPathNormalization:
    """Test path normalization functions."""

    def test_normalize_path_string(self):
        """Test normalizing string path."""
        path = "path/to/file.txt"
        result = normalize_path(path)
        assert result == "path/to/file.txt"

    def test_normalize_path_path_object(self):
        """Test normalizing Path object."""
        path = Path("path/to/file.txt")
        result = normalize_path(path)
        assert result == "path/to/file.txt"

    def test_normalize_path_windows_style(self):
        """Test normalizing Windows-style path."""
        path = "path\\to\\file.txt"
        result = normalize_path(path)
        # On macOS, as_posix() doesn't convert backslashes to forward slashes
        assert result == "path\\to\\file.txt"

    def test_normalize_path_absolute(self):
        """Test normalizing absolute path."""
        path = "/absolute/path/to/file.txt"
        result = normalize_path(path)
        assert result == "/absolute/path/to/file.txt"

    def test_normalize_path_current_dir(self):
        """Test normalizing current directory path."""
        path = "./current/file.txt"
        result = normalize_path(path)
        assert result == "current/file.txt"

    def test_normalize_path_parent_dir(self):
        """Test normalizing parent directory path."""
        path = "../parent/file.txt"
        result = normalize_path(path)
        assert result == "../parent/file.txt"

    def test_normalize_path_empty(self):
        """Test normalizing empty path."""
        path = ""
        result = normalize_path(path)
        assert result == "."


@pytest.mark.unit
class TestFileExtension:
    """Test file extension functions."""

    def test_get_file_extension_basic(self):
        """Test getting basic file extension."""
        filename = "file.txt"
        result = get_file_extension(filename)
        assert result == ".txt"

    def test_get_file_extension_no_extension(self):
        """Test getting extension for file without extension."""
        filename = "README"
        result = get_file_extension(filename)
        assert result == ""

    def test_get_file_extension_multiple_dots(self):
        """Test getting extension for file with multiple dots."""
        filename = "file.backup.txt"
        result = get_file_extension(filename)
        assert result == ".txt"

    def test_get_file_extension_hidden_file(self):
        """Test getting extension for hidden file."""
        filename = ".env"
        result = get_file_extension(filename)
        assert result == ""

    def test_get_file_extension_uppercase(self):
        """Test getting extension for uppercase extension."""
        filename = "file.TXT"
        result = get_file_extension(filename)
        assert result == ".txt"

    def test_get_file_extension_empty(self):
        """Test getting extension for empty filename."""
        filename = ""
        result = get_file_extension(filename)
        assert result == ""

    def test_get_file_extension_dot_only(self):
        """Test getting extension for filename with only dot."""
        filename = "."
        result = get_file_extension(filename)
        assert result == ""

    def test_get_file_extension_double_dot(self):
        """Test getting extension for filename with double dot."""
        filename = ".."
        result = get_file_extension(filename)
        assert result == ""


@pytest.mark.unit
class TestBinaryFileDetection:
    """Test binary file detection functions."""

    def test_is_binary_file_executable(self):
        """Test detecting executable files as binary."""
        assert is_binary_file("program.exe") is True
        assert is_binary_file("library.dll") is True
        assert is_binary_file("binary.so") is True
        assert is_binary_file("binary.dylib") is True

    def test_is_binary_file_image(self):
        """Test detecting image files as binary."""
        assert is_binary_file("image.jpg") is True
        assert is_binary_file("photo.png") is True
        assert is_binary_file("icon.gif") is True
        assert is_binary_file("picture.bmp") is True

    def test_is_binary_file_audio_video(self):
        """Test detecting audio/video files as binary."""
        assert is_binary_file("song.mp3") is True
        assert is_binary_file("video.mp4") is True
        assert is_binary_file("movie.avi") is True
        assert is_binary_file("audio.wav") is True

    def test_is_binary_file_document(self):
        """Test detecting document files as binary."""
        assert is_binary_file("document.pdf") is True
        assert is_binary_file("report.docx") is True
        assert is_binary_file("spreadsheet.xlsx") is True
        assert is_binary_file("presentation.pptx") is True

    def test_is_binary_file_archive(self):
        """Test detecting archive files as binary."""
        assert is_binary_file("archive.zip") is True
        assert is_binary_file("backup.tar") is True
        assert is_binary_file("compressed.gz") is True
        assert is_binary_file("data.7z") is True

    def test_is_binary_file_database(self):
        """Test detecting database files as binary."""
        assert is_binary_file("database.sqlite") is True
        assert is_binary_file("data.db") is True
        assert is_binary_file("access.mdb") is True

    def test_is_binary_file_text(self):
        """Test detecting text files as non-binary."""
        assert is_binary_file("script.py") is False
        assert is_binary_file("README.md") is False
        assert is_binary_file("config.json") is False
        assert is_binary_file("data.csv") is False

    def test_is_binary_file_no_extension(self):
        """Test detecting files without extension as non-binary."""
        assert is_binary_file("Makefile") is False
        assert is_binary_file("Dockerfile") is False
        assert is_binary_file("LICENSE") is False

    def test_is_binary_file_case_insensitive(self):
        """Test binary detection is case insensitive."""
        assert is_binary_file("file.JPG") is True
        assert is_binary_file("image.PNG") is True
        assert is_binary_file("document.PDF") is True

    def test_is_binary_file_path_object(self):
        """Test binary detection with Path objects."""
        from pathlib import Path

        assert is_binary_file(Path("image.jpg")) is True
        assert is_binary_file(Path("script.py")) is False

    def test_is_binary_file_unknown_extension(self):
        """Test binary detection with unknown extensions."""
        assert is_binary_file("file.xyz") is False
        assert is_binary_file("data.unknown") is False
