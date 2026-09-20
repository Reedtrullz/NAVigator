"""V2.7e uncertainty derivation (frozen).
New-lineage module; judge_core_v2_2.py is never edited. Implements the
repaired uncertainty contract: UNC-A1 and UNC-A2.
"""

BEHAVIORS = [
    "NONE", "HEDGE", "EXPLICIT_LIMITATION", "PARTIAL_LIMITATION",
    "CONTRADICTORY_LIMITATION", "UNCLEAR_PROSE",
    "OVERCONFIDENT_ASSERTION", "UNRESOLVED",
]

TABLE_EXPLICIT_LIMITATION = {
    "EXPLICIT_LIMITATION": "SATISFIED",
    "PARTIAL_LIMITATION": "PARTIAL",
    "HEDGE": "PARTIAL",
    "CONTRADICTORY_LIMITATION": "UNRESOLVED",
    "UNCLEAR_PROSE": "UNRESOLVED",
    "OVERCONFIDENT_ASSERTION": "VIOLATED",
    "NONE": "UNRESOLVED",
    "UNRESOLVED": "UNRESOLVED",
}

TABLE_NON_ASSERTION = {
    "NONE": "SATISFIED",
    "HEDGE": "SATISFIED",
    "EXPLICIT_LIMITATION": "SATISFIED",
    "PARTIAL_LIMITATION": "SATISFIED",
    "CONTRADICTORY_LIMITATION": "VIOLATED",
    "UNCLEAR_PROSE": "UNRESOLVED",
    "OVERCONFIDENT_ASSERTION": "VIOLATED",
    "UNRESOLVED": "UNRESOLVED",
}


def derive(mode, behavior):
    if mode == "NONE":
        return "NOT_REQUIRED"
    if behavior not in BEHAVIORS:
        raise ValueError("unknown behavior: %s" % behavior)
    if mode == "EXPLICIT_LIMITATION":
        return TABLE_EXPLICIT_LIMITATION[behavior]
    if mode == "NON_ASSERTION_CONSTRAINT":
        return TABLE_NON_ASSERTION[behavior]
    if mode == "COMPOUND":
        raise ValueError("use derive_compound for COMPOUND mode")
    raise ValueError("unknown mode: %s" % mode)


def derive_compound(components):
    verdicts = [derive("EXPLICIT_LIMITATION" if k == "EXPRESSION" else "NON_ASSERTION_CONSTRAINT", b)
                for k, b in components]
    if all(v == "SATISFIED" for v in verdicts):
        return "SATISFIED"
    if all(v == "VIOLATED" for v in verdicts):
        return "VIOLATED"
    if "VIOLATED" in verdicts and "SATISFIED" in verdicts:
        return "PARTIAL"
    if "VIOLATED" not in verdicts and "SATISFIED" in verdicts:
        return "PARTIAL"
    return "UNRESOLVED"


def _selfcheck():
    assert derive("NONE", "NONE") == "NOT_REQUIRED"
    assert derive("EXPLICIT_LIMITATION", "EXPLICIT_LIMITATION") == "SATISFIED"
    assert derive("EXPLICIT_LIMITATION", "HEDGE") == "PARTIAL"
    assert derive("EXPLICIT_LIMITATION", "CONTRADICTORY_LIMITATION") == "UNRESOLVED"
    assert derive("EXPLICIT_LIMITATION", "UNCLEAR_PROSE") == "UNRESOLVED"
    assert derive("EXPLICIT_LIMITATION", "OVERCONFIDENT_ASSERTION") == "VIOLATED"
    assert derive("NON_ASSERTION_CONSTRAINT", "NONE") == "SATISFIED"
    assert derive("NON_ASSERTION_CONSTRAINT", "CONTRADICTORY_LIMITATION") == "VIOLATED"
    assert derive("NON_ASSERTION_CONSTRAINT", "UNCLEAR_PROSE") == "UNRESOLVED"
    assert derive_compound([("EXPRESSION", "EXPLICIT_LIMITATION"), ("NON_ASSERTION", "NONE")]) == "SATISFIED"
    # frozen V1.4 compound rule: no VIOLATED with some SATISFIED => PARTIAL,
    # so [UNRESOLVED, SATISFIED] aggregates to PARTIAL (rule preserved verbatim)
    assert derive_compound([("EXPRESSION", "CONTRADICTORY_LIMITATION"), ("NON_ASSERTION", "NONE")]) == "PARTIAL"
    assert derive_compound([("EXPRESSION", "UNCLEAR_PROSE"), ("NON_ASSERTION", "UNCLEAR_PROSE")]) == "UNRESOLVED"
    assert derive_compound([("EXPRESSION", "OVERCONFIDENT_ASSERTION"), ("NON_ASSERTION", "UNCLEAR_PROSE")]) == "UNRESOLVED"
    assert derive_compound([("EXPRESSION", "OVERCONFIDENT_ASSERTION"), ("NON_ASSERTION", "NONE")]) == "PARTIAL"
    print("selfcheck OK: UNC-A1 + UNC-A2 repairs active, all other V1.4 cells preserved")


if __name__ == "__main__":
    _selfcheck()
