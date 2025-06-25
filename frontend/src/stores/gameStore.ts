import { defineStore } from 'pinia';
import { createSession, getForm, processAgentInput, type AgentType, playGame, getSessionStatus } from '@/services/apiService';
import type { WorldState, CharacterState } from '@/services/apiService';

export type GamePhase = 'INIT' | 'WORLD_CREATION' | 'CHARACTER_CREATION' | 'GAMEPLAY' | 'GAME_OVER';

export interface Message {
    id: number;
    text: string;
    sender: 'DM' | 'Player';
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
        addMessage(text: string, sender: 'DM' | 'Player') {
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
                this.addMessage(data.message, 'DM');
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
                        this.addMessage("世界已经创建完毕！接下来，让我们创建你的角色吧。", 'DM');
                        this.startCharacterCreation();
                    }
                } else if (agentType === 'character-manager') {
                    this.characterState = result.updated_state as CharacterState;
                    if (result.is_complete) {
                        this.isCharacterCreated = true;
                        this.addMessage("角色创建完成！正在准备你的冒险...", "DM");
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

            // 在游戏开场时，玩家的输入（"开始"）不应显示
            if (userInput !== "开始") {
                this.addMessage(userInput, 'Player');
            }

            this.isReplying = true;
            try {
                const result = await playGame(this.sessionId, userInput);
                this.addMessage(result.narrative, 'DM');
                if (result.is_game_over) {
                    this.gamePhase = 'GAME_OVER';
                    this.addMessage("游戏结束。感谢你的游玩！", "DM");
                }
            } catch (error: any) {
                this.error = error.message || 'Failed to process player input';
            } finally {
                this.isReplying = false;
            }
        },

        async startCharacterCreation() {
            if (!this.sessionId) return;
            this.gamePhase = 'CHARACTER_CREATION';
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
                        this.addMessage("你的冒险现在正式开始。", "DM");
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