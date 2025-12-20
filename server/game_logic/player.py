from enum import Enum
from typing import Any


class Role(Enum):
    """The character enum"""

    VILLAGER = "villager"
    WITCH = "witch"
    HUNTER = "hunter"
    WEREWOLF = "werewolf"
    PROPHET = "prophet"
    GUARD = "guard"


class DeathReason(Enum):
    """Possible death reasons"""

    WEREWOLF_KILLED = "werewolf_killed"
    WITCH_POISON = "witch_poison"
    VOTED = "voted"
    HUNTER_SHOT = "hunter_shot"


# pylint: disable=too-many-instance-attributes
class Player:
    """The player class."""

    def __init__(self, player_id: int, role: Role):
        self.id: int = player_id
        self.role: Role = role
        self.is_alive: bool = True

        self.witch_antidote: bool = True
        self.witch_poison: bool = True
        self.can_shoot: bool = True

        self.prophet_check_history: list[dict[str, Any]] = []

        self.survived_nights: int = 0
        self.vote_correct_counts: int = 0
        self.mistake_counts: int = 0

    def die(self, method: DeathReason) -> None:
        """
        Set the player's state to death
        """
        self.is_alive = False
        if self.role == Role.HUNTER and method == DeathReason.WITCH_POISON:
            self.can_shoot = False

    def __repr__(self) -> str:
        return (
            f"Player(id={self.id}, role={self.role.value}, "
            f"Alive={self.is_alive})"
        )
