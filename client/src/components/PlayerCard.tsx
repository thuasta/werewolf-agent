/*
    PlayerCard.tsx

    说明：
    - 负责渲染单个玩家的卡片视图（头像、编号、状态、身份展示）。
    - 在 `isGodMode` 或玩家死亡时显示真实身份（用于观战或调试）。
    - 提供视觉化的“怀疑度”条（当前为演示，使用随机值）。
    - 不改变游戏逻辑，仅做展示层：真实的怀疑度/投票逻辑应来自服务端或 AI 决策输出（`suspicion_scores`）。

    组件约定：
    - `player.isHuman` 用来标识当前用户（高亮显示）。
    - `player.isAlive` 决定视觉风格（灰化/去饱和）。
*/

import React from 'react';
import { Player, Role } from '../types';
import { Shield, Skull, Zap, Crown } from 'lucide-react';

interface PlayerCardProps {
    player: Player;
    isGodMode: boolean;
    onClick?: () => void;
}

const RoleIcon = ({ role }: { role: Role }) => {
    // Simple mapping from Role enum to a compact visual label.
    // This is purely presentational; role semantics live in `types.ts` and the game engine.
    switch (role) {
        case Role.WEREWOLF: return <span className="text-cyber-danger text-xs font-bold">WOLF</span>;
        case Role.SEER: return <span className="text-cyber-purple text-xs font-bold">SEER</span>;
        case Role.WITCH: return <span className="text-pink-500 text-xs font-bold">WITCH</span>;
        case Role.HUNTER: return <span className="text-cyber-warning text-xs font-bold">HUNT</span>;
        default: return <span className="text-cyber-success text-xs font-bold">VILL</span>;
    }
};

const PlayerCard: React.FC<PlayerCardProps> = ({ player, isGodMode, onClick }) => {
    // Only show role when appropriate:
    // - `isGodMode`: developer/observer wants to see all roles
    // - `!player.isAlive`: dead players' identities are revealed for clarity
    // - `player.isHuman`: the local human player should see their own role
    const showRole = isGodMode || !player.isAlive || player.isHuman;

    return (
        <div
            onClick={onClick}
            className={`
        relative flex flex-col items-center justify-center p-2 rounded-xl border-2 transition-all duration-300 cursor-pointer
        ${!player.isAlive ? 'opacity-50 grayscale border-gray-700' : 'border-cyber-700 hover:border-cyber-accent hover:shadow-[0_0_15px_rgba(14,165,233,0.4)]'}
        ${player.isHuman ? 'ring-2 ring-cyber-accent ring-offset-2 ring-offset-cyber-900' : ''}
        w-24 h-32 sm:w-28 sm:h-36
      `}
        >
            {/* Status Indicators */}
            <div className="absolute -top-2 -right-2 flex space-x-1">
                {/* Show a skull icon when player is dead */}
                {!player.isAlive && <Skull className="w-5 h-5 text-gray-400 bg-cyber-900 rounded-full p-0.5" />}
                {/*
                                    Mock 'sheriff' badge shown for a fixed id in the demo. In a real
                                    game the sheriffId would come from GameState and this check would
                                    be `player.id === gameState.sheriffId`.
                                */}
                {player.id === 2 && player.isAlive && <Crown className="w-5 h-5 text-yellow-400 bg-cyber-900 rounded-full p-0.5" />}
            </div>

            {/* Avatar */}
            <div className="relative w-14 h-14 sm:w-16 sm:h-16 mb-2">
                <img
                    src={player.avatarUrl}
                    alt={player.name}
                    className={`w-full h-full rounded-full object-cover border-2 ${player.isAlive ? 'border-gray-500' : 'border-gray-800'}`}
                />
                <div className="absolute -bottom-1 -right-1 bg-cyber-800 text-white text-xs px-1.5 rounded border border-gray-600">
                    {player.id}
                </div>
            </div>

            {/* Name & Role */}
            <div className="text-center w-full">
                <div className="text-xs text-gray-300 truncate w-full px-1 font-mono mb-1">
                    {player.isHuman ? 'YOU' : `Bot-${player.id}`}
                </div>

                <div className="h-4 flex items-center justify-center">
                    {/* Reveal role label or obfuscate with ??? when not allowed */}
                    {showRole ? (
                        <RoleIcon role={player.role} />
                    ) : (
                        <span className="text-gray-600 text-[10px]">???</span>
                    )}
                </div>
            </div>

            {/* Suspicion Bar (Visualization of AI logic) */}
            {player.isAlive && (
                <div className="absolute bottom-1 w-10/12 h-1 bg-cyber-800 rounded-full overflow-hidden mt-1">
                    {/*
                      Suspicion bar - visualization only. In production this should
                      reflect `player.suspicionScore` (0-100) provided by the AI or
                      scoring engine. Here we use a random width for demo purposes.
                    */}
                    <div
                        className="h-full bg-cyber-danger transition-all duration-500"
                        style={{ width: `${Math.random() * 100}%` }}
                    />
                </div>
            )}
        </div>
    );
};

export default PlayerCard;