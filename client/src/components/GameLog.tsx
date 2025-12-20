/*
    GameLog.tsx

    说明：
    - 用于显示来自游戏流的时间序列日志（系统消息、玩家发言、动作、警报等）。
    - 订阅 `gameState.logs` 并自动滚动到最新项，便于观战者追踪比赛进程。
    - 日志项应包含 `phase` 与 `timestamp`，便于在 UI 上呈现阶段与时间戳。
*/

import React, { useEffect, useRef } from 'react';
import { LogEntry, Phase } from '../types';
import { Terminal, MessageSquare, Zap, AlertTriangle } from 'lucide-react';

interface GameLogProps {
    logs: LogEntry[];
}

const LogItem: React.FC<{ log: LogEntry }> = ({ log }) => {
    const getIcon = () => {
        // Choose an icon depending on the log type to help users scan messages.
        switch (log.type) {
            case 'speech': return <MessageSquare className="w-4 h-4 text-cyber-accent" />;
            case 'action': return <Zap className="w-4 h-4 text-cyber-warning" />;
            case 'alert': return <AlertTriangle className="w-4 h-4 text-cyber-danger" />;
            default: return <Terminal className="w-4 h-4 text-gray-500" />;
        }
    };

    const getColor = () => {
        switch (log.type) {
            case 'speech': return 'text-gray-200';
            case 'action': return 'text-cyber-warning';
            case 'alert': return 'text-cyber-danger font-bold';
            default: return 'text-gray-400 italic';
        }
    };

    return (
        <div className="flex gap-3 mb-3 text-sm animate-fade-in">
            <div className="mt-0.5 opacity-70 shrink-0">
                {getIcon()}
            </div>
            <div className="flex-1">
                <div className="flex items-center gap-2 mb-0.5">
                    {log.speakerId && (
                        <span className="font-mono text-cyber-accent text-xs bg-cyber-800 px-1 rounded">
                            Player {log.speakerId}
                        </span>
                    )}
                    <span className="text-[10px] text-gray-600 font-mono uppercase">
                        {/* Show the phase and a human-readable time for each log */}
                        {log.phase.replace('_', ' ')} • {new Date(log.timestamp).toLocaleTimeString([], { hour12: false })}
                    </span>
                </div>
                <p className={`${getColor()} leading-relaxed`}>{log.content}</p>
            </div>
        </div>
    );
};

const GameLog: React.FC<GameLogProps> = ({ logs }) => {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    return (
        <div className="flex flex-col h-full glass-panel rounded-xl overflow-hidden">
            <div className="bg-cyber-800/50 px-4 py-3 border-b border-white/5 flex items-center gap-2">
                <Terminal className="w-4 h-4 text-cyber-accent" />
                <h3 className="font-mono text-sm font-bold tracking-wider text-gray-300">TERMINAL LOGS</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-4 scrollbar-hide bg-cyber-900/30">
                {logs.length === 0 && (
                    <div className="text-center text-gray-600 mt-10 italic">
                        Waiting for game stream...
                    </div>
                )}
                {logs.map((log) => (
                    <LogItem key={log.id} log={log} />
                ))}
                <div ref={bottomRef} />
            </div>
        </div>
    );
};

export default GameLog;