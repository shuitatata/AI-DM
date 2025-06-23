"""世界构建 Agent - 负责收集和管理世界设定"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from app.core.template_manager import PromptManager
from app.models.game_state import WorldState, GameSession
import json
import re


class WorldBuilderOutput(BaseModel):
    """LLM为世界构建Agent生成的结构化输出。"""

    world_state_update: WorldState = Field(
        ...,
        description="包含游戏世界状态更新字段的对象。只包含你有新信息的字段，对于未知的字段留空。",
    )
    response_text: str = Field(
        ...,
        description="给用户的回复。如果世界设定不完整，这里应该是一个追问更多细节的问题；如果设定完整，则是一段确认信息。",
    )
    is_complete: bool = Field(
        ...,
        description="布尔标志。如果你认为所有必要的世界信息都已收集完毕，则设为 true，否则设为 false。",
    )


class BaseAgent(ABC):
    """Agent基类 - 定义所有Agent的通用接口"""

    def __init__(self, template_manager: PromptManager):
        self.template_manager = template_manager
        self.chain = None

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入并返回结果"""
        pass

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """返回Agent能力列表"""
        pass


class WorldBuilderAgent(BaseAgent):
    """世界构建Agent - 专门负责收集世界设定信息"""

    def __init__(self, template_manager: PromptManager, llm_instance):
        super().__init__(template_manager)
        self.llm = llm_instance
        self._setup_chain()

    def _setup_chain(self):
        """设置Agent的推理链"""
        if not self.llm:
            raise ValueError("LLM实例未提供")

        template_content = self.template_manager.get_template("world_form", "zh")
        if not template_content:
            raise ValueError(f"无法加载 'world_form' 模板，请确保模板文件存在于{self.template_manager.base_directory}")

        # LLM被配置为输出我们定义的新WorldBuilderOutput模型
        structured_llm = self.llm.with_structured_output(WorldBuilderOutput)
        self.chain = PromptTemplate.from_template(template_content) | structured_llm

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """通过多轮对话处理世界设定收集请求。"""
        session: Optional[GameSession] = input_data.get("session")
        user_input: str = input_data.get("user_input", "")

        if not session:
            raise ValueError("需要提供有效的游戏会话")

        if not self.chain:
            raise ValueError("WorldBuilderAgent的推理链未初始化")

        # 获取当前世界状态并格式化以用于Prompt
        current_world = session.world_state
        current_data = self._format_current_data(current_world)

        # 准备传递给链的上下文
        context = {
            "form_fields": ", ".join(self.get_form_fields()),
            "current_data": current_data,
            "input": user_input,
        }

        # 核心步骤：调用链进行推理。返回值是WorldBuilderOutput对象
        llm_response: WorldBuilderOutput = await self.chain.ainvoke(context)

        # 使用LLM返回的数据更新当前的世界状态
        if llm_response.world_state_update:
            # model_dump(exclude_unset=True)只会包含LLM实际提供值的字段
            update_dict = llm_response.world_state_update.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                if value and hasattr(current_world, key):
                    setattr(current_world, key, value)

        # 回复和完成状态现在直接来自LLM的结构化输出
        return {
            "response": llm_response.response_text,
            "is_complete": llm_response.is_complete,
            "updated_state": current_world.model_dump(),
        }

    def _format_current_data(self, world_state: WorldState) -> str:
        """格式化当前已收集的数据"""
        # 使用model_dump可以更优雅地处理所有已设置的字段
        data = world_state.model_dump(exclude_defaults=True, exclude_none=True)
        if not data:
            return "暂无数据"

        field_map = {
            "name": "世界名称",
            "geography": "地理环境",
            "history": "历史背景",
            "cultures": "文化设定",
            "magic_system": "魔法体系",
        }
        formatted_data = [
            f"{field_map.get(key, key)}: {value}" for key, value in data.items()
        ]
        return "\n".join(formatted_data)

    def get_capabilities(self) -> list[str]:
        """返回世界构建Agent的能力"""
        return [
            "world_setting_collection",
            "world_data_validation",
            "world_state_management",
        ]

    def get_form_fields(self) -> list[str]:
        """获取世界设定需要收集的字段"""
        return ["name", "geography", "history", "cultures", "magic_system"]

