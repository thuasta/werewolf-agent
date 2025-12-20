"""Tests for GameResult enum."""

from game_logic.result import GameResult


class TestGameResult:
    """Test cases for GameResult enum."""

    def test_game_result_values(self):
        """Test GameResult enum has expected values."""
        assert GameResult.WEREWOLF_WIN is not None
        assert GameResult.VILLAGERS_WIN is not None

    def test_game_result_are_different(self):
        """Test GameResult enum values are distinct."""
        assert GameResult.WEREWOLF_WIN != GameResult.VILLAGERS_WIN
