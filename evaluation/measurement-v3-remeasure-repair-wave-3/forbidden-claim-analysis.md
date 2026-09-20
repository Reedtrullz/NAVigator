# Wave-3 Forbidden-Claim Analysis

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3
Classification: BURNED_DEV_BASELINE_ONLY
Basis: frozen Wave-3 measurement, frozen Wave-2 measurement, wave2-wave3-transition-matrix.json.

## Resolution of the pending criterion

ROUT-026::forbidden:01, the single PENDING criterion from Wave 2, was blind dual-pass reviewed by Astra (reasoning LOW) and resolved as ABSENT via bounded Sol residual adjudication. Authority: LLM_ADJUDICATED. With this resolution all 600/600 criteria are authoritative in Wave 3; pending count is 0. This was the last PENDING_LLM_ADJUDICATION criterion in the remeasurement lineage.

## Verdict distribution

Verdict | Wave 2 | Wave 3
--- | --- | ---
ABSENT | 57 | 58
CLAIM_ABSENT_TAKEN | 59 | 59
PRESENT | 1 | 1
CLAIM_PRESENT | 2 | 2
PENDING | 1 | 0

The only distributional change is the resolved PENDING -> ABSENT. No forbidden criterion regressed and none improved in W3; the W3 repair did not touch retrieval.

## Remaining forbidden FAILs (3, unchanged since Wave 2)

1. DIS-100 (PRESENT, LLM_REVIEWED) - contamination-shaped text "Fant ingen registrerte kommunale tilbud..." inside cross-contaminated national-information blocks; also failed in Wave 1.
2. DIS-119 (CLAIM_PRESENT, deterministic lexical) - unchanged since Wave 1.
3. ROUT-042 (CLAIM_PRESENT, deterministic lexical) - unchanged since Wave 1; ROUT-042's critical_condition criterion simultaneously improved FAIL -> PASS in W3.

Forbidden lane has no new failures and no new improvements; the contamination-shaped DIS-100 mechanism persists.

