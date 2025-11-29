"""Type definitions for the Werewolf game."""

# pylint: disable=too-few-public-methods,unnecessary-ellipsis

from enum import Enum
from typing import Any, Dict, List, Protocol, TypedDict


class Role(Enum):
    """Player roles."""

    VILLAGER = "villager"
    WEREWOLF = "werewolf"
    WITCH = "witch"
    SEER = "seer"
    HUNTER = "hunter"


class SpeechRecord(TypedDict):
    """Speech record."""

    player_id: int
    content: str
    round: int
    phase: str


class DeathInfo(TypedDict):
    """Death information."""

    player_id: int
    round: int
    cause: str


class GameState(TypedDict, total=False):
    """Game state."""

    phase: str
    round: int
    alive_players: List[int]
    death_info: List[DeathInfo]


class KnowledgeBase(TypedDict, total=False):
    """Agent's accumulated game knowledge."""

    game_phase: str | None
    current_round: int
    history_speeches: List[SpeechRecord]
    vote_history: List[Dict[str, Any]]
    death_info: List[DeathInfo]
    alive_players: List[int]


class ActionResult(TypedDict, total=False):
    """Action result."""

    action_type: str
    success: bool
    message: str
    content: str
    vote_target: int
    target_id: int
    check_result: str


class SkillResult(TypedDict, total=False):
    """Skill usage result."""

    success: bool
    message: str
    target_id: int
    check_result: str


class SkillParams(TypedDict, total=False):
    """Skill parameters."""

    action: str
    target_id: int


class DecisionOutput(TypedDict, total=False):
    """Decision output for game API."""

    natural_speech: str
    vote_target: int
    skill_target: int
    reasoning_steps: List[str]
    suspicion_scores: Dict[int, float]


class AIClient(Protocol):
    """AI language model client protocol."""

    def generate(self, prompt: str) -> str:
        """Generate a response from the prompt."""
        ...


class BackendInterface(Protocol):
    """Backend communication protocol."""

    def get_speech_history(self, player_id: int) -> List[SpeechRecord]:
        """Get speech history for a player."""
        ...

    def get_game_state(self, player_id: int) -> GameState:
        """Get current game state."""
        ...

    def submit_speech(self, player_id: int, content: str) -> None:
        """Submit a speech."""
        ...

    def submit_vote(self, player_id: int, target_id: int) -> None:
        """Submit a vote."""
        ...

    def update_agent_action(self, player_id: int, action_result: ActionResult) -> None:
        """Update backend with action result."""
        ...

    def werewolf_kill(self, player_id: int, target_id: int) -> None:
        """Submit werewolf kill."""
        ...

    def witch_save(self, player_id: int, target_id: int) -> None:
        """Submit witch save."""
        ...

    def witch_poison(self, player_id: int, target_id: int) -> None:
        """Submit witch poison."""
        ...

    def seer_check(self, player_id: int, target_id: int) -> str:
        """Submit seer check. Returns 'good' or 'werewolf'."""
        ...

    def hunter_shoot(self, player_id: int, target_id: int) -> None:
        """Submit hunter shoot."""
        ...
