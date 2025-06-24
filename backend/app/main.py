"""FastAPI应用入口 - 联邦式Agent架构演示"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import logging

# 导入新架构组件
from app.core.template_manager import PromptManager
from app.agents.world_builder import WorldBuilderAgent
from app.models.game_state import session_store
from app.services.llm_service import llm_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Dungeon Master API",
    description="基于联邦式Agent架构的文字冒险游戏引擎",
    version="2.0.0",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局组件初始化
template_manager = PromptManager()
world_builder = WorldBuilderAgent(template_manager, llm_service.get_llm())


class SessionCreateRequest(BaseModel):
    """创建会话请求"""

    session_id: Optional[str] = None


class WorldFormRequest(BaseModel):
    """世界设定表单请求"""

    session_id: str
    user_input: str


class SessionResponse(BaseModel):
    """会话响应"""

    session_id: str
    message: str


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI Dungeon Master API v2.0 - 联邦式Agent架构",
        "architecture": "federated_agents",
        "available_agents": [
            "WorldBuilderAgent",
            "CharacterManagerAgent (TODO)",
            "StoryParserAgent (TODO)",
            "NarrativeGeneratorAgent (TODO)",
            "StateUpdaterAgent (TODO)",
        ],
    }


@app.get("/ping")
async def ping():
    """健康检查"""
    return {"status": "ok", "architecture": "federated_agents"}


@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """创建新的游戏会话"""
    session_id = request.session_id or str(uuid.uuid4())

    # 检查会话是否已存在
    if session_store.get_session(session_id):
        raise HTTPException(status_code=400, detail="会话已存在")

    # 创建新会话
    session_store.create_session(session_id)
    logger.info(f"创建新会话: {session_id}")

    return SessionResponse(
        session_id=session_id,
        message="游戏会话创建成功！欢迎来到AI地下城主世界。让我们先创建你的世界设定吧！",
    )


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话状态"""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {
        "session_id": session_id,
        "world_complete": session.is_world_complete(),
        "character_complete": session.is_character_complete(),
        "ready_for_game": session.is_ready_for_game(),
        "world_state": session.world_state.model_dump(),
        "character_state": session.character_state.model_dump(),
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


@app.post("/api/world-form")
async def process_world_form(request: WorldFormRequest):
    """处理世界设定表单输入"""
    # 获取会话
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    try:
        # 使用世界构建Agent处理输入
        result = await world_builder.process(
            {"session": session, "user_input": request.user_input}
        )

        # 更新会话
        session.add_message("user", request.user_input)
        session.add_message("assistant", result["response"])
        session_store.update_session(session)

        logger.info(f"世界设定处理完成 - 会话: {request.session_id}")

        return {
            "response": result["response"],
            "is_world_complete": result["is_complete"],
            "world_state": result["updated_state"],
        }

    except Exception as e:
        logger.error(f"处理世界设定时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.get("/api/agents/capabilities")
async def get_agent_capabilities():
    """获取所有Agent的能力"""
    return {
        "world_builder": world_builder.get_capabilities(),
        "template_manager": {
            "available_templates": template_manager.get_available_templates()
        },
        "llm_service": {
            "is_real_llm": llm_service.is_real_llm(),
            "model_name": llm_service.settings.model_name,
            "temperature": llm_service.settings.temperature,
        },
    }


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    if session_store.delete_session(session_id):
        logger.info(f"删除会话: {session_id}")
        return {"message": "会话删除成功"}
    else:
        raise HTTPException(status_code=404, detail="会话不存在")


@app.get("/api/debug/sessions")
async def list_all_sessions():
    """调试用：列出所有会话"""
    return {
        "sessions": session_store.list_sessions(),
        "total": len(session_store.list_sessions()),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
