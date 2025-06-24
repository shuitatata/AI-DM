import pytest
import os
from dotenv import load_dotenv

from app.agents.world_builder import WorldBuilderAgent
from app.core.template_manager import PromptManager
from app.models.game_state import GameSession
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

# 在所有测试运行前加载 .env 文件
load_dotenv()

# 检查API密钥是否存在，如果不存在，则跳过所有测试
API_KEY_EXISTS = os.getenv("API_KEY") is not None
REASON = "需要设置 API_KEY 环境变量以运行集成测试"


@pytest.mark.skipif(not API_KEY_EXISTS, reason=REASON)
@pytest.mark.asyncio
class TestWorldBuilderIntegration:
    """
    WorldBuilderAgent 的集成测试套件。
    这个测试会真实调用 API。
    """

    @pytest.fixture(scope="class")
    def prompt_manager(self) -> PromptManager:
        """为集成测试提供一个真实的 PromptManager 实例。"""
        # 注意：这里的路径是相对于项目根目录的
        # 在运行 pytest 时，根目录通常是 backend/
        # 因此，我们需要向上追溯到项目根目录来找到 templates
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../templates")
        )
        return PromptManager(base_directory=base_dir)

    @pytest.fixture(scope="class")
    def llm_instance(self) -> ChatOpenAI:
        """根据环境变量提供一个真实的 ChatOpenAI 实例。"""
        return ChatOpenAI(
            model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
            temperature=float(os.getenv("TEMPERATURE", 0.7)),
            api_key=SecretStr(os.getenv("API_KEY", "")),
            base_url=os.getenv("BASE_URL"),
        )

    async def test_world_creation_dialogue(
        self, prompt_manager: PromptManager, llm_instance: ChatOpenAI
    ):
        """
        测试一个完整的世界构建对话流程。
        """
        # 1. 初始化
        agent = WorldBuilderAgent(prompt_manager, llm_instance)
        session = GameSession(session_id="integration-test-session")

        # 2. 第一轮对话：用户提出初步想法
        user_input_1 = (
            "我想创建一个叫‘艾瑞多利亚’的奇幻世界，那里有漂浮的岛屿和巨大的水晶森林。"
        )

        print("\n--- 对话 1 ---")
        print(f"用户输入: {user_input_1}")

        result_1 = await agent.process({"session": session, "user_input": user_input_1})

        print(f"Agent 回复: {result_1.get('response')}")
        print(f"世界状态更新: {session.world_state.model_dump(exclude_none=True)}")

        # 3. 断言第一轮
        assert isinstance(result_1, dict)
        assert "response" in result_1 and result_1["response"]
        assert "is_complete" in result_1 and not result_1["is_complete"]
        assert session.world_state.name == "艾瑞多利亚"
        assert session.world_state.geography is not None and (
            "漂浮的岛屿" in session.world_state.geography
            or "水晶森林" in session.world_state.geography
        )

        # 4. 第二轮对话：用户补充历史背景
        user_input_2 = "这个世界的历史很悠久，曾经发生过一场被称为‘碎裂之战’的古老战争，塑造了现在的格局。"

        print("\n--- 对话 2 ---")
        print(f"用户输入: {user_input_2}")

        result_2 = await agent.process({"session": session, "user_input": user_input_2})

        print(f"Agent 回复: {result_2.get('response')}")
        print(f"世界状态更新: {session.world_state.model_dump(exclude_none=True)}")

        # 5. 断言第二轮
        assert isinstance(result_2, dict)
        assert "response" in result_2 and result_2["response"]
        assert "is_complete" in result_2  # 完成与否取决于模型的判断，我们只检查字段存在
        assert session.world_state.history is not None
        assert "碎裂之战" in session.world_state.history
        assert session.world_state.name == "艾瑞多利亚", "之前的状态应该被保留"
