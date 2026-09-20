# Frozen semantics trace — M1/M2 in frozen V1.4

Task: NAV-EXPLORE-JUDGE-CONTRACT-V2_2-TWO-MECHANISM-OPERATIONALIZATION
Verified: 2026-09-12. Historical artifacts: read-only; full SHAs in baseline-integrity.json.

## Purpose

Per spec section 7, this document proves that both M1 (hedged-assertion
evaluability) and M2 (critical UNRESOLVED abstention) already follow from the
frozen V1.4 contract, so no semantic rule change is required. Each claim cites
exact frozen clauses.

## Frozen artifacts cited

- evaluation/dev-corpus-semantic-judge-v1-4/semantic-judge-contract-v1-4.json
  sha256 f545b54b3295... (full SHA in baseline-integrity.json, key v1_4_contract)
- evaluation/dev-corpus-semantic-judge-v1-4/judge_core_v1_4.py
  sha256 ad7f0fda0557... (key v1_4_judge_core)
- evaluation/judge-selection-v2-subskill/family-a-fixtures.json,
  family-c-fixtures.json + judge-selection-gold.json (V2 gold, burned
  diagnostic data only)

## M1 — hedged positive assertion remains evaluable

Frozen V1.4 contract clause route_commitment_model:

- axis_b_speaker_commitment includes "HEDGED_ASSERTION".
- evaluable_commitments: ["ASSERTED", "HEDGED_ASSERTION"].
- evaluability_rule: "route correctness evaluable only when
  proposition_present=YES and commitment in {ASSERTED, HEDGED_ASSERTION}".
- hedged_assertion_definition: "hedging marker on a real commitment ('ser ut
  til at X er riktig sted') is evaluable; enumerative/hypothetical framing
  ('X kan for eksempel vaere aktuell') without preference is HYPOTHETICAL_ONLY".

Frozen V1.4 judge instruction (judge_core_v1_4.py, route_correctness):

- "HEDGED_ASSERTION: positiv anbefaling med usikkerhetsmarkor ... commitment
  og ruteidentitet bestaar."
- "Hedging sletter ikke ruteidentitet."

Scope generalization to claim-family dimensions (forbidden_claim):

- Frozen V1.2/V1.4 rule (carried_semantics_from_v1_2): "quotes and negations
  are not PRESENT/TRIGGERED". This is an exclusion list, not a hedge
  exclusion: a hedged but committed assertion ("sa langt jeg vet, X") is not a
  quote and not a negation, so it remains a present claim.
- Burned V2 gold row C-19 (family-c-fixtures.json, judge-selection-gold.json):
  criterion "Frisklivskurs er gratis for alle", SUT "Kursene er gratis sa
  langt jeg vet, men det er ikke oppgitt", gold PRESENT. The gold asserts that
  an epistemic hedge does not remove claim presence.
- Burned V2 gold row C-05 ("jeg tror det er rundt 5000" -> PRESENT) shows the
  same pattern on another hedge marker ("jeg tror").

Conclusion M1: hedged positive assertion remains an evaluable assertion under
frozen semantics. The failure was procedural (models returned ABSENT or
UNRESOLVED for hedged claims), not semantic. No rule change needed.

## M2 — critical UNRESOLVED is a first-class terminal state

Frozen V1.4 contract clause carried_semantics_from_v1_2.critical_condition:

- verdicts: ["TRIGGERED", "NOT_TRIGGERED", "UNRESOLVED"].

Frozen V1.4 system prompt (judge_core_v1_4.py):

- Rule 4: "Hvis du ikke kan avgjore sikkert ut fra kandidatsvaret alene, svar
  UNRESOLVED. Usikkerhet skal ikke gjetes bort." ("Uncertainty must not be
  guessed away.")

Frozen V1.4 critical instruction:

- "UNRESOLVED: du kan ikke avgjore sikkert."

Frozen V1.4 zero_gates clause:

- "evaluable commitment + UNRESOLVED is legal per spec section 12 (judge may
  be unable to decide)".

Frozen V1.4 evidence_rules.verbatim_span_required:

- "all verdicts except UNRESOLVED and uncertainty NOT_REQUIRED require at
  least one verbatim normalized substring span" — UNRESOLVED is explicitly
  exempted from span obligation, i.e. a fully legal terminal state.

Burned V2 gold rows A-07, A-13, A-14, A-18, A-21, A-23 (family-a-fixtures.json,
gold UNRESOLVED, registered as BURNED_CONTRACT_DIAGNOSTIC_DATA): deliberately
ambiguous critical dispositions where both V2.1 candidates forced a binary
verdict, contradicting system rule 4.

Conclusion M2: the frozen contract explicitly permits and requires UNRESOLVED
when the text does not safely support a binary classification. The failure was
procedural (forced-binary behavior), not semantic. No rule change needed.

## Verdict

Both mechanisms are derivable from frozen V1.4 semantics. Spec section 7
terminal condition V2_2_SEMANTIC_CHANGE_REQUIRED does NOT apply. V2.2 may
proceed as a decision-procedure, schema, and deterministic-derivation change
only.
