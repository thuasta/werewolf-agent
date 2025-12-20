"""Contains game runner class"""


class GameRunner:
    """The game runner class, which controls the game progress"""

    async def start(self) -> None:
        """Start the game"""
        raise NotImplementedError

    async def on_message(self) -> None:
        """Deal with the message from AgentServer"""
        raise NotImplementedError
