# Annotation Summary

## Model and isolation

- Model: command-code/gpt-5.6-luna via local proxy, temperature 0.
- Every pass ran in a fresh process and fresh model context. Each request
  contained only: frozen contract text, schema, and one case. No pass saw
  another pass's output, gold labels, old annotations, or annotator identity.
- Outputs were schema-validated before acceptance; invalid output retried,
  then recorded as SCHEMA_FAILURE. Final schema-failure count: 0.

## Runs

| Run | Cases | Completed | Schema failures |
|---|---|---|---|
| cal1-pass1 / cal1-pass2 | 20 (CC3) | 20/20 each | 0 |
| cal2-pass1 / cal2-pass2 | 20 (CD3) | 20/20 each | 0 |
| FINALP1 / FINALP2 (30-case) | 30 (RC33M2) | 30/30 each | 0 |

## Contract freeze

contract-freeze.json: ANNOTATION_CONTRACT_V3_FROZEN, SHA256 recorded for
contract, schema, both calibration sets, and both calibration result files.
Contract SHA 57fad046..., schema SHA 5c28d914... No wording change after
freeze; the final 30-case passes used the frozen bytes.

## Terminal state

ANNOTATION_CONTRACT_NOT_READY. The 30-case passes are complete and
machine-readable (pass1-results.json, pass2-results.json) but no gold was
adjudicated and no key was sealed, because pre-adjudication gates failed.
The two pass files are honest artifacts of a failed-gate terminal state;
they are not certification input.
