import markdown
import imgkit
from environs import Env
from pathlib import Path
from .styles import STYLES

# 初始化环境变量
env = Env()

# 修改 markdown_to_image 函数
def markdown_to_image(
    markdown_text: str,
    output_path: str,
    width: int = 800,
    css: str = None,
    style: str = "light",
    options: dict = None
) -> str:
    """
    使用 wkhtmltoimage 将 Markdown 转为自适应图片
    
    参数:
    - markdown_text: Markdown 文本
    - output_path: 输出图片路径 (.png/.jpg)
    - width: 目标宽度 (像素)
    - css: 自定义 CSS 样式 (优先级高于style参数)
    - style: 预设样式名称 (light/dark/pink/blue/green)
    - options: wkhtmltoimage 高级选项
    
    返回: 输出文件路径
    """
    # 1. 渲染 Markdown 为 HTML
    html_content = markdown.markdown(markdown_text)
    
    # 2. 构建完整 HTML
    if css is None:
        # 使用预设样式
        css = STYLES.get(style, STYLES["light"])
    
    # 添加自适应宽度
    css += f"\nbody {{ width: {width - 60}px; }}"
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>{css}</style>
    </head>
    <body>{html_content}</body>
    </html>
    """
    
    # 3. 配置转换选项
    default_options = {
        'enable-local-file-access': None,  # 允许本地文件
        'encoding': "UTF-8",              # 编码设置
        'quiet': ''                       # 静默模式
    }
    if options:
        default_options.update(options)
    
    # 4. 转换并保存图片
    config = imgkit.config(wkhtmltoimage=env.str('WKHTMLTOPDF_PATH'))
    imgkit.from_string(
        string=full_html,
        output_path=output_path,
        config=config,
        options=default_options
    )
    
    return str(Path(output_path).resolve())

# 修改使用示例
if __name__ == "__main__":
    example_markdown = """
# 主题样式演示

## 代码块示例
```python
def greet(name):
    print(f"Hello, {name}!")

greet("World")
```

## 列表示例
- 项目 1
- 项目 2
- 项目 3

## 引用
> 这是优雅的引用样式

## 表格
| 姓名   | 年龄 | 职业    |
|--------|------|---------|
| Alice  | 28   | 工程师  |
| Bob    | 32   | 设计师  |
    """
    
    # 生成所有样式示例
    for style_name in ["light", "dark", "pink", "blue", "green"]:
        output_file = markdown_to_image(
            markdown_text=example_markdown,
            output_path=f"output_{style_name}.png",
            width=800,
            style=style_name
        )
        print(f"生成 {style_name} 主题: {output_file}")