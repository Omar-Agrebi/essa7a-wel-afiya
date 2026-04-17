import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("api.middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request methodology and timing."""
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time_ms = (time.time() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} → "
            f"{response.status_code} ({process_time_ms:.2f}ms)"
        )
        
        return response
