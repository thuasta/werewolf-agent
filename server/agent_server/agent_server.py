"""Contains the Agent Server Class

AgentServer is used to deal with connections from player's code. Its role
includes:
- Deal with connections from agent. Provide functions like connecting,
reconnecting, disconnecting, etc.
- Parse the messages according to the protocol. Then send necessary message
to GameRunner.
- Afford a sending message interface to GameRunner.
- ...
"""

import asyncio
import json
import logging
import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

if TYPE_CHECKING:
    from game_controller.game_runner import GameRunner

logger = logging.getLogger("AgentServer")


class AgentServer:
    """The Agent Server"""

    def __init__(self, host_port: Tuple[str, int]) -> None:
        self._host, self._port = host_port
        self._runner: Optional["GameRunner"] = None
        self._server: Optional[asyncio.AbstractServer] = None

        self._connections: Dict[
            int, Tuple[asyncio.StreamReader, asyncio.StreamWriter]
        ] = {}

        self._pending_requests: Dict[str, asyncio.Future] = {}

    def bind_runner(self, runner: "GameRunner") -> None:
        """Bind the AgentServer into a GameRunner."""
        if self._runner is not None:
            if self._runner is runner:
                return
            raise RuntimeError(
                "AgentServer is already bound to a different GameRunner"
            )
        self._runner = runner
        logger.info("GameRunner bound successfully.")

    async def start(self) -> None:
        """Start the agent server."""
        if self._server is not None:
            raise RuntimeError("Server is already running")

        logger.info("AgentServer starting on %s:%s", self._host, self._port)
        self._server = await asyncio.start_server(
            self._handle_client, self._host, self._port
        )

        async with self._server:
            await self._server.serve_forever()

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """
        Handle individual client connection.
        Orchestrates handshake, registration, message loop, and cleanup.
        """
        addr = writer.get_extra_info("peername")
        logger.info("New connection from %s", addr)

        player_id: Optional[int] = None

        try:
            player_id = await self._perform_handshake(reader, addr)
            if player_id is None:
                return

            await self._register_connection(player_id, reader, writer)

            await self._message_loop(player_id, reader)

        except (ConnectionResetError, BrokenPipeError):
            logger.warning("Connection reset by %s", addr)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Unexpected error with %s", addr)
        finally:
            await self._cleanup_connection(player_id, writer)

    async def _perform_handshake(
        self, reader: asyncio.StreamReader, addr: Any
    ) -> Optional[int]:
        """Read the first line and extract player_id."""
        try:
            line = await asyncio.wait_for(reader.readuntil(b"\n"), timeout=5.0)
            handshake_data = json.loads(line.decode("utf-8"))

            player_id = handshake_data.get("player_id") or handshake_data.get(
                "params", {}
            ).get("player_id")

            if player_id is None:
                logger.warning(
                    "Connection from %s failed: Missing player_id", addr
                )
                return None
            return player_id

        except asyncio.TimeoutError:
            logger.warning(
                "Connection from %s timed out during handshake.", addr
            )
            return None
        except (json.JSONDecodeError, ValueError):
            logger.warning(
                "Connection from %s failed: Invalid handshake JSON", addr
            )
            return None

    async def _register_connection(
        self,
        player_id: int,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Handle player registration and old connection cleanup."""
        if player_id in self._connections:
            logger.info(
                "Player %s reconnecting, closing old connection.", player_id
            )
            _, old_writer = self._connections[player_id]
            if not old_writer.is_closing():
                old_writer.close()
                await old_writer.wait_closed()

        self._connections[player_id] = (reader, writer)
        addr = writer.get_extra_info("peername")
        logger.info("Player %s registered on %s", player_id, addr)

        if self._runner:
            self._runner.player_count = len(self._connections)

    async def _message_loop(
        self, player_id: int, reader: asyncio.StreamReader
    ) -> None:
        """The main loop reading messages from the agent."""
        while not reader.at_eof():
            try:
                data = await reader.readuntil(b"\n")
                if not data:
                    break

                message = json.loads(data.decode("utf-8"))
                await self._process_message(player_id, message)

            except asyncio.IncompleteReadError:
                break
            except json.JSONDecodeError:
                logger.error("Invalid JSON from Player %s", player_id)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Error reading from Player %s", player_id)
                break

    async def _cleanup_connection(
        self, player_id: Optional[int], writer: asyncio.StreamWriter
    ) -> None:
        """Clean up connection resources and update runner."""
        if player_id is not None and player_id in self._connections:
            _, current_writer = self._connections[player_id]
            if current_writer == writer:
                del self._connections[player_id]
                logger.info("Player %s disconnected.", player_id)

                if self._runner:
                    self._runner.player_count = len(self._connections)

        if not writer.is_closing():
            writer.close()
            await writer.wait_closed()

    async def _process_message(
        self, player_id: int, message: Dict[str, Any]
    ) -> None:
        """Process incoming JSON-RPC response."""
        if "id" in message:
            request_id = message.get("id")
            if request_id in self._pending_requests:
                future = self._pending_requests[request_id]
                if not future.done():
                    if "error" in message and message["error"]:
                        logger.error(
                            "RPC Error from Player %s: %s",
                            player_id,
                            message["error"],
                        )
                        future.set_result(None)
                    else:
                        future.set_result(message.get("result"))
            else:
                logger.debug(
                    "Received response for unknown/timed-out ID: %s",
                    request_id,
                )
        else:
            logger.debug(
                "Received unsolicited message from Player %s: %s",
                player_id,
                message,
            )

    async def call_agent_method(
        self,
        player_id: int,
        method: str,
        params: Dict[str, Any],
        timeout: int = 10,
    ) -> Any:
        """
        Public Interface for GameRunner.
        """
        if player_id not in self._connections:
            logger.error(
                "Cannot call %s: Player %s not connected.", method, player_id
            )
            return None

        _, writer = self._connections[player_id]
        request_id = str(uuid.uuid4())

        rpc_request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": request_id,
        }

        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending_requests[request_id] = future

        try:
            data = json.dumps(rpc_request) + "\n"
            writer.write(data.encode("utf-8"))
            await writer.drain()

            result = await asyncio.wait_for(future, timeout=timeout)
            return result

        except asyncio.TimeoutError:
            logger.warning(
                "Timeout calling %s on Player %s (>%ss)",
                method,
                player_id,
                timeout,
            )
            return None
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            logger.warning(
                "Error calling %s on Player %s: %s", method, player_id, e
            )
            return None
        finally:
            self._pending_requests.pop(request_id, None)

    async def broadcast(self, method: str, params: Dict[str, Any]) -> None:
        """Helper to send a notification to all players."""
        for pid in list(self._connections.keys()):
            asyncio.create_task(
                self.call_agent_method(pid, method, params, timeout=5)
            )
