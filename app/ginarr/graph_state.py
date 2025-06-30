from dataclasses import dataclass, field
from typing import Any, Literal

from app.ginarr.llm.allowed_routes import RouteNameEnum


@dataclass
class MemorizePayload:
    memorize_scope: Literal[
        "recent",
        "period",
        "filtered",
    ]
    memorize_n: int | None = None
    memorize_period: str | None = None
    memorize_topic: str | None = None


@dataclass
class ToolPayload:
    tool_name: str
    tool_args: dict[str, Any]


@dataclass
class GinarrState:
    input: str = ""
    user_id: int | None = None
    route: RouteNameEnum | None = RouteNameEnum.LLM
    visited_routes: list[RouteNameEnum] = field(default_factory=list)
    result: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, str]] = field(default_factory=list)
    user_settings: dict[str, Any] = field(default_factory=dict)
    context: str = ""
    memorize_payload: MemorizePayload | None = None
    tool_payload: ToolPayload | None = None
    is_done: bool = False
    number_of_cycles: int = 0
