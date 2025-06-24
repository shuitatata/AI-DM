import { defineStore } from 'pinia';
import { createSession, getForm, processAgentInput, type AgentType } from '@/services/apiService';
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
                        this.gamePhase = 'CHARACTER_CREATION';
                        // TODO: 触发角色创建流程
                        this.addMessage("世界已经创建完毕！接下来，让我们创建你的角色吧。", 'DM');
                    }
                }
                // TODO: 添加 character-manager 的逻辑
            } catch (error: any) {
                this.error = error.message || 'Failed to process input';
            } finally {
                this.isReplying = false;
            }
        }
    },
}); 