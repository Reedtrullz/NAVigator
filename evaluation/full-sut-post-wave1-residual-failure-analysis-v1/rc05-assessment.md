# RC-05 Assessment: Evidence Completeness

RC-05 (evidence completeness) was deferred. This assessment splits the 38 residual evidence FAILs (score 0.0) into missing provenance vs attachment defects.

## Attachment classes (recomputed)

| Class | Count | Meaning |
|---|---|---|
| PROV_HAS_URL_NOT_ATTACHED (MIXED) | 23 | Provenance entries with source URLs exist; evidence dict fields never populated |
| NO_PROVENANCE_ENTRIES | 15 | No provenance entries at all |
| Total | 38 | 17 SAF + 10 ROUT + 11 DIS |

## Sub-mechanisms

1. **Attachment defect (23 cases, standalone-repairable).** The data required by the scorer exists in the prediction's provenance array (with URLs) but is never copied into the evidence dict keys the scorer checks. The safety pattern is the clearest: all 17 SAF cases carry a correct top-level safety_priority, and none copy it into evidence. This is a mechanical field-mapping defect inside the evidence aggregation stage.
2. **Upstream retrieval gap (15 cases).** No provenance entries exist at all, meaning the retrieval/aggregation stage produced nothing to attach. These are downstream of the retrieval-contamination/scoping defect (PW1-R4) and of route absence; fixing attachment alone cannot score them.

The 3 RC-01 residual rows (DIS-096, DIS-099, ROUT-053) are the same URL-resolution defect as sub-mechanism 1, surfacing at the critical_condition layer instead of evidence_completeness.

## Standalone or downstream?

**Both, in fixed proportion:** roughly 60% of the residual evidence failures are a genuine standalone attachment defect (sub-mechanism 1), and 40% are downstream of retrieval. A scoped evidence-attachment repair addresses the 23 + 3 rows without touching retrieval; the remaining 15 wait for upstream repairs.

**Recommendation shape:** RC-05 is justified as a narrow, deterministic evidence-attachment repair (sub-mechanism 1 only), sequenced after or alongside route-selection work; it should not be sized as a full evidence-pipeline repair.
