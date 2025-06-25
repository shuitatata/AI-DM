// src/services/apiService.ts

const API_BASE_URL = 'http://localhost:8000';

// --- 数据模型定义 (根据 API.md) ---

export interface WorldState {
    name: string;
    geography: string;
    history: string;
    cultures: string;
    magic_system: string;
    additional_info: Record<string, any>;
}

export interface CharacterState {
    name: string;
    physical_appearance: string;
    background: string;
    internal_motivation: string;
    unique_traits: string;
    additional_info: Record<string, any>;
}

export interface NarrativeResponse {
    inner_monologue: string;
    narrative: string;
    is_game_over: boolean;
}

export interface SessionResponse {
    session_id: string;
    message: string;
}

export interface FormDefinitionResponse {
    fields: string[];
    field_map: Record<string, string>;
}

export type AgentType = 'world-builder' | 'character-manager';

export interface AgentProcessResponse {
    response: string;
    is_complete: boolean;
    updated_state: Partial<WorldState> | Partial<CharacterState>;
}

export interface SessionStatusResponse {
    session_id: string;
    world_complete: boolean;
    character_complete: boolean;
    ready_for_game: boolean;
    world_state: WorldState;
    character_state: CharacterState;
}

// --- API 调用封装 ---

/**
 * 创建一个新的游戏会话
 * @param sessionId - 可选的自定义会话 ID
 * @returns {Promise<SessionResponse>}
 */
export async function createSession(sessionId?: string): Promise<SessionResponse> {
    const response = await fetch(`${API_BASE_URL}/api/sessions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '创建会话失败');
    }

    return response.json();
}

/**
 * 获取会话状态和信息
 * @param sessionId - 会话唯一标识符
 * @returns {Promise<SessionStatusResponse>}
 */
export async function getSessionStatus(sessionId: string): Promise<SessionStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`);

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '获取会话状态失败');
    }

    return response.json();
}

/**
 * 获取指定表单Agent的动态表单定义
 * @param agentType - Agent类型
 * @returns {Promise<FormDefinitionResponse>}
 */
export async function getForm(agentType: AgentType): Promise<FormDefinitionResponse> {
    const response = await fetch(`${API_BASE_URL}/api/agents/${agentType}/form`);

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `获取 ${agentType} 表单失败`);
    }

    return response.json();
}

/**
 * 使用指定的表单Agent处理用户输入
 * @param agentType - Agent类型
 * @param sessionId - 当前会话ID
 * @param userInput - 用户输入
 * @returns {Promise<AgentProcessResponse>}
 */
export async function processAgentInput(agentType: AgentType, sessionId: string, userInput: string): Promise<AgentProcessResponse> {
    const response = await fetch(`${API_BASE_URL}/api/agents/${agentType}/process`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId, user_input: userInput }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `处理 ${agentType} 输入失败`);
    }

    return response.json();
}

/**
 * 进行一轮游戏
 * @param sessionId - 当前会话ID
 * @param userInput - 玩家输入
 * @returns {Promise<NarrativeResponse>}
 */
export async function playGame(sessionId: string, userInput: string): Promise<NarrativeResponse> {
    const response = await fetch(`${API_BASE_URL}/api/game/play`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId, user_input: userInput }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '游戏主循环失败');
    }

    return response.json();
} 