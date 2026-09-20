# V2 Selection/QA Root Cause - why construction QA said ALL_QUOTAS_PASS

Date: 2026-09-04. Evidence: RC2-V2-set/qa_check.sh (on disk), blind-manifest.json (on disk), quota-report.md, recovered construction-session data.

## 1. The mechanism

qa_check.sh section 5 ran this assertion:

    man = blind-manifest.json
    pa = man['pool_aggregates']
    assert sem['SUPPORTED'] >= 40 and sem['CONTRADICTED'] >= 40 and
            sem['PARTIALLY_SUPPORTED'] >= 40 and sem['INSUFFICIENT_EVIDENCE'] >= 30
    assert qf[flag] >= minimum   # for every structural flag

It read **pool_aggregates (n = 277)** and never **core_class_distributions (n = 160)**. Both blocks live in the same manifest. The pool block passed every assertion; the CORE block is where the failures lived (INSUFFICIENT 0, ABSTAIN 0, multi-span 18). The script then printed:

    PASS  quota targets: ALL_QUOTAS_PASS (pool snapshot, provenance recorded in manifest)

The manifest's own quota_verification string even discloses the pool scope ("pool n=277") - the scope qualifier was recorded, but the script treated it as satisfying spec quotas that are CORE-scoped.

## 2. Answers to the spec 4 audit questions

**Which quotas were checked pool-wide?** All of them: semantic classes, product classes, compound, multi_span, numeric, age_legal, temporal, actor, modality, safety, legal, locality, cond_exc. Every quota assertion in qa_check.sh reads pool_aggregates.

**Which should have been CORE-only?** Per spec 19-21, all of them: semantic class balance, genuine insufficiency >= 30, product classes >= 25 each, cond/exception >= 30, compound >= 50, multi-span >= 30, numeric/temporal/actor/modality >= 30, safety >= 20, legal >= 30, locality >= 20, age/legal adversarial >= 20.

**Selection ordering.** CORE selection (firewall design) ran first and placed cases by criteria that did not include quota constraints; all 40 genuine INSUFFICIENT cases were systematically routed to reserve. Quota validation then ran on the pool only, after selection, so the selection's CORE skew was never observed. The correct order is the reverse: enforce constraints ON the selection (constraint-based selection, spec 22), then verify on the selected CORE.

**Were semantic/product class quotas omitted at CORE level?** Yes - there is no assertion anywhere in qa_check.sh against core_class_distributions. The CORE distribution was published in the manifest and still passed QA.

**Was the agreement gate warning-only?** Yes. manifest.annotation_agreement.gate_met is false (0.7645/0.6232/0.7645 pool; 0.7799 CORE against target 0.90). qa_check.sh asserted only remaining_disputes == 0 - a post-adjudication cleanup number, not the pre-adjudication agreement gate. No exit-nonzero path referenced agreement.

**Completeness.** qa_check.sh never verified two-pass coverage. RC2B-0277 (single pass, recorded in the manifest note) passed QA silently.

## 3. Why the firewall selection dropped all INSUFFICIENT cases

The CORE selection was designed as a firewall (hardest cases) but its ordering criteria favored resolvable, evidence-rich cases; INSUFFICIENT_EVIDENCE cases by construction lack resolving evidence and were deprioritized into reserve. With no CORE-level constraint check after selection, the skew was invisible to QA. This is the construction bug V3's constraint-based selection (spec 22) and fail-closed CORE-only QA (spec 5-6, 43) are built to eliminate.

## 4. What V3 changes

1. construction_qa.py checks every hard quota against the CORE candidate list only; pool counts are reported informationally and can never satisfy a gate.
2. Selection is constraint-based: hard quotas are satisfied during selection (greedy with backtracking), not measured afterward.
3. Agreement gate (>= 0.90 all three, pre-adjudication) and double-annotation completeness are hard, fail-closed gates.
4. Adjudication rate <= 35% of CORE is a hard gate (spec 25), preventing the V2 pattern of adjudicating 73.6% of the pool to force agreement.
