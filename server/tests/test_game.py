import pytest
from game_logic.game import Game, GameState
from game_logic.game_config import NORMAL_CONFIG_6_PLAYER
from game_logic.player import Character


class TestGame:
    def test_game_initialization(self):
        """Test that the game initializes with the correct state and config."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        assert game._state == GameState.NOT_STARTED
        assert game._config == NORMAL_CONFIG_6_PLAYER
        assert game._players == []

    def test_game_start_raises_not_implemented(self):
        """Test that start method raises NotImplementedError."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        with pytest.raises(NotImplementedError):
            game.start()

    def test_sun_rise_raises_not_implemented(self):
        """Test that _sun_rise method raises NotImplementedError."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        with pytest.raises(NotImplementedError):
            game._sun_rise()

    def test_sun_set_raises_not_implemented(self):
        """Test that _sun_set method raises NotImplementedError."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        with pytest.raises(NotImplementedError):
            game._sun_set()

    def test_is_end_raises_not_implemented(self):
        """Test that is_end method raises NotImplementedError."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        with pytest.raises(NotImplementedError):
            game.is_end()

    def test_is_character_alive_raises_not_implemented(self):
        """Test that is_character_alive method raises NotImplementedError."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        with pytest.raises(NotImplementedError):
            game.is_character_alive(Character.WEREWOLF)

    def test_get_result_raises_not_implemented(self):
        """Test that get_result method raises NotImplementedError."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        with pytest.raises(NotImplementedError):
            game.get_result()

    def test_state_switch_raises_not_implemented(self):
        """Test that state_switch method raises NotImplementedError."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        with pytest.raises(NotImplementedError):
            game.state_switch()
