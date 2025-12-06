"""Tests for GameRunner."""

import pytest
from game_controller.game_runner import GameRunner


class TestGameRunner:
    """Test cases for GameRunner."""

    @pytest.mark.asyncio
    @pytest.mark.xfail(strict=True, reason="Not implemented yet")
    async def test_start(self):
        """Test that start method runs the game loop."""
        runner = GameRunner()
        await runner.start()

    @pytest.mark.asyncio
    @pytest.mark.xfail(strict=True, reason="Not implemented yet")
    async def test_on_message(self):
        """Test message handling."""
        runner = GameRunner()
        # Mock a message
        # Note: The current signature of on_message takes no arguments,
        # which might be a placeholder. We test what is there.
        await runner.on_message()
