# Annotation disagreements (pass-1 vs pass-2)

Pass-1: codex-first-hand (contract + engine-layer knowledge). Pass-2: gpt-5.6-luna x3, independent, prompt-only (claim + evidence + evaluation contract, no pass-1 access).

Raw cross-pass agreement: semantic_truth 15/21, proof_safe 10/21, product_action 10/21, required_operator 7/21. Fully identical on 4/21 (CAL063, CAL073, CAL088, LOC-13).

Adjudication rule: contract text and engine-layer facts govern; no forced agreement. Final labels: `review-final-dual-labels.json`. Residual unresolved disputes: 0.

| Case | Divergence (pass1 vs pass2) | Resolution | Status |
|---|---|---|---|
| CAL011 | proof_safe INSUF vs SUPPORTED; operator TIER1 vs DIRECT_PROOF | Direct proof constructible from source; engine lexicon gap is the blocker. Final: SUPPORTED/AUTO_SUPPORTED, TIER1_OPERATOR, bug candidate. | RESOLVED_NEW |
| CAL014 | Same shape as CAL011 ('ingen kostnad'/'ingen henvisning' double negatives) | Final: SUPPORTED/AUTO_SUPPORTED, TIER1_OPERATOR, bug candidate. | RESOLVED_NEW |
| CAL015 | operator TIER2 vs DIRECT_PROOF (labels agree) | Luna right on outcome, mechanism label wrong: engine cannot fire today. Final: RULE_PLUS_CONDITION (Tier-2), near-verbatim span. | PASS1_CONFIRMED |
| CAL020 | proof_safe INSUF vs SUPPORTED; action REVIEW vs AUTO_SUPPORTED | Pass-2 inferred after-cutoff from silence + date arithmetic; contract requires explicit premise. Boundary operator unmapped. | PASS1_CONFIRMED |
| CAL025 | proof_safe INSUF vs CONTRADICTED; action REVIEW vs AUTO_CONTRADICTED | Compound-atom adjudication: contradicted conjunct falsifies conjunction (contract-legal necessary implication). Pass-2 outcome accepted with strict preconditions. | RESOLVED_NEW |
| CAL031 | sem INSUF vs CONTRADICTED; action REVIEW vs AUTO_CONTRADICTED | Hedge 'normalt ikke' + unestablished actor membership; N-R1 adversarial shape. Auto-CONTRADICTED unsafe. | PASS1_CONFIRMED |
| CAL034 | proof_safe INSUF vs CONTRADICTED; operator TIER1 vs DIRECT_PROOF | 4 G vs 6 G conflict; NUMERIC_CONFLICT blocked by G-unit lexing. Bug candidate. | RESOLVED_NEW |
| CAL044 | sem CONTRADICTED vs PARTIAL | False conjunct ('lovfestet individrettighet' vs 'KAN'/'skjonnsbestemt') falsifies conjunction. Proof-side remains INSUF. | PASS1_CONFIRMED |
| CAL072 | sem INSUF vs PARTIAL | 'Noen kommuner' cannot establish 'min kommune'. | PASS1_CONFIRMED |
| CAL077 | sem/proof INSUF vs CONTRADICTED/CONTRADICTED; action ABSTAIN vs AUTO_CONTRADICTED | Source silent on January; silence is not exclusivity. Pass-2 assumed closed world. | PASS1_CONFIRMED |
| CI-062 | sem INSUF vs CONTRADICTED; action ABSTAIN vs AUTO_CONTRADICTED | Semantic truth accepted as CONTRADICTED ('ikke lovregulert' contradicts fixed 2-year rule). Proof stays INSUF (negation scope); product REVIEW_REQUIRED. | RESOLVED_NEW |
| D20-A5 | action REVIEW vs AUTO_SUPPORTED; operator REVIEWER_SEMANTIC vs DIRECT_PROOF | Marked disjunction ('eller') with enumerated signatories; outcome AUTO_SUPPORTED accepted, mechanism adjudicated as ACTOR_MEMBERSHIP with strict preconditions. | RESOLVED_NEW |
| HOL006 | sem CONTRADICTED vs PARTIAL; proof/action INSUF/REVIEW vs CONTRADICTED/AUTO_CONTRADICTED | 2,48 vs 2,25 falsifies conjunct; compound-atom doctrine. Bug candidate (G-multiplier lexing). | RESOLVED_NEW |
| HOL014 | Same shape (6 585 vs 6 385, thousands-separator lexing) | Bug candidate. | RESOLVED_NEW |
| HOL023 | proof/action INSUF/REVIEW vs CONTRADICTED/AUTO_CONTRADICTED | Nested negation scope makes deterministic polarity unsafe. | PASS1_CONFIRMED |
| LOC-07 | sem/proof/action INSUF/INSUF/REVIEW vs SUPPORTED/SUPPORTED/AUTO_SUPPORTED | Subjectless address line; binding requires hidden document-context premise. | PASS1_CONFIRMED |
| MOD-14 | proof_safe INSUF vs SUPPORTED; operator TIER1 vs DIRECT_PROOF | Verbatim support constructible; missing lexicon concept + dummy-actor extraction. Bug candidate. | RESOLVED_NEW |

Pattern: pass-2's prompt-only view systematically over-credits `DIRECT_PROOF_ALREADY_EXISTS` (13/21) because it cannot see engine-layer failures (lexicon, lexer, actor equality). Where both passes agreed on the outcome but pass-1 attributed an engine gap, the engine-layer attribution was kept and registered as IMPLEMENTATION_BUG_CANDIDATE (7 cases) rather than as achievable direct proof.
