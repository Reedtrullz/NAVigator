# Presentation vs semantic product failure (READ-ONLY)

Task: NAV-EXPLORE-FULL-SUT-BURNED-BASELINE-FAILURE-ANALYSIS-V1
Created: 2026-09-16T02:01:56+02:00
Sources: frozen baseline criteria, frozen phase-3 predictions, frozen
product-diagnostics.json (111 SUCCESS / 9 EXECUTION_FAILED; discovery_invoked=0;
291/610 claims provenance-linked; 98 presented_as_complete).

## A. Semantic / product correctness failures

- 111 critical_condition FAIL + 5 UNRESOLVED (fail-closed), 6 forbidden FAIL, 2 uncertainty VIOLATED.
- Headline semantic mechanism: the SUT asserts "no offers found" as a structural
  state for every case (no_route_asserted=true in 120/120) while prose answers
  carry substantial national information. The scorer treats this as
  PREMATURE_ABSENCE (88) and NO_ACCEPTABLE_ROUTE (108/108 scored).
- 5 forbidden fails are LLM-confirmed assertions (DIS-100, DIS-116, DIS-118,
  DIS-119, ROUT-050); DIS-105 is a literal ROUTE_FULLY_VERIFIED block printed in
  the answer. ROUT-042 is a suspected negation false positive of the frozen
  lexical rule (ROOT_CAUSE_HYPOTHESIS; no gold change proposed).

## B. Routing / discovery failures

- discovery_invoked_n = 0 in frozen diagnostics: the discovery subsystem never
  produced structured results for any case, including all 25 discovery_adversarial
  cases (21 route FAIL, 4 NOT_APPLICABLE).
- This makes F2/F4 substantially downstream of one root: no structured route or
  provenance object is ever emitted. OBSERVED at interface level; whether the
  cause is retrieval, extraction, or assembly is a hypothesis (MEDIUM confidence).

## C. Provenance / evidence failures

- All predictions carry empty structured provenance arrays; answers end with
  "Ingen kilde kunne verifiseres." 291/610 claims are provenance-linked at the
  claim-object level.
- DIS-096 SOURCE_URL_REQUIRED_MISSING, 2 PROVENANCE_CHAIN_BROKEN, 38
  evidence_completeness rows below 1.0 (mean 0.6833; safety 0.15 is worst).

## D. Presentation / rendering defects (no frozen criterion fails because of these)

- Repeated "Nasjonal informasjon:" blocks in 98/120 answers (>=2 occurrences; 0
  answers with exactly 1).
- Fixed no-offers disclaimer in 111/120 answers, including cases whose prose
  contains concrete routes; juxtaposed with emergency numbers on safety cases.
- Irrelevant cross-domain material (pleiepenger, barnebidrag, skatteetaten,
  husbanken, bostotte, omsorgspenger) in 23/120 answers.
- Evaluation meta-text leakage in 1/120 answers (DIS-105 prints
  ROUTE_FULLY_VERIFIED plus frozen-protocol percentages).
- 98 answers presented_as_complete while carrying recoverable failures;
  9 EXECUTION_FAILED cases correctly did not present as complete.

## Key separation

1. Presentation noise (D) does not drive any frozen verdict; it degrades usability and must not be folded into semantic failure counts.
2. The prose/structured divergence (A+B) is the single most consequential observed defect: useful content exists in prose, but the machine-readable contract (routes, provenance, uncertainty fields) is empty or default, so both the scorer and any downstream consumer see failure.
3. Two items are measurement-side, not product failures: the 5 UNRESOLVED critical conditions (contract fail-closed behavior) and the suspected ROUT-042 negation false positive.
