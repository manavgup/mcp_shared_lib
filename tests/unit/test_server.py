import asyncio

import pytest

from mcp_shared_lib.models.base.types import LogLevel
from mcp_shared_lib.utils import logging_service


def test_get_logger_returns_logger_instance():
    logger = logging_service.get_logger("test_logger")
    assert logger.name == "test_logger"


@pytest.mark.asyncio
async def test_set_level_and_notify(caplog):
    # Set log level to DEBUG
    await logging_service.set_level(LogLevel.DEBUG)

    # Use caplog to capture logs
    with caplog.at_level("DEBUG"):
        await logging_service.notify(
            "Test debug message", LogLevel.DEBUG, "test_notify_logger"
        )
        assert any("Test debug message" in record.message for record in caplog.records)


@pytest.mark.asyncio
async def test_subscribe_and_notify():
    gen = logging_service.subscribe()

    # Create a task to get the next message from the generator
    # This ensures the generator starts executing and is waiting for messages
    message_task = asyncio.create_task(gen.__anext__())

    # Give the generator a chance to start and reach the queue.get() call
    await asyncio.sleep(0.01)

    # Now send the notification
    await logging_service.notify(
        "Test subscription", LogLevel.INFO, "test_subscribe_logger"
    )

    try:
        # Wait for the message with timeout
        message = await asyncio.wait_for(message_task, timeout=2)
        assert message["data"]["data"] == "Test subscription"
        assert message["data"]["level"] == LogLevel.INFO
        assert message["data"]["logger"] == "test_subscribe_logger"
    finally:
        await gen.aclose()
