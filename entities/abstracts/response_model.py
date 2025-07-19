from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")

class ResponseModel(GenericModel, Generic[T]):
    message: str
    status: int
    data: Optional[T]
    metadata: Optional[dict] = None
