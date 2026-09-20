# Automatic packet router v2 (spec 19)

Implementation: packet_router.py (build_v2_packet). No new retrieval:
uses the existing aligner candidates() per claim atom (top_n=6), then
ranking/grouping/pruning/linking only.

## Pipeline

1. Atomize claim (existing engine atomization; falls back to whole claim).
2. Per atom: candidates(atom, source, top_n=6).
3. Global span registry with canonical-text dedup (max score kept).
4. Role tagging per span: CONDITION, EXCEPTION, NEGATION, MODALITY,
   NUMERIC, TEMPORAL, LOCALITY, ACTOR, MAIN_RULE.
5. Within-atom diversity: drop near-duplicates (Jaccard >= 0.8 on
   content tokens) before ranking.
6. Joint evidence sets: greedy span set with union token coverage
   >= 0.7, max 3 spans (distributed entailment support).
7. Relations: single_support (coverage >= 0.7), joint_support (member
   of evidence_set), else qualifier.
8. group_type: RULE_WITH_CONDITION / RULE_WITH_EXCEPTION when
   condition/exception terms or roles are present.
9. Global budget: spans ranked by atom-use count then score, keep
   max_spans; never orphan an atom (top evidence + joint set always
   kept).
10. S0 policy: include | no_s0 | fallback (S0 only when some atom has
    no evidence or joint coverage < 0.5, and source < 1200 chars).

## Output

packet-v2.1 JSON (see packet-schema.md). Reviewer v1.1 + syntactic
addendum receives it; deterministic fusion aggregates atom verdicts.

## Oracle approximation quality

Of the 45 Iteration-B error claims, rule-based oracle packets achieved
7/45 correct with the frozen reviewer; the automatic router achieved
1/45 (no_s0). The dominant residual is reviewer reasoning over
implicit/absent contradiction evidence, not span selection (see
final-report.md).
