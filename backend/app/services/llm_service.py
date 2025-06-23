"""LLM服务管理模块"""

import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_community.llms.fake import FakeListLLM
from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务管理器"""

    def __init__(self):
        self.settings = get_settings()
        self._llm_instance: Optional[object] = None
        self._setup_llm()

    def _setup_llm(self):
        """设置LLM实例"""
        # 检查API密钥是否有效（不是默认值）
        if (
            self.settings.openai_api_key
            and self.settings.openai_api_key != "your_openai_api_key_here"
        ):
            try:
                self._llm_instance = ChatOpenAI(
                    api_key=self.settings.openai_api_key,
                    model_name=self.settings.openai_model_name,
                    temperature=self.settings.openai_temperature,
                )
                logger.info(f"已配置OpenAI LLM: {self.settings.openai_model_name}")
            except Exception as e:
                logger.error(f"配置OpenAI LLM失败: {e}")
                self._setup_mock_llm()
        else:
            logger.warning("未配置有效的OpenAI API密钥，使用模拟LLM")
            self._setup_mock_llm()

    def _setup_mock_llm(self):
        """设置模拟LLM用于演示"""
        mock_responses = [
            "太棒了！你想要创造一个魔法世界。让我们先从给这个世界起个名字开始吧。你希望这个魔法世界叫什么名字呢？",
            "艾尔多拉德，多么美妙的名字！现在让我们来描述一下这个世界的地理环境。艾尔多拉德是一个怎样的地方？有山脉、森林、海洋，还是浮空岛屿？",
            "浮空岛屿的设定非常有趣！现在我们来聊聊艾尔多拉德的历史背景。这个浮空世界是如何形成的？有什么重大的历史事件吗？",
            "古老的魔法大战听起来很史诗！接下来让我们了解一下这个世界的文化设定。不同的浮空岛屿上居住着什么样的民族或种族？他们有什么独特的文化特色？",
            '最后，让我们来设计这个世界的魔法体系。在艾尔多拉德，魔法是如何运作的？是元素魔法、符文魔法，还是其他体系？\n\n恭喜！世界设定已经完成：\n{"name": "艾尔多拉德", "geography": "浮空岛屿组成的魔法世界", "history": "古老魔法大战的结果", "cultures": "多元素民族共存", "magic_system": "元素与符文结合的魔法体系"}',
        ]

        self._llm_instance = FakeListLLM(responses=mock_responses)
        logger.info("已配置模拟LLM用于演示")

    def get_llm(self):
        """获取LLM实例"""
        return self._llm_instance

    def is_real_llm(self) -> bool:
        """检查是否为真实LLM"""
        return (
            self.settings.openai_api_key is not None
            and self.settings.openai_api_key != "your_openai_api_key_here"
            and not isinstance(self._llm_instance, FakeListLLM)
        )


# 全局LLM服务实例
llm_service = LLMService()
