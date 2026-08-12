from src.logs.logger import logger


class BaseService:

    def log_info(self, message: str):

        logger.info(message)

    def log_error(self, message: str):

        logger.error(message)

    def log_exception(self, message: str):

        logger.exception(message)