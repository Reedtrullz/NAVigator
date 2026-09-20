# Overlap / Lineage Report - Fresh Batch V1

Preparation-stage artifact. No model calls. Comparison of the 350 fresh rows
against the burned reference corpus (text pool) and all historical fixture files.

## Inputs

- dataset-frozen.jsonl rows: 350 (SHA f3e11e83f03b...)
- reference-corpus.jsonl rows: 387 (SHA b85caaaa64f3...)
- historical fixture files scanned: 25
- total reference text triples indexed: 1785

## Gate results

- canonical_hash / packet_sha256 exact hits: 0
- exact triple hits: 0
- normalized-text duplicates: 0
- masked-text (numbers/place) duplicates: 0
- near-dup candidate pairs (sim>=0.55, >=2 shared decision terms): 14
- decision-equivalent candidates (sim>=0.85, >=3 shared terms): 0

Gate: **0 exact/normalized duplicates required.** Masked and near-dup hits are
expected at phrase level because the fresh batch intentionally draws on the same
KB domain; only true decision-equivalent duplicates require builder revision.

## Top near-dup pairs

| row_id | source | sim | shared decision terms |
|---|---|---|---|
| FB1-ARD-001 | dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json:RE11-10 | 0.6502 | bup, fastlege |
| FB1-ARD-001 | dev-corpus-semantic-judge-v1-2/uncertainty-calibration-a.json:UA-NR-02 | 0.5978 | bup, fastlege |
| FB1-SCR-052 | dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json:RE11-01 | 0.5895 | bup, fastlege |
| FB1-CMP-004 | dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json:UN11-11 | 0.5751 | fastlege, henvisning |
| FB1-SCR-051 | dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json:RE11-01 | 0.5739 | bup, fastlege |
| FB1-CMP-004 | dev-corpus-semantic-judge-v1-1/calibration-fixtures-v1-1.json:CAL11-UN-04 | 0.5738 | fastlege, henvisning |
| FB1-CTL-003 | dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json:UN11-11 | 0.5727 | bup, fastlege |
| FB1-SCR-054 | dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json:RE11-01 | 0.5706 | bup, fastlege |
| FB1-ARD-001 | dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json:RE11-01 | 0.5704 | bup, fastlege |
| FB1-ARD-001 | dev-corpus-semantic-judge-v1/judge-validation-fixtures.json:RE-V09 | 0.5702 | bup, fastlege |
| FB1-ARD-016 | dev-corpus-semantic-judge-v1/judge-validation-fixtures.json:RE-V09 | 0.5669 | bup, henvisning |
| FB1-CTL-003 | dev-corpus-semantic-judge-v1-1/calibration-fixtures-v1-1.json:CAL11-UN-04 | 0.5628 | bup, fastlege |
| FB1-CTL-003 | dev-corpus-semantic-judge-v1-4/model-calibration-fixtures.json:MCU-12 | 0.5596 | bup, fastlege |
| FB1-CMP-004 | dev-corpus-semantic-judge-v1-4/model-calibration-fixtures.json:MCU-12 | 0.5534 | fastlege, henvisning |

## Verdict: PASS
