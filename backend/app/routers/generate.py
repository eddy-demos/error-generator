from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..generator import generate
from ..schemas import GenerateRequest, GeneratedError
from ..ratelimit import limiter

router = APIRouter(tags=["generate"])


@router.post("/generate", response_model=GeneratedError)
@limiter.limit("60/minute")
def post_generate(request: Request, payload: GenerateRequest, db: Session = Depends(get_db)):
    out = generate(db, severity=payload.severity, subsystem=payload.subsystem, seed=payload.seed)
    return out


@router.get("/preview/{seed}", response_model=GeneratedError)
@limiter.limit("120/minute")
def get_preview(request: Request, seed: str, db: Session = Depends(get_db)):
    out = generate(db, seed=seed)
    return out
