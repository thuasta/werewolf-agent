/*
    ActionPanel.tsx

    说明：
    - 提供人类玩家在“人类挑战”模式下的决策提交界面：发言（natural_speech）与目标选择（vote_target / skill_target）。
    - 组件接收当前 `gameState`，并根据 `phase` 与玩家存活状态启用/禁用输入控件：
            * 讨论阶段允许输入发言；投票阶段允许选择目标并提交决策。
    - onAction 会被调用并传入 `AgentDecision` 对象；当前实现为本地模拟（mock）发送。
    - 注意：真实竞赛应将 `AgentDecision` POST 到后端 AI 服务并由后端进行验证/计分。
*/

import React, { useState } from 'react';
import { AgentDecision, GameState, Phase } from '../types';
import { Send, Target, Microscope } from 'lucide-react';

interface ActionPanelProps {
    gameState: GameState;
    onAction: (decision: AgentDecision) => void;
}

const ActionPanel: React.FC<ActionPanelProps> = ({ gameState, onAction }) => {
    const [speech, setSpeech] = useState('');
    const [target, setTarget] = useState<string>('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Determine whether the local player may act. `isTurn` here is simplified:
    // it checks whether the player represented by `selfId` is alive. In a real
    // game you might also check turn order, timers, and role-specific permissions.
    const isTurn = gameState.players.find(p => p.id === gameState.selfId)?.isAlive;

    // Control which inputs are active depending on current phase.
    // - Discussion phases allow speech input.
    // - Vote phase enables target selection.
    const canSpeak = gameState.phase === Phase.DAY_DISCUSS || gameState.phase === Phase.DAY_ANNOUNCE;
    const canVote = gameState.phase === Phase.DAY_VOTE;
    // In a real implementation, we would check roles for Night phases

    const handleSubmit = () => {
        if (!speech && !target) return;
        setIsSubmitting(true);

        // Mock "Think" delay
        setTimeout(() => {
            // Build the AgentDecision object to follow the competition contract.
            // - `natural_speech`: human readable string for comment / narration.
            // - `vote_target`: numeric player id (if selected).
            // - `reasoning_steps`: an array of strings capturing the decision chain (useful for scoring/debugging).
            // - `suspicion_scores`: optional per-player scores produced by AI; here left empty.
            onAction({
                natural_speech: speech,
                vote_target: target ? parseInt(target) : undefined,
                reasoning_steps: ["User input received", "Processing strategy..."],
                suspicion_scores: {}
            });
            setSpeech('');
            setTarget('');
            setIsSubmitting(false);
        }, 500);
    };

    // If the player is not alive or not allowed to act, show a spectator message.
    if (!isTurn) {
        return (
            <div className="glass-panel p-6 rounded-xl text-center h-full flex items-center justify-center">
                <p className="text-gray-500 font-mono">You are spectating (or dead).</p>
            </div>
        );
    }

    return (
        <div className="glass-panel p-4 rounded-xl h-full flex flex-col">
            <h3 className="font-mono text-sm font-bold text-cyber-accent mb-4 flex items-center gap-2">
                <Microscope className="w-4 h-4" />
                DECISION MODULE
            </h3>

            <div className="flex-1 space-y-4">
                {/* Speech Input */}
                <div className={`space-y-2 ${!canSpeak ? 'opacity-50 pointer-events-none' : ''}`}>
                    <label className="text-xs text-gray-400 font-mono">NATURAL_SPEECH_OUTPUT</label>
                    <textarea
                        value={speech}
                        onChange={(e) => setSpeech(e.target.value)}
                        placeholder={canSpeak ? "Enter your argument..." : "Waiting for discussion phase..."}
                        className="w-full bg-cyber-900/50 border border-cyber-700 rounded-lg p-3 text-sm text-gray-200 focus:outline-none focus:border-cyber-accent h-24 resize-none font-mono"
                    />
                </div>

                {/* Action Input */}
                <div className={`space-y-2 ${!canVote ? 'opacity-50 pointer-events-none' : ''}`}>
                    <label className="text-xs text-gray-400 font-mono">TARGET_SELECTION (ID)</label>
                    <div className="flex gap-2">
                        <select
                            value={target}
                            onChange={(e) => setTarget(e.target.value)}
                            className="bg-cyber-900/50 border border-cyber-700 rounded-lg p-2 text-sm text-gray-200 flex-1 focus:outline-none focus:border-cyber-accent"
                        >
                            <option value="">Select Player ID...</option>
                            {gameState.players.map(p => (
                                <option key={p.id} value={p.id} disabled={!p.isAlive || p.id === gameState.selfId}>
                                    Player {p.id} {p.isAlive ? '' : '(Dead)'}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            <button
                onClick={handleSubmit}
                disabled={isSubmitting || (!canSpeak && !canVote)}
                className={`
            mt-4 w-full py-3 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-all
            ${isSubmitting || (!canSpeak && !canVote)
                        ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                        : 'bg-cyber-accent text-cyber-900 hover:bg-sky-400 shadow-[0_0_20px_rgba(14,165,233,0.3)]'
                    }
        `}
            >
                {isSubmitting ? 'TRANSMITTING...' : (
                    <>
                        <Send className="w-4 h-4" /> COMMIT DECISION
                    </>
                )}
            </button>
        </div>
    );
};

export default ActionPanel;