from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ErrorMessage, Severity
from ..schemas import ErrorCreate, ErrorUpdate, ErrorOut, ErrorListOut
from ..ratelimit import limiter

router = APIRouter(prefix="/errors", tags=["errors"])


@router.post("", response_model=ErrorOut, status_code=201)
@limiter.limit("120/minute")
def create_error(request: Request, payload: ErrorCreate, db: Session = Depends(get_db)):
    obj = ErrorMessage(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=ErrorListOut)
@limiter.limit("120/minute")
def list_errors(
    request: Request,
    severity: Optional[Severity] = None,
    subsystem: Optional[str] = None,
    favorite: Optional[bool] = None,
    q: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(ErrorMessage)
    if severity is not None:
        query = query.filter(ErrorMessage.severity == severity)
    if subsystem:
        query = query.filter(ErrorMessage.subsystem == subsystem)
    if favorite is not None:
        query = query.filter(ErrorMessage.is_favorite == favorite)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(ErrorMessage.title.ilike(like), ErrorMessage.description.ilike(like)))
    if tag:
        # JSON contains: use string match as a portable fallback
        query = query.filter(func.cast(ErrorMessage.tags, type_=__import__("sqlalchemy").String).ilike(f'%"{tag}"%'))

    total = query.count()
    items = (
        query.order_by(ErrorMessage.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/{error_id}", response_model=ErrorOut)
@limiter.limit("120/minute")
def get_error(request: Request, error_id: str, db: Session = Depends(get_db)):
    obj = db.get(ErrorMessage, error_id)
    if not obj:
        raise HTTPException(404, "not found")
    return obj


@router.put("/{error_id}", response_model=ErrorOut)
@limiter.limit("120/minute")
def replace_error(request: Request, error_id: str, payload: ErrorCreate, db: Session = Depends(get_db)):
    obj = db.get(ErrorMessage, error_id)
    if not obj:
        raise HTTPException(404, "not found")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{error_id}", response_model=ErrorOut)
@limiter.limit("120/minute")
def patch_error(request: Request, error_id: str, payload: ErrorUpdate, db: Session = Depends(get_db)):
    obj = db.get(ErrorMessage, error_id)
    if not obj:
        raise HTTPException(404, "not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{error_id}", status_code=204)
@limiter.limit("120/minute")
def delete_error(request: Request, error_id: str, db: Session = Depends(get_db)):
    obj = db.get(ErrorMessage, error_id)
    if not obj:
        raise HTTPException(404, "not found")
    db.delete(obj)
    db.commit()
    return None
