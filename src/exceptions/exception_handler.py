from fastapi import Request
from fastapi.responses import JSONResponse

from src.exceptions.custom_exceptions import EduAIException


async def eduai_exception_handler(
    request: Request,
    exc: EduAIException
):

    return JSONResponse(

        status_code=exc.status_code,

        content={

            "success": False,

            "message": exc.message,

            "error_code": exc.error_code

        }

    )