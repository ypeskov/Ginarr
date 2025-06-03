from fastapi import APIRouter, Depends
from app.api.v1.schemas.oktal_schema import OktalQuery
from app.oktal.agent import run_oktal_agent
from app.oktal.graph import build_oktal_graph
from langchain_core.runnables import Runnable
from app.models.User import User
from app.dependencies.auth import get_current_user
from app.core.database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from icecream import ic

ic.configureOutput(includeContext=True)

router = APIRouter(prefix="/oktal", tags=["oktal"])

graph_instance: Runnable | None = None


# Dependency function that will create or return a compiled graph.
# It must be async since build_oktal_graph() is async.
async def get_agent_graph() -> Runnable:
    global graph_instance
    if graph_instance is None:
        graph_instance = await build_oktal_graph()
    return graph_instance  # type: ignore


@router.post("/query")
async def query_oktal(
    data: OktalQuery,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    graph_instance: Runnable = Depends(get_agent_graph),
):
    result = await run_oktal_agent(data.input, graph_instance, user, db_session)
    return result
