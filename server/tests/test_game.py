"""Tests for the main Game class."""

import pytest
from game_logic.game import Game, GameState
from game_logic.game_config import NORMAL_CONFIG_6_PLAYER
from game_logic.player import Character, Player
from game_logic.result import GameResult


class TestGame:
    """Test cases for Game class."""

    def test_game_initialization(self):
        """Test that the game initializes with the correct state and config."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        # pylint: disable=protected-access
        assert game._state == GameState.NOT_STARTED
        assert game._config == NORMAL_CONFIG_6_PLAYER
        assert not game._players

    @pytest.mark.xfail(strict=True, reason="Game logic not implemented yet")
    def test_game_start(self):
        """Test that start method initializes players and sets state."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        game.start()
        assert game._state == GameState.EVENING
        assert len(game._players) == 6

        # Verify character distribution
        characters = [p.character for p in game._players]
        assert characters.count(Character.VILLAGER) == 2
        assert characters.count(Character.WEREWOLF) == 2
        assert characters.count(Character.SEER) == 1
        assert characters.count(Character.WITCH) == 1

    @pytest.mark.xfail(strict=True, reason="Game logic not implemented yet")
    def test_sun_rise(self):
        """Test that _sun_rise method changes state to MORNING."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        game._state = GameState.EVENING
        game._sun_rise()
        assert game._state == GameState.MORNING

    @pytest.mark.xfail(strict=True, reason="Game logic not implemented yet")
    def test_sun_set(self):
        """Test that _sun_set method changes state to EVENING."""
        game = Game(NORMAL_CONFIG_6_PLAYER)
        game._state = GameState.MORNING
        game._sun_set()
        assert game._state == GameState.EVENING

    @pytest.mark.xfail(strict=True, reason="Game logic not implemented yet")
    def test_is_end(self):
        """Test is_end method."""
        game = Game(NORMAL_CONFIG_6_PLAYER)

        # Scenario 1: Game just started, not end
        # Manually setup players
        game._players = []
        for _ in range(6):
            player = Player()
            player.alive = True
            player.character = Character.VILLAGER  # Just dummy
            game._players.append(player)
        # Set some werewolves
        game._players[0].character = Character.WEREWOLF
        game._players[1].character = Character.WEREWOLF

        assert not game.is_end()

        # Scenario 2: All werewolves dead
        game._players[0].alive = False
        game._players[1].alive = False
        assert game.is_end()

    @pytest.mark.xfail(strict=True, reason="Game logic not implemented yet")
    def test_is_character_alive(self):
        """Test is_character_alive method."""
        game = Game(NORMAL_CONFIG_6_PLAYER)

        # Setup players
        p1 = Player()
        p1.character = Character.WEREWOLF
        p1.alive = True

        p2 = Player()
        p2.character = Character.VILLAGER
        p2.alive = False

        game._players = [p1, p2]

        assert game.is_character_alive(Character.WEREWOLF)
        assert not game.is_character_alive(Character.VILLAGER)

    @pytest.mark.xfail(strict=True, reason="Game logic not implemented yet")
    def test_get_result(self):
        """Test get_result method."""
        game = Game(NORMAL_CONFIG_6_PLAYER)

        # Setup players for Werewolf win (Villagers dead)
        # Note: This logic depends on specific win conditions which might be complex
        # For now, we assume if all villagers are dead, werewolves win.
        game._players = []
        for _ in range(2):
            player = Player()
            player.character = Character.WEREWOLF
            player.alive = True
            game._players.append(player)
        for _ in range(4):
            player = Player()
            player.character = Character.VILLAGER
            player.alive = False
            game._players.append(player)

        result = game.get_result()
        assert result == GameResult.WEREWOLF_WIN

    @pytest.mark.xfail(strict=True, reason="Game logic not implemented yet")
    def test_state_switch(self):
        """Test state_switch method."""
        game = Game(NORMAL_CONFIG_6_PLAYER)

        # Not Started -> Start (Evening)
        game.state_switch()
        assert game._state == GameState.EVENING
