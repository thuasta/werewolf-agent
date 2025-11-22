from enum import Enum, unique

@unique
class act_type(Enum):
    #在这里完成动作类型的定义
    WITCH_Kill = "witch_kill"
    WITCH_Save = "witch_save"
    WOLF_Kill = "wolf_kill"
    PROPHET_Check = "prophet_check"
    VOTE_Kill = "vote_kill"
    HUNTER_Kill = "hunter_kill"