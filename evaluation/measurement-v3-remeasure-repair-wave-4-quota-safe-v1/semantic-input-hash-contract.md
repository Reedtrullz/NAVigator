# Canonical semantic review input hash contract (WAVE4-QUOTA-SAFE-V1)

## Purpose

This contract defines the ONLY mechanical rule by which a historical frozen
semantic observation may be carried forward into the Wave-3 compatibility
bridge or the Wave-4 partial measurement. Fuzzy reuse is forbidden by the
task spec; reuse requires byte-exact reviewer-visible authority input.

## Canonical hash definition

For a semantic review packet P (any source lineage), compute:

```
semantic_review_input_hash = sha256(
    json.dumps(
        {
            "contract_version": P["contract_version"],
            "dimension": P["dimension"],
            "case_context": P["case_context"],
            "criterion": P["criterion"],
            "sut_output": P["sut_output"],
        },
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")
).hexdigest()
```

This reproduces the serialization style of the frozen review transport
(`json.dumps(obj, sort_keys=True, ensure_ascii=False)`, the same style the
frozen Wave-3 review runner used for record hashing).

## Field provenance (reviewer-visible authority content)

The frozen reviewer user prompt (Wave-3 `run_astra_review.py.user_prompt`)
shows the reviewer exactly five authority-relevant things:

1. the frozen per-dimension contract text, selected by `dimension` and
   pinned by `contract_version` (semantic-judge-contract-v1-4 for all
   eligible source lineages);
2. the response schema, likewise pinned by `dimension` +
   `contract_version`;
3. `case_context` (the case utterance);
4. `criterion` (verbatim gold criterion text);
5. `sut_output` (the full serialized SUT answer JSON, which contains all
   evidence-source text available to the reviewer).

Every one of these is covered by the canonical hash. No authority-relevant
reviewer input exists outside these fields. The reviewer system prompt and
transport configuration are model-side constants shared by all candidate
source lineages and are not per-packet authority content.

## Reuse rule

Carry a historical observation forward if and only if:

1. the new packet's canonical `semantic_review_input_hash` equals the
   historical packet's canonical hash, AND
2. the historical packet's stored `packet_sha256` matches its recomputed
   body hash in the frozen source lineage (source integrity), AND
3. the historical observation is authoritative and frozen
   (LLM_REVIEWED or LLM_ADJUDICATED; never pending, never partial).

Otherwise the criterion is `NEW_SEMANTIC_REVIEW_REQUIRED` and becomes
`PENDING_MODEL_REVIEW_QUOTA` in this task. No verdict-based selection,
no "almost identical" equivalence, no whitespace normalization, and no
agent judgment is permitted at any step.

## Eligible source lineages (preferred order)

1. `evaluation/measurement-v3-remeasure-repair-wave-3`
   (ASTRA_WAVE3_DUAL_PASS_CONSENSUS + SOL_WAVE3_DUAL_PASS_RESIDUAL_CONSENSUS)
2. `evaluation/measurement-v3-remeasure-repair-wave-2`
   (ASTRA_WAVE2_DUAL_PASS_CONSENSUS)
3. `evaluation/measurement-v3-human-review-batch-2-repaired`
   (ASTRA_BATCH1_DUAL_PASS_CONSENSUS)

All three use contract `semantic-judge-contract-v1-4`, lanes
`critical_condition` and `forbidden_claim`, and the same frozen
reviewer-visible packet shape. No other lineage is eligible in this task.

## No self-authority

Packets generated inside this task are never authority for this task. The
Wave-3 compatibility bridge reuses the HISTORICAL Wave-3 frozen
observations (the intended Phase A source); the Wave-4 pass reuses any
prior frozen lineage. In both cases the authority record comes from the
frozen source lineage's observation files, never from this task's own
packet generation.
