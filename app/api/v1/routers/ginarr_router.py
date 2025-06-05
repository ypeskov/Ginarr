from fastapi import APIRouter, Depends
from app.api.v1.schemas.ginarr_schema import GinarrQuery
from app.ginarr.agent import run_ginarr_agent
from app.ginarr.graph import build_ginarr_graph
from langchain_core.runnables import Runnable
from app.models.User import User
from app.dependencies.auth import get_current_user
from app.core.database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from icecream import ic

ic.configureOutput(includeContext=True)

router = APIRouter(prefix="/ginarr", tags=["ginarr"])

graph_instance: Runnable | None = None


# Dependency function that will create or return a compiled graph.
# It must be async since build_ginarr_graph() is async.
async def get_agent_graph() -> Runnable:
    global graph_instance
    if graph_instance is None:
        graph_instance = await build_ginarr_graph()
    return graph_instance  # type: ignore


@router.post("/query")
async def query_ginarr(
    data: GinarrQuery,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    graph_instance: Runnable = Depends(get_agent_graph),
):
    result = await run_ginarr_agent(data.input, graph_instance, user, db_session)
    return result
