from icecream import ic

from app.core.logger.app_logger import log
from app.ginarr.graph_state import GinarrState, MemorizePayload, ToolPayload
from app.ginarr.llm.router_llm import router_llm

ic.configureOutput(includeContext=True)


tool_list = """
universal_question_tool:
  Назначение: Ответ на универсальный вопрос
  Аргументы:
    - question (str): вопрос, на который требуется ответ
"""


async def router_node(state: GinarrState) -> GinarrState:
    log.info("Entering router_node")
    user_input = state.input

    result = await router_llm.ainvoke({"input": user_input, "tool_list": tool_list})
    ic(result)

    allowed_routes = {"memory", "llm", "web_search", "memorize", "tool"}
    route = result.get("route")
    state.route = route if route in allowed_routes else "llm"

    if route not in allowed_routes:
        log.warning(f"Unsupported route '{route}' from router_llm. Falling back to 'llm'")

    if route == "tool":
        state.tool_payload = ToolPayload(
            tool_name=result.get("tool_name", ""),
            tool_args=result.get("tool_args", {}),
        )
    elif route == "memorize":
        state.memorize_payload = MemorizePayload(**result.get("memorize_payload", {}))
    else:
        state.memorize_payload = MemorizePayload()

    log.info(f"Router node set route to [{state.route}]")

    log.info("Exiting router_node")
    return state


def fallback_router_node(state: GinarrState) -> GinarrState:
    log.info("Entering fallback_router_node")
    ic(state)
    log.info("================================================")
    state.route = "llm"
    log.info("Exiting fallback_router_node")
    return state
