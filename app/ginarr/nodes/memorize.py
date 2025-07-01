from icecream import ic
from langchain_core.runnables import RunnableConfig

from app.core.logger.app_logger import log
from app.ginarr.graph_state import GinarrState
from app.ginarr.llm.allowed_routes import RouteNameEnum

ic.configureOutput(includeContext=True)


async def memorize_node(state: GinarrState, config: RunnableConfig) -> GinarrState:
    log.info("Entering memorize_node")

    state.visited_routes.append(RouteNameEnum.MEMORIZE)

    if state.memorize_payload is None:
        log.error("memorize_payload is None")
        state.result = {
            "type": "memorize",
            "input": state.input,
            "output": [],
            "error": "No memorize payload provided",
        }
        return state

    memorize_scope = state.memorize_payload.memorize_scope
    memorize_n = state.memorize_payload.memorize_n
    memorize_period = state.memorize_payload.memorize_period
    memorize_topic = state.memorize_payload.memorize_topic

    if memorize_scope == "recent":
        pass

    log.info("Exiting memorize_node")
    return state
