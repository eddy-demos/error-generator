from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Template, Vocab, ErrorMessage
from ..schemas import (
    TemplateCreate, TemplateUpdate, TemplateOut,
    VocabCreate, VocabOut, Stats,
)
from ..ratelimit import limiter

router = APIRouter(tags=["admin"])


# ----- Templates -----
@router.get("/templates", response_model=list[TemplateOut])
@limiter.limit("120/minute")
def list_templates(request: Request, db: Session = Depends(get_db)):
    return db.query(Template).all()


@router.post("/templates", response_model=TemplateOut, status_code=201)
@limiter.limit("120/minute")
def create_template(request: Request, payload: TemplateCreate, db: Session = Depends(get_db)):
    obj = Template(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/templates/{template_id}", response_model=TemplateOut)
@limiter.limit("120/minute")
def update_template(request: Request, template_id: str, payload: TemplateUpdate, db: Session = Depends(get_db)):
    obj = db.get(Template, template_id)
    if not obj:
        raise HTTPException(404, "not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/templates/{template_id}", status_code=204)
@limiter.limit("120/minute")
def delete_template(request: Request, template_id: str, db: Session = Depends(get_db)):
    obj = db.get(Template, template_id)
    if not obj:
        raise HTTPException(404, "not found")
    db.delete(obj)
    db.commit()


# ----- Vocab -----
@router.get("/vocab", response_model=list[VocabOut])
@limiter.limit("120/minute")
def list_vocab(request: Request, slot: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Vocab)
    if slot:
        q = q.filter(Vocab.slot == slot)
    return q.all()


@router.post("/vocab", response_model=VocabOut, status_code=201)
@limiter.limit("120/minute")
def create_vocab(request: Request, payload: VocabCreate, db: Session = Depends(get_db)):
    obj = Vocab(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/vocab/{vocab_id}", status_code=204)
@limiter.limit("120/minute")
def delete_vocab(request: Request, vocab_id: str, db: Session = Depends(get_db)):
    obj = db.get(Vocab, vocab_id)
    if not obj:
        raise HTTPException(404, "not found")
    db.delete(obj)
    db.commit()


# ----- Stats -----
@router.get("/stats", response_model=Stats)
@limiter.limit("120/minute")
def stats(request: Request, db: Session = Depends(get_db)):
    total = db.query(func.count(ErrorMessage.id)).scalar() or 0
    favorites = db.query(func.count(ErrorMessage.id)).filter(ErrorMessage.is_favorite == True).scalar() or 0  # noqa: E712
    by_severity_rows = (
        db.query(ErrorMessage.severity, func.count(ErrorMessage.id))
        .group_by(ErrorMessage.severity)
        .all()
    )
    by_severity = {str(s.value if hasattr(s, "value") else s): c for s, c in by_severity_rows}
    top_rows = (
        db.query(ErrorMessage.subsystem, func.count(ErrorMessage.id).label("c"))
        .group_by(ErrorMessage.subsystem)
        .order_by(func.count(ErrorMessage.id).desc())
        .limit(5)
        .all()
    )
    top_subsystems = [{"subsystem": s, "count": c} for s, c in top_rows]
    return {"total": total, "favorites": favorites, "by_severity": by_severity, "top_subsystems": top_subsystems}
