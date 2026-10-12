from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, TypeVar, cast

F = TypeVar("F", bound=Callable[..., object])

if TYPE_CHECKING:
    from typing_extensions import override as override
else:
    def override(function: F) -> F:
        return function


def object_mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError("Expected object")
    fields = cast(Mapping[object, object], value)
    if not all(isinstance(key, str) for key in fields):
        raise ValueError("Expected string keys")
    return cast(Mapping[str, object], fields)


def object_list(value: object) -> Sequence[object]:
    if not isinstance(value, list):
        raise ValueError("Expected array")
    return cast(Sequence[object], value)


def string(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Expected string")
    return value


def strings(value: object) -> list[str]:
    return [string(item) for item in object_list(value)]
