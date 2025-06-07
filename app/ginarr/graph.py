from typing import TypedDict, Literal, Any
from icecream import ic
import aiosqlite

from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.ginarr.settings import settings as ginarr_settings
from app.ginarr.nodes.router import router_node
from app.ginarr.nodes.memory import memory_node
from app.ginarr.nodes.tool import tool_node
from app.ginarr.nodes.llm import llm_node

ic.configureOutput(includeContext=True)


class GinarrState(TypedDict, total=False):
    input: str
    user_id: int | None
    route: Literal["memory", "tool", "llm"]
    fallback_to_llm: bool | None
    rerouted: bool | None
    result: dict[str, Any]


def end_node(state: GinarrState) -> GinarrState:
    """Узел завершения - просто очищает служебные поля"""
    ic("--- Entering end_node ---")

    # Очищаем служебные поля
    state.pop("route", None)
    state.pop("fallback_to_llm", None)
    state.pop("rerouted", None)

    ic("--- Exiting end_node ---")
    return state


def check_fallback_node(state: GinarrState) -> GinarrState:
    ic("--- Entering check_fallback_node ---")
    return state  # Просто возвращаем state без изменений


def should_fallback_to_llm(state: GinarrState) -> str:
    if state.get("fallback_to_llm") and not state.get("rerouted"):
        state["rerouted"] = True
        return "llm"
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

    # LLM всегда идет в end (без возможности повторного fallback)
    builder.add_edge("llm", "end")

    builder.add_conditional_edges(
        "check_fallback",
        should_fallback_to_llm,
        {
            "llm": "llm",
            "end": "end",  # НЕ "__end__" — мы явно вызываем end_node
        },
    )

    conn = await aiosqlite.connect(ginarr_settings.MEMORY_SQLITE_PATH)
    checkpointer = AsyncSqliteSaver(conn=conn)

    return builder.compile(checkpointer=checkpointer)
