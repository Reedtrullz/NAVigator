"""Deterministic S2 safety triage (Phase 2).

Loads the frozen data/safety-triage-rules-v2.json vocabulary, evaluates the
internal 12-value safety_class taxonomy with precedence and an allowlist
negation guard, and collapses to the canonical 3-value output enum.

FC-01: a missing, corrupt, or structurally invalid rules file raises
TriageError; the pipeline maps that to the INTERFACE_GAP-001 fail-closed
output mapping (no ordinary verified recommendation).
"""

import hashlib
import json
import re
from typing import TypedDict, cast
from runtime.type_support import object_mapping, string, strings
from .contracts import Context, SafetyResult


class Guard(TypedDict, total=False):
    non_negated_affirmative_idioms: list[str]
    negation_patterns: list[str]
    match_window_chars_before: int


class CollapseMapping(TypedDict):
    priority: str
    suppressed_routing: bool


class SafetyRules(TypedDict):
    class_precedence: list[str]
    class_signals: dict[str, list[str]]
    class_collapse: dict[str, CollapseMapping]
    negation_guard: Guard
    _sha256: str

from .text_normalization import normalize_match_text


REQUIRED_KEYS = (
    "class_precedence",
    "class_signals",
    "class_collapse",
    "negation_guard",
)
CANONICAL_PRIORITIES = ("ACUTE_RISK_NOW", "URGENT_NOT_ACUTE", "NOT_ACUTE")


class TriageError(Exception):
    """Safety rules unavailable or invalid (FC-01)."""


def load_rules(path: str) -> SafetyRules:
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as exc:
        raise TriageError("safety rules unavailable: %s" % exc) from exc
    try:
        decoded = cast(object, json.loads(raw.decode("utf-8")))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise TriageError("safety rules corrupt: %s" % exc) from exc
    rules = _validate(decoded)
    rules["_sha256"] = hashlib.sha256(raw).hexdigest()
    return rules


def _validate(value: object) -> SafetyRules:
    try:
        fields = object_mapping(value)
        for key in REQUIRED_KEYS:
            if key not in fields:
                raise TriageError("safety rules missing key %r" % key)
        signals = {cls: strings(values) for cls, values in object_mapping(fields["class_signals"]).items()}
        if not signals:
            raise TriageError("class_signals missing or empty")
        collapse: dict[str, CollapseMapping] = {}
        for cls, raw in object_mapping(fields["class_collapse"]).items():
            mapping = object_mapping(raw)
            priority = string(mapping.get("priority"))
            suppressed = mapping.get("suppressed_routing")
            if priority not in CANONICAL_PRIORITIES or not isinstance(suppressed, bool):
                raise TriageError("invalid collapse mapping for %r" % cls)
            collapse[cls] = {"priority": priority, "suppressed_routing": suppressed}
        if any(cls not in collapse for cls in signals):
            raise TriageError("signal class has no collapse mapping")
        guard = object_mapping(fields["negation_guard"])
        return {
            "class_precedence": strings(fields["class_precedence"]),
            "class_signals": signals, "class_collapse": collapse,
            "negation_guard": {
                "non_negated_affirmative_idioms": strings(guard.get("non_negated_affirmative_idioms", [])),
                "negation_patterns": strings(guard.get("negation_patterns", [])),
            },
            "_sha256": "",
        }
    except ValueError as exc:
        raise TriageError("invalid safety rules structure") from exc


def _overlaps(span_a: tuple[int, int], span_b: tuple[int, int]) -> bool:
    return span_a[0] < span_b[1] and span_b[0] < span_a[1]


def _is_guarded(text: str, span: tuple[int, int], guard: Guard, is_acute_class: bool) -> bool:
    if not is_acute_class:
        return False
    for idiom in guard.get("non_negated_affirmative_idioms", []):
        for m in re.finditer(r"\b" + re.escape(normalize_match_text(idiom)) + r"\b", text):
            if m.start() <= span[0] and span[1] <= m.end():
                return False
    for pattern in guard.get("negation_patterns", []):
        for m in re.finditer(r"\b" + re.escape(normalize_match_text(pattern)) + r"\b", text):
            pat_span = (m.start(), m.end())
            if _overlaps(pat_span, span):
                return True
    return False


def classify(text: str, rules: SafetyRules) -> SafetyResult:
    hay = normalize_match_text(text)
    guard = rules.get("negation_guard", {})
    matched_by_class: dict[str, list[str]] = {}
    guarded: list[str] = []
    for cls in rules["class_precedence"]:
        is_acute_class = (
            rules["class_collapse"].get(cls, {}).get("priority") == "ACUTE_RISK_NOW"
        )
        for signal in rules["class_signals"].get(cls, []):
            for m in re.finditer(r"\b" + re.escape(normalize_match_text(signal)) + r"\b", hay):
                if _is_guarded(hay, (m.start(), m.end()), guard, is_acute_class):
                    if signal not in guarded:
                        guarded.append(signal)
                else:
                    _ = matched_by_class.setdefault(cls, [])
                    if signal not in matched_by_class[cls]:
                        matched_by_class[cls].append(signal)
        if matched_by_class.get(cls):
            return _result(cls, matched_by_class[cls], guarded, rules)
    return _result(None, [], guarded, rules)


def _result(safety_class: str | None, signals: list[str], guarded: list[str], rules: SafetyRules) -> SafetyResult:
    if safety_class is None:
        collapse = rules["class_collapse"]["NON_ACUTE_ROUTINE"]
        return {
            "safety_class": "NON_ACUTE_ROUTINE",
            "priority": collapse["priority"],
            "signals": [],
            "suppressed_routing": collapse["suppressed_routing"],
            "guarded_signals": guarded,
        }
    collapse = rules["class_collapse"][safety_class]
    return {
        "safety_class": safety_class,
        "priority": collapse["priority"],
        "signals": list(signals),
        "suppressed_routing": collapse["suppressed_routing"],
        "guarded_signals": guarded,
    }


def evaluate_safety(ctx: Context, rules: SafetyRules) -> None:
    """S2 stage body: classify the user query and set ctx safety state."""
    result = classify(ctx["input"]["user_query"], rules)
    ctx["safety"]["priority"] = result["priority"]
    ctx["safety"]["safety_class"] = result["safety_class"]
    ctx["safety"]["signals"] = result["signals"]
    ctx["safety"]["suppressed_routing"] = result["suppressed_routing"]
    ctx["safety"]["rule_file_sha256"] = rules["_sha256"]
    ctx["_s2"] = result
