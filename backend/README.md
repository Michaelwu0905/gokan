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

#### 🇨🇳 推荐：阿里云语音服务（国内网络友好）

**注册地址:** https://www.aliyun.com/product/nls

**优势:**
- ✅ 国内访问速度快，无需翻墙
- ✅ 语音识别 + 语音合成一体化
- ✅ 每月免费额度充足（50万次/月）
- ✅ 支持日语语音合成

**配置项:**
```bash
# 必须配置
ALIYUN_ACCESS_KEY_ID=your-access-key-id
ALIYUN_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_APP_KEY=your-nls-app-key

# 可选配置（默认日语女声）
ALIYUN_TTS_VOICE=xiaoyun
AUDIO_PROVIDER=aliyun
```

**获取步骤:**
1. 访问 https://www.aliyun.com/ 注册阿里云账号
2. 进入控制台 → 搜索 "智能语音交互"
3. 开通服务（有免费试用额度）
4. 创建项目，获取 **AppKey**
5. 进入 "AccessKey 管理" 创建 AccessKey，获取 **AccessKey ID** 和 **AccessKey Secret**
6. 填入 `.env` 文件

**日语声音选项:**
- `xiaoyun` - 日语女声（推荐，默认）
- `xiaogang` - 日语男声

---

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

#### 🔑 OpenAI API (语音转文字) - 国外方案

**⚠️ 中国用户推荐使用阿里云语音服务替代（见上文）**

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

#### 🔑 Azure TTS API (语音合成) - 国外方案

**⚠️ 中国用户推荐使用阿里云语音服务替代（见上文）**

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

### 🇨🇳 推荐：国内用户配置方案

```bash
# 必需配置（国内网络友好）
MOONSHOT_API_KEY=sk-your-moonshot-key     # 月之暗面（国内公司）
ALIYUN_ACCESS_KEY_ID=your-aliyun-id       # 阿里云（国内网络）
ALIYUN_ACCESS_KEY_SECRET=your-aliyun-secret
ALIYUN_APP_KEY=your-aliyun-app-key
AUDIO_PROVIDER=aliyun                     # 启用阿里云语音
```

**完整服务链：**
- AI 对话 → Moonshot Kimi (国内)
- 语音转文字 → 阿里云 NLS (国内)
- 语音合成 → 阿里云 NLS (国内)

**优势：**
- ✅ 无需翻墙，国内访问速度快
- ✅ 阿里云每月 50 万次免费调用额度
- ✅ 支持日语语音识别和合成

---

### 🌍 国外用户配置方案

```bash
# 国外 API 配置
MOONSHOT_API_KEY=sk-your-moonshot-key     # AI对话
OPENAI_API_KEY=sk-your-openai-key         # 语音识别
AZURE_TTS_KEY=your-azure-key              # 语音合成
AUDIO_PROVIDER=openai+azure
```

**完整服务链：**
- AI 对话 → Moonshot Kimi
- 语音转文字 → OpenAI Whisper
- 语音合成 → Azure TTS

---

### ⚪ 虚拟模式（无需 API Key）

当未配置任何 API Key 时，系统使用虚拟模式：
- AI 对话 → 基于规则的预设回复
- 语音转文字 → 提示用户配置 API Key
- 语音合成 → 返回模拟音频 URL

**适合：** 开发测试、演示环境

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

### 🇨🇳 国内方案（推荐）

| 服务 | 费用 | 免费额度 |
|------|------|----------|
| **Moonshot Kimi** | ¥0.012 / 1K tokens | 新用户有免费额度 |
| **阿里云 NLS** (语音识别) | ¥1.2 / 小时 | **每月 50 万次调用** |
| **阿里云 NLS** (语音合成) | ¥2 / 千次 | **每月 50 万次调用** |

**实际使用成本估算（每天练习 30 分钟）:**
- AI 对话: ~¥0.5/天
- 语音识别: **免费**（在额度内）
- 语音合成: **免费**（在额度内）
- **总计: ~¥15/月**

### 🌍 国外方案

| 服务 | 费用 | 免费额度 |
|------|------|----------|
| Moonshot Kimi | ¥0.012 / 1K tokens | 新用户有免费额度 |
| OpenAI Whisper | $0.006 / 分钟 | 无 |
| Azure TTS | $1 / 1M 字符 | 每月 0.5M 字符 |

**实际使用成本估算（每天练习 30 分钟）:**
- AI 对话: ~¥0.5/天
- 语音识别: ~¥2.5/天
- 语音合成: ~¥0.5/天
- **总计: ~¥105/月**

---

**💡 省钱技巧:**
1. **首选阿里云方案**：免费额度充足，国内访问快
2. 开发阶段使用虚拟模式
3. 只对日语练习使用真实 API
4. 监控用量，设置预算提醒
5. 阿里云新用户有 3 个月免费试用
