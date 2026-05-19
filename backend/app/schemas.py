from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator
import re

from .models import Severity

CODE_REGEX = re.compile(r"^0x[0-9A-F]{1,6}[A-Z]{0,2}$")


class ErrorBase(BaseModel):
    code: str = Field(..., max_length=16)
    title: str = Field(..., max_length=120)
    description: str = Field(..., max_length=500)
    severity: Severity
    subsystem: str = Field(..., max_length=60)
    tags: list[str] = Field(default_factory=list)
    is_favorite: bool = False

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not CODE_REGEX.match(v):
            raise ValueError("code must match ^0x[0-9A-F]{1,6}[A-Z]{0,2}$")
        return v


class ErrorCreate(ErrorBase):
    pass


class ErrorUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    severity: Optional[Severity] = None
    subsystem: Optional[str] = Field(default=None, max_length=60)
    tags: Optional[list[str]] = None
    is_favorite: Optional[bool] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not CODE_REGEX.match(v):
            raise ValueError("code must match ^0x[0-9A-F]{1,6}[A-Z]{0,2}$")
        return v


class ErrorOut(ErrorBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class ErrorListOut(BaseModel):
    items: list[ErrorOut]
    total: int
    page: int
    limit: int


class GenerateRequest(BaseModel):
    severity: Optional[Severity] = None
    subsystem: Optional[str] = Field(default=None, max_length=60)
    seed: Optional[str] = Field(default=None, max_length=16)


class GeneratedError(BaseModel):
    code: str
    title: str
    description: str
    severity: Severity
    subsystem: str
    tags: list[str] = []
    seed: str


# Templates & vocab
class TemplateBase(BaseModel):
    pattern: str = Field(..., max_length=400)
    kind: str = Field(default="title", max_length=20)
    severity_hint: Optional[Severity] = None
    weight: int = 1


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    pattern: Optional[str] = Field(default=None, max_length=400)
    kind: Optional[str] = Field(default=None, max_length=20)
    severity_hint: Optional[Severity] = None
    weight: Optional[int] = None


class TemplateOut(TemplateBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class VocabBase(BaseModel):
    slot: str = Field(..., max_length=40)
    value: str = Field(..., max_length=120)


class VocabCreate(VocabBase):
    pass


class VocabOut(VocabBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class Stats(BaseModel):
    total: int
    favorites: int
    by_severity: dict[str, int]
    top_subsystems: list[dict]
