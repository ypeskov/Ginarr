from icecream import ic

from app.ginarr.llm.router_llm import router_llm
from app.ginarr.graph_state import GinarrState, MemorizePayload
from app.core.logger.app_logger import log

ic.configureOutput(includeContext=True)

def universal_question_tool(question: str) -> str:
    """Return the answer to the question"""
    ic(question)
    ic('========================================')
    return "the answer is 42"

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

    route = result.get("route", "llm")  # default route is llm
    # TODO: filter unsupported routes (e.g. tool) at runtime
    allowed_routes = {"memory", "llm", "web_search", "memorize"}
    if route not in allowed_routes:
        log.warning(f"Unsupported route '{route}' from router_llm. Falling back to 'llm'")
        route = "llm"
    state.route = route

    # directly extract route_payload if present
    if "route_payload" in result:
        state.route_payload = MemorizePayload(**result["route_payload"])

    log.info(f"Router node set route to [{state.route}]")

    log.info("Exiting router_node")
    return state
