import pytest
import os
from dotenv import load_dotenv

from app.agents.character_manager import CharacterManagerAgent
from app.core.template_manager import PromptManager
from app.models.game_state import GameSession, WorldState
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

# 在所有测试运行前加载 .env 文件
load_dotenv()

# 检查API密钥是否存在，如果不存在，则跳过所有测试
API_KEY_EXISTS = os.getenv("API_KEY") is not None
REASON = "需要设置 API_KEY 环境变量以运行集成测试"


@pytest.mark.skipif(not API_KEY_EXISTS, reason=REASON)
@pytest.mark.asyncio
class TestCharacterManagerIntegration:
    """CharacterManagerAgent 的集成测试套件。"""

    @pytest.fixture(scope="class")
    def prompt_manager(self) -> PromptManager:
        """为集成测试提供一个真实的 PromptManager 实例。"""
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

    async def test_character_creation_dialogue(
        self, prompt_manager: PromptManager, llm_instance: ChatOpenAI
    ):
        """测试一个完整的角色创建对话流程。"""
        # 1. 初始化
        agent = CharacterManagerAgent(prompt_manager, llm_instance)
        session = GameSession(session_id="char-integration-test")
        # 为角色创建提供一个简单的世界背景
        session.world_state = WorldState(
            name="艾瑞多利亚",
            geography="一个由漂浮岛屿和水晶森林构成的奇幻世界。",
            history="曾发生过一场被称为'碎裂之战'的古老战争。",
        )

        # 2. 第一轮对话：用户给出名字和职业
        user_input_1 = "我想创建一个名叫'里昂'的圣骑士。"

        print(f"\n--- 对话 1 ---")
        print(f"用户输入: {user_input_1}")

        result_1 = await agent.process({"session": session, "user_input": user_input_1})

        print(f"Agent 回复: {result_1.get('response')}")
        print(f"角色状态更新: {session.character_state.model_dump(exclude_none=True)}")

        # 3. 断言第一轮
        assert isinstance(result_1, dict)
        assert "response" in result_1 and result_1["response"]
        assert not result_1["is_complete"]
        assert session.character_state.name == "里昂"
        background_text = session.character_state.background or ""
        traits_text = session.character_state.abilities or ""
        character_class_text = session.character_state.character_class or ""

        assert (
            "圣骑士" in background_text
            or "圣骑士" in traits_text
            or "圣骑士" in character_class_text
        ), "角色的背景或能力中应包含'圣骑士'关键词"

        # 4. 第二轮对话：用户补充外貌和动机
        user_input_2 = (
            "他有银色的短发和坚毅的蓝色眼睛。他的目标是寻找失落的圣物，为王国带来和平。"
        )

        print(f"\n--- 对话 2 ---")
        print(f"用户输入: {user_input_2}")

        result_2 = await agent.process({"session": session, "user_input": user_input_2})

        print(f"Agent 回复: {result_2.get('response')}")
        print(f"角色状态更新: {session.character_state.model_dump(exclude_none=True)}")

        # 5. 断言第二轮
        assert isinstance(result_2, dict)
        assert "response" in result_2 and result_2["response"]
        assert (
            session.character_state.physical_appearance is not None
            and "银色" in session.character_state.physical_appearance
        )
        assert (
            session.character_state.background is not None
            and ("圣物" in session.character_state.background
            or "relic" in session.character_state.background)
        )
        assert session.character_state.name == "里昂", "之前的状态应该被保留"
