"""Contains game runner class.

Game runner is used to deal with main game logic. It uses the model classes like
`Game` and `Player` and interacts with `AgentServer` and `Recorder`.

When using, first create a GameRunner instance and then bind it to your AgentServer
and Recorder.
"""

import asyncio
from http import server
from typing import Optional

from asyncio.base_events import logger

from agent_server.agent_server import AgentServer
from game_logic.game import Game, GameState
from game_logic.game_config import GameConfig
from recorder.recorder import Recorder


class GameRunner:
    """The game runner class, which controls the game progress.

    Attributes:
        config: The game config used to initialize a game.
    """

    def __init__(self, config: GameConfig):
        self.config = config
        self._game: Optional[Game] = None
        self._agent_server: Optional[AgentServer] = None
        self._recorder: Optional[Recorder] = None

        self._task: Optional[asyncio.Task[None]] = None

        self._lock = asyncio.Lock()  

        # players that are already connected, different from config.player_number
        self.player_count = 0

    
    async def start(self) -> None:
        """Start the game.

        Start a game when it's not running. If the game is already started, then
        raise. This coroutine should be awaited, and it will finish immediately,
        leaving a running game task.

        Rules:
            - If the game is already running: raise RuntimeError.
            - If required components (AgentServer/Recorder) are not bound: raise RuntimeError.
            - If player count is insufficient: raise RuntimeError.
            - Otherwise: initialize Game, start game loop task, update running state.

        This coroutine finishes immediately after starting the game task (non-blocking).

        Raises:
            RuntimeError: If game is running, components are missing, or players are insufficient.
        """
        async with self._lock:

            if self.IsRunning:
                raise RuntimeError("Cannot start game: game is already running")
            
            if self._agent_server is None:
                raise RuntimeError("Cannot start game: AgentServer is not bound")
            if self._recorder is None:
                raise RuntimeError("Cannot start game: Recorder is not bound")

            if self.player_count < self.config.player_number:
                raise RuntimeError(
                    f"Cannot start game: insufficient players (need {self.config.player_number}, "
                    f"current {self.player_count})"
                )

            if self._game is None:
                self._game = Game(self.config)
            else:
                raise RuntimeError("Cannot start game: Game already started")

            # record initial info of the game 
            self._recorder.game_start(
                config=self.config
            )

            self._task: asyncio.Task[None] = asyncio.create_task(self._game_loop())

    async def _game_loop(self) -> None:
        """Internal game loop (core logic, runs in background task)."""
        try:
            while self._game:
                player_actions = await self._agent_server.get_player_actions()
                
                game_state = self._game.step(player_actions)
                
                self._recorder.record_game_state(self._game, game_state)
                
                if game_state == GameState.FINISHED:
                    logger.info(f"Game finished (game_id: {self._game.game_id})")
                    await self.stop()
                    break
                


        except Exception as e:
            # error found, now stopped
            logger.error(f"Game loop error (game_id: {self._game.game_id}): {str(e)}", exc_info=True)
            self._recorder.record_game_error(self._game.game_id, str(e))
            await self.stop()
            raise

    def _record_game_state(self, game_state: GameState) -> None:
        """record incidents"""
        if not self._game or not self._recorder:
            return
        
        """record night-day shifting"""
        if game_state == GameState.NIGHT:
            self._recorder.record_night_phase()
        elif game_state == GameState.MORNING:
            self._recorder.record_morning_phase()
        elif game_state == GameState.DAY:
            self._recorder.new_day()

        """record player's death"""
        for player in self._game.players:
            if player.is_dead:
                self._recorder.record_player_death(
                    player_id=player.player_id,
                    reason=player.death_reason or "unknown"
                )

        """record prophet"""
        if hasattr(self._game, 'last_prophet_check'):
            check = self._game.last_prophet_check
            self._recorder.record_prophet_check(
                prophet_id=check["prophet_id"],
                checked_player_id=check["target_id"],
                result="werewolf" if check["is_werewolf"] else "not werewolf"
            )

        """record vote result"""
        if hasattr(self._game, 'last_voting_result'):
            voting = self._game.last_voting_result
            self._recorder.record_voting_result(
                voting_result=voting["votes"],
                voted_out_player=voting["eliminated"]
            )

        """record wolf"""
        if hasattr(self._game, 'last_wolf_action'):
            wolf_action = self._game.last_wolf_action
            for wolf_id, target_id in wolf_action["votes"].items():
                self._recorder.record_wolf_action(wolf_id, target_id)
            self._recorder.record_wolf_kill(wolf_action["killed"])

        """record witch"""
        if hasattr(self._game, 'last_witch_action'):
            witch = self._game.last_witch_action
            if witch["saved"] is not None:
                self._recorder.record_witch_save(witch["saved"])
            if witch["killed"] is not None:
                self._recorder.record_witch_kill(witch["killed"])

        """record hunter"""
        if hasattr(self._game, 'last_hunter_action'):
            hunter = self._game.last_hunter_action
            if hunter["killed"] is not None:
                self._recorder.record_hunter_kill(hunter["killed"])

    
    async def stop(self) -> None:
        """Stop the game and clean up resources"""
        async with self._lock:
            if not self.is_running:
                logger.warning("Cannot stop game: game is not running")
                return

            if self._task and not self._task.done():
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    logger.info(f"Game loop task cancelled (task_id: {id(self._task)})")

            if self._game and self._recorder:
                winner = self._game.get_winner()
                self._recorder.game_end(winner)
                self._recorder.record_game_result(self._game)
                self._game.finalize()

            self._task = None
            self._game = None
            logger.info("Game stopped successfully")



    def bind_server(self, server: AgentServer) -> None:
        """Bind the GameRunner into a AgentServer.

        If the bound already exists, then pass. If already bound with different
        agent server, then raise. Otherwise, build the binding relationship.
        """
        if server is None:
            raise ValueError("Cannot bind a None AgentServer to GameRunner")

        if self._agent_server is not None:
            raise ValueError(
            f"GameRunner is already bound to a different AgentServer (id: {id(self._agent_server)}). "
            "Cannot bind multiple AgentServers."
            )

        self._agent_server = server
        

    def bind_recorder(self, recorder: Recorder) -> None:
        """Bind the GameRunner into a Recorder.

        If the bound already exists, then pass. If already bound with different
        recorder, then raise. Otherwise, build the binding relationship.
        """

        if recorder is None:
            raise ValueError("Cannot bind a None Recorder to GameRunner")

        if self._recorder is not None:
            raise ValueError(
                f"GameRunner is already bound to a different Recorder (id: {id(self._recorder)}). "
                "Cannot bind multiple Recorders to one GameRunner."
            )
        
        self._recorder = recorder

    async def on_message(self) -> None:
        """Deal with the message from AgentServer"""
        if not self._agent_server or not self._recorder or not self._game:
            return

        message = await self._agent_server.receive_message()
        if message["type"] == "speech":
            self._recorder.record_speech(
                player_id=message["player_id"],
                content=message["content"]
            )
        elif message["type"] == "vote":
            self._recorder.record_vote(
                voter_id=message["voter_id"],
                target_id=message["target_id"]
            )

    @property
    def is_running(self) -> bool:
        """If the game is running"""
        return self._game is None or self._game.state is not GameState.NOT_STARTED

    @property
    def is_bound_with_server(self) -> bool:
        """If it is bound with an agent server"""
        return self._agent_server is None

    @property
    def is_bound_with_recorder(self) -> bool:
        """If it is bound with a recorder"""
        return self._recorder is None

    @property
    def is_end(self) -> bool:
        """If the game is already ended."""
        return self._game is not None and self._game.state is GameState.FINISHED

    @property
    def player_ready(self) -> bool:
        """If number of connected players is enough"""
        return self.player_count == self.config.player_number
