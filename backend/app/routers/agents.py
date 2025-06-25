from typing import Any, Dict, Literal
from pathlib import Path as P

from fastapi import APIRouter, HTTPException, Path as FastAPIPath
from pydantic import BaseModel

from app.agents.base_form_agent import FormBasedAgent
from app.agents.character_manager import CharacterManagerAgent
from app.agents.world_builder import WorldBuilderAgent
from app.agents.narrative_generator import NarrativeGeneratorAgent
from app.core.template_manager import PromptManager
from app.models.game_state import session_store
from app.services.llm_service import llm_service

# --- 模型定义 ---

AgentType = Literal["world-builder", "character-manager", "narrative-generator"]


class AgentProcessRequest(BaseModel):
    session_id: str
    user_input: str


router = APIRouter()

# --- Agent 实例管理 ---

# 简化版的Agent实例缓存, 它将在应用启动时被填充
AGENT_INSTANCES: Dict[str, Any] = {}


def initialize_agents():
    """初始化所有需要的Agent, 并填充到AGENT_INSTANCES缓存中"""
    if AGENT_INSTANCES:
        return

    # 此处路径是相对于当前文件 (backend/app/routers/agents.py)
    # P(__file__).parent.parent.parent -> backend/
    # P(__file__).parent.parent.parent.parent -> aidm/ (项目根目录)
    project_root = P(__file__).parent.parent.parent.parent
    templates_dir = project_root / "templates"

    prompt_manager = PromptManager(base_directory=str(templates_dir))
    llm = llm_service.get_llm()

    # 实例化所有Agents
    AGENT_INSTANCES["world-builder"] = WorldBuilderAgent(prompt_manager, llm)
    AGENT_INSTANCES["character-manager"] = CharacterManagerAgent(prompt_manager, llm)
    AGENT_INSTANCES["narrative-generator"] = NarrativeGeneratorAgent(
        prompt_manager, llm
    )
    print("Agents initialized.")


# --- API 端点 ---


@router.get("/{agent_type}/form", tags=["Agents"])
async def get_agent_form(
    agent_type: AgentType = FastAPIPath(
        ..., title="Agent类型", description="要获取表单的Agent类型"
    )
):
    """获取指定Agent的表单结构定义, 用于前端动态生成表单"""
    agent = AGENT_INSTANCES.get(agent_type)
    if not isinstance(agent, FormBasedAgent):
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent_type}' 不存在或不是表单类型的Agent"
        )

    return {"fields": agent.get_form_fields(), "field_map": agent.get_field_map()}


@router.post("/{agent_type}/process", tags=["Agents"])
async def process_with_agent(
    request: AgentProcessRequest,
    agent_type: AgentType = FastAPIPath(
        ..., title="Agent类型", description="要处理请求的Agent类型"
    ),
):
    """
    使用指定的Agent处理用户输入.
    这是创建世界和角色的核心交互端点.
    """
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=404, detail=f"会话 '{request.session_id}' 不存在"
        )

    agent = AGENT_INSTANCES.get(agent_type)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_type}' 不存在")

    try:
        # 调用Agent的核心处理方法
        result = await agent.process(
            {"session": session, "user_input": request.user_input}
        )

        # 检查Agent是否发出了创建完成的信号 (修正：应该检查字典中的 'is_complete' 键)
        if result.get("is_complete", False):
            if agent_type == "world-builder":
                session.is_world_created = True
                print(f"世界创建完成 for session {session.session_id}")
            elif agent_type == "character-manager":
                session.is_character_created = True
                print(f"角色创建完成 for session {session.session_id}")

        # Agent处理后, GameSession的状态可能已改变, 我们需要更新它
        session_store.update_session(session)

        return result
    except Exception as e:
        # 在真实应用中, 这里应该有更精细的错误处理和日志记录
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")
