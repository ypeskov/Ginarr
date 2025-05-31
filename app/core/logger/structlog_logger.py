import logging
import sys
import structlog

# Configure standard logging, since structlog uses it
logging.basicConfig(
    format="%(message)s", # Structlog will format it, here is the minimum
    stream=sys.stderr,
    level=logging.INFO,
)

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer() if sys.stderr.isatty() else structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Export the configured logger
log = structlog.get_logger()

def get_logger():
    """
    Get the logger for the app.
    This is a wrapper around the structlog.get_logger() function.
    In case of need additional configuration of the logger, you can do it here.
    """
    return log