# Forbidden Claim Analysis

## Residual set

6 forbidden_claim criteria FAIL in Wave 1 (old: 6). All have the prohibited content inside a "Nasjonal informasjon" retrieval block in the rendered answer; none is an assertion in the product's own voice.

| Case | Verdict | Gold forbidden | Observed content |
|---|---|---|---|
| DIS-100 | PRESENT | ingen resultater uten renderstatus | National block emits "Status: Lovstoff, NAV-brukerstoff... verifisert 30.08.2026" |
| DIS-105 | CLAIM_PRESENT | FULLY_VERIFIED | National block: "ROUTE_FULLY_VERIFIED - tjeneste + maalgruppe + tilgang + kontakt dokumentert" |
| DIS-116 | PRESENT | presenteres som fullfort | National block describes a completed "trinnvis discovery" with 18/20 cells recovered |
| DIS-118 | PRESENT | overtolkning av unge | National block cites services for "0-24 ar" beyond the case's scope |
| DIS-119 | CLAIM_PRESENT | lavterskel = drop-in | National block: 65-virkedager maximum-frist text (drop-in implication) |
| ROUT-042 | CLAIM_PRESENT | automatisk rett til aa forbli i BUP | National block: 65-virkedager / BUP content beyond case scope |

## Classification

- **Retrieval contamination: 6/6.** Every failure is unscoped retrieval material rendered into the answer. The product does not assert these claims itself.
- **Negation handling: 0.** No failure involves missing negation of a product assertion.
- **Quoting/attribution: 0 as failure mode.** The blocks are unattributed verbatim KB dumps, which is the contamination problem, not a quoting rule violation per se.
- **Renderer contamination: 0/6.** The renderer renders what retrieval/aggregation delivered; source is upstream.
- **Measurement sensitivity: 1/6 flagged separately.** ROUT-042 ("automatisk rett til aa forbli i BUP") is a known label-sensitivity case from prior lineages; it is retained here as an observed FAIL under the frozen contract but marked LABEL_SENSITIVITY_KNOWN and excluded from repair-candidate sizing.
- **Unclear: 0.**

## Conclusion

All 5 proven product-side failures (6 minus the label-sensitivity case) resolve to the same upstream mechanism as PW1-R4: unscoped/track-unfiltered retrieval blocks. A retrieval-scoping repair that prevents cross-domain and stale national blocks from entering answers addresses the entire residual forbidden-claim set without any forbidden-claim-specific logic. No Measurement V3 change is proposed or made.
