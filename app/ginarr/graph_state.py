from typing import TypedDict, Literal, Any


class GinarrState(TypedDict, total=False):
    input: str
    user_id: int | None
    route: Literal["memory", "tool", "llm"]
    result: dict[str, Any]
    history: list[dict[str, str]]
