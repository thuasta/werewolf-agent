import json

from .interface import GameEvent, GameState, Player


class Message:
    def __init__(self, json_string: str = "{}"):
        try:
            self.msg = json.loads(json_string)
        except json.JSONDecodeError:
            self.msg = {}

    def json(self):
        try:
            return json.dumps(self.msg)
        except Exception:
            return "{}"


# server send InitializeMessage to agent
class InitializeMessage(Message):
    def __init__(
        self,
        token: str,
        player_id: int,
        role: str,
        role_description: str,
        all_players: list,
        game_config: dict,
    ):
        super().__init__()
        self.msg = {
            "type": "initialize",
            "token": token,
            "player_id": player_id,
            "role": role,
            "role_description": role_description,
            "all_players": all_players,
            "game_config": game_config,
        }


# agent send InitializeResponseMessage to server
class InitializeResponseMessage(Message):
    def __init__(self, token: str, status: str, message: str):
        super().__init__()
        self.msg = {
            "type": "initialize_response",
            "token": token,
            "status": status,
            "message": message,
        }


# server send WerewolfActionMessage to agent
class WerewolfActionMessage(Message):
    def __init__(
        self,
        token: str,
        game_state: GameState,
        night_numbers: int,
        alive_players: list,
        teammates: list,
        previous_votes: list,
    ):
        super().__init__()
        self.msg = {
            "type": "werewolf_action",
            "token": token,
            "game_state": game_state,
            "night_numbers": night_numbers,
            "alive_players": alive_players,
            "teammates": teammates,
            "previous_votes": previous_votes,
        }


# agent send WerewolfActionResponseMessage to server
class WerewolfActionResponseMessage(Message):
    def __init__(
        self, token: str, action: str, target_id: int, reasoning: str, confidence: float
    ):
        super().__init__()
        self.msg = {
            "type": "werewolf_action_response",
            "token": token,
            "action": action,
            "target_id": target_id,
            "reasoning": reasoning,
            "confidence": confidence,
        }


# sever send SeerActionMessage to agent
class SeerActionMessage(Message):
    def __init__(
        self,
        token: str,
        game_state: GameState,
        night_numbers: int,
        alive_players: list,
        previous_checks: list,
    ):
        super().__init__()
        self.msg = {
            "type": "seer_action",
            "token": token,
            "game_state": game_state,
            "night_numbers": night_numbers,
            "alive_players": alive_players,
            "previous_checks": previous_checks,
        }


# agent send SeerActionResponseMessage to server
class SeerActionResponseMessage(Message):
    def __init__(self, token: str, action: str, target_id: int, reasoning: str):
        super().__init__()
        self.msg = {
            "type": "seer_action_response",
            "token": token,
            "action": action,
            "target_id": target_id,
            "reasoning": reasoning,
        }


# server send WitchActionMessage to agent
class WitchActionMessage(Message):
    def __init__(
        self,
        token: str,
        game_state: GameState,
        night_numbers: int,
        alive_players: list,
        poison_available: bool,
        antidote_available: bool,
        killed_player_id: int,
        previous_actions: list,
    ):
        super().__init__()
        self.msg = {
            "type": "witch_action",
            "token": token,
            "game_state": game_state,
            "night_numbers": night_numbers,
            "alive_players": alive_players,
            "poison_available": poison_available,
            "antidote_available": antidote_available,
            "killed_player_id": killed_player_id,
            "previous_actions": previous_actions,
        }


# agent send WitchActionResponseMessage to server
class WitchActionResponseMessage(Message):
    def __init__(self, token: str, action: str, target_id: int, reasoning: str):
        super().__init__()
        self.msg = {
            "type": "witch_action_response",
            "token": token,
            "action": action,
            "target_id": target_id,
            "reasoning": reasoning,
        }


# server send HunterActionMessage to agent
class HunterActionMessage(Message):
    def __init__(
        self,
        token: str,
        game_state: GameState,
        cause: str,
        killed_by: int,
        alive_players: list,
    ):
        super().__init__()
        self.msg = {
            "type": "hunter_action",
            "token": token,
            "game_state": game_state,
            "cause": cause,
            "killed_by": killed_by,
            "alive_players": alive_players,
        }


# agent send HunterActionResponseMessage to server
class HunterActionResponseMessage(Message):
    def __init__(self, token: str, action: str, target_id: int, reasoning: str):
        super().__init__()
        self.msg = {
            "type": "hunter_action_response",
            "token": token,
            "action": action,
            "target_id": target_id,
            "reasoning": reasoning,
        }


# server send DiscussMessage to agent
class DiscussMessage(Message):
    def __init__(
        self,
        token: str,
        game_state: GameState,
        day_number: int,
        speech_order: int,
        previous_speeches: list,
        last_night_events: list,
        remaining_time: int,
    ):
        super().__init__()
        self.msg = {
            "type": "discuss",
            "token": token,
            "game_state": game_state,
            "day_number": day_number,
            "speech_order": speech_order,
            "previous_speeches": previous_speeches,
            "last_night_events": last_night_events,
            "remaining_time": remaining_time,
        }


# agent send DiscussResponseMessage to server
class DiscussResponseMessage(Message):
    def __init__(
        self,
        token: str,
        speech: str,
        emotion: str,
        target_players: int,
        is_accusation: bool,
    ):
        super().__init__()
        self.msg = {
            "type": "discuss_response",
            "token": token,
            "speech": speech,
            "emotion": emotion,
            "target_players": target_players,
            "is_accusation": is_accusation,
        }


# server send VoteMessage to agent
class VoteMessage(Message):
    def __init__(
        self,
        token: str,
        game_state: GameState,
        day_number: int,
        alive_players: list,
        discussion_summary: str,
        previous_votes: list,
        vote_type: str,
    ):
        super().__init__()
        self.msg = {
            "type": "vote",
            "token": token,
            "game_state": game_state,
            "day_number": day_number,
            "alive_players": alive_players,
            "discussion_summary": discussion_summary,
            "previous_votes": previous_votes,
            "vote_type": vote_type,
        }


# agent send VoteResponseMessage to server
class VoteResponseMessage(Message):
    def __init__(self, token: str, vote_target: int, reasoning: str, confidence: float):
        super().__init__()
        self.msg = {
            "type": "vote_response",
            "token": token,
            "vote_target": vote_target,
            "reasoning": reasoning,
            "confidence": confidence,
        }


# server send DefendMessage to agent
class DefendMessage(Message):
    def __init__(
        self, token: str, game_state: GameState, accusations: list, time_limit: int
    ):
        super().__init__()
        self.msg = {
            "type": "defend",
            "token": token,
            "game_state": game_state,
            "accusations": accusations,
            "time_limit": time_limit,
        }


# agent send DefendResponseMessage to server
class DefendResponseMessage(Message):
    def __init__(
        self, token: str, defense: str, counter_arguments: list, emotional_tone: str
    ):
        super().__init__()
        self.msg = {
            "type": "defend_response",
            "token": token,
            "defense": defense,
            "counter_arguments": counter_arguments,
            "emotional_tone": emotional_tone,
        }


# server send GameOverMessage to agent
class GameOverMessage(Message):
    def __init__(
        self,
        token: str,
        winner: str,
        winning_players: list,
        final_state: GameState,
        role_reveal: list,
        performance_stats: list,
    ):
        super().__init__()
        self.msg = {
            "type": "game_over",
            "token": token,
            "winner": winner,
            "winning_players": winning_players,
            "final_state": final_state,
            "role_reveal": role_reveal,
            "performance_stats": performance_stats,
        }


# agent send GameOverResponseMessage to server
class GameOverResponseMessage(Message):
    def __init__(self, token: str, status: str, reflection: str, rating: float):
        self.msg = {
            "type": "game_over",
            "token": token,
            "status": status,
            "reflection": reflection,
            "rating": rating,
        }
