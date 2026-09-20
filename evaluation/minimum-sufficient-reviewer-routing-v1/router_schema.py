#!/usr/bin/env python3
"""A.6 frozen-candidate Jev router schema (burned development).

Jev role: difficulty / routing model ONLY. It predicts the tier where review
should START. It never decides correctness and never stops a review.

State fields are all available BEFORE any reviewer outcome is known:
criterion, case_context, sut_output, lane. No gold, no model results.
"""

REASONING_COMPLEXITY_LEVELS = {
    "0": "Direct semantic relation between criterion and answer text; little or no inference needed to judge it.",
    "1": "One simple distinction decides the judgment (for example present vs absent, or one clear polarity).",
    "2": "One substantive condition, exception, or role relationship must be applied correctly.",
    "3": "Several interacting conditions, or subtle polarity/negation, must be handled together.",
    "4": "Substantial ambiguity, or precise multi-part semantic reasoning, is needed before the judgment can be made.",
}

TIER_CHOICES = {
    "T1_BASIC": "A basic reviewer route is likely sufficient: the needed judgment is simple and the answer text is not adversarial.",
    "T2_INTERMEDIATE": "An intermediate reviewer route is a prudent starting point: one substantive condition or distinction matters.",
    "T3_STRONG": "A strong reviewer route is likely needed: interacting conditions, subtle polarity, or boundary semantics matter.",
    "T4_FRONTIER_RESERVE": "Only a frontier reviewer route can plausibly handle this; reserve this for extreme cases.",
    "UNCERTAIN": "The router cannot responsibly pick a tier from the available information.",
}

TIER_INSTRUCTIONS = (
    "You are a routing model, NOT a correctness judge. Predict where semantic review of this row "
    "should START so that expensive reviewers are used only when cheaper ones are unlikely to suffice. "
    "Under-predicting the needed tier is the dangerous error; over-predicting wastes cost. "
    "Judge the semantic difficulty of comparing the criterion (state field criterion) against the "
    "SUT answer text (state field sut_output), using the case context (state field case_context) "
    "and the review lane (state field lane). Do not try to decide whether the answer is correct.",
)

COMPLEXITY_INSTRUCTIONS = (
    "Rate the semantic reasoning complexity of judging this row: how much inference, condition "
    "tracking, polarity sensitivity, or ambiguity resolution does the criterion-vs-answer "
    "comparison require? Use the ordered level descriptions; pick the highest level that applies.",
)

NOUL_SIGNALS = {
    "negation_or_polarity_sensitive": "Does correctly judging this row depend on sensitive handling of negation or polarity in the answer text?",
    "exception_or_condition_sensitive": "Does correctly judging this row depend on an exception, qualification, or conditional clause?",
    "multiple_conditions_interact": "Do multiple conditions in the criterion or answer interact so that they must be combined correctly?",
    "actor_or_role_distinction_material": "Does correctly judging this row depend on distinguishing actors, roles, or who referred/initiated what?",
    "ambiguity_material_to_outcome": "Is ambiguity in the answer text material to the judgment outcome (not just stylistic)?",
    "semantic_boundary_case": "Is this row a semantic boundary case where similar-looking text has different correct judgments?",
    "requires_cross_context_integration": "Does the judgment require integrating information across the criterion, case context, and different parts of the answer?",
    "trigger_classification_sensitive": "Does the judgment hinge on whether a specific critical condition/trigger is actually presented in the answer?",
}

NOUL_INSTRUCTIONS = (
    'Answer each yes/no question about this row (criterion, case_context, sut_output, lane). '
    "These signals feed a conservative routing policy that escalates difficult rows to stronger "
    "reviewer tiers. Answer yes only when the property is genuinely present and material.",
)

def router_state(row):
    pkt = row["packet"]
    return {
        "criterion": pkt.get("criterion", ""),
        "case_context": pkt.get("case_context", ""),
        "sut_output": pkt.get("sut_output", ""),
        "lane": row.get("lane", ""),
    }

def router_questions():
    qs = {
        "reasoning_complexity": {
            "type": "score",
            "instructions": COMPLEXITY_INSTRUCTIONS,
            "criteria": [REASONING_COMPLEXITY_LEVELS[str(i)] for i in range(len(REASONING_COMPLEXITY_LEVELS))],
        },
        "predicted_starting_tier": {
            "type": "choice",
            "instructions": TIER_INSTRUCTIONS,
            "criteria": TIER_CHOICES,
        },
    }
    for name, crit in NOUL_SIGNALS.items():
        qs["signal_" + name] = {
            "type": "noul",
            "instructions": NOUL_INSTRUCTIONS,
            "criterion": crit,
        }
    return qs
