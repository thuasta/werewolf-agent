
# 狼人杀智能体 SDK 使用指南

## 概览

开发环境：python 3.12.12+websockets 15.0.1
本 SDK 提供了一个完整的智能体框架，用于与狼人杀游戏服务器通过 WebSocket 通讯，实现以下功能：

- **初始化** (`initialize`)：接收玩家身份和游戏配置
- **夜晚行动**：
  - `werewolf_action`：狼人选择目标进行击杀
  - `seer_action`：预言家选择目标进行查验
  - `witch_action`：女巫使用解药或毒药
  - `hunter_action`：猎人反击（被杀或投票出局时）
- **白天阶段**：
  - `discuss`：白天讨论发言
  - `vote`：投票出局目标
  - `defend`：在被指控时进行辩护
- **游戏结束** (`game_over`)：接收游戏结果和反思

## 快速开始

### 1. 基本设置

```python
import asyncio
from sdk.agent import Agent

async def main():
    # 创建智能体
    agent = Agent(name="MyAgent")
  
    # 连接到服务器
    await agent.start("ws://localhost:8000/ws")
  
    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. 使用命令行工具

```bash
# 启动智能体，连接到本地服务器
python -m sdk.runner --name "MyAgent" --server "ws://127.0.0.1:8000/ws"

# 也可以不指定参数（使用默认值）
python -m sdk.runner
```

### 3. 自定义行为

继承 `Agent` 类并重写行为方法：

```python
from sdk.agent import Agent
from sdk.messages import WerewolfActionMessage, WerewolfActionResponseMessage

class SmartAgent(Agent):
    def on_werewolf_action(self, msg: WerewolfActionMessage) -> WerewolfActionResponseMessage:
        # 获取信息
        alive_players = msg.msg.get("alive_players", [])
        teammates = msg.msg.get("teammates", [])
    
        # 实现自定义策略
        target_id = self.select_best_target(alive_players, teammates)
    
        return WerewolfActionResponseMessage(
            token=msg.msg["token"],
            action="kill",
            target_id=target_id,
            reasoning="我的分析表明这个玩家最有可能是好人...",
            confidence=0.8
        )
  
    def select_best_target(self, alive_players, teammates):
        # 自定义选择逻辑
        teammate_ids = {p.get("player_id") for p in teammates}
        for p in alive_players:
            if p.get("player_id") not in teammate_ids:
                return p.get("player_id", 0)
        return 0
```

## 消息格式

所有消息都是 JSON 格式，包含 `type` 和 `token` 字段。

### 请求示例（服务器 → 智能体）

```json
{
  "type": "initialize",
  "token": "abc123",
  "player_id": 1,
  "role": "werewolf",
  "role_description": "你是狼人，每晚可以杀死一名玩家",
  "all_players": [
    {"player_id": 1, "name": "玩家1"},
    {"player_id": 2, "name": "玩家2"}
  ],
  "game_config": {
    "roles": ["werewolf", "seer", "witch", "villager"],
    "wolf_count": 2,
    "max_days": 10,
    "language": "zh-CN"
  }
}
```

### 响应示例（智能体 → 服务器）

```json
{
  "type": "initialize_response",
  "token": "abc123",
  "status": "success",
  "message": "初始化完成"
}
```

## 行为方法文档

### 初始化

**方法**: `on_initialize(msg: InitializeMessage) -> InitializeResponseMessage`

记录玩家 ID、角色和游戏配置。

### 狼人行动

**方法**: `on_werewolf_action(msg: WerewolfActionMessage) -> WerewolfActionResponseMessage`

选择要杀害的目标。

**消息字段**:

- `game_state`: 当前游戏状态
- `night_numbers`: 当前是第几晚
- `alive_players`: 所有存活的玩家列表
- `teammates`: 狼队友（只显示还活着的队友）
- `previous_votes`: 历史投票记录

### 预言家行动

**方法**: `on_seer_action(msg: SeerActionMessage) -> SeerActionResponseMessage`

选择要查验的目标。

### 女巫行动

**方法**: `on_witch_action(msg: WitchActionMessage) -> WitchActionResponseMessage`

决定是否使用解药或毒药，以及对谁使用。

### 猎人行动

**方法**: `on_hunter_action(msg: HunterActionMessage) -> HunterActionResponseMessage`

在被杀死或投票出局时选择射击目标。

### 讨论

**方法**: `on_discuss(msg: DiscussMessage) -> DiscussResponseMessage`

在白天讨论阶段发言表达观点。

### 投票

**方法**: `on_vote(msg: VoteMessage) -> VoteResponseMessage`

投票选择要出局的玩家。

### 辩护

**方法**: `on_defend(msg: DefendMessage) -> DefendResponseMessage`

在被指控时进行辩解。

### 游戏结束

**方法**: `on_game_over(msg: GameOverMessage) -> GameOverResponseMessage`

处理游戏结束，返回反思总结和自评分数。

## 文件结构

```
sdk/
├── __init__.py           # SDK 入口
├── agent.py              # 智能体主类
├── messages.py           # 消息类型定义
├── websocket_client.py   # WebSocket 客户端
├── interface.py          # 接口定义
├── runner.py             # 命令行启动脚本
└── README.md             # SDK 文档
```

## 日志

SDK 使用 Python 标准的 `logging` 模块。可以通过以下方式配置日志级别：

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("sdk.agent")
```

## 错误处理

所有行为方法的异常会被捕获，智能体会发送错误响应给服务器，包含错误码和建议行动。

## 扩展

可以通过继承 `Agent` 类来实现更复杂的策略：

1. 维护游戏状态和历史信息
2. 实现复杂的分析和决策逻辑
3. 添加自定义日志和统计

示例：

```python
class AdvancedAgent(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.history = []
        self.suspicions = {}
  
    def on_discuss(self, msg: DiscussMessage) -> DiscussResponse:
        # 分析历史信息
        self.update_suspicions(msg.msg.get("previous_speeches", []))
    
        # 生成发言
        speech = self.generate_speech()
        return DiscussResponseMessage(
            token=msg.msg["token"],
            speech=speech,
            emotion="confident",
            target_players=list(self.suspicions.keys()),
            is_accusation=True
        )
  
    def update_suspicions(self, speeches):
        for speech in speeches:
            # 分析发言逻辑
            pass
  
    def generate_speech(self):
        # 根据分析生成发言
        return "根据前面的讨论，我认为..."
```

## 常见问题

### 消息没有被发送

确保 Agent 已经连接到服务器，检查网络连接和服务器地址。

### 收不到服务器消息

检查事件循环是否正常运行，以及 `on_message` 回调是否正确设置。

### 超时错误

确保行为方法在规定时间内返回（通常 5-10 秒），避免进行耗时的操作
