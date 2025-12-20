"""Tests for AgentServer."""

import pytest
from agent_server.agent_server import AgentServer


class TestAgentServer:
    """Test cases for AgentServer."""

    def test_initialization(self):
        """Test server initialization."""
        server = AgentServer()
        assert isinstance(server, AgentServer)

    @pytest.mark.xfail(strict=True, reason="Not implemented yet")
    async def test_start(self):
        """Test server start."""
        server = AgentServer()
        await server.start()
