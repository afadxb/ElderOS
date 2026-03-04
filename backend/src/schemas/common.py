from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Generic, TypeVar

T = TypeVar("T")


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class PaginatedResponse(CamelModel, Generic[T]):
    data: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
