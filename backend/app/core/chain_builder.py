"""Chain Builder - 联邦式Agent架构的核心基础设施"""

import json
import logging
from typing import Optional, Dict, Any, List
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence, Runnable
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


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
        self,
        prompt: PromptTemplate,
        llm: LLM,
        context_manager: Optional[ContextManager] = None,
    ):
        self.prompt = prompt
        self.llm = llm
        self.chain = prompt | llm  # 使用新的 Runnable 语法
        self.context_manager = context_manager or ContextManager()
        self.chat_history: List[BaseMessage] = []  # 手动管理对话历史

    def update_context(self, **kwargs):
        """更新上下文"""
        self.context_manager.set_context(kwargs)

    def inject_prompt(self, injected_prompt: str):
        """动态注入新的prompt模板"""
        logging.debug(f"注入新的Prompt: {injected_prompt}")
        self.prompt = PromptTemplate.from_template(injected_prompt)
        self.chain = self.prompt | self.llm  # 重新构建链

    def retrieve_memory(self, as_string: bool = False):
        """获取对话记忆"""
        if as_string:
            formatted_memory = []
            for msg in self.chat_history:
                if isinstance(msg, HumanMessage):
                    formatted_memory.append(f"User: {msg.content}")
                elif isinstance(msg, AIMessage):
                    formatted_memory.append(f"AI: {msg.content}")
            return "\n".join(formatted_memory)

        return self.chat_history

    def add_to_memory(self, user_input: str, ai_response: str):
        """添加对话到记忆中"""
        self.chat_history.append(HumanMessage(content=user_input))
        self.chat_history.append(AIMessage(content=ai_response))

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

        # 添加对话历史到上下文
        combined_context["chat_history"] = self.retrieve_memory(as_string=True)

        # 添加用户输入
        if user_input:
            combined_context["input"] = user_input

        # 调用链
        try:
            response = await self.chain.ainvoke(combined_context)

            # 提取响应内容（处理AIMessage对象）
            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            # 如果有用户输入，保存到记忆中
            if user_input:
                self.add_to_memory(user_input, response_text)

            return response_text
        except Exception as e:
            logging.error(f"链执行失败: {e}")
            raise


class ChainBuilder:
    """链构建器 - 使用构建器模式创建可复用的LLM调用链"""

    def __init__(self):
        self.prompt: Optional[PromptTemplate] = None
        self.llm: Optional[LLM] = None
        self.context_manager: Optional[ContextManager] = None

    def with_prompt_template(self, prompt_template: str):
        """设置Prompt模板"""
        self.prompt = PromptTemplate.from_template(prompt_template)
        return self

    def with_llm(self, llm_instance: LLM):
        """设置LLM实例"""
        self.llm = llm_instance
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
        if not self.context_manager:
            self.context_manager = ContextManager()

        # 创建现代化的链
        return InjectedChain(self.prompt, self.llm, self.context_manager)

    def from_config(self, config: Dict[str, Any]) -> "ChainBuilder":
        """从配置字典创建构建器"""
        if "prompt_template" in config:
            self.with_prompt_template(config["prompt_template"])

        # 这里可以扩展更多配置选项
        return self
