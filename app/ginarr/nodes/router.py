from app.ginarr.llm.router_llm import router_llm
from app.ginarr.graph_state import GinarrState
from app.core.logger.app_logger import log


async def router_node(state: GinarrState) -> GinarrState:
    log.info("Entering router_node")
    user_input = state.get("input", "")

    result = await router_llm.ainvoke({"input": user_input})

    state["route"] = result["route"]
    log.info(f"Router node set route to [{state['route']}]")

    log.info("Exiting router_node")
    return state
