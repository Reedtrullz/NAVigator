# Future blind holdout contract (holdout-v3 spec; NOT built here)

## Mandatory pre-exposure annotation

Every blind case carries four annotations before any evaluator or tuning agent sees the set:
1. semantic_truth (bounded-inference reading, CONFIRMED via two-pass)
2. proof_safe verdict under the frozen doctrine
3. required inference operator + class
4. expected product action (auto / review / abstain)

## Firewall

The agent/model tuning the evaluator must not see semantic or proof-safe answer keys before the system is frozen. Answer keys live in a separate access-controlled file; tuning sessions work from claims and sources only. Same blind principle as holdout-v2, extended to the dual keys.

## Second-pass policy

Legal, safety, bounded-inference, and implicit-contradiction cases require at least two independent annotation passes; pass disagreement -> ANNOTATION_DISPUTE and exclusion from scoring until resolved. Reviewer outputs are never used as answer keys.

## Reporting contract

Holdout results are reported per target (semantic accuracy, invalid-proof rate, product quality) with label_disagreement_rate and annotation_dispute_rate stated alongside. Single-number accuracy over the whole set is prohibited.
