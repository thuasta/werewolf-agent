from role import Role
from typing import Any

# Player类表示游戏中的玩家，包含玩家的ID、角色和存活状态等属性。
class Player:
    # 这样写之后，Game中传入的roles : list[Role] 中的元素需要是Role类型的对象，例如[Role.VILLAGER, Role.WOLF]
    def __init__(self, player_id:int, role : Role) :
        self.id : int = player_id
        self.role : Role = role
        self.is_alive : bool = True

        self.witch_antidote : bool = True # 女巫解药，True表示可用
        self.witch_poison : bool = True   # 女巫毒药，True表示可用

        self.can_shoot : bool = True # 表示猎人是否能开枪，True表示可以开枪

        self.prophet_check_history: list[dict[str, Any]] = [] # 预言家查看历史记录，包含查看的玩家ID和角色

        self.survived_nights : int = 0 # 玩家存活的夜晚数
        self.vote_correct_counts : int = 0 # 玩家投票正确的次数
        self.mistake_counts : int = 0 # 玩家失误的次数，如毒杀好人等

    def die(self, method: str) -> None :
        # 将玩家的状态设置为死亡，同时标记死亡后果（如猎人不能开枪）
        self.is_alive = False
        # 如果猎人被毒杀，设置为不能开枪
        if self.role.is_hunter and method == "poison":    
            self.can_shoot = False

    # 显示玩家信息
    def __repr__(self) -> str:
        return f"Player(id={self.id}, role={self.role.value}, Alive={self.is_alive})"