# B.AI Semantic Reviewer Qualification V3

Task: NAV-EXPLORE-SEMANTIC-REVIEWER-BAI-QUALIFICATION-V3
Terminal status: NO_BAI_LOW_COST_MODEL_QUALIFIES

Owner-authorized bounded test of exactly two B.AI candidates (glm-5.3-flash,
deepseek-v4-flash-vision-exp) against the frozen V1 qualification standard used
by V1/V2/Luna. No gates, corpus, contract, or thresholds were changed.

## Results

- BAI-GLM: failed Stage 1 screening in both lanes (schema_valid_rate 0.9434
  forbidden / 0.8919 critical vs required 1.0).
- BAI-DEEPSEEK: failed forbidden lane at screening (0.9057); passed critical
  screening, then failed Stage 2 dual-pass on the frozen critical gates:
  29 unique evidence-invalid rows (max 0), 9 consensus-vs-reference errors
  (max 0), 33 pass-level errors (max 3), 5 dual-field disagreements (max 0),
  safety subset 37/39 with 2 UNDER_ESCALATION errors (max 0). Catastrophic
  false-trigger consensus: 0.

Per the frozen no-best-of-bad rule no candidate was selected. Stability
(Stage 3) was not run: the frozen stage order admits only fully qualified
candidates. No cascade simulation or router proposal was issued (spec
sections 15-16 apply to qualified candidates only).

Operational viability is reported separately: BAI-DEEPSEEK was transport-clean
across 340 calls (0x429/402/403, 0 invalid JSON); BAI-GLM showed chronic
invalid-review friction. Operational viability does not confer semantic
qualification.

## Key artifacts

- final-report.md - 38-point terminal report per spec section 19
- lane-qualification-results.json - per candidate/lane qualification state
- dual-pass-scorecard-v3.json - frozen gate application to dual-pass outputs
- disagreement-analysis.json - mechanical failure enumeration
- disagreement evidence: all INVALID_MODEL_REVIEW rows are verbatim-span
  violations (evidence_valid=false), not parse failures
- cost-analysis.json - token/call profile only; no pricing exposed
- transport-screen-results.json / semantic-screen-results.json /
  screening-scored-v3.json / full-qualification-results.json - frozen raw data

## Hard-rule attestation

ASTRA_CALLS=0, SOL_CALLS=0, LUNA_CALLS=0, GPT_5_5_CALLS=0; no OpenRouter or
OpenCode fallback; no silent model substitution; no router activation; no
historical measurement or SUT/gold changes; fresh cases consumed: 0.

This lineage is closed. Any further reviewer-candidate testing, gate changes,
or product integration requires a new explicit owner-authorized task.
