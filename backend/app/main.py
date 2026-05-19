from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .config import settings
from .database import Base, engine
from . import models  # noqa: F401 — register models with Base.metadata
from .ratelimit import limiter
from .routers import generate as generate_router
from .routers import errors as errors_router
from .routers import admin as admin_router


def create_app() -> FastAPI:
    # Create tables for SQLite dev convenience; prod uses alembic.
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="Fake Error Generator", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.include_router(generate_router.router, prefix="/api")
    app.include_router(errors_router.router, prefix="/api")
    app.include_router(admin_router.router, prefix="/api")

    @app.get("/api/healthz")
    def healthz():
        return {"status": "ok"}

    return app


app = create_app()
