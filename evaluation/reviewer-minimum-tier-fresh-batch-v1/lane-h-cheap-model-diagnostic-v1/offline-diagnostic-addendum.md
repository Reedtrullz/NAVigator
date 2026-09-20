# Offline Diagnostic Addendum V1

Task: NAV-EXPLORE-LANE-H-CHEAP-MODEL-DIAGNOSTIC-V1 (post-terminal offline addendum)
Scope: read-only recomputation of existing per-row results; no new inference, no semantic calls, no changes to frozen artifacts or diagnostic-report.md.

## D1. Recomputed counts (numerators / denominators explicit)

Recomputed directly from per-row-comparison.jsonl (150 unique rows). All original report numbers confirmed; no corrections.

| Route / view | Planned N | Valid | Invalid | Ref hits / valid | Ref hits / planned |
|---|---|---|---|---|---|
| MIMO full | 150 | 115 | 24 INVALID_JSON + 11 INVALID_MODEL_REVIEW | 76/115 = 66.1% | 76/150 = 50.7% |
| MIMO A | 109 | 81 | 11 INVALID_MODEL_REVIEW + 17 INVALID_JSON | 62/81 = 76.5% | 62/109 = 56.9% |
| MIMO B | 41 | 34 | 7 INVALID_JSON | 14/34 = 41.2% | 14/41 = 34.1% |
| DeepSeek full | 150 | 150 | 0 | 104/150 = 69.3% | 104/150 = 69.3% |
| DeepSeek A | 109 | 109 | 0 | 99/109 = 90.8% | 99/109 = 90.8% |
| DeepSeek B | 41 | 41 | 0 | 5/41 = 12.2% | 5/41 = 12.2% |

## D2. Pairwise hits over the 115 both-valid rows

- Both match reference: 62
- Only MIMO matches: 14
- Only DeepSeek matches: 16
- Both deviate with same label: 16; both deviate with different labels: 7
- DeepSeek paired hits: (62 + 16)/115 = 78/115 = 67.8%
- MIMO paired hits: (62 + 14)/115 = 76/115 = 66.1%

Union separation (mutually exclusive, no double counting):

- Union of label deviations (both valid, at least one deviates): 53 rows.
- Union of invalid outcomes (MIMO invalid on the row): 35 rows (0 overlap with the 53).
- Union of (label deviation OR invalid): 53 + 35 = 88 rows.

The original report's paired-over-B numbers (MIMO proposed 14 / alternative 16 / other 4; DeepSeek proposed 4 / alternative 29 / other 1) remain unchanged.

## D3. Root causes of MIMO's 35 invalid outcomes

All 35 have finish_reason = "stop" (no transport failures). Per-row detail: mimo-invalid-causes.jsonl in the export package.

INVALID_JSON (24): every raw response was fenced with markdown code fences (```json ... ```). 23 of 24 parse cleanly after fence stripping. The single exception, FB1-SCR-103, is additionally truncated/malformed: the JSON is coherent up to the evidence_spans array (unterminated), then a stray `" "rationale"` fragment appears; json.loads fails at char 181 ("Expecting ':' delimiter"). All 24 remain INVALID in the original scoring; the fence observation is diagnostic only.

INVALID_MODEL_REVIEW (11): all failed the verbatim-span check (span_not_verbatim). Two subgroups:

1. Quote-annotation prefix as span (7 rows): 008, 013, 023, 038, 073, 093, 118. The span includes commentary such as "Tidligere tekst sa: '...'" or leading quotation marks; the quoted SUT text inside is usually verbatim, but the span as submitted is not a verbatim substring.
2. Near-cited paraphrase (4 rows): 059 (model wrote "at naevne" vs SUT "a nevner" - grammar variant), 075 (span wrapped in <<<SUT ... SUT>>> decoration), 076 and 126 (single-letter typo "oppgrir" for "oppgir" - the typo exists only in the model output, not in the SUT text).

Disposition (owner review 2026-09-20): fence handling and evidence-span rewriting are different interventions. Removing an outer markdown wrapper and editing the decoded evidence field are NOT the same. The 23 fence-strippable responses were not normalized or re-scored in the original scoring; they were replayed read-only with unchanged validation (D5). The 11 span_not_verbatim rows remain invalid under the current contract; any tolerant evidence mechanism would be a separate, explicit design change, not a silent repair of this scoring. FB1-SCR-103 additionally needs a truncation/malformed-JSON policy.

## D4. Model identity as measured

- MIMO: requested wire command-code/xiaomi/mimo-v2.5-pro; model_reported = "command-code/xiaomi/mimo-v2.5-pro" on all 150 rows. Consistent.
- DeepSeek: requested wire B.AI/deepseek-v4-flash-vision-exp; model_reported = "deepseek-v4-flash-vision-exp" on all 150 rows (proxy strips the vendor prefix). The frozen provider-route-selection.json (BAI-DEEPSEEK, sha c7a8c7b6...) documents the same wire ID for the authorized B.AI route. No evidence of reroute or alias drift.
- Underlying vendor identity behind the B.AI proxy: UNKNOWN (no provider metadata was persisted). Reported name "DeepSeek v4-flash-vision-exp" is consistent with the authorized route; no route deviation is claimed and none is concealed.

## D5. Fence-only replay (offline, hypothetical; original scoring unchanged)

Owner-directed replay of the 24 INVALID_JSON responses: strip ONLY the outer markdown fence, then apply the identical JSON/schema/verbatim-span validation used in the original run (exact validate() replica; same ENUM and SPAN_REQUIRED). No span text is added, removed, or rewritten. The 11 INVALID_MODEL_REVIEW rows are NOT eligible for this replay: their defect is inside the decoded evidence field, not the outer format.

Result over the 24 INVALID_JSON rows:

- 22 RECOVERABLE_PASS: parse + full unchanged validation pass (16 view A, 6 view B).
- 1 STILL_INVALID: FB1-SCR-040 parses after fence strip but fails span_not_verbatim - confirming that parse success does not imply full validation pass.
- 1 STILL_INVALID: FB1-SCR-103 remains malformed/truncated (json_parse_failed).
- Of the 22 recoverable: 14 match the AI proposed reference, 5 match the AI alternative label, 3 match neither.

Hypothetical counts if fence handling had been part of the integration (HYPOTHETICAL_REPLAY_ONLY; not a measured model improvement, not a new official score, original scoring unchanged):

| Route / view | Valid | Ref hits / valid | Ref hits / planned |
|---|---|---|---|
| MIMO full | 137/150 = 91.3% | 90/137 = 65.7% | 90/150 = 60.0% |
| MIMO A | 97/109 | 75/97 = 77.3% | 75/109 = 68.8% |
| MIMO B | 40/41 | 15/40 = 37.5% | 15/41 = 36.6% |

The conditional ceiling in the owner review (115 + 23 = 138/150) is not reached: FB1-SCR-040 fails the verbatim-span check after parsing, so actual fence-only recovery is 115 + 22 = 137/150 valid. Whether these 22 responses would have matched the reference in a real run under a fence-tolerant parser is what the reference-match counts above describe hypothetically; DeepSeek's 26/9 split on the 35 Mimo-invalid rows (D6) is measured.

Per-row dispositions: fence-only-replay.jsonl in the export package.

## D6. Whole-set deviation accounting (per owner review)

- Pairwise label deviations (115 rows both valid): 53 rows (D2).
- On the 35 rows where MIMO is invalid, DeepSeek is valid on all 35: reference match 26, deviate 9 (recomputed from per-row-comparison.jsonl).
- Whole-set rows with at least one available valid model outcome deviating from the AI reference: 62 = 53 + 9.
- Union identity: 62 deviation rows + 35 Mimo-invalid rows - 9 overlap = 88 total problem rows (same 88 as D2, two decompositions).
- The 9 DeepSeek deviations without a valid Mimo outcome are preserved in per-row-comparison.jsonl and disagreements-vs-ai-reference.jsonl and remain in scope for any later semantic review; they are not captured by the pairwise 53.

## D7. Verification against the independent owner-side audit (2026-09-20)

An independent owner-side audit (ChatGPT sandbox review of the exported package) reported four findings. All four were re-verified read-only against local raw data before this note was written. Original diagnostic-report.md remains frozen and uncorrected; corrections live here.

1. Report error (CONFIRMED): diagnostic-report.md line 48 states "3/30 exact each" for AMBIGUOUS_OR_CONFLICTING reference rows. Recomputed from per-row-comparison.jsonl: MIMO original 10/30, DeepSeek 3/30. The frozen report's machine-readable counts (12 of 30 MIMO -> CLEAR_TRIGGER_SUPPORT, 26 of 30 DeepSeek -> CLEAR_TRIGGER_SUPPORT) are correct; the prose "3/30 exact each" is wrong for MIMO. After fence-only replay MIMO modal hits = 11/30 (FB1-SCR-032 recovers as a reference hit; 032/047/092/117 are the recovered modal rows).
2. Constant semantic_input_hash (CONFIRMED): all 300 result rows carry an identical semantic_input_hash while request_fingerprint is unique per row/route. The field cannot document row input identity and must not be used alone for cache/resume keys. Recomputed per-row input hashes exist only in the owner-side audit package; they are not reproduced here.
3. Manifest self-hash (CONFIRMED): export-manifest.json carried a contents_sha256 entry for itself that could not match its own file (pre-write hash). Actual self SHA at last export was 8d7ef707...6bee26c7. Corrected by removing the self-referential entry below; EXPORT-SHA256.txt sidecar remains the integrity anchor for the ZIP.
4. FB1-SCR-103 cause wording (CONFIRMED as owner-audit description): the response is a fenced, complete-length object with finish_reason=stop and a closed evidence list; the syntactic defect is a stray extra quote before "rationale". Addendum D5/D6 previously described this as "truncated/malformed"; the malformed-JSON wording stands, the truncation implication is withdrawn. No token-budget increase or response reconstruction is supported by the raw data.

Additional owner-audit observations verified but not previously stated locally: MIMO ran json_mode_effective=false on all 150 rows, DeepSeek true on all 150; format-reliability differences are therefore model+configuration effects, not model-name effects alone. Pairwise on the 137 rows valid for both models after replay: DeepSeek 95 reference hits, MIMO 90. SCR-040's source SUT text contains the malformed token "kunret"; the model's span reads "kun ret", so the span is not verbatim relative to the source text (model-side spacing change, still invalid).
