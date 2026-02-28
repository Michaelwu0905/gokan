# 語感（Gokan）MVP

AI驱动的日语口语练习App MVP版本。

## 技术栈

- **后端**: FastAPI + SQLite + uv
- **前端**: React + Vite + React Router

## 项目结构

```
gokan/
├── backend/                 # FastAPI 后端
│   ├── src/gokan_backend/   # 后端源码
│   │   ├── main.py         # FastAPI 主应用
│   │   ├── database.py     # 数据库配置
│   │   ├── models.py       # SQLAlchemy 模型
│   │   ├── schemas.py      # Pydantic 模型
│   │   └── ai_service.py   # 虚拟 AI 服务
│   └── pyproject.toml      # uv 项目配置
│
└── frontend/               # React 前端
    ├── src/
    │   ├── pages/          # 页面组件
    │   │   ├── Scenarios.jsx   # 场景选择
    │   │   ├── Chat.jsx        # 对话界面
    │   │   ├── Summary.jsx     # 练习总结
    │   │   └── Stats.jsx       # 学习档案
    │   ├── api.js          # API 客户端
    │   ├── App.jsx         # 主应用
    │   └── App.css         # 全局样式
    └── package.json
```

## 快速开始

### 1. 配置 API Keys（可选）

#### 🇨🇳 中国用户推荐（国内网络友好）

```bash
cd backend
cp .env.example .env
# 编辑 .env 填入以下配置
```

**核心配置（无需翻墙）:**
- **Moonshot Kimi** (AI对话): https://platform.moonshot.cn/
- **阿里云 NLS** (语音服务): https://www.aliyun.com/product/nls

阿里云语音服务优势:
- ✅ 国内网络直连，速度快
- ✅ 语音识别 + 语音合成一体化
- ✅ 每月 **50 万次免费调用额度**
- ✅ 支持日语语音合成

#### 🌍 国外用户

- **Moonshot Kimi** (AI对话)
- **OpenAI Whisper** (语音转文字)
- **Azure TTS** (语音合成)

#### ⚪ 虚拟模式

如果不配置 API Keys，系统会使用虚拟模式（模拟数据），适合开发和测试。

**详细配置说明见 [backend/README.md](backend/README.md)**

### 2. 启动后端服务

**方式1: 使用启动脚本（推荐）**
```bash
cd backend
./start.sh
```

**方式2: 手动启动**
```bash
cd backend
uv run uvicorn gokan_backend.main:app --host 0.0.0.0 --port 8000 --reload
```

后端将在 http://localhost:8000 运行  
API 文档: http://localhost:8000/docs

### 3. 启动前端服务

```bash
cd frontend
npm run dev
```

前端将在 http://localhost:5173 运行

## 核心功能

✅ **10个预设场景**: 便利店、自我介绍、餐厅、问路、酒店、医院、银行、理发店、超市、邮局
✅ **虚拟AI对话**: 基于规则的模拟回复
✅ **智能纠错**: 助词错误检测（演示用）
✅ **学习档案**: 练习统计和错误分析
✅ **微信式聊天界面**: 简洁友好的UI

## API 端点

- `GET /` - 欢迎信息
- `GET /scenarios` - 获取所有场景
- `POST /sessions` - 创建对话会话
- `GET /sessions/{id}` - 获取会话详情
- `POST /sessions/{id}/messages` - 发送消息
- `GET /sessions/{id}/summary` - 获取练习总结
- `GET /stats` - 获取学习统计

## 设计特点

- **温暖配色**: 紫色渐变，减少学习焦虑
- **拟声词加载**: "ふむふむ"思考中
- **核心词汇提示**: 每个场景提供3-5个关键词
- **气泡式对话**: 类似微信的聊天体验
