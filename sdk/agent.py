"""AI Agent for the Werewolf game."""

import json
import logging
import random
from typing import Any

from sdk.game_types import (
    AIClient,
    ActionResult,
    BackendInterface,
    GameState,
    KnowledgeBase,
    Role,
    SkillParams,
    SkillResult,
    SpeechRecord,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Agent:
    """AI Agent for playing the Werewolf game.

    Attributes:
        player_id: Player identifier (1-9).
        role: Assigned role.
        api_client: AI language model client.
        is_alive: Alive status.
        vote_target: Last vote target.
        skill_used: Skill usage status.
        knowledge_base: Accumulated game knowledge.
    """

    def __init__(
        self,
        player_id: int,
        role: Role,
        api_client: AIClient | None = None,
    ) -> None:
        self.player_id = player_id
        self.role = role
        self.api_client = api_client
        self.is_alive = True
        self.vote_target: int | None = None
        self.skill_used = False
        self.knowledge_base: KnowledgeBase = {
            "game_phase": None,
            "current_round": 0,
            "history_speeches": [],
            "vote_history": [],
            "death_info": [],
        }

    def interact_with_ai(self, prompt: str, context: dict[str, Any]) -> str:
        """Send prompt to AI and get response. Falls back to simulation if unavailable."""
        if self.api_client is None:
            return self._simulate_ai_response(prompt, context)

        try:
            full_prompt = self._construct_full_prompt(prompt, context)
            response = self.api_client.generate(full_prompt)
            return response
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("AI API call failed: %s", e)
            return self._simulate_ai_response(prompt, context)

    def get_history_speeches(
        self, backend_interface: BackendInterface
    ) -> list[SpeechRecord]:
        """Fetch and cache speech history from backend."""
        try:
            history = backend_interface.get_speech_history(self.player_id)
            self.knowledge_base["history_speeches"] = history
            return history
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to get speech history: %s", e)
            return []

    def get_current_state(self, backend_interface: BackendInterface) -> GameState:
        """Fetch and cache current game state from backend."""
        try:
            state = backend_interface.get_game_state(self.player_id)
            self.knowledge_base["game_phase"] = state.get("phase")
            self.knowledge_base["current_round"] = state.get("round", 0)
            self.knowledge_base["alive_players"] = state.get("alive_players", [])
            self.knowledge_base["death_info"] = state.get("death_info", [])
            return state
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to get game state: %s", e)
            return {}

    def speak(
        self,
        backend_interface: BackendInterface,
        speech_type: str = "normal",
    ) -> str:
        """Generate and submit a speech. Returns empty string if dead."""
        if not self.is_alive:
            return ""

        self.get_current_state(backend_interface)
        history = self.get_history_speeches(backend_interface)

        context = {
            "player_id": self.player_id,
            "role": self.role.value,
            "game_phase": self.knowledge_base["game_phase"],
            "speech_type": speech_type,
            "history": history[-10:],
            "alive_players": self.knowledge_base.get("alive_players", []),
        }

        prompt = self._construct_speech_prompt(context)
        speech_content = self.interact_with_ai(prompt, context)

        try:
            backend_interface.submit_speech(self.player_id, speech_content)
            return speech_content
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to submit speech: %s", e)
            return speech_content

    def vote(
        self,
        backend_interface: BackendInterface,
        target_id: int | None = None,
    ) -> int:
        """Cast a vote. If target_id is None, AI decides. Returns -1 if dead."""
        if not self.is_alive:
            return -1

        if target_id is not None:
            vote_target = target_id
        else:
            context = {
                "player_id": self.player_id,
                "role": self.role.value,
                "game_phase": self.knowledge_base["game_phase"],
                "alive_players": self.knowledge_base.get("alive_players", []),
                "history": self.knowledge_base["history_speeches"][-5:],
            }

            prompt = self._construct_vote_prompt(context)
            ai_response = self.interact_with_ai(prompt, context)
            vote_target = self._parse_vote_decision(ai_response)

        self.vote_target = vote_target

        try:
            backend_interface.submit_vote(self.player_id, vote_target)
            return vote_target
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to submit vote: %s", e)
            return vote_target

    def use_skill(
        self,
        backend_interface: BackendInterface,
        skill_params: SkillParams | None = None,
    ) -> SkillResult:
        """Use role-specific skill. Returns failure if dead or already used."""
        if not self.is_alive or self.skill_used:
            return {"success": False, "message": "Cannot use skill"}

        if skill_params is None:
            skill_params = {}

        skill_result: SkillResult = {"success": False, "message": ""}

        if self.role == Role.WEREWOLF:
            skill_result = self._use_werewolf_skill(backend_interface, skill_params)
        elif self.role == Role.WITCH:
            skill_result = self._use_witch_skill(backend_interface, skill_params)
        elif self.role == Role.SEER:
            skill_result = self._use_seer_skill(backend_interface, skill_params)
        elif self.role == Role.HUNTER:
            skill_result = self._use_hunter_skill(backend_interface, skill_params)

        if skill_result.get("success", False):
            self.skill_used = True

        return skill_result

    def act(
        self,
        backend_interface: BackendInterface,
        action_type: str,
        **kwargs: Any,
    ) -> ActionResult:
        """Perform action ('speak', 'vote', 'use_skill') and update backend."""
        result: ActionResult = {"action_type": action_type, "success": False}

        try:
            if action_type == "speak":
                speech_type = kwargs.get("speech_type", "normal")
                content = self.speak(backend_interface, speech_type)
                result["success"] = True
                result["content"] = content

            elif action_type == "vote":
                target_id = kwargs.get("target_id")
                vote_target = self.vote(backend_interface, target_id)
                result["success"] = True
                result["vote_target"] = vote_target

            elif action_type == "use_skill":
                skill_params = kwargs.get("skill_params", {})
                skill_result = self.use_skill(backend_interface, skill_params)
                result["success"] = skill_result.get("success", False)
                result["message"] = skill_result.get("message", "")

            backend_interface.update_agent_action(self.player_id, result)

        except Exception as e:  # pylint: disable=broad-exception-caught
            result["message"] = f"Action failed: {e}"

        return result

    def _use_werewolf_skill(
        self,
        backend_interface: BackendInterface,
        skill_params: SkillParams,
    ) -> SkillResult:
        """Execute the werewolf kill skill."""
        target_id = skill_params.get("target_id")
        if target_id is None:
            context = self._get_skill_context()
            prompt = (
                "As a werewolf, choose a player to kill tonight. "
                "Return only the player ID number:"
            )
            ai_response = self.interact_with_ai(prompt, context)
            target_id = self._parse_number_from_response(ai_response)

        try:
            backend_interface.werewolf_kill(self.player_id, target_id)
            return {
                "success": True,
                "message": f"Werewolf chose to kill player {target_id}",
                "target_id": target_id,
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {"success": False, "message": f"Werewolf kill failed: {e}"}

    def _use_witch_skill(
        self,
        backend_interface: BackendInterface,
        skill_params: SkillParams,
    ) -> SkillResult:
        """Execute the witch save or poison skill."""
        action = skill_params.get("action")
        target_id = skill_params.get("target_id")

        context = self._get_skill_context()

        if action is None:
            prompt = (
                "As a witch, decide whether to use antidote or poison. "
                "Return 'save X' or 'poison X' or 'abstain':"
            )
            ai_response = self.interact_with_ai(prompt, context)
            action, target_id = self._parse_witch_decision(ai_response)

        try:
            if action == "save":
                backend_interface.witch_save(self.player_id, target_id)
                return {
                    "success": True,
                    "message": f"Witch used antidote to save player {target_id}",
                }
            if action == "poison":
                backend_interface.witch_poison(self.player_id, target_id)
                return {
                    "success": True,
                    "message": f"Witch used poison on player {target_id}",
                }
            return {"success": True, "message": "Witch chose not to use skill"}
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {"success": False, "message": f"Witch skill failed: {e}"}

    def _use_seer_skill(
        self,
        backend_interface: BackendInterface,
        skill_params: SkillParams,
    ) -> SkillResult:
        """Execute the seer check skill."""
        target_id = skill_params.get("target_id")
        if target_id is None:
            context = self._get_skill_context()
            prompt = (
                "As a seer, choose a player to check. "
                "Return only the player ID number:"
            )
            ai_response = self.interact_with_ai(prompt, context)
            target_id = self._parse_number_from_response(ai_response)

        try:
            check_result = backend_interface.seer_check(self.player_id, target_id)
            return {
                "success": True,
                "message": (
                    f"Seer checked player {target_id}, " f"result is {check_result}"
                ),
                "check_result": check_result,
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {"success": False, "message": f"Seer check failed: {e}"}

    def _use_hunter_skill(
        self,
        backend_interface: BackendInterface,
        skill_params: SkillParams,
    ) -> SkillResult:
        """Execute the hunter shoot skill."""
        target_id = skill_params.get("target_id")
        if target_id is None:
            context = self._get_skill_context()
            prompt = (
                "As a hunter, choose a player to shoot. "
                "Return only the player ID number (or 0 to not shoot):"
            )
            ai_response = self.interact_with_ai(prompt, context)
            target_id = self._parse_number_from_response(ai_response)

        if target_id == 0:
            return {"success": True, "message": "Hunter chose not to shoot"}

        try:
            backend_interface.hunter_shoot(self.player_id, target_id)
            return {
                "success": True,
                "message": f"Hunter shot player {target_id}",
                "target_id": target_id,
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {"success": False, "message": f"Hunter shoot failed: {e}"}

    def _construct_speech_prompt(self, context: dict[str, Any]) -> str:
        """Construct the prompt for generating a speech."""
        role_descriptions = {
            Role.VILLAGER.value: (
                "You are a villager, you need to find the werewolves"
            ),
            Role.WEREWOLF.value: (
                "You are a werewolf, disguise as a good player "
                "and protect your teammates"
            ),
            Role.WITCH.value: (
                "You are a witch, guide the good faction with your speech"
            ),
            Role.SEER.value: ("You are a seer, carefully reveal check information"),
            Role.HUNTER.value: (
                "You are a hunter, speak cautiously to avoid being pushed out"
            ),
        }

        role_desc = role_descriptions.get(
            context.get("role", ""), context.get("role", "")
        )

        prompt = f"""
You are playing a Werewolf game.
Your role: {role_desc}
Player ID: {self.player_id}
Game phase: {context['game_phase']}
Alive players: {context['alive_players']}
Speech type: {context['speech_type']}

Recent speech history:
{self._format_speech_history(context['history'])}

Please make a speech based on the above information. Requirements:
1. Stay consistent with your role identity
2. Analyze the situation and provide reasonable deductions
3. Speak naturally like a human player
4. Keep the length between 50-150 words

Your speech:
"""
        return prompt

    def _construct_vote_prompt(self, context: dict[str, Any]) -> str:
        """Construct the prompt for making a vote decision."""
        prompt = f"""
As a {context['role']} (Player {self.player_id}), decide who to vote for \
based on the current situation.
Alive players: {context['alive_players']}
Game phase: {context['game_phase']}

Analyze and return only the player ID number you want to vote for.
Vote target:
"""
        return prompt

    def _get_skill_context(self) -> dict[str, Any]:
        """Get the context for skill usage."""
        return {
            "player_id": self.player_id,
            "role": self.role.value,
            "alive_players": self.knowledge_base.get("alive_players", []),
            "history": self.knowledge_base["history_speeches"][-5:],
            "death_info": self.knowledge_base.get("death_info", []),
        }

    def _construct_full_prompt(self, prompt: str, context: dict[str, Any]) -> str:
        """Construct the full AI prompt with context."""
        full_context = {
            "role": self.role.value,
            "player_id": self.player_id,
            "game_state": dict(self.knowledge_base),
            **context,
        }
        return (
            f"Context: {json.dumps(full_context, ensure_ascii=False)}\n\n"
            f"Question: {prompt}"
        )

    def _simulate_ai_response(self, prompt: str, context: dict[str, Any]) -> str:
        """Simulate an AI response for testing purposes."""
        alive_players = context.get("alive_players", list(range(1, 10)))
        other_players = [p for p in alive_players if p != self.player_id]

        simulated_responses = {
            "speech": (
                f"I am player {self.player_id}, as a {self.role.value}, "
                "I think we need to carefully analyze the current situation."
            ),
            "vote": str(random.choice(other_players) if other_players else 1),
            "skill": "Based on the current situation, I choose to act.",
        }

        prompt_lower = prompt.lower()
        if "speech" in prompt_lower or "speak" in prompt_lower:
            return simulated_responses["speech"]
        if "vote" in prompt_lower:
            return simulated_responses["vote"]
        return simulated_responses["skill"]

    def _format_speech_history(self, history: list[SpeechRecord]) -> str:
        """Format the speech history for display."""
        formatted = []
        for speech in history:
            player_id = speech.get("player_id", "?")
            content = speech.get("content", "")
            formatted.append(f"Player {player_id}: {content}")
        return "\n".join(formatted)

    def _parse_vote_decision(self, ai_response: str) -> int:
        """Parse the vote decision from AI response."""
        try:
            numbers = [int(s) for s in ai_response.split() if s.isdigit()]
            if numbers:
                return numbers[0]
        except ValueError:
            pass

        alive_players = self.knowledge_base.get("alive_players", list(range(1, 10)))
        other_players = [p for p in alive_players if p != self.player_id]
        return random.choice(other_players) if other_players else -1

    def _parse_number_from_response(self, response: str) -> int:
        """Parse a number from the AI response."""
        try:
            numbers = [int(s) for s in response.split() if s.isdigit()]
            return numbers[0] if numbers else 0
        except ValueError:
            return 0

    def _parse_witch_decision(self, response: str) -> tuple[str, int]:
        """Parse the witch's decision from AI response."""
        response_lower = response.lower()
        if "save" in response_lower:
            numbers = [int(s) for s in response.split() if s.isdigit()]
            return "save", numbers[0] if numbers else 0
        if "poison" in response_lower:
            numbers = [int(s) for s in response.split() if s.isdigit()]
            return "poison", numbers[0] if numbers else 0
        return "abstain", 0

    def update_status(self, new_status: dict[str, Any]) -> None:
        """Update agent status from dictionary."""
        if "is_alive" in new_status:
            self.is_alive = new_status["is_alive"]
        if "skill_used" in new_status:
            self.skill_used = new_status["skill_used"]

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Agent(Player {self.player_id}, "
            f"Role: {self.role.value}, "
            f"Alive: {self.is_alive})"
        )
