# NAV-EXPLORE-REVIEWER-MINIMUM-TIER-FRESH-BATCH-V1 — TASK SPEC DRAFT

Status: DRAFT_NOT_AUTHORIZED. Nothing in this file may be executed,
generated, or called until the owner authorizes the task by exact
SHA. No subagents, no model calls, no fixture generation, no dataset
construction before authorization.

## 0. Purpose and hypothesis

Empirical question this batch exists to answer:

> How far down the reviewer-tier ladder (T1 -> T2 -> T3) can we go
> before a stronger model is actually required?

Default hypothesis to falsify (pre-registered):

> Astra / frontier tier (T4) is NOT a necessary reviewer tier for this
> corpus. For every fresh row, at least one of T1/T2/T3 is sufficient.

Basis: routing-v1 Stage 0 found 0 empirically demonstrated
T4-required rows (all 26 T3=FAILED rows had a cheaper tier SUFFICIENT
or UNRESOLVED). The hypothesis is falsified only if a fresh row has a
frozen gold, T1+T2+T3 all definitively FAILED against it, and the
failure is adjudicated (human for safety-critical).

Consequence: the entire batch runs with ASTRA_CALLS = 0. A row where
T1+T2+T3 all fail against frozen gold is labeled >T3 WITHOUT calling
Astra. Astra is never called to "confirm" anything in this task.

## 1. Scope and lineage

- Task ID: NAV-EXPLORE-REVIEWER-MINIMUM-TIER-FRESH-BATCH-V1
- Predecessor (immutable, CLOSED): NAV-EXPLORE-MINIMUM-SUFFICIENT-REVIEWER-ROUTING-V1,
  terminal ROUTER_V1_INSUFFICIENT_REVIEWER_EVIDENCE, label set SHA
  4cd87708c79c44ce8a424b1feee491727096dbfd4edc55e0985a3a26fc64902e.
- Tiers inherit frozen definitions (routing-v1 report):
  T1_BASIC = mimo-v2.5-pro, laguna-s-2.1, ling-3.0-flash-sante;
  T2_INTERMEDIATE = bai-deepseek, nex-n2.5-pro; T3_STRONG = luna-high,
  luna-max; T4 = Astra (reserved, NOT called).
- Ladder rule inherits frozen definition: minimum sufficient tier =
  cheapest tier SUFFICIENT with all cheaper tiers definitively FAILED.
- This batch produces EVIDENCE (fresh rows + gold + empirical minimum
  tier labels). It does NOT train, tune, or evaluate any router.
  Jev/router work is explicitly deferred to a later task.

## 2. Hard invariants

- ASTRA_CALLS = 0. T4 is never invoked for any reason.
- NO GPT-5.5, no LongCat, no unapproved model escalation.
- Frozen gold per row is committed BEFORE any tier model sees the row.
- No gold change after tier evaluation starts (except pre-registered
  human adjudication flow, section 5).
- No runtime/cascade/reviewer changes in NAV Explore product.
- 0 subagents unless owner authorizes them at execution time.
- Every tier verdict is persisted with raw response + parsed verdict +
  SHA, one run per model per row (single-run labels; stability is a
  later question, not this batch's objective).

## 3. Dataset construction

Target size: 250-350 fresh rows. All rows must be NEW (not present in
the 375-row burned pool: V2 140 + V3 235; row-level overlap check is a
construction gate, target overlap = 0).

Stratified construction plan (sample families to build, not labels to
optimize):

| Family | Target rows | Note |
|---|---|---|
| MATCH / ASSERTED positive | ~50 | historically weakest cheap-model lane |
| CLEAR_TRIGGER_SUPPORT / safety-critical boundary | ~150 | sized for statistical upper bound; human-adjudicated gold |
| Referral / actor distinction | ~30 | routed vs performed, who refers whom |
| Negation / polarity | ~30 | support phrase + negation, not-required |
| UNRESOLVED-intentional | ~20 | ambiguity must be intentional and explainable |
| Exception / condition clauses | ~30 | only-if, bare-dersom, per-atom qualifiers |
| Multi-condition / compound | ~20 | conjunction, per-atom gating |
| Simple control rows | ~20 | semantically easy; anchor the low end of the ladder |

Constraints:
- Gold distribution must NOT be pre-optimized toward any tier mix.
  Stratification is by semantic family only.
- Each row carries: case_id (fresh namespace, no V2/V3 case IDs),
  semantic family, source/derivation provenance, gold commit SHA,
  safety_critical flag.
- Construction is deterministic and scripted; the builder script and
  dataset freeze with SHAs before any model call.

## 4. Gold authority (two lanes)

- Lane H (human): ALL safety-critical rows (~150). Human adjudication
  by owner against written per-row criterion text, single canonical
  verdict + evidence span, blind to any model output (rows have not
  been shown to any model at gold time). Recorded via the established
  mechanical-transcription pattern (owner decides, agent transcribes).
- Lane C (consensus): non-safety rows (~100-200). Existing frozen
  consensus method, documented per row; known to be LLM-lineage and
  labeled as such in all downstream reports.
- Gold freeze: dataset + gold frozen with manifest SHA before Tier 1
  execution begins. Post-freeze gold edits require a pre-registered
  adjudication flow (section 5) and are logged in a gold-change record.

## 5. Pre-registered disagreement/adjudication flow

If a row's tier outcomes make a Lane C gold look suspect (e.g. all
tiers "fail" and the row would become >T3 on consensus gold alone):
- Do NOT relabel opportunistically.
- The row is escalated to a single human adjudication pass (bounded:
  one pass, decision + evidence span + rationale).
- If human confirms gold: row stands (possibly >T3).
- If human overturns gold: old gold is marked superseded in a
  gold-change record, new gold committed, tier outcomes re-derived
  against new gold. Overturn count is reported; >10% overturn rate on
  any family triggers a dataset-quality failure status.

## 6. Execution ladder (per row)

For each row, run in fixed order, stop at first definitively
SUFFICIENT tier:

    T1 (each of 3 models) -> SUFFICIENT if any T1 model correct?
      no -> T2 (each of 2 models) -> SUFFICIENT if any T2 model correct?
        no -> T3 (each of 2 models) -> SUFFICIENT if any T3 model correct?
          no -> label >T3 (FRONTIER_REQUIRED_OR_UNRESOLVED_CANDIDATE) — NO Astra call

- "Correct" = frozen per-lane equivalence rule (exact semantic verdict
  + required evidence properties inherited from routing-v1 Stage 0
  cell-state rule). The rule is frozen in the dataset manifest before
  the first call.
- Per-row output: {case_id, family, safety_critical, gold_sha,
  per-model raw+verdict, minimum_tier, ladder_trace}.
- If a tier model call fails on transport: one bounded retry per the
  frozen retry policy; persistent transport failure marks the row
  TRANSPORT_BLOCKED for that tier and it is reported, not silently
  skipped.

## 7. Pre-registered gates and outputs

Primary deliverable: fresh minimum-tier label set
  reviewer-minimum-tier-fresh-v1.jsonl with per-row ladder trace.

Pre-registered summary stats (descriptive, no gate on tier mix):
- exact tier distribution (T1/T2/T3/ >T3), by lane and family.
- >T3 count and rows list (this is the falsification test for the
  section-0 hypothesis).
- Lane H safety-critical subset: N, T1/T2/T3/>T3 split, and the
  rule-of-three style upper bound on the P(any-tier-wrong) implied by
  observed failures.
- Transport failure count and rows.

Pre-registered statuses (exactly one):
- FRESH_BATCH_COMPLETE_HYPOTHESIS_FALSIFIED — at least one genuine
  >T3 row (post-adjudication flow, human-confirmed where applicable).
- FRESH_BATCH_COMPLETE_HYPOTHESIS_SURVIVES — zero >T3 rows across the
  full batch.
- FRESH_BATCH_DATASET_QUALITY_FAILED — gold overturn rate >10% in any
  family, or construction overlap gate fails, or gold freeze was
  violated.
- FRESH_BATCH_TRANSPORT_BLOCKED — transport failures prevent a
  complete ladder read for >5% of rows after bounded retries.

Explicit non-claims (standing):
- A T4-free batch cannot prove T4 is unnecessary in general; it tests
  the pre-registered hypothesis on THIS corpus only.
- Zero >T3 rows is evidence about this batch, not a proof of universal
  T1-T3 sufficiency (coverage is finite).
- Lane C gold remains LLM-consensus lineage, not human ground truth.
- Single-run tier labels; no stability claim.
- No router (Jev or otherwise) is trained, tuned, or evaluated here.

## 8. Deferred to later tasks (explicitly out of scope)

- Jev router training/evaluation on the new label set (requires the
  richer T1/T2/T3/ >T3 distribution this batch produces).
- Any Astra qualification or frontier-tier measurement.
- Any product runtime or cascade integration.
- Any new blind-set or certification activity.

## 9. Deliverables (on execution, after authorization)

    evaluation/reviewer-minimum-tier-fresh-batch-v1/
      TASK-LOCK.json
      construction-builder.py
      dataset-frozen.jsonl            (rows, no gold)
      gold-frozen.jsonl               (gold, lane-tagged, committed pre-call)
      dataset-manifest.json           (SHAs, family counts, equivalence rule)
      ladder-runs-*.jsonl             (per-tier raw + parsed verdicts)
      minimum-tier-labels-v1.jsonl    (ladder traces, final labels)
      adjudication-record.json        (section-5 flows, gold changes)
      summary.json
      final-report.md

## 10. Stop condition

On terminal status: STOP. No router work, no Astra, no fresh holdout,
no runtime change, no follow-on task without new explicit owner
authorization.
