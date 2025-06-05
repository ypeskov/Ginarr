from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class GinarrQuery(BaseModel):
    input: str = Field(..., min_length=1, max_length=100_000)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, alias_generator=to_camel)
