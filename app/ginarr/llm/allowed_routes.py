from typing import Literal, get_args

type RouteName = Literal["memory", "tool", "llm", "web_search", "memorize", "custom_end", "fallback_router"]

ALLOWED_ROUTES = set(get_args(RouteName))


def is_allowed_route(route: str) -> bool:
    return route in ALLOWED_ROUTES
