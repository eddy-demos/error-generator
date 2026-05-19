from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, Integer, DateTime, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Severity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    EXISTENTIAL = "EXISTENTIAL"


def _uuid() -> str:
    return str(uuid.uuid4())


class ErrorMessage(Base):
    __tablename__ = "errors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    code: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(SAEnum(Severity), nullable=False, default=Severity.ERROR)
    subsystem: Mapped[str] = mapped_column(String(60), nullable=False, default="unknown")
    tags: Mapped[list] = mapped_column(JSON, default=list)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    pattern: Mapped[str] = mapped_column(String(400), nullable=False)
    kind: Mapped[str] = mapped_column(String(20), nullable=False, default="title")  # title|description
    severity_hint: Mapped[Optional[Severity]] = mapped_column(SAEnum(Severity), nullable=True)
    weight: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class Vocab(Base):
    __tablename__ = "vocab"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    slot: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    value: Mapped[str] = mapped_column(String(120), nullable=False)
