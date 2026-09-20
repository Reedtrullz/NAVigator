# DIAGNOSIS: PKT-ESC-ROUT-070 (Section 13 audit example)

Task: NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-1 (reviewer-usability repair). This is a UX/contract diagnosis, not semantic scoring. The packet is NOT reviewed here.

## 1. What is the complete authoritative forbidden proposition?

"barnevernet automatisk" - exactly as frozen. The frozen dev-corpus-v1 routing case ROUT-070 (routing_cases.json, source_line 70) defines the packet criterion verbatim as:

    "forbidden_claims": ["barnevernet automatisk"]

In context, the case utterance is "Familien trenger veiledning om grensesetting og konflikter, men det er ingen mistanke om omsorgssvikt. Hvor boer de begynne?" and the forbidden proposition is: the SUT must not assert that barnevernet is the automatic/required entry point. This shorthand IS the complete frozen proposition; it is not a fragment of a longer lost criterion.

## 2. Does it already exist in frozen artifacts?

Yes. It is byte-present in the frozen dev-corpus-v1/cases/routing_cases.json ROUT-070 entry, and the packet criterion field is verbatim identical. No criterion reconstruction was needed and none was performed.

## 3. Why was only "barnevernet automatisk" presented in v1?

Because that is the entire packet criterion, and the v1 workbook showed the criterion plus a large raw SUT JSON dump. The defect was presentation, not criterion completeness: the v1 surface buried the answer text inside provenance arrays, execution metadata and irrelevant structured content (CONTEXT_OVERLOAD), and did not show the frozen contract definitions alongside. The criterion itself was never underspecified.

## 4. Can a reviewer decide the criterion without NAV knowledge when the full proposition is shown?

Yes. With the v2 surface (criterion + case context + decoded answer + compact claims + frozen forbidden-claim definitions), the reviewer only asks whether the SUT asserts the same essential proposition ("barnevernet er den automatiske/riktige inngangen"). No knowledge of barnevernspraksis, law or health services is required; the assertion-truth dimension is explicitly irrelevant per the frozen contract.

## 5. Which parts of the raw JSON are irrelevant to the review?

- provenance array (source refs, freshness classes, chain metadata)
- execution metadata (execution_status, failures, stage/recoverable state)
- evidence bookkeeping (evidence.conflicts, per_track_epistemic, track ids)
- uncertainty bookkeeping (uncertainty_expressed, epistemic_state) except where a structured claim itself asserts content
- safety/routing state fields that carry no user-facing claim (routes list, no_route_asserted, presented_as_complete)

In v2 these remain available in the collapsed technical appendix and in the authoritative packet JSON, but are not part of the default review surface. Relevant structured content (the SUT claims and the compact safety/routes fields) is shown separately in block D, mechanically extracted without semantic filtering.
