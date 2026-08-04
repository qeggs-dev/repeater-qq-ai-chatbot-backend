# 配置文件

用于对 Repeater 进行全局配置
Repeater 会首先从 `CONFIG_DIR` 环境变量
指定的目录去遍历`.md`文件，并加载配置文件。
加载后的配置文件按照路径名称进行排序后
进行合并处理
排名在后的会覆盖在前面的配置项。

PS: 配置管理器会递归扫描环境变量`CONFIG_DIR`下的所有json/yaml文件
并按照路径的字符串顺序排列，后加载配置中的字段会覆盖之前的配置
你也可以使用环境变量`CONFIG_FORCE_LOAD_LIST`来强制按照指定的顺序加载配置


## 最小配置

配置文件的所有字段都有默认值，你只需要填写你需要的部分即可
比如：
``` json
{
    "logger": {
        // 建议填写，默认的是DEBUG，可能会有很多你不需要关注的内容
        "level": "INFO"
    },
    // 如果不填写此项，那么 Repeater 将无法获取模型 API 数据
    "model_api": {
        // MODEL INFO Server URL
        // 填写你实际部署的那个 API Server 地址
        "base_url": "...",

        // 这里非常建议你填写，因为默认的`chat`真的很容易冲突
        // 一定要保证这个 UID 在 Model Server 中存在
        "default_model_id": "deepseek-chat"
    },
    "text_template": {
        "time": {
            // 建议填写，默认是UTC时间，你可能更需要的是本地时间
            "timezone": "Asia/Shanghai"
        },
        // 部分组件依赖于此配置，建议填写
        "enable_user_input_template": true,
    },
    "render": {
        "to_image": {
            // 建议填写，除非你完全用不到 Markdown 图片渲染功能
            "base_url": "",

            // 建议填高一点，渲染时间可能会比较长
            "timeout": 600.0,
        }
    },
    // 建议填写
    // 如果不配置此项，那么 Repeater 将无法找到提示词和渲染所需的 HTML/CSS
    "static_resources_server": {
        // Static Resources Server URL
        // 填写你实际部署的那个 Static Resources Server 地址
        "base_url": "..."
    }
}
```

当你不知道如何配置时，直接运行程序
它可以给你自动生成一份默认配置文件

## 详细字段信息：
```json
{
    // 黑名单配置
    "blacklist": {
        // 黑名单文件路径
        // 格式为 RegexChecker 格式
        // 详情参考本目录下的 regex_checker.md
        "file_path": "./config/blacklist.regex",

        // 黑名单匹配超时时间，单位为秒
        "match_timeout": 10.0 // 匹配超时时间，单位为秒
    },

    // CallAPI 配置
    "callapi": {
        // 协程池最大并发数
        // 仅在 AI 请求路径下生效
        "max_concurrency": 1000,

        // 当为 true 时，将启用流混淆。
        // 流混淆会在流 delta 事件的 `obfuscation` 字段中添加随机字符，
        // 提高攻击者根据长度去推断模型输出内容的难度
        "include_obfuscation":false,

        // 用于在某些 API 下告诉服务方
        // 自己是否需要返回 Usage 信息
        // 默认值：true，因为 Fast Statistics 需要这部分数据
        "include_usage": true,

        // 单次请求的最大生成次数
        // 通常用于模型进行 Tool Calls 等需要循环调用的任务时
        // 限制其最大循环次数，防止模型陷入死循环
        "max_generate_times": 10,

        // 是否发送用户 ID 到服务端
        // 默认值：false
        // 如果为 true，则 Repeater 会讲 user_id 进行 sha256 后填充到 `user_id` 字段中
        // 需要服务端明确支持 `user_id` 字段
        "send_user_id": false,

        // 快速统计配置
        "fast_statistics": {

            // 是否启用快速统计
            "enable": true,

            // 单元项标题最小长度
            "title_width": 50,

            // 图表宽度
            "chart_width": 50,

            // 图表高度
            "chart_height": 10
        }
    },

    // Context 配置
    "context": {
        // 自动上下文长度裁剪
        // 当你聊天过长时，可能会超过模型上下文窗口限制
        // 这个设置可以让 Repeater 为你自动裁剪最久的消息
        // 让你可以继续聊天
        // 默认值： null ，表示不启用
        // 你可以在这里填写一个整数，表示自动裁剪的长度，单位为字符数量
        "context_shrink_limit": null,
        
        // 是否在用户未指定的情况下
        // 保存用户的上下文历史
        "save_context": true,

        // 是否丢弃非文本数据
        // 只保存文本，不保存图片，音频等其他数据
        // 默认为 false
        // 设为 true 可能会让你获得更快的解析速度
        "save_text_only": false,

        // 是否只保存新数据
        // 默认为 false
        // 设为 true 则只保存新消息，而不是追加到历史消息中
        "save_new_only": false,

        // 是否构建多模态消息
        // 如果禁用，则附加数据会以 JSON 的方式传入
        "make_multimodal_message": true,

        // 是否移除上下文中的推理内容
        // 通常建议设置为 true
        // 通常推理模型不愿意重新读入推理内容
        "remove_reasoning_prompt": true,

        // 非文本数据在日志中的最大显示长度
        // 设置为 null 则不进行截断
        "max_log_length_for_non_text_content": 25
    },

    // 全局异常处理器配置
    "global_exception_handler": {
        // 当异常未被处理时，服务器返回的错误信息
        "error_message": "Internal Server Error",

        // 遇到关键错误是，服务器返回的错误信息
        "critical_error_message": "Critical Server Error!",

        // 在遇到关键错误时，是否让服务器关闭
        "crash_exit": true,

        // 遇到问题时，保存 traceback 的目录
        // 如果该值为 null 则程序会跳过这一步骤
        // 但日志中的错误追踪不受影响
        "traceback_save_to": "./workspace/crash_log",

        // 是否记录所有异常(比如 KeyboardInterrupt)
        "record_all_exceptions": true,

        // 是否记录非 500 的 HTTP 异常的 Traceback
        "record_warn_http_exception": false,

        // 代码读取器配置
        // 通常是为了更直观的显示错误位置
        "code_reader": {
            // 是否启用代码读取器
            "enable": true,

            // 读取代码文件时使用的编码
            "code_encoding": "utf-8",

            // 读取代码文件时
            // 从错误发生行开始
            // 向上下扩展读取的行数
            // 比如：错误发生在第 10 行
            // 且 "code_line_dilation" 设置为 3
            // 则会读取 7-13 行
            "code_line_dilation": 3,

            // 读取时是否添加行数标记
            "with_numbers": true,

            // 行数标记所占用的字符长度
            // 默认为5
            // 即行数在5个字符的最右边
            // 举例：
            // |    1| def foo():
            // |>   2|     raise Exception("Error")
            // └─────┴─────────────────────────────
            "reserve_space": 5,

            // 行数标记填充字符
            // 通常为空格
            "fill_char": " ",

            // 添加底部边框
            // 一般长度上限为终端宽度减去行数标记所占的长度
            "add_bottom_border": true,

            // 底部边框延长线的长度上限
            // 当值为 null 时，将使用终端宽度减去行数标记所占的长度
            "bottom_border_limit": null
        },
        
        // 使用 Repeater 自己的 Traceback 格式化函数
        "repeater_traceback": {
            // 是否启用
            "enable": false,

            // 在 Traceback 中格式化时间使用的格式
            "timeformat": "YYYY-MM-DD HH:mm:ss",

            // 是否排除库函数的 Traceback
            "exclude_library_code": true,
        
            // 是否使用自定义的 pydantic.ValidationError 格式化信息
            "format_validation_error": true,

            // 是否记录警告信息
            "record_warnings": true,

            // 是否使用传统堆栈帧格式 (Python 原版 Traceback)
            "traditional_stack_frame": false,
        }
    },

    // 许可证信息
    "licenses": {
        // 依赖项的许可证文件所在目录
        // 注意：这个目录需要保持正确的结构才能被程序正确解析
        "license_dir": "./LICENSES",

        // 许可证文件读取时使用的编码
        "license_encoding": "utf-8",

        // 项目自己的许可证文件
        "self_license_files": {
            "MIT": "./LICENSE"
        }
    },

    // Logger 配置
    "logger": {
        // Log 文件输出路径
        "file_path": "./logs/repeater-log-{time:YYYY-MM-DD_HH-mm-ss.SSS}.log",

        // Log 控制台输出格式
        "console_format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{extra[user_id]}</cyan> - <level>{message}</level>",

        // Log 文件输出格式
        "file_format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[user_id]} - {message}",

        // Log 级别
        "level": "INFO",

        // Log 轮换设置
        "rotation": "1 days",

        // Log 保留设置
        "retention": "1 months",

        // Log 过期后执行的操作
        "compression": "zip"
    },

    // 模型参数配置
    // 你可以微调默认的请求的默认参数
    // 如果用户没有定义模型参数，则使用这里定义的参数取请求 API
    "model": {
        // 默认模型超时时间，单位为秒
        "default_timeout": 600.0,

        // 默认模型种子
        // 如果值为 null, 则表示未定义, 值将由模型提供方的默认值决定
        "default_seed": null,

        // 默认模型温度，更高的温度意味着下一个词更高的不确定性
        // 如果值为 null, 则表示未定义, 值将由模型提供方的默认值决定
        "default_temperature": null,

        // 默认模型 Top_A
        // 筛选出所有概率不低于 最高概率的token × A 的 token
        // 然后归一化重新采样
        // 如果值为 null, 则表示未定义, 值将由模型提供方的默认值决定
        "default_top_a": null,

        // 默认模型 Top_P ，值越大在采样时考虑的词汇越多
        // 如果值为 null, 则表示未定义, 值将由模型提供方的默认值决定
        "default_top_p": null,

        // 默认模型 Top_K
        // 从概率最高的 K 个 token 中抽样，其余 token 的概率被直接置为零
        // 如果值为 null, 则表示未定义, 值将由模型提供方的默认值决定
        "default_top_k": null,

        // 默认模型最大生成长度(兼容)
        // 如果值为 null, 则表示未定义, 值将由模型提供方的默认值决定
        "default_max_tokens": null,

        // 默认模型最大生成长度
        // 如果值为 null, 则表示未定义, 值将由模型提供方的默认值决定
        "default_max_completion_tokens": null,

        // 默认模型重复惩罚，值越高模型越不容易出现重复内容
        // 惩罚程度按照重复次数增加，该值不允许为负
        // 如果值为 null, 则表示未定义, 值将由模型提供方的默认值决定
        "default_repetition_penalty": null,

        // 默认模型频率惩罚，值越高模型越不容易出现重复内容
        // 惩罚程度按照频率增加，如果该值为负则是奖励模型输出重复内容
        // 如果值为 null, 则表示未定义, 值将由模型提供方的默认值决定
        "default_frequency_penalty": null,

        // 默认模型存在惩罚，值越高模型越不容易出现重复内容
        // 惩罚程度只要存在就一直不变，如果该值为负则是奖励模型输出重复内容
        // 如果值为 null, 则表示未定义, 值将由模型提供方的默认值决定
        "default_presence_penalty": null,

        // 默认在 FIM 模式下，模型是否重复用户输入
        // 如果值为 null, 则表示未定义, 值将由模型提供方的默认值决定
        "default_fim_echo": null,

        // 默认模型停止符
        // 当模型输出到停止符内容时，停止生成
        "default_stop": [],
        
        // 开启混合推理模型的思考模式
        // 如果这里为 null，则使用默认
        // 如果为 true 则强制开启
        // 如果为 false 则强制关闭
        "default_thinking": null,


        // 控制模型的推理强度
        // 允许的值有：
        // - "low"
        // - "medium"
        // - "high"
        // - "xhigh"
        // - "max"
        // - null
        "default_reasoning_effort": null,

        // 控制模型是否输出 logprobs
        // 如果这里为 null，则使用提供方的默认值
        "logprobs": null,

        // 默认模型返回的 logprobs 数量
        // 如果这里为 null，则使用提供方的默认值
        "top_logprobs": null,


        // 默认模型是否流式输出
        // 注意：这里只是在告诉 Repeater 应该使用什么方式调用模型接口
        // 如果模型不支持流式生成，调用可能会报错
        // 且该参数不能决定 /generate/chat/completion 接口是否流式输出
        // 如果这里为 false
        // 那么 /generate/chat/completion 接口调用时 stream 参数能且只能为 false
        // 此时如果客户端请求流式响应，会返回503错误
        // 请求控制台和日志不会显示生成过程，也不会有chunk统计数据
        // 如果这里为 true
        // 那么 /generate/chat/completion 接口调用时 stream 参数可以为 true 或 false
        // 且控制台和日志会打印当前 chunk ，并生成 chunk 统计数据
        "stream": true,

        // 可以填写一些固定的其他参数
        // 如果用户填写了其他参数
        // 优先使用此处填写的参数
        "extra_bodys_priority": {
            
        },

        // 可以填写一些固定的其他参数
        // 如果用户填写了其他参数
        // 则会覆盖此处填写的参数
        "extra_bodys": {
            
        },

        // 是否启用用户自定义参数
        // 如果启用，用户可以自定义参数
        // 如果不启用，用户自定义参数会被忽略，但服务器定义的参数不会受影响
        // 该值也会影响 call_model 工具的行为
        // 如果禁用，会忽略传入的 extra_bodys 参数
        "enable_user_extra_bodys": false,
    },

    // MODEL API 配置
    "model_api": {
        // MODEL INFO Server URL
        "base_url": "",

        // 请求超时时间
        "timeout": 10.0,

        // MODEL INFO Server 鉴权 token 环境变量名
        "api_key_env_name": "MODEL_INFO_API_KEY",

        // 默认模型 ID
        // 如果填写为列表，则顺序尝试直到找到第一个有匹配的 ID
        "default_model_id": "chat",

        // 随机选择模型 ID 的概率衰减指数
        "random_decay_index": 0.5,

        // Ping 服务提供方配置
        "ping_provider":{
            "timeout": 5.0,
            "times": 4,
            "size": 32,
            "interval": 0.0
        }
    },

    // Nexus Client 配置
    "nexus": {

        // Nexus Client 的服务器 URL
        "base_url": "",

        // Nexus Client 的请求超时时间
        "api_timeout": 60
    },

    // template 提示词文本模板展开器配置
    // 注：此选项不会改变实际的其他系统内容，而只会改变模板展开器中的变量
    "text_template": {
        // 模板展开器中显示的程序版本
        // 如果为 null 或空字符串
        // 则程序会使用 core 版本号填充
        "version": null,

        // 模板展开器的沙箱模式
        "sandbox": {
            // 沙箱模式选项
            // 可选值：
            // "sandboxed" - 普通沙箱模式，限制私有内容、危险内置函数、特殊方法、内置类型修改、高危模块等内容
            // "immutable_sandboxed" - 不可变沙箱模式，一切数据都将是不可变，列表的修改将会失效
            // "none" - 无沙箱模式，程序将对用户输入不做任何限制
            "sandbox_mode": "sandboxed",
        },
        "time": {
            // 时区字符串
            "timezone": "Asia/Shanghai",

            // 时间格式字符串
            // 在 time 函数未指定 time_format 参数时使用
            "time_format": "%Y-%m-%d(%A) %H:%M:%S %Z"
        },

        // 默认用户信息
        // 当用户未填写个人设定时，将使用此文本作为值
        // 通常建议为空值，因为这样模板就能检查是否有用户设定并针对性地处理了
        "default_user_profile": "",

        // 请求日志模板
        // 用于在请求返回时自定义统计内容信息的格式
        "request_statistics_template": "Total Tokens: {{request_log.total_tokens}} | Input: {{request_log.prompt_tokens}} | Output: {{request_log.completion_tokens}}",

        // 允许模板中使用 HTTP 请求
        "allow_http": false,
        
        // 模板展开器启用控制
        "enable": {
            // 是否在用户输入中激活模板展开器
            "user_input_template": false,

            // 是否在 ASSISTANT 输出中激活模板展开器
            "assistant_template": false,

            // 是否启用 API
            "api_template": false,

            // 是否启用 request_statistics_template
            "request_statistics_template": false
        }
    },

    // Tool Calls 配置
    "tool_calls": {
        // 是否启用 Tool Calls
        "enabled": false,

        // 注册的 Tool Calls
        // 即使是内置 Tool
        // 也需要在此注册
        // 你需要在此处填写它们的注册名
        // 否则模型将无法找到它们
        "registed": [],

        // 所有用户默认允许 Tool Calls
        "allow_by_default": false,

        // Tool Calls 结果最大长度（用于日志）
        // 设置为 null 则不限制长度
        "result_max_length_for_logs": 100,

        // Tools 自己的配置
        "tools_configs": {

            // HTTP 请求配置
            "http_requests": {
                // 允许的 HTTP 方法
                // 设置为 null 则所有方法不可用
                // 设置为 "ALL" 则所有方法可用
                // 可以指定仅能的方法，比如 ["GET", "POST"]
                "allowed_http_methods": null,

                // 上报给目标服务器的爬虫名称
                // 默认为 "Repeater AI Crawler"
                "crawler_name": "Repeater AI Crawler",

                // 缓存的 Robots.txt 项目数量
                "robots_cache_size": 8192,

                // 缓存 Robots.txt 的超时时间（秒）
                "robots_cache_timeout": 3600,

                // 是否允许对私有网络进行 HTTP 请求
                // 包括局域网与回环
                "allow_private_network_requests": false
            },

            // 系统信息配置
            "system_info": {
                
                // 系统信息的拓展内容
                "extra_info": {}
            }
        }
    },

    // Prompt 配置
    "prompt": {
        // 告诉 Prompt 加载器预设提示词目录的路径
        "base_path": "/prompt/presets",

        // 预设提示词文件的后缀名
        "suffix": ".md",

        // 预设提示词文件应该用什么编码打开
        "encoding": "utf-8",

        // 如果用户没有指定用一个预设提示词时
        // 应该使用哪一个提示词
        "preset_name": "official/normal/repeater",

        // 是否在用户未指定的情况下
        // 加载提示词
        "load_prompt": true
    },
    
    // Markdown 图片渲染器配置
    "render": {
        // 图片等待多少时间后被删除（URL有效时间）
        "default_image_timeout": 60.0,

        // Markdown 到 HTML 渲染配置
        "markdown": {
            // 默认样式
            "default_style": "light",

            // 样式文件目录
            "styles_base_path": "/configs/styles",

            // HTML 模板文件目录
            "html_template_base_path": "/configs/html_templates",

            // HTML 模板文件应该用什么编码打开
            "html_template_file_encoding": "utf-8",

            // 默认使用的 HTML 模板文件
            "default_html_template": "standard.html",

            // 是否允许请求自定义 CSS
            "allow_custom_styles": false,

            // 是否允许请求自定义 HTML 模板
            "allow_custom_html_templates": false,

            // 是否允许文本跳过 Mardown 解析
            "allow_direct_output": false,

            // 允许使用的 HTML 标签白名单
            "allowed_tags": [
                "p", "br", "strong", "em", "u", "del", "ins",
                "h1", "h2", "h3", "h4", "h5", "h6",
                "ul", "ol", "li",
                "a", "img",
                "code", "pre", "blockquote",
                "table", "thead", "tbody", "tr", "th", "td",
            ],
            
            // 允许使用的 HTML 属性白名单
            "allowed_attrs": {
                "a": ["href", "title", "rel"],
                "img": ["src", "alt", "title"],
                "code": ["class"],
                "pre": ["class"],
            },

            // 允许使用的协议白名单
            "allowed_protocols": ["http", "https", "mailto"],
            
            // 在使用 direct_output 时，是否不添加 pre 标签
            // 为 null 时使用请求中的值
            "no_pre_labels": false,

            // Markdown 预处理器配置
            "preprocess_map": {
                // Before 预处理器
                // 处理 Markdown 数据
                "before": {},
                // After 预处理器
                // 处理 HTML 数据
                "after": {}
            },
            // 在 HTML 中添加的标题
            "title": "Repeater Image Generator",

            // 在 HTML 中添加的底部注释
            "document_bottom_comment": ""
        },

        // HTML 到图片的渲染器配置
        "to_image": {
            // 渲染服务的 Base URL
            "base_url": "",

            // 渲染服务请求超时时间
            "timeout": 600.0,
        }
    },

    // /chat/completion 端口的请求日志
    "request_log": {
        // 请求日志的保存目录
        "dir": "./workspace/request_log",

        // 是否自动保存请求日志
        "auto_save": true,

        // 缓存请求日志的等待时间
        "debonce_save_wait_time": 1200.0,

        // 请求日志缓存的队列最大长度
        "max_cache_size": 1000,

        // 全量缓存的存活时间
        "cache_keep_time": 1200.0,

        // 是否开启全量内存缓存
        "full_memory_cache": false
    },

    // 服务器配置
    // 这里的几个字段为 null 或不填则会使用环境变量中定义的配置
    // 如果这里填写了内容，那么这里的内容会覆盖环境变量中的值
    "server": {
        // 监听的IP
        "host": null,

        // 监听的端口
        "port": null,

        // 工作进程数量
        "workers": null,

        // 是否在文件发生变动时自动重启
        "reload": null,

        // 是否启动服务器
        // 如果为 false
        // 那么在初始化结束后
        // 程序将会直接退出
        // 而不是启动服务器
        "run_server": true,

        // 是否开启异步事件循环的调试模式
        "asyncio_debug": false
    },

    // 静态文件配置
    "static": {
        // README.md 文件的路径
        "readme_file_path": "./README.md",

        // 静态文件目录
        "static_dir": "./static"
    },

    // 静态资源配置
    // 在多实例的情况下，可以集中管理共享资源
    "static_resources_server": {

        // 静态资源服务器的地址
        "base_url": "",

        // 静态资源服务器的超时时间
        "timeout": 10.0
    },

    // 系统识别配置
    "system_identification": {
        // 系统名称
        "system_name": "Repeater AI System",

        // 系统的 User-Agent
        "system_ua": "Repeater AI System",

        // 爬虫名称
        "crawler_name": "Repeater AI Crawler"
    },

    // 用户数据配置
    "user_data": {
        // 用户数据的保存目录
        "dir": "./workspace/data/user_data",

        // 分支数据使用的目录名称
        "branches_dir_name": "branches",

        // 元数据文件名称
        "metadata_file_name": "metadata.json",

        // 默认分支名称
        "default_branch_id": "main",

        // 使用 Base64 编码处理文件路径
        // 以安全的包含用户传入的字符串
        // 而不是触发异常文件名或路径穿越
        "b64_encode_path": true,

        // 是否阻止跨用户数据访问
        // 如果为 true，则请求时按照请求的 `cross_user_data_routing` 来加载数据
        // 否则，则只能操作当前用户的数据
        "cross_user_data_access": false,

        // 是否缓存
        // 这里的两个字段同时支持 bool 和 cache_data 结构
        // 如果为 bool ，则该值对所有数据类型生效
        // 如果为 cache_data 结构，则该值对指定的数据类型生效
        // 警告：缓存系统仍未进行可行性与稳定性验证，请谨慎使用

        // 是否缓存元数据
        "cache_medadata": false,
        // 是否缓存用户数据
        "cache_data": {
            "context": false,
            "prompt": false,
            "config": false
        }
    },

    // 用户昵称映射配置
    "user_nickname_mapping": {
        // 昵称映射文件路径
        // 有些用户的昵称可能会让模型陷入循环
        // 可以用这个文件来映射它们到一个安全的昵称
        "file_path": "./config/user_nickname_mapping.json"
    },

    // Web配置
    "web": {
        // Index Web 文件路径
        // 如果不填写这个项目，那么默认会使用内置的索引页面
        // 你也可以使用这个来为 Repeater 创建一个自定义前端
        "index_web_file": "./static/index.html",

        // 更多的 Web 页面
        // 虽然这里其实可以用 static 来代替
        // 但一个 Web 页面要是 static 出现在 URL 上
        // 至少我觉得怪怪的
        "web_directory": "./configs/web"
    }
}
```