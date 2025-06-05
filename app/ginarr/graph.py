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
    result: dict[str, Any]


def end_node(state: GinarrState) -> GinarrState:
    return state


async def build_ginarr_graph():
    builder = StateGraph(state_schema=GinarrState)

    builder.add_node("router", router_node)
    builder.add_node("memory", memory_node)
    builder.add_node("tool", tool_node)
    builder.add_node("llm", llm_node)
    builder.add_node("end", end_node)

    builder.set_entry_point("router")

    builder.add_conditional_edges(
        "router", lambda state: state["route"], {"memory": "memory", "tool": "tool", "llm": "llm"}
    )

    builder.add_edge("memory", "end")
    builder.add_edge("tool", "end")
    builder.add_edge("llm", "end")

    conn = await aiosqlite.connect(ginarr_settings.MEMORY_SQLITE_PATH)
    checkpointer = AsyncSqliteSaver(conn=conn)

    return builder.compile(checkpointer=checkpointer)
