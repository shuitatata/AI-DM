"""FastAPI应用入口 - 联邦式Agent架构演示"""

import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入新架构组件
from app.models.game_state import session_store
from app.routers import agents as agents_router
from app.routers import game as game_router


# --- Lifespan 事件处理器 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期事件:
    - 在应用启动时, 调用 agets_router.initialize_agents() 来初始化所有Agent
    - 在应用关闭时, 可以添加清理逻辑
    """
    print("--- Server starting up ---")
    agents_router.initialize_agents()
    yield
    print("--- Server shutting down ---")


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Dungeon Master API",
    description="基于联邦式Agent架构的文字冒险游戏引擎",
    version="2.0.0",
    lifespan=lifespan,  # 注册lifespan事件
)

# CORS配置
# 定义允许的前端源
origins = [
    "http://localhost",
    "http://localhost:5173",  # Vue3 Vite 开发服务器的默认地址
    "http://127.0.0.1:5173",
    # 如果您有其他前端部署地址，也一并加入
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 将 "*" 修改为具体的源列表
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 路由注册 ---
# 将Agent相关的API路由包含进来, 并添加统一前缀
app.include_router(agents_router.router, prefix="/api/agents", tags=["Agents"])
app.include_router(game_router.router, prefix="/api/game", tags=["Game"])


# --- 数据模型 ---


class SessionCreateRequest(BaseModel):
    """创建会话请求"""

    session_id: Optional[str] = None


class SessionResponse(BaseModel):
    """会话响应"""

    session_id: str
    message: str


# --- API 端点 ---


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI Dungeon Master API v2.0 - 联邦式Agent架构",
        "architecture": "federated_agents",
        "docs": "/docs",
        "available_agent_endpoints": [
            "/api/agents/world-builder/form",
            "/api/agents/world-builder/process",
            "/api/agents/character-manager/form",
            "/api/agents/character-manager/process",
        ],
    }


@app.get("/ping", tags=["Health Check"])
async def ping():
    """健康检查"""
    return {"status": "ok", "architecture": "federated_agents"}


@app.post("/api/sessions", response_model=SessionResponse, tags=["Session Management"])
async def create_session(request: SessionCreateRequest):
    """创建新的游戏会话"""
    session_id = request.session_id or str(uuid.uuid4())

    if session_store.get_session(session_id):
        raise HTTPException(status_code=400, detail="会话已存在")

    session_store.create_session(session_id)
    logger.info(f"创建新会话: {session_id}")

    return SessionResponse(
        session_id=session_id,
        message="游戏会话创建成功！欢迎来到AI地下城主世界。请先使用 'world-builder' Agent创建你的世界。",
    )


@app.get("/api/sessions/{session_id}", tags=["Session Management"])
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


@app.delete("/api/sessions/{session_id}", tags=["Session Management"])
async def delete_session(session_id: str):
    """删除会话"""
    if session_store.delete_session(session_id):
        logger.info(f"删除会话: {session_id}")
        return {"message": "会话删除成功"}

    raise HTTPException(status_code=404, detail="会话不存在")


@app.get("/api/debug/sessions", tags=["Debug"])
async def list_all_sessions():
    """调试用：列出所有会话"""
    return {
        "sessions": session_store.list_sessions(),
        "total": len(session_store.list_sessions()),
    }


if __name__ == "__main__":
    import uvicorn

    # 注意: uvicorn的reload需要字符串形式的app路径
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
