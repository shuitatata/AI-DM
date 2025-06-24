import pytest
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path

from app.agents.character_manager import CharacterManagerAgent, CharacterManagerOutput
from app.core.template_manager import PromptManager
from app.models.game_state import (
    GameSession,
    WorldState,
    CharacterState,
    LLMCharacterStateUpdate,
    DynamicField,
)


@pytest.fixture
def prompt_manager(tmp_path: Path) -> PromptManager:
    """
    创建一个指向临时目录的 PromptManager fixture，
    并预先放置一个用于测试的 'character_form.txt' 模板。
    """
    agents_dir = tmp_path / "agents" / "zh"
    agents_dir.mkdir(parents=True)
    template_content = (
        "Template: {form_fields} | {current_data} | {world_context} | {input}"
    )
    (agents_dir / "character_form.txt").write_text(template_content, encoding="utf-8")
    return PromptManager(base_directory=str(tmp_path))


@pytest.fixture
def mock_llm() -> MagicMock:
    """创建一个模拟的LLM实例，它已经配置好可以用于Agent初始化。"""
    llm = MagicMock(name="MockLLM")
    llm.with_structured_output.return_value = MagicMock(name="StructuredChain")
    return llm


@pytest.fixture
def agent(prompt_manager: PromptManager, mock_llm: MagicMock) -> CharacterManagerAgent:
    """创建一个CharacterManagerAgent的实例用于测试。"""
    return CharacterManagerAgent(prompt_manager, mock_llm)


class TestCharacterManagerAgent:
    """为CharacterManagerAgent编写的单元测试套件。"""

    def test_initialization(self, agent: CharacterManagerAgent, mock_llm: MagicMock):
        """测试: Agent能否使用有效的依赖成功初始化。"""
        assert agent.llm is not None
        assert agent.chain is not None, "推理链应该在初始化时被创建"
        mock_llm.with_structured_output.assert_called_once_with(CharacterManagerOutput)

    def test_update_target_state(self, agent: CharacterManagerAgent):
        """测试: _update_target_state 方法能否正确更新角色状态。"""
        initial_state = CharacterState(name="初始角色", background="初始背景")
        initial_state.additional_info["力量"] = "10"

        update = LLMCharacterStateUpdate(
            name="新角色",
            physical_appearance="高大威猛",
            additional_info=[DynamicField(key="敏捷", value="12")],
        )

        agent._update_target_state(initial_state, update)

        assert initial_state.name == "新角色"
        assert initial_state.background == "初始背景"  # 未更新
        assert initial_state.physical_appearance == "高大威猛"
        assert initial_state.additional_info["力量"] == "10"
        assert initial_state.additional_info["敏捷"] == "12"

    def test_get_prompt_context(self, agent: CharacterManagerAgent):
        """测试: get_prompt_context 方法能否正确构建包含世界背景的上下文。"""
        session = GameSession(session_id="test_context")
        session.world_state = WorldState(name="艾泽拉斯", history="一段战火纷飞的历史")
        current_data = "当前无角色数据"
        user_input = "我想创建一个兽人战士"

        context = agent.get_prompt_context(session, current_data, user_input)

        assert "form_fields" in context
        assert "current_data" in context
        assert "input" in context
        assert "world_context" in context
        assert "艾泽拉斯" in context["world_context"]
        assert "战火纷飞" in context["world_context"]

    @pytest.mark.asyncio
    async def test_process_flow(self, agent: CharacterManagerAgent):
        """测试: 完整的process方法流程，使用mock的chain。"""
        # 1. 准备
        session = GameSession(session_id="test_process")
        session.world_state = WorldState(name="费伦")
        user_input = "我叫阿尔萨斯"

        mock_output = CharacterManagerOutput(
            character_state_update=LLMCharacterStateUpdate(name="阿尔萨斯"),
            response_text="好的，你叫阿尔萨斯。那你的外貌是怎样的？",
            is_complete=False,
        )

        # 替换内部的 chain 为一个可控的 mock
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_output)
        agent.chain = mock_chain

        # 2. 执行
        result = await agent.process({"session": session, "user_input": user_input})

        # 3. 断言
        mock_chain.ainvoke.assert_awaited_once()
        # 验证传递给ainvoke的上下文中是否包含了world_context
        call_args, _ = mock_chain.ainvoke.call_args
        assert "费伦" in call_args[0]["world_context"]

        assert result["response"] == "好的，你叫阿尔萨斯。那你的外貌是怎样的？"
        assert not result["is_complete"]
        assert result["updated_state"]["name"] == "阿尔萨斯"
        assert session.character_state.name == "阿尔萨斯"
