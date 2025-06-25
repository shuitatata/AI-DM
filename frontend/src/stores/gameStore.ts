import { defineStore } from 'pinia';
import { createSession, processAgentInput, type AgentType, getSessionStatus, streamPlayGame } from '@/services/apiService';
import type { WorldState, CharacterState } from '@/services/apiService';

export type GamePhase = 'INIT' | 'WORLD_CREATION' | 'CHARACTER_CREATION' | 'GAMEPLAY' | 'GAME_OVER';

// 让Message接口支持一个新的sender类型
export interface Message {
    id: number;
    text: string;
    sender: 'DM' | 'Player' | 'System';
}

interface GameState {
    sessionId: string | null;
    gamePhase: GamePhase;
    isInitializing: boolean;
    isReplying: boolean;
    error: string | null;
    messages: Message[];
    worldState: Partial<WorldState>;
    characterState: Partial<CharacterState>;
    isWorldCreated: boolean;
    isCharacterCreated: boolean;
}

export const useGameStore = defineStore('game', {
    state: (): GameState => ({
        sessionId: null,
        gamePhase: 'INIT',
        isInitializing: false,
        isReplying: false,
        error: null,
        messages: [],
        worldState: {},
        characterState: {},
        isWorldCreated: false,
        isCharacterCreated: false,
    }),

    actions: {
        addMessage(text: string, sender: 'DM' | 'Player' | 'System') {
            const newMessage: Message = {
                id: Date.now(),
                text,
                sender,
            };
            this.messages.push(newMessage);
        },

        async initializeSession() {
            this.isInitializing = true;
            this.error = null;
            try {
                const data = await createSession();
                this.sessionId = data.session_id;
                this.addMessage(
                    "游戏会话创建成功！欢迎来到AI地下城主世界。在这里，您需要先描绘您想游玩的世界，再创造您的专属角色，然后就可以开始一场独一无二的冒险了！",
                    'DM'
                );
                this.isInitializing = false;
                await this.startWorldCreation();
            } catch (error: any) {
                this.error = error.message || 'Failed to initialize session';
                this.isInitializing = false;
            }
        },

        async startWorldCreation() {
            if (!this.sessionId) return;
            this.gamePhase = 'WORLD_CREATION';
            this.addMessage("开始创建世界", "System");
            this.isReplying = true;
            try {
                // 向用户发送第一条引导消息
                const firstPrompt = await processAgentInput('world-builder', this.sessionId, "你好，我想创建一个新的世界。");
                this.addMessage(firstPrompt.response, 'DM');
            } catch (error: any) {
                this.error = error.message || 'Failed to start world creation';
            } finally {
                this.isReplying = false;
            }
        },

        async sendAgentMessage(userInput: string, agentType: AgentType) {
            if (!this.sessionId) return;

            this.addMessage(userInput, 'Player');
            this.isReplying = true;
            try {
                const result = await processAgentInput(agentType, this.sessionId, userInput);
                this.addMessage(result.response, 'DM');

                if (agentType === 'world-builder') {
                    this.worldState = result.updated_state as WorldState;
                    if (result.is_complete) {
                        this.isWorldCreated = true;
                        this.addMessage("世界创建完成", 'System');
                        this.startCharacterCreation();
                    }
                } else if (agentType === 'character-manager') {
                    this.characterState = result.updated_state as CharacterState;
                    if (result.is_complete) {
                        this.isCharacterCreated = true;
                        this.addMessage("角色创建完成", "System");
                        this.pollForGameReady();
                    }
                }
            } catch (error: any) {
                this.error = error.message || 'Failed to process input';
            } finally {
                this.isReplying = false;
            }
        },

        async sendPlayerInput(userInput: string) {
            if (!this.sessionId) return;

            if (userInput !== "开始") {
                this.addMessage(userInput, 'Player');
            }

            this.isReplying = true;
            // 创建一个空的 DM 消息用于填充流式数据
            const dmMessage: Message = { id: Date.now(), sender: 'DM', text: '' };
            this.messages.push(dmMessage);

            await streamPlayGame(
                this.sessionId,
                userInput,
                (chunk) => {
                    // 追加收到的数据块
                    dmMessage.text += chunk;
                },
                (error) => {
                    this.error = error.message || '流式传输发生错误';
                    this.isReplying = false;
                },
                () => {
                    // 流结束
                    this.isReplying = false;
                    // 这里可以添加游戏是否结束的逻辑
                }
            );
        },

        async startCharacterCreation() {
            if (!this.sessionId) return;
            this.gamePhase = 'CHARACTER_CREATION';
            this.addMessage("开始创建角色", "System");
            this.isReplying = true;
            try {
                const firstPrompt = await processAgentInput('character-manager', this.sessionId, "你好，我想创建一个角色。");
                this.addMessage(firstPrompt.response, 'DM');
            } catch (error: any) {
                this.error = error.message || 'Failed to start character creation';
            } finally {
                this.isReplying = false;
            }
        },

        pollForGameReady() {
            if (!this.sessionId) return;

            const intervalId = setInterval(async () => {
                if (!this.sessionId) {
                    clearInterval(intervalId);
                    return;
                }
                try {
                    const status = await getSessionStatus(this.sessionId);
                    if (status.ready_for_game) {
                        clearInterval(intervalId);
                        this.gamePhase = 'GAMEPLAY';
                        this.addMessage("准备就绪... 冒险即将拉开序幕！", "System");
                        this.sendPlayerInput("开始");
                    }
                } catch (error) {
                    this.error = "无法验证游戏状态，请稍后重试。";
                    clearInterval(intervalId);
                }
            }, 1000); // 每秒查询一次

            // 设置一个超时，以防万一
            setTimeout(() => {
                if (this.gamePhase !== 'GAMEPLAY') {
                    clearInterval(intervalId);
                    if (!this.error) {
                        this.error = "游戏准备超时，请尝试刷新页面。";
                    }
                }
            }, 20000); // 20秒超时
        },
    },
}); 