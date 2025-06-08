from typing import TypedDict, Any

from app.ginarr.llm.router_llm import RouteName


class GinarrState(TypedDict, total=False):
    input: str
    user_id: int | None
    route: RouteName
    result: dict[str, Any]
    history: list[dict[str, str]]
