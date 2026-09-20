# Comparator Metric Contract v2 (FROZEN 2026-09-08, pre-implementation)

This contract replaces the RC3.3 "strict vs verdict-consistent" dual
reading. After this freeze there is exactly one authoritative comparator
metric. No metric-definition change is permitted for the rest of the task.

## M1. NUMERIC_RELATION_ACCURACY

Final semantic-relation correctness (ENTAILS / CONTRADICTS /
RELATED_BUT_INSUFFICIENT / PARTIAL / AMBIGUOUS per the canonical relation
contract) on ALL numeric cases. This is the primary numeric metric.

## M2. COMPARATOR_STATE_ACCURACY

Scored ONLY on the subset where comparator_applicable = true (gold). For
those cases the comparator relation that decides the numeric relation must
match gold. Where comparator_applicable = false the comparator state scores
N/A and is excluded from this metric; NUMERIC_RELATION_ACCURACY still
applies normally.

## Applicability rule (frozen)

comparator_applicable = true KUN when ALL hold:

1. claim and source both express numeric constraints;
2. they concern the same semantic quantity;
3. relevant actor/object/scope is compatible;
4. relevant temporal applicability overlaps (no historical-vs-current
   mismatch and no unresolved temporal status on either side);
5. the comparator relation is actually needed to decide the numeric
   relation (not derivable from identity, aggregation, or arithmetic alone).

If any condition fails: comparator_applicable = false, comparator state N/A.

## Per-case gold fields (targeted corpus)

- final semantic relation
- semantic quantity identity (type:unit:value[:qualifier])
- temporal applicability (CURRENT_MATCH / HISTORICAL_VS_CURRENT / SUPERSEDED / PERIOD_MISMATCH / UNKNOWN / NOT_APPLICABLE)
- quantity status (CURRENT / HISTORICAL / SUPERSEDED / FUTURE / UNKNOWN)
- comparator_applicable (bool)
- comparator relation (only when applicable)
- aggregate_component_role
- supporting spans

## Rationale (pre-blind, no V4 targets)

The single RC3.3 CONTRADICTS false positive was a stale-amount conflict:
different temporal statuses were treated as the same comparable quantity.
The applicability gate separates "different number, same quantity, same
time window" (comparable, may contradict) from "different number, different
time window" (not comparable, fails closed to RBI/unresolved).
