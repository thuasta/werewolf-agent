"""Contains recorder class."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from game_logic.game_config import GameConfig
from game_logic.player import Role
from game_logic.result import GameResult


class Recorder:
    """The recorder for game replay.

    Records game events and provides serialization to file.
    Can save game information at any time, not just when game ends.
    """

    def __init__(self):
        """Initialize the recorder."""
        self.speech_log: List[Dict[str, Any]] = []
        self.vote_log: List[Dict[str, Any]] = []
        self.public_log: List[Dict[str, Any]] = []
        self.wolf_log: List[Dict[str, Any]] = []
        self.day_count = 0
        self.game_config: Optional[GameConfig] = None
        self.game_start_time: Optional[str] = None
        self.game_end_time: Optional[str] = None
        self.winner: Optional[str] = None
        self.players_info: List[Dict[str, Any]] = []

    def add_log(
        self, key: str, entry: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a log entry with timestamp.

        Args:
            key: The log type ("speech", "vote", "public", "wolf")
            entry: The log entry content (can be string or dict)
            metadata: Optional metadata to include with the log entry
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "day": self.day_count,
            "content": entry,
        }
        if metadata:
            log_entry.update(metadata)

        if key == "speech":
            self.speech_log.append(log_entry)
        elif key == "vote":
            self.vote_log.append(log_entry)
        elif key == "public":
            self.public_log.append(log_entry)
        elif key == "wolf":
            self.wolf_log.append(log_entry)

    def get_logs(self, key: str) -> List[Dict[str, Any]]:
        """Get all log entries for a given key.

        Args:
            key: The log type ("speech", "vote", "public", "wolf")

        Returns:
            List of log entries
        """
        if key == "speech":
            return self.speech_log
        elif key == "vote":
            return self.vote_log
        elif key == "public":
            return self.public_log
        elif key == "wolf":
            return self.wolf_log
        return []

    def clear_logs(self, key: str) -> None:
        """Clear all log entries for a given key.

        Args:
            key: The log type ("speech", "vote", "public", "wolf")
        """
        if key == "speech":
            self.speech_log.clear()
        elif key == "vote":
            self.vote_log.clear()
        elif key == "public":
            self.public_log.clear()
        elif key == "wolf":
            self.wolf_log.clear()

    def game_start(
        self,
        config: Optional[GameConfig] = None,
        players_info: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Handle game start event.

        Args:
            config: The game configuration
            players_info: List of player information (id, role, etc.)
        """
        self.game_start_time = datetime.now().isoformat()
        self.day_count = 0

        if config:
            self.game_config = config

        if players_info:
            self.players_info = players_info

        self.add_log("public", "Game started.", {"event": "game_start"})

    def game_end(self, winner: GameResult) -> None:
        """Handle game end event.

        Args:
            winner: The game result (GameResult enum)
        """
        self.game_end_time = datetime.now().isoformat()
        winner_str = (
            winner.name if isinstance(winner, GameResult) else str(winner)
        )
        self.winner = winner_str
        self.add_log(
            "public",
            f"Game ended. Winner: {winner_str}.",
            {"event": "game_end"},
        )

    def new_day(self) -> None:
        """Handle new day event."""
        self.day_count += 1
        self.add_log(
            "public", f"Day {self.day_count} begins.", {"event": "new_day"}
        )

    def record_speech(self, player_id: int, content: str) -> None:
        """Record a player's speech.

        Args:
            player_id: The ID of the player speaking
            content: The speech content
        """
        self.add_log(
            "speech", content, {"event": "speech", "player_id": player_id}
        )

    def record_vote(self, voter_id: int, target_id: Optional[int]) -> None:
        """Record a vote action.

        Args:
            voter_id: The ID of the player voting
            target_id: The ID of the player being voted (None if abstain)
        """
        target_str = str(target_id) if target_id is not None else "abstain"
        self.add_log(
            "vote",
            f"Player {voter_id} voted for {target_str}.",
            {"event": "vote", "voter_id": voter_id, "target_id": target_id},
        )

    def record_voting_result(
        self, voting_result: List[int], voted_out_player: Optional[int]
    ) -> None:
        """Record the voting result.

        Args:
            voting_result: List of all votes (player IDs voted for)
            voted_out_player: The ID of the player voted out (None if tie)
        """
        if voted_out_player is not None:
            self.add_log(
                "public",
                f"Player {voted_out_player} was voted out.",
                {
                    "event": "voting_result",
                    "voted_out_player": voted_out_player,
                    "vote_counts": self._count_votes(voting_result),
                },
            )
        else:
            self.add_log(
                "public",
                "Voting resulted in a tie. No one was voted out.",
                {
                    "event": "voting_result",
                    "voted_out_player": None,
                    "vote_counts": self._count_votes(voting_result),
                },
            )

    def record_wolf_action(
        self, werewolf_id: int, target_id: Optional[int]
    ) -> None:
        """Record werewolf voting action.

        Args:
            werewolf_id: The ID of the werewolf voting
            target_id: The ID of the player being targeted (None if abstain)
        """
        target_str = str(target_id) if target_id is not None else "abstain"
        self.add_log(
            "wolf",
            f"Werewolf {werewolf_id} voted to kill {target_str}.",
            {
                "event": "wolf_vote",
                "werewolf_id": werewolf_id,
                "target_id": target_id,
            },
        )

    def record_wolf_kill(self, target_id: Optional[int]) -> None:
        """Record werewolf kill result.

        Args:
            target_id: The ID of the player killed (None if no kill)
        """
        if target_id is not None:
            self.add_log(
                "public",
                f"Werewolves killed player {target_id}.",
                {"event": "wolf_kill", "target_id": target_id},
            )
        else:
            self.add_log(
                "public",
                "Werewolves did not kill anyone.",
                {"event": "wolf_kill", "target_id": None},
            )

    def record_witch_save(self, saved_player_id: Optional[int]) -> None:
        """Record witch saving action.

        Args:
            saved_player_id: The ID of the player saved (None if not saved)
        """
        if saved_player_id is not None:
            self.add_log(
                "public",
                f"Witch saved player {saved_player_id}.",
                {"event": "witch_save", "saved_player_id": saved_player_id},
            )

    def record_witch_kill(self, killed_player_id: Optional[int]) -> None:
        """Record witch poison action.

        Args:
            killed_player_id: The ID of the player killed by poison (None if not used)
        """
        if killed_player_id is not None:
            self.add_log(
                "public",
                f"Witch poisoned player {killed_player_id}.",
                {"event": "witch_kill", "killed_player_id": killed_player_id},
            )

    def record_hunter_kill(self, killed_player_id: Optional[int]) -> None:
        """Record hunter shooting action.

        Args:
            killed_player_id: The ID of the player killed by hunter (None if not used)
        """
        if killed_player_id is not None:
            self.add_log(
                "public",
                f"Hunter shot player {killed_player_id}.",
                {"event": "hunter_kill", "killed_player_id": killed_player_id},
            )

    def record_player_death(self, player_id: int, reason: str) -> None:
        """Record a player's death.

        Args:
            player_id: The ID of the player who died
            reason: The reason for death (e.g., "werewolf", "voting", "poison", "hunter")
        """
        self.add_log(
            "public",
            f"Player {player_id} died. Reason: {reason}.",
            {
                "event": "player_death",
                "player_id": player_id,
                "reason": reason,
            },
        )

    def record_prophet_check(
        self, prophet_id: int, checked_player_id: int, result: str
    ) -> None:
        """Record prophet's check action.

        Args:
            prophet_id: The ID of the prophet
            checked_player_id: The ID of the player checked
            result: The check result (e.g., "werewolf" or "not werewolf")
        """
        self.add_log(
            "public",
            f"Prophet {prophet_id} checked player {checked_player_id}. Result: {result}.",
            {
                "event": "prophet_check",
                "prophet_id": prophet_id,
                "checked_player_id": checked_player_id,
                "result": result,
            },
        )

    def record_night_phase(self) -> None:
        """Record the start of night phase."""
        self.add_log(
            "public",
            f"Night {self.day_count + 1} begins.",
            {"event": "night_start"},
        )

    def record_morning_phase(self) -> None:
        """Record the start of morning phase."""
        self.add_log(
            "public",
            f"Morning of Day {self.day_count} begins.",
            {"event": "morning_start"},
        )

    def _count_votes(self, voting_result: List[int]) -> Dict[int, int]:
        """Count votes for each player.

        Args:
            voting_result: List of all votes

        Returns:
            Dictionary mapping player ID to vote count
        """
        vote_counts: Dict[int, int] = {}
        for player_id in voting_result:
            vote_counts[player_id] = vote_counts.get(player_id, 0) + 1
        return vote_counts

    def to_dict(self) -> Dict[str, Any]:
        """Convert recorder data to dictionary for serialization.

        Returns:
            Dictionary containing all recorded game information
        """
        result: Dict[str, Any] = {
            "game_info": {
                "start_time": self.game_start_time,
                "end_time": self.game_end_time,
                "winner": self.winner,
                "day_count": self.day_count,
            },
            "logs": {
                "speech": self.speech_log,
                "vote": self.vote_log,
                "public": self.public_log,
                "wolf": self.wolf_log,
            },
        }

        if self.game_config:
            result["game_config"] = {
                "player_number": self.game_config.player_number,
                "character_count": {
                    role.value: count
                    for role, count in self.game_config.character_count.items()
                },
            }

        if self.players_info:
            result["players_info"] = self.players_info

        return result

    def save_to_file(self, filepath: str) -> None:
        """Save the recorded game information to a JSON file.

        Args:
            filepath: The path to save the file
        """
        data = self.to_dict()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filepath: str) -> "Recorder":
        """Load recorded game information from a JSON file.

        Args:
            filepath: The path to load the file from

        Returns:
            A Recorder instance with loaded data
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        recorder = cls()
        recorder.game_start_time = data.get("game_info", {}).get("start_time")
        recorder.game_end_time = data.get("game_info", {}).get("end_time")
        recorder.winner = data.get("game_info", {}).get("winner")
        recorder.day_count = data.get("game_info", {}).get("day_count", 0)

        logs = data.get("logs", {})
        recorder.speech_log = logs.get("speech", [])
        recorder.vote_log = logs.get("vote", [])
        recorder.public_log = logs.get("public", [])
        recorder.wolf_log = logs.get("wolf", [])

        if "players_info" in data:
            recorder.players_info = data["players_info"]

        return recorder
