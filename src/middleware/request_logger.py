import time

from starlette.middleware.base import BaseHTTPMiddleware

from src.logs.logger import logger


class RequestLoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request,
        call_next
    ):

        start = time.time()

        logger.info(
            f"Incoming Request: "
            f"{request.method} {request.url.path}"
        )

        response = await call_next(request)

        duration = round(
            time.time() - start,
            4
        )

        logger.info(
            f"Completed Request: "
            f"{request.method} "
            f"{request.url.path} "
            f"Status={response.status_code} "
            f"Time={duration}s"
        )

        return response
