# NAV-EXPLORE-SEMANTIC-REVIEWER-LUNA-QUALIFICATION-V1

Lineage testing `gpt-5.6-luna` (HIGH and MAX reasoning) as a lower-cost
replacement for routine GPT-6 Astra LOW semantic review in Measurement V3.

- Inherited standard: `SEMANTIC-REVIEWER-QUALIFICATION-CONTRACT-V1`
  (SHA256 `a27523eae4edb5b730900da712f1b25514c1bab95f8edb5875b1f314cfcd073f`),
  frozen wins over any prompt on divergence.
- Inherited reference corpus: `evaluation/semantic-reviewer-cost-qualification-v1/reference-corpus.jsonl`
  (SHA256 `b85caaaa64f3393f27f8177f0b4979e6139c0ff8d18ee3c80efb45eab9e11c2b`).
  The reference is a frozen authoritative semantic reference, NOT human ground truth.
- Terminal status: `NO_LUNA_REVIEWER_CONFIG_QUALIFIES`.

## Stage results

| Stage | LUNA-HIGH | LUNA-MAX |
|---|---|---|
| Transport calibration | PASS (0 transport errors, 19 rows) | PASS (0 transport errors, 19 rows) |
| Screening | PASS both lanes | PASS both lanes |
| Core dual pass | FAIL forbidden and critical | NOT RUN (cheapest-sufficient, section 14) |
| Stability | NOT RUN (core gates failed) | NOT RUN |

Core gate failures (LUNA-HIGH):

- Forbidden: consensus-vs-reference errors 10 (max 2), dual-consensus field
  errors 9 (max 5), evidence-invalid rows 3 (max 2), pass-level errors 30 (max 11).
- Critical: consensus-vs-reference errors 9 (max 0), safety-subset errors 7
  (max 0, 25 safety rows), evidence-invalid rows 46 (max 2), 69/80 rows
  INVALID_MODEL_REVIEW. Only under-escalation (2 = 2) and catastrophic false
  triggers (0) passed.

## File map

- `input-integrity.json` - predecessor SHA verification and inherited pins.
- `luna-high-config.json` / `luna-max-config.json` - frozen candidate configs.
- `luna_transport.py` - in-process auth transport (token never printed/persisted).
- `run_transport_calibration_luna.py`, `run_screening_luna.py`,
  `run_dual_pass_luna.py`, `run_stability_luna.py` - stage runners.
- `score_screening_luna.py`, `score_dual_pass_luna.py` - frozen-gate scorers.
- `build_report_luna.py` - disagreement analysis, qualification rollups,
  token/cost analysis, cascade simulation, proposed router.
- `edge_diag_luna.py` + `edge-agreement-diagnostic.json` - EDGE-partition
  pass-level agreement diagnostic.
- `*-progress-*.jsonl` - raw append-only call logs per stage/config.
- `hashes.txt` - SHA256 pins for all deliverables except TASK-LOCK.json
  (predecessor convention: lock closes after hash freeze).

Protocol-correct absences (not failures): LUNA-MAX core dual pass and
stability were stopped after screening by the frozen cheapest-sufficient
policy; LUNA-HIGH stability was blocked by failed core gates.

## Reproduce

All scorers and the diagnostic are deterministic over the frozen result files:

    cd "evaluation/semantic-reviewer-luna-qualification-v1"
    python3 score_screening_luna.py
    python3 score_dual_pass_luna.py
    python3 build_report_luna.py
    python3 edge_diag_luna.py
    shasum -a 256 -c hashes.txt

Stage runners require the local proxy route (`127.0.0.1:10100`) and are not
re-run in this lineage. No Astra, Sol, GPT-5.5, LongCat or third-party model
calls were made; fresh cases consumed: 0.

See `final-report.md` for the full 55-point report.
