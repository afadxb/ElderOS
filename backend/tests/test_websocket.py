"""Tests for the WebSocket /ws/alerts endpoint."""

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

pytestmark = pytest.mark.asyncio


def test_ws_no_token(test_app):
    """Connecting without a token closes the socket with code 4001."""
    # Use Starlette's synchronous TestClient for WebSocket testing
    client = TestClient(test_app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/alerts"):
            pass  # should not reach here
    assert exc_info.value.code == 4001


def test_ws_invalid_token(test_app):
    """Connecting with an invalid token closes the socket with code 4001."""
    client = TestClient(test_app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/alerts?token=invalid-jwt-garbage"):
            pass
    assert exc_info.value.code == 4001
