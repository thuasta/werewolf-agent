"""Tests for the main Game class."""

import pytest
from game_logic.game import Game, GameState
from game_logic.game_config import NORMAL_CONFIG_6_PLAYER
from game_logic.player import Character


class TestGame:
    """Test cases for Game class."""

    def test_game_initialization(self):
        """Test that the game initializes with the correct state and config."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        # pylint: disable=protected-access
        assert game._state == GameState.NOT_STARTED
        assert game._config == NORMAL_CONFIG_6_PLAYER
        assert not game._players

    @pytest.mark.xfail(reason="Game logic not implemented yet", raises=NotImplementedError)
    def test_game_start(self):
        """Test that start method initializes players and sets state."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        game.start()
        assert game._state == GameState.EVENING
        assert len(game._players) == 6

    @pytest.mark.xfail(reason="Game logic not implemented yet", raises=NotImplementedError)
    def test_sun_rise(self):
        """Test that _sun_rise method changes state to MORNING."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        # We need to start the game first to get to EVENING, but start() raises NotImplementedError
        # So we manually set the state for this test, assuming start() worked or we are in a valid state
        game._state = GameState.EVENING
        game._sun_rise()
        assert game._state == GameState.MORNING

    @pytest.mark.xfail(reason="Game logic not implemented yet", raises=NotImplementedError)
    def test_sun_set(self):
        """Test that _sun_set method changes state to EVENING."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        game._state = GameState.MORNING
        game._sun_set()
        assert game._state == GameState.EVENING

    @pytest.mark.xfail(reason="Game logic not implemented yet", raises=NotImplementedError)
    def test_is_end(self):
        """Test is_end method."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        # Assuming game started
        assert not game.is_end()

    @pytest.mark.xfail(reason="Game logic not implemented yet", raises=NotImplementedError)
    def test_is_character_alive(self):
        """Test is_character_alive method."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        # This will fail because players are not initialized
        assert game.is_character_alive(Character.WEREWOLF)

    @pytest.mark.xfail(reason="Game logic not implemented yet", raises=NotImplementedError)
    def test_get_result(self):
        """Test get_result method."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        assert game.get_result() is None

    @pytest.mark.xfail(reason="Game logic not implemented yet", raises=NotImplementedError)
    def test_state_switch(self):
        """Test state_switch method."""
        game = Game(NORMAL_CONFIG_6_PLAYER)

        # Not Started -> Start (Evening)
        game.state_switch()
        assert game._state == GameState.EVENING
