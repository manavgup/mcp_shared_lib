"""Tests for file_utils module."""

from pathlib import Path

import pytest

from mcp_shared_lib.utils.file_utils import get_file_extension, is_binary_file


@pytest.mark.unit
class TestFileExtension:
    """Test get_file_extension function."""

    def test_get_file_extension_basic(self):
        """Test basic file extension extraction."""
        assert get_file_extension("file.txt") == ".txt"
        assert get_file_extension("document.pdf") == ".pdf"
        assert get_file_extension("script.py") == ".py"

    def test_get_file_extension_uppercase(self):
        """Test uppercase extension conversion to lowercase."""
        assert get_file_extension("FILE.TXT") == ".txt"
        assert get_file_extension("Document.PDF") == ".pdf"
        assert get_file_extension("Script.PY") == ".py"

    def test_get_file_extension_no_extension(self):
        """Test files without extensions."""
        assert get_file_extension("README") == ""
        assert get_file_extension("Makefile") == ""
        assert get_file_extension("file_without_ext") == ""

    def test_get_file_extension_multiple_dots(self):
        """Test files with multiple dots."""
        assert get_file_extension("archive.tar.gz") == ".gz"
        assert get_file_extension("config.local.yaml") == ".yaml"
        assert get_file_extension("file.backup.txt") == ".txt"

    def test_get_file_extension_double_dot(self):
        """Test files with double extensions."""
        assert get_file_extension("file.test.js") == ".js"
        assert get_file_extension("backup.old.sql") == ".sql"

    def test_get_file_extension_hidden_file(self):
        """Test hidden files with dots."""
        assert get_file_extension(".gitignore") == ""
        assert get_file_extension(".env.local") == ".local"
        assert get_file_extension(".vscode/settings.json") == ".json"

    def test_get_file_extension_empty(self):
        """Test empty string."""
        assert get_file_extension("") == ""

    def test_get_file_extension_dot_only(self):
        """Test file with just a dot."""
        assert get_file_extension(".") == ""
        assert get_file_extension("..") == ""

    def test_get_file_extension_path_object(self):
        """Test with Path objects."""
        assert get_file_extension(Path("file.txt")) == ".txt"
        assert get_file_extension(Path("/path/to/file.py")) == ".py"
        assert get_file_extension(Path("no_extension")) == ""

    def test_get_file_extension_with_path(self):
        """Test files with full paths."""
        assert get_file_extension("/home/user/document.pdf") == ".pdf"
        assert get_file_extension("./src/main.py") == ".py"
        assert get_file_extension("../config/settings.json") == ".json"


@pytest.mark.unit
class TestBinaryFileDetection:
    """Test is_binary_file function."""

    def test_is_binary_file_executables(self):
        """Test executable file detection."""
        assert is_binary_file("program.exe") is True
        assert is_binary_file("library.dll") is True
        assert is_binary_file("lib.so") is True
        assert is_binary_file("lib.dylib") is True

    def test_is_binary_file_compiled_objects(self):
        """Test compiled object file detection."""
        assert is_binary_file("main.obj") is True
        assert is_binary_file("main.o") is True
        assert is_binary_file("static.a") is True
        assert is_binary_file("dynamic.lib") is True

    def test_is_binary_file_images(self):
        """Test image file detection."""
        assert is_binary_file("photo.jpg") is True
        assert is_binary_file("image.jpeg") is True
        assert is_binary_file("icon.png") is True
        assert is_binary_file("animation.gif") is True
        assert is_binary_file("bitmap.bmp") is True
        assert is_binary_file("favicon.ico") is True
        assert is_binary_file("vector.svg") is True
        assert is_binary_file("photo.tiff") is True

    def test_is_binary_file_audio_video(self):
        """Test audio/video file detection."""
        assert is_binary_file("song.mp3") is True
        assert is_binary_file("video.mp4") is True
        assert is_binary_file("movie.avi") is True
        assert is_binary_file("clip.mov") is True
        assert is_binary_file("audio.wav") is True
        assert is_binary_file("music.flac") is True
        assert is_binary_file("sound.ogg") is True

    def test_is_binary_file_documents(self):
        """Test document file detection."""
        assert is_binary_file("document.pdf") is True
        assert is_binary_file("text.doc") is True
        assert is_binary_file("text.docx") is True
        assert is_binary_file("spreadsheet.xls") is True
        assert is_binary_file("data.xlsx") is True
        assert is_binary_file("slides.ppt") is True
        assert is_binary_file("presentation.pptx") is True

    def test_is_binary_file_archives(self):
        """Test archive file detection."""
        assert is_binary_file("archive.zip") is True
        assert is_binary_file("backup.tar") is True
        assert is_binary_file("compressed.gz") is True
        assert is_binary_file("data.bz2") is True
        assert is_binary_file("archive.7z") is True
        assert is_binary_file("backup.rar") is True

    def test_is_binary_file_databases(self):
        """Test database file detection."""
        assert is_binary_file("data.sqlite") is True
        assert is_binary_file("cache.db") is True
        assert is_binary_file("access.mdb") is True

    def test_is_binary_file_text_files(self):
        """Test text file detection (should be False)."""
        assert is_binary_file("document.txt") is False
        assert is_binary_file("script.py") is False
        assert is_binary_file("stylesheet.css") is False
        assert is_binary_file("markup.html") is False
        assert is_binary_file("data.json") is False
        assert is_binary_file("config.yaml") is False
        assert is_binary_file("code.js") is False

    def test_is_binary_file_no_extension(self):
        """Test files without extensions (should be False)."""
        assert is_binary_file("README") is False
        assert is_binary_file("Makefile") is False
        assert is_binary_file("LICENSE") is False

    def test_is_binary_file_unknown_extension(self):
        """Test files with unknown extensions (should be False)."""
        assert is_binary_file("file.unknown") is False
        assert is_binary_file("data.custom") is False
        assert is_binary_file("config.myext") is False

    def test_is_binary_file_case_insensitive(self):
        """Test case insensitive detection."""
        assert is_binary_file("IMAGE.JPG") is True
        assert is_binary_file("Document.PDF") is True
        assert is_binary_file("ARCHIVE.ZIP") is True
        assert is_binary_file("Program.EXE") is True

    def test_is_binary_file_path_object(self):
        """Test with Path objects."""
        assert is_binary_file(Path("image.png")) is True
        assert is_binary_file(Path("script.py")) is False
        assert is_binary_file(Path("/path/to/binary.exe")) is True

    def test_is_binary_file_with_path(self):
        """Test files with full paths."""
        assert is_binary_file("/home/user/photo.jpg") is True
        assert is_binary_file("./src/main.py") is False
        assert is_binary_file("../docs/manual.pdf") is True

    def test_is_binary_file_edge_cases(self):
        """Test edge cases."""
        assert is_binary_file("") is False  # Empty string
        assert is_binary_file(".") is False  # Just dot
        assert is_binary_file("..") is False  # Double dot
        assert is_binary_file("file.") is False  # Trailing dot only

    def test_is_binary_file_multiple_extensions(self):
        """Test files with multiple extensions."""
        # Should check the final extension
        assert is_binary_file("backup.tar.gz") is True  # .gz
        assert is_binary_file("config.local.json") is False  # .json
        assert is_binary_file("image.backup.png") is True  # .png
