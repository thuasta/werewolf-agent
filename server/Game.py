'''这是Game类，用于记录游戏环境'''
import random
from player import Player  # player类


class Game:
    def __init__(self, players: list[Player], roles: list[str]):
        self.running = True
        self.day = 0

        #随机分配角色
        random.shuffle(roles)
        for player, role in zip(players, roles):
            player.role = role

        self.survivors = {p.id: p for p in players} #存活玩家
        self.dead_players = {} #死亡玩家  
        self.pending_death = None  # 待死亡玩家，1.在狼人杀人，女巫确认用药之前 2.投票之后，判断猎人开枪之前

        #不同阵营存活人数，任意一方清零游戏结束
        self.wolfs_number = sum(r == "wolf" for r in roles)
        self.clergy_number = sum(r in ["prophet", "witch", "hunter"] for r in roles)
        self.villagers_number = len(players) - self.wolfs_number - self.clergy_number

        self.votes = {}
        self.kill_votes = {}
        self.message_log = []

    def receive_message(self, msg: str):
        self.message_log.append(msg)

    def send_message(self, msg: str):
        print(f"Game broadcast: {msg}")

    def wolf_kill(self):
        # 实现狼人集体投票击杀
        # 狼人杀人是一名狼人决定还是狼人讨论投票决定？
        pass

    def witch_time(self):
        #包含女巫获悉死亡玩家
        #女巫救人逻辑
        #女巫毒人逻辑
        pass

    def prophet_check(self) -> str:
        #预言家验人逻辑
        pass

    def day_change(self):
        self.day += 1
        self.votes.clear()
        self.kill_votes.clear()

    def vote(self):
        pass

    def vote_kill(self):
        pass

    def hunter_kill(self):
        pass

    def end_game(self):
        # 胜负判断逻辑
        pass
