# 日语沉浸式学习助手 (MVP) - AI 开发需求文档

## 1. 项目概述
本项目是一个跨平台桌面端日语学习辅助工具。采用 **Electron (前端) + FastAPI (Python 本地后端)** 的双进程架构。
核心功能：用户通过全局快捷键唤醒截屏，框选屏幕上的日语文本，Electron 前端将截图（Base64）发送给本地运行的 FastAPI 服务；FastAPI 调用大语言模型（Vision LLM）进行图文识别、翻译和语法拆解，并返回 JSON；最后 Electron 在截图位置附近弹出一个现代化的悬浮卡片展示结果。

## 2. 技术栈约束 (强制)
请严格遵守以下技术栈，不要引入无关的复杂框架：
* **前端 (主干与 UI)**: `Electron`, `Node.js`, HTML/CSS/JS (MVP 阶段可直接使用原生 JS 或轻量级框架如 Vue3/Vite，避免引入臃肿的脚手架)。
* **本地后端 (逻辑与 AI)**: `Python 3.10+`, `FastAPI`, `Uvicorn`。
* **前后端通信**: HTTP REST API (使用 `fetch` 或 `axios` 调用 `localhost:8000`)。
* **AI 接口**: `openai` 官方 Python 库 (调用兼容 OpenAI 格式的 Vision 多模态大模型,默认为moonshot kimi)。
* **项目管理**: 请使用uv进行项目管理

## 3. 系统架构与进程管理
本项目包含两个核心进程：
1. **Node 进程 (Electron Main)**: 程序的生命周期掌控者。启动时，使用 `child_process.spawn` 以后台静默方式启动 Python FastAPI 服务。退出时，必须确保 `kill` 掉 Python 进程。
2. **Python 进程 (FastAPI)**: 作为 Sidecar（本地微服务）运行，监听 `http://127.0.0.1:8000`。

## 4. 核心交互工作流 (Workflow)
1. 程序后台运行，Electron 注册全局快捷键（如 `Command+Shift+X` 或 `Ctrl+Alt+D`）。
2. 用户触发快捷键 -> Electron 获取当前屏幕截图，并在所有屏幕上层铺设一个全屏、无边框、置顶的透明窗口（Capture Window）。
3. Capture Window 加载刚才的截图，用户用鼠标拖拽生成矩形选区，释放鼠标后完成局部裁剪，将局部图片转为 Base64 字符串。
4. Capture Window 关闭 -> Electron 在选区位置附近弹出一个带有阴影的悬浮窗（Result Window），显示 "Loading..."。
5. Electron 将 Base64 图片 POST 给 FastAPI 本地接口 `/api/analyze`。
6. FastAPI 组装 Prompt，请求云端大模型 Vision API，获取 JSON 结果并返回给前端。
7. Result Window 渲染 JSON 数据（原文、翻译、读音、语法、例句）。
8. 用户点击 Result Window 外部或按 `Esc`，关闭悬浮窗，等待下一次唤醒。

## 5. 接口协议定义 (API Contract)
**Endpoint**: `POST http://127.0.0.1:8000/api/analyze`

**Request Body (JSON)**:
```json
{
  "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
  "context": "" // 预留字段，当前留空
}
```

**Response Body (JSON)**:
```json
{
  "status": "success",
  "data": {
    "original_text": "提取出的日文原文",
    "translation": "对应的中文翻译",
    "furigana": "原文的平假名注音（仅针对汉字标注）",
    "grammar_analysis": [
      {"word": "单词或语法点1", "explanation": "词性与用法解释"}
    ],
    "example_sentence": {
      "japanese": "包含核心语法或单词的日文例句",
      "chinese": "例句的中文翻译"
    }
  }
}
```

## 6. 模块详细需求与开发步骤指引

请 AI 助手按照以下 **4 个阶段（Phases）** 逐步进行开发，每完成一个阶段请让我进行测试确认：

### Phase 1: 搭建 Python FastAPI 后端 (无 UI)
* **目标**: 跑通 AI 核心逻辑。
* **任务**:
  1. 创建 `backend/main.py`，初始化 FastAPI 应用。
  2. 实现 `/api/analyze` POST 路由。
  3. 编写调用 LLM Vision API 的逻辑。**System Prompt 要求**：你是一个专业的日语教师。请提取图片中的日语文本，进行精确翻译并拆解核心语法。严格以 JSON 格式输出，不带 markdown 代码块标记。
  4. 使用写死的本地图片转换为 base64 进行测试，确保能稳定返回符合上述定义的 JSON。

### Phase 2: 搭建 Electron 骨架与进程管理
* **目标**: 让 Electron 能安全地管理 Python 后端。
* **任务**:
  1. 初始化 Electron 项目 (`main.js`)。
  2. 编写启动 Python 服务的逻辑：检查空闲端口（默认8000），使用 `spawn` 执行 `python backend/main.py`（开发环境下直接调用，打包环境后续再处理）。
  3. 捕获 Python 进程的 stdout/stderr 输出到 Electron 控制台以供调试。
  4. 监听 Electron 的 `app.on('will-quit')` 事件，确保彻底销毁 Python 子进程。

### Phase 3: 实现全屏截屏与交互 (Capture Window)
* **目标**: 实现丝滑的划区截图体验。
* **任务**:
  1. 注册全局快捷键。
  2. 快捷键触发时，使用 Electron 的 `desktopCapturer` 获取当前屏幕画面，创建一个全屏、无边框、置顶的 `BrowserWindow`。
  3. 在全屏窗口内实现前端逻辑（HTML/JS）：绘制一层半透明黑色遮罩，监听鼠标的 `mousedown`, `mousemove`, `mouseup` 事件，绘制一个高亮矩形（选区）。
  4. 鼠标松开后，利用 HTML5 `<canvas>` 将选区内的图像裁剪出来，转换为 Base64。通过 IPC 传递给 Electron 主进程，然后关闭该全屏窗口。

### Phase 4: 结果展示与前后端联调 (Result Window)
* **目标**: 完成最终的数据流闭环和 UI 展示。
* **任务**:
  1. Electron 主进程拿到 Base64 截图后，创建一个较小的无边框窗口 (Result Window)，位置设定在刚才截图选区的正下方或旁边（确保不超出屏幕边界）。
  2. Result Window 初始显示 Loading 动画。
  3. Result Window 内部发起 `fetch` 请求调用 `http://127.0.0.1:8000/api/analyze`。
  4. 拿到结果后，使用 CSS 优雅排版展示原文、翻译和语法树（字号适中，背景支持毛玻璃效果更佳）。
  5. 监听 Result Window 的失去焦点事件 (`blur`) 或键盘 `Esc` 事件，自动隐藏/关闭窗口。

## 7. 异常处理要求
* **截图误触**: 如果鼠标框选区域宽或高小于 15px，视为误触，直接退出截图状态，不发起请求。
* **后端服务未就绪**: 如果快捷键按下时，FastAPI 服务尚未启动成功，需弹出系统通知 (Notification) 提示用户“服务正在启动，请稍候”。
* **网络/API 错误**: 如果 LLM 请求超时或失败，Result Window 需要显示红色的错误提示信息，并允许用户一键关闭。