from enum import StrEnum

class SupportedParameters(StrEnum):
    # === 基础核心参数 ===
    MODEL = "model"
    MESSAGES = "messages"
    STREAM = "stream"
    N = "n"
    USER = "user"
    SERVICE_TIER = "service_tier"

    # === 输出长度控制 ===
    MAX_TOKENS = "max_tokens"
    MAX_COMPLETION_TOKENS = "max_completion_tokens"

    # === 采样与随机性控制 ===
    TEMPERATURE = "temperature"
    TOP_P = "top_p"
    TOP_A = "top_a"
    TOP_K = "top_k"
    MIN_P = "min_p"
    SEED = "seed"

    # === 惩罚机制 ===
    FREQUENCY_PENALTY = "frequency_penalty"
    PRESENCE_PENALTY = "presence_penalty"
    REPETITION_PENALTY = "repetition_penalty"

    # === 停止与日志概率 ===
    STOP = "stop"
    LOGPROBS = "logprobs"
    TOP_LOGPROBS = "top_logprobs"

    # === 工具 / 函数调用 ===
    TOOLS = "tools"
    TOOL_CHOICE = "tool_choice"
    PARALLEL_TOOL_CALLS = "parallel_tool_calls"

    # === 结构化输出 ===
    RESPONSE_FORMAT = "response_format"
    STRUCTURED_OUTPUTS = "structured_outputs"

    # === 推理相关（Reasoning Models）===
    REASONING = "reasoning"
    REASONING_EFFORT = "reasoning_effort"
    INCLUDE_REASONING = "include_reasoning"

    # === 其他常见参数 ===
    VERBOSITY = "verbosity"
    LOGIT_BIAS = "logit_bias"
    WEB_SEARCH_OPTIONS = "web_search_options"

    # === 附加其他常见 ===
    PROMPT = "prompt"
    DURATION = "duration"
    RESOLUTION = "resolution"
    ASPECT_RATIO = "aspect_ratio"
    SIZE = "size"
    GENERATE_AUDIO = "generate_audio"
    FRAME_IMAGES = "frame_images"
    INPUT_REFERENCES = "input_references"
    CALLBACK_URL = "callback_url"
    PROVIDER = "provider"