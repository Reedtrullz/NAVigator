# PHASE 2B - RC2 BLIND V4 SCORING (POST-FREEZE)

Task: NAV-EXPLORE-RC2-BLIND-V4-PHASE2B-SCORING

Mechanical scoring of the 160 frozen RC2-V4 CORE predictions with the
frozen scoring policy and frozen scorer, after authenticated decryption
of answer-key.sealed. Official score was written and hash-frozen BEFORE
any individual error inspection.

## Order of operations (executed)

1. TASK-LOCK-PHASE2B.json written; no runtime/prediction/policy/key changes allowed.
2. Pre-decryption integrity: prediction/policy/scorer/certification-metrics
   SHAs verified; RC2 manifest 10/10 components; V4 blind-cases, sealed
   answer key, sealed construction audit all match blind-manifest.json.
3. AES-256-GCM authenticated decryption of answer-key.sealed in memory
   (key: memory-only shell variable, never written to disk). AAD =
   urlsafe-b64 of the blind-cases SHA hex bytes, per blind-manifest.
4. Structural answer-key validation: 160 rows, 160 unique IDs, exact ID
   equality with predictions, all label fields present 160/160, 62
   compound cases with complete atoms (141 total), 40 critical/120
   standard, annotation statuses valid, unresolved disputes 0.
5. Plaintext fed to the frozen scorer through an unlinked /tmp FIFO
   (no plaintext answer key on disk). Frozen scorer applied the frozen
   policy mechanically; official-score.json written.
6. official-score.json SHA-256 = e47890d0f5bd57f1f326e679adc8c9707998d663b46445e202adc969ebaa14b2,
   frozen in official-score-freeze.json with error_analysis_started=false.
7. Only after the freeze: error analysis, confusion matrices, subgroup
   and compound deliverables, label audit, sensitivity audit.
8. Post-analysis rehash: all frozen artifacts unchanged.

## Files

* official-score.json - frozen mechanical score (input to everything else)
* official-score-freeze.json - freeze record
* certification-results.json - machine-readable gates + verdict
* semantic-confusion.json / proof-safe-confusion.json / product-confusion.json
  (rows expected, columns predicted; corrected post-freeze view)
* subgroup-results.json - product exact per frozen subgroup membership
* compound-results.json - compound product + atom accuracy
* proof-audit.json - accepted proof audit
* error-analysis.json / error-analysis.md - per-case errors (post-freeze)
* label-audit.md - potential blind label errors + audited sensitivity
* certification-report.md / final-report.md - narrative + checklist

## Notes

* The Phase-2B driver (score_phase2b.py) is new in Phase 2B and is NOT
  part of the frozen artifact set. It performs decryption, structural
  validation, and field mapping only (nested sealed schema to the flat
  schema the frozen scorer expects). No label values were read or
  transformed.
* Known scorer display-key defect (RC3_BUG_CANDIDATE, post-freeze):
  the frozen scorer's semantic confusion matrix looks up the predicted
  column key "REVIEW_REQUIRED_PREDICTED_ONLY" while its counter stores
  raw "REVIEW_REQUIRED". 103 review predictions are therefore omitted
  from the matrix view inside official-score.json. All exact metrics,
  gates, and the verdict are unaffected (53 diagonal + 57 + 103 = 160).
  The corrected matrix is in semantic-confusion.json.
* KEY_ACCEPTED = TRUE. Key not persisted anywhere; key-carrying shell
  session terminated after scoring; disk scans clean.
