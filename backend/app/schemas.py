"""数据模型定义"""

from pydantic import BaseModel, Field


class PlayRequest(BaseModel):
    session_id: str = Field(..., description="会话 ID，用于追踪用户状态")
    user_input: str = Field(..., description="玩家的输入")


class PlayResponse(BaseModel):
    role: str
    content: str
    done: bool
