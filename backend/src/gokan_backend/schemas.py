from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ScenarioBase(BaseModel):
    name: str
    name_jp: str
    description: str
    character_name: str
    difficulty: str


class ScenarioResponse(ScenarioBase):
    id: int
    opening_line: str
    vocab_hints: List[str]

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str
    is_voice: bool = False


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    audio_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    scenario_id: int


class SessionResponse(BaseModel):
    id: str
    scenario_id: int
    created_at: datetime
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


class ErrorItem(BaseModel):
    error_type: str
    original_text: str
    correction: str
    explanation: str


class SessionSummary(BaseModel):
    session_id: str
    total_messages: int
    errors: List[ErrorItem]
    suggestions: List[str]


class StatsResponse(BaseModel):
    total_sessions: int
    total_messages: int
    total_practice_minutes: int
    common_error_types: List[dict]
