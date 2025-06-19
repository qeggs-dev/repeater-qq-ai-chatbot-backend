@echo off

:: 检查是否安装了 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python 未安装，请先安装 Python。
    pause
    exit /b 1
)

:: 创建虚拟环境
echo 创建虚拟环境...
python -m venv .venv

:: 激活虚拟环境并安装依赖
echo 激活虚拟环境并安装依赖...
call .venv\Scripts\activate.bat
pip install -r requirements.txt

echo 环境配置完成！运行以下命令启动：
echo run.bat
pause