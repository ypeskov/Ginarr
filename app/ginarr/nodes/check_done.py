from icecream import ic

from app.core.logger.app_logger import log
from app.ginarr.graph_state import GinarrState
from app.ginarr.llm.allowed_routes import RouteNameEnum

ic.configureOutput(includeContext=True)


def check_done_node(state: GinarrState) -> GinarrState:
    log.info("Entering check_done_node")

    if state.number_of_cycles > 2:
        log.info("Number of cycles is greater than 2. Ending conversation")
        state.route = RouteNameEnum.CUSTOM_END
        return state

    if state.is_done:
        log.info("Conversation is done")
        state.route = RouteNameEnum.CUSTOM_END
    else:
        log.info("Conversation is not done. Reasoning...")
        state.route = RouteNameEnum.FALLBACK_ROUTER
        state.number_of_cycles += 1

    log.info("Exiting check_done_node")
    return state
