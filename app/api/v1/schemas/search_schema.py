from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

DEFAULT_LIMIT = 20


class SearchQuery(BaseModel):
    query: str = Field(..., description="Text query to search for")
    content_types: list[str] = Field(..., description="List of embedding types to search (e.g., ['text', 'pdf'])")
    from_date: list[datetime] | None = Field(None, description="Start datetime filter (optional)")
    to_date: list[datetime] | None = Field(None, description="End datetime filter (optional)")
    limit: int | None = Field(DEFAULT_LIMIT, description="Limit the number of results")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, alias_generator=to_camel)
