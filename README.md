<div align="center">

# @复读机Repeater

**- Only Chat, Focus Chat. -**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-63b9ff.svg)](https://opensource.org/licenses/MIT) [![Model Protocol](https://img.shields.io/badge/Model%20Protocol-OpenAI%20Completions%20API-brightgreen.svg)](https://platform.openai.com/docs/overview)

</div>

---

一个主要基于 [`OpenAI SDK`](https://pypi.org/project/openai/) 开发的聊天机器人中间件
将状态管理封装到API中，以提供带状态的接口服务，降低对接成本

目前，复读机具有以下特点：

 - 平行数据管理：支持平行数据管理，用户可以随意切换平行数据，减少数据丢失的风险
 - 多模型支持：支持 OpenAI 接口的对话模型即可调用，可以根据需要选择不同的模型进行对话
 - 更高自由度：用户可以自定义会话注入、切换、删除，以及自定义提示词和模型参数
 - MD图片渲染：可以将回复以图片的形式渲染发送，减少对正常聊天的干扰
 - 用户自治设计：用户可以自己管理自己的所有用户数据
 - 多预设人设：复读机支持多预设人设，用户可以自由选择自己喜欢的人设进行对话

拟人化并非复读机的赛道，复读机不对拟人化需求做过多保证，如有需要请自行引导或编写提示词。

---

## 注意事项:

 - 使用者需确认生成内容的合法性，并自行承担使用本服务可能产生的风险。
 - 如果你觉得这个 Bot 非常好用，请去看一下 [`Deepseek`](https://www.deepseek.com/) 的官网吧，这个 Bot 最初就是基于他们的模型API文档开发的。( OpenAI 兼容就是省事啊~)
 - 机器人本体是免费的，开发者不承担使用时的 API 费用，还请注意。

---

## License

这个项目基于 [MIT License](LICENSE) 发布。

---

### 依赖项:

| Name              | Version  | License                              | License Link                                                                        | Where it is used                    | Reasons                               |
|-------------------|----------|--------------------------------------|-------------------------------------------------------------------------------------|-------------------------------------|---------------------------------------|
| Markdown          | 3.10.2   | BSD 3-Clause License                 | [BSD-3-Clause](https://github.com/Python-Markdown/markdown/blob/master/LICENSE.md)  | `core.markdown`                     | Parses Markdown text into HTML        |
| pyyaml            | 6.0.3    | MIT License                          | [MIT](https://github.com/yaml/pyyaml/blob/main/LICENSE)                             | `core.api` & `core.global_config_manager` | Read configuration file         |
| aiofiles          | 25.1.0   | Apache Software License              | [Apache-2.0](https://github.com/Tinche/aiofiles/blob/main/LICENSE)                  | `core.data_manager`                 | Asynchronous file support             |
| environs          | 14.5.0   | MIT License                          | [MIT](https://github.com/sloria/environs/blob/main/LICENSE)                         | `run_repeater.py` & `core.global_config_manager` | Support for environment variables |
| fastapi           | 0.129.0  | MIT License                          | [MIT](https://github.com/fastapi/fastapi/blob/master/LICENSE)                       | `core.api`                          | Build API                             |
| httpx             | 0.28.1   | BSD License                          | [BSD-3-Clause](https://github.com/encode/httpx/blob/master/LICENSE.md)              | *Entire Project*                    | Asynchronous HTTP client              |
| loguru            | 0.7.3    | MIT License                          | [MIT](https://github.com/Delgan/loguru/blob/master/LICENSE)                         | *Entire Project*                    | Logging                               |
| openai            | 2.21.0   | Apache Software License              | [Apache-2.0](https://github.com/openai/openai-python/blob/main/LICENSE)             | `core.call_api`                     | Call the OpenAI API                   |
| orjson            | 3.11.7   | MPL-2.0 AND (Apache-2.0 OR MIT)      | [Apache-2.0](https://github.com/ijl/orjson/blob/master/LICENSE-APACHE) / [MIT](https://github.com/ijl/orjson/blob/master/LICENSE-MIT) / [MPL-2.0](https://github.com/ijl/orjson/blob/master/LICENSE-MPL-2.0) | `core.DataManager` & `API`        | High-performance JSON  resolution |
| pydantic          | 2.11.7   | MIT License                          | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE)                       | `core.global_config_manager` & `core.api` | Simple and convenient data validation |
| python-multipart  | 0.0.22   | Apache-2.0                           | [Apache-2.0](https://github.com/Kludex/python-multipart/blob/master/LICENSE.txt)    | `core.data_manager` & `core.api`    | Support for form data                 |
| uvicorn           | 0.40.0   | BSD License                          | [BSD-3-Clause](https://github.com/Kludex/uvicorn/blob/main/LICENSE.md)              | `run_repeater.py`                   | Run FastAPI                           |
| numpy             | 2.4.2    | BSD License                          | [BSD-3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt)                | *Entire Project*                    | Speed up batch computing of data      |
| python-box        | 7.3.2    | MIT License                          | [MIT](https://github.com/cdgriffith/Box/blob/master/LICENSE)                        | `core.global_config_manager`        | Mixed configuration files             |
| jinja2            | 3.1.6    | BSD-3-Clause license                 | [BSD-3-Clause](https://github.com/pallets/jinja/blob/main/LICENSE.txt)              | `core.text_template_processer`      | Render text templates                 |
| tzdata            | 2025.3   | Apache-2.0                           | [Apache-2.0](https://github.com/python/tzdata/blob/master/LICENSE)                  | `core.text_template_processer`      | Get timezone information              |
| yarl              | 1.23.0   | MIT License                          | [MIT](https://github.com/aio-libs/yarl/blob/master/LICENSE)                         | *Entire Project*                    | URL parsing                           |
| bleach            | 6.3.0    | Apache-2.0                           | [Apache-2.0](https://github.com/mozilla/bleach/blob/main/LICENSE)                   | `core.markdown_render`              | Clean HTML                            |
| asteval           | 1.0.8    | MIT License                          | [MIT](https://github.com/newville/asteval/blob/main/LICENSE)                        | `core.model_requester.tools`        | Assist AI in performing mathematical calculations. |
| pip-requirements-parser | 32.0.1 | MIT License                      | [MIT](https://github.com/jazzband/pip-requirements-parser/blob/main/LICENSE)        | `core.requirements_version_checker` | Parse requirements.txt files.         |
| jsonpatch         | 1.33     | BSD-3-Clause license                 | [BSD-3-Clause license](https://github.com/stefankoegl/python-json-patch/blob/master/LICENSE) | `core.data_manager`        | JSON Diff & Patch                     |
| pythonping        | 1.1.4    | MIT License                          | [MIT](https://github.com/alessandromaggio/pythonping/blob/main/LICENSE)             | `core.api`                          | Checking network connectivity         |
| cachetools        | 7.1.4    | MIT License                          | [MIT](https://github.com/tkem/cachetools/blob/master/LICENSE)                       | *Entire Project*                    | Cachetools is a caching library for Python |

具体依赖的License请查看[LICENSES](./LICENSES/index.md)

---

## 安装部署

**使用 Python3.11 及以上版本安装**
> Repeater 使用了 Python3.11 的一些新特性
> 请在部署时确保你的 Python 版本符合要求

### 自动安装

1. 将项目克隆到本地
2. 进入项目目录
5. 运行 `run.py` 启动器 (该项目的详情请查看 [Sloves_Starter](https://github.com/qeggs-dev/Sloves_Starter))

### 手动安装

1. 将项目克隆到本地
2. 进入项目目录
3. 执行 `python3 -m venv .venv` 创建虚拟环境
4. 执行 `.venv/bin/activate` 激活虚拟环境 (Windows下则是 `.venv\Scripts\activate` )
5. 执行 `pip install -r requirements.txt` 安装依赖
6. 执行 `python3 run_repeater.py` 启动服务

PS: `run.py` 启动器会在完成所有操作后启动主程序，而这只需要你保证你的配置正确

并且每一次你都可以通过启动器来启动程序

---

## 跨平台

本项目并未在项目中加入平台强相关逻辑
经过测试，Repeater可以在 Windows、Linux 上正常运行
启动器也根据平台特性做了适配
暂未测试过 MacOS (因为没钱买Mac)

---

## 详细文档

[从这里开始使用 Repeater!](./docs/index.md)

---

## 功能拓展

Repeater 的功能拓展主要靠编写对应领域的 Client
比如，你可以使用 Repeater 的 API 来制作一个每天自动写日记的 Client
或者，将其接入到其他地方，以减少手动维护状态的成本

---

## 项目设计

> 这个项目在最初只是为了给 Bot 添加方便的有状态 AI API
> 后面逐渐发现，这个项目其实可以独立出去，作为一个单独的项目使用
> 设计理念上，Repeater 希望用户能完全掌握自己的数据 (别把锅甩运营头上)
> Repeater 并不主动的把目标放在拟人化上，工具的行为越清晰，用户越能对工具放心
> 它希望在有人与它进行交流时，能时刻想起自己可以对自己才是有控制权的那方
> (我才不会告诉你是因为我不会写拟人化才走的这条路呢)

---

## 相关仓库

[Sloves_Starter](https://github.com/qeggs-dev/Sloves_Starter)
[Repeater Nexus](https://github.com/repeater-bot/repeater-nexus)
[Repeater Modelinfo Server](https://github.com/repeater-bot/repeater-modelinfo-server)
[Static Resources Server](https://github.com/repeater-bot/static-resources-server)