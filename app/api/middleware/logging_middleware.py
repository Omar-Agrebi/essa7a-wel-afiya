import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("api.middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request methodology and timing."""
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time_ms = (time.time() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} -> "
            f"{response.status_code} ({process_time_ms:.2f}ms)"
        )

        if response.status_code == 400 and request.method == "OPTIONS":
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            the_origin = request.headers.get("origin", "Missing Origin Header")
            logger.error(f"400 Bad Request Body: {body.decode(errors='ignore')}")
            logger.error(f"FATAL CORS ERROR - The origin was: {the_origin}")
            logger.error(f"Currently allowed origins are: {settings.CORS_ORIGINS}")
            
            from starlette.responses import Response as StarletteResponse
            response = StarletteResponse(content=body, status_code=response.status_code, headers=dict(response.headers))
        
        return response
