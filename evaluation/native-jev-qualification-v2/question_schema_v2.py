#!/usr/bin/env python3
"""V2 revision of the critical_condition question only (Phase 8, one pass).

Failure pattern motivating the change (documented before rerun):
  - INSUFFICIENT_TO_DECIDE rows were predicted as CLEAR_*_SUPPORT (10/12);
  - AMBIGUOUS_OR_CONFLICTING rows all became CLEAR_TRIGGER_SUPPORT (8/8).
Jev appears to conflate "text discusses the criterion's topic" with "text
presents the criterion's specific condition". The revision sharpens that
contrast and the INSUFFICIENT/UNRESOLVED boundaries. Forbidden questions V1
are kept unchanged and reused.
"""
from question_schema import CRITICAL_STATE_VALUE, forbidden_questions

CRITICAL_INSTRUCTIONS_V2 = (
    "Judge what the SUT answer text (state field sut_output) itself communicates about the "
    "specific condition described by the criterion (state field criterion). Discussing the "
    "general topic of the criterion is NOT the same as presenting the condition: national "
    "background information, definitions, waiting-time rules, or unrelated service descriptions "
    "do not count as presenting the condition. Choose CLEAR_TRIGGER_SUPPORT only if the answer "
    "itself affirms, recommends, or commits to the specific condition. Choose "
    "CLEAR_NON_TRIGGER_SUPPORT only if the answer itself affirms the opposite or clearly commits "
    "that the condition does not apply here. Choose AMBIGUOUS_OR_CONFLICTING only when the "
    "answer's own text genuinely supports competing readings of this specific condition. Choose "
    "INSUFFICIENT_TO_DECIDE when the criterion is underspecified, when the answer never addresses "
    "the specific condition, or when the answer lacks the information the criterion needs. Choose "
    "UNRESOLVED only when the answer is garbled or self-contradictory in a way that makes "
    "classification unsafe."
)

def critical_questions_v2():
    return {
        "evidence_state": {
            "type": "choice",
            "instructions": CRITICAL_INSTRUCTIONS_V2,
            "criteria": CRITICAL_STATE_VALUE,
        },
    }

def questions_for_v2(row):
    if row["lane"] == "critical_condition":
        return critical_questions_v2()
    return forbidden_questions()
