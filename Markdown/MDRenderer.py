import markdown
import imgkit
from environs import Env
from pathlib import Path

# 初始化环境变量
env = Env()
env.read_env()  # 读取 .env 文件

def markdown_to_image(
    markdown_text: str,
    output_path: str,
    width: int = 800,
    css: str = None,
    options: dict = None
) -> str:
    """
    使用 wkhtmltoimage 将 Markdown 转为自适应图片
    
    参数:
    - markdown_text: Markdown 文本
    - output_path: 输出图片路径 (.png/.jpg)
    - width: 目标宽度 (像素)
    - css: 自定义 CSS 样式
    - options: wkhtmltoimage 高级选项
    
    返回: 输出文件路径
    """
    # 1. 渲染 Markdown 为 HTML
    html_content = markdown.markdown(markdown_text)
    
    # 2. 构建完整 HTML
    if css is None:
        css = f"""
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            width: {width}px;
            padding: 20px;
            margin: 0 auto;
            line-height: 1.6;
            color: #333;
        }}
        pre {{
            background: #f8f8f8;
            padding: 1em;
            border-radius: 5px;
            overflow: auto;
        }}
        """
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>{css}</style>
    </head>
    <body>{html_content}</body>
    </html>
    """
    
    # 3. 配置转换选项
    default_options = {
        'enable-local-file-access': None,  # 允许本地文件
        # 'width': width,                 # 控制输出宽度
        # 'disable-smart-shrinking': None,  # 禁止自动缩放
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

# 使用示例
if __name__ == "__main__":
    example_markdown = """
    # 自适应 Markdown 渲染

    ![示例图片](https://via.placeholder.com/300x200)

    ```python
    def hello():
        print("代码高亮保留")
    ```

    - 列表项1
    - 列表项2

    > 引用内容也会正确适配
    """
    
    output_file = markdown_to_image(
        markdown_text=example_markdown,
        output_path="output_demo.png",
        width=600,
        css="""
        body {
            background-color: #f9f9f9;
            border: 1px solid #eee;
            border-radius: 5px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #eee;
        }
        """
    )
    
    print(f"图片已生成: {output_file}")