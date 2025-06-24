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