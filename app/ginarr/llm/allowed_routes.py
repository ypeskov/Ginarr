from enum import Enum


class RouteNameEnum(Enum):
    MEMORY = "memory"
    TOOL = "tool"
    LLM = "llm"
    WEB_SEARCH = "web_search"
    MEMORIZE = "memorize"
    CUSTOM_END = "custom_end"
    FALLBACK_ROUTER = "fallback_router"


def parse_route_or_default(
    route_str: str,
    default: RouteNameEnum = RouteNameEnum.LLM,
) -> RouteNameEnum:
    try:
        return RouteNameEnum(route_str)
    except ValueError:
        return default
