from icecream import ic
from langchain_core.runnables import RunnableConfig

from app.core.logger.app_logger import log

ic.configureOutput(includeContext=True)


async def memorize_node(state: dict, config: RunnableConfig) -> dict:
    log.info("Entering memorize_node")
    # ic(state)
    log.info("Exiting memorize_node")
    return state
