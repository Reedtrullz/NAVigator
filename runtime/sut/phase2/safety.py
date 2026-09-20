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


REQUIRED_KEYS = (
    "class_precedence",
    "class_signals",
    "class_collapse",
    "negation_guard",
)
CANONICAL_PRIORITIES = ("ACUTE_RISK_NOW", "URGENT_NOT_ACUTE", "NOT_ACUTE")


class TriageError(Exception):
    """Safety rules unavailable or invalid (FC-01)."""


def load_rules(path):
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as exc:
        raise TriageError("safety rules unavailable: %s" % exc) from exc
    try:
        rules = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise TriageError("safety rules corrupt: %s" % exc) from exc
    _validate(rules)
    rules["_sha256"] = hashlib.sha256(raw).hexdigest()
    return rules


def _validate(rules):
    for key in REQUIRED_KEYS:
        if key not in rules:
            raise TriageError("safety rules missing key %r" % key)
    if not isinstance(rules["class_signals"], dict) or not rules["class_signals"]:
        raise TriageError("class_signals missing or empty")
    for cls in rules["class_signals"]:
        if cls not in rules["class_collapse"]:
            raise TriageError("signal class %r has no collapse mapping" % cls)
    for cls, mapping in rules["class_collapse"].items():
        if mapping.get("priority") not in CANONICAL_PRIORITIES:
            raise TriageError("invalid collapse priority for %r" % cls)


def _contains(text, phrase):
    return re.search(r"\b" + re.escape(phrase) + r"\b", text) is not None


def _overlaps(span_a, span_b):
    return span_a[0] < span_b[1] and span_b[0] < span_a[1]


def _is_guarded(text, signal, span, guard, is_acute_class):
    """Negation guard: discard an acute-class signal occurrence when a
    negation pattern overlaps it or sits within the window before it.
    Occurrences inside a listed affirmative idiom are never guarded.
    """
    if not is_acute_class:
        return False
    for idiom in guard.get("non_negated_affirmative_idioms", []):
        for m in re.finditer(r"\b" + re.escape(idiom) + r"\b", text):
            if m.start() <= span[0] and span[1] <= m.end():
                return False
    window = int(guard.get("match_window_chars_before", 30))
    for pattern in guard.get("negation_patterns", []):
        for m in re.finditer(r"\b" + re.escape(pattern) + r"\b", text):
            pat_span = (m.start(), m.end())
            if _overlaps(pat_span, span):
                return True
            if 0 < span[0] - pat_span[1] <= window:
                return True
    return False


def classify(text, rules):
    hay = text.lower()
    guard = rules.get("negation_guard", {})
    matched_by_class = {}
    guarded = []
    for cls in rules["class_precedence"]:
        is_acute_class = (
            rules["class_collapse"].get(cls, {}).get("priority") == "ACUTE_RISK_NOW"
        )
        for signal in rules["class_signals"].get(cls, []):
            for m in re.finditer(r"\b" + re.escape(signal) + r"\b", hay):
                if _is_guarded(hay, signal, (m.start(), m.end()), guard, is_acute_class):
                    if signal not in guarded:
                        guarded.append(signal)
                else:
                    matched_by_class.setdefault(cls, [])
                    if signal not in matched_by_class[cls]:
                        matched_by_class[cls].append(signal)
        if matched_by_class.get(cls):
            return _result(cls, matched_by_class[cls], guarded, rules)
    return _result(None, [], guarded, rules)


def _result(safety_class, signals, guarded, rules):
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


def evaluate_safety(ctx, rules):
    """S2 stage body: classify the user query and set ctx safety state."""
    result = classify(ctx["input"]["user_query"], rules)
    ctx["safety"]["priority"] = result["priority"]
    ctx["safety"]["safety_class"] = result["safety_class"]
    ctx["safety"]["signals"] = result["signals"]
    ctx["safety"]["suppressed_routing"] = result["suppressed_routing"]
    ctx["safety"]["rule_file_sha256"] = rules["_sha256"]
    ctx["_s2"] = result
