from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Player:
    """Player data structure"""

    player_id: int  # Unique player ID
    name: str  # Player name
    is_alive: bool  # Whether alive or not
    role: Optional[str] = None  # Role (provided only when known)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "is_alive": self.is_alive,
            "role": self.role,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Player":
        """Create instance from dictionary"""
        return cls(**data)


@dataclass
class GameEvent:
    """Game event data structure"""

    event_type: str  # Event type
    day: int  # Day when event occurred
    phase: str  # Phase when event occurred
    data: Any  # Event data
    timestamp: datetime = field(default_factory=datetime.now)  # Timestamp

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "event_type": self.event_type,
            "day": self.day,
            "phase": self.phase,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class GameState:
    """Game state data structure"""

    day_number: int  # Current day number
    phase: str  # Current phase
    alive_players: List[Player]  # List of alive players
    dead_players: List[Player]  # List of dead players
    history: List[GameEvent]  # History of events

    def __post_init__(self):
        """Validate data after initialization"""
        if self.day_number < 0:
            raise ValueError("Day number cannot be negative")

    @property
    def all_players(self) -> List[Player]:
        """Get all players (alive + dead)"""
        return self.alive_players + self.dead_players

    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """Find player by ID"""
        for player in self.all_players:
            if player.player_id == player_id:
                return player
        return None

    def add_event(self, event: GameEvent) -> None:
        """Add event to history"""
        self.history.append(event)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "day_number": self.day_number,
            "phase": self.phase,
            "alive_players": [p.to_dict() for p in self.alive_players],
            "dead_players": [p.to_dict() for p in self.dead_players],
            "history": [e.to_dict() for e in self.history],
        }
