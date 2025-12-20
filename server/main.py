"""Entry Point for Server"""

import argparse
import asyncio
import logging
import os

from agent_server.agent_server import AgentServer
from game_controller.game_runner import GameRunner
from game_logic.game_config import (
    NORMAL_CONFIG_6_PLAYER,
    NORMAL_CONFIG_9_PLAYER,
    GameConfig,
)
from recorder.recorder import Recorder


class Options:
    def __init__(
        self, logging_level: int, host: str, port: int, config_id: str
    ):
        self.logging_level = logging_level
        self.host = host
        self.port = port
        self.config_id = config_id


DEFAULT_LOGGING_LEVEL = logging.INFO
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 1999
DEFAULT_CONFIG_ID = "6"
DEFAULT_LOOP_INTERVAL = 0.5
LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"


def parse_options() -> Options:
    host_env = os.getenv("WEREWOLF_HOST", default=DEFAULT_HOST)
    port_env = os.getenv("WEREWOLF_PORT", default=str(DEFAULT_PORT))

    parser = argparse.ArgumentParser("werewolf_server")
    parser.add_argument(
        "--logging-level",
        type=int,
        help="Logging level",
        default=DEFAULT_LOGGING_LEVEL,
        choices=[
            logging.CRITICAL,
            logging.ERROR,
            logging.WARNING,
            logging.INFO,
            logging.DEBUG,
        ],
    )
    parser.add_argument(
        "--host", type=str, help="Server host", default=host_env
    )
    parser.add_argument(
        "--port", type=int, help="Server port", default=int(port_env)
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Game config (6 or 9)",
        default=DEFAULT_CONFIG_ID,
        choices=["6", "9"],
    )

    args = parser.parse_args()
    return Options(
        logging_level=args.logging_level,
        host=args.host,
        port=args.port,
        config_id=args.config,
    )


async def main():
    # Configuration is read from command line arguments and environment
    # variables, which includes host, port, game rules, number of players,
    # and trusted tokens

    options = parse_options()

    logging.basicConfig(level=options.logging_level, format=LOGGING_FORMAT)
    game_config: GameConfig
    if options.config_id == "9":
        game_config = NORMAL_CONFIG_9_PLAYER
    else:
        game_config = NORMAL_CONFIG_6_PLAYER

    game_runner = GameRunner(game_config)
    agent_server = AgentServer((options.host, options.port))
    recorder = Recorder()

    game_runner.bind_server(agent_server)
    game_runner.bind_recorder(recorder)
    agent_server.bind_runner(game_runner)

    logging.info(
        "Werewolf Server is starting on %s:%d with %d players expected",
        options.host,
        options.port,
        game_config.player_number,
    )
    # recorder.bind_runner(game_runner)
    # ^ TODO: finish the method definition

    # Stage I: wait for connection
    await agent_server.start()
    is_previous_waiting = False
    is_game_running = False
    while True:
        await asyncio.sleep(DEFAULT_LOOP_INTERVAL)
        if not game_runner.player_ready:
            if not is_previous_waiting:
                logging.info(
                    "Server is waiting for players (%d/%d)",
                    game_runner.player_count,
                    game_config.player_number,
                )
                is_previous_waiting = True
            else:
                # Optional: debug log for heartbeat
                logging.debug(
                    "Still waiting... (%d/%d)",
                    game_runner.player_count,
                    game_config.player_number,
                )
            continue
        # Stage II: run the game
        if not is_game_running:
            if is_previous_waiting:
                logging.info("All players connected. Initializing game...")
                is_previous_waiting = False

            # This triggers the role assignment and sends the
            # initializing message to agents
            await game_runner.start()

            logging.info(
                "Game started! Roles assigned and broadcast sent. Day %d.",
                game_runner.day,
            )
            is_game_running = True
            continue
        if game_runner.is_end:
            logging.info("Game finished. Server stopping.")
            break

    # Game finished, close the server, and save the recording.


if __name__ == "__main__":
    print("Hello World!")
