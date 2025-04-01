"""Pydantic model type configuration."""

from typing import Dict, Any, List, Optional, TypeVar, Generic, Type  # type: ignore
from pydantic import BaseModel, Field, ConfigDict, field_validator  # type: ignore
from pydantic.generics import GenericModel  # type: ignore
from pydantic.fields import ValidationInfo  # type: ignore

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
        str_max_length=65536,
        str_min_length=1,
    )


class GenericResponse(GenericModel, Generic[T]):
    """Generic response wrapper with strict typing."""

    data: T
    success: bool = Field(default=True)
    errors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("errors")
    def validate_errors(
        cls, v: Optional[List[str]], info: ValidationInfo
    ) -> Optional[List[str]]:
        """Validate errors field."""
        if info.data.get("success", True) and v:
            raise ValueError("Cannot have errors when success is True")
        return v
