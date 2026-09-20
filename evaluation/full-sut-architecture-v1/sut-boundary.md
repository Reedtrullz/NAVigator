# SUT Boundary

## Definition

The full NAV Explore SUT is the product pipeline that receives one canonical
case input (user query + context) and returns one canonical structured output
(user-facing answer + machine-readable decision state) without access to gold,
scorer metadata, or expected labels.

## Input (canonical, versioned as sut-input/v1)

    {
      "case_id": "ROUT-021",
      "user_query": "Datteren min paa 13 har alvorlig skolevegring. ...",
      "profile": {"age": 13, "role": "user"},
      "context": {},
      "location_context": {},
      "timestamp_context": {"executed_at": "2026-09-14T08:00:00Z"}
    }

- case_id: identity only; the SUT does not interpret it.
- user_query: the user-facing text (corpus utterance in evaluation, free text
  in production).
- profile: age and role as provided by the corpus or caller.
- location_context: municipality/fylke when known; may be absent -> the
  discovery stage responds fail-closed (UNVERIFIED locality), never guesses.
- timestamp_context: execution time; freshness checks compute from it.
- The SUT receives NO gold, NO corpus family, NO scoring-model fields. The
  loader is responsible (corpus-loader-design.md).

## Output (canonical, versioned as sut-output/v1)

    {
      "answer": "user-facing Norwegian text",
      "safety": {"priority": "ACUTE_RISK_NOW", "signals": [], "suppressed_routing": true},
      "tracks": [{"track_id": "T1", "domain": "mental_health", "status": "RESOLVED"}],
      "routes": [{"label": "113", "provenance_ids": ["P1"], "epistemic_state": "FULLY_VERIFIED"}],
      "claims": [{"text": "...", "provenance_ids": ["P1"], "kind": "LEGAL_REQUIREMENT"}],
      "uncertainty_expressed": ["..."],
      "evidence": {"safety_priority": "ACUTE_RISK_NOW", "source_url": "..."},
      "provenance": [{"id": "P1", "source_url": "...", "verified_at": "..."}],
      "epistemic_state": "ACCESS_PARTIAL",
      "failures": [{"stage": "local_discovery", "state": "RECOVERABLE"}],
      "execution_status": "SUCCESS",
      "no_route_asserted": false,
      "presented_as_complete": true
    }

Field-by-field contract: sut-output.schema.json. The raw answer object the
scorer consumes is exactly routes / claims / uncertainty_expressed / evidence /
execution_status / safety_priority / no_route_asserted /
presented_as_complete; answer, tracks, provenance, epistemic_state, and
failures are product-level extensions measurement can consume without
heuristic prose parsing.

## What crosses the boundary

- IN: the input object above. Nothing else. No evaluator artifacts, no gold,
  no prior SUT outputs.
- OUT: the output object above. The SUT does not score, does not read the
  corpus files, does not import evaluation/.

## Boundary edges (ADR-001)

- The SUT is deterministic in structure: same input + same frozen knowledge
  state -> same output fields. LLM draft stages, if any, are registered as
  non-deterministic (canonical-pipeline.md, ADR-006).
- The SUT executes ONCE per case. No scorer feedback, no retry with knowledge
  of expectations (execution-harness-design.md).
- Fail-closed: every stage failure is represented in output.failures with a
  fail-closed state (fail-closed-contract.md); a failed stage never produces
  negative existence claims.
