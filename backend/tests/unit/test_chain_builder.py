import pytest
from app.core.chain_builder import ContextManager, ChainBuilder, InjectedChain
from langchain_core.language_models.fake import FakeListLLM as FakeLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from unittest.mock import AsyncMock


class TestContextManager:
    """
    为 ContextManager 编写的单元测试套件。
    """

    def test_set_and_get_context(self):
        """
        测试：能否正确设置和获取上下文。
        """
        manager = ContextManager()
        initial_context = {"player_name": "Alice", "world_name": "Eldoria"}

        manager.set_context(initial_context)
        assert manager.get_context() == initial_context
        assert manager.get_context()["player_name"] == "Alice"

    def test_get_context_returns_copy(self):
        """
        测试：get_context 是否返回上下文的副本，而非引用。
        """
        manager = ContextManager()
        initial_context = {"player_name": "Alice", "world_name": "Eldoria"}

        manager.set_context(initial_context)
        context_copy = manager.get_context()
        context_copy["world_name"] = "Moria"

        assert manager.get_context()["world_name"] == "Eldoria"
        assert context_copy["world_name"] == "Moria"

    def test_clear_context(self):
        """
        测试：能否成功清空上下文。
        """
        manager = ContextManager()
        initial_context = {"player_name": "Alice", "world_name": "Eldoria"}

        manager.set_context(initial_context)
        manager.clear_context()

        assert manager.get_context() == {}


class TestChainBuilder:
    """
    为 ChainBuilder 编写的单元测试套件。
    """

    def test_build_successful(self):
        """
        测试：当所有必需组件都提供时，build() 是否能成功创建 InjectedChain。
        """
        llm = FakeLLM(responses=["AI的固定回复"])
        prompt_template = "问题: {input}"
        builder = ChainBuilder()

        chain = builder.with_prompt_template(prompt_template).with_llm(llm).build()

        # 1. 验证返回的是 InjectedChain 的实例
        assert isinstance(chain, InjectedChain)

        # 2. 验证内部组件是否被正确设置
        assert chain.llm is llm
        assert chain.prompt.template == prompt_template
        assert isinstance(chain.context_manager, ContextManager)

    def test_build_fails_without_llm_or_prompt(self):
        """
        测试：缺少 LLM 或 Prompt 时，build() 是否会按预期抛出 ValueError。
        """
        llm = FakeLLM(responses=["AI的固定回复"])

        with pytest.raises(ValueError):
            ChainBuilder().with_prompt_template("test").build()

        with pytest.raises(ValueError):
            ChainBuilder().with_llm(llm).build()


class TestInjectedChain:
    """
    为 InjectedChain 编写的单元测试套件。
    我们将使用 FakeLLM 来模拟真实的 LLM 行为。
    """

    @pytest.fixture
    def fake_llm(self):
        """一个返回固定响应的模拟LLM."""
        return FakeLLM(responses=["AI的固定回复"])

    @pytest.fixture
    def basic_chain(self, fake_llm):
        """一个基本的、可供测试的 InjectedChain 实例。"""
        return (
            ChainBuilder()
            .with_prompt_template("问题: {input}")
            .with_llm(fake_llm)
            .build()
        )

    @pytest.mark.asyncio
    async def test_step_combines_context_correctly(self, basic_chain):
        """
        测试：step() 方法是否能正确地将所有来源的上下文合并后传递给LLM。
        """
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = AIMessage(content="AI的固定回复")
        basic_chain.chain = mock_chain

        basic_chain.update_context(system_context="is_test")
        external_context = {"external_context": "is_present"}
        user_input = "这是一个问题"

        # 2. 执行 step
        await basic_chain.step(user_input, external_context)

        # 3. 验证 ainvoke 被正确调用，并且参数是我们预期的组合字典
        mock_chain.ainvoke.assert_called_once()
        call_args, _ = mock_chain.ainvoke.call_args
        final_context = call_args[0]

        assert final_context.get("system_context") == "is_test"
        assert final_context.get("external_context") == "is_present"
        assert final_context.get("input") == user_input
        assert "chat_history" in final_context
        # 在第一次调用时，历史记录为空字符串
        assert final_context["chat_history"] == ""

    @pytest.mark.asyncio
    async def test_memory_is_updated_after_step(self, basic_chain):
        """
        测试：执行 step() 后，对话历史是否被正确更新。
        """
        user_input = "你好"
        ai_response_content = "AI的固定回复"

        await basic_chain.step(user_input)

        memory = basic_chain.retrieve_memory()

        assert len(memory) == 2
        assert isinstance(memory[0], HumanMessage)
        assert memory[0].content == user_input
        assert isinstance(memory[1], AIMessage)
        assert memory[1].content == ai_response_content
