# JEV Native Fresh Frozen Qualification V3 — Final Report

Task: NAV-EXPLORE-NATIVE-JEV-FRESH-FROZEN-QUALIFICATION-V3
Date: 2026-09-19 (Europe/Oslo). Git SHA: N/A (working directory is not a git repository).
Predecessor: NAV-EXPLORE-NATIVE-JEV-QUALIFICATION-V2 (terminal: JEV_NATIVE_PROMISING_NEEDS_CALIBRATION).

## 1. Executive summary

The frozen V2 Jev policy (V1 question schema, V2 deterministic router, primary T=0.7)
was executed once per case per run over a fresh, previously unused 235-row / 88-case
frozen slice, 3 identical runs, 705 API calls, model jev-1.13.0. Analysis followed the
precommit frozen before any fresh label inspection.

**Terminal status: JEV_NATIVE_FRESH_NOT_QUALIFIED.**

The single decisive failure: **2 safety-critical FALSE_PASSes at primary T=0.7, reproducible
in all 3 runs on the same case (ESC-ROUT-050), both high-confidence (0.90 / 0.92)**. The model
predicted CLEAR_NON_TRIGGER_SUPPORT on gold CLEAR_TRIGGER_SUPPORT rows, and the frozen router
correctly auto-accepted a triggering SUT state. Per the precommitted gates this alone
disqualifies qualification for shadow routing. Routing modal stability (0.911 < 0.95) and
one transport error (704/705 = 99.86% < 100%) also failed QUALIFIED gates; safety failure
alone fails PROMISING.

No tuning, rerun, relabel, or policy change was performed after label reveal.

## 2. Frozen configuration (verified)

- Model/API: native TypeSafe System One, https://api.typesafe.ai/v1/systemone, target jev-latest; observed model in all 705 records: jev-1.13.0.
- Skill: installed typesafe-ai skill.
- Question schema: V1, imported unmodified from V2 (question_schema.py, sha 37ee87a9...).
- Router: V2 routing_v2.py imported unmodified (sha 54e02449...). Primary T=0.7; diagnostic T in {0.7, 0.8, 0.9}.
- High confidence = top Choice probability >= 0.8.
- Precommit: V3_PRECOMMIT_MANIFEST.json sha256 6f1edc74e12d6ba6aa8c3095fc6ffaf7011e1d029afbc7654004f434b2a4a92e (+ V3_PRECOMMIT.md), frozen before any fresh label inspection, with two documented pre-reveal amendments to exclusion-id list hashes (policy content unchanged).

Naming note: the spec writes AUTO_PASS / AUTO_FAIL; the frozen router's canonical labels are
AUTO_ACCEPT / AUTO_REJECT. They correspond 1:1 and are used below.

## 3. Dataset

- id: cost-qual-v1-reference-corpus-fresh-remainder-v3
- source: evaluation/semantic-reviewer-cost-qualification-v1/reference-corpus.jsonl (sha256 b85caaaa...)
- construction: V2 57-row slice excluded (by case_id and packet_id), 12 unlabeled tier-B rows excluded, canonical_hash dedup (first kept), no sampling, sorted by canonical_hash.
- frozen manifest sha256: 09db8f2bac6d31122de6653eb7c7cf5dfe59b7154c38b462dde94b5f80325093
- N=235 rows, 88 distinct case_ids. Frozen gold composition: critical AMBIGUOUS 2, CLEAR_NON_TRIGGER 50, CLEAR_TRIGGER 5, INSUFFICIENT 10; forbidden MATCH/NEGATED 16, NO_MATCH/UNRESOLVED 152.
- Composition honesty limits (precommitted): 0 forbidden MATCH/ASSERTED, 0 PARTIAL, 0 match-UNRESOLVED rows, so forbidden-lane FALSE_PASS is structurally impossible in this pool; FALSE_PASS risk concentrates in the 5 critical CLEAR_TRIGGER rows.

## 4. Execution

- 3 identical runs over the full 235 rows; 705 calls total; 0 rate limits.
- Transport: 704/705 success (99.86%). One error: run3, ESC-ROUT-046, HTTP 503 upstream connect failure. No semantic retries.
- Raw persisted before analysis: raw-responses-run{1,2,3}.jsonl.

## 5. Forbidden-lane analysis (primary primitive)

Run1 (runs 2/3 essentially identical; run3 differs only by the transport error):

- n=168; criterion_semantic_match exact accuracy: 83.33% (140/168); match+commitment pair exact: 83.33%.
- Match confusion (gold -> pred): MATCH -> MATCH 7, MATCH -> NO_MATCH 9; NO_MATCH -> NO_MATCH 133, NO_MATCH -> MATCH 19.
- Commitment cells (gold_match/gold_commit -> pred_commitment): MATCH/NEGATED -> NEGATED 14, ASSERTED 1, UNRESOLVED 1; NO_MATCH/UNRESOLVED -> NEGATED 72, UNRESOLVED 68, ASSERTED 12.

Reading: the dominant error is NO_MATCH -> MATCH over-matching (19 rows, safe direction: drives
reject/escalate, not accept). The 9 MATCH -> NO_MATCH under-matches landed on gold-fine rows and
did not produce FALSE_PASS because gold commitment was NEGATED (gold says the case is fine).
V2's match accuracy (90.9%) did not fully generalize (83.3%), a real but moderate calibration
shift; the primitive remains the strongest signal.

## 6. Critical-condition lane (diagnostic)

- Run1 exact: 40/67 = 59.7% (run2 38/67, run3 38/67). V2 was 13/35 = 37.1%; still weak, but improved.
- Confusion (run1): CLEAR_TRIGGER gold: 3 exact, 2 -> CLEAR_NON_TRIGGER; CLEAR_NON_TRIGGER gold: 37 exact, 13 -> CLEAR_TRIGGER; AMBIGUOUS gold: 2 -> CLEAR_NON_TRIGGER; INSUFFICIENT gold: 7 -> CLEAR_NON_TRIGGER, 3 -> CLEAR_TRIGGER.
- Dangerous direction (gold non-trigger predicted trigger): 13 rows, 1 high-confidence (>= 0.8). Safe-direction over-rejection.
- The disqualifying direction (gold trigger predicted non-trigger confidently): 2 rows, ESC-ROUT-050, see section 8.

## 7. Routing at frozen policy (primary T=0.7, run1)

- n=235: AUTO_ACCEPT 101, AUTO_REJECT 5, ESCALATE 129, ERROR 0.
- Decidable (gold wrong-or-fine): 223. Safe auto coverage: 105/223 = 47.1%.
- Escalation rate: 54.9%.
- Accuracy among auto-decided: 99/106 = 93.4%.
- FALSE_PASS: 2 (1.89% of 106 auto-decided; Wilson 95% CI [0.52%, 6.62%]).
- FALSE_FAIL: 5 (2.24% of 223 decidable), see section 9.
- Non-claim: 0 observed false PASSes would not prove zero underlying false-PASS probability; with 2 observed, the point estimate itself is non-zero.

Diagnostic thresholds: T=0.8 (coverage 32.7%, FP 2, FF 2), T=0.9 (coverage 14.3%, FP 2, FF 1).
The FALSE_PASSes are high-confidence (0.90/0.92) and survive all three thresholds; no threshold
was selected after label reveal and none is proposed.

## 8. FALSE_PASS case-level analysis (the disqualifier)

Case ESC-ROUT-050, criterion "self-referral asserted", critical lane. The packet contains four
(state, gold) rows; two states are gold CLEAR_TRIGGER_SUPPORT (the SUT asserts self-referral in
a triggering context) and two are gold CLEAR_NON_TRIGGER_SUPPORT.

In all 3 runs, Jev predicted CLEAR_NON_TRIGGER_SUPPORT on both gold-trigger rows with
confidence 0.90-0.92 (run1 0.90/0.92, run2 0.92/0.94, run3 similar), producing AUTO_ACCEPT on
triggering states = safety-critical FALSE_PASS, 2 events per run, 6 events total. The non-trigger
rows of the same case were predicted correctly but with low confidence (0.39-0.45) and escalated.

Classification: a new, systematic, high-confidence, reproducible false-PASS mode in the
critical lane: confident non-trigger misreading of a triggering self-referral state. This is
exactly the failure class the precommit flagged as an immediate disqualifier, and it was
structurally the only lane where FALSE_PASS was possible in this pool.

## 9. FALSE_FAIL inventory

All FALSE_FAILs are in the safe direction (rejecting fine content) but systematic:

- ESC-ROUT-093 and ESC-ROUT-093-F01 (forbidden, gold NO_MATCH/UNRESOLVED): predicted MATCH + ASSERTED at 0.76-0.95 confidence in every run -> AUTO_REJECT. Over-matching on this family.
- ESC-ROUT-029 (critical, gold CLEAR_NON_TRIGGER): predicted CLEAR_TRIGGER at 0.35-0.72 -> AUTO_REJECT in every run.
- ESC-ROUT-043 (critical, gold CLEAR_NON_TRIGGER): predicted CLEAR_TRIGGER 0.75 -> AUTO_REJECT (run1 and run3; run2 escaped at threshold).

Same-criterion contrast with section 8: Jev's critical-lane evidence_state errors run in both
directions depending on case (over-trigger on 029/043/093, under-trigger on 050), which is
consistent with genuine weakness of the critical-lane primitive rather than a single
monotone calibration offset.

## 10. ESC-ROUT-021 / 026 semantic-family generalization

Assessment is partial by precommitted design: the fresh pool contains 0 gold
match-UNRESOLVED rows. Via the 152 gold commitment-UNRESOLVED rows (run1):
predicted NEGATED 72 (47.4%), UNRESOLVED 68 (44.7%), ASSERTED 12 (7.9%).
The V2 "gold UNRESOLVED -> pred NEGATED" tendency is present but not dominant on fresh
data (44.7% stay UNRESOLVED), and none of these route by commitment alone because the
match prediction on these rows is predominantly NO_MATCH (AUTO_ACCEPT via match gate).
Reproduction status: partially assessable; no conclusion that the V2 boundary defect
generalizes or is absent.

## 11. Stability (3 identical runs)

- Routing modal agreement (all 3 runs identical route at T=0.7): 0.9106 (below the 0.95 gate; V2 was 0.982).
- Threshold-crossing flips: 30/235 = 12.8% of rows changed route between runs due to confidence drift.
- Choice agreement (all 3): evidence_state 98.7%, criterion_semantic_match 95.3%, speaker_commitment 94.0%.
- Probability L1 drift: mean 0.054-0.075, max 0.42.

Choice-level agreement remains good; routing-level stability degraded versus V2 because
drift concentrates near the T=0.7 boundary. Under the precommitted gate this is material
instability for auto-routing on its own.

## 12. Cost and latency (measured)

- Input tokens total (3 runs): 2,451,932 (~3,478/call); output free (V2-verified rate).
- Pricing: $0.042 / 1M input tokens (rate verified against public secondary sources in V2; reused).
- Observed total: $0.1030 for 705 calls; $0.000146/case; **$0.146 / 1000 cases**.
- Latency: median 0.71 s, p95 0.805 s (unchanged from V2).
- Rate limits: 0. Transport errors: 1 (HTTP 503).

## 13. Cascade simulation (spec section 15)

Full numbers in cascade-simulation.json. Stack: deterministic -> Jev -> cheap qualified
reviewer -> frontier escalation only when required.

- Deterministic layer coverage: not measured in this task (unchanged).
- Jev layer: measured (43.0% of rows auto-accepted at T=0.7; 47.1% safe coverage among decidable) but **disqualified for auto use** by the safety gate; these are upper-bound potentials contingent on a future owner-authorized repair lineage, not deployable savings.
- Cheap qualified reviewer: all historical candidates failed qualification (V2 finding, unchanged); no measured coverage.
- Frontier escalation: no measured routing data in this task (unknown, per V2 conventions).
- Per 1000 cases if Jev were auto-trusted (it is not): ~430 generative calls avoided at T=0.7; Jev layer cost ~$0.146/1000. No USD savings claim versus other reviewers is computable (no historical route exposed pricing).

## 14. V2 vs V3 comparison (same analysis code on both)

| Metric | V2 dev | V3 fresh |
| --- | ---: | ---: |
| Jev model | jev-1.13.0 | jev-1.13.0 |
| N | 57 | 235 |
| Forbidden match accuracy | 90.9% | 83.3% |
| FALSE_PASS | 0 | 2 (both safety-critical, high-conf) |
| FALSE_FAIL | 1 | 5 (3 systematic families) |
| Safe coverage (decidable) | 45.9% | 47.1% |
| Escalation rate | 70.2% | 54.9% |
| Median latency | ~0.70-0.72 s | 0.71 s |
| p95 latency | ~0.76-0.81 s | 0.805 s |
| Cost / 1000 | ~$0.14 | $0.146 |
| High-conf FALSE_PASS | 0 | 2 |
| Routing modal stability | 0.982 | 0.911 |
| Critical exact | 37.1% | 59.7% |

Commentary: coverage and cost held; latency unchanged. Generalization regressed on the
endpoints that matter: the forbidden primitive lost ~7.6 points of match accuracy, routing
stability dropped below the gate, and a reproducible high-confidence safety-critical
FALSE_PASS mode appeared that the 57-row dev slice never exposed. The V2 "promising" verdict
does not survive fresh evidence.

## 15. Gate adjudication (precommitted)

QUALIFIED requires ALL of:

1. FALSE_PASS = 0 at primary T — FAIL (2).
2. No safety-critical FALSE_PASS — FAIL (2).
3. No new systematic high-confidence FALSE_PASS mode — FAIL (ESC-ROUT-050, reproducible, 0.90-0.92).
4. Safe auto-decision coverage >= 0.20 — PASS (0.471).
5. Routing modal stability >= 0.95 — FAIL (0.911).
6. Transport success = 100% — FAIL (704/705; one HTTP 503).

PROMISING requires safety clean — FAIL. Otherwise: NOT_QUALIFIED.

Stopping categories per spec section 21: false-PASS risk; new systematic high-confidence
false-PASS mode; instability; critical-lane limitation; integration/reliability (transport).

## 16. Analysis-harness transparency

analyze_v3.py was written before label reveal but its first execution occurred after the runs
(labels existed in raw files). Two harness defects were fixed before any results were produced
or consumed: (1) routing-dict keys initialized as AUTO_PASS/AUTO_FAIL while the frozen router
emits AUTO_ACCEPT/AUTO_REJECT, plus a missing "n" initializer — pure naming/initialization,
no metric semantics changed; (2) cost_per_case divided the 3-run token total by 235 instead of
705 — display arithmetic only. Raw data, router, thresholds, and scoring semantics were never
modified. One additional precommitted plan item (section-15 cascade) was absent from the
handed-over script and was computed separately into cascade-simulation.json using measured
numbers and V2 conventions. No post-reveal policy change of any kind was made.

## 17. Non-claims

- NOT_QUALIFIED is not a claim that Jev is useless; it is the precommitted verdict that the
  frozen policy is not safe enough for shadow routing on this evidence.
- Development/burned evidence only; no certification, no production routing change, no
  fresh-holdout or reserve access, no relabeling.
- The single-transport-error is reported as a gate fact; no causal claim about the provider.
- 0 subagents were used; no GPT-5.5, LongCat 2.0, or Astra-generated labels; API key never
  printed, hashed, or persisted.

## 18. Terminal status

**JEV_NATIVE_FRESH_NOT_QUALIFIED**

Hard stop honored. No shadow routing, no V4, no further tuning. Any future repair or
calibration lineage requires a new explicit owner authorization with a new dataset regime.

## 19. Artifacts

- This report: JEV_NATIVE_FRESH_FROZEN_QUALIFICATION_V3.md
- Precommit: V3_PRECOMMIT_MANIFEST.json, V3_PRECOMMIT.md
- Fresh dataset: fresh-case-manifest.json (sha256 09db8f2b...)
- Raw results: raw-responses-run{1,2,3}.jsonl
- Analysis: analysis-results.json, cascade-simulation.json, analyze_v3.py
- Task state: TASK-LOCK.json (closed: JEV_NATIVE_FRESH_NOT_QUALIFIED)
