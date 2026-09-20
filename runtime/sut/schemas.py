"""Schema validation for the SUT canonical contracts.

Stdlib-only subset validator over the frozen schema copies in
runtime/sut/schemas/ (same pattern as runtime/discovery/schema.py,
extended with additionalProperties, minItems, maximum and local $ref).
"""

import json
import os
import re

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemas")

_SCHEMA_CACHE = {}


class SchemaError(Exception):
    pass


def _load_schema(name):
    if name not in _SCHEMA_CACHE:
        with open(os.path.join(SCHEMA_DIR, name), "r", encoding="utf-8") as f:
            _SCHEMA_CACHE[name] = json.load(f)
    return _SCHEMA_CACHE[name]


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


def _resolve_ref(ref, root):
    # Local refs only: "#/$defs/name".
    node = root
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def _validate(value, schema, path, errors, root):
    if "$ref" in schema:
        _validate(value, _resolve_ref(schema["$ref"], root), path, errors, root)
        return
    if "enum" in schema and value not in schema["enum"]:
        errors.append("%s: %r not in enum" % (path or "root", value))
        return
    expected = schema.get("type")
    if expected is not None and not _type_ok(value, expected):
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
        if "maximum" in schema and value > schema["maximum"]:
            errors.append("%s: above maximum" % (path or "root"))
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append("%s: missing required field %r" % (path or "root", req))
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append("%s: unknown field %r" % (path or "root", key))
        for key, sub in props.items():
            if key in value:
                _validate(value[key], sub, "%s.%s" % (path, key) if path else key, errors, root)
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append("%s: fewer than minItems" % (path or "root"))
        items = schema.get("items")
        if items:
            for i, item in enumerate(value):
                _validate(item, items, "%s[%d]" % (path, i), errors, root)


def _errors_for(doc, schema_name):
    schema = _load_schema(schema_name)
    errors = []
    _validate(doc, schema, "", errors, schema)
    return errors


def validate_input(doc):
    errors = _errors_for(doc, "sut-input.schema.json")
    if errors:
        raise SchemaError("sut-input/v1 invalid: " + "; ".join(errors))


def validate_output(doc):
    errors = _errors_for(doc, "sut-output.schema.json")
    if errors:
        raise SchemaError("sut-output/v1 invalid: " + "; ".join(errors))


def validate_context(doc):
    errors = _errors_for(doc, "decision-context.schema.json")
    if errors:
        raise SchemaError("decision-context-v1 invalid: " + "; ".join(errors))
