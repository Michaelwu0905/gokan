from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    messages = relationship("Message", back_populates="session")
    scenario = relationship("Scenario")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    audio_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    name_jp = Column(String)
    description = Column(Text)
    character_name = Column(String)
    character_profile = Column(Text)
    opening_line = Column(Text)
    vocab_hints = Column(Text)  # JSON string
    difficulty = Column(String)  # 'N5' or 'N4'


class ErrorRecord(Base):
    __tablename__ = "error_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    message_id = Column(Integer, ForeignKey("messages.id"))
    error_type = Column(String)  # 'particle', 'verb', 'keigo', etc.
    original_text = Column(Text)
    correction = Column(Text)
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class SavedPhrase(Base):
    __tablename__ = "saved_phrases"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    phrase = Column(Text)
    meaning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
