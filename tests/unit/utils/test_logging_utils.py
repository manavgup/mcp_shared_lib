"""Tests for logging_utils module."""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_shared_lib.models.base.types import LogLevel
from mcp_shared_lib.utils.logging_utils import (
    LoggingService,
    get_logger,
    logging_service,
    setup_logging,
)


@pytest.mark.unit
class TestLoggingService:
    """Test LoggingService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = LoggingService()

    def test_logging_service_initialization(self):
        """Test LoggingService initialization."""
        assert self.service._level == LogLevel.INFO
        assert self.service._subscribers == []
        assert self.service._loggers == {}

    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test logging service initialization."""
        with patch("logging.basicConfig") as mock_config, patch(
            "logging.getLogger"
        ) as mock_get_logger, patch("logging.info") as mock_info:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            await self.service.initialize(LogLevel.DEBUG)

            mock_config.assert_called_once_with(
                level=LogLevel.DEBUG.value,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            mock_get_logger.assert_called_once()
            mock_info.assert_called_once_with("Logging service initialized")
            assert self.service._loggers[""] == mock_logger

    @pytest.mark.asyncio
    async def test_shutdown(self):
        """Test logging service shutdown."""
        # Add some mock subscribers
        self.service._subscribers = [asyncio.Queue(), asyncio.Queue()]

        with patch("logging.info") as mock_info:
            await self.service.shutdown()

            assert self.service._subscribers == []
            mock_info.assert_called_once_with("Logging service shutdown")

    def test_get_logger_new(self):
        """Test getting a new logger."""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            result = self.service.get_logger("test_logger")

            mock_get_logger.assert_called_once_with("test_logger")
            mock_logger.setLevel.assert_called_once_with(logging.INFO)
            assert result == mock_logger
            assert self.service._loggers["test_logger"] == mock_logger

    def test_get_logger_existing(self):
        """Test getting an existing logger."""
        mock_logger = MagicMock()
        self.service._loggers["existing"] = mock_logger

        result = self.service.get_logger("existing")

        assert result == mock_logger

    def test_get_logger_with_different_level(self):
        """Test getting a logger with custom service level."""
        self.service._level = LogLevel.WARNING

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            self.service.get_logger("warning_logger")

            mock_logger.setLevel.assert_called_once_with(logging.WARNING)

    @pytest.mark.asyncio
    async def test_set_level(self):
        """Test setting log level."""
        # Add some loggers
        mock_logger1 = MagicMock()
        mock_logger2 = MagicMock()
        self.service._loggers = {"logger1": mock_logger1, "logger2": mock_logger2}

        with patch.object(self.service, "notify") as mock_notify:
            await self.service.set_level(LogLevel.ERROR)

            assert self.service._level == LogLevel.ERROR
            mock_logger1.setLevel.assert_called_once_with(logging.ERROR)
            mock_logger2.setLevel.assert_called_once_with(logging.ERROR)
            mock_notify.assert_called_once_with(
                "Log level set to LogLevel.ERROR", LogLevel.INFO, "logging"
            )

    @pytest.mark.asyncio
    async def test_notify_basic(self):
        """Test basic log notification."""
        with patch.object(self.service, "get_logger") as mock_get_logger, patch(
            "datetime.datetime"
        ) as mock_datetime:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_datetime.now.return_value.isoformat.return_value = (
                "2023-01-01T00:00:00Z"
            )

            await self.service.notify("Test message", LogLevel.INFO, "test_logger")

            mock_get_logger.assert_called_once_with("test_logger")
            mock_logger.info.assert_called_once_with("Test message")

    @pytest.mark.asyncio
    async def test_notify_below_level(self):
        """Test notification below current level is skipped."""
        self.service._level = LogLevel.WARNING

        with patch.object(self.service, "get_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            await self.service.notify("Debug message", LogLevel.DEBUG, "test_logger")

            # Should not call logger methods
            mock_get_logger.assert_not_called()

    @pytest.mark.asyncio
    async def test_notify_with_subscribers(self):
        """Test notification with subscribers."""
        queue = asyncio.Queue()
        self.service._subscribers.append(queue)

        with patch.object(self.service, "get_logger") as mock_get_logger, patch(
            "mcp_shared_lib.utils.logging_utils.datetime"
        ) as mock_datetime:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Mock datetime
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T00:00:00+00:00"
            mock_datetime.now.return_value = mock_now

            await self.service.notify("Test message", LogLevel.ERROR, "test_logger")

            # Check message was queued
            assert not queue.empty()
            message = await queue.get()

            expected = {
                "type": "log",
                "data": {
                    "level": LogLevel.ERROR,
                    "data": "Test message",
                    "timestamp": "2023-01-01T00:00:00+00:00",
                    "logger": "test_logger",
                },
            }
            assert message == expected

    @pytest.mark.asyncio
    async def test_notify_without_logger_name(self):
        """Test notification without logger name."""
        with patch.object(self.service, "get_logger") as mock_get_logger, patch(
            "mcp_shared_lib.utils.logging_utils.datetime"
        ) as mock_datetime:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_datetime.now.return_value.isoformat.return_value = (
                "2023-01-01T00:00:00+00:00"
            )

            await self.service.notify("Test message", LogLevel.INFO)

            mock_get_logger.assert_called_once_with("")

    @pytest.mark.asyncio
    async def test_notify_subscriber_error(self):
        """Test handling subscriber notification errors."""
        # Create a queue that will fail
        failing_queue = AsyncMock()
        failing_queue.put.side_effect = Exception("Queue error")
        self.service._subscribers.append(failing_queue)

        with patch.object(self.service, "get_logger") as mock_get_logger, patch(
            "mcp_shared_lib.utils.logging_utils.datetime"
        ) as mock_datetime:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_datetime.now.return_value.isoformat.return_value = (
                "2023-01-01T00:00:00+00:00"
            )

            await self.service.notify("Test message", LogLevel.INFO, "test")

            # Should log the error
            mock_logger.error.assert_called_once_with(
                "Failed to notify subscriber: Queue error"
            )

    @pytest.mark.asyncio
    async def test_subscribe(self):
        """Test log subscription."""

        async def consume_subscription():
            subscription = self.service.subscribe()
            try:
                message = await subscription.__anext__()
                return message
            finally:
                await subscription.aclose()

        # Start subscription in background task
        subscription_task = asyncio.create_task(consume_subscription())

        # Wait a bit for subscription to be set up
        await asyncio.sleep(0.1)

        # Send a notification
        with patch("mcp_shared_lib.utils.logging_utils.datetime") as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = (
                "2023-01-01T00:00:00+00:00"
            )
            await self.service.notify("Test message", LogLevel.INFO, "test")

        # Get the message from subscription
        message = await subscription_task

        assert message["type"] == "log"
        assert message["data"]["data"] == "Test message"
        assert message["data"]["level"] == LogLevel.INFO

    def test_subscribers_list_manipulation(self):
        """Test direct manipulation of subscribers list."""
        initial_count = len(self.service._subscribers)

        # Manually add a queue to test list behavior
        queue = asyncio.Queue()
        self.service._subscribers.append(queue)

        assert len(self.service._subscribers) == initial_count + 1

        # Remove it
        self.service._subscribers.remove(queue)

        assert len(self.service._subscribers) == initial_count

    def test_should_log_debug_level(self):
        """Test _should_log with DEBUG level service."""
        self.service._level = LogLevel.DEBUG

        assert self.service._should_log(LogLevel.DEBUG) is True
        assert self.service._should_log(LogLevel.INFO) is True
        assert self.service._should_log(LogLevel.WARNING) is True
        assert self.service._should_log(LogLevel.ERROR) is True

    def test_should_log_info_level(self):
        """Test _should_log with INFO level service."""
        self.service._level = LogLevel.INFO

        assert self.service._should_log(LogLevel.DEBUG) is False
        assert self.service._should_log(LogLevel.INFO) is True
        assert self.service._should_log(LogLevel.WARNING) is True
        assert self.service._should_log(LogLevel.ERROR) is True

    def test_should_log_warning_level(self):
        """Test _should_log with WARNING level service."""
        self.service._level = LogLevel.WARNING

        assert self.service._should_log(LogLevel.DEBUG) is False
        assert self.service._should_log(LogLevel.INFO) is False
        assert self.service._should_log(LogLevel.WARNING) is True
        assert self.service._should_log(LogLevel.ERROR) is True

    def test_should_log_error_level(self):
        """Test _should_log with ERROR level service."""
        self.service._level = LogLevel.ERROR

        assert self.service._should_log(LogLevel.DEBUG) is False
        assert self.service._should_log(LogLevel.INFO) is False
        assert self.service._should_log(LogLevel.WARNING) is False
        assert self.service._should_log(LogLevel.ERROR) is True

    def test_should_log_all_levels(self):
        """Test _should_log with all RFC 5424 levels."""
        self.service._level = LogLevel.NOTICE

        assert self.service._should_log(LogLevel.DEBUG) is False
        assert self.service._should_log(LogLevel.INFO) is False
        assert self.service._should_log(LogLevel.NOTICE) is True
        assert self.service._should_log(LogLevel.WARNING) is True
        assert self.service._should_log(LogLevel.ERROR) is True
        assert self.service._should_log(LogLevel.CRITICAL) is True
        assert self.service._should_log(LogLevel.ALERT) is True
        assert self.service._should_log(LogLevel.EMERGENCY) is True


@pytest.mark.unit
class TestModuleFunctions:
    """Test module-level functions."""

    def test_get_logger_function(self):
        """Test get_logger module function."""
        with patch(
            "mcp_shared_lib.utils.logging_utils.logging_service"
        ) as mock_service:
            mock_logger = MagicMock()
            mock_service.get_logger.return_value = mock_logger

            result = get_logger("test_module")

            mock_service.get_logger.assert_called_once_with("test_module")
            assert result == mock_logger

    @pytest.mark.asyncio
    async def test_setup_logging_function(self):
        """Test setup_logging module function."""
        with patch(
            "mcp_shared_lib.utils.logging_utils.logging_service"
        ) as mock_service:
            mock_service.initialize = AsyncMock()

            await setup_logging(LogLevel.DEBUG)

            mock_service.initialize.assert_called_once_with(LogLevel.DEBUG)

    def test_logging_service_singleton(self):
        """Test that logging_service is a singleton instance."""
        assert isinstance(logging_service, LoggingService)
        assert logging_service._level == LogLevel.INFO
        assert logging_service._subscribers == []


@pytest.mark.unit
class TestLoggingServiceIntegration:
    """Integration tests for LoggingService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = LoggingService()

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete logging workflow."""
        # Initialize service
        with patch("logging.basicConfig"), patch(
            "logging.getLogger"
        ) as mock_get_logger, patch("logging.info"):
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            await self.service.initialize(LogLevel.INFO)

        # Create subscription
        queue = asyncio.Queue()
        self.service._subscribers.append(queue)

        # Send notification
        with patch("mcp_shared_lib.utils.logging_utils.datetime") as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = (
                "2023-01-01T00:00:00+00:00"
            )
            await self.service.notify(
                "Integration test", LogLevel.WARNING, "integration"
            )

        # Verify message received
        message = await queue.get()
        assert message["type"] == "log"
        assert message["data"]["data"] == "Integration test"
        assert message["data"]["level"] == LogLevel.WARNING
        assert message["data"]["logger"] == "integration"

        # Shutdown
        with patch("logging.info"):
            await self.service.shutdown()

    @pytest.mark.asyncio
    async def test_level_filtering_workflow(self):
        """Test log level filtering in complete workflow."""
        self.service._level = LogLevel.ERROR

        queue = asyncio.Queue()
        self.service._subscribers.append(queue)

        # Send INFO message (should be filtered)
        await self.service.notify("Filtered message", LogLevel.INFO, "test")

        # Send ERROR message (should pass)
        with patch("mcp_shared_lib.utils.logging_utils.datetime") as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = (
                "2023-01-01T00:00:00+00:00"
            )
            await self.service.notify("Error message", LogLevel.ERROR, "test")

        # Only ERROR message should be in queue
        assert queue.qsize() == 1
        message = await queue.get()
        assert message["data"]["data"] == "Error message"

    @pytest.mark.asyncio
    async def test_multiple_loggers(self):
        """Test managing multiple loggers."""
        with patch("logging.getLogger") as mock_get_logger, patch.object(
            self.service, "notify"
        ) as mock_notify:
            mock_logger1 = MagicMock()
            mock_logger2 = MagicMock()
            mock_get_logger.side_effect = [mock_logger1, mock_logger2]

            logger1 = self.service.get_logger("module1")
            logger2 = self.service.get_logger("module2")

            assert logger1 == mock_logger1
            assert logger2 == mock_logger2
            assert len(self.service._loggers) == 2

            # Test level change affects all loggers
            await self.service.set_level(LogLevel.DEBUG)

            mock_logger1.setLevel.assert_called_with(logging.DEBUG)
            mock_logger2.setLevel.assert_called_with(logging.DEBUG)
            mock_notify.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_log_function_selection(self):
        """Test correct log function selection for different levels."""
        # Set to DEBUG level to ensure all messages pass through
        self.service._level = LogLevel.DEBUG

        with patch.object(self.service, "get_logger") as mock_get_logger:
            mock_logger = MagicMock()
            # Set up log function attributes
            mock_logger.debug = MagicMock()
            mock_logger.info = MagicMock()
            mock_logger.warning = MagicMock()
            mock_logger.error = MagicMock()
            mock_logger.critical = MagicMock()

            mock_get_logger.return_value = mock_logger

            # Test various log levels map to correct functions
            await self.service.notify("Debug msg", LogLevel.DEBUG, "test")
            mock_logger.debug.assert_called_with("Debug msg")

            await self.service.notify("Info msg", LogLevel.INFO, "test")
            mock_logger.info.assert_called_with("Info msg")

            await self.service.notify("Warning msg", LogLevel.WARNING, "test")
            mock_logger.warning.assert_called_with("Warning msg")

            await self.service.notify("Error msg", LogLevel.ERROR, "test")
            mock_logger.error.assert_called_with("Error msg")

            await self.service.notify("Critical msg", LogLevel.CRITICAL, "test")
            mock_logger.critical.assert_called_with("Critical msg")
