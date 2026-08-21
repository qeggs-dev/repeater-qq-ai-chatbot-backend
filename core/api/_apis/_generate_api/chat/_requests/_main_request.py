import uuid
from pydantic import BaseModel, Field
from ......context import ContentRole, ContentUnit
from ......assist_struct import RequestUserInfo, CrossUserDataRouting, AdditionalData
from typing import Any

class ChatRequest(BaseModel):
    message: str | None = ""
    task_id: uuid.UUID | None = None
    suffix: str | None = None
    echo: bool = False
    fim_mode: bool = False
    history_messages: list[ContentUnit] | None = None
    user_info: RequestUserInfo = Field(default_factory=RequestUserInfo)
    role: ContentRole = ContentRole.USER
    assistant_role: ContentRole = ContentRole.ASSISTANT
    history_msg_role_map: dict[ContentRole, ContentRole | None] | None = None
    role_name: str | None = None
    model_id: str | None = None
    thinking: bool | None = None
    load_prompt: bool | None = None
    save_context: bool | None = None
    save_new_only: bool | None = None
    temporary_prompt: str | None = None
    extra_template_fields: dict[str, Any] | None = None
    additional_data: AdditionalData | None = None
    cross_user_data_routing: CrossUserDataRouting[str | None] | None = None
    allowed_tool_calls: set[str] | None = None
    stream: bool = False
    extra_bodys: dict[str, Any] | None = None