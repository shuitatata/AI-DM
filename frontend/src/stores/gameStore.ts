import { defineStore } from 'pinia';
import { createSession } from '@/services/apiService';
import type { WorldState, CharacterState } from '@/services/apiService';

interface GameState {
    sessionId: string | null;
    isLoading: boolean;
    error: string | null;
    worldState: Partial<WorldState>;
    characterState: Partial<CharacterState>;
    isWorldCreated: boolean;
    isCharacterCreated: boolean;
}

export const useGameStore = defineStore('game', {
    state: (): GameState => ({
        sessionId: null,
        isLoading: false,
        error: null,
        worldState: {},
        characterState: {},
        isWorldCreated: false,
        isCharacterCreated: false,
    }),

    actions: {
        async initializeSession() {
            this.isLoading = true;
            this.error = null;
            try {
                const data = await createSession();
                this.sessionId = data.session_id;
            } catch (error: any) {
                this.error = error.message || 'Failed to initialize session';
            } finally {
                this.isLoading = false;
            }
        },
    },
}); 