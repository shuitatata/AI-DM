from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.agents.base_form_agent import FormBasedAgent
from app.core.template_manager import PromptManager
from app.models.game_state import (
    CharacterState,
    GameSession,
    LLMCharacterStateUpdate,
    WorldState,
)


class CharacterManagerOutput(BaseModel):
    """LLM为角色构建Agent生成的结构化输出。"""

    character_state_update: LLMCharacterStateUpdate = Field(
        ...,
        description="包含角色状态更新字段的对象。只包含你有新信息的字段，对于未知的字段留空。",
    )
    response_text: str = Field(
        ...,
        description="给用户的回复。如果角色设定不完整，这里应该是一个追问更多细节的问题；如果设定完整，则是一段确认信息。",
    )
    is_complete: bool = Field(
        ...,
        description="布尔标志。如果你认为所有必要的信息都已收集完毕，则设为 true，否则设为 false。",
    )


class CharacterManagerAgent(
    FormBasedAgent[CharacterState, LLMCharacterStateUpdate, CharacterManagerOutput]
):
    """角色管理Agent - 专门负责收集和管理角色信息"""

    def __init__(self, template_manager: PromptManager, llm_instance: Any):
        super().__init__(template_manager, llm_instance, CharacterManagerOutput)

    def get_agent_name(self) -> str:
        return "character_manager"

    def get_template_name(self) -> str:
        return "character_form"

    def get_form_fields(self) -> List[str]:
        """返回需要收集的所有字段列表"""
        # 去掉addtional_info
        return [
            field
            for field in CharacterState.model_fields.keys()
            if field != "additional_info"
        ]

    def get_field_map(self) -> Dict[str, str]:
        # 从get_form_fields中获取字段列表
        fields = self.get_form_fields()
        field_map = {}
        # 与CharacterState中对应字段的description拼接
        for field_name, field_info in CharacterState.model_fields.items():
            if field_name in fields:
                field_map[field_name] = field_info.description
        return field_map

    def get_target_state(self, session: GameSession) -> CharacterState:
        return session.character_state

    def get_update_from_output(
        self, output: CharacterManagerOutput
    ) -> LLMCharacterStateUpdate:
        return output.character_state_update

    def get_response_text_from_output(self, output: CharacterManagerOutput) -> str:
        return output.response_text

    def get_completion_status_from_output(self, output: CharacterManagerOutput) -> bool:
        return output.is_complete

    def get_prompt_context(
        self, session: GameSession, current_data: str, user_input: str
    ) -> Dict[str, Any]:
        """重载此方法以加入世界背景信息"""
        context = super().get_prompt_context(session, current_data, user_input)
        world_data = self._format_world_context(session.world_state)
        context["world_context"] = world_data
        return context

    def _format_world_context(self, world_state: WorldState) -> str:
        """格式化世界设定用于Prompt"""
        data = world_state.model_dump(exclude_defaults=True, exclude_none=True)
        if not data:
            return "暂无世界背景信息"

        # 为了简洁，只展示核心信息
        core_fields = ["name", "geography", "history", "cultures", "magic_system"]
        formatted_data = [
            f"{key}: {value}"
            for key, value in data.items()
            if key in core_fields and value
        ]
        return "\n".join(formatted_data)

    def _update_target_state(
        self, current_state: CharacterState, update: LLMCharacterStateUpdate
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
            "character_creation",
            "character_data_validation",
            "character_state_management",
        ]
