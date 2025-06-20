from typing import TypedDict, Any, Literal

from app.ginarr.llm.router_llm import RouteName


class MemorizePayload(TypedDict, total=False):
    memorize_scope: Literal["recent", "period", "filtered"]
    memorize_n: int
    memorize_period: str
    memorize_topic: str


class GinarrState(TypedDict, total=False):
    input: str
    user_id: int | None
    route: RouteName
    result: dict[str, Any]
    history: list[dict[str, str]]
    user_settings: dict[str, Any]
    context: str
    route_payload: MemorizePayload
