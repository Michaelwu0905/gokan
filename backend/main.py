import os
import sys
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .models import AnalyzeRequest, AnalyzeResponse
from .ai_service import AIService

# 全局 AI 服务实例
ai_service: Optional[AIService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global ai_service
    # 启动时初始化 AI 服务
    try:
        ai_service = AIService()
        print("✅ AI Service initialized successfully")
    except ValueError as e:
        print(f"⚠️  Warning: {e}")
        print("Please set OPENAI_API_KEY environment variable")
    yield
    # 关闭时清理资源
    print("🛑 Shutting down AI Service...")


app = FastAPI(
    title="Japanese Learning Assistant API",
    description="AI-powered Japanese text analysis API",
    version="0.1.0",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（仅本地开发使用）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "japanese-learning-assistant"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_image(request: AnalyzeRequest):
    """
    分析图片中的日语文本

    - **image_base64**: Base64 编码的图片数据
    - **context**: 可选的上下文信息
    """
    global ai_service

    if ai_service is None:
        raise HTTPException(
            status_code=503,
            detail="AI Service is not initialized. Please check OPENAI_API_KEY configuration.",
        )

    try:
        result = ai_service.analyze_image(request.image_base64)
        return AnalyzeResponse(status="success", data=result)
    except Exception as e:
        return AnalyzeResponse(status="error", error=f"Analysis failed: {str(e)}")


def main():
    """主入口函数"""
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "127.0.0.1")

    print(f"🚀 Starting Japanese Learning Assistant API on http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False, log_level="info")


if __name__ == "__main__":
    main()
