# Measurement V3 Mapping

SUT output field -> Measurement V3 input/criterion. Mapping direction: the SUT
emits; the frozen scorer + combined engine consume. No evaluator metadata ever
flows into the SUT.

## Scorer raw-answer consumption (dev-corpus-scorer-v1)

| Measurement needs | SUT output field | Status |
|---|---|---|
| routes (list) | routes | direct structured field |
| claims (list) | claims | direct structured field |
| uncertainty_expressed (list) | uncertainty_expressed | direct structured field |
| evidence (dict) | evidence | direct structured field |
| execution_status | execution_status | direct structured field |
| safety_priority (safety corpus critical rule R1) | safety_priority | direct structured field (mirror of safety.priority) |
| no_route_asserted (routing critical rule) | no_route_asserted | direct structured field |
| presented_as_complete (failed-execution critical rule) | presented_as_complete | direct structured field |

Normalize guard compliance: scorer _normalize_raw_answer requires routes list,
claims list, uncertainty_expressed list, evidence dict. sut-output/v1 types
match exactly.

## Capability flags (runner-side, not SUT)

| Corpus family | Capability key | Source |
|---|---|---|
| safety_cases | safety | runner config, not from SUT output |
| routing_cases | routing | runner config |
| discovery_adversarial_cases | local_discovery | runner config |

The runner sets capabilities per corpus family from the harness config
(execution-harness-design.md); the SUT does not self-declare capability.

## Human-review lane inputs (M2 + V2.15)

| Lane needs | SUT output field | Status |
|---|---|---|
| sut_output text (verbatim span validation) | answer | direct; quoted spans must be substrings |
| raw answer JSON for context | whole output object | serialized by the runner for the lane |

Span rule: evidence_span values that the answer quotes are verbatim
substrings of answer (S10 guarantee). Lanes validate against sut_output.

## Item identity + provenance for audit

| Engine needs | Source | Status |
|---|---|---|
| case identity | case_id (input) echoed by runner in prediction record | runner-supplied |
| prediction provenance | runner execution log (harness metadata, not SUT output) | runner-supplied |

## Missing metadata (evaluator-side, explicitly out of SUT scope)

| Measurement needs | Status | Owner |
|---|---|---|
| M2-workflow classification per critical-condition item | missing in corpus; currently synthetic | follow-up evaluator task; SUT never emits it |
| gold fields (GOLD_FIELDS) | present in corpus, stripped by loader before SUT | scorer reads gold only |

## Derived fields (no new SUT burden)

| Measurement criterion | Derived from |
|---|---|
| forbidden-claim presence | claims + answer text (scorer-side lexical/judge logic, frozen) |
| route acceptability | routes (scorer-side alias matching, frozen) |
| uncertainty satisfaction | uncertainty_expressed + claims blob (frozen scorer logic) |
| required evidence fields | evidence map keys (frozen scorer logic) |

All derived evaluation logic already lives in the frozen scorer. The SUT adds
nothing for these; it only supplies honest structured fields.

## Completeness check

Every field consumed by run_scorer_item / run_m2_item / run_semantic_item is
accounted for above as direct structured, runner-supplied, evaluator-side
missing-metadata, or frozen-scorer-derived. GOLD_VISIBLE_TO_SUT = 0 holds:
gold appears nowhere in sut-input/v1 or sut-output/v1.
