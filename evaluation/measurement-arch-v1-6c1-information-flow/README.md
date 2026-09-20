# V1.6C.1 Information-Flow Repair A/B

Task: `NAV-EXPLORE-MEASUREMENT-ARCH-V1_6C1-INFORMATION-FLOW-REPAIR`

Paired A/B on the burned V1.6B residual set (92 judge-stage rows):

- **OLD arm**: frozen V1.6B checkpoint replay
  (`screening-checkpoint-mimo-v2-5-pro.json`, sha `a5e9d87a...`), no calls.
- **NEW arm**: one fresh call per row with the `semantic-residual-packet-v1`
  structure packet (clause spans, marker spans, route candidates, A3 output,
  deterministic evidence) added to the identical frozen judge prompt/model
  (`command-code/xiaomi/mimo-v2.5-pro`, temp 0).

No gold, ids, or strata enter the packet (audited: `gold-leakage-audit.json`,
`packet-provenance-audit.json`). Packet contract frozen before any call.
No tuning after first call. No fresh validation, no full SUT, no lexical fallback.

Key artifacts:

- `ab-experiment-contract.json` - preregistered gates
- `paired-comparison.py` / `paired-comparison.json` - gate adjudication
- `analysis-suite.py` - old-flow extraction, clusters, attribution, token/latency
- `semantic-residual-packet-v1-manifest.json` - frozen component SHAs
- `final-report.md` - terminal report and status
- `failure-cluster-root-cause.md` - post-terminal diagnosis of the 14 failing
  rows (M1-M4 hypotheses, burned-data diagnostic, no changes made)
- `failure-row-digest.json` - row-level detail for the diagnosis
- `ab-failure-rows-a3-replay.json` - A3 replay proving the frozen boundary
  abstains on 13/14 failure rows (residual is judge-capacity, not boundary)
- `next-stage-design-brief-v1-6c2.md` - post-C1 stage proposal (draft, not
  authorized)
- `next-task-draft-prompt-v1-6c2.md` - draft task prompt for Judge Selection
  V2 (NOT YET AUTHORIZED)

Reproduce NEW arm: `python3 runner_v1_6c1.py` (checkpoint-resume safe).
Reproduce comparison: `python3 paired-comparison.py && python3 analysis-suite.py`.
