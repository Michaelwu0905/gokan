#!/bin/bash

# 日语学习助手启动脚本

cd "$(dirname "$0")"

echo "🚀 启动日语沉浸式学习助手..."
echo ""

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: uv venv"
    exit 1
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查依赖
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 安装 Python 依赖..."
    uv pip install -e .
fi

echo ""
echo "📝 使用说明:"
echo "   快捷键: Command+Shift+X (Mac) / Ctrl+Alt+D (Windows/Linux)"
echo "   拖拽选择屏幕上的日语文本区域"
echo "   按 ESC 取消或关闭结果窗口"
echo ""

# 启动 Electron
cd frontend && npm start
