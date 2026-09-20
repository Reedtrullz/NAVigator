# Process Deviations - Permanent Record

## V1_6A1_TARGETED_GOLD_PROCESS_DEVIATION = TRUE

- **Task:** NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6A1-ABSTAIN-REPAIR
- **Fixture:** ADV-11
- **What happened:** The fixture was disputed before execution (initial assertion
  reading of the first sentence conflicted with the unknown-noun sentence) and was
  resolved by the curator instead of being discarded and replaced with a new
  fixture, as the frozen section-20 dispute policy required.
- **Consequence:** The entire V1.6A.1 targeted-60 set is marked
  BURNED_DIAGNOSTIC_DATA. It can never serve as fresh evidence for any later
  lineage, including V1.6A.2.
- **Engine impact:** None. The frozen engine (SHA 40d85f317383...) was unaffected;
  the deviation was in gold curation, not in classification logic.
- **Historical result:** The official targeted-validation result remains exactly
  as recorded (overall/route precision 0.9677, one false deterministic on ADV-11).
  No retroactive rescoring.

## V1.6A.2 protocol commitments (this task)

- Contract section 29 dispute policy (DISPUTED_PRE_FREEZE -> remove -> replace
  with NEW ID -> label from scratch) will be followed without exception.
- Fixture authoring runs the candidate engine zero times
  (ENGINE_QUERIES_DURING_FIXTURE_AUTHORING = 0).
- The ADV-11 diagnostic fixture is used only for root-cause trace and mechanism
  abstraction (contract section 6), never as a regression anchor or exact-match
  target.

## V1.6A.2 DEV-02: Post-freeze bounded bugfix pass (contract section 49)

- **Trigger:** During blind official fixture authoring (batch 1), TDD-CROSS-07
  was added as a contract-derived RED case: hypothetical frame in one clause +
  assertion in another. The frozen engine emitted HYPOTHETICAL_ONLY because the
  mixed-polarity guard (BC_ROUTE_MIXED_POLARITY_03) did not count
  HYPOTHETICAL_ONLY as a commitment label.
- **Action:** Added HYPOTHETICAL_ONLY to the commitment set in
  BC_ROUTE_MIXED_POLARITY_03. No other engine change.
- **Order:** Genuine RED first (16/17 passing, TDD-CROSS-07 failing), then fix,
  then full suite re-verification: TDD 17/17, unit 72/72, burned-120 all gates
  PASS, burned-60 precision 1.0, ADV-11/ADV-15 both correct.
- **Scope:** No official fixture had been executed. No fresh-set tuning. No
  judge calls. Single bounded bugfix pass per contract section 49.
- **Engine re-hash:** Post-fix SHA recorded in official-fixture-hashes.json
  before official validation.
