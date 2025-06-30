from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict

from app.ginarr.llm.allowed_routes import RouteName


class MemorizePayload(TypedDict, total=False):
    memorize_scope: Literal[
        "recent",
        "period",
        "filtered",
    ]
    memorize_n: int
    memorize_period: str
    memorize_topic: str


class ToolPayload(TypedDict, total=False):
    tool_name: str
    tool_args: dict[str, Any]


@dataclass
class GinarrState:
    input: str = ""
    user_id: int | None = None
    route: RouteName | None = "llm"
    result: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, str]] = field(default_factory=list)
    user_settings: dict[str, Any] = field(default_factory=dict)
    context: str = ""
    memorize_payload: MemorizePayload = field(default_factory=MemorizePayload)
    tool_payload: ToolPayload = field(default_factory=ToolPayload)
    is_done: bool = False
    number_of_cycles: int = 0
