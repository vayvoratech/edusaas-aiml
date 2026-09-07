class EduAIException(Exception):
    """
    Base exception for the EduSaaS platform.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "EDUAI_ERROR"
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

        super().__init__(message)


class DatabaseException(EduAIException):

    def __init__(self, message="Database Error"):

        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR"
        )


class ModelException(EduAIException):

    def __init__(self, message="Model Prediction Failed"):

        super().__init__(
            message=message,
            status_code=500,
            error_code="MODEL_ERROR"
        )


class ValidationException(EduAIException):

    def __init__(self, message="Validation Failed"):

        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR"
        )


class NotFoundException(EduAIException):

    def __init__(self, message="Resource Not Found"):

        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND"
        )