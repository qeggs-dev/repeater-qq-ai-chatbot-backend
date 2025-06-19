# @复读机Repeater
**- Only Chat, Focus Chat. -**
一个基于[`NoneBot`](https://nonebot.dev/)和[`OpenAI SDK`](https://pypi.org/project/openai/)开发的**实验性**QQ聊天机器人
将原始会话数据的处理直接公开给用户使用
灵活性较高，只需要与账号取得联系即可开箱使用
(私聊请注意先加好友，临时消息可能会失败)

该机器人暂未考虑开源，后续可能会考虑开源

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
 - 初始服务仅作为实验项目运行，不保证服务稳定性。
 - 项目随时可能会因为开发者个人原因，或API额度耗尽等因素而被迫中止。
 - 仅供学习和非商业用途。使用者需确认生成内容的合法性，并自行承担使用本服务可能产生的风险。
 - 如果你觉得这个Bot非常好用，请去看一下[`Deepseek`](https://www.deepseek.com/)他们的官网吧，这个Bot是基于他们的API开发的。

---

## 主要依赖
#### [`NoneBot`](https://nonebot.dev/)：一个基于Python的异步OneBot框架
安装步骤(默认你已经安装了Python)：

> 1. 打开命令行终端，切换路径到你希望安装NoneBot的目录下
> 2. 初始化虚拟环境(此处以venv为例，已经有虚拟环境的可以跳过此步骤)：python -m venv venv
> 3. 激活虚拟环境(如果已经激活可以跳过此步骤)：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）

部署步骤(默认你已经获取到了复读机的NoneBot插件)：

> 1. 命令行输入pip install nb-cli，回车运行命令
> 2. 再次输入nb create回车，创建一个项目
> 3. 选择simple模板
> 4. 给项目起个名字
> 5. 建议使用FastAPI驱动器
> 6. **至少必须选择OneBot V11适配器**
> 7. 输入Yes安装默认依赖
> 8. 输入Yes安装虚拟环境
> 9. 如果需要，可以选择内置插件，如echo
> 11. 在项目目录下，找到`.env`文件
> 12. 填写HOST(x.x.x.x)和PORT(数字)，并保存
> 13. 将复读机的NoneBot插件放入项目目录下（通常是`plugins`文件夹下）
> 14. 部署完成后，运行nb run

#### [`OpenAI SDK`](https://github.com/openai/openai-python)：一个基于Python的大模型对接SDK
安装步骤(默认你已经安装了Python)：

> 1. 打开命令行终端，切换路径到你希望安装OpenAI SDK的目录下
> 2. 初始化虚拟环境(此处以venv为例，已经有虚拟环境的可以跳过此步骤)：python -m venv venv
> 3. 激活虚拟环境(如果已经激活可以跳过此步骤)：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> 4. 输入命令pip install openai，回车运行命令

#### [`FastAPI`](https://fastapi.tiangolo.com/)：一个用于构建高性能、可扩展的API的Python框架
安装步骤(默认你已经安装了Python)：

> 1. 打开命令行终端，切换路径到你希望安装FastAPI的目录下
> 2. 初始化虚拟环境(此处以venv为例，已经有虚拟环境的可以跳过此步骤)：python -m venv venv
> 3. 激活虚拟环境(如果已经激活可以跳过此步骤)：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> 4. 输入命令pip install fastapi，回车运行命令

#### [`uvicorn`](https://www.uvicorn.org/)：一个基于ASGI的Python服务器，用于运行FastAPI应用
安装步骤(默认你已经安装了Python)：

> 1. 打开命令行终端，切换路径到你希望安装uvicorn的目录下
> 2. 初始化虚拟环境(此处以venv为例，已经有虚拟环境的可以跳过此步骤)：python -m venv venv
> 3. 激活虚拟环境(如果已经激活可以跳过此步骤)：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> 4. 输入命令pip install uvicorn，回车运行命令

#### [`NapCat`](https://napneko.github.io/guide/napcat): 一个用于处理QQ消息的OneBot适配器
安装步骤(此处默认选择Shell版安装方式)

> 1. 前往 NapCatQQ 的 release 页面 下载NapCat.Shell.zip解压
> 2. 确保QQ版本安装且最新
> 3. 双击目录下launcher.bat启动(如果是win10 则使用launcher-win10.bat)

配置步骤：

> 1. 启动后，扫码登陆NapCatQQ
> 2. 访问WebUI(http://127.0.0.1:xxxx/webui/?token=napcat)
> 3. 点击`网络配置`
> 4. 点击`新建`，选择`WebSocket客户端`
> 5. 打开`启用`，输入一个名称
> 6. 输入NoneBot配置时填写的`HOST`和`PORT`(格式：ws://`HOST`:`PORT`/onebot/v11/ws)
> 7. 输入token(如果你没改密码那么就填入`napcat`，否则需要填入你的密码)
> 8. 点击`保存`，等待连接成功

---

## 次级依赖

*默认你已经完成主要依赖的安装*

 - aiofiles
 - environs
 - python-multipart
 - loguru
 - orjson
 - uvicorn
 - markdown
 - imgkit

---

## 后端安装部署

#### 1. 初始化虚拟环境

> python -m venv venv
> venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> pip install -r requirements.txt
> 或可以使用脚本安装
> `setup.bat`（Windows）或`source setup.sh`（Linux）

#### 2. 创建环境变量文件

> 具体环境变量请参考[环境变量表](#环境变量表)内容

#### 3. 运行项目

> `run.bat`（Windows）或`source run.sh`（Linux）
---

## 环境变量表

| 环境变量 | 描述 | 是否必填 | 默认值(推荐值) |
| :---: | :---: | :---: | :---: |
| `HOST` | 服务监听的IP | *选填* | 0.0.0.0 |
| `PORT` | 服务监听端口 | *选填* | 8080 |
| `SAVE_CALL_LOG` | 运行时是否记录主API的调用日志 | *选填* | True |
| `VERSION` | 版本号 | *选填* | \*由代码自动生成 |
| `*API_KEY` | API_Key (具体变量名由`API_INFO_FILE_PATH`指向 文件中`ApiKeyEnv`字段的名称) | **必填** | |
| `API_INFO_FILE_PATH` | API信息文件路径 | **必填** | `./config/apiconfig.json` |
| `CALL_LOG_FILE_PATH` | 主API调用日志的持久化存储文件 | **必填** | `./config/calllog.jsonl` |
| `DEFAULT_PROMPT_DIR` | 默认提示词文件夹 | *选填* | `./PresetsPrompt` |
| `PARSET_PROMPT_NAME` | 默认提示词文件名(不包括后缀) | *选填* | `default` |
| `README_FILE_PATH` | README文件位置 | *选填* | `./README.md` |
| `RENDERED_IMAGE_DIR` | 渲染图片的缓存位置 | **必填** | `./temp/render` |
| `STATIC_DIR` | 静态资源位置 | **必填** | `./static` |
| `USER_DATA_DIR` | 用户数据存放位置 | **必填** | `./data/userdata` |
| `USER_NICKNAME_MAPPING_FILE_PATH` | 用户昵称映射表文件位置 | *选填* | `./config/UserNicknameMapping.json` |
| `WEB_PATH` | 前端页面文件存放位置 | **必填** | `./web` |
| `TIMEZONE_OFFSET` | 默认时区偏移设置 | *选填* | `8` |
| `DEFAULT_TEMPERATURE` | 默认模型温度 | *选填* | `1.0` |
| `DEFAULT_TOP_P` | 默认模型`Top_P` | *选填* | `1.0` |
| `DEFAULT_FREQUENCY_PENALTY` | 默认模型频率惩罚 | *选填* | `0.0` |
| `DEFAULT_PRESENCE_PENALTY` | 默认模型存在惩罚 | *选填* | `0.0` |
| `DEFAULT_MAX_TOKENS` | 默认模型最大输出token<br/>(部分API不支持 `DEFAULT_MAX_COMPLETION_TOKENS`设置 提供此项以兼容) | *选填* | `1024` |
| `DEFAULT_MAX_COMPLETION_TOKENS` | 默认模型最大生成token | *选填* | `1024` |
| `DEFAULT_MODEL_TYPE` | 调用时默认使用的模型类型 | **必填** | `chat` |
| `WKHTMLTOPDF_PATH` | 渲染图片依赖的`Wkhtmltopdf`的位置 | **必填** | |
| `DEFAULT_OUTPUT_DPI` | 渲染图片输出的DPI | **必填** | `150` |
| `BOT_NAME` | 机器人名字 | **必填** |  |
| `BIRTHDAY_YEAR` | 机器人出生年份 | **必填** | `2024` |
| `BIRTHDAY_MONTH` | 机器人出生月份 | **必填** | `6` |
| `BIRTHDAY_DAY` | 机器人出生日期 | **必填** | `28` |

---

## 渲染样式

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

## 命令表

| 命令                       | 别名    | 全名                       | 功能描述                       | 参数描述                                  | 版本      | 命令版本 | 描述 |
| :---:                      | :---:  | :---:                      | :---:                         | :---:                                     | :---:    | :---:   | :---: |
| `chat`                     | `c`    | `Chat`                     | 与机器人对话                   | 自然语言输入                               | 4.0 Beta | 1.0     | 默认命令，可被`to_me`消息调起 |
| `keepAnswering`            | `ka`   | `KeepAnswering`            | 持续对话(常规)                 | 无                                        | 4.0 Beta | 1.0     | 无须输入，AI再次回复 |
| `keepReasoning`            | `kr`   | `KeepReasoning`            | 持续对话(推理)                 | 无                                        | 4.0 Beta | 1.0     | 无须输入，AI再次使用推理回复 |
| `renderChat`               | `rc`   | `RenderChat`               | 渲染Markdown回复               | 自然语言输入                               | 4.0 Beta | 1.0     | 强制渲染图片输出 |
| `setRenderStyle`           | `srs`  | `SetRenderStyle`           | 设置渲染样式                   | [渲染样式](#渲染样式)                       | 4.0 Beta | 1.0     | 设置Markdown图片渲染样式 |
| `npChat`                   | `np`   | `NoPromptChat`             | 不加载提示词进行对话            | 自然语言输入                               | 4.0 Beta | 1.0     | 使用常规模型 |
| `prover`                   | `p`    | `Prover`                   | 使用Prover模型进行数学形式化证明 | 自然语言输入                               | 4.0 Beta | 1.0     | 使用`Prover`模型 |
| `reason`                   | `r`    | `Reason`                   | 使用Reasoner模型进行推理        | 自然语言输入                               | 4.0 Beta | 1.0     | 使用`Reasoner`模型 |
| `recomplete`               | `rcm`  | `Recomplete`               | 重新进行对话补全                | 无                                        | 4.0 Beta | 1.0     | 重新生成 |
| `setFrequencyPenalty`      | `sfp`  | `SetFrequencyPenalty`      | 设置频率惩罚                   | `-2`\~`2`的浮点数 或`-200%`\~`200%`的百分比 | 4.0 Beta | 1.0     | 控制着模型输出重复相同内容的可能性 |
| `setPresencePenalty`       | `spp`  | `SetPresencePenalty`       | 设置存在惩罚                   | `-2`\~`2`的浮点数 或`-200%`\~`200%`的百分比 | 4.0 Beta | 1.0     | 控制着模型谈论新主题的可能性 |
| `setTemperature`           | `st`   | `SetTemperature`           | 设置温度                       | `0`\~`2`的浮点数 或`-100%`\~`100%`的百分比 | 4.0 Beta | 1.0     | 控制着模型生成内容的不确定性 |
| `setPrompt`                | `sp`   | `SetPrompt`                | 设置提示词                     | 自然语言输入                               | 4.0 Beta | 1.0     | 设置提示词 |
| `changeDefaultPersonality` | `cdp`  | `ChangeDefaultPersonality` | 修改默认人格                   | [人格预设](#人格预设)                       | 4.0 Beta | 1.0     | 修改默认人格路由 |
| `deletePrompt`             | `dp`   | `DeletePrompt`             | 删除提示词                     | 无                                        | 4.0 Beta | 1.0     | 删除提示词 |
| `deleteContext`            | `dc`   | `DeleteContext`            | 删除上下文                     | 无                                        | 4.0 Beta | 1.0     | 删除上下文 |
| `varExpand`                | `ve`   | `VarExpand`                | 变量展开                       | 文本模板(使用大括号作为[变量](#变量表)标记)  | 4.0 Beta | 1.0     | 变量展开 |
| `setDefaultModel`          | `sdm`  | `SetDefaultModel`          | 设置默认模型                   | [模型](#模型)                              | 4.0 Beta | 1.0     | 设置默认使用的模型 |
| `setTopP`                  | `stp`  | `SetTopP`                  | 设置Top_P参数                  | 0~1的浮点数 或`0%`~`100%`的百分比           | 4.0.1 Beta | 1.0   | 设置Top_P参数 |
| `setMaxTokens`             | `stm`  | `SetMaxTokens`             | 设置最大生成tokens数           | 0~4096的整数                               | 4.0.1 Beta | 1.0   | 设置最大生成tokens数 |
| `getContextTotalLength`    | `gctl` | `GetContextTotalLength`    | 获取上下文总长度               | 无                                         | 4.0.1 Beta | 1.0   | 获取上下文总长度     |
