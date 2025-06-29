from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict

from app.ginarr.llm.router_llm import RouteName


class MemorizePayload(TypedDict, total=False):
    memorize_scope: Literal[
        "recent",
        "period",
        "filtered",
    ]
    memorize_n: int
    memorize_period: str
    memorize_topic: str



@dataclass
class GinarrState:
    input: str = ""
    user_id: int | None = None
    route: RouteName | None = "llm"
    result: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, str]] = field(default_factory=list)
    user_settings: dict[str, Any] = field(default_factory=dict)
    context: str = ""
    route_payload: MemorizePayload = field(default_factory=MemorizePayload)
    is_done: bool = False
