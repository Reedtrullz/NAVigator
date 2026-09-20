"""Schema validation for runtime results (stdlib-only subset validator).

Validates the frozen result contract in
data/local-discovery-runtime-result-v1.schema.json without adding a
jsonschema dependency. Covers the constructs the schema actually uses:
type, enum, required, pattern, minimum, minLength, items, properties,
and nested object definitions.
"""

import json
import re


def _type_ok(value, expected):
    if isinstance(expected, list):
        return any(_type_ok(value, t) for t in expected)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _validate(value, schema, path, errors):
    if "enum" in schema and value not in schema["enum"]:
        errors.append("%s: %r not in enum %s" % (path or "root", value, schema["enum"]))
        return
    expected = schema.get("type")
    if expected and not _type_ok(value, expected):
        errors.append("%s: expected type %s" % (path or "root", expected))
        return
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append("%s: does not match pattern" % (path or "root"))
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append("%s: shorter than minLength" % (path or "root"))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append("%s: below minimum" % (path or "root"))
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append("%s: missing required field %r" % (path or "root", req))
        props = schema.get("properties", {})
        for key, sub in props.items():
            if key in value:
                _validate(value[key], sub, "%s.%s" % (path, key) if path else key, errors)
    if isinstance(value, list):
        items = schema.get("items")
        if items:
            for i, item in enumerate(value):
                _validate(item, items, "%s[%d]" % (path, i), errors)


def validate_result(result, schema_path):
    """Return a list of human-readable validation errors (empty = valid)."""
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    errors = []
    _validate(result, schema, "", errors)
    return errors

