#!/bin/bash

# 检查是否安装了 Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python 3 未安装，请先安装 Python 3。"
    exit 1
fi

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv .venv

# 激活虚拟环境并安装依赖
echo "激活虚拟环境并安装依赖..."
source .venv/bin/activate
pip install -r requirements.txt

echo "环境配置完成！运行以下命令启动："
echo "./run.sh"