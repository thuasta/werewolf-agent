import asyncio
import logging
from typing import Optional

from .websocket_client import WebsocketClient
from .messages import (
    Message,
    InitializeMessage,
    InitializeResponseMessage,
    WerewolfActionMessage,
    WerewolfActionResponseMessage,
    SeerActionMessage,
    SeerActionResponseMessage,
    WitchActionMessage,
    WitchActionResponseMessage,
    HunterActionMessage,
    HunterActionResponseMessage,
    DiscussMessage,
    DiscussResponseMessage,
    VoteMessage,
    VoteResponseMessage,
    DefendMessage,
    DefendResponseMessage,
    GameOverMessage,
    GameOverResponseMessage,
)

logger = logging.getLogger(__name__)


class Agent:
    """狼人杀智能体，通过 WebSocket 与后端通讯，处理各阶段的决策请求。"""

    def __init__(self, name: str):
        self.name = name
        self.role: Optional[str] = None
        self.player_id: Optional[int] = None
        self.is_alive = True
        self.client = WebsocketClient()

    async def start(self, server_url: str):
        """连接到游戏服务器并开始接收消息。"""
        await self.client.connect(server_url)
        self.client.on_message = self._on_message
        logger.info(f"Agent {self.name} connected to {server_url}")

    async def stop(self):
        """断开连接。"""
        await self.client.disconnect()
        logger.info(f"Agent {self.name} disconnected")

    # ---- 协议行为方法（接收 Message，返回 ResponseMessage） ----

    def on_initialize(self, msg: InitializeMessage) -> InitializeResponseMessage:
        """初始化：记录玩家身份和游戏配置。"""
        self.player_id = msg.msg["player_id"]
        self.role = msg.msg["role"]
        logger.info(
            f"Agent {self.name} initialized as {self.role} (ID: {self.player_id})"
        )
        return InitializeResponseMessage(
            token=msg.msg["token"], status="success", message="初始化完成"
        )

    def on_werewolf_action(
        self, msg: WerewolfActionMessage
    ) -> WerewolfActionResponseMessage:
        """狼人行动：选择要杀害的目标。"""
        alive_players = msg.msg.get("alive_players", [])
        teammates = msg.msg.get("teammates", [])
        teammate_ids = {p.get("player_id") for p in teammates if isinstance(p, dict)}

        target_id = 0
        for p in alive_players:
            if isinstance(p, dict) and p.get("player_id") not in teammate_ids:
                target_id = p.get("player_id", 0)
                break

        if target_id == 0 and alive_players:
            target_id = (
                alive_players[0].get("player_id", 0)
                if isinstance(alive_players[0], dict)
                else 0
            )

        logger.info(f"Werewolf {self.name} action: kill target {target_id}")
        return WerewolfActionResponseMessage(
            token=msg.msg["token"],
            action="kill",
            target_id=target_id,
            reasoning="默认狼人策略",
            confidence=0.5,
        )

    def on_seer_action(self, msg: SeerActionMessage) -> SeerActionResponseMessage:
        """预言家行动：选择要查验的目标。"""
        alive_players = msg.msg.get("alive_players", [])
        target_id = 0
        if alive_players and isinstance(alive_players[0], dict):
            target_id = alive_players[0].get("player_id", 0)

        logger.info(f"Seer {self.name} action: check target {target_id}")
        return SeerActionResponseMessage(
            token=msg.msg["token"],
            action="check",
            target_id=target_id,
            reasoning="默认预言家策略",
        )

    def on_witch_action(self, msg: WitchActionMessage) -> WitchActionResponseMessage:
        """女巫行动：使用解药或毒药。"""
        poison_available = msg.msg.get("poison_available", False)
        antidote_available = msg.msg.get("antidote_available", False)
        killed_player_id = msg.msg.get("killed_player_id", 0)
        alive_players = msg.msg.get("alive_players", [])

        action = "abstain"
        target_id = 0

        if killed_player_id and antidote_available:
            action = "save"
            target_id = killed_player_id
        elif poison_available and alive_players and isinstance(alive_players[0], dict):
            action = "poison"
            target_id = alive_players[0].get("player_id", 0)

        logger.info(f"Witch {self.name} action: {action} on target {target_id}")
        return WitchActionResponseMessage(
            token=msg.msg["token"],
            action=action,
            target_id=target_id,
            reasoning="默认女巫策略",
        )

    def on_hunter_action(self, msg: HunterActionMessage) -> HunterActionResponseMessage:
        """猎人行动：被击杀或投票出局时的反击。"""
        alive_players = msg.msg.get("alive_players", [])
        target_id = 0
        if alive_players and isinstance(alive_players[0], dict):
            target_id = alive_players[0].get("player_id", 0)

        logger.info(f"Hunter {self.name} action: shoot target {target_id}")
        return HunterActionResponseMessage(
            token=msg.msg["token"],
            action="shoot",
            target_id=target_id,
            reasoning="默认猎人策略",
        )

    def on_discuss(self, msg: DiscussMessage) -> DiscussResponseMessage:
        """白天讨论：发言陈述观点。"""
        speech = "我是好人，大家相信我。"
        logger.info(f"Agent {self.name} discuss: {speech}")
        return DiscussResponseMessage(
            token=msg.msg["token"],
            speech=speech,
            emotion="neutral",
            target_players=0,
            is_accusation=False,
        )

    def on_vote(self, msg: VoteMessage) -> VoteResponseMessage:
        """白天投票：选择要投票出局的玩家。"""
        alive_players = msg.msg.get("alive_players", [])
        target_id = 0
        if alive_players and isinstance(alive_players[0], dict):
            target_id = alive_players[0].get("player_id", 0)

        logger.info(f"Agent {self.name} vote: target {target_id}")
        return VoteResponseMessage(
            token=msg.msg["token"],
            vote_target=target_id,
            reasoning="默认投票策略",
            confidence=0.5,
        )

    def on_defend(self, msg: DefendMessage) -> DefendResponseMessage:
        """辩护：在被指控时进行辩解。"""
        defense = "我昨晚没有可疑行为，请相信我。"
        logger.info(f"Agent {self.name} defend: {defense}")
        return DefendResponseMessage(
            token=msg.msg["token"],
            defense=defense,
            counter_arguments=[],
            emotional_tone="calm",
        )

    def on_game_over(self, msg: GameOverMessage) -> GameOverResponseMessage:
        """游戏结束：返回反思和评分。"""
        winner = msg.msg.get("winner")
        logger.info(f"Agent {self.name} game over, winner: {winner}")
        return GameOverResponseMessage(
            token=msg.msg["token"],
            status="acknowledged",
            reflection="下次继续优化决策策略",
            rating=4.0,
        )

    # ---- 消息路由 ----

    def _on_message(self, msg: Message):
        """接收服务器消息并路由到对应的行为方法。"""
        try:
            msg_type = msg.msg.get("type")
            logger.debug(f"Received message type: {msg_type}")

            response = None

            if msg_type == "initialize":
                init_msg = InitializeMessage(
                    token=msg.msg.get("token", ""),
                    player_id=msg.msg.get("player_id", 0),
                    role=msg.msg.get("role", ""),
                    role_description=msg.msg.get("role_description", ""),
                    all_players=msg.msg.get("all_players", []),
                    game_config=msg.msg.get("game_config", {}),
                )
                response = self.on_initialize(init_msg)

            elif msg_type == "werewolf_action":
                wolf_msg = WerewolfActionMessage(
                    token=msg.msg.get("token", ""),
                    game_state=msg.msg.get("game_state", {}),
                    night_numbers=msg.msg.get("night_numbers", 0),
                    alive_players=msg.msg.get("alive_players", []),
                    teammates=msg.msg.get("teammates", []),
                    previous_votes=msg.msg.get("previous_votes", []),
                )
                response = self.on_werewolf_action(wolf_msg)

            elif msg_type == "seer_action":
                seer_msg = SeerActionMessage(
                    token=msg.msg.get("token", ""),
                    game_state=msg.msg.get("game_state", {}),
                    night_numbers=msg.msg.get("night_numbers", 0),
                    alive_players=msg.msg.get("alive_players", []),
                    previous_checks=msg.msg.get("previous_checks", []),
                )
                response = self.on_seer_action(seer_msg)

            elif msg_type == "witch_action":
                witch_msg = WitchActionMessage(
                    token=msg.msg.get("token", ""),
                    game_state=msg.msg.get("game_state", {}),
                    night_numbers=msg.msg.get("night_numbers", 0),
                    alive_players=msg.msg.get("alive_players", []),
                    poison_available=msg.msg.get("poison_available", False),
                    antidote_available=msg.msg.get("antidote_available", False),
                    killed_player_id=msg.msg.get("killed_player_id", 0),
                    previous_actions=msg.msg.get("previous_actions", []),
                )
                response = self.on_witch_action(witch_msg)

            elif msg_type == "hunter_action":
                hunter_msg = HunterActionMessage(
                    token=msg.msg.get("token", ""),
                    game_state=msg.msg.get("game_state", {}),
                    cause=msg.msg.get("cause", ""),
                    killed_by=msg.msg.get("killed_by", 0),
                    alive_players=msg.msg.get("alive_players", []),
                )
                response = self.on_hunter_action(hunter_msg)

            elif msg_type == "discuss":
                discuss_msg = DiscussMessage(
                    token=msg.msg.get("token", ""),
                    game_state=msg.msg.get("game_state", {}),
                    day_number=msg.msg.get("day_number", 0),
                    speech_order=msg.msg.get("speech_order", 0),
                    previous_speeches=msg.msg.get("previous_speeches", []),
                    last_night_events=msg.msg.get("last_night_events", []),
                    remaining_time=msg.msg.get("remaining_time", 0),
                )
                response = self.on_discuss(discuss_msg)

            elif msg_type == "vote":
                vote_msg = VoteMessage(
                    token=msg.msg.get("token", ""),
                    game_state=msg.msg.get("game_state", {}),
                    day_number=msg.msg.get("day_number", 0),
                    alive_players=msg.msg.get("alive_players", []),
                    discussion_summary=msg.msg.get("discussion_summary", ""),
                    previous_votes=msg.msg.get("previous_votes", []),
                    vote_type=msg.msg.get("vote_type", "elimination"),
                )
                response = self.on_vote(vote_msg)

            elif msg_type == "defend":
                defend_msg = DefendMessage(
                    token=msg.msg.get("token", ""),
                    game_state=msg.msg.get("game_state", {}),
                    accusations=msg.msg.get("accusations", []),
                    time_limit=msg.msg.get("time_limit", 0),
                )
                response = self.on_defend(defend_msg)

            elif msg_type == "game_over":
                game_over_msg = GameOverMessage(
                    token=msg.msg.get("token", ""),
                    winner=msg.msg.get("winner", ""),
                    winning_players=msg.msg.get("winning_players", []),
                    final_state=msg.msg.get("final_state", {}),
                    role_reveal=msg.msg.get("role_reveal", []),
                    performance_stats=msg.msg.get("performance_stats", {}),
                )
                response = self.on_game_over(game_over_msg)

            else:
                logger.warning(f"Unknown message type: {msg_type}")
                return

            # 发送响应
            if response:
                try:
                    asyncio.create_task(self.client.send(response))
                except RuntimeError:
                    # 如果没有运行的事件循环，记录警告（测试场景）
                    logger.debug("No running event loop, response not sent")

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
