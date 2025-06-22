from fastapi import FastAPI

app = FastAPI(
    title="AI Dungeon Master",
    description="一个基于大型语言模型（LLM）的文字冒险游戏引擎。",
    version="0.1.0",
)


@app.get("/ping", summary="检查服务健康状况")
async def ping():
    """返回一个简单的 pong 消息，用于确认服务正在运行。"""
    return {"message": "pong"}
