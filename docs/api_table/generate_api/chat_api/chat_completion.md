# Chat API

负责与 AI 进行对话
服务器会自动管理对话状态文件

- **`/generate/chat/completion/{user_id:str}`**
  - **Requset**
    - **method:** `POST`
    - **type:** `JSON`
    - **Content:**
      - `message` (str | null): 用户发送的消息，允许为空，但这时模型的行为可能是未定义的
      - `task_id` (str | null): 任务 ID，如果客户端需要管理任务，可以由客户端生成，否则服务端自行生成
      - `suffix` (str | null): 消息后缀，需要保证 `fim_mode` = `true` 才可使用，允许为空
      - `echo` (bool): 是否回显用户消息，默认为 True，需要 `fim_mode` = `true` 才可使用
      - `fim_mode` (bool): 是否使用 FIM 模式，默认为 False
      - `history_messages` (list[dict]): 历史消息，如果填写则使用此处提供的上下文，否则使用用户保存的，格式为 `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`
      - `user_info` 用户信息，全部可选
        - `username` (str): 用户名
        - `nickname` (str): 昵称
        - `age` (int | float): 年龄
        - `gender` (str): 性别
      - `role` (str): 用户角色，可选值：`user`、`assistant`、`system`，默认为 `user`
      - `assistant_role` (str): 机器人角色，可选值：`user`、`assistant`、`system`，默认为 `assistant`
      - `history_msg_role_map` (dict[str, str | null]): 历史消息角色映射，用于临时按角色批量转换上下文角色，格式为 `{"raw_role": "new_role"}`，比如 `{"user": "assistant", "assistant": "user", "system": null}` 表示反转用户与AI并移除 `system` 消息，建议配合 `save_context` = `false` 使用
      - `role_name` (str): 用户角色名称，用于模型区分相同上下文里相同用户角色的不同的用户
      - `allowed_tool_calls` (list[str]): 允许调用的工具列表，格式为 `["tool_name"]`
      - `extra_template_fields` (dict[str, Any]): 额外模板字段，用于在模板中填充额外字段，格式为 `{"key": "value"}`
      - `temporary_prompt` (str): 临时Prompt，临时指定一个Prompt，覆盖配置系统中的Prompt进行生成
      - `model_id` (str): 模型UID，用于临时指定一个模型对话，如果不填则根据配置系统推断值
      - `thinking` (str): 思考模式，部分模型可以用于开启或关闭思考模式
      - `load_prompt` (bool): 是否加载Prompt，如果不填则根据配置系统推断值
      - `save_context` (bool): 是否在完成后保存上下文，如果不填则根据配置系统推断值
      - `save_new_only` (bool): 是否仅保存本次生成的上下文，而丢弃所有历史记录
      - `additional_data`
        - `image_url` (str | list[str]): 图片URL，用于视觉输入，支持单张或多张图片，需要保证内容**长期有效**或在配置中默认移除这些内容 ，以及确保不会因为内容过期而出现上下文不可用的情况
        - `audio_url` (str | list[str]): 音频URL，用于听觉输入，支持单条或多条音频，需要保证内容**长期有效**或在配置中默认移除这些内容 ，以及确保不会因为内容过期而出现上下文不可用的情况
        - `video_url` (str | list[str]): 视频URL，用于视频输入，支持单个或多个视频，需要保证内容**长期有效**或在配置中默认移除这些内容 ，以及确保不会因为内容过期而出现上下文不可用的情况
        - `file_url` (str | list[str]): 文件URL，用于文件输入，支持单个或多个文件，需要保证内容**长期有效**或在配置中默认移除这些内容 ，以及确保不会因为内容过期而出现上下文不可用的情况
      - `cross_user_data_routing`
        - `context`
          - `load_from_user_id` (str): 从指定用户ID加载上下文数据
          - `save_to_user_id` (str): 将上下文数据保存到指定用户ID
        - `prompt`
          - `load_from_user_id` (str): 从指定用户ID加载Prompt数据
          - `save_to_user_id` (str): 将Prompt数据保存到指定用户ID
        - `config`
          - `load_from_user_id` (str): 从指定用户ID加载配置数据
          - `save_to_user_id` (str): 将配置数据保存到指定用户ID
      - `stream` (bool): 是否流式返回（设置该值为 `true` 需要保证在配置中启用了流式处理器，否则会返回`503`错误码）
      - `extra_bodys` (dict[str, Any]): 额外参数，用于传递给模型，具体参数根据模型定义，需保证启用 `model.enable_user_extra_bodys` 才能生效
  - **Response**
    - **type:** `JSON` | `JSONL STREAM`
    - **Content:**
      - `JSON`:
        - `context`
          - `context_list` (list[ContentUnit]): 上下文列表，包含所有新生成的上下文内容
        - `user_raw_input` (str): 用户发送的原始消息
        - `user_input` (str | list[ContentBlock]): 用户发送的消息经过格式化后处理后的内容，使用[OpenAI Chat Completion User Message Content](https://platform.openai.com/docs/api-reference/chat/create#chat_create-messages-user_message-content)格式
        - `model_group` (str): 模型组，由[API_Info文件](../configs/api_info.md)决定
        - `model_name` (str): 模型名称，通常是该模型的可读名称
        - `model_uid` (str): 模型唯一标识，用于锁定当前请求使用的模型
        - `create_time` (int): 提交请求到API时API厂商报告的请求创建时间戳
        - `id` (str): 请求ID，通常是一个随机的字符串，由API厂商生成，通常可以被作为唯一标识使用
        - `finish_reason_code` (str): 模型结束生成的原因，由API厂商提供
        - `finish_reason_cause` (str): 模型结束生成的原因，该字段为可读版本，由程序自动生成
        - `request_log` (RequestLogObject): [Request Log Object](./../request_log/request_log_object.md)
        - `request_statistics` (str): 请求统计信息，由程序自动生成
        - `status` (int): 状态码，这里和http状态码一致，只是为了报告而写，通常应该优先选择检查 http 报告的状态码而不是这个字段
      - `JSON STREAM`:
        - *\*每一行*
          - **Delta**:
            - `id` (str): 请求ID
            - `reasoning_content` (str): CoT回复内容，即使模型没有返回CoT它仍然存在，注意判断逻辑应为非null和非空字符串
            - `content` (str): AI回复内容
            - `function_id` (str): 函数ID，如果模型没有返回函数ID，则该字段为空字符串
            - `function_type` (str): 函数类型，如果模型没有返回函数ID，则该字段为空字符串
            - `function_name` (str): 函数名称，如果模型没有返回函数ID，则该字段为空字符串
            - `function_arguments` (str): 函数参数，通常是JSON格式，如果模型没有返回函数ID，则该字段为空字符串
            - `token_usage`
              - `prompt_tokens` (int): 输入的token数量
              - `completion_tokens` (int): 输出的token数量
              - `total_tokens` (int): 总的token数量
              - `prompt_cache_hit_tokens` (int): 输入的token中缓存命中的数量
              - `prompt_cache_miss_tokens` (int): 输入的token中缓存未命中的数量
            - `finish_reason` (str): 模型结束生成的原因，由API厂商提供
            - `created` (int): 请求创建时间，时间戳，单位为秒
            - `model` (str): 模型名称
            - `system_fingerprint` (str): 系统指纹，由API厂商提供
            - `logprobs`
              - `token` (str): token内容
              - `logprob` (float): token的概率
              - `top_logprobs`
                - `token` (str): token内容
                - `logprob` (float): token的概率
          - **ContentUnit**:
            - *\*ContentUnit* (ContentUnit): 请求内容单元 (通常是 Tool 的响应)

注：该API有**RUL(Request User Lock)**
在 `user_id` 相同且上一个请求**未完成**时
该API将会**堵塞**后来的请求
直到该用户的上一个请求完成
这保证了用户在频繁发起请求时数据的线性处理
`user_id` 不同时RUL不会阻碍它们并行处理
当 `save_context` 为 `false` 时，RUL 不会生效

在请求时，Repeater 并不会立刻保存当前用户的输入
而是先放在内存中，并在生成完全结束后与生成的部分一起保存
这有效避免了在出现异常导致流程中断时
本地上下文不会因此而多出来一个 `user` 消息

请求预处理大概持续 `80ms ~ 150ms` 左右

`logprobs` 参数目前并没有数据内容
它只是在占位

你可以在 `message` 中编写模板
参考 [模板展开器](./../template_engine/main.md)
同时模型返回的数据也会被模板展开器处理并保存下来
(仅限非流式输出，流式输出时客户端无法收到展开的数据
但是它们仍然会在保存时展开一次，以确保数据正确)

当你在提供 `history_messages` 数据时
建议设置 `save_context` 为 `false`
否则临时上下文可能会覆盖你的数据

设置 `history_msg_role_map` 时
如果不设置 `save_context` 为 `false`
那么用户的上下文会被新的内容所覆盖