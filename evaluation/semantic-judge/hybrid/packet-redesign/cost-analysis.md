# Cost analysis (spec 37)

All live runs: openai/gpt-5.6-luna via local proxy, temperature 0,
max_tokens 300, 1 review call per review-path claim.

## Model calls

| Stage | Calls |
|---|---|
| Gate subset runs (5 variants x 59 review claims) | 295 |
| Oracle experiment (45 claims, 2 revisions) | 90 |
| **Total this task** | **385** |

Per 100 claims (full suite, 389 claims, 268 review-path): ~69 model
calls/100 claims, identical to Iteration B routing (same auto_gate;
0 fidelity failures, so no re-calls).

## Packet tokens (approx, chars/4)

| Packet | avg spans (review rows) | avg packet tokens |
|---|---|---|
| Iteration B v1 (error cases) | 2.87 | ~45 |
| packet-v2.1 no_s0 max6 | 1.24 | 84 |
| packet-v2.1 no_s0 max8 | 1.6 | ~110 |

Notes:

* v2 span count is lower (aggressive dedup + diversity pruning) but
  per-span metadata (roles, coverage, relations, per-atom groups)
  raises tokens ~85% vs B's error-case packets.
* 0 fidelity failures means no wasted re-calls; the syntactic schema
  was followed in 100% of the 295 live review calls (route never
  fidelity_failed, no JSON parse failures).
* Size experiment: max4 81.3%, max6 80.4%, max8 78.9% on the gate
  subset. Fewer tokens was mildly BETTER; there is no accuracy case
  for max8. If packet-v2.1 is ever shipped, max4 is the cost-optimal
  setting (further token reduction available by dropping qualifier
  spans).
* Latency unchanged (~2.5-3.5 s/call); no batching used.
