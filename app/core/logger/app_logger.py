from app.core.logger.loguru_logger import get_logger
# from app.core.logger.structlog_logger import get_logger

log = get_logger()


def get_app_logger():
    return log
