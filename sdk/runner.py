"""简单的 agent 启动脚本示例。

用法:
    python -m sdk.runner --name <agent_name> --server <server_url>
"""

import asyncio
import argparse
import logging
from .agent import Agent

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="Werewolf Agent Runner")
    parser.add_argument("--name", type=str, default="DefaultAgent", help="Agent name")
    parser.add_argument(
        "--server",
        type=str,
        default="ws://127.0.0.1:8000/ws",
        help="Server WebSocket URL",
    )
    args = parser.parse_args()

    # 创建智能体
    agent = Agent(name=args.name)
    logger.info(f"Starting agent: {args.name}")

    try:
        # 连接到服务器
        await agent.start(args.server)
        logger.info(f"Agent {args.name} connected to {args.server}")

        # 保持运行直到中断
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await agent.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
