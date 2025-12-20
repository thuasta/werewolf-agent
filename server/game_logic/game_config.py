"""Contains the configuration of a game."""

from dataclasses import dataclass
from typing import Dict

from game_logic.player import Character


@dataclass
class GameConfig:
    """The game config class"""

    player_number: int
    character_count: Dict[Character, int]


NORMAL_CONFIG_6_PLAYER = GameConfig(
    6,
    {
        Character.VILLAGER: 2,
        Character.WEREWOLF: 2,
        Character.SEER: 1,
        Character.WITCH: 1,
    },
)

NORMAL_CONFIG_9_PLAYER = GameConfig(
    9,
    {
        Character.VILLAGER: 3,
        Character.WEREWOLF: 3,
        Character.SEER: 1,
        Character.WITCH: 1,
        Character.HUNTER: 1,
    },
)
