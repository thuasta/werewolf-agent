/*
  types.ts

  说明：
  - 定义前端使用的核心类型（Role, Phase, Player, LogEntry, GameState, AgentDecision）。
  - 这些类型与比赛后台的 `game_state` / `decision` 协议相对应：
      * `GameState` 表示当前回合、阶段、玩家列表、日志与剩余时间等信息。
      * `AgentDecision` 表示智能体或人类在被请求时应提交的决策载体（natural_speech、vote_target 等）。
  - 在与后端集成时，请确保前后端约定的字段名与含义一致。
*/

export enum Role {
  WEREWOLF = 'WEREWOLF',
  VILLAGER = 'VILLAGER',
  SEER = 'SEER',
  WITCH = 'WITCH',
  HUNTER = 'HUNTER',
  UNKNOWN = 'UNKNOWN'
}

export enum Phase {
  NIGHT_WOLF = 'NIGHT_WOLF',
  NIGHT_WITCH = 'NIGHT_WITCH',
  NIGHT_SEER = 'NIGHT_SEER',
  NIGHT_HUNTER = 'NIGHT_HUNTER',
  DAY_ANNOUNCE = 'DAY_ANNOUNCE',
  DAY_DISCUSS = 'DAY_DISCUSS',
  DAY_VOTE = 'DAY_VOTE',
  GAME_OVER = 'GAME_OVER'
}

export interface Player {
  id: number;
  name: string; // e.g., "Agent-001" or "Human"
  isAlive: boolean;
  role: Role;
  isHuman?: boolean;
  avatarUrl?: string;
  suspicionScore?: number; // 0-100
}

export interface LogEntry {
  id: string;
  day: number;
  phase: Phase;
  speakerId?: number;
  content: string;
  type: 'system' | 'speech' | 'action' | 'alert';
  timestamp: number;
}

export interface GameState {
  day: number;
  phase: Phase;
  players: Player[];
  logs: LogEntry[];
  timeLeft: number; // Seconds remaining for current action
  winner: 'WEREWOLVES' | 'VILLAGERS' | null;
  selfId: number | null; // If playing as human
  sheriffId: number | null;
}

export interface AgentDecision {
  natural_speech: string;
  vote_target?: number;
  skill_target?: number;
  reasoning_steps: string[];
  suspicion_scores: Record<string, number>;
}

/*
  注：
  - `GameState` 是前端与后端交换的主要快照。后端应保证此结构包含当前回合信息与玩家列表。
  - `AgentDecision` 即为智能体/人类在被请求时提交的响应；比赛计分服务会解析 `reasoning_steps` 与 `suspicion_scores` 来评估策略质量。
*/