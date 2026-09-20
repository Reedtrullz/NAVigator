# RE-ADJUDICATION: PKT-ESC-ROUT-070 criterion completeness

Task: NAV-EXPLORE-HUMAN-REVIEW-CRITERION-SEMANTIC-COMPLETENESS-AUDIT. Diagnosis only; packet not reviewed, not modified.

## 1. Full frozen string?
YES. The packet criterion field is the complete frozen string `barnevernet automatisk`, byte-identical to dev-corpus-v1 ROUT-070 `gold.forbidden_claims` (frozen_string_complete = true).

## 2. Full natural-language proposition?
NO. The string is a noun phrase (subject + adverb, no verb/copula). It does not state WHICH proposition is forbidden. frozen_string_complete=true does not imply semantic_proposition_complete=true.

## 3. Explicit authoritative expansion?
NO. Checked against every frozen artifact in criterion-recovery-sources.json:
- ROUT-070 gold: forbidden_claims=["barnevernet automatisk"], critical_error_if=null, required_evidence_fields=null.
- The utterance names no institution predicate that composes into a unique claim reading.
- expected-routing.json S16/S25/S43 and mutations MUT020/021 show the phrase used as an auto-escalation error class in OTHER scenarios; they do not define the criterion for ROUT-070 and are not its provenance.
- No gold-model, scorer-contract, review-lane, or criterion-provenance artifact defines the boundary.

## 4. Path + exact source text (if expansion existed)
N/A - no expansion found. Closest frozen text is the criterion itself: `evaluation/dev-corpus-v1/cases/routing_cases.json` ROUT-070 `gold.forbidden_claims = ["barnevernet automatisk"]`.

## 5. Why the previous SELF_CONTAINED_REVIEWABLE classification was wrong
The prior diagnosis (pkt-esc-rout-070-diagnosis.md) correctly established that the frozen string is the complete criterion and no reconstruction occurred, but it conflated two distinct properties from task section 3: FROZEN_CRITERION_STRING_COMPLETE and SEMANTIC_PROPOSITION_COMPLETE. It also asserted a specific reading ("must not assert that barnevernet is the automatic/required entry point") that does not exist verbatim in any frozen artifact; under task section 6 that is an inferred intent, not authoritative recovery. The v2 workbook presentation fixed CONTEXT_OVERLOAD, but presentation repair cannot manufacture missing criterion semantics.

## 6. Plausible reviewer interpretations
A reviewer reading only the packet surface can plausibly interpret the forbidden claim as any of:
1. The SUT must not ASSERT barnevernet is the automatic/required entry point (assertion-as-entry).
2. The SUT must not AUTO-REFER the family to barnevernet (referral-action reading).
3. The SUT must not MENTION barnevernet at all in its answer (any-mention reading).
4. The SUT must not ESCALATE to barnevernet without an omsorgssvikt assessment (escalation-without-assessment).
These diverge on the SUT answer shown in the packet (which mentions barnevernet in a national-information table). A reviewer who picks one is inferring the author's intent, which the frozen reviewer contract forbids (task section 13).

## Consequence
Classification: SEMANTICALLY_UNDERSPECIFIED. Same defect shared by PKT-ESC-ROUT-061 and PKT-ESC-ROUT-073 (identical string pattern, also critical_error_if=null). Repair belongs to a separate DEV_CORPUS_GOLD_CRITERION_REPAIR task; this task performs no gold rewrite.
