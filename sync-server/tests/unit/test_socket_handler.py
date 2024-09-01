import pytest
import json

from freeze_gun import freeze_time
from unittest.mock import AsyncMock, MagicMock

import constants
from handlers.socket_handler import SocketHandler


@pytest.mark.asyncio
@freeze_time("2024-01-01T00:00:00")
async def test_handle_message_push_message():
    # Arrange
    sync_service_mock = MagicMock()
    updated_record_mock = MagicMock()
    updated_record_mock.to_dict.return_value = {"id": 1, "data": "updated"}

    sync_service_mock.push_batch.return_value = updated_record_mock
    
    websocket_mock = AsyncMock()
    other_websocket_mock = AsyncMock()

    handler = SocketHandler()  # Replace with your actual handler class
    handler.sync_service = sync_service_mock
    handler.connected_clients = [other_websocket_mock]

    message = json.dumps({
        constants.MESSAGE_TYPE: constants.PUSH_MESSAGE,
        constants.ID: 1,
        constants.BATCH_DATA: "test",
        constants.BATCH_CHANGE_METHOD: "update"
    })

    # Act
    await handler.handle_message(message, websocket_mock)

    # Assert
    sync_service_mock.push_batch.assert_called_once_with(1, "update", "test")
    other_websocket_mock.send.assert_called_once_with(json.dumps({"id": 1, "data": "test", "status": "active", "updated_at": "2024-01-01T00:00:00"}))