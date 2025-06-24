"""世界构建 Agent - 负责收集和管理世界设定"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from app.core.template_manager import PromptManager
from app.models.game_state import WorldState, GameSession, LLMWorldStateUpdate
from app.agents.base_form_agent import FormBasedAgent


class WorldBuilderOutput(BaseModel):
    """LLM为世界构建Agent生成的结构化输出。"""

    world_state_update: LLMWorldStateUpdate = Field(
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


class WorldBuilderAgent(
    FormBasedAgent[WorldState, LLMWorldStateUpdate, WorldBuilderOutput]
):
    """世界构建Agent - 专门负责收集世界设定信息"""

    def __init__(self, template_manager: PromptManager, llm_instance: Any):
        super().__init__(template_manager, llm_instance, WorldBuilderOutput)

    def get_agent_name(self) -> str:
        return "world_builder"

    def get_template_name(self) -> str:
        return "world_form"

    def get_form_fields(self) -> List[str]:
        return ["name", "geography", "history", "cultures", "magic_system"]

    def get_field_map(self) -> Dict[str, str]:
        return {
            "name": "世界名称",
            "geography": "地理环境",
            "history": "历史背景",
            "cultures": "文化设定",
            "magic_system": "魔法体系",
        }

    def get_target_state(self, session: GameSession) -> WorldState:
        return session.world_state

    def get_update_from_output(self, output: WorldBuilderOutput) -> LLMWorldStateUpdate:
        return output.world_state_update

    def get_response_text_from_output(self, output: WorldBuilderOutput) -> str:
        return output.response_text

    def get_completion_status_from_output(self, output: WorldBuilderOutput) -> bool:
        return output.is_complete

    def _update_target_state(
        self, current_state: WorldState, update: LLMWorldStateUpdate
    ):
        if not update:
            return

        update_dict = update.model_dump(exclude={"additional_info"}, exclude_unset=True)
        for key, value in update_dict.items():
            if value and hasattr(current_state, key):
                setattr(current_state, key, value)

        if update.additional_info:
            for field in update.additional_info:
                if field.key and field.value is not None:
                    current_state.additional_info[field.key] = field.value

    def get_capabilities(self) -> list[str]:
        return [
            "world_setting_collection",
            "world_data_validation",
            "world_state_management",
        ]
