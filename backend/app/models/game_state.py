"""游戏状态数据模型"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class WorldState(BaseModel):
    """世界状态模型"""

    name: Optional[str] = Field(None, description="世界名称")
    geography: Optional[str] = Field(None, description="地理环境描述")
    history: Optional[str] = Field(None, description="历史背景")
    cultures: Optional[str] = Field(None, description="文化设定")
    magic_system: Optional[str] = Field(None, description="魔法体系")
    additional_info: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="额外信息"
    )


class CharacterState(BaseModel):
    """角色状态模型"""

    name: Optional[str] = Field(None, description="角色名称")
    physical_appearance: Optional[str] = Field(None, description="外貌描述")
    background: Optional[str] = Field(None, description="背景故事")
    internal_motivation: Optional[str] = Field(None, description="内在动机")
    unique_traits: Optional[str] = Field(None, description="独特特征")
    additional_info: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="额外信息"
    )


class GameSession(BaseModel):
    """游戏会话模型"""

    session_id: str = Field(..., description="会话唯一标识")
    world_state: Optional[WorldState] = Field(
        default_factory=WorldState, description="世界状态"
    )
    character_state: Optional[CharacterState] = Field(
        default_factory=CharacterState, description="角色状态"
    )
    current_scene: Optional[str] = Field(None, description="当前场景描述")
    game_history: List[Dict[str, str]] = Field(
        default_factory=list, description="游戏历史记录"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    def add_message(self, role: str, content: str):
        """添加消息到游戏历史"""
        self.game_history.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )
        self.updated_at = datetime.now()

    def is_world_complete(self) -> bool:
        """检查世界设定是否完整"""
        return all(
            [
                self.world_state.name,
                self.world_state.geography,
                self.world_state.history,
                self.world_state.cultures,
                self.world_state.magic_system,
            ]
        )

    def is_character_complete(self) -> bool:
        """检查角色设定是否完整"""
        return all(
            [
                self.character_state.name,
                self.character_state.physical_appearance,
                self.character_state.background,
                self.character_state.internal_motivation,
                self.character_state.unique_traits,
            ]
        )

    def is_ready_for_game(self) -> bool:
        """检查是否可以开始游戏"""
        return self.is_world_complete() and self.is_character_complete()


class SessionStore:
    """会话存储管理器"""

    def __init__(self):
        self._sessions: Dict[str, GameSession] = {}

    def create_session(self, session_id: str) -> GameSession:
        """创建新会话"""
        session = GameSession(session_id=session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[GameSession]:
        """获取会话"""
        return self._sessions.get(session_id)

    def update_session(self, session: GameSession):
        """更新会话"""
        session.updated_at = datetime.now()
        self._sessions[session.session_id] = session

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def list_sessions(self) -> List[str]:
        """列出所有会话ID"""
        return list(self._sessions.keys())


# 全局会话存储实例
session_store = SessionStore()
