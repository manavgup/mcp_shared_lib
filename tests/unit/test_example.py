import pytest

"""
Example test file for mcp_shared_lib.
"""


class TestExample:
    """Example test class."""

    @pytest.mark.unit
    def test_example(self):
        """Example test method."""
        assert True

    @pytest.mark.unit
    def test_basic_math(self):
        """Test basic functionality."""
        assert 1 + 1 == 2
        assert 2 * 3 == 6
