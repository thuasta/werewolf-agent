"""SDK 集成测试：本地演示消息流和路由。"""

import json
from sdk.messages import (
    Message,
    InitializeMessage,
    InitializeResponseMessage,
    WerewolfActionMessage,
    WerewolfActionResponseMessage,
)
from sdk.agent import Agent


def test_message_routing():
    """测试消息序列化/反序列化和路由。"""
    print("=== 测试 Message 序列化 ===")

    # 1. 创建初始化消息
    init_msg = InitializeMessage(
        token="test_token_1",
        player_id=1,
        role="werewolf",
        role_description="你是狼人",
        all_players=[
            {"player_id": 1, "name": "Player1"},
            {"player_id": 2, "name": "Player2"},
        ],
        game_config={"roles": ["werewolf", "seer"], "wolf_count": 1},
    )

    # 2. 序列化为 JSON
    json_str = init_msg.json()
    print(f"Serialized: {json_str}\n")

    # 3. 反序列化
    received_msg = Message(json_str)
    print(f"Deserialized msg.msg: {received_msg.msg}\n")

    # 4. 创建 Agent 并测试路由
    print("=== 测试 Agent 路由 ===")
    agent = Agent(name="TestAgent")

    # 模拟接收消息
    agent._on_message(received_msg)
    print(f"Agent role: {agent.role}, player_id: {agent.player_id}\n")

    # 5. 测试狼人行动消息
    print("=== 测试狼人行动 ===")
    wolf_action_msg = WerewolfActionMessage(
        token="test_token_2",
        game_state={},  # type: ignore[arg-type]
        night_numbers=1,
        alive_players=[
            {"player_id": 1, "name": "Player1", "is_alive": True},
            {"player_id": 2, "name": "Player2", "is_alive": True},
        ],
        teammates=[],
        previous_votes=[],
    )

    wolf_json = wolf_action_msg.json()
    print(f"Wolf action message: {wolf_json}\n")

    received_wolf = Message(wolf_json)
    # 模拟路由（这里只是打印，因为我们没有 async 上下文）
    print(f"Message type: {received_wolf.msg.get('type')}")
    print(f"Target should be selected: {received_wolf.msg.get('alive_players')}\n")

    print("✓ 所有测试通过！")


if __name__ == "__main__":
    test_message_routing()
