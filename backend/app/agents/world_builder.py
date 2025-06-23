"""世界构建 Agent - 负责收集和管理世界设定"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from backend.app.core.chain_builder import ChainBuilder, ContextManager
from backend.app.core.template_manager import PromptManager
from backend.app.models.game_state import WorldState, GameSession
import json
import re


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

    def __init__(self, template_manager: PromptManager, llm_instance=None):
        super().__init__(template_manager)
        self.llm = llm_instance
        self._setup_chain()

    def _setup_chain(self):
        """设置Agent的推理链"""
        if not self.llm:
            # 这里暂时不设置LLM，等后续配置
            return

        template = self.template_manager.get_template("world_form", "zh")
        if template:
            self.chain = (
                ChainBuilder()
                .with_prompt_template(template)
                .with_llm(self.llm)
                .with_context_manager(ContextManager())
                .build()
            )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理世界设定收集请求"""
        session: GameSession = input_data.get("session")
        user_input: str = input_data.get("user_input", "")

        if not session:
            raise ValueError("需要提供有效的游戏会话")

        # 获取当前世界状态
        current_world = session.world_state

        # 准备上下文
        form_fields = "name, geography, history, cultures, magic_system"
        current_data = self._format_current_data(current_world)

        if not self.chain:
            # 如果没有LLM链，返回静态响应
            return {
                "response": f"收到世界设定输入: {user_input}。请配置LLM后重试。",
                "is_complete": False,
                "updated_state": current_world.dict(),
            }

        # 更新链的上下文
        self.chain.update_context(form_fields=form_fields, current_data=current_data)

        # 执行推理
        response = await self.chain.step(user_input)

        # 尝试提取JSON数据
        updated_world_data = self._extract_json_from_response(response)
        if updated_world_data:
            # 更新世界状态
            for key, value in updated_world_data.items():
                if hasattr(current_world, key) and value:
                    setattr(current_world, key, value)

        # 检查是否完成
        is_complete = session.is_world_complete()

        return {
            "response": response,
            "is_complete": is_complete,
            "updated_state": current_world.dict(),
        }

    def _format_current_data(self, world_state: WorldState) -> str:
        """格式化当前已收集的数据"""
        data = []
        if world_state.name:
            data.append(f"世界名称: {world_state.name}")
        if world_state.geography:
            data.append(f"地理环境: {world_state.geography}")
        if world_state.history:
            data.append(f"历史背景: {world_state.history}")
        if world_state.cultures:
            data.append(f"文化设定: {world_state.cultures}")
        if world_state.magic_system:
            data.append(f"魔法体系: {world_state.magic_system}")

        return "\n".join(data) if data else "暂无数据"

    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """从响应中提取JSON数据"""
        try:
            # 尝试寻找JSON块
            json_pattern = r"\{[^{}]*\}"
            matches = re.findall(json_pattern, response, re.DOTALL)

            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict):
                        return data
                except json.JSONDecodeError:
                    continue

            return None
        except Exception:
            return None

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

    def is_complete(self, world_state: WorldState) -> bool:
        """检查世界设定是否完整"""
        return all(
            [
                world_state.name,
                world_state.geography,
                world_state.history,
                world_state.cultures,
                world_state.magic_system,
            ]
        )
