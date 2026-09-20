# Annotation Contract V3 - RC2 Blind Set Construction

Date: 2026-09-04. Governing spec: NAV-EXPLORE-RC2-BLIND-V3-CONSTRUCTION sections 8-12. This contract governs ANNOTATORS ONLY. It does not change the evaluator runtime contract. It extends the existing evaluation contract with an operational, unambiguous annotation procedure.

## 1. Fixed per-case annotation order (mandatory)

For every case, annotate in exactly this sequence. Do not skip ahead; do not jump to product action.

1. **Atoms** - identify claim atoms (compound claims: list each atom separately).
2. **Semantic truth** - annotate the semantic truth of the full claim against the evidence.
3. **Required inference** - identify the inference the evaluator must draw (bounded inference, numeric comparison, condition resolution, etc.).
4. **Proof-safe verdict** - annotate whether the proof is safe to expose.
5. **Product expected action** - annotate the product action LAST.

Rationale: V2 disagreements showed pass-2 jumping to product action and back-filling semantic labels. Fixed order prevents slot contagion.

## 2. Explicit contradiction proof (semantic and proof-safe CONTRADICTED)

You may label semantic_truth or proof_safe as CONTRADICTED **only** when a positive conflict is documented in the annotation. Valid documentation (any one):

- the exact opposite span (evidence states the contrary),
- an incompatible same-quantity numeric fact (e.g. evidence says 12%, claim says 15%),
- an exhaustive exclusion (evidence enumerates the closed set and the claim's item is not in it),
- another already-permitted bounded inference that entails the negation.

**Absence of evidence is never contradiction.** If the evidence neither establishes X nor not-X, the semantic label is INSUFFICIENT_EVIDENCE, not CONTRADICTED. Each CONTRADICTED annotation must record: the span ID(s) and which of the four conflict types applies.

## 3. INSUFFICIENT vs REVIEW_REQUIRED decision rule

The proof-safe and product slots separate "cannot prove" from "needs a human":

- **proof_safe = INSUFFICIENT_EVIDENCE**: the evidence establishes neither the claim nor its negation; there is nothing further the system could extract from the provided sources to resolve it.
- **proof_safe = REVIEW_REQUIRED**: the evidence is incomplete, ambiguous, or partially conflicting, but a human with the same sources (or additional context) could plausibly resolve the case; the system must not auto-decide.
- **product_action = ABSTAIN_INSUFFICIENT**: genuine insufficiency should lead the product to abstain rather than guess.
- **product_action = REVIEW_REQUIRED**: the case needs further human evaluation but is not a clean abstain.

Annotators must justify the choice in one line. If you cannot articulate why the case is not resolvable from the sources, it is REVIEW_REQUIRED, not INSUFFICIENT.

**Gap-flag rule (amended 2026-09-04 after pilot round 1):** when the ONLY relevant evidence is an explicit statement that a fact was not verified/retrieved in the provided sources, annotate proof_safe = INSUFFICIENT_EVIDENCE and product_action = ABSTAIN_INSUFFICIENT. REVIEW_REQUIRED is reserved for evidence that is present but partially conflicting or ambiguous - not for absent evidence. "A human could find it elsewhere" never converts INSUFFICIENT into REVIEW.

**Gap vs silent absence (amended 2026-09-04 after pilot round 2):** classify each unresolved atom as gap-flagged or silent-absent. Gap-flagged: a provided source explicitly states the fact was not verified/retrieved, or poses it as an open unanswered question - annotate proof_safe = INSUFFICIENT_EVIDENCE and product_action = ABSTAIN_INSUFFICIENT. Silent-absent: no provided source addresses the atom at all - annotate proof_safe = REVIEW_REQUIRED and product_action = REVIEW_REQUIRED. In both cases, "a human could find it elsewhere" never changes the label.

## 4. PARTIAL is compound aggregation only

PARTIALLY_SUPPORTED is reserved for compound claims where the atoms split (some supported, some not). When using PARTIAL, show which atoms are supported and which are not.

PARTIAL is **never** a general "unsure" label. If you are unsure, use the INSUFFICIENT/REVIEW rule above. A single-atom claim is either SUPPORTED, CONTRADICTED, or INSUFFICIENT_EVIDENCE - never PARTIAL.

**Rider rule (amended 2026-09-04 after pilot round 1):** if a claim is one core assertion with an attached date/scope/quantity rider, annotate the atom outcomes separately. The claim-level semantic label is PARTIALLY_SUPPORTED iff the core is supported and the rider is not; it is CONTRADICTED only if the core itself is positively contradicted. An unsupported rider never upgrades or downgrades a contradicted core.

**Temporal/label riders count as atoms (amended 2026-09-04 after pilot round 2):** a date, year, scheme-name, or rate-label qualifier asserted by the claim (e.g. "i 2026", "fra 1. juli 2026", "den statlige veiledende satsen") is an atom. If the sources support the core amount or rule but not the qualifier, semantic_truth = PARTIALLY_SUPPORTED, never SUPPORTED.

**Main-rule hedge (amended 2026-09-04 after pilot round 2):** when a source states a rule with a hedge such as "som hovedregel", "normalt", or "vanligvis", and the claim asserts the same rule without the hedge, the implicit "unconditionally" atom is unsupported: semantic_truth = PARTIALLY_SUPPORTED. If the claim preserves the hedge, semantic_truth = SUPPORTED.

**Deterministic slot mapping (amended 2026-09-04 after pilot round 2):** semantic_truth drives the other two slots. SUPPORTED -> proof_safe = SUPPORTED, product_action = AUTO_SUPPORTED. CONTRADICTED -> proof_safe = CONTRADICTED, product_action = AUTO_CONTRADICTED. INSUFFICIENT_EVIDENCE or PARTIALLY_SUPPORTED -> classify every unresolved atom by the gap-vs-silent rule above: if any unresolved atom is gap-flagged, proof_safe = INSUFFICIENT_EVIDENCE and product_action = ABSTAIN_INSUFFICIENT; otherwise (silent-absent or present-but-conflicting) proof_safe = REVIEW_REQUIRED and product_action = REVIEW_REQUIRED. This mapping is mandatory; do not deviate case by case.

## 5. Fixed label vocabulary (no variants)

Use exactly these strings, in exactly these slots:

| Slot | Allowed labels |
|---|---|
| semantic_truth | SUPPORTED, CONTRADICTED, PARTIALLY_SUPPORTED, INSUFFICIENT_EVIDENCE |
| proof_safe | SUPPORTED, CONTRADICTED, INSUFFICIENT_EVIDENCE, REVIEW_REQUIRED |
| product_action | AUTO_SUPPORTED, AUTO_CONTRADICTED, REVIEW_REQUIRED, ABSTAIN_INSUFFICIENT |

**Known V2 bug, do not repeat:** the V2 passes used two different proof-safe vocabularies (INSUFFICIENT vs INSUFFICIENT_EVIDENCE), producing 33 fake disagreements. Any label outside the table above is a contract violation and the case must be re-annotated.

## 6. Pilot gate

Before any full V3 selection: >= 30 varied candidates, two fully independent passes, agreement >= 0.90 on semantic, proof-safe, and product action measured BEFORE any adjudication. If any slot is below 0.90: STOP, status ANNOTATION_CONTRACT_NOT_READY, do not seal V3. Adjudication may not be used to raise the measured agreement.

## 7. Disagreement handling

Disputes are adjudicated only after agreement is measured. Adjudication follows the rules above; it may not invent new labels. CORE adjudication rate must stay <= 35% (target <= 25%).
