"""Tests for Player class and Character enum."""

from game_logic.player import Character, Player


class TestPlayer:
    """Test cases for Player class."""

    def test_player_initialization(self):
        """Test that Player can be instantiated."""
        player = Player()
        assert isinstance(player, Player)

    def test_character_enum(self):
        """Test Character enum values."""
        assert Character.VILLAGER.value == "villager"
        assert Character.WEREWOLF.value == "werewolf"
        assert Character.SEER.value == "seer"
        assert Character.WITCH.value == "witch"
        assert Character.HUNTER.value == "hunter"
        assert Character.GUARD.value == "guard"
