from typing import Any, Dict

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.agents.base_form_agent import BaseAgent
from app.core.template_manager import PromptManager
from app.models.game_state import (
    CharacterState,
    GameSession,
    NarrativeResponse,
    WorldState,
)

# 这是一个简化的、用于存储所有用户会话历史的内存缓存。
# 在生产环境中，这里应该被替换为更持久化的存储，如 Redis 或数据库。
message_histories = {}


def get_session_history(session_id: str):
    """
    一个工厂函数，用于根据 session_id 获取或创建聊天历史记录对象。
    这是 RunnableWithMessageHistory 要求的回调函数。
    """
    if session_id not in message_histories:
        message_histories[session_id] = ChatMessageHistory()
    return message_histories[session_id]


class NarrativeGeneratorAgent(BaseAgent):
    """
    核心叙事Agent，负责驱动游戏主循环。
    使用LangChain的RunnableWithMessageHistory来管理对话历史。
    """

    def __init__(self, template_manager: PromptManager, llm_instance: Any):
        super().__init__(template_manager)
        self.llm = llm_instance
        self._setup_chain()

    def _setup_chain(self):
        """
        构建基于LangChain标准组件的、带记忆和结构化输出的推理链。
        """
        template_content = self.template_manager.get_template(
            "narrative_generator", "zh"
        )
        if not template_content:
            raise ValueError("无法加载 'narrative_generator' 模板")

        # 1. 创建包含历史记录占位符的Prompt模板
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", template_content),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{user_input}"),
            ]
        )

        # 2. 移除 with_structured_output，让LLM直接输出文本
        # structured_llm = self.llm.with_structured_output(NarrativeResponse)

        # 3. 创建基础的推理链: prompt | llm
        chain = prompt | self.llm

        # 4. 使用RunnableWithMessageHistory包装推理链，为其添加记忆功能
        self.chain_with_history = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="user_input",
            history_messages_key="chat_history",
        )

    def _format_game_context(
        self, world_state: WorldState, character_state: CharacterState
    ) -> str:
        """一个辅助函数，用于将复杂的游戏状态对象格式化为单个字符串，以便注入Prompt。"""
        # 这里可以根据需要进行更精细的格式化
        world_info = world_state.model_dump_json(indent=2, exclude_defaults=True)
        char_info = character_state.model_dump_json(indent=2, exclude_defaults=True)
        return f"### 世界设定\n{world_info}\n\n### 角色卡\n{char_info}"

    async def process(self, input_data: Dict[str, Any]) -> NarrativeResponse:
        """
        处理玩家输入并返回结构化的叙事响应。
        此版本经过修改，以适应不再直接输出结构化对象的链。
        """
        session = input_data.get("session")
        user_input = input_data.get("user_input")

        # 类型守卫
        if not isinstance(session, GameSession) or not isinstance(user_input, str):
            raise ValueError("需要提供有效的游戏会话和用户输入")

        game_context = self._format_game_context(
            session.world_state, session.character_state
        )

        # 调用带历史记录的链，它现在返回一个 AIMessage 对象
        response_message = await self.chain_with_history.ainvoke(
            {"game_context": game_context, "user_input": user_input},
            config={"configurable": {"session_id": session.session_id}},
        )

        # 手动构建 NarrativeResponse
        narrative_text = response_message.content
        # 简单的游戏结束检测
        is_game_over = "游戏结束" in narrative_text

        response = NarrativeResponse(
            narrative=narrative_text,
            inner_monologue="N/A in non-structured streaming mode.",
            is_game_over=is_game_over,
        )

        # 如果游戏结束，可以考虑在这里清理该会话的聊天记录
        if response.is_game_over and session.session_id in message_histories:
            del message_histories[session.session_id]

        return response

    async def stream_process(self, input_data: Dict[str, Any]):
        """
        以流式方式处理玩家输入，逐块生成并返回叙事内容。
        """
        session = input_data.get("session")
        user_input = input_data.get("user_input")

        if not isinstance(session, GameSession) or not isinstance(user_input, str):
            raise ValueError("需要提供有效的游戏会话和用户输入")

        game_context = self._format_game_context(
            session.world_state, session.character_state
        )

        # 使用 astream 来获取文本块流
        # 我们迭代流并仅 `yield` 每个块的文本内容
        async for chunk in self.chain_with_history.astream(
            {"game_context": game_context, "user_input": user_input},
            config={"configurable": {"session_id": session.session_id}},
        ):
            yield chunk.content

    def get_capabilities(self) -> list[str]:
        return [
            "narrative_generation",
            "game_loop_management",
            "stateful_storytelling",
        ]
