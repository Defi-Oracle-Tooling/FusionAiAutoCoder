"""Pydantic model type configuration."""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict, validator
from pydantic.generics import GenericModel

T = TypeVar("T")


class BaseModelStrict(BaseModel):
    """Base model with strict type checking."""

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=False,
        smart_union=True,
        validate_default=True,
        extra="forbid",
        str_max_length=2**16,
        str_min_length=1,
    )


class GenericResponse(GenericModel, Generic[T]):
    """Generic response wrapper with strict typing."""

    data: T
    success: bool = Field(default=True)
    errors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator("errors")
    def validate_errors(
        cls, v: Optional[List[str]], values: Dict[str, Any]
    ) -> Optional[List[str]]:
        """Validate that errors are present only when success is False."""
        if values.get("success", True) and v:
            raise ValueError("Errors should not be present when success is True")
        return v
