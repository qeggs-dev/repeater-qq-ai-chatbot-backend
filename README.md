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

## 次级依赖：
*(默认你已经完成主要依赖的安装，且已经学会了如何使用pip安装依赖)*

 - aiofiles
 - environs
 - python-multipart
 - loguru
 - orjson
 - uvicorn
 - markdown
 - imgkit

---

## <span id="render-style">渲染风格</span>
| 风格 | 译名 |
| :---: | :---: |
| **`light`** | 亮色 |
| `dark` | 暗色 |
| `pink` | 粉色 |
| `blue` | 蓝色 |
| `green` | 绿色 |

---

## 命令

### > 对话补全

####  - **Chat** -
> 默认AI自然语言对话补全命令
> ```plaintext
> @复读机 /chat <对话内容>
> ```
> 此命令也是默认命令，可以直接被`to_me`调起使用
> ```plaintext
> @复读机 <对话内容>
> ```
> 调用后复读机应该就可以回复你的消息了
> **注：在群聊中，使用`to_me`会渲染为图片回复，而`/chat`则就强制纯文本回复(仅限200字以内)**

#### - **Reason**
> 默认AI推理补全命令
> ```plaintext
> @复读机 /reason <推理内容>
> ```
> 调用后复读机就可以使用推理模型回复你的内容了
> **注：此命令无论何时，都会渲染为图片回复**

#### - **Prover**
>  默认AI证明模型补全命令
>  ```plaintext
> @复读机 /prover <自然语言命题描述>
> ```
> 调用后复读机就可以使用推理模型回复你的内容了
> **注：此命令无论何时，都会渲染为图片回复，且不加载任何提示词**
> **该模型是专业模型，在日常使用中可能不会有较强表现**

#### - **KeepAnswering**
> 让AI再次回复内容
>  ```plaintext
> @复读机 /keep <对话内容>
> ```
> **在群聊中，此命令会渲染为图片回复**

#### - **DeleteContext(dc)**
> 清除当前对话上下文
> ```plaintext
> @复读机 /dc
> ```
> **注：每个用户仅能清除自己的上下文**

### > 配置设置

#### - **SetRenderStyle(srs)**
> 设置渲染风格
> ```plaintext
> @复读机 /srs <渲染风格>
> ```
> **注：[渲染风格](#render-style)仅允许已经被定义的类型，否则会使用默认值**

#### - **SetFrequencyPenalty(sfp)**
> 设置频率惩罚
> ```plaintext
> @复读机 /sfp <频率惩罚>
> ```
> **注：频率惩罚仅允许-2~2之间的浮点数，否则会使用默认值0.0**

#### - **SetPresencePenalty(spp)**
> 设置存在惩罚
> ```plaintext
> @复读机 /spp <存在惩罚>
> ```
> **注：存在惩罚仅允许-2~2之间的浮点数，否则会使用默认值0.0**

#### - **SetTemperature(st)**
> 设置温度
> ```plaintext
> @复读机 /st <温度>
> ```
> **注：温度仅允许0~2之间的浮点数，否则会使用默认值1.0**
