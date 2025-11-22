from player import Player
from role import Role
from act_type import ActType

class Act:
    def __init__(self, act_player: Player, act_type: ActType):
        self.act_player = act_player
        self.act_type = act_type
    
    # Here, coresponds happen. AI should decide which player to act.
    # Later code here.

    def get_poison_target():
        return None
    
    def get_shoot_target():
        return None
    
    def get_wolf_killed_target():
        return None
    
    def get_prophet_check_target():
        return None
    
    def get_vote_kill_target():
        return None
    
    def is_saved_by_witch():
        return False
    
    def acted_player():
        return acted_player #not defined yet

    def act_result(self):
        if act_type == WITCH_SAVE:
            return is_saved_by_witch()
        else:
            return acted_player()
        