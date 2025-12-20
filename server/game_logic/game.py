"""Contains Game Class"""

import random
from enum import Enum, auto
from typing import List, Optional

from game_logic.game_config import NORMAL_CONFIG_9_PLAYER, GameConfig
from game_logic.player import DeathReason, Player, Role
from game_logic.result import GameResult


class GameState(Enum):
    """
    Represent the state of the game.
    """

    NOT_STARTED = auto()
    EVENING = auto()
    MORNING = auto()
    FINISHED = auto()


# pylint: disable=too-many-instance-attributes
class Game:
    """The game state class"""

    def __init__(self, config: GameConfig = NORMAL_CONFIG_9_PLAYER) -> None:
        """
        Initialize the game.
        Args:
            roles: Optional list of roles to assign to players.
            If None, players should be set separately.
        """
        self.state = GameState.NOT_STARTED
        # the player list. the player with ID `i` is _player[i - 1] since in
        # werewolf game, the index begin at 1.
        self._players: List[Player] = []
        self.day: int = 0
        self._running: bool = True
        # Track night actions
        # Player killed by werewolves
        self._night_killed_player: Optional[int] = None
        self._witch_saved_player: Optional[int] = None  # Player saved by witch
        # Player killed by witch
        self._witch_killed_player: Optional[int] = None
        # Player killed by hunter
        self._hunter_killed_player: Optional[int] = None

        # Initialize players if roles provided
        roles: List[Role] = []
        for role, count in config.character_count.items():
            roles.extend([role] * count)
        if len(roles) != config.player_number:
            raise ValueError(
                f"Config Error: Sum of roles ({len(roles)}) does not match "
                f"player_number ({config.player_number})"
            )
        player_ids = list(range(1, 10))
        for i, role in enumerate(roles):
            self._players.append(Player(player_ids[i], Role(role)))

    def start(self) -> None:
        """
        Start the game. Only useful when the state is `NOT_STARTED`.
        After started, the state will be `EVENING`.
        """
        # Assign the character, shuffle the id of the players
        # If the player needs any initialization operations, do it.
        if self.state != GameState.NOT_STARTED:
            raise ValueError(
                "Game can only be started when state is NOT_STARTED"
            )

        # Shuffle player IDs if not already done
        if self._players:
            player_ids = [p.id for p in self._players]
            random.shuffle(player_ids)
            for i, player in enumerate(self._players):
                player.id = player_ids[i]

        # Initialize game state
        self.state = GameState.EVENING
        self.day = 0
        self._running = True

    def _sun_rise(self) -> None:
        """Going from night to morning."""
        if self.state != GameState.EVENING:
            raise ValueError("Can only call _sun_rise when state is EVENING")

        # Process night actions
        self._process_night_actions()

        # Reset night action tracking
        self._night_killed_player = None
        self._witch_saved_player = None
        self._witch_killed_player = None
        self._hunter_killed_player = None

        # Increment day and change state
        self.day += 1
        self.state = GameState.MORNING

    def _sun_set(self) -> None:
        """Going from morning to evening."""
        if self.state != GameState.MORNING:
            raise ValueError("Can only call _sun_set when state is MORNING")

        # Update survived nights for alive players
        for player in self._players:
            if player.is_alive:
                player.survived_nights += 1

        self.state = GameState.EVENING

    def is_end(self) -> bool:
        """
        Checks if the game is already end.
        Returns:
        bool: if the game is end.
        """
        if self.state == GameState.FINISHED:
            return True

        alive_werewolves = sum(
            1 for p in self._players if p.is_alive and p.role == Role.WEREWOLF
        )
        alive_villagers = sum(
            1 for p in self._players if p.is_alive and p.role == Role.VILLAGER
        )
        alive_gods = sum(
            1
            for p in self._players
            if p.is_alive and p.role not in (Role.WEREWOLF, Role.VILLAGER)
        )

        # Game ends if all werewolves are dead (villagers win)
        # or if werewolves equal or outnumber villagers (werewolves win)
        return alive_werewolves == 0 or alive_werewolves >= (
            alive_villagers + alive_gods
        )

    def is_character_alive(self, character: Role) -> bool:
        """
        Checks if the given character has at least one player alive
        Args:
            character(Role): the character to be checked
        Returns:
        bool: if the given character has someone(>0) alive
        """
        return any(p.is_alive and p.role == character for p in self._players)

    def get_result(self) -> Optional[GameResult]:
        """
        Get the game result if the game is end

        Returns:
            the game result if game is end, else you'll get None.
        """
        if not self.is_end():
            return None

        # Count alive werewolves
        alive_werewolves = 0
        alive_villagers = 0
        alive_gods = 0

        for p in self._players:
            if not p.is_alive:
                continue

            if p.role == Role.WEREWOLF:
                alive_werewolves += 1
            elif p.role == Role.VILLAGER:
                alive_villagers += 1
            else:
                # Any role that is not Werewolf or Villager is considered a God
                alive_gods += 1

        if alive_werewolves == 0:
            return GameResult.VILLAGERS_WIN
        if alive_werewolves >= (alive_villagers + alive_gods):
            return GameResult.WEREWOLF_WIN
        return None

    def state_switch(self) -> None:
        """
        Maintaining the state machine for `self`, should be called when:
        - Switching from day to night
        - Switching from night to day
        Only this method can change the state into `end`.
        """
        if self.state == GameState.NOT_STARTED:
            # Not Started --> Evening: do exactly the same thing as Start()
            self.start()
        elif self.state == GameState.EVENING:
            # Evening --> Morning or End
            self._sun_rise()
            # Check if game ends after night actions
            if self.is_end():
                self.state = GameState.FINISHED
                self._running = False
        elif self.state == GameState.MORNING:
            # Morning --> Evening or End
            # Check if game ends after voting
            # (should be checked before calling state_switch)
            if self.is_end():
                self.state = GameState.FINISHED
                self._running = False
            else:
                self._sun_set()
        # FINISHED state doesn't change

    def process_morning_voting_result(self, voting_result: List[int]) -> bool:
        """
        Process the voting result.
        Args:
            voting_result (List[int]): the list of voted players' ID
        Returns:
            bool: True if a player was successfully voted out,
                  False if there's a tie
        """
        if not voting_result:
            return False

        # Count votes for each player
        vote_count: dict[int, int] = {}
        for player_id in voting_result:
            if player_id in vote_count:
                vote_count[player_id] += 1
            else:
                vote_count[player_id] = 1

        # Find the maximum vote count
        if not vote_count:
            return False

        max_votes = max(vote_count.values())

        # Find all players with max votes
        max_voted_players = [
            pid for pid, votes in vote_count.items() if votes == max_votes
        ]

        # If there's a tie (multiple players with max votes), return False
        if len(max_voted_players) > 1:
            return False

        # Execute the vote - kill the player with most votes
        voted_player_id = max_voted_players[0]
        player = self._get_player_by_id(voted_player_id)
        if player and player.is_alive:
            player.die(DeathReason.VOTED)
            return True

        return False

    def process_werewolf_voting_result(self, voting_result: List[int]) -> bool:
        """
        Process the voting result in the night, when werewolves is killing.
        Args:
            voting_result (List[int]): the list of voted players' ID
        Returns:
            bool: True if a player was successfully voted to be killed,
                  False if there's a tie
        """
        if not voting_result:
            return False

        # Count votes for each player
        vote_count: dict[int, int] = {}
        for player_id in voting_result:
            if player_id in vote_count:
                vote_count[player_id] += 1
            else:
                vote_count[player_id] = 1

        # Find the maximum vote count
        if not vote_count:
            return False

        max_votes = max(vote_count.values())

        # Find all players with max votes
        max_voted_players = [
            pid for pid, votes in vote_count.items() if votes == max_votes
        ]

        # If there's a tie (multiple players with max votes), return False
        if len(max_voted_players) > 1:
            return False

        # Set the night killed player
        # (will be processed in _process_night_actions)
        voted_player_id = max_voted_players[0]
        self._night_killed_player = voted_player_id
        return True

    def process_witch_saving(self, saved_player: int) -> bool:
        """
        Process the witch saving player.
        Args:
            saved_player(int): the saved player's ID
        Returns:
            bool: True if saving was successful, False otherwise
        """
        # Find the witch player
        witch = self._get_player_by_role(Role.WITCH)
        if not witch or not witch.is_alive:
            return False

        # Check if witch still has antidote
        if not witch.witch_antidote:
            return False

        # Save the player and consume antidote
        self._witch_saved_player = saved_player
        witch.witch_antidote = False
        return True

    def process_witch_killing(self, killed_player: int) -> bool:
        """
        Process the witch killing player.
        Args:
            killed_player(int): the killed player's ID
        Returns:
            bool: True if killing was successful, False otherwise
        """
        # Find the witch player
        witch = self._get_player_by_role(Role.WITCH)
        if not witch or not witch.is_alive:
            return False

        # Check if witch still has poison
        if not witch.witch_poison:
            return False

        # Set the player to be killed and consume poison
        self._witch_killed_player = killed_player
        witch.witch_poison = False
        return True

    def process_hunter_killing(self, killed_player: int) -> bool:
        """
        Process the hunter killing player.
        Args:
            killed_player(int): the killed player's ID
        Returns:
            bool: True if killing was successful, False otherwise
        """
        # Find the hunter player
        hunter = self._get_player_by_role(Role.HUNTER)
        if not hunter or not hunter.is_alive:
            return False

        # Check if hunter can shoot
        if not hunter.can_shoot:
            return False

        # Set the player to be killed
        self._hunter_killed_player = killed_player
        hunter.can_shoot = False  # Hunter can only shoot once
        return True

    def get_player_character(self, player_id: int) -> Role:
        """
        Get the character of a player
        Args:
            player_id(int): the player's ID
        Returns:
        Role: The character of the player
        """
        player = self._get_player_by_id(player_id)
        if player:
            return player.role
        raise ValueError(f"Player with ID {player_id} not found")

    def _get_player_by_id(self, player_id: int) -> Optional[Player]:
        """Helper method to get player by ID."""
        for player in self._players:
            if player.id == player_id:
                return player
        return None

    def _get_player_by_role(self, role: Role) -> Optional[Player]:
        """Helper method to get the first alive player with the given role."""
        for player in self._players:
            if player.is_alive and player.role == role:
                return player
        return None

    def _process_night_actions(self) -> None:
        """Process all night actions in the correct order."""
        # Order: Werewolf kill -> Witch save -> Witch kill -> Hunter kill

        # 1. Werewolf kill (if not saved)
        if self._night_killed_player is not None:
            killed_player = self._get_player_by_id(self._night_killed_player)
            # Check if saved by witch
            if killed_player and killed_player.id != self._witch_saved_player:
                killed_player.die(DeathReason.WEREWOLF_KILLED)

        # 2. Witch kill
        if self._witch_killed_player is not None:
            killed_player = self._get_player_by_id(self._witch_killed_player)
            if killed_player and killed_player.is_alive:
                killed_player.die(DeathReason.WITCH_POISON)

        # 3. Hunter kill (if hunter died and can shoot)
        if self._hunter_killed_player is not None:
            killed_player = self._get_player_by_id(self._hunter_killed_player)
            if killed_player and killed_player.is_alive:
                killed_player.die(DeathReason.HUNTER_SHOT)
