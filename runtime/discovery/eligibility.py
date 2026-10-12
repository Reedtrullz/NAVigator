from collections.abc import Mapping
from typing import cast


def age_in_bounds(bounds: object, age: object, age_text: str | None = None) -> bool | None:
    if not isinstance(bounds, dict) or not isinstance(age, int) or isinstance(age, bool):
        return None
    fields = cast(Mapping[object, object], bounds)
    low, high = fields.get("min"), fields.get("max")
    if low is None and high is None:
        return None
    for value in (low, high):
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 120):
            return None
    if low is not None and not isinstance(low, int):
        return None
    if high is not None and not isinstance(high, int):
        return None
    if not 0 <= age <= 120 or (low is not None and high is not None and low > high):
        return None
    text = (age_text or "").casefold()
    if low is not None and (age < low or (text.startswith("over ") and age == low)):
        return False
    if high is not None and (age > high or (text.startswith("under ") and age == high)):
        return False
    return True
