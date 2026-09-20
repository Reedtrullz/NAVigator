"""V2.5 M2 validator + derivation adapter (frozen artifact candidate).

Reuses the frozen V2.2 core's span checker verbatim; substitutes only the
M2 intermediate schema (four independent sub-fields) required by the V2.5
decomposition contract. Final verdicts come from the frozen derivation table.
"""
import json
from pathlib import Path

import judge_core_v2_2 as jc

HERE = Path(__file__).parent
TABLE = json.loads((HERE / "deterministic-derivation-table.json").read_text())["rows"]
FIELDS = ["trigger_support", "non_trigger_support", "evidence_conflict", "evidence_sufficiency"]
ENUMS = {
    "trigger_support": {"PRESENT", "ABSENT", "UNRESOLVED"},
    "non_trigger_support": {"PRESENT", "ABSENT", "UNRESOLVED"},
    "evidence_conflict": {"YES", "NO", "UNRESOLVED"},
    "evidence_sufficiency": {"SUFFICIENT", "INSUFFICIENT", "UNRESOLVED"},
}


def derive(judgment):
    for row in TABLE:
        if all(row[f] == judgment[f] for f in FIELDS):
            return row["derived_state"]
    return "UNRESOLVED"


def validate_result_v2_5(dimension, parsed, sut_answer):
    if not isinstance(parsed, dict):
        raise ValueError("result must be object")
    inter = {k: parsed[k] for k in FIELDS}
    if set(parsed.keys()) != set(FIELDS) | {"evidence_spans", "note"}:
        raise ValueError("unexpected top-level keys: " + str(sorted(parsed.keys())))
    for f in FIELDS:
        if inter[f] not in ENUMS[f]:
            raise ValueError("invalid " + f + ": " + str(inter[f]))
    spans = parsed.get("evidence_spans") or []
    needs_span = inter["trigger_support"] == "PRESENT" or inter["non_trigger_support"] == "PRESENT"
    if needs_span:
        jc._check_spans(spans, {}, sut_answer)
    elif spans:
        raise ValueError("spans only allowed with PRESENT support")
    state = derive(inter)
    verdict = {
        "CLEAR_TRIGGER_SUPPORT": "TRIGGERED",
        "CLEAR_NON_TRIGGER_SUPPORT": "NOT_TRIGGERED",
    }.get(state, "UNRESOLVED")
    return {
        "dimension": dimension,
        "intermediate": inter,
        "verdict": verdict,
        "derivation_basis": "M2V25:" + state,
        "evidence_spans": spans,
        "note": str(parsed.get("note", ""))[:160],
    }
