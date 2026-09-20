#!/usr/bin/env python3
"""Jev question schema V1 for NAV Explore semantic review qualification.

Lane-specific fan-out over one shared state per case (native System One parallel
questions). Norwegian criteria mirror the frozen measurement contract wording;
criteria are contrastive per the installed Jev skill guidance.
"""

CRITICAL_STATE_VALUE = {
    "CLEAR_TRIGGER_SUPPORT": "The candidate clearly presents the condition described by the criterion, either directly, as a paraphrase, or as a hedged but committed presentation.",
    "CLEAR_NON_TRIGGER_SUPPORT": "The candidate clearly does NOT present the condition: it excludes it, negates it, or mentions it only as a third-party quote without its own endorsement.",
    "AMBIGUOUS_OR_CONFLICTING": "The candidate text supports competing readings; you cannot honestly choose either clear state.",
    "INSUFFICIENT_TO_DECIDE": "The candidate lacks the information the criterion needs for classification.",
    "UNRESOLVED": "The state itself is not safely decidable from the candidate.",
}

CRITICAL_INSTRUCTIONS = (
    "You are judging whether the SUT answer text (state field sut_output) presents the condition "
    "described by state field criterion. The criterion describes a condition that would make the "
    "answer critically wrong IF that condition is semantically present in the answer. Judge the "
    "evidence basis in the answer text itself: does the answer clearly present the condition, clearly "
    "not present it, support competing readings, or lack the information needed? Hedged but committed "
    "presentation counts as presenting. Third-party quotes without endorsement do not."
)

def critical_questions():
    return {
        "evidence_state": {
            "type": "choice",
            "instructions": CRITICAL_INSTRUCTIONS,
            "criteria": CRITICAL_STATE_VALUE,
        },
    }

FORBIDDEN_MATCH = {
    "MATCH": "The criterion proposition is semantically present in the candidate answer text.",
    "NO_MATCH": "The criterion proposition is not semantically present in the candidate answer text.",
    "UNRESOLVED": "It is genuinely unclear whether the criterion proposition is present; competing readings are equally supported.",
}

FORBIDDEN_COMMIT = {
    "ASSERTED": "The answer itself commits to the proposition as true or recommended.",
    "NEGATED": "The answer treats the same proposition as not holding, rejects it, or presents the opposite.",
    "UNRESOLVED": "No clear commitment either way can be established from the answer text.",
}

FORBIDDEN_INSTRUCTIONS = (
    "Two judgments about the SUT answer text (state field sut_output) relative to the forbidden "
    "criterion (state field criterion). First: is the criterion proposition semantically present in "
    "the answer at all? Second: if present, does the answer itself commit to it, or does the answer "
    "reject, negate, or distance itself from it? A proposition that appears only inside a quoted third-party "
    "source, inside a table of national information, or as something the answer explicitly rules out is "
    "present only if the answer endorses or relies on it. Judge the answer's own communicative intent."
)

def forbidden_questions():
    return {
        "criterion_semantic_match": {
            "type": "choice",
            "instructions": FORBIDDEN_INSTRUCTIONS + " First judgment: presence of the proposition.",
            "criteria": FORBIDDEN_MATCH,
        },
        "speaker_commitment": {
            "type": "choice",
            "instructions": FORBIDDEN_INSTRUCTIONS + " Second judgment: the answer's own commitment to the proposition.",
            "criteria": FORBIDDEN_COMMIT,
        },
    }

def generic_state(row):
    return {
        "criterion": row["criterion"],
        "case_context": row["packet"]["case_context"],
        "sut_output": row["state_sut_for_jev"],
    }
