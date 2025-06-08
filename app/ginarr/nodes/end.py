from app.ginarr.graph_state import GinarrState
from app.core.logger.app_logger import log


def end_node(state: GinarrState) -> GinarrState:
    """End node. Just clears state.
    Args:
        state: (GinarrState) State to clear
    Returns:
        (GinarrState) State with cleared fields
    """
    log.info("Entering end_node")
    state.pop("route", None)
    log.info("Exiting end_node")
    return state
