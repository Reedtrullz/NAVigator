# Evaluation contract: semantic_truth vs proof_safe

Task: SEMANTIC-JUDGE-EVALUATION-CONTRACT-REDESIGN. This contract separates what is semantically true from what a production evaluator can prove, and defines separate metrics for each plus product-decision quality.

## Why single-target evaluation failed

The oracle probe showed 33/46 (71.7%) benchmark labels diverge from doctrine-consistent verdicts, and reviewer v1.1 scored 20.8% against benchmark labels but 91.7% against doctrine. A single benchmark label cannot serve both as semantic ground truth and as a production-safety gate; it forced every artifact into one undifferentiated accuracy number.

## semantic_truth

The most natural reading of the evidence when small, reasonable inferences are allowed. Labels: SUPPORTED / CONTRADICTED / PARTIALLY_SUPPORTED / INSUFFICIENT_EVIDENCE.

Allowed inferences (bounded): explicit synonymy; simple definition -> instance (identity/inclusion only); rule + condition; explicit exhaustive list -> exclusion; simple multi-span conjunction; necessary logical implications; transitive paraphrase chains of at most small steps.

Not allowed: external world knowledge; closed-world assumptions from unmarked lists; implicit legal knowledge absent from the source; commonsense premises without evidence.

## proof_safe

What the evaluator may conclude with an explicitly validatable proof under current doctrine. Labels: SUPPORTED / CONTRADICTED / INSUFFICIENT / REVIEW_REQUIRED (PARTIAL kept as an explicit aggregation result, not a proof form). proof_safe is always equal to or more cautious than semantic_truth. A case with semantic_truth=CONTRADICTED and proof_safe=INSUFFICIENT is a desired state: a human would read a contradiction, but the system correctly refrains from auto-concluding.

## product_decision

The fusion layer chooses auto-decision vs review vs abstention. Correctness is judged against the proof-safe target: auto is right iff the verdict matches proof_safe; review is right iff semantic and proof-safe targets diverge (or the operator is REVIEW_ONLY); unnecessary review is an efficiency cost, not a safety failure.

## Mismatch taxonomy (spec 6)

BOUNDED_INFERENCE_NOT_IMPLEMENTED; DOCTRINE_INTENTIONALLY_CONSERVATIVE; EVIDENCE_MISSING; EXPECTED_LABEL_OVERREACH; BENCHMARK_SCHEMA_PROBLEM; AGGREGATION_DIFFERENCE; TRUE_REVIEWER_ERROR.

## Case schema

See evaluation-contract.schema.json. Required fields per case: case_id; set; original_benchmark_label; semantic_truth{label, required_inference}; proof_safe{label, reason}; annotation_status; justification. Original labels are never rewritten or removed.

## Annotation rules

At least two passes on all C/E cases and every semantic-vs-proof disagreement; disagreement -> ANNOTATION_DISPUTE (never force a label). Reviewer output is never used as the answer key. Future blind holdouts get all four annotations (semantic, proof-safe, required operator, expected product action) before any evaluator sees the set, with an annotation firewall.

## Error-cost model (spec 21)

Critical: false auto-SUPPORTED. Very severe: false auto-CONTRADICTED (legal/safety). Moderate: unnecessary REVIEW_REQUIRED. Low: semantic miss without auto-decision.
