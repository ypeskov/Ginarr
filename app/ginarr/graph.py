from typing import Any

from app.ginarr.nodes.check_done import check_done_node
from icecream import ic
import aiosqlite

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.ginarr.settings import settings as ginarr_settings
from app.core.logger.app_logger import log
from app.ginarr.nodes.router import router_node
from app.ginarr.nodes.memory import memory_node
from app.ginarr.nodes.tool import tool_node
from app.ginarr.nodes.llm import llm_node, summarize_found_result_node
from app.ginarr.nodes.end import end_node as custom_end_node
from app.ginarr.nodes.web_search import web_search_node
from app.ginarr.nodes.memorize import memorize_node
from app.ginarr.graph_state import GinarrState
from app.ginarr.ginarr_errors import GinarrGraphCompilationError

ic.configureOutput(includeContext=True)


async def build_ginarr_graph() -> Any:
    log.info("Building Ginarr graph")
    builder = StateGraph(state_schema=GinarrState)

    builder.add_node("router", router_node)
    builder.add_node("memory", memory_node)
    builder.add_node("tool", tool_node)
    builder.add_node("llm", llm_node)
    builder.add_node("custom_end", custom_end_node)
    builder.add_node("summarize_found_result", summarize_found_result_node)
    builder.add_node("web_search", web_search_node)
    builder.add_node("memorize", memorize_node)
    builder.add_node("check_done", check_done_node)

    builder.set_entry_point("router")

    builder.add_conditional_edges(
        "router",
        lambda state: state.route,
        {
            "memory": "memory",
            "tool": "tool",
            "llm": "llm",
            "web_search": "web_search",
            "memorize": "memorize",
            "check_done": "check_done",
        },
    )

    builder.add_conditional_edges(
        "check_done",
        lambda state: state.route,
        {
            "llm": "llm",
            "custom_end": "custom_end",
        },
    )

    builder.add_edge("memory", "summarize_found_result")
    builder.add_edge("tool", "summarize_found_result")
    builder.add_edge("web_search", "summarize_found_result")
    builder.add_edge("llm", "check_done")
    builder.add_edge("summarize_found_result", "check_done")  
    builder.add_edge("memorize", "check_done")
    builder.add_edge("custom_end", END)

    conn = await aiosqlite.connect(ginarr_settings.MEMORY_SQLITE_PATH)
    checkpointer = AsyncSqliteSaver(conn=conn)

    log.info("Compiling Ginarr graph")
    try:
        graph = builder.compile(checkpointer=checkpointer)
        log.info("Ginarr graph compiled successfully")
        return graph
    except Exception as e:
        log.error(f"Error compiling Ginarr graph: {e}", exc_info=True)
        raise GinarrGraphCompilationError(f"Error compiling Ginarr graph: {e}")
