"""Werewolf Agent SDK - 狼人杀智能体开发工具包。

支持与游戏服务器通过 WebSocket 通讯，实现各阶段的决策逻辑。
"""

from .agent import Agent
from .websocket_client import WebsocketClient
from . import messages

__all__ = ["Agent", "WebsocketClient", "messages"]
