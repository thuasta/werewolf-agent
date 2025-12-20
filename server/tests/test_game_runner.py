"""Tests for GameRunner."""

from game_controller.game_runner import GameRunner
from game_logic.game_config import NORMAL_CONFIG_6_PLAYER


class TestGameRunner:
    """Test cases for GameRunner."""

    def test_initialization(self):
        """Test GameRunner can be instantiated with config."""
        runner = GameRunner(config=NORMAL_CONFIG_6_PLAYER)
        assert isinstance(runner, GameRunner)
        assert runner.config == NORMAL_CONFIG_6_PLAYER
        assert runner.player_count == 0

    def test_is_running_initially_false(self):
        """Test is_running property is False initially."""
        runner = GameRunner(config=NORMAL_CONFIG_6_PLAYER)
        assert runner.is_running is False

    def test_is_bound_with_server_initially_false(self):
        """Test is_bound_with_server property is False initially."""
        runner = GameRunner(config=NORMAL_CONFIG_6_PLAYER)
        assert runner.is_bound_with_server is False

    def test_is_bound_with_recorder_initially_false(self):
        """Test is_bound_with_recorder property is False initially."""
        runner = GameRunner(config=NORMAL_CONFIG_6_PLAYER)
        assert runner.is_bound_with_recorder is False

    def test_is_end_initially_false(self):
        """Test is_end property is False initially."""
        runner = GameRunner(config=NORMAL_CONFIG_6_PLAYER)
        assert runner.is_end is False

    def test_player_ready_when_count_matches(self):
        """Test player_ready property."""
        runner = GameRunner(config=NORMAL_CONFIG_6_PLAYER)
        assert runner.player_ready is False
        runner.player_count = 6
        assert runner.player_ready is True
