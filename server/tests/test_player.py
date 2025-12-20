"""Tests for Player class and Role enum."""

from game_logic.player import DeathReason, Player, Role


class TestRole:
    """Test cases for Role enum."""

    def test_role_enum_values(self):
        """Test Role enum values."""
        assert Role.VILLAGER.value == "villager"
        assert Role.WEREWOLF.value == "werewolf"
        assert Role.PROPHET.value == "prophet"
        assert Role.WITCH.value == "witch"
        assert Role.HUNTER.value == "hunter"
        assert Role.GUARD.value == "guard"


class TestPlayer:
    """Test cases for Player class."""

    def test_player_initialization(self):
        """Test that Player can be instantiated with required parameters."""
        player = Player(1, Role.VILLAGER)
        assert isinstance(player, Player)
        assert player.id == 1
        assert player.role == Role.VILLAGER
        assert player.is_alive is True

    def test_player_initial_attributes(self):
        """Test Player initial attribute values."""
        player = Player(1, Role.WITCH)
        assert player.witch_antidote is True
        assert player.witch_poison is True
        assert player.can_shoot is True
        assert not player.prophet_check_history
        assert player.survived_nights == 0
        assert player.vote_correct_counts == 0
        assert player.mistake_counts == 0

    def test_player_die(self):
        """Test Player.die() method sets is_alive to False."""
        player = Player(1, Role.VILLAGER)
        player.die(DeathReason.VOTED)
        assert player.is_alive is False

    def test_hunter_poison_disables_shot(self):
        """Test that hunter poisoned by witch cannot shoot."""
        hunter = Player(1, Role.HUNTER)
        assert hunter.can_shoot is True
        hunter.die(DeathReason.WITCH_POISON)
        assert hunter.is_alive is False
        assert hunter.can_shoot is False

    def test_hunter_other_death_keeps_shot(self):
        """Test that hunter killed by other means can still shoot."""
        hunter = Player(1, Role.HUNTER)
        hunter.die(DeathReason.WEREWOLF_KILLED)
        assert hunter.is_alive is False
        assert hunter.can_shoot is True

    def test_player_repr(self):
        """Test Player.__repr__() method."""
        player = Player(1, Role.VILLAGER)
        assert repr(player) == "Player(id=1, role=villager, Alive=True)"
        player.die(DeathReason.VOTED)
        assert repr(player) == "Player(id=1, role=villager, Alive=False)"
