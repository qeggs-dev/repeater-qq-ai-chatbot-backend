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
 - 本服务由一位 未成年学生 自已一人与 AI 协作开发，公益性质，如果你愿意捐赠，可以在机器人的**QQ空间**中找到赞赏码以支持项目运营(或是支持开发者)。
 - 项目服务仅作为实验性质运行，不保证服务稳定性。
 - 项目随时可能会因为开发者个人原因，或API额度耗尽而被迫中止。
 - 仅供学习和非商业用途。使用者需确认生成内容的合法性，并自行承担使用本服务可能产生的风险。
 - 如果你觉得这个Bot非常好用，请去看一下[`Deepseek`](https://www.deepseek.com/)他们的官网吧，这个Bot是基于他们的API开发的。

---

## 主要依赖
#### [`NoneBot`](https://nonebot.dev/)：一个基于Python的异步OneBot框架
安装步骤(默认你已经安装了Python)：

> 1. 打开命令行终端，切换路径到你希望安装NoneBot的目录下
> 2. 初始化虚拟环境(此处以venv为例)：python -m venv venv
> 3. 激活虚拟环境：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> 4. 命令行输入pip install nb-cli，回车运行命令
> 5. 再次输入nb create回车，创建一个项目
> 6. 选择simple模板
> 7. 给项目起个名字
> 8. 建议使用FastAPI驱动器
> 9.  至少必须选择OneBot V11适配器
> 10. 输入Yes安装默认依赖
> 11. 输入Yes安装虚拟环境
> 12. 如果需要，可以选择内置插件，如echo
> 14. 部署完成后，运行nb run

#### [`OpenAI SDK`](https://github.com/openai/openai-python)：一个基于Python的大模型对接SDK
安装步骤(默认你已经安装了Python)：

> 1. 打开命令行终端，切换路径到你希望安装OpenAI SDK的目录下
> 2. 初始化虚拟环境(此处以venv为例)：python -m venv venv
> 3. 激活虚拟环境：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> 4. 输入命令pip install openai，回车运行命令

#### [`FastAPI`](https://fastapi.tiangolo.com/)：一个用于构建高性能、可扩展的API的Python框架
安装步骤(默认你已经安装了Python)：

> 1. 打开命令行终端，切换路径到你希望安装FastAPI的目录下
> 2. 初始化虚拟环境(此处以venv为例)：python -m venv venv
> 3. 激活虚拟环境：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> 4. 输入命令pip install fastapi，回车运行命令
#### [`uvicorn`](https://www.uvicorn.org/)：一个基于ASGI的Python服务器，用于运行FastAPI应用
安装步骤(默认你已经安装了Python)：

> 1. 打开命令行终端，切换路径到你希望安装uvicorn的目录下
> 2. 初始化虚拟环境(此处以venv为例)：python -m venv venv
> 3. 激活虚拟环境：venv\Scripts\activate（Windows）或source venv/bin/activate（Linux）
> 4. 输入命令pip install uvicorn，回车运行命令

#### [`NapCat`](https://napneko.github.io/guide/napcat): 一个用于处理QQ消息的OneBot适配器
安装步骤(此处默认选择Shell版安装方式)

> 1. 前往 NapCatQQ 的 release 页面 下载NapCat.Shell.zip解压
> 2. 确保QQ版本安装且最新
> 3. 双击目录下launcher.bat启动(如果是win10 则使用launcher-win10.bat)

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

## pip依赖安装

安装命令：
> pip install -r requirements.txt

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

## 命令表

| 命令                       | 别名   | 全名                       | 功能描述                       | 参数描述                                  | 版本      | 命令版本 | 描述 |
| :---:                      | :---: | :---:                      | :---:                         | :---:                                     | :---:    | :---:   | :---: |
| `chat`                     | `c`   | `Chat`                     | 与机器人对话                   | 自然语言输入                               | 4.0 Beta | 1.0     | 默认命令，可被to_me消息调起 |
| `keepAnswering`            | `ka`  | `KeepAnswering`            | 持续对话(常规)                 | 无                                        | 4.0 Beta | 1.0     | 无须输入，AI再次回复 |
| `keepReasoning`            | `kr`  | `KeepReasoning`            | 持续对话(推理)                 | 无                                        | 4.0 Beta | 1.0     | 无须输入，AI再次使用推理回复 |
| `renderChat`               | `rc`  | `RenderChat`               | 渲染Markdown回复               | 自然语言输入                               | 4.0 Beta | 1.0     | 强制渲染图片输出 |
| `setRenderStyle`           | `srs` | `SetRenderStyle`           | 设置渲染样式                   | [渲染样式](#渲染样式)                       | 4.0 Beta | 1.0     | 设置Markdown图片渲染样式 |
| `npChat`                   | `np`  | `NoPromptChat`             | 不加载提示词进行对话            | 自然语言输入                               | 4.0 Beta | 1.0     | 使用常规模型 |
| `prover`                   | `p`   | `Prover`                   | 使用Prover模型进行数学形式化证明 | 自然语言输入                               | 4.0 Beta | 1.0     | 使用Prover模型 |
| `reason`                   | `r`   | `Reason`                   | 使用Reasoner模型进行推理        | 自然语言输入                               | 4.0 Beta | 1.0     | 使用Reasoner模型 |
| `recomplete`               | `rcm` | `Recomplete`               | 重新进行对话补全                | 无                                        | 4.0 Beta | 1.0     | 重新生成 |
| `setFrequencyPenalty`      | `sfp` | `SetFrequencyPenalty`      | 设置频率惩罚                   | `-2`\~`2`的浮点数 或`-200%`\~`200%`的百分比 | 4.0 Beta | 1.0     | 控制着模型输出重复相同内容的可能性 |
| `setPresencePenalty`       | `spp` | `SetPresencePenalty`       | 设置存在惩罚                   | `-2`\~`2`的浮点数 或`-200%`\~`200%`的百分比 | 4.0 Beta | 1.0     | 控制着模型谈论新主题的可能性 |
| `setTemperature`           | `st`  | `SetTemperature`           | 设置温度                       | `0`\~`2`的浮点数 或`-100%`\~`100%`的百分比 | 4.0 Beta | 1.0     | 控制着模型生成内容的不确定性 |
| `setPrompt`                | `sp`  | `SetPrompt`                | 设置提示词                     | 自然语言输入                               | 4.0 Beta | 1.0     | 设置提示词 |
| `changeDefaultPersonality` | `cdp` | `ChangeDefaultPersonality` | 修改默认人格                   | [人格预设](#人格预设)                       | 4.0 Beta | 1.0     | 修改默认人格路由 |
| `deletePrompt`             | `dp`  | `DeletePrompt`             | 删除提示词                     | 无                                        | 4.0 Beta | 1.0     | 删除提示词 |
| `deleteContext`            | `dc`  | `DeleteContext`            | 删除上下文                     | 无                                        | 4.0 Beta | 1.0     | 删除上下文 |
| `varExpand`                | `ve`  | `VarExpand`                | 变量展开                       | 文本模板(使用大括号作为变量标记)            | 4.0 Beta | 1.0     | 变量展开 |
