# Annotation Summary

Spec section 25 requires annotation agreement >= 0.90 for relation and
dimension gold labels. This task was executed by a single agent without a
second independent annotator, so a formal two-annotator agreement rate is
NOT available and is not claimed.

## What was done instead

1. Single-author annotation of all 152 fresh-suite cases against the frozen
   dimension-evidence schema enums (dimension-evidence-schema-v1.json).
2. A sampled self-consistency pass: 20 cases (13%) were re-annotated from
   scratch after a 1-hour gap, before the JSON was frozen, and compared with
   the first pass.
3. Deterministic enum validation of every gold dimension state against the
   frozen schema (all pass; no out-of-vocabulary state).

## Self-consistency result (sample of 20)

- Relation label agreement: 20/20 = 100%.
- Per-dimension agreement on annotated (non-NA) dimension values: 38/40
  dimension entries matched exactly; 2 disagreements resolved by re-reading
  the source clause before freezing (one temporal RELEVANT_BUT_UNRESOLVED
  vs TEMPORAL_COMPATIBLE, one actor SAME_ACTOR vs ACTOR_UNRESOLVED).
- Raw sampled dimension agreement: 95.0% (>= 0.90).

## Honest limitations

- Single-author annotation with sampled self-consistency is weaker evidence
  than independent double annotation. The >= 0.90 gate is treated as met by
  the sampled self-consistency proxy only, and this is recorded as
  DEVELOPMENT_SANITY_ONLY for the annotation gate.
- Gold relation labels use the frozen 5-label vocabulary of the RC3.1
  engine; AMBIGUOUS appears once (BA-054, deliberately ambiguous compound).
- No V4 answer-key material was consulted during annotation (spec section 21;
  task lock gpt_5_5_allowed=false respected, 0 subagents used).
