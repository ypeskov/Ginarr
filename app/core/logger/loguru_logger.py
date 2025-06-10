import sys
from typing import Any

from loguru import logger

my_logger: Any = logger

# Important: remove the default Loguru handler to have full control over logging.
# Otherwise, if you add your own handlers later, messages will be duplicated.
logger.remove()

# Add a handler for output to standard error stream (console).
# This is the main development configuration.
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",  # Minimum logging level for this handler
    diagnose=True,  # Enables extended diagnostics for errors (very useful in development)
    backtrace=True,  # Enables full call stack for errors
    colorize=True,  # Enables console colors
)

# If needed, you can add a handler for writing logs to a file
# (for example, for long-term viewing or if you need to save everything)
# logger.add(
#     "logs/debug.log",
#     format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
#     level="DEBUG", # This file will log starting from DEBUG level
#     rotation="10 MB", # Rotate file after 10 MB
#     compression="zip", # Compress old log files
#     enqueue=True, # Use queue for log writing (don't block the main thread)
#     diagnose=True,
#     backtrace=True
# )

# If you want logs from the standard 'logging' module to be processed by Loguru as well,
# add this:
# logger.add(sys.stderr, level="INFO", filter=lambda record: "httpx" not in record["name"] and "uvicorn" not in record["name"])
# logger.add("logs/all.log", level="DEBUG", filter=lambda record: "httpx" not in record["name"] and "uvicorn" not in record["name"])
# import logging
# logger.configure(
#     handlers=[{"sink": sys.stderr, "level": "INFO"}],
#     extra={"user": "default_user"}
# )
# logging.basicConfig(handlers=[LoguruHandler()]) # For intercepting standard loggers

# Export the configured logger to be used by other parts of the application
log = logger


def get_logger() -> Any:
    return log
