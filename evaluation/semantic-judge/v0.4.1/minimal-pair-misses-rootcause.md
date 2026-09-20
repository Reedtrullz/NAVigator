# Minimal-Pair Miss Root Cause (spec section 7)

Data: v0.4 minimal pairs combined grade (40/52 = 76.92%), judge C = gpt-5.6-luna. Sources: v0.4/results/v04-minimal-pairs-combined-grade.json, v04-results-minimal-pairs-C-judge-c-gpt-5.6-luna.json, v04-results-minimal-pairs-supplement-C-judge-c-gpt-5.6-luna.json.

Note: the main bench and the supplement reuse the IDs MP-014A/B and MP-015A/B for different cases; all IDs below are tagged main/supp. The supplement adds 2 negation cases (both correct) and 2 temporal cases (1 miss).

## Per-dimension table (bench labels)

| Dimension | N | Correct | Accuracy |
| --------- | -: | ------: | -------: |
| actor | 13 | 13 | 100.0% |
| modality | 8 | 8 | 100.0% |
| negation | 6 | 6 | 100.0% |
| numeric | 4 | 0 | 0.0% |
| scope | 12 | 7 | 58.3% |
| temporal | 9 | 6 | 66.7% |
| Total | 52 | 40 | 76.9% |

Confusion pattern: SUPPORTED->INSUFFICIENT_EVIDENCE 8, CONTRADICTED->INSUFFICIENT_EVIDENCE 3, INSUFFICIENT_EVIDENCE->PARTIALLY_SUPPORTED 1. The judge over-routes to INSUFFICIENT when qualifiers, hedges, or noun-level coreference gaps are present.

## Miss-by-miss audit

### NUMERIC (4 misses, 0/4)

| ID | Expected -> Got | Mechanism |
| --- | --------------- | --------- |
| MP-007A | SUPPORTED -> INSUFFICIENT | Claim "normalt 4 652/mnd" vs source "4 652 (ett bosted)". Hedge weaker than exact value; same numeric value. Judge treated "(ett bosted)" qualifier as scope mismatch and never compared numbers. |
| MP-007B | CONTRADICTED -> INSUFFICIENT | Claim "4 200/mnd" vs source "4 652 (ett bosted)". Mutually exclusive values, but scope-mismatch reasoning preempted the numeric conflict. |
| MP-014A | SUPPORTED -> INSUFFICIENT | Claim "Vanlig sats er 1 006/mnd" vs source "delt ordinær barnetrygd 1 006/mnd per forelder". Same value; qualifier "per forelder" treated as unresolved scope instead of compatible naming of the rate's unit. |
| MP-014B | CONTRADICTED -> INSUFFICIENT | Claim "over 1 500/mnd" vs source "1 006/mnd". Incompatible magnitude; again preempted by scope reasoning. |

Classification: NUMERIC with SCOPE-precedence failure. Root cause: when a scope/qualifier mismatch is (sometimes wrongly) detected, numeric comparison is skipped and the verdict collapses to INSUFFICIENT even for mutually exclusive values. Also, hedged claim modality (USUALLY) vs exact source value is not recognized as COMPATIBLE_WEAKER.

### TEMPORAL (3 misses)

| ID | Expected -> Got | Mechanism |
| --- | --------------- | --------- |
| MP-009A | SUPPORTED -> INSUFFICIENT | "Ordningen gjelder fra 1.7.2026" vs "Regelen gjelder fra 1.7.2026". Same date, noun-level coreference gap ("ordningen" vs "regelen"); subject_match=false sank the atom. |
| MP-015A (main) | SUPPORTED -> INSUFFICIENT | "senest 3 måneder etter meldefristen" vs "senest 3 måneder etter 1-ukesfristen". Same deadline under different names; coreference not resolved. |
| MP-015A (supp) | SUPPORTED -> INSUFFICIENT | Application before cutoff follows old rules. Source: new rules apply to applications sent after 01.07.2026. Judge did not infer temporal closure (before-cutoff = old rules); wanted explicit statement. |

Classification: TEMPORAL. Root cause: (a) same-date/deadline equivalence fails on noun-level coreference; (b) implicit temporal closure (rule applies after X implies previous rule before X) is not derived deterministically.

### SCOPE (5 misses)

| ID | Expected -> Got | Mechanism |
| --- | --------------- | --------- |
| MP-011B | INSUFFICIENT -> PARTIALLY_SUPPORTED | Two conjunctive mechanisms; source establishes only one. Unsupported conjunct yielded "unknown" atom but fusion still returned PARTIALLY_SUPPORTED. |
| MP-013B | CONTRADICTED -> INSUFFICIENT | Claim "teller ikke i Husbankens inntektsgrunnlag" vs source "reduserer ikke bostøtten direkte". Source's opposite assertion on the income basis not linked to the claim's formulation. |
| MP-016A | SUPPORTED -> INSUFFICIENT | Claim "ved nytt barn i husstanden reduseres bidraget" vs source "lav inntekt reduserer bidraget". Compatible-but-different trigger; judge demanded the claim's exact cause in source. |
| MP-022A | SUPPORTED -> INSUFFICIENT | Claim "Kommunen kan ha egne lavterskeltilbud" vs source "Kommunene kan ha egne lavterskeltilbud innen psykisk helse". Claim narrower than source; domain qualifier wrongly read as scope mismatch. |
| MP-024A | SUPPORTED -> INSUFFICIENT | "Krisesentrene er gratis" vs "Opphold på krisesenter er gratis". Same property, general-vs-instance phrasing; judge demanded literal subject equality. |

Classification: LOCALITY_SCOPE with RELATION_EXTRACTION and fusion-policy components. Root causes: (a) a source qualifier ("innen psykisk helse", "ett bosted") or a source-side cause makes the judge declare scope mismatch even when the claim is a compatible narrowing or a hedge of the source assertion; claim-narrower-than-source should be compatible support when the source uses MAY/exact value; (b) conjunctive claims with one unknown conjunct must route to INSUFFICIENT, not PARTIALLY_SUPPORTED; (c) subject identity is judged by literal noun overlap rather than normalized actor/instance relation (krisesentrene = krisesenter-opphold setting).

## Cross-cutting implications for the v0.4.1 repair (general rules, no testcase patches)

1. Compute numeric relation independently of scope relation; mutually exclusive numeric values route to CONTRADICTION unless modality makes them compatible (hedge vs exact = COMPATIBLE_WEAKER -> SUPPORTED at claim level with weaker strength).
2. Normalize temporal expressions (dates, deadlines, cutoffs) and derive temporal closure deterministically; treat "same value, different noun" via subject normalization, not literal match.
3. Represent source qualifiers as claim-side scope relations (claim NARROWER/SAME/BROADER than source assertion), with NARROWER of an affirmed assertion = supported; UNKNOWN qualifier never blocks numeric/temporal affirmation.
4. Fusion policy for conjunctions: any atom INSUFFICIENT and none CONTRADICTED -> INSUFFICIENT (not PARTIALLY_SUPPORTED); PARTIALLY_SUPPORTED only when at least one atom SUPPORTED and at least one CONTRADICTED.
5. Replace boolean subject/scope matches judged by literal nouns with normalized actor/scope primitives (spec sections 13-14).
