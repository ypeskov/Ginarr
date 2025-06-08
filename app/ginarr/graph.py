from icecream import ic
import aiosqlite

from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.ginarr.settings import settings as ginarr_settings
from app.core.logger.app_logger import log
from app.ginarr.nodes.router import router_node
from app.ginarr.nodes.memory import memory_node
from app.ginarr.nodes.tool import tool_node
from app.ginarr.nodes.llm import llm_node, summarize_found_result_node
from app.ginarr.graph_state import GinarrState

ic.configureOutput(includeContext=True)


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


async def build_ginarr_graph():
    builder = StateGraph(state_schema=GinarrState)

    builder.add_node("router", router_node)
    builder.add_node("memory", memory_node)
    builder.add_node("tool", tool_node)
    builder.add_node("llm", llm_node)
    builder.add_node("end", end_node)
    builder.add_node("summarize_found_result", summarize_found_result_node)

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

    builder.add_edge("memory", "summarize_found_result")
    builder.add_edge("tool", "summarize_found_result")
    builder.add_edge("llm", "end")
    builder.add_edge("summarize_found_result", "end")

    conn = await aiosqlite.connect(ginarr_settings.MEMORY_SQLITE_PATH)
    checkpointer = AsyncSqliteSaver(conn=conn)

    return builder.compile(checkpointer=checkpointer)
