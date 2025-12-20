"""Tests for game configuration."""

from game_logic.game_config import (
    NORMAL_CONFIG_6_PLAYER,
    NORMAL_CONFIG_9_PLAYER,
    GameConfig,
)
from game_logic.player import Role


class TestGameConfig:
    """Test cases for GameConfig class."""

    def test_game_config_initialization(self):
        """Test GameConfig dataclass initialization."""
        config = GameConfig(
            player_number=6, character_count={Role.VILLAGER: 2}
        )
        assert config.player_number == 6
        assert config.character_count == {Role.VILLAGER: 2}

    def test_normal_config_6_player(self):
        """Test the predefined 6 player config."""
        assert NORMAL_CONFIG_6_PLAYER.player_number == 6
        assert NORMAL_CONFIG_6_PLAYER.character_count[Role.VILLAGER] == 2
        assert NORMAL_CONFIG_6_PLAYER.character_count[Role.WEREWOLF] == 2
        assert NORMAL_CONFIG_6_PLAYER.character_count[Role.PROPHET] == 1
        assert NORMAL_CONFIG_6_PLAYER.character_count[Role.WITCH] == 1

    def test_normal_config_9_player(self):
        """Test the predefined 9 player config."""
        assert NORMAL_CONFIG_9_PLAYER.player_number == 9
        assert NORMAL_CONFIG_9_PLAYER.character_count[Role.VILLAGER] == 3
        assert NORMAL_CONFIG_9_PLAYER.character_count[Role.WEREWOLF] == 3
        assert NORMAL_CONFIG_9_PLAYER.character_count[Role.PROPHET] == 1
        assert NORMAL_CONFIG_9_PLAYER.character_count[Role.WITCH] == 1
        assert NORMAL_CONFIG_9_PLAYER.character_count[Role.HUNTER] == 1
