# Measurement V3 Combined Freeze

Stage 3 of the AFK measurement-system campaign. Combines the frozen
deterministic scorer (dev-corpus-scorer-v1), the frozen M2 human-review lane
(V2.6), and the frozen generic semantic human-review lane (V2.15) under one
combined engine with exactly one authoritative owner per item.

Key properties:

- Deterministic scorer notes that require semantic judgment escalate to the
  generic human-review lane (fail-closed; no automated semantic verdicts).
- M2 workflow items route to the M2 lane; all four semantic dimensions route
  to the generic lane.
- Pending / invalid / disagreement states never carry a final label.
- Full provenance on every lane record, including accepted duplicate-rejection
  terminal tails.

"python3 run_integration_v3.py" runs 150 mixed-workflow fixtures through 9
gates; current state: all gates PASS. See final-report.md and v3-manifest.json
(hashes in hashes.txt).
