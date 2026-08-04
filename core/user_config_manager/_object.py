from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    field_serializer,
    Field,
)
from ..global_config_manager import ReasoningEffort
from zoneinfo import ZoneInfo, available_timezones
from typing import Any

class UserConfigs(BaseModel):
    """
    Configs for user.
    """
    model_config = ConfigDict(
        validate_assignment=True
    )
    
    # Model Parameters
    model_id: str | list[str] | None = None
    image_model_id: str | list[str] | None = None
    fim_echo: bool | None = None
    seed: int | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_a: float | None = Field(default=None, ge=0.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    top_k: int | None = Field(default=None, ge=1)
    max_tokens: int | None = None
    max_completion_tokens: int | None = None
    stop: list[str] | None = None
    thinking: bool | None = None
    model_timeout: int | float | None = None
    repetition_penalty: float | None = Field(default=None, gt=0.0, le=2.0)
    frequency_penalty: float | None = Field(default=None, ge=-2.0, le=2.0)
    presence_penalty: float | None = Field(default=None, ge=-2.0, le=2.0)
    reasoning_effort: ReasoningEffort | None = None
    send_user_id: bool | None = None
    extra_bodys: dict[str, Any] | None = None

    # Generate Loop
    max_generate_times: int | None = None

    # Render
    render_style: str | None = None
    render_html_template: str | None = None
    render_title: str | None = None
    render_document_bottom_comment: str | None = None

    # Prompt
    load_prompt: bool | None = None
    preset_prompt_name: str | None = None
    prompt_directives: dict[str, list[str]] | None = None

    # Context
    context_shrink_limit: int | None = None
    tool_calling_remove_reasoning: bool | None = None
    remove_reasoning_prompt: bool | None = None
    request_statistics_template: str | None = None
    allowed_tool_calls: set[str] | None = None
    save_context: bool | None = None
    save_new_only: bool | None = None
    save_text_only: bool | None = None
    make_multimodal_message: bool | None = None

    # User Profile
    user_name: str | None = None
    user_profile: str | None = None
    user_age: int | float | None = None
    user_gender: str | None = None
    timezone: float | str | None = None

    # Permission
    cross_user_data_access: bool | None = None

    # Additional User Data
    additional_user_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("timezone")
    def check_timezone(cls, v):
        if isinstance(v, str):
            if v not in available_timezones():
                raise ValueError(f"Invalid time zone {v}")
        elif isinstance(v, ZoneInfo):
            pass
        elif isinstance(v, int) or isinstance(v, float):
            if not -12 <= v <= 14:
                raise ValueError(f"Invalid time offset {v}")
        elif v is None:
            pass
        else:
            raise ValueError("Invalid time offset type")
        return v
    
    @field_serializer("allowed_tool_calls")
    def allowed_tool_calls_serializer(self, value: set[str] | None) -> list[str] | None:
        if value is None:
            return None
        return list(value)