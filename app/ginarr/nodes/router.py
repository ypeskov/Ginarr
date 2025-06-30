from icecream import ic

from app.core.logger.app_logger import log
from app.ginarr.graph_state import GinarrState, MemorizePayload, ToolPayload
from app.ginarr.llm.allowed_routes import RouteNameEnum, parse_route_or_default
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

    route = result.get("route")
    state.route = parse_route_or_default(route)

    if route == "tool":
        tool_name = result.get("tool_name", None)
        tool_args = result.get("tool_args", None)
        if tool_name and tool_args:
            state.tool_payload = ToolPayload(tool_name=tool_name, tool_args=tool_args)
        else:
            log.warning(f"Tool payload is not valid: [{tool_name}] {tool_args}]. Falling back router to LLM")
            state.route = RouteNameEnum.LLM
    elif route == "memorize":
        memorize_scope = result.get("memorize_scope", None)
        memorize_n = result.get("memorize_n", None)
        memorize_period = result.get("memorize_period", None)
        memorize_topic = result.get("memorize_topic", None)
        if memorize_scope and (memorize_n or memorize_period or memorize_topic):
            state.memorize_payload = MemorizePayload(
                memorize_scope=memorize_scope,
                memorize_n=memorize_n,
                memorize_period=memorize_period,
                memorize_topic=memorize_topic,
            )
        else:
            log.warning(
                f"Memorize payload is not valid: [{memorize_scope}] [{memorize_n}] [{memorize_period}] [{memorize_topic}]."
                "Falling back router to LLM"
            )
            state.route = RouteNameEnum.LLM

    log.info(f"Router node set route to [{state.route}]")

    log.info("Exiting router_node")
    return state


def fallback_router_node(state: GinarrState) -> GinarrState:
    log.info("Entering fallback_router_node")
    ic(state)
    log.info("================================================")
    state.route = RouteNameEnum.LLM
    log.info("Exiting fallback_router_node")
    return state
