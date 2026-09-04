# Markdown图片渲染样式

当 Repeater 想要将 Markdown 渲染成图片时
可以通过配置对使用的 CSS 进行路由
在全局配置中，这个字段是 `render.markdown.default_style`
在用户配置中，这个字段是 `render_style`
用户配置总会优先使用
而在用户配置未定义的情况下
会使用全局配置进行兜底
实际文件请查看：[https://github.com/repeater-bot/repeater-static-data/tree/main/styles](https://github.com/repeater-bot/repeater-static-data/tree/main/styles)
啊因为我不会写前端，所以此处的所有 CSS 其实全是由AI生成的
如果你不喜欢，可以不将其放在资源服务器中，而是自己手动编写