# @复读机Repeater
**- Only Chat, Focus Chat. -**

*注：本仓库仅为后端实现，NoneBot插件部分请查看[`Repater-Nonebot-Plugin`](https://github.com/qeggs-dev/repeater-qq-ai-chatbot-nonebot-plugins)*

一个基于[`NoneBot`](https://nonebot.dev/)和[`OpenAI SDK`](https://pypi.org/project/openai/)开发的**实验性**QQ聊天机器人
**此仓库仅为后端实现，NoneBot插件部分请查看[`Repater-Nonebot-Plugin`](https://github.com/qeggs-dev/repeater-qq-ai-chatbot-nonebot-plugins)**
将原始会话数据的处理直接公开给用户使用
接近直接操作API的灵活度体验
(私聊请注意先加好友，临时消息可能会失败)

与其他QQ机器人相比，复读机具有以下特点：

 - 平行数据管理：支持平行数据管理，用户可以随意切换平行数据，而不需要担心数据丢失。
 - 多模型支持：支持OpenAI接口的模型即可调用，可以根据需要选择不同的模型进行对话。
 - 超高自由度：用户可以自定义会话注入、切换、删除，以及自定义提示词
 - MD图片渲染：可以将回复以图片的形式渲染发送，降低其妨碍用户正常聊天的程度（但鬼知道为什么这东西竟然不支持Emoji渲染！！！）
 - 命令别名触发：不管是缩写还是全文，都可以触发命令操作
 - 用户自治设计：用户可以自己管理自己的所有用户数据
 - 多预设人设：复读机支持多预设人设，用户可以自由选择自己喜欢的人设进行对话
> 注：拟人化并非复读机的赛道，复读机不对拟人化需求做过多保证，如有需要请自行处理。

## 注意事项:
 - 本服务由一位 `16岁自学开发者` 使用AI协作开发，公益项目，如果你愿意捐赠，可以在机器人的**QQ空间**中找到赞赏码以支持项目运营(或是支持开发者)。
 - 初始服务仅作为实验项目运行，不保证服务稳定性（存在维修断电以及临时消息丢失的可能，但这与项目本身无关，~~只是我不懂运维罢了~~），有需要可自行部署。
 - 项目随时可能会因为开发者个人原因，或API额度耗尽等因素而被迫中止。
 - 仅供学习和非商业用途。使用者需确认生成内容的合法性，并自行承担使用本服务可能产生的风险。
 - 如果你觉得这个Bot非常好用，请去看一下[`Deepseek`](https://www.deepseek.com/)的官网吧，这个Bot最初就是基于他们的模型API开发的。

---

## License
这个项目基于[MIT License](LICENSE)发布。

---

<details>
    <summary>旧版部署教程(已废弃)</summary>

> ## 主要依赖
> #### [`NoneBot`](https://nonebot.dev/)：一个基于Python的异步OneBot框架
> 安装步骤(默认你已经安装了Python)：
> 
> > 1. 打开命令行终端，切换路径到你希望安装NoneBot的目录下
> > 2. 初始化虚拟环境(此处以venv为例，已经有虚拟环境的可以跳过此步骤)：python -m venv venv
> > 3. 激活虚拟环境(如果已经激活可以跳过此步骤)：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> 
> 部署步骤(默认你已经获取到了复读机的NoneBot插件)：
> 
> > 1. 命令行输入pip install nb-cli，回车运行命令
> > 2. 再次输入nb create回车，创建一个项目
> > 3. 选择simple模板
> > 4. 给项目起个名字
> > 5. 建议使用FastAPI驱动器
> > 6. **至少必须选择OneBot V11适配器**
> > 7. 输入Yes安装默认依赖
> > 8. 输入Yes安装虚拟环境
> > 9. 如果需要，可以选择内置插件，如echo
> > 11. 在项目目录下，找到`.env`文件
> > 12. 填写HOST(x.x.x.x)和PORT(数字)，并保存
> > 13. 将复读机的NoneBot插件放入项目目录下（通常是`plugins`文件夹下）
> > 14. 部署完成后，运行nb run
> 
> #### [`OpenAI SDK`](https://github.com/openai/openai-python)：一个基于Python的大模型对接SDK
> 安装步骤(默认你已经安装了Python)：
> 
> > 1. 打开命令行终端，切换路径到你希望安装OpenAI SDK的目录下
> > 2. 初始化虚拟环境(此处以venv为例，已经有虚拟环境的可以跳过此步骤)：python -m venv venv
> > 3. 激活虚拟环境(如果已经激活可以跳过此步骤)：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> > 4. 输入命令pip install openai，回车运行命令
> 
> #### [`FastAPI`](https://fastapi.tiangolo.com/)：一个用于构建高性能、可扩展的API的Python框架
> 安装步骤(默认你已经安装了Python)：
> 
> > 1. 打开命令行终端，切换路径到你希望安装FastAPI的目录下
> > 2. 初始化虚拟环境(此处以venv为例，已经有虚拟环境的可以跳过此步骤)：python -m venv venv
> > 3. 激活虚拟环境(如果已经激活可以跳过此步骤)：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> > 4. 输入命令pip install fastapi，回车运行命令
> 
> #### [`uvicorn`](https://www.uvicorn.org/)：一个基于ASGI的Python服务器，用于运行FastAPI应用
> 安装步骤(默认你已经安装了Python)：
> 
> > 1. 打开命令行终端，切换路径到你希望安装uvicorn的目录下
> > 2. 初始化虚拟环境(此处以venv为例，已经有虚拟环境的可以跳过此步骤)：python -m venv venv
> > 3. 激活虚拟环境(如果已经激活可以跳过此步骤)：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> > 4. 输入命令pip install uvicorn，回车运行命令
> 
> #### [`NapCat`](https://napneko.github.io/guide/napcat): 一个用于处理QQ消息的OneBot适配器
> 安装步骤(此处默认选择Shell版安装方式)
> 
> > 1. 前往 NapCatQQ 的 release 页面 下载NapCat.Shell.zip解压
> > 2. 确保QQ版本安装且最新
> > 3. 双击目录下launcher.bat启动(如果是win10 则使用launcher-win10.bat)
> 
> 配置步骤：
> 
> > 1. 启动后，扫码登陆NapCatQQ
> > 2. 访问WebUI(http://127.0.0.1:xxxx/webui/?token=napcat)
> > 3. 点击`网络配置`
> > 4. 点击`新建`，选择`WebSocket客户端`
> > 5. 打开`启用`，输入一个名称
> > 6. 输入NoneBot配置时填写的`HOST`和`PORT`(格式：ws://`HOST`:`PORT`/onebot/v11/ws)
> > 7. 输入token(如果你没改密码那么就填入`napcat`，否则需要填入你的密码)
> > 8. 点击`保存`，等待连接成功
> 
> ---
> 
> ## 次级依赖
> 
> *默认你已经完成主要依赖的安装*
> 
>  - aiofiles
>  - environs
>  - python-multipart
>  - loguru
>  - orjson
>  - uvicorn
>  - markdown
>  - imgkit
>  - httpx
</details>

---

## 安装部署

**至少需要确保安装了Python3.10以上版本**

### 1. 初始化环境
> 将项目克隆到本地后，进入项目目录，执行以下操作：
> ###### Windows:
> 执行setup.bat
> 
> ###### Linux:
> 执行下列命令
> ```shell
> bash setup.sh
> ```

### 2. 配置环境变量
> 在项目目录下创建.env文件，参照[环境变量表](#环境变量表)填写相关配置

### 3. 启动服务
> ###### Windows:
> 执行run.bat
> 
> ###### Linux:
> 执行下列命令
> ```shell
> bash run.sh
> ```

---

## 环境变量表

| 环境变量 | 描述 | 是否必填 | 默认值(*示例值*) |
| :---: | :---: | :---: | :---: |
| `HOST` | 服务监听的IP | *选填* | 0.0.0.0 |
| `PORT` | 服务监听端口 | *选填* | 8080 |
| `SAVE_CALL_LOG` | 运行时是否记录主API的调用日志 | *选填* | True |
| `VERSION` | 版本号 | *选填* | \*由代码自动生成 |
| `*API_KEY` | API_Key (具体变量名由`API_INFO_FILE_PATH`指向 文件中`ApiKeyEnv`字段的名称) | **必填** | *\*可从[Deepseek开放平台/API Keys](https://platform.deepseek.com/api_keys)页面获取* |
| `API_INFO_FILE_PATH` | API信息文件路径 | **必填** | *`./config/apiconfig.json`* |
| `CALL_LOG_FILE_PATH` | 主API调用日志的持久化存储文件 | **必填** | *`./config/calllog.jsonl`* |
| `MAX_CONCURRENCY` | 最大并发数 | *选填* | 1000 |
| `DEFAULT_PROMPT_DIR` | 默认提示词文件夹 | *选填* | `./PresetsPrompt` |
| `PARSET_PROMPT_NAME` | 默认提示词文件名(不包括后缀) | *选填* | `default` |
| `README_FILE_PATH` | README文件位置 | *选填* | `./README.md` |
| `RENDERED_IMAGE_DIR` | 渲染图片的缓存位置 | **必填** |* `./temp/render`* |
| `STATIC_DIR` | 静态资源位置 | **必填** | *`./static`* |
| `USER_DATA_DIR` | 用户数据存放位置 | **必填** | *`./data/userdata`* |
| `USER_DATA_SUB_DIR_NAME` | 用户子数据文件夹名称 | *选填* | `ParallelData` |
| `USER_DATA_CACHE_METADATA` | 是否缓存用户数据元数据 | *选填* | `False` |
| `CONTEXT_USERDATA_CACHE_METADATA` | 控制用户数据元数据缓存是否开启 | *选填* | \*`USER_DATA_CACHE_METADATA`的值 |
| `PROMPT_USERDATA_CACHE_METADATA` | 控制提示词数据元数据缓存是否开启 | *选填* | \*`USER_DATA_CACHE_METADATA`的值 |
| `USERCONFIG_USERDATA_CACHE_METADATA` | 配置用户数据元数据缓存是否开启 | *选填* | \*`USER_DATA_CACHE_METADATA`的值 |
| `USER_DATA_CACHE_DATA` | 是否缓存用户数据 | *选填* | `False` |
| `CONTEXT_USERDATA_CACHE_DATA` | 控制用户数据缓存是否开启 | *选填* | \*`USER_DATA_CACHE_DATA`的值 |
| `PROMPT_USERDATA_CACHE_DATA` | 控制提示词数据缓存是否开启 | *选填* | \*`USER_DATA_CACHE_DATA`的值 |
| `USERCONFIG_USERDATA_CACHE_DATA` | 配置用户数据缓存是否开启 | *选填* | \*`USER_DATA_CACHE_DATA`的值 |
| `CONFIG_CACHE_DOWNGRADE_WAIT_TIME` | 配置管理器缓存降级等待时间 | *选填* | `60` |
| `CONFIG_CACHE_DEBONCE_SAVE_WAIT_TIME` | 配置管理器缓存延迟保存时间 | *选填* | `60` |
| `USER_NICKNAME_MAPPING_FILE_PATH` | 用户昵称映射表文件位置 | *选填* | `./config/UserNicknameMapping.json` |
| `TIMEZONE_OFFSET` | 默认时区偏移设置 | *选填* | `8` |
| `DEFAULT_TEMPERATURE` | 默认模型温度 | *选填* | `1.0` |
| `DEFAULT_TOP_P` | 默认模型`Top_P` | *选填* | `1.0` |
| `DEFAULT_FREQUENCY_PENALTY` | 默认模型频率惩罚 | *选填* | `0.0` |
| `DEFAULT_PRESENCE_PENALTY` | 默认模型存在惩罚 | *选填* | `0.0` |
| `DEFAULT_MAX_TOKENS` | 默认模型最大输出token<br/>(部分API不支持 `DEFAULT_MAX_COMPLETION_TOKENS`设置 提供此项以兼容) | *选填* | `1024` |
| `DEFAULT_MAX_COMPLETION_TOKENS` | 默认模型最大生成token | *选填* | `1024` |
| `CALLLOG_DEBONCE_SAVE_WAIT_TIME` | 日志持久化存储的防抖时间 | *选填* | `60` |
| `CALLLOG_MAX_CACHE_SIZE` | 日志缓存的最大数量 | *选填* | `1000` |
| `DEFAULT_MODEL_TYPE` | 调用时默认使用的模型类型 | **必填** | *`chat`* |
| `WKHTMLTOPDF_PATH` | 渲染图片依赖的[`Wkhtmltopdf`](https://wkhtmltopdf.org/downloads.html)的位置 | **必填** | |
| `DEFAULT_OUTPUT_DPI` | 渲染图片输出的DPI | **必填** | *`150`* |
| `BOT_NAME` | 机器人名字 | **必填** | *`复读机`* |
| `BIRTHDAY_YEAR` | 机器人出生年份 | **必填** | *`2024`* |
| `BIRTHDAY_MONTH` | 机器人出生月份 | **必填** | *`06`* |
| `BIRTHDAY_DAY` | 机器人出生日期 | **必填** | *`28`* |
| `ADMIN_API_KEY` | 机器人管理API的密钥 | *选填* | \*自动生成 |

---

## Markdown图片渲染样式

| 风格 | 译名 |
| :---: | :---: |
| **`light`** | 亮色 |
| `dark` | 暗色 |
| `pink` | 粉色 |
| `blue` | 蓝色 |
| `green` | 绿色 |

---

## 人格预设

| 预设 | 描述 |
| :---: | :---: |
| `default` | 默认 |
| `sister` | 姐姐 |

---

## 模型

| 模型 | 描述 |
| :---: | :---: |
| `chat` | 聊天 |
| `reasoner` | 推理 |
| `coder` | 编码 |
| `prover` | 证明 |

---

## 变量表

| 变量 | 描述 | 参数 |
| :---: | :---: | :---: |
| `user_id` | 用户ID | 无 |
| `user_name` | 用户名 | 无 |
| `BirthdayCountdown` | 复读机生日倒计时 | 无 |
| `model_type` | 模型类型 | 无 |
| `birthday` | 复读机生日 | 无 |
| `zodiac` | 复读机星座 | 无 |
| `time` | 当前时间 | 无 |
| `age` | 复读机年龄 | 无 |
| `random` | 随机数 | 随机数范围 |
| `randfloat` | 随机浮点数 | 随机数范围 |
| `randchoice` | 随机选择 | 项目内容 |

---

## 接口表

| 请求 | URL | 参数(表单数据) | 描述 |
| :---: | :---: | :---: | :---: |
| `POST` | `/chat/completion/{user_id:str}` | `message(str)`<br/>`user_name(str)`<br/>`role(str) = 'user'`<br/>`role_name(str)`<br/>`model_type(str)`<br/>`load_prompt(bool) = true`<br/>`rendering(bool) = false`<br/>`save_context(bool) = true`<br/>`reference_context_id(str)`<br/>`continue_completion(bool)`  | AI聊天 |
| `POST` | `/userdata/variable/expand/{user_id:str}` | `username(str)`<br/>`text(str)` | 变量解析 |
| `GET` | `/userdata/context/get/{user_id:str}` | | 获取上下文 |
| `GET` | `/userdata/context/length/{user_id:str}` | | 获取上下文长度 |
| `GET` | `/userdata/context/userlist` | | 获取用户列表 |
| `POST` | `/userdata/context/withdraw/{user_id:str}` | `index(int)` | 撤回上下文 |
| `POST` | `/userdata/context/rewrite/{user_id:str}` | `index(int)`<br/>`content(str)`<br/>`reasoning_content(str)` | 重写上下文 |
| `GET` | `/userdata/context/branch/{user_id:str}` | | 获取用户分支ID列表 |
| `GET` | `/userdata/context/now_branch/{user_id:str}` | | 获取用户当前分支ID |
| `POST` | `/userdata/context/change/{user_id:str}` | `new_branch_id(str)` | 切换上下文 |
| `DELETE` | `/userdata/context/delete/{user_id:str}` | | 删除上下文 |
| `GET` | `/userdata/prompt/get/{user_id:str}` | | 获取提示词 |
| `POST` | `/userdata/prompt/set/{user_id:str}` | `prompt(str)` | 设置提示词 |
| `GET` | `/userdata/prompt/userlist` | | 获取用户列表 |
| `GET` | `/userdata/prompt/branch/{user_id:str}` | | 获取用户分支ID列表 |
| `GET` | `/userdata/prompt/now_branch/{user_id:str}` | | 获取用户当前分支ID |
| `POST` | `/userdata/prompt/change/{user_id:str}` | `new_branch_id(str)` | 切换提示词 |
| `DELETE` | `/userdata/prompt/delete/{user_id:str}` | | 删除提示词 |
| `GET` | `/userdata/config/get/{user_id:str}` | | 获取配置 |
| `POST` | `/userdata/config/set/{user_id:str}/{value_type:str}` | `config(str)` | 设置配置 |
| `POST` | `/userdata/config/delkey/{user_id:str}` | `key(str)` | 删除配置 |
| `GET` | `/userdata/config/userlist` | | 获取用户列表 |
| `GET` | `/userdata/config/branch/{user_id:str}` | | 获取用户分支ID列表 |
| `GET` | `/userdata/config/now_branch/{user_id:str}` | | 获取用户当前分支ID |
| `POST` | `/userdata/config/change/{user_id:str}` | `new_branch_id(str)` | 切换分支数据 |
| `DELETE` | `/userdata/config/delete/{user_id:str}` | | 删除用户配置文件 |
| `GET` | `/userdata/file/{user_id:str}.zip` | | 获取用户数据 |
| `GET` | `/calllog` | | 获取调用日志(不推荐) |
| `GET` | `/calllog/stream` | | 流式获取调用日志(推荐) |
| `GET` | `/file/render/{file_uuid:str}.png` | | 获取图片渲染输出文件 |
| `POST` | `/admin/reload/apiinfo` | (Header: `X-Admin-API-Key`) | 刷新API信息 |
| `POST` | `/admin/regenerate/admin_key` | (Header: `X-Admin-API-Key`) | 重新生成管理密钥 |

---

## 命令表：

\*已被移动至[NoneBot插件仓库](https://github.com/qeggs-dev/repeater-qq-ai-chatbot-nonebot-plugins)

---

## 联系我们

 - **QQ群**：`870063670`
 - **Bot账号**: `3843736490`