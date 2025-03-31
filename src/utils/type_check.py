"""Type checking utilities and runtime verification."""

from typing import Any, Callable, TypeVar, cast, Type, Optional
from functools import wraps
import logging
from typeguard import TypeCheckError, typechecked

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger(__name__)


def type_error_handler(error: TypeCheckError, stack: Optional[Any] = None) -> None:
    """Handle type checking errors."""
    logger.error(f"Type check failed: {error}")
    if stack:
        logger.debug(f"Stack trace: {stack}")
    raise error


def strict_types(*type_args: Any, **type_kwargs: Any) -> Callable[[F], F]:
    """Decorator for strict type checking."""

    def decorator(func: F) -> F:
        @wraps(func)
        @typechecked
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


def ensure_type(value: Any, expected_type: Type[T]) -> T:
    """Ensure value matches expected type."""
    if not isinstance(value, expected_type):
        raise TypeError(
            f"Expected {expected_type.__name__}, got {type(value).__name__}"
        )
    return cast(T, value)


def runtime_checkable(cls: Type[T]) -> Type[T]:
    """Class decorator for runtime type checking."""
    cls.__post_init__ = lambda self: validate_types(self)
    return cls


def validate_types(obj: Any) -> None:
    """Validate type annotations at runtime."""
    hints = getattr(obj.__class__, "__annotations__", {})
    for name, expected_type in hints.items():
        if hasattr(obj, name):
            value = getattr(obj, name)
            try:
                ensure_type(value, expected_type)
            except TypeError as e:
                raise TypeError(f"Invalid type for {name}: {e}")


def coerce_type(value: Any, target_type: Type[T]) -> T:
    """Attempt to coerce value to target type."""
    if isinstance(value, target_type):
        return cast(T, value)
    try:
        return target_type(value)
    except (ValueError, TypeError) as e:
        raise TypeError(
            f"Cannot coerce {type(value).__name__} to {target_type.__name__}: {e}"
        )
