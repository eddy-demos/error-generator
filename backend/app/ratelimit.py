from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import settings


storage_uri = settings.rate_limit_redis_url or "memory://"
limiter = Limiter(key_func=get_remote_address, storage_uri=storage_uri)
