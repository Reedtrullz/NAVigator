# Consensus Rule Analysis

Task: `NAV-EXPLORE-MEASUREMENT-V3-WAVE1-CONSENSUS-COMPARATOR-REPAIR-V1`

## Finding

`CONSENSUS_COMPARATOR_IMPLEMENTATION_DEFECT` (Branch A). The measurement
contract's consensus semantic for dual-pass LLM adjudication is primitive-level:
the two independent passes must agree on the AUTHORITATIVE_SEMANTIC fields
(`criterion_semantic_match`, `speaker_commitment`) and each pass must
independently satisfy schema/enum/evidence validation. This is the semantics
implemented by the frozen upstream consensus builders
(`build_primary_consensus.py`, `build_residual_consensus.py`,
`auth_fields()` equality) in the
`measurement-v3-remeasure-repair-wave-1` lineage.

The Wave-1 Sol residual task implemented a stricter task-local rule:
"A==B on all fields" / "A==B on entire result object". That wording appears only
in that task's own execution artifacts (`sol-adjudication-consensus.json`,
`sol-adjudication-frozen-observations.json`, its TASK-LOCK terminal summary) and
in no measurement contract, frozen spec, or persisted comparator. The residual
comparator was ephemeral, so the defect existed only in its run-time
implementation.

## Consequence

All four Sol residual packets had identical authoritative primitives across
passes A and B (and identical evidence spans); only the stochastic explanatory
`rationale` fields differed. Under the contract semantic these are semantic
consensus: 4/4 `LLM_CONSENSUS`. The four `PENDING_HUMAN_ADJUDICATION` rows
were therefore implementation artifacts of the stricter comparator, not
evidence of semantic disagreement. No new LLM calls, no third pass, and no
majority vote were needed; both passes were already independently validated.

## Deterministic replay

`build_comparator_replay.py` (zero LLM calls) re-validates all eight Sol
observation records against the frozen schema/enums/evidence rules, cross-checks
the old comparator's whole-object outcome, replays the corrected rule, and
derives final verdicts through the unmodified frozen kernel
(`judge_core_v2_13.derive_final`):

| Packet | match / commitment | Corrected-rule consensus | Derived verdict |
|---|---|---|---|
| PKT-ESC-DIS-118 | MATCH / ASSERTED | LLM_CONSENSUS | PRESENT |
| PKT-ESC-ROUT-026-F01 | MATCH / NEGATED | LLM_CONSENSUS | ABSENT |
| PKT-ESC-ROUT-031-F01 | NO_MATCH / UNRESOLVED | LLM_CONSENSUS | ABSENT |
| PKT-ESC-ROUT-037 | NO_MATCH / UNRESOLVED | LLM_CONSENSUS | ABSENT |

PRESENT is the FAIL state for forbidden_claim; ABSENT is the PASS state.

## Guardrails

Rationale remains EXPLANATORY_NON_AUTHORITATIVE in the field authority map and
can never break consensus or drive auto-route. The whole-object equality rule is
not deleted from history; it is preserved verbatim as task-local scope. No
historical artifact is rewritten and no measurement-contract amendment is
created (`MEASUREMENT_CONTRACT_CHANGED = false`).
