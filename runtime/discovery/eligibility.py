def age_in_bounds(bounds, age, age_text=None):
    if not isinstance(bounds, dict) or not isinstance(age, int) or isinstance(age, bool):
        return None
    low, high = bounds.get("min"), bounds.get("max")
    if low is None and high is None:
        return None
    for value in (low, high):
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 120):
            return None
    if not 0 <= age <= 120 or (low is not None and high is not None and low > high):
        return None
    text = (age_text or "").casefold()
    if low is not None and (age < low or (text.startswith("over ") and age == low)):
        return False
    if high is not None and (age > high or (text.startswith("under ") and age == high)):
        return False
    return True
