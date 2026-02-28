from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from .database import engine, get_db, Base
from .models import Session as DBSession, Message, Scenario, ErrorRecord
from .schemas import (
    ScenarioResponse,
    SessionCreate,
    SessionResponse,
    MessageCreate,
    MessageResponse,
    SessionSummary,
    StatsResponse,
)
from .ai_service_real import ai_service

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gokan API", version="1.0.0")

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to Gokan API", "version": "1.0.0"}


@app.get("/scenarios", response_model=List[ScenarioResponse])
def get_scenarios(db: Session = Depends(get_db)):
    """获取所有场景"""
    scenarios = db.query(Scenario).all()
    if not scenarios:
        # 初始化场景数据
        for s in ai_service.get_scenarios():
            scenario = Scenario(
                id=s["id"],
                name=s["name"],
                name_jp=s["name_jp"],
                description=s["description"],
                character_name=s["character_name"],
                character_profile=s["character_profile"],
                opening_line=s["opening_line"],
                vocab_hints=",".join(s["vocab_hints"]),
                difficulty=s["difficulty"],
            )
            db.add(scenario)
        db.commit()
        scenarios = db.query(Scenario).all()

    # 转换为响应格式
    result = []
    for s in scenarios:
        result.append(
            {
                "id": s.id,
                "name": s.name,
                "name_jp": s.name_jp,
                "description": s.description,
                "character_name": s.character_name,
                "difficulty": s.difficulty,
                "opening_line": s.opening_line,
                "vocab_hints": s.vocab_hints.split(","),
            }
        )
    return result


@app.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """获取单个场景详情"""
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")

    return {
        "id": scenario.id,
        "name": scenario.name,
        "name_jp": scenario.name_jp,
        "description": scenario.description,
        "character_name": scenario.character_name,
        "difficulty": scenario.difficulty,
        "opening_line": scenario.opening_line,
        "vocab_hints": scenario.vocab_hints.split(","),
    }


@app.post("/sessions", response_model=SessionResponse)
def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    """创建新对话会话"""
    scenario = (
        db.query(Scenario).filter(Scenario.id == session_data.scenario_id).first()
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")

    # 创建会话
    session_id = str(uuid.uuid4())
    db_session = DBSession(
        id=session_id,
        scenario_id=session_data.scenario_id,
        created_at=datetime.utcnow(),
    )
    db.add(db_session)

    # 添加AI开场白
    opening_message = Message(
        session_id=session_id,
        role="assistant",
        content=scenario.opening_line,
        audio_url=None,
    )
    db.add(opening_message)
    db.commit()
    db.refresh(db_session)

    return {
        "id": db_session.id,
        "scenario_id": db_session.scenario_id,
        "created_at": db_session.created_at,
        "messages": [
            {
                "id": opening_message.id,
                "role": "assistant",
                "content": opening_message.content,
                "audio_url": None,
                "created_at": opening_message.created_at,
            }
        ],
    }


@app.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """获取会话详情"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )

    return {
        "id": session.id,
        "scenario_id": session.scenario_id,
        "created_at": session.created_at,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "audio_url": m.audio_url,
                "created_at": m.created_at,
            }
            for m in messages
        ],
    }


@app.post("/sessions/{session_id}/messages", response_model=MessageResponse)
def send_message(
    session_id: str, message: MessageCreate, db: Session = Depends(get_db)
):
    """发送消息并获取AI回复"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 保存用户消息
    user_msg = Message(
        session_id=session_id, role="user", content=message.content, audio_url=None
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 获取对话历史
    history = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )
    history_list = [{"role": m.role, "content": m.content} for m in history]

    # 生成AI回复
    ai_response, errors = ai_service.generate_response(
        session.scenario_id, message.content, history_list
    )

    # 保存错误记录
    for error in errors:
        error_record = ErrorRecord(
            session_id=session_id,
            message_id=user_msg.id,
            error_type=error["error_type"],
            original_text=error["original_text"],
            correction=error["correction"],
            explanation=error["explanation"],
        )
        db.add(error_record)

    # 保存AI回复（模拟音频URL）
    assistant_msg = Message(
        session_id=session_id,
        role="assistant",
        content=ai_response,
        audio_url=f"/audio/mock/{uuid.uuid4()}.mp3",  # 模拟音频URL
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return {
        "id": assistant_msg.id,
        "role": "assistant",
        "content": assistant_msg.content,
        "audio_url": assistant_msg.audio_url,
        "created_at": assistant_msg.created_at,
    }


@app.get("/sessions/{session_id}/summary", response_model=SessionSummary)
def get_session_summary(session_id: str, db: Session = Depends(get_db)):
    """获取会话总结"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )
    history_list = [{"role": m.role, "content": m.content} for m in messages]

    summary = ai_service.generate_summary(history_list)

    return {
        "session_id": session_id,
        "total_messages": summary["total_messages"],
        "errors": summary["errors"],
        "suggestions": summary["suggestions"],
    }


@app.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """获取学习统计"""
    total_sessions = db.query(DBSession).count()
    total_messages = db.query(Message).count()

    # 计算练习时长（假设平均每条消息30秒）
    total_practice_minutes = (total_messages * 30) // 60

    # 统计错误类型
    from sqlalchemy import func

    error_stats = (
        db.query(ErrorRecord.error_type, func.count(ErrorRecord.error_type))
        .group_by(ErrorRecord.error_type)
        .all()
    )

    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "total_practice_minutes": total_practice_minutes,
        "common_error_types": [{"type": e[0], "count": e[1]} for e in error_stats],
    }


@app.post("/sessions/{session_id}/end")
def end_session(session_id: str, db: Session = Depends(get_db)):
    """结束会话"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session.ended_at = datetime.utcnow()
    db.commit()

    return {"message": "会话已结束", "session_id": session_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
