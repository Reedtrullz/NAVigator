# Evaluation contract (SEMANTIC-JUDGE-EVALUATION-CONTRACT-REDESIGN)

Deliverable set for the dual-target evaluation contract. Original benchmark labels are preserved everywhere; no evaluator, aligner, reviewer, or adjudicator code was modified in this task.

## Files

| File | Content |
|---|---|
| TASK-LOCK.json | Task lock; set to COMPLETED when QA passes |
| evaluation-contract.md | The contract: semantic_truth / proof_safe / product-decision definitions, mismatch taxonomy, annotation rules |
| evaluation-contract.schema.json | JSON Schema (draft-07) for dual-label case files |
| oracle-46-dual-labels.json | 46 oracle cases, two-pass annotated (44 CONFIRMED, 2 ANNOTATION_DISPUTE) |
| novel-40-dual-labels.json | 40 novel-development cases; 8 oracle-overlap ids imported, 32 curated |
| ent-controls-dual-labels.json | ENT-A..D dual labels (spec 25; ENT-B/C annotated fresh) |
| operator-classification.json | The 15 inference operators classified; nothing implemented |
| operator-backlog.md | Operators sorted tier 1-3 by impact x safety x implementation confidence |
| historical-reinterpretation.md | Hybrid 87.57% recomputed under dual targets; quote-aligner v0.2 and reviewer v1.1 reinterpretations; 45-error reclassification |
| future-holdout-spec.md | Holdout-v3 contract and annotation firewall (not built) |
| metrics-spec.md | Semantic accuracy, proof safety, product quality, error costs, label-quality metrics |
| final-report.md | The 50-point SLUTTRAPPORT |

## Validate

Validate all dual-label files against the schema (falls back to structural checks if jsonschema is not installed):

    python3 - <<'PYEOF'
    import json
    try:
        import jsonschema
        have = True
    except ImportError:
        have = False
    base = 'evaluation/semantic-judge/evaluation-contract/'
    schema = json.load(open(base + 'evaluation-contract.schema.json'))
    for f in ['oracle-46-dual-labels.json', 'novel-40-dual-labels.json', 'ent-controls-dual-labels.json']:
        doc = json.load(open(base + f))
        if have:
            jsonschema.validate(doc, schema)
        else:
            assert doc['schema'] == 'evaluation-contract-dual-labels-v1' and len(doc['cases']) >= 1
        print(f, 'OK', len(doc['cases']))
    PYEOF

Frozen inputs referenced (never modified): hybrid/oracle-reasoning-probe/oracle-proof-ledger.json, oracle-packets.json, inference-operators.json, quote-aligner/v0.2/novel-development-set.json, ent-controls-set.json, ent-controls-expected.json, hybrid/results/hybrid-eval.json.
