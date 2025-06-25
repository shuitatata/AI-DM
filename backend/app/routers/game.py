from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json

from app.models.game_state import NarrativeResponse, session_store
from app.routers.agents import AGENT_INSTANCES


class GamePlayRequest(BaseModel):
    session_id: str
    user_input: str


router = APIRouter()


@router.post("/play", response_model=NarrativeResponse)
async def play_turn(request: GamePlayRequest):
    """
    游戏主循环端点。
    接收玩家的行动，调用核心叙事Agent，并返回下一段故事。
    """
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=404, detail=f"会话 '{request.session_id}' 不存在"
        )

    # 检查游戏是否已经可以开始
    if not session.is_ready_for_game():
        raise HTTPException(
            status_code=400,
            detail="游戏尚未准备就绪。请先完成世界和角色的创建。",
        )

    # 获取叙事Agent实例
    narrative_agent = AGENT_INSTANCES.get("narrative-generator")
    if not narrative_agent:
        # 这是一个服务器内部错误，因为Agent应该在启动时就被初始化了
        raise HTTPException(status_code=500, detail="核心叙事Agent未初始化")

    try:
        # 调用Agent处理玩家输入
        narrative_response = await narrative_agent.process(
            {"session": session, "user_input": request.user_input}
        )

        # Agent的响应中包含了游戏状态的判断
        if narrative_response.is_game_over:
            # 如果游戏结束，我们可以从会话存储中删除这个会话
            session_store.delete_session(request.session_id)
            print(f"游戏会话 {request.session_id} 已结束并被清理。")

        return narrative_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理游戏回合时发生错误: {str(e)}")


@router.post("/play/stream")
async def play_turn_stream(request: GamePlayRequest):
    """
    游戏主循环的流式端点。
    """
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=404, detail=f"会话 '{request.session_id}' 不存在"
        )
    if not session.is_ready_for_game():
        raise HTTPException(
            status_code=400, detail="游戏尚未准备就绪。请先完成世界和角色的创建。"
        )

    narrative_agent = AGENT_INSTANCES.get("narrative-generator")
    if not narrative_agent:
        raise HTTPException(status_code=500, detail="核心叙事Agent未初始化")

    async def stream_generator():
        full_text_chunks = []
        try:
            # agent的stream_process现在直接yield纯文本块
            async for text_chunk in narrative_agent.stream_process(
                {"session": session, "user_input": request.user_input}
            ):
                if not text_chunk:
                    continue

                full_text_chunks.append(text_chunk)

                # SSE格式要求每个消息以 "data: " 开头，以 "\n\n" 结尾。
                # 直接发送原始文本块。
                yield f"data: {text_chunk}\n\n"
                await asyncio.sleep(0.02)  # 轻微延迟以改善前端接收效果

            # 流结束后，检查游戏是否结束
            final_narrative = "".join(full_text_chunks)
            if "游戏结束" in final_narrative:
                session_store.delete_session(request.session_id)
                print(f"游戏会话 {request.session_id} 已结束并被清理。")

        except Exception as e:
            # 在流中处理错误
            error_message = json.dumps({"error": f"处理游戏回合时发生错误: {str(e)}"})
            yield f"data: {error_message}\n\n"
        finally:
            # 发送一个特殊的结束信号
            yield "data: [DONE]\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")
