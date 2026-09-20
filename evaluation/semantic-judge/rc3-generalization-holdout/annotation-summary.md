# Annotation Summary

## Passes
- Pass 1 (deterministic author): case authors wrote claims against exact
  KB fact blocks with predefined truth codes; labels were derived by the
  build pipeline, never from snapshot output.
- Pass 2 (independent, model-assisted): GPT-5.6-Luna at temperature 0 via
  local proxy, one call per CORE case, received ONLY claim + evidence
  packet + annotation contract. 159/159 valid structured responses.
  Pass 2 never saw pass-1 labels; the checkpoint file contained only its
  own outputs.

## Contract repairs (bounded, before final run)
The first two agreement runs exposed real contract gaps, not noise:
1. Compound aggregation in the annotation contract contradicted the
   frozen runtime rule; aligned to routing.aggregate_atoms (uniform
   atoms keep class; any mix -> PARTIALLY_SUPPORTED) and fixed the same
   bug in the pass-1 builder.
2. Two documentation gaps were repaired and one clarification added:
   atoms scoped to compound claims only; genuine_insufficiency defined
   (true iff product action is ABSTAIN_INSUFFICIENT); silence vs
   contradiction codified (another stated value for the same quantity =
   CONTRADICTED; general rule not refuted by one dated example).
3. Temporal binding clarification: a claim binding a value to a period
   requires the evidence to bind the same value to the same period;
   otherwise the temporal part is unresolved.
After each repair, pass 2 was fully re-run (temperature 0) so both
final passes used the identical contract. No resolution was derived
from V4 labels or snapshot behavior.

## Final agreement (pre-adjudication, n=159)
| Gate | Result | Target |
|---|---|---|
| semantic | 91.82% | >=90% PASS |
| proof-safe | 91.19% | >=90% PASS |
| product | 90.57% | >=90% PASS |
| atom count | 100% | >=90% PASS |

## Adjudication
19/159 disputes resolved (11.95%, cap 35%), 0 unresolved. Each
resolution re-read the exact evidence packet and cites the contract
rule applied: 6 pass-1 upheld, 9 pass-2 upheld, 4 compound atom-level
corrections (one with a per-atom override). Full table:
construction-audit.sealed (adjudication.json).
