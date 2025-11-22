from enum import Enum, unique

@unique
# Role中定义了游戏中的角色，调用时可以使用Role.VILLAGER等方式引用。例如：player.role = Role.WOLF
class Role(Enum):
    VILLAGER = "Villager"
    WOLF = "Werewolf"
    PROPHET = "Prophet"
    WITCH = "Witch"
    HUNTER = "Hunter"

    def __str__(self) -> str:
        return self.value
    
    @property #转换为属性，调用时可以使用为player.role.is_wolf
    def is_wolf(self) -> bool:
        return self == Role.WOLF
    
    @property
    def is_cleric(self) -> bool:
        return self in {Role.PROPHET, Role.WITCH, Role.HUNTER}
    
    @property
    def is_hunter(self) -> bool:
        return self == Role.HUNTER
    
    @property
    def is_prophet(self) -> bool:
        return self == Role.PROPHET
    
    @property
    def is_witch(self) -> bool:
        return self == Role.WITCH
    
    @property
    def is_villager(self) -> bool:
        return self == Role.VILLAGER
    
    @property
    def is_good(self) -> bool:
        return self in {Role.VILLAGER, Role.PROPHET, Role.WITCH, Role.HUNTER}