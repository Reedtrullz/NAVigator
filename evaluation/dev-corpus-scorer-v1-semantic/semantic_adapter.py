#!/usr/bin/env python3
"""Scorer V1 semantic adapter: deterministic-first, judge kun paa UNRESOLVED.

Ingen deterministisk terminal verdi kan overstyres. Override-count skal
vaere 0 i alle integrajsonstester.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "dev-corpus-semantic-judge-v1"))
import semantic_judge as sj  # noqa: E402


class SemanticJudgeAdapter:
    """Drop-in judge for score_case med samme interface som stubben."""

    name = "SEMANTIC_JUDGE_V1_LIVE"

    def __init__(self):
        self.calls = 0
        self.overrides = 0
        self.unresolved = 0

    def paraphrase_forbidden(self, claim_norm, forbidden_norm):
        # Deterministic layer has already checked exact/alias match and
        # returned PRESENT for those. This hook is only consulted for
        # candidates that the stub would mark ABSENT_TAK with token overlap.
        self.calls += 1
        res = sj.semantic_verdict(
            "forbidden_claim",
            "Kandidatsystemets claims-liste.",
            "Forbudt paastand som systemet ikke maa fremsette: " + forbidden_norm,
            claim_norm,
        )
        verdict = res["verdict"]
        if verdict == "UNRESOLVED":
            self.unresolved += 1
        return verdict == "PRESENT"

    def route_equivalent(self, offered_norm, gold_route_norm):
        self.calls += 1
        res = sj.semantic_verdict(
            "route_equivalence",
            "Kandidatsystemets tilbudte rute.",
            "Akseptabel rute: " + gold_route_norm,
            offered_norm,
        )
        verdict = res["verdict"]
        if verdict == "UNRESOLVED":
            self.unresolved += 1
            return False
        return verdict in ("CANONICAL_ACCEPTABLE", "EQUIVALENT_ACCEPTABLE")

    def free_text_critical(self, condition, answer_blob_norm):
        self.calls += 1
        res = sj.semantic_verdict(
            "critical_condition",
            "Kandidatsystemets svar.",
            "Kritisk feil hvis: " + condition,
            answer_blob_norm,
        )
        verdict = res["verdict"]
        if verdict == "UNRESOLVED":
            self.unresolved += 1
        return verdict
