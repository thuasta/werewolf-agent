/*
  App.tsx - 主应用与路由入口

  说明：
  - 管理页面路由（Lobby / Arena），提供整体布局（Header + 主内容区）。
  - 包含三个主要视图职责：
    1. Lobby：选择模式（观战 / 回放 / 人类挑战），初始化或重置游戏引擎。
    2. Arena：展示游戏主界面，包括玩家面板（PlayerCard）、日志（GameLog）、操作面板（ActionPanel）或统计（StatsChart）。
    3. Layout：统一页面头部导航与主题样式。
  - 通过 `mockGameEngine` 暴露的 `subscribeToGame`、`startGameLoop`、`sendHumanAction` 等函数与模拟后端交互。

  与比赛规则关联：Arena 中展示的 `day/phase/timeLeft`、玩家状态（role, isAlive）和日志，可以直接映射到竞赛中的 `game_state` 与 `decision` 协议。
*/

import React, { useState, useEffect } from 'react';
import { HashRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Activity, Play, Film, Eye, Cpu, Users } from 'lucide-react';
import { startGameLoop, subscribeToGame, sendHumanAction, getInitialState, resetGame } from './services/mockGameEngine';
import type { GameState, AgentDecision } from '../src/types';
import PlayerCard from './components/PlayerCard';
import GameLog from './components/GameLog';
import ActionPanel from './components/ActionPanel';
import StatsChart from './components/StatsChart';

// --- Layout Component ---
const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-cyber-900 text-gray-100 font-sans selection:bg-cyber-accent selection:text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-white/10 bg-cyber-900/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-8 h-8 bg-gradient-to-br from-cyber-accent to-cyber-purple rounded-lg flex items-center justify-center">
              <Cpu className="text-white w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight leading-none">UNDER TIDES:</h1>
              <p className="text-[10px] text-cyber-accent font-mono tracking-wider">AI WEREWOLVES ARENA</p>
            </div>
          </div>

          <nav className="flex gap-1 bg-cyber-800/50 p-1 rounded-lg">
            <button
              onClick={() => navigate('/')}
              className={`px-4 py-1.5 rounded text-xs font-medium transition-colors ${isActive('/') ? 'bg-cyber-700 text-white' : 'text-gray-400 hover:text-white'}`}
            >
              LOBBY
            </button>
            <button
              onClick={() => navigate('/arena')}
              className={`px-4 py-1.5 rounded text-xs font-medium transition-colors ${isActive('/arena') ? 'bg-cyber-700 text-white' : 'text-gray-400 hover:text-white'}`}
            >
              ARENA
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      {/* Main content region - pages will be injected here by Router */}
      <main className="flex-1 flex flex-col">
        {children}
      </main>
    </div>
  );
};

// --- Lobby Page ---
const Lobby = () => {
  const navigate = useNavigate();

  const modes = [
    {
      title: "SPECTATOR MODE",
      desc: "Watch top-tier AI agents battle in real-time.",
      icon: <Eye className="w-8 h-8 mb-4 text-cyber-accent" />,
      action: () => { resetGame(); startGameLoop(); navigate('/arena?mode=spectator'); }
    },
    {
      title: "REPLAY ANALYSIS",
      desc: "Review historical matches with full state inspection.",
      icon: <Film className="w-8 h-8 mb-4 text-cyber-purple" />,
      action: () => { resetGame(); navigate('/arena?mode=replay'); }
    },
    {
      title: "HUMAN CHALLENGE",
      desc: "Join the lobby as Player 1 and face the AI.",
      icon: <Users className="w-8 h-8 mb-4 text-cyber-success" />,
      action: () => { resetGame(); startGameLoop(); navigate('/arena?mode=human'); }
    }
  ];

  // Lobby shows several start modes; clicking a card starts or navigates accordingly.
  return (
    <div className="flex-1 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyber-accent/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyber-purple/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1.5s' }}></div>
      </div>

      <div className="max-w-5xl w-full grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
        {modes.map((mode, i) => (
          <div
            key={i}
            onClick={mode.action}
            className="group glass-panel p-8 rounded-2xl border border-white/5 hover:border-cyber-accent/50 cursor-pointer transition-all duration-300 hover:-translate-y-1"
          >
            <div className="bg-cyber-800/50 w-16 h-16 rounded-xl flex items-center justify-center mb-6 group-hover:bg-cyber-800 transition-colors">
              {mode.icon}
            </div>
            <h2 className="text-xl font-bold text-white mb-2 font-mono">{mode.title}</h2>
            <p className="text-gray-400 text-sm leading-relaxed">{mode.desc}</p>
            <div className="mt-6 flex items-center text-cyber-accent text-xs font-bold tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
              INITIALIZE <Activity className="w-3 h-3 ml-2" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// --- Arena Page ---
const Arena = () => {
  const [gameState, setGameState] = useState<GameState>(getInitialState());
  const [godMode, setGodMode] = useState(false);
  const location = useLocation();

  // Parse query param for mode
  const mode = new URLSearchParams(location.search).get('mode') || 'spectator';
  const isReplay = mode === 'replay';

  useEffect(() => {
    const unsubscribe = subscribeToGame((newState) => {
      setGameState(newState);
    });
    return () => {
      // ensure the cleanup returns void even if unsubscribe() returns a boolean
      void unsubscribe();
    };
  }, []);

  // subscribeToGame registers a listener to receive updated GameState objects.
  // This mirrors how a real application might receive server-sent updates (WebSocket/SSE).

  // Determine Grid Layout for 9 Players
  // Visualizing as a 3x3 grid or circle. Let's do a specialized layout.
  // Top: 3, Middle: 3 (Left, Center-Table, Right), Bottom: 3
  const renderPlayerGrid = () => {
    // Mapping specific indices to create a "seated" feel
    const topRow = gameState.players.slice(3, 6); // 4,5,6
    const midRowLeft = gameState.players[2]; // 3
    const midRowRight = gameState.players[6]; // 7
    const bottomRow = [gameState.players[1], gameState.players[0], gameState.players[8], gameState.players[7]].slice(0, 3); // 2,1,9 (using simplified logic for demo)

    // Actually, simpler loop is better for robustness
    // Render a responsive 3x3 grid of player cards. Each card renders the
    // localized view for a player (avatar, id, role when visible, suspicion bar).
    return (
      <div className="grid grid-cols-3 gap-4 w-full max-w-2xl mx-auto aspect-square p-4 relative">
        {/* Center Table decoration */}
        <div className="absolute inset-0 m-auto w-1/2 h-1/2 bg-cyber-800/30 rounded-full border border-white/5 flex flex-col items-center justify-center z-0 pointer-events-none backdrop-blur-sm">
          <div className="text-3xl font-bold font-mono text-cyber-accent tracking-widest">
            DAY {gameState.day}
          </div>
          <div className="text-xs text-cyber-warning mt-1 uppercase tracking-wider">
            {gameState.phase.replace('_', ' ')}
          </div>
          <div className="mt-4 text-4xl font-mono font-light text-white">
            {gameState.timeLeft}s
          </div>
        </div>

        {/* Players */}
        {gameState.players.map((player) => (
          <div key={player.id} className="flex items-center justify-center z-10">
            {/*
              PlayerCard receives the player object and a flag telling it whether
              to reveal roles (godMode or spectator). In human mode the UI hides
              roles unless revealed by game logic.
            */}
            <PlayerCard player={player} isGodMode={godMode || mode === 'spectator'} />
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col lg:flex-row overflow-hidden h-[calc(100vh-64px)]">

      {/* LEFT COLUMN: Game Board */}
      <div className="flex-[2] p-4 flex flex-col relative bg-gradient-to-b from-transparent to-cyber-900/50">
        {/* Toolbar */}
        <div className="absolute top-4 left-4 z-20 flex gap-2">
          <button
            onClick={() => setGodMode(!godMode)}
            className={`px-3 py-1 rounded text-xs font-mono border ${godMode ? 'bg-cyber-accent text-cyber-900 border-cyber-accent' : 'bg-transparent text-gray-400 border-gray-700'}`}
          >
            {godMode ? 'GOD_VIEW: ON' : 'GOD_VIEW: OFF'}
          </button>
          {isReplay && (
            <div className="flex gap-1 bg-cyber-800 rounded px-2 items-center">
              <Play className="w-3 h-3 text-green-400" />
              <span className="text-xs text-gray-300 font-mono">REPLAYING...</span>
            </div>
          )}
        </div>

        {/* The Table */}
        <div className="flex-1 flex items-center justify-center overflow-y-auto">
          {renderPlayerGrid()}
        </div>
      </div>

      {/* RIGHT COLUMN: Info Panels */}
      <div className="flex-1 lg:max-w-md bg-cyber-800/20 border-l border-white/5 flex flex-col h-full">

        {/* Top: Action/Stats Panel */}
        <div className="h-1/3 p-4 border-b border-white/5">
          {mode === 'human' ? (
            <ActionPanel gameState={gameState} onAction={sendHumanAction} />
          ) : (
            <StatsChart players={gameState.players} />
          )}
        </div>

        {/* Bottom: Logs */}
        <div className="flex-1 p-4 min-h-0">
          <GameLog logs={gameState.logs} />
        </div>

      </div>
    </div>
  );
};

// --- Main App ---
const App = () => {
  return (
    <HashRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Lobby />} />
          <Route path="/arena" element={<Arena />} />
        </Routes>
      </Layout>
    </HashRouter>
  );
};

export default App;