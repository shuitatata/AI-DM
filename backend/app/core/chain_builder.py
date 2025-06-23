"""Chain Builder - 联邦式Agent架构的核心基础设施"""

import json
import logging
from typing import Optional, Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, AIMessage


class ContextManager:
    """上下文管理器 - 管理Agent之间共享的上下文信息"""

    def __init__(self):
        self._context: Dict[str, Any] = {}

    def set_context(self, context: Dict[str, Any]):
        """设置上下文"""
        self._context.update(context)

    def get_context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        return self._context.copy()

    def clear_context(self):
        """清空上下文"""
        self._context.clear()


class InjectedChain:
    """包装的LLM链 - 支持上下文注入和动态模板"""

    def __init__(
        self, chain: LLMChain, context_manager: Optional[ContextManager] = None
    ):
        self.chain = chain
        self.context_manager = context_manager or ContextManager()

    def update_context(self, **kwargs):
        """更新上下文"""
        self.context_manager.set_context(kwargs)

    def inject_prompt(self, injected_prompt: str):
        """动态注入新的prompt模板"""
        logging.debug(f"注入新的Prompt: {injected_prompt}")
        self.chain.prompt.template = injected_prompt

    def retrieve_memory(self, as_string: bool = False):
        """获取对话记忆"""
        try:
            memory = self.chain.memory.chat_memory.messages
        except Exception:
            logging.warning("获取记忆失败")
            return []

        if as_string:
            formatted_memory = []
            for msg in memory:
                if isinstance(msg, HumanMessage):
                    formatted_memory.append(f"User: {msg.content}")
                elif isinstance(msg, AIMessage):
                    formatted_memory.append(f"AI: {msg.content}")
            return "\n".join(formatted_memory)

        return memory

    async def step(
        self,
        user_input: Optional[str] = None,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """执行一步推理"""
        if external_context is None:
            external_context = {}

        # 合并上下文
        combined_context = {**self.context_manager.get_context(), **external_context}

        # 根据是否有用户输入决定调用方式
        if not user_input:
            return await self.chain.arun(**combined_context)
        return await self.chain.arun(input=user_input, **combined_context)

    def __getattr__(self, attr):
        """代理访问底层chain的属性"""
        return getattr(self.chain, attr)


class ChainBuilder:
    """链构建器 - 使用构建器模式创建可复用的LLM调用链"""

    def __init__(self):
        self.prompt: Optional[PromptTemplate] = None
        self.llm: Optional[LLM] = None
        self.memory: Optional[ConversationBufferMemory] = None
        self.context_manager: Optional[ContextManager] = None

    def with_prompt_template(self, prompt_template: str):
        """设置Prompt模板"""
        self.prompt = PromptTemplate.from_template(prompt_template)
        return self

    def with_llm(self, llm_instance: LLM):
        """设置LLM实例"""
        self.llm = llm_instance
        return self

    def with_memory(self, memory_instance: ConversationBufferMemory):
        """设置记忆组件"""
        self.memory = memory_instance
        return self

    def with_context_manager(self, context_manager: ContextManager):
        """设置上下文管理器"""
        self.context_manager = context_manager
        return self

    def build(self) -> InjectedChain:
        """构建最终的链"""
        if not self.prompt or not self.llm:
            raise ValueError("Prompt和LLM都必须设置才能构建链")

        # 设置默认组件
        if not self.memory:
            self.memory = ConversationBufferMemory(
                input_key="input", memory_key="chat_history"
            )

        if not self.context_manager:
            self.context_manager = ContextManager()

        # 创建LLM链
        llm_chain = LLMChain(llm=self.llm, prompt=self.prompt, memory=self.memory)

        return InjectedChain(llm_chain, self.context_manager)

    def from_config(self, config: Dict[str, Any]) -> "ChainBuilder":
        """从配置字典创建构建器"""
        if "prompt_template" in config:
            self.with_prompt_template(config["prompt_template"])

        # 这里可以扩展更多配置选项
        return self
