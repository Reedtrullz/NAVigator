#!/usr/bin/env python3
"""RC2 fusion policy (Iteration B, bounded single fix).

RC1 routed every gated case to review and never auto-accepted a
reviewer verdict. Counterfactual band analysis on burned V1
(BURNED_BLIND_V1_DEVELOPMENT_ONLY, phase-b-band-results.json) shows:

  - reviewer SUPPORT at confidence >= 0.90: 32/32 semantic and product
    correct, zero false supports
  - reviewer CONTRA at >= 0.90: 30/31 (RC1B-0169, HIGH criticality)
  - every sub-0.90 band: near-zero accuracy (0/12 at 0.78-0.84)
  - engine-agreement conditioning halves accept volume with no gain

Policy: accept only reviewer SUPPORT at >= 0.90 when the deterministic
layer raised no specific defect evidence; everything else stays review.
Gate reasons are split into two classes: generic proof-thinness flags
(not_a_proof:*, engine_review_flag), which the counterfactual data
shows are safe to bypass for high-confidence SUPPORT, and specific
defect evidence (numeric_support_binding, compound_claim,
weak_support_rule:*, support_undercovered:*, weak span,
universal_quantifier_support, weak_contra_rule:*), which always veto.
Asymmetric by design: a wrong auto-SUPPORT creates an unsafe grant; a
wrong review costs human time only.
"""

AUTO_ACCEPT_CONF = 0.90

_GENERIC_FLAGS = ("not_a_proof:", "engine_review_flag")

_SPECIFIC_VETOES = ("numeric_support_binding", "compound_claim",
                    "weak_support_rule", "support_undercovered",
                    "support_weak_span", "universal_quantifier_support",
                    "weak_contra_rule")


def _gate_blocks(gate_reason):
    if not gate_reason:
        return False
    if gate_reason.startswith(_GENERIC_FLAGS):
        return False
    return gate_reason.startswith(_SPECIFIC_VETOES)


def fuse(reviewer_verdict, reviewer_confidence, gate_reason=None):
    """Return (semantic_verdict, product_action, route, reason)."""
    if (reviewer_verdict == "SUPPORTED"
            and isinstance(reviewer_confidence, (int, float))
            and reviewer_confidence >= AUTO_ACCEPT_CONF
            and not _gate_blocks(gate_reason)):
        return ("SUPPORTED", "AUTO_SUPPORTED", "auto", None)
    return ("REVIEW_REQUIRED", "REVIEW_REQUIRED", "review",
            gate_reason or "below_auto_accept_threshold")
