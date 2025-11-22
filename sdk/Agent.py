import json
import random
from typing import Dict, List, Any, Optional

class Agent:
    def __init__(self, player_id: int, role: str, api_client=None):
        """
        初始化Agent
        
        Args:
            player_id: 玩家编号 (1~9)
            role: 角色 ('villager', 'werewolf', 'witch', 'seer', 'hunter')
            api_client: AI大语言模型接口客户端
        """
        self.player_id = player_id
        self.role = role
        self.api_client = api_client
        self.is_alive = True
        self.vote_target = None
        self.skill_used = False
        self.knowledge_base = {
            "game_phase": None,  # 'day' or 'night'
            "current_round": 0,
            "history_speeches": [],
            "vote_history": [],
            "death_info": []
        }
    
    def interact_with_ai(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        向AI大语言模型接口进行交互
        
        Args:
            prompt: 给AI的提示词
            context: 游戏上下文信息
            
        Returns:
            AI的回复
        """
        if self.api_client is None:
            # 模拟AI回复（实际使用时替换为真实API调用）
            return self._simulate_ai_response(prompt, context)
        
        try:
            # 实际调用AI接口的代码
            full_prompt = self._construct_full_prompt(prompt, context)
            response = self.api_client.generate(full_prompt)
            return response
        except Exception as e:
            print(f"AI接口调用失败: {e}")
            return self._simulate_ai_response(prompt, context)
    
    def get_history_speeches(self, backend_interface) -> List[Dict]:
        """
        从后端获取历史发言
        
        Args:
            backend_interface: 后端接口对象
            
        Returns:
            历史发言列表
        """
        try:
            history = backend_interface.get_speech_history(self.player_id)
            self.knowledge_base["history_speeches"] = history
            return history
        except Exception as e:
            print(f"获取历史发言失败: {e}")
            return []
    
    def get_current_state(self, backend_interface) -> Dict[str, Any]:
        """
        从后端获取此时的状态
        
        Args:
            backend_interface: 后端接口对象
            
        Returns:
            当前游戏状态
        """
        try:
            state = backend_interface.get_game_state(self.player_id)
            self.knowledge_base.update({
                "game_phase": state.get("phase"),
                "current_round": state.get("round", 0),
                "alive_players": state.get("alive_players", []),
                "death_info": state.get("death_info", [])
            })
            return state
        except Exception as e:
            print(f"获取游戏状态失败: {e}")
            return {}
    
    def speak(self, backend_interface, speech_type: str = "normal") -> str:
        """
        发言
        
        Args:
            backend_interface: 后端接口对象
            speech_type: 发言类型 ('normal', 'defense', 'accusation', 'analysis')
            
        Returns:
            发言内容
        """
        if not self.is_alive:
            return ""
            
        # 获取最新状态和历史
        self.get_current_state(backend_interface)
        history = self.get_history_speeches(backend_interface)
        
        # 构建发言上下文
        context = {
            "player_id": self.player_id,
            "role": self.role,
            "game_phase": self.knowledge_base["game_phase"],
            "speech_type": speech_type,
            "history": history[-10:],  # 最近10条发言
            "alive_players": self.knowledge_base.get("alive_players", [])
        }
        
        prompt = self._construct_speech_prompt(context)
        speech_content = self.interact_with_ai(prompt, context)
        
        # 提交发言到后端
        try:
            backend_interface.submit_speech(self.player_id, speech_content)
            return speech_content
        except Exception as e:
            print(f"提交发言失败: {e}")
            return speech_content
    
    def vote(self, backend_interface, target_id: Optional[int] = None) -> int:
        """
        投票
        
        Args:
            backend_interface: 后端接口对象
            target_id: 指定投票目标，如果为None则由AI决定
            
        Returns:
            投票目标ID
        """
        if not self.is_alive:
            return -1
            
        if target_id is not None:
            vote_target = target_id
        else:
            # 由AI决定投票目标
            context = {
                "player_id": self.player_id,
                "role": self.role,
                "game_phase": self.knowledge_base["game_phase"],
                "alive_players": self.knowledge_base.get("alive_players", []),
                "history": self.knowledge_base["history_speeches"][-5:]
            }
            
            prompt = self._construct_vote_prompt(context)
            ai_response = self.interact_with_ai(prompt, context)
            vote_target = self._parse_vote_decision(ai_response)
        
        self.vote_target = vote_target
        
        # 提交投票到后端
        try:
            backend_interface.submit_vote(self.player_id, vote_target)
            return vote_target
        except Exception as e:
            print(f"提交投票失败: {e}")
            return vote_target
    
    def use_skill(self, backend_interface, skill_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        使用技能
        
        Args:
            backend_interface: 后端接口对象
            skill_params: 技能参数
            
        Returns:
            技能使用结果
        """
        if not self.is_alive or self.skill_used:
            return {"success": False, "message": "无法使用技能"}
            
        skill_result = {"success": False, "message": ""}
        
        if self.role == "werewolf":
            # 狼人技能：杀人
            skill_result = self._use_werewolf_skill(backend_interface, skill_params)
        elif self.role == "witch":
            # 女巫技能：救人或毒人
            skill_result = self._use_witch_skill(backend_interface, skill_params)
        elif self.role == "seer":
            # 预言家技能：验人
            skill_result = self._use_seer_skill(backend_interface, skill_params)
        elif self.role == "hunter":
            # 猎人技能：开枪
            skill_result = self._use_hunter_skill(backend_interface, skill_params)
        
        if skill_result["success"]:
            self.skill_used = True
            
        return skill_result
    
    def act(self, backend_interface, action_type: str, **kwargs) -> Dict[str, Any]:
        """
        行动（行动后向后端更新信息）
        
        Args:
            backend_interface: 后端接口对象
            action_type: 行动类型 ('speak', 'vote', 'use_skill')
            **kwargs: 其他参数
            
        Returns:
            行动结果
        """
        result = {"action_type": action_type, "success": False}
        
        try:
            if action_type == "speak":
                speech_type = kwargs.get("speech_type", "normal")
                content = self.speak(backend_interface, speech_type)
                result.update({"success": True, "content": content})
                
            elif action_type == "vote":
                target_id = kwargs.get("target_id")
                vote_target = self.vote(backend_interface, target_id)
                result.update({"success": True, "vote_target": vote_target})
                
            elif action_type == "use_skill":
                skill_params = kwargs.get("skill_params", {})
                skill_result = self.use_skill(backend_interface, skill_params)
                result.update(skill_result)
                
            # 更新后端信息
            backend_interface.update_agent_action(self.player_id, result)
            
        except Exception as e:
            result["message"] = f"行动失败: {e}"
            
        return result
    
    def _use_werewolf_skill(self, backend_interface, skill_params: Dict[str, Any]) -> Dict[str, Any]:
        """狼人技能：杀人"""
        target_id = skill_params.get("target_id")
        if target_id is None:
            # AI决定杀人目标
            context = self._get_skill_context()
            prompt = "作为狼人，请选择今晚要杀死的玩家，只返回玩家ID数字："
            ai_response = self.interact_with_ai(prompt, context)
            target_id = self._parse_number_from_response(ai_response)
        
        try:
            backend_interface.werewolf_kill(self.player_id, target_id)
            return {"success": True, "message": f"狼人选择杀死玩家{target_id}", "target_id": target_id}
        except Exception as e:
            return {"success": False, "message": f"狼人杀人失败: {e}"}
    
    def _use_witch_skill(self, backend_interface, skill_params: Dict[str, Any]) -> Dict[str, Any]:
        """女巫技能：救人或毒人"""
        action = skill_params.get("action")  # 'save' or 'poison'
        target_id = skill_params.get("target_id")
        
        context = self._get_skill_context()
        
        if action is None:
            prompt = "作为女巫，请决定是否使用解药或毒药，返回'save X'或'poison X'或'abstain'："
            ai_response = self.interact_with_ai(prompt, context)
            action, target_id = self._parse_witch_decision(ai_response)
        
        try:
            if action == "save":
                backend_interface.witch_save(self.player_id, target_id)
                return {"success": True, "message": f"女巫使用解药拯救玩家{target_id}"}
            elif action == "poison":
                backend_interface.witch_poison(self.player_id, target_id)
                return {"success": True, "message": f"女巫使用毒药毒死玩家{target_id}"}
            else:
                return {"success": True, "message": "女巫选择不使用技能"}
        except Exception as e:
            return {"success": False, "message": f"女巫技能使用失败: {e}"}
    
    def _use_seer_skill(self, backend_interface, skill_params: Dict[str, Any]) -> Dict[str, Any]:
        """预言家技能：验人"""
        target_id = skill_params.get("target_id")
        if target_id is None:
            context = self._get_skill_context()
            prompt = "作为预言家，请选择要查验的玩家，只返回玩家ID数字："
            ai_response = self.interact_with_ai(prompt, context)
            target_id = self._parse_number_from_response(ai_response)
        
        try:
            result = backend_interface.seer_check(self.player_id, target_id)
            return {"success": True, "message": f"预言家查验玩家{target_id}，身份是{result}", "check_result": result}
        except Exception as e:
            return {"success": False, "message": f"预言家查验失败: {e}"}
    
    def _use_hunter_skill(self, backend_interface, skill_params: Dict[str, Any]) -> Dict[str, Any]:
        """猎人技能：开枪"""
        target_id = skill_params.get("target_id")
        if target_id is None:
            context = self._get_skill_context()
            prompt = "作为猎人，请选择要开枪带走的玩家，只返回玩家ID数字（如果不开枪返回0）："
            ai_response = self.interact_with_ai(prompt, context)
            target_id = self._parse_number_from_response(ai_response)
        
        if target_id == 0:
            return {"success": True, "message": "猎人选择不开枪"}
        
        try:
            backend_interface.hunter_shoot(self.player_id, target_id)
            return {"success": True, "message": f"猎人开枪带走了玩家{target_id}", "target_id": target_id}
        except Exception as e:
            return {"success": False, "message": f"猎人开枪失败: {e}"}
    
    def _construct_speech_prompt(self, context: Dict) -> str:
        """构建发言的提示词"""
        role_descriptions = {
            "villager": "你是村民，要通过发言找出狼人",
            "werewolf": "你是狼人，要伪装成好人，保护狼同伴",
            "witch": "你是女巫，要通过发言引导好人阵营",
            "seer": "你是预言家，要谨慎地透露查验信息",
            "hunter": "你是猎人，发言要谨慎避免被抗推"
        }
        
        prompt = f"""
        你正在参与狼人杀游戏。
        你的角色：{role_descriptions.get(self.role, self.role)}
        玩家ID：{self.player_id}
        游戏阶段：{context['game_phase']}
        存活玩家：{context['alive_players']}
        发言类型：{context['speech_type']}
        
        最近发言记录：
        {self._format_speech_history(context['history'])}
        
        请根据以上信息进行发言，要求：
        1. 符合你的角色身份
        2. 分析局势，给出合理推理
        3. 语言自然，像真人发言
        4. 长度在50-150字之间
        
        发言内容：
        """
        return prompt
    
    def _construct_vote_prompt(self, context: Dict) -> str:
        """构建投票的提示词"""
        prompt = f"""
        作为{self.role}（玩家{self.player_id}），请根据当前局势决定投票给谁。
        存活玩家：{context['alive_players']}
        游戏阶段：{context['game_phase']}
        
        请分析并只返回你要投票的玩家ID数字。
        投票目标：
        """
        return prompt
    
    def _get_skill_context(self) -> Dict:
        """获取技能使用的上下文"""
        return {
            "player_id": self.player_id,
            "role": self.role,
            "alive_players": self.knowledge_base.get("alive_players", []),
            "history": self.knowledge_base["history_speeches"][-5:],
            "death_info": self.knowledge_base.get("death_info", [])
        }
    
    def _construct_full_prompt(self, prompt: str, context: Dict) -> str:
        """构建完整的AI提示词"""
        full_context = {
            "role": self.role,
            "player_id": self.player_id,
            "game_state": self.knowledge_base,
            **context
        }
        return f"上下文：{json.dumps(full_context, ensure_ascii=False)}\n\n问题：{prompt}"
    
    def _simulate_ai_response(self, prompt: str, context: Dict) -> str:
        """模拟AI回复（用于测试）"""
        # 这里可以替换为真实的AI模型调用
        simulated_responses = {
            "speech": f"我是玩家{self.player_id}，作为{self.role}，我认为我们需要仔细分析当前的局势。",
            "vote": str(random.choice([p for p in context.get('alive_players', [1,2,3,4,5,6,7,8,9]) if p != self.player_id])),
            "skill": "基于当前局势，我选择行动。"
        }
        
        if "发言" in prompt or "speech" in prompt.lower():
            return simulated_responses["speech"]
        elif "投票" in prompt or "vote" in prompt.lower():
            return simulated_responses["vote"]
        else:
            return simulated_responses["skill"]
    
    def _format_speech_history(self, history: List[Dict]) -> str:
        """格式化发言历史"""
        formatted = []
        for speech in history:
            formatted.append(f"玩家{speech.get('player_id', '?')}: {speech.get('content', '')}")
        return "\n".join(formatted)
    
    def _parse_vote_decision(self, ai_response: str) -> int:
        """解析AI的投票决定"""
        try:
            # 尝试从响应中提取数字
            numbers = [int(s) for s in ai_response.split() if s.isdigit()]
            if numbers:
                return numbers[0]
        except:
            pass
        # 默认返回随机存活玩家（不包括自己）
        alive_players = self.knowledge_base.get("alive_players", [p for p in range(1, 10)])
        other_players = [p for p in alive_players if p != self.player_id]
        return random.choice(other_players) if other_players else -1
    
    def _parse_number_from_response(self, response: str) -> int:
        """从响应中解析数字"""
        try:
            numbers = [int(s) for s in response.split() if s.isdigit()]
            return numbers[0] if numbers else 0
        except:
            return 0
    
    def _parse_witch_decision(self, response: str) -> tuple:
        """解析女巫的决定"""
        response = response.lower()
        if "save" in response:
            numbers = [int(s) for s in response.split() if s.isdigit()]
            return "save", numbers[0] if numbers else 0
        elif "poison" in response:
            numbers = [int(s) for s in response.split() if s.isdigit()]
            return "poison", numbers[0] if numbers else 0
        else:
            return "abstain", 0
    
    def update_status(self, new_status: Dict[str, Any]):
        """更新Agent状态"""
        if "is_alive" in new_status:
            self.is_alive = new_status["is_alive"]
        if "skill_used" in new_status:
            self.skill_used = new_status["skill_used"]
    
    def __str__(self):
        return f"Agent(玩家{self.player_id}, 角色:{self.role}, 存活:{self.is_alive})"