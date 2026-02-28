# Gokan Backend

Gokan 后端服务，支持真实 AI API 和虚拟模式。

## 快速开始

### 方式1: 使用启动脚本（推荐）

```bash
cd backend
./start.sh
```

脚本会自动检测 API Key 配置状态并启动服务。

### 方式2: 手动启动

```bash
cd backend
uv run uvicorn gokan_backend.main:app --reload
```

## 环境配置

### 1. 创建配置文件

复制 `.env.example` 到 `.env`:

```bash
cp .env.example .env
```

### 2. 获取 API Keys

编辑 `.env` 文件，填入以下 API Keys:

#### 🔑 Moonshot Kimi API (AI对话)

**注册地址:** https://platform.moonshot.cn/

**用途:** 日语对话生成、智能纠错

**配置项:**
```
MOONSHOT_API_KEY=sk-your-key-here
```

**获取步骤:**
1. 访问 https://platform.moonshot.cn/ 注册账号
2. 创建 API Key
3. 复制到 `.env` 文件

---

#### 🔑 OpenAI API (语音转文字)

**注册地址:** https://platform.openai.com/

**用途:** Whisper 语音转文字

**配置项:**
```
OPENAI_API_KEY=sk-your-key-here
```

**获取步骤:**
1. 访问 https://platform.openai.com/ 注册账号
2. 进入 API 页面创建 API Key
3. 需要绑定支付方式（支持国内信用卡）
4. 复制到 `.env` 文件

---

#### 🔑 Azure TTS API (语音合成)

**注册地址:** https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/

**用途:** 日语语音合成

**配置项:**
```
AZURE_TTS_KEY=your-key-here
AZURE_TTS_REGION=japaneast
AZURE_TTS_VOICE=ja-JP-NanamiNeural
```

**获取步骤:**
1. 访问 Azure Portal (https://portal.azure.com/)
2. 创建 "Speech Service" 资源
3. 选择地区: Japan East (支持日语)
4. 在 "Keys and Endpoint" 页面获取 Key
5. 复制到 `.env` 文件

**支持的日语声音:**
- `ja-JP-NanamiNeural` (女声，默认)
- `ja-JP-KeitaNeural` (男声)

---

### 3. 配置完成后的 `.env` 示例

```bash
# Moonshot Kimi API
MOONSHOT_API_KEY=sk-moonshot-your-key-here

# OpenAI API
OPENAI_API_KEY=sk-openai-your-key-here

# Azure TTS API
AZURE_TTS_KEY=your-azure-key-here
AZURE_TTS_REGION=japaneast
AZURE_TTS_VOICE=ja-JP-NanamiNeural
```

## 运行模式

系统支持两种运行模式：

### ✅ 真实 API 模式
当配置了对应的 API Key 时，系统会使用真实服务：
- AI 对话 → Moonshot Kimi
- 语音转文字 → OpenAI Whisper
- 语音合成 → Azure TTS

### ⚪ 虚拟模式
当 API Key 为空时，系统会自动使用虚拟模式：
- AI 对话 → 基于规则的预设回复
- 语音转文字 → 提示用户配置 API Key
- 语音合成 → 返回模拟音频 URL

**你可以只配置部分 API Key，系统会智能切换。**

## 安全性提醒

⚠️ **重要安全提示:**

1. **千万不要提交 `.env` 文件到 Git！**
   - `.env` 已添加到 `.gitignore`
   - 只提交 `.env.example` 作为模板

2. **保护好你的 API Keys:**
   - 不要在代码中硬编码 API Keys
   - 不要在公开场合分享 API Keys
   - 定期轮换 API Keys

3. **监控 API 用量:**
   - Moonshot: https://platform.moonshot.cn/
   - OpenAI: https://platform.openai.com/usage
   - Azure: https://portal.azure.com/

## API 端点

服务启动后访问:
- API 地址: http://localhost:8000
- API 文档: http://localhost:8000/docs

主要端点:
- `GET /scenarios` - 获取所有场景
- `POST /sessions` - 创建对话会话
- `POST /sessions/{id}/messages` - 发送消息
- `GET /sessions/{id}/summary` - 获取练习总结
- `GET /stats` - 获取学习统计

## 故障排查

### 问题: 无法连接到 API

**检查:**
```bash
# 测试后端是否运行
curl http://localhost:8000/

# 应该返回:
# {"message": "Welcome to Gokan API", "version": "1.0.0"}
```

### 问题: API Key 无效

**检查:**
1. 确认 `.env` 文件存在且格式正确
2. 确认 API Key 没有额外的空格或换行
3. 检查 API Key 是否已过期
4. 查看提供商的控制台是否有错误信息

### 问题: Azure TTS 返回错误

**检查:**
1. 确认 `AZURE_TTS_REGION` 设置为 `japaneast`
2. 确认 Speech Service 已创建且状态为 "Running"
3. 检查 API Key 是否复制完整（通常很长）

## 费用参考

使用真实 API 会产生费用，以下是大概参考：

| 服务 | 费用 |
|------|------|
| Moonshot Kimi | ¥0.012 / 1K tokens (8K模型) |
| OpenAI Whisper | $0.006 / 分钟 |
| Azure TTS | 每月 0.5M 字符免费，超出 $1 / 1M 字符 |

**省钱技巧:**
- 开发阶段使用虚拟模式
- 只对日语练习使用真实 API
- 监控用量，设置预算提醒
