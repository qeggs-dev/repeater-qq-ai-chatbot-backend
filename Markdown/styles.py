# md_styles.py
# Markdown 渲染样式预设 - 纯色主题

LIGHT_THEME = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: #ffffff;
    color: #333333;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    line-height: 1.7;
}

h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    margin-top: 1.2em;
    margin-bottom: 0.6em;
    font-weight: 600;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.3em;
}

a {
    color: #3498db;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

code {
    background-color: #f8f9fa;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}

pre {
    background-color: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
    overflow: auto;
    border-left: 4px solid #3498db;
}

blockquote {
    background-color: #f9f9f9;
    border-left: 4px solid #ddd;
    padding: 12px 20px;
    margin: 0;
    color: #555;
}

ul, ol {
    padding-left: 28px;
}

li {
    margin-bottom: 8px;
}

img {
    max-width: 100%;
    border-radius: 6px;
    margin: 10px 0;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}

th, td {
    border: 1px solid #e1e4e8;
    padding: 12px 15px;
    text-align: left;
}

th {
    background-color: #f6f8fa;
    font-weight: 600;
}

hr {
    border: 0;
    height: 1px;
    background: #e1e4e8;
    margin: 30px 0;
}
"""

DARK_THEME = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: #1e1e2e;
    color: #e0e0e0;
    padding: 30px;
    border-radius: 12px;
    line-height: 1.7;
}

h1, h2, h3, h4, h5, h6 {
    color: #bb86fc;
    margin-top: 1.2em;
    margin-bottom: 0.6em;
    font-weight: 600;
    border-bottom: 1px solid #44475a;
}

a {
    color: #64b5f6;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

code {
    background-color: #2d2d3d;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}

pre {
    background-color: #2d2d3d;
    padding: 16px;
    border-radius: 8px;
    overflow: auto;
    border-left: 4px solid #bb86fc;
}

blockquote {
    background-color: #252536;
    border-left: 4px solid #44475a;
    padding: 12px 20px;
    margin: 0;
    color: #b0b0c0;
}

ul, ol {
    padding-left: 28px;
}

li {
    margin-bottom: 8px;
}

img {
    max-width: 100%;
    border-radius: 6px;
    margin: 10px 0;
    filter: brightness(0.9);
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}

th, td {
    border: 1px solid #44475a;
    padding: 12px 15px;
    text-align: left;
}

th {
    background-color: #2d2d3d;
    font-weight: 600;
}

hr {
    border: 0;
    height: 1px;
    background: #44475a;
    margin: 30px 0;
}
"""

# 纯色主题
PINK_THEME = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: #fff0f5;
    color: #5a1a37;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    line-height: 1.7;
}

h1, h2, h3, h4, h5, h6 {
    color: #8a1c4a;
    margin-top: 1.2em;
    margin-bottom: 0.6em;
    font-weight: 600;
    border-bottom: 1px solid #ffd1dc;
}

a {
    color: #d81b60;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

code {
    background-color: #ffeef4;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}

pre {
    background-color: #ffeef4;
    padding: 16px;
    border-radius: 8px;
    overflow: auto;
    border-left: 4px solid #ff9ebd;
}

blockquote {
    background-color: #ffeef4;
    border-left: 4px solid #ff9ebd;
    padding: 12px 20px;
    margin: 0;
    color: #7a2a4c;
}

ul, ol {
    padding-left: 28px;
}

li {
    margin-bottom: 8px;
}

img {
    max-width: 100%;
    border-radius: 6px;
    margin: 10px 0;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}

th, td {
    border: 1px solid #ffd1dc;
    padding: 12px 15px;
    text-align: left;
}

th {
    background-color: #ffeef4;
    font-weight: 600;
}

hr {
    border: 0;
    height: 1px;
    background: #ffd1dc;
    margin: 30px 0;
}
"""

BLUE_THEME = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: #f0f8ff;
    color: #0d3b66;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    line-height: 1.7;
}

h1, h2, h3, h4, h5, h6 {
    color: #1a508b;
    margin-top: 1.2em;
    margin-bottom: 0.6em;
    font-weight: 600;
    border-bottom: 1px solid #c2e0ff;
}

a {
    color: #1e88e5;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

code {
    background-color: #e3f2fd;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}

pre {
    background-color: #e3f2fd;
    padding: 16px;
    border-radius: 8px;
    overflow: auto;
    border-left: 4px solid #90caf9;
}

blockquote {
    background-color: #e3f2fd;
    border-left: 4px solid #90caf9;
    padding: 12px 20px;
    margin: 0;
    color: #1a508b;
}

ul, ol {
    padding-left: 28px;
}

li {
    margin-bottom: 8px;
}

img {
    max-width: 100%;
    border-radius: 6px;
    margin: 10px 0;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}

th, td {
    border: 1px solid #bbdefb;
    padding: 12px 15px;
    text-align: left;
}

th {
    background-color: #e3f2fd;
    font-weight: 600;
}

hr {
    border: 0;
    height: 1px;
    background: #bbdefb;
    margin: 30px 0;
}
"""

GREEN_THEME = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: #f0fff4;
    color: #1d3c34;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    line-height: 1.7;
}

h1, h2, h3, h4, h5, h6 {
    color: #1a5d38;
    margin-top: 1.2em;
    margin-bottom: 0.6em;
    font-weight: 600;
    border-bottom: 1px solid #c6f6d5;
}

a {
    color: #2e7d32;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

code {
    background-color: #e6ffed;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}

pre {
    background-color: #e6ffed;
    padding: 16px;
    border-radius: 8px;
    overflow: auto;
    border-left: 4px solid #81c995;
}

blockquote {
    background-color: #e6ffed;
    border-left: 4px solid #81c995;
    padding: 12px 20px;
    margin: 0;
    color: #1a5d38;
}

ul, ol {
    padding-left: 28px;
}

li {
    margin-bottom: 8px;
}

img {
    max-width: 100%;
    border-radius: 6px;
    margin: 10px 0;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}

th, td {
    border: 1px solid #a7f3d0;
    padding: 12px 15px;
    text-align: left;
}

th {
    background-color: #e6ffed;
    font-weight: 600;
}

hr {
    border: 0;
    height: 1px;
    background: #a7f3d0;
    margin: 30px 0;
}
"""

# 所有样式集合
STYLES = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
    "pink": PINK_THEME,
    "blue": BLUE_THEME,
    "green": GREEN_THEME
}