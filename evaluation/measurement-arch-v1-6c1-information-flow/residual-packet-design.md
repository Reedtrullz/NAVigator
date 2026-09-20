# Semantic Residual Packet v1 - Design

Task: NAV-EXPLORE-MEASUREMENT-ARCH-V1_6C1-INFORMATION-FLOW-REPAIR

## Purpose

Give the semantic judge the deterministic structure the pipeline already
computed, next to the raw prose, so it does not have to re-derive clause
structure, scope, and commitment probabilistically. This repairs the
information boundary documented in current-information-flow.md.

## Source-of-truth rule (contract section 8)

Every field is either (1) produced verbatim by the frozen A3 engine
(21047fda...) via its public classify() output, or (2) mechanically derived
from A3's own frozen marker lists by substring location. No new semantic
classification, no gold-derived content, no new rules.

## Packet fields

| field | origin | provenance |
|---|---|---|
| dimension | frozen fixture row | source fixture |
| source_text | frozen fixture sut | source fixture |
| criterion | frozen fixture crit, verbatim | source fixture |
| clause_spans | A3 _clauses() segmentation (same regex the engine uses) | derived: a3_clause_segmentation |
| route_candidates | A3 ROUTE_TERMS hit locations | derived: a3_route_terms_hits |
| quote_spans | A3 QUOTE_MARKERS hits | derived: a3_marker_hits |
| negation_spans | A3 NEGATION_MARKERS hits | derived: a3_marker_hits |
| retraction_spans | A3 RETRACTION_MARKERS hits | derived: a3_marker_hits |
| hedge_spans | A3 HEDGE_MARKERS hits | derived: a3_marker_hits |
| assertion_spans | A3 ASSERTION_MARKERS hits | derived: a3_marker_hits |
| conditional_spans | A3 CONDITIONAL_ROUTE_MARKERS + CONDITIONAL_UNC_MARKERS hits | derived: a3_marker_hits |
| attribution_spans | A3 USER_ATTRIBUTION_MARKERS + THIRD_PARTY_ATTRIBUTION_MARKERS hits | derived: a3_marker_hits |
| vague_spans | A3 VAGUE_MARKERS hits | derived: a3_marker_hits |
| a3 | full frozen A3 classify() output | engine: boundary_preclassifier.py 21047fda |
| deterministic_evidence | A3 evidence_span texts that exist in source | engine output, span-verified |

## DELIBERATE INFORMATION HYGIENE: route_candidates

A3's route_commitment conflict blocks carry an "inventory": true/false flag
for route nouns. That flag is a lexical inventory property, not a semantic
verdict - but it could function as a deterministic hint about whether the
route name is a real service. The packet strips the inventory flag
mechanically everywhere (deep redaction inside a3 conflict blocks) and keeps
everything else verbatim: abstain reason, rule ids, labels, clause indices.
The abstain REASON (e.g. UNGROUNDED_ROUTE_CANDIDATE) already conveys the
substance and is explicitly allowed context under contract section 11.
route_candidates carry {start, end, text, clause_index} only.

## A3 ABSTAIN is context, not a verdict hint (contract section 11)

The packet exposes a3.abstained and a3.reason exactly as the engine
produced them. It does NOT contain any field named or phrased as a
semantic verdict suggestion. The prompt wrapper states: "deterministic
structure er kontekst, ikke fasit".

## Raw text stays authoritative (contract section 13)

source_text is always included in full. The judge can verify every span
against it.

## Gold leakage zero-gate (contract section 10)

The packet builder NEVER reads gold files, fixture stratum, expected
verdicts, or the fixture id. It receives (dimension, criterion, source_text)
only. The mechanical leakage audit greps the packet for forbidden keys and
verifies no gold-only vocabulary from screening-gold.json enters the packet.
