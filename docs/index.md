# 详细配置

下面，请您按照您的需求查阅详细配置文档

---

## 环境变量

[环境变量表](./envs.md)

---

## 配置文件

- [Main Config](./configs/main.md)
- [Blacklist](./configs/blacklist.md)
- [User_Nickname_Mapping](./configs/uer_nickname_mapping.md)

用于管理程序的运行行为
以及模型资源等内容

---

## 用户配置

请参阅：[用户配置](./configs/user_config.md).
注：用户配置不属于部署配置
这个部分只有你需要为其进行 Client 开发时才需要用到

---

## Repeater API

请参阅：[Repeater API](./api_table/index.md)
如果你正在使用已经开发好的 Client
那么这个章节就不是给你准备的

---

## Markdown图片渲染

- [Markdown图片渲染模板](./markdown_render/template.md)
- [Markdown图片渲染样式](./markdown_render/style.md)

---

## Tool Calls

请参阅：[Tool Calls](./tool_calls/index.md)

---

## Prompt

该项目在 [`repeater-static-data/prompt/presets/official`](https://github.com/repeater-bot/repeater-static-data/tree/main/prompt/presets/official) 中
提供了多个预设的Prompt
通常你可以用这些文件作为模板

---

## 模板展开系统

项目中提供了模板展开系统
用于对提示词模板和用户输入模板进行变量展开
充分利用好模板展开器，可以实现很多有趣的功能
详情请参阅：[模板展开系统](./template_engine/main.md)

---

## 多模态输入

在 `/generate/chat/completion` 端点下面
传入 `additional_data` 即可让后端构造多模态请求
但需要保证目标模型支持你请求的模态输入
目前图像视觉模态的支持会更多一些
而其他模态则相对来说可能支持的比较少

---

## 版本号规则

请参阅：[版本号系统](./version.md)
你需要确保 Client 支持当前 Repeater 的版本
否则可能会出现接口不兼容的问题

## 微服务生态组件适配

请参阅：[微服务生态组件适配](./microservices_adapters_version.md)

## 静态资源

在 Repeater 中，静态资源分为 `主机数据` 和 `资源服务器数据`
`主机数据` 默认存放在 Repeater 的 `./static` 目录中
`资源服务器数据` 则需要部署[资源服务器](https://github.com/qeggs-dev/static-resources-server)
并让 Repeater 访问资源服务器的数据
**注意：静态资源本身并不与服务器属于一个仓库**
**需要从[静态资源存储库](https://github.com/qeggs-dev/repeater-static-data)中下载静态资源**

也将资源放在 Repeater 主机的 `./static` 目录中
Repeater 内置了一个简单的静态资源服务器
只不过你需要在配置资源基础路径时需要在前面加上 `/static`