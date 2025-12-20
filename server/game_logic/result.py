"""Contains the game result enum."""

from enum import Enum, auto


class GameResult(Enum):
    """Represents the result of the game."""

    WEREWOLF_WIN = auto()
    VILLAGERS_WIN = auto()
