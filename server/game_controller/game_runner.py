"""Contains game runner class"""


class GameRunner:

    def start(self) -> None:
        raise NotImplementedError

    def on_message(self) -> None:
        raise NotImplementedError
