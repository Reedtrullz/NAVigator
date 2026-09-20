# NAV-EXPLORE-REVIEWER-MINIMUM-TIER-FRESH-BATCH-V1 — TASK SPEC V1.1 (PREPARATION)

Status: PREPARATION_AUTHORIZED. This revision is authorized by owner
authorization "FRESH BATCH PREPARATION ONLY" (2026-09-19). It freezes
the PREPARATION stage only: source selection, deterministic fixture
construction, overlap/lineage control, blind human-adjudication
package, and offline call/cost planning. NO model call of any kind is
authorized in this stage. Execution stages (human gold, consensus
gold, tier evaluation) require separate owner authorization.

## 0.1 Original draft provenance

- Original file: evaluation/minimum-sufficient-reviewer-routing-v1/fresh-batch-spec-draft.md
- Original SHA256: 96cbf4fe980941405c450f449d8984dccaaaa9b59e0a7cb8215e941d5d28cd2f
- Verified byte-identical against this SHA before any work in this task.
- The original draft remains UNCHANGED and is referenced, not superseded
  in place. This V1.1 spec is the authoritative specification; where the
  two differ, this spec governs.

## 0.2 Authorization scope limitation

Owner authorization covers EXACTLY:
1. verification of the original draft,
2. this revised spec,
3. selection and freezing of existing local knowledge sources,
4. deterministic construction of new reviewer fixtures (no LLM in the
   construction loop),
5. overlap/lineage control against the entire known historical fixture pool,
6. a blind human-adjudication package (no gold fabrication),
7. an offline call/cost plan for a future authorized run.

The authorization does NOT cover:
- Jev calls, consensus-gold calls, T1/T2/T3 calls, SUT runs,
  Astra/Sol calls, subagents, or any model call (all = 0 in this stage);
- runtime, reviewer, or routing changes in the NAV Explore product;
- creation of gold-frozen.jsonl or any completed-gold artifact;
- a new holdout claim on data that later feeds router development.

## 0.3 Change log vs original draft (owner revisions)

| # | Original draft | V1.1 revision (owner-mandated) |
|---|---|---|
| R1 | implicit minimum-tier semantics | Section 2.1: minimum_observed_success_tier defined explicitly as a pass-assisted capacity measurement, not a qualified runtime router; per-model identity retained; no assumption of tier dominance. |
| R2 | ">T3" label | Section 2.2: ">T3" becomes compatibility alias for NO_TESTED_T1_T3_SUCCESS with explicitly bounded meaning; never evidence that Astra is necessary, would succeed, or that other models would fail. ASTRA_CALLS = 0 absolute, no diagnostic exception. |
| R3 | draft listed 8 families incl. MATCH/ASSERTED ~50 | Section 3: families are PROPERTIES, not gold labels. One primary family per row; additional properties as tags. MATCH/ASSERTED and CLEAR_TRIGGER_SUPPORT are never pre-filled as expected gold. Family targets: 350 rows total: 50 assertion/mention/attribute, 150 safety-critical rule/trigger boundary, 30 actor/referral distinctions, 30 negation/polarity, 20 insufficient/ambiguous context, 30 exceptions/conditions, 20 compound conditions, 20 simple controls. |
| R4 | gold authority lanes | Section 4: Lane H human gold = Reidar or an explicitly designated human ONLY. Codex and other AI models are never human adjudicators. Lane C consensus gold is documented and costed now but NOT called in this stage; consensus model identity and overlap with tier models documented. |
| R5 | freeze order ambiguous | Section 5: fixed order (1) builder+sources+reviewer-inputs freeze, (2) human gold + separately authorized consensus gold, (3) complete gold freeze, (4) separately authorized tier evaluation. |
| R6 | adjudication flow only on suspect rows | Section 5: pre-registered blind control sample of other Lane C rows selected BEFORE tier results; overturn rate = overturns / actually human-adjudicated rows, with control sample and targeted escalations reported separately. |
| R7 | >5 percent transport tolerance could mask unresolved | Section 6: NOT_RUN, transport failure, and missing gold are never semantic FAILED. Unresolved cheaper tier yields MINIMUM_UNKNOWN; NO_TESTED_T1_T3_SUCCESS requires all relevant configurations to have definitive failing outcomes; HYPOTHESIS_SURVIVES requires documented coverage of the full evaluable batch; statuses split task completion, hypothesis outcome, and minimum-tier label completeness; explicit unresolved/blocked status added (4+1 statuses). |
| R8 | statistical claim P(any-tier-wrong) | Section 7: replaced with the actual observed event (no tested T1-T3 configuration succeeds); rule-of-three style bound labeled one-sided 95 percent upper bound on THAT event with independence assumptions stated; rows and scenario groups reported separately; no production-risk or production-cost inference from this targeted challenge set. |
| R9 | no cost plan | Section 8: offline preflight plan required: exact provider/model/config identities, call order, max primary calls (2450 at 350 rows x 7 configurations, planning cap only), retry caps, separate consensus-gold calls, token limits, cost basis, unknown costs, quota stops, persistent result register, content-hash resume. |
| R10 | fixtures described loosely | Section 3: construction from existing frozen KB + reviewer contract only; new deterministic scenarios; no new municipalities/rules; no SUT-generated answers; no LLM fixture generation; no cosmetic rewrites of old benchmark rows; old case IDs and memorized benchmark wording forbidden in new fixtures; no real person/patient data. |
| R11 | single rows | Section 3.3: scenario_group_id per base scenario; report row counts AND scenario-group counts. |
| R12 | overlap check target 0 on burned pool | Section 4: overlap check against ENTIRE known historical fixture pool (burned 375 rows plus other available historical fixtures), including exact input overlap, normalized text overlap, trivial name/number swaps, and near-duplicates with same decision structure. New IDs are not new instances. |

## 1. Scope and lineage

- Task ID: NAV-EXPLORE-REVIEWER-MINIMUM-TIER-FRESH-BATCH-V1
- Task directory: evaluation/reviewer-minimum-tier-fresh-batch-v1/
- Predecessor (immutable, CLOSED): NAV-EXPLORE-MINIMUM-SUFFICIENT-REVIEWER-ROUTING-V1, terminal ROUTER_V1_INSUFFICIENT_REVIEWER_EVIDENCE, label set SHA 4cd87708c79c44ce8a424b1feee491727096dbfd4edc55e0985a3a26fc64902e.
- Reviewer contract: semantic-judge-contract-v1-4, frozen in
  evaluation/semantic-reviewer-cost-qualification-v1/qualification-contract.json
  (critical_condition + forbidden_claim semantics, enum domains,
  evidence rule, schemas, system_prompt).
- Tiers inherit frozen definitions (routing-v1):
  T1_BASIC = mimo-v2.5-pro, laguna-s-2.1, ling-3.0-flash-sante;
  T2_INTERMEDIATE = bai-deepseek, nex-n2.5-pro; T3_STRONG = luna-high,
  luna-max; T4 = Astra (reserved, never called).
- Ladder rule inherits frozen definition: cheapest tier SUFFICIENT with
  all cheaper tiers definitively FAILED (see 2.1 for semantics).
- This batch produces EVIDENCE (fresh rows + gold + empirical minimum
  tier labels). It does NOT train, tune, or evaluate any router. Jev/
  router work is explicitly deferred to a later task.

## 2. Hard invariants

- ASTRA_CALLS = 0, absolute, including confirmation or diagnostic calls.
- NO GPT-5.5, no LongCat, no unapproved model escalation.
- In the PREPARATION stage: ALL model calls = 0.
- Frozen gold per row is committed BEFORE any tier model sees the row.
- No gold change after tier evaluation starts, except the pre-registered
  adjudication flow (Section 5).
- No runtime/cascade/reviewer changes in the NAV Explore product.
- Every persisted tier verdict includes raw response + parsed verdict + SHA,
  one run per model per row (single-run labels; stability is out of scope).
- Construction is deterministic and scripted with a fixed seed; no LLM
  participates in fixture generation.

## 2.1 Minimum tier: explicit measurement semantics

minimum_observed_success_tier =
the lowest tier with at least one observed sufficient model outcome,
where all cheaper tiers have DEFINITIVELY FAILED under the frozen cell
rule (a cell is CORRECT only if ALL valid runs of that tier on the row
match frozen gold; NOT_RUN is not an error; transport failure and
missing gold are not failures).

Explicit limits:
- This is a PASS-ASSISTED capacity measurement. It is NOT a qualified
  runtime router. Knowing afterward that one of three models was correct
  is not the same as production knowing which one.
- A tier with three models is not one reviewer. Per-model identity of
  all observed correct and incorrect outcomes is retained.
- No assumption that higher tiers dominate lower tiers on any row.
- No realized Astra-savings number is computed from a policy that uses
  gold to pick the winning model; such a number would be pass-assisted
  and is reported only as a labeled upper-bound estimate, if at all.

## 2.2 NO_TESTED_T1_T3_SUCCESS (">T3" alias)

Testable hypothesis (pre-registered): for every evaluable row in this
batch, at least one of the specified T1-T3 configurations delivers a
sufficient outcome under the frozen single-run protocol.

If all relevant configurations for a row DEFINITIVELY fail against
adjudicated gold, register NO_TESTED_T1_T3_SUCCESS. The string ">T3"
may be kept as a compatibility alias but carries exactly this bounded
meaning. This outcome is NOT evidence that:
- Astra is necessary;
- Astra would succeed;
- all other cheap models would fail;
- capacity is stable across repeated runs.

## 3. Dataset construction

Target: 350 rows (draft family target kept; if source quality cannot
honestly support a family target, report the shortfall and stop rather
than fill with trivial duplicates).

- Source material: existing frozen KB (root *.md files, e.g. 25, 26,
  28b, 28c, 31, 45 and related) + the frozen v1-4 reviewer contract
  definitions. No new municipalities, services, or rules are researched.
- Candidate text per fixture is a deterministic synthetic SUT-output
  analog constructed from frozen KB statements, controlled for the
  property under test. SUT is never called.
- No LLM fixture generation. No real person/patient data. No cosmetic
  rewrites of old benchmark rows. Old case IDs and memorized benchmark
  wording are not used as new test content.
- No gold is created in this stage. Nothing in a fixture encodes an
  expected verdict.

### 3.1 Families as properties (not gold labels)

Each row has ONE primary family; additional properties are tags.
"MATCH/ASSERTED" and "CLEAR_TRIGGER_SUPPORT" are never pre-filled as
expected gold by virtue of family membership. Safety-critical status
follows the existing contract and harm potential, not later model
errors.

| Primary family | Target rows | Property tested |
|---|---|---|
| assertion_mention_attribution | 50 | claim vs mention/quotation/hedging/attribution |
| safety_critical_rule_trigger_boundary | 150 | safety rule/trigger boundaries (65-day/10-day rules, suicide/acute, crisis routing, deontic qualifiers) |
| actor_referral_distinction | 30 | who refers whom, routed vs performed, referral rights |
| negation_polarity | 30 | support phrase + negation, not-required, exception of obligation |
| insufficient_ambiguous_context | 20 | context genuinely insufficient or intentionally ambiguous |
| exception_condition_clauses | 30 | bare-dersom, only-if, per-atom qualifiers |
| compound_conditions | 20 | conjunction, per-atom gating, multi-condition |
| simple_control | 20 | semantically easy anchor rows |

Total = 350. Safety-critical rows target ~150; simple controls ~20.

### 3.2 Row fields

Every row carries at minimum:
- row_id (fresh namespace: FB1-<group>-<nn>; no historical IDs),
- scenario_group_id,
- primary semantic family + property tags,
- safety_critical,
- source_id + source_hash (KB file + its SHA256),
- derivation/template_id,
- reviewer-input fields only: contract_version, dimension, case_context,
  criterion, candidate_text (sut_output slot), reviewer_instructions.

Canonical packet hash (inherited): sha256 of
JSON {contract_version, dimension, case_context, criterion, sut_output},
sort_keys=True, ensure_ascii=False.

### 3.3 Scenario grouping

scenario_group_id identifies variations of the same base scenario
(same KB scenario, different linguistic/semantic manipulation).
Reports give BOTH row counts and scenario-group counts, so that N
near-variant rows are never mistaken for N independent scenarios.

## 4. Freshness and overlap control

Overlap check against the ENTIRE known historical fixture pool:
- the 375-row burned pool (evaluation/minimum-sufficient-reviewer-routing-v1/minimum-sufficient-reviewer-burned.jsonl, V2 140 + V3 235, 0 internal overlap),
- other available historical fixture files under evaluation/ (V1-V1.4 official sets and related judge-validation fixtures where present in JSON/JSONL form).

Checks:
1. exact input overlap (canonical hash or exact field equality),
2. normalized text overlap (case/whitespace/ASCII-folding normalization; Norwegian/English token sequences),
3. trivial name/number swaps (normalized comparison with municipality/name/number masks),
4. near-duplicates with same decision structure (shared decision-bearing key phrases + same gold-relevant polarity/modality structure).

Gate: no exact/normalized duplicate; trivial-swap or near-duplicate hits require builder revision before freeze. Verdict: recorded in overlap-lineage-report.md. New row IDs are not evidence of new instances.

## 4.1 Source manifest

Every KB source used by the builder is frozen in source-manifest.json:
path, SHA256, and the statement ranges used. Reviewer-contract source:
qualification-contract.json + its SHA256.

## 5. Gold authority and adjudication (future stages, frozen now)

Freeze order for later authorized stages:
1. builder + sources + reviewer-inputs freeze (this preparation);
2. human gold AND separately authorized consensus gold;
3. complete gold freeze + assessment rules;
4. separately authorized tier evaluation.

- Lane H (human): ALL safety-critical rows plus any additional rows
  designated at gold time. Adjudicated by Reidar or an explicitly
  designated human. Codex and other AI models are never human
  adjudicators. Blind adjudication package: neutral row ID, criterion,
  required source/reference text, candidate text, allowed verdict
  options + definitions, empty verdict/evidence/rationale fields, and
  the right to mark a row unclear/insufficiently documented. No
  recommended verdict, no model info, no expected tier, no forced gold.
  The agent may later transcribe explicitly received human decisions
  but never fills gaps itself.
- Lane C (consensus): documented and costed in the offline plan but
  NOT called in this stage. The consensus model identity and any
  overlap with tier models are documented; no claim of independent
  ground truth where it does not exist.
- No gold-frozen.jsonl is created in this stage.

### 5.1 Pre-registered adjudication flow for suspect Lane C rows

If tier outcomes make a Lane C gold look suspect:
- no opportunistic relabeling;
- the human never sees tier/model outcomes for the row and is not told
  the row was selected because models failed;
- original gold version remains unchanged; a separate adjudicated
  version is created; both original and revised scoring are retained;
- no new model calls as a consequence of new gold unless a later call
  authorization covers it.
- Pre-registered blind control sample: a small random sample of other
  Lane C rows, selected and frozen BEFORE tier results exist.
- Overturn rate = overturns / actually-human-adjudicated rows, reported
  separately for (a) targeted escalated rows and (b) the control
  sample. Unexamined rows never dilute the denominator.

## 6. Transport, UNKNOWN, and terminal interpretation

- NOT_RUN, transport failure, and missing gold are NEVER semantic FAILED.
- One bounded transport retry per frozen retry policy; persistent
  transport failure marks the row-tier TRANSPORT_BLOCKED and is reported.
- If a cheaper tier is unresolved (transport/gold/other evidence gap),
  a later correct model does NOT yield an exact minimum tier; the row
  keeps MINIMUM_UNKNOWN (or the corresponding evidence-gap label).
- NO_TESTED_T1_T3_SUCCESS requires every relevant configuration to
  have a definitive failing outcome against frozen gold.
- HYPOTHESIS_SURVIVES requires documented coverage of the full
  evaluable batch, not merely absence of recorded counterexamples.
- Unresolved evidence must not hide inside a transport tolerance.

### 6.1 Statuses (exactly one task status; hypothesis and label completeness reported alongside)

Task completion statuses:
- PREPARATION_COMPLETE_AWAITING_HUMAN_GOLD_AND_RUN_AUTHORIZATION (this stage)
- FRESH_BATCH_COMPLETE_HYPOTHESIS_FALSIFIED
- FRESH_BATCH_COMPLETE_HYPOTHESIS_SURVIVES
- FRESH_BATCH_DATASET_QUALITY_FAILED
- FRESH_BATCH_TRANSPORT_BLOCKED
- (4+1 rule) FRESH_BATCH_INCOMPLETE_UNRESOLVED_EVIDENCE: batch finished
  mechanically but minimum-tier labels are incomplete due to evidence
  gaps (transport, missing gold, unresolved adjudication).

Reported alongside the task status:
- hypothesis outcome: HYPOTHESIS_SURVIVES / HYPOTHESIS_FALSIFIED /
  HYPOTHESIS_UNEVALUABLE (insufficient complete rows),
- minimum-tier label completeness: complete / partial with counts.

## 7. Statistical reporting rules (non-claims)

- Replace P(any-tier-wrong) with the actual observed event: no tested
  T1-T3 configuration succeeds.
- Safety results: report rows AND scenario groups separately with the
  correct denominator for each.
- Any binomial upper bound must be labeled: one-sided/two-sided level,
  the exact event it bounds, and independence/selection assumptions.
- Near-variant rows are not presented as equivalent to many independent
  safety observations; scenario-group counts are always shown alongside.
- No production-risk or production-cost conclusion is drawn from this
  targeted, stratified challenge set.

## 8. Offline call/cost plan (planning only, zero calls in this stage)

Routes are only the verified predecessor-spec routes; no new candidates.
The plan (call-cost-plan.json + human-readable section in
final-report.md) must show:
- exact provider/model/config identities per tier,
- call order (ladder), stop-at-first-sufficient tier rule,
- max primary tier calls: 350 rows x 7 configurations = 2450
  (theoretical planning cap; NOT an authorization to spend it; ladder
  stopping and Lane H/C gates will reduce actual usage),
- retry caps per frozen retry policy (1 technical retry, no semantic retry),
- separate consensus-gold calls for Lane C (model identity, per-row call count),
- token/output limits per call,
- cost estimate + pricing basis, unknown costs explicitly marked,
- planned stops at quota/budget limits,
- persistent result register with content-hash-based resume so a restart
  never repeats completed calls.

Model calls in THIS preparation stage: exactly 0.

## 9. Deliverables (preparation stage)

    evaluation/reviewer-minimum-tier-fresh-batch-v1/
      TASK-SPEC-V1.1.md            (this file)
      TASK-LOCK.json
      source-manifest.json
      construction-builder.py      (versioned, fixed seed, deterministic)
      dataset-frozen.jsonl         (rows, NO gold)
      dataset-manifest.json        (SHAs, counts, hashes)
      overlap-lineage-report.md    (+ machine-checkable summary)
      scenario-group-manifest.json
      human-review-workbook.md     (blind adjudication package)
      call-cost-plan.json
      final-report.md

Execution-stage artifacts (later authorization): ladder-runs-*.jsonl,
minimum-tier-labels-v1.jsonl, adjudication-record.json,
gold-change-record.json, summary.json.

## 10. Stop condition

At PREPARATION_COMPLETE_AWAITING_HUMAN_GOLD_AND_RUN_AUTHORIZATION:
STOP. No consensus gold, no tier evaluation, no Jev work, no runtime
change, no follow-on task without new explicit owner authorization.

