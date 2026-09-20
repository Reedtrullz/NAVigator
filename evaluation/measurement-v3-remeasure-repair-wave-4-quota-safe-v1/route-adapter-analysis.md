# Route adapter analysis (gold-blind, Wave-4 predictions)

Source: evaluation/full-sut-repair-wave-4-v1/runs/structural-120-replay-v1
Adapter: measurement_route_adapter.py (frozen pin, gold-blind observation)

| Metric | Value |
|---|---|
| Cases observed | 120 |
| STRUCTURED_V2_2 cases | 62 |
| LEGACY_LABELS_ONLY cases | 58 |
| structured present but fallback used | 0 (hard gate: 0) |
| Routes observed total | 125 |
| Routes with service identity | 125 |
| Evaluable routes | 125 |
| Access binding present | 125 |
| Condition binding present | 125 |
| Evidence joins resolved | 0 |
| Evidence joins missing | 125 |
| no_route_asserted cases | 58 |
| presented_as_complete cases | 104 |

Route criteria with pending semantic review are NOT reported as semantic
PASS anywhere in this task. Structural observation only.
