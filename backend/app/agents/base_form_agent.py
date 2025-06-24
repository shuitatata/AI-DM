from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from langchain.prompts import PromptTemplate
from pydantic import BaseModel

from app.core.template_manager import PromptManager
from app.models.game_state import GameSession

T_State = TypeVar("T_State", bound=BaseModel)
T_Update = TypeVar("T_Update", bound=BaseModel)
T_Output = TypeVar("T_Output", bound=BaseModel)


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


class FormBasedAgent(BaseAgent, Generic[T_State, T_Update, T_Output], ABC):
    """
    一个通用的、基于表单的Agent基类。
    通过多轮对话收集信息并填充一个Pydantic状态模型。
    """

    def __init__(
        self,
        template_manager: PromptManager,
        llm_instance: Any,
        output_model: Type[T_Output],
    ):
        super().__init__(template_manager)
        self.llm = llm_instance
        self.output_model = output_model
        self._setup_chain()

    def _setup_chain(self):
        """根据子类配置设置Agent的推理链"""
        if not self.llm:
            raise ValueError("LLM实例未提供")

        template_content = self.template_manager.get_template(
            self.get_template_name(), "zh"
        )
        if not template_content:
            raise ValueError(f"无法加载 '{self.get_template_name()}' 模板")

        structured_llm = self.llm.with_structured_output(self.output_model)
        self.chain = (
            PromptTemplate.from_template(template_content) | structured_llm
        ).with_config({"run_name": self.get_agent_name()})

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """通用处理逻辑"""
        session: Optional[GameSession] = input_data.get("session")
        user_input: str = input_data.get("user_input", "")

        if not session:
            raise ValueError("需要提供有效的游戏会话")
        if not self.chain:
            raise ValueError(f"{self.get_agent_name()} 的推理链未初始化")

        target_state = self.get_target_state(session)
        current_data = self._format_current_data(target_state)

        context = self.get_prompt_context(session, current_data, user_input)

        llm_response: T_Output = await self.chain.ainvoke(context)

        self._update_target_state(
            target_state, self.get_update_from_output(llm_response)
        )

        return {
            "response": self.get_response_text_from_output(llm_response),
            "is_complete": self.get_completion_status_from_output(llm_response),
            "updated_state": target_state.model_dump(),
        }

    def _format_current_data(self, target_state: T_State) -> str:
        """格式化当前已收集的数据"""
        data = target_state.model_dump(exclude_defaults=True, exclude_none=True)
        if not data:
            return "暂无数据"

        additional_data = data.pop("additional_info", {})
        field_map = self.get_field_map()

        formatted_data = [
            f"{field_map.get(key, key)}: {value}"
            for key, value in data.items()
            if value
        ]

        if additional_data:
            additional_formatted = [
                f"{key}: {value}" for key, value in additional_data.items()
            ]
            if additional_formatted:
                formatted_data.append("\n动态设定:")
                formatted_data.extend(additional_formatted)

        return "\n".join(formatted_data)

    def get_prompt_context(
        self, session: GameSession, current_data: str, user_input: str
    ) -> Dict[str, Any]:
        """构建并返回传递给Prompt的上下文"""
        return {
            "form_fields": ", ".join(self.get_form_fields()),
            "current_data": current_data,
            "input": user_input,
        }

    # --- 子类必须实现的抽象方法 ---

    @abstractmethod
    def get_agent_name(self) -> str:
        """返回Agent的名称"""
        pass

    @abstractmethod
    def get_template_name(self) -> str:
        """返回Prompt模板的名称"""
        pass

    @abstractmethod
    def get_form_fields(self) -> List[str]:
        """返回需要收集的所有字段列表"""
        pass

    @abstractmethod
    def get_field_map(self) -> Dict[str, str]:
        """返回字段名到其中文描述的映射"""
        pass

    @abstractmethod
    def get_target_state(self, session: GameSession) -> T_State:
        """从会话中获取目标状态对象"""
        pass

    @abstractmethod
    def get_update_from_output(self, output: T_Output) -> T_Update:
        """从LLM的输出中提取状态更新对象"""
        pass

    @abstractmethod
    def get_response_text_from_output(self, output: T_Output) -> str:
        """从LLM的输出中提取要回复给用户的文本"""
        pass

    @abstractmethod
    def get_completion_status_from_output(self, output: T_Output) -> bool:
        """从LLM的输出中提取完成状态"""
        pass

    @abstractmethod
    def _update_target_state(self, current_state: T_State, update: T_Update):
        """根据LLM的输出更新目标状态"""
        pass
