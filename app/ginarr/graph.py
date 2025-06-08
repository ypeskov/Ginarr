from typing import TypedDict, Literal, Any
from icecream import ic
import aiosqlite

from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.ginarr.settings import settings as ginarr_settings
from app.core.logger.app_logger import log
from app.ginarr.nodes.router import router_node
from app.ginarr.nodes.memory import memory_node
from app.ginarr.nodes.tool import tool_node
from app.ginarr.nodes.llm import llm_node

ic.configureOutput(includeContext=True)


class GinarrState(TypedDict, total=False):
    input: str
    user_id: int | None
    route: Literal["memory", "tool", "llm", "write"]
    fallback_to_llm: bool | None
    rerouted: bool | None
    result: dict[str, Any]


def end_node(state: GinarrState) -> GinarrState:
    """End node. Just clears state.
    Args:
        state: (GinarrState) State to clear
    Returns:
        (GinarrState) State with cleared fields
    """
    log.info("--- Entering end_node ---")

    state.pop("route", None)
    state.pop("fallback_to_llm", None)
    state.pop("rerouted", None)

    log.info("--- Exiting end_node ---")
    return state


def check_fallback_node(state: GinarrState) -> GinarrState:
    log.info("--- Entering check_fallback_node ---")
    return state


def should_fallback_to_llm(state: GinarrState) -> str:
    log.info("--- Verifying fallback to LLM ---")
    if state.get("fallback_to_llm") and not state.get("rerouted"):
        log.info("Fallback to LLM is required")
        state["rerouted"] = True
        return "llm"
    log.info("Fallback to LLM is not required")
    return "end"


async def build_ginarr_graph():
    builder = StateGraph(state_schema=GinarrState)

    builder.add_node("router", router_node)
    builder.add_node("memory", memory_node)
    builder.add_node("tool", tool_node)
    builder.add_node("llm", llm_node)
    builder.add_node("end", end_node)
    builder.add_node("check_fallback", check_fallback_node)

    builder.set_entry_point("router")

    builder.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {
            "memory": "memory",
            "tool": "tool",
            "llm": "llm",
        },
    )

    builder.add_edge("memory", "check_fallback")
    builder.add_edge("tool", "check_fallback")
    builder.add_edge("llm", "end")

    builder.add_edge("llm", "end")

    builder.add_conditional_edges(
        "check_fallback",
        should_fallback_to_llm,
        {
            "llm": "llm",
            "end": "end",
        },
    )

    conn = await aiosqlite.connect(ginarr_settings.MEMORY_SQLITE_PATH)
    checkpointer = AsyncSqliteSaver(conn=conn)

    return builder.compile(checkpointer=checkpointer)
