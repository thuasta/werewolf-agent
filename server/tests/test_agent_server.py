"""Tests for AgentServer."""

import pytest
from agent_server.agent_server import AgentServer


class TestAgentServer:
    """Test cases for AgentServer."""

    def test_initialization(self):
        """Test server initialization."""
        server = AgentServer(("127.0.0.1", 8080))
        assert isinstance(server, AgentServer)


@pytest.mark.asyncio
async def test_start_not_implemented():
    """Test that start() raises NotImplementedError."""
    server = AgentServer(("127.0.0.1", 8080))
    await server.start()


def test_bind_runner_no_error():
    """Test that bind_runner() can be called without error."""
    server = AgentServer(("127.0.0.1", 8080))
    # bind_runner has no implementation body, so it should not raise
    server.bind_runner(None)
