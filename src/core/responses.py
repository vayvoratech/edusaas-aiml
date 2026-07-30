from datetime import datetime


def success_response(
    message: str,
    data=None
):

    return {

        "success": True,

        "message": message,

        "timestamp": datetime.utcnow().isoformat(),

        "data": data

    }


def error_response(
    message: str,
    error_code: str
):

    return {

        "success": False,

        "message": message,

        "error_code": error_code,

        "timestamp": datetime.utcnow().isoformat()

    }