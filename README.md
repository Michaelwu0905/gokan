# Japanese Learning Assistant

一个跨平台桌面端日语学习辅助工具，采用 Electron + FastAPI 双进程架构。

## 功能特性

- 🔥 全局快捷键唤醒截图
- 📸 屏幕区域选择
- 🤖 AI 驱动的日语文本识别、翻译和语法分析
- 📝 平假名注音、语法拆解、例句展示
- 🎨 现代化悬浮卡片 UI

## 技术栈

- **前端**: Electron, Node.js, HTML/CSS/JS
- **后端**: Python 3.10+, FastAPI, Uvicorn
- **AI**: OpenAI Vision API (兼容格式)
- **项目管理**: uv

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd japanese-learning-assistant
```

### 2. 安装 Python 依赖

```bash
# 安装 uv（如果还没有）
pip install uv

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

uv pip install -e .
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置你的 OpenAI API Key
```

### 4. 启动后端服务（测试）

```bash
python -m backend.main
```

### 5. 启动 Electron 应用

```bash
cd frontend
npm install
npm start
```

## 开发

### 项目结构

```
japanese-learning-assistant/
├── backend/              # Python FastAPI 后端
│   ├── __init__.py
│   ├── main.py          # FastAPI 入口
│   ├── models.py        # Pydantic 数据模型
│   └── ai_service.py    # AI 服务
├── frontend/            # Electron 前端
│   ├── main.js         # 主进程
│   ├── preload.js      # 预加载脚本
│   ├── capture.html    # 截图窗口
│   └── result.html     # 结果窗口
├── pyproject.toml       # Python 项目配置
└── .env.example        # 环境变量示例
```

## 许可证

MIT
