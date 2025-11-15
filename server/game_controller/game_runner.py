"""Contains game runner class"""


class GameRunner:
    """The game runner class, which controls the game progress"""

    def start(self) -> None:
        """Start the game"""
        raise NotImplementedError

    def on_message(self) -> None:
        """Deal with the message from AgentServer"""
        raise NotImplementedError
