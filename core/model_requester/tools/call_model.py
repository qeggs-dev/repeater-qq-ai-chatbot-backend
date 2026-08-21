from typing import Any
from ...call_api.completions_api import (
    Request,
    Runtime,
    StreamOptions
)
from ...context import ToolCallPacakage, CallMode, Context, ContentRole
from ...global_config_manager import ReasoningEffort
from ...data_manager import PromptManager
from .._caller import ModelRequester
from ...runtime_container import RuntimeContainer
from ...text_buffer import ContentBuffer, TextBuffer
from ...clients.model_info import ModelInfo, SafeModelInfo
from pydantic import BaseModel, Field
from enum import StrEnum

class OutputFormat(StrEnum):
    TEXT = "text"
    JSON = "json"
    CONTENT_ONLY = "content_only"
    REASONING_ONLY = "reasoning_only"
    NEW_CONTENT_ONLY = "new_content_only"
    NEW_REASONING_ONLY = "new_reasoning_only"

@ModelRequester.reg_global_package
class CallModel(ToolCallPacakage):
    prompt_manager: PromptManager = PromptManager()
    name = "call_model"
    document = "Send a request to an llm and get the generated results."
    call_mode = CallMode.ASYNC
    
    class Params(BaseModel):
        model_id: str = Field(
            "", 
            description="Unique identifier used to locate and load the target model."
        )
        user_name: str = Field(
            "", 
            description="Name of the user making the request, used for logging and personalization."
        )
        temperature: float = Field(
            1.0, 
            ge=0.0, 
            le=2.0, 
            description="Controls randomness in output. Lower values (e.g., 0.2) make output more deterministic; higher values (e.g., 1.5) increase diversity. Must be between 0 and 2."
        )
        top_p: float = Field(
            1.0, 
            ge=0.0, 
            le=1.0, 
            description="Nucleus sampling threshold. The model considers only the smallest set of tokens whose cumulative probability >= top_p. Must be between 0 and 1."
        )
        presence_penalty: float = Field(
            0.0, 
            ge=-2.0, 
            le=2.0, 
            description="Penalizes tokens that have appeared at all in the text so far, encouraging the model to talk about new topics. Positive values discourage repetition. Range: -2.0 to 2.0."
        )
        frequency_penalty: float = Field(
            0.0, 
            ge=-2.0, 
            le=2.0, 
            description="Penalizes tokens proportionally to how often they have appeared, reducing verbatim repetition. Positive values discourage frequent tokens. Range: -2.0 to 2.0."
        )
        max_tokens: int = Field(
            4096, 
            gt=0, 
            description="The maximum number of tokens the model can generate in the response."
        )
        max_completion_tokens: int = Field(
            4096, 
            gt=0, 
            description="Alias for max_tokens. The maximum number of tokens allowed in the completion output."
        )
        thinking: bool | None = Field(
            None, 
            description="When enabled, the model allocates tokens for internal reasoning before producing the final answer. Useful for complex, multi-step problems."
        )
        stop: list[str] | None = Field(
            None, 
            description="List of strings where the model stops generating further tokens when encountered."
        )
        context: Context | None = Field(
            None, 
            description="Predefined conversation history or system context to guide the model's behavior."
        )
        reasoning_effort: ReasoningEffort | None = Field(
            None, 
            description="Controls how many tokens the model spends on internal reasoning (e.g., 'low', 'medium', 'high')."
        )
        remove_reasoning_prompt: bool = Field(
            False, 
            description="If True, strips the internal reasoning prompt from the output, returning only the final answer."
        )
        output_role: ContentRole = Field(
            ContentRole.ASSISTANT, 
            description="Role assigned to the generated content in the conversation structure (e.g., 'assistant')."
        )
        timeout: int | float | None = Field(
            None, 
            gt=0, 
            description="Maximum time in seconds to wait for a response before the request is cancelled."
        )
        output_format: OutputFormat = Field(
            OutputFormat.TEXT, 
            description="Format of the output data returned by the API (e.g., 'text')."
        )
        extra_bodys: dict[str, Any] = Field(
            default_factory=dict, 
            description="Additional parameters to pass to the API call."
        )
    
    class Result(BaseModel):
        model: SafeModelInfo = Field(description="The model used for the API call.")
        context: Context = Field(description="The context used for the API call.")
    
    @staticmethod
    def response_parser(
        model: ModelInfo,
        context: Context,
        include_reasoning: bool = True,
        include_content: bool = True,
    ):
        for index, content in enumerate(context):
            yield f"<content index: \"{index}\" role: \"{content.role}\" model: \"{model.name}\">"
            if include_reasoning and content.reasoning_content:
                yield "<think>"
                yield content.reasoning_content
                yield "</think>"
            if include_content and content.content:
                yield content.content_to_string()
            yield "</content>"

    async def call(self, args: Params):
        runtime = RuntimeContainer.get_runtime()
        
        model = await runtime.model_info_client.get_random_model(
            model_id = args.model_id
        )
        
        if self.user_configs.send_user_id is not None:
            send_user_id = self.user_configs.send_user_id
        else:
            send_user_id = self.global_configs.callapi.send_user_id
        
        if model.api_key is None:
            raise Exception("Model api key is not set")

        extra_bodys: dict[str, Any] = {}
        if self.global_configs.model.enable_user_extra_bodys:
            extra_bodys.update(args.extra_bodys)
        if self.global_configs.model.extra_bodys is not None:
            extra_bodys.update(self.global_configs.model.extra_bodys)
        if self.global_configs.model.enable_user_extra_bodys and self.user_configs.extra_bodys is not None:
            extra_bodys.update(self.user_configs.extra_bodys)
        if self.global_configs.model.extra_bodys_priority is not None:
            extra_bodys.update(self.global_configs.model.extra_bodys_priority)

        request = Request(
            url = model.get_base_url(),
            limits = model.limits,
            key = model.api_key,
            timeout = args.timeout if args.timeout is not None else model.timeout,
            model = model.id,
            model_id = args.model_id,
            model_uid = model.uid,
            user_name = args.user_name,
            temperature = args.temperature,
            top_p = args.top_p,
            presence_penalty = args.presence_penalty,
            frequency_penalty = args.frequency_penalty,
            max_tokens = args.max_tokens,
            max_completion_tokens = args.max_completion_tokens,
            thinking = args.thinking,
            stop = args.stop,
            context = args.context,
            reasoning_effort = args.reasoning_effort,
            remove_reasoning_prompt = args.remove_reasoning_prompt,
            remove_created = True,
            send_user_id = send_user_id,
            stream = self.global_configs.model.stream,
            stream_options = StreamOptions(
                include_obfuscation = self.global_configs.callapi.include_obfuscation,
                include_usage = self.global_configs.callapi.include_usage
            ),
            extra_bodys = extra_bodys,
        )
        
        request_runtime = Runtime(
            client_pool = runtime.openai_pool,
            content_buffer = ContentBuffer()
        )
        requestser = ModelRequester(
            user_id = self.user_id,
            user_configs = self.user_configs,
            global_configs = self.global_configs,
            model_info_client = runtime.model_info_client,
            max_concurrency = self.global_configs.callapi.max_concurrency
        )

        responses = await requestser.submit(
            user_id = self.user_id,
            request = request,
            runtime = request_runtime,
            available_tool_calls = None,
            stream = False
        )

        context = responses.new_contexts()
        match args.output_format:
            case OutputFormat.TEXT:
                buffer = TextBuffer(separator = "\n")
                buffer.consume_iterable_no_conversion(
                    self.response_parser(
                        model,
                        context
                    )
                )
                return str(buffer)
            case OutputFormat.JSON:
                return self.Result(
                    model = model.to_safe(),
                    context = context,
                )
            case OutputFormat.CONTENT_ONLY:
                buffer = TextBuffer(separator = "\n")
                buffer.consume_iterable_no_conversion(
                    self.response_parser(
                        model,
                        context,
                        include_content = True,
                        include_reasoning = False,
                    )
                )
                return str(buffer)
            case OutputFormat.REASONING_ONLY:
                buffer = TextBuffer(separator = "\n")
                buffer.consume_iterable_no_conversion(
                    self.response_parser(
                        model,
                        context,
                        include_content = False,
                        include_reasoning = True,
                    )
                )
                return str(buffer)
            case OutputFormat.NEW_CONTENT_ONLY:
                last_content = context.last_content
                if last_content is None:
                    return ""
                return last_content.content_to_string()
            case OutputFormat.NEW_REASONING_ONLY:
                last_content = context.last_content
                if last_content is None:
                    return ""
                return last_content.reasoning_content