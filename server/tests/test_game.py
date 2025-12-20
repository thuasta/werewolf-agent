"""Tests for the main Game class."""

import pytest
from game_logic.game import Game, GameState
from game_logic.player import Role


class TestGameState:
    """Test cases for GameState enum."""

    def test_game_state_values(self):
        """Test GameState enum has expected values."""
        assert GameState.NOT_STARTED is not None
        assert GameState.EVENING is not None
        assert GameState.MORNING is not None
        assert GameState.FINISHED is not None


class TestGame:
    """Test cases for Game class."""

    def test_game_initialization(self):
        """Test that the game initializes with the correct state."""
        game = Game()
        assert game.state == GameState.NOT_STARTED

    def test_game_start(self):
        """Test that start method sets state to EVENING."""
        game = Game()
        game.start()
        assert game.state == GameState.EVENING

    def test_game_start_twice_raises_error(self):
        """Test that calling start() twice raises ValueError."""
        game = Game()
        game.start()
        with pytest.raises(ValueError):
            game.start()

    def test_is_end_not_ended_initially(self):
        """Test is_end returns False for a fresh game."""
        game = Game()
        assert game.is_end() is False

    def test_is_character_alive(self):
        """Test is_character_alive method."""
        game = Game()
        assert game.is_character_alive(Role.WEREWOLF) is True
        assert game.is_character_alive(Role.VILLAGER) is True

    def test_get_result_returns_none_when_not_ended(self):
        """Test get_result returns None when game is not ended."""
        game = Game()
        assert game.get_result() is None

    def test_state_switch_from_not_started(self):
        """Test state_switch from NOT_STARTED goes to EVENING."""
        game = Game()
        game.state_switch()
        assert game.state == GameState.EVENING

    def test_get_player_character(self):
        """Test get_player_character returns correct role."""
        game = Game()
        # Default game has player IDs 1-9
        role = game.get_player_character(1)
        assert isinstance(role, Role)

    def test_get_player_character_invalid_id_raises(self):
        """Test get_player_character raises ValueError for invalid ID."""
        game = Game()
        with pytest.raises(ValueError):
            game.get_player_character(999)

    def test_process_morning_voting_result_empty(self):
        """Test process_morning_voting_result with empty list."""
        game = Game()
        game.start()
        result = game.process_morning_voting_result([])
        assert result is False

    def test_process_morning_voting_result_tie(self):
        """Test process_morning_voting_result with tie votes."""
        game = Game()
        game.start()
        # Two players each get one vote - tie
        result = game.process_morning_voting_result([1, 2])
        assert result is False

    def test_process_morning_voting_result_success(self):
        """Test process_morning_voting_result with clear winner."""
        game = Game()
        game.start()
        # Player 1 gets 2 votes, player 2 gets 1 vote
        result = game.process_morning_voting_result([1, 1, 2])
        assert result is True

    def test_process_werewolf_voting_result_empty(self):
        """Test process_werewolf_voting_result with empty list."""
        game = Game()
        game.start()
        result = game.process_werewolf_voting_result([])
        assert result is False

    def test_process_werewolf_voting_result_success(self):
        """Test process_werewolf_voting_result with clear winner."""
        game = Game()
        game.start()
        result = game.process_werewolf_voting_result([1, 1])
        assert result is True

    def test_process_witch_saving(self):
        """Test process_witch_saving method."""
        game = Game()
        game.start()
        # First save should succeed (witch has antidote)
        result = game.process_witch_saving(1)
        assert result is True
        # Second save should fail (antidote used)
        result = game.process_witch_saving(2)
        assert result is False

    def test_process_witch_killing(self):
        """Test process_witch_killing method."""
        game = Game()
        game.start()
        # First kill should succeed (witch has poison)
        result = game.process_witch_killing(1)
        assert result is True
        # Second kill should fail (poison used)
        result = game.process_witch_killing(2)
        assert result is False

    def test_process_hunter_killing(self):
        """Test process_hunter_killing method."""
        game = Game()
        game.start()
        # First kill should succeed (hunter can shoot)
        result = game.process_hunter_killing(1)
        assert result is True
        # Second kill should fail (already shot)
        result = game.process_hunter_killing(2)
        assert result is False
