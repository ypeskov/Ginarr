# app/oktal/graph.py

from typing import TypedDict, Literal, Any
import aiosqlite
from sqlalchemy.ext.asyncio import AsyncSession

from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.oktal.nodes.router import router_node
from app.oktal.nodes.memory import memory_node
from app.oktal.nodes.tool import tool_node
from app.oktal.nodes.llm import llm_node


class OktalState(TypedDict, total=False):
    input: str
    user_id: int
    db_session: AsyncSession
    route: Literal["memory", "tool", "llm"]
    result: dict[str, Any]


def end_node(state: OktalState) -> OktalState:
    return state


async def build_oktal_graph():
    builder = StateGraph(state_schema=OktalState)

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

    conn = await aiosqlite.connect("./oktal_checkpoints.sqlite")
    checkpointer = AsyncSqliteSaver(conn=conn)

    return builder.compile(checkpointer=checkpointer)
