"""游戏状态数据模型"""

from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime


class DynamicField(BaseModel):
    """一个动态的键值对"""

    key: str = Field(..., description="动态生成字段的名称或键")
    value: str = Field(..., description="动态生成字段的值")


class LLMWorldStateUpdate(BaseModel):
    """LLM为世界构建Agent生成的结构化输出。"""

    name: Optional[str] = Field(default=None, description="世界名称")
    geography: Optional[str] = Field(default=None, description="地理环境描述")
    history: Optional[str] = Field(default=None, description="历史背景")
    cultures: Optional[str] = Field(default=None, description="文化设定")
    magic_system: Optional[str] = Field(default=None, description="魔法体系")
    # 将 Dict[str, str] 修改为 List[DynamicField]
    additional_info: List[DynamicField] = Field(
        default_factory=list,
        description="由LLM动态生成的其他结构化世界信息列表，每个元素都是一个键值对。",
    )

    # (可选) 添加一个辅助方法，方便地将列表转回字典
    def get_additional_info_as_dict(self) -> Dict[str, str]:
        return {item.key: item.value for item in self.additional_info}


class LLMCharacterStateUpdate(BaseModel):
    """LLM为角色构建Agent生成的结构化输出。"""

    name: Optional[str] = Field(default=None, description="角色名称")
    physical_appearance: Optional[str] = Field(default=None, description="外貌描述")
    character_class: Optional[str] = Field(
        default=None,
        description="角色的主要职业、阶级或身份。例如：圣骑士、赏金猎人、星际商人、流浪者。",
    )
    background: Optional[str] = Field(default=None, description="背景故事")
    personality: Optional[str] = Field(
        default=None, description="性格特点、理想、羁绊、缺点等"
    )
    abilities: Optional[str] = Field(
        default=None, description="角色的技能、专长或魔法能力"
    )
    additional_info: List[DynamicField] = Field(
        default_factory=list,
        description="由LLM动态生成的其他结构化世界信息列表，每个元素都是一个键值对。",
    )

    def get_additional_info_as_dict(self) -> Dict[str, str]:
        return {item.key: item.value for item in self.additional_info}


class WorldState(BaseModel):
    """内部使用的世界状态模型"""

    name: Optional[str] = Field(default=None, description="世界名称")
    geography: Optional[str] = Field(default=None, description="地理环境描述")
    history: Optional[str] = Field(default=None, description="历史背景")
    cultures: Optional[str] = Field(default=None, description="文化设定")
    magic_system: Optional[str] = Field(default=None, description="魔法体系")
    additional_info: Dict[str, str] = Field(default_factory=dict)


class CharacterState(BaseModel):
    """角色状态模型"""

    name: Optional[str] = Field(default=None, description="角色名称")
    character_class: Optional[str] = Field(
        default=None,
        description="角色的主要职业、阶级或身份。例如：圣骑士、赏金猎人、星际商人、流浪者。",
    )
    physical_appearance: Optional[str] = Field(default=None, description="外貌描述")
    background: Optional[str] = Field(default=None, description="背景故事")
    personality: Optional[str] = Field(
        default=None, description="性格特点、理想、羁绊、缺点等"
    )
    abilities: Optional[str] = Field(
        default=None, description="角色的技能、专长或魔法能力"
    )
    additional_info: Dict[str, str] = Field(default_factory=dict)


class GameSession(BaseModel):
    """游戏会话模型"""

    session_id: str = Field(..., description="会话唯一标识")
    world_state: WorldState = Field(default_factory=WorldState, description="世界状态")
    character_state: CharacterState = Field(
        default_factory=CharacterState, description="角色状态"
    )
    # 添加两个状态标志
    is_world_created: bool = Field(False, description="世界是否已创建完成")
    is_character_created: bool = Field(False, description="角色是否已创建完成")

    current_scene: Optional[str] = Field(default=None, description="当前场景描述")
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
        """检查世界设定是否完整 (此方法将被弃用)"""
        return self.is_world_created

    def is_character_complete(self) -> bool:
        """检查角色设定是否完整 (此方法将被弃用)"""
        return self.is_character_created

    def is_ready_for_game(self) -> bool:
        """检查是否可以开始游戏"""
        return self.is_world_created and self.is_character_created


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


class NarrativeResponse(BaseModel):
    """定义叙事Agent的结构化输出模型"""

    inner_monologue: str = Field(
        ...,
        description="DM的内心思考，用于记录决策过程和对游戏状态变化的判断。这部分内容不会展示给玩家。",
    )
    narrative: str = Field(
        ...,
        description='呈现给玩家的故事内容，请使用第二人称（"你……"）来描述。',
    )
    is_game_over: bool = Field(
        False,
        description="如果玩家死亡、达成目标或陷入无法挽回的境地，则设为 true。",
    )
