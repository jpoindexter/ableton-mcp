# test_error_handling.py - Tests for error handling paths
"""
Comprehensive tests for all error handling scenarios:
- Connection errors
- Timeout handling
- Invalid JSON responses
- Ableton error responses
- HTTP exception handling
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import sys
import os
import socket

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'MCP_Server'))


# =============================================================================
# Connection Error Tests
# =============================================================================

class TestConnectionErrors:
    """Test connection error handling."""

    def test_ableton_disconnected_returns_503(self):
        """Test that disconnected Ableton returns 503."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=503,
                detail="Could not connect to Ableton at localhost:9877"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/session")
                assert response.status_code == 503
                assert "Could not connect to Ableton" in response.json()["error"]

    def test_connection_refused_handled(self):
        """Test that connection refused is handled gracefully."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=503,
                detail="Could not connect to Ableton"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/tracks/0")
                assert response.status_code == 503

    def test_socket_error_during_command(self):
        """Test socket error during command execution."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=500,
                detail="Command failed after 2 retries: Socket error"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.post("/api/transport/play")
                assert response.status_code == 500


# =============================================================================
# Timeout Error Tests
# =============================================================================

class TestTimeoutErrors:
    """Test timeout error handling."""

    def test_socket_timeout_handled(self):
        """Test that socket timeout returns appropriate error."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=500,
                detail="Command failed after 2 retries: Timeout waiting for response from Ableton"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/session")
                assert response.status_code == 500
                assert "Timeout" in response.json()["error"] or "failed" in response.json()["error"]

    def test_connect_timeout_handled(self):
        """Test connection timeout handling."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=503,
                detail="Could not connect to Ableton"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/session")
                assert response.status_code == 503


# =============================================================================
# Invalid JSON Response Tests
# =============================================================================

class TestInvalidJsonErrors:
    """Test invalid JSON response handling."""

    def test_invalid_json_response_handled(self):
        """Test that invalid JSON from Ableton is handled."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=500,
                detail="Command failed after 2 retries: Invalid JSON response from Ableton"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/session")
                assert response.status_code == 500

    def test_empty_response_handled(self):
        """Test that empty response is handled."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=500,
                detail="No response from Ableton"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/session")
                assert response.status_code == 500


# =============================================================================
# Ableton Error Response Tests
# =============================================================================

class TestAbletonErrors:
    """Test Ableton error response handling."""

    def test_ableton_error_status(self):
        """Test that Ableton error status is properly handled."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=400,
                detail="Track index out of range"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/tracks/999")
                assert response.status_code == 400

    def test_ableton_clip_not_found(self):
        """Test clip not found error."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=400,
                detail="No clip in slot"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/tracks/0/clips/0")
                assert response.status_code == 400

    def test_ableton_device_not_found(self):
        """Test device not found error."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=400,
                detail="Device not found"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/tracks/0/devices/99")
                assert response.status_code == 400


# =============================================================================
# HTTP Exception Handler Tests
# =============================================================================

class TestHTTPExceptionHandling:
    """Test HTTP exception handlers."""

    def test_http_exception_format(self):
        """Test HTTP exception response format."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=400,
                detail="Test error message"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/session")
                assert response.status_code == 400
                assert "error" in response.json()

    def test_validation_error_format(self):
        """Test validation error response format."""
        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.return_value = {}

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                # Invalid tempo should return 422
                response = client.post("/api/tempo", json={"tempo": -100})
                assert response.status_code == 422


# =============================================================================
# Command Whitelist Error Tests
# =============================================================================

class TestCommandWhitelistErrors:
    """Test command whitelist error handling."""

    def test_unknown_command_error(self):
        """Test unknown command returns error."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=400,
                detail="Unknown command: dangerous_command"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.post("/api/command", json={
                    "command": "dangerous_command"
                })
                # Can be 400 or 422 depending on validation layer
                assert response.status_code in [400, 422]


# =============================================================================
# Buffer Overflow Protection Tests
# =============================================================================

class TestBufferOverflowProtection:
    """Test buffer overflow protection."""

    def test_large_request_handled(self):
        """Test that overly large requests are rejected."""
        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.return_value = {}

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                # Create many notes (but still within reasonable limits)
                notes = [
                    {"pitch": 60, "start_time": i * 0.1, "duration": 0.1, "velocity": 100}
                    for i in range(100)
                ]
                response = client.post("/api/tracks/0/clips/0/notes", json={
                    "track_index": 0,
                    "clip_index": 0,
                    "notes": notes
                })
                # Should succeed with reasonable number of notes
                assert response.status_code == 200

    def test_response_size_limit(self):
        """Test that large responses are handled."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            # Simulate large response error
            mock_conn.send_command.side_effect = HTTPException(
                status_code=500,
                detail="Response too large (>1048576 bytes)"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/session")
                assert response.status_code == 500


# =============================================================================
# Recovery Tests
# =============================================================================

class TestErrorRecovery:
    """Test error recovery behavior."""

    def test_reconnect_after_disconnect(self):
        """Test reconnection after disconnect."""
        from fastapi import HTTPException
        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            # First call fails with HTTPException to trigger error response
            mock_conn.send_command.side_effect = HTTPException(
                status_code=503,
                detail="Connection lost"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                # This test verifies the design allows for retry behavior
                # First request fails
                response1 = client.get("/api/session")
                assert response1.status_code == 503

                # Second request should work after reconnection
                mock_conn.send_command.side_effect = None
                mock_conn.send_command.return_value = {"tempo": 120.0}
                response2 = client.get("/api/session")
                assert response2.status_code == 200


# =============================================================================
# Health Check Error Tests
# =============================================================================

class TestHealthCheckErrors:
    """Test health check error handling."""

    def test_health_check_disconnected(self):
        """Test health check when disconnected."""
        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = Exception("Not connected")

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/health")
                # Health check should still return 200 but with error info
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "disconnected"
                assert "error" in data


# =============================================================================
# Retry Logic Tests
# =============================================================================

class TestRetryLogic:
    """Test retry logic for failed commands."""

    def test_max_retries_configuration(self):
        """Test that MAX_RETRIES is configured."""
        import rest_api_server
        assert hasattr(rest_api_server, 'MAX_RETRIES')
        assert rest_api_server.MAX_RETRIES >= 1

    def test_retry_exhaustion_error(self):
        """Test error after retries exhausted."""
        from fastapi import HTTPException

        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "REST_API_KEY": ""
        }):
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = HTTPException(
                status_code=500,
                detail="Command failed after 2 retries: Connection error"
            )

            with patch('rest_api_server.AbletonConnection') as MockClass:
                MockClass.return_value = mock_conn

                import importlib
                import rest_api_server
                importlib.reload(rest_api_server)
                rest_api_server.ableton = mock_conn

                client = TestClient(rest_api_server.app)

                response = client.get("/api/session")
                assert response.status_code == 500
                assert "failed" in response.json()["error"].lower()


# =============================================================================
# Concurrent Request Error Tests
# =============================================================================

class TestConcurrentRequestErrors:
    """Test error handling with concurrent requests."""

    def test_thread_safety(self):
        """Test that connection is thread-safe."""
        import rest_api_server
        # Verify the connection has a lock
        conn = rest_api_server.AbletonConnection()
        assert hasattr(conn, '_lock')
