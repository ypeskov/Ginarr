from datetime import datetime, timezone

import httpx
from icecream import ic

from app.core.logger.app_logger import log
from app.ginarr.graph_state import GinarrState
from app.ginarr.llm.allowed_routes import RouteNameEnum
from app.ginarr.settings import settings

ic.configureOutput(includeContext=True)

TAVILY_URL = "https://api.tavily.com/search"


async def web_search_node(state: GinarrState) -> GinarrState:
    log.info("Entering web_search_node")

    state.visited_routes.append(RouteNameEnum.WEB_SEARCH)

    query = state.input
    api_key = settings.TAVILY_API_KEY.get_secret_value()

    if not api_key:
        log.error("TAVILY_API_KEY not set")
        return state

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TAVILY_URL,
                json={"api_key": api_key, "query": query, "search_depth": "advanced"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        log.error(f"Tavily request failed: {e}", exc_info=True)
        return state

    results = data.get("results", [])

    state.result = {
        "type": "web_search",
        "input": query,
        "output": [],
    }

    tmp_output = []
    for r in results:
        tmp_output.append(
            {
                "text": f"{r['title']}\n{r['content']}\n{r['url']}\n--------------------------------",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    state.result["output"] = tmp_output

    log.info("Exiting web_search_node")
    return state
