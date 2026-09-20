# Source fidelity report - RC1 blind set construction

Method: deterministic checker (validation/source_fidelity.py). Excerpts are canon-normalized for whitespace only; any other deviation from knowledge-base bytes fails.

| Wave | Candidates checked | Verbatim excerpts | File refs valid | Failures |
|---|---|---|---|---|
| w1 familieokonomi | 58 | 58 | 58 | 0 |
| w2 tjenestekjede-sikkerhet | 85 | 85 | 85 | 0 |
| w3 bolig-skole-hull | 24 | 24 | 24 | 0 |
| Total | 167 | 167 | 167 | 0 |

Result: all_pass = true for every wave. Every retained case excerpt exists verbatim in the referenced knowledge-base file with sufficient surrounding context.

Deliberate ASCII orthography in knowledge-base files 48, 49, 57, 58 and 60 (for example onsker, maneder, nodhjelp) is preserved byte-for-byte, including the literal typo "o kolonomisk" in file 49.
