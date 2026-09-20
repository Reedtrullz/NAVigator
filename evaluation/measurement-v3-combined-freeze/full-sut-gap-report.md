# Full-SUT Gap Report

## Confirmed state

The dev-corpus-scorer-v1 TASK-LOCK registers
FULL_NAV_EXPLORE_SUT_NOT_AVAILABLE. No component in this workspace executes
the end-to-end NAV Explore product flow. The AFK campaign therefore freezes
the measurement system with terminal status MEASUREMENT-READY-SUT-MISSING.

## Interfaces the measurement system expects from a full SUT

1. Raw answer object per item with at minimum: routes, claims,
   uncertainty_expressed, evidence (field -> value), execution_status
   (consumed by dev-corpus-scorer-v1 scorer.py).
2. Capability flags: safety / routing / local_discovery (scorer capabilities).
3. SUT output text per semantic item (consumed by M2 and V2.15 lanes as
   sut_output; evidence spans are validated as verbatim substrings).
4. Case/gold metadata per corpus item: safety_priority, critical_error_if,
   acceptable_routes, forbidden_claims, required_uncertainty,
   required_evidence_fields (scorer contract v1).
5. M2-workflow classification for critical-condition items (which cases enter
   the M2 lane rather than the generic lane).
6. Item identity + provenance sufficient for single-owner routing and audit.

## Missing product components

- The product runtime itself: query handling, retrieval/local discovery
  integration, answer generation, and the glue that emits the raw answer
  object above. The frozen local-discovery runtime lineages (V2.x) cover
  evidence discovery only, are separately frozen, and are not wired here.
- A corpus loader that turns the existing dev-corpus-v1 corpus into scored
  cases with gold metadata at runtime.
- M2-workflow routing metadata on corpus items (currently synthetic).

## Existing and verified building blocks

- dev-corpus-scorer-v1: deterministic criteria scoring, frozen contract.
- measurement-v2-6: M2 human-review lane with frozen derivation table.
- measurement-v2-12: uncertainty human-review lane (frozen).
- measurement-v2-15: generic four-dimension semantic human-review lane
  (frozen, terminal SEMANTIC_HUMAN_REVIEW_FALLBACK_READY).
- measurement-v3-combined-freeze: combined engine with single-owner routing,
  escalation, fail-closed states, provenance, and the 9-gate integration suite.

## Next architecture proposal (not authorized by this task)

Phase 1: corpus loader + answer-schema adapter so the frozen scorer can run
against the existing 120-case dev corpus end to end. Phase 2: wire the frozen
local-discovery V2.4 candidate as the evidence provider behind the answer
generator, keeping provenance and fail-closed semantics. Phase 3: human-review
lane ingestion UI/CLI for M2 + generic lanes. Only after those exist does a
full SUT baseline become runnable, at which point a new blind/holdout task can
be drafted separately.
