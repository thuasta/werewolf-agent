"""Tests for AgentServer."""

import pytest
from agent_server.agent_server import AgentServer


class TestAgentServer:
    """Test cases for AgentServer."""

    def test_initialization(self):
        """Test server initialization."""
        server = AgentServer()
        assert isinstance(server, AgentServer)

    @pytest.mark.xfail(reason="Not implemented yet")
    async def test_start(self):
        """Test server start."""
        server = AgentServer()
        # Assuming there will be a start method eventually
        if hasattr(server, "start"):
            await server.start()
        else:
            pytest.fail("AgentServer should have a start method")
