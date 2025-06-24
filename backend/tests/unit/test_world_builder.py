import pytest
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path

from app.agents.world_builder import WorldBuilderAgent, WorldBuilderOutput
from app.core.template_manager import PromptManager
from app.models.game_state import GameSession, WorldState, LLMWorldStateUpdate, DynamicField


@pytest.fixture
def prompt_manager(tmp_path: Path) -> PromptManager:
    """
    创建一个指向临时目录的 PromptManager fixture，
    并预先放置一个用于测试的 'world_form.txt' 模板。
    """
    agents_dir = tmp_path / "agents" / "zh"
    agents_dir.mkdir(parents=True)
    template_content = (
        "Template: {{ form_fields }} | {{ current_data }} | {{ user_input }}"
    )
    (agents_dir / "world_form.txt").write_text(template_content, encoding="utf-8")
    return PromptManager(base_directory=str(tmp_path))


class TestWorldBuilderAgent:
    """
    为 WorldBuilderAgent 编写的单元测试套件。
    """

    def test_initialization(self, prompt_manager: PromptManager):
        """测试: Agent能否使用有效的依赖成功初始化。"""
        # 创建一个灵活的mock来模拟LLM
        mock_llm = MagicMock(name="MockLLM")
        # 关键：配置mock以正确响应 with_structured_output 调用
        mock_llm.with_structured_output.return_value = MagicMock(name="StructuredChain")

        # 现在初始化应该可以成功了
        agent = WorldBuilderAgent(prompt_manager, mock_llm)

        assert agent.llm is not None
        assert agent.chain is not None, "推理链应该在初始化时被创建"
        # 验证 with_structured_output 是否被正确调用，并传入了正确的模型
        mock_llm.with_structured_output.assert_called_once_with(WorldBuilderOutput)

    def test_initialization_fails_without_llm(self, prompt_manager: PromptManager):
        """测试: 没有提供LLM时，初始化是否会引发ValueError。"""
        with pytest.raises(ValueError, match="LLM实例未提供"):
            WorldBuilderAgent(prompt_manager, llm_instance=None)

    def test_initialization_fails_without_template(self, tmp_path: Path):
        """测试: 当模板文件不存在时，初始化是否会引发ValueError。"""
        # 创建一个空的PromptManager，它找不到模板
        empty_manager = PromptManager(base_directory=str(tmp_path))
        # 即使是失败测试，也需要一个mock llm来让初始化代码走到模板检查那一步
        mock_llm = MagicMock()

        with pytest.raises(ValueError, match="无法加载 'world_form' 模板"):
            WorldBuilderAgent(empty_manager, mock_llm)

    @pytest.mark.asyncio
    async def test_process_in_progress(self, prompt_manager: PromptManager):
        """
        测试: process方法在世界构建未完成时的行为。
        LLM返回部分更新和追问，Agent应该更新状态并返回追问。
        """
        # 1. 设置
        # a. 创建一个简单的 mock LLM 仅用于成功初始化 Agent
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = MagicMock()

        # b. 初始化 Agent。此时 agent.chain 是一个我们不关心的真实对象。
        agent = WorldBuilderAgent(prompt_manager, mock_llm)

        # c. 关键步骤：用我们完全控制的 mock 对象替换掉 agent 内部的 chain
        mock_output = WorldBuilderOutput(
            world_state_update=LLMWorldStateUpdate(name="新世界"),
            response_text='好的，世界叫"新世界"。那么它的历史背景是什么？',
            is_complete=False,
        )
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_output)
        agent.chain = mock_chain  # <--- 猴子补丁

        session = GameSession(session_id="test-session-progress")
        user_input = "就叫它新世界吧"

        # 2. 执行
        result = await agent.process({"session": session, "user_input": user_input})

        # 3. 断言
        agent.chain.ainvoke.assert_awaited_once()  # 现在断言会成功
        assert result["response"] == '好的，世界叫"新世界"。那么它的历史背景是什么？'
        assert not result["is_complete"]
        assert session.world_state.name == "新世界"
        assert session.world_state.history is None, "未被更新的字段应保持原样"

    @pytest.mark.asyncio
    async def test_process_completion(self, prompt_manager: PromptManager):
        """
        测试: process方法在世界构建完成时的行为。
        LLM返回最终更新和完成信号，Agent应该更新状态并返回完成信息。
        """
        # 1. 设置
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = MagicMock()
        agent = WorldBuilderAgent(prompt_manager, mock_llm)

        # 替换 agent 内部的 chain
        mock_output = WorldBuilderOutput(
            world_state_update=LLMWorldStateUpdate(history="一段漫长而曲折的历史。"),
            response_text="世界设定完成！准备好开始冒险了吗？",
            is_complete=True,
        )
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_output)
        agent.chain = mock_chain

        # 假设这是第二轮对话，session中已经有部分数据
        session = GameSession(session_id="test-session-completion")
        session.world_state.name = "艾泽拉斯"
        user_input = "它的历史是漫长而曲折的。"

        # 2. 执行
        result = await agent.process({"session": session, "user_input": user_input})

        # 3. 断言
        agent.chain.ainvoke.assert_awaited_once()
        assert result["response"] == "世界设定完成！准备好开始冒险了吗？"
        assert result["is_complete"]
        assert session.world_state.name == "艾泽拉斯", "原始数据应保留"
        assert session.world_state.history == "一段漫长而曲折的历史。"
    
    def test_update_world_state(self, prompt_manager: PromptManager):
        """测试: _update_world_state 方法能否正确更新世界状态。"""
        # 这个测试不需要一个功能齐全的LLM，所以用一个简单的mock来通过初始化
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = MagicMock()
        agent = WorldBuilderAgent(prompt_manager, mock_llm)

        # 创建一个初始的世界状态
        initial_state = WorldState(name="初始世界", history="初始历史")
        initial_state.additional_info["动态字段1"] = "动态值1"
        initial_state.additional_info["动态字段2"] = "动态值2"
        
        # 创建一个LLM的输出
        WorldStateUpdata = LLMWorldStateUpdate(
            name="新世界",
            history="新历史",
            additional_info=[DynamicField(key="动态字段3", value="动态值3")]
        )
        
        # 调用方法进行更新
        agent._update_world_state(initial_state, WorldStateUpdata)
        
        # 断言更新后的状态
        assert initial_state.name == "新世界"
        assert initial_state.history == "新历史"
        assert initial_state.additional_info["动态字段1"] == "动态值1"
        assert initial_state.additional_info["动态字段2"] == "动态值2"
        assert initial_state.additional_info["动态字段3"] == "动态值3"

        # 断言没有被更新的字段保持不变
        assert initial_state.geography is None
        assert initial_state.cultures is None
        assert initial_state.magic_system is None

    def test_format_current_data(self, prompt_manager: PromptManager):
        """测试: _format_current_data 方法能否正确格式化世界状态。"""
        # 这个测试不需要一个功能齐全的LLM，所以用一个简单的mock来通过初始化
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = MagicMock()
        agent = WorldBuilderAgent(prompt_manager, mock_llm)

        # 创建一个初始的世界状态
        initial_state = WorldState(name="初始世界", history="初始历史")
        initial_state.additional_info["动态字段1"] = "动态值1"
        initial_state.additional_info["动态字段2"] = "动态值2"

        # 调用方法进行格式化
        formatted_data = agent._format_current_data(initial_state)

        # 断言格式化后的数据包含所有已设置的字段
        assert "世界名称: 初始世界" in formatted_data
        assert "历史背景: 初始历史" in formatted_data
        assert "动态字段1: 动态值1" in formatted_data
        assert "动态字段2: 动态值2" in formatted_data

        # 断言没有包含未设置的字段
        assert "地理环境" not in formatted_data 
        
